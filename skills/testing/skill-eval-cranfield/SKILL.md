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

---

## 十、全套验证流程 — 超越 Cranfield 的系统集成测试

> **Cranfield 侧重 IR 指标的量化评估；但一个推荐系统在发布前，还需要通过系统集成验证、CLI/HTTP 接口测试、仿真压力测试，确保功能完整性。**

### 10.1 为什么需要多层级验证

| 层级 | 覆盖 | 工具 | 发现的问题类型 |
|:-----|:-----|:-----|:--------------|
| **L0 单元测试** | 匹配算法/同义词表/索引 | pytest | 算法逻辑错误 |
| **L1 集成测试** | SkillAdvisor 加载/推荐/记录 | pytest + fixtures | 索引/加载错误 |
| **L2 CLI 命令测试** | 全部子命令的可用性 | sra status/recommend/coverage/... | CLI 入口/参数错误 |
| **L3 HTTP API 测试** | REST 端点的响应 | curl + JSON 验证 | API 路由/序列化错误 |
| **L4 仿真测试** | 真实用户场景模拟 | 连续问答/中英混合/边缘/压力 | 语义理解/性能瓶颈 |

### 10.2 推荐验证流程

```bash
#!/bin/bash
# SRA 全量验证脚本
set -e

echo "🧪 L0+L1: pytest (单元+集成)"
cd /path/to/sra-proxy
python3 -m pytest tests/ -v --tb=short | tail -20
echo ""

echo "🧪 L2: CLI 命令测试"
sra status
sra version
sra refresh
echo ""

echo "🧪 L3: HTTP API 测试"
curl -s http://localhost:8536/status | python3 -m json.tool
curl -s -X POST http://localhost:8536/recommend \
  -H 'Content-Type: application/json' \
  -d '{"message": "画架构图"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Top: {d[\"recommendations\"][0][\"skill\"]} ({d[\"recommendations\"][0][\"score\"]})')"
echo ""

echo "🧪 L4: 仿真 (压力测试)"
for i in $(seq 1 10); do
  curl -s -X POST http://localhost:8536/recommend \
    -H 'Content-Type: application/json' \
    -d '{"message": "画架构图"}' -o /dev/null -w "第${i}次: %{time_total}s\\n"
done
```

### 10.3 关键验证点

#### L2 CLI 命令检查清单

```bash
# 必须验证的 12 个子命令
sra status       # ✅ Daemon 运行状态
sra version      # ✅ 版本号 + 作者
sra help         # ✅ 帮助文档
sra refresh      # ✅ 索引刷新
sra stats        # ✅ 运行统计
sra config show  # ✅ 配置读取
sra adapters     # ✅ 适配器列表
sra recommend 画架构图   # ✅ 场景推荐
sra recommend 帮我做个PPT  # ✅ 场景推荐
sra recommend 飞书发送文件  # ✅ 场景推荐
sra coverage     # ✅ 覆盖率分析
sra record <skill> <query>  # ✅ 记录使用
```

#### L3 HTTP API 端点验证

| 端点 | 方法 | 预期响应 | 测试命令 |
|:-----|:-----|:---------|:---------|
| `/status` | GET | `{"status": "ok", "sra_engine": true, ...}` | `curl http://localhost:8536/status` |
| `/recommend` | POST | `{"rag_context": "...", "recommendations": [...]}` | `curl -X POST -d '{"message":"..."}' http://localhost:8536/recommend` |
| `/stats` | GET | `{"version": "...", "status": "running", ...}` | `curl http://localhost:8536/stats` |

#### L4 仿真场景模板

**场景 1: 连续问答**
```bash
# 模拟用户连续需求
curl -X POST -d '{"message":"生成PDF"}'       # → pdf-layout
curl -X POST -d '{"message":"然后是PPT"}'       # → pptx-guide
curl -X POST -d '{"message":"最后整理成Excel"}'  # → xlsx-guide
curl -X POST -d '{"message":"把这些发到飞书上"}'  # → feishu-send-file（⚠️ 可能为 NONE）
```

**场景 2: 中英混合**
```bash
curl -X POST -d '{"message":"git push 怎么撤销"}'
curl -X POST -d '{"message":"deploy to production"}'
curl -X POST -d '{"message":"financial analysis 股票"}'
```

**场景 3: 边缘情况**
```bash
curl -X POST -d '{"message":""}'              # 空 → NONE
curl -X POST -d '{"message":"a"}'             # 单字 → NONE
curl -X POST -d '{"message":"!@#$%^&"}'       # 特殊字符 → NONE
curl -X POST -d '{"message":"主人帮我看看这个代码"}' # 口语化 → python-debugpy
```

