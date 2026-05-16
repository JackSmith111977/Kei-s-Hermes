# 🏗️ 后置质量升级 — 实际执行模式

> **实战验证**: hermes-cap-pack EPIC-004 (2026-05-14~16)  
> **范围**: 17 个能力包, 122 skills, 5 个 Phase, 12 个 Story, ~16h  
> **基线 → 结果**: CHI 67.92, SQS 67.9, 低分占比 ~0% (从 47%)

---

## 〇、核心理念

质量升级不作为模块提取的串行阻塞，而是 **增量循环**：每一层独立推进，不等待全部模块提取完，对现有包立即生效。

```
提取新模块 ──→ Phase 0 基线扫描 ──→ Phase 1 L2/L3补充 ──→ Phase 2 质量提升
   ↑                                                                  │
   └────────── Phase 4 门禁固化 ←── Phase 3 合并清理 ←─────────────────┘
```

---

## 一、Phase 0: 健康度基线扫描 (~1.5h)

**目标**: 建立可度量的质量基线，确定优先级

| 步骤 | 工具 | 产出 |
|:-----|:-----|:------|
| 全量 SQS 扫描 | `skill-quality-score.py --audit --json` | 每个 skill 五维评分 JSON |
| 按包聚合 | `aggregate-sqs.py` | `chi-by-pack.json` (包级 SQS 分布) |
| 健康仪表盘 | `skill-tree-index.py --dashboard` | `chi-dashboard-v2.html` (按包分组、趋势可追踪) |
| 优先级排序 | `aggregate-sqs.py --prioritize` | `chi-priority-list.md` (最低分包排最前) |

**关键产出**: `reports/chi-baseline.json` (基线 CHI 值, 后续门禁的比较基准)

```json
{"chi": 67.92, "threshold": 0.75, "updated": "2026-05-15T00:12:42"}
```

---

## 二、Phase 1: L2/L3 逐层补充 (~6h)

**目标**: 每个能力包具备三层知识体系

| 层 | 说明 | 文件位置 | 工作量 |
|:---|:------|:---------|:------:|
| **L1 Skills** | SKILL.md 技能文件 | `SKILLS/{id}/SKILL.md` | ✅ 已提取, 保持不变 |
| **L2 Experiences** | 实战经验/教训/最佳实践 | `EXPERIENCES/{id}.md` | 每个包 1-3 篇 |
| **L3 Knowledge** | 核心概念/实体/领域分析 | `KNOWLEDGE/concepts/{id}.md` | 每个包 1-3 篇 |

**验证脚本**: `validate-layers.py` (检查每个包是否三层齐全 + frontmatter 标准化)

**实战经验**:
- 不要一次性为所有包创建 L2/L3 — 分 2-3 批, 每批验证后再继续
- L3 文档的 type 字段用 `concept`, L2 用 `experience`
- frontmatter 必须包含 `type/description/tags` 三个字段 (`fix-l2-frontmatter.py` 可批量修复)

---

## 三、Phase 2: 质量提升迭代 (~5h)

**目标**: SQS < 60 的 skill 全部提升, 元数据补齐, 质量门禁嵌入 CI

### 3.1 低分 skill 改进

使用 `fix-low-score-skills.py` 为低分 skill 补充 `depends_on` 和 `see_also` 字段 (S4 关联维度修复):

```python
# LOW_SKILLS 字典中定义每个低分 skill 的关联
LOW_SKILLS = {
    'markdown-guide': {'depends_on': ['html-guide','pdf-layout-weasyprint'],
                       'see_also': ['epub-guide','latex-guide']},
    # ... 26 个 skill
}
```

**恢复执行检查**: 脚本是幂等的 — 如果字段已存在则跳过。可安全重复运行。

### 3.2 元数据补齐

使用 `fix-pack-metadata.py` 确保每个 `cap-pack.yaml` 包含:

```yaml
name:           # 必填
version:        # 必填, semver
description:    # 必填, 一句话描述
author:         # 必填
triggers:       # 必填, SRA 发现用关键词列表
```

### 3.3 CHI 门禁 (chi-gate.py)

```bash
# 检查 CHI 是否降级
python3 scripts/chi-gate.py --threshold 0.75

# 更新基线 (质量提升后)
python3 scripts/chi-gate.py --update-baseline
```

**CI 集成要点**:
- 开始时用 `continue-on-error: true` (warning 模式) — Phase 2 阶段
- 质量稳定后移除 `continue-on-error` (blocking 模式) — Phase 4 阶段
- 渐进目标: 0.75 → 0.80 → 0.85

**退出码**:
- `0`: PASS (CHI >= 基线)
- `1`: WARNING (CHI 轻度降级)
- `2`: BLOCKED (CHI 严重降级)

---

## 四、Phase 3: 合并清理 (~3h)

**目标**: 检测并消除跨包冗余

### 4.1 检测 (STORY-4-9)

```bash
# 全量检测
python3 scripts/merge-suggest.py

# YAML 格式输出 (可执行)
python3 scripts/merge-suggest.py --yaml

# 列出问题
python3 scripts/merge-suggest.py --list
```

