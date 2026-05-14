# CI 失败恢复速查

> 基于 hermes-cap-pack 项目实战经验。当 CI 变红时按此流程排查。

## 通用排查流程

```bash
# 1. 查看失败详情
gh run view <run-id> --log-failed 2>&1 | tail -80

# 2. 确认是哪个门禁失败
# 可能来源:
#   - validate-readme → README/pyproject 版本不一致
#   - project-state.py verify → 状态机漂移
#   - ci-check-cross-refs.py → 交叉引用断开
#   - pytest → 测试失败
```

## 常见失败模式

### 1. README/pyproject 版本不一致

**CI 输出**: `🔴 [blocking] 版本号一致性` + `版本不一致: README=X, pyproject.toml=Y`

**处理**:
```bash
# 哪个版本更新？README 反映里程碑，pyproject.toml 反映正式版本
grep 'version' README.md | head -1
grep 'version =' pyproject.toml

# 修复: 将较旧的一方同步到较新的一方
# 通常需同时更新 README 版本（头部）和 pyproject.toml 的 version 字段
```

**根因**: 提取模块时只改了 README，没同步 pyproject.toml，或反之。

### 2. project-state 状态不一致

**CI 输出**: `❌ 状态不一致 (N)` + 类似 `STORY X: YAML=implemented, DOC=approved 状态不一致`

**处理**:
```bash
# 一键同步: 从 SDD 文档状态覆盖 YAML
python3 scripts/project-state.py sync

# 验证
python3 scripts/project-state.py verify
```

**根因**: 提取模块时更新了 EPIC 文档和全景图，但 `docs/project-state.yaml` 状态机文件未同步。所有模块提取后必须执行 `project-state.py sync`（或使用 unified 工具 `scripts/complete-extraction.py`）。

### 3. 文档存在但 YAML 未注册

**CI 输出**: `SPEC X: 文档存在但 YAML 中未注册` 或 `STORY X: 文档存在但 YAML 中未注册`

**处理**: 同上，`project-state.py sync` 会自动注册缺失实体。

**根因**: 新增 Spec/Story 文档后未在 YAML 中注册实体项。

### 4. 交叉引用断裂

**CI 输出**: `ci-check-cross-refs.py` 报告引用指向不存在的文件或模块

**处理**:
```bash
python3 scripts/ci-check-cross-refs.py  # 查看断裂详情
# 通常是项目改名或模块合并后残留的旧引用
# 用 grep 查找旧名称并更新
```

**根因**: 模块合并后残留了对旧包名的引用。
