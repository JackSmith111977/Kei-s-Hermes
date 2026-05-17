---
name: generic-dev-workflow
description: "通用开发工作流 — 项目无关的轻量级开发实施流程。从需求理解到提交的 7 步标准循环。可被任何项目直接加载使用，与 sdd-workflow(Spec管理) 和 development-workflow-index(决策树) 互补。任何涉及开发/实现/编码/修复等任务时自动加载。"
version: 1.3.0
triggers:
  - 开发
  - 实现
  - 编码
  - 写代码
  - 修复
  - 开发流程
  - 通用开发
  - 开发步骤
  - feature
  - 功能实现
  - implement
  - coding
  - html对齐
  - 报告对齐
  - 文档对齐
  - 继续开发
  - 继续实现
  - 开始实施
  - start implementing
  - 多阶段
  - 多阶段执行
  - 自动化实施
  - phase
  - 阶段执行
  - 自主执行
  - 进度监控
  - 进度记录
  - phase-gate
  - 计划实施
author: Emma (小玛)
license: MIT
metadata:
  hermes:
    tags:
      - workflow
      - development
      - generic
      - step-by-step
    category: dogfood
    skill_type: workflow
    design_pattern: pipeline
depends_on:
  - test-driven-development
  - self-review
  - doc-alignment
  - commit-quality-check
  - unified-state-machine
  - project-state-machine
  - generic-qa-workflow
  - chain-state
  - sdd-workflow
  - opencode-dev-workflow
---

# 🛠️ 通用开发工作流 v1.0

> **定位**: 轻量、自包含、项目无关的开发实施流程。不绑定到任何特定项目。
> **与相关 skill 的关系**:
> - `development-workflow-index` → 决策树，告诉你选哪条路（调研/快速/标准/完整）
> - `sdd-workflow` → 管理 Spec 的生命周期（创建→审批→归档）
> - **本 skill → 实际的开发实施步骤（怎么把代码写出来）**

---

## 〇、什么时候加载此 skill？

当主人说以下内容时，**必须**加载此 skill：

| 触发词 | 示例 |
|:-------|:------|
| 开发/实现 | 「实现这个功能」「开发 XX 模块」 |
| 编码/写代码 | 「帮我写这个代码」「开始编码」 |
| 修复 | 「修一下这个 Bug」 |
| 功能 | 「加个新功能」「做 feature X」 |

**加载后，按以下 7 步流程执行，不可跳过顺序。**

---

## 📋 7 步开发流程（含 Step 0：SDD 门禁）

```text
[0] SDD 门禁 ─→ [1] 需求确认 ─→ [2] 环境检查 ─→ [3] 实施计划 ─→ [4] TDD实现 ─→ [5] 验证 ─→ [6] 自检 ─→ [7] 提交
  SDD就绪    理解需求    Reality Check    writing-plans   RED-GREEN   全量测试    self-review  git commit
                                                                                                    +
                                                                                              doc-alignment
```

### 🔴 Step 0: SDD 定义与文档对齐门禁

**做什么**: 在写任何代码前，先确认 SDD 定义是否完成、文档是否已对齐。

**铁律**: "先在 SDD 工作流中定义，对齐文档，再开始实施"——不要代码先于文档。

```text
检查清单:
  □ 当前任务是否有已批准的 Spec/Story？
      → 加载 sdd-workflow → 运行 spec-state.py list
      → 如无 → ❌ 先创建 Spec → 主人批准 → 再回来
  □ 涉及跨项目集成时，目标项目是否有对应文档更新？
      → 例如：SRA 插件 → INTEGRATION.md / README / EPIC 文档
      → 如无 → ❌ 先对齐文档 → 再开始实施
  □ 变更的文件属于哪个 git 仓库？
      → 源码必须在项目的 git 仓库中管理，不可直接在目标部署目录创建
      → 安装脚本负责部署，源码版本管理
```

**实战教训**（2026-05-15 SRA EPIC-004 Phase 0）：

