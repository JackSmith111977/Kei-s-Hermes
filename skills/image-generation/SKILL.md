---
name: image-generation
description: 生成高质量配图（支持 gpt-image-2, Stable Diffusion, Dashscope），含 Prompt 模板与 API 接入指南。
triggers:
- 生图
- 配图
- image gen
- 画图
metadata:
  hermes:
    tags:
    - image
    - generative-ai
    - design
    - prompt-engineering
    category: creative
    related_skills: ["web-ui-ux-design"]
    skill_type: library
    design_pattern: generator
depends_on: []

---
# Image Generation Skill - AI 图片生成技能

## 描述
AI 图片生成技能，支持通过多种方式为文档、PPT、营销素材等生成高质量配图。

## 支持的图片生成方案

### 方案一：OpenAI gpt-image-2（推荐，质量最高）

**模型 ID**: `gpt-image-2`（快照版本 `gpt-image-2-2026-04-21`）

**能力**:
- 文本生图（text-to-image）
- 图片编辑（image-to-image / edit）
- 透明背景输出
- 精确的中文文字渲染（比 DALL·E 3 强很多）
- 4K 分辨率支持

**接入方式 A：OpenAI 官方 API**（需要 OpenAI API Key + 代理）

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

response = client.images.generate(
    model="gpt-image-2",
    prompt="A photorealistic Tokyo cafe interior at golden hour",
    size="1024x1024",
    quality="medium",
    n=1,
)

import base64
with open("output.png", "wb") as f:
    f.write(base64.b64decode(response.data[0].b64_json))
```

**接入方式 B：Fal.ai 聚合 API**（推荐国内使用）

```python
import httpx, os

FAL_KEY = os.environ.get("FAL_KEY", "")

def generate_with_fal(prompt: str, size: str = "landscape_4_3"):
    url = "https://fal.run/openai/gpt-image-2"
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "image_size": size, "quality": "medium", "num_images": 1}
    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json=payload)
        return resp.json()["images"][0]["url"]
```

**Pricing（OpenAI 官方）**:
| Quality | 1024×1024 | 1536×1024 | 备注 |
|---------|-----------|-----------|------|
| low | ~$0.01 | ~$0.02 | 快速预览 |
| medium | ~$0.04 | ~$0.06 | 平衡质量与成本 |
| high | ~$0.07 | ~$0.10 | 最高质量 |

### 方案二：Stable Diffusion（本地部署）

需要安装 diffusers 库 + GPU。

```python
from diffusers import StableDiffusionXLPipeline
import torch

pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
).to("cuda")

image = pipe(prompt="A cute cat girl, anime style").images[0]
image.save("output.png")
```

### 方案三：阿里云 Dashscope（通义万相）✅ 已配置

**免费额度**: 开通百炼后 90 天内，100 张文生图 + 50 秒视频

**推荐模型**:
- `wanx2.1-t2i-turbo` — 快速、免费额度可用 ✅
- `wanx2.7-t2i-turbo` — 更高质量

**HTTP API 调用（异步模式）**:

```python
import httpx
from pathlib import Path

API_KEY = os.environ.get("DASHSCOPE_IMAGE_API_KEY", "")

