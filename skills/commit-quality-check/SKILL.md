---
name: commit-quality-check
description: "GitHub 项目提交前文档与业务一致性检查 + 提交质量检查清单。涵盖 Conventional Commits 规范验证、安全红线扫描、文档一致性检查、变更范围评估。适用于任何需要做 git commit 或 PR 前自检的场景。"
version: 1.1.0
triggers:
  - 提交检查
  - 提交质量
  - commit check
  - 一致性检查
  - 提交前检查
  - pre-commit
  - 审查提交
  - 代码审查前检查
  - 提交规范
  - commitlint
  - 质量门禁
  - 代码审查前自检
  - pre-push
author: Emma (小喵)
license: MIT
metadata:
  hermes:
    tags:
    - commit
    - quality
    - review
    - consistency
    - security
    - conventional-commits
    - pre-commit
    - git-hooks
    category: software-development
    skill_type: reviewer
    design_pattern: pipeline
---

# commit-quality-check — 提交前文档一致性与质量检查

> 核心原则：**AI 写代码很快，但提交质量决定了项目能不能长期维护。**
> 每次 git commit 或 PR 前，用此 Skill 做系统性自检。

## 触发方式

在 commit 或 PR 前，直接说：
- "帮我的提交做质量检查"
- "检查一下这次提交合不合格"
- "pre-commit 检查"

## 检查流程

### Step 0: 环境检测

```bash
# 检查当前是否有 staged changes
git diff --cached --stat

# 检查是否有未跟踪文件
git status --short

# 检查当前分支
git branch --show-current
```

### Step 1: 安全检查（🔴 P0 — 一票否决）

**🚨 以下任一不通过则必须修复后才能提交：**

```bash
# 1. 扫描硬编码密码/Token/API Key
git diff --cached -S "gph_" -- . || true
git diff --cached -S "sk-" -- . || true
git diff --cached -S "token" -- . || true
git diff --cached -S "password" -- . || true
git diff --cached -S "api_key" -- . || true

# 1b. 辅助：扫描 staged diff 原文（不受 git 脱敏影响）
git diff --cached -U1000 | grep -E '^\+(.*(token|password|api_key|secret|sk-|gph_))' || echo "✅ 未发现敏感信息"

# 2. 检查 .gitignore 是否覆盖敏感文件
grep -l ".env\|\.key\|credentials\|secret\|token" .gitignore 2>/dev/null || echo "⚠️ .gitignore 未覆盖敏感文件模式"

# 3. 检查 Git 历史中是否有敏感信息
git log -p --diff-filter=M -S "password" HEAD~5..HEAD 2>/dev/null | head -30
```

**修复指南：**
- 硬编码敏感信息 → 使用环境变量或配置文件
- 示例路径/用户名 → 脱敏为 `<user>`、`<token>` 等占位符
- Git 历史中有敏感信息 → 使用 `git filter-branch` 或 `bfg` 清理

### Step 2: 文档一致性检查（🔴 P0）

**核心原则：代码改了，文档必须同步更新。**

```bash
# 1. 列出所有修改的文件
git diff --name-only HEAD

# 2. 检查是否修改了核心逻辑但没改相关文档
```

| 修改类型 | 必须同步的文档 |
|----------|---------------|
| 新增 API/端点 | README API 表、docs/ 相关文件 |
| 修改匹配逻辑 | RUNTIME.md 已知限制表、SKILL.md 描述 |
| 修改阈值/权重 | 文档中是否有记录该值？ |
| 修复已知问题 | RUNTIME.md 的"当前限制"是否需删除该条 |
| 添加同义词映射 | RUNTIME.md 的"已修复"列表是否需更新 |

### Step 3: Commit Message 检查（🟡 P1）

**格式：`<type>(<scope>): <description>`**

```bash
# 查看最后一次 commit message
git log -1 --pretty=format:"%s"
```

| 类型 | 何时使用 | SemVer 对应 |
|------|----------|-------------|
| `feat` | 新功能 | MINOR |
| `fix` | 修复 Bug | PATCH |
| `docs` | 文档变更 | - |
| `refactor` | 代码重构（不修 Bug 不加功能） | - |
| `test` | 添加/修改测试 | - |
| `chore` | 构建/工具/依赖变更 | - |
| `ci` | CI 配置变更 | - |
| `perf` | 性能优化 | - |
| `style` | 格式/风格变更（不影响逻辑） | - |

**检查清单：**
- [ ] type 正确（不能 `feet` 代替 `feat`）
- [ ] scope 准确反映了受影响的模块
- [ ] description 具体可理解（"修复了X问题" 而非 "修了点东西"）
- [ ] 破坏性变更用 `!` 或 `BREAKING CHANGE:` footer
- [ ] 如果是 revert，使用 `revert:` 类型 + Ref 引用被 revert 的 commit SHA

