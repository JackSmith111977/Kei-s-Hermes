# SRA 代码库审计与修复 Sprint — 实战配方

> **来源**: 2026-05-11 SRA 项目 3 轮修复 Sprint 实战
> **项目规模**: 14 个 Python 源文件（~3,919 行代码），11 个测试文件，225 个测试用例

---

## 一、四层并行代码库审计模式

### 适用场景

首次接触一个 Python 中大型代码库（10-40 源文件），需要快速获得全景问题清单。

### 工作流

**加载**: `skill_view(name="analysis-workflow")` → 加载 `references/codebase-tech-debt-audit.md`

**执行**:

```text
[Phase 0] 库存清点 (boku 主会话)
    ├── cd <project> && find . -name "*.py" | grep -v ...
    ├── find . -name "*.py" -exec wc -l {} + | sort -n
    └── 输出: 文件清单 + 行数统计 + 模块依赖

[Phase 1] 四层代码扫描 (delegate_task 并行)
    │
    ├── 第一批 (max_concurrent_children=3):
    │   ├── Layer 1: 架构层
    │   │   检查: 模块职责、线程安全、配置系统、模块耦合
    │   │   工具: read_file(daemon.py, cli.py, advisor.py)
    │   │   目标: daemon.py 是否职责过多？import 循环？线程锁？
    │   │
    │   ├── Layer 2: 代码质量
    │   │   检查: except:pass、类型标注覆盖率、魔法数字、print/logging
    │   │   工具: grep + python3 -c "import ast; ..." + terminal
    │   │   目标: 量化所有反模式的数量
    │   │
    │   └── Layer 3: 测试覆盖
    │       │   检查: 源文件↔测试文件矩阵、覆盖率缺口、测试质量
    │       │   工具: ls tests/ + pytest -q + read_file
    │       └── 目标: 识别零测试模块 + 评估测试品质
    │
    └── 第二批 (第一批完成后立即启动):
        └── Layer 4: 文档与基础设施
            检查: README/ROADMAP/CHANGELOG 时效、CI/CD、.gitignore
            工具: read_file + grep + git diff
            目标: 文档漂移点 + 基础设施缺口

[Phase 2] 分类分级 (boku 主会话合并)
    ├── 按 4 维度: 🏗️架构 / 💻代码 / 🧪测试 / 📝文档
    ├── 按 3 等级: 🔴P0 / 🟡P1 / 🟢P2
    ├── 成本收益排序: 低成本+高收益 → 立即修
    └── 输出: 格式化问题清单

[Phase 3] 汇报
    ├── 结论先行 (BLUF): "共发现 N 个问题，P0/P1/P2 各多少"
    ├── 核心发现: 最严重的 3 个问题
    └── 建议: "先修 P0，再排 P1，P2 随缘"
```

### 子代理 Prompt 模板（Layer 1-3）

```text
context="工作目录: ~/projects/<project>

Layer 1 — 架构层面扫描

检查要点:
1. <模块名> 是否有职责过多？
2. 线程安全: threading.Lock 使用是否正确？
3. 配置管理: 配置如何加载？是否硬编码路径？
4. 模块耦合: import 关系是否合理？

输出格式:
- 问题描述 (位置:文件:行号)
- 风险等级 (🔴P0/🟡P1/🟢P2)
- 影响分析
- 建议修复",
goal="Layer 1 — <Project> 架构层面扫描",
toolsets=["terminal","file"]
```

### ⚠️ 约束

- `delegate_task` 默认 `max_concurrent_children=3` → 4 层分 2 批（3+1）
- 每层输出控制在 4000 字符以内，避免上下文爆炸
- 子代理结果需要验证（文件是否存在、命令是否执行成功）

---

## 二、修复 Sprint 工作流

### Sprint 节奏

```text
每个 Sprint = 2-4 个 Task，~3-5h 工作量
```

| Sprint | 焦点 | 任务数 | 工作量 |
|:-------|:-----|:------:|:------:|
| Sprint 1 (P0) | 线程锁 + 版本号 + except:pass | 4 Task | ~3h |
| Sprint 2 (P1) | 零测试覆盖补齐 | 3 Task | ~4h |
| Sprint 3 (P1) | 架构拆分 + logging 统一 | 2 Task | ~3h |

