---
name: pptx-analysis
description: PPT 深度理解与解析原子技能。循环分析流水线（树状递归+中间反思+process files），三层架构（结构解析→视觉分析→语义理解），27种设计缺陷检测。
version: 2.0.0
triggers:
- pptx analysis
- pptx-analysis
- PPT 深度理解
- PPT 解析
- 幻灯片分析
- slide analysis
- 设计缺陷检测
- CRAP 原则检测
- PPT 阅读理解
- 循环分析
- 深度分析
- 迭代精炼
- gleaning loop
metadata:
  hermes:
    tags:
    - powerpoint
    - pptx
    - presentation
    - slides
    - vision-analysis
    - design-flaws
    - cyclic-analysis
    - iterative-refinement
    category: productivity
    skill_type: doc-analysis
    format: pptx
depends_on:
  - analysis-workflow
  - mermaid-guide
design_pattern: Cyclic-Pipeline
---
# PPT 深度理解与解析 Skill v2.0

> **来源**：SlideAudit（UIST 2025）+ VLM-SlideEval（NeurIPS 2025）+ DocRefine + DocETL Gleaning + LongRefiner 树状结构
> **版本**：v2.0.0 | **日期**：2026-05-07

---

## 🔄 核心创新：循环分析流水线 (Cyclic Analysis Pipeline)

### 为什么需要循环？

传统单次分析（v1.0）只能提取表层信息。**SlideAudit 论文证明**：LLM 单次分析设计缺陷的 F1 仅 0.476~0.655，且对跨页叙事理解几乎无效。**VLM-SlideEval 论文建议**：使用 "critic-in-the-loop evaluators that drive iterative refinement"。

### 五阶段循环架构

```
Phase 1: 粗分析 (Coarse Analysis)
  ├─ 提取所有文本/表格/图片
  └─ 识别章节边界和主题
       ↓
Phase 2: 缺口检测 (Gap Detection)
  ├─ 识别信息缺失/模糊之处
  ├─ 标记需要深挖的知识点
  └─ 生成缺口报告 → 保存到 process_file
       ↓ (如有缺口)
Phase 3: 深潜分析 (Deep Dive Loop) ← 核心循环
  ├─ 对每个缺口进行深度分析
  ├─ 可触发子主题递归（树状下降）
  ├─ 可联网搜索补充信息
  ├─ 可渲染 Mermaid 图表辅助理解
  └─ 更新 process_file
       ↓
Phase 4: 交叉验证 (Cross-Validation)
  ├─ 对比多个来源验证一致性
  ├─ 检查逻辑自洽性
  └─ 标记已验证/待修正
       ↓
Phase 5: 树状合并 (Tree Merge)
  ├─ 子主题结果合并到父主题
  └─ 去重、排序、结构化输出
       ↓
┌─ 质量门禁 ←────────────────┐
│  评分 ≥ 80？ → ✅ 完成       │
│  评分 < 80？ → 🔄 进入下一轮  │
└──────────────────────────────┘
```

### Process File 机制

每轮分析的结果写入独立 process file，不累积在对话上下文中：

```
~/.hermes/learning/cycle-analysis/process_files/
├── topic_name/
│   ├── coarse_analysis.md      # Phase 1 输出
│   ├── gap_analysis.md         # Phase 2 输出
│   ├── deep_dive.md            # Phase 3 输出 (每次循环追加)
│   ├── validation_report.md    # Phase 4 输出
│   └── tree_merge.md           # Phase 5 输出
├── topic_name_subtopic1/
│   └── ...                     # 子主题独立分析
└── master_state.json           # 总状态机
```

### 状态管理命令

```bash
# 初始化
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py init "主题名"

# 管理进度
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py complete "主题名" coarse_analysis
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py fail "主题名" deep_dive "信息不足"
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py loop "主题名"
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py quality "主题名" 85

# 添加子主题（树状递归）
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py subtopic "主题名" "子主题名"

# 查看状态
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py status
```

