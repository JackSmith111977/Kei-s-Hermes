# 文件系统规范执行实施笔记

> 2026-05-17 | 继承自 `docs/plans/fs-enforcement-implementation-plan.md`

## 架构决策

### 为什么用 Shell Hooks + Python Plugin 双通道

| 通道 | 优势 | 场景 |
|:-----|:------|:------|
| Shell Hooks (L1) | 零代码，配置即生效 | 审计日志记录，pre_tool_call 轻度拦截 |
| Python Plugin (L2) | 完整 Python 能力，可注册命令 | 复杂检查逻辑，/fs-enforce 诊断命令 |

**同时使用的原因**：L1 不需要 Hermes 重启就能生效（Shell Hooks 是配置驱动的），L2 需要 `plugins.enabled` 配置 + 重启。两者同时运作，L1 兜底保证即使插件加载失败也有审计记录。

### 插件钩子系统关键发现

Hermes 的 `VALID_HOOKS` 定义在 `hermes_cli/plugins.py:78-114`，共 14 个钩子：

```python
VALID_HOOKS = {
    "pre_tool_call",           # 工具调用前（可 block）
    "post_tool_call",          # 工具调用后（审计）
    "transform_terminal_output", # terminal 输出转换
    "transform_tool_result",   # 工具结果转换
    "pre_llm_call", "post_llm_call",  # LLM 调用前后
    "pre_api_request", "post_api_request",  # API 请求前后
    "on_session_start", "on_session_end", "on_session_finalize", "on_session_reset",  # 会话生命周期
    "subagent_stop",           # 子代理停止
    "pre_gateway_dispatch",    # 网关调度前
    "pre_approval_request", "post_approval_response",  # 审批生命周期
}
```

**文件操作相关的钩子**：`pre_tool_call`、`post_tool_call`、`on_session_end`

### 关键坑点

1. **Plugin 在 __init__.py 的 register() 中注册钩子**，不是在 plugin.yaml 中声明（yaml 只是清单）
2. **Shell Hooks 的 matcher 只对 pre/post_tool_call 生效**，对其他钩子类型会被忽略
3. **pre_tool_call 的 block 返回值必须精确匹配**：`{"action": "block", "message": "..."}`
4. **post_tool_call 不能 block**，只能记录和警告
5. **Plugin 回调内部的异常不会传播到主循环**（每个回调有独立的 try/except）
6. **Python Plugin 不支持热加载**，修改后需重启 Hermes

### 审计日志格式

JSON Lines 格式（每行一个 JSON 对象），追加写入：

```json
{"ts": "2026-05-17T13:42:03Z", "tool": "write_file", "path": "~/.hermes/test.txt", "verdict": "BLOCKED", "reason": "naming:禁止的文件名", "session": "test_3"}
```

verdict 取值：
- `PASS` — 合规通过
- `BLOCKED` — 被拦截（pre_tool_call 阻断）
- `WARN` — 合规警告（post_tool_call 发现不合规但未拦截）

### 检查引擎架构

```
enforcer.py
├── check_write_path()      # 入口：保护路径 → 命名 → 目录归属
├── _check_protected()      # 保护路径（AGENTS.md, SOUL.md, config.yaml, state.db）
├── _check_naming()         # 命名（禁止名/字符/空格/大小写）
├── _check_scope()          # 目录归属（scripts/只放.py, skills/只放.md 等）
├── audit_log()             # 写入审计日志
├── get_stats()             # 统计审计数据
├── handle_command()        # /fs-enforce 子命令
├── _cmd_status()           # status
├── _cmd_stats()            # stats
├── _cmd_log()              # log N
└── _cmd_check()            # check <path>
```

### 实施状态

| 组件 | 文件 | 状态 |
|:-----|:-----|:------|
| 规范文档 | `standards/filesystem-规范.md` | ✅ |
| 规则配置 | `scripts/fs-enforce/rules.yaml` | ✅ |
| Shell Hook 脚本 | `scripts/fs-enforce/fs-audit.sh` (wrapper) + `fs-audit.py` | ✅ |
| Python Plugin | `plugins/fs-enforce/{__init__.py, enforcer.py, plugin.yaml}` | ✅ |
| cronjob | `daily-fs-audit` (每天 9:00) | ✅ |
| 健康报告 | `scripts/fs-enforce/fs-health.py` | ✅ |
| 实施计划 | `docs/plans/fs-enforcement-implementation-plan.md` | ✅ |

### 审计日志文件管理

- 位置: `~/.hermes/data/fs-audit/audit.log`
- 格式: JSON Lines
- 最大大小: 10MB（超过自动轮转，待实施）
- 保留期: 90 天
- 每日归档: 通过 cronjob 实现
