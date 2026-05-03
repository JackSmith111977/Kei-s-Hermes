---
name: learning
description: Meta-skill：持续进化的学习方法论。负责信息收集、过滤、清洗、精炼， 以及将知识整合到对应的领域 skill 中。它本身成长的是学习技巧、 整...
version: 2.0.0
triggers:
- 学习
- 研究
- 调研
- 最佳实践
- learn
author: 小喵
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- patch
- skill_manage
- skills_list
- skill_view
metadata:
  hermes:
    tags:
    - learning
    - research
    - meta-skill
    - knowledge-integration
    related_skills:
    - web-access
    - skill-creator
    category: learning
    skill_type: research
    design_pattern: pipeline
---
# 小喵学习技能 · Meta-Skill 持续进化版

> **核心定位**：本 skill 本身成长的是**学习方法论**（搜索技巧、过滤标准、清洗方法、精炼模板、整合策略），
> **学习的内容**通过 skill-creator 流程输出到对应的领域 skill（已有的或新创建的）。

## 触发条件

**使用此 skill 当：**
- 用户要求"学习/研究/了解"某个主题
- 遇到不熟悉的新技术、工具、概念
- 需要为某个领域创建或更新 skill
- 需要对比多个方案并给出建议

**不使用此 skill 当：**
- 只需简单事实性回答
- 用户明确要求不联网
- 已有 skill 完全覆盖该主题且信息最新

## 核心能力框架（持续进化）

本 skill 成长的是以下 5 种能力，每次学习后都应迭代优化：

### 1. 信息收集能力
- 如何高效使用 web-access 的各种工具（Search/Extract/Crawl/Map/Browser）
- 如何组合不同搜索策略获取全面信息
- 如何定位官方文档和权威来源

### 2. 信息过滤能力
- 如何判断信息质量（官方 > 权威教程 > 社区 > 个人博客）
- 如何识别过时信息（检查日期、版本号、API 变更）
- 如何去重和去噪

### 3. 信息清洗能力
- 如何提取关键信息，去除营销话术和冗余内容
- 如何识别并记录配置示例、代码片段、最佳实践
- 如何处理矛盾信息（交叉验证）

### 4. 信息精炼能力
- 如何用自己的话总结复杂概念
- 如何结构化呈现（表格、列表、代码块）
- 如何提炼可操作的步骤和建议

### 5. 知识整合能力
- 如何确定学习内容应该输出到哪个 skill
- 如何通过 skill-creator 创建新 skill 或更新已有 skill
- 如何保持 skill 的原子化和结构一致性

## 学习流程（Pipeline）

### Stage 1: 需求澄清

明确：
- 学什么？（主题、范围、深度）
- 输出到哪里？（已有 skill / 新 skill / 临时笔记）
- 需要什么格式？（教程 / 对比 / 速查表 / API 参考）

### Stage 2: 信息收集（通过 web-access）

**必须先加载 web-access skill**，由它决策搜索策略：

```
学习目标 → web-access → 搜索策略：
├─ 快速了解概况 → Tavily Search（5-10 条结果）
├─ 深入阅读文章 → Tavily Extract（精读 2-3 篇）
├─ 系统性知识 → Tavily Crawl（官方文档站点）
└─ 交互式学习 → CDP Browser（动态页面/需要登录）
```


> 🔍 **## Stage 3: 信息过滤与清洗** moved to [references/detailed.md](references/detailed.md)