### 树状递归处理

```
[父主题] 软件工程基本概念
  ├─ [子主题 1] 软件四大特性
  │   ├─ 复杂性 → 处理 → 验证 → ✅
  │   ├─ 可变性 → 处理 → 验证 → ✅
  │   ├─ 一致性 → 缺口→深潜→补充→✅
  │   └─ 不可见性 → 处理 → 验证 → ✅
  ├─ [子主题 2] 传统vs现代开发
  │   └─ 处理 → 验证 → ✅
  └─ [合并] → 输出完整章节分析
```

### 质量门禁评分公式

```
质量评分 = 信息覆盖度(30) + 交叉验证(25) + 可操作性(25) + 结构完整度(20)

评分 ≥ 80：✅ 通过，进入下一主题
评分 60-79：⚠️ 建议再循环一轮
评分 < 60：🔄 强制进入下一轮循环（最多 3 轮）
```

---

## 核心架构：三层能力

PPT 深度理解需要三层能力：

| Layer | 目标 | 工具 | 输出 |
|-------|------|------|------|
| **Layer 1: 结构解析** | 提取所有元素（文本、形状、图片、表格） | python-pptx | slide_texts[], slide_shapes[], slide_images[] |
| **Layer 2: 视觉分析** | 分析视觉特征（布局、颜色、图片内容） | Vision AI | layout_analysis, color_analysis, image_content |
| **Layer 3: 语义理解** | 理解内容语义（叙事、逻辑、设计质量） | LLM + Taxonomy | narrative_structure, design_flaws[] |

---

## Layer 1: 结构解析（python-pptx）

### 快速提取文本
```python
from pptx import Presentation

prs = Presentation('input.pptx')
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(shape.text_frame.text)
```

### 提取完整结构
```python
def parse_ppt_structure(pptx_path):
    prs = Presentation(pptx_path)
    slides_data = []
    
    for slide_idx, slide in enumerate(prs.slides):
        slide_data = {
            "index": slide_idx,
            "width": prs.slide_width / 914400,  # EMU → inches
            "height": prs.slide_height / 914400,
            "elements": []
        }
        
        for shape in slide.shapes:
            element = {
                "shape_id": shape.shape_id,
                "shape_type": str(shape.shape_type),
                "left": shape.left / 914400,
                "top": shape.top / 914400,
                "width": shape.width / 914400,
                "height": shape.height / 914400,
                "name": shape.name
            }
            
            if shape.has_text_frame:
                element["text"] = shape.text_frame.text
            
            if shape.has_table:
                table = shape.table
                element["table_rows"] = len(table.rows)
                element["table_cols"] = len(table.columns)
            
            if hasattr(shape, "image"):
                element["has_image"] = True
            
            slide_data["elements"].append(element)
        
        slides_data.append(slide_data)
    
    return slides_data
```

### 提取图片
```python
from PIL import Image
from io import BytesIO
import os

prs = Presentation('input.pptx')
os.makedirs('output_images/', exist_ok=True)

img_count = 0
for slide_idx, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if hasattr(shape, "image"):
            img_bytes = BytesIO(shape.image.blob)
            img = Image.open(img_bytes)
            img.save(f'output_images/slide_{slide_idx}_img_{img_count}.png')
            img_count += 1
```

---

## Layer 2: 视觉分析（Vision AI）

### PPT → 图片转换
```bash
# Step 1: PPT → PDF
libreoffice --headless --convert-to pdf --outdir /tmp/ppt_output/ input.pptx

# Step 2: PDF → PNG
pdftoppm -png -r 150 /tmp/ppt_output/input.pdf /tmp/ppt_output/
```

### Vision AI 分析
使用 `browser_vision` 或 `vision_analyze` 工具：
```python
# 每张幻灯片图片进行分析
for img_path in slide_images:
    analysis = vision_analyze(
        image_url=img_path,
        question="分析这张幻灯片的：1. 布局（元素位置、对齐方式、视觉层次）2. 颜色（配色方案、对比度）3. 图片内容（如果有图片）"
    )
```

