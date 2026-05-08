# Karpathy Bounded Autonomy — 学习流程中的约束理论应用

> 基于 Andrej Karpathy 的 AutoResearch 项目 (2026) 提炼的约束自主性工程实践。

## 核心命题

> **给 Agent 最大自由度，但用紧密定义的结构性约束来框定其行为边界。约束不是限制，而是使自主成为可能。**

## 七层约束 → learning-workflow 映射

| Karpathy 约束 | learning-workflow 实现 | 说明 |
|:---:|:---|:---|
| ⏱️ **时间盒** | 每步权重 + 预计剩余时间 | STEP 权重决定进度估算，辅助调用 timeout=60s |
| 📄 **作用域** | 步骤依赖强制 + artifact 检查 | 前置步骤未完成禁止进入下一步 |
| 📊 **单一指标** | R1/R2/R3/QG 评分公式 | 每个门禁有明确的量化评分标准 |
| 🔄 **安全回滚** | `regress` 命令 + `reject` 命令 | 失败自动回退到指定步骤，保留拒绝记录 |
| 🚫 **NEVER STOP** | 循环控制 + 自动回退 | 门禁失败不停止流程，自动进入下一轮循环 |
| 📋 **结构化循环** | LOOP FOREVER + 编号步骤 | STEP 0→1→R1→2→R2→3→R3→4→5→QG→6 |
| 🔌 **无外部依赖** | 所有产出物本地文件 | knowledge_map.md / raw_search_results.md 等 |

## v5.1 新增：最小循环 + 递进等级

### 为什么需要最小循环次数？

Karpathy 的 AutoResearch 中，Agent **永远不会在第一次尝试就停止**。即使第一次实验就找到改进，也会继续尝试更多方案。同样，学习流程中：

- **第 1 轮（广度扫描）**：覆盖面广但深度不够。即使分数 ≥ 60，也强制进入第 2 轮
- **第 2 轮（深度挖掘）**：深入验证关键发现。评分标准自动提升 10 分
- **第 3 轮（精炼优化）**：打磨细节。评分标准自动提升 20 分

### 递进惩罚的数学原理

```
effective_score = raw_score + level_penalty

level_penalty:
  第 1 轮: 0    (合格线 60)
  第 2 轮: -10  (合格线 70)
  第 3 轮: -20  (合格线 80)
```

这意味着：
- 第 1 轮搜索（广度扫描）拿到 80 分 → 显示为 80，但 **passed=false**（未达 MIN_LOOPS）
- 第 2 轮搜索（深度挖掘）拿到 80 分 → 显示为 70（-10 惩罚），passed=true
- 第 3 轮搜索（精炼优化）拿到 85 分 → 显示为 65（-20 惩罚），passed=warning

### 与 Karpathy's AutoResearch 的对比

| 特性 | AutoResearch | learning-workflow |
|:---|:---|:---|
| 单次迭代时间 | 5 分钟固定 | 步骤权重 + timeout |
| 迭代次数 | 直到停止（NEVER STOP） | 最小 1 次，最大 2/3 次 |
| 通过标准 | val_bpb 改进 | effective_score ≥ 60 |
| 回滚机制 | git reset | regress 到前置步骤 |
| 人类接口 | program.md | knowledge_map.md |
| 递进性 | 隐含（仅持续改进） | **显式定义**（广度→深度→精炼） |

## References

- Karpathy, A. (2026). *AutoResearch*. https://github.com/karpathy/autoresearch
- marc0.dev. (2026). *Karpathy's autoresearch: Why Constraints Enable Autonomy*
- The New Stack. (2026). *Andrej Karpathy's 630-line Python script ran 50 experiments overnight*
