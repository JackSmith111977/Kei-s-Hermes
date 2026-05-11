---
name: hermes-ops-tips
description: "Hermes 运维与工具流最佳实践。包含 Hermes 手动升级流程、SRA 迁移与独立工具管理、高清架构图生成 (SVG + cairosvg)、Memory 降级策略。"
triggers: [高清截图, cairosvg, sra迁移, sra管理, sra安装, 架构图, memory full, hermes运维, 升级hermes, hermes升级, sra升级, sra安装, sra重装, sra从源码安装, sra卸载, sra uninstall, sra upgrade, hermes doctor, hermes修复, statusline, 状态栏, 自定义功能恢复, gateway hook, 网关钩子, 升级后修复, browser vision, vision provider, 视觉模型, 截图卡住, 国内视觉api, openrouter vision, qwen vl]
---

# Hermes Ops & Workflow Tips

## 1. 高清架构图生成工作流
**问题**: `browser_vision` 截图会被压缩，导致文字模糊。
**解决方案**:
1.  使用 SVG 矢量图定义结构 (无限清晰)。
2.  使用 `cairosvg` (Python) 将 SVG 渲染为高分辨率 PNG。
    *   命令: `cairosvg input.svg -o output.png --output-width 3600`
    *   环境依赖: `sudo apt install libcairo2-dev` + `pip install cairosvg`.

## 2. SRA — 从 Hermes 集成 → 独立工具迁移记录

SRA 原本通过代码注入集成到 Hermes 核心循环（每次用户消息自动调 SRA Proxy → 注入 `[SRA]` 前缀）。2026-05-10 已完全剥离：

**剥离内容**：
- `run_agent.py`：删除 `_query_sra_context()` 函数（~60行）和 `run_conversation()` 中的注入点（4行）
- `agent/prompt_builder.py`：删除 `build_sra_context_prompt()` 函数（~60行）
- 删除所有 SRA 相关 skill 目录（`sra-agent/`, `skill-advisor/`, `hermes-message-injection/`）
- 删除 SRA 运行时数据（`~/.sra/`）和旧源码（`/tmp/sra-latest/`）
- 清理 Memory 中的 SRA 集成引用

**当前状态**：SRA 作为独立工具运行，不侵入 Hermes 核心代码。

**项目存放位置**（独立项目统一规范）：
- 所有独立项目源码统一放在 `~/projects/` 下
- SRA 源码：`~/projects/sra/`（从 GitHub 克隆）
- 其他独立项目（如有）同样放在 `~/projects/<project-name>/`

**当前安装**：
- 源码：`~/projects/sra/`（editable 安装）
- 版本：v1.2.1（端口 8536）
- 安装方式：`pip install --no-build-isolation -e .`
- 仓库：`https://github.com/JackSmith111977/Hermes-Skill-View.git`
- 运行时数据：`~/.sra/`（配置、日志、PID、socket）

## 3. Memory 溢出降级策略
当 Memory 达到上限 (约 2200 chars) 无法写入时：
1.  优先替换过时的长条目 (如旧的学习记录)。
2.  若无法替换，将学习成果/报告保存为本地 Markdown 文件 (`~/.hermes/docs/`)。
3.  在 Memory 中记录文件路径作为索引。

## 4. SRA Daemon 开发模式

SRA 项目源码在 `~/projects/sra/`，editable 安装到 Hermes venv。开发时修改源码后重启 srad 即可生效。

### 4.1 四层变更链
新功能从底到顶依次修改：`memory.py → advisor.py → daemon.py → cli.py`。详见 `references/sra-dev-patterns.md`。

### 4.2 关键陷阱
- **双 dispatch 点**：daemon.py 的 `do_POST()`（HTTP）和 `_handle_request()`（Socket）必须同步更新
- **相对导入**：`from ..endpoints.validate` 应该是 `from .endpoints.validate`（单点 vs 双点）
- **向后兼容**：memory.py 的 JSON 持久化必须用 `_ensure_skill_entry()` 模式处理旧数据

## 5. SRA Skill 推荐优化
**现象**: 通用动词 (如"学习") 在 SRA 中分数低。
**对策**: 优化 Skill 的 `description` 和 `triggers`。增加用户视角的自然语言描述 (如 "当你需要搞懂/学习...时使用")，避免纯内部视角的术语。

