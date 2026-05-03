#!/usr/bin/env python3
"""
Skill 依赖扫描器 (Dependency Scanner) v1.0
扫描所有 Skill 的 YAML Frontmatter，构建依赖关系图谱。
输出：依赖关系表格 + 断裂引用警告 + 建议操作。
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")

def parse_yaml_frontmatter(filepath):
    """解析 Markdown 文件的 YAML Frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 YAML frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        yaml_content = match.group(1)
        return yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"⚠️  解析失败 {filepath}: {e}")
        return None

def scan_all_skills():
    """扫描所有 Skill，构建依赖图谱"""
    skills = {}
    depends_on_map = defaultdict(list)  # skill -> [依赖的 skill]
    referenced_by_map = defaultdict(list)  # skill -> [引用它的 skill]
    
    for root, dirs, files in os.walk(SKILLS_DIR):
        for file in files:
            if file == "SKILL.md":
                filepath = os.path.join(root, file)
                meta = parse_yaml_frontmatter(filepath)
                
                if meta and 'name' in meta:
                    name = meta['name']
                    skills[name] = {
                        'path': filepath,
                        'description': meta.get('description', ''),
                        'triggers': meta.get('triggers', []),
                        'depends_on': meta.get('depends_on', []),
                        'version': meta.get('version', '1.0.0')
                    }
                    
                    for dep in meta.get('depends_on', []):
                        depends_on_map[name].append(dep)
                        referenced_by_map[dep].append(name)
    
    return skills, depends_on_map, referenced_by_map

def check_broken_references(skills, depends_on_map):
    """检查断裂的引用"""
    broken = []
    for skill, deps in depends_on_map.items():
        for dep in deps:
            if dep not in skills:
                broken.append({
                    'skill': skill,
                    'missing_dep': dep,
                    'path': skills[skill]['path']
                })
    return broken

def print_dependency_report(skills, depends_on_map, referenced_by_map, broken_refs):
    """打印依赖关系报告"""
    print("\n" + "="*60)
    print("📊 Skill 依赖关系图谱 (Dependency Graph)")
    print("="*60)
    
    # 1. 依赖统计表
    print("\n📋 依赖关系总览:")
    print(f"  总 Skill 数: {len(skills)}")
    print(f"  有依赖声明的 Skill: {len(depends_on_map)}")
    print(f"  被引用的 Skill: {len(referenced_by_map)}")
    print(f"  断裂引用数: {len(broken_refs)}")
    
    # 2. 详细依赖列表
    print("\n🔗 详细依赖关系:")
    for skill in sorted(skills.keys()):
        deps = depends_on_map.get(skill, [])
        refs = referenced_by_map.get(skill, [])
        
        if deps or refs:
            print(f"\n  📦 {skill} (v{skills[skill]['version']})")
            if deps:
                print(f"    ← 依赖: {', '.join(deps)}")
            if refs:
                print(f"    → 被引用: {', '.join(refs)}")
    
    # 3. 断裂引用警告
    if broken_refs:
        print("\n" + "!"*60)
        print("🚨 断裂引用警告 (Broken References):")
        print("!"*60)
        for item in broken_refs:
            print(f"  ❌ {item['skill']} 依赖了不存在的 Skill: {item['missing_dep']}")
            print(f"     文件: {item['path']}")
        print("\n  💡 建议: 创建缺失的 Skill 或更新依赖声明")
    else:
        print("\n✅ 所有依赖引用完整，无断裂！")
    
    # 4. 核心 Skill 识别 (被引用最多的)
    if referenced_by_map:
        print("\n🌟 核心 Skill (被引用最多):")
        sorted_refs = sorted(referenced_by_map.items(), key=lambda x: len(x[1]), reverse=True)
        for skill, refs in sorted_refs[:5]:
            print(f"  ⭐ {skill}: 被 {len(refs)} 个 Skill 引用 ({', '.join(refs)})")
    
    print("\n" + "="*60)

def main():
    print("🔍 开始扫描 Skill 依赖关系...")
    skills, depends_on_map, referenced_by_map = scan_all_skills()
    broken_refs = check_broken_references(skills, depends_on_map)
    print_dependency_report(skills, depends_on_map, referenced_by_map, broken_refs)

if __name__ == "__main__":
    main()
