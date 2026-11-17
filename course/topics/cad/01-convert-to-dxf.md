---
title: 把 DWG 变成可精确读取的 DXF
audience: dad
status: active
summary: 建立私有图纸目录，把 DWG 另存或批量转成 DXF，然后生成第一份结构化清单和覆盖报告。
---
这一讲开始，所有自动化都在**文件**上做：读取 DXF 里的图层、块、实体、属性和 handle，不向 AutoCAD 窗口键入任何命令。AutoCAD 只负责你自己打开、查看和核对。

先明确一件事：我们不是让 AI「看图猜」，而是让它读到图纸的矢量数据。第一步就是把 DWG 变成 DXF。

### 1. 建一个只放工作副本的私有目录

在 Finder 的「文稿」里新建 `CAD-Review/`，真实图纸和所有产出都留在这里，不进课程仓库。

```text
CAD-Review/
├── original/     AutoCAD 原件，只读，不覆盖
├── dxf/          另存或转换出来的 DXF
├── toolkit/      本课下载的工具箱
├── inventory/    结构化清单
├── work/         修改后的副本
├── review/       审图页与批注
└── notes/        每张图的核对记录
```

也可以在 Harness 里说「当前工作区是 CAD-Review/，只创建 original、dxf、toolkit、inventory、work、review、notes 七个空目录，不要复制或移动现有文件」。

### 2. 在 AutoCAD 里另存为 DXF（主路线）

1. 在 AutoCAD 打开要整理的图纸，先记下图号、图名和版本。
2. 选「文件 → 另存为」，文件类型选 **AutoCAD 2018 DXF (\*.dxf)**，存到 `CAD-Review/dxf/`。菜单名称以你本机版本为准；命令行 `DXFOUT` 也可以。
3. 文件名用图号，例如 `DEMO-PFD-001.dxf`，后面的清单、计划、审图页都用同一个名字。
4. 图纸引用了外部参照（XREF）时，先在 AutoCAD 里用 `XREF` 面板绑定再另存；未绑定的参照不会进入 DXF。
5. 确认原件没有被覆盖。同目录里多出来的 `.bak` 或 `.dxf` 只是副本。

### 3. 批量转换（可选）

图纸很多时，可以让程序批量转换，但需要先装 [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter)（官方免费，选 macOS 13 以上、Apple 芯片版）。装好后：

```sh
python3 toolkit/cad.py convert original/ -o dxf/ --to dxf
```

没有安装时，命令会打印手动步骤，不会假装转换成功。Homebrew 的 `libredwg`（`dwg2dxf`）只作最后手段，结果必须逐张核对。

### 4. 准备工具箱环境

1. 下载工具箱：[cad.py](../../../assets/topics/cad/toolkit/cad.py)、[cad_inventory.py](../../../assets/topics/cad/toolkit/cad_inventory.py)、[cad_edit.py](../../../assets/topics/cad/toolkit/cad_edit.py)、[make_review_sheet.py](../../../assets/topics/cad/toolkit/make_review_sheet.py)、[requirements.txt](../../../assets/topics/cad/toolkit/requirements.txt)，放进 `CAD-Review/toolkit/`。
2. 在 `CAD-Review/` 里建独立环境：

```sh
python3 -m venv .venv-cad
.venv-cad/bin/python -m pip install -r toolkit/requirements.txt
```

3. 先跑一次自检，确认读、改、校验三条链路都正常：

```sh
.venv-cad/bin/python toolkit/cad.py selftest
```

自检会在一张虚构示例上跑完整流程，最后输出「自检全部通过」。任何一项失败，先修环境或把报错记进 `notes/`，不要继续。

### 5. 生成第一份清单

先拿虚构示例练手，再换成自己的图。示例可以下载：[sample-pfd.dxf](../../../assets/topics/cad/examples/sample-pfd.dxf)。

```sh
.venv-cad/bin/python toolkit/cad.py inventory dxf/DEMO-PFD-001.dxf -o inventory
```

打开 `inventory/DEMO-PFD-001.md`，再打开同名 `.json`。先看四件事：

| 先看什么 | 在哪里 |
|---|---|
| 文件 sha256、DXF 版本、编码、审计结果 | `.json` 开头与 `.md` 顶部 |
| 图层表：每层实体数、零实体图层 | `.md` 的图层表 |
| 块：定义、引用次数、属性标签 | `.md` / `.json` 的 `blocks`、`block_attrib_tags` |
| 异常：外部参照、代理对象、缺失字体、空图层 | `warnings` |

### 6. 只读清单，让 Harness 复述事实

```text
当前工作区是 CAD-Review/。请只读 inventory/ 里的清单文件，先报告你实际打开了哪几个文件。
然后只根据文件内容回答：
1. 图框里的图名、图号、版本、日期；
2. 图层表里每层的实体数，哪些图层没有实体；
3. 设备位号与名称、仪表位号与名称；
4. 位号候选里哪些像管线号、哪些像设备或仪表位号；
5. warnings 里有哪些异常，各自影响什么。
每条结论注明来自哪条文字或哪个 handle。文件里没有的写「无法从文件确认」，不要补猜，也不要评价工艺。
```

### 7. 亲手核对

打开 AutoCAD 原图，对照清单：

| 核对什么 | 清单里怎么写 | 原图里怎么看 |
|---|---|---|
| 图名、图号 | 标题栏文字与 handle | 打开图框逐字对照 |
| 图层数量 | 图层表的行数 | 图层管理器里的图层数 |
| 某层实体数 | 该图层行的实体数 | 关闭其他图层，数该层图元 |
| 设备/仪表位号 | 设备、仪表清单的 TAG 与 handle | 在图上找到该位号 |

核对结果写进 `notes/<图号>-阅读.md`：这张图能不能完整读出、哪些内容没读到、编码和外部参照有没有问题。

### 检查清单

- [ ] `CAD-Review/` 七个目录已建好，原件只读。
- [ ] 至少一张图另存为 AutoCAD 2018 DXF，文件名用图号。
- [ ] 外部参照已绑定，或已在笔记里记录未绑定情况。
- [ ] `.venv-cad` 可用，`cad.py selftest` 全部通过。
- [ ] 生成了 `inventory/<图号>.json` 与 `.md`，warnings 逐条看过。
- [ ] Harness 的复述能指回 handle，没有补猜。
- [ ] 至少核对了图名、图层数和两个位号。

下一讲：[精确读懂一张图](02-read-a-drawing.md)。

备查：[ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) · [ezdxf 文档](https://ezdxf.mozman.at/) · [工具箱说明](../../../assets/topics/cad/toolkit/README.md)
