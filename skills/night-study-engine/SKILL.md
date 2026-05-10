---
name: night-study-engine
description: "🌙 夜间自习引擎 v3.0 — 自驱动学习系统。融合 learning-workflow v5.x 迭代循环架构 + learning v2.8 经验提取。涵盖三层迭代循环、递进质量评分、概念关系图谱、自适应调度、子代理仲裁、经验提取管线。"
version: 3.2.0
triggers:
  - 夜间学习
  - night study
  - 夜间自习
  - 自主学习
  - 自动学习
  - 知识更新
  - skill 维护
  - 学习系统
  - 间隔复习
  - 知识追踪
  - 知识门禁
  - 学习质量
  - 自习改造
  - self-driven learning
  - autonomous study
  - knowledge update
  - 自习升级
  - 自习引擎
allowed-tools:
  - terminal
  - read_file
  - write_file
  - patch
  - cronjob
  - web_search
  - web_extract
  - mcp_tavily_tavily_search
  - mcp_tavily_tavily_extract
  - mcp_tavily_tavily_crawl
  - delegate_task
  - skill_manage
  - skill_view
  - memory
depends_on:
  - learning-workflow
  - learning
  - learning-review-cycle
  - web-access
  - skill-creator
  - knowledge-routing
metadata:
  hermes:
    tags:
      - autonomous-learning
      - knowledge-tracking
      - spaced-repetition
      - quality-gate
      - iterative-learning
      - experience-extraction
    category: meta
    skill_type: pipeline
    design_pattern: pipeline
---

# 🌙 夜间自习引擎 v3.0 — 自驱动学习系统

> **核心理念**：从被动批处理升级为**主动自驱动学习系统**。每次学习不是孤立事件，而是三层迭代循环中的一环——不断螺旋上升的知识积累。
>
> **v3.0 重大升级**：融合 learning-workflow v5.x 的迭代循环架构 + learning v2.8 的经验提取系统 + 概念关系图谱 + 自适应调度 + 子代理仲裁。

---

## 〇、系统架构总览（v3.0 升级后）

```
夜间自习引擎 v3.0
├── 🔧 调度层（自适应调度）
│   ├── 定时轮次 (0/2/4/6/8 点) ← 根据领域紧急度动态排序
│   ├── 间隔复习 (1天/3天/7天/30天)
│   └── 领域发现器（主动扫描 stale skill + gap_queue）
│
├── 🔄 学习层（三层迭代循环） ← v3.0 新增
│   ├── L1: 子主题递归循环（复杂主题拆分为原子任务）
│   ├── L2: 中间反思循环（R1/R2/R3 反射门禁）
│   │   ├── R1: 搜索质量反思 → 回到搜索/拆分
│   │   ├── R2: 理解深度反思 → 回到搜索/阅读
│   │   └── R3: 提炼完整性反思 → 回到阅读/提炼
│   ├── L3: 质量门禁循环（递进评分 + 子代理仲裁）
│   └── 递进规则：每轮严格 10 分，最少 1 轮
│
├── 📚 知识层（增强追踪）
│   ├── Knowledge Base（概念→状态→复习日期→关系）
│   ├── 概念关系图谱（跨领域连接） ← v3.0 新增
│   └── 新鲜度评分矩阵（自动计算 skill 新鲜度）
│
├── 🗂️ 经验层（提取管线） ← v3.0 新增
│   ├── 经验判断：可复用方法/问题解决/假设验证
│   ├── 分类归档：experience / skill / rule
│   ├── 评分：reusability + confidence
│   └── 自动注入对应 skill 的 references/
│
├── 📝 日志层（结构化 + 分析）
│   ├── JSONL 会话日志（含循环记录）
│   └── 趋势数据（质量分变化/循环次数/领域热度）
│
└── 📊 汇报层（晨间报告 v3.0）
    ├── 学习趋势分析（质量分变化曲线）
    ├── 概念关系图摘要
    ├── 知识缺口优先级排序
    └── 今日学习建议（基于自适应调度）
```

