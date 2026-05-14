# Spec/Story 飞书审阅工作流

> 当 Spec/Story 文档完成后，通过飞书发送给主人审阅，等待批准后再继续。

## 工作流

```text
文档写完成 → 调用 feishu send_message 发送审阅请求 → 等待主人回复
  → 主人回复"批准" → 继续下一阶段
  → 主人回复"驳回" → 记录原因，退回修改
```

## 飞书消息模板

发送给主人的审阅消息应包含：

```markdown
🔔 **Spec/Story 审阅请求**

**标题**: {{文档标题}}
**类型**: {{Spec / Story}}
**状态**: 待批准

**验收标准**:
1. {{AC-1}}
2. {{AC-2}}

**不做的范围**:
- {{Out of scope}}

**完整文档**: MEDIA:/path/to/{{文档路径}}

主人，请审阅后回复「批准」或「驳回+原因」喵～
```

## 关键规则

| 规则 | 说明 |
|:-----|:------|
| **必须等待回复** | 不得在未收到主人回复的情况下自行继续 |
| **超时处理** | 如果长时间未回复，每 30 分钟提醒一次，最多提醒 3 次 |
| **驳回处理** | 记录驳回原因到文档头部或 `spec-state.py reject <id> "原因"` |
| **批准信号** | 主人回复"批准"、"ok"、"可以"、"✅"、"同意" 均视为批准 |
| **文档发送** | 使用 `MEDIA:/path/to/doc.md` 发送文档文件 |

## 审阅状态对应

| 飞书记录 | SDD 状态 | 下一状态 |
|:---------|:---------|:---------|
| 已发送审阅请求 | `spec_review` / `story_review` | 等待 |
| 主人批准 | 调用 `transition` 到下一状态 | `story_create` / `qa_gate` |
| 主人驳回 | 调用 `transition` + `reject <id> "原因"` | `research` / `spec_create` |

## 实战案例

```python
# 伪代码：发送审阅请求
import json
content = {
    "msg_type": "interactive",
    "card": {
        "header": {"title": {"tag": "plain_text", "content": "🔔 Spec 审阅请求: SPEC-3-2"}},
        "elements": [
            {"tag": "markdown", "content": "**验收标准**:\n1. AC-01: upgrade 命令...\n2. AC-02: search 命令..."},
            {"tag": "markdown", "content": "主人请回复「批准」或「驳回+原因」"},
        ]
    }
}
# 通过飞书 API 发送
```
