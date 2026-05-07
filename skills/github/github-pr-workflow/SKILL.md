---
name: github-pr-workflow
description: Full pull request lifecycle — create branches, commit changes, open PRs, mo...
version: 1.1.0
triggers:
- github pr workflow
- github-pr-workflow
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - GitHub
    - Pull-Requests
    - CI/CD
    - Git
    - Automation
    - Merge
    related_skills:
    - github-auth
    - github-code-review
---
# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle. Each section shows the `gh` way first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

This part is pure `git` — identical either way:

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

## 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

## 3. Pushing and Creating a PR

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

## 🚩 PR 创建失败排查

### 症状：`Resource not accessible by personal access token`

gh 和 curl 都报这个错，说明当前 GitHub token **没有 pull requests write 权限**。

### 根因

GitHub 有两种 Personal Access Token：

| Token 类型 | 权限模型 | 创建 PR 所需 |
|:-----------|:---------|:-------------|
| **Classic PAT** | 粗粒度 scope（如 `repo`） | `repo` scope 包含 PR 写权限 ✅ |
| **Fine-grained PAT** | 细粒度按权限开关 | 必须显式开启 **"Pull requests: Read and write"** 🔧 |

如果你用的是 fine-grained PAT（以 `github_pat_` 开头），即使仓库权限显示 `Admin: true`，也不代表能创建 PR —— 因为 fine-grained PAT 的权限是**按功能模块独立授权**的。

### 解决方案

#### 方案 A：在 GitHub 上给 token 添加权限
1. 打开 https://github.com/settings/tokens
2. 找到你的 fine-grained PAT
3. 在 **Repository permissions** → **Pull requests** → 改为 **Read and write**
4. 等待几秒后重试

#### 方案 B：提供手动创建 PR 的链接（Token 权限不可改时）
```bash
BRANCH=$(git branch --show-current)
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')

echo "👉 https://github.com/$OWNER_REPO/compare/master...$BRANCH?expand=1"
echo ""
echo "📝 PR Title:"
echo "<copy from git log -1 --format=%s>"
echo ""
echo "📝 PR Body (复制以下内容):"
echo "---"
echo "## 概述"
echo ""
echo "<简要说明改了什么>"
echo "---"
```

用户打开链接后，GitHub Web UI 自动填充对比页面，点击 "Create pull request" 即可。

#### 方案 C：切换到 Classic PAT
创建一个 Classic PAT（Settings → Developer settings → Personal access tokens → Tokens (classic)），勾选 `repo` scope。然后用新 token：

```bash
# 更新 git 凭据
git remote set-url origin https://<username>:<classic-pat>@github.com/<owner>/<repo>.git
```

### 验证 token 权限

```bash
# 检查 token 类型和可用权限
TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')

# Classic PAT 会显示 OAuth scopes
curl -sI -H "Authorization: token $TOKEN" https://api.github.com/ | grep -i "x-oauth-scopes"

# Fine-grained PAT 则不会显示 scopes header，但可以尝试创建 PR 来测试
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/<owner>/<repo>/pulls \
  -d '{"title":"test","head":"<branch>","base":"master"}' | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'html_url' in d:
    print('✅ PR create OK')
else:
    print(f'❌ {d.get(\"message\", \"unknown error\")}')
"
```

> 🔍 **## 4. Monitoring CI Status** moved to [references/detailed.md](references/detailed.md)
