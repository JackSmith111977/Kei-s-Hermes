# 知识新鲜度四维度评分框架（2026）

> **来源**：Wrodium/AgentForge/Atlan/Tianpan 四源综合（2026年5月）
> **用途**：补充夜间自习引擎 v3.0 的新鲜度评分矩阵，引入多维评估

## 核心概念

标准 RAG 评测指标（Faithfulness/Context Recall/Answer Relevance）不含时间维度。一个系统可以在所有这些指标上达到 95%+，但返回数小时前已过时的信息。新鲜度失效是**静默**的。

## 四维度模型

| 维度 | 衡量什么 | 关键洞察 | 改进方式 |
|:-----|:---------|:---------|:---------|
| **Content Age** | 文档上次人类验证/更新时间 | 阈值必须按文档类型设定（非统一） | 添加 `last_verified_at` 字段 |
| **Embedding Lag** | 文档更新到重索引延迟 | 最易改善；流式CDC可降至<10秒 | 哈希变更检测替代全量重建 |
| **Stale Retrieval Rate** | 实际查询返回过期文档的比例 | 最运营重要；需要记录 `embedding_timestamp` | 每次检索时对比时间戳 |
| **Coverage Drift** | 全部语料中过期的比例 | 前置指标；低检索率可能掩盖沉默腐败 | 日/时扫描整体语料 |

## 复合评分阈值

| 复合分数 | 状态 | 操作 |
|:-------:|:----:|:----|
| ≥ 85% | ✅ 健康 | 常规维护 |
| 70–84% | ⚠️ 告警 | 通知知识管理团队，标记待刷新 |
| < 70% | 🛑 降级 | 应用层警告用户信息可能过时 |

## 元数据栈

每个概念/文档应包含：

| 字段 | 必选？ | 含义 |
|:-----|:------:|:-----|
| `published_at` | ✅ | 发布时间 |
| `last_verified_at` | ✅ **最关键** | 最后验证时间（≠更新时间） |
| `owner` | ✅ | 负责人 |
| `source_system` | ✅ | 来源系统 |
| `doc_state` | ✅ | 状态：draft/active/archived/superseded |
| `supersedes` | 推荐 | 被取代的旧版本ID |
| `expires_at` | 推荐 | 自动过期时间 |

## 新鲜度 SLA 分级示例

| 内容类型 | 刷新周期 | 警告阈值 | 排除阈值 |
|:---------|:--------:|:--------:|:--------:|
| 定价/合规 | 6小时 | 24小时 | 48小时 |
| 内部 SOP | 每日 | 7天 | 14天 |
| 供应商文档 | 每周 | 30天 | 60天 |
| 参考材料 | 30天 | 90天 | 180天 |
| 背景/历史 | 90天 | 180天 | 365天 |

## 实施路线图（5阶段）

1. **添加元数据** — 每个概念添加 `owner` + `last_verified_at`
2. **三类源+年龄阈值** — hot/warm/cold 三条通道
3. **降级过时内容** — 归档/草稿/被取代内容降级排名
4. **阻塞高风险操作** — 高风险操作前检查证据新鲜度
5. **运营仪表板** — 添加新鲜度指标到 ops dashboard

## 应用到 Hermes night-study-engine

当前 freshness_score 计算公式：
```
freshness_score = (
    recency_weight * min(1, days_since_update / 30) +
    stability_weight * (1 - version_change_frequency) +
    activity_weight * session_count_30d / expected_sessions +
    relevance_weight * user_query_frequency / total_queries
)
```

建议扩展为包含 staleness_window 维度的复合评分：
```
freshness_score = (
    content_age_score * w1 +
    embedding_lag_score * w2 +
    stale_retrieval_rate_score * w3 +
    coverage_drift_score * w4 +
    recency_score * w5 +
    activity_score * w6
)
```

其中 content_age_score = `min(1, days_since_last_verified / staleness_threshold)`
