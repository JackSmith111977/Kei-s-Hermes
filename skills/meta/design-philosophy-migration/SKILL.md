---
name: design-philosophy-migration
description: |
  跨项目设计哲学重构方法论。从研究目标项目的设计哲学 → 提炼可复用模式 → 应用到自己的项目中。
  当需要从优秀项目中学习设计模式、并同构到自己的项目时使用此 skill。
version: 1.0.0
triggers:
  - 设计哲学
  - 跨项目
  - 知识迁移
  - 设计重构
  - 借鉴
  - 参考
  - 学习其设计
  - 项目重构
  - 哲学迁移
  - 设计模式迁移
  - 架构重构
  - 借鉴设计
  - 学一下
  - 学学它的
metadata:
  hermes:
    tags:
      - cross-project
      - design-philosophy
      - knowledge-transfer
      - refactoring
      - methodology
    category: meta
    skill_type: methodology
    design_pattern: pipeline
---

# 跨项目设计哲学重构方法论（Design Philosophy Migration）

> **核心思想**：从优秀项目中提取"为什么好"而不是"做了什么"，再将"为什么"同构到自己的项目。
>
> 这不只是一次代码迁移，而是一次**世界观对齐**（Worldview Alignment）。

---

## 一、适用场景

| 场景 | 原项目 | 目标项目 | 示例 |
|------|--------|----------|------|
| 功能相似但体验不同 | web-access（一键安装成功） | SRA（AI 无法一次安装） | boku 刚才做的工作 |
| 架构相似但维度不同 | web-access（浏览器自动化） | Hermes（技能引擎） | 代理模式、中间件架构 |
| 设计理念不同 | web-access（哲学驱动） | SRA（命令驱动） | README/SKILL.md 设计 |

**不适用场景**：
- ❌ 单纯复制代码（没有理解"为什么"）
- ❌ 功能完全不同（如数据库 vs 前端框架）
- ❌ 一次性小改动（不需要完整方法论）

---

## 二、工作流（6 步法）

### STEP 0: 前置准备

1. 加载本 skill：`skill_view design-philosophy-migration`
2. 如果涉及学习/研究 → 走 learning-workflow：`skill_view learning-workflow`
3. 如果涉及代码开发 → 加载开发相关 skill：`skill_view git-advanced-ops` + `skill_view github-project-ops`

---

### STEP 1: 全量文件扫描

扫描目标项目的完整仓库，了解"它有什么"。

**方法**：使用 Tavily Crawl 或 GitHub API

**Tavily 方式（推荐）**：使用 `mcp_tavily_tavily_crawl` 爬取 GitHub 仓库，获取完整文件树

**GitHub API 方式（备选）**：使用终端和 Python 解析 JSON，获取仓库文件结构

**输出物**：仓库文件清单

**关键洞察**：关注**文件数量和结构**，而不是单个文件内容。
- web-access 只有 10 个文件 → 极简 = 极低认知负荷
- SRA 有 40+ 个文件 → 信息过载

---

### STEP 2: 关键文件深度提取

逐一分析核心文件，按优先级排序：

| 优先级 | 文件 | 分析要点 |
|--------|------|----------|
| 🔴 **高** | README.md | 行数、安装方式数量、是否包含预期输出 |
| 🔴 **高** | SKILL.md | 有无哲学层、前置检查机制、错误处理 |
| 🔴 **高** | check-deps / install | 环境自检、自动恢复、跨平台性 |
| 🟡 **中** | 配置文件 | 配置可脚本化程度 |
| 🟡 **中** | scripts/ | 各脚本职责、错误处理 |
| 🟢 **低** | .github/ | CI/CD、Issue 模板 |

**提取方法**（因网络超时等问题，使用多策略轮换）：

1. **Tavily Extract**：使用 `mcp_tavily_tavily_extract` 提取原始文件内容
2. **Tavily Crawl**：使用 `mcp_tavily_tavily_crawl` 完整爬取仓库
3. **raw.githubusercontent.com**：直接获取原始文件

**输出物**：`reading_notes.md`

---

### STEP 3: 设计哲学提炼

从文件内容中抽象出**设计哲学**，而非具体操作步骤。

**提炼框架**——问自己 5 个问题：

1. 这个项目解决了什么"元问题"？（不只是功能上的，而是设计上的）
2. 什么机制让它对 AI 更友好？（自检？哲学层？多路径？）
3. 它在哪些地方做了"取舍"？（复杂 vs 简单？灵活 vs 确定？）
4. 如果我只有一句话描述它的设计哲学，是什么？
5. 哪些是它做对了但我没做的？

**哲学模板**：

```
## 设计哲学 N：[短语]

### 原则
[一句话描述核心原则]

### 具体体现
- [在该项目的文件/代码中的体现]
- [另一个体现]

### 为什么重要
[为什么不这样做就会出问题]

### 可复用模式
[如何应用到自己的项目中]
```

**输出物**：`extracted_knowledge.md`（6~8 条设计哲学）

