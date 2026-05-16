# 统一管理标准研究 — 最优 Skill 包结构 (2026-05-16)

> 深度调研 8 个行业标准 + 5 个生产实践 + 4 篇学术论文的浓缩摘要。
> 支撑 cap-pack 统一管理标准的 Level 0-3 框架设计。

## 一、行业标准调研

### 1.1 Agent Skills Spec (Anthropic) — 事实标准
- **目录**: `skill-name/{SKILL.md, scripts/, references/, assets/}`
- **frontmatter 必填**: `name`, `description`
- **可选**: `license`, `compatibility`, `metadata`, `allowed-tools`
- **三级渐进披露**: Metadata (~100t) → Instructions (<5K t) → Resources (按需)
- **SKILL.md** < 500 行 / < 5000 tokens
- **来源**: agentskills.io/specification

### 1.2 其他标准
| 标准 | 独特设计 | 可借鉴 |
|:-----|:---------|:-------|
| **USK v3** (AI Skill Store) | SKILL.md + interface/capabilities/permissions/schemas | 扩展字段设计 |
| **ccpkg** | ZIP 打包 + manifest | 多平台适配策略 |
| **Open Plugins** | 多组件 (skills+agents+hooks+MCP) | 可插拔架构 |
| **APS v0.1** | tarball + manifest + registry API | 注册中心接口设计 |
| **Microsoft Agent Skills** | C# class-based skills | 与 spec 兼容的实现参考 |

## 二、生产实践调研

| 实践 | 核心发现 | 对标准的启示 |
|:-----|:---------|:-------------|
| **Perplexity 技能工程** | 3 层嵌套 + 1945 节税法代码（分层导航至关重要） | 树状结构不是可选的——复杂领域必须层次化 |
| **skill-tree** (danielbrodie) | 88% token 节省，100% 路由精度，manifest 为唯一真相来源 | 簇路由器 + 叶子 skill 模式 |
| **Anthropic 官方指南** | 描述要「pushy」以对抗 under-triggering | 描述质量直接影响路由准确性 |
| **Agent Layer** | SKILL.md 结构应由 primacy/recency 效应驱动 | SKILL.md 内部章节顺序影响执行可靠性 |
| **Skillsmith** | 渐进披露 + 子代理 + 子技能模式 | 分层加载的标准模式 |

## 三、学术论文发现

| 论文 | 关键发现 | 对标准的意义 |
|:-----|:---------|:-------------|
| **SkillRouter** (arxiv 2603.22455) | 全文本比纯元数据路由精确 31-44pp | 合规检查必须读完整 SKILL.md |
| **SkillOrchestra** (arxiv 2602.19672) | Skill-aware 路由需技能手册 | 标准本身是 Agent 路由的基础设施 |
| **Corpus2Skill** (arxiv 2604.14572) | 导航式 skill 树 = 迭代 embed-cluster-summarize | 构建 skill 层次可自动完成 |
| **Louvain Skill Hierarchy** (NeurIPS 2023) | 模块最大化聚类生成多层 skill 层次 | 自动层次化的理论基础 |

### 3.1 相变临界点 (Phase Transition)

关键发现：LLM 的 skill 选择精度在 ~100-200 个 skill 时发生**相变**——不是逐渐降低，而是**急剧崩塌**。

| 规模 | 行为 | 推荐方案 |
|:----:|:-----|:---------|
| < 50 | 扁平列表可工作 | 简单语义分类 |
| 50-100 | 开始需要轻量分类 | 2 层结构（类别→skill） |
| 100-200 | **相变区**，精度急剧下降 | 必须层次化 + 簇路由器 |
| > 200 | 扁平路由几乎不可用 | 树状索引 + 簇路由 + 可选工作流编排 |

## 四、cap-pack 现有标准积累

| 组件 | 内容 | 状态 |
|:-----|:-----|:------|
| cap-pack-v2.schema.json | 包 manifest JSON Schema | ✅ 17 个 pack 验证通过 |
| SQS | 五维 skill 质量评分 | ✅ 200+ skill 已评分 |
| CHI | 六维综合健康指数 | ✅ 已嵌入代码 |
| skill-tree-index | 三层树状索引 | ✅ 生成 + 合并建议 |
| EPIC-004 质量标准 | 低分率<15%, L2/L3 全覆盖 | ✅ 已执行完毕 |
| 行业生态调研 (§13) | 12 工具 + 4 论文 + 7 维差距 | ✅ 已纳入 SKILL.md |

## 五、直接影响的标准设计决策

| 发现 | 对标准框架的影响 |
|:-----|:----------------|
| Agent Skills Spec 是事实标准 | Level 0 必须 100% 兼容，不应 fork |
| 相变临界点 ~100-200 | Level 2 要求树状归属（超过 50 skill 的包必须层次化） |
| 全文本 > 元数据 | Level 1-3 检查必须读完整 SKILL.md |
| 现有工具不覆盖 cap-pack 合规 | Level 1 的 cap-pack 合规项是独特护城河 |
| 多 Agent 生态需要最小公共标准 | Level 0 兼容层确保跨平台可移植性 |
