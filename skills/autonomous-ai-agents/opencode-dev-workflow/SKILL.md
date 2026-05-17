---
name: opencode-dev-workflow
description: "使用 OpenCode CLI Agent 完成编码任务的完整工作流。涵盖单次任务委托、交互式会话、多代理并行、代码审查、PR 操作。将 Hermes 的规划/分析能力与 OpenCode 的编码能力结合的最优模式。"
version: 3.0.0
triggers:
  - opencode 开发
  - opencode 编码
  - opencode 任务
  - opencode 委托
  - 用 opencode 写代码
  - opencode dev
  - opencode coding
  - opencode task
  - opencode delegate
  - 编码任务
author: boku (Emma)
license: MIT
metadata:
  hermes:
    tags:
      - Coding-Agent
      - OpenCode
      - Workflow
      - Delegation
      - PTY
      - Autonomous
    category: autonomous-ai-agents
    skill_type: workflow
    design_pattern: pipeline
    related_skills:
      - claude-code
      - codex
      - opencode
      - generic-dev-workflow
      - writing-plans
      - github-code-review
      - commit-quality-check
      - subagent-driven-development
depends_on: []

---

# OpenCode 开发工作流 v2.1

> **🏗️ 架构定位**: Hermes（规划+分析）→ OpenCode（编码+执行）
> Hermes 负责理解需求、规划方案、审查代码；OpenCode 负责实现编码任务。

## 检查清单（每次使用前）

- [ ] `which opencode` — OpenCode 已安装？
- [ ] `opencode --version` — 版本 ≥ 1.14.41？
- [ ] `opencode debug info` — 无报错？
- [ ] 项目在 git 仓库内？— OpenCode 依赖 git context
- [ ] **已使用五要素协议** — 检查 prompt 是否包含任务声明、输入上下文、验收标准、约束边界、输出产物

---

## 一、五要素委托协议（2026-05-16 新增）

> **教训**: 无结构的 `opencode run '帮我实现XXX'` 导致结果不可控、超时中断、输出不可验证。
> **解决方案**: 每次 OpenCode 任务，prompt 必须包含以下五个要素：

### 1.1 任务声明 (Task Declaration)

```
[任务ID]       ← 唯一标识（与 Story ID 对应）
[任务标题]     ← 一句话描述
[任务类型]     ← new_feature | bugfix | refactor | test
[依赖前置]     ← 依赖的任务 ID（如有）
```

### 1.2 输入上下文 (Input Context)

```
[项目根目录]   ← 绝对路径（--dir 参数）
[参考文件清单]  ← 需要读取的现有文件路径列表
[标准/规则引用] ← 需要遵循的规则文件（如 standards/rules.yaml）
[数据模型]     ← 需要遵循的数据结构定义
```

### 1.3 验收标准 (Acceptance Criteria)

```
[AC-1]: 具体可验证的标准
[AC-2]: 具体可验证的标准
[验证命令]: 执行后验证的命令
```

### 1.4 约束边界 (Bounded Constraints)

```
[范围]: 只改什么文件
[不做的]: 明确不改什么
[风格]: 类型标注/docstring/命名规范
[时间盒]: 最大执行分钟数
```

### 1.5 输出产物 (Output Artifacts)

```
[创建的文件]: 路径列表
[修改的文件]: 路径列表
[验证结果]: 验证命令的输出
```

### 1.6 标准模板（复制即用）

````
opencode run '
[任务] {task_id}: {title}
[上下文] {project_dir}  |  文件: {files}
[AC-1] {criterion-1}
[AC-2] {criterion-2}
[约束] 只改 {scope}，不改 {out_of_scope}
[产出] 创建: {files_to_create}  |  修改: {files_to_modify}
[验证] {verify_command}
' --thinking --dir {project_dir}
````

---

## 二、超时策略（2026-05-16 新增）

> **教训**: 默认 `opencode run` 等待超时（60s）远短于多文件任务实际所需，导致文件写到一半中断。
> **原则**: 先估任务规模再设 timeout，宁大勿小。

### 超时推荐表

