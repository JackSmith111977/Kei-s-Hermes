---
name: project-report-generator
description: "项目全景报告HTML生成技能 — 融合深度循环学习工作流 + HTML/CSS 设计能力的结构化报告创作。每次任务都从零分析项目数据、设计叙事结构、手工定制HTML，而非模板替换。可配合 web-ui-ux-design、visual-aesthetics、html-presentation 等设计skill组合使用。"
version: 1.0.0
author: boku (Emma/小玛)
tags:
  - project-report
  - html-generation
  - documentation
  - panorama
  - report-design
  - data-visualization
triggers:
  - 生成项目报告
  - 项目全景
  - project report
  - 项目概况
  - 项目文档
  - 全景报告
  - panorama
  - 项目总览
  - 项目状态报告
  - project status
  - 生成HTML报告
  - 项目展示页
  - 项目仪表盘
  - 项目健康报告
depends_on:
  - web-ui-ux-design
  - visual-aesthetics
  - html-presentation
  - learning-workflow
  - deep-research
  - unified-state-machine
design_pattern: Pipeline
skill_type: Workflow
---

# 🏗️ 项目全景报告生成器 (Project Report Generator)

> **核心理念**：每个项目都是独特的，项目报告也应该是独特的。
> 本 skill 不是模板引擎，而是 **创作工作流**——引导 boku 通过深度分析 + 叙事设计 + 手工 HTML 定制，每次生成独一无二的项目全景报告。
>
> **与 generate-panorama.py 的区别**：
> - ❌ 旧方案：Python 脚本 + 硬编码 HTML 模板 + `.replace()` 占位符替换
> - ✅ 新方案：Hermes Skill + LLM 驱动 + 深度循环分析 + 手工定制 HTML
> - 旧方案产出「看起来都一样」的报告；新方案产出**有灵魂的数据叙事**
>
> **什么时候生成报告？**
> 报告生成是 SDD 工作流的自然一环，不是手动触发的独立任务。
> - Sprint/Phase 完成 → QA_GATE 后 → 自动进入报告生成步骤
> - Epic 批准后 → 生成全景报告
> - 主人说「看看最新状态」→ 按需生成
> - **不要**在任务中途主动问「要不要生成报告」——等流程走到该步骤再生成

---

## 📐 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│          Project Report Generator — 五阶段创作工作流              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 0: 需求理解 + 加载设计基础                                 │
│  ├─ 明确受众、用途、格式要求                                      │
│  └─ 加载 web-ui-ux-design + visual-aesthetics + html-presentation│
│                                                                  │
│  Phase 1: 深度数据收集 (深度循环)                                 │
│  ├─ 扫描项目元数据源 (JSON/DB/文档)                               │
│  ├─ 分析数据关联和核心洞察                                        │
│  ├─ [R1反思] 数据覆盖度检查 → 不足则回到收集                      │
│  └─ 输出数据清单: 所有可用数据 + 关键指标                          │
│                                                                  │
│  Phase 2: 叙事结构设计                                           │
│  ├─ 确定「数据故事」: 从数据中提取叙事线                          │
│  ├─ 设计报告章节: 选择最合适的章节组合 (10选N)                    │
│  ├─ [R2反思] 结构完整性检查 → 缺内容则回到 Phase 1               │
│  └─ 输出报告蓝图: 章节大纲 + 每节数据映射                          │
│                                                                  │
│  Phase 3: HTML 创作 (手工定制)                                   │
│  ├─ 定义视觉设计系统 (配色/字体/间距/卡片风格)                    │
│  ├─ 逐章创作 HTML (先结构再内容)                                 │
│  ├─ 嵌入图表/可视化 (Chart.js / CSS 条状图等)                     │
│  ├─ [R3反思] 视觉质量检查 → 不美则回到设计系统                   │
│  └─ 输出完整 HTML 文件                                            │
│                                                                  │
│  Phase 4: Review & 交付                                          │
│  ├─ 内容完整性审查: 是否有遗漏的重要信息                          │
│  ├─ 视觉一致性审查: 颜色/间距/排版是否统一                         │
│  ├─ 浏览器预览验证                                                │
│  ├─ 质量门禁 (Quality Gate)                                      │
│  └─ 交付给主人                                                    │
│                                                                  │
│  Phase 5: 反思迭代 (STEP 6)                                      │
│  ├─ 本次创作有什么可复用的经验？                                  │
│  └─ 更新本 skill 的 references/ 积累模板模式                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 循环机制 (深度循环学习集成)

