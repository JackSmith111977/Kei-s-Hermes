#!/usr/bin/env python3
"""
Skill Auto-Linker & Merge Detector v1.0
自动关联新创建的 skill 与已有 skill，检测功能重合。

功能：
1. 🔗 auto-link：新 skill 创建后，自动扫描所有 skill 并更新 related_skills
2. 🧩 merge-detect：检测功能高度重合的 skill（建议合并）
3. 🔄 full-scan：对全部 skill 执行关联和合并检测
4. 📊 report：生成关联关系报告

用法：
  python3 ~/.hermes/scripts/skill-auto-link.py auto-link <skill_name>
  python3 ~/.hermes/scripts/skill-auto-link.py merge-detect <skill_name>
  python3 ~/.hermes/scripts/skill-auto-link.py full-scan
  python3 ~/.hermes/scripts/skill-auto-link.py report
"""

import os
import re
import sys
import json
import math
import yaml
from pathlib import Path
from collections import defaultdict

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")

# ── 同义词扩展表（复用 skill_finder_v2 的逻辑） ──
SYNONYMS = {
    "UI": ["界面", "用户界面", "用户接口", "user interface", "interface", "ui设计", "ui/ux"],
    "UX": ["用户体验", "user experience", "体验", "交互", "交互设计", "usability"],
    "设计": ["design", "设计语言", "设计系统", "design system", "视觉", "审美", "风格", "style", "styling"],
    "网页": ["web", "网站", "html", "前端", "frontend", "页面", "website", "webpage"],
    "CSS": ["样式", "style", "stylesheet", "排版", "布局", "css3", "css代码"],
    "审美": ["aesthetics", "美学", "品味", "taste", "美丑", "好不好看", "视觉判断"],
    "风格": ["style", "流派", "样式", "主题", "theme", "视觉风格", "设计风格"],
    "技能": ["skill", "工具", "能力", "workflow", "流程"],
    "学习": ["learn", "study", "research", "调研", "研究", "掌握"],
    "文档": ["document", "doc", "写作", "writing", "文档生成"],
    "开发": ["development", "dev", "编程", "代码", "code", "软件"],
    "数据": ["data", "分析", "analytics", "可视化", "chart"],
    "AI": ["人工智能", "机器学习", "ML", "deep learning", "LLM", "模型"],
    "测试": ["test", "testing", "验证", "quality", "qa"],
    "部署": ["deploy", "发布", "ci", "cd", "pipeline"],
    "安全": ["security", "安全", "auth", "认证", "权限", "token"],
    "自动": ["auto", "自动化", "automation", "定时", "cron", "schedule"],
    "Git": ["github", "git", "版本控制", "version control", "代码管理"],
    "html": ["html5", "超文本", "网页", "web", "前端"],
    "原型": ["prototype", "mockup", "sketch", "线框图", "wireframe", "设计稿"],
    "可访问性": ["accessibility", "a11y", "wcag", "无障碍", "包容性", "inclusive"],
    "情感化": ["emotional", "emotion", "本能", "visceral", "behavioral", "reflective"],
    "排版": ["typography", "字体", "布局", "grid", "网格", "瑞士风格"],
}

# ── YAML 解析 ──
def parse_yaml_frontmatter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        return yaml.safe_load(match.group(1))
    except Exception as e:
        return None

# ── 扫描所有 skill ──
def scan_all_skills():
    """返回 {name: {path, description, tags, triggers, related_skills, depends_on, metadata}}"""
    skills = {}
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f == "SKILL.md":
                filepath = os.path.join(root, f)
                meta = parse_yaml_frontmatter(filepath)
                if meta:
                    name = meta.get('name', '')
                    if not name:
                        # 用目录名作为 fallback
                        name = os.path.basename(os.path.dirname(filepath))
                    hermes = meta.get('metadata', {}).get('hermes', {})
                    skills[name] = {
                        'path': filepath,
                        'description': meta.get('description', ''),
                        'tags': hermes.get('tags', meta.get('tags', [])),
                        'triggers': meta.get('triggers', []),
                        'related_skills': hermes.get('related_skills', []),
                        'depends_on': meta.get('depends_on', []),
                        'category': hermes.get('category', ''),
                        'skill_type': hermes.get('skill_type', ''),
                    }
    return skills

