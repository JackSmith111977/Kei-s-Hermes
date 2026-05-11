# web-access Skill — skill-creator 参考索引

> 指向 doc-design 中的完整 skill-creator 参考文档

## 快速参考

完整 skill-creator 参考文档见：
`~/.hermes/skills/doc-design/references/skill-creator-reference.md`

## 本 Skill 使用的设计模式

| 模式 | 应用场景 | 文件 |
|------|---------|------|
| Tool Wrapper | 简单搜索/抓取 | 按需加载 Tavily/curl 文档 |
| Generator | 重复性抓取 | `references/site-patterns/{domain}.md` |
| Reviewer | 验证抓取质量 | 评估体系（十二、评估体系） |
| Inversion | 探索性抓取 | 先调研再执行 |
| Pipeline | 复杂多步骤抓取 | Stage 1-7 流程 |

## 本 Skill 的 Pipeline 阶段

```
Stage 1: 前置检查（check-deps）
Stage 2: 环境启动（Chrome + Proxy）
Stage 3: 导航目标（new/navigate）
Stage 4: 内容提取（eval/截图）
Stage 5: 数据清洗（格式化/去重）
Stage 6: 验证交付（完整性检查）
Stage 7: 清理收尾（close tabs）
```
