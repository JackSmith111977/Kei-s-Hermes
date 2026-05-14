# 项目全景报告 10 章模板设计

> 基于 arc42 + CODITECT + 项目管理最佳实践融合而成。
> 适用于软件项目的全景概览报告（PROJECT-PANORAMA）。

---

## 模板概览

```
┌─ 头部: 项目身份 + 元数据 + 状态徽章
├─ §1 执行摘要 (BLUF)         ← 结论先行 + KPI 卡片
├─ §2 项目概况                ← 背景/目标/Sprint 时间线
├─ §3 架构总览                ← 分层架构 + 模块全景表
├─ §4 Epics & 交付进度         ← Epic 状态卡 + Story 清单
├─ §5 质量全景                ← SQS 均分 + 五维 + 趋势
├─ §6 测试与 CI/CD            ← 测试分布 + CI 门禁 + cron
├─ §7 文档体系 (SDD)          ← 文档树 + 状态 + 路径链接
├─ §8 风险与技术债务            ← 已知问题 + P0/P1/P2 改进建议
├─ §9 路线图                  ← 已完成 / 阻塞 / 规划中
└─ §10 附录                   ← 术语表 + 数据源说明
```

---

## 各章节详细规格

### 头部

```
<h1>📦 {项目名称}</h1>
<div>项目描述</div>
<div class="badges">
  <span>{版本号}</span>
  <span>{分支名}</span>
  <span>{提交数} commits</span>
  <span>{Sprint 数} Sprints</span>
</div>
<div>生成于 {时间戳}</div>
```

**数据源**: git describe + git branch + git rev-list

---

### §1 执行摘要 (BLUF)

**目的**: 让读者在 10 秒内了解项目全貌。

**内容**:
- 一句话结论（BLUF）
- 6 KPI 卡片网格:

| KPI | 来源 |
|:----|:-----|
| 当前版本 | project-report.json |
| 测试通过率 | project-report.json |
| SQS 健康度 | SQS DB |
| 完成 Stories | project-report.json |
| Python 行数 | 脚本统计 |
| HTML 报告数 | reports/ 计数 |

**数据源**: project-report.json + SQS DB + git + 文件系统

---

### §2 项目概况

**目的**: 交代背景、范围和进展节奏。

**内容**:
- **背景与目标**: 1-2 段说明项目动机
- **关键指标表**:

| 指标 | 值 |
|:-----|:----|
| 能力包模块 | 18 个（N 个已提取）|
| 总技能数 | N 个 |
| 未分类技能 | N 个 |
| Python 脚本 | N 个 |
| 自动化 Cron | N 个 |

- **Sprint 时间线**: 每行显示 Sprint 名称/日期/总结/故事数+测试数

**数据源**: project-report.json (sprint_history)

---

### §3 架构总览

**目的**: 展示项目的分层结构和模块全景。

**内容**:
- **N 层架构卡片**: 每层一个 KPI 卡片，含层名称、描述、子模块列表
- **模块全景表**:

| 模块 | SQS 均分 | Skill 数 | 条形图 |
|:-----|:--------:|:--------:|:------:|
| 📚 知识库系统 | 71.1 | 5 | ████████████ |

**数据源**: SQS DB (scores 表) + 分类规则

---

### §4 Epics & 交付进度

**目的**: 展示项目进展的具体状态。

**内容**:
- **Epic 状态卡**: 每个 Epic 一张卡片，包含:
  - Epic ID + 状态徽章 (approved/qa_gate/create/draft)
  - 名称
  - 完成率进度条
  - Story 完成数/总数
- **Story 清单表**:

| ID | 名称 | 状态 | 所属 Epic |
|:---|:-----|:----:|:---------:|

**数据源**: project-report.json (epics[].stories[])

---

### §5 质量全景

**目的**: 展示系统质量健康状况。

**内容**:
- **KPI 卡片**: 平均 SQS / 合格数 / 待改进数 / 趋势点
- **五维分析表**:

| 维度 | 得分 | 条形图 |
|:-----|:----:|:------:|
| S1 结构完整性 | 15.5/20 | ████████████ |

- **低分排行榜 Top 10**
- **SQS 历史趋势折线图** (Chart.js)

**数据源**: SQS DB (scores + score_history 表)

---

### §6 测试与 CI/CD

**目的**: 展示质量保障基础设施。

**内容**:
- KPI: 测试通过率 / 执行耗时 / CI job 数 / cron 数
- **测试文件分布表**:

| 文件 | 测试数 | 通过 | 状态 |
|:-----|:-----:|:----:|:----:|

- CI Pipeline 描述

**数据源**: project-report.json (tests)

---

### §7 文档体系 (SDD)

**目的**: 展示 SDD 文档完整性和可追溯性。

**内容**:
- KPI: 总文档数 / Epics / Specs / Stories
- **文档树表**:

| 类型 | 名称 | 状态 | 路径 |
|:-----|:-----|:----:|:----:|

**数据源**: docs/ 目录扫描 + 文档 frontmatter

---

### §8 风险与技术债务

**目的**: 暴露项目的已知问题和待改进项。

**内容**:
- **主要风险表**: 风险项 / 等级 / 影响
- **改进建议表**: 优先级 / 建议

**常见风险类别**:
| 风险 | 典型影响 |
|:-----|:---------|
| S4 关联完整性低分 | 技能间引用断裂 |
| 未分类 Skill | 模块覆盖不全 |
| 微技能 (<50行) | 应降级为经验文件 |
| Epic 待审 | 阻塞后续开发 |

**数据源**: SQS DB + project-report.json

---

### §9 路线图

**目的**: 展示过去、现在、未来的项目节奏。

**内容**:
- ✅ **已完成** (已完成 Epics)
- 🔜 **下一步** (当前阻塞 + 规划中)

每项包含: 名称 / 状态 / 描述 / 优先级

**数据源**: project-report.json (epics[].status)

---

### §10 附录

**目的**: 补充参考信息。

**内容**:
- **术语表**

| 术语 | 定义 |
|:-----|:-----|
| SQS | Skill Quality Score — 五维 0-100 质量评分 |
| Cap Pack | 能力包 — 标准化可移植的技能集合 |
| SDD | Spec-Driven Development |
| SRA | Skill Runtime Advisor |
| CHI | Capability Health Index |

- **数据源表**

| 来源 | 位置 |
|:-----|:-----|
| 项目元数据 | docs/project-report.json |
| SQS 评分 | ~/.hermes/data/skill-quality.db |
| SDD 文档 | docs/*.md + docs/stories/*.md |
| Git 状态 | .git/ (运行时获取) |

---

## 实现指南

### HTML 模板技术 (避免 f-string 花括号冲突)

```python
# ❌ 错误做法 — f-string 花括号与 CSS/JS 冲突
html = f"""<style>.cls {{ color: {val} }}</style>
<script>data = {json.dumps(data)}</script>"""

# ✅ 正确做法 — 占位符替换
TEMPLATE = """<style>.cls { color: __VAL__ }</style>
<script>data = __DATA__</script>"""
html = TEMPLATE.replace("__VAL__", str(val)).replace("__DATA__", json.dumps(data))
```

### 数据驱动原则

所有报告内容必须从结构化数据源自动生成：
1. `project-report.json` — 项目元数据、交付状态、测试统计
2. `skill-quality.db` (SQLite) — SQS 评分、历史趋势
3. `docs/` 目录扫描 — SDD 文档树
4. `git` 命令 — 版本、分支、提交数

### 文档对齐

每节标注数据源路径：报告 → 原始文档的双向追溯。
```
§5 质量全景 ← SQS DB (SPEC-2-2 定义)
§7 文档体系 ← docs/ 目录 (SDD 规范)
```

---

## 版本记录

| 版本 | 日期 | 变更 |
|:-----|:-----|:------|
| 1.0 | 2026-05-14 | 初始版本。基于 arc42 + CODITECT + 项目管理标准融合。 |
