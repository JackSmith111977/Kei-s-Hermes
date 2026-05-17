---
name: system-health-check
description: Hermes Agent 系统健康检查、LLM 可观测性与自动修复指南。涵盖 429 限流降级、Fallback 链断裂、辅助模型配置、日志分析、Ci...
version: 2.1.0
triggers:
- 健康检查
- 诊断
- 报错
- '429'
- health check
metadata:
  hermes:
    tags:
    - health-check
    - diagnostics
    - fallback
    - observability
    - circuit-breaker
    - vision
    category: dogfood
    related_skills: ["file-system-manager"]
    skill_type: diagnosis
    design_pattern: inversion
depends_on: []

---
# 系统健康检查与修复 🔍🔧

> **核心理念**：生产级 LLM 应用需要防御性编程。不仅仅是看日志，而是建立 **可观测性（Observability）** 和 **容错机制（Resilience）**。

## 〇、快速诊断：hermes doctor（首选）

升级 v0.12.0 后，Hermes 内置了 `hermes doctor` 诊断工具：

```bash
# 一键健康检查
hermes doctor

# 自动修复可修复的问题
hermes doctor --fix
```

**`hermes doctor --fix` 会自动修复：**
- Config 版本迁移（如 v21 → v23）
- WAL 文件 checkpoint（清理过大的 WAL）
- Seed curator 默认配置项

> ⚠️ 升级后第一步：运行 `hermes doctor --fix` 确保配置和数据库状态最新。

---

## 一、LLM 可观测性四大支柱

根据业界最佳实践，LLM Agent 的健康检查应覆盖以下四个维度：

| 维度 | 指标 | 如何检查 |
|:---|:---|:---|
| **1. 技术性能** | 延迟 (p50/p99), Token 生成速度, 错误率 | `grep 'latency\|429\|500' agent.log` |
| **2. 输出质量** | 幻觉率, 重复循环, 语义相关性 | `grep 'repetition\|hallucination' agent.log` |
| **3. 行为模式** | Tool Call 成功率, 推理深度, 工具偏好 | `grep 'tool.*fail\|tool.*success' agent.log` |
| **4. 依赖健康** | Provider 可用性, 速率限制, Fallback 触发 | `grep 'provider.*error\|fallback' agent.log` |

---

## 二、日志位置与 Trace 分析

### 日志路径
```
主日志: ~/.hermes/logs/agent.log
错误日志: ~/.hermes/logs/errors.log
轮转配置: max_size_mb=5, backup_count=3
```

### 高级扫描命令（Trace Replay）
```bash
# 追踪失败链路：找出是哪个 Tool Call 导致了最终错误
grep -B5 'ERROR' ~/.hermes/logs/agent.log | grep -E 'tool.*call|provider|ERROR'

# 查找 Fallback 链断裂（最终导致服务不可用）
grep 'Fallback activated' agent.log | tail -10

# 统计各 Provider 错误率
grep -oP 'provider=\K[^ ]+' agent.log | sort | uniq -c | sort -rn

# 查找 429 限流爆发点（判断是否遭遇突发流量）
grep '429' agent.log | awk '{print $1, $2}' | sort | uniq -c | sort -rn
```

---

## 三、告警诊断与自动修复

### 🔴 告警 1：429 限流 + Fallback 链断裂

**表现**：
```
API call failed after 3 retries. HTTP 429: usage allocated quota exceeded
Fallback activated: qwen3.6-plus → LongCat-2.0-Preview
Fallback activated: LongCat-2.0-Preview → deepseek-v4-flash
Non-retryable client error: Error code: 401 - Authentication Fails
```

**根因分析**：
1. 主 Provider 触发限流，进入 Retry（通常重试 3 次）。
2. Retry 耗尽后，Fallback 到备用 Provider。
3. 如果备用 Provider 的 API Key 无效（401），**整个链路断裂**，Agent 停止响应。

**修复方案**：
1. **确保 Fallback 链至少有 3 个节点**，且每个节点的 Key 都有效。
2. **实施 Circuit Breaker（熔断）**：当某 Provider 连续失败 N 次，暂时将其标记为 "down"，直接跳到下一个，避免无意义重试浪费时间。
3. **检查环境变量**：确认 `DEEPSEEK_API_KEY`, `CUSTOM_LONGCAT_API_KEY` 是否过期。

