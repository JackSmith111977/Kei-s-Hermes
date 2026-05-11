---
name: sprint-planning
description: 敏捷 Sprint 规划方法论 — 从项目现状分析到 Sprint Backlog 生成的完整流程。涵盖 Git 状态分析、测试健康检查、文档审计、代码质量扫描、技术债评估、Sprint Backlog 生成。任何涉及「分析项目现状」「制定开发计划」「规划下个 Sprint」等任务时自动加载。
version: 1.1.0
triggers:
  - 项目现状分析
  - 制定开发计划
  - 规划 Sprint
  - 下一个 Sprint
  - 敏捷开发计划
  - 迭代计划
  - sprint planning
  - 项目评估
  - 开发路线图
  - 迭代规划
  - 分析项目
  - 当前项目状态
  - 准备发布
  - 版本规划
author: Emma (小玛)
license: MIT
metadata:
  hermes:
    tags:
      - sprint
      - planning
      - agile
      - project-analysis
      - methodology
    category: dogfood
    skill_type: methodology
    design_pattern: workflow
depends_on:
  - analysis-workflow
  - deep-research
  - self-review
  - doc-alignment
  - commit-quality-check
  - development-workflow-index
---

# 🏃 Sprint Planning · 项目分析 → 敏捷计划流程

> **从「我们到哪了」到「完成交付」的完整方法论。**
> v1.1.0 — 新增 Phase 2: Sprint 执行（分支同步、版本管理、doc-alignment）

---

## 适用场景

| 用户说… | 触发路径 |
|:--------|:---------|
| 「分析一下 xxx 项目的现状」 | 全流程 |
| 「规划下个 Sprint」 | 全流程（假设已有分析） |
| 「我们的项目到哪了」 | Step 1-3（只分析，不规划） |
| 「帮我排一下优先级」 | Step 6-7（在已有 Backlog 上做） |

---

## 七步方法论

```text
┌──────────────────────────────────────────────────┐
│ Step 1: Git 状态分析  📊                          │
│   ├── 分支关系（merge-base, ahead/behind）        │
│   ├── 最近开发节奏（commit 频率、模式）            │
│   └── 未合并的分支 / PR                          │
│   输出: branch-status.md                          │
├──────────────────────────────────────────────────┤
│ Step 2: 测试健康检查  🧪                         │
│   ├── pytest 运行（全部通过？失败数？）           │
│   ├── 测试总览（文件数、用例数、覆盖模块）         │
│   └── 覆盖率分析 / 质量趋势                      │
│   输出: test-health.md                            │
├──────────────────────────────────────────────────┤
│ Step 3: 文档审计  📝                             │
│   ├── README / CHANGELOG / ROADMAP 一致性         │
│   ├── EPIC / Story / 设计文档 同步状态           │
│   ├── API 参考 / 架构文档 版本对齐               │
│   └── 文档漂移检测（代码改了文档没改）            │
│   输出: doc-audit.md                              │
├──────────────────────────────────────────────────┤
│ Step 4: 代码质量扫描  💻                         │
│   ├── 模块大小（行数、函数数）                    │
│   ├── TODO/FIXME/HACK 统计                       │
│   ├── 类型标注覆盖率                              │
│   ├── print/logging 混用                         │
│   ├── 裸 except / 魔法数字 / 死代码              │
│   └── 架构耦合度 / 单一职责评估                  │
│   输出: code-quality.md                           │
├──────────────────────────────────────────────────┤
│ Step 5: 技术债评估  🏚️                          │
│   ├── 加载已有的债务分析文档（如有）              │
│   ├── 对照上次评估看修复进展                      │
│   ├── 新增债务识别                                │
│   └── 按 P0/P1/P2 分类分级                       │
│   输出: tech-debt-status.md                       │
├──────────────────────────────────────────────────┤
│ Step 6: Sprint Backlog 生成  📋                  │
│   ├── 从 ROADMAP 中提取未完成的 Story            │
│   ├── 从 TechDebt 中提取高优修复项               │
│   ├── 合并为新 Story（带 Story ID/优先级/估时）  │
│   ├── 识别依赖关系（哪些 Story 阻塞其他）         │
│   └── 按 Sprint 容量打包                          │
│   输出: sprint-backlog.md | sprint-plan.md       │
├──────────────────────────────────────────────────┤
│ Step 7: 汇报与确认  📣                           │
│   ├── 状态总览 Dashboard（可视化表格）            │
│   ├── 已完成 vs 未完成对比图                     │
│   ├── 建议的 Sprint 目标 + 优先级排序            │
│   └── 询问主人确认方向                            │
│   输出: sprint-report                            │
└──────────────────────────────────────────────────┘
```

---

## 各步骤详细指令

### Step 1: Git 状态分析

**核心检查项：**