借鉴 learning-workflow 的三层循环架构，每个 Phase 后都有反思门禁：

```
Phase 0 → Phase 1 → [R1] ─→ Phase 2 → [R2] ─→ Phase 3 → [R3] ─→ Phase 4 → [QG] → Phase 5
                 ↑            ↑            ↑             ↑
                 └─── 不足 ────┘            │             │
                            └─── 欠缺 ──────┘             │
                                        └─── 不美 ────────┘
```

| 门禁 | 位置 | 检查内容 | 回退到 |
|:----:|:----:|:---------|:------:|
| **R1** | Phase 1 后 | 数据是否覆盖所有关键维度？有无遗漏重要数据源？ | Phase 1 重新收集 |
| **R2** | Phase 2 后 | 章节结构是否完整？叙事线是否清晰？是否回答了核心问题？ | Phase 1 补充数据或 Phase 2 重新设计 |
| **R3** | Phase 3 后 | HTML 视觉是否一致？信息层级是否清晰？配色是否和谐？ | Phase 3 重新设计系统 |
| **QG** | Phase 4 后 | 报告是否满足所有验收标准？ | 回到对应 Phase |

---

## 〇、🚨 前置门禁

**在开始任何报告创作前，必须执行：**

```bash
# 1. 检查 pre_flight
python3 ~/.hermes/scripts/pre_flight.py "生成项目全景报告"

# 2. 加载设计基础 skills
skill_view(name='web-ui-ux-design')
skill_view(name='visual-aesthetics')
skill_view(name='html-presentation')

# 3. 加载数据收集 tools
skill_view(name='deep-research')  # 如果需要外部调研

# 4. 检查项目状态一致性（如项目有 unified-state-machine）
if [ -f "docs/project-state.yaml" ]; then
    python3 scripts/project-state.py verify  # 确认零漂移再开始
fi
```

---

## Phase 0: 需求理解 + 加载设计基础

### 必须回答的问题

| 问题 | 作用 | 默认值 |
|:-----|:-----|:-------|
| 👤 受众是谁？ | 决定技术深度和风格 | 主人 + 技术团队 |
| 📊 项目是什么？ | 确定数据源范围 | hermes-cap-pack |
| 🎨 需要什么风格？ | 影响视觉设计 | 暗色主题 + 数据驱动 |
| 📋 要涵盖哪些方面？ | 决定章节选择 | 执行摘要/架构/交付/质量/路线图 |

### 加载的设计 skill

| Skill | 提供什么 | 为什么需要 |
|:------|:---------|:----------|
| `web-ui-ux-design` | 9 种 UI 风格、7 大 UX 定律、布局原则 | 报告需要专业的信息层级 |
| `visual-aesthetics` | 美丑判断标准、Dieter Rams 十原则、配色理论 | 报告需要「好看」 |
| `html-presentation` | HTML/CSS 实现方案、7 种设计风格、打印样式 | 报告是 HTML 格式 |

### Phase 0 产出物

```markdown
## 报告创作计划
**受众**: {受众描述}
**项目**: {项目名称}
**风格基调**: {暗色/亮色/彩色/极简}
**核心数据源**: {列出所有可用数据源}
**预计章节**: {初步章节清单}
```

---

## Phase 1: 深度数据收集

### 数据源清单（hermes-cap-pack 示例）

| 数据源 | 位置 | 提供信息 |
|:-------|:-----|:---------|
| `docs/project-report.json` | 项目根目录 | 版本/Epics/Sprints/测试/元数据 |
| `docs/project-state.yaml` | 项目根目录 | 统一状态机 — 3 Epic/9 Spec/28 Story 状态 + 4 Sprint 进度 + 质量指标 |
| `~/.hermes/data/skill-quality.db` | SQS 数据库 | 200+ skills 的五维质量评分 + 历史趋势 |
| `docs/*.md` + `docs/stories/*.md` | SDD 文档目录 | 文档树 + 状态 + SDD 阶段 |
| `.git/` | Git 仓库 | 版本标签/分支/提交数 |
| `scripts/*.py` | 脚本目录 | 代码行数统计 |
| `reports/*.html` | 报告目录 | 已生成的报告清单 |

