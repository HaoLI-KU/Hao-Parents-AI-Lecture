# 课程和网站怎么维护

这是你和协作工具共用的维护说明。审课时可直接打开对应课稿，新增课、补素材或调整网页时再查这里。

```text
course/lessons/01.md               一课一份，内分爸爸和妈妈
course/lessons/github.md           共同练习：GitHub（备用）
course/lessons/image-gen.md        共同练习：Seedream 生图
course/audit-01-07.md              首版核查记录（历史，课号沿用首版）
assets/lessons/06/examples/        第 6 节参考模板、ZIP 和预览 PDF
assets/lessons/01/screenshots/     第 1 节可公开的截图
assets/lessons/01/examples/        第 1 节可公开的案例、模板及练习文件
assets/site/                       全站侧脸插画、图标
site/build.py                      从 Markdown 和 README 课表生成网页
site/style.css                     全站样式和设计变量
site/ui.js                         菜单、目录高亮、提示词复制
site/search.js                     搜索页交互
site/check_site.py                 链接、锚点、搜索、共同练习、方式残留检查
site/fonts/                        自托管的拉丁字体
docs/                              生成物，GitHub Pages 从这里发布
```

## 一节课或一个共同练习怎样变成网页

1. **先定小任务。** 每条路线写清输入、要动手的步骤、最后产出和如何确认成功。需要 AI 完成具体任务时，在课稿提供可直接使用的提示词，交代材料或工具、允许操作范围、预期结果和学员怎样亲手核对；简单手动操作保持短步骤。
2. **补素材并确认。** 可公开的截图放 `assets/lessons/NN/screenshots/`，示例放 `examples/`，已核对的示意图放 `illustrations/`。课稿用相对链接引用，图片补说明和替代文字。未制作的配图想法留在备课记录中，真实家庭媒体和私人资料不进仓库。
3. **更新课表或共同练习。** 路线课在 `README.md` 的表格中加行/改行，列名保持 `课稿`、`爸爸`、`妈妈`、`状态`、`说明`；某一侧没有这一节时写 `—`，`状态` 只写“后续课/草稿”，不写地点或平台。共同练习写进 `README.md` 的“共同练习”小节，并在 `site/build.py` 的 `PRACTICES` 中登记。
4. **重建。** 在仓库根目录运行 `make build`。构建器读取 README 课表，从 `course/lessons/NN.md` 提取 `## 爸爸｜…` / `## 妈妈｜…` 正文，生成 `docs/` 下的课表、课页、共同练习首页、练习页、搜索页和搜索索引，并复制被引用的素材和字体。
5. **检查。** 运行 `make check`：检查内部链接、锚点、重复 `id`、`.md` 残留链接、课稿是否都进了课表、共同练习覆盖、搜索索引、快捷键、方式标签和养花草稿残留。任何错误先修，不带错误发布。
6. **预览。** 运行 `make serve`，打开 `http://localhost:8000`。对照 1280px、1024px、500px 和 200% 放大看首页、两条课表、共同练习首页和课页；用一份长课检查提示词、表格、清单和打印。
7. **提交。** 课稿、README 课表、样式、脚本和重建后的 `docs/` 一起提交。推送 `main` 后 GitHub Pages 自动发布，等 1–2 分钟刷新线上地址。

## 共同练习

- `/practice/index.html` 是共同练习首页；`/practice/github.html` 和 `/practice/image-gen.html` 是两个练习页。
- 共同练习不占爸爸妈妈的课号，不写进路线课表；只在 README 的“共同练习”小节和站点栏目出现。
- GitHub 练习是备用：需要时再排，内容保持通用，不依赖养花项目。
- Seedream 生图练习是按需安排：先核对火山方舟/模型价格和账号状态，再让父母用自己的 API Key 跑通。课程里的模型 ID、价格和限制可能变化，发布前以火山方舟控制台和官方文档为准。
- 真实家庭照片、门牌、API Key 不进公开仓库；公开课稿只用虚构房间。

## 爸爸第 6 节的参考模板

- 源文件在 `assets/lessons/06/examples/chinese-book-template/`，ZIP 和预览 PDF 在同一层。
- 改模板后在本机运行 `latexmk -xelatex main.tex`，检查 PDF 后再重新生成 ZIP；不要提交 `.aux/.log/.toc/.out/.bcf/.run.xml/.idx/.ind/.ilg/.fls/.fdb_latexmk` 和 `main.pdf`（预览 PDF 单独放）。
- 参考模板是课程样例，不替代爸爸选中的 Overleaf 模板；正式项目仍按 `template/technical-book/` 的工作副本维护。

## 链接、搜索和素材

- 课稿里跨课引用写 `01.md#dad`、`03.md#dad`、`github.md`、`image-gen.md`；构建器会改成对应 HTML 课页和锚点。
- 课页内容容器保留 `id="dad"` / `id="mom"`，共同练习页保留 `id="practice"`。
- 不要手写 `docs/` 里的路径，也不要手改 `docs/` 页面。
- 搜索索引由构建器按每个 `###` 段落生成；共同练习按 `##` 段落生成；新增或改写步骤后重新 `make build`。
- 搜索页的查询用 `?q=`，路线筛选用 `?route=dad|mom|practice`；不要手工维护结果列表。
- 课稿里引用 `../../assets/...` 的练习文件会在构建时复制到 `docs/assets/`；没有引用的素材不会进入发布目录。
- 外部链接在页面上自动加 `target="_blank" rel="noopener"`；发布前人工抽查官方域名、页面用途和下载平台。

## 嵌入式浏览器

- 站点的每个页面由构建器写入 `data-page-dir` 和一段内联导航脚本；在 iframe 中用真实页面目录设置 `<base>`，并把内部链接改成绝对地址。
- 普通 Chrome 和 `make serve` 是顶层页面，不加 base；如果预览时链接被带到线上，先确认是不是在 iframe 里打开的。
- 页脚“在浏览器打开”是兜底；DeepSeek 侧栏仍空白时，记录具体页面和地址，再判断是侧栏 iframe 状态还是站点链接问题。

## 全部 Markdown 复查

改完课稿、README、website、workflow、teaching、skills 后，人工读一遍：

- 标题、状态、爸爸/妈妈小节与 README 课表一致；
- `NN.md`、`NN.md#dad`、共同练习链接都指向存在的文件；
- 妈妈 1–4 未改；5–7 指向爸爸 1–3；没有妈妈 8–10 和养花草稿；
- `skills.md` 妈妈长期技能完整保留，不被清理误删；
- README/website/workflow/teaching 没有排课方式标签；课表和课页 eyebrow 也没有；
- 爸爸第 6 节的模板、ZIP、PDF、检查表和参考模板文件树一致；
- 共同练习首页、GitHub、Seedream 生图三页互链正确；生图事实和链接可核对。

做网页批注时，从右侧 Files 面板直接打开对应的 `.html` 课页文件（例如 `docs/dad/lesson-02.html`）；批注按文件保存，改完发送给 Agent。跨页批注浮层不在多页站点的设计范围内。

从[第 1 节课稿](course/lessons/01.md)开始。语言、颜色、字体和打印规则见[网站语言与视觉规范](website-style.md)。
