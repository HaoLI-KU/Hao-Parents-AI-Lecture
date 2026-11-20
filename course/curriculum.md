# 课程地图

这是课程的计划索引，不是第二份课稿。正文、步骤、提示词和检查清单仍然只写在
`course/topics/<slug>/NN-slug.md`。本文件只记录：讲次顺序、受众、前置、学完能做到什么、
产出/验收、覆盖点和计划中的配图类型。

## 维护顺序

新增或修改内容时按这个顺序做：

1. 先在本文加/改一行计划，或在已有行上改元数据。
2. 再改 `course/topics/<slug>/NN-slug.md` 的 frontmatter 和正文。
3. 讲数或专题数变化时，更新 `README.md` 的专题总览。
4. 运行 `make all`。
5. 处理 `make check` 的结构错误；重复提醒由人判断是否合并。
6. 提交课稿、本文、README 和生成页。

不要在本文件里复制完整步骤、提示词或长段正文。地图和课稿的标题、受众、状态必须一致，
`make check` 会校验。

## 字段

- **讲**：同一专题内的两位编号，和 `NN-slug.md` 一致。
- **文件**：相对 `course/` 的路径。
- **受众**：`爸爸`、`妈妈`、`共同`。
- **状态**：`active`、`followup`、`draft`。
- **前置**：无，或指向前面的讲次/技能。
- **学完能做到**：一句话，不复制正文。
- **产出 / 验收**：可检查的结果。
- **覆盖点**：短标签，逗号分隔；重复标签会触发提醒。标签要具体，不要用「AI」「GitHub」这类泛词。
- **视觉**：`—`、`概念图`、`截图`、`结果图`、`对照`，可带数量，例如 `结果图 ×3`、`概念图 ×2`。这是配图计划；`截图`/`结果图` 放 `assets/topics/<slug>/screenshots/`，`概念图`/`对照` 放 `assets/topics/<slug>/illustrations/`。

## 专题：mac｜把 Mac 用顺

| 讲 | 文件 | 标题 | 受众 | 状态 | 前置 | 学完能做到 | 产出 / 验收 | 覆盖点 | 视觉 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | topics/mac/01-new-mac.md | 把新 Mac 设置到能上远程课 | 妈妈 | active | 无 | 能联网、装软件、更新、登录 Apple 账户并进入一次远程会议 | 成功入会并共享屏幕；记下卡住的一步 | mac-first-run, software-install, apple-account, remote-meeting | 截图 |
| 02 | topics/mac/02-apps-and-email.md | 验收应用，配好邮箱并核对同步 | 妈妈 | active | Mac 01 | 能检查应用、添加邮箱并完成一次收发同步核对 | 收件箱和已发送各有一封测试邮件 | app-check, email-setup, mail-sync | 截图 |
| 03 | topics/mac/03-shortcuts-and-sharing.md | 练快捷键、触控板与家庭共享 | 妈妈 | active | Mac 02 | 能用复制粘贴、截图、窗口操作，并验证家庭共享 | 完成一次截图；共享日历、备忘录或相簿可见 | mac-shortcuts, trackpad, family-sharing | 截图 |
| 04 | topics/mac/04-meetings-and-mactex.md | 会议预约、语音输入与 MacTeX | 妈妈 | active | Mac 03 | 能预约会议、用语音输入，并用 TeXShop 编译中文 PDF | 日历出现会议；一条语音转文字；中文 PDF 编译成功 | meeting-scheduling, voice-input, mactex | 截图 |

## 专题：ai｜和 AI 一起做事

| 讲 | 文件 | 标题 | 受众 | 状态 | 前置 | 学完能做到 | 产出 / 验收 | 覆盖点 | 视觉 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | topics/ai/01-models-and-tools.md | 认识两层 AI，用自己的账户跑通 Codex | 共同 | active | 无 | 能分清界面与模型，用自己的账户跑通 Codex 并核对用量 | 收到测试回复；开放平台能看到这次用量 | ai-layers, deepseek-account, codex-setup, usage-check | 概念图 |
| 02 | topics/ai/02-harness-setup.md | 初始化 Harness，装输入法和六个插件 | 共同 | active | AI 01 | 能初始化 Harness，安装微信输入法和指定插件并逐项核对 | Harness 登录成功；插件开关核对表 | harness-install, wechat-ime, plugin-install | 截图 |
| 03 | topics/ai/03-effort-and-usage.md | 比较推理强度，读网页和日历 | 共同 | active | AI 02 | 能比较推理档位、核对用量，并只读网页和日历 | 两次用量记录；一次只读网页/日历操作 | effort-comparison, usage-reading, readonly-web-calendar | 截图 |

## 专题：word-to-latex｜把技术文档做成书

