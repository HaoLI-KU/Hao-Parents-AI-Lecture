---
title: 批量梳理、跨图核对与交付
audience: dad
status: active
summary: 用自然语言让 Harness 对一批图纸做只读台账和跨图疑点，再选一张低风险图按「计划—执行—核对」修改并交付。
---
单张图读准、改准之后，真正花时间的是「一批图放在一起看」。这一讲你仍然只说任务：Harness 负责跑批量和整理台账，你负责判定疑点、选图和最终核对。

### 1. 把这一批图放进工作区

把 3–5 张关联图纸的副本放进 `~/CAD-Work/originals/`，文件名用图号。也可以让 Harness 复制并列出它看到的文件。

只读分析，不要在这一步改图。

### 2. 一句话生成只读台账

```text
工作区是 ~/CAD-Work/。请只读 originals/ 里的全部 DWG/DXF，不要修改任何文件。
对每张图运行 info 和 texts（limit 500），把原始结果放进 notes/<图号>-info.json 和 <图号>-texts.jsonl。
然后生成 notes/ledger.md，每张图一行：文件、实体数、图层数、设备位号、仪表位号、readNotes/skipped、备注。
先报告你实际运行了哪些命令，再给台账。读不全的写清楚，不要跳过。
```

它跑的命令（备查）：

```sh
cd ~/CAD-Work
for f in originals/*.dwg; do
  name=$(basename "$f" .dwg)
  tools/cad info "$f" > "notes/$name-info.json"
  tools/cad run "$f" --cmd 'texts {"limit":500}' > "notes/$name-texts.jsonl"
done
```

如果图纸是 DXF，把 `*.dwg` 换成 `*.dxf`。先看每张图的：

- `entityCount` 和 `counts`：实体数、类型分布；
- `layers`：图层清单和每层实体；
- `readNotes` / `skipped`：有没有读不全的内容；
- `texts`：图名、图号、设备/仪表位号、说明文字。

### 3. 让它只列疑点

```text
只读 notes/ledger.md、notes/*-info.json 和 notes/*-texts.jsonl，不要修改任何图纸。
请做跨图核对，但不要下结论。只列需要我人工确认的项目：
1. 同一位号在不同图纸里名称或参数不一致；
2. 设备或仪表位号重复、跳号，或只出现在一张图里；
3. 图层命名、图框版本、图号格式不一致；
4. readNotes/skipped 里读不全、可能缺内容的地方。
每条写清：疑点、证据（文件 + handle + 原文）、为什么值得核对、建议我在原图里看哪里。
没有把握的写「待确认」，不要编造位号，也不要替我判断工艺是否合理。
```

逐条在 `notes/cross-check-<日期>.md` 里判定「成立 / 不成立 / 需原件确认」。没核对到的写「待核对」，不要填「通过」。

### 4. 选一张低风险图修改

从台账里挑一张：结构简单、你熟悉、改动明确（例如一个位号名称或一处文字）。

然后沿用上一讲的**三段式自然语言**：

1. 先让它只给计划（handle、当前值、目标值、保真门槛），不执行；
2. 你说「按计划执行」，只改 `work/` 副本，先过 roundtrip 门槛，再 `saveas` 2018；
3. 让它重读输出、核对实体数/新值/未涉及实体/原件哈希，并导出前后 PNG。

### 5. 让它整理交付目录

```text
请把这次修改整理到 work/<图号>-<日期>/：
- 修改后的 DXF；
- 需要时用 saveas 生成 DWG；
- before.png 和 after.png；
- roundtrip 报告；
- plan-notes.md，写输入文件与 sha256、保真门槛结论、每条修改的 handle/旧值/新值、重读核对结果、未处理项。
只整理，不要改 originals/。
```

`plan-notes.md` 由 Harness 起草，你逐条对照 App 和报告确认；不要把 AI 的结论直接当成已核对。

### 6. 最后一眼

- 在 CADCraft App 里打开修改后的 DXF，对照 `before.png`/`after.png` 看图层、位号、文字和位置；
- 需要时用 AutoCAD 再打开一次（CADCraft 写的是标准 DWG/DXF）；
- 真实图纸、修改记录和预览只留在本机 `~/CAD-Work/`，不要提交到课程仓库。

### 7. 关于 MCP

CADCraft 官方也提供 MCP，可以让 Agent 直接调用工具。本课不依赖它：先把 CLI 走稳，能复现每条命令和每份报告，再考虑更自动的调用方式。官方说明见 [MCP 文档](https://github.com/storytold/cadcraft/blob/main/docs/mcp.md)。

### 检查清单

- [ ] 一批 3–5 张图的只读台账已生成。
- [ ] Harness 报告了实际运行的命令和读不全的地方。
- [ ] 跨图结果只包含「疑点 + 证据 + 建议核对位置」。
- [ ] 每条疑点都有成立/不成立/需原件确认的判定。
- [ ] 选中的图按「先计划、再执行、后核对」完成修改。
- [ ] 保真门槛通过，修改只写 `work/`，原件哈希未变。
- [ ] 交付目录含修改文件、前后预览、roundtrip 报告和 `plan-notes.md`。
- [ ] 在 CADCraft 或 AutoCAD 里目视核对过。

上一讲：[按 handle 改图并核对](03-edit-and-verify.md) · 回到专题：[和图纸对话](index.html)。

备查：[CLI 文档](https://github.com/storytold/cadcraft/blob/main/docs/cli.md) · [CADCraft 官网](https://getartcraft.com/apps/cadcraft)
