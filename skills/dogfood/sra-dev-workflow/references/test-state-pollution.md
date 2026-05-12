# 测试文件间全局状态污染调试记录

> 2026-05-12 实战记录 — SRA v2.0.0 Release CI 失败调试

## 背景

SRA v2.0.0 的 Release CI 在 `test_init_default_config` 测试中失败：

```
tests/test_daemon.py:50: in test_init_default_config
    assert daemon.config["http_port"] == 8536
E   assert 8080 == 8536
```

单独运行该测试通过 (`python -m pytest tests/test_daemon.py -q`)，但运行整个测试套件时失败 (`python -m pytest tests/ -q`)。

## 调试流程

### Step 1: 确认失败类型

从 `gh run list` 看到 Release CI 仅运行 46s 就失败了——远短于正常时长（正常~10min），提示测试阶段失败。

```bash
gh run view <run-id> --log --job build | grep -i "FAILED\|error"
# 输出: FAILED tests/test_daemon.py::TestSRaDDaemonInit::test_init_default_config
```

### Step 2: 定位污染源

`test_init_default_config` 测试读取 `http_port` 得到了意外的 `8080`。这个值不在任何 `DEFAULT_CONFIG` 中（默认值是 `8536`）。排查所有含 `8080` 的测试文件：

```bash
grep -rn "8080" tests/ --include="*.py"
# 输出: tests/test_config.py:240: test_config = {"http_port": 8080}
```

找到 `test_env_precedence_over_file` 测试写入了 `http_port: 8080` 的配置文件。

### Step 3: 确认测试顺序依赖

```bash
# 单独运行 ✅ 通过
python -m pytest tests/test_daemon.py::TestSRaDDaemonInit::test_init_default_config -q

# 按字母序运行 ❌ 失败
python -m pytest tests/test_config.py tests/test_daemon.py -q
```

### Step 4: 检查 pytest tmp_path 残留

```bash
find /tmp/pytest-of-*/ -name "config.json" -exec cat {} \;
# 输出: {"http_port": 8080}{"http_port": 8080}{"http_port": 8080}
```

pytest 保留最近的 tmp_path 目录（`tmp_path_retention_count=3`）且不清空文件（`tmp_path_retention_policy="all"`）。

### Step 5: 验证模块变量污染

```python
from skill_advisor.runtime import config as cfg_module
print(cfg_module.SRA_HOME)     # → 残留的 tmp_path
print(cfg_module.CONFIG_FILE)  # → 残留的 tmp_path/config.json
```

## 根因分析

```
污染链
═══════
test_env_precedence_over_file (test_config.py)
  │
  ├─ 修改 cfg_module.SRA_HOME     → tmp_path     （← 未恢复）
  ├─ 修改 cfg_module.CONFIG_FILE  → tmp_path/config.json （← 未恢复）
  ├─ 修改 cfg_module.CONFIG_SCHEMA → tmp_path/config.schema.json （← 未恢复）
  │
  ├─ pytest 保留 tmp_path 文件（retention_policy=all）
  │   └─ config.json 带 http_port=8080 持续存活
  │
  └─ test_init_default_config (test_daemon.py)
      └─ SRaDDaemon() → load_config() → 读到残留的 config.json
      └─ assert http_port == 8536 → ❌ 得到 8080
```

## 修复

给 `test_env_precedence_over_file` 添加 `try/finally` 恢复原始值：

```python
def test_env_precedence_over_file(self, mock_sra_home):
    from skill_advisor.runtime import config as cfg_module
    orig_home = cfg_module.SRA_HOME
    orig_file = cfg_module.CONFIG_FILE
    orig_schema = cfg_module.CONFIG_SCHEMA
    try:
        cfg_module.SRA_HOME = str(mock_sra_home)
        cfg_module.CONFIG_FILE = str(mock_sra_home / "config.json")
        cfg_module.CONFIG_SCHEMA = str(mock_sra_home / "config.schema.json")
        # ... 测试 ...
    finally:
        cfg_module.SRA_HOME = orig_home
        cfg_module.CONFIG_FILE = orig_file
        cfg_module.CONFIG_SCHEMA = orig_schema
```

## 预防检查清单

当编写需要修改模块级变量的测试时：

- [ ] 是否用 `try/finally` 恢复所有修改过的模块变量？
- [ ] 是否了解 pytest 的 `tmp_path` 保留策略（默认保留最近 3 次，不清空文件）？
- [ ] 测试文件按字母序运行时，前面的测试可能污染后面的——验证过排序依赖吗？
- [ ] 是否可以用 `unittest.mock.patch` / `mock.patch.dict` / `mock.patch.object` 替代直接修改变量？

## 相关工具命令速查

```bash
# 查看 pytest 的 tmp_path 保留策略
python -c "import pytest; help(pytest.Config) if hasattr(pytest, 'Config') else print('use: python -m pytest --help|grep tmp_path')"
python -m pytest --help 2>/dev/null | grep -A2 "tmp_path"

# 清空残留的 pytest tmp_path
rm -rf /tmp/pytest-of-*/

# 运行特定文件的测试，隔离污染
python -m pytest tests/test_daemon.py -q --tb=short -o "addopts="

# 重现测试顺序依赖
python -m pytest tests/test_config.py tests/test_daemon.py -q --tb=short -o "addopts="

# 检查当前模块变量的值
python -c "from skill_advisor.runtime import config as c; print(f'SRA_HOME={c.SRA_HOME}'); print(f'CONFIG_FILE={c.CONFIG_FILE}')"
```
