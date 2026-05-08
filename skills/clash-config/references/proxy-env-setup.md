# 代理环境变量配置指南

> 当 mihomo 已正常运行，但某些应用（如 Python 的 httpx/requests、Hermes vision 工具）无法走代理时的排查和解决方案。

## 一、需要配置的原因

很多应用和库并非原生支持 mihomo/Clash 的代理端口。它们通过读取环境变量来决定是否走代理：

| 变量 | 用途 | 被哪些库读取 |
|------|------|-------------|
| `HTTP_PROXY` | HTTP 请求的代理 | `requests`, `httpx`, `curl`, `wget` |
| `HTTPS_PROXY` | HTTPS 请求的代理 | `requests`, `httpx`, `curl`, `wget` |
| `http_proxy` | HTTP 请求（小写） | 部分传统工具 |
| `https_proxy` | HTTPS 请求（小写） | 部分传统工具 |
| `NO_PROXY` | 不走代理的白名单 | 所有上述工具 |

**关键坑**：Python 的 `requests` 和 `httpx` 库优先读取 **大写的** `HTTP_PROXY` / `HTTPS_PROXY`。如果只配了小写版本，Python 应用可能完全不走代理！

## 二、三层配置法

为了让代理环境变量对所有场景生效，需要在三个层面分别配置：

```
┌──────────────────────────────────────────┐
│  Layer 1: 交互式 Shell (~/.bashrc)        │ ← 登录服务器后 terminal 使用
├──────────────────────────────────────────┤
│  Layer 2: systemd 用户服务                │ ← Hermes Gateway 等 background service
│            (~/.config/environment.d/)     │
├──────────────────────────────────────────┤
│  Layer 3: 应用专属配置文件                │ ← 各工具的内部配置
│            (Hermes: ~/.hermes/.env)       │
└──────────────────────────────────────────┘
```

### Layer 1: ~/.bashrc（交互式 Shell）

```bash
# 追加到 ~/.bashrc 末尾
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export http_proxy=$HTTP_PROXY
export https_proxy=$HTTPS_PROXY
export NO_PROXY=localhost,127.0.0.1,.local,.hermes
```

- 生效时机：新开终端或 `source ~/.bashrc`
- 覆盖范围：bash 交互式 shell

### Layer 2: systemd environment.d（用户级服务）

```bash
# 创建配置文件
mkdir -p ~/.config/environment.d
cat > ~/.config/environment.d/proxy.conf << 'EOF'
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
http_proxy=http://127.0.0.1:7890
https_proxy=http://127.0.0.1:7890
NO_PROXY=localhost,127.0.0.1,.local,.hermes
EOF
```

- 生效时机：`systemctl --user daemon-reload` 后，所有新启动的 user service 自动继承
- 覆盖范围：所有 systemd --user 服务（如 Hermes Gateway）
- 不会影响已运行的服务，需要重启服务才能生效

### Layer 3: 应用专属配置

对于使用 `EnvironmentFile=` 加载环境变量的服务（如 Hermes Gateway），可直接在对应的 `.env` 文件中追加：

```bash
# ~/.hermes/.env 中追加
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
http_proxy=http://127.0.0.1:7890
https_proxy=http://127.0.0.1:7890
NO_PROXY=localhost,127.0.0.1,.local,.hermes
```

### 验证配置是否生效

```bash
# 查看当前 shell 环境
env | grep -i proxy

# 模拟新 shell（测试 .bashrc 是否生效）
bash -c 'echo "HTTP_PROXY=$HTTP_PROXY"'

# Python 环境测试
python3 -c "
import os
for k in sorted(os.environ):
    if 'proxy' in k.lower():
        print(f'{k}={os.environ[k]}')
"

# 测试 httpx 能否走代理
python3 -c "
import httpx
r = httpx.get('https://www.google.com')
print(f'HTTP {r.status_code}')
"
```

## 三、常见问题排查

### ❌ 现象：mihomo 正常运行，但某些应用连不上外网

```
检查清单：
1. □ mihomo 进程是否运行？          → ps aux | grep mihomo
2. □ mihomo 端口是否监听？          → ss -tlnp | grep 7890
3. □ HTTP_PROXY 环境变量是否存在？   → env | grep -i proxy
4. □ 大写和小写版本是否都配了？      → 见上方"关键坑"
5. □ systemd 服务是否重启了？        → systemctl --user restart <service>
```

### ❌ 现象：本地服务测试（curl/postman）返回 502 Bad Gateway 或不正常

当 `http_proxy` / `HTTPS_PROXY` 设置了 `127.0.0.1:7890` 但测试本地服务（如 SRA 在 `127.0.0.1:8536`、mihomo API 在 `127.0.0.1:9090`）时：
- curl 日志显示 `Trying 127.0.0.1:7890...` — 说明请求走了代理而非直连本地
- 报 `502 Bad Gateway` 或连接超时

**原因**：curl 等工具自动读取 `http_proxy` 环境变量，即使目标是 localhost 也会尝试走代理。

**解决**：
```bash
# 方案1：加 --noproxy 参数（推荐，不影响全局）
curl --noproxy '*' -s http://127.0.0.1:8536/recommend

# 方案2：临时取消代理环境变量
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 方案3：确保 NO_PROXY 已设置（见上方三层配置法）
export NO_PROXY=localhost,127.0.0.1,.local,.hermes
```

### ❌ 现象：[Errno 101] Network is unreachable

这是一个系统级的网络不可达错误，常见原因：

| 原因 | 排查方法 | 解决 |
|------|---------|------|
| 代理进程挂了 | `ps aux \| grep mihomo` | 重启 mihomo |
| 代理环境变量缺失 | `env \| grep -i proxy` | 按三层配置法补齐 |
| 代理节点瞬断 | `curl -x http://127.0.0.1:7890 https://www.google.com` | 等待或切换节点 |
| DNS 解析失败 | `curl -x http://127.0.0.1:7890 https://8.8.8.8` | 检查 DNS 配置 |

### ❌ 现象：Python 应用能直连但走不了代理

```bash
# 检查 Python 看到的代理变量
python3 -c "
import os
for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy']:
    v = os.environ.get(k, '(未设置)')
    print(f'{k}={v}')
"
```

如果未设置大写版本，需要补充：
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

## 四、三条经验法则

1. **四个变量都配齐**：大写和小写、HTTP 和 HTTPS 都要配
2. **三层都配到**：shell + systemd + 应用配置
3. **配完后记得重启**：环境变量只在进程启动时读取一次，运行中的进程需要重启才能生效
