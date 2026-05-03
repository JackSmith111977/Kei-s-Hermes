# Clash / mihomo 配置完整参考

> 基于 mihomo v1.19.24 官方文档 (wiki.metacubex.one)
> mihomo 是 Clash Meta 的分支，配置格式完全兼容原版 Clash

## 一、配置文件结构概览

```yaml
# 1. 基础配置 (General)
mixed-port: 7890          # 混合代理端口 (HTTP + SOCKS5)
allow-lan: true           # 允许局域网访问
mode: rule                # 运行模式: rule / global / direct
log-level: info           # 日志级别
external-controller: 127.0.0.1:9090  # 外部控制器 API

# 2. DNS 配置 (DNS)
dns:
  enable: true
  listen: 0.0.0.0:53
  enhanced-mode: fake-ip  # fake-ip / redir-host
  fake-ip-range: 198.18.0.1/16

# 3. 代理节点 (Proxies)
proxies:
  - name: "节点名称"
    type: ss/vmess/vless/trojan/hysteria2/...
    server: example.com
    port: 443
    # ... 协议特定字段

# 4. 代理提供者 (Proxy Providers)
proxy-providers:
  provider1:
    type: http
    url: "https://example.com/proxy.yaml"
    path: ./proxy_providers/provider1.yaml
    interval: 3600
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300

# 5. 代理组 (Proxy Groups)
proxy-groups:
  - name: "Proxy"
    type: select          # select / url-test / fallback / load-balance / relay
    proxies:
      - DIRECT
      - provider1

# 6. 路由规则 (Rules)
rules:
  - DOMAIN-SUFFIX,google.com,Proxy
  - GEOIP,CN,DIRECT
  - MATCH,DIRECT

# 7. 规则提供者 (Rule Providers)
rule-providers:
  reject:
    type: http
    behavior: classical
    url: "https://example.com/reject.yaml"
    path: ./rules/reject.yaml
    interval: 86400
```

## 二、General 配置字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mixed-port` | int | - | 混合代理端口 (HTTP + SOCKS5 共用) |
| `port` | int | - | HTTP 代理端口 |
| `socks-port` | int | - | SOCKS5 代理端口 |
| `redir-port` | int | - | 透明代理端口 (仅 Linux/macOS) |
| `tproxy-port` | int | - | TPROXY 透明代理端口 (仅 Linux) |
| `allow-lan` | bool | false | 允许局域网设备通过代理端口上网 |
| `bind-address` | string | * | 绑定地址，仅允许此地址访问 |
| `lan-allowed-ips` | list | 0.0.0.0/0, ::/0 | 允许连接的 IP 范围 (白名单) |
| `lan-disallowed-ips` | list | - | 禁止连接的 IP 范围 (黑名单优先) |
| `authentication` | list | - | HTTP/SOCKS 代理认证 `["user:pass"]` |
| `skip-auth-prefixes` | list | - | 跳过认证的 IP 范围 |
| `mode` | string | rule | 运行模式: `rule` / `global` / `direct` |
| `log-level` | string | info | `silent` / `error` / `warning` / `info` / `debug` |
| `ipv6` | bool | true | 是否允许内核接受 IPv6 流量 |
| `keep-alive-interval` | int | - | TCP Keep Alive 间隔(秒) |
| `keep-alive-idle` | int | - | TCP Keep Alive 最大空闲时间(秒) |
| `disable-keep-alive` | bool | false | 禁用 TCP Keep Alive |
| `find-process-mode` | string | strict | `always` / `strict` / `off` |
| `external-controller` | string | - | API 监听地址 `127.0.0.1:9090` |
| `external-controller-cors` | obj | - | API CORS 配置 |
| `external-controller-unix` | string | - | Unix socket API 路径 |
| `external-controller-pipe` | string | - | Windows Named Pipe API 路径 |
| `external-controller-tls` | string | - | HTTPS API 地址 |
| `secret` | string | - | API 访问密钥 |
| `external-ui` | string | - | 外部 UI 目录路径 |
| `external-ui-name` | string | - | 自定义 UI 名称 (子目录) |
| `external-ui-url` | string | - | 自定义 UI 下载 URL |
| `profile.store-selected` | bool | - | 保存 API 选择的状态 |
| `profile.store-fake-ip` | bool | - | 保存 fake-ip 映射表 |
| `unified-delay` | bool | - | 统一延迟测试 |
| `tcp-concurrent` | bool | - | TCP 并发连接 |
| `interface-name` | string | - | 出站网络接口 |
| `routing-mark` | int | - | 路由标记 (仅 Linux) |

