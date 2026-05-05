#!/usr/bin/env python3
"""
Web Backend Status Checker

检查 web-search 工具的后端状态，确定哪个 backend 可用。

用法：
    python ~/.hermes/scripts/web_backend_status.py
    python ~/.hermes/scripts/web_backend_status.py --switch firecrawl  # 切换 backend
"""

import argparse
import os
import sys
from pathlib import Path

# 添加 Hermes Agent 路径
HERMES_AGENT_PATH = Path.home() / ".hermes" / "hermes-agent"
sys.path.insert(0, str(HERMES_AGENT_PATH))

try:
    from hermes_cli.config import load_config
except ImportError:
    # 简化版本：直接读取 YAML
    import yaml
    def load_config():
        config_path = Path.home() / ".hermes" / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

# Backend 检测函数
def check_api_key(env_var: str) -> bool:
    """检查环境变量中是否有 API key"""
    # 方法 1: 直接检查环境变量
    val = os.getenv(env_var)
    if val and val.strip():
        return True
    
    # 方法 2: 从 ~/.hermes/.env 文件读取
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{env_var}="):
                    val = line.split("=", 1)[1]
                    if val and not val.startswith("#"):
                        return True
    
    return False

def check_config_key(config_path: str, key_name: str) -> bool:
    """检查 config.yaml 中是否有 API key"""
    config = load_config()
    
    # 尝试在多个位置查找
    # 1. mcp_servers.{backend}.env.{key}
    # 2. 直接在环境变量引用
    
    # 检查 MCP servers 配置
    mcp_servers = config.get("mcp_servers", {})
    for server_name, server_config in mcp_servers.items():
        env_vars = server_config.get("env", {})
        if key_name in env_vars:
            val = env_vars[key_name]
            if val and not val.startswith("${"):  # 不是环境变量引用
                return True
    
    return False

def get_backend_status() -> dict:
    """获取所有 backend 的状态"""
    backends = {
        "tavily": {
            "env_var": "TAVILY_API_KEY",
            "config_key": "TAVILY_API_KEY",
            "mcp_server": "tavily",
            "free_quota": "1,000 credits/月",
            "status": "unknown",
        },
        "firecrawl": {
            "env_var": "FIRECRAWL_API_KEY",
            "config_key": "FIRECRAWL_API_KEY",
            "mcp_server": None,  # 无 MCP
            "free_quota": "500 credits (一次性)",
            "status": "unknown",
        },
        "exa": {
            "env_var": "EXA_API_KEY",
            "config_key": "EXA_API_KEY",
            "mcp_server": None,
            "free_quota": "1,000 credits/月",
            "status": "unknown",
        },
        "parallel": {
            "env_var": "PARALLEL_API_KEY",
            "config_key": "PARALLEL_API_KEY",
            "mcp_server": None,
            "free_quota": "有限免费",
            "status": "unknown",
        },
        "brave": {
            "env_var": "BRAVE_API_KEY",
            "config_key": "BRAVE_API_KEY",
            "mcp_server": "brave",
            "free_quota": "2,000 次/月",
            "status": "unknown",
        },
    }
    
    for backend, info in backends.items():
        has_env = check_api_key(info["env_var"])
        has_config = check_config_key(info["config_key"], info["config_key"])
        
        if has_env or has_config:
            info["status"] = "available"
        else:
            info["status"] = "no_key"
    
    # 检查 MCP server 状态
    mcp_servers = load_config().get("mcp_servers", {})
    for backend, info in backends.items():
        if info["mcp_server"] and info["mcp_server"] in mcp_servers:
            info["mcp_configured"] = True
        else:
            info["mcp_configured"] = False
    
    # 检查当前 backend
    config = load_config()
    current_backend = config.get("web", {}).get("backend", "tavily")
    
    return {
        "current_backend": current_backend,
        "backends": backends,
    }

def switch_backend(new_backend: str) -> bool:
    """切换 backend（修改 config.yaml）"""
    import yaml
    
    config_path = Path.home() / ".hermes" / "config.yaml"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    # 读取当前配置
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # 检查新 backend 是否可用
    status = get_backend_status()
    backend_info = status["backends"].get(new_backend)
    
    if not backend_info:
        print(f"❌ Unknown backend: {new_backend}")
        return False
    
    if backend_info["status"] != "available":
        print(f"⚠️  Backend {new_backend} has no API key configured")
        print(f"   Please configure {backend_info['env_var']} first")
        return False
    
    # 修改配置
    if "web" not in config:
        config["web"] = {}
    
    old_backend = config["web"].get("backend", "unknown")
    config["web"]["backend"] = new_backend
    
    # 写回配置
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Switched backend: {old_backend} → {new_backend}")
    return True

def print_status_report(status: dict):
    """打印状态报告"""
    print("=" * 50)
    print("Web Backend Status Report")
    print("=" * 50)
    print()
    
    print(f"📍 当前 Backend: {status['current_backend']}")
    print()
    
    print("📊 Backend 可用性：")
    for backend, info in status["backends"].items():
        status_icon = "✅" if info["status"] == "available" else "❌"
        mcp_icon = "🔗" if info.get("mcp_configured") else "  "
        current_icon = "🔵" if backend == status["current_backend"] else "  "
        
        print(f"  {current_icon} {status_icon} {mcp_icon} {backend}")
        print(f"      ├─ API Key: {info['status']}")
        print(f"      ├─ MCP: {info.get('mcp_configured', False)}")
        print(f"      └─ 免费额度: {info['free_quota']}")
    
    print()
    print("=" * 50)
    
    # 建议
    available_backends = [b for b, i in status["backends"].items() if i["status"] == "available"]
    
    if not available_backends:
        print("⚠️  所有 backend 都没有 API key！")
        print("   建议配置：")
        print("   1. Tavily: https://tavily.com (1,000 credits/月)")
        print("   2. Brave Search: https://brave.com/search/api/ (2,000 次/月)")
        print("   3. Firecrawl: https://firecrawl.dev (500 credits)")
    elif status["current_backend"] not in available_backends:
        print(f"⚠️  当前 backend '{status['current_backend']}' 不可用！")
        print(f"   建议切换到: {available_backends[0]}")
        print(f"   命令: python3 ~/.hermes/scripts/web_backend_status.py --switch {available_backends[0]}")
    else:
        print(f"✅ 当前 backend '{status['current_backend']}' 可用")

def main():
    parser = argparse.ArgumentParser(description="Web Backend Status Checker")
    parser.add_argument("--switch", type=str, help="切换到指定 backend")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    if args.switch:
        success = switch_backend(args.switch)
        if success:
            status = get_backend_status()
            print_status_report(status)
    else:
        status = get_backend_status()
        
        if args.json:
            import json
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print_status_report(status)

if __name__ == "__main__":
    main()