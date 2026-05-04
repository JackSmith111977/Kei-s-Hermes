---
name: learning-workflow
description: "所有学习/研究任务的强制流程拦截器。通过状态机+文件标志物实现防跳过机制。任何涉及'学习、研究、了解、搞懂'的请求必须先走此流程。v3.0 新增：自驱动循环集成、学习报告自动生成、知识缺口探测。"
version: 3.1.0
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
  - 沉淀
  - 总结复盘
  - 学习周报
  - 学习月报
  - 技能盘点
  - study
  - learn
  - research
  - explore
  - review
depends_on:
  - skill-creator
  - web-access
  - learning
  - learning-review-cycle
design_pattern: Pipeline
skill_type: Workflow
---

# 🧠 Learning Workflow · 强制学习流程 v3.0

> **铁律**：任何学习任务（用户说"学习/研究/了解XXX"）必须严格走此流程。
> **v3.0 重大更新**：自驱动学习循环、学习报告自动生成、知识缺口自动探测。

---

## 〇、🚨 强制拦截流程 (MANDATORY Gate)

**在任何任务开始前，必须按顺序执行：**

```
[任务开始]
   ↓
[检查 -2] 🛑 运行 pre_flight.py → BLOCKED? → 🛑 立即停止！
   ↓ PASS
[检查 -1] 🛑 运行 skill_finder_v2.py → 有 ≥ 50 分的 skill → 强制加载！
   ↓ 无高匹配 skill
[检查 0] 是否需要走学习流程？(涉及"学习/研究/了解/查/探索")
   ├─ 是 → 进入学习状态机
   └─ 否 → 正常处理
```

**🔒 防跳过机制：**
- 所有涉及"学习/研究"关键词的任务，必须先调用 `learning-state.py` 检查状态
- 如果状态文件不存在，直接初始化新任务
- 禁止直接跳过搜索/阅读步骤去创建 skill

---

## 一、双模式选择 (v2.0 新增)

根据任务复杂度选择模式：

| 模式 | 适用场景 | 流程 | 预计耗时 |
|------|----------|------|----------|
| **⚡ 快速模式** | 简单查询/了解概念 | STEP 0→1→3→6 | ~5-10 分钟 |
| **🔬 深度模式** | 系统学习/创建 skill | 全流程 STEP 0→6 | ~20-60 分钟 |

**选择标准：**
- 用户说"查一下/看看/了解下" → 快速模式
- 用户说"学习/研究/深度学习/搞懂" → 深度模式
- 不确定时 → 询问用户

---

## 二、状态机定义（v2.0 多任务版）

**状态文件**：`~/.hermes/learning_state.json`
**历史文件**：`~/.hermes/learning_history.json`

新格式（多任务支持）：
```json
{
  "task_id_1": {
    "topic": "学习主题",
    "task_id": "task_id_1",
    "created_at": "2026-05-04T14:00:00",
    "current_step": 1,
    "steps": {
      "step0_map": {"status": "completed", "artifact": "..."},
      "step1_search": {"status": "in_progress", "artifact": "..."},
      "step2_read": {"status": "pending", "artifact": "..."},
      "step3_extract": {"status": "pending", "artifact": "..."},
      "step4_scaffold": {"status": "pending", "artifact": null},
      "step5_validate": {"status": "pending", "artifact": null}
    }
  }
}
```

### 步骤权重（进度估算）

| 步骤 | 权重 | 快速模式 | 深度模式 |
|------|------|----------|----------|
| **STEP 0** 知识图谱 | 5% | ✅ 必做 | ✅ 必做 |
| **STEP 1** 联网搜索 | 20% | ✅ 必做 | ✅ 必做 |
| **STEP 2** 深度阅读 | 30% | ❌ 跳过 | ✅ 必做 |
| **STEP 3** 知识提炼 | 20% | ✅ (精简版) | ✅ (完整版) |
| **STEP 4** Skill 脚手架 | 15% | ❌ 跳过 | ✅ 必做 |
| **STEP 5** 验证测试 | 10% | ❌ 跳过 | ✅ 必做 |

### 状态流转规则