| 任务规模 | 文件数 | 预估耗时 | 推荐 timeout | 模式 |
|:---------|:------:|:--------:|:------------:|:-----|
| 单文件修复 | 1 | < 30s | 60s | `run` 同步 |
| 小功能（2-3 文件） | 2-3 | 30-90s | 120s | `run` 同步 |
| 多文件功能（4-8 文件） | 4-8 | 1-3min | 300s | `run` 或 `terminal background` |
| 批量并行任务 | 10+ | 2-5min | 600s | `terminal background` + notify |
| 全包大任务 | 15+ | 5-15min | ❌ 拆为小任务 | 单文件逐个委托 |

### 经验法则

- **1-3 文件**: `opencode run '...' --dir <dir>`（同步，设 timeout ≤ 120s）
- **4-8 文件**: `terminal(command="opencode run '...'", workdir="<dir>", background=true, timeout=300)` + `process(poll/wait)`
- **8+ 文件**: 拆分为多个独立子任务，每个 2-4 文件，逐个委托
- **超过 5 分钟的大任务** → 拆！不拆的后果：写到一半超时，输出被截断，无法恢复

---

## 三、模型配置

### 3.1 查看可用模型

```bash
opencode models
# 自带免费模型（无需 API Key）:
#   opencode/big-pickle      ← 默认，通用
#   opencode/hy3-preview-free
#   opencode/minimax-m2.5-free
#   opencode/nemotron-3-super-free

opencode providers list     # 查看已配置的 provider
opencode providers login    # 登录自定义 provider
```

### 3.2 指定模型的方式

```bash
# 方式 1: 每次运行指定
opencode run '任务描述' --model openrouter/anthropic/claude-sonnet-4

# 方式 2: 配置默认模型（opencode.json）
# {
#   "model": "openrouter/anthropic/claude-sonnet-4"
# }
```

### 3.3 模型选择建议

| 场景 | 推荐模型 | 理由 |
|:-----|:---------|:-----|
| 简单 Bug 修复 | `opencode/big-pickle`（默认免费） | 够用，零成本 |
| 功能开发 | `opencode/big-pickle` | 免费免费免费 |
| 复杂架构任务 | `openrouter/anthropic/claude-sonnet-4` | 推理更强 |
| 代码审查 | `opencode/big-pickle` | 足够胜任 |

---

## 四、验证协议（2026-05-16 新增）

> **教训**: OpenCode 自述「通过」但实际测试可能失败。Hermes 必须独立验证，不能相信 OpenCode 的自评。

### 4.1 每次 OpenCode 完成后执行的检查清单

```text
□ 所有预期文件是否存在？
   → test -f <path> 逐个检查
□ 测试是否通过？
   → pytest <test_path> -q
□ 是否有语法错误？
   → python3 -c "import ast; ast.parse(open('<path>').read())"
□ 是否有类型错误？
   → mypy <path> 2>/dev/null || echo "⚠️  non-blocking"
```

### 4.2 验证函数（Python）

```python
def verify_opencode(task_id: str, expected_files: list[str], verify_cmds: list[str]) -> dict:
    """验证 OpenCode 产出：文件存在性 + 验证命令。"""
    from pathlib import Path
    import subprocess
    result = {"task_id": task_id, "passed": True, "missing": [], "test_results": []}
    for f in expected_files:
        if not Path(f).exists():
            result["missing"].append(f)
            result["passed"] = False
    for cmd in verify_cmds:
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            result["test_results"].append({"cmd": cmd, "passed": r.returncode == 0,
                                           "output": (r.stdout+r.stderr)[:200]})
            if r.returncode != 0:
                result["passed"] = False
        except Exception as e:
            result["test_results"].append({"cmd": cmd, "passed": False, "output": str(e)})
            result["passed"] = False
    return result
```

### 4.3 超时恢复

| 超时场景 | 现象 | 恢复方法 |
|:---------|:-----|:---------|
| `opencode run` 中断 | 写到一半的文件不完整 | `process(action="log")` 查看已创建文件，补完剩余 |
| 后台任务超时 | session 还在运行但无输出 | `process(action="poll")` 检查存活，手动延长 wait |
| 输出截断 | 50KB stdout 上限 | 用后台模式（terminal background）避免截断 |

---

## 五、五种委托模式（2026-05-16 新增 — 替代旧版临时示例）

