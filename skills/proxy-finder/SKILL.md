---
name: proxy-finder
description: 免费代理机场搜集与节点测试技能。搜索可用机场订阅源、下载订阅、测试节点连通性、 筛选可用节点并写入 mihomo 配置。当用户需要找免费节点、测试代理...
version: 2.0.0
triggers:
- proxy finder
- proxy-finder
author: 小喵
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- patch
- mcp_tavily_tavily_search
- mcp_tavily_tavily_extract
metadata:
  hermes:
    tags:
    - proxy
    - v2ray
    - clash
    - network
    - automation
    - scraping
    category: devops
    skill_type: data-analysis
    design_pattern: pipeline
---
# proxy-finder · 机场搜集与节点测试

## 技能概述

搜集免费代理机场订阅源，测试节点连通性，筛选可用节点并生成 mihomo 配置。

**核心工作流（5 阶段 Pipeline）：**

```
Phase 1: 搜集订阅源 → Phase 2: 下载订阅 → Phase 3: 测试节点 → Phase 4: 筛选排序 → Phase 5: 写入配置
```

## Phase 1: 搜集订阅源

### 1.1 已知订阅源

参见 `references/subscription-sources.md`，包含已验证的 Clash/V2Ray 订阅链接。

### 1.2 搜索新源

使用 Tavily 搜索发现新的免费机场：

```bash
# 搜索关键词模板
"free clash subscription links {year} github"
"免费机场订阅 clash v2ray {year} 每日更新"
"free v2ray proxy nodes {year} daily update"
```

### 1.3 GitHub Topics 发现

搜索 GitHub Topics 获取最新仓库：
- `https://github.com/topics/freeproxy`
- `https://github.com/topics/v2ray-config`


> 🔍 **## Phase 2** moved to [references/detailed.md](references/detailed.md)
