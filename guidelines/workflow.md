# 课程和网站怎么维护

这是你和协作工具共用的维护说明。审课时可直接打开对应课稿，新增专题、加讲或补素材时再查这里。本文件里的路径都相对仓库根目录。

```text
course/topics/mac/               专题：topic.md + 01-….md
course/topics/ai/
course/topics/word-to-latex/
course/topics/cad/
course/topics/image-generation/
course/topics/version-control/
course/curriculum.md             课程地图：逐讲计划、前置、验收和覆盖点
course/gallery/whiteboard.md     拾趣（不占专题）
course/archive/audit-01-07.md    历史核查记录
assets/topics/<slug>/            该专题的图片、示例和工具
assets/gallery/                  拾趣图片
assets/site/                     全站侧脸插画、图标、线稿
site/build.py                    从 topics 和 gallery 生成网页
site/style.css                   全站样式和设计变量
site/ui.js                       菜单、目录高亮、提示词复制
site/search.js                   搜索页交互
site/check_site.py               链接、锚点、搜索、残留检查
site/fonts/                      自托管的拉丁字体
docs/                            生成物，GitHub Pages 从这里发布
```

## 专题和讲次

- 一个专题一个文件夹，英文 slug；`topic.md` 写 `title`、`subtitle`、`summary`、`order`，需要时加 `optional: true`（页面显示「按需」）或 `ai: practice`（专题卡显示「用 AI」）。
- 讲次写在同一文件夹，文件名 `NN-slug.md`；frontmatter 必填 `title`、`audience`（`dad|mom|both`）、`status`（`active|followup|draft`）、`summary`。
- 编号只决定顺序，不写进 URL 之外的展示；页面显示「第 N 讲」，不再出现 Lesson。
- 正文从介绍段开始，`### 1. …` 是步骤；步骤会生成本节目录和搜索条目。
- 跨讲引用写相对 Markdown 链接，例如 `[下一讲](02-read-a-drawing.md)`、`[上一专题](../ai/01-models-and-tools.md)`；构建器会改成网页链接。
- 素材放 `assets/topics/<slug>/`，课稿用 `../../../assets/topics/...` 引用；构建器复制被引用的文件，并给非 HTML 素材加 `download`。

## 课程地图

- `course/curriculum.md` 是计划索引，不是第二份课稿；正文仍然只写在 `course/topics/<slug>/NN-slug.md`。
- 每个专题一节，每讲一行，记录 `讲 / 文件 / 标题 / 受众 / 状态 / 前置 / 学完能做到 / 产出验收 / 覆盖点 / 视觉`。
- 新增一讲：先在地图加行，再建课稿；改标题、受众、状态、顺序或验收时，两边一起改。
- 删除一讲：同时删地图行和课稿，并更新 README 的讲数。
- 新增专题：建 `topic.md`、在地图加专题段、更新 README 专题总览。
- `make check` 校验地图和课稿是否一一对应；重复覆盖点、相似标题/摘要、重复步骤标题只提醒，不自动删课。
- 覆盖点用具体短标签，例如 `cad-roundtrip`，不要用「AI」「GitHub」这种泛词。

## 一讲怎样变成网页

1. **先定小任务**：输入、动手步骤、产出、怎样确认成功。需要 AI 做具体任务时给可直接使用的提示词，写清材料、允许范围、预期结果和亲手核对办法。
2. **补素材并确认**：只发布实际制作并核对过的图；截图裁掉账号和个人信息；真实图纸和家庭资料留在本机。
3. **改课程地图、frontmatter 和 README**：先在 `course/curriculum.md` 加/改计划，再改讲次 frontmatter；新增讲更新 README 的专题总览和 `guidelines/skills.md`，新增专题更新总览表。
4. **重建**：`make build`。
5. **检查**：`make check`。链接、锚点、搜索覆盖、快捷键和残留有一项不过就不发布。
6. **预览**：`make serve`，看首页、专题总览、每个专题、两条路径、课页和搜索；按 1280/1024/500px 和 200% 放大检查，打印一节长课。
7. **提交**：课稿、专题文件、素材、样式和重建后的 `docs/` 一起提交；推送 `main` 后等 1–2 分钟刷新线上地址。

## 配图流程

