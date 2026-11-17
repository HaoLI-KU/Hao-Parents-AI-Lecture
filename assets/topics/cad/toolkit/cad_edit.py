#!/usr/bin/env python3
"""按修改计划精确修改 DXF，并在写盘后重读校验。

原则：
- 只写新文件，绝不覆盖输入；
- 每条操作都带 handle 和“修改前状态”守卫（expect），不符就整体中止；
- --dry-run 只输出前后对照；
- 写盘后重新打开，逐项检查计划是否达成、未涉及实体是否原样。

用法（通常由 cad.py 调用）：
    python3 cad_edit.py check-plan plan.json --drawing work.dxf
    python3 cad_edit.py apply plan.json --drawing work.dxf --out work/out.dxf
    python3 cad_edit.py apply plan.json --drawing work.dxf --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

import ezdxf
from ezdxf import bbox, recover

HANDLE_RE = re.compile(r"^[0-9A-Fa-f]+$")
SUPPORTED_OPS = {
    "set_layer", "move", "delete", "set_attribute", "replace_text",
    "set_color", "rename_layer", "add_line", "add_polyline", "add_circle", "add_text",
}
EXPECT_KEYS = {"type", "layer", "text", "insert", "tag", "name", "color", "attributes", "block"}


class PlanError(Exception):
    """计划本身或守卫检查失败。"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_drawing(path: Path):
    try:
        doc, auditor = recover.readfile(str(path))
    except ezdxf.DXFStructureError as error:
        raise PlanError(f"{path.name} 不是有效的 DXF：{error}")
    if auditor.has_errors:
        raise PlanError(f"{path.name} 审计有严重错误，先处理源文件再修改。")
    return doc


def load_plan(path: Path) -> dict:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PlanError(f"{path.name} 不是有效 JSON：{error}")
    if not isinstance(plan.get("operations"), list) or not plan["operations"]:
        raise PlanError("计划里必须有非空的 operations 列表。")
    for index, op in enumerate(plan["operations"], start=1):
        if op.get("op") not in SUPPORTED_OPS:
            raise PlanError(f"第 {index} 条操作不支持：{op.get('op')!r}")
        if op["op"].startswith("add_"):
            if not op.get("layer"):
                raise PlanError(f"第 {index} 条新增操作缺少 layer。")
            continue
        if op["op"] == "rename_layer":
            if not op.get("from") or not op.get("to"):
                raise PlanError(f"第 {index} 条图层改名缺少 from/to。")
            continue
        handle = str(op.get("handle", ""))
        if not HANDLE_RE.match(handle):
            raise PlanError(f"第 {index} 条操作缺少合法 handle。")
        expect = op.get("expect")
        if not isinstance(expect, dict) or not expect:
            raise PlanError(f"第 {index} 条操作缺少 expect 守卫；不允许盲目修改。")
        unknown = set(expect) - EXPECT_KEYS
        if unknown:
            raise PlanError(f"第 {index} 条操作的 expect 含未知字段：{sorted(unknown)}")
    return plan


def text_of(entity) -> str:
    if entity.dxftype() == "MTEXT":
        return entity.plain_text()
    if entity.dxftype() == "TEXT":
        return entity.dxf.text
    return ""


def attributes_of(entity) -> dict:
    if entity.dxftype() != "INSERT":
        return {}
    return {attrib.dxf.tag: attrib.dxf.text for attrib in entity.attribs}


def vec(value) -> list[float]:
    return [round(float(value.x), 3), round(float(value.y), 3)]


def current_value(entity, key: str):
    if key == "type":
        return entity.dxftype()
    if key == "layer":
        return entity.dxf.get("layer", "")
    if key == "text":
        return text_of(entity)
    if key == "insert":
        return vec(entity.dxf.insert) if entity.dxf.hasattr("insert") else None
    if key == "tag":
        return attributes_of(entity).get("TAG", "")
    if key == "name":
        return attributes_of(entity).get("NAME", "")
    if key == "color":
        return entity.dxf.get("color", None)
    if key == "attributes":
        return attributes_of(entity)
    if key == "block":
        return entity.dxf.get("name", "") if entity.dxftype() == "INSERT" else ""
    return None


def values_match(expected, actual) -> bool:
    if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
        return len(expected) == len(actual) and all(
            abs(float(a) - float(b)) < 0.002 for a, b in zip(expected, actual)
        )
    if isinstance(expected, dict) and isinstance(actual, dict):
        return all(values_match(expected[key], actual.get(key)) for key in expected)
    return expected == actual