## 6. Hermes 手动升级流程（国内服务器）

### 场景
国内服务器上 `git fetch` 出现 TLS 错误，无法直接 `hermes update` 或 `git pull`。

### 前置准备
1. **启动代理**：确保 mihomo/Clash 代理已启动（`systemctl --user start mihomo`）
2. **检查版本**：`hermes --version`
3. **备份自定义修改**：
   ```bash
   cd ~/.hermes/hermes-agent
   git stash push -m "custom-backup-before-upgrade"
   # 或者用 patch 方式：
   git diff > ~/hermes_custom_backup/modified_files.patch
   # 如果是新增文件（不在 git 中）：
   mkdir -p ~/hermes_custom_backup/new_files_originals/
   cp gateway/statusline.py ~/hermes_custom_backup/new_files_originals/ 2>/dev/null
   ```

### 手动升级步骤
```bash
# 1. 下载目标版本的 GitHub Release tarball
wget https://github.com/nousresearch/hermes-agent/archive/refs/tags/v0.12.0.tar.gz \
  -O /tmp/hermes_latest.tar.gz

# 2. 解压
mkdir -p /tmp/hermes_new
cd /tmp/hermes_new
tar xzf /tmp/hermes_latest.tar.gz

# 3. rsync 替换（保留 .git, venv, __pycache__）
cd ~/.hermes/hermes-agent
rsync -av --exclude='.git' --exclude='venv' --exclude='__pycache__' \
  /tmp/hermes_new/hermes-agent-main/ ./

# 4. 重新安装依赖
source venv/bin/activate
pip install -e ".[all]" --break-system-packages

# 5. 验证版本
hermes --version
```

### 升级后需恢复的自定义修改

#### ⚠️ 关键判断标准：文件存在 ≠ 正确集成

升级后发现自定义文件还在但功能失效，通常是因为文件存在但**没有被新的代码导入/调用**（死代码）。必须验证实际集成链路，而不能只看文件存在性。

**排查方法 — 验证集成链路：**
```bash
# 1. 检查文件是否存在
ls -la gateway/statusline.py

# 2. 检查是否被其他文件 import（这才是关键！）
grep -rn "from gateway.statusline" gateway/run.py

# 3. 检查是否被调用
grep -n "statusline" gateway/run.py | grep -v "^.*\.py:" | head -10
#   如果只匹配到 statusline.py 自身的内容，说明是死代码
```

#### 各功能实际状态

| 功能 | 文件存在? | 代码集成? | 需要恢复? |
|------|:--------:|:--------:|:---------:|
| Pollinations 生图 (`tools/pollinations_image_tool.py`) | ✅ | ✅ | ❌ |
| Web 缓存 (`tools/web_cache.py`) | ✅ | ✅ | ❌ |
| GPT Image 2 (`tools/image_generation_tool.py`) | ✅ | ✅ | ❌ |
| 状态栏脚注 (`gateway/statusline.py`) | ✅ | ❌ 有文件但未被导入 | **✅ 需要恢复** |
| 微信 session 修复 | ❌ 需检查 | ❌ | **✅ 需要恢复** |

以下功能需要**手动恢复**：

1. 🐱 **飞书卡片 🐱小玛**：恢复 `_build_markdown_card_payload()`、`_build_text_card_payload()` 函数，修改 `_build_outbound_payload()` 返回 interactive card，添加发送/编辑的卡片失败降级逻辑

2. 📊 **状态栏脚注 (`gateway/statusline.py`)**：文件保留但集成丢失，需要以下两步恢复：
   ```python
   # 步骤 A: 在 gateway/run.py 顶部添加导入（与已有 gateway import 放在一起）
   from gateway.statusline import build_statusline

   # 步骤 B: 在 gateway/run.py 的响应构建区添加调用
   # 找到 "runtime_footer" 代码块和 "# Emit agent:end hook" 之间的位置
   # 添加:
   # Append statusline footer (model, context, git info)
   try:
       _platform_name = getattr(source.platform, "value", "") if source.platform else ""
       _statusline = build_statusline(agent_result=agent_result, platform=_platform_name)
       if _statusline and response:
           response += _statusline
   except Exception:
       logger.debug("Statusline generation failed (non-fatal)", exc_info=True)
   ```
   > 详细步骤见 `references/reintegrating-gateway-hooks.md`

