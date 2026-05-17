---
name: knowledge-routing
description: "Multi-dimensional knowledge routing — decide where to store new knowledge: Memory, User profile, Experience archive, Skill, or L3 Brain. Full three-layer knowledge system support."
version: 3.2.0
triggers:
  - 知识路由
  - 知识分类
  - 存入Memory
  - 存入User
  - 存入经验
  - 存入Skill
  - 存入Brain
  - 存入L3
  - 存入知识库
  - 经验吸收
  - 经验沉淀
  - 总结
  - 总结经验
  - 复盘
  - 踩坑
  - 教训
  - 经验教训
  - 记下来
  - 学到的经验
  - 沉淀经验
  - 知识库
  - ⭐ 新增触发词:
  - 自动检测
  - auto-detect
  - 自动沉淀
  - 自动 ingest
  - knowledge-ingest
  - 管线
  - 链路
  - 知识链路
  - 健康检查
  - review-cycle
  - self-review
metadata:
  hermes:
    tags: [knowledge-management, routing, memory, skills, experiences, brain]
    category: meta
depends_on: []

---

# 知识路由指南 v3.2 — 三层知识库完全适配版 + Pipeline 集成

> **基于 PlugMem 知识分类 + Experience Compression Spectrum + 三层知识库架构**

---

## 五维路由决策树

### 决策流程

```
遇到新经验/知识/教训 ↓
第一维：判断知识类型
├─ 命题知识（事实/偏好/环境） → 第二维 A
└─ 程序知识（流程/方法/模式） → 第二维 B

第二维 A（命题知识）：
├─ 用户相关（偏好/习惯/风格） → User 存储
├─ 环境相关（OS/工具/配置） → Memory 存储
└─ 一次性事实（某 API 报错） → Memory 存储

第二维 B（程序知识）：
├─ 复用频率 ≤ 1 次？ → Experience 存储
├─ 复用频率 2-3 次？ → 第五维：知识深度
│   ├─ 深度浅（具体技巧/单场景） → Experience 存储
│   └─ 深度深（通用模式/方法论） → L3 Brain 存储
└─ 复用频率 > 3 次？ → 第五维：知识深度
    ├─ 深度浅（操作步骤/命令） → Skill 存储
    └─ 深度深（核心概念/理论） → L3 Brain + Skill 双存

第三维：知识抽象层次（新增 — L3 Brain 专用）
├─ 核心概念（定理/原则/模式） → concepts/ （如 Bounded Autonomy）
├─ 实体档案（人/公司/工具/项目） → entities/（如 GBrain, Karpathy）
├─ 资料摘要（文档/论文提炼） → summaries/
└─ 分析洞察（对比/推演/论证） → analyses/

第四维：Hermes 环境适配
├─ Memory 容量检查（>80% → 先 consolidate）
├─ 检查 Curator 状态 → 避免创建重复 skill
├─ 检查 brain 知识库 → 避免创建重复页面
├─ 参考 SRA 推荐 → 了解上下文
└─ 检查 experiences/ 中是否有类似经验

第五维：知识深度（新增 — L2 vs L3 的关键区分）
├─ 深度浅（Specific）→ 具体情境、单次验证、操作细节 → L2 Experience
└─ 深度深（General）→ 抽象模式、跨场景适用、核心理论 → L3 Brain
```

---

## 五个存储目标

### 1. 🧠 Memory — Agent 笔记 (目标: memory)
- **用途**：环境事实、工具特性、工作流规范、一次性教训
- **容量**：2,200 chars
- **特点**：Frozen snapshot pattern
- **操作**：`memory(action="add/replace/remove", target="memory")`
- **满时处理**：先 consolidate 或 replace 合并，再添加

### 2. 👤 User — 用户画像 (目标: user)
- **用途**：用户偏好、沟通风格、习惯、个人设定
- **容量**：1,375 chars
- **操作**：`memory(action="add/replace/remove", target="user")`

