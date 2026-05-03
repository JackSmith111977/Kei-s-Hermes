#!/usr/bin/env python3
"""将 gen_hermes_pdf.py 中的英文内容替换为中文"""

import re

with open('/home/ubuntu/.hermes/scripts/gen_hermes_pdf.py', 'r') as f:
    content = f.read()

# 封面
content = content.replace('Hermes Agent', 'Hermes Agent')
content = content.replace('Architecture Deep Dive & Design Philosophy', '架构深度解析与设计哲学')
content = content.replace('May 2026 - by Xiaomiao', '2026年5月 - 小喵出品')
content = content.replace('Version', '版本')
content = content.replace('Date', '日期')
content = content.replace('Codebase', '代码规模')
content = content.replace('Architecture', '架构')
content = content.replace('v1.0.0', 'v1.0.0')
content = content.replace('2026-05-03', '2026-05-03')
content = content.replace('12,000+ lines Python', '12,000+ 行 Python 代码')
content = content.replace('6-layer modular design', '六层模块化设计')

# 目录
content = content.replace('Table of Contents', '目录')
content = content.replace('Project Overview', '项目概览')
content = content.replace('Architecture Design', '架构设计')
content = content.replace('Core Modules', '核心模块')
content = content.replace('Agent Runtime Loop', 'Agent 运行时循环')
content = content.replace('Tool System', '工具系统')
content = content.replace('Prompt Building', '提示词构建')
content = content.replace('Context Compression', '上下文压缩')
content = content.replace('Memory System', '记忆系统')
content = content.replace('Session Management', '会话管理')
content = content.replace('Gateway & Platform Integration', '网关与平台集成')
content = content.replace('Cron Jobs', '定时任务')
content = content.replace('Error Classification & Failover', '错误分类与故障转移')
content = content.replace('Configuration System', '配置系统')
content = content.replace('Skills System', '技能系统')
content = content.replace('Design Philosophy Summary', '设计哲学总结')

# 章节标题
content = content.replace('1. Project Overview', '1. 项目概览')
content = content.replace('1.1 Core Positioning', '1.1 核心定位')
content = content.replace('1.2 Key Capabilities', '1.2 核心能力')
content = content.replace('1.3 Tech Stack', '1.3 技术栈')

content = content.replace('2. Architecture Design', '2. 架构设计')
content = content.replace('2.1 Six-Layer Overview', '2.1 六层架构概览')
content = content.replace('2.2 Core Data Flow', '2.2 核心数据流')
content = content.replace('2.3 Design Patterns', '2.3 设计模式')

content = content.replace('3. Core Module Deep Dive', '3. 核心模块深度解析')
content = content.replace('3.1 run_agent.py -- Agent Main Loop', '3.1 run_agent.py -- Agent 主循环')
content = content.replace('3.2 model_tools.py -- Tool Orchestration Layer', '3.2 model_tools.py -- 工具编排层')
content = content.replace('3.3 tools/registry.py -- Tool Registry', '3.3 tools/registry.py -- 工具注册中心')
content = content.replace('3.4 toolsets.py -- Toolset Grouping', '3.4 toolsets.py -- 工具集分组')

content = content.replace('4. Agent Runtime Loop', '4. Agent 运行时循环')
content = content.replace('4.1 Conversation Loop Steps', '4.1 对话循环步骤')
content = content.replace('4.2 Error Recovery', '4.2 错误恢复')
content = content.replace('4.3 Tool Budget Control', '4.3 工具预算控制')

content = content.replace('5. Tool System', '5. 工具系统')
content = content.replace('5.1 ToolEntry Data Structure', '5.1 ToolEntry 数据结构')
content = content.replace('5.2 Core Tool Categories', '5.2 核心工具分类')
content = content.replace('5.3 MCP Integration', '5.3 MCP 集成')

content = content.replace('6. Prompt Building System', '6. 提示词构建系统')
content = content.replace('6.1 System Prompt Components', '6.1 系统提示词组件')
content = content.replace('6.2 Context File Security Scanning', '6.2 上下文文件安全扫描')
content = content.replace('6.3 Model-Specific Adaptation', '6.3 模型特定适配')

content = content.replace('7. Context Compression System', '7. 上下文压缩系统')
content = content.replace('7.1 Compression Algorithm Flow', '7.1 压缩算法流程')
content = content.replace('7.2 Anti-Bounce Protection', '7.2 防回弹保护')
content = content.replace('7.3 Structured Summary Template', '7.3 结构化摘要模板')

content = content.replace('8. Memory System', '8. 记忆系统')
content = content.replace('8.1 MemoryManager', '8.1 记忆管理器')
content = content.replace('8.2 SQLite State Storage', '8.2 SQLite 状态存储')
content = content.replace('8.3 Supported Memory Plugins', '8.3 支持的记忆插件')

