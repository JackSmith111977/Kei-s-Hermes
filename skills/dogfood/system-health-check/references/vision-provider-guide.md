# Vision Provider 配置指南（国内服务器专版）

> 从中国服务器访问 Vision API 的已验证方案。更新于 2026-05-08。

## 已验证可用的配置

### 方案 1：OpenRouter + Qwen VL ✅ 推荐

```yaml
# config.yaml auxiliary.vision
model: qwen/qwen3-vl-32b-instruct
provider: openrouter
timeout: 60
```

**验证结果**：
- 国内直连（`--noproxy '*'`）：✅ 成功，~3 秒响应
- 费用：~$0.00003/次（32B 模型）
- OpenRouter 自动路由到 Alibaba 等国内 provider

**可用模型**（按质量排序）：
- `qwen/qwen3-vl-32b-instruct` — 推荐，性价比最佳
- `qwen/qwen3-vl-8b-instruct` — 更便宜，质量稍弱
- `qwen/qwen2.5-vl-72b-instruct` — 最强但较慢

### 方案 2：DashScope 阿里云百炼（需有效 API Key）

```yaml
model: qwen3-vl-plus
provider: custom
base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
api_key: ${DASHSCOPE_API_KEY}
```

**免费额度**：新用户每个 VL 模型 100万 tokens，有效期 90 天
**Key 位置**：`~/.hermes/.env` → `DASHSCOPE_API_KEY=sk-xxx`
**注意**：API Key 可能已过期，需去 https://bailian.console.aliyun.com 刷新

### 方案 3：Google Gemini（备用）

```yaml
model: gemini-3-flash-preview
provider: google
```

**问题**：
- 从中国直接访问：HTTP 403 "User location is not supported"
- 通过代理：不稳定，取决于代理节点质量
- 即使通过代理，Google 仍会检测源 IP

## 不可用的方案

| Provider | 原因 | 日志特征 |
|:---|:---|:---|
| DeepSeek V4 | 不支持 `image_url` 格式 | `unknown variant 'image_url', expected 'text'` |
| OpenRouter Gemini 模型 | 区域封锁（中国 IP） | `This model is not available in your region.` |
| LongCat-2.0-Preview | 文本模型，不支持视觉 | 模型无法理解图片输入 |

## 超时诊断速查

当 browser_vision 卡住时：

1. 检查 `agent.log` → 定位 `Auxiliary vision: using xxx` 行
2. 确认 `config.yaml` → `auxiliary.vision.timeout` 值
3. 若 `provider: google` → 检查 `gemini_native_adapter.py:834` 的 `read=600.0`
4. 修复：改 `read=600.0` → `read=120.0`（或直接换 OpenRouter）
5. 测连通性：`curl --noproxy '*' --max-time 30 https://openrouter.ai/api/v1/models`
