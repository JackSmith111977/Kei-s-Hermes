# Phase 1 执行记录 — hermes-cap-pack (2026-05-13)

> 从零创建第一个能力包（doc-engine）的完整实操记录。
> 作为能力包设计方法论的真实案例参考。

## 基本信息

- **项目**: ~/projects/hermes-cap-pack/
- **时间**: 2026-05-13
- **主人**: 已批准 Phase 0 → Phase 1 推进
- **第一阶段范围**: 格式规范 v1 + doc-engine 原型

## 执行步骤

### Step 1: 初始化 Git

```bash
git init && git branch -m main
# .gitignore: __pycache__/ .env .vscode/ node_modules/ *.log
git add -A && git commit -m "feat: initial project structure"
```

### Step 2: 设计格式规范

1. 先写 `schemas/cap-pack-format-v1.md` — 8 大字段组定义
2. 再写 `schemas/cap-pack-v1.schema.json` — 配套 JSON Schema
3. 最后写 `packs/doc-engine/cap-pack.yaml` — 实例数据

⚠️ **关键教训**：必须先 Schema 后 YAML。边写 YAML 边决定字段名导致 `capabilities` 字段在实例中变成扁平字段（`skills`/`experiences`/`mcp_servers` 直接挂在顶层而非 `capabilities` 子对象下）。格式规范定稿后再写实例，Schema 就是蓝本。

### Step 3: 创建 doc-engine 能力包

**技能选择**：从 `self-capabilities-map` 中提取所有属于"文档生成"领域的技能：
- pdf-layout, pdf-pro-design, pdf-render-comparison
- pptx-guide, docx-guide
- html-guide, markdown-guide
- latex-guide, epub-guide
- doc-design, vision-qc-patterns, readme-for-ai

**经验选择**：从实际踩坑记录中提取：
- `wqy-font-fallback` — 字体注册失败
- `reportlab-cjk-encoding` — UnicodeEncodeError
- `pptx-chinese-fonts` — 跨平台字体映射
- `pdf-tool-decision-tree` — WeasyPrint vs ReportLab vs LaTeX
- `design-crap-principles` — 排版设计原则

### Step 4: 验证

**发现的坑：YAML 日期解析**
```yaml
# ❌ 错误 — YAML 解析为 datetime.date 对象
created: 2026-05-13
# ✅ 正确 — 加引号后为字符串
created: '2026-05-13'
```

JSON Schema 验证捕获了此问题（`jsonschema.validate` 报 `datetime.date is not of type 'string'`）。

### Step 5: 提交

```bash
git add -A && git commit -m "feat: Phase 1 — format v1 and doc-engine prototype"
```
21 files changed, 1003 insertions.

## 结构决策记录

| 决策 | 选项 | 选定 | 理由 |
|:-----|:------|:----:|:------|
| 物理路径 | `cap-pack/` vs `packs/` | `packs/` | 多包管理，与 monorepo 约定一致 |
| 版本 | 0.x vs 1.x | 1.0.0 | 格式已可用，非实验期 |
| SKILLS 内容 | 引用 vs 复制 | 引用（指向源 Skill） | Phase 1 避免重复维护，Phase 2 再做完整复制 |
| 日期格式 | 裸值 vs 引号 | 引号包裹 | JSON Schema 要求 string 类型 |

## 未来改进

1. `capabilities` 顶层 vs 子对象 — 当前实例中 `skills`/`experiences`/`mcp_servers` 在顶层，而原始设计建议用 `capabilities.skills`。需决策是否调整。
2. MCP 目录 — doc-engine 当前无 MCP 依赖，`mcp_servers: []`。未来添加文档转换服务时再填充。
3. Hermes 适配器 — 当前能力包只是格式定义 + 数据，没有自动化安装脚本。
