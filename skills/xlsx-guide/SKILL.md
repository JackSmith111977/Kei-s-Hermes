---
name: xlsx-guide
description: Excel (.xlsx) 电子表格操作原子技能。使用 openpyxl 创建带样式和图表的表格。
triggers:
- xlsx guide
- xlsx-guide
metadata:
  hermes:
    tags:
    - excel
    - xlsx
    - spreadsheet
    - data
    category: productivity
    skill_type: doc-generation
    format: xlsx
---
# Excel (.xlsx) 原子操作技能

> 库：`openpyxl` | 安装：`pip install openpyxl`
> 默认使用中文，除非用户特意说明。

## 快速开始

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

wb = Workbook()
ws = wb.active
ws.title = '数据表'
```

## 样式定义

```python
header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='4472C4', fill_type='solid')
center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)
alt_fill = PatternFill(start_color='F2F2F2', fill_type='solid')  # 斑马纹
```

## 写入带样式的数据

```python
headers = ['姓名', '部门', '工资', '绩效评分']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

data = [('张三', '研发', 15000, 4.5), ('李四', '产品', 12000, 4.2)]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        cell.border = thin_border
        if row_idx % 2 == 0:
            cell.fill = alt_fill
```

## 条件格式

```python
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule

# 色阶
ws.conditional_formatting.add('C2:C100',
    ColorScaleRule(start_type='min', start_color='F8696B',
                   mid_type='percentile', mid_value=50, mid_color='FFEB84',
                   end_type='max', end_color='63BE7B'))

# 数据条
ws.conditional_formatting.add('C2:C100',
    DataBarRule(start_type='min', end_type='max', color='4472C4'))
```

## 图表

```python
# 柱状图
chart = BarChart()
chart.title = "部门工资对比"
data = Reference(ws, min_col=3, min_row=1, max_row=10)
cats = Reference(ws, min_col=1, min_row=2, max_row=10)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws.add_chart(chart, 'E2')
```

## 公式与格式

```python
ws['C11'] = '=SUM(C2:C10)'
ws['C2'].number_format = '#,##0'       # 千分位
ws['D2'].number_format = '0.00%'       # 百分比
ws.freeze_panes = 'A2'                 # 冻结首行
ws.auto_filter.ref = 'A1:D100'         # 筛选

wb.save('output.xlsx')
```
