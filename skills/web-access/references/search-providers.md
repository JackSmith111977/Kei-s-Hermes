# Agent 搜索 Provider 方案对比与配置指南

> 本文档记录 Tavily 额度用完后 AGent 联网搜索的替代方案
> 创建日期：2026-05-05

## 一、为什么需要这个参考

Tavily 是当前 Hermes 唯一的搜索 MCP Provider，但它：
- 免费额度仅 1,000 credits/月
- 被 Nebius 收购后发展方向偏企业
- 大规模使用时价格较高（100K 请求约 $800）

需要一个多 Provider fallback 体系。

## 二、所有可用方案概览

### 第三方 API（最快部署）

| 方案 | 免费额度 | 付费价格 | 100K 费用 | MCP | 特点 |
|------|---------|---------|-----------|-----|------|
| **Brave Search** | 2,000 次/月 | $3/1K 查询 | ~$300 | ✅ 官方 | 独立索引，技术搜索好 |
| **Perplexity Sonar** | 无免费 | $1/1K 请求 | ~$100 | ❌ 需适配 | 直接返回 AI 答案 |
| **Firecrawl** | 500 credits | $16/月 (3K) | ~$333 | 开源可自托管 | 搜索+抓取一体化 |
| **Valyu DeepSearch** | 免费试用 | 按量 | - | ❌ | 36+ 专业数据源 |
| **Mojeek** | 有免费层 | 按量 | - | ❌ | 独立索引 |
| **Exa** | 1,000 credits | 按量 | - | ❌ | 语义搜索 |

### 自托管方案（零 API 费用，有服务器成本）

| 方案 | 部署难度 | 资源需求 | 搜索质量 | 服务器月费 |
|------|---------|---------|---------|-----------|
| **SearXNG** | 中（Docker 一键） | 1GB RAM, 1vCPU | ✅ 高（聚合多引擎） | ~$5 |
| **Whoogle** | 极低（Docker 一键） | 256MB RAM | ✅ 高（Google 结果） | ~$3 |
| **YaCy** | 中 | 2GB RAM | 🟡 中（取决于节点） | ~$10 |
| **Crawl4AI** | 中 | 4GB RAM | ✅ 高 | ~$10-20 |
| **全自建管线** | 高 | 2GB RAM | 取决于爬取范围 | ~$10-20 |

## 三、TinyFish Search API 配置（推荐首选 ✅ 已配置）

> **TinyFish Search 和 Fetch API 完全免费**，不限次数（仅限速）。
> 比 Brave Search 更好：无月配额限制，搜索+抓取都免费。
> **当前状态：✅ 已配置（API Key 已写入 ~/.hermes/.env）**

### Search API 详情

| 项目 | 内容 |
|:---|---:|
| **端点** | `GET https://api.search.tinyfish.ai?query=xxx` |
| **费用** | **完全免费** 🆓（0 credits/请求） |
| **速率限制** | 免费 5次/分钟，Starter 20次/分钟 |
| **延迟** | p50 < **0.5秒** |
| **返回格式** | JSON：`title`, `snippet`, `url`, `position`, `site_name` |

### Fetch API 详情

| 项目 | 内容 |
|:---|---:|
| **端点** | `POST https://api.fetch.tinyfish.ai` |
| **费用** | **完全免费** 🆓 |
| **速率限制** | 免费 25次/分钟 |
| **并行** | 最多 10 URLs/请求 |
| **返回** | Clean Markdown（去广告/导航），延迟 ~35ms |

### 调用方式

**方式 A：通过 boku 的封装脚本（推荐）**
```bash
# 搜索
python3 ~/.hermes/scripts/tinyfish_search.py search "关键词" --location US --language en

# 抓取网页内容
python3 ~/.hermes/scripts/tinyfish_search.py fetch https://example.com --format markdown
```

**方式 B：直接 curl**
```bash
# 搜索
curl "https://api.search.tinyfish.ai?query=关键词&location=US&language=en" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# 抓取
curl -X POST "https://api.fetch.tinyfish.ai" \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com"],"format":"markdown"}'
```

