---
name: self-capabilities-map
description: "boku（小玛/Emma）对 Hermes Agent 完整能力边界的认知地图。涵盖已掌握能力、未利用能力、能力限制、可扩展方向。当 boku 需要评估自己能否完成某项任务时，先加载此 skill 进行能力匹配。"
version: 1.0.0
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
depends_on:
  - hermes-self-analysis
  - web-access
  - skill-creator
referenced_by: []
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

## 二、boku 尚未利用的能力（可以立即启用）

### 🟢 立即可用（无需额外安装）

| 能力 | 说明 | 使用场景 |
|------|------|----------|
| **@ Context References** | 消息中 @ 引用文件/文件夹/git diff/URL | 引用外部内容注入上下文 |
| **Checkpoint & Rollback** | 文件变更前自动快照，/rollback 回滚 | 安全修改文件 |
| **Process 管理** | 后台进程全生命周期管理 | 长任务监控、服务器守护 |
| **多 Profile** | 隔离运行多个 Hermes 实例 | 不同场景隔离 |
| **Skins** | CLI 主题切换 | 视觉定制 |
| **Moa Toolset** | Mixture of Agents 混合策略 | 复杂任务多模型协作 |
| **Debugging Toolset** | 专用调试工具 | 问题诊断 |
| **Safe Toolset** | 安全操作工具 | 危险操作防护 |

### 🟡 需要配置（环境变量或 CLI 设置）

| 能力 | 说明 | 启用方式 |
|------|------|----------|
| **Honcho Memory** | 跨会话辩证用户建模 | 安装 Honcho 插件 |
| **外部 Memory Provider** | Mem0/Supermemory 等 | 配置 memory provider |
| **Docker Terminal** | 隔离终端执行 | `hermes config set terminal.backend docker` |
| **SSH Terminal** | 远程服务器执行 | 配置 SSH 凭证 |
| **Web UI Dashboard** | `hermes web` 管理面板 | 安装 `[web]` 依赖 |
| **ACP 编辑器集成** | VS Code/Zed/JetBrains | 安装 `[acp]` 依赖 |
| **API Server** | OpenAI 兼容 HTTP 端点 | 配置 API_SERVER_ENABLED |
| **MCP Server 模式** | 让其他 Agent 消费 boku | `hermes mcp serve` |
| **Voice Mode** | Telegram/Discord 语音回复 | 配置 TTS provider |
| **Discord VC** | 加入语音频道实时对话 | 安装 discord.py[voice] |
| **Spotify** | 音乐控制 | 配置 Spotify API |

### 🔴 需要开发/学习

| 能力 | 说明 | 难度 |
|------|------|------|
| **自定义 Plugin** | 开发新工具/钩子/集成 | 中等（Python） |
| **自定义 MCP Server** | 创建 MCP 服务器暴露工具 | 中等（任意语言） |
| **自定义 Context Engine** | 替换上下文管理策略 | 高级 |
| **RL 训练数据生成** | 批量生成训练轨迹 | 高级 |
| **Batch Processing** | 批量 prompt 执行 | 中等 |
| **Gateway Hook** | 自定义消息处理流程 | 中等 |
| **自定义 Tool** | 添加新的内置工具 | 高级 |
| **自定义 Skin** | 创建 CLI 主题 | 简单（YAML） |
| **Composio MCP** | 连接 1000+ 服务 | 简单（配置） |

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
- `run_agent.py` — AIAgent 核心循环 (~13,700 行)
- `cli.py` — 终端 UI (~11,500 行)
- `gateway/run.py` — 消息网关 (~12,200 行)
- `hermes_state.py` — SQLite 会话存储 (FTS5)
- `tools/registry.py` — 61 工具 / 52 toolsets 注册中心
- `mcp_tool.py` — MCP 客户端 (~3,100 行)

### 数据流
```
入口(CLI/Gateway/Cron/ACP) → AIAgent → Prompt Builder → Provider Resolution
→ API 调用 → Tool Dispatch → 结果追加 → 循环 → 持久化到 SQLite
```

### 7 种 Terminal Backend
local, docker, ssh, singularity, modal, daytona, vercel_sandbox

### 20 种消息平台适配器
telegram, discord, slack, whatsapp, signal, matrix, mattermost, email, sms,
dingtalk, feishu, wecom, weixin, bluebubbles, qqbot, homeassistant, webhook, api_server, yuanbao

### 4 种 API Mode
chat_completions, codex_responses, anthropic_messages, bedrock_converse

---

## 六、boku 的进化路线图

### 短期（立即）
- [x] 建立完整能力认知地图（本文件）
- [x] 学习 Process 管理用于长任务监控
- [x] 学习 Docker Terminal 隔离执行
- [x] 学习 Web UI Dashboard
- [ ] 启用 @ Context References 用法

### 中期（1-2 周）
- [ ] 学习 Honcho Memory 跨会话建模
- [ ] 学习自定义 Plugin 开发
- [ ] 学习 MCP Server 创建

### 长期（1 个月+）
- [ ] 开发自定义 Plugin
- [ ] 创建自定义 MCP Server
- [ ] 探索 RL 训练数据生成
- [ ] 通过 Composio MCP 连接 1000+ 服务
---

**⚠️ Red Flags**：
- 不要凭记忆判断能力边界，每次评估前加载此 skill
- 遇到"不能做"的事情，先查此 map 确认是硬限制还是软限制
- 发现新能力时，及时更新此 map 和 hermes-self-analysis