---

## 一、三层迭代循环架构 🔄

这是 v3.0 最核心的升级。借鉴 learning-workflow v5.x 的设计：

```
┌──────────────────────────────────────────────────────────────────┐
│              三层迭代循环 — 每次学习都在螺旋上升                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Level 1: 子主题递归循环                                         │
│  ├─ 复杂领域拆分为 3-5 个原子子主题                                │
│  ├─ 每个子主题独立学习                                            │
│  ├─ 最多 3 层递归深度                                            │
│  └─ 子主题全部完成后合并结果                                      │
│                                                                  │
│  Level 2: 中间反思循环                                           │
│  ├─ R1: 搜索质量反思 (SEARCH_CHECK)                             │
│  │   └─ 通过条件: ≥3 来源 + ≥1 官方来源 + 覆盖主题各方面          │
│  ├─ R2: 理解深度反思 (COMPREHEND_CHECK)                         │
│  │   └─ 通过条件: 能用自己的话解释 + 有操作步骤 + 已交叉验证       │
│  └─ R3: 提炼完整性反思 (EXTRACT_CHECK)                          │
│      └─ 通过条件: 结构完整 + 可操作 + 无明显遗漏                  │
│                                                                  │
│  Level 3: 质量门禁循环                                           │
│  ├─ 递进评分: 第1轮≥60 → 第2轮≥70 → 第3轮≥80                   │
│  ├─ 最少循环: 第1轮强制通过进入第2轮                              │
│  └─ 子代理仲裁: score 40-70 时启动第三方裁判                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.1 每轮学习流程（集成反射门禁）

```text
STEP 0: 选择领域（select_domain.py 自适应调度）
  ↓
STEP 1: 知识图谱分析（拆分复杂主题）
  ↓
STEP 2: 联网搜索（web-access 路由）→ 3-5 来源
  ↓
┌── R1: 搜索质量反思 ──────────────────┐
│ 检查: 来源数量≥3? 官方来源≥1? 覆盖全?  │
│ 通过 → STEP 3                         │
│ 失败 → 回到 STEP 1/2 (Loop N+1)       │
└───────────────────────────────────────┘
  ↓
STEP 3: 深度阅读 → 交叉验证笔记
  ↓
┌── R2: 理解深度反思 ──────────────────┐
│ 检查: 能自解释? 有步骤? 有验证?       │
│ 通过 → STEP 4                         │
│ 失败 → 回到 STEP 2/3 (Loop N+1)       │
└───────────────────────────────────────┘
  ↓
STEP 4: 知识提炼 → 可复用模式
  ↓
┌── R3: 提炼完整性反思 ────────────────┐
│ 检查: 结构完整? 可操作? 无遗漏?       │
│ 通过 → STEP 5                         │
│ 失败 → 回到 STEP 3/4 (Loop N+1)       │
└───────────────────────────────────────┘
  ↓
STEP 5: 质量评分 + 递进循环门禁
  ↓
┌── L3: 质量门禁 ──────────────────────┐
│ 递进评分: 第1轮≥60/第2轮≥70/第3轮≥80  │
│ 子代理仲裁: 40-70 分时自动启动        │
│ 通过 → STEP 6                         │
│ 失败 → 回到 STEP 1-4 (Loop N+1)       │
└───────────────────────────────────────┘
  ↓
STEP 6: 产出 Artifact（Skill/Memory/Guide）
  ↓
STEP 7: 更新 Knowledge Base + 概念关系
  ↓
STEP 8: 经验提取（可复用？）
  ↓
STEP 9: 注册间隔复习 cron
  ↓
