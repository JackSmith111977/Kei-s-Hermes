# ⚡ 模块合并标注模式

> **来源**: 2026-05-14 hermes-cap-pack 实战 — knowledge-base → learning-engine 合并
> **适用场景**: 任何需要合并/重命名/废弃模块时的全文档对齐操作

## 核心原则

用户明确要求：**「对齐到文档中，并标注原因」**

每次结构性变更（合并、拆分、重命名、废弃模块），必须：
1. 更新所有引用该模块的文档
2. **标注变更原因** — 使用 `[^n]` 脚注模式
3. 更新项目报告（project-report.json + HTML）

---

## 标准流程

### Step 1: 搜索所有引用

```bash
# 搜索文件名中含关键词的文档
find . -name "*.md" | xargs grep -l "knowledge-base" 2>/dev/null

# 搜索内容中所有出现该关键词的文档
grep -r "knowledge-base" docs/ --include="*.md" -l
```

### Step 2: 按文档类型批量更新

| 文档类型 | 更新内容 | 标注方式 |
|:---------|:---------|:---------|
| SPEC 文档（如 SPEC-1-1） | 模块表、分层图、示例 | `[^1]` 脚注 + 行内标记 |
| EPIC 文档 | Phase 表、路线图、KPI | `[^1]` 脚注 |
| 路线图/计划文档 | 全景表、依赖图、Phase 列表 | `[^1]` 脚注 |
| README | 包列表、覆盖统计 | `[^kb]` 脚注（独立标记） |
| 项目报告 JSON | 架构层、Epics、Sprint | 直接更新，无需脚注 |
| HTML 报告 | KPI、包卡片、剩余模块 | 醒目合并注释块 (`merge-note`) |
| SRA 分类映射 | 别名合并 | 直接合并，无需脚注 |
| cap-pack.yaml | 依赖关系 | 注释行标注 |

### Step 3: 脚注标注模式

#### Markdown 脚注（[^1] 模式）

在文档中引用处添加 `[^1]`：

```markdown
| 1 | `learning-engine` | 🧠 学习引擎（含知识库[^1]） | ~11 | **元能力层** |
```

在文档末尾定义脚注内容：

```markdown
[^1]: **⚡ v1.0.1 合并注释**: `knowledge-base`（原 #1）已于 2026-05-14 合并至 `learning-engine`。
原因：① 核心技能已在 learning-engine 提取时吸收；② 消除包间循环依赖。
```

#### 脚注内容规范

```
[^n]: **⚡ {原模块} → {目标模块} 合并注释**
{原因清单，用① ② ③ 编号}。
{影响：模块体系从 X 更新为 Y}。
{详情参见文档引用}。
```

### Step 4: HTML 报告合并注释块

在 HTML 报告中使用醒目卡片展示合并信息：

```html
<div class="merge-note">
  <strong>📚 knowledge-base 模块 → 合并至 learning-engine</strong><br>
  核心知识技能已在 learning-engine 提取时吸收。
  消除包间循环依赖，模块体系从 18+3 更新为 <strong>17+3</strong>。<br>
  <span style="color:var(--dim); font-size:0.82rem;">详见 docs/SPEC-1-1.md 合并注释 [^1]</span>
</div>
```

CSS 样式：
```css
.merge-note {
  background: rgba(188,140,255,0.08);
  border: 1px solid var(--purple);
  border-radius: var(--radius);
  padding: var(--space-md);
  margin-bottom: var(--space-md);
  font-size: 0.88rem;
}
.merge-note strong { color: var(--purple); }
```

### Step 5: 状态机同步

```bash
# 更新 project-state.yaml
python3 scripts/project-state.py sync

# 验证零漂移
python3 scripts/project-state.py verify
```

### Step 6: 项目报告对齐

```bash
# 1. 更新 project-report.json（版本号、架构层、Epics、Sprint）
# 2. 创建/更新 PROJECT-PANORAMA.html
# 3. browser_navigate 预览验证
# 4. git add + git commit（数据 + HTML + 代码一起）
```

---

## 实战清单（hermes-cap-pack knowledge-base 合并）

主人要求的具体合并步骤清单，可直接复用：

```
□ SPEC-1-1: 模块表移除 knowledge-base 行 + 更新 learning-engine 计数 + [^1] 脚注
□ SPEC-1-1: 分层图移除 knowledge-base 框
□ SPEC-1-1: cap-pack.yaml 示例从 knowledge-base 改为 learning-engine
□ EPIC-003: Phase 2 表移除 knowledge-base + 添加 [^1] 脚注
□ EPIC-003: 路线图 5→4 pack + KPI 更新
□ EPIC-003-comprehensive-roadmap: 全景表 + Phase 5 + 依赖图 + KPI
□ SPEC-3-3: 模块5 改为 learning-engine + 执行计划 + AC
□ SPEC-2-3: SRA 分类别名合并到 learning-engine
□ README: 包列表 + 覆盖统计 + [^kb] 脚注
□ learning-engine/cap-pack.yaml: 移除 knowledge-base 依赖
□ project-report.json: 版本号 + 架构 + Epic + Sprint
□ PROJECT-PANORAMA.html: KPI + 包卡片 + merge-note + 剩余模块
□ git commit: 全部变更 + 标注原因
```
