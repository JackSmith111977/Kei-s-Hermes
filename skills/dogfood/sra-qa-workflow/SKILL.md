---
name: sra-qa-workflow
description: SRA 项目 QA 工作流 — L0-L4 五层质量门禁体系 + 开发流程集成。涵盖测试分类、质量门禁、QA 状态报告、回归预防。
version: 1.0.0
triggers:
  - qa
  - quality
  - 质量
  - 质量门禁
  - 测试分类
  - 回归
  - 冒烟测试
  - 质量检查
  - 发布检查
  - release gate
  - qa gate
  - 测试覆盖
  - 质量报告
  - qa status
depends_on:
  - sra-dev-workflow
  - generic-dev-workflow
  - test-driven-development
  - commit-quality-check
skill_type: workflow
design_pattern: pipeline
---

# 🎯 SRA QA 工作流 v1.0

> **定位**: SRA 项目的完整质量保证体系。定义了 L0-L4 五层质量门禁、每个开发阶段的 QA 要求、以及 QA 状态报告机制。
> **核心原则**: 机械门禁优于原则提醒。所有 QA 门禁必须可自动执行（脚本/exit code）。

---

## 一、QA 五层体系 (L0-L4)

```
L0 ─ 静态分析门禁 ─── ruff lint + mypy + syntax-check + import sort
 │     pre-commit      阻塞: lint error / 语法不兼容
 │
L1 ─ 单元测试门禁 ─── pytest unit tests + fixture integrity
 │     per-commit      阻塞: 测试失败 / fixture 退化
 │
L2 ─ 集成测试门禁 ─── HTTP API + CLI + adapter + contract tests
 │     pre-merge       阻塞: 接口变更不兼容 / 契约断裂
 │
L3 ─ 系统测试门禁 ─── concurrency + stress + benchmark + cross-version
 │     pre-release     阻塞: 并发竞态 / 性能回退 / 跨版本不兼容
 │
L4 ─ 发布门禁 ─────── smoke test + version consistency + CHANGELOG alignment
       pre-publish     阻塞: 版本不对齐 / 发布包损坏 / 文档滞后
```

### L0: 静态分析门禁

**时机**: 每次 git commit 前（pre-commit）
**命令**:
```bash
# 🧹 Ruff lint
ruff check skill_advisor/ tests/
# 预期: "All checks passed!"

# 🔤 Mypy type check (当前 continue-on-error)
mypy skill_advisor/ || echo "⚠️ non-blocking"

# 🔬 Python 语法兼容性
python3 -c "
import ast, os, sys
errors = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git','__pycache__','build','dist','venv','.egg-info')]
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root,f)) as fp:
                try: ast.parse(fp.read())
                except SyntaxError as e: errors.append((os.path.join(root,f), e))
if errors:
    for p,e in errors: print(f'❌ {p}: {e}')
    sys.exit(1)
print('✅ Syntax OK')
"

# ✅ Fixture 完整性检查
python3 -c "
import os
d = 'tests/fixtures/skills'
if os.path.isdir(d):
    count = sum(1 for _,_,f in os.walk(d) for fn in f if fn == 'SKILL.md')
    assert count >= 300, f'Fixture degraded: {count} < 300'
    print(f'✅ {count} fixture skills')
"
```

**失败处理**: L0 失败 = 代码不准提交。自动修复（ruff --fix）或手动修复。

---

### L1: 单元测试门禁

**时机**: 每次代码变更后
**范围**: `tests/test_*.py` 中标记为 `unit` 的测试（默认全部）
**命令**:
```bash
# 全量测试
python -m pytest tests/ -q --tb=short -o "addopts="

# 如果已添加 pytest markers:
# python -m pytest tests/ -m "not slow and not integration" -q --tb=short
```

**AC 验证**: 每个 Story 的验收条件必须有关联的测试覆盖
**阻断条件**:
- ❌ 任何测试失败（已知 flaky 除外，需标记）
- ❌ 测试总数低于基线（说明测试退化）
- ❌ CI 矩阵中任一 Python 版本失败

---

### L2: 集成测试门禁