```
❌ 错误：直接在 ~/.hermes/hermes-agent/plugins/sra-guard/ 下创建文件
    → 被主人纠正："你怎么不是在projects中的sra中进行啊"
    → 问题：代码不在 git 仓库中，无法版本管理

❌ 错误：代码写完了才补 SDD 定义和文档对齐
    → 被主人纠正："先在sdd工作流中定义，对齐文档，再开始实施"
    → 问题：实施先于定义，导致方向偏差时回退成本高

✅ 正确流程：SDD 定义完成 → 文档对齐 → 实施
```

**耗时**: ~1 分钟

### Step 1: 需求确认

**做什么**: 确认要改什么、不改什么、做到什么程度算完成。

```text
问题模板:
  1. 要改哪个文件/模块？
  2. 预期行为是什么？
  3. 验收标准是什么？（可测试的条件）
  4. 不做的范围？（防止 scope creep）
```

**产出**: 一句话需求描述 + 验收标准清单
**耗时**: ~2 分钟

---

### Step 2: 环境检查（Reality Check）

**做什么**: 验证代码库的实际状态，不盲信文档。

```bash
# 2.1 最近变更
git log --oneline -10

# 2.2 是否有未提交的修改
git status --short

# 2.3 测试基线
python -m pytest --collect-only -q 2>/dev/null | tail -1
# 或: python -m pytest tests/ -q --tb=short -o "addopts=" 2>&1 | tail -3

# 2.4 版本号
python -c "from pkg import __version__; print(__version__)" 2>/dev/null
```

**产出**: 基线记录（测试数、版本号、未提交变更）
**耗时**: ~1 分钟

---

### Step 3: 实施计划（writing-plans）

**做什么**: 将功能拆解为 2-5 分钟的原子任务。每个任务包含：
- 确切的文件路径
- 确切的代码改动
- 验证命令

```text
Task N: {标题}
  文件: {确切的路径}
  操作: {具体改什么}
  验证: {验证命令}
```

**规则**:
- 🚫 每个任务 ≤ 5 分钟
- 🚫 每个 Task 有对应的测试 Task（TDD）
- 🚫 如果 Task 需要「实现时再做决定」→ 太模糊，退回

**产出**: `todo` 清单或实施计划文件
**耗时**: ~3-5 分钟

---

### Step 4: TDD 实现（RED-GREEN-REFACTOR）

> **有两种实现方式**：手动实现（Hermes 直接写代码）或 **委托 OpenCode 实现（推荐）**。
> 使用 OpenCode 可以隔离编码上下文、并行处理多任务，且不占用 Hermes 的 context window。

| 方式 | 适用场景 | 优点 |
|:-----|:---------|:-----|
| 🧑‍💻 **手动实现** | 简单修改（1-2 个文件） | 直接控制，无需额外工具 |
| 🤖 **OpenCode 委托** | 复杂功能（3+ 文件），多任务并行 | 隔离上下文，可并行，不撑爆 context |

#### 🤖 方式 A：使用 OpenCode 实现（推荐）

加载 `opencode-dev-workflow` skill 后，按以下模式委托：

```bash
# 1. Hermes 先将任务拆解为原子 Task（见 Step 3 的计划）
# 2. 逐个 Task 委托给 OpenCode（或批量委托）

# 单 Task 委托
opencode run 'Task 1: 在 tests/test_auth.py 添加 test_login_success 测试，然后实现 login() 函数使其通过' \
  --thinking --dir ~/projects/myapp

# 批量委托（Hermes 提供完整上下文）
opencode run \
  '根据以下 plan 实现所有 Task：
   Task 1: 在 auth.py 中添加 login() 函数...
   Task 2: 在 tests/ 中添加测试...
   实现完成后运行 pytest tests/ -q 确认通过。' \
  --thinking --dir ~/projects/myapp

# 跟踪进度
process(action="log", session_id="<id>")
```



#### 🧑‍💻 方式 B：手动实现（传统方式）

逐个 Task 实现。每个功能 Task 前必须有对应的测试 Task。

```text
[RED]   写一个会失败的测试 → 确认测试确实失败
[GREEN] 写最少代码让测试通过 → 确认测试通过
[REFACTOR] 重构代码 → 确认测试仍然通过
```