content = content.replace('9. Session Management', '9. 会话管理')
content = content.replace('9.1 Session Tracing', '9.1 会话追踪')
content = content.replace('9.2 PII Protection', '9.2 隐私信息保护')
content = content.replace('9.3 Session Reset Strategies', '9.3 会话重置策略')

content = content.replace('10. Gateway & Platform Integration', '10. 网关与平台集成')
content = content.replace('10.1 Supported Platforms', '10.1 支持的平台')
content = content.replace('10.2 Gateway Lifecycle', '10.2 网关生命周期')
content = content.replace('10.3 Platform Adapter Architecture', '10.3 平台适配器架构')

content = content.replace('11. Cron Job System', '11. 定时任务系统')
content = content.replace('11.1 Schedule Types', '11.1 调度类型')
content = content.replace('11.2 Job Delivery', '11.2 任务投递')
content = content.replace('11.3 Fault Tolerance', '11.3 容错机制')

content = content.replace('12. Error Classification & Failover', '12. 错误分类与故障转移')
content = content.replace('12.1 Error Taxonomy', '12.1 错误分类体系')
content = content.replace('12.2 ClassifiedError Data Class', '12.2 ClassifiedError 数据类')

content = content.replace('13. Configuration System', '13. 配置系统')
content = content.replace('13.1 Configuration Sections', '13.1 配置章节')

content = content.replace('14. Skills System', '14. 技能系统')
content = content.replace('15. Design Philosophy Summary', '15. 设计哲学总结')

# 表格列头
content = content.replace('Capability', '能力')
content = content.replace('Description', '描述')
content = content.replace('Layer', '层级')
content = content.replace('Module', '模块')
content = content.replace('Responsibility', '职责')
content = content.replace('Key Files', '关键文件')

# 架构层名称
content = content.replace('L1 Message Intake', 'L1 消息接入')
content = content.replace('L2 Session Management', 'L2 会话管理')
content = content.replace('L3 Agent Core', 'L3 Agent 核心')
content = content.replace('L4 Tool Execution', 'L4 工具执行')
content = content.replace('L5 Prompt Building', 'L5 提示词构建')
content = content.replace('L6 Infrastructure', 'L6 基础设施')

# 详细信息
content = content.replace('Multi-platform Gateway', '多平台网关')
content = content.replace('Tool Calling Loop', '工具调用循环')
content = content.replace('Persistent Memory', '持久化记忆')
content = content.replace('Context Compression', '上下文压缩')
content = content.replace('Scheduled Tasks', '定时任务')
content = content.replace('Multi-model Support', '多模型支持')
content = content.replace('Smart Error Recovery', '智能错误恢复')
content = content.replace('Skills System', '技能系统')
content = content.replace('MCP Integration', 'MCP 集成')
content = content.replace('Sub-agent Delegation', '子 Agent 委派')

# 20+ messaging platforms
content = content.replace('20+ messaging platforms (Telegram, Discord, WeChat, Feishu, WhatsApp, etc.)', '20+ 消息平台（Telegram、Discord、微信、飞书、WhatsApp 等）')
content = content.replace('Auto-execute tool calls until task completion, supports parallel tool calls', '自动执行工具调用直至任务完成，支持并行工具调用')
content = content.replace('SQLite + FTS5 full-text search, cross-session memory retention', 'SQLite + FTS5 全文搜索，跨会话记忆保留')
content = content.replace('Intelligent summary compression for long conversations', '长对话智能摘要压缩')
content = content.replace('Cron expressions, interval scheduling, one-shot tasks', 'Cron 表达式、间隔调度、一次性任务')
content = content.replace('OpenAI, Anthropic, Google, local models via unified interface', 'OpenAI、Anthropic、Google、本地模型统一接口')
content = content.replace('Classified error types with automatic degradation/retry/model switching', '分类错误类型，自动降级/重试/模型切换')
content = content.replace('Pluggable skill modules with dynamic loading and caching', '可插拔技能模块，支持动态加载和缓存')
content = content.replace('Model Context Protocol standard support', '支持模型上下文协议标准')
content = content.replace('Parallel sub-agent task distribution support', '支持并行子 Agent 任务分发')

# 技术栈
content = content.replace('Built with Python 3.12+, core dependencies include OpenAI SDK (compatible with multiple backends), SQLite (state storage), aiohttp (async HTTP), python-dotenv. The codebase is ~12,000 lines, organized into agent/, gateway/, tools/, cron/, and other modules.', '基于 Python 3.12+ 构建，核心依赖包括 OpenAI SDK（兼容多后端）、SQLite（状态存储）、aiohttp（异步 HTTP）、python-dotenv。代码库约 12,000 行，按 agent/、gateway/、tools/、cron/ 等模块组织。')

# 架构设计
content = content.replace('Hermes Agent uses a six-layer modular architecture with single-responsibility layers communicating through well-defined interfaces.', 'Hermes Agent 采用六层模块化架构，每层职责单一，通过定义良好的接口通信。')