**时机**: PR 合并前 / Feature 完成时
**范围**:
| 测试文件 | 覆盖内容 | 运行命令 |
|:---------|:---------|:---------|
| `test_daemon_http.py` | HTTP API 端点 | `pytest tests/test_daemon_http.py -q` |
| `test_cli.py` | CLI 命令 | `pytest tests/test_cli.py -q` |
| `test_adapters.py` | 多 Agent 适配器 | `pytest tests/test_adapters.py -q` |
| `test_contract.py` | 契约兼容性 | `pytest tests/test_contract.py -q` |
| `test_dropin.py` | 替换性 API | `pytest tests/test_dropin.py -q` |
| `test_validate.py` | 校验端点 | `pytest tests/test_validate.py -q` |

**命令**:
```bash
# 全部集成测试
python -m pytest tests/test_daemon_http.py tests/test_cli.py tests/test_adapters.py \
  tests/test_contract.py tests/test_dropin.py tests/test_validate.py -q --tb=short

# HTTP 服务测试（需启动 daemon 或 mock）
python -m pytest tests/test_daemon_http.py -q --tb=short -o "addopts="
```

**阻断条件**:
- ❌ 任何集成测试失败
- ❌ HTTP API 响应格式或状态码不符合契约
- ❌ CLI 子命令缺失或报错

---

### L3: 系统测试门禁

**时机**: 版本发布前 / 架构变更后
**范围**:
| 测试文件 | 覆盖内容 | 运行命令 |
|:---------|:---------|:---------|
| `test_concurrency.py` | 并发安全、文件锁、竞态 | `pytest tests/test_concurrency.py -q` |
| `test_force.py` | 强制注入机制 | `pytest tests/test_force.py -q` |
| `test_benchmark.py` | 性能基线 | `pytest tests/test_benchmark.py -q --benchmark-only` |
| `test_singleton.py` | 单例、端口冲突 | `pytest tests/test_singleton.py -q` |

**跨版本矩阵**:
```bash
# 确保 CI 矩阵全绿 (3.9, 3.10, 3.11, 3.12)
# GitHub Actions 会自动并行
```

**性能基线**（如 benchmark 已配置）:
```bash
pytest tests/test_benchmark.py --benchmark-compare --benchmark-compare-fail=min=5
# 失败条件: 性能回退超过 5%
```

**阻断条件**:
- ❌ 并发测试暴露竞态条件
- ❌ 跨版本测试任一失败
- ❌ 性能回退超过基线 5%+
- ❌ 文件锁/端口冲突机制失效

---

### L4: 发布门禁

**时机**: `git tag v*.*.*` 推送前
**检查项**:
```bash
# === 1. 版本一致性 ===
echo "=== Version ==="
python -c "from skill_advisor import __version__; print(__version__)"
# 预期: 与 git tag 一致 (v前缀除外)

# === 2. CHANGELOG 对齐 ===
echo "=== CHANGELOG ==="
grep -n "^## " CHANGELOG.md | head -10
# 预期: 当前版本有对应条目

# === 3. 构建验证 ===
echo "=== Build ==="
python -m build 2>&1 | tail -5
ls -la dist/
# 预期: wheel + sdist 生成成功

# === 4. 冒烟测试 ===
echo "=== Smoke Test ==="
python -c "
from skill_advisor import __version__
from skill_advisor.advisor import SkillAdvisor
import tempfile
a = SkillAdvisor(skills_dir=tempfile.mkdtemp(), data_dir=tempfile.mkdtemp())
a.refresh_index()
result = a.recommend('test')
assert isinstance(result, list)
print(f'✅ Smoke test passed (v{__version__})')
"

# === 5. project-report 对齐 ===
echo "=== project-report ==="
python3 ~/.hermes/scripts/generate-project-report.py --data docs/project-report.json --verify 2>&1 || echo "⚠️ project-report 验证跳过"
```

**阻断条件**:
- ❌ 版本号与 git tag 不一致
- ❌ CHANGELOG 无当前版本条目
- ❌ 构建产物不完整（缺 wheel 或 sdist）
- ❌ 冒烟测试失败
- ❌ CI 矩阵未全绿（依赖外部 CI 状态）

---

## 二、QA 决策树 — 按变更类型选择门禁

不是每次变更都需要跑全部 L0-L4。根据变更类型选择最低必要门禁：

