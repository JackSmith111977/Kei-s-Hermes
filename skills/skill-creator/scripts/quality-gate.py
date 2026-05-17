#!/usr/bin/env python3
"""
quality-gate.py v1.0 — Skill 操作质量门禁

在 skill_manage 操作前自动检查：
  1. SQS 是否 ≥ 阈值（创建 ≥ 50，修改 ≥ 30）
  2. 是否存在断裂引用
  3. YAML frontmatter 是否完整
  4. name 与目录名是否一致
  5. 文件命名是否规范

用法:
  python3 quality-gate.py create <skill-name>   # 创建前检查
  python3 quality-gate.py edit <skill-name>     # 修改前检查
  python3 quality-gate.py delete <skill-name>   # 删除前检查
  python3 quality-gate.py check <skill-name>    # 仅检查
  python3 quality-gate.py check <skill-name> --json  # JSON 输出
  python3 quality-gate.py --help                # 帮助
"""

import json
import os
import re
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
SQS_SCRIPT = SKILLS_DIR / "skill-creator" / "scripts" / "skill-quality-score.py"

# ── 门禁阈值 ──────────────────────────────────────────────────
THRESHOLDS = {
    "create": 50,    # 创建需要 ≥ 50
    "edit": 30,      # 修改需要 ≥ 30（允许小幅改进）
    "delete": 0,     # 删除不做 SQS 检查（但做引用检查）
    "check": 0,      # 仅检查
}

# 禁止的文件名
FORBIDDEN_FILENAMES = {"test.txt", "output.json", "file.py", "new_1.md",
                        "untitled.md", "tmp.txt", "index.html"}
FORBIDDEN_CHARS = set(' \\:*?"<>|')


def get_sqs(skill_name):
    """调用 SQS 脚本获取评分"""
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(SQS_SCRIPT), skill_name, "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        return None
    except Exception:
        return None


def check_frontmatter(skill_dir):
    """检查 YAML frontmatter 完整性"""
    failures = []
    sk_path = skill_dir / "SKILL.md"

    if not sk_path.exists():
        return [{"field": "SKILL.md", "issue": "文件不存在"}]

    content = sk_path.read_text(encoding="utf-8")

    # 检查 frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return [{"field": "frontmatter", "issue": "缺失 YAML frontmatter"}]

    try:
        import yaml
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except Exception as e:
        return [{"field": "frontmatter", "issue": f"YAML 解析错误: {e}"}]

    # 检查必填字段
    required = ["name", "version", "description"]
    for field in required:
        if not fm.get(field):
            failures.append({"field": field, "issue": f"缺失必填字段"})

    # 检查 name 是否匹配目录名
    dir_name = skill_dir.name
    if fm.get("name") and fm["name"] != dir_name:
        failures.append({"field": "name", "issue": f"'{fm['name']}' ≠ 目录名 '{dir_name}'"})

    return failures


def check_broken_refs(skill_name):
    """检查断裂引用"""
    failures = []
    sk_path = SKILLS_DIR / skill_name / "SKILL.md"

    if not sk_path.exists():
        return []

    content = sk_path.read_text(encoding="utf-8")
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return []

    try:
        import yaml
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except Exception:
        return []

    depends = fm.get("depends_on", []) or []
    for dep in depends:
        if isinstance(dep, str):
            dep_path = SKILLS_DIR / dep / "SKILL.md"
            if not dep_path.exists():
                failures.append({
                    "field": "depends_on",
                    "issue": f"依赖的 skill '{dep}' 不存在",
                })

    return failures


def check_naming(skill_name):
    """检查命名规范"""
    failures = []
    sk_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not sk_path.exists():
        return []

    # 检查文件名
    for item in (sk_path.parent).iterdir():
        if item.is_file() and item.name not in ("SKILL.md",):
            bn = item.name.lower()
            if bn in FORBIDDEN_FILENAMES:
                failures.append({"field": "filename", "issue": f"禁止的文件名: {item.name}"})
            for c in FORBIDDEN_CHARS:
                if c in item.name:
                    failures.append({"field": "filename", "issue": f"文件名含禁止字符: {item.name}"})
                    break

    return failures


