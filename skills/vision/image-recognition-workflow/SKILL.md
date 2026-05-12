---
name: image-recognition-workflow
description: "图片识别与文档识别工作流 — 当主模型不具备多模态能力时，通过 Gemini API (File API + file_data) 识别图片/docx/PDF 中的内容。涵盖图片提取、File API 上传、视觉分析、结构化输出的完整流程。"
version: 1.0.0
triggers:
  - 识图
  - 图片识别
  - 文档识别
  - OCR
  - 提取图片文字
  - 识别图片内容
  - 看图
  - 视觉分析
  - image recognition
  - ocr
  - document recognition
  - 检测图片
  - 识别图片
  - 读取图片
  - 图片中的文字
  - 扫描文档
  - docx 图片
  - pdf 图片
  - vision
depends_on:
  - web-access
metadata:
  hermes:
    tags:
      - vision
      - ocr
      - document-processing
      - gemini
      - multimodal
    category: vision
    skill_type: workflow
    design_pattern: pipeline
---

# 🖼️ 图片识别与文档识别工作流 v1.0

> **核心理念**: 主模型不具备多模态时，自动路由到 Gemini API 辅助视觉服务。
> **关键发现**: `inline_data` 在代理环境下返回 403，必须使用 **File API + file_data** 方式。
> **代理要求**: 所有请求通过 `http://127.0.0.1:7890`（mihomo 代理）

---

## 〇、工作流总览

```text
用户输入（图片/docx/PDF/文件路径）
  ↓
[Gate 0] 是否需要走视觉识别？
  ├─ 主模型支持多模态 + 用户无特殊要求 → 直接主模型处理
  └─ 需要辅助视觉 → 进入本工作流
        ↓
[Phase 1] 文件类型判断与图片提取
  ├─ 直接图片 (PNG/JPEG/WEBP/GIF) → 直接上传
  ├─ docx 文件 → 解压提取 word/media/ 图片
  ├─ PDF 文件 → 直接上传 File API
  └─ 文件路径 → 读取后判断类型
        ↓
[Phase 2] Gemini File API 上传
  POST /upload/v1beta/files → 获取 file_uri
        ↓
[Phase 3] Gemini 视觉分析
  POST /v1beta/models/gemini-3-flash-preview:generateContent
  → 使用 file_data 引用上传的文件
        ↓
[Phase 4] 结果结构化输出
  根据提示词返回结构化/非结构化结果
```

---

## Gate 0: 触发条件判断

当以下任一条件满足时，触发本工作流：

```python
def should_route_to_vision_workflow(user_input: str, has_attachments: bool) -> bool:
    """判断是否需要走视觉识别工作流"""
    vision_keywords = [
        "识别", "看", "图", "图片", "image", "photo", "截图",
        "ocr", "提取文字", "文档", "扫描", "视觉",
    ]
    has_vision_intent = any(kw in user_input.lower() for kw in vision_keywords)
    return has_attachments or has_vision_intent
```

---

## Phase 1: 文件类型判断与图片提取

### 1.1 图片文件直接传递
支持的格式：PNG, JPEG, WEBP, HEIC, HEIF, GIF

### 1.2 docx 文件图片提取
```python
import zipfile, os, tempfile

def extract_docx_images(docx_path: str) -> list[str]:
    """从 docx 中提取所有图片，返回图片路径列表"""
    output_dir = tempfile.mkdtemp(prefix="docx_images_")
    images = []
    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.startswith("word/media/"):
                data = z.read(name)
                fname = os.path.basename(name)
                fpath = os.path.join(output_dir, fname)
                with open(fpath, "wb") as f:
                    f.write(data)
                images.append(fpath)
    return images
```

### 1.3 PDF 文件直接处理（无需提取图片）
PDF 可以**直接上传到 File API**，Gemini 原生理解 PDF 中的图表、图片和文字：
- MIME type: `application/pdf`
- 限制: ≤50MB 或 1000 页
- 每页 ~560 tokens（默认 media_resolution）
- Gemini 3 支持 media_resolution 粒度控制 (LOW/MEDIUM/HIGH)

---

## Phase 2: Gemini File API 上传

### 核心命令
```bash
# 上传文件到 Gemini File API
UPLOAD_RESP=$(curl -s --max-time 30 \
  --proxy http://127.0.0.1:7890 \
  -X POST \
  -H "x-goog-api-key: ${GOOGLE_API_KEY}" \
  -F "file=@/path/to/image.png" \
  "https://generativelanguage.googleapis.com/upload/v1beta/files")

# 从响应中提取 file_uri
FILE_URI=$(echo "$UPLOAD_RESP" | python3 -c "
import sys, json
print(json.load(sys.stdin)['file']['uri'])
")
```

