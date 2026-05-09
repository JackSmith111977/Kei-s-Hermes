# SRA Daemon Management

## Overview

SRA (Skill Runtime Advisor) 是一个独立的 HTTP 守护进程，运行在 127.0.0.1:8536，负责：
1. 扫描 ~/.hermes/skills/ 下的所有 skill
2. 对用户消息进行语义匹配 → 推荐最相关的 skill
3. 返回 `rag_context` + `should_auto_load` 标志

## Key Paths

| 路径 | 说明 |
|------|------|
| `/tmp/sra-latest/` | SRA 项目根目录（包含 venv） |
| `/tmp/sra-latest/skill_advisor/runtime/daemon.py` | 守护进程主代码 |
| `/tmp/sra-latest/skill_advisor/advisor.py` | SkillAdvisor 主类 |
| `/tmp/sra-latest/venv/bin/sra` | CLI 入口（支持子命令） |
| `/tmp/sra-latest/venv/bin/srad` | 旧式启动命令（仅 start） |
| `~/.sra/` | SRA 数据目录 |
| `~/.sra/config.json` | 用户配置 |
| `~/.sra/srad.sock` | Unix Socket |
| `~/.sra/srad.log` | 日志文件 |
| `~/.sra/srad.pid` | PID 文件（fork 模式用） |
| `~/.sra/data/` | 场景记忆持久化目录 |
| `~/.config/systemd/user/srad.service` | **(推荐)** systemd 用户级服务单元 |
| `~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf` | Gateway 依赖配置 |

## 🏆 生产推荐：systemd 用户级服务

### 服务单元

**`~/.config/systemd/user/srad.service`**：
```ini
[Unit]
Description=SRA — Skill Runtime Advisor Daemon
After=network.target

[Service]
Type=simple
ExecStart=/tmp/sra-latest/venv/bin/sra attach  # 前台运行，Type=simple 兼容
Restart=on-failure    # 崩溃自动重启
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=srad

[Install]
WantedBy=default.target  # 用户登录自启
```

**关键设计**：
- `Type=simple` + `sra attach`：前台运行，systemd 直接管理进程生命周期
- `Restart=on-failure`：SRA 崩溃（如端口冲突、OOM）时自动恢复
- `WantedBy=default.target`：用户登录时自动启动

### Gateway 依赖链

**`~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf`**：
```ini
[Unit]
Requires=srad.service   # Gateway 要求 SRA 必须启动
After=srad.service      # SRA 先就绪，Gateway 后启动
```

作用：
- **Requires**：确保 Gateway 激活时 SRA 也被激活。停止 Gateway 不影响 SRA。
- **After**：保证 SRA 在 Gateway 之前完全就绪，首次消息即有技能推荐。
- 注：`BindsTo=` 更严格（SRA 停止则 Gateway 也停），此处不适用。

### 启用与启动

```bash
# 首次安装
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
# 创建上述两个文件...

# 加载并启动
systemctl --user daemon-reload
systemctl --user enable srad.service     # 开机自启
systemctl --user start srad.service      # 立即启动

# 验证
systemctl --user status srad.service     # 应显示 active (running)
curl --noproxy '*' http://127.0.0.1:8536/health

# Gateway 重启让依赖生效（⚠️ 需主人手动执行）
systemctl --user restart hermes-gateway
```

### 日常管理

```bash
systemctl --user status srad              # 查看状态
systemctl --user restart srad             # 重启 SRA
systemctl --user stop srad                # 停止 SRA
journalctl --user -u srad -n 50           # 查看最近日志
journalctl --user -u srad -f              # 跟踪日志输出
```

## CLI 命令

SRA 的 CLI 通过 `sra` 命令提供完整子命令支持：

```bash
# 所有命令必须用 SRA 项目 venv 中的版本
/tmp/sra-latest/venv/bin/sra <subcommand>

# 子命令列表
attach      前台运行（调试用，Ctrl+C 停止）
start       后台守护进程（fork 模式）
stop        停止守护进程
status      查看运行状态
restart     重启
recommend   推荐匹配（一次查询）
query       同 recommend
stats       查看统计
coverage    查看技能覆盖率
refresh     刷新索引
record      记录使用
config      配置管理
install     安装 systemd 服务
adapters    列出 Agent 适配器
version     显示版本
help        帮助信息
```

### CLI 与 srad 的关系

| 命令 | 说明 | 等价于 |
|:----|:-----|:-------|
| `sra attach` | 前台运行（Type=simple 模式） | 直接运行 `SRaDDaemon().attach()` |
| `sra start` | 后台守护进程（fork 模式） | 同 `srad` |
| `srad` | 仅 `cmd_start()` 快捷方式 | `sra start` |

## API Endpoints

### GET /health

```json
{
  "status": "running",
  "version": "1.2.0",
  "uptime_seconds": 3600,
  "skills_count": 338,
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

- **Module-level cache**: `_SRA_CACHE` dict
- **Query function**: `_query_sra_context(user_message)`
  - Calls `POST http://127.0.0.1:8536/recommend`
  - 2s timeout, silent failure
  - Returns formatted string like `"[SRA] Skill Runtime Advisor 推荐:\n..."` or `""`
- **Injection point**: `run_conversation()` before `# Add user message`
  - `user_message = f"{_sra_ctx}\n\n{user_message}"` if context exists

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SRA_PROXY_URL` | `http://127.0.0.1:8536` | SRA Daemon base URL |

## Troubleshooting

### SRA won't start under systemd

```bash
# 检查 journal 日志
journalctl --user -u srad -n 50 --no-pager

# 常见原因：端口被占用
ss -tlnp | grep 8536
kill -9 <PID>
systemctl --user restart srad
```

### Port 8536 already in use

```bash
ss -tlnp | grep 8536  # 查看占用进程
# 如果是旧 SRA 进程
/tmp/sra-latest/venv/bin/sra stop
# 或强制杀掉
kill -9 <PID>
systemctl --user restart srad
```

### curl 测试时超时

```bash
# ⚠️ 如果设了 http_proxy 环境变量，curl 会将 localhost 请求也走代理
# ✅ 必须用 --noproxy '*' 绕过
curl --noproxy '*' -s --connect-timeout 3 http://127.0.0.1:8536/health
```

### Skills index outdated

SRA 自动检测技能目录变更并刷新索引（每 30 秒校验和检测 + 每小时定时刷新），无需手动触发。

### Injection not working

```bash
# 1. 验证 daemon 运行
curl --noproxy '*' http://127.0.0.1:8536/health

# 2. 验证 recommend API
curl --noproxy '*' -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# 3. 检查注入代码是否存在
grep -n "_query_sra_context" ~/.hermes/hermes-agent/run_agent.py

# 4. 检查 SRA 是否在 Gateway 的依赖链中
systemctl --user show hermes-gateway -p Requires -p After
# 应输出 Requires=... srad.service ... 和 After=... srad.service ...
```

### Installation fails: setuptools too old

```bash
# 错误：Could not find a version that satisfies the requirement setuptools>=61.0
# 解决方案：用 --no-build-isolation 跳过构建隔离
/tmp/sra-latest/venv/bin/python3 -m pip install --no-build-isolation -e /tmp/sra-latest
```
