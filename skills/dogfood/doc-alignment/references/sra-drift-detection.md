# SRA 项目文档漂移检测实战

> 来自 Sprint 2 + Sprint 3 文档对齐的实操经验
> 日期: 2026-05-11

## 检测到的漂移（Sprint 2）

Sprint 2 完成后，API-REFERENCE.md 缺失以下内容：

| 缺失项 | 类型 | 严重度 |
|:-------|:-----|:------:|
| `GET /stats/compliance` | HTTP 端点 | 🔴 |
| `POST /validate` | HTTP 端点 | 🔴 |
| `POST /recheck` | HTTP 端点 | 🔴 |
| `sra compliance` | CLI 命令 | 🔴 |
| `action: viewed\|used\|skipped` | `/record` 参数扩展 | 🔴 |
| `compliance` | Socket action | 🔴 |
| `recheck` | Socket action | 🔴 |
| `validate` | Socket action | 🔴 |

## 根因分析

```
直接原因：Sprint 2 开发时专注于代码实现，未同步更新文档
  ↓
深层原因：工作流中缺少"提交前的文档对齐"强制步骤
  ↓
根本原因：AGENTS.md 没有 post-task 文档对齐要求
```

## 漂移检测命令

```bash
# 检测 API-REFERENCE 是否缺少端点
for endpoint in "/recheck" "/stats/compliance" "/validate"; do
  if ! grep -q "$endpoint" docs/API-REFERENCE.md; then
    echo "❌ 缺失: $endpoint"
  fi
done

# 检测 CLI 命令
for cmd in "compliance" "validate" "recheck"; do
  if ! grep -q "$cmd" docs/API-REFERENCE.md; then
    echo "❌ 缺失 CLI: $cmd"
  fi
done

# 检测 ROADMAP Story 状态
grep "pending" ROADMAP.md

# 跨文档一致性：对比 pytest 计数
pytest tests/ --collect-only -q 2>&1 | tail -1
grep -c "passed" PROJECT-PANORAMA.html
```

## 修复流程

```
Step 1: 识别所有受影响文档
  → docs/API-REFERENCE.md, PROJECT-PANORAMA.html, ROADMAP.md

Step 2: 确定漂移位置
  → API-REFERENCE.md §1 缺少 3 个端点
  → API-REFERENCE.md §2 缺少 3 个 socket actions
  → API-REFERENCE.md §3 缺少 1 个 CLI 命令
  → API-REFERENCE.md §4 缺少 3 个 Python 方法

Step 3: 逐文档修复
  → 在对应位置插入新内容

Step 4: 跨文档验证
  → 对比 PROJECT-PANORAMA.html 和 API-REFERENCE.md 的端点列表

Step 5: 单次提交
  → git add docs/ PROJECT-PANORAMA.html && git commit
```

---

## 检测到的漂移（Sprint 3 — 2026-05-11）

### 模式 1：CLI 命令名漂移

**现象**：文档中写 `sra list-adapters`，实际代码中命令名是 `sra adapters`（`cli.py` 的 COMMANDS dict 中注册的是 `"adapters": cmd_adapters`）。

**根因**：早期设计命名 `list-adapters`，重构为 `adapters` 后 API-REFERENCE.md 未同步。

**漂移检测命令**：
```bash
# 对比 API-REFERENCE.md 中的 CLI 命令与 cli.py 的 COMMANDS dict
echo "=== CLI 实际命令 ==="
grep '"' skill_advisor/cli.py | grep -E '": (cmd_|lambda)' | sed 's/"//g' | awk '{print $1}'
echo "=== CLI 文档命令 ==="
grep -oE '`sra [a-z-]+`' docs/API-REFERENCE.md | sed 's/`//g' | sed 's/sra //'
```

### 模式 2：raw.githubusercontent.com URL 分支漂移

**现象**：README 中写 `raw.githubusercontent.com/.../main/...`，但仓库默认分支是 `master`（非 `main`），URL 返回 404。

**检测命令**：
```bash
# 检测仓库默认分支
git symbolic-ref refs/remotes/origin/HEAD | sed 's@.*/@@'
# 检测所有 raw URL 是否使用正确的分支名
grep -rn "raw.githubusercontent.com" . --include="*.md" | grep -v ".git/"
```

### 模式 3：README 安装步骤与实际情况漂移

**现象**：`pip install sra-agent` 不提 venv → 用户找不到 `sra` 命令。`curl .../main/install.sh` → 404。不提 GFW → 中国用户超时。

**检测方法**：在全新环境中按 README 逐步骤执行安装说明。grep 只能发现表面问题，唯一可靠的是实际执行测试。

## 预防清单

| 检查项 | 执行频率 | 命令 |
|:-------|:--------|:-----|
| CLI 命令名一致性 | 每次新增/重命名命令 | 对比 `COMMANDS dict` vs `API-REFERENCE.md §3` |
| raw URL 分支正确性 | 仓库默认分支变更时 | `grep 'raw.*main/'` vs `git branch -r \| grep origin/HEAD` |
| README 安装步骤可执行 | 每次发布前 | 在全新环境中逐步骤执行安装说明 |
| HTTP 端点完整性 | 每次新增端点 | `grep -c 新端点 docs/API-REFERENCE.md` |