### 升级后验证
```bash
# 1. 系统健康检查 + 自动修复
hermes doctor
hermes doctor --fix    # 自动修复：config 版本迁移 + WAL checkpoint

# 2. 语法检查
python3 -c "import py_compile; py_compile.compile('gateway/platforms/feishu.py', doraise=True)"
python3 -c "import py_compile; py_compile.compile('run_agent.py', doraise=True)"

# 3. 重启网关
systemctl --user restart hermes-gateway
journalctl --user -u hermes-gateway --since "1 min ago" --no-pager

# 4. 清理临时文件
rm -rf /tmp/hermes_latest.tar.gz /tmp/hermes_new/
```

### Git TLS 错误对策
如果不配置代理，直接下载 GitHub Release tarball 替代 `git clone/fetch`。备份目录统一放在 `~/hermes_custom_backup/`。

> 详细升级记录见 `references/hermes-upgrade-checklist.md`

## 8. SRA 升级与卸载

SRA v1.2.1+ 内置了自动化升级和卸载命令，推荐优先使用。手动流程仅保留作为备选/非标准环境下的降级方案。

### 8.1 推荐方式—内置命令 (v1.2.1+)

```bash
# ── 升级 ──
sra upgrade                    # 从 GitHub 拉取最新代码并重新安装
sra upgrade --version 1.2.0    # 升级到指定版本（checkout tag）

# ── 卸载 ──
sra uninstall                  # 卸载包 + 移除 systemd 服务（保留 ~/.sra/ 配置）
sra uninstall --all            # 完全卸载（含配置和索引数据）
```

**`sra upgrade` 的自动流程：**
1. ⏹️ 自动停止运行中的 Daemon
2. 📦 检查当前版本和安装模式（editable/标准）
3. 🌐 自动检测代理端口（7890/7891/1080/1087）
4. 🔄 已有 Git 仓库 → `git pull`；无则从 GitHub 克隆
5. 🏷️ 指定 `--version` 则 checkout 对应 tag
6. 🔧 `pip install --no-build-isolation -e .` 安装
7. ⚠️ `--no-build-isolation` 失败时自动降级为标准安装

**`sra uninstall` 的自动流程：**
1. ⏹️ 自动停止 Daemon
2. 🗑️ 移除 systemd 用户级服务（disable + 删文件 + daemon-reload）
3. 📦 `pip uninstall sra-agent -y`
4. 📁 `--all` 时删除 `~/.sra/`，否则提示保留
5. ⚠️ 系统级 systemd 服务（需 sudo）仅打印提示，不强行删除

### 8.2 备选—手动升级/全新安装流程（非标准环境降级方案）

**场景：** 内置 `sra upgrade` 不可用（网络受限、需要使用特定 venv、或环境特殊时）。