def resolve(doc, handle: str):
    entity = doc.entitydb.get(handle)
    if entity is None:
        raise PlanError(f"找不到 handle {handle}；清单可能过期，请重新生成。")
    if not entity.dxf.hasattr("layer"):
        raise PlanError(f"handle {handle} 不是图形实体。")
    return entity


def entity_signature(entity) -> str:
    data = {key: str(value) for key, value in sorted(entity.dxfattribs().items())}
    data.pop("handle", None)
    kind = entity.dxftype()
    if kind == "MTEXT":
        data["__text"] = entity.text
    if kind == "INSERT":
        data["__attribs"] = sorted(attributes_of(entity).items())
    if kind in ("LWPOLYLINE", "POLYLINE"):
        try:
            data["__points"] = [vec(point) for point in entity.get_points("xy")]
        except Exception:  # noqa: BLE001
            data["__points"] = []
    return hashlib.sha1(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def graphical_entities(doc):
    return {
        entity.dxf.handle: entity
        for entity in doc.entitydb.values()
        if entity.dxftype() not in ("LAYER", "STYLE", "BLOCK_RECORD")
        and entity.dxf.hasattr("layer")
    }


def layout_entity_count(doc) -> int:
    total = 0
    for layout in doc.layouts:
        try:
            total += len(list(layout))
        except Exception:  # noqa: BLE001
            continue
    return total


def dependent_handles(doc, handle: str) -> set[str]:
    entity = doc.entitydb.get(handle)
    if entity is None or entity.dxftype() != "INSERT":
        return set()
    return {attrib.dxf.handle for attrib in entity.attribs}


def ensure_layer(doc, name: str) -> None:
    if not doc.layers.has_entry(name):
        doc.layers.add(name, color=7)


def plan_check(doc, plan: dict) -> list[dict]:
    resolved = []
    for index, op in enumerate(plan["operations"], start=1):
        item = {"id": op.get("id") or f"op{index}", **op}
        if op["op"].startswith("add_") or op["op"] == "rename_layer":
            resolved.append(item)
            continue
        entity = resolve(doc, op["handle"])
        item["resolved_type"] = entity.dxftype()
        for key, expected in op["expect"].items():
            actual = current_value(entity, key)
            item.setdefault("before", {})[key] = actual
            if not values_match(expected, actual):
                raise PlanError(
                    f"{item['id']}（handle {op['handle']}）守卫不符：{key} 期望 {expected!r}，实际 {actual!r}")
        resolved.append(item)
    return resolved


def apply_operations(doc, resolved: list[dict]) -> list[dict]:
    msp = doc.modelspace()
    applied = []
    for item in resolved:
        op = item["op"]
        if op.startswith("add_"):
            ensure_layer(doc, item["layer"])
        record = {"id": item["id"], "op": op, "handle": item.get("handle"), "status": "done"}
        if op == "add_line":
            entity = msp.add_line(item["start"], item["end"], dxfattribs={"layer": item["layer"]})
        elif op == "add_polyline":
            entity = msp.add_lwpolyline(item["points"], close=item.get("close", False),
                                        dxfattribs={"layer": item["layer"]})
        elif op == "add_circle":
            entity = msp.add_circle(item["center"], float(item["radius"]),
                                    dxfattribs={"layer": item["layer"]})
        elif op == "add_text":
            entity = msp.add_text(item["text"], dxfattribs={
                "layer": item["layer"], "height": float(item.get("height", 2.5))})
            entity.dxf.insert = item["insert"]
        elif op == "set_layer":
            entity = resolve(doc, item["handle"])
            entity.dxf.layer = item["to"]
        elif op == "move":
            entity = resolve(doc, item["handle"])
            dx, dy = item["delta"]
            entity.translate(float(dx), float(dy), 0)
        elif op == "delete":
            entity = resolve(doc, item["handle"])
            record["handle"] = item["handle"]
            entity.destroy()
            applied.append(record)
            continue
        elif op == "set_attribute":
            entity = resolve(doc, item["handle"])
            attrib = next((a for a in getattr(entity, "attribs", []) if a.dxf.tag == item["tag"]), None)
            if attrib is None:
                raise PlanError(f"{item['id']}：handle {item['handle']} 上没有属性 {item['tag']}")
            attrib.dxf.text = item["to"]
        elif op == "replace_text":
            entity = resolve(doc, item["handle"])
            if entity.dxftype() == "TEXT":
                entity.dxf.text = item["to"]
            elif entity.dxftype() == "MTEXT":
                entity.text = item["to"]
            else:
                raise PlanError(f"{item['id']}：handle {item['handle']} 不是文字实体")
        elif op == "set_color":
            entity = resolve(doc, item["handle"])
            entity.dxf.color = int(item["to"])
        elif op == "rename_layer":
            old, new = item["from"], item["to"]
            layer = doc.layers.get(old)
            layer.dxf.name = new
            for other in graphical_entities(doc).values():
                if other.dxf.get("layer") == old:
                    other.dxf.layer = new
        else:
            raise PlanError(f"未实现的操作：{op}")
        if op.startswith("add_"):
            record["new_handle"] = entity.dxf.handle
            record["handle"] = entity.dxf.handle
            record["layer"] = item["layer"]
        else:
            record["before"] = item.get("before", {})
            record["to"] = {key: item[key] for key in ("to", "delta", "tag", "from") if key in item}
        applied.append(record)
    return applied


def post_check(doc, resolved: list[dict]) -> list[dict]:
    results = []
    for item in resolved:
        op = item["op"]
        ok = True
        detail = ""
        try:
            if op == "add_line" or op == "add_polyline" or op == "add_circle" or op == "add_text":
                handle = item.get("new_handle")
                entity = doc.entitydb.get(handle) if handle else None
                ok = entity is not None and entity.dxf.get("layer") == item["layer"]
                detail = f"新实体 {handle} 在图层 {item['layer']}" if ok else "新实体没有落盘"
            elif op == "delete":
                ok = doc.entitydb.get(item["handle"]) is None
                detail = "已删除" if ok else "实体仍存在"
            elif op == "set_layer":
                ok = resolve(doc, item["handle"]).dxf.layer == item["to"]
                detail = f"图层 -> {item['to']}"
            elif op == "move":
                entity = resolve(doc, item["handle"])
                before = item.get("before_insert")
                after = vec(entity.dxf.insert) if entity.dxf.hasattr("insert") else None
                ok = before is not None and after is not None and values_match(
                    [before[0] + item["delta"][0], before[1] + item["delta"][1]], after)
                detail = f"插入点 {before} -> {after}" if before else "已平移"
            elif op == "set_attribute":
                ok = attributes_of(resolve(doc, item["handle"])).get(item["tag"]) == item["to"]
                detail = f"属性 {item['tag']} = {item['to']}"
            elif op == "replace_text":
                ok = text_of(resolve(doc, item["handle"])) == item["to"]
                detail = "文字已替换"
            elif op == "set_color":
                ok = resolve(doc, item["handle"]).dxf.get("color") == int(item["to"])
                detail = f"颜色 -> {item['to']}"
            elif op == "rename_layer":
                ok = doc.layers.has_entry(item["to"]) and not doc.layers.has_entry(item["from"])
                detail = f"图层 {item['from']} -> {item['to']}"
        except PlanError as error:
            ok = False
            detail = str(error)
        results.append({"name": f'{item["id"]}（{op}）', "ok": ok, "detail": detail})
    return results


def run(drawing: Path, plan_path: Path, output: Path | None, dry_run: bool) -> dict:
    plan = load_plan(plan_path)
    doc = load_drawing(drawing)
    resolved = plan_check(doc, plan)
    before_entities = graphical_entities(doc)
    before_sigs = {handle: entity_signature(entity) for handle, entity in before_entities.items()}
    before_count = layout_entity_count(doc)
    rename_targets = set()
    for item in resolved:
        if item["op"] == "rename_layer":
            rename_targets |= {handle for handle, entity in before_entities.items()
                               if entity.dxf.get("layer") == item["from"]}

    # 记录移动前的插入点，便于写盘后核对
    for item in resolved:
        if item["op"] == "move":
            entity = resolve(doc, item["handle"])
            if entity.dxf.hasattr("insert"):
                item["before_insert"] = vec(entity.dxf.insert)

    report = {
        "drawing": str(drawing),
        "plan": str(plan_path),
        "input_sha256": sha256(drawing),
        "dry_run": dry_run,
        "operations": resolved,
        "counts": {"before": before_count},
        "checks": [],
        "ok": True,
    }
    if dry_run:
        report["counts"]["after"] = before_count
        report["checks"].append({"name": "dry-run 未写文件", "ok": True})
        return report

    applied = apply_operations(doc, resolved)
    for record in applied:
        if record.get("new_handle"):
            for item in resolved:
                if item["id"] == record["id"]:
                    item["new_handle"] = record["new_handle"]
    report["applied"] = applied
    if output is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        output = drawing.with_name(f"{drawing.stem}-edit-{stamp}.dxf")
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(output)
    report["output"] = str(output)
    report["output_sha256"] = sha256(output)

    edited = load_drawing(output)
    after_entities = graphical_entities(edited)
    after_sigs = {handle: entity_signature(entity) for handle, entity in after_entities.items()}
    report["counts"]["after"] = layout_entity_count(edited)

    targets = {item["handle"] for item in resolved if item.get("handle")}
    for handle in list(targets):
        targets |= dependent_handles(doc, handle)
    targets |= rename_targets
    added = sum(1 for item in resolved if item["op"].startswith("add_"))
    deleted = sum(1 for item in resolved if item["op"] == "delete")
    expected_after = before_count + added - deleted
    report["counts"].update({"added": added, "deleted": deleted, "expected": expected_after})

    checks = post_check(edited, resolved)
    unchanged_changed = [
        handle for handle, signature in before_sigs.items()
        if handle not in targets and handle in after_sigs and after_sigs[handle] != signature
    ]
    after_count = report["counts"]["after"]
    checks.append({
        "name": "实体数",
        "ok": after_count == expected_after,
        "detail": f"修改前 {before_count}，修改后 {after_count}，预期 {expected_after}",
    })
    checks.append({
        "name": "未涉及实体保持原样",
        "ok": not unchanged_changed,
        "detail": "全部一致" if not unchanged_changed else f"{len(unchanged_changed)} 个实体变化：{unchanged_changed[:8]}",
    })
    report["checks"] = checks
    report["ok"] = all(check["ok"] for check in checks)
    return report


def render_markdown(report: dict) -> str:
    lines = [f"# 修改报告：{Path(report['drawing']).name}", ""]
    lines.append(f"- 输入 sha256：`{report['input_sha256']}`")
    if report.get("output"):
        lines.append(f"- 输出文件：`{report['output']}`")
        lines.append(f"- 输出 sha256：`{report['output_sha256']}`")
    if report.get("dry_run"):
        lines.append("- 本次为 dry-run，没有写文件。")
    lines.append("")
    lines.append("## 操作")
    lines.append("")
    lines.append("| id | 操作 | handle | 结果 |")
    lines.append("|---|---|---|---|")
    for item in report.get("applied", report.get("operations", [])):
        lines.append(f"| {item.get('id', '')} | {item.get('op', '')} | {item.get('handle', '')} | {item.get('status', 'checked')} |")
    lines.append("")
    lines.append("## 校验")
    lines.append("")
    lines.append("| 检查 | 结果 | 说明 |")
    lines.append("|---|---|---|")
    for check in report["checks"]:
        lines.append(f"| {check['name']} | {'通过' if check['ok'] else '失败'} | {check.get('detail', '')} |")
    lines.append("")
    lines.append(f"总体结果：{'通过' if report['ok'] else '未通过'}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="按计划修改 DXF 并校验")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check-plan", help="只检查计划与守卫，不修改")
    check.add_argument("plan")
    check.add_argument("--drawing", required=True)
    apply_cmd = sub.add_parser("apply", help="应用计划并写新文件")
    apply_cmd.add_argument("plan")
    apply_cmd.add_argument("--drawing", required=True)
    apply_cmd.add_argument("--out", default=None)
    apply_cmd.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    drawing = Path(args.drawing)
    try:
        if args.command == "check-plan":
            plan = load_plan(plan_path)
            doc = load_drawing(drawing)
            resolved = plan_check(doc, plan)
            print(f"计划可执行：{len(resolved)} 条操作")
            for item in resolved:
                print(f"- {item['id']}: {item['op']} handle={item.get('handle', '')}")
            return 0
        report = run(drawing, plan_path, Path(args.out) if args.out else None, args.dry_run)
    except PlanError as error:
        print(f"计划失败：{error}", file=sys.stderr)
        return 2
    print(render_markdown(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
