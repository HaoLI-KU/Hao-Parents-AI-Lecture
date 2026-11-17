#!/usr/bin/env python3
"""把 DXF 图纸生成一页自包含的「审图页」HTML，便于在浏览器或 DeepSeek Harness 预览里
浏览、缩放、按图层显示隐藏、点选设备/仪表热点并写批注。

设计原则：
- 几何由 DXF 渲染成矢量 SVG；中文文字用 HTML/SVG 文本单独叠加，因此不依赖 SHX 字体；
- 每个设备、仪表、标题栏文字都有一个稳定热点 id（`hs-<handle>`），批注能对回 DXF 实体；
- 单文件、无外部依赖，可以离线打开，也可以放进 docs/ 供课堂预览；
- 只读 DXF，不修改任何原图。

用法：
    python3 make_review_sheet.py sample-pfd.dxf
    python3 make_review_sheet.py sample-pfd.dxf -o review.html --title "糖浆配制工艺流程图"
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import ezdxf
from ezdxf import bbox, recover
from ezdxf.math import BoundingBox2d
from ezdxf.addons.drawing import Frontend, RenderContext, config, layout, svg

VIEW_SCALE = 1_000_000  # ezdxf SVG 后端的 viewBox 宽度
INSTRUMENT_PREFIXES = {
    "TI", "PI", "FI", "LI", "AI", "SI", "DI",
    "TIC", "PIC", "FIC", "LIC", "AIC", "SIC",
    "PSV", "TSV", "LSV", "FSV",
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def load(path: Path) -> ezdxf.document.Drawing:
    try:
        doc, auditor = recover.readfile(str(path))
    except ezdxf.DXFStructureError as error:
        raise SystemExit(f"{path.name} 不是有效的 DXF：{error}")
    if auditor.has_errors:
        print(f"提醒：审计发现 {len(auditor.errors)} 处严重错误，渲染结果可能不完整", file=sys.stderr)
    return doc


def layout_by_name(doc, name: str):
    if name == "Model":
        return doc.modelspace()
    for layout in doc.layouts:
        if layout.name == name:
            return layout
    raise SystemExit(f"找不到布局：{name}")


def text_anchor(entity) -> tuple[float, float] | None:
    """取文字的基线锚点；取不到时返回 None。

    TEXT/ATTRIB 在左对齐、基线对齐时用 insert；设置了对齐方式时用 align_point。
    MTEXT 的 insert 是第一个字的左上角，这里换算成大致基线位置。
    """
    dxf_type = entity.dxftype()
    try:
        if dxf_type in ("TEXT", "ATTRIB", "ATTDEF"):
            halign = int(entity.dxf.get("halign", 0))
            valign = int(entity.dxf.get("valign", 0))
            point = entity.dxf.insert
            if halign or valign:
                point = entity.dxf.get("align_point", point)
        elif dxf_type == "MTEXT":
            point = entity.dxf.insert
            attachment = int(entity.dxf.get("attachment_point", 1))
            if attachment in (1, 2, 3):  # 顶部对齐的三种情况
                return float(point.x), float(point.y) - text_height(entity) * 0.8
        else:
            return None
    except Exception:  # noqa: BLE001 - 个别损坏实体取不到锚点就跳过
        return None
    return float(point.x), float(point.y)


def text_height(entity) -> float:
    dxf_type = entity.dxftype()
    if dxf_type == "MTEXT":
        return float(entity.dxf.get("char_height", 2.5))
    return float(entity.dxf.get("height", 2.5))


def text_rotation(entity) -> float:
    return float(entity.dxf.get("rotation", 0.0))


def text_content(entity) -> str:
    dxf_type = entity.dxftype()
    if dxf_type == "MTEXT":
        return entity.plain_text()
    return entity.dxf.text


def collect_labels(layout) -> list[dict]:
    """收集所有要显示的中文文字：TEXT、MTEXT，以及块参照上的属性文字。"""
    labels: list[dict] = []
    for entity in layout:
        dxf_type = entity.dxftype()
        if dxf_type in ("TEXT", "MTEXT"):
            content = text_content(entity).strip()
            anchor = text_anchor(entity)
            if content and anchor is not None:
                labels.append({
                    "handle": entity.dxf.handle,
                    "layer": entity.dxf.get("layer", "0"),
                    "text": content,
                    "x": anchor[0],
                    "y": anchor[1],
                    "height": text_height(entity),
                    "rotation": text_rotation(entity),
                })
        elif dxf_type == "INSERT":
            for attrib in entity.attribs:
                content = attrib.dxf.text.strip()
                anchor = text_anchor(attrib)
                if not content or anchor is None:
                    continue
                labels.append({
                    "handle": attrib.dxf.handle,
                    # 属性文字跟随它所属块参照的图层，隐藏设备时标签一起隐藏
                    "layer": entity.dxf.get("layer", "0"),
                    "text": content,
                    "x": anchor[0],
                    "y": anchor[1],
                    "height": text_height(attrib),
                    "rotation": text_rotation(attrib),
                })
    return labels


def collect_inserts(layout) -> list[dict]:
    """带 TAG 属性的块参照就是可点热点的设备或仪表。"""
    hotspots: list[dict] = []
    for entity in layout:
        if entity.dxftype() != "INSERT":
            continue
        attribs = {attrib.dxf.tag: attrib.dxf.text for attrib in entity.attribs}
        tag = attribs.get("TAG", "").strip()
        if not tag:
            continue
        prefix = re.split(r"[-\s]", tag, maxsplit=1)[0].upper()
        kind = "仪表" if prefix in INSTRUMENT_PREFIXES else "设备"
        hotspots.append({
            "handle": entity.dxf.handle,
            "tag": tag,
            "name": attribs.get("NAME", "").strip(),
            "kind": kind,
            "block": entity.dxf.name,
            "x": float(entity.dxf.insert.x),
            "y": float(entity.dxf.insert.y),
            "layer": entity.dxf.get("layer", "0"),
            "attributes": attribs,
        })
    return hotspots


def collect_title_hotspots(labels: list[dict], title_layer: str) -> list[dict]:
    hotspots: list[dict] = []
    for label in labels:
        if label["layer"] != title_layer:
            continue
        hotspots.append({
            "handle": label["handle"],
            "tag": label["text"],
            "name": "标题栏文字",
            "kind": "标题栏",
            "block": "",
            "x": label["x"],
            "y": label["y"],
            "layer": label["layer"],
            "attributes": {},
        })
    return hotspots


def render_layers(doc, layout_obj, width: float, height: float, render_box,
                  layers: list[str], keep_color: bool) -> dict[str, str]:
    """每个图层单独渲染一段 SVG，保证坐标系统一、可独立显示隐藏。"""
    page = layout.Page(width, height, layout.Units.mm, margins=layout.Margins.all(0))
    settings = layout.Settings(fit_page=True, scale=1.0)
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.OFF,
        color_policy=config.ColorPolicy.COLOR if keep_color else config.ColorPolicy.BLACK,
        text_policy=config.TextPolicy.IGNORE,
    )
    context = RenderContext(doc)
    fragments: dict[str, str] = {}
    for index, layer in enumerate(layers):
        backend = svg.SVGBackend()
        frontend = Frontend(context, backend, config=cfg)
        try:
            frontend.draw_layout(
                layout_obj,
                finalize=True,
                filter_func=lambda entity, name=layer: entity.dxf.get("layer", "0") == name,
            )
            fragment = backend.get_string(page, settings=settings, render_box=render_box)
        except Exception as error:  # noqa: BLE001 - 单个图层失败不阻断整页
            print(f"提醒：图层 {layer} 渲染失败：{error}", file=sys.stderr)
            continue
        fragment = re.sub(r"^<\?xml.*?\?>", "", fragment, flags=re.S).strip()
        # 类名加图层前缀，避免各段 <style> 互相覆盖
        fragment = re.sub(r"\bC(\d+)\b", rf"L{index}-C\1", fragment)
        view_box = re.search(r'<svg[^>]*viewBox="([^"]+)"', fragment)
        if not view_box:
            continue
        inner = fragment[fragment.index(">", view_box.start()) + 1: fragment.rindex("</svg>")]
        fragments[layer] = {"viewBox": view_box.group(1), "inner": inner}
    return fragments


def build_html(data: dict) -> str:
    width = data["width"]
    height = data["height"]
    view_h = VIEW_SCALE * height / width if width else VIEW_SCALE

    layer_items = "".join(
        f'<label class="layer"><input type="checkbox" checked data-layer-toggle="{esc(name)}">'
        f'<span class="swatch" style="background:{colour}"></span><span class="layer-name">{esc(name)}</span>'
        f'<span class="layer-count">{count}</span></label>'
        for name, colour, count in data["layers"]
    )

    layer_svgs = "".join(
        f'<svg class="layer-svg" data-layer="{esc(name)}" x="0" y="0" width="{width:g}" height="{height:g}" '
        f'viewBox="{fragment["viewBox"]}" aria-hidden="true">{fragment["inner"]}</svg>'
        for name, fragment in data["fragments"].items()
    )

    label_markup = []
    for label in data["labels"]:
        x = label["x"] - data["xmin"]
        y = data["ymax"] - label["y"]
        rotation = label["rotation"]
        transform = f' transform="rotate({-rotation:g} {x:.3f} {y:.3f})"' if rotation else ""
        size = max(label["height"] * 1.35, data["min_font"])
        lines = label["text"].split("\n")
        tspans = "".join(
            f'<tspan x="{x:.3f}" dy="{0 if index == 0 else size * 1.45:.3f}">{esc(line)}</tspan>'
            for index, line in enumerate(lines)
        )
        label_markup.append(
            f'<text class="lab" data-layer="{esc(label["layer"])}" data-handle="{esc(label["handle"])}" '
            f'x="{x:.3f}" y="{y:.3f}" font-size="{size:.3f}"{transform}>{tspans}</text>'
        )

    hotspot_markup = []
    for index, spot in enumerate(data["hotspots"], start=1):
        x = spot["x"] - data["xmin"]
        y = data["ymax"] - spot["y"]
        title = f'{spot["kind"]} {spot["tag"]}'
        if spot["name"]:
            title += f'｜{spot["name"]}'
        radius = data["hotspot_radius"]
        hotspot_markup.append(
            f'<g class="hs" id="hs-{esc(spot["handle"])}" data-handle="{esc(spot["handle"])}" '
            f'data-tag="{esc(spot["tag"])}" data-name="{esc(spot["name"])}" data-kind="{esc(spot["kind"])}" '
            f'data-layer="{esc(spot["layer"])}" tabindex="0" role="button" aria-label="{esc(title)}">'
            f'<title>{esc(title)}（handle {esc(spot["handle"])}）</title>'
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius:.3f}"></circle>'
            f'<text x="{x:.3f}" y="{y + radius * 0.55:.3f}" font-size="{radius * 2.1:.3f}" '
            f'text-anchor="middle">{index}</text></g>'
        )

    replacements = {
        "@@TITLE@@": esc(data["name"]),
        "@@NAME@@": esc(data["name"]),
        "@@VERSION@@": esc(data["version"]),
        "@@ENTITIES@@": str(data["counts"]["entities"]),
        "@@TEXTS@@": str(data["counts"]["texts"]),
        "@@HOTSPOT_COUNT@@": str(data["counts"]["hotspots"]),
        "@@WIDTH@@": f"{width:g}",
        "@@HEIGHT@@": f"{height:g}",
        "@@VIEWH@@": f"{view_h:g}",
        "@@LAYER_ITEMS@@": layer_items,
        "@@LAYER_SVGS@@": layer_svgs,
        "@@LABELS@@": "".join(label_markup),
        "@@HOTSPOTS@@": "".join(hotspot_markup),
        "@@SPOTS_JSON@@": json.dumps(data["hotspots"], ensure_ascii=False),
        "@@META@@": json.dumps({
            "drawing": data["name"],
            "source": data["source"],
            "generated": data["generated"],
            "counts": data["counts"],
        }, ensure_ascii=False),
        "@@DRAWING_JSON@@": json.dumps(data["name"], ensure_ascii=False),
        "@@SOURCE@@": esc(data["source"]),
        "@@GENERATED@@": esc(data["generated"]),
    }
    page = PAGE_TEMPLATE
    for key, value in replacements.items():
        page = page.replace(key, value)
    return page


PAGE_TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@｜审图页</title>
<style>
:root {
  --paper: #f7f6f2; --card: #ffffff; --ink: #16201e; --muted: #626d6a;
  --line: #e2e0d8; --accent: #0a6b60; --accent-soft: #e4f1ee;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; }
body { font-family: Inter, -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--paper); color: var(--ink); font-size: 14px; }
.app { display: flex; height: 100vh; overflow: hidden; }
.side { width: 300px; flex: 0 0 300px; background: var(--card); border-right: 1px solid var(--line);
  padding: 16px; overflow-y: auto; }
.view { position: relative; flex: 1; overflow: hidden; background: #fff; }
h1 { font-size: 18px; margin: 0 0 4px; font-family: "Source Serif 4", "Songti SC", serif; }
.meta { color: var(--muted); font-size: 12px; margin: 0 0 12px; }
.toolbar { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0; }
button { font: inherit; border: 1px solid var(--line); background: #fff; color: var(--ink);
  border-radius: 8px; padding: 5px 10px; cursor: pointer; min-height: 30px; }
button:hover { border-color: var(--accent); color: var(--accent); }
button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
h2 { font-size: 12px; text-transform: uppercase; letter-spacing: .12em; color: var(--muted);
  margin: 18px 0 8px; font-weight: 600; }
.layers { display: grid; gap: 2px; }
.layer { display: flex; align-items: center; gap: 8px; padding: 3px 0; cursor: pointer; }
.layer input { accent-color: var(--accent); }
.swatch { width: 10px; height: 10px; border-radius: 2px; border: 1px solid var(--line); }
.layer-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.layer-count { color: var(--muted); font-variant-numeric: tabular-nums; }
.info { border: 1px solid var(--line); border-radius: 10px; padding: 10px; margin-top: 10px;
  background: #fbfaf7; min-height: 64px; }
.info.empty { color: var(--muted); }
.info dl { display: grid; grid-template-columns: 60px 1fr; gap: 2px 8px; margin: 0; }
.info dt { color: var(--muted); }
.info dd { margin: 0; word-break: break-all; }
.note-box { margin-top: 10px; display: grid; gap: 6px; }
textarea { font: inherit; width: 100%; min-height: 64px; resize: vertical; padding: 6px 8px;
  border: 1px solid var(--line); border-radius: 8px; background: #fff; color: var(--ink); }
.notes { list-style: none; padding: 0; margin: 8px 0 0; display: grid; gap: 6px; }
.notes li { border-left: 3px solid var(--accent); background: var(--accent-soft); padding: 6px 8px;
  border-radius: 0 6px 6px 0; font-size: 13px; }
.notes .note-head { display: flex; justify-content: space-between; gap: 8px; color: var(--muted);
  font-size: 11px; margin-bottom: 2px; }
.notes button { padding: 0 4px; min-height: 18px; border: 0; background: transparent; color: var(--muted); }
.hint { color: var(--muted); font-size: 12px; line-height: 1.5; margin-top: 10px; }
.stage { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  cursor: grab; touch-action: none; }
.stage.dragging { cursor: grabbing; }
.paper { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.paper > svg { width: 100%; height: 100%; max-width: 100%; max-height: 100%;
  box-shadow: 0 12px 34px -16px rgba(0,0,0,.35); }
#sheet text.lab { fill: #16201e; font-family: "PingFang SC", "Songti SC", "Noto Sans CJK SC", sans-serif; }
#sheet .hs circle { fill: #ffffff; stroke: #0a6b60; stroke-width: .6; }
#sheet .hs text { fill: #0a6b60; font-family: Inter, sans-serif; font-weight: 600; pointer-events: none; }
#sheet .hs { cursor: pointer; }
#sheet .hs:hover circle, #sheet .hs:focus circle { fill: #e4f1ee; stroke-width: 1; }
#sheet .hs.active circle { fill: #0a6b60; }
#sheet .hs.active text { fill: #fff; }
#sheet .hs.hidden, #sheet text.lab.hidden, .layer-svg.hidden { display: none; }
.foot { position: absolute; left: 12px; bottom: 8px; color: var(--muted); font-size: 11px;
  background: rgba(255,255,255,.85); padding: 2px 6px; border-radius: 4px; }
@media (max-width: 900px) {
  .app { flex-direction: column; }
  .side { width: auto; flex: 0 0 auto; max-height: 44vh; border-right: 0; border-bottom: 1px solid var(--line); }
  .view { min-height: 56vh; }
}
@media print {
  .side, .foot { display: none; }
  .app, .view { height: auto; overflow: visible; }
  .stage { position: static; }
  .paper > svg { box-shadow: none; max-width: 100%; }
}
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <h1>@@NAME@@</h1>
    <p class="meta">DXF @@VERSION@@ · 实体 @@ENTITIES@@ 个 · 热点 @@HOTSPOT_COUNT@@ 个</p>

    <div class="toolbar">
      <button type="button" data-zoom="in" aria-label="放大">放大</button>
      <button type="button" data-zoom="out" aria-label="缩小">缩小</button>
      <button type="button" data-zoom="reset" aria-label="适应窗口">适应窗口</button>
      <button type="button" data-toggle="labels">隐藏文字</button>
      <button type="button" data-toggle="hotspots">隐藏热点</button>
    </div>

    <h2>图层</h2>
    <div class="layers">@@LAYER_ITEMS@@</div>

    <h2>选中的实体</h2>
    <div class="info empty" id="info">点图纸上的编号热点，查看对应的设备、仪表或标题栏文字。</div>

    <div class="note-box">
      <textarea id="note" placeholder="给这个热点写一条批注，例如：这里缺少蒸汽伴热？"></textarea>
      <button type="button" class="primary" id="save-note">保存批注</button>
    </div>

    <h2>批注清单</h2>
    <ul class="notes" id="notes"></ul>
    <div class="toolbar">
      <button type="button" id="export-notes">导出批注 JSON</button>
      <button type="button" id="copy-notes">复制批注</button>
    </div>

    <p class="hint">批注存在本机浏览器里，导出 JSON 后可以交给 DeepSeek Harness 读取。
    在 Harness 的 Files 面板预览这一页时，也可以直接用「点选批注」浮层。</p>
    <p class="hint" id="status" role="status" aria-live="polite"></p>
  </aside>

  <main class="view">
    <div class="stage" id="stage">
      <div class="paper">
        <svg id="sheet" viewBox="0 0 @@WIDTH@@ @@HEIGHT@@" xmlns="http://www.w3.org/2000/svg">
          <rect x="0" y="0" width="@@WIDTH@@" height="@@HEIGHT@@" fill="#ffffff"></rect>
          <g id="layers-group">@@LAYER_SVGS@@</g>
          <g id="labels-group">@@LABELS@@</g>
          <g id="hotspots-group">@@HOTSPOTS@@</g>
        </svg>
      </div>
    </div>
    <div class="foot">只读 DXF 生成 · @@SOURCE@@ · @@GENERATED@@</div>
  </main>
</div>

<script>
const DRAWING = @@DRAWING_JSON@@;
const SPOTS = @@SPOTS_JSON@@;
const META = @@META@@;
const STORAGE_KEY = "cad-review:" + (META.source || DRAWING);
const stage = document.getElementById("stage");
const sheet = document.getElementById("sheet");
const info = document.getElementById("info");
const noteInput = document.getElementById("note");
const notesList = document.getElementById("notes");
const status = document.getElementById("status");

let view = { scale: 1, x: 0, y: 0 };
let selected = null;
let notes = [];

function applyView() {
  sheet.style.transform = `translate(${view.x}px, ${view.y}px) scale(${view.scale})`;
  sheet.style.transformOrigin = "center center";
  sheet.style.transition = "transform .08s ease-out";
}
function zoom(factor) {
  view.scale = Math.min(12, Math.max(0.4, view.scale * factor));
  applyView();
}
function resetView() {
  view = { scale: 1, x: 0, y: 0 };
  sheet.style.transform = "none";
}
document.querySelector('[data-zoom="in"]').onclick = () => zoom(1.25);
document.querySelector('[data-zoom="out"]').onclick = () => zoom(0.8);
document.querySelector('[data-zoom="reset"]').onclick = resetView;

stage.addEventListener("wheel", (event) => {
  if (!event.ctrlKey && !event.metaKey) return;
  event.preventDefault();
  zoom(event.deltaY < 0 ? 1.12 : 0.9);
}, { passive: false });

let drag = null;
stage.addEventListener("pointerdown", (event) => {
  if (event.target.closest(".hs")) return;
  drag = { x: event.clientX - view.x, y: event.clientY - view.y };
  stage.classList.add("dragging");
  stage.setPointerCapture(event.pointerId);
});
stage.addEventListener("pointermove", (event) => {
  if (!drag) return;
  view.x = event.clientX - drag.x;
  view.y = event.clientY - drag.y;
  applyView();
});
stage.addEventListener("pointerup", () => { drag = null; stage.classList.remove("dragging"); });
stage.addEventListener("pointercancel", () => { drag = null; stage.classList.remove("dragging"); });

document.querySelectorAll("[data-toggle]").forEach((button) => {
  const key = button.dataset.toggle;
  button.addEventListener("click", () => {
    const hidden = button.classList.toggle("off");
    const selector = key === "labels" ? "#labels-group" : "#hotspots-group";
    document.querySelector(selector).style.display = hidden ? "none" : "";
    button.textContent = hidden ? (key === "labels" ? "显示文字" : "显示热点") : (key === "labels" ? "隐藏文字" : "隐藏热点");
  });
});

document.querySelectorAll("[data-layer-toggle]").forEach((input) => {
  input.addEventListener("change", () => {
    const name = input.dataset.layerToggle;
    document.querySelectorAll(`.layer-svg[data-layer="${CSS.escape(name)}"]`).forEach((node) => {
      node.classList.toggle("hidden", !input.checked);
    });
    document.querySelectorAll(`.lab[data-layer="${CSS.escape(name)}"]`).forEach((node) => {
      node.classList.toggle("hidden", !input.checked);
    });
    document.querySelectorAll(`.hs[data-layer="${CSS.escape(name)}"]`).forEach((node) => {
      node.classList.toggle("hidden", !input.checked);
    });
  });
});

function selectSpot(node) {
  document.querySelectorAll(".hs.active").forEach((item) => item.classList.remove("active"));
  const handle = node.dataset.handle;
  const index = SPOTS.findIndex((item) => item.handle === handle);
  const spot = index >= 0 ? SPOTS[index] : {
    handle, tag: node.dataset.tag, name: node.dataset.name, kind: node.dataset.kind,
  };
  selected = spot;
  node.classList.add("active");
  info.classList.remove("empty");
  const rows = [
    ["编号", String(index + 1)],
    ["类型", spot.kind || ""],
    ["位号", spot.tag || ""],
    ["名称", spot.name || ""],
    ["图层", spot.layer || node.dataset.layer || ""],
    ["handle", handle],
  ];
  if (spot.block) rows.push(["块名", spot.block]);
  Object.entries(spot.attributes || {}).forEach(([key, value]) => {
    if (key !== "TAG" && key !== "NAME") rows.push([key, value]);
  });
  info.innerHTML = "<dl>" + rows.map(([key, value]) =>
    `<dt>${key}</dt><dd>${String(value).replace(/</g, "&lt;")}</dd>`).join("") + "</dl>";
  const existing = notes.find((item) => item.handle === handle);
  noteInput.value = existing ? existing.text : "";
  noteInput.focus();
}

document.querySelectorAll(".hs").forEach((node) => {
  node.addEventListener("click", (event) => {
    event.stopPropagation();
    selectSpot(node);
  });
  node.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectSpot(node);
    }
  });
});

function loadNotes() {
  try {
    notes = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch (error) {
    notes = [];
  }
  renderNotes();
}
function saveNotes() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
  } catch (error) {
    status.textContent = "当前预览环境不允许本地保存：请用「复制批注」或在浏览器里打开本页。";
  }
  renderNotes();
}
function renderNotes() {
  notesList.innerHTML = notes.map((note) => `<li data-handle="${note.handle}">
      <div class="note-head"><span>${note.kind || ""} ${note.tag || note.handle}</span>
      <button type="button" data-remove="${note.handle}" aria-label="删除这条批注">删除</button></div>
      <div>${String(note.text).replace(/</g, "&lt;")}</div>
    </li>`).join("");
  notesList.querySelectorAll("[data-remove]").forEach((button) => {
    button.addEventListener("click", () => {
      notes = notes.filter((note) => note.handle !== button.dataset.remove);
      saveNotes();
    });
  });
  status.textContent = notes.length ? `已保存 ${notes.length} 条批注` : "";
}
document.getElementById("save-note").addEventListener("click", () => {
  if (!selected) {
    status.textContent = "先点一个图纸热点，再写批注。";
    return;
  }
  const text = noteInput.value.trim();
  if (!text) {
    status.textContent = "批注内容为空，没有保存。";
    return;
  }
  notes = notes.filter((note) => note.handle !== selected.handle);
  notes.push({
    handle: selected.handle,
    tag: selected.tag || "",
    name: selected.name || "",
    kind: selected.kind || "",
    text,
    createdAt: new Date().toISOString(),
  });
  saveNotes();
  status.textContent = `已保存「${selected.tag || selected.handle}」的批注`;
});
document.getElementById("export-notes").addEventListener("click", () => {
  const payload = {
    drawing: DRAWING,
    source: META.source,
    exportedAt: new Date().toISOString(),
    notes,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = (META.source || DRAWING).replace(/\.dxf$/i, "") + "-notes.json";
  try {
    link.click();
    status.textContent = "已导出批注 JSON";
  } catch (error) {
    status.textContent = "预览环境拦截了下载：请在浏览器里打开本页再导出。";
  }
  URL.revokeObjectURL(link.href);
});
document.getElementById("copy-notes").addEventListener("click", async () => {
  const text = notes.map((note) => `- [${note.handle}] ${note.kind || ""} ${note.tag || ""}：${note.text}`).join("\n");
  try {
    await navigator.clipboard.writeText(text || "（还没有批注）");
    status.textContent = "批注已复制到剪贴板";
  } catch (error) {
    status.textContent = "浏览器不允许自动复制，请用「导出批注 JSON」。";
  }
});

loadNotes();
applyView();
</script>
</body>
</html>
'''


def build(path: Path, out: Path, title: str | None, layername: str,
          title_layer: str, keep_color: bool) -> None:
    doc = load(path)
    layout_obj = layout_by_name(doc, layername)

    bounds = bbox.extents(layout_obj)
    if not bounds.has_data:
        raise SystemExit("这张图里没有可显示的内容（包围盒为空）。")
    padding = 0.02
    spans = (bounds.extmax.x - bounds.extmin.x, bounds.extmax.y - bounds.extmin.y)
    xmin = bounds.extmin.x - spans[0] * padding
    ymin = bounds.extmin.y - spans[1] * padding
    xmax = bounds.extmax.x + spans[0] * padding
    ymax = bounds.extmax.y + spans[1] * padding
    width = xmax - xmin
    height = ymax - ymin

    layer_counts: Counter = Counter()
    layer_colors: dict[str, str] = {}
    for layer in doc.layers:
        layer_colors[layer.dxf.name] = aci_to_hex(int(layer.dxf.get("color", 7)))
    for entity in layout_obj:
        layer_counts[entity.dxf.get("layer", "0")] += 1
    layers = [(name, layer_colors.get(name, "#8a8a8a"), count)
              for name, count in layer_counts.most_common()]
    text_types = {"TEXT", "MTEXT"}
    renderable = set()
    for entity in layout_obj:
        if entity.dxftype() not in text_types:
            renderable.add(entity.dxf.get("layer", "0"))
    render_names = [name for name, _, _ in layers
                    if name not in ("Defpoints",) and name in renderable]

    render_box = BoundingBox2d([(xmin, ymin), (xmax, ymax)])
    fragments = render_layers(doc, layout_obj, width, height, render_box, render_names, keep_color)
    layers = [item for item in layers if item[0] != "Defpoints"]

    labels = [label for label in collect_labels(layout_obj) if label["layer"] != "Defpoints"]
    hotspots = collect_inserts(layout_obj)
    hotspots.extend(collect_title_hotspots(labels, title_layer))
    hotspots.sort(key=lambda item: (item["kind"], item["tag"]))

    data = {
        "name": title or path.stem,
        "source": path.name,
        "version": doc.dxfversion,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "counts": {
            "entities": len(list(layout_obj)),
            "texts": len(labels),
            "hotspots": len(hotspots),
        },
        "width": width,
        "height": height,
        "xmin": xmin,
        "ymax": ymax,
        "min_font": max(width, height) * 0.0016,
        "hotspot_radius": max(width, height) * 0.006,
        "layers": layers,
        "fragments": fragments,
        "labels": labels,
        "hotspots": hotspots,
    }
    out.write_text(build_html(data), encoding="utf-8")
    print(f"审图页已生成：{out}")
    print(f"图层 {len(layers)} 个；文字 {len(labels)} 条；热点 {len(hotspots)} 个")


ACI_COLORS = {
    1: "#c62828", 2: "#b8860b", 3: "#2e7d32", 4: "#00838f", 5: "#1565c0",
    6: "#7b1fa2", 7: "#16201e", 8: "#616161", 9: "#9e9e9e",
}


def aci_to_hex(value: int) -> str:
    return ACI_COLORS.get(value, "#8a8a8a")


def main() -> int:
    parser = argparse.ArgumentParser(description="把 DXF 生成自包含的审图页 HTML")
    parser.add_argument("source", help="DXF 文件")
    parser.add_argument("-o", "--out", default=None, help="输出 HTML，默认与 DXF 同名")
    parser.add_argument("--title", default=None, help="页面标题，默认用文件名")
    parser.add_argument("--layout", default="Model", help="布局名，默认 Model")
    parser.add_argument("--title-layer", default="TITLE", help="标题栏所在图层，默认 TITLE")
    parser.add_argument("--colors", action="store_true", help="保留图层颜色（默认黑色线）")
    args = parser.parse_args()

    source = Path(args.source).expanduser()
    if not source.is_file():
        print(f"找不到：{source}", file=sys.stderr)
        return 1
    out = Path(args.out).expanduser() if args.out else source.with_suffix(".html")
    build(source, out, args.title, args.layout, args.title_layer, args.colors)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
