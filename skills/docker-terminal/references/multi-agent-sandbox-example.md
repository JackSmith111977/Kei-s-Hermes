# 多 Agent Docker 沙箱搭建记录

> 日期: 2026-05-17 | 环境: Ubuntu, Docker 29.1.3, mihomo v1.19.3
> 目标: 创建三个隔离的 Docker 容器，分别承载 Hermes Agent, OpenCode, OpenClaw

## 环境概况

- **Docker 版本**: 29.1.3
- **磁盘**: 50G (17G 可用)
- **代理**: mihomo mixed-proxy on port 7890
- **用户**: ubuntu (在 docker 组)
- **DNS**: systemd-resolved (127.0.0.53), 腾讯云 DNS 119.29.29.29 可用

## 关键步骤

### 1. Docker Daemon 配置

```bash
# daemon.json — registry mirrors
sudo python3 -c "
import json, os
config = {'registry-mirrors': ['https://mirror.ccs.tencentyun.com']}
with open('/etc/docker/daemon.json', 'w') as f:
    json.dump(config, f, indent=2)
os.system('systemctl daemon-reload')
os.system('systemctl restart docker')
"

# systemd proxy drop-in（可选，在同时需要 daemon 级代理时）
sudo python3 -c "
import os
os.makedirs('/etc/systemd/system/docker.service.d', exist_ok=True)
with open('/etc/systemd/system/docker.service.d/proxy.conf', 'w') as f:
    f.write('[Service]\n')
    f.write('Environment=\"HTTP_PROXY=http://127.0.0.1:7890\"\n')
    f.write('Environment=\"HTTPS_PROXY=http://127.0.0.1:7890\"\n')
os.system('systemctl daemon-reload')
os.system('systemctl restart docker')
"
```

### 2. 镜像拉取

```bash
# 总耗时约 1-2 分钟（通过腾讯云镜像）
sg docker -c "docker pull nikolaik/python-nodejs:python3.12-nodejs22"
sg docker -c "docker pull node:22-bookworm-slim"
```

### 3. 容器创建

详见 docker-terminal skill §七「多容器 Agent 沙箱架构」。

### 4. Agent 安装

```bash
# Hermes（用时 ~2 分钟，依赖 Python 3.12）
sg docker -c "docker exec -d hermes-agent-box pip3 install hermes-agent"
sleep 90  # 等 pyyaml/dotenv/rich 等依赖下载
sg docker -c "docker exec hermes-agent-box pip3 install python-dotenv pyyaml rich"

# OpenCode（通过 npm, ~30 秒）
sg docker -c "docker exec -d opencode-agent-box npm install -g opencode-ai@latest"

# OpenClaw（通过 npm, ~30 秒）
sg docker -c "docker exec -d openclaw-agent-box npm install -g openclaw@latest"
```

### 5. 验证结果

```bash
# 版本检查
docker exec hermes-agent-box hermes --version     # v0.13.0
docker exec opencode-agent-box opencode --version  # 1.15.3
docker exec openclaw-agent-box openclaw --version  # 2026.5.12
```

## 已知陷阱

### 陷阱 1: sudo + 管道重定向 hang

`sleep 3 && sudo tee /etc/docker/daemon.json > /dev/null <<< '...'` 这种写法在通过 Hermes terminal 执行时经常 hang。**解决方案**: 用 Python 脚本写文件 + `os.system()` 调用 systemctl。

### 陷阱 2: sg docker -c 嵌套引号

`sg docker -c "docker exec container bash -c 'long command with &&'"` 在 cmd 链复杂时引号解析失败。
**解决方案**: 写脚本 → `docker cp` → `docker exec -d container bash /script.sh`。

### 陷阱 3: 终端超时杀死后台进程

Hermes terminal 的默认 timeout 限制导致 `pip install` 等长任务被 KILL。
**解决方案**: `docker exec -d` (detached mode) 在后台运行，之后轮询检查。

### 陷阱 4: 容器内 GitHub 不可达

通过 mihomo 代理时 GitHub 的 git clone 经常 TLS 超时。
**解决方案**: 对 Hermes 使用 `pip install hermes-agent` 替代 `install.sh`（后者需要 git clone 仓库）。

### 陷阱 5: OpenClaw 容器无 curl/python

`node:22-bookworm-slim` 只含 Node.js，不含 curl、python、ping。
**影响**: 无法在容器内直接做 HTTP 测试。通过其他容器（如 opencode-agent-box）测试网络连通性。
