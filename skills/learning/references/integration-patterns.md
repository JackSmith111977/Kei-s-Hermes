# 知识整合模式

> 本文件记录 learning skill 积累的知识整合经验和 skill 更新策略，每次学习后更新。

## 整合决策树

```
精炼后的知识 → 决策：
├─ 该领域是否有已有 skill？
│   ├─ 是 → 通过 skill-creator M1-M4 流程更新
│   │   ├─ M1: 读取当前 skill
│   │   ├─ M2: 确认更新内容
│   │   ├─ M3: 生成预览（Diff）
│   │   └─ M4: 写入更新
│   └─ 否 → 继续
├─ 该领域是否需要独立 skill？
│   ├─ 是 → 通过 skill-creator 创建新 skill
│   │   ├─ Stage 1: 需求澄清
│   │   ├─ Stage 2: 用例定义
│   │   ├─ Stage 3: 选择类型 + 设计模式
│   │   ├─ Stage 4: 生成草稿
│   │   ├─ Stage 5: 用户确认
│   │   ├─ Stage 6: 写入文件
│   │   ├─ Stage 7: Review 检查
│   │   ├─ Stage 8: 测试建议
│   │   └─ Stage 9: 评估迭代（可选）
│   └─ 否 → 继续
└─ 是否作为 references 存入现有 skill？
    └─ 是 → 写入目标 skill 的 references/ 目录
```

## Skill 类型匹配

| 知识类型 | 对应 Skill 类型 | 设计模式 |
|----------|----------------|----------|
| 库/API 使用指南 | 库和 API 参考 | Tool Wrapper |
| 工具测试/验证流程 | 产品验证 | Pipeline + Reviewer |
| 数据分析/报表 | 数据获取与分析 | Generator |
| 框架教程/示例 | 代码生成 | Generator + Pipeline |
| 概念解释/对比 | 调研整理 | Inversion + Generator |
| 代码规范/风格 | 团队规范 | Tool Wrapper |
| 部署/发布流程 | 部署流程 | Pipeline + Reviewer |

## 整合原则

1. **原子化**：一个 skill 专注一个领域，不造庞然大物
2. **一致性**：遵循 skill-creator 的目录结构（SKILL.md + references/ + checklists/）
3. **可追溯**：更新时记录版本变更和修改原因
4. **可评估**：为新 skill 创建 evals.json

## 整合经验积累

<!-- 每次学习后添加 -->

| 日期 | 主题 | 整合方式 | 经验总结 |
|------|------|----------|----------|
<!-- 示例 -->
<!-- | 2026-05-03 | FastAPI | 创建新 skill | 使用"库和 API 参考"类型，Tool Wrapper 模式 | -->
