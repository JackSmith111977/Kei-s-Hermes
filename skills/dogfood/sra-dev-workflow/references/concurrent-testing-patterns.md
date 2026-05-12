# 并发安全测试模式 — SRA SRA-003-16 实战记录

> 2026-05-12 | SRA-003-16 (并发安全 + 路由统一)

## 1. 多线程状态写入测试

验证 `_update_status()` 的 `self._lock` 保护是否有效：

```python
def test_concurrent_update_status(self, tmp_path):
    daemon = SRaDDaemon({"skills_dir": str(tmp_path), "data_dir": str(tmp_path)})
    errors = []

    def writer(status_val):
        try:
            for _ in range(20):
                daemon._update_status(f"status_{status_val}")
                time.sleep(0.001)
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()

    assert len(errors) == 0
    # 验证文件是合法完整 JSON
    with open(test_file) as f:
        data = json.load(f)
    assert "status" in data
```

## 2. 统计计数精确性测试

验证 `self._stats` 锁保护的并发正确性（轻量 daemon 不含真实 socket）：

```python
daemon = SRaDDaemon.__new__(SRaDDaemon)
daemon.config = {}
daemon._lock = threading.Lock()
daemon._stats = {"total_requests": 0, "total_recommendations": 0, ...}
daemon.force_manager = MagicMock()
daemon.advisor = MagicMock()
daemon.advisor.recommend.return_value = {"recommendations": []}
daemon.running = True
daemon.ROUTER = SRaDDaemon.ROUTER

# 5 线程 × 20 次 = 100 次请求
def make_request():
    for _ in range(20):
        daemon._handle_request({"action": "ping", "params": {}})
threads = [threading.Thread(target=make_request) for _ in range(5)]
...
assert daemon._stats["total_requests"] == 100
```

## 3. 跨进程文件锁测试 (fcntl.flock)

验证 `memory.py` 的 `fcntl.flock` 在多线程保存时不损坏文件：

```python
memory = SceneMemory(str(tmp_path))
memory._cache = {"skills": {}, ...}

def saver():
    for _ in range(10):
        memory._cache["total_recommendations"] += 1
        memory.save()  # 内部有 fcntl.flock(LOCK_EX)

threads = [threading.Thread(target=saver) for _ in range(3)]
...
# 验证文件合法 JSON
data = memory.load()
assert data["total_recommendations"] >= 0
```

## ⚠️ 陷阱: 模块级常量导入无法通过重新赋值打补丁

**现象**：在测试中 `cfg_module.STATUS_FILE = str(test_file)` 后，`daemon._update_status()` 仍写入原路径。

**根因**：`daemon.py` 使用 `from .config import STATUS_FILE` 在**模块导入时**绑定了 `STATUS_FILE` 的引用。修改 `config.STATUS_FILE` 不会影响 `daemon.STATUS_FILE`。

```python
# ❌ 不行：daemon.STATUS_FILE 仍指向旧值
from skill_advisor.runtime import config as cfg_module
cfg_module.STATUS_FILE = "/new/path"  # ❌ 不影响 daemon.py 的 STATUS_FILE

# ✅ 正确：直接打补丁到 daemon 模块
import skill_advisor.runtime.daemon as daemon_mod
daemon_mod.STATUS_FILE = "/new/path"  # ✅ 覆盖 daemon 模块中的引用
```

**黄金规则**：模块级常量导入 (`from X import Y`) 不可通过 reassign X.Y 打补丁。必须 reassign **引用该常量的模块** 的对应属性。

## 4. 路由统一验证测试

检查 ROUTER 完整性和 handler 签名一致性：

```python
def test_router_contains_all_actions(self):
    router = SRaDDaemon.ROUTER
    expected_actions = {
        "recommend", "record", "refresh", "stats", "ping",
        "coverage", "stats/compliance", "stop", "validate",
        "force", "recheck",
    }
    assert set(router.keys()) == expected_actions

def test_router_handler_signature(self):
    import inspect
    for action, handler_name in SRaDDaemon.ROUTER.items():
        handler = getattr(SRaDDaemon, handler_name)
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())
        assert "params" in params  # 所有 handler 接受 params dict
```

## 相关文件

- `tests/test_concurrency.py` — 完整并发测试实现（8 个测试）
- `skill_advisor/runtime/daemon.py` — `ROUTER` + `_handle_*` handler 实现
- `skill_advisor/memory.py` — `fcntl.flock` 跨进程文件锁