| 检查 | 命令 | 解读 |
|:-----|:-----|:-----|
| 当前分支 | `git branch` | 确认在正确分支上工作 |
| 分支关系 | `git merge-base A B` + `git rev-list --count A..B` | 谁领先谁？差距多大？ |
| 未提交修改 | `git status` | 工作区是否干净？ |
| 最近提交 | `git log --oneline -10` | 开发节奏、提交模式 |
| 未合并分支 | `git branch -a --merged` / `--no-merged` | 有多少分支该清理了？ |
| 标签 | `git tag --list \| sort -V` | 发布版本状态 |

**🔴 铁律：**
- 必须先做 `merge-base` 判断分支关系 — `ahead/behind` 数值容易误导
- 如果工作分支领先 master > 10 commits → 标记为「⚠️ 分支漂移风险」

**输出格式：**
```markdown
## Git 状态摘要
- **当前分支:** feat/v2.0-enforcement-layer
- **领先 master:** 33 commits
- **工作区:** 干净
- **最近 5 次提交:** feat(CONTRACT), fix(QUALITY), refactor(SPLIT), test(COVERAGE)
- **标签:** v1.1.0, v1.2.0, v1.2.1
- **分支状态:** ⚠️ 领先较多，建议合并后继续
```

---

### Step 2: 测试健康检查

**核心检查项：**

| 检查 | 命令 | 说明 |
|:-----|:-----|:-----|
| 测试通过 | `python3 -m pytest tests/ -q --tb=short` | 全部通过？ |
| 测试数量 | `python3 -m pytest tests/ --collect-only -q` | 总用例数 |
| 测试分布 | `wc -l tests/*.py \| sort -rn` | 各文件分布 |
| 模块覆盖 | 对比源文件数 vs 测试文件数 | 零测试模块识别 |

**🔴 铁律：**
- 不要只看「通过了」的数字 — 检查测试数量是否因改错而减少
- 如果测试从 290 降到 200 → 立即标记为 🔴 回归
- 如果某模块没有对应测试文件 → 标记为 🧪 测试缺口

**输出格式：**
```markdown
## 测试健康
- **总用例:** 290 passed ✅
- **测试文件:** 15 个，3,152 行
- **测试分布:** daemon(285) cli(264) force(223) adapters(273) ...
- **零测试模块:** ❌ 无（全部覆盖）
- **健康度:** 🟢 优秀
```

---

### Step 3: 文档审计

**检查目标（按优先级排序）：**

1. **PROJECT-PANORAMA.html** — 是否与代码同步？
2. **CHANGELOG.md** — 当前版本号与实际匹配？Unreleased 段是否过时？
3. **ROADMAP.md** — 已完成的故事标记正确？待办项合理？
4. **EPIC 文档** — 验收标准与实现一致？未完成项清晰标注？
5. **README / CONTRIBUTING** — 命令表、安装步骤可用？
6. **TECHDEBT 分析** — 最新版本，与当前状态一致？

**🔴 铁律：**
- 版本号一致性检查是 P0 — README/install.sh/ROADMAP 的版本号必须一致
- 如果发现 CHANGELOG 中标记为 completed 但在 ROADMAP 中仍为 pending → 立即同步

---

### Step 4: 代码质量扫描

**扫描项清单：**

```bash
# 模块大小
find . -name '*.py' -not -path './.git/*' -exec wc -l {} + | sort -rn

# TODO/FIXME/HACK
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" . | grep -v .git | grep -v venv

# 类型标注覆盖率
# 使用 mypy 或 grep 函数定义中的类型标注

# print vs logging
grep -rn "print(" --include="*.py" skill_advisor/ | grep -v __pycache__ | grep -v "#"

# 裸 except
grep -rn "except:" --include="*.py" . | grep -v .git | grep -v venv
```

---

### Step 5: 技术债评估

1. 查找项目目录中已有的 `TECHDEBT-ANALYSIS.md` 或类似文档
2. 对比当前状态与上一份债务分析：
   - 已修复的标记 ✅
   - 新增的标记 🆕
   - 未解决的保持原标记
3. 如果无现有债务文档 → 用 `analysis-workflow` §§8 做四层并行审计

**输出格式（债务变化追踪）：**
```markdown
| 维度 | 上次 | 本次 | 变化 |
|:---|:---:|:---:|:----:|
| 🔴 P0 | 3 | 3 | 旧问题已修复，新问题出现 |
| 🟡 P1 | 11 | 8 | -3 |
| 🟢 P2 | 9 | 8 | -1 |
| **合计** | **23** | **19** | **-4** |
```

---

### Step 6: Sprint Backlog 生成

**故事结构：**

```markdown
### SRA-003-NN: 故事标题 (优先级)

**类型:** 🔴 P0 / 🟡 P1 / 🟢 P2
**来源:** TechDebt #A7 / ROADMAP / 新功能
**估时:** ~X 小时
**依赖:** SRA-003-XX (如适用)

**背景：**（问题描述 / 用户故事）
**验收标准：**
- [ ] 标准 1
- [ ] 标准 2
```