### 收集方法

```python
# 读取 project-report.json
import json
pr = json.loads(Path("docs/project-report.json").read_text())

# 读取 SQS 数据库
import sqlite3
conn = sqlite3.connect(str(Path.home() / ".hermes/data/skill-quality.db"))
scores = conn.execute("SELECT * FROM scores").fetchall()
trend = conn.execute("SELECT DATE(scored_at), AVG(sqs_total) FROM score_history GROUP BY 1 ORDER BY 1").fetchall()

# 扫描 SDD 文档
from pathlib import Path
docs = list(Path("docs/").glob("**/*.md"))

# 获取 Git 状态
import subprocess
tag = subprocess.run(["git", "describe", "--tags", "--always"], capture_output=True, text=True).stdout.strip()
```

### [R1 门禁] 数据覆盖度检查

```markdown
## R1 数据覆盖度自检
- [ ] 项目元数据: version/author/repo/license
- [ ] 架构信息: 模块数/层数/技术栈
- [ ] Epics & Stories: 完整交付清单
- [ ] 状态一致性: project-state.yaml 已 verify（零漂移）
- [ ] SQS 数据: 均分/分布/五维/趋势/低分
- [ ] 测试数据: 总数/通过率/文件分布
- [ ] 文档体系: 类型/数量/状态
- [ ] Git 状态: tag/branch/commits
- [ ] 脚本规模: 代码行数/脚本数

❗ 如有任何缺失 → 回到 Phase 1 补充
✅ 全部覆盖 → 进入 Phase 2
```

### Phase 1 产出物

```markdown
## 数据清单
### 核心指标
- 版本: v0.7.0
- 测试: 101/101 ✅
- SQS: 67.8
- 总 skills: 200
- ...
### 关键发现
- 最强模块: 学习引擎 84.7
- 最弱维度: S4 关联完整性 6.0/20
- 最大风险: 64 个未分类 skill
- ...
```

---

## Phase 2: 叙事结构设计

### 可选章节库（10 个标准模块）

根据项目特点和数据情况，从以下模块中选择 5-10 个组成报告：

| # | 章节 | 适用场景 | 核心数据源 |
|:-:|:-----|:---------|:----------|
| 1 | **§1 执行摘要** | ✅ 必选 | 全部 KPI 浓缩 |
| 2 | **§2 项目概况** | ✅ 必选 | project-report.json |
| 3 | **§3 架构总览** | 架构型项目 | 模块定义 + SQS |
| 4 | **§4 Epics & 交付** | ✅ 必选 | project-report.json |
| 5 | **§5 质量全景** | SQS 已启用 | SQS DB |
| 6 | **§6 测试与 CI/CD** | 有自动化测试 | project-report.json |
| 7 | **§7 文档体系** | SDD 文档完善 | docs/ 目录 |
| 8 | **§8 风险与债务** | 有风险数据 | SQS + 分析 |
| 9 | **§9 路线图** | ✅ 必选 | Sprint 历史 |
| 10 | **§10 附录** | 可选 | 术语/数据源 |

### 叙事线设计

**核心提问**：这些数据在讲什么故事？

例如 hermes-cap-pack 的故事线：
```
"2 天内从零到 5 个 Sprint，交付 27 个 Story，质量逐步提升但关联性仍是短板"
```

**章节组合选择原则**：
- 必选：§1 执行摘要 + §2 项目概况 + §4 交付 + §9 路线图
- 根据数据丰富度选择 2-4 个附加章节
- 最多 10 章，最少 5 章

### [R2 门禁] 结构完整性检查

