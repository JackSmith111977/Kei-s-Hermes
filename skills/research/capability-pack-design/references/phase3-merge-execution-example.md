# 🔄 能力包 Phase 3 合并实战记录 — BMAD 合并 + 微技能降级

> **日期**: 2026-05-15
> **项目**: hermes-cap-pack
> **Commit**: `cb24627`, `5956d88`
> **模式**: 跨层合并 (Hermes 系统 + cap-pack 包) + 技能降级

---

## 场景 1: Hermes 系统级合并（BMAD 系列）

### 背景

3 个 BMAD 技能（`bmad-context-engineering`, `bmad-party-mode-orchestration`, `bmad-context-insights`）存在于 `~/.hermes/skills/` 中，但**没有**被提取到任何 cap-pack 包中。

### 合并方案

```
源技能 A: bmad-party-mode-orchestration (SQS 72.8)
源技能 B: bmad-context-insights       (SQS 50.2)
目标技能: bmad-context-engineering    (SQS 74.8)
```

### 执行步骤

```bash
# Step 1: 内容分析
# 读三个 SKILL.md，识别独有内容区域

# Step 2: 合并独有内容到目标
# 将源技能的内容复制为 target/references/{source-name}.md
cp ~/.hermes/skills/bmad-party-mode-orchestration/SKILL.md \
   ~/.hermes/skills/bmad-context-engineering/references/bmad-party-mode-orchestration.md

# Step 3: 标记源技能 deprecated
# 在每个源 SKILL.md 末尾追加:
echo '> 💡 本 skill 已合并到 bmad-context-engineering。请使用 bmad-context-engineering。' \
   >> ~/.hermes/skills/bmad-party-mode-orchestration/SKILL.md

# Step 4: 更新目标技能 frontmatter
# 添加 deprecated: [] 字段到目标 SKILL.md 的 frontmatter 中
```

### 验证命令

```bash
# 检查标记是否到位
grep -r "合并到 bmad-context-engineering" ~/.hermes/skills/bmad-*/SKILL.md

# 检查目标 references 是否存在
ls ~/.hermes/skills/bmad-context-engineering/references/
```

### 关键要点

| 要点 | 说明 |
|:-----|:------|
| **不删除原文件** | 只标记 deprecated，保留 SKILL.md 作为回溯依据 |
| **内容合并到 references/** | 不修改 target 的 SKILL.md 主体，避免破坏其 frontmatter |
| **SQS 高的保留** | 总是保留 SQS 更高的 skill 作为 target |
| **cap-pack 无影响** | 因为源技能不在任何 cap-pack 包中，无需修改 cap-pack 文件 |

---

## 场景 2: 微技能 → Experience 降级（doc-engine 包）

### 背景

6 个 <50 行的 micro-skill（markdown-guide, docx-guide, epub-guide, html-guide, latex-guide, xlsx-guide）同时存在于：
- `~/.hermes/skills/`（Hermes 系统）
- `packs/doc-engine/SKILLS/`（cap-pack 包内）

### 降级方案

```
技能 → Experience
├── SKILLS/ 中的独立技能目录 → 删除
├── EXPERIENCES/ 新增 experience 文件
├── cap-pack.yaml: skills[] → experiences[] 迁移
└── ~/.hermes/skills/ → 标记 deprecated
```

### 执行步骤

```bash
# Step 1: 创建 experience 文件
# 从 SKILL.md 提取核心内容，去掉 frontmatter，加 experience frontmatter
cat > packs/doc-engine/EXPERIENCES/docx-quick-ref.md << 'EOF'
---
id: docx-quick-ref
title: Word 文档操作速查
type: experience
description: python-docx 创建/编辑 Word 文档 — 从 docx-guide skill 降级
---
# Word (.docx) 快速参考
## 常用代码模式
...
EOF

# Step 2: 从 SKILLS/ 移除源技能目录
rm -rf packs/doc-engine/SKILLS/docx-guide/

# Step 3: 更新 cap-pack.yaml
# 从 skills: 列表移除该条目
# 在 experiences: 列表添加新条目（含 description 标注来源）

# Step 4: 标记 Hermes 系统级 skill deprecated
echo '> 💡 本 skill 已降级为 doc-engine 包的 experience。直接用法见 packs/doc-engine/EXPERIENCES/docx-quick-ref.md' \
   >> ~/.hermes/skills/docx-guide/SKILL.md
```

### cap-pack.yaml 变更示例

```yaml
# Before: skills 列表含微技能
skills:
  - id: docx-guide
    name: Word 文档操作
    ...
  - id: markdown-guide
    name: Markdown 写作
    ...

# After: 微技能从 skills 移除
skills:
  - id: pdf-layout          # 保留核能技能
  - id: pptx-guide
  ...

# experiences 新增降级来源标注
experiences:
  - id: docx-quick-ref
    title: Word 文档操作速查
    description: python-docx 创建/编辑 Word 文档 — 从 docx-guide skill 降级
  - id: markdown-quick-ref
    title: Markdown 写作与转换
    description: Markdown 语法 + pandoc 转换 — 从 markdown-guide skill 降级
```

### 验证命令

```bash
# 验证 cap-pack.yaml 完整性
python3 scripts/validate-pack.py packs/doc-engine

# 检查无残留 SKILL 目录
find packs/doc-engine/SKILLS -name "SKILL.md" | wc -l
# 预期输出: 9 (原来 15，移除 6 个)

# 检查 experience 存在
find packs/doc-engine/EXPERIENCES -name "*.md" | wc -l
# 预期输出: 11 (原来 5，新增 6 个)

# 验证 YAML
python3 -c "import yaml; yaml.safe_load(open('packs/doc-engine/cap-pack.yaml'))"
```

### 关键要点

| 要点 | 说明 |
|:-----|:------|
| **双层级操作** | 同时修改 Hermes 系统 + cap-pack 包，两者必须同步 |
| **experience 保留来源信息** | description 标注 \"从 XX skill 降级\"，方便追溯 |
| **SKILLS 目录清理** | 直接删除旧 skill 目录（git rm），不保留空目录 |
| **cap-pack.yaml 的 skills/experiences 都需更新** | 一处移除一处添加，不要漏 |

---

## merge-suggest.py 的使用和限制

### 已知限制

| 限制 | 表现 | 应对 |
|:-----|:------|:------|
| **只扫描 ~/.hermes/skills/** | 不检查 cap-pack packs/ 内的 skill | 合并后手动同步 cap-pack |
| **BMAD/MICRO 标记 action=inspect** | --apply 无法自动执行 | BMAD 需手动 content merge，MICRO 需手动降级 |
| **概念冗余检测基于命名+标签** | 不分析语义内容 | 人工确认每项合并建议 |

### 建议流程

```text
merge-suggest.py 输出建议
    ↓
[人工分类]
├── BMAD/MICRO → 手动执行（按本参考文档的步骤）
├── DUPLICATE/OVERLAP → --apply 自动合并
└── 降级 → 按场景 2 流程执行
    ↓
验证 + 提交
```
