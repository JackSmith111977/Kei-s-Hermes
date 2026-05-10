---
name: commit-quality-check
description: "GitHub 项目提交前文档与业务一致性检查 + 提交质量检查清单。涵盖 Conventional Commits 规范验证、安全红线扫描、文档一致性检查、变更范围评估。适用于任何需要做 git commit 或 PR 前自检的场景。"
version: 1.2.0
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
  - 忘了一致性检查
  - 又忘了
  - 还没检查
  - 检查一下提交
  - self review
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

**🚨 强制触发条件**：完成任何产生文件变更的任务后，在向用户汇报前必须触发此检查。
即使不涉及 git commit，也需要做文档一致性和安全检查。

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

### Step 6b: 裸 except 扫描（🔴 P0 — 新增）

**🚨 禁止提交包含 `except: pass` 的代码。所有异常必须区分类型并做适当处理。**

```bash
# 1. 扫描本次变更中的裸 except
git diff --cached -U0 | grep -E '^\+.*except\s*:' | grep -v 'Exception\|Error\|OSError\|KeyError\|ValueError\|TypeError\|JSONDecode\|ProcessLookup\|FileNotFound\|BlockingIO\|StopIteration\|KeyboardInterrupt\|SystemExit' || echo "✅ 无裸 except"

# 2. 如果发现裸 except，逐行检查是否满足以下任一条件：
#    - 可以指定具体的异常类型（首选）
#    - 必须用 logger 记录异常信息（至少 debug 级别）
#    - 在 SUPPRESSED_EXCEPTIONS 白名单中（需有注释说明为什么允许静默）
```

**裸 except 处理规范：**

| 原始代码 | 改进后 | 说明 |
|----------|--------|------|
| `except:` | `except OSError:` | 指定异常类型 |
| `except:` | `except Exception as e: logger.warning("%s", e)` | 记录日志 |
| `except:` | `except (FileNotFoundError, json.JSONDecodeError):` | 多类型捕获 |
| `except:` | `except: logger.debug("expected")` | ❌ 仍不达标，需指定类型 |

**排查方法（批量扫描项目）：**
```bash
# 全量扫描裸 except
grep -rn "^\s*except\s*:\s*$" --include="*.py" . | grep -v __pycache__ | grep -v fixtures

# 全量扫描 except: pass
grep -rn "except:.*pass" --include="*.py" . | grep -v __pycache__ | grep -v fixtures

# 验证无裸 except 残留
if grep -rn "^\s*except\s*:\s*$" --include="*.py" . | grep -v __pycache__ | grep -q .; then
    echo "❌ 发现裸 except，请修复后再提交"
    exit 1
fi
```

### Step 7: 完整性检查（🟢 P2）

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

### 7. 使用场景检查时间

**不要在 CI 阶段才做这些检查**——那时已经来不及了。最佳时机：

| 时机 | 做什么 | 谁执行 |
|------|--------|--------|
| **完成任务后、汇报前** | Step 1-2 快速检（无 git 时也要跑） | AI Agent **必须先跑** |
| **git commit 前** | Step 1 安全检查（快速） | 开发者 / AI Agent |
| **git push 前** | Step 1-4 完整检查 | 开发者 / AI Agent |
| **PR 创建时** | Step 1-6 全面检查 + 输出报告 | AI Agent |
| **CI 流程** | 自动化验证（补充而非替代） | CI 系统 |

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

### 9. 🚨 致命陷阱：完成任务后直接汇报，跳过自检

**场景**：AI Agent 完成了一个功能实现（建文件、改配置、写文档），然后直接向用户汇报完成，**没有先跑 commit-quality-check**。

**后果**：用户发现需要追着问「你有做一致性检测吗」，说明 Agent 的完成报告不完整、不可信。

**根因**：Agent 认为「没有 git commit → 不需要质量检查」。但文档一致性检查和变更范围检查**不依赖 git**——即使只是对比「我做了什么」和「文档说了什么」就能发现问题。

**对策**：
1. **触发时机前置**：任何产生文件变更的任务完成后，在汇报前先跑 Step 2（文档一致性）+ Step 4（变更范围）
2. **即使不 commit 也要检**：系统配置文件（如 `~/.config/systemd/`）、部署脚本等不在 repo 中的变更也要做一致性检查
3. **汇报包含检查报告**：向用户汇报时，附上质量检查结果，让用户看到「我已自检过」
4. **自我问责**：如果用户问「你检查了吗」→ 立即补跑检查 + 把教训加到 skill 的 pitfalls 中

### 9b. 🔥 实战案例：写完功能直接 commit，忘了版本号一致性检查

**场景**：在 SRA 项目中新增了 `upgrade` 和 `uninstall` 两个 CLI 命令。写完代码后直接 `git commit`，没有先做一致性检查。

**后果**：用户提醒「你又忘了一致性检查了！」，补跑后发现 `daemon.py` 有三处硬编码版本号 `"1.1.0"`，与 `pyproject.toml` 的 `1.2.1` 不一致。

