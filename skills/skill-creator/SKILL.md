---
name: skill-creator
description: "创建、优化、评估 Skill 的完整工作流。支持从实战任务中提取知识、从学习笔记转化 Skill。内置 5 种设计模式，9 阶段创作流程（含快速更新通道），引用依赖检查，以及 skill-manage 联动拦截。"
version: 5.0.0
triggers:
- skill
- 创建技能
- 优化技能
- 模板
- 技能升级
- 依赖检查
- skill-manage 联动
- 质量评分
- 质量检查
- SQS
- 技能质量
- 技能审计
- 技能生命周期
- 技能退役
- skill audit
- 全量审计
- 技能健康
- quality gate
- 质量门禁
allowed-tools:
- terminal
- read_file
- write_file
- patch
- search_files
- skill_manage
- skills_list
- skill_view
metadata:
  hermes:
    tags:
    - skill-creation
    - evaluation
    - knowledge-extraction
    - versioning
    - dependency-tracking
    category: meta
    skill_type: generator
    design_pattern: pipeline
---
# Skill Creator · Skill 创建与评估工具 v4.0

> **核心理念**：Skill 不仅仅是文档，是**可执行的代码级逻辑**。创建 Skill 就像写软件：需要设计模式、版本控制、依赖管理、测试评估。
> **v4.0 新增**：Skill 间引用依赖检查机制 + skill-manage 联动拦截。

## 技能概述

提供 5 种核心工作流：
1.  **新建 (Creation)**：从零构建一个 Skill，支持 9 种类型。
2.  **提取 (Extraction)**：从一次成功的任务对话中提取通用模式，沉淀为 Skill。
3.  **转化 (Transformation)**：将学习笔记、调研结果转化为标准化的 Skill。
4.  **优化 (Optimization)**：对现有 Skill 进行瘦身、精简、结构调整。
5.  **评估 (Evaluation)**：通过 Eval 用例验证 Skill 的有效性。

## 〇、🚨 铁律拦截 (Pre-flight Gate)

**在任何 Skill 操作前，必须通过此检查门！**

> **v4.2 更新**: pre_flight.py v2.0 现在会自动检测技能操作（识别 "创建/编辑/更新/删除 skill" 等关键词），自动运行 `dependency-scan.py --target <skill>` 定向扫描，并提示加载 skill-creator。但仍需 agent 手动执行 `skill_view(name='skill-creator')` 加载完整流程。

```
[准备调用 skill_manage] 
   ↓
[检查 0] 是否为知识沉淀任务？ → 是 → 🛑 检查是否经过 learning-workflow 的搜索阶段！
   ├─ 是（已有 raw_search_results.md）→ ✅ 放行
   └─ 否 → 🛑 拦截！报错：需要先过 learning-workflow
   ↓
[检查 1] 是否为简单更新（如修复错别字、优化描述）？
   ├─ 是 → 走快速更新通道（跳过完整 9 阶段）
   └─ 否 → 继续
[检查 2] 是否已加载 skill-creator？ → 否 → 🛑 强制加载！
   ↓ 是
[检查 3] 是否已执行依赖检查？ → 否 → 🛑 运行 dependency-scan！
   ↓ 是
[检查 4] 是否通过质量清单？ → 否 → 🛑 补全缺失项！
   ↓ 是
[✅ 放行] 允许调用 skill_manage
```

### 快速更新通道（v4.1 新增）

适用于：错别字修复、描述优化、触发词添加、简单版本号更新等小改动

**无需经过：**
- ❌ 9 阶段完整流程
- ❌ learning-workflow 前置搜索检查

**必须经过：**
- ✅ 依赖检查（检查是否影响其他 skill）
- ✅ 质量清单检查（YAML frontmatter 完整性）
- ✅ 修改后通知用户

### 完整创建通道（标准）

适用于：全新 skill 创建、重大重构、知识沉淀

**必须经过：**
- ✅ learning-workflow 前置搜索检查（知识沉淀类）
- ✅ 9 阶段完整流程
- ✅ 依赖检查 + 质量清单
- ✅ 验证测试（子代理 QA）

## 一、5 种设计模式 (Design Patterns)

| 模式 | 核心思想 | 适用场景 |
|:---|:---|:---|
| **Tool Wrapper** | 将工具/库的最佳实践封装为指令 | API 参考、团队规范、脚本调用 |
| **Generator** | 根据输入规格生成结构化输出 | 代码生成、文档生成、配置初始化 |
| **Reviewer** | 对照标准检查并评分 | 代码审查、产品验证、安全检查 |
| **Inversion** | 从结果反推执行步骤 | 调研整理、问题诊断、逆向工程 |
| **Pipeline** | 多步骤顺序执行 + 进度追踪 | 部署流程、复杂分析、工作流 |

