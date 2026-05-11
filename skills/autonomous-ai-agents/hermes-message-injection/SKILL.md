---
name: hermes-message-injection
description: "向 Hermes Agent 的消息管道注入外部服务上下文（如 SRA 技能推荐）。每次用户消息自动拦截 → 调外部服务 → 将结果作为 [前缀] 注入到消息前。涵盖 run_agent.py 的 run_conversation() 注入点、module-level 缓存、降级策略。"
version: 2.2.0
triggers:
  - hermes 注入
  - hermes 消息拦截
  - message injection
  - sra integration
  - context injection
  - hermes hook
  - run_conversation
  - sra daemon
  - sra start
  - 启动sra
  - 开启sra
  - 下载sra
  - 安装sra
  - 更新sra
  - sra管理
  - 上下文注入
depends_on:
  - hermes-agent
design_pattern: Pipeline Injection
skill_type: Pattern
---

# Hermes Message Injection — 消息管道上下文注入模式

## 问题

需要让每个用户消息在进入 LLM 前自动调外部服务（如 SRA 技能推荐、安全检查、内容过滤等），把结果注入到系统提示或消息中。

## 不可行的方案（已试错）

### 方案 A: AGENTS.md / SOUL.md 文档规则
- 文件中的规则是"劝告式"的，Agent 可能忽略
- 上下文压缩会裁剪掉规则
- 不同模型遵守程度不同
- **结论：不可靠**

### 方案 B: Gateway Hook 系统 (`agent:start` 事件)
- Hermes 自带的 Hook 系统 (`gateway/hooks.py`) 支持注册事件处理器
- Hook 是**异步非阻塞**的——错误被 catch 但不会阻塞消息
- Hook handler **不能修改消息内容或 system prompt**
- **结论：只能触发副作用（写日志/写文件），不能注入上下文**

### 方案 C: 改 `_build_system_prompt()` 或 `prompt_builder.py`
- `_build_system_prompt()` 在整个 session 中**只调用一次**并缓存
- 后续 `run_conversation()` 调用复用缓存的 system prompt
- 后续消息不会触发外部服务查询
- **结论：只对第一轮消息有效**

## ✅ 内置方案（Hermes v0.12.0+）

**从 v0.12.0 开始，SRA 注入代码已经内置到 `run_agent.py` 中，无需手动修改。**

### 注入点

- **Module-level 函数**: `_query_sra_context()` — 第 891 行 (`run_agent.py`)
  - 查询 `SRA_PROXY_URL`（默认 `http://127.0.0.1:8536`）的 `/recommend` 端点
  - 返回 `[SRA] Skill Runtime Advisor 推荐:` 格式的上下文字符串
  - 内置 MD5 hash 缓存（避免重复 HTTP 调用）
  - 2 秒超时 + try/except 全catch → 服务不可用时自动降级
- **注入时机**: `run_conversation()` 中 `# Add user message` 前（第 10802 行）
  - 前缀注入到 user_message：`f"{_sra_ctx}\n\n{user_message}"`
  - 覆盖 CLI + Gateway 所有入口

### 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **注入点** | `run_conversation()` 中 `# Add user message` 前 | 每轮消息触发，覆盖 CLI + Gateway |
| **注入方式** | 前缀注入到 user_message，不修改 system prompt | 不破坏 prompt caching |
| **缓存** | module-level dict，MD5 hash 做 key | 避免 retry 时重复 HTTP 调用 |
| **超时** | 2 秒 | 快速失败，不阻塞消息 |
| **降级** | try/except 全 catch，返回空字符串 | 服务不可用时不影响正常对话 |

### 搜索助手

```bash
# 找到注入点
grep -n "_query_sra_context\|SRA Context" ~/.hermes/hermes-agent/run_agent.py

# 验证函数定义
grep -n "def _query_sra_context" ~/.hermes/hermes-agent/run_agent.py
```

## 🚀 SRA Daemon 管理

SRA 注入代码依赖外部的 SRA Daemon 服务。需要单独启动。

### 📌 关键路径

| 路径 | 说明 |
|------|------|
| `~/projects/sra/venv/bin/sra` | CLI 命令（支持子命令: start/stop/attach/status/recommend 等） |
| `~/projects/sra/venv/bin/srad` | 旧版启动命令（仅调用 cmd_start，建议用 sra 替代） |
| `~/projects/sra/skill_advisor/` | SRA 源码目录 |
| `~/.sra/srad.sock` | Unix Socket |
| `~/.sra/srad.log` | 日志文件 |
| `~/.sra/config.json` | 用户配置 |
| `~/.config/systemd/user/srad.service` | 用户级 systemd 服务单元（推荐方式） |
| `~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf` | Gateway 依赖配置 |

### ✅ 前置条件

