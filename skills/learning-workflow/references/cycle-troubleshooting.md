# Cycle Troubleshooting — 学习循环故障诊断指南

> 当学习流程的 R1/R2/R3/QG 门禁没有按预期触发循环回退时，使用本指南进行深度诊断。

## 五层诊断框架（来自实战经验）

当循环"没跑起来"时，从表层到底层逐一排查：

### 第5层（最表层）：状态机没有循环入口
**症状**：`complete` 后永远前进，没有回退
**检查**：`learning-state.py` 是否有 `regress` 命令
**修复**：需要调用 `learning-state.py regress <target_step>` 手动触发回退
**自动拦截**：`learning-state.py reject` 标记需重做 + `regress` 回退

### 第4层：R1/R2/R3 是"纸面检查"没有拦截
**症状**：reflection-gate.py 输出 score < 60 但流程仍在前进
**检查**：`reflection-gate.py` CLI exit code 是否为 1
**修复**：在 SKILL.md 中 boku 必须检查 exit code，对 exit=1 自动执行 regress

### 第3层：无 regress 函数入口
**症状**：想回退但发现没有命令可用
**检查**：`python3 learning-state.py regress` 是否存在
**修复**：需要添加 regress_step() 函数 + CLI 注册

### 第2层：质量评分公式未落地
**症状**：STEP 5.5 质量门禁只在 SKILL.md 里，没有代码实现
**检查**：`reflection-gate.py quality` 是否存在且能运行
**修复**：需要实现 check_quality() 函数，调用 4 维度评分公式

### 第1层（最根本）：自评自判的"完成主义"惯性
**症状**：boku 自己检查自己的输出，永远给 "通过"
**检查**：是否使用了子代理作为第三方裁判
**修复**：在 score 40-70 的边界区间，启动 delegate_task 让子代理作为独立裁判

## 快速诊断命令

```bash
# 1. 检查状态机版本
python3 learning-state.py --help | grep regress
# → 如果有 regress 说明 P0 已修复

# 2. 检查反射门禁
python3 reflection-gate.py r1 <task_id>
# → 查看 score 和 exit code

# 3. 查看循环状态
python3 learning-state.py loop-status <task_id>
# → 查看 R1/R2/R3/QG 各自的循环次数

# 4. 手动触发循环（如果门禁没自动拦截）
python3 learning-state.py reject step1_search "原因"
python3 learning-state.py regress step0_map <task_id>
python3 learning-state.py loop-status <task_id>
```

## 循环不触发排查清单

- [ ] `learning-state.py` 是否有 `regress` 命令？
- [ ] `reflection-gate.py` exit code 是否被检查？
- [ ] 是否在 score < 60 时自动执行了 regress？
- [ ] `loop_count` 是否在每次门禁检查后递增？
- [ ] QG 评分公式是否从 artifact 文件读取了数据？
- [ ] 子代理裁判是否在 score 40-70 区间被触发？
