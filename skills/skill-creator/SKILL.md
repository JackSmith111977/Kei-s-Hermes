---
name: skill-creator
description: >
  创建、优化、评估 Skill 的完整工作流。支持 9 种 Skill 类型（库API/产品验证/数据分析/代码生成/文档生成/代码审查/部署/团队规范/调研整理），
  5 种设计模式（Tool Wrapper/Generator/Reviewer/Inversion/Pipeline），9 阶段工作流，以及基于 Eval 的自动化评估体系。
  当用户需要创建新 Skill、优化已有 Skill、评估 Skill 质量、或了解 Skill 设计模式时触发。
  触发词：创建skill、新建技能、写skill、skill-creator、优化skill、评估skill、skill设计、skill模板。
allowed-tools:
  - terminal
  - read_file
  - write_file
  - patch
  - search_files
  - skill_manage
  - skills_list
  - skill_view
---

# Skill Creator · Skill 创建与评估工具

## 技能概述

创建高质量 Skill 的完整工作流，包含 9 种类型模板、5 种设计模式、9 阶段创作流程、以及基于 Eval 的自动化评估体系。

**核心工作流（9 阶段）：**

```
Stage 1: 需求澄清 → Stage 2: 用例定义 → Stage 3: 选择类型+模式 → Stage 4: 生成草稿
→ Stage 5: 用户确认 → Stage 6: 写入文件 → Stage 7: Review 检查
→ Stage 8: 测试建议 → Stage 9: 评估迭代
```

## 9 种 Skill 类型

| # | 类型 | 适用场景 | 设计模式 |
|---|------|----------|----------|
| 1 | **库和 API 参考** | 内部库、CLI、SDK 使用指南 | Tool Wrapper |
| 2 | **产品验证** | 测试流程、断言验证 | Pipeline + Reviewer |
| 3 | **数据获取与分析** | 数据查询、报表生成 | Generator |
| 4 | **代码生成** | 规格转代码、设计稿转前端 | Generator + Pipeline |
| 5 | **文档生成** | PR 描述、API 文档、发布说明 | Generator + Inversion |
| 6 | **代码审查** | 安全检查、性能分析、代码质量 | Reviewer + Tool Wrapper |
| 7 | **部署流程** | 部署、发布、回滚 | Pipeline + Reviewer |
| 8 | **团队规范** | 编码风格、提交规范 | Tool Wrapper |
| 9 | **调研整理** | 技术调研、知识整理 | Inversion + Generator |

详见 `references/skill-types.md`。

## 5 种设计模式

| 模式 | 核心思想 | 适用场景 |
|------|----------|----------|
| **Tool Wrapper** | 将工具/库的最佳实践封装为可复用指令 | API 参考、团队规范 |
| **Generator** | 根据输入规格生成结构化输出 | 代码生成、文档生成 |
| **Reviewer** | 对照标准检查并评分 | 代码审查、产品验证 |
| **Inversion** | 从结果反推执行步骤（逆向工作流） | 调研整理、问题诊断 |
| **Pipeline** | 多步骤顺序执行 + 进度追踪 | 部署流程、产品验证 |

详见 `references/google-design-patterns.md`。

## Stage 1: 需求澄清

### 5 个关键问题

| 问题 | 目的 | 示例选项 |
|------|------|----------|
| 1. 主要用途 | 确定 Skill 类型 | 代码审查、文档生成 |
| 2. 触发方式 | 配置调用方式 | 显式/隐式/两者 |
| 3. 使用者 | 确定作用域 | 个人/团队 |
| 4. 外部工具 | 确定权限需求 | 脚本执行、API 调用 |
| 5. 输出格式 | 确定交付物 | Markdown、代码、JSON |

### 类型推荐逻辑

```
if 用途 contains "内部库" or "API": → 库和 API 参考
elif 用途 contains "测试" or "验证": → 产品验证
elif 用途 contains "查询" or "报表": → 数据获取与分析
elif 用途 contains "生成代码": → 代码生成
elif 用途 contains "文档": → 文档生成
elif 用途 contains "审查" or "检查": → 代码审查
elif 用途 contains "部署" or "发布": → 部署流程
elif 用途 contains "规范" or "风格": → 团队规范
elif 用途 contains "调研" or "整理": → 调研整理
```