# ── 文本相似度评分 ──
def expand_synonyms(text):
    """对文本做同义词扩展"""
    text_lower = text.lower()
    expanded = set()
    # 原始词
    for word in re.findall(r'[a-zA-Z\u4e00-\u9fff]+', text_lower):
        expanded.add(word)
        # 同义词扩展
        for key, syns in SYNONYMS.items():
            if word == key.lower() or word in syns or key.lower() in word:
                expanded.update(syns)
    return expanded

def score_similarity(skill_a, skill_b, name_a="", name_b=""):
    """计算两个 skill 之间的关联度分数 (0-100)
    使用点积法：每命中一个维度就加分，不按比例"""
    score = 0

    def text_to_set(text):
        return set(re.findall(r'[a-zA-Z\u4e00-\u9fff]+', text.lower()))

    # 1. 名称匹配 (最高 15)
    a_name = set(name_a.lower().replace('-', ' ').replace('_', ' ').split())
    b_name = set(name_b.lower().replace('-', ' ').replace('_', ' ').split())
    # 精确匹配
    exact_name = a_name & b_name
    if exact_name:
        score += 15
    else:
        # 部分匹配
        for wa in a_name:
            for wb in b_name:
                if len(wa) > 2 and len(wb) > 2 and (wa in wb or wb in wa):
                    score += 8
                    break
            else:
                continue
            break

    # 2. Tags 匹配 (最高 20)
    a_tags = set(t.lower() for t in skill_a.get('tags', []))
    b_tags = set(t.lower() for t in skill_b.get('tags', []))
    if a_tags and b_tags:
        exact_tag = a_tags & b_tags
        if exact_tag:
            score += 20
        else:
            # 同义词匹配
            for ta in a_tags:
                for tb in b_tags:
                    if (ta in SYNONYMS and tb in SYNONYMS[ta]) or \
                       (tb in SYNONYMS and ta in SYNONYMS[tb]):
                        score += 12
                        break
                else:
                    continue
                break

    # 3. Triggers 匹配 (最高 15)
    a_triggers = set(t.lower() for t in skill_a.get('triggers', []))
    b_triggers = set(t.lower() for t in skill_b.get('triggers', []))
    if a_triggers & b_triggers:
        score += 15

    # 4. 分类匹配 (最高 10)
    if skill_a.get('category') and skill_a['category'] == skill_b.get('category'):
        score += 10

    # 5. 关联关系匹配 (最高 15)
    if skill_a.get('related_skills') and name_b in skill_a['related_skills']:
        score += 15
    elif skill_b.get('related_skills') and name_a in skill_b['related_skills']:
        score += 15

    # 6. 正文内容关键词匹配 (最高 25)
    try:
        for skill_dict in [skill_a, skill_b]:
            if 'body_snippet' not in skill_dict:
                fp = skill_dict.get('path', '')
                if fp and os.path.exists(fp):
                    with open(fp, 'r', encoding='utf-8') as f:
                        ct = f.read()
                    bm = re.search(r'---\n(.*?)\n---\n(.*)', ct, re.DOTALL)
                    if bm:
                        skill_dict['body_snippet'] = bm.group(2)[:200].lower()
        a_body = skill_a.get('body_snippet', '')
        b_body = skill_b.get('body_snippet', '')
        if a_body and b_body:
            a_bw = set(re.findall(r'[a-zA-Z\u4e00-\u9fff]{2,}', a_body))
            b_bw = set(re.findall(r'[a-zA-Z\u4e00-\u9fff]{2,}', b_body))
            body_overlap = a_bw & b_bw
            # 只看有意义的词（长度≥3的英文词或中文词）
            sig_overlap = {w for w in body_overlap if len(w) >= 3}
            if sig_overlap:
                # 根据重叠词数量给分
                overlap_count = len(sig_overlap)
                if overlap_count >= 10: score += 25
                elif overlap_count >= 5: score += 18
                elif overlap_count >= 3: score += 12
                elif overlap_count >= 1: score += 8
    except Exception:
        pass

    return min(100, round(score, 1))

