# Hermes Prompt Assembly & SOUL.md 机制

> 来源：Hermes Agent 官方 Prompt Assembly 文档
> https://hermes-agent.nousresearch.com/docs/developer-guide/prompt-assembly

## System Prompt 组装顺序

每次会话初始化时，system prompt 按以下顺序组装：

```
1. Agent Identity → SOUL.md（替换 DEFAULT_AGENT_IDENTITY）
2. Tool-aware behavior guidance
3. Honcho static block（启用时）
4. Optional system message
5. MEMORY.md 快照（2,200 chars 上限）
6. USER.md 快照（1,375 chars 上限）
7. Skills index（已安装 skill 清单）
8. Context files（AGENTS.md / .cursorrules 等，仅加载一种）
9. Timestamp / session ID
10. Platform hint（飞书/微信/CLI 等）
```

## SOUL.md 加载流程

```python
# agent/prompt_builder.py (简化)
soul_path = home() / "SOUL.md"
if not soul_path.exists():
    return None  # 回退到 DEFAULT_AGENT_IDENTITY

content = soul_path.read_text(encoding="utf-8").strip()
content = _scan_context_content(content, "SOUL.md")  # 安全扫描
content = _truncate_content(content, "SOUL.md")       # 20k chars 上限
return content
```

### 关键行为

| 行为 | 说明 |
|------|------|
| **文件缺失** | 回退到内置 `DEFAULT_AGENT_IDENTITY` |
| **文件为空** | 空内容，不注入任何身份文本 |
| **安全扫描** | 检测 prompt injection（不可见 unicode、忽略指令、凭据窃取） |
| **截断上限** | **20,000 字符**，用 70/20 头尾比 + 截断标记 |
| **去重保护** | 如果 SOUL.md 已作为 identity 加载，`build_context_files_prompt(skip_soul=True)` 防止重复 |

## 上下文文件优先级

`build_context_files_prompt()` 使用优先级系统——**仅加载一种**，先匹配者胜出：

| 优先级 | 文件 | 搜索范围 | 备注 |
|--------|------|----------|------|
| 1 | `.hermes.md` / `HERMES.md` | CWD 到 git root | Hermes 原生项目配置 |
| 2 | `AGENTS.md` | CWD 仅 | 通用 agent 指令文件 |
| 3 | `CLAUDE.md` | CWD 仅 | Claude Code 兼容 |
| 4 | `.cursorrules` / `.cursor/rules/*.mdc` | CWD 仅 | Cursor 兼容 |

## 大小限制一览

| 文件 | 上限 | 截断策略 | 位置 |
|------|------|----------|------|
| SOUL.md | **20,000 chars** | 70/20 头尾 + 截断标记 | ~/.hermes/SOUL.md |
| AGENTS.md / CLAUDE.md | **20,000 chars** | 70/20 头尾 + 截断标记 | 项目目录 |
| MEMORY.md | **2,200 chars** (~800 tokens) | 写入时报错，需合并/删除 | ~/.hermes/memories/ |
| USER.md | **1,375 chars** (~500 tokens) | 同上 | ~/.hermes/memories/ |

## SOUL.md 的压缩免疫特性

- SOUL.md 属于 system prompt 的前半部分
- 上下文压缩时，`protect_first_n = 3`（硬编码）保护 system prompt + 前几轮对话
- 因此 SOUL.md 在上下文压缩后不会被摘要化或丢失
- 但 system prompt 本身会占用上下文窗口——SOUL.md 过大（>20k）会被截断

## 重要注意事项

1. **SOUL.md vs AGENTS.md 分工**：SOUL.md 专注身份和风格，项目指令放 AGENTS.md
2. **安全扫描误判**：如果包含类似 prompt injection 的内容可能被阻断或更改
3. **太长被截断**：检查是否有冲突指令导致内容被误判为 injection
4. **临时切换**：用 `/personality` 做临时模式切换，不要频繁改 SOUL.md
5. **subagent 场景**：`skip_context_files=True` 时 SOUL.md 不会被加载，回退到 DEFAULT_AGENT_IDENTITY