**配置示例**（config.yaml）：
```yaml
fallback_providers:
- provider: custom_longCat
  model: LongCat-2.0-Preview
  base_url: https://api.longcat.chat/openai
  key_env: CUSTOM_LONGCAT_API_KEY
- provider: deepseek
  model: deepseek-v4-flash
  base_url: https://api.deepseek.com/v1
  key_env: DEEPSEEK_API_KEY
- provider: glm
  model: glm-4
  base_url: https://open.bigmodel.cn/api/paas/v4
  key_env: GLM_API_KEY
```

### 🔴 告警 2：辅助模型（Auxiliary）无 Fallback

**表现**：
```
Auxiliary compression: connection error on auto and no fallback available
(tried: openrouter, nous, local/custom, openai-codex, api-key)
```

**根因**：
- `auxiliary.*` 设置为 `provider: auto`，但 auto 检测失败且无其他配置。
- 导致上下文压缩、记忆整理等后台任务静默失败。

**修复方案**（显式指定 Provider）：
```yaml
auxiliary:
  compression:
    provider: deepseek
    model: deepseek-v4-flash
  session_search:
    provider: deepseek
    model: deepseek-v4-flash
  flush_memories:
    provider: deepseek
    model: deepseek-v4-flash
```

### 🟡 告警 3：微信发送失败 (上游服务问题)

**表现**：
```
[Weixin] Send failed: iLink sendmessage error: ret=-2 errcode=None errmsg=unknown error
```

**对策**：
- 文本发送偶发失败，属于上游 iLink 服务问题。
- boku 侧无法修复，但可监控失败频率，若持续失败则告警。

### 🟡 告警 4：browser_vision 超时/卡死

**表现**：
```
用户：怎么卡在这里了？
日志：[Auxiliary vision: using gemini (gemini-3-flash-preview)]
     → 之后完全静默 8+ 分钟无任何日志
```

**根因诊断链路**（按顺序排查）：

```
① agent.log 确认 vision API 调用开始时间
    ↓
② 检查 auxiliary.vision.timeout 配置（默认 120s）
    ↓
③ 如果 provider=google，检查 GeminiNativeClient 默认 read timeout
   → gemini_native_adapter.py:834 默认 read=600s（10分钟！）
   → 即使 per-request timeout 设了 60s，底层 httpx 可能未被正确 override
   → 修复：改 read=120s（或更低）
    ↓
④ 如果从中国访问 Gemini API，检查是否被区域封锁：
   → HTTP 403 "User location is not supported for the API use"
   → 此错误不可修复，必须换 provider
    ↓
⑤ 测试 vision provider 连通性：
   # 测试 OpenRouter Qwen VL（从中国直连已验证）
   curl -s --noproxy '*' --max-time 30 -X POST "https://openrouter.ai/api/v1/chat/completions" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -d '{"model":"qwen/qwen3-vl-32b-instruct","messages":[{"role":"user","content":[{"type":"text","text":"hi"}]}],"max_tokens":10}'
```

**修复方案**（按优先级）：

| 方案 | 操作 | 适用场景 |
|:---|:---|:---|
| **A. 加超时兜底** | `gemini_native_adapter.py` 中改 `read=600.0` → `read=120.0` | Gemini 能用但响应慢 |
| **B. 切换 provider** | `config.yaml` 中 `vision.provider: openrouter` + `model: qwen/qwen3-vl-32b-instruct` | Gemini 被区域封锁 / 需要国内直连 |
| **C. 换 API 端点** | 用 OpenRouter 的 qwen VL 系列（已验证可用） | 需要免费/低价方案 |

**已验证可行的 Vision Provider 配置**：

```yaml
# config.yaml auxiliary.vision
# 方案 1：OpenRouter + Qwen VL（从中国直连，已验证 ✅）
vision:
  model: qwen/qwen3-vl-32b-instruct
  provider: openrouter
  timeout: 60

# 方案 2：DashScope 阿里云百炼（国内直连，需有效 Key）
# model: qwen3-vl-plus
# provider: custom
# base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
# 注意：DASHSCOPE_API_KEY 可能已过期

# 方案 3：Google Gemini（需要代理 + 不保证国内可用）
# model: gemini-3-flash-preview
# provider: google
```

