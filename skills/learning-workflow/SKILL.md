---
name: learning-workflow
description: "所有学习/研究任务的强制流程拦截器。通过状态机+文件标志物实现防跳过机制。v5.0 重大更新：循环真正落地——learning-state.py 新增 regress/reject/loop-status 命令，reflection-gate.py 实现 R1/R2/R3/Quality Gate 自动化检查，子代理裁判打破自评自判。"
version: 5.5.0
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
  - 失败分析
  - 根因分析
  - ci 失败
  - 故障分析
  - 复盘
depends_on:
  - skill-creator
  - web-access
  - learning
  - learning-review-cycle
design_pattern: Pipeline
skill_type: Workflow
---

# 🧠 Learning Workflow · 强制学习流程 v5.0

> **铁律**：任何学习任务（用户说"学习/研究/了解XXX"）必须严格走此流程。
> **v5.0 重大更新**：循环真正落地 — 状态机三剑客 (regress/reject/loop-status) + 反射门禁 (reflection-gate.py R1/R2/R3/QG) + 子代理裁判
>
> **依赖脚本**：\n> - `scripts/learning-state.py` — 状态机管理（init/complete/reject/regress/loop-status/check/reset）\n> - `scripts/reflection-gate.py` — 反射门禁自动化评分（r1/r2/r3/quality）+ MIN_LOOPS 最小循环检查 + 递进等级惩罚\n>\n> **参考文件**：\n> - `references/cycle-troubleshooting.md` — 循环故障五层诊断指南（当门禁不触发时排查用）
- `references/knowledge-base-patterns.md` — Hermes 知识库构建模式参考（Karpathy LLM Wiki + GBrain）\n> - `references/karpathy-bounded-autonomy.md` — Karpathy 约束理论在学习流程中的应用（v5.1）\n> - `references/engineering-foundation-charter.md` — 工程化基础建设工作流—先分析建规约，再学习建规范，后开发（EFC 双阶段）\n> - `references/experience-format.md` — 经验积累系统格式指南与提取流程（v5.2）

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

## 🔄 三层迭代循环架构 (v4.0 核心创新)

**基于主人洞察 + Self-RAG (2023) + Spiral Learning (Bruner 1960) 的螺旋式学习设计：**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Iterative Learning Workflow v4.0                 │
├─────────────────────────────────────────────────────────────────────┤
│  Level 1: 子主题递归循环                                             │
│  ├─ 复杂主题拆分为多个子主题                                          │
│  ├─ 每个子主题独立学习                                                │
│  ├─ 子主题可再拆分（递归，最多 3 层）                                  │
│  └─ 合并结果后继续                                                    │
├─────────────────────────────────────────────────────────────────────┤
│  Level 2: 中间反思循环（主人建议的核心改进）                          │
│  ├─ R1: 搜索质量反思 → 可回到 STEP 0 细化拆分                        │
│  ├─ R2: 理解深度反思 → 可回到 STEP 1 针对性搜索                      │
│  ├─ R3: 提炼完整性反思 → 可回到 STEP 2 重新阅读                      │
│  └─ 每个检查点有明确的通过/失败标准                                    │
├─────────────────────────────────────────────────────────────────────┤
│  Level 3: 质量门禁循环（v3.1 已实现）                                 │
│  ├─ STEP 5.5 深度循环门禁                                            │
│  ├─ 学习质量评分 < 60 → 回到 STEP 0/1/2/3/4                          │
│  └─ 最多 3 次循环                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**核心洞察（来自主人）**：
- 当前流程只在 STEP 5 后才循环，浪费了中间的反思机会
- 应该让 STEP 0→1→2→3 之间就可以循环，类似螺旋式学习
- 每次循环理解更深一层，而不是一次性线性流程

**迭代流程示意**：

