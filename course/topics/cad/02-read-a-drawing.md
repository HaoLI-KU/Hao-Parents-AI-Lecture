---
title: 让 Harness 读懂图层、块和文字
audience: dad
status: active
summary: 用自然语言让 Harness 读取图层、块、属性、文字和 handle，每条结论都能指回证据；命令由 Harness 执行，父亲负责核对。
---
上一讲装好了工具，也看到了一张图。这一讲练「读准」：你对 Harness 说清楚要什么，它负责运行命令；你负责让它给证据，并在 CADCraft 里核对。

不需要记命令。下面的提示词可以直接复制；命令块是「Harness 会执行什么」的备查记录。

### 1. 先让它读总览

在 `~/CAD-Work` 工作区里发：

```text
只读 originals/sample-pfd.dxf，不要修改任何文件。
请运行 tools/cad info，报告：实体数、每个类型的计数、图层清单、块定义、textStyles，以及 readNotes 和 skipped。
先列出你实际运行的完整命令，再给结论。
```

它应该报告 **62 个实体、9 个图层、9 个块**。重点看：

| 字段 | 含义 |
|---|---|
| `entityCount` | 模型和布局里的实体数 |
| `counts` | 按类型计数：Line、Polyline、Text、MText、Block Reference 等 |
| `layers` | 图层名、颜色、线型、开/关、冻结、锁定 |
| `blocks` | 块定义名 |
| `readNotes` / `skipped` | 读取时跳过了什么；不为空要先弄清原因 |

如果 `readNotes` 或 `skipped` 非空，让它把内容列出来并记进 `notes/`，不要继续往下猜。

### 2. 读文字和块属性

```text
继续只读 originals/sample-pfd.dxf。
运行 texts（limit 500），给我设备、仪表位号和名称，每条带 handle、图层和原文。
再单独列出图框里的图名、图号、版本和日期，同样带 handle。
不要推断管线连接，不要补猜缺失位号；文件里没有的写「无法从文件确认」。
```

它应该给出设备/仪表属性，例如 `E4` 上的 `TAG = V-101`、`NAME = 原料储罐`，以及图框文字和 handle。

可以继续追问某个范围：

```text
只列 TITLE 图层的文字，并告诉我这条命令实际是怎么写的。
```

### 3. 读实体和 handle

```text
继续只读 originals/sample-pfd.dxf。
运行 drawing.inspect（entities: true，limit 80），给我：
1. 每个图层的实体数；
2. 设备、仪表块参照的 handle、图层、插入点；
3. 哪些实体是 Polyline/Line/Text/MText。
只报告摘要和关键 handle，不要粘贴整份 JSON。
```

先看清三类东西：

- `type`：Block Reference / Polyline / Line / Text / MText；
- `layer`：这个实体在哪一层；
- `handle`：以后修改时用它定位，不能靠「大概在那个位置」。

### 4. 让结论带上证据

把下面这段作为这一讲的核对规则：

```text
从现在开始，每条结论后面写清楚证据：handle、图层或原文。
对不上的结论请重读一遍再回答，不要用「看起来像」代替证据。
如果你无法从文件确认，写「无法从文件确认」。
```

检查它的回答：

- 位号有没有 handle；
- 图框信息有没有原文；
- 图层用途是不是只根据图层名和该层实体判断；
- 有没有把管线连接当成事实。

### 5. 在 App 里核对

打开 CADCraft App，打开同一张 DXF：

1. 看图层管理器，图层数应与 `info` 一致；
2. 选中一台设备，看属性里的 TAG/NAME 是否与 Harness 的报告一致；
3. 抽 3 个 handle，让 Harness 说出对应实体的位置，你到 App 里找到并确认。

把手动核对结果写进 `~/CAD-Work/notes/sample-pfd-阅读.md`：

```markdown
# sample-pfd 阅读记录
- 实体/图层/块：
- 设备位号与 handle：
- 仪表位号与 handle：
- 图框信息：
- readNotes/skipped：
- 我核对过的 3 个 handle：
```

### 6. 关于块属性的一个坑

`texts` 里块属性的 `handle` 是**块参照的 handle**，不是属性自己的独立 handle。下一讲修改属性时要让 Harness 对这个 handle 用 `attedit`，不能用 `properties.set` 改 `text`。下一讲会实测对比。

### 7. 备查命令：读图

```sh
~/CAD-Work/tools/cad info ~/CAD-Work/originals/sample-pfd.dxf
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'texts {"limit":500}'
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'texts {"layer":"TITLE"}'
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'drawing.inspect {"entities":true,"limit":80}'
```

### 检查清单

- [ ] 我只用自然语言就让它读出了实体数、图层数和块数。
- [ ] `info` 的数字与 App 对得上。
- [ ] Harness 给出的每个位号和图框信息都有 handle 或原文。
- [ ] 抽 3 个 handle，在 App 里核对过位置。
- [ ] `readNotes`/`skipped` 已记录或解释。
- [ ] 写完了 `notes/sample-pfd-阅读.md`。
- [ ] 没有把 AI 的推断当成文件事实。

上一讲：[装好 CADCraft 和命令行](01-install-and-inspect.md) · 下一讲：[按 handle 改图并核对](03-edit-and-verify.md)。

备查：[CLI 文档](https://github.com/storytold/cadcraft/blob/main/docs/cli.md) · [MCP 文档](https://github.com/storytold/cadcraft/blob/main/docs/mcp.md)
