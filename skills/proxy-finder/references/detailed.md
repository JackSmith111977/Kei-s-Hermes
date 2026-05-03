# Detailed Reference

## Phase 2: 下载订阅

### 2.1 直接下载 Clash YAML

```bash
curl -sL --connect-timeout 15 "<订阅URL>" -o /tmp/proxy-dl/<来源>.yaml
```

### 2.2 验证下载

```bash
# 检查文件大小
wc -c /tmp/proxy-dl/<来源>.yaml

# 检查节点数量
grep -c "^  - name:" /tmp/proxy-dl/<来源>.yaml

# 检查协议分布
grep "^    type:" /tmp/proxy-dl/<来源>.yaml | sort | uniq -c | sort -rn
```

### 2.3 合并多个源

```bash
# 使用 yq 或 Python 合并多个 YAML 的 proxies 部分
python3 -c "
import yaml, glob
all_proxies = []
for f in glob.glob('/tmp/proxy-dl/*.yaml'):
    with open(f) as fh:
        data = yaml.safe_load(fh)
        proxies = data.get('proxies', [])
        # 添加来源标记
        for p in proxies:
            p['name'] = f\"[{f.split('/')[-1].replace('.yaml','')}] {p.get('name','?')}\"
        all_proxies.extend(proxies)
print(f'合并后共 {len(all_proxies)} 个节点')
with open('/tmp/proxy-dl/merged.yaml', 'w') as fh:
    yaml.dump({'proxies': all_proxies}, fh, allow_unicode=True)
"
```

## Phase 3: 测试节点连通性

### 3.1 TCP 连通性测试（快速）

```bash
python3 ~/.hermes/skills/proxy-finder/scripts/test_nodes.py \
  --input /tmp/proxy-dl/merged.yaml \
  --output /tmp/proxy-results.json \
  --timeout 5 \
  --max-nodes 50 \
  --test-type tcp \
  --workers 10
```

### 3.2 HTTP 代理测试（准确但慢）

```bash
python3 ~/.hermes/skills/proxy-finder/scripts/test_nodes.py \
  --input /tmp/proxy-dl/merged.yaml \
  --output /tmp/proxy-results-http.json \
  --timeout 10 \
  --max-nodes 30 \
  --test-type http \
  --workers 5
```

### 3.3 单节点手动测试

```bash
# TCP 测试
timeout 5 bash -c "echo >/dev/tcp/<server>/<port>" && echo "✅ 连通" || echo "❌ 不通"

# 通过 curl 测试 HTTP 代理
curl -x socks5://<server>:<port> -s -o /dev/null -w "%{http_code}" \
  --connect-timeout 5 https://www.gstatic.com/generate_204
```

## Phase 4: 筛选排序

### 4.1 从测试结果提取可用节点

```python
import json, yaml

with open('/tmp/proxy-results.json') as f:
    data = json.load(f)

available = [r for r in data['results'] if r['ok']]
available.sort(key=lambda x: x['latency_ms'])

# 按协议分组
from collections import defaultdict
by_type = defaultdict(list)
for r in available:
    by_type[r['type']].append(r)

for t, nodes in by_type.items():
    print(f"{t}: {len(nodes)} 个可用节点")
    for n in nodes[:5]:
        print(f"  {n['name']} - {n['latency_ms']:.0f}ms")
```

### 4.2 筛选策略

- **延迟 < 300ms**：优质节点
- **延迟 300-800ms**：可用节点
- **延迟 > 800ms**：备用节点
- **协议优先级**：VLESS+Reality > Trojan > VMess > SS > HTTP

## Phase 5: 写入 mihomo 配置

### 5.1 使用 proxy-providers（推荐）

在 `~/.config/mihomo/config.yaml` 中配置 `proxy-providers`：

```yaml
proxy-providers:
  机场名称:
    type: http
    url: "订阅链接"
    path: ./proxy_providers/名称.yaml
    interval: 3600
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
```

