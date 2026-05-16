# 📐 标准优先过渡模式 — Phase 0→1/2/3 Transition Pattern

> **实战验证**: hermes-cap-pack EPIC-005 (2026-05-16)  
> **范围**: Phase 0（统一标准制定）→ Phase 1（核心引擎 MVP），7 Stories，~16h  
> **核心原则**: 标准必须先于检测器存在

---

## 〇、背景

当 EPIC 包含多个 Phase，且 Phase 0 是「标准定义阶段」时，Phase 0 的产出物（标准文档、schema、规则集）会成为后续 Phase（检测器、集成、适配）的**规范来源**。

本模式描述了 Phase 0→Phase N 的标准化过渡流程，确保标准锁定后才进入实现阶段。

---

## 一、典型 Phase 结构

```
EPIC-NNN: Skill 治理引擎 (4 Phases)
  │
  ├── Phase 0: 标准定义        ← 前置门禁：所有后续 Phase 依赖此 Phase
  │   ├── L0-L4 标准文档
  │   ├── machine-checkable 规则集
  │   ├── schema 更新
  │   └── workflow 编排定义
  │
  ├── Phase 1: 核心实现        ← 引用 Phase 0 的标准做检测器
  │   ├── 规则驱动引擎（从 rules.yaml 加载）
  │   └── 分层输出（L0-L4 对应标准）
  │
  ├── Phase 2: 平台集成        ← 引用 Phase 0/1 的检测结果
  └── Phase 3: 多 Agent 适配  ← 引用 Phase 0/1/2
```

**门禁规则**:
- Phase N 完成 → 才能进入 Phase N+1
- Phase 0 的每个 AC 需通过「主人批准」门禁
- Phase 1 的 SPEC 需在 Phase 0 完成后**重新对齐**（如有新标准产出）

---

## 二、Phase 0 标准定义阶段（详细流程）

### 2.1 执行步骤

```text
Step 1: CLARIFY — 确认标准范围（全貌展示 + 主人确认）
    ↓
Step 2: RESEARCH — 行业调研（已有工具/标准/学术研究）
    ↓
Step 3: SPEC CREATE — 创建 SPEC-N-0（标准定义专属 SPEC）
    ↓
Step 4: SPEC REVIEW — 主人批准标准方向
    ↓
Step 5: Story 分解 (典型 3 Stories)
    ├── STORY-N-0-1: 标准文档定稿
    ├── STORY-N-0-2: machine-checkable 规则集（供后续 Phase 引用）
    └── STORY-N-0-3: 模式定义（如 workflow 编排、模板等）
    ↓
Step 6: 实施 → 验证 → 完成
```

### 2.2 产出物规范

| 产出物 | 用途 | 消费方 |
|:-------|:-----|:-------|
| `docs/CAP-PACK-STANDARD.md` | 人类可读的标准文档 | 所有后续 Phase 的规范来源 |
| `standards/rules.yaml` | machine-checkable 规则集 | Phase 1 检测器直接加载 |
| `schemas/cap-pack-v{N}.schema.json` | 结构化验证 schema | Phase 1 合规检查器 |
| `standards/*.md` | 模式定义（workflow 等） | Phase 1 特定检测器 |

### 2.3 验收条件模板

```markdown
**Phase 0 验收标准：**
- [ ] 标准文档覆盖 L0-L{N} 全部层级
- [ ] 每层有明确的 machine-checkable 规则（JSON/YAML）
- [ ] Layer N 模式支持预定义的全部类型
- [ ] 标准通过主人审阅批准
- [ ] 项目状态已同步并 commit
```

---

## 三、Phase 1 过渡流程（关键）

### 3.1 过渡前检查清单

**在进入 Phase 1 前确认：**

```text
□ Phase 0 验收条件全部满足（AC 全 [x]）
□ Phase 0 已标记 completed_phases
□ project-state.yaml 已同步
□ SPEC-N-1 已对照 Phase 0 产出物对齐更新
```

### 3.2 SPEC 对齐更新（重要）

Phase 0 完成前草拟的 Phase 1 SPEC（如 SPEC-5-1）需要**在 Phase 0 完成后重新对齐**：

