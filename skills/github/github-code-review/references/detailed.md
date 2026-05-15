# Detailed Reference

## 2. Reviewing a Pull Request on GitHub

### View PR Details

**With gh:**

```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
```

**With git + curl:**

```bash
PR_NUMBER=123

# Get PR details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "
import sys, json
pr = json.load(sys.stdin)
print(f\"Title: {pr['title']}\")
print(f\"Author: {pr['user']['login']}\")
print(f\"Branch: {pr['head']['ref']} -> {pr['base']['ref']}\")
print(f\"State: {pr['state']}\")
print(f\"Body:\n{pr['body']}\")"

# List changed files
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

### Check Out PR Locally for Full Review

This works with plain `git` — no `gh` needed:

```bash
# Fetch the PR branch and check it out
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Now you can use read_file, search_files, run tests, etc.

# View diff against the base branch
git diff main...pr-123
```

**With gh (shortcut):**

```bash
gh pr checkout 123
```

**If the branch can't be fetched** (remote ref not found, force-pushed, or deleted):

```bash
# Fall back to PR diff only, work from the text diff
gh pr diff 123 > /tmp/pr-123.diff
gh pr diff 123 --name-only
gh pr view 123 --json title,body,state,author,createdAt,additions,deletions,files,commits,reviews
```

---

### 🔬 Verify PR Claims Against Actual Behavior

**🚨 Don't trust commit messages at face value.** PR descriptions and commit messages may contain inaccurate claims about behavior, performance, or correctness. Always verify by running the actual code path.

#### Step 1: Install any new dependencies introduced by the PR

```bash
# Check pyproject.toml for new deps
grep -A5 "dependencies\|optional-dependencies" pyproject.toml

# Install for testing
pip install jieba requests  # example: whatever the PR adds
```

#### Step 2: Reproduce the claimed behavior

Take the exact examples from the commit message and run them:

```bash
# Python example
python3 -c "
# Replicate the exact code path from the PR diff
import re

# Copy the new function/logic from the diff
# (work from gh pr diff, or use read_file on the changed file)

text = 'example input from commit message'
result = your_function(text)
print('Result:', result)

# Assert the claim
assert 'expected_word' in result, f'PR claims {expected_word} but actual result is {result}'
"
```

#### Step 3: Run existing tests with the new code path

```bash
# Run the full test suite
python -m pytest tests/ -q --tb=short

# Run specifically relevant tests
python -m pytest tests/test_indexer.py -v

# If the PR adds an optional dependency, install it before testing
# to ensure the new code path is exercised
```

#### Step 4: Document discrepancies found

If the actual behavior differs from what the PR claims:

| PR Claim | Actual Behavior | Severity |
|:---------|:----------------|:--------:|
| jieba produces '公众号' | jieba produces '公众' + '号' | 🔴 Inaccurate example |
| Feature improves X by Y% | Measured improvement is Z% | 🟡 Needs correction |

Reference these findings in your review output. The discrepancy itself is often more valuable than the PR's stated intent.

#### Real-world example (SRA PR #17):

The commit message claimed jieba on "帮我写一篇公众号文章" produces `['帮', '我', '写', '一篇', '公众号', '文章']`. Verification revealed **jieba 0.42.1 with default dictionary** produces `['帮', '我', '写', '一篇', '公众', '号', '文章']` — `公众号` is NOT in jieba's default dictionary. The claim was incorrect, and the fix required `jieba.add_word('公众号')` or a custom dictionary. Without this verification step, the misleading example would have been merged into the commit history.

### Leave Comments on a PR

**General PR comment — with gh:**

```bash
gh pr comment 123 --body "Overall looks good, a few suggestions below."
```

**General PR comment — with curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments \
  -d '{"body": "Overall looks good, a few suggestions below."}'
```

### Leave Inline Review Comments

**Single inline comment — with gh (via API):**

```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')

gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="This could be simplified with a list comprehension." \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

**Single inline comment — with curl:**

```bash
# Get the head commit SHA
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -d "{
    \"body\": \"This could be simplified with a list comprehension.\",
    \"path\": \"src/auth/login.py\",
    \"commit_id\": \"$HEAD_SHA\",
    \"line\": 45,
    \"side\": \"RIGHT\"
  }"
```

### Submit a Formal Review (Approve / Request Changes)

**With gh:**

```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
gh pr review 123 --comment --body "Some suggestions, nothing blocking."
```

**With curl — multi-comment review submitted atomically:**

```bash
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"COMMENT\",
    \"body\": \"Code review from Hermes Agent\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"Use parameterized queries to prevent SQL injection.\"},
      {\"path\": \"src/models/user.py\", \"line\": 23, \"body\": \"Hash passwords with bcrypt before storing.\"},
      {\"path\": \"tests/test_auth.py\", \"line\": 1, \"body\": \"Add test for expired token edge case.\"}
    ]
  }"
```

Event values: `"APPROVE"`, `"REQUEST_CHANGES"`, `"COMMENT"`

The `line` field refers to the line number in the *new* version of the file. For deleted lines, use `"side": "LEFT"`.

---


> 🔍 **## 3. Review Checklist** moved to [references/detailed.md](references/detailed.md)
