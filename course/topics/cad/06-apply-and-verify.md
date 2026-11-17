---
title: 应用、验证与交付
audience: dad
status: active
summary: 执行修改计划，自动重读校验，按报告逐项确认未涉及实体没有变化，再在 AutoCAD 里核对并交付。
---
最后一讲把修改落到新文件，并且用程序自己验证一遍。目标是：你能拿着报告和 AutoCAD 里的结果，说清「改了什么、没改什么、原件在哪」。

### 1. 执行到新文件

```sh
.venv-cad/bin/python toolkit/cad.py apply plan.json \
  --drawing dxf/<图号>.dxf \
  --out work/<图号>-edit-<日期>.dxf
```

工具会：

1. 再核对一遍每条 `expect`；
2. 在内存里执行操作；
3. 另存为新文件（绝不覆盖 `dxf/` 或 `original/`）；
4. 重新打开新文件，逐项校验；
5. 在输出文件旁写一份 `<输出>.report.md`。

### 2. 看懂报告

报告里有三段：

| 段落 | 看什么 |
|---|---|
| 输入/输出 sha256 | 证明改的是副本；输入哈希与原件对应 |
| 操作表 | 每条操作的结果是不是 done |
| 校验表 | 每条操作是否达成、实体数、未涉及实体是否原样 |

重点看两条：

- **实体数**：修改前 + 新增 − 删除 = 修改后；
- **未涉及实体保持原样**：如果列出变化的 handle，说明有预期之外的改动，必须停下来查。

示例报告：[sample-edit-report.md](../../../assets/topics/cad/examples/sample-edit-report.md)。

### 3. 在 AutoCAD 里核对

1. 打开输出 DXF，先看图层管理器：新图层在不在，改名的图层对不对。
2. 对照报告里的操作表，逐个找到实体：位号、属性、文字、位置。
3. 用审图页复核一次：

```sh
.venv-cad/bin/python toolkit/cad.py review work/<图号>-edit-<日期>.dxf -o review/<图号>-edit.html
```

4. 原件和 `dxf/` 工作副本的时间和哈希不变。

### 4. 交付与版本命名

- 输出统一放 `work/`，文件名带日期；不要用「最终版」「最新版」这类名字。
- 需要 DWG 时，在 AutoCAD 里打开输出 DXF，另存为 DWG；装了 ODA 也可以用 `cad.py convert work/xxx.dxf --to dwg`。
- 交付前把 `plan.json`、报告、输出 DXF 和讨论记录放在同一个目录，方便以后追溯。

### 5. 失败与回退

| 现象 | 先做什么 |
|---|---|
| 「守卫不符」 | 图纸或清单过期；重新生成 inventory，确认后再生成计划 |
| 「找不到 handle」 | 实体被删或换了文件；不要猜新 handle |
| 校验表「未涉及实体变化」 | 停下来，查计划范围；可能是图层改名或块属性连带变化 |
| 实体数不符 | 检查新增/删除计数，确认没有重复执行 |
| 输出打不开 | 用原始 DXF 重跑；仍失败就保留输入、计划和报告，记进 `notes/` |

任何失败都不要回头改原件。输入 DXF、计划、报告和失败的输出都保留，下一次换新文件名重来。

### 6. 把有效做法留下来

跑通一次之后，在 `standards/cad-review.md` 里补一条可复用的规则，并在 `notes/` 记下这次用了哪个计划、哪份报告、哪些 handle。以后同类修改直接套用，不要重新发明。

### 检查清单

- [ ] 输出写在 `work/`，文件名带日期。
- [ ] 报告里的每条操作都是 done。
- [ ] 实体数、未涉及实体两项校验都通过。
- [ ] 在 AutoCAD 里看过图层、位号、属性和位置。
- [ ] 审图页复核过修改后的图。
- [ ] 原件和 `dxf/` 工作副本没有被覆盖。
- [ ] `plan.json`、报告、输出和讨论记录已归档。

上一讲：[修改计划与 dry-run](05-plan-and-dry-run.md) · 回到专题：[和图纸对话](index.html)。

备查：[工具箱说明](../../../assets/topics/cad/toolkit/README.md) · [sample-edit-report.md](../../../assets/topics/cad/examples/sample-edit-report.md)
