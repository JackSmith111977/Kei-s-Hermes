---
name: problem-solving-sherlock
description: 通用问题解决的 meta-skill——不限于代码调试，而是面对任何卡住的情况时的系统化突破方法。基于 systematic-debugging 但扩...
version: 1.0.0
triggers:
- 卡住了
- 怎么办
- 行不通
- 不好用
- 没办法了
- 不知道怎么做
- 试试别的方法
- 哪里出问题了
- 遇到困难
- 想不通
allowed-tools:
- terminal
- read_file
- write_file
- search_files
- session_search
- mcp_tavily_tavily_search
- mcp_tavily_tavily_extract
metadata:
  hermes:
    tags:
    - problem-solving
    - troubleshooting
    - research
    - methodology
    - debugging
    category: dogfood
    skill_type: research
    design_pattern: pipeline
---
# 夏洛克的解决方案 🔍

> "当你排除了所有不可能的情况，剩下的，不管多么难以置信，都必定是真相。" —— 夏洛克·福尔摩斯

## 核心哲学

**问题解决不是知识，是方法。** 遇到任何卡住的情况时，按此流程突破：

---

## 阶段 0：冷静！不要慌 ⏸️

卡住时的第一反应：

```python
# ❌ 不要做的事
"再试一次"    # 同样的方法不会得到不同的结果
"随便改改"    # 猜测性修复浪费时间
"跳过吧"      # 问题不会自己消失

# ✅ 做的事
"让我理解为什么卡住了"
```

**行动：** 先花 10 秒回答：**我在哪？我想要什么？卡在哪里了？**

---

## 阶段 1：定义问题 🎯

**没有清晰的问题描述，就不可能有解决方案。**

### 问题格式化模板
```
[症状] 发生了什么？
[预期] 应该发生什么？
[差异] 两者之间差了哪一步？
[环境] 什么上下文？（文件/工具/平台/数据）
```

### 示例
```
[症状] patch 工具替换大块代码后文件被污染
[预期] 文件应该只有指定内容被替换
[差异] patch 吞掉了相邻的变量定义
[环境] 50 行代码替换，old_string 30 个字符
```

### 问题分级

| 级别 | 特征 | 处理方式 |
|:---|:---|:---|
| **S 级** | 系统挂了、数据丢了 | 立即止损，再找根因 |
| **A 级** | 功能不可用、流程中断 | 找替代方案继续 |
| **B 级** | 方案不够好、效率低 | 优化但不阻塞 |
| **C 级** | 代码风格、小 bug | 标记后有空再改 |

---


> 🔍 **## 阶段 2** moved to [references/detailed.md](references/detailed.md)
> 
> 诊断类型速查：A=工具不可靠 | B=搜不到 | C=不确定 | D=没思路 | E=反复失败 | **F=文档-代码落差** | **G=自评自判陷阱**
