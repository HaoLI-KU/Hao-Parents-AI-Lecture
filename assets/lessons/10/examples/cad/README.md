# CAD 审图小工具（虚构示例）

这里放的是爸爸第 10–12 节用到的三个脚本和一张**虚构**的工艺流程图示例。真实 AutoCAD 图纸、真实位号和厂名一律留在本机私有目录，不进入这个仓库。

## 文件

| 文件 | 作用 |
|---|---|
| `make_sample_pfd.py` | 生成虚构的「糖浆配制工艺流程图」示例 DXF，可重复运行 |
| `sample-pfd.dxf` | 上面脚本生成的示例图纸（R2018，含中文） |
| `cad_inventory.py` | 只读 DXF，输出结构化清单 `inventory/*.json`、`*.md` 和台账 `ledger.csv` |
| `make_review_sheet.py` | 把 DXF 生成一页自包含的审图 HTML（几何 + 中文标签 + 编号热点 + 图层开关 + 缩放 + 批注） |
| `sample-review.html` | 由示例 DXF 生成的审图页，可在浏览器或 DeepSeek Harness 预览中直接打开 |
| `requirements.txt` | 依赖版本 |

## 环境

需要 Python 3.9 或更新版本。建议在私有工作目录里单独建环境，不动仓库和网站的 `.venv`：

```sh
python3 -m venv .venv-cad
.venv-cad/bin/python -m pip install -r requirements.txt
```

## 用法

先在示例上跑一遍：

```sh
.venv-cad/bin/python make_sample_pfd.py -o sample-pfd.dxf
.venv-cad/bin/python cad_inventory.py sample-pfd.dxf -o inventory
.venv-cad/bin/python make_review_sheet.py sample-pfd.dxf -o review.html \
  --title "糖浆配制工艺流程图（虚构示例）"
```

再换成自己的图纸：

```sh
.venv-cad/bin/python cad_inventory.py dxf/ -o inventory
.venv-cad/bin/python make_review_sheet.py dxf/DEMO-PFD-001.dxf -o review/DEMO-PFD-001.html
```

`cad_inventory.py` 也可以尝试直接读 DWG：先装 [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter)，并让 `ODAFileConverter` 命令在 PATH 里（本仓库不附带转换器）。转换器不可用时，仍建议先在 AutoCAD 里另存 DXF。

## 读得懂什么、读不懂什么

- **能精确读到**：文字、块名、块属性、图层、尺寸标注、布局、每个实体的 handle。这是矢量数据，不是 OCR。
- **读不到或不可靠**：管线之间的连接关系。DXF 的线只是线段，连接语义要靠人判断；脚本和 AI 只能给「疑似」。
- **可能不完整**：未绑定的外部参照（XREF）、AutoCAD 代理对象、加密文件、缺失的 SHX 字体。脚本会把这些写进 `warnings`，不静默跳过。
- 中文：R2004 及以前的 DXF 由 `$DWGCODEPAGE` 决定编码（国产图纸常见 `ANSI_936`），R2007 以后是 UTF-8；自动识别失败时用 `--encoding gbk` 重试。

## 隐私

- 脚本只读输入文件，不修改任何原图。
- 生成的清单、审图页和批注都写在你自己指定的输出目录。
- 公开课稿和本仓库只用虚构示例；真实图纸、位号和厂名不要放进仓库、截图或公开网页。

## 限制与取舍

- 审图页默认按图层分开渲染矢量 SVG，所以可以逐层显示/隐藏；图层特别多或图元特别大的图纸会慢一些，可以先用 `--layout` 指定布局。
- 中文文字不依赖 AutoCAD 的 SHX 字体：几何由 DXF 渲染，文字由识别的字符串单独叠加，所以中文一定能显示。
- 批注存在浏览器 localStorage，可导出 JSON；在 DeepSeek Harness 里也可以直接用已安装的「点选批注」浮层。
