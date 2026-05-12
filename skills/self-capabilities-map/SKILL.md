---
name: self-capabilities-map
description: "boku（小玛/Emma）对 Hermes Agent 完整能力边界的认知地图。涵盖已掌握能力、未利用能力、能力限制、可扩展方向。当 boku 需要评估自己能否完成某项任务时，先加载此 skill 进行能力匹配。"
version: 2.2.0
triggers:
  - boku 能做什么
  - 能力边界
  - Hermes 还能做什么
  - 自我评估
  - 能力盘点
  - 可以做什么
  - 能做到什么程度
  - Hermes capability
  - 扩展能力
  - 还能学什么
  - 未启用功能
  - 未使用功能
  - 隐藏功能
  - 能力审计
  - 功能盘点
depends_on:
  - hermes-self-analysis
  - web-access
  - skill-creator
referenced_by:
  - hermes-self-analysis
design_pattern: Inversion
skill_type: research
---

# boku 的能力边界认知地图 (Self-Capabilities Map)

> **用途**：当 boku 需要评估自己能否完成某项任务时，先查此地图确认能力覆盖范围。
> **核心原则**：知己才能更好地发挥所长、规避短板。

---

## 一、boku 的现有能力清单（已掌握 ✅）

### 核心工具（日常使用）
- `terminal` — shell 命令执行（local backend）
- `read_file` / `write_file` / `patch` / `search_files` — 文件操作
- `execute_code` — Python 沙箱执行（可调用 hermes_tools）
- `delegate_task` — 子代理并行任务（默认 3 个并发）
- `memory` / `session_search` — 持久记忆与跨会话搜索
- `cronjob` — 定时任务管理
- `send_message` — 跨平台消息（飞书/微信）
- `browser_*` — 10 个浏览器自动化工具
- `vision_analyze` / `image_generate` / `text_to_speech` — 多媒体
- `todo` / `clarify` — 任务追踪与用户确认
- `mcp_tavily_*` — Tavily 搜索/提取/爬取/映射
- `skill_view` / `skill_manage` / `skills_list` — Skill 管理
- `process` — 后台进程管理（list/poll/wait/log/kill/write）

### 已有 Skill 生态

> ⚠️ 以下分类是**示例性**的，不是穷举列表。完整覆盖需执行 `find ~/.hermes/skills -name "SKILL.md" -maxdepth 3 | wc -l` 获取总数 + 逐项归类。真实能力覆盖约 **185 个技能 / 18 个领域**（详见 `capability-pack-design`）。

| 领域 | Skills |
|------|--------|
| 学习体系 | learning-workflow, learning, skill-creator, knowledge-routing |
| 文档排版 | doc-design, pdf-layout, pptx-guide, docx-guide, markdown-guide, html-guide |
| 开发流程 | systematic-debugging, writing-plans, plan, patch-file-safety |
| 运维 | linux-ops-guide, web-access, proxy-monitor |
| GitHub | github-pr-workflow, git-advanced-ops, github-deploy-upload |
| 飞书 | feishu, feishu-send-file |
| 自我认知 | hermes-self-analysis, anti-repetition-loop |
| 金融 | financial-analyst |
| 其他 | delete-safety, mermaid-guide, clash-config |

---

## 二、boku 尚未利用的能力（可以立即启用）— 总计 ~100+ 项

> 📊 完整审计于 2026-05-09 (v2)。根据 `hermes status` + `hermes tools list` + `hermes plugins list` + `hermes config check` + `hermes memory status` + `hermes mcp list` + `hermes profile list` + `hermes curator status` + `hermes skills browse --source official` (全4页) + `hermes --help` (全命令) + 源码扫描 + config.yaml 全文解析。
> 
> **全景快照 (2026-05-09) — Batch 3 完成后**:
> - 工具集: **23/23** enabled ✅ **全部启用！**
> - 插件: **3/3** enabled ✅ (disk-cleanup, google_meet, spotify)
> - 消息平台: **2/20** configured (飞书 + 微信; 18 未配)
> - API Key: **~8/23** configured (~15 未配)
> - CLI 子命令: **~20/36** 已尝试 (~16 未尝试)
> - 官方 Skills: **~15/65** installed (~50 未装)
> - 记忆提供商: **0/8** configured
> - Profile: **3 个存在** (default/experiment/research), 仅 default 使用
> - 外部 MCP: **1 个** (Tavily) 运行中
> - FFmpeg: **已安装** (v6.1.1)
> - Dashboard: **运行中** (PID 2425614 :9119)

