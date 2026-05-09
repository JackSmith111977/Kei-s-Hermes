---
name: learning
description: "当你需要从零开始学习一个新主题、研究新技术、了解陌生领域时使用此 skill。涵盖：联网上下文补充引擎、过滤高质量信息、清洗冗余内容、精炼核心知识、最终通过 skill-creator 沉淀为可复用的 skill。v2.6 核心升级：强制联网补充协议，内置信息源分级、时效性门禁与交叉验证机制。"
version: 2.8.0
triggers:
- 学习
- 研究
- 调研
- 最佳实践
- learn
- 学学
- 深入了解
- 查一下
- 沉淀
- 总结复盘
- 学习总结
- 自驱动
- 帮我搞懂
- 我想学
- 这是什么
- 怎么用
- 怎么用XXX
- 搞懂
- 了解
- 了解一下
- 看看
- 探索
- 掌握
- 熟悉
- 入门
- 新手教程
- 从零开始
- 快速上手
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
    - reflection
    - self-driven
    related_skills:
    - web-access
    - skill-creator
    - learning-workflow
    - learning-review-cycle
    category: learning
    skill_type: research
    design_pattern: pipeline
depends_on:
  - web-access
  - skill-creator
  - learning-workflow
  - learning-review-cycle
---
# 🧠 小喵学习技能 · Meta-Skill 持续进化版 v2.2

> **核心定位**：本 skill 本身成长的是**学习方法论**（搜索技巧、过滤标准、清洗方法、精炼模板、整合策略），
> **学习的内容**通过 skill-creator 流程输出到对应的领域 skill（已有的或新创建的）。

## 触发条件

**使用此 skill 当：**
- 用户要求"学习/研究/了解"某个主题
- 遇到不熟悉的新技术、工具、概念
- 需要为某个领域创建或更新 skill
- 需要对比多个方案并给出建议
- 需要深度研究一个复杂领域

**不使用此 skill 当：**
- 只需简单事实性回答
- 用户明确要求不联网
- 已有 skill 完全覆盖该主题且信息最新

## 核心能力框架（持续进化）

## 核心能力框架（持续进化）

### 0. 🧠 认知科学基础 (v2.7 新增)

**基于证据最强的学习理论**（Bjork "Desirable Difficulties"、Cepeda 2008、Roediger & Karpicke 2006）：

| 原则 | 含义 | 在 AI 学习中的映射 |
|------|------|-------------------|
| **Spaced Repetition（间隔重复）** | 在遗忘曲线临界点复习，强化长期记忆 | 学习后安排 1天/7天/30天 间隔复习 |
| **Active Recall（主动回忆）** | 从记忆中主动提取而非被动重读 | 验证时不看原始资料，凭理解重写 |
| **Interleaving（交替学习）** | 混合不同主题，迫使大脑区分概念 | 相关主题交替学习，建立跨领域连接 |
| **Desirable Difficulties（合意困难）** | 适度困难促进长期保持 | 学习过程不应"太容易"，引入质量门检 |

本 skill 成长的是以下 **6 种能力**，每次学习后都应迭代优化：

### 1. 信息收集能力
- 如何高效使用 web-access 的各种工具（Search/Extract/Crawl/Map/Browser/CDP）
- 如何组合不同搜索策略获取全面信息
- 如何定位官方文档和权威来源
- **研究分治策略**：复杂主题拆为 3-5 个原子子主题，每个独立搜索后合并
- **交叉源对比法**：同一主题从 arXiv(学术)/Blog(实践)/GitHub(开源) 三个角度搜集
- **CDP 浏览器获取**：需要 JS 渲染/登录态/反爬绕过时，优先使用 CDP 浏览器工具直达源头
- **多工具编排**：Search(找线索) → Extract(获取内容) → Browser(深入源头) → Vision(验证) 的组合链

