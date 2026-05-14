---
name: generic-dev-workflow
description: "通用开发工作流 — 项目无关的轻量级开发实施流程。从需求理解到提交的 7 步标准循环。可被任何项目直接加载使用，与 sdd-workflow(Spec管理) 和 development-workflow-index(决策树) 互补。任何涉及开发/实现/编码/修复等任务时自动加载。"
version: 1.1.0
triggers:
  - 开发
  - 实现
  - 编码
  - 写代码
  - 修复
  - 开发流程
  - 通用开发
  - 开发步骤
  - feature
  - 功能实现
  - implement
  - coding
  - html对齐
  - 报告对齐
  - 文档对齐
author: Emma (小玛)
license: MIT
metadata:
  hermes:
    tags:
      - workflow
      - development
      - generic
      - step-by-step
    category: dogfood
    skill_type: workflow
    design_pattern: pipeline
depends_on:
  - test-driven-development
  - self-review
  - doc-alignment
  - commit-quality-check
  - unified-state-machine
  - project-state-machine
---

# 🛠️ 通用开发工作流 v1.0

> **定位**: 轻量、自包含、项目无关的开发实施流程。不绑定到任何特定项目。
> **与相关 skill 的关系**:
> - `development-workflow-index` → 决策树，告诉你选哪条路（调研/快速/标准/完整）
> - `sdd-workflow` → 管理 Spec 的生命周期（创建→审批→归档）
> - **本 skill → 实际的开发实施步骤（怎么把代码写出来）**

---

## 〇、什么时候加载此 skill？

当主人说以下内容时，**必须**加载此 skill：

| 触发词 | 示例 |
|:-------|:------|
| 开发/实现 | 「实现这个功能」「开发 XX 模块」 |
| 编码/写代码 | 「帮我写这个代码」「开始编码」 |
| 修复 | 「修一下这个 Bug」 |
| 功能 | 「加个新功能」「做 feature X」 |

**加载后，按以下 7 步流程执行，不可跳过顺序。**

---

## 📋 7 步开发流程

```text
[1] 需求确认 ─→ [2] 环境检查 ─→ [3] 实施计划 ─→ [4] TDD实现 ─→ [5] 验证 ─→ [6] 自检 ─→ [7] 提交
  理解需求    Reality Check    writing-plans   RED-GREEN   全量测试    self-review  git commit
                                                                                +
                                                                          doc-alignment
```

### Step 1: 需求确认

**做什么**: 确认要改什么、不改什么、做到什么程度算完成。

```text
问题模板:
  1. 要改哪个文件/模块？
  2. 预期行为是什么？
  3. 验收标准是什么？（可测试的条件）
  4. 不做的范围？（防止 scope creep）
```

**产出**: 一句话需求描述 + 验收标准清单
**耗时**: ~2 分钟

---

### Step 2: 环境检查（Reality Check）

**做什么**: 验证代码库的实际状态，不盲信文档。

```bash
# 2.1 最近变更
git log --oneline -10

# 2.2 是否有未提交的修改
git status --short

# 2.3 测试基线
python -m pytest --collect-only -q 2>/dev/null | tail -1
# 或: python -m pytest tests/ -q --tb=short -o "addopts=" 2>&1 | tail -3

# 2.4 版本号
python -c "from pkg import __version__; print(__version__)" 2>/dev/null
```

**产出**: 基线记录（测试数、版本号、未提交变更）
**耗时**: ~1 分钟

---

### Step 3: 实施计划（writing-plans）

**做什么**: 将功能拆解为 2-5 分钟的原子任务。每个任务包含：
- 确切的文件路径
- 确切的代码改动
- 验证命令

```text
Task N: {标题}
  文件: {确切的路径}
  操作: {具体改什么}
  验证: {验证命令}
```

**规则**:
- 🚫 每个任务 ≤ 5 分钟
- 🚫 每个 Task 有对应的测试 Task（TDD）
- 🚫 如果 Task 需要「实现时再做决定」→ 太模糊，退回

**产出**: `todo` 清单或实施计划文件
**耗时**: ~3-5 分钟

---

### Step 4: TDD 实现（RED-GREEN-REFACTOR）

**做什么**: 逐个 Task 实现。每个功能 Task 前必须有对应的测试 Task。

```text
[RED]   写一个会失败的测试 → 确认测试确实失败
[GREEN] 写最少代码让测试通过 → 确认测试通过
[REFACTOR] 重构代码 → 确认测试仍然通过
```

**强制前序**: 必须先执行 `test-driven-development` skill

```bash
# 加载 TDD skill
skill_view(name="test-driven-development")
```

**规则**:
- 🔴 没有失败的测试就不准写代码
- 🔴 代码写好了没测试 → 删掉重写
- 🔴 每个 Task 完成后 git commit（原子提交）

---

### Step 5: 全量验证

**做什么**: 运行所有测试，确保不破坏已有功能。

```bash
# 5.1 运行全量测试
python -m pytest tests/ -q --tb=short -o "addopts="

# 5.2 与基线对比（测试数不应低于基线）
# 5.3 如果有 lint: ruff check / flake8 等
```

