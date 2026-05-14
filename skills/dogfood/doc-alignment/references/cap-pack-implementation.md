## hermes-cap-pack 项目 — doc-alignment 首个完整实现

### 项目概况

| 项目 | 值 |
|:-----|:----|
| 路径 | `~/projects/hermes-cap-pack/` |
| 版本 | v0.7.0 |
| 数据文件 | `docs/project-report.json` |
| HTML 报告 | `PROJECT-PANORAMA.html` |
| Epic/Story 数 | 3 Epics, 27 Stories, 19 implemented |
| 测试 | 101 passing |

### 数据结构

`project-report.json` 包含以下主要部分：
- `project` — 项目元信息 + overview_cards + info_table
- `architecture` — 三层架构 + module_table（模块/文件/描述/方法）
- `cli_commands` — CLI 命令列表
- `epics` — Epic 列表，每个含 stories（id/name/status）
- `tests` — 测试统计 + 按文件分组
- `sprint_history` — Sprint 迭代记录

### module_table 格式要求

HTML 生成器期望的格式（与模板不同——已根据实际生成器代码修正）：

```json
{
  "module": "模块名称",
  "file": "相对路径",
  "desc": "描述文本（支持含行数）",
  "methods": ["方法1", "方法2"]
}
```

### 验证结果

```bash
python3 ~/.hermes/scripts/generate-project-report.py \
    --data docs/project-report.json --verify
# ✅ 数据与代码状态一致
```

### 生命周期状态

当前处于 SDD Sprint 状态，每次 Story 完成后三步：

1. 编辑 `docs/project-report.json`（更新 story status / tests）
2. 重新生成 `PROJECT-PANORAMA.html`
3. `--verify` 确认漂移=0

### 参考

- SDD 集成协议：`~/.hermes/skills/dogfood/sdd-workflow/references/sdd-doc-alignment-integration.md`
- HTML 生成器：`~/.hermes/scripts/generate-project-report.py`
- JSON 模板：`~/.hermes/skills/dogfood/doc-alignment/references/project-report-template.json`
