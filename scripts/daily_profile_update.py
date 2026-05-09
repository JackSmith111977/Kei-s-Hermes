#!/usr/bin/env python3
"""
每日全貌更新辅助脚本
收集今日更新的数据，供 agent 更新飞书文档
"""
import json, os, datetime

# Get today's date
today = datetime.date.today().isoformat()
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

# Read current profile
profile_path = os.path.expanduser('~/.hermes/docs/emma-full-profile.md')
current_content = ""
if os.path.exists(profile_path):
    with open(profile_path) as f:
        current_content = f.read()

# Read Feishu doc info
doc_info = {}
doc_path = '/tmp/emma_feishu_doc.json'
if os.path.exists(doc_path):
    with open(doc_path) as f:
        doc_info = json.load(f)

output = {
    'date': today,
    'yesterday': yesterday,
    'profile_exists': os.path.exists(profile_path),
    'profile_size': len(current_content),
    'feishu_doc_id': doc_info.get('doc_id', ''),
    'feishu_has_token': 'token' in doc_info,
    'updates_found': False,
    'daily_updates': []
}

# Check for changelog section in profile
if current_content:
    if '## 九、演进日志' in current_content:
        output['has_changelog'] = True
    if '## 八、当前状态' in current_content:
        output['has_status'] = True

print(json.dumps(output, ensure_ascii=False))
