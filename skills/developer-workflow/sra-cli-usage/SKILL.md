---
name: sra-cli-usage
description: "SRA (Skill Runtime Advisor) 完整指南 — CLI 命令 + SRA Proxy 调用 + 四维评分引擎 + 排错。核心: 每次消息前调 SRA Proxy 获取技能上下文。"
version: 2.1.0
triggers:
- sra
- sra 推荐
- sra 查询
- sra 命令行
- sra proxy
- sra 没有推荐
- 忘记调用sra
- sra 未使用
- sra 集成
- skill runtime advisor
- 技能推荐
- 四维匹配
- sra force
- sra omni
- sra 力度
- sra 安装
- sra 卸载
- sra 重装
- sra 配置
- sra 日志级别
- sra 护进程
- sra 启动
- sra 停止
- sra 双重安装
author: boku
license: MIT
allowed-tools:
- terminal
metadata:
  hermes:
    tags:
    - sra
    - cli
    - security
    - best-practice
    - proxy
    - recommendation
    category: developer-workflow
    skill_type: tool-wrapper
    design_pattern: tool-wrapper
depends_on: []

---

# SRA 完整指南 v2.1

> **核心原则**：每次消息必须先调 `SRA Proxy` 获取上下文。`sra` CLI 是推荐的交互方式。
> **配套 skill**：`hermes-message-injection` 详细说明注入架构和 Hermes 集成。

---

## 一、SRA Proxy 铁律（每次消息必须执行）

**这是 SOUL.md 和 AGENTS.md 共同要求的强制性步骤。**

```bash
curl -s --noproxy '*' --max-time 10 -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "<主人消息>"}'
```

### 响应关键字段速查

| 字段 | 含义 | 你的操作 |
|:-----|:------|:---------|
| `should_auto_load` | 是否有得分≥80 的 skill | `true` → 自动 `skill_view()` 加载 |
| `top_skill` | 最高分 skill 名称 | 优先加载此 skill |
| `rag_context` | 格式化推荐文本 | 注入到思考过程 |
| `recommendations` | top-3 推荐列表 | 查看得分和原因 |
| `sra_available` | SRA 服务是否正常 | `false` → 跳过，用标准流程 |

### 输出示例解读

```json
{
  "recommendations": [
    {"skill": "pdf-layout", "score": 72.2, "confidence": "medium",
     "reasons": ["name匹配'pdf'", "trigger'reportlab'"], "category": "doc-design"}
  ],
  "should_auto_load": false,
  "contract": {"optional_skills": ["pdf-layout", "weasyprint"], "confidence": "medium"}
}
```

得分 72.2 → medium 级别 → 放入 `optional_skills` → 手动参考但不强制加载。

---

## 二、完整 CLI 命令参考

### 守护进程管理

```bash
sra start            # 启动后台守护进程（fork 模式）
sra stop             # 停止
sra restart          # 重启
sra status           # 查看状态
sra attach           # 前台运行（调试用）
```

### 技能推荐

```bash
sra recommend "生成PDF文档"              # 查询推荐（默认 top_k=3）
sra recommend "生成PDF文档" --top-k 5     # 返回更多结果
sra recommend "生成PDF文档" --json        # JSON 格式输出
```

### 索引管理

```bash
sra refresh          # 刷新技能索引
sra stats            # 查看运行统计
sra coverage         # 分析技能识别覆盖率
sra compliance       # 查看技能遵循率统计
```

### 运行时力度管理

```bash
sra force                 # 查看当前力度状态 + 所有可用等级
sra force set omni        # 切换到 omni（最高强度）
sra force list            # 列出所有等级详情

# 四级力度:
#   🐣 basic   仅用户消息
#   🦅 medium  消息 + 关键工具前
#   🦖 advanced 消息 + 全部工具前后
#   🐉 omni    全部 + 周期性重注入防漂移
```

### 配置管理

```bash
sra config show                  # 显示全部配置
sra config set <key> <value>     # 设置配置项
sra config set runtime_force.level omni  # 点号设置嵌套字段
sra config reset                 # 重置为默认值
sra config validate              # 校验配置（Schema）
```

### 高级操作

```bash
sra record <skill> <输入>           # 记录技能使用
sra adapters                         # 列出 Agent 适配器
sra install hermes                   # 安装到 Hermes
sra version                          # 版本信息 + 运行状态
sra upgrade                          # 从 GitHub 升级到最新
```

---

## 三、四维评分引擎详解（来自源码 matcher.py）

### 权重分配

```
最终分 = 词法x0.40 + 语义x0.25 + 场景x0.20 + 类别x0.15
```

### 子分值明细