```
STEP 0(分析) → STEP 1(搜索) → [R1反思] → 
├─ R1通过 → STEP 2(学习) → [R2反思] →
│   ├─ R2通过 → STEP 3(提炼) → [R3反思] →
│   │   ├─ R3通过 → STEP 4→5→QG→6
│   │   └─ R3失败 → 回到 STEP 2 (Loop N+1)
│   └─ R2失败 → 回到 STEP 1 (Loop N+1)
└─ R1失败 → 回到 STEP 0 (细化拆分) → STEP 1 (Loop N+1)
```

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

### v5.0 新命令 — 循环控制三剑客

| 命令 | 作用 | 示例 |
|:---|:---|:---|
| `learning-state.py regress <step> [task_id]` | 🔙 回退到指定步骤（重置后续所有步骤为 pending） | `regress step1_search "my_task"` |
| `learning-state.py reject <step> <reason> [task_id]` | 🔴 标记步骤为"需重做"，记录原因到 refusal_log | `reject step1_search "缺少官方来源"` |
| `learning-state.py loop-status [task_id]` | 🔄 显示 L2/L3 循环次数 + 拒绝记录 + 步骤状态 | `loop-status "my_task"` |

**循环上限**：
- L2 中间反思（R1/R2/R3）：各 **2** 次
- L3 质量门禁（QG）：**3** 次
- 超过上限时自动拦截，引导用户手动评估

### v5.1 新增 — 最小循环次数 + 递进循环设计（基于 Karpathy 约束理论）

> **核心变化**：循环不能"一轮游"。即使第 1 轮得分够高，也必须进入第 2 轮深度验证。

**最小循环次数**：
- L2 中间反思（R1/R2/R3）：最少 **1 次**（= 必须进入第 2 轮）
- L3 质量门禁（QG）：最少 **1 次**（= 必须进入第 2 轮）
- 第 1 轮强制通过但标记"进入第 2 轮" → 第 2 轮才真正计为"通过"

**递进循环等级**：

| 循环次数 | 等级名称 | 评分标准 | 通过门槛 |
|:---:|:---|:---:|:---:|
| 第 1 次 | 🌐 **广度扫描** | 正常评分 | raw ≥ 60 |
| 第 2 次 | 🔍 **深度挖掘** | 标准严格 10 分 | effective ≥ 60（需 raw ≥ 70） |
| 第 3 次 | ✨ **精炼优化** | 标准严格 20 分 | effective ≥ 60（需 raw ≥ 80） |

**为什么需要递进？**
- 第 1 轮广度扫描：容易达标但只覆盖表面，目的是**识别所有候选**
- 第 2 轮深度挖掘：强制交叉验证和深入分析，保证**信息质量和可靠性**
- 第 3 轮精炼优化：按需执行，用于**打磨细节和查漏补缺**

**代码实现**：`reflection-gate.py` 中的 `MIN_L2_LOOPS`、`MIN_L3_LOOPS`、`PROGRESSIVE_LEVELS`

### v5.0 反射门禁系统

在每个检查点（R1/R2/R3/QG），使用 `reflection-gate.py` 进行自动化评分：

```bash
# 搜索质量检查（STEP 1 后）
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py r1 <task_id>

# 理解深度检查（STEP 2 后）
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py r2 <task_id>

# 提炼完整性检查（STEP 3 后）
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py r3 <task_id>

# 质量门禁（STEP 5 后）
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py quality <task_id>
```

**输出格式**（JSON）：
```json
{"gate": "r1", "passed": true, "score": 85,
 "failures": [{"check": "覆盖度", "detail": "...", "severity": "medium"}],
 "recommendation": "通过，进入 STEP 2",
 "loop": {"current": 1, "max": 2, "min": 1, "level": 2, "level_name": "深度挖掘"}}
```

**判定逻辑**：
| score | 结果 | 操作 |
|:-----:|:----:|:----|
| ≥ 80 | ✅ 优质通过 | 直接进入下一步 |
| 60-79 | ⚠️ 边界通过 | 进入下一步 + 标记待改进 |
| 40-59 | 🔴 拦截 + 子代理裁判 | 子代理评估后决定回退或放行 |
| < 40 | 🛑 强制拦截 | 自动 `regress` 回退 |

