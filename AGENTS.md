# 课程仓库协作说明

1. 先读 README.md 和 teaching.md，理解课程受众、节奏和机器起点。
2. 内容只按专题组织：`course/topics/<英文slug>/topic.md` 定义专题，`NN-slug.md` 定义讲次。新增专题建新文件夹和 `topic.md`；给已有专题加内容就继续加 `NN-slug.md`。不要重建 `course/lessons/`、`course/practices/` 或其它与 topics 平级的课程目录。
3. 每讲 frontmatter 必填 `title`、`audience`（`dad|mom|both`）、`status`（`active|followup|draft`）、`summary`；`topic.md` 必填 `title`、`subtitle`、`summary`、`order`、可选 `optional`。讲次编号在同一专题内唯一，顺序按文件名前缀。
4. 新增或修改内容、制作或更新网页前，都读 website.md 和 website-style.md。按具体教学需要决定是否配图；未制作的图片构想不要写进学员课稿。需要指认界面操作时优先考虑可公开、已遮去个人信息的真实截图。操作步骤需要外部入口时，加入并验证官方直达链接。
5. 示例用虚构或明确可分享的素材。仓库只放教学资料，真实家庭媒体、技术档案、密钥和账号资料留在本地私有目录。
6. 工具或版本尚未确认时写明现场验证条件，保留低门槛替代流程。修订后检查相对链接和每条路线的任务是否明确。
7. 需要学员让 AI 完成具体任务时，给出可直接使用的提示词示例，写清任务、可用材料或工具、操作范围、预期结果和亲手核对的方法。使用虚构或测试素材，按实际课堂条件替换占位内容。简单的手动操作保持短步骤。
8. 网站由 `site/build.py` 从 `course/topics/`、`course/gallery/` 和 README 的专题总览生成，`docs/` 是生成物。修改课稿、专题或样式后运行 `make build && make check`；不要手改 `docs/`。保留课稿里的快捷键写法（如 `⌘C`）和课页的本节步骤、上一讲/下一讲导航；新增讲必须同时更新 README 专题总览、`skills.md` 和搜索覆盖。
9. 旧 URL 只由 `site/build.py` 的 `LEGACY_REDIRECTS` 生成重定向页；源码树里不得保留旧课稿、旧目录、别名文件或指向旧目录的过渡结构。
10. 拾趣是独立栏目，不占专题，内容在 `course/gallery/*.md`，图片放 `assets/gallery/`；页面文案用「拾趣」，技术路径保留 `/gallery/`。公开真人姓名、单位、邮箱或原图前必须获得本人确认；`whiteboard-original.jpeg` 和赵诗雅博士的联系方式已确认公开，是明确例外。
11. 爸爸的 CAD 工作流只做文件层（DXF）读取、计划式修改和重读校验，**禁止用 GUI 自动化向 AutoCAD 键入命令**。真实 AutoCAD 图纸、图号、位号、修改计划和报告留在本机私有目录（如 `~/CAD-Review/`），不进入仓库、截图或公开网页；审图批注只以「文件路径 + handle」引用。

本仓库直接承载爸爸妈妈的公开 HTML 教程网站。根据两人的实际进度维护各自的学习路径。学员页以 `course/topics/` 的 Markdown 为内容源，`docs/` 由构建器生成，发布内容使用可公开的素材和占位信息。编辑前读 workflow.md，涉及站点结构或语言视觉时读 website.md 和 website-style.md。网页反馈涉及内容时回写 Markdown。
