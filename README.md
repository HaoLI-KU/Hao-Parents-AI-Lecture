# 爸妈的 Mac 与 AI 课

**[打开公开课程网站](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/)** · [爸爸的课表](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/dad/) · [妈妈的课表](https://haoli-ku.github.io/Hao-Parents-AI-Lecture/mom/)

网站已在 GitHub Pages 上线。两条路线均已发布第 1–7 节，首页可搜索课名和正文。课程正文维护在 Markdown 课稿中，网页由课稿生成。[网站设计](website.md)

## 2026 年 12 月家庭试讲

第 1、3、5、7、9、11、13 天上课，每次留一段大致的时间，按当天进度灵活安排。第 14 天留作补练。第 1、5、6、7 节在上海家中，第 2–4 节通过腾讯会议。

| 课稿 | 方式 | 爸爸 | 妈妈 |
|---|---|---|---|
| [第 1 节](course/lessons/01.md) | 上海 | 认识模型和工具，用自己的 DeepSeek 账户跑通 Codex | 新 Mac 联网后先装豆包桌面版，试语音通话和屏幕共享，再更新和验证入会 |
| [第 2 节](course/lessons/02.md) | 腾讯会议 | 用 Chat 查生活信息，认识 DeepSeek 推理强度与用量 | 安装应用、配邮箱并核对同步 |
| [第 3 节](course/lessons/03.md) | 腾讯会议 | 归档文件，比较 Codex 权限与审批 | 快捷键和触控板，验证共享日历、备忘录和相册 |
| [第 4 节](course/lessons/04.md) | 腾讯会议 | 用 Codex 编译并排错多章节中文 LaTeX 项目 | 会议预约与分享、语音输入、MacTeX 验证 |
| [第 5 节](course/lessons/05.md) | 上海 | 讨论文档愿景，比较 PDF 的几种修改方式 | 请参考爸爸第 1 节 |
| [第 6 节](course/lessons/06.md) | 上海 | 建技术手册目录和 Markdown 规则 | 请参考爸爸第 2 节 |
| [第 7 节](course/lessons/07.md) | 上海 | 确定第一个真实项目，一起挑 Overleaf 模板 | 请参考爸爸第 3 节 |

第 7 节是本次休假的最后一节线下课。第 8–10 节为后续草稿，目前保留在仓库中。

- [第 8 节](course/lessons/08.md)｜爸爸按真实项目和选定模板搭目录、写首批 Markdown 规则，妈妈做可本地预览的养花小站。
- [第 9 节](course/lessons/09.md)｜爸妈各自注册 GitHub、建立私有仓库，用 Codex 帮忙提交与推送各自的项目。
- [第 10 节](course/lessons/10.md)｜妈妈给养花小站写维护规则，爸爸内容待定。

备课可参照[家庭带练方式](teaching.md)和[长期技能地图](skills.md)。[AGENTS.md](AGENTS.md)与 [CLAUDE.md](CLAUDE.md)供后续维护使用。

从[第 1 节课稿](course/lessons/01.md)开始。目录、素材和迭代步骤见[工作流程](workflow.md)，简体中文、British English 和视觉规则见[网站语言与视觉规范](website-style.md)。

[第 1–7 节事实核查与现场待验证项](course/audit-01-07.md)

## 本地预览与发布

直接用浏览器打开 `docs/index.html` 即可预览。修改课程 Markdown、课程总览或站点样式后，在仓库根目录执行以下命令重建。已有虚拟环境时，可直接运行最后一条。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r site/requirements.txt
.venv/bin/python site/build.py
```

`.venv` 仅用于本机。生成的页面在 `docs/`，GitHub Pages 从 `main` 分支的 `/docs` 发布。修改网站后，提交课稿及重建后的网页，再推送到 `main`。原始插图在 `assets/`，样式与生成脚本在 `site/`。

需要清理本地临时文件时，在仓库根目录运行 `make clean`，可移除 `.DS_Store` 和 Python 缓存。
