# 高密度领域边缘狩猎策略

> 当一个领域的 Knowledge Base 已高度完善（>50 个概念、大部分 mastered），传统搜索策略会陷入"重温已有知识"的低效循环。需要切换到「边缘狩猎」模式。

## 适用场景

| 指标 | 阈值 | 含义 |
|:----|:---:|:------|
| 概念总数 | ≥ 50 | 领域知识已充分覆盖 |
| mastered 占比 | ≥ 60% | 核心知识已掌握 |
| 今日已有 session | ≥ 2 | 今日已多次学习此领域 |
| 最近一次更新 | < 6h | 知识库非常新鲜 |

**同时满足上述条件时**，应切换到边缘狩猎模式。

## 边缘狩猎策略

### 1. 时段感知搜索关键词

不是泛泛地搜整个领域，而是面向**最近发生的事件**：

| 策略 | 做法 | 示例 |
|:----|:-----|:------|
| **版本差异** | 搜索最新 patch/point release | `Python 3.14.5 changes`（而非 `Python 3.14 features`） |
| **回溯/更正** | 搜索 bugfix、revert、deprecation | `incremental GC revert`、`removed feature` |
| **生态边缘** | 搜索周边工具链而非核心语言 | `Cargo regression`、`pip known issues` |
| **时间窗收窄** | 搜索结果限制在最近 N 天 | `past week` / `past 2 weeks` |

### 2. 搜索前的 KB 分析

搜索之前，先跑一次现有 KB 的「概念密度分析」：

```python
concepts = kb['concepts']
total = len(concepts)
mastered = sum(1 for c in concepts.values() if c.get('status') == 'mastered')
developing = sum(1 for c in concepts.values() if c.get('status') == 'developing')
new_count = sum(1 for c in concepts.values() if c.get('status') == 'new')
due_today = sum(1 for c in concepts.values() if c.get('next_review', '') <= today)

print(f"Total:{total} Mastered:{mastered} Developing:{developing} New:{new_count} Due:{due_today}")
if mastered >= total * 0.6:
    print("🔧 高密度领域 — 切换到边缘狩猎模式")
    # 搜索策略: 聚焦 patch release / bugfix / regression
```

### 3. 搜索关键词生成规则

从 KB 已知概念中逆向推导搜索优先级：

```
已知概念的关键词列表 → 从搜索词中排除（避免重温）
                         ↓
搜索词 = 最新版本号 + "rc" / "beta" / "regression" / "revert" / "CVE" / "deprecation"
```

**示例**（dev_tools 领域，2026-05-12）：
- KB 已有 `python3.15_lazy_imports` → 不需要搜 "Python 3.15 features"
- 但 KB 没有 `python3.14_gc_revert` → 搜 "Python 3.14.5 GC regression revert" → **命中！**

### 4. 质量分调整

边缘狩猎模式下，质量评分标准微调：

| 维度 | 常规模式 | 边缘狩猎模式 |
|:----|:--------|:------------|
| 信息覆盖度 | 要求覆盖 4+ 子主题 | 允许聚焦 1-2 个具体变更 |
| 交叉验证 | ≥2 来源 | 官方单来源可接受（patch note） |
| 可操作性 | 要求完整操作步骤 | 允许只记录影响和迁移建议 |
| 结构完整度 | 5 章齐全 | 可压缩为 3 章 |

**通过门槛不变**（raw ≥ 60），但搜索效率提升：用更少的时间覆盖更多的领域边际。

## 配套的 KB 更新策略

边缘狩猎发现的通常是「微小但重要」的变更：

| 发现类型 | KB 操作 | 示例 |
|---------|---------|------|
| Bugfix/安全修复 | 更新现有概念的 key_points | Python 3.14.5 GC revert |
| 性能微调 | 更新数值、追加来源 | JIT 6-7% → 8-9% |
| 版本状态更新 | 更新版本号和日期 | Rust 1.96 P-critical regression |
| 弃用提醒 | 新建 concept + 链接父概念 | Ingress NGINX retirement |

**不建新概念的条件**：如果变更只影响已有概念的数值/状态/日期，只更新 key_points，不创建新概念。避免概念膨胀。

## 实战验证

### dev_tools 领域 (2026-05-12)
- 已有概念: 92, mastered: ~60%, 今日 session: 3
- 传统搜索会得到大量已知信息
- 边缘搜索发现: Python 3.14.5 GC revert (增量→分代回退) — 运营关键变更
- 结果: 1 新概念 + 3 个已有概念更新, Q=90

### ai_tech 领域 (2026-05-05)
- 已有概念: 68, mastered: ~55%, 今日 session: 1
- 边缘搜索发现: GPT-5.5-Cyber 安全专用模型 (官方公告)
- 结果: 2 新概念, Q=89

---

**来源**：2026-05-12 dev_tools 知识库回访实践