| 匹配类型 | 分值 | 匹配条件 |
|:---------|:----:|:---------|
| name 精确 | 30 | w = skill_name 或 skill_name in w |
| name 部分 | 20 | len(w)>=3 且 w in skill_name |
| trigger 匹配 | 25 | w in triggers |
| tag 匹配 | 15 | w in tags |
| 描述匹配 | 8/词 | w in description（长度>=2） |
| match_text | 3 | w in match_text |
| 同义词精确 | 25 | 同义词 in name/trigger/tags |
| 同义词宽泛 | 12 | 同义词 in description |
| 语义描述 | 10 | w in full_description |
| 语义关键词 | 5 | w in body_keywords |
| 场景模式 | 3 x hit | 场景模式命中（x hit_count） |
| 使用频率 | 2 x uses | 历史使用次数 |
| 类别匹配 | 20 | w in category |
| tag 类别 | 15 | w/tag 互相包含 |

### SQS 质量惩罚（关键！）

```python
SQS >= 80: modifier = 1.0  (不降权)  # 目标
SQS >= 60: modifier = 0.9  (轻度)
SQS >= 40: modifier = 0.7  (中度)
SQS < 40: modifier = 0.4   (严重)
无评分: modifier = 0.5     (中性)
```

**例**：词法得 60 分，但 SQS=35 → 最终分 = 60x0.4 = 24 → 低于 weak 线(40) → 不推荐！

### 短查询提升

```python
if raw_word_count <= 2 and lex_score >= 20:
    total = total * 1.6  # 短查询自动提升 60%
```

---

## 四、为什么 skill 没有被推荐？排错流程

```text
1. 检查覆盖: sra coverage | grep <skill>
   → covered=true? 否 → 补充 triggers
2. 测试查询: sra recommend "<查询>" --json
   → score >= 40? 否 → 优化 description
3. 查看评分: sra stats
   → skills_scanned 正常?
4. 刷新索引: sra refresh
   → 新 triggers 生效
5. 检查 SQS: cat ~/.sra/data/sqs-scores.json
   → sqs_score 多少?
```

| 步骤 | 命令 | 判断标准 |
|:-----|:------|:---------|
| 1. 检查覆盖 | `sra coverage` | covered=true? |
| 2. 测试查询 | `sra recommend` | score >= 40？ |
| 3. 查看评分 | `sra stats` | skills_scanned 正常？ |
| 4. 刷新索引 | `sra refresh` | 新 triggers 生效 |
| 5. 检查 SQS | `cat ~/.sra/data/sqs-scores.json` | sqs_score 值 |

---

## 五、安装管理

> **核心要点**：SRA 需安装到 **Hermes 的 venv** 中（`~/.hermes/hermes-agent/venv/`），因为 `sra`/`srad` CLI 命令和 Hermes 的 `sra-guard` 插件都在这个 venv 中运行。

### 5.1 安装位置矩阵

| 安装位置 | Python 版本 | 是否可用 | 说明 |
|:---------|:-----------:|:--------:|:-----|
| Hermes venv (`~/.hermes/hermes-agent/venv/`) | 3.11 | ✅ **必须** | sra/srad CLI 在此，插件也在此运行 |
| 系统 Python (`/usr/bin/python3`) | 3.12 | ⚠️ 可选 | 外部托管环境，需 `--break-system-packages` |
| `~/.local/bin/` | 3.12 | ❌ 不要 | 与 Hermes venv 冲突 |

### 5.2 🚨 双重安装陷阱（最重要的坑）

**现象**：`sra status` 和 Hermes 插件都正常工作，但版本号始终是旧的 `0.0.0.dev0`，或者修改了源码重启后不生效。

**根因**：`pip install -e .` 可能同时安装在**两个位置**：
1. 系统 Python 的 `~/.local/lib/python3.12/site-packages/` (editable)
2. Hermes venv 的 `.../lib/python3.11/site-packages/` (editable)

当系统 Python 的安装优先被找到时，Hermes venv 的 `sra`/`srad` 命令会指向错误的包。

**诊断命令**：
```bash
# 检查系统 Python 是否有
python3 -c "import skill_advisor; print(skill_advisor.__file__)" 2>&1
# 检查 Hermes venv 是否有
~/.hermes/hermes-agent/venv/bin/python -c "import skill_advisor; print(skill_advisor.__file__)" 2>&1
```

**修复**：两个位置都要卸载，然后只安装到 Hermes venv。

### 5.3 全新安装流程

```bash
# 1. 停止旧版 SRA（如有）
sra stop 2>/dev/null

# 2. 从系统 Python 卸载（如有残留）
python3 -m pip uninstall sra-agent -y --break-system-packages 2>/dev/null

# 3. 从 Hermes venv 卸载
~/.hermes/hermes-agent/venv/bin/python -m pip uninstall sra-agent -y 2>/dev/null

# 4. 清理残留文件（pyc, egg-link, pth 等）
rm -rf ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/skill_advisor*
rm -rf ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/sra_agent*
rm -f ~/.hermes/hermes-agent/venv/bin/sra ~/.hermes/hermes-agent/venv/bin/srad

# 5. 安装到 Hermes venv（从本地仓库或 GitHub）
cd ~/projects/sra  # 本地已有仓库
~/.hermes/hermes-agent/venv/bin/python -m pip install .

# 或从 GitHub 安装
~/.hermes/hermes-agent/venv/bin/python -m pip install \
  "sra-agent @ git+https://github.com/JackSmith111977/Hermes-Skill-View.git"

# 6. 验证
~/.hermes/hermes-agent/venv/bin/python -c "
import skill_advisor
print(f'版本: {skill_advisor.__version__}')
print(f'路径: {skill_advisor.__file__}')
"
```

