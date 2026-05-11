# SRA Daemon Management

## Overview

SRA (Skill Runtime Advisor) 是一个独立的 HTTP 守护进程，运行在 127.0.0.1:8536，负责：
1. 扫描 ~/.hermes/skills/ 下的所有 skill
2. 对用户消息进行语义匹配 → 推荐最相关的 skill
3. 返回 `rag_context` + `should_auto_load` 标志 + `contract` 契约

SRA v1.3.0 新增了**契约机制**（强制/可选技能建议）和**运行时力度体系**（4 级注入覆盖度）。

## Key Paths

| 路径 | 说明 |
|------|------|
| `~/projects/sra/` | SRA 项目根目录（包含 venv，当前部署路径） |
| `~/projects/sra/skill_advisor/runtime/daemon.py` | 守护进程主代码 |
| `~/projects/sra/skill_advisor/advisor.py` | SkillAdvisor 主类 |
| `~/projects/sra/skill_advisor/runtime/force.py` | 运行时力度管理引擎 🆕 v1.3.0 |
| `~/projects/sra/venv/bin/sra` | CLI 入口（支持子命令） |
| `~/projects/sra/venv/bin/srad` | 旧式启动命令（仅 start） |
| `~/.sra/` | SRA 数据目录 |
| `~/.sra/config.json` | 用户配置（含 `runtime_force.level` 🆕） |
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
ExecStart=$HOME/projects/sra/venv/bin/sra attach  # 前台运行，Type=simple 兼容（注意：systemd 不展开 $HOME，需替换为绝对路径如 /home/user/...）
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
Wants=srad.service      # 软依赖：有就用，没有就忽略（不会阻塞 Gateway 启动）
After=srad.service      # 如果 SRA 存在，保证先就绪
```

**关键决策：`Wants=` 而非 `Requires=`**

| 特性 | `Requires=` (❌ 危险) | `Wants=` (✅ 安全) |
|:---|:---|:---|
| 依赖不存在时 | ❌ Gateway 启动失败 (exit 5) | ✅ Gateway 正常启动 |
| SRA 崩溃时 | Gateway 不受影响 | Gateway 不受影响 |
| 对 Hermes 注入的影响 | 无（注入代码已降级） | 无（注入代码已降级） |
| SRA 可用时的行为 | Gateway 等待 SRA 就绪 | Gateway 等待 SRA 就绪 |

理由：
- Hermes 注入代码（`_query_sra_context()`）有 2s 超时 + try/except 全 catch → SRA 不可用时自动降级，消息照常处理
- `Requires=` 并未提供额外保护，反而引入「单元不存在就崩溃」的脆弱性
- `Wants=` 完美平衡：SRA 存在则依赖链生效，不存在则 Gateway 独立运行

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

SRA 的 CLI 通过 `sra` 命令提供完整子命令支持（当前版本 v1.3.0）：

```bash
# 所有命令必须用 SRA 项目 venv 中的版本
# 当前部署路径：~/projects/sra/venv/bin/sra <subcommand>
~/projects/sra/venv/bin/sra <subcommand>

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
compliance  查看技能遵循率统计
refresh     刷新索引
record      记录使用
force       运行时力度管理 🆕 v1.3.0
  sra force              查看当前力度等级
  sra force set <level>  切换等级 (basic/medium/advanced/omni)
  sra force list         列出所有等级详情
