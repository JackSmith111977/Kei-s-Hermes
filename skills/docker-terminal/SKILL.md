---
name: docker-terminal
description: Docker 沙箱终端执行指南 — 安全地在隔离容器中运行命令。涵盖配置、安全参数、镜像选择、卷挂载、资源限制、多容器 Agent 沙箱架构及中国网络环境 Docker 配置。当用户需要配置 Docker backend、搭建多 Agent 测试沙箱、排查容器问题、选择镜像或配置安全策略时使用此 skill。
version: 2.0.0
triggers:
  - docker terminal
  - container sandbox
  - terminal isolation
  - docker backend
  - 容器安全
  - sandboxed execution
  - Docker 沙箱
  - 隔离执行
  - multi-container
  - agent sandbox
  - docker network
  - docker proxy
  - 国内 docker
  - docker 镜像
  - registry mirror
  - docker daemon
  - 多容器
  - agent 测试
design_pattern: Tool Wrapper
skill_type: product-verification
depends_on: []

---

# Docker Terminal 沙箱执行

Hermes Agent 的 Docker backend 提供安全的容器化命令执行环境。所有命令在隔离的 Docker 容器中运行，具有降权的 Linux capabilities、进程隔离和可配置的资源限制。

## 何时使用

- 需要安全执行不可信或第三方代码
- 想要隔离的开发/实验环境（不影响宿主机）
- 需要特定语言版本或工具链（通过自定义镜像）
- 批量基准测试需要可重复的干净环境
- 排查容器配置、安全或挂载问题

## 快速启用

### 方法一：环境变量

在 Hermes 配置文件中设置 `TERMINAL_ENV=docker`。

### 方法二：config.yaml

```yaml
terminal:
  backend: "docker"
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  container_persistent: true
  container_cpu: 1
  container_memory: 5120
```

重启 Hermes Agent 后生效。

## 核心配置项

| 配置键 | 环境变量 | 默认值 | 说明 |
|--------|---------|--------|------|
| `terminal.backend` | `TERMINAL_ENV` | `"local"` | 设为 `"docker"` 启用 |
| `terminal.docker_image` | `TERMINAL_DOCKER_IMAGE` | `nikolaik/python-nodejs:python3.11-nodejs20` | 容器镜像 |
| `terminal.container_cpu` | `TERMINAL_CONTAINER_CPU` | `1` | CPU 核心数 |
| `terminal.container_memory` | `TERMINAL_CONTAINER_MEMORY` | `5120` | 内存上限 (MB) |
| `terminal.container_disk` | `TERMINAL_CONTAINER_DISK` | `51200` | 磁盘上限 (MB, 仅 XFS+overlay2) |
| `terminal.container_persistent` | `TERMINAL_CONTAINER_PERSISTENT` | `true` | 跨会话持久化文件系统 |
| `terminal.docker_forward_env` | `TERMINAL_DOCKER_FORWARD_ENV` | `[]` | 从宿主机传递的环境变量名列表 |
| `terminal.docker_env` | — | `{}` | 直接设置到容器的环境变量 (key-value) |
| `terminal.docker_volumes` | `TERMINAL_DOCKER_VOLUMES` | `[]` | 自定义卷挂载 `["host:container"]` |

## 安全特性（默认启用）

每个容器自动应用以下安全参数：

```
--cap-drop ALL                    # 移除所有 Linux capabilities
--cap-add DAC_OVERRIDE            # 仅保留：写入 bind-mount 目录
--cap-add CHOWN                   # 仅保留：修改文件属主（pip/npm 需要）
--cap-add FOWNER                  # 仅保留：绕过属主检查
--security-opt no-new-privileges  # 禁止获取新特权
--pids-limit 256                  # 防止 fork bomb
--tmpfs /tmp:rw,nosuid,size=512m
--tmpfs /var/tmp:rw,noexec,nosuid,size=256m
--tmpfs /run:rw,noexec,nosuid,size=64m
```