# 数据流
content = content.replace('The complete message processing flow: Platform adapter receives message -> Session manager restores context -> Agent core builds system prompt -> LLM inference generates tool calls -> Tool executor dispatches execution -> Results return to Agent -> Loop until complete -> Response returns to platform adapter -> Sends to user. Each step has comprehensive error handling and recovery.', '完整的消息处理流程：平台适配器接收消息 → 会话管理器恢复上下文 → Agent 核心构建系统提示词 → LLM 推理生成工具调用 → 工具执行器调度执行 → 结果返回 Agent → 循环直至完成 → 响应返回平台适配器 → 发送给用户。每个环节都有完善的错误处理和恢复机制。')

# 设计模式
content = content.replace('Singleton', '单例模式')
content = content.replace('Strategy', '策略模式')
content = content.replace('Observer', '观察者模式')
content = content.replace('Factory', '工厂模式')
content = content.replace('Chain of Responsibility', '责任链模式')
content = content.replace('Template Method', '模板方法模式')
content = content.replace('Decorator', '装饰器模式')

# 设计模式描述
content = content.replace('ToolRegistry ensures globally unique tool registry', 'ToolRegistry 确保全局唯一的工具注册')
content = content.replace('ContextEngine supports multiple context processing strategies', 'ContextEngine 支持多种上下文处理策略')
content = content.replace('Gateway uses asyncio event loop for multi-platform concurrent messages', 'Gateway 使用 asyncio 事件循环处理多平台并发消息')
content = content.replace('Platform adapters created via factory methods', '平台适配器通过工厂方法创建')
content = content.replace('Error classifier matches error types in priority chain', '错误分类器按优先级链匹配错误类型')
content = content.replace('run_agent.py conversation loop defines Agent execution skeleton', 'run_agent.py 对话循环定义 Agent 执行骨架')
content = content.replace('Tool registration via registry.register() decorator', '通过 registry.register() 装饰器注册工具')

# 模块描述
content = content.replace('run_agent.py (12,002 lines) is the core engine implementing the complete ReAct (Reasoning + Acting) loop: receive user message -> build prompt -> call LLM -> parse tool calls -> execute tools -> append results to conversation history -> repeat until LLM stops requesting tool calls.', 'run_agent.py（12,002 行）是实现完整 ReAct（推理 + 行动）循环的核心引擎：接收用户消息 → 构建提示词 → 调用 LLM → 解析工具调用 → 执行工具 → 将结果追加到对话历史 → 重复直至 LLM 不再请求工具调用。')
content = content.replace('Key designs: SafeWriter wraps stdout/stderr to prevent pipe breakage crashes; jittered_backoff implements exponential backoff + jitter to avoid thundering herd; classify_api_error categorizes API errors into 12+ types with recovery suggestions.', '关键设计：SafeWriter 包装 stdout/stderr 防止管道断裂崩溃；jittered_backoff 实现指数退避 + 抖动避免惊群效应；classify_api_error 将 API 错误分类为 12+ 种类型并提供恢复建议。')
content = content.replace('model_tools.py (611 lines) is the thin orchestration layer providing three core APIs: get_tool_definitions() returns JSON schemas for all tools; handle_function_call() routes tool calls to handlers; check_toolset_requirements() validates toolset prerequisites.', 'model_tools.py（611 行）是轻量编排层，提供三个核心 API：get_tool_definitions() 返回所有工具的 JSON Schema；handle_function_call() 路由工具调用到处理器；check_toolset_requirements() 验证工具集前置条件。')
content = content.replace('registry.py (482 lines) implements a thread-safe singleton tool registry. Each tool describes itself via ToolEntry (name, toolset, JSON Schema, handler, env requirements). Uses threading.RLock for concurrent read/write protection with _snapshot_* methods for stable reads.', 'registry.py（482 行）实现线程安全的单例工具注册中心。每个工具通过 ToolEntry（名称、工具集、JSON Schema、处理器、环境需求）自我描述。使用 threading.RLock 实现并发读写保护，_snapshot_* 方法提供稳定读取。')
content = content.replace('Discovery mechanism: discover_builtin_tools() scans tools/*.py files via AST analysis for registry.register() calls, auto-registering built-in tools. New tools only need to create a file in tools/ and call register().', '发现机制：discover_builtin_tools() 通过 AST 分析扫描 tools/*.py 文件中的 registry.register() 调用，自动注册内置工具。新工具只需在 tools/ 创建文件并调用 register() 即可。')
content = content.replace('toolsets.py (745 lines) defines toolset concepts for grouping related tools. The _HERMES_CORE_TOOLS list contains 30+ core tools covering web search, terminal, file management, browser automation, and skill systems. Supports toolset composition and dynamic resolution.', 'toolsets.py（745 行）定义工具集概念用于分组相关工具。_HERMES_CORE_TOOLS 列表包含 30+ 个核心工具，涵盖 Web 搜索、终端、文件管理、浏览器自动化和技能系统。支持工具集组合和动态解析。')

