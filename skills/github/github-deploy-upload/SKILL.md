---
name: github-deploy-upload
description: 安全地将本地部署目录通过定时 cron 推送到 GitHub 仓库。涵盖认证令牌安全存储（独立文件 600 权限）、git remote 内容自动清理、远程分支适配等实践。
version: 1.5.0
triggers:
- deploy upload
- deploy-upload
- 定时上传
- 自动推送
- github push token
- github deploy token
- 安全推送脚本
- deploy-upload.sh
author: 小喵 (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags:
    - GitHub
    - Deploy
    - Security
    - Git
    - Cron
    - Token
    related_skills:
    - github-repo-management
    - github-auth
    - hermes-ops-tips
---

# GitHub 安全部署上传 (Deploy Upload)

将本地 `~/.hermes` 配置和 `skills` 定时推送到 GitHub 仓库的安全实践。

## 认证令牌安全存储方案

### 推荐方案：独立安全文件 + 推送后清理

**创建认证令牌安全文件：**

```bash
# 写入令牌（仅此一次）
echo -n 'your_github_token_here' > ~/.hermes/.deploy_token

# 设置权限：仅 owner 可读写
chmod 600 ~/.hermes/.deploy_token

# 验证
ls -la ~/.hermes/.deploy_token
# 输出: -rw------- 1 user user ... /home/user/.hermes/.deploy_token
```

**脚本中安全使用：**

```bash
# 从安全文件读取
TOKEN_FILE="$HOME/.hermes/.deploy_token"
if [ -f "$TOKEN_FILE" ]; then
    GITHUB_TOKEN=$(cat "$TOKEN_FILE" | tr -d ' \n\r')
fi

# 获取当前 remote URL，清除可能残留的认证信息
REMOTE_BASE=$(git remote get-url origin 2>/dev/null || echo "")
if echo "$REMOTE_BASE" | grep -q '@'; then
    CLEAN_URL=$(echo "$REMOTE_BASE" | sed -E 's|https?://[^@]*@|https://|')
    git remote set-url origin "$CLEAN_URL"
    REMOTE_BASE="$CLEAN_URL"
fi

# 构建临时认证 URL（仅内存中，不持久化到磁盘）
USER_REPO=$(echo "$REMOTE_BASE" | sed -E 's|https?://[^/]*/||' | sed -E 's|\.git$||' | sed -E 's|.*@github\.com/||')
AUTH_URL="https://username:${GITHUB_TOKEN}@github.com/${USER_REPO}.git"
git remote set-url origin "$AUTH_URL"

# ... push 操作 ...

# ★★★ 安全关键：推送后立即恢复纯 URL ★★★
git remote set-url origin "$REMOTE_BASE"
```

## 完整脚本模板

参考 `~/.hermes/scripts/deploy-upload.sh` 和 `/tmp/hermes-catgirl-deploy/scripts/deploy-upload.sh`。

### 脚本核心逻辑流程

```
1. 读取 ~/.hermes/.deploy_token (权限600)
2. 获取 git remote, 清除可能残留的认证信息
3. 用认证令牌构建临时 URL -> 设置 remote
4. rsync 同步 ~/.hermes 到部署目录
5. ⭐ 清理内嵌 .git 目录（post-rsync 步骤）

   bash scripts/cleanup-embedded-git.sh "$DEPLOY_DIR"

   作用：移除 rsync 从 skill 目录带入的 .git/（如 web-access/.git/），
        防止 git 检测为子模块变更（"modified content, untracked content"）
6. git add + commit
7. git push (通过代理)
8. 立即恢复 remote URL 为纯 URL
```

### 关键注意事项

| 注意点 | 说明 | 应对方案 |
|--------|------|----------|
| **Git 配置短暂残留** | push 过程中 `.git/config` 会短暂保存带认证信息的 URL | 推送后立即恢复纯 URL |
| **分支名不一致** | 本地可能用 `master`，远程是 `main` | 脚本自动检测当前分支 |
| **Cron 环境隔离** | cron 任务无交互式 shell 的环境变量 | 用独立文件而非环境变量 |
| **代理环境** | 某些网络环境需代理才能访问 GitHub | `git -c http.proxy="http://127.0.0.1:7890" push` |
| **SCM 工具脱敏** | Hermes 的 `patch` 工具在写入含认证相关字符串时会自动处理，可能影响内容完整性 | 用 `write_file` 完整重写 |
| **运行时状态文件混入** | rsync 从 `~/.hermes/skills/` 同步时，会将 `.curator_state`、`.usage.json`、`.hub/` 等本地缓存/状态文件也复制进来，污染 git 仓库 | 在部署目录 `.gitignore` 中添加排除规则 |
| **技能目录内嵌 .git 仓库** | 某些 skill 目录（如 `web-access`）本身包含 `.git/` 目录，rsync 复制后部署目录 git 会将其检测为子模块（"modified content, untracked content"），导致 `git status` 异常 | 在 `.gitignore` 中添加 `skills/**/.git/` 排除所有内嵌 git 仓库；同步后清理已复制的 `.git/` 目录 |
| **HERMES_REPO_URL 环境变量** | cron 任务指令中引用此变量控制是否推送：未设置时只同步+commit，设置后才 push | 由 cron job 指令逻辑判断，非脚本内部逻辑；用于区分纯本地备份与远程同步 |
| **deploy-upload.sh 忽略 HERMES_REPO_URL** | `~/.hermes/scripts/deploy-upload.sh` 的判断逻辑基于 git remote 配置 + token 文件是否存在，而非 `$HERMES_REPO_URL` 环境变量。即使 HERMES_REPO_URL 未设置，只要有 git remote 和 `.deploy_token`，脚本仍然会推送 | 如需严格遵从 HERMES_REPO_URL，有两种方案：(A) 在脚本开头添加 `[[ -z "$HERMES_REPO_URL" ]] && PUSH_ENABLED=false` 的显式判断；(B) 在 cron job 指令中判断该变量，仅当设置时才调用带 push 的脚本变体 |
| **子模块条目已在 index 中 (mode 160000)** | 当某个 skill 目录（如 `skills/web-access`）**此前已被意外提交为 gitlink 子模块**（`git ls-files --stage` 显示 mode 160000），单纯清理磁盘上的 `.git/` 目录和 `.gitignore` 规则都无法修复。git status 会持续显示 `M skills/<name>`（modified content） | 需要执行三步手术：(1) `git rm --cached skills/<name>` 移除 index 中的子模块条目；(2) `rm -rf skills/<name>/.git` 清理磁盘上的内嵌仓库；(3) `git add skills/<name>/` 作为普通文件重新跟踪。此问题可能源自早期 rsync 同步时误提交了内嵌 `.git/` 目录，导致 git 自动将其注册为子模块 |
| **`***` 脱敏陷阱** | `git remote get-url origin` 输出的 URL 中，token 部分会被 git 自动替换为 `***`。直接捕获此输出用于恢复 remote URL 会导致 literal `***` 写入 git config，认证失效 | 恢复 URL 时必须从 `~/.hermes/.deploy_token` 读取真实 token 重建 URL，而非依赖 captured output |

## 定时任务配置

使用 Hermes cron job 创建定时推送：

```
# Cron prompt 示例:
# 执行部署上传脚本：运行 `bash ~/.hermes/scripts/deploy-upload.sh`
# 注意：如果 ~/.hermes/.deploy_token 不存在，仅同步文件但跳过推送
```

常用调度：
- 中午12点: `0 12 * * *`
- 午夜0点: `0 0 * * *`

## 安全验证清单

推送后验证：

```bash
# 1. 检查 git 配置文件干净
grep -c '@' /tmp/hermes-catgirl-deploy/.git/config | grep -q '0' && echo "安全通过"

# 2. 检查 remote URL 是否含有 literal '***' 污染
#    ⚠️ 注意：不要用 git remote get-url origin 来检查！
#       git 的输出会自动脱敏显示为 ***（即使 .git/config 里是干净的 URL），
#       会导致假阳性。必须直接检查配置文件。
if grep -q '\*\*\*' /tmp/hermes-catgirl-deploy/.git/config 2>/dev/null; then
    echo "⚠️ WARNING: .git/config 含有 literal '***'，认证凭证已损坏！需从 .deploy_token 重新构造 URL"
else
    echo "✅ remote URL 无 '***' 污染（确认方式：直接检查 .git/config）"
fi

# 3. 检查令牌文件权限
ls -la ~/.hermes/.deploy_token

# 4. 验证远程仓库更新
git -C /tmp/hermes-catgirl-deploy log --oneline -1
```

**验证 remote URL 最佳实践：**

| 你想要做什么 | 正确的命令 | 不要用的方式 |
|:---|:---|:---:|
| 查看实际存储的 URL | `grep url /tmp/hermes-catgirl-deploy/.git/config` | ❌ `git remote -v`（脱敏显示 `***`） |
| 检查有无 token 泄露 | `grep '@github' .git/config` | ❌ `git remote get-url`（脱敏显示 `***`） |
| 确认推送目标 | 读 `.git/config` 中的 remote 段 | ❌ 依赖 git 命令输出 |

## 部署目录 .gitignore 维护

skills 目录同步时会带入运行时状态文件，以及某些技能目录自身包含的 `.git/` 仓库，需在部署目录 `.gitignore` 中排除：

```gitignore
# ── 运行时状态（curator 缓存／使用统计）──
skills/.curator_state
skills/.usage.json
skills/.hub/

# ── 内嵌 git 仓库（子模块检测问题）──
# rsync 会将 skill 目录中的 .git/ 也复制过来，
# 导致部署目录 git 将其检测为子模块
skills/web-access/.git/
skills/**/.git/
```

**验证排除生效：**
```bash
cd /tmp/hermes-catgirl-deploy
# 确认这些文件不在 git tracked 中
git ls-files skills/.curator_state skills/.usage.json | wc -l
# 应输出: 0

# 确认没有内嵌 .git 被跟踪（子模块检测问题）
git status skills/ | grep -c 'modified content' || echo "无子模块检测问题"

# ★ 额外检查：检测子模块条目（mode 160000 gitlink）是否存在于 index 中
#    这是比磁盘 .git/ 更严重的问题——子模块条目一旦提交，光靠 .gitignore
#    和磁盘清理无法修复，必须 git rm --cached 移除
SUBMODULE_COUNT=$(git ls-files --stage skills/ 2>/dev/null | grep -c '^160000' || true)
if [ "$SUBMODULE_COUNT" -gt 0 ]; then
    echo "⚠️  检测到 $SUBMODULE_COUNT 个子模块条目！需要 git rm --cached 修复"
    git ls-files --stage skills/ | grep '^160000'
else
    echo "✅ 无子模块条目残留"
fi
```

**修复已混入的内嵌 .git 与子模块条目：**

内嵌 `.git` 问题有两种严重程度，需要不同方案处理：

**程度 A — 仅磁盘上有 .git 目录（尚未被提交为子模块）**

推荐使用专用脚本（skill 已内置）进行清理：

```bash
# 方式一：使用内置清理脚本（推荐）
bash scripts/cleanup-embedded-git.sh /tmp/hermes-catgirl-deploy

# 方式二：手动清理
cd /tmp/hermes-catgirl-deploy
find skills/ -maxdepth 2 -name '.git' -type d -exec rm -rf {} + 2>/dev/null || true
```

**程度 B — .git 已被提交为子模块（index 中存在 mode 160000 gitlink）**

当 `git ls-files --stage skills/web-access` 显示 `160000 ...` 时，说明该目录已被 git 注册为子模块（gitlink）。单纯删除磁盘上的 `.git/` 无效，需要从 index 中移除子模块条目：

```bash
cd /tmp/hermes-catgirl-deploy

# 1. 检查哪些 skill 被错误地作为子模块跟踪
git ls-files --stage skills/ | grep '^160000'

# 2. 移除子模块条目（不会删除实际文件）
git rm --cached skills/web-access

# 3. 清理磁盘上的内嵌 .git 仓库
rm -rf skills/web-access/.git

# 4. 重新将目录作为普通文件跟踪
git add skills/web-access/
```

**验证两种修复效果：**
```bash
cd /tmp/hermes-catgirl-deploy
# 检查 git 状态是否干净（无 submodule modified content）
git status --short
# 输出应为空

# 确认无残留子模块条目
git ls-files --stage skills/ | grep '^160000' || echo "✅ 无子模块条目残留"
```

⚠️ **注意**：此问题是**每次 rsync 同步后都会出现**的 recurring issue，因为 `web-access` 等 skill 目录自身包含 `.git/` 仓库。建议在 `deploy-upload.sh` 的 rsync 步骤后自动调用 `scripts/cleanup-embedded-git.sh` 脚本。

**验证清理效果：**
```bash
cd /tmp/hermes-catgirl-deploy
git status --short
# 应输出为空（无子模块检测问题）

当有新的运行时文件被带入时，先 `git reset HEAD <file>` 取消暂存，再更新 `.gitignore`。

## 更新认证令牌

当 PAT 过期时，直接覆盖文件即可，无需修改脚本或 cron 任务：

```bash
echo -n 'new_token_here' > ~/.hermes/.deploy_token
chmod 600 ~/.hermes/.deploy_token
```
