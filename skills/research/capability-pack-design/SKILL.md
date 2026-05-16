---
name: capability-pack-design
description: >-
  Agent 能力模块化与跨平台复用方法论。涵盖能力包(Capability Pack)格式设计、
  模块分割决策、生命周期管理、迭代进化闭环、跨 Agent 适配层架构。
  适用于将单体 Agent 能力拆分为可移植、可组合、可进化的模块化能力单元。
version: 3.0.0
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
  - 树状索引
  - skill tree
  - skill树
  - 能力包管理
  - 模块合并
  - skill 冗余
  - 技能精简
  - consolidation
  - skill 审计
  - 全量审计
  - 技能健康度
  - 能力包工具链
  - extract pack
  - validate pack
  - install pack
  - skill-tree-index
  - 健康检查
  - health check
  - CHI
  - 包健康度
  - 技能诊断
  - sra 集成
  - SRA 适配
  - skill runtime advisor
  - 运行时发现
  - 后置质量升级
  - 三层改造
  - post-extraction
  - 质量升级
  - 能力包合并
  - skill 治理
  - 技能治理
  - governance engine
  - 治理引擎
  - skill quality
  - skill scanner
  - skill validator
  - 治理修复
  - fix engine
  - 自动修复
  - skill-governance fix
  - 扫描修复闭环
  - 检测修复
  - 治理修复引擎
  - governance fix
  - cross-agent 挂载
  - 跨 Agent 挂载
  - 不碰原生技能
  - 挂载层
  - mount layer
  - AI 友好 README
  - readme for ai
  - 适配器指南
  - adapter guide
  - 批量修复
  - batch fix
  - 修复后对齐
  - post-fix
  - skill to cap-pack
  - 转换为能力包
  - skill转换
  - convert skill
  - cap-pack converter
  - skill extract
  - 技能提取
  - 技能转包
  - hermes skill 转换
  - skillkit
depends_on:
  - sdd-workflow
  - deep-research
  - writing-plans
  - development-workflow-index
  - skill-creator
  - self-capabilities-map
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

### 核心原则：cap-pack 是挂载层，不是改造层

> **2026-05-16 关键设计纠正**：cap-pack 的目标不是改造任何 Agent 的原生技能库，而是提供一个标准化挂载层。

```
Agent A 原生技能       Agent B 原生技能
     ↕                    ↕
┌──────────────────────────────────┐
│       Cap-Pack 挂载层              │
│  install / uninstall / list       │
│  (通过各 Agent 适配器操作)          │
└──────────────────────────────────┘
     ↕                    ↕
  合规扫描 + 自动修复        ← 治理引擎确保包质量
  README + Adapter Guide   ← 让任意 Agent 5 分钟上手
```

**设计铁律**：
- ❌ 不改造 Agent 原生技能目录（不碰 `~/.hermes/skills/` 原生内容）
- ✅ Agent 自有技能和 cap-pack 安装的技能共存
- ✅ cap-pack 安装到约定的挂载路径（如 `~/.hermes/skills/` 下以包名为前缀的新目录）
- ✅ 卸载时只删除挂载路径下的文件，不影响 Agent 原生技能

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

#### ①-α Skill 组织架构决策（2026-05-13 调研新增）

> **背景**：2026-05 深度调研了原子 Skill + MCP + Workflow 编排 vs 树状多层 Skill 两种架构的效率差异。调研覆盖 9 篇学术论文 + 8 篇实践指南，详见 `reports/skill-tree-architecture-research.html`。

**核心发现**：两种架构不是竞争对手，而是互补的设计模式。

| 对比维度 | 原子 Skill + MCP + Workflow | 树状多层 Skill |
|:---------|:---------------------------:|:--------------:|
| 设计哲学 | 微内核：小即是美，组合胜过继承 | 层次抽象：分类驱动，渐进式降维 |
| 检索复杂度 | **O(n)**（依赖 workflow 匹配） | **O(log n)**（树遍历） |
| 并行能力 | ✅ **原生 DAG 并行**（3.6× 加速） | ❌ 串行递归 |
| Token 成本 | **极低**（蓝本固化，99% 节省） | 中（三层渐进式加载） |
| 大规模韧性 | ⚠️ 随规模递减（100+ 临界点） | ✅ **优异**（树路由防止相变） |
| 组合灵活性 | ⭐ **9.5/10**（DAG: 并行/条件/循环） | ⭐ 5.5/10（本质串行） |
| 推理可追溯 | ⭐ 7/10（需理解编排逻辑） | ⭐ **8.5/10**（天然清晰） |
| 生态整合 | ✅ **极佳**（MCP 10,000+ 服务器） | ⚠️ 自有体系 |

**关键学术发现**（arxiv 2601.04748）：LLM 的 skill 选择精度存在**相变临界点**——当库大小超过 ~100-200 时，选择精度不是逐渐降低而是急剧崩塌。根因是 skill 间的**语义混淆度**而非库大小本身。层次化组织（即树模式）能显著缓解此问题。

**三支柱融合模型**——能力包的推荐架构：

```text
                  Agent LLM
                     |
            +--------+--------+
            │  🌳 树状 Skill   │  ← 渐进式索引（发现/路由）
            │  Index           │     树分类 + 粗到细检索
            +--------+--------+
                     |
            +--------+--------+
            │  🔄 Workflow    │  ← DAG 编排（组合/执行）
            │  Orchestrator   │     并行/串行/管道/条件
            +--------+--------+
                     |
     +---------------+---------------+
     │               │               │
  Skill A         Skill B        Skill C  ← 原子 Skill（能力单元）
     │               │               │
   MCP X           MCP Y          MCP Z   ← MCP 工具（连接层）
```

**针对能力包的决策指南**：

| 能力包规模 | Skill 数 | 推荐组织方式 | 理由 |
|:----------|:--------:|:------------|:-----|
| **小型包** | < 10 | 扁平列表 + 语义描述 | 树状开销 > 收益 |
| **中型包** | 10-50 | **轻度层次化**（2-3 级分类） | ⬅️ 大部分 cap pack 在此区间 |
| **大型包** | 50+ | 完整树状索引 + 可选 Workflow | 进入相变区，必须层次化 |

**实践建议**：
1. **包内 skill 用 2 层深度**（类别→skill）足够，3 层以上开始造成过深遍历开销
2. **MCP 连接层与 skill 层保持正交**——skill 描述"做什么/怎么做"，MCP 描述"能连什么"
3. **Workflow 编排**在 cap pack 中通过 `cap-pack.yaml` 的 `lifecycle` hooks 和跨 skill 引用实现轻量级编排，不引入外部 DAG 引擎

#### ② 管理方案 (Management)

**六阶段生命周期**：

```
DRAFT → ACTIVE → MATURING → STABLE → DEPRECATED → ARCHIVED
```

**后置质量升级阶段**: 当所有模块提取完成后，建议执行 EPIC-004 规划的三层改造（L2 Experiences + L3 Brain 补充）、全量健康度检测（CHI ≥ 0.85）、合并重叠 skill。详见 `capability-pack-design/references/post-extraction-quality-upgrade.md`。

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

### v1 格式 (2026-05-13)

- **JSON Schema**: `schemas/cap-pack-v1.schema.json`（基本验证）
- **三工具链**: `scripts/extract-pack.py` / `validate-pack.py` / `install-pack.py`
- **原型验证**: doc-engine（12 skills, 5 experiences）

### v2 结构化格式 (2026-05-14 新增) 🔥

**JSON Schema**: `schemas/cap-pack-v2.schema.json`（完整验证，全部 7 个 pack 已通过）

**v1 → v2 核心变更**：

| 字段 | v1 | v2 | 原因 |
|:-----|:---|:---|:------|
| `classification` | ❌ 可选 | ✅ 必填（domain/toolset/skill/**infrastructure**） | 区分业务包与系统包 |
| `display_name` | ❌ 缺失 | ✅ 必填 | 人类可读包名 |
| `integration` | ❌ 缺失 | ✅ 新增 | 声明外部集成脚本 |
| `verification` | ❌ 缺失 | ✅ 新增 | 健康检查 + 签名 |
| `lifecycle` | 仅有简单 hooks | ✅ 三阶段（install/update/uninstall 各含子阶段） | 工程化安装 |
| `config_schema` | ❌ 缺失 | ✅ 新增 | 配置值类型声明 |
| `compatibility.hermes_version` | ❌ 缺失 | ✅ 新增（min/max 版本范围） | 跨版本兼容性 |
| `skills[].path` | ❌ 必填 | 🔄 可选（与 source 二选一） | 向后兼容 v1 |
| `experiences[].type` | `enum` 限制 | 🔄 新增 `experience` 类型 | 默认通用类型 |
| 日期字段 | 未限制 | 必须加引号（`"2026-05-14"`） | JSON Schema 要求 string |

**快速迁移**：
```bash
cd ~/projects/hermes-cap-pack
python3 -c "
import json, yaml
from pathlib import Path
with open('schemas/cap-pack-v2.schema.json') as f:
    schema = json.load(f)
import jsonschema
for p in sorted(Path('packs').iterdir()):
    if p.is_dir() and (p / 'cap-pack.yaml').exists():
        pack = yaml.safe_load((p / 'cap-pack.yaml').read_text())
        try:
            jsonschema.validate(instance=pack, schema=schema)
            print(f'✅ {p.name}')
        except jsonschema.ValidationError as e:
            print(f'❌ {p.name}: {e.message[:80]}')
"
```
- **JSON Schema**: `schemas/cap-pack-v1.schema.json`（基本验证）
- **三工具链**: `scripts/extract-pack.py` / `validate-pack.py` / `install-pack.py`
- **原型验证**: doc-engine（12 skills, 5 experiences）

### v2 结构化格式 (2026-05-14 新增) 🔥

**JSON Schema**: `schemas/cap-pack-v2.schema.json`（完整验证，全部 7 个 pack 已通过）

**v1 → v2 核心变更**：

| 字段 | v1 | v2 | 原因 |
|:-----|:---|:---|:------|
| `classification` | ❌ 可选 | ✅ 必填（domain/toolset/skill/**infrastructure**） | 区分业务包与系统包 |
| `display_name` | ❌ 缺失 | ✅ 必填 | 人类可读包名 |
| `integration` | ❌ 缺失 | ✅ 新增 | 声明外部集成脚本（见 §七） |
| `verification` | ❌ 缺失 | ✅ 新增 | 健康检查 + 签名 |
| `lifecycle` | 仅有简单 hooks | ✅ 三阶段（install/update/uninstall 各含子阶段） | 工程化安装 |
| `config_schema` | ❌ 缺失 | ✅ 新增 | 配置值类型声明 |
| `compatibility.hermes_version` | ❌ 缺失 | ✅ 新增（min/max 版本范围） | 跨版本兼容性检查 |
| `skills[].path` | ❌ 必填 | 🔄 可选（与 source 二选一） | 向后兼容 v1 pack |
| `experiences[].type` | `enum` 限制 | 🔄 新增 `experience` 类型 | 默认通用类型 |
| 日期字段 | 可能被 YAML 解析为 date 对象 | 必须加引号（`"2026-05-14"`） | JSON Schema 验证要求 |

**快速迁移：**
```bash
# 验证所有 pack 是否符合 v2
cd ~/projects/hermes-cap-pack
python3 -c "
import json, yaml, os
from pathlib import Path
with open('schemas/cap-pack-v2.schema.json') as f:
    schema = json.load(f)
import jsonschema
for p in Path('packs').iterdir():
    if p.is_dir() and (p / 'cap-pack.yaml').exists():
        pack = yaml.safe_load((p / 'cap-pack.yaml').read_text())
        try:
            jsonschema.validate(instance=pack, schema=schema)
            print(f'✅ {p.name}')
        except jsonschema.ValidationError as e:
            print(f'❌ {p.name}: {e.message[:80]}')
"
```
- **三工具链就绪**: `scripts/extract-pack.py` / `validate-pack.py` / `install-pack.py`
- **原型验证通过**: doc-engine（12 skills, 5 experiences, 完整 linked files）

### 文件结构

能力包的物理存储推荐使用两层结构：项目级仓库存放多个能力包，每个包独立一个目录。

```
packs/{name}/                # 推荐结构，适合多包管理
├── cap-pack.yaml            ← 模块清单（必需）
├── SKILLS/                  ← 技能目录
│   ├── skill-a.md
│   └── skill-b.md
├── EXPERIENCES/             ← 经验目录
│   ├── pitfall-foo.md       # type: pitfall
│   └── decision-bar.md      # type: decision-tree
└── MCP/                     ← MCP 配置目录（可选）
    └── server.yaml
```

> **注意**: 物理路径是 `packs/` 而非 `cap-pack/`——因为多包场景下 `packs/` 语义更清晰，与常见的 monorepo 约定一致。单包场景可直接使用 `cap-pack/{name}/`。

### 配套文件

每个格式定义应附带一个 JSON Schema 用于编程验证：

```
schemas/
├── cap-pack-format-v1.md       ← 格式规范文档（人类阅读）
└── cap-pack-v1.schema.json     ← JSON Schema（机器验证）
```

验证命令：
```bash
python3 -c "
import json, yaml
with open('schemas/cap-pack-v1.schema.json') as f:
    schema = json.load(f)
with open('packs/doc-engine/cap-pack.yaml') as f:
    pack = yaml.safe_load(f)
import jsonschema
jsonschema.validate(instance=pack, schema=schema)
print('✅ 验证通过')
"
```

> ⚠️ 确保 YAML 中所有日期字段（`created`/`updated`）都加引号，否则被解析为 `datetime.date` 对象而非字符串。

### cap-pack.yaml 核心字段

```yaml
name: doc-engine
version: 2.0.0
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

### 四-B、能力包提取 SOP (Standard Operating Procedure) 🔥

> **2026-05-14 实战经验** — 从 Hermes 技能目录提取标准化能力包的 6 步操作流程。  
> 实战验证: learning-engine 能力包（11 skills, 平均 SQS 72.1）

当需要将一批 Hermes skill 提取为 cap-pack 时，严格按以下 6 步执行：

#### 第 1 步：盘点 (Inventory)

```bash
# 确认每个 skill 的 SKILL.md 文件位置
for skill in skill-a skill-b skill-c; do
    find "$HOME/.hermes/skills" -path "*/$skill/SKILL.md" -type f
