# Skill 架构研究关键来源（2026年5月汇总）

> 本文件整理 deep-research 在处理 Agent skill 架构对比研究时发现的关键学术来源和实践指南。供后续类似调研复用。

## 学术论文

### 架构基础
| 论文 | 核心论点 | 链接 |
|------|---------|------|
| SoK: Agentic Skills (2026) | 正式定义 skill 为 4-tuple (C,π,T,R)。Skills ≠ Tools。7个设计模式 | [arxiv 2602.20867](https://arxiv.org/abs/2602.20867) |
| Agent Skills Survey (2026) | Skills 和 MCP 是正交层。渐进式加载定义架构创新 | [arxiv 2602.12430](https://arxiv.org/abs/2602.12430) |
| Comprehensive Survey on Agent Skills (2026) | 4阶段生命周期(表示/获取/检索/进化)。结构感知检索 | [arxiv 2605.07358](https://arxiv.org/abs/2605.07358) |

### 技能选择与可扩展性
| 论文 | 核心论点 | 链接 |
|------|---------|------|
| When Single-Agent with Skills Replace MAS (2026) | **相变发现**：skill 选择精度在~100-200临界点后急剧下降。根因是语义混淆度不是库大小 | [arxiv 2601.04748](https://arxiv.org/abs/2601.04748) |
| GraSP: Graph-Structured Skill Compositions (2026) | 2-3 skill 最佳，4+收益递减。DAG编译优于扁平执行 | [arxiv 2604.17870](https://arxiv.org/abs/2604.17870) |

### 双粒度与层次化
| 论文 | 核心论点 | 链接 |
|------|---------|------|
| D2Skill: Dynamic Dual-Granularity Skill Bank (2026) | 任务级+步骤级双粒度，10-20pp提升 | [arxiv 2603.28716](https://arxiv.org/abs/2603.28716) |
| SkillLens (2026) | 4层图混合粒度检索优于纯扁平或纯层次 | [arxiv 2605.08386](https://arxiv.org/abs/2605.08386) |
| AgentSkillOS (2026) | 树检索 O(log n) + DAG 编排。200K skill 验证 | [arxiv 2603.02176](https://arxiv.org/abs/2603.02176) |

### Workflow 编排
| 论文 | 核心论点 | 链接 |
|------|---------|------|
| MCP Workflow Engine (2026) | 智能-执行分离。99% token节省。MCP Mediator 模式 | [arxiv 2605.00827](https://arxiv.org/abs/2605.00827) |
| AgentSlimming (2026) | 多Agent工作流剪枝，减少78.9%成本 | [arxiv 2605.08813](https://arxiv.org/abs/2605.08813) |
| MCP 生产部署模式 (2026) | CABP + ATBA + SERF 三种生产缺失原语 | [arxiv 2603.13417](https://arxiv.org/abs/2603.13417) |

## 实践指南

| 来源 | 核心贡献 | 链接 |
|------|---------|------|
| Microsoft — Skills & MCP Guide v3 | Skill=大脑, MCP=手。WHEN:触发器取代DO NOT USE FOR | [aka.ms/skills/guidance](https://aka.ms/skills/guidance) |
| Perplexity — Designing Skills (2026) | 3层加载模型(Index/Load/Runtime)。3问测试。Skills≠Code | [research.perplexity.ai](https://research.perplexity.ai/articles/designing-refining-and-maintaining-agent-skills-at-perplexity) |
| Agent Layer — Skill Design Guide | 12条证据驱动原则。ComplexBench/IFScale 研究引用 | [agent-layer.dev](https://agent-layer.dev/skill-design/) |
| AI Skill Market — MCP vs Skills | Skills=智能层, MCP=连接层。内联vs分叉执行选择 | [aiskill.market](https://aiskill.market/blog/mcp-skills-complementary-layers-ai-stack) |
| DAG-First Orchestration (2026) | 3.6x加速比。关键路径分析法则 | [tianpan.co](https://tianpan.co/blog/2026-04-10-dag-first-agent-orchestration-linear-chains-scale) |

## 关键数据点

| 数据 | 值 | 来源 |
|:----|:---|:-----|
| MCP 生态规模 | 10,000+ 服务器, 97M SDK月下载 | arxiv 2603.13417 |
| MCP Workflow Engine token节省 | >99%（1,246,800→150 tokens） | arxiv 2605.00827 |
| DAG 加速比 | 3.6x（LLMCompiler） | tianpan.co |
| 相变临界点 | ~100-200 skills | arxiv 2601.04748 |
| Voyager 技能库效果 | 15.3x 科技树解锁加速 | arxiv 2305.16291 |
| OpenClaw vs AutoGPT | 40-60% token节省 | clawbot.blog |
