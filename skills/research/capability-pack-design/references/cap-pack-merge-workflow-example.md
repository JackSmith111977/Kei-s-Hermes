# 🔄 能力包合并实战记录 — knowledge-base → learning-engine

> **日期**: 2026-05-14
> **项目**: hermes-cap-pack
> **Commit**: `c0b0627`
> **合并方向**: `knowledge-base` → `learning-engine`

## 背景

`learning-engine` 能力包提取（11 skills, commit `bc191ed`）后，发现原定后续提取的 `knowledge-base` 模块的核心技能（knowledge-precipitation, knowledge-routing, hermes-knowledge-base, llm-wiki）**已在提取时被 learning-engine 吸收**。若再独立提取 knowledge-base，将导致：
1. 包间技能重复（同一技能同时出现在两个 pack）
2. 循环依赖（learning-engine 依赖 knowledge-base，但 knowledge-base 又依赖 learning 方法论）
3. 管理成本翻倍

## 合并决策

**决策**: 不提取独立的 knowledge-base 包，而是合并至 learning-engine

**原因三要素**:
- ① 核心知识技能已吸收（4 个 skill 已在 learning-engine 中）
- ② 消除循环依赖（原包间依赖设计不合理）
- ③ 模块体系 18+3 → 17+3，降低整体管理成本

## 对齐范围

合并后共更新 **8 份文件**，每处附带合并注释：

| 文件 | 更新类型 | 注释方式 |
|:-----|:---------|:---------|
| `packs/learning-engine/cap-pack.yaml` | 移除 knowledge-base 依赖 | YAML 行内注释 |
| `docs/SPEC-1-1.md` | 模块表 + 分层图 + 示例 | `[^1]` 脚注 |
| `docs/EPIC-003-module-extraction.md` | Phase 2 表 + 路线图 + KPI | `[^1]` 脚注 |
| `docs/plans/EPIC-003-comprehensive-roadmap.md` | 全景表 + Phase 5 + 依赖图 + KPI | `[^1]` 脚注 |
| `docs/SPEC-3-3.md` | 模块 5 改为 learning-engine + 执行计划 + AC | 行内注释 |
| `docs/SPEC-2-3.md` | SRA 分类别名合并 | 代码行内（aliases 合并） |
| `README.md` | 包列表 + 覆盖统计 | `[^kb]` 脚注 |

## 关键操作

### 1. 发现重叠
```bash
# 比对所有 pack 的 skill 清单与未提取 skill
# 发现 learning-engine 已有 knowledge-precipitation, knowledge-routing 等
# 确认 knowledge-base 的 4/6 核心技能已被覆盖
```

### 2. 更新 cap-pack.yaml
```yaml
# ⚡ knowledge-base 已合并至此包 — 详见 SPEC-1-1.md 合并注释
dependencies:
  cap_packs:
    - name: skill-quality
      version: "1.0.0"
    # knowledge-base 依赖已移除（合并至本包）
```

### 3. 更新模块体系计数
- 旧: `18+3 模块`（含 knowledge-base #1 独立）
- 新: `17+3 模块`（knowledge-base 合并至 learning-engine）
- 旧覆盖率: 37% (7/19)
- 新覆盖率: 47% (8/17)

### 4. 更新 SRA 分类映射
```yaml
# Before: 两个独立入口
knowledge-base:  {aliases: ["知识库", "知识管理", "knowledge"]}
learning-engine: {aliases: ["学习", "研究", "调研", "learning"]}

# After: 别名合并
learning-engine: {aliases: ["知识库", "知识管理", "knowledge", "学习", "研究", "调研", "learning"]}
```

## 验证

```bash
# 检查残留引用
grep -rn "knowledge-base" docs/ packs/ README.md | grep -v "合并注释\|合并"
# → 无输出 ✅

# 验证 YAML
python3 -c "import yaml; yaml.safe_load(open('packs/learning-engine/cap-pack.yaml'))"
# → 通过 ✅

# 项目状态
python3 scripts/project-state.py verify
# → 通过 ✅
```

## 教训

1. **提取前先做重叠分析**: 每个新包提取前，先比对已有包的 skill 清单，避免重复
2. **合并不是「不做」**: 合并需要更全面的文档对齐而非更少
3. **脚注是 Markdown 标注合并原因的最佳方式**: `[^id]` 在表格和标题中都能工作