**免费额度参考**（截至 2026-05）：

| Provider | 费用 | 国内直连 | 已验证 |
|:---|:---:|:---:|:---:|
| OpenRouter Qwen3-VL-32B | ~$0.00003/次 | ✅ | ✅ |
| 阿里云百炼 Qwen3-VL-Plus | 新用户 100万 tokens/模型 | ✅ | ❌ Key 过期 |
| Google Gemini Flash | 15 RPM 免费 | ❌ 区域封锁 | ✅ 通过代理但不稳 |

**调试技巧**：当 browser_vision 卡住时，检查 agent.log 中 `Auxiliary vision: using` 行之后的日志间隔。如果 > 120s 无后续日志 → 大概率是 GeminiNativeClient 的 read timeout 问题。

---

## 四、一键健康检查脚本 v2

```bash
#!/bin/bash
# ~/.hermes/scripts/health-check.sh
# 全面检查：进程、端口、日志告警、Provider 连通性、辅助模型配置

LOG=~/.hermes/logs/agent.log
echo "=== Hermes Agent 深度健康检查 ==="
echo ""

# 1. 进程与端口
echo "[1/5] 基础设施:"
pgrep -f "hermes" > /dev/null && echo "✅ Hermes 进程运行中" || echo "❌ Hermes 未运行"
pgrep -f "mihomo" > /dev/null && echo "✅ mihomo 代理运行中" || echo "⚠️ 代理未运行"

# 2. 日志统计（近 1000 行）
echo ""
echo "[2/5] 最近日志统计:"
COUNT_429=$(tail -1000 "$LOG" | grep -c '429' 2>/dev/null || echo 0)
COUNT_FB=$(tail -1000 "$LOG" | grep -c 'Fallback activated' 2>/dev/null || echo 0)
echo "   429 限流: $COUNT_429 次"
echo "   Fallback 触发: $COUNT_FB 次"

if [ "$COUNT_429" -gt 5 ]; then
    echo "   ⚠️ 警告：限流频繁，请检查 API 额度或增加 Fallback 节点"
fi

# 3. Fallback 链完整性检查
echo ""
echo "[3/5] Fallback 链:"
if grep -q '401.*Authentication Fails' "$LOG" 2>/dev/null; then
    echo "   ❌ 发现认证失败 (401)：Fallback 链已断裂！"
    echo "   请检查 DEEPSEEK_API_KEY 或其他备用 Key 是否有效"
else
    echo "   ✅ Fallback 链完整（无认证失败）"
fi

# 4. 辅助模型配置检查
echo ""
echo "[4/5] 辅助模型:"
if grep -q 'provider: auto' ~/.hermes/config.yaml 2>/dev/null; then
    echo "   ⚠️ auxiliary 配置为 'auto'，可能导致 fallback 失败"
    echo "   建议在 config.yaml 中显式指定 provider"
else
    echo "   ✅ auxiliary 已显式配置"
fi

# 5. Provider 连通性测试（通过代理）
echo ""
echo "[5/5] Provider 连通性:"
PROXY="http://127.0.0.1:7890"
curl -s -o /dev/null -w "api.deepseek.com: HTTP %{http_code}\n" \
    --connect-timeout 3 --proxy "$PROXY" https://api.deepseek.com/v1/models 2>/dev/null || \
    echo "api.deepseek.com: 连接失败"

echo ""
echo "=== 检查完成 ==="
```

---

## 五、主动防御策略 (Circuit Breaker)

### 规则
1. **指数退避重试**：遇到 429/500 错误，等待 2s → 4s → 8s 后重试。
2. **熔断机制**：同一 Provider 1 分钟内连续 5 次失败 → 标记为 "unhealthy"，直接使用 Fallback，跳过该 Provider 10 分钟。
3. **金丝雀测试**：每隔 30 分钟发送一个简单 prompt 到各 Provider，验证连通性，若失败则提前切换。
