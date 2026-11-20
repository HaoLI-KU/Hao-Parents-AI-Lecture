---
title: 审图页与批注讨论
audience: dad
status: active
summary: 把 DXF 生成可点选的审图页，按 handle 给具体实体写批注，再让 Harness 按证据逐条回应。
---
清单适合查数，不适合「看着图说话」。这一讲把一张图变成可缩放、按图层显示、点选实体、写批注的审图页；批注和实体 handle 绑定，讨论时不会脱离图纸。

### 1. 生成审图页

```sh
.venv-cad/bin/python toolkit/cad.py review dxf/<图号>.dxf -o review/<图号>.html \
  --title "<图名>"
```

- 几何用矢量 SVG 逐图层渲染，放大不糊；中文文字单独叠加，不依赖 AutoCAD 的 SHX 字体。
- 设备、仪表和标题栏文字都有编号热点，热点带 handle，能对回 DXF 实体。
- 单文件、无外部依赖，可以离线打开。

示例可以看：[sample-review.html](../../../assets/topics/cad/examples/sample-review.html)。

### 2. 打开与操作

1. 在 Harness 右侧 Files 面板打开 `review/<图号>.html`；也可以用浏览器打开同一文件。
2. 用「放大 / 缩小 / 适应窗口」和拖动查看细节。
3. 勾选左侧图层，只看设备、仪表或管线。
4. 点编号热点，看位号、名称、图层、块名和 handle。
5. 在文本框写批注，点「保存批注」。批注存在本机浏览器里，可「导出批注 JSON」或「复制批注」。

Harness 预览是受限沙箱页面，页面自带的批注可能存不住、下载也可能被拦；要长期保存就在浏览器里打开同一份 HTML。「AI 入门与基础」第 2 讲装过 HTML 批注插件（Installed plugins 里显示为 HTML Annotations 或 `dsh-annotate-sync`）时，也可以在预览里用「点选批注」浮层，以本机实际显示为准。

### 3. 批注要挂在实体上

好的批注是「点 27 号 V-101，问出口为什么没有止回阀」；不好的批注是「这里感觉不对」。每条批注尽量包含：

- 热点编号 / 位号；
- 你看到的现象；
- 你怀疑的原因或想确认的问题。

### 4. 让 Harness 按 handle 回应

把清单和导出的批注放在一起：

```text
当前工作区是 CAD-Review/。请只读 inventory/<图号>.json、review/<图号>-notes.json 和 review/<图号>.html，不要修改 original/ 和 dxf/ 里的图纸。
请按 handle 把每条批注对回实体，逐条回答：
1. 这条批注涉及哪个位号、哪条原文、在图纸的哪个位置；
2. 从清单能确认什么；
3. 从清单不能确认什么（需要看原图或做工艺判断的部分）；
4. 值得进一步讨论的两三个问题，按重要性排序。
只提讨论点，不要给工艺结论，不要改图，也不要替我决定哪一版是对的。
```

对不上 handle 的批注，把热点编号贴回会话再问一次。

### 5. 留下讨论记录

在 `review/<图号>-讨论.md` 记录：批注原文、对应 handle 或位号、从清单能确认的事实、仍需原图判断的问题、你的结论或「待定」。

`notes/` 记这张图读得对不对；`review/` 记这张图讨论出了什么，不要混写。

### 检查清单

- [ ] 至少一张图生成了审图页，能在浏览器打开。
- [ ] 缩放、平移、图层勾选都试过。
- [ ] 点热点能看到位号、图层和 handle。
- [ ] 至少写了一条批注，导出的 JSON 放进了 `review/`。
- [ ] Harness 能把每条批注对回具体 handle，且没有编造工艺结论。
- [ ] `review/<图号>-讨论.md` 记下了事实、待确认项和你的判断。

上一讲：[批量台账与跨图核对](03-batch-and-cross-check.md) · 下一讲：[修改计划与 dry-run](05-plan-and-dry-run.md)。

备查：[dsh-annotate-sync](https://github.com/chopperH0824/dsh-annotate-sync) · [工具箱说明](../../../assets/topics/cad/toolkit/README.md)