---

## Layer 3: 语义理解（LLM + Taxonomy）

### 设计缺陷分类（27 种）

基于 SlideAudit 论文，27 种设计缺陷分为 5 大维度：

#### 维度 1: Composition & Layout（9 种）
| 缺陷 | 检测方法 |
|------|---------|
| Lack of Visual Hierarchy | Vision AI 层次识别 |
| Cluttered Layout | 元素数量 >32 |
| Unbalanced Space/Margin | 空间分布计算 |
| Misaligned Elements | grid alignment 检测 |
| Content Overflow | 元素超出边界 |
| Occluded Content | 元素重叠检测 |
| Lack of Navigation | 跨 slide 导航检查 |
| Inconsistent Layout | 跨 slide 布局对比 |
| Logical Flow Issues | LLM 叙事分析 |

#### 维度 2: Typography（6 种）
| 缺陷 | 检测方法 |
|------|---------|
| Illegible Typeface | 装饰化字体检测 |
| Inadequate Sizing | 字号 <24pt |
| Excessive Text Density | 6×6 rule（>6行或>6词/行） |
| Inconsistent Styling | 跨 slide 字体对比 |
| Improper Spacing | 行距/段落间距检测 |
| Lack of Text Hierarchy | 标题与正文对比度 |

#### 维度 3: Color（3 种）
| 缺陷 | 检测方法 |
|------|---------|
| Insufficient Contrast | WCAG 2.0 ratio <4.5 |
| Overuse/Inconsistent Color | 颜色数量 >5 |
| Jarring Combinations | Vision AI 颜色和谐性 |

#### 维度 4: Imagery（4 种）
| 缺陷 | 检测方法 |
|------|---------|
| Irrelevant Visuals | 图片语义匹配 |
| Low-Quality Images | 分辨率检测 |
| Improper Scaling | 宽高比检测 |
| Inconsistent Style | 跨 slide 图片风格对比 |

#### 维度 5: Animation（5 种）
| 缺陷 | 检测方法 |
|------|---------|
| Excessive Animations | 动画数量统计 |
| Inappropriate Timing | 动画时长检测 |
| Logic Errors | 动画顺序检测 |
| Distracting Transitions | 转场效果检测 |
| Inconsistent Animation | 跨 slide 动画风格对比 |

### 设计缺陷检测 Prompt 模板
```text
根据以下 27 种设计缺陷分类，评估这张幻灯片：

**Composition & Layout（9 种）**
- Lack of Visual Hierarchy: 无清晰视觉层次
- Cluttered Layout: 元素过载
- Unbalanced Space/Margin: 空间分布不均
- Misaligned Elements: 对齐不一致
- Content Overflow/Truncation: 内容溢出边界
- Occluded Content: 重要内容被遮挡
- Lack of Navigation Across Slides: 无导航指示
- Inconsistent Layout Across Slides: 布局不一致
- Content Logical Flow Issues: 逻辑不连贯

**Typography（6 种）**
- Illegible Typeface Usage: 字体不可读
- Inadequate Sizing: 字号不当
- Excessive Text Density: 文字过多
- Inconsistent/Distracting Text Styling: 字体样式不一致
- Improper Line/Paragraph Spacing: 间距不当
- Lack of Text Hierarchy: 无文字层次

**Color（3 种）**
- Insufficient Contrast: 对比度不足
- Overuse/Inconsistent Color: 颜色过多或不一致
- Poor/Jarring Color Combinations: 颜色组合刺眼

**Imagery（4 种）**
- Irrelevant/Off-topic Visuals: 图片与主题无关
- Low-Quality/Distorted Images: 图片质量差
- Improper Aspect Ratio/Size: 图片尺寸不当
- Inconsistent Visual Style: 图片风格不一致

**Animation & Interaction（5 种）**
- Excessive Animations: 动画过多
- Inappropriate Animation Timing: 动画时间不当
- Animation Logic Errors: 动画逻辑错误
- Distracting Transitions: 转场效果干扰
- Inconsistent Animation Across Slides: 动画风格不一致

请指出这张幻灯片存在哪些缺陷，并给出修复建议。

幻灯片内容：{slide_content}
```

