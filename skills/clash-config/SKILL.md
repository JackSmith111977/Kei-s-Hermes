---
name: clash-config
description: 'Clash / mihomo 代理工具配置管理技能。涵盖配置格式、代理协议、代理组、路由规则、

  DNS 设置、TUN 模式、代理提供者等完整配置参考。...'
version: 2.1.0
triggers:
- clash config
- clash-config
- 代理环境变量
- 应用走不了代理
- Network is unreachable
- proxy env
author: 小喵
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- patch
metadata:
  hermes:
    tags:
    - proxy
    - clash
    - mihomo
    - network
    - config
    - vpn
    category: devops
    skill_type: library-reference
    design_pattern: tool-wrapper
    related_skills:
    - web-access
    - browser-automation
depends_on: []

---
# Clash / mihomo 配置管理 Skill

## 触发条件（When to Use）

**使用此 skill 当：**
- 用户需要编写或修改 Clash / mihomo 配置文件
- 用户询问代理协议配置（SS/VMess/VLESS/Trojan/Hysteria2 等）
- 用户需要配置代理组、路由规则、DNS
- 用户需要生成配置模板
- 用户询问 Clash 和 mihomo 的差异
- 用户需要配置 proxy-providers 或 rule-providers
- **browser/CDP 工具遇到网络问题（无法访问外网）**
- **curl/web_search 测试代理失败**

**不使用此 skill 当：**
- 只需要启动/停止 mihomo 服务 → 直接用 terminal
- 只需要测试代理连通性 → 直接用 curl 通过代理测试
- 需要搜索机场/订阅源 → 使用代理机场搜集 skill

**相关 Skill 联动**：
- `web-access`：联网操作统一入口（会自动检查代理状态）
- `browser-automation`：浏览器自动化（依赖代理访问外网）

**📎 参考文件**：
- `references/proxy-env-setup.md` — **代理环境变量三层配置法**：当应用走不了代理时的排查和解决方案（Python httpx/requests、Hermes vision 工具等）
- `references/proxy-lifecycle.md` — **代理生命周期管理**：mihomo 完整启停监控流程（start→verify→stop→restart），含 Hermes terminal(background=true) 适配

---

## 一、工具选择决策树

```
Clash/mihomo 配置任务
├─ 需要生成配置模板？ → 读取 templates/standard-config.yaml
├─ 需要查询配置字段？ → 读取 references/config-reference.md
├─ 需要验证配置文件？ → mihomo -t -f config.yaml
├─ 需要启动服务？ → terminal (mihomo -f config.yaml)
└─ 需要对比 Clash vs mihomo？ → 读取 references/config-reference.md §十
```

---

## 二、环境信息

| 项目 | 值 |
|------|-----|
| mihomo 路径 | `/usr/local/bin/mihomo` |
| 配置目录 | `~/.config/mihomo/` |
| 配置文件 | `~/.config/mihomo/config.yaml` |
| 缓存文件 | `~/.config/mihomo/cache.db` |
| GEO 数据 | `~/.config/mihomo/Country.mmdb` |
| GEO 元数据 | `~/.config/mihomo/geoip.metadb` |
| 代理端口 | 7890 (HTTP+SOCKS5) |
| API 端口 | 9090 |
| Skill 目录 | `~/.hermes/skills/clash-config` |

---

## 三、配置文件结构速查

配置文件为 YAML 格式，主要部分：

```
config.yaml
├── mixed-port / port / socks-port    # 代理端口
├── allow-lan                         # 允许局域网
├── mode                              # rule / global / direct
├── log-level                         # 日志级别
├── external-controller               # API 地址
├── secret                            # API 密钥
├── dns                               # DNS 配置
├── dns.enhanced-mode                 # fake-ip / redir-host
├── tun                               # TUN 模式 (可选)
├── listeners                         # 多入口 (可选)
├── proxies                           # 代理节点列表
├── proxy-providers                   # 代理提供者 (订阅)
├── proxy-groups                      # 代理组
├── rules                             # 路由规则
├── rule-providers                    # 规则提供者
├── profile                           # 缓存设置
├── geodata-mode                      # GEO 数据格式
├── geox-url                          # GEO 下载地址
└── tls                               # HTTPS API 证书
```

---

## 四、常用操作

### 4.1 验证配置文件

```bash
mihomo -t -f ~/.config/mihomo/config.yaml
```

### 4.2 启动 mihomo

> **⚠️ 坑**：Hermes 环境下，terminal 工具会拦截 nohup/disown/setsid 等 shell 后台包装。请使用 `terminal(background=true)` 代替。

```python
# ✅ Hermes agent 中启动（推荐）
terminal(command="mihomo -f ~/.config/mihomo/config.yaml",
         background=True,
         watch_patterns=["Start initial configuration", "HTTP proxy started", "proxy listening"])
```

```bash
# 传统终端（人肉操作）
nohup mihomo -f ~/.config/mihomo/config.yaml > /tmp/mihomo.log 2>&1 &

# 前台启动（调试）
mihomo -f ~/.config/mihomo/config.yaml

# 指定工作目录
mihomo -d ~/.config/mihomo -f config.yaml
```

### 4.3 停止 mihomo

```bash
# 通过 API 停止
curl -X PUT http://127.0.0.1:9090/stop

# 或直接 kill
pkill mihomo
```

### 4.4 通过代理测试连通性

```bash
# HTTP 代理测试
curl -x http://127.0.0.1:7890 https://www.google.com -I -s -o /dev/null -w "%{http_code}"

# SOCKS5 代理测试
curl -x socks5://127.0.0.1:7890 https://www.google.com -I -s -o /dev/null -w "%{http_code}"

# 查看出口 IP
curl -x http://127.0.0.1:7890 https://api.ipify.org
```

### 4.5 更新 GEO 数据

```bash
# 手动下载 GEO 数据
cd ~/.config/mihomo
wget -O Country.mmdb "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.mmdb"
wget -O geoip.dat "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat"
```

### 4.6 通过 API 切换代理

```bash
# 获取所有代理组
curl -s http://127.0.0.1:9090/proxies | python3 -m json.tool

# 切换代理
curl -X PUT "http://127.0.0.1:9090/proxies/🚀%20Proxy" -d '{"name":"⚡ Auto"}'

# 延迟测试
curl -X GET "http://127.0.0.1:9090/proxies/⚡%20Auto/delay?url=https://www.gstatic.com/generate_204&timeout=5000"
```

---


> 🔍 **## 五、配置生成指南** moved to [references/detailed.md](references/detailed.md)