### Step 4: 变更范围检查（🟡 P1）

- [ ] 仅包含本次目标相关的文件（不夹带私货）
- [ ] 如果包含无关文件 → 拆分为独立提交或用 `git add -p` 分段提交
- [ ] 新增文件是否有对应的测试/文档？
- [ ] 删除文件是否从其他引用中同步移除？

### Step 5: 业务一致性检查（🟢 P2）

- [ ] 代码变更是否符合 commit message 声称的目标
- [ ] 边界条件和错误路径是否覆盖
- [ ] 如果是修复：修复了根因还是只修了表面？
- [ ] 回滚方案：如果出问题，回滚是否有副作用？

### Step 6: 完整性检查（🟢 P2）

```bash
# 检查是否有未 add 的文件
git status --short

# 检查版本号（如果是官方发布）
grep "version" pyproject.toml 2>/dev/null | head -1
grep "__version__" */__init__.py 2>/dev/null | head -1

# 检查是否有需要更新的 CHANGELOG
find . -name "CHANGELOG*" -o -name "RELEASE*" 2>/dev/null | head -3 || echo "⚠️ 没有 CHANGELOG/RELEASE 文件"
```

## 输出报告格式

每次检查后输出结构化的报告：

```markdown
## 📋 提交质量检查报告

### 🔴 P0 安全检查: {PASS/FAIL}
- [x] 无硬编码密码/Token
- [x] .gitignore 覆盖敏感文件
- [ ] Git 历史无敏感信息 → ⚠️ 需清理

### 🔴 P0 文档一致性: {PASS/FAIL}
- [ ] 代码改了什么 →
- [ ] 需要更新什么文档 →
- [ ] 实际更新了什么 →

### 🟡 P1 Commit Message: {PASS/FAIL}
- type: {type}
- scope: {scope}
- description: {desc}

### 🟡 P1 变更范围: {PASS/FAIL}
- [ ] 单次提交单一职责

### 🟢 P2 业务一致性: {PASS/FAIL}
- [ ] 符合目标

### 🟢 P2 完整性: {PASS/FAIL}
- [ ] 无遗漏文件

**建议: {通过/修改后提交/禁止提交}**
```

## 判断标准

| 结论 | 条件 | 操作 |
|------|------|------|
| ✅ **通过** | P0 全部通过 + P1 至少 1 项通过 | 可以提交 |
| ⚠️ **修改后提交** | P0 全部通过 + P1 部分未通过 | 建议修改但可提交 |
| 🚫 **禁止提交** | 任何 P0 不通过 | 修复后才能提交 |

## 🚩 实战经验教训 (v1.1.0 新增)

### 1. git `-S` pickaxe 的脱敏陷阱

`git diff --cached -S "token"` 可以找到包含 token 的提交，但 git 在 diff 输出中**自动将敏感值脱敏为 `***`**。所以如果凭 `-S` 的输出判断是否发现敏感信息，会看到类似：

```
+API_TOKEN = "***"
```

**解决方案**：必须同时用 `git diff --cached -U1000 | grep` 做辅助检查，这个方式能看到原文。

### 2. 文档一致性是 AI 项目的最大痛点

在 AI 驱动的开发中（如 SRA 项目），最常见的提交缺陷是：**代码改了但文档没同步**。具体场景：
- 添加了同义词映射 → 忘记更新 RUNTIME.md 的"已知限制"表
- 修改了匹配阈值 → 没有在文档中记录新值
- 修复了已知问题 → 没有从文档的"已知限制"列表中移除该条

**对策**：每次代码修改后，强制对照"修改类型→必须同步的文档"表。

### 2b. API 端点声称 vs 实际实现的偏差

**典型场景**：README 中声称 `/targets` 端点存在，但实际 HTTP Handler 中从未实现过该路由。这是文档一致性检查中最容易被忽略的一类——因为 README 的 API 表是手写的，和代码没有自动关联。

**排查方法**：
```bash
# 1. 提取 README 中声明的所有端点
grep -E '^\| \`/\w+' README.md | cut -d'`' -f2

# 2. 提取实际代码中的所有路由
#    Flask/FastAPI: grep -rn '@.*\.route|@.*\.get|@.*\.post' app/
#    标准库 HTTP: grep -rn 'self.path == |def do_GET|def do_POST' *.py

