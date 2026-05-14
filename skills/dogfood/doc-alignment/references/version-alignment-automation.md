# 版本号自动对齐 — bump-version.py sync

> **问题**: `pyproject.toml` 更新版本号后，README.md 和 project-state.yaml 的版本号不同步 → validate-readme.py 报错

## 方案

`bump-version.py` 扩展为全文档版本同步引擎：

```bash
# 版本号 bump + 全文档同步（三步合一）
python3 scripts/bump-version.py patch    # Story / Debug 更新
python3 scripts/bump-version.py minor    # Spec 更新
python3 scripts/bump-version.py major    # Epic 更新

# 仅同步不 bump（修复漂移）
python3 scripts/bump-version.py sync
```

## 同步目标

| 文件 | 匹配模式 | 示例 |
|:-----|:---------|:------|
| `pyproject.toml` | `version = "x.y.z"` | `version = "0.8.0"` |
| `README.md` | `**版本**：\`x.y.z\`` | `**版本**：\`0.8.0\`` |
| `README.md` | 目录树中的 `vx.y.z` | `v0.8.0` |
| `docs/project-state.yaml` | `version: x.y.z` | `version: 0.8.0` |

## 扩展新的同步目标

修改 `scripts/bump-version.py` 中的 `VERSION_SYNC_TARGETS` 列表：

```python
VERSION_SYNC_TARGETS = [
    {
        "path": "README.md",
        "patterns": [
            (r'(\*\*版本\*\*：)`[\d\.]+`', r'\g<1>`{version}`'),
        ],
    },
    {
        "path": "docs/project-state.yaml",
        "patterns": [
            (r'^(  version: )[\d\.]+', r'\g<1>{version}'),
        ],
    },
    # 添加更多文件...
]
```

## 集成到工作流

1. **在 bump 流程中自动执行** — `bump-version.py patch|minor|major` 内部调用 `sync_all_versions()`
2. **作为 CI check** — `validate-readme.py` 的 `check_version_consistency()` 自动检测版本漂移
3. **一键修复** — `validate-readme.py --fix` 调用 `bump-version.py sync` 自动对齐

## 实战效果

之前需要手动修改 3 个文件（pyproject.toml + README.md + project-state.yaml），现在一个命令搞定。
