# CAD-Work 项目规则

这是 `~/CAD-Work/` 工作区的项目指令。Harness 在这个目录打开会话时先读这份文件。

## 工具与目录

- 工具：`~/CAD-Work/tools/cad`，它已经设置 `CADCRAFT_CONFIG_DIR="$HOME/CAD-Work/config"`。
- `originals/`：图纸原件副本，**只读，绝不修改或覆盖**。
- `work/`：所有修改、另存和中间副本。
- `preview/`：PNG/PDF 预览。
- `notes/`：读图记录、台账、核对结果。

## 工作方式

1. 先读，再问，再改。读图用 `tools/cad info`、`tools/cad run ... --cmd 'texts {...}'`、`drawing.inspect`。
2. 每个结论都要能指回 handle、图层或原文。文件里没有的写「无法从文件确认」，不要补猜。
3. 任何修改先给计划：要改的 handle、当前值、目标值、将运行的命令、保真门槛步骤。等我说「执行」再动手。
4. 改图前先对 `work/` 副本跑一次 `roundtrip --same-format`；geometry、objects、table records 或 layouts 有丢失就停止，只做只读分析。
5. 修改只写 `work/` 的新文件，用 `saveas` 指定 `version:2018`；不要用 `--in-place`，不要写 `originals/`。
6. 改完重读输出：`info` 对实体数，`texts` 对新值，`drawing.inspect` 对 handle/图层/位置；导出修改前后 PNG；核对原件 sha256。
7. 删除、移动、整层改名等破坏性操作，先确认对象和范围。
8. 报告实际运行的命令、关键 JSON 结果和 handle；不要粘贴整份大 JSON。

## 隐私与边界

- 真实图纸、图号、位号、截图和修改记录只留在本机 `~/CAD-Work/`，不写进课程仓库，也不上传到公开网页。
- 不操作用户界面，不向 AutoCAD 键入命令，不做 GUI 自动化。
- 工具失败时报告工作区路径、命令和报错；不要猜文件位置，也不要假装已经执行。
