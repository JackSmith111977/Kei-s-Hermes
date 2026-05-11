# 测试基础设施机械门禁 — SRA 实战模式

> 沉淀自 2026-05-11 Sprint 20: test_contract.py 绕过 fixture 数据使用 ~/.hermes/skills
> 问题: 测试依赖运行时环境，CI 中无此目录 → 测试被 pytest.skip() 静默跳过

---

## 根因链

```text
test_contract.py 使用 ~/.hermes/skills
  ↓
CI 无此目录 → pytest.skip() 跳过关键测试
  ↓
根源: 开发时没检查 tests/fixtures/ 已有 317 个真实 skill 数据
  ↓
更深层: test_matcher.py 就在同目录，已正确使用 FIXTURES_DIR 模式
  ↓
最深: 眼睛看到 ≠ 思维复用 — 需要显式步骤触发模式发现
```

## 三层机械门禁架构

### 第 1 层: 写代码前 (Phase 0 — 模式发现)

```bash
# 扫描已有 fixture 模式
grep -rn "FIXTURES_DIR\|fixtures/" tests/ 2>/dev/null | head -10

# 检查 fixture 目录是否存在
ls tests/fixtures/ 2>/dev/null || echo "⚠️  无 fixture 目录"
```

**执行时机**: 任何「写新测试」任务开始时，写代码之前。

### 第 2 层: 提交前 (Phase 1 — 门禁)

```bash
# 🔴 P0 门禁: 阻断 ~/.hermes/skills 引用
if [ -d "tests/fixtures" ]; then
    found=$(grep -rn "hermes/skills\|~/.hermes" tests/ --include="*.py" 2>/dev/null | grep -v "conftest.py" | head -5)
    if [ -n "$found" ]; then
        echo "❌ BLOCKED: 测试引用了运行时依赖！请用 tests/fixtures/ 替代"
        exit 1
    fi
fi

# ✅ 验证 fixture 完整性
python3 tests/check_fixtures.py
```

### 第 3 层: CI 流水线 (自动验证)

```yaml
# .github/workflows/ci.yml 中的步骤
- name: ✅ Verify test fixture integrity
  run: python3 tests/check_fixtures.py
```

## 文件清单

| 文件 | 作用 | 创建时间 |
|:-----|:-----|:---------|
| `tests/conftest.py` | 标准化 Fixture（`advisor_from_fixtures` 等） | 2026-05-11 |
| `tests/TEST-DATA-MANIFESTO.md` | 测试数据宣言 + 铁律 + 使用规范 | 2026-05-11 |
| `tests/check_fixtures.py` | CI 可执行的 fixture 完整性检查脚本 | 2026-05-11 |
| `.hermes/AGENTS.md` | Phase 0 测试模式发现 + Phase 1 门禁 | 2026-05-11 |

## 关键使用模式

### ✅ 正确: 从 fixture 加载
```python
from conftest import FIXTURES_DIR

@pytest.fixture
def advisor(tmp_path):
    return SkillAdvisor(skills_dir=FIXTURES_DIR, data_dir=str(tmp_path))
```

### ❌ 错误: 运行时依赖
```python
@pytest.fixture
def advisor(tmp_path):
    hermes_skills = os.path.expanduser("~/.hermes/skills")
    if os.path.isdir(hermes_skills):
        return SkillAdvisor(skills_dir=hermes_skills, ...)
    return SkillAdvisor(data_dir=str(tmp_path))  # CI 中空数据!
```

### 🔍 测试模式发现命令
```bash
# 在任何项目中写测试前执行
grep -rn "FIXTURES_DIR\|fixtures/" tests/ 2>/dev/null | head -10
# 输出示例:
# tests/conftest.py:FIXTURES_DIR = os.path.join(...)
# tests/test_matcher.py:FIXTURES_DIR = os.path.join(...)
# tests/test_matcher.py:SKILLS_FIXTURE = FIXTURES_DIR
```

## 可迁移性

本模式不限于 SRA 项目。在任何 Python 项目中：
1. 创建 `tests/fixtures/` 存放静态测试数据
2. 创建 `tests/conftest.py` 标准化 fixture 访问
3. 在 AGENTS.md 中加入 Phase 0 门禁
4. 关键: 数据必须能提交到 git，不依赖运行时环境