```text
[RED]   写一个会失败的测试 → 确认测试确实失败
[GREEN] 写最少代码让测试通过 → 确认测试通过
[REFACTOR] 重构代码 → 确认测试仍然通过
```

**强制前序**: 必须先执行 `test-driven-development` skill

```bash
# 加载 TDD skill
skill_view(name="test-driven-development")
```

**规则**:
- 🔴 没有失败的测试就不准写代码
- 🔴 代码写好了没测试 → 删掉重写
- 🔴 每个 Task 完成后 git commit（原子提交）

---

### Step 5: 全量验证 + QA 门禁

**做什么**: 运行所有测试 + QA 分层门禁，确保不破坏已有功能。

```bash
# 5.1 运行全量测试
python -m pytest tests/ -q --tb=short -o "addopts="

# 5.2 与基线对比（测试数不应低于基线）
# 5.3 如果有 lint: ruff check / flake8 等

# 🚦 ----- QA 门禁（自动触发）-----
# 根据变更类型运行对应 L0-Lx 门禁
# 变更类型: bugfix/feature/arch/release
# 需要加载 generic-qa-workflow 后执行:
#   skill_view(name='generic-qa-workflow')
#   查看 generic-qa-workflow §三、QA 决策树

# L0: ruff check / ast.parse
ruff check . 2>/dev/null || echo "⚠️  lint not configured"
python3 -c "
import ast, os, sys
errors = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git','__pycache__','venv','node_modules')]
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root,f)) as fp:
                try: ast.parse(fp.read())
                except SyntaxError as e: errors.append((os.path.join(root,f), e))
if errors:
    for p,e in errors: print(f'❌ {p}: {e}')
    sys.exit(1)
print('✅ L0: All .py files parseable')
"

# L1: 单元测试
python -m pytest tests/ -q --tb=short -o "addopts=" || {
    echo "❌ L1: 单元测试失败 — 阻塞提交"
    exit 1
}
echo "✅ L1: 单元测试通过"

# 如果有集成测试: L2
if [ -f "tests/test_api.py" ] || [ -f "tests/test_cli.py" ]; then
    python -m pytest tests/test_api*.py tests/test_cli*.py -q --tb=short || {
        echo "❌ L2: 集成测试失败"
        exit 1
    }
    echo "✅ L2: 集成测试通过"
fi

# 🚦 ----- QA 门禁完成 -----
```

**产出**: 测试报告 + QA 门禁结果
**耗时**: ~2-5 分钟（取决于测试数量）

---

### Step 6: 自我审查（self-review）

**做什么**: 在向主人汇报前，自己先检查一遍。

加载 `self-review` skill，执行场景 F（任务交付验证）：

```text
[ ] 是否做了文档一致性检查？
[ ] 是否只改了该改的？（变更范围检查）
[ ] 是否有硬编码密码/token？（安全检查）
[ ] 每个 AC 是否实测确认过？
```

**产出**: 自我审查报告
**耗时**: ~2 分钟

---

### Step 7: 提交与对齐

**做什么**: 代码 + 文档 + HTML 报告同一次提交。

