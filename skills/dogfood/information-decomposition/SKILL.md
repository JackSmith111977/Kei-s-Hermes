---
name: information-decomposition
description: 信息分解与上下文管理指南。教 boku 如何用高级搜索策略（Boolean/Operators）和多级摘要策略（Chunking/Summarizat...
version: 1.0.0
triggers:
- 信息量太大
- 搜索结果太多
- 读不完
- 上下文不够用
  - dogfood
  - 高级搜索
  - 分治法
  - 大文件处理
related_skills:
- analysis-workflow
allowed-tools:
- mcp_tavily_tavily_search
- mcp_tavily_tavily_extract
- mcp_tavily_tavily_crawl
metadata:
  hermes:
    tags:
    - search-strategies
    - context-management
    - chunking
    - summarization
    - boolean
    category: dogfood
    skill_type: library-reference
    design_pattern: tool-wrapper
---
# 信息分解与高级搜索策略 🧩🔍

> **核心原则**：不要试图一口吞下大象。把大问题切碎，把大信息提炼。

## 一、阶段 1：源头控制——高级搜索策略 (Search Strategies)

**不要搜完了才发现信息量太大，要在搜索时就过滤掉 90% 的垃圾！**

### 1. Boolean 逻辑组合
*   **AND**：`python AND flask`（必须同时包含）
*   **OR**：`python OR django`（包含任意一个即可，用于同义词扩展）
*   **NOT / -**：`jaguar speed -car`（排除干扰项）

### 2. 高级操作符 (Operators)
*   **`site:`**：限定权威来源。
    *   例：`machine learning site:arxiv.org`（只看论文）
    *   例：`python tutorial site:github.com`（只看代码库）
*   **`filetype:`**：只搜文件。
    *   例：`annual report 2025 filetype:pdf`
*   **`intitle:` / `allintitle:`**：限定标题必须包含。
    *   例：`intitle:"guide to"`（找教程专用）
*   **`""` (精确匹配)**：
    *   例：`"error code 500"`（必须完全一致，不要拆开）

### 3. Tavily 工具的妙用
*   **Search (广度)**：用于探索方向，获取摘要。设置 `max_results=5` 即可，不要贪多。
*   **Extract (深度)**：看到好的 URL，再单独用 `tavily_extract` 读取全文。不要一次性 search 几十个结果然后全部读。
*   **Crawl (系统)**：针对特定官网进行爬取。

---

## 二、阶段 2：数据切分——多级分块 (Chunking)

当信息量确实很大（如长篇文档、多页搜索结果）时，**绝对不要一次性丢给 LLM**，也不要傻傻地按字符数硬切。

### 1. 结构化切分 (Structural Chunking)
*   **按标题切分**：如果文档有 H1/H2/H3，按章节切分。这保持了语义完整性。
*   **按功能切分**：代码按函数切分，数据按表头切分。

### 2. 递归摘要 (Recursive Summarization / Map-Reduce)
这是处理超大上下文的核心算法：
1.  **Map (分治)**：把长文档切成 N 个 Chunk（例如每 2000 字一块）。
2.  **Process (摘要)**：对每个 Chunk 单独提取要点。
3.  **Reduce (汇总)**：把所有 Chunk 的要点合并，再进行一次最终摘要。

> **boku 的执行策略**：
> 如果我要读 10 篇长文章：
> 1. 先读所有文章的**标题 + 摘要 + 前 200 字**。
> 2. 筛选出最相关的 2-3 篇。
> 3. 对这 2-3 篇进行**深入提取 (Extract)**。
> *绝对不要一次性把 10 篇全文都读进来！*

---

## 三、阶段 3：克服位置偏差 (Positional Bias)

LLM 通常对输入的**开头**和**结尾**印象最深，中间的内容容易被忽略（Lost in the Middle 现象）。

### 应对技巧
1.  **关键信息前置**：把最重要的问题或指令放在 Prompt 的最前面。
2.  **多次询问**：如果信息很长，分批次问，比如 "基于第一部分..." "基于第二部分..."。
3.  **打乱顺序 (Shuffling)**：在比较多个同类信息时，可以打乱顺序再处理，防止模型偷懒。

---

## 四、实战演练：面对 100 页的调研报告怎么办？

**❌ 错误做法 (Old boku)**：
1. 搜索 "Report 2025"。
2. 得到 10 个链接。
3. 试图用 Extract 一次性读所有链接的全文。
4. Token 爆炸，或者读得太慢，最后放弃。

**✅ 正确做法 (New boku)**：
1. **搜索 (Search)**：使用 `site:` 或 `filetype:` 限制范围，只要最权威的 3-5 个来源。
2. **侦察 (Recon)**：只读这 3-5 个来源的摘要。
3. **选择 (Select)**：发现其中 1 个最相关。
4. **深入 (Deep Dive)**：只 Extract 那 1 个来源的全文。
5. **合成 (Synthesize)**：如果内容还是太长，按章节分段读取，每读完一段总结一次要点，最后合并。

---

## 五、常用搜索模板 (Copy-Paste)

| 场景 | 搜索词模板 |
| :--- | :--- |
| **找官方文档** | `[keyword] site:docs.[company].com` |
| **找学术论文** | `[keyword] filetype:pdf site:arxiv.org` |
| **找具体报错解法** | `"[exact error message]"` |
| **找最佳实践** | `[keyword] best practices -site:pinterest.com` |
| **排除干扰词** | `[keyword] -tutorial -course` (不想看教程，想看干货) |