---

## VLM 能力边界

| 能力 | GPT-4o | o3/GPT-5 | 建议 |
|------|--------|---------|------|
| **元素提取（≤8 elem）** | 88% | 99%+ | ✅ 推荐 GPT-5 |
| **元素提取（≥32 elem）** | 17% | 99%+ | ✅ 必须 GPT-5/o3 |
| **字体识别** | 17% | 42% | ⚠️ 需 python-pptx 补充 |
| **几何精度（IoU）** | 65% | 75% | ⚠️ 需 EMU 校准 |
| **叙事重构** | 困难 | 困难 | ❌ 需 LLM 专门处理 |

---

## 工具链决策树

```
PPT 深度理解任务
│
├─ 任务 1: 结构解析
│   └─ python-pptx（提取文本、形状、图片、表格）
│
├─ 任务 2: 视觉分析
│   ├─ PPT → 图片（LibreOffice: pptx→pdf→png）
│   └─ Vision AI（browser_vision / vision_analyze）
│
├─ 任务 3: 语义理解
│   ├─ LLM + Taxonomy（27 种设计缺陷）
│   └─ 叙事分析（开头→内容→总结）
│
└─ 任务 4: 质量评估
    ├─ Contrast Detection（WCAG 2.0 ≥ 4.5）
    ├─ Alignment Detection（grid alignment）
    ├─ Text Density（6×6 rule）
    └─ Design Flaws（27 taxonomy）
```

---

## 快速使用指南

### 场景 1: 提取 PPT 文本
```bash
python3 -c "
from pptx import Presentation
prs = Presentation('input.pptx')
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(shape.text_frame.text)
"
```

### 场景 2: 提取 PPT 图片
```bash
python3 -c "
from pptx import Presentation
from PIL import Image
from io import BytesIO
import os

prs = Presentation('input.pptx')
os.makedirs('output_images/', exist_ok=True)

for slide_idx, slide in enumerate(prs.slides):
    for shape_idx, shape in enumerate(slide.shapes):
        if hasattr(shape, 'image'):
            img_bytes = BytesIO(shape.image.blob)
            img = Image.open(img_bytes)
            img.save(f'output_images/slide{slide_idx}_img{shape_idx}.png')
"
```

### 场景 3: PPT 转图片（Vision AI 分析）
```bash
libreoffice --headless --convert-to pdf --outdir /tmp/ppt_output/ input.pptx
pdftoppm -png -r 150 /tmp/ppt_output/input.pdf /tmp/ppt_output/
```

---

## Pitfalls & Gotchas

1. **EMU 单位转换**：python-pptx 使用 EMU，1 inch = 914400 EMU
2. **VLM 字体识别弱**：字体信息应从 python-pptx 提取
3. **复杂幻灯片**：≥32 个元素时，必须使用 GPT-5/o3
4. **动画检测**：python-pptx 不支持动画解析，需检查 XML
5. **LibreOffice 路径**：确保 `libreoffice` 和 `pdftoppm` 已安装

---

## 参考资料

### 学术论文
- SlideAudit（arxiv 2508.03630）：27 种设计缺陷分类
- VLM-SlideEval（arxiv 2510.22045）：Vision AI 能力边界

### 官方文档
- python-pptx Shapes API：https://python-pptx.readthedocs.io/en/latest/api/shapes.html
- IBM Granite Vision：https://www.ibm.com/think/tutorials/ppt-ai-analyzer

### 相关 Skill
- pptx-guide：PPT 创建指南（CRAP 原则）
- powerpoint：PowerPoint 设计 Quick Reference