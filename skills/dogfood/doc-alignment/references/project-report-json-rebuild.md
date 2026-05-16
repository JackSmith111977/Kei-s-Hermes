# 📋 project-report.json 全量重建指南

> **场景**: 当 project-report.json 与实际项目状态出现**系统性漂移**（版本/模块数/Epic 数/测试数等多处不一致）时，增量更新不足以修复，需要全量重建。
>
> **典型信号**:
> - 版本号落后 1+ 个版本
> - 模块数远少于实际（如 8 个声称 vs 17 个实际）
> - 缺失完整的 Epic（如 EPIC-004 完全不存在）
> - Story 完成率严重失真（如声称 0/7 但实际 8/8）
> - 测试文件列表包含已删除的文件

---

## 一、数据收集清单

重建前从以下 4 个真相来源收集数据：

### 1. 项目元数据 — project-state.yaml

```bash
grep "version:" docs/project-state.yaml    # 获取当前版本
grep "overall_state:" docs/project-state.yaml
grep "current_phase:" docs/project-state.yaml
```

**获取字段**: version, name, description, author, license, current_phase

### 2. 能力包清单 — packs/ 目录

```bash
for pack in packs/*/; do
    name=$(basename "$pack")
    skills=$(find "$pack/SKILLS" -name "SKILL.md" 2>/dev/null | wc -l)
    desc=$(grep "^description:" "$pack/cap-pack.yaml" 2>/dev/null | head -1 | sed 's/description: *//' | sed 's/^"//;s/"$//')
    echo "$name|$skills|$desc"
done
```

**获取字段**: 所有包的 name, skill_count, description

### 3. Epic/Story 状态 — project-state.yaml

```bash
python3 -c "
import yaml
with open('docs/project-state.yaml') as f:
    state = yaml.safe_load(f)
for eid, e in state['entities']['epics'].items():
    print(f'{eid}: {e[\"title\"]} — {e[\"completed_count\"]}/{e[\"story_count\"]} stories, state={e[\"state\"]}')
"
```

**获取字段**: 每个 Epic 的 id, name, status, stories 列表（含每个 story 的 id, name, status）

### 4. 测试计数 — pytest

```bash
python3 -m pytest scripts/tests/ --collect-only -q 2>&1 | grep "collected"
```

逐个文件计数：
```bash
for f in scripts/tests/test_*.py; do
    count=$(grep -c "^    def test_" "$f")
    echo "  $(basename $f): $count tests"
done
```

**获取字段**: passing, total, files 列表（name, tests, passing）

### 5. Sprint 历史 — project-state.yaml + git log

```bash
grep -B1 -A5 "^  sprint-" docs/project-state.yaml
git log --oneline --since="2026-05-12"
```

**获取字段**: 每个 sprint 的 date, summary, tests_added, stories_completed

### 6. 架构模块 — 工具脚本清单

```bash
for f in scripts/*.py; do
    grep "^class\|^def main\|^def cmd_" "$f" 2>/dev/null | head -3
    echo "---"
done
```

**获取字段**: module 名, file 路径, desc, 关键 methods

---

## 二、重建流程

### Step 1: 创建 JSON 结构

用 Python 脚本（而非手写）生成，避免 JSON 格式错误：

```python
import json

report = {
    "project": {
        "version": "0.9.1",  # ← 从 project-state.yaml
        "overview_cards": [...],
        "info_table": [...]
    },
    "architecture": {
        "layers": [
            {
                "name": "Layer 3 — 能力包层",
                "modules": [...]  # ← 从 packs/ 目录
            },
            {
                "name": "Layer 2 — 工具层",
                "modules": [...]  # ← 从 scripts/ 目录
            },
            {
                "name": "Layer 1 — 基础设施层",
                "modules": [...]  # ← docs, packs, schemas, reports, .github
            }
        ],
        "module_table": [...]  # ← 关键工具脚本的 module/file/desc/methods
    },
    "epics": [...],  # ← 从 project-state.yaml
    "tests": {
        "passing": 141,
        "total": 141,
        "files": [...]  # ← 从 pytest 收集
    },
    "sprint_history": [...]  # ← 从 project-state.yaml + git log
}

with open('docs/project-report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
```

### Step 2: 验证

```bash
# 1. JSON 语法有效
python3 -c "import json; json.load(open('docs/project-report.json'))"

# 2. 版本对齐
grep version pyproject.toml
grep version docs/project-state.yaml

# 3. 测试数对齐
python3 -m pytest scripts/tests/ --collect-only -q | grep collected

# 4. Epic 数对齐
grep "epic:" docs/project-state.yaml | wc -l
```

---

## 三、常见陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **module_table 缺少 module/file/desc/methods** | HTML 报告渲染报 KeyError | 每个条目都必须包含这 4 个字段 |
| **Sprint 历史不完整** | 项目报告缺少关键里程碑 | 对照 project-state.yaml 的 sprint 列表逐一核对 |
| **测试文件列表包含已删除的文件** | pytest 总数与实际不匹配 | 用 `pytest --collect-only` 确认实际文件列表 |
| **version 只更新了一处** | project-report.json vs pyproject.toml 不同步 | 两处都改，运行 verify 检查 |
| **Epic 的 Story 状态与 project-state.yaml 不一致** | 报告显示错误完成率 | 按 project-state.yaml entities.stories 的数据填写，不要凭记忆 |

---

## 四、增量 vs 全量决策树

```
project-report.json 需要更新吗？
    ↓
是 → 检查漂移程度
    ↓
    ├── 仅版本号 + 少数 Story 状态 → 🔄 增量 patch
    │   修改 version + 对应 stories[].status
    │
    ├── 缺少模块/Epic + 版本落后 → 🔄 局部重建
    │   追加 modules[] + epics[] + sprint_history[]
    │
    └── 多处不一致（版本/模块数/Epic/测试数/文件列表） → 🏗️ 全量重建
        按本指南 Step 1 → 2 顺序执行
```

---

## 五、实战案例

**项目**: hermes-cap-pack (2026-05-15)
**漂移程度**: 🔴 重度（版本 0.9.0→0.9.1, 模块 8→17, 缺少 EPIC-004, EPIC-002 完成率 0/7→8/8）
**修复方式**: 全量重建
**数据来源**: project-state.yaml + pytest + packs/ 目录 + git log
**耗时**: ~15 分钟（收集数据 + 编写 JSON + 验证）
**验证结果**: `project-state.py verify` ✅ 4 Epics, 15 Specs, 49 Stories 全一致
