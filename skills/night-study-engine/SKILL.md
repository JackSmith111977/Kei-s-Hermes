---
name: night-study-engine
description: "Hermes 夜间自习引擎 v2.0 — 自驱动学习系统。涵盖动态领域引擎、学习质量门禁、知识追踪、间隔复习、结构化日志、晨间汇报增强、Artifact 产出门禁。v2.0 核心升级：从简单批处理升级为完整学习系统。"
version: 2.0.0
triggers:
  - 夜间学习
  - night study
  - 夜间自习
  - 自主学习
  - 自动学习
  - 知识更新
  - skill 维护
  - 学习系统
  - 间隔复习
  - 知识追踪
  - 知识门禁
  - 学习质量
  - 自习改造
  - self-driven learning
  - autonomous study
  - knowledge update
author: 小喵 (Emma)
license: MIT
allowed-tools:
  - terminal
  - read_file
  - write_file
  - patch
  - cronjob
  - web_search
  - web_extract
  - mcp_tavily_tavily_search
  - mcp_tavily_tavily_extract
  - mcp_tavily_tavily_crawl
  - delegate_task
depends_on:
  - learning-workflow
  - learning-review-cycle
  - web-access
  - skill-creator
metadata:
  hermes:
    tags:
      - autonomous-learning
      - knowledge-tracking
      - spaced-repetition
      - quality-gate
    category: meta
    skill_type: pipeline
    design_pattern: pipeline
---

# 🌙 夜间自习引擎 v2.0 — 自驱动学习系统

> **核心理念**：夜间学习室不应只是"定时搜索→写入"的简单批处理，而是具备**知识追踪、质量门禁、间隔复习、失败恢复**的完整自驱动学习系统。
> **v2.0 升级**：从静态 4 领域 + 简易日志 → 动态领域引擎 + 结构化日志 + 知识追踪 + 质量门禁

---

## 一、系统架构概览

```
夜间自习引擎 v2.0
├── 🔧 调度层（Cron + 自适应调度）
│   ├── 夜间自习轮次 (0/2/4/6/8 点)
│   └── 间隔复习 cron (1天/7天/30天)
├── 🔍 学习层（按领域并行学习）
│   ├── 领域发现引擎（自动发现新领域）
│   ├── 学习质量门禁（评分 < 60 拦截）
│   └── Artifact 产出门禁（每次必须产出）
├── 📚 知识层（持久化追踪）
│   ├── Knowledge Base（概念→状态→复习日期）
│   └── 间隔复习协议（1天→3天→7天→30天）
├── 📝 日志层（结构化记录）
│   ├── JSONL 会话日志
│   └── 汇总文本日志（向后兼容）
└── 📊 汇报层（晨间报告）
    ├── 学习趋势分析
    ├── 技能新鲜度报告
    └── 今日学习建议
```

---

## 二、领域配置（Dynamic Domain Engine）

### 配置文件：`~/.hermes/config/night_study_config_v2.json`

```json
{
  "version": "2.0",
  "domains": [
    {
      "id": "ai_tech",
      "name": "AI与前沿技术",
      "keywords": "AI agents, LLM new models, ML papers, ICLR/NeurIPS breakthroughs",
      "target_skill": "ai-trends",
      "priority": 0.9,
      "schedule_interval_hours": 2,
      "last_updated": "2026-05-05T00:02:00",
      "freshness_score": 0.7
    },
    {
      "id": "dev_tools",
      "name": "开发工具与语言",
      "keywords": "Python new libraries, frontend frameworks, DevOps tools, Rust/Go updates",
      "target_skill": "dev-tools-guide",
      "priority": 0.7,
      "schedule_interval_hours": 4,
      "freshness_score": 0.5
    },
    {
      "id": "anime_acg",
      "name": "二次元与文娱",
      "keywords": "2026 new anime, manga releases, game industry news, ACG culture",
      "target_skill": "bangumi-recommender",
      "priority": 0.5,
      "schedule_interval_hours": 8,
      "freshness_score": 0.3
    },
    {
      "id": "productivity",
      "name": "效率与工作方法论",
      "keywords": "productivity apps, knowledge management, remote work, AI tools",
      "target_skill": "productivity-guide",
      "priority": 0.6,
      "schedule_interval_hours": 6,
      "freshness_score": 0.4
    }
  ],
  "discovery_rules": [
    "skill 超过 30 天未更新 → 自动加入学习队列",
    "用户频繁查询某主题 → 自动创建领域",
    "gap_queue 中 ≥ 3 个相关缺口 → 自动创建领域"
  ],
  "quality_threshold": {
    "min_score": 60,
    "artifact_required": true,
    "max_loops": 3
  }
}
```

---

## 三、学习流程（每个领域的标准流程）

### 步骤 1：获取任务（从配置读取当前领域）
```bash
python3 -c "
import json
with open('$HOME/.hermes/config/night_study_config_v2.json') as f:
    config = json.load(f)
# 按优先级和新鲜度排序，选最需要的领域
domains = sorted(config['domains'], key=lambda d: d['priority'] * (1 - d['freshness_score']), reverse=True)
print(json.dumps(domains[0]))
"
```

