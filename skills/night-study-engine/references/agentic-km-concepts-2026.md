# 🧠 Agentic Knowledge Management 2026 — 关键概念速查

> **提炼日期**: 2026-05-11 | **最后更新**: 2026-05-13 | **来源**: 18+ 权威来源交叉验证（含 2026-05 更新）  
> **用途**: 为夜间自习引擎 productivity 领域轮次提供即时上下文

---

## 📌 2026-05-13 更新：最新进展补充

### A. FalkorDB GraphRAG SDK 1.0 — 首个生产级 SDK
**来源**: FalkorDB Blog (Apr 29, 2026) 🥇
- GraphRAG-Bench Novel **#1 (63.73)**, Medical **#1 (75.73)**
- Modular API, async-first architecture, strategy pattern
- 增量图合并（非全量重建）— 摄入成本 $0.0055/文档
- 跨 LLM 兼容: OpenAI/Anthropic/Google/Cohere/本地模型
- **核心洞察**: "The harness matters more than the model"

### B. A-RAG — 分层检索接口 Agentic RAG
**来源**: arXiv 2602.03442 🥇
- 三层检索工具: `keyword_search`, `semantic_search`, `chunk_read`
- 一致性超越 GraphRAG 和 Workflow RAG 方法
- **关键结论**: Agent 友好接口比复杂检索算法更重要
- test-time scaling 表现优秀（强推理模型扩展更好）

### C. RAGSearch — "我们还需要 GraphRAG 吗？"
**来源**: arXiv 2604.09666 (Apr 1, 2026) 🥇
- Agentic search + Dense RAG 大幅缩小与 GraphRAG 差距
- **GraphRAG 在复杂多跳推理上仍然占优势**
- 两者互补：显式图结构 vs 隐式交互结构

### D. LazyGraphRAG — 1000x 成本降低
**来源**: Microsoft Research via BestAIWeb 🥈
- 索引成本降至全量 GraphRAG 的 ~0.1%
- 之前的成本屏障消失，GraphRAG 部署门槛大幅降低

### E. ServiceNow Context Engine (Knowledge 2026, May 5)
**来源**: ServiceNow 🥇
- **4 Graph 架构**: Enterprise Knowledge + Security + Decision + User Graph
- 共享本体层（ServiceNow Data Catalog + Pyramid Analytics）
- 通过 350+ 系统（Workflow Data Fabric）拓展上下文覆盖
- `Veza(身份)+Armis(设备)+TraceLoop(决策追溯)+Cuein(结果确认)`
- **核心叙事**: "模型从来不是问题，上下文才是缺失的一环"
- **与已有知识关联**: 独立验证了 Context Kubernetes 架构在企业级平台的可行性

### F. Opcito — 5 个 Agentic AI Context Engineering 模式 (May 5)
**来源**: Opcito Blog 🥇
1. **Task State as Explicit Context** — 结构化对象每步注入，保持目标可读
2. **Structured Context Checkpointing** — ACE 框架(Stanford+SambaNova)减少 context drift
3. **Dynamic Tool Loading** — 按需加载 tool schema（Hermes skill_view() 已实现）
4. **Validated Action Tiers** — 可逆→日志→硬验证三级
5. **Cross-Agent Trust Boundaries** — Agent 间通信不应默认信任
- EU AI Act **2026 年 8 月截止** — 上下文级可观测性成为合规门槛 🚨

### G. CDO's Playbook — 企业上下文工程
**来源**: Promethium.ai 🥈
- 2025 Karpathy 提出 → 2026 成为核心学科
- 70% CDAOs 领导 AI 战略 (Gartner)
- 四阶段框架: Anchor → Operationalize → Scale → Embed
- 现有数据架构(BI/目录/语义模型)是资产不是负担

---

## 5 大核心新概念

### 1. Context Kubernetes (CK)
**来源**: arXiv 2604.11623 (Mouzouni, 2026) 🥇  
**核心洞察**: 将企业知识编排类比容器编排问题。Context Engineering 是 AI 时代的 DevOps。

```
7 服务架构:
  Context Registry (元数据) → Context Router (调度) 
  → Permission Engine (权限) → Freshness Manager (新鲜度)
  → Trust Policy Engine (护栏) → Context Operators (控制器)
  → LLM Gateway (计量)

关键数据: 92 自动测试 + TLA+ 460万状态零违规
映射 Hermes: pre_flight+skill_finder+memory ≈ Context Registry+Permission
缺口: 无显式 Freshness Manager + Trust Policy Engine
```

