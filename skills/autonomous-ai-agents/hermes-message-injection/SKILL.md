---
name: hermes-message-injection
description: "SRA Proxy 调用规程与自动注入架构。涵盖手动调用铁律、四维评分、omni 力度体系、EPIC-004 插件方案进展，以及 2026-05-15 深度审计发现的根因分析（幻影集成根本原因）。"
version: 2.7.0
triggers:
  - hermes 注入
  - hermes 消息拦截
  - message injection
  - sra integration
  - sra proxy
  - sra 推荐
  - sra 命令行
  - sra 没有推荐
  - sra 未使用
  - 忘记调用sra
  - sra 推荐系统
  - skill runtime advisor
  - 技能推荐
  - context injection
  - hermes hook
  - run_conversation
  - sra daemon
  - sra start
  - sra recommend
  - sra开启了吗
  - sra没开
  - sra状态
  - sra健康
  - sra跳过
  - 忘记调sra
  - sra 纠正
  - sra 教训
  - sra proxy 调用
  - sra 第一条规则
  - 消息注入
  - 上下文注入
  - hermes-message-injection
  - 自动注入
  - 没有自动注入
  - 不主动调sra
  - 自动调用
  - auto-inject
  - 为什么没有自动注入
  - 自动注入为什么没工作
  - 根因分析
  - sra 从未工作
  - 幻影集成
  - 补丁未执行
  - ac 审计盲点
  - 文档漂移
depends_on:
  - hermes-agent
  - sra-cli-usage
  - knowledge-routing
design_pattern: Pipeline Injection
skill_type: Pattern
---

# Hermes Message Injection — SRA 消息注入模式 v2.3

> **核心**：通过 SRA Proxy 在每次用户消息前注入技能推荐上下文。
> **补充 skill**：`sra-cli-usage` 包含完整的 SRA CLI 命令参考和四维评分引擎原理。

---

## 一、SRA Proxy 调用铁律

**每次收到主人消息（非闲聊），必须按此流程调用 SRA：**

```bash
curl -s --noproxy '*' --max-time 10 -X POST http://127.0.0.1:8536/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "<主人消息>"}'
```

### 响应格式解析

```json
{
  "recommendations": [
    {"skill": "skill-name", "score": 72.5, "confidence": "medium",
     "reasons": ["name匹配'xxx'", "trigger'xxx'"], "description": "..."}
  ],
  "contract": {
    "required_skills": [],        // score >= 80
    "optional_skills": [...],     // 40 <= score < 80
    "confidence": "medium",       // high(≥80) / medium(≥60) / low
    "task_type": "类别名"
  },
  "should_auto_load": false,      // true 当有 score >= 80 的 skill
  "top_skill": null,              // 最高分 skill 名称
  "rag_context": "...",           // 格式化的推荐上下文文本
  "sra_available": true,
  "sra_version": "2.0.3"
}
```

### 处理逻辑

```
收到响应 →
├─ should_auto_load == true
│    ├─ skill_view(name=top_skill) 自动加载
│    └─ 回复开头标注 [SRA] 推荐
├─ rag_context 非空
│    └─ 将 rag_context 注入思考过程
├─ SRA 不可用 (sra_available=false)
│    └─ 跳过，回退标准流程
└─ 超时/异常
     └─ 降级，不阻塞消息
```

---

## 二、should_auto_load 为什么是 false？

SRA 的 `should_auto_load` 由 `build_contract()` 决定：

```python
THRESHOLD_STRONG = 80  # 强推荐线
THRESHOLD_WEAK = 40    # 弱推荐线

required = [s for s in scored if s.score >= 80]  # ← 这才是 should_auto_load=true 的条件
should_auto_load = len(required) > 0
```

**当前 SRA 最高分仅 ~60**，所以始终 false。要让 skill 达到 80+：

