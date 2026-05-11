# SRA 项目文档漂移检测实战

> 来自 Sprint 2 完成后文档对齐的实操经验
> 日期: 2026-05-10

## 检测到的漂移

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
