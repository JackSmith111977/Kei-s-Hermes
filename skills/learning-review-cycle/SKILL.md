---
name: learning-review-cycle
description: "学习-Review-总结自驱动循环。定时扫描 skill 新鲜度、自动生成学习总结/周报/月报、探测知识缺口并生成学习建议。让整个 learning ecosystem 自动运转。"
version: 1.0.0
triggers:
  - review
  - 复盘
  - 总结
  - 学习总结
  - 学习周报
  - 学习月报
  - 自动学习
  - 自驱动
  - 知识缺口
  - 知识审计
  - skill review
  - 技能盘点
  - 定期回顾
  - learning review
depends_on:
  - learning-workflow
  - learning
  - skill-creator
design_pattern: Pipeline + Generator
skill_type: Workflow
---

# 🔄 Learning Review Cycle · 自驱动学习循环 v1.0

> **核心定位**：让学习不再需要"等人来触发"。通过定时 Review + 总结 + 缺口探测，形成自动学习循环。
> **三环结构**：学习环(task) → Review环(定时) → 总结环(产出)

---

## 〇、自驱动循环总览

```
                      ┌──────────────────────┐
                      │   🔬 学习环 (Task)     │
                      │  主人触发 / 缺口触发   │
                      │  learning-workflow    │
                      └────────┬─────────────┘
                               │ 完成后自动触发
                               ▼
┌────────────────────────────────────────────────┐
│            🔄 Review 环 (定时扫描)              │
│                                                │
│  每周/每月自动扫描：                            │
│  ├─ Skill 新鲜度检查（版本号/日期）             │
│  ├─ 学习历史回顾（最近学了什么）                │
│  ├─ 使用频率分析（哪些 skill 用得多/少）        │
│  └─ 知识缺口探测（任务失败 → 需要学习）         │
│                                                │
│  产出：Review 报告 → 学习建议清单               │
└───────────────────────┬────────────────────────┘
                        │ 定期自动产出
                        ▼
┌────────────────────────────────────────────────┐
│           📝 总结环 (定期产出)                  │
│                                                │
│  自动生成：                                     │
│  ├─ 学习周报（本周学了什么）                    │
│  ├─ 学习月报（本月知识沉淀统计）                │
│  ├─ Skill 健康报告（哪些需要更新）              │
│  └─ 学习规划建议（下周/月该学什么）             │
│                                                │
│  交付：发送到主人指定的平台                      │
└────────────────────────────────────────────────┘
```

---

## 一、Review 环 — 定时扫描引擎

### 1.1 扫描范围

| 扫描项 | 频率 | 数据源 | 产出 |
|--------|------|--------|------|
| **Skill 新鲜度** | 每周 | `skill_view()` 读取所有 SKILL.md 的 version/date | skill 老旧度报告 |
| **学习历史回顾** | 每周 | `~/.hermes/learning_history.json` | 最近学习总结 |
| **使用频率分析** | 每月 | skill 文件修改时间 + learning state | 高频/低频 skill 列表 |
| **知识缺口探测** | 每次任务失败后 | 任务执行日志/error trace | 学习建议（待学习队列） |

### 1.2 新鲜度评分公式

```
新鲜度 = 基础分(50) 
       + 版本活跃度(30)  — 近30天有更新 +10，近7天 +20
       - 时间衰减(20)    — 超过30天无更新 -5，超过90天 -15
       + 使用加分(20)    — 频繁使用 +5，偶尔使用 +2
       
评分 < 60 → "待检查" 
评分 < 40 → "建议更新" 
评分 < 20 → "紧急更新"
```

### 1.3 知识缺口探测

**触发条件**（任一个满足即触发）：
1. **任务失败**：使用某个 skill 但任务报错/不完整
2. **多次调整**：同一任务需要 3 次以上修正
3. **信息过时**：搜索结果发现 skill 引用的 API 已变更
4. **用户抱怨**：用户说"这个怎么不行"、"上次不是学了么"

**处理流程**：
```
[缺口触发] → 分析缺口类型 → 
├─ 知识过时 → 创建"刷新学习"任务
├─ 知识缺失 → 创建"主题学习"任务
├─ 知识冲突 → 创建"对比验证"任务
└─ 工具失效 → 创建"替代方案研究"任务
     ↓
缺口写入 ~/.hermes/learning/gap_queue.json
     ↓
下次 Review 扫描时，将缺口任务提升为建议
```

---

## 二、总结环 — 自动报告生成

### 2.1 学习周报模板

```markdown
# 📚 学习周报 W{周数}
**生成时间**：{日期}
**周期**：{周一} ~ {周日}

## 📊 本周学习统计
- 完成了 {N} 个学习任务
- 创建/更新了 {M} 个 Skill
- 总学习时长约 {H} 小时

## ✅ 本周完成
| 日期 | 主题 | 产出 | 状态 |
|------|------|------|------|
| {日} | {主题} | {skill 名} | ✅ |

## ⚠️ 待办事项
| 优先级 | 事项 | 原因 |
|--------|------|------|
| 🔴 高 | {待办} | {原因} |
| 🟡 中 | {待办} | {原因} |

## 💡 学习建议
1. {建议1}
2. {建议2}

## 🔄 知识缺口
- {缺口1}
- {缺口2}
```

### 2.2 学习月报模板

