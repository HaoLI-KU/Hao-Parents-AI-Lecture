# 修改报告：sample-pfd.dxf

- 输入 sha256：`332608172255d661ee00106a2f67b3c166b773bbb13dbdfa366ce5317a565ffb`
- 输出文件：`work/sample-edited.dxf`
- 输出 sha256：`4240af7a063515752d1d06656f25c4fc56293474c560ec7baccb068729340584`

## 操作

| id | 操作 | handle | 结果 |
|---|---|---|---|
| layer-v101 | set_layer | E4 | done |
| name-v101 | set_attribute | E4 | done |
| title | replace_text | D5 | done |
| move-ti101 | move | 114 | done |
| new-line | add_polyline | 147 | done |

## 校验

| 检查 | 结果 | 说明 |
|---|---|---|
| layer-v101（set_layer） | 通过 | 图层 -> EQ-REVIEW |
| name-v101（set_attribute） | 通过 | 属性 NAME = 原料罐 |
| title（replace_text） | 通过 | 文字已替换 |
| move-ti101（move） | 通过 | 插入点 [330.0, 440.0] -> [330.0, 430.0] |
| new-line（add_polyline） | 通过 | 新实体 147 在图层 REVIEW |
| 实体数 | 通过 | 修改前 62，修改后 63，预期 63 |
| 未涉及实体保持原样 | 通过 | 全部一致 |

总体结果：通过

报告：work/sample-edited.report.md