### 🟢 工具集（全部 23/23 已启用 ✅）
| 工具集 | 说明 | 状态 | 推荐度 |
|--------|------|:----:|:------:|
| ~~**moa**~~ | ~~Mixture of Agents 多模型混合推理~~ | **✅ Batch 1** | — |
| ~~**video**~~ | ~~视频分析~~ | **✅ Batch 3** — FFmpeg 6.1.1 已装 | — |
| ~~**rl**~~ | ~~RL Training — 强化学习~~ | **✅ Batch 3** — 需 TINKER/WANDB Key | — |
| ~~**spotify**~~ | ~~Spotify 音乐控制~~ | **✅ Batch 3** — 需 OAuth 认证 | — |
| ~~**yuanbao**~~ | ~~元宝 AI 群的钩子~~ | **✅ Batch 3** — 需额外配置 | — |
| ~~**homeassistant**~~ | ~~智能家居控制~~ | **✅ Batch 3** — 需配置 HA 地址 | — |

### 🟢 立即可用 CLI 功能（无需额外安装）

| 命令 | 说明 | 推荐度 |
|------|------|:------:|
| ~~**`hermes dashboard`**~~ | ~~Web UI 管理面板（端口 9119）~~ | **✅ 已启用 (Batch 2)** | — |
| **`hermes --tui`** | React/Ink 终端 UI（交互式控制台） | ⭐⭐⭐ |
| ~~**`hermes insights`**~~ | ~~使用分析 — Token 消耗/成本/工具模式/趋势~~ | **✅ 已启用 (Batch 2)** | — |
| **`hermes acp`** | ACP 服务器 — VS Code / Zed / JetBrains 集成 | ⭐⭐ |
| **`hermes auth`** | 凭证池管理 — 多 API Key 自动轮换/负载均衡 | ⭐⭐ |
| ~~**`hermes backup`**~~ | ~~备份配置~~ | **✅ 已尝试 (Batch 2)** — 快照 `20260508-162119` | — |
| ~~**`hermes checkpoints`**~~ | ~~快照存储管理~~ | **✅ 已尝试 (Batch 2)** — 当前 0 B | — |
| ~~**`hermes curator`**~~ | ~~背景技能维护~~ | **✅ 已尝试 (Batch 2)** — dry-run 已验证 | — |
| ~~**`hermes logs`**~~ | ~~高级日志查看~~ | **✅ 已尝试 (Batch 2)** — 发现 OpenRouter SSL 错误 | — |
| ~~**`hermes profile`**~~ | ~~多 Profile 隔离（3 个存在）~~ | **✅ 已尝试 (Batch 2)** — default/experiment/research | — |
| **`hermes config migrate`** | 升级后自动添加新配置选项 | ⭐⭐ |
| **`hermes config check`** | 检查缺失/过期配置 | ⭐ |
| **`hermes doctor --fix`** | 自动修复检测到的问题 | ⭐ |
| **`hermes pairing`** | 配对码用户访问控制（网关多用户） | ⭐ |
| ~~**`hermes completion`**~~ | ~~Shell 补全脚本生成~~ | **✅ 已尝试 (Batch 2)** | — |

> 查看全部未用 CLI 功能：`hermes --help` 中未尝试过的子命令。

### 🟡 需要配置的架构能力

