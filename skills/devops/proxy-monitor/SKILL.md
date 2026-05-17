---
name: proxy-monitor
description: 代理节点健康监控与工业级部署流水线。涵盖活性/依赖性检查、熔断策略、安全部署（Secrets 扫描/原子同步/回滚）。
version: 2.0.0
triggers:
- 代理
- mihomo
- 监控
- deploy
- 部署
metadata:
  hermes:
    tags:
    - proxy
    - monitoring
    - deployment
    - github
    - circuit-breaker
    category: devops
    skill_type: operational
    design_pattern: tool_wrapper
depends_on: []

---
# 代理监控与部署技能 📡🚀

> **核心理念**：监控不仅仅是“通不通”，而是“好不好”。部署不仅仅是“传上去”，而是“安全且可回滚”。

## 一、工具清单

| 脚本 | 路径 | 功能 |
|:---|:---|:---|
| 代理监控 | `~/.hermes/scripts/proxy-monitor.sh` | 活性检查 + 依赖性测试 + 延迟测量 + 熔断建议 |
| 部署 v2 | `~/.hermes/scripts/deploy-v2.sh` | Secrets 扫描 + 增量同步 + Git 原子提交 + 推送验证 |
| 健康检查 | `~/.hermes/scripts/health-check.sh` | 系统全量健康检查（日志/告警/进程/端口/Provider） |

## 二、代理监控 (Proxy Monitoring)

### 运行方式
```bash
bash ~/.hermes/scripts/proxy-monitor.sh
```

### 监控维度
1. **活性检查 (Liveness)**：mihomo 进程是否在运行？端口 7890/9090 是否在监听？
2. **依赖性检查 (Dependency)**：关键域名（GitHub, Google）是否可达？HTTP 状态码是否为 200？
3. **延迟测量 (Latency)**：连接时间是否 > 1s？（高延迟会导致 Agent 响应变慢）
4. **配置健康 (Config)**：节点数量是否 > 0？是否存在规则冲突？

### 熔断策略 (Circuit Breaker)
如果某代理节点连续 3 次请求失败或延迟 > 2s：
- **标记为 DOWN**：在后续 10 分钟内不再尝试使用该节点。
- **切换备用路由**：尝试直连（如果是国内域名）或切换到备用代理端口。

### 已知问题
- 当前 mihomo 配置节点数为 0，但代理仍可用（可能通过订阅动态注入）。
- Google 返回 302 重定向属于正常现象（需处理登录跳转）。

## 三、部署流水线 (Deployment Pipeline)

### 运行方式
```bash
# 正常部署
bash ~/.hermes/scripts/deploy-v2.sh

# 预演（不同步，只检查）
bash ~/.hermes/scripts/deploy-v2.sh --dry-run

# 强制部署（跳过安全检查）
bash ~/.hermes/scripts/deploy-v2.sh --force
```

### 6 阶段流水线
```
Phase 1: 预检     → 目录/git/rsync/代理检查
Phase 2: 安全     → Secrets 扫描 (18种敏感文件) + .gitignore 自动修复
Phase 3: 同步     → 增量同步 (config/scripts/skills)
Phase 4: Git      → 自动 commit（带变更文件列表）
Phase 5: 推送     → 通过代理推送至 GitHub (main/master 自动回退)
Phase 6: 统计     → 文件数/大小/提交历史
```

### 安全检查清单 (Security Scan)
在推送前，脚本会自动扫描并拦截以下文件：
- 🔴 **凭证**：`.env`, `*.key`, `*.pem`, `*password*`, `*token*`
- 🔴 **运行时**：`state.db`, `sessions/`, `logs/`, `*.log`, `cache/`
- 🔴 **系统**：`.bundled_manifest`, `node_modules/`

### 环境变量
```bash
export HERMES_REPO_URL='https://<token>@github.com/<user>/<repo>.git'
```

## 四、最佳实践

1. **定期健康检查**：每 30 分钟运行一次 `proxy-monitor.sh`。
2. **金丝雀部署**：在 `deploy-v2.sh` 中，先推送一个小文件验证连通性，再推送全量。
3. **日志轮转**：确保监控脚本自身的日志也进行轮转，避免占满磁盘。
4. **Secrets 绝不提交**：即使使用 `.gitignore`，也要在 `pre-commit` 钩子中再次扫描。
