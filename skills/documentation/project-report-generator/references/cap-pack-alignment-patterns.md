# 🎯 Cap-Pack 文档对齐模式

> **场景**: 对 hermes-cap-pack 项目做全量文档对齐时，需要更新 3 个文件 + 验证。
> **来源**: 2026-05-16 实战：commit `0311f2d` — 7 files, +1611/-244
> **相关 skill**: `project-report-generator` Phase 6（增量更新模式）

---

## 一、三文件对齐清单

每次文档对齐必须同步以下三个文件，顺序不可颠倒：

```text
Step 1: docs/project-report.json    (数据源 — 真相来源)
Step 2: PROJECT-PANORAMA.html        (数据展示 — 从 JSON 推导)
Step 3: docs/project-state.yaml      (状态机 — 由 JSON 同步)
  └─ 验证: python3 scripts/project-state.py verify
  └─ 提交: git add + commit (四文件打包)
```

### 1.1 project-report.json — 六处检查点

| 检查点 | 常见漂移 | 修复方式 |
|:-------|:---------|:---------|
| `epics[].stories[].status` | EPIC-001 的 10 个 Story 停留在 `draft` | 批量替换 `draft`/`implemented` → `completed` |
| `epics[]` 缺 EPIC | 旧报告不含 EPIC-004/005 | 追加故事数组 |
| `sprint_history[]` | 时间线停在 Sprint 6，缺 7/8/9 | 追加最新 Sprint |
| `overview_cards` | Stories 数「30+」、Sprints 数「6」 | 同步更新 |
| `info_table` | Epics/Specs 统计过期 | 从 `epics` 重新计数 |
| `architecture.layers` | Layer 1 docs 数量「4 Epics/15 Specs」 | 更新为「5 Epics/16 Specs」 |

### 1.2 PROJECT-PANORAMA.html — 八处检查点

| 检查点 | 常见漂移 | 修复方式 |
|:-------|:---------|:---------|
| 页面标题版本号 | `v0.9.0 → v0.9.1` | 字符串替换 |
| Version badge | 同标题 | 字符串替换 |
| KPI Stories 值 | `30+ → 53` | 替换数字 |
| KPI Epics/Specs 子标题 | `3 Epics · 11 Specs` | 更新计数 |
| KPI Sprints 值 + 日期范围 | `6 → 9`, `05-14 → 05-16` | 替换 |
| §3 Epic 卡片 | 进度条百分比、状态标签、story grid 缺失 | 详见下方 §二 |
| §4 Sprint 时间线 | 缺少最新 Sprint | 追加 tl-item |
| §8 文档统计 | Epics/Specs/Stories/Sprints 数字 | 同步 JSON |

### 1.3 project-state.yaml — 两处检查点

| 检查点 | 常见漂移 | 修复方式 |
|:-------|:---------|:---------|
| `entities.epics.EPIC-005` 的 `spec_count`/`story_count` | 为 0 但实际已有 SPEC-5-1 | `yaml.dump` 更新 |
| `entities.specs.SPEC-5-1` 的 `stories` 列表 | 新建 SPEC 后未注册 | 追加 story ID 列表 |

---

## 二、Epic 卡片漂移模式

### 模式 A：Story 状态标签错误

HTML 中 `story-item` 元素的 class 决定了颜色：
- `story-item done` = 绿色（已完成）
- `story-item wip` = 黄色（进行中）
- `story-item` (无 class) = 灰色（未开始）

**典型错误**: EPIC-002 的 6 个灰色 Story 实际已实现完成。
**修复**: 将所有灰色/黄色的 class 替换为 `done`。

### 模式 B：进度条百分比错误

```html
<!-- 错误: 30% -->
<div class="progress-fill" style="width:30%"></div>
<!-- 正确: 100% -->
<div class="progress-fill" style="width:100%"></div>
```

**典型错误**: EPIC-002 的进度条显示 30% 但 8/8 已完成。
**修复**: 用 `完成数/总数 × 100` 计算百分比。

### 模式 C：Story 网格不完整

HTML 中的 story-grid 可能遗漏了部分 story。在 hermes-cap-pack 中：

| EPIC | 应有 Story 数 | 常见遗漏 |
|:-----|:-------------:|:---------|
| EPIC-002 | 8 | STORY-2-2-2/3/4, STORY-2-3-1/2, STORY-2-4-1 |
| EPIC-003 | 13 | STORY-3-8 到 STORY-3-13 |
| EPIC-004 | 8 | ⚠️ 整个 EPIC 卡片缺失 |
| EPIC-005 | 4 | ⚠️ 整个 EPIC 卡片缺失 |

**一次性添加的策略**：
1. 找到 EPIC-003 的 story-grid 尾部
2. 使用 HTML 字符串替换插入 EPIC-004 + EPIC-005 的完整 epic-card 块

---

## 三、验证方法

对齐完成后，运行以下验证：

```bash
# 1. 状态机一致性
python3 scripts/project-state.py verify
# exit 0 = 通过，exit 1 = 有漂移

# 2. HTML 关键内容检查
python3 -c "
with open('PROJECT-PANORAMA.html') as f:
    html = f.read()
assert 'v0.9.1' in html, '版本号不对'
assert 'EPIC-005' in html, 'EPIC-005 缺失'
assert '53 Stories' in html or '53 stories' in html, 'Story 数不对'
print('✅ HTML 验证通过')
"

# 3. Git 状态确认
git status --short
# 应仅显示三文件变更 + 新文件
```

---

## 四、实战参考

| 项目 | 值 |
|:-----|:----|
| 对齐日期 | 2026-05-16 |
| Git commit | `0311f2d` |
| 变更统计 | 7 files · +1611/-244 |
| 漂移类型 | Story 状态(×10) + Epic 缺失(×2) + Sprint 缺失(×3) + KPI 过期(×5) |
| 耗时 | ~15 min (含 HTML 增量替换 + JSON 编辑 + 验证 + commit) |
