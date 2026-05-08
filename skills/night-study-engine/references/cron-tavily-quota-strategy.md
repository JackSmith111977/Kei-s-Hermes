# 📊 自动学习 Cron 时段 Tavily 配额策略

> **来源**: 2026-05-08 06:00 学习会话实测数据
> **目的**: 避免 Tavily 1,000 credits/月配额在多个 Cron 轮次中提前耗尽

---

## 背景

夜间自习引擎按 Cron 调度运行（00, 02, 04, 06, 08 时）。每个轮次至少使用 3 次 Tavily 搜索（每个领域 3-5 个搜索）。按月 30 天计算：

| 用量 | 计算 |
|------|------|
| 每日最低 | ~5 轮次 × 3 次搜索 = 15 次 |
| 每日最高 | ~5 轮次 × 5 次搜索 = 25 次 |
| 月均搜索 | ~450-750 次 |
| Tavily 免费额度 | 1,000 credits/月 |
| 单次搜索成本 | ~1-2 credits |

**结论**: 月后半段（15 日后）Tavily 配额极易耗尽。

---

## 时段分布模式

### 实测数据（2026-05-08）

| Cron 时间 | 使用的搜索工具 | 结果 |
|-----------|---------------|------|
| 00:00 | Tavily MCP | ✅ 成功 |
| 02:00 | Tavily MCP | ✅ 成功 |
| 04:00 | Tavily MCP | ✅ 部分成功 |
| **06:00** | Tavily MCP → ❌ 限流 | 🛑 Rate limit error |
| **06:00 (降级)** | **web_search (原生)** | **✅ 8 个官方源, Q=95** |
| **08:00** | Tavily MCP → ❌ 配额耗尽 | 🛑 `exceeds plan usage limit` |
| **08:00 (降级)** | **web_search (原生)** | **✅ 12 个来源(4主题×3), Q=88** |

### 规律

- **00:00-02:00**: 配额充足，Tavily 可用
- **04:00**: 可能出现首次失败
- **06:00+**: 🔴 高概率限流，MCP 服务器级联失败累计至 7 次后锁定 ~58s
- **MCP 级联效应**: Tavily API 返回 rate limit/quota exhaustion → 后续调用继续失败（即使配额已恢复） → 7 次后 MCP 服务器标记为 unreachable → 锁定 ~58s

### 配额耗尽 (Quota Exhaustion) vs 限流 (Rate Limit)

08:00 session 确认了两种不同的错误模式：

| 特征 | Rate Limit | Quota Exhaustion |
|------|-----------|------------------|
| 错误消息 | `rate limit` / `too many requests` | `exceeds your plan's set usage limit` / `Please upgrade your plan` |
| 恢复时间 | 分钟级 | **月度级**（下个月才重置） |
| 应对策略 | 等待后重试 / 降级 | 立即**永久降级**到 web_search |
| 典型时段 | 06:00+（多轮次累积后） | 月初~月中（配额用尽后） |

**实测结论（2026-05-08）**：
- 05-08 08:00 时 Tavily 已报告 exceeds your plan's set usage limit，说明 1,000 credits/月配额在 5 月 8 日已彻底耗尽
- 之前的策略推荐"每月 15 日后降级"过于乐观 —— 实际可用天数仅 5-7 天
- 推荐方案：**首次 Tavily 失败后立即降级**，而不是按日期硬编码

**web_search 在 08:00 session 的验证**：
- 4 个并行搜索覆盖 Notion Agents / Obsidian MCP / AI Meeting / Lark Feishu
- 获取 12 个独立来源，覆盖所有到期概念的最新信息
- 质量评分 0.88（与 Tavily 的 ~0.85+ 相当）
- 无配额限制、无 MCP 级联锁定风险

---

## 主动策略

### 推荐方案：按时段选择工具

```
[00:00-02:00] → 优先 Tavily MCP（配额充裕，精度高）
[04:00]       → 尝试 Tavily → 失败则降级 web_search
[06:00-08:00] → 直接使用 web_search 原生（跳过 Tavily，避免 MCP 级联锁定）
```

### web_search 原生作为默认降级的优势

本次 06:00 实测证明：
- **结果质量**: 8 个来源全部来自各大官方博客（Rust Blog、Next.js Blog、releases.rs）
- **结构清晰**: 返回 JSON(title, url, description)，便于后续 extract
- **无配额限制**: 不消耗 Tavily credits
- **速度**: 比 Tavily MCP 更快（无 MCP 序列化开销）
- **无级联锁定风险**: 不会触发 "unreachable after N consecutive failures"

### 实施步骤

1. **时段检测**: 在执行搜索前检查当前时间
   ```python
   hour = datetime.now().hour
   if hour >= 6:
       use_tavily = False  # 06:00+ 直接跳 Tavily
   ```

2. **配额预检**: 每月 10 日后（或首次 Tavily 失败后）自动降级
   ```python
   if datetime.now().day >= 10 or quota_exhausted:
       use_tavily = False  # 实测：5月8日配额即耗尽，10日已属乐观
   ```

3. **失败计数**: 跟踪本次会话中 Tavily 失败次数
   ```python
   tavily_failures = 0
   if tavily_failures >= 2:
       use_tavily = False  # 连续失败，切到 web_search
   ```

---

## MCP 级联锁定处理

当 Tavily API 返回 rate limit 后，MCP 服务器的行为：

| 连续失败次数 | MCP 行为 |
|-------------|----------|
| 1-3 | 正常重试 |
| 4 | 标记 "unreachable after 4 consecutive failures" |
| **7** | **完全锁定 ~58s（不可重试）— 08:00 session 实测** |

**关键**: 一旦进入 ~58s 锁定期，不要等待！立即使用 `web_search`/`web_extract` 原生工具。锁定期过后 MCP 自动恢复，不影响下一轮 Cron。

---

## 降级流程（快速参考）

```python
# 简化版降级逻辑
for query in queries:
    if use_tavily and hour < 6:
        try:
            result = mcp_tavily_tavily_search(query)
            tavily_failures = 0
        except RateLimitError:
            tavily_failures += 1
            if tavily_failures >= 2:
                use_tavily = False
                log("Tavily 降级到 web_search (连续失败)")
            result = web_search(query)
    else:
        result = web_search(query)  # 直接原生搜索
```

---

## 日志记录建议

降级发生时记录以下信息以便后续分析：
- `tavily_fallback_used: true/false`
- `fallback_reason: "rate_limit" / "scheduled" / "quota_projection"`
- `cron_hour: 0-23`
- `month_day: 1-31`
- `search_tool: "web_search / tavily"`

此数据可帮助优化策略（如降低 06:00 后的搜索数量）。
