# 📚 学习方法论 2026 全景 — 从 KM 治理到 KB 构建实操

> **建立日期**: 2026-05-17 | **来源**: 4 篇独立权威来源交叉验证  
> **用途**: 为 learning_methodology 领域提供即时上下文，指导 boku 的学习方法和 KB 构建决策  
> **关联领域**: productivity (Agentic KM), learning_methodology

---

## 一、本次学习的新增来源（未覆盖于 agentic-km-concepts-2026.md）

### 来源 1: Fluid Topics — Reshaping KM for Agentic AI Enablement 🥇
**URL**: https://www.fluidtopics.com/blog/industry-insights/knowledge-management-for-agentic-ai-enablement/  
**类型**: 行业报告 | **日期**: Mar 6, 2026 | **来源质量**: 🥇 官方博客

**核心论点**:
- KM 的主要消费者从人类转向 AI Agent（"Your user is not human anymore"）
- 技术突破：LRM（Large Reasoning Models）+ MCP（Model Context Protocol）使 agent 能直接与业务系统交互
- 统一搜索/Data Lake 模式已失败（上下文丢失、治理困难、只读）
- **新信息架构**: Agent 需要每个业务领域的权威参考源，KM 必须成为 MCP 使能的网关

**与 Hermes 的映射**:
- boku 的每个领域独立 KB JSON 文件 = Fluid Topics 的"领域权威参考源"模式
- boku 的 `mcp_tavily_*` 工具调用 = MCP 网关模式的实现
- 非结构化内容（PDF/幻灯片）是最大盲区 — Hermes 的 `web_extract`/`vision-qc-patterns` 等 skill 已覆盖此盲区

### 来源 2: KalTalk — AI Knowledge Base 2026: Build Without Hallucinations 🥇
**URL**: https://kaltalk.com/blog/ai-knowledge-base  
**类型**: 实操指南 | **日期**: 2026 | **来源质量**: 🥇 专业博客

**5 步构建法**:
| 步骤 | 操作 | 检查点 |
|:----|:-----|:-------|
| 1 | 选规范文档（一个问题一个文档，去重） | 无重复、无矛盾 |
| 2 | 为检索写作（短声明句，每段以问题开头） | chunk 可独立理解 |
| 3 | 分块策略（固定 500-1000 tokens 或按章节） | 测试 recall |
| 4 | 添加元数据（last_updated/author/topic/source_url） | 支持过滤和审计 |
| 5 | 选 Embedding 模型并固定 | 评估集验证 |

**5 种失败模式**:
| 失败 | 症状 | 结构性修复 |
|:-----|:-----|:----------|
| Empty Retrieval | 模型用预训练数据填空 | 硬拒绝 + 应用层软门禁 |
| Stale Content | 过期策略的自信错误答案 | last_updated + 主题负责人 |
| Contradiction | 相似查询不同答案 | 摄入时去重 |
| Privacy Leak | 内部文档暴露给外部 | 检索时访问控制 |
| Retrieval Drift | 嵌入模型变化偏移向量空间 | 索引版本化 |

**操作检查清单**:
1. 🟢 **每个主题一个负责人**（永久座位，非委员会）
2. 🟢 **100 真实查询评估集**（从历史 tickets 提取，跟踪 recall+correctness）
3. 🟢 **空检索软门禁**（拒绝而非猜测）
4. 🟢 **新鲜度作为一等指标**（显示每个 chunk 年龄，阈值告警）
5. 🟢 **每周抽样审计**（20 轮对话，检查答案和引用 chunk）
6. 🟢 **索引版本化**（更换模型时并排运行，评估后再切换）

**与 Hermes 的映射**:
- boku 的 nightly `freshness_score` 在 KB JSON 中 = 新鲜度一等指标 ✅
- boku 的 `learning_history.avg_quality` = 评估集指标 ✅
- boku 的 knowledge-routing = 摄入时去重机制 ✅
- **缺口**: 无显式"硬拒绝"机制（当 KB 无法回答时应拒绝而非猜测）

### 来源 3: Supermemory — Agentic Workflows for 2026 🥇
**URL**: https://supermemory.ai/blog/agentic-workflows-vp-engineering-guide  
**类型**: 工程指南 | **日期**: 2026 | **来源质量**: 🥇 工程博客

**核心论点**: 记忆是基础设施，不是功能特性

**生产上下文栈 (5 层)**:
| 层 | 功能 | 失败模式 | Hermes 映射 |
|:---|:-----|:---------|:------------|
| 1. Connectors | 从 Notion/Slack/DG 拉实时数据 | 数据过时 | web_search/mcp_tavily |
| 2. Extractors | 处理 PDF/音视频/图片 | 格式不兼容 | web_extract/vision-qc |
| 3. Retrieval | 混合 RAG(向量+关键词)+重排序 | 检索不准 | mcp_tavily_search/skill_finder |
| 4. Memory Graph | 追踪事实间关系 | 矛盾/更新丢失 | KB JSON 的 relationships 字段 |
| 5. User Profiles | 静态事实+情景记忆 | 个性化失效 | SOUL.md + memory tool |

