# 爸妈的 Mac 与 AI 课

**[打开公开课程网站](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/)** · [专题总览](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/topics/) · [爸爸的学习路径](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/dad/) · [妈妈的学习路径](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/mom/)

网站通过 GitHub Pages 发布，全站可搜索课名、步骤、正文和拾趣。课程正文按**专题**维护在 `course/topics/<英文slug>/`，网页由课稿生成。结构与规则见[维护指南](guidelines/README.md)：[工作流程](guidelines/workflow.md)和[网站设计](guidelines/website.md)。

## 专题

| 专题 | 讲什么 | 讲数 | 谁 |
|---|---|---|---|
| [把 Mac 用顺](course/topics/mac/topic.md) | Mac 基础与家庭协作 | 4 | 妈妈 |
| [AI 入门与基础](course/topics/ai/topic.md) | 从提问到 DeepSeek Harness | 3 | 共同 |
| [把技术文档做成书](course/topics/word-to-latex/topic.md) | 从 Word 到可维护的中文 LaTeX（用 AI） | 6 | 爸爸 |
| [和图纸对话](course/topics/cad/topic.md) | AutoCAD 工艺流程图：精确读取与修改（用 AI） | 6 | 爸爸 |
| [把想法画出来](course/topics/image-generation/topic.md) | 图片生成与改图（用 AI，按需） | 2 | 共同 |
| [版本管理与协作](course/topics/version-control/topic.md) | 用 GitHub 管好文件和改动（按需） | 1 | 共同 |
| [把一次出门安排明白](course/topics/trip-planning/topic.md) | 用行程规划插件做一日行程（用 AI，按需） | 3 | 共同 |

学习路径：爸爸 15 讲（AI 3 + LaTeX 6 + 图纸 6），妈妈 7 讲（Mac 4 + AI 3）；另有生图 2 讲、版本管理 1 讲和行程规划 3 讲三个按需专题，两边都可以随时插入。

逐讲的顺序、前置、学完能做到、产出验收和覆盖点见[课程地图](course/curriculum.md)。

## 2026 年 12 月家庭试讲

爸爸第 1–3 讲（AI 入门）继续推进，第 6 讲 Word 小段转换作为后续课；第 4–5、7–9 讲按 LaTeX 文档路线走。妈妈第 1–4 讲按 Mac 基础练，AI 三讲和爸爸同一份内容、各用自己的账户和密钥。图纸专题六讲按「读准 → 台账 → 批注 → 计划 → 修改 → 验证」推进，工具链在虚构示例上自检通过，真实图纸由爸爸在本机核对。两条路径不要求同步。行程规划三讲按「你发 prompt → AI 做 → 你接手」推进，案例（上海一日，3 人、zine 版）已跑通。

## 拾趣

课程之外的小作品、画和家里好玩的东西。第一件是[办公室白板上的画](course/gallery/whiteboard.md)：原画由**我的妻子赵诗雅博士**手绘，整理版线稿由 **ChatGPT** 生成；页面可以点击切换原图和线稿。

备课可参照[家庭带练方式](guidelines/teaching.md)和[长期技能地图](guidelines/skills.md)；维护文档都在 [guidelines/](guidelines/README.md)。[AGENTS.md](AGENTS.md)与 [CLAUDE.md](CLAUDE.md)供后续维护使用。

从[第一个专题](course/topics/mac/topic.md)或[专题总览](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/topics/)开始。目录、素材和迭代步骤见[工作流程](guidelines/workflow.md)，简体中文、British English 和视觉规则见[网站语言与视觉规范](guidelines/website-style.md)。

[首版课稿核查记录（历史）](course/archive/audit-01-07.md)

## 许可与引用

- **代码**（`site/`、`assets/topics/cad/toolkit/` 等）：[MIT](LICENSE)。
- **课程文字、原创插图和站点文案**：[CC BY 4.0](LICENSE-CONTENT.md)。转载或改编请署名并链接回本仓库。
- **第三方素材**（字体、行程插件示例、白板原图和 AI 生成图）：按各自条款，见 [THIRD-PARTY.md](THIRD-PARTY.md)。
- **引用格式**：[CITATION.cff](CITATION.cff)；GitHub 仓库页的 "Cite this repository" 会读取它。

建议署名：Hao Li，《爸妈的 Mac 与 AI 课》，<https://github.com/HaoLI-KU/Hao-Parents-AI-Lecture>，CC BY 4.0。

## 本地预览与发布

页面由 `site/build.py` 从 `course/topics/` 和 `course/gallery/` 生成；README 只维护专题总览，`docs/` 是生成物，不要手改。首次使用时安装依赖：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r site/requirements.txt
```

日常改完课稿或样式后，在仓库根目录运行：

```sh
make all                        # 重建并检查链接、锚点、搜索覆盖
make serve                      # 打开 http://localhost:8000 预览
make PYTHON=.venv/bin/python all  # 使用虚拟环境
```

`make build` 只重建，`make check` 只检查。生成的页面在 `docs/`，GitHub Pages 从 `main` 分支的 `/docs` 发布。修改网站后，提交课稿、专题文件和重建后的网页，再推送到 `main`。

CAD 工具箱自带自检，改工具后运行：

```sh
cd assets/topics/cad/toolkit
python3 -m venv .venv-cad && .venv-cad/bin/python -m pip install -r requirements.txt
.venv-cad/bin/python cad.py selftest
```

做网页批注时，从右侧 Files 面板直接打开对应的课页文件（例如 `docs/topics/mac/01-new-mac.html`）；批注按文件保存，改完发送给 Agent 即可。

需要清理本地临时文件时，在仓库根目录运行 `make clean`。
