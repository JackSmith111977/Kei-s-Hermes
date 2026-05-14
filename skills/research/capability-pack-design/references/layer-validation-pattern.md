# 🏗️ 能力包三层结构验证模式 (Layer Validation Pattern)

> **创建**: 2026-05-14 · **来源**: hermes-cap-pack EPIC-004 Phase 1 实战
> **模式**: 验证能力包是否具备完整的 L1 Skills + L2 Experiences + L3 Knowledge 三层结构

---

## 〇、问题

能力包提取完成后，如何系统性地验证每个包的三层结构完整性？手动检查 17+ 个包的目录结构不可扩展。

## 一、三层结构定义

| 层 | 目录 | 内容 | 必须满足 |
|:---|:-----|:-----|:---------|
| **L1 Skills** | `SKILLS/` | SKILL.md 操作文档 | 至少 1 个 .md 文件 |
| **L2 Experiences** | `EXPERIENCES/` | 实战经验/教训/最佳实践 | 至少 1 个 .md 文件 |
| **L3 Knowledge** | `KNOWLEDGE/concepts/` | 核心概念/实体/摘要 | 至少 1 个 .md 文件 |

## 二、验证脚本模式

核心验证脚本 `validate-layers.py` 实现了以下检查：

```
对于每个能力包目录：
  ├── 检查 EXPERIENCES/ 是否存在 + 至少 1 个 .md 文件
  ├── 检查 KNOWLEDGE/concepts/ 是否存在 + 至少 1 个 .md 文件
  └── 对每个 .md 文件：
      ├── 检查 YAML frontmatter 是否存在 (文件以 "---" 开头)
      ├── 检查必填字段完整性
      │   ├── L2: type, skill_ref
      │   └── L3: type, domain
      └── 检查 type 值是否合法
          ├── L2: best-practice | lesson-learned | tutorial | case-study | decision-tree | pitfall
          └── L3: concept | entity | summary
```

## 三、YAML Frontmatter 标准

### L2 Experience 格式

```markdown
---
type: best-practice | lesson-learned | tutorial | case-study | decision-tree | pitfall
skill_ref: "<关联 skill 名称>"
keywords: [关键词1, 关键词2]
created: 2026-05-14
---

# <标题>

## 背景

## 核心内容

## 为什么有效

## 陷阱/注意事项
```

### L3 Knowledge 格式

```markdown
---
type: concept | entity | summary
domain: <所属能力包名>
keywords: [关键词1, 关键词2]
created: 2026-05-14
---

# <标题>

## 定义/描述

## 核心要点

## 关联
```

## 四、CI 集成模式

验证脚本应集成到 CI 管道中：

```yaml
# .github/workflows/layer-check.yml
layer-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Check L2/L3 layers
      run: python3 scripts/validate-layers.py --ci
    - name: Frontmatter check
      run: python3 scripts/validate-layers.py --ci
```

## 五、先行迁移策略

当已有 L2 文档使用旧格式（如 `>` frontmatter 或无 frontmatter）时：

1. 编写 `fix-l2-frontmatter.py` 批量检测并添加 YAML frontmatter
2. 检测策略：文件名关键词 → 推测 type（`quick-ref` → `tutorial`, `pitfall` → `pitfall`）
3. 内容分析 → 推测 skill_ref
4. 始终保留原始内容，仅在文件头部添加 frontmatter
5. 运行 `validate-layers.py` 确认迁移完成

## 六、门禁指标

| 指标 | Healthy | 警告 | 失败 |
|:-----|:-------:|:----:|:----:|
| L2 覆盖率 (有 EXPERIENCES 的包) | 100% | ≥ 80% | < 80% |
| L3 覆盖率 (有 KNOWLEDGE 的包) | 100% | ≥ 80% | < 80% |
| frontmatter 异常率 | 0% | < 10% | ≥ 10% |

## 七、参考实现

- `scripts/validate-layers.py` — 全量层验证 + frontmatter 检查
- `scripts/fix-l2-frontmatter.py` — 批量 L2 frontmatter 迁移工具
- `reports/chi-priority-list.md` — 健康度优先级排序报告
