---
name: capability-pack-design
description: >-
  Agent 能力模块化与跨平台复用方法论。涵盖能力包(Capability Pack)格式设计、
  模块分割决策、生命周期管理、迭代进化闭环、跨 Agent 适配层架构。
  适用于将单体 Agent 能力拆分为可移植、可组合、可进化的模块化能力单元。
version: 1.0.0
author: boku (Emma/小玛)
license: MIT
tags:
  - capability-pack
  - modularization
  - agent-design
  - cross-platform
  - architecture
triggers:
  - 能力模块化
  - capability pack
  - 能力包
  - 模块分割
  - 跨 Agent 复用
  - agent 能力拆分
  - 能力适配
  - 模块化设计
  - 能力包格式
  - cap-pack
  - 统一能力适配器
  - UCA
  - 将能力拆分为模块
  - agent 模块化
depends_on:
  - sdd-workflow
  - deep-research
  - writing-plans
  - development-workflow-index
design_pattern: framework
skill_type: methodology
---

# 🧩 Capability Pack Design — Agent 能力模块化方法论

> **一句话**: 将 Agent 的「技能+经验+工具配置」拆分为标准化能力包，通过适配层部署到不同 Agent 框架。

---

## 〇、核心理念

### 能力包 ≠ 技能分组

能力包不是把几个 SKILL.md 打包在一起。每个能力包是三类成分的**有机组合**：

| 成分 | 作用 | 示例（文档模块） |
|:-----|:------|:----------------|
| 📝 **技能 (Skills)** | 操作步骤 — **怎么做** | pdf-layout/SKILL.md 的 WeasyPrint 用法 |
| 🧠 **经验 (Experiences)** | 领域知识 — **什么场景用什么、有什么坑** | WQY 字体回退、ReportLab 中文编码、CI 环境差异 |
| 🔌 **MCP 配置** | 外部工具连接 — **可以调什么服务** | 文档转换服务 MCP、OCR 服务 |

三者运行时配合：**经验**告诉 Agent「这种情况该用 WeasyPrint 而非 ReportLab」，**技能**告诉它操作步骤，**MCP** 告诉它能调什么外部服务。

---

## 一、可行性调查（四支柱框架）

启动模块化项目前，先回答四个核心问题。每个问题对应一份 Spec：

```text
┌──────────────────────────────────────────────────┐
│             四支柱可行性框架                        │
│                                                   │
│  ① 如何分割？   → 维度分析 + 边界判断 + 粒度标准     │
│  ② 如何管理？   → 生命周期 + 版本号 + 依赖          │
│  ③ 如何迭代？   → 反馈闭环 + 经验同步                │
│  ④ 如何适配？   → 适配层架构 + 多 Agent 映射         │
│                                                   │
│  产出: EPIC 文档 + 4 个 Spec + HTML 追踪报告         │
└──────────────────────────────────────────────────┘
```

### 建议使用 SDD 规范驱动

按 `sdd-workflow` 的流程管理：EPIC → Spec → Story → 实现 → 验证 → 归档。

### 四支柱详细说明

#### ① 分割方案 (Splitting)

**三种候选维度**：

| 维度 | 说明 | 推荐度 |
|:-----|:------|:------:|
| **按领域** | 按「解决什么问题」分类 | 🥇 **推荐** |
| 按工具类型 | 按「用什么工具」分类 | 🥈 备选 |
| 按单技能 | 每个 SKILL.md 一个模块 | ❌ 太碎 |

**四问测试**（判断模块边界是否合理）：

```
Q1: 用户能不假思索地说出这个模块干什么？
    → 否 → 太大，需要拆
Q2: 模块内技能是否共享相同领域知识？
    → 否 → 混入无关技能，需拆
Q3: 移除本模块后其他模块是否受影响？
    → 是 → 有依赖耦合，需解耦
Q4: 本模块能独立在另一个 Agent 上运行吗？
    → 否 → 依赖了宿主 Agent 特有能力
```

#### ② 管理方案 (Management)

**六阶段生命周期**：

