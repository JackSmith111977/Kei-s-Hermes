#!/usr/bin/env python3
"""
Gemini Vision — 图片理解工具
使用 Gemini API (OpenAI兼容端点) 分析图片
支持：图片描述、OCR、图标识别、流程图理解等

用法:
  python3 gemini_vision.py <图片路径> [提示词] [--model 模型名]

示例:
  python3 gemini_vision.py screenshot.jpg "描述这张图"
  python3 gemini_vision.py diagram.png "解释这个架构图" --model models/gemini-2.5-pro
"""

import os, sys, json, base64, argparse
from pathlib import Path

# 从 .env 加载 API Key
ENV_PATH = os.path.expanduser("~/.hermes/.env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

PROXY = "http://127.0.0.1:7890"
API_KEY = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
DEFAULT_MODEL = "models/gemini-3-flash-preview"
DEFAULT_PROMPT = "请详细描述这张图片的内容"

MIME_MAP = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.png': 'image/png', '.gif': 'image/gif',
    '.webp': 'image/webp', '.bmp': 'image/bmp',
}


def encode_image(image_path):
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {image_path}")
    mime = MIME_MAP.get(path.suffix.lower(), 'image/jpeg')
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    return b64, mime


def analyze_image(image_path, prompt=DEFAULT_PROMPT, model=DEFAULT_MODEL,
                  temperature=0.5, max_tokens=2048):
    import httpx
    b64_data, mime_type = encode_image(image_path)

    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}}
            ]
        }],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    old_proxy = os.environ.get("HTTPS_PROXY", "")
    os.environ["HTTPS_PROXY"] = PROXY
    os.environ["HTTP_PROXY"] = PROXY

    response = None
    try:
        with httpx.Client(timeout=120) as client:
            response = client.post(
                f"{BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=payload
            )
    finally:
        os.environ["HTTPS_PROXY"] = old_proxy
        os.environ["HTTP_PROXY"] = old_proxy

    if response is None:
        return {"error": "API 请求失败（无响应）"}
    if response.status_code != 200:
        return {"error": f"API错误 {response.status_code}: {response.text[:300]}"}

    result = response.json()
    if "choices" in result and result["choices"]:
        usage = result.get("usage", {})
        return {
            "content": result["choices"][0]["message"]["content"],
            "usage": {k: usage.get(k, 0) for k in ("prompt_tokens", "completion_tokens", "total_tokens")},
            "model": model,
            "image": image_path,
        }
    return {"error": f"未知响应: {json.dumps(result, indent=2)[:300]}"}


def main():
    parser = argparse.ArgumentParser(description="Gemini Vision - 图片分析工具")
    parser.add_argument("image", help="图片路径")
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT, help="分析提示词")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型名 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if not API_KEY:
        print("❌ 错误: 未设置 GOOGLE_API_KEY 环境变量")
        sys.exit(1)

    try:
        file_size = os.path.getsize(args.image)
        if file_size > 10 * 1024 * 1024:
            print(f"⚠️ 图片过大 ({file_size/1024/1024:.1f}MB)，建议压缩")

        result = analyze_image(args.image, args.prompt, args.model,
                               temperature=args.temperature, max_tokens=args.max_tokens)
        if "error" in result:
            print(f"❌ {result['error']}")
            sys.exit(1)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"📷 图片: {result['image']}")
            print(f"🤖 模型: {result['model']}")
            print(f"{'='*50}\n")
            print(result['content'])
            print(f"\n{'='*50}")
            print(f"📊 Token: {result['usage']['total_tokens']} "
                  f"(输入 {result['usage']['prompt_tokens']} → 输出 {result['usage']['completion_tokens']})")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
