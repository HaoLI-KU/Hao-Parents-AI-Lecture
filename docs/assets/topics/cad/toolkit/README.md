# CAD 代码流工具箱

这套工具把 AutoCAD 图纸当作**文件**来处理，不操作 AutoCAD 窗口：读取靠 DXF 矢量数据，修改靠可审阅的 JSON 计划，写完自动重读校验。AutoCAD 只负责人工查看、核对和另存 DWG。

仓库里只有虚构示例；真实图纸、清单、计划和报告都留在本机私有目录（例如 `~/Documents/CAD-Review/`）。

## 环境

需要 Python 3.9+：

```sh
python3 -m venv .venv-cad
.venv-cad/bin/python -m pip install -r requirements.txt
```

## 六条命令

```sh
# 1. 生成结构化清单 + 覆盖报告 + 台账
python3 cad.py inventory dxf/ -o inventory

# 2. 可选：用 ODA File Converter 批量 DWG <-> DXF（未安装时会给出手动步骤）
python3 cad.py convert original/ -o dxf/ --to dxf

# 3. 检查修改计划：逐条核对 handle 和“修改前状态”
python3 cad.py check-plan plan.json --drawing dxf/DEMO-PFD-001.dxf

# 4. 只看差异，不写文件
python3 cad.py apply plan.json --drawing dxf/DEMO-PFD-001.dxf --dry-run

# 5. 写新文件并自动重读校验
python3 cad.py apply plan.json --drawing dxf/DEMO-PFD-001.dxf \
  --out work/DEMO-PFD-001-edit.dxf

# 6. 生成审图页（浏览器或 DSH 预览里看，可点热点、写批注）
python3 cad.py review dxf/DEMO-PFD-001.dxf -o review/DEMO-PFD-001.html

# 用虚构示例跑完整链路自检
python3 cad.py selftest
```

## 读取：清单里有什么

`inventory/<图号>.json` / `.md` 记录：

- 文件 sha256、DXF 版本、编码、审计结果；
- 图层表全量（颜色、线型、开/关、冻结、锁定、每层实体数），零实体图层单列；
- 块定义、引用次数、属性标签、未引用块；
- 按实体类型的计数；
- TEXT/MTEXT/ATTRIB 的原文、图层、位置、handle；
- 标为 `TITLE` 图层的标题栏文字（图名、图号、版本、日期）；
- 位号候选（默认正则 `[A-Z]{1,4}-\d{2,4}`）；
- 异常：未绑定外部参照、代理对象、缺失字体、审计错误、空图层。

`ledger.csv` 是多张图的台账。读到什么写什么，读不到的项目进 `warnings`，不静默跳过。

## 修改：计划格式

```json
{
  "drawing": "sample-pfd.dxf",
  "operations": [
    {"id": "layer-v101", "op": "set_layer", "handle": "E4",
     "expect": {"type": "INSERT", "layer": "EQUIPMENT", "tag": "V-101"},
     "to": "EQ-REVIEW"},
    {"id": "name-v101", "op": "set_attribute", "handle": "E4",
     "expect": {"tag": "V-101", "name": "原料储罐"},
     "tag": "NAME", "to": "原料罐"},
    {"id": "new-line", "op": "add_polyline", "layer": "REVIEW",
     "points": [[520, 300], [560, 300]]}
  ]
}
```

支持：`set_layer`、`move`、`delete`、`set_attribute`、`replace_text`、`set_color`、`rename_layer`、`add_line`、`add_polyline`、`add_circle`、`add_text`。

规则：

- 除新增操作外，每条都必须带 `handle` 和 `expect` 守卫；任何一条与当前图纸不符，整体中止，不写文件。
- `--dry-run` 只输出前后对照。
- 正式执行只写新文件，绝不覆盖输入。
- 写盘后重新打开：逐项检查计划、未涉及实体的哈希、实体数增量、审计；任一项失败返回非零。
- 报告默认写在输出文件旁：`<输出>.report.md`；含输入/输出 sha256、操作表、校验表。

## 目录与文件

| 文件 | 作用 |
|---|---|
| `cad.py` | 统一命令行入口 |
| `cad_inventory.py` | 读取、覆盖报告、清单与台账 |
| `cad_edit.py` | 计划校验、dry-run、应用、重读校验 |
| `make_review_sheet.py` | 自包含审图页（SVG + 标签 + 热点 + 批注） |
| `../examples/` | 虚构示例 DXF、示例计划、示例报告、审图页 |
| `requirements.txt` | ezdxf、Pillow |

## 边界

- 不向 AutoCAD 键入命令，不需要辅助功能权限，不抢占焦点。
- 只支持 DXF；DWG 需要先在 AutoCAD 里另存 DXF，或安装 [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) 用 `convert`。
- 管线连接关系仍是「疑似」，需要人工判断；工具箱不把它写成事实。
- 动态块、代理对象、外部参照、缺失 SHX 字体可能读不全，报告会明确指出。
- 大图纸建议用 `inventory` 按层核对，审图页默认限制热点数。
