# 免费代理订阅源参考

> 最后更新: 2026-05-03 00:42
> ⚠️ 免费节点随时可能失效，使用前请测试连通性

## 最近更新记录

- **2026-05-03**: 测试了 11 个订阅源，成功下载 6 个，共获得 149 个不重复节点，66 个可用（TCP 连通）
  - ✅ 可用源: anaer, Barabama(89节点), ermaozi, 10ium, mermeroo, itsyebekhe(45节点), Misaka-blog(67节点)
  - ❌ 404失效: barry-far, rxsweet, aiboboxx, oslook, learnhard-cn, MrMohebi

## 一、Clash/Mihomo 订阅源

### 高可用源（已测试 2026-05 可用）

| 名称 | 链接 | 协议 | 节点数 | 更新频率 |
|------|------|------|--------|----------|
| yoyapai | `https://freenode.yoyapai.com/2026/04/28-yoyapai.com-clash-vpn-mianfeijiedian.yaml` | VLESS/VMess/Trojan/SS | ~118 | 每日 |
| mermeroo | `https://raw.githubusercontent.com/mermeroo/V2RAY-and-CLASH-Subscription-Links/main/SUB%20LINKS` | 多协议 | 多个源 | 不定期 |
| barry-far | `https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt` | V2Ray | ~100+ | 每15分钟 |
| ebrasha | `https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/README.md` | SS/SSR/Trojan/VLESS/VMess | ~50+ | 每日 |
| 10ium/MihomoSaz | `https://raw.githubusercontent.com/10ium/MihomoSaz/main/Sublist/ainita.yaml` | 多协议 | ~35 | 不定期 |
| learnhard-cn | `https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/clash/config.yaml` | SS/SSR | ~50+ | 不定期 |
| Barabama/FreeNodes | `https://raw.githubusercontent.com/Barabama/FreeNodes/main/nodes/clashmeta.yaml` | ClashMeta | ~50+ | 不定期 |
| rxsweet | `https://raw.githubusercontent.com/rxsweet/proxies/main/sub/free.yaml` | 多协议 | ~100+ | 不定期 |
| aiboboxx | `https://raw.githubusercontent.com/aiboboxx/clashfree/main/clash.yml` | 多协议 | ~50+ | 不定期 |
| anaer | `https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml` | 多协议 | ~100+ | 不定期 |

### 备用源

| 名称 | 链接 |
|------|------|
| cxr9912 | `https://raw.githubusercontent.com/cxr9912/cxr2022/main/free.yaml` |
| itsyebekhe/PSG | `https://raw.githubusercontent.com/itsyebekhe/PSG/main/subscriptions/clash/mix` |
| MrMohebi | `https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/clash-meta/all.yaml` |
| Misaka-blog | `https://raw.githubusercontent.com/Misaka-blog/chromego_merge/main/sub/merged_proxies_new.yaml` |
| oslook | `https://raw.githubusercontent.com/oslook/clash-freenode/main/clash.yaml` |
| ermaozi | `https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml` |
| ermaozi01 | `https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/subscribe/clash.yml` |
| ts-sf | `https://raw.githubusercontent.com/ts-sf/fly/main/clash` |
| moneyfly1 | `https://raw.githubusercontent.com/moneyfly1/sublist/main/clash.yml` |

## 二、V2Ray 订阅源

| 名称 | 链接 |
|------|------|
| yoyapai V2Ray | `https://yoyapai.com/mianfeijiedian/20260428-ssr-v2ray-vpn-jiedian-yoyapai.com.txt` |
| barry-far Base64 | `https://github.com/barry-far/V2ray-Config/tree/dev/Base64` |
| MatinGhanbari | `https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/index.txt` |

## 三、GitHub Topics 持续发现

通过 GitHub Topics 发现新的免费代理仓库：

- https://github.com/topics/freeproxy
- https://github.com/topics/free-proxy
- https://github.com/topics/free-proxies
- https://github.com/topics/v2ray-config
- https://github.com/topics/free-v2ray
- https://github.com/topics/clash-config

## 四、mihomo proxy-providers 配置格式

在 mihomo 配置中使用 `proxy-providers` 自动更新订阅：

```yaml
proxy-providers:
  # 免费订阅源
  free-nodes:
    type: http
    url: "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml"
    path: ./proxy_providers/free-nodes.yaml
    interval: 3600  # 每小时更新
    proxy: DIRECT
    size-limit: 0
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
      timeout: 5000
      lazy: true
      expected-status: 204
    filter: "(?i)港|台|日本|新加坡|韩国|美国|HK|TW|JP|SG|KR|US"  # 可选：按地区过滤
```

## 五、安全注意事项

1. **免费节点有风险**：可能被监控、记录流量、突然失效
2. **敏感操作不要用免费节点**：网银、重要账号登录等
3. **定期测试**：免费节点存活时间短，需要频繁更新
4. **优先使用 HTTPS 网站**：增加一层加密保护
5. **不要用相同密码**：代理账号和其他重要账号密码要分开
6. **推荐使用机场付费服务**：稳定、高速、更安全
