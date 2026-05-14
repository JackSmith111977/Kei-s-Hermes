---
name: python-testing
description: Python 测试最佳实践、反模式诊断与修复指南。涵盖测试污染、fixture 隔离、模块级状态管理、pytest 陷阱等。
version: 1.0.0
metadata:
  hermes:
    tags: [python, testing, pytest, debugging, fixtures]
    category: testing
---

# Python 测试最佳实践与反模式急救指南

## When to Use

当用户遇到以下任何场景时加载此 skill：

- **测试在隔离条件下通过，但全量运行失败**（经典测试污染信号）
- **测试依赖某个全局/模块级状态，出现不可复现的失败**
- **pytest `tmp_path` 相关测试行为异常**
- **需要编写更健壮的 fixture 和测试隔离方案**
- **需要调试 CI 中失败但本地通过的测试**

## Core Principles

### 1. 测试污染的两大根因

```
污染源 A: 模块级变量突变 (Module-Level Mutation)
  └─ 测试 A 修改了模块的全局变量 (SRA_HOME / CONFIG_FILE 等)
  └─ 测试 B 依赖同一模块，读到被污染的状态
  └─ 污染传播路径: import → 全局状态 → 跨测试文件

污染源 B: pytest tmp_path 保留策略
  └─ pytest 默认保留最近 3 个 tmp_path 目录 (retention_policy=all)
  └─ 测试 A 写入文件到 tmp_path(包含遗留配置) + 修改模块变量指向它
  └─ 测试 B 读取模块变量 → 指向仍存在的旧 tmp_path → 读到遗留数据
```

### 2. 故障模式识别

| 症状 | 最可能原因 | 诊断方法 |
|:-----|:----------|:---------|
| 单测通过，全量失败 | 模块级变量污染 | 按文件顺序逐步排查 |
| CI 失败，本地通过 | 环境差异/运行顺序差异 | 复现 CI 的文件顺序 |
| `tmp_path` 内容"幽灵"出现 | pytest 保留策略 | 检查 /tmp/pytest-of-*/ 目录 |
| 断言值偏离默认值 | 配置文件/环境变量被污染 | 打印当前模块状态 |

### 3. 修复模式

#### 模式 A: try/finally 恢复模块级变量（首选）

```python
def test_something(self, mock_dir):
    from my_module import config as cfg
    
    # 保存原始值
    orig_home = cfg.SRA_HOME
    orig_file = cfg.CONFIG_FILE
    
    try:
        # 修改模块级变量指向临时目录
        cfg.SRA_HOME = str(mock_dir)
        cfg.CONFIG_FILE = str(mock_dir / "config.json")
        
        # ... 测试逻辑 ...
    finally:
        # 务必恢复！避免污染后续测试
        cfg.SRA_HOME = orig_home
        cfg.CONFIG_FILE = orig_file
```

#### 模式 B: `unittest.mock.patch.object`（当属性可 patch 时）

```python
from unittest.mock import patch

def test_something(self):
    with patch.object(cfg_module, 'SRA_HOME', str(tmp_dir)):
        with patch.object(cfg_module, 'CONFIG_FILE', str(tmp_dir / "config.json")):
            result = cfg_module.load_config()
```

#### 模式 C: `monkeypatch` 内置 fixture（pytest 推荐）

```python
def test_something(monkeypatch, tmp_path):
    monkeypatch.setattr(cfg_module, 'SRA_HOME', str(tmp_path))
    monkeypatch.setattr(cfg_module, 'CONFIG_FILE', str(tmp_path / "config.json"))
```

### 4. pytest tmp_path 行为速查

| 配置项 | 默认值 | 说明 |
|:-------|:------|:-----|
| `tmp_path_retention_count` | **3** | 保留最近 N 个目录 |
| `tmp_path_retention_policy` | **"all"** | 保留所有文件 ("failed" 只保留失败用例的) |
| 目录位置 | `/tmp/pytest-of-<user>/pytest-N/` | 按数字递增 |
| 清理时机 | 超过 retention_count 后自动删除最旧的 |

**⚠️ 陷阱**: `tmp_path` 目录及其内容在测试间是**持久保留**的！
如果测试 A 写入了文件且修改了模块全局变量指向该路径，
测试 B 读到该模块变量时，文件依然存在 → **测试污染**。

### 5. 诊断方法论

当怀疑测试污染时：

