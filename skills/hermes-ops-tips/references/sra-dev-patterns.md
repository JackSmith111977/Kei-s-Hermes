# SRA Daemon 开发模式

> SRA v1.2.1+ 开发最佳实践 — 端点模式、导入陷阱、测试策略

---

## 1. 端点添加三件套

每次添加新端点必须改 **三处**（两个 dispatcher + CLI）：

```
daemon.py ──┬── do_POST()          # HTTP POST 端点
            └── _handle_request()  # Socket action
cli.py ──────── COMMANDS 字典      # CLI 命令
```

### 1.1 HTTP 端点 (do_POST)

```python
# skill_advisor/runtime/daemon.py
class SRAHTTPHandler:
    def do_POST(self):
        ...
        elif self.path == "/recheck":
            summary = data.get("conversation_summary", "")
            if not summary:
                self._send_json({"error": "missing conversation_summary"}, 400)
                return
            loaded_skills = data.get("loaded_skills", [])
            result = self.daemon.advisor.recheck(summary, loaded_skills)
            self._send_json({"status": "ok", "recheck": result})
```

### 1.2 Socket action (_handle_request)

同一个 `daemon.py`，另一个 dispatch 点：

```python
def _handle_request(self, request: dict) -> dict:
    action = request.get("action", "")
    params = request.get("params", {})
    ...
    elif action == "recheck":
        summary = params.get("conversation_summary", "")
        if not summary:
            return {"error": "missing conversation_summary"}
        loaded_skills = params.get("loaded_skills", [])
        result = self.advisor.recheck(summary, loaded_skills)
        return {"status": "ok", "recheck": result}
```

⚠️ **常见漏改**：HTTP 端点和 Socket 端点必须**同步**添加，遗漏任何一个会导致对应的调用方式失败。

### 1.3 CLI 命令 (cli.py + COMMANDS)

```python
# skill_advisor/cli.py
def cmd_recheck(args: List[str]):
    ...

COMMANDS = {
    ...
    "recheck": cmd_recheck,
}

# 帮助文本也要加
```

---

## 2. 四层文件变更链

完整的功能从底层到顶层依次修改：

```
memory.py      → 数据层（新增存储方法）
advisor.py     → 业务层（透传/封装方法）
daemon.py      → API 层（HTTP + Socket 端点）
cli.py         → CLI 层（命令行接口）
```

**Sprint 2 实模式板**：

| 文件 | 作用 | SRA-003-03 | SRA-003-04 |
|:-----|:-----|:-----------|:-----------|
| `memory.py` | 数据持久化 | `record_view/use/skip` + `compliance_stats` | — |
| `advisor.py` | 业务逻辑 | 透传方法 | `recheck()` 方法 |
| `daemon.py` | API 端点 | 扩展 `/record` + `/stats/compliance` | `POST /recheck` |
| `cli.py` | 命令行 | `sra compliance` | — |

---

## 3. ⚠️ 导入陷阱：相对路径与包结构

### 3.1 问题

`skill_advisor/runtime/daemon.py` 中有延迟导入：

```python
# ❌ 错误（实际代码有 bug！）
from ..endpoints.validate import handle_validate
# 解析为：skill_advisor.endpoints.validate  ← 不存在！
```

### 3.2 修正

```python
# ✅ 正确
from .endpoints.validate import handle_validate
# 解析为：skill_advisor.runtime.endpoints.validate  ← 存在！
```

`..` 从 `skill_advisor.runtime.daemon` 上溯到 `skill_advisor` 包。
`.` 保持在 `skill_advisor.runtime` 包内。

### 3.3 根因

`skill_advisor/runtime/` 和 `skill_advisor/runtime/endpoints/` **没有 `__init__.py`**，依赖 Python 3.3+ 的 namespace package 机制。这本身没问题，但相对导入行为不变——`..` 仍然上溯一级。

### 3.4 如何自检

