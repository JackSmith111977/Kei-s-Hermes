# Research Workflow: 源头信息获取完整流程

> 参考 Research Agent 模式（Bounded Pipeline），在 Hermes 环境中落地为可执行流程。

## 五阶段研究流程

```
Phase 1: 问题定义 → Phase 2: 源头发现 → Phase 3: 源头获取 → Phase 4: 深度挖掘 → Phase 5: 整理输出
```

### Phase 1: 问题定义
- 明确研究目标（一句话）
- 拆分子问题（复杂主题）
- 确定信息源头类型（参照源头信息获取框架）

### Phase 2: 源头发现
1. `web_search` 初步探索（3-5 个关键词，多角度）
2. 从搜索结果中提取高质量 URL
3. 直接定位原始来源（官方文档 > GitHub > 权威网站）
4. **去重**：URL 归一化，去除重复

### Phase 3: 源头获取
根据源头类型选择工具链（参照工具组合矩阵）：
- 静态 → web_extract
- 动态 → browser_navigate + browser_console
- 反爬 → CDP Proxy
- API → browser_console 捕获

### Phase 4: 深度挖掘
- 对关键来源深入：滚动、点击展开、JS 提取
- 结构化数据提取：`browser_console("JSON.stringify(...)")`
- 交叉验证：≥2 独立来源佐证
- 截图验证：`browser_vision` 或 CDP `/screenshot`

### Phase 5: 整理输出
- 去重、清洗冗余内容
- 结构化笔记（含 provenance：来源 URL + 获取方式）
- 标记质量等级
- 归档到 site-patterns/（如有新站点经验）

## 搜索策略模式

### 1. Iterative Deepening（迭代深入）
先广度搜索获取概览 → 发现关键子主题 → 深入搜索子主题 → 循环直到掌握

### 2. Multi-Source Triangulation（多源三角验证）
同一信息从 3 种不同类型来源验证：官方文档 + 权威教程 + 社区实践

### 3. Temporal Filtering（时效过滤）
技术类知识 >6 个月标记为「可能过时」，需确认最新版本

### 4. Adversarial Verification（对抗验证）
形成初步结论后，主动搜索反方证据："为什么 X 可能不对？"

### 5. Cross-Source Contrast（跨源对比）
同一主题从 学术(arXiv) / 实践(Blog) / 开源(GitHub) 三个角度搜集，对比分析

## 质量评估

| 等级 | 标准 | 行动 |
|:----:|------|------|
| ✅ 高质量 | ≥3 独立来源，含官方源，信息一致 | 直接使用 |
| ⚠️ 需验证 | 1-2 来源，或来源权威性不足 | 标记待验证，后续补充 |
| ❌ 不可用 | 仅 1 来源 / 信息矛盾 / 严重过时 | 重新搜索 |