```
[变更类型]
    │
    ├─ 🔧 修 Bug / 小重构
    │   ├─ L0: ✅ 必须
    │   ├─ L1: ✅ 必须（全量测试）
    │   ├─ L2: ⚠️ 仅影响集成接口时
    │   ├─ L3: ❌ 跳过
    │   └─ L4: ❌ 跳过（除非发版）
    │
    ├─ ✨ 新功能
    │   ├─ L0: ✅ 必须
    │   ├─ L1: ✅ 必须 + 新增测试覆盖新功能
    │   ├─ L2: ✅ 必须（新功能涉及接口/CLI时）
    │   ├─ L3: ⚠️ 仅影响并发/性能时
    │   └─ L4: ❌ 跳过（除非发版）
    │
    ├─ 🏗️ 架构变更 / 跨模块重构
    │   ├─ L0: ✅ 必须
    │   ├─ L1: ✅ 必须
    │   ├─ L2: ✅ 必须
    │   ├─ L3: ✅ 必须（并发安全 + 跨版本）
    │   └─ L4: ❌ 跳过（除非发版）
    │
    └─ 📦 版本发布
        ├─ L0: ✅ 必须
        ├─ L1: ✅ 必须
        ├─ L2: ✅ 必须
        ├─ L3: ✅ 必须
        └─ L4: ✅ 必须
```

### 决策流程

```python
def select_qa_gates(change_type: str) -> list[str]:
    """根据变更类型返回需要通过的 QA 门禁列表"""
    matrix = {
        "bugfix":  ["L0", "L1"],
        "feature": ["L0", "L1", "L2"],
        "refactor": ["L0", "L1", "L2"],
        "arch":    ["L0", "L1", "L2", "L3"],
        "release": ["L0", "L1", "L2", "L3", "L4"],
    }
    return matrix.get(change_type, ["L0", "L1"])
```

---

## 三、开发工作流中的 QA 集入点

QA 不是开发完成后的附加步骤，而是嵌入开发全流程：

```text
开发前                             开发中                             开发后
┌──────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ Phase 0:     │          │ Phase 2:         │          │ Phase 3:         │
│ Reality Check│          │ Implementation   │          │ Pre-submit       │
│   +          │          │   +              │          │   +              │
│ Phase 0.5:   │ ───────► │ Phase 2.5:      │ ───────► │ Phase 3.5:       │
│ QA Impact    │          │ QA Verify        │          │ QA Gate Report   │
│ Assessment   │          │ (每个 Task 后)   │          │ (提交前)         │
└──────────────┘          └──────────────────┘          └──────────────────┘
       │                         │                            │
       ▼                         ▼                            ▼
  选择 QA 门禁              逐 Task 验证              生成 QA 状态报告
  (按变更类型)              (RED→GREEN→QA)           (门禁通过/失败)
```

### Phase 0.5: QA 影响评估

在每个开发任务开始前，确定 QA 等级：

```bash
# 命令: qa assess <change_type>
# 示例:
qa_assess() {
    case "$1" in
        bugfix)  echo "QA gates: L0+L1";;
        feature) echo "QA gates: L0+L1+L2";;
        arch)    echo "QA gates: L0+L1+L2+L3";;
        release) echo "QA gates: L0+L1+L2+L3+L4";;
        *)       echo "QA gates: L0+L1 (default)";;
    esac
}
```

### Phase 2.5: QA 逐任务验证

每个 Task 完成后，运行该 Task 对应的 QA 门禁：

```bash
# Task N 完成后:
# 1. 运行 L0 门禁
ruff check skill_advisor/ tests/

# 2. 运行 L1 门禁（新增测试 + 全量）
python -m pytest tests/ -q --tb=short -o "addopts="

# 3. 如果 Task 涉及集成接口，运行 L2 门禁
python -m pytest tests/test_daemon_http.py tests/test_cli.py -q --tb=short
```

### Phase 3.5: QA 门禁报告

提交前生成最终 QA 状态报告：

```bash
# 运行 QA 状态检查脚本
python3 scripts/qa-status.py --gates L0,L1,L2
# 输出: JSON 格式的状态报告
```

---

## 四、测试分类体系

### pytest markers 定义（建议添加）

```python
# conftest.py 中添加:
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: 单元测试，快速执行")
    config.addinivalue_line("markers", "integration: 集成测试，需外部依赖或 mock")
    config.addinivalue_line("markers", "slow: 慢速测试（>5s）")
    config.addinivalue_line("markers", "flaky: 已知不稳定测试，失败不阻断")
    config.addinivalue_line("markers", "smoke: 冒烟测试，版本发布前运行")
    config.addinivalue_line("markers", "benchmark: 性能基准测试")
    config.addinivalue_line("markers", "concurrency: 并发安全测试")
```

### 测试文件与 QA 层级对照

