---
name: web-access
description: '所有联网操作的统一入口。搜索、网页抓取、浏览器自动化、Tavily MCP
  等都必须先经过此 skill，由它根据任务类型决策最优工具。'
version: "7.0.0-hermes"
triggers:
- 联网
- 搜索
- 查资料
- web search
- crawl
- 爬取
- 抓取
- 提取
- 浏览器
author: 一泽Eze (adapted & upgraded by 小喵)
license: MIT
github: https://github.com/eze-is/web-access
allowed-tools:
- terminal
- read_file
- write_file
- patch
- web_search
- web_extract
- web_crawl
- browser_navigate
- browser_snapshot
- browser_click
- browser_type
- browser_scroll
- browser_back
- browser_press
- browser_get_images
- browser_vision
- browser_console
- mcp_tavily_tavily_search
- mcp_tavily_tavily_extract
- mcp_tavily_tavily_crawl
- mcp_tavily_tavily_map
metadata:
  hermes:
    tags:
    - web
    - browser
    - scraping
    - search
    - automation
    - tavily
    related_skills:
    - clash-config
    - doc-design
    - skill-creator
    category: web-access
    related_skills: ["clash-config", "doc-design", "skill-creator", "web-ui-ux-design"]
    skill_type: product-verification
    design_pattern: pipeline
---
# web-access Skill (Hermes 统一版 v6)

## ⚠️ 铁律：所有联网任务必须经过此 skill

> **任何需要联网的操作（搜索、抓取、提取、浏览）都必须先加载此 skill**，
> 由它根据任务类型决策最合适的工具。
> **禁止跳过此 skill 直接调用联网工具。**

---

## 一、工具选择决策树（统一版）

### 第一优先级：Hermes 原生工具（零成本、直接可用）

```
需要联网操作？
├─ 搜索信息（无特定 URL）？
│   └─ web_search（原生）→ 返回 JSON(title, url, description)
│      后端：config.yaml → web.backend（Firecrawl/Tavily/Exa/Parallel 四选一）
│      配置检查：EXA_API_KEY / TAVILY_API_KEY / FIRECRAWL_API_KEY / PARALLEL_API_KEY
│
├─ 已知 URL，提取内容？
│   └─ web_extract（原生）→ 返回 Markdown 内容
│      特性：LLM 自动摘要(>5000chars)、并行处理 5 个 URL、SSRF 保护、URL 密钥检测
│      超时：60s/URL
│
├─ 爬取整个网站？
│   └─ web_crawl（原生）→ 返回多页 Markdown 内容
│      后端：Firecrawl/Tavily
│      特性：限 20 页、LLM 处理、website_policy 检查
│
├─ 需要交互操作（点击/填表/登录）？
│   └─ browser_navigate → browser_type → browser_click → browser_press
│      特性：navigate 已返回 snapshot，无需额外调用 browser_snapshot
│
├─ 需要视觉理解（CAPTCHA/布局验证）？
│   └─ browser_vision → 截图 + Vision AI 分析
│
└─ 需要 JS 执行/DOM 检查？
    └─ browser_console(expression="...")
```

### 第二优先级：MCP Tavily 工具（原生后端未配置时的替代）

```
原生 web 工具不可用？（config.yaml 未配置 web.backend 或 API Key 缺失）
├─ 搜索 → mcp_tavily_tavily_search（1,000 credits/月）
├─ 提取 → mcp_tavily_tavily_extract
├─ 爬取 → mcp_tavily_tavily_crawl
└─ 网站映射 → mcp_tavily_tavily_map
```

### 第三优先级：高级浏览器（复杂交互、反自动化绕过）