### TLS 配置 (用于 HTTPS API)

```yaml
tls:
  certificate: string  # 证书 PEM 或路径
  private-key: string # 私钥 PEM 或路径
  ech-key: |-          # ECH 密钥
    -----BEGIN ECH KEYS-----
    ...
    -----END ECH KEYS-----
```

### GEO 数据配置

| 字段 | 说明 |
|------|------|
| `geodata-mode` | true=使用 dat 格式, false=使用 mmdb (默认) |
| `geodata-loader` | `standard` / `memconservative` (默认) |
| `geo-auto-update` | 是否自动更新 GEO 数据 |
| `geo-update-interval` | 更新间隔(小时) |
| `geox-url` | 自定义 GEO 下载地址 |

```yaml
geox-url:
  geoip: "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat"
  geosite: "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat"
  mmdb: "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.mmdb"
  asn: "https://github.com/xishang0128/geoip/releases/download/latest/GeoLite2-ASN.mmdb"
```

## 三、代理协议配置

### 通用字段 (所有协议)

| 字段 | 必须 | 说明 |
|------|------|------|
| `name` | ✅ | 代理名称，不可重复 |
| `type` | ✅ | 代理类型 |
| `server` | ✅ | 服务器地址 (域名/IP) |
| `port` | ✅ | 端口 |
| `ip-version` | - | `dual`/`ipv4`/`ipv6`/`ipv4-prefer`/`ipv6-prefer` |
| `udp` | - | 是否允许 UDP (默认 false) |
| `interface-name` | - | 绑定出站接口 |
| `routing-mark` | - | 路由标记 |
| `tfo` | - | TCP Fast Open |
| `mptcp` | - | TCP Multi Path |
| `dialer-proxy` | - | 通过指定代理/策略组建立连接 |
| `smux` | - | sing-mux 多路复用配置 |

### smux 多路复用

```yaml
smux:
  enabled: true
  protocol: smux      # smux / yamux / h2mux
  max-connections: 4  # 最大连接数 (与 max-streams 冲突)
  min-streams: 4      # 最小流数 (与 max-streams 冲突)
  max-streams: 0      # 最大流数 (与 max-connections/min-streams 冲突)
  statistic: false    # 是否在面板显示底层连接
  only-tcp: false     # 仅 TCP
  padding: true       # 启用填充
  brutal-opts:        # TCP Brutal 设置
    enabled: true
    up: 50            # 上传带宽 Mbps
    down: 100         # 下载带宽 Mbps
```

### Shadowsocks (ss)

```yaml
- name: "ss1"
  type: ss
  server: server
  port: 443
  cipher: aes-128-gcm
  password: "password"
  udp: true
  udp-over-tcp: false
  udp-over-tcp-version: 2
  plugin: obfs           # obfs/v2ray-plugin/gost-plugin/shadow-tls/restls/kcptun
  plugin-opts:
    mode: tls
    host: bing.com
```

**加密方法：**
- AES: `aes-128-ctr`, `aes-192-ctr`, `aes-256-ctr`, `aes-128-cfb`, `aes-192-cfb`, `aes-256-cfb`, `aes-128-gcm`, `aes-192-gcm`, `aes-256-gcm`
- CHACHA: `chacha20-ietf-poly1305`, `xchacha20-ietf-poly1305`
- 2022 Blake3: `2022-blake3-aes-128-gcm`, `2022-blake3-aes-256-gcm`, `2022-blake3-chacha20-poly1305`
- LEA: `lea-128-gcm`, `lea-256-gcm`

### VMess

```yaml
- name: "vmess"
  type: vmess
  server: server
  port: 443
  uuid: uuid
  alterId: 0
  cipher: auto           # auto/none/zero/aes-128-gcm/chacha20-poly1305
  packet-encoding: packetaddr  # packetaddr/xudp
  global-padding: false
  authenticated-length: false
  tls: true
  servername: example.com
  alpn:
    - h2
    - http/1.1
  fingerprint: xxxx
  client-fingerprint: chrome
  skip-cert-verify: true
  reality-opts:
    public-key: xxxx
    short-id: xxxx
  network: tcp           # tcp/ws/http/h2/grpc
```

