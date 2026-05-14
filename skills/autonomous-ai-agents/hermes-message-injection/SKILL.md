---
name: hermes-message-injection
description: "向 Hermes Agent 的消息管道注入 SRA 技能推荐。每次用户消息自动拦截 → 调 SRA Proxy /recommend → 将结果作为前缀注入消息前。涵盖 run_conversation() 注入点、should_auto_load 逻辑、四维评分解读、omni 级别周期性重检。"
version: 2.3.0
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
  - 消息注入
  - 上下文注入
  - hermes-message-injection
depends_on:
  - hermes-agent
  - sra-cli-usage
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

## 四、Hermes 内置注入机制

从 Hermes v0.12.0+，`_query_sra_context()` 已内置到 `run_agent.py`：

```
run_conversation()
  ├─ _query_sra_context(message)     ← 自动调 SRA Proxy
  │   ├─ SRA 可用 → 获取 recs → 格式化为前缀
  │   └─ SRA 不可用 → 返回空字符串
  ├─ f"{sra_ctx}\n\n{user_message}"  ← 注入到消息前
  └─ 进入 LLM 处理
```

- 超时：2 秒（快速失败不阻塞）
- 缓存：MD5 hash 避免重复请求
- 降级：全 catch → 空字符串

---

## 五、运行时力度体系（omni 级别）

SRA 的 `force level` 控制注入时机：

| 级别 | 注入点 | omni 带来的额外功能 |
|:----|:-------|:--------------------|
| basic | 仅用户消息 | — |
| medium | 消息 + 关键工具前 | 写文件/改代码前检查 |
| advanced | 消息 + 全部工具前后 | 所有操作前后核查 |
| **omni** 🐉 | 全部 + 周期性 | **每 3 轮自动上下文漂移检测** |

**当前状态**：`🐉 omni` ✅（已配置并重启生效）

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

## 七、相关文件路径

| 路径 | 用途 |
|:-----|:------|
| `~/.sra/config.json` | SRA 配置文件（force level, port, interval） |
| `~/.sra/data/sqs-scores.json` | SQS 质量评分数据 |
| `~/.sra/srad.sock` | Unix Socket（IPC 通信） |
| `~/.hermes/hermes-agent/run_agent.py` | Hermes 的注入点（`_query_sra_context()`） |
| `~/projects/sra/skill_advisor/advisor.py` | SRA 推荐引擎（`build_contract()` + `recommend()`） |
| `~/projects/sra/skill_advisor/matcher.py` | 四维匹配引擎（权重 + 评分逻辑） |
| `~/projects/sra/skill_advisor/runtime/force.py` | 力度管理器（4 级注入点控制） |
| `~/projects/sra/venv/bin/sra` | SRA CLI 入口 |
