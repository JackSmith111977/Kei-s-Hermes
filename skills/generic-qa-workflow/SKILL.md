---
name: generic-qa-workflow
description: 通用 QA 工作流 — 项目无关的 L0-L4 五层质量门禁体系。任何 Python 项目都能直接使用，与 generic-dev-workflow 互补。覆盖测试分类、门禁决策、回归预防、适配指南。
version: 1.0.0
triggers:
  - qa
  - quality
  - 质量
  - 质量门禁
  - 测试
  - 测试分类
  - 回归
  - 冒烟测试
  - 质量检查
  - 通用 qa
  - 通用质量
  - qa gate
  - quality gate
  - 测试覆盖
  - 质量报告
  - 测试策略
author: Emma (小玛)
license: MIT
metadata:
  hermes:
    tags:
      - workflow
      - qa
      - testing
      - generic
      - quality
    category: testing
    skill_type: workflow
    design_pattern: pipeline
depends_on:
  - generic-dev-workflow
  - test-driven-development
  - self-review
  - commit-quality-check
  - unified-state-machine
  - project-state-machine
---

# 🎯 通用 QA 工作流 v1.0

> **定位**: 项目无关的 L0-L4 五层质量门禁体系。任何 Python 项目都能直接使用，无需修改。
> **与相关 skill 的关系**:
> - `sra-qa-workflow` → SRA 项目的具体 QA 实现（含 SRA 特定路径和脚本）
> - `generic-dev-workflow` → 通用开发实施流程（本 skill 的上游：开发完 → QA 门禁）
> - **本 skill → 通用的质量门禁定义（项目拿来即用）**

---

## 〇、什么时候加载此 skill？

当主人说以下内容时，**必须**加载此 skill：

| 触发词 | 示例 |
|:-------|:------|
| QA / 质量 | 「做一下 QA」「质量检查」 |
| 测试分类 | 「测试怎么分类」「哪些测试该跑」 |
| 门禁 | 「设置质量门禁」「加个门禁」 |
| 回归 | 「做回归测试」「防止回归」 |
| 冒烟 | 「跑冒烟测试」「发布前检查」 |
| 通用 QA | 「通用的 QA 怎么做」 |

**加载后，按以下流程执行。**

---

## 一、L0-L4 五层质量门禁

```
L0 ─ 静态分析 ─── lint + format + type check + syntax
 │      pre-commit     🔴 阻塞: lint 错误 / 语法不兼容
 │
L1 ─ 单元测试 ─── pytest unit tests + 新代码测试覆盖
 │      per-commit     🔴 阻塞: 测试失败 / 测试退化
 │
L2 ─ 集成测试 ─── API + CLI + DB + 外部服务契约
 │      pre-merge      🔴 阻塞: 接口变更 / 契约断裂
 │
L3 ─ 系统测试 ─── 并发 + 压力 + 跨版本 + 性能基线
 │      pre-release    🔴 阻塞: 竞态 / 性能回退 / 版本不兼容
 │
L4 ─ 发布门禁 ─── 版本 + CHANGELOG + 构建 + 冒烟
        pre-publish    🔴 阻塞: 版本不对齐 / 构建损坏
```

---

## 二、各层详细门禁

### L0: 静态分析门禁

**时机**: 每次 git commit 前

**通用命令** (适用于任何 Python 项目):

```bash
# 🧹 Ruff lint（如果用 ruff）
ruff check .

# 或用 flake8
# flake8 .

# 🔤 类型检查（如果用 mypy）
mypy src/ || echo "⚠️ non-blocking (known issues)"

# 🔬 Python 语法兼容性（检查最低版本兼容）
python3 -c "
import ast, os, sys
errors = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git','__pycache__','build','dist','venv','.egg-info','node_modules')]
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root,f)) as fp:
                try: ast.parse(fp.read())
                except SyntaxError as e: errors.append((os.path.join(root,f), e))
if errors:
    for p,e in errors: print(f'❌ {p}: {e}')
    sys.exit(1)
print('✅ All .py files parseable')
"

# ✅ 测试数据完整性（如有 fixture 数据）
python3 -c "
import os
d = 'tests/fixtures'
if os.path.isdir(d):
    count = len([f for f in os.listdir(d) if f.endswith(('.json','.yaml','.yml'))])
    print(f'✅ {count} fixture data files')
else:
    print('⏭️  No fixture directory')
"
```

**适配指南**: 将 `src/` 替换为项目实际的源码目录。将 `tests/fixtures` 替换为实际测试数据目录。

---

### L1: 单元测试门禁

