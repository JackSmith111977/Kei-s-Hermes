# Sprint 迭代规划与 Git 分支工作流

> 用于 Hermes/Boku 环境下的项目迭代启动标准流程
> 结合 BMad Method 与 GitHub 最佳实践

---

## 🎯 设计哲学验证（先于具体设计）

> **关键教训**：在开始设计任何功能特性前，先验证设计哲学方向。
> 否则可能做了「阻断强度」才发现用户要的是「注入覆盖度」。

**启动任何新功能设计前，先确认：**

| 问题 | 正确方向 vs 错误方向 |
|:-----|:--------------------|
| 这个功能是控制**阻断力度**还是**注入时机**？ | ❌ 阻断力度（block）→ ✅ 注入覆盖度（inject） |
| 用户要的是**强制力**还是**可见度**？ | ❌ 强制执行 → ✅ 增加可见性 |
| Agent 不配合时怎么办？ | ❌ 阻断工具执行 → ✅ 在适当时机注入推荐上下文 |

**核心原则 — Injection Over Interruption**：
- **注入优先**：在适当时机注入上下文和建议，让 Agent 自主决定是否采纳
- **阻断慎用**：除非安全/合规等绝对必要场景，否则不阻断工具执行
- **力度 ≠ 阻断强度**，力度 = **注入覆盖度**（控制在哪 些 时 机 注入推荐，而非是否允许执行）

**4 级注入覆盖度参考模型**：
```
L1: 仅用户消息时注入推荐
L2: + 关键工具调用前注入提醒
L3: + 全部工具调用前后核查
L4: + 周期性重注入防漂移
```

---

## 标准流程

### 第 1 步：分析现状

在开始新迭代前，先收集：
- 当前版本号（`pyproject.toml` / `package.json`）
- 现有分支结构（`git branch -a`）
- 已规划的 Epic/Story（roadmap/changelog）
- 最近的 commit 历史（`git log --oneline -10`）
- Epic 文档中的已有设计方向和验收标准

### 第 2 步：创建迭代分支

```bash
# 从 master/main 切出
git checkout master
git pull
git checkout -b feat/v<version>-<descriptive-name>
```

**命名规范**：
- 大版本：`feat/v2.0-enforcement-layer`
- 功能：`feat/xxx-feature`
- 修复：`fix/xxx-bug`
- 文档：`docs/xxx`

### 第 3 步：编写 Sprint 计划

按 BMad 标准 Sprint 计划模板，保存到 `.hermes/plans/`：

```markdown
## Sprint Goal
[一行概括]

## Sprint Backlog
### Story N: 标题 — 🔴 P0 — X天
**目标**: [一句话]
**任务分解**:
1. [原子任务 1]
2. [原子任务 2]
**文件变更**:
- 新增: `path/to/file`
- 修改: `path/to/file`

## 估时汇总
| Story | 优先级 | 天数 | 依赖 |

## 验收标准（DoD）

## 风险管理
```

### 第 4 步：更新项目文档

| 文档 | 更新内容 |
|:-----|:---------|
| `CHANGELOG.md` | [Unreleased] 下新增 Sprint 条目（含状态/优先级/估时） |
| `ROADMAP.md` | Sprint 状态表更新 |
| Epic 文档 | 状态改为 `sprint-N` |
| `.hermes/plans/` | 保存 Sprint 计划文件 |

### 第 5 步：提交分支起点

```bash
git add CHANGELOG.md ROADMAP.md docs/EPIC-*.md .hermes/plans/*
git commit -m "chore(sprint): init <version> iteration branch"
git push origin feat/v<version>-<name>
```

### 第 6 步：实施与一致性检测

每个 Story 实施的完整流程：

```
  实现 Story
      ↓
  写测试
      ↓
  代码审查 (code-review)
      ↓
  ⚡ 一致性检测 ← 强制！提交前自检
     ├─ P0 安全检查（一票否决）
     ├─ P0 文档一致性（代码改了文档同步了吗？）
     ├─ P1 Commit Message 规范
     ├─ P1 变更范围纯净
     └─ P2 业务一致性
      ↓
  通过 → git commit → git push
  失败 → 修复后重检
```

> **一致性检测内容**（由 `commit-quality-check` skill 执行）：
> - 安全红线：硬编码密码/Token/API Key
> - 文档一致性：README API 表与代码路由匹配
> - 版本一致性：`pyproject.toml` 与 `__init__.py` 版本同步
> - 变更范围：不夹带与本次 Story 无关的修改

---

## 避坑指南

- ❌ **跳过 CHANGELOG 更新** → 迭代结束后不知道改了什么
  - ✅ 分支起点就标记 Sprint 启动
- ❌ **Sprint 计划只存脑子里** → 过两天忘了目标
  - ✅ 保存到 `.hermes/plans/` 持久化
- ❌ **Epic 文档状态不更新** → 读文档的人不知道当前在做什么
  - ✅ 每次 Sprint 启动/结束更新状态
- ❌ **分支名太笼统**（如 `dev`/`feature`） → 不知道 scope
  - ✅ 用 `feat/v2.0-xxx` 语义化命名
- ❌ **对设计方向做过度假设** → 设计时自动假设「阻断强度」而非「注入覆盖度」
  - ✅ **先验证设计哲学**：在具体设计前，用一句话确认核心意图
- ❌ **完成 Story 直接 git commit，跳过一致性检测**
  - ✅ 任何代码/文档变更后，**先跑 commit-quality-check 再 commit**
  - ✅ 一致性检测最晚在 git commit 前、最好在完成任务后立即执行
- ❌ **CI 阶段才做质量检查** → 已经来不及了
  - ✅ 检测在提交前完成，CI 是补充验证而非替代
