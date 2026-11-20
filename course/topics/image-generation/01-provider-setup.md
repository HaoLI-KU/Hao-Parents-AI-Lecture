---
title: 配置 Seedream 和 dsh-image-gen
audience: both
status: active
summary: 开通火山方舟、安装 dsh-image-gen，配置 Provider 并生成一张测试图。
---
这一讲只做一件事：把「用 DeepSeek Harness 生成图片」的链路配置好，并用一张简单测试图确认真的跑通。软装客厅和改图放在下一讲。

公开课稿只用虚构内容和示例文字；真实家庭照片、门牌、快递单和家人物品只在本机使用。

### 1. 先分清四个名字

| 名称 | 是什么 | 这一课怎么用 |
|---|---|---|
| **Seedream / SeeDream** | 字节跳动 Seed 团队的图像生成模型，支持文生图、参考图生图、局部编辑、组图 | 本课要调用的模型 |
| **即梦 AI** | 消费端网页/App，使用 Seedream；会员/订阅是消费级入口 | 可以自己玩，但**不能**直接给 DSH 插件当 API |
| **火山方舟 Ark** | 火山引擎的模型 API 平台：开通模型、创建 API Key、按量计费 | 本课必须走这条 |
| **dsh-image-gen** | DeepSeek Harness 的生图插件，支持 Seedream / 火山方舟 Provider | 本课安装和配置的插件 |

**关于“订阅”**：即梦会员和火山方舟 API 是两条账本。DSH 插件要的是 Ark API Key，按生成张数计费；不需要先买即梦会员。火山引擎的 Agent Plan 是另一种订阅套餐，可能含部分 Seedream Lite 额度，但先确认它是否提供可用于 `/api/v3` 的 API Key，不要把它当成图片余额。若只想在网页里随手生成，才考虑即梦会员。

### 2. 开通火山方舟和 Seedream