**产出**: 测试报告（全部通过 / 失败详情）
**耗时**: ~2-5 分钟（取决于测试数量）

---

### Step 6: 自我审查（self-review）

**做什么**: 在向主人汇报前，自己先检查一遍。

加载 `self-review` skill，执行场景 F（任务交付验证）：

```text
[ ] 是否做了文档一致性检查？
[ ] 是否只改了该改的？（变更范围检查）
[ ] 是否有硬编码密码/token？（安全检查）
[ ] 每个 AC 是否实测确认过？
```

**产出**: 自我审查报告
**耗时**: ~2 分钟

---

### Step 7: 提交与对齐

**做什么**: 代码 + 文档 + HTML 报告同一次提交。

```bash
# 7.1 文档对齐（如果有 doc-alignment）
skill_view(name="doc-alignment")
# 执行 5 步对齐协议

# 7.2 🌐 HTML 报告对齐（如果项目有生命周期 HTML 报告）
#     检查 reports/lifecycle.html 或 PROJECT-PANORAMA.html
#     是否反映最新的文档状态（状态表、徽章、AC 进度）
#     如有 project-report.json → generate-project-report.py 自动同步
#     如手动维护 → grep/搜索 HTML 中的状态信息对比文档

# 7.3 提交前检查
skill_view(name="commit-quality-check")
# 执行安全检查 + 一致性检查

# 7.4 项目状态同步 (unified-state-machine skill)
```bash
cd /home/ubuntu/projects/hermes-cap-pack
python3 scripts/project-state.py sync
python3 scripts/project-state.py verify
```

# 7.5 Git 提交
git add -A
git commit -m "type(scope): description"
```

**产出**: git commit + 文档同步完成
**耗时**: ~2 分钟

---

## 🪤 常见陷阱

| 陷阱 | 场景 | 解决 |
|:-----|:------|:------|
| **CLI 脚本导入失败** | `ModuleNotFoundError: No module named 'scripts'` | CLI 入口和命令模块都需要加 `sys.path.insert(0, ...)` 指向项目根目录。详见 `references/python-cli-pitfalls.md` |
| **测试路径假设** | 测试从项目根运行没问题，但从子目录运行报错 | 所有路径用 `Path(__file__).resolve().parent` 构造，不用相对路径字符串 |
| **版本号不同步** | pyproject.toml 的 version 和 CHANGELOG 的版本不一致 | 提交前用 `grep "version"` 交叉检查，或用 `bump-version.py` 统一管理 |

---

## 🔴 铁律

| # | 铁律 | 违背后果 |
|:-:|:-----|:---------|
| 1 | **Step 1-7 顺序不可颠倒** | 跳过需求确认就写代码 = 返工 |
| 2 | **没有测试就不准写代码**（TDD） | 代码不可维护、回归风险 |
| 3 | **没有自检就不准汇报** | 主人发现遗漏→信任下降 |
| 4 | **代码改了文档必须同步** | 下次决策基于过时信息 |
| 5 | **每个原子 Task 独立 git commit** | 无法回滚、无法追溯 |
| 6 | **每次开发完成后同步 project-state.yaml** | 状态机与开发实际脱节 (unified-state-machine skill) |

---

## 🔗 与本 skill 链中其他 skill 的关系

```
主人说「开始开发」
    ↓
development-workflow-index  ← 决策树：选哪条路？
    ↓ 选择「标准路径」
sdd-workflow              ← Spec 门禁：有批准吗？
    ↓ 已批准
本 skill                  ← 通用开发工作流：7 步实施
    ↓ 完成
sdd-workflow              ← 更新 Spec 状态：complete → archive
    ↓
主人确认完成
```

---

## 🗂️ 文件结构

```
~/.hermes/skills/dogfood/generic-dev-workflow/
├── SKILL.md                         ← 主入口（7 步流程 + 铁律 + 陷阱）
└── references/
    ├── scenario-guide.md            ← 场景指南（新功能/修 Bug/重构/快速修复）
    └── python-cli-pitfalls.md       ← Python CLI 导入路径问题与解决
```

## 📚 参考深度阅读

- **`references/scenario-guide.md`** — 4 种常见开发场景的完整走法（新功能/修 Bug/重构/快速修复）

## 🚀 使用示例

### 场景：实现 SRA 的批量推荐接口

```text
Step 1: 「主人，要改的是什么？验收标准是什么？」
Step 2: git log + pytest --collect-only + 版本检查
Step 3: Task 1: 写 test_batch_recommend → 验证: pytest -k batch
         Task 2: 实现 recommend_batch() → 验证: pytest -k batch
         Task 3: 集成到 daemon.py 端点 → 验证: curl POST /recommend/batch
Step 4: RED→GREEN→REFACTOR 每个 Task
Step 5: pytest tests/ -q → 确认全绿
Step 6: self-review 场景 F
Step 7: doc-alignment + commit-quality-check → git commit
```
