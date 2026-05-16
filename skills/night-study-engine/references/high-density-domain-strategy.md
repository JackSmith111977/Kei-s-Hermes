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

**⚠️ 补充：高成熟度但概念数少的领域** — 当 mastered ≥ 80% 且概念总数 < 50 时，边缘狩猎同样合适。因为核心知识已完全掌握，广度搜索只会重复已有内容。这种「小但精」的领域常见于研究型话题（如 Context Engineering 这类新兴学科），应优先搜索：学术界新论文、行业整合实践、交叉验证性文章。

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
open_q_count = len(kb.get('open_questions', []))

print(f"Total:{total} Mastered:{mastered} Developing:{developing} New:{new_count} Due:{due_today}")
print(f"Open questions: {open_q_count}")
if mastered >= total * 0.6:
    print("🔧 高密度领域 — 切换到边缘狩猎模式")
    # 搜索策略: 聚焦 patch release / bugfix / regression
```

**🆕 新增检查：开放问题对齐** — 记录 `open_q_count`，在搜索和提炼阶段**检查新发现是否回答了任何开放问题**。如果发现某个新信息来源回答了开放问题，在 KB 更新时同步更新该问题的 `status` 和 `answer_preview`。

### 3. 搜索关键词生成规则

从 KB 已知概念中逆向推导搜索优先级：

```
已知概念的关键词列表 → 从搜索词中排除（避免重温）
                         ↓
搜索词 = 最新版本号 + "rc" / "beta" / "regression" / "revert" / "CVE" / "deprecation"
```

对于**研究型话题**（如连版本号都不存在的架构概念），关键词生成规则调整为：

```
已知概念的关键词列表 → 从搜索词中排除
                         ↓
搜索词 = 领域名 + 最新领域进展关键词
         "new developments" / "2026 May" / "latest" / "production" /
         "enterprise" / "benchmark" / "conference"
