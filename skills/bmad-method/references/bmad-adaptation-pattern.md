# BMad 适配模式 — 无 _bmad 基础设施的项目

> **场景**：项目没有 `_bmad/` 目录、`sprint-status.yaml`、`customize.toml` 等 BMad 工作流基础设施
> **原则**：结构化流程的精神比基础设施更重要

---

## 判断标准

| 项目状态 | 推荐路径 |
|:---|:---|
| 有 `_bmad/` 目录 + `sprint-status.yaml` | ✅ 走完整 BMad 流程（`create-story → dev-story → code-review`） |
| 无 `_bmad/` 但有 Epic/Story 文档 | ✅ **简化 BMad**：`todo` 分解 → 逐个实施 → 测试 → 一致性检测 |
| 无 Epic 也无基础设施 | ⚡ bmad-quick-dev（需先确定需求范围） |

---

## 简化 BMad 流程

### Step 1: 确认 Story 范围

从 Epic 文档中提取当前 Story 的：
- 验收标准（Acceptance Criteria）
- 实现文件清单
- 依赖关系

### Step 2: 用 `todo` 工具分解任务

```python
todo(todos=[
    {"content": "子任务 1 — 具体可执行", "id": "s1", "status": "pending"},
    {"content": "子任务 2 — 具体可执行", "id": "s2", "status": "pending"},
])
```

### Step 3: 逐个实施（红-绿-重构）

```
子任务 → 写测试(红) → 实现(绿) → 重构 → 验证
```

### Step 4: 全量测试

```bash
python3 -m pytest tests/ -v
```

### Step 5: 一致性检测

加载 `commit-quality-check` skill 执行一致性检测：
- 安全红线（硬编码密码/Token）
- 文档一致性
- 版本一致性
- 变更范围纯净

### Step 6: 更新 Story 状态

在 Epic 文档中标记 Story 完成状态。

---

## 关键区别

| 维度 | 完整 BMad | 简化 BMad |
|:---|:---|:---|
| Story 文件 | `{implementation_artifacts}/{story_key}.md` | 直接在 Epic 文档中标记 |
| 进度追踪 | `sprint-status.yaml` | `todo` 工具 + Epic 文档状态 |
| Code Review | `bmad-code-review` | 手动 code review 或跳过（小改动） |
| 一致性检测 | `commit-quality-check` | 同样执行 ✅ |
| Retrospective | `bmad-retrospective` | 可选 |
