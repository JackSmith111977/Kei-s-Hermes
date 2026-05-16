---
name: opencode-dev-workflow
description: "使用 OpenCode CLI Agent 完成编码任务的完整工作流。涵盖单次任务委托、交互式会话、多代理并行、代码审查、PR 操作。将 Hermes 的规划/分析能力与 OpenCode 的编码能力结合的最优模式。"
version: 1.0.0
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
---

# OpenCode 开发工作流 v1.0

> **🏗️ 架构定位**: Hermes（规划+分析）→ OpenCode（编码+执行）
> Hermes 负责理解需求、规划方案、审查代码；OpenCode 负责实现编码任务。

## 检查清单（每次使用前）

- [ ] `which opencode` — OpenCode 已安装？
- [ ] `opencode --version` — 版本 ≥ 1.14.41？
- [ ] `opencode debug info` — 无报错？
- [ ] 项目在 git 仓库内？— OpenCode 依赖 git context

---

## 一、快速开始 — 核心命令

### 1.1 单次任务（最常用）

```bash
# 基础用法 — 自动使用默认模型
opencode run '在 src/utils.py 中添加一个 retry 装饰器，支持指数退避'

# 指定工作目录
opencode run '修复 tests/test_api.py 中的 flaky 测试' --dir ~/projects/sra

# 显示思考过程
opencode run '重构 auth 模块，提取公共中间件' --thinking --dir ~/projects/myapp

# 附带文件作为上下文
opencode run '审查这份测试文件的覆盖率' -f tests/test_api.py --dir ~/projects/myapp

# 指定模型
opencode run '实现用户注册 API' --model openrouter/anthropic/claude-sonnet-4 --dir ~/projects/myapp
```

### 1.2 后台长任务

```bash
# 启动后台任务
terminal(command="opencode run '实现完整的用户认证系统，包括登录、注册、JWT 刷新'", 
         workdir="~/projects/myapp", background=true, timeout=600)

# 返回 session_id → 用 process 监控
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
process(action="wait", session_id="<id>", timeout=300)
```

### 1.3 交互式会话（复杂多步任务）

```bash
# 启动交互会话
terminal(command="opencode", workdir="~/projects/myapp", background=true, pty=true)

# 发送指令
process(action="submit", session_id="<id>", data="实现用户管理 CRUD")

# 检查进度
process(action="poll", session_id="<id>")

# 查看完整输出
process(action="log", session_id="<id>", offset=0, limit=100)

# 发送后续指令
process(action="submit", session_id="<id>", data="现在加单元测试")

# 退出交互
process(action="write", session_id="<id>", data="\x03")  # Ctrl+C
# 或直接
process(action="kill", session_id="<id>")
```

---

## 二、与 Hermes 的协作模式

### 2.1 最优分工

```
┌─────────────────┐         ┌──────────────────┐
│    Hermes (boku) │         │    OpenCode      │
│                  │         │                  │
│  ✅ 需求分析     │         │  ✅ 编码实现     │
│  ✅ 架构设计     │         │  ✅ 测试编写     │
│  ✅ 代码审查     │         │  ✅ 重构优化     │
│  ✅ 文档对齐     │         │  ✅ Bug 修复     │
│  ✅ PR 管理      │         │  ✅ Git 操作     │
│  ✅ 质量门禁     │         │                  │
└─────────────────┘         └──────────────────┘
```

### 2.2 典型流程：Hermes 规划 → OpenCode 执行

```bash
# Step 1: Hermes 分析需求、设计方案
# （boku 做规划，使用 writing-plans skill）

# Step 2: Hermes 将实现任务委托给 OpenCode
opencode run '实现规划中描述的 Task 1-5' --thinking --dir ~/projects/myapp

# Step 3: Hermes 审查 OpenCode 的输出
# （boku 运行 commit-quality-check + github-code-review）

# Step 4: 如有问题，迭代
opencode run '修复审查中发现的问题：1) ... 2) ...' --dir ~/projects/myapp
```