**容量估算参考：**

| Sprint 时长 | 可用容量 | 说明 |
|:-----------|:---------|:-----|
| 半天 (4h) | 3-4 个故事 | 纯技术债修复 Sprint |
| 1 天 (8h) | 6-8 个故事 | 混合 Sprint |
| 3 天 | 15-20 个故事 | 完整迭代 |

**优先级排序规则：**
1. 🔴 P0 先于 🟡 P1 先于 🟢 P2
2. 依赖关系（被阻塞的故事排后）
3. 主人明确指出的紧急项优先

---

### Step 7: 汇报与确认

**输出模板：**

```markdown
# 📊 Sprint 计划 — {项目名} v{目标版本}

## 当前状态
| 维度 | 状态 | 说明 |
|:----|:----:|:-----|

## 建议的 Sprint 目标
> {一句话目标}

## Sprint Backlog
| 故事 | 类型 | 估时 | 依赖 |
|:----|:----:|:----:|:----:|

## 提议的 Sprint 顺序
1. Sprint {N}: {名称} — {焦点}
2. Sprint {N+1}: {名称} — {焦点}
3. ...

## 需要主人确认
- [ ] Sprint 目标是否正确？
- [ ] 优先级排序是否合适？
- [ ] 可以开始了吗？
```

---

## 🔴 铁律

1. **Step 1-5 不可跳过** — 没有分析就做计划 = 拍脑袋
2. **分支关系必须先做 `merge-base`** — `ahead/behind` 数值本身不能说明完整关系
3. **测试不能只看「通过」数字** — 要检查测试用例数是否因 fault 而减少
4. **版本号一致性是 P0** — 文档与代码版本必须匹配
5. **Sprint Backlog 必须有估时** — 没估时 = 无法做容量规划
6. **汇报后等主人确认再开始** — 方向错了白做
7. **分支分歧时优先 merge 而非 rebase** — 当本地 master 与 origin/master 因 GitHub PR merge commit 分歧时，merge 保留双方历史，rebase 会重写大量 commit 导致冲突蔓延

---

## Phase 2: Sprint 执行（计划确认后）

当主人确认计划后，进入执行阶段。这是 Planning Step 1~7 的延续。

### 执行流程

```
Step 8: 初始验证
  └── 全量测试确认基线 (pytest -q)
Step 9~15: 按计划逐个执行 Story
  ├── Story N: 实现 + TDD
  ├── Story N+1: 实现 + TDD 
  └── 每个 Story 独立 commit
Step 16: Git 分支同步
  ├── merge/rebase 到 master
  ├── 处理分歧历史
  └── push + tag
Step 17: doc-alignment 协议
  └── 更新 project-report.json + 生成 PANORAMA
Step 18: 最终验证
  ├── pytest 全量
  ├── git status clean
  └── 版本号一致性检查
```

### Git 分支同步（关键）

当本地分支领先 master 且远程已因 PR merge 产生分歧时：

```bash
# 1. 检查分支关系
git merge-base master origin/master

# 2. 分歧处理策略
#
# 情况                          | 策略
# ------------------------------|------------------------------
# 本地 master 是远程祖先         | git push (正常)
# 远程有额外 merge commit       | git merge origin/master (保留)
# 都分歧但本地文件最新            | git merge + git checkout --ours 解决
# 分歧含代码冲突                 | 仔细检查每处，不可简单 --ours

# 3. 标签管理
git tag -a vX.Y.Z -m "message"
git push origin vX.Y.Z
```

### 版本管理

```
发布前: __init__.py = "1.2.0", pyproject.toml = "1.2.0"
发布时: 两者同步后 merge → tag v1.2.0
发布后: dev 分支 bump → v1.3.0-dev
```

**P0 铁律:** `__init__.py` 与 `pyproject.toml` 版本号必须永远一致 —— 忘了就出 bug。

---

## 与相关技能的关系

| 技能 | 关系 |
|:-----|:-----|
| `development-workflow-index` | 本技能是 Sprint 规划阶段的实施者。规划完成后流入索引中的开发路径 |
| `analysis-workflow` | Step 4 代码质量扫描可复用其并行子代理审计模式 |
| `bmad-sprint-planning` | BMAD 版 Sprint 规划，适用于需要完整 BMAD 仪式感的项目 |
| `deep-research` | 如需调研可行性，属 Sprint 规划的前置依赖 |
| `doc-alignment` | 每个 Sprint 结束后必须对齐文档 |

---

## 参考文件

在 `references/` 目录下：
- `sra-v1.3.0-analysis.md` — SRA 项目 v1.3.0 实际分析示例（git/测试/文档/代码/债务/计划全流程）
- `sra-sprint3-execution.md` — SRA Sprint 3 执行实录：分支同步实战（分歧历史处理）、fork→subprocess 替换模式、版本发布流程
