---
name: learning-workflow
description: "所有学习/研究任务的强制流程拦截器。通过状态机+文件标志物实现防跳过机制。任何涉及'学习、研究、了解、搞懂'的请求必须先走此流程。"
version: 1.0.0
triggers:
  - 学习
  - 研究
  - 了解
  - 搞懂
  - 看看
  - 学学
  - 查一下
  - 调研
  - 探索
  - 掌握
  - study
  - learn
  - research
depends_on:
  - skill-creator
  - web-access
design_pattern: Pipeline
skill_type: Workflow
---

# 🧠 Learning Workflow · 强制学习流程 v1.0

> **铁律**：任何学习任务（用户说"学习/研究/了解XXX"）必须严格走此流程。
## 〇、🚨 拦截规则 (Pre-flight Gate)

**在任何 Skill 操作前，必须通过此检查门！**

```
[任务开始]
   ↓
[检查 -1] 🛑 强制运行 skill_finder.py 扫描是否有可用 Skill
   ├─ 有高置信度结果？ → 是 → 🛑 **强制 skill_view 加载该 Skill**，必须阅读后执行！
   └─ 否 (或无结果) → 继续后续检查
   ↓
[检查 0] 是否为知识沉淀任务？ → 是 → 🛑 检查是否经过 learning-workflow 的搜索阶段！
   ↓
[状态检查] ~/.hermes/learning_state.json 是否存在？
   ├─ 无 → 🆕 初始化状态机，进入 STEP 1
   ├─ 有 → 📖 读取当前进度，从断点继续
   └─ 已完成 → ✅ 直接输出学习成果
```

## 一、状态机定义（State Machine）

**状态文件**：`~/.hermes/learning_state.json`

```json
{
  "topic": "写作风格指南",
  "current_step": 0,
  "steps": {
    "step0_map": {"status": "pending", "artifact": null},
    "step1_search": {"status": "pending", "artifact": null},
    "step2_read": {"status": "pending", "artifact": null},
    "step3_extract": {"status": "pending", "artifact": null},
    "step4_scaffold": {"status": "pending", "artifact": null},
    "step5_validate": {"status": "pending", "artifact": null}
  }
}
```

### 状态流转规则
| 步骤 | 动作 | 前置条件 | 产出物 | 状态更新 |
|:---|:---|:---|:---|:---|
| **STEP 0** | **知识图谱分析** | 无 | `~/.hermes/learning/knowledge_map.md` | step0_map: completed |
| **STEP 1** | 针对性搜索 | **STEP 0 完成** | `~/.hermes/learning/raw_search_results.md` | step1_search: completed |
| **STEP 2** | 深度阅读 | step1 完成 | `~/.hermes/learning/reading_notes.md` | step2_read: completed |
| **STEP 3** | 知识提炼 | step2 完成 | `~/.hermes/learning/extracted_knowledge.md` | step3_extract: completed |
| **STEP 4** | Skill 脚手架 | step3 完成 | `~/.hermes/skills/[name]/SKILL.md` | step4_scaffold: completed |
| **STEP 5** | 验证测试 | step4 完成 | 测试用例通过 | step5_validate: completed |

**🚨 硬拦截**：如果前置步骤的 artifact 文件不存在，**禁止进入下一步**！必须报错并要求用户确认是否跳过（默认不跳过）。

## 二、各步骤详细指令

### STEP 1: 🔍 联网搜索（必须执行）
1. 加载 `web-access` skill
2. 使用 Tavily MCP 搜索 3-5 个高质量来源
3. **必须**将搜索结果原文摘要写入 `~/.hermes/learning/raw_search_results.md`
4. 更新 `learning_state.json` 的 step1_search 状态

**🚩 禁止行为**：
- ❌ 用训练数据里的知识冒充搜索结果
- ❌ 只搜索 1 个来源就声称"完成了"
- ❌ 不保存原始素材直接跳到总结

### STEP 2: 📖 深度阅读（至少 3 篇）
1. 使用 `mcp_tavily_tavily_extract` 或 `mcp_tavily_tavily_crawl` 提取正文
2. **必须**将阅读笔记写入 `~/.hermes/learning/reading_notes.md`
3. 笔记格式：`## 来源 URL\n- 核心观点\n- 可操作建议\n- 与主题的相关性`

### STEP 3: 🧪 知识提炼
1. 从阅读笔记中提取**可复用的模式/规则/流程**
2. 输出到 `~/.hermes/learning/extracted_knowledge.md`
3. 必须包含：核心概念、操作步骤、避坑指南、应用场景

### STEP 4: 🏗️ Skill 脚手架
1. 加载 `skill-creator`，走工作流 B（学习沉淀）
2. **必须**通过 dependency-check（检查依赖的 skill 是否存在）
3. 生成 SKILL.md 并写入对应目录

### STEP 5: ✅ 验证测试（强烈推荐子代理黑盒测试）
**🚀 最佳实践**：不要手动测试！启动一个子代理（Subagent）作为 QA 机器人。
1.  **启动子代理**：使用 `delegate_task`，赋予 `toolsets=['terminal', 'file', 'skills']`。
2.  **测试目标**：要求子代理作为“不知道规则的用户”，尝试触发 Skill。
3.  **必测用例**：
    -   **正常流**：初始化 -> 搜索 -> 阅读 -> 提炼 -> 完成。
    -   **异常流**：初始化后，直接尝试跳到 STEP 4（预期：应被脚本拦截报错）。
    -   **并发流**：同时进行两个不同的学习任务（预期：状态文件不应冲突）。
4.  **收集报告**：子代理输出测试结果，确认拦截机制有效后，标记主任务 STEP 5 为 completed。

## 三、防呆设计（Anti-Bypass）

### 1. 文件存在性检查
```python
import os
def check_step(step_name, artifact_path):
    if not os.path.exists(artifact_path):
        raise RuntimeError(f"🚨 STEP {step_name} 未完成！产出物不存在：{artifact_path}")
```

### 2. 搜索真实性验证
- 搜索结果必须包含**真实的 URL 和时间戳**
- 如果 `raw_search_results.md` 中的 URL 无法访问，必须重新搜索
- 禁止使用"根据我的知识"等模糊表述替代搜索

### 3. 进度汇报机制
每完成一个 STEP，必须向用户汇报：
```
✅ STEP 1 完成：已搜索 5 篇资料，保存到 raw_search_results.md
📊 当前进度：1/5（20%）
⏭️ 下一步：深度阅读（预计 3 分钟）
```

## 四、异常处理

| 异常 | 处理方式 |
|:---|:---|
| 搜索无结果 | 更换关键词，最多重试 3 次；仍无结果则告知用户并建议换个角度 |
| 网页无法访问 | 标记为"不可读"，跳过并搜索替代来源 |
| 用户要求跳过某步 | 必须警告风险，用户明确确认后在 state.json 中标记 `skipped: true` |
| skill-creator 依赖检查失败 | 停止流程，先解决依赖问题再继续 |

## 五、完成标志

当 `learning_state.json` 中所有 steps 状态为 completed 时：
1. 将学习成果**交付给用户**（摘要或文件）
2. 询问是否将本次流程经验**沉淀为永久 skill**
3. 归档 state.json 到 `~/.hermes/learning/archive/[timestamp].json`

---

**🔒 本 skill 为强制拦截器，任何学习任务不得绕过！**