# ── 核心功能 1: Auto-Link ──
def auto_link(target_name, skills=None, dry_run=False):
    """为新 skill 自动关联最相关的 skill（≥40分）"""
    if skills is None:
        skills = scan_all_skills()

    if target_name not in skills:
        print(f"❌ 未找到 skill: {target_name}")
        return [], []

    target = skills[target_name]
    candidates = []

    for name, data in skills.items():
        if name == target_name:
            continue
        s = score_similarity(target, data, name_a=target_name, name_b=name)
        if s >= 15:  # 阈值：15 分以上就考虑关联
            candidates.append((name, s))

    # 按分数排序
    candidates.sort(key=lambda x: x[1], reverse=True)

    # 生成关联建议（≥20分）
    strong_links = [c for c in candidates if c[1] >= 20]
    weak_links = [c for c in candidates if 15 <= c[1] < 20]

    if not dry_run:
        updates = []
        # 更新目标 skill 的 related_skills
        for skill_name, score in strong_links:
            if skill_name not in target.get('related_skills', []):
                updates.append((target_name, skill_name, score))
        
        # 也更新关联 skill 的 related_skills
        for skill_name, score in strong_links:
            if target_name not in skills[skill_name].get('related_skills', []):
                updates.append((skill_name, target_name, score))

        if updates:
            print(f"\n🔗 将添加 {len(updates)} 条关联关系：")
            for src, dst, s in updates:
                print(f"   {src} ←→ {dst} (分数: {s})")
        else:
            print("\n✅ 所有关联关系已存在，无需更新")
    else:
        print(f"\n[干运行] 建议关联：")
        for name, s in strong_links:
            print(f"   ⭐ {name} (分数: {s})")
        for name, s in weak_links:
            print(f"   💡 {name} (分数: {s})")

    return strong_links, weak_links

# ── 核心功能 2: Merge Detection ──
def merge_detect(threshold=70, skills=None):
    """检测高度重合的 skill pairs（≥70 分），建议合并"""
    if skills is None:
        skills = scan_all_skills()

    names = list(skills.keys())
    merge_candidates = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s = score_similarity(skills[names[i]], skills[names[j]],
                                 name_a=names[i], name_b=names[j])
            if s >= threshold:
                merge_candidates.append((names[i], names[j], s))

    merge_candidates.sort(key=lambda x: x[2], reverse=True)

    if merge_candidates:
        print(f"\n🧩 发现 {len(merge_candidates)} 对建议合并的 skill（阈值 ≥{threshold}）：")
        for a, b, s in merge_candidates:
            print(f"\n  🔀 {a} <--> {b} (重合度: {s}%)")
            print(f"     📝 {skills[a].get('description', '')[:60]}...")
            print(f"     📝 {skills[b].get('description', '')[:60]}...")
            print(f"     💡 建议: 将较小 skill 的内容合并到较大的 skill 中，"
                  f"再用 `skill_manage delete` 移除")
    else:
        print(f"\n✅ 未发现重合度 ≥{threshold}% 的 skill 对")
    
    return merge_candidates

# ── 核心功能 3: Full Scan ──
def full_scan():
    """全量扫描：对每个 skill 执行 auto-link 和 merge detection"""
    print("=" * 60)
    print("🔄 Skill 全量扫描报告")
    print("=" * 60)

    skills = scan_all_skills()
    print(f"\n📊 总计 {len(skills)} 个 skill")

    # 对每个 skill 计算关联
    link_count = 0
    for name in skills:
        strong, _ = auto_link(name, skills, dry_run=True)
        link_count += len(strong)

    print(f"\n📎 潜在关联数: ~{link_count} 条")

    # 合并检测
    merge_candidates = merge_detect(70, skills)
    
    return {
        'total_skills': len(skills),
        'link_count': link_count,
        'merge_candidates': merge_candidates
    }