| 步骤 | 动作 | 前置条件 | 产出物 | 命令 |
|:---|:---|:---|:---|:---|
| **STEP 0** | 知识图谱分析 | 初始化完成 | `~/.hermes/learning/knowledge_map.md` | `complete step0_map` |
| **STEP 1** | 针对性搜索 | STEP 0 完成 | `~/.hermes/learning/raw_search_results.md` | `complete step1_search` |
| **STEP 2** | 深度阅读 | step1 完成 | `~/.hermes/learning/reading_notes.md` | `complete step2_read` |
| **STEP 3** | 知识提炼 | step2 完成 | `~/.hermes/learning/extracted_knowledge.md` | `complete step3_extract` |
| **STEP 4** | Skill 脚手架 | step3 完成 | `~/.hermes/skills/[name]/SKILL.md` | `complete step4_scaffold` |
| **STEP 5** | 验证测试 | step4 完成 | 测试用例通过 | `complete step5_validate` |

> 🚨 **硬拦截**：前置步骤的 artifact 文件不存在时，禁止进入下一步！

---

## 三、各步骤详细指令

### STEP 0: 📐 知识图谱分析（v2.0 增强）

1. **分析主题复杂度**：是简单主题还是复杂主题？
2. **决定学习模式**：快速模式还是深度模式？
3. **如果是复杂主题** → 拆分为原子子主题
4. 输出到 `knowledge_map.md`

**知识图谱模板：**
```markdown
# 知识图谱：{主题}
## 复杂度评估：{简单/中等/复杂}
## 推荐模式：{快速/深度}
## 子主题拆分（如适用）：
1. {子主题1}
2. {子主题2}
## 预期输出：{已有 skill 更新 / 新 skill / 笔记}
```

**进度汇报**：`learning-state.py complete step0_map`

---

### STEP 1: 🔍 联网搜索（必须执行）

1. 加载 `web-access` skill
2. 使用 Tavily MCP 搜索 3-5 个高质量来源
3. **必须**将搜索结果原文摘要写入 `~/.hermes/learning/raw_search_results.md`
4. **进度汇报**：`learning-state.py complete step1_search`

**🚩 禁止行为**：
- ❌ 用训练数据里的知识冒充搜索结果
- ❌ 只搜索 1 个来源就声称"完成了"
- ❌ 不保存原始素材直接跳到总结
- ❌ 复杂主题不拆分直接搜索

**进度汇报示例：**
```
✅ STEP 1 完成：已搜索 5 篇资料，保存到 raw_search_results.md
📊 当前进度：20%（1/5 步骤完成）
⏭️ 下一步：深度阅读（预计 10 分钟）
```

---

### STEP 2: 📖 深度阅读（快速模式跳过）

1. 使用 `mcp_tavily_tavily_extract` 或 `mcp_tavily_tavily_crawl` 提取正文
2. **必须**将阅读笔记写入 `~/.hermes/learning/reading_notes.md`
3. 笔记格式：`## 来源 URL\n- 核心观点\n- 可操作建议\n- 与主题的相关性`
4. **进度汇报**：`learning-state.py complete step2_read`

**快速模式跳过**：直接标记为 skipped 并记录原因

---

### STEP 3: 🧪 知识提炼

1. 从阅读笔记中提取**可复用的模式/规则/流程**
2. 输出到 `~/.hermes/learning/extracted_knowledge.md`
3. 必须包含：核心概念、操作步骤、避坑指南、应用场景
4. **进度汇报**：`learning-state.py complete step3_extract`

**快速模式精简版：**
- 直接从搜索结果提炼关键信息
- 输出简化版知识总结

---

### STEP 4: 🏗️ Skill 脚手架（深度模式 / 快速模式跳过）

1. 加载 `skill-creator`，走工作流 B（学习沉淀）
2. **必须**通过 dependency-check（检查依赖的 skill 是否存在）
3. 生成 SKILL.md 并写入对应目录
4. **进度汇报**：`learning-state.py complete step4_scaffold`

---

### STEP 5: ✅ 验证测试（深度模式 / 快速模式跳过）

**🚀 最佳实践**：不要手动测试！启动一个子代理（Subagent）作为 QA 机器人。
1. **启动子代理**：使用 `delegate_task`，赋予 `toolsets=['terminal', 'file', 'skills']`
2. **测试目标**：要求子代理作为"不知道规则的用户"，尝试触发 Skill
3. **必测用例**：
   - **正常流**：初始化 → 搜索 → 阅读 → 提炼 → 完成
   - **异常流**：初始化后直接跳到 STEP 4（预期：拦截报错）
4. **进度汇报**：`learning-state.py complete step5_validate`