### 模式 A: 单文件修复 (Bugfix) — timeout 60s

```bash
opencode run '
[任务] 修复 #42: login() 返回 500 当 token 过期
[上下文] ~/projects/myapp  |  文件: src/auth.py
[AC-1] 过期 token 返回 401 而非 500
[AC-2] 正常 token 仍返回 200
[约束] 只改 auth.py，不改数据库层
[发出] 修改: src/auth.py
[验证] pytest tests/test_auth.py -q
' --thinking --dir ~/projects/myapp
```

### 模式 B: 多文件功能 (Feature) — timeout 300s

```bash
opencode run '
[任务] 实现用户注册 API
[上下文] ~/projects/myapp  |  文件: src/api/auth.py (风格参考)
[AC-1] POST /api/users 返回 201 + {"token": "..."} 
[AC-2] email 格式验证 (regex)
[AC-3] password 哈希存储
[AC-4] 重复 email 返回 409
[约束] 遵循 src/api/auth.py 的现有风格，所有函数类型标注
[产出] 创建: src/api/users.py, src/models/user.py, tests/test_users.py  |  修改: src/api/__init__.py
[验证] pytest tests/test_users.py -v -q
' --thinking --dir ~/projects/myapp
```

### 模式 C: TDD 三阶段 (推荐) — timeout 300s

```bash
opencode run '
[任务] TDD: 实现 retry 装饰器
[上下文] ~/projects/myapp
[阶段1-RED] 写 test_retry.py 测试（预期失败）
[阶段2-GREEN] 实现 retry.py 让测试通过
[阶段3-REFACTOR] 重构，确认测试仍通过
[约束] 使用 functools.wraps 保留元数据
[验证] pytest tests/test_retry.py -v
' --thinking --dir ~/projects/myapp
```

### 模式 D: 代码审查 — timeout 60s

```bash
opencode run '
[任务] 审查当前 diff 的安全性
[上下文] ~/projects/myapp
[检查点] 1. SQL 注入风险？2. 密码硬编码？3. 错误处理完整？
[发出] 每个检查点: pass/fail + 行号 + 建议
' --thinking --dir ~/projects/myapp
```

### 模式 E: 批量并行 — timeout 600s

```bash
# Hermes 先创建 git worktree 隔离
git worktree add -b feat/module-a /tmp/work-a main
git worktree add -b feat/module-b /tmp/work-b main

# 同时委托
terminal(command="opencode run '[任务A] 实现模块 A ...'", 
         workdir="/tmp/work-a", background=true, timeout=300)
terminal(command="opencode run '[任务B] 实现模块 B ...'", 
         workdir="/tmp/work-b", background=true, timeout=300)

# 等全部完成，验证每个 worktree
pytest /tmp/work-a/tests -q && pytest /tmp/work-b/tests -q
git worktree remove /tmp/work-a /tmp/work-b
```

### 模式 F: 依赖→并行（依赖任务先，独立任务并行）

当 Phase 中有依赖关系的多个 Story 时（如基础层 → 依赖层），用此模式替代纯串行或纯并行：

```text
Phase 3 Stories:
  STORY-5-3-1: 适配器抽象层 (基础层, 无依赖)  ← 先做
  STORY-5-3-2: MCP Server                    ← 可并行于 5-3-3
  STORY-5-3-3: OpenClaw/Claude 适配器         ← 依赖 5-3-1 的 base.py

执行顺序:
  时间 ├── STORY-5-3-1 ───────┤
       │                      │
       │                      ├── STORY-5-3-2 ──┤
       │                      ├── STORY-5-3-3 ──┤
       └─────────────────────────────────────────→ 完成

代码实现:
  # Step 1: 先做依赖项 (delegate_task 同步等待)
  delegate_task(goal="实现 STORY-5-3-1: 适配器抽象层", ...)
  # 验证: pytest && ast.parse 检查
  
  # Step 2: 并行无依赖项
  delegate_task(goal="实现 STORY-5-3-2: MCP Server", ...)  # 并行
  delegate_task(goal="实现 STORY-5-3-3: 适配器", ...)      # 并行
  # 验证: python3 -m pytest scripts/tests/ -q && import 检查

# 实战验证: EPIC-005 Phase 3 (2026-05-16)
# STORY-5-3-1 创建 base.py(139行) + opencode_adapter.py(460行) + hermes重构
# → 然后并行 STORY-5-3-2 MCP Server(506行) + STORY-5-3-3 两个适配器(619行)
# → 141/141 pytest 通过
```