**循环递进判定（v5.1 新增）**：
- 除了原始 score，`reflection-gate.py` 还应用了**递进等级惩罚**（level_penalty）
- `effective_score = raw_score + level_penalty`（惩罚为负数）
- 同时强制检查 **MIN_LOOPS** — 未达到最小循环次数时 passed=false
- `loop` 字段新增 `min`、`level`、`level_name` 标识当前递进阶段

---

## 三、各步骤详细指令

### STEP 0: 📐 知识图谱分析（v4.0 增强）

1. **分析主题复杂度**：是简单主题还是复杂主题？
2. **决定学习模式**：快速模式还是深度模式？
3. **如果是复杂主题** → 拆分为原子子主题（支持递归）
4. 输出到 `knowledge_map.md`

**知识图谱模板：**
```markdown
# 知识图谱：{主题}
## 复杂度评估：{简单/中等/复杂}
## 推荐模式：{快速/深度}
## 子主题拆分（如适用）：
1. {子主题1} — 递归深度: 0
2. {子主题2} — 递归深度: 0
## 预期输出：{已有 skill 更新 / 新 skill / 笔记}
## 循环次数限制：{max_loops=3}
```

**递归深度限制**（v4.0 新增）：
- 子主题可再拆分为子子主题（最多 3 层）
- 复杂主题：子主题 → 子子主题 → 子子子主题
- 超过限制时自动停止并报告用户

**进度汇报**：`learning-state.py complete step0_map`

---

### STEP 1: 🔍 联网搜索（必须执行）

1. 加载 `web-access` skill
2. 使用 `web_search`（Hermes 原生，优先）或 `mcp_tavily_tavily_search` 搜索 3-5 个高质量来源
3. 使用 `web_extract`（原生）或 `mcp_tavily_tavily_extract` 提取内容；需 JS 渲染时用 `browser_navigate` + `browser_console`
4. **必须**将搜索结果原文摘要写入 `~/.hermes/learning/raw_search_results.md`
5. **进度汇报**：`learning-state.py complete step1_search`

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

### R1: 🔍 搜索质量反思 (RETRIEVE_CHECK) — v4.0 新增

**位置**：STEP 1 搜索后、STEP 2 阅读前

**检查标准**：

| 检查项 | 通过标准 | 失败处理 |
|--------|---------|---------|
| 数量 | ≥ 3 个来源 | 回到 STEP 0，细化搜索关键词 |
| 权威性 | ≥ 1 个官方来源 | 回到 STEP 1，指定官方来源搜索 |
| 覆盖度 | 覆盖主题各个方面 | 回到 STEP 0，拆分子主题 |
| 时效性 | 信息发布日期 < 12 个月 | 回到 STEP 1，添加版本号搜索 |

**反思问题**：
- 搜索结果是否覆盖了主题的各个方面？
- 来源权威性是否达标？
- 是否有官方文档或权威教程？

**执行方式（v5.0 自动化）**：

**Step 1 — 自动门禁**（每次必做）：
```bash
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py r1 <task_id>
```
- **exit code = 0** (score ≥ 60) → 通过，进入 STEP 2
- **exit code = 1** (score < 60) → 🛑 拦截！自动执行：
  ```bash
  # 自动回退到 STEP 0 或 STEP 1（根据失败类型）
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py regress step0_map <task_id>
  # 或
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py regress step1_search <task_id>
  ```
- 循环次数自动递增，可通过 `loop-status` 查看

**Step 2 — 子代理裁判**（当 score 在 40-70 之间时触发）：
用 delegate_task 启动独立子代理作为第三方裁判：

```python
delegate_task(
    goal="以严格的质量检查员身份，评估学习任务的搜索质量",
    context=f"引用文件：~/.hermes/learning/raw_search_results.md\n"
            f"知识图谱：~/.hermes/learning/knowledge_map.md\n"
            f"reflection-gate.py 给分：{score}/100\n"
            f"请给出：1) 具体改进建议 2) pass/fail 判断 3) 改进优先级",
    toolsets=['terminal', 'file']
)
```
- 子代理判 **fail** → 执行 regress 回退
- 子代理判 **pass** → 进入 STEP 2（即使自动门禁是 40-70 的边界分）