def run_checks(skill_name, action):
    """执行所有门禁检查"""
    result = {
        "pass": True,
        "skill": skill_name,
        "action": action,
        "failures": [],
        "warnings": [],
        "sqs_score": None,
    }

    # 1. SQS 评分检查
    sqs = get_sqs(skill_name)
    threshold = THRESHOLDS.get(action, 0)

    if sqs and "error" not in sqs:
        total = sqs.get("sqs_total", 0)
        result["sqs_score"] = total

        if action in ("create", "edit") and total < threshold:
            result["failures"].append({
                "field": "sqs",
                "issue": f"SQS {total}/140 < 阈值 {threshold} (操作: {action})",
                "details": sqs.get("dimensions", {}),
            })
            result["pass"] = False

        if total < 30:
            result["warnings"].append(f"SQS 分数极低 ({total}/140)，建议重建而非修改")
    else:
        if action in ("create",):
            # 新建时 SQS 不可用正常
            pass
        else:
            result["warnings"].append(f"无法获取 SQS 评分 (skill 可能不存在)")

    # 2. 检查 frontmatter（仅对已存在的 skill）
    skill_dir = SKILLS_DIR / skill_name
    if skill_dir.exists():
        fm_failures = check_frontmatter(skill_dir)
        for f in fm_failures:
            result["failures"].append(f)
            result["pass"] = False

    # 3. 检查断裂引用
    ref_failures = check_broken_refs(skill_name)
    for f in ref_failures:
        result["failures"].append(f)
        result["pass"] = False

    # 4. 检查命名规范
    naming_failures = check_naming(skill_name)
    for f in naming_failures:
        result["failures"].append(f)
        result["pass"] = False

    # 5. 删除前引用检查
    if action == "delete":
        # 查找引用此 skill 的其他 skill
        referrers = []
        for root, dirs, files in os.walk(SKILLS_DIR):
            if "SKILL.md" in files:
                try:
                    ref_content = (Path(root) / "SKILL.md").read_text(encoding="utf-8")
                    ref_match = re.match(r'^---\n(.*?)\n---', ref_content, re.DOTALL)
                    if ref_match:
                        import yaml
                        ref_fm = yaml.safe_load(ref_match.group(1)) or {}
                        depends = ref_fm.get("depends_on", []) or []
                        if skill_name in depends:
                            referrers.append(os.path.basename(root))
                except Exception:
                    pass
        if referrers:
            result["failures"].append({
                "field": "referenced_by",
                "issue": f"被 {len(referrers)} 个 skill 引用: {', '.join(referrers[:10])}",
            })
            result["pass"] = False

    return result


def print_result(result, output_json=False):
    """输出检查结果"""
    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    icon = "✅" if result["pass"] else "🛑"
    print(f"\n{icon} 质量门禁检查: {result['skill']} (操作: {result['action']})")
    print(f"  {'='*50}")

    if result["sqs_score"] is not None:
        print(f"  SQS 评分: {result['sqs_score']}/140")

    if result["failures"]:
        print(f"\n  ❌ 失败 ({len(result['failures'])} 项):")
        for f in result["failures"]:
            print(f"    • [{f['field']}] {f['issue']}")

    if result["warnings"]:
        print(f"\n  ⚠️  警告 ({len(result['warnings'])} 项):")
        for w in result["warnings"]:
            print(f"    • {w}")

    if result["pass"]:
        print(f"\n  ✅ 所有检查通过！")
    print()


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    action = sys.argv[1]
    skill_name = sys.argv[2]
    output_json = "--json" in sys.argv

    if action not in THRESHOLDS:
        print(f"❌ 未知操作: {action}")
        print(f"   有效操作: {', '.join(THRESHOLDS.keys())}")
        sys.exit(1)

    result = run_checks(skill_name, action)
    print_result(result, output_json)

    if not result["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
