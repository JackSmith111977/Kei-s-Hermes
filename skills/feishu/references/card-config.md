# 飞书消息卡片配置指南

> Hermes 飞书网关的 Interactive Card（JSON 1.0）自动包装机制配置与维护

## 概述

Hermes 飞书网关（`gateway/platforms/feishu.py`）**自动**将所有出站文本消息包装为飞书 Interactive Card。无需额外配置即可生效。

## 核心配置位置

**文件**：`~/.hermes/hermes-agent/gateway/platforms/feishu.py`

### 关键函数

| 函数 | 行号 | 说明 |
|------|------|------|
| `_build_outbound_payload()` | ~3675 | 入口：判断内容类型，自动调用卡片构建函数 |
| `_build_markdown_card_payload()` | ~509 | Markdown 内容 → 交互式卡片 |
| `_build_text_card_payload()` | ~546 | 纯文本内容 → 简化卡片 |

## 卡片结构

### Markdown 卡片模板

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "🐱 小玛"},
    "template": "blue"
  },
  "elements": [
    {"tag": "markdown", "content": "消息内容..."}
  ]
}
```

### 模板颜色自动选择

根据内容前 300 字符的语气自动选择：

| 触发词 | 模板颜色 |
|--------|----------|
| ⚠️ / ❌ / error: / failed: | `red` |
| ⚠ / warning: / caution | `orange` |
| 默认（无触发词） | `blue` |

## 错误处理

- `_INTERACTIVE_CONTENT_INVALID_RE`（~130 行）— 正则检测常见卡片错误
- 发送失败时自动降级为普通文本消息（~1511-1521 行）
- 降级后不会丢失消息内容

## 维护指南

### 修改卡片标题
编辑 `_build_markdown_card_payload()` 中 `"content": "🤖 Hermes"` 为想要的内容。

### 修改颜色逻辑
编辑 header_template 的选择逻辑（`feishu.py ~522-526`），添加或修改触发词和对应的颜色。

### 添加更多卡片元素
在 `elements` 数组中添加新的 tag 元素：
```python
"elements": [
    {"tag": "markdown", "content": content},
    {"tag": "hr"},  # 分割线
    {"tag": "note", "elements": [{"tag": "plain_text", "content": "备注信息"}]}
]
```

### 修改卡片配置
编辑 `config` 字段，如 `wide_screen_mode`、`enable_forward` 等。

### 完全禁用卡片
修改 `_build_outbound_payload()`，直接返回 `("text", content)` 而非调用卡片函数。

### 重启生效
修改 `feishu.py` 后需要**重启飞书网关服务**才能生效。

## 飞书卡片 API 参考

- 消息类型：`msg_type: "interactive"`
- 内容格式：JSON 1.0（飞书卡片协议）
- 支持元素：markdown、plain_text、hr、note、button、image 等
- 接口：`POST /open-apis/im/v1/messages`
- 大小限制：卡片 JSON 序列化后一般不超过 100KB

## 常见问题

**Q：卡片发送失败怎么办？**
A：系统会自动降级为文本消息。查看飞书网关日志可以找到具体错误原因。

**Q：如何调试卡片格式？**
A：在飞书开发者后台的「卡片调试工具」中粘贴卡片 JSON 预览效果。