### VLESS

```yaml
- name: "vless"
  type: vless
  server: server
  port: 443
  uuid: uuid
  flow: xtls-rprx-vision
  packet-encoding: xudp   # packetaddr/xudp
  encryption: ""
  tls: true
  servername: example.com
  alpn:
    - h2
    - http/1.1
  client-fingerprint: chrome
  skip-cert-verify: true
  reality-opts:
    public-key: xxxx
    short-id: xxxx
  network: tcp           # tcp/ws/http/h2/grpc/xhttp
```

### Trojan

```yaml
- name: "trojan"
  type: trojan
  server: server
  port: 443
  password: "password"
  sni: example.com
  alpn:
    - h2
    - http/1.1
  skip-cert-verify: true
  network: tcp           # tcp/ws/grpc
```

### Hysteria2

```yaml
- name: "hysteria2"
  type: hysteria2
  server: server
  port: 443
  password: "password"
  obfs: salamander      # 混淆类型
  obfs-password: "obfs_pass"
  sni: example.com
  skip-cert-verify: true
  ports: "20000-50000"  # 端口跳跃
  up: "100 Mbps"        # 上传带宽
  down: "1000 Mbps"     # 下载带宽
```

### TUIC

```yaml
- name: "tuic"
  type: tuic
  server: server
  port: 443
  uuid: uuid
  password: "password"
  congestion-controller: bbr
  udp-relay-mode: native
  sni: example.com
  skip-cert-verify: true
  alpn:
    - h3
```

### WireGuard

```yaml
- name: "wg"
  type: wireguard
  server: server
  port: 51820
  private-key: "xxxx"
  public-key: "xxxx"
  ip: 10.0.0.2
  ipv6: fd00::2
  mtu: 1400
  udp: true
  preshared-key: "xxxx"
  reserved: [1, 2, 3]
  dns:
    - 1.1.1.1
    - 8.8.8.8
```

### SSH

```yaml
- name: "ssh"
  type: ssh
  server: server
  port: 22
  user: root
  password: "password"
  private-key: /path/to/key
  host-key:
    - "ssh-rsa ..."
```

## 四、代理组 (Proxy Groups)

### 类型

| 类型 | 说明 |
|------|------|
| `select` | 手动选择 |
| `url-test` | 自动选择延迟最低的节点 |
| `fallback` | 按顺序切换可用节点 |
| `load-balance` | 负载均衡 |
| `relay` | 代理链 |

### 通用字段

| 字段 | 必须 | 说明 |
|------|------|------|
| `name` | ✅ | 代理组名称 |
| `type` | ✅ | 代理组类型 |
| `proxies` | - | 引用的代理或代理组 |
| `use` | - | 引用的代理提供者 |
| `url` | - | 健康检查地址 |
| `interval` | - | 健康检查间隔(秒) |
| `lazy` | - | 懒检查 (默认 true) |
| `timeout` | - | 健康检查超时(毫秒) |
| `max-failed-times` | - | 最大失败次数 (默认 5) |
| `disable-udp` | - | 禁用 UDP |
| `include-all` | - | 包含所有出站代理 |
| `include-all-proxies` | - | 包含所有出站代理 |
| `include-all-providers` | - | 包含所有代理提供者 |
| `filter` | - | 过滤关键词/正则 (包含) |
| `exclude-filter` | - | 排除关键词/正则 |
| `exclude-type` | - | 排除类型 (用 `\|` 分隔) |
| `expected-status` | - | 期望 HTTP 状态码 |
| `hidden` | - | API 中隐藏 |
| `icon` | - | API 中图标 |

### 示例

```yaml
proxy-groups:
  # 手动选择
  - name: "Proxy"
    type: select
    proxies:
      - Auto
      - HK
      - JP
      - DIRECT

  # 自动选择 (延迟最低)
  - name: "Auto"
    type: url-test
    use:
      - my-provider
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    lazy: true
    timeout: 5000
    filter: "(?i)港|hk|hongkong"

  # 故障转移
  - name: "Fallback"
    type: fallback
    proxies:
      - Auto
      - DIRECT
    url: "https://www.gstatic.com/generate_204"
    interval: 300

  # 负载均衡
  - name: "LB"
    type: load-balance
    proxies:
      - HK-1
      - HK-2
    url: "https://www.gstatic.com/generate_204"
    interval: 300

  # 代理链
  - name: "Relay"
    type: relay
    proxies:
      - HK
      - US
```

