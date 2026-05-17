# 领域选择交叉验证 — 超越调度器的决策层

> **问题**：`select_domain.py` 的自适应调度公式 `priority × freshness_weight × (1-freshness) + (1-performance_weight) × (1-avg_quality) - failure_penalty` 可能因低 avg_quality 而过度推荐一个不适合的领域。
>
> **解决方案**：在调度器输出后增加一层交叉验证，检查今日实际已学记录 + KB 饱和状态 + 更新时间间隔。

## 配置版本检测 — v3/v2 抉择

> **问题**：当 `night_study_config_v3.json`（18 领域，自动生成于 2026-05-16）存在时，读取 v2（4 领域）会导致调度数据严重不完整 —— 从未初始化的领域（0 sessions、freshness=0.5、avg_Q=0.5）会被完全忽略。

### 检测方式

会话开始时，优先检查 v3 配置的存在性：

| 文件名 | 领域数 | 来源 | 生成方式 |
|--------|:------:|:----:|:--------:|
| `night_study_config_v3.json` | 18 | `generate-night-study-config.py` | 自动从 cap-pack 映射 |
| `night_study_config_v2.json` | 4 | 手动创建 | 原始 4 领域配置 |

```python
from pathlib import Path
import json

v3 = Path.home() / ".hermes" / "config" / "night_study_config_v3.json"
v2 = Path.home() / ".hermes" / "config" / "night_study_config_v2.json"

config_path = v3 if v3.exists() else v2
domains_count = len(json.load(open(config_path))["domains"])
# v3 → 18 领域；v2 → 4 领域
```

### 漂移标志

即使使用 v3 配置，也需要检查 `learning_history` 是否真实：

| 检查项 | 健康值 | 漂移标志 | 处理方法 |
|:-------|:------:|:---------|:---------|
| `total_sessions` vs KB session_log 数 | 匹配 | v3 中为 0 但 KB 有 5+ session | 运行 `batch-config-sync-pattern.md` 全量同步 |
| `avg_quality` vs KB 实际 | 0.8-0.95 | v3 中为 0.5 但 KB 有实际 session | `config-drift-check.py --fix-all` |
| 领域数量 | 18 | 突然少于 15（已学习领域在 KB 存在但不在配置中） | 重新运行 `generate-night-study-config.py` |

### 实战验证：2026-05-17 08:00

首次使用 v3 配置进行调度。v3 配置中的 14 个新领域（如 devops_monitoring、github_ecosystem）均为 `total_sessions=0, avg_quality=0.5`，调度公式为 `priority*0.3 + 0.3`：

| 领域 | priority | 调度分 | 结果 |
|:-----|:--------:|:------:|:-----|
| devops_monitoring | 0.70 | 0.510 | 🥇 **被选择，首次初始化成功** |
| github_ecosystem | 0.70 | 0.510 | 第二顺位 |
| ai_tech（对比） | 0.95 | 0.260 | 已学 17 次，分数被高 freshness 压低 |

若不检查 v3 配置，仅看 v2 的 4 个领域，ai_tech 会因 `0.95*0.6*0.34 + 0.6*0.11 = 0.26` 被选中——但 ai_tech 早就今天 02:04 学过了。v3 配置正确地将 12 个从未学习的领域排在前面。

```text
[无 v3]  v2 选择 ai_tech (0.26) → 6h 前刚学过，边际收益低
[有 v3]  v3 选择 devops_monitoring (0.51) → 首次初始化，+7 概念，Q=89 ✓
```

---

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