### 2. 信息过滤能力
- 如何判断信息质量（官方 > 权威教程 > 社区 > 个人博客）
- 如何识别过时信息（检查日期、版本号、API 变更）
- 如何去重和去噪
- **无价值丢弃原则**：过滤出明确无价值的内容直接标记丢弃，节约 80% 认知存储

### 3. 信息清洗能力
- 如何提取关键信息，去除营销话术和冗余内容
- 如何识别并记录配置示例、代码片段、最佳实践
- 如何处理矛盾信息（交叉验证）
- 如何识别 AI 生成内容的痕迹

### 4. 信息精炼能力
- 如何用自己的话总结复杂概念
- 如何结构化呈现（表格、列表、代码块）
- 如何提炼可操作的步骤和建议
- 如何选择合适的信息呈现形式

### 5. 知识整合能力
- 如何确定学习内容应该输出到哪个 skill
- 如何通过 skill-creator 创建新 skill 或更新已有 skill
- 如何保持 skill 的原子化和结构一致性
- 如何建立 skill 间的引用关系

### 6. 反思迭代能力（v2.1 新增）
- 每次学习后反思：搜索策略是否高效？过滤标准是否合理？
- 将反思结果写入 `reflections/` 目录
- 将可复用的方法论改进更新到 learning skill 本身

## 学习流程（Pipeline）

```
Stage 1: 需求澄清 → Stage 2: web-access 收集 → Stage 3: 过滤清洗
  → Stage 4: 精炼 → Stage 5: skill-creator 整合 → Stage 6: 反思迭代
```

### Stage 1: 需求澄清

明确：
- **学什么？**（主题、范围、深度）
  - 复杂主题 → 拆分为原子子主题
  - 简单主题 → 直接搜索
- **输出到哪里？**（已有 skill / 新 skill / 临时笔记）
- **需要什么格式？**（教程 / 对比 / 速查表 / API 参考 / 学习路径）
- **学习模式？**（快速模式 vs 深度模式）
  - **快速模式**：搜索 → 阅读 1-2 篇 → 直接输出笔记
  - **深度模式**：全流程（搜索 → 阅读 3+ 篇 → 精炼 → 创建/更新 skill → 验证）

### Stage 2: 联网上下文补充 (Online Context Supplementation) 🔗
**🚨 铁律：禁止仅凭训练数据回答陌生领域！必须启动联网补充协议。**

**Step 2.1: 加载决策器**
必须先执行 `skill_view(name="web-access")`，由该 skill 的路由机制决定搜索策略（Search / Crawl / Extract / Browser）。

**Step 2.2: 信息源优先级 (Source Hierarchy)**
- 🥇 **官方文档/源码** (GitHub, 官方指南, API Reference) → 权威性最高，优先采信
- 🥈 **权威社区/实践** (StackOverflow 高票, 官方 Discord/论坛, 核心贡献者博客) → 需交叉验证
- 🥉 **AI 摘要/聚合站** → **仅作为线索入口**，绝不可直接作为最终事实依据！

**Step 2.3: 时效性与版本门禁 (Freshness Gate)**
- 必须记录信息的**发布日期**和**适用版本号**。
- 技术类知识若超过 **12 个月**未更新，视为 `"🟠 高风险/可能过时"`，必须寻找最新 `vX.Y` 的替代方案。
- 记录环境依赖矩阵 (e.g., `Requires Python 3.10+`, `Deprecated in v2.0`)。

**Step 2.4: 交叉验证 (Triangulation)**
- 核心结论/配置参数必须找到 **≥2 个独立来源** 佐证。
- 若来源冲突，以**官方文档**为准；若无官方文档，标记为 `[⚠️ 社区争议/待验证]`。

**Step 2.5: 输出去噪与沉淀**
- 剥离营销话术、SEO 填充内容、AI 生成痕迹。
- 提取核心逻辑、代码片段、配置参数，存入临时笔记或 `references/`。

**Step 2.6: 源头优先获取策略 (v2.8 新增)**
在加载 web-access 后，根据信息类型选择工具链：

