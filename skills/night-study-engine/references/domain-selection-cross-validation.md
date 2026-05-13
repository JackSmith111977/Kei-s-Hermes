# 领域选择交叉验证 — 超越调度器的决策层

> **问题**：`select_domain.py` 的自适应调度公式 `priority × freshness_weight × (1-freshness) + (1-performance_weight) × (1-avg_quality) - failure_penalty` 可能因低 avg_quality 而过度推荐一个不适合的领域。
>
> **解决方案**：在调度器输出后增加一层交叉验证，检查今日实际已学记录 + KB 饱和状态 + 更新时间间隔。

## 适用场景

调度器输出与以下条件冲突时：

| 条件 | 检查方式 | 示例 |
|:----|:---------|:-----|
| 推荐领域今天已学过 | `grep {domain} ~/.hermes/logs/night_study.log \| grep {today}` | productivity 04:00 已学 |
| KB 高度饱和 | `mastered / total ≥ 90%` | productivity 33/33 = 100% |
| 与上次学习间隔 < schedule_interval | 检查 session_log 最后时间 vs 当前 cron 时间 | 04:00 学 → 08:00 cron，间隔 4h < 6h |
| 配置 freshness 很高 | `freshness_score > 0.85` | productivity 0.9（很新鲜） |
| avg_quality 异常低 | `avg_quality < 0.6` 但 KB 内容已经很丰富 | productivity 0.47 但 KB 已 33 mastered |

## 检查清单

在信任调度器输出之前，逐项验证：

```python
# 伪代码：交叉验证检查
domain = scheduler_output

# 1️⃣ 今日是否已学习此领域？
today_sessions = grep(night_study.log, today, domain)
if len(today_sessions) >= 1:
    last_session_time = extract_time(today_sessions[-1])
    hours_since = current_hour - last_session_time
    if hours_since < domain.schedule_interval_hours:
        FLAG("今日内容尚新，不足间隔时间")

# 2️⃣ KB 是否已饱和？
kb = load_kb(domain.id)
mastered_ratio = count_mastered(kb) / len(kb.concepts)
if mastered_ratio > 0.85:
    if len(today_sessions) >= 1:
        SKIP("饱和领域 + 今日已有 session")
    else:
        FLAG("饱和领域，考虑边缘狩猎而非广度学习")

# 3️⃣ 分数是否由低 avg_quality 驱动？
# 当新鲜度 > 0.85 且 avg_quality < 0.6，分数主要来自低质量分
if domain.freshness_score > 0.85 and domain.avg_quality < 0.6:
    CALCULATE("剔除 avg_quality 后的分数", pure_freshness_score)
    if pure_freshness_score < 0.1:
        SKIP_OR_LOWER("调度器分数被质量分扭曲")
```

## 决策树

```
调度器推荐领域 A
    │
    ├─ A 今天已学过 AND 饱和度 ≥ 85%？
    │   └─ ✅ → 跳过 A，选第二顺位
    │
    ├─ A 今天已学过 AND 饱和度 < 85%？
    │   ├─ 间隔 ≥ schedule_interval_hours？
    │   │   ├─ ✅ → 可以继续学 A（边缘狩猎模式）
    │   │   └─ ❌ → 跳过 A，选第二顺位
    │
    ├─ A 今天未学但饱和度 ≥ 90%？
    │   ├─ 上次更新距今 > 24h？
    │   │   ├─ ✅ → 可选 A（边缘狩猎）
    │   │   └─ ❌ → 跳过，选其他领域
    │
    └─ A 今天未学且饱和度 < 85%？
        └─ ✅ → 接受调度器推荐
```

## 实战验证：2026-05-13 08:00

### 初始状态

| 领域 | 调度器分 | 今日已学 | 饱和度 | 新鲜度 | avg_quality |
|:---|:-------:|:-------:|:-----:|:-----:|:----------:|
| productivity | 0.354 | ✅ 1次@04:00 | 100% | 0.9 | 0.47 |
| anime_acg | 0.315 | ❌ | 80% | 0.95 | — |
| dev_tools | 0.177 | ✅ 2次 | 50% | 0.85 | 0.81 |
| ai_tech | 0.108 | ❌ | 83% | 0.9 | 0.91 |

### 交叉验证过程

```
调度器推荐 → productivity (0.354)
    │
    ├─ 今日已学? ✅ 04:00 (4h前, < 6h间隔)
    ├─ 饱和度? ✅ 100% (33/33全部mastered)
    ├─ 新鲜度? ✅ 0.9
    ├─ avg_quality? ⚠️ 0.47 (异常低, 但内容已丰富)
    │
    └─ 结论: ❌ 跳过 → 选择第二顺位
         │
         └─ ai_tech (调度器分最低但今日未学 + 高优先级0.9)
              → ✅ 选择 ai_tech
```

### 结果

选择 ai_tech 而非 productivity 后：

| 指标 | 值 |
|:---|:---:|
| 新概念 | +14 |
| 升级 | +2 |
| 质量分 | 89 |
| 会话总概念 | 61 |
| ai-trends Skill | v1.12 |

验证了「不盲目信任调度器」的可行性——ai_tech 虽然调度器分最低 (0.108)，但高优先级 + 今日未学 + 有缺口的概念空间，产出了本日最有价值的会话。

## 已知陷阱

1. ❌ **信任调度器为绝对真理** — 调度器公式是静态的，不感知今天已学了多少次，也不感知 KB 概念饱和度
2. ❌ **过度依赖 avg_quality** — 低 avg_quality 会让调度器过度推荐同一领域（再学一次提升质量分）。检查 avg_quality 是否因早期session拉低（首次 session 数据点少时）
3. ❌ **忽略疲劳因子** — 即使调度器推荐，同一领域在单日内学习 ≥3 次时边际收益递减
4. ❌ **只看优先级不看饱和度** — priority 0.9 的领域如果已 100% mastered + 今日已学，学它等于浪费时间

---

**来源**: 2026-05-13 08:00 cron 实践 — 覆盖 select_domain.py 推荐，转向实际优先级更高、今日未学的领域