```
原生 browser 工具不够用？（需要真实鼠标手势、文件上传、反爬绕过）
├─ 方案 A：agent-browser（已内置）
│  └─ Hermes Agent 内置 agent-browser CLI (v0.13.0)
│  └─ 支持：Browser Use / Browserbase 云服务 / 本地 Chromium
│  └─ 启动：自动检测，无需手动配置
│
└─ 方案 B：CDP Proxy（可选，高级场景）
   └─ CDP Proxy (:3456) + Chrome (:9222)
   └─ 适用于：需要 /clickAt 真实点击、/setFiles 文件上传、复杂 JS 注入
   └─ 详见 references/cdp-api.md
   
   ⚠️ 代理配置（国内服务器必需）：
   ├─ 检查代理状态：curl -x http://127.0.0.1:7890 https://www.google.com
   ├─ 代理配置 skill：clash-config（mihomo 代理管理）
   ├─ 如果代理不可用 → 先加载 clash-config skill 检查/修复代理
   └─ Chrome 需要通过代理访问外网（启动时添加 --proxy-server 参数）
```

### 第四优先级：curl（兜底方案）

```
无 API Key、无 MCP、只需要静态 HTML？
├─ curl + 代理（国内服务器必需）
│  └─ curl -x http://127.0.0.1:7890 https://example.com
│  └─ 代理配置 skill：clash-config
│
└─ curl + 文本处理（grep/awk/sed）
   └─ 适用于：简单 API 调用、静态页面、已知结构的 HTML 提取
```

**相关 Skill 引用**：
- `clash-config`：代理配置管理（mihomo 端口 7890）
- `browser-automation`：浏览器自动化详细指南

---

## 二、源头信息获取框架（v7.0 新增）

### 2.1 核心原则：Source-First

> **不是「用什么工具搜」，而是「信息源头在哪，选什么工具直达」。**

每次联网操作前先问：
1. **信息源头在哪？** — 搜索引擎索引？官方文档？动态页面？API 接口？需要登录吗？
2. **源头可直达吗？** — 有 URL 吗？需要 JS 渲染吗？有反爬保护吗？
3. **选什么工具链？** — 从下面的矩阵中选择。

### 2.2 信息源头类型与工具映射

| 源头类型 | 特征 | 推荐工具组合 | CDP 角色 |
|----------|------|-------------|---------|
| **搜索引擎索引** | Google/Bing 可搜到 | `web_search` → `web_extract` | 备选 |
| **静态文档/API** | 无动态渲染的 HTML/JSON/文本 | `web_extract` / `curl` + 代理 | 备选 |
| **SPA 动态页面** | React/Vue 渲染，需 JS 执行 | `browser_navigate` → `browser_console` / `browser_vision` | 核心 |
| **需要登录态** | Cookie/Auth Token 认证 | `browser`（复用已有 session）/ CDP Proxy | 核心 |
| **反爬保护** | Cloudflare/DataDome 拦截 | CDP Proxy + anti-detection 策略 | 核心 |
| **API 后端数据** | JSON/XHR 接口返回 | `browser_console` 捕获 Network response / curl | 辅助 |

### 2.3 CDP 优先路径（实际环境优先级）

```
源头信息获取 → 判断信息类型 →
├─ 可公开访问的静态内容 → web_extract（最快最省，零成本）
├─ 需要 JS 渲染的动态内容 → browser_navigate（Hermes 原生浏览器工具）
│   ├─ 提取文本 → browser_snapshot / browser_console("document.body.innerText")
│   ├─ 提取数据 → browser_console("JSON.stringify(data)")
│   └─ 视觉验证 → browser_vision("页面显示了什么内容？")
├─ 需要登录态/反爬绕过 → CDP Proxy (:3456)
│   ├─ /new?url= → 创建 tab
│   ├─ /eval?target= → 执行 JS (POST body)
│   ├─ /clickAt?target= → 真实鼠标点击 (POST body CSS选择器)
│   ├─ /scroll?target=&direction= → 滚动
│   ├─ /screenshot?target=&file= → 截图
│   └─ /close?target= → 关闭 tab
├─ 需要多 tab 协作 → CDP Proxy /targets 管理多个页面
└─ 兜底 → curl -x http://127.0.0.1:7890（静态内容）
```

### 2.4 工具组合矩阵

