#!/usr/bin/env python3
"""
spec-gate.py v1.0 — SDD 开发前门禁检查

在执行开发任务前检查：
1. 是否有对应的 Spec 文档？
2. Spec 是否处于 approved 或 in_progress 状态？
3. Spec 的 AC 是否可验证？

用法:
  python3 spec-gate.py check   <task_description>  # 检查（非阻塞）
  python3 spec-gate.py enforce <task_description>  # 强制（exit code 控制）
  python3 spec-gate.py verify  <story_id>          # 验证 Spec 完整性
  
输出:
  JSON 格式，包含 passed/failed、blockers、建议等
"""
import json
import os
import re
import sys
import glob
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPTS_DIR)
STATE_FILE = os.path.expanduser("~/.hermes/sdd_state.json")

# 搜索的目录
SEARCH_PATHS = [
    os.path.expanduser("~/projects/sra/docs/stories/"),
    os.path.expanduser("~/projects/sra/.hermes/plans/"),
    os.path.expanduser("~/projects/sra/docs/"),
]


def find_story_by_keyword(keyword):
    """通过关键词搜索所有 Story/Spec 文件"""
    results = []
    for base_path in SEARCH_PATHS:
        if not os.path.isdir(base_path):
            continue
        pattern = os.path.join(base_path, "**/*.md")
        for f in glob.glob(pattern, recursive=True):
            # 文件名匹配
            if keyword.lower() in os.path.basename(f).lower():
                results.append(f)
                continue
            # 内容匹配
            try:
                with open(f, encoding="utf-8") as fh:
                    content = fh.read()
                if keyword.lower() in content.lower():
                    results.append(f)
            except Exception:
                continue
    return list(set(results))  # 去重


def get_spec_status_from_file(spec_path):
    """从 Spec 文件的 frontmatter 读取 status 字段"""
    try:
        with open(spec_path, encoding="utf-8") as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                # 手动解析 status 行，不依赖 yaml 模块
                for line in parts[1].split("\n"):
                    line_stripped = line.strip()
                    if line_stripped.startswith("status:"):
                        status = line_stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        return status
        return None
    except Exception:
        return None


def get_meta_from_file(spec_path):
    """从 Spec 文件读取完整 frontmatter"""
    try:
        with open(spec_path, encoding="utf-8") as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                try:
                    import yaml
                    return yaml.safe_load(parts[1]) or {}
                except ImportError:
                    # 无 yaml 模块时手动解析关键字段
                    meta = {}
                    for line in parts[1].split("\n"):
                        m = re.match(r'^(\w+):\s*(.*)', line)
                        if m:
                            key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
                            meta[key] = val
                    return meta
        return {}
    except Exception:
        return {}


