---
name: feishu-batch-send
description: 飞书批量发送文件/图片技能。支持一次发送多个文件到同一个或多个聊天，自动处理 token 刷新、错误重试、速率限制。
  包含批量发送脚本和速率控制策略。
version: 1.0.0
triggers:
  - 批量发送飞书
  - 飞书批量发送
  - feishu batch send
  - 发送多个文件到飞书
  - 飞书多发
  - 批量发文件
depends_on:
  - feishu
  - feishu-send-file
design_pattern: Pipeline
skill_type: generator
---

# 飞书批量发送技能 v1.0

> 基于 feishu-send-file 单文件发送流程，扩展为批量发送能力。
> 自动处理 token 刷新、错误重试、速率限制（5次/秒）。

## 一、核心流程

```
获取 token
  ↓
遍历文件列表
  ↓
  上传文件 → 获取 file_key
  ↓
  发送文件消息（带速率控制）
  ↓
记录结果（成功/失败/重试）
  ↓
token 即将过期？ → 是 → 刷新 token
```

## 二、批量发送脚本

保存在 `scripts/batch_send.py`，用法：

```bash
python3 scripts/batch_send.py \
  --chat-id "oc_xxxxx" \
  --files /tmp/file1.pdf /tmp/file2.docx /tmp/file3.pdf \
  --msg-type file          # file 或 image
```

## 三、速率控制

飞书限制：
- 消息发送：**5次/秒**（租户维度）
- 文件上传：**5次/秒**（应用维度）

**策略**：每次请求间隔 0.3 秒（约 3次/秒，留有安全余量）。

## 四、Token 管理

- tenant_access_token 有效期 2 小时
- 批量发送前检查 token 剩余时间
- 如果剩余 < 5 分钟，自动刷新

## 五、错误处理

| 错误 | 处理策略 |
|------|---------|
| 429 限频 | 等待 2 秒后重试，最多 3 次 |
| 99991663 token 过期 | 刷新 token 后重试 |
| 文件不存在 | 跳过并记录错误 |
| 网络超时 | 等待 3 秒后重试，最多 3 次 |

## 六、Red Flags

1. **file_type 陷阱**：通用文件必须用 `stream`，不是 `file`！
2. **图片用 image_type**：图片上传用 `/im/v1/images` + `image_type=message`
3. **文件大小限制**：单文件 ≤ 30MB（普通应用）
4. **execute_code 无环境变量**：必须用 `terminal()` 获取 FEISHU_APP_ID/SECRET
