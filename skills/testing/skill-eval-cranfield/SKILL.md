---
name: skill-eval-cranfield
description: "基于 Cranfield 信息检索范式的 skill 推荐系统评估方法论。涵盖分层测试查询设计(L1-L5)、自动 Qrels 生成、量化指标(Recall/MRR/NDCG/Spurious)、基线对比、按难度分层报告。适用于需要量化评估推荐/匹配系统改进效果的场景。"
version: 1.0.0
author: Emma (小喵)
license: MIT
triggers:
  - eval
  - 评估
  - recall
  - mrr
  - ndcg
  - baseline
  - 基线
  - ground truth
  - qrels
  - 相关性判断
  - 测试框架
  - cranfield
  - 评估指标
  - 量化测试
  - 对照测试
metadata:
  hermes:
    tags:
      - evaluation
      - testing
      - information-retrieval
      - cranfield-paradigm
      - recommendation-system
      - benchmark
    category: testing
    skill_type: methodology
    design_pattern: pipeline
    related_skills:
      - skill-creator
      - systematic-debugging
---

# 🎯 Skill Eval Cranfield — Cranfield 范式的推荐质量评估

> **核心理念**：任何一个 skill 推荐/匹配系统的改进，都需要**量化、可复现、按难度分层**的评估来验证，而不是靠"测 4 个手动场景"来判断好坏。

---

## 一、为什么需要这套方法

### 常见问题

| 问题 | 表现 | 后果 |
|------|------|------|
| **只测几个场景** | "画架构图、设计数据库" | 无法代表全技能的分布 |
| **无 Ground Truth** | "应该推荐什么"纯靠人工判断 | 评估主观，不能自动化 |
| **无量化指标** | "改进前 52.8 vs 改进后 51.0" | 看不出整体是变好还是变差 |
| **无难度分层** | 简单和复杂场景混在一起 | 无法定位"哪个环节出了问题" |

### Cranfield 范式的答案

Cranfield 实验范式（1960s 至今，TREC 沿用）由三部分组成：
1. **文档集 (Corpus)** — 所有可推荐的对象（如 SKILL.md）
2. **查询集 (Topics/Queries)** — 精心设计的测试查询（按难度分层）
3. **相关性判断 (Relevance Judgments / Qrels)** — 每个查询应该推荐哪些对象

有了这三样，就能做**量化、可复现、自动化**的评估。

---

## 二、测试查询分层设计

### 五级难度 (L1-L5)

借鉴 Meta AI 的研究结论：**评估数据集若偏向简单查询，会高估 25-30% 的生产质量。**

| 层级 | 难度 | 定义 | 数量建议 | 示例 |
|------|------|------|---------|------|
| 🟢 **L1 精确匹配** | 简单 | skill 名称直接包含查询词 | 30% | "pdf" → pdf-layout |
| 🟡 **L2 同义映射** | 中等 | 需要同义词桥接的中文查询 | 30% | "幻灯片" → pptx-guide |
| 🔴 **L3 语义理解** | 困难 | 自然语言任务描述，需跨技能 | 20% | "帮我把设计稿做成能演示的PPT" |
| 🟣 **L4 多跳推理** | 极难 | 组合多个 skill 的任务 | 10% | "每天自动爬取新闻生成PDF报告" |
| ⚫ **L5 噪声检测** | 验证 | 无关查询不应推荐任何 skill | 10% | "今天天气怎么样" |

### 设计原则

1. **覆盖全技能** — 确保每个 skill 至少被 1 个查询覆盖
2. **代表性分布** — 反映真实用户的使用模式
3. **难度均衡** — 简单/困难按 3:3:2:1:1 比例
4. **可扩展** — 新加 skill 后只需追加对应查询

---

## 三、自动 Qrels 生成

### 从 Triggers 自动生成 Ground Truth

**关键洞察**：如果 skill 的 trigger 字段设计合理，它就是天然的 Ground Truth！

```python
def compute_relevance(query_expanded, skill):
    """
    多级相关性判断：
    - 2.0: 精确 trigger 匹配
    - 1.5: 部分 trigger 或类别匹配
    - 1.0: 名称或标签匹配
    - 0.5: 描述中包含关键词
    - 0:   不相关
    """
    triggers = [t.lower() for t in skill.get("triggers", [])]
    name = skill.get("name", "").lower()
    category = skill.get("category", "").lower()
    tags = [t.lower() for t in skill.get("tags", [])]

    for word in query_expanded:
        w = word.lower()
        if w in triggers:           return 2.0   # 精确触发
        for t in triggers:
            if w in t or t in w:    return 1.5   # 部分触发
        if w in name:               return 1.5   # 名称命中
        if w in tags or w in category: return 1.0 # 标签/类别命中
    
    # 描述中宽泛匹配
    desc = skill.get("description", "").lower()
    for word in query_expanded:
        if len(word) >= 3 and word in desc:
            return 0.5
    return 0
```