## 二、9 种 Skill 类型

1.  **库/API 参考** (Tool Wrapper)
2.  **产品验证** (Pipeline + Reviewer)
3.  **数据分析** (Generator)
4.  **代码生成** (Generator + Pipeline)
5.  **文档生成** (Generator + Inversion)
6.  **代码审查** (Reviewer + Tool Wrapper)
7.  **部署流程** (Pipeline + Reviewer)
8.  **团队规范** (Tool Wrapper)
9.  **调研整理** (Inversion + Generator)

## 三、核心工作流

### 工作流 0: pre_flight 自动触发（v4.2 新增）

日常开发中无需手动想起 skill-creator。运行 `pre_flight.py` 后自动检测：

```bash
python3 ~/.hermes/scripts/pre_flight.py "更新pdf-layout skill的字体配置"

# Gate 3 自动输出:
#   🎯 检测到技能操作: Skill CRUD
#   📌 必须加载 skill-creator:
#      skill_view(name='skill-creator')
#   📌 自动运行定向依赖扫描...
#      🎯 定向扫描: pdf-layout
#      📦 pdf-layout (v2.0.0)
#        → 被 2 个 skill 引用: pdf-render-comparison, vision-qc-patterns
```

**流程链**:
```
主人说"更新 skill X"
  ↓
pre_flight.py 检测到技能操作
  ├── 自动跑 dependency-scan --target X
  └── 提示加载 skill-creator
      ↓
skill_view(name='skill-creator')  ← agent 手动执行
  ↓
本 skill 的 9 阶段流程（或快速更新通道）
  ↓
dependency-scan 确认无断裂引用
  ↓
skill_manage 执行操作
```

**关键点**: pre_flight 负责**检测+提醒**，skill-creator 负责**流程+质量**。两者配合形成完整的 Skill 操作管道。

### 工作流 A: 从零创建 (9 阶段)
```
S1: 需求澄清 (用途/触发/使用者) → S2: 用例定义 (至少 3 个) 
→ S3: 类型+模式选择 → S4: 生成草稿 
→ S5: 用户确认 → S6: 写入文件 → S7: Review 检查 
→ S8: 测试建议 → S9: Eval 评估
```

### 工作流 B: 学习沉淀/知识提取 (Learning Bridge)
**触发场景**：用户说"把刚才的经验沉淀为 skill"或 learning skill 完成学习后。
```
Step 1: 提取核心模式 (从对话/笔记中找出重复使用的逻辑)
Step 2: 定义输入输出 (Prompt -> Expected Output)
Step 3: 确定依赖 (是否需要终端、脚本、特定环境)
Step 4: 生成 SKILL.md (遵循标准模板)
Step 5: 存入对应分类目录 (references/scripts/checklists)
Step 6: 注册到 skill-creator 索引
```

### 工作流 C: 优化已有 Skill
1.  **读取**：当前 SKILL.md 内容。
2.  **诊断**：行数过多 (>300 行)、缺乏触发词、缺少 Example、指令模糊。
3.  **瘦身**：将长篇大论移至 `references/`，主文档只保留核心指令。
4.  **增强**：补充 YAML Triggers 和 Eval Cases。
5.  **写入**：使用 `patch` 或 `write_file` 更新。

### 工作流 D: 🔗 依赖检查与引用管理 (v4.0 新增)
**触发场景**：修改/删除 Skill 前、或用户要求"检查依赖关系"时。
```
Step 1: 扫描全量 Skill 的 YAML Frontmatter
Step 2: 构建依赖图谱 (depends_on / referenced_by)
Step 3: 检查引用链是否完整
   - 若目标 Skill 被其他 Skill 引用 → 提示同步更新
   - 若目标 Skill 引用了不存在的 Skill → 报错警告
Step 4: 生成依赖报告 (Markdown 表格)
Step 5: 用户确认后执行修改/删除
```

**YAML 依赖字段规范**：
```yaml
# 在 SKILL.md 的 frontmatter 中添加
depends_on:
  - web-access
  - pdf-layout
referenced_by:
  - doc-design
  - quality-assurance
```

## 四、质量标准与检查清单 (Quality Checklist)

在输出 Skill 前，boku 必须自测以下项目：

