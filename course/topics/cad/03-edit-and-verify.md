---
title: 按 handle 改图，写副本并核对
audience: dad
status: active
summary: 用三段自然语言完成「先计划、再执行、最后核对」；Harness 运行 attedit、properties.set、move、erase 和 saveas，父亲只确认和核对。
---
这一讲开始动图。你只需要说三段话：**先要计划，确认后执行，最后核对**。命令由 Harness 运行；它必须先给你 handle、当前值、目标值和保真门槛，等你说「执行」才动手。

### 1. 第一段：只要计划

在 `~/CAD-Work` 工作区里发：

```text
工作区是 ~/CAD-Work/。请只读 originals/sample-pfd.dxf，不要修改任何文件。
先把原件复制成 work/sample-pfd.dxf（只复制，不修改）。
然后给我一份修改计划，目标是：
- 把 V-101 的 NAME 从「原料储罐」改成「原料罐」；
- 把图名「糖浆配制工艺流程图」改成「糖浆配制流程（审核版）」；
- 把 V-101 移到 EQ-REVIEW 图层；
- 把 TI-101 下移 10 个单位；
- 删除 TI-102。
计划里每条写：handle、当前值、目标值、将运行的命令、如何核对。
还要先说明保真门槛怎么做。现在不要执行任何修改，等我确认。
```

它应该先运行 `info`/`texts`/`drawing.inspect` 找 handle，然后给出计划。你要逐条确认：

- handle 对不对（可以让它在 App 里说出位置）；
- 改的值是不是你要的；
- 有没有顺带改别的东西；
- 删除的对象是不是确定要删。

如果它直接开始改，立刻说「停，先只给计划」。

### 2. 第二段：确认后执行

确认计划后发：

```text
按刚才的计划执行。只改 work/ 的副本，不碰 originals/。
先对 work/sample-pfd.dxf 跑 roundtrip --same-format，把报告目录放在 work/roundtrip-sample；
如果 geometry、objects、table records 或 layouts 有丢失，就停下报告，不要继续。
保真通过后按顺序执行修改，saveas 到 work/sample-pfd-edit-<今天日期>.dxf，version 2018。
每一步报告实际运行的命令和 JSON 结果；不要用 --in-place。
```

它会运行 `attedit`、`properties.set`、`move`、`erase`、`saveas`。看到 `error` 就让它停下；看到 `nonPortableFonts` 是字体提示，不是保存失败。

### 3. 第三段：重读核对

```text
重读 work/sample-pfd-edit-<日期>.dxf，不要修改它。请核对：
1. 实体数应是 61（原来 62，删除 1 个）；
2. V-101 的 NAME 是「原料罐」，图层是 EQ-REVIEW；
3. 图名是「糖浆配制流程（审核版）」；
4. TI-101 的 y 坐标从 440 变成 430；
5. TI-102 已不存在；
6. 导出修改前后两张 PNG 到 preview/；
7. 报告 originals/sample-pfd.dxf 的 sha256，确认原件没变。
把每条检查的实际命令和结果写进 notes/sample-pfd-修改.md。
```

打开前后两张 PNG，在 CADCraft App 里对照图层、位号、文字和位置。原件哈希应与第一讲记录的一致。

### 4. 备查命令：修改与核对

计划阶段：

```sh
cp ~/CAD-Work/originals/sample-pfd.dxf ~/CAD-Work/work/sample-pfd.dxf
~/CAD-Work/tools/cad info ~/CAD-Work/work/sample-pfd.dxf
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf --cmd 'texts {"contains":"V-101"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf --cmd 'drawing.inspect {"entities":true,"limit":80}'
```

执行阶段：

```sh
~/CAD-Work/tools/cad roundtrip ~/CAD-Work/work/sample-pfd.dxf --same-format --out ~/CAD-Work/work/roundtrip-sample
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'attedit {"handle":"E4","values":{"NAME":"原料罐"}}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'properties.set {"handles":["D5"],"text":"糖浆配制流程（审核版）"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'properties.set {"handles":["E4"],"layer":"EQ-REVIEW"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'move {"handles":["114"],"delta":[0,-10]}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'erase {"handles":["123"]}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'saveas {"path":"work/sample-pfd-edit-20261123.dxf","version":2018}'
```

核对阶段：

```sh
~/CAD-Work/tools/cad info ~/CAD-Work/work/sample-pfd-edit-20261123.dxf
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd-edit-20261123.dxf --cmd 'texts {"contains":"原料罐"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd-edit-20261123.dxf --cmd 'texts {"contains":"审核版"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd-edit-20261123.dxf --cmd 'drawing.inspect {"entities":true,"limit":80}'
~/CAD-Work/tools/cad convert ~/CAD-Work/work/sample-pfd-edit-20261123.dxf ~/CAD-Work/preview/sample-pfd-edit.png
shasum -a 256 ~/CAD-Work/originals/sample-pfd.dxf
```

### 5. 失败时怎么退

| 现象 | 处理 |
|---|---|
| Harness 直接改图 | 说「停，先只给计划」；让它恢复/重来，只改副本 |
| `attedit` 报 unknown tag | 让它用 `texts` 核对属性标签拼写，不要猜 |
| `properties.set` 输出 changed 但文字没变 | 很可能改的是块参照而不是属性；让它改用 `attedit` |
| 实体数不对 | 可能重复执行了命令；从修改前的副本重来 |
| 保真门槛报 geometry/objects 丢失 | 这张图只读分析，不交付修改 |
| 预览里中文缺字 | 放大确认；必要时设置 `CADCRAFT_FONTALT`/`CADCRAFT_FONTFALLBACK` |
| 原件哈希变了 | 立即停止，检查是否写到了 `originals/`；用备份恢复 |

### 检查清单

- [ ] 我先要了计划，没有让它直接改。
- [ ] 计划里每条都有 handle、当前值、目标值。
- [ ] 保真门槛已做并记录结论。
- [ ] 我只在 `work/` 副本上修改。
- [ ] 修改用 `attedit`/`properties.set`/`move`/`erase`，另存 2018。
- [ ] 重读确认实体数、新值、图层和位置。
- [ ] 原件 sha256 未变。
- [ ] 修改前后各有一张预览。

上一讲：[让 Harness 读懂图层、块和文字](02-read-a-drawing.md) · 下一讲：[批量梳理、跨图核对与交付](04-batch-and-deliver.md)。

备查：[CLI 文档](https://github.com/storytold/cadcraft/blob/main/docs/cli.md)