### 3. 📁 Experience — 经验档案 (目标: L2)
- **用途**：具体情境下的可复用发现，含完整背景
- **路径**：`~/.hermes/experiences/active/`
- **格式**：YAML frontmatter + 结构化 body
- **操作**：`write_file("~/.hermes/experiences/active/exp-{date}-{id}.md")`
- **升级路径**：reusability=high + 深度深 → 同时提炼到 L3 Brain

### 4. ⚙️ Skill — 程序知识 (目标: L1)
- **用途**：可复用的流程、模式、避坑指南
- **路径**：`~/.hermes/skills/`
- **操作**：`skill_manage(action="patch/create")`
- **前置检查**：加载 `skill-creator`，检查 curator 状态

### 5. 🧬 L3 Brain — 知识库 (目标: L3) ⭐ 新增
- **用途**：结构化的实体级知识（概念、人物、摘要、分析）
- **路径**：`~/.hermes/brain/wiki/{type}/{name}.md`
- **页面类型**：

| 类型 | 路径 | 适合存入的知识 | 示例 |
|:----|:-----|:-------------|:-----|
| concepts/ | `brain/wiki/concepts/` | 核心概念、设计原则、理论模式 | Bounded Autonomy |
| entities/ | `brain/wiki/entities/` | 人物、工具、项目、公司的档案 | Andrej Karpathy |
| summaries/ | `brain/wiki/summaries/` | 文档/论文/学习的摘要提炼 | 文件系统自主管理 |
| analyses/ | `brain/wiki/analyses/` | 对比分析、推演论证、研究结论 | 三层知识库架构对比 |

- **操作流程**：
  1. 选择页面类型（concepts/entities/summaries/analyses）
  2. 遵循 `brain/AGENTS.md` 页面模板写入内容
  3. 使用 `[[页面名称]]` 建立交叉引用
  4. 更新 `brain/index.md` 索引
  5. 追加 `brain/log.md` 日志条目
  6. 更新 `KNOWLEDGE_INDEX.md`（如涉及新主题）

---

## Pipeline 集成 — 端到端知识链路

> **知识路由现在是整个知识管线的中枢纽带**，连接各阶段形成闭环。

```
┌─────────────────────────────────────────────────────┐
│                 学习/调研阶段                         │
│  learning-workflow (v5.4) → STEP 6 反思总结          │
│  deep-research → 研究结论                            │
│  日常开发 → 踩坑教训                                 │
└─────────────────┬───────────────────────────────────┘
                  │ 知识原始材料
                  ▼
┌─────────────────────────────────────────────────────┐
│                 路由判断阶段 (本 Skill)                │
│  五维决策树 → 类型/频率/深度/层级/容量判断             │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Memory   │ │ User    │ │ L2 Exp   │ │ L3 Brain│ │
│  │ 2200chr  │ │ 1375chr │ │ 具体技巧  │ │ 核心概念 │ │
│  └──────────┘ └─────────┘ └──────────┘ └─────────┘ │
│                          │ 指令                      │
│                          ▼                           │
│          ╔═══════════════════════════════╗            │
│          ║  knowledge-ingest.py          ║ ← 统一入口  │
│          ║  (--auto-detect / 直接模式)    ║            │
│          ╚═══════════════════════════════╝            │
└─────────────────┬───────────────────────────────────┘
                  │ 执行结果
                  ▼
┌─────────────────────────────────────────────────────┐
│              健康检查/Review 阶段                      │
│  learning-review-cycle (v1.1)                       │
│  ├─ 每月 L1 Skill 新鲜度扫描                          │
│  ├─ 双周 L2 Experience 健康度检查                     │
│  └─ 每月 L3 Brain 知识库维护                          │
│                  │                                    │
│                  ▼ 发现过时/缺失                       │
│         ↻ 回到路由判断 → 重新沉淀                      │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│             知识沉淀/生命周期管理                       │
│  knowledge-precipitation (v1.3)                     │
│  ├─ 去重 → 合并 → 迁移 → 废弃                          │
│  ├─ KNOWLEDGE_INDEX.md 全局索引                      │
│  └─ 三层知识库一致性维护                              │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│             输出/消费阶段                              │
│  SRA 上下文注入 → 下次任务自动参考                      │
│  Memory 注入 → 日常任务使用                           │
└─────────────────────────────────────────────────────┘
```