---

### STEP 2: 📖 深度阅读（快速模式跳过）

1. 使用 `web_extract`（Hermes 原生，优先）或 `mcp_tavily_tavily_extract` / `mcp_tavily_tavily_crawl` 提取正文
2. **必须**将阅读笔记写入 `~/.hermes/learning/reading_notes.md`
3. 笔记格式（两种方式均可，**关键：每个观点都必须绑定来源**）：

   **方式 A — 按来源组织：**
   ```markdown
   ## 来源: {URL}
   ### 核心观点
   - {观点1} [来源: {URL}]
   - {观点2}
   ### 可操作建议
   - {建议}
   ```

   **方式 B — 按主题组织（推荐，便于理解）：**
   ```markdown
   ## {主题标题}
   ### 核心概念
   - {概念} [来源: {URL}]
   - {概念} [来源: {URL}]
   ### 关键洞察
   - {洞察} [来源: {URL}，{URL}—交叉验证]
   
   ## 交叉验证
   | 概念 | 来源 1 | 来源 2 | 来源 3 | 一致？ |
   |------|--------|--------|--------|:------:|
   | {概念} | {URL} ✅ | {URL} ✅ | {URL} ✅ | ✅ |
   ```

   > ⚠️ **R2 门禁关键点**：整理笔记时，**每个观点必须绑定来源 URL**。不要只写概念不写来源。交叉验证表格能显著提升 R2 评分。

4. **进度汇报**：`learning-state.py complete step2_read`

**快速模式跳过**：直接标记为 skipped 并记录原因

---

### R2: 📖 理解深度反思 (COMPREHEND_CHECK) — v4.0 新增

**位置**：STEP 2 阅读后、STEP 3 提炼前

**检查标准**：

| 检查项 | 通过标准 | 失败处理 |
|--------|---------|---------|
| 核心概念 | 能用自己的话解释 | 回到 STEP 1，搜索补充资料 |
| 可操作性 | 能写出操作步骤 | 回到 STEP 2，重读实践部分 |
| 完整性 | 无明显知识缺口 | 回到 STEP 1，针对性搜索缺口 |
| 交叉验证 | ≥ 2 个来源佐证 | 回到 STEP 1，搜索更多来源 |

**反思问题**：
- 是否真正理解了核心概念？
- 还是只是复制粘贴？
- 能否用自己的话解释给他人？

**执行方式（v5.0 自动化）**：

**Step 1 — 自动门禁**：
```bash
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py r2 <task_id>
```
- score ≥ 60 → 进入 STEP 3
- score < 60 → 🛑 `learning-state.py regress step1_search` 或 `step2_read`

**Step 2 — 子代理裁判**（score 40-70 时触发）：
子代理评估 reading_notes.md 的理解深度，判 fail 则回退。

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

### R3: 🧪 提炼完整性反思 (EXTRACT_CHECK) — v4.0 新增

**位置**：STEP 3 提炼后、STEP 4 脚手架前

**检查标准**：

| 检查项 | 通过标准 | 失败处理 |
|--------|---------|---------|
| 结构 | 有核心概念/步骤/避坑指南 | 回到 STEP 2，重读结构部分 |
| 可操作性 | 能指导实际操作 | 回到 STEP 2，重读实践部分 |
| 完整性 | 无明显遗漏 | 回到 STEP 2，补充阅读 |
| 格式 | 符合 skill 模板 | 回到 STEP 3，重新提炼 |

**反思问题**：
- 提炼的知识是否可操作？
- 能否指导实际操作？
- 结构是否完整？

**执行方式（v5.0 自动化）**：

**Step 1 — 自动门禁**：
```bash
python3 ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py r3 <task_id>
```
- score ≥ 60 → 进入 STEP 4
- score < 60 → 🛑 `learning-state.py regress step2_read` 或 `step3_extract`

