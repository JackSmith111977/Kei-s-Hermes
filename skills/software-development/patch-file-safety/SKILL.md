---
name: patch-file-safety
description: 安全使用 patch 工具的最佳实践指南——何时用 patch、何时用 write_file、什么时候该重写整个文件。避免大块替换污染文件的风险。
version: 1.0.0
triggers:
- 需要修改代码文件
- patch 工具遇到问题
- 文件被 patch 污染了
- 如何安全编辑文件
- 大块替换代码
allowed-tools:
- read_file
- write_file
- patch
- terminal
- execute_code
metadata:
  hermes:
    tags:
    - patch
    - file-edit
    - safety
    - code-modification
    category: software-development
    skill_type: library-reference
    design_pattern: tool-wrapper
---
# patch-file-safety: 安全文件编辑指南 🛠️

## 一、工具选择决策树

```
需要修改文件？
├─ 改动 1-3 行，字符串唯一 → ✅ patch（安全）
├─ 改动 1-3 行，多处相同 → ✅ patch(replace_all=true)
├─ 改动 4+ 行，但只有一处 → ⚠️ patch（有风险，确保 old_string 包含上下文）
├─ 改动 4+ 行，多处 → ❌ write_file 重写整个文件
├─ 插入/删除一段代码 → ⚠️ patch（先 read_file 看清周围代码）
└─ 重构/重写函数 → ✅ write_file 重写整个文件
```

## 二、patch 安全操作规范

### 2.1 通用规则
- **永远先 read_file** 看清待修改区域
- **old_string 必须包含足够上下文**（至少前后各 2 行）
- **检查 diff**：patch 返回后立即查看修改是否超出预期
- **立即验证**：用 read_file 或语法检查确认文件完整

### 2.2 Do's and Don'ts

✅ **做：**
```python
patch(
    path="file.py",
    old_string="def old_function():\n    \"\"\"旧的文档字符串\"\"\"\n    return 42",
    new_string="def old_function():\n    \"\"\"新的文档字符串\"\"\"\n    return 43"
)
```

❌ **不做：**
```python
patch(
    path="file.py",
    old_string="def old_function():",
    new_string="def new_function():"  # 太短，可能匹配到多个地方
)
```

### 2.3 patch 污染后怎么恢复

如果 patch 污染了文件（吞了行、改乱了变量），**不要继续用 patch 修补**：

```
1. read_file(path) 看清当前状态
2. write_file(path, correct_content) 直接用正确内容重写
3. 验证文件完整性
```

## 三、什么时候必须用 write_file 重写

| 场景 | 原因 |
|:---|:---|
| 整个函数/类的重写 | patch 的大块替换容易吞相邻代码 |
| 超过 30 行的修改 | patch 匹配成功率随长度下降 |
| 插入一整块新代码到中间 | patch 可能找不到唯一位置 |
| 文件已经受过一次 patch 污染 | 继续 patch 只会更乱 |
| 修改配置文件/JSON/YAML | 结构文件最易被 patch 破坏 |

## 四、write_file 的正确用法

```python
# 先读取原文件
content = read_file("target.py")["content"]

# 输出原文件内容 → 手动修改后写回
# 或者直接从零构建新内容
write_file("target.py", """
def new_function():
    return "这个文件被完整重写了"
""")
```

## 五、execute_code 里的 patch 沙箱技巧

```python
from hermes_tools import read_file, write_file, patch, terminal

# 1. 先确认文件内容
orig = read_file("config.yaml")
print(orig["content"])

# 2. 如果是小改动（<3行），用 patch
result = patch("config.yaml", "old_value", "new_value")

# 3. 如果是大改动，用 write_file 方式
new_yaml = orig["content"].replace("old_part", "new_part")
# ... 更多修改 ...
write_file("config.yaml", new_yaml)
```

## 六、边界情况

| 边界情况 | 处理方式 |
|:---|:---|
| old_string 在文件中有多处匹配 | 用 `replace_all=true`，或用更独特的上下文 |
| 文件是二进制/非 UTF-8 | 用 terminal() 配合 sed/awk |
| 文件巨大（1000+ 行） | 先 read_file 分段读，精确定位修改区域 |
| patch 返回 exit_code=0 但 diff 奇怪 | 立即 read_file 验证，不要继续信任 |

## 七、验证清单

每次文件修改后检查：

- [ ] read_file 确认修改位置正确
- [ ] 没有吞掉/修改了不该动的代码
- [ ] Python/JS/YAML 语法正确（对可解析格式）
- [ ] git diff（如有）确认只有预期改动

## 八、经验教训

1. **patch 是手术刀，不是砍刀** — 适合精准小改动，不适合大块替换
2. **文件被污染后不要尝试修补** — write_file 重写更安全
3. **永远先 read_file** — 不要凭记忆写 old_string
4. **替换后立即验证** — 不要等到后面再查
