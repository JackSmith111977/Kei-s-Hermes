# Choice 交互卡片实现记录

> 知行记录 — 在飞书适配器中新增 `<!-- card:choice -->` 交互卡片类型的过程与经验

## 背景

需要让 boku 在飞书上能向主人展示可点击的选择按钮，而不是纯文本列表。

## 实现方案

### 1. 新增卡片构建函数

`gateway/platforms/feishu.py` → `_build_choice_card_payload(content: str) -> dict`

- 解析 `<!-- card:choice -->` 标记后的文本
- 识别编号列表（`1. xxx`）作为按钮选项
- 最多 5 个按钮，第一个为 primary 样式，其余为 default
- 按钮 value 携带 `choice`（序号）和 `label`（完整文本）
- 底部显示提示「💡 点击上方按钮选择，或直接输入文字回复」

### 2. 注册到路由

在 `_build_outbound_payload()` 中新增 elif 分支：

```python
elif card_type == "choice":
    card = _build_choice_card_payload(body)
    return "interactive", json.dumps(card, ensure_ascii=False)
```

### 3. 修复回调消息格式

`_handle_card_action_event()` 原本产生 `/card button {...}` 格式（COMMAND 类型），导致 LLM 无法理解。修改为：

```python
# 从 action_value 提取 label，生成自然语言文本
if label:
    synthetic_text = f"📋 [卡片选择] {label}"
else:
    synthetic_text = f"📋 [卡片操作] {compact}"

message_type = MessageType.TEXT  # 改为 TEXT 而非 COMMAND
```

## 测试

- 6 个单元测试覆盖（`tests/gateway/test_feishu.py::TestChoiceCardPayload`）
- 手动测试：卡片渲染正常，按钮可点击，按钮有反馈效果
- 回调到达 `_handle_card_action_event` 确认，但 `/card` 非注册命令导致响应中断
- 修复为 TEXT + 自然语言后，回调作为普通用户消息进入 agent 管道

## 边界安全

- 不修改默认卡片构建路径（`_build_markdown_card_payload` / `_build_text_card_payload`）
- 不修改消息发送/编辑逻辑
- 不修改配置/鉴权
- 审批卡片走 `_handle_approval_card_action` 独立路径，完全不受影响
