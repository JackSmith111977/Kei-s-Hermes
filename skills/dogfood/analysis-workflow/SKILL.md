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
> **v2.0 新增：循环深度分析流水线 (Cyclic Deep Analysis Pipeline)**

---

## 🔄 循环深度分析流水线 (v2.0 核心创新)

### 为什么需要循环？

传统的 Split-Process-Merge（v1.0）是一次性线性处理，无法应对：
- **复杂主题**：需要多层次理解（如 PPT 中一个概念跨多页展开）
- **信息缺口**：单次扫描可能遗漏关键信息
- **交叉依赖**：文档前后内容互相引用
- **质量不可控**：没有验证环节，无法自我纠错

### 五阶段循环分析架构

受 **SlideAudit（UIST 2025）**、**VLM-SlideEval（NeurIPS 2025）**、**DocETL Gleaning** 和 **LongRefiner 树状结构** 启发：

```
文档输入 → Phase 1: 粗分析 → Phase 2: 缺口检测
                ↓                    ↓
         结构感知分块          识别信息缺失/模糊
         提取文本/图片         生成缺口优先级
                ↓                    ↓
    ┌──── Phase 3: 深潜分析 (核心循环) ────┐
    │  按优先级处理每个缺口                   │
    │  复杂缺口 → 触发子主题递归（树状下降）    │
    │  信息不足 → 联网搜索补充                │
    │  图表缺失 → 渲染 Mermaid                │
    └─────────────────────────────────────────┘
                ↓
         Phase 4: 交叉验证
         对比来源/检查自洽
                ↓
         Phase 5: 树状合并
         子主题合并/去重/结构化
                ↓
         质量门禁 (Quality Gate)
         评分 ≥ 80？→ ✅ 完成
         评分 < 80？→ 🔄 下一轮
```

### Process File 机制

每轮分析结果写入独立文件，不累积在对话上下文中：

```
~/.hermes/learning/cycle-analysis/process_files/
├── topic_name/
│   ├── coarse_analysis.md      # 粗分析输出
│   ├── gap_analysis.md         # 缺口列表
│   ├── deep_dive.md            # 深潜输出（循环追加）
│   ├── validation_report.md    # 验证报告
│   └── tree_merge.md           # 合并结果
├── topic_name_subtopic/        # 子主题
└── master_state.json           # 总状态机
```

### 状态管理命令

```bash
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py init "任务名"
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py complete "任务名" coarse_analysis
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py status
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py quality "任务名" 85
python3 ~/.hermes/learning/cycle-analysis/scripts/cycle-state.py loop "任务名"
```

### 循环触发逻辑

```python
while loop_count < max_loops and quality_score < 80:
    gaps = detect_gaps(current_output)    # Phase 2
    if not gaps: break
    current_output = deep_dive(gaps)      # Phase 3
    verified = cross_validate(current_output)  # Phase 4
    quality_score = calculate_quality(verified)
    loop_count += 1
```

### 跨文件类型适用性

| 文件类型 | 分块策略 | 缺口检测重点 | 树状结构 |
|:---|:---|:---|:---|
| **PPT** | 按章/页分 | 设计缺陷、叙事断点 | 章→节→子节 |
| **PDF 报告** | 按章节分 | 数据缺失、逻辑跳跃 | 章→节→论点 |
| **代码库** | 按模块分 | 注释缺失、边界条件 | 模块→类→方法 |
| **CSV/数据** | 按列/行分 | 空值、异常值 | 表→列→统计 |

## ⚠️ 空响应预防（保障输出不丢失）🚨

**背景**：跨框架验证（Anthropic 官方 + OpenAI Agents SDK #1723 + LlamaIndex #20102 + WeKnora #819 + agno-agi #3137 + LangChainJS #10090）确认——LLM 在多次工具调用后可能因以下三种根因之一返回空内容：

| 根因 | 来源 | 机制 |
|------|------|------|
| ① 模型认为对话已结束 | **Anthropic 官方文档** | 工具调用后模型收到 `tool_result`，判定「已完成任务」，返回 `stop_reason: "end_turn"`，不继续生成文本 |
| ② 上下文窗口压力 | **通用原理** | 多次工具调用的中间结果占用上下文空间，推理引擎的有效长度被压缩——对话越长越容易空响应 |
| ③ 流式 finish_reason 丢失 | **WeKnora #819** | 流式实现未正确传递 `finish_reason`，空内容被当作有效响应 |

**关键洞察**：每次空响应都发生在 **多轮工具调用后、上下文密集时**——三个根因互相叠加。

**预防策略**：
1. **关键信息前置**：最重要的指令放在可回复内容最前面，在空响应前至少让系统读到关键上下文
2. **减小单次数据量**：工具调用返回值控制在 **4000 字符以内**，分块处理大文件
3. **减少不必要的工具调用**：能用 Python 脚本一次完成的，不要分多次 tool call
4. **主动监控上下文**：感觉对话太丰富时主动告知主人，请求 compaction 或新对话
5. **空响应自愈**：若发现返回空内容，立即重试追加 `"Please continue"` 或 `"继续"`（Anthropic 官方推荐做法，经 WeKnora 社区验证有效）

