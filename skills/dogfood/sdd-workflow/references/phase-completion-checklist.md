# 📋 Phase 完成检查清单 — 文档元数据同步

> **问题**: 代码完成 ≠ 文档完成。Story/SPEC/EPIC markdown 文件的元数据（status 字段、AC 复选框、完成条件清单）不会自动更新。
> **影响**: 11 个 Story + 3 SPEC + EPIC + project-report 全部停留在 draft → 下次迭代出现系统性能文档漂移。
> **根因**: SDD 工作流只要求 `spec-state.py complete` 更新状态机，不要求同步 markdown 文件的 frontmatter/AC。

---

## 一、强制同步清单

完成一个 Phase 的所有 Story 后，按此顺序执行：

### 1. Story 文件（每 Phase 3-5 个）

```text
修改项:
  status: draft|active|in_progress → completed
  AC 列表: [ ] → [x]（所有验收条件的条件/验证/预期项）
  完成检查清单: [ ] → [x]
  updated 日期: 更新为当前日期
```

批量操作示例（Python）：
```python
import re, os, glob

for fpath in glob.glob("docs/stories/STORY-4-*.md"):
    with open(fpath) as f:
        content = f.read()
    content = content.replace("status: draft", "status: completed")
    content = content.replace("status: active", "status: completed")
    content = content.replace("- [ ] ", "- [x] ")  # 注意: 如果还有未完成的 AC 会误标
    content = re.sub(r'updated: \d{4}-\d{2}-\d{2}', 'updated: 2026-05-15', content)
    with open(fpath, 'w') as f:
        f.write(content)
```

⚠️ **安全警告**: 只在确认所有 AC 都已完成后才执行全局 `- [ ] ` → `- [x]`。如果有未完成的 AC，逐个标记。

### 2. SPEC 文件（通常 1 个/Phase）

```text
修改项:
  status: active|draft → completed
  完成条件清单: [ ] → [x]
  updated 日期: 更新
```

### 3. EPIC 文件（1 个）

```text
修改项:
  status: draft → active（首次）| completed（全部完成）
  添加/更新 completed_phases 区块:
    ### ✅ 已完成 Phase
    | Phase | 状态 | Stories | 验证 |
    | Phase X: 标题 | ✅ 完成 | N/N | 验证结果 |
  优先级的 Phase 表格: 对应 Phase 添加 ✅ 标记
  updated 日期: 更新
```

### 4. project-report.json

```text
修改项:
  epics[]: 添加 EPIC-N 条目 + 完成的 stories 列表
  tests: 更新 passing/total 计数
  sprint_history[]: 添加新 sprint 条目
  architecture/module_table: 添加新模块（如有）
```

> **⚠️ 漂移程度判断**: 如果 project-report.json 出现系统性漂移（版本落后、模块数不符、缺失完整 Epic、测试文件列表过期），请使用 doc-alignment skill 的 `references/project-report-json-rebuild.md` 执行全量重建，而非增量 patch。

---

## 二、验证命令

执行完同步后运行：

```bash
# 1. 确认所有 Story 状态
grep "^status:" docs/stories/STORY-*.md

# 2. 确认无残留 [ ]
grep -c "\[ \]" docs/stories/STORY-*.md    # 应全部返回 0
grep -c "\[ \]" docs/SPEC-*.md             # 应全部返回 0（或只有确实未完成的）

# 3. 确认 project-report.json 更新
python3 -c "import json; d=json.load(open('docs/project-report.json')); print(f'Tests: {d[\"tests\"][\"passing\"]}/{d[\"tests\"][\"total\"]}'); print('Epics:', [e['id'] for e in d['epics']])"
```

---

### 5. chain-state.json（多 Phase EPIC 时）⚠️ 容易遗漏

当 EPIC 包含多个 Phase（如 EPIC-005 的 Phase 0/1/2/3），每完成一个 Phase，`chain-state.json` 需要手动更新 Phase 字段，否则下一个 Phase 的状态机无法感知当前进度。

```text
修改项:
  phase: 更新为下一 Phase 编号（如 "Phase-3"→"Phase-4"）
  completed_stages: 如有需要可追加（但 multi-phase 场景通常复用已完成阶段）
```

**为什么需要手动更新？**
- `chain-state.json` 追踪的是 **workflow chain 阶段**（SPEC→DEV→QA→COMMIT），而非 **EPIC Phase**（Phase-0→Phase-1→Phase-2）
- 每个 Phase 都会走一遍完整的 `SPEC→DEV→QA→COMMIT` 链
- 完成后 `chain-state.json` 显示完成，但不会自动进入下一 Phase
- 需要手动将 `"phase": "Phase-N"` 更新为 `"phase": "Phase-(N+1)"`

**示例**（EPIC-005 Phase 2 完成后）：
```json
{
  "EPIC-005": {
    "epic": "EPIC-005",
    "current_stage": "SPEC",
    "completed_stages": ["COMMIT", "QA", "DEV", "SPEC"],
    "phase": "Phase-3",       // ← 手动从 Phase-2 改为 Phase-3
    "gate_history": []
  }
}
```

**检查清单**：在 Phase 所有 Story 都标记 `completed` 后，问自己：
- [ ] 这是多 Phase EPIC 吗？
- [ ] chain-state.json 的 `phase` 字段是否为下一 Phase？
- [ ] 如果是最后一个 Phase → `phase` 可设为 `COMPLETED`

---

## 三、常见失误

| 失误 | 后果 | 预防 |
|:-----|:-----|:------|
| 只更新 status，忘更新 AC 标记 | 文档状态为 completed 但 AC 仍全为 [ ] | 运行 `grep "\[ \]"` 验证 |
| 只更新 Story 忘更新 SPEC/EPIC | EPIC 仍显示 Phase 未完成 | 检查 project-report + EPIC |
| 用 patch 逐文件更新（11 文件 × 3 处 = 33 次 api 调用） | 耗时、易出错 | 用 execute_code + Python 一次处理 |
| 忘记 project-report.json 的 test 计数 | 报告显示旧测试数 | 验证 `tests.passing/tests.total` |
| **先跑 `project-state.py sync` 再手动修 frontmatter** | sync 从 spec-state.py JSON 读取 → spec-state.py 无记录 → 将已完成的 story/spec 回退到 draft | **顺序很重要**: 先手动修 markdown frontmatter → 再 `python3 scripts/project-state.py verify` → 如果 verify 报错，直接 patch `project-state.yaml` 手动修正，跳过 sync。或者：修 frontmatter → patch project-state.yaml → verify 通过。**永远不要在手动修 frontmatter 之前跑 sync** |

---

> 实战案例: 2026-05-15 EPIC-004 Phase 0/1/2 完成后，11 个 Story + 3 SPEC + EPIC + report 共 16 个文档全部停留在 draft 状态。用本清单 + execute_code 一次同步完成。
