# Knowledge Base Patterns for Hermes Agent

## 概述
本参考文件记录了从 Karpathy LLM Wiki 模式 + GBrain（Garry Tan）项目提炼的知识库构建方法，适用于为 Hermes Agent 搭建持久化知识库。

## Karpathy LLM Wiki 模式 (2025)
> 来源：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

### 三层架构
| 层级 | 目录 | 谁拥有 | 用途 |
|------|------|--------|------|
| Raw sources | `raw/` | 人类 | 不可变原始文档，LLM 只读 |
| The wiki | `wiki/` | LLM | 结构化的 Markdown 页面，LLM 创建/更新/维护 |
| The schema | `CLAUDE.md` | 人+LLM | 定义页面类型、工作流、约定 |

### 核心机制
- **增量式构建**：每添加一个来源，LLM 读取→提取→集成到现有 Wiki，更新相关页面
- **永久性 Wiki**：知识编译一次，持续更新，不在每次查询时重新推导
- **索引驱动检索**：`index.md` 作为目录，查询时先读 index 再深入具体页面
- **回答即知识**：好的回答可以归档为 Wiki 新页面，知识持续累积
- **规模**：适用于 ~100 个来源、数百页面的规模，无需向量检索基础设施

### 页面类型
- `wiki/sources/` — 原始文档摘要
- `wiki/concepts/` — 概念定义与相关术语
- `wiki/features/` — 功能特性说明
- `wiki/products/` — 产品概览
- `wiki/personas/` — 用户角色
- `wiki/analyses/` — 综合分析（对比/差距/大纲）

---

## GBrain — Garry Tan 的 Hermes 知识库 (2026)
> 来源：https://github.com/garrytan/gbrain

### 生产数据
- 17,888 页面，4,383 人，723 公司
- 21 个自主运行 cron 任务
- 12 天内建成

### 核心架构
```
Brain Repo (git)         GBrain (检索层)          AI Agent (Skills)
  markdown 文件  ──────>  Postgres + pgvector  <────>  29+ skills
  = 数据源                  混合搜索                   定义 HOW 使用 brain
                            vector + keyword + RRF      ingest/query/maintain
                            + 自布线知识图谱           enrich/briefing/migrate
```

### 混合检索管线
1. 意图分类（entity / temporal / event / general）
2. 多查询扩展（Haiku 重述问题 3 种方式）
3. 向量搜索（HNSW cosine over embeddings）
4. 关键词搜索（Postgres tsvector + websearch_to_tsquery）
5. RRF 融合：score = sum(1/(60+rank))
6. Cosine 重排 + compiled-truth boost
7. 来源感知去重

### 知识图谱（自布线）
- 每次页面写入自动提取实体引用
- 创建类型化链接：`attended`、`works_at`、`invested_in`、`founded`、`advises`
- 零 LLM 调用（纯算法提取）
- 递归 CTE + 循环预防

### 部署选项
| 模式 | 引擎 | 配置 |
|------|------|------|
| PGLite（默认） | 嵌入式 PostgreSQL 17.5 | 零配置，~/.gbrain/brain.pglite |
| Supabase | 云端 PostgreSQL + pgvector | $25/月，适合大规模 |
| 双向迁移 | `gbrain migrate --to supabase\|pglite` | 可随时切换 |

### 29+ Autonomous Skills
| Skill | 功能 |
|-------|------|
| ingest | 会议/文档/文章摄入，更新 compiled truth |
| query | 3 层搜索 + 合成 + 引用，不胡说 |
| maintain | 健康检查：矛盾/孤儿页/死链 |
| enrich | 从外部 API 丰富实体 |
| briefing | 每日简报 + 会议准备 |
| migrate | 从 Obsidian/Notion/Logseq 迁移 |

### Hermes 集成方式
- MCP 协议：通过 stdio 暴露 30+ tools
- 直接安装：`openclaw skills install gbrain`
- CLI 模式：`gbrain init` → `import` → `embed` → `query`
- Dream Cycle：夜间自动实体扫描、引用修复、记忆整合

---

## Hermes 当前的知识积累机制（可融合方向）

| 机制 | 目录 | 说明 |
|------|------|------|
| Skills | `~/.hermes/skills/` | 90+ skill，SKILL.md + references/ + scripts/ |
| Learning | `~/.hermes/learning/` | 学习状态机 + 知识图谱 + 阅读笔记 |
| Experiences | `~/.hermes/experiences/` | 可复用经验，分类 active/archive/skills |
| Night Study | `~/.hermes/night_study/` | 自驱动学习系统 v3.0 |
| Memory | `~/.hermes/memories/` | 跨会话持久记忆（2200 chars 限制） |

### 潜在融合路径
1. **GBrain MCP 集成**：将 GBrain 作为 MCP server 接入 Hermes
2. **LLM Wiki 模式**：用 `~/.hermes/knowledge/` 作为 wiki，CLAUDE.md 定义 schema
3. **Hybrid**：保留 Hermes Memory/Skills，将长期知识迁移到 GBrain

---

## Karpathy Bounded Autonomy — 知识库设计约束

从 autoresearch 项目提炼的七大约束（适用于知识库 Agent 设计）：
1. **固定时间盒** — 每次 ingest/query 有明确时间预算
2. **单文件/单职责范围** — 每个 Agent 只改一个文件
3. **单一指标** — 明确的成功/失败标准
4. **回滚保障** — Git 或备份机制确保失败零成本
5. **永远不停止** — 不要等待人类确认
6. **结构化循环** — 显式步骤，隐式推理不可靠
7. **零外部依赖** — 运行时不需要网络

---

## 文件分类参考（跨项目汇总）

| 类别 | LLM Wiki | GBrain | Hermes |
|------|----------|--------|--------|
| 原始来源 | sources/raw/ | Brain Repo (git) | learning/、research/ |
| 实体/人物 | concepts/、personas/ | people/ | experiences/ |
| 产品/功能 | features/、products/ | companies/、deals/ | skills/ |
| 分析/洞察 | analyses/ | meetings/、ideas/ | night_study/knowledge_base/ |
| 临时数据 | — | — | output/、cache/、cron/output/ |
| 归档 | — | archive/ | archive/、learning/archive/ |
