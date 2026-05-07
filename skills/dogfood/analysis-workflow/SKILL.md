---
name: analysis-workflow
description: 大文件分析与数据处理工作流——boku 处理大型文档、数据文件、代码库时的标准分析框架。涵盖分块策略、Map-Reduce 模式、渐进式摘要、内存管理等核心模式。
version: 1.0.0
triggers:
- 分析大文件
- 处理大型文档
- 分块处理
- chunking
- map reduce
- 流式处理
- 大文件分析
- 文档提炼
allowed-tools:
- terminal
- read_file
- write_file
- patch
- execute_code
- search_files
- delegate_task
metadata:
  hermes:
    tags:
    - analysis
    - workflow
    - chunking
    - map-reduce
    - streaming
    - memory-management
    category: dogfood
    skill_type: methodology
    design_pattern: meta-workflow
---

# 大文件分析与数据处理工作流 🧩📊

> **核心铁律：永远不要全量读取大文件到上下文中！分块、流式、渐进处理。**

## 零、问题诊断——boku 为什么会空响应？

当 boku 执行 `cat large_file.json` 时，54,000+ 字符直接注入对话上下文，**超过记忆容量**导致推理引擎中断。

**正确做法**：用 Python 脚本在终端内读取和处理，只输出结果摘要，不把原始数据塞进对话。

---

## 一、分析工作流总览——Split-Process-Merge 模式

源自 **GoTFlow** (Microsoft) 和 **DocETL** (UC Berkeley) 的三阶段模式：

```
Split (分) → Process (处理) → Merge (合)
```

### 1.1 何时触发此工作流？

| 场景 | 阈值 | 触发工作流 |
|------|------|-----------|
| 文本文件 > 10KB | ~3000 字符 | 分块读取 |
| JSON/CSV > 50 条记录 | ~50 items | 分批处理 |
| PPT/PDF > 50 页 | ~50 pages | 按章节分块 |
| 多文件 > 5 个文件 | ~5 files | 并行子代理 |
| 任何超过 4000 字符的上下文 | ~4000 chars | 绝不全量注入 |

---

## 二、阶段 1：Split（分块策略）

### 2.1 结构感知分块（Structural Chunking）⭐ 首选

**不要按字符数硬切！按语义边界切分！**

```python
# ❌ 错误：按字符数硬切
chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]

# ✅ 正确：按章节/标题切分
import json

# 读取 JSON 但不注入上下文——在脚本内处理
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 按章节/功能模块分块
for chapter in data:
    process_chapter(chapter)  # 一次只处理一个章节
    write_summary(chapter['name'], summary)
```

### 2.2 分块尺寸指南

| 用途 | 推荐大小 | 说明 |
|------|---------|------|
| 摘要/提炼 | 2000-4000 字符 | 约 500-1000 tokens |
| 深度分析 | 3000-6000 字符 | 保留完整语义上下文 |
| 代码文件 | 按函数/类切 | AST-aware，不切分代码块 |
| 表格数据 | 按行/表切 | 保持表结构完整 |

### 2.3 流式读取（Streaming/Generators）

```python
# ✅ 使用生成器，不一次性加载全部
def read_chunks(filepath, chunk_size=3000):
    with open(filepath, 'r', encoding='utf-8') as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(''.join(chunk)) >= chunk_size:
                yield ''.join(chunk)
                chunk = []
        if chunk:
            yield ''.join(chunk)

# 逐块处理，Python 自动 GC 已处理的块
for chunk in read_chunks('large_file.txt'):
    summary = process(chunk)  # 处理完即释放
    print(summary)
```

### 2.4 重叠分块（Overlap Chunking）

当信息可能跨边界时，使用 100-300 字符重叠：

```python
def overlapping_chunks(text, size=3000, overlap=200):
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i + size])
    return chunks
```

---

## 三、阶段 2：Process（处理模式）

### 3.1 Map-Reduce 模式（并行处理）⭐ 推荐

源自 **Google Cloud Workflows** 和 **LLM×MapReduce (ACL 2025)**：

```
Map（分治） → Collapse（压缩） → Reduce（汇总）
```

**步骤：**
1. **Map**：对每个 chunk 并行处理，提取要点
2. **Collapse**：如果结果仍太大，递归压缩
3. **Reduce**：汇总所有要点，生成最终输出

```python
# 伪代码：Map-Reduce 处理流程
chunk_summaries = []
for chunk in chunks:  # 可并行执行
    summary = extract_key_points(chunk)
    chunk_summaries.append(summary)

# Collapse（如果需要）
if len(''.join(chunk_summaries)) > 4000:
    chunk_summaries = compress_summaries(chunk_summaries)

# Reduce
final_output = synthesize(chunk_summaries)
```

### 3.2 渐进式精炼（Iterative Refinement）

源自 **DocETL 的 Gleaning** 模式：

```
初始提取 → 验证 → 精炼 → 验证 → ...（最多 3 轮）
```

```python
# DocETL Gleaning 模式
result = initial_extract(chunk)
for _ in range(2):  # 最多 2 轮精炼
    validator = validate(result)
    if validator['is_complete']:
        break
    result = refine(result, validator['missing'])
```

