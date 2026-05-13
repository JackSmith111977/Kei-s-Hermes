#!/usr/bin/env python3
"""
skill-quality-score.py v1.0 — Skill 质量评分系统 (SQS)

Skill Quality Score (SQS) 是衡量 Hermes Skill 质量的标准化评分体系。
满分 100 分，5 个维度各 20 分。

用法:
  python3 skill-quality-score.py <skill-name>         # 评分单个技能
  python3 skill-quality-score.py <skill-name> --json   # JSON 输出
  python3 skill-quality-score.py --audit               # 审计所有技能
  python3 skill-quality-score.py --audit --threshold 70 # 只报告低于阈值
  python3 skill-quality-score.py --audit --json        # 全量 JSON 报告

评分维度:
  S1: 结构完整性 (20分) — YAML frontmatter 完整度
  S2: 内容准确性 (20分) — 步骤可执行性、具体性
  S3: 时效性     (20分) — 版本新鲜度、更新频率
  S4: 关联完整性 (20分) — 依赖声明、引用完整性
  S5: 可发现性   (20分) — triggers 丰富度、标签完整度

等级:
  90-100: 🟢 优秀  70-89: 🟡 良好  50-69: 🟠 需改进  <50: 🔴 不合格
"""

import os, sys, re, json
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
NOW = datetime.now(timezone.utc)


def read_skill(skill_name):
    """读取 skill 的 SKILL.md，返回 frontmatter 和正文"""
    # 查找 skill 路径
    for root, dirs, files in os.walk(SKILLS_DIR):
        if os.path.basename(root) == skill_name and "SKILL.md" in files:
            skill_path = Path(root) / "SKILL.md"
            break
        for d in dirs:
            if d == skill_name:
                sub_path = Path(root) / d / "SKILL.md"
                if sub_path.exists():
                    skill_path = sub_path
                    break
    else:
        # 尝试直接路径
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"

    if not skill_path.exists():
        return None, None, None

    content = skill_path.read_text(encoding='utf-8')

    # 解析 YAML frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    fm = None
    if fm_match:
        try:
            import yaml
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except:
            fm = {}

    body = content[fm_match.end():] if fm_match else content

    # 查找 linked files
    skill_dir = skill_path.parent
    linked = {
        "references": list(skill_dir.glob("references/**/*")),
        "scripts": list(skill_dir.glob("scripts/**/*")),
        "templates": list(skill_dir.glob("templates/**/*")),
        "checklists": list(skill_dir.glob("checklists/**/*")),
        "assets": list(skill_dir.glob("assets/**/*")),
    }
    linked = {k: [f for f in v if f.is_file()] for k, v in linked.items()}

    return content, fm, body, linked, skill_path


