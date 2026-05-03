# 数据格式操作指南（CSV/JSON/YAML/TOML）

## 格式选择指南

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| **CSV** | 简单表格，无嵌套 | 数据交换、Excel 导入、简单数据集 |
| **JSON** | 层级结构，无注释 | API 配置、NoSQL、前后端数据交换 |
| **YAML** | 可读性好，支持注释 | 配置文件、CI/CD、Docker Compose |
| **TOML** | 简洁，强类型 | 项目配置（Cargo/pyproject.toml） |
| **INI** | 最简单 | Windows 配置、简单设置 |
| **XML** | 严格，支持命名空间 | 企业数据交换、SOAP、配置文件 |

## JSON

```python
import json

# 读取
with open('config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 写入（美化输出）
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# 字符串操作
json_str = json.dumps(data, indent=2, ensure_ascii=False)
data = json.loads(json_str)
```

**最佳实践：**
- 键名用双引号
- 不支持注释（需要 JSON5）
- 不允许尾逗号
- 数字不补零（`1` 不是 `01`）
- 日期用 ISO 8601 字符串

## YAML

```python
import yaml

# 读取
with open('config.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# 写入
with open('output.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
```

**最佳实践：**
- 缩进用 2 空格
- 字符串一般不用引号，特殊字符用引号
- 多行字符串：`|` 保留换行，`>` 合并为一行
- 锚点和别名避免重复

```yaml
# 锚点和别名
default: &default
  adapter: postgresql
  encoding: unicode

development:
  <<: *default
  database: dev_db
```

## CSV

```python
import csv

# 读取
with open('data.csv', 'r', encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# 写入
with open('output.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'age', 'city'])
    writer.writeheader()
    writer.writerows(rows)

# 简单读写
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

**最佳实践：**
- 第一行必须是表头
- 包含逗号的字段用引号包裹
- UTF-8 编码
- 换行符：LF（Unix）或 CRLF（Windows）

## TOML

```python
import tomllib  # Python 3.11+ 内置

# 读取
with open('config.toml', 'rb') as f:
    data = tomllib.load(f)

# 写入（需要 tomli_w）
import tomli_w
with open('output.toml', 'wb') as f:
    tomli_w.dump(data, f)
```

```toml
# pyproject.toml 示例
[project]
name = "my-project"
version = "1.0.0"
description = "项目描述"
requires-python = ">=3.10"

[project.dependencies]
requests = "^2.28"
pandas = "^2.0"

[tool.black]
line-length = 88
target-version = ["py310"]
```

## 格式转换

```python
import json, yaml, csv

# JSON ↔ YAML
yaml_str = yaml.dump(json.loads(open('config.json').read()))
json_str = json.dumps(yaml.safe_load(open('config.yaml').read()), indent=2)

# CSV ↔ JSON
rows = list(csv.DictReader(open('data.csv', encoding='utf-8')))
json.dump(rows, open('data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

# JSON → CSV
data = json.load(open('data.json', encoding='utf-8'))
with open('data.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
```