### 什么时候需要人工标注

- 当 skill 的 trigger 字段为空或不全时
- 当查询涉及**多 skill 组合**（L4 级别）
- 当需要精确比较两个相似系统的差异时

---

## 四、评估指标

### 4 个核心指标

| 指标 | 缩写 | 衡量什么 | 权重 |
|------|------|---------|:----:|
| **召回率@K** | Recall@K | "正确的 skill 被推荐的比例" | 30% |
| **平均倒数排名** | MRR | "第一个正确结果的位置" | 35% |
| **归一化折损累计增益** | NDCG@K | "推荐的排序质量" | 25% |
| **未经请求推荐率** | Spurious@K | "推荐了不相关 skill 的比例" | 10% |

### 综合得分公式

```python
Score = Recall@K × 0.30 + MRR × 0.35 + NDCG@K × 0.25 + (1 - Spurious@K) × 0.10
```

### 分难度加权

不同难度层级的重要性不同：

```python
总得分 = L1得分 × 0.20 + L2得分 × 0.35 + L3得分 × 0.30 + L4得分 × 0.10 + L5得分 × 0.05
```

这个权重反映：**同义映射和语义理解是最关键的改进方向**（因为它们最有优化空间）。

---

## 五、实施步骤

### Step 1: 设计测试查询

```
按 L1-L5 分层设计 60-100 个查询
每个查询记录: {query_id, query_text, expected_categories/expected_skills, level}
```

### Step 2: 自动生成 Qrels

```
读取所有 skill 的 triggers/metadata
对每个查询，计算它与每个 skill 的相关性
输出标准 Qrels 格式
```

### Step 3: 运行首次评估（基线）

```
对所有查询依次调推荐系统的 API
收集推荐结果列表
计算 4 个核心指标
保存基线结果
```

### Step 4: 改进后对比

```
对改进后的系统重复 Step 3
用 --compare 模式与基线自动对比
输出差异报告
```

### Step 5: 按难度分层分析

```
检查每层的变化：
- L1 退步了？→ 精确匹配环节出现问题
- L2 没有提升？→ 同义词扩展需要改进
- L3 还是差？→ 语义理解是最难突破的点
```

---

## 六、输出报告示例

```
╔════════════════════════════════════════════╗
║  SRA 推荐质量评估报告                      ║
╠════════════════════════════════════════════╣
║  综合得分:         58.7/100               ║
║  Recall@5:         0.450  ❌              ║
║  MRR:              0.689  ⚠️              ║
║  NDCG@5:           0.500  ❌              ║
║  Spurious@5:       0.142  (越低越好)      ║
╠════════════════════════════════════════════╣
║  按难度分层:                              ║
║  L1 精确匹配       : 64.2/100            ║
║  L2 同义映射       : 65.0/100            ║
║  L3 语义理解       : 42.0/100 ❌         ║
║  L4 多跳推理       : 63.4/100            ║
║  L5 噪声抑制       : 40.0/100            ║
╚════════════════════════════════════════════╝

📊 与上次对比:
   Recall@5: 0.450 → 0.480 ↑ +0.030
   MRR:      0.689 → 0.712 ↑ +0.023
```

---

## 七、参考来源

| 来源 | 核心借鉴 |
|------|---------|
| Cranfield Experiments (Cleverdon 1967) | 测试集三要素：文档/查询/相关性判断 |
| TREC Ad Hoc Track (NIST 1992-1999) | 池化(pooling)方法、MAP/NDCG 指标标准化 |
| Meta AI RAG Evaluation (2024) | 简单查询高估 25-30%，必须分层测试 |
| Weaviate IR Metrics Guide | Recall/MRR/NDCG 的计算实现 |
| Stanford CS276 IR Evaluation | NDCG 多级相关性处理的数学定义 |
| Anthropic Contextual Retrieval (2024) | Hybrid 方法降低 failure rate 49% |

## 🚨 重要前提：必须先审计实际 Skill 库

这是从 SRA v2 评估框架实战中沉淀的关键发现。

### 为什么必须审计？

**原来的做法**: boku 假设 skill 库里有 docker/pokemon/obsidian/arxiv 等 skill，设计了 60 个"通用"测试查询。结果这些 skill 在主人的实际库中并不存在。

**后果**: 评估结果的 Qrels 自动生成依赖于不存在的 category 字段，地面真值不准，无法反映真实覆盖情况。

### 审计方法

**Step 0（在开始设计测试查询之前执行）**:

