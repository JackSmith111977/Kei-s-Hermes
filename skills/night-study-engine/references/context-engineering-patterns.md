# Context Engineering 2.0 — 系统级上下文架构模式参考

> **来源**：appxlab.io(2026-03), qubittool.com(2026), swirlai.com(2026-03-22), contextstudios.ai(2026), rephrase-it.com(2026)
> **用途**：补充夜间自习引擎的 Agentic RAG 2.0 映射，提供 CE 模式的速查

## 一、模式演进：CE 1.0 → 2.0

| 维度 | 1.0 | 2.0 |
|:----|:----|:----|
| 核心焦点 | Token 窗口优化 / RAG 检索 | 规则文件生态 / 团队级上下文架构 |
| 信息源 | 聊天历史 / 手动复制粘贴 | 版本控制规则文件 / MCP 动态注入 |
| 目标受众 | 个人开发者 | 团队 / 组织 / 开源项目 |
| 持久化方式 | CLAUDE.md, 对话摘要 | agents.md, instructions.md, prompts.md |
| 标准化程度 | 低（各 IDE 独立定义） | 高（GitHub 驱动行业标准） |

## 二、Write/Select/Compress/Isolate 四模式

| 模式 | 解决的问题 | 适用条件 | 风险 |
|:----|:----------|:--------|:----|
| **Write** | 超长任务截断（>10-15 轮） | 非平凡 Agent 的表态门槛 | 写入 I/O 成本 |
| **Select** | 噪声干扰导致注意力分散 | 大型工具集（10+）| 检索延迟增加 |
| **Compress** | Token 成本膨胀 | 成本敏感的长工作流 | Briefity bias，复述层数过多导致信息丢失 |
| **Isolate** | 多步上下文爆炸 | 具有真正不同子任务的工作流 | 最高 15× Token 消耗（LangChain） |

**决策流**：
```
>10-15轮? → Write
已加Write仍有噪声? → 加Select
已加Select成本仍高? → 加Compress
有真正独立子任务? → 考虑Isolate
```

## 三、五大 CE 2026 模式

| 模式 | 来源 | 解决什么问题 | 自习引擎映射 |
|:----|:----|:-----------|:-----------|
| **Progressive Disclosure** | swirlai + Anthropic | 全量指令撑爆窗口 | Skill 触发匹配（80 tokens 发现→275-8000 激活） |
| **Context Compression** | swirlai + Manus | 动作历史积累挤走早期上下文 | R1/R2/R3 门禁前自动压缩边界点 |
| **Context Routing** | swirlai + rephrase | 多领域查询加载全部知识库 | select_domain.py priority × freshness 路由 |
| **Retrieval Evolution** | swirlai | 固定 RAG 管道无法处理复杂查询 | learning skill 的源头优先 + 交叉验证 |
| **Tool Management** | swirlai + design.dev | 所有工具暴露导致的窗口占用 | 按需 skill_view 加载 |

## 四、GitHub 规则文件生态（工业标准）

| 文件 | 位置 | 功能 | 最佳长度 |
|:----|:----|:----|:-------:|
| `agents.md` | 仓库根 | Linux Foundation AAF 标准，定义 AI 身份/边界/工作流 | 800-1,500 词 |
| `copilot-instructions.md` | `.github/` | 项目级全局 AI 指令（AI 的文档，非人类文档） | 500-1,000 词 |
| `*.prompt.md` | `.github/prompts/` | 版本控制的可复用任务模板 | 200-800 词 |

**agents.md 五大核心元素**（QubitTool 分析）：
1. **Identity** — 你是谁？项目中扮演的角色
2. **Knowledge** — 熟悉哪些目录/模块/技术栈
3. **Boundaries** — 禁止行为 + 限制条件
4. **Workflow** — 开始执行前的检查清单
5. **Communication** — 语言 / 格式 / 汇报约定

**最佳实践**（多源验证）：
- 命令式语言（"Always use..."）应用率 94% vs 描述式 73%（Anthropic）
- 代码示例效果最佳，硬编码函数名/文件路径
- Commands 段最重要——没有它 AI 浪费 tokens 猜测构建系统
- 子目录放置额外 agents.md 实现 monorepo 模块级规则

## 五、Hermes 规则文件对照

| Hermes 文件 | CE 2.0 对应 | 功能 |
|:-----------|:-----------|:----|
| `AGENTS.md` (项目根) | agents.md | 强制工作流规则 |
| `SOUL.md` (.hermes/) | 组织层规则 | 身份/行为准则/铁律 |
| `SKILL.md` (每个 skill) | *.prompt.md | 任务模板 + 触发条件 + 流程 |
| `.hermes/config.yaml` | copilot-instructions.md | 全局配置指令 |

## 六、三/四层上下文架构

**组织层**：安全/合规基线（最高优先级，不可被 override）
**项目层**：技术栈、架构约束、核心模式
**个人层**：语言偏好、编码风格、沟通习惯

冲突解决：个人 > 项目 > 组织，**安全/合规始终获胜**。

**Context Studios 8 层模型**：
1. Core Role / Policy（稳定，可缓存）
2. Task Goal + Acceptance Tests
3. Constraints + Output Contract
4. Working Set（当前所需最小事实）
5. Tools（仅相关，按需加载）
6. Memory / State（仅相关，非全部历史）
7. Evidence（带来源标记的检索片段）
8. Safety Wrapper（指令/数据分离 + 注入扫描）

## 七、参考来源

| 来源 | URL | 提取价值 |
|:----|:----|:--------|
| appxlab.io (2026-03) | https://blog.appxlab.io/2026/03/27/context-engineering-ai-agents/ | 四模式 + 决策框架 + 代码示例 |
| qubittool.com (2026) | https://qubittool.com/blog/context-engineering-2-system-architecture | CE 2.0 范式 + agents.md 标准 + 三层架构 |
| swirlai.com (2026-03-22) | https://www.newsletter.swirlai.com/p/state-of-context-engineering-in-2026 | 五大模式 + Manus 实践细节 + 压缩策略 |
| contextstudios.ai (2026) | https://www.contextstudios.ai/blog/context-engineering-how-to-build-reliable-llm-systems-by-designing-the-context | 8 层上下文包 + 11 步指南 + 预算分配 |
| rephrase-it.com (2026) | https://rephrase-it.com/blog/7-steps-to-context-engineering-2026 | 7 步迁移 + 分层模板 + 质量门 |
| design.dev (2026) | https://design.dev/guides/context-engineering/ | 跨平台配置对照 + AGENTS.md 标准细则 |