| 场景 | 工具链 | 说明 |
|------|--------|------|
| **快速调研** | `web_search` → `web_extract` × 3-5 | 简单概念查询，5 分钟内 |
| **深度调研** | `web_search` → `browser_navigate`(直入源头) → `browser_console`(JS提取) → `web_extract`(内容保存) | 复杂主题研究 |
| **源头溯源** | `web_search`(找源头 URL) → `browser_navigate`(直达原始来源) → `browser_vision`(截图验证) | 需权威源头时 |
| **数据提取** | `browser_navigate` → `browser_scroll`(触发懒加载) → `browser_console`(JSON.stringify 提取) | 结构化数据采集 |
| **反爬绕过** | CDP Proxy `/new`(创建) → `/eval`(注入反检测脚本) → `/clickAt`(真实点击) → `/screenshot`(结果截图) | 高防护站点 |
| **API 捕获** | `browser_navigate` → `browser_console`(捕获 Network response) | SPA 数据提取 |

### 2.5 反检测/反爬策略

当遇到反爬保护时的应对方案（按顺序尝试）：

1. **切换 headless 模式**：使用新 headless（`--headless=new`），相比旧模式更接近真实浏览器
2. **CDP 脚本注入**：在页面初始化前注入反检测脚本（`Page.addScriptToEvaluateOnNewDocument`）
3. **真实鼠标操作**：使用 CDP Proxy 的 `/clickAt` 而非 JS 层面 `/click`
4. **复用登录态**：连接已有 Chrome 实例，复用已登录的 Session（绕过认证检测）
5. **寻找替代源**：放弃被拦截的站点，找镜像/缓存/API 替代
6. **标记不可达**：记录到 site-patterns/，下次直接跳过

> **注意**：本环境主要用于信息获取，非高频对抗性爬虫。大多数站点用原生工具即可。

---

## 三、工具速查表

### 原生工具（Hermes 内置）

| 工具 | 用途 | 关键特性 |
|------|------|----------|
| `web_search` | 搜索引擎查询 | 支持 4 种后端，返回 JSON(title, url, description) |
| `web_extract` | 提取 URL 内容 | LLM 自动摘要、并行 5 URL、SSRF/密钥检测、60s 超时 |
| `web_crawl` | 爬取整个网站 | Firecrawl/Tavily、限 20 页、LLM 处理 |
| `browser_navigate` | 导航到 URL | 返回 snapshot + ref ID，无需额外调用 snapshot |
| `browser_snapshot` | 页面快照 | compact(默认)/full 模式，8000 chars 截断 |
| `browser_click` | 点击元素 | 通过 ref ID（如 @e5） |
| `browser_type` | 输入文本 | 通过 ref ID，自动清空再输入 |
| `browser_scroll` | 滚动页面 | up/down |
| `browser_press` | 按键 | Enter/Tab/Esc 等 |
| `browser_back` | 后退 | 浏览器历史 |
| `browser_get_images` | 获取图片 | 返回 URL + alt text |
| `browser_vision` | 视觉分析 | 截图 + Vision AI，支持 annotate 模式 |
| `browser_console` | 控制台/JS | 获取 console 输出，执行 JS 表达式 |

### MCP 工具（Tavily 服务）

| 工具 | 用途 | 额度 |
|------|------|------|
| `mcp_tavily_tavily_search` | 搜索 | 1,000 credits/月 |
| `mcp_tavily_tavily_extract` | 提取 | 同上 |
| `mcp_tavily_tavily_crawl` | 爬取 | 同上 |
| `mcp_tavily_tavily_map` | 网站映射 | 同上 |

### CDP Proxy API（Chrome :9222 → Proxy :3456）

| 端点 | 用途 |
|------|------|
| `GET /new?url=` | 创建新 tab |
| `GET /close?target=` | 关闭 tab |
| `POST /eval?target=` | 执行 JS |
| `POST /click?target=` | JS 点击 |
| `POST /clickAt?target=` | 真实鼠标点击 |
| `POST /setFiles?target=` | 文件上传 |
| `GET /scroll?target=&direction=` | 滚动 |
| `GET /screenshot?target=&file=` | 截图 |

---

## 🚨 强制搜索门禁（最高优先级，不可跳过）