### 2. Atomic Knowledge Units (AKU)
**来源**: arXiv 2603.14805 (Knowledge Activation) 🥇  
**核心洞察**: 机构知识 → Agent 可执行原子单元。AKU 是 AI Skill 的企业特化版。

```
7 组件模式:
  ① Intent → ② Procedural Knowledge → ③ Tool Bindings
  ④ Organizational Metadata → ⑤ Governance Constraints
  ⑥ Continuation Paths → ⑦ Validators

三层部署: AKU Registry → Knowledge Topology → Activation Policy
AI-Generated Golden Paths: 策展路径 → Agent 运行时动态组合
映射 Hermes: Skills 实现了 ①-③, 缺 ⑤⑥⑦
```

### 3. Agentic Operating System (AOS)
**来源**: Knowlee + a21.ai + Zylos Research (多源交叉) 🥇  
**核心洞察**: OS > 编排。Framework=协调, OS=运行时+治理层。

```
3 前提条件 (2024-2025 汇聚):
  ① 模型成本降 ~80% → 推断环境化
  ② MCP 标准化工具层 → 工具调用形状统一
  ③ EU AI Act 治理元数据合规化 → 风险分类/数据类别/监督

6 原语:
  ① Kanban Fleet Observability
  ② Jobs Registry (risk_level/data_categories/human_oversight/approval)
  ③ Flashcard Pre-Review Queue
  ④ Cross-Vertical Knowledge Graph
  ⑤ Workspace Isolation
  ⑥ MCP Routing Fabric (最便宜工具优先)

映射 Hermes: kanban ≈ ①, process-management ≈ ⑤, 缺 ②④
```

### 4. Enterprise Memory Layer (EML)
**来源**: Zylos Research (Mar 2026) + AWS Bedrock AgentCore Memory 🥇  
**核心洞察**: 知识层是 Agent AI 最被低估的基建。

```
关键数据:
  - 60% 企业 RAG 失败 → 新鲜度/一致性问题
  - 91% AI 模型经历时间退化
  - 知识库 8 个月: 95%→78% 无信号
  - Zep Graphiti: 双时间戳, 94.8% 准确率, 90% 延迟降低

4 记忆类型: Episodic | Semantic(会衰减) | Procedural | Working
3 层存储: Hot(即时) | Warm(跨会话不可变) | Cold(图谱+SLA+访问控制)
```

### 5. Agentic Knowledge Fabric (AKF)
**来源**: agenticmesh.substack.com (Agentic Process Automation)  
**核心洞察**: 上下文应该作为"产品"——可预测大小、稳定标识、可溯源、确定性组装。

```
3 阶段管线:
  Ingestion → Compilation (概念卡+策略卡) → Serving (最小可行上下文包)
  Context Server: 请求 → 步骤模板 → 管辖过滤 → 检索 → 组装

映射 Hermes: extracted_knowledge.md ≈ 概念卡雏形
缺口: 从手动提取 → 自动编译
```

---

## 关键趋势

| 趋势 | 影响 | 时间线 |
|:---|---|:---:|
| Context Engineering 2.0 成熟度金字塔 | PE→CE→IE→SE 四级 | 2026 Q2 已成熟 |
| Knowledge Runtime 取代静态 RAG | 检索+验证+推理+审计集成 | 2026 已发生 |
| Agentic OS vs Framework 区分 | 新架构决策维度 | 2026 H2 |
| EU AI Act 8 月截止线 | 高风险 AI 必满足记录/透明/监督 | 2026-08 |

## 关键数据汇总

| 指标 | 值 | 来源 |
|:---|---|:---:|
| Agentic Graph RAG 准确率 | 94% (vs 向量 RAG 67%) | ValueStreamAI |
| Zep Graphiti 准确率 | 94.8% | Zylos+AAIA |
| 知识衰减周期 (95%→78%) | 8 个月无信号 | Zylos |
| 企业 RAG 失败 (新鲜度问题) | 60% | Zylos |
| Context Kubernetes TLA+ 验证 | 460 万状态零违规 | arXiv |

## 推荐下一步行动

1. **Freshness Manager**: 为 KB 每个概念添加 `expires_at` + `last_verified_at` 字段
2. **Validators**: 利用 skill_manage 的 pre/post 挂钩实现 AKU Validators 模式
3. **Continuation Paths**: 在 skill references/ 中实现跨 skill 导航
4. **AOS Jobs Registry**: kanban-orchestrator 新增 risk_level/data_categories/human_oversight 字段
