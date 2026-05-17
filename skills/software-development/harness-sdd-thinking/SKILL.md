---
name: harness-sdd-thinking
description: "Harness 约束思维 + SDD 全栈开发实践。源自得物技术的最佳实践：给 AI 精确的参考对象而非空白画布，通过约束思维、多仓工作区、多 Agent 协作提升 AI 代码质量。适用于任何需要委托编码任务的场景 (OpenCode/Claude Code/Codex)。"
version: 1.0.0
triggers:
  - harness
  - 约束思维
  - 约束编程
  - ai 编码约束
  - ai constrained coding
  - 给 ai 参考
  - ai reference
  - 多 agent 协作
  - 全栈开发
  - 前后端并行
  - 多仓开发
  - 代码生成 prompt
  - 得物实践
  - sdd 模板
  - ai coding prompt pattern
author: boku (Emma) — 基于得物技术文章提炼
license: MIT
metadata:
  hermes:
    tags:
      - Harness
      - SDD
      - Prompt-Engineering
      - Multi-Agent
      - Full-Stack
      - Best-Practice
    category: software-development
    skill_type: workflow
    design_pattern: pipeline
    related_skills:
      - sdd-workflow
      - generic-dev-workflow
      - opencode-dev-workflow
      - writing-plans
      - subagent-driven-development
depends_on: []

---

# Harness + SDD 约束思维实践

> **核心哲学：不要让 AI 从空白画布开始创造——给它精确的参考对象。**
> 源自得物技术《基于 Harness + SDD + 多仓管理模式的 AI 全栈开发实践》

---

## 一、什么时候用这个 Skill？

| 场景 | 推荐 |
|:-----|:----:|
| 委托 OpenCode 实现新功能 | ✅ **必用** |
| 写 coding prompt 给 AI Agent | ✅ **必用** |
| 创建 SDD Story 后的实施阶段 | ✅ **推荐** |
| 跨前后端全栈开发 | ✅ **推荐** |
| 简单的单文件 Bug 修复 | ❌ 不需要 |

---

## 二、Harness 约束思维 — 核心法则

### 2.1 四个步骤

```
[找参考] 在代码库中找功能最相似的已有实现
   ↓
[优先复用] 直接复用组件、API 封装、数据结构
   ↓
[模仿复制] "复制+调整"优于从零创造新风格
   ↓
[约束范围] 在 Prompt 中指定确切的参考文件和接口
```

### 2.2 错误 vs 正确示例

```text
// ❌ 错误：从零创造
请实现一个结束语管理的 CRUD 接口

// ✅ 正确：Harness 约束
请参照现有"场景欢迎语"功能来实现"结束语"功能：
- 后端参考接口：/api/v1/feature/list
- 前端参考入口：FeatureTable/index.tsx:53-58
- 数据结构、分层方式、命名风格保持一致
- 新增场景 code：categoryCode = "SCENARIO_CLOSING"
```

### 2.3 Hermes + OpenCode 中的实践

```bash
# 1. Hermes 分析需求时，先找参考实现
# 2. 在委托给 OpenCode 时，把参考文件路径注入 prompt

opencode run \
  '请参照现有实现来实现新功能。
  
  参考文件：
  - src/features/greeting/service.ts （完整实现参考）
  - src/features/greeting/types.ts （类型定义参考）
  
  新功能要求：
  - 功能名称：结束语管理
  - 新增字段：categoryCode = "SCENARIO_CLOSING"
  - 数据结构、API 风格、命名规范与参考实现保持一致
  实现完成后运行 npm test 确认通过。' \
  --thinking --dir ~/projects/myapp
```

---

## 三、全栈 SDD Prompt 模板

### 3.1 标准模板

```
这是一个前后端全栈开发工作区，需要你设计技术接口方案，同时开发前后端项目；
首先你需要 cd 到对应前后端应用目录中，创建 sdd 文件；
所以你需要生成两份 sdd 文档，之后我会启动两个 agent 分别实现；
在生成之前，如果你需要确认某些细节，你应当先确认后生成 sdd 文档。

📂 前端应用：{frontend_app}/sdd-propose feature/{feature_name}
📂 前端入口参考：{frontend_entry_files}
📂 后端应用：{backend_app}/sdd-propose feature/{feature_name}
📂 后端接口参考：{backend_api_ref}
📋 需求内容：
{requirements_attachment}
```

### 3.2 Hermes 适配版本（单项目 + OpenCode）