1. **判断信息类型**（参照 web-access skill 的「源头信息获取框架」）
   - 搜索引擎能搜到？→ `web_search` + `web_extract`
   - 已知 URL 的静态页面？→ `web_extract` / `curl`
   - 需要 JS 渲染的动态页面？→ `browser_navigate` + `browser_console`
   - 需要登录态/反爬绕过？→ CDP Proxy 或复用已有 session
   - SPA/API 数据？→ `browser_console` 捕获 Network response

2. **选择工具链**（从 web-access 的工具组合矩阵中选择）
   - 快速调研：`web_search` → `web_extract` × 3-5
   - 深度调研：`web_search` → `browser_navigate`(直入源头) → `browser_console`(JS提取)
   - 源头溯源：`web_search`(找源头URL) → `browser_navigate`(直达原始来源) → `browser_vision`(截图验证)
   - 反爬绕过：CDP Proxy → anti-detection 脚本注入 → 真实点击

3. **源头优先**：优先直接访问原始来源（官方文档、GitHub 源码、权威网站），避免过度依赖二手资料聚合站

**Step 2.7: 信息溯源方法论 (v2.8 新增)**
每个发现的信息片段必须追溯其原始来源：

1. **前向追踪**：从搜索结果 → 找到引用的原始来源 URL
   - 博客引用论文？→ 找到论文原文
   - 社区帖引用官方文档？→ 找到官方文档原文
   
2. **后向验证**：从原始来源 → 检查是否有 ≥2 个独立来源佐证
   - 官方文档 + 权威教程 = 可靠
   - 仅社区帖 = 需进一步验证

3. **横向比对**：同一信息在不同类型来源中的一致性
   - 学术(arXiv) vs 实践(Blog) vs 开源(GitHub) 三方一致 → 高可信

**质量标记系统**：
| 标记 | 含义 | 使用 |
|:---:|:----:|:----:|
| 🥇 | 原始来源 | 官方文档/源码/一手数据 → 直接使用 |
| 🥈 | 高质量二手 | 权威教程/学术论文 → 交叉验证后使用 |
| 🥉 | 普通参考 | 博客/社区讨论 → 仅作为线索 |
| ⚠️ | 需验证 | 仅单一来源/无日期标注 → 继续搜索 |

**Step 2.8: 反爬应对策略 (v2.8 新增)**
当 `web_extract` 或 `browser_navigate` 失败时（被 Cloudflare/反爬拦截）：

```
1. 先用 browser_vision 截图确认是否被拦截
2. 尝试 CDP Proxy 操作有界面的浏览器（而非 headless）
3. 尝试 curl + 代理 + 伪造 User-Agent
4. 切换信息来源（放弃该站点，找替代源）
5. 标记为「源不可达」并记录到 site-patterns/
```

### Stage 3: 过滤与清洗

详见 `references/detailed.md`

关键原则：
1. **权威性优先**：官方文档 > 权威教程 > 社区 > 个人博客
2. **时效性检查**：检查发布日期、版本号、API 变更
3. **无价值丢弃**：明确无价值的内容直接丢弃，不记录
4. **交叉验证**：矛盾信息用官方文档验证

### Stage 4: 精炼输出

详见 `references/detailed.md`

**精炼模板**：
```markdown
## {主题}
### 核心概念
（用自己的话总结，3-5 句话）

### 关键特性/用法
| 特性 | 说明 | 示例 |
|------|------|------|

### 最佳实践
（经验总结、反模式、常见陷阱，分条列出）

### 与其他方案对比
（如适用，多维度对比表格）

### 学习路径建议
（如果复杂/进阶方向，推荐学习顺序）
```

### Stage 5: 知识整合（通过 skill-creator）

详见 `references/integration-patterns.md`

**决策树**：
```
精炼后的知识 → 
├─ 已有 skill 覆盖该领域？
│   ├─ 是 → 通过 skill-creator 更新
│   └─ 否 → 是否需要创建新 skill？
└─ 否则 → 作为 references 存入现有 skill
```