```bash
# 7.1 🔴 实施后文档同步（新增强制步骤）
#     在关闭 Story 前，必须同步更新所有相关文档的状态。
#     否则会出现"代码已实现、测试全绿、但文档还写着 draft"的漂移。
#
#     检查清单：
#     □ STORY 文件: status: draft → status: completed
#     □ STORY 文件: 所有 AC 改为 [x]（- [ ] → - [x]）
#     □ SPEC 文件: status: active/draft → status: completed
#     □ EPIC 文件: 更新 completed_phases 表格（新增已完成 Phase 行）
#     □ EPIC 文件: 优先级表格中对应 Phase 标记 ✅
#     □ project-report.json: 更新 test count / 新增 sprint entry
#     □ 其他项目级报告（epic-summary, panorama 等）
#
#     实战教训（2026-05-15 SRA EPIC-004 Phase 0-3）：
#     11 个 Story + 3 个 SPEC 全部 status: draft，AC 全未勾选
#     → 被主人纠正"对齐文档" → 额外花 10 分钟批量修复

# 7.2 文档对齐（如果有 doc-alignment）
skill_view(name="doc-alignment")
# 执行 5 步对齐协议

# 7.3 🌐 HTML 报告对齐（如果项目有生命周期 HTML 报告）
#     检查 reports/lifecycle.html 或 PROJECT-PANORAMA.html
#     是否反映最新的文档状态（状态表、徽章、AC 进度）
#     如有 project-report.json → generate-project-report.py 自动同步
#     如手动维护 → grep/搜索 HTML 中的状态信息对比文档

# 7.4 提交前检查
skill_view(name="commit-quality-check")
# 执行安全检查 + 一致性检查

# 7.4 项目状态同步 (unified-state-machine skill)
```bash
cd /home/ubuntu/projects/hermes-cap-pack
python3 scripts/project-state.py sync
python3 scripts/project-state.py verify
```

# 7.5 Git 提交
git add -A
git commit -m "type(scope): description"
```

**产出**: git commit + 文档同步完成
**耗时**: ~2 分钟

---

## 🪤 常见陷阱

| 陷阱 | 场景 | 解决 |
|:-----|:------|:------|
| **代码先于 SDD 定义** | 主人说「开始实现」→ 直接写代码 | 🔴 先执行 Step 0：检查 SDD 定义和文档对齐状态。有 Spec/Story 批准了再写代码 |
| **实施后文档还在 draft** | 代码写了、测试全绿，但 Story/SPEC 文件仍是 `draft`，AC 未勾选 | 🔴 Step 7.1 新增了「实施后文档同步」清单。每个 Story 结束后立即更新 status + AC，不等最后一起做 |
| **模块级变量作用域（global）** | 在 Hermes 插件 `__init__.py` 的 hook 函数中写 `_turn_counter += 1`，报 `UnboundLocalError` | Python 函数内对模块级变量的赋值会创建局部变量，遮蔽模块级同名变量。必须用 `global _turn_counter` 声明：<br><br>```python<br>_turn_counter: int = 0  # 模块级<br><br>def my_hook(...):<br>    try:<br>        global _turn_counter  # ✅ 必须声明<br>        _turn_counter += 1    # 否则 UnboundLocalError<br>```<br><br>⚠️ 典型场景：hook 回调函数中使用模块级计数器/缓存状态时最容易踩坑 |
| **源码创建在部署目标目录** | 插件源码直接创建在 Hermes plugins 目录 | 源码必须在项目的 git 仓库中管理。安装脚本负责部署，源码不直接在目标目录创建 |
| **CLI 脚本导入失败** | `ModuleNotFoundError: No module named 'scripts'` | CLI 入口和命令模块都需要加 `sys.path.insert(0, ...)` 指向项目根目录。详见 `references/python-cli-pitfalls.md` |
| **测试路径假设** | 测试从项目根运行没问题，但从子目录运行报错 | 所有路径用 `Path(__file__).resolve().parent` 构造，不用相对路径字符串 |
| **版本号不同步** | pyproject.toml 的 version 和 CHANGELOG 的版本不一致 | 提交前用 `grep "version"` 交叉检查，或用 `bump-version.py` 统一管理 |
| **`setup.py` 正则解析 `__init__.py` 提取版本号** | `setup.py` 用 `re.search(r'__version__\\s*=\\s*["\\']([^"\\']+)', ...).group(1)` 从 `__init__.py` 读版本号。当版本解析改为函数调用时（如 `__version__ = _resolve_version()`），正则返回 `None` → CI 所有 Python 版本在 `pip install` 阶段全部崩溃 | ❌ 不要在 `setup.py` 中解析 `__init__.py` 提取版本。版本应完全由 `pyproject.toml` + `setuptools-scm` 管理。`setup.py` 仅做最小调用：<br><br>```python<br>from setuptools import setup, find_packages<br>setup(packages=find_packages())<br>```<br><br>📌 实战案例：SRA v2.1.1 CI 全炸，根因为 `__init__.py` 改为函数赋值后正则无匹配 |
| **`__init__.py` 顶层导入与 `__version__` 循环引用** | `__init__.py` 在顶层 `from .runtime.daemon import X`，但 `daemon.py` 又 `from .. import __version__`。导入时 `__init__.py` 尚未执行到 `__version__` 定义 → `ImportError` | 将模块级导入移到 `__version__` 定义**之后**，加 `# noqa: E402` 抑制 lint：<br><br>```python<br>__version__ = _resolve_version()<br>from .runtime.daemon import X  # noqa: E402<br>```<br><br>📌 实战教训：SRA 重构版本解析后出现循环导入 |
| **setuptools-scm 配置陷阱（v10+）** | 1) `version_file` 改名为 `write_to`；2) `tag_regex` 在 TOML 中推荐用单引号 literal string 避转义；3) `write_to_template` 缺失则 `_version.py` 不生成；4) `vcs-versioning` 是 setuptools-scm ≥10 的必需依赖 | 推荐配置：<br><br>```toml<br>[tool.setuptools_scm]<br>tag_regex = '^(?:[\\w-]+-)?v?(?P<version>[\\d\\.a-b]{3,}(?:rc\\d+)?)$'<br>version_scheme = "post-release"<br>local_scheme = "no-local-version"<br>write_to = "pkg/_version.py"<br>write_to_template = "__version__ = '{version}'\\nversion = '{version}'\\n"<br>```<br><br>📌 `_version.py` 加入 `.gitignore`。开发环境用 `git describe` 实时解析 |

