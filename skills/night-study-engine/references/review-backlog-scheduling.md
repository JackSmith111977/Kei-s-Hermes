# 复习积压调度信号

> **发现**：2026-05-15 dev_tools L1 批量复习实践中发现，`select_domain.py`/`adaptive_scheduler.py` 的自适应调度算法未考虑「到期概念数」（review backlog pressure），导致调度器推荐刚学过的领域而非积压严重的领域。

---

## 问题描述

### 实际案例（2026-05-15 06:00）

```
调度器推荐: ai_tech (score=0.277)
  - 2 小时前刚学过 (Q=88)
  - 0 个到期概念 ✅
  - 74 概念, 76% mastered

实际最优: dev_tools (score=0.064)
  - 22 小时前学习
  - 30 个到期概念 🔴
  - 109 概念, 75% mastered
```

调度器按公式 `priority × freshness_weight × (1-freshness) + (1-perf_weight) × (1-avg_quality)` 计算，ai_tech 的 low freshness (0.61) 使其得分远高于 dev_tools (freshness=0.99)。但 dev_tools 的 30 个到期概念意味着**知识债正在累积**——这些概念得不到复习就会过期、遗忘、信息过时。

### 根因

调度算法的 4 个输入维度中缺少「知识债压力」：

| 现有维度 | 捕获的信号 | 缺失的信号 |
|:---------|:-----------|:-----------|
| priority | 领域重要性 | 到期概念数 → 知识债压力 |
| freshness_score | 内容新鲜度 | 到期概念占比 → 维护负担 |
| avg_quality | 学习效果 | 连续跳到期 → 知识退步风险 |
| consecutive_failures | 学习难度 | — |

---

## 建议的改进

### 在调度算法中增加 Review Backlog Pressure 因子

```python
# 增加一个简单的压力因子
def review_backlog_pressure(kb, today="today"):
    concepts = kb.get("concepts", {})
    total = len(concepts)
    if total == 0:
        return 0.0
    overdue = sum(1 for c in concepts.values() 
                  if c.get("next_review", "1970-01-01") <= today)
    return overdue / total  # 0.0 ~ 1.0
```

### 整合到调度分中

```python
domain.score = (
    priority * freshness_weight * (1 - freshness_score) +
    (1 - performance_weight) * (1 - avg_quality) -
    consecutive_failures * failure_penalty +
    review_backlog_pressure(kb) * backlog_weight  # ← 新增
)
```

**建议权重**：`backlog_weight = 0.3`（低于 freshness_weight 但足以区分同等优先级领域）

### 边界条件

| 到期占比 | 压力级别 | 效果 |
|:--------:|:--------:|:----|
| 0% | 无压力 | 不改变现有排序 |
| 1-10% | 低 | 轻微调高优先级 |
| 10-25% | 中 | 明显提升 |
| >25% | 高 | 应大幅提升，除非 priority 极低 |

### 无需全量读取 KB 的检测方式

为了避免每次调度都读取整个 KB JSON，可以在 `learning_history` 配置中加入缓存字段：

```json
{
  "id": "dev_tools",
  "learning_history": {
    "total_sessions": 10,
    "avg_quality": 0.85,
    "consecutive_failures": 0,
    "due_concepts_count": 30,          # ← 新增缓存
    "due_concepts_ratio": 0.28,        # ← 新增缓存
    "due_concepts_updated": "2026-05-15" # 上次更新日期
  }
}
```

然后每次 KB 更新（通过 `update_knowledge_base.py` 或 `execute_code`）时同步更新这些缓存字段。

---

## 人工调度的回退策略

如果调度器仍推荐不理想的领域（比如本会话的情况），执行器可以：

1. **检查每个领域 KB 的到期概念数**（用 `execute_code` 快速计算）
2. **按「到期概念数 > 优先权分」判断**：到期数 ≥ 15 且 priority ≥ 0.5 时，应优先于刚学过的领域
3. **使用 `--skip` 参数跳过调度器推荐的领域**：`python3 select_domain.py --skip ai_tech`

不需要修改调度器代码即可在日常轮次中使用这个启发式规则。

---

## 后续跟踪

- [ ] 将 `due_concepts_count` 缓存字段集成到 `config-drift-check.py` 的同步逻辑中
- [ ] 在 `adaptive_scheduler.py` 中可选启用 backlog pressure 因子
- [ ] 验证 backlog_weight=0.3 在不同规模 KB 上的效果

### 2026-05-16 验证：Backlog 清除后的正常状态

在修复 ai_tech 的 config-KB 漂移后（配置同步从 12→15 sessions），本轮次对 dev_tools 进行了定期学习：

| 指标 | 值 |
|:-----|:---|
| 到期概念 | 5/109 (4.6%) — 低压力 |
| 调度器选择 | dev_tools (ai_tech 1.5h 前学过，已跳过) |
| 人工校验 | ✅ 到期数低 → 调度器推荐合理 |
| 结果 | 5 个到期全部 cleared, +1 新概念, Q=92 |

**关键验证**：配置漂移修复后，调度器推荐与人工判断一致。此前（2026-05-15）dev_tools 有 30 个到期概念是因调度器基于过期数据跳过优先级导致的累积。证明：**定期修复配置漂移是解决 backlog 堆积的前提条件**。当漂移存在时，调度器可能推荐刚学过的领域（基于过期 freshness），导致到期概念被忽视；漂移修复后，freshness 恢复正常，且 backlog 压力因子自然降低（因为到期概念已被清理）。