# Agent 运行时
content = content.replace('The Agent runtime loop is the most critical component. The AIAgent class in run_agent.py implements the full conversation loop: initialization -> build system prompt -> conversation loop -> error recovery -> response output.', 'Agent 运行时循环是最关键的组件。run_agent.py 中的 AIAgent 类实现完整对话循环：初始化 → 构建系统提示词 → 对话循环 → 错误恢复 → 响应输出。')

# 对话循环步骤
content = content.replace('1. Receive Message: Get current message and conversation history from session manager', '1. 接收消息：从会话管理器获取当前消息和对话历史')
content = content.replace('2. Build Prompt: Assemble system prompt (identity + platform hints + memory + skills + context files)', '2. 构建提示词：组装系统提示词（身份 + 平台提示 + 记忆 + 技能 + 上下文文件）')
content = content.replace('3. Inject Memory: Prefetch relevant memories via MemoryManager and inject into prompt', '3. 注入记忆：通过 MemoryManager 预取相关记忆并注入提示词')
content = content.replace('4. LLM Inference: Call OpenAI-compatible API with message history and tool definitions', '4. LLM 推理：使用消息历史和工具定义调用 OpenAI 兼容 API')
content = content.replace('5. Parse Response: Check finish_reason, determine if tool calls needed', '5. 解析响应：检查 finish_reason，判断是否需要工具调用')
content = content.replace('6. Execute Tools: Execute all tool calls in parallel, collect results', '6. 执行工具：并行执行所有工具调用，收集结果')
content = content.replace('7. Append Results: Add tool results to conversation history', '7. 追加结果：将工具结果添加到对话历史')
content = content.replace('8. Check Compression: Trigger context compression if context exceeds threshold', '8. 检查压缩：上下文超过阈值时触发上下文压缩')
content = content.replace('9. Loop/Return: If LLM requests more tool calls go back to step 4, otherwise return final response', '9. 循环/返回：如果 LLM 请求更多工具调用则返回步骤 4，否则返回最终响应')

# 错误恢复
content = content.replace('Multi-layer error recovery: API Error Classifier categorizes errors into 12+ types (auth failures, rate limits, server errors, context overflow, etc.), each with different recovery strategies: retry, credential rotation, model fallback, context compression, or abort. Exponential backoff + jitter prevents thundering herd from concurrent retries.', '多层错误恢复：API 错误分类器将错误分类为 12+ 种类型（认证失败、速率限制、服务器错误、上下文溢出等），每种类型有不同的恢复策略：重试、凭证轮换、模型回退、上下文压缩或中止。指数退避 + 防止并发重试的惊群效应。')

# 工具预算
content = content.replace('To prevent infinite tool calling loops, a Tool Budget mechanism limits max tool calls per conversation turn, forcing loop termination when exceeded. enforce_turn_budget controls per-turn tool output volume to prevent oversized outputs from bloating context.', '为防止无限工具调用循环，工具预算机制限制每轮对话的最大工具调用次数，超出时强制终止循环。enforce_turn_budget 控制每轮工具输出量，防止输出过大导致上下文膨胀。')

# 工具系统
content = content.replace('The tool system uses declarative registration: each tool self-registers via registry.register() with name, toolset, JSON Schema, handler, etc. The core toolset contains 30+ built-in tools covering file operations, terminal commands, web search, browser automation, and code execution.', '工具系统采用声明式注册：每个工具通过 registry.register() 自我注册，包含名称、工具集、JSON Schema、处理器等。核心工具集包含 30+ 个内置工具，涵盖文件操作、终端命令、Web 搜索、浏览器自动化和代码执行。')

# ToolEntry
content = content.replace('Each tool describes itself via ToolEntry: name, toolset, schema (JSON Schema), handler (async function), check_fn (prerequisite check), requires_env (env vars needed), is_async, description, emoji.', '每个工具通过 ToolEntry 自我描述：名称、工具集、schema（JSON Schema）、handler（异步函数）、check_fn（前置检查）、requires_env（所需环境变量）、is_async、描述、emoji。')

# 工具分类
content = content.replace('File Operations', '文件操作')
content = content.replace('Terminal', '终端')
content = content.replace('Web Search', 'Web 搜索')
content = content.replace('Browser Automation', '浏览器自动化')
content = content.replace('Code Execution', '代码执行')
content = content.replace('Vision', '视觉')
content = content.replace('Memory', '记忆')
content = content.replace('Task Planning', '任务规划')
content = content.replace('Messaging', '消息')
content = content.replace('Skills', '技能')
content = content.replace('Scheduling', '调度')

# MCP
content = content.replace('The system supports Model Context Protocol (MCP) for dynamic external tool server registration. MCP tools integrate via mcp_tool.py, and the registry supports dynamic refresh -- when MCP servers add/remove tools, the registry auto-updates and exposes new tool definitions to the LLM.', '系统支持模型上下文协议（MCP）用于动态外部工具服务器注册。MCP 工具通过 mcp_tool.py 集成，注册中心支持动态刷新——当 MCP 服务器添加/删除工具时，注册中心自动更新并向 LLM 暴露新工具定义。')