---

---

## 🏗️ 附加模式：多阶段自主执行 (Multi-Phase Autonomous Execution)

> **适用场景**: 主人分配了一个包含多个 Phase 的大型实施计划，要求自动化执行、逐阶段 Review、用 `todo` 追踪进度。

### 何时使用

主人说出以下模式时自动加载此模式：
- 「自动化实施所有阶段的任务」
- 「每个阶段需要 review」
- 「进度需要记录」
- 「每完成一项原子任务都需要标记完成」
- 「完成后将实施文案发我审阅」

### 模式流程

```text
[0] 审阅方案（等待主人批准）
    │ 主人批准后开始
    ▼
[1] 初始化 todo 清单
    │ todo() 设置所有任务，标记为 pending
    ▼
[2] 执行 Phase N
    │ ├── 逐原子任务执行
    │ ├── 每完成一个 → todo(merge: true) 标记 completed
    │ └── 每遇到失败 → 修复后重新验证
    ▼
[3] Phase Review
    │ 检查所有任务是否符合验收标准
    │ ├── 全部通过 → 标记 Phase 完成
    │ └── 有失败 → 重新执行 → 直到全部通过
    ▼
[4] 汇报 Phase 结果给主人
    │ 等待主人说"继续"或"批准"
    ▼
[5] 重复 [2]→[4] 直到所有 Phase 完成
    │
    ▼
[6] 最终交付报告
```

### 关键规则

| 规则 | 说明 |
|:-----|:------|
| **先审阅后实施** | Phase 计划必须先给主人审阅，主人批准后才能开始实施（"在你批准前禁止修改和实施"）|
| **进度追踪** | 每个原子任务创建时立即在 `todo` 中注册（`"status":"in_progress"`），完成后标记 `"completed"` |
| **逐阶段 Review** | 每完成一个 Phase 必须自我验证：检查所有任务是否符合预期。不符合的重新执行直到通过（「否则重新开发」）|
| **等待主人信号** | Phase Review 通过后汇报给主人，等主人说"继续"才能进下一个 Phase |
| **不可擅自推进** | ❌ 永远不跳过 Phase Review 直接进入下一 Phase |
| **失败重做** | 任何任务失败或不符合预期，必须重做到通过为止，不可遗留降级 |

### 奖励机制

当你成功完成多阶段自主执行后（所有 Phase 通过审查），`SELF.md` 中记录一次成功经验，积累信任分数。