def check_gate(task_description):
    """执行 SDD 门禁检查（非阻塞）"""
    result = {
        "gate": "spec-approval",
        "passed": True,
        "spec_found": None,
        "spec_status": None,
        "message": "",
        "blockers": []
    }
    
    # Step 1: 找 Spec 文件
    specs_found = find_story_by_keyword(task_description)
    
    # 过滤：只保留 story 相关文件（排除 README 等）
    story_files = [f for f in specs_found if "STORY-" in os.path.basename(f) 
                   or "story-" in os.path.basename(f).lower()
                   or "EPIC-" in os.path.basename(f)]
    
    if not story_files:
        # 试着找 Sprint Plan
        plan_files = [f for f in specs_found if "plan" in os.path.basename(f).lower()]
        if plan_files:
            result["spec_found"] = plan_files[0]
            result["spec_status"] = "plan"
            result["message"] = f"⚠️  找到 Sprint Plan，但不是正式 Story Spec: {os.path.basename(plan_files[0])}"
            result["passed"] = True  # 有 Plan 也可以开发
            return result
        
        result["passed"] = False
        result["blockers"].append(f"任务 '{task_description}' 没有对应的 Spec 文档")
        result["message"] = f"❌ BLOCKED: 未找到 Spec。请先用 docs/STORY-TEMPLATE.md 创建"
        return result
    
    # Step 2: 检查 Spec 状态
    spec_path = story_files[0]
    result["spec_found"] = spec_path
    status = get_spec_status_from_file(spec_path)
    result["spec_status"] = status
    
    if status in ("approved", "in_progress"):
        result["message"] = f"✅ Spec 已批准（{status}），可以开始开发"
        return result
    
    elif status == "completed":
        result["message"] = f"⚠️  Spec 已完成（{status}），如有新的改动请创建新 Spec"
        result["passed"] = True
        return result
    
    elif status == "draft":
        result["passed"] = False
        result["blockers"].append(f"Spec '{os.path.basename(spec_path)}' 状态为 draft（未提交审阅）")
        result["message"] = "❌ BLOCKED: Spec 未提交审阅"
        return result
    
    elif status == "review":
        result["passed"] = False
        result["blockers"].append(f"Spec '{os.path.basename(spec_path)}' 正在审阅中，等待主人批准")
        result["message"] = "❌ BLOCKED: Spec 正在审阅中"
        return result
    
    else:
        result["passed"] = False
        result["blockers"].append(f"Spec 状态异常: {status}")
        result["message"] = f"❌ BLOCKED: Spec 状态异常（{status}）"
        return result


def enforce_gate(task_description):
    """强制门禁检查 — 失败时 exit code=1"""
    result = check_gate(task_description)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if not result["passed"]:
        print("\n🛑 SDD 门禁拦截！先创建 Spec 再开发。")
        print("   模板: docs/STORY-TEMPLATE.md（或用 sdd-workflow skill）")
        sys.exit(1)
    
    sys.exit(0)


def verify_spec(story_id):
    """验证 Spec 的完整性"""
    # 查找 Spec 文件
    spec_path = None
    for base_path in SEARCH_PATHS:
        if not os.path.isdir(base_path):
            continue
        for f in glob.glob(os.path.join(base_path, "**/*.md"), recursive=True):
            if story_id in os.path.basename(f) and f.endswith(".md"):
                spec_path = f
                break
        if spec_path:
            break
    
    if not spec_path:
        print(f"❌ 未找到 Spec: {story_id}")
        sys.exit(1)
    
    meta = get_meta_from_file(spec_path)
    with open(spec_path, encoding="utf-8") as f:
        content = f.read()
    
    checks = {
        "story_id": story_id in content,
        "has_status": "status:" in content,
        "has_acceptance_criteria": "Acceptance Criteria" in content or "AC-" in content,
        "has_user_story": "As a" in content and "I want" in content,
        "has_test_data": "test_data" in content or "test_data_contract" in content,
        "has_out_of_scope": "out_of_scope" in content or "Out of scope" in content,
        "has_spec_references": "spec_references" in content or "EPIC-" in content,
    }
    
    print(f"📋 Spec 完整性检查: {os.path.basename(spec_path)}")
    print("=" * 50)
    
    all_pass = True
    for check_name, passed in checks.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {check_name}")
        if not passed:
            all_pass = False
    
    print()
    if all_pass:
        print("✅ Spec 完整性检查通过")
    else:
        print("⚠️  Spec 完整性检查有未通过项")
    
    return all_pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  spec-gate.py check   <task_description>   # 检查（非阻塞，输出 JSON）")
        print("  spec-gate.py enforce <task_description>   # 强制（exit code=1 时拦截）")
        print("  spec-gate.py verify  <story_id>           # 验证 Spec 完整性")
        sys.exit(1)
    
    action = sys.argv[1]
    arg = sys.argv[2]
    
    if action == "check":
        result = check_gate(arg)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif action == "enforce":
        enforce_gate(arg)
    elif action == "verify":
        verify_spec(arg)
    else:
        print(f"❌ 未知操作: {action}")
        sys.exit(1)