## 五、路由规则 (Rules)

### 规则类型

| 类型 | 格式 | 说明 |
|------|------|------|
| `DOMAIN` | `DOMAIN,google.com,Proxy` | 精确域名匹配 |
| `DOMAIN-SUFFIX` | `DOMAIN-SUFFIX,google.com,Proxy` | 域名后缀匹配 |
| `DOMAIN-KEYWORD` | `DOMAIN-KEYWORD,google,Proxy` | 域名关键词匹配 |
| `DOMAIN-REGEX` | `DOMAIN-REGEX,^google.*com,Proxy` | 正则匹配 |
| `GEOSITE` | `GEOSITE,google,Proxy` | geo 网站分类匹配 |
| `GEOIP` | `GEOIP,CN,DIRECT` | geo IP 国家匹配 |
| `IP-CIDR` | `IP-CIDR,8.8.8.0/24,Proxy` | IP 段匹配 |
| `IP-CIDR6` | `IP-CIDR6,::1/128,DIRECT` | IPv6 段匹配 |
| `SRC-IP-CIDR` | `SRC-IP-CIDR,192.168.1.100/32,DIRECT` | 源 IP 匹配 |
| `SRC-PORT` | `SRC-PORT,80,DIRECT` | 源端口匹配 |
| `DST-PORT` | `DST-PORT,443,Proxy` | 目标端口匹配 |
| `PROCESS-NAME` | `PROCESS-NAME,telegram,Proxy` | 进程名匹配 |
| `PROCESS-PATH` | `PROCESS-PATH,/usr/bin/telegram,Proxy` | 进程路径匹配 |
| `NETWORK` | `NETWORK,udp,Proxy` | 网络类型匹配 (tcp/udp) |
| `SUB-RULE` | `SUB-RULE,(netflix rules),Proxy` | 子规则匹配 |
| `AND` | `AND,((NETWORK,UDP),(DST-PORT,443)),REJECT` | 逻辑与 |
| `OR` | `OR,((GEOIP,CN),(GEOIP,TW)),DIRECT` | 逻辑或 |
| `NOT` | `NOT,((DOMAIN,example.com)),Proxy` | 逻辑非 |
| `RULE-SET` | `RULE-SET,reject,REJECT` | 规则集匹配 |
| `MATCH` | `MATCH,DIRECT` | 匹配所有 (通常放最后) |

### 规则优先级

规则**按顺序匹配**，先匹配到的规则生效。一般顺序：
1. 内网/局域网规则
2. 特定应用规则 (如 Telegram)
3. 广告屏蔽规则
4. 分地区规则 (流媒体等)
5. 国内直连规则
6. `MATCH` 兜底规则

### 示例

```yaml
rules:
  # 内网直连
  - IP-CIDR,192.168.0.0/16,DIRECT
  - IP-CIDR,10.0.0.0/8,DIRECT

  # 广告屏蔽
  - RULE-SET,reject,REJECT

  # 特定应用
  - PROCESS-NAME,telegram,Proxy

  # 流媒体
  - RULE-SET,netflix,Streaming
  - RULE-SET,disney,Streaming

  # 国内直连
  - GEOIP,CN,DIRECT,no-resolve

  # 兜底
  - MATCH,Proxy
```

## 六、DNS 配置

```yaml
dns:
  enable: true
  listen: 0.0.0.0:53
  ipv6: true
  enhanced-mode: fake-ip           # fake-ip / redir-host
  fake-ip-range: 198.18.0.1/16
  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "localhost"
    - "*.example.com"
  default-nameserver:
    - 8.8.8.8
    - 114.114.114.114
  nameserver:
    - https://dns.google/dns-query
    - https://doh.pub/dns-query
  fallback:
    - https://dns.cloudflare.com/dns-query
    - https://dns.quad9.net/dns-query
  fallback-filter:
    geoip: true
    geoip-code: CN
    ipcidr:
      - 240.0.0.0/4
  nameserver-policy:
    "geosite:cn":
      - https://doh.pub/dns-query
      - 114.114.114.114
    "geosite:google":
      - https://dns.google/dns-query
  prefer-h3: true
```

