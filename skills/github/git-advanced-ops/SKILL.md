---
name: git-advanced-ops
description: Git 和 GitHub 高级操作指南，特别包含代理环境下的配置。涵盖 interactive rebase、stash、冲突解决、force pus...
version: 1.2.0
triggers:
- git
- rebase
- stash
- 冲突
- RPC failed
- GnuTLS
- 推送失败
- worktree
- 分支分歧
- duplicate repo
- 仓库重复
- 隔离开发
allowed-tools:
- terminal
- read_file
metadata:
  hermes:
    tags:
    - git
    - github
    - rebase
    - proxy
    - collaboration
    category: github
    skill_type: library-reference
    design_pattern: tool-wrapper
---
# Git 高级操作指南 🐙

## Hermes 特殊配置：代理环境

服务器在国内，GitHub 被墙，需要代理：

```bash
# 配置 HTTP 代理（mihomo 在 7890）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 一、Interactive Rebase（交互式变基）

### 基本操作
```bash
# 对最近 N 个 commit 进行变基
git rebase -i HEAD~5

# 对某个分支变基
git rebase -i main
```

打开编辑器后会看到：
```
pick abc1234 添加用户模型
pick def5678 修复类型错误
pick ghi9012 WIP: 更多功能
```

### 可用命令
| 命令 | 缩写 | 作用 |
|:---|:---:|:---|
| pick | p | 保留该 commit |
| reword | r | 保留 commit，修改提交信息 |
| edit | e | 保留 commit，但停下来修改 |
| squash | s | 合并到上一个 commit（两个信息都保留） |
| fixup | f | 合并到上一个 commit（丢弃本信息） |
| drop | d | 删除该 commit |
| exec | x | 运行 shell 命令 |

### 常见场景

**压缩多个 WIP commit：**
```bash
# 把最后 4 个合并成 1 个
git rebase -i HEAD~4
# 在编辑器中把后 3 个改为 squash 或 fixup
```

**重新排序：** 在编辑器中直接调整行顺序

**修改历史 commit 信息：**
```bash
git rebase -i HEAD~3
# 把对应的 pick 改为 reword
```

### 冲突处理
```bash
# 修复冲突后
git add <fixed-file>
git rebase --continue

# 放弃此次变基
git rebase --abort

# 跳过当前 commit
git rebase --skip
```

### --autosquash（自动排序）
```bash
# 先创建 fixup commit
git commit --fixup=abc1234

# 然后 rebase 时自动排序
git rebase -i --autosquash main

# 设为默认
git config --global rebase.autosquash true
```

## 二、Stash（暂存）

```bash
# 暂存当前修改
git stash

# 带信息暂存
git stash save "WIP: 正在开发功能 X"

# 查看暂存列表
git stash list

# 恢复最新暂存（不移除）
git stash apply

# 恢复并移除
git stash pop

# 恢复指定暂存
git stash apply stash@{1}

# 删除指定暂存
git stash drop stash@{0}
```

## 三、代理环境下的 Push 陷阱

### 陷阱：`RPC failed; GnuTLS recv error` — 推送未必真失败

**现象**：
```bash
$ git push origin feature
error: RPC failed; curl 56 GnuTLS recv error (-110): The TLS connection was non-properly terminated.
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
```

**关键洞察**：这个错误 **不代表推送一定失败**。HTTP 层面的 TLS 断开发生在响应回传阶段，但 Git 的推送数据可能已经到达服务器端并被处理。典型表现：
- 第一次尝试报错
- 第二次尝试显示 `Everything up-to-date` — 说明第一次实际上成功了

**建议的应对流程**：
```bash
# 第一步：不要立即惊慌重试
# 第二步：验证远端是否已接收提交
git ls-remote origin feature

# 第三步：确认远端 commit hash 是否匹配本地
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git ls-remote origin feature | cut -f1)
if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
  echo "✅ 推送已成功，无需重试"
else
  echo "❌ 推送未成功，需要重试"
  git push origin feature
fi
```

**根因**：通过 mihomo/Clash 代理推送时，代理偶尔会在响应传输中提前关闭 TLS 连接（非 Git 问题）。推送数据本身已在关闭前完成传输。

## 四、Force Push（强制推送）

```bash
# 安全强制推送（推荐）
git push --force-with-lease origin feature

# 强制推送（仅在确定没有别人在用该分支时）
git push --force origin feature
```

> `--force-with-lease` 比 `--force` 安全：如果有人先推送了，它会失败而不是覆盖

## 五、Reflog（后悔药）

```bash
# 查看所有操作历史
git reflog

# 恢复到某个历史状态
git reset --hard HEAD@{2}

# 找回丢失的 commit
git cherry-pick <lost-commit-hash>
```

所有操作（包括 rebase、reset）都可以通过 reflog 恢复。

## 六、冲突解决

```bash
# 查看冲突文件
git status

# 查看冲突详情
git diff

