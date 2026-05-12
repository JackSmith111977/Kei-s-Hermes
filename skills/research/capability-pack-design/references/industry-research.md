# 能力模块化研究参考

> 用于 capability-pack-design skill 的行业研究参考。
> 整理自 2026-05-12 深度调研，涉及 8 个框架、6 篇 arXiv 论文、3 个行业标准。

---

## 一、主流框架模块化对比

| 框架 | 模块化粒度 | 能力复用机制 | 跨 Agent 移植 | 成熟度 |
|:-----|:----------|:------------|:-------------|:------:|
| Hermes Agent | SKILL.md / Profile / Plugin | 半自动（手动+SRA注入） | ✅ Profile 导出/MCP Serve | 成熟 |
| LangChain/LangGraph | Tool / Chain / Agent | ✅ 声明式组合（LCEL） | ⚠️ 需 Adapter | 非常成熟 |
| CrewAI | Agent Role / Task / Tool | ✅ Role 模板可复用 | ⚠️ 相对封闭 | 快速成熟 |
| AutoGen (MS) | Agent / Tool / Workflow | ✅ 对话式 Agent 组合 | ⚠️ 需自定义 | 发展中 |
| STEM Agent | Protocol / Skill / Memory | ✅ 细胞分化式技能获取 | ✅ MCP 标准化 | 研究原型 |
| Agency | Primitive（NL 构建块） | ✅ 语义组合+评估 | ✅ 跨项目复用 | 概念验证 |
| MoFA | Agent Template / Data Flow | ✅ 管道式堆叠 | ⚠️ 框架绑定 | 早期 |
| ALTK | Middleware Component | ✅ 生命周期钩子插入 | ✅ 框架无关 | 发展中 |

## 二、核心论文

### SkillX (arXiv:2604.04804)
- **三层技能层次**: Planning Skills（高层任务组织）→ Functional Skills（可复用工具子程序）→ Atomic Skills（单工具用法与约束）
- **自动流水线**: 从轨迹提取 → 迭代优化（合并+过滤）→ 探索性扩展
- **结论**: 插拔式技能知识库可显著提升弱 Agent 能力

### STEM Agent (arXiv:2603.22359)
- **生物学隐喻**: 未分化 Agent 核心 → 分化为专门化的协议处理器/工具绑定/记忆子系统
- **技能获取**: 细胞分化模型 — progenitor → committed → mature；失败则 apoptosis
- **统一网关**: 5 种协议 (A2A, AG-UI, A2UI, UCP, AP2) 统一于一个网关

### Agent Lifecycle Toolkit (ALTK, arXiv:2603.15473)
- **生命周期钩子**: post-user-request / pre-LLM / post-LLM / pre-tool / post-tool / pre-response
- **框架无关**: 可插入 LangChain、MCP、Claude SDK
- **10 个组件**: 每个针对一种失败模式（SPARC 检查工具调用、TAME 输出验证等）

### Auton AgenticFormat (arXiv:2602.23720)
- **核心分离**: Cognitive Blueprint（声明式 Agent 身份与能力）≠ Runtime Engine（执行环境）
- **AgenticFormat**: YAML/JSON 声明式 schema，语言无关
- **MCP 互补**: AgenticFormat 定义 Agent 是什么，MCP 定义 Agent 能用什么工具

## 三、行业标准协议

### MCP (Model Context Protocol)
- **状态**: 97M+ SDK 月下载，10,000+ 公开 Server（2026.03）
- **采纳方**: Anthropic（创建者）+ OpenAI（2025.03）+ Google（2025.04）
- **治理**: 2025.12 捐赠给 Linux Foundation
- **三大原语**: Tools（可调用函数）+ Resources（只读数据）+ Prompts（模板）
- **传输**: stdio（本地）+ Streamable HTTP（远程）+ in-process（嵌入）

### SKILL.md / agentskills.io
- **Hermes/Hub 通用**: Claude Code Skills 也使用类似格式
- **渐进式披露**: 先读索引 → 按需加载全文，token 友好
- **前件 YAML**: name + description + triggers + depends_on + platforms

### Agent2Agent (A2A, Google)
- 互补 MCP：MCP 连接 Agent 到工具，A2A 连接 Agent 到 Agent
- 跨组织 Agent 生态的基础协议

## 四、关键设计模式

### 渐进式复杂性
"从单体 Agent 开始，按需分解为模块" — 避免过早抽象。

### Manifest 驱动发现
每个模块携带机器可读的描述（YAML frontmatter / JSON Schema），Agent 运行时发现能力。

### 技能作为程序记忆
"Skills 不是文档，是 '我知道怎么做' 的程序性记忆。" — 与 declarative memory（事实）和 episodic memory（经历）互补。

### 编译式优化
多 Agent 系统编译为单 Agent with skills 可减少 **54% token** 和 **50% 延迟**（Wang et al. 2023）。

## 五、关键教训

| 来源 | 教训 | 应用到本项目 |
|:-----|:------|:------------|
| LangChain → CrewAI 转换 | Tool schema 冲突（Pydantic V1 vs V2） | 适配器层做格式隔离，不让 Agent 差异污染能力包 |
| Hermes SRA 开发 | 测试数据必须与运行时解耦 | 能力包的验证用 fixture 而非依赖线上服务 |
| Hermes Curator | 技能安全门禁（60+ 威胁模式） | 能力包安装时同样需要安全扫描 |
| MCP 生产部署 | 缺少 identity/error/retry 三原语 | 适配器需补充这些生产级能力 |