**检测类型**:
| 类型 | 阈值 | 说明 |
|:-----|:----:|:------|
| DUPLICATE | >95% | 完全重复 → 删除冗余副本 |
| OVERLAP | >75% | 高度重叠 → 合并为主 skill |
| SUBSET | >85% | 子集关系 → 扩展主 skill |
| CONCEPTUAL | >60% | 概念冗余 → 人工判断 |
| BMAD | — | BMAD 系列冗余检测 (特殊规则) |
| MICRO | <50行 | 微技能 → 降级为 experience |

### 4.2 执行 (STORY-4-10)

**实战试点** (hermes-cap-pack):

| 试点 | 操作 | 效果 |
|:-----|:-----|:------|
| **BMAD 系列合并** | 3→1 保留 `bmad-context-engineering` | 内容合并 + deprecated 标记 |
| **微技能降级** | 6 个 <50行 skill → experiences | doc-engine: 15→9 skills |

**执行步骤**:
1. 内容合并: 源 skill 的独有内容复制到目标 skill 的 `references/` 目录
2. 弃用标记: 源 SKILL.md 末尾添加 `> 💡 已合并到 [目标]。`
3. 系统 skill 标记 deprecated
4. cap-pack 更新: SKILLS/ 移除, EXPERIENCES/ 添加, cap-pack.yaml 调整
5. `git add && git commit`

---

## 五、Phase 4: 门禁固化 (~1.5h)

**目标**: 锁定质量基准, 生成最终报告

### 5.1 质量升级报告

创建 HTML 报告, 包含:
- KPI 卡片 (包数/技能数/CHI/SQS/低分率)
- Before/After 对比表
- Phase 执行时间线 (已完成/进行中)
- 交付物清单
- 验收标准进度

示例: `reports/epic004-quality-upgrade-report.html`

### 5.2 CI 门禁升级

```yaml
# .github/workflows/ci.yml
chi-gate:
  name: 📈 CHI Quality Gate
  steps:
    - name: 📊 Check CHI baseline (blocking)
      run: python3 scripts/chi-gate.py --threshold 0.75
```

关键: **移除 `continue-on-error: true`** — 让 CHI 降级导致 CI 失败

### 5.3 项目状态同步

```bash
# Phase 完成后
python3 scripts/phase-gate.py complete EPIC-004 Phase-4

# 更新 project-state.yaml: AC done=true, completed_phases 追加
# 更新 EPIC 文档: AC [ ] → [x]
# 验证一致性
python3 scripts/project-state.py verify
```

---

## 六、工具清单

| 工具 | 用途 | Phase |
|:-----|:------|:-----:|
| `skill-quality-score.py` | SQS 五维评分 + DB 持久化 | 0 |
| `aggregate-sqs.py` | 按包聚合 SQS + 优先级排序 | 0 |
| `health-check.py` | 6 KPI + CHI 综合健康指数 | 0 |
| `validate-layers.py` | 三层完整性检查 + frontmatter 校验 | 1 |
| `fix-l2-frontmatter.py` | 批量修复 L2 frontmatter | 1 |
| `fix-low-score-skills.py` | 低分 skill S4 关联修复 | 2 |
| `fix-pack-metadata.py` | cap-pack.yaml 元数据补齐 | 2 |
| `chi-gate.py` | CHI 不降级门禁 (CI 集成) | 2→4 |
| `merge-suggest.py` | 跨包重叠检测 + 合并建议 | 3 |
| `phase-gate.py` | Phase 门禁管理 | 全部 |
| `project-state.py` | 统一状态机管理 + 验证 | 全部 |

---

## 七、实战陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 串行假设 | 质量升级无限期推迟 | **增量循环**: 不等全部模块提取完, 对现有包立即生效 |
| CHI 门禁过早阻塞 | CI 频繁失败, 决策疲劳 | Phase 2 用 warning, Phase 4 才升级为 blocking |
| BMAD 标记 inspect | `--apply` 无法自动执行 | 手动内容合并 + deprecated 标记 |
| micro-skill 只降级不改 cap-pack | 包内仍有旧 skill 引用 | 同时更新 cap-pack.yaml 的 skills/experiences 列表 |
| 一次性更新太多 AC | Phase 完成度不可追踪 | 逐 Phase 更新 AC, 每 Phase 完成后 `phase-gate.py complete` |
| 文档漂移累积 | project-report.json 滞后 | 每次 commit 前 `project-state.py verify` |

---

## 八、EPIC-004 实战基线 (参考)

| 指标 | Before | After (Phase 2 后) |
|:-----|:------:|:------------------:|
| CHI | 0.6355 | 67.92 |
| SQS 平均 | 67.9 | 67.9 |
| 低分占比 | 47% | ~0% |
| L2 覆盖 | 6/18 | 17/17 |
| L3 覆盖 | 0/18 | 17/17 |
| Skills 总数 | 141 | 122 (17 合并降级) |
| Experiences | 10 | 37 |
| Knowledge | 0 | 50 |
| 能力包 | 14+ | 17 (全部提取完成) |
| 测试 | 141 ✅ | 141 ✅ |

**待渐进目标**: CHI 67.92→85, SQS 67.9→80 (在常规迭代中自然提升)
