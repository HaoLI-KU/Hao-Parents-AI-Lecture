# 可公开的课程素材

按专题放在 `topics/<slug>/` 下，继续使用三个目录：

- `screenshots/`：真实界面截图、实际结果截图；
- `illustrations/`：SVG、概念图、ChatGPT 生成示意图；
- `examples/`：DXF、ZIP、PDF、代码等非图片练习文件。

图片按 `NN-短描述.扩展名` 命名，例如 `01-remote-meeting.png`；一讲多图用 `NN-短描述-2`。课稿里用 `figure` 引用，图片必须有替代文字和一句图注。截图里的账号、通知、姓名、门牌和私人文件必须裁掉；真实家庭资料、CAD 图纸和账号资料留在本机，不进入这个仓库。不新增 `images/` 或更深的图片目录。

中文技术书参考模板在 `topics/word-to-latex/examples/chinese-book-template/`，ZIP 和预览 PDF 也放在同一层。真实家庭和工作资料留在仓库外；发布目录只复制页面实际引用的素材。

CAD 材料在 `topics/cad/`：`toolkit/` 是代码流工具箱（读取、修改计划、重读校验、审图页），`examples/` 是**虚构**的「糖浆配制」示例 DXF、示例计划、修改报告和审图页。真实 AutoCAD 图纸、图号、位号和审图批注一律留在本机私有目录，不进入这个仓库。

首页 Hero 的线稿水印来自本人提供的白板画，整理版是 `assets/site/whiteboard-lineart.svg`，只保留人物线稿和阴阳符号；透明度、尺寸和响应式用法见 `website-style.md`。

拾趣的公开图片放在 `gallery/`：

- `gallery/whiteboard-original.jpeg`：赵诗雅博士在办公室白板上的原图，已经本人确认公开；保留白板边框、照片、磁铁、姓名、日期和手写文字。
- 对应的整理版线稿在 `site/whiteboard-lineart.svg`，由 ChatGPT 生成；页面 caption 和作品信息要分别署名，不把线稿归为赵诗雅博士手绘。
- `gallery/whiteboard-peek.jpg`：从原图裁出的脸部缩略角，只用于后卡露出的 `peek_image`，不替代完整原图。
- `gallery/` 下的图片由构建器复制到 `docs/assets/gallery/`，供 `/gallery/` 页面使用。
- 新增展品涉及真人、姓名或邮箱时，先确认再发布；其他私人素材仍留在仓库外的本地私有目录，不进入仓库。