done
```

**产出**: skill 清单 + 位置映射表

#### 第 2 步：SQS 质检 (Quality Baseline)

```bash
for skill in skill-a skill-b skill-c; do
    python3 ~/.hermes/skills/skill-creator/scripts/skill-quality-score.py "$skill" --json
done
```

**门禁**: SQS < 50 的 skill 不放行，标注到 exceptions

#### 第 3 步：提取 (Extraction)

```bash
mkdir -p packs/{name}/SKILLS/{skill-a,skill-b}
cp "$SOURCE/$skill/SKILL.md" "packs/{name}/SKILLS/$skill/SKILL.md"
```

**cap-pack.yaml 编写要点**:
- `classification`: domain / toolset / infrastructure
- `compatibility.hermes_version`: 设置 min/max 范围
- 日期字段加引号：`created: "2026-05-14"`
- 依赖包声明：`dependencies.cap_packs`

#### 第 4 步：验证 (Validation)

```bash
python3 -c "import json, yaml; import jsonschema; ..."  # v2 schema 验证
```

#### 第 5 步：项目对齐 (Project Alignment)

> **🚨 强制门禁** — 提取后必须同步更新以下项目文档，否则全景报告与代码状态脱节。

```bash
# 5a. 更新 project-report.json 或项目状态文件
#  - 在 architecture.layers[].modules[] 添加新包
#  - 注册新 Story

# 5b. 更新 PROJECT-PANORAMA.html
#  - 添加新包卡片
#  - 更新 KPI 数据（包数、覆盖百分比）
#  - 更新"剩余模块"清单

# 5c. 更新 EPIC 文档（EPIC-003-module-extraction.md）
#  - 标记模块为 ✅ 已提取

# 5d. 更新全景路线图（EPIC-003-comprehensive-roadmap.md）
#  - 全景表: ⬜ → ✅
#  - Story 行: 更新状态

# 5e. 🆕 运行提取完成仪式（自动更新 project-state.yaml + Story doc）
python3 scripts/complete-extraction.py <module-name>

# 5f. 🆕 验证项目状态一致性
python3 scripts/project-state.py verify
# exit 0 = 通过, exit 1 = 失败（必须修复）

# 5g. 确认无残留引用
# 如涉及模块合并（见 四-D），用 grep 检查残留旧名称
```

#### 第 6 步：提交前门禁 (Pre-push Gate)

> **🚨 新增门禁** — 提交前必须运行 pre-push 本地检查，避免 CI 失败。

```bash
# 运行本地门禁
bash scripts/pre-push.sh
# 全部 ✅ → 可以提交
# 任何 ❌ → 先修复再提交

git add packs/{name}/ docs/ PROJECT-PANORAMA.html scripts/
git commit -m "feat: {name} 能力包提取 (N skills)"

项目报告同步更新：project-report.json + PROJECT-PANORAMA.html"
```

#### SOP 速查表

| 步骤 | 命令 | 关键检查点 | 耗时 |
|:-----|:------|:-----------|:----:|
| ① 盘点 | `find + ls` | 所有 skill 都有 SKILL.md | 10min |
| ② SQS | `skill-quality-score.py` | 无可跳过项（<50） | 5min |
| ③ 提取 | `mkdir + cp + write yaml` | cap-pack.yaml 包含全部 skill | 20-40min |
| ④ 验证 | `jsonschema.validate` | v2 schema 全部通过 | 5min |
| ⑤ 对齐 | 更新 project-report + HTML + state | 项目报告反映新包 | 5min |
| ⑥ 提交 | `git commit` | SDD complete | 2min |

### 四-B-1 自动转换方向 — Hermes Skill → Cap-Pack（待实现）

> **2026-05-16 新增** — 以上 SOP 是**手动**流程。治理引擎当前**不包含**从 `~/.hermes/skills/` 自动转换到 Cap-Pack 格式的能力。
> **现状**: `extract-pack.py` 只做单 skill 文件复制（不生成 manifest），`CapPackAdapter.suggest()` 做匹配但不自动执行。
> **完整差距分析**: `references/hermes-to-cap-pack-converter.md`

**需要新增的模块**: `skill_governance/converter/`

| 文件 | 用途 |
|:-----|:------|
| `converter/extractor.py` | 核心提取逻辑（文件解析+复制+manifest 生成） |
| `converter/manifest_builder.py` | cap-pack.yaml 生成器（从 SKILL.md frontmatter 构造） |
| `converter/grouping.py` | 智能分组引擎（按 tag/domain/classification 聚类） |

**CLI 示例**（规划中）:
```bash
skill-governance extract pdf-layout --pack doc-engine     # 单 skill
skill-governance extract --all --auto-group                # 全量
```

**可复用资产**（无需重写）:
- `CapPackAdapter.suggest()` → 自动匹配合适 pack
- `_parse_frontmatter()` → 解析 SKILL.md
- `find_skill_dir()` / `list_skill_files()` → 文件操作
- `validate-pack.py` + schema → 验证输出

---

### 四-B-α 批量操作模式（"继续"工作流）

> **实战验证**: 从 cap-pack-operations 吸收——当用户对已建立的工作流只说"继续"时，进入批量高效模式。

| 行为 | 说明 |
|:-----|:------|
| 交互模式 | 每完成一个模块，用户回应"继续"即启动下一个。无需汇报摘要、等待明确批准 |
| 模块顺序 | 按 Phase 优先级执行。提供下一模块名让用户确认（如"继续 next-module？"），用户回"继续"视为确认 |
| 每模块时间盒 | 大模块（5+ skills）~10 min，小模块（1-2 skills）~5 min |
| 产出原则 | 只提交实质性变更；不创建中间状态文件 |
| 批量完成清单 | SKILL.md 复制 + experiences 创建 + cap-pack.yaml 更新 + schema 验证 + 项目报告同步 + 提取完成仪式 + pre-push 门禁 |

**详细命令参考**: `references/extraction-commands.md`（已吸收自 cap-pack-operations）
**CI 失败恢复**: `references/ci-failure-recovery.md`（已吸收自 cap-pack-operations）

---

### 四-D、能力包合并工作流 (Merge Workflow) 🔥

> **2026-05-14 新增** — 当发现两个能力包内容重叠、技能已被另一包吸收、或边界划分不合理时的标准化合并流程。
> **2026-05-15 扩展** — 新增跨层合并模式 (Hermes 系统 + cap-pack 包) 和技能降级模式 (Skill→Experience)
> 实战验证: knowledge-base 合并至 learning-engine（8 份文档对齐 + 脚注标注原因）

#### 触发条件

| 信号 | 示例 | 优先级 |
|:-----|:------|:------:|
| **技能重叠** | 包 A 的 70%+ 技能已在包 B 中 | 🔴 立即 |
| **循环依赖** | 包 A 依赖包 B，包 B 也依赖包 A | 🔴 立即 |
| **自然吸收** | 提取包 A 时发现核心技能已被包 B 吸收 | 🟡 中 |
| **边界模糊** | 包 A 的领域描述与包 B 无法清晰区分 | 🟡 中 |

#### 合并七步流程

```text
Step 1: 重叠审计 ── 列出两个包的技能清单，精确比对重叠度
    ↓
Step 2: 决策确认 ── 主人批准合并方向（A→B 还是 B→A）
    ↓
Step 3: 依赖解除 ── 更新目标包 cap-pack.yaml：移除合并源包的依赖声明
    ↓
Step 4: 技能整合 ── 更新目标包描述、技能数、tag 以反映合并
    ↓
Step 5: 文档对齐 ── 逐一更新所有引用合并源包的文档
    ↓
Step 6: 标注原因 ── 每处修改添加合并注释 + 脚注（原因三要素）
    ↓
Step 7: 提交验证 ── git commit + 验证无残留引用
```

#### 文档对齐检查清单（Step 5 + 6）

合并后必须检查并更新以下文档层级。每一处修改必须附带合并注释和原因：

| 层级 | 文档 | 需更新内容 |
|:-----|:-----|:----------|
| 🔴 **P0** | 目标包 `cap-pack.yaml` | 移除合并源包依赖 + 添加注释 |
| 🔴 **P0** | 模块分割 Spec（如 `SPEC-1-1`） | 模块表移除/合并行 + 更新技能数 + 分层图 |
| 🔴 **P0** | 提取路线图（如 `EPIC-003`） | Phase 表、路线图、KPI、验收标准 |
| 🟡 **P1** | 全景路线图（如 `EPIC-003-comprehensive-roadmap`） | 全景表、Phase 分配、依赖图 |
| 🟡 **P1** | 提取计划 Spec（如 `SPEC-3-3`） | 模块清单、执行计划、AC 表 |
| 🟡 **P1** | 分类映射表（如 `SPEC-2-3` SRA） | 合并类别别名 |
| 🟢 **P2** | `README.md` | 包列表、覆盖统计、脚注 |
| 🟢 **P2** | `constraints.md` | 如有模块数引用 → 更新 |

#### 合并注释三要素

每处修改必须标注以下三个信息，保证可追溯性：

```
原因①: 什么被合并（技能/领域列表）
原因②: 为什么合并（消除循环依赖 / 自然吸收 / 边界模糊）
原因③: 合并后影响（模块数变化 / 覆盖率变化 / 依赖树变化）
```

**脚注格式示例**（用于 Markdown 文档）：
```markdown
[^1]: **⚡ 合并注释**: `knowledge-base`（原 #1，📚 知识库系统）已于 2026-05-14 合并至
      `learning-engine`。原因：① 核心知识技能（knowledge-precipitation, knowledge-routing,
      hermes-knowledge-base, llm-wiki）已在 learning-engine 提取时吸收；② 消除包间循环依赖
      （原 learning-engine 依赖 knowledge-base，但 knowledge-base 又依赖 learning 方法论）；
      ③ 合并后模块体系从 18+3 更新为 **17+3**。
```

**cap-pack.yaml 注释示例**：
```yaml
# ⚡ knowledge-base 已合并至此包 — 详见 SPEC-1-1 合并注释
dependencies:
  cap_packs:
    - name: skill-quality
      version: "1.0.0"
```

#### 合并风险与回退

| 风险 | 概率 | 缓解 |
|:-----|:----:|:------|
| 文档对齐遗漏 | 中 | 用 `grep -r "原模块名"` 检查残留引用后提交 |
| 依赖指向已删除包 | 低 | `validate-pack.py` 会检测断裂依赖 |
| 分类映射未更新 | 低 | SRA 仍使用旧类别名 → 无错但效率降低 |

### 四-D-α 跨层合并模式 (Cross-Layer Merge) ⚡

> **场景**: 技能存在于 `~/.hermes/skills/`（Hermes 系统）但 **不在** 任何 cap-pack 包中。
> **例如**: BMAD 系列技能（bmad-context-engineering, bmad-party-mode-orchestration, bmad-context-insights）

| 特征 | 含义 |
|:-----|:------|
| 源技能位置 | `~/.hermes/skills/{name}/SKILL.md` |
| cap-pack 影响 | **无** — 技能不在任何 pack 中 |
| 操作层级 | 纯 Hermes 系统级 |

**执行步骤**:

```bash
# 1. 内容分析 → 识别源技能的独有内容
# 2. 合并内容到目标: 将源 SKILL.md 内容复制到目标 references/
# 3. 标记源 deprecated: 在源 SKILL.md 末尾追加弃用提示
# 4. 更新目标 frontmatter: 添加 deprecated: [] 字段
```

**铁律**:
- ❌ 不删除原文件 — 只标记 deprecated（保留回溯依据）
- ✅ 内容合并到 `references/` — 不修改 target 的 SKILL.md 主体
- ✅ 保留 SQS 高的 skill 作为 target

### 四-D-β 技能降级模式 (Skill→Experience Downgrade) ⚡

> **场景**: 微技能（<50 行，SQS < 60）同时存在于 `~/.hermes/skills/` **和** cap-pack 包中。
> **例如**: 6 个 doc-engine 微技能（markdown-guide, docx-guide 等）降级为 experiences

| 特征 | 含义 |
|:-----|:------|
| 源技能位置 | 双层级: Hermes 系统 + cap-pack `SKILLS/` |
| cap-pack 影响 | **大** — 需修改 SKILLS/ + EXPERIENCES/ + cap-pack.yaml |
| 操作层级 | 双层级: 系统级 deprecated + 包级降级 |

**执行步骤**:

```text
[包级操作]                    [Hermes 系统级操作]
   ↓                                ↓
