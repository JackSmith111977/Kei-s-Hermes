# Hermes Agent 未启用功能审计报告

> 审计日期: 2026-05-08
> 最后更新: 2026-05-08 (Batch 1 升级后)
> 审计方法: `hermes status` + `hermes tools list` + `hermes plugins list` + `hermes memory status` + 源码扫描
> 环境: Ubuntu 22.04, Hermes Agent (git install), 飞书/微信网关运行中

## 批次升级记录

### ✅ Batch 1 (2026-05-08) — 已完成

| # | 变更项 | 类型 | 验证 |
|:---:|:---|:---:|:---:|
| 1 | `privacy.redact_pii: true` | 配置 | ✅ |
| 2 | `sessions.auto_prune: true` | 配置 | ✅ |
| 3 | `updates.pre_update_backup: true` | 配置 | ✅ |
| 4 | `tool_loop_guardrails.hard_stop_enabled: true` | 配置 | ✅ |
| 5 | `streaming.enabled: true` | 配置 | ✅ |
| 6 | `delegation.max_spawn_depth: 2` | 配置 | ✅ |
| 7 | `moa` 工具集启用 | CLI | ✅ |
| 8 | `disk-cleanup` 插件启用 | CLI | ✅ |

### ⏳ Batch 2 (待计划)

候选项目: `hermes dashboard`, `hermes auth` 凭证池, `hermes profile`, `hermes insights`, `google_meet` 插件, 外部内存提供商

## 一、已禁用工具集 (5 个 + 1 个已启用 ✅)

当前已启用: web, browser, terminal, file, code_execution, vision, image_gen, tts, skills, todo, memory, session_search, clarify, delegation, cronjob, messaging, **moa** ✅
当前已禁用: video, rl, homeassistant, spotify, yuanbao

### 1.1 moa — Mixture of Agents ✅ 已启用 (Batch 1)

```
描述: 多模型混合推理策略
启用: hermes tools enable moa ✅
状态: 已启用
价值: 让多个模型共同推理一个任务，提高答案质量和深度
依赖: 需要多 API Key 或多模型访问
```

### 1.2 rl — RL Training (Tinker-Atropos)

```
描述: 强化学习训练工具集
工具列表: rl_list_environments, rl_select_environment, rl_get_current_config,
          rl_edit_config, rl_start_training, rl_check_status,
          rl_stop_training, rl_get_results, rl_list_runs, rl_test_inference
环境: HermesAgentBaseEnv → TerminalTestEnv / HermesSweEnv / TerminalBench2EvalEnv
启用: hermes tools enable rl
价值: 可对 boku 进行 RL 训练优化
依赖: Atropos 框架（已内置）
```

### 1.3 video — Video Analysis

```
描述: 视频分析
启用: hermes tools enable video
依赖: 需要安装视频处理依赖
```

### 1.4 homeassistant — Home Assistant

```
描述: 智能家居控制
启用: hermes tools enable homeassistant
依赖: 需要 Home Assistant 实例
```

### 1.5 spotify — Spotify (工具集版)

```
描述: Spotify 音乐控制
启用: hermes tools enable spotify
另注: 还有一个单独的 spotify 插件（hermes plugins list）
```

### 1.6 yuanbao — Yuanbao

```
描述: 元宝 AI 群的 reader/translator 钩子
启用: hermes tools enable yuanbao
```

## 二、未配置的消息平台 (20 个)

gateway/platforms/ 目录中存在的平台适配器：

| # | 平台 | 适配器文件 | 状态 |
|:---:|:---|:---|:---:|
| 1 | Telegram | telegram.py | not configured |
| 2 | Discord | discord.py | not configured |
| 3 | Slack | slack.py | not configured |
| 4 | WhatsApp | whatsapp.py | not configured |
| 5 | Signal | signal.py | not configured |
| 6 | Matrix | matrix.py | not configured |
| 7 | Mattermost | mattermost.py | not configured |
| 8 | Email | email.py | not configured |
| 9 | SMS | sms.py | not configured |
| 10 | DingTalk | dingtalk.py | not configured |
| 11 | WeCom | wecom.py | not configured |
| 12 | WeCom Callback | wecom_callback.py | not configured |
| 13 | BlueBubbles (iMessage) | bluebubbles.py | not configured |
| 14 | QQBot | qqbot/ | not configured |
| 15 | Home Assistant | homeassistant.py | not configured |
| 16 | Webhook | webhook.py | not configured |
| 17 | API Server | api_server.py | not configured |
| 18 | Yuanbao | yuanbao.py | not configured |
| 19 | Feishu Comment | feishu_comment.py | not configured (飞书本身已配) |
| 20 | WhatsApp (另) | whatsapp.py | not configured |