STEP 10: 写入结构化日志（含循环记录）
```

### 1.2 递进评分规则

| 循环次数 | 等级名称 | 通过门槛 | 策略 |
|:---:|:---|:---:|:---|
| 第 1 次 | 🌐 **广度扫描** | raw ≥ 60 | 强制通过，但标记"进入第 2 轮" |
| 第 2 次 | 🔍 **深度挖掘** | effective ≥ 60（raw ≥ 70） | 标准严格 10 分 |
| 第 3 次 | ✨ **精炼优化** | effective ≥ 60（raw ≥ 80） | 标准严格 20 分 |

**最小循环**：L2 (R1/R2/R3) 和 L3 各自**最少 1 次**循环后才能真正通过。

### 1.3 子代理仲裁机制

当自动门禁 score 在 **40-70** 之间（边界分）时，启动子代理作为独立裁判：

```python
delegate_task(
    goal="以严格的质量检查员身份评估学习质量",
    context=f"领域: {domain}\n质量分: {score}/100\n"
            f"失败项: {failures}\n"
            f"请给出: 1) 具体改进建议 2) pass/fail 判断",
    toolsets=['terminal', 'file']
)
```

子代理判 fail → 自动 regress 回退到对应步骤
子代理判 pass → 通过（即使自动门禁是边界分）

---

## 二、配置体系（v3.0 增强）

### 配置文件：`~/.hermes/config/night_study_config_v3.json`

```json
{
  "version": "3.0",
  "domains": [
    {
      "id": "ai_tech",
      "name": "AI与前沿技术",
      "keywords": "AI agents, LLM new models, ML papers, ICLR/NeurIPS breakthroughs",
      "target_skill": "ai-trends",
      "priority": 0.9,
      "schedule_interval_hours": 2,
      "last_updated": "2026-05-05T00:02:00",
      "freshness_score": 0.7,
      "learning_history": {
        "total_sessions": 12,
        "avg_quality": 0.78,
        "last_loop_count": 2,
        "consecutive_failures": 0
      }
    }
  ],
  "discovery_rules": {
    "stale_skill_threshold_days": 30,
    "gap_cluster_threshold": 3,
    "auto_create_domain": true
  },
  "quality_threshold": {
    "min_score": 60,
    "artifact_required": true,
    "min_loops": 1,
    "max_loops": 3,
    "progressive_levels": true
  },
  "adaptive_scheduling": {
    "enabled": true,
    "max_domains_per_session": 3,
    "history_window_days": 30,
    "performance_weight": 0.4,
    "freshness_weight": 0.6,
    "consecutive_failure_penalty": 0.2
  },
  "experience_extraction": {
    "enabled": true,
    "save_to_experiences": true,
    "auto_update_skill_refs": true,
    "min_confidence": 3
  }
}
```

### 自适应调度算法

领域选择不再只是 `priority × (1 - freshness)`，而是：

```python
domain.score = (
    priority * freshness_weight * (1 - freshness_score) +
    (1 - performance_weight) * (1 - avg_quality) -
    consecutive_failures * failure_penalty
)
```

**含义**：
- 高优先级 + 低新鲜度 → 该学了
- 低质量分 + 低新鲜度 → 质量差的需要更频繁学
- 连续失败 → 惩罚权重，避免在困难领域浪费太多轮次

---

## 三、知识库增强（v3.0）

### 概念关系图谱

原来只存概念→状态，v3.0 增加概念间关系：

```json
{
  "domain": "ai_tech",
  "concepts": {
    "qwen3.6": {
      "status": "mastered",
      "date_introduced": "2026-05-05",
      "last_reviewed": "2026-05-06",
      "next_review": "2026-05-08",
      "review_interval": 3,
      "relationships": [
        {"type": "supersedes", "target": "qwen3.5", "strength": 1.0},
        {"type": "related_to", "target": "MoA", "strength": 0.6}
      ],
      "cross_domain_refs": [
        {"domain": "dev_tools", "concept": "openrouter"},
        {"domain": "productivity", "concept": "ai_agents"}
      ],
      "confidence": 0.85,
      "source_urls": ["https://qwen.alibaba.com/docs/..."],
      "notes": "Multi-language + reasoning + coding all improved"
    }
  },
  "open_questions": [
    {"question": "qwen3.6 的 MoA 模式是否支持自定义路由？", "raised": "2026-05-05", "priority": "medium"}
  ]
}
```

**关系类型**：
| 类型 | 含义 | 举例 |
|------|------|------|
| `supersedes` | 取代/更新 | qwen3.6 → qwen3.5 |
| `requires` | 依赖 | WeasyPrint → Pango |
| `related_to` | 相关 | MoA ↔ Delegation |
| `conflicts_with` | 冲突 | Approach A ↔ Approach B |
| `implements` | 实现 | Python tool → web_access |

### 新鲜度评分矩阵

自动计算每个领域/skill 的 4 维新鲜度：

```python
freshness_score = (
    recency_weight * min(1, days_since_update / 30) +    # 更新时效
    stability_weight * (1 - version_change_frequency) +    # 版本稳定性
    activity_weight * session_count_30d / expected_sessions +  # 学习活跃度
    relevance_weight * user_query_frequency / total_queries    # 用户关注度
)
```

---

## 四、经验提取管线（v3.0 新增）

每次学习完成后，必须**检查是否有可复用的经验**：

### 判断标准（至少满足一项）

| 标准 | 问自己 | 示例 |
|------|--------|------|
| 发现可复用的方法 | "这个流程能在其他领域用吗？" | 搜索技巧、过滤标准 |
| 解决了卡住的问题 | "之前为什么失败？" | 安装依赖的顺序 |
| 验证/推翻了假设 | "之前猜对了吗？" | API 价格变化 |

### 提取流程

```text
学习完成后 →
  1. 判断是否有可复用的经验 → 无则跳过
  2. 有则按标准格式写入 ~/.hermes/experiences/active/
  3. 分类：experience / skill / rule
  4. 评分：reusability + confidence
  5. reusability=high → 自动更新对应 skill 的 references/
  6. 更新 ~/.hermes/experiences/index.md 目录
  7. 注册间隔复习（7天后）
