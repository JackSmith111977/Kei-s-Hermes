# SRA v2.0.1 — 真实测试污染案例

## 背景

SRA (Skill Runtime Advisor) v2.0.0 Release CI 在 `test_daemon.py::TestSRaDDaemonInit::test_init_default_config` 阶段失败：
```
assert daemon.config["http_port"] == 8536
E   assert 8080 == 8536
```

## 症状

| 场景 | 结果 |
|:-----|:-----|
| 单独运行 `test_daemon.py` | ✅ 通过 (http_port=8536) |
| 先跑 `test_config.py` 再跑 `test_daemon.py` | ❌ 失败 (http_port=8080) |
| CI 全量测试 | ❌ 失败 |
| 本地开发环境 | ✅ 通过（顺序不同） |

## 根因分析

### 污染源代码

`tests/test_config.py::TestEnvOverride::test_env_precedence_over_file`:

```python
def test_env_precedence_over_file(self, mock_sra_home):
    from skill_advisor.runtime import config as cfg_module

    # ⚠️ 永久污染模块级变量！
    cfg_module.SRA_HOME = str(mock_sra_home)
    cfg_module.CONFIG_FILE = str(mock_sra_home / "config.json")
    cfg_module.CONFIG_SCHEMA = str(mock_sra_home / "config.schema.json")

    test_config = {"http_port": 8080}
    with open(cfg_module.CONFIG_FILE, "w") as f:
        json.dump(test_config, f)
    # ... 测试环境变量覆盖 ...
    # ⚠️ 没有恢复原始变量！
```

### 污染传播链

```
test_config.py 运行
  │
  ├─ 1. mock_sra_home fixture 创建 /tmp/pytest-xxx/.sra/
  ├─ 2. 修改 cfg_module.SRA_HOME → /tmp/pytest-xxx/.sra/
  ├─ 3. 写入 config.json → http_port=8080
  └─ 4. 测试结束，但模块级变量未恢复！
                        ↓
pytest 保留 tmp_path（默认策略: retention_count=3, retention_policy=all）
  └─ /tmp/pytest-xxx/.sra/config.json 仍存在！
                        ↓
test_daemon.py::test_init_default_config 运行
  ├─ 1. SRaDDaemon() → load_config()
  ├─ 2. load_config() 使用 cfg_module.CONFIG_FILE
  │     → /tmp/pytest-xxx/.sra/config.json（仍存在！）
  ├─ 3. 读到 http_port=8080
  └─ 4. assert 8536 == 8080 ❌ 失败
```

## 修复

添加 `try/finally` 恢复原始模块级变量：

```python
def test_env_precedence_over_file(self, mock_sra_home):
    from skill_advisor.runtime import config as cfg_module

    # 保存原始值
    orig_home = cfg_module.SRA_HOME
    orig_file = cfg_module.CONFIG_FILE
    orig_schema = cfg_module.CONFIG_SCHEMA

    try:
        cfg_module.SRA_HOME = str(mock_sra_home)
        cfg_module.CONFIG_FILE = str(mock_sra_home / "config.json")
        cfg_module.CONFIG_SCHEMA = str(mock_sra_home / "config.schema.json")

        # ... 测试逻辑 ...
    finally:
        # 恢复原始值
        cfg_module.SRA_HOME = orig_home
        cfg_module.CONFIG_FILE = orig_file
        cfg_module.CONFIG_SCHEMA = orig_schema
```

## 验证

修复后全量测试通过（313 passed，仅剩已知 flaky HTTP 测试）。

## 教训

1. **测试污染是"沉默的杀手"** — 仅在特定运行顺序下暴露
2. **pytest tmp_path 保留策略** 是隐形的污染放大器
3. **所有修改模块级变量的测试**必须恢复原始值
4. CI 中失败的跨文件测试链值得优先排查