## 三、未启用的插件 (5 个)

### 3.1 disk-cleanup ✅ 已启用 (Batch 1)

```
描述: 自动跟踪和清理临时文件（测试脚本、temp 输出、cron 日志）
启用: hermes plugins enable disk-cleanup ✅
状态: 已启用
价值: 省磁盘空间，自动维护
```

### 3.2 google_meet

```
描述: 加入 Google Meet 会议，实时转写字幕，语音回复，事后跟进
模式: v1 转写-only, v2 realtime 双工 (OpenAI Realtime + BlackHole/PulseAudio),
      v3 远程节点 (网关在 Linux, Chrome 在 Mac)
启用: hermes plugins enable google_meet
工具: audio_bridge.py, cli.py, meet_bot.py, process_manager.py, realtime/, tools.py
价值: 自动参加会议并做摘要
依赖: Google Meet 访问 + Chrome
```

### 3.3 spotify (插件版)

```
描述: 7 个工具（播放、设备、队列、搜索、播放列表、专辑、库）
      使用 Spotify Web API + PKCE OAuth
启用: hermes plugins enable spotify; hermes auth spotify
工具: client.py, tools.py
```

### 3.4 hermes-achievements

```
描述: 游戏化成就系统
启用: hermes plugins enable hermes-achievements
目录: dashboard/, docs/, tests/
价值: 让使用 Hermes 更有趣
```

### 3.5 observability/langfuse

```
描述: LLM 可观测性追踪（Langfuse）
启用: hermes plugins enable observability 或手动启用 langfuse 子插件
价值: 追踪 LLM 调用、延迟、成本
依赖: Langfuse API Key
```

## 四、未使用的内存提供商 (8 个已安装)

honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb

所有 8 个内存插件位于 `~/.hermes/hermes-agent/plugins/memory/`。
当前仅使用内置内存（`memory` 工具 + `session_search`）。
启用外部提供商可实现跨会话用户建模。

### 推荐: honcho 🥇

```
描述: 跨会话辩证用户建模
类型: API Key / Local
启用: hermes plugins enable honcho (需先通过 hermes memory setup 配置)
价值: 记住用户长期偏好、行为模式
```

## 五、未使用的 CLI 功能 (11 个)

| # | 命令 | 说明 | 尝试命令 |
|:---:|:---|:---|:---|
| 1 | `hermes dashboard` | Web UI 管理面板 | `hermes dashboard --port 9119` |
| 2 | `hermes --tui` | React/Ink TUI | `hermes --tui` |
| 3 | `hermes insights` | 使用分析 | `hermes insights --days 30` |
| 4 | `hermes acp` | ACP 服务器 | `hermes acp` |
| 5 | `hermes auth` | 凭证池管理 | `hermes auth add` |
| 6 | `hermes profile` | 多 Profile | `hermes profile create dev` |
| 7 | `hermes config migrate` | 配置迁移 | `hermes config migrate` |
| 8 | `hermes config check` | 配置检查 | `hermes config check` |
| 9 | `hermes doctor --fix` | 自动修复 | `hermes doctor --fix` |
| 10 | `hermes pairing` | 配对码管理 | `hermes pairing list` |
| 11 | `hermes completion` | Shell 补全 | `hermes completion bash` |

## 六、未使用的配置选项 (10 个)

### 推荐开启项 ✅ (Batch 1 已完成 6/6)