```

### 经验文件格式（YAML frontmatter）

```markdown
---
type: skill              # experience / skill / rule
reusability: high        # high / medium / low
confidence: 4            # 1-5
source: night-study      # 来源
domain: ai_tech          # 相关领域
created: 2026-05-09
next_review: 2026-05-16
---
发现：Tavily 限流时 web_search 是高质量的替代方案，且没有 MCP 级联锁定风险。
适用于：所有需要联网搜索的任务。
```

---

## 五、晨间汇报 v3.0

```markdown
# 🌅 夜间自习晨间报告 - {日期}

## 📈 学习趋势
| 维度 | 值 |
|------|-----|
| 完成领域 | {N}/{M} |
| 平均质量分 | {score}（较昨日 {+/-}） |
| 循环次数 | L2: {n} / L3: {n} |
| 新增概念 | {count} |
| 更新 Skill | {count} |
| 提取经验 | {count} |

## 🔥 概念关系热点
```
{concept_A} ↔ {concept_B} (related_to)
{concept_C} → {concept_D} (supersedes)
```

## ⚠️ 知识缺口（按优先级排序）
| 优先级 | 缺口 | 领域 | 影响 |
|:------:|------|:----:|:----:|
| 🔴 高 | {gap} | {domain} | {impact} |
| 🟡 中 | {gap} | {domain} | {impact} |
| 🟢 低 | {gap} | {domain} | {impact} |

