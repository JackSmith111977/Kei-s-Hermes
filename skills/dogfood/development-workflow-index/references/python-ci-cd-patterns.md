# Python CI/CD Setup Patterns

> 快速参考：为 Python 项目创建 GitHub Actions CI/CD 流水线的通用模式

## 标准 CI 流水线

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

permissions:
  contents: read

jobs:
  test:
    name: pytest (${{ matrix.python-version }})
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 需要完整历史用于 setuptools-scm
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: python -m pytest tests/ -q --tb=short

  lint:
    name: Ruff lint
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check src/ tests/
```

## setuptools-scm 版本管理

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
dynamic = ["version"]

[tool.setuptools_scm]
version_file = "src/my_package/_version.py"
```

**版本推导逻辑**：基于最近 git tag → 自动生成 `{tag}.dev{distance}+g{hash}`

## 常见问题排查

| 症状 | 根因 | 修复 |
|:-----|:-----|:-----|
| CI 中版本为 `0.0.0` | `fetch-depth: 0` 缺失 | 加上 `fetch-depth: 0` 让 setuptools-scm 能看到 tag |
| ruff 报 300+ 错误 | 项目未提前清理 lint | 先在本地跑 `ruff check --fix --unsafe-fixes .` |
| mypy 报 `python_version 3.8 not supported` | 最低版本是 3.10 | 改为 `python_version = "3.10"` |
| YAML 提交后 CI 不触发 | 语法错误或路径不对 | `python3 -c "import yaml; yaml.safe_load(open('file.yml'))"` 验证 |
| `pypi-publish` 失败 | 未配置 Trusted Publishing | 在 PyPI 配置 GitHub Trusted Publisher |
