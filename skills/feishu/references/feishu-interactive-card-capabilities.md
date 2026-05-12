# 飞书交互卡片能力速查

> 基于飞书开放平台官方文档研究和深度阅读 (2026-05-12)
> 用途: 为需要交互卡片的场景（需求澄清、选择确认等）提供快速参考

---

## 一、交互组件总览

| 组件 | tag | 交互类型 | 交互模块位置 | 回调标识 tag |
|:-----|:----|:---------|:------------|:------------|
| **按钮** | `button` | `callback` / `open_url` / `form_submit` / `form_reset` | JSON 1.0: `action.actions[].button`<br>JSON 2.0: `elements[].button` → `behaviors[]` | `"button"` |
| **列表选择器** | `selectMenu` | `callback` | JSON 1.0: `action.actions[].selectMenu` | `"select_static"`（自定义选项）<br>`"select_person"`（人员选择） |
| **输入框** | `input` | `callback`（提交按钮触发） | JSON 1.0: `action.actions[].input`<br>JSON 2.0: `elements[].input` + 表单提交 | `"input"` |
| **表单容器** | `form` | 统一提交（内嵌组件 → form_submit 按钮） | `elements[].form` 包裹 | 各组件独立 tag |
| **日期选择器** | `datePicker` / `picker_time` / `picker_datetime` | `callback` | `action.actions[]` | `"date_picker"` / `"picker_time"` / `"picker_datetime"` |
| **折叠按钮组** | `overflow` | `callback` / `open_url` | `action.actions[].overflow` | `"overflow"` |

---

## 二、交互配置方式

### JSON 2.0（推荐，新卡片使用此格式）

组件直接放 `elements` 数组，通过 `behaviors[]` 配置交互：

```json
{
  "elements": [
    {
      "tag": "button",
      "text": {"tag": "plain_text", "content": "确认"},
      "type": "primary",
      "behaviors": [
        {
          "type": "callback",
          "value": {"action": "confirm"}
        }
      ]
    }
  ]
}
```

### JSON 1.0（Hermes feishu.py 当前使用的格式）

交互组件必须放在 `action` 模块的 `actions` 数组中——这是 Hermes 网关的 `send_exec_approval()` 和 `_build_choice_card_payload()` 所用的格式：

```json
{
  "elements": [
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {"tag": "plain_text", "content": "确认"},
          "type": "primary",
          "value": {"key": "value"}
        }
      ]
    }
  ]
}
```

> 注意: JSON 1.0 中 `value` 直接在按钮定义中，不是通过 `behaviors` 字段

---

## 三、表单容器（核心方案 — 多输入+提交）

适用于需要用户填写多个字段的场景：

```json
{
  "tag": "form",
  "name": "feedback_form",
  "elements": [
    {
      "tag": "markdown",
      "content": "请补充信息："
    },
    {
      "tag": "input",
      "name": "comment",
      "label": {"tag": "plain_text", "content": "意见"},
      "placeholder": {"tag": "plain_text", "content": "请输入..."}
    },
    {
      "tag": "button",
      "name": "submit_btn",
      "text": {"tag": "plain_text", "content": "提交"},
      "type": "primary",
      "action_type": "form_submit"
    },
    {
      "tag": "button",
      "name": "reset_btn",
      "text": {"tag": "plain_text", "content": "取消"},
      "type": "default",
      "action_type": "form_reset"
    }
  ]
}
```

---

## 四、回调数据结构

### 回调接收

用户点击交互组件后，飞书向配置的 webhook 地址发送 POST：

```json
{
  "schema": "2.0",
  "event_type": "card.action.trigger",
  "operator": {
    "open_id": "ou_xxx",
    "union_id": "on_xxx"
  },
  "action": {
    "value": {"action": "confirm"},
    "tag": "button",
    "form_value": {
      "comment": "用户输入的内容"
    },
    "name": "submit_btn"
  },
  "context": {
    "open_message_id": "om_xxx",
    "open_chat_id": "oc_xxx"
  },
  "token": "c-xxx"
}
```

### 回调后的响应要求

