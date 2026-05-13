# 多主题广度域并行搜索策略

> 当一个领域覆盖多个松散耦合的子主题（如 dev_tools 覆盖 Python/TypeScript/Go/Rust/Web框架/IDE），单一搜索词无法有效覆盖。需要「多轮并行·发现驱动」的搜索策略。

## 适用场景

| 特征 | 判断标准 |
|:----|:---------|
| 领域子主题数量 | ≥ 4 个松散耦合子领域 |
| 概念总数 | ≥ 50（知识库已有较多内容） |
| mastered 占比 | ≤ 60%（尚未进入边缘狩猎模式，仍有大量空间） |
| 上次更新距今 | ≥ 24h（不是已高度饱和的领域） |

**与边缘狩猎策略的关系**：
- 边缘狩猎（high-density-domain-strategy.md）适用于 **mastered ≥ 60%** 时
- 本策略适用于 **mastered ≤ 60% 但概念总数已较大** 时 — 即"广度扩张期"
- 两者顺序：本策略 → 边缘狩猎（按领域成熟度递进）

## 搜索策略：三轮并行·发现驱动

### 第 1 轮：广度覆盖（3-4 个并行搜索）

不追求深度，先用多个角度探测最新动态：

| 搜索角度 | 示例关键词 | 预期产出 |
|:--------|:----------|:---------|
| **语言更新** | `2026 TypeScript Rust Go Python latest version May` | 语言版本线 |
| **框架/工具** | `2026 web framework build tool updates May` | 工具链动态 |
| **IDE/平台** | `2026 VS Code JetBrains IDE updates May` | 开发环境更新 |
| **新兴项目** | `2026 new programming languages developer tools` | 新技术信号 |

**数量要求**：每个搜索 8-10 个结果，总计 30-40 个候选 URL。

### 第 2 轮：定向深挖（2-3 个并行搜索）

从第 1 轮结果中识别热点，做针对性深度搜索：

```python
# 伪代码：第 2 轮搜索词生成
round1_results = analyze("raw_search_results.md")
hot_topics = extract_hot_topics(round1_results)
for topic in hot_topics:
    search(f"{topic} 2026 release announcement migration guide")
```

常见的热点方向：
- 发现版本发布 → 搜 `{version} release notes migration guide`  
- 发现工具重写 → 搜 `{tool} Rust rewrite performance benchmark`
- 发现新概念 → 搜 `{concept} documentation tutorial`

**数量要求**：每个搜索 5-8 个结果，找到官方文档。

### 第 3 轮：缺失填补（可选）

检查覆盖缺口：

```python
kb_topics = get_kb_topics()  # 已有概念的关键词
searched_topics = get_searched_keywords()
gaps = kb_topics - searched_topics  # KB 里有但本次没搜到的
if gaps:
    search(f"{gap} 2026 update news")
```

**目的**：不是追求全覆盖，而是避免"AI 领域已经更新过 3 次但 Go 语言因为 KB 里概念更多反而忘记更新"的偏差。

## 搜索量控制

| 领域总概念数 | 第1轮搜索数 | 第2轮搜索数 | 总来源数目标 |
|:----------:|:----------:|:----------:|:----------:|
| < 30 | 2 | 1-2 | 8-12 |
| 30-80 | 3 | 2-3 | 12-20 |
| 80+ | 3-4 | 2-3 | 15-25 |

**上限原则**：来源数不是目标，信息增益才是。如果在第 2 轮已经发现足够的差异化新知识点，不强制凑满来源数。

## 实战验证: dev_tools 领域 (2026-05-13)

### 领域状态
- 总概念: 92 → 100, mastered: 50% (50/100)
- 子主题: Python/TypeScript/Go/Rust/Web框架/IDE工具
- 上次更新: ~2 天前

### 执行记录

