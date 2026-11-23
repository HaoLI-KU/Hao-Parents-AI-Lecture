---
title: 批量梳理、跨图核对与交付
audience: dad
status: active
summary: 对一批图纸做只读台账和跨图疑点，选一张低风险图修改并交付，保留原件、输出、预览和记录。
---
单张图读准、改准之后，真正花时间的是「一批图放在一起看」。这一讲只做两件事：批量**只读**梳理，和从里面挑一张做**可回退的修改**。

### 1. 批量生成只读台账

把 3–5 张关联图纸的副本放进 `originals/`，文件名用图号。然后：

```sh
cd ~/CAD-Work
for f in originals/*.dwg; do
  name=$(basename "$f" .dwg)
  tools/cad info "$f" > "notes/$name-info.json"
  tools/cad run "$f" --cmd 'texts {"limit":500}' > "notes/$name-texts.jsonl"
done
```

如果图纸是 DXF，把 `*.dwg` 换成 `*.dxf`。先看 `notes/` 里每张图的：

- `entityCount` 和 `counts`：实体数、类型分布；
- `layers`：图层清单和每层实体；
- `readNotes` / `skipped`：有没有读不全的内容；
- `texts`：图名、图号、设备/仪表位号、说明文字。

用这些字段拼一张 `notes/ledger.md` 台账：

| 图号 | 实体数 | 图层数 | 设备位号 | 仪表位号 | readNotes/skipped | 备注 |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

不要在这一步改任何图纸。

### 2. 让 Harness 只列疑点

```text
当前工作区是 ~/CAD-Work/。请只读 originals/ 和 notes/ 里的台账、info.json 与 texts.jsonl，不要修改任何图纸。
请做跨图核对，但不要下结论。只列需要我人工确认的项目：
1. 同一位号在不同图纸里名称或参数不一致；
2. 设备或仪表位号重复、跳号，或只出现在一张图里；
3. 图层命名、图框版本、图号格式不一致；
4. readNotes/skipped 里读不全、可能缺内容的地方。
每条写清：疑点、证据（文件 + handle + 原文）、为什么值得核对、建议我在原图里看哪里。
没有把握的写「待确认」，不要编造位号，也不要替我判断工艺是否合理。
```

逐条在 `notes/cross-check-<日期>.md` 里判定「成立 / 不成立 / 需原件确认」。没核对到的写「待核对」，不要填「通过」。

### 3. 选一张低风险图修改

从台账里挑一张：结构简单、你熟悉、改动明确（例如一个位号名称或一处文字）。流程与上一讲相同：

1. 复制到 `work/`，原件不动；
2. `roundtrip --same-format` 做保真门槛，geometry/objects/table records/layouts 有丢失就换一张或只读；
3. 找 handle，修改，`saveas` 到 `work/<图号>-edit-<日期>.dxf`；
4. 重读 `info`/`texts`/`drawing.inspect`，出前后 PNG；
5. 核对原件 sha256 未变。

### 4. 交付目录

建议一次交付一个文件夹：

```text
work/<图号>-<日期>/
  <图号>-edit.dxf        修改后的 DXF
  <图号>-edit.dwg        需要时由 CADCraft 另存或 saveas 生成
  before.png             修改前预览
  after.png              修改后预览
  plan-notes.md          改了什么、为什么、哪些没改
  roundtrip/report.md    保真门槛结果
```

`plan-notes.md` 只写事实：

```markdown
# <图号> 修改记录
- 输入文件与 sha256：
- 保真门槛结论：
- 修改项（handle、旧值、新值）：
- 重读核对结果：
- 未处理/待确认项：
```

### 5. 最后一眼

- 在 CADCraft App 里打开修改后的 DXF，对照 `before.png`/`after.png` 看图层、位号、文字和位置；
- 需要时用 AutoCAD 再打开一次（CADCraft 写的是标准 DWG/DXF，AutoCAD 可以读）；
- 真实图纸、修改记录和预览只留在本机 `~/CAD-Work/`，不要提交到课程仓库。

### 6. 关于 MCP

CADCraft 官方也提供 MCP 服务，可以让 Agent 直接调用工具。本课不依赖它：先把 CLI 走稳，能复现每条命令和每份报告，再考虑更自动的调用方式。官方说明见 [MCP 文档](https://github.com/storytold/cadcraft/blob/main/docs/mcp.md)。

### 检查清单

- [ ] 一批 3–5 张图的只读台账已生成。
- [ ] 跨图结果只包含「疑点 + 证据 + 建议核对位置」。
- [ ] 每条疑点都有成立/不成立/需原件确认的判定。
- [ ] 选中的图已过保真门槛。
- [ ] 修改只写 `work/`，原件哈希未变。
- [ ] 交付目录含修改文件、前后预览、修改记录和 roundtrip 报告。
- [ ] 在 CADCraft 或 AutoCAD 里目视核对过。

上一讲：[按 handle 改图并核对](03-edit-and-verify.md) · 回到专题：[和图纸对话](index.html)。

备查：[CLI 文档](https://github.com/storytold/cadcraft/blob/main/docs/cli.md) · [CADCraft 官网](https://getartcraft.com/apps/cadcraft)
