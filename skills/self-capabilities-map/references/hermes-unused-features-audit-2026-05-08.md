# Hermes Agent 未启用功能审计报告

> 审计日期: 2026-05-08
> 最后更新: 2026-05-09 (深度审计 v2 — 全面验证 + Batch 2+3 完成)
> 审计方法: `hermes status` + `hermes tools list` + `hermes plugins list` + `hermes memory status` + `hermes config check` + `hermes mcp list` + `hermes profile list` + `hermes curator status` + `hermes skills browse --source official` (4 页全量) + `hermes --help` (全部子命令) + `hermes insights --days 30` + `hermes logs --since 24h` + `hermes backup -q` + `hermes checkpoints status` + `hermes curator run --dry-run` + 源码扫描 + config.yaml 全文解析
> 环境: Ubuntu 22.04, Hermes Agent v0.10.0 (pip editable install), 飞书/微信网关运行中
> 当前状态: 工具集 23/23 全部启用 ✅ | 插件 3/3 全部启用 ✅ | 官方 Skill ~15/65 已安装 ✅ | Profile 3 个 (default/research/experiment)

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

### ✅ Batch 2 (2026-05-09) — 已完成

| # | 变更项 | 类型 | 验证 |
|:---:|:---|:---:|:---:|
| 1 | `security.website_blocklist.enabled: true` | 配置 | ✅ hermes config check |
| 2 | `delegation.subagent_auto_approve: true` | 配置 | ✅ hermes config check |
| 3 | `hermes dashboard` 探索 | CLI | ✅ 运行中 PID 2425614 :9119 |
| 4 | `hermes insights --days 30` 使用分析 | CLI | ✅ 381 sessions/6,431 tool calls/1B tokens |
| 5 | `hermes backup -q` 快速备份 | CLI | ✅ 快照 created |
| 6 | `hermes checkpoints status` 快照检查 | CLI | ✅ 0 B 存储 |
| 7 | `hermes curator run --dry-run` 预览 | CLI | ✅ 1 候选 skill |
| 8 | `hermes logs --since 24h` 日志查看 | CLI | ✅ 发现 OpenRouter SSL 错误 |
| 9 | `hermes completion bash` 补全脚本 | CLI | ✅ 已验证 |
| 10 | `hermes profile list + show` 多 Profile | CLI | ✅ 3 个 Profile |

**关键发现**: OpenRouter SSL 错误 — `model_catalog.enabled: true` 每 24h 尝试同步 OpenRouter 模型列表失败 (国内网络). 可以考虑禁用或调整 `ttl_hours`.

### ✅ Batch 3 (2026-05-09) — 已完成

| # | 变更项 | 类型 | 验证 |
|:---:|:---|:---:|:---:|
| 1 | `video` 工具集启用 | CLI | ✅ FFmpeg 6.1.1 已预装 |
| 2 | `rl` 工具集启用 | CLI | ✅ 需 TINKER_API_KEY + WANDB_API_KEY |
| 3 | `spotify` 工具集启用 | CLI | ✅ 需 OAuth 认证 |
| 4 | `yuanbao` 工具集启用 | CLI | ✅ .env 已有 YUANBAO_ALLOW_ALL_USERS |
| 5 | `homeassistant` 工具集启用 | CLI | ✅ 需配置 HA 地址 |
| 6 | `google_meet` 插件启用 | CLI | ✅ 需 Chrome + Google 登录 |
| 7 | `spotify` 插件启用 | CLI | ✅ 配套工具集 |
| 8 | 安装 12 个官方 skill | CLI | ✅ duckduckgo/agentmail/1password/memento/concept-diagrams/sherlock/1-3-1/adversarial-ux/fitness-nutrition/blackbox/canvas/docker-mgmt/searxng |

**经验教训**:
- `hermes tools enable <name>` — 无需确认, 直接成功
- `hermes skills install <name>` — 需要 `--yes` 或 `yes |` 跳过确认
- `hermes plugins enable <name>` — 无需确认, 直接成功
- `hermes-achievements` 和 `observability` 插件在此版本未打包

## 一、已启用工具集 (23/23 — 全部启用 ✅)

当前已启用全部 23 个工具集: web, browser, terminal, file, code_execution, vision, **video**, image_gen, **moa**, tts, skills, todo, memory, session_search, clarify, delegation, cronjob, messaging, **rl**, **homeassistant**, **spotify**, **yuanbao**

> 全部工具集已在 Batch 1-3 中陆续启用。rl/spotify/yuanbao/homeassistant 需额外配置才能完全生效。

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

## 三、已启用插件 (3/3 — 全部启用 ✅)

### 3.1 disk-cleanup ✅ 已启用 (Batch 1)
### 3.2 google_meet ✅ 已启用 (Batch 3)
### 3.3 spotify ✅ 已启用 (Batch 3)