```bash
# 1. 停止旧版 SRA Daemon（如有）
~/.hermes/hermes-agent/venv/bin/sra stop

# 2. 从 Hermes venv 卸载旧版（如有）
~/.hermes/hermes-agent/venv/bin/python3 -m pip uninstall sra-agent -y

# 3. 从 GitHub 克隆最新源码（需要代理）
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
git clone https://github.com/JackSmith111977/Hermes-Skill-View.git ~/projects/sra

# 4. 安装到 Hermes venv
# ⚠️ 坑1: Hermes venv 的 pip 可能较旧，找不到 setuptools>=61.0（腾讯镜像无此版本）
#     → 使用 --no-build-isolation 跳过构建隔离，直接用 venv 已有的 setuptools
cd ~/projects/sra
~/.hermes/hermes-agent/venv/bin/python3 -m pip install --no-build-isolation -e .

# 5. 启动新版 SRA Daemon
~/.hermes/hermes-agent/venv/bin/sra start

# 6. 测试新版（注意代理干扰！）
# ⚠️ 坑2: 如果 http_proxy 环境变量设置了 127.0.0.1:7890，
#     curl 会尝试将 localhost 请求也走代理，导致 502 Bad Gateway
#     → 必须加 --noproxy '*' 绕过
curl -s --noproxy '*' -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### 常见坑

| 坑 | 现象 | 原因 | 解决 |
|:---|:-----|:-----|:-----|
| **pip 找不到 setuptools** | `Could not find a version that satisfies the requirement setuptools>=61.0` | Hermes venv pip 较旧 + 腾讯内网镜像无新版 setuptools | 加 `--no-build-isolation` |
| **curl 代理干扰** | curl 报 `502 Bad Gateway` 或请求去了 7890 端口 | `http_proxy` 环境变量导致 curl 代理所有流量，包括 localhost | 加 `--noproxy '*'` |
| **系统 sra 找不到模块** | `ModuleNotFoundError: No module named 'skill_advisor'` | `/usr/local/bin/sra` 用系统 Python，但包装在 Hermes venv 里 | 始终用 `~/.hermes/hermes-agent/venv/bin/srad` 启动 |
| **端口号不一致** | `sra start` 输出 8532 但 API 实际在 8536 | daemon.py 中 cmd_start 硬编码了 8532 | 修改 daemon.py 读取 `load_config()` |
| **版本号返回旧版** | API 返回的 `sra_version` 与 pyproject.toml 不一致 | 代码中版本常量可能有缓存或硬编码 | 检查 `skill_advisor/__init__.py` 和 daemon 版号 |

### 注意：使用 editable 安装后修改代码自动生效

`pip install -e .` 以 editable 模式安装，修改 `~/projects/sra/` 下的源码后重启 srad 即可生效，无需重新安装。

## 9. Statusline 运行状态诊断（集成后验证）

### 场景
statusline 代码已按第 6 节恢复（import 和调用点都存在），但飞书回复中未见 `───🤖 Model | 📊 ▰▰▰...` 脚注。如何定位问题？

### 诊断流程

#### Level 1：确认集成链路（快速检查）

```bash
cd ~/.hermes/hermes-agent

# 1. 文件存在？
ls -la gateway/statusline.py

# 2. import 存在？
grep "from gateway.statusline" gateway/run.py

# 3. 调用点存在？
grep -A5 "build_statusline(" gateway/run.py

# 4. Gateway 进程已重启并加载了新代码？
# 比较 statusline.py 修改时间和 gateway 启动时间
stat --format='%y' gateway/statusline.py
echo "---"
ps -o lstart,pid,cmd -p $(systemctl --user show hermes-gateway -p MainPID --value)
# 启动时间需 > statusline.py 修改时间才生效
```

#### Level 2：运行时输出验证（关键！）

集成链路确认后仍无输出时，很可能是 **`agent_result` 缺少预期字段** 导致 statusline 返回空串，而非功能关闭。

```bash
# 临时将 DEBUG 日志写入可见日志（或直接修改 statusline.py 临时加 print）
# 在 build_statusline() 开头添加临时调试：
#   import sys; print(f"[STATUSLINE-DEBUG] agent_result={agent_result}", file=sys.stderr)

# 或者更安全的方式：检查 agent_result 典型结构
grep -n "agent_result =" gateway/run.py | head -5
# 查看 agent_result 从哪里来，确认 keys
```

#### Level 3：常见静默失败根因

| 现象 | 可能原因 | 排查方向 |
|:----|:---------|:---------|
| statusline 不报错但无输出 | `agent_result` 为 `None` 或空字典 | 检查 `_run_agent()` 返回值 |
| 只有模型名没有 context bar | `last_prompt_tokens` / `input_tokens` 缺失 | provider 需要传递 token 计数 |
| 没有 git 信息 | gateway 以 systemd 运行，`os.getcwd()` 不在 git 仓库 | 检查 `_get_git_info()` 的 `cwd` |
| statusline 有时有有时无 | 流式响应 (`already_sent=True`) 时被跳过 | 检查流式模式下的直接发送逻辑 |

#### Level 4：终极诊断 — 制造一个确定触发的测试

```bash
cd ~/.hermes/hermes-agent

# 直接测试 build_statusline 的 Python 行为
python3 -c "
import sys
sys.path.insert(0, '.')
from gateway.statusline import build_statusline