---

### STEP 5.5: 🔄 深度循环门禁 (Deep Loop Gate) — v3.1 新增

**基于前沿研究的关键机制**（受 Memento-Skills 2025、RISE NeurIPS 2024 启发）：

在 STEP 5 验证之后、STEP 6 反思之前，执行循环质量门检：

```
STEP 5 验证结果 → 
├─ 通过（质量分 ≥ 60）→ 进入 STEP 6 反思
└─ 不通过（质量分 < 60）→ 
     分析失败类型 →
     ├─ 信息不足 → 回到 STEP 1 重新搜索（Loop N+1）
     ├─ 理解不深 → 回到 STEP 2 重新阅读（Loop N+1）
     ├─ 提炼不好 → 回到 STEP 3 重新提炼（Loop N+1）
     └─ 设计不好 → 回到 STEP 4 重新设计（Loop N+1）
```

**学习质量评分公式**：
```
学习质量 = 信息覆盖度(30) + 交叉验证得分(25) + 可操作性(25) + 结构完整度(20)
```

**评分 < 60**：🛑 拦截！必须进入 Loop N+1 重新学习
**评分 60-79**：⚠️ 警告，可以进入 STEP 6 但需标记"待改进"
**评分 ≥ 80**：✅ 通过，进入 STEP 6

**反思检查点 (Reflection Tokens)**：（类比 Self-RAG 2023）

| 检查点 | 位置 | 反思问题 |
|--------|------|----------|
| RETRIEVE_CHECK | STEP 1 后 | 搜索结果是否覆盖了主题的各个方面？来源权威性是否达标？ |
| COMPREHEND_CHECK | STEP 2 后 | 是否真正理解了核心概念？还是只是复制粘贴？ |
| EXTRACT_CHECK | STEP 3 后 | 提炼的知识是否可操作？能否指导实际操作？ |
| SKILL_CHECK | STEP 4 后 | Skill 的结构是否完整？是否有避坑指南和示例？ |
| VALIDATE_CHECK | STEP 5 后 | 验证是否充分？是否覆盖了正常流和异常流？ |

**循环次数限制**：最多 3 次循环（Loop N, N+1, N+2）。超过 3 次仍未通过则报告用户请求协助。

### STEP 6: 📝 反思迭代（v3.1 增强）

**每次学习/研究任务完成后执行：**

1. 运行 `learning-state.py list` 查看任务概览
2. **搜索策略反思**：本次搜索效果如何？记录可复用的技巧
3. **更新 learning skill**：将本次积累的方法论改进写入 learning skill
4. **归档任务**：`learning-state.py reset [task_id]`

**反思输出格式**：
```markdown
## 学习反思：{主题}
### 搜索策略有效性
- 使用关键词：...
- 效果评估：{高效/一般/不理想}
- 改进建议：...

### 方法论改进
- 新发现的高质量信息源：...
- 可复用的搜索/过滤技巧：...

### 下次改进
- ...
```

**反思记录文件**：`~/.hermes/learning/reflections/{task_id}.md`

---

## 四、进度汇报机制

每完成一个 STEP，必须向用户汇报进度：

```
✅ STEP X 完成：[描述做了什么]
📊 当前进度：{N}%（X/5 步骤完成） — [======>-------------] {N}%
⏱️  预计剩余：~{M} 分钟
⏭️  下一步：[下一步做什么]
```

如果任务中断（用户要求中断 / 外部因素），必须说明原因：
```
⚠️ 任务中断：[原因]
📊 当前进度：{N}%
💡 使用以下命令恢复：learning-state.py status
```

---

## 五、防呆设计（Anti-Bypass）

### 1. 文件存在性检查

`learning-state.py check <step_name>` 会自动检查：
- 状态是否为 completed
- artifact 文件是否存在

### 2. 搜索真实性验证

- 搜索结果必须包含**真实的 URL 和时间戳**
- 如果 `raw_search_results.md` 中的 URL 无法访问，必须重新搜索
- 禁止使用"根据我的知识"等模糊表述替代搜索

### 3. 步骤依赖强制

```python
# 不允许跳过前置步骤
before_step2 = ["step0_map", "step1_search"]
# 不允许在未完成 STEP 1 的情况下做 STEP 2
```

---

## 六、异常处理

