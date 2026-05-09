---
name: file-system-manager
description: Hermes Agent 文件系统自主管理——归档、清理、整理、健康监控
version: 2.0.0
triggers:
  - 文件管理
  - 清理
  - 归档
  - 磁盘
  - 整理
  - 文件系统
  - 磁盘空间
  - 缓存
  - 磁盘清理
  - 文件整理
  - disk
  - clean
  - organize
  - archive
  - storage
  - space
  - cache cleanup
  - disk-cleanup
depends_on:
  - delete-safety
  - linux-ops-guide
design_pattern: Library-Reference
skill_type: Workflow
---

# 📁 Hermes 文件系统自主管理 v2.0

> **核心理念**：分层自动管理——即时清理 + 每日/每周/每月维护，让文件系统保持整洁高效！

## 一、系统现状（当前环境）

| 项目 | 数值 |
|------|:----:|
| 磁盘容量 | 50GB |
| 已使用 | 34GB (72%) |
| cache 总占用 | ~7.5GB |
| state.db | 207MB |
| sessions | 178MB |
| 旧版本备份 | 452MB |

## 二、已启用的自动机制

### ✅ disk-cleanup 插件（v2.0.0 — 已启用）
自动追踪 `write_file`/`terminal`/`patch` 创建的临时文件，会话结束时自动清理。

**清理规则**：

| 分类 | 阈值 | 确认方式 |
|------|:----:|:--------:|
| test 文件 | 每次会话结束 | 自动 |
| temp 文件 | >7天 | 自动 |
| cron-output | >14天 | 自动 |
| 空目录 | 总是 | 自动 |
| research | >30天（保留最新10个） | deep模式确认 |
| >500MB 文件 | 永不自动 | deep模式确认 |

**Slash 命令**：
- `/disk-cleanup status` — 查看状态
- `/disk-cleanup quick` — 快速清理
- `/disk-cleanup deep` — 深度清理
- `/disk-cleanup dry-run` — 预览

### ✅ Sessions 管理

**手动**：`hermes sessions prune --older-than 30 --yes`（清理30天前的会话）

**自动（可选配置）**：
```yaml
# ~/.hermes/config.yaml
sessions:
  auto_prune: true
  retention_days: 30
  vacuum_after_prune: true
  min_interval_hours: 24
```

## 三、安全缓存清理（一键脚本）

使用 `scripts/cache-cleanup.sh` 安全清理构建工具缓存：

```bash
# 预览模式（不删除）
python3 ~/.hermes/skills/file-system-manager/scripts/cache-cleanup.py --dry-run

# 执行清理
python3 ~/.hermes/skills/file-system-manager/scripts/cache-cleanup.py --apply
```

**可安全清理的缓存**：
| 缓存 | 典型大小 | 命令 |
|------|:--------:|------|
| pip cache | ~3.2GB | `pip cache purge` |
| npm cache | ~1.5GB | `npm cache clean --force` |
| uv cache | ~817MB | `uv cache clean` |
| APT cache | 安全 | `sudo apt clean` |
| Journal logs | 可回收 | `sudo journalctl --vacuum-time=7d` |

## 四、文件整理（organize）

使用 `scripts/file-organize.py` 整理 `~/.hermes/` 根目录散乱文件：

```bash
# 预览
python3 ~/.hermes/skills/file-system-manager/scripts/file-organize.py --dry-run

# 执行
python3 ~/.hermes/skills/file-system-manager/scripts/file-organize.py --apply
```

**文件分类规则**：
| 扩展名 | 目标目录 |
|--------|----------|
| .pdf, .docx, .pptx, .xlsx | output/documents/ |
| .png, .jpg, .jpeg, .gif, .svg | output/images/ |
| .html, .htm | output/html/ |
| .py, .sh | scripts/ |
| 版本标记文件（_v, _backup） | archive/ |

## 五、健康检查

使用 `scripts/file-health-check.py` 检查文件系统健康状态：

```bash
python3 ~/.hermes/skills/file-system-manager/scripts/file-health-check.py
```

**检查项**：
- 根目录散乱文件
- 缺失的必备目录
- 缺失的重要文件
- output 目录结构
- 文件数量/总大小统计

## 六、旧版本清理

确认当前 Hermes 版本运行正常后可以安全删除：

```bash
# 检查当前版本
hermes --version

# 确认后删除旧版本
rm -rf ~/.hermes/hermes-agent_old_v0.10.0
```

**⚠️ 前提**：确保新版 hermes 已稳定运行至少 1 天，功能正常。

## 七、自动定时清理（建议 cron）

```bash
# 每日 3:00 — disk-cleanup quick
cronjob create --name "daily-disk-cleanup" --schedule "0 3 * * *" \
  --prompt "运行 /disk-cleanup quick 进行安全清理"

# 每周日 3:00 — session prune
cronjob create --name "weekly-session-prune" --schedule "0 3 * * 0" \
  --prompt "运行 hermes sessions prune --older-than 30 --yes"

# 每月 1 日 3:00 — 缓存清理
cronjob create --name "monthly-cache-cleanup" --schedule "0 3 1 * *" \
  --prompt "运行 python3 ~/.hermes/skills/file-system-manager/scripts/cache-cleanup.py --apply"
```

## 八、绝对安全规则

### 🚫 永远不自动清理
- `sessions/` 中活跃会话文件
- `state.db`（只 prune 不删除）
- `logs/` 下 7 天内的日志
- `sessions/` 下最近 7 天的会话记录

### 🛡️ 清理前必须确认
- `hermes-agent_old_v0.10.0/`：确认新版正常
- `state-snapshots/`：保留最近 3 个
- `~/.cache/camoufox/`：浏览器配置，重建成本高

### 📍 路径安全
- 只清理 `$HERMES_HOME` 和 `/tmp/hermes-*`
- 拒绝对外部路径的操作
- 所有脚本都有 `dry-run` 模式