### 关键循环

| 触发点 | 流程 | 涉及的 Skill |
|:------|:-----|:------------|
| **学习完成** | learning-workflow STEP 6 → 反思总结 → 触发路由 → ingest 自动沉淀 | 本 Skill + knowledge-ingest.py |
| **Review 发现过时** | review-cycle 发现 L2/L3 健康度低 → 触发路由 → 重新学习/更新 | 本 Skill + review-cycle |
| **自检触发** | self-review Knowledge 检查 → 自动检测未处理知识 | 本 Skill + self-review |
| **手动沉淀** | 用户说"记下来" → 路由判断 → 选择目标 → ingest | 本 Skill + knowledge-ingest.py |

### 快速定位

| 场景 | 直接跳到 |
|:----|:---------|
| 刚学完新知识 | ⏩ 执行清单 步骤 1-8（判断）→ 步骤 9（auto-detect）→ 步骤 10（ingest）|
| Review 发现过时条目 | ⏩ 执行清单 步骤 1（类型判断）→ 步骤 10（--type update）|
| 用户直说"记下来" | ⏩ 执行清单 步骤 1-8 → 步骤 10（直接模式）|
| 不知道要存什么 | ⏩ 执行清单 步骤 9（auto-detect 扫描）|

---

## 质量评分标准

| 分数 | 等级 | 标准 | 路由动作 |
|:---:|:----:|:----|:---------|
| 8-10 | 🟢 高 | 已验证 ≥2 次，有交叉验证，可复用性强 | 立即存入目标 |
| 4-7 | 🟡 中 | 已验证 1 次，需要进一步验证 | 存入 + 标记"待验证" |
| 0-3 | 🔴 低 | 未验证 / 仅单次观察 / 可能过时 | Experience 暂存 / 丢弃 |

---

## 执行清单

遇到新知识时，按顺序执行：

- [ ] 1. 判断知识类型（命题 vs 程序）
- [ ] 2. 判断复用频率（1次 vs 2-3次 vs 3次+）
- [ ] 3. **判断知识深度（新增）**：浅→L2/深→L3
- [ ] 4. **判断抽象层次（新增）**：concepts/entities/summaries/analyses
- [ ] 5. 检查 Memory 容量（>80% 则先 consolidate）
- [ ] 6. 如需创建 Skill → 先检查 curator 状态
- [ ] 7. **如需写入 Brain → 检查是否有重复页面**
- [ ] 8. 质量评分（0-10）
- [ ] 9. **自动检测未处理知识**（新增 — `--auto-detect` 模式）
   → 当触发时内容不明确或无指定内容时，先跑自动检测：

   ```bash
   # 扫描 learning-workflow 的 STEP 6 反思总结 → 自动批量沉淀
   python3 ~/.hermes/scripts/knowledge-ingest.py --auto-detect
   ```
   **适用场景**：学习总结完成后、Review 触发后、知识沉淀需求不明确时

