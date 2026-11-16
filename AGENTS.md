# 课程仓库协作说明

1. 先读 README.md 和 teaching.md，理解课程受众、节奏和机器起点。
2. 编辑单课时读 course/lessons/ 对应文件及 skills.md，每课用一份 Markdown 写两条路线。新增课程沿用编号与结构，并更新 README 索引。
3. 新增或修改课程、制作或更新网页前，都读 website.md 和 website-style.md。按具体教学需要决定是否配图；未制作的图片构想不要写进学员课稿。需要指认界面操作时优先考虑可公开、已遮去个人信息的真实截图。操作步骤需要外部入口时，加入并验证官方直达链接。
4. 示例用虚构或明确可分享的素材。仓库只放教学资料，真实家庭媒体、技术档案、密钥和账号资料留在本地私有目录。
5. 工具或版本尚未确认时写明现场验证条件，保留低门槛替代流程。修订后检查相对链接和每条路线的任务是否明确。
6. 需要学员让 AI 完成具体任务时，给出可直接使用的提示词示例，写清任务、可用材料或工具、操作范围、预期结果和亲手核对的方法。使用虚构或测试素材，按实际课堂条件替换占位内容。简单的手动操作保持短步骤。
7. 网站由 `site/build.py` 从 Markdown 和 README 课表生成，`docs/` 是生成物。修改课稿、课表或样式后运行 `make build && make check`；不要手改 `docs/`。保留课稿里的快捷键写法（如 `⌘C`）和课页的本节步骤、上一节/下一节导航；新增课必须同时更新 README 课表、`skills.md` 和搜索覆盖。
8. 共同练习不占课号，维护在 `course/lessons/github.md`、`course/lessons/image-gen.md` 和 `site/build.py` 的 `PRACTICES`；不要写排课地点或平台。清理课程时保留 `skills.md` 中妈妈的长期技能地图，除非本人确认再改。
9. 拾趣是独立栏目，不占课号，内容在 `course/gallery/*.md`，图片放 `assets/gallery/`；页面文案用「拾趣」，技术路径保留 `/gallery/`。公开真人姓名、单位、邮箱或原图前必须获得本人确认；`whiteboard-original.jpeg` 和赵诗雅博士的联系方式已确认公开，是明确例外。
10. 爸爸第 10–12 节的 CAD 材料只用虚构示例（`assets/lessons/10/examples/cad/`）。真实 AutoCAD 图纸、图号、位号、审图批注和转换产出留在本机私有目录，不进入仓库、截图或公开网页；审图批注只以「文件路径 + handle」引用。

本仓库直接承载爸爸妈妈的公开 HTML 教程网站。根据两人的实际进度维护各自的学习路线。学员页以 course/lessons/ 的 Markdown 为内容源，`docs/` 由构建器生成，发布内容使用可公开的素材和占位信息。编辑前读 workflow.md，涉及站点结构或语言视觉时读 website.md 和 website-style.md。网页反馈涉及内容时回写 Markdown。