| QA 层级 | 测试文件 | Markers | 典型耗时 |
|:-------|:---------|:--------|:--------|
| L1 | `test_matcher.py`, `test_indexer.py`, `test_config.py`, `test_memory.py`, `test_skill_map.py`, `test_coverage.py` | unit | < 5s |
| L2 | `test_daemon_http.py`, `test_cli.py`, `test_adapters.py`, `test_contract.py`, `test_dropin.py`, `test_validate.py` | integration | < 30s |
| L3 | `test_concurrency.py`, `test_force.py`, `test_singleton.py`, `test_benchmark.py` | concurrency, slow, benchmark | < 60s |
| L0 | (静态分析) | — | < 10s |
| L4 | (冒烟+构建) | smoke | < 30s |

---

## 五、回归预防机制

### 测试总数基线

每次 CI 运行后记录测试总数，退化自动报警：

```bash
# 检查测试总数是否低于基线
python3 -c "
import subprocess, json
result = subprocess.run(
    ['python', '-m', 'pytest', 'tests/', '--collect-only', '-q'],
    capture_output=True, text=True, timeout=30
)
# 输出示例: '314 tests collected'
# 提取数字...
"
```

### Fixture 退化门禁

```bash
python3 -c "
import os
d = 'tests/fixtures/skills'
count = sum(1 for _,_,f in os.walk(d) for fn in f if fn == 'SKILL.md')
assert count >= 300, f'Fixture degraded: {count} < 300'
print(f'✅ Fixture integrity: {count} skills')
"
```

### flaky 测试管理

已知 flaky 测试必须：
1. 标记 `@pytest.mark.flaky`（需安装 `pytest-rerunfailures`）
2. 在测试文档中记录 flaky 原因
3. 有修复计划（关联 Issue/Story）

当前已知 flaky:
- `test_daemon_http.py::TestHTTPServerCore::test_serve_forever_in_thread` — HTTP 400 竞态条件

---

## 六、QA 状态报告

### 命令

```bash
python3 scripts/qa-status.py [--gates L0,L1,L2,L3,L4]
```

### 输出格式

```json
{
  "timestamp": "2026-05-12T01:00:00Z",
  "project": "sra-agent",
  "version": "2.0.2",
  "gates": {
    "L0": {"status": "pass", "details": {"ruff": "pass", "syntax": "pass", "fixtures": "pass"}},
    "L1": {"status": "pass", "details": {"total": 314, "passed": 314, "failed": 0}},
    "L2": {"status": "pass", "details": {"integration": 120, "passed": 120}},
    "L3": {"status": "skip", "details": {"reason": "not required for bugfix"}},
    "L4": {"status": "skip", "details": {"reason": "not a release"}}
  },
  "summary": "✅ All required gates pass"
}
```

---

## 七、快速参考卡

```text
┌─────────────────────────────────────────────────────────────────────┐
│  SRA QA 快速参考卡                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  变更类型 → 必需门禁                                                │
│  ─────────────────────────                                         │
│  🔧 bugfix  → L0 + L1                                              │
│  ✨ feature → L0 + L1 + L2                                         │
│  🏗️  arch   → L0 + L1 + L2 + L3                                   │
│  📦 release → L0 + L1 + L2 + L3 + L4                               │
│                                                                    │
│  L0 门禁: ruff check + syntax-check + fixtures                     │
│  L1 门禁: pytest -q (全量测试)                                     │
│  L2 门禁: HTTP/CLI/Adapter/Contract tests                          │
│  L3 门禁: concurrency + cross-version + benchmark                  │
│  L4 门禁: version + CHANGELOG + build + smoke                      │
│                                                                    │
│  Phase 0.5: qa_assess <change_type> → 选门禁                       │
│  Phase 2.5: 每个 Task 后跑对应门禁                                  │
│  Phase 3.5: qa-status.py --gates L0,L1,L2 → 报告                   │
│                                                                    │
│  铁律: QA 门禁失败 = 不准提交 / 不准合并 / 不准发布                 │
│  flaky 测试必须标记并记录原因                                       │
│  Fixture 退化 (count < 300) = L0 门禁阻断                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 八、Docker 环境 QA 测试

> SRA 项目可在 Docker 容器内执行完整 QA 流程，用于隔离测试、CI 模拟、多版本兼容性验证。

### 8.1 测试架构

```
hermes-agent-box (Docker)
├── SRA 源码挂载: /workspace/sra (ro — 需用 PYTHONPATH 而非 pip install)
├── pytest 314 tests
├── SRA Daemon (端口 8536)
│   ├── GET  /health      → {"status": "running"}
│   ├── POST /recommend   → {"recommendations": [...]}
│   └── POST /validate    → {"result": {"compliant": true/false, ...}}
└── Skills 目录: /workspace/skills (配置后 recommend 才返回结果)
```

### 8.2 常用测试命令

```bash
# 进入容器运行测试
sg docker -c "docker exec -w /workspace/sra hermes-agent-box \\
  bash -c 'PYTHONPATH=/workspace/sra python3 -m pytest tests/ -q --tb=short -o addopts='"