```
Step 1: 复现
  python -m pytest tests/test_a.py tests/test_b.py -q --tb=long
  # 如果 test_b 单独通过但跟在 test_a 后失败 → 污染确认

Step 2: 定位污染源
  grep -rn "module_var\s*=" tests/  # 查找模块变量赋值
  grep -rn "from.*import.*config" tests/  # 查找模块导入后赋值

Step 3: 检查保留文件
  find /tmp/pytest-of-*/ -name "*.json" -exec cat {} \;
  # 确认遗留文件内容

Step 4: 修复
  # 在污染测试中添加 try/finally 恢复原始值
```

### 6. 防御性编码

- **所有修改模块级变量的测试**必须有 `try/finally` 或 `monkeypatch` 恢复
- Fixture 中声明的临时路径不要"泄露"到模块级变量
- 使用 `monkeypatch` fixture（pytest 内置）而非直接赋值
- 关键测试文件添加 `# WARNING: modifies global state` 注释

### 7. Python 版本兼容性：类型注解语法差异

当 CI 矩阵包含多个 Python 版本时，新版类型语法在旧版本上会导致**导入时崩溃**（SyntaxError），而非运行时错误。

#### 常见陷阱速查

| 语法 | 最低 Python | 错误表现 | 兼容写法 |
|:-----|:-----------|:---------|:---------|
| `dict \| None` | **3.10** (PEP 604) | `TypeError: unsupported operand type(s) for \|` | `Optional[dict]` 或 `dict = None` |
| `list[str]` | **3.9** (PEP 585) | `TypeError: 'type' object is not subscriptable` (3.8-) | `List[str]` (from typing) |
| `str \| int` | **3.10** | 同上 PEP 604 | `Union[str, int]` |
| `X \| Y` 联合类型 | **3.10** | 同上 | `Union[X, Y]` 或 `Optional[X]` |
| `\`self\` type` | **3.11** (PEP 673) | `NameError: name 'Self' is not defined` | `from typing import Self` (3.11+) |

#### 真实案例：PEP 604 union types in CI matrix

```python
# ❌ Python 3.9 上导入时报错
def _load_schema() -> dict | None:     # PEP 604 需要 3.10+
    ...

# ✅ 兼容写法
def _load_schema() -> dict:            # 返回值可为 None；返回 None 兼容
    ...
```

**CI 诊断命令**：

```bash
# 在 CI 中快速定位哪个 Python 版本失败
gh run view <run-id> --log | grep "FAILED\|Error\|exit code 1"

# 或按 job 名过滤
gh run view <run-id> --log --job "pytest (3.9)" | grep "Error"
```

#### 防御策略

1. **声明最低版本前确认语法支持范围** — `requires-python = ">=3.9"` 意味着不能用 PEP 604
2. **CI 矩阵必须包含最低支持版本** — 仅测 3.11/3.12 会漏掉兼容性回归
3. **import-time 错误 vs runtime 错误** — 类型语法错误在导入时立即崩溃，不是"测试失败"而是"模块无法加载"
4. **`from __future__ import annotations`** — 在 Python 3.7+ 中可用，将所有注解转为字符串（延迟求值）

```python
# 安全选项：使用 __future__ 延迟求值（3.7+）
from __future__ import annotations

def load() -> dict | None:  # 3.7+ 可用！因为注解是惰性字符串
    ...
```

⚠️ **注意**：`from __future__ import annotations` 仅在以下条件下安全：
- 运行时不需要读取注解值（如 `dataclasses` field type、`inspect.get_annotations`、Pydantic model）
- 仅在 `TYPE_CHECKING` 块或其他类型检查场景使用
- 对于运行时依赖注解的项目（如 FastAPI、Pydantic、dataclasses），此方法可能导致运行时类型信息丢失

**安全双模式（`__future__` + 运行时兼容）**：

```python
from __future__ import annotations  # 3.7+: 仅类型检查器看到联合语法
from typing import TYPE_CHECKING, Dict, Optional, Union

# 运行时兼容的显式标注（用于 dataclass/Pydantic 等）
class Config:
    http_port: int = 8536
    data: Optional[Dict[str, str]] = None  # 运行时可见，兼容 3.8+

# 类型检查专用（仅 mypy/pyright 看到）
if TYPE_CHECKING:
    ConfigDict = dict | None  # 3.10+ 语法，但只给类型检查器用
    LoadResult = dict | str | None
```

如果运行时需要注解信息，仍必须写兼容低版本的 `Union[X, Y]` / `Optional[X]`。

5. **CI 增加语法兼容性门禁** — 在 Python 最低版本上运行语法检查，防止上游提交时遗漏

