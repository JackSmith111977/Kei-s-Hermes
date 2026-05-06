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

## 当前环境状态

| 方案 | 状态 | 说明 |
|------|------|------|
| OpenAI gpt-image-2 官方 | ❌ 不可用 | 无 API Key + 被墙 |
| Fal.ai | ❌ 余额用尽 | 已配置但余额耗尽 |
| Dashscope 通义万相 | ✅ 可用 | Key 已配置 |
| 本地 SD | ❌ 不可用 | 无 GPU |

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