适用条件:
- 基础层 Story < 5 个文件（过多文件应先拆解为更细的 Story）
- 依赖层 Story 不共享文件（避免合并冲突）
- 每个 Story 独立可验证（pytest 全绿是前提）

### 模式 G: Hermes delegate_task（推荐大型任务）— timeout 600s

`delegate_task` 是 Hermes 内建的并行任务工具，适合需要读取大量项目上下文、创建多个文件的复杂任务：

```python
# Hermes 将完整上下文 + 任务描述交给子代理
delegate_task(
    goal="实现模块 A、B、C，包含完整测试",
    context="项目根路径: ~/projects/myapp\n" +
            "已有参考文件: src/models.py (数据模型风格参考)\n" +
            "标准引用: standards/rules.yaml (规则来源)",
    toolsets=["terminal", "file"]
)
```

delegate_task 的优势 vs `opencode run`：
| 对比维度 | opencode run | delegate_task |
|:---------|:------------|:--------------|
| 上下文量 | 有限（prompt 长度受限） | 大（可传递大量上下文） |
| 文件创建 | 需要 git 仓库 | 任意路径 |
| 超时处理 | 同步等待，超时即中断 | 独立子代理，不阻塞 Hermes |
| 并行能力 | 需手动 worktree | 内置并行（list of tasks） |
| 适用场景 | 单文件/小功能（1-3 文件） | 复杂多文件任务（4+ 文件） |

**选择原则**: 1-3 文件 + 简单改动 → `opencode run`。4+ 文件 + 复杂跨模块逻辑 → `delegate_task`。
```

---

## 六、与工作流链的集成（2026-05-16 新增）

在 SDD → DEV → QA → COMMIT 链中，OpenCode 的角色清晰划分：

```text
链阶段        OpenCode 角色                  典型模式   超时
──────────────────────────────────────────────────────────
DEV (开发)    负责编码实现（Hermes 规划→OpenCode 编码） B/E  300s
QA (门禁)     负责修测试（如果 L0/L1 失败）          A/D   60s
COMMIT (提交)  不需要 OpenCode                      —     —
```

### 使用步骤

```bash
# 1. 先检查链状态
python3 scripts/workflow-chain.py status EPIC-XXX

# 2. 确认当前在 DEV 阶段 → 委托 OpenCode
opencode run '[五要素模板]' --thinking --dir ~/projects/myapp

# 3. Hermes 验证产出（验证协议）
# 4. 链推进到 QA
python3 scripts/workflow-chain.py advance EPIC-XXX
```

---

## ⚠️ 常见陷阱

### 模型名称错误

```
❌ opencode run '...' --model claude-sonnet-4
✅ opencode run '...' --model openrouter/anthropic/claude-sonnet-4
```

模型名称必须包含 provider 前缀，用 `opencode models` 查看可用格式。

### 忘记指定工作目录

```
❌ opencode run '修复 bug'（在 /home/ubuntu 下运行）
✅ opencode run '修复 bug' --dir ~/projects/myapp
```

OpenCode 默认在当前目录运行，务必用 `--dir` 指定项目目录。

### 本地包导入失败（editable install 问题）

当 OpenCode 需要调用项目内的本地 Python 包（如 `skill_governance`）时，editable pip install 可能因构建后端兼容问题（如 `setuptools.backends._legacy` 在系统 setuptools 中不存在）或路径钩子未触发而失败：

```
❌ pip install -e packages/skill-governance/
   → ModuleNotFoundError: No module named 'skill_governance'

✅ PYTHONPATH="packages/skill-governance:$PYTHONPATH" python3 -m ... 
```

两种修复方式：

```bash
# 方式 A（推荐 — 临时修复，适合 OpenCode run）
PYTHONPATH="/path/to/packages/pkg:$PYTHONPATH" opencode run '...' --dir /project

