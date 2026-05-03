---
name: github-issues
description: Create, manage, triage, and close GitHub issues. Search existing issues, ad...
version: 1.1.0
triggers:
- github issues
- github-issues
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - GitHub
    - Issues
    - Project-Management
    - Bug-Tracking
    - Triage
    related_skills:
    - github-auth
    - github-pr-workflow
---
# GitHub Issues Management

Create, search, triage, and manage GitHub issues. Each section shows `gh` first, then the `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repo with a GitHub remote, or specify the repo explicitly

### Setup

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Viewing Issues

**With gh:**

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**With curl:**

```bash
# List open issues
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:  # GitHub API returns PRs in /issues too
        labels = ', '.join(l['name'] for l in i['labels'])
        print(f\"#{i['number']:5}  {i['state']:6}  {labels:30}  {i['title']}\")"

# Filter by label
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&labels=bug&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"

# View a specific issue
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  | python3 -c "
import sys, json
i = json.load(sys.stdin)
labels = ', '.join(l['name'] for l in i['labels'])
assignees = ', '.join(a['login'] for a in i['assignees'])
print(f\"#{i['number']}: {i['title']}\")
print(f\"State: {i['state']}  Labels: {labels}  Assignees: {assignees}\")
print(f\"Author: {i['user']['login']}  Created: {i['created_at']}\")
print(f\"\n{i['body']}\")"

# Search issues
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/search/issues?q=authentication+error+repo:$OWNER/$REPO" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin)['items']:
    print(f\"#{i['number']}  {i['state']:6}  {i['title']}\")"
```


> 🔍 **## 2. Creating Issues** moved to [references/detailed.md](references/detailed.md)
