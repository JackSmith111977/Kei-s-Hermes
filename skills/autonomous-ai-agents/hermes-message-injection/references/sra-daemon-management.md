# SRA Daemon Management

## Overview

SRA (Skill Runtime Advisor) 是一个独立的 HTTP 守护进程，运行在 127.0.0.1:8536，负责：
1. 扫描 ~/.hermes/skills/ 下的所有 skill
2. 对用户消息进行语义匹配 → 推荐最相关的 skill
3. 返回 `rag_context` + `should_auto_load` 标志

## Key Paths

| 路径 | 说明 |
|------|------|
| `/tmp/sra-latest/` | Editable pip 安装源码（从 GitHub 克隆） |
| `/tmp/sra-latest/skill_advisor/runtime/daemon.py` | 守护进程主代码 |
| `/tmp/sra-latest/skill_advisor/advisor.py` | SkillAdvisor 主类 |
| `~/.sra/config.json` | 用户配置 |
| `~/.sra/srad.sock` | Unix Socket |
| `~/.sra/srad.log` | 日志文件 |
| `~/.sra/data/` | 场景记忆持久化目录 |
| `~/.hermes/hermes-agent/venv/bin/sra` | CLI 入口（⚠️ 必须用 venv 版本） |
| `~/.hermes/hermes-agent/venv/bin/srad` | 守护进程命令（⚠️ 必须用 venv 版本） |

## CLI Commands

```bash
# ⚠️ 所有 sra/srad 命令必须用 Hermes venv 版本，系统 Python 找不到 skill_advisor 模块

~/.hermes/hermes-agent/venv/bin/srad          # 启动守护进程（后台）
~/.hermes/hermes-agent/venv/bin/sra stop      # 停止
~/.hermes/hermes-agent/venv/bin/sra --query "<text>"  # 手动测试技能匹配
```

**说明**：新版 SRA（v1.2.0+）用 `srad` 命令启动守护进程，`sra start/restart/status/attach` 等旧版子命令已不再支持。

## 安装流程

```bash
# 1. 确保代理已启动（国内服务器必需）
mihomo -f /etc/mihomo/config.yml -d /etc/mihomo

# 2. 设置代理环境变量后 git clone
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
cd /tmp
git clone https://github.com/JackSmith111977/Hermes-Skill-View.git sra-latest

# 3. 安装到 Hermes venv
# ⚠️ 必须用 --no-build-isolation，因为 venv 中 pip 版本较旧（24.0），
#    腾讯云镜像没有 setuptools>=61.0
~/.hermes/hermes-agent/venv/bin/python3 -m pip install --no-build-isolation -e /tmp/sra-latest
```

## API Endpoints

### GET /health

```json
{
  "status": "running",
  "version": "1.2.0",
  "uptime_seconds": 3600,
  "skills_count": 315,
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
  "sra_version": "1.2.0"
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

## 查看版本

```bash
# sra --version 在新版中会当作查询字符串
~/.hermes/hermes-agent/venv/bin/python3 -c "import skill_advisor; print(skill_advisor.__version__)"
```

## Troubleshooting

### Daemon won't start

```bash
# 检查是否用了正确路径
~/.hermes/hermes-agent/venv/bin/srad

# 查看日志
cat ~/.sra/srad.log
```

### Port 8536 already in use

```bash
lsof -i :8536  # 查看占用进程
kill -9 <PID>  # 杀掉
~/.hermes/hermes-agent/venv/bin/srad  # 重新启动
```

### Skills index outdated

新版 SRA 自动检测技能目录变更并刷新索引，无需手动触发。

### Injection not working

```bash
# 验证 daemon 运行（⚠️ 用 --noproxy 绕过代理环境变量）
curl -s --noproxy '*' http://127.0.0.1:8536/health

# 验证 recommend
curl -s --noproxy '*' -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# 检查注入代码是否存在
grep -n "_query_sra_context" ~/.hermes/hermes-agent/run_agent.py
```

### 安装失败：setuptools 版本过旧

```bash
# 错误：Could not find a version that satisfies the requirement setuptools>=61.0
# 解决方案：用 --no-build-isolation 跳过构建隔离
~/.hermes/hermes-agent/venv/bin/python3 -m pip install --no-build-isolation -e /tmp/sra-latest
```
