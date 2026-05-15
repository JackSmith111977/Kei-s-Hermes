#!/usr/bin/env python3
"""
skill_finder.py - Agent Skill 优先发现雷达
用法:
  python3 ~/.hermes/skills/learning-workflow/scripts/skill_finder.py "我想画个架构图"
  
原理：
  扫描所有 SKILL.md 的元数据，根据 Query 进行关键词/Trigger 匹配打分。
  输出最相关的 Skill 列表。
"""

import os
import sys
import glob
import yaml

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")

def load_skill_meta(skill_path):
    """Load YAML frontmatter from SKILL.md"""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        try:
            # Simple extraction of first yaml block
            parts = content.split('---', 2)
            if len(parts) >= 2:
                return yaml.safe_load(parts[1])
        except:
            pass
    return {}

def score_skill(query, meta):
    """Score a skill based on query relevance"""
    query_lower = query.lower()
    score = 0
    
    # 1. Check Name (Weight 20)
    if meta.get('name', '').lower() in query_lower:
        score += 20
    
    # 2. Check Description (Weight 10)
    desc = meta.get('description', '').lower()
    # Simple keyword matching (split query into words)
    query_words = query_lower.split()
    for word in query_words:
        if len(word) > 1 and word in desc:
            score += 5
            
    # 3. Check Triggers (Weight 50 - Highest Priority)
    triggers = meta.get('triggers', [])
    for trigger in triggers:
        # Handle both string triggers and dict triggers (e.g. {'task': 'deploy'})
        if isinstance(trigger, dict):
            for v in trigger.values():
                if isinstance(v, str) and (v.lower() in query_lower or query_lower in v.lower()):
                    score += 50
        elif isinstance(trigger, str):
            if trigger.lower() in query_lower or query_lower in trigger.lower():
                score += 50
            
    return score

def main():
    if len(sys.argv) < 2:
        print("Usage: skill_finder.py 'query'")
        sys.exit(1)
        
    query = sys.argv[1]
    results = []
    
    # Scan all skills
    sk_files = glob.glob(os.path.join(SKILLS_DIR, '**/SKILL.md'), recursive=True)
    
    for f in sk_files:
        meta = load_skill_meta(f)
        if meta:
            s = score_skill(query, meta)
            if s > 0:
                results.append({
                    'score': s,
                    'name': meta.get('name', 'Unknown'),
                    'desc': meta.get('description', 'No description'),
                    'path': f
                })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Print top 5
    print(f"🔍 扫描到 {len(results)} 个相关 Skill，为您列出 Top 5：\n")
    
    found_good_match = False
    for i, r in enumerate(results[:5]):
        icon = "✅" if r['score'] >= 30 else "💡"
        print(f"{i+1}. {icon} {r['name']} (匹配度：{r['score']})")
        print(f"   📄 {r['desc']}")
        print(f"   📂 路径：{r['path']}")
        print()
        if r['score'] >= 30: found_good_match = True

    if not found_good_match:
        print("⚠️ 未找到高匹配度 Skill，建议自由发挥或联网搜索。")

if __name__ == "__main__":
    main()
