---
title: 让 Harness 读懂图层、块和文字
audience: dad
status: active
summary: 用 info、texts 和 drawing.inspect 读出图层、块、属性、文字和 handle，让每条结论都能指回证据。
---
上一讲装好了工具，也看到了一张图。这一讲练「读准」：先把图里的结构读出来，AI 的每条结论都要能指回某个 handle、图层或原文。

### 1. 先看总览

```sh
~/CAD-Work/tools/cad info ~/CAD-Work/originals/sample-pfd.dxf
```

重点看：

| 字段 | 含义 |
|---|---|
| `entityCount` | 模型和布局里的实体数 |
| `counts` | 按类型计数：Line、Polyline、Text、MText、Block Reference 等 |
| `layers` | 图层名、颜色、线型、开/关、冻结、锁定 |
| `blocks` | 块定义名 |
| `readNotes` / `skipped` | 读取时跳过了什么；不为空要先弄清原因 |

如果 `readNotes` 或 `skipped` 非空，先把内容记进 `notes/`，不要继续往下猜。

### 2. 读文字和块属性

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'texts {"limit":500}'
```

每一行是一条文字：`handle`、`type`、`layer`、`text`、插入点、字号和样式。块属性会多一个 `tag`，例如设备 `E4` 上的 `TAG = V-101`、`NAME = 原料储罐`。

可以用过滤缩小范围：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'texts {"layer":"TITLE"}'
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'texts {"contains":"V-101"}'
```

### 3. 读实体和 handle

`drawing.inspect` 返回实体、图层、几何和 handle。图纸大时一定加 `limit`，不要一次打印全部：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/originals/sample-pfd.dxf --cmd 'drawing.inspect {"entities":true,"limit":80}'
```

先看清三类东西：

- `type`：Block Reference / Polyline / Line / Text / MText；
- `layer`：这个实体在哪一层；
- `handle`：以后修改时用它定位，不能靠「大概在那个位置」。

### 4. 让 Harness 带着证据复述

把输出交给 Harness 时，先把规矩说清楚：

```text
当前工作区是 ~/CAD-Work/。请只读 originals/sample-pfd.dxf，不要修改任何文件。
请用 tools/cad 读取这张图，先报告你实际运行了哪几条命令。
然后回答：
1. 实体数、图层数、块定义数；
2. 每个图层的名字和用途（只根据图层名和该层实体判断）；
3. 设备、仪表的位号与名称，每条给出 handle；
4. 图框里的图名、图号、版本、日期，每条给出 handle；
5. readNotes/skipped 里有没有需要先处理的内容。
不要推断管线连接，不要补猜缺失位号；文件里没有的写「无法从文件确认」。
```

Harness 的每条结论都应该能对回 `texts` 或 `drawing.inspect` 里的一行。对不上就让它重读，不要接受「看起来像」。

### 5. 在 App 里核对

打开 CADCraft App，打开同一张 DXF：

1. 看图层管理器，图层数应与 `info` 一致；
2. 选中一台设备，看属性里的 TAG/NAME 是否与 `texts` 一致；
3. 抽 3 个 handle，在 `drawing.inspect` 输出里找到对应实体，并确认几何位置。

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

`texts` 里块属性的 `handle` 是**块参照的 handle**，不是属性自己的独立 handle。下一讲修改属性时要对这个 handle 用 `attedit`，不能用 `properties.set` 改 `text`。先记住这条，下一讲会实测对比。

### 检查清单

- [ ] `info` 的实体数、图层数、块数与 App 对得上。
- [ ] `texts` 能看到设备/仪表位号和图框文字。
- [ ] 抽 3 个 handle，在 `drawing.inspect` 里找到并核对位置。
- [ ] `readNotes`/`skipped` 已记录或解释。
- [ ] 写完了 `notes/sample-pfd-阅读.md`。
- [ ] 没有把 AI 的推断当成文件事实。

上一讲：[装好 CADCraft 和命令行](01-install-and-inspect.md) · 下一讲：[按 handle 改图并核对](03-edit-and-verify.md)。

备查：[CLI 文档](https://github.com/storytold/cadcraft/blob/main/docs/cli.md) · [MCP 文档](https://github.com/storytold/cadcraft/blob/main/docs/mcp.md)
