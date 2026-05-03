# Excel (.xlsx) 完整操作指南

> 库：`openpyxl` | 安装：`pip install openpyxl`

## 基础操作

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

wb = Workbook()
ws = wb.active
ws.title = '数据表'
```

## 样式定义（复用）

```python
# 标题样式
header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='4472C4', fill_type='solid')
center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_align = Alignment(horizontal='left', vertical='center')
right_align = Alignment(horizontal='right', vertical='center')

thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# 数据样式
data_font = Font(name='Arial', size=11)
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

# 数据行（带斑马纹）
data = [
    ('张三', '研发', 15000, 4.5),
    ('李四', '产品', 12000, 4.2),
    ('王五', '设计', 13000, 4.8),
]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        cell.font = data_font
        cell.border = thin_border
        cell.alignment = center_align
        if row_idx % 2 == 0:
            cell.fill = alt_fill
```

## 列宽行高

```python
ws.column_dimensions['A'].width = 12
ws.column_dimensions['B'].width = 15
ws.column_dimensions['C'].width = 12
ws.column_dimensions['D'].width = 12
ws.row_dimensions[1].height = 30

# 自动调整列宽（基于内容长度）
for col in ws.columns:
    max_length = 0
    col_letter = get_column_letter(col[0].column)
    for cell in col:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[col_letter].width = max_length + 4
```

## 合并单元格

```python
ws.merge_cells('A1:D1')
ws['A1'].value = '员工信息表'
ws['A1'].font = Font(size=16, bold=True)
ws['A1'].alignment = center_align
```

## 条件格式

```python
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, DataBarRule

# 色阶（红-黄-绿）
ws.conditional_formatting.add(
    'C2:C100',
    ColorScaleRule(
        start_type='min', start_color='F8696B',
        mid_type='percentile', mid_value=50, mid_color='FFEB84',
        end_type='max', end_color='63BE7B'
    )
)

# 数据条
ws.conditional_formatting.add(
    'C2:C100',
    DataBarRule(start_type='min', end_type='max', color='4472C4')
)

# 规则格式（如：大于 10000 标绿）
green_fill = PatternFill(start_color='C6EFCE', fill_type='solid')
ws.conditional_formatting.add(
    'C2:C100',
    CellIsRule(operator='greaterThan', formula=['10000'], fill=green_fill)
)
```

## 图表

```python
# 柱状图
chart = BarChart()
chart.title = "部门工资对比"
chart.y_axis.title = "工资"
chart.x_axis.title = "姓名"
chart.style = 10

data = Reference(ws, min_col=3, min_row=1, max_row=10)
cats = Reference(ws, min_col=1, min_row=2, max_row=10)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4
ws.add_chart(chart, 'E2')

# 折线图
line = LineChart()
line.title = "趋势图"
line.y_axis.title = "数值"
data = Reference(ws, min_col=2, min_row=1, max_row=10)
line.add_data(data, titles_from_data=True)
ws.add_chart(line, 'E20')

# 饼图
pie = PieChart()
pie.title = "部门占比"
labels = Reference(ws, min_col=2, min_row=2, max_row=10)
data = Reference(ws, min_col=3, min_row=1, max_row=10)
pie.add_data(data, titles_from_data=True)
pie.set_categories(labels)
ws.add_chart(pie, 'E38')
```

## 公式

```python
ws['C11'] = '=SUM(C2:C10)'
ws['D11'] = '=AVERAGE(D2:D10)'
ws['E2'] = '=C2/SUM($C$2:$C$10)'  # 百分比
ws['E2'].number_format = '0.00%'
```

## 冻结窗格

```python
ws.freeze_panes = 'A2'  # 冻结第一行
ws.freeze_panes = 'B2'  # 冻结第一行+第一列
```

## 筛选

```python
ws.auto_filter.ref = f'A1:D100'
```

## 数字格式

```python
ws['C2'].number_format = '#,##0'       # 千分位整数
ws['C3'].number_format = '#,##0.00'    # 千分位两位小数
ws['D2'].number_format = '0.00%'       # 百分比
ws['E2'].number_format = 'YYYY-MM-DD'  # 日期
```

## 保存与读取

```python
wb.save('output.xlsx')

# 读取
wb2 = load_workbook('output.xlsx', data_only=True)  # data_only 读取公式计算值
ws2 = wb2.active
for row in ws2.iter_rows(min_row=1, max_row=10, values_only=True):
    print(row)
```