**Step 2 — 子代理裁判**（score 40-70 时触发）：
子代理评估 extracted_knowledge.md 的完整性，判 fail 则回退。

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

**反思检查点 (Reflection Tokens)**：（类比 Self-RAG 2023，v4.0 增强）

| 检查点 | 位置 | 反思问题 | 循环入口 |
|--------|------|----------|----------|
| **R1** RETRIEVE_CHECK | STEP 1 后 | 搜索结果是否覆盖了主题的各个方面？来源权威性是否达标？ | 回到 STEP 0 细化拆分 |
| **R2** COMPREHEND_CHECK | STEP 2 后 | 是否真正理解了核心概念？还是只是复制粘贴？ | 回到 STEP 1 针对性搜索 |
| **R3** EXTRACT_CHECK | STEP 3 后 | 提炼的知识是否可操作？能否指导实际操作？ | 回到 STEP 2 重新阅读 |
| SKILL_CHECK | STEP 4 后 | Skill 的结构是否完整？是否有避坑指南和示例？ | 回到 STEP 4 重新设计 |
| VALIDATE_CHECK | STEP 5 后 | 验证是否充分？是否覆盖了正常流和异常流？ | 回到 STEP 0-4 (质量门禁) |

**循环次数限制**：
- L2 中间反思：R1/R2/R3 **最少 1 次**，最多 2 次
- L3 质量门禁：**最少 1 次**，最多 3 次循环
- 递进节奏：第 1 轮广度扫描(合格线60) → 第 2 轮深度挖掘(合格线70) → 第 3 轮精炼优化(合格线80)
- 未达到最小循环次数时，即使分数 ≥ 60 也会被拦截进入下一轮
- 超过最大限制则报告用户请求协助

### STEP 6: 📝 反思迭代（v3.1 增强）

**每次学习/研究任务完成后执行：**

1. 运行 `learning-state.py list` 查看任务概览
2. **搜索策略反思**：本次搜索效果如何？记录可复用的技巧
3. **更新 learning skill**：将本次积累的方法论改进写入 learning skill
4. **🗂️ 经验提取**（v5.2 新增）：检查是否有可复用的经验，按标准格式写入 `~/.hermes/experiences/active/`
   - 判断标准：发现可复用的方法/解决了卡住的问题/验证了假设
   - 格式：YAML frontmatter + 结构化 body
   - 分类：experience（动作级）/ skill（任务级）/ rule（原则级）
   - 评分：reusability (high/medium/low) + confidence (1-5)
   - 若 reusability=high → 自动更新对应 skill 的 references/
   - 更新 `~/.hermes/experiences/index.md` 目录
   - 详见 learning skill Stage 6 Step 9

5. **🧬 L3 Brain 沉淀**（v5.4 新增）：检查本次学习是否产生了**可提炼为核心概念/实体/摘要/分析**的知识。
   - 如果学习产出了一个**通用模式/方法论/原则** → 创建/更新 `brain/wiki/concepts/{name}.md`
   - 如果学习中出现了**重要人物/工具/项目** → 创建/更新 `brain/wiki/entities/{name}.md`
   - 如果学习来源于**某篇文档/论文** → 创建/更新 `brain/wiki/summaries/{name}.md`
   - 如果学习产出了**对比分析/推演结论** → 创建/更新 `brain/wiki/analyses/{name}.md`
   - 使用 `[[页面名称]]` 建立交叉引用
   - 更新 `~/.hermes/brain/index.md` 索引
   - 追加 `~/.hermes/brain/log.md` 日志条目
   - 检查并更新 `~/.hermes/KNOWLEDGE_INDEX.md`（如涉及新主题）

6. **🔗 自动 Skill 关联**（v5.3 新增）：如果本次学习创建了新 skill，自动扫描所有已有 skill 并建立关联关系
   ```bash
   # 自动执行关联
   if [ -n "$NEW_SKILL_NAME" ]; then
       echo "🔗 自动关联 skill: $NEW_SKILL_NAME"
       python3 ~/.hermes/scripts/skill-auto-link.py auto-link "$NEW_SKILL_NAME"
   fi
   ```

