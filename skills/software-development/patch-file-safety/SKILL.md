---
name: patch-file-safety
description: 安全使用 patch 工具的最佳实践指南——何时用 patch、何时用 write_file、什么时候该重写整个文件。避免大块替换污染文件的风险。
version: 1.2.0
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

### 🚩 实战陷阱 6：multi-line old_string 中的换行符被转义为 \n

**场景**：用 patch 工具替换多行文本（如 markdown 文档中的一段验收标准列表）。例如替换 EPIC-003.md 中的多行 AC：

```python
# old_string 有多行，直接写在字符串中：
patch(
    path="docs/EPIC-003.md",
    old_string="- [ ] 映射表作为配置文件，支持用户自定义扩展\n- [ ] 在 `/validate` 端点中集成文件类型检查",
    new_string="- [x] 映射表作为配置文件，支持用户自定义扩展\n- [x] 在 `/validate` 端点中集成文件类型检查"
)
```

patch 成功后查看文件，发现换行符被转义为字面量 `\\n`：
```
- [ ] 映射表作为配置文件，支持用户自定义扩展\\n- [ ] 在 `/validate` 端点...
```

**根因**：patch 工具在序列化多行 old_string/new_string 时，对实际换行符做了二次转义。这与 §8 实战陷阱 1 的 f-string 转义类似，但触发条件不同——只要 old_string 或 new_string 包含**字面量换行符**（而非 `\n` 转义序列），就可能被二次转义。

**诊断方法**：patch 后立即 `read_file` 查看被修改的区域，检查是否有 `\n` 变成 `\\n` 或 `\\n` 变成 `\\\\n`。

**预防措施**：

1. **首选方案**：用 `execute_code` 沙箱 + `hermes_tools.patch` 绕开转义问题：
   ```python
   from hermes_tools import patch
   result = patch(path, old_string, new_string)
   # execute_code 沙箱中的 patch 不会出现转义问题
   ```

2. **次选方案**：old_string 和 new_string 用**实际换行符**（按回车）写，但将 patch 作为 `execute_code` 中的 Python 调用来执行（从主会话调用也会触发转义）。

3. **第三方案**：如果 patch 已经被转义污染，用第二遍 patch 把 `\\n` 替换回实际换行符：
   ```python
   # 第一遍 patch 后文件内容变成了 \\n，修复：
   patch(path, old_string="\\n", new_string="\n")
   # 注意：old_string 中写字面量 \\n，new_string 中写实际换行
   ```

4. **兜底方案**：如果文件已有多处转义污染，直接用 `write_file` 完整重写。

**验证流程**（patch 多行内容后强制执行）：
```bash
# 对 Python 文件
python3 -m py_compile modified_file.py

# 对 markdown 文件——检查是否有异常转义
grep -n '\\\\n' modified.md && echo "⚠️ 发现转义污染" || echo "✅ 无转义污染"
```

**铁律**：每次 patch 多行文本内容后，**必须检查转义污染**。尤其是 markdown 文档、配置文件、代码注释等非可执行文件——它们不会被语法检查器发现。

**场景**：用 `replace_all=true` 替换文件中多处相同的文本行，但该文本出现在**不同嵌套深度**的代码块中。例如：

```python
# 文件中有 6 处 print("⚠️  SRA Daemon 未运行，使用本地模式")
# 其中 4 处是顶级 if 块：
if "error" in result:
    print("⚠️  SRA Daemon 未运行，使用本地模式")  # ← 缩进 4 空格

# 另外 2 处嵌套在二级 if 块内：
if "error" in result:
    if "未运行" in result.get("error", ""):
        print("⚠️  SRA Daemon 未运行，使用本地模式")  # ← 缩进 8 空格
```

当用 `replace_all=true` 把 `print` 替换为 `logger.warning(...)` + `print` 双行时，**所有 6 处都被替换**，但 `new_string` 的缩进基于第一处匹配的上下文（4 空格）：