### 实战教训（2026-05-17）

```text
❌ 错误：未等主人批准计划就开始实施
    → 被主人纠正：先写计划 → 等批准 → 再实施
    → 浪费：写了实施计划文档后又等了一轮

✅ 正确流程：
    1. 写实施计划 → 2. 发给主人审阅 → 3. 主人批准 → 
    4. 创建 todo 清单 → 5. 逐任务执行 → 
    6. 每完成一个标记 completed → 7. Phase 完成自检 → 
    8. 汇报给主人 → 9. 等主人说"继续" → 10. 下一 Phase
```

### 与 7 步开发流程的关系

```
多阶段自主执行模式           → 适用于「大规模实施计划」
    ↓ 每个原子任务内部
7 步开发流程 (本 skill)      → 适用于「具体的编码/实现任务」
```

两者是嵌套关系：多阶段模式的每个原子任务内部，可以调用 7 步流程来实施具体的开发工作。

---

## 🔴 铁律

| # | 铁律 | 违背后果 |
|:-:|:-----|:---------|
| 1 | **Step 0-7 顺序不可颠倒** — 先 SDD 定义再写代码 | 方向不对白做、主人纠正 → 信任下降 |
| 2 | **没有测试就不准写代码**（TDD） | 代码不可维护、回归风险 |
| 3 | **没有自检就不准汇报** | 主人发现遗漏→信任下降 |
| 4 | **代码改了文档必须同步** — 每个 Story 完成后立即更新其 status 和 AC | 文档漂移 → 下次决策基于过时信息 |
| 5 | **每个原子 Task 独立 git commit** | 无法回滚、无法追溯 |
| 6 | **源码必须在项目 git 仓库中管理**，部署目录通过安装脚本复制 | 代码丢失、无法版本管理 |
| 7 | **实施后立即更新文档状态** — 不等最后一起做 | 所有 Story 停留在 draft → 需要额外的「对齐文档」步骤 |

---

## 🔗 与本 skill 链中其他 skill 的关系

```text
主人说「开始开发」
    ↓
development-workflow-index  ← 决策树：选哪条路？
    ↓ 选择「标准路径」
sdd-workflow              ← Spec 门禁：有批准吗？
    ↓ 已批准
本 skill                  ← 通用开发工作流：7 步实施
    ├── Step 0: SDD 门禁（先定义，再实施）
    ├── Step 5 自动触发 QA 门禁
    │   └── generic-qa-workflow ← L0-L4 分层检查
    ↓ 完成
chain-state.py advance    ← 自动推进工作流链
    ↓
sdd-workflow              ← 更新 Spec 状态：complete → archive
    ↓
主人确认完成
```

---

## 🗂️ 文件结构

```
~/.hermes/skills/dogfood/generic-dev-workflow/
├── SKILL.md                         ← 主入口（7 步流程 + 铁律 + 陷阱）
└── references/
    ├── scenario-guide.md            ← 场景指南（新功能/修 Bug/重构/快速修复）
    ├── python-cli-pitfalls.md       ← Python CLI 导入路径问题与解决
    └── version-resolution-architecture.md  ← 版本解析架构（三层降级链 + setuptools-scm 配置 + 陷阱）
```

## 📚 参考深度阅读

- **`references/scenario-guide.md`** — 4 种常见开发场景的完整走法（新功能/修 Bug/重构/快速修复）

## 🚀 使用示例

### 场景：实现 SRA 的批量推荐接口

```text
Step 1: 「主人，要改的是什么？验收标准是什么？」
Step 2: git log + pytest --collect-only + 版本检查
Step 3: Task 1: 写 test_batch_recommend → 验证: pytest -k batch
         Task 2: 实现 recommend_batch() → 验证: pytest -k batch
         Task 3: 集成到 daemon.py 端点 → 验证: curl POST /recommend/batch
Step 4: RED→GREEN→REFACTOR 每个 Task
Step 5: pytest tests/ -q → 确认全绿
Step 6: self-review 场景 F
Step 7: doc-alignment + commit-quality-check → git commit
```
