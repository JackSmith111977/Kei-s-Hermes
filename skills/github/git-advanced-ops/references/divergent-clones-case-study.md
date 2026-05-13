# 🔍 案例分析：SRA 项目的分歧工作副本

> 源自 2026-05-13 的 Hermes 项目审计 —— `~/projects/sra/` vs `~/projects/sra-new/`

## 背景

Hermes 的 SRA 项目中存在两个文件夹：

| 仓库 | 路径 | HEAD | 版本 |
|:-----|:-----|:-----|:----:|
| `sra` | `~/projects/sra/` | `cbdd122` | v2.0.3 |
| `sra-new` | `~/projects/sra-new/` | `d3f002a` | v2.0.4 |

## 发现问题

在日常 QA 中注意到 `~/projects/` 下存在两个 SRA 目录。通过系统化调查确认：

### 症状
1. 两个仓库指向**同一个 GitHub 远程** (`JackSmith111977/Hermes-Skill-View.git`)
2. 两者 HEAD **不同**（差 3 个 commit）
3. 工作目录有实际差异（`sra-new` 有 `scripts/ac-audit.py`，`sra` 没有）

### 诊断命令

```bash
# Step 1: 确认远程相同
cd ~/projects/sra && git remote -v
# → origin https://github.com/JackSmith111977/Hermes-Skill-View.git
cd ~/projects/sra-new && git remote -v
# → origin https://github.com/JackSmith111977/Hermes-Skill-View.git

# Step 2: 比较 HEAD
cd ~/projects/sra && git rev-parse HEAD        # cbdd122
cd ~/projects/sra-new && git rev-parse HEAD    # d3f002a

# Step 3: 查看差异 commit
cd ~/projects/sra-new && git log --oneline \
  $(cd ~/projects/sra && git rev-parse HEAD)..HEAD
# → d3f002a docs: 文档对齐 v2.0.4
# → ae63e97 feat: 三重加固 — AC 审计脚本 + 工作流门禁
# → 6d10588 feat: AC 审计脚本 ac-audit.py — check/sync/dashboard 三模式

# Step 4: 工作目录对比
diff -rq ~/projects/sra/ ~/projects/sra-new/ --exclude=.git
# → scripts/ac-audit.py 只在 sra-new 存在
# → CHANGELOG.md / EPIC-003 内容不同
# → build/ dist/ 只在 sra 存在（构建产物）
```

### 根因

`sra-new` 是由某次 AI 会话**直接拷贝** `sra/` 目录后在其内部开发新功能（AC 审计脚本）创建的。这**不是** `git branch` 或 `git clone` 的结果，而是手动的 `cp -r`。

Git 层面没有任何合并关系——两个仓库是完全独立的 `.git/`。

## 重建的统一路径

```bash
# 方案：以 sra-new 为准（它更新）
# 1. 备份 sra 的独有内容（build/dist 重建即可，无需保留）
# 2. 删除 sra
# 3. 重命名 sra-new → sra
# 4. 验证 sra push 是否成功

# 或方案 B：cherry-pick 到 sra
cd ~/projects/sra
git remote add sra-new ~/projects/sra-new/.git
git fetch sra-new
git cherry-pick 6d10588..d3f002a
```

## 经验教训

1. **永远不要 `cp -r` 整个 Git 仓库来"复制"项目**——使用 `git clone` 或 `git worktree` 来确保共享对象存储
2. **定期检查 `~/projects/` 下的目录是否有非预期重复**
3. **为每个项目建立唯一的 Git 仓库路径**——项目初始化时就确定好路径，不要临时决定
4. **AI 生成的"新副本"要立即 merge 回主分支**，不应长期独立存在

## 扩展：`git worktree` 替代方案

如果确实需要同时打开多个工作目录：

```bash
# 在主仓库中创建额外工作树（共享同一 .git）
cd ~/projects/sra
git worktree add ~/projects/sra-feat-work feat/v2.0-enforcement-layer

# 完成后移除
git worktree remove ~/projects/sra-feat-work

# 列出所有工作树
git worktree list
```

`git worktree` 保证所有工作目录共享同一对象存储，永不出现"副本分歧"。