> 所有 bundled 插件已全部启用。`hermes-achievements` 和 `observability/langfuse` 在此版本未打包。
描述: 自动跟踪和清理临时文件（测试脚本、temp 输出、cron 日志）
启用: hermes plugins enable disk-cleanup ✅
状态: 已启用
价值: 省磁盘空间，自动维护
```

> 所有 bundled 插件已全部启用。`hermes-achievements` 和 `observability/langfuse` 在此版本未打包。

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

## 五、已探索的 CLI 功能 (2026-05-09 深度审计)

| # | 命令 | 说明 | 状态 |
|:---:|:---|:---|:---:|
| 1 | `hermes dashboard` | Web UI 管理面板 (port 9119) | ✅ 运行中 (PID 2425614) |
| 2 | `hermes --tui` | React/Ink 终端交互式 UI | ⏳ 待尝试 |
| 3 | `hermes insights` | Token/成本/工具使用趋势分析 | ✅ 已验证 (381 sessions/1B tokens) |
| 4 | `hermes acp` | ACP 服务器 — VS Code/Zed/JetBrains | ⏳ 待尝试 |
| 5 | `hermes auth` | 凭证池管理 | ⏳ 待尝试 |
| 6 | `hermes profile` | 多 Profile 隔离 | ✅ 3 个存在 (default/experiment/research) |
| 7 | `hermes kanban` | SQLite 任务看板 | ⏳ 待尝试 |
| 8 | `hermes webhook` | 动态 Webhook 订阅 | ⏳ 待尝试 |
| 9 | `hermes backup` | 配置备份 | ✅ 已验证 (quick snapshot) |
| 10 | `hermes checkpoints` | 文件快照管理 | ✅ 已验证 (0 B) |
| 11 | `hermes logs` | 高级日志过滤 | ✅ 已验证 (发现 OpenRouter SSL 错误) |
| 12 | `hermes curator run` | 手动技能审查 | ✅ 已验证 (dry-run) |
| 13 | `hermes config migrate` | 配置升级 | ⏳ 待尝试 |
| 14 | `hermes config check` | 配置健康检查 | ⏳ 待尝试 |
| 15 | `hermes doctor --fix` | 全量诊断+自动修复 | ⏳ 待尝试 |
| 16 | `hermes pairing` | 配对码访问控制 | ⏳ 待尝试 |
| 17 | `hermes completion` | Shell 补全生成 | ✅ 已验证 (bash) |
| 18 | `hermes hooks` | Shell 钩子管理 | ⏳ 待尝试 |
| 19 | `hermes debug` | 调试上传 | ⏳ 待尝试 |
| 20 | `hermes mcp serve` | Hermes 作为 MCP Server | ⏳ 待尝试 |
| 21 | `hermes --worktree` | 隔离 git worktree | ⏳ 待尝试 |

## 六、未使用的配置选项 (14 个)

### 推荐开启项 ✅ (Batch 1 已完成 6/6, Batch 2 已完成 2/2)

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

# 6. ✅ 子代理数量 — 3 并发 (Batch 1)

# 7. ✅ 域名黑名单 — 安全防护 (Batch 2)
security:
  website_blocklist:
    enabled: true
    domains: []

# 8. ✅ 子代理自动审批 — 提速 (Batch 2)
delegation:
  subagent_auto_approve: true
```

### 体验优化项 ✅ (Batch 1 已完成 1/3)

```yaml
# 9. ✅ Token 流式输出 (Batch 1)
streaming:
  enabled: true

# 10. CLI 底部状态栏 (⏳ 待启)
display:
  runtime_footer:
    enabled: true
    fields:
      - model
      - context_pct
      - cwd

# 11. 人类打字延迟 (⏳ 待启)
human_delay:
  mode: proportional  # off | uniform | proportional | lognormal
```

### 高级配置项

```yaml
# 12. Terminal 后端切换 — 隔离沙箱执行 (⏳ 待启)
terminal:
  backend: docker  # 可选: local | docker | ssh | singularity | modal | daytona | vercel_sandbox

# 13. Browser 引擎指定 (⏳ 待启)
browser:
  engine: camofox  # auto | playwright | camofox

# 14. 模型目录自动更新 (⏳ 待启)
model_catalog:
  enabled: true  # 已启用，可按需扩展 providers 映射
```

## 七、可安装的官方可选 Skill (~40+)

来源: `hermes skills browse --source official`

### 推荐安装 ✅ (Batch 3 已完成 12 个)

```bash
# ✅ MCP 相关 — 已装
# ✅ 搜索相关 — duckduckgo-search, searxng-search 已装
# ✅ 安全相关 — 1password, sherlock 已装
# ✅ 其他 — agentmail, memento-flashcards, concept-diagrams, one-three-one-rule,
#           adversarial-ux-test, fitness-nutrition, blackbox, canvas,
#           docker-management 已装
```

### 仍可安装的推荐 (全量 65 个中 ~50 个未装)

```bash
# 🔬 Research
hermes skills install scrapling        # Web 爬虫
hermes skills install parallel-cli     # 并行 CLI 工具

# 🛡️ Security
hermes skills install oss-forensics    # 供应链调查/证据恢复

# 🏭 Productivity
hermes skills install shopify          # Shopify 管理
hermes skills install siyuan           # SiYuan 笔记集成
hermes skills install telephony        # 电话能力

# 🌐 Web Development
hermes skills install page-agent       # 网页 Agent 集成

# 🧪 ML Ops / 训练
hermes skills install peft-fine-tuning # LoRA 微调
hermes skills install simpo-training   # 偏好优化
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