```

**示例**（productivity 领域，2026-05-13）：
- KB 已掌握 "Context Kubernetes 7 services" → 不需要搜 "What is Context Kubernetes"
- 但 KB 没有 "ServiceNow Context Engine" → 搜 "ServiceNow context engineering 2026" → **命中！**

### 4. 搜索后的开放问题对齐

边缘狩猎发现的可能回答了 KB 中的开放问题：

| 开放问题状态 | 发现类型 | 处理方式 |
|:-----------|:---------|:---------|
| **新发现完全回答** | 搜索命中明确匹配 | 设置 `status: "answered"` + 填充 `answer_preview` |
| **新发现部分回答** | 搜索命中间接证据 | 设置 `status: "partially_answered"` + 填充 `answer_preview` |
| **无关联** | 搜索无相关结果 | 保持原状 |

**🆕 建议流程**：提炼阶段后半段（R3 之前）增加一个检查步骤：
1. 遍历 KB 的 `open_questions` 数组
2. 逐一对照新发现的核心结论
3. 若匹配 → 更新问题状态 + 记录来源引用
4. 在 session_log 中记录开放问题更新数量

### 5. 质量分调整

边缘狩猎模式下，质量评分标准微调：

| 维度 | 常规模式 | 边缘狩猎模式 |
|:----|:--------|:------------|
| 信息覆盖度 | 要求覆盖 4+ 子主题 | 允许聚焦 1-2 个具体变更，但需包含开放问题对齐检查 |
| 交叉验证 | ≥2 来源 | 官方单来源可接受（patch note），但新概念需验证 |
| 可操作性 | 要求完整操作步骤 | 允许只记录影响和迁移建议 |
| 结构完整度 | 5 章齐全 | 可压缩为 3 章，但开放问题对齐部分不可省略 |

**通过门槛不变**（raw ≥ 60），但搜索效率提升：用更少的时间覆盖更多的领域边际。

**🆕 开放问题对齐奖励分**：如果本次边缘狩猎回答了 ≥1 个开放问题，在 operability 维度 +5 分奖励。

## 配套的 KB 更新策略

边缘狩猎发现的通常是「微小但重要」的变更：

| 发现类型 | KB 操作 | 示例 |
|---------|---------|------|
| Bugfix/安全修复 | 更新现有概念的 key_points | Python 3.14.5 GC revert |
| 性能微调 | 更新数值、追加来源 | JIT 6-7% → 8-9% |
| 版本状态更新 | 更新版本号和日期 | Rust 1.96 P-critical regression |
| 弃用提醒 | 新建 concept + 链接父概念 | Ingress NGINX retirement |

**不建新概念的条件**：如果变更只影响已有概念的数值/状态/日期，只更新 key_points，不创建新概念。避免概念膨胀。

**🆕 开放问题更新**：如果新发现回答了开放问题，在 KB 更新时同步修改 `open_questions` 数组中的对应条目。

### ⚠️ 跨会话概念重复（新增坑 — 2026-05-15 ai_tech 实测）

边缘狩猎可能由多个 cron 轮次独立运行。**概念可能已被同一日的其他会话添加**。本会话中就出现了 `openai_daybreak` 已存在的情况。

| 问题 | 表现 | 影响 |
|:----|:-----|:-----|
| **概念重复** | 尝试添加 `openai_daybreak` 但 KB 中已存在（置信度 0.85, monitoring 状态） | `already_exists` — 跳过新增，浪费一次工具调用 |
| **信息丢失** | 本会话发现的新信息（Daybreak 三层模型、8 家合作伙伴）未合并到已有概念 | 重要信息散落在不同会话中，旧概念 notes 未更新 |
| **状态不一致** | 旧概念 `monitoring`（未 mastering），但新信息已足够支撑 mastering | mastering 进度被拖延 |

**缓解策略**：

```python
# 添加概念前检查是否已存在
if name in kb["concepts"]:
    # 不跳过 —— 检查是否有新信息需要补充
    existing = kb["concepts"][name]
    new_info = {...}  # 你发现的新信息
    if "关键新信息" not in existing.get("notes", ""):
        existing["notes"] += "\n[跨会话补充] " + new_info
        existing["confidence"] = min(1.0, existing.get("confidence", 0.5) + 0.05)
        print(f"🔄 扩展已有概念: {name}（追加跨会话发现）")
    else:
        print(f"⏭️  已有概念 {name} 已包含最新信息")
else:
    kb["concepts"][name] = new_concept_data
```

**根因**：同一领域被多个 cron 轮次调度（如 ai_tech 每 2 小时可调度一次），搜索词可能在不同轮次命中相同的「新发表事件」。第一次添加后，第二次再搜到同一事件时会尝试重复添加。

**预防**：KB 更新前先 `name in kb["concepts"]` 检查，对已存在概念采用「追加 notes」而非「跳过」策略。这样跨会话发现的信息能自然合并到同一个概念条目中。

### 🆕 定向 developing 概念并行搜索模式（2026-05-16 新增）

当高密度领域的 developing/new 概念积压（≥5 个）且需要更新时，不要逐个顺序搜索——使用**批量并行**搜索模式：

#### 适用条件
| 条件 | 阈值 |
|:----|:----:|
| mastered 占比 | ≥ 60%（高密度领域） |
| developing/new 概念数 | ≥ 5 |
| 今日已有 session 数 | < 2 |

#### 流程

```text
[边缘狩猎开始]
  │
  ├─ ① 从 KB 读取所有 developing/new 概念列表
  │
  ├─ ② 按主题聚类（如「Google 系」「Anthropic 系」「架构论文」「MCP 生态」）
  │
  ├─ ③ 每聚类发起 1 次并行 web_search（最多 4-5 个并行请求）
  │     搜索词 = "{概念名} 2026 latest update"
  │
  ├─ ④ 综合分析搜索结果
  │     ├─ 有显著新信息 → 升级状态（developing→mastered）
  │     ├─ 部分新信息 → 扩展 notes，提升置信度
  │     └─ 无新信息 → 保持原状，推进复习日期
  │
  └─ ⑤ 批量更新 KB（一次 execute_code 完成所有更新）