参见 `templates/mihomo-airport.yaml` 完整配置模板。

### 5.2 写入内联节点

```python
import json, yaml

with open('/tmp/proxy-results.json') as f:
    data = json.load(f)

available = [r for r in data['results'] if r['ok']][:20]  # 取前20个

with open('/tmp/hermes/skills/proxy-finder/templates/mihomo-airport.yaml') as f:
    config = yaml.safe_load(f)

config['proxies'] = [r['raw'] for r in available]

with open(os.path.expanduser('~/.config/mihomo/config.yaml'), 'w') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

print(f"✅ 已写入 {len(available)} 个节点到 mihomo 配置")
```

### 5.3 重启 mihomo

```bash
# 先验证配置语法
mihomo -t -f ~/.config/mihomo/config.yaml

# 重启（假设用 systemd）
systemctl restart mihomo

# 或手动重启
pkill mihomo
nohup mihomo -f ~/.config/mihomo/config.yaml > /tmp/mihomo.log 2>&1 &
```

## 安全注意事项

> ⚠️ **免费节点有风险！**

1. **不要用免费节点做敏感操作**（网银、重要账号登录）
2. **定期更换节点**：免费节点随时失效
3. **优先使用 HTTPS 网站**
4. **重要账号开启双重验证**
5. **付费机场更稳定安全**：每月 10-30 元即可获得稳定服务
6. **不要在代理环境下保存密码**

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 所有节点都超时 | 检查网络连通性，尝试更换订阅源 |
| mihomo 启动失败 | 检查 YAML 语法：`mihomo -t -f config.yaml` |
| 订阅下载失败 | 检查 URL 是否有效，尝试用 curl -v 调试 |
| 节点连上但无法上网 | 尝试不同协议（VLESS/Trojan 通常更稳定） |
| GitHub 被墙 | 使用 gh-proxy.com 代理：`https://gh-proxy.com/https://raw.githubusercontent.com/...` |

---

## 设计模式映射（skill-creator v10.1.0）

### 🔄 Pipeline 模式（主模式）
- **适用场景**：完整的机场搜集 → 测试 → 写入配置流程
- **流程**：
  ```
  Phase 1: 搜集订阅源（Tavily 搜索 + 已知源）
  Phase 2: 下载订阅（curl 下载 + 验证）
  Phase 3: 测试节点（TCP/HTTP 连通性测试）
  Phase 4: 筛选排序（按延迟/协议筛选）
  Phase 5: 写入配置（proxy-providers 或内联节点）
  ```

### 📦 Tool Wrapper 模式
- **适用场景**：单节点测试、手动验证代理连通性
- **流程**：test_nodes.py 脚本封装 → 传入参数 → 输出结果

### 🔍 Reviewer 模式
- **适用场景**：验证已有配置的节点可用性
- **流程**：读取配置 → 批量测试 → 输出可用率报告

---

## 评估体系（Stage 9）

### 评估维度

| 维度 | 权重 | 关键检查点 |
|------|------|-----------|
| E1 节点可用率 | 30% | 测试节点中可用比例 ≥ 50% |
| E2 延迟质量 | 25% | 优质节点（<300ms）≥ 3 个 |
| E3 协议多样性 | 20% | 覆盖 ≥ 2 种协议（VLESS/Trojan/VMess） |
| E4 配置正确性 | 15% | 写入后 mihomo -t 验证通过 |
| E5 安全性 | 10% | 已提示免费节点风险 |

### Grader 等级

| 总分 | 等级 | 行动 |
|------|------|------|
| ≥ 0.90 | ✅ PASS | 直接交付使用 |
| 0.75-0.89 | ⚠️ WARN | 补充节点后交付 |
| 0.60-0.74 | ❌ FAIL | 更换订阅源重试 |
| < 0.60 | 🚨 CRITICAL | 检查网络连通性后重试 |

*Proxy-Finder v2.0.0 | 基于 skill-creator v10.1.0 升级*
