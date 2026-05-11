---
name: git-advanced-ops
description: Git 和 GitHub 高级操作指南，特别包含代理环境下的配置。涵盖 interactive rebase、stash、冲突解决、force pus...
version: 1.0.0
triggers:
- git
- rebase
- stash
- 冲突
- RPC failed
- GnuTLS
- 推送失败
- proxy push
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

## 九、快速参考

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