### Stage 6: 反思迭代（v2.7 增强）

**每次学习后必须完成：**

1. **搜索策略反思**：
   - 本次搜索用了什么关键词？效果如何？
   - 有没有更高效的搜索方式？

2. **过滤清洗反思**：
   - 有没有漏掉重要的信息源？
   - 哪些信息源不可靠？加入排除列表。

3. **可复用技巧沉淀**：
   - 学到了什么搜索/过滤技巧？
   - 能否写入 `references/` 让下次复用？

4. **更新方法论**：
   - 新的技巧写入对应的 references 文件
   - 更新 `references/detailed.md` 中的"已积累的学习经验"表

5. **自动触发学习总结**（v2.2 新增）：
   ```bash
   python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py summary "{主题}" "{模式}" {耗时} "{产出}"
   ```

6. **🔄 深度循环门检 (v2.7 新增 — 受 Memento-Skills 2025 启发)**：
   - 检查学习产出质量（信息覆盖度 + 交叉验证 + 可操作性 + 结构完整度）
   - 质量分 < 60 → 进入 Loop N+1 重新学习（最多 3 次循环）
   - 分析失败类型，决定回到哪个步骤

7. **🧠 AI 自改进模式应用 (v2.7 新增 — 受 Gödel Agent / RISE 2024-2025 启发)**：
   - **Self-Reflection**：学习后反思"boku 这次学习哪里做得不好？"
   - **Verified Trace**：记录成功和失败的学习轨迹到 `~/.hermes/learning/traces/`
   - **Skill Mutation**：不只是创建 skill，还要能"重写"过时的 skill
   - **Adversarial Validation**：启动子代理作为"挑错者"，专门找 skill 的漏洞

8. **知识缺口探测与深度循环 (v2.4 核心进化)**：
   - **🚨 深度循环门禁 (Deep Loop Gate)**：
     - **检查点**：本次学习是否产生了实质性的 **Artifact (制品)**？
     - **标准**：必须至少包含以下一项：
       - 更新或创建了一个 **Skill** (通过 skill-creator)
       - 沉淀了一条高价值的 **Memory** (通过 memory tool)
       - 输出了一份实战指南存入 `~/.hermes/docs/learning-logs/`
     - **如果未通过**：🛑 **拦截！** 判定为"浅层浏览"。必须进入 **Loop N+1**，针对未掌握的难点重新执行 Stage 2-5，直到产出 Artifact 为止！
   - **🛡️ Memory 满时的降级策略 (v2.5 新增)**：
     - 如果调用 Memory 工具失败（如超出容量限制），**绝不停止！**
     - **自动执行降级**：将学习精华输出为 Markdown 文件，保存至 `~/.hermes/docs/learning-logs/` 目录下。
     - 文件名格式：`{date}-{topic}-summary.md`。
   - **遇到困难了吗？** → 调用 `gap-add` 记录为知识缺口
     - 检查点：本次学习是否产生了实质性的 **Artifact (制品)**？
     - **标准**：必须至少包含以下一项：
       - 更新/创建了一个 **Skill** (通过 skill-creator)
       - 沉淀了一条高价值的 **Memory** (通过 memory tool)
       - 输了一份实战指南存入 `references/`
     - **如果未通过**：🛑 **拦截！** 判定为"浅层浏览"。必须进入 **Loop N+1**，针对未掌握的难点重新执行 Stage 2-5，直到产出 Artifact 为止！
   - **遇到困难了吗？** → 调用 `gap-add` 记录为知识缺口
     ```bash
     python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py gap-add knowledge_conflict "描述" high
     ```
   - **skill 有过时信息？** → 调用 `gap-add` 记录为"知识过时"
     ```bash
     python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py gap-add knowledge_outdated "描述" high
     ```
   - **发现缺少的 skill？** → 调用 `gap-add` 记录为"知识缺失"
     ```bash
     python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py gap-add knowledge_missing "描述" medium
     ```

