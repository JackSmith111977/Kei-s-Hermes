---
name: bmad-context-engineering
description: "BMAD 上下文工程与配置指南。详解 BMAD 如何通过文件系统、TOML 配置和 project-context.md 注入上下文。适用于配置新项目、定制 Agent 行为或调试上下文丢失问题。"
version: 1.0.0
triggers:
- BMAD 配置
- BMAD 上下文
- project-context
- bmad 定制
- customize toml
- bmad 目录结构
- bmad 注入
author: 小玛
license: MIT
allowed-tools:
- read_file
- write_file
- terminal
deprecated: []
metadata:
  hermes:
    tags:
    - bmad
    - context-engineering
    - configuration
    - toml
    category: devops
    skill_type: Tool Wrapper
---

# 🧬 BMAD 上下文工程指南 (Context Engineering)

> **核心定位**: BMAD 不是单纯的 Prompt，而是基于**文件系统契约**的上下文注入系统。
> 本 Skill 指导 boku 如何正确配置 BMAD 环境，确保 Agent 拥有完整的上下文记忆。

## 🔍 BMAD 目录结构解剖

BMAD 的上下文由三个层级构成，按优先级从低到高排列：

```text
_project-root/
├── _bmad/
│   ├── core/
│   │   └── config.yaml          <-- [层级 1] 核心配置 (用户、语言)
│   ├── bmm/
│   │   └── config.yaml          <-- [层级 1] BMM 模块配置
│   ├── custom/
│   │   ├── config.toml          <-- [层级 2] 团队级定制 (可提交到 Git)
│   │   └── config.user.toml     <-- [层级 2] 个人级定制 (gitignore)
│   └── scripts/
│       └── resolve_customization.py <-- 上下文解析引擎
├── project-context.md           <-- [层级 3] 全局上下文注入 (最强!)
└── _bmad-output/
```

## ⚙️ 核心机制 1: TOML 三层合并 (The Resolver)

BMAD 启动时通过 `resolve_customization.py` 合并配置，规则如下：

1.  **基础层 (Base)**: `skill/customize.toml` (Skill 默认值)
2.  **团队层 (Team)**: `custom/{skill-name}.toml`
3.  **个人层 (User)**: `custom/{skill-name}.user.toml` (最高优先级)

**合并规则 (Merge Rules)**:
- **标量 (Scalars)**: 覆盖 (Override wins)。
- **数组 (Arrays)**: 
  - 如果数组项包含 `code` 或 `id` 字段：**按键合并** (Keyed Merge)。
  - 普通数组：**追加** (Append)。
- **表 (Tables)**: 深度合并 (Deep Merge)。

**实战技巧**: 永远不要修改 `customize.toml` (Skill 默认值)，它会在更新时被覆盖！要在 `_bmad/custom/` 下创建定制文件。

## 🧠 核心机制 2: 上下文注入 (Persistent Facts)

这是 BMAD 最强大的功能——**强制记忆注入**。
在 TOML 中配置 `persistent_facts`：

```toml
[workflow]
persistent_facts = [
  "file:{project-root}/**/project-context.md",
  "All code must use Rust.",
  "file:{project-root}/docs/api-specs.md"
]
```

**效果**:
1.  AI 会在启动时自动搜索并读取匹配的文件内容。
2.  这些内容会被视为 "Facts" (事实)，直接作为 System Prompt 的一部分注入！
3.  **优先级**: `project-context.md` 中的规则优先级极高，因为它是作为 Facts 加载的。

## 🛠️ 4. 核心机制 3: 流程控制流派 (Step Architecture)

BMAD 有两种截然不同的流程控制方式，创建或修改 Skill 时需注意：

### 流派 A: Micro-File 架构 (推荐用于 PRD/架构)
- **结构**: 使用外部 `steps/step-01.md` 等文件。
- **机制**: AI 每次只能读当前文件，用户点 'C' 才能加载下一个。
- **优点**: **防跳步能力最强**，AI 无法偷看未来步骤，专注度极高。
- **代表**: `bmad-create-prd`, `bmad-create-architecture`。

### 流派 B: In-Skill XML 架构 (推荐用于 开发/Dev)
- **结构**: 所有步骤都在 `SKILL.md` 的 `<workflow>` XML 标签中。
- **机制**: 通过 `<goto step="N">` 在内部跳转。
- **优点**: 减少文件 I/O，加载速度快。
- **缺点**: 如果文件太长，AI 容易丢失当前状态或跳过步骤。
- **代表**: `bmad-dev-story`。

## 📝 5. 实战指南：编写 project-context.md

`project-context.md` 是项目级的 "灵魂文件"。它应该包含：
1.  **技术栈约束**: (如 "Must use Python 3.12+", "No external DB libs")
2.  **代码规范**: (如 "Use snake_case", "Include docstrings")
3.  **业务领域知识**: (如 "User roles: Admin, Editor, Viewer")
4.  **禁止事项**: (如 "DO NOT use global variables")

**模板示例**:

```markdown
# Hermes Project Context

## Tech Stack
- Backend: FastAPI (Python 3.12)
- DB: PostgreSQL + SQLAlchemy
- Testing: Pytest

## Standards
- All endpoints must have error handling.
- Use Pydantic models for validation.
- Comments must be in Chinese.

## Domain Rules
- Users can only delete their own posts.
- "Active" status means user logged in within 7 days.
```

## 🐞 调试上下文丢失

如果 Agent 忘记了规则：
1.  检查 `project-context.md` 是否存在于项目根目录。
2.  运行 `python3 _bmad/scripts/resolve_customization.py --skill <skill-path>` 查看输出的 JSON 中 `persistent_facts` 是否正确解析。
3.  确认 `config.yaml` 中的路径变量（如 `{project-root}`）是否正确。

## 🚩 Red Flags

- ❌ **直接修改 Skill 目录下的 `customize.toml`**: 更新后会被覆盖丢失。
- ❌ **在 `project-context.md` 中写具体的代码实现**: 这里只写规则和上下文，不写具体逻辑。
- ❌ **忘记配置语言**: 确保 `_bmad/core/config.yaml` 里的 `communication_language` 正确。