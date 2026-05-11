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
- patch 后语法错误
- patch 缩进问题
- patch 转义问题
- patch 返回成功但文件坏了
- mock_open call_args_list
- 测试 mock 写入内容验证
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

### 🚩 实战陷阱 1：patch 会转义 Python f-string 中的换行符

**场景**：修改 Python 文件中的 f-string 版本号。原始代码：
```python
            f"\n## SRA Runtime ({s.get('version', '1.1.0')})\n"
```
其中 `\n` 是 Python 源码中的**实际换行符**（不是字面量反斜杠-n）。当用 `patch()` 替换版本号时，patch 工具将实际换行符重新转义为字面量 `\\n`，导致文件内容变为：
```python
            f"\\n## SRA Runtime ({s.get('version', '1.2.1')})\\n"
```
`\\n` 在 Python 中变成字面量文本 `\n`，而不是换行。

**根因**：patch 工具的 `new_string` 参数在内部序列化时，对 Python 源码中的实际换行符（`\n`）做了二次转义。

**预防措施**：
- 修改含换行符的 f-string 时，先用 `read_file` 确认换行符是「实际换行」还是「源码中的 `\\n`」
- 如果 patch 后 diff 显示 `\\n` 比原文件多了反斜杠 → 需要第二遍 patch 修正
- 修正方法：重新 patch，用**实际换行符**（在 old_string 中按回车换行，不要写 `\n`）
- 或者：如果修改范围可控，直接用 `write_file` 重写整个函数/段落

**检测方法**：patch 后立即 `git diff` 检查，如果发现 `\n` 变成 `\\n` 或 `\\n` 变成 `\\\\n`，说明被二次转义了。

### 🚩 实战陷阱 2：patch 依赖缩进的代码（try/except/if/else）会破坏语法

**场景**：修复 Python 文件中的 `except: pass`。当你用 patch 替换 `except:` 时，如果 `old_string` 的缩进层次**只多了一个空格**或**少了一个空格**，patch 会把 `except` 行放到错误的位置：

```python
# 原代码（缩进正确，4 空格）
    try:
        do_something()
    except:
        pass

# patch 后 —— except 行缩进错误！
    try:
        do_something()
        except Exception as e:  # ← 缩进多了！语法错误
            pass
```

**更危险的情况**：patch 可能把 `except` 行放在 `if` 块内部，或者在 `try:` 后面留下一行孤立的 `try:` 语句（无 `except` 块匹配），导致 Python 报 `SyntaxError: expected 'except' or 'finally' block`。

**根因**：patch 工具的字符串匹配对**缩进极其敏感**。当你从 `read_file` 复制 old_string 时，编辑器/复制操作可能改变了空白的数量（比如 tab 变空格、多一个空格等）。

**预防措施**：
- **永远从 `read_file` 输出直接复制 old_string**，不要目测缩进然后手动输入
- 对于 try/except 块，old_string 必须包含完整的前后上下文（从 `try:` 到 `except:` 至少 4 行），确保唯一匹配且缩进正确
- patch 后**立即进行语法检查**：`python3 -c "import ast; ast.parse(open('file.py').read()); print('OK')"` 或 `python3 -m py_compile file.py`
- 如果 patch 后 `py_compile` 报语法错误 → **立即用 `write_file` 重写整个文件**，不要用第二遍 patch 修补

### 🚩 实战陷阱 3：patch 返回 exit_code=0 但文件语法错误

**场景**：patch 报告 `"success": true`，diff 看起来合理，但文件实际上有语法错误。

```bash
# patch 说成功
patch(path="file.py", old_string="...", new_string="...")
# → {"success": true, "diff": "..."}

# 但实际上：
python3 -m py_compile file.py
# → SyntaxError: invalid syntax
```

**为什么 patch 会无声地制造语法错误？**
- patch 是以**文本行**为单位运作的，不是 AST 级别。它不知道 Python 的语法结构
- 如果 `old_string` 匹配到了文件中的非目标位置（比如类似的 `except:` 在其他地方），替换后语法可能被破坏
- 如果替换的代码改变了代码块的嵌套层级（缩进变了），Python 语法检查才会发现问题

**强制验证流程（每次 patch 后必须执行）：**

```bash
# Python 文件
python3 -m py_compile modified_file.py

# 或用于多个文件
for f in $(git diff --name-only | grep '\.py$'); do
    python3 -m py_compile "$f" && echo "$f ✅" || echo "$f ❌"
done
```

**铁律**：patch 成功 ≠ 文件正确。**任何 patch 操作后，必须对修改过的源文件做语法检查。**

### 🚩 实战陷阱 4：mock_open.call_args_list 的 write 内容提取

**场景**：在 pytest 中验证 `mock_open().write()` 写入了什么内容。

```python
# ❌ 错误方式（call_args_list 返回 call 对象，不是 tuple）
handle = mock_file()
written = "".join(c[0] for c in handle.write.call_args_list)
# TypeError: sequence item 0: expected str instance, tuple found

# ✅ 正确方式（用 str(c) 把 call 对象转为字符串）
handle = mock_file()
all_writes = "".join(str(c) for c in handle.write.call_args_list)
assert "expected_content" in all_writes
# str(call('text')) == "call('text')"，所以内容会被 call() 包裹

# ✅ 更精确的方式（用 call_args）
handle = mock_file()
first_call_text = handle.write.call_args[0][0]  # 第一次调用的参数

# ✅ 最可靠的方式（拼接所有 write 调用的第一个参数）
handle = mock_file()
all_text = ""
for call_args in handle.write.call_args_list:
    all_text += call_args[0][0]
assert "expected_content" in all_text

# ✅ 或者直接用 assert_any_call 检查关键内容
handle.write.assert_any_call("expected_substring")
# 注意：assert_any_call 需要精确匹配整个参数，不适合部分匹配
```

**要点**：
- `call_args_list` 的元素是 `unittest.mock.call` 对象，不是裸 tuple
- 使用 `call_args[0][0]` 获取第一个位置参数
- 对于多行写入，逐一提取并拼接
- 如果只需确认内容包含某字符串，`str(call_obj)` 是最简单的近似方案