# 方式 B（持久修复）
# 在 pyproject.toml 中确保 build-backend = "setuptools.build_meta"
# 而非 setuptools.backends._legacy:_Backend（后者在 setuptools ≥69 时已移除）
```

| 场景 | 推荐方式 | 理由 |
|:-----|:---------|:------|
| OpenCode run 需要 import 本地包 | A (PYTHONPATH) | 临时、无侵入、不影响 pip 状态 |
| 永久修复 pip install -e | B (改 build-backend) | 一次性修复，后续 pip 操作正常 |
| delegate_task + 子代理需要 import | A (PYTHONPATH + sys.path) | 子代理隔离环境 |

**根因诊断**：

```bash
# 检查是否 editable install 问题
pip show <pkg>                    # 显示已安装但 import 失败？
python3 -c "import sys; print(sys.path)"  # 检查 site-packages 路径

# 检查 build-backend
grep build-backend packages/*/pyproject.toml

# 通用兜底（任何工具上下文都可用）
python3 -c "
import sys
sys.path.insert(0, '/path/to/package/dir')
from <pkg> import <module>
print('✅ OK')
"
```

**实战验证**: EPIC-005 Phase 3 实施中碰到的 skill_governance 包导入问题（2026-05-16）。`pip install -e` 安装成功但 `import skill_governance` 失败，根因是 `pyproject.toml` 的 `build-backend = "setuptools.backends._legacy:_Backend"` 在 Python 3.12 的 setuptools 中不可用。修复为 `setuptools.build_meta` 后 pip install 正常工作。

### 交互式会话的超时

`opencode` 交互模式下如果没有 PTY 会 hang。两种解决方式：
- 单次任务用 `opencode run`（不需要 pty）
- 交互式会话用 `pty=true` + `background=true`

### 长任务不返回

`opencode run` 默认等待任务完成才返回。长任务建议：
- 用 `background=true` + `notify_on_complete=true` 异步监控
- 或 `timeout=600` 给足够时间

### OpenCode 需要 git 仓库

和 Codex 类似，OpenCode 在非 git 目录下功能受限。务必在项目 git 仓库内运行。

### 无结构 prompt（2026-05-16 新增）

```
❌ opencode run '帮我实现用户注册功能'
✅ opencode run ' [五要素协议] ...'
```

无结构 prompt 的后果：结果不可控、超时中断、无法验证。**每次必须用五要素协议。**

### 相信 OpenCode 自评（2026-05-16 新增）

```
❌ opencode run '...'  →  OpenCode 说"完成" → 直接通过
✅ opencode run '...'  →  OpenCode 说"完成" → Hermes 跑 pytest 确认
```

OpenCode 说「测试通过」不一定是真的。**必须 Hermes 亲自跑验证命令。**

### 超时没留余量（2026-05-16 新增）

```
❌ 4 文件的任务设 timeout=60s  →  写到一半超时中断
✅ 4 文件的任务设 timeout=300s  →  正常完成
```

超时值 = 预估时间 × 2 + 60s 缓冲。宁大勿小。

---

## 七、验证 CheckList

- [ ] `opencode run 'print 1+1' --dir /tmp` 返回 "2"
- [ ] 后台任务能正常启动和监控
- [ ] 文件附件 `-f` 能正确加载
- [ ] `--thinking` 显示推理过程
- [ ] 模型能自由切换

---

## 八、与其他编码 Agent 的对比

| 特性 | OpenCode 🆕 | Claude Code | Codex CLI |
|:-----|:-----------|:------------|:----------|
| 安装方式 | npm/pip | npm | npm |
| 免费模型 | ✅ 内置 | ❌ 需 API Key | ❌ 需 API Key |
| ACP 协议 | ✅ 支持 | ✅ 支持 | ❌ |
| 交互模式 | TUI/CLI/Server | TUI/CLI | CLI |
| 自动补全 | ✅ | ❌ | ❌ |
| 文件 attachment | ✅ `-f` | ✅ `-f` | ❌ |
| PTY 必须 | ❌（run模式不需要） | ✅ | ✅ |
| 适用场景 | **默认编码首选** | 复杂架构任务 | 沙箱安全执行 |