### 步骤 2：联网搜索（web-access 路由）
- 使用领域关键词搜索 3-5 个高质量来源
- 记录搜索元数据（URL、时间戳、来源类型）

### 步骤 3：深度阅读（extract/crawl）
- 提取核心内容
- 标记权威来源（官方文档 > 社区 > 博客）
- 检查时效性（超过 12 个月标记为可能过时）

### 步骤 4：知识提炼
- 从阅读笔记中提取可复用的模式
- 交叉验证核心结论（≥2 个独立来源）

### 步骤 5：质量评分
```
质量分 = 信息覆盖度(30) + 交叉验证(25) + 可操作性(25) + 结构完整度(20)
```

| 评分 | 行为 |
|------|------|
| < 60 | 🛑 拦截！进入 Loop N+1 重新学习 |
| 60-79 | ⚠️ 警告，标记"待改进" |
| ≥ 80 | ✅ 通过，产出 Artifact |

### 步骤 6：产出 Artifact（必须至少一项）
- ✅ 更新或创建 Skill（通过 skill-creator）
- ✅ 沉淀 Memory（通过 memory tool）
- ✅ 输出实战指南到 `~/.hermes/docs/learning-logs/`

### 步骤 7：更新 Knowledge Base
```json
{
  "domain": "ai_tech",
  "concepts": {
    "qwen3.6": {
      "status": "mastered",
      "date_introduced": "2026-05-05",
      "last_reviewed": "2026-05-05",
      "next_review": "2026-05-06",
      "review_interval": 1
    }
  }
}
```

### 步骤 8：写入结构化日志
```jsonl
{"timestamp": "2026-05-05T00:02:00+08:00", "domain": "ai_tech", "session_id": "ns_20260505_00", "quality_score": 0.85, "artifact_produced": true}
```

---

## 四、间隔复习机制

### 复习节奏
| 复习级别 | 间隔 | 检查内容 |
|----------|------|----------|
| Level 1 | 1 天后 | Skill 是否可执行？是否有明显错误？ |
| Level 2 | 7 天后 | 是否有新知识出现？是否需要更新？ |
| Level 3 | 30 天后 | 对比最新版本本文档，检查 API 变更 |

### 实现方式
- 学习完成时自动注册 3 个复习 cron 任务
- 复习到期时自动加载对应 Skill，检查新鲜度
- 如果发现问题 → 自动加入 gap_queue

---

### 失败恢复机制

| 异常类型 | 恢复策略 |
|----------|----------|
| 搜索无结果 | 更换关键词，最多重试 3 次 |
| Tavily API 限流 (rate limit) | 立即降级到 `web_search`/`web_extract`（无需重试 Tavily，因为限流通常是分钟级的），记录降级原因到日志中 |
| Tavily API 配额耗尽 (quota exhaustion) | ⚠️ 比 rate limit 更严重——配额要到下个月才会重置！立即永久降级到 `web_search`/`web_extract` 并在日志中标记 `quota_exhausted`，后续所有轮次直接跳过 Tavily。错误特征：`This request exceeds your plan's set usage limit` |
| Tavily Extract 失败 | 尝试用 `web_extract`（通用提取工具）替代，或直接从搜索结果摘要中提取关键信息 |

### 主动配额管理（v2.1 新增）

> 内置策略与详细实测数据参见 `references/cron-tavily-quota-strategy.md`

当多个 Cron 轮次在一天内连续消耗 Tavily 配额时，月配额（1,000 credits）可能在 15 日后或 06:00+ 轮次时耗尽。推荐主动策略：

| 策略 | 描述 |
|------|------|
| **时段感知** | 06:00+ 轮次直接使用 `web_search` 原生（跳过 Tavily，避免 MCP 级联锁定 ~58s） |
| **配额预判** | 每月 10 日后（或首次 Tavily 失败后）默认降级至 `web_search`。实测：5月8日月配额已耗尽，15日阈值过于乐观。当 `month_day >= 10` 或检测到 `quota_exhausted` 错误时，直接跳过 Tavily。 |
| **失败计数** | 同一会话中 Tavily 连续失败 ≥2 次 → 切换到 `web_search` |

**实测验证**: 06:00 轮次纯 `web_search` 获得 8 个高质量官方源（Rust Blog、Next.js Blog、releases.rs），质量评分 95——比 Tavily 搜索效果更好、更快、无级联锁定风险。

### 失败恢复（续）

| 异常类型 | 恢复策略 |
|----------|----------|
| 网页无法访问 | 标记"不可读"，跳过并搜索替代来源 |
| Skill 更新失败 | 写入 gap_queue，下次 Review 重试 |
| Cron 执行超时 | 标记"未完成"，下次轮次继续 |

---

## 六、晨间汇报模板

