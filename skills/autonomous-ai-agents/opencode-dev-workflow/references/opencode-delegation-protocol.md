# OpenCode 委托协议 — 详细参考

> 本文件是 opencode-dev-workflow skill 的配套参考。
> 包含五要素协议的完整格式、超时策略、验证协议和与工作流链的集成方式。

## 一、五要素协议速查

每次 OpenCode prompt 必须包含：

```
[任务] {id}: {标题}
[上下文] {dir}  |  文件: {ref_files}
[AC-1] {验收标准}
[AC-2] {验收标准}
[约束] 只改 {scope}
[产出] 创建: {new_files}  |  修改: {modified_files}
[验证] {verify_command}
```

## 二、超时策略

| 任务规模 | 推荐超时 | 模式 |
|:---------|:--------:|:-----|
| 单文件修复 | 60s | `opencode run` |
| 2-3 文件小功能 | 120s | `opencode run` |
| 4-8 文件多文件 | 300s | `terminal background` |
| 批量并行 | 600s | `git worktree` + 多个 background |
| 8+ 文件 | ❌ 拆 | 每个子任务 2-4 文件 |

经验公式: `timeout = 预估秒数 × 2 + 60`

## 三、验证协议

每次 OpenCode 完成后执行：

```bash
# 1. 文件存在性
for f in files; do test -f "$f" || echo "MISSING: $f"; done

# 2. 语法检查
python3 -c "import ast; ast.parse(open('$file').read())"

# 3. 测试
pytest tests/ -q
```

## 四、集成到 workflow-chain

```bash
# DEV 阶段 → 委托 OpenCode
python3 scripts/workflow-chain.py status EPIC-XXX
opencode run '[五要素协议]' --thinking --dir <dir>
# 验证 → 推进
python3 scripts/workflow-chain.py advance EPIC-XXX
```
