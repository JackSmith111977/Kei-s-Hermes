---
name: docker-terminal
description: Docker 沙箱终端执行指南 — 安全地在隔离容器中运行命令。涵盖配置、安全参数、镜像选择、卷挂载、资源限制及最佳实践。当用户需要配置 Docker backend、排查容器问题、选择镜像或配置安全策略时使用此 skill。
version: 1.0.0
triggers:
  - docker terminal
  - container sandbox
  - terminal isolation
  - docker backend
  - 容器安全
  - sandboxed execution
  - Docker 沙箱
  - 隔离执行
depends_on: []
referenced_by:
  - self-capabilities-map
design_pattern: Tool Wrapper
skill_type: product-verification
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