### 单 Task 节奏

```text
1. cd <project> && git checkout <branch> && git pull
2. 读待修改文件 → read_file
3. 写测试 → TDD（优先）或直接修改
4. 验证: pytest tests/ -q --tb=short
5. 验证: python3 -m py_compile modified_file.py
6. git add + commit + push
```

### 实现方式选择

| 实现方式 | 适用场景 | 优点 | 缺点 |
|:---------|:---------|:-----|:-----|
| **手动 TDD** | 简单明确的小改动（版本号、类型标注） | 完全控制、无间接错误 | 串行 |
| **子代理 refactor** | 复杂重构（daemon.py 拆分、模块提取） | 专注上下文、自动处理 import | 需验证侧效果 |
| **子代理 + 审查** | 跨模块变更 | 自动 spec 审查 | 耗时较长 |

### 子代理重构模板

当需要提取一个模块中的子模块时（如拆分 daemon.py）：

```text
delegate_task(
    goal="将 <源文件> 中的 <XXX> 拆分到 <新文件>",
    toolsets=["terminal","file"]
)
```

**关键注意事项**（从实战中提炼）：
- 子代理需要读到完整源文件 → 先 `read_file` 再传给 context
- 子代理修改后必须验证: `python3 -m py_compile` + `pytest tests/ -q`
- 子代理会自动更新 import 路径（已验证工作正常）
- 但子代理可能处理不好 `\\\\n` 转义等边缘情况 → 需主会话复查

---

## 三、版本号漂移检测

这是 AI 项目最常见的文档漂移类型。

### 检测命令

```bash
# 扫描所有硬编码 semver
grep -rn '"v1\.\|"1\.' --include="*.py" --include="*.md" --include="*.sh" . | \
  grep -v __pycache__ | grep -v .git | grep -v node_modules | grep -v ".pytest_cache"

# 对比核心版本声明
grep "version" pyproject.toml 2>/dev/null
grep "__version__" */__init__.py 2>/dev/null

# 检查 install.sh/check-sra.py 等脚本中的版本
grep -n "v1\.\|1\.\." scripts/install.sh scripts/check-sra.py
```

### 修复模式

对于「默认版本号回退字符串」，如 `stats.get('version', '1.1.0')`，应直接改为当前版本。

---

## 四、四层扫描的 Layer 输出参考

### 架构层 (Layer 1) — 典型发现
```
- daemon.py 职责过多 (937行/5职责) → 🔴P0
- SceneMemory 线程零锁保护 → 🔴P0
- os.fork() + 线程不兼容 → 🔴P0
- 配置路径硬编码，无环境变量 → 🟡P1
```

### 代码质量层 (Layer 2) — 典型发现
```
- except:pass 共 16 处 → 🔴P0
- daemon.py 类型标注仅 33% → 🟡P1
- 3 个文件 print/logging 混用 → 🟡P1
- 魔法数字 25+ 处 → 🟢P2
```

### 测试层 (Layer 3) — 典型发现
```
- dropin.py (206行) 零测试 → 🟡P1
- adapters/__init__.py (316行) 零测试 → 🟡P1
- 测试数据使用真实 fixture (313 skills) → ✅优秀
- 无 conftest.py 通用 fixture → 🟢P2
```

### 文档层 (Layer 4) — 典型发现
```
- 8 处版本号过时 (README/install.sh/check-sra.py) → 🔴P0
- README 命令表缺 3 个命令 → 🟡P1
- CHANGELOG Sprint 状态交叉不一致 → 🟡P1
```

---

## 五、完整的 Sprint 规划模板

```markdown
# Sprint N — <名称>

**目标版本:** <version>

**Goal:** <一句话>

**范围:** <涉及模块>

**前提:** git checkout <branch> && git pull

**验证:** pytest tests/ -q (当前 <N> passed)

---

### Task 1: <标题> (<估时>)

**Objective:** <一句话>

**Files:**
- Create: <文件路径>
- Modify: <文件路径>

**步骤:**
1. <操作>
2. <操作>
3. 验证: <命令>

### Task N: ...

---

**提交规范:**
- Task 完成一个提交一个（原子提交）
- 按 func/fix/test/docs 等 Conventional Commits 格式
- 每个提交包含变更说明 + 影响范围
```