- 先在 `course/curriculum.md` 的 `视觉` 列写类型和数量，例如 `结果图 ×3`、`概念图 ×2`。
- 真实截图放 `assets/topics/<slug>/screenshots/`；概念图、SVG 和 ChatGPT 生成示意图放 `assets/topics/<slug>/illustrations/`；DXF、ZIP、PDF 等练习文件继续放 `examples/`。不新增 `images/` 目录。
- 文件名 `NN-短描述.扩展名`；一讲多图用 `NN-短描述-2`。
- 课稿用 HTML `figure` 引用，图片必须有非空 `alt` 和一句 `figcaption`：
  ```html
  <figure>
    <img src="../../../assets/topics/mac/screenshots/01-remote-meeting.png"
         alt="腾讯会议窗口，底部工具栏有共享屏幕按钮"
         width="1600" height="1000" loading="lazy">
    <figcaption>图注：点底部工具栏的共享屏幕。</figcaption>
  </figure>
  ```
- 真实截图裁掉账号、通知、姓名和私人文件；AI 生成图在图注写「ChatGPT 生成」，不冒充真实界面或结果。
- 每讲最多 3 张图，每个 `###` 步骤最多 1 张；没有必要时不配图。
- 运行 `make all`；检查 1280px、500px 和打印。图片确认后再更新 `视觉` 状态。

## URL

- 页面：`/`、`/topics/`、`/topics/<slug>/`、`/topics/<slug>/<stem>.html`、`/dad/`、`/mom/`、`/gallery/`。
- URL 由专题 slug 和讲次文件名决定；调整后直接生效，不保留旧路径兼容页或重定向映射。
- 调整讲次文件名或专题 slug 时，同步改所有站内引用，再跑 `make check`。

## 搜索和素材

- 搜索索引按每个 `###` 段落生成，另加每个专题一条介绍；字段含专题、讲次、受众、标题、步骤、正文和 URL。
- 搜索页用 `?q=` 和 `?topic=`；筛选项由专题自动生成，另加「拾趣」。
- CSS/JS 引用带内容版本号 `?v=`；改样式、脚本或课稿后重新构建。
- 外部链接自动加 `target="_blank" rel="noopener"`；发布前抽查官方域名和页面用途。

## CAD 工作流

- 使用外部 **CADCraft App + cadcraft-cli**；仓库不提交二进制，安装步骤写在 CAD 专题第 1 讲。
- 示例只放虚构的 `assets/topics/cad/examples/sample-pfd.dxf` 和它的预览图；真实图纸、台账、修改记录和截图只在本机 `~/CAD-Work/`。
- 课程默认自然语言：父亲说任务，Harness 执行 `info`、`run --cmd`（`drawing.inspect`/`texts`/`attedit`/`properties.set`/`move`/`erase`）、`convert` 和 `saveas`；命令块是备查/手动兜底。
- 工作区必须放 `CAD-Work-AGENTS.md` 模板（安装讲第 4 步），固定只读原件、先计划后执行、保真门槛和报告要求。
- 禁止 GUI 自动化，包括向 AutoCAD 键入命令；AutoCAD 只作为人工目视核对的备选。

## 嵌入式浏览器

- 每个页面由构建器写入 `data-page-dir` 和一段内联导航脚本；在 iframe 中用真实页面目录设置 `<base>`，并把内部链接改成绝对地址。
- 普通 Chrome 和 `make serve` 是顶层页面，不加 base；如果预览时链接被带到线上，先确认是不是在 iframe 里打开的。
- 页脚「在浏览器打开」是兜底。

## 全部 Markdown 复查

改完课稿、专题、README、website、workflow、teaching、skills 后，人工读一遍：

- 每个专题有 `topic.md`，每讲 frontmatter 齐全，编号唯一；
- `course/curriculum.md` 覆盖每个专题和每一讲，标题、受众、状态与课稿一致；
- `README.md` 的专题总览与 `course/topics/` 一致；
- 课稿里的相对链接和 `assets/topics/` 引用都存在；
- `guidelines/skills.md` 的妈妈长期技能完整保留；
- 没有 `course/lessons/`、`course/practices/` 或旧课稿残留；
- 真实图纸、位数和审图批注没有进入仓库。

做网页批注时，从右侧 Files 面板直接打开对应的 `.html` 课页（例如 `docs/topics/mac/01-new-mac.html`）；批注按文件保存，改完发送给 Agent。

从[第一个专题](../course/topics/mac/topic.md)开始。语言、颜色、字体和打印规则见[网站语言与视觉规范](website-style.md)。