```
DRAFT → ACTIVE → MATURING → STABLE → DEPRECATED → ARCHIVED
```

**语义版本号**：MAJOR.MINOR.PATCH（格式变更/新增技能/经验修正）

**依赖管理**：模块依赖 + 工具依赖 + MCP 依赖 + 环境依赖

#### ③ 迭代方案 (Iteration)

**五步闭环**：

```text
[使用中触发] → [评估影响范围] → [执行更新] → [同步通知] → [验证回环]
```

**三种经验来源**：
- 🐛 Pitfall — 陷阱记录（「步骤 X 报错 Y，原因 Z，解法 W」）
- 🌳 Decision Tree — 选型决策（「场景 A 用方案 X，场景 B 用方案 Y」）
- 📊 Comparison — 对比分析（「方案 X 比 Y 快 3 倍，但需额外安装 Z」）

#### ④ 适配方案 (Adaptation)

**UCA (Unified Capability Adapter) 架构**：

```text
Capability Pack (cap-pack.yaml)
        ↓
  UCA Core (解析 + 验证 + 路由)
        ↓
  ┌──────┼──────┐
 Hermes  Claude  Codex
Adapter  Adapter Adapter
```

每个适配器实现 `AgentAdapter` Protocol：
```python
class AgentAdapter(Protocol):
    def install(self, pack: CapPack) -> AdapterResult: ...
    def uninstall(self, pack_name: str) -> AdapterResult: ...
    def update(self, pack: CapPack, old_version: str) -> AdapterResult: ...
    def list_installed(self) -> list[str]: ...
    def verify(self, pack_name: str) -> bool: ...
```

---

## 二、Capability Pack 格式

### 文件结构

```text
cap-pack/{name}/
├── cap-pack.yaml        ← 模块清单（必需）
├── SKILLS/              ← 技能目录
│   ├── skill-a.md
│   └── skill-b.md
├── EXPERIENCES/         ← 经验目录
│   ├── pitfall-foo.md   # type: pitfall
│   └── decision-bar.md  # type: decision-tree
└── MCP/                 ← MCP 配置目录
    └── server.yaml
```

### cap-pack.yaml 核心字段

```yaml
name: doc-engine
version: 1.0.0
type: capability-pack
classification: domain        # domain | toolset | skill
description: 文档生成全套能力

compatibility:
  agent_types: [hermes, claude-code, codex-cli]
  requires_mcp: true
  requires_network: false

capabilities:
  skills:      [id, path, version]
  experiences: [id, path, type]
  mcp_servers: [id, server, endpoint, tools]

config_defaults:        # 默认配置
  pdf_font: WQY-ZenHei

hooks:                  # 生命周期钩子
  on_activate:
    - type: shell
      command: pip install weasyprint python-pptx
  on_deactivate:
    - type: notify
      message: 模块已卸载
```

---

## 三、适配器实现要点

### Hermes 适配器

| 能力包组件 → | Hermes 目标 | 方式 |
|:-------------|:------------|:-----|
| SKILLS/ | `~/.hermes/skills/{pack}/{skill}/SKILL.md` | 直接写入 |
| EXPERIENCES/ | 技能 references/ 目录 | 复制引用文件 |
| MCP/ | `config.yaml` 的 `mcpServers` | `hermes config set` |
| hooks | 安装后 shell | `terminal()` |

**Hermes 特有优势**: Profile 隔离、SRA 自动索引、Curator 生命周期

### Claude Code 适配器

| 能力包组件 → | Claude Code 目标 | 方式 |
|:-------------|:-----------------|:-----|
| SKILLS/ | `~/.claude/skills/{pack}/{id}/SKILL.md` | 直接写入 |
| EXPERIENCES/ | 注入 CLAUDE.md 或 skills reference | 文本追加 |
| MCP/ | `claude.json` 的 `mcpServers` | 修改 JSON |

**注意**: Claude Code 没有 skill_manage 工具，需手动文件操作。

### Codex CLI 适配器

