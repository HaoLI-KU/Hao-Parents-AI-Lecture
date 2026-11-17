---
title: 初始化 Harness，装输入法和六个插件
audience: both
status: active
summary: 安装 DeepSeek Harness、配置模型、安装微信输入法，并逐项核对插件开关。
---
这一节不做网站、不编译 LaTeX，也不验证批注工作流。目标只有一个：把以后要用的 DeepSeek Harness 环境准备齐，并用安装清单逐项核对。

### 1. 安装并初始化 DeepSeek Harness

1. 打开 [DeepSeek Harness 官方发布页](https://github.com/DeepSeek-ai/deepseek-harness/releases)，在所选版本的 Assets 中找适用于 macOS Apple Silicon 的桌面安装文件，安装到「应用程序」并打开。发布页若只显示源码或找不到对应安装文件，先核对家里已安装的桌面版及其更新入口，再继续本课。
2. 沿用[第 1 讲](../ai/01-models-and-tools.md)使用的 DeepSeek 开放平台账户。在 Harness 的模型设置中配置自己的 API Key。远程上课时先停止屏幕共享，再由本人粘贴密钥；密钥不放进聊天、截图或课程仓库。
3. 打开模型选择器，确认能看到 DeepSeek 提供方和可选模型。模型、推理强度和用量统一放到第 3 讲练。

[DeepSeek Harness 模型配置说明](https://deepseek-harness.github.io/deepseek-harness/guide/providers.html) · [DeepSeek 开放平台](https://platform.deepseek.com/)

### 2. 安装微信输入法

1. 打开[微信输入法官网](https://wetype.weixin.qq.com/)，下载并安装 macOS 版。
2. 在「系统设置 → 键盘 → 文字输入」确认微信输入法已经加入输入法列表；按系统提示授予麦克风权限。
3. 找到微信输入法的语音输入快捷键并记下来。今天只确认安装和入口，不在 Harness 里口述任务，也不另外安装 Harness 的语音输入插件。

### 3. 先装插件市场

在 Harness 的插件设置中安装并启用 `dshmarket`。重开 Harness 后，确认可以进入可视化插件市场。插件入口和按钮名称以你这台电脑上的版本为准。

### 4. 安装另外五个指定插件

在插件市场按下表的界面显示名称逐项搜索和安装。每装一个就回到 Installed plugins 清单核对名称，并确认右侧开关已开启。搜索不到时记录本机版本和搜索结果，课上一起核对安装入口。

插件市场能打开后，可以在 Harness 会话中输入下面的任务。先看它实际能使用哪些插件管理工具，以及列出的已安装状态，再让它逐项继续。

```text
请帮我准备这六个 DeepSeek Harness 插件：dshmarket、HTML Annotations、Config Sync、dsh-image-gen、dsh-quote-annotate-pro、dsh-workspace-folders。
先检查 Installed plugins，按这六个显示名称列出「已安装并启用／已安装但未启用／未找到」，再告诉我当前会话能否调用安装或启用插件的工具。不要安装 dsh-ears。
如果能操作插件，请逐项安装或启用缺少的插件。每完成一项就重新查看 Installed plugins，报告显示名称和开关状态；需要我在界面确认时停下来。
如果当前会话没有安装能力，请只告诉我在插件页逐项搜索和核对的步骤，不要声称已经安装。
```

对照自己的 Installed plugins 清单核对六项。若 Harness 无法在会话中安装，就在插件页按清单逐项完成；界面显示的版本与来源以本机确认框为准。[DeepSeek Harness 插件索引说明](https://deepseek-harness.github.io/deepseek-harness/guide/plugin-market)

| Installed plugins 中的显示名称 | 以后负责什么 |
|---|---|
| HTML Annotations | 在 Harness 预览的 HTML 页面上定位并提交批注 |
| Config Sync | 导出或迁移 Harness 配置与插件设置 |
| dsh-image-gen | 以后需要时接入图像生成服务 |
| dsh-quote-annotate-pro | 在 PDF、Markdown 和代码预览中做精确划词批注 |
| dsh-workspace-folders | 给工作区增加额外的工作目录 |

不安装 `dsh-ears`。语音输入统一使用微信输入法。

### 5. 用清单收尾

- [ ] DeepSeek Harness 可以打开，模型设置里已保存自己的 DeepSeek 配置。
- [ ] 微信输入法已安装，能在菜单栏切换，并已找到语音输入入口。
- [ ] `dshmarket` 已安装并启用。
- [ ] HTML Annotations 已安装并启用。
- [ ] Config Sync 已安装并启用。
- [ ] dsh-image-gen 已安装并启用。
- [ ] dsh-quote-annotate-pro 已安装并启用。
- [ ] dsh-workspace-folders 已安装并启用。

今天不要求这些插件真正完成任务。若某个插件因版本不相容而无法启用，记下显示名称、版本和报错，其他项目继续安装。

### 妈妈清单

这一讲两人同一份清单，账户和密钥用自己的。

1. 完成 Harness 安装、模型设置和一条「连接成功」测试。
2. 安装微信输入法，找到语音输入快捷键。
3. 安装插件市场 `dshmarket` 和另外五个指定插件，逐项核对 Installed plugins 的开关。
4. 不安装 `dsh-ears`；语音输入统一用微信输入法。卡住时记下显示名称、版本和报错，下一讲继续。