| 改进方向 | 效果 | 方法 |
|:---------|:----:|:-----|
| **补充 triggers** | +25/匹配 | 添加用户常说的关键词到 SKILL.md 的 triggers |
| **提高 SQS 分** | modifier 0.7→1.0 | 提升 skill 内容质量到 SQS ≥ 80 |
| **优化描述** | +8/词 | 在 description 中包含高频关键词 |
| **使用频率** | +2/次 | 多使用该 skill，积累场景记忆 |
| **短查询提升** | ×1.6 | ≤2 个词时自动 boost |

---

## 三、四维评分引擎速览

SRA 使用四维匹配（详见 `sra-cli-usage` skill 的完整说明）：

| 维度 | 权重 | 你能控制的 |
|:-----|:----:|:-----------|
| **词法** | 40% | 📝 triggers + name + description 关键词 |
| **语义** | 25% | 📝 description + body_keywords 覆盖 |
| **场景** | 20% | 🎯 使用频率（多用就加分） |
| **类别** | 15% | 🏷️ category + tags 设置 |

**质量惩罚**：SQS < 40 时最终分 ×0.4，SQS ≥ 80 时 ×1.0（不降权）

---

## 四、SRA 自动注入现状（重要 ⚠️ 2026-05-15 验证）

### 4.1 结论：Hermes 代码库中不存在 SRA 自动注入集成

**经源码全量验证（2026-05-15）：**

```bash
# 搜索整个 hermes-agent 代码库
grep -r "_query_sra_context" /home/ubuntu/.hermes/hermes-agent/ --include="*.py"
# → 无结果！此函数不存在于任何 Python 文件中

grep -r "sra\|SRA\|recommend\|8536" /home/ubuntu/.hermes/hermes-agent/run_agent.py
# → 无结果！run_agent.py（738KB）完全没有 SRA 相关代码

grep -r "sra\|SRA\|recommend\|8536" /home/ubuntu/.hermes/hermes-agent/gateway/run.py
# → 仅一个无关的 "not recommended" 字符串
```

| 检查项 | 结果 |
|:-------|:----:|
| `run_agent.py` 中 `_query_sra_context()` | ❌ 不存在 |
| `gateway/run.py` 中 SRA 调用 | ❌ 不存在 |
| agent.log 中 SRA 自动调用痕迹 | ❌ 仅用户对话内容含 sra 关键词 |
| agent.log 中 gateway 自动调 SRA | ❌ 无 |
| 整个 hermes-agent 代码库 | ❌ 零行 SRA 集成代码 |

### 4.2 为什么之前的文档说「内置注入机制」？

这是一个**过时/错误的描述**。SRA 项目确实设计了 `force level` 系统（见第五节），定义了 `on_user_message` 等注入点——但这些是 **SRA 侧的配置蓝图**，而 **Hermes 侧从未实现对应的集成代码**。

```
SRA 侧定义（force.py）               Hermes 侧实现
┌──────────────────────────┐       ┌──────────────────────┐
│ on_user_message          │ ──❌→ │ 无任何调用代码        │
│ pre_tool_call            │ ──❌→ │ 无                    │
│ post_tool_call           │ ──❌→ │ 无                    │
│ periodic                 │ ──❌→ │ 无                    │
└──────────────────────────┘       └──────────────────────┘
```

### 4.3 实际工作方式：手动调用是唯一途径

由于自动集成不存在，每次收到非闲聊消息时 **AI Agent 必须手动调用 SRA Proxy**。这是 SOUL.md 中规定的第一条规则，也是本 skill 第一节详细描述的流程。

**不要被「omni 已配置」麻痹**——omni 只是 SRA 侧允许的最高力度，但没有人（没有 Hermes 代码）在那些时机去调用 SRA。

### 4.4 如何验证自动注入是否真的存在

```bash
# 1. 检查源码中是否有 SRA 集成
grep -r "_query_sra_context\|sra_context\|_inject_sra" ~/.hermes/hermes-agent/ --include="*.py"

# 2. 检查 SRA 统计中的 total_requests 是否在自动增长
curl -s http://127.0.0.1:8536/stats | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'总请求: {d[\"total_requests\"]}')"

# 3. 检查 agent.log 中是否有 SRA 自动调用（非用户消息中的 sra 关键词）
grep -i "recommend.*8536\|sra.*context.*inject" ~/.hermes/logs/agent.log
```