# 3. 对比两份列表，标记不一致的：
#    - 文档有但代码没有 → 🔴 P0 必修
#    - 代码有但文档没有 → 🟡 P1 建议补充
```

**检查清单扩展项**（添加到文档一致性检查表）：
| 修改类型 | 必须同步的文档 | 检查方法 |
|----------|---------------|---------|
| 新增/删除/修改 API 端点 | README API 表、docs/ 相关文件 | grep 提取路由表对比 |
| 新增/删除 CLI 子命令 | README 命令表、--help 输出 | 对比 COMMANDS dict 和文档表 |

### 3. 子代理验证能发现自身盲点

用子代理作为 QA 来验证本 skill 时，发现了：
- grep 脱敏问题（上面第 1 点）
- CHANGELOG 检查用 `ls` 不够健壮（子目录中可能有）
- `.gitignore` 检查模式需要补充 `token` 模式

**启示**：**不要自己验证自己的代码**。子代理作为"不知道规则的用户"能发现设计者看不见的盲点。

### 4. Conventional Commits 常见错误

| 错误 | 示例 | 正确 |
|------|------|------|
| type 拼写错误 | `feet: add login` | `feat: add login` |
| type 遗漏冒号 | `feat add login` | `feat: add login` |
| description 太模糊 | `fix: fix stuff` | `fix: prevent null pointer on empty user list` |
| 破坏性变更未标记 | `feat: change API format` | `feat!: change API format` |
| 多个改在一起 | `feat: add login and fix typo` | 应拆为 2 个提交 |

### 5. 安全检查的优先级

| 泄露类型 | 严重度 | 检测方式 |
|----------|--------|----------|
| GitHub Token (`ghp_`, `gho_`) | 🔴 致命 | `-S "ghp_"` |
| API Key (`sk-`, `gph_`) | 🔴 致命 | `-S "sk-"` + grep |
| 数据库密码 | 🔴 致命 | `-S "password"` + grep |
| 内网地址/域名 | 🟡 中等 | 需人工检查 |
| 测试凭据 | 🟡 中等 | `-S "test.*key\|staging.*pass"` |
| 内部实现细节 | 🟢 低 | 需人工判断 |

### 6. 输出报告的结构化重要性

每次检查的输出应该是**可审计的、可比较的**结构化报告。使用本文档中定义的报告模板，可以让：
- 同一项目的不同提交之间有可比性
- 团队可以追踪"哪类问题最常出现"
- 积累数据后可以针对性地改进 CI 流程

### 8. CI 环境测试适配 — Hermes 依赖测试的降级模式

**问题场景**：在 GitHub Actions CI 中运行 Hermes 项目的测试时，`~/.hermes/skills` 目录不存在，导致依赖该目录的测试类（如 `TestAdvisor`）在 `setup_method` 中就崩溃，`self.advisor` 从未被初始化。

**根因**：测试的 `setup_method()` 只有一条初始化路径——读取 `~/.hermes/skills`。当目录不存在时，什么都不创建，导致后续测试 `assert self.advisor is not None` 直接 AttributeError。

**修复模式**（双模式初始化）：

```python
def setup_method(self):
    skills_dir = os.path.expanduser("~/.hermes/skills")
    if os.path.exists(skills_dir):
        # 本地模式：使用真实技能目录
        self.advisor = SkillAdvisor(skills_dir=skills_dir)
        self.has_real_skills = True
    else:
        # CI 模式：用临时空目录兜底，确保对象初始化
        import tempfile
        self._tmp_skills = tempfile.mkdtemp()
        self.advisor = SkillAdvisor(skills_dir=self._tmp_skills)
        self.has_real_skills = False

def teardown_method(self):
    if hasattr(self, '_tmp_skills') and os.path.exists(self._tmp_skills):
        import shutil
        shutil.rmtree(self._tmp_skills, ignore_errors=True)
```

**关键原则**：
- **对象始终创建** — 不要出现 `AttributeError: ... has no attribute 'advisor'`
- **用 `has_real_skills` 标志位** — 依赖真实环境的测试（如推荐 PDF/飞书）用 `if not self.has_real_skills: return` 跳过
- **清理临时目录** — 用 `teardown_method` 回收临时目录
- **本地和 CI 都要过** — 修复后在本地 `pytest tests/ -q` 确认全绿，再推 CI

**为什么不用 mock？** 真实技能目录的测试是集成测试，mock 会丢失真实匹配行为。双模式初始化保留了本地集成测试的价值，同时保证 CI 不自爆。

### 7. 使用场景检查时间（原序号顺延）

**不要在 CI 阶段才做这些检查**——那时已经来不及了。最佳时机：

| 时机 | 做什么 | 谁执行 |
|------|--------|--------|
| **git commit 前** | Step 1 安全检查（快速） | 开发者 / AI Agent |
| **git push 前** | Step 1-4 完整检查 | 开发者 / AI Agent |
| **PR 创建时** | Step 1-6 全面检查 + 输出报告 | AI Agent |
| **CI 流程** | 自动化验证（补充而非替代） | CI 系统 |
## 参考

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [GitHub PR Best Practices](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/best-practices-for-pull-requests)
- [SemVer](https://semver.org/)
