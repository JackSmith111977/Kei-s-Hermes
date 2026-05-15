---
name: pr-review-workflow
description: "专业 Pull Request 审查工作流 — Google 工程实践驱动的 5 阶段审查流程。涵盖范围评估、设计审查、逐文件审查、测试文档验证、最终评级。支持 CLI 审查指令、自动安全检查、结构化输出模板。"
version: 1.0.0
triggers:
  - review pr
  - 审查 PR
  - pull request review
  - pr review
  - 代码审查
  - code review
  - 审查合并请求
  - review changes
  - 审查变更
author: "Emma (小玛)"
license: MIT
tags:
  - GitHub
  - PR-Review
  - Code-Quality
  - Workflow
  - Best-Practices
---

# 🎯 PR Review 工程化工作流 v1.0

> **基于 Google Engineering Practices + 行业最佳实践**
> 核心理念：代码审查的核心是**确保代码库健康持续改善**，而非追求完美。

---

## 📋 快速导航

| 章节 | 内容 |
|:----|:-----|
| [审查流程](#-审查流程5阶段) | 5 阶段审查流程详解 |
| [审查维度](#-审查维度优先级) | 10 大审查维度优先级排序 |
| [标签系统](#-评论标签系统) | Critical/Warning/Suggestion 标签规范 |
| [CLI 操作指南](#-cli-操作指南) | gh + curl + git 实际操作命令 |
| [输出模板](#-输出模板) | 结构化审查报告模板 |
| [CI 集成](#-ci-自动化集成) | 自动化门禁配置 |
| [红色警戒](#-红色警戒区) | 常见陷阱与反模式 |

---

## 🔍 审查流程（5阶段）

### Phase 1: 范围评估 — PR 合理性检查

**目标**：确认 PR 本身是否合理，范围是否可控。

```bash
# 获取 PR 信息
gh pr view <NUMBER>
gh pr diff <NUMBER> --stat
gh pr diff <NUMBER> --name-only

# 或通过 API（无 gh）
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "
import sys, json
pr = json.load(sys.stdin)
print(f'Title: {pr[\"title\"]}')
print(f'Author: {pr[\"user\"][\"login\"]}')
print(f'State: {pr[\"state\"]}')
print(f'Body:\n{pr[\"body\"]}')
"
```

**检查清单**：
- [ ] PR 标题是否描述清楚变更内容？（符合 Conventional Commits 格式）
- [ ] PR Body 是否包含"为什么改 / 改了什么 / 怎么测试"？
- [ ] 变更行数是否合理？> 400 行应建议拆分
- [ ] 文件数量是否合理？> 15 个文件应询问原因
- [ ] 是否只包含本次目标相关变更（无夹杂私货）？

**判定**：
- 🟢 合理 → 进入 Phase 2
- 🔴 不合理 → 立即反馈，要求澄清或拆分

---

### Phase 2: 设计审查 — 从架构角度评估

**目标**：确认变更的整体设计是否合理。

```bash
# 检出 PR 分支进行本地审查
gh pr checkout <NUMBER>

# 或
git fetch origin pull/<NUMBER>/head:pr-<NUMBER>
git checkout pr-<NUMBER>
git diff main...HEAD --stat
git log main..HEAD --oneline
```

**检查清单**：
- [ ] 整体设计意图是否清晰？变更是否解决了 PR 描述的问题？
- [ ] 是否与现有系统架构一致（目录结构/依赖方向/扩展点）？
- [ ] 此功能是否应该现在添加（scope creep 检查）？
- [ ] 是否有过度设计（over-engineering）？解决的是现在的问题还是未来的问题？
- [ ] 可逆性（reversibility）：如果回滚此变更，代价有多大？

**判定**：
- 🟢 设计合理 → 进入 Phase 3
- 🔴 设计有重大问题 → **立即反馈**，避免浪费后续审查时间

---

### Phase 3: 逐文件审查 — 深入代码细节

**目标**：逐行审查核心逻辑，重点关注正确性、安全、复杂度。

```bash
# 获取具体文件 diff
gh pr diff <NUMBER> -- src/auth/login.py

# 查看完整文件（不只看diff）
git show HEAD:src/auth/login.py | head -100

# 安全检查
git diff main...HEAD | grep -n "print(\|TODO\|FIXME\|debugger"
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="

# 安全红线扫描
git diff main...HEAD -S "password" -- . || true
git diff main...HEAD -S "token" -- . || true
git diff main...HEAD -S "api_key" -- . || true
git diff main...HEAD -S "secret" -- . || true
```

**检查清单**（按优先级）：

| 优先级 | 检查项 | 检查方法 |
|:------:|:-------|:---------|
| 🔴 P0 | 安全漏洞（注入/XSS/鉴权缺失） | 人工审查 + `git diff -S` |
| 🔴 P0 | 硬编码凭据/Token/密码 | `git diff -S "token\|secret\|password"` |
| 🔴 P0 | 裸 exception（如 `except: pass`） | `grep -n "except:" *.py` |
| 🔴 P0 | **PR 声称 vs 实际行为验证** — 不轻信 commit message 中的行为描述 | 运行实际代码路径验证示例，详见 `references/verify-pr-claims.md` |
| 🟡 P1 | 逻辑正确性（边界/异常/并发） | 人工审查 |
| 🟡 P1 | N+1 查询/资源泄漏 | 人工审查 + 数据库查询分析 |
| 🟡 P1 | 阻塞操作在异步代码中 | `grep -n "time.sleep\|requests\.\|open("` |
| 🟢 P2 | 命名清晰度 | 人工审查 |
| 🟢 P2 | 魔法数字/硬编码字符串 | `grep -n "[0-9]\{4,}" *.py` |
| 🟢 P2 | 死代码/未使用导入 | 人工审查 + `vulture` |
| 🟢 P2 | 注释解释 WHY（不是 WHAT） | 人工审查 |

---

### Phase 4: 测试与文档验证

**目标**：确认测试覆盖充分、文档同步更新、CI 通过。

```bash
# 运行测试
pytest tests/ -q --tb=short

# CI 检查（如果有 CI 工具）
gh pr checks <NUMBER>

# API 端点一致性检查
grep -rn "def \|@router\|@app\." src/ --include="*.py"
grep -E "^\| \`/" README.md | cut -d'`' -f2
```

**检查清单**：
- [ ] 新代码有对应的单元测试？
- [ ] Bug 修复有回归测试？
- [ ] 测试验证的是正确行为（不通过时会失败）？
- [ ] 测试覆盖了边界条件和异常路径？
- [ ] CI 全部通过（lint/test/build）？
- [ ] 文档同步更新（README/CHANGELOG/API 文档）？
- [ ] 如果删除了代码，相关文档也被清理？
- [ ] 如果修改了 API 端点，README 的 API 表已更新？

---

### Phase 5: 最终评级

**目标**：根据审查结果确定 PR 状态。

```bash
# 批准 PR
gh pr review <NUMBER> --approve --body "LGTM! 详见评论。"
gh pr review <NUMBER> --request-changes --body "有一些需要修改的问题。"
gh pr review <NUMBER> --comment --body "观察备注。"
```

| 评级 | 条件 | 操作 |
|:----:|:----|:----|
| ✅ **APPROVED** | 无 P0 问题，P1/P2 可选 | `--approve` |
| 🔴 **CHANGES_REQUESTED** | 有 P0 问题未解决 | `--request-changes` |
| 💬 **COMMENT** | 草案/信息性/不确定 | `--comment` |

**LGTM With Comments**（Google 模式）：当满足以下任一条件时可提前批准：
- 信任开发者会正确处理剩余评论
- 评论是可选/非阻塞的
- 评论是微小调整（排序 import、修复 typo、删除未用依赖）

---

## 🎯 审查维度优先级

```
优先级排序（从高到低）：
┌────────────────────────────────────────────────────────────┐
│ 🔴 Tier 1: 必须检查（不通过则阻塞）                          │
│   1.  Design     — 整体设计/架构是否合理                     │
│   2.  Correctness — 逻辑完整性/边界/异常/并发               │
│   3.  Security   — 注入/鉴权/凭据/敏感数据                   │
├────────────────────────────────────────────────────────────┤
│ 🟡 Tier 2: 应该检查（影响合并质量）                          │
│   4.  Tests      — 测试覆盖/有效性/回归                      │
│   5.  Complexity — 是否过度设计/可理解性                     │
│   6.  Performance — N+1/泄漏/阻塞/复杂度                     │
├────────────────────────────────────────────────────────────┤
│ 🟢 Tier 3: 建议检查（持续改进）                              │
│   7.  Naming     — 命名清晰度/注释 WHY                      │
│   8.  Consistency — 与现有代码一致                           │
│   9.  Docs       — README/CHANGELOG/API 同步                 │
│   (10) Style     — 🔄 完全交给自动化工具（linter/formatter） │
└────────────────────────────────────────────────────────────┘
```

---

## 🏷️ 评论标签系统

| 标签 | 含义 | 是否阻塞 | 示例 |
|:----:|:-----|:--------:|:-----|
| 🔴 **Critical** | 必须修复才能合并 | ✅ | `🔴 Critical: SQL 注入风险` |
| ⚠️ **Warning** | 应该修复 | 🟡 通常 | `⚠️ Warning: 未捕获可能的 KeyError` |
| 💡 **Suggestion** | 改进建议 | ❌ | `💡 Suggestion: 这可以用列表推导简化` |
| 💬 **Question** | 需澄清 | ❌ | `💬 Question: 为什么这里用了可变默认参数？` |
| 📌 **Nit:** | 非强制微调 | ❌ | `📌 Nit: 变量名用 camelCase 保持统一` |
| ✅ **Nice** | 正向反馈 | ❌ | `✅ Nice: 异常处理写得很优雅` |

**Google 的 `Nit:` 惯例**：来自 Google eng-practices，用于标记纯个人偏好/教育性评论，不强制解决。

---

## 📝 输出模板

### 审查总结评论格式

```markdown
## 🔍 PR 审查报告

**PR:** [#{NUMBER}]({URL}) — {TITLE}
**审查评级:** {APPROVED ✅ / CHANGES_REQUESTED 🔴 / COMMENT 💬}
**文件变更:** {N} 个文件 (+{A} -{D})

---

### 🔴 Critical（{N} 项）
<!-- 必须修复才能合并 -->
- **{file}:{line}** — {问题描述}。{修复建议}

### ⚠️ Warnings（{N} 项）
<!-- 应该修复，非严格阻塞 -->
- **{file}:{line}** — {问题描述}

### 💡 Suggestions（{N} 项）
<!-- 非阻塞改进建议 -->
- **{file}:{line}** — {改进建议}

### ✅ Looks Good
<!-- 做得好的地方 — 正向反馈 -->
- {值得称赞的方面}

---

**审查用时:** {N} 分钟
*Reviewed by Hermes Agent — PR Review Workflow v1.0*
```

### 内联评论格式

```markdown
🔴 **Critical:** 用户输入直接拼接到 SQL 查询——使用参数化查询防止注入。
⚠️ **Warning:** 此异常被静默吞没。至少用 logger 记录。
💡 **Suggestion:** 可用字典推导简化：`{k: v for k, v in items if v is not None}`
📌 **Nit:** 命名为 `process_data` 略泛，建议 `validate_user_input`。
✅ **Nice:** 巧用上下文管理器——确保了异常时的清理。
```

---

## 💬 审查沟通 — PR 不通过时的标准做法

> **核心原则**：审查不是挑错，而是**一起把代码变好**。

### 审查结论分类

| 结论 | GitHub 操作 | 含义 |
|:----|:-----------|:-----|
| ❌ **Changes Requested** | `gh pr review N --request-changes` | 有 P0 问题，必须修改才能合并 |
| 💬 **Comment** | `gh pr review N --comment` | 提建议/问题，不阻塞合并，或 PR 仍在草案阶段 |
| ✅ **Approve** | `gh pr review N --approve` | 可以直接合并（或 LGTM With Comments） |

### 🚫 Request Changes 的操作规范

当 PR 有 P0 问题时，按此流程处理：

**1. 确认 Token 有写权限**

```bash
# 检查 token 能否提交 Review
gh pr review <NUMBER> --comment --body "test" 2>&1 || echo "❌ Token 无 PR write 权限"

# 如果失败（"Resource not accessible by personal access token"）：
# → 需要 Classic PAT（Token 创建页面选择 "Tokens (classic)"）
# → 或 Fine-grained PAT：Repository permissions → Pull requests → Read and write
# 详见 github-auth skill 的 §Token 类型说明
```

**2. 审查内容结构**

```
## ❌ Request Changes

### 感谢贡献 + 🟢 肯定的部分（先夸）
- [方向/设计/实现方式] 做得好的地方

### 🔴 必须修复（P0）
1. 问题描述 → 根因 → 建议修复方案
2. ...

### 🟡 建议修改（P1）
- ...

### 🟢 可选优化（P2）
- ...

期待 updated 后再次审查！🎉
```

**3. 沟通态度**

PR 被拒绝时，贡献者的心理状态通常是：
> 「我花了时间写代码 → 被拒绝 → 不爽」

Review 的 Message 应该传达：
> 「**感谢花时间贡献**。不是做错了，而是还没达到合并标准。**方向完全正确**，改完后就是一个高质量的 PR」

| 原则 | 解释 |
|:-----|:------|
| 🚫 **不直接改 PR 代码** | 除非是合作者，否则不 push 到别人的分支 |
| 💬 **问题说清楚「为什么」** | 不光说「这个不对」，要说「因为…会导致…建议…」 |
| 🎯 **区分阻塞和非阻塞** | P0 = Request Changes，P1/P2 = Comment |
| 🙏 **肯定贡献价值** | 先夸再指问题，PR 作者才愿意继续改 |
| 🔄 **约定回应期限** | 「请在一周内更新，否则 PR 可能被关闭」 |

### 实战模板

```bash
# 用 gh CLI 提交 Request Changes
gh pr review <NUMBER> --request-changes -b "$(cat /tmp/review.md)" -R owner/repo

# 或直接用 API 提交（token 需有 pull_requests: write）
HEAD_SHA=$(gh pr view <NUMBER> --json headRefOid --jq '.headRefOid')
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"REQUEST_CHANGES\",
    \"body\": \"$(cat /tmp/review.md | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')\"
  }"
```

### 🔴 陷阱：GitHub Token 权限不足

**现象**：执行 `gh pr review N --request-changes` 时报错：
```
failed to create review: GraphQL: Resource not accessible by personal access token (addPullRequestReview)
```

**根因**：当前 GitHub Token 对 PR 操作只有读取权限，没有写入权限。

**快速诊断**：
```bash
# 检查能否创建 issue comment（PR 是最低写操作）
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments \
  -d '{"body": "test"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','OK'))"
```

**修复**：
- 如果是 Classic PAT → 勾选 `repo` scope（包含 full access）
- 如果是 Fine-grained PAT → **Repository permissions → Pull requests → Read and write**

> 详见 `github-auth` skill 的 §Token 类型说明——已在 Phase 0 中有专门介绍。

---

## 🚀 CLI 操作指南

### 基本操作

```bash
# 环境检测
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # 从 git credential 获取 token
  GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | \
    sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

### gh CLI（推荐）

```bash
# 查看 PR 详情
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
gh pr diff 123 -- src/auth.py  # 只看某个文件

# 检出 PR 本地
gh pr checkout 123

# 审查操作
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "需要修改"
gh pr review 123 --comment --body "观察备注"

# 查看 CI 状态
gh pr checks 123

# 内联评论（通过 API）
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')
gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="🔴 Critical: SQL注入风险" \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

### git + curl（无 gh 时）

```bash
# 获取 PR 详情
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER

# 获取变更文件列表
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")
"

# 提交正式审查
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{\"commit_id\": \"$HEAD_SHA\", \"event\": \"COMMENT\", \"body\": \"审查报告\", \"comments\": [...]}"
```

---

## 🤖 CI 自动化集成

### GitHub Actions 自动审查

在仓库中创建 `.github/workflows/pr-review.yml`：

```yaml
name: PR Review Automation
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      # L1: 机械检查（完全自动化）
      - name: Lint & Format Check
        run: |
          pip install ruff
          ruff check --output-format=github .

      - name: Security Scan
        run: |
          # 扫描硬编码凭据
          git diff origin/main...HEAD -S "token\|secret\|password\|api_key" -- . || true

      # L2: 测试覆盖门禁
      - name: Test Coverage
        run: |
          pytest tests/ --cov=src --cov-fail-under=80

      # L3: 审查报告（给 AI Agent 的入口）
      - name: Post Review Summary
        uses: actions/github-script@v7
        with:
          script: |
            const body = `## 🤖 自动审查摘要
            | 检查项 | 状态 |
            |:-------|:----:|
            | Lint 检查 | ✅ |
            | 安全扫描 | ✅ |
            | 测试覆盖 | ✅ |
            
            > ⚡ 此审查为自动化辅助。架构/设计/复杂逻辑需人工审查。`;
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.payload.pull_request.number,
              body
            });
```

### AGENTS.md 仓库审查指南

在仓库根目录创建 `AGENTS.md`，定义审查标准：

```markdown
## Review Guidelines

### 本仓库的审查重点
- 安全敏感（auth/payment 模块需额外注意）
- 性能敏感（API 端点为高并发场景）
- 样式遵循 PEP 8（已有 ruff 自动化）

### 禁止模式
- 裸 `except:` 禁止（必须指定异常类型）
- 硬编码凭据禁止
- 生产代码中的 `print()` 调试禁止

### 测试要求
- 新功能必须有单元测试，覆盖 >= 80%
- Bug 修复必须有回归测试
```

---

## 🔴 红色警戒区

### 常见反模式（Anti-Patterns）

| 反模式 | 问题 | 最佳实践 |
|:-------|:-----|:---------|
| PR 过大（> 400 行） | 审查者难以全面覆盖 | 拆分为多个小 PR |
| 混合变更 | 重构 + 新功能 + 格式化在同个 PR | 单一职责 PR |
| 无测试 | 无法验证改动的正确性 | 代码与测试同 PR |
| 忽略样式 | 格式不统一导致审查噪音 | 用 linter 自动化 |
| 审查太慢（> 1d） | 阻塞团队进度 | 1 个工作日内响应 |
| 追求完美 | 阻塞合并降低团队速度 | 接受"更好"而非"完美" |
| 跳过安全检查 | 引入安全漏洞 | 自动 + 人工双检 |
| 不读完整代码 | 遗漏系统级影响 | 至少读核心文件的完整上下文 |

### 自身审查的陷阱

**🚨 不要只审查 diff——要看完整文件的上下文**：一个 4 行的新增可能意味函数已经太长需要重构。

**🚨 不要忽视正向反馈**：只说不好的会降低团队士气。做得好的地方也要标注。

**🚨 不理解就放行**：如果你不理解某段代码，未来的维护者也不会。要求开发者简化或加注释。

**🚨 跳过 Phase 1 直接看代码**：先确认 PR 本身是否合理。如果方向错了，代码审查就是浪费。

**🚨 在异步代码中忽略阻塞操作**：`time.sleep()`、`requests.get()`、文件 IO 在事件循环中会阻塞整个进程。

---

## 📚 参考来源

- [Google Engineering Practices — Code Review](https://google.github.io/eng-practices/review/reviewer/)
- [Google — What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Google — Navigating a CL in review](https://google.github.io/eng-practices/review/reviewer/navigate.html)
- [Google — The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Google — Speed of Code Reviews](https://google.github.io/eng-practices/review/reviewer/speed.html)
- [GitHub — Configuring automatic code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/configure-automatic-review)
- [Pull Checklist — 8 Core Components](https://www.pullchecklist.com/posts/github-pr-review-checklist)
- [DEV — The Code Review Checklist](https://dev.to/apaksh/the-code-review-checklist-every-engineering-team-needs-283d)
