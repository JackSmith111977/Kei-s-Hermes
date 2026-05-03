---
name: smart-broadcast
description: "Hermes 智能播报引擎 v2.0 管理指南。涵盖状态检查、数据源配置、静默管理、故障排查及扩展开发。"
version: 1.0.0
triggers:
  - 播报
  - 广播
  - 通知
  - 播报状态
  - 智能播报
  - 广播配置
  - 添加播报源
  - 广播测试
depends_on: []
design_pattern: Tool Wrapper
skill_type: Tool Wrapper
---

# 📢 Smart Broadcast · 智能播报引擎 v2.0 管理指南

> **核心理念**：事件驱动 + 增量过滤 + 哈希去重。只有在有新增高价值信息时才打扰主人。
> **核心脚本**：`~/.hermes/scripts/broadcast/smart_broadcast.py`
> **状态文件**：`~/.hermes/state/broadcast_state.json`
> **Cron 任务 ID**：`fed8e1444a92` (每 2 小时轮询)

## 🛠️ 核心操作指令

### 1. 状态检查 (Status Check)
当主人问"播报状态"或"最近报了什么"时：
1. **运行脚本**：`python3 ~/.hermes/scripts/broadcast/smart_broadcast.py --dry-run`
2. **查看状态文件**：读取 `~/.hermes/state/broadcast_state.json`
   - `last_run_at`: 上次播报时间。
   - `silence_until`: 当前是否在静默期（动态免打扰）。
   - `stats`: 统计发送次数和跳过次数。

### 2. 强制播报 (Force Broadcast)
当主人要求"现在播报一次"或"测试播报"时：
1. **运行脚本**：`python3 ~/.hermes/scripts/broadcast/smart_broadcast.py --force`
2. **捕获输出**：如果脚本输出包含 `BROADCAST_PAYLOAD_START` 和 `BROADCAST_PAYLOAD_END`，提取中间内容发送给用户。
3. **注意**：强制播报会重置静默计时器。

### 3. 管理静默期 (Manage Silence)
- **临时解除**：运行 `--force` 会自动发送并进入新的静默期。
- **手动修改**：编辑 `broadcast_state.json`，将 `silence_until` 改为过去的时间即可立即恢复播报。

## 🧩 扩展数据源与功能模块 (Functional Modules)

脚本 v3.0 内置了四大核心功能模块。主人可以根据需要开启或定制：

### 1. 系统监控 (System Stats) - **默认开启**
*   **数据源**: Shell 命令 (`uptime`, `free`, `df`)。
*   **内容**: 1分钟负载、内存使用率、磁盘空间。
*   **报警**: 当 内存>80% 或 磁盘>85% 时，自动标记为 `WARN` 或 `CRITICAL`，并在播报中高亮显示。

### 2. 任务队列 (Tasks) - **默认开启**
*   **数据源**: `~/.hermes/TASK_QUEUE.md`。
*   **内容**: 统计 `IN_PROGRESS` 和 `PENDING` 的任务数量。
*   **作用**: 提醒主人当前有哪些工作正在进行，或有多少待办堆积。

### 3. 天气提醒 (Weather) - **晨报时段开启 (08:00-10:00)**
*   **数据源**: **Open-Meteo API** (真实数据，免费，无需 Key)。
*   **坐标配置**: 默认北京 (39.9, 116.4)。若要修改，请在脚本中更改 `lat, lon` 变量。
*   **内容**: 实时温度、天气状况（支持 WMO 代码解析）、出行建议。
*   **容灾**: 带有缓存机制，API 失败时自动读取缓存，播报永不中断。

### 4. 日程提醒 (Calendar) - **晨报时段开启**
*   **数据源**: `~/.hermes/config/calendar.json`。
*   **内容**: 读取今日前两个日程。
*   **格式**:
    ```json
    {
      "events": [
        {"title": "周会", "time": "10:00"},
        {"title": "提交报告", "time": "14:00"}
      ]
    }
    ```

## 🚩 常见问题 (Troubleshooting)

- **脚本执行报错**：检查 Python 路径，确保使用 `python3`。
- **播报不发送**：
  1. 检查 Cron 任务 `fed8e1444a92` 是否处于 `paused` 状态。
  2. 检查 `broadcast_state.json` 中的 `silence_until` 是否在未来。
  3. 检查内容是否被 Hash 去重拦截（内容没变化）。
- **内容重复**：如果主人抱怨"怎么总是报一样的"，说明 `collect_data` 里的过滤逻辑没写好，需要增加 `last_seen_id` 等去重机制。
