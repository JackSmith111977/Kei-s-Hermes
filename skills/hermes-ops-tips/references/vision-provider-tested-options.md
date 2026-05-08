# Vision Provider 实测数据（2026-05 月，国内服务器）

> 测试时间: 2026-05-08 | 服务器: Ubuntu, China
> 测试方式: curl 直接测试 + Hermes call_llm 集成测试

## 各 Provider 详细测试结果

### ✅ OpenRouter — 推荐使用

**模型**: `qwen/qwen3-vl-32b-instruct`
**费用**: $0.000000104/token （prompt）
**国内直连**: ✅ 成功（不需代理）
**响应时间**: ~3秒
**测试结果**:
- 正确识别 200x100 蓝色矩形为 "Solid light blue background"
- 图片尺寸限制: 宽度和高度需 >= 10px
- API 格式: 标准 OpenAI `chat/completions`，支持 `image_url`

**其他可用模型** (同方式测试通过):
- `qwen/qwen2.5-vl-72b-instruct` — 质量更好，$0.00000025/token
- `qwen/qwen3-vl-8b-instruct` — 更轻量，$0.00000008/token
- `qwen/qwen-vl-plus` — 旧款，$0.0000001365/token

### ❌ Google Gemini — 区域封锁

**模型**: `gemini-3-flash-preview`
**错误**: `User location is not supported for the API use.` (HTTP 400)
**原因**: Google 检测源 IP 为中国地区，即使通过代理和 API Key 也拒绝服务
**注意**: 即使通过 mihomo 代理转发，出口 IP 仍被识别为中国地区

### ❌ Aliyun DashScope — Key 过期

**模型**: `qwen3-vl-plus`
**国内直连**: ✅ 网络可达
**错误**: `Incorrect API key provided` (HTTP 401)
**原因**: `DASHSCOPE_API_KEY` 已过期
**解决方法**: 前往 https://bailian.console.aliyun.com/ → 设置 → API-Key 重新创建
**免费额度**: 新用户 100万 tokens/模型，有效期 90天

### ❌ DeepSeek V4 Flash — 不支持 vision

**模型**: `deepseek-v4-flash`
**错误**: `unknown variant 'image_url', expected 'text'`
**原因**: DeepSeek V4 的 `chat/completions` 接口不支持 `image_url` 类型，仅接受文本
**替代**: 需使用 DeepSeek 专门的 `/vision` 端点（非 OpenAI 兼容格式）

### ❌ LongCat — 文本模型

**模型**: `LongCat-2.0-Preview`
**结果**: API 返回成功但无法识别图片内容（"I don't see any image attached"）
**原因**: 模型本身不支持多模态输入，仅文本

## API Key 清单

| Key 名称 | 来源 | 用途 | 状态 |
|:---------|:-----|:-----|:----|
| `OPENROUTER_API_KEY` | openrouter.ai | 主 LLM + vision fallback | ✅ 有效 |
| `GOOGLE_API_KEY` | aistudio.google.com | Gemini 原生 API | ✅ 有效但区域封锁 |
| `DASHSCOPE_API_KEY` | dashscope.aliyuncs.com | Aliyun 百炼 | ❌ 已过期 |
| `DEEPSEEK_API_KEY` | platform.deepseek.com | DeepSeek API | ✅ 有效但无 vision |
| `CUSTOM_LONGCAT_API_KEY` | api.longcat.chat | LongCat LLM | ✅ 有效但无 vision |

## Vision API 调用时序建议

```
browser_vision("描述截图")
  │
  ├─ 1. agent-browser screenshot → 截图到文件 (~1-2s)
  │
  ├─ 2. call_llm(task="vision", provider=openrouter, model=qwen3-vl-32b) (~3-5s)
  │     ├─ timeout: config.yaml → auxiliary.vision.timeout (建议 60s)
  │     └─ GeminiNativeClient 底层 read timeout (默认 600s → 改为 120s)
  │
  └─ 3. 返回 {"analysis": "...", "screenshot_path": "..."}
```

## 超时设置清单

| 位置 | 默认值 | 建议值 | 修改文件 |
|:-----|:------:|:------:|:---------|
| config `auxiliary.vision.timeout` | 120s | **60s** | `~/.hermes/config.yaml` |
| GeminiNativeClient `read` timeout | **600s** | **120s** | `agent/gemini_native_adapter.py:834` |
