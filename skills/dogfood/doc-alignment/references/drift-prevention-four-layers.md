# 四层防御体系 — 文档漂移预防参考

> **来源**: doc-alignment skill v4.0 §2
> **基于**: hermes-cap-pack v1.0.1 发布漂移分析 + BMAD Method 声明式依赖模式
> **目的**: 每个项目初始化时安装此模板

## 四层架构

```
第 1 层: SSoT 定义 ── 每个数据项指定唯一权威来源
第 2 层: pre-commit 漂移脚本 ── git hook 自动检查
第 3 层: CI 门禁 ── GitHub Actions 兜底
第 4 层: 提交模板提醒 ── .gitmessage 心理提醒
```

## 第 1 层: SSoT 定义模板

在项目 `docs/DATA-AUTHORITY.md` 中定义：

```markdown
# 数据权威来源定义

| 数据项 | SSoT (权威来源) | 派生文件 |
|:-------|:---------------|:---------|
| 版本号 | `pyproject.toml` | README, project-report.json, PANORAMA |
| 测试数 | `pytest --collect-only` (运行时) | README, project-report.json |
| EPIC 状态 | `docs/project-state.yaml` | project-report.json, EPIC.md |
| CLI 命令 | CLI help 输出 (运行时) | README, QUICKSTART, ADAPTER_GUIDE |
| Python 版本 | `pyproject.toml` | README, project-report.json |
| 依赖列表 | `pyproject.toml` | README, project-report.json |
```

## 第 2 层: pre-commit 脚本模板

在 `scripts/pre-push.sh` 中增加：

```bash
check_doc_consistency() {
    local errors=0

    # 1. 版本号一致性 (SSoT: pyproject.toml)
    if [ -f pyproject.toml ]; then
        PYPROJ_VER=$(grep "^version" pyproject.toml | grep -oP '\d+\.\d+\.\d+')
        for f in README.md docs/project-report.json docs/project-state.yaml; do
            [ ! -f "$f" ] && continue
            FVER=$(grep -oP '\d+\.\d+\.\d+' "$f" | head -1)
            if [ "$PYPROJ_VER" != "$FVER" ]; then
                echo "❌ $f: 版本 $FVER ≠ SSoT $PYPROJ_VER"
                errors=$((errors+1))
            fi
        done
    fi

    # 2. 测试数一致性 (SSoT: pytest)
    if [ -f pyproject.toml ] && command -v pytest &>/dev/null; then
        ACTUAL=$(python -m pytest --collect-only -q 2>&1 | tail -1 | grep -oP '\d+')
        for f in README.md; do
            [ ! -f "$f" ] && continue
            DOC_TEST=$(grep -m1 '测试\|test' "$f" | grep -oP '\d+(?= ✅|\s+tests?)')
            if [ -n "$DOC_TEST" ] && [ "$ACTUAL" != "$DOC_TEST" ]; then
                echo "❌ $f: 测试数 $DOC_TEST ≠ 实际 $ACTUAL"
                errors=$((errors+1))
            fi
        done
    fi

    # 3. EPIC 状态一致性 (SSoT: project-state.yaml)
    if [ -f docs/project-state.yaml ] && [ -f docs/project-report.json ]; then
        python3 -c "
import json, yaml, sys
report = json.load(open('docs/project-report.json'))
state = yaml.safe_load(open('docs/project-state.yaml'))
state_epics = dict()
for k, v in state.get('entities', {}).get('epics', {}).items():
    state_epics[k] = v['state'] if isinstance(v, dict) else ''
report_epics = {e['id']: e['status'] for e in report.get('epics', [])}
errs = [f'{eid}: SSoT={s_state} vs report={s_report}'
        for eid, s_state in state_epics.items()
        if (s_report := report_epics.get(eid)) and s_state != s_report]
sys.exit(len(errs))
" 2>/dev/null && echo "✅ EPIC 状态一致" || { echo "❌ EPIC 状态不一致"; errors=$((errors+1)); }
    fi

    # 4. CLI 路径一致性（检查是否还有旧路径残留）
    if grep -rq 'scripts\.cli\.main' docs/ 2>/dev/null; then
        echo "❌ 有文件仍引用旧的 scripts.cli.main"
        grep -rl 'scripts\.cli\.main' docs/
        errors=$((errors+1))
    fi

    if [ "$errors" -gt 0 ]; then
        echo "🔴 文档一致性: $errors 个漂移，请修复后再提交"
        return 1
    fi
    echo "✅ 文档一致性检查通过"
    return 0
}
```

## 第 3 层: CI 门禁模板

在 `.github/workflows/ci.yml` 中增加：

```yaml
  doc-consistency:
    name: 📋 Doc Consistency Gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Check version consistency
        run: |
          PYPROJ_VER=$(grep "^version" pyproject.toml | grep -oP '\d+\.\d+\.\d+')
          for f in README.md docs/project-report.json docs/project-state.yaml; do
            [ ! -f "$f" ] && continue
            FVER=$(grep -oP '\d+\.\d+\.\d+' "$f" | head -1)
            [ "$PYPROJ_VER" != "$FVER" ] && echo "❌ $f: $FVER" && exit 1 || echo "✅ $f: $FVER"
          done
      - name: Check test count
        run: |
          ACTUAL=$(python -m pytest --collect-only -q 2>&1 | tail -1 | grep -oP '\d+')
          echo "✅ Tests: $ACTUAL"
      - name: Check CLI path consistency
        run: |
          ! grep -rq 'scripts\.cli\.main' docs/ 2>/dev/null || \
            { echo "❌ Old CLI path found"; grep -rl 'scripts\.cli\.main' docs/; exit 1; }
          echo "✅ CLI paths consistent"
```

## 第 4 层: 提交模板

在 `.gitmessage` 或 `COMMIT_EDITMSG` 模板中：

```
# === 提交前检查清单 ===
# □ SSoT 更新了吗？
#   - 版本: pyproject.toml（改这里）
#   - EPIC 状态: project-state.yaml（改这里）
#   - 其他文件从 SSoT 同步
# □ 旧 CLI 路径清除了吗？(scripts.cli.main → skill_governance.cli.main)
# □ 测试数同步了吗？（README/project-report）
# □ CHANGELOG 更新了吗？
```

## 安装命令

```bash
# 1. 创建 DATA-AUTHORITY.md
cp this-file.md docs/DATA-AUTHORITY.md

# 2. 启用 pre-commit 检查
#    将 check_doc_consistency() 加入 scripts/pre-push.sh

# 3. 启用提交模板
git config commit.template .gitmessage
