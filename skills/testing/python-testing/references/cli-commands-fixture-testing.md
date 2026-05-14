# CLI Command Testing with monkeypatch + tmp_path

> 当 CLI 命令内部引用模块级路径常量（`PROJECT_ROOT`, `SCHEMA_PATH`, `HERMES_HOME`）时，使用 monkeypatch 重定向路径 + tmp_path 创建临时文件系统。

## 适用场景

CLI 命令函数（如 `cmd_install`, `cmd_search`, `cmd_upgrade`）通常：
- 内部使用模块级 `PROJECT_ROOT` 和 `SCHEMA_PATH` 常量
- 读取 `packs/<name>/cap-pack.yaml` 等文件
- 写 `~/.hermes/installed_packs.json`
- 返回 `int` 状态码（0=成功, 1=失败）

## 测试模式

### 模式 A: monkeypatch + tmp_path 双 fixture

```python
@pytest.fixture
def project_root(tmp_path: Path, monkeypatch) -> Path:
    """模拟项目根目录，替换所有模块级路径常量"""
    root = tmp_path / "my-project"
    root.mkdir()

    # 创建必需目录结构
    (root / "schemas").mkdir()
    (root / "packs").mkdir()

    # 创建 schema 文件（parser 需要）
    with open(root / "schemas" / "cap-pack-v1.schema.json", "w") as f:
        json.dump({"type": "object", "required": ["name"]}, f)

    # 注入到 CLI 命令模块
    import scripts.cli.commands as cmds
    monkeypatch.setattr(cmds, "PROJECT_ROOT", root)
    monkeypatch.setattr(cmds, "SCHEMA_PATH", root / "schemas" / "cap-pack-v1.schema.json")

    return root


@pytest.fixture
def hermes_home(tmp_path: Path, monkeypatch) -> Path:
    """模拟 ~/.hermes/ 目录"""
    hh = tmp_path / ".hermes"
    hh.mkdir()
    (hh / "skills").mkdir()

    import scripts.cli.commands as cmds
    monkeypatch.setattr(cmds, "HERMES_HOME", hh)
    monkeypatch.setattr(cmds, "INSTALLED_PACKS_PATH", hh / "installed_packs.json")

    return hh
```

### 模式 B: 创建测试用 pack 目录 fixture

```python
@pytest.fixture
def demo_pack(project_root: Path) -> Path:
    """在 packs/ 中创建测试用的能力包"""
    pack_dir = project_root / "packs" / "demo-pack"
    pack_dir.mkdir()

    # cap-pack.yaml
    manifest = {
        "name": "demo-pack",
        "version": "2.0.0",
        "type": "capability-pack",
        "skills": [
            {"id": "skill-a", "path": "SKILLS/skill-a/SKILL.md", "description": "First skill"},
        ],
    }
    with open(pack_dir / "cap-pack.yaml", "w") as f:
        yaml.dump(manifest, f)

    # SKILLS/
    d = pack_dir / "SKILLS" / "skill-a"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nid: skill-a\n---\n# Skill A")

    return pack_dir
```

### 模式 C: 模拟已安装包状态

```python
@pytest.fixture
def installed_pack(hermes_home: Path) -> dict:
    """创建 installed_packs.json 模拟已安装状态"""
    data = {"demo-pack": {"version": "1.0.0", "skill_count": 2}}
    hermes_home.joinpath("installed_packs.json").write_text(json.dumps(data))
    return data
```

## 测试场景

### 1. 测试正常路径

```python
def test_search_match(project_root, demo_pack, capsys):
    exit_code = cmd_search("demo")
    assert exit_code == 0
```

### 2. 测试错误路径

```python
def test_remove_not_found(capsys):
    exit_code = cmd_skill_remove("nonexistent", "skill-a")
    assert exit_code == 1
```

### 3. 测试 dry-run 不修改状态

```python
def test_upgrade_dry_run_does_not_mutate(project_root, hermes_home, demo_pack, capsys):
    installed = {"demo-pack": {"version": "1.0.0"}}
    hermes_home.joinpath("installed_packs.json").write_text(json.dumps(installed))

    exit_code = cmd_upgrade("demo-pack", dry_run=True)
    assert exit_code == 0

    # 验证版本未被更新
    fresh = json.loads(hermes_home.joinpath("installed_packs.json").read_text())
    assert fresh["demo-pack"]["version"] == "1.0.0"
```

### 4. 测试回滚

```python
def test_rollback_on_failure(project_root, demo_pack, monkeypatch, capsys):
    def _broken_write(*args, **kwargs):
        return False
    import scripts.cli.commands as cmds
    monkeypatch.setattr(cmds, "_write_yaml_file", _broken_write)

    exit_code = cmd_skill_add("demo-pack", str(sample_skill_dir))
    assert exit_code == 1
    # 验证没有残留文件
    assert not (demo_pack / "SKILLS" / "tmp-skill").exists()
```

### 5. 端到端工作流

```python
def test_full_lifecycle(project_root, demo_pack, sample_skill, capsys):
    """add → list → update → remove"""
    assert cmd_skill_add("demo-pack", str(sample_skill)) == 0
    assert cmd_skill_list("demo-pack") == 0
    assert cmd_skill_update("demo-pack", "my-skill", str(sample_skill)) == 0
    assert cmd_skill_remove("demo-pack", "my-skill") == 0
```

## 陷阱

| 陷阱 | 症状 | 修复 |
|:-----|:-----|:-----|
| `monkeypatch` 修改非模块级属性 | `AttributeError` | 检查被修改属性是否存在于模块级命名空间 |
| 忘记创建 schema 文件 | `FileNotFoundError` | 在 fixture 中创建最小 schema |
| `tmp_path` 在不同 test 间共享状态 | 测试间污染 | 每个 fixture 用独立的 `tmp_path` 参数 |
| 未恢复 `monkeypatch.setattr` | 跨文件污染 | 使用 `monkeypatch` context manager（自动恢复） |
| `capsys` 读取 stdout 但命令写 stderr | 空输出 | 用 `capsys.readouterr().err` 或合并流 |

## 验证

```bash
python -m pytest tests/test_cli.py -v          # 单文件
python -m pytest tests/ -q                     # 全量
python -m pytest tests/ -q --co                # 带覆盖率
```