### 4.5 如果未来实现自动注入

如果 Hermes 后续版本实现了 SRA 集成，会表现为：
- `run_agent.py` 中出现 `_query_sra_context()` 函数
- `gateway/` 中出现 SRA 调用
- `total_requests` 会在不手动调用的情况下自动增长
- agent.log 中出现 SRA recommend 的日志条目

---

## 五、运行时力度体系（SRA 侧配置 ⚠️）

> **重要：以下力度等级是 SRA 服务自身定义的配置，定义了「SRA 可以在哪些时机被调用」。**
> **但如前文第四节所述，Hermes 尚未实现任何时机的自动调用。**
> 这些等级是**潜在能力**，不是当前工作状态。

SRA 的 `force level` 控制其推荐引擎的理论注入时机：

| 级别 | 注入点 | omni 带来的额外功能 |
|:----|:-------|:--------------------|
| basic | 仅用户消息 | — |
| medium | 消息 + 关键工具前 | 写文件/改代码前检查 |
| advanced | 消息 + 全部工具前后 | 所有操作前后核查 |
| **omni** 🐉 | 全部 + 周期性 | **每 3 轮自动上下文漂移检测** |

**当前配置**：`🐉 omni` ✅（SRA 侧已允许最高力度，但 Hermes 侧未实现自动调用）

---

## 六、常见问题

| 问题 | 原因 | 修复 |
|:-----|:-----|:------|
| SRA 返回空推荐 | 查询与所有 skill 的 score < 40 | 检查查询是否太短/太泛，或补充 skill triggers |
| should_auto_load 一直 false | 所有 skill 得分 < 80 | 提升 skill SQS 质量分 + 补充 triggers |
| curl 超时 | SRA 索引构建中 | 检查 `sra stats` 等待索引就绪 |
| curl 连接被拒 | SRA Daemon 未运行 | `systemctl --user restart srad` |
| 推荐结果不相关 | skill 的 triggers/description 不够覆盖 | 补充对应 skill 的触发词 |

---

## 七、行为红牌 (Behavioral Red Flags) 🚨

> 以下陷阱与「常见问题」的区别：常见问题是技术层面的异常（SRA 连不上、超时等），行为红牌是 **AI Agent 自身的行为失误**，即使 SRA 正常也可能发生。

### 🚨 红牌 1：以为 SRA 会自动注入 = 不需要手动调

> ⚠️ **2026-05-15 更新**：经源码验证，Hermes 代码库中**不存在** `_query_sra_context()` 或任何 SRA 自动注入功能。之前的文档描述是过时的。详见第四节。

有些人可能会认为「SRA 配置了 omni 级别，应该会自动注入吧？」——但这是一个危险的误解。

```diff
- ❌ 错误：系统会自动帮我调 SRA，我不需要再手动 curl 了
+ ✅ 正确：我必须先手动 curl POST /recommend 获取 rag_context
+    内置机制是二次保险，不是第一道防线
```

**根因**：Section 四介绍的内置机制容易让人产生「自动处理」的错觉。但事实是——**你收到消息的第一个动作必须是调 SRA**，不能依赖系统自动注入。

### 🚨 红牌 2：关于 SRA 自身的消息不调 SRA

这是本次会话被主人纠正的具体教训。

```diff
- ❌ 错误：主人问"sra开启了吗"是 meta 问题，不需要调 SRA
- ❌ 错误：主人问"总结经验"是简单问题，不需要调 SRA
+ ✅ 正确：所有非闲聊消息，包括关于 SRA 自身的问题，都必须先调 SRA
```

**判断标准**：唯一能跳过 SRA 的是**纯闲聊**（打招呼、寒暄「今天天气不错」等）。其他所有消息——包括对 SRA 状态的查询、对工作流的反思——都**必须**先调 SRA。

### 🚨 红牌 3：以「问题简单」为由跳过 SRA