**这意味着即使容器内获得 root，也无法：**
- 挂载文件系统（缺少 `SYS_ADMIN`）
- 加载内核模块（缺少 `SYS_MODULE`）
- 使用原始 socket 嗅探（缺少 `NET_RAW`）
- 追踪宿主机进程（缺少 `SYS_PTRACE`）
- 通过特殊方式提升权限（受 `no-new-privileges` 保护）

## 镜像选择指南

### 默认镜像

```
nikolaik/python-nodejs:python3.11-nodejs20
```

预装 Python 3.11 + Node.js 20 + 常用构建工具。适合大多数场景。

### 常用替代

| 镜像 | 大小 | 适用场景 |
|------|------|---------|
| `python:3.12-slim` | ~150MB | 纯 Python 项目，快速启动 |
| `python:3.12` | ~1GB | Python + 需要编译 C 扩展 |
| `node:20-slim` | ~200MB | 纯 Node.js 项目 |
| `ubuntu:24.04` | ~78MB | 需要 apt 安装系统工具 |
| `debian:bookworm-slim` | ~80MB | 轻量 Debian 基础 |

## 持久化卷配置

### 持久化模式

```yaml
terminal:
  container_persistent: true  # 默认值
```

数据存储在 Hermes sandboxes 目录中：
- `home/` → 映射到容器 `/root`
- `workspace/` → 映射到容器 `/workspace`

跨会话保留已安装的包和文件。

### 临时模式

```yaml
terminal:
  container_persistent: false
```

使用 tmpfs，容器删除后数据丢失，适合一次性任务。

## 环境变量传递

### docker_forward_env（从宿主机读取）

```yaml
terminal:
  docker_forward_env: ["MY_API_KEY", "DATABASE_URL"]
```

从宿主机的环境变量中读取值传入容器。

### docker_env（直接指定值）

```yaml
terminal:
  docker_env:
    MY_VAR: "my_value"
    CONFIG_PATH: "/etc/myapp/config.yaml"
```

适合 systemd 服务部署（无用户 shell 环境变量）。

### 安全过滤

- Hermes 的 provider API keys 默认**不传递**
- 只有显式列入 `docker_forward_env` 的变量才会传递
- Skill 声明的 `required_environment_variables` 自动加入传递列表

## 排查指南

### 检查 Docker 是否可用

```bash
docker version
docker info
```

### 查看运行中的容器

```bash
docker ps --filter "name=hermes-"
```

### 容器启动失败

检查：
1. Docker daemon 是否运行
2. 镜像是否存在
3. 镜像拉取是否成功

## 最佳实践

### DO ✅

- ✅ 执行不可信代码时**始终**使用 Docker backend
- ✅ 预拉取常用镜像避免首次延迟
- ✅ 使用 `container_persistent: true` 用于交互式会话
- ✅ 使用 `container_persistent: false` 用于一次性/批量任务
- ✅ 通过 `docker_forward_env` 最小化环境变量传递

### DON'T ❌

- ❌ 挂载敏感目录到容器
- ❌ 传递不必要的 API keys 到容器
- ❌ 使用 `alpine` 镜像运行需要 glibc 的预编译二进制文件
- ❌ 在生产环境使用 `docker_mount_cwd_to_workspace: true`（削弱隔离）

---

## 六、中国网络环境 Docker 配置

> 当宿主机位于中国境内，Docker daemon 无法直连 Docker Hub 时使用此方案。

### 6.1 Registry Mirrors

```bash
# 用 Python 脚本写 daemon.json（sudo + 管道重定向可能 hang，用脚本更可靠）
sudo python3 -c "
import json, os
config = {'registry-mirrors': ['https://mirror.ccs.tencentyun.com']}
with open('/etc/docker/daemon.json', 'w') as f:
    json.dump(config, f, indent=2)
os.system('systemctl daemon-reload')
os.system('systemctl restart docker')
print('Done')
"
```