```bash
# 测试 validate 端点是否可用
cd ~/projects/sra
python3 -c "
import sys, os, tempfile; tmp=tempfile.mkdtemp()
sys.path.insert(0, '.')
from skill_advisor.runtime.daemon import SRaDDaemon
d = SRaDDaemon({'skills_dir':tmp,'data_dir':tmp,'enable_http':False,'enable_unix_socket':False})
r = d._handle_request({'action':'validate','params':{'tool':'write_file','args':{'path':'test.md'}}})
print(r['status'])
"
# 输出应为: ok
# 输出 ModuleNotFoundError → 导入路径有问题
```

---

## 4. 数据向后兼容模式

`memory.py` 的 JSON 持久化文件需要向前兼容旧数据：

### 4.1 默认值工厂

```python
def _default_compliance(self) -> Dict:
    """新字段默认值"""
    return {
        "total_views": 0,
        "total_uses": 0,
        "total_skips": 0,
        "overall_compliance_rate": 1.0,
        "recent_events": [],
    }
```

### 4.2 load() 中补全

```python
def load(self) -> Dict:
    ...
    try:
        with open(self.stats_file) as f:
            data = json.load(f)
        # 向前兼容：旧数据缺少 compliance 字段
        if "compliance" not in data:
            data["compliance"] = self._default_compliance()
        self._cache = data
    except (FileNotFoundError, json.JSONDecodeError):
        self._cache = self._default_stats()
    return self._cache
```

### 4.3 技能条目安全初始化

```python
def _ensure_skill_entry(self, stats: Dict, skill_name: str):
    """确保所有字段存在（新旧 API 兼容）"""
    if skill_name not in stats["skills"]:
        stats["skills"][skill_name] = {
            "total_uses": 0,
            "last_used": None,
            "trigger_phrases": [],
            "accepted_count": 0,
            "acceptance_rate": 1.0,
            "view_count": 0,       # 新增
            "use_count": 0,        # 新增
            "skip_count": 0,       # 新增
            "last_viewed": None,   # 新增
        }
```

---

## 5. 测试策略

### 5.1 测试文件结构

```
tests/
├── test_memory.py     # SceneMemory 单元测试（27 个）
├── test_daemon.py     # SRaDDaemon 核心测试（22 个）
├── test_cli.py        # CLI 命令测试（22 个）
├── test_daemon_http.py# HTTP 服务器集成测试（已有）
└── ...                # 其他测试
```

### 5.2 关键测试技术

| 场景 | 方法 | 示例 |
|:-----|:-----|:-----|
| 文件隔离 | `tmp_path` + `tempfile.mkdtemp()` | `SceneMemory(tmpdir)` 自动创建分离文件 |
| 避免真启动 | `monkeypatch.setattr(daemon, "_run_socket_server", lambda: None)` | 阻止 Socket/HTTP 线程启动 |
| CLI mock | `@patch("skill_advisor.cli._socket_request")` | 模拟 daemon 响应 |
| 旧数据兼容 | 手动写 JSON 文件再调 `load()` | 验证 `compliance` 自动补全 |

### 5.3 测试清单

`test_memory.py` 覆盖：
- ✅ 空目录/损坏文件 → 默认值
- ✅ record_view/use/skip 计数
- ✅ 遵循率计算（纯使用、混合、无数据）
- ✅ per_skill 维度统计
- ✅ 旧 API `record_usage()` 向后兼容
- ✅ 最近事件列表（200 条上限）
- ✅ 场景模式创建/命中
- ✅ 触发短语记录（20 条上限）

`test_daemon.py` 覆盖：
- ✅ 自定义/默认配置初始化
- ✅ 启动前/启动后统计状态
- ✅ 全部 12 个 socket action（ping/recommend/refresh/stats/record 三种/coverage/stats/compliance/validate/recheck/stop）
- ✅ 空查询/未知 action 错误处理

`test_cli.py` 覆盖：
- ✅ 所有命令（recommend/stats/coverage/compliance/refresh/record/config/version）
- ✅ daemon 运行模式 vs 本地模式回退
- ✅ 无效参数错误提示
- ✅ 命令注册表完整性校验