| 讲 | 文件 | 标题 | 受众 | 状态 | 前置 | 学完能做到 | 产出 / 验收 | 覆盖点 | 视觉 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | topics/word-to-latex/01-project-goal.md | 说清 Word 转 LaTeX 的目标 | 爸爸 | active | 无 | 能写清原件、预期产出、内容保持要求和长期目标 | 一页项目说明 | project-input, latex-goal | — |
| 02 | topics/word-to-latex/02-compile-and-annotate.md | 编译中文 LaTeX，练习 PDF 批注 | 爸爸 | active | LaTeX 01 | 能在本机编译中文 PDF，做带位置批注、改源码、重编 | 带批注 PDF；重编成功 | xelatex-compile, pdf-annotation, template-discovery | 结果图 |
| 03 | topics/word-to-latex/03-template.md | 做可编译的中文技术书模板 | 爸爸 | active | LaTeX 02 | 能做出覆盖章节、图表、公式、TikZ、代码和索引的中文模板 | 可编译模板；预览 PDF | latex-book-structure, latex-template, tikz-code-index | 结果图 |
| 04 | topics/word-to-latex/04-project-layout.md | 分开模板来源、通用模板和项目 | 爸爸 | active | LaTeX 03 | 能分开模板来源、工作副本和第一份 Word | Technical-Publishing 目录；来源记录 | publishing-layout, file-provenance | 截图 |
| 05 | topics/word-to-latex/05-project-rules.md | 写项目入口、路线和内容规则 | 爸爸 | active | LaTeX 04 | 能写 AGENTS.md、ROADMAP.md 和 standards，并验证新会话读取 | 三份规则文件；新会话核对 | agents-md, roadmap, standards, harness-verification | 结果图 |
| 06 | topics/word-to-latex/06-convert-segment.md | 转换一小段 Word 并沉淀流程 | 爸爸 | followup | LaTeX 05 | 能把一小段 Word 忠实转成 LaTeX，编译、核对并沉淀 Skill | 编译通过；逐项核对；一份 Skill | word-segment-convert, latex-verification, skill-capture | 结果图 |

## 专题：cad｜和图纸对话

| 讲 | 文件 | 标题 | 受众 | 状态 | 前置 | 学完能做到 | 产出 / 验收 | 覆盖点 | 视觉 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | topics/cad/01-convert-to-dxf.md | 把 DWG 变成可精确读取的 DXF | 爸爸 | active | 无 | 能建立私有目录，把 DWG 转 DXF 并生成清单和覆盖报告 | DXF；inventory；coverage 报告 | dwg-dxf, cad-inventory, coverage-report | 结果图 |
| 02 | topics/cad/02-read-a-drawing.md | 精确读懂一张图 | 爸爸 | active | CAD 01 | 能读懂图层、块、属性、文字和图框，并回到 AutoCAD 核对 | 一页读图记录；AutoCAD 核对 | cad-layers, blocks-attributes, title-block | 结果图 |
| 03 | topics/cad/03-batch-and-cross-check.md | 批量台账与跨图核对 | 爸爸 | active | CAD 02 | 能批量整理关联图纸，列出疑点并沉淀核对规则 | 台账；疑点清单；规则 | cad-batch, cross-drawing-check, rule-capture | 结果图 |
| 04 | topics/cad/04-review-and-annotate.md | 审图页与批注讨论 | 爸爸 | active | CAD 03 | 能生成审图页，按 handle 写批注并让 Harness 回应 | 审图页；批注记录 | review-sheet, entity-annotation, handle-evidence | 结果图 |
| 05 | topics/cad/05-plan-and-dry-run.md | 修改计划与 dry-run | 爸爸 | active | CAD 04 | 能写出带 handle 和修改前状态的计划，并先做 dry-run | JSON 计划；dry-run 差异 | change-plan, plan-validation, dry-run | 概念图 |
| 06 | topics/cad/06-apply-and-verify.md | 应用、验证与交付 | 爸爸 | active | CAD 05 | 能应用计划、重读校验、核对未涉及实体并交付 | 新 DXF；校验报告；AutoCAD 核对 | apply-plan, reread-verify, cad-delivery, rollback | 结果图 |

## 专题：image-generation｜把想法画出来

| 讲 | 文件 | 标题 | 受众 | 状态 | 前置 | 学完能做到 | 产出 / 验收 | 覆盖点 | 视觉 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | topics/image-generation/01-generate-and-edit.md | 用 Harness 生成和修改图片 | 共同 | active | AI 02 | 能配置图像服务，生成、局部改图并做软装方向对比 | 原图；改图；三套方向 | image-provider, text-to-image, image-edit, soft-furnishing | 结果图 ×3 |

## 专题：version-control｜版本管理与协作

| 讲 | 文件 | 标题 | 受众 | 状态 | 前置 | 学完能做到 | 产出 / 验收 | 覆盖点 | 视觉 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | topics/version-control/01-first-repository.md | 第一次把文件放进 GitHub 仓库 | 共同 | active | AI 02 | 能注册账号、建私有仓库，并完成 clone、commit、push | 私有仓库；提交记录；本机文件 | github-account, private-repo, clone-commit-push | 概念图 ×2 |

## 待安排

- 配图阶段：按每行 `视觉` 列逐讲补图；第一轮试点是图片生成第 1 讲（3 张效果图）和版本管理第 1 讲（2 张 Git 示意图）。
- 不把未制作的图写进学员课稿；图片构想先留在这里。