```

#### 执行示例（2026-05-16 ai_tech）

| 搜索轮次 | 聚类 | 并行数 | 命中 | 结果 |
|:-------:|:----:|:------:|:----:|:----:|
| 第 1 轮 | Adaption/Cisco | 2 | 5/5 ✅ | AutoScientist GA, Foundry OSS |
| 第 2 轮 | Gemini 系列 | 2 | 5/5 ✅ | 3.2 Flash leak, Omni leak |
| 第 3 轮 | SubQ/MCP 生态 | 2 | 5/5 ✅ | SubQ launch, Bifrost v1.4.0 |
| 第 4 轮 | Anthropic/Zyphra | 2 | 5/5 ✅ | NEC/PwC deals, ZAYA1-8B |

**结果**: 9 个概念全部更新，8 个 developing→mastered 升级。4 批搜索共 ~38 来源，Q=92。总工具调用 ~15 次（9 搜索 + 4 提取 + 2 KB 更新），而非逐个概念搜索的 20+ 次。

#### 关键技巧
- **搜索词要精准**：`"{项目名} 2026 latest update"` 避免重温已知知识
- **先聚类再搜索**：同一公司/生态的概念放一起搜，减少重复结果
- **批量更新**：所有发现汇总后一次性写入 KB JSON（用 `execute_code` + Python dict），避免多次小 I/O
- **Tavily 配额管理**：边缘狩猎通常需要 4-8 次搜索。若 Tavily 配额紧张，直接用 `web_search`（本 session 验证：9 次 web_search 全部成功，Q=92）

#### 与其它搜索模式的关系
| 模式 | 适用 | 概念数 | 每批搜索数 |
|:----|:----|:------:|:---------:|
| 广度扩张（multi-topic） | mastered ≤ 60% | 3-5 新/轮 | 3-4 并行 × 3 轮 |
| **定向 developing 并行（本文案）** | mastered ≥ 60% + dev backlog ≥ 5 | 全部 dev 概念 | 4-5 并行 × 1-2 轮 |
| L1 批量复习（Red Flag #25） | 到期概念 ≥ 15 | 到期概念 | 按主题聚类 2-3 轮 |

---

## 实战验证

### ai_tech 领域 (2026-05-15) — 🆕 跨会话概念重复验证
- 已有概念: 66, mastered: 85%, 今日 session: 第 1 轮
- 搜索发现: OpenAI Daybreak（但概念已存在）, Cisco Foundry（新）, SAP+Anthropic（新）, Gemini 3.2 Flash leak（新）, Gemini Omni（新）
- 处理: 4 新概念 + 4 已存在概念 notes 扩展 + 2 到期复习
- Q=86, 跨会话重复捕获并正确处理

### dev_tools 领域 (2026-05-12)
- 已有概念: 92, mastered: ~60%, 今日 session: 3
- 传统搜索会得到大量已知信息
- 边缘搜索发现: Python 3.14.5 GC revert (增量→分代回退) — 运营关键变更
- 结果: 1 新概念 + 3 个已有概念更新, Q=90

### ai_tech 领域 (2026-05-05)
- 已有概念: 68, mastered: ~55%, 今日 session: 1
- 边缘搜索发现: GPT-5.5-Cyber 安全专用模型 (官方公告)
- 结果: 2 新概念, Q=89

### productivity 领域 (2026-05-13) — 🆕 高熟度低数量案例
- 已有概念: 29, mastered: 90% (28/29), 今日 session: 0
- 概念数 < 50 但 mastered > 80% → 边缘狩猎同样适用
- 开放问题: 19 个（部分可回答的新发现）
- 搜索方向: GraphRAG 新基准 / Context Engineering 企业实践 / Obsidian MCP 新项目
- 发现: FalkorDB SDK 1.0 (#1 benchmark)、A-RAG 框架、ServiceNow Context Engine 4 Graph 架构（验证 CK 企业可行性）、Opcito 5 个 Agentic CE 模式
- 更新: 3 概念复习 + 4 notes 扩展 + 1 概念升级 mastered, Q=86

---

**来源**：2026-05-12 dev_tools 知识库回访实践 + 2026-05-13 productivity 边缘狩猎实践