- [ ] **YAML Frontmatter**：包含 `name`, `version`, `description`, `triggers`。
- [ ] **显式 Triggers**：**必须**在 YAML 中包含 `triggers` 列表（3-5 个关键词），不能只写在正文。
- [ ] **具体指令**：避免模糊词汇（如"适当处理"），使用精确指令（如"若返回 404 则执行 X"）。
- [ ] **防呆设计**：包含 **Red Flags** 章节，列出常见错误。
- [ ] **目录结构**：`SKILL.md` + `references/` + `scripts/` + `checklists/`。
- [ ] **渐进式披露**：大体积引用文档放入 `references/`，SKILL.md 仅做路由。
- [ ] **依赖声明**：若依赖其他 Skill，必须在 YAML 中声明 `depends_on`。
- [ ] **联动拦截**：调用 `skill_manage` 前，必须已通过本检查清单。

## 五、评估体系 (Evaluation)

### 定义成功 (Definition of Done)
对于每个 Skill，必须定义：
```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "eval-001",
      "prompt": "[触发词] [测试输入]",
      "expected_checks": ["检查 1: 是否调用了正确工具", "检查 2: 输出格式是否正确"]
    }
  ]
}
```

### 评估步骤
1.  **人工验证**：boku 模拟用户触发该 Skill，检查是否能成功执行。
2.  **边界测试**：输入错误参数或边缘情况，验证 Skill 是否能优雅报错。
3.  **依赖测试**：验证 `depends_on` 中声明的 Skill 是否真实存在且可用。

## 六、目录结构规范

```
~/.hermes/skills/[skill-name]/
├── SKILL.md                          # 主文档 (必须 < 300 行)
├── references/                       # 详细参考文档
│   └── api-details.md
├── scripts/                          # 自动化脚本
│   └── dependency-scan.py            # v4.0: 依赖扫描脚本
└── checklists/                       # 执行清单
    └── pre-flight.md
```

## 七、版本管理

- **主版本号 (X.0.0)**：破坏性变更（改变了 Skill 类型或核心逻辑）。
- **次版本号 (0.X.0)**：增加新功能、新用例或新的 References。
- **修订号 (0.0.X)**：修复错别字、优化指令清晰度、瘦身。

## 八、🚩 Red Flags (常见错误)

1. **绕过 skill-creator 直接调用 skill_manage**：这是最严重的违规！必须拦截。
2. **删除被引用的 Skill 不提示**：会导致其他 Skill 的引用链断裂，必须提前扫描并警告。
3. **YAML 中 triggers 只写在正文**：加载器无法识别，必须写在 frontmatter 中。
4. **不声明依赖关系**：导致 Skill 升级时影响范围不可控。
5. **把长流程塞进 Memory**：Memory 容量有限，操作 SOP 必须存入 Skill。
6. **触发词过于书面化/学术化**：如果 Trigger 只写"经验沉淀"而没写"总结/复盘/踩坑"，用户在自然对话中就**无法自动触发**该 Skill！**必须穷举口语化表达**。
7. **忽略了 pre_flight 的检测输出**：pre_flight v2.0 Gate 3 会检测技能操作并提示加载 skill-creator。看到提示后必须执行 `skill_view(name='skill-creator')`，不能跳过该步骤直接操作。

## 九、评估用例 (Eval Cases)

1. **Eval-001 (依赖检查)**：
   - *输入*："修改 pdf-layout 的字体配置"
   - *预期*：自动扫描哪些 Skill 引用了 pdf-layout，提示同步更新 doc-design。
2. **Eval-002 (联动拦截)**：
   - *输入*：直接调用 `skill_manage(action='delete', name='old-skill')`
   - *预期*：拦截并提示"请先加载 skill-creator 执行依赖检查"。
3. **Eval-003 (引用断裂检测)**：
   - *输入*："删除 web-access skill"
   - *预期*：报错警告，因为多个 Skill 依赖 web-access，删除会导致连锁失败。
4. **Eval-004 (创建新 Skill)**：
   - *输入*："创建一个新的 API 参考 skill"
   - *预期*：走 9 阶段流程，生成标准 SKILL.md，询问依赖关系，写入文件。

---

## 十、Skill 质量生命周期体系 (Quality Lifecycle System)

> 本节定义了 skill-creator 在 skill 全生命周期中的角色——不仅是创建工具，更是**质量守门员**。

### 10.1 生命周期概览