### Python 封装
```python
import subprocess, json

def upload_to_gemini(file_path: str, mime_type: str = None) -> str:
    """上传文件到 Gemini File API，返回 file_uri"""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    proxy = "http://127.0.0.1:7890"
    
    resp = subprocess.run([
        "curl", "-s", "--max-time", "30",
        "--proxy", proxy,
        "-X", "POST",
        "-H", f"x-goog-api-key: {api_key}",
        "-F", f"file=@{file_path}",
        "https://generativelanguage.googleapis.com/upload/v1beta/files",
    ], capture_output=True, text=True, timeout=35)
    
    result = json.loads(resp.stdout)
    return result["file"]["uri"]
```

### ⚠️ 注意事项
- 文件最大 2GB，项目总存储 20GB
- 文件 48 小时后自动删除
- API 免费使用
- 认证必须用 `x-goog-api-key` 请求头（query param 也可以但 header 更可靠）

---

## Phase 3: Gemini 视觉分析

### 核心命令
```bash
curl -s --max-time 60 \
  --proxy http://127.0.0.1:7890 \
  -X POST \
  -H "x-goog-api-key: ${GOOGLE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "请详细描述这张图片中的所有内容"},
        {"file_data": {"mime_type": "image/png", "file_uri": "'"${FILE_URI}"'"}}
      ]
    }]
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
```

### Python 封装
```python
def vision_analyze(file_uri: str, prompt: str, mime_type: str = "image/png",
                   model: str = "gemini-3-flash-preview") -> str:
    """通过 Gemini 视觉分析图片/文档"""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    proxy = "http://127.0.0.1:7890"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"file_data": {"mime_type": mime_type, "file_uri": file_uri}}
            ]
        }]
    }
    
    resp = subprocess.run([
        "curl", "-s", "--max-time", "60",
        "--proxy", proxy,
        "-X", "POST",
        "-H", f"x-goog-api-key: {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    ], capture_output=True, text=True, timeout=70)
    
    result = json.loads(resp.stdout)
    if "candidates" in result:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    raise RuntimeError(f"Vision API error: {result.get('error', {}).get('message', 'unknown')}")
```

### 整合 pipeline
```python
def image_recognition_pipeline(file_path: str, prompt: str = None) -> str:
    """完整的图片识别流水线"""
    # 1. 判断文件类型
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        mime = "application/pdf"
    elif ext in (".png", ".jpg", ".jpeg", ".webp"):
        mime = f"image/{ext[1:]}".replace("jpg", "jpeg")
    elif ext == ".docx":
        # docx 需要先提取图片
        images = extract_docx_images(file_path)
        if not images:
            return "文档中未找到图片"
        # 这里简化处理：只分析第一张图
        file_path = images[0]
        mime = "image/png"
    else:
        return f"不支持的文件类型: {ext}"
    
    if prompt is None:
        prompt = "请详细描述这张图片中的所有文字和内容"
    
    # 2. 上传到 File API
    file_uri = upload_to_gemini(file_path, mime)
    
    # 3. 视觉分析
    result = vision_analyze(file_uri, prompt, mime)
    
    return result
```

### 推荐 Prompt 模板
| 场景 | Prompt |
|:---|:---|
| 通用描述 | "请详细描述这张图片中的所有内容" |
| 文字提取 (OCR) | "请提取这张图片中的所有文字，保持原有格式和排版" |
| 表格识别 | "请将图中的表格转换为 Markdown 格式" |
| 图表分析 | "请分析这张图表的类型（折线/柱状/饼图）和数据趋势" |
| 文档扫描 | "请将这份文档的内容结构化输出，包括标题、段落和列表" |

---

## Phase 4: 结果处理

### 结构化输出
```python
import json, re

def parse_vision_result(text: str, format_hint: str = "text") -> dict:
    """将视觉分析结果结构化"""
    result = {"raw": text, "format": format_hint}
    
    if format_hint == "json":
        # 尝试从文本中提取 JSON
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            result["structured"] = json.loads(json_match.group(1))
    
    elif format_hint == "table":
        # 提取 Markdown 表格
        table_match = re.findall(r'\|.*\|', text)
        if table_match:
            result["table_lines"] = table_match
    
    return result
```

---

## 🚨 坑与注意事项

### 坑 1: inline_data 403
- **现象**: `{"inline_data": {...}}` 返回 403
- **原因**: API key 限制或代理对超大 payload 处理问题
- **解决**: **必须使用 File API + file_data 方式**

### 坑 2: 代理必须配置
```bash
# curl 都必须加 --proxy
curl ... --proxy http://127.0.0.1:7890 ...
```
- Python httpx/requests 需配置 `proxies={"http://": "...", "https://": "..."}`

### 坑 3: x-goog-api-key 头
- 优先用请求头而非 query param
- 部分端点对 query param 支持不完整

### 坑 4: 文件 48h 过期
- File API 上传的文件 48 小时后自动删除
- 长时间任务需重新上传
- 如果需要持久化，保存图片本地 + 用前上传

### 坑 5: 超时设置
- 上传: timeout ≥ 30s（大文件更久）
- 分析: timeout ≥ 60s（复杂图片更久）
- 建议使用 `--max-time` 参数