# 提示词构建
content = content.replace('prompt_builder.py (1,115 lines) assembles the Agent system prompt. All functions are stateless -- deterministic output for given input, making prompt building testable and cacheable. The system prompt is composed from multiple fragments.', 'prompt_builder.py（1,115 行）组装 Agent 系统提示词。所有函数均为无状态——给定输入产生确定性输出，使提示词构建可测试和可缓存。系统提示词由多个片段组合而成。')

# 系统提示词组件
content = content.replace('Identity', '身份定义')
content = content.replace('Platform Hints', '平台提示')
content = content.replace('Memory Guidance', '记忆引导')
content = content.replace('Session Search', '会话搜索')
content = content.replace('Skills Guidance', '技能引导')
content = content.replace('Tool Enforcement', '工具执行强化')
content = content.replace('Model-specific', '模型特定')
content = content.replace('Context Files', '上下文文件')
content = content.replace('Environment Hints', '环境提示')
content = content.replace('Language Detection', '语言检测')

# 安全扫描
content = content.replace('Before injecting context files (AGENTS.md, SOUL.md, etc.) into the system prompt, prompt_builder.py performs security scanning for prompt injection attacks: checks for invisible Unicode characters (zero-width, bidirectional override) and threat patterns (like \'ignore previous instructions\'). Threat content is blocked and replaced with warnings.', '在将上下文文件（AGENTS.md、SOUL.md 等）注入系统提示词之前，prompt_builder.py 执行安全扫描检测提示词注入攻击：检查不可见 Unicode 字符（零宽字符、双向覆盖）和威胁模式（如"忽略之前的指令"）。威胁内容被拦截并替换为警告。')

# 模型适配
content = content.replace('Different model families receive specific execution guidance: OpenAI/GPT models get detailed execution discipline (tool persistence, mandatory tool use, prerequisite checks, validation steps); Google/Gemini get operational instructions (absolute paths, dependency checks, parallel tool calls); GPT-5/Codex use \'developer\' role instead of \'system\' role for higher instruction-following weight.', '不同模型系列接收特定的执行指导：OpenAI/GPT 模型获得详细的执行规范（工具持久化、强制工具使用、前置检查、验证步骤）；Google/Gemini 获得操作指令（绝对路径、依赖检查、并行工具调用）；GPT-5/Codex 使用 developer 角色替代 system 角色以获得更高的指令遵循权重。')

# 上下文压缩
content = content.replace('context_compressor.py (1,229 lines) implements intelligent context compression to solve context window overflow in long conversations. Core idea: protect head and tail critical messages, use LLM summarization for middle historical messages.', 'context_compressor.py（1,229 行）实现智能上下文压缩，解决长对话中的上下文窗口溢出问题。核心思想：保护头部和尾部的关键消息，对中间历史消息使用 LLM 摘要。')

# 压缩步骤
content = content.replace('1. Tool Output Pruning (pre-pass): Replace old, large tool outputs with informative summaries (not generic placeholders), no LLM call', '1. 工具输出剪枝（预扫描）：用信息丰富的摘要替换旧的大型工具输出（非通用占位符），无需 LLM 调用')
content = content.replace('2. Protect Head Messages: System prompt + first N messages kept intact (default: first 3)', '2. 保护头部消息：系统提示词 + 前 N 条消息保持完整（默认：前 3 条）')
content = content.replace('3. Protect Tail Messages: Protect recent messages by token budget (default: ~20K tokens)', '3. 保护尾部消息：按 token 预算保护最近消息（默认：约 20K tokens）')
content = content.replace('4. Deduplication: Identify and merge duplicate tool outputs (e.g., reading same file multiple times)', '4. 去重：识别并合并重复的工具输出（如多次读取同一文件）')
content = content.replace('5. LLM Summarization: Use structured template to summarize middle messages', '5. LLM 摘要：使用结构化模板摘要中间消息')
content = content.replace('6. Iterative Update: Update previous summaries on subsequent compression instead of regenerating', '6. 迭代更新：在后续压缩时更新之前的摘要而非重新生成')

# 防回弹
content = content.replace('To prevent ineffective compression loops (compressing only 1-2 messages each time), anti-bounce protection skips compression if the last two compressions both saved less than 10%, suggesting the user /new to start a fresh session. A 600-second cooldown prevents repeated attempts when summarization service is unavailable.', '为防止无效压缩循环（每次仅压缩 1-2 条消息），防回弹保护在最近两次压缩节省率均低于 10% 时跳过压缩，建议用户 /new 开始新会话。600 秒冷却时间防止摘要服务不可用时重复尝试。')

