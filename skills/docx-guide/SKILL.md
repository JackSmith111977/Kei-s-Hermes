---
name: docx-guide
description: Word 文档操作快速入口 — python-docx 核心代码速查，完整排版请用 pdf-layout skill
version: 1.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- docx guide
- docx-guide
- .docx 文件
metadata:
  hermes:
    tags:
    - docx
    - word
    - quick-ref
    - redirect
    category: productivity
    skill_type: experience-quickref
---

# Word 文档快速入口

> 💡 **完整文档排版请用 `pdf-layout` skill**。本 skill 保留 python-docx 核心速查。

## 快速代码

```python
from docx import Document
from docx.shared import Inches, Pt

doc = Document()
doc.add_heading('文档标题', level=1)
p = doc.add_paragraph('正文内容')
table = doc.add_table(rows=3, cols=2)
table.style = 'Table Grid'
table.cell(0, 0).text = '姓名'
doc.save('output.docx')
```

> 💡 本 skill 已降级为 doc-engine 包的 experience。直接用法见 packs/doc-engine/EXPERIENCES/docx-quick-ref.md
