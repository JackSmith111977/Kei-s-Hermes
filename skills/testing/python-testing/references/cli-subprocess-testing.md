# CLI 子进程测试模式 — subprocess-based testing

当测试对象是**独立 CLI 脚本**（不可 import 为模块）时，用 `subprocess.run` 替代 pytest fixture 测试。

## 适用场景

- 测试 `if __name__ == "__main__":` 入口逻辑
- 测试 argparse/手动 sys.argv 解析
- 测试 stdout/stderr 输出格式
- 测试不同参数组合的 exit code
- 脚本依赖硬编码路径（如 `Path.home() / ".hermes"`）且不方便 mock

## 核心模式

```python
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

def run_script(name: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """运行项目脚本，返回 CompletedProcess"""
    cmd = [sys.executable, str(SCRIPTS_DIR / name)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
```

## 测试用例模式

```python
class TestMyCLI:
    def test_help(self):
        """--help 正常输出"""
        result = run_script("my-tool.py", "--help")
        assert result.returncode == 0
        assert "用法" in result.stdout or "Usage" in result.stdout

    def test_json_output(self):
        """--json 输出有效 JSON"""
        result = run_script("my-tool.py", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "key" in data

    def test_filter_param(self):
        """参数过滤有效"""
        result = run_script("my-tool.py", "--filter", "value")
        assert result.returncode == 0

    def test_error_handling(self):
        """非法参数返回非零"""
        result = run_script("my-tool.py", "--nonexistent-flag")
        assert result.returncode != 0

    def test_timeout_protection(self):
        """防止脚本死循环（内置 30s timeout）"""
        result = run_script("my-tool.py", "--audit")
        assert result.returncode == 0
```

## 关键参数说明

| 参数 | 用途 | 陷阱 |
|:-----|:------|:------|
| `capture_output=True` | 捕获 stdout/stderr，不污染测试输出 | 脚本输出过多时可能撑爆内存 |
| `text=True` | 返回字符串而非 bytes | UTF-8 解码问题 |
| `timeout=30` | 防止死循环挂死 CI | 全量审计类操作可能超时 |
| `check=False`（默认） | 不因非零退出码抛异常 | 需自行 assert returncode |

## 路径陷阱

```python
# ❌ 错误：tests/ 在 scripts/ 下一级
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
# → 如果 tests/ 和 scripts/ 是同级目录，实际解析为 scripts/scripts/ 路径不存在

# ✅ 正确：根据目录层级调整
# 项目结构: project/scripts/ 和 project/scripts/tests/
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
# 项目结构: project/scripts/ 和 project/tests/
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
```

## 性能考量

| 场景 | 耗时 | 建议 |
|:-----|:----:|:------|
| 简单 CLI（--help/--json） | < 1s | 适合单元测试 |
| 全量扫描（200+ skills） | 10-30s | 只用 1 个端到端测试 |
| 全量审计（SQS 评分所有 skill） | 30s+ | ⚠️ 跳过或设为手动测试 |

**经验法则**：每个测试调用 ≤ 3 秒。超出就用 `threshold` 限制范围。

## 真实案例

参见 `test_epic002_tools.py`：

- `TestSkillTreeIndex` — 测试 `skill-tree-index.py`（6 tests，~2s）
- `TestSkillQualityScore` — 测试 `skill-quality-score.py`（5 tests，~3s）
- `TestSkillLifecycleAudit` — 测试 `skill-lifecycle-audit.py`（6 tests，~4s）

## 何时不用此模式

- 测试对象是**可 import 的函数/类** → 用 pytest + unittest.mock
- 需要 mock 网络/文件系统 → 用 pytest fixtures + monkeypatch
- 测试框架本身是 Python 库（如 pytest、unittest） → 直接 import 测试