config      配置管理（支持嵌套 key，如 `runtime_force.level`）
install     安装 systemd 服务
adapters    列出 Agent 适配器
upgrade     升级到最新版本
uninstall   卸载 SRA（--all 清除配置和数据）
dep-check   检查 Gateway 依赖链健康度
version     显示版本
help        显示帮助
```

## API Endpoints

### GET /health

```json
{
  "status": "running",
  "version": "1.3.0",
  "uptime_seconds": 3600,
  "skills_count": 338,
  "total_requests": 42,
  "total_recommendations": 18,
  "errors": 0,
  "force_level": {                         # 🆕 v1.3.0
    "level": "medium",
    "label": "🦅 medium",
    "tier": 2,
    "active_points": ["on_user_message", "pre_tool_call"],
    "monitored_tools": ["write_file", "patch", "terminal", "execute_code"],
    "periodic": false
  },
  "last_refresh": 0,
  "config": {
    "http_port": 8536,
    "auto_refresh_interval": 3600,
    "enable_http": true,
    "enable_unix_socket": true
  }
}
```

### GET /status

```json
{
  "status": "ok",
  "sra_engine": true,
  "version": "1.3.0",
  "force_level": { ... },                  # 🆕 v1.3.0 力度状态
  "stats": { "skills_scanned": 338 },
  "config": { "host": "0.0.0.0", "port": 8536, ... }
}
```

### POST /recommend (v1.3.0)

Request:
```json
{"message": "帮我写个python脚本"}
```

Response (v1.3.0 含 contract 字段):
```json
{
  "rag_context": "...",
  "recommendations": [
    {"skill": "python-env-guide", "confidence": "high", "score": 85.0, ...}
  ],
  "contract": {                            # 🆕 v1.3.0 — 契约机制
    "task_type": "software-development",
    "required_skills": ["python-env-guide"],
    "optional_skills": ["systematic-debugging"],
    "confidence": "high",
    "summary": "任务类型「software-development」— 必须加载: python-env-guide"
  },
  "top_skill": "python-env-guide",
  "should_auto_load": true,
  "timing_ms": 12.5,
  "sra_available": true,
  "sra_version": "1.3.0"
}
```

**Contract 字段说明**（v1.3.0 新增）：

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `task_type` | string | 从推荐技能 category 推断的任务类型 |
| `required_skills` | string[] | 强推荐技能（score ≥ 80），Agent 应加载 |
| `optional_skills` | string[] | 可选技能（40 ≤ score < 80），建议参考 |
| `confidence` | string | 置信度 (`high`/`medium`/`low`) |
| `summary` | string | 人类可读的自然语言总结，已格式化到 rag_context |

### POST /force (🆕 v1.3.0)

力度等级管理端点。

```json
// 查询当前等级（不传 level）
POST /force {}

// 切换等级
POST /force {"level": "advanced"}
```

**可用等级**：

| 等级 | 标签 | 说明 | 注入点 |
|:----|:----|:-----|:-------|
| `basic` | 🐣 basic | 仅用户消息时注入 | `on_user_message` |
| `medium` | 🦅 medium | 消息 + 关键工具调用前检查 | `on_user_message`, `pre_tool_call` (write_file/patch/terminal/execute_code) |
| `advanced` | 🦖 advanced | 消息 + 全部工具钩子 + 后检 | `on_user_message`, `pre_tool_call` (全部), `post_tool_call` |
| `omni` | 🐉 omni | 全部 L3 + 周期性重注入 | 全部 + `periodic` (每 5 轮) |

**响应**：
```json
{
  "status": "ok",
  "current_level": {
    "level": "advanced",
    "label": "🦖 advanced",
    "tier": 3,
    "active_points": ["on_user_message", "post_tool_call", "pre_tool_call"],
    "monitored_tools": "__all__",
    "periodic": false
  },
  "available_levels": ["basic", "medium", "advanced", "omni"]
}
```

### POST /validate (v1.3.0 力度感知)

validate 端点现在感知力度等级（通过 daemon 自动注入 `_force_level` 和 `_monitored_tools`）：

| 力度等级 | 行为 |
|:--------|:-----|
| `basic` | ✅ 不拦截任何工具调用（`compliant: true`） |
| `medium` | ✅ 只拦截关键工具（write_file/patch/terminal/execute_code） |
| `advanced` | ✅ 拦截全部工具 |
| `omni` | ✅ 拦截全部工具 + 周期性重注入 |

所有级别均不阻断工具执行（`severity` 最大为 `warning`）。

## 运行时力度体系（🆕 v1.3.0）

力度不是阻断强度，而是注入覆盖度。力度越高，SRA 的注入点越多。

```
     用户消息    工具调用前    工具调用后    周期性注入
       ↓           ↓           ↓           ↓
L1 🐣  ●
L2 🦅  ●           ●
L3 🦖  ●           ●           ●
L4 🐉  ●           ●           ●           ●
```

配置方式：
```bash
# CLI 直接管理
sra force                    # 查看当前等级
sra force set advanced       # 切换为高级模式

