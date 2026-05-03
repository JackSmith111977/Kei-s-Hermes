# Detailed Reference

## 五、配置生成指南

### 5.1 最小配置生成

当用户需要一个最小可用配置时：

1. 从 `templates/standard-config.yaml` 读取最小配置模板
2. 替换 `proxies` 中的节点信息
3. 验证配置文件

### 5.2 标准配置生成

当用户需要一个完整配置时：

1. 从 `templates/standard-config.yaml` 读取标准配置模板
2. 根据用户需求调整：
   - 代理节点列表
   - proxy-providers URL
   - proxy-groups 分组和过滤规则
   - rules 路由规则
3. 验证配置文件

### 5.3 协议选择指南

| 需求 | 推荐协议 | 说明 |
|------|---------|------|
| 简单稳定 | Shadowsocks (ss) | 兼容性好，客户端广泛 |
| 主流机场 | VMess / VLESS | 大部分机场支持 |
| 最强抗干扰 | VLESS + Reality | 伪装成 TLS 1.3 |
| 高速传输 | Hysteria2 | 基于 QUIC，抗丢包 |
| 低延迟游戏 | TUIC v5 | 基于 QUIC |
| 二次代理 | WireGuard | 作为出站协议 |

---

## 六、路由规则最佳实践

### 规则顺序（从上到下匹配）

```
1. 内网/局域网规则 → DIRECT
2. 广告屏蔽规则 → REJECT
3. 特定应用规则 → 指定代理组
4. 流媒体分流规则 → 指定代理组
5. 国内直连规则 → DIRECT
6. MATCH 兜底规则 → 默认代理组
```

### 常用规则集

| 规则集 | behavior | URL |
|--------|----------|-----|
| 广告屏蔽 | classical | Loyalsoldier/clash-rules release/reject.txt |
| 国内域名 | classical | Loyalsoldier/clash-rules release/direct.txt |
| 国外域名 | classical | Loyalsoldier/clash-rules release/proxy.txt |
| 私网 IP | ipcidr | Loyalsoldier/clash-rules release/private.txt |
| Telegram | classical | Loyalsoldier/clash-rules release/telegramcidr.txt |
| Apple | classical | Loyalsoldier/clash-rules release/apple.txt |

---

## 七、DNS 配置建议

### 国内用户推荐

```yaml
dns:
  enable: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  default-nameserver:
    - 114.114.114.114
    - 223.5.5.5
  nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query
  fallback:
    - https://dns.google/dns-query
    - https://dns.cloudflare.com/dns-query
  fallback-filter:
    geoip: true
    geoip-code: CN
```

---

## 八、常见问题排查

### ❌ 配置文件错误
```bash
# 验证配置
mihomo -t -f config.yaml
```

### ❌ 代理不工作
```bash
# 检查端口是否监听
ss -tlnp | grep 7890

# 检查进程是否运行
ps aux | grep mihomo

# 检查日志
tail -f /tmp/mihomo.log
```

### ❌ DNS 泄漏
```bash
# 检查 DNS 配置
cat ~/.config/mihomo/config.yaml | grep -A 20 "dns:"

# 测试 DNS 泄漏
curl -x http://127.0.0.1:7890 https://ipleak.net/json/
```

### ❌ 订阅更新失败
```bash
# 手动下载订阅
curl -x http://127.0.0.1:7890 "https://your-provider.com/sub?token=xxx" -o ./proxy_providers/provider.yaml
```

---

## 九、mihomo 特有功能

mihomo (Clash Meta) 相比原版 Clash 的额外功能：

| 功能 | 说明 |
|------|------|
| VMess Reality | VLESS + REALITY 协议支持 |
| Hysteria2 | QUIC 高速代理协议 |
| TUIC v5 | 低延迟 QUIC 协议 |
| AnyTLS | 新型 TLS 伪装协议 |
| MASQUE | HTTP/3 代理隧道 |
| WireGuard 出站 | 作为出站代理协议 |
| SSH 出站 | 作为出站代理协议 |
| SMux 多路复用 | 连接复用减少握手 |
| TCP Brutal | 高性能拥塞控制 |
| 规则逻辑 | AND / OR / NOT 逻辑组合 |
| 子规则 | SUB-RULE 规则分组 |
| 进程匹配 | PROCESS-NAME / PROCESS-PATH |
| 多入口 | listeners 多端口监听 |
| TrustTunnel | 新型隧道协议 |

---

## 十、References 索引

| 文件 | 何时加载 |
|------|----------|
| `references/config-reference.md` | 需要查询具体配置字段、协议参数、完整参考时 |
| `templates/standard-config.yaml` | 需要生成配置模板时 |

---

## 十一、设计模式映射（skill-creator v10.1.0）

### 📦 Tool Wrapper 模式（主模式）
- **适用场景**：查询配置字段、生成配置模板、验证配置文件
- **流程**：读取参考文档 → 按需注入配置片段 → 生成/修改配置 → 验证
- **Token 优化**：只加载需要的配置字段文档，不加载全部参考

### 🔄 Pipeline 模式（配置生成时）
- **适用场景**：从零生成完整 mihomo 配置
- **流程**：
  ```
  Stage 1: 需求分析（端口/协议/路由需求）
  Stage 2: 加载模板（templates/standard-config.yaml）
  Stage 3: 填充节点（proxies / proxy-providers）
  Stage 4: 配置路由（proxy-groups / rules）
  Stage 5: 验证配置（mihomo -t -f config.yaml）
  Stage 6: 启动服务（mihomo -f config.yaml）
  ```

---

## 十二、评估体系（Stage 9）

### 评估维度

| 维度 | 权重 | 关键检查点 |
|------|------|-----------|
| E1 配置正确性 | 30% | YAML 语法正确、字段值合法、能通过 mihomo -t 验证 |
| E2 协议适当性 | 20% | 协议选择符合需求（速度/稳定性/抗干扰） |
| E3 路由完整性 | 20% | 规则覆盖所有场景、无遗漏、顺序正确 |
| E4 DNS 安全性 | 15% | 无 DNS 泄漏、fake-ip 配置正确 |
| E5 可维护性 | 15% | 有注释、结构清晰、proxy-providers 分离 |

### Grader 等级

| 总分 | 等级 | 行动 |
|------|------|------|
| ≥ 0.90 | ✅ PASS | 直接交付使用 |
| 0.75-0.89 | ⚠️ WARN | 小修后交付 |
| 0.60-0.74 | ❌ FAIL | 返工对应阶段 |
| < 0.60 | 🚨 CRITICAL | 重新设计配置 |

*Clash-Config v2.0.0 | 基于 skill-creator v10.1.0 升级*