# 测试1：带完整 agent_result
result = {
    'model': 'deepseek/deepseek-v4',
    'last_prompt_tokens': 45000,
    'input_tokens': 42000,
    'output_tokens': 3000,
}
line = build_statusline(agent_result=result, platform='feishu')
print(f'Test 1 (full data): {repr(line)}')

# 测试2：空 agent_result
line = build_statusline(agent_result={}, platform='feishu')
print(f'Test 2 (empty dict): {repr(line)}')

# 测试3：None agent_result
line = build_statusline(agent_result=None, platform='feishu')
print(f'Test 3 (None): {repr(line)}')
"

# 预期：Test 1 应有内容，Test 2/3 返回空串
```

### 快速恢复命令

如果诊断为 `agent_result` 数据问题：

```bash
cd ~/.hermes/hermes-agent
# 检查 _run_agent() 返回结构
grep -B5 -A20 "agent_result = await" gateway/run.py | head -40
```

如果诊断为其他运行时问题，重启 gateway：
```bash
systemctl --user restart hermes-gateway
journalctl --user -u hermes-gateway --since "10 sec ago" --no-pager | grep -i "statusline"
```

> 详细诊断要点见 `references/statusline-runtime-diagnostics.md`

## 10. Vision Provider 配置与故障排查（国内服务器）

### 场景
国内服务器需要 `browser_vision` （截图分析）正常工作。默认 Gemini 从国内无法直接访问。

### 各 Provider 实测状态（2026-05 月）

| Provider | 模型 | 国内直连 | 费用 | 状态 |
|:---------|:-----|:--------:|:----|:----|
| **OpenRouter** | `qwen/qwen3-vl-32b-instruct` | ✅ 成功 | ~$0.00003/次 | **✅ 推荐使用** |
| Google Gemini | `gemini-3-flash-preview` | ❌ "User location not supported" | 免费层 15RPM | ❌ 区域封锁 |
| Aliyun DashScope | `qwen3-vl-plus` | ✅ 可达但 key 过期 | 新用户 100万 tokens 免费 | ⚠️ 需更新 API Key |
| DeepSeek V4 | `deepseek-v4-flash` | ✅ 可达 | $0.14/百万tokens | ❌ 不支持 image_url |
| OpenRouter 其他 | `qwen/qwen2.5-vl-72b-instruct` | ✅ 成功 | $0.00025/次 | ✅ 可选 |
| LongCat | `LongCat-2.0-Preview` | ✅ 可达 | 已有额度 | ❌ 文本模型，不支持 vision |

### 推荐配置 — OpenRouter + Qwen3-VL

```yaml
# ~/.hermes/config.yaml
auxiliary:
  vision:
    api_key: ''                  # OpenRouter 自动从 OPENROUTER_API_KEY 读取
    base_url: ''
    model: qwen/qwen3-vl-32b-instruct   # 32B 模型，平衡质量与速度
    provider: openrouter
    timeout: 60
```

**前提**：`.env` 中必须有 `OPENROUTER_API_KEY=sk-or-...`。

### 故障排查流程

当 `browser_vision` 卡住或失败时：

```
浏览器截图卡住？
├─ 检查 agent.log 是否有 "Auxiliary vision: using ..." 日志
│   └─ 有 → 截图已完成，vision API 调用阶段卡住
│   └─ 无 → 截图阶段卡住（检查 agent-browser CLI 是否安装）
├─ vision API 调用卡住？
│   ├─ timeout 设了多少？→ 默认 120s，建议 60s
│   └─ GeminiNativeClient 默认 read timeout 是 600s！→ 改为 120s 或更低
│       └─ 文件: `agent/gemini_native_adapter.py:834`
├─ API 返回错误？
│   ├─ 403 / "User location not supported" → Gemini 封锁，换 OpenRouter
│   ├─ 400 / "unknown variant `image_url`" → 模型不支持 vision，换 VL 模型
│   └─ 401 / "Incorrect API key" → API Key 过期或无效
└─ 最终降级方案
    └─ 即使 vision 失败，截图文件已保存到 cache/screenshots/，可用 MEDIA:<path> 发送