**场景 4: 压力测试**
```bash
# 连续 20 次请求，验证成功率 100%，平均 < 500ms
for i in $(seq 1 20); do
  curl -s -X POST -d '{"message":"画架构图"}' \
    http://localhost:8536/recommend -o /dev/null -w "%{http_code} %{time_total}s\\n"
done
```

### 10.4 Daemon 生命周期管理

**关键注意事项:**

| 操作 | 命令 | 陷阱 |
|:-----|:-----|:-----|
| **停止旧 daemon** | `sra stop` | 必须先 stop 再 pip reinstall，否则文件锁 |
| **重新安装** | `pip install --break-system-packages -e .` | 需要 `--break-system-packages`（PEP 668 环境） |
| **启动新版** | `sra start` | 启动前检查日志/端口占用 |
| **验证版本** | `sra version` | 确认版本号正确 |
| **刷新索引** | `sra refresh` | Daemon 启动后首次加载 313 skills 需要 ~0.3s |

**⚠️ 常见陷阱:**
1. `pip install -e .` 不重启 daemon → 代码改动不生效（daemon 独立进程）
2. `sra coverage` 和 `SkillAdvisor.analyze_coverage()` 的结果可能不同（前者走 daemon 索引，后者实时加载）
3. HTTP API 的延迟（~225ms）远高于 CLI（~30ms）— 因为 JSON 序列化和网络开销

### 10.5 实战参考（SRA v1.1.0，2026-05-07）

| 测试项 | 结果 | 耗时 |
|:------|:----|:----|
| pytest (39 tests) | ✅ 全部通过 | 19.5s |
| CLI 基础命令 (12 个) | ✅ 全部正常 | ~1s |
| CLI 场景推荐 (7 个) | ✅ 全部精准匹配 | ~0.2s |
| HTTP API (3 端点) | ✅ JSON 有效 | ~0.1s |
| 仿真 20 次压力 | ✅ 100% 成功 | ~4s |
| 推荐平均延迟 (CLI) | ~30ms | — |
| 推荐平均延迟 (HTTP) | ~225ms | — |
| 技能覆盖率 | 94.9% | — |
| 有 trigger 技能覆盖率 | 99.4% | — |

### 10.6 经验教训

1. **不要凭直觉判断改进效果** — 改前后必须跑完整 L0-L4 流程
2. **仿真测试暴露的问题 pytest 不一定能发现** — 模糊口语化查询、"把这些发到飞书上"等自然语言表达经常匹配失败
3. **HTTP 延迟是 CLI 的 7-8 倍** — 如果用户主要用 HTTP API，性能基准应基于 HTTP 而非 CLI
4. **Daemon 重启是必要的** — pip reinstall 后不重启 daemon，变更不会生效
5. **门禁断言应 >= 300** — 确保 CI 不会降级到用假数据
6. **同义词表是命门** — 一个缺失的同义词（如"系统设计"与 architecture diagram 之间）就导致完全无匹配。每次新增 skill 后应同步补全同义词
7. **仿真必须先于量化评估** — 在跑 Recall/MRR 等指标前，先用仿真场景暴露明显的匹配错误，否则量化指标可能掩盖严重缺陷
8. **HTTP API 端点覆盖不全** — daemon 的 /coverage 端点返回 404，需要从 CLI 覆盖。发布前必须验证每个端点返回正确的 HTTP 状态码

### 10.7 实战发现的典型匹配盲区（SRA v1.1.0）

以下是从 2026-05-07 仿真测试中发现的典型缺陷：

| 查询 | 推荐结果 | 问题类型 | 根因 |
|:-----|:---------|:---------|:-----|
| `发飞书消息` | himalaya (59分) | 同义词桥接错误 | synonyms 中 himalaya 与飞书产生交叉干扰 |
| `画系统设计图` | NONE (0分) | 同义词缺失 | 无"系统设计"到 architecture diagram 的映射 |
| `用 python 画个折线图` | NONE (0分) | 技能盲区 | 无 matplotlib/seaborn 相关 skill |
| `把这些发到飞书上` | NONE (0分) | 模糊指代 | "把这些"等口语化指代无法被特征拆分捕获 |
| `主人帮我看看这个代码` | python-debugpy (51.8) | 正确但薄弱 | 靠"代码"到 debug 映射，仅中等置信度 |

**处理策略**：这些缺陷先记录后治理。同义词表修改可能引发连锁反应，需要先跑基线再修改，修改完重新跑全套 L0-L4 验证。

---

> **本页内容来自 2026-05-07 实战：将 ~/.hermes/skills/ 的全部真实技能 YAML 提取为可复用的测试 Fixture。**

### 9.1 为什么需要真实数据

| 方法 | 问题 |
|------|------|
| 手工编造 15 个测试技能 | 覆盖率不真实，CI 上跑不出有意义的结果 |
| 直接从 ~/.hermes/skills/ 加载 | 依赖外部环境，CI 上不可用 |
| **✅ 提取 YAML → 创建 Fixture** | **既真实又独立，git clone 即跑** |

