# 免费搜索类 MCP Server 清单

> 最后更新：2026-05-05
> 用途：当 Tavily 额度用完时，作为备选方案
> 数据来源：PulseMCP、GitHub MCP Servers、行业基准测试

---

## 🥇 强烈推荐（有官方 MCP Server + 免费额度）

### 🏆 TinyFish Search MCP — 新首选（搜索+Fetch 完全免费）

| 项目 | 说明 |
|------|------|
| **MCP 端点** | `https://agent.tinyfish.ai/mcp`（HTTP，需 OAuth） |
| **REST API（推荐）** | `GET https://api.search.tinyfish.ai`（API Key，免 OAuth） |
| **费用** | **搜索和 Fetch 完全免费** 🆓（不限次数，仅限速） |
| **限速** | 免费 5次/分钟，Starter 20次/分钟 |
| **延迟** | **<0.5s**（搜索），**~35ms**（Fetch） |
| **API 注册** | https://agent.tinyfish.ai/api-keys |
| **当前状态** | **✅ 已配置**（API Key 在 ~/.hermes/.env） |
| **封装脚本** | `python3 ~/.hermes/scripts/tinyfish_search.py` |

**特点**：
- 搜索和网页抓取都免费，同类方案中唯一
- Fetch 返回 Clean Markdown（去广告/导航），比原生 web_extract 更干净
- 支持 `site:` 过滤、Geo-targeting、分页
- 同一 API Key 可升级到付费计划（Agent/Browser API）

**配置方法**（search-providers.md 有完整文档）

### 1. Brave Search MCP — 最佳直接替代

| 项目 | 说明 |
|------|------|
| **MCP 包名** | `@modelcontextprotocol/server-brave-search` |
| **安装方式** | `npx -y @modelcontextprotocol/server-brave-search` |
| **免费额度** | **2,000 查询/月**（注册即得 $5 credits） |
| **后续价格** | $5/1K 查询 |
| **API 注册** | https://brave.com/search/api/ |
| **搜索质量** | ⭐⭐⭐⭐⭐ 2026年Agent Score排名第1（14.89/20） |
| **隐私** | 独立索引，不追踪用户 |
| **支持类型** | 网页搜索、新闻搜索、图片搜索、本地搜索 |

**配置方法**（在 config.yaml 的 mcp_servers 中添加）：
```yaml
brave-search:
  command: npx
  args:
    - -y
    - '@modelcontextprotocol/server-brave-search'
  env:
    BRAVE_API_KEY: "你的API密钥"
  timeout: 60
  connect_timeout: 30
```

### 2. Firecrawl MCP — 搜索+抓取一体化

| 项目 | 说明 |
|------|------|
| **MCP 包名** | `@modelcontextprotocol/server-firecrawl` 或 `firecrawl-mcp` |
| **免费额度** | **500 credits**（一次性，注册即送） |
| **后续价格** | $16/月 (3K credits) → $333/月 (500K credits) |
| **API 注册** | https://www.firecrawl.dev/ |
| **搜索质量** | ⭐⭐⭐⭐⭐ Agent Score 14.58（排名第2） |
| **特色** | 不仅能搜索，还能抓取完整页面内容、结构化提取、支持 JS 渲染 |
| **开源** | ✅ AGPL 协议，可自托管 |

### 3. Perplexity Sonar MCP — LLM 合成答案

| 项目 | 说明 |
|------|------|
| **MCP 包名** | `@anthropic-ai/mcp-server-perplexity` |
| **免费额度** | 有限免费（$5 试用额度） |
| **后续价格** | **$1/1K 请求**（最便宜之一） |
| **API 注册** | https://docs.perplexity.ai/ |
| **特色** | 返回 LLM 合成答案（含引用），节省下游推理成本 |
| **搜索质量** | ⭐⭐⭐⭐ 但延迟较高（~11秒） |

### 4. Exa MCP — 语义搜索

| 项目 | 说明 |
|------|------|
| **MCP 包名** | `exa-mcp-server` |
| **免费额度** | **1,000 credits** |
| **后续价格** | $10-20/月（按量） |
| **API 注册** | https://exa.ai/ |
| **搜索质量** | ⭐⭐⭐⭐⭐ Agent Score 14.39（排名第3） |
| **特色** | 嵌入向量驱动的语义搜索（"找类似文章"） |

---

## 🥈 可用备选（有 MCP 但需适配）

### 5. Parallel Search MCP

| 项目 | 说明 |
|------|------|
| **MCP** | 官方提供 |
| **免费额度** | 有限免费 |
| **后续价格** | $10-50/月 |
| **特色** | 47% HLE 准确率（最高），带出处和证据 |
| **搜索质量** | Agent Score 14.21（排名第4） |

### 6. Valyu DeepSearch API

| 项目 | 说明 |
|------|------|
| **MCP** | 不直接提供，但可通过自己的 MCP Client 调用 |
| **免费额度** | 免费试用（无需信用卡） |
| **特色** | 支持 36+ 专业数据源（SEC、PubMed、临床试验等） |
| **FreshQA 准确率** | 79%（排名第1） |

---

## 🥉 自托管方案（零 API 费用）

### 7. SearXNG（元搜索引擎）

| 项目 | 说明 |
|------|------|
| **部署** | `docker run -d -p 8080:8080 searxng/searxng` |
| **服务器费** | $3-10/月 |
| **API** | ✅ 原生 REST API |
| **搜索质量** | ⭐⭐⭐⭐⭐ 聚合 Google/Bing/DuckDuckGo/Wikipedia 等 |
| **需要** | 一台 VPS（1GB RAM 足够） |

### 8. Whoogle（Google 代理）

| 项目 | 说明 |
|------|------|
| **部署** | `docker run -d -p 5000:5000 benbusby/whoogle-search` |
| **服务器费** | $3-5/月（甚至可跑在 Raspberry Pi） |
| **搜索质量** | ⭐⭐⭐⭐⭐ Google 原生质量，无追踪 |
| **特点** | 极轻量 |

---

## 📊 搜索质量排名（2026年基准测试）

| 排名 | Provider | Agent Score | 相关结果数 | 质量分 | 延迟 |
|------|----------|------------|-----------|--------|------|
| 1 | **Brave Search** | **14.89** | 4.26/5 | 3.49/5 | **669ms** |
| 2 | Firecrawl | 14.58 | 4.30/5 | 3.39/5 | 1335ms |
| 3 | Exa | 14.39 | 4.32/5 | 3.33/5 | ~1200ms |
| 4 | Parallel Search | 14.21 | 4.32/5 | 3.29/5 | 待测 |
| 5 | Tavily | 13.67 | 4.18/5 | 3.27/5 | 998ms |
| 6 | Perplexity | 12.96 | 4.00/5 | 3.24/5 | ~11000ms |
| 7 | SerpAPI | 12.28 | 3.58/5 | 3.43/5 | 2400ms |

> 来源：AIMultiple (Feb 2026)，8 个 API，每查询 5 个结果

---

## 💡 建议策略

### 阶段 1：快速配置（今天）
1. ~~Tavily（当前在用）~~
2. **注册 Brave Search API** → 配置 MCP → 给 Tavily 当 fallback

### 阶段 2：增加搜索多样性（本周）
3. 注册 Perplexity Sonar（$1/1K 很便宜）
4. 注册 Firecrawl（免费 500 credits）

### 阶段 3：自托管（本月）
5. Docker 部署 SearXNG
6. 编写 SearXNG→MCP 适配器

### 阶段 4：长期保障（需投入）
7. 搭建 Meilisearch 本地索引
8. 定期爬取维护