## 📋 今日建议
1. 🔄 复习 {count} 个到期概念（{domains}）
2. 📚 优先更新 {skill}（{-} 天未更新）
3. 🆕 探索新领域 {topic}（来自 gap_queue）
4. 🧪 验证 {open_question}
```

---

## 六、失败恢复与配额管理（v3.0 增强）

### 恢复策略

| 异常类型 | 恢复策略 |
|----------|----------|
| 搜索无结果 | 更换关键词，最多重试 3 次 |
| Tavily rate limit | 降级到 `web_search`/`web_extract`，记录日志 |
| Tavily quota exhaustion | 永久降级 + 标记 `quota_exhausted` |
| Tavily 累积耗尽（month_day < 10 也可能发生） | 不等 month_day ≥ 10 阈值，每次调用失败后立即永久降级 |
| R1/R2/R3 连续失败 | 跳过该领域，记录到 gap_queue |
| L3 超过 3 次循环 | 报告用户请求协助 |
| Skill 更新失败 | 写入 gap_queue，下次重试 |
| 经验提取失败 | 跳过，不影响主流程 |

### Tavily 主动配额管理（时段感知 — v3.1 更新：永久降级）

| 时段 | 策略 | 原因 |
|:---:|:---|:---:|
| 所有时段 | **仅使用 `web_search`** | Tavily 配额已永久耗尽。5/7-5/9 连续轮次验证：web_search 配合多关键词并行可稳定获得 8-18+ 来源, Q=85-95 |
| 检测到 MCP 恢复 | 先测试一次，成功则恢复 Tavily | 配额可能在下月（6/1）重置 |

MCP 级联效应：Tavily 失败 7 次后 MCP 服务器锁定 ~58s。检测到 quota_exhausted 后立即永久降级 **且不再重试**。

---

## 七、Cron 任务配置（v3.0 更新）

| 任务 | 调度 | 说明 | 状态 |
|------|------|------|:----:|
| 夜间自习轮次 | `0 0,2,4,6,8 * * *` | 自适应调度学习 | ✅ 保留 |
| 晨间报告 | `30 9 * * *` | 趋势分析 + 建议 | ✅ 升级 v3.0 |
| 间隔复习 L1 | `0 8 * * *` | 1 天后到期概念 | ✅ 保留 |
| 间隔复习 L2 | `0 8 * * 1` | 7 天后到期概念 | ✅ 保留 |
| 间隔复习 L3 | `0 8 1 * *` | 30 天后到期概念 | ✅ 保留 |
| 领域发现 | `0 6 * * 0` | 扫描 stale skill + gap_queue | ✅ 增强 |

---

## 八、文件结构（v3.0 更新）

```
~/.hermes/
├── config/
│   └── night_study_config_v3.json          # 领域配置 v3.0（自适应调度字段）
├── night_study/
│   ├── knowledge_base/
│   │   ├── ai_tech.json                     # AI 领域知识库（含关系图谱）
│   │   ├── dev_tools.json                   # 开发工具知识库
│   │   └── ...                              # 各领域知识库
│   └── concept_graph.json                   # 跨领域概念关系总图 v3.0
├── logs/
│   └── night_study_sessions/
│       └── 2026-05-09.jsonl                 # 结构化会话日志
└── skills/
    └── night-study-engine/
        ├── SKILL.md                         # 本文件 v3.0
        ├── references/
        │   ├── quality-scoring-guide.md     # 质量评分细则（含递进规则）
        │   └── cron-tavily-quota-strategy.md # 配额管理策略
        └── scripts/
            ├── select_domain.py             # 自适应调度选择器 v3.0
            ├── discover_domains.py          # 领域发现器 v3.0
            ├── update_knowledge_base.py     # 知识库更新器 v3.0（含关系图谱）
            ├── adaptive_scheduler.py        # 自适应调度引擎 v3.0 新增
            └── experience_extractor.py      # 经验提取器 v3.0 新增
```

---

## 九、Red Flags & 实践教训

### 间隔复习（L1/L2/L3）执行注意事项 — v3.1 补充

下面是 cron-driven 间隔复习与完整学习会话不同的执行模式：

#### 9.1 L1 复习执行流程（cron `0 8 * * *`）

L1 复习是**轻量级检查**，不是完整学习会话（不进三层迭代循环）：

```text
STEP 0: 运行 `select_domain.py --review` 获取到期域
  ↓