# 接受当前/传入的版本
git checkout --ours file.txt
git checkout --theirs file.txt

# 标记已解决
git add file.txt
```

## 七、Submodule（子模块）

```bash
# 添加子模块
git submodule add <url> <path>

# 克隆带子模块的仓库
git clone --recurse-submodules <url>

# 更新子模块
git submodule update --remote

# 初始化子模块（已克隆但没拉子模块）
git submodule update --init --recursive
```

## 八、Cherry-pick（精选提交）

```bash
# 从其他分支挑一个 commit
git cherry-pick abc1234

# 挑多个
git cherry-pick abc1234 def5678

# 只挑改动不提交
git cherry-pick -n abc1234
```

## 九、防止仓库重复（Preventing Divergent Repositories）

> **核心原则**：永远不要 `cp -r` 整个 Git 仓库来创建"副本"——使用 `git worktree` 或 `hermes -w`。

### 问题的根源

AI 代理在需要隔离工作空间时，最常见的错误是直接复制目录：

```bash
# ❌ 错误做法 —— 导致两个独立 Git 仓库
cp -r ~/projects/sra/ ~/projects/sra-new/
# 两个仓库有各自的 .git/，共享同一远程
# 但 commit 历史各自演进，最终需要手动合并
```

这会导致：
- **commit 历史分裂** —— 两个仓库各自提交，`git merge-base` 无法跨仓库工作
- **文档漂移** —— 同一份 EPIC 文档在两个仓库中内容不同
- **版本混乱** —— 一个 v2.0.3，另一个 v2.0.4，不知道哪个是"最新"
- **手动合并痛苦** —— 需要用 `diff -rq` 对比工作目录 + 手动 cherry-pick

### ✅ 解决方案：Git Worktree

`git worktree` 允许一个仓库拥有多个工作目录，**共享同一个 `.git` 对象库**：

```bash
# ✅ 正确做法 —— 创建链接工作树
cd ~/projects/sra
git worktree add -b feat/new-feature ../sra-feat-new-feature main
# 在 ~/projects/sra-feat-new-feature/ 目录下自动切换到 feat/new-feature 分支
# 共享 ~/projects/sra/.git/ 对象库 —— 永远不出现分裂
```

| 方式 | 创建时间 | 磁盘开销 | 历史共享 | 合并方式 |
|:-----|:--------:|:--------:|:--------:|:--------:|
| ❌ `cp -r` 复制目录 | 秒级 | 全量重复 | ❌ 分离 | 手动 diff |
| ❌ `git clone` | 30-120s | 完整仓库 | ❌ 需同步 remote | git merge |
| ✅ `git worktree` | **< 1s** | **仅工作文件** | ✅ **共享对象库** | **标准 merge** |

#### Worktree 常用命令

```bash
# 创建 worktree + 新分支
git worktree add -b <branch> <path> <base>

# 创建 worktree（检出已有分支）
git worktree add <path> <existing-branch>

# 查看所有 worktree
git worktree list

# 移除 worktree（完成后清理）
git worktree remove <path>

# 手动删除目录后清理残留引用
git worktree prune
```

#### Hermes 原生 Worktree 支持

Hermes 内置 `-w` 参数，一行命令自动创建隔离工作空间：

```bash
# 自动创建 .worktrees/hermes-<timestamp> + 隔离分支
cd ~/projects/sra
hermes -w

# 带查询的自动 worktree
hermes -w -q "修复 Issue #123"

# 并行代理 —— 每个终端都开一个 worktree
# 终端 1: hermes -w
# 终端 2: hermes -w
# 终端 3: hermes -w
# 每个代理有独立目录 + 独立分支，永不互相干扰
```

### 🔴 AI 代理铁律

```markdown
## 🔴 铁律：禁止复制仓库目录
- 需要独立工作空间 → 必须用 `git worktree` 或 `hermes -w`
- 禁止 `cp -r <repo> <repo>-new`
- 禁止 `git clone` 到 `~/projects/` 作为临时工作目录
- 工作完成后立即 `git worktree remove` 清理
```

### 检测脚本（定期扫描）

> 📎 速查参考: `references/git-worktrees-quickref.md` — Git worktree 命令速查表
> 📎 案例分析: `references/divergent-clones-case-study.md` — SRA 项目实际案例

```bash
#!/bin/bash
# detect-duplicate-repos.sh —— 扫描 ~/projects/ 下的重复仓库
# 用法: bash detect-duplicate-repos.sh

PROJECTS_DIR="$HOME/projects"

echo "=== 扫描重复 Git 仓库 ==="

