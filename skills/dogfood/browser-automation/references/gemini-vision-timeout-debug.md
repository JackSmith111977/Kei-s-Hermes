# GeminiNativeClient Vision Timeout 调试记录

> 场景：browser_vision 在中国服务器通过 mihomo 代理调用 Gemini Flash 分析截图时挂死 8+ 分钟

## 时间线

| 时间 | 事件 |
|:---|:---|
| T+0 | `browser_vision(question)` 被调用，先截图（agent-browser CLI 本地执行） |
| T+2min | 截图成功，`call_llm(timeout=120)` 调用 Gemini API |
| T+2~10min | **完全静默**——无异常、无超时、无返回 |
| T+10min | 用户手动打断（`/new` 重置会话） |

## 根因链

### 核心缺陷：GeminiNativeClient 默认 read timeout = 600s

文件：`agent/gemini_native_adapter.py:833-835`

```python
self._http = http_client or httpx.Client(
    timeout=httpx.Timeout(connect=15.0, read=600.0, write=30.0, pool=30.0)
)
```

- `read=600.0` = **10 分钟**读取超时
- `browser_vision` 传入的 `timeout=120` 通过 `call_llm()` → `kwargs["timeout"]` → `client.chat.completions.create(**kwargs)` 传递到 `_create_chat_completion(timeout=120)` → `self._http.post(url, timeout=120)`
- 理论上 httpx 的 per-request timeout 应覆盖 client 默认值，**但实践中可能未正确生效**（可能是 httpx proxy transport 的特殊行为）

### 环境叠加因素

```
🇨🇳 中国服务器
  → http_proxy=http://127.0.0.1:7890 (mihomo)
    → 代理节点 → Google Gemini API (generativelanguage.googleapis.com)
      → GFW 干扰导致连接缓慢/重置
```

- `generativelanguage.googleapis.com` 在国内可能被限速或阻断
- mihomo 代理通过代理节点转发，如果节点质量差，可能长时间无响应
- httpx 通过代理时，timeout 行为可能与非代理场景不同

## 日志关键行

```log
# Vision 调用开始（之后 8 分钟无任何日志）
2026-05-08 20:38:32,221 INFO agent.auxiliary_client:
  Auxiliary vision: using gemini (gemini-3-flash-preview)
  at https://generativelanguage.googleapis.com/v1beta

# 用户打断后，session_search fallback 也失败
2026-05-08 20:55:47,485 INFO agent.auxiliary_client:
  Auxiliary session_search: connection error on auto
  — falling back to openrouter (google/gemini-3-flash-preview)
2026-05-08 20:59:04,433 WARNING root:
  Session summarization failed after 3 attempts:
  Error code: 403 - This model is not available in your region.
```

注意：`openrouter` 的 fallback 最终也返回 403（Gemini 模型在所在区域不可用）。

## Config 确认

```yaml
auxiliary:
  vision:
    api_key: ''
    base_url: ''
    download_timeout: 30
    model: gemini-3-flash-preview
    provider: google   # ← 关键：使用 google provider 触发 GeminiNativeClient
    timeout: 120       # ← 此超时可能未被 GeminiNativeClient 正确覆盖
```

## 修复方向

### A. 降低 GeminiNativeClient 默认 read timeout（立即生效）

```python
# gemini_native_adapter.py:834
timeout=httpx.Timeout(connect=15.0, read=120.0, write=30.0, pool=30.0)
```

### B. 切换 vision provider 为国内可达的

```yaml
auxiliary:
  vision:
    provider: custom  # 或 auto（但 auto 可能 fallback 到 google）
    model: longcat-vision  # 或其他国内 vision 模型
```

### C. browser_vision 外层加超时兜底

在 `browser_tool.py` 的 `browser_vision()` 中，用 `asyncio.wait_for()` 或 `concurrent.futures` 包装 `call_llm()` 调用，超时后降级返回截图路径。

### D. 优先使用国内可达的 vision provider

从记忆看，`custom_longCat`（LongCat-2.0-Preview）在国内可用且支持 vision。

## 相关代码文件

- `tools/browser_tool.py` — `browser_vision()` 函数（line 2731）
  - 调用链：截图 → `call_llm(timeout=120)` → Gemini API
- `agent/gemini_native_adapter.py` — `GeminiNativeClient` 类（line 805）
  - `__init__` 默认 `read=600.0`（line 834）
  - `_create_chat_completion` 接收 timeout 参数（line 880）
  - HTTP 调用：`self._http.post(url, timeout=timeout)`（line 902）
- `agent/auxiliary_client.py` — `call_llm()`（line 3468）
  - `_build_call_kwargs()` 包含 timeout（line 3372）