```yaml
# 1. ✅ 安全脱敏 — 保护用户隐私 (Batch 1)
privacy:
  redact_pii: true

# 2. ✅ 自动清理会话 — 省磁盘 (Batch 1)
sessions:
  auto_prune: true
  retention_days: 90

# 3. ✅ 工具循环保护 — 防止无限循环 (Batch 1)
tool_loop_guardrails:
  hard_stop_enabled: true
  warnings_enabled: true

# 4. ✅ 更新前备份 — 安全升级 (Batch 1)
updates:
  pre_update_backup: true

# 5. ✅ 子代理深度提升 — 更复杂的并行任务 (Batch 1)
delegation:
  max_spawn_depth: 2

# 6. 域名黑名单 — 安全防护 (⏳ 待启)
security:
  website_blocklist:
    enabled: true
    domains: []
```

### 体验优化项 ✅ (Batch 1 已完成 2/2)

```yaml
# 7. ✅ Token 流式输出 (Batch 1)
streaming:
  enabled: true

# 8. CLI 底部状态栏 (⏳ 待启)
display:
  runtime_footer:
    enabled: true
    fields:
      - model
      - context_pct
      - cwd
```

## 七、可安装的官方可选 Skill (~40+)

来源: `hermes skills browse --source official`

### 推荐安装

```bash
# 🥇 MCP 相关
hermes skills install fastmcp      # 开发 MCP Server
hermes skills install mcporter     # MCP 代理

# 🥇 搜索相关
hermes skills install searxng-search   # 自托管搜索引擎
hermes skills install duckduckgo-search # 备用搜索引擎

# 🥇 安全相关
hermes skills install 1password    # 密码管理集成
hermes skills install sherlock     # 用户名搜索
```

### 完整类别列表

```
autonomous-ai-agents/  — blackbox, honcho
blockchain/            — base, solana
communication/         — one-three-one-rule
creative/              — 创意技能
devops/                — DevOps 技能
dogfood/               — 吃狗粮技能
email/                 — 邮件技能
health/                — fitness-nutrition, neuroskill-bci
mcp/                   — fastmcp, mcporter (核心!)
migration/             — openclaw-migration
mlops/                 — ML Ops 技能
productivity/          — canvas, here-now, memento-flashcards, shop-app, shopify, siyuan, telephony
research/              — bioinformatics, domain-intel, drug-discovery, duckduckgo-search,
                         gitnexus-explorer, parallel-cli, qmd, scrapling, searxng-search
security/              — 1password, oss-forensics, sherlock
web-development/       — page-agent
```

## 八、架构级未探索能力

### 8.1 Atropos RL 训练管线

```
文件: ~/.hermes/hermes-agent/environments/
架构:
  Atropos BaseEnv
    └── HermesAgentBaseEnv
          ├── TerminalTestEnv (栈测试)
          ├── HermesSweEnv (SWE 训练)
          └── TerminalBench2EvalEnv (TB2 评估)

用途: 对 Hermes agent 进行强化学习训练
入口: hermes tools enable rl → rl_start_training
```

### 8.2 MCP Server 模式

```bash
# 让其他 Agent (Claude Code / Cursor 等) 消费 boku 的能力
hermes mcp serve
```

### 8.3 API Server 模式

```bash
# OpenAI 兼容 HTTP 端点 — 任何兼容 OpenAI SDK 的工具都可调用 boku
# 配置: 在 config.yaml 中启用 api_server 平台
```

### 8.4 Worktree 模式

```bash
# 隔离 git worktree 并行运行多个 Hermes Agent
hermes --worktree
```

### 8.5 Context Engine 插件

```
文件: ~/.hermes/hermes-agent/plugins/context_engine/
状态: 仅 __init__.py，空壳待填
可自定义: 替换默认的 compressor 上下文引擎
```

### 8.6 Gateway 内置钩子

```
文件: ~/.hermes/hermes-agent/gateway/builtin_hooks/
状态: 空目录
可添加: pre_llm_call, on_session_start 等 10+ 钩子
```

### 8.7 Batch Runner

```
文件: ~/.hermes/hermes-agent/batch_runner.py (~1,287 行)
用途: 并行批处理 — 同时处理多个 prompt
```

---

> 此文件是 `self-capabilities-map` skill 的审计参考。
> 下次大版本升级后应重新运行审计（`hermes config check` + `hermes status`）。
