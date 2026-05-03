#!/usr/bin/env python3
"""
proxy-finder/scripts/test_nodes.py
测试代理节点连通性

用法:
  python3 test_nodes.py --input <订阅文件> --output <结果文件> [--timeout 5] [--max-nodes 20]

输入: Clash YAML 订阅文件或节点列表
输出: 可用节点列表 (JSON)
"""

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def parse_clash_yaml(path):
    """解析 Clash YAML 订阅文件，提取节点列表"""
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    proxies = data.get('proxies', [])
    return proxies


def parse_subscription_links(path):
    """解析订阅链接文件（每行一个 URL）"""
    links = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                links.append(line)
    return links


def download_subscription(url, timeout=15):
    """下载订阅内容"""
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; ProxyFinder/1.0)'
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            return content
    except (URLError, HTTPError, socket.timeout) as e:
        return None


def test_node_tcp(node, timeout=5):
    """TCP 连通性测试"""
    server = node.get('server', '')
    port = node.get('port', 0)
    
    if not server or not port:
        return False, 0
    
    try:
        port = int(port)
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server, port))
        elapsed = (time.time() - start) * 1000  # ms
        sock.close()
        return result == 0, elapsed
    except Exception:
        return False, 0


def test_node_http(node, timeout=5):
    """HTTP 代理测试（通过节点访问 Google generate_204）"""
    server = node.get('server', '')
    port = node.get('port', 0)
    
    if not server or not port:
        return False, 0
    
    try:
        port = int(port)
        start = time.time()
        
        # 使用 curl 通过 SOCKS5/HTTP 代理测试
        proxy_types = [f'socks5://{server}:{port}', f'http://{server}:{port}']
        
        for proxy in proxy_types:
            try:
                result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                     '--connect-timeout', str(timeout),
                     '-x', proxy,
                     'https://www.gstatic.com/generate_204'],
                    capture_output=True, text=True, timeout=timeout + 2
                )
                elapsed = (time.time() - start) * 1000
                if result.stdout.strip() in ('204', '302'):
                    return True, elapsed
            except (subprocess.TimeoutExpired, Exception):
                continue
        
        return False, 0
    except Exception:
        return False, 0


def test_node(node, timeout=5, test_type='tcp'):
    """测试单个节点"""
    name = node.get('name', 'unknown')
    node_type = node.get('type', 'unknown')
    
    if test_type == 'http':
        ok, latency = test_node_http(node, timeout)
    else:
        ok, latency = test_node_tcp(node, timeout)
    
    return {
        'name': name,
        'type': node_type,
        'server': node.get('server', ''),
        'port': node.get('port', 0),
        'ok': ok,
        'latency_ms': round(latency, 1),
        'raw': node
    }


def main():
    parser = argparse.ArgumentParser(description='测试代理节点连通性')
    parser.add_argument('--input', required=True, help='订阅文件或链接列表')
    parser.add_argument('--output', default='/tmp/proxy-test-results.json', help='输出文件')
    parser.add_argument('--timeout', type=int, default=5, help='超时秒数')
    parser.add_argument('--max-nodes', type=int, default=50, help='最大测试节点数')
    parser.add_argument('--test-type', choices=['tcp', 'http'], default='tcp', help='测试类型')
    parser.add_argument('--workers', type=int, default=10, help='并发数')
    args = parser.parse_args()
    
    # 解析输入
    if args.input.startswith('http'):
        print(f"📥 下载订阅: {args.input}")
        content = download_subscription(args.input)
        if not content:
            print("❌ 下载失败")
            sys.exit(1)
        data = yaml.safe_load(content)
        nodes = data.get('proxies', [])
    else:
        ext = os.path.splitext(args.input)[1].lower()
        if ext in ('.yaml', '.yml'):
            nodes = parse_clash_yaml(args.input)
        else:
            nodes = parse_subscription_links(args.input)
    
    total = min(len(nodes), args.max_nodes)
    print(f"🔍 找到 {len(nodes)} 个节点，测试前 {total} 个...")
    
    # 并发测试
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for node in nodes[:total]:
            future = executor.submit(test_node, node, args.timeout, args.test_type)
            futures[future] = node.get('name', 'unknown')
        
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            status = "✅" if result['ok'] else "❌"
            latency = f"{result['latency_ms']:.0f}ms" if result['ok'] else "超时"
            print(f"  [{done}/{total}] {status} {result['name']} ({result['type']}) - {latency}")
            results.append(result)
    
    # 排序：可用节点在前，按延迟排序
    available = [r for r in results if r['ok']]
    unavailable = [r for r in results if not r['ok']]
    available.sort(key=lambda x: x['latency_ms'])
    
    sorted_results = available + unavailable
    
    # 输出结果
    output = {
        'total': len(results),
        'available': len(available),
        'unavailable': len(unavailable),
        'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': sorted_results
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 结果: {len(available)}/{len(results)} 个节点可用")
    print(f"📄 结果保存到: {args.output}")
    
    # 打印可用节点摘要
    if available:
        print("\n🏆 可用节点 (按延迟排序):")
        for r in available[:10]:
            print(f"  {r['name']} ({r['type']}) - {r['latency_ms']:.0f}ms")


if __name__ == '__main__':
    main()