```python
# 结果：二级 if 块的缩进被破坏！
if "error" in result:
    if "未运行" in result.get("error", ""):
        logger.warning("SRA Daemon 未运行，使用本地模式")
    print("⚠️  SRA Daemon 未运行，使用本地模式")  # ← 缩进回退到 4 空格！
        # ← 下面的原有代码缩进还停留在 8 空格，语法错误
```

**根因**：`replace_all=true` 用**相同的 `new_string` 替换所有匹配**，不感知每个匹配处周围的缩进上下文。`new_string` 中硬编码的缩进只能匹配一种嵌套层级。

**预防措施**：

1. **先 grep 确认上下文的统一性**：
   ```bash
   # 检查匹配行的上下文是否一致
   grep -B2 "print.*SRA Daemon" cli.py | head -20
   # 观察：是否有的前面是 if 语句，有的前面是另一个 if？
   ```

2. **`replace_all=true` 仅适用于纯文本内容（字符串字面量、版本号、URL）**，不适用于包含缩进的代码块替换

3. **如果匹配行出现在多种缩进上下文** → 使用多个独立的 patch 调用，每个定位一种上下文：
   ```python
   # patch 1: 4 空格缩进版本（顶级 if）
   patch(path, old_string="    print(...)", new_string="    logger.warning(...)\n    print(...)")
   
   # patch 2: 8 空格缩进版本（二级 if）  
   patch(path, old_string="        print(...)", new_string="        logger.warning(...)\n        print(...)")
   ```
   每个 patch 的 `old_string` 包含足够的上下文（前后各 1 行）确保唯一匹配。

4. **验证法则**：`replace_all` 后必须做两件事：
   - `python3 -m py_compile file.py` — 语法检查（原样漏语法错误）
   - `grep -n "your_pattern" file.py` — 检查替换后每一处的缩进是否一致

5. **安全替代方案**：当替换涉及代码结构（非纯字符串），且有多处但不同上下文，直接用 `write_file` 重写整个函数/块，避免 patch 的多处替换风险。

**检测方法**：`replace_all` 后立即 `python3 -m py_compile` 检查语法。如果语法正确但缩进可疑，用 `grep -n` 或 `cat -A` 查看每行的前导空格。最彻底的检测：`read_file` 逐一检查所有被替换的位置。此陷阱不会产生错误提示——patch 返回 `success: true`，文件也合法——但生成不正确的缩进的代码。

### 🚩 实战陷阱 7：批量字符串替换时短字符串被长字符串的子串提前匹配

**场景**：批量重命名文档 ID，如把 `STORY-1-10` 统一替换为 `STORY-1-4-3`，同时把 `STORY-1-1` 替换为 `STORY-1-1-1`。用 Python 脚本遍历字典做 `str.replace()`：

```python
# ❌ 危险方式：按字典顺序替换
replacements = {
    'STORY-1-1': 'STORY-1-1-1',   # 先替换短字符串
    'STORY-1-10': 'STORY-1-4-3',  # 后替换长字符串
}

for old, new in replacements.items():
    content = content.replace(old, new)
```

处理后，`STORY-1-10` 变成了 `STORY-1-1-10`（因为 `STORY-1-10` 中包含了 `STORY-1-1` 子串，被提前匹配变成了 `STORY-1-1-10`，然后 `STORY-1-10` 已不再存在，后一轮替换轮空）。

**表现形式**：
- `STORY-1-10` → `STORY-1-1-10` ❌（本应是 `STORY-1-4-3`）
- `test_version_2` → 被 `test_version` 提前替换
- `SPEC-001` → 被 `SPEC-0` 子串匹配

**根因**：`str.replace()` 不做「最长匹配优先」。短字符串如果是长字符串的前缀，长字符串会在短字符串的替换中被破坏，导致后续再也无法匹配。

**预防措施**：

```python
# ✅ 安全方式1：按字符串长度降序排列（最长优先）
replacements = {
    'STORY-1-10': 'STORY-1-4-3',   # 长字符串先替换
    'STORY-1-9': 'STORY-1-4-2',
    'STORY-1-1': 'STORY-1-1-1',    # 短字符串后替换
}

for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
    content = content.replace(old, new)

# ✅ 安全方式2：用正则的词边界确保完整词匹配
import re
for old, new in replacements.items():
    content = re.sub(r'\b' + re.escape(old) + r'\b', new, content)
```