# 通过配置系统
sra config set runtime_force.level omni

# 通过 HTTP API
curl -X POST http://127.0.0.1:8536/force \
  -H "Content-Type: application/json" \
  -d '{"level": "medium"}'
```

配置文件 `~/.sra/config.json`：
```json
{
  "runtime_force": {
    "level": "medium",
    "periodic_interval_rounds": 5
  }
}
```

## Client-side Integration (built-in v0.12.0+)

### run_agent.py

- **Module-level cache**: `_SRA_CACHE` dict
- **Query function**: `_query_sra_context(user_message)`
  - Calls `POST http://127.0.0.1:8536/recommend`
  - 2s timeout, silent failure
  - Returns formatted string like `"[SRA] Skill Runtime Advisor 推荐:\\n..."` or `""`
- **Injection point**: `run_conversation()` before `# Add user message`
  - `user_message = f"{_sra_ctx}\\n\\n{user_message}"` if context exists

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
~/projects/sra/venv/bin/sra stop
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
systemctl --user show hermes-gateway -p Wants -p After
# 应输出 Wants=... srad.service ... 和 After=... srad.service ...
```

### Installation fails: setuptools too old

```bash
# 错误：Could not find a version that satisfies the requirement setuptools>=61.0
# 解决方案 1：用 --no-build-isolation 跳过构建隔离（推荐）
~/projects/sra/venv/bin/python3 -m pip install --no-build-isolation -e ~/projects/sra

# 解决方案 2：升级 setuptools 后重试
pip install --upgrade setuptools wheel
pip install -e ~/projects/sra
```

### Verify SRA version and features

```bash
# 查看版本
~/projects/sra/venv/bin/python3 -c "import skill_advisor; print(skill_advisor.__version__)"

# 查看力度等级（运行中）
curl --noproxy '*' -s http://127.0.0.1:8536/status | python3 -m json.tool

# 查看 contrat （recommend 响应）
curl --noproxy '*' -s -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "写个脚本"}' | python3 -c "import sys,json; r=json.load(sys.stdin); print(json.dumps(r.get('contract',{}), indent=2))"
```

---

## 🚨 常见陷阱

### 陷阱 1：孤儿 drop-in 依赖（`sra-dep.conf` 残留）

**现象**：`systemctl --user start hermes-gateway` 失败，journal 显示 `Unit srad.service not found`。

**根因**：SRA 被迁移/卸载后，`~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf` 成为孤儿文件。若该文件含 `Requires=srad.service`，systemd 因找不到依赖 unit 而拒绝启动 Gateway（exit 5）。

**修复**：
```bash
rm ~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf
systemctl --user daemon-reload
systemctl --user start hermes-gateway
```

**预防**：
- 安装脚本使用 `Wants=` 而非 `Requires=`（软依赖 → 不影响 Gateway）
- SRA 卸载脚本自动清理 drop-in 文件（v1.2.1+）
- 即使不清理，`Wants=` 下 Gateway 也能正常启动

**诊断**：
```bash
systemctl --user show hermes-gateway -p Requires,Wants,After | grep srad
ls -la ~/.config/systemd/user/hermes-gateway.service.d/
systemctl --user cat srad 2>/dev/null || echo "srad.service not found"
```

### 陷阱 2：ExecStart 路径硬编码

SRA 从 `/tmp/sra-latest/` 迁移到其他路径（如 `~/projects/sra/`）后，`srad.service` 的 `ExecStart` 如果未同步更新，服务启动静默失败。建议用 symlink 或 `$SRA_HOME` 变量规避。

### 陷阱 3：`sra uninstall` 不清理 Gateway drop-in（已修复 ✅）

> **状态**：Story 17 (SRA-003-17) 已于 2026-05-11 实现，`sra uninstall` 现在会自动清理 `sra-dep.conf`。

**当前行为**：
```bash
sra uninstall --all
# ✅ 已删除: sra-dep.conf
# ✅ systemd daemon-reload 完成
```

**如果遇到旧版本残留，手动清理**：
```bash
rm -f ~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf
systemctl --user daemon-reload
```
