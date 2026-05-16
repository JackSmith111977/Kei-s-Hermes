# 联合工作流实战记录：EPIC-005 Phase 3

> **日期**: 2026-05-16
> **项目**: hermes-cap-pack
> **主人指令**: 「可以进行联合工作流」

## 全链流程

```
主人说「继续」→ boku CLARIFY Phase 3 →
主人说「可以进行联合工作流」→

SPEC 创建 → Story 创建 → DEV 实现 → QA 门禁 → COMMIT
(无逐阶段停顿, 一次完成)
```

## 执行细节

### 1. CLARIFY + SPEC 创建
- 展示完整的 Phase 3 规划（3 Stories, 架构图, 依赖关系）
- 主人说「可以进行联合工作流」— 这是触发词

### 2. Story 创建 (一次性全部创建)
- SPEC-5-3.md (8.9K, 含技术方案 + AC + 不做范围)
- STORY-5-3-1.md (适配器抽象层 + OpenCode)
- STORY-5-3-2.md (MCP Server)
- STORY-5-3-3.md (OpenClaw / Claude Code)

### 3. DEV 实现 (依赖→并行)
- **先**: delegate_task STORY-5-3-1（base.py 139行 + opencode_adapter.py 460行 + hermes重构）
  - 验证: 141/141 pytest ✅
- **并行**: delegate_task STORY-5-3-2（MCP Server 506行）
           delegate_task STORY-5-3-3（openclaw_adapter.py + claude_adapter.py 619行）
  - 验证: MCP 5 tools + 3 resources ✅, 141/141 pytest ✅

### 4. QA 门禁
- L0: ast.parse 语法检查 — 6 新文件全过 ✅
- L1: pytest 141/141 ✅
- L2: MCP tools/resources 验证 ✅

### 5. Phase-end 一次性对齐 (5 层一次性更新)
```
Layer 1: Story frontmatter  (3文件: draft→completed)
Layer 2: SPEC frontmatter   (1文件: draft→completed)
Layer 3: EPIC 文件           (Phase 3 AC [x] + ✅标记)
Layer 4: project-state.yaml (completed_count: 11→14)
Layer 5: project-report.json (stories + sprint 更新)
Layer 6: chain-state.json   (phase: Phase-3, COMPLETED)
```

### 6. COMMIT
```
commit 8edfc50
feat: EPIC-005 Phase 3 完成 — 多 Agent 适配层 (3 Stories)
29 files changed, 2516 insertions(+), 67 deletions(-)
```

## 关键决策

| 决策 | 选择 | 理由 |
|:-----|:-----|:------|
| 委托方式 | delegate_task（非 opencode run） | 4+ 文件/Story，上下文量大 |
| 执行顺序 | 依赖先→并行 | STORY-5-3-1 创建 base.py → 5-3-2 + 5-3-3 并行 |
| 对齐时机 | Phase end 一次性 | 比逐个 Story 更新高效 5x |
| 安装方式 | pip install -e (--break-system-packages) | 系统 Python 3.12 PEP 668 限制 |
| pyproject.toml | setuptools.build_meta（非 _legacy） | 旧版后端在当前环境不可用 |

## 触发词总结

主人说「可以进行联合工作流」→ 跑完整链不停等。
主人说「继续」→ 逐段推进，每阶段停顿等确认。
