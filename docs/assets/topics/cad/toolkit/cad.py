#!/usr/bin/env python3
"""AutoCAD 图纸代码流工具箱的统一入口。

所有操作只在 DXF 文件上做，不向 AutoCAD 窗口键入任何命令；AutoCAD 只用来人工查看和核对。

    python3 cad.py inventory <dxf|目录> [-o inventory/]
    python3 cad.py convert <dwg|dxf> [-o 输出目录] [--to dwg|dxf]
    python3 cad.py check-plan <plan.json> --drawing <dxf>
    python3 cad.py apply <plan.json> --drawing <dxf> [--dry-run] [--out 新文件.dxf]
    python3 cad.py review <dxf> [-o review.html] [--title 标题]
    python3 cad.py selftest
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cad_edit  # noqa: E402
import cad_inventory  # noqa: E402

ODA_PATHS = (
    "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",
    "/Applications/ODAFileConverter/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",
)


def find_oda() -> str | None:
    found = shutil.which("ODAFileConverter")
    if found:
        return found
    return next((path for path in ODA_PATHS if Path(path).is_file()), None)


def cmd_inventory(args) -> int:
    source = Path(args.source).expanduser()
    if not source.exists():
        print(f"找不到：{source}", file=sys.stderr)
        return 1
    files = sorted([*source.rglob("*.dxf"), *source.rglob("*.DXF"),
                    *source.rglob("*.dwg"), *source.rglob("*.DWG")]) if source.is_dir() else [source]
    outdir = Path(args.out).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    import csv

    ledger = []
    for path in files:
        print(f"读取 {path.name} …")
        try:
            data = cad_inventory.collect(path, args.encoding, args.tag_pattern, args.title_layer)
        except SystemExit as error:
            print(f"  跳过：{error}", file=sys.stderr)
            ledger.append({"file": path.name, "error": str(error)})
            continue
        cad_inventory.write_json(data, outdir / f"{path.stem}.json")
        cad_inventory.write_markdown(data, outdir / f"{path.stem}.md")
        counts = data["counts"]
        ledger.append({
            "file": path.name, "dxf_version": data["dxf_version"],
            "entities": counts["entities"], "texts": counts["texts"],
            "inserts": counts["inserts"], "equipment": counts["equipment"],
            "instruments": counts["instruments"], "tags": counts["tags"],
            "warnings": len(data["warnings"]),
        })
        print(f"  实体 {counts['entities']}，文字 {counts['texts']}，"
              f"设备 {counts['equipment']}，仪表 {counts['instruments']}，"
              f"图层 {data['coverage']['layers']}，异常 {len(data['warnings'])}")
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


def cmd_convert(args) -> int:
    source = Path(args.source).expanduser()
    if not source.exists():
        print(f"找不到：{source}", file=sys.stderr)
        return 1
    oda = find_oda()
    if not oda:
        print("没有找到 ODA File Converter。", file=sys.stderr)
        print("请先安装：https://www.opendesign.com/guestfiles/oda_file_converter", file=sys.stderr)
        print("或者：在 AutoCAD 里打开图纸，另存为 AutoCAD 2018 DXF。", file=sys.stderr)
        return 3
    target = "DWG" if args.to == "dwg" else "DXF"
    outdir = Path(args.out).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [oda, str(source.parent), str(outdir), "ACAD2018", target, "0", "1"],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        print(f"转换失败：{result.stderr.strip() or result.stdout.strip()}", file=sys.stderr)
        return 1
    print(f"已请求 {source.name} -> {target}，输出目录 {outdir}")
    return 0


def cmd_check_plan(args) -> int:
    try:
        plan = cad_edit.load_plan(Path(args.plan))
        doc = cad_edit.load_drawing(Path(args.drawing))
        resolved = cad_edit.plan_check(doc, plan)
    except cad_edit.PlanError as error:
        print(f"计划失败：{error}", file=sys.stderr)
        return 2
    print(f"计划可执行：{len(resolved)} 条操作")
    for item in resolved:
        print(f"- {item['id']}: {item['op']} handle={item.get('handle', '(新增)')}")
    return 0


def cmd_apply(args) -> int:
    try:
        report = cad_edit.run(
            Path(args.drawing), Path(args.plan),
            Path(args.out) if args.out else None, args.dry_run,
        )
    except cad_edit.PlanError as error:
        print(f"计划失败：{error}", file=sys.stderr)
        return 2
    print(cad_edit.render_markdown(report))
    if not args.dry_run and report.get("output"):
        report_path = Path(args.report) if args.report else Path(report["output"]).with_suffix(".report.md")
        report_path.write_text(cad_edit.render_markdown(report), encoding="utf-8")
        print(f"报告：{report_path}")
    return 0 if report["ok"] else 1


def cmd_review(args) -> int:
    script = HERE / "make_review_sheet.py"
    command = [sys.executable, str(script), args.drawing]
    if args.out:
        command += ["-o", args.out]
    if args.title:
        command += ["--title", args.title]
    if args.colors:
        command += ["--colors"]
    return subprocess.run(command).returncode


def cmd_selftest(args) -> int:
    failures: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        print(f"[{'通过' if condition else '失败'}] {name}{('：' + detail) if detail else ''}")
        if not condition:
            failures.append(name)

    with tempfile.TemporaryDirectory(prefix="cad-selftest-") as tmp:
        work = Path(tmp)
        sample = HERE.parent / "examples" / "sample-pfd.dxf"
        if not sample.is_file():
            subprocess.run([sys.executable, str(HERE.parent / "examples" / "make_sample_pfd.py"),
                            "-o", str(work / "sample-pfd.dxf")], check=True)
            sample = work / "sample-pfd.dxf"
        data = cad_inventory.collect(sample, None, cad_inventory.DEFAULT_TAG_PATTERN)
        counts = data["counts"]
        check("读取实体", counts["entities"] == 62, str(counts["entities"]))
        check("读取设备", counts["equipment"] == 8, str(counts["equipment"]))
        check("读取仪表", counts["instruments"] == 6, str(counts["instruments"]))
        check("图层覆盖", data["coverage"]["layers"] >= 9, str(data["coverage"]["layers"]))
        check("无异常", not data["warnings"], "; ".join(data["warnings"]))

        plan = work / "plan.json"
        plan.write_text(json.dumps({
            "drawing": sample.name,
            "operations": [
                {"id": "layer", "op": "set_layer", "handle": "E4",
                 "expect": {"type": "INSERT", "layer": "EQUIPMENT", "tag": "V-101"}, "to": "EQ-REVIEW"},
                {"id": "name", "op": "set_attribute", "handle": "E4",
                 "expect": {"tag": "V-101", "name": "原料储罐"}, "tag": "NAME", "to": "原料罐"},
                {"id": "move", "op": "move", "handle": "114",
                 "expect": {"layer": "INSTRUMENT", "insert": [330.0, 440.0]}, "delta": [0, -10]},
                {"id": "add", "op": "add_polyline", "layer": "REVIEW",
                 "points": [[520, 300], [560, 300]]},
            ],
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        out = work / "edited.dxf"
        report = cad_edit.run(sample, plan, out, dry_run=False)
        check("修改校验", report["ok"], "; ".join(
            f"{item['name']} {item['detail']}" for item in report["checks"] if not item["ok"]))
        check("输入未变", cad_edit.sha256(sample) == report["input_sha256"])

        bad = work / "bad.json"
        bad.write_text(json.dumps({
            "operations": [{"id": "bad", "op": "set_layer", "handle": "E4",
                            "expect": {"layer": "WRONG"}, "to": "X"}],
        }), encoding="utf-8")
        try:
            cad_edit.run(sample, bad, work / "bad.dxf", dry_run=True)
            check("守卫失败中止", False, "没有报错")
        except cad_edit.PlanError:
            check("守卫失败中止", True)

        dry_out = work / "dry.dxf"
        cad_edit.run(sample, plan, dry_out, dry_run=True)
        check("dry-run 不写文件", not dry_out.exists())
    print("")
    if failures:
        print(f"自检失败：{len(failures)} 项")
        return 1
    print("自检全部通过。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoCAD 图纸代码流工具箱")
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory", help="生成结构化清单与覆盖报告")
    inventory.add_argument("source")
    inventory.add_argument("-o", "--out", default="inventory")
    inventory.add_argument("--encoding", default=None)
    inventory.add_argument("--tag-pattern", default=cad_inventory.DEFAULT_TAG_PATTERN)
    inventory.add_argument("--title-layer", default="TITLE")
    inventory.set_defaults(func=cmd_inventory)

    convert = sub.add_parser("convert", help="用 ODA File Converter 批量转换 DWG/DXF")
    convert.add_argument("source")
    convert.add_argument("-o", "--out", default="dxf")
    convert.add_argument("--to", choices=("dxf", "dwg"), default="dxf")
    convert.set_defaults(func=cmd_convert)

    check = sub.add_parser("check-plan", help="检查修改计划与守卫")
    check.add_argument("plan")
    check.add_argument("--drawing", required=True)
    check.set_defaults(func=cmd_check_plan)

    apply_cmd = sub.add_parser("apply", help="应用计划并写新文件、自动校验")
    apply_cmd.add_argument("plan")
    apply_cmd.add_argument("--drawing", required=True)
    apply_cmd.add_argument("--out", default=None)
    apply_cmd.add_argument("--report", default=None)
    apply_cmd.add_argument("--dry-run", action="store_true")
    apply_cmd.set_defaults(func=cmd_apply)

    review = sub.add_parser("review", help="生成审图页")
    review.add_argument("drawing")
    review.add_argument("-o", "--out", default=None)
    review.add_argument("--title", default=None)
    review.add_argument("--colors", action="store_true")
    review.set_defaults(func=cmd_review)

    selftest = sub.add_parser("selftest", help="用虚构示例跑完整链路自检")
    selftest.set_defaults(func=cmd_selftest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