9. **🗂️ 经验提取与归档 (v2.8 新增 — 受 Post-mortem + PlugMem/MUSE 启发)**
   每次学习完成后，必须评估是否有可复用的经验。

   **判断标准**（至少满足一项）：
   - 发现了一个可复用的方法/模式/原则
   - 解决了以前卡住的问题，找到了可靠方案
   - 验证了一个假设，推翻了错误认知

   **提取流程**：
   1. 判断是否有可复用的经验 → 无则跳过
   2. 有则按标准格式写入 `~/.hermes/experiences/active/`
   3. 分类：experience（动作级）/ skill（任务级）/ rule（原则级）
   4. 评分：reusability (high/medium/low) + confidence (1-5)
   5. 若 reusability=high → 自动更新对应 skill 的 references/
   6. 更新 `~/.hermes/experiences/index.md` 目录
   7. 注册间隔复习（7天后）

   **经验类型体系**（借鉴 Experience Compression Spectrum）：
   | 类型 | 压缩率 | 说明 | 存储位置 |
   |:----:|:------:|:----|:---------|
   | **Experience** | 低 | 具体情境下的发现，含背景 | experiences/active/ |
   | **Skill** | 中 | 可重复的流程/模式 | experiences/skills/ → skill 更新 |
   | **Rule** | 高 | 抽象原则，无具体绑定 | experiences/archive/ |

## 输出规范

学习完成后，必须输出：

1. **一句话总结**（核心结论）
2. **关键要点**（3-5 条）
3. **输出目标**（写入了哪个 skill / 创建了什么新 skill）
4. **方法论改进**（本次学习对 filtering/washing/integration 的改进）
5. **下一步建议**（还需要深入学习什么）
6. **学习路径建议**（推荐学习顺序：先学什么→再学什么→最后学什么）

## 设计模式映射

| 模式 | 用法 | 适用场景 |
|------|------|----------|
| 🔄 **Pipeline** | 主流程（Stage 1→6 顺序执行） | 标准学习流程 |
| 🎤 **Inversion** | 先确定最终输出，反推需要的信息 | 复杂主题研究 |
| 🏭 **Generator** | 通过 skill-creator 创建/更新 skill | 知识沉淀 |
| 🔍 **Tool Wrapper** | web-access 封装所有搜索策略 | 信息收集 |

## Red Flags（常见错误）

- ❌ 仅凭记忆回答不确定的问题 → 必须先联网搜索
- ❌ 学习内容写入 learning skill 本身 → 应输出到对应的领域 skill
- ❌ 不更新学习方法论 → 每次学习后应反思迭代
- ❌ 跳过 skill-creator 直接创建/修改 skill → 必须经过 skill-creator 流程
- ❌ 跳过 web-access 直接搜索 → 必须通过 web-access 路由
- ❌ 复杂主题不拆分直接搜索 → 信息过载，应先研究分治
- ❌ 长期任务不汇报进度 → 每完成一个 Stage 必须汇报
- ❌ 只搜索不沉淀 → 学习必须产出知识文件
- ❌ 经验不提取归档 → 每次学习后应检查是否有可复用的经验，按标准格式写入 ~/.hermes/experiences/

## 已积累的学习经验

