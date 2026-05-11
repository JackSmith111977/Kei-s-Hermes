# Brave Search MCP 配置指南

## 概述

Brave Search MCP 是 Tavily 的推荐替代方案：
- **免费额度**：2,000 次搜索/月
- **独立索引**：不依赖 Google/Bing
- **技术搜索质量**：优于 Tavily
- **MCP 支持**：有官方 MCP Server

---

## 配置步骤

### 1. 获取 Brave Search API Key

1. 访问 https://brave.com/search/api/
2. 点击 "Get Started" 注册账号
3. 在 Dashboard 创建 API Key
4. 复制 API Key（格式：`BSA...`）

### 2. 添加到 Hermes config.yaml

在 `~/.hermes/config.yaml` 的 `mcp_servers` 部分添加：

```yaml
mcp_servers:
  # 已有的 Tavily MCP（保留作为备用）
  tavily:
    command: npx
    args:
    - -y
    - tavily-mcp
    env:
      TAVILY_API_KEY: tvly-dev-xxx  # 你的 Tavily Key
    timeout: 60
    connect_timeout: 30
  
  # 新增 Brave Search MCP
  brave:
    command: npx
    args:
    - -y
    - "@brave/search-mcp-server"  # Brave Search MCP Server
    env:
      BRAVE_API_KEY: BSAxxx  # 你的 Brave Search API Key
    timeout: 60
    connect_timeout: 30
```

### 3. 重启 Hermes Agent

```bash
# 如果 Hermes Agent 正在运行
pkill -f run_agent

# 或重启 gateway
systemctl restart hermes-gateway  # 如果用 systemd
```

### 4. 验证 Brave Search MCP 工具

重启后，检查是否出现以下工具：
- `mcp_brave_web_search`
- `mcp_brave_suggest`  # 搜索建议

---

## 使用方式

Brave Search MCP 工具命名规则：`mcp_brave_{tool_name}`

示例：
```
mcp_brave_web_search(query="Python 3.13 新特性", count=5)
```

---

## 在 web-access Skill 中的位置

Brave Search MCP 是搜索决策树中的第二步：

```
需要联网搜索？
├─ Tavily 还有额度？
│  ├─ 是 → 用 Tavily MCP
│  └─ 否 ↓
├─ Brave Search API 已配置？
│  ├─ 是 → 用 Brave Search MCP  ← 这里！
│  └─ 否 ↓
├─ SearXNG 已部署？
│  ├─ 是 → 用 SearXNG REST API
│  └─ 否 ↓
├─ curl 直接搜索特定网站？
│  ├─ 能 → 用 Wikipedia/GitHub API
│  └─ 不能 → 报错
```

---

## 常见问题

### Q: Brave Search 对中文搜索质量如何？
A: 不如百度/搜狗，但对英文技术搜索足够。如果主要搜索英文内容，Brave Search 足够好用。

### Q: 2,000 次/月够用吗？
A: ≈ 每天 66 次，对个人使用足够。如果不够，可以付费升级（$5/月 = 5,000 次）。

### Q: MCP Server 名称是什么？
A: 官方 MCP Server 包名：`@brave/search-mcp-server`

### Q: 为什么保留 Tavily MCP？
A: Tavily 额度刷新后（每月 1 日）可能恢复可用，保留作为备用。

---

## 相关链接

- Brave Search API: https://brave.com/search/api/
- Brave Search MCP Server: https://github.com/brave/search-mcp-server
- MCP Protocol: https://modelcontextprotocol.io/