| 能力 | 说明 | 启用方式 | 推荐度 |
|------|------|----------|:------:|
| **Honcho Memory** | 跨会话用户辩证建模 | `hermes memory setup` → honcho | ⭐⭐⭐ |
| **Mem0 / Supermemory** | 替代内置内存的长期记忆 | `hermes plugins enable` + 配置 | ⭐⭐⭐ |
| ~~**Web UI Dashboard**~~ | ~~浏览器管理 Hermes~~ | **✅ 已启动 (Batch 2)** — PID 2425614 :9119 | — |
| **API Server 模式** | OpenAI 兼容 HTTP 端点 | 配置 `api_server` 平台启用 | ⭐⭐ |
| **MCP Server 模式** | 让其他 Agent (Claude Code 等) 消费 boku | `hermes mcp serve` | ⭐⭐ |
| **Docker Terminal** | 隔离终端沙箱执行 | `hermes config set terminal.backend docker` | ⭐⭐ |
| **SSH Terminal** | 远程服务器执行 | 配置 SSH 凭证 | ⭐⭐ |
| **ACP 编辑器集成** | VS Code / Zed / JetBrains | 安装 `[acp]` 依赖 | ⭐⭐ |
| **Composio MCP** | 连接 1000+ 外部服务 (GitHub/Stripe/Database/Gmail...) | 添加 MCP Server | ⭐⭐ |
| **Worktree 模式** | `hermes --worktree` 隔离 git worktree 并行 Agent | `hermes --worktree` | ⭐⭐ |
| **Batch Runner** | `batch_runner.py` 并行批处理引擎 | 直接调用 | ⭐⭐ |
| **Atropos RL 训练** | HermesAgentBaseEnv / HermesSweEnv 完整 RL 管线 | `hermes tools enable rl` | ⭐⭐ |

### 🟢 插件（全部 3/3 已启用 ✅）

| 插件 | 说明 | 状态 | 推荐度 |
|------|------|:----:|:------:|
| ~~**disk-cleanup**~~ | ~~自动清理临时文件~~ | **✅ Batch 1** | — |
| ~~**google_meet**~~ | ~~Google Meet 转写+语音回复~~ | **✅ Batch 3** — 需 Chrome 登录 | — |
| ~~**spotify**~~ | ~~Spotify 原生集成（7 工具）~~ | **✅ Batch 3** — 需 OAuth 认证 | — |

### 🟡 未配置的消息平台 (20 个)

| 类别 | 平台 | 适配器位置 |
|:---|:---|:---|
| **主流国际** | Telegram · Discord · Slack · WhatsApp · Signal · Matrix · Mattermost | `gateway/platforms/` |
| **通信** | Email · SMS | `gateway/platforms/` |
| **国内** | DingTalk · WeCom · WeCom Callback · QQBot · Yuanbao | `gateway/platforms/` |
| **特殊** | BlueBubbles(iMessage) · Home Assistant | `gateway/platforms/` |
| **无客户端** | **API Server** (OpenAI 兼容 HTTP) · **Webhook Adapter** | `gateway/platforms/` |

### 🟢 配置开关（已启用 8 项 + 剩余 6 项推荐）

| 配置项 | 旧值 | 新值 | 状态 | 作用 |
|:---|:---:|:---:|:----:|:---|
| `privacy.redact_pii` | false | **true** | ✅ Batch 1 | 自动脱敏敏感信息 |
| `streaming.enabled` | false | **true** | ✅ Batch 1 | CLI token 流式输出 |
| `sessions.auto_prune` | false | **true** | ✅ Batch 1 | 自动清理旧会话 |
| `tool_loop_guardrails.hard_stop_enabled` | false | **true** | ✅ Batch 1 | 工具循环硬停止保护 |
| `updates.pre_update_backup` | false | **true** | ✅ Batch 1 | 更新前自动备份 |
| `delegation.max_spawn_depth` | 1 | **2** | ✅ Batch 1 | 子代理嵌套深度提升 |
| `delegation.max_concurrent_children` | 3 | **3** | ✅ 已验证 | 子代理并发数 |
| `orchestrator_enabled` | true | **true** | ✅ 已验证 | 子代理可再 delegate |
| ~~`security.website_blocklist.enabled`~~ | false | **true** | **✅ Batch 2** | 域名黑名单防护 |
| `display.runtime_footer.enabled` | false | — | ⏳ 待启 | CLI 底部显示模型/上下文/路径 |
| ~~`delegation.subagent_auto_approve`~~ | false | **true** | **✅ Batch 2** | 子代理自动审批提速 |
| `human_delay.mode` | off | — | ⏳ 待启 | 模拟人类打字延迟 |
| `terminal.backend` | local | — | ⏳ 待启 | Docker/SSH/Singularity 等沙箱 |
| `browser.engine` | auto | — | ⏳ 待启 | 指定浏览器引擎(camofox等)