```markdown
# 🌅 夜间自习晨间报告 - {日期}

## 📈 学习概览
- 完成领域：{N}/{M}
- 平均质量分：{score}
- 新增知识点：{count}
- 更新 Skill：{count}

## 🔥 技能新鲜度
| Skill | 最后更新 | 新鲜度 | 状态 |
|-------|----------|--------|------|
| ai-trends | 2026-05-05 | 🟢 新鲜 | 已更新 |
| dev-tools | 2026-05-03 | 🟡 待更新 | 已超 2 天 |

## ⚠️ 知识缺口
- {N} 个高优先级缺口：...
- {N} 个中优先级缺口：...

## 📋 今日建议
1. 优先更新 {skill_name}（已超 7 天未更新）
2. 复习 {domain} 领域的间隔复习到期概念
3. 关注 {topic} 的最新动态
```

---

## 七、文件结构

```
~/.hermes/
├── config/
│   └── night_study_config_v2.json          # 领域配置 v2.0
├── night_study/
│   └── knowledge_base/
│       ├── ai_tech.json                     # AI 领域知识库
│       ├── dev_tools.json                   # 开发工具知识库
│       ├── anime_acg.json                   # 二次元知识库
│       └── productivity.json                # 效率方法论知识库
├── logs/
│   ├── night_study.log                      # 汇总日志（向后兼容）
│   └── night_study_sessions/
│       └── 2026-05-05.jsonl                 # 结构化会话日志
└── skills/
    └── night-study-engine/                  # 本 skill
        ├── SKILL.md
        ├── references/
        │   ├── quality-scoring-guide.md     # 质量评分细则
        │   └── cron-tavily-quota-strategy.md # Tavily 配额管理与 Cron 时段降级策略（v2.1）
        ├── scripts/
        │   ├── select_domain.py             # 领域选择脚本
        │   └── update_knowledge_base.py     # 知识库更新脚本
        └── checklists/
            └── pre-study-check.md           # 学习前检查清单
```

---

## 八、Cron 任务配置

### 现有任务（保留）
| 任务 | 调度 | 状态 |
|------|------|------|
| 夜间自习轮次 | 0 0,2,4,6,8 * * * | ✅ 保留 |
| 夜间自习晨报 | 30 9 * * * | ✅ 保留 |

### 新增任务（按需）
| 任务 | 调度 | 说明 |
|------|------|------|
| 间隔复习 L1 | 每日 8:00 | 检查 1 天后到期的概念 |
| 间隔复习 L2 | 每周一 8:00 | 检查 7 天后到期的概念 |
| 间隔复习 L3 | 每月 1 日 8:00 | 检查 30 天后到期的概念 |

---

## 九、🚩 Red Flags（常见错误）

1. **❌ 只搜索不沉淀** — 学习必须产出 Artifact（Skill/Memory/Guide）
2. **❌ 质量门禁跳过** — 评分 < 60 必须进入 Loop N+1，不可跳过
3. **❌ 日志格式不统一** — 必须写入 JSONL 结构化日志
4. **❌ Knowledge Base 不更新** — 每次学习后必须更新概念状态
5. **❌ 间隔复习未注册** — 学习完成后必须注册复习 cron
6. **❌ 领域固定不变** — 应该动态发现和添加新领域
7. **❌ 失败不恢复** — 遇到异常必须重试或降级，不可静默跳过
8. **❌ Tavily API 失败不降级** — Tavily 是付费 API，容易遇到 rate limit。必须准备 `web_search`/`web_extract` 作为降级方案，不要因为 Tavily 失败就放弃学习轮次
9. **❌ 仅依赖一种搜索工具** — 同一来源多个并行调用容易触发限流。建议交替使用 Tavily 和 web_search，或在 Tavily 限流时立即切换到 web_search
- **❌ Tavily 限流后忽略 MCP 服务器状态级联** — 当 Tavily API 返回 rate limit 错误后，MCP 服务器可能将 Tavily 标记为"unreachable after 7 consecutive failures"并锁定 ~58 秒。此时不要重试 Tavily MCP 工具，而是**立即切换到备用的 web_search/web_extract 工具**。Tavily 限流→MCP 服务器级联锁定的行为容易让后续轮次误判"Tavily 挂了"，需要在日志中记录降级原因以便区分

---

## 十、评估用例

### Eval-001：标准学习流程
- **输入**：夜间自习轮次触发 ai_tech 领域
- **预期**：搜索 → 阅读 → 提炼 → 质量评分 ≥ 60 → 更新 ai-trends skill → 写入结构化日志

### Eval-002：质量门禁拦截
- **输入**：搜索结果为空或质量极低
- **预期**：质量评分 < 60 → 进入 Loop N+1 → 重新搜索

### Eval-003：知识追踪更新
- **输入**：学习新概念 "qwen3.6"
- **预期**：Knowledge Base 中新增概念，状态=developing，next_review=1天后

### Eval-004：结构化日志写入
- **输入**：完成一次学习会话
- **预期**：JSONL 日志新增一行，包含 timestamp/domain/quality_score/artifact_produced