7. **🤖 自动知识沉淀**（v5.5 新增 — 自动化增强）：使用 `knowledge-ingest.py` 将本次学习的经验自动写入 L2/L3
   ```bash
   # 自动检测本次学习是否产生了可沉淀的知识
   python3 ~/.hermes/scripts/knowledge-ingest.py --auto-detect
   ```
   相比第 4、5 步的手动方式，此步骤自动完成：文件创建 + 索引更新 + 交叉引用维护。

8. **🏁 归档任务**：`learning-state.py reset [task_id]`

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
4. **🗂️ 经验提取归档**（v5.2 新增）
   - 按 STEP 6 第 4 步的标准，将本次学习产生的可复用经验写入 `~/.hermes/experiences/active/`
   - 更新 `~/.hermes/experiences/index.md`
5. **🧬 L3 Brain 沉淀**（v5.4 新增）
   - 按 STEP 6 第 5 步的标准，将本次学习产生的核心知识沉淀到 `~/.hermes/brain/wiki/`
   - 更新 `~/.hermes/brain/index.md` + 追加 `log.md`
   - 更新 `~/.hermes/KNOWLEDGE_INDEX.md`（如涉及新主题）
6. 执行**学习反思**（STEP 6）
7. **归档状态**：`learning-state.py reset [task_id]`
8. **🏁 判断是否走三阶段行动**（v5.5 新增）
   - 检查学习产出是否涉及系统改进（见 第十一章）
   - 如果是 → 进入 Phase 2: 建立基础设施
   - 如果不是 → 正常归档：`learning-state.py reset [task_id]`
9. 询问是否将本次流程经验**沉淀为永久 skill**

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

### 8.5 防无限循环 + 防一轮游（v4.0 增强 / v5.1 补完）

**三层循环各自的限制**：

| 循环层 | 最小次数 | 最大次数 | 超过上限处理 |
|--------|:-------:|:-------:|-------------|
| L1 子主题递归 | 0（可选） | 3 层深度 | 报告用户，不再拆分 |
| L2 中间反思 | **1**（v5.1 新增） | 每检查点 2 次 | 自动进入下一层循环 |
| L3 质量门禁 | **1**（v5.1 新增） | 3 次 | 报告用户，请求协助 |

**递进节奏**（Karpathy Bounded Autonomy 模式）：
- 第 1 轮（广度扫描）：全面覆盖，但**不通过**——强制进入第 2 轮
- 第 2 轮（深度挖掘）：深入验证，合格线提升 10 分
- 第 3 轮（精炼优化）：精雕细琢，合格线提升 20 分
- 每轮都比上一轮更深、更严格

**防循环叠加**：
- 自动触发的学习任务**禁止再次触发自动学习**
- 每次循环前检查 `loop_count`
- 超过限制时自动停止并报告用户
- 不同检查点的循环次数独立计算（R1/R2/R3 各有 2 次）

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

---

## 十、子主题递归学习 (v4.0 新增)

### 适用场景判断

| 场景 | 是否适用 | 示例 |
|------|---------|------|
| 复杂主题（≥ 3 个子主题） | ✅ 适用 | "学习 Hermes Agent" → 拆分为架构/工具/流程 |
| 简单主题（1-2 个子主题） | ❌ 不适用 | "查一下 Python 3.13 新特性" |
| R1 失败后发现主题太大 | ✅ 适用 | 搜索后发现主题涵盖太多内容 |

### 递归流程示意