**时机**: 每次代码变更后

**通用命令:**

```bash
# 全量测试
python -m pytest tests/ -q --tb=short -o "addopts="

# 快速模式（跳过慢测试，如有 markers）
python -m pytest tests/ -m "not slow" -q --tb=short

# 新代码相关测试（假设新增 test_new_feature.py）
python -m pytest tests/test_new_feature.py -q --tb=long

# 测试总数基线检查（防止测试退化）
python -m pytest tests/ --collect-only -q 2>&1 | tail -1
```

**阻断条件**:
- ❌ 任何测试失败（已知 flaky 除外—需标记）
- ❌ 测试总数低于项目基线
- ❌ 新增代码没有对应测试

---

### L2: 集成测试门禁

**时机**: PR 合并前 / Feature 完成时

**分类模式**（按测试类型选择运行）:

| 类型 | 典型目录/文件 | 运行命令 |
|:-----|:-------------|:---------|
| API 测试 | `tests/test_api*.py`, `tests/integration/` | `pytest tests/test_api*.py -q` |
| CLI 测试 | `tests/test_cli*.py` | `pytest tests/test_cli*.py -q` |
| 数据库测试 | `tests/test_db*.py`, `tests/integration/` | `pytest tests/test_db*.py -q` |
| 契约测试 | `tests/test_contract*.py` | `pytest tests/test_contract*.py -q` |
| 外部服务 | `tests/test_adapter*.py` | `pytest tests/test_adapter*.py -q` |

**阻断条件**:
- ❌ 任何集成测试失败
- ❌ API 响应格式/状态码不符合契约
- ❌ CLI 子命令缺失或报错

---

### L3: 系统测试门禁

**时机**: 版本发布前 / 架构变更后

**通用命令**:

```bash
# 并发测试（如果项目有）
pytest tests/test_concurrency*.py -q --tb=short

# 性能基线（如果配置了 pytest-benchmark）
pytest tests/ --benchmark-only --benchmark-compare 2>/dev/null || echo "⏭️  No benchmark configured"

# 跨版本（项目配置了 tox/nox 时）
# tox  # 或
# nox -s tests
```

**阻断条件**:
- ❌ 并发测试暴露竞态条件
- ❌ 跨版本测试任一失败
- ❌ 性能回退超过基线 5%+

---

### L4: 发布门禁

**时机**: 版本 tag 推送前

**通用命令**:

```bash
# === 1. 版本一致性 ===
echo "=== Version ==="
python -c "from <package> import __version__; print(__version__)" 2>/dev/null || \
python -c "import importlib.metadata; print(importlib.metadata.version('<package>'))"
# 预期: 与 git tag 一致

# === 2. CHANGELOG 对齐 ===
echo "=== CHANGELOG ==="
grep -n "^## " CHANGELOG.md | head -10
# 预期: 当前版本有对应条目

# === 3. 构建验证 ===
echo "=== Build ==="
python -m build 2>&1 | tail -3
ls -la dist/

# === 4. 冒烟测试 ===
echo "=== Smoke Test ==="
python -c "
from <package> import __version__
from <package>.core import main
result = main()  # 或项目的核心入口
assert result is not None
print(f'✅ Smoke test passed (v{__version__})')
"

# === 5. 项目状态一致性 ===
echo "=== State ==="
python3 scripts/project-state.py verify 2>/dev/null || echo "⚠️  project-state.py not available (optional gate)"

# === 6. CI 状态检查 ===
echo "=== CI ==="
gh run list --limit 3 --json name,conclusion,headBranch 2>/dev/null || echo "⚠️  gh CLI not available"
```

**阻断条件**:
- ❌ 版本号与 git tag 不一致
- ❌ CHANGELOG 无当前版本条目
- ❌ 构建产物不完整
- ❌ 冒烟测试失败

---

## 三、QA 决策树

```
变更类型                             必需门禁
────────────────────────────────────────────────
🔧 修 Bug / 小重构     →  L0 + L1
✨ 新功能              →  L0 + L1 + L2
🏗️  架构变更/重构      →  L0 + L1 + L2 + L3
📦 版本发布            →  L0 + L1 + L2 + L3 + L4
```

### 决策函数 (可直接用)

```python
def select_qa_gates(change_type: str) -> list[str]:
    """返回需要通过的 QA 门禁列表"""
    return {
        "bugfix":  ["L0", "L1"],
        "feature": ["L0", "L1", "L2"],
        "arch":    ["L0", "L1", "L2", "L3"],
        "release": ["L0", "L1", "L2", "L3", "L4"],
    }.get(change_type, ["L0", "L1"])
```