## 七、Inbounds (入口)

### 代理端口

```yaml
mixed-port: 7890      # 混合端口 (HTTP + SOCKS5)
port: 7890            # HTTP 代理
socks-port: 7891      # SOCKS5 代理
redir-port: 7892      # 透明代理 (Linux/macOS)
tproxy-port: 7893     # TPROXY (Linux)
```

### TUN 模式

```yaml
tun:
  enable: true
  stack: mixed        # system / gvisor / mixed
  dns-hijack:
    - any:53
  auto-route: true
  auto-detect-interface: true
  mtu: 9000
  strict-route: false
```

### Listener (多入口)

```yaml
listeners:
  - name: socks5-in-1
    type: socks5
    port: 1081
    listen: 0.0.0.0

  - name: http-in-1
    type: http
    port: 8090
    listen: 0.0.0.0
```

## 八、Proxy Providers (代理提供者)

```yaml
proxy-providers:
  # HTTP 类型
  provider1:
    type: http
    url: "https://example.com/proxy.yaml"
    path: ./proxy_providers/provider1.yaml
    interval: 3600                    # 更新间隔(秒)
    proxy: DIRECT                     # 下载使用的代理
    size-limit: 0                     # 文件大小限制
    header:
      User-Agent:
        - "mihomo/1.18.3"
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
      timeout: 5000
      lazy: true
      expected-status: 204
    override:
      tfo: false
      mptcp: false
      udp: true
      skip-cert-verify: true
      interface-name: eth0
      down: "50 Mbps"
      up: "10 Mbps"
    filter: "(?i)港|hk|hongkong"
    exclude-filter: "美|日"
    exclude-type: "Shadowsocks|Http"

  # File 类型
  provider2:
    type: file
    path: ./proxy_providers/provider2.yaml
    health-check:
      enable: true
      interval: 300
```

## 九、Rule Providers (规则提供者)

```yaml
rule-providers:
  # 域名类型 (Domain)
  reject:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt"
    path: ./ruleset/reject.yaml
    interval: 86400

  # IP 类型 (IP-CIDR)
  private:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt"
    path: ./ruleset/private.yaml
    interval: 86400

  # 经典类型 (Classical - 混合规则)
  cn-domain:
    type: http
    behavior: classical
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt"
    path: ./ruleset/cn-domain.yaml
    interval: 86400

  # 直接类型 (纯文本规则)
  telegram:
    type: http
    behavior: classical
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt"
    path: ./ruleset/telegram.yaml
    interval: 86400
```

**behavior 类型：**
- `domain`: 仅包含 DOMAIN / DOMAIN-SUFFIX / DOMAIN-KEYWORD 规则
- `ipcidr`: 仅包含 IP-CIDR / IP-CIDR6 规则
- `classical`: 可包含所有类型规则

## 十、Clash vs mihomo 差异

| 特性 | 原版 Clash | mihomo (Clash Meta) |
|------|-----------|-------------------|
| VMess Reality | ❌ | ✅ |
| VLESS XTLS | ❌ | ✅ |
| Hysteria2 | ❌ | ✅ |
| TUIC v5 | ❌ | ✅ |
| AnyTLS | ❌ | ✅ |
| WireGuard 出站 | ❌ | ✅ |
| SSH 出站 | ❌ | ✅ |
| MASQUE | ❌ | ✅ |
| 多入口 Listener | ❌ | ✅ |
| SMux 多路复用 | ❌ | ✅ |
| TCP Brutal | ❌ | ✅ |
| 规则逻辑 (AND/OR/NOT) | ❌ | ✅ |
| 子规则 (SUB-RULE) | ❌ | ✅ |
| 进程名匹配 | ❌ | ✅ |
| 配置格式 | YAML | YAML (完全兼容) |
| API | ✅ | ✅ (扩展) |
| TUN 模式 | ✅ | ✅ |

## 十一、常用公共规则集

| 名称 | URL |
|------|-----|
| 拒绝规则 | `https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt` |
| 直连规则 | `https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt` |
| 代理规则 | `https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt` |
| 私网规则 | `https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt` |
| 苹果规则 | `https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt` |
| 电报规则 | `https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt` |
| GEO 数据 | `https://github.com/Loyalsoldier/v2ray-rules-dat` |
| Meta 规则数据 | `https://github.com/MetaCubeX/meta-rules-dat` |