# ── 核心功能 4: Report ──
def report():
    """生成完整的 skill 关联状态报告"""
    skills = scan_all_skills()
    
    # 统计
    has_related = sum(1 for s in skills.values() if s.get('related_skills'))
    total_related_refs = sum(len(s.get('related_skills', [])) for s in skills.values())
    
    # 被引用最多的 skill
    ref_count = defaultdict(int)
    for s in skills.values():
        for r in s.get('related_skills', []):
            ref_count[r] += 1
    
    print("=" * 60)
    print("📊 Skill 关联状态报告")
    print("=" * 60)
    print(f"\n📈 统计概览：")
    print(f"  总 skill 数: {len(skills)}")
    print(f"  有关联关系的 skill: {has_related}/{len(skills)} ({has_related/max(len(skills),1)*100:.0f}%)")
    print(f"  总关联引用数: {total_related_refs}")
    
    # 孤立 skill（没有任何关联）
    isolated = [n for n, s in skills.items() 
                if not s.get('related_skills') 
                and ref_count.get(n, 0) == 0]
    
    if isolated:
        print(f"\n📌 孤立 Skill（无任何关联，建议检查）：")
        for name in isolated[:15]:
            cat = skills[name].get('category', '无分类')
            desc = skills[name].get('description', '')[:50]
            print(f"   🏝️  {name} [{cat}] — {desc}")
        if len(isolated) > 15:
            print(f"   ... 及其他 {len(isolated)-15} 个")
    
    # 关联中心（被引用最多的 skill）
    if ref_count:
        print(f"\n🌟 关联中心（被引用最多）：")
        top = sorted(ref_count.items(), key=lambda x: x[1], reverse=True)[:10]
        for name, cnt in top:
            if name in skills:
                print(f"   ⭐ {name}: 被 {cnt} 个 skill 引用")
    
    return {
        'total': len(skills),
        'has_related': has_related,
        'total_refs': total_related_refs,
        'isolated': isolated
    }

# ── 直接更新 SKILL.md 的 related_skills ──
def update_related_skills(skill_name, new_related_list):
    """直接更新 skill 的 SKILL.md 中的 related_skills 字段"""
    skills = scan_all_skills()
    if skill_name not in skills:
        print(f"❌ 未找到 skill: {skill_name}")
        return False
    
    filepath = skills[skill_name]['path']
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建新的 related_skills YAML 行
        new_line = f"    related_skills: {json.dumps(new_related_list)}"
        
        # 查找现有的 related_skills 行并替换
        pattern = r'    related_skills: \[.*?\]'
        if re.search(pattern, content):
            content = re.sub(pattern, new_line, content)
        else:
            # 在 tags 或 category 后插入
            insert_pattern = r'(    (?:tags|category): .*?\n)'
            match = re.search(insert_pattern, content)
            if match:
                insert_pos = match.end()
                content = content[:insert_pos] + new_line + '\n' + content[insert_pos:]
            else:
                print(f"❌ 无法找到插入位置")
                return False
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新 {skill_name} 的 related_skills")
        return True
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

# ── 主入口 ──
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "auto-link":
        if len(sys.argv) < 3:
            print("用法: skill-auto-link.py auto-link <skill_name> [--dry-run]")
            sys.exit(1)
        dry_run = "--dry-run" in sys.argv
        target = sys.argv[2]
        strong, weak = auto_link(target, dry_run=dry_run)
        # 如果非干运行，执行更新
        if not dry_run and strong:
            skills = scan_all_skills()
            for skill_name, score in strong:
                # 更新目标 skill
                target_data = skills.get(target)
                if target_data and skill_name not in target_data.get('related_skills', []):
                    new_related = target_data['related_skills'] + [skill_name]
                    update_related_skills(target, new_related)
                # 更新关联 skill
                rel_data = skills.get(skill_name)
                if rel_data and target not in rel_data.get('related_skills', []):
                    new_related = rel_data['related_skills'] + [target]
                    update_related_skills(skill_name, new_related)

    elif command == "merge-detect":
        threshold = 70
        if len(sys.argv) >= 3:
            threshold = int(sys.argv[2])
        merge_detect(threshold)

    elif command == "full-scan":
        full_scan()

    elif command == "report":
        report()

    elif command == "score":
        if len(sys.argv) < 4:
            print("用法: skill-auto-link.py score <skill_a> <skill_b>")
            sys.exit(1)
        skills = scan_all_skills()
        a, b = sys.argv[2], sys.argv[3]
        if a not in skills or b not in skills:
            print("❌ 未找到指定 skill")
            sys.exit(1)
        s = score_similarity(skills[a], skills[b])
        print(f"关联度分数: {a} <--> {b} = {s}/100")

    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