---

## 四、集成到开发工作流

```
开发前                    开发中                    开发后
Phase 0.5                Phase 2.5                Phase 3.5
QA 影响评估               QA 逐任务验证             QA 门禁报告
  │                         │                        │
  ├─ 确定变更类型            ├─ L0: ruff/syntax       ├─ 运行所有必需门禁
  ├─ 查决策树 → 选门禁       ├─ L1: pytest -q          ├─ 生成 QA 报告
  └─ 输出: 门禁清单          └─ L2: 集成测试           └─ 阻断? → 修复
```

### Phase 0.5: QA 影响评估

```bash
# 通用 QA 评估函数
qa_assess() {
    case "$1" in
        bugfix)  echo "🔧 QA gates: L0+L1";;
        feature) echo "✨ QA gates: L0+L1+L2";;
        arch)    echo "🏗️  QA gates: L0+L1+L2+L3";;
        release) echo "📦 QA gates: L0+L1+L2+L3+L4";;
        *)       echo "❓ QA gates: L0+L1";;
    esac
}
```

### Phase 2.5: QA 逐任务验证

每个开发 Task 完成后：

```bash
# 1. L0 静态分析
ruff check .
python -m pytest tests/ --collect-only -q 2>&1 | tail -1

# 2. L1 单元测试
python -m pytest tests/ -q --tb=short -o "addopts="

# 3. L2（如涉及接口）
python -m pytest tests/test_api*.py tests/test_cli*.py -q --tb=short
```

### Phase 3.5: QA 门禁报告

```bash
# 根据变更类型运行门禁
GATES=$(python3 -c "print(','.join($(python3 -c "
matrix = {'bugfix':['L0','L1'],'feature':['L0','L1','L2'],'arch':['L0','L1','L2','L3'],'release':['L0','L1','L2','L3','L4']}
print(matrix.get('${CHANGE_TYPE}', ['L0','L1']))
")))")

echo "📋 Running QA gates: $GATES"
# 逐项运行
```

---

## 五、项目适配指南

### 新项目首次设置 QA 门禁

```bash
# Step 1: 确定项目结构
ls src/          # 源码目录
ls tests/        # 测试目录
cat pyproject.toml  # 项目配置

# Step 2: 检查已安装的工具
which ruff flake8 mypy pytest 2>/dev/null

# Step 3: 安装缺失工具
pip install ruff mypy pytest pytest-cov

# Step 4: 创建 pytest markers（在 conftest.py 中添加）
# 见本 skill 第六节

# Step 5: 运行 L0 基线
ruff check .
python -m pytest tests/ --collect-only -q

# Step 6: 记录测试基线数
python -m pytest tests/ --collect-only -q 2>&1 | grep -oP '\d+(?= collected)'
# → 设为 BASELINE_TEST_COUNT
```

### 配置模板

**pyproject.toml QA 配置**:

```toml
[tool.ruff]
target-version = "py39"  # 对齐最低版本
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B"]

[tool.pytest.ini_options]
addopts = "--tb=short -q"
testpaths = ["tests"]
markers = [
    "unit: 单元测试，快速执行",
    "integration: 集成测试",
    "slow: 慢速测试 (>5s)",
    "flaky: 已知不稳定测试",
    "smoke: 冒烟测试",
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
```

---

## 六、pytest Markers 定义

在项目的 `tests/conftest.py` 中添加：

```python
def pytest_configure(config):
    """注册 QA 工作流相关的 pytest markers"""
    config.addinivalue_line("markers", "unit: 单元测试，快速执行")
    config.addinivalue_line("markers", "integration: 集成测试，需多模块配合")
    config.addinivalue_line("markers", "slow: 慢速测试 (>5s)")
    config.addinivalue_line("markers", "flaky: 已知不稳定测试，失败不阻断")
    config.addinivalue_line("markers", "smoke: 冒烟测试，版本发布前验证")
    config.addinivalue_line("markers", "concurrency: 并发安全测试")
    config.addinivalue_line("markers", "benchmark: 性能基准测试")
```

按 QA 层级运行：

```bash
pytest -m "unit"                     # L1: 快速单元测试
pytest -m "integration"              # L2: 集成测试
pytest -m "concurrency or slow"      # L3: 系统测试
pytest -m "smoke"                    # L4: 冒烟测试
pytest -m "not slow"                 # 日常快速反馈
pytest -m "not flaky"                # 排除已知 flaky
```

---

## 七、回归预防机制

### 测试总数基线