| 响应方式 | 时间要求 | 说明 |
|:---------|:--------:|:-----|
| 立即更新卡片 | 3 秒内 | 在 HTTP 200 响应体中返回新卡片 JSON |
| 不更新卡片 | 3 秒内 | 仅返回空 HTTP 200 |
| 延时更新卡片 | 30 分钟内 | 先返回空 200，再调用 `延时更新消息卡片` API |

---

## 五、重要限制

1. **回调仅对应用发送的卡片有效** — 自定义机器人发送的卡片不支持回调（Hermes 网关以应用身份发送，所以没问题）
2. **有效期**：
   - JSON 2.0: 请求回调和更新有效期统一 **14 天**
   - JSON 1.0: 请求回调 **30 天**，更新卡片 **14 天**
3. **超时**：服务端必须在 **3 秒内**以 HTTP 200 响应，否则客户端显示错误
4. **单次可更新**：同一卡片最多可通过 `token` 更新 **2 次**
5. **按钮禁用**：需要准备两张卡片（可点击/已禁用），回调后切换

---

## 六、Hermes 网关集成

### 现有基础设施（已就绪 ✅）

`gateway/platforms/feishu.py` 已具备完整的卡片交互基础设施：

| 能力 | 行号 (v0.12.0) | 说明 |
|:-----|:-:|------|
| **`<!-- card:xxx -->` 标记解析** | `_CARD_TYPE_HINT_RE` @ L190 | 正则匹配 `<!-- card:{type} -->`，目前支持 `dashboard`/`progress`/`choice` |
| **卡片类型路由** | `_build_outbound_payload()` @ ~4680 | 按 type 分发到对应构建函数 |
| **交互卡片发送** | `send_exec_approval()` @ ~2400 | 已实现带按钮的审批卡片 |
| **按钮回调注册** | `.register_p2_card_action_trigger()` @ L2109 | 通过飞书 SDK 接收 `card.action.trigger` |
| **回调路由** | `_on_card_action_trigger()` @ L2953 | 区分审批(`hermes_action`)和通用回调 |
| **通用回调处理** | `_handle_card_action_event()` @ L3102 | 按钮点击 → 合成 `/card button {...}` 消息 → Agent 管道 |
| **去重机制** | `_is_card_action_duplicate()` @ L3090 | 15 分钟窗口防重复处理 |

### 添加新的卡片类型（标准模式）

要添加新的交互卡片类型（如 `<!-- card:survey -->`），只需要：

**1. 在 `_build_outbound_payload()` 新增 elif 分支**（~L4694）：

```python
elif card_type == "survey":
    card = _build_survey_card_payload(body)
    return "interactive", json.dumps(card, ensure_ascii=False)
```

**2. 添加构建函数**（按现有模式）：

```python
def _build_survey_card_payload(content: str) -> dict:
    # 解析 content 构建卡片 JSON
    # 使用 JSON 1.0 格式（action.actions[] 放按钮）
    return {
        "config": {"wide_screen_mode": True, "enable_forward": True},
        "header": _build_card_header(title="📋 问卷", template="blue"),
        "elements": [
            {"tag": "markdown", "content": _sanitize_card_markdown(content)},
            {"tag": "action", "actions": [buttons...]},
            {"tag": "hr"},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "💡 请选择"}]},
        ],
    }
```

**3. 添加单元测试**（按 `TestChoiceCardPayload` 模式）

**4. 重启网关**：`systemctl --user restart hermes-gateway`

### 已实现的卡片类型

#### `<!-- card:choice -->`（2026-05-12 新增，2026-05-12 更新）

让用户从多个选项中用按钮选择。Agent 在内容中使用如下格式：

```
<!-- card:choice -->
主人，请选择：

1. 方案A：快速实现
2. 方案B：深度优化
3. 其他想法
```

解析规则：
- 第一个编号行之前的所有内容 → 问题文本（markdown 渲染）
- 编号行 `N. text` → 按钮（最多 5 个）
- 第一个按钮为 `primary` 类型，其余为 `default`

按钮的 `value` 结构：
```json
{"choice": "1", "label": "方案A：快速实现"}
```

