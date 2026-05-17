#!/usr/bin/env python3
"""
pre_flight.py v2.0 — 通用守门员（Gateway Guardian）

在接到任何新任务时必须首先运行。执行三类检查：
  1. 学习状态检查（learning_state.json 是否存在）
  2. SDD 门禁检查（复杂任务是否需要 Story）
  3. Skill/CapPack 操作检测（是否需加载 skill-creator / pack 工具链）

用法:
  python3 ~/.hermes/scripts/pre_flight.py "<Task Description>"

输出:
  - PASS + 0 → 可继续
  - BLOCKED + 非 0 → 必须先处理阻塞项
"""

import os, sys, json, subprocess, re
from datetime import datetime

HERMES_DIR = os.path.expanduser("~/.hermes")
STATE_FILE = os.path.join(HERMES_DIR, "learning_state.json")
SDD_GATE = os.path.join(HERMES_DIR, "skills/sdd-workflow/scripts/spec-gate.py")
SDD_STATE = os.path.join(HERMES_DIR, "sdd_state.json")
SKILL_CREATOR_DIR = os.path.join(HERMES_DIR, "skills/skill-creator")
SQS_SCRIPT = os.path.join(SKILL_CREATOR_DIR, "scripts/skill-quality-score.py")

PASS = 0
BLOCKED = 1


def section(title):
    """打印分段标题"""
    print(f"\n{'='*55}")
    print(f"  🔍 {title}")
    print(f"{'='*55}")


def check_learning_state(task):
    """检查 1: 学习状态"""
    section("Gate 1/3: 学习状态检查")

    if not os.path.exists(STATE_FILE):
        print("  ❌ BLOCKED: learning_state.json 不存在")
        print("  💡 运行: python3 ~/.hermes/skills/learning-workflow/"
              "scripts/learning-state.py init \"<task>\"")
        return BLOCKED

    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except:
        print("  ❌ BLOCKED: learning_state.json 损坏")
        return BLOCKED

    topic = state.get("current_task") or state.get("topic", "")
    current_step = state.get("current_step", -1)
    workflow_steps = state.get("workflow_steps", {})

    # 检查状态
    pre_flight_done = workflow_steps.get("STEP_0_pre_flight", {}).get("completed", False)
    skill_scan_done = workflow_steps.get("STEP_1_skill_scan", {}).get("completed", False)

    print(f"  📋 当前任务: {topic or '(空)'}")
    print(f"  📋 Step: {current_step}")
    print(f"  📋 pre_flight: {'✅' if pre_flight_done else '❌'}")
    print(f"  📋 skill_scan: {'✅' if skill_scan_done else '❌'}")

    # 若当前任务不同，提醒初始化新任务
    if topic and task.lower() not in topic.lower():
        print(f"  ⚠️  当前学习任务 '{topic}' 与本次任务 '{task}' 不同")
        print(f"  💡 如需新任务: learning-state.py init \"{task}\"")

    print("  ✅ 学习状态存在")
    return PASS


