# 爸妈的 Mac 与 AI 课

**[打开公开课程网站](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/)** · [爸爸的课表](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/dad/) · [妈妈的课表](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/mom/)

网站通过 GitHub Pages 发布，首页可搜索课名和正文。课程正文维护在 Markdown 课稿中，网页由课稿生成。[网站设计](website.md)

## 2026 年 12 月家庭试讲

爸爸目前进度较快，第 1–8 节安排腾讯会议，第 9 节作为后续课继续推进；制作模板的第 6 节可分多次完成。妈妈仍按原安排进行：第 1 节在上海家中，第 2–4 节腾讯会议，第 5–7 节在上海家中。两条路线不要求同步。

| 课稿 | 爸爸方式 | 爸爸 | 妈妈方式 | 妈妈 |
|---|---|---|---|---|
| [第 1 节](course/lessons/01.md) | 腾讯会议 | 认识模型和工具，用自己的 DeepSeek 账户跑通 Codex | 上海家中 | 新 Mac 联网后先装豆包桌面版，试语音通话和屏幕共享，再更新和验证入会 |
| [第 2 节](course/lessons/02.md) | 腾讯会议 | 初始化 DeepSeek Harness，安装微信输入法与六个指定插件 | 腾讯会议 | 安装应用、配邮箱并核对同步 |
| [第 3 节](course/lessons/03.md) | 腾讯会议 | 在 DeepSeek Harness 比较推理强度与用量，练习读网页和日程 | 腾讯会议 | 快捷键和触控板，验证共享日历、备忘录和相册 |
| [第 4 节](course/lessons/04.md) | 腾讯会议 | 说清 Word 转 LaTeX 的输入、产出和长期工作流目标 | 腾讯会议 | 会议预约与分享、语音输入、MacTeX 验证 |
| [第 5 节](course/lessons/05.md) | 腾讯会议 | 编译中文 LaTeX，练习 PDF 批注并认识 Overleaf 模板库 | 上海家中 | 请参考爸爸第 1 节 |
| [第 6 节](course/lessons/06.md) | 腾讯会议 | 在 Overleaf 选模板，做可编译的中文多章节技术书并逐项验收 | 上海家中 | 请参考爸爸第 3 节 |
| [第 7 节](course/lessons/07.md) | 腾讯会议 | 分开放 Overleaf 模板来源、通用模板和第一份 Word，建立项目目录 | 上海家中 | 后续内容待重新安排 |
| [第 8 节](course/lessons/08.md) | 腾讯会议 | 写项目指令、阶段路线与内容保持规则，并开新会话核对 | — | — |
| [第 9 节](course/lessons/09.md) | 后续课 | 用已验证模板转换一小段 Word，编译、核对并沉淀流程 | — | — |

后续草稿保留在仓库中。

- [妈妈第 8 节](course/lessons/08.md)｜做可本地预览的养花小站。
- [妈妈第 9 节及 GitHub 共同练习](course/lessons/github.md)｜各自的项目起步后，注册 GitHub、建立私有仓库，用 Codex 帮忙提交与推送。
- [妈妈第 10 节](course/lessons/10.md)｜给养花小站写维护规则。

备课可参照[家庭带练方式](teaching.md)和[长期技能地图](skills.md)。[AGENTS.md](AGENTS.md)与 [CLAUDE.md](CLAUDE.md)供后续维护使用。

从[第 1 节课稿](course/lessons/01.md)开始。目录、素材和迭代步骤见[工作流程](workflow.md)，简体中文、British English 和视觉规则见[网站语言与视觉规范](website-style.md)。

[首版课稿核查记录（课号沿用首版）](course/audit-01-07.md)

## 本地预览与发布

直接用浏览器打开 `docs/index.html` 即可预览。修改课程 Markdown、课程总览或站点样式后，在仓库根目录执行以下命令重建。已有虚拟环境时，可直接运行最后一条。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r site/requirements.txt
.venv/bin/python site/build.py
```

`.venv` 仅用于本机。生成的页面在 `docs/`，GitHub Pages 从 `main` 分支的 `/docs` 发布。修改网站后，提交课稿及重建后的网页，再推送到 `main`。原始插图在 `assets/`，样式与生成脚本在 `site/`。

需要清理本地临时文件时，在仓库根目录运行 `make clean`，可移除 `.DS_Store` 和 Python 缓存。