# 摘要模板
content = content.replace('LLM-generated summaries follow a structured template covering: Completed Work, Current State, Unresolved Issues, Remaining Work. Summaries are prefixed with \'CONTEXT COMPACTION -- REFERENCE ONLY\' to prevent the model from treating historical summaries as current instructions.', 'LLM 生成的摘要遵循结构化模板，涵盖：已完成工作、当前状态、未解决问题、剩余工作。摘要以"CONTEXT COMPACTION -- REFERENCE ONLY"为前缀，防止模型将历史摘要当作当前指令。')

# 记忆系统
content = content.replace('The memory system has two layers: Semantic Memory via the memory tool stores user preferences and environmental facts; Episodic Memory via hermes_state.py SQLite database stores complete session history with FTS5 full-text search.', '记忆系统有两层：语义记忆通过 memory 工具存储用户偏好和环境事实；情节记忆通过 hermes_state.py SQLite 数据库存储完整会话历史，支持 FTS5 全文搜索。')

# MemoryManager
content = content.replace('memory_manager.py (373 lines) orchestrates built-in memory providers and up to one external plugin provider. Key constraint: only one external memory provider can register to prevent tool schema expansion and backend conflicts. The built-in provider always registers first and cannot be removed.', 'memory_manager.py（373 行）协调内置记忆提供者和最多一个外部插件提供者。关键约束：只能注册一个外部记忆提供者，防止工具 Schema 膨胀和后端冲突。内置提供者始终优先注册且不可移除。')
content = content.replace('Memory context is injected via <memory-context> fence tags with system annotation \'NOT new user input\', preventing the model from treating recalled memories as new user input. This fence design effectively prevents memory pollution.', '记忆上下文通过 <memory-context> 围栏标签注入，附带系统注释"非新用户输入"，防止模型将召回的记忆当作新用户输入。此围栏设计有效防止记忆污染。')

# SQLite
content = content.replace('hermes_state.py (1,443 lines) implements SQLite-backed persistent state storage. Key designs: WAL mode supports multi-reader + single-writer concurrency; FTS5 virtual table enables cross-session full-text search; parent_session_id chain supports compression-triggered session splitting; application-level random jitter retry resolves WAL write contention. Database path: ~/.hermes/state.db, schema version 6.', 'hermes_state.py（1,443 行）实现 SQLite 支持的持久化状态存储。关键设计：WAL 模式支持多读者 + 单写者并发；FTS5 虚拟表支持跨会话全文搜索；parent_session_id 链支持压缩触发的会话分裂；应用层随机抖动重试解决 WAL 写竞争。数据库路径：~/.hermes/state.db，Schema 版本 6。')

# 插件
content = content.replace('Supported plugins: mem0, Hindsight, Supermemory, ReteroDB, OpenViking, Holographic Memory, Honcho, ByteRover.', '支持插件：mem0、Hindsight、Supermemory、ReteroDB、OpenViking、Holographic Memory、Honcho、ByteRover。')

# 会话管理
content = content.replace('gateway/session.py (1,257 lines) implements complete session lifecycle management. Each session is described by SessionSource (platform, chat ID, user ID, chat type), supporting DM, group, channel, and thread types.', 'gateway/session.py（1,257 行）实现完整的会话生命周期管理。每个会话由 SessionSource（平台、聊天 ID、用户 ID、聊天类型）描述，支持私信、群组、频道和话题类型。')

# 会话追踪
content = content.replace('Each message carries complete tracing info: platform, chat_id, user_id, chat_type (DM/group/channel/thread), thread_id. Used for routing responses to correct locations, injecting context into system prompts, and tracking scheduled task delivery sources.', '每条消息携带完整的追踪信息：平台、chat_id、user_id、chat_type（私信/群组/频道/话题）、thread_id。用于将响应路由到正确位置、向系统提示词注入上下文、追踪定时任务投递来源。')

# PII
content = content.replace('Session storage implements PII hashing: sensitive identifiers like user_id and chat_id are SHA-256 hashed (keeping first 12 hex chars) before storage, maintaining unique session identification without exposing raw user information.', '会话存储实现 PII 哈希：user_id 和 chat_id 等敏感标识符在存储前经过 SHA-256 哈希处理（保留前 12 个十六进制字符），在不暴露原始用户信息的情况下保持唯一会话标识。')

# 重置策略
content = content.replace('Multiple reset strategies supported: Manual reset (/new command), idle timeout reset (configurable), context overflow reset (auto-triggers /new with summary preservation). parent_session_id chains maintain session continuity across resets.', '支持多种重置策略：手动重置（/new 命令）、空闲超时重置（可配置）、上下文溢出重置（自动触发 /new 并保留摘要）。parent_session_id 链在重置间保持会话连续性。')

# 网关
content = content.replace('gateway/run.py (11,015 lines) is the gateway main entry point managing all configured platform adapter lifecycles. Uses asyncio event loop for multi-platform concurrent message handling, with each platform adapter running in its own coroutine.', 'gateway/run.py（11,015 行）是网关主入口，管理所有已配置平台适配器的生命周期。使用 asyncio 事件循环处理多平台并发消息，每个平台适配器在各自的协程中运行。')