**可用的国内镜像**：
| 镜像地址 | 状态 |
|:---------|:-----|
| `https://mirror.ccs.tencentyun.com` | ✅ 腾讯云，稳定 |
| `https://docker.mirrors.ustc.edu.cn` | ⚠️ 有时 DNS 解析失败 |
| `https://hub-mirror.c.163.com` | ⚠️ 有时 DNS 解析失败 |

### 6.2 Docker Daemon 代理配置

当镜像拉取需要走 HTTP 代理时：

```bash
sudo python3 -c "
import os
dropin_dir = '/etc/systemd/system/docker.service.d'
os.makedirs(dropin_dir, exist_ok=True)
with open(f'{dropin_dir}/proxy.conf', 'w') as f:
    f.write('[Service]\n')
    f.write('Environment=\"HTTP_PROXY=http://127.0.0.1:7890\"\n')
    f.write('Environment=\"HTTPS_PROXY=http://127.0.0.1:7890\"\n')
    f.write('Environment=\"NO_PROXY=localhost,127.0.0.1\"\n')
os.system('systemctl daemon-reload')
os.system('systemctl restart docker')
print('Docker proxy configured')
"
```

### 6.3 Docker Socket 权限问题

症状：`permission denied while trying to connect to the Docker API at unix:///var/run/docker.sock`

```bash
# ❌ 直接执行（当前 shell 无 docker 组权限）
docker ps

# ✅ 用 sg 临时切换组
sg docker -c "docker ps"

# ✅ 或使用 newgrp 启动新 shell
newgrp docker
```

---

## 七、多容器 Agent 沙箱架构

> 用于运行多个隔离的 AI Agent（Hermes / OpenCode / OpenClaw）进行 Cap Pack 和 SRA 测试验证。

### 7.1 架构总览

```
        宿主机 (Host)
              │
         hermes-sandbox-net (bridge, 172.18.0.0/16)
              │
         ┌────┼────┐
         │    │    │
      herm  open  open
      -es   -code -claw
      (SRA  (编码  (网关
       :8536) 代理)   :18789)
              │
         ┌────┴────┐
      共享卷 (read-only)
      ~/projects/hermes-cap-pack
      ~/projects/sra
      ~/.hermes/skills
```

### 7.2 镜像选择

| Agent | 运行时需求 | 推荐镜像 | 大小 |
|:------|:-----------|:---------|:----:|
| **Hermes Agent** | Python 3.11+ + Node.js 22+ | `nikolaik/python-nodejs:python3.12-nodejs22` | ~1.2GB |
| **OpenCode** | Node.js 22+ | `nikolaik/python-nodejs:python3.12-nodejs22` | ~1.2GB |
| **OpenClaw** | Node.js 22.16+ | `node:22-bookworm-slim` | ~250MB |

### 7.3 创建网络

```bash
sg docker -c "docker network create hermes-sandbox-net"
```

### 7.4 启动三个空白 Agent 容器

```bash
# Hermes Agent
sg docker -c "docker run -d \
  --name hermes-agent-box \
  --hostname hermes-agent \
  --network hermes-sandbox-net \
  --memory 2g --cpus 1.0 --pids-limit 256 \
  --restart unless-stopped \
  -p 8537:8536 \
  -v ~/projects/hermes-cap-pack:/workspace/cap-pack:ro \
  -v ~/projects/sra:/workspace/sra:ro \
  -v ~/.hermes/skills:/workspace/skills:ro \
  nikolaik/python-nodejs:python3.12-nodejs22 \
  sleep infinity"

# OpenCode
sg docker -c "docker run -d \
  --name opencode-agent-box \
  --hostname opencode-agent \
  --network hermes-sandbox-net \
  --memory 1g --cpus 1.0 --pids-limit 256 \
  --restart unless-stopped \
  -v ~/projects/hermes-cap-pack:/workspace/cap-pack:ro \
  nikolaik/python-nodejs:python3.12-nodejs22 \
  sleep infinity"

# OpenClaw (Node.js only - no curl/python)
sg docker -c "docker run -d \
  --name openclaw-agent-box \
  --hostname openclaw-agent \
  --network hermes-sandbox-net \
  --memory 1g --cpus 1.0 --pids-limit 256 \
  --restart unless-stopped \
  -p 18789:18789 \
  node:22-bookworm-slim \
  sleep infinity"
```

