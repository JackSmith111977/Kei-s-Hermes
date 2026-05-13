---
name: xlsx-guide
description: Excel 表格操作快速入口 — openpyxl 核心代码速查
version: 1.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- xlsx guide
- xlsx-guide
- .xlsx 文件
metadata:
  hermes:
    tags:
    - xlsx
    - excel
    - quick-ref
    - redirect
    category: productivity
    skill_type: experience-quickref
---

# Excel 表格操作快速入口

> 💡 **完整文档生成请用 `pdf-layout` skill**。本 skill 保留 openpyxl 核心速查。

## 快速代码

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

wb = Workbook()
ws = wb.active
ws.title = "数据"
ws['A1'] = '标题'
ws['A1'].font = Font(bold=True, size=14)
data = [['姓名','分数'],['张三',95],['李四',88]]
for row in data:
    ws.append(row)
wb.save('output.xlsx')
```