### 5.4 配置管理

所有配置存储在 `~/.sra/config.json` 中。常用配置项：

| 配置项 | 默认值 | 说明 |
|:-------|:------:|:-----|
| `log_level` | `"INFO"` | 日志级别（`"DEBUG"` 为最高级别） |
| `runtime_force.level` | `"medium"` | 力度等级（`"omni"` 为最高级别） |
| `http_port` | `8536` | HTTP API 端口 |
| `auto_refresh_interval` | `3600` | 技能索引自动刷新间隔（秒） |

#### 配置 DEBUG 日志（最高级别）
```json
{
  "log_level": "DEBUG",
  "runtime_force": {
    "level": "omni"
  }
}
```

#### 通过环境变量覆盖
```bash
# 所有 DEFAULT_CONFIG 中的字段都可以通过 SRA_<KEY> 环境变量覆盖
export SRA_LOG_LEVEL=DEBUG
export SRA_HTTP_PORT=8536
```

配置加载优先级：`环境变量 > 用户配置 > 默认值`。

### 5.5 验证安装完成

```bash
# 1. 启动
sra start

# 2. 检查健康状态
curl -s --noproxy '*' http://127.0.0.1:8536/health | python3 -m json.tool
# → force_level.level 应为 omni（如果设置了）
# → 日志中应有 [DEBUG] 消息

# 3. 测试推荐
curl -s --noproxy '*' -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# 4. 检查 Socket 通信
python3 -c "
import socket, json
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.settimeout(3)
sock.connect('/home/ubuntu/.sra/srad.sock')
sock.sendall(json.dumps({'action': 'ping', 'params': {}}).encode('utf-8'))
print(sock.recv(65536).decode('utf-8'))
sock.close()
"
```

---

## 六、常见问题

| 问题 | 排查 | 解决 |
|:-----|:------|:------|
| `sra: command not found` | CLI 在 venv 中 | `~/projects/sra/venv/bin/sra` 或加到 PATH |
| Daemon 未运行 | `sra status` | `systemctl --user restart srad` |
| 推荐为空 | 查询太短或没有匹配 | `sra refresh` + 详细查询 |
| 分数偏低 | SQS 惩罚或触发词不够 | 检查 `cat ~/.sra/data/sqs-scores.json` |
| curl 被安全拦截 | `--noproxy` 未加 | 始终用 `--noproxy '*'` |

## 七、诊断：SRA 零请求问题

> **实战发现 (2026-05-14)**: SRA 运行 11 小时 `total_requests=0`。Daemon 正常、索引正常、omni 力度已启用，但从未收到请求。

### 7.1 快速诊断

```bash
# 1. 检查服务状态
curl -s --noproxy '*' http://127.0.0.1:8536/health
# → 关注: total_requests, total_recommendations

# 2. 检查集成是否存在
grep -rn "sra\|8536\|recommend" ~/.hermes/config.yaml
grep -rn "_query_sra_context" ~/.hermes/hermes-agent/*.py

# 3. Hermes 内置集成可能不存在
# → _query_sra_context() 在文档但可能未在 run_agent.py 中实现
# → 当前唯一可靠的调用方式是手动 curl 或通过 pre_flight 集成
```

### 7.2 根因

| 层 | 问题 | 状态 |
|:---|:------|:----:|
| Hermes 核心 | `_query_sra_context()` 不存在于 run_agent.py | ❌ |
| config.yaml | 无 sra_proxy_url 配置 | ❌ |
| pre_flight | 未集成 SRA 调用 | ❌ |
| SOUL.md | 要求「每次消息调 curl」→ 拉模式不可靠 | ⚠️ |

### 7.3 阈值问题：单字延续关键词不满足 40 分门槛

即使手动调 SRA，单字延续关键词（如「继续」「phase」）也无法达到 THRESHOLD_WEAK=40：

```
trigger 匹配 +25
  × 词法权重 0.40 = 10
  × 短查询 boost 1.6 = 16
  总分 ≈ 16-25 < 40
  → ❌ 不推荐
```

**解决方案方向**:
1. 降低 THRESHOLD_WEAK 到 25 或 30
2. 为已知 phase 转换词加专用 boost（`if w in CONTINUATION_KEYWORDS: total *= 2.0`）
3. 通过 pre_flight 自动调 SRA（确保至少收到一些推荐）
## 八、设计原理

SRA CLI 遵循 **「自带安全」** 原则：
- CLI 不需要 pipe-to-interpreter，不会被安全扫描器标记
- 输出已格式化文本，无需额外解析
- `subprocess.run(["sra", "recommend", q])` 可编程调用

## 参考
