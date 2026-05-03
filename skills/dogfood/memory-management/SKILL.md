---
name: memory-management
description: Hermes Agent 记忆库（Memory）智能管理与上下文窗口优化指南。涵盖 Memory 分层策略、Context Window 管理（滑动窗...
version: 2.0.0
triggers:
- 记忆
- 上下文
- memory
- token
- 遗忘
metadata:
  hermes:
    tags:
    - memory
    - context-management
    - optimization
    - sliding-window
    category: dogfood
    skill_type: operational
    design_pattern: inversion
---
# Memory 智能管理 🔧🧠

> **核心理念**：上下文管理不仅仅是“删除旧消息”，而是**信息密度的博弈**。更精简、聚焦的上下文能产生更高质量的输出。

## 一、当前环境配置

```yaml
# config.yaml
compression:
  enabled: true
  threshold: 0.5           # 上下文达到 50% 时触发压缩
  target_ratio: 0.2        # 压缩到原始大小的 20%
  protect_last_n: 20       # 保护最近 20 轮对话不被压缩
memory:
  memory_char_limit: 2200  # 持久记忆库限制
  user_char_limit: 1375
  nudge_interval: 10
  flush_min_turns: 6
```

## 二、Memory (持久化) 分层策略

Memory 是跨会话的少量关键信息，容量极小（2200 chars）。

### 三层优先级模型

| 层级 | 内容类型 | 保留策略 | 示例 |
|:---|:---|:---|:---|
| 🔴 **P0 核心** | 用户偏好、系统身份、铁律 | 永不删除 | "用户偏好猫娘风格" |
| 🟡 **P1 重要** | 环境配置、API经验、工具链 | 合并后保留 | "飞书发文件正确流程" |
| 🟢 **P2 参考** | Skill 创建记录、临时发现 | 可删除/压缩 | "xxx skill 已创建" |

### 容量分配建议
- P0 核心：~800 chars（36%）
- P1 重要：~1000 chars（45%）
- P2 参考：~400 chars（18%）

### 写入前检查清单
- [ ] 这条信息下次会话还有用吗？→ 否 → **不写**
- [ ] session_search 能找到吗？→ 能 → **不写**
- [ ] 有对应的 skill 记录了吗？→ 有 → **简化写**（只写索引）
- [ ] 会和已有条目重复吗？→ 会 → **用 replace 而非 add**

## 三、上下文窗口（Context Window）管理策略

当对话变长，Context Window 接近上限时，Hermes 会自动触发压缩。理解这些策略有助于 boku 更好地配合。

### 1. 滑动窗口 (Sliding Window) - Hermes 默认行为
- **机制**：保留最近 N 轮对话 (`protect_last_n: 20`)，丢弃更早的。
- **优点**：极快，O(1) 复杂度。
- **缺点**：**丢失早期上下文**，如果用户在第 5 轮提到的需求在第 25 轮被引用，boku 会“忘记”。
- **boku 的对策**：重要需求或约束如果较早提出，在对话中期**主动重申**，将其“滑入”保护窗口。

### 2. 摘要压缩 (Summarization) - Hermes 压缩引擎
- **机制**：当上下文 > 50% 时，调用 LLM 将旧对话压缩为摘要。
- **优点**：保留关键信息，大幅减少 Token 消耗。
- **缺点**：丢失细节，压缩过程本身消耗 Token 和时间。
- **boku 的对策**：在压缩触发前，用一两句话**总结当前任务状态**，这样即使被压缩，摘要中也会包含关键进度。

### 3. Token 截断 (Truncation) - 兜底方案
- **机制**：直接切掉最早的 Token 以腾出空间。
- **风险**：可能切断 System Prompt 或关键指令。
- **对策**：永远不要假设 boku 记得很久以前的代码细节。

### 4. 选择性记忆 (Selective Memory / RAG) - 进阶
- **机制**：通过 `session_search` 按需检索历史会话，而不是全量加载到上下文。
- **boku 的对策**：当用户问“我们之前做了什么？”时，优先用 `session_search` 而不是在 Memory 里翻找。

## 四、上下文压缩恢复机制

### 问题
Context Compression 发生后，boku 可能会丢失对当前任务的“体感”。

### 解决方案：压缩前快照 + 压缩后自检

**压缩前**（boku 主动执行，或发现上下文快满时）：
1. 用 `memory` 记录当前任务状态（如“正在进行 PDF 生成，已完成第 3 页”）。
2. 用 `todo` 工具保存进度。

**压缩后**（boku 自动恢复）：
1. 检查 `memory` 中是否有任务状态记录。
2. 查看 `todo` 队列。
3. 用 `session_search` 找回最近的会话片段。
4. 继续执行，并向用户汇报“上下文已刷新，boku 正在继续...”

## 五、Skill 密度优化

### 问题
90+ 个 skill，SKILL.md 总大小占用大量上下文，导致可用空间减少。

### 优化策略

1. **精简 description**：控制在 30 字内，只包含触发词。
   ```yaml
   # ❌ 太长 (占用上下文)
   description: "Complete guide to using and orchestrating autonomous AI coding agents..."
   # ✅ 精简 (节省 Token)
   description: "Spawn and orchestrate AI coding agents (Claude Code, Codex, OpenCode)"
   ```

2. **延迟加载 (Lazy Loading)**：详细内容放在 references/ 目录，SKILL.md 只做索引。
   ```yaml
   # SKILL.md 中只写路由规则
   triggers: ["浏览器操作", "打开网页"]  # 匹配时才加载全文
   ```

3. **定期清理**：删除/归档不使用的 skill。

## 六、常见陷阱与对策

| 陷阱 | 表现 | 对策 |
|:---|:---|:---|
| **中间遗忘** | LLM 容易忘记中间的信息，只记得开头和结尾 | 重要信息放在 System Prompt 或最近 5 轮对话中 |
| **上下文污染** | 大量的调试日志、失败尝试占据了上下文 | 使用 `terminal` 时尽量精简输出，或重定向到文件 |
| **Token 膨胀** | 粘贴大段代码导致上下文瞬间爆炸 | 只粘贴关键部分，用 `read_file` 按需读取 |
