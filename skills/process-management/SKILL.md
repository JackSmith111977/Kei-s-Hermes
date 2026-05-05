---
name: process-management
description: "长任务监控与后台进程管理最佳实践。涵盖 terminal(background=true) 的 8 种操作模式、notify_on_complete 异步通知、watch_patterns 实时监控、以及与 cronjob/delegate_task/execute_code 的配合策略。当需要启动长时间运行的任务时使用此 skill。"
version: 1.0.0
triggers:
  - 长任务
  - 后台进程
  - process管理
  - 进程监控
  - 异步任务
  - 长时间运行
  - background task
  - process tool
  - notify_on_complete
  - watch_patterns
  - 部署监控
  - 训练监控
depends_on: []
referenced_by:
  - self-capabilities-map
design_pattern: Pipeline
skill_type: product-verification
---

# Process 管理最佳实践

> **用途**：启动和管理长时间运行的后台任务，实现异步监控和自动通知。
> **核心原则**：让 boku 能够 fire-and-forget，同时保持对关键事件的实时监控。

---

## 一、Process 工具 8 种操作

| 操作 | 用途 | 示例 |
|------|------|------|
| `list` | 查看所有后台进程 | 检查卡住的进程 |
| `poll` | 状态 + 新输出 | 定期查看进度 |
| `log` | 完整输出（分页） | 获取全部结果 |
| `wait` | 阻塞直到完成 | 等待测试完成 |
| `kill` | 终止进程 | 停止失控任务 |
| `write` | 发送原始 stdin | 向 REPL 输入 |
| `submit` | 发送数据 + Enter | 回答 yes/no |
| `close` | 关闭 stdin/EOF | 结束输入流 |

---

## 二、4 种参数组合模式

### 模式 1：Fire-and-Forget（完全异步）
```python
terminal(command="...", background=True, notify_on_complete=True)
# boku 继续做其他事情，完成后自动通知
```

### 模式 2：实时监控（错误检测）
```python
terminal(command="...", background=True, 
         watch_patterns=["ERROR", "Traceback", "FAILED"])
# 看到错误立即收到警告
```

### 模式 3：混合模式（监控 + 完成通知）
```python
terminal(command="...", background=True, notify_on_complete=True,
         watch_patterns=["listening on port", "ERROR"])
```

### 模式 4：交互式（PTY）
```python
terminal(command="python", background=True, pty=True)
# 使用 process(action="submit") 发送输入
```

---

## 三、5 种场景模板

### 模板 1：服务器部署
```python
terminal(command="docker-compose up -d --build", 
         background=True, notify_on_complete=True,
         watch_patterns=["ERROR", "unhealthy", "started"])
```

### 模板 2：数据处理
```python
terminal(command="python process_data.py --input large.csv",
         background=True, notify_on_complete=True,
         watch_patterns=["Error", "MemoryError", "processed 10000"])
```

### 模板 3：测试执行
```python
terminal(command="pytest -v tests/",
         background=True, notify_on_complete=True,
         watch_patterns=["FAILED", "ERROR", "passed"])
```

### 模板 4：模型训练
```python
terminal(command="python train.py --epochs 100",
         background=True, notify_on_complete=True,
         watch_patterns=["Epoch", "loss=", "val_loss", "early stopping"])
```

### 模板 5：爬虫/抓取
```python
terminal(command="python scraper.py --urls 1000",
         background=True, notify_on_complete=True,
         watch_patterns=["ERROR", "rate limit", "completed", "blocked"])
```

---

## 四、与其他工具配合

### cronjob + process
- 定时任务中启动后台进程
- 进程完成后自动交付结果到目标平台

### delegate_task + process
- 子代理有自己的终端会话
- 子代理可以管理自己的后台进程

### execute_code + process
- 沙箱中启动后台进程
- 通过 process 工具管理

---

## 五、最佳实践清单

### ✅ 应该做的
1. 使用 `notify_on_complete` — 避免轮询
2. 设置 `watch_patterns` — 实时监控关键事件
3. 区分用途 — 中途信号用 watch_patterns，结束用 notify_on_complete
4. 使用 Docker 隔离 — 未信任代码用 `TERMINAL_BACKEND=docker`
5. 定期 poll 检查进度 — 对长时间任务
6. 完成后用 log 获取完整输出

### ❌ 不应该做的
1. 不要用轮询代替 notify_on_complete
2. 不要用 watch_patterns 监控结束标记
3. 不要在消息平台用 verbose=all
4. 不要禁用命令审批（生产环境）
5. 不要在容器内运行危险命令（检查会跳过）

---

## 六、常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 进程卡住 | `process(action="submit")` 发送输入 |
| 没有收到通知 | 重新启动时设置 `notify_on_complete=True` |
| 输出太多 | 使用 `watch_patterns` 过滤 |
| 进程被杀 | 增加 `timeout` 参数 |
| 权限错误 | 设置 `SUDO_PASSWORD` 或使用 Docker |

---

**⚠️ Red Flags**：
- 启动长任务时**必须**设置 notify_on_complete 或 watch_patterns
- 不要同时用 watch_patterns 监控结束标记（会与 notify_on_complete 重复）
- 容器后端跳过危险命令检查，确保容器镜像已锁定