## Stage 2: 用例定义

### 用例格式

```markdown
**用例名称：** [简短描述]
- **触发条件：** 用户说什么/做什么
- **执行步骤：** 1 → 2 → 3
- **预期结果：** 输出格式和内容
```

**数量要求：** 至少 2-3 个具体用例

### 触发配置

**显式命令：**
- 格式：`/skill-name`
- 使用英文连字符
- 示例：`/code-review`、`/research`

**隐式触发词：**
- 数量：3-5 个中文触发词
- 包含同义词、常见说法
- 示例：`[调研，研究，整理资料，帮我调研]`

## Stage 3: 选择类型 + 设计模式

根据 Stage 1 的结果选择类型和模式组合：

| 推荐类型 | 推荐模式 | 模板文件 |
|----------|----------|----------|
| 库和 API 参考 | Tool Wrapper | `templates/library-reference.md` |
| 产品验证 | Pipeline + Reviewer | `templates/product-verification.md` |
| 数据获取与分析 | Generator | `templates/data-analysis.md` |
| 代码生成 | Generator + Pipeline | `templates/code-generation.md` |
| 文档生成 | Generator + Inversion | `templates/doc-generation.md` |
| 代码审查 | Reviewer + Tool Wrapper | `templates/code-review.md` |
| 部署流程 | Pipeline + Reviewer | `templates/deployment.md` |
| 团队规范 | Tool Wrapper | `templates/team-norms.md` |
| 调研整理 | Inversion + Generator | `templates/research.md` |

## Stage 4: 生成草稿

### 4.1 加载模板

从 `templates/` 目录加载对应模板文件。

### 4.2 填充内容

将 Stage 2 收集的信息填入模板：
- 用例描述 → 示例章节
- 触发方式 → Frontmatter
- 文件结构 → 资源索引

### 4.3 输出草稿预览

以变更摘要格式输出，等待用户确认。

## Stage 5: 用户确认

展示草稿变更摘要，等待用户确认或修改：

```markdown
## Skill 草稿预览（变更摘要）
### 变更项
- **Frontmatter:** 新增/修改的字段
- **核心原则:** 新增的原则
- **工作流程:** 修改的步骤
- **输出规范:** 更新的内容
```

用户确认后进入 Stage 6。如需修改，返回 Stage 4 重新生成。

## Stage 6: 写入文件

### 6.1 确认输出位置

- **项目级：** `.claude/skills/[skill-name]/`
- **全局级：** `~/.hermes/skills/[skill-name]/`（跨项目使用）

### 6.2 创建目录结构

使用脚本 `scripts/create-skill-dir.sh` 创建标准目录结构：

```bash
mkdir -p ~/.hermes/skills/[skill-name]/{templates,references,scripts,checklists}
```

### 6.3 写入文件

1. SKILL.md（主文档，必需）
2. 模板文件（如适用）
3. 参考文档（如适用）
4. 检查清单（如适用）
5. 脚本文件（如适用）

## Stage 7: Review 检查

加载 `checklists/skill-creation-check.md` 逐项检查：

**必须项（不满足不能发布）：**
- [ ] YAML Frontmatter 格式正确
- [ ] description 清晰具体（100 词内）
- [ ] 包含可执行的工作流程
- [ ] 配置了显式触发命令
- [ ] 配置了隐式触发词（3-5 个）
- [ ] 没有陈述显而易见的内容
- [ ] 用户已确认草稿

**安全检查：**
- [ ] 无敏感权限（不读取 .env 等）
- [ ] 脚本执行前需用户确认
- [ ] 外部 API 验证 SSL

## Stage 8: 测试建议

生成 3 类测试用例：

```markdown
### 测试 1：显式触发
/skill-name [测试输入]
**预期：** Skill 正常响应并执行流程

### 测试 2：隐式触发
[触发词 1] [测试输入]
**预期：** 自动识别并触发 Skill

### 测试 3：边界情况
[边界场景描述]
**预期：** 正确处理边界情况
```

## Stage 9: 评估迭代（可选）

基于 `references/eval-iteration-loop.md` 执行完整评估循环：