**检测方法**：替换后检查结果中是否有异常模式：

```bash
# 检查是否出现了不该出现的组合
grep -n 'STORY-1-1-1[0-5]' output.md
```

**铁律**：批量字符串替换时，**永远按字符串长度降序排列**。或者使用带词边界检测的正则替换。替换后必须做**反向验证**——检查目标格式中是否混入了不应该出现的源模式。

### 🚩 实战陷阱 8：TOML + regex + patch 工具 = 三重转义地狱

**场景**：用 patch 工具修改 `pyproject.toml` 中的 `tag_regex` 正则表达式。期望 TOML 中的 regex 字符串是 `^(?:[\w-]+-)?v?(?P<version>[\d\.]+)$`（`\w` = 单词字符）。

```python
# ❌ 危险：在 patch 的 new_string 中写 \w（意图 TOML 中得到 \w）
patch(
    path="pyproject.toml",
    old_string='tag_regex = "^(?:[\\\\w-]+-)?v?(?P<version>[\\\\d\\\\.]+)$"',
    new_string='tag_regex = "^(?:[\\\\w-]+-)?v?(?P<version>[\\\\d\\\\.]+)$"'
)
```

结果：patch 工具对 `\\w` 做了二次转义 → TOML 中得到 `\\\\w`（4 个反斜杠）→ Python regex 编译为 `\\w`（匹配字面量反斜杠 + w）→ **所有 tag 匹配失败**。

**转义链解析（三层地狱）**：

```
Layer 1: patch 工具的 new_string 参数（Python 字符串）
  \\\\w  → 文件内容得到 \\w     ← patch 可能二次转义

Layer 2: TOML 解析器解读文件内容
  \\w    → 字符串得到 \w       ← TOML 解译 \\ → \

Layer 3: Python re.compile() 解读字符串
  \w     → 单词字符            ← 正确！

问题：如果 patch 工具二次转义 \\\\w → \\\\\w（文件内容变成 4 个反斜杠）
  TOML 解译: \\\\w → \\w
  Python regex: \\w → 匹配字面量反斜杠 + w ❌
```

**诊断方法**（patch TOML regex 后立即执行）：

```python
import tomllib, re
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
pattern = data['tool']['setuptools_scm']['tag_regex']
print(repr(pattern))  # 检查实际字符串
# 如果看到 \\w → 二次转义了，应为 \w

r = re.compile(pattern)
print(r.match('v2.1.0'))  # 应为 <re.Match>，不能是 None
```

**预防方案**（按优先级）：

| 方案 | 操作 | 适用场景 |
|:----|:-----|:---------|
| ⭐ **首选** | TOML 单引号字符串 `'...'` 彻底绕过转义 | `tag_regex = '^(?:[\\w-]+-)?v?(?P<version>[\\d\\.]+)$'` |
| **次选** | `write_file` 完整重写整个 TOML section | 多行改动，避免 patch 的转义干扰 |
| **备选** | `execute_code` + `hermes_tools.patch` 沙箱执行 | 需要 patch 但受转义困扰时 |
| **最后** | 手动逐层检查转义正确后 patch | 只有单处小改动 |

**为什么 TOML 单引号字符串（literal string）能根治**？

```toml
# ❌ 基本字符串（双引号）：\\ 是转义前缀
tag_regex = "^(?:[\\w-]+-)?..."

# ✅ 字面量字符串（单引号）：无转义，内容原样保留
tag_regex = '^(?:[\w-]+-)?...'
```

在 TOML 单引号字符串中，`\w` 保持为 `\w`，被 Python 的 `re.compile()` 正确解读为单词字符。**patch 工具无法「过度转义」单引号字符串，因为 TOML 解析器不会对单引号内容做任何转义。**

**铁律**：在 `pyproject.toml`、`setup.cfg` 等 TOML 格式文件中写入正则表达式时，**永远使用 TOML 字面量字符串（单引号 `'...'`）**。如果该区域需要批量修改，用 `write_file` 完整重写 section，不要用 `patch` 逐段替换。