---

### STEP 4: 对比分析（差距分析）

用表格对比「目标项目（标杆）」vs「自己的项目」：

| 设计维度 | ✅ 目标项目（标杆） | ❌ 自己项目（改进前） | 差距等级 |
|----------|-------------------|---------------------|----------|
| README 行数 | 174 行 | 443 行 | 🔴 严重 |
| 环境自检 | check-deps.mjs | 无 | 🔴 严重 |
| SKILL.md 范式 | 哲学驱动 | 命令列表 | 🟡 中等 |

**排序**：按差距等级（🔴 高 → 🟡 中 → 🟢 低）

---

### STEP 5: 实施改进（Git 分支开发）

按差距等级从高到低逐项改进：

1. **创建独立分支**
   - 使用 `terminal` 执行 `git checkout -b feat/design-philosophy-overhaul`

2. **设置 Git 用户信息**
   - 使用 `terminal` 设置 `user.name` 和 `user.email`

3. **各改进项单独提交**
   - 提交信息格式：`feat: [改进项名称] — 依据 [具体设计哲学]`

**改进优先级**：

| 优先级 | 改进项 | 参考 |
|--------|--------|------|
| 🔴 1 | 创建 SKILL.md（哲学层） | 目标项目的 SKILL.md |
| 🔴 2 | 重写 README.md（精简 + 预期输出） | 目标项目的 README.md |
| 🔴 3 | 创建环境自检脚本（check.*） | check-deps.mjs |
| 🟡 4 | 多路径安装 / 一键安装 | README 安装部分 |
| 🟡 5 | 插件市场配置 | .claude-plugin/ |
| 🟢 6 | CI/CD / Issue 模板 | .github/ |

**每个文件改动的核心原则**：

- **README.md**：入口文件，只放"够用"的信息。详细内容放在 SKILL.md 和 docs/ 中。
- **SKILL.md**：世界观文件，放哲学层 + 技术事实。告诉 AI "为什么"而不是"怎么做"。
- **check-deps**：AI 的眼睛，让 AI 永远知道"当前状态是什么"和"下一步该做什么"。
- **install.sh**：多路径降级策略，一条不行就试下一条。

---

### STEP 6: 提交与验证

1. **查看变更**：`git status` / `git diff --stat`
2. **提交所有更改**：`git add -A && git commit -m "feat: 基于 [目标项目] 设计哲学重构 [自己项目]"`
3. **推送分支**：`git push -u origin feat/design-philosophy-overhaul`
4. **创建 PR（可选）**

---

## 三、检查清单

- [ ] STEP 1: 全量文件扫描完成
- [ ] STEP 2: 关键文件深度提取完成（考虑网络故障备选策略）
- [ ] STEP 3: 至少提炼出 6 条设计哲学
- [ ] STEP 4: 对比分析表格完成，差距按等级排序
- [ ] STEP 5: 创建了独立开发分支
- [ ] STEP 5: 按优先级从高到低逐项改进
- [ ] STEP 5: 每个文件改动遵循核心原则
- [ ] STEP 6: 提交信息包含"依据"和"改动"两部分
- [ ] STEP 6: 分支已推送到远程

---

## 四、🚩 Red Flags

1. **❌ 跳过 STEP 1 和 STEP 2 直接改代码**：必须先理解目标项目的设计哲学，不能靠猜测
2. **❌ 复制代码而不是复制哲学**：web-access 的 check-deps.mjs 是用 Node.js 写的，但如果自己的项目是 Python，应该用 Python 重新实现
3. **❌ 只改一个文件**：改进应该覆盖 README + SKILL.md + 安装脚本 + 自检脚本，形成完整闭环
4. **❌ 不改 SKILL.md**：SKILL.md 是 AI 的"世界观"，如果项目原本没有 SKILL.md，这恰恰是最关键的问题
5. **❌ 信息过载的 README**：README 是入口不是文档，443 行不如 174 行有用
6. **❌ 网络故障时只试一种提取策略**：多策略轮换，异常时切换方案

---

## 五、评估用例 (Eval Cases)

### Eval-001（标准流程）
- **输入**："学习一下 web-access 的设计哲学，然后改进 SRA 项目"
- **预期**：
  - STEP 1: 扫描 web-access 仓库（10 个文件）
  - STEP 2: 提取 README/SKILL.md/check-deps
  - STEP 3: 提炼 6+ 条设计哲学
  - STEP 4: 对比分析表格
  - STEP 5: 创建分支、逐项 commit
  - STEP 6: 推送分支

### Eval-002（网络故障恢复）
- **输入**："raw.githubusercontent.com 超时了继续"
- **预期**：
  - 切换到 Tavily extract 或其他方式
  - 不因网络问题放弃关键文件提取

### Eval-003（防呆 - 跳过分析直接改）
- **输入**："别说那么多，直接改 SRA 的 README"
- **预期**：
  - 🛑 拦截并提示：必须先走 STEP 1-4 完成分析，不能跳过
