# Skill 设计规范与哲学 学习笔记

> 来源：分析现有 skill（writing-plans, systematic-debugging, test-driven-development, subagent-driven-development, hermes-agent）+ skill_manage 工具文档

---

## 一、Skill 设计哲学

### 1. Skill 的本质
Skill 是**程序性记忆**——告诉 agent "遇到这类任务时，按这个流程做"。
不是参考文档，不是知识库，而是**可执行的流程指南**。

### 2. 核心设计原则

#### 🎯 触发条件明确（When to Use）
- 好的 skill 有清晰的触发场景描述
- 在 YAML frontmatter 的 `description` 字段中体现
- 正文中明确列出"何时用"和"何时不用"

```
✅ 好的触发条件：
"Use when implementing any feature or bugfix, before writing implementation code."

❌ 差的触发条件：
"For development tasks"
```

#### 📏 任务粒度控制（Granularity）
- 每个任务 = 2-5 分钟专注工作
- 一个步骤 = 一个动作
- 避免"做X"这种模糊描述，改为"执行命令Y，期望输出Z"

#### 🔍 可验证的输出（Verifiability）
- 每个步骤都有明确的验证方式
- 包含精确的命令和期望输出
- 有完成清单（checklist）

#### 🚫 反模式清单（Red Flags / Anti-Patterns）
- 列出常见错误和陷阱
- 说明什么情况下不应该使用
- 包含"常见借口"及其反驳

#### 🔗 技能间关联（Integration）
- 明确说明与其他 skill 的协作关系
- 说明在什么流程中的什么位置使用

### 3. 写作风格原则

#### 简洁而完整
- 不要重复显而易见的内容
- 但必须包含所有关键细节
- 代码示例要完整可复制粘贴

#### 结构化
- 使用表格对比选项
- 使用清单跟踪进度
- 使用代码块展示命令和代码

#### 权威性
- 用"必须/禁止"而不是"建议/最好"
- 给出明确的规则而不是模糊的建议
- 解释"为什么"以增强遵从性

---

## 二、Skill 文件结构规范

### Frontmatter（YAML 头部）

```yaml
---
name: skill-name
description: |
  一句话描述 + 触发条件。
  当遇到 X、Y、Z 情况时使用此 skill。
version: 1.0.0
author: 作者
license: MIT
metadata:
  hermes:
    tags: [tag1, tag2, tag3]
    homepage: https://...
    related_skills: [skill-a, skill-b]
    category: optional-category
---
```

**关键字段：**
- `name`: 小写，连字符分隔
- `description`: 最重要的字段——agent 靠它决定是否加载此 skill
- `version`: 语义化版本
- `metadata.hermes.tags`: 用于搜索和分类
- `metadata.hermes.related_skills`: 关联技能

### 正文结构

```
# Skill 名称

## Overview
- 核心理念（一句话）
- 核心价值主张

## When to Use
- 明确的使用场景
- 明确的不使用场景

## The Process / Core Content
- 分步骤的流程
- 每个步骤有：目标、操作、验证

## Red Flags / Anti-Patterns
- 常见错误
- 如何避免

## Integration with Other Skills
- 与其他 skill 的协作

## Quick Reference
- 速查表/备忘录

## Remember
- 核心原则总结
```

---

## 三、Skill 描述（description）写作技巧

description 是 skill 选择的关键依据，需要包含：

1. **功能描述**：这个 skill 做什么
2. **触发条件**：什么情况下使用
3. **特征关键词**：帮助 agent 匹配

```yaml
# ✅ 好的 description
description: |
  文档排版设计与生成技能。涵盖 Word(.docx)、Excel(.xlsx)、PPT(.pptx)、PDF、
  Markdown、LaTeX、HTML、EPUB 等所有常见文档格式的编辑、转换、审美排版。
  当用户需要创建、编辑、美化任何格式的文档，或需要在不同格式之间转换时使用此技能。
```

```yaml
# ❌ 差的 description
description: Help with documents
```

---

## 四、现有 Skill 的问题分析

### doc-design skill 的问题
1. **description 过长**：包含了太多细节，应该简洁
2. **内容过于冗长**：SKILL.md 有 495 行，应该拆分到 references/
3. **缺少 Red Flags**：没有列出常见错误
4. **缺少验证步骤**：没有说明如何验证文档质量
5. **代码示例缺乏上下文**：只有代码，没有说明何时用哪个
6. **notes.md 和 notes-extended.md 内容重复**：应该整合

### web-access skill 的问题
1. **description 是中文**：应该用英文（agent 主要用英文匹配）
2. **缺少版本信息**：没有 version 字段
3. **结构不够清晰**：流程不够步骤化
4. **缺少故障排除部分**：没有 Red Flags 或 Troubleshooting

---

## 五、Skill 升级清单

升级一个 skill 时检查：

- [ ] description 是否清晰描述了触发条件？
- [ ] 是否有明确的 When to Use / When NOT to Use？
- [ ] 流程是否分步骤且可执行？
- [ ] 每个步骤是否有验证方式？
- [ ] 是否有 Red Flags / Anti-Patterns？
- [ ] 是否说明了与其他 skill 的集成？
- [ ] 是否有 Quick Reference / 速查表？
- [ ] 代码示例是否完整可复制？
- [ ] 内容是否适当拆分到 references/？
- [ ] frontmatter 是否完整？
