# 代理生命周期管理

> mihomo 代理的完整生命周期：启动 → 验证 → 监控 → 停止 → 重启

## 一、完整启动流程

```python
# Step 1: 检查配置是否有效
terminal(command="mihomo -t -f ~/.config/mihomo/config.yaml")

# Step 2: 后台启动 mihomo（使用 Hermes process 工具）
terminal(command="mihomo -f ~/.config/mihomo/config.yaml",
         background=True,
         watch_patterns=["Start initial configuration", "HTTP proxy started"])

# Step 3: 等待端口就绪
sleep 2

# Step 4: 验证代理连通性
# 检查端口是否监听
terminal(command="ss -tlnp | grep mihomo || netstat -tlnp | grep mihomo")
# 测试外网访问
terminal(command="curl -x http://127.0.0.1:7890 https://www.google.com -s -o /dev/null -w '%{http_code}' --connect-timeout 5")
```

## 二、验证清单

启动后按顺序检查：

| # | 检查项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 进程运行 | `process(action="poll")` | status=running |
| 2 | 端口监听 | `ss -tlnp \| grep 7890` | LISTEN |
| 3 | HTTP 代理 | `curl -x http://127.0.0.1:7890 https://google.com` | 200 |
| 4 | SOCKS5 代理 | `curl -x socks5://127.0.0.1:7890 https://google.com` | 200 |
| 5 | API 可用 | `curl http://127.0.0.1:9090/version` | JSON 响应 |

## 三、停止方式

### 方式 A：优雅停止（通过 API 推荐）

```bash
curl -X PUT http://127.0.0.1:9090/stop
```

### 方式 B：Hermes process 工具终止

```python
# 如果通过 terminal(background=true) 启动
process(action="kill", session_id="<session_id>")
```

### 方式 C：强制终止

```bash
pkill mihomo
```

## 四、重启流程

```python
# 1. 停止（API 优雅停止）
terminal(command="curl -X PUT http://127.0.0.1:9090/stop")

# 2. 等待端口释放
sleep 2

# 3. 确认旧进程已结束
terminal(command="pgrep mihomo || echo 'clean'")

# 4. 重新启动
terminal(command="mihomo -f ~/.config/mihomo/config.yaml",
         background=True,
         watch_patterns=["Start initial configuration"])

# 5. 验证
sleep 2
terminal(command="curl -x http://127.0.0.1:7890 https://www.google.com -s -o /dev/null -w '%{http_code}'")
```

## 五、常见场景

### 场景 1：配置变更后需要重启
```python
# 改完配置后验证
terminal(command="mihomo -t -f ~/.config/mihomo/config.yaml")
# 然后按"四、重启流程"执行
```

### 场景 2：代理不通但进程在运行
```python
# 切换节点
terminal(command='curl -X PUT "http://127.0.0.1:9090/proxies/🚀%20Proxy" -d \'{"name":"⚡ Auto"}\'')
# 测延迟
terminal(command='curl -X GET "http://127.0.0.1:9090/proxies/⚡%20Auto/delay?url=https://www.gstatic.com/generate_204&timeout=5000"')
```

### 场景 3：只想临时换节点不用重启
```bash
# 获取当前代理组
curl -s http://127.0.0.1:9090/proxies | python3 -m json.tool
# 切换特定节点
curl -X PUT "http://127.0.0.1:9090/proxies/🚀%20Proxy" -d '{"name":"🇯🇵 JP xxx"}'
```

## 六、相关技能联动

- `process-management` — 后台进程管理的通用最佳实践
- `proxy-monitor` — 代理节点健康监控与部署流水线
- `web-access` — 联网操作统一入口（会自动检查代理状态）