- [ ] 10. **执行沉淀**（首选 — `knowledge-ingest.py` 统一入口）
   根据前面路由判断结果，选择对应 CLI 模式：

   **→ L2 Experiences（复用率低/深度浅/置信度中低）**
   ```bash
   python3 ~/.hermes/scripts/knowledge-ingest.py \
     --type experience --title "标题" --content "内容" \
     --reusability high --confidence 4
   ```
   *自动完成：文件创建 → index.md 更新 → KNOWLEDGE_INDEX 增量*

   **→ L3 Brain（深度深/核心概念/实体档案）**
   ```bash
   # 概念 (concept)
   python3 ~/.hermes/scripts/knowledge-ingest.py \
     --type concept --name "Bounded Autonomy" --content "七层约束体系..."
   
   # 实体 (entity)
   python3 ~/.hermes/scripts/knowledge-ingest.py \
     --type entity --name "Andrej Karpathy" --content "前 OpenAI, Tesla..."
   
   # 摘要 (summary)
   python3 ~/.hermes/scripts/knowledge-ingest.py \
     --type summary --name "论文摘要" --content "核心发现..."
   ```
   *自动完成：页面创建 → index.md 更新 → log.md 追加 → 交叉引用检测*

   **→ 双存：L1 Skill + L3 Brain（高频 + 深度深）**
   ```bash
   # 先在 brain 沉淀概念
   python3 ~/.hermes/scripts/knowledge-ingest.py \
     --type concept --name "Bounded Autonomy" --content "..."
   # 再使用 skill_manage 创建/更新 Skill
   ```
   *注意：脚本负责 L2/L3，L1 Skill 仍需 skill_manage 手动完成*

- [ ] 11. ~~更新 index~~ → 已由脚本自动完成
- [ ] 12. 通知用户存储结果

---

## 评估用例 (Eval Cases)

### Eval-001 (事实 → Memory)
- **输入**: "GitHub API 现在需要新的 Token 格式了"
- **预期**: 命题知识，一次性事实 → Memory 存储
- **检查**: 不使用 skill_manage，不涉及 Brain

### Eval-002 (流程 → Skill)
- **输入**: "每次部署前都要先扫描敏感文件，步骤是 1...2...3..."
- **预期**: 程序知识，复用 >3 次，深度浅 → Skill 更新/创建
- **检查**: 先加载 skill-creator

### Eval-003 (用户偏好 → User)
- **输入**: "主人偏好猫娘女仆风格"
- **预期**: 用户偏好 → User 存储
- **检查**: `memory(target="user")`

### Eval-004 (情境经验 → Experience)
- **输入**: "今天发现用 web_extract 获取百度百科内容比直接搜索更准确"
- **预期**: 情境经验，深度浅，需验证 → L2 Experience 暂存
- **检查**: 写入 experiences/active/ 并更新 index

### Eval-005 (Skill 重复检测 → Curator)
- **输入**: "学习一下知识路由的最佳实践，创建一个新 skill"
- **预期**: 先 skills_list 检查已有类似 skill
- **检查**: 不直接 create，先检查 curator

### Eval-006 (Memory 满 → Consolidate)
- **输入**: "再记一条：发现 curator 在 30 天后将技能标记为 stale"
- **预期**: 检查容量，如 >80% 先 consolidate
- **检查**: 先 consolidate 再添加

### Eval-007 (核心概念 → L3 Brain) ⭐ 新增
- **输入**: "Bounded Autonomy 是 Karpathy 提出的约束驱动 Agent 设计原则"
- **预期**: 程序知识，深度深，核心概念 → L3 Brain/concepts/
- **检查**: 写入 brain/wiki/concepts/ + 更新 index.md + 追加 log.md

### Eval-008 (实体档案 → L3 Brain) ⭐ 新增
- **输入**: "Andrej Karpathy 是前 OpenAI 研究员，提出 Bounded Autonomy"
- **预期**: 命题知识，实体类型 → L3 Brain/entities/
- **检查**: 写入 brain/wiki/entities/ + 建立 [[交叉引用]]

### Eval-009 (深度判断 → L2 vs L3) ⭐ 新增
- **输入**: "PDF 字体回退问题的解决方案：先检查 WQY 字体存在性，再 fallback 到系统字体"
- **预期**: 程序知识，深度浅（具体技巧）→ L2 Experience
- **检查**: 不写入 L3 Brain