def generate_with_dashscope(prompt: str, model: str = "wanx2.1-t2i-turbo"):
    """通过 Dashscope API 生成图片"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    payload = {"model": model, "input": {"prompt": prompt}, "parameters": {"size": "1024*1024", "n": 1}}
    
    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json=payload)
        task_id = resp.json()["output"]["task_id"]
        
        status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        for _ in range(15):
            status_resp = client.get(status_url, headers={"Authorization": f"Bearer {API_KEY}"})
            status_data = status_resp.json()
            if status_data["output"]["task_status"] == "SUCCEEDED":
                img_url = status_data["output"]["results"][0]["url"]
                img_resp = client.get(img_url)
                img_path = Path.home() / ".hermes" / "cache" / "generated.png"
                img_path.parent.mkdir(parents=True, exist_ok=True)
                img_path.write_bytes(img_resp.content)
                return str(img_path)
            elif status_data["output"]["task_status"] == "FAILED":
                raise Exception(f"生成失败: {status_data}")
            import time
            time.sleep(3)
```

### 方案四：Google Gemini Nano Banana（🍌 彩蛋模型）⚠️ 部分可用

Google 内部代号 **Nano Banana** 的图片生成模型，在 Gemini API 速率限制文档中以 `Images Per Minute (IPM)` 指标被提及。

**模型名**: `models/nano-banana-pro-preview`
**替代模型**: `models/gemini-3-pro-image-preview`, `models/gemini-3.1-flash-image-preview`

**已验证事实**:
- ✅ 模型真实存在，可通过 OpenAI 兼容端点调用
- ✅ 成功返回 `image/jpeg` MIME 类型（证明模型生成了图片）
- ❌ OpenAI 兼容的 `/chat/completions` 端点无法正确处理图片输出 → 返回 `"Unhandled generated data mime type: image/jpeg"`
- ⚠️ 原生 Google API (`generateContent`) 需要更高权限的 API Key（当前 Key 返回 403）

**接入方式**（OpenAI 兼容端点，仅调用，暂无法取回图片）:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
  -H "Authorization: Bearer $GOOGLE_API_KEY" \
  -d '{
    "model": "models/nano-banana-pro-preview",
    "messages": [{"role":"user","content":"一只可爱的猫娘女仆在服务器机房泡茶"}]
  }'
```

**状态追踪**:
| 日期 | 事件 |
|------|------|
| 2026-05-08 | 首次发现并验证 Nano Banana 模型存在，OpenAI 端点尚不能取回图片 |

## 便捷脚本

为了方便调用，以下脚本已安装到 `~/.hermes/scripts/`：

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `dashscope_gen.py` | 首选生图 — Dashscope 通义万相 | `python3 ~/.hermes/scripts/dashscope_gen.py "prompt" --size 1024*1024` |
| `gemini_vision.py` | 图片理解 — Gemini API 分析图片 | `python3 ~/.hermes/scripts/gemini_vision.py image.jpg "描述这张图"` |
| `fallback_search.py` | 搜索备选 — DuckDuckGo + 直接抓取 | `python3 ~/.hermes/scripts/fallback_search.py "关键词" --limit 5` |

### Dashscope 生图（推荐首选）
```bash
python3 ~/.hermes/scripts/dashscope_gen.py "一只可爱的猫娘女仆" \
  --model wanx2.1-t2i-turbo --size 1024*1024 --wait 45
```
- 支持尺寸：1:1, 16:9, 9:16, 3:4, 4:3
- 免费额度：100 张文生图（90 天内）
- 无需代理，国内直接访问

### Gemini Vision（图片理解）
```bash
python3 ~/.hermes/scripts/gemini_vision.py screenshot.jpg \
  "请详细描述这张图片的内容，包括文字" --model models/gemini-3-flash-preview
```
- 支持 jpg/png/webp/gif/bmp
- 免费额度：输入输出完全免费
- 需走 mihomo 代理

## 当前环境状态

| 方案 | 状态 | 说明 |
|------|------|------|
| OpenAI gpt-image-2 官方 | ❌ 不可用 | 无 API Key + 被墙 |
| Fal.ai | ❌ 余额用尽 | 已配置但余额耗尽 |
| Dashscope 通义万相 | ✅ 可用 | Key 已配置 |
| 本地 SD | ❌ 不可用 | 无 GPU |
| Google Gemini Nano Banana | ⚠️ 模型存在，端点不完善 | 见下方方案四 |

## Prompt 模板

**架构图/流程图风格**：
```
Clean minimalist architecture diagram, white background, flat design,
soft pastel colors, rounded rectangles with subtle shadows,
thin connecting arrows, no text
```

**技术概念插图**：
```
Technical illustration, isometric style, gradient background,
glowing neon accents, clean lines, no text
```

**封面图**：
```
Professional tech book cover, dark gradient background,
abstract circuit board pattern, glowing blue accents,
centered composition, minimalist
```

**动漫/插画风格**：
```
Cute anime character, soft pastel colors, kawaii style,
chibi proportions, clean background, digital art
```

## 尺寸建议

| 用途 | 推荐尺寸 | Dashscope 参数 |
|------|----------|----------------|
| PPT 封面 | 16:9 | `1920*1080` |
| PDF 插图 | 1:1 | `1024*1024` |
| 手机壁纸 | 9:16 | `720*1280` |

## 工作流程

1. 分析内容，确定配图需求
2. 编写 Prompt（英文效果更好）
3. 调用 API 生成图片
4. 下载并保存图片
5. 嵌入到文档中

## 注意事项

- Dashscope 使用异步模式，需等待任务完成（通常 3-15 秒）
- 批量生成时注意 rate limit
- 中文 prompt 也支持，但英文 prompt 效果更好