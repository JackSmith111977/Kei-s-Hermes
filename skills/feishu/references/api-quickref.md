# 飞书 API 速查表

> 飞书开放平台 REST API 核心端点速查。基础 URL: `https://open.feishu.cn/open-apis/`
> 所有请求 Header: `Authorization: Bearer {access_token}`, `Content-Type: application/json`

---

## 目录

1. [鉴权](#1-鉴权)
2. [消息 (im/v1)](#2-消息-imv1)
3. [云文档 (docx/v1)](#3-云文档-docxv1)
4. [电子表格 (sheets/v3)](#4-电子表格-sheetsv3)
5. [多维表格 (bitable/v1)](#5-多维表格-bitablev1)
6. [云空间 (drive/v1)](#6-云空间-drivev1)
7. [通讯录 (contact/v3)](#7-通讯录-contactv3)
8. [日历 (calendar/v4)](#8-日历-calendarv4)
9. [审批 (approval/v4)](#9-审批-approvalv4)
10. [知识库 (wiki/v2)](#10-知识库-wikiv2)
11. [任务 (task/v2)](#11-任务-taskv2)
12. [事件订阅 (event/v1)](#12-事件订阅-eventv1)

---

## 1. 鉴权

### 获取 tenant_access_token（应用身份）

```
POST /auth/v3/tenant_access_token/internal
Body: {
  "app_id": "cli_xxxxxxxxxx",
  "app_secret": "xxxxxxxxxxxxxxxx"
}
Response: { "code": 0, "tenant_access_token": "t-xxx", "expire": 7200 }
```

- 有效期 **2 小时**（7200 秒）
- 建议缓存并在过期前 5 分钟刷新
- 频率限制: 5次/秒

### 获取 user_access_token（用户身份）

需要用户授权码（authorization_code），通过 OAuth2 流程获取。适用于需要以用户身份操作的场景。

---

## 2. 消息 (im/v1)

### 发送消息

```
POST /im/v1/messages?receive_id_type={open_id|chat_id|union_id}
Body: {
  "receive_id": "ou_xxx 或 oc_xxx",
  "msg_type": "text|image|file|audio|media|sticker|interactive|share_chat|share_user|system|post",
  "content": "{\"text\":\"你好\"}",  // JSON string
  "uuid": "可选，幂等ID"
}
Response: { "code": 0, "data": { "message_id": "om_xxx", ... } }
```

**msg_type 说明：**

| 类型 | 说明 | content 格式 |
|------|------|-------------|
| `text` | 纯文本 | `{"text":"内容"}` |
| `image` | 图片 | `{"image_key":"img_xxx"}` |
| `file` | 文件 | `{"file_key":"file_xxx"}` |
| `post` | 富文本 | `{"zh_cn":{"title":"标题","content":[[{"tag":"text","text":"内容"}]]}}` |
| `interactive` | 卡片消息 | 卡片 JSON |
| `share_chat` | 群名片 | `{"chat_id":"oc_xxx"}` |
| `share_user` | 个人名片 | `{"user_id":"ou_xxx"}` |

**频率限制**: 5次/秒（租户维度），机器人单群 1000条/分钟

### 回复消息

```
POST /im/v1/messages/{message_id}/reply
Body: { "msg_type": "text", "content": "{\"text\":\"回复内容\"}", "reply_in_thread": false }
```

### 获取消息

```
GET /im/v1/messages/{message_id}
```

### 获取消息列表

```
GET /im/v1/messages?container_id_type=chat&container_id=oc_xxx&start_time=xxx&end_time=xxx&page_size=50
```

### 撤回消息

```
DELETE /im/v1/messages/{message_id}
```

### 编辑消息

```
PATCH /im/v1/messages/{message_id}
Body: { "msg_type": "text", "content": "{\"text\":\"新内容\"}" }
```

### 消息加急（催一催）

```
POST /im/v1/messages/{message_id}/urgent_app
Body: { "user_id_list": ["ou_xxx"] }
```

### 消息已读回执

```
POST /im/v1/messages/{message_id}/read_users
```

### 发送表情回应

```
POST /im/v1/messages/{message_id}/reactions
Body: { "reaction_type": { "emoji_type": "THUMBSUP" } }
```

### 删除表情回应

```
DELETE /im/v1/messages/{message_id}/reactions/{reaction_id}
```

### 获取群列表

```
GET /im/v1/chats?page_size=50&page_token=xxx
```

### 获取群信息

```
GET /im/v1/chats/{chat_id}
```

### 创建群

```
POST /im/v1/chats
Body: {
  "name": "群名称",
  "description": "群描述",
  "user_id_list": ["ou_xxx"],
  "open_ids": ["ou_xxx"],
  "i18n_names": { "zh_cn": "中文名", "en_us": "English Name" }
}
```

### 添加群成员

```
POST /im/v1/chats/{chat_id}/members
Body: { "id_list": ["ou_xxx"], "member_id_type": "open_id" }
```

### 移除群成员

```
DELETE /im/v1/chats/{chat_id}/members
Body: { "id_list": ["ou_xxx"], "member_id_type": "open_id" }
```

### 解散群

```
DELETE /im/v1/chats/{chat_id}
```

### 上传图片

```
POST /im/v1/images  (multipart/form-data)
Form: image_type=message, image=<binary>
Response: { "data": { "image_key": "img_xxx" } }
```

### 上传文件

```
POST /im/v1/files  (multipart/form-data)
Form: file_type=file|opus|mp4|doc|sheet|bitable, file_name=xxx, file=<binary>
Response: { "data": { "file_key": "file_xxx" } }
```

---

## 3. 云文档 (docx/v1)

### 创建文档

```
POST /docx/v1/documents
Body: { "title": "文档标题", "folder_token": "fldbcxxx" }
Response: { "data": { "document": { "document_id": "doccnxxx", "revision_id": 1, "title": "..." } } }
```

- 频率限制: 3次/秒
- 仅创建空文档，内容需用 Block API 写入

### 获取文档信息

```
GET /docx/v1/documents/{document_id}
```

### 获取文档纯文本内容

```
GET /docx/v1/documents/{document_id}/raw_content
```

### 获取文档所有 Block

```
GET /docx/v1/documents/{document_id}/blocks?page_size=500&page_token=xxx
```

### 获取单个 Block

```
GET /docx/v1/documents/{document_id}/blocks/{block_id}
```

### 创建 Block（批量）

```
POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
Body: {
  "children": [
    {
      "block_type": 2,  // 2=文本, 3=标题1, 4=标题2, ..., 12=无序列表, 13=有序列表, 22=图片, 25=代码块...
      "text": {
        "elements": [{ "text_run": { "content": "文本内容" } }],
        "style": {}
      }
    }
  ]
}
```

**Block 类型对照表：**

| block_type | 类型 | 说明 |
|-----------|------|------|
| 1 | page | 页面（根节点） |
| 2 | text | 文本段落 |
| 3 | heading1 | 一级标题 |
| 4 | heading2 | 二级标题 |
| 5 | heading3 | 三级标题 |
| 6 | heading4 | 四级标题 |
| 7 | heading5 | 五级标题 |
| 8 | heading6 | 六级标题 |
| 9 | heading7 | 七级标题 |
| 10 | heading8 | 八级标题 |
| 11 | heading9 | 九级标题 |
| 12 | bullet | 无序列表 |
| 13 | ordered | 有序列表 |
| 14 | code | 代码块 |
| 15 | quote | 引用 |
| 17 | todo | 待办 |
| 22 | image | 图片 |
| 23 | table | 表格 |
| 25 | code_block | 代码块（新版） |
| 27 | divider | 分割线 |
| 28 | callout | 高亮块 |
| 34 | mindnote | 思维导图 |

### 更新 Block

```
PATCH /docx/v1/documents/{document_id}/blocks/{block_id}
Body: { "text": { "elements": [{ "text_run": { "content": "新内容" } }] } }
```

### 删除 Block

```
DELETE /docx/v1/documents/{document_id}/blocks/{block_id}/children?delete_range=1
```

### 搜索文档

```
POST /suite/docs-api/search/object
Body: { "search_key": "", "count": 10, "offset": 0 }
```

### 复制文件

```
POST /drive/v1/files/{file_token}/copy
Body: { "name": "副本名称", "type": "docx", "folder_token": "fldbcxxx" }
```

---

## 4. 电子表格 (sheets/v3)

### 创建电子表格

```
POST /sheets/v3/spreadsheets
Body: { "title": "表格标题", "folder_token": "可选" }
Response: { "data": { "spreadsheet": { "spreadsheet_token": "shtcnxxx", "url": "...", "title": "..." } } }
```

### 获取电子表格信息

```
GET /sheets/v3/spreadsheets/{spreadsheet_token}
```

### 获取工作表列表

```
GET /sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query
```

### 写入数据（单范围）

```
PUT /sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}
Body: {
  "valueRange": {
    "range": "Sheet1!A1:D5",
    "values": [
      ["姓名", "年龄", "部门", "备注"],
      ["张三", 25, "研发", ""],
      ["李四", 30, "产品", ""]
    ]
  }
}
```

- range 格式: `{sheet_id}!{start_cell}:{end_cell}`
- 单次写入不超过 **5000行 × 100列**，每个格子不超过 **5万字符**

### 读取数据

```
GET /sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}
```

### 批量写入数据

```
POST /sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update
Body: {
  "valueRanges": [
    { "range": "Sheet1!A1:B2", "values": [["a","b"],["c","d"]] },
    { "range": "Sheet1!C1:D2", "values": [["e","f"],["g","h"]] }
  ]
}
```

### 追加数据

```
POST /sheets/v2/spreadsheets/{spreadsheet_token}/values_append
Body: { "valueRange": { "range": "Sheet1!A1:B2", "values": [...] } }
```

### 插入行列

```
POST /sheets/v2/spreadsheets/{spreadsheet_token}/insert_dimension_range
Body: {
  "dimension": "ROWS|COLUMNS",
  "majorDimension": "ROWS|COLUMNS",
  "sheetId": "0",
  "startIndex": 0,
  "endIndex": 2
}
```

### 删除行列

```
DELETE /sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range
```

### 更新行列（插入/删除合并）

```
PUT /sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range
```

### 写入图片

```
POST /sheets/v2/spreadsheets/{spreadsheet_token}/values_image
Body: {
  "range": "A1",
  "image": "<base64>",
  "name": "image.png"
}
```

---

## 5. 多维表格 (bitable/v1)

### 创建多维表格

```
POST /bitable/v1/apps
Body: { "name": "表格名称", "folder_token": "可选" }
Response: { "data": { "app": { "app_token": "bascnxxx", "name": "...", "url": "..." } } }
```

### 获取多维表格元数据

```
GET /bitable/v1/apps/{app_token}
```

### 获取数据表列表

```
GET /bitable/v1/apps/{app_token}/tables
```

### 创建数据表

```
POST /bitable/v1/apps/{app_token}/tables
Body: {
  "table": {
    "name": "数据表名称",
    "default_view_name": "默认视图",
    "fields": [
      { "field_name": "文本字段", "type": 1 },
      { "field_name": "数字字段", "type": 2 },
      { "field_name": "单选", "type": 3 },
      { "field_name": "多选", "type": 4 },
      { "field_name": "日期", "type": 5 },
      { "field_name": "复选框", "type": 7 },
      { "field_name": "人员", "type": 11 },
      { "field_name": "超链接", "type": 13 },
      { "field_name": "附件", "type": 17 },
      { "field_name": "关联", "type": 18 },
      { "field_name": "公式", "type": 1005 }
    ]
  }
}
```

**字段类型对照表：**

| type | 字段类型 | 说明 |
|------|---------|------|
| 1 | 文本 | 单行文本 |
| 2 | 数字 | 数字 |
| 3 | 单选 | 单选选项 |
| 4 | 多选 | 多选选项 |
| 5 | 日期 | 日期（毫秒时间戳） |
| 6 | 复选框 | 布尔值 |
| 7 | 人员 | 用户（open_id 数组） |
| 11 | 超链接 | 链接 |
| 13 | 附件 | 文件附件 |
| 17 | 关联 | 关联其他表 |
| 18 | 公式 | 公式计算 |
| 1005 | 查找引用 | 查找引用 |
| 2013 | 创建时间 | 自动记录创建时间 |
| 2014 | 创建人 | 自动记录创建人 |
| 2015 | 修改时间 | 自动记录修改时间 |
| 2016 | 修改人 | 自动记录修改人 |

### 新增记录

```
POST /bitable/v1/apps/{app_token}/tables/{table_id}/records
Body: {
  "fields": {
    "文本字段": "值",
    "数字字段": 123,
    "单选": "选项1",
    "多选": ["选项1", "选项2"],
    "日期": 1609459200000,
    "人员": [{ "id": "ou_xxx" }],
    "复选框": true,
    "超链接": { "link": "https://...", "text": "链接文字" },
    "附件": [{ "file_token": "boxcnxxx" }]
  }
}
Response: { "data": { "record": { "record_id": "recxxx", "fields": {...} } } }
```

- 单次最多 500 条

### 更新记录

```
PUT /bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
Body: { "fields": { "文本字段": "新值" } }
```

### 删除记录

```
DELETE /bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
```

### 查询记录

```
GET /bitable/v1/apps/{app_token}/tables/{table_id}/records?filter=xxx&fields=xxx&sort=xxx&page_size=100&page_token=xxx
```

**filter 格式（筛选条件）：**

```
AND(
  字段名 = "值",
  字段名 > 100,
  字段名 Contains "关键词"
)
```

支持的运算符: `=`, `!=`, `>`, `<`, `>=`, `<=`, `Contains`, `Not Contains`, `Is True`, `Is False`, `Is Null`, `Not Null`, `In`

### 批量新增记录

```
POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create
Body: { "records": [{ "fields": {...} }, { "fields": {...} }] }
```

- 单次最多 500 条

### 批量更新记录

```
POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update
Body: { "records": [{ "record_id": "recxxx", "fields": {...} }] }
```

- 单次最多 1000 条

### 批量删除记录

```
POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete
Body: { "records": ["recxxx1", "recxxx2"] }
```

### 获取字段列表

```
GET /bitable/v1/apps/{app_token}/tables/{table_id}/fields
```

### 新增字段

```
POST /bitable/v1/apps/{app_token}/tables/{table_id}/fields
Body: {
  "field_name": "新字段",
  "type": 1,
  "property": {
    "options": [{ "name": "选项1", "color": 1 }]
  }
}
```

### 更新字段

```
PUT /bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}
Body: { "field_name": "新名称", "type": 1, "property": {...} }
```

### 删除字段

```
DELETE /bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}
```

---

## 6. 云空间 (drive/v1)

### 获取文件列表

```
GET /drive/v1/files?page_size=50&page_token=xxx
```

### 获取文件夹下的文件清单

```
GET /drive/v1/files/{folder_token}/children?page_size=50
```

### 获取文件元信息

```
GET /drive/v1/files/{file_token}?type={docx|sheet|bitable|file|folder|wiki|doc|mindnote}
```

### 搜索文件

```
POST /drive/v1/files/search
Body: { "search_key": "", "count": 20, "offset": 0, "offset": 0 }
```

### 上传文件

```
POST /drive/v1/files/upload_all  (multipart/form-data)
Form: file_name=xxx, parent_type=drive|explorer, parent_node=xxx, size=xxx, checksum=xxx, file=<binary>
Response: { "data": { "file_token": "xxx", "type": "file" } }
```

- 文件大小限制: 普通文件 **20MB**
- 导入文件（转在线文档）无限制

### 下载文件

```
GET /drive/v1/files/{file_token}/download
Header: Authorization: Bearer {access_token}
```

### 创建文件夹

```
POST /drive/v1/files/create_folder
Body: { "name": "文件夹名称", "folder_token": "可选父文件夹" }
Response: { "data": { "token": "fldbcxxx", "id": "...", "type": "folder" } }
```

### 移动文件

```
POST /drive/v1/files/{file_token}/move
Body: { "type": "docx|sheet|bitable|file|folder", "target_parent_token": "fldbcxxx" }
```

### 删除文件

```
DELETE /drive/v1/files/{file_token}?type={docx|sheet|bitable|file|folder}
```

### 获取权限设置

```
GET /drive/v1/permissions/{token}/members?type={docx|sheet|bitable|file|folder}&member_type=openid|userid
```

### 添加权限

```
POST /drive/v1/permissions/{token}/members?type={docx|sheet|bitable|file|folder}&need_notification=true
Body: {
  "member_type": "openid",
  "member_id": "ou_xxx",
  "perm": "full_access|edit|comment|view"
}
```

### 更新权限

```
PATCH /drive/v1/permissions/{token}/members/{member_id}?type=xxx&member_type=openid&need_notification=true
Body: { "perm": "edit" }
```

### 删除权限

```
DELETE /drive/v1/permissions/{token}/members/{member_id}?type=xxx&member_type=openid
```

### 更新文档权限设置（公开范围）

```
PATCH /drive/v1/permissions/{token}/public?type={docx|sheet|bitable|file|folder}
Body: {
  "external_access": true,
  "security_entity": "anyone_can_view|anyone_can_edit|only_full_access",
  "comment_entity": "anyone_can_view|only_full_access",
  "share_entity": "anyone|only_full_access|same_tenant",
  "link_share_entity": "tenant_readable|tenant_editable|anyone_readable|anyone_editable|closed",
  "invite_external": true
}
```

### 创建导入任务（将本地文件转为飞书文档）

```
POST /drive/v1/import_tasks
Body: {
  "file_token": "xxx",
  "file_type": "docx|sheet|bitable",
  "point": {
    "mount_type": 1,
    "mount_key": "docx_file",
    "mount_type": 1
  }
}
Response: { "data": { "ticket": "xxx" } }
```

### 查询导入任务结果

```
GET /drive/v1/import_tasks/{ticket}
Response: { "data": { "result": { "ticket": "xxx", "type": "docx", "token": "doccnxxx", "url": "..." } } }
```

### 上传素材（图片/文件到文档）

```
POST /drive/v1/medias/upload_all  (multipart/form-data)
Form: file_name=xxx, parent_type={doc_image|doc_file|docx_image|docx_file|sheet_image|sheet_file|bitable_image|bitable_file}, parent_node=xxx, size=xxx, extra=可选, file=<binary>
Response: { "data": { "file_token": "xxx" } }
```

### 分片上传素材

```
POST /drive/v1/medias/upload_part  (multipart/form-data)
Form: upload_id=xxx, seq=0, size=xxx, checksum=xxx, file=<binary>

POST /drive/v1/medias/upload_finish
Body: { "upload_id": "xxx", "block_num": N }
```

---

## 7. 通讯录 (contact/v3)

### 获取用户信息

```
GET /contact/v3/users/{user_id}?user_id_type={open_id|user_id|union_id}&department_id_type={open_department_id|department_id}
```

响应包含: name, name_py, en_name, mobile(需权限), email, avatar, department_ids, leader_user_id, city, country, work_station, is_tenant_manager, employee_no, employee_type, gender, join_time, is_frozen 等

### 批量获取用户信息

```
GET /contact/v3/users/batch?user_ids={id1}&user_ids={id2}&user_id_type=open_id
```

- 单次最多 50 个

### 获取部门直属用户列表

```
GET /contact/v3/users/find_by_department?department_id=0&department_id_type=open_department_id&page_size=50&page_token=xxx
```

- `department_id=0` 表示根部门（需要全员通讯录权限）

### 搜索用户

```
POST /contact/v3/users/search
Body: { "search_key": "张三", "count": 20, "offset": 0, "department_id": "可选" }
```

### 创建用户

```
POST /contact/v3/users
Body: {
  "name": "张三",
  "mobile": "+86138xxxx",
  "department_ids": ["od-xxx"],
  "email": "zhangsan@example.com",
  "employee_no": "EMP001"
}
```

### 更新用户

```
PATCH /contact/v3/users/{user_id}?user_id_type=open_id
Body: { "name": "新名称", "department_ids": ["od-xxx"] }
```

### 删除用户

```
DELETE /contact/v3/users/{user_id}?user_id_type=open_id
```

### 获取部门信息

```
GET /contact/v3/departments/{department_id}?department_id_type=open_department_id&user_id_type=open_id
```

### 获取子部门列表

```
GET /contact/v3/departments/{department_id}/children?department_id_type=open_department_id&page_size=50&fetch_child=false
```

### 批量获取部门信息

```
GET /contact/v3/departments/batch?department_ids={id1}&department_ids={id2}&department_id_type=open_department_id
```

### 创建部门

```
POST /contact/v3/departments
Body: {
  "name": "研发部",
  "parent_department_id": "0",
  "department_id": "可选自定义ID",
  "leader_user_id": "ou_xxx",
  "order": 100
}
```

### 更新部门

```
PATCH /contact/v3/departments/{department_id}?department_id_type=open_department_id
Body: { "name": "新名称", "parent_department_id": "od-xxx" }
```

### 删除部门

```
DELETE /contact/v3/departments/{department_id}?department_id_type=open_department_id
```

### 搜索部门

```
POST /contact/v3/departments/search
Body: { "search_key": "研发", "count": 20, "offset": 0 }
```

---

## 8. 日历 (calendar/v4)

### 获取日历列表

```
GET /calendar/v4/calendars?page_size=50&page_token=xxx
```

### 获取日历信息

```
GET /calendar/v4/calendars/{calendar_id}
```

### 创建日历

```
POST /calendar/v4/calendars
Body: {
  "summary": "日历名称",
  "description": "描述",
  "permissions": "private|public|show_only_free_busy",
  "color": -1,
  "summary_alias": "备注名"
}
Response: { "data": { "calendar": { "calendar_id": "feishu.cn_xxx@group.calendar.feishu.cn", ... } } }
```

### 更新日历

```
PATCH /calendar/v4/calendars/{calendar_id}
Body: { "summary": "新名称", "description": "新描述" }
```

### 删除日历

```
DELETE /calendar/v4/calendars/{calendar_id}
```

### 搜索日历

```
POST /calendar/v4/calendars/search
Body: { "query": "关键词", "page_size": 20, "page_token": "xxx" }
```

### 创建日程

```
POST /calendar/v4/calendars/{calendar_id}/events
Body: {
  "summary": "日程标题",
  "description": "描述",
  "start_time": { "timestamp": "1609459200", "timezone": "Asia/Shanghai" },
  "end_time": { "timestamp": "1609462800", "timezone": "Asia/Shanghai" },
  "need_notification": true,
  "reminders": [{ "minutes": 15 }],
  "recurrence": "FREQ=DAILY;INTERVAL=1;COUNT=5",
  "location": { "name": "会议室", "address": "地址" },
  "attendees": [{ "type": "user", "is_optional": false, "user_id": "ou_xxx" }],
  "vchat": { "vc_type": "feishu", "icon_type": "vc" },
  "visibility": "default|public|private"
}
```

- `start_time` / `end_time` 支持 `timestamp`（秒级）或 `date`（全天事件，格式 `2024-01-01`）
- `recurrence` 遵循 RFC 5545 标准

### 获取日程

```
GET /calendar/v4/calendars/{calendar_id}/events/{event_id}
```

### 获取日程列表

```
GET /calendar/v4/calendars/{calendar_id}/events?start_time=xxx&end_time=xxx&page_size=50
```

### 更新日程

```
PATCH /calendar/v4/calendars/{calendar_id}/events/{event_id}
Body: { "summary": "新标题", "start_time": {...}, "end_time": {...} }
```

### 删除日程

```
DELETE /calendar/v4/calendars/{calendar_id}/events/{event_id}
```

### 搜索日程

```
POST /calendar/v4/calendars/{calendar_id}/events/search
Body: { "query": "关键词", "filter": { "start_time": {...}, "end_time": {...} } }
```

### 查询忙闲状态

```
POST /calendar/v4/freebusy/query
Body: {
  "time_min": "2024-01-01T00:00:00+08:00",
  "time_max": "2024-01-07T23:59:59+08:00",
  "user_id_list": ["ou_xxx"],
  "room_id_list": ["xxx"],
  "include_external_calendar": true
}
```

### 添加日程参与人

```
POST /calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees
Body: {
  "attendees": [
    { "type": "user", "is_optional": false, "user_id": "ou_xxx" }
  ],
  "need_notification": true
}
```

### 删除日程参与人

```
DELETE /calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees/{attendee_id}
```

### 订阅日历变更事件

```
POST /calendar/v4/calendars/{calendar_id}/subscribe
```

- 需要 `user_access_token`

### 取消订阅

```
POST /calendar/v4/calendars/{calendar_id}/unsubscribe
```

---

## 9. 审批 (approval/v4)

### 获取审批定义列表

```
GET /approval/v4/approvals?page_size=100&page_token=xxx
```

### 获取审批定义详情

```
GET /approval/v4/approvals/{approval_code}
```

### 创建审批实例

```
POST /approval/v4/instances
Body: {
  "approval_code": "xxx",
  "form": [
    { "id": "field_id", "type": "input", "value": "审批内容" }
  ],
  "user_id": "ou_xxx",
  "open_id": "ou_xxx",
  "department_id": "od-xxx",
  "node_approver_user_ids": { "node_id_or_node_key": ["ou_xxx"] },
  "uuid": "可选，幂等ID"
}
```

### 获取审批实例详情

```
GET /approval/v4/instances/{instance_id}
```

### 获取审批实例列表

```
GET /approval/v4/instances?approval_code=xxx&start=xxx&end=xxx&page_size=100&status=PENDING|APPROVED|REJECTED|WITHDRAWN|CANCELLED|DELETED
```

### 审批（同意/拒绝/转办）

```
POST /approval/v4/tasks/approve
Body: {
  "approval_code": "xxx",
  "instance_code": "xxx",
  "user_id": "ou_xxx",
  "task_id": "xxx",
  "comment": "审批意见"
}

POST /approval/v4/tasks/reject
Body: { "approval_code": "xxx", "instance_code": "xxx", "user_id": "ou_xxx", "task_id": "xxx", "comment": "拒绝原因" }

POST /approval/v4/tasks/transfer
Body: { "approval_code": "xxx", "instance_code": "xxx", "user_id": "ou_xxx", "task_id": "xxx", "transfer_user_id": "ou_xxx", "comment": "转办原因" }
```

### 撤回审批

```
POST /approval/v4/instances/cancel
Body: {
  "approval_code": "xxx",
  "instance_code": "xxx",
  "user_id": "ou_xxx"
}
```

### 订阅审批事件

需要在开发者后台配置事件回调地址，订阅 `approval_task` 相关事件。

---

## 10. 知识库 (wiki/v2)

### 获取知识空间列表

```
GET /wiki/v2/spaces
```

### 获取知识空间信息

```
GET /wiki/v2/spaces/{space_id}
```

### 创建知识空间

```
POST /wiki/v2/spaces
Body: { "name": "空间名称", "description": "描述" }
```

### 获取节点信息

```
GET /wiki/v2/spaces/get_node?token={node_token 或 obj_token}&obj_type={doc|docx|sheet|bitable}
```

### 获取子节点列表

```
GET /wiki/v2/spaces/{space_id}/nodes?page_size=50&page_token=xxx&parent_node_token=可选
```

### 创建节点

```
POST /wiki/v2/spaces/{space_id}/nodes
Body: {
  "obj_type": "doc|docx|sheet|bitable|file|folder",
  "parent_node_token": "可选",
  "node_type": "origin|shortcut",
  "origin_node_token": "shortcut 时必填",
  "origin_space_id": "shortcut 时必填",
  "title": "节点标题"
}
```

- 节点数上限: 40万/空间
- 目录树深度: 50层
- 单层节点数: 2000

### 移动节点

```
POST /wiki/v2/spaces/{space_id}/nodes/{node_token}/move
Body: {
  "target_parent_token": "可选，不传则移到空间根目录",
  "target_space_id": "可选，不传则移到同空间"
}
```

### 删除节点

```
DELETE /wiki/v2/spaces/{space_id}/nodes/{node_token}
```

### 添加知识空间成员

```
POST /wiki/v2/spaces/{space_id}/members
Body: {
  "member_type": "openid|userid|unionid|email|openchat|opendepartmentid",
  "member_id": "ou_xxx",
  "perm": "full_access|edit|comment|view"
}
```

### 删除知识空间成员

```
DELETE /wiki/v2/spaces/{space_id}/members/{member_id}?member_type=openid
```

### 更新知识空间设置

```
PUT /wiki/v2/spaces/{space_id}/setting
Body: {
  "create_setting": { "member_type": "admin|member", "perm": "full_access|edit|comment|view" },
  "edit_setting": { "member_type": "admin|member", "perm": "full_access|edit|comment|view" },
  "comment_setting": { "member_type": "admin|member", "perm": "full_access|edit|comment|view" },
  "share_setting": { "member_type": "admin|member", "perm": "full_access|edit|comment|view" }
}
```

### 搜索知识库内容

```
POST /suite/wiki/search/object
Body: { "search_key": "", "count": 10, "offset": 0, "offset": 0 }
```

### 将云文档移入知识库

```
POST /wiki/v2/spaces/{space_id}/nodes/move_docs_to_wiki
Body: {
  "obj_token": "doccnxxx",
  "obj_type": "docx",
  "apply": false
}
```

---

## 11. 任务 (task/v2)

> 注意：v1 版本已废弃，请使用 v2

### 创建任务

```
POST /task/v2/tasks
Body: {
  "summary": "任务标题",
  "description": "任务描述（最多3000字符）",
  "due": { "timestamp": "1675742789470", "is_all_day": false },
  "start": { "timestamp": "1675742789470", "is_all_day": false },
  "members": [
    { "id": "ou_xxx", "role": "assignee|follower" }
  ],
  "repeat_rule": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR",
  "completed_at": 0,
  "extra": "自定义数据"
}
```

### 获取任务详情

```
GET /task/v2/tasks/{task_guid}
```

### 更新任务

```
PATCH /task/v2/tasks/{task_guid}
Body: { "summary": "新标题", "description": "新描述" }
```

### 删除任务

```
DELETE /task/v2/tasks/{task_guid}
```

### 完成任务

```
PATCH /task/v2/tasks/{task_guid}
Body: { "completed_at": 1675742789470 }
```

### 获取任务列表

```
GET /task/v2/tasks?page_size=50&page_token=xxx&completed=false&type=my_tasks
```

### 创建清单（Tasklist）

```
POST /task/v2/tasklists
Body: { "name": "清单名称" }
```

### 获取清单详情

```
GET /task/v2/tasklists/{tasklist_guid}
```

### 获取清单任务列表

```
GET /task/v2/tasklists/{tasklist_guid}/tasks?page_size=50&completed=false
```

### 添加任务到清单

```
POST /task/v2/tasklists/{tasklist_guid}/activity_subscriptions
Body: { "activity_type": "task_update", "action_type": "update" }
```

### 创建评论

```
POST /task/v2/tasks/{task_guid}/comments
Body: { "content": "评论内容", "reply_to_comment_id": "可选" }
```

### 获取评论列表

```
GET /task/v2/tasks/{task_guid}/comments?page_size=50
```

### 添加自定义字段

```
POST /task/v2/tasks/{task_guid}/custom_fields
Body: {
  "custom_field_guid": "xxx",
  "number_value": 100,
  "member_value": [{ "id": "ou_xxx" }],
  "datetime_value": 1675742789470,
  "select_value": "选项ID",
  "text_value": "文本"
}
```

### 上传任务附件

```
POST /task/v2/tasks/{task_guid}/attachments
  (multipart/form-data)
Form: file_name=xxx, file=<binary>
```

---

## 12. 事件订阅 (event/v1)

飞书通过 Webhook 推送事件通知。需要在开发者后台配置回调地址。

### 事件类型（常用）

| 事件 | event_type | 说明 |
|------|-----------|------|
| 消息接收 | `im.message.receive_v1` | 收到新消息 |
| 审批任务 | `approval_task.approval_task` | 审批任务状态变更 |
| 日历事件 | `calendar.calendar.event.changed_v1` | 日程变更 |
| 通讯录变更 | `contact.user.created_v1` | 用户创建 |
| 文档权限变更 | `drive.file.permission_member_added_v1` | 文档权限变更 |
| 知识库节点变更 | `wiki.node.updated_v1` | 知识库节点更新 |

### 事件回调数据结构

```json
{
  "schema": "2.0",
  "header": {
    "event_id": "xxx",
    "event_type": "im.message.receive_v1",
    "create_time": "1234567890",
    "token": "xxx",
    "app_id": "cli_xxx",
    "tenant_key": "xxx"
  },
  "event": {
    "sender": { "sender_id": { "open_id": "ou_xxx" } },
    "message": { "message_id": "om_xxx", "chat_type": "p2p|group", "msg_type": "text", "content": "{\"text\":\"...\"}" }
  }
}
```

### URL 验证（首次配置时）

飞书会发送 URL 验证请求，需原样返回 challenge：

```
POST {你的回调地址}
Body: { "challenge": "xxx", "token": "xxx", "type": "url_verification" }
Response: { "challenge": "xxx" }
```

---

## 附录 A: ID 类型对照

| ID 类型 | 前缀 | 说明 | 示例 |
|---------|------|------|------|
| open_id | `ou_` | 用户在应用内的身份 | `ou_7dab8a3d3cdcc9da365777c7ad535d62` |
| user_id | - | 用户在租户内的身份（仅自建应用） | `on_xxx` |
| union_id | - | 用户在应用开发商下的身份 | `on_xxx` |
| open_chat_id | `oc_` | 群聊 ID | `oc_993a2cc55f4b32d4a8164a0d4566c37f` |
| open_message_id | `om_` | 消息 ID | `om_xxx` |
| open_department_id | `od_` | 部门 ID | `od-xxxxxxxxxxxxx` |
| department_id | - | 自定义部门 ID | `D067` |
| app_id | `cli_` | 应用 ID | `cli_xxxxxxxxxx` |

## 附录 B: HTTP 错误码速查

| HTTP 状态码 | code | 说明 |
|------------|------|------|
| 400 | 99991400 | 请求频率超限，需要降速 |
| 400 | 99991663 | tenant_access_token 无效或过期 |
| 400 | 99991664 | user_access_token 无效或过期 |
| 400 | 99991665 | app_id 或 app_secret 无效 |
| 400 | 99991668 | 请求体格式错误 |
| 403 | 99991671 | 应用无权限 |
| 404 | 99991672 | 资源不存在 |
| 429 | 99991400 | 接口限频 |
| 500 | 99991660 | 服务内部错误 |
| 200 | 0 | 成功 |

## 13. 文件上传 (im/v1 + drive/v1)

### 上传图片

```
POST /open-apis/im/v1/images
Body: { "image_type": "message" }
Header: Content-Type: multipart/form-data
Form: file=<图片文件>
Response: { "code": 0, "data": { "image_key": "img_xxx" } }
```

- 图片上限: **10MB**
- 支持格式: jpg, png, gif, webp, bmp

### 上传文件

```
POST /open-apis/im/v1/files
Body: { "file_type": "pdf", "file_name": "xxx.pdf" }
Header: Content-Type: multipart/form-data
Form: file=<文件>
Response: { "code": 0, "data": { "file_key": "file_xxx" } }
```

- 文件上限: **50MB** (普通应用) / **200MB** (大型应用)
- 支持格式: pdf, doc, docx, xls, xlsx, ppt, pptx, mp4 等

### 上传云空间文件

```
POST /open-apis/drive/v1/files/upload_prepare    // 准备上传
POST /open-apis/drive/v1/files/upload_part       // 分片上传
POST /open-apis/drive/v1/files/upload_finish     // 完成上传
```

### 下载文件

```
GET /open-apis/im/v1/messages/:message_id/resources/:file_key?type=file
GET /open-apis/im/v1/images/:image_key
Header: Authorization: Bearer {token}
Response: 二进制流
```

---

## 附录 C: 频率限制速查

| 接口类别 | 限制 | 维度 |
|---------|------|------|
| 消息发送 | 5次/秒 | 租户 |
| 消息发送 | 1000条/分钟 | 单群 |
| 批量操作 | 50次/秒 | 应用 |
| 大部分接口 | 5次/秒 | 应用 |
| tenant_access_token 获取 | 5次/秒 | 应用 |
| 导入任务 | 1次/秒 | 应用 |
| 云文档读写 | 3次/秒 | 应用 |
