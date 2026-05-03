---
name: feishu-send-file
description: 飞书发送文件的正确流程和最佳实践。通过飞书原生 API（上传→获 file_key→发送 file 消息）实现文件发送。解释为什么 send_mess...
version: 1.0.0
triggers:
- 发送文件到飞书
- 飞书上传文件
- 飞书发送 PDF
- 飞书发送图片
- feishu file upload
- 飞书 API 文件
aliases:
- /feishu-send-file
allowed-tools:
- terminal
- read_file
- write_file
metadata:
  hermes:
    tags:
    - feishu
    - file
    - upload
    - send
    - api
    category: feishu
    skill_type: library-reference
    design_pattern: tool-wrapper
    related_skills:
    - feishu
---
# 飞书发送文件指南 📁

## 一、核心结论

**❌ `send_message` 的 MEDIA 附件语法在飞书不可用。**
**✅ 必须通过飞书原生 API：上传文件 → 获取 file_key → 发送 file 消息。**

## 二、标准流程

### Step 1: 获取 tenant_access_token

```python
import os, requests, json

resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={
        "app_id": os.environ["FEISHU_APP_ID"],
        "app_secret": os.environ["FEISHU_APP_SECRET"]
    }
)
token = resp.json()["tenant_access_token"]
```

> ⚠️ 环境变量 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 必须通过 `terminal()` 访问
> （execute_code 沙箱没有环境变量）

### Step 2: 上传文件

```python
filepath = "/path/to/document.pdf"
filename = "document.pdf"
file_type = "stream"  # 通用文件类型

with open(filepath, "rb") as f:
    resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/files",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (filename, f, "application/octet-stream")},
        data={
            "file_type": file_type,
            "file_name": filename
        }
    )

result = resp.json()
file_key = result["data"]["file_key"]
print(f"Upload OK: file_key={file_key}")
```

### file_type 可选值

| 文件类型 | file_type 值 |
|:---|:---|
| 通用文件（PDF/DOCX/PPTX） | `stream` |
| 图片（JPG/PNG/GIF） | `image` |
| 音频（OPUS） | `opus` |
| 视频（MP4） | `mp4` |

### Step 3: 发送文件消息

```python
chat_id = "oc_xxxxx"  # 用目标 chat/open_id

resp = requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages",
    headers={"Authorization": f"Bearer {token}"},
    params={"receive_id_type": "chat_id"},
    json={
        "receive_id": chat_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
)
```

### 完整脚本参考
见 `~/.hermes/skills/feishu/scripts/send_file.py`

## 三、图片发送

图片不可用 MEDIA 语法，需要走图片上传 API：

```python
with open("image.jpg", "rb") as f:
    resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("image.jpg", f, "image/jpeg")},
        data={"image_type": "message"}
    )
image_key = resp.json()["data"]["image_key"]
```

## 四、常见错误

| 错误 | 原因 | 解决 |
|:---|:---|:---|
| MEDIA 语法发文件没用 | send_message 不支持飞书文件附件 | 用原生 API 上传+发送 |
| token 无效 | token 过期（2h 有效期） | 每次发文件前重新获取 |
| file_key 为空 | 文件类型/大小不对 | 检查 file_type 参数，文件不超过 30MB |
| "robot cannot send message to ..." | 机器人不在该群/用户未授权 | 检查 `receive_id` 和 `receive_id_type` |

## 五、lark-oapi SDK（可替代方案）

飞书官方 Python SDK 也可用：

```bash
pip install lark-oapi -U
```

但 Hermes 环境下 raw API 更可靠（避免 SDK 版本兼容问题）。

lark-mcp（MCP 工具）也可探索：`npm install -g lark-mcp` 后将飞书 API 暴露为 MCP 工具。
