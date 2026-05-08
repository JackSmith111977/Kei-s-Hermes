# Gemini Vision 配置指南

## 概述
将 Hermes 的 `auxiliary.vision` 配置为使用 Google Gemini API 处理图片分析任务。

## 前提条件
- 在 `~/.hermes/.env` 中设置 `GOOGLE_API_KEY`（或 `GEMINI_API_KEY` 作为别名）
- 获取 API Key：https://aistudio.google.com/app/apikey

## 配置命令

```bash
# 设置 provider 为 Google Gemini
hermes config set auxiliary.vision.provider google

# 设置模型（选择下方任一模型 ID）
hermes config set auxiliary.vision.model gemini-3.1-pro-preview
```

## 可用模型列表（Gemini 3 系列，均支持 Vision）

| 模型 ID | 说明 | 价格 /1M tokens (输入/输出) | 适用场景 |
|---------|------|:--------------------------:|:--------:|
| `gemini-3.1-pro-preview` | 🏆 最强，1M上下文 | $2 / $12 | 最详细分析、复杂推理 |
| `gemini-3-flash-preview` | ⚡ 性价比之王，视觉推理强 | $0.50 / $3 | 日常图片分析 🔥 |
| `gemini-3.1-flash-image-preview` | 🖼️ 专为图片优化 | $0.25 / $0.067 | 快速批量识图 |
| `gemini-3.1-flash-lite-preview` | 🪶 最轻量 | $0.25 / $1.50 | 简单视觉任务 |

## 验证配置

```bash
# 确认配置已写入
grep -A 10 "vision:" ~/.hermes/config.yaml

# 期望输出：
#   vision:
#     provider: google
#     model: gemini-3-flash-preview
```

## 注意事项
1. **需要 /reset（新会话）** 后才能生效——工具的 provider 变更不能实时切换
2. `Gemini 3 Pro Preview`（`gemini-3-pro-preview`）已于 2026年3月9日 关停，自动指向 `gemini-3.1-pro-preview`
3. `gemini-3-flash-preview` 和 `gemini-3.1-flash-lite-preview` 有免费 tier
4. DeepSeek 不支持 vision——必须配置 auxiliary.vision 才能用 `vision_analyze` 工具

## ⚠️ 已知问题与修复

### 1. browser_vision 卡死/长时间无响应

**根因**：GeminiNativeClient 的默认 HTTP read timeout 为 **600秒（10分钟）**（位于 `gemini_native_adapter.py:834`）：
```python
self._http = httpx.Client(
    timeout=timeout or httpx.Timeout(connect=15.0, read=600.0, write=30.0, pool=30.0)
)
```
当代理连接慢或 Gemini API 从国内访问不稳定时，请求可能挂 10 分钟而不触发超时。

**修复**：
- 降低 `auxiliary.vision.timeout`（config.yaml）为 60s 或更低
- 同时修改 `gemini_native_adapter.py` 中的默认 read timeout 为 `read=120.0`

### 2. Gemini 从中国国内不可用

Google Gemini API 对中国 IP 返回 `"User location is not supported for the API use"`（HTTP 403），即使通过代理也可能被检测。

**替代方案**：使用 **OpenRouter + Qwen-VL 模型**，国内直连可用。

## 替代方案：OpenRouter + Qwen-VL

当 Gemini 不可用或超时时，推荐使用 OpenRouter 托管的 Qwen-VL 模型：

### 配置

```yaml
auxiliary:
  vision:
    api_key: ''                # OpenRouter 自动从 OPENROUTER_API_KEY 读取
    base_url: ''
    provider: openrouter
    model: qwen/qwen3-vl-32b-instruct    # 或 qwen/qwen2.5-vl-72b-instruct
    timeout: 60
```

### 已测试可用的模型（从中国国内直连）

| 模型 | 价格 | 质量 | 备注 |
|:---|:---:|:---:|:---|
| `qwen/qwen3-vl-32b-instruct` | ~$0.0001/张 | ⭐⭐⭐⭐ | **推荐**——性价比最佳 |
| `qwen/qwen2.5-vl-72b-instruct` | ~$0.0003/张 | ⭐⭐⭐⭐⭐ | 质量最高 |
| `qwen/qwen3-vl-8b-instruct` | ~$0.00002/张 | ⭐⭐⭐ | 最便宜 |

### 验证命令

```bash
# 测试 Vision API（需要先设置 OPENROUTER_API_KEY）
SMALL_B64="iVBORw0KGgoAAAANSUhEUgAAAAE..."
curl -s --noproxy '*' --max-time 30 -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d "{
    \"model\": \"qwen/qwen3-vl-32b-instruct\",
    \"messages\": [{
      \"role\": \"user\",
      \"content\": [
        {\"type\": \"text\", \"text\": \"Describe this image.\"},
        {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/png;base64,$SMALL_B64\"}}
      ]
    }],
    \"max_tokens\": 50
  }"
```

### 其他可选方案

| 方案 | 优点 | 缺点 | 适合场景 |
|:---|:---|:---|:---|
| **DashScope (阿里云百炼)** | 国内直连，免费100万tokens新用户 | API Key 可能过期 | 国内用户首选 |
| **Moondream Cloud** | 免费5000次/天 | 国外服务，国内不稳 | 轻量备选 |
| **自托管 Qwen-VL** | 0边际成本 | 需24GB+ VRAM | 长期高用量 |

### 常见问题排查

**`browser_vision` 长时间无响应：**
1. 检查 `~/.hermes/logs/agent.log` 中 `Auxiliary vision: using` 日志的时间戳
2. 用 curl 直接测试 vision provider（见上方验证命令）
3. 检查 config.yaml 中 `auxiliary.vision.timeout` 是否设置合理
4. 检查 `gemini_native_adapter.py` 中默认 read timeout 是否已从 600s 降低

**`call_llm` 抛出连接错误：**
- Gemini：从国内 IP 访问会被拒绝，考虑更换为 OpenRouter + Qwen-VL
- OpenRouter：部分地区可能返回 `"This model is not available in your region"`，换不同模型或 provider