| 轮次 | 搜索数 | 来源数 | 发现 |
|:---:|:------:|:------:|:-----|
| 第1轮 - 语言 | 3 | ~30 | TS 7.0 Beta, Node.js 26, Python 3.15 Beta, Mojo 1.0 |
| 第1轮 - 工具 | 3 | ~18 | Vite 8 Rolldown, VS Code 1.119, Next.js 16 Turbopack |
| 第2轮 - 定向深挖 | 3 | ~15 | Oxc Rust 工具链, AWS Agent Toolkit, JetBrains ACP |
| 合计 | 9 | 63 候选 → 19 选用 | 8 新概念 + 3 关系更新 |

### 分析
- **有效命中率**: 19/63 = 30%（约 1/3 的结果被深度阅读）
- **官方来源占比**: 79% (15/19)
- **第2轮价值**: Oxc 和 AWS 的详细信息来自第2轮深挖，这两项是第1轮无法覆盖的
- **最佳实践**: 不在第1轮贪多求全，留出时间做第2轮定向深挖

## 混合模式：广度搜索 + 到期概念同步复习

在 **backlog 状态**（mastered ≤ 60% 且总概念 ≥ 50）的领域中，每次学习会话的最佳策略不是「只搜新」或「只复习」，而是**混合模式**：

### 流程

```text
[会话开始]
   │
   ├─ ① 识别到期概念（read KB JSON next_review ≤ today）
   │
   ├─ ② 并行广度搜索新内容（常规三轮并行）
   │
   ├─ ③ 按到期概念做定向搜索
   │     └─ 对每个到期概念：search("{concept_keyword} 2026 latest")
   │
   ├─ ④ 综合整理结果
   │     ├─ 新发现 → 新概念（注意限制数量）
   │     └─ 到期概念 → 更新 key_points 和 status
   │
   └─ ⑤ 状态升级（按间隔复习算法推进 next_review）
```

### 概念状态升级路线

| 来源 | 旧状态 | → 新状态 | 条件 |
|:----|:------:|:---------:|:----:|
| 到期复习 | new | developing | 复习后有确认信息 |
| 到期复习 | developing | mastering | 有官方来源佐证 |
| 到期复习 | mastering | mastered | 已有巩固的覆盖理解 |
| 新发现 | ∅ | new | 来自官方文档或权威来源 |
| 新发现 | new | developing | 信息从 ≥ 2 个独立来源验证 |

### 参考比例（经验值）

| KB 总概念 | 每个会话新增上限 | 到期概念复习数 |
|:--------:|:---------------:|:-------------:|
| < 50 | 5-8 | 全部到期（通常 2-5） |
| 50-100 | 3-5 | 全部到期（通常 5-10） |
| 100+ | 1-3 | 按优先级选择（5 个以内） |

**关键约束**：始终优先复习到期概念，有余力再加新概念。KB 膨胀而 mastered 率不升 = 知识债。

### 实战验证: dev_tools 领域 (2026-05-13 混合模式)

- KB 状态：100 概念，50% mastered (backlog 临界)
- 到期概念：5 个（k8s 相关 + ts7_beta + selinux）
- 新搜索：8 个方向（TS/Rust/Go/Python/K8s/Vite/Node.js/Kotlin+Swift）
- 产出：3 新增 + 7 更新（含 5 到期全部处理）
- 状态升级：`ts7_beta_go_rewrite` mastering→mastered, `k8s_sharded_list_watch` new→developing

## 已知陷阱

1. ❌ **第1轮搜索词太窄** — 如果只搜 `Python new features 2026` 会错过 IDE 工具链和 Rust 生态的变化
2. ❌ **跳过第2轮深挖** — 第1轮的搜索摘要往往只有标题，容易漏掉有价值的细节
3. ❌ **概念膨胀不自知** — 每次学习都加 5-10 个新概念而不提升旧概念的状态，会导致 KB 膨胀但 mastered 率下降
4. ❌ **来源过载** — 打开 30+ 个标签页不如精选 15-20 个深入阅读
5. ❌ **混合模式下忽视到期概念** — 新鲜内容太吸引人，容易把所有精力投到搜索新内容，到期概念简单「标记已读」了事。**必须真正搜索最新信息并更新**。

---

**来源**: 2026-05-13 dev_tools 学习实践 — 4 轮并行搜索 + 3 轮定向深挖，产出 8 新概念