```diff
- ❌ 错误：这个问题太简单了，不需要 SRA 推荐也能回答
+ ✅ 正确：SRA 的作用不只是找到你缺的 skill——它还提供 rag_context 作为思考的锚点
+   哪怕你觉得不需要推荐，rag_context 也可能包含你没想到的上下文线索
```

**事实检查**：本次会话中 boku 认为「总结经验」很简单，跳过了 SRA。结果 SRA 返回了 `learning-review-cycle`（51.8分）和 `deep-research`（45.0分）——这两个 skill 对「总结经验」任务非常有帮助。

### 🚨 红牌 4：调 /health 代替 /recommend

```diff
- ❌ 错误：curl /health 返回 200 → SRA 在工作 → 不用调 /recommend 了
+ ✅ 正确：/health 只检查存活状态，/recommend 获取技能推荐上下文
+   两者是不同端点，各有用处，不可替代
```

本会话中 boku 先查了 `/health`，然后就直接回复了——这就是典型的「用健康检查代替推荐调用」。

### 🚨 红牌 5：事后补救而不事先预防

```diff
- ❌ 错误：被主人指出后才调 SRA
+ ✅ 正确：每次收到消息的第一个动作就是调 SRA，形成肌肉记忆
```

> **self-check（回复前自问）**：我调用 SRA Proxy `/recommend` 了吗？
> 如果答案是「没调」或「调的是 /health」→ 🛑 先调再回复！

---

### 🚨 红牌 6：源码直接创建在部署目标目录

```diff
- ❌ 错误：直接在 ~/.hermes/hermes-agent/plugins/sra-guard/ 下创建文件
+ ✅ 正确：源码在项目目录中管理（如 ~/projects/sra/plugins/sra-guard/）
+     通过安装脚本部署到 Hermes plugins 目录
```

**self-check**：创建文件前问自己「这个文件属于哪个 git 仓库？」如果答案是「不属于任何仓库」→ 先找到正确的项目目录再创建。

---

## 八、相关文件路径

| 路径 | 用途 |
|:-----|:------|
| `~/.sra/config.json` | SRA 配置文件（force level, port, interval） |
| `~/.sra/data/sqs-scores.json` | SQS 质量评分数据 |
| `~/.sra/srad.sock` | Unix Socket（IPC 通信） |
| `~/.hermes/hermes-agent/run_agent.py` | Hermes 核心对话循环——目前无 SRA 集成，待未来实现 |
| `~/projects/sra/skill_advisor/advisor.py` | SRA 推荐引擎（`build_contract()` + `recommend()`） |
| `~/projects/sra/skill_advisor/matcher.py` | 四维匹配引擎（权重 + 评分逻辑） |
| `~/projects/sra/skill_advisor/runtime/force.py` | 力度管理器（4 级注入点控制） |
| `~/projects/sra/venv/bin/sra` | SRA CLI 入口 |

## 九、EPIC-004 进展：从补丁到插件的重构

> **2026-05-15 更新**: EPIC-004 (SRA Hermes 原生插件集成) 已批准，Phase 0 已完成。

### 当前状态

| Phase | 状态 | 内容 |
|:------|:----:|:------|
| Phase 0: 插件框架 | ✅ 完成 | sra-guard 插件目录 + pre_llm_call hook + client.py + 安装脚本 + 文档对齐 |
| Phase 1: 消息注入 | ✅ 完成 | [SRA] 上下文格式化 + MD5 缓存 + 集成测试（40 tests） |
| Phase 2: 工具校验 | ⏳ 待开始 | pre_tool_call → POST /validate |
| Phase 3-6 | ⏳ 待开始 | 轨迹追踪/重注入/文档/CI |

### 补丁方案 → 插件方案 迁移

```
旧方案 (sed 补丁 run_agent.py):            新方案 (Hermes 插件):
  patches/hermes-sra-integration.patch →     plugins/sra-guard/plugin.yaml
  install-hermes-integration.sh          →   自动发现 (无需安装)
  每次 Hermes 升级需重装                   →   升级后自动保留
  urllib.request                          →   httpx (与 Hermes 一致)
  except Exception: pass                  →   logger.warning + 返回 None
  无测试                                  →   19 个自动化测试
```