```

### 实测可用模型（从国内直连验证通过）

```bash
# 测试命令（替换 YOUR_KEY）
curl -s --noproxy '*' --max-time 30 -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{
    "model": "qwen/qwen3-vl-32b-instruct",
    "messages": [{"role":"user","content":[{"type":"text","text":"Describe this image"},
      {"type":"image_url","image_url":{"url":"data:image/png;base64,<base64>"}}]}],
    "max_tokens": 100
  }'
```

注意：测试时务必加 `--noproxy '*'`，否则若设了 http_proxy，curl 会把 localhost 请求也走代理。

### 超时配置要点

- `config.yaml` → `auxiliary.vision.timeout`：单次 API 调用超时（建议 **60s**）
- `gemini_native_adapter.py:834` → `httpx.Timeout(read=120.0)`：底层 HTTP 读取超时（默认 600s，**必须改**）
- 两者都要改才能根治卡死问题。只改 config 可能被底层 httpx 默认 read timeout 覆盖。

## 7. 日常系统升级与配置优化流程

### 场景
需要对 Hermes 系统进行配置迁移、依赖安装、工具开启等日常升级操作时。

### 推荐流程与顺序

```bash
# Step 1: 配置版本迁移（解锁新功能）
hermes config migrate

# Step 2: 自动修复（WAL checkpoint + 其他）
hermes doctor --fix

# Step 3: 初始化 Skills Hub（社区技能库）
hermes skills list
hermes skills browse     # 浏览社区 skill
```

### API Key 别名技巧

当自定义 provider 用了 `CUSTOM_XXX_API_KEY` 但标准工具需要 `XXX_API_KEY` 时：

```bash
# 1. 从环境变量获取现有 key（避免暴露明文）
python3 -c "
import os
key = os.environ['CUSTOM_OPENROUTER_API_KEY']
print(key)
" > /tmp/key.txt

# 2. 添加到 .env
echo "OPENROUTER_API_KEY=$(cat /tmp/key.txt)" >> ~/.hermes/.env
rm /tmp/key.txt

# 或者直接用 Python 操作 .env 文件（更安全）
```

这会解锁标准工具对 provider 的识别（如 MOA 需要 `OPENROUTER_API_KEY`）。

### 语音能力配置

```bash
# 1. 安装 faster-whisper（本地语音转文字，免费）
# 注意：如果系统 Python 有 externally-managed-environment 限制，
# 使用 venv 的 pip 安装（Hermes 的 venv 在 ~/.hermes/hermes-agent/venv/）
python3 -m ensurepip --upgrade       # 如果 venv 没有 pip
python3 -m pip install faster-whisper

# 2. 配置 STT（语音→文字）
# 编辑 config.yaml:
# stt:
#   enabled: true
#   provider: local
#   local:
#     model: base

# 3. 配置 TTS（文字→语音，Edge 免费）
# tts:
#   provider: edge
```

### 文件快照回滚（Checkpoints）

```yaml
# config.yaml 配置：
checkpoints:
  enabled: true
  max_snapshots: 50
```
启用后可在会话中使用 `/rollback [N]` 回滚文件变更。

### 安装 Docker 沙箱

```bash
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER    # 加入 docker 组（需重新登录生效）
# 验证：sudo docker ps
```

### externally-managed-environment 错误处理

当 `pip install` 报 `externally-managed-environment` 时：

| 方法 | 命令 | 适用场景 |
|:----|:----|:---------|
| 使用 venv 的 pip | `python3 -m pip install <pkg>`（当前活跃的 venv）| Hermes venv 包 |
| 确保 pip 在 venv 中 | `python3 -m ensurepip --upgrade` | venv 缺少 pip |
| 系统 Python 安装 | `sudo apt install python3-<pkg>` | 系统级包 |
| 强制安装（不推荐） | `pip install <pkg> --break-system-packages` | 临时方案 |

### 子模块状态检查

```bash
cd ~/.hermes/hermes-agent
git submodule status        # 查看子模块状态
cat .gitmodules             # 查看定义了的子模块
git ls-tree HEAD <name>     # 确认子模块是否在当前 commit 树中
```

如果子模块定义在 `.gitmodules` 但不在当前 commit 树中，说明是残留配置，无需处理。