# Git Worktrees 速查表

> 适用于：需要隔离工作空间的 AI 代理任务 / 并行开发 / 实验性变更

## 创建 Worktree

```bash
# 新建分支 + worktree（最常见）
git worktree add -b feat/my-feature ../repo-my-feature main

# 检出已有分支到 worktree
git worktree add ../repo-bugfix bugfix-123

# 从当前 HEAD 创建
git worktree add ../repo-experiment

# 分离 HEAD（不创建分支名）
git worktree add -d ../repo-throwaway
```

## 管理 Worktree

```bash
# 列出所有 worktree
git worktree list

# 移除 worktree（完成后）
git worktree remove ../repo-my-feature

# 强制移除（有未提交变更时）
git worktree remove --force ../repo-my-feature

# 手工删目录后清理残留
git worktree prune
```

## Hermes 集成

```bash
# 自动创建 worktree + 隔离分支
hermes -w

# 带查询
hermes -w -q "实现用户注册功能"

# 多代理并行
# 终端 1: hermes -w
# 终端 2: hermes -w
```

## 注意事项

| 陷阱 | 说明 |
|:-----|:------|
| **同一分支不能出现在两个 worktree** | Git 阻止此操作 —— 每个 worktree 必须用唯一分支 |
| **Worktree 不含 node_modules / .venv** | 创建后需重新安装依赖 |
| **手工 `rm -rf` 后要 `git worktree prune`** | 否则 Git 残留引用 |
| **Worktree 不会自动删除分支** | 分支需单独 `git branch -d <branch>` |
| **长时间不合并 → 冲突变大** | 尽量避免 worktree 存活超过一天 |

## 与 `git clone` 的对比

| | `git worktree` | `git clone` |
|:--|:---------------|:------------|
| 对象存储 | 共享同一 `.git/objects` | 复制完整 `.git/` |
| 创建速度 | < 1 秒 | 30-120 秒（网络） |
| 远程跟踪 | 继承父仓库 | 需单独配置 |
| 看到其他分支的提交 | 立即可见 | 需 fetch |
| 适用场景 | 短生命周期、多分支并行 | 长期 fork / 完全分离的环境 |
