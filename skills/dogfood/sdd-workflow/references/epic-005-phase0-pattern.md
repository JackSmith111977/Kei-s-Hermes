# EPIC-005 Phase 0 实战模式 — 标准定义先行

> **2026-05-16** — hermes-cap-pack 项目 EPIC-005「Skill 治理引擎」Phase 0 完整生命周期记录。
> **模式价值**：验证了「标准先于检测器」的 Phase 级别 SPEC 分离模式。

---

## Phase 0 概要

| 项目 | 值 |
|:-----|:----|
| EPIC | EPIC-005: Skill 治理引擎（4 Phases, ~24h） |
| Phase | **Phase 0: 统一标准制定**（前置门禁） |
| SPEC | SPEC-5-0: 统一标准制定（独立于 SPEC-5-1 核心引擎） |
| Stories | 3（5-0-1 / 5-0-2 / 5-0-3） |
| 总耗时 | ~6h |
| 交付物 | 4 个新文件 + 3 个 Story 文件 |

---

## SDD 生命周期

### Step 1: CLARIFY
- 展示 EPIC-005 全貌（4 个 Phase 的完整路线图）
- 明确 Phase 0 是「纯标准定义阶段，不涉及检测器代码」
- 主人回复「确认」即通过

### Step 2: SPEC-5-0 创建
```bash
spec-state.py create "SPEC-5-0" "统一标准制定 — Phase 0"
spec-state.py submit "SPEC-5-0"   # → review
spec-state.py approve "SPEC-5-0"  # 主人批准
```

### Step 3: Story 创建 + 批准
```bash
spec-state.py create "STORY-5-0-1" "制定四层统一标准"
spec-state.py create "STORY-5-0-2" "machine-checkable 规则集"
spec-state.py create "STORY-5-0-3" "Workflow 编排模式定义"

spec-state.py submit "STORY-5-0-1"  # → review
spec-state.py submit "STORY-5-0-2"
spec-state.py submit "STORY-5-0-3"

spec-state.py approve "STORY-5-0-1"  # 3 个一起批准
spec-state.py approve "STORY-5-0-2"
spec-state.py approve "STORY-5-0-3"
```

### Step 4: 实现（依赖有序 + 并行）

```text
STORY-5-0-1 (标准文档) ── 先完成 ──→ STORY-5-0-2 (规则集) — 可并行 —→
                                 └─→ STORY-5-0-3 (编排模式) — 可并行 —→
```

STORY-5-0-2 和 STORY-5-0-3 通过 `delegate_task` 并行执行，节省 ~40% 时间。

### Step 5: 完成 + 三维一致性检查

```bash
# 1. spec-state.py complete（状态机）
spec-state.py complete "STORY-5-0-1"
spec-state.py complete "STORY-5-0-2"
spec-state.py complete "STORY-5-0-3"

# 2. ⚠️ 同步 markdown frontmatter
# 手动修改 > **status**: `draft` → `completed`
# 批量标记 AC: [ ] → [x]

# 3. 同步 project-state.yaml
project-state.py sync

# 4. 三维一致性验证
project-state.py verify  # exit 0
```

### Step 6: Phase 完成仪式

```bash
# 1. 更新 project-state.yaml phases
#    - 标记 Phase-0 AC 为 done
#    - 追加 completed_phases: [Phase-0]
#    - 更新 EPIC-005 completed_count: 3

# 2. 标记 SPEC-5-0 完成
spec-state.py architect "SPEC-5-0"
spec-state.py plan "SPEC-5-0"
spec-state.py implement "SPEC-5-0"
spec-state.py complete "SPEC-5-0"

# 3. 最终验证
project-state.py verify  # 全一致

# 4. 提交
git commit -m "feat: EPIC-005 Phase 0 完成"
```

---

## 关键决策

| 决策 | 选择 | 理由 |
|:-----|:-----|:------|
| Phase 0 独立 SPEC（SPEC-5-0）| ✅ 是 | 与 Phase 1 解耦，标准定义可独立审批 |
| 标准文档格式 | Markdown | 人类可读为主，machine-checkable 规则单独用 YAML |
| v3 schema 兼容策略 | `allOf` + `if/then` 扩展 | v2 包全部通过 v3 验证 |
| Workflow 定义位置 | 独立文件 + cap-pack.yaml 引用 | 不侵入 skill 本身，声明式定义 |

## 实战教训

| 陷阱 | 表现 | 根因 | 预防 |
|:-----|:------|:------|:------|
| spec-state.py complete → verify 失败 | 状态机显示 completed 但 verify 报状态不一致 | markdown frontmatter `> **status**:` 仍为 draft | complete 后先改 frontmatter 再 sync 再 verify |
| EPIC 无 Phase 配置 → phase-gate.py 失败 | `❌ Epic EPIC-005 没有 Phase 配置` | project-state.yaml 的 phases 字段未注册 | 创建 EPIC 后立即注册 Phase 结构 |
| delegate_task 并行 → spec-state 不同步 | 委托后忘记更新状态机 | 委托子任务只写文件不管理 SDD 状态 | delegate 完成后手动 spec-state.py complete |