# 按标记分组
sg docker -c "docker exec -w /workspace/sra hermes-agent-box \\
  bash -c 'PYTHONPATH=/workspace/sra python3 -m pytest tests/ -q -m unit -o addopts='"

# 特定模块
sg docker -c "docker exec -w /workspace/sra hermes-agent-box \\
  bash -c 'PYTHONPATH=/workspace/sra python3 -m pytest tests/test_matcher.py tests/test_validate.py -q'"

# 生成 JUnit 报告
sg docker -c "docker exec -w /workspace/sra hermes-agent-box \\
  bash -c 'PYTHONPATH=/workspace/sra python3 -m pytest tests/ -q --junitxml=/tmp/sra-results.xml'"
```

### 8.3 SRA Daemon API 验证

启动守护进程后验证各端点：

```python
# /health — 返回 {"status": "running"} 而非 "ok"
import urllib.request, json
r = urllib.request.urlopen("http://localhost:8536/health", timeout=5)
data = json.loads(r.read())
assert data["status"] == "running"

# /recommend (POST) — 需配置 skills_dir 才有推荐结果
body = json.dumps({"message": "Python开发", "top_k": 3}).encode()
req = urllib.request.Request("http://localhost:8536/recommend", data=body,
                             headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req, timeout=5)
data = json.loads(r.read())
# 返回格式: {"recommendations": [...], "contract": {...}, "timing_ms": ...}

# /validate — 合规检测
body = json.dumps({"tool":"write_file","args":{"path":"report.pdf"},"loaded_skills":[]}).encode()
req = urllib.request.Request("http://localhost:8536/validate", data=body,
                             headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req, timeout=5)
data = json.loads(r.read())
result = data.get("result", {})
# result.compliant: True/False
# result.missing: ["pdf-layout", ...] (不合规时列出缺失技能)
# result.severity: "warning" / "info"
```

### 8.4 跨容器测试

当 SRA Daemon 运行在 `hermes-agent-box` 时，同一 docker network 的其他容器可通过容器名访问：

```bash
# 从 opencode 容器测试
sg docker -c "docker exec opencode-agent-box \\
  curl -s --connect-timeout 5 http://hermes-agent:8536/health"

# 从 openclaw 容器（无 curl — 用其他容器做客户端）
```

### 8.5 Docker 环境 QA 的已知陷阱

| # | 陷阱 | 表现 | 解决 |
|:-:|:-----|:------|:------|
| 1 | 源码所在卷 ro | pip install -e 失败 | 用 `PYTHONPATH=/workspace/sra` 替代 |
| 2 | /recommend 返回空 | skills_scanned=0 | 配置 skills_dir 指向有效目录 |
| 3 | 端口冲突 | 8536 已被宿主机占用 | 用 `-p 8537:8536` 映射不同主机端口 |
| 4 | 容器内无 curl | node:slim 镜像不含 curl | 用 `wget -qO-` 或 Python urllib |
| 5 | Daemon 启动需 PYTHONPATH | sra 命令未安装 | 用 `python3 -m skill_advisor.runtime.commands cmd_start` |

## 🔗 相关文件

| 文件 | 说明 |
|:-----|:------|
| `scripts/qa-status.py` | QA 状态检查脚本（生成 JSON 报告） |
| `.github/workflows/ci.yml` | CI 工作流（含 L0/L1/L2 门禁） |
| `.github/workflows/release.yml` | Release 工作流（含 L4 门禁） |
| `docs/TEST-STRATEGY.md` | 测试策略文档 |
| `tests/TEST-DATA-MANIFESTO.md` | 测试数据宣言 |
| `~/.hermes/skills/docker-terminal/SKILL.md` | Docker 沙箱技能（多容器 Agent 架构） |
| `~/.hermes/learning/hermes-opencode-openclaw-sandbox/sra-docker-test-plan.md` | 完整 Docker SRA 测试计划 |
