# 经验积累系统格式指南

> 基于 Post-mortem 最佳实践 + PlugMem（微软研究院）+ MUSE 三层记忆 + Experience Compression Spectrum 设计。

## 目录结构

```
~/.hermes/experiences/
├── index.md         # 经验目录（自动维护）
├── active/          # 活跃经验（当前有效的经验）
├── skills/          # 已升级为 skill 的经验
└── archive/         # 归档经验（过期或已验证完成）
```

## 经验条目格式

每个经验文件必须包含 YAML frontmatter + 结构化 body：

```markdown
---
id: exp-YYYYMMDD-NNN
type: experience   # experience | skill | rule
status: active     # active | under_review | archived
source: 本次学习/任务名称
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
reusability: high  # high | medium | low
verified: true     # true | false
confidence: 3      # 1-5（验证次数越多越高）
---

## 经验：{一句话标题}

### 背景
{什么情境下发现了这个经验}

### 核心发现
{这个经验的关键内容是什么}

### 可操作建议
1. {具体怎么做}
2. {具体怎么做}

### 验证记录
- YYYY-MM-DD: 在 {场景} 中验证 ✅
```

## 经验三类型

| 类型 | 压缩率 | 说明 | 存储位置 |
|:----:|:------:|:----|:---------|
| **Experience** | 低 | 具体情境下的发现，含背景 | experiences/active/ |
| **Skill** | 中 | 可重复的流程/模式 | experiences/skills/ → 更新对应 skill |
| **Rule** | 高 | 抽象原则，无具体绑定 | experiences/archive/ |

## 提取判断标准

当满足以下任一条件时，应提取经验：
1. 发现了一个可复用的方法/模式/原则
2. 解决了以前卡住的问题，找到了可靠方案
3. 验证了一个假设，推翻了错误认知
4. 找到了一个值得记录的坑/陷阱/反模式

## 评分体系

| 维度 | 值 | 含义 |
|:----:|:----:|:----:|
| reusability | high | 跨任务/跨领域可复用 → 升级为 skill |
| reusability | medium | 同类型任务可复用 → 保持为 experience |
| reusability | low | 单次有效 → 归档 |
| confidence | 1-5 | 被成功验证的次数 |