**国内服务器**：GitHub 下载前必须先启动 mihomo 代理，否则 `git clone` 会超时。

### 安装

```bash
# 1. 确保代理已启动（国内服务器必需）
mihomo -f /etc/mihomo/config.yml -d /etc/mihomo

# 2. 设置代理环境变量后 git clone（国内服务器必需）
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
git clone --depth 1 https://github.com/JackSmith111977/Hermes-Skill-View.git ~/projects/sra

# 3. 创建 venv 并安装（⚠️ 必须用 --no-build-isolation，venv 中 setuptools 较旧）
cd ~/projects/sra
python3 -m venv venv
source venv/bin/activate
pip install --no-build-isolation -e .

# 4. 或者直接升级已有的 venv（如果已安装）
~/projects/sra/venv/bin/python3 -m pip install --no-build-isolation -e ~/projects/sra
```

### 🏆 推荐：systemd 用户级服务自启动

这是生产环境推荐的方式，SRA Daemon 会随系统启动自动运行，崩溃后自动恢复。

#### 服务单元

**`~/.config/systemd/user/srad.service`**：
```ini
[Unit]
Description=SRA — Skill Runtime Advisor Daemon
After=network.target

[Service]
Type=simple
ExecStart=$HOME/projects/sra/venv/bin/sra attach  # 前台运行模式，$HOME 需替换为实际路径
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=srad

[Install]
WantedBy=default.target
```

#### Gateway 依赖链

**`~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf`**：
```ini
[Unit]
Wants=srad.service
After=srad.service
```

作用：确保 Gateway 启动时 SRA 已就绪，且 SRA 故障不会影响 Gateway。
- Hermes 的 `_query_sra_context()` 已有 2s 超时 + try/except 全 catch 降级机制，SRA 不可用时自动跳过消息注入，不阻塞 Gateway

> ⚠️ **孤儿依赖陷阱**：SRA 迁移/卸载后，`sra-dep.conf` 成为孤儿文件。它仍然声明 `Wants=srad.service`，但因为 `Wants=` 是软依赖，Gateway 仍可正常启动（唯 SRA 注入不可用）。但如果误用了 `Requires=`，则 Gateway 崩溃。**SRA 卸载流程必须同步清理此 drop-in 文件**。

#### 启用并启动

```bash
systemctl --user daemon-reload          # 加载新服务
systemctl --user enable srad.service    # 开机自启
systemctl --user start srad.service     # 立即启动
systemctl --user status srad.service    # 验证状态

# Gateway 只需重启一次让依赖生效
systemctl --user restart hermes-gateway
```

#### 管理命令

```bash
systemctl --user status srad              # 查看状态
systemctl --user restart srad             # 重启 SRA
systemctl --user stop srad                # 停止 SRA
journalctl --user -u srad -n 50           # 查看日志
journalctl --user -u srad -f              # 跟踪日志
```

### 手动启动/停止（开发调试用）

```bash
# ⚠️ 必须用 SRA venv 中的命令（系统 Python 找不到 skill_advisor 模块）

# sra 命令支持子命令：
$HOME/projects/sra/venv/bin/sra attach    # 前台运行（Type=simple 模式，Ctrl+C 停止）
$HOME/projects/sra/venv/bin/sra start     # 后台守护进程（fork 模式）
$HOME/projects/sra/venv/bin/sra stop      # 停止
$HOME/projects/sra/venv/bin/sra status    # 查看状态
$HOME/projects/sra/venv/bin/sra restart   # 重启
$HOME/projects/sra/venv/bin/sra recommend <查询>  # 手动测试推荐

# srad = cmd_start() 的快捷方式（仅启动，无子命令）
$HOME/projects/sra/venv/bin/srad
```

### 验证

```bash
# ❌ 不要直接 curl（当前 shell 可能设了 http_proxy，会走代理导致失败）
# ✅ 用 --noproxy 绕过：
curl -s --noproxy '*' http://127.0.0.1:8536/health

# 技能推荐测试
curl -s --noproxy '*' -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我写个python脚本"}'
```

### 默认端口

HTTP API: `8536`（通过 `~/.sra/config.json` 的 `http_port` 配置）

### 查看版本

```bash
$HOME/projects/sra/venv/bin/python3 -c "import skill_advisor; print(skill_advisor.__version__)"
```

## 与 Hook 系统的关系

| 机制 | 触发时机 | 是否阻塞 | 能否改消息 |
|------|---------|---------|-----------|
| `agent:start` Hook | LLM 处理前 | 异步非阻塞 | 不能 |
| `run_conversation()` 注入 | 消息入队列前 | 同步阻塞 | 能修改 |

两个机制**互补**：Hook 用于日志/监控等副作用，`run_conversation()` 注入用于实际修改消息内容。
