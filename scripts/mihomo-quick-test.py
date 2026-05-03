#!/usr/bin/env python3
"""快速测试 mihomo 节点连通性"""

import yaml, socket, time, concurrent.futures, json, sys, os
from collections import defaultdict

def test_tcp(server, port, timeout=5):
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server, port))
        sock.close()
        latency = (time.time() - start) * 1000
        return result == 0, latency
    except:
        return False, 0

def main():
    config_path = os.path.expanduser("~/.config/mihomo/config.yaml")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    proxies = config.get('proxies', [])
    print(f"📋 测试 {len(proxies)} 个节点...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {}
        for p in proxies:
            if 'server' in p and 'port' in p:
                f = executor.submit(test_tcp, p['server'], int(p['port']))
                futures[f] = p
        
        for f in concurrent.futures.as_completed(futures):
            p = futures[f]
            ok, latency = f.result()
            results.append({
                'name': p.get('name', '?'),
                'type': p.get('type', '?'),
                'server': p['server'],
                'port': p['port'],
                'ok': ok,
                'latency_ms': round(latency, 1) if ok else None
            })
    
    ok = sorted([r for r in results if r['ok']], key=lambda x: x['latency_ms'])
    fail = [r for r in results if not r['ok']]
    
    print(f"\n✅ 可用: {len(ok)} | ❌ 不可用: {len(fail)}")
    
    if ok:
        print(f"\n--- 可用节点（按延迟排序）---")
        for r in ok:
            flag = "🟢" if r['latency_ms'] < 100 else "🟡" if r['latency_ms'] < 300 else "🔴"
            print(f"  {flag} {r['latency_ms']:7.1f}ms | {r['type']:8s} | {r['name']}")
    
    if fail:
        print(f"\n--- 不可用节点 ---")
        for r in fail:
            print(f"  ❌ {r['type']:8s} | {r['name']}")
    
    # 按协议分组
    by_type = defaultdict(list)
    for r in ok:
        by_type[r['type']].append(r)
    print(f"\n--- 按协议分组 ---")
    for t, ns in sorted(by_type.items()):
        avg = sum(n['latency_ms'] for n in ns) / len(ns)
        print(f"  {t}: {len(ns)} 个可用，平均延迟 {avg:.0f}ms")
    
    # 保存结果
    with open('/tmp/proxy-quick-test.json', 'w') as f:
        json.dump({'ok': ok, 'fail': fail, 'time': time.strftime('%Y-%m-%d %H:%M:%S')}, 
                  f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到 /tmp/proxy-quick-test.json")

if __name__ == '__main__':
    main()
