#!/usr/bin/env python3
"""TinyFish Search & Fetch CLI — 搜索与网页抓取工具

搜索（免费，不限次数，仅限速 5次/分钟）：
    python3 tinyfish_search.py search "query" [--location US] [--language en] [--page 0]

抓取（免费，不限次数）：
    python3 tinyfish_search.py fetch <url1> [url2 ...] [--format markdown]

环境变量：TINYFISH_API_KEY（必填，从 ~/.hermes/.env 自动加载）

使用文档：详见 web-access skill 的 references/search-providers.md
"""

import json
import os
import sys
import urllib.parse
import urllib.request

# 从 .env 加载 API Key
ENV_PATH = os.path.expanduser("~/.hermes/.env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("TINYFISH_API_KEY="):
                os.environ.setdefault("TINYFISH_API_KEY", line.split("=", 1)[1].strip().strip('"').strip("'"))

API_KEY = os.environ.get("TINYFISH_API_KEY", "")

if not API_KEY:
    print("❌ TINYFISH_API_KEY not set. Add to ~/.hermes/.env or export it.")
    sys.exit(1)


def search(query: str, location: str = "US", language: str = "en", page: int = 0) -> dict:
    """TinyFish Search API — 完全免费，不限次数"""
    params = {
        "query": query,
        "location": location,
        "language": language,
        "page": str(page),
    }
    url = "https://api.search.tinyfish.ai?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-API-Key": API_KEY})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch(urls: list[str], fmt: str = "markdown") -> dict:
    """TinyFish Fetch API — 完全免费，不限次数"""
    payload = json.dumps({"urls": urls, "format": fmt}).encode()
    req = urllib.request.Request(
        "https://api.fetch.tinyfish.ai",
        data=payload,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    mode = args[0]

    if mode == "search":
        query = args[1] if len(args) > 1 else None
        if not query:
            print('❌ Usage: tinyfish_search.py search "query" [--location US] [--language en] [--page 0]')
            sys.exit(1)

        kwargs = {}
        if "--location" in args:
            kwargs["location"] = args[args.index("--location") + 1]
        if "--language" in args:
            kwargs["language"] = args[args.index("--language") + 1]
        if "--page" in args:
            kwargs["page"] = int(args[args.index("--page") + 1])

        result = search(query, **kwargs)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        total = result.get("total_results", len(result.get("results", [])))
        print(f"\n📊 共 {total} 条结果", file=sys.stderr)

    elif mode == "fetch":
        urls = []
        fmt = "markdown"
        i = 1
        while i < len(args):
            if args[i] == "--format":
                i += 1
                fmt = args[i] if i < len(args) else "markdown"
            elif args[i].startswith("http"):
                urls.append(args[i])
            i += 1

        if not urls:
            print("❌ Usage: tinyfish_search.py fetch <url1> [url2 ...] [--format markdown|json|html]")
            sys.exit(1)

        result = fetch(urls, fmt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        success = len([r for r in result.get("results", []) if r.get("text")])
        errors = len(result.get("errors", []))
        print(f"\n📊 成功: {success} 页, 失败: {errors}", file=sys.stderr)
    else:
        print(f"❌ 未知模式: {mode}. 使用 'search' 或 'fetch'")
        sys.exit(1)


if __name__ == "__main__":
    main()