### 🟡 可安装的官方可选 Skill（65 个，已安装 ~15 个）

| 领域 | 已安装 | 未安装 |
|:---|:---|:---|
| 🔬 Research | duckduckgo-searxng-search, searxng-search | scrapling, parallel-cli, bioinformatics, drug-discovery, domain-intel, gitnexus-explorer, qmd |
| 🔒 Security | 1password, sherlock | oss-forensics |
| 🔗 MCP | **fastmcp**(已装), **mcporter**(已装) | — |
| 🏭 Productivity | canvas, memento-flashcards, fitness-nutrition | shopify, siyuan, telephony, here-now, shop-app |
| 💬 Communication | one-three-one-rule | — |
| 🤖 Autonomous | honcho(已装), blackbox | — |
| 📧 Email | **agentmail**(已装) | — |
| 🐳 DevOps | **docker-management**(已装) | — |
| 🎭 Special | adversarial-ux-test, concept-diagrams | — |

### 🔴 架构级未探索能力

| 能力 | 说明 | 入口 |
|:---|:---|:---|
| **Context Engine 插件** | 除 compressor 外可写自定义上下文引擎 | `plugins/context_engine/` |
| **Gateway 内置钩子** | `builtin_hooks/` 空位待填 | `gateway/builtin_hooks/` |
| **自定义 Gateway Hook** | pre_llm_call / on_session_start 等 10+ 钩子 | `run_agent.py:10912+` |
| **MCP Composio** | 一键连接 1000+ 外部服务 | `hermes mcp add composio` |
| **自定义 Tool** | 添加新内置工具（3 个文件） | `tools/` + `toolsets.py` + 注册 |
| **自定义 Plugin** | 完整 Python 插件（工具+钩子+CLI） | `plugins/` |
| **RL 训练数据生成** | 批量生成 agent 轨迹用于训练 | `environments/` + Atropos |
| **自定义 Skin** | YAML 驱动的 CLI 主题 | `hermes_cli/skin_engine.py` |

---

## 三、boku 的能力边界（不能做什么 ❌）

### 硬限制
1. **无法自行重启 Gateway** — 可以修改代码，但需要主人手动重启
2. **无法绕过 max_turns=60** — 单次会话最多 60 次 tool 调用
3. **无法在子代理中使用 clarify** — 子代理不能与用户交互
4. **无法跨 profile 共享记忆** — profile 完全隔离
5. **execute_code 沙箱无 .env** — 沙箱隔离，无法访问环境变量
6. **上下文窗口有限** — 压缩会丢失细节，长对话需依赖文件

### 软限制（可通过学习克服）
1. **Python 环境混淆** — venv 3.11 vs 系统 3.12
2. **大信息量处理** — 容易跳过大量搜索结果（解决方案：分批处理）
3. **重复回复循环** — 上下文截断导致遗忘（解决方案：anti-repetition-loop）
4. **Skill 创建过快** — 跳过 skill-creator 流程（解决方案：严格走 pre-flight gate）

---

## 四、Hermes 可扩展能力分层

### 层级 1：配置级（零代码）
- 启用/禁用工具集 per platform
- 切换 Provider 路由策略 / Fallback / Credential Pools
- 切换 Terminal Backend（7 种）
- 添加 MCP Server
- 配置外部 Memory Provider

### 层级 2：Skill 级（Markdown）
- 创建/更新/安装 Skill
- 配置 external_dirs 共享 Skill 库

