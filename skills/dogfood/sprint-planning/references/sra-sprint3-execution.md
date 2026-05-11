# SRA Sprint 3 执行实录 — 实战参考

> **日期:** 2026-05-11
> **分支:** feat/v2.0-enforcement-layer → master
> **Sprint 目标:** 质量巩固 & 分支清理 🧹

## Sprint 使命

| Story | 类型 | 状态 |
|:------|:----:|:----:|
| SRA-003-21: 分支同步 & v1.3.0 发布 | 🏗️ | ✅ |
| SRA-003-22: os.fork() → subprocess.Popen (A-8) | 🔴 P0 | ✅ |
| README 命令补全 (D-2) + CHANGELOG 同步 (D-3) | 🟡 | ✅ |
| doc-alignment 协议执行 | 📐 | ✅ |

## Git 分支对齐实录

### 问题
`master` 本地落后 `feat/v2.0-enforcement-layer` 33 commits，但远程 `origin/master` 有 GitHub 自动 PR merge commits (#10, #11)，形成分歧历史：

```
本地 master:   A → B → C → D ... (33 个线性 commit)
origin/master: A → B' → C'      (2 个 merge commit)
```

### 解决步骤

```bash
# 1. 尝试 fast-forward 失败
git push origin master
# → rejected (non-fast-forward)

# 2. 检查远程差异
git log --oneline origin/master --not master
# → 发现 1 个 merge commit: "Feat/v2.0 enforcement layer (#11)"

# 3. 尝试 rebase 但产生冲突 (历史重写太复杂)
git pull origin master --rebase
# → 3 个文件冲突 (CHANGELOG, ROADMAP, plan file)

# 4. 改用 merge 保留双方历史
git merge origin/master --no-edit
# → 3 个文件冲突 (ROADMAP, EPIC doc, cli.py)
# 解决: git checkout --ours <file> + git add
# 继续: GIT_EDITOR=true git merge --continue

# 5. 推送成功
git push origin master
git push origin v1.3.0
```

### 经验
- **先 `merge-base` 再操作**: 确认 master 是分支的祖先 (33 ahead ≠ 33 diverged)
- **rebase vs merge 选择**: 分歧小(≤3 commits) + 仅 plan 文件冲突 → rebase 可接受；分歧含 source code → merge 更安全
- **--ours 策略**: 确认本地文件是最新版时用 `git checkout --ours` 快速解决
- **force push 规避**: 环境封锁 force push 时通过 merge 创建合并提交

## 关键技巧

### daemon fork 替换模式

**旧:** `os.fork()` → 子进程继承文件锁 → `os.setsid()` → I/O 重定向
**新:** `subprocess.Popen([sys.executable, "-c", code], start_new_session=True, …)`

```python
proc = subprocess.Popen(
    [sys.executable, "-c", subprocess_code],
    stdin=subprocess.DEVNULL,
    stdout=open(LOG_FILE, 'a'),
    stderr=open(LOG_FILE, 'a'),
    start_new_session=True,  # 等效 os.setsid()
)
pid = proc.pid
lock.release()  # 子进程独立运行后释放父进程的锁
```

### 版本发布流程

```
1. sync pyproject.toml version ← 修复遗漏
2. merge branch → master (ff/merge)
3. tag v1.3.0 + push
4. bump dev branch → v1.4.0-dev
```

## 验证清单

- [x] `pytest tests/ -q` → 290/290 passed
- [x] `git status` → clean
- [x] `PROJECT-PANORAMA.html --verify` → 无漂移
- [x] 远程推送成功 (branch + master + tag)