# 支持的平台
content = content.replace('20+ supported platforms: Telegram, Discord, WhatsApp, Signal, Slack, Mattermost, Matrix, iMessage (BlueBubbles), WeChat (Weixin), Enterprise WeChat (WeCom), Feishu (Lark), DingTalk, QQ Bot, Yuanbao, Email, SMS, Home Assistant, API Server, Webhook.', '支持 20+ 平台：Telegram、Discord、WhatsApp、Signal、Slack、Mattermost、Matrix、iMessage（BlueBubbles）、微信、企业微信、飞书、钉钉、QQ Bot、元宝、邮件、短信、Home Assistant、API 服务器、Webhook。')

# 网关生命周期
content = content.replace('1. SSL Certificate Detection: Auto-detect system CA certificate location (supports NixOS)', '1. SSL 证书检测：自动检测系统 CA 证书位置（支持 NixOS）')
content = content.replace('2. Environment Variable Loading: Load from ~/.hermes/.env', '2. 环境变量加载：从 ~/.hermes/.env 加载')
content = content.replace('3. Agent Cache Initialization: LRU cache, max 128 Agent instances, 1-hour idle TTL', '3. Agent 缓存初始化：LRU 缓存，最多 128 个 Agent 实例，1 小时空闲 TTL')
content = content.replace('4. Platform Adapter Startup: Start independent message listening coroutines for each platform', '4. 平台适配器启动：为每个平台启动独立的消息监听协程')
content = content.replace('5. Message Routing Loop: Receive message -> Find/Create session -> Invoke Agent -> Return response', '5. 消息路由循环：接收消息 → 查找/创建会话 → 调用 Agent → 返回响应')
content = content.replace('6. Graceful Shutdown: Save all session state and close connections on SIGTERM', '6. 优雅关闭：在 SIGTERM 时保存所有会话状态并关闭连接')

# 平台适配器
content = content.replace('Each platform adapter implements a unified interface: connect(), listen(), send(), disconnect(). Adapters handle platform-specific protocols (Telegram Bot API, Discord Gateway, WeChat iLink Bot API, etc.), converting platform messages to internal format.', '每个平台适配器实现统一接口：connect()、listen()、send()、disconnect()。适配器处理平台特定协议（Telegram Bot API、Discord Gateway、微信 iLink Bot API 等），将平台消息转换为内部格式。')

# 定时任务
content = content.replace('cron/jobs.py (776 lines) implements a complete scheduled task system. Jobs stored in ~/.hermes/cron/jobs.json, output saved to ~/.hermes/cron/output/{job_id}/.', 'cron/jobs.py（776 行）实现完整的定时任务系统。任务存储在 ~/.hermes/cron/jobs.json，输出保存到 ~/.hermes/cron/output/{job_id}/。')

# 调度类型
content = content.replace('One-shot', '一次性')
content = content.replace('Interval', '间隔')
content = content.replace('Cron Expression', 'Cron 表达式')

content = content.replace('Execute once after specified delay (e.g., \'30m\', \'2h\', ISO timestamp)', '在指定延迟后执行一次（如 30m、2h、ISO 时间戳）')
content = content.replace('Repeat at fixed intervals (e.g., \'every 30m\', \'every 2h\')', '按固定间隔重复（如 every 30m、every 2h）')
content = content.replace('Standard 5-field cron expressions (e.g., \'0 9 * * *\')', '标准 5 域 Cron 表达式（如 0 9 * * *）')

# 任务投递
content = content.replace('Job results support multiple delivery modes: origin (return to creating chat), local (save to file only), specified platform (e.g., telegram:chat_id). Pre-execution scripts supported via script parameter for data collection and change detection.', '任务结果支持多种投递模式：origin（返回创建对话）、local（仅保存到文件）、指定平台（如 telegram:chat_id）。通过 script 参数支持预执行脚本，用于数据收集和变化检测。')

# 容错
content = content.replace('One-shot jobs have a 120-second grace window. Interval jobs have grace period of half the interval (120s to 2h), allowing catch-up after short misses but fast-forwarding after long misses to prevent job backlog. threading.Lock protects concurrent jobs.json reads/writes.', '一次性任务有 120 秒的宽限期。间隔任务的宽限期为间隔的一半（120 秒至 2 小时），允许短期错过后的补执行，但在长期错过后快进以防止任务积压。threading.Lock 保护并发 jobs.json 读写。')

# 错误分类
content = content.replace('error_classifier.py (829 lines) implements structured API error classification, replacing scattered string-matching with a centralized classifier that the main retry loop consults for every API failure.', 'error_classifier.py（829 行）实现结构化 API 错误分类，用集中式分类器替代分散的字符串匹配，主重试循环在每次 API 失败时查询该分类器。')