### 层级 3：Plugin 级（Python）
- 自定义 Plugin（工具 + 钩子）
- Memory Provider Plugin
- Context Engine Plugin
- CLI 子命令 Plugin

### 层级 4：MCP 级（任意语言）
- 自定义 MCP Server
- 集成现有 MCP Server（GitHub, Stripe, FileSystem, Database 等）
- 通过 Composio MCP 连接 1000+ 服务

### 层级 5：核心级（Python）
- 修改/添加内置工具
- 修改 Gateway Adapter
- 修改 Provider Resolution
- 修改 Context Compression 策略

---

## 五、Hermes 架构速查

### 核心文件
- `run_agent.py` — AIAgent 核心循环 (~14,471 行 / 70 个方法)
- `cli.py` — 终端 UI + 命令注册 (~12,508 行 / 36+ 命令)
- `gateway/run.py` — 消息网关控制器 (~15,059 行 / GatewayRunner)
- `batch_runner.py` — 并行批处理引擎 (~1,287 行)
- `hermes_state.py` — SQLite 会话存储 FTS5 (~2,669 行)
- `model_tools.py` — 工具编排 (~847 行)
- `tools/registry.py` — 工具注册中心 (~537 行 / ToolRegistry)
- `mcp_tool.py` — MCP 客户端 (~3,100 行)
- `hermes_constants.py` — 配置路径 (~460 行)

### 项目规模
- **总文件**: 1464 个 Python 文件
- **总代码**: 707,214 行
- **测试**: ~17K 测试 / ~900 测试文件

### 核心架构分层
```
Layer 1 (P0): 核心运行时    — run_agent.py / cli.py / batch_runner.py
Layer 2 (P0): 网关平台      — Gateway / 飞书 / 微信 / Telegram 等 20+ 平台
Layer 3 (P1): 工具系统      — 80+ 内置工具 / 工具注册 / 7 种终端后端
Layer 4 (P1): 插件生态      — Provider / 记忆 / Kanban / 可观测性 / 图片生成
Layer 5 (P2): 数据状态      — SQLite 会话 / 持久记忆 / 日志系统
Layer 6 (P2): 基础设施      — Cron / CLI 子系统 / ACP 适配器 / TUI
Layer 7 (P3): 运行环境      — Local / Docker / SSH / Modal / Singularity
Layer 8 (P3): 测试系统      — 17K 测试 / L0-L4 分级
```

### 数据流
```
入口(CLI/Gateway/Cron/ACP) → AIAgent.run_conversation()
  → SRA 上下文注入 → 构建系统提示缓存 → 预检压缩
  → 主循环: API 调用 ↔ 工具执行 → 持久化到 SQLite
```

### AIAgent 核心设计模式

| 模式 | 说明 | 位置 |
|:---|:---|:---:|
| **懒加载 OpenAI SDK** | 延迟导入 ~240ms，守护进程不崩溃 | run_agent.py:40-86 |
| **迭代预算** | 父子代理共享调用次数上限 | run_agent.py:272-312 |
| **SRA 上下文注入** | 用户消息前注入技能推荐 | run_agent.py:10802 |
| **上下文压缩** | 长对话自动压缩中间轮次 | run_agent.py:10865+ |
| **插件钩子** | pre_llm_call / on_session_start | run_agent.py:10912+ |
| **Fallback 链** | 主模型失败自动降级备用模型 | run_agent.py:~10660 |
| **代理池** | 多 API Key 轮换/负载均衡 | agent/credential_pool.py |
| **Tool Guardrails** | 工具调用安全护栏 | agent/tool_guardrails.py |
| **Checkpoints** | 文件变更前快照，/rollback 回滚 | run_agent.py 内置 |

### 工具调用 3 种模式
- **顺序执行**: `_execute_tool_calls_sequential` — 可靠
- **并行执行**: `_execute_tool_calls_concurrent` — 性能优先
- **自动选择**: `_execute_tool_calls` — 根据配置

