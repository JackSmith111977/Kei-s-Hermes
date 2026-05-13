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

def scan_single_skill(target_name):
    """定向扫描指定 skill 的引用关系（快速模式）"""
    skills = {}
    depends_on_map = defaultdict(list)
    referenced_by_map = defaultdict(list)

    for root, dirs, files in os.walk(SKILLS_DIR):
        # 快速路径过滤
        if f"/{target_name}/" not in root and not root.endswith(f"/{target_name}"):
            # 但仍然需要扫描所有 SKILL.md 来找到引用 target 的 skill
            pass
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

    broken_refs = check_broken_references(skills, depends_on_map)

    print(f"\n{'='*60}")
    print(f"🎯 定向扫描: {target_name}")
    print(f"{'='*60}")

    # 只显示目标 skill 的相关信息
    if target_name in skills:
        print(f"\n📦 {target_name} (v{skills[target_name]['version']})")
        deps = depends_on_map.get(target_name, [])
        refs = referenced_by_map.get(target_name, [])
        if deps:
            print(f"  ← 依赖: {', '.join(deps)}")
        else:
            print(f"  ← 依赖: (无)")
        if refs:
            print(f"  → 被 {len(refs)} 个 skill 引用: {', '.join(refs[:10])}")
            if len(refs) > 10:
                print(f"     ...及另外 {len(refs)-10} 个")
        else:
            print(f"  → 被引用: (无)")
    else:
        print(f"  ❌ Skill '{target_name}' 不存在")
        # 建议相似名称
        close_matches = [n for n in skills if target_name in n or n in target_name]
        if close_matches:
            print(f"  💡 相近名称: {', '.join(close_matches[:5])}")

    if broken_refs:
        print(f"\n🚨 断裂引用 (影响 {len(broken_refs)} 个 skill):")
        for item in broken_refs:
            if item['skill'] == target_name or item['missing_dep'] == target_name:
                print(f"  ❌ {item['skill']} → {item['missing_dep']}")

    return skills, depends_on_map, referenced_by_map


def main():
    import sys
    target = None
    args = sys.argv[1:]

    for i, arg in enumerate(args):
        if arg in ('--target', '-t') and i + 1 < len(args):
            target = args[i + 1]
            args.pop(i + 1)
            args.pop(i)
            break

    if target:
        print(f"🔍 定向扫描 '{target}' 的依赖关系...")
        scan_single_skill(target)
    else:
        print("🔍 开始全量扫描 Skill 依赖关系...")
        skills, depends_on_map, referenced_by_map = scan_all_skills()
        broken_refs = check_broken_references(skills, depends_on_map)
        print_dependency_report(skills, depends_on_map, referenced_by_map, broken_refs)
        # 输出关键数据供 pre_flight 调用
        if len(sys.argv) > 1 and sys.argv[1] == '--json':
            import json as j
            print(f"\n---JSON---")
            result = {
                "total_skills": len(skills),
                "skills_with_deps": len(depends_on_map),
                "referenced_skills": len(referenced_by_map),
                "broken_refs": len(broken_refs),
                "most_referenced": [
                    {"skill": s, "refs": len(r)}
                    for s, r in sorted(referenced_by_map.items(),
                                       key=lambda x: -len(x[1]))[:5]
                ]
            }
            print(j.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
