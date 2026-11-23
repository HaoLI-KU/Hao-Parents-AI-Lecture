# 爸妈的 Mac 与 AI 课

**[打开公开课程网站](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/)** · [专题总览](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/topics/) · [爸爸的学习路径](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/dad/) · [妈妈的学习路径](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/mom/)

**7 个专题 / 25 讲** · Python + Markdown 静态站点 · 代码 MIT / 内容 CC BY 4.0

> A public family course on macOS, AI tools, LaTeX, CAD drawing review and trip planning — a static site generated from Markdown.

## 这是什么

这是给爸爸妈妈做的家庭 AI 课，也是一份公开的课程网站。课程正文按**专题**维护在 `course/topics/<英文slug>/`，每讲是一份 Markdown；`site/build.py` 把它们生成静态页面，发布在 GitHub Pages。内容覆盖 Mac 基础、AI 工具与 DeepSeek Harness、中文 LaTeX、CAD 图纸（CADCraft）、图片生成、版本管理和行程规划。

## 怎么学

- 按专题和进度走；两条路径不必同步，共用的讲次只有一份内容。
- 在自己的电脑上动手；需要提示词时，照课页里的提示词块发给 AI。
- 做完亲手核对；卡住就描述眼前画面，让 AI 给一步。

详细做法见[怎么学：家庭训练模式](guidelines/teaching.md)。

## 课程一览

| 专题 | 讲什么 | 讲数 | 谁 |
|---|---|---|---|
| [把 Mac 用顺](course/topics/mac/topic.md) | Mac 基础与家庭协作 | 4 | 妈妈 |
| [AI 入门与基础](course/topics/ai/topic.md) | 从提问到 DeepSeek Harness | 3 | 共同 |
| [把技术文档做成书](course/topics/word-to-latex/topic.md) | 从 Word 到可维护的中文 LaTeX（用 AI） | 6 | 爸爸 |
| [和图纸对话](course/topics/cad/topic.md) | 用 CADCraft 读懂、修改和核对工艺流程图（用 AI） | 4 | 爸爸 |
| [把想法画出来](course/topics/image-generation/topic.md) | 图片生成与改图（用 AI，按需） | 2 | 共同 |
| [版本管理与协作](course/topics/version-control/topic.md) | 用 GitHub 管好文件和改动（按需） | 1 | 共同 |
| [把一次出门安排明白](course/topics/trip-planning/topic.md) | 用行程规划插件做一日行程（用 AI，按需） | 3 | 共同 |

学习路径：爸爸主路径 13 讲（AI 3 + LaTeX 6 + 图纸 4），妈妈主路径 7 讲（Mac 4 + AI 3）；算上生图 2 讲、版本管理 1 讲和行程规划 3 讲三个按需专题，两条路径分别显示 19 讲和 13 讲，按需专题两边都可以随时插入。

逐讲的顺序、前置、学完能做到、产出验收和覆盖点见[课程地图](course/curriculum.md)。可以从[第一个专题](course/topics/mac/topic.md)或[专题总览](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/topics/)开始。

## 仓库结构

```text
.
├── README.md
├── AGENTS.md / CLAUDE.md      # 协作工具读的仓库规则
├── guidelines/                # 维护手册，不发布
│   ├── README.md              # 手册索引
│   ├── workflow.md            # 新增/修改课稿、素材、发布
│   ├── website.md             # 站点结构、页面、搜索
│   ├── website-style.md       # 语言、颜色、字体、图片、打印
│   ├── teaching.md            # 怎么学：家庭训练模式
│   └── skills.md              # 长期技能地图
├── course/
│   ├── topics/<slug>/         # 专题：topic.md + NN-slug.md
│   ├── gallery/               # 拾趣
│   ├── curriculum.md          # 课程地图
│   └── archive/               # 历史核查记录
├── assets/
│   ├── topics/<slug>/         # 课稿图片、示例、工具箱
│   ├── gallery/               # 拾趣图片
│   └── site/                  # 全站插画和图标
├── site/                      # 构建器与样式
│   ├── build.py               # Markdown → HTML
│   ├── check_site.py          # 链接、锚点、搜索、残留检查
│   └── ...
├── docs/                      # 生成的站点，GitHub Pages 从这里发布
├── LICENSE
├── LICENSE-CONTENT.md
├── THIRD-PARTY.md
├── CITATION.cff
└── Makefile
```

