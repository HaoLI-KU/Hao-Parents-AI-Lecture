---
title: 会议预约、语音输入与 MacTeX
audience: mom
status: active
summary: 预定会议并同步日历、试微信语音转文字，用 TeXShop 验证中文排版环境。
---
先补前几节没完成、今天会用到的项目。腾讯会议、微信和 Apple 账户能打开后，再做下面的练习。

### 预定会议并同步日历

1. 在腾讯会议 Mac 客户端主页点「预定会议」，填主题和时间，再点「预定」。从会议详情或邀请菜单复制会议号和链接。把日期、时区与链接通过邮件发给约好的家人，请对方核对在哥本哈根看到的时间。
2. 在苹果「日历」建立测试日程，用日程右上角的彩色标记选一个自己可编辑的共享日历。双击日程，在「添加备注、URL 或附件」贴入会议链接。需要指定时区时，在「日历 → 设置 → 高级」打开时区支持，再点日程日期选择上海时区。请家人在哥本哈根用自己的设备核对当地开始时间，并打开链接确认是同一场会议。 [Apple 添加和修改日程](https://support.apple.com/zh-hans/guide/calendar/icalwr13-events/mac)
### 试微信语音转文字

优先练微信 Mac 客户端自带的语音转文字。打开一个测试聊天，把光标放在输入框，找语音输入的小话筒或客户端显示的快捷键。试说「明天给薄荷浇水，check the leaves」。确认中英文出现在可编辑的输入框，核对后清空。入口以现场客户端版本为准。如果只有发送语音消息的按钮，先请家人一起检查版本和设置。macOS 听写作为备用，可在「系统设置 → 键盘 → 听写」查看启用方式和快捷键。

### 验证 MacTeX

本节只用 Mac 上已经装好的 TeXShop，不需要 DeepSeek Harness。

1. 下载[中文手册练习项目（ZIP）](../../../assets/topics/word-to-latex/examples/chinese-manual.zip)和[测试文件](../../../assets/topics/word-to-latex/examples/mom-mactex-test.tex)。把 ZIP 解压到「文稿」，测试文件也放到同一个「文稿」位置。
2. 双击测试文件，TeXShop 会打开它。点工具栏的「排版」（Typeset），等预览窗口出现。若能看到「MacTeX 练习」和下面那行中文，说明中文编译环境可用。
3. 在 TeXShop 里打开解压后的 `chinese-manual/main.tex`。文件第一行指定 XeLaTeX，按「排版」编译；第一次目录可能为空，再按一次「排版」更新目录。
4. 在预览里核对封面、目录，以及「准备设备」「记录与复查」两个中文章节。看到本次生成的 PDF 就完成本节验证；妈妈本节不做 PDF 批注。
5. 若排版报错，先看 TeXShop 日志窗口的第一条错误，记下文件名和提示。确认 MacTeX 已安装、TeXShop 是从「应用程序」打开的；修不了就记下错误，下节课一起看。

如仍有待完成的基础操作，记下从哪一步接着做。豆包桌面版继续按需使用。工具选择与提示词的系统练习留到第 5、6 节。

备查：[腾讯会议预定常规会议](https://meeting.tencent.com/support/topic/392/index.html) · [Apple 听写设置](https://support.apple.com/zh-cn/guide/mac-help/-kbdm162/mac) · [MacTeX 图形工具](https://www.tug.org/mactex/gui-link.html)