# 收集所有仓库及其远程
declare -A remotes
for repo in "$PROJECTS_DIR"/*/; do
  if [ -d "$repo/.git" ]; then
    remote=$(cd "$repo" && git remote -v 2>/dev/null | head -1 | awk '{print $2}')
    name=$(basename "$repo")
    if [ -n "$remote" ]; then
      echo "  $name → $remote"
      key="$remote"
      if [ -n "${remotes[$key]}" ]; then
        echo "    ⚠️  远程重复！已有: ${remotes[$key]}"
      fi
      remotes[$key]="${remotes[$key]:+${remotes[$key]}, }$name"
    fi
  fi
done

echo ""
for key in "${!remotes[@]}"; do
  count=$(echo "${remotes[$key]}" | tr ',' '\n' | wc -l)
  if [ "$count" -gt 1 ]; then
    echo "🔴 发现重复仓库！远程: $key"
    echo "   目录: ${remotes[$key]}"
  fi
done
```

### 决策树：检测到重复后如何统一

```
发现两个仓库指向同一远程
    ↓
    ├─ commit 历史完全相同 → 直接删除冗余方
    │
    ├─ 一方领先（额外 commit）→ 以该方为准
    │   ├─ 验证领先方可正常 push → 删除冗余方
    │   └─ 无法 push → cherry-pick 到另一方再 push
    │
    ├─ 双方各有额外 commit → 需要合并
    │   ├─ 基相同 → rebase 统一
    │   └─ 基不同 → cherry-pick 逐个搬移
    │
    └─ 不确定时 → 先 push 双方到远程，再在 GitHub 上对比


## 十、检测分支工作副本（Divergent Working Copies）

### 场景：怀疑存在两个独立的 Git 仓库指向同一个远程

当 `~/projects/foo/` 和 `~/projects/foo-new/` 同时存在且都指向同一个远程时，需要判断哪个更"新"、它们是否独立：

```bash
# 1. 确认两个仓库指向同一个远程
cd ~/projects/foo && git remote -v
cd ~/projects/foo-new && git remote -v

# 2. 查看各自 HEAD
echo "foo HEAD: $(cd ~/projects/foo && git rev-parse HEAD)"
echo "foo-new HEAD: $(cd ~/projects/foo-new && git rev-parse HEAD)"

# 3. 比较工作目录差异（排除 .git）
diff -rq ~/projects/foo/ ~/projects/foo-new/ --exclude=.git

# 4. 查看各自独一无二的 commit
echo "--- foo 领先的 commits ---"
cd ~/projects/foo && git log --oneline --format="%h %s" \
  ~/projects/foo-new/HEAD..HEAD 2>/dev/null || \
  # 备选：直接比较 hash
  git log --oneline --format="%h %s" --not \
  $(cd ~/projects/foo-new && git rev-parse HEAD)

echo "--- foo-new 领先的 commits ---"
cd ~/projects/foo-new && git log --oneline --format="%h %s" \
  ~/projects/foo/HEAD..HEAD 2>/dev/null

# 5. 检查各仓库的工作目录是否干净
cd ~/projects/foo && git status --short
cd ~/projects/foo-new && git status --short
```

### 关键判断指标

| 指标 | 含义 | 代表 |
|:-----|:-----|:-----|
| 两者 HEAD 不同 | 两个副本的代码基线不同 | 需要合并 |
| 一方有额外 commit | 该方在本地做了未同步的工作 | 可以作为"事实来源" |
| 一方工作目录不干净 | 有未提交的修改 | 先 commit 再决策 |
| 工作目录 diff 大但 commit 历史一样 | 一方是拷贝而非 clone，修改了文件但没 commit | 需要 git add + commit |
| `.git/objects` 是否共享 | `readlink -f .git` 可检测是否为同一个 repo | 独立 vs 共享 |

### 决策树：如何统一

```
两个仓库指向同一远程
    ↓
    ├─ 一方领先（额外 commit）→ 以该方为准，删除另一方
    │   └─ 验证：git fetch origin && git merge-base --is-ancestor
    │       └─ 是：cherry-pick 额外 commit 到另一分支
    │
    ├─ 双方各有额外 commit → 需要合并
    │   ├─ 基相同 → rebase 统一
    │   └─ 基不同 → cherry-pick 命令比较
    │
    └─ 完全相同 → 删除冗余方，保留一个
```

### 常见陷阱

- **两个仓库的 commit hash 完全一致**不意味着它们等价——可能只是没 push/pull 统一后。一定要比较 HEAD hash。
- **`git merge-base` 在跨仓库时不可用**（exit code 128）——因为不同 `.git/objects` 不共享对象。用 `git log --not <hash>` 替代。
- **代理断开导致 `git fetch` 失败**时，无法对比远程状态。此时只能靠本地 commit 历史做判断。

## 十一、快速参考

```bash
# 日志美化
git log --oneline --graph --all

# 查看某文件的修改历史
git log -p -- filename

# 查看某行是谁改的
git blame filename

# 暂存部分改动
git add -p

# 修改最近 commit 信息
git commit --amend

# 放弃未暂存的修改
git checkout -- file.txt

# 删除远程分支
git push origin --delete feature

# 打标签
git tag v1.0 && git push origin v1.0
```