### MCP 集成（备选，需 OAuth）

```yaml
mcp_servers:
  tinyfish:
    url: "https://agent.tinyfish.ai/mcp"
    auth: oauth  # OAuth 2.1，首次需浏览器验证
```

> ⚠️ MCP 模式下搜索消耗 credits（1 credit = 2次搜索），且需 OAuth。
> **推荐直接用 REST API（免费 + 无需 OAuth）。**

---

## 四、Brave Search MCP 配置（备选）

这是最快、最可靠的替代方案。

### 步骤 1：注册 Brave Search API
1. 访问 https://brave.com/search/api/
2. 注册免费账号
3. 获取 API Key（免费额度 2,000 次/月）

### 步骤 2：在 config.yaml 添加 MCP Server

```yaml
mcp_servers:
  brave-search:
    command: npx
    args:
      - -y
      - '@modelcontextprotocol/server-brave-search'
    env:
      BRAVE_API_KEY: "${BRAVE_API_KEY}"  # 引用环境变量，不要明文写
    timeout: 60
    connect_timeout: 30
```

### 步骤 3：在 .env 中添加 API Key
```bash
echo 'BRAVE_API_KEY="你的API密钥"' >> ~/.hermes/.env
```

### 步骤 4：restart Hermes
```bash
# 重启 Hermes gateway 或 CLI 重新加载配置
hermes restart  # 或直接开启新会话
```

## 四、SearXNG 自托管配置

### Docker 部署
```bash
docker run -d --name searxng \
  -p 8080:8080 \
  -e SEARXNG_BASE_URL=http://localhost:8080/ \
  -e SEARXNG_SECRET_KEY=$(openssl rand -hex 32) \
  searxng/searxng
```

### REST API 调用
```bash
# 搜索
curl "http://localhost:8080/search?q=hello+world&format=json"
```

### Hermes 集成
SearXNG 提供 REST API，boku 可以通过 terminal 调用：
```bash
curl -s "http://localhost:8080/search?q=搜索关键词&format=json&language=zh-CN&categories=general"
```

返回 JSON 格式，包含 title、url、content 等字段。

## 六、搜索 Provider 选择决策树

```
需要联网搜索？
├─ 首选：TinyFish REST API（免费 ✅ 已配置）
│  ├─ 搜索 → python3 ~/.hermes/scripts/tinyfish_search.py search "关键词"
│  ├─ 抓取 → python3 ~/.hermes/scripts/tinyfish_search.py fetch <url>
│  └─ ⚠️ 如果 429（限速）→ 等 12s 重试
├─ Tavily 还有额度？
│  ├─ 是 → 用 Tavily（当前 MCP）
│  └─ 否 ↓
├─ Brave Search API 已配置？
│  ├─ 是 → 用 Brave Search MCP
│  └─ 否 ↓
├─ SearXNG 已部署？
│  ├─ 是 → 用 SearXNG REST API
│  └─ 否 ↓
├─ 可以用 curl 直接搜索？
│  ├─ 能 → 用 curl 查特定网站（如 Wikipedia API、GitHub API）
│  └─ 不能 → 告诉用户"搜索功能暂不可用，请配置 Brave Search 或部署 SearXNG"
```

## 七、注意事项

1. **中文搜索质量**：Brave Search 对中文搜索质量不如中文引擎（百度），但如果英文为主则足够
2. **API Key 安全**：Tavily API Key 当前明文在 config.yaml 中，应改为 `${TAVILY_API_KEY}` 环境变量引用
3. **搜索频率限制**：Brave 免费 2,000 次/月 ≈ 每天 66 次，对个人使用足够
4. **MCP Server 数量**：Hermes 支持多个 MCP Server 共存，不会冲突
5. **SearXNG 需要外网**：虽然自托管，但 SearXNG 需要连接各搜索引擎的 API，不是完全离线的