**编排规则**:
- 确定性层：Agent 之上需要刚性层处理路由/重试/恢复（防无限循环）
- 分层状态：临时(step) | 持久(session) | 检查点(long-running)
- 显式失败路径：每个工具调用需 fallback（不是无限重试）
- HITL 门禁：定义强制人工审批点

**与 Hermes 的映射**:
- Hermes 的 `pre_flight.py` + `AGENTS.md` = 确定性层 ✅
- boku 的 constraint system（timebox/rollback/verification）= 显式失败路径 ✅
- Hermes `learning-state.py` 的 regress/reject/loop-status = 分层状态 ✅
- Memory Graph 缺口：KB JSON 的 relationships 字段在部分领域缺失

### 来源 4: Skywork AI — AI Agents in the Workplace: 2026 Trends 🥇
**URL**: https://skywork.ai/blog/ai-agent/ai-agents-workplace-agentic-workflows/  
**类型**: 实践指南 | **日期**: 2026 | **来源质量**: 🥇 专业博客

**核心实践模式**:
- **编排模式**: orchestrator + specialists（与 Hermes `delegate_task` 一致）
- **RAG + Actions**: 检索增强动作（与 boku 的 reading→extraction→artifact 一致）
- **可观测性**: prompt/决策/工具结果/审批 全部可追溯
- **测量优先**: "没办法衡量就没法管理" — A/B 测试 agent vs 人工

**实践建议**: 从"研究→文档→演示"单一流程开始，逐步扩展到复杂场景。

---

## 二、交叉验证汇总：6 个关键结论

| 结论 | 独立来源数 | 来源 | Hermes 状态 |
|:-----|:----------:|:-----|:------------|
| KM 主要用户从人→AI Agent | 3/4 | FluidTopics, SMRITEX, Skywork | ✅ 已实现（KB→skill_finder→SRA） |
| 需要层级化治理框架 | 4/4 | SMRITEX, KalTalk, Supermemory, FluidTopics | ✅ Bounded Autonomy 七层约束 |
| 空检索应拒绝而非猜测 | 3/4 | KalTalk, SMRITEX, Skywork | ⚠️ 未显式实现 |
| 新鲜度需要主动追踪 | 4/4 | KalTalk, SMRITEX, Supermemory, FluidTopics | ✅ freshness_score + 间隔复习 |
| 记忆是基础设施 | 4/4 | Supermemory, SMRITEX, FluidTopics, KalTalk | ✅ KB JSON + session_log + memory tool |
| 编排需要确定性层 | 3/4 | Supermemory, Skywork, SMRITEX | ✅ AGENTS.md + pre_flight |

---

## 三、可操作建议（按优先级）

### 🔴 短期（立即）
1. **实现空检索硬拒绝** — 当 web_search/knowledge_base 无结果时，在 reading_notes 中标记"❌ 无法找到可靠的来源答案"，而非编造
2. **延续 metadata 规范** — 新 KB 概念统一使用 `key_points`(list) + `source_urls`(list) + `confidence`(float) + `notes`(str)
3. **延续 session_log 格式** — quality_score 统一 int(0-100)，concepts_updated/new_concepts_added 统一 list

### 🟡 中期（2-4 周内）
4. **为 learning-workflow 增加 Continuation Paths** — SKILL.md frontmatter 新增 `continuations:` 字段
5. **KB 关系图谱增强** — 为有复杂关联的 KB 添加 relationships 字段（night-study-engine v4.0 已定义 schema 但尚未推广）

### 🟢 长期方向
6. **Memory Graph 模式实现** — 在 KB JSON 基础上增加概念间关系索引，支持跨域概念推理
7. **Freshness SLA** — 为每个 KB 概念设置 `expires_at` 字段，超时自动触发复习

---

## 四、First-Session Domain 初始化模式

从 learning_methodology 首次建立 KB 的实战中提炼的通用模式：

```text
首次建立 KB 的标准流程:
  1. 确认领域调度分 → select_domain.py --list
  2. 阅读 KB JSON → 确认 concepts 为空
  3. 搜索 3-5 个高质量来源（web_search 多关键词并行）
  4. 提取核心内容（web_extract）
  5. 写 reading_notes.md（按主题组织 + URL 绑定）
  6. 创建 KB JSON（8-12 个概念起步，mastered/developing 各半）
  7. 写 extracted_knowledge.md（交叉验证表格 + 可操作建议）
  8. 质量自评（4 维度: 覆盖度/交叉验证/可操作性/结构）
  9. 更新 config v3 learning_history + freshness_score
  10. 写入 JSONL 日志 + summary log
  11. 清理 ~/.hermes/learning/ 缓存
```

**注意事项**:
- 首次 KB 概念不宜过多（8-12 个合适，覆盖核心领域即可）
- mastered:developing 比例建议 6:4（给未来留知识升级空间）
- 必须添加 2-3 个 open_questions 为后续学习铺路
- session_log 必须记录 sources_used URL 列表供 audit