> **核心规则：Agent 绝对不能跳过搜索！当一种方法失败时，必须尝试下一个可用方法，直到找到结果或确认所有方法都不可用。**

### 门禁检查脚本

**✅ 已实现**：`~/.hermes/scripts/web_search_gatekeeper.py`

```bash
# 检查门禁状态（显示可用方法）
python3 ~/.hermes/scripts/web_search_gatekeeper.py --status

# 强制 curl 保底搜索
python3 ~/.hermes/scripts/web_search_gatekeeper.py "搜索关键词" --force-curl

# JSON 输出（用于自动化）
python3 ~/.hermes/scripts/web_search_gatekeeper.py --status --json
```

### 搜索方案优先级（必须按顺序尝试）

| 优先级 | 方案 | 检查条件 | 执行方式 |
|--------|------|---------|---------|
| 0 | **TinyFish REST API** 🆓🏆 | API Key (.env) | `python3 ~/.hermes/scripts/tinyfish_search.py search "查询"` |
| 1 | Tavily MCP | API key + MCP server | `mcp_tavily_tavily_search` |
| 2 | Firecrawl | API key (.env) | `web_search` (backend=firecrawl) |
| 2 | Exa | API key (.env) | `web_search` (backend=exa) |
| 3 | curl + 代理 | 代理端口 7890 | `curl -x http://127.0.0.1:7890` |
| 4 | Chrome CDP | 端口 9222 | `browser_navigate` |

> **当前状态**：TinyFish ✅（免费无限） | Tavily ✅ | Firecrawl ✅ | Exa ✅ | curl+代理 ✅ | CDP ✅

### Agent 行为规则

**禁止行为**：
- ❌ 直接跳过搜索
- ❌ 只尝试一种方法就放弃
- ❌ 不报告失败原因

**必须行为**：
- ✅ 运行门禁检查脚本确认可用方法
- ✅ 按优先级依次尝试
- ✅ 每次失败后尝试下一个方案
- ✅ 最后报告所有失败原因

---

## ⚡ 自动 Fallback 与后端切换机制（最高优先级）

> **核心原则：当当前后端（如 Tavily）额度耗尽或报错时，boku 必须自动切换到下一个可用后端，并立即重试任务，绝不让主人手动干预！**

### 1. 错误特征识别
在调用 `web_search`, `web_extract`, `web_crawl` 等工具失败时，如果出现以下关键词，判定为 **额度耗尽** 或 **Key 失效**：
- `402`, `Payment Required`, `Usage limit exceeded`, `Monthly quota reached`
- `401 Unauthorized`, `Invalid API Key`
- `firecrawl: error`, `tavily: error` (明确指示 API 拒绝)
- `MCP server 'tavily' is unreachable after 3 consecutive failures` (连续失败)

### 2. Backend 状态检测脚本

**✅ 已实现**：`~/.hermes/scripts/web_backend_status.py`

```bash
# 检查所有 backend 状态
python3 ~/.hermes/scripts/web_backend_status.py

# 输出 JSON（用于自动化）
python3 ~/.hermes/scripts/web_backend_status.py --json

# 切换 backend（自动修改 config.yaml）
python3 ~/.hermes/scripts/web_backend_status.py --switch firecrawl
```

### 3. 自动切换决策树

```
检测到 API 错误？
├─ Step 1: 检查 TinyFish 是否可用（免费无限，无需切换）
│  └─ 是 → 直接改调 tinyfish_search.py
├─ Step 2: 运行 backend 状态检测
│  └─ python3 ~/.hermes/scripts/web_backend_status.py --json
│
├─ Step 3: 找到下一个可用 backend
│  ├─ Tavily 不可用？
│  │  ├─ TinyFish → python3 ~/.hermes/scripts/tinyfish_search.py search "..."
│  │  ├─ Firecrawl 有 API Key？ → 切换 firecrawl
│  │  ├─ Exa 有 API Key？ → 切换 exa
│  │  └─ Brave MCP 已配置？ → 用 Brave MCP
│  │
│  └─ 其他 backend 不可用？
│     └─ 同样逻辑向下查找
│
├─ Step 4: 执行切换
│  └─ python3 ~/.hermes/scripts/web_backend_status.py --switch <new_backend>
│
├─ Step 5: 通知用户
│  └─ "喵！Tavily 额度用完了，boku 切换到 TinyFish（免费）继续搜索喵！"
│
└─ Step 6: 重试任务
   └─ 使用完全相同的参数再次调用原工具
```