1. 创建 experience 文件         4. 标记源 skill deprecated
   到 EXPERIENCES/                 在 SKILL.md 末尾追加提示
   (带 type: experience
   + description 标注来源)
   ↓
2. 从 SKILLS/ 移除源技能目录
   (rm -rf, git rm)
   ↓
3. 更新 cap-pack.yaml
   - skills[] 移除 ← 注意 skill 数量
   - experiences[] 新增 ← 标注"从 XX skill 降级"
```

**cap-pack.yaml 变更示例**:
```yaml
# 从 skills 移除:
# - id: docx-guide

# 在 experiences 新增:
- id: docx-quick-ref
  title: Word 文档操作速查
  description: python-docx 创建/编辑 Word 文档 — 从 docx-guide skill 降级
```

**验证**:
```bash
python3 scripts/validate-pack.py packs/<name>        # 包完整性
find packs/<name>/SKILLS -name "SKILL.md" | wc -l     # 技能数核对
grep -r "合并到\|已降级" ~/.hermes/skills/<name>/SKILL.md  # deprecated 标记
```

**陷阱**:
| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 只改 cap-pack 不改 Hermes 系统 | Hermes 仍推荐已降级的 skill | 两端必须同步 deprecated 标记 |
| experience 的 description 不标注来源 | 无法追溯降级历史 | 用 `从 XX skill 降级` 格式 |
| 忘记更新 cap-pack.yaml 的 skill 计数 | 文档与代码漂移 | 运行 `validate-pack.py` 验证 |

#### 相关参考

| 文档 | 说明 |
|:-----|:------|
| `references/cap-pack-merge-workflow-example.md` | knowledge-base → learning-engine 实战合并记录（完整对齐清单 + 验证步骤） |
| `references/phase3-merge-execution-example.md` | **BMAD 跨层合并 + 微技能降级 实战记录** — Hermes 系统 + cap-pack 双层级操作 |

#### 验证命令（提交前运行）

```bash
# 1. 检查残留引用（确保无遗漏）
cd ~/projects/hermes-cap-pack
grep -rn "knowledge-base" docs/ packs/ README.md | grep -v "合并注释\|合并" || echo "✅ 无残留引用"

# 2. 验证目标包 YAML 完整性
python3 -c "import yaml; yaml.safe_load(open('packs/target/cap-pack.yaml'))"

# 3. 项目状态一致性
python3 scripts/project-state.py verify
```

---

### 四-C、SRA 运行时发现适配（原 §四-C 不变，编号后移）

> **2026-05-13 新增** — CAP Pack 与 SRA (Skill Runtime Advisor) 的适配策略

### 为什么需要适配

| 系统 | 管什么 | 不管什么 |
|:-----|:--------|:---------|
| **CAP Pack** | 技能静态结构 — 分类/质量/生命周期 | 运行时的技能发现 |
| **SRA** | 运行时语义匹配 — TF‑IDF/同义词/上下文注入 | 技能的结构管理 |

两者互补。SRA 的类别维度（15% 推荐权重）在无分类体系时靠「猜标签」精度低。CAP Pack 的 18 模块分类体系可直接提升 SRA 匹配精度。

### 三层适配架构

```
                     ┌──────────────────────────────┐
                     │     CAP Pack (结构管理层)      │
                     └──────────┬───────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   适配层 (Adapter)     │
                    │ ① 分类映射器           │
                    │ ② 质量注入器           │
                    │ ③ 变更通知器           │
                    └───────────┬───────────┘
                                │
                     ┌──────────┴──────────┐
                     │  SRA (运行时发现层)   │
                     │ 四维匹配 · 场景记忆   │
                     └─────────────────────┘
```

### 三个集成点

| 集成点 | 方案 | 效果 |
|:-------|:-----|:------|
| **分类映射** | CAP Pack 18 模块 → SRA 类别维度别名表 | 类别匹配精度 +15-20% |
| **质量加权** | SQS 分 → 推荐修饰因子 (≥80:1.0 / ≥60:0.9 / ≥40:0.7 / <40:0.4) | 低分 skill 不再被优先推荐 |
| **树状感知** | `skill-tree-index.py --sra` 输出簇/包/同类技能 | SRA 支持簇级推荐 |

### 关键设计决策

| 决策 | 理由 |
|:-----|:------|
| **不合并项目** | SRA 已独立发布 PyPI (`sra-agent`) |
| **适配层而非侵入修改** | 双方独立演进 |
| **分类映射表先行** | 最简单、收益最高、零侵入 |
| **`--sra` 模式在 tree-index 中** | 现有工具扩展 |

### 相关文档

| 文档位置 | 说明 |
|:---------|:------|
| `~/projects/hermes-cap-pack/docs/SPEC-007-sra-adaptation.md` | SRA-CAP Pack 适配方案完整规范 |
| `~/projects/hermes-cap-pack/docs/stories/STORY-016-sra-category-map.md` | 分类映射表工作项 |
| `~/projects/hermes-cap-pack/docs/stories/STORY-017-sqs-sra-weighting.md` | SQS 加权推荐工作项 |

---

## 五、子系统整合工作流

> **2026-05-13 新增** — 当需要将已完成的研究/工具正式整合为 CAP Pack 项目子系统时使用。

### 整合流程

```text
研究成果（研究报告/工具脚本）
    ↓ Step 1: EPIC 文档化
    ↓ Step 2: Spec 规范制定
    ↓ Step 3: Story 分解
    ↓ Step 4: 工具纳入项目
    ↓ Step 5: 能力包创建
    ↓ Step 6: 文档同步
    ↓ Step 7: Git 提交 & 推送
    ↓ Step 8: SDD 注册
```

### 文档模板参考

| 文档 | 参考模板 |
|:-----|:---------|
| EPIC | `docs/EPIC-002-tree-health.md` |
| SPEC | `docs/SPEC-005-tree-index.md`, `docs/SPEC-006-quality-health.md` |
| Story | `docs/stories/STORY-NNN-short-name.md` 格式 |

### 已完成子系统

| 子系统 | EPIC | 状态 |
|:-------|:-----|:----:|
| 能力模块化 | EPIC-001 | ✅ completed |
| 树状层次 + 健康度 | EPIC-002 | ✅ integrated |
| SRA 运行时发现适配 | SPEC-007 | ⬜ planned |

---

---

## 十六、三层 Cap-Pack 管理体系 (Three-Layer Cap-Pack Management System) 🔥

> **2026-05-16 新增** — 基于 EPIC-007 深度设计 (本地 Cap-Pack 管理系统) 的经验沉淀。能力包不是只放在 GitHub 上就行了——需要「远程官方包 ↔ 本地工作副本 ↔ Hermes 原生技能」三层管理体系来支撑日常开发与发布。

### 16.1 三层架构

```
┌─────────────────────────────────────────────┐
│  Layer 1: 远程仓库 (GitHub)                  │
│  🏛️ 官方能力包 — 发布态                      │
│  经过治理引擎认证的稳定版本                    │
│  (只读, 通过 release 更新)                   │
├─────────────────────────────────────────────┤
│         ↕ sync (存在性 + 版本变更)           │
├─────────────────────────────────────────────┤
│  Layer 2: 本地 Cap-Pack 管理                 │
│  📦 本地工作副本 — 开发态                    │
│  ~/.cap-pack/packs/                         │
│  从官方拉取 · 本地修改 · 治理验证 · 推回官方  │
│  支持自建包（仅本地，不推远程）               │
├─────────────────────────────────────────────┤
│         ↕ convert (Hermes 原生 → Cap-Pack)  │
├─────────────────────────────────────────────┤
│  Layer 3: Hermes 原生技能目录                │
│  📝 ~/.hermes/skills/ — 日常运行态          │
│  主 Agent 使用的扁平原生技能库                │
└─────────────────────────────────────────────┘

🧠 经验积累系统 (跨层横向)
任务出错 → 标记经验 → 路由 → 改良技能包 / 记忆存档
```

### 16.2 各层职责

| 层 | 路径 | 读写 | 治理门禁 | 同步方向 |
|:--|:-----|:----:|:---------|:---------|
| **Layer 1** 远程 | GitHub `packs/` | 🏛️ 只读（官方） | L0-L4 全量 | ↓ pull |
| **Layer 2** 本地 | `~/.cap-pack/packs/` | ✏️ 读写（开发） | push 前 L0-L1 | ↑ push |
| **Layer 3** 原生 | `~/.hermes/skills/` | ✏️ 读写（日常） | convert 前 SQS | → convert |

### 16.3 两种同步模式

#### 存在性同步 (Existence Sync)

检测本地 vs 远程的**包的有无**，新增或缺失：

```text
本地      远程      状态      操作
✅        ✅        同步      —
✅        ❌        仅本地    push 或标记自建
❌        ✅        缺失      pull
```

#### 版本变更同步 (Version Sync)

检测**版本号 + 文件 hash**的差异：

| 本地版本 | 远程版本 | 本地 Hash | 远程 Hash | 状态 | 操作 |
|:--------:|:--------:|:---------:|:---------:|:-----|:-----|
| 2.0.0 | 2.0.0 | abc | abc | ✅ 同步 | — |
| 2.0.0 | 2.0.0 | abc | def | 🔄 远程变更 | pull |
| 2.0.0 | 2.0.0 | def | abc | 🔄 本地修改 | push |
| 2.0.0 | 2.0.1 | — | — | ⬇️ 可更新 | pull |
| 2.0.1 | 2.0.0 | — | — | ⬆️ 未推送 | push |

**推送前门禁**: `cap-pack push` 自动执行 L0-L1 治理扫描 + schema 验证，失败则拦截。

### 16.4 经验积累：不在转换阶段生成

**关键设计决策**: EXPERIENCES/ 不在 `convert` 阶段自动生成。改为：

```
技能包完成任务 → 出问题 → 标记经验 (cap-pack experience mark)
                                      ↓
                              ┌───────┴───────┐
                              ↓               ↓
                     改良技能包 (学习回路)   记忆存档 (仅供参考)
```

本层只搭架子（记录格式 + 标记命令），路由和反馈回路留给后续 EPIC。

### 16.5 本地管理体系 CLI

```bash
# 同步
cap-pack pull              # 拉取官方包
cap-pack push              # 推送（自动治理门禁）
cap-pack status            # 本地 vs 远程差异
cap-pack sync              # 一键双向

# 转换
cap-pack convert            # Hermes 原生 → Cap-Pack
cap-pack convert --all      # 批量

# 管理
cap-pack list / --remote / --unpacked
cap-pack init               # 初始化 ~/.cap-pack/

# 经验积累（架子）
cap-pack experience mark --type pitfall
cap-pack experience list
```

### 16.6 与已有架构的关系

```text
EPIC-005 (治理引擎) ── 三层每层的质量门禁
    ↓
EPIC-006 (修复引擎) ── push 前自动修复
    ↓
EPIC-007 (本地管理) ── 三层 sync + convert + 管理 CLI
    ↓
EPIC-008 (经验路由) ── 未来: 经验反馈回路
```

### 16.7 实战参考

- `docs/EPIC-007-skill-to-cap-pack-converter.md` — 完整 EPIC 设计 (5 Phases · 16 Stories)
- `docs/project-report.json` — 7 EPIC 状态追踪 (EPIC-007: draft, 0/16 stories)


## 六、能力包健康诊断与量化测试方法论

> **2026-05-13 新增** — 基于 doc-engine 实战验证的包级健康测量体系

### 6.1 核心思想

能力包不仅是「打包技能」，更需要**持续可测量的健康度监控**。健康的包应该是：
- 技能之间语义内聚（簇结构合理）
- 每个技能有版本号、高 SQS 分
- 低分技能被及时降级或合并
- 整体健康度可通过自动化脚本验证

### 6.2 六维 KPI 体系

| KPI | 测量方式 | 健康阈值 | 权重 |
|:----|:---------|:--------:|:----:|
| **KPI-1** 平均 SQS | 包内所有技能的 SQS 总分 / 技能数 | ≥ 70 | 30% |
| **KPI-2** 低分率 | SQS < 60 的技能占比 | 0% | 20% |
| **KPI-3** 版本完整率 | 有版本号技能占比 | ≥ 80% | 15% |
| **KPI-4** 关联完整率 | SQS 的 S4 维度均分 | ≥ 10/20 | 15% |
| **KPI-5** 簇内聚度 | 树状索引的簇技能数标准差 | < 2.0 | 10% |
| **KPI-6** 技能总数 | 包内原子技能数量 | 按包类型定 | 10% |

### 6.3 综合健康指数 (CHI)

```
CHI = (avg_sqs/100 × 0.30) 
    + ((1 - low_rate) × 0.20)
    + (ver_rate × 0.15) 
    + (avg_s4/20 × 0.15)
    + max(0, 1 - cluster_std/5) × 0.10
    + max(0, 1 - |total-optimal|/20) × 0.10

阈值: ≥ 0.85 🟢 优秀 | ≥ 0.70 🟡 良好 | ≥ 0.55 🟠 需改进 | < 0.55 🔴 不合格
```

### 6.4 诊断四步法

每次要对某个包做健康评估时，按以下顺序执行：

```
Step 1: SQS 全量评分
→ python3 scripts/skill-quality-score.py --audit --json
→ 获取每个技能的五维分数

