# Phase Gate 模式 — SDD 增量工作流门禁

> 用途：防止 EPIC 级别的 Phase 化工作中跳过 SDD 流程
> 创建：2026-05-14 · 来源：hermes-cap-pack EPIC-004 实战

---

## 问题背景

当 EPIC 采用 Phase 化工作流（如 Phase 0 → 1 → 2 → 3 → 4）时，EPIC 的批准容易造成「EPIC 已批准 = 所有 Phase 可直接实施」的误解。实际上：

- **EPIC 批准** = 工作方向被认可
- **每个 Phase 的 CLARIFY** = 具体实施方案的确认
- **Phase N 进入前** = Phase N-1 必须已全部完成

## 模式架构

### 三层防护

```
L1: Phase Schema (数据层)
    ├── project-state.yaml 中的 phases: 字段
    └── 定义所有 Phase、AC、依赖关系

L2: phase-gate.py (门禁层)
    ├── check — 能否进入目标 Phase
    ├── start — 开始 Phase（前置检查）
    └── complete — 标记 Phase 完成（AC 检查）

L3: SDD Workflow (行为层)
    ├── EPIC 批准后不自动赋予实施权限
    ├── 每个 Phase 前必须 CLARIFY
    └── Phase 门禁是 boku 的铁律
```

### Phase Schema（YAML 段）

```yaml
phases:
  EPIC-XXX:
    title: 描述
    phases:
      - name: Phase-N
        title: Phase 标题
        acceptance_criteria:
          - criteria: AC 描述
            done: false
        requires:
          - Phase-(N-1) 已完成
        stories:
          - STORY-X-Y-Z
    completed_phases:
      - Phase-0
      - Phase-1
```

### 门禁流程

```text
EPIC 已批准
    ↓
Phase-0 ──→ CLARIFY ──→ 主人批准 ──→ 实施 ──→ phase-gate complete
    ↓
Phase-1 ──→ CLARIFY ──→ 主人批准 ──→ 实施 ──→ phase-gate complete
    ↓
Phase-2 ──→ CLARIFY ──→ 主人批准 ──→ 实施 ──→ phase-gate complete
    ↓
...
```

## 实战案例：EPIC-004

| Phase | 状态 | 说明 |
|:------|:----:|:------|
| Phase-0 | ✅ 已完成 | SQS 基线扫描 → CLIARIFY → 实施 → complete |
| Phase-1 | ✅ 已完成 | L2/L3 补充 → CLIARIFY → 实施 → complete |
| Phase-2 | ⏳ 当前 | 质量提升 → 需要 CLIARIFY → 主人批准 → 实施 |
| Phase-3 | ⏭️ 等待 | 合并/清理 |
| Phase-4 | ⏭️ 等待 | 门禁固化 |

## 关键教训（2026-05-14）

1. **Phase 定义 ≠ 实施许可**。EPIC 文档中描述的 Phase 仅仅是计划，每个 Phase 在进入前仍然需要单独的 CLARIFY
2. **甚至不是只差 CLARIFY**。Phase 门禁要阻止的是「EPIC 批准 → 直接写代码/改文件」的跳跃
3. **恢复路径**：如果已经跳过 Phase 门禁直接实施，回退所有更改 → 从 CLARIFY 重新走 SDD 流程

## 集成方法

### 选项 A：独立脚本（推荐首次使用）

将 `phase-gate.py` 放在项目的 `scripts/` 目录下，在 `docs/project-state.yaml` 中配置 `phases:` 字段。

### 选项 B：SDD skill 内置

此参考文档记录了模式，可供任何项目直接复现。
