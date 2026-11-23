---
title: 按 handle 改图，写副本并核对
audience: dad
status: active
summary: 先做保真门槛，再用 attedit、properties.set、move、erase 修改副本，另存为新文件并重读验证。
---
这一讲开始动图。顺序固定：**先检查保真，再改副本，最后重读验证**。原件和 `originals/` 里的文件永远不覆盖。

### 1. 复制一份工作副本

```sh
cp ~/CAD-Work/originals/sample-pfd.dxf ~/CAD-Work/work/sample-pfd.dxf
```

后面所有修改都只对 `work/sample-pfd.dxf` 做。

### 2. 先做保真门槛

CADCraft 保存时会重写文件；它没有建模的对象可能不会被保留。改图前先让它原样往返一次：

```sh
~/CAD-Work/tools/cad roundtrip ~/CAD-Work/work/sample-pfd.dxf \
  --same-format --out ~/CAD-Work/work/roundtrip-sample
```

打开 `~/CAD-Work/work/roundtrip-sample/report.md`，看 `Lost` 列和分类：

- **geometry、objects、table records、layouts 有 Lost**：这张图不要改，只做只读分析；
- 只有 `header` 变量丢失：记下来，可以继续；
- 完全没丢：可以进入下一步。

示例图是虚构的简单 PFD，预计只在 header 上有差异；看到 geometry 丢失就停下。

把结论写进 `notes/`：这次门禁通过/不通过、丢失了哪一类。

### 3. 找 handle

先用 `texts` 找要改的文字或块属性：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf --cmd 'texts {"contains":"糖浆"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf --cmd 'texts {"contains":"V-101"}'
```

用 `drawing.inspect` 核对图层和位置：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf --cmd 'drawing.inspect {"entities":true,"limit":80}'
```

示例里可用：

| 要改什么 | handle | 依据 |
|---|---|---|
| 设备 NAME | `E4`（TAG = V-101） | `texts` 的 Attribute 行 |
| 图名文字 | `D5` | `texts` 的 Text 行 |
| 仪表 TI-101 | `114` | `drawing.inspect` 的 Block Reference |
| 仪表 TI-102 | `123` | 只用来演示删除，示例可删 |

### 4. 修改副本

**改块属性**用 `attedit`，不要用 `properties.set` 改 `text`：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'attedit {"handle":"E4","values":{"NAME":"原料罐"}}'
```

**改文字**：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'properties.set {"handles":["D5"],"text":"糖浆配制流程（审核版）"}'
```

**改图层**：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'properties.set {"handles":["E4"],"layer":"EQ-REVIEW"}'
```

**移动**：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'move {"handles":["114"],"delta":[0,-10]}'
```

**删除**（先确认 handle 和对象，示例里 TI-102 是 `123`）：

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'erase {"handles":["123"]}'
```

每一步都会打印 JSON 结果，例如 `{"changed":1}`、`{"moved":1}`、`{"erased":1}`。看到 `error` 就停下，不要继续叠加修改。

### 5. 另存为新文件

```sh
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd.dxf \
  --cmd 'saveas {"path":"/Users/你的用户名/CAD-Work/work/sample-pfd-edit-20261123.dxf","version":2018}'
```

把路径换成自己的 `$HOME` 路径；不要用 `--in-place`，不要写到 `originals/`。

命令会打印 `nonPortableFonts` 警告，列出这台 Mac 有、Windows AutoCAD 未必有的字体。这是提示，不是保存失败；只要 `path` 和 `version` 正确就可以继续。

### 6. 重读验证

```sh
~/CAD-Work/tools/cad info ~/CAD-Work/work/sample-pfd-edit-20261123.dxf
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd-edit-20261123.dxf \
  --cmd 'texts {"contains":"原料罐"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd-edit-20261123.dxf \
  --cmd 'texts {"contains":"审核版"}'
~/CAD-Work/tools/cad run ~/CAD-Work/work/sample-pfd-edit-20261123.dxf \
  --cmd 'drawing.inspect {"entities":true,"limit":80}'
```

逐项确认：

| 检查 | 预期 |
|---|---|
| 实体数 | 删除 1 个后应是 61（示例 62 起） |
| 属性 NAME | 新值「原料罐」 |
| 图名文字 | 新值「糖浆配制流程（审核版）」 |
| E4 图层 | `EQ-REVIEW` |
| 114 位置 | y 从 440 到 430 |
| 123 | 已不存在 |

再导一张修改后的预览：

```sh
~/CAD-Work/tools/cad convert ~/CAD-Work/work/sample-pfd-edit-20261123.dxf \
  ~/CAD-Work/preview/sample-pfd-edit.png
```

最后确认原件没变：

```sh
shasum -a 256 ~/CAD-Work/originals/sample-pfd.dxf
```

哈希应与第一讲记录的一致。

### 7. 失败时怎么退

| 现象 | 处理 |
|---|---|
| `attedit` 报 unknown tag | 用 `texts` 确认属性标签拼写；标签大小写可能不敏感，但值要看清 |
| `properties.set` 输出 changed 但文字没变 | 很可能改的是块参照而不是属性；改用 `attedit` |
| 实体数不对 | 可能重复执行了同一命令；回到修改前的副本重来 |
| 保真门槛报 geometry/objects 丢失 | 这张图只读分析，不要交付修改 |
| 预览里中文缺字 | 放大确认；必要时设置 `CADCRAFT_FONTALT`/`CADCRAFT_FONTFALLBACK` |

### 检查清单

- [ ] 只在 `work/` 的副本上修改。
- [ ] roundtrip 门槛已做并记录结论。
- [ ] 每个 handle 都先核对过对象。
- [ ] 块属性用 `attedit`，文字用 `properties.set`。
- [ ] `saveas` 指定了 `version:2018` 和新文件名。
- [ ] 重读确认实体数、新值、图层和位置。
- [ ] 原件 sha256 未变。
- [ ] 修改前后各有一张预览。

上一讲：[让 Harness 读懂图层、块和文字](02-read-a-drawing.md) · 下一讲：[批量梳理、跨图核对与交付](04-batch-and-deliver.md)。

备查：[CLI 文档](https://github.com/storytold/cadcraft/blob/main/docs/cli.md)
