#!/usr/bin/env python3
"""
skill-quality-score.py v2.0 — Skill 质量评分系统 (SQS)

Skill Quality Score (SQS) v2.0: 7 维度评分体系
满分 140 分（7 维度 × 20 分）

用法:
  python3 skill-quality-score.py <skill-name>              # 评分单个
  python3 skill-quality-score.py <skill-name> --json       # JSON 输出
  python3 skill-quality-score.py <skill-name> --verbose    # 详细维度分解
  python3 skill-quality-score.py --audit                    # 审计所有 skills
  python3 skill-quality-score.py --audit --threshold 70     # 只报告低于阈值
  python3 skill-quality-score.py --audit --json             # 全量 JSON

评分维度:
  S1 元数据完整性  (20分) — YAML frontmatter 完整度
  S2 结构合规性    (20分) — 目录结构 + 文件命名
  S3 内容可执行性  (20分) — 步骤清晰度 + 代码示例 + Red Flags
  S4 时效性        (20分) — 版本新鲜度 + 更新频率
  S5 关联完整性    (20分) — 依赖 + 引用网络
  S6 可发现性      (20分) — triggers + tags + 描述质量
  S7 验证覆盖度    (20分) — Eval Cases + Verification Checklist

等级:
  119-140: 🟢 优秀    98-118: 🟡 良好
  70-97:   🟠 需改进   <70:    🔴 不合格
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
NOW = datetime.now(timezone.utc)

# ── 枚举值 ────────────────────────────────────────────────────
VALID_DESIGN_PATTERNS = {"Tool-Wrapper", "Generator", "Reviewer",
                          "Inversion", "Pipeline", "External-Gate"}
VALID_SKILL_TYPES = {"Workflow", "Reference", "Meta-Skill",
                      "Generator", "Checklist", "Research"}
VALID_CATEGORIES = {"dogfood", "creative", "software-development", "research",
                     "productivity", "autonomous-ai-agents", "devops", "media",
                     "doc-design", "apple", "mcp", "testing", "security",
                     "meta", "gaming", "feishu", "email", "documentation",
                     "developer-workflow"}
FORBIDDEN_FILENAMES = {"test.txt", "output.json", "file.py", "new_1.md",
                        "untitled.md", "tmp.txt", "index.html"}
FORBIDDEN_CHARS = set(' \\:*?"<>|')


# ── 读取 ──────────────────────────────────────────────────────

def read_skill(skill_name):
    """读取 skill 的 SKILL.md，返回结构体"""
    # 搜索
    skill_path = None
    for root, dirs, files in os.walk(SKILLS_DIR):
        if os.path.basename(root) == skill_name and "SKILL.md" in files:
            skill_path = Path(root) / "SKILL.md"
            break
    if not skill_path or not skill_path.exists():
        return None

    content = skill_path.read_text(encoding="utf-8")

    # 解析 YAML frontmatter
    fm = None
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    body = ""
    if fm_match:
        try:
            import yaml
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            fm = {}
        body = content[fm_match.end():]
    else:
        body = content

    # 查找 linked files
    sd = skill_path.parent
    linked = {
        "references": list(sd.glob("references/**/*")),
        "scripts": list(sd.glob("scripts/**/*")),
        "templates": list(sd.glob("templates/**/*")),
        "checklists": list(sd.glob("checklists/**/*")),
        "tests": list(sd.glob("tests/**/*")),
        "examples": list(sd.glob("examples/**/*")),
        "assets": list(sd.glob("assets/**/*")),
    }
    linked = {k: [f for f in v if f.is_file()] for k, v in linked.items()}

    return {
        "content": content,
        "fm": fm,
        "body": body,
        "path": skill_path,
        "skill_dir": sd,
        "linked": linked,
    }


# ── S1: 元数据完整性 (20分) ──────────────────────────────────

def score_s1(fm, body):
    """S1: YAML frontmatter 完整度"""
    score = 0
    if not fm:
        return 0

    # (A) 必填字段 (8分)
    required = {"name", "version", "description"}
    for field in required:
        if fm.get(field):
            score += 3  # 每个 3 分, 共 9 分, cap at 8
    score = min(score, 8)
    # 加分: name 匹配目录名 (由调用者提供)

    # (B) 非空正文 (2分)
    if body and len(body.strip()) > 100:
        score += 2

    # (C) 推荐字段存在性 (6分)
    recommended = [
        ("author", 1), ("license", 1), ("design_pattern", 1.5),
        ("skill_type", 1.5), ("tags", 1), ("category", 1),
        ("date_created", 0.5), ("date_updated", 0.5),
    ]
    for field, pts in recommended:
        if fm.get(field):
            score += pts
    score = min(score, 16)

    # (D) design_pattern 有效性 (2分)
    dp = fm.get("design_pattern", "")
    if dp in VALID_DESIGN_PATTERNS:
        score += 2

    # (E) skill_type 有效性 (2分)
    st = fm.get("skill_type", "")
    if st in VALID_SKILL_TYPES:
        score += 2

    return min(score, 20)


# ── S2: 结构合规性 (20分) ────────────────────────────────────

def score_s2(fm, body, skill_dir):
    """S2: 目录结构 + 文件命名"""
    score = 0
    if not fm:
        return 0

    # (A) SKILL.md 存在 (3分)
    sk_path = skill_dir / "SKILL.md"
    if sk_path.exists():
        score += 3

    # (B) 子目录存在 (6分)
    expected_dirs = {"references": 2, "scripts": 2, "templates": 1,
                     "checklists": 1, "tests": 1.5, "examples": 1, "assets": 0.5}
    for d, pts in expected_dirs.items():
        if (skill_dir / d).exists():
            score += pts
    score = min(score, 9)

    # (C) 文件命名规范 (5分)
    bad_files = []
    for item in skill_dir.iterdir():
        if item.is_file() and item.name not in ("SKILL.md",):
            bn = item.name.lower()
            if bn in FORBIDDEN_FILENAMES:
                bad_files.append(item.name)
            for c in FORBIDDEN_CHARS:
                if c in item.name:
                    bad_files.append(item.name)
                    break

    total_items = len(list(skill_dir.iterdir()))
    if total_items <= 10:
        score += 3  # 目录不臃肿
    elif total_items <= 20:
        score += 1

    if not bad_files:
        score += 2

    score = min(score, 14)

    # (D) 无未知子目录 (3分)
    allowed_subdirs = {"references", "scripts", "templates", "checklists",
                       "tests", "examples", "assets"}
    for item in skill_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            if item.name not in allowed_subdirs:
                score -= 1  # 发现未知子目录扣分

    # (E) 目录无冗余文件 (3分)
    md_files = list(skill_dir.glob("*.md"))
    if len(md_files) == 1:  # 只有 SKILL.md
        score += 3
    elif len(md_files) <= 3:
        score += 1

    return max(min(score, 20), 0)


# ── S3: 内容可执行性 (20分) ──────────────────────────────────

def score_s3(content, fm, body):
    """S3: 步骤清晰度 + 代码示例 + Red Flags"""
    score = 0
    if not content:
        return 0

    c = content or ""
    b = body or ""

    # (A) 代码块 (6分)
    code_blocks = len(re.findall(r'```', c)) // 2
    if code_blocks >= 5:
        score += 6
    elif code_blocks >= 3:
        score += 4
    elif code_blocks >= 1:
        score += 2

    # (B) Red Flags / 陷阱章节 (5分)
    if re.search(r'Red Flag|陷阱|Pitfall|常见错误|Anti|Common Mistakes',
                 c, re.IGNORECASE):
        # 检查是否有具体内容
        pitfall_section = re.search(
            r'(?:Red Flags?|陷阱|Pitfalls?|常见错误|Common Mistakes).*?\n'
            r'(\d+\.\s.*?(?:\n\d+\.|\Z))',
            c, re.IGNORECASE | re.DOTALL)
        if pitfall_section:
            items = re.findall(r'\d+\.\s', pitfall_section.group(1))
            count = len(items)
            score += min(count, 5)
        else:
            score += 2

    # (C) 步骤/编号列表 (5分)
    has_steps = bool(re.search(r'(步骤|Step \d|1\.\s|2\.\s|3\.\s)', c))
    if has_steps:
        score += 5

    # (D) 内容长度适中 (2分)
    lines = c.split("\n")
    if 30 <= len(lines) <= 400:
        score += 2
    elif len(lines) > 0:
        score += 1

    # (E) 示例/场景 (2分)
    if re.search(r'(示例|Example|例子|场景|Eval|TestCase)', c, re.IGNORECASE):
        score += 2

    return min(score, 20)


# ── S4: 时效性 (20分) ────────────────────────────────────────

def score_s4(fm, skill_path):
    """S4: 版本新鲜度 + 更新频率"""
    score = 8  # 基础分

    # (A) 版本号 (4分)
    version = (fm or {}).get("version", "")
    if version:
        parts = str(version).split(".")
        try:
            major = int(parts[0])
            if major >= 1:
                score += 2
            if len(parts) >= 3:
                score += 2
        except (ValueError, IndexError):
            pass

    # (B) 文件修改时间 (4分)
    if skill_path and skill_path.exists():
        mtime = datetime.fromtimestamp(skill_path.stat().st_mtime, tz=timezone.utc)
        days = (NOW - mtime).days
        if days < 7:
            score += 4
        elif days < 30:
            score += 3
        elif days < 90:
            score += 2
        elif days < 180:
            score += 1
        # > 180 天不加分

    # (C) date_created + date_updated (4分)
    created = (fm or {}).get("date_created")
    updated = (fm or {}).get("date_updated")
    if updated:
        score += 2
        try:
            ud = datetime.fromisoformat(str(updated))
            days_since_update = (NOW - ud).days
            if days_since_update < 30:
                score += 2
        except (ValueError, TypeError):
            pass
    if created:
        score += 2

    # (D) 版本活跃度 (4分)
    if version:
        try:
            parts = str(version).split(".")
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            if minor > 0:
                score += 2
            if patch > 0:
                score += 1
            if minor >= 5:
                score += 1
        except (ValueError, IndexError):
            pass

    return min(score, 20)


# ── S5: 关联完整性 (20分) ────────────────────────────────────

def score_s5(fm, content):
    """S5: 依赖 + 引用网络"""
    score = 5  # 基础分

    # (A) depends_on 存在性 + 有效性 (6分)
    depends = (fm or {}).get("depends_on", []) or []
    if depends:
        score += 3
        valid = 0
        for dep in depends:
            dep_path = SKILLS_DIR / dep / "SKILL.md"
            if dep_path.exists():
                valid += 1
            else:
                score -= 1  # 断裂引用扣分
        if valid >= 2:
            score += 2
        elif valid >= 1:
            score += 1

    # (B) referenced_by 双向检查 (4分)
    referenced = (fm or {}).get("referenced_by", []) or []
    if referenced:
        score += 2
        for ref in referenced:
            ref_path = SKILLS_DIR / ref / "SKILL.md"
            if ref_path.exists():
                try:
                    ref_content = ref_path.read_text(encoding="utf-8")
                    ref_match = re.match(r'^---\n(.*?)\n---', ref_content, re.DOTALL)
                    if ref_match:
                        import yaml
                        ref_fm = yaml.safe_load(ref_match.group(1)) or {}
                        ref_depends = ref_fm.get("depends_on", []) or []
                        skill_name = (fm or {}).get("name", "")
                        if skill_name in ref_depends:
                            score += 2  # 双向一致
                except Exception:
                    pass

    # (C) related_skills (3分)
    related = (fm or {}).get("related_skills", []) or []
    if related:
        score += min(len(related), 3)

    # (D) 交叉引用链接 (3分)
    refs = re.findall(r'\[.*?\]\(.*?skills.*?\)', content or "", re.IGNORECASE)
    if refs:
        score += min(len(refs), 3)

    # (E) metadata.hermes (4分)
    meta = (fm or {}).get("metadata", {}) or {}
    hermes_meta = meta.get("hermes", {}) if isinstance(meta, dict) else {}
    if hermes_meta:
        if hermes_meta.get("tags"):
            score += 2
        if hermes_meta.get("related_skills"):
            score += 2

    return min(max(score, 0), 20)


# ── S6: 可发现性 (20分) ──────────────────────────────────────

def score_s6(fm, content, body):
    """S6: triggers + tags + 描述质量"""
    score = 5  # 基础分

    # (A) triggers 数量 + 质量 (8分)
    triggers = (fm or {}).get("triggers", []) or []
    if not triggers:
        triggers = (fm or {}).get("tags", []) or []

    if triggers:
        tlen = len(triggers)
        if tlen >= 8:
            score += 8
        elif tlen >= 5:
            score += 6
        elif tlen >= 3:
            score += 4
        elif tlen >= 1:
            score += 2

        # 口语化奖励
        common_words = {"创建", "修改", "删除", "设置", "配置", "运行", "调试",
                        "检查", "生成", "更新", "查看", "管理", "学习", "研究",
                        "测试", "部署", "安装", "启动", "停止", "监控"}
        oral_count = sum(1 for t in triggers if any(cw in t for cw in common_words))
        if oral_count >= 3:
            score += 2

    # (B) 描述质量 (4分)
    desc = (fm or {}).get("description", "")
    if desc:
        dlen = len(desc)
        if dlen > 200:
            score += 4
        elif dlen > 100:
            score += 3
        elif dlen > 50:
            score += 2
        elif dlen > 0:
            score += 1

    # (C) tags 多样性 (3分)
    tags = (fm or {}).get("tags", []) or []
    if len(tags) >= 5:
        score += 3
    elif len(tags) >= 3:
        score += 2
    elif tags:
        score += 1

    # (D) 标题清晰度 (2分)
    name = (fm or {}).get("name", "")
    if name:
        if re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', str(name)):
            score += 1
        if len(name) >= 5:
            score += 1

    # (E) usage_hint (2分)
    hint = (fm or {}).get("usage_hint", "")
    if hint:
        score += 2

    # (F) category 标记 (1分)
    cat = (fm or {}).get("category", "")
    if cat in VALID_CATEGORIES:
        score += 1

    return min(score, 20)


# ── S7: 验证覆盖度 (20分) ────────────────────────────────────

def score_s7(content, fm, skill_dir):
    """S7: Eval Cases + Verification Checklist"""
    score = 5  # 基础分

    c = content or ""

    # (A) Verification Checklist (7分)
    has_checklist = bool(re.search(r'Verification Checklist|验证清单|检查清单|Checklist', c, re.IGNORECASE))
    if has_checklist:
        # 提取 checklist 项数
        checklist_items = re.findall(r'- \[ \]', c)
        count = len(checklist_items)
        if count >= 5:
            score += 7
        elif count >= 3:
            score += 5
        elif count >= 1:
            score += 3

        # 可执行检查奖励（含具体命令的 checklist）
        has_commands = bool(re.search(r'- \[ \].*?`', c))
        if has_commands:
            score += 2

    # (B) Eval Cases (5分)
    has_eval = bool(re.search(r'Eval|评估|TestCase|测试用例|评价用例', c, re.IGNORECASE))
    if has_eval:
        eval_items = re.findall(r'\*\*.*?\*\*', c)
        if len(eval_items) >= 3:
            score += 5
        elif len(eval_items) >= 1:
            score += 3

    # (C) tests/ 目录存在 (5分)
    if skill_dir:
        test_dir = skill_dir / "tests"
        if test_dir.exists():
            test_files = list(test_dir.glob("*.py")) + list(test_dir.glob("*.sh"))
            score += 3
            if len(test_files) >= 2:
                score += 2

    # (D) 目录中 evals 文件 (3分)
    for eval_file in ["evals.json", "evals.yaml", "eval-cases.md", "test-cases.md"]:
        if (skill_dir / eval_file).exists():
            score += 3
            break

    return min(score, 20)


# ── 总分计算 ──────────────────────────────────────────────────

def calculate_sqs(skill_name, verbose=False, output_json=False):
    """计算单个 skill 的 SQS v2.0 总分"""
    data = read_skill(skill_name)
    if data is None:
        if output_json:
            print(json.dumps({"skill": skill_name, "error": "not found"}, ensure_ascii=False))
        else:
            print(f"❌ Skill '{skill_name}' 未找到")
        return None, {}

    content = data["content"]
    fm = data["fm"]
    body = data["body"]
    skill_path = data["path"]
    skill_dir = data["skill_dir"]
    linked = data["linked"]

    s1 = score_s1(fm, body)
    s2 = score_s2(fm, body, skill_dir)
    s3 = score_s3(content, fm, body)
    s4 = score_s4(fm, skill_path)
    s5 = score_s5(fm, content)
    s6 = score_s6(fm, content, body)
    s7 = score_s7(content, fm, skill_dir)

    total = round(s1 + s2 + s3 + s4 + s5 + s6 + s7, 1)

    # 等级
    if total >= 119:
        level = "🟢 优秀"
    elif total >= 98:
        level = "🟡 良好"
    elif total >= 70:
        level = "🟠 需改进"
    else:
        level = "🔴 不合格"

    version = (fm or {}).get("version", "?")
    desc = ((fm or {}).get("description", "") or "")[:60]
    triggers = (fm or {}).get("triggers", []) or (fm or {}).get("tags", []) or []

    report = {
        "skill": skill_name,
        "sqs_total": total,
        "level": level,
        "max_score": 140,
        "dimensions": {
            "S1_metadata": round(s1, 1),
            "S2_structure": round(s2, 1),
            "S3_content": round(s3, 1),
            "S4_freshness": round(s4, 1),
            "S5_relations": round(s5, 1),
            "S6_discoverability": round(s6, 1),
            "S7_validation": round(s7, 1),
        },
        "version": version,
        "description": desc,
        "triggers_count": len(triggers),
        "depends_on": (fm or {}).get("depends_on", []),
        "referenced_by": (fm or {}).get("referenced_by", []),
        "linked_files": {k: len(v) for k, v in linked.items() if v},
    }

    if output_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif verbose:
        print(f"\n{'='*60}")
        print(f"  📊 SQS v2.0: {skill_name} (max: 140)")
        print(f"{'='*60}")
        print(f"  总分: {total}/140  {level}")
        print(f"  版本: {version}  |  描述: {desc[:50]}...")
        print(f"\n  维度得分:")
        dims = [
            ("S1 元数据完整性", s1),
            ("S2 结构合规性", s2),
            ("S3 内容可执行性", s3),
            ("S4 时效性", s4),
            ("S5 关联完整性", s5),
            ("S6 可发现性", s6),
            ("S7 验证覆盖度", s7),
        ]
        for name, val in dims:
            icon = "🟢" if val >= 15 else ("🟡" if val >= 10 else "🟠")
            bar = "█" * int(val) + "░" * (20 - int(val))
            print(f"    {icon} {name:12s}: {val:5.1f}/20 {bar}")
        if linked:
            cats = ", ".join(f"{k}({len(v)})" for k, v in linked.items() if v)
            print(f"\n  关联文件: {cats}")
        print(f"{'='*60}\n")
    else:
        print(f"  {skill_name:30s} {total:5.1f}/140  {level:10s} [{version}]")

    return total, report


# ── 全量审计 ──────────────────────────────────────────────────

def cmd_audit(threshold=70, output_json=False):
    """审计所有 skill"""
    all_results = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            name = os.path.basename(root)
            try:
                total, report = calculate_sqs(name, output_json=False)
                if total is not None:
                    all_results.append((total, report))
            except Exception as e:
                print(f"  ⚠️  {name}: {e}", file=sys.stderr)

    all_results.sort(key=lambda x: -x[0])

    if output_json:
        print(json.dumps([r[1] for _, r in all_results], ensure_ascii=False, indent=2))
        return

    excellent = [s for s in all_results if s[0] >= 119]
    good = [s for s in all_results if 98 <= s[0] < 119]
    needs_work = [s for s in all_results if 70 <= s[0] < 98]
    failing = [s for s in all_results if s[0] < 70]

    print(f"\n{'#'*60}")
    print(f"#  📊 SQS v2.0 全量审计报告")
    print(f"#  扫描: {len(all_results)} skills  |  满分: 140")
    print(f"{'#'*60}")
    print(f"\n🟢 优秀 (119+):   {len(excellent)}")
    print(f"🟡 良好 (98-118):  {len(good)}")
    print(f"🟠 需改进 (70-97): {len(needs_work)}")
    print(f"🔴 不合格 (<70):   {len(failing)}")

    below = [s for s in all_results if s[0] < threshold]
    if below:
        print(f"\n⚠️  低于阈值 ({threshold}): {len(below)} 个:")
        for total, report in below[:15]:
            print(f"  {total:5.1f}  {report['skill']:30s} [{report['version']}]")
        if len(below) > 15:
            print(f"  ...及另外 {len(below)-15} 个")

    print(f"\n🏆 Top 5:")
    for total, report in all_results[:5]:
        print(f"  {total:5.1f}  {report['skill']:30s} [{report['version']}]")

    print(f"\n📉 Bottom 5:")
    for total, report in all_results[-5:]:
        print(f"  {total:5.1f}  {report['skill']:30s} [{report['version']}]")

    # 维度平均
    dims = {f"S{i}_": [] for i in range(1, 8)}
    dim_names = {
        "S1_": "元数据完整性", "S2_": "结构合规性", "S3_": "内容可执行性",
        "S4_": "时效性", "S5_": "关联完整性", "S6_": "可发现性", "S7_": "验证覆盖度",
    }
    for _, report in all_results:
        for dk, dv in report["dimensions"].items():
            for prefix in dims:
                if dk.startswith(prefix):
                    dims[prefix].append(dv)

    print(f"\n📊 维度平均分:")
    for prefix, scores in dims.items():
        if scores:
            avg = sum(scores) / len(scores)
            icon = "🟢" if avg >= 15 else ("🟡" if avg >= 10 else "🔴")
            bar = "█" * int(avg) + "░" * (20 - int(avg))
            name = dim_names.get(prefix, prefix)
            print(f"  {icon} {name}: {avg:5.1f}/20 {bar}")

    # 建议
    print(f"\n💡 改进建议 (维度平均 < 10 需重点改进):")
    for prefix, scores in dims.items():
        if scores:
            avg = sum(scores) / len(scores)
            name = dim_names.get(prefix, prefix)
            if avg < 8:
                print(f"  🔴 {name} ({avg:.1f}) 严重缺失")
            elif avg < 12:
                print(f"  🟡 {name} ({avg:.1f}) 需加强")

    print()


# ── 入口 ──────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    output_json = "--json" in sys.argv
    verbose = "--verbose" in sys.argv
    threshold = 70

    for i, arg in enumerate(sys.argv):
        if arg == "--threshold" and i + 1 < len(sys.argv):
            try:
                threshold = int(sys.argv[i + 1])
            except ValueError:
                pass

    if sys.argv[1] == "--audit":
        cmd_audit(threshold, output_json)
    else:
        calculate_sqs(sys.argv[1], verbose=verbose, output_json=output_json)


if __name__ == "__main__":
    main()