| 日期 | 学到的主题 | 方法论改进 | 新积累的技巧 |
|------|-----------|-----------|-------------|
| 2026-05-03 | Mermaid 图表 | 优先提取"场景模板"而非纯语法 | 收集 Cheat Sheet 和常见场景模板 |
| 2026-05-03 | WeasyPrint PDF | 官方文档 First Steps 是最佳入口 | pip vs apt 选择标准; Jinja2+CSS 分离 |
| 2026-05-03 | lark-oapi / lark-mcp | 先搞清"是否需要"再去选"怎么用" | SDK 直接看 GitHub demo 比官网快 |
| 2026-05-03 | 工具审计 | 分阶段学习更高效 | 学习目标拆成原子主题按顺序学 |
| 2026-05-03 | P0-P2 能力提升 | 分批吸收信息避免过载 | Python logging、Git rebase、Linux排查 |
| 2026-05-04 | Agent 学习 | 研究分治策略对抗信息爆炸 | 交叉源对比法; 无价值丢弃原则 |
| 2026-05-04 | PPT 制作系统学习 | 中英文混合搜索 + 多源交叉验证 | 英文搜趋势理论+中文搜实战技巧；子代理验证能发现自身未知错误 |
| 2026-05-04 | 本学习流程改进 | 自举式改进 learning-workflow | 多任务支持; 进度可视化; 反思机制 |
| 2026-05-04 | 深度循环学习机制 | 引入认知科学基础 + AI自改进前沿 | Spaced Repetition/Active Recall/Interleaving 映射到AI学习; Deep Loop Gate; Reflection Tokens; 间隔复习(1天/7天/30天); 学习质量评分公式 |
| 2026-05-04 | GitHub 提交质量检查 | git -S pickaxe 脱敏陷阱; 子代理验证找盲点; 文档一致性是AI项目最大痛点 | git diff脱敏需grep辅助; 按P0/P1/P2分优先级; 结构化报告可审计可比较; 不要在CI阶段才检查; 代码改了必须同步文档 |
| 2026-05-08 | Rust 2026 + Next.js 16.2 | 官方博客 > 社区 优先级有效; 多版本覆盖可追踪演化趋势; Tavily 限流时 web_search 降级无缝 | Rust 官方博客 + releases.rs + GitHub releases 三源验证; Next.js 官方博客是唯一权威源; 表格化对比呈现版本间演化; 知识库 freshness_score 更新到 0.7 |
| 2026-05-08 | TypeScript 6.0/7.0 + Rust 1.95 + Python 3.15b1 + Go 1.27 | 多语言并行学习有效；Beta 发布监测重要 | 跨语言版本追踪矩阵表；Bridge-vs-destination 定位 |
| 2026-05-08 | **改进 web-access + learning 调研流程** | **源头优先范式转变：从「用什么工具搜」→「信息源头在哪，选什么工具直达」；CDP 提升为一等公民；建立反爬 L1-L6 应对体系；Research Agent 模式（Bounded Pipeline/PRISM/Multi-Source）引入学习流程** | **CDP 浏览器直达源头（GitHub 权威来源）；工具组合矩阵（Search→Extract→Browser→Vision）；信息溯源三步法（前向追踪/后向验证/横向比对）；provenance 记录格式；质量标记系统（🥇🥈🥉⚠️）** |
| 2026-05-09 | **Productivity 领域研究（KM/Obsidian/Notion/Agent Orchestration）** | **多视角并行搜索法：追踪行业/产品型领域时，并行搜索4个独立视角（官方发布 + 开源生态 + 行业报告 + 技术实践），比单一关键词搜索覆盖更全面，交叉验证效率更高** | **并行搜索法：1)官方源（Notion releases）→ 直接获取官方更新；2)开源生态（GitHub Obsidian MCP）→ 发现并行竞品项目；3)行业报告（KMWorld/Yenra）→ 宏观趋势判断；4)技术实践（ValueStreamAI/StackAI）→ 可操作模式；KM行业权威来源分级（🥇KMWorld/Gartner → 🥈Yenra/Zylos → 🥉普通博客）** |

## 知识库索引

| 文件 | 内容 | 最后更新 |
|------|------|----------|
| `references/filtering-standards.md` | 信息过滤标准和质量评估维度 | 2026-05-04 |
| `references/washing-techniques.md` | 信息清洗方法和去噪技巧 | 2026-05-04 |
| `references/integration-patterns.md` | 知识整合模式和 skill 更新策略 | 2026-05-04 |
| `references/detailed.md` | 完整学习流程细节（Stage 3-6） | 2026-05-04 |