```bash
# 记录基线
BASELINE=$(python -m pytest tests/ --collect-only -q 2>&1 | grep -oP '\d+(?= collected)')
echo "Baseline: $BASELINE tests"

# 每次 CI 检查
python3 -c "
import subprocess
r = subprocess.run(['python', '-m', 'pytest', 'tests/', '--collect-only', '-q'],
    capture_output=True, text=True, timeout=30)
import re
m = re.search(r'(\d+) collected', r.stdout)
current = int(m.group(1)) if m else 0
baseline = $BASELINE
if current < baseline:
    print(f'❌ Tests degraded: {current} < {baseline}')
    exit(1)
print(f'✅ {current} tests (baseline: {baseline})')
"
```

### Flaky 测试管理

```python
# 💡 flaky 测试必须：
# 1. 标记 @pytest.mark.flaky
# 2. 在测试文档中记录根因
# 3. 有修复计划

@pytest.mark.flaky(reason="HTTP 400 竞态条件 — 服务端未就绪")
def test_server_endpoint():
    # 临时方案：重试
    import time, urllib.request
    for _ in range(3):
        try:
            resp = urllib.request.urlopen("http://localhost:8080/")
            assert resp.status == 200
            return
        except Exception:
            time.sleep(0.5)
    raise AssertionError("Server not ready after retries")
```

---

## 八、场景指南

### 场景 1: 快速修 Bug

```text
变更类型: bugfix
QA 门禁: L0 + L1

执行:
  L0 → ruff check . + ast.parse
  L1 → pytest tests/ -q
总耗时: ~2 分钟
```

### 场景 2: 加新 API 端点

```text
变更类型: feature
QA 门禁: L0 + L1 + L2

执行:
  L0 → ruff + syntax + mypy
  L1 → pytest tests/ -q (全量)
  L2 → pytest tests/test_api*.py -q
总耗时: ~5 分钟
```

### 场景 3: 架构重构

```text
变更类型: arch
QA 门禁: L0 + L1 + L2 + L3

执行:
  L0 → ruff + syntax + mypy
  L1 → pytest tests/ -q
  L2 → pytest tests/test_api*.py tests/test_cli*.py -q
  L3 → pytest tests/test_concurrency*.py -q
  L3 → tox (跨版本)
总耗时: ~15 分钟
```

### 场景 4: 版本发布

```text
变更类型: release
QA 门禁: L0 + L1 + L2 + L3 + L4

执行:
  L0 → ruff + syntax + mypy
  L1 → pytest tests/ -q
  L2 → 全部集成测试
  L3 → 并发 + 跨版本
  L4 → 版本/CHANGELOG/构建/冒烟/CI检查
总耗时: ~20 分钟
```

---

## 九、快速参考卡

```text
┌─────────────────────────────────────────────────────────────┐
│  通用 QA 快速参考卡                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  变更类型 → 必需门禁                                         │
│  ─────────────────────                                      │
│  🔧 bugfix  → L0 + L1                                       │
│  ✨ feature → L0 + L1 + L2                                  │
│  🏗️  arch   → L0 + L1 + L2 + L3                            │
│  📦 release → L0 + L1 + L2 + L3 + L4                        │
│                                                             │
│  L0: ruff check . + ast.parse + mypy                        │
│  L1: pytest tests/ -q                                       │
│  L2: pytest tests/test_api* test_cli* -q                    │
│  L3: pytest tests/test_concurrency* -q + tox                │
│  L4: version + CHANGELOG + build + smoke                    │
│                                                             │
│  Phase 0.5: qa_assess <change_type> → 选门禁                │
│  Phase 2.5: 每个 Task 后跑对应门禁                           │
│  Phase 3.5: 提交前运行所有必需门禁                            │
│                                                             │
│  铁律: QA 门禁失败 = 不准提交 / 不准合并 / 不准发布          │
│  project-agnostic: 改 src/ 和 tests/ 为你项目的实际路径      │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 与本 skill 链中其他 skill 的关系

```text
主人说「开始开发」
    ↓
development-workflow-index  ← 决策树：选哪条路？
    ↓ 选择「标准路径」
generic-dev-workflow      ← 7 步开发实施
    ↓ 开发完成
generic-qa-workflow       ← 🆕 QA 门禁验证（本 skill）
    ├─ Phase 0.5: QA 影响评估
    ├─ Phase 2.5: 逐 Task 验证
    └─ Phase 3.5: 提交前门禁报告
    ↓ QA 通过
commit-quality-check      ← 提交前安全与一致性检查
    ↓
主人确认完成
```
