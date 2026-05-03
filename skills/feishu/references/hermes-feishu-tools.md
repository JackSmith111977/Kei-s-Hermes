# Hermes 内置飞书工具能力说明

> Hermes Agent 框架中与飞书/Lark 相关的内置工具和适配能力。

---

## 架构概览

Hermes 通过 **Gateway 平台适配器** + **工具注册** 两层机制支持飞书操作：

```
飞书消息/事件
    ↓
Gateway (FeishuAdapter)  ← WebSocket / Webhook
    ↓
Agent 工具调用
    ↓
┌──────────────────────────────────────────┐
│ send_message (文本/图片/文件/音频/视频)   │
│ feishu_doc (文档读写)                     │
│ feishu_drive (文档评论)                   │
└──────────────────────────────────────────┘
    ↓
lark-oapi SDK → 飞书开放平台 API
```

---

## 1. Gateway 平台适配器 (`gateway/platforms/feishu.py`)

### 1.1 传输层

| 传输方式 | 依赖 | 说明 |
|---------|------|------|
| **WebSocket 长连接** | `websockets` | 默认方式，实时接收消息和事件 |
| **HTTP Webhook** | `aiohttp` | 备选方式，通过 HTTP 回调接收事件 |

### 1.2 消息接收能力

| 能力 | 说明 |
|------|------|
| 私信 (P2P) | 接收用户发给机器人的私聊消息 |
| 群聊 @mention | 接收群聊中 @机器人 的消息（需配置 mention_gating） |
| 图片消息 | 自动缓存图片到本地 |
| 文件消息 | 自动缓存文件到本地 |
| 音频/媒体消息 | 自动缓存 |
| 表情回应 (Reaction) | 路由为合成文本事件 |
| 卡片按钮点击 | 路由为合成 COMMAND 事件 |

### 1.3 消息发送能力（通过 `send_message` 工具）

| 消息类型 | 方法 | 支持格式 |
|---------|------|---------|
| **文本** | `adapter.send()` | 纯文本、Markdown（自动转换） |
| **图片** | `adapter.send_image_file()` | jpg, jpeg, png, gif, webp, bmp |
| **文件** | `adapter.send_document()` | pdf, doc, docx, xls, xlsx, ppt, pptx |
| **音频/语音** | `adapter.send_voice()` | ogg, opus, mp3, wav, m4a, aac |
| **视频** | `adapter.send_video()` | mp4, mov, avi, m4v |
| **富文本** | `adapter.send()` + post type | 飞书 post 富文本格式 |

### 1.4 Markdown 支持

飞书适配器内置 Markdown → 飞书富文本格式转换：

| Markdown 语法 | 飞书渲染 |
|--------------|---------|
| `**粗体**` | 粗体 |
| `*斜体*` | 斜体 |
| `~~删除线~~` | 删除线 |
| `[链接](url)` | 超链接 |
| `` `代码` `` | 行内代码 |
| ` ```代码块``` ` | 代码块 |
| `# 标题` | 标题 |
| `- 列表` | 无序列表 |
| `1. 列表` | 有序列表 |
| `> 引用` | 引用块 |
| `@_user_N` | @提及用户 |

### 1.5 连接参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `FEISHU_CONNECT_ATTEMPTS` | 3 | WebSocket 连接重试次数 |
| `FEISHU_SEND_ATTEMPTS` | 3 | 消息发送重试次数 |
| `_DEFAULT_TEXT_BATCH_DELAY` | 0.6s | 批量发送间隔 |
| `_DEFAULT_TEXT_BATCH_MAX` | 8条 | 每批最大消息数 |
| `_DEFAULT_TEXT_BATCH_MAX_CHARS` | 4000 | 每批最大字符数 |
| `_FEISHU_DEDUP_TTL` | 24h | 消息去重 TTL |
| `_FEISHU_REPLY_FALLBACK_CODES` | {230011, 231003} | 回复失败时转为新建消息 |

---

## 2. `send_message` 工具

### 2.1 工具签名

```python
send_message(
    target: str,       # "feishu", "feishu:#channel", "feishu:chat_id", "feishu:chat_id:thread_id"
    message: str,      # 消息文本（支持 Markdown）
)
```

### 2.2 发送文件/媒体

通过 `MEDIA:/path` 语法嵌入文件路径：

```
这是要发送的消息，附带一个文件：
MEDIA:/path/to/document.pdf
```

支持的文件类型自动识别：
- **图片**: `.jpg` `.jpeg` `.png` `.gif` `.webp` `.bmp`
- **文档**: `.pdf` `.doc` `.docx` `.xls` `.xlsx` `.ppt` `.pptx`
- **音频**: `.ogg` `.opus` `.mp3` `.wav` `.m4a` `.aac` `.flac`
- **视频**: `.mp4` `.mov` `.avi` `.m4v` `.mkv` `.webm` `.3gp` `.m4v`

### 2.3 发送到话题 (Thread)

```
target = "feishu:oc_xxx:thread_yyy"
```

### 2.4 依赖

需要安装飞书依赖：
```bash
pip install 'hermes-agent[feishu]'
# 或
pip install lark-oapi aiohttp websockets
```

---

## 3. `feishu_doc` 工具集

> 飞书云文档读写能力（需要 `lark-oapi`）