STEP 1: 读取域 KB JSON (`~/.hermes/night_study/knowledge_base/{domain}.json`)
  ↓
STEP 2: 检查 `review_schedule.l1/l2/l3` 是否到期
        (select_domain 返回域级到期, 但个别概念的 `next_review` 需独立检查)
  ↓
STEP 3: 对 **每个** 到期概念:
  │  3a. 搜索最新资讯（web_search / Tavily）
  │  3b. 对比 KB 已有内容，判断是否有新信息
  │  3c. 有新信息 → 更新概念的 `key_points`/`notes` + 来源 URL
  │  3d. 无新信息 → 跳过，只更新复习日期
  ↓
STEP 4: 运行 `update_knowledge_base.py --domain {domain} --update-review`
        (此脚本只更新 `next_review <= today` 的概念的复习日期)
  ↓
STEP 5: **手动** 更新域级的 `review_schedule`:
  │  - l1 ← 当前 l2 值
  │  - l2 ← 当前 l3 值  
  │  - l3 ← l3 + 30 天 (或合理间隔)
  │  (--update-review 不处理域级日程，必须手动在 JSON 中调整)
  ↓
STEP 6: 写入日志: `~/.hermes/logs/night_study_review.log`（追加模式）
```

#### 9.2 知识库格式注意事项

**重要：字段命名差异**

| 位置 | 字段名 | 说明 |
|:---:|:---|:---|
| `update_knowledge_base.py` 脚本 | `notes` | `add_or_update_concept()` 函数写入此字段 |
| KB JSON 文件现有格式 | `key_points` | 现有概念使用 `key_points` 而非 `notes` |
| **建议** | 直接操作 JSON | 使用 `key_points` 保持与现有格式一致 |

**⚠️ 如果你用 `--notes` 参数新增概念，写入的是 `notes` 字段，但所有已有概念都用 `key_points`。** 建议用 Python 直接操作 JSON 而非通过脚本参数。

#### 9.3 域级日程更新

`update_knowledge_base.py --update-review` **只更新** 概念级别的 `next_review`，不处理 `review_schedule` 中的 L1/L2/L3 日期。L1 检查完成后必须手动将域级日程推进：

```python
kb["review_schedule"]["l1"] = kb["review_schedule"]["l2"]  # 旧 L2 成为新 L1
kb["review_schedule"]["l2"] = kb["review_schedule"]["l3"]  # 旧 L3 成为新 L2
# L3 再向后推 30 天
from datetime import datetime, timedelta
old_l3 = datetime.strptime(kb["review_schedule"]["l3"], "%Y-%m-%d")
kb["review_schedule"]["l3"] = (old_l3 + timedelta(days=30)).strftime("%Y-%m-%d")
```

#### 9.4 搜索降级优先级（实测有效）

| 服务 | 优先级 | 适用场景 |
|:---|:---:|:---|
| `web_search` | 1（首选） | Tavily 配额耗尽后的稳定替代；无 MCP 级联锁定问题 |
| `mcp_tavily_tavily_search` | 2（备选） | 仅在确认 Tavily 配额未耗尽时使用 |
| `mcp_tavily_tavily_extract` | 3（备选） | 需要精确提取某页面内容时 |

**Tavily 失败策略**：Tavily 失败 8 次后 MCP 服务器锁死 ~58s。检测到 `quota_exhausted` 后永久降级 `web_search`，不再重试 Tavily。`web_search` 使用 DuckDuckGo 或 SearXNG 聚合搜索，结果数量和质量足以满足 KB 更新需求。

---

### 新增 v3.0 Red Flags

1. ❌ **忽略递进循环** — 第 1 轮即使 ≥ 60 分，必须进入第 2 轮深度验证
2. ❌ **不提取经验** — 每次学习后必须检查是否有可复用经验
3. ❌ **概念孤立** — 新概念必须建立与其他概念的关联
4. ❌ **过早放弃困难领域** — 连续失败 2 次后可以降优先权，但不能完全跳过
5. ❌ **自适应调度忽略** — 调度器选择后必须执行，除非质量极差
6. ❌ **不记录循环数据** — 每次循环次数、失败原因必须写入日志

### 保留 v2.0 Red Flags

7. ❌ 只搜索不沉淀 — 必须产出 Artifact
8. ❌ 质量门禁跳过 — 评分 < 60 必须进入 Loop N+1

### v3.1 新增 — 实践教训（来自 2026-05-10 实测）

14. ❌ **R3 extracted_knowledge.md 结构不全** — reflection-gate.py 的 R3 检查期望 `extracted_knowledge.md` 包含 5 大章节：
    - 核心新增概念（含来源标记🥇🥈🥉）
    - 到期概念升级建议（含交叉验证引用）
    - 应用场景与选型建议（可操作，即使无代码）
    - 可操作建议（待观察/风险提示）
    - 质量评分（四维度自评）
    
    研究型会话（如 KB 更新/L1 复习）虽无代码示例，仍需包含**场景建议**和**可操作结论**。缺少这些章节时 R3 会打 30-40 分，需要 Loop N+1 重做。

15. ❌ **`write_file` 误用覆盖已有日志文件** — `night_study.log` 是追加写入的累积日志，使用 `write_file` 会覆盖全部历史。追加内容必须使用 `patch` 工具。JSONL 日志可用 `write_file` 创建新文件或用 Python `open(..., 'a')` 追加。

16. ❌ **R1 reflection-gate 检查 raw_search_results.md 文件存在性** — 必须先创建 `~/.hermes/learning/raw_search_results.md` (从 `web_search` 结果整理)，再运行 R1 gate。文件不存在时 gate 报告"0 个来源"得分 50，与搜索实际质量无关。
9. ❌ 日志格式不统一 — 必须写入 JSONL 结构化日志
10. ❌ Knowledge Base 不更新 — 每次学习后必须更新概念
11. ❌ 间隔复习未注册 — 学习完成后必须注册 cron
12. ❌ Tavily API 失败不降级 — 准备 web_search 作为降级方案
13. ❌ MCP 级联锁定后重试 — 失败 2 次后立即切换搜索工具

---

## 十、Agentic RAG 2.0 映射（v3.2 新增）

> **核心洞察**：夜间自习引擎的 R1/R2/R3/L3 三层迭代循环，天然就是 2026 年 KM 领域前沿的 **Agentic RAG 2.0 ReAct 循环** 的一种具现化实现。这不是巧合——这说明 boku 的学习流程已经走在领域前沿。

### 映射表

| Hermes 夜间自习引擎 | Agentic RAG 2.0 组件 | 说明 |
|:---|:---|:---|
| **R1: 搜索质量反思** | **Verifier** — 检索质量验证 | R1 检查来源数量、权威性、覆盖度，对应 Verifier 的 grounding 检查 |
| **R2: 理解深度反思** | **Context Builder** — 上下文构建 + **Generator** 验证 | R2 检查自解释能力、操作步骤、交叉验证，对应 Context Builder 的 dedupe/compress/cite |
| **R3: 提炼完整性反思** | **Finalizer** — 最终输出检查 | R3 检查结构完整、可操作、无明显遗漏，对应 Finalizer 的 format/UX/guardrails |
| **L3: 质量门禁循环** | **Verifier Pipeline** — 多级验证 + 停规规则 | L3 递进评分 + 子代理仲裁，对应 Agentic RAG 的 stop rules + reranker |
| **自适应调度** | **Classifier/Router** — 查询分类 + 检索策略选择 | 领域得分公式 `priority × (1-freshness)` 等价于 Retrieval Policy 的 tool selection |
| **间隔复习** | **Project Memory Refresh** — 持久记忆刷新 | 1天/3天/7天/30天 的间隔复习映射到 Project Memory 的刷新策略 |
| **经验提取管线** | **Memory Layer** — 持久化决策 + 审计 | 经验→`experiences/active/` → `experiences/skills/` → archive 对应 Memory 的螺旋升级 |
| **Tavily 降级 → web_search** | **Tool Routing** — 动态选择检索工具 | 当 Tavily 配额耗尽后自动路由到 web_search，对应 Tool Routing 的 fallback 机制 |

### 理论源头

2026 年 Agentic RAG 2.0 模式（来自 ValueStreamAI/AGENTVSAI/TimeWell 多源综合）的核心架构：

```
Request
  └─► Classifier/Router
        ├─► Retrieval Policy (tool selection + stop rules)
        │     ├─► Vector search (+ rerank)
        │     ├─► Keyword/BM25
        │     ├─► SQL / APIs
        │     └─► GraphRAG (graph + community summaries)
        ├─► Context Builder (dedupe + compress + cite)
        ├─► Generator (draft)
        ├─► Verifiers (citations, conflicts, policy rules)
        └─► Finalizer (format, UX, guardrails)