`docs/` 是生成物，不要手改；`guidelines/` 是维护文档，不发布到课程网站。

## 快速开始

首次使用时安装依赖：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r site/requirements.txt
```

日常改完课稿或样式后，在仓库根目录运行：

```sh
make all                        # 重建并检查链接、锚点、搜索覆盖
make serve                      # 打开 http://localhost:8000 预览
make PYTHON=.venv/bin/python all  # 使用虚拟环境
make build                      # 只重建
make check                      # 只检查
make clean                      # 清理 .DS_Store 和 __pycache__
```

技术栈：Python 3 + `Markdown==3.9`，无前端框架；生成的页面在 `docs/`，GitHub Pages 从 `main` 分支的 `/docs` 发布。修改网站后，提交课稿、专题文件和重建后的网页，再推送到 `main`。

CAD 图纸专题使用外部 CADCraft App 和 CLI；课程默认由父亲用自然语言交代任务、Harness 执行命令，父亲负责核对。课程不把二进制放进仓库，安装步骤见课稿第 1 讲。

做网页批注时，从右侧 Files 面板直接打开对应的课页文件（例如 `docs/topics/mac/01-new-mac.html`）；批注按文件保存，改完发送给 Agent 即可。

## 内容模型

- **专题**：`course/topics/<slug>/topic.md` 定义标题、副标题、摘要、顺序，可选「按需」和「用 AI」。
- **讲次**：同一目录下的 `NN-slug.md`，编号只决定顺序。frontmatter 必填 `title`、`audience`（`dad|mom|both`）、`status`（`active|followup|draft`）、`summary`。
- **课程地图**：`course/curriculum.md` 只做计划索引，不复制正文；改讲次时同步地图和 frontmatter。
- **新增或修改一讲**的完整步骤见[工作流程](guidelines/workflow.md)。

## 拾趣

课程之外的小作品、画和家里好玩的东西。第一件是[办公室白板上的画](course/gallery/whiteboard.md)：原画由**我的妻子赵诗雅博士**手绘，整理版线稿由 **ChatGPT** 生成；页面可以点击切换原图和线稿。

## 维护文档

- [维护指南](guidelines/README.md)：五份手册的索引。
- [工作流程](guidelines/workflow.md)、[网站设计](guidelines/website.md)、[网站语言与视觉规范](guidelines/website-style.md)。
- [怎么学](guidelines/teaching.md)、[长期技能地图](guidelines/skills.md)。
- [AGENTS.md](AGENTS.md) 与 [CLAUDE.md](CLAUDE.md)：协作工具的仓库规则。
- [首版课稿核查记录（历史）](course/archive/audit-01-07.md)。

## 许可与引用

- **代码**（`site/` 等）：[MIT](LICENSE)。
- **课程文字、原创插图和站点文案**：[CC BY 4.0](LICENSE-CONTENT.md)。转载或改编请署名并链接回本仓库。
- **第三方素材**（字体、行程插件示例、白板原图和 AI 生成图）：按各自条款，见 [THIRD-PARTY.md](THIRD-PARTY.md)。
- **引用格式**：[CITATION.cff](CITATION.cff)；GitHub 仓库页的 "Cite this repository" 会读取它。

建议署名：Hao Li，《爸妈的 Mac 与 AI 课》，<https://github.com/HaoLI-KU/Hao-Parents-AI-Lecture>，CC BY 4.0。