### Eval-010 (双存：L1 + L3) ⭐ 新增
- **输入**: "Bounded Autonomy 的七大约束：固定时间盒、单一指标..."
- **预期**: 既有核心概念（L3 Brain/concepts/）又有可执行规范（L1 Skill）
- **检查**: 同时更新 brain 和（如适用）SOUL.md 中的约束体系

---

## Hermes v0.12.0 + 三层知识库 适配清单

| Hermes 特性 | 在路由中的角色 | 操作 |
|:-----------|:-------------|:-----|
| **Curator** | 避免重复创建 skill | 创建 skill 前用 `skills_list` 检查 |
| **SRA** | 上下文感知 | 参考 SRA 推荐决定路由方向 |
| **Memory (2200 chars)** | 容量管理 | >80% 时先 consolidate 再添加 |
| **Skills Hub** | 安装已有 skill | 如需新功能，先搜索 hub |
| **experiences/** | L2 经验存储 | 复用频率低/置信度低 → 先存 experience |
| **L3 Brain** ⭐ | 实体级知识存储 | 深度深/抽象化 → 走 brain 流程 |
| **knowledge-ingest.py** 🆕 | **统一执行入口** | 所有 L2/L3 沉淀走此脚本，取代手动写入 |
| **--auto-detect** 🆕 | **自动扫描** | 学习完成/Review 触发后扫描未处理知识 |
| **KNOWLEDGE_INDEX.md** ⭐ | 跨层索引 | 写入 brain 后检查是否需要更新 |
| **AGENTS.md (brain/)** ⭐ | L3 操作手册 | 页面类型/模板遵循 schema 定义 |

---

## 自动执行引擎 — knowledge-ingest.py

> **v3.2 升级：执行引擎已整合到 Pipeline 集成图 + 执行清单，本章节作为快速入口。**

`knowledge-routing` 的决策树告诉你 **存到哪里**，`knowledge-ingest.py` 负责 **统一执行**：

```
决策树回答: → 应该存到 L2 Experiences
执行引擎:   → python3 ~/.hermes/scripts/knowledge-ingest.py --type experience ...
              → 自动：文件创建 + 索引更新 + KNOWLEDGE_INDEX 增量
```

### 快速入口

| 需要 | 跳到 |
|:----|:-----|
| 完整 CLI 参数 & 模式 | ↪ `references/execution-engine.md` |
| 路由→执行 一键流程 | ↪ **执行清单 步骤 9-10**（上方） |
| 端到端管线图 | ↪ **Pipeline 集成** 章节 |
| 自动检测未处理知识 | ↪ `--auto-detect` 模式（执行清单步骤 9） |
| **🆕 升级后验证流程** | ↪ `references/upgrade-verification.md` |

---

## Red Flags（更新版）

- ❌ **五缺一**：知识不只 Memory/User/Experience/Skill — 还有 **L3 Brain**！
- ❌ **深度误判**：具体技巧塞进 Brain（引发 brain 膨胀）vs 核心概念塞进 Experience（难以检索）
- ❌ **跳过容量检查**：Memory 只有 2200 chars，写入前必须先检查
- ❌ **绕过 skill-creator**：创建/更新 Skill 必须加载 skill-creator
- ❌ **忽略 curator**：创建 skill 前不检查 curator 状态
- ❌ **跳过 brain 索引**：写入 brain 页面后不更新 index.md/log.md → 知识无法检索
- ❌ **长流程塞进 Memory**：操作 SOP 存 Memory → 耗尽容量且难以复用 → 走 Skill/Experience
- ❌ **琐碎事实写进 Skill**：一次性事件 → 建 Skill 造成库臃肿 → 走 Memory/Experience
- ❌ **🆕 手动写入**：有 `knowledge-ingest.py` 却手动写文件 → 丢失索引更新、交叉引用、KNOWLEDGE_INDEX 增量 → **L2/L3 沉淀必须走脚本**
- ❌ **🆕 跳过 auto-detect**：学习总结完成/Review 触发后不先跑 `--auto-detect` → 可能遗漏未处理知识 → 先扫描再判断