| 能力包组件 → | Codex CLI 目标 | 方式 |
|:-------------|:---------------|:-----|
| SKILLS/ | `.codex/rules/{pack}-{id}.md` | 写入 rules 目录 |
| EXPERIENCES/ | 嵌入 rules 文件 | 内容合并 |
| MCP/ | `.codex/mcp.json` | 修改 JSON |

---

## 四、迭代闭环流程

### 触发条件

| 触发源 | 示例 | 优先级 |
|:-------|:------|:------:|
| 执行报错 | API 变更导致技能步骤失效 | 🔴 高 |
| 主人反馈 | 「这个步骤不对」 | 🔴 高 |
| 效率提升 | 发现更快的操作方法 | 🟡 中 |
| 知识缺口 | 新场景无对应经验 | 🟡 中 |
| 外部变更 | 依赖 API/工具更新 | 🔴 高 |

### 更新模板

```markdown
## 迭代提案

**模块**: doc-engine v1.0.0
**触发条件**: weasyprint 59.0 API 变更
**影响等级**: 🟡 增强 (MINOR → 1.1.0)
**变更内容**:
  - SKILLS/pdf-layout.md: 更新 weasyprint 命令
  - EXPERIENCES/font-setup.md: 新增字体映射经验

**验证方法**:
  1. 生成测试 PDF → 确认格式
  2. 中文字体环境测试 → 确认回退
```

---

## 五、实战陷阱 ⚠️

### 格式设计阶段

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 过度设计 — 追求完美格式 | 项目卡在 Phase 1 出不来 | 先最小可用（只含 skills + experiences），再逐步迭代 |
| 分割维度不统一 | 模块间边界模糊 | 用「四问测试」验证每个模块边界 |
| 忽略 MCP 差异 | 适配时发现某些 Agent 不支持 | 在 compatibility 中声明每项能力 |

### 适配层阶段

| 陷阱 | 后果 | 预防 |
|:------|:------|:------|
| 假设所有 Agent 都有 skill_manage | Claude Code 无法自动创建技能 | 适配器用文件系统直接写入 |
| 忽略 config 格式差异 | Hermes 用 YAML，Claude 用 JSON | 适配器内做格式转换 |
| 未处理 on_activate 钩子 | 安装后缺少依赖 | 每个适配器都执行钩子 |

### 迭代阶段

| 陷阱 | 后果 | 预防 |
|:------|:------|:------|
| 更新通知轰炸 | 主人厌烦 | PATCH 级别静默更新，MAJOR 才通知 |
| 跨模块级联更新不回滚 | 部分 Agent 更新成功部分失败 | 用 `on_deactivate` + 备份实现原子性 |
| 经验与技能脱节 | 经验说 A 但技能步骤已是 B | SKILL.md 中加 `experience_ref` 字段显式关联 |

---

## 六、验证清单

启动模块化项目前检查：

- [ ] 四支柱可行性框架已完成（分割/管理/迭代/适配）
- [ ] 候选模块清单已用「四问测试」验证
- [ ] cap-pack.yaml 格式已定稿
- [ ] 至少一个模块包含真实经验（非空 EXPERIENCES/）
- [ ] 每个适配器有显式的「能力覆盖矩阵」
- [ ] 迭代闭环的触发条件已明确
- [ ] 回滚机制已建立（安装前备份）

---

## 七、相关 Skill

| Skill | 用途 |
|:------|:------|
| `sdd-workflow` | Spec 生命周期管理 + 状态机 |
| `deep-research` | 四支柱框架的行业调研阶段 |
| `development-workflow-index` | 选择开发路径的决策树 |
| `writing-plans` | 模块实现的实施计划 |
| `self-capabilities-map` | 盘点现有 Agent 能力存量（⚠️ 需配合穷举扫描） |

## 八、参考文件

| 文件 | 内容 |
|:-----|:------|
| `references/feasibility-study-2026-05-12.md` | 实战记录：18 模块分类 + 遗漏分析 + 业界对比数据 + 扩展性设计 |
| `references/industry-research.md` | 业界模块化方案调研笔记 |