```markdown
## R2 结构自检
- [ ] 有执行摘要（BLUF 先行）
- [ ] 有数据支撑（每个结论都有数据来源）
- [ ] 有架构或技术内容
- [ ] 有交付进度
- [ ] 有质量指标
- [ ] 有未来路线图
- [ ] 叙事线清晰（数据在讲什么故事？）

❗ 缺核心章节 → 回到 Phase 1 补充数据
✅ 结构完整 → 进入 Phase 3
```

### Phase 2 产出物

```markdown
## 报告蓝图
**标题**: Hermes Capability Pack — 项目全貌 v2
**叙事线**: ...
**章节选择**: §1 §2 §3 §4 §5 §6 §7 §8 §9 §10
**每节数据映射**:
  §1: avg_sqs, test_passing, completed_stories, code_lines
  §2: Sprint 时间线, 关键指标表
  ...
**视觉基调**: 暗色背景 + 卡片布局 + 蓝色渐变点缀
```

---

## Phase 3: HTML 创作

### 3.0 设计系统定义

**在写任何 HTML 之前，先定义设计 tokens：**

```css
:root {
  /* 配色系统 */
  --bg: #0d1117;           /* 深色背景 */
  --card: #161b22;          /* 卡片底色 */
  --border: #30363d;        /* 边框色 */
  --text: #e6edf3;          /* 主文字 */
  --dim: #8b949e;           /* 辅助文字 */
  --accent: #58a6ff;        /* 强调色 — 蓝色 */
  --ok: #3fb950;            /* 成功/绿色 */
  --warn: #d29922;          /* 警告/黄色 */
  --bad: #f85149;           /* 失败/红色 */
  --purple: #bc8cff;        /* 点缀色 — 紫色 */

  /* 间距系统 */
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  
  /* 圆角 */
  --radius: 8px;
  
  /* 字体 */
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
}
```

### 3.1 逐章创作顺序

```
1. 先写 CSS（设计系统 → 布局 → 组件）
2. 再写 HTML 结构（header → sections → footer）
3. 最后填充数据内容
4. 添加交互（Chart.js 等）
5. 添加打印样式
```

### 3.2 最佳实践

| 原则 | 说明 |
|:-----|:------|
| **信息层级** | h1 > h2 > h3，颜色/字号/间距逐步递减 |
| **卡片化** | 每个信息块用卡片包裹，统一圆角和阴影 |
| **数据驱动** | 所有数字从数据源读取，不硬编码 |
| **链接可追溯** | 每个文档名都指向真实路径 |
| **打印友好** | 从第一行代码就包括 `@media print` |
| **响应式** | 768px 断点，大屏双列小屏单列 |

### 3.3 Chart.js 集成

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<canvas id="trendChart"></canvas>
<script>
new Chart(document.getElementById('trendChart'), {
  type: 'line',
  data: {
    labels: [...] ,
    datasets: [{ ... }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { min: 50, max: 85, ticks: { color: '...' }, grid: { color: '...' } },
      x: { ticks: { color: '...' }, grid: { display: false } }
    }
  }
});
</script>
```

### [R3 门禁] 视觉质量检查

```markdown
## R3 视觉质量自检
- [ ] 设计系统已定义（配色/间距/圆角统一）
- [ ] 信息层级清晰（一眼能看出重点）
- [ ] 配色和谐（不超过 4 种主色）
- [ ] 卡片间距一致
- [ ] 数据和文字不溢出
- [ ] 链接可点击
- [ ] 暗色/亮色模式（至少一种）
- [ ] 整体「看起来专业」

❗ 不美 → 回到 3.0 重新定义设计系统
✅ 视觉达标 → 进入 Phase 4
```

### Phase 3 产出物

```markdown
## 交付物
**文件**: PROJECT-PANORAMA.html
**大小**: {文件大小}
**章节数**: {N} 章
**图表数**: {N} 个 Chart.js
**代码行**: {N} 行 HTML+CSS+JS
```

---

## Phase 4: Review & 交付

### 4.1 内容完整性审查

```markdown
## 内容审查清单
- [ ] 数据没有过时的
- [ ] 所有数据源正确引用
- [ ] 没有事实错误
- [ ] 所有链接可访问（相对路径正确）
- [ ] 文档状态是最新的
- [ ] 版本号/Git 信息正确
- [ ] 没有拼写错误
```

### 4.2 浏览器预览

```bash
# 用 browser_navigate 预览
browser_navigate(url="file:///path/to/PROJECT-PANORAMA.html")