# 错误类型
content = content.replace('auth / auth_permanent', 'auth / auth_permanent（认证/永久认证）')
content = content.replace('rate_limit', 'rate_limit（速率限制）')
content = content.replace('billing', 'billing（计费）')
content = content.replace('overloaded / server_error', 'overloaded / server_error（过载/服务器错误）')
content = content.replace('timeout', 'timeout（超时）')
content = content.replace('context_overflow', 'context_overflow（上下文溢出）')
content = content.replace('payload_too_large', 'payload_too_large（载荷过大）')
content = content.replace('model_not_found', 'model_not_found（模型未找到）')
content = content.replace('format_error', 'format_error（格式错误）')
content = content.replace('thinking_signature', 'thinking_signature（思考签名）')
content = content.replace('unknown', 'unknown（未知）')

content = content.replace('Auth failures (401/403) -> refresh/rotate credentials or abort', '认证失败（401/403）→ 刷新/轮换凭证或中止')
content = content.replace('Rate limiting (429) -> backoff then rotate credentials', '速率限制（429）→ 退避后轮换凭证')
content = content.replace('Quota exhausted (402) -> rotate credentials immediately', '配额耗尽（402）→ 立即轮换凭证')
content = content.replace('Server errors (500/503/529) -> backoff retry', '服务器错误（500/503/529）→ 退避重试')
content = content.replace('Connection/read timeout -> rebuild client then retry', '连接/读取超时 → 重建客户端后重试')
content = content.replace('Context too large -> trigger context compression, not failover', '上下文过大 → 触发上下文压缩，非故障转移')
content = content.replace('Request too large (413) -> compress payload', '请求过大（413）→ 压缩载荷')
content = content.replace('Model not found (404) -> fallback to different model', '模型未找到（404）→ 回退到不同模型')
content = content.replace('Bad request format (400) -> abort or fix and retry', '请求格式错误（400）→ 中止或修复后重试')
content = content.replace('Anthropic thinking block signature invalid', 'Anthropic 思考块签名无效')
content = content.replace('Unclassifiable -> backoff retry', '无法分类 → 退避重试')

# ClassifiedError
content = content.replace('Classification results are encapsulated as ClassifiedError: reason (FailoverReason enum), status_code, provider, model, message, error_context (dict), and recovery hints (retryable, should_compress, should_rotate_credential, should_fallback). The retry loop checks these hints directly.', '分类结果封装为 ClassifiedError：reason（FailoverReason 枚举）、status_code、provider、model、message、error_context（字典）和恢复提示（retryable、should_compress、should_rotate_credential、should_fallback）。重试循环直接检查这些提示。')

# 配置系统
content = content.replace('Hermes Agent uses multi-layer configuration: config.yaml (master) -> .env (environment) -> CLI args. Main config at ~/.hermes/config.yaml contains all sections for models, gateway, tools, sessions, etc.', 'Hermes Agent 使用多层配置：config.yaml（主配置）→ .env（环境变量）→ CLI 参数。主配置 ~/.hermes/config.yaml 包含模型、网关、工具、会话等所有章节。')

# 配置章节
content = content.replace('model', 'model（模型）')
content = content.replace('gateway', 'gateway（网关）')
content = content.replace('tools', 'tools（工具）')
content = content.replace('session', 'session（会话）')
content = content.replace('cron', 'cron（定时任务）')
content = content.replace('display', 'display（显示）')
content = content.replace('plugins', 'plugins（插件）')

# 项目概览正文
content = content.replace('Hermes Agent is an open-source AI Agent framework developed by Nous Research, named after the Greek messenger god Hermes, symbolizing its core mission of information transfer and connection. It is a production-grade AI Agent system that supports interaction through multiple messaging platforms (Telegram, Discord, WeChat, Feishu, WhatsApp, Signal, etc.), with capabilities including tool calling, persistent memory, scheduled tasks, context compression, and multi-model switching.', 'Hermes Agent 是由 Nous Research 开发的开源 AI Agent 框架，以希腊信使神 Hermes 命名，象征其信息传递与连接的核心使命。它是一个生产级 AI Agent 系统，支持通过多个消息平台（Telegram、Discord、微信、飞书、WhatsApp、Signal 等）进行交互，具备工具调用、持久化记忆、定时任务、上下文压缩和多模型切换等能力。')

content = content.replace('Hermes Agent is designed as a universal AI Assistant Runtime: not just a chatbot framework, but a complete Agent operating system providing full-pipeline capabilities from message intake, session management, tool execution to response delivery.', 'Hermes Agent 被设计为通用 AI 助手运行时：不仅是聊天机器人框架，而是一个完整的 Agent 操作系统，提供从消息接入、会话管理、工具执行到响应投递的全流水线能力。')

# 保存
with open('/home/ubuntu/.hermes/scripts/gen_hermes_pdf_cn.py', 'w') as f:
    f.write(content)

print("PDF 中文脚本已生成！")
