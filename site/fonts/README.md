# 自托管字体

课程站点只用两个拉丁字体，中文回落到 macOS 的宋体和苹方。

| 文件 | 字体 | 来源 | 许可 |
|---|---|---|---|
| `inter.woff2` | Inter（可变字重） | [Google Fonts](https://fonts.google.com/specimen/Inter) | SIL Open Font License 1.1 |
| `source-serif-4.woff2` | Source Serif 4（可变字重） | [Google Fonts](https://fonts.google.com/specimen/Source+Serif+4) | SIL Open Font License 1.1 |

`site/build.py` 会把这个目录复制到 `docs/assets/fonts/`。字体只含拉丁字符，中文使用系统字体；页面不会在运行时请求 Google Fonts，避免课堂网络不稳定时卡住。

更新字体时保留文件名，或同时修改 `site/style.css` 的 `@font-face` 路径。
