#!/usr/bin/env python3
"""把 DXF 图纸整理成可核对的结构化清单。

只读 DXF，不改原文件。输出：
    <outdir>/<图纸名>.json   完整清单（含每个实体的 handle）
    <outdir>/<图纸名>.md     给人看的摘要
    <outdir>/ledger.csv      多张图时的台账

设计原则：
- 读到什么就写什么，读不到的项目明确记在 warnings 里，不静默跳过；
- 文字用 DXF 里的原始字符串（不是 OCR，也不是渲染图上的字）；
- 每条记录保留 handle，便于回到原图核对。

用法：
    python3 cad_inventory.py sample-pfd.dxf
    python3 cad_inventory.py dxf/ --out inventory/
    python3 cad_inventory.py old.dxf --encoding gbk
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import ezdxf
from ezdxf import bbox, recover

DEFAULT_TAG_PATTERN = r"[A-Z]{1,4}-\d{2,4}"
INSTRUMENT_PREFIXES = {
    "TI", "PI", "FI", "LI", "AI", "SI", "DI",
    "TIC", "PIC", "FIC", "LIC", "AIC", "SIC",
    "PSV", "TSV", "LSV", "FSV",
}
PROXY_TYPES = {"ACAD_PROXY_ENTITY", "ACAD_PROXY_OBJECT", "ACAD_PROXY_OBJECT_CLASS"}


def load_document(path: Path, encoding: str | None) -> tuple[ezdxf.document.Drawing, list[str]]:
    """容错读取；返回文档和需要提醒的问题列表。"""
    warnings: list[str] = []
    if path.suffix.lower() == ".dwg":
        # DWG 需要本机先装 ODA File Converter，再由 ezdxf 调用它转换
        from ezdxf.addons import odafc

        if not odafc.is_installed():
            raise SystemExit(
                "读取 DWG 需要先安装 ODA File Converter，并让 ODAFileConverter 命令在 PATH 里；"
                "也可以先在 AutoCAD 里另存为 DXF。")
        try:
            doc = odafc.readfile(str(path))
        except Exception as error:  # noqa: BLE001 - 转换器的错误类型随版本变化
            raise SystemExit(f"ODA File Converter 转换 {path.name} 失败：{error}")
        warnings.append("经由 ODA File Converter 读取 DWG")
        return doc, warnings
    try:
        doc, auditor = recover.readfile(str(path))
    except UnicodeDecodeError:
        if not encoding:
            raise
        doc = ezdxf.readfile(str(path), encoding=encoding)
        warnings.append(f"按 {encoding} 编码读取（自动识别失败）")
        auditor = None
    except ezdxf.DXFStructureError as error:
        raise SystemExit(f"{path.name} 不是有效的 DXF：{error}")
    if auditor is not None:
        if auditor.errors:
            warnings.append(f"审计发现 {len(auditor.errors)} 处严重错误（已尽量修复）")
        if not auditor.has_errors and auditor.fixes:
            warnings.append(f"审计自动修复 {len(auditor.fixes)} 处问题")
    return doc, warnings


def vec(value) -> list[float]:
    return [round(float(value.x), 3), round(float(value.y), 3)]


def text_of(entity) -> str:
    dxf_type = entity.dxftype()
    if dxf_type == "TEXT":
        return entity.dxf.text
    if dxf_type == "MTEXT":
        return entity.plain_text()
    return ""


def block_xref_names(doc) -> list[str]:
    names: list[str] = []
    try:
        for record in doc.blocks.block_records:
            if record.dxf.name.startswith("*"):
                continue
            # bit 4 = 外部参照
            if int(record.dxf.get("flags", 0)) & 4:
                names.append(record.dxf.name)
    except Exception:  # noqa: BLE001 - 个别文件结构异常时不阻断清单生成
        pass
    return names


def collect(path: Path, encoding: str | None, tag_pattern: str) -> dict:
    doc, warnings = load_document(path, encoding)
    tag_re = re.compile(tag_pattern, re.IGNORECASE)

    layouts = [doc.modelspace()] + [layout for layout in doc.layouts if layout.name != "Model"]
    texts: list[dict] = []
    equipment: list[dict] = []
    instruments: list[dict] = []
    block_counts: Counter = Counter()
    layer_counts: Counter = Counter()
    type_counts: Counter = Counter()
    tags: set[str] = set()
    proxy_count = 0
    layout_stats: list[dict] = []

    for layout in layouts:
        try:
            entities = list(layout)
        except Exception as error:  # noqa: BLE001
            warnings.append(f"布局 {layout.name} 读取失败：{error}")
            continue
        layout_counts = Counter()
        for entity in entities:
            dxf_type = entity.dxftype()
            layer = entity.dxf.get("layer", "0")
            type_counts[dxf_type] += 1
            layer_counts[layer] += 1
            layout_counts[dxf_type] += 1
            if dxf_type in PROXY_TYPES:
                proxy_count += 1

            if dxf_type in ("TEXT", "MTEXT"):
                text = text_of(entity).strip()
                if text:
                    texts.append({
                        "handle": entity.dxf.handle,
                        "type": dxf_type,
                        "layout": layout.name,
                        "layer": layer,
                        "text": text,
                        "insert": vec(entity.dxf.insert),
                    })
                    tags.update(tag_re.findall(text))

            elif dxf_type == "INSERT":
                name = entity.dxf.name
                block_counts[name] += 1
                attribs = {attrib.dxf.tag: attrib.dxf.text for attrib in entity.attribs}
                for value in attribs.values():
                    tags.update(tag_re.findall(value))
                record = {
                    "handle": entity.dxf.handle,
                    "layout": layout.name,
                    "layer": layer,
                    "block": name,
                    "attributes": attribs,
                    "insert": vec(entity.dxf.insert),
                }
                tag = attribs.get("TAG") or attribs.get("tag") or ""
                prefix = re.split(r"[-\s]", tag, maxsplit=1)[0].upper() if tag else ""
                if name.upper().startswith("INS") or prefix in INSTRUMENT_PREFIXES:
                    instruments.append(record)
                else:
                    equipment.append(record)
            elif dxf_type == "DIMENSION":
                # 尺寸标注文字不参与位号统计，但记下数量，便于判断图纸是否带尺寸
                layout_counts["DIMENSION"] += 0

        try:
            extents = bbox.extents(layout)
            extent_box = [list(map(lambda v: round(float(v), 3), extents.extmin)),
                          list(map(lambda v: round(float(v), 3), extents.extmax))] if extents.has_data else []
        except Exception:  # noqa: BLE001
            extent_box = []
        layout_stats.append({
            "name": layout.name,
            "entities": len(entities),
            "by_type": dict(layout_counts),
            "extents": extent_box,
        })

    style_fonts = sorted({style.dxf.get("font", "") for style in doc.styles if style.dxf.get("font")})
    xrefs = block_xref_names(doc)
    if xrefs:
        warnings.append(f"有未绑定的外部参照：{', '.join(xrefs)}（清单只含本图内容）")
    if proxy_count:
        warnings.append(f"有 {proxy_count} 个代理对象（AutoCAD 自定义对象），几何可能不完整")

    return {
        "source": path.name,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dxf_version": doc.dxfversion,
        "encoding": doc.encoding,
        "tag_pattern": tag_pattern,
        "counts": {
            "entities": sum(type_counts.values()),
            "texts": len(texts),
            "inserts": sum(block_counts.values()),
            "equipment": len(equipment),
            "instruments": len(instruments),
            "proxy_objects": proxy_count,
            "tags": len(tags),
        },
        "by_type": dict(type_counts),
        "by_layer": dict(layer_counts),
        "layers": [
            {"name": layer.dxf.name, "color": int(layer.dxf.get("color", 7))}
            for layer in doc.layers
        ],
        "blocks": [
            {"name": name, "inserts": count}
            for name, count in block_counts.most_common()
        ],
        "insert_definitions": [
            {"name": block.name, "entity_types": sorted({e.dxftype() for e in block})}
            for block in doc.blocks
            if not block.name.startswith("*")
        ],
        "styles": style_fonts,
        "layouts": layout_stats,
        "texts": texts,
        "equipment": equipment,
        "instruments": instruments,
        "tags": sorted(tags),
        "warnings": warnings,
    }


def write_json(data: dict, path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(data: dict, path: Path) -> None:
    lines: list[str] = []
    counts = data["counts"]
    lines.append(f"# {data['source']}｜图纸清单")
    lines.append("")
    lines.append(f"- DXF 版本：{data['dxf_version']}")
    lines.append(f"- 实体：{counts['entities']}；文字：{counts['texts']}；块引用：{counts['inserts']}")
    lines.append(f"- 设备：{counts['equipment']}；仪表：{counts['instruments']}；位号候选：{counts['tags']}")
    lines.append("")

    if data["warnings"]:
        lines.append("## 需要先看的问题")
        lines.append("")
        for warning in data["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("## 布局")
    lines.append("")
    lines.append("| 布局 | 实体数 | 范围 |")
    lines.append("|---|---|---|")
    for layout in data["layouts"]:
        extent = layout["extents"]
        box = f"{extent[0]} – {extent[1]}" if extent else "无"
        lines.append(f"| {layout['name']} | {layout['entities']} | {box} |")
    lines.append("")

    if data["equipment"]:
        lines.append("## 设备")
        lines.append("")
        lines.append("| handle | 位号 | 名称 | 块 | 插入点 |")
        lines.append("|---|---|---|---|---|")
        for item in data["equipment"]:
            attribs = item["attributes"]
            lines.append(
                f"| {item['handle']} | {attribs.get('TAG', '')} | {attribs.get('NAME', '')} "
                f"| {item['block']} | {item['insert']} |"
            )
        lines.append("")

    if data["instruments"]:
        lines.append("## 仪表")
        lines.append("")
        lines.append("| handle | 位号 | 名称 | 块 | 插入点 |")
        lines.append("|---|---|---|---|---|")
        for item in data["instruments"]:
            attribs = item["attributes"]
            lines.append(
                f"| {item['handle']} | {attribs.get('TAG', '')} | {attribs.get('NAME', '')} "
                f"| {item['block']} | {item['insert']} |"
            )
        lines.append("")

    lines.append("## 图层")
    lines.append("")
    lines.append("| 图层 | 颜色 | 实体数 |")
    lines.append("|---|---|---|")
    for layer in data["layers"]:
        lines.append(f"| {layer['name']} | {layer['color']} | {data['by_layer'].get(layer['name'], 0)} |")
    lines.append("")

    lines.append("## 文字（前 200 条）")
    lines.append("")
    lines.append("| handle | 图层 | 文字 | 位置 |")
    lines.append("|---|---|---|---|")
    for item in data["texts"][:200]:
        text = item["text"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item['handle']} | {item['layer']} | {text} | {item['insert']} |")
    if len(data["texts"]) > 200:
        lines.append("")
        lines.append(f"另有 {len(data['texts']) - 200} 条文字，见同名 JSON。")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="把 DXF 整理成结构化清单（只读）")
    parser.add_argument("source", help="DXF 文件或包含 DXF 的目录")
    parser.add_argument("-o", "--out", default="inventory", help="输出目录，默认 inventory/")
    parser.add_argument("--encoding", default=None, help="自动识别失败时强制指定，例如 gbk")
    parser.add_argument("--tag-pattern", default=DEFAULT_TAG_PATTERN, help="位号正则")
    args = parser.parse_args()

    source = Path(args.source).expanduser()
    if not source.exists():
        print(f"找不到：{source}", file=sys.stderr)
        return 1
    files = sorted([*source.rglob("*.dxf"), *source.rglob("*.DWG")]) if source.is_dir() else [source]
    if not files:
        print(f"{source} 里没有 .dxf 或 .dwg 文件", file=sys.stderr)
        return 1

    outdir = Path(args.out).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []
    for path in files:
        print(f"读取 {path.name} …")
        try:
            data = collect(path, args.encoding, args.tag_pattern)
        except SystemExit as error:
            print(f"  跳过：{error}", file=sys.stderr)
            ledger.append({"file": path.name, "error": str(error)})
            continue
        stem = path.stem
        write_json(data, outdir / f"{stem}.json")
        write_markdown(data, outdir / f"{stem}.md")
        counts = data["counts"]
        ledger.append({
            "file": path.name,
            "dxf_version": data["dxf_version"],
            "entities": counts["entities"],
            "texts": counts["texts"],
            "inserts": counts["inserts"],
            "equipment": counts["equipment"],
            "instruments": counts["instruments"],
            "tags": counts["tags"],
            "warnings": len(data["warnings"]),
        })
        print(f"  实体 {counts['entities']}，文字 {counts['texts']}，设备 {counts['equipment']}，"
              f"仪表 {counts['instruments']}，位号候选 {counts['tags']}")

    with (outdir / "ledger.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "file", "dxf_version", "entities", "texts", "inserts",
            "equipment", "instruments", "tags", "warnings", "error",
        ])
        writer.writeheader()
        for row in ledger:
            writer.writerow({key: row.get(key, "") for key in writer.fieldnames})
    print(f"清单写入 {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