### 3.3 结构化信息协议

源自 **LLM×MapReduce (ACL 2025)**——每个 chunk 处理结果应包含：

```python
{
    "key_points": [...],        # 核心要点
    "reasoning": "...",          # 推理过程
    "confidence": 4,             # 置信度（1-5）
    "missing_info": [...],       # 缺失信息
    "page_ref": 42               # 页码/位置引用
}
```

### 3.4 处理模式选择决策树

```
需要处理大文件？
├── 只需提取关键信息？ → Map-Reduce（并行快）
├── 需要深度理解每部分？ → Iterative Refinement（质量高）
├── 需要回答具体问题？ → DocAgent 模式（先建大纲再定向检索）
└── 需要保留所有细节？ → Parent-Child Chunking（大 chunk 存上下文，小 chunk 检索）
```

---

## 四、阶段 3：Merge（合并与汇总）

### 4.1 合并策略

| 策略 | 适用场景 | 说明 |
|------|---------|------|
| **顺序合并** | 线性内容（文章、报告） | 按原始顺序拼接 |
| **结构化合并** | 表格/列表 | 按列/行合并，去重 |
| **主题合并** | 跨章节相关点 | 按主题归类合并 |
| **层级合并** | 大纲/目录 | 保持层级结构 |

### 4.2 合并时的冲突解决

源自 **LLM×MapReduce**：
- 使用 **置信度校准**：不同 chunk 对同一信息给出不同答案时，选择高置信度的
- 如果置信度相同，保留两者并标注

---

## 五、内存管理——boku 的自我保护

### 5.1 上下文窗口预算

| 组件 | 预算 |
|------|------|
| 用户消息 | ~1000 字符 |
| 系统提示 | ~3000 字符 |
| 工具调用参数/结果 | ~2000 字符 |
| **可用处理空间** | **~剩余部分** |
| **安全红线** | **单次注入 ≤ 4000 字符** |

### 5.2 内存泄漏防护

```python
# ✅ 正确：处理完立即释放
for chunk in chunks:
    result = process(chunk)
    save_to_disk(result)  # 存到文件，不累积在内存
    del result  # 显式释放

# ❌ 错误：累积所有结果
all_results = []
for chunk in chunks:
    all_results.append(process(chunk))  # 内存爆炸！
```

### 5.3 boku 的行为规范

1. **永远不用 `cat` 读取大文件**——用 Python 脚本在终端内处理
2. **永远不一次性 `read_file` 超过 2000 行**——用 `offset` + `limit` 分页读取
3. **处理结果写入文件**——不累积在对话中
4. **用 `delegate_task` 并行处理独立子任务**——每个子代理有独立上下文
5. **每处理完一个 chunk 就汇报进度**——让主人知道 boku 在工作，不会以为卡住了

---

## 六、实战案例——PPT 分析的正确姿势

### ❌ 错误做法（导致空响应）

```bash
# 把 54000 字符注入对话上下文
cat ppt_extracted.json
# 💥 BOOM！上下文爆炸，boku 空响应
```

### ✅ 正确做法（Map-Reduce）

```python
# 在终端内读取、处理、写入——不注入对话上下文
import json

with open('ppt_extracted.json', 'r') as f:
    data = json.load(f)

# Map：逐章提炼
for chapter in data:
    summary = extract_key_points(chapter)
    html_sections.append(generate_html(summary))

# Reduce：合并所有章节
final_html = merge_and_format(html_sections)
write_file('output.html', final_html)

# 只输出简短结果到对话
print("✅ 处理完成！共 9 章，生成 18 页 PDF")
```

---

## 七、工具链推荐

| 任务 | 工具 | 说明 |
|------|------|------|
| 读取大文件 | `execute_code` + Python 脚本 | 在沙箱内处理，不注入上下文 |
| 超长文本 | `read_file` + offset/limit | 分页读取，每次 ≤ 2000 行 |
| 并行处理 | `delegate_task` | 每个子代理独立上下文 |
| 存储中间结果 | `write_file` | 写入临时文件，不累积在内存 |
| 搜索文件 | `search_files` | 内容搜索，不读取全文 |

---

## 八、性能参考

| 操作 | 时间 | 说明 |
|------|------|------|
| 读取 188 页 PPT 文本 | ~5 秒 | Python 脚本终端内 |
| 单章提炼 | ~3-10 秒 | 取决于章节复杂度 |
| 9 章逐章处理 | ~30-60 秒 | 串行处理 |
| HTML 生成 | ~2 秒 | 纯 Python 字符串拼接 |
| PDF 生成（WeasyPrint）| ~3-5 秒 | 系统级工具 |
| **总计** | **~45-75 秒** | 完整流程 |

---

## 九、检查清单

处理大文件前，boku 必须自查：

- [ ] 文件大小是否超过 10KB？→ 分块处理
- [ ] 是否使用 `cat`/`head` 读取？→ 改用 Python 脚本
- [ ] 是否会把结果注入对话？→ 写入文件，只输出摘要
- [ ] 是否需要并行处理？→ 考虑 `delegate_task`
- [ ] 是否每步都汇报进度？→ 让主人知道进展
