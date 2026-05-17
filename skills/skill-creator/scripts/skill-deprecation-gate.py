#!/usr/bin/env python3
"""
skill-deprecation-gate.py v1.0 — Skill 废弃/删除门禁

在标记 deprecated 或删除前检查:
  1. 引用链分析（哪些 skill 依赖此 skill）
  2. 是否已 >= 30 天 deprecated
  3. 替代 skill 是否已声明
  4. 是否有备份/归档

用法:
  python3 skill-deprecation-gate.py check <skill-name>           # 检查
  python3 skill-deprecation-gate.py check <skill-name> --json    # JSON
  python3 skill-deprecation-gate.py pre-deprecate <skill-name>   # 废弃前检查
  python3 skill-deprecation-gate.py pre-delete <skill-name>      # 删除前检查
  python3 skill-deprecation-gate.py --help                       # 帮助
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
LIFECYCLE_FILE = Path.home() / ".hermes" / "skill_lifecycle_state.json"
NOW = datetime.now(timezone.utc)

# ── 检查函数 ──────────────────────────────────────────────────

def find_referrers(skill_name):
    """查找引用此 skill 的其他 skill"""
    referrers = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            try:
                content = (Path(root) / "SKILL.md").read_text(encoding="utf-8")
                fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if fm_match:
                    import yaml
                    fm = yaml.safe_load(fm_match.group(1)) or {}
                    depends = fm.get("depends_on", []) or []
                    related = fm.get("related_skills", []) or []

                    if skill_name in depends:
                        referrers.append({"skill": os.path.basename(root), "type": "depends_on"})
                    elif skill_name in related:
                        referrers.append({"skill": os.path.basename(root), "type": "related"})
            except Exception:
                pass
    return referrers


def check_lifecycle_state(skill_name):
    """检查生命周期状态"""
    state = {}
    if LIFECYCLE_FILE.exists():
        try:
            state = json.loads(LIFECYCLE_FILE.read_text())
        except Exception:
            pass
    return state.get("skills", {}).get(skill_name, {})


def find_backup(skill_name):
    """查找是否有备份"""
    hermes_home = os.path.expanduser("~/.hermes")
    archive_dir = Path(hermes_home) / "archive" / "skills"
    if archive_dir.exists():
        backups = list(archive_dir.glob(f"{skill_name}*"))
        return backups
    return []


def run_checks(skill_name, mode="check"):
    """执行所有废弃/删除门禁检查"""
    result = {
        "pass": True,
        "skill": skill_name,
        "mode": mode,
        "failures": [],
        "warnings": [],
        "info": {},
    }

    # 1. 查找引用者
    referrers = find_referrers(skill_name)
    result["info"]["referrers"] = [r["skill"] for r in referrers]
    result["info"]["referrer_count"] = len(referrers)

    if referrers and mode in ("pre-deprecate", "pre-delete"):
        pass
        # Warning but not blocking - owner can override
        result["warnings"].append(
            f"被 {len(referrers)} 个 skill 引用: {', '.join(r['skill'] for r in referrers[:8])}"
        )

    # 2. 检查生命周期状态
    lc = check_lifecycle_state(skill_name)
    status = lc.get("status", "active")

    if mode == "pre-delete":
        if status not in ("deprecated", "archived"):
            result["failures"].append({
                "field": "status",
                "issue": f"当前状态 '{status}'，删除前应先标记 deprecated 或 archived"
            })
            result["pass"] = False

        if status == "deprecated":
            dep_at = lc.get("deprecated_at", "")
            if dep_at:
                try:
                    dep_date = datetime.fromisoformat(dep_at)
                    days = (NOW - dep_date).days
                    if days < 30:
                        result["warnings"].append(
                            f"废弃仅 {days} 天（建议 ≥30 天后再删除）"
                        )
                except (ValueError, TypeError):
                    pass

    # 3. 检查是否有替代声明
    replaced_by = lc.get("replaced_by", "")
    result["info"]["replaced_by"] = replaced_by or "无"
    if mode in ("pre-deprecate", "pre-delete") and not replaced_by:
        result["warnings"].append("未声明替代 skill (replaced_by)")

    # 4. 查找备份
    backups = find_backup(skill_name)
    result["info"]["backups"] = len(backups)
    if mode == "pre-delete" and not backups:
        result["warnings"].append("无备份，删除后不可恢复")

    # 5. SKILL.md 存在性
    sk_path = SKILLS_DIR / skill_name / "SKILL.md"
    result["info"]["exists"] = sk_path.exists()
    if not sk_path.exists():
        if mode not in ("pre-delete",):
            result["failures"].append({"field": "existence", "issue": "SKILL.md 不存在"})
            result["pass"] = False

    # 6. 最后修改时间
    if sk_path.exists():
        mtime = datetime.fromtimestamp(sk_path.stat().st_mtime, tz=timezone.utc)
        days = (NOW - mtime).days
        result["info"]["last_modified_days"] = days
        if mode == "pre-deprecate" and days < 7:
            result["warnings"].append("该 skill 最近 7 天内刚修改过，确认要废弃吗？")

    return result


def print_result(result, output_json=False):
    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    mode_labels = {
        "check": "检查",
        "pre-deprecate": "废弃前检查",
        "pre-delete": "删除前检查",
    }
    label = mode_labels.get(result["mode"], result["mode"])

    icon = "✅" if result["pass"] else "🛑"
    print(f"\n{icon} 废弃门禁: {result['skill']} ({label})")
    print(f"  {'='*50}")
    print(f"  引用: {result['info'].get('referrer_count', 0)} 个 skill")
    refs = result['info'].get('referrers', [])
    if refs:
        print(f"    引用者: {', '.join(refs[:8])}")
    print(f"  替代: {result['info'].get('replaced_by', '无')}")
    print(f"  备份: {result['info'].get('backups', 0)} 个")
    print(f"  存在: {'✅' if result['info'].get('exists') else '❌'}")

    lmd = result['info'].get('last_modified_days')
    if lmd is not None:
        print(f"  最后修改: {lmd} 天前")

    if result["failures"]:
        print(f"\n  ❌ 失败 ({len(result['failures'])}):")
        for f in result["failures"]:
            print(f"    • [{f['field']}] {f['issue']}")

    if result["warnings"]:
        print(f"\n  ⚠️  警告 ({len(result['warnings'])}):")
        for w in result["warnings"]:
            print(f"    • {w}")

    if result["pass"] and not result["warnings"]:
        print(f"\n  ✅ 可以安全执行此操作")
    elif result["pass"]:
        print(f"\n  ⚠️  可以执行（请确认以上警告）")

    print()


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    mode = sys.argv[1]
    skill_name = sys.argv[2]
    output_json = "--json" in sys.argv

    if mode not in ("check", "pre-deprecate", "pre-delete"):
        print(f"❌ 未知模式: {mode}")
        sys.exit(1)

    result = run_checks(skill_name, mode)
    print_result(result, output_json)

    if not result["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