当用户点击按钮时，`_handle_card_action_event()` 合成 TEXT 消息：
`📋 [卡片选择] 方案A：快速实现`

⚠️ **按钮 value 推荐包含 `question` 字段**：避免 Agent 收到选择后不知道原始问题上下文。详见下方「已知问题 → 上下文丢失」。

实现位置：
- `_build_choice_card_payload()` — 卡片构建函数（约 L1159）
- `_handle_card_action_event()` — 回调合成处理（约 L3181）
- 测试: `tests/gateway/test_feishu.py::TestChoiceCardPayload`（6 个测试用例 ✅ 全部通过）

### 已知问题

#### ✅ 已修复：卡片回调无法触发 Agent 回复（COMMAND→TEXT）

> **2026-05-12 修复**：`_handle_card_action_event()` 已将消息类型从 `COMMAND` 改为 `TEXT`，内容从 `/card button {...}` 改为 `📋 [卡片选择] {label}`。

**历史根因**（修复前）：

`_handle_card_action_event()` 原来创建以下合成事件：

```python
synthetic_text = f"/card {action_tag}"                           # → "/card button {...}"
message_type = MessageType.COMMAND
```

当此事件进入网关 `run.py` 的 `_process_bridge_event_pipeline` 消息管道时：
1. `event.get_command()` → 返回 `"card"`（因为文本以 `/` 开头）
2. `resolve_command("card")` → 返回 `None`（`/card` 不在 `GATEWAY_KNOWN_COMMANDS` 中）
3. 经过所有 `if _cmd_def_inner and ...` 守卫条件 → 全部跳过
4. 最终到达 `_DEDICATED_HANDLERS` 检查 → `/card` 不在此集合中
5. 消息被丢弃，不产生可见回复

**修复内容**（两处改动）：

```python
# 改动①：消息类型从 COMMAND 改为 TEXT
message_type = MessageType.TEXT  # 原: MessageType.COMMAND

# 改动②：消息内容从 /card 命令改为自然语言
label = action_value.get('label', '') if isinstance(action_value, dict) else ''
if label:
    synthetic_text = f"📋 [卡片选择] {label}"  # 原: f"/card button {...}"
```

**安全性验证**：
- ✅ 审批卡片不受影响（走 `_handle_approval_card_action` 单独路径）
- ✅ 回调去重保留（`_is_card_action_duplicate()` 在上游已检查）
- ✅ Agent 上下文正常（自然语言被正常处理）

---

#### 🔴 未修复：上下文丢失导致回复不对

**问题**：Agent 收到 `📋 [卡片选择] {label}` 时，**没有原始问题的上下文**。例如收到「📋 [卡片选择] 方案A」，但不知道方案A对应什么问题。

**触发场景**：点击 choice 卡片按钮 → 回调合成消息仅含 label → Agent 回复与原始问题无关。

**根因**：按钮 `value` 中只有 `choice` 和 `label` 字段，缺少 `question`。回调合成消息只有 label，没有原始问题。

**修复方案**（两处修改 `feishu.py`）：

**① `_build_choice_card_payload()`** — 在按钮 value 中加入 `question`：

```python
# 第 1213 行附近
"value": {
    "choice": str(i + 1),
    "label": opt[:200],
    "question": question[:300],   # ← 加上问题原文，方便回调携带上下文
}
```

**② `_handle_card_action_event()`** — 合成消息带上问题：

```python
# 第 3217 行附近
synthetic_text = f"📋 [卡片选择] {label}"
if action_value.get("question"):
    synthetic_text += f"\n> {action_value['question'][:200]}"
```

Agent 收到的消息变成：
```
📋 [卡片选择] 方案A：快速实现
> 主人，请选择项目的实现方案？
```

---

#### 🔴 未修复：中断递归导致消息被吞

**问题**：快速点击多个 choice 按钮，或点击按钮同时发送消息时，部分 callback 合成消息被丢弃，Agent 无任何回复。

**网关日志特征**：
```
WARNING gateway.run: Interrupt recursion depth 3 reached for session ... — queueing message instead of recursing.
```