### 4. 执行步骤（Agent 必须遵守）

**当检测到 API 错误时**：

1. **检测 backend 状态**：运行 `python3 ~/.hermes/scripts/web_backend_status.py --json`
2. **找到可用 backend**：解析 JSON，找 `status == "available"` 的 backend
3. **切换 backend**：运行 `--switch <new_backend>`
4. **通知用户**：告诉主人切换了什么
5. **重试任务**：用相同参数再次调用

---

## 四、搜索 Provider 选择

| Provider | 推荐时机 | 免费额度 | 价格 | 接入方式 |
|----------|---------|---------|------|---------|
| 🔴 **TinyFish** 🏆 | **首选（已配置）** | 搜索 **无限免费** 🆓 | **$0** | `REST API`（curl/Python） |
| 🔵 **Tavily** | 备选 | 1,000 credits/月 | $8/1K | MCP |
| 🟢 **Brave Search** | Tavily 用完 | 2,000 查询/月 | $3/1K | MCP |
| 🟢 **Perplexity Sonar** | 需要 LLM 合成答案 | 有限免费 | $1/1K | MCP |
| 🟠 **SearXNG** | 自托管备选 | 免费（自托管） | 仅服务器费 | REST API |
| 🟠 **Firecrawl** | 搜索+抓取一体化 | 500 credits（一次性） | $16/月起 | MCP |

### 搜索 Fallback 流程