```yaml
# .github/workflows/ci.yml — Python 语法兼容性门禁
syntax-check:
  name: 🔬 Python 3.9 syntax compatibility
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.9"
    - name: 🔬 Check all .py files parseable
      run: |
        python3 -c "
        import ast, sys, os
        errors = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'build', 'dist', '.egg-info')]
            for f in files:
                if f.endswith('.py'):
                    with open(os.path.join(root, f)) as fp:
                        try: ast.parse(fp.read())
                        except SyntaxError as e: errors.append((os.path.join(root, f), e))
        if errors:
            for p, e in errors: print(f'❌ {p}: {e}')
            sys.exit(1)
        print('✅ All .py files parseable')
        "
    - name: 🔬 Check no PEP 604 union syntax
      run: |
        python3 -c "
        import re, sys, os
        errors = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'build', 'dist', '.egg-info')]
            for f in files:
                if not f.endswith('.py'): continue
                for i, line in enumerate(open(os.path.join(root, f)), 1):
                    s = line.split('#')[0]
                    if re.search(r'->\s*\w[\w.]*\s+\|\s+\w', s) or \
                       re.search(r':\s*\w[\w.]*\s+\|\s+\w[\w.]*(?=\s*[=)])', s):
                        errors.append(f'{os.path.join(root, f)}:{i}: {line.rstrip()}')
        if errors:
            for e in errors: print(f'❌ PEP 604 (3.10+): {e}')
            sys.exit(1)
        print('✅ No PEP 604 union syntax')
        "
```

6. **注意 Release 工作流的 Python 版本脱敏** — 如果 `release.yml` 只用高版本 Python（如 3.11）运行，它不会暴露低版本兼容性问题。Release 通过但 CI 红了 = 脱敏。确保 Release CI 的 Python 版本覆盖 CI 矩阵中的最老版本。

#### 快速诊断（CI 失败时）

```bash
# 哪个 Python 版本失败了？
gh run list --limit 5 --json name,headBranch,conclusion

# 查看具体 job 日志
gh run view <run-id> --log --job "pytest (3.9)" | grep -E "FAILED|Error|SyntaxError|TypeError"

# 本地用目标版本验证
docker run --rm -v $(pwd):/src -w /src python:3.9 python3 -c "
import ast, sys, os
for path in __import__('glob').glob('**/*.py', recursive=True):
    if 'site-packages' not in path and '.git' not in path and 'venv' not in path:
        try:
            with open(path) as f: ast.parse(f.read())
        except SyntaxError as e:
            print(f'❌ {path}: {e}')
"
```

## Pitfalls

- ❌ 测试单独通过就认为没问题 — 测试污染只在特定运行顺序下暴露
- ❌ 依赖 `tmp_path` 测试间的路径一致性 — `tmp_path` 在测试间轮换
- ❌ 用环境变量代替模块变量修改 — 如果被测试代码不读 env var，同样无效
- ❌ 忽略 pytest 的 tmp_path 保留策略 — 文件残留是隐形的污染源

## Verification

修复测试污染后：

```bash
# 1. 单文件测试
python -m pytest tests/test_a.py -q

# 2. 污染源 + 受影响文件顺序运行
python -m pytest tests/test_a.py tests/test_b.py -q

# 3. 全量测试
python -m pytest tests/ -q

# 4. 如果怀疑 tmp_path 残留
find /tmp/pytest-of-*/ -name "*.json" -exec rm -f {} \;
python -m pytest tests/ -q
```

## References

- `references/test-pollution-real-world.md`: SRA 项目的真实测试污染案例（症状 → 诊断 → 修复全流程）。⚠️ 与 `sra-dev-workflow/references/test-state-pollution.md` 内容重叠——后者是项目级记录，前者是通用知识提取。
- `references/ci-version-failure-patterns.md`: CI 版本兼容性失败真实案例（PEP 604 union types / Release 版本脱敏）。
- `references/cli-subprocess-testing.md`: CLI 独立脚本的子进程测试模式 — 当测试对象不可 import 时用 subprocess.run 验证 exit code / stdout / stderr。含路径陷阱、性能考量、真实案例。

## Overlap Notes

此 skill 与以下 skill 存在内容重叠：
- **`sra-dev-workflow`** → SKILL.md §「陷阱 6」(test state pollution) + `references/test-state-pollution.md` — 项目级（SRA 特定）记录
- **`sra-dev-workflow`** → SKILL.md §「陷阱 8」(gh CLI CI diagnostic commands)
- **`python-debugpy`** → 调试工具部分可能有重叠

本 skill 定位为 **Python 测试通用类级知识**，非项目特定。重叠由 background curator 在 consolidation 时处理。
