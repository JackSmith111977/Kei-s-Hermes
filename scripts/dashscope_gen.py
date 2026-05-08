#!/usr/bin/env python3
"""
Dashscope Image Gen — 生图工具
使用阿里云 Dashscope (通义万相) 生成图片
支持多种模型、尺寸、风格

用法:
  python3 dashscope_gen.py "一只可爱的猫娘女仆" --output ~/output.png
  python3 dashscope_gen.py "A cute catgirl" --model wanx2.7-t2i-turbo --size 1920*1080

模型选择:
  wanx2.1-t2i-turbo   — 快速生成（免费额度可用）✅ 默认
  wanx2.7-t2i-turbo   — 更高质量
"""

import os, sys, json, time, argparse
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

API_KEY = os.environ.get("DASHSCOPE_IMAGE_API_KEY", "")
DEFAULT_MODEL = "wanx2.1-t2i-turbo"
DEFAULT_SIZE = "1024*1024"

# 尺寸映射
SIZE_MAP = {
    "1:1": "1024*1024", "16:9": "1920*1080", "9:16": "720*1280",
    "3:4": "768*1024", "4:3": "1024*768",
}


def generate_image(prompt, model=DEFAULT_MODEL, size=DEFAULT_SIZE, n=1, max_wait=60):
    """调用 Dashscope API 生成图片"""
    import httpx

    # 处理尺寸
    if size in SIZE_MAP:
        size = SIZE_MAP[size]
    if 'x' in size:
        size = size.replace('x', '*')

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }

    payload = {
        "model": model,
        "input": {"prompt": prompt},
        "parameters": {"size": size, "n": n}
    }

    # Dashscope 国内不需要代理
    with httpx.Client(timeout=30) as client:
        # 提交任务
        resp = client.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
            headers=headers, json=payload
        )
        if resp.status_code != 200:
            return {"error": f"提交失败 {resp.status_code}: {resp.text[:300]}"}

        task_id = resp.json()["output"]["task_id"]
        print(f"📤 已提交任务: {task_id}", file=sys.stderr)

        # 轮询结果
        status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        for i in range(max_wait // 3):
            time.sleep(3)
            status_resp = client.get(status_url, headers={"Authorization": f"Bearer {API_KEY}"})
            status_data = status_resp.json()
            status = status_data["output"]["task_status"]
            print(f"⏳ 第 {i+1} 次轮询: {status}", file=sys.stderr)

            if status == "SUCCEEDED":
                results = status_data["output"]["results"]
                images = []
                for r in results:
                    img_url = r["url"]
                    img_resp = client.get(img_url)
                    images.append({"url": img_url, "data": img_resp.content})
                return {"images": images, "task_id": task_id, "model": model}

            elif status == "FAILED":
                return {"error": f"生成失败: {json.dumps(status_data, ensure_ascii=False)}"}

        return {"error": f"等待超时 ({max_wait}s)"}


def main():
    parser = argparse.ArgumentParser(description="Dashscope 通义万相 - 生图工具")
    parser.add_argument("prompt", help="图片描述提示词")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"尺寸 (默认: {DEFAULT_SIZE}, 支持 1:1/16:9/9:16)")
    parser.add_argument("--n", type=int, default=1, help="生成数量 (默认: 1)")
    parser.add_argument("--output", "-o", default="", help="保存路径（默认自动生成）")
    parser.add_argument("--wait", type=int, default=60, help="最大等待秒数 (默认: 60)")
    args = parser.parse_args()

    if not API_KEY:
        print("❌ 错误: 未设置 DASHSCOPE_IMAGE_API_KEY 环境变量")
        sys.exit(1)

    print(f"🎨 生图提示: {args.prompt}", file=sys.stderr)
    print(f"🤖 模型: {args.model}", file=sys.stderr)

    result = generate_image(args.prompt, args.model, args.size, args.n, args.wait)

    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)

    # 保存图片
    output_dir = Path.home() / ".hermes" / "image_cache"
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for i, img in enumerate(result["images"]):
        if args.output:
            path = Path(args.output)
        else:
            path = output_dir / f"dashscope_{int(time.time())}_{i}.png"

        path.write_bytes(img["data"])
        saved.append(str(path))
        print(f"✅ 图片已保存: {path}", file=sys.stderr)

    # 输出 JSON 供脚本链式调用
    print(json.dumps({
        "status": "success",
        "images": saved,
        "task_id": result["task_id"],
        "model": result["model"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
