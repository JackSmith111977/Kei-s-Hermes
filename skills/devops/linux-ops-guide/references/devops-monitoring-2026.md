# DevOps 监控模式参考（2026）

> 创建时间：2026-05-17
> 来源：Grafana 2026 报告、SolarWinds 2026 报告、OneUptime 指南、Stackpick 评测等 10+ 来源
> 适用于：Hermes Agent 服务器运维监控体系建设

## 一、核心监控架构

### 推荐栈（自托管，免费）
```
主机（Hermes 服务器）
├── Node Exporter (端口 9100)     ← 采集系统指标
├── Prometheus (端口 9090)         ← 存储+查询
├── Grafana (端口 3000)            ← 可视化
├── cAdvisor (端口 8080)           ← 容器指标（如有 Docker）
└── Alertmanager (端口 9093)       ← 告警路由
```

### 快速部署参考
```bash
# Prometheus 配置文件 (prometheus.yml)
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']  # Docker Engine metrics

# Grafana systemd 服务
sudo systemctl enable --now grafana-server
# Grafana Web: http://server:3000 (默认 admin/admin)
# 添加 Prometheus 数据源: http://localhost:9090
# 导入仪表盘: ID 1860 (Node Exporter Full)
```

## 二、进程管理选型（2026）

| 方案 | 内存 | 冷启动 | 崩溃恢复 | 适用场景 |
|------|------|--------|---------|---------|
| **systemd** | ~0 MB | 78ms | 182ms | Linux 原生，零开销，Hermes 就用它 |
| Oxmgr | 4.2 MB | 38ms | 11ms | 新项目首选，Rust 写，2026 年新秀 |
| PM2 | 83 MB | 1247ms | 412ms | Node.js 生态 |
| Supervisor | 31 MB | 640ms | 530ms | Python/遗留环境，维护模式 |

### systemd Watchdog（适合 AI Agent 心跳）
```ini
[Service]
Type=notify
WatchdogSec=120s
Restart=on-failure
RestartSec=5s
```
Agent 需每 120s 内发送 `WATCHDOG=1` keepalive，超时自动重启。

## 三、Cron 作业监控（死信开关模式）

### 最佳实践
```bash
# 在脚本末尾添加（而非开头！）
/usr/local/bin/my-backup.sh \
  && curl -fsS -m 10 --retry 5 https://hc-ping.com/your-uuid
# 只在成功后 ping，失败不 ping → 服务检测到超时告警
```

### 关键原则
1. **成功后 ping**，防半途崩溃
2. 设置合理**宽限期**（基于实际运行时长的 1.5-2 倍）
3. `flock`/锁定文件**防止重叠运行**
4. 使用 **UTC 时区** 调度
5. 连续失败 **2-3 次**才告警
6. 监控整个管线的**最终步骤**而非开始

### 推荐工具
- **Healthchecks.io** — 专注 Cron 监控，开源可自托管，免费 20 个检测
- **Uptime Kuma** — 自托管免费，支持 Push 监控
- **Cronitor** — Cron + Uptime 整合，CLI 工具

## 四、分布式追踪（OpenTelemetry）

### 架构
```
Service SDK → OTel Collector (localhost:4317) → 后端 (Jaeger/Tempo)
```

### 关键配置
```yaml
# OTel Collector 尾采样配置
tail_sampling:
  policies:
    - type: status_code
      status_code: { status_codes: [ERROR] }
    - type: latency
      latency: { threshold_ms: 500 }
    - type: probabilistic
      sampling: { sampling_percentage: 10 }
```

### 实施步骤
1. 部署 OTel Collector 作为 DaemonSet 或 sidecar
2. 添加 OTel SDK 自动插装（HTTP/gRPC/DB）
3. 尾采样：100% 错误 + 100% 慢查询 + 10% 随机
4. W3C Trace Context 传播标准 (traceparent/tracestate)
5. 注入 trace ID 到日志管线，实现 metrics → traces → logs 关联

## 五、2026 观测性趋势关键数据

| 趋势 | 数据 |
|------|------|
| 统一观测性采用率 | 73% 已采用/转型 |
| 77% 认为工具整合重要 | 仅 14% 成功 |
| AI 观测性信任度 | 90% 信任 AI 改善观测 |
| OpenTelemetry 采用 | 76% 投资 |
| 观测性支出增长 | 62% 预计增加 |
| 工具平均数量 | 7 个/组织 |
| 混合环境可见性缺口 | 77% 缺乏全栈可见性 |
| AI 自动告警优先级 | 47% 已在使用 |

## 六、常见问题排查

```bash
# Prometheus targets 状态
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool

# Node Exporter 指标检查
curl -s http://localhost:9100/metrics | head

# 系统级问题：JMeter-like 检查
ss -tlnp | grep -E '9090|9100|3000|9093'
systemctl status prometheus grafana-server
journalctl -u prometheus -n 20 -p err
```