```
需要搜索？
├─ 🥇 TinyFish REST API（免费，已配置 ✅）
│  ├─ python3 ~/.hermes/scripts/tinyfish_search.py search "关键词"
│  └─ ⚠️ 限速 5次/分钟 → 超限则等 12s 重试
├─ 🥈 原生 web_search 可用？（API Key 存在）
│  └─ 是 → web_search（Hermes 内置）
├─ 🥉 Tavily MCP 可用（有额度）？
│  └─ 是 → mcp_tavily_tavily_search
├─ 4️⃣ Brave Search MCP 已配置？
│  └─ 是 → Brave Search MCP
├─ 5️⃣ SearXNG 已部署？
│  └─ 是 → curl "http://localhost:8080/search?format=json&q=..."
└─ 兜底 → 告诉用户搜索功能暂不可用

> 📖 **详细 Provider 对比和配置指南**：参见 `references/search-providers.md`

---

## 五、环境信息

| 项目 | 值 |
|------|-----|
| Chrome 路径 | `google-chrome` (已安装) |
| Remote Debugging 端口 | 9222 |
| CDP Proxy 端口 | 3456 |
| 虚拟显示 | Xvfb :99 |
| 用户数据目录 | `/tmp/chrome-debug` |
| Node.js | v22.22.2 |
| Skill 目录 | `~/.hermes/skills/web-access` |

> ⚠️ 所有脚本路径使用 `$HERMES_SKILL_DIR`（= `~/.hermes/skills/web-access`）

---

## 六、常见任务模式

### 模式 A：搜索信息
```
web_search("query") → 得到搜索结果 → web_extract(urls) → 提取内容
```

### 模式 B：提取已知 URL 内容
```
web_extract(["https://example.com"]) → Markdown 内容
```

### 模式 C：爬取整个网站
```
web_crawl("https://example.com", "Find product pages") → 多页内容
```

### 模式 D：登录态操作
```
browser_navigate("https://login.example.com")
→ browser_type("@e3", "username")
→ browser_type("@e7", "password")
→ browser_click("@e10")
→ browser_snapshot() → 验证登录成功
```

### 模式 E：CAPTCHA/视觉验证
```
browser_navigate("https://example.com")
→ browser_vision(question="What is the CAPTCHA text?")
```

### 模式 F：无限滚动页面
```
browser_navigate("https://example.com")
→ browser_scroll("down") → sleep 2s
→ browser_scroll("down") → sleep 2s
→ browser_snapshot() → 获取完整内容
```

### 模式 G：获取页面图片
```
browser_navigate("https://example.com")
→ browser_get_images() → 返回所有图片 URL + alt
```

### 模式 H：执行页面 JS
```
browser_navigate("https://example.com")
→ browser_console(expression="document.querySelectorAll('a').length")
```

---

## 七、Red Flags（常见错误与陷阱）

### ❌ 连接错误
- **CDP Proxy 连接超时** → Chrome 147 headless 需要从 `/json/version` 获取 UUID 路径，已修复
- **WebSocket 失败** → 使用 `ws` 模块而非 Node.js 22 原生 WebSocket
- **端口占用** → 检查 `lsof -i :3456` 和 `lsof -i :9222`

### ❌ 操作错误
- **选择器不匹配** → 先用 `browser_snapshot` 或 `/eval` 检查 DOM 结构
- **页面未加载完就操作** → `browser_navigate` 会自动等待，但复杂页面需额外 `sleep`
- **忘记关闭 tab** → 任务结束必须关闭，避免内存泄漏
- **重复调用 browser_snapshot** → `browser_navigate` 已经返回 snapshot，不需要额外调用

### ❌ 安全错误
- **未展示风险提示就开始操作** → 必须在操作前告知用户
- **在用户原有 tab 中操作** → 始终在 `/new` 创建的后台 tab 中操作
- **硬编码凭证** → 不要在脚本中硬编码账号密码

---

## 八、验证清单

每次联网任务完成后检查：

- [ ] 环境检查通过（原生工具或 MCP 或 CDP）
- [ ] 已向用户展示风险提示（如需浏览器操作）
- [ ] 所有 tab 已关闭（CDP 模式下确认无残留）
- [ ] 获取的内容满足用户需求
- [ ] 无敏感信息泄露

---

## 九、设计模式映射

### 模式选择决策树

```
联网任务
├─ 只需要搜索/摘要？ → Tool Wrapper 模式（web_search / Tavily Search）
├─ 有固定抓取模板？ → Generator 模式（站点模板驱动）
├─ 需要验证页面质量？ → Reviewer 模式（加载→验证→报告）
├─ 目标不明确/需要探索？ → Inversion 模式（先调研再行动）
└─ 多步骤复杂抓取？ → Pipeline 模式（强制顺序）
```

---

## 十、搜索次数节省策略（v6.2 已实现）

> **✅ 已实现**：L1 Response Cache 已完全实现并整合到 Hermes Agent 中喵！
> - 缓存模块：`tools/web_cache.py`（基于 SQLite，持久化存储）
> - 整合位置：`model_tools.py` 的 `handle_function_call()` 函数
> - 缓存命中时跳过 `registry.dispatch`，直接返回缓存结果
> - 缓存未命中时执行 API 调用后自动存储缓存
>
> **详细指南**：参见 `references/query-caching.md`

### 三级缓存架构

```
Level 1: Response Cache (精确缓存)
├─ Key: request_hash
├─ TTL: 1h (动态) / 24h (静态)
└─ 预估节省: 35-40%

Level 2: Semantic Cache (语义缓存)
├─ Key: embedding vector
├─ Threshold: 0.85 (cosine similarity)
└─ 预估节省: 61-68%