### 10 种回调
tool_progress, tool_start, tool_complete, thinking, reasoning, clarify,
step, stream_delta, interim_assistant, tool_gen, status

### 7 种 Terminal Backend
local, docker, ssh, singularity, modal, daytona, vercel_sandbox

### 20+ 种消息平台适配器
telegram, discord, slack, whatsapp, signal, matrix, mattermost, email, sms,
dingtalk, feishu, wecom, weixin, bluebubbles, qqbot, homeassistant, webhook, api_server, yuanbao

### 4 种 API Mode
chat_completions, codex_responses, anthropic_messages, bedrock_converse

---

## 六、boku 的进化路线图

> 📌 最后更新: 2026-05-08 | 已完成能力审计: ~100+ 项未启用功能已映射

### 短期（立即 — 探索性启用）
- [x] 建立完整能力认知地图（本文件）
- [x] 学习 Process 管理用于长任务监控
- [x] 学习 Docker Terminal 隔离执行
- [x] 学习 Web UI Dashboard (`hermes dashboard`)
- [x] **完成 Hermes 能力全面审计** (~100+ 未启用功能映射)
- [x] **第一批升级完成 (2026-05-08)** — 启用 privacy/streaming/auto_prune/hard_stop/pre_update_backup/max_spawn_depth/MoA/disk-cleanup
- [x] **第二批审计完成 (2026-05-09)** — 发现 21 个未用 CLI 子命令、5 个禁用工具集、4 个未启用插件、18 个未配平台、~60 个官方 skill 未安装、3 个 Profile 仅用 1 个
- [ ] 启用 `hermes dashboard --tui` Web 管理面板 + 内嵌聊天
- [ ] 启用 `hermes insights` 使用分析
- [ ] 启用 `security.website_blocklist`
- [ ] 启用 `delegation.subagent_auto_approve`
- [ ] 试用 `hermes backup -q` 快速备份

### 中期（1-2 周 — 深度启用）
- [ ] 学习 Honcho Memory 跨会话建模
- [ ] 启用 `hermes dashboard` Web 管理面板
- [ ] 学习 `hermes profile` 多 Profile 隔离
- [ ] 尝试 `hermes auth` 凭证池管理（多 API Key 轮换）
- [ ] 启用 `hermes dashboard --tui` 嵌入式聊天
- [ ] 学习自定义 Plugin 开发流程
- [ ] 学习 MCP Server 创建（fastmcp / mcporter）

### 长期（1 个月+ — 架构级探索）
- [ ] 开发自定义 Plugin（工具 + 钩子）
- [ ] 创建自定义 MCP Server（暴露 boku 能力给其他 Agent）
- [ ] 通过 Composio MCP 连接 1000+ 服务
- [ ] 探索 RL 训练数据生成（Atropos 管线）
- [ ] 尝试 `hermes acp` 编辑器集成
- [ ] 探索 Batch Runner 并行批处理
- [ ] 尝试 Worktree 模式并行 Agent 协作
- [ ] 探索自定义 Context Engine 插件

## 七、能力审计方法论（如何自己发现新能力）

> 本方法论用于 boku 或主人自行发现 Hermes 中尚未启用的功能。
> 结合批次升级流程使用 — 先审计再升级。

### 审计命令清单

```bash
# 1. 查看已禁用工具集
hermes tools list | grep disabled

# 2. 查看未配置平台
hermes status | grep -i "not configured"

# 3. 查看未启用插件
hermes plugins list | grep "not enabled"

# 4. 查看未登录的 Auth Provider
hermes status | grep -i "not logged\|not set"

# 5. 查看未配置的内存提供商
hermes memory status

# 6. 查看可选 Skills
hermes skills browse --source official

# 7. 查看未使用的 CLI 子命令
hermes --help | grep -v "not found" | xargs -I{} sh -c 'hermes {} --help 2>/dev/null | head -1'

# 8. 查看可用的 MCP Server
hermes mcp list

# 9. 查看未使用的配置选项
hermes config check
```

