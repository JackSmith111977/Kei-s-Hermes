# doc-engine 健康诊断实战案例

> 2026-05-13 首次完整诊断结果

## 诊断命令

```bash
cd ~/projects/hermes-cap-pack

# Step 1: 树状索引
python3 scripts/skill-tree-index.py --pack doc-engine --json

# Step 2: SQS 逐个评分（17 个技能）
for skill in pdf-layout pdf-layout-reportlab pdf-layout-weasyprint pdf-pro-design pdf-render-comparison doc-design docx-guide html-guide html-presentation pptx-guide latex-guide markdown-guide epub-guide xlsx-guide readme-for-ai vision-qc-patterns nano-pdf; do
  python3 scripts/skill-quality-score.py "$skill" --json
done

# Step 3: 综合健康测量
python3 scripts/health-check.py --json
```

## Before 基线

| KPI | 测量值 | 评级 |
|:----|:------:|:----:|
| KPI-1 平均 SQS | 64.0/100 | 🟡 |
| KPI-2 低分率 | 6/17 (35%) | 🔴 |
| KPI-3 版本完整率 | 10/17 (59%) | 🔴 |
| KPI-4 关联完整率 | 6.9/20 | 🔴 |
| KPI-5 簇数 | 12 簇 (std 1.2) | 🟢 |
| KPI-6 技能总数 | 17 | 🔴 |
| **CHI 综合健康指数** | **0.6029** | 🟠 |

## 发现的问题

1. **6 个微技能** SQS < 60（latex/html/epub/xlsx/docx/markdown），无版本号
2. **5 个 PDF 技能** 重叠 70-90%，可合并
3. **S4 关联性** 普遍 5/20 — 缺少 depends_on 声明
4. **7 个技能** 版本号为 "?"

## 改造方案

详见 `packs/doc-engine/restructure-plan.md` 和 `packs/doc-engine/cap-pack-v2.yaml`

## 量化结论

✅ **可量化测试完全可行** — 每次改造后执行 `python3 scripts/health-check.py --json` 即可准确对比 CHI 变化
