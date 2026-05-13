# doc-engine SRA 改造前后发现测试数据

> 关联: capability-pack-design §六 | 测试日期: 2026-05-13
> SRA v1.2.1 | 350 skills indexed | `scripts/sra-discovery-test.py`

---

## Before (扁平结构, 17 skills)

### SRA 推荐

| 用户查询 | SRA Top-3 | 问题 |
|:---------|:-----------|:------|
| **生成PDF文档** | #1 docx-guide (66.5) ❌ #2 pdf-layout-weasyprint (66.5) #3 pdf-layout (65.5) | docx-guide 不相关；PDF 三碎片 |
| **用WeasyPrint生成中文PDF** | #1 pdf-layout-weasyprint (77.0) #2 pdf-layout-reportlab (72.8) #3 pdf-layout (68.2) | 用户需知精确技能名 |
| **ReportLab生成表格PDF** | #1 pdf-layout-weasyprint (72.5) #2 docx-guide (68.0) #3 pdf-layout (66.5) | WeasyPrint 排在 ReportLab 前 |
| **写LaTeX论文** | #1 latex-guide (59.5, SQS=45.2) 🔴 | 最低质技能排最前 |
| **生成Word文档** | #1 docx-guide (71.5, SQS=50.2) 🔴 | 微技能占首位 |
| **Markdown转PDF** | #1 markdown-guide (66.8, SQS=54.2) 🔴 | 微技能占首位 |

### 量化指标

```text
CHI: 0.6029 🟠 | 均SQS: 64.0 | 低分率: 6/17(35%) | 版本率: 10/17(59%)
```

### 三个根因

1. **微技能抢高位** — latex/docx/markdown 低质技能在相关查询排第一
2. **PDF 三碎片** — 三个 PDF 技能相互竞争，入口不统一
3. **不相关推荐** — "生成PDF"→#1 docx-guide(Word技能)

---

## 改造方案

| 操作 | 影响 | P |
|:-----|:------|:--:|
| 降级 6 微技能为经验 | 17→10技能, 低分率35%→0% | P0 |
| 合并 3 PDF 为 pdf-layout v3.0 | 统一入口 | P0 |
| 补充版本号+依赖声明 | 版本率 59%→100% | P1 |

### After 预期

```text
CHI: ≥ 0.75 🟢 | 均SQS: >75 | 低分率: 0% | 技能数: ~10
```

预期 SRA: "生成PDF"→#1 pdf-layout | "写LaTeX"→deep-research | 全查-无微技能占位

### 验证命令

```bash
# 健康度
python3 ~/projects/hermes-cap-pack/scripts/health-check.py [--json] [--gate]

# SRA 发现
python3 ~/projects/hermes-cap-pack/scripts/sra-discovery-test.py [--json] [--query "..."]

# 手动
curl -s http://127.0.0.1:8536/recommend -X POST -H 'Content-Type: application/json' \
  -d '{"message": "生成PDF文档"}'
```