### 7.5 容器内安装 Agent

```bash
# ⚠️ 用 docker exec -d（detached）避免终端超时

# Hermes（pip install 替代 install.sh，因 GitHub 可能不可达）
sg docker -c "docker exec -d hermes-agent-box pip3 install hermes-agent"
# 检查完成后安装依赖
sg docker -c "docker exec hermes-agent-box pip3 install python-dotenv pyyaml rich"

# OpenCode
sg docker -c "docker exec -d opencode-agent-box npm install -g opencode-ai@latest"

# OpenClaw
sg docker -c "docker exec -d openclaw-agent-box npm install -g openclaw@latest"
```

### 7.6 网络连通性验证

```bash
# 查看各容器 IP
sg docker -c "docker network inspect hermes-sandbox-net \
  --format '{{range .Containers}}{{.Name}} ({{.IPv4Address}}) {{end}}'"

# HTTP 通信测试
sg docker -c "docker exec opencode-agent-box \
  curl -s --connect-timeout 3 http://hermes-agent:8536/health"

# 注意：node:22-bookworm-slim 没有 curl/python，通过其他容器测试
```

---

## 八、长命令执行模式

> 网络延迟高、Agent 安装耗时长时的执行策略。

| 场景 | 推荐方式 | 理由 |
|:-----|:---------|:-----|
| 快速命令 (< 30s) | `docker exec <container> <cmd>` | 同步等待 |
| 中等任务 (30-180s) | `docker exec` + 足够 timeout | 可同步 |
| 长任务 (5min+) | **`docker exec -d`** 后轮询检查 | 避免终端超时 |
| 复杂安装 | 写 `.sh` 脚本 → `docker cp` → `exec -d` | 避免嵌套引号 |

### 8.1 脚本模式（避免嵌套引号问题）

```bash
# 1. 写脚本
cat > /tmp/install.sh << 'SCRIPT'
#!/bin/bash
export HTTP_PROXY=http://172.18.0.1:7890
pip install hermes-agent 2>&1
SCRIPT

# 2. 复制到容器
sg docker -c "docker cp /tmp/install.sh container:/tmp/"

# 3. 后台执行
sg docker -c "docker exec -d container bash /tmp/install.sh"

# 4. 轮询检查完成
sg docker -c "docker exec container which hermes"
```

### 8.2 嵌套引号注意事项

`sg docker -c "docker exec ... bash -c '...'"` 嵌套引号易失败：
- ❌ 多层 bash -c 嵌套 → 引号解析错误
- ✅ 脚本文件模式 → 零引号问题
- ✅ 单命令模式 → `docker exec -e KEY=VAL container command args`

---

## 九、容器内网络可达性速查

> 通过代理环境下，不同 registry 的可达性可能不同。

```bash
# 从容器内测试各端点
sg docker -c "docker exec <container> curl -s -o /dev/null -w '%{http_code}' https://registry.npmjs.org/"
sg docker -c "docker exec <container> curl -s -o /dev/null -w '%{http_code}' https://pypi.org/simple/"
sg docker -c "docker exec <container> curl -s -o /dev/null -w '%{http_code}' https://github.com"
```

**典型结果（通过 mihomo 代理）**：
| 目标 | 可达性 | 替代方案 |
|:-----|:------:|:---------|
| npm registry | ✅ 200 | npm install 可用 |
| PyPI | ✅ 200 | pip install 可用 |
| GitHub | ❌ 超时 | 用 pip 替代 install.sh |
| Docker Hub | ❌ 超时 | 配 registry mirrors |

---

## 十、相关参考

- `references/multi-agent-sandbox-example.md` — 本 skill 实战记录：Docker 配置 + 三容器搭建全过程