**根因**：卡片回调的合成消息进入 `_handle_message_with_guards()`（per-chat lock 序列化）→ 传给 `handle_message()` → 进入 agent 管道。当 agent 正在处理上一条消息时：
1. 新消息进入 `_process_bridge_event_pipeline`
2. 检查到 agent 正忙 → 尝试中断当前处理 → 递归调用 `run_conversation()`
3. 递归深度达到上限（3 层）→ 消息被排队
4. 排队的消息可能永远不会被处理

**影响范围**：
- 快速连续点击按钮（间隔 < 5 秒）
- 点击按钮同时发送文本消息
- cron 触发消息与人工消息同时到达

**暂无简单修复**。涉及网关消息调度架构。缓解措施：
- 点击按钮后等待 Agent 回复再点下一个
- 避免在 Agent 处理消息时快速点击按钮

### 边界保障原则

修改 `feishu.py` 时必须遵守：

| 原则 | 说明 | 违反后果 |
|:-----|:-----|:---------|
| 🚫 不动默认路径 | 不修改 `_build_markdown_card_payload()` / `_build_text_card_payload()` | 所有系统消息变成错误格式 |
| 🚫 不动收发核心 | 不修改 `send_message()` / `edit_message()` | 消息发送失败 |
| 🚫 不动回调处理 | 不修改 `_handle_card_action_event()` / `_on_card_action_trigger()` | 卡片交互断裂 |
| 🚫 不动配置鉴权 | 不修改 config / .env / 回调地址 | 连接中断 |
| ✅ 只加新分支 | 在 `_build_outbound_payload()` 加新 `elif` | 零副作用 |

### 卡片回调调试清单

当 choice 卡片按钮点击后 Agent 无响应或响应不对时，按以下顺序排查：

```text
□ 1. 检查 gateway 日志是否有 card action 路由
   journalctl --user -u hermes-gateway --since "5 min ago"
   grep "Routing card action" → 确认回调被接收
   grep "Unrecognized slash command /card" → 旧版代码（未修复 COMMAND→TEXT）
   grep "Interrupt recursion depth" → 消息被排队/丢弃
   grep "Send failed" → 消息发送失败

□ 2. 检查消息类型
   确认 _handle_card_action_event() 使用 MessageType.TEXT（非 COMMAND）
   查看 feishu.py L3241（当前行号可能随版本变化）

□ 3. 检查按钮 value 结构
   查看 _build_choice_card_payload() 的 value 字典：
   - 是否有 label 字段？→ 否则合成消息为空
   - 是否有 question 字段？→ 否则 Agent 缺少上下文
   - label 是否超过 200 字符？→ 会被截断

□ 4. 检查去重
   确认同一按钮未被重复点击（15 分钟窗口内）
   查看 _is_card_action_duplicate() 的日志 Debug 输出

□ 5. 检查网关是否重启
   修改 feishu.py 后必须：systemctl --user restart hermes-gateway
   查看 gateway 启动时间：systemctl --user status hermes-gateway

□ 6. 实机测试流程
   ① 让 Agent 发送 <!-- card:choice --> 卡片
   ② 在飞书客户端点击按钮
   ③ 观察客户端是否有「已发送」反馈
   ④ 检查 gateway 日志是否有 Routing card action
   ⑤ 等待 Agent 回复（可能需要几秒）
   ⑥ 如无回复，检查日志的 Interrupt recursion / Send failed
```

---

## 七、参考来源

- [配置卡片交互](https://open.feishu.cn/document/feishu-cards/configuring-card-interactions)
- [按钮组件](https://open.feishu.cn/document/feishu-cards/card-components/interactive-components/button)
- [输入框组件](https://open.feishu.cn/document/feishu-cards/card-components/interactive-components/input)
- [列表选择器](https://open.feishu.cn/document/ukTMukTMukTM/uIzNwUjLycDM14iM3ATN)
- [卡片回调通信](https://open.feishu.cn/document/feishu-cards/card-callback-communication)
- [处理卡片回调](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/handle-card-callbacks)
- [开发卡片交互机器人](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/quick-start/develop-a-card-interactive-bot)