```bash
# 1. 从 SRA 索引加载所有 skill
python3 -c "
import json
with open('~/.sra/data/skill_full_index.json') as f:
    raw = f.read()
# 解析 skills 数组
start = raw.find('\"skills\": [')
arr_start = raw.index('[', start)
skills = []
i = arr_start + 1
while i < len(raw):
    while i < len(raw) and raw[i] in ' \\n\\r\\t': i += 1
    if i >= len(raw) or raw[i] == ']': break
    if raw[i] == '{':
        depth = 1; j = i + 1
        while j < len(raw) and depth > 0:
            if raw[j] == '{': depth += 1
            elif raw[j] == '}': depth -= 1
            j += 1
        try:
            s = json.loads(raw[i:j]); skills.append(s)
        except: pass
        i = j
    else: i += 1
"
```

### 审计清单

量化评估前，对 skill 库做以下检查：

| 检查项 | 为什么重要 |
|--------|-----------|
| **总 skill 数** | 是否有 bmad/gds 等外部系列需要过滤 |
| **有 trigger 的 skill 数** | trigger 不足的 skill 会对哪些查询有匹配 |
| **仅英文 trigger 的 skill 数** | 中文用户查询时会有缺失 |
| **各 skill 触发词长度分布** | trigger 太短（2个以下）可能匹配困难 |
| **独立 skill 与系列 skill 分类** | bmad/gds 系列是否应该被纳入评估 |

### 基于审计设计查询

根据审计结果调整测试查询：

```python
# 审计输出示例
normal_skills = [s for s in all_skills 
    if not s['name'].startswith('bmad-') 
    and not s['name'].startswith('gds-')
    and not s['name'].startswith('skill-')]

# 中文 trigger 的 skill → 优先设计中文查询
cn_skills = [s for s in normal_skills if any('\u4e00' <= c <= '\u9fff' for t in s['triggers'] for c in t)]

# 仅英文 trigger 的 skill → 测试中英桥接能力
en_only_skills = [s for s in normal_skills if s['triggers'] and s not in cn_skills]

# 无 trigger 的 skill → 标记为需要补种或无法被推荐
no_trig_skills = [s for s in normal_skills if not s['triggers']]
```

设计原则：
1. 每个查询的 expected skill 必须**真实存在于 skill 库中**
2. 查询文本应该反映**真实用户会怎么表达**，而不是直接把 trigger 抄过来
3. 对仅英文 trigger 的 skill，设计中文同义查询来验证中英桥接能力
4. L5 噪声查询应确认不匹配任何 skill——如果匹配了是非预期的假正

---

## 📌 实战经验教训 (来自 SRA Sprint SRAS1)

### 案例 1: body_keywords 加入 match_text
**直觉判断**: "肯定有用，skill 的正文关键词应该被纳入匹配文本"
**实证结果**: Recall@5 从 0.447 降至 0.446 ↓
**原因**: body_keywords 已经通过 matcher.py 的 `_match_semantic` 路径被使用，重复加入 match_text 只是噪声
**教训**: 永远不要凭直觉——先用评估工具测基线，改完再跑同样的测试对比

### 案例 2: 同义词映射粒度修正
**问题**: "设计数据库"被推荐为 pdf-layout(52.8分)
**根因**: synonyms.py 中 "计划": ["设计", "architecture"] 导致"设计"→"计划"→"architecture"→命中 pdf-layout
**修复**: 移除模糊映射 + 区分精确匹配(25分)和宽泛匹配(12分)
**教训**: Qrels 需要同步更新才能准确反映改进——否则评估工具仍用旧 Qrels 判断相关性

### 案例 3: 文件监听自动刷新
**问题**: 新增 SKILL.md 需等 3600 秒或手动 POST /refresh
**修复**: 改用双模式——定时刷新(3600s) + 校验和轮询(30s)
**验证**: 创建 test skill → 35 秒后 daemon 技能数从 281→282，新 skill 可被推荐(60.2分 Top1)
**关键**: 这个改进不会体现在 Recall/MRR/NDCG 指标上——需要功能性测试验证

### 关键原则
1. **先基线再动手** — 任何改动前跑一次完整评估
2. **单变量实验** — 一次只改一个东西
3. **Qrels 同步更新** — 改 synonyms 后必须更新 Qrels 才能看到真实提升
4. **量化 > 直觉** — 数据面前，感觉不值一提
5. **不是所有改进都能用 IR 指标衡量** — 文件监听是功能性改进，需单独测试
6. **Daemon 重启后才加载代码改动** — 测试前必须先重启

---

## 八、已经积累的经验

| 日期 | 经验 | 来源 |
|------|------|------|
| 2026-05-04 | 小规模(200-300)推荐系统不需要向量数据库，BM25足够 | SRA 研究实战 |
| 2026-05-04 | 同义词匹配应区分"精确命中trigger/name"和"宽泛命中description" | SRA matcher.py 改进 |
| 2026-05-04 | Qrels 可从 skill triggers 自动生成，不需要人工标注（但 L3/L4 需要人工辅助） | SRA 评估框架设计 |
| 2026-05-04 | Daemon 重启后才能加载代码改动——测试时必须先重启 | SRA Story 1 实战 |
