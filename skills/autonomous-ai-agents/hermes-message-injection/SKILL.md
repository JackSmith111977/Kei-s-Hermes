---
name: hermes-message-injection
description: "向 Hermes Agent 的消息管道注入外部服务上下文（如 SRA 技能推荐）。每次用户消息自动拦截 → 调外部服务 → 将结果作为 [前缀] 注入到消息前。涵盖 run_agent.py 的 run_conversation() 注入点、module-level 缓存、降级策略。"
version: 2.0.0
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
| `~/.hermes/hermes-agent/venv/bin/srad` | 守护进程启动命令（必须用 venv 版本） |
| `~/.hermes/hermes-agent/venv/bin/sra` | CLI 查询命令（必须用 venv 版本） |
| `/tmp/sra-latest/` | Editable pip 安装源码（从 GitHub 克隆） |
| `~/.sra/srad.sock` | Unix Socket |
| `~/.sra/srad.log` | 日志文件 |
| `~/.sra/config.json` | 用户配置 |

### ✅ 前置条件

**国内服务器**：GitHub 下载前必须先启动 mihomo 代理，否则 `git clone` 会超时。

### 安装

```bash
# 1. 确保代理已启动（国内服务器必需）
mihomo -f /etc/mihomo/config.yml -d /etc/mihomo

# 2. 设置代理环境变量后 git clone
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
cd /tmp
git clone https://github.com/JackSmith111977/Hermes-Skill-View.git sra-latest

# 3. 安装到 Hermes venv（⚠️ 必须用 --no-build-isolation，venv 中 setuptools 较旧）
~/.hermes/hermes-agent/venv/bin/python3 -m pip install --no-build-isolation -e /tmp/sra-latest
```

### 启动/停止

```bash
# ⚠️ 必须用 Hermes venv 中的命令（系统 Python 找不到 skill_advisor 模块）
~/.hermes/hermes-agent/venv/bin/srad     # 启动守护进程（后台）
~/.hermes/hermes-agent/venv/bin/sra stop # 停止
```

**说明**：新版 SRA（v1.2.0+）用 `srad` 命令启动守护进程，`sra` 命令仅用于停止和查询。

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
# sra --version 在新版中会当作查询字符串，需用 Python 检查
~/.hermes/hermes-agent/venv/bin/python3 -c "import skill_advisor; print(skill_advisor.__version__)"
```

## 与 Hook 系统的关系

| 机制 | 触发时机 | 是否阻塞 | 能否改消息 |
|------|---------|---------|-----------|
| `agent:start` Hook | LLM 处理前 | 异步非阻塞 | 不能 |
| `run_conversation()` 注入 | 消息入队列前 | 同步阻塞 | 能修改 |

两个机制**互补**：Hook 用于日志/监控等副作用，`run_conversation()` 注入用于实际修改消息内容。