### 3.1 可用工具

| 工具名 | 功能 |
|--------|------|
| `feishu_doc_create` | 创建文档 |
| `feishu_doc_get` | 获取文档信息 |
| `feishu_doc_get_content` | 获取文档内容（Markdown） |
| `feishu_doc_get_raw_content` | 获取文档原始内容 |
| `feishu_doc_search` | 搜索文档 |
| `feishu_doc_update` | 更新文档内容 |
| `feishu_doc_delete` | 删除文档 |
| `feishu_doc_move` | 移动文档 |
| `feishu_doc_copy` | 复制文档 |
| `feishu_doc_get_meta` | 获取文档元信息 |
| `feishu_doc_create_block` | 创建内容块 |
| `feishu_doc_get_block` | 获取内容块 |
| `feishu_doc_update_block` | 更新内容块 |
| `feishu_doc_delete_block` | 删除内容块 |

### 3.2 使用示例

```python
# 创建文档
feishu_doc_create(title="我的文档", folder_token="xxx")

# 获取文档内容
feishu_doc_get_content(document_id="xxx")

# 搜索文档
feishu_doc_search(query="项目方案")
```

---

## 4. `feishu_drive` 工具集

> 飞书文档评论操作（需要 `lark-oapi`）

### 4.1 可用工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `feishu_drive_list_comments` | 列出文档评论 | file_token, file_type, is_whole, page_size, page_token |
| `feishu_drive_list_comment_replies` | 列出评论回复 | file_token, comment_id, file_type, page_size, page_token |
| `feishu_drive_reply_comment` | 回复评论 | file_token, comment_id, content, file_type |
| `feishu_drive_add_comment` | 添加全文评论 | file_token, content, file_type |

### 4.2 使用示例

```python
# 列出文档所有评论
feishu_drive_list_comments(file_token="xxx", file_type="docx")

# 回复评论
feishu_drive_reply_comment(
    file_token="xxx",
    comment_id="yyy",
    content="这是一条回复"
)

# 添加全文评论
feishu_drive_add_comment(
    file_token="xxx",
    content="这是一条新评论"
)
```

---

## 5. 事件处理

### 5.1 支持的事件类型

| 事件 | 说明 |
|------|------|
| `im.message.receive_v1` | 收到消息 |
| `im.message.message_read_v1` | 消息已读 |
| `card.action.trigger` | 卡片按钮点击 |
| `im.message.reaction.created_v1` | 添加表情回应 |
| `im.message.reaction.deleted_v1` | 删除表情回应 |

### 5.2 事件处理流程

```
飞书推送事件
    → Gateway 解析
    → EventDispatcherHandler 路由
    → 转换为 MessageEvent
    → Agent 处理
    → 回复（通过 send_message 或 adapter.send）
```

---

## 6. 配置要求

### 6.1 环境变量

| 变量名 | 说明 |
|--------|------|
| `FEISHU_APP_ID` | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 飞书应用密钥 |
| `FEISHU_VERIFICATION_TOKEN` | Webhook 验证令牌 |
| `FEISHU_ENCRYPT_KEY` | 加密密钥（可选） |
| `FEISHU_ALLOWED_USERS` | 允许的用户列表（可选，逗号分隔 open_id） |

### 6.2 config.yaml 配置

```yaml
platforms:
  feishu:
    enabled: true
    app_id: cli_xxxxxxxxxx
    app_secret: xxxxxxxxxxxxxxxx
    # WebSocket 或 Webhook 二选一
    use_websocket: true
    # webhook 配置
    webhook_host: 127.0.0.1
    webhook_port: 8765
    webhook_path: /feishu/webhook
```

---

## 7. 依赖清单

| 包名 | 用途 | 必需 |
|------|------|------|
| `lark-oapi` | 飞书 SDK | ✅ 核心功能 |
| `aiohttp` | Webhook 服务器 | ⚠️ Webhook 模式必需 |
| `websockets` | WebSocket 客户端 | ⚠️ WebSocket 模式必需 |

安装命令：
```bash
# 完整安装
pip install 'hermes-agent[feishu]'

# 最小安装（仅 lark-oapi）
pip install lark-oapi

# 开发安装
pip install 'hermes-agent[feishu,dev]'
```

---

## 8. 与飞书 API 的关系

| Hermes 工具 | 对应飞书 API | 模块 |
|------------|-------------|------|
| `send_message` → `adapter.send()` | `POST /open-apis/im/v1/messages` | im/v1 |
| `send_message` → `send_image_file()` | `POST /open-apis/im/v1/images` + `POST /open-apis/im/v1/messages` | im/v1 |
| `send_message` → `send_document()` | `POST /open-apis/im/v1/files` + `POST /open-apis/im/v1/messages` | im/v1 |
| `feishu_doc_*` | `drive/v1/docx/*` | drive/v1 |
| `feishu_drive_*` | `drive/v1/files/:token/comments/*` | drive/v1 |

> **注意**: Hermes 内置工具覆盖了飞书最核心的消息和文档操作。对于多维表格、日历、通讯录、审批、知识库、任务等模块，需要通过 `terminal` + `curl` 调用飞书 HTTP API 实现，或使用 Python 脚本调用 `lark-oapi` SDK。