### 坑 6: docx 图片提取
- 图片在 `word/media/` 目录中
- 嵌入的 EMF/WMF 矢量图可能需要特殊处理
- 图片顺序可能与文档中显示的不一致

---

## 🔧 模型选择指南

| 模型 | 适用场景 | Token价格 | 特点 |
|:---|:---|:---:|:---|
| `gemini-3-flash-preview` | 通用识图（默认） | 低 | 快速，性价比高 |
| `gemini-2.5-flash` | 通用多模态 | 低 | 稳定版 |
| `gemini-2.5-flash-image` | 图像理解优化 | 中 | 专为图像优化 |
| `gemini-3-pro-image-preview` | 高精度识图 | 高 | 精度最高 |
| `gemini-3.1-flash-image-preview` | 最新Flash图像 | 中 | 支持图像生成+理解 |

---

## 📊 Token 计算参考

| 内容类型 | Token 消耗 |
|:---|:---:|
| 图片 ≤384px | 258 tokens |
| 大图 (960×540) | ~6 tiles × 258 = 1548 tokens |
| PDF 每页 (默认) | 560 tokens |
| PDF 每页 (LOW) | 280 tokens |
| PDF 每页 (HIGH) | 1120 tokens |
| 文本 | 按字符计算 |

---

## 🔍 验证测试

### 测试 1: 图片上传 + 识别
```bash
# 创建测试图片
python3 -c "
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (400, 200), 'white')
draw = ImageDraw.Draw(img)
draw.text((30, 50), 'Test OCR 123', fill='black')
img.save('/tmp/test_ocr.png')
"

# 上传并识别
source ~/.hermes/.env
UPLOAD=$(curl -s --max-time 15 --proxy http://127.0.0.1:7890 \
  -X POST -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -F "file=@/tmp/test_ocr.png" \
  "https://generativelanguage.googleapis.com/upload/v1beta/files")
URI=$(echo "$UPLOAD" | python3 -c "import sys,json;print(json.load(sys.stdin)['file']['uri'])")

curl -s --max-time 20 --proxy http://127.0.0.1:7890 \
  -X POST -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"What text is in this image?\"},{\"file_data\":{\"mime_type\":\"image/png\",\"file_uri\":\"$URI\"}}]}]}" \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
```

### 测试 2: PDF 文档识别
同上，改 MIME type 为 `application/pdf` 即可

### 测试 3: docx 图片提取 + 识别
```bash
python3 -c "
import zipfile, os, tempfile, json, subprocess

# 提取 docx 图片
with zipfile.ZipFile('document.docx') as z:
    for name in z.namelist():
        if name.startswith('word/media/'):
            z.extract(name, '/tmp/docx_images/')
            # ... 后续上传 + 识别同上
"
```

---

## 📚 参考资料
- [Gemini API Image Understanding](https://ai.google.dev/gemini-api/docs/image-understanding)
- [Gemini API Files API](https://ai.google.dev/gemini-api/docs/files)
- [Gemini API Document Processing](https://ai.google.dev/gemini-api/docs/document-processing)
- [Gemini CLI](https://google-gemini.github.io/gemini-cli/)
- [Chrome DevTools MCP](https://github.com/chromedevtools/chrome-devtools-mcp)

---

## 🛠️ GeminiNativeClient 修改记录

### 修改文件
`~/.hermes/hermes-agent/agent/gemini_native_adapter.py`

### 变更内容
| # | 变更 | 说明 |
|:---:|:---|:---|
| 1 | 添加 `import os, tempfile` | 新增系统模块依赖 |
| 2 | 添加 `DEFAULT_FILE_API_BASE` | File API 端点常量 |
| 3 | 添加 `_detect_proxy()` | 自动检测代理（env → mihomo 7890） |
| 4 | 修改 `__init__` | httpx 客户端添加 `proxy` 参数 |
| 5 | 添加 `_upload_image_to_file_api()` | 通过 File API 上传图片，返回 file_uri |
| 6 | 添加 `_preprocess_messages_for_vision()` | 预处理消息：将 `image_url` 替换为 `file_data` |
| 7 | 修改 `_extract_multimodal_parts()` | 新增 `file_data` 类型处理器 |
| 8 | 修改 `_create_chat_completion()` | 调用预处理后再构建请求 |

### 数据流变化
```
Before: image_url → inlineData → 403 ❌
After:  image_url → File API upload → file_data → 200 ✅
```

### 回滚方法
```bash
cp ~/.hermes/hermes-agent/agent/gemini_native_adapter.py.bak \
   ~/.hermes/hermes-agent/agent/gemini_native_adapter.py
```

---

## 📝 更新记录
| 版本 | 日期 | 变更 |
|:---|:---|:---|
| 1.0.0 | 2026-05-12 | 初始版本。基于深度学习研究，建立 File API + file_data 完整工作流。 |
| 1.0.0 | 2026-05-12 | 修改 GeminiNativeClient：添加代理支持 + File API 落难/预处理。 |