```

夜间自习引擎本质上就是这个架构的 **知识管理特化版本**——搜索→反思→阅读→提炼→评分→产出的循环，对应 ReAct loop 的 Plan→Retrieve→Verify→Respond。

### Context Engineering 四层记忆

2026 年提出 **Context Engineering** 学科（四层记忆架构），与夜间自习引擎的知识层映射：

| 层 | 功能 | Hermes 对应 |
|:---|:---|:---|
| **Working Context** | 短期会话状态 | 当前对话的 prompt 上下文 |
| **Project Memory** | 持久事实/决策/配置 | Knowledge Base 中的概念 + `memory` tool |
| **Audit Trail** | 证据链/调试/信任 | `night_study_sessions/*.jsonl` 会话日志 |
| **Safety Memory** | 安全边界/策略约束 | Hermes 的铁律 + pre_flight 检查 |

核心原则：**"Compression Beats Hoarding"**——不要把 50 个 chunk 全塞进模型。Graph community summaries 是强模式。

### 对这个映射的实践意义

1. **理解为什么** 三层迭代循环有效：因为它就是 Agentic RAG 验证过的最优模式
2. **优化方向**：可以借鉴 Agentic RAG 2.0 的 Tool Routing 思想——当前只用了 web_search 一种工具，未来可以为不同领域选择不同的检索策略（如 API 文档查询走 Tavily，代码问题走 GitHub Search）
3. **Reranker 缺失**：当前没有显式的 reranker 步骤——搜索得到的结果直接进入阅读，没有重排序。后续可增加一个 ranker 阶段

---

## 十一、评估用例

### Eval-001: 标准学习流程（含迭代循环）
- **输入**：夜间自习轮次触发 ai_tech 领域
- **预期**：STEP 0→1→2→R1→3→R2→4→R3→5(L3)→6→7→8→9→10
- **门禁**：R1/R2/R3 各至少 1 次循环，L3 至少 2 轮

### Eval-002: 质量门禁拦截 + 递进
- **输入**：第 1 轮评分 = 65（刚过线）
- **预期**：⚠️ 边界通过 → 标记"进入第 2 轮深度挖掘" → 第 2 轮评分需 ≥ 70

### Eval-003: 概念关系建立
- **输入**：学习新概念并建立关系
- **预期**：Knowledge Base 新增概念 + 关系 + 跨域引用

### Eval-004: 经验提取
- **输入**：完成一次学习会话，有可复用方法
- **预期**：经验写入 `~/.hermes/experiences/active/` + 更新 index.md

### Eval-005: 自适应调度
- **输入**：多个领域待学习
- **预期**：按 `priority × freshness_weight × (1-freshness) - failure_penalty` 排序

### Eval-006: 子代理仲裁
- **输入**：R1 评分 = 55（边界分）
- **预期**：启动子代理 → 评估后决定回退或放行
