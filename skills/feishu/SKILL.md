---
name: feishu
description: 飞书全套操作技能 — 消息、云文档、多维表格、日历、通讯录、审批、知识库、电子表格、任务、事件订阅。当用户需要操作飞书任何功能时触发。
triggers:
  - "飞书"
  - "feishu"
  - "lark"
  - "发消息"
  - "创建文档"
  - "多维表格"
  - "日历"
  - "审批"
  - "知识库"
  - "电子表格"
  - "通讯录"
  - "飞书任务"
  - "群管理"
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":["python3"]},"install":[{"id":"pip","kind":"pip","package":"lark-oapi"}]}}
---

# 飞书操作技能 (Feishu Skill)

> 基于飞书开放平台 API v3/v4，覆盖消息、云文档、多维表格、日历、通讯录、审批、知识库、电子表格、任务等全套操作能力。

## 技能定位

- **类型**: 库和 API 参考 + Tool Wrapper
- **模式**: 飞书开放平台 REST API 的 Hermes 工具层封装
- **鉴权**: tenant_access_token（应用身份）+ user_access_token（用户身份）

## 核心能力速览

| 模块 | API 前缀 | 版本 | 主要能力 |
|------|---------|------|---------|
| 消息 | `/open-apis/im` | v1 | 发送/接收/更新/撤回消息、富文本、卡片、表情回应 |
| 云文档 | `/open-apis/docx` | v1 | 创建/编辑/读取文档、Block 操作、内容更新 |
| 多维表格 | `/open-apis/bitable` | v1 | 创建/查询/更新/删除记录、字段管理、视图管理 |
| 电子表格 | `/open-apis/sheets` | v3 | 创建工作表、读写数据、行列操作、公式、图表 |
| 云空间 | `/open-apis/drive` | v1 | 文件/文件夹管理、权限设置、导入导出 |
| 通讯录 | `/open-apis/contact` | v3 | 用户/部门 CRUD、搜索、权限范围 |
| 日历 | `/open-apis/calendar` | v4 | 日历/日程 CRUD、忙闲查询、会议室预定 |
| 审批 | `/open-apis/approval` | v4 | 创建/查询/审批/撤回审批流程 |
| 知识库 | `/open-apis/wiki` | v2 | 空间/节点管理、文档迁移、搜索 |
|| 任务 | `/open-apis/task` | v2 | 任务/清单/评论/自定义字段 |
|| 文件上传 | `/open-apis/im` | v1 | 上传/下载图片和文件、云空间分片上传 |
|| 事件订阅 | `/open-apis/event` | v1 | Webhook 事件订阅、回调处理 |

## 使用方式

### 1. 通过 Hermes send_message 发送飞书消息

最简单的方式，适用于文本/富文本/卡片消息：

```
send_message(
  target="feishu:oc_xxx",  # 聊天 open_id
  message="你好喵～",
)
```

支持的 target 格式：
- `feishu:oc_xxx` — 聊天（open_chat_id）
- `feishu:ou_xxx` — 用户（open_id）
- `feishu:on_xxx` — 消息回复（open_message_id）

### 2. 通过飞书原生 API 操作

当需要超出 send_message 能力的操作时（上传文件、创建文档、操作多维表格等），直接调用飞书 REST API：

```python
# 获取 tenant_access_token
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Body: {"app_id": "cli_xxx", "app_secret": "xxx"}

# 调用具体 API
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
Header: Authorization: Bearer {tenant_access_token}
```

### 3. 通过 feishu_doc / feishu_drive 工具集

 Hermes 内置了飞书专用工具集：
- `feishu_doc` — 飞书文档操作
- `feishu_drive` — 飞书云空间操作

## 详细参考

- 📖 [API 速查表](references/api-quickref.md) — 各模块核心端点、参数、频率限制
- 🔐 [认证指南](references/auth-guide.md) — token 获取、权限申请、安全最佳实践
- ❌ [错误码速查](references/error-codes.md) — 常见错误码及解决方案
- 🛠️ [Hermes 飞书工具](references/hermes-feishu-tools.md) — 内置工具能力详解

## 权限要求概览

| 权限名称 | 说明 | 类型 |
|---------|------|------|
| `im:message` | 获取与发送单聊、群组消息 | 应用 |
| `im:message:send_as_bot` | 以机器人身份发消息 | 应用 |
| `im:chat` | 获取群组信息 | 应用 |
| `drive:drive` | 云空间文件管理 | 应用 |
| `docx:document` | 读写云文档 | 应用 |
| `bitable:app` | 读写多维表格 | 应用 |
| `sheets:spreadsheet` | 读写电子表格 | 应用 |
| `calendar:calendar` | 读写日历 | 应用 |
| `approval:approval` | 审批流程管理 | 应用 |
| `wiki:wiki` | 知识库管理 | 应用 |
| `task:task` | 任务管理 | 应用 |
| `contact:user.base:readonly` | 读取用户基本信息 | 应用 |

## 频率限制

- 大部分接口: **5次/秒**（应用维度）
- 消息发送: **5次/秒**（租户维度）
- 批量接口: **50次/秒**
- 超限返回 `429` + `code: 99991400`

## 注意事项

1. **token 有效期**: tenant_access_token 有效期 2 小时，需定时刷新
2. **ID 类型**: 注意区分 open_id / user_id / union_id / open_chat_id
3. **分页**: 大部分列表接口支持 page_token 分页，单次最多 100 条
4. **Webhook**: 事件订阅需要公网可访问的回调地址
5. **文件上传**: 飞书不支持通过 send_message MEDIA 附件上传文件，需走飞书原生 API
