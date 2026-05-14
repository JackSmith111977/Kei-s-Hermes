---
name: capability-pack-design
description: >-
  Agent 能力模块化与跨平台复用方法论。涵盖能力包(Capability Pack)格式设计、
  模块分割决策、生命周期管理、迭代进化闭环、跨 Agent 适配层架构。
  适用于将单体 Agent 能力拆分为可移植、可组合、可进化的模块化能力单元。
version: 2.3.0
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

### 2026-05-13 更新
- **JSON Schema 已发布**: `schemas/cap-pack-v1.schema.json`（可编程验证所有 cap-pack.yaml）
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

## 四-B、SRA 运行时发现适配

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

**doc-engine 实战基线 (Before)**:
- CHI: 0.6029 🟠 | 平均 SQS: 64.0 | 低分率: 35% | 版本完整率: 59%
- 17 技能 → 目标 10 技能 + 11 经验 + 7 簇
- SRA 推荐命中率: ~85% | 错误推荐: 3/13 (23%) | 微技能占位: 3/13 (23%)

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
| `merge-suggest.py` | `~/projects/hermes-cap-pack/scripts/merge-suggest.py` | 合并建议引擎。内容相似度分析（difflib SequenceMatcher）+ 分组优化（按 name prefix 分组避免 O(n²)，见 `references/content-comparison-optimization.md`）。支持 --yaml/--json 导出、--apply 备份执行 |
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

