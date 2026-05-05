#!/usr/bin/env python3
"""
Web Search Gatekeeper - 强制搜索门禁

防止 Agent 跳过搜索步骤。当搜索失败时，必须尝试所有可用方案，
直到找到结果或确认所有方案都不可用。

使用方式：
    from hermes_tools import terminal
    result = terminal("python3 ~/.hermes/scripts/web_search_gatekeeper.py '搜索关键词'")
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 搜索方案优先级
SEARCH_METHODS = [
    {
        "name": "tavily_mcp",
        "description": "Tavily MCP（需要 MCP server 运行）",
        "check": "检查 MCP server 是否响应",
        "execute": "使用 mcp_tavily_tavily_search",
    },
    {
        "name": "web_search_builtin",
        "description": "原生 web_search 工具",
        "check": "检查 API key 是否存在",
        "execute": "使用 web_search",
    },
    {
        "name": "brave_mcp",
        "description": "Brave Search MCP",
        "check": "检查 BRAVE_API_KEY 和 MCP 配置",
        "execute": "使用 Brave MCP",
    },
    {
        "name": "curl_with_proxy",
        "description": "curl + 代理（最底保底）",
        "check": "检查代理端口",
        "execute": "curl -x http://127.0.0.1:7890 https://www.google.com/search?q=...",
    },
    {
        "name": "browser_cdp",
        "description": "Chrome CDP（浏览器保底）",
        "check": "检查 Chrome CDP 端口",
        "execute": "browser_navigate + browser_snapshot",
    },
]

# 代理端口（mihomo）
PROXY_PORT = 7890

# Chrome CDP 端口
CDP_PORT = 9222


def check_proxy() -> bool:
    """检查代理是否可用"""
    try:
        import requests
        r = requests.get("https://www.google.com", 
                        proxies={"http": f"http://127.0.0.1:{PROXY_PORT}",
                                 "https": f"http://127.0.0.1:{PROXY_PORT}"},
                        timeout=5)
        return r.status_code == 200
    except:
        return False


def check_cdp() -> bool:
    """检查 Chrome CDP 是否可用"""
    try:
        import requests
        r = requests.get(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=3)
        return r.status_code == 200 and "webSocketDebuggerUrl" in r.json()
    except:
        return False


def check_tavily_api_key() -> bool:
    """检查 Tavily API Key"""
    # 方法 1: 直接检查环境变量
    if os.getenv("TAVILY_API_KEY"):
        return True
    
    # 方法 2: 从 ~/.hermes/.env 文件读取
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("TAVILY_API_KEY="):
                    val = line.split("=", 1)[1]
                    if val and not val.startswith("#"):
                        return True
    
    # 方法 3: 检查 config.yaml
    config_path = Path.home() / ".hermes" / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        # 检查 MCP servers
        mcp_servers = config.get("mcp_servers", {})
        for name, server in mcp_servers.items():
            if "tavily" in name.lower():
                env_vars = server.get("env", {})
                if "TAVILY_API_KEY" in env_vars:
                    key = env_vars["TAVILY_API_KEY"]
                    if key and not key.startswith("${"):
                        return True
    return False


def check_api_key_from_env(env_var: str) -> bool:
    """从环境变量或 .env 文件检查 API Key"""
    # 方法 1: 直接检查环境变量
    if os.getenv(env_var):
        return True
    
    # 方法 2: 从 ~/.hermes/.env 文件读取
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{env_var}="):
                    val = line.split("=", 1)[1]
                    if val and not val.startswith("#"):
                        return True
    return False


def start_chrome_cdp() -> bool:
    """启动 Chrome headless CDP"""
    try:
        # 检查是否已运行
        if check_cdp():
            return True
        
        # 启动 Chrome
        subprocess.Popen([
            "google-chrome",
            "--headless",
            "--disable-gpu",
            f"--remote-debugging-port={CDP_PORT}",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待启动
        time.sleep(3)
        return check_cdp()
    except:
        return False


def curl_search(query: str) -> dict:
    """使用 curl + 代理搜索"""
    import requests
    
    # DuckDuckGo HTML 版本（不需要 API key）
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        r = requests.get(url,
                        proxies={"http": f"http://127.0.0.1:{PROXY_PORT}",
                                 "https": f"http://127.0.0.1:{PROXY_PORT}"},
                        timeout=30)
        
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "method": "curl_with_proxy"}
        
        # 解析 HTML 提取结果
        import re
        results = []
        
        # DuckDuckGo HTML 格式
        for match in re.finditer(r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>', r.text):
            url = match.group(1)
            title = match.group(2)
            results.append({"title": title, "url": url})
        
        if not results:
            return {"error": "No results found", "method": "curl_with_proxy"}
        
        return {
            "success": True,
            "method": "curl_with_proxy",
            "results": results[:5],
            "total": len(results),
        }
    except Exception as e:
        return {"error": str(e), "method": "curl_with_proxy"}


def get_available_methods() -> list:
    """获取所有可用的搜索方法"""
    available = []
    
    # 1. 检查 Tavily API Key
    if check_tavily_api_key():
        available.append({
            "name": "tavily",
            "available": True,
            "reason": "API key 存在",
            "priority": 1,
        })
    else:
        available.append({
            "name": "tavily",
            "available": False,
            "reason": "无 API key",
            "priority": 1,
        })
    
    # 2. 检查 Firecrawl API Key
    if check_api_key_from_env("FIRECRAWL_API_KEY"):
        available.append({
            "name": "firecrawl",
            "available": True,
            "reason": "API key 存在 (.env)",
            "priority": 2,
        })
    else:
        available.append({
            "name": "firecrawl",
            "available": False,
            "reason": "无 API key",
            "priority": 2,
        })
    
    # 3. 检查 Exa API Key
    if check_api_key_from_env("EXA_API_KEY"):
        available.append({
            "name": "exa",
            "available": True,
            "reason": "API key 存在 (.env)",
            "priority": 2,
        })
    else:
        available.append({
            "name": "exa",
            "available": False,
            "reason": "无 API key",
            "priority": 2,
        })
    
    # 4. 检查代理
    if check_proxy():
        available.append({
            "name": "curl_with_proxy",
            "available": True,
            "reason": f"代理端口 {PROXY_PORT} 可用",
            "priority": 3,
        })
    else:
        available.append({
            "name": "curl_with_proxy",
            "available": False,
            "reason": f"代理端口 {PROXY_PORT} 不可用",
            "priority": 3,
        })
    
    # 5. 检查 CDP
    if check_cdp():
        available.append({
            "name": "browser_cdp",
            "available": True,
            "reason": f"Chrome CDP 端口 {CDP_PORT} 可用",
            "priority": 4,
        })
    else:
        # 尝试启动
        if start_chrome_cdp():
            available.append({
                "name": "browser_cdp",
                "available": True,
                "reason": f"Chrome CDP 已自动启动",
                "priority": 4,
            })
        else:
            available.append({
                "name": "browser_cdp",
                "available": False,
                "reason": "Chrome CDP 不可用",
                "priority": 4,
            })
    
    return sorted(available, key=lambda x: x["priority"])


def print_gatekeeper_status():
    """打印门禁状态"""
    methods = get_available_methods()
    
    print("=" * 50)
    print("Web Search Gatekeeper Status")
    print("=" * 50)
    print()
    
    print("🔍 可用搜索方法：")
    for m in methods:
        status_icon = "✅" if m["available"] else "❌"
        print(f"  {status_icon} {m['name']} (优先级: {m['priority']})")
        print(f"      └─ {m['reason']}")
    
    print()
    
    available_count = sum(1 for m in methods if m["available"])
    if available_count == 0:
        print("⚠️  所有搜索方法都不可用！")
        print("   Agent 不能跳过搜索，必须报告给用户。")
        print()
        print("   建议：")
        print("   1. 检查代理配置（mihomo 端口 7890）")
        print("      → 加载 clash-config skill 修复代理")
        print("   2. 启动 Chrome CDP（端口 9222）")
        print("   3. 配置 Tavily/Brave API key")
    else:
        print(f"✅ 有 {available_count} 种搜索方法可用")
        print("   Agent 必须尝试至少一种方法，不能跳过搜索！")
    
    print()
    print("=" * 50)
    print()
    print("📌 相关 Skill 引用：")
    print("   - clash-config：代理配置管理（mihomo 端口 7890）")
    print("   - web-access：联网操作统一入口")


def main():
    parser = argparse.ArgumentParser(description="Web Search Gatekeeper")
    parser.add_argument("query", nargs="?", help="搜索关键词")
    parser.add_argument("--status", action="store_true", help="仅显示门禁状态")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--force-curl", action="store_true", help="强制使用 curl 保底")
    
    args = parser.parse_args()
    
    if args.status:
        print_gatekeeper_status()
        return
    
    if args.force_curl and args.query:
        result = curl_search(args.query)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if result.get("success"):
                print(f"✅ 使用 curl + 代理搜索成功喵！")
                for r in result["results"]:
                    print(f"  - {r['title']}: {r['url']}")
            else:
                print(f"❌ 搜索失败：{result.get('error')}")
        return
    
    if args.query:
        methods = get_available_methods()
        
        # 找到第一个可用方法
        for m in methods:
            if m["available"]:
                if m["name"] == "curl_with_proxy":
                    result = curl_search(args.query)
                    if args.json:
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                    else:
                        if result.get("success"):
                            print(f"✅ 使用 {m['name']} 搜索成功喵！")
                            for r in result["results"]:
                                print(f"  - {r['title']}: {r['url']}")
                        else:
                            print(f"❌ 搜索失败：{result.get('error')}")
                    return
                else:
                    # 其他方法需要 Agent 自己调用
                    print(f"💡 建议使用 {m['name']} 搜索喵！")
                    print(f"   query: {args.query}")
                    return
        
        # 没有可用方法
        print("⚠️  所有搜索方法都不可用！")
        print("   请检查代理、CDP 或 API key 配置。")
    else:
        print_gatekeeper_status()


if __name__ == "__main__":
    main()