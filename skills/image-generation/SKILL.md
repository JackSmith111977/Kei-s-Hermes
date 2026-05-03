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
    skill_type: library
    design_pattern: generator
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

client = OpenAI(
    api_key="sk-...",
    # 如果需要代理，在环境变量中设置：
    # HTTP_PROXY=http://127.0.0.1:7890
    # HTTPS_PROXY=http://127.0.0.1:7890
)

# 基础生图
response = client.images.generate(
    model="gpt-image-2",
    prompt="A photorealistic Tokyo cafe interior at golden hour",
    size="1024x1024",        # 1024x1024, 1536x1024, 1024x1536, auto
    quality="medium",        # low, medium, high
    n=1,
)

# 获取图片（默认返回 b64_json）
image_b64 = response.data[0].b64_json
image_url = response.data[0].url  # 如果传了 response_format="url"

# 保存图片
import base64
with open("output.png", "wb") as f:
    f.write(base64.b64decode(image_b64))
```

**接入方式 B：Fal.ai 聚合 API**（推荐国内使用，无需代理）

```python
import httpx, os

FAL_KEY = os.environ.get("FAL_KEY", "")

async def generate_with_fal(prompt: str, size: str = "landscape_4_3"):
    """通过 Fal.ai 调用 gpt-image-2"""
    url = "https://fal.run/openai/gpt-image-2"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "image_size": size,
        "quality": "medium",
        "num_images": 1,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload, timeout=120)
        data = resp.json()
        return data["images"][0]["url"]
```

**Pricing（OpenAI 官方）**:
| Quality | 1024×1024 | 1536×1024 | 备注 |
|---------|-----------|-----------|------|
| low | ~$0.01 | ~$0.02 | 快速预览 |
| medium | ~$0.04 | ~$0.06 | 平衡质量与成本 |
| high | ~$0.07 | ~$0.10 | 最高质量 |

### 方案二：Stable Diffusion（本地部署，免费）

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

### 方案三：阿里云 Dashscope（通义万相）

```python
from dashscope import ImageSynthesis

resp = ImageSynthesis.call(
    model='wanx-v1',  # 或 'wanx2.1-t2i-turbo'（更快更便宜）
    prompt='一只可爱的猫娘，动漫风格',
    n=1,
    size='1024*1024',
)
if resp.status_code == 200:
    with open('output.png', 'wb') as f:
        f.write(resp.output['result_url'])
```

## 当前环境状态

| 方案 | 状态 | 说明 |
|------|------|------|
| OpenAI gpt-image-2 官方 | ❌ 不可用 | 无 API Key + 被墙 |
| Fal.ai | ⚠️ 待配置 | 需要 FAL_KEY |
| LongCat | ❌ 不支持 | 仅支持文本模型 |
| Dashscope | ⚠️ 待安装 | 需要 `pip install dashscope` |
| 本地 SD | ❌ 不可用 | 无 GPU |

## 推荐配置步骤

1. **最快方案**：注册 Fal.ai（免费额度），获取 FAL_KEY，设置环境变量
2. **最经济方案**：安装 dashscope（阿里云有免费额度），使用通义万相
3. **最佳质量方案**：获取 OpenAI API Key + 配置代理

## 为文档生成配图的最佳实践

### Prompt 模板

**架构图/流程图风格**：
```
Clean minimalist architecture diagram, white background, flat design,
soft pastel colors (blue #4A90D9, coral #FF6B6B, mint #4ECDC4),
rounded rectangles with subtle shadows, thin connecting arrows,
no text, professional technical illustration style
```

**技术概念插图**：
```
Technical illustration of [CONCEPT], isometric style,
gradient background from #1a1a2e to #16213e,
glowing neon accents in cyan and purple,
clean lines, no text, suitable for presentation slides
```

**封面图**：
```
Professional tech book cover, dark gradient background (#0d1117 to #161b22),
abstract circuit board pattern, glowing blue accents,
centered composition with space for title text,
minimalist, modern, no characters
```

### 尺寸建议

| 用途 | 推荐尺寸 | gpt-image-2 参数 |
|------|----------|------------------|
| PPT 封面 | 16:9 | `landscape_16_9` |
| PPT 内容图 | 4:3 | `landscape_4_3` |
| PDF 插图 | 1:1 | `1024x1024` |
| 横幅 | 21:9 | `auto` |
| 手机壁纸 | 9:16 | `portrait_9_16` |

### 工作流程

1. 分析文档内容，确定需要配图的章节
2. 为每个配图编写英文 prompt（gpt-image-2 对英文理解更好）
3. 先用 `quality="low"` 快速预览
4. 满意后用 `quality="high"` 生成最终版本
5. 将图片嵌入 PDF/PPT

## 注意事项

- gpt-image-2 默认返回 `b64_json`，不是 URL
- 如果要用 URL 格式，需要传 `response_format="url"`（但 URL 1 小时后过期）
- 中文 prompt 也支持，但英文 prompt 效果更好
- 批量生成时注意 rate limit（OpenAI: 5 images/min for free tier）
