---
name: learning
version: "2.0.0"
author: 小喵
license: MIT
description: >
  Meta-skill：持续进化的学习方法论。负责信息收集、过滤、清洗、精炼，
  以及将知识整合到对应的领域 skill 中。它本身成长的是学习技巧、
  整合技巧、信息处理能力，而非学习内容。学习内容输出到目标 skill。
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
    tags: [learning, research, meta-skill, knowledge-integration]
    related_skills: [web-access, skill-creator]
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

### Stage 3: 信息过滤与清洗

应用当前积累的过滤标准（见 `references/filtering-standards.md`）：

**过滤维度：**
| 维度 | 标准 | 权重 |
|------|------|------|
| 权威性 | 官方文档 > 权威教程 > 社区讨论 > 个人博客 | 40% |
| 时效性 | 近 1 年 > 1-2 年 > 2-3 年 > 3 年以上 | 30% |
| 实用性 | 可操作 > 理论 > 概念介绍 | 20% |
| 完整性 | 全面覆盖 > 部分覆盖 > 单一角度 | 10% |

**清洗步骤：**
1. 去除营销内容、重复信息
2. 提取关键概念、代码示例、配置片段
3. 交叉验证矛盾信息
4. 标注信息来源和时效性

### Stage 4: 信息精炼

用结构化模板精炼知识：

```markdown
## {主题}
### 核心概念
（用自己的话总结，3-5 句话）

### 关键特性
| 特性 | 说明 | 示例/备注 |
|------|------|-----------|

### 使用方法
（分步骤，包含代码示例）

### 最佳实践
（经验总结、反模式、常见陷阱）

### 与其他方案对比
（如适用，多维度对比表格）

### 延伸阅读
- [来源 1](URL) - 权威性/时效性标注
- [来源 2](URL)
```

### Stage 5: 知识整合（通过 skill-creator）

**确定输出目标：**

```
精炼后的知识 → 决策：
├─ 已有 skill 覆盖该领域？
│   ├─ 是 → 通过 skill-creator 的 M1-M4 流程更新该 skill
│   └─ 否 → 继续
├─ 该领域需要独立 skill？
│   ├─ 是 → 通过 skill-creator 创建新 skill
│   └─ 否 → 继续
└─ 作为 references 存入现有 skill？
    └─ 是 → 写入目标 skill 的 references/ 目录
```

**整合原则：**
- 遵循原子化拆解原则（一个 skill 专注一个领域）
- 遵循 skill-creator 的 9 阶段流程
- 保持 skill 结构一致性（SKILL.md + references/ + checklists/）

### Stage 6: 学习经验迭代

**更新 learning skill 本身：**

1. **更新 `references/filtering-standards.md`**
   - 新增/调整过滤标准
   - 记录本次发现的高质量信息源

2. **更新 `references/washing-techniques.md`**
   - 新增信息清洗技巧
   - 记录处理矛盾信息的经验

3. **更新 `references/integration-patterns.md`**
   - 新增知识整合模式
   - 记录 skill 创建/更新的最佳实践

4. **更新 SKILL.md 中的"已积累的学习经验"表格**

## 已积累的学习经验

<!-- 每次学习后，在此处记录方法论的改进 -->

| 日期 | 学习的主题 | 方法论改进 | 新积累的过滤/清洗/整合技巧 |
|------|-----------|-----------|--------------------------|
<!-- 示例 -->
<!-- | 2026-05-03 | FastAPI | 新增 API 框架类学习模式 | 优先关注路由定义、依赖注入、中间件 | -->

## 知识库索引（学习经验的存储）

| 文件 | 内容 | 最后更新 |
|------|------|----------|
| `references/filtering-standards.md` | 信息过滤标准和质量评估维度 | 2026-05-03 |
| `references/washing-techniques.md` | 信息清洗方法和去噪技巧 | 2026-05-03 |
| `references/integration-patterns.md` | 知识整合模式和 skill 更新策略 | 2026-05-03 |

## 学习原则

### 1. 联网优先，记忆为辅
- 不确定的信息必须先搜索验证
- 记忆中的信息需要搜索确认时效性
- 优先官方文档 > 权威教程 > 社区讨论

### 2. 内容与方法分离
- **学习内容** → 输出到对应的领域 skill
- **学习方法** → 积累到 learning skill 本身
- 每次学习都应同时产出两者

### 3. 质量导向
- 信息质量 > 信息数量
- 深度理解 > 表面覆盖
- 可操作性 > 理论描述

### 4. 持续迭代
- 每次学习后反思：搜索策略是否高效？过滤标准是否合理？
- 定期更新 filtering-standards.md 和 washing-techniques.md
- 积累不同领域的学习模式

## Red Flags（常见错误）

- ❌ 仅凭记忆回答不确定的问题 → 必须先联网搜索
- ❌ 学习内容写入 learning skill 本身 → 应输出到对应的领域 skill
- ❌ 不更新学习方法论 → 每次学习后应迭代 filtering/washing/integration 经验
- ❌ 跳过 skill-creator 直接创建/修改 skill → 必须经过 skill-creator 流程
- ❌ 跳过 web-access 直接搜索 → 必须通过 web-access 路由

## 输出规范

学习完成后，必须输出：
1. **一句话总结**（核心结论）
2. **关键要点**（3-5 条）
3. **输出目标**（写入了哪个 skill / 创建了什么新 skill）
4. **方法论改进**（本次学习对 filtering/washing/integration 的改进）
5. **下一步建议**（还需要深入学习什么）

## 设计模式映射

### 🔄 Pipeline 模式（主流程）
```
Stage 1: 需求澄清 → Stage 2: web-access 信息收集 → Stage 3: 过滤清洗
→ Stage 4: 精炼 → Stage 5: skill-creator 整合 → Stage 6: 方法论迭代
```

### 🎤 Inversion 模式（逆向思考）
当学习复杂主题时：
1. 先确定"最终 skill 应该包含什么"
2. 反推需要收集哪些信息
3. 针对性搜索，避免信息过载

### 🏭 Generator 模式（skill 创建/更新）
1. 通过 skill-creator 创建或更新目标 skill
2. 将精炼后的知识按 skill 结构组织
3. 生成 SKILL.md + references/ + checklists/