# 截图验证
browser_vision(question="截图检查布局是否正常")
```

### 4.3 质量门禁 (QG)

```markdown
## 质量门禁 (Quality Gate)
### 功能性（30 分）
- [ ] 所有链接有效
- [ ] Chart.js 图表正常渲染
- [ ] 页面可滚动
- [ ] 响应式布局正常

### 内容性（40 分）
- [ ] 所有数据准确
- [ ] 叙事线清晰
- [ ] 无重要遗漏
- [ ] 结论有数据支撑

### 视觉性（30 分）
- [ ] 配色一致
- [ ] 排版美观
- [ ] 信息层级清晰

**总分**: {N}/100
**结果**: {通过/需改进/不通过}
```

### 4.4 交付

发送 HTML 文件到飞书或指定平台：

```
send_message(
  target="feishu",
  message="📦 项目全景报告 MEDIA:/path/to/PROJECT-PANORAMA.html"
)
```

---

## Phase 5: 反思迭代 (STEP 6)

### 每次报告创作后完成：

1. **创作过程反思**：
   - 本次哪个 Phase 最耗时？为什么？
   - 数据收集有什么可以自动化的？

2. **经验提取**：
   - 有没有可复用的 CSS 模式？
   - 有没有值得记录到 references/ 的技巧？

3. **更新 references/**：
   - 将可复用的模式/技巧写入 `project-report-generator/references/`

4. **更新本 skill**：
   - 如果发现流程有改进空间，更新 SKILL.md

---

## 🚩 常见陷阱 (Red Flags)

### ❌ 陷阱 1：在任务中途主动问「要不要生成报告」
- **后果**：打断工作流，主人觉得你在推销而不是在做事
- **解决**：报告生成是 SDD 工作流的自然一环（Sprint/Phase 完成 → QA_GATE → 报告生成），不要在半路问。等流程走到该步骤再生成，或者主人说「看看最新状态」时再按需生成

### ❌ 陷阱 2：跳过 Phase 0 直接写 HTML
- **后果**：没有设计系统，边写边改，最后风格不一致
- **解决**：严格走 Phase 0 → 1 → 2 → 3 顺序

### ❌ 陷阱 2：用 Python 脚本生成 HTML
- **后果**：模板僵硬、缺乏叙事灵活性、LLM 的创作能力被浪费
- **解决**：让 LLM 直接从零创作，用 skill 引导流程而非脚本生成内容

### ❌ 陷阱 3：所有数据塞进一个页面
- **后果**：信息过载，读者找不到重点
- **解决**：每节承载 3-4 个核心信息块，宁可分页不要挤满

### ❌ 陷阱 4：忽略打印样式
- **后果**：打印/导出 PDF 时布局错乱
- **解决**：从一开始就加入 `@media print`

### ❌ 陷阱 5：不预览就直接交付
- **后果**：可能有无数据的空白区域、CSS 渲染异常
- **解决**：必须用 `browser_navigate` 预览 + `browser_vision` 截图验证

### ❌ 陷阱 6：每个报告都从零开始
- **后果**：重复造轮子，每次都花时间搭基础 CSS
- **解决**：将可复用的 CSS 模式和布局技巧存入 references/

---

## 📚 参考资源

| 资源 | 位置 | 用途 |
|:-----|:------|:------|
| web-ui-ux-design | Hermes skill | 布局原则和 UI 风格参考 |
| visual-aesthetics | Hermes skill | 美丑判断标准 |
| html-presentation | Hermes skill | HTML/CSS 实现方案 |
| deep-research | Hermes skill | 需要外部调研时使用 |
| learning-workflow | Hermes skill | 深度循环学习方法论 |
| unified-state-machine | Hermes skill | 项目状态机 — 数据一致性验证 + 实体状态跟踪 |
| [cap-pack-merge-pattern](references/cap-pack-merge-pattern.md) | (ref) | 模块合并全流程 7 步 + 文件清单 + 注释模板 |
| [data-sources-hermes-cap-pack](references/data-sources-hermes-cap-pack.md) | (ref) | cap-pack 项目数据源清单 |
| [css-patterns](references/css-patterns.md) | (ref) | 可复用的 CSS 布局模式 |
| [cap-pack-alignment-patterns](references/cap-pack-alignment-patterns.md) | (ref) | cap-pack 项目文档对齐模式 — 三文件六/八检查点 + Epic 漂移修复 + 验证 |

---

## Phase 6: 增量更新模式（非首次创作）

**适用场景**: 项目已有报告，只需反映最新变更（如新增模块、更新 Story 状态、版本升级）。
**不适用场景**: 首次创作、大幅度重新设计、风格变更 → 走 Phase 0-5 全流程。

### 何时用增量模式

| 场景 | 模式 | 理由 |
|:-----|:----:|:------|
| 新增 1 个能力包 | ✅ 增量 | 包列表 + KPI + 剩余模块数变化 |
| Story 状态变更 | ✅ 增量 | 只改 epic 进度条和 story grid |
| 版本号更新 | ✅ 增量 | 只改 KPI 卡片数值 |
| 首次创建报告 | ❌ 全量 | 需要 Phase 0-5 设计系统 |
| Sprint 完成 | ✅ 增量 | 时间线 + KPI + 进度条 |
| 模块合并/删除 | ✅ 增量 | 改包列表 + KPI + 剩余模块 + 合并注释 |

### 增量更新标准流程（四步法）

```
Every project data change → apply ALL four steps in order:

Step 1 ── project-report.json
  - 包列表: architecture.layers[0].modules[] 增/删/改
  - KPI: overview_cards[] 数值更新
  - Stories: epics[].stories[].status 更新
  - Sprint: sprint_history[] 追加

Step 2 ── PROJECT-PANORAMA.html
  - KPI cards: 数值与 JSON 保持同步
  - 包卡片: 增/删/改包名、描述、skills 数
  - 剩余模块列表: 移除已提取的
  - Epic 故事网格: 更新状态标签
  - Sprint 时间线: 追加最新 sprint

Step 3 ── project-state.yaml (if exists)
  - EPIC story_count / completed_count
  - Story 状态添加
  - Sprint 状态

Step 4 ── git commit
  - git add project-report.json PROJECT-PANORAMA.html project-state.yaml
  - git commit -m "docs: {变更摘要}"
  
🔄 循环: 每次变更重复 1→2→3→4，不可跳过
```

### cap-pack 项目特殊字段对照表

| JSON 字段 | HTML 对应 | 更新频率 | 典型值示例 |
|:----------|:----------|:--------:|:----------|
| overview_cards[2].value | KPI 能力包数 | 每次提取 | 11 → 12 |
| info_table[3].value | 覆盖百分比 | 每次提取 | "65% (11/17)" |
| architecture.layers[0].modules[] | 包卡片 grid | 每次提取 | 新增 {name, description} |
| epics[2].stories[] | Epic 故事网格 | Story 完成 | 追加 {id, status} |
| sprint_history[] | Sprint 时间线 | Sprint 完成 | 追加条目 |

### 增量更新陷阱

| 陷阱 | 后果 | 解决 |
|:-----|:------|:-----|
| 改了 JSON 不改 HTML | HTML 与 JSON 数据不一致 | 每次 JSON 变更 → 立即同步 HTML |
| 忘了更新 project-state.yaml | project-state.py status 报错 | 将 state.yaml 加入增量三件套 |
| 只改 KPI 卡片不改包列表 | 报告自相矛盾 | 所有关联字段必须同步更新 |
| JSON 括号错误导致无效 | git hook 拒绝提交 | 改完立即 python3 -c 验证 |

---

## 📝 更新记录

| 版本 | 日期 | 变更 |
|:-----|:-----|:------|
| 1.0.0 | 2026-05-14 | 初始创建。五阶段创作工作流 + 三层循环门禁 + HTML 手工定制方法论 |
| 1.1.0 | 2026-05-14 | 新增 Phase 6: 增量更新模式 + cap-pack 数据字段参考 |
