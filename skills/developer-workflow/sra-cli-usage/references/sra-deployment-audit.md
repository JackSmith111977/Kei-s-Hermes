# SRA 部署审计报告 (2026-05-14)

> **核心发现**: SRA 运行 11 小时 total_requests=0。集成层从未真正部署。

---

## 诊断过程

### 1. 健康检查

```json
{
  "status": "running",
  "version": "2.0.3",
  "uptime_seconds": 40449,
  "skills_count": 202,
  "total_requests": 0,
  "total_recommendations": 0,
  "errors": 0,
  "force_level": {
    "level": "omni",
    "active_points": ["on_user_message", "periodic", "post_tool_call", "pre_tool_call"],
    "periodic_interval": 3
  }
}
```

### 2. 索引确认

202 个 skill 已索引，覆盖率 87.1%。sdd-workflow 包含正确的延续 triggers（`继续` `phase` `下一阶段` `continue` 等），SQS=80.8 (modifier 1.0)。

### 3. 集成层确认

```bash
# Hermes 核心 — 无 _query_sra_context()
grep -rn "_query_sra_context" ~/.hermes/hermes-agent/*.py  # → 空

# config.yaml — 无 SRA 配置
grep -rn "sra\|8536\|recommend" ~/.hermes/config.yaml  # → 空
```

## 根因：三层断裂

| 层 | 文档声称 | 代码现实 |
|:---|:---------|:---------|
| Hermes 核心 | `_query_sra_context()` 内置在 run_conversation() | ❌ 不存在 |
| config.yaml | SRA Proxy URL 配置 | ❌ 无引用 |
| SOUL.md | 「每次消息先调 SRA Proxy」 | ⚠️ 拉模式，不执行 |

## 阈值问题

即使手动调 SRA，单字延续关键词（如「继续」「phase」）也无法达到 THRESHOLD_WEAK=40。

```
trigger 匹配 +25 → ×0.4 词法权重 = 10 → ×1.6 短查询 boost = 16 → 16 < 40
```

## 解决方案方向

1. 在 pre_flight.py 中添加 SRA 查询调用
2. 调整 THRESHOLD_WEAK 或添加延续关键词专用 boost
3. 确认 SOUL.md 的 SRA 调用铁律可执行