### 2.3 多任务并行

```bash
# 并行处理多个独立任务（使用 git worktree 隔离）
git worktree add -b feat/user-auth /tmp/work-auth main
git worktree add -b feat/api-docs /tmp/work-docs main

# 同时启动
terminal(command="opencode run '实现用户认证模块'", 
         workdir="/tmp/work-auth", background=true, pty=true, timeout=600)
terminal(command="opencode run '编写 API 文档'", 
         workdir="/tmp/work-docs", background=true, pty=true, timeout=600)

# 监控全部
process(action="list")
process(action="log", session_id="<auth_session_id>")
process(action="log", session_id="<docs_session_id>")

# 完成后清理
git worktree remove /tmp/work-auth
git worktree remove /tmp/work-docs
```

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

## 四、集成到 Hermes SDD 工作流

### 4.1 在 SDD Story 实施阶段使用 OpenCode

当 SDD Story 已获批准、进入 `implement` 阶段时：

```bash
# 1. Hermes 加载 Story 文档理解需求
# 2. Hermes 编写 execution plan（使用 writing-plans skill）
# 3. Hermes 调用 OpenCode 执行

opencode run \
  '根据以下 plan 实现 Task 1-5：...' \
  --thinking \
  --dir ~/projects/myapp
```

### 4.2 在 PR review 中使用 OpenCode

```bash
# 创建一个临时 worktree 做 review
git worktree add -b review-pr-17 /tmp/review-pr-17 master

# 让 OpenCode 审查代码
opencode run 'Review this PR diff: ...' \
  --thinking --dir /tmp/review-pr-17

# 清理
git worktree remove /tmp/review-pr-17
```

---

## 五、常见场景速查

### 5.1 实现新功能

```bash
opencode run '实现 PDF 导出功能，支持中文内容。使用 WeasyPrint 渲染 HTML 到 PDF。' \
  --thinking --dir ~/projects/myapp
```

### 5.2 修复 Bug

```bash
opencode run '修复 #42: 用户登录时如果 token 过期，应返回 401 而非 500' \
  --thinking --dir ~/projects/myapp
```

### 5.3 编写测试

```bash
opencode run '为 src/auth.py 编写 pytest 单元测试，覆盖所有公共函数和边界情况' \
  -f src/auth.py --dir ~/projects/myapp
```

### 5.4 重构代码

```bash
opencode run '将 controllers/user.py 拆分为多个模块：auth.py、profile.py、admin.py' \
  --thinking --dir ~/projects/myapp
```

### 5.5 代码审查

```bash
opencode run '审查当前的 diff，检查安全问题和设计模式' \
  --thinking --dir ~/projects/myapp
```

---

## 六、⚠️ 常见陷阱

### 6.1 模型名称错误

```
❌ opencode run '...' --model claude-sonnet-4
✅ opencode run '...' --model openrouter/anthropic/claude-sonnet-4
```

模型名称必须包含 provider 前缀，用 `opencode models` 查看可用格式。

### 6.2 忘记指定工作目录

```
❌ opencode run '修复 bug'（在 /home/ubuntu 下运行）
✅ opencode run '修复 bug' --dir ~/projects/myapp
```

OpenCode 默认在当前目录运行，务必用 `--dir` 指定项目目录。

### 6.3 交互式会话的超时

`opencode` 交互模式下如果没有 PTY 会 hang。两种解决方式：
- 单次任务用 `opencode run`（不需要 pty）
- 交互式会话用 `pty=true` + `background=true`

### 6.4 长任务不返回

`opencode run` 默认等待任务完成才返回。长任务建议：
- 用 `background=true` + `notify_on_complete=true` 异步监控
- 或 `timeout=600` 给足够时间

### 6.5 OpenCode 需要 git 仓库

和 Codex 类似，OpenCode 在非 git 目录下功能受限。务必在项目 git 仓库内运行。

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
