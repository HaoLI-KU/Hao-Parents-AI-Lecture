#!/usr/bin/env python3
"""生成一张虚构的「糖浆配制」工艺流程图（DXF R2018）。

全部位号、设备名称与流程都是教学虚构，不对应任何真实装置、单位或项目。
用途：让学员在不接触真实图纸的前提下，练习 DWG/DXF → 结构化清单 → 审图页
这一整条流程。

用法：
    python3 make_sample_pfd.py                    # 输出 sample-pfd.dxf
    python3 make_sample_pfd.py -o /tmp/demo.dxf   # 指定输出路径
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import ezdxf

DRAWING_WIDTH = 841.0  # A1 横版，单位 mm
DRAWING_HEIGHT = 594.0

LAYERS = {
    "FRAME": 7,
    "TITLE": 7,
    "EQUIPMENT": 4,
    "PIPE": 3,
    "INSTRUMENT": 6,
    "TEXT": 7,
    "NOTE": 2,
}


def new_document() -> ezdxf.document.Drawing:
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 4  # 毫米
    doc.header["$LUNITS"] = 2
    doc.header["$DWGCODEPAGE"] = "ANSI_936"  # 简体中文图纸的常见代码页
    doc.styles.add("HZ", font="simsun.ttf")

    for name, color in LAYERS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    return doc


def draw_frame(msp: ezdxf.layouts.Modelspace) -> None:
    msp.add_lwpolyline(
        [(10, 10), (DRAWING_WIDTH - 10, 10), (DRAWING_WIDTH - 10, DRAWING_HEIGHT - 10),
         (10, DRAWING_HEIGHT - 10)],
        close=True,
        dxfattribs={"layer": "FRAME"},
    )
    msp.add_lwpolyline(
        [(20, 20), (DRAWING_WIDTH - 20, 20), (DRAWING_WIDTH - 20, DRAWING_HEIGHT - 20),
         (20, DRAWING_HEIGHT - 20)],
        close=True,
        dxfattribs={"layer": "FRAME"},
    )


def add_text(msp, text, insert, height=3.5, layer="TEXT", align=None, width=None):
    attribs = {"layer": layer, "height": height, "style": "HZ"}
    entity = msp.add_text(text, dxfattribs=attribs)
    if width is not None:
        entity.dxf.width = width
    if align is not None:
        entity.set_placement(insert, align=align)
    else:
        entity.dxf.insert = insert
    return entity


def add_note(msp, text, insert, height=3.2):
    entity = msp.add_mtext(text, dxfattribs={"layer": "NOTE", "style": "HZ", "char_height": height})
    entity.dxf.insert = insert
    return entity


def equipment_blocks(doc):
    tank = doc.blocks.new("EQ-TANK")
    tank.add_lwpolyline([(-25, -30), (25, -30), (25, 30), (-25, 30)], close=True)
    tank.add_ellipse((0, 30), major_axis=(25, 0), ratio=0.3)
    tank.add_line((-25, -12), (25, -12))

    pump = doc.blocks.new("EQ-PUMP")
    pump.add_circle((0, 0), 12)
    pump.add_lwpolyline([(-16, -18), (16, -18), (12, -26), (-12, -26)], close=True)
    pump.add_line((12, 0), (22, 0))

    hx = doc.blocks.new("EQ-HX")
    hx.add_lwpolyline([(-25, -15), (25, -15), (25, 15), (-25, 15)], close=True)
    hx.add_line((-25, 15), (25, -15))
    hx.add_line((-25, -15), (25, 15))

    reactor = doc.blocks.new("EQ-REACTOR")
    reactor.add_lwpolyline([(-30, -25), (30, -25), (30, 20)], close=True)
    reactor.add_ellipse((0, 20), major_axis=(30, 0), ratio=0.28)
    reactor.add_line((0, 28), (0, -8))
    reactor.add_line((-14, -8), (14, -8))
    reactor.add_line((0, 28), (20, 36))

    column = doc.blocks.new("EQ-COLUMN")
    column.add_lwpolyline([(-18, -80), (18, -80), (18, 80), (-18, 80)], close=True)
    column.add_ellipse((0, 80), major_axis=(18, 0), ratio=0.3)
    column.add_ellipse((0, -80), major_axis=(18, 0), ratio=0.3)
    for y in range(-56, 61, 16):
        column.add_line((-17, y), (17, y))

    bubble = doc.blocks.new("INS-BUBBLE")
    bubble.add_circle((0, 0), 11)
    bubble.add_line((-11, 0), (11, 0))
    bubble.add_attdef("TAG", insert=(-8, -2.6), dxfattribs={"height": 2.6, "style": "HZ"})
    bubble.add_attdef("NAME", insert=(-8, -8.5), dxfattribs={"height": 2.4, "style": "HZ"})

    tank.add_attdef("TAG", insert=(-20, 0), dxfattribs={"height": 3.5, "style": "HZ"})
    tank.add_attdef("NAME", insert=(-20, -8), dxfattribs={"height": 3.0, "style": "HZ"})
    pump.add_attdef("TAG", insert=(-14, 26), dxfattribs={"height": 3.5, "style": "HZ"})
    pump.add_attdef("NAME", insert=(-14, 19), dxfattribs={"height": 3.0, "style": "HZ"})
    hx.add_attdef("TAG", insert=(-16, 18), dxfattribs={"height": 3.5, "style": "HZ"})
    hx.add_attdef("NAME", insert=(-16, 11), dxfattribs={"height": 3.0, "style": "HZ"})
    reactor.add_attdef("TAG", insert=(-28, 32), dxfattribs={"height": 3.5, "style": "HZ"})
    reactor.add_attdef("NAME", insert=(-28, 25), dxfattribs={"height": 3.0, "style": "HZ"})
    column.add_attdef("TAG", insert=(-16, 88), dxfattribs={"height": 3.5, "style": "HZ"})
    column.add_attdef("NAME", insert=(-16, 81), dxfattribs={"height": 3.0, "style": "HZ"})


def insert_equipment(msp, name, insert, tag, label, layer="EQUIPMENT"):
    ref = msp.add_blockref(name, insert, dxfattribs={"layer": layer})
    ref.add_attrib("TAG", tag, insert=(insert[0] - 20, insert[1]), dxfattribs={
        "height": 3.5, "style": "HZ", "layer": "TEXT"})
    ref.add_attrib("NAME", label, insert=(insert[0] - 20, insert[1] - 8), dxfattribs={
        "height": 3.0, "style": "HZ", "layer": "TEXT"})
    return ref


def pipe(msp, points, line_number=None, label_at=None):
    msp.add_lwpolyline(points, dxfattribs={"layer": "PIPE"})
    if line_number and label_at:
        add_text(msp, line_number, label_at, height=2.8, layer="TEXT")


def instrument(msp, insert, tag, name, leader_end):
    msp.add_line(insert, leader_end, dxfattribs={"layer": "INSTRUMENT"})
    ref = msp.add_blockref("INS-BUBBLE", insert, dxfattribs={"layer": "INSTRUMENT"})
    ref.add_attrib("TAG", tag, insert=(insert[0] - 8, insert[1] - 1.2), dxfattribs={
        "height": 2.6, "style": "HZ", "layer": "TEXT"})
    ref.add_attrib("NAME", name, insert=(insert[0] - 8, insert[1] - 7.5), dxfattribs={
        "height": 2.4, "style": "HZ", "layer": "TEXT"})
    return ref


def draw_title_block(msp) -> None:
    left, bottom, right, top = 600, 20, 821, 110
    msp.add_lwpolyline([(left, bottom), (right, bottom), (right, top), (left, top)],
                       close=True, dxfattribs={"layer": "TITLE"})
    for y in (80, 55, 32):
        msp.add_line((left, y), (right, y), dxfattribs={"layer": "TITLE"})
    for x in (660, 720, 780):
        msp.add_line((x, bottom), (x, 80), dxfattribs={"layer": "TITLE"})

    add_text(msp, "图名", (605, 91), height=3.2, layer="TITLE")
    add_text(msp, "糖浆配制工艺流程图", (668, 90), height=5.0, layer="TITLE")
    add_text(msp, "图号", (605, 66), height=3.2, layer="TITLE")
    add_text(msp, "DEMO-PFD-001", (666, 64), height=4.0, layer="TITLE")
    add_text(msp, "版本", (725, 66), height=3.2, layer="TITLE")
    add_text(msp, "A", (785, 64), height=4.0, layer="TITLE")
    add_text(msp, "日期", (605, 43), height=3.2, layer="TITLE")
    add_text(msp, "2026-11", (666, 41), height=3.6, layer="TITLE")
    add_text(msp, "比例", (725, 43), height=3.2, layer="TITLE")
    add_text(msp, "1:1", (785, 41), height=3.6, layer="TITLE")
    add_text(msp, "专业", (605, 24), height=3.2, layer="TITLE")
    add_text(msp, "工艺", (666, 23), height=3.6, layer="TITLE")
    add_text(msp, "设计", (725, 24), height=3.2, layer="TITLE")
    add_text(msp, "教学示例", (778, 23), height=3.2, layer="TITLE")


def draw_notes(msp) -> None:
    add_note(msp,
             "注：\\P本图为虚构教学示例，设备位号、仪表位号与流程均不对应任何真实装置或项目。"
             "\\P用途：练习 DWG/DXF → 结构化清单 → 审图页的完整流程。",
             (30, 92), height=3.4)
    add_note(msp,
             "管线说明：PL-101 原料进料；PL-102 预热后进料；PL-103 反应出料；"
             "PL-104 塔顶气相；PL-105 回流液。",
             (30, 62), height=3.4)


def build(path: Path) -> None:
    doc = new_document()
    msp = doc.modelspace()
    equipment_blocks(doc)

    draw_frame(msp)
    draw_title_block(msp)
    draw_notes(msp)

    insert_equipment(msp, "EQ-TANK", (110, 380), "V-101", "原料储罐")
    insert_equipment(msp, "EQ-PUMP", (220, 340), "P-101", "进料泵")
    insert_equipment(msp, "EQ-HX", (330, 380), "E-101", "预热器")
    insert_equipment(msp, "EQ-REACTOR", (470, 380), "R-101", "反应釜")
    insert_equipment(msp, "EQ-COLUMN", (650, 380), "T-101", "精馏塔")
    insert_equipment(msp, "EQ-HX", (730, 500), "E-102", "塔顶冷凝器")
    insert_equipment(msp, "EQ-TANK", (730, 420), "V-102", "回流罐")
    insert_equipment(msp, "EQ-PUMP", (730, 350), "P-102", "回流泵")

    pipe(msp, [(110, 350), (110, 310), (220, 310), (220, 324)],
         "PL-101-25-A1A", (130, 313))
    pipe(msp, [(242, 340), (300, 340), (300, 380), (305, 380)],
         "PL-102-25-A1A", (250, 344))
    pipe(msp, [(355, 380), (440, 380)],
         "PL-103-40-A1A", (378, 384))
    pipe(msp, [(500, 380), (632, 380)],
         "PL-103-40-A1A", (540, 384))
    pipe(msp, [(650, 460), (650, 500), (705, 500)],
         "PL-104-100-A1A", (655, 470))
    pipe(msp, [(730, 485), (730, 450)],
         "PL-104-100-A1A", (735, 462))
    pipe(msp, [(730, 390), (730, 362)],
         "PL-105-50-A1A", (735, 372))
    pipe(msp, [(718, 350), (650, 350), (650, 300)],
         None)

    instrument(msp, (330, 440), "TI-101", "预热出口温度", (330, 405))
    instrument(msp, (275, 268), "FIC-101", "进料流量", (258, 310))
    instrument(msp, (470, 460), "PIC-101", "反应压力", (470, 410))
    instrument(msp, (650, 500), "TI-102", "塔顶温度", (650, 470))
    instrument(msp, (110, 270), "LI-101", "储罐液位", (110, 340))
    instrument(msp, (730, 470), "LI-102", "回流罐液位", (730, 450))

    add_text(msp, "工艺流程图", (40, 540), height=8.0, layer="TEXT")
    add_text(msp, "（虚构教学示例）", (40, 525), height=4.0, layer="TEXT")

    doc.saveas(path)
    print(f"已生成 {path}")
    print(f"实体 {len(msp)} 个；图层 {len(doc.layers)} 个；块 {len(doc.blocks)} 个")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成虚构工艺流程图示例 DXF")
    parser.add_argument("-o", "--output", default="sample-pfd.dxf", help="输出文件路径")
    args = parser.parse_args()
    try:
        build(Path(args.output))
    except Exception as error:  # noqa: BLE001 - 命令行工具，直接给出原因
        print(f"生成失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