```
STEP 0: 分析主题 → 拆分为 3-5 个子主题
    ↓
[子主题 1] STEP 1→R1→2→R2→3→R3 → 完成 ✓
    ↓
[子主题 2] STEP 1→R1 → R1 失败 ✗
    ↓
[回到 STEP 0] 细化子主题 2 → 拆分为 2-1 和 2-2（递归深度 +1）
    ↓
[子主题 2-1] STEP 1→R1→2→R2→3→R3 → 完成 ✓
[子主题 2-2] STEP 1→R1→2→R2→3→R3 → 完成 ✓
    ↓
合并子主题 2 的结果 → 继续
    ↓
[子主题 3] STEP 1→R1→2→R2→3→R3 → 完成 ✓
    ↓
合并所有子主题结果 → STEP 4→5→QG→6
```

### 递归深度限制

- **最大递归深度**：3 层（子主题 → 子子主题 → 子子子主题）
- **超过限制**：停止拆分，报告用户"主题过于复杂，建议分多次学习"

### 合并机制

合并子主题结果时：
1. 按子主题顺序合并 `extracted_knowledge.md`
2. 统一格式（核心概念、操作步骤、避坑指南）
3. 去重（避免重复内容）
4. 输出到 `~/.hermes/learning/merged_knowledge.md`

---

## 十一、🌀 从学习到行动：三阶段工程化方法论 (v5.5 新增)

> **核心理念**: 学习不是终点，行动才是。从「知道」到「做到」需要一座桥。
> **来源**: SRA 项目测试基建重构 + SDD 工作流创建实战 (2026-05-11)
> **参考**: `references/engineering-foundation-charter.md` (EFC 双阶段流程)
> **主人偏好**: 「不只是建立思想，更要建立可用的工作流」——产出脚本/门禁/skill，而非只是概念。

### 11.1 什么时候需要走三阶段？

当学习产出的方案涉及**系统层面的改进**（不是单点修复）时，必须走三阶段：

| 判断标准 | 单点修复 | 系统改进 |
|:---------|:---------|:---------|
| 问题范围 | 一个文件/一个函数 | 跨文件/跨模块 |
| 修复方式 | 直接改代码 | 先建基础设施再改代码 |
| 复发风险 | 高（同类问题还会出现） | 低（门禁机制阻止复发） |
| 示例 | 改一个函数名 | 建立测试数据契约 + 门禁 |

### 11.2 三阶段流程

```
[学习完成] ← 走 STEP 0-6
    ↓
Phase 1: 深度循环学习（已完成）
    STEP 0→1→2→3→4→5→QG→6
    产出: knowledge_map + extracted_knowledge + skill
    ↓ —— 系统改进？→ 否 → 直接修
    ↓ 是
Phase 2: 建立基础设施
    ① 文件层: 模板/宣言/检查脚本
    ② 规则层: AGENTS.md / 铁律
    ③ 门禁层: 可自动执行的脚本（exit code）
    验证: 每个基础设施单独测试通过
    ↓ —— 就绪？→ 否 → 回到 Phase 2
    ↓ 是
Phase 3: 用新系统解决原始问题
    ① 旧问题自然被新系统覆盖
    ② 验证新系统能拦截同类问题
    ③ 输出经验沉淀到 L2/L3
```

### 11.3 三阶段门禁

**Phase 1 → 2 门禁**：
```
- [ ] 方案是否涉及系统改进？
  否 → 直接修；是 → 走 Phase 2/3
- [ ] 是否识别出了「机械门禁」机会？
  哪些规则可以写成脚本/grep/exit code？
  如果全部只能靠自觉 → 工程化不够
```

**Phase 2 → 3 门禁**：
```
- [ ] 基础设施可独立运行？
  脚本可直接 python3 xxx.py 执行？exit code 反映 pass/fail？
- [ ] 原问题的根因被门禁覆盖？
  同样错误再犯一次，门禁能拦住？
```

### 11.4 主人偏好提醒

> 学习完成后，优先问自己：
> 1. 能不能产出一个**可执行的脚本**？
> 2. 能不能产出一个**机械门禁**（grep/exit code）？
> 3. 能不能**更新一个 skill** 让下次更快？
>
> 如果都不能 → 学习成果还不够工程化，回到 STEP 3 重新提炼。

## 🔒 本 skill 为强制拦截器，任何学习任务不得绕过！
