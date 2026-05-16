---
name: capability-pack-design
description: >-
  Agent 能力模块化与跨平台复用方法论。涵盖能力包(Capability Pack)格式设计、
  模块分割决策、生命周期管理、迭代进化闭环、跨 Agent 适配层架构。
  适用于将单体 Agent 能力拆分为可移植、可组合、可进化的模块化能力单元。
version: 2.6.0
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
| `~/projects/hermes-cap-pack/scripts/sra-discovery-test.py` | SRA 发现验证脚本（15条测试查询） |
| `references/doc-engine-sra-test-data.md` | doc-engine 实战 SRA 测试原始数据 |
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

### 迭代阶段

| 陷阱 | 后果 | 预防 |
|:------|:------|:------|
| 更新通知轰炸 | 主人厌烦 | PATCH 级别静默更新，MAJOR 才通知 |
| 跨模块级联更新不回滚 | 部分 Agent 更新成功部分失败 | 用 `on_deactivate` + 备份实现原子性 |
| 经验与技能脱节 | 经验说 A 但技能步骤已是 B | SKILL.md 中加 `experience_ref` 字段显式关联 |

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

