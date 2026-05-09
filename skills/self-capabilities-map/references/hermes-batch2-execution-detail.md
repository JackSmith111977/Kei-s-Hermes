# Batch 2 执行详情 (2026-05-09)

> 附属于 `self-capabilities-map` skill — 作为批次升级的实操案例参考。

---

## 执行流水

```bash
# 1. 审计命令清单
hermes tools list                     # → 18/22 enabled
hermes plugins list                   # → 1/4 enabled
hermes status                         # → 2/20 platforms, ~8/23 API keys
hermes config check                   # → Config v23, all required ✓
hermes memory status                  # → 8 providers available, 0 configured
hermes mcp list                       # → 1 server (tavily)
hermes profile list                   # → 3 profiles: default/research/experiment
hermes curator status                 # → ENABLED, 7d interval, 1 agent-created skill
hermes skills browse --source official --page 1-4  # → 65 official skills
hermes --help                         # → 36 CLI subcommands

# 2. 备份
hermes backup -q -l "pre-batch2"      # → 快照: 20260508-162119-pre-batch2

# 3. 配置变更 (patch config.yaml)
#    security.website_blocklist.enabled: false → true
#    delegation.subagent_auto_approve: false → true

# 4. 探索性 CLI 命令
hermes dashboard --status             # → PID 2425614 运行中, port 9119
hermes insights --days 30             # → 381 sessions, 6,431 tool calls, 1B tokens
hermes checkpoints status             # → 0 B (未触发)
hermes curator run --dry-run          # → 1 candidate, no transitions
hermes logs --since 24h --level INFO  # → 发现 OpenRouter SSL 错误
hermes completion bash                # → 补全脚本可用
hermes profile show research          # → 独立 SOUL.md/.env, 315 skills
hermes profile show experiment        # → 同上，有 shell alias

# 5. 更新记录
memory action=replace ...             # 更新持久记忆
self-capabilities-map v2.1.0 → 2.2.0  # 更新技能
hermes-self-analysis 进化路线图更新     # 标记 Batch 2 完成
```

## 重要发现

### 1. OpenRouter 模型目录 SSL 错误
- **现象**: `hermes logs` 发现每 24h 约 28 条 WARNING:
  `Failed to fetch model metadata from OpenRouter: SSLError(SSLEOFError)`
- **根因**: 国内服务器访问 OpenRouter 的 SSL 连接被中断（GFW 干扰）
- **影响**: `model_catalog` 功能降级 — 动态模型发现不可用；不影响推理
- **缓解方案**:
  - 关闭: `config set model_catalog.enabled false`
  - 或调整重试: `config set model_catalog.ttl_hours 168` (一周同步一次)

### 2. Dashboard 已在运行
- `hermes dashboard --status` 返回 3 个进程
- 端口 9119, 绑定 127.0.0.1
- 可通过 `curl http://127.0.0.1:9119` 访问
- 附带 `--tui` 参数可启用内嵌聊天

### 3. Profile 详情
- **default**: 当前使用，Gateway running
- **research**: 独立 SOUL.md/.env，315 skills，shell alias `research`
- **experiment**: 同上，shell alias `experiment`
- 每个 profile 完全隔离（config/skills/memory/env）
- `hermes profile use <name>` 切换默认 profile

### 4. Checkpoints 系统
- 路径: `~/.hermes/checkpoints/`
- 当前 0 B（尚未触发过快照）
- 配置: 最大 50 快照 / 500MB / 7 天保留
- 触发时机: 每次 `write_file` / `patch` / `terminal` 之前

### 5. Curator 状态
- 已启用，7 天间隔（周日触发）
- 仅 1 个 agent-created skill: `meme-creation`
- 最后运行: 1 天前（首次 seeding）
- 手动触发: `hermes curator run`
- 预览: `hermes curator run --dry-run`

## 批次升级通用流程

```text
1. 📋 制定计划 ← 定义 scope/约束/成功指标/回滚路径
2. 🔄 备份配置 ← hermes backup -q
3. ⚡ 逐项执行 ← 每个变更后立即验证
4. ✅ 全部验证 ← hermes tools list / grep config / hermes plugins list
5. 🧠 保存记忆 ← 记录变更内容到持久记忆
6. 📝 更新 skill + 参考文件 ← 反映新状态
```

## 后续待处理 (Batch 3+)

参见: `~/.hermes/hermes-upgrade-roadmap-v2.md`