```
                      ┌──────────────────────────┐
                      │   🔬 pre_flight v2.0      │
                      │   自动检测 skill 操作      │
                      │   ├─ SQS 质量评分          │
                      │   ├─ 依赖扫描              │
                      │   └─ 提醒加载 skill-creator │
                      └──────────┬───────────────┘
                                 │ 触发
                                 ▼
┌──────────────────────────────────────────────────────┐
│  skill-creator 全生命周期管理                          │
│                                                        │
│  创建 (CREATE) → 质量门禁 (QA) → 部署 (DEPLOY)         │
│     │               │              │                   │
│     │ 9 阶段流程    SQS >= 50    写入技能库           │
│     │ + 质量清单    SQS < 50     触发钩子             │
│     │ + 依赖扫描    返回改进                        │
│     │                                                  │
│  维护 (MAINTAIN) → 审计 (AUDIT) → 退役 (DEPRECATE)     │
│     │               │              │                   │
│     │ 更新内容      SQS 定期扫描   影响分析              │
│     │ 更新版本      新鲜度检查     通知引用者             │
│     │ 同步依赖      生命周期报告   标记退役               │
└──────────────────────────────────────────────────────────┘
```

### 10.2 质量门禁 (Quality Gate)

所有 skill 操作前必须通过的质量检查：

| 门禁 | 检查项 | 阻断条件 | 自动化程度 |
|:-----|:-------|:---------|:----------|
| **QSG-1** | SQS 质量分 >= 50 | < 50 分时禁止创建/部署 | ✅ pre_flight 自动 |
| **QSG-2** | 依赖无断裂引用 | 存在断裂引用时警告 | ✅ pre_flight 自动 |
| **QSG-3** | YAML frontmatter 完整 | 缺少 name/version/description | ✅ validate-skill.sh |
| **QSG-4** | triggers 列表 >= 3 | < 3 个 triggers 时警告 | 手册 质量清单 |
| **QSG-5** | 有 Red Flags 章节 | 缺失时建议补充 | 手册 质量清单 |

### 10.3 SQS 质量评分公式

Skill Quality Score (SQS) = 5 维度 x 20 分 = **100 分**

| 维度 | 权重 | 评分依据 | 工具 |
|:-----|:----:|:---------|:-----|
| S1 结构完整性 | 20 | YAML frontmatter 完整度、目录结构 | skill-quality-score.py |
| S2 内容准确性 | 20 | 代码示例、Red Flags、操作步骤 | skill-quality-score.py |
| S3 时效性 | 20 | 版本号、最后更新日期、创建日期 | skill-quality-score.py |
| S4 关联完整性 | 20 | depends_on、referenced_by、交叉引用 | skill-quality-score.py |
| S5 可发现性 | 20 | triggers 丰富度、标签、描述质量 | skill-quality-score.py |

**等级**:
- 优秀 (90-100): 可直接发布
- 良好 (70-89): 建议优化薄弱维度
- 需改进 (50-69): 必须改进后才能部署
- 不合格 (< 50): 禁止部署，需重建

### 10.4 生命周期状态管理

每个 skill 有 5 个生命周期状态：

| 状态 | 含义 | 转换条件 |
|:-----|:------|:---------|
| active | 活跃、可正常使用 | 默认状态 |
| under_review | 正在被审查/改进 | SQS < 50 或主人标记 |
| frozen | 暂时冻结，不主动推荐 | 依赖工具变更待适配 |
| deprecated | 已标记退役，仍可使用但警告 | 被替代或不再维护 |
| archived | 已归档，不再可用 | deprecated 超过 30 天 |

### 10.5 自动化管道

当主人说「创建/编辑/更新 skill」时，以下流程自动触发：

```
主人: "更新 pdf-layout skill"
  ↓
pre_flight v2.0:
  ├── Gate 1: 学习状态检查
  ├── Gate 2: SDD 门禁 (技能操作，跳过)
  └── Gate 3: 触发 skill-creator 管道
        ├── SQS 质量评分 -> 71.8/100
        ├── 定向依赖扫描 -> 被 2 个 skill 引用
        └── 提示: 必须加载 skill-creator
  ↓
boku:
  skill_view(name='skill-creator')     <- 强制加载
  检查质量清单                           <- 确保符合标准
  skill_manage(action='patch', ...)    <- 允许操作
```

### 10.6 相关脚本

| 脚本 | 位置 | 用途 |
|:-----|:------|:------|
| skill-quality-score.py | scripts/ | SQS 质量评分（单 skill / --audit 全量） |
| skill-lifecycle-audit.py | scripts/ | 生命周期审计 + deprecate/revive 管理 |
| dependency-scan.py | scripts/ | 依赖关系扫描（全量 / --target 定向） |
| pre_flight.py | ~/.hermes/scripts/ | 通用守门员（集成以上所有检查） |