1. 打开[火山方舟控制台](https://console.volcengine.com/ark/region:cn-beijing)，用爸爸妈妈自己的火山引擎账号登录，按页面要求完成实名认证和开通。
2. 在模型广场或「开通管理」里找到 **Seedream**，开通要用的版本。课堂先用 **Seedream 5.0 Lite** 或 **5.0 Pro** 试，确认流程后再用 5.5 或更高分辨率。
3. 打开 [API Key 管理](https://console.volcengine.com/ark/region:cn-beijing/apiKey)，创建一把只给这台 Mac 用的 Key，命名例如 `dsh-image-gen-dad` 或 `dsh-image-gen-mom`。先停止屏幕共享，由本人复制；Key 不写进聊天、截图或课程仓库。
4. 回到控制台确认计费方式和余额。API 是按量后付费；先在预算里留一小笔练习额度，开启用量/余额提醒。
5. 记下区域和端点。图片生成默认端点是 `https://ark.cn-beijing.volces.com/api/v3`；实际以控制台和插件“拉取模型”结果为准。

当前常见模型 ID（以控制台/插件拉取结果为准）：

- `doubao-seedream-5-5-261028`：Seedream 5.5，2026-11-09 发布，API 陆续开放；
- `doubao-seedream-5-0-pro-260628`：Seedream 5.0 Pro，插件当前默认之一；
- `doubao-seedream-5-0-260128` / `doubao-seedream-5-0-lite-260128`：Seedream 5.0 Lite。

价格示例（2026-11-15 查到的官方口径，实际以下单页面为准）：Seedream 5.0 Pro 输出图不超过 236 万像素约 0.3 元/张，更大尺寸约 0.6 元/张；5.5 约 0.28 元/2K 方图编辑；Lite 更便宜。先用 Lite/1K 试构图，满意后用 Pro/5.5/2K。

### 3. 安装并启用 dsh-image-gen

1. 打开 DeepSeek Harness 左侧的「插件」面板，进入「已安装」或插件市场，搜索 `dsh-image-gen`。
2. 安装或启用后重启 Harness。插件详情页应出现「图像生成」配置表单；输入框旁也会出现生图按钮。
3. 不要照搬插件 README 里的 `--profile web` 命令到 Desktop；父母用界面安装即可。若界面找不到，先确认 Harness 版本，再让家人协助用插件管理。
4. 安装只需一次；以后升级插件后重新打开详情页检查 Provider 和模型是否还在。

### 4. 配置 Seedream Provider

在插件详情页：

1. 默认 Provider 选 **ByteDance Seedream / 火山方舟**（界面可能显示「字节 Seedream」）。
2. 填入第 2 步创建的 API Key。
3. Endpoint / Base URL 保持默认；若为空，填 `https://ark.cn-beijing.volces.com/api/v3`。
4. 模型先填 `doubao-seedream-5-0-pro-260628`，或点「拉取模型」后选可用的 5.5 / 5.0 Lite。
5. 点「测试连接」。通过后再点「拉取模型」核对模型列表；失败先看第 8 步的排错。
6. 设置输出格式（PNG/JPEG）、水印开关和保存工作区。水印是否可关以模型和条款为准；课堂先用默认。
7. 保存后，回到会话输入框旁确认 Provider 是 Seedream，不要误用 ChatGPT 订阅通道。

密钥只保存在本机 DSH 凭据里；不要为了“方便”把 Key 写进课稿、仓库、聊天或截图。

### 5. 生成一张测试图

配置完成后，先不要做软装效果图。用一张最简单的图验证链路：白纸上一个红苹果，不包含文字和复杂背景。

```text
请生成一张极简产品图：纯白纸面上放一个红苹果，柔和自然光，正面略俯视，1:1，不要文字、不要品牌、不要其他物体。
```

看到图片后确认：请求没有报错、图片能在图库或工作区打开、能说出这次使用的模型和大约费用。这张测试图只用于验收，不放进课程页面。

### 6. 费用、隐私和故障排查

**费用**

- 按生成张数计费；先 Lite/1K 试构图，再用 Pro/5.5/2K 做最终图。
- 在火山方舟控制台看用量、余额和账单；设预算提醒，避免一次批量生成过多。
- 5.0 Pro 输出图 ≤236 万像素约 0.3 元/张，更大尺寸约 0.6 元/张；5.5 约 0.28 元/2K 编辑；以控制台为准。

**隐私**

- API Key 不截图、不进聊天、不进仓库；只放本机 DSH 凭据。
- 真实家庭照片不上传公开仓库；按火山方舟条款处理图片。
- 课堂投屏时先停共享再粘贴 Key。

**排错**

| 现象 | 先检查 |
|---|---|
| 401/403 | Key 是否复制完整；模型是否开通；账号是否欠费；实名/区域是否符合 |
| 404 模型不存在 | 模型 ID 是否过期；点「拉取模型」选当前 ID；5.5 是否已对该账号开放 |
| 429 | 触发限流；等一会儿，减少并发/批量 |
| 测试连接失败 | Endpoint 是否 `/api/v3`；Key 是否属于当前区域；网络是否可访问火山方舟 |
| 生成成功但看不到图 | 图库/工作区保存位置；Provider 是否选对；刷新或重开插件 |
| 中文小字乱码 | 减少画面文字；重要文字后期另加，不依赖模型写小字 |
| 改图改得太多 | 提示词写“只改…、保留…”，用选区圈定；降低一次修改数量 |

### 7. 验收清单

- [ ] 能直接说出 Seedream / SeeDream 是官方模型名称。
- [ ] 火山方舟账号已开通 Seedream，API Key 只保存在本机。
- [ ] dsh-image-gen 已安装并启用，Provider 选 ByteDance Seedream / 火山方舟。
- [ ] 「测试连接」通过，「拉取模型」能看到可用模型。
- [ ] 生成一张简单测试图，能说出模型、尺寸和大约费用。
- [ ] 知道 Key、真实照片和费用记录的边界。

#### 备查

- [Seedream 5.5 教程](https://docs.volcengine.com/docs/ark/seedream-5-5?lang=zh)
- [Seedream 5.0 Pro 教程](https://docs.volcengine.com/docs/ark/seedream-5-0-pro?lang=zh)
- [图片生成教程](https://docs.volcengine.com/docs/ark/image-generation-tutorial?lang=zh)
- [模型价格](https://docs.volcengine.com/docs/ark/model-pricing?lang=zh)
- [API Key 管理](https://console.volcengine.com/ark/region:cn-beijing/apiKey)
- [dsh-image-gen 插件](https://github.com/shanliuling/dsh-image-gen)
