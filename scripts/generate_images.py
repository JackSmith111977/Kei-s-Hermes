#!/usr/bin/env python3
"""
AI 图片生成工具 - 支持多种后端
用法:
    python3 generate_images.py --prompt "描述" --output output.png
    python3 generate_images.py --batch prompts.txt --output-dir ./images/
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

def load_env():
    """从 .env 文件加载环境变量"""
    env_file = os.path.expanduser('~/.hermes/.env')
    keys = {}
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys

def generate_openai(prompt: str, size: str = "1024x1024", quality: str = "medium",
                    api_key: str = None, proxy: str = None) -> bytes:
    """通过 OpenAI API 生成图片（需要有效的 API Key + 代理）"""
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    kwargs = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }
    if proxy:
        os.environ["HTTPS_PROXY"] = proxy
        os.environ["HTTP_PROXY"] = proxy
    
    response = client.images.generate(**kwargs)
    
    if response.data[0].b64_json:
        return base64.b64decode(response.data[0].b64_json)
    elif response.data[0].url:
        with urllib.request.urlopen(response.data[0].url) as resp:
            return resp.read()
    raise ValueError("No image data in response")

def generate_fal(prompt: str, size: str = "landscape_4_3", 
                quality: str = "medium", fal_key: str = None) -> bytes:
    """通过 Fal.ai 生成图片"""
    import urllib.request, json
    
    url = "https://fal.run/openai/gpt-image-2"
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "prompt": prompt,
        "image_size": size,
        "quality": quality,
        "num_images": 1,
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    
    img_url = data["images"][0]["url"]
    with urllib.request.urlopen(img_url) as resp:
        return resp.read()

def generate_dashscope(prompt: str, size: str = "1024*1024", 
                       model: str = "wanx2.1-t2i-turbo", api_key: str = None) -> bytes:
    """通过阿里云 Dashscope 通义万相生成图片"""
    import urllib.request, json
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    payload = json.dumps({
        "model": model,
        "input": {"prompt": prompt},
        "parameters": {"size": size, "n": 1},
    }).encode()
    
    # 提交任务
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    if data.get("code") == "InvalidApiKey":
        raise ValueError("Invalid Dashscope API Key")
    
    task_id = data["output"]["task_id"]
    
    # 轮询结果
    poll_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    
    for _ in range(60):  # 最多等 60 秒
        time.sleep(2)
        req = urllib.request.Request(poll_url, headers=poll_headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        
        status = result["output"]["task_status"]
        if status == "SUCCEEDED":
            img_url = result["output"]["results"][0]["url"]
            with urllib.request.urlopen(img_url) as r:
                return r.read()
        elif status == "FAILED":
            raise ValueError(f"Task failed: {result['output'].get('message', 'Unknown error')}")
    
    raise TimeoutError("Image generation timed out")

def generate_openrouter(prompt: str, size: str = "1024x1024",
                        model: str = "openai/gpt-image-2", api_key: str = None,
                        proxy: str = None) -> bytes:
    """通过 OpenRouter 生成图片"""
    import urllib.request, json
    
    url = "https://openrouter.ai/api/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    
    if "data" in data and len(data["data"]) > 0:
        if "b64_json" in data["data"][0]:
            return base64.b64decode(data["data"][0]["b64_json"])
        elif "url" in data["data"][0]:
            with urllib.request.urlopen(data["data"][0]["url"]) as r:
                return r.read()
    raise ValueError(f"No image data: {data}")

BACKENDS = {
    "openai": generate_openai,
    "fal": generate_fal,
    "dashscope": generate_dashscope,
    "openrouter": generate_openrouter,
}

def main():
    parser = argparse.ArgumentParser(description="AI 图片生成工具")
    parser.add_argument("--prompt", "-p", required=True, help="图片描述")
    parser.add_argument("--output", "-o", default="output.png", help="输出文件路径")
    parser.add_argument("--size", "-s", default="1024x1024", help="图片尺寸")
    parser.add_argument("--quality", "-q", default="medium", help="质量: low/medium/high")
    parser.add_argument("--backend", "-b", default="auto", 
                        choices=["auto", "openai", "fal", "dashscope", "openrouter"],
                        help="后端选择")
    parser.add_argument("--batch", help="批量生成：每行一个 prompt 的文件")
    parser.add_argument("--output-dir", default="./images", help="批量输出目录")
    
    args = parser.parse_args()
    env = load_env()
    
    # 自动选择后端
    backend = args.backend
    if backend == "auto":
        if env.get("OPENAI_API_KEY"):
            backend = "openai"
        elif env.get("FAL_KEY"):
            backend = "fal"
        elif env.get("OPENROUTER_API_KEY"):
            backend = "openrouter"
        elif env.get("DASHSCOPE_API_KEY"):
            backend = "dashscope"
        else:
            print("❌ 没有找到任何可用的 API Key！")
            print("请配置以下任一环境变量：")
            print("  - OPENAI_API_KEY (需要代理)")
            print("  - FAL_KEY")
            print("  - OPENROUTER_API_KEY")
            print("  - DASHSCOPE_API_KEY")
            sys.exit(1)
    
    print(f"🎨 使用后端: {backend}")
    print(f"📝 Prompt: {args.prompt[:80]}...")
    
    try:
        if backend == "openai":
            image_data = generate_openai(
                args.prompt, args.size, args.quality,
                api_key=env["OPENAI_API_KEY"],
                proxy="http://127.0.0.1:7890"
            )
        elif backend == "fal":
            image_data = generate_fal(
                args.prompt, args.size, args.quality,
                fal_key=env["FAL_KEY"]
            )
        elif backend == "dashscope":
            image_data = generate_dashscope(
                args.prompt, args.size,
                api_key=env["DASHSCOPE_API_KEY"]
            )
        elif backend == "openrouter":
            image_data = generate_openrouter(
                args.prompt, args.size,
                api_key=env["OPENROUTER_API_KEY"],
                proxy="http://127.0.0.1:7890"
            )
        
        with open(args.output, "wb") as f:
            f.write(image_data)
        
        size_kb = len(image_data) / 1024
        print(f"✅ 图片已保存: {args.output} ({size_kb:.1f} KB)")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
