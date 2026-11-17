---
title: 修改计划与 dry-run
audience: dad
status: active
summary: 把「想改什么」写成带 handle 和修改前状态的 JSON 计划，先检查、再 dry-run 看差异，确认后才允许执行。
---
从这一讲开始动图。原则是：**先把改动写成计划，看清差异，再执行**；执行只写新文件，原图和 DXF 工作副本都不覆盖。

### 1. 修改计划长什么样

计划是一个 JSON 文件，`operations` 里每条写清操作、目标 handle、修改前状态（`expect`）和修改后的值。示例见 [sample-plan.json](../../../assets/topics/cad/examples/sample-plan.json)：

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

支持的操作：

| op | 作用 | 必填 |
|---|---|---|
| `set_layer` | 改实体图层 | `handle`、`expect`、`to` |
| `move` | 平移 | `handle`、`expect`、`delta: [dx, dy]` |
| `delete` | 删除 | `handle`、`expect` |
| `set_attribute` | 改块属性 | `handle`、`expect`、`tag`、`to` |
| `replace_text` | 改 TEXT/MTEXT 文字 | `handle`、`expect`、`to` |
| `set_color` | 改 ACI 颜色 | `handle`、`expect`、`to` |
| `rename_layer` | 图层改名 | `expect`、`from`、`to` |
| `add_line` / `add_polyline` / `add_circle` / `add_text` | 新增图元 | `layer` 与几何参数 |

`expect` 是守卫：执行前逐条核对当前值；只要有一条与图纸不符，整套计划中止，不写任何文件。

### 2. 先检查计划

```sh
.venv-cad/bin/python toolkit/cad.py check-plan plan.json --drawing dxf/<图号>.dxf
```

输出应列出每条操作的 id 和 handle。任何一条报「找不到 handle」或「守卫不符」，说明清单或图纸已经变了，回到第一讲重新生成清单，不要绕过守卫。

### 3. dry-run：只看差异

```sh
.venv-cad/bin/python toolkit/cad.py apply plan.json --drawing dxf/<图号>.dxf --dry-run
```

dry-run 不写文件，只确认计划能通过守卫。把操作逐条对照成自然语言，例如：

| id | 操作 | 现在的样子 | 修改后 |
|---|---|---|---|
| layer-v101 | set_layer | E4 / EQUIPMENT / V-101 | 图层改为 EQ-REVIEW |
| name-v101 | set_attribute | NAME = 原料储罐 | NAME = 原料罐 |
| new-line | add_polyline | 无 | REVIEW 图层新增一段折线 |

确认三件事：改的对象对不对、改的值对不对、有没有漏掉要改的东西。

### 4. 让 Harness 起草计划，但不要执行

```text
当前工作区是 CAD-Review/。请只读 inventory/<图号>.json 和 dxf/<图号>.dxf 的清单，不要修改任何文件。
我要做的修改是：<用一句话说清，例如「把 V-101 的 NAME 改成原料罐，并把这台设备移到 EQ-REVIEW 图层」>。
请先列出你准备改的实体的 handle、当前值、修改后的值，以及你依据的清单字段。
然后按工具箱 README 的 schema 起草 plan.json，只在会话里展示，不要写入文件，也不要执行 apply。
如果你无法从清单确认某个 handle，写「待确认」，不要猜。
```

你逐条核对 handle 和当前值，确认后让 Harness 写入 `plan.json`；也可以自己改示例文件。

### 5. 什么情况下不允许执行

- 计划里有你没确认过的 handle；
- 某条操作会删除实体，但你还没在 AutoCAD 里确认它能删；
- 计划扩大了范围（比如本来只改一个位号，却顺带改了文字或图层）；
- 图纸在 AutoCAD 里被另存或改过，清单已经过期。

遇到这些情况，先改计划，不要先执行再回滚。

### 检查清单

- [ ] 每条操作都有 `handle` 和 `expect`，没有空守卫。
- [ ] `check-plan` 全部通过。
- [ ] dry-run 的对照表逐条看过。
- [ ] 删除类操作已在 AutoCAD 里确认。
- [ ] 计划范围与口头需求一致，没有顺带改动。
- [ ] 还没有写任何文件。

上一讲：[审图页与批注](04-review-and-annotate.md) · 下一讲：[应用、验证与交付](06-apply-and-verify.md)。

备查：[sample-plan.json](../../../assets/topics/cad/examples/sample-plan.json) · [sample-edit-report.md](../../../assets/topics/cad/examples/sample-edit-report.md) · [工具箱说明](../../../assets/topics/cad/toolkit/README.md)