def score_structure(fm, has_body):
    """S1: 结构完整性 (0-20)"""
    score = 0

    # 必需字段 (10分)
    required = ["name", "version", "description"]
    for field in required:
        if fm and fm.get(field):
            score += 3

    # 可选增强字段 (5分)
    optional = ["author", "tags", "triggers", "license"]
    for field in optional:
        if fm and fm.get(field):
            score += 1.25
            if score > 20:
                score = 20

    # 正文存在性 (3分)
    if has_body and len(has_body.strip()) > 100:
        score += 3

    # 目录结构 (2分)
    skill_dir = None
    if fm and fm.get('name'):
        for root, dirs, files in os.walk(SKILLS_DIR):
            if os.path.basename(root) == fm['name']:
                skill_dir = Path(root)
                break
    if skill_dir:
        subdirs = [d for d in skill_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if subdirs:
            score += 2

    return min(score, 20)


def score_content(content, fm, body):
    """S2: 内容准确性 (0-20)"""
    score = 0
    if not content:
        return 0

    # 有具体命令/代码示例 (5分)
    code_blocks = len(re.findall(r'```', content or '')) // 2
    if code_blocks >= 3:
        score += 5
    elif code_blocks >= 1:
        score += 3

    # 有 Red Flags / 常见陷阱章节 (5分)
    if re.search(r'Red Flag|陷阱|Pitfall|常见错误|注意事项', content or '', re.IGNORECASE):
        score += 5

    # 有具体步骤 (5分)
    if re.search(r'步骤|Step \d|1\.\s|2\.\s|3\.\s', content or ''):
        score += 5

    # 内容长度适中 (3分)
    line_count = len((content or '').split('\n'))
    if 30 <= line_count <= 400:
        score += 3
    elif line_count > 0:
        score += 1

    # 有 Example 或示例章节 (2分)
    if re.search(r'示例|Example|例子|场景', content or '', re.IGNORECASE):
        score += 2

    return min(score, 20)


def score_freshness(fm, skill_path):
    """S3: 时效性 (0-20)"""
    score = 10  # 基础分

    # 版本号 (5分)
    version = (fm or {}).get('version', '')
    if version:
        try:
            parts = version.split('.')
            major = int(parts[0])
            if major >= 1:
                score += 3  # 有正式版本
            if len(parts) >= 3:
                score += 2  # 完整 semver
        except:
            pass

    # 文件修改时间 (5分)
    if skill_path and skill_path.exists():
        mtime = datetime.fromtimestamp(skill_path.stat().st_mtime, tz=timezone.utc)
        days = (NOW - mtime).days
        if days < 7:
            score += 5
        elif days < 30:
            score += 4
        elif days < 90:
            score += 2
        elif days < 180:
            score += 1
        # >180天不加分

    # 创建日期 (在 frontmatter 中) (5分)
    created = (fm or {}).get('created') or (fm or {}).get('date')
    if created:
        score += 5

    # 版本活跃度 (5分)
    if version:
        try:
            minor = int(version.split('.')[1])
            if minor > 0:
                score += 3  # 有次版本号更新
            patch = int(version.split('.')[2])
            if patch > 0:
                score += 2
        except:
            pass

    return min(score, 20)


def score_relations(fm, content):
    """S4: 关联完整性 (0-20)"""
    score = 5  # 基础分

    # depends_on 声明 (5分)
    depends = (fm or {}).get('depends_on', [])
    if depends:
        score += 5
        # 检查依赖是否存在
        for dep in depends:
            dep_path = SKILLS_DIR / dep / "SKILL.md"
            if dep_path.exists():
                score += 1
            else:
                score -= 1  # 断裂引用扣分

    # referenced_by (5分)
    referenced = (fm or {}).get('referenced_by', [])
    if referenced:
        score += 3

    # 交叉引用 (5分)
    refs = re.findall(r'\[.*?\]\(.*?skills.*?\)', content or '', re.IGNORECASE)
    if refs:
        score += min(len(refs) * 1.5, 5)

    # experience_refs / skill_refs (5分)
    exp_refs = (fm or {}).get('experience_refs', []) if fm else []
    if exp_refs:
        score += 3

    # 关联相关 skill (2分)
    related = (fm or {}).get('related_skills', [])
    if related:
        score += 2

    return min(max(score, 0), 20)


def score_discoverability(fm, content, body):
    """S5: 可发现性 (0-20)"""
    score = 5  # 基础分

    # triggers (8分)
    triggers = (fm or {}).get('triggers', [])
    if not triggers:
        # 也可能是 tags
        triggers = (fm or {}).get('tags', [])
    if triggers:
        trigger_count = len(triggers)
        if trigger_count >= 8:
            score += 8
        elif trigger_count >= 5:
            score += 6
        elif trigger_count >= 3:
            score += 4
        elif trigger_count >= 1:
            score += 2

    # 描述质量 (4分)
    desc = (fm or {}).get('description', '')
    if len(desc) > 100:
        score += 4
    elif len(desc) > 50:
        score += 2
    elif len(desc) > 0:
        score += 1

    # 标题清晰度 (3分)
    name = (fm or {}).get('name', '')
    if name and not re.match(r'^[a-z-]+$', name):
        score += 3

    # 有 usage_hint 或使用示例 (3分)
    if fm and fm.get('usage_hint'):
        score += 3
    elif re.search(r'用法|使用|how to use|Usage|用法:', content or '', re.IGNORECASE):
        score += 2

    # 标签完整性 (2分)
    tags = (fm or {}).get('tags', [])
    if len(tags) >= 3:
        score += 2

    return min(score, 20)


def calculate_sqs(skill_name, output_json=False):
    """计算单个 skill 的 SQS 总分"""
    result = read_skill(skill_name)
    if result[0] is None:
        if output_json:
            print(json.dumps({"skill": skill_name, "error": "not found"}, ensure_ascii=False))
        else:
            print(f"❌ Skill '{skill_name}' 未找到")
        return None, {}

    content, fm, body, linked, skill_path = result

    s1 = score_structure(fm, body)
    s2 = score_content(content, fm, body)
    s3 = score_freshness(fm, skill_path)
    s4 = score_relations(fm, content)
    s5 = score_discoverability(fm, content, body)

    total = s1 + s2 + s3 + s4 + s5

    # 等级
    if total >= 90:
        level = "🟢 优秀"
    elif total >= 70:
        level = "🟡 良好"
    elif total >= 50:
        level = "🟠 需改进"
    else:
        level = "🔴 不合格"

    # 提取版本和 last_updated
    version = (fm or {}).get('version', '?')
    desc = (fm or {}).get('description', '')[:60]
    triggers = (fm or {}).get('triggers', []) or (fm or {}).get('tags', [])

    report = {
        "skill": skill_name,
        "sqs_total": round(total, 1),
        "level": level,
        "dimensions": {
            "S1_structure": round(s1, 1),
            "S2_content": round(s2, 1),
            "S3_freshness": round(s3, 1),
            "S4_relations": round(s4, 1),
            "S5_discoverability": round(s5, 1),
        },
        "version": version,
        "description": desc,
        "linked_files": {k: len(v) for k, v in linked.items() if v},
        "triggers_count": len(triggers),
        "depends_on": (fm or {}).get('depends_on', []),
    }

    if output_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  📊 SQS: {skill_name}")
        print(f"{'='*55}")
        print(f"  总分: {total:.1f}/100  {level}")
        print(f"  版本: {version}")
        print(f"  描述: {desc}")
        print(f"\n  维度得分:")
        print(f"    S1 结构完整性:  {s1:5.1f}/20  {'🟢' if s1>=15 else '🟡' if s1>=10 else '🟠'}")
        print(f"    S2 内容准确性:  {s2:5.1f}/20  {'🟢' if s2>=15 else '🟡' if s2>=10 else '🟠'}")
        print(f"    S3 时效性:      {s3:5.1f}/20  {'🟢' if s3>=15 else '🟡' if s3>=10 else '🟠'}")
        print(f"    S4 关联完整性:  {s4:5.1f}/20  {'🟢' if s4>=15 else '🟡' if s4>=10 else '🟠'}")
        print(f"    S5 可发现性:    {s5:5.1f}/20  {'🟢' if s5>=15 else '🟡' if s5>=10 else '🟠'}")
        if linked:
            cats = ", ".join(f"{k}({len(v)})" for k, v in linked.items() if v)
            print(f"\n  关联文件: {cats}")
        print(f"{'='*55}\n")

    return total, report


def cmd_audit(threshold=50, output_json=False):
    """审计所有 skill，输出 SQS 报告"""
    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            name = os.path.basename(root)
            total, report = calculate_sqs(name, output_json=False)
            if total is not None:
                skills.append((total, report))

    skills.sort(key=lambda x: -x[0])

    if output_json:
        print(json.dumps([s[1] for s in skills], ensure_ascii=False, indent=2))
        return

    # 分组
    excellent = [s for s in skills if s[0] >= 90]
    good = [s for s in skills if 70 <= s[0] < 90]
    needs_work = [s for s in skills if 50 <= s[0] < 70]
    failing = [s for s in skills if s[0] < 50]

    print(f"\n{'#'*55}")
    print(f"#  📊 SQS 全量审计报告")
    print(f"#  扫描: {len(skills)} skills")
    print(f"{'#'*55}")
    print(f"\n🟢 优秀 (90+):   {len(excellent)}")
    print(f"🟡 良好 (70-89):  {len(good)}")
    print(f"🟠 需改进 (50-69): {len(needs_work)}")
    print(f"🔴 不合格 (<50):   {len(failing)}")

    # 低于阈值
    below = [s for s in skills if s[0] < threshold]
    if below:
        print(f"\n⚠️  低于阈值 ({threshold}): {len(below)} 个 skill:")
        for total, report in below[:20]:
            print(f"  {total:5.1f}  {report['skill']:30s} [{report['version']}]")
        if len(below) > 20:
            print(f"  ...及另外 {len(below)-20} 个")

    # Top 10
    print(f"\n🏆 Top 10:")
    for total, report in skills[:10]:
        print(f"  {total:5.1f}  {report['skill']:30s} [{report['version']}]")

    # Bottom 5
    print(f"\n📉 Bottom 5:")
    for total, report in skills[-5:]:
        print(f"  {total:5.1f}  {report['skill']:30s} [{report['version']}]")

    # 按维度分析平均分
    dims = {
        "S1_structure": [], "S2_content": [], "S3_freshness": [],
        "S4_relations": [], "S5_discoverability": []
    }
    for _, report in skills:
        for d in dims:
            dims[d].append(report["dimensions"][d])

    print(f"\n📊 维度平均分:")
    for d, scores in dims.items():
        avg = sum(scores) / len(scores) if scores else 0
        bar = "█" * int(avg / 2) + "░" * (10 - int(avg / 2))
        print(f"  {d}: {avg:5.1f}/20 {bar}")

    # 统计关联文件
    total_linked = sum(len(report.get("linked_files", {})) for _, report in skills)
    print(f"\n📎 总关联文件组: {total_linked}")

    # 生成改进建议
    print(f"\n💡 改进建议:")
    for d, scores in dims.items():
        avg = sum(scores) / len(scores) if scores else 0
        dname = {"S1_structure": "结构完整性", "S2_content": "内容准确性",
                 "S3_freshness": "时效性", "S4_relations": "关联完整性",
                 "S5_discoverability": "可发现性"}.get(d, d)
        if avg < 12:
            print(f"  🔴 {dname} ({avg:.1f}) 需重点改进")
        elif avg < 16:
            print(f"  🟡 {dname} ({avg:.1f}) 可进一步优化")

    print()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    output_json = '--json' in sys.argv
    threshold = 50

    # 提取阈值
    for i, arg in enumerate(sys.argv):
        if arg == '--threshold' and i + 1 < len(sys.argv):
            try:
                threshold = int(sys.argv[i + 1])
            except:
                pass

    if sys.argv[1] == '--audit':
        cmd_audit(threshold, output_json)
    else:
        skill_name = sys.argv[1]
        calculate_sqs(skill_name, output_json)


if __name__ == "__main__":
    main()