### 9.2 批量提取流程

```
~/.hermes/skills/ (313 SKILL.md)
       ↓ python3 scripts/create-fixtures-from-real-skills.py
       ├── tests/fixtures/skills/         ← 317 个 SKILL.md（按类别组织）
       ├── tests/fixtures/skills_yaml/    ← 每个技能 1 个 YAML
       └── tests/fixtures/skills_yaml/_all_yamls.json  ← 合并 JSON（测试数据源）
```

### 9.3 关键技术决策

| 决策 | 方案 | 理由 |
|------|------|------|
| **类别嵌套** | `bmad-method/agents` → `bmad-method__agents` | `/` 在文件系统中会被识别为目录分隔符 |
| **YAML 源保留** | 独立 YAML + 合并 JSON | 独立 YAML 便于单技能审计，合并 JSON 便于测试加载 |
| **跳过重复** | 已有 Fixture 的技能（15 个）跳过 | 保留原始的精确控制数据，不覆盖 |
| **验证门禁** | `assert skills >= 300` | 确保 CI 上不会退化到用假数据 |

### 9.4 脚本使用

```bash
# 运行一次，生成全部 Fixture
cd /path/to/sra-proxy
python3 tests/fixtures/../scripts/create-fixtures-from-real-skills.py

# 在测试中验证真实数据
# 参考 test_matcher.py:
def test_all_skills_indexed(self):
    indexed_names = set(s["name"] for s in self.skills)
    missing = REAL_SKILL_NAMES - indexed_names
    coverage = len(indexed_names & REAL_SKILL_NAMES) / len(REAL_SKILL_NAMES) * 100
    assert coverage >= 90, f"真实技能索引覆盖率应 ≥ 90%，实际 {coverage:.1f}%"
```

### 9.5 从真实 YAML 生成测试查询

```python
with open("_all_yamls.json") as f:
    ALL_REAL_SKILLS_YAML = json.load(f)

def get_real_skill_test_queries():
    """遍历每个真实技能的 trigger/name/desc → 自动生成测试查询"""
    tests = []
    for ydata in ALL_REAL_SKILLS_YAML:
        name = ydata.get("_source_name", "")
        triggers = ydata.get("triggers", []) or []
        queries = []
        # 1. 中文 trigger 优先
        for t in triggers:
            if isinstance(t, str) and any('\u4e00' <= c <= '\u9fff' for c in t):
                queries.append(t)
        # 2. 英文 trigger（前 2 个）
        eng = [t for t in triggers if isinstance(t, str) and all(c.isascii() or c in ' -' for c in t)]
        queries.extend(eng[:2])
        # 3. 名称语义化
        queries.append(name.replace("-", " "))
        # 4. description 关键词
        desc = ydata.get("description", "")
        if desc:
            queries.extend([w for w in desc.replace("—", " ").split() if len(w) >= 2][:2])
        tests.append({"name": name, "test_queries": list(set(q for q in queries if q))[:5]})
    return tests
```

### 9.6 实战结果（313 真实技能）

| 指标 | 值 |
|:-----|:--:|
| 有 YAML frontmatter | **313/313 (100%)** |
| 生成的 Fixture 数 | **317 个**（含原有 15 个） |
| 覆盖类别 | **67 个** |
| 索引覆盖率 | **96.8%** |
| 有 trigger 技能覆盖率 | **99.4%** |

### 9.7 经验教训

1. **不要在 CI 上依赖真实 `~/.hermes/skills/`** — 换环境就挂
2. **不要用手工编造的测试技能** — 测不出真实的问题
3. **提取 YAML 时保留 `_source_path`** — 方便追查来源
4. **门禁验证** — 用 `assert count >= 300` 杜绝退化到假数据
5. **重复技能的处理** — 已有手工 fixtures 时，跳过保留，不覆盖

### 9.8 参考

- 脚本: `scripts/create-fixtures-from-real-skills.py`
- 测试示例: `tests/test_matcher.py` (`TestAdvisor` class)
- 覆盖率测试: `tests/test_coverage.py`

---

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
| 2026-05-07 | 仿真测试暴露的缺陷与 pytest 不同，必须同时跑两种测试 | SRA v1.1.0 Full QA |
| 2026-05-07 | HTTP API 延迟约 225ms，是 CLI 的 7-8 倍，性能基准应区分 | SRA v1.1.0 压力测试 |
| 2026-05-07 | 同义词表一个缺口就导致完全无匹配，是系统的命门 | SRA v1.1.0 仿真测试 |
| 2026-05-07 | Fixture 必须 assert skills>=300 阻止 CI 退化到假数据 | SRA v1.1.0 测试改造 |