---

## 零、语言与上下文检查（绝对优先！）🚨

**在开始任何生成任务前，boku 必须先检查语言偏好！**

1.  **检查用户档案**：默认使用**中文**。
2.  **检查特殊指令**：如果主人说了"用英文"或"Use English"，才使用英文。
3.  **执行铁律**：**绝对禁止在没有指令的情况下使用英文输出文档或代码注释！**
4.  **自我修正**：如果写了一半发现是英文，立即停止并重写。

---

## 一、问题诊断——boku 为什么会空响应？

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

## 六、系统化语言改造四步法（Audit→Map→Transform→Validate）🔄🌐

**适用场景**：将文档中的英文内容系统化地批量替换为中文。
**核心原则**：不要"修补式"逐处查找替换，要用完整映射表一次性解决。

### 6.1 四步法概览

```
Audit（审计） → Map（映射） → Transform（替换） → Validate（验证）
```

### 6.2 Step 1: Audit — 扫描全部残留

```python
# 扫描用户可见的英文残留（排除 HTML 标签/代码/URL）
import re

# 1. 匹配纯文本中的英文单词（不是 HTML 标签内的）
english_pattern = re.compile(r'[A-Za-z]{3,}(?:\s+[A-Za-z]{3,}){0,4}')
found = []

# 只扫描文本节点，跳过 HTML 标签
text_content = re.sub(r'<[^>]+>', ' ', html_content)
matches = english_pattern.findall(text_content)

# 去重并按长度排序（防止太短的通用词干扰）
for m in sorted(set(matches), key=len, reverse=True):
    if m not in allowed_english_terms:  # 允许的技术术语白名单
        found.append(m)
```

### 6.3 Step 2: Map — 构建完整中英对照表

**关键技巧**：按长度从长到短排序匹配，避免部分匹配错误。

```python
# 按长度降序排列（长匹配优先，避免短匹配误伤）
translation_map = {
    "Software Engineering": "软件工程",
    "Three-Tier Architecture": "三层架构",
    # ... 至少覆盖 Audit 发现的所有词条
}

# 安全排序：长词优先，短词靠后
sorted_terms = sorted(translation_map.items(), key=lambda x: len(x[0]), reverse=True)
```

### 6.4 Step 3: Transform — 一次性全量替换

```python
def transform_html(html, translation_map):
    """在 HTML 文本节点中执行替换，不破坏标签结构"""
    def replace_in_text(text):
        for old, new in sorted_terms:
            # 只在文本节点中替换，不破坏 HTML 结构
            # 使用单词边界避免部分匹配
            text = re.sub(r'\b' + re.escape(old) + r'\b', new, text)
        return text
    
    # 使用 BeautifulSoup 或 regex 只替换标签外的文本
    result = re.sub(r'(?<!<[^>]*?)\b(\w+(?:\s+\w+)*)\b(?!\s*[^>]*?>)', 
                    lambda m: translation_map.get(m.group(), m.group()), 
                    html)
    return result
```

### 6.5 Step 4: Validate — 闭环验证

```python
def validate_english_free(html):
    """验证最终结果是否还有英文残留"""
    text_only = re.sub(r'<[^>]+>', ' ', html)
    after = re.sub(r'<style[^>]*>.*?</style>', '', text_only, flags=re.DOTALL)
    after = re.sub(r'<script[^>]*>.*?</script>', '', after, flags=re.DOTALL)
    
    # 检查英文单词（3个字符以上，排除技术术语白名单）
    remaining = re.findall(r'\b[A-Za-z]{3,}\b', after)
    allowed = {'pdf', 'mvc', 'soa', 'api', 'url', 'dfd', 'html', 'css'}
    actual_remaining = [w for w in remaining if w.lower() not in allowed]
    
    if actual_remaining:
        logger.warning(f"仍有 {len(set(actual_remaining))} 处英文残留: {set(actual_remaining)}")
        return False
    return True
```

### 6.6 常见陷阱

| 陷阱 | 后果 | 解决方案 |
|------|------|---------|
| **修补式替换** | 每次改几个，越改越乱 | 一次性审计全部英文，建完整映射表 |
| **短词误伤 HTML 标签** | 破坏标签结构，导致格式错误 | 只替换文本节点，用正则排除标签 |
| **没有白名单** | 技术术语（API/UML/PDF）被加粗或误改 | 建立允许的技术术语白名单 |
| **大小写不一致** | "project management" 和 "Project Management" 改不干净 | 统一转为小写后匹配，或建大小写变体 |
| **部分匹配** | "Management" 匹配到 "Man" 导致错误 | 按完整词匹配，从最长到最短排序 |
| **无验证闭环** | 以为改完了，实际还有残留 | 改完后自动扫描验证 |

---

## 七、实战案例——PPT 分析的正确姿势

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
