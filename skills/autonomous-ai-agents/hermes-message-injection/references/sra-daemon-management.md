# SRA Daemon Management

## Overview

SRA (Skill Runtime Advisor) 是一个独立的 HTTP 守护进程，运行在 127.0.0.1:8536，负责：
1. 扫描 ~/.hermes/skills/ 下的所有 skill
2. 对用户消息进行语义匹配 → 推荐最相关的 skill
3. 返回 `rag_context` + `should_auto_load` 标志

## Key Paths

| 路径 | 说明 |
|------|------|
| `/tmp/sra-agent/` | Editable pip 安装源码 |
| `/tmp/sra-agent/skill_advisor/runtime/daemon.py` | 守护进程主代码 (742 行) |
| `/tmp/sra-agent/skill_advisor/advisor.py` | SkillAdvisor 主类 |
| `~/.sra/config.json` | 用户配置 |
| `~/.sra/srad.pid` | PID 文件 |
| `~/.sra/srad.sock` | Unix Socket |
| `~/.sra/srad.log` | 日志文件 |
| `~/.sra/data/` | 场景记忆持久化目录 |
| `~/.local/bin/sra` | CLI 入口 |

## CLI Commands

```bash
sra start            # 后台启动（fork 守护进程）
sra stop             # 停止
sra restart          # 重启
sra status           # 查看状态（PID + 运行时统计）
sra attach           # 前台运行（调试用）
sra --refresh        # 强制刷新技能索引
sra --stats          # 查看统计（最常用技能、接受率等）
sra --coverage       # 技能识别覆盖率分析
sra --query "<text>" # 手动测试技能匹配
sra --enhanced-prompt # 生成增强版 skills 列表
sra install-service  # 生成 systemd service 文件
```

## API Endpoints

### GET /health

```json
{
  "status": "running",
  "version": "1.1.0",
  "uptime_seconds": 3600,
  "skills_count": 313,
  "total_requests": 42,
  "total_recommendations": 18,
  "errors": 0,
  "last_refresh": 0,
  "config": {
    "http_port": 8536,
    "auto_refresh_interval": 3600,
    "enable_http": true,
    "enable_unix_socket": true
  }
}
```

### POST /recommend

Request:
```json
{"message": "帮我写个python脚本"}
```

Response:
```json
{
  "rag_context": "...",
  "recommendations": [
    {"skill": "...", "confidence": "high", "score": 85.0, ...}
  ],
  "top_skill": "python-env-guide",
  "should_auto_load": false,
  "timing_ms": 12.5,
  "sra_available": true,
  "sra_version": "1.1.0"
}
```

## Client-side Integration (built-in v0.12.0+)

### run_agent.py

- **Module-level cache**: `_SRA_CACHE` dict (line 888)
- **Query function**: `_query_sra_context(user_message)` (line 891)
  - Calls `POST http://127.0.0.1:8536/recommend`
  - 2s timeout, silent failure
  - Returns formatted string like `"[SRA] Skill Runtime Advisor 推荐:\n..."` or `""`
- **Injection point**: `run_conversation()` (line 10802)
  - Before `# Add user message`
  - `user_message = f"{_sra_ctx}\n\n{user_message}"` if context exists

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SRA_PROXY_URL` | `http://127.0.0.1:8536` | SRA Daemon base URL |

## Troubleshooting

### Daemon won't start
```bash
sra attach     # 前台运行看错误日志
```

### Port 8536 already in use
```bash
lsof -i :8536  # 查看占用进程
kill -9 <PID>  # 杀掉
sra start      # 重新启动
```

### Skills index outdated
```bash
sra --refresh   # 强制重建索引
```

### Injection not working
```bash
# 验证 daemon 运行
curl http://127.0.0.1:8536/health

# 验证 recommend
curl -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# 检查注入代码是否存在
grep -n "_query_sra_context" ~/.hermes/hermes-agent/run_agent.py
```