| 异常 | 处理方式 |
|:---|:---|
| 搜索无结果 | 更换关键词，最多重试 3 次；仍无结果则告知用户并建议换个角度 |
| 网页无法访问 | 标记为"不可读"，跳过并搜索替代来源 |
| 用户要求跳过某步 | 必须警告风险，用户明确确认后标记 `skipped: true` |
| 多任务冲突 | 用 task_id 区分，不影响其他任务的状态 |
| skill-creator 依赖检查失败 | 停止流程，先解决依赖问题再继续 |
| 自动学习触发失败 | 写入 gap_queue，下次 Review 重试 |

---

## 七、完成标志（v3.0 增强）

当 `learning-state.py status` 显示进度为 100% 时：
1. 将学习成果**交付给用户**（摘要或文件）
2. **自动生成学习总结**（v3.0 新增）
   ```bash
   python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py summary "{topic}" "{mode}" {duration} "{output}"
   ```
   - `{topic}` = 学习主题
   - `{mode}` = 快速 或 深度
   - `{duration}` = 耗时分钟数
   - `{output}` = "skill_name" 或 "笔记"
3. **检查是否产生知识缺口**（v3.0 新增）
   - 如果学习过程中遇到困难、发现 skill 过时 → 调用 `review-engine.py gap-add`
   - 示例：`review-engine.py gap-add knowledge_outdated "WeasyPrint v62 API 变更" high`
4. 执行**学习反思**（STEP 6）
5. **归档状态**：`learning-state.py reset [task_id]`
6. 询问是否将本次流程经验**沉淀为永久 skill**

---

## 八、自驱动循环集成（v3.0 新增）

### 8.1 自驱动三环结构

```
学习环(任务) → 每次学习完成后，自动触发 Review
Review环(定时) → 扫描新鲜度，自动探测缺口
总结环(产出) → 自动生成周报/月报
```

### 8.2 什么时候会自驱动？

**定时触发：**
- **每周**：`review-engine.py weekly` → 生成周报，列出需要更新的 skill
- **每月**：`review-engine.py monthly` → 生成月报+深度扫描+建议学习计划

**条件触发：**
- **缺口 ≥ 3 个高优先级** → `review-engine.py auto-check` → 自动发起深度学习

**手动触发：**
- 用户说"review/复盘/盘点" → 加载 learning-review-cycle skill

### 8.3 注册定时任务

通过 `cronjob` 注册两个定时任务：
1. `每周一早 9 点` → review-engine.py weekly
2. `每月 1 号早 9 点` → review-engine.py monthly

### 8.4 间隔复习机制 (Spaced Review) — v3.1 新增

**基于认知科学证据最强的学习机制**（Cepeda et al. 2008, 254项meta分析）：

学习完成后，不是一次性归档，而是安排**间隔复习**：

| 复习时间 | 复习类型 | 检查内容 |
|----------|----------|----------|
| **1 天后** | 快速回顾 | skill 是否可执行？是否有明显的错误？ |
| **7 天后** | 深度回顾 | 是否有新知识出现？是否需要更新？ |
| **30 天后** | 全面审计 | 对比最新版本文档，检查 API 变更、版本更新 |

**实现方式**：
- 学习完成时自动注册 3 个 cron 任务
- 复习时自动加载对应 skill，检查新鲜度
- 如果发现问题 → 自动加入 gap_queue

### 8.5 防无限循环

- 自动触发的学习任务**禁止再次触发自动学习**
- 每次自驱动学习前检查 gap_queue 中的 `auto_learn_enabled` 标志
- 超过 20 个未处理缺口时自动暂停

---

## 九、使用示例

### 快速模式（简单查询）
```
> 查一下 Python 3.13 有什么新特性

1. STEP 0: 知识图谱 → 决定快速模式
2. STEP 1: 搜索 3-5 篇资料
3. STEP 3: 提炼关键信息
4. STEP 6: 输出总结 + 反思
```

### 深度模式（系统学习）
```
> 学习一下 WeasyPrint 的 PDF 生成

1. STEP 0: 知识图谱 → 决定深度模式
2. STEP 1: 搜索官方文档 + 教程
3. STEP 2: 精读 3+ 篇
4. STEP 3: 提炼知识
5. STEP 4: 创建/更新 skill
6. STEP 5: 子代理验证
7. STEP 6: 反思 + 归档
```

---

**🔒 本 skill 为强制拦截器，任何学习任务不得绕过！**