### A. 定义测试用例

创建 `evals/evals.json`：

```json
{
  "skill_name": "my-skill",
  "evals": [{
    "id": "eval-001",
    "prompt": "[触发词] [测试内容]",
    "expected_output": "[预期输出描述]",
    "expectations": [
      "期望 1 — 具体可验证",
      "期望 2 — 具体可验证"
    ]
  }]
}
```

### B. 执行测试

对每个测试用例执行并记录转录和输出。

### C. 评分

使用 `references/grader-agent.md` 的评分流程，输出 `grading.json`。

### D. 改进

根据失败期望改进 SKILL.md：
- 指令不清 → 重写具体指令，加入 DO NOT
- 步骤缺失 → 补充缺失步骤
- 触发不准 → 优化 description 或 triggers

### E. 迭代

重复 B → C → D，直到通过率 ≥ 80%。

## 修改已有 Skill（M1-M4）

### M1：读取
读取当前 SKILL.md 内容

### M2：确认
询问用户需要修改的内容

### M3：生成预览
输出 Diff 格式变更摘要

### M4：写入
更新文件，记录版本变更

检查清单见 `checklists/skill-modify-check.md`。

## 优化已有 Skill（O1-O4）

### O1：读取
读取当前 Skill 文件

### O2：分析
- 主文档行数（> 500 行需精简）
- 重复内容
- 可移至 references/ 的内容
- 目录结构符合性

### O3：生成方案
输出优化计划

### O4：执行
按确认的方案执行优化

## 目录结构

```
skill-creator/
├── SKILL.md                          # 主文件（本文件）
├── references/                       # 参考文档
│   ├── execution-guide.md            # 执行指南（详细步骤）
│   ├── google-design-patterns.md     # 5种设计模式详解
│   ├── skill-types.md                # 9种Skill类型详解
│   ├── eval-schemas.md               # 评估体系JSON Schema
│   ├── eval-iteration-loop.md        # Eval迭代循环
│   ├── grader-agent.md               # 评分器Agent
│   ├── pipeline-progress-format.md   # Pipeline进度追踪格式
│   └── workflow.md                   # 6阶段工作流详解
├── templates/                        # Skill模板
│   ├── library-reference.md          # 类型1: 库和API参考
│   ├── product-verification.md       # 类型2: 产品验证
│   ├── data-analysis.md              # 类型3: 数据获取与分析
│   ├── code-generation.md            # 类型4: 代码生成
│   ├── doc-generation.md             # 类型5: 文档生成
│   ├── code-review.md                # 类型6: 代码审查
│   ├── deployment.md                 # 类型7: 部署流程
│   ├── team-norms.md                 # 类型8: 团队规范
│   ├── research.md                   # 类型9: 调研整理
│   └── evals-template.json           # 评估模板
├── checklists/                       # 检查清单
│   ├── creation-checklist.md         # 创建前检查
│   ├── skill-creation-check.md       # 创建后检查
│   └── skill-modify-check.md         # 修改检查
├── examples/                         # 使用示例
│   └── usage-examples.md             # 5个典型使用场景
└── scripts/                          # 工具脚本
    ├── create-skill-dir.sh           # 创建目录结构
    └── validate-skill.sh             # 验证Skill完整性
```

## 快速参考

| 任务 | 参考文档 |
|------|----------|
| 创建新 Skill | Stage 1-9 + `references/workflow.md` |
| 了解设计模式 | `references/google-design-patterns.md` |
| 了解 Skill 类型 | `references/skill-types.md` |
| 设置评估体系 | `references/eval-iteration-loop.md` |
| 评分标准 | `references/grader-agent.md` |
| Pipeline 模式 | `references/pipeline-progress-format.md` |
| 执行详细步骤 | `references/execution-guide.md` |
| 创建检查 | `checklists/creation-checklist.md` |
| 修改检查 | `checklists/skill-modify-check.md` |
| 使用示例 | `examples/usage-examples.md` |
| 验证 Skill | `scripts/validate-skill.sh` |

*Skill Creator v10.1.0 | 参考: github.com/JackSmith111977/Knowledge-Base/.claude/skills/skill-creator*