Step 2: 树状索引分析  
→ python3 scripts/skill-tree-index.py --pack <name> --json
→ 获取簇结构、合并潜力、冗余检测

Step 3: 生命周期审计
→ python3 scripts/skill-lifecycle-audit.py --audit
→ 检查技能新鲜度、依赖完整性

Step 4: 综合健康报告
→ python3 scripts/health-check.py [--json] [--gate]
→ 输出 6 KPI + CHI 指数
```

### 6.5 分层改造策略

当健康诊断发现问题时，按以下优先级处理：

| 优先级 | 问题类型 | 处理方式 | 效果 |
|:------:|:---------|:---------|:------|
| 🔴 P0 | 微技能 (SQS<60, <100行, 无版本) | **降级为经验** → 移入 EXPERIENCES/ | 立即提升平均分 |
| 🔴 P0 | 高度重叠技能 (>80% 内容重复) | **合并** → 整合为一个复合技能 | 减少维护成本 |
| 🟡 P1 | 版本号缺失 | **补充 version 字段** → semver 格式 | 提升版本完整率 |
| 🟡 P1 | 依赖关系未声明 (S4 低分) | **添加 depends_on** → 声明显式依赖 | 提升关联完整率 |
| 🟢 P2 | 标签不足/发现性差 | **补充 tags/triggers** | 提升可发现性 |

### 6.6 改造后验证

每次改造后必须重新运行健康检查，对比 before/after：

```bash
# Before
python3 scripts/health-check.py --json | python3 -c "import sys,json; print(json.load(sys.stdin)['chi'])"
# 执行改造...
# After
python3 scripts/health-check.py --json | python3 -c "import sys,json; print(json.load(sys.stdin)['chi'])"
# 期望: CHI 提升 ≥ 0.10
# 如果 CHI 下降 → 回滚
```

### 6.7 SRA 发现验证闭环

改造不能只看健康指标，还要验证 **SRA 运行时是否能正确发现改造后的技能**。

**诊断前先测 SRA:**
```bash
python3 ~/projects/hermes-cap-pack/scripts/sra-discovery-test.py --json
# 记录当前推荐命中率，作为改造基线
```

**改造后再测 SRA:**
```bash
python3 ~/projects/hermes-cap-pack/scripts/sra-discovery-test.py --json
# 对比命中率变化
```

**doc-engine Before SRA 数据（关键发现）:**

| 查询 | 问题 | 根因 |
|:-----|:------|:------|
| "生成PDF文档" → #1 **docx-guide** (不相关) | 错误推荐 | PDF 技能碎片化 + 无分类加权 |
| "写LaTeX论文" → #1 **latex-guide** (SQS=45.2) | 最低质技能排最前 | 微技能不应是独立 skill |
| "Markdown转PDF" → #1 **markdown-guide** (SQS=54.2) | 微技能占高位 | 降级为经验后自动消除 |

完整数据: `references/doc-engine-sra-test-data.md`

### 6.8 相关文档

| 文档位置 | 说明 |
|:---------|:------|
| `~/projects/hermes-cap-pack/packs/doc-engine/restructure-plan.md` | 完整改造方案、KPI公式、分层验证策略 |
| `~/projects/hermes-cap-pack/packs/doc-engine/cap-pack-v2.yaml` | 重组后包定义预览 |
| `~/projects/hermes-cap-pack/packs/doc-engine/health-gate.yaml` | 质量门禁配置示例 |
| `~/projects/hermes-cap-pack/packs/doc-engine/transformation-report.md` | 改造前后对比报告 （含 SRA 测试数据） |
| `~/projects/hermes-cap-pack/scripts/health-check.py` | 可复用健康检查脚本 |
| `references/ci-failure-recovery.md` | CI 失败恢复步骤（15+ 模块实战）
| `references/doc-engine-sra-test-data.md` | doc-engine 实战 SRA 测试原始数据
| `references/governance-fix-strategies.md` | 治理驱动修复策略 — 扫描→修复闭环设计（确定性+LLM 混合方案） |
| `references/standard-phase-transition-pattern.md` | **标准优先过渡模式** — EPIC 多 Phase 中标准阶段→实现阶段的标准化过渡流程，含 Phase 0→1 实战案例 |
| `references/post-extraction-quality-upgrade.md` | **后置质量升级执行模式** — EPIC-004 实战验证的 5 阶段模式 (基线→L2/L3→质量提升→合并→门禁固化), 含工具清单/实战陷阱/基线数据 |
| `references/layer-validation-pattern.md` | **三层结构验证模式** — validate-layers.py + frontmatter 标准 + CI 集成 |
| `references/extraction-commands.md` | 能力包提取命令速查（15+ 模块实战） |

**doc-engine 实战基线 (Before)**:
- CHI: 0.6029 🟠 | 平均 SQS: 64.0 | 低分率: 35% | 版本完整率: 59%
- 17 技能 → 目标 10 技能 + 11 经验 + 7 簇
- SRA 推荐命中率: ~85% | 错误推荐: 3/13 (23%) | 微技能占位: 3/13 (23%)

---

## 七、外部集成架构 (External Integration Pattern) 🔥

> **2026-05-14 新增** — 当需要扩展 Agent 能力但**不修改核心代码**时使用此模式。

### 7.1 核心理念

并非所有能力都需要修改 Agent 核心。许多扩展可以通过 **检测 + 监控 + 门禁 + 审计 + 行为约束** 的五层纯外部方案实现：

```
🚫 不修改 Agent 核心代码
🚫 不维护 .diff / .patch 文件（路径随版本改变）
🚫 不依赖特定版本的内部 API

✅ 通过已有扩展点集成（pre_flight / cron / skill 规则）
✅ 用自动化环境检测替代硬编码路径
✅ 用行为约束替代代码钩子
✅ 用事后审计兜底替代事前拦截
```

### 7.2 五层架构

```
┌────────────────────────────────────────────────────────┐
│  Layer 5: 行为约束 (Behaviors)                          │
│  Agent 自我约束规则，通过 context 注入 / 路径自检 / cron   │
│  无代码修改，纯行为规范                                  │
├────────────────────────────────────────────────────────┤
│  Layer 4: 审计层 (Audits)                               │
│  定期扫描 + 报告生成 → 发现异常时通知                    │
│  替代缺失的事前拦截，事后检测兜底                         │
├────────────────────────────────────────────────────────┤
│  Layer 3: 门禁层 (Gates)                                │
│  通过已有入口调用（pre_flight / skill-creator 流程等）    │
│  不修改被调用系统，只提供可选检查脚本                     │
├────────────────────────────────────────────────────────┤
│  Layer 2: 监控层 (Monitors)                             │
│  文件变更监控 / 版本变化检测 / 定时扫描                  │
│  纯外部进程，不侵入 Agent 运行                           │
├────────────────────────────────────────────────────────┤
│  Layer 1: 检测层 (Locate)                               │
│  跨系统自动检测 Agent 安装位置 / 版本 / 工具路径         │
│  所有外部脚本的先决条件                                  │
└────────────────────────────────────────────────────────┘
```

### 7.3 核心组件：hermes-locate.py

环境检测引擎是所有外部方案的基础：

| 检测项 | 方法 | 支持场景 |
|:-------|:------|:---------|
| Hermes home | `HERMES_HOME` env var → `~/.hermes` | git clone / pip / system |
| 源码位置 | 优先 git_clone，回退 pip_package → system → unknown | 4 种安装类型 |
| Hermes 版本 | `hermes --version` 或 `__init__.py` | 兼容性判断 |
| 工具路径 | `tools/file_tools.py` 等 | 定位目标文件 |
| Skills 目录 | 主目录 + external_dirs + profile skills | 全量技能扫描 |
| 补丁状态 | 检查已应用 vs 未应用的修改 | 增量判断 |

```bash
python3 hermes-locate.py              # JSON 输出
python3 hermes-locate.py --format human  # 人类可读
python3 hermes-locate.py --check-only   # exit 0/1 就绪判定
```

### 7.4 行为约束模式

行为约束是纯外部方案中最柔性的机制——通过规则约束 Agent 行为：

| 约束类型 | 示例 | 执行方式 |
|:---------|:-----|:---------|
| **context 注入** | delegate_task 时附加「如需修改 skill 请先加载 skill-creator」 | 每次委托时手动注入 |
| **路径自检** | write_file/patch 前检查目标是否为 skill 目录 | 每次文件操作前自检 |
| **操作后验证** | 修改 skill 后自动运行 SQS 评分 | 每次 skill 操作后 |
| **定时自省** | cron 每日检查 skill 目录完整性和脚本一致性 | 定时触发 |

cap-pack.yaml 中通过 `integration.behaviors` 声明：

```yaml
integration:
  behaviors:
    - id: subagent-skill-guard
      rule: "在 delegate_task context 中注入 skill 操作约束：如需修改 skill 必须先加载 skill-creator"
      enforcement: self_discipline
      trigger_condition: "每次调用 delegate_task 时检查任务描述"
    - id: script-integrity-check
      rule: "learning-workflow 等关键脚本应定期校验 hash，防止被意外覆盖"
      enforcement: cron_audit
      trigger_condition: "每日 6:00 检查关键脚本 hash"