```
这是一个开发任务。你需要实现以下功能：

📋 需求：
{需求描述}

📂 项目路径：{project_path}

📂 参考实现：
{参考文件路径列表}

🎯 验收标准：
{验收标准列表}

请实现以上功能，完成后运行测试验证。
```

### 3.3 关键 Prompt 元素

| 元素 | 作用 | 示例 |
|:-----|:-----|:------|
| `cd to directory` | 防止文件放错位置 | `cd service-frontend` |
| 参考实现路径 | 约束 AI 风格 | `@FeatureTable/index.tsx:53-58` |
| 验收标准 | 定义完成条件 | `所有测试通过` |
| 约束条件 | 限定范围 | `不改动核心架构` |

---

## 四、多 Agent 并行分工范式

### 4.1 什么时候用多 Agent

前端和后端代码生成在 SDD 完成后是**独立**的，可以并行执行：
- SDD 文档定义好接口契约后
- 前端 Agent 和后端 Agent 可以同时工作
- 接口契约是桥梁（API 路径、请求/响应格式）

### 4.2 Hermes 多 Agent 配置

```python
# 使用 delegate_task 并行委托
delegate_task(tasks=[
    {
        "goal": "实现前端功能：...",
        "context": f"参考文件：xxx\n接口契约：{contract}",
        "toolsets": ["terminal", "file"],
    },
    {
        "goal": "实现后端功能：...",
        "context": f"参考文件：xxx\n接口契约：{contract}",
        "toolsets": ["terminal", "file"],
    },
])
```

### 4.3 OpenCode 多任务并行（同一项目内）

```bash
# 使用 git worktree 隔离
git worktree add -b feat/frontend /tmp/work-frontend main
git worktree add -b feat/backend /tmp/work-backend main

# 并行执行
opencode run '实现前端功能...' --dir /tmp/work-frontend --thinking &
opencode run '实现后端功能...' --dir /tmp/work-backend --thinking &
```

---

## 五、SDD 三命令工作流

### 5.1 极简命令模式

借鉴得物实践的 `openspec-propose/apply-change/archive-change`：

| 阶段 | 命令 | 对应 Hermes |
|:-----|:-----|:------------|
| **Think** 🤔 | 设计方案 | `spec-state.py research` + 创建 Spec |
| **Do** ⚡ | 执行变更 | OpenCode 实现 / delegate_task |
| **Close** ✅ | 归档完成 | `chain-state.py advance` + 文档对齐 |

### 5.2 思考阶段的 Prompt

```
在生成 SDD 文档之前，请先确认以下细节：
1. 前端需要新增/修改哪些文件？
2. 后端需要新增/修改哪些接口？
3. 接口的请求/响应格式是什么？
4. 有没有现成的参考实现可以复用？
如果你不确定，请先搜索代码库再回答。
```

---

## 六、结合现有工作流的整合示例

### 完整流程：需求 → SDD → Harness 约束 → OpenCode 实现

```bash
# Step 1: Hermes 分析需求，找参考实现
# （走 generic-dev-workflow Step 1-3）

# Step 2: 创建 SDD Story（已有 spec-state.py）

# Step 3: 编写 Harness 约束 Prompt
REFERENCE_FILES=(
  "src/features/greeting/service.ts"
  "src/features/greeting/types.ts"
)
ACCEPTANCE_CRITERIA=(
  "所有 CRUD 接口可用"
  "单元测试覆盖率 > 80%"
  "与参考实现风格一致"
)

# Step 4: 委托 OpenCode
opencode run \
  "请参照现有参考文件实现新功能。
  参考文件：$(printf '%s\n' "${REFERENCE_FILES[@]}")
  
  验收标准：
  $(printf '%s\n' "${ACCEPTANCE_CRITERIA[@]}")
  
  请实现完成后运行测试验证。" \
  --thinking --dir ~/projects/myapp

# Step 5: Hermes 审查 + 文档对齐
# （走 generic-dev-workflow Step 5-7）
```

---

## 七、Red Flags（常见陷阱）

| 陷阱 | 说明 | 避免方式 |
|:-----|:------|:---------|
| ❌ 给太多参考文件 | AI 会困惑于哪个才是主要参考 | 最多给 2-3 个核心参考 |
| ❌ 不给参考直接开干 | 产出"外星代码" | 始终先找参考实现 |
| ❌ 前后端契约未对齐就并行 | 联调时发现接口不匹配 | SDD 完成后再并行 |
| ❌ 一个 Agent 做所有事 | 上下文窗口爆炸 | 拆分为多个独立职责 |
| ❌ 忘记指定目录 | 文件创建在错误位置 | Prompt 开头加 `cd to directory` |