Level 3: Retrieval Cache (检索缓存)
├─ Key: query_cluster_hash
└─ 预估节省: 20-30%
```

### 缓存检查流程（Agent 必须执行）

```
联网工具调用前：
├─ Step 1: L1 Response Cache 检查
│   ├─ Hit → 直接返回缓存结果 ✅ (毫秒级)
│   └─ Miss → 继续
├─ Step 2: L2 Semantic Cache 检查（仅搜索类）
│   ├─ Hit (similarity > 0.85) → 返回相似缓存 ✅
│   └─ Miss → 执行 API 调用
└─ Step 3: API 调用完成后 → 存储到 L1 + L2 缓存
```

### 适用工具与 TTL

| 工具 | 缓存策略 | TTL | 预估命中率 |
|------|---------|-----|-----------|
| `web_search` | L1 + L2 | 24h (默认) / 1h (news) | 35-68% |
| `web_extract` | L1 | 24h | 40% |
| `web_crawl` | L1 | 3d | 50% |
| `browser_navigate` | L1 | 1h | 30% |
| `mcp_tavily_*` | L1 | 24h | 40% |

### 实现位置

**✅ 已实现**（v6.2）：

- 缓存模块：`~/.hermes/hermes-agent/tools/web_cache.py`
- 整合位置：`~/.hermes/hermes-agent/model_tools.py` 的 `handle_function_call()` 函数
- 缓存数据库：`~/.hermes/cache/web/request_cache.db`
- **监控脚本**：`~/.hermes/scripts/web_cache_monitor.py`（查看命中率、节省成本）

**监控命令**：

```bash
# 查看缓存状态
python3 ~/.hermes/scripts/web_cache_monitor.py

# 详细报告
python3 ~/.hermes/scripts/web_cache_monitor.py --report

# 清理过期缓存
python3 ~/.hermes/scripts/web_cache_monitor.py --cleanup

# JSON 格式输出（用于自动化）
python3 ~/.hermes/scripts/web_cache_monitor.py --json
```

**实际代码**（非伪代码）：

```python
# model_tools.py 中的缓存检查（已实现）
if function_name in CACHEABLE_TOOLS:
    cached_result = check_cache(function_name, function_args)
    if cached_result is not None:
        logger.info(f"💾 Cache hit for {function_name}, skipping API call")
        return cached_result  # Cache hit - skip API call
# ... 执行 API 调用 ...
if function_name in CACHEABLE_TOOLS:
    store_cache(function_name, function_args, result)  # 存储缓存
```

### 不适合缓存的场景

| 场景 | 原因 |
|------|------|
| 创意写作 | 每次请求独特 |
| 实时数据 | 秒级变化 |
| 个性化推荐 | 用户特定上下文 |
| 高安全要求 | 数据敏感性 |

---

## 十一、References 索引

| 文件/脚本 | 何时加载 |
|-----------|----------|
| `references/search-providers.md` | 搜索 Provider 选择和配置指南（含 TinyFish 配置详情） |
| `references/search-mcp-list.md` | 免费搜索 MCP 清单（TinyFish 已列为首选） |
| `references/query-caching.md` | 搜索次数节省策略、缓存实现代码 |
| `references/detailed.md` | 需要 CDP 启动流程、详细 API 参考时 |
| `references/cdp-api.md` | 需要 CDP API 详细参考、JS 提取模式、错误处理时 |
| `references/research-workflow.md` | 源头信息获取完整流程、五阶段研究流程、搜索策略模式 |
| `references/site-patterns/{domain}.md` | 确定目标网站后，读取对应站点经验 |
| `references/bilibili-subtitle-extraction.md` | B站视频字幕提取 |
| `scripts/tinyfish_search.py` | **[新增]** TinyFish 搜索/抓取封装脚本（`~/.hermes/scripts/tinyfish_search.py`） |

---

## 十二、评估体系

### 评估维度

| 维度 | 权重 | 关键检查点 |
|------|------|-----------|
| E1 内容完整性 | 30% | 目标信息全部获取、无遗漏 |
| E2 格式正确性 | 20% | 编码正确、无乱码、结构完整 |
| E3 时效性 | 20% | 内容是最新的、无过期数据 |
| E4 操作安全性 | 15% | 无账号风险、已展示提示 |
| E5 资源清理 | 15% | 所有 tab 已关闭、无残留进程 |

### Grader 等级

| 总分 | 等级 | 行动 |
|------|------|------|
| ≥ 0.90 | ✅ PASS | 直接交付 |
| 0.75-0.89 | ⚠️ WARN | 补充抓取后交付 |
| 0.60-0.74 | ❌ FAIL | 重新抓取 |
| < 0.60 | 🚨 CRITICAL | 更换策略重试 |