**教训**：
- **提交必须在自检之后**，不是自检在提交之后
- 修改了 API 端点/CLI 命令 → 必须检查 HELP 文本、docstring、COMMANDS 注册表三者是否一致
- 修改了代码逻辑 → 必须检查版本号/常量是否有多处散落的硬编码
- 即使只是「新增功能」而非「修 Bug」，自检也不可跳过

**版本一致性检查法**：
```bash
# 检查项目中所有硬编码版本号
grep -rn '"1\.' --include="*.py" --include="*.toml" --include="*.json" . | grep -v __pycache__ | grep -v '.bak'
# 对比 pyproject.toml 和 __init__.py 的版本
grep "version" pyproject.toml
grep "__version__" */__init__.py
# 检查 daemon/HTTP handler 中是否有遗漏的硬编码版本
grep -rn '"version"' --include="*.py" . | grep -v __pycache__
```

### 10. 🔥 实战案例：系统化消除 `except: pass` 的经验

**场景**：在 SRA 项目中发现了 16 处 `except: pass`，散布在 4 个模块中（daemon.py 10 处、indexer.py 2 处、memory.py 1 处、cli.py 1 处、sra-eval 脚本 2 处）。

**系统化消除步骤**：

```
Step 1: 全量扫描定位
    grep -rn "^\s*except\s*:\s*$" --include="*.py" . | grep -v __pycache__
    
Step 2: 分类处理策略（按严重程度）
    🔴 关键路径（YAML 解析、配置加载、状态写入）→ 改为特定异常 + logger.warning + 向上传播
    🟡 良性路径（socket close、文件清理）→ 改为 OSError + logger.debug
    🟢 回退路径（JSON 解析失败 → 返回空 dict）→ 改为 json.JSONDecodeError + logger.debug
    
Step 3: 逐处修复
    16 处平均 2 分钟/处 = 约 30 分钟总工作量
    
Step 4: 验证
    - 正则扫描确认无残留：grep -rn "^\s*except\s*:\s*$" ...
    - 全量测试确认无回归
```

**经验总结**：
- 不要在修复阶段做「顺便优化」——每处只改 except 行，不改其他逻辑
- 裸 except 的「罪魁祸首」通常是懒编程，根源是「不想想这个异常会是什么」
- 修复时反问自己：这行代码可能抛什么异常？然后精确捕获它
- `except: pass` 是最危险的 Python 反模式之一，因为它让程序在错误状态下继续执行

### 11. 🔥 实战案例：即使 skill 有警示，还是会忘——关键是把检查嵌入项目流程文档

**场景**：在 SRA 项目中完成了 SRA-003-13（HTTP 架构重构+异常处理），测试全绿后直接 git commit + push + 向主人汇报。主人反问「你又忘了一致性检查了？」。

**根因分析**：

```
表面原因：boku 忘了加载 commit-quality-check
  ↓
深层原因：开发流程中没有把质量检查作为「不可跳过的步骤」
  ↓
根本原因：流程只存在于 skill 文档中，没有被写进项目架构文档作为强制铁律
```

**教训**：
1. **靠「记得」是 unreliable 的** — 即使 skill 有 §9 的警示，任务密集时仍然会忘
2. **必须把质量检查嵌入项目开发流程文档** — 在 `ARCHITECTURE.md` 或 `CONTRIBUTING.md` 中明确定义开发步骤的顺序
3. **步骤必须不可跳过、不可重排** — 用编号①→②→③... 的形式，让每一步依赖前一步完成

**对抗措施**（已在 SRA 项目中实施）：

在项目 `docs/ARCHITECTURE.md` 中新增 §8.1 开发流程铁律：

```
① 实现代码 + 测试
    ↓
② pytest tests/ -v 全量验证
    ↓
③ 🔴 加载 commit-quality-check → 完整质量检查  ← 这一步在 git commit 之前！
    ↓
④ 修复发现的问题
    ↓
⑤ 再次全量测试
    ↓
⑥ git commit + push
    ↓
⑦ 向主人汇报（含检查报告）
```

**关键区别**：
- 旧方案：质量检查是「建议步骤」，存在于 skill 文档中
- 新方案：质量检查是「强制步骤」，存在于项目架构文档中，与其他步骤**线性排列**

**AI Agent 的 self-fix 清单**（当用户指出「你又忘了一致性检查」时）：
1. ✅ 立即补跑质量检查（确认当前 commit 是否干净）
2. ✅ 更新项目架构文档（`ARCHITECTURE.md`），加入开发流程铁律
3. ✅ 更新 `CONTRIBUTING.md` 的 PR 自查清单
4. ✅ 将教训写入长期 memory
5. ✅ 更新 `commit-quality-check` skill 的本节内容
6. ✅ 提交流程修复（带着质量检查报告一起提交）

## 参考
- [GitHub PR Best Practices](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/best-practices-for-pull-requests)
- [SemVer](https://semver.org/)
