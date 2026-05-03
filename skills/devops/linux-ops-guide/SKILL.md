---
name: linux-ops-guide
description: Hermes 服务器（Ubuntu）日常运维指南。涵盖 systemd 服务管理、日志分析、端口排查、磁盘监控、进程管理、快速排查流程。
version: 1.0.0
triggers:
- linux
- 运维
- systemd
- 命令
- ops
allowed-tools:
- terminal
- read_file
- search_files
metadata:
  hermes:
    tags:
    - linux
    - ops
    - systemd
    - monitoring
    - troubleshooting
    category: devops
    skill_type: library-reference
    design_pattern: tool-wrapper
---
# Linux 运维基础指南 🖥️

## Hermes 服务器概况

OS: Ubuntu, CPU: 1 core, RAM: 2GB (1.0GB available)
Disk: 50GB (22GB used, 55%)
Hermes: 以 systemd 服务运行

## 一、进程管理

```bash
ps aux                                    # 所有进程
ps aux | grep hermes | grep -v grep      # 找 Hermes
ps aux --sort=-%mem | head -10            # 内存大户 TOP10
ps aux --sort=-%cpu | head -10            # CPU 大户 TOP10
top                                       # 实时监控
htop                                      # 更好看的监控
kill PID                                  # 优雅终止
kill -9 PID                               # 强制杀死
pkill -f "pattern"                        # 按模式杀
nohup python3 script.py > log 2>&1 &      # 后台运行
```

## 二、systemd 服务

```bash
# 查看（不需要 sudo）
systemctl status hermes-agent
systemctl list-units --type=service
systemctl --failed
systemctl cat hermes-agent

# 管理（需要 sudo，用户有 sudo 免密权限）
sudo systemctl start/stop/restart hermes-agent
sudo systemctl enable/disable hermes-agent
```

## 三、日志分析

```bash
journalctl -u hermes-agent                # 全部日志
journalctl -u hermes-agent -n 50          # 最近 50 行
journalctl -u hermes-agent -f             # 实时跟踪
journalctl -u hermes-agent --since today  # 今天的
journalctl -u hermes-agent -p err         # 只看错误
journalctl -u hermes-agent | grep -i "error"
journalctl -u hermes-agent | grep "Traceback"
```

## 四、端口排查

```bash
ss -tlnp                                  # 所有 TCP 监听
ss -tlnp | grep :7890                     # 查特定端口
netstat -tlnp                             # 传统方式
lsof -i :7890                             # 谁在用端口
```

### 常用端口
```
7890  mihomo 代理     9090  mihomo API
9222  Chrome 调试     3456  CDP Proxy
```

## 五、磁盘监控

```bash
df -h /                                   # 磁盘空间
du -sh /* 2>/dev/null | sort -rh | head   # 大目录
find / -type f -size +100M 2>/dev/null    # 大文件
sudo apt clean                            # 清理 apt 缓存
sudo apt autoremove
sudo journalctl --vacuum-time=7d          # 清理 journal
```

## 六、内存监控

```bash
free -h
ps aux --sort=-%mem | head -5
dmesg | grep -i "out of memory"
```

## 七、快速排查流程

```bash
# 1. Hermes 活着吗？
systemctl status hermes-agent

# 2. 有错误吗？
journalctl -u hermes-agent -n 50 -p err

# 3. 磁盘满了？
df -h /

# 4. 内存够？
free -h

# 5. 代理活着？
curl -s --connect-timeout 3 http://127.0.0.1:7890/version 2>/dev/null || echo "代理无响应"

# 6. 关键端口？
ss -tlnp | grep -E '7890|9090|9222|3456'

# 7. 最近异常？
journalctl -u hermes-agent --since "1 hour ago" | grep -iE "error|fail|traceback"
```
