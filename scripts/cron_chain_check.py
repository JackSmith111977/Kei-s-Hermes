#!/usr/bin/env python3
"""
Cron 链步骤2的预处理脚本
读取步骤1的新闻数据，准备报告模板
"""
import json, os, sys

step1_file = "/tmp/cron_chain_step1.json"

if not os.path.exists(step1_file):
    print("ERROR: /tmp/cron_chain_step1.json not found. Step 1 may have failed.")
    sys.exit(1)

with open(step1_file) as f:
    data = json.load(f)

news = data.get("news", [])
print(f"STATUS: ok")
print(f"NEWS_COUNT: {len(news)}")
print(f"COLLECTED_AT: {data.get('collected_at', 'unknown')}")
print("---NEWS---")
for i, n in enumerate(news):
    print(f"{i+1}. [{n.get('source','?')}] {n.get('title','?')}")
    print(f"   URL: {n.get('url','?')}")
    print(f"   摘要: {n.get('summary','?')[:100]}")