**重要**: 在 EPIC-004 全部完成前，手动 curl 调用 `/recommend` 仍是唯一可靠的注入方式。详见本节铁律。

### 根因分析与修复方向

详见 `references/2026-05-15-epic004-root-cause-analysis.md`。

---

## 十、本次会话知识沉淀

### 📁 参考文件

| 文件 | 内容 | 日期 |
|:-----|:------|:----:|
| `references/2026-05-15-sra-skip-correction.md` | 被主人纠正跳过 SRA 调用的案例复盘 | 2026-05-15 |
| `references/2026-05-15-autoinjection-test.md` | Hermes 无 SRA 自动注入的源码验证报告 | 2026-05-15 |
| `references/2026-05-15-root-cause-analysis.md` | 自动注入从未工作的根因分析（2026-05-15 深度审计） | 2026-05-15 |
| `references/hermes-plugin-architecture.md` | Hermes 插件架构指南 — sra-guard 模式（importlib + hook 注册 + 双协议通信） | 2026-05-15 |

### 🧠 Memory 新增

**第11条 - SRA 调用铁律**：
> SRA 调用铁律：每条非闲聊消息必须先 curl POST /recommend 获取 rag_context→标注[SRA]→再处理。曾被主人纠正跳过此步，不可再犯。

### 📁 L2 Experience 新增

- `exp-20260515-sra-proxy-调用铁律被主人纠正跳` — 完整背景、教训、正确流程、自检方式

---

## 十、根因分析：自动注入为何从未工作（2026-05-15 深度审计）

> 本节记录 2026-05-15 对 SRA 自动注入功能的完整源码审计。发现：**SRA 自动注入从未真正工作过**。

### 10.1 核心发现

```
[文档宣称的状态]                  [代码真实状态]
┌──────────────────────┐        ┌──────────────────────┐
│ EPIC-001: ✅ 已完成   │        │ run_agent.py:        │
│ INTEGRATION.md:      │   ≠   │ ❌ _query_sra_context│
│ 自动触发每次消息      │        │    不存在             │
│ README: "自动注入"    │        │ ❌ 无 .sra-backup     │
└──────────────────────┘        └──────────────────────┘
```

**证据链**：

| 检查项 | 结果 | 证据 |
|:-------|:----:|:-----|
| `run_agent.py` 中 `_query_sra_context()` | ❌ 不存在 | `grep` 零匹配 |
| 任意 SRA 相关代码在 Hermes 代码库 | ❌ 不存在 | 整个 hermes-agent/ 无 sra 引用 |
| 备份文件 `run_agent.py.sra-backup` | ❌ 不存在 | 文件缺失 |
| 补丁文件 `patches/hermes-sra-integration.patch` | ✅ 存在 | 112 行定义完整 |
| 安装脚本 `scripts/install-hermes-integration.sh` | ✅ 存在 | 259 行逻辑完整 |
| **脚本是否被执行过？** | ❌ **否** | 无备份文件 + run_agent.py 未修改 |

### 10.2 四重根因

| # | 根因 | 归属维度 | 描述 |
|:-:|:-----|:--------|:------|
| ① | **EPIC-001 AC 只检查了 SRA 侧** | SDD 缺陷 | 6 个 AC 全部针对 SRA 端（补丁文件存在、脚本存在），**没有一个 AC 要求验证 Hermes 端是否被修改** |
| ② | **无跨项目端到端验证门禁** | 流程缺陷 | 没有集成测试检查 `run_agent.py` 是否包含 `_query_sra_context()`。AC 审计只检查文档中的 `[x]`，不验证代码 |
| ③ | **`sra install hermes` 是打印语句** | 代码缺陷 | 命令只是 `print("步骤 1...步骤 2...")`，**不执行任何实际安装**。真正的安装脚本是 `install-hermes-integration.sh` 但从未运行 |
| ④ | **Hermes 升级覆盖补丁** | 维护缺陷 | 即使曾成功安装过，Hermes 从 v20260422 → v0.12.0 的升级也会覆盖对 `run_agent.py` 的修改 |