### 审计原则
1. **先看禁用再看缺失** — `hermes tools list` 比 `hermes status` 更快发现未用能力
2. **平台适配器是最容易被忽略的** — 20+ 平台适配器在 `gateway/platforms/` 中躺着
3. **插件是第二容易被忽略的** — 已安装的插件往往未启用
4. **内存提供商是第三容易被忽略的** — 内存插件已安装但未使用是常见情况
5. **可选 Skills 仓库有 65 个内容** — `hermes skills browse --source official`（4 页)

### 批次升级流程 (Bounded Autonomy 模式)

执行批次启用时的标准工作流：

```text
1. 📋 制定计划 ← 定义 scope/约束/成功指标/回滚路径
2. 🔄 备份配置
3. ⚡ 逐项执行 ← 每个变更后立即验证
4. ✅ 全部验证 ← hermes tools list / grep config / hermes plugins list
5. 🧠 保存记忆 ← 记录变更内容到持久记忆
6. 📝 更新 skill + 参考文件 ← 反映新状态
```

**约束检查模板**（启动批次任务前逐项检查）：
```
⏱️  时间盒: 每步 ≤ 60s，总任务 ≤ 15min
📄  作用域: 只改哪些文件/配置？
📊  成功指标: 怎样算"做好了"？
🔄  回滚路径: 备份确认了？
🚫  自主决策: 什么要问主人？
📋  步骤清单: todo 写好了？
🔌  依赖检查: 外部服务都正常？
```
---

**⚠️ Red Flags**：
- 不要凭记忆判断能力边界，每次评估前加载此 skill
- 遇到"不能做"的事情，先查此 map 确认是硬限制还是软限制
- 发现新能力时，及时更新此 map 和 hermes-self-analysis
- 能力审计结果会随 Hermes 版本升级而变化 — 每次大版本升级后应重新审计

**🚨 已知陷阱 — 能力审计不完整（2026-05-12 新增）**：

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **仅依赖 `self-capabilities-map` 的领域列表** | 遗漏整个能力类别（如知识库/元认知/质量保障） | 必须同时执行 `find ~/.hermes/skills -name SKILL.md \| wc -l` 获取完整技能数 & 逐项手动归类 |
| **按「工具/平台」而非「领域」分类** | 分类碎片化，飞书/微信被归入「工具」而非「消息平台」能力域 | 按「解决什么问题」分类，而非「用什么工具」 |
| **忽略隐性知识体系** | Skills 列表看不到 L1/L2/L3 三层知识库 | 除了扫 SKILL.md，还要检查 `~/.hermes/experiences/` 和 `~/.hermes/brain/` 的存在性 |
| **只计已安装技能，忽略「能力域」完整性** | 声称某模块包含某个技能但该技能未安装 | 审计时注"已安装/可用"状态，非空列表 |

**正确的能力审计流程（v2.0 已验证）**：

```bash
# Step 1: 穷举所有技能
find ~/.hermes/skills -name "SKILL.md" -maxdepth 3 | wc -l

# Step 2: 逐项读取 name + tags + description
for f in $(find ~/.hermes/skills -name "SKILL.md" -maxdepth 3); do
  dir=$(dirname "$f")
  cat "$f" | head -5 | grep -E "^name:|^description:|tags:" | sed 's/name: //'
  echo "  └─ $dir"
done

# Step 3: 按领域归类（参考 capability-pack-design 中的 18 模块分类框架）
# 不要预设分类，让技能自己告诉你它属于哪

# Step 4: 检查隐性知识体系
ls ~/.hermes/experiences/active/ 2>/dev/null | head -5
ls ~/.hermes/brain/wiki/ 2>/dev/null | head -5
```

> 💡 这个陷阱的直接教训来自 2026-05-12 的能力模块化项目：初始版本只列出了 8 个模块（基于 `self-capabilities-map` 的领域列表），被主人指出遗漏了知识库、元认知、质量保障等 10 个完整领域后，重新做穷举扫描 + 手动归类才发现实际有 185 个技能可归为 18 个模块。
