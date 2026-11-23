# 课程仓库协作说明

本仓库直接承载爸爸妈妈的公开 HTML 教程网站。根据两人的实际进度维护各自的学习路径。学员页以 `course/topics/` 的 Markdown 为内容源，`docs/` 由构建器生成，发布内容使用可公开的素材和占位信息。维护文档在 `guidelines/`，协作工具从根目录的 `AGENTS.md` 和 `CLAUDE.md` 进入。网页反馈涉及内容时回写 Markdown。

## 仓库地图

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
├── docs/                      # 生成物，GitHub Pages 从这里发布
├── LICENSE / LICENSE-CONTENT.md / THIRD-PARTY.md
├── CITATION.cff
└── Makefile
```

`docs/` 是生成物，不要手改；`guidelines/` 不发布到课程网站。

## 开始前

1. 先读 `README.md` 和 `guidelines/teaching.md`，理解课程受众、节奏和机器起点。编辑前读 `guidelines/workflow.md`；涉及站点结构或语言视觉时，读 `guidelines/website.md` 和 `guidelines/website-style.md`。
2. 新增或修改内容、制作或更新网页前，读 `guidelines/website.md` 和 `guidelines/website-style.md`。按具体教学需要决定是否配图；未制作的图片构想不要写进学员课稿。需要指认界面操作时优先考虑可公开、已遮去个人信息的真实截图。操作步骤需要外部入口时，加入并验证官方直达链接。

## 内容组织

3. 内容只按专题组织：`course/topics/<英文slug>/topic.md` 定义专题，`NN-slug.md` 定义讲次。新增专题建新文件夹和 `topic.md`；给已有专题加内容就继续加 `NN-slug.md`。不要重建 `course/lessons/`、`course/practices/` 或其它与 topics 平级的课程目录。
4. 每讲 frontmatter 必填 `title`、`audience`（`dad|mom|both`）、`status`（`active|followup|draft`）、`summary`；`topic.md` 必填 `title`、`subtitle`、`summary`、`order`，可选 `optional` 和 `ai: practice`（专题卡显示「用 AI」）。讲次编号在同一专题内唯一，顺序按文件名前缀。
5. 课程地图是 `course/curriculum.md`，只做计划索引，不复制正文；新增/修改/删除讲次时同步地图和课稿 frontmatter，`make check` 校验；重复覆盖点、相似标题/摘要和重复步骤标题以提醒方式给出，由人判断是否合并。

## 写作、素材与隐私

6. 示例用虚构或明确可分享的素材。仓库只放教学资料，真实家庭媒体、技术档案、密钥和账号资料留在本地私有目录。
7. 工具或版本尚未确认时写明现场验证条件，保留低门槛替代流程。修订后检查相对链接和每条路线的任务是否明确。
8. 需要学员让 AI 完成具体任务时，给出可直接使用的提示词示例，写清任务、可用材料或工具、操作范围、预期结果和亲手核对的方法。使用虚构或测试素材，按实际课堂条件替换占位内容。简单的手动操作保持短步骤。
9. 教学图片按 `guidelines/website-style.md` 的四类图片和数量规则执行；真实截图、结果图、概念图和 AI 生成图必须明确区分，AI 图不得冒充真实界面或结果；素材路径和命名见 `assets/README.md`，不新增 `images/` 目录。
10. 拾趣是独立栏目，不占专题，内容在 `course/gallery/*.md`，图片放 `assets/gallery/`；页面文案用「拾趣」，技术路径保留 `/gallery/`。公开真人姓名、单位、邮箱或原图前必须获得本人确认；`whiteboard-original.jpeg` 和赵诗雅博士的联系方式已确认公开，是明确例外。

## 网站、构建与发布

11. 网站由 `site/build.py` 从 `course/topics/` 和 `course/gallery/` 生成；README 只维护专题总览，`docs/` 是生成物。修改课稿、专题或样式后运行 `make build && make check`；不要手改 `docs/`。保留课稿里的快捷键写法（如 `⌘C`）和课页的本节步骤、上一讲/下一讲导航；新增讲必须同时更新 README 专题总览、`guidelines/skills.md` 和搜索覆盖。
12. URL 变更直接生效；仓库和 `docs/` 都不保留旧课稿、旧目录、别名文件、重定向页或指向旧路径的过渡结构。

## CAD 工作流

13. 爸爸的 CAD 工作流使用外部 CADCraft App + cadcraft-cli，在文件层读取、修改和校验 DWG/DXF；**禁止 GUI 自动化，包括向 AutoCAD 键入命令**。真实图纸、图号、位号、修改记录和预览留在本机 `~/CAD-Work/`，不进入仓库、截图或公开网页。课程第 1 讲负责从零安装 App 和 CLI；日常默认由父亲用自然语言交代任务、Harness 执行 CLI，工作区规则放在 `~/CAD-Work/AGENTS.md`（课程模板 `assets/topics/cad/examples/CAD-Work-AGENTS.md`）。仓库不提交二进制。

## 常用命令

| 命令 | 用途 |
|---|---|
| `make all` | 重建并检查 |
| `make build` | 只重建 |
| `make check` | 只检查 |
| `make serve` | 本地预览 `http://localhost:8000` |
| `make clean` | 清理 `.DS_Store` 和 `__pycache__` |
| `cd assets/topics/cad && ls examples` | 查看虚构 CAD 示例 |

## 维护入口

- [维护指南](guidelines/README.md)：五份手册的索引。
- [工作流程](guidelines/workflow.md) · [网站设计](guidelines/website.md) · [网站语言与视觉规范](guidelines/website-style.md) · [怎么学](guidelines/teaching.md) · [长期技能地图](guidelines/skills.md)。
