# 课程和网站怎么维护

这是你和协作工具共用的维护说明。审课时可直接打开对应课稿，新增专题、加讲或补素材时再查这里。

```text
course/topics/mac/               专题：topic.md + 01-….md
course/topics/ai/
course/topics/word-to-latex/
course/topics/cad/
course/topics/image-generation/
course/topics/version-control/
course/gallery/whiteboard.md     拾趣（不占专题）
course/archive/audit-01-07.md    历史核查记录
assets/topics/<slug>/            该专题的图片、示例和工具箱
assets/gallery/                  拾趣图片
assets/site/                     全站侧脸插画、图标、线稿
site/build.py                    从 topics 和 gallery 生成网页
site/style.css                   全站样式和设计变量
site/ui.js                       菜单、目录高亮、提示词复制
site/search.js                   搜索页交互
site/check_site.py               链接、锚点、搜索、重定向、残留检查
site/fonts/                      自托管的拉丁字体
docs/                            生成物，GitHub Pages 从这里发布
```

## 专题和讲次

- 一个专题一个文件夹，英文 slug；`topic.md` 写 `title`、`subtitle`、`summary`、`order`，需要时加 `optional: true`（页面显示「按需」）。
- 讲次写在同一文件夹，文件名 `NN-slug.md`；frontmatter 必填 `title`、`audience`（`dad|mom|both`）、`status`（`active|followup|draft`）、`summary`。
- 编号只决定顺序，不写进 URL 之外的展示；页面显示「第 N 讲」，不再出现 Lesson。
- 正文从介绍段开始，`### 1. …` 是步骤；步骤会生成本节目录和搜索条目。
- 跨讲引用写相对 Markdown 链接，例如 `[下一讲](02-read-a-drawing.md)`、`[上一专题](../ai/01-models-and-tools.md)`；构建器会改成网页链接。
- 素材放 `assets/topics/<slug>/`，课稿用 `../../../assets/topics/...` 引用；构建器复制被引用的文件，并给非 HTML 素材加 `download`。

## 一讲怎样变成网页

1. **先定小任务**：输入、动手步骤、产出、怎样确认成功。需要 AI 做具体任务时给可直接使用的提示词，写清材料、允许范围、预期结果和亲手核对办法。
2. **补素材并确认**：只发布实际制作并核对过的图；截图裁掉账号和个人信息；真实图纸和家庭资料留在本机。
3. **改 frontmatter 和 README**：新增讲更新 README 的专题总览和 `skills.md`；新增专题更新总览表。
4. **重建**：`make build`。
5. **检查**：`make check`。链接、锚点、搜索覆盖、重定向、快捷键和残留有一项不过就不发布。
6. **预览**：`make serve`，看首页、专题总览、每个专题、两条路径、课页、搜索和重定向；按 1280/1024/500px 和 200% 放大检查，打印一节长课。
7. **提交**：课稿、专题文件、素材、样式和重建后的 `docs/` 一起提交；推送 `main` 后等 1–2 分钟刷新线上地址。

## URL 和重定向

- 页面：`/`、`/topics/`、`/topics/<slug>/`、`/topics/<slug>/<stem>.html`、`/dad/`、`/mom/`、`/gallery/`。
- 旧课页 URL 不保留源码文件，只在 `site/build.py` 的 `LEGACY_REDIRECTS` 里映射；每次构建生成 22 个重定向页。
- 新增或调整讲次时，如果 URL 会变，把旧路径加进 `LEGACY_REDIRECTS`，并让 `make check` 验证目标存在。
- 不要手写 `docs/` 里的重定向。

## 搜索和素材

- 搜索索引按每个 `###` 段落生成，另加每个专题一条介绍；字段含专题、讲次、受众、标题、步骤、正文和 URL。
- 搜索页用 `?q=` 和 `?topic=`；筛选项由专题自动生成，另加「拾趣」。
- CSS/JS 引用带内容版本号 `?v=`；改样式、脚本或课稿后重新构建。
- 外部链接自动加 `target="_blank" rel="noopener"`；发布前抽查官方域名和页面用途。

## CAD 工具箱

- 位置：`assets/topics/cad/toolkit/`；示例在 `assets/topics/cad/examples/`。
- 改工具后运行 `python3 cad.py selftest`，再跑 `make build`，让课稿里的下载文件和示例同步。
- 工作流只做 DXF 文件层：`inventory`、`check-plan`、`apply`（dry-run/写副本/重读校验）、`review`、`convert`；不要写 GUI 自动化。
- 真实图纸、清单、计划、报告只在本机 `~/CAD-Review/`；公开示例必须是虚构的。

## 嵌入式浏览器

- 每个页面由构建器写入 `data-page-dir` 和一段内联导航脚本；在 iframe 中用真实页面目录设置 `<base>`，并把内部链接改成绝对地址。
- 普通 Chrome 和 `make serve` 是顶层页面，不加 base；如果预览时链接被带到线上，先确认是不是在 iframe 里打开的。
- 页脚「在浏览器打开」是兜底。

## 全部 Markdown 复查

改完课稿、专题、README、website、workflow、teaching、skills 后，人工读一遍：

- 每个专题有 `topic.md`，每讲 frontmatter 齐全，编号唯一；
- `README.md` 的专题总览与 `course/topics/` 一致；
- 课稿里的相对链接和 `assets/topics/` 引用都存在；
- `skills.md` 的妈妈长期技能完整保留；
- 没有 `course/lessons/`、`course/practices/` 或旧课稿残留；
- `LEGACY_REDIRECTS` 覆盖所有已迁移的旧 URL；
- 真实图纸、位数和审图批注没有进入仓库。

做网页批注时，从右侧 Files 面板直接打开对应的 `.html` 课页（例如 `docs/topics/mac/01-new-mac.html`）；批注按文件保存，改完发送给 Agent。

从[第一个专题](course/topics/mac/topic.md)开始。语言、颜色、字体和打印规则见[网站语言与视觉规范](website-style.md)。