def check_sdd_gate(task):
    """检查 2: SDD 门禁"""
    section("Gate 2/3: SDD 门禁检查")

    # 检测是否为技能操作（不需要 SDD 的特殊场景）
    skill_ops = [
        r'skill.*(create|edit|update|delete|patch)',
        r'创建.*skill|编辑.*skill|更新.*skill',
        r'skill_manage',
        r'dependency.?scan',
        r'查看.*skill|列出.*skill|浏览.*skill',
    ]
    is_skill_op = any(re.search(p, task.lower()) for p in skill_ops)

    if is_skill_op:
        print("  ⏭️  技能操作任务，不强制 SDD（转到 skill-creator 检查）")
        return PASS

    # 检查 SDD 门禁脚本是否存在
    if not os.path.exists(SDD_GATE):
        print("  ⚠️  spec-gate.py 不存在，跳过 SDD 门禁")
        return PASS

    if not os.path.exists(SDD_STATE):
        print("  ⚠️  sdd_state.json 不存在，跳过 SDD 门禁")
        return PASS

    # 运行 SDD 门禁
    try:
        result = subprocess.run(
            [sys.executable, SDD_GATE, "check", task],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()
        if result.returncode != 0 or "BLOCKED" in output or '"passed": false' in output:
            print(f"  ❌ SDD 门禁未通过")
            # 提取关键信息
            for line in output.split('\n'):
                if 'message' in line or 'blocker' in line or 'story_id' in line:
                    print(f"     {line.strip()}")
            print("  💡 先创建 Story: python3 spec-state.py create <id> \"<title>\"")
            return BLOCKED
        else:
            # 提取通过信息
            for line in output.split('\n'):
                if 'message' in line:
                    print(f"  {line.strip()}")
            print("  ✅ SDD 门禁通过")
            return PASS
    except subprocess.TimeoutExpired:
        print("  ⚠️  SDD 门禁超时，跳过")
        return PASS
    except Exception as e:
        print(f"  ⚠️  SDD 门禁异常 ({e})，跳过")
        return PASS


def check_skill_creator_need(task):
    """检查 3: 检测是否需要 skill-creator"""
    section("Gate 3/3: 技能/包操作检测")

    skill_indicators = [
        (r'skill.*(create|edit|update|delete|patch|fix)', "创建/编辑 Skill"),
        (r'创建.*skill|编辑.*skill|更新.*skill|删除.*skill|修改.*skill', "Skill CRUD"),
        (r'skill_manage', "skill_manage 操作"),
        (r'dependency.?scan|依赖扫描', "依赖扫描"),
        (r'优化.*skill|skill.*优化', "Skill 优化"),
        (r'评估.*skill|skill.*评估|skill.*eval', "Skill 评估"),
    ]

    pack_indicators = [
        (r'capability.*pack|能力包|cap-pack', "能力包操作"),
        (r'extract.*pack|提取.*包', "提取能力包"),
        (r'install.*pack|安装.*包', "安装能力包"),
        (r'packs?/.*/cap-pack', "能力包文件操作"),
    ]

    found_skills = [desc for pattern, desc in skill_indicators if re.search(pattern, task.lower())]
    found_packs = [desc for pattern, desc in pack_indicators if re.search(pattern, task.lower())]

    need_skill_creator = bool(found_skills)
    need_pack_tools = bool(found_packs)

    if need_skill_creator:
        print(f"  🎯 检测到技能操作: {', '.join(found_skills)}")
        print(f"  📌 必须加载 skill-creator:")
        print(f"     skill_view(name='skill-creator')")

        # 自动 SQS 质量检查
        target_skill = None
        for word in re.findall(r'[a-zA-Z][a-zA-Z0-9_-]{2,}', task):
            skill_path = os.path.join(HERMES_DIR, "skills", word)
            if os.path.isdir(skill_path) and os.path.exists(
                    os.path.join(skill_path, "SKILL.md")):
                target_skill = word
                break

        if target_skill and os.path.exists(SQS_SCRIPT):
            print(f"  📌 自动运行 SQS 质量检查...")
            try:
                sqs_result = subprocess.run(
                    [sys.executable, SQS_SCRIPT, target_skill, "--json"],
                    capture_output=True, text=True, timeout=15
                )
                if sqs_result.returncode == 0:
                    sqs_data = json.loads(sqs_result.stdout)
                    total = sqs_data.get("sqs_total", 0)
                    level = sqs_data.get("level", "?")
                    max_score = sqs_data.get("max_score", 140)
                    print(f"     SQS v2.0: {total}/{max_score} {level}")
                    if total < 70:
                        print(f"     🔴 质量分过低，禁止部署！")
                        print(f"     💡 建议先改进: ", end="")
                        weak = [d for d, s in sqs_data.get("dimensions", {}).items() if s < 10]
                        print(", ".join(weak) if weak else "全部维度")
                    elif total < 98:
                        print(f"     🟡 可优化维度: ", end="")
                        weak = [d for d, s in sqs_data.get("dimensions", {}).items() if s < 12]
                        print(", ".join(weak) if weak else "无")
                    else:
                        print(f"     🟢 质量良好")
            except Exception as e:
                print(f"     ⚠️ SQS 异常: {e}")

        if os.path.exists(os.path.join(SKILL_CREATOR_DIR, "scripts/dependency-scan.py")):
            print(f"  📌 自动运行定向依赖扫描...")
            try:
                if not target_skill:
                    for word in re.findall(r'[a-zA-Z][a-zA-Z0-9_-]{2,}', task):
                        skill_path2 = os.path.join(HERMES_DIR, "skills", word)
                        if os.path.isdir(skill_path2) and os.path.exists(
                                os.path.join(skill_path2, "SKILL.md")):
                            target_skill = word
                            break
                if target_skill:
                    scan_result = subprocess.run(
                        [sys.executable, 
                         os.path.join(SKILL_CREATOR_DIR, "scripts/dependency-scan.py"),
                         "--target", target_skill],
                        capture_output=True, text=True, timeout=30
                    )
                    for line in scan_result.stdout.split('\n')[:15]:
                        print(f"     {line}")
                else:
                    print(f"     运行: dependency-scan.py --target <skill-name>")
                    print(f"     (未从任务描述中识别到具体 skill 名称)")
            except Exception as e:
                print(f"     ⚠️ 扫描异常: {e}")

    if need_pack_tools:
        print(f"  🎯 检测到能力包操作: {', '.join(found_packs)}")
        PROJECT_DIR = os.path.expanduser("~/projects/hermes-cap-pack")
        if os.path.exists(PROJECT_DIR):
            print(f"  📌 能力包项目: {PROJECT_DIR}")
            print(f"  📌 格式规范: schemas/cap-pack-format-v1.md")
            print(f"  📌 验证: python3 -c \"import yaml, json; "
                  "json.load(open('schemas/cap-pack-v1.schema.json')); "
                  "yaml.safe_load(open('packs/doc-engine/cap-pack.yaml'))\"")

    if not need_skill_creator and not need_pack_tools:
        print("  ⏭️  未检测到技能/包操作")

    # ── skill-quality enhancer 集成 ──
    ENHANCER = os.path.expanduser(
        "~/.hermes/cap-packs/skill-quality/scripts/pre-flight-enhancer.py")
    if not os.path.exists(ENHANCER):
        ENHANCER = os.path.expanduser(
            "~/projects/hermes-cap-pack/packs/skill-quality/scripts/pre-flight-enhancer.py")
    if os.path.exists(ENHANCER):
        try:
            enh_result = subprocess.run(
                [sys.executable, ENHANCER, task, "--json"],
                capture_output=True, text=True, timeout=10
            )
            if enh_result.returncode == 0:
                enh_data = json.loads(enh_result.stdout)
                analysis = enh_data.get("analysis", {})
                if analysis.get("is_skill_operation"):
                    detected_skill = analysis.get("detected_skill_name")
                    path_match = analysis.get("matches_skill_dir")
                    conf = analysis.get("confidence", 0)
                    print(f"\n  🔎 [skill-quality 增强检测]")
                    print(f"     操作类型: {analysis.get('operation_type', '?')}")
                    if detected_skill:
                        print(f"     检测到 skill: {detected_skill}")
                    if path_match:
                        print(f"     路径匹配: 检测到 skill 目录文件操作")
                    print(f"     置信度: {conf:.0%}")
                    
                    # Check for gaps
                    gaps = enh_data.get("recommendation", {}).get("pre_flight_gaps", [])
                    if gaps:
                        print(f"     ⚠️ pre_flight 遗漏:")
                        for g in gaps:
                            print(f"        • {g}")
                    
                    # If it's a delete operation, run delete gate
                    if analysis.get("operation_type") == "delete" and detected_skill:
                        DELETE_GATE = os.path.join(os.path.dirname(ENHANCER),
                                                    "skill-delete-gate.py")
                        if os.path.exists(DELETE_GATE):
                            del_result = subprocess.run(
                                [sys.executable, DELETE_GATE, detected_skill, "--json"],
                                capture_output=True, text=True, timeout=15
                            )
                            if del_result.returncode == 0:
                                del_data = json.loads(del_result.stdout)
                                if not del_data.get("passed", True):
                                    blocks = del_data.get("blocks", [])
                                    refs = del_data.get("referrers", [])
                                    print(f"     🗑️  删除门禁: ❌ BLOCKED")
                                    for b in blocks:
                                        print(f"        • {b}")
                                    if refs:
                                        print(f"        引用者 ({len(refs)}):")
                                        for r in refs[:3]:
                                            print(f"          - {r['skill']}")
                                        if len(refs) > 3:
                                            print(f"          ...及另外 {len(refs)-3} 个")
                    
                    # If it's a create operation, run create gate
                    if analysis.get("operation_type") in ("create", "edit") and detected_skill:
                        CREATE_GATE = os.path.join(os.path.dirname(ENHANCER),
                                                    "skill-create-gate.py")
                        if os.path.exists(CREATE_GATE):
                            cr_result = subprocess.run(
                                [sys.executable, CREATE_GATE, detected_skill, "--json"],
                                capture_output=True, text=True, timeout=10
                            )
                            if cr_result.returncode == 0:
                                cr_data = json.loads(cr_result.stdout)
                                if not cr_data.get("passed", True):
                                    print(f"     📝 创建门禁: ❌ 冲突")
                                    for i in cr_data.get("issues", []):
                                        print(f"        • {i}")
                                elif cr_data.get("warnings"):
                                    print(f"     📝 创建门禁: ✅ 但需注意")
                                    for w in cr_data.get("warnings", []):
                                        print(f"        • {w}")
        except Exception as e:
            print(f"  ⚠️ skill-quality enhancer 异常: {e}")

    return PASS


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "未知任务"
    print(f"\n{'#'*55}")
    print(f"#  🛡️  PRE-FLIGHT CHECK v2.0")
    print(f"#  任务: {task}")
    print(f"{'#'*55}")

    gates = [
        ("学习状态", check_learning_state(task)),
        ("SDD 门禁", check_sdd_gate(task)),
        ("技能/包检测", check_skill_creator_need(task)),
    ]

    # 汇总
    print(f"\n{'='*55}")
    print(f"  📊 门禁汇总")
    print(f"{'='*55}")
    all_pass = True
    for name, result in gates:
        status = "✅ PASS" if result == PASS else "❌ BLOCKED"
        if result != PASS:
            all_pass = False
        print(f"  {status} {name}")

    if all_pass:
        print(f"\n  🎉 全部门禁通过！可以继续。")
        print(f"  ⏭️  下一步: skill_finder.py")
        sys.exit(PASS)
    else:
        print(f"\n  🛑 存在阻塞项！必须先处理再继续。")
        sys.exit(BLOCKED)


if __name__ == "__main__":
    main()
