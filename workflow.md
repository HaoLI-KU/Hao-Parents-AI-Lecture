# 课程和网站怎么维护

这是你和协作工具共用的维护说明。审课时可直接打开对应课稿，新增课、补素材或调整网页时再查这里。

```text
course/lessons/01.md               一课一份，内分爸爸和妈妈
course/lessons/github.md           共同练习正文
course/audit-01-07.md              首版核查记录（历史，课号沿用首版）
assets/lessons/01/screenshots/      第 1 节可公开的截图
assets/lessons/01/examples/         第 1 节可公开的案例、模板及练习文件
assets/lessons/01/illustrations/    已制作并核对的教学示意图
assets/site/                        全站侧脸插画、图标
site/build.py                       从 Markdown 和 README 课表生成网页
site/style.css                      全站样式和设计变量
site/ui.js                          菜单、目录高亮、提示词复制
site/search.js                      搜索页交互
site/check_site.py                  链接、锚点、搜索覆盖和快捷键检查
site/fonts/                         自托管的拉丁字体
skills.md                           长期技能地图，用来选课题
teaching.md                         简短的家庭带练方式
website.md                          站点结构、搜索和发布规则
website-style.md                    语言、视觉、字体和打印规范
docs/                               生成物，GitHub Pages 从这里发布
```

## 一节课怎样从草稿变成网页

1. **先定小任务。** 每条路线写清输入是什么、要动手做哪几步、最后产出什么以及如何确认成功。需要让 AI 完成具体任务时，在课稿提供可直接使用的提示词，交代材料或工具、允许操作的范围、预期结果和学员怎样亲手核对；只需手动点按的操作保持短步骤。
2. **补素材并确认。** 例如第 1 节新 Mac 的入会截图放到 `assets/lessons/01/screenshots/mom-join-test-meeting.png`，虚构技术案例放在 `assets/lessons/01/examples/`。使用课号、小写英文和连字符。从对应课稿用相对链接引用，图片补上说明和替代文字。需要解释实际按钮或菜单时，可使用已遮去个人信息的真实截图；确定有教学价值并完成制作的插图按课号放入 `assets/lessons/NN/illustrations/`。未制作的配图想法留在备课记录中。
3. **更新课表。** 在 `README.md` 的双路线表格中加行或改行。列名保持 `课稿`、`爸爸方式`、`爸爸`、`妈妈方式`、`妈妈`、`说明`；某一侧没有这一节时写 `—`。方式列写「草稿」的课会进入路线页的「后续课程」分组。爸爸和妈妈各自编号，不必同步。
4. **重建。** 在仓库根目录运行：

   ```sh
   make build
   ```

   构建器会读取 README 课表，从 `course/lessons/NN.md` 提取 `## 爸爸｜…` / `## 妈妈｜…` 正文，生成 `docs/` 下的课表、课页、搜索页、共同练习页和搜索索引，并复制被引用的素材和字体。
5. **检查。** 运行：

   ```sh
   make check
   ```

   这项检查内部链接、锚点、重复 `id`、`.md` 残留链接、课稿是否都进了课表、搜索索引覆盖、快捷键是否保留。任何错误先修，不带错误发布。
6. **预览。** 运行 `make serve`，打开 `http://localhost:8000`。对照 1280px、1024px、500px 和 200% 放大看首页、课表和课页；用一份长课检查提示词、表格、清单和打印。
7. **提交。** 课稿、README 课表、样式、脚本和重建后的 `docs/` 一起提交。推送 `main` 后 GitHub Pages 自动发布，等 1–2 分钟刷新线上地址。

## 草稿和发布

- 妈妈第 8–10 节和 GitHub 共同练习目前是草稿：README 方式列带「草稿」，路线页单独分组。
- 某节课还没准备好时，把对应方式列改成 `—`，重新构建，页面和课表入口会消失；课稿文件仍留在仓库。
- 草稿课页也进入搜索索引，但结果带「草稿」标签。不要把它当成当天任务。
- 共同练习不占课号，正文只维护 `course/lessons/github.md`，页面固定在 `docs/practice/github.html`。

## 链接和锚点

- 课稿里跨课引用写 `01.md#dad`、`05.md#dad`、`github.md`；构建器会改成 `lesson-01.html#dad`、`../dad/lesson-05.html#dad`、`../practice/github.html`。
- 课页内容容器保留 `id="dad"` / `id="mom"`，共同练习页保留 `id="practice"`；搜索索引和跨课链接依赖这些锚点。
- 不要手写 `docs/` 里的路径，也不要手改 `docs/` 页面。
- 外部链接在页面上自动加 `target="_blank" rel="noopener"`；发布前人工抽查官方域名、页面用途和下载平台。

## 搜索和素材

- 搜索索引由构建器按每个 `###` 段落生成；新增或改写步骤后重新 `make build`，`make check` 会确认每节课页至少有索引条目。
- 搜索页的查询用 `?q=`，路线筛选用 `?route=dad|mom|practice`；不要手工维护结果列表。
- 课稿里引用 `../../assets/...` 的练习文件会在构建时复制到 `docs/assets/`；没有引用的素材不会进入发布目录。
- 真实家庭媒体、技术档案、密钥和账号资料留在本地私有目录，不放进 `assets/` 或课稿。

## 反馈和回写

- 反馈可以用「第 1 节 / 爸爸 / 第 4 步」直接标出。
- 改步骤、文字或示例时回写课稿；改外观时更新 `site/style.css`、`website.md` 和 `website-style.md`。
- 网页上发现的内容错误，先改 Markdown，再 `make build`，不要只改生成页。

从[第 1 节课稿](course/lessons/01.md)开始。目录、素材和迭代步骤见本页，简体中文、British English 和视觉规则见[网站语言与视觉规范](website-style.md)。