```markdown
# 📚 学习月报 {月份}
**生成时间**：{日期}

## 📊 月度统计
- 任务总数：{N}
- Skill 变化：{新增}/{更新}/{移除}
- 知识领域覆盖：{领域列表}

## 🏆 本月亮点
- {亮点1}
- {亮点2}

## 📈 Skill 健康报告
| Skill | 版本 | 新鲜度 | 状态 | 建议 |
|-------|------|--------|------|------|
| {name} | {ver} | {score} | ✅/⚠️/🔴 | {建议} |

## 🎯 下月学习计划
1. **优先级 1**：{建议1} — 原因
2. **优先级 2**：{建议2} — 原因

## 🧠 方法论积累
「本月的搜索/过滤技巧积累」
```

### 2.3 学习总结模板

每次学习任务完成时自动生成：

```markdown
# 📝 学习总结：{主题}

## 📋 基本信息
- **日期**：{日期}
- **模式**：{快速/深度}
- **耗时**：{N} 分钟
- **产出**：{skill 名 / 笔记}

## 🎯 学到了什么
{3-5 句话总结}

## 💡 方法论反思
- 本次搜索效率：{高效/一般/不理想}
- 可复用技巧：{技巧}

## 📌 下步建议
{还需要的深入学习方向}
```

---

## 三、自驱动学习队列

### 3.1 缺口队列文件

`~/.hermes/learning/gap_queue.json`

```json
{
  "gaps": [
    {
      "id": "gap_001",
      "created_at": "2026-05-04T14:00:00",
      "type": "knowledge_outdated",
      "source": "task_failure",
      "skill": "pdf-layout-weasyprint",
      "description": "WeasyPrint v62 的 API 变了，当前 skill 引用的是 v60",
      "priority": "high",
      "status": "pending",
      "suggested_action": "创建刷新学习任务"
    }
  ],
  "last_review": "2026-05-04T16:00:00",
  "auto_learn_enabled": true
}
```

### 3.2 自动消费规则

```
[定时触发 Review]
  ↓
读取 gap_queue.json → 取出高优先级缺口
  ↓
高优先级缺口数量 ≥ 3？
├─ 是 → 自动触发 learning-workflow（深度模式）
│    └─ 主题：按优先级顺序取 top 3
└─ 否 → 等待下次 Review（标记为学习建议）
```

### 3.3 禁止无限循环

- 每次自动学习只能处理 **最多 3 个缺口**
- 自动学习的 skill 产出必须在 Review 中验证
- 同类型缺口连续 3 次自动学习后，必须等用户手动确认

---

## 四、使用方式

### 手动触发 Review

```bash
# 完整 Review：扫描所有 skill 的新鲜度
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py scan

# 生成学习周报
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py weekly

# 生成学习月报
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py monthly

# 查看知识缺口
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py gap-list

# 添加知识缺口
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py gap-add knowledge_missing "描述" high

# 检查是否可以自动触发学习（高优先级缺口 ≥ 3 时自动触发）
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py auto-check

# 生成单次学习总结
python3 ~/.hermes/skills/learning-review-cycle/scripts/review-engine.py summary "主题" "深度" 45 "skill产出名"
```

### 学习完成后自动触发的流程

每次学习任务完成（learning-workflow 的 STEP 6 反思迭代）时：
1. **生成学习总结**：`review-engine.py summary "主题" "模式" 耗时 "产出"`
2. **检查知识缺口**：如果学习过程中遇到困难，调用 `review-engine.py gap-add`
3. **记录到 gap_queue**：下次 Review 扫描时会自动处理

### 定时任务（自动）

```yaml
每周一早 9 点：学习周报 + 扫描
每月 1 号早 9 点：学习月报 + 深度扫描
```

### 与夜间自习引擎的协同

已有 `6aa75cd6b8d3`（夜间自习 00-08 点）定时任务，learning-review-cycle 与它互补：
- 夜间自习 → 主动学习新知识
- Review 循环 → 检查学了什么、哪些 skill 需要更新、探测知识缺口
- 两者互不冲突，夜间自习的学习记录会自动被 Review 循环捕获

---

## 五、相关文件

| 文件 | 用途 | 
|------|------|
| `~/.hermes/learning/gap_queue.json` | 知识缺口队列 |
| `~/.hermes/learning/reports/` | 周报/月报输出目录 |
| `~/.hermes/learning/reviews/` | Review 报告目录 |
| `~/.hermes/learning_history.json` | 学习历史（已有） |

---

## 六、Red Flags

- ❌ **无限循环**：自动触发的学习不能再自动触发了！
- ❌ **缺口堆积**：如果缺口队列超过 20 条未处理，自动学习暂停，等用户处理
- ❌ **重复学习**：同一主题的缺口 7 天内不会重复触发
- ❌ **报告轰炸**：周报/月报只能发送一次，禁止重复发送

---

## 七、集成方式

### 与 learning-workflow 的集成

learning-workflow 的 STEP 6（反思迭代）完成后：
1. 自动调用 `learning-review-cycle` 检查是否产生新的缺口
2. 如果学习产出是一个 skill 更新，记录到使用频率统计

### 与 skill-creator 的集成

skill-creator 创建/更新 skill 后：
1. 记录版本变更到新鲜度追踪
2. 标记该 skill 为"最近更新"

---

**🔒 本 skill 负责自驱动循环，不可被循环自身触发！**
