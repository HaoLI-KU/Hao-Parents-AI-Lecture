# 示例中文技术书模板

这是课程用的参考骨架，只含虚构内容，用来对照“一本中文技术书应该有哪些部分”。它不是爸爸在 Overleaf 选中的正式模板，也不替代正式项目的来源副本。

## 编译

```sh
latexmk -xelatex main.tex
```

需要：

- XeLaTeX（本机 MacTeX/TeX Live，或 Overleaf 选择 XeLaTeX）；
- `biber`：处理 `references.bib`；
- `makeindex`：处理索引；
- 字体：`ctex` 的 `fontset=fandol`，本机 TeX Live 和 Overleaf 都可复现。

如果 `latexmkrc` 没有自动跑 biber/makeindex，可手动执行：

```sh
xelatex main.tex
biber main
makeindex main
xelatex main.tex
xelatex main.tex
```

## 目录

```text
main.tex                         入口：宏包、页面、前置/正文/附录/后置
latexmkrc                        本机编译配置
references.bib                   虚构参考文献
frontmatter/                     封面、版权、前言、符号表
chapters/                        两个正文章节
figures/tikz/                    TikZ 框图与标注图
tables/                          SI 数值表、横向宽表
code/                            代码清单
appendix/                        图示速查、术语与检查表
```

## 已包含的功能

- 中文封面、版权/版本页、前言、目录、图目录、表目录、符号表；
- 前言罗马页码、正文阿拉伯页码、章首页、页眉页脚；
- 单图、子图、图注、正文引用；
- 三线表、数值 S 列、横向宽表、跨页长表；
- 编号公式、SI 数值和单位；
- TikZ 流程图、标注坐标图；
- 代码清单、提示框、定理/定义/例；
- `hyperref` 书签/元数据、`cleveref` 中文图/表/式名称；
- `biblatex`+biber 参考文献、`imakeidx` 索引、附录 A/B。

## 使用时注意

- 先编译，再逐组替换成自己的虚构示例；不要把真实 Word 正文、家庭照片或密钥放进公开仓库。
- 遇到文档类/宏包冲突时，保留功能、换实现方式，不为通过编译删章节。
- 真实项目的字体、图表样式和许可以选中模板和学校/出版社要求为准。
- 本模板的示例数据均为虚构，不能当作真实技术资料。