| 更新点 | 原内容 | 对齐后 |
|:-------|:-------|:-------|
| 标准引用 | 引用 v2 schema 或无标准引用 | 引用 Phase 0 的 standards/rules.yaml |
| 检测器实现 | 硬编码检查逻辑 | 规则驱动（从 rules.yaml 加载） |
| 合规检查 | 自定义验证 | 引用 Phase 0 的 v3 schema |
| Workflow 检测 | 简单 pattern 匹配 | 引用 workflow-patterns.md 的 W 规则 |
| CLI 输出 | 自由格式 | 按 L0-L4 分层输出（对应标准层级） |

### 3.3 检测器架构模式

```
standards/rules.yaml (Phase 0)
         ↓ 加载
    RuleLoader (base.py)
         ↓ 按层分组
    ┌──────┼──────┐
    L1     L2     L4
  Compliance Atomicity Workflow
  Checker   Scanner   Detector
         ↓ 按 L0-L4 分层
    JSONReporter / HTMLReporter
```

**关键设计决策**: 检测器不硬编码任何检查逻辑——所有规则从 Phase 0 的 `rules.yaml` 加载。规则变更只需修改 YAML，不需改代码。

### 3.4 过渡中的文档对齐链

Phase 0 → Phase 1 过渡时需要执行的文档对齐链（从底向上）：

```text
Phase 0 完成
    ↓
更新 Phase 0 的 Story/SPEC 元数据（status, AC）
    ↓
更新 EPIC 文档（completed_phases 追加 Phase 0）
    ↓
重新对齐 Phase 1 的 SPEC（更新标准引用）
    ↓
提交 Phase 0 + Phase 1 的 SPEC 变更
    ↓
Phase 1 CLARIFY（基于更新后的 SPEC）
```

---

## 四、通用化：任意 Phase N→N+1 过渡

本模式不限于 Phase 0→1，适用于任意标准定义→实现的阶段过渡：

```
Phase N: 标准/规范/接口定义
    ↓ 产出：文档 + schema + 规则 + 契约
Phase N+1: 引用实现的开发
    ↓ 关键：Phase N 的 SPEC 和产出物必须先锁定
Phase N+2: 集成/部署
```

### 通用过渡检查清单

```text
□ Phase N 的 AC 全部 [x]
□ Phase N 产出物已 commit 到 main
□ project-state.yaml 已标记 completed_phases
□ Phase N+1 的 SPEC 已重新对齐（引用 Phase N 产出物）
□ EPIC 文档已更新 completed_phases
□ 主人已确认过渡（phase-gate.py check EPIC Phase-(N+1)）
```

---

## 五、实战陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| Phase 1 的 SPEC 在 Phase 0 前已草案但未重新对齐 | 检测器仍硬编码逻辑，不引用 rules.yaml | Phase 0 完成后强制更新 SPEC 引用 |
| standard 文档产出后未通知 Phase 1 的 SPEC 作者 | 检测器实现与标准脱节 | Phase 0 AC 中包含「通知下游 SPEC」检查项 |
| 状态机双写冲突 | spec-state.py 和 project-state.yaml 状态不一致 → sync 时回退到旧状态 | 每次变更后手动验证 project-state.yaml 的最终状态 |
| 检测器代码直接硬编码阈值而非引规则文件 | 规则变更需改代码 → 维护成本高 | 在 Architecture Review 中强制检查 RuleLoader 引用 |

---

## 六、实际案例：EPIC-005 Phase 0→1

| 项目 | 值 |
|:-----|:----|
| Phase 0 标准文档 | `docs/CAP-PACK-STANDARD.md` v1.0 (290行) |
| Phase 0 规则集 | `standards/rules.yaml` — 5 layers, 33 rules |
| Phase 0 Schema | `schemas/cap-pack-v3.schema.json` (v2 兼容) |
| Phase 0 编排模式 | `standards/workflow-patterns.md` (1078行) |
| Phase 1 检测器 | `packages/skill-governance/` — 18文件, 2691行 Python |
| 过渡耗时 | ~10min（对齐更新 + 审阅） |