```

### 7.5 什么时候用纯外部？什么时候必须改核心？

| 场景 | 推荐方案 | 理由 |
|:-----|:---------|:------|
| 增强 pre_flight 检测 | ✅ 纯外部 | pre_flight 设计为可扩展脚本管道 |
| 约束子代理行为 | ✅ 纯外部 | delegate_task 有 context 参数可注入 |
| 监控 curator 质量 | ✅ 纯外部 | 事后审计足够 |
| CLI 安装质量门禁 | ✅ 纯外部 | 安装后验证脚本 |
| 学习脚本完整性 | ✅ 纯外部 | 定时校验 hash |
| 拦截 write_file 到 skill 目录 | 部分外部(行为约束+审计) | 文件工具无钩子系统 |
| 修改 curator 内部逻辑 | ❌ 需改核心 | 后台进程无外部注入点 |
| 修改 skill_manage 工具行为 | ❌ 需改核心 | 工具注册表无外部钩子 |

### 7.6 实战参考：skill-quality 能力包

`packs/skill-quality/` 是纯外部方案的原型实现：

| 层 | 脚本 | 状态 |
|:---|:-----|:----:|
| Locate | `scripts/hermes-locate.py` | ✅ 完成 |
| Gates | `scripts/*-gate.py` (×4) | 🚧 骨架 |
| Audits | `scripts/*-audit.py` (×2) | 🚧 骨架 |
| Monitors | `scripts/*-monitor.py` (×2) | 🚧 骨架 |
| Behaviors | `cap-pack.yaml` 声明 | ✅ 完成 |

### 7.7 与适配器模式的关系

| 维度 | 适配器 (Adapter) | 外部集成 (External Integration) |
|:-----|:----------------|:-------------------------------|
| 目标 | 安装能力包到不同 Agent | 不修改核心，扩展 Agent 能力 |
| 修改方式 | 代码层写入目标路径 | 行为层 + 脚本层 |
| 风险 | 可能破坏目标 Agent 配置 | 零侵入 |
| 维护 | 需跟踪 Agent 版本变化 | 低维护成本 |
| 覆盖度 | 100%（可做任何事） | 60-90%（受限于扩展点） |

---

## 七、实战陷阱 ⚠️

### 格式设计阶段

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 过度设计 — 追求完美格式 | 项目卡在 Phase 1 出不来 | 先最小可用（只含 skills + experiences），再逐步迭代 |
| 分割维度不统一 | 模块间边界模糊 | 用「四问测试」验证每个模块边界 |
| 忽略 MCP 差异 | 适配时发现某些 Agent 不支持 | 在 compatibility 中声明每项能力 |
| **包内 SKILLS 只有 stub 指针文件** | 跨 Agent 移植时只能看不能用 | 必须用 `extract-pack.py` 提取完整 skill（含 references/scripts/templates/checklists）。stub 文件只适用于纯文本 skill。 |
| **YAML 日期未引号包裹** | `created: 2026-05-13` 被 YAML 解析为 `datetime.date` 对象 → JSON Schema 验证失败（期望 string） | **`created: '2026-05-13'`** 日期字段务必加引号！YAML 自动解析 ISO 日期为 date 对象 |
| **cap-pack.yaml 缺少 `type` 字段** | `validate-pack.py` 报错「type 必须为 capability-pack」| manifest 必须包含 `type: capability-pack` 和 `compatibility.agent_types`。见下方 §十 的字段要求。 |
| **`.yaml` 文件实际内容为 Markdown** | CI YAML lint 报语法错误 | 文档参考文件（检查清单、流程说明）使用 `.md` 扩展名而非 `.yaml`。`.yaml` 应仅用于纯 YAML 数据文件。 |

### 适配层阶段

| 陷阱 | 后果 | 预防 |
|:------|:------|:------|
| 假设所有 Agent 都有 skill_manage | Claude Code 无法自动创建技能 | 适配器用文件系统直接写入 |
| 忽略 config 格式差异 | Hermes 用 YAML，Claude 用 JSON | 适配器内做格式转换 |
| 未处理 on_activate 钩子 | 安装后缺少依赖 | 每个适配器都执行钩子 |

### 改造阶段

| 陷阱 | 后果 | 预防 |
|:------|:------|:------|
| **改造后忘记刷新 SRA 索引** | SRA 仍推荐旧 skill（如已降级的微技能） | 改造后立即 `curl -X POST http://127.0.0.1:8536/refresh` 或 `sra index --rebuild`。SRA 有 1h 自动刷新周期，等不及。 |
| **只改 cap-pack.yaml 不改实际 skill 文件** | 能力包结构新但实际 skill 是旧的 | `extract-pack.py` 提取后再 `validate-pack.py` 验证，确保包内文件与实际一致 |
| **降级微技能后未确认 SRA 不再推荐** | 用户仍被引导到低质技能 | 改造后运行 `scripts/sra-discovery-test.py --json` 验证推荐列表已更新 |
| **合并 PDF 技能后旧技能文件未标记退役** | 新旧并存，SRA 两个都推荐 | 旧 skill 标记 `deprecated` 或移入 `_archived/` 目录。SRA 扫描时自动剔除 |

### 文档排版约定

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **使用 ASCII 字符画替代图示** | 主人明确纠正「不要使用 asc 字符画，使用 mermaid 画 uml 图」。ASCII art 在 markdown 中无法在 GitHub 等平台渲染、不可缩放、不易维护 | 所有架构图/流程图/序列图使用 **Mermaid** (` ```mermaid`) 而非 ASCII 字符画。Mermaid 支持 `flowchart` / `sequenceDiagram` / `classDiagram` / `stateDiagram` 等类型。 |
| **README CLI 命令参考表不加前缀** | 用户看到 `install <pack>` 可能直接输入 `install` 而非 `cap-pack install`，造成「command not found」错误。主人明确纠正「readme的cli命令参考建议使用完整命令」 | CLI 命令参考表必须使用**完整命令前缀**。如 `cap-pack install <dir>`，不能只写 `install <dir>`。可在表前加提示说明 alias 和完整入口。 |
| **README 项目身份表信息过时** | CLI 入口、Schema 版本、依赖列表等字段随项目演进但未同步更新 | 每次 EPIC/Spec 完成后检查 `项目身份` 表的 7 个字段：CLI 入口 / Schema 版本 / Python 版本 / 依赖 / 仓库 / 作者 / 目的 |

### 迭代阶段

| 陷阱 | 后果 | 预防 |
|:------|:------|:------|
| 更新通知轰炸 | 主人厌烦 | PATCH 级别静默更新，MAJOR 才通知 |
| 跨模块级联更新不回滚 | 部分 Agent 更新成功部分失败 | 用 `on_deactivate` + 备份实现原子性 |
| 经验与技能脱节 | 经验说 A 但技能步骤已是 B | SKILL.md 中加 `experience_ref` 字段显式关联 |

### 标准优先顺序陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **构建合规检测器时先写检测器再定义标准** | 检测维度模糊、标准与检测逻辑不一致、Owner 质疑「你到底在检测什么」 | **标准必须定义在检测器之前**。合规检测需要明确的判定基准（level/维度/阈值），这些必须在编写检测器之前以文档形式锁定。先写 `STANDARD.md` → Owner 批准 → 再构建检测器。参见 §13.6 统一标准框架。 |
| **SPEC 中合规描述过于概括**（如仅写「检查合规性」而无具体维度） | Owner 无法判断检测范围、实现过程需要反复澄清 | 合规相关 SPEC 必须写明「检查哪几层、每层什么标准、阈值多少」。参见 SPEC-5-1 的教训。 |

---

## 八、验证清单

启动模块化项目前检查：

- [ ] 四支柱可行性框架已完成（分割/管理/迭代/适配）
- [ ] 候选模块清单已用「四问测试」验证
- [ ] cap-pack.yaml 格式已定稿
- [ ] 至少一个模块包含真实经验（非空 EXPERIENCES/）
- [ ] 每个适配器有显式的「能力覆盖矩阵」
- [ ] 迭代闭环的触发条件已明确
- [ ] 回滚机制已建立（安装前备份）

---

## 九、相关 Skill

| Skill | 用途 |
|:------|:------|
| `sdd-workflow` | Spec 生命周期管理 + 状态机 |
| `deep-research` | 四支柱框架的行业调研阶段 |
| `development-workflow-index` | 选择开发路径的决策树 |
| `writing-plans` | 模块实现的实施计划 |
| `self-capabilities-map` | 盘点现有 Agent 能力存量 |
| `skill-creator` | 个体技能创建与 SQS 质量门禁 |

---

## 十、工具链参考 — 能力包操作 + 诊断套件

> **2026-05-13 新增** — 能力包操作的三件套 + 健康诊断套件

### 操作工具

| 工具 | 路径 | 用途 |
|:-----|:------|:------|
| `extract-pack.py` | `~/projects/hermes-cap-pack/scripts/extract-pack.py` | 从 `~/.hermes/skills/<name>` 提取完整 skill 到 cap-pack 格式（含 linked files） |
| `validate-pack.py` | `~/projects/hermes-cap-pack/scripts/validate-pack.py` | 验证能力包完整性：manifest 格式 + 文件存在 + 交叉引用 |
| `install-pack.py` (v2.0) | `~/projects/hermes-cap-pack/scripts/install-pack.py` | **多 Agent 安装工具**。支持 `--target hermes|opencode|auto` 指定目标，auto 模式自动检测可用 Agent。子命令: `status` / `remove` / `verify`。含 `--dry-run` 预览、`--skip-deps` 跳过依赖。详见 `references/install-cli-v2-multi-agent.md`。 |
| `skill-tree-index.py` | `~/projects/hermes-cap-pack/scripts/skill-tree-index.py` | 三层树状索引生成器 + 合并潜力分析 + 系统健康度审计。`--pack` 查看单包、`--consolidate` 合并建议、`--health` 全量健康度、`--sra` SRA 兼容输出（含 pack/cluster/siblings/avg_sqs） |
| `skill-quality-score.py` | `~/projects/hermes-cap-pack/scripts/skill-quality-score.py` | SQS 五维质量评分（结构/内容/时效/关联/发现）。**v2.0** 新增 SQLite 持久化（`--save`/`--init-db`/`--history <skill>`），`scores`+`score_history` 双表支持历史趋势追踪 |
| `skill-lifecycle-audit.py` | `~/.hermes/skills/skill-creator/scripts/skill-lifecycle-audit.py` | 生命周期审计 + deprecate/revive 管理 |
| `health-dashboard.py` | `~/projects/hermes-cap-pack/scripts/health-dashboard.py` | Chart.js 健康趋势仪表盘生成器。从 SQS DB 读取数据，生成 HTML（折线图/雷达图/低分排行/退化检测）。`--cron` 静默模式配合 `health-report.py` 每周联动 |
| `merge-suggest.py` | `~/projects/hermes-cap-pack/scripts/merge-suggest.py` | 合并建议引擎。内容相似度分析 + BMAD 冗余检测 + 微技能识别。⚠️ BMAD/MICRO 标记 `action=inspect` 需手动按 `references/phase3-merge-execution-example.md` 执行，`--apply` 只追加合并标注 |
| `sqs-sync.py` | `~/projects/hermes-cap-pack/scripts/sqs-sync.py` | SQS → SRA 质量分同步器。每 6 小时 cron 同步 200 个 skill 的 SQS 分到 `~/.sra/data/sqs-scores.json`。`--dry-run` 预览、`--no-quality` 禁用加权 |

### 健康诊断工具

| 工具 | 路径 | 用途 |
|:-----|:------|:------|
| `health-check.py` | `~/projects/hermes-cap-pack/scripts/health-check.py` | 包级健康检查 — 6 KPI + CHI 综合健康指数，支持 `--json`(机器解析) 和 `--gate`(门禁模式) |
| `health-gate.yaml` | `~/projects/hermes-cap-pack/packs/{name}/health-gate.yaml` | 质量门禁声明（min-sqs/zero-low-score/full-version/chi-index） |

### 快速使用

```bash
# 提取 skill → 能力包
cd ~/projects/hermes-cap-pack
python3 scripts/extract-pack.py pdf-layout --pack doc-engine --update-manifest

# 验证包完整性
python3 scripts/validate-pack.py packs/doc-engine

# 预览安装
python3 scripts/install-pack.py packs/doc-engine --dry-run

# 包级健康检查
python3 scripts/health-check.py                    # 人类可读报告
python3 scripts/health-check.py --json             # 机器解析（CI/CD 用）
python3 scripts/health-check.py --gate && echo "✅" # 门禁模式
```

---

## 十一、适配器验证门禁模式 (Verification Gate Pattern)

> **2026-05-14 新增** — 基于 HermesAdapter 实战总结的验证门禁设计模式

### 11.1 问题

能力包安装后，如何确保安装结果是可用的？安装引擎可能成功复制了文件，但：
- skill 的 SKILL.md 缺少 YAML frontmatter（无效技能）
- 脚本文件没有可执行权限（无法运行）
- 依赖包未安装（运行时失败）
- 引用文件缺失（经验丢失）

传统的「安装成功 = 文件复制完成」定义过于脆弱。

### 11.2 方案：四层验证门禁

在安装流程中插入 **验证门禁步骤**，在 tracking 之前、post_install 之后：

```text
Step 0:  依赖检查（非阻塞警告）
Step 1:  创建快照（用于回滚）
Step 2-5: 安装各项组件（skills/scripts/references/MCP）
Step 6:  post_install 执行
Step 7:  ⚠️ 验证门禁 ← 新增
         ├── ① SKILL.md 存在 + YAML frontmatter 完整性
         ├── ② 脚本文件存在 + 可执行权限
         └── ③ 引用文件存在
         失败 → 自动从快照回滚 + 报错
Step 8:  记录跟踪
Step 9:  清理快照
```

### 11.3 实现模板

```python
def _verify_installation(self, pack: CapPack) -> dict:
    """安装后验证门禁
    Returns: {"passed": bool, "checks": [], "failures": []}
    """
    checks, failures = [], []

    # ① 检查 SKILL.md + YAML frontmatter
    for skill in pack.skills:
        skill_file = pack.pack_dir / "SKILLS" / skill.id / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text()
            if content.startswith("---"):
                try:
                    import yaml
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        fm = yaml.safe_load(parts[1])
                        if isinstance(fm, dict) and ("id" in fm or "name" in fm or "description" in fm):
                            checks.append(f"skill {skill.id}: frontmatter 完整")
                        else:
                            failures.append(f"skill {skill.id}: frontmatter 缺 id/name/description")
                except Exception as e:
                    failures.append(f"skill {skill.id}: frontmatter 解析失败: {e}")
            else:
                failures.append(f"skill {skill.id}: 无 frontmatter (---)")
        else:
            failures.append(f"skill {skill.id}: SKILL.md 不存在")

    # ② 检查脚本可执行性
    manifest = pack.manifest
    for entry in manifest.get("install", {}).get("scripts", []):
        dst = Path(entry["target"]).expanduser()
        if dst.exists():
            if not os.access(str(dst), os.X_OK):
                failures.append(f"script {dst.name}: 无可执行权限")
            else:
                checks.append(f"script {dst.name}: 可执行")
        else:
            failures.append(f"script {dst.name}: 文件不存在")

    return {"passed": len(failures) == 0, "checks": checks, "failures": failures}
```

### 11.4 集成到 install 流程

```python
def install(self, pack, dry_run=False, skip_deps=False):
    result = AdapterResult(success=True, pack_name=pack.name, action="install")

    # Step 0: 依赖检查（非阻塞）
    missing = self._check_dependencies(pack, skip_deps)
    if missing:
        result.warnings.append(f"缺失依赖包: {', '.join(missing)}")

    # Step 1: 快照
    snapshot_id = SnapshotManager.create(pack.name)

    try:
        # Step 2-6: 安装各项组件 + post_install
        ...

        # Step 7: 验证门禁
        verify = self._verify_installation(pack)
        if not verify["passed"]:
            for f in verify["failures"]:
                result.errors.append(f"验证失败: {f}")
            # 自动回滚
            SnapshotManager.restore(snapshot_id)
            result.warnings.append("验证门禁未通过，已自动回滚")
            result.success = False
            return result

        # Step 8: 记录跟踪
        # Step 9: 清理快照
    except Exception as e:
        SnapshotManager.restore(snapshot_id)
        raise
```

### 11.5 依赖检查模式

```python
def _check_dependencies(self, pack, skip_deps=False):
    """检查包级依赖 — 返回缺失列表（非阻塞）"""
    if skip_deps or not pack.depends_on:
        return []

    tracked = self._load_installed()  # 读取 installed_packs.json
    missing = []
    for dep_name, dep_info in pack.depends_on.items():
        if dep_name not in tracked:
            reason = dep_info.get("reason", "") if isinstance(dep_info, dict) else ""
            msg = f"{dep_name} ({reason})" if reason else dep_name
            missing.append(msg)
    return missing
```

### 11.6 关键设计决策

| 决策 | 选项 | 选择理由 |
|:-----|:------|:---------|
| 依赖检查阻塞 vs 非阻塞 | **非阻塞**（仅警告） | 依赖可能通过其他方式满足，不因缺失依赖阻塞安装流程 |
| 验证失败阻塞 vs 非阻塞 | **阻塞+回滚** | 安装破损技能比不安装更危险 |
| 回滚策略 | **快照恢复** | 安装前快照完整状态，失败时原子恢复 |
| 验证范围 | skill frontmatter + 脚本权限 | 覆盖最常见安装失败模式 |
| `depends_on` 数据来源 | **CapPack.depends_on 字段** | 与 manifest 分离，适配器直接访问结构化字段 |

### 11.7 实战陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 测试 fixture 的 SKILL.md 无 frontmatter | 验证门禁拦截导致全部测试失败 | fixture 必须生成 `---\nid: ...\nname: ...\ndescription: ...\n---\n` 格式 |
| 验证门禁中检查 source 而非 target 路径 | 永远提示「文件不存在」 | 检查 `install.scripts[].target` 展开后的路径 |
| tracking 未记录 script_targets | verify() 无法找到脚本文件做可执行检查 | 安装时在 tracking 中保存 `script_targets: [str]` 列表 |
| `depends_on` 只写在 manifest 未传给 CapPack 构造器 | 依赖检查永远返回空 | 解析 manifest 后显式 `depends_on=manifest.get("depends_on", {})` |

### 11.8 测试模式

验证门禁的核心测试有 4 个覆盖维度：

| 测试 | 验证点 |
|:-----|:--------|
| `test_verify_pass` | 正常包 → 验证通过 |
| `test_verify_no_frontmatter` | 无 frontmatter → 验证失败 |
| `test_verify_script_not_executable` | 脚本不可执行 → 验证失败 |
| `test_verify_with_install_flow` | 验证失败 → install 自动回滚 |

参考实现：`scripts/tests/test_hermes_adapter.py` 中的 `TestVerificationGate` 类。

---

## 十二、多 Agent CLI 架构模式

> **2026-05-14 新增** — 基于 install-pack.py v2.0 实战总结的多 Agent 安装 CLI 设计模式

### 12.1 问题

当能力包需要支持多个 Agent 目标时（Hermes / OpenCode / Codex / Claude），单一目标的 CLI 不够灵活。需要一种模式让用户轻松指定目标，且能自动检测可用环境。

### 12.2 方案：Adapter Registry + --target 模式

```text
                              ┌──────────────────┐
                              │   CLI (argparse)  │
                              │  --target hermes  │
                              │  --target opencode│
                              │  --target auto    │
                              └────────┬─────────┘
                                       │
                              ┌────────┴────────┐
                              │  Adapter Registry│
                              │  name → class    │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ↓                  ↓                  ↓
            HermesAdapter       OpenCodeAdapter     CodexAdapter
          (is_available ✓)    (is_available ✓)    (is_available ✗)
```

### 12.3 实现模板

```python
# ── 适配器注册表 ──
ADAPTERS = {
    "hermes": HermesAdapter,
    "opencode": OpenCodeAdapter,
}

def get_adapter(name: str):
    cls = ADAPTERS.get(name)
    if cls is None:
        print(f"❌ 未知目标: {name}")
        sys.exit(1)
    return cls()

def detect_available() -> list[str]:
    """自动检测可用的 Agent 环境"""
    available = []
    for name, cls in ADAPTERS.items():
        adapter = cls()
        if adapter.is_available:
            available.append(name)
    return available

def cmd_install(pack_dir, target, dry_run, skip_deps):
    # 确定目标
    if target == "auto":
        targets = detect_available()
        if not targets:
            print("❌ 未检测到可用的 Agent 环境")
            sys.exit(1)
        print(f"🔍 自动检测到: {', '.join(targets)}")
    else:
        targets = [target]

    # 逐个安装
    for tgt in targets:
        adapter = get_adapter(tgt)
        if not adapter.is_available and not dry_run:
            print(f"   ⚠️  {tgt} 环境不可用，跳过")
            continue
        result = adapter.install(pack, dry_run=dry_run, skip_deps=skip_deps)
        ...
```

### 12.4 CLI 子命令设计

使用 argparse subparsers 实现 install / status / remove / verify 四个子命令：

```python
def main():
    # 兼容旧用法: install-pack.py <pack-dir> [--target ...]
    if sys.argv[1] not in ("status", "remove", "verify", "-h"):
        pack_dir = sys.argv[1]
        # 手动解析 --target, --dry-run, --skip-deps
        cmd_install(pack_dir, target, dry_run, skip_deps)
        return

    # 子命令模式
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    p_status = subparsers.add_parser("status")
    p_status.add_argument("--target", default="hermes")
    
    p_remove = subparsers.add_parser("remove")
    p_remove.add_argument("pack_name")
    p_remove.add_argument("--target", default="hermes")
    ...
```

### 12.5 Adapter API 统一要求

所有适配器必须接受相同的 install() 签名，确保 CLI 可以透明切换：

```python
class HermesAdapter:
    def install(self, pack: CapPack, dry_run: bool = False, skip_deps: bool = False) -> AdapterResult: ...

class OpenCodeAdapter:
    def install(self, pack: CapPack, dry_run: bool = False, skip_deps: bool = False) -> AdapterResult: ...
```

| 参数 | 类型 | 说明 |
|:-----|:------|:------|
| `pack` | CapPack | 已解析的能力包 |
| `dry_run` | bool | 预览模式，不实际写入 |
| `skip_deps` | bool | 跳过依赖检查 |

### 12.6 实战陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| `install()` 签名不一致 | CLI 调用时报 `unexpected keyword argument` | 所有适配器必须统一 `(pack, dry_run, skip_deps)` 签名 |
| auto 检测到环境但实际不可写 | 安装到一半失败 | 在 `is_available` 中做完整可写性检查 |
| 目录不存在时 `mkdir()` 不传 `exist_ok=True` | 多包源目录冲突 → `FileExistsError` | 始终使用 `exist_ok=True` |

### 12.7 参考实现

完整实现见 `~/projects/hermes-cap-pack/scripts/install-pack.py` (v2.0)。

集成测试见 `scripts/tests/test_hermes_adapter.py` 中的 `TestMultiAgentInstall` 类。

---

## 十三、行业生态与差距分析 (Industry Landscape & Gap Analysis)

---

## 十四、治理修复引擎架构 (Governance Fix Engine Architecture) 🔥

> **2026-05-16 新增** — 基于 EPIC-006 深度设计和代码库分析的经验沉淀。  
> **核心问题**: 治理引擎能「发现问题」后，如何「自动修复问题」？  
> **核心决策**: 确定性脚本 vs LLM workflow vs **混合方案**的选择框架和架构模式。

### 14.1 问题背景

EPIC-005 交付的治理引擎能对能力包进行 L0-L4 四层扫描，但 **不能自动修复**。跨包扫描结果显示：

| 指标 | 值 | 目标 |
|:-----|:---|:----|
| 平均合规分 | 79.6 | ≥ 90 |
| 100% 出现的问题 | 4 项 | 0 |
| 自动修复覆盖 | 0% | ≥ 80% |

手动修复 18 个包的问题需要 3+ 小时。需要一条 `skill-governance fix` 命令来闭环检测→修复循环。

### 14.2 方案选择框架

构建修复引擎时面临一个核心决策：**用确定性脚本还是 LLM workflow**？以下框架帮助选择：

#### 步骤 1: 按修复类型分类

每条规则的可自动化程度决定了最适合的方式：

| 修复类型 | 特征 | 示例规则 | 推荐方式 |
|:---------|:-----|:---------|:---------|
| 🟢 **确定性** | 修复动作唯一，可模板化 | 创建缺失文件、填充空字段 | **脚本** |
| 🟢 **算法性** | 可用数学/统计方法解决 | Jaccard 聚类、相似度匹配 | **脚本** |
| 🟡 **启发式** | 需一定上下文推断但可建模 | 从名称/描述推分类 | **脚本 + 简单规则** |
| 🧠 **LLM 辅助** | 需语义理解才能正确修复 | 推断 skill 用途、验证链接有效性 | **LLM** |

#### 步骤 2: 量化评估

```text
评估维度:
  - 可自动化比例: 70%+ → 优先脚本
  - 准确率要求: 100% → 脚本; 可接受 80-90% → LLM
  - 执行频率: 每天多次 → 脚本; 偶尔 → LLM
  - 成本敏感: 高 → 脚本; 低 → LLM

最终选择:
  ✅ 确定性问题的修复不值得 LLM 调用
  ✅ 混合方案= 脚本处理 70% + LLM 处理 30%
  ❌ 纯 LLM workflow = 90 次 LLM 调用/全量修复 → 过度设计
  ❌ 纯脚本 = 无法处理语义问题 (classification推断, 断链修复)
```

#### 步骤 3: 分层修复架构

```text
┌─────────────────────────────────────────────────────┐
│              CLI: skill-governance fix <pack>         │
│  --dry-run (预览) / --apply (执行) / --llm-assist    │
├─────────────────────────────────────────────────────┤
│            Fix Dispatcher (策略路由)                   │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ 确定性修复  │  │ 算法修复      │  │ LLM 辅助修复  │   │
│  │ FixRule    │  │ Algorithmic  │  │ LLMFixRule  │   │
│  │ (模板生成)  │  │ (Jaccard聚类) │  │ (语义推断)    │   │
│  └──────────┘  └──────────────┘  └──────────────┘   │
├─────────────────────────────────────────────────────┤
│          基础设施层 (复用已有扫描器/适配器)               │
│  Scanner · CapPackAdapter · 规则集 · dry_run/apply   │
└─────────────────────────────────────────────────────┘
```

### 14.3 FixRule 架构模式

核心数据模型是 **FixRule 抽象基类 + FixDispatcher 路由**：

```python
@dataclass
class FixAction:
    rule_id: str              # 对应扫描规则的 ID
    action_type: str          # create / modify / delete
    target_path: str          # 目标文件路径
    old_content: str          # 原内容（用于 diff）
    new_content: str          # 新内容（用于 diff）
    description: str          # 人工可读描述

@dataclass
class FixResult:
    rule_id: str
    dry_run: bool
    applied: int = 0          # 成功修复数
    skipped: int = 0          # 已合规跳过（幂等）
    errors: list[str] = field(default_factory=list)
    actions: list[FixAction] = field(default_factory=list)

class FixRule(ABC):
    rule_id: str
    description: str
    severity: str
    
    @abstractmethod
    def analyze(self, pack_path: str, scan_result: dict) -> FixResult:
        """分析包，生成修复计划（dry_run 模式）"""
    
    @abstractmethod
    def apply(self, pack_path: str, scan_result: dict) -> FixResult:
        """执行修复"""
    
    def _backup(self, path: str) -> str: ...
    def _is_already_fixed(self, pack_path: str) -> bool: ...

class FixDispatcher:
    """Rule ID → FixRule 路由"""
    def register(self, rule: FixRule): ...
    def get_rule(self, rule_id: str) -> Optional[FixRule]: ...
    def dispatch(self, report: dict, rules_filter: list[str]=None) -> list[FixResult]: ...
```

### 14.4 代码库分析模式（为修复引擎做设计时）

在构建修复引擎前，必须系统化分析现有代码库，确定哪些可以复用、哪些需要新建。分析五步法：

#### 第 1 步：扫描基础设施分析

| 需要回答的问题 | 检查内容 |
|:--------------|:---------|
| 扫描结果是什么格式？ | `ScanReport.to_dict()` → 含 `layers[].checks[].rule_id/details/suggestions` |
| 扫描如何触发？ | `_build_report()` 在 CLI 中，CLI 外无直接入口 |
| 已失败的检查是什么格式？ | `CheckResult` dataclass → `details` 字典含修复所需上下文 |

#### 第 2 步：适配器/编辑器分析

| 需要回答的问题 | 检查内容 |
|:--------------|:---------|
| 已有适配器的 suggest/dry_run/apply 能力？ | CapPackAdapter: 扫描+Jaccard+写入能力 |
| 哪些模式可以直接复用？ | `_parse_frontmatter()`, `_jaccard_similarity()`, `PackManifest.from_file()` |
| 哪些模式需要新建？ | 对不同文件的读写；修复而不是安装的 apply |

**关键问题**：适配器是用于安装的，修复引擎需要的是**编辑**能力——两者相似但不同。修复引擎复用适配器的数据提取和写入模式，但逻辑是修改现有文件而非安装新文件。

#### 第 3 步：已有修复脚本分析

| 脚本 | 可复用模式 |
|:-----|:----------|
| `fix-pack-metadata.py` | YAML 读/修改/写模式；幂等性检查 |
| `fix-low-score-skills.py` | Frontmatter 正则注入；YAML 有效性验证 |
| `fix-l2-frontmatter.py` | 启发式类型检测；内容关键词推断 |

**提取通用模式**：
1. YAML RMW: `read → yaml.safe_load() → modify → yaml.dump() → write`
2. Frontmatter regex: `^(---\\n)(.*?)(\\n---\\n)` + re.DOTALL
3. Idempotency: `if already_fixed: skip`
4. Heuristics: keyword → classification mapping

#### 第 4 步：CLI 分析

| 问题 | 答案 |
|:-----|:------|
| CLI 命令注册方式？ | `@app.command()` in Typer |
| 现有命令？ | `scan`, `watcher`, `rules` |
| fix 命令放哪？ | **cli/main.py 新增** `@app.command("fix")` |
| 复用哪些函数？ | `_load_skills_from_pack()`, `_build_report()` |

#### 第 5 步：依赖与测试分析

| 问题 | 答案 |
|:-----|:------|
| 需要新增 pip 依赖？ | **零新增** — pyyaml + typer + rich + 标准库足够 |
| 测试 fixture 模式？ | `tmp_path` + `monkeypatch` 创建模拟包结构 |
| 测试位置？ | **包内 `tests/`** 而非 `scripts/tests/` |

### 14.5 分阶段实施模式

修复引擎推荐按 4 个 Phase 渐进实施：

```text
Phase 0: 基础设施 (3 Stories, ~4h)
  FixRule 抽象层 + Dispatcher + CLI fix 子命令 + 报告格式
  → 产出: fixer/base.py, fixer/dispatcher.py, CLI 扩展

Phase 1: 确定性修复 (4 Stories, ~6h)
  F001 SKILL.md 生成 + F007 triggers 提取 + H001/H002 树簇优化 + F006 启发式分类
  → 产出: fixer/rules/ 下 5 个 fix 规则
  → 覆盖: ~70% 的扫描规则有对应修复

Phase 2: LLM 辅助修复 (3 Stories, ~4h)
  LLM 辅助修复框架 + E001/E002 SRA 元数据 + E005 断链修复
  → 产出: fixer/llm_assist.py + 3 个 LLM 规则
  → 覆盖: ~95% 的规则有对应修复

Phase 3: 批量工作流 (2 Stories, ~2h)
  fix --all 批量执行 + 修复前后对比报告
  → 产出: fixer/batch.py
```

### 14.6 修复引擎代码库分析五步法 🔥

> **2026-05-16 新增** — 在构建修复引擎前必须系统化分析现有代码库。以下五步法确保找到所有可复用资产，避免重复造轮子。

在创建新的 FixRule 前，按此五步法分析代码库：

#### 第 1 步：扫描基础设施分析

| 需要回答的问题 | 检查内容 |
|:--------------|:---------|
| 扫描结果是什么格式？ | `ScanReport.to_dict()` → 含 `layers[].checks[].rule_id/details/suggestions` |
| 扫描如何触发？ | `_build_report()` 在 CLI 中，CLI 外无直接入口 |
| 已失败的检查是什么格式？ | `CheckResult` dataclass → `details` 字典含修复所需上下文 |

#### 第 2 步：适配器/编辑器分析

| 问题 | 检查内容 |
|:-----|:---------|
| 已有适配器的 suggest/dry_run/apply 能力？ | CapPackAdapter: 扫描+Jaccard+写入能力 |
| 哪些模式可以直接复用？ | `_parse_frontmatter()`, `_jaccard_similarity()`, `PackManifest.from_file()` |
| 哪些需要新建？ | 对不同文件的读写；修复（编辑现有文件）而非安装（新建文件） |

**关键区别**：适配器用于安装（新建文件），修复引擎需要编辑（修改现有文件）。两者复用数据提取和写入模式，但逻辑不同。

#### 第 3 步：已有修复脚本分析

逐个分析项目中已有的 `fix-*.py` 脚本，提取通用模式：

```text
YAML 读/修改/写模式:  read → yaml.safe_load() → modify → yaml.dump() → write
Frontmatter 正则:     ^(---\\n)(.*?)(\\n---\\n) + re.DOTALL
幂等性检查:           if already_fixed: skip（否则反复跑产生重复修改）
启发式推断:           keyword/keyphrase → classification mapping
```

#### 第 4 步：CLI 分析

| 问题 | 答案 |
|:-----|:------|
| CLI 命令注册方式？ | `@app.command()`（Typer）或 `parser.add_parser()`（argparse） |
| 新命令放哪？ | 与现有命令同文件（如 `cli/main.py`），复用包加载/扫描函数 |
| 复用哪些函数？ | `_load_skills_from_pack()`, `_build_report()` 等基础设施 |

#### 第 5 步：依赖与测试分析

| 问题 | 答案 |
|:-----|:------|
| 需要新增 pip 依赖？ | **尽量零新增** — 标准库 + 项目已有依赖通常足够 |
| 测试 fixture 模式？ | `tmp_path` + `monkeypatch` 创建模拟场景 |
| 测试位置？ | 包内 `tests/` 优先于独立脚本目录 |

**实战案例**：EPIC-006 的深度代码库分析使用了此五步法，发现 7 个关键可复用资产、零新增 pip 依赖。详见 `docs/research/SPEC-6-1-research.md`。

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **把所有修复都做成 LLM** | 90 次 LLM 调用/全量修复，浪费资源 | 先用五步分析确定可自动化程度，70% 是确定性的 |
| **扫描器和修复器紧耦合** | 扫描数据结构变了修复也得改 | FixRule 接收 `dict`（序列化的 CheckResult），而非内部对象 |
| **忽略幂等性** | 反复跑 fix 产生重复修改 | 每个 FixRule 必须实现 `_is_already_fixed()` 检查 |
| ❌ 不做 dry_run 预览 | 批量修复出问题难以回滚 | `dry_run` 输出 unified diff，主人确认后再 `apply` |
| ❌ 复制现有 fix 脚本而非提取模式 | 新脚本和旧脚本不一致，维护成本翻倍 | 提取 YAML RMW/frontmatter/幂等性模式为通用工具函数 |
| ❌ FixRule 写好了却不生效 | `_setup_fix_dispatcher()` 是空壳，未注册任何规则 | 用 `importlib` + `inspect` + `pkgutil.walk_packages()` 自动发现 FixRule 子类 |
| ❌ F001 对完整路径声明的 skill 报告缺失 | skill `path: SKILLS/plan/SKILL.md` 被再次追加 `/SKILL.md` → 双重路径 | `_resolve_skill_path()` 检测路径是否已以 `.md` 结尾 |
| ❌ .bak 备份文件污染 git 状态 | `FixRule._backup()` 创建 `*.bak`，`git status` 显示一大批 `??` | `.gitignore` 添加 `*.bak` |

### 14.7 与已有架构的关系

```text
EPIC-005 (治理引擎) ──检测──→ EPIC-006 (修复引擎)
   Scanner              FixRule
   CLI scan             CLI fix
   Report               dry_run diff
                          ↓
                    cap-pack.yaml / SKILL.md 修改
                          ↓
                    EPIC-005 重新扫描验证
```

修复引擎不替代治理引擎，而是在其上游消费扫描结果、在其下游用重新扫描验证修复效果。两个引擎组成 **scan → analyze → fix → verify** 闭环。

### 14.8 跨 Agent 文档模式 (Cross-Agent Documentation Pattern) 🔥

> **2026-05-16 新增** — 基于 EPIC-006 Phase 3 的设计经验。治理引擎做完后，下一步是让任意 Agent 理解并使用 cap-pack。

#### 问题
适配器写得再好，如果没人知道怎么用就等于白做。EPIC-005 Phase 3 交付了 4 个适配器（Hermes/OpenCode/OpenClaw/Claude），但缺乏清晰的文档让新 Agent 快速上手。

#### 三文档模式

构建跨 Agent 文档时，按以下三个层次组织：

| 文档 | 目标读者 | 核心内容 | 典型结构 |
|:-----|:---------|:---------|:---------|
| **README.md** | 所有 AI Agent | 「这是什么？我能用它做什么？」 | readme-for-ai 方法论：编号章节 + 三列 CLI 表 + 每节验证命令 |
| **ADAPTER_GUIDE.md** | 需要扩展新 Agent 的开发者 | 「如何接入新 Agent？」 | 每个适配器的使用案例 + 配置 + 验证方法 + 故障排查 |
| **QUICKSTART.md** | 首次接触 cap-pack 的 Agent | 「如何 5 分钟用起来？」 | 3-5 条命令完成安装/检查/修复 |

#### README 的 AI 友好标准

参考 `readme-for-ai` skill 的 11 条原则，cap-pack README 必须满足：

- [ ] CLI 参考表使用三列格式（命令 / 关键参数 / 预期输出）
- [ ] 每个章节末尾有验证命令
- [ ] 提供多路径安装方式
- [ ] 前置条件明确且可自检
- [ ] 包含跨 Agent 模型图（挂载层示意图）
- [ ] 适配器一览表（Agent → 适配器 → 状态）
- [ ] FAQ 即恢复路径

#### 实战参考
EPIC-006 Phase 3 (STORY-6-3-1 + STORY-6-3-2) 是此模式的完整实践，详见 `docs/EPIC-006-governance-fix-engine.md`。

### 14.10 行业生态更新（2026-05-16）

| 新工具 | 类型 | Stars | 核心发现 |
|:-------|:-----|:-----:|:---------|
| **SkillKit** | TS CLI | ⭐935 | 跨 46 Agent 格式翻译/安装/推荐，`skillkit translate` 验证了 SKILL.md 的跨平台可行性 |
| **Agent Skill Porter** | npm | — | 7 Agent 格式互转，Chimera Hub 中间格式模式与本 converter 的解耦设计思路一致 |

**核心洞察**: 已有工具全部在做「格式翻译」（Hermes↔Claude↔Cursor），**没有工具做「语义化结构重组」（扁平 skill → 语义能力包）**。

详见 `references/industry-landscape-2026.md` 完整调研报告。

### 14.9 相关资源

| 资源 | 路径 | 说明 |
|:-----|:------|:------|
| EPIC-006 完整设计 | `docs/EPIC-006-governance-fix-engine.md` | 4 Phase 12 Story 的完整计划 |
| SPEC-6-1 技术方案 | `docs/SPEC-6-1.md` | Fix 基础设施 + 确定性修复的详细架构设计 |
| 代码库深度分析 | `references/governance-fix-strategies.md` | 7 维代码库分析（CLI/适配器/扫描器/脚本/包结构/依赖/测试） |
| 混合方案论证 | (本 §14) | 确定性 vs LLM vs 混合方案的选择框架 |
| 跨 Agent 文档模式 | (本 §14.8) | README + ADAPTER_GUIDE + QUICKSTART 三文档模式 |
| 修复模式速查 | `references/fix-pattern-cookbook.md` | 7 种可复用的代码模式（YAML RMW/frontmatter/启发式/备份/幂等/diff/测试） |
| 实战陷阱速查 | `references/fix-engine-production-lessons.md` | FixRule 自动发现 / F001 路径双重 / .bak git 管理 / 模式错位 |
| 修复后文档对齐 | `references/fix-engine-production-lessons.md#六修复后文档对齐清单post-fix-doc-alignment` | 修复后必须更新的 6 种文档及其对齐顺序 |

---

### 15.8 主 Agent 驱动模式 (Main Agent-Driven Analysis)

> **2026-05-16 新增** — 基于 EPIC-007 设计反馈的架构决策。

Script+LLM 混合模式中的 "LLM" **不建立独立的 LLM 调用模块**，而是通过 **主 Agent驱动**来完成：

```text
// ❌ 错误做法：内置 LLM prompt 模块
converter/llm_analyzer.py → 自己调 API → 自己解析 → 耦合 LLM 逻辑

// ✅ 正确做法：主 Agent 通过 skill 流程驱动
1. 脚本执行 SCAN → 输出候选清单 (JSON)
2. 主 Agent (boku) 读取 JSON →
   用自己的推理能力判断「分类/分组/描述」
3. 脚本根据主 Agent 的判断执行 EXTRACT
4. 治理引擎 (scanner+fixer) 自动跑验证
```

#### 实现方式

整个 `convert` 流程本身就是一个 Hermes Skill（`cap-pack-converter`）。Script 和 Agent 通过**结构化 JSON 文件**交换数据：

```bash
# 步骤① 脚本扫描 → 输出 JSON
cap-pack scan --unpacked-only --format json > /tmp/candidates.json

# 步骤② 主 Agent 读取 candidates.json → 分析 → 输出 decisions.json
# （这是通过 skill 流程完成的，不是独立命令）
# 输出示例: [{"skill":"pdf-layout","target_pack":"doc-engine","confidence":92}]

# 步骤③ 脚本消费 decisions.json → 提取
cap-pack convert --from-json /tmp/decisions.json

# 步骤④-⑤ 治理扫描 + 报告
cap-pack scan packs/doc-engine
cap-pack fix packs/doc-engine
```

#### 决策

| 谁做 | 做什么 | 依据 |
|:-----|:-------|:------|
| 🛠️ 脚本 | 文件扫描/枚举、目录创建/复制、YAML 生成/解析、schema 验证、治理扫描/修复 | 确定性操作，用脚本又快又准 |
| 🤖 **主 Agent** | 分类推断、分组决策、描述撰写、经验标记 | 需语义理解，不适合规则硬编码 |

---

> **2026-05-16 新增** — 基于 EPIC-007 的深度设计经验。当需要将「非结构化 Agent 原生技能」自动转换为「标准化能力包」时使用的架构模式。核心创新：**脚本做确定性的文件操作，LLM 做需要语义理解的分析决策，两者通过结构化 JSON 接口解耦**。

### 15.1 问题

治理引擎（EPIC-005/006）能「发现问题」和「修复问题」，但无法将 `~/.hermes/skills/` 下的扁平原生技能自动组织成语义分组的能力包。手动提取一个包需要 20-40 分钟，且依赖人工判断。

### 15.2 五阶段管线

```
┌──────────┐   ┌────────────┐   ┌────────────┐   ┌──────────┐   ┌───────────┐
│ ① SCAN  │──▶│ ② ANALYZE  │──▶│ ③ EXTRACT  │──▶│ ④ GOVERN │──▶│ ⑤ REPORT  │
│ 枚举扫描  │   │ LLM分类+   │   │ 复制文件 +  │   │ 治理扫描  │   │ 输出摘要  │
│ (脚本)   │   │ 分组决策    │   │ 生成结构   │   │ + LLM调优 │   │ (脚本)    │
└──────────┘   │ (LLM)      │   │ (脚本)    │   │ (脚本+LLM)│   └───────────┘
               └────────────┘   └────────────┘   └──────────┘
```

| Phase | 谁驱动 | 输入 → 输出 |
|:-----:|:------:|:----------|
| ① SCAN | 🛠️ 脚本 | `~/.hermes/skills/` → skill 候选清单 + 已有包索引 |
| ② ANALYZE | 🧠 LLM | skill frontmatter + 内容 → 分类/分组/描述/经验标记 (JSON) |
| ③ EXTRACT | 🛠️ 脚本 | LLM 决策 JSON + skill 文件 → 目录结构 + cap-pack.yaml |
| ④ GOVERN | 🛠️+🧠 | 新包 → L0-L4 扫描 + FixRule + LLM 经验提取 |
| ⑤ REPORT | 🛠️ | 修复结果 → 转换摘要 + schema 验证 |

### 15.3 接口契约：脚本 ↔ LLM 的 JSON 桥

```json
// 脚本→LLM 输入 (SCAN 产出)
{
  "unpacked_skills": [
    {"name": "pdf-layout", "tags": ["pdf"], "dir_size": "1.2MB"}
  ],
  "existing_packs": [
    {"name": "doc-engine", "skills": ["pdf-layout"], "classification": "domain"}
  ]
}

// LLM→脚本 输出 (ANALYZE 产出)
{
  "decisions": [{
    "skill_name": "pdf-layout",
    "target_pack": "doc-engine",
    "new_pack_name": null,
    "new_pack_classification": "domain",
    "new_pack_description": null,
    "confidence": 92,
    "reasoning": "tags+domain → doc-engine",
    "has_experience_content": true,
    "experience_types": ["pitfall"]
  }]
}
```

### 15.4 可信度分级

| Confidence | 处理方式 |
|:----------:|:---------|
| ≥ 80 | 自动执行 |
| 60-79 | 执行 + 标记「建议复核」 |
| < 60 | **不执行**，放入待确认池 |

### 15.5 与现有治理引擎的集成

| 可复用组件 | 来源 | 用途 |
|:-----------|:------|:------|
| `find_skill_dir()` / `list_skill_files()` | `scripts/extract-pack.py` | 文件操作 |
| `CapPackAdapter.suggest()` | `adapter/cap_pack_adapter.py` | 包匹配推荐 (LLM 参考) |
| `BaseScanner` + 子类 | `scanner/` | L0-L4 扫描 |
| `FixRule` | `fixer/` | 自动修复 |

### 15.6 行业对标

| 对比维度 | SkillKit (⭐935) | Agent Skill Porter | **本模式** |
|:---------|:--------------:|:-----------------:|:----------:|
| 核心方向 | 跨 46 Agent 格式翻译 | 7 Agent 格式互转 | **语义化结构重组** |
| 语义分组 | ❌ 无 | ❌ 无 | ✅ LLM 智能分组 |
| 治理闭环 | ❌ 无 | ❌ 无 | ✅ 自动 scan+fix |
| 经验提取 | ❌ 无 | ❌ 无 | ✅ EXPERIENCES/ 生成 |

**核心洞察**: 已有工具专注「格式翻译」，空白区是「结构化重组 + 治理闭环」。

### 15.7 实战参考

- `docs/EPIC-007-skill-to-cap-pack-converter.md` — 完整 EPIC 设计 (4 Phase · 14 Stories)
- `references/hermes-to-cap-pack-converter.md` — 治理引擎代码差距分析
- `references/industry-landscape-2026.md` — 行业调研报告 (SkillKit 等详情)

> **2026-05-16 新增** — 基于深度调研（12 款工具 + 4 篇学术论文 + 8 篇实践指南）的 Agent Skill 治理工具全景图。
> 完整数据见 `references/industry-landscape-2026.md`。

### 13.6 统一标准框架 — Cap-Pack Compliance Levels

> **2026-05-16 新增** — 基于行业调研（8 个标准/规范 + 5 个生产实践）和学术研究（SkillRouter/skill-tree/Perplexity/Corpus2Skill）的能力包统一管理标准框架。
> 
> **核心原则**: 不 fork 行业标准（Agent Skills Spec），只在其上扩展 cap-pack 特有的合规层。
> 
> **标准优先铁律**: 构建治理/合规类工具时，必须先定义标准再构建检测器。标准是检测器的规范来源，而不是反过来从检测器推导标准。详见 §实战陷阱「标准优先顺序」。

#### 框架概览

```
Agent Skills Spec (行业基础)
     ↓ 100% 兼容，不 fork
┌─────────────────────────────────────┐
│  cap-pack 统一管理标准                │
│                                     │
│  Level 0: 兼容层 (强制)              │
│  ├── 目录结构: SKILL.md + scripts/  │
│  │   references/ + assets/          │
│  ├── YAML frontmatter: name + desc  │
│  ├── 渐进披露: 3 级加载              │
│  └── SKILL.md < 500 行              │
│                                     │
│  Level 1: 强制层 (门槛)              │
│  ├── 结构合规: 目录规范 + frontmatter│
│  ├── 质量合规: SQS ≥ 60 / CHI pass  │
│  ├── 元数据合规: version/tags/       │
│  │   classification 必填            │
│  └── 包描述: domain + capability     │
│                                      │
│  Level 2: 推荐层 (健康)              │
│  ├── 树状归属: 每个 skill 在 cluster │
│  ├── 内聚性: 簇大小 3-15,           │
│  │   无 >60% 重叠                    │
│  ├── 编排声明: design_pattern 声明   │
│  ├── 原子性: 行数<500, 主题数≤3      │
│  └── 版本规范: semver + changelog    │
│                                      │
│  Level 3: 生态层 (最佳实践)          │
│  ├── SRA 可发现性: 描述含触发关键词   │
│  ├── 跨平台: compatibility表         │
│  ├── 跨包无冗余: 不同包无>60%重叠    │
│  └── 经验积累: L2 Experiences 文档    │
└──────────────────────────────────────┘
```

#### 各 Level 详细标准

##### Level 0 — 兼容层（与 Agent Skills Spec 100% 一致）

| 检查项 | 标准 | 来源 |
|:-------|:-----|:------|
| `name` 字段 | 1-64 字符，小写+连字符，匹配目录名 | Agent Skills Spec |
| `description` 字段 | 1-1024 字符，含触发词 | Agent Skills Spec |
| 目录结构 | 只允许 scripts/references/assets 作为子目录 | Agent Skills Spec |
| SKILL.md 行数 | < 500 行 | Agent Skills Spec (rec.) |
| 渐进披露 | 三级加载: metadata → instructions → resources | Agent Skills Spec |

##### Level 1 — 强制层（cap-pack 最低门槛）

| 检查项 | 标准 | 测量方式 |
|:-------|:-----|:---------|
| v2 schema 验证 | cap-pack.yaml 通过 `cap-pack-v2.schema.json` | `validate-pack.py` |
| SQS 最低分 | ≥ 60（硬性门槛） | `skill-quality-score.py` |
| CHI pass | ≥ 0.55（硬性门槛） | `health-check.py --gate` |
| classification | 必填（domain/toolset/infrastructure） | schema 验证 |
| version | 必填，semver 格式 | schema 验证 |
| tags | 至少 2 个，与分类匹配 | schema 验证 |
| compatibility.agent_types | 非空 | schema 验证 |

##### Level 2 — 推荐层（健康度标准）

| 检查项 | 标准 | 测量方式 |
|:-------|:-----|:---------|
| 树状归属 | 每个 skill 至少属于一个 cluster | `skill-tree-index.py` |
| 簇大小 | 3-15 个 skill/簇 | `skill-tree-index.py --cluster-stats` |
| 包内重叠 | 同包 skill 间语义重叠 < 60% | `merge-suggest.py` |
| 编排声明 | 有编排的 skill 声明 `design_pattern` | `workflow_detector.py` |
| 原子性 | 主题数 ≤ 3, 功能内聚 | `atomicity_scanner.py` |
| 版本规范 | semver + CHANGELOG | `skill-lifecycle-audit.py` |
| 低分率 | SQS < 60 的 skill < 15% | `health-check.py` |

##### Level 3 — 生态层（最佳实践）

| 检查项 | 标准 | 测量方式 |
|:-------|:-----|:---------|
| SRA 可发现性 | SRA 推荐命中率 > 80% | `sra-discovery-test.py` |
| 跨平台兼容 | 至少 2 个 agent_types | schema 验证 |
| 跨包无冗余 | 不同包间无 > 60% skill 重叠 | `merge-suggest.py --cross-pack` |
| L2 经验 | 至少 1 篇 Experience 文档 | validates-packs.py |
| 链接有效性 | 无死链 | skill-validator validate links |

#### 标准的生产级验证（从规范到门禁）

统一标准的最终目标是**可执行门禁**，而非思想原则：

```bash
# 全量合规检查（Level 0-3 的自动检查）
python3 scripts/compliance-gate.py check <pack-name>

# 单层检查
python3 scripts/compliance-gate.py check <pack-name> --level 1
python3 scripts/compliance-gate.py check <pack-name> --level 2

# CI 门禁模式
python3 scripts/compliance-gate.py gate <pack-name> --min-level 1
# exit 0 = 通过 Level 1 门槛
# exit 1 = 未通过
```

#### 触发词补充

添加以下触发词以便基于本 skill 发现标准相关内容：
`统一标准` `合规标准` `compliance levels` `cap-pack 标准` `管理标准` `标准框架` `Level 0` `Level 1` `Level 2` `Level 3` `强制层` `推荐层` `生态层` `兼容层`

### 13.1 为什么关注行业生态

能力包不是孤岛——它在快速演进的 Agent Skill 治理生态中。理解已有工具：
- 🚫 避免重复造轮子（复用现有工具的扫描/验证输出作为上游数据）
- 🎯 发现差异化空间（Cap-Pack 合规 + 自动适配是独特护城河）
- 🔗 制定集成策略（哪些工具通过 MCP/CLI 提供可消费的数据）

### 13.2 七维差距矩阵

| 检测维度 | 现有工具覆盖 | Cap-Pack 差异化定位 |
|:---------|:-----------|:-------------------|
| ① 原子性扫描 | ⚠️ 部分（skill-validator/skill-guard 检查结构） | 定义**原子性阈值标准**+四问测试（cap-pack §①） |
| ② 树状结构管理 | ⚠️ skill-tree（danielbrodie）做聚类，但不关联质量 | 树状 + 质量 SQS + cap-pack 三者统一 |
| ③ 工作流编排检测 | ❌ **完全空白** | 检测 SKILL.md 的 `design_pattern` + `depends_on` + 步骤编排 |
| ④ Cap-Pack 合规 | ❌ **完全空白** | 基于 cap-pack-v2.schema.json 的扩展检查 |
| ⑤ 自动新增检测 | ⚠️ 部分（pre-commit hooks: skill-guard） | 持续 cron watcher + fingerprint 快照对比 |
| ⑥ 自动质量测试 | ⚠️ 部分（on-demand 命令） | 触发性扫描（skill 创建/修改时自动触发） |
| ⑦ 自动适配改造 | ❌ **完全空白** | 自动生成 cap-pack.yaml 条目 + 元数据补充 |

> **核心洞察**: 现有 12 款工具全部集中在「发现问题→报告问题」阶段。**「发现问题→自动适配到 Cap-Pack 标准」是 cap-pack 项目的独特护城河**。

### 13.3 三层集成架构（已有工具的复用策略）

```text
Layer 1: 现有工具作为数据源（集成层）
  skill-guard validate    → 格式合规分数
  skill-validator score   → LLM 质量评分
  skill-tree manifest     → 树状聚类建议

Layer 2: Cap-Pack 治理引擎（本项目的核心层）
  解析上游数据 + 补充 cap-pack 自有检测
  → 生成综合治理报告 + 适配改造建议

Layer 3: Agent 适配层（输出层）
  Hermes:   pre_flight gate + cron watcher + SRA 质量注入
  MCP:      跨 Agent 暴露治理能力（Skilldex 已验证此模式）
  CLI:      skill-governance 命令
```

### 13.4 战略价值评估

| 维度 | 评估 |
|:-----|:------|
| 差异化 | 🔥 **强** — cap-pack 合规 + 自动适配 + 工作流检测 = 3 个完全空白维度 |
| 项目价值 | 填补 cap-pack 缺失的自动化治理环节，使「提取→质量→治理→发布」形成闭环 |
| 技术可行性 | ✅ **高** — 核心逻辑纯 Python，Hermes 扩展点充分（pre_flight/cron/SRA） |
| 跨 Agent 适配 | 三层架构确保核心层与适配层分离，先做 Hermes + MCP |
| 实现成本 | ~4-6 周全功能版，2 周 MVP（核心扫描引擎 + Hermes 集成） |

### 13.5 相关资源

| 资源 | 路径 |
|:-----|:------|
| 完整生态调研报告（12 工具 + 来源索引） | `references/industry-landscape-2026.md` |
| 学术论文: Skilldex 格式合规评分 | `arxiv 2604.16911` |
| 学术论文: SkillRouter 大规模技能路由 | `arxiv 2603.22455` |
| 学术论文: SkillOrchestra 技能感知编排 | `arxiv 2602.19672` |