### 10.3 EPIC-003 文档漂移：标记 ✅ 但未实现的 AC

EPIC-003 的 AC 审计脚本 (`ac-audit.py`) 只检查 `[x]` 标记是否存在，**不验证对应的代码是否真实存在**。导致以下 AC 被标记 ✅ 但从未实现：

| Story | AC | 标记 | 实际状态 |
|:------|:---|:----:|:--------|
| Story 1 | Hermes pre_tool_call hook 集成的代码 | ✅ | ❌ Hermes plugins 中无 sra-guard |
| Story 3 | `skill_view()` 自动 POST /record | ✅ | ❌ run_agent.py 无拦截代码 |
| Story 3 | 工具调用自动 POST /record | ✅ | ❌ model_tools.py 无 SRA 引用 |
| Story 4 | 每 5 轮自动重查 SRA | ✅ | ❌ 无周期性重注入逻辑 |
| Story 6 | `config.yaml` 可覆盖 force level | ✅ | ❌ config.yaml 无 SRA 配置项 |

### 10.4 Force 层级图解：SRA 侧已实现但 Hermes 侧无人调用

```
SRA 侧定义 (force.py)               Hermes 侧实现
┌──────────────────────────┐       ┌──────────────────────┐
│ on_user_message          │ ──❌→ │ 无人调用 SRA          │
│ pre_tool_call            │ ──❌→ │ 无人调用 /validate    │
│ post_tool_call           │ ──❌→ │ 无人调用 /record      │
│ periodic                 │ ──❌→ │ 无人周期性重查        │
└──────────────────────────┘       └──────────────────────┘

SRA Daemon 像一台广播电台——所有节目（/recommend、/validate、/record）
都已就绪，但没有收听者（Hermes 端代码）在调频接收。
```

### 10.5 深层模式：三类文档漂移

这次审计暴露了三种文档漂移模式，在跨项目集成时尤其危险：

| 类型 | 描述 | 本案例实例 | 检测难度 |
|:----|:-----|:----------|:--------:|
| **幻影功能** | 文档描述的功能在代码中从未存在 | `_query_sra_context()` 整个函数不存在 | 高——需要跨项目搜索 |
| **幻影集成** | 文档称 A→B 已集成，实际连接从未建立 | force.py 定义了但无消费者调用 | 中——需要在两个代码库追调用链 |
| **幻影 AC** | AC 标记 ✅ 但对应的变更从未实现 | Hermes pre_tool_call hook 集成 ✅ | 低——检查代码是否存在即可 |

### 10.6 自检：如何验证自动注入是否真实存在

```bash
# 1. 检查 run_agent.py 是否存在 SRA 函数
grep -n "_query_sra_context" ~/.hermes/hermes-agent/run_agent.py

# 2. 检查是否有 SRA 插件
ls ~/.hermes/hermes-agent/plugins/sra-guard/ 2>/dev/null

# 3. 检查 SRA 统计——如果 total_requests 不手动调用也增长 → 有自动调用
curl -s http://127.0.0.1:8536/stats | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'总请求: {d[\"total_requests\"]}')"

# 4. 检查 agent.log 是否有 SRA 自动调用痕迹
grep -i "recommend.*8536\|sra.*context.*inject" ~/.hermes/logs/agent.log

# 5. 检查 sra 安装状态
# 真正的安装脚本位置：
ls ~/projects/sra/scripts/install-hermes-integration.sh
```

### 10.7 根因修复方向

修复不是重新运行 `install-hermes-integration.sh`，而是：

1. **用 Hermes 插件系统替代 sed 补丁**——Hermes 已有 `pre_llm_call` / `pre_tool_call` 钩子
2. **增加跨项目 AC 验证门禁**——AC 涉及外部项目时，必须在外部项目中验证代码存在
3. **AC 审计增强**——从只检查 `[x]` 标记升级为检查代码与文档的双向一致性

详见 `references/2026-05-15-root-cause-analysis.md`
