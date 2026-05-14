# SDD × 项目报告/状态机 集成指南 v2.0

> 2026-05-14 在 hermes-cap-pack 项目首次完整实现。
> SDD v3.6.0 起内置本文档描述的所有集成点。
>
> **v2.0 更新**:
> - ❌ `generate-project-report.py` 脚本已废弃（主人明确否定模板脚本方案）
> - ✅ 项目报告改用 `project-report-generator` skill 五阶段 LLM 驱动创作
> - ✅ 项目状态管理改用 `project-state-machine` skill 统一 YAML 中枢 + 脚本门禁

---

## 整体集成架构

```text
SDD Stage              项目报告 Phase                  状态机 Phase
─────────────────────────────────────────────────────────────────────
CLARIFY/RESEARCH       Phase 0: Reality Check         project-state.py status
    │                       │
    │                       ├── git log --oneline -30
    │                       ├── pytest --collect-only
    │                       └── project-state.py verify
    ▼
ARCHITECT/PLAN        (不涉及报告，专注架构)
    ▼
IMPLEMENT             Phase 1: 更新数据文件           project-state.py sync
    │                       │
    │                       ├── 编辑 project-report.json
    │                       └── 更新 Story 状态
    ▼
COMPLETE              Phase 2: 生成 HTML 报告         project-state.py sync → verify
    │                   (project-report-generator skill)
    │                       ├── skill_view + 五阶段创作
    │                       └── HTML 与 JSON 同 commit
    ▼
ARCHIVE               Phase 3: 验证漂移               project-state.py verify
                            │
                            ├── project-state.py verify (exit 0)
                            └── 漂移=0 → archive | 漂移>0 → 修复
```

---

## 三阶段具体命令

### Phase 0: Reality Check（每个任务开始前）

```bash
# 0.1 看代码最新动向
git log --oneline -30 | head -15

# 0.2 看测试是否真的通过
python -m pytest tests/ --collect-only -q

# 0.3 检测文档状态漂移（如有 project-state.yaml）
python3 scripts/project-state.py verify

# 0.4 检查关键文件
ls -la path/to/alleged-missing-file 2>/dev/null

# 0.5 检查版本号
grep "version" pyproject.toml
```

### Phase 1: IMPLEMENT 完后更新数据

编辑 `docs/project-report.json`：

| 场景 | 更新字段 |
|:-----|:---------|
| Story 完成 | `epics[].stories[].status = "implemented"` |
| 新增模块 | `architecture.module_table[]` 新增条目 |
| 测试增长 | `tests.passing` 和 `.total` 更新 |
| 版本升级 | `project.version` 更新 |

### Phase 2: 重新生成 HTML（project-report-generator skill）

```bash
# 加载 project-report-generator skill
skill_view(name='project-report-generator')
skill_view(name='web-ui-ux-design')
skill_view(name='visual-aesthetics')

# 按五阶段流程创建 HTML（非模板替换）
# Phase 0: 需求理解 + 加载设计基础
# Phase 1: 深度数据收集（读取 project-report.json + SQS DB + git）
# Phase 2: 叙事结构设计
# Phase 3: HTML 手工创作
# Phase 4: Review + 交付
# Phase 5: 反思迭代
```

确保 HTML + JSON + YAML 在**同一次 git commit** 中提交。

### Phase 3: 归档前验证

```bash
# 项目状态一致性验证（主门禁）
python3 scripts/project-state.py verify

# 输出：✅ 一致性验证通过 → 可归档
# 输出：🔴 状态不一致 → 先同步再归档
```

---

## cap-pack 项目实战记录（首个完整实现）

| 项目 | 文件 | 状态 |
|:-----|:-----|:----:|
| hermes-cap-pack | `docs/project-report.json` | ✅ v0.7.0, 3 Epics, 27 Stories, 101 测试 |
| hermes-cap-pack | `PROJECT-PANORAMA.html` | ✅ 自动生成 |
| hermes-cap-pack | `--verify` | ✅ 漂移=0 |

### 初始化命令（新项目参考）

```bash
# 1. 创建 project-report.json（记录项目元数据和报告数据）
touch docs/project-report.json
# 手动填充项目信息

# 2. 创建 project-state.yaml（统一状态机中枢）
# 参考 project-state-machine skill 的 references/yaml-schema-template.md
# touch docs/project-state.yaml
# 手动填充 Epics/Specs/Stories

# 3. 创建 project-state.py 管理脚本
cp ~/.hermes/skills/dogfood/project-state-machine/references/yaml-schema-template.md \
   docs/project-state.yaml
# 或手动编写（参考 project-state-machine skill）

# 4. 同步状态并验证
python3 scripts/project-state.py sync
python3 scripts/project-state.py verify

# 5. 提交
git add docs/project-report.json docs/project-state.yaml PROJECT-PANORAMA.html
git commit -m "docs: init project report + state machine"
```

---

## 状态机门禁规则（spec-state.py 转换）

| 转换 | 门禁 |
|:-----|:------|
| `complete` → `completed` | pytest 通过 + AC 验证通过 + doc-alignment Phase 1-2 完成 |
| `completed` → `archived` | doc-alignment Phase 3 验证通过 (`--verify` 漂移=0) |

---

## 常见问题

### Q: 项目没有 project-state.yaml 怎么办？

创建它。参考 `project-state-machine` skill 的 `references/yaml-schema-template.md`：
1. 列出所有 Epics 和它们的 Stories
2. 列出所有 Specs
3. 添加 Sprint 历史
4. 运行 `python3 scripts/project-state.py verify` 验证

### Q: project-state.py verify 状态不一致如何定位？

```bash
# 查看漂移详情
python3 scripts/project-state.py scan

# 自动同步
python3 scripts/project-state.py sync

# 再验证
python3 scripts/project-state.py verify
```
