# 爸妈的 Mac 与 AI 课

**[打开公开课程网站](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/)** · [爸爸的课表](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/dad/) · [妈妈的课表](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/mom/)

网站通过 GitHub Pages 发布，全站可搜索课名、步骤和正文。课程正文维护在 Markdown 课稿中，网页由课稿生成。[网站设计](website.md)

## 2026 年 12 月家庭试讲

爸爸第 1–8 节继续推进，第 9 节作为后续课；制作模板的第 6 节可分多次完成。妈妈第 1–4 节按 Mac 基础练，第 5–7 节直接按爸爸第 1–3 节完成 AI 入门；后续项目待定。两条路线不要求同步。

| 课稿 | 爸爸 | 妈妈 | 状态 | 说明 |
|---|---|---|---|---|
| [第 1 节](course/lessons/01.md) | 认识模型和工具，用自己的 DeepSeek 账户跑通 Codex | 新 Mac 联网后先装豆包桌面版，试语音通话和屏幕共享，再更新和验证入会 |  | 首课 |
| [第 2 节](course/lessons/02.md) | 初始化 DeepSeek Harness，安装微信输入法与六个指定插件 | 安装应用、配邮箱并核对同步 |  |  |
| [第 3 节](course/lessons/03.md) | 在 DeepSeek Harness 比较推理强度与用量，练习读网页和日程 | 快捷键和触控板，验证共享日历、备忘录和相册 |  |  |
| [第 4 节](course/lessons/04.md) | 说清 Word 转 LaTeX 的输入、产出和长期工作流目标 | 会议预约与分享、语音输入、MacTeX 验证 |  | 妈妈用 TeXShop 验证，不需要 Harness |
| [第 5 节](course/lessons/05.md) | 编译中文 LaTeX，练习 PDF 批注并认识 Overleaf 模板库 | 按爸爸第 1 节：认识 AI 与 DeepSeek/Codex |  | 妈妈用自己的账户和密钥；Codex 安装可由家人协助 |
| [第 6 节](course/lessons/06.md) | 在 Overleaf 选模板，做可编译的完整中文技术书模板 | 按爸爸第 2 节：安装与初始化 Harness |  | 妈妈用自己的账户和密钥 |
| [第 7 节](course/lessons/07.md) | 分开放 Overleaf 模板来源、通用模板和第一份 Word，建立项目目录 | 按爸爸第 3 节：推理强度、用量与查网页/日历 |  |  |
| [第 8 节](course/lessons/08.md) | 写项目指令、阶段路线与内容保持规则，并开新会话核对 | — |  | 妈妈路线到第 7 节 |
| [第 9 节](course/lessons/09.md) | 用已验证模板转换一小段 Word，编译、核对并沉淀流程 | — | 后续课 |  |

## 共同练习

两项共用练习，不占爸爸妈妈的课号，按需要安排；网站单独列出。

- [爸妈第一次用 GitHub](course/lessons/github.md)｜备用；注册、私有仓库、克隆、提交和推送。
- [用 DeepSeek Harness 生成房间软装图](course/lessons/image-gen.md)｜建议安排；配置 Seedream/火山方舟，跑通生图、改图和软装对比。

备课可参照[家庭带练方式](teaching.md)和[长期技能地图](skills.md)。[AGENTS.md](AGENTS.md)与 [CLAUDE.md](CLAUDE.md)供后续维护使用。

从[第 1 节课稿](course/lessons/01.md)开始。目录、素材和迭代步骤见[工作流程](workflow.md)，简体中文、British English 和视觉规则见[网站语言与视觉规范](website-style.md)。

[首版课稿核查记录（课号沿用首版）](course/audit-01-07.md)

## 本地预览与发布

页面由 `site/build.py` 从 `course/lessons/` 和 `README.md` 的课表生成；`docs/` 是生成物，不要手改。首次使用时安装依赖：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r site/requirements.txt
```

日常改完课稿或样式后，在仓库根目录运行：

```sh
make all                        # 重建并检查链接、锚点、搜索覆盖和快捷键
make serve                      # 打开 http://localhost:8000 预览
make PYTHON=.venv/bin/python all  # 使用虚拟环境
```

`make build` 只重建，`make check` 只检查。生成的页面在 `docs/`，GitHub Pages 从 `main` 分支的 `/docs` 发布。修改网站后，提交课稿、课表和重建后的网页，再推送到 `main`。原始插图和练习文件在 `assets/`，样式、脚本和自托管字体在 `site/`。

需要清理本地临时文件时，在仓库根目录运行 `make clean`，可移除 `.DS_Store` 和 Python 缓存。
