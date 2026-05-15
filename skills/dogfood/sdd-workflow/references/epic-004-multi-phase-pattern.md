# 🏛️ EPIC-004 实战模式 — 多 Phase EPIC 完整生命周期

> **来源**: 2026-05-15 SRA 项目 EPIC-004
> **范围**: 7 Phase, 22 Story, 7 SPEC, 407 tests (plugin 93 + SRA 314)
> **核心模式**: 从补丁方案重构为 Hermes 原生插件的完整 SDD 旅程

---

## 一、EPIC 多 Phase 管理结构

### 1.1 EPIC 前置元数据

```yaml
# EPIC-N.md 的 frontmatter
---
epic_id: EPIC-004
title: "描述"
status: draft → active → done  # 三态演进
stories:  # 列出所有 SPEC 编号
  - SPEC-4-1
  - SPEC-4-2
  ...
---
```

### 1.2 Phase 分解表

EPIC 体中使用 Markdown 表格声明所有 Phase：

```markdown
### Phase 0: 名称 (P0)

**入口门禁**: 条件
**出口里程碑**: 条件

| SPEC | Story | 标题 | 估时 | 描述 |
| SPEC-4-1 | STORY-4-1-1 | ... | 1h | ... |
```

### 1.3 已完成 Phase 追踪表

每个 Phase 完成后，在 EPIC 中追加一行到追踪表：

```markdown
### ✅ 已完成 Phase

| Phase | 状态 | Stories | 验证 |
| Phase 0: 插件框架 | ✅ 完成 | 5/5 | 55/55 测试全绿 |
| Phase 1: 消息注入 | ✅ 完成 | 3/3 | 55/55 测试全绿 |
```

### 1.4 优先级汇总表

```markdown
| Phase | 优先级 | Stories | 估时 |
| Phase 0: 插件框架 | 🔴 P0 ✅ | 5 | 5h |
| Phase 1: 消息注入 | 🔴 P0 ✅ | 3 | 3.5h |
```

---

## 二、Phase 逐阶段推进流程

### 2.1 每个 Phase 的生命周期

```
入口门禁确认 → CLARIFY → SPEC → REVIEW → STORY → REVIEW → IMPLEMENT → COMPLETE
  Phase N-1 done    主人确认   创建SPEC   主人审批   创建Story  主人审批   TDD实施   文档对齐
```

### 2.2 铁律

- EPIC 批准 ≠ Phase 批准。每个 Phase 独立 CLARIFY
- Phase N 的 CLARIFY 必须在 Phase N-1 全部完成后才能发起
- 不允许在同一个 CLARIFY 中同时确认多个 Phase

### 2.3 估时与优先级

- P0（核心功能）：Phase 0-1 — 必须优先完成
- P1（重要功能）：Phase 2-3, 5-6 — 核心补充
- P2（优化功能）：Phase 4 — 锦上添花

---

## 三、文档对齐链（从底向上）

每个 Phase 完成后，从底向上同步——先改最底层的 Story，最后改最顶层的 project-report：

```text
Layer 1: Story 文件            ← 先更新
  └─ status: draft → completed
  └─ AC: [ ] → [x]
Layer 2: SPEC 文件
  └─ status: active → completed
  └─ 完成条件: [ ] → [x]
Layer 3: EPIC 文件
  └─ completed_phases 追加
  └─ 优先级表格标记 ✅
Layer 4: project-report.json   ← 最后更新
  └─ tests, epics, sprint
```

详细步骤见 `references/phase-completion-checklist.md`。

---

## 四、防止虚假 [x] — AC 验证注释模式

### 4.1 问题

AC 标记 [x] 只说明「文档上打了勾」，不说明「代码真实存在」。
EPIC-001/003 共 12 个虚假 [x] 从未被检测到。

### 4.2 解决方案：`<!-- 验证: -->` 注释

在每个 [x] AC 行后附加可执行的验证命令：

```markdown
- [x] Hermes pre_tool_call hook 集成 <!-- 验证: python3 -m pytest
       plugins/sra-guard/tests/test_validate_hook.py -q -->
```

### 4.3 验证脚本

配套 `scripts/ac-audit-code-check.py` 脚本自动执行所有验证命令：

```bash
# 验证 EPIC-003 的所有 AC
python3 scripts/ac-audit-code-check.py docs/EPIC-003-v2-enforcement-layer.md
# 输出: ✅ 全部 4 个 AC 验证通过！ (exit 0)

# 列出所有验证点（不执行）
python3 scripts/ac-audit-code-check.py --list
```

### 4.4 验证命令规范

| AC 类型 | 验证命令 | 示例 |
|:--------|:---------|:------|
| 测试覆盖 | `pytest <path>` | `pytest tests/test_validate_hook.py -q` |
| 端点存在 | `curl <url>` | `curl http://127.0.0.1:8536/health` |
| 代码存在 | `grep <pattern> <file>` | `grep -r "pre_tool_call" plugins/` |

---

## 五、端到端收尾模式

### 5.1 最终 Phase 的设计

最后一个 Phase 应为 **验证+收尾** 阶段：

| Story | 内容 | 目的 |
|:------|:-----|:------|
| 端到端测试 | mock 服务器 + 真实插件加载 → 全链路验证 | 验证所有 hook 协作 |
| AC 门禁脚本 | 自动化验证每个 [x] 有真实代码 | 防止虚假标记复发 |
| 文档收尾 | 回归测试 + 所有文档标记完成 | EPIC status: done |

### 5.2 EPIC 完成条件表

EPIC 最后放置完成条件追踪表：

```markdown
## ✅ 完成条件

| # | 条件 | 状态 | 说明 |
|:-:|:-----|:----:|:------|
| 1 | Phase 0-6 全部完成 | ✅ | 全部完成！ |
| 2 | 全量测试通过 | ✅ | 407 tests |
```

### 5.3 最终状态

```yaml
# EPIC frontmatter
status: done
```

---

## 六、EPIC-004 数据参考

| 指标 | 数值 |
|:-----|:-----:|
| Phase 总数 | 7 |
| SPEC 总数 | 7 |
| Story 总数 | 22 |
| 代码文件 | 9（插件）+ 1（门禁脚本）|
| 测试文件 | 7（插件测试）|
| 测试总数 | 93（plugin）+ 314（SRA）= 407 |
| 总估时 | ~21h |

### Phase 拆分统计

| Phase | Stories | 优先级 | 测试增长 |
|:------|:-------:|:------:|:---------|
| 0: 插件框架 | 5 | P0 | 0→55 |
| 1: 消息注入 | 3 | P0 | 55→55 |
| 2: 工具校验 | 3 | P1 | 55→55 |
| 3: 轨迹追踪 | 3 | P1 | 55→67 |
| 4: 周期重注入 | 3 | P2 | 67→83 |
| 5: 文档修复 | 2 | P1 | 83→83 |
| 6: 端到端+CI | 3 | P1 | 83→93 |
