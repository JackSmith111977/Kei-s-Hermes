# 💻 能力包提取命令速查 (Session Reference)

> 从 2026-05-14 实战中提取的可复用命令。

## 技能盘点

```bash
# 查看某类 skill
ls -d ~/.hermes/skills/<category>/*/

# 查看复合 skill 结构
ls ~/.hermes/skills/<name>/

# 确认 SKILL.md 存在
ls ~/.hermes/skills/<category>/<name>/SKILL.md
```

## 批量复制

```python
from pathlib import Path
import shutil

skills = { 'name': Path.home() / '.hermes/skills/<category>/<name>' }
dest = Path('packs/<pack-name>/SKILLS')
dest.mkdir(parents=True, exist_ok=True)

for name, src in skills.items():
    d = dest / name
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src / 'SKILL.md'), str(d / 'SKILL.md'))
```

## Schema 验证

```bash
python3 -c "
import json, yaml
with open('schemas/cap-pack-v2.schema.json') as f: schema = json.load(f)
with open('packs/<name>/cap-pack.yaml') as f: pack = yaml.safe_load(f)
import jsonschema
jsonschema.validate(instance=pack, schema=schema)
print(f'✅ {len(pack[\"skills\"])} skills')
"
```

## project-report.json 更新模式

```python
# 四个必须改的地方:
# 1. architecture.modules → 新增模块条目
# 2. epics[EPIC-003].stories → 新增 STORY
# 3. overview_cards → 能力包数 +1
# 4. info_table → 覆盖百分比更新
```

## 项目状态更新

```bash
# 查看当前状态
python3 scripts/project-state.py status

# 手动修改 project-state.yaml 中:
# - entities.epics.EPIC-003.story_count++
# - entities.epics.EPIC-003.completed_count++
# - entities.stories 新增条目
```

## 批量提取高效模式

当用户只说"继续"时，无需额外确认，直接按 Phase 顺序提取下一个模块。

```bash
# 快速检查 EPIC 模块定义
grep -A1 '<module>' docs/EPIC-003-module-extraction.md

# 检查源技能存在性与结构
for skill in skill-a skill-b skill-c; do
    echo "=== $skill ==="
    ls ~/.hermes/skills/*/"$skill"/SKILL.md 2>/dev/null || echo "❌ 未找到"
done
```

## 经验文件批量创建模式

每个模块统一创建 4 个 experiences，命名规则 `<skill>-<topic>.md`：

```bash
# 创建空的 experiences（手动填充）
touch EXPERIENCES/{first-pitfall.md,second-pitfall.md,third-topic.md,fourth-topic.md}
```

## 项目文件更新三剑客 PLUS（强制）

```bash
# 每次提取后必须更新以下四个文件：
# 1. PROJECT-PANORAMA.html — KPI 卡片 + 能力包卡片 + 剩余模块行
# 2. docs/EPIC-003-module-extraction.md — 模块表 ✅ 标记
# 3. docs/plans/EPIC-003-comprehensive-roadmap.md — 全景表 + Story 状态
# 4. 🆕 运行提取完成仪式（自动更新 project-state.yaml + Story doc）
python3 scripts/complete-extraction.py <module>
```

## 推送前门禁（🆕）

```bash
bash scripts/pre-push.sh
# Gate 1: README 对齐
# Gate 2: 项目状态一致性
# Gate 3: 交叉引用完整性
# Gate 4: YAML 语法
```

## CI 失败恢复

```bash
# 详见 references/ci-failure-recovery.md
# 常见修复:
python3 scripts/project-state.py sync   # 状态不一致
# 或用 unified tool:
python3 scripts/complete-extraction.py --all  # 批量修复所有待完成
```

## Commit 信息模板（批量）

```
feat: <module> 能力包提取 (N skills)

覆盖率 X%→Y% (A/17→B/17)
新增模块: <module> — <简短描述>
项目报告同步更新
```
