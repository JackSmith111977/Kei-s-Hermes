# 信息过滤标准

> 本文件记录 learning skill 积累的信息过滤经验和质量标准，每次学习后更新。

## 信息源权威性分级

| 等级 | 类型 | 权重 | 示例 |
|------|------|------|------|
| S 级 | 官方文档/官网 | 40% | docs.python.org, github.com/owner/repo |
| A 级 | 权威教程/技术博客 | 25% | Real Python, Mozilla MDN, 官方教程 |
| B 级 | 社区讨论/Stack Overflow | 15% | Stack Overflow 高票回答, Reddit r/programming |
| C 级 | 个人博客/视频 | 10% | Medium, YouTube 教程, 个人技术博客 |
| D 级 | 营销内容/AI 生成 | 0% | SEO 文章, AI 生成的教程, 广告内容 |

## 时效性评估标准

| 时间范围 | 权重 | 处理方式 |
|----------|------|----------|
| 近 6 个月 | 30% | 直接使用，标注日期 |
| 6 个月 -1 年 | 20% | 使用，标注日期，检查 API 是否变更 |
| 1-2 年 | 10% | 谨慎使用，必须交叉验证 |
| 2-3 年 | 5% | 仅参考概念，具体实现必须找新的 |
| 3 年以上 | 0% | 废弃，除非是经典理论 |

## 信息质量检查清单

- [ ] 信息来源是否明确？
- [ ] 作者是否有相关资质/经验？
- [ ] 是否有代码示例/实操内容？
- [ ] 是否有用户反馈/评论验证？
- [ ] 是否与官方文档一致？
- [ ] 是否包含明确的版本信息？

## 已验证的高质量信息源

<!-- 每次学习后添加 -->

| 学域类型 | 来源 | 验证日期 | 备注 |
|------|------|----------|----------|
| WeasyPrint | doc.courtbouillon.org/weasyprint/ | 2026-05-03 | 官方文档，完整准确 |
| WeasyPrint | github.com/Kozea/WeasyPrint | 2026-05-03 | 源码 + 6407 commits |
| Mermaid | mermaid.js.org/syntax/ | 2026-05-03 | 官方语法参考 |
| 飞书 API | open.feishu.cn/document/ | 2026-05-03 | 官方 API 文档 |
| Python | docs.python.org/3/howto/logging.html | 2026-05-03 | 官方 logging 教程 |
| Python | typing.python.org | 2026-05-03 | 官方类型注解最佳实践 |
| Git | git-scm.com/docs | 2026-05-03 | Git 官方文档 |
| Agent/LLM Research | arxiv.org (cs.AI, cs.LG) | 2026-05-04 | 学术研究首选，但需搭配实践验证 |
| Agent 实践 | huggingface.co/blog, blog.ml.cmu.edu | 2026-05-04 | 工业界最佳实践，时效性强 |
| 开源 Agent 项目 | github.com (topics: ai-agents, llm-agent) | 2026-05-04 | Stars+活跃度作为过滤器 |
