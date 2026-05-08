#!/usr/bin/env python3
"""
Fallback Search — 搜索策略备选工具
当 Tavily MCP 不可用时，自动降级到备选搜索源
支持：DuckDuckGo (免费无Key) / 直接HTTP抓取

用法:
  python3 fallback_search.py "查询关键词" [--limit 5]
  python3 fallback_search.py "site:github.com gemini api" --source duckduckgo

策略:
  1️⃣ DuckDuckGo — 免费，无需 API Key
  2️⃣ Direct HTTP — 直接抓取搜索引擎结果
"""

import os, sys, json, argparse, re
from urllib.parse import quote_plus

# 尝试导入 duckduckgo_search
try:
    from duckduckgo_search import DDGS
    HAVE_DDG = True
except ImportError:
    HAVE_DDG = False


def search_duckduckgo(query, limit=5, timeout=15):
    """使用 DuckDuckGo 搜索"""
    if not HAVE_DDG:
        return {"error": "duckduckgo_search 未安装"}

    try:
        results = []
        with DDGS(timeout=timeout) as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=limit)):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "description": r.get("body", ""),
                })
                if len(results) >= limit:
                    break

        return {"results": results, "source": "duckduckgo", "count": len(results)}
    except Exception as e:
        return {"error": f"DuckDuckGo 搜索失败: {e}"}


def search_direct(query, limit=5, timeout=15):
    """直接通过 HTTP 抓取搜索（备选备选）"""
    import httpx

    # 先尝试 DuckDuckGo 的 HTML 版
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/131.0.0.0 Safari/537.36"
    }

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)

        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}

        # 简单提取结果
        import lxml.html
        tree = lxml.html.fromstring(resp.text)
        results = []

        for result in tree.cssselect(".result"):
            title_el = result.cssselect(".result__title a")
            snippet_el = result.cssselect(".result__snippet")

            if title_el:
                title = title_el[0].text_content().strip()
                url = title_el[0].get("href", "")
                # DuckDuckGo 的 URL 是重定向链接
                if "uddg=" in url:
                    url = url.split("uddg=")[-1].split("&")[0]
                    from urllib.parse import unquote
                    url = unquote(url)
                snippet = snippet_el[0].text_content().strip() if snippet_el else ""

                results.append({"title": title, "url": url, "description": snippet})

                if len(results) >= limit:
                    break

        return {"results": results, "source": "direct", "count": len(results)}

    except Exception as e:
        return {"error": f"Direct 搜索失败: {e}"}


def search(query, limit=5, source="auto", timeout=15):
    """搜索入口：自动选择最佳可用源"""
    if source == "auto":
        # 先尝试 DuckDuckGo
        if HAVE_DDG:
            result = search_duckduckgo(query, limit, timeout)
            if "error" not in result and result.get("count", 0) > 0:
                return result
        # 降级到 direct
        return search_direct(query, limit, timeout)
    elif source == "duckduckgo":
        return search_duckduckgo(query, limit, timeout)
    elif source == "direct":
        return search_direct(query, limit, timeout)
    else:
        return {"error": f"未知搜索源: {source}"}


def main():
    parser = argparse.ArgumentParser(description="搜索备选工具 - Tavily 降级方案")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--limit", "-l", type=int, default=5, help="结果数量 (默认: 5)")
    parser.add_argument("--source", "-s", default="auto",
                        choices=["auto", "duckduckgo", "direct"],
                        help="搜索源 (默认: auto，自动选择)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    result = search(args.query, args.limit, args.source)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"🔍 搜索: {args.query}")
    print(f"📡 来源: {result['source']} | 结果: {result['count']}条")
    print(f"{'='*50}\n")

    for i, r in enumerate(result.get("results", []), 1):
        print(f"{i}. {r['title']}")
        print(f"   🔗 {r.get('url', '')[:100]}")
        desc = r.get('description', '')
        if desc:
            print(f"   💬 {desc[:150]}")
        print()

    print(f"{'='*50}")
    print(f"💡 提示: 用 --json 输出 JSON 格式供程序调用")


if __name__ == "__main__":
    main()
