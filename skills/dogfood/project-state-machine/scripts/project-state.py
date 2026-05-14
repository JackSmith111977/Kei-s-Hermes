#!/usr/bin/env python3
"""
project-state.py v1.0 — 项目统一状态机管理器

用法:
  python3 scripts/project-state.py status              # 显示当前状态
  python3 scripts/project-state.py scan                # 扫描 SDD 文档，检测漂移
  python3 scripts/project-state.py verify              # 一致性验证 (exit code)
  python3 scripts/project-state.py list                # 列出所有实体及状态
  python3 scripts/project-state.py list --by-state     # 按状态分组
  python3 scripts/project-state.py list --by-type      # 按类型分组
  python3 scripts/project-state.py gate <entity> <to>  # 门禁检查（不执行）
  python3 scripts/project-state.py transition <entity> <to> [reason]  # 状态转换 + 门禁
  python3 scripts/project-state.py sync                # 同步 SDD 文档状态到 YAML
  python3 scripts/project-state.py history             # 查看变更历史
"""

import sys
import os
import re
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_DIR / "docs" / "project-state.yaml"
SDD_DIR = PROJECT_DIR / "docs"
STORY_DIR = SDD_DIR / "stories"

SDD_STATES = ["draft", "review", "approved", "architect", "plan", "implement", "completed", "archived"]
EPIC_STATES = ["draft", "create", "qa_gate", "review", "approved"]
SPRINT_STATES = ["planning", "in_progress", "released"]


def load_state():
    import yaml
    if not STATE_FILE.exists():
        print(f"❌ STATE_FILE not found: {STATE_FILE}")
        print("   从 unified-state-machine skill 复制模板:")
        print("   cp ~/.hermes/skills/dogfood/project-state-machine/templates/project-state.yaml docs/")
        sys.exit(1)
    with open(STATE_FILE, "r") as f:
        return yaml.safe_load(f)


def save_state(state):
    import yaml
    with open(STATE_FILE, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✅ 已保存状态到 {STATE_FILE}")


def get_doc_states():
    doc_states = {"epics": {}, "specs": {}, "stories": {}}
    for f in sorted(SDD_DIR.glob("EPIC-*.md")):
        text = f.read_text()
        m = re.search(r'\*\*状态\*\*:\s*`(\w+)`', text) or re.search(r'\*\*status\*\*:\s*`(\w+)`', text)
        if m:
            eid = f.stem.split("-")[0] + "-" + f.stem.split("-")[1]
            doc_states["epics"][eid] = m.group(1)
    for f in sorted(SDD_DIR.glob("SPEC-*.md")):
        text = f.read_text()
        m = re.search(r'\*\*状态\*\*:\s*`(\w+)`', text) or re.search(r'\*\*status\*\*:\s*`(\w+)`', text)
        if m:
            doc_states["specs"][f.stem] = m.group(1)
    for f in sorted(STORY_DIR.glob("STORY-*.md")):
        text = f.read_text()
        m = re.search(r'\*\*状态\*\*:\s*`(\w+)`', text) or re.search(r'\*\*status\*\*:\s*`(\w+)`', text)
        if m:
            doc_states["stories"][f.stem] = m.group(1)
    return doc_states


def cmd_status():
    state = load_state()
    p = state["project"]
    q = state["quality"]
    print(f"\n{'='*60}")
    print(f"  📊 {p['name']} v{p['version']} — 统一状态机")
    print(f"  Phase: {p['current_phase']} · 总体状态: {p['overall_state']}")
    print(f"{'='*60}")
    print(f"\n📋 Epics:")
    for eid, e in state["entities"]["epics"].items():
        print(f"  {eid:12s} [{e['state']:10s}] {e['title'][:50]} ({e['completed_count']}/{e['story_count']})")
    print(f"\n📄 Specs:")
    for sid, s in state["entities"]["specs"].items():
        print(f"  {sid:12s} [{s['state']:10s}] {s['epic']} · {len(s.get('stories',[]))} stories")
    print(f"\n🏃 Sprints:")
    for spid, sp in state.get("sprints", {}).items():
        print(f"  {spid:12s} [{sp['state']:10s}] {sp.get('title','')} ({sp['stories_completed']}/{sp['stories_planned']})")
    print(f"\n📈 质量指标:")
    print(f"  SQS: {q['sqs']['avg']}/{q['sqs']['target']}  Tests: {q['tests']['passing']}/{q['tests']['count']}  CHI: {q['chi']['value']}/{q['chi']['target']}")
    print()


def cmd_verify():
    state = load_state()
    doc_states = get_doc_states()
    errors = []
    warnings = []
    for eid, e in state["entities"]["epics"].items():
        doc_s = doc_states["epics"].get(eid)
        if doc_s and doc_s != e["state"]:
            errors.append(f"🔴 EPIC {eid}: YAML={e['state']}, DOC={doc_s}")
        elif not doc_s:
            warnings.append(f"🟡 EPIC {eid}: YAML 有记录但未找到文档文件")
    for sid, s in state["entities"]["specs"].items():
        doc_s = doc_states["specs"].get(sid)
        if doc_s and doc_s != s["state"]:
            errors.append(f"🔴 SPEC {sid}: YAML={s['state']}, DOC={doc_s}")
        elif not doc_s:
            warnings.append(f"🟡 SPEC {sid}: YAML 有记录但未找到文档文件")
    for stid, st in state["entities"]["stories"].items():
        doc_s = doc_states["stories"].get(stid)
        if doc_s and doc_s != st["state"]:
            errors.append(f"🔴 STORY {stid}: YAML={st['state']}, DOC={doc_s}")
        elif not doc_s:
            warnings.append(f"🟡 STORY {stid}: YAML 有记录但未找到文档文件")
    for eid in doc_states["epics"]:
        if eid not in state["entities"]["epics"]:
            errors.append(f"🔴 EPIC {eid}: 文档存在但 YAML 中未注册")
    for sid in doc_states["specs"]:
        if sid not in state["entities"]["specs"]:
            errors.append(f"🔴 SPEC {sid}: 文档存在但 YAML 中未注册")
    for stid in doc_states["stories"]:
        if stid not in state["entities"]["stories"]:
            errors.append(f"🔴 STORY {stid}: 文档存在但 YAML 中未注册")
    if warnings:
        print(f"🟡 警告 ({len(warnings)}):\n")
        for w in warnings:
            print(f"  {w}")
    if errors:
        print(f"\n❌ 状态不一致 ({len(errors)}):\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    if not errors and not warnings:
        print(f"✅ 一致性验证通过 — {len(state['entities']['epics'])} Epics, {len(state['entities']['specs'])} Specs, {len(state['entities']['stories'])} Stories 全一致")
    else:
        print(f"\n✅ 关键状态一致性通过，{len(warnings)} 个警告 (非 blocking)")
    return True


def cmd_scan():
    state = load_state()
    doc_states = get_doc_states()
    print(f"\n{'='*60}")
    print("  扫描结果: 文档实际状态 vs YAML 记录状态")
    print(f"{'='*60}")
    total = drift = 0
    for eid, e in sorted(state["entities"]["epics"].items()):
        total += 1
        doc_s = doc_states["epics"].get(eid, "—")
        mark = "⚠️" if doc_s != "—" and doc_s != e["state"] else " ✅"
        if doc_s != "—" and doc_s != e["state"]:
            drift += 1
        print(f"  {mark} EPIC {eid:12s} YAML={e['state']:10s} DOC={doc_s}")
    for sid, s in sorted(state["entities"]["specs"].items()):
        total += 1
        doc_s = doc_states["specs"].get(sid, "—")
        mark = "⚠️" if doc_s != "—" and doc_s != s["state"] else " ✅"
        if doc_s != "—" and doc_s != s["state"]:
            drift += 1
        print(f"  {mark} SPEC {sid:12s} YAML={s['state']:10s} DOC={doc_s}")
    for stid, st in sorted(state["entities"]["stories"].items()):
        total += 1
        doc_s = doc_states["stories"].get(stid, "—")
        mark = "⚠️" if doc_s != "—" and doc_s != st["state"] else " ✅"
        if doc_s != "—" and doc_s != st["state"]:
            drift += 1
        print(f"  {mark} STORY {stid:12s} YAML={st['state']:10s} DOC={doc_s}")
    print(f"\n总计: {total} 个实体, 漂移: {drift} 个")
    return drift


def cmd_gate(entity, target_state):
    state = load_state()
    current = None
    for etype in ["epics", "specs", "stories"]:
        if entity in state["entities"].get(etype, {}):
            current = state["entities"][etype][entity]["state"]
            break
    if not current:
        if entity in state.get("sprints", {}):
            current = state["sprints"][entity]["state"]
    if not current:
        print(f"❌ 未找到实体: {entity}")
        sys.exit(1)
    all_valid = SDD_STATES + EPIC_STATES + SPRINT_STATES
    if target_state not in all_valid:
        print(f"❌ 无效目标状态: {target_state}")
        print(f"   有效状态: {', '.join(all_valid)}")
        sys.exit(1)
    print(f"🔍 门禁检查: {entity}: {current} → {target_state}")
    print(f"  ✅ 当前状态有效: {current}")
    print(f"  ✅ 目标状态有效: {target_state}")
    if target_state == "qa_gate" and current in ("draft", "create"):
        print(f"  ⚠️  需要先经过 REVIEW 才能进入 QA_GATE")
    if target_state == "completed":
        print(f"  ⚠️  需要检查: pytest 通过 + AC 验证 + doc-alignment")
    print(f"\n✅ 门禁预检通过 (软检查)")
    return True


def cmd_transition(entity, target_state, reason=""):
    try:
        cmd_gate(entity, target_state)
    except SystemExit as e:
        if e.code != 0:
            print(f"🛑 门禁拦截: 转换被拒绝")
            sys.exit(1)
    state = load_state()
    found = False
    old_state = None
    for etype in ["epics", "specs", "stories"]:
        if entity in state["entities"].get(etype, {}):
            old_state = state["entities"][etype][entity]["state"]
            state["entities"][etype][entity]["state"] = target_state
            found = True
            break
    if not found:
        if entity in state.get("sprints", {}):
            old_state = state["sprints"][entity]["state"]
            state["sprints"][entity]["state"] = target_state
            found = True
    if not found:
        print(f"❌ 未找到实体: {entity}")
        sys.exit(1)
    log_entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entity": entity, "from": old_state, "to": target_state,
        "action": "transition", "reason": reason or f"{entity}: {old_state} → {target_state}", "gate": "pre_flight"
    }
    if "history" not in state:
        state["history"] = []
    state["history"].append(log_entry)
    state["project"]["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    save_state(state)
    print(f"✅ 状态转换完成: {entity}: {old_state} → {target_state}")
    return True


def cmd_sync():
    state = load_state()
    doc_states = get_doc_states()
    changes = []
    for eid, doc_s in doc_states["epics"].items():
        if eid in state["entities"]["epics"]:
            if state["entities"]["epics"][eid]["state"] != doc_s:
                changes.append(f"EPIC {eid}: {state['entities']['epics'][eid]['state']} → {doc_s}")
                state["entities"]["epics"][eid]["state"] = doc_s
        else:
            changes.append(f"EPIC {eid}: (新增) → {doc_s}")
            state["entities"]["epics"][eid] = {"state": doc_s, "title": "", "spec_count": 0, "story_count": 0, "completed_count": 0, "priority": "", "qa_gate_date": None, "review_date": None}
    for sid, doc_s in doc_states["specs"].items():
        if sid in state["entities"]["specs"]:
            if state["entities"]["specs"][sid]["state"] != doc_s:
                changes.append(f"SPEC {sid}: {state['entities']['specs'][sid]['state']} → {doc_s}")
                state["entities"]["specs"][sid]["state"] = doc_s
        else:
            changes.append(f"SPEC {sid}: (新增) → {doc_s}")
            state["entities"]["specs"][sid] = {"state": doc_s, "epic": "?", "stories": []}
    for stid, doc_s in doc_states["stories"].items():
        if stid in state["entities"]["stories"]:
            if state["entities"]["stories"][stid]["state"] != doc_s:
                changes.append(f"STORY {stid}: {state['entities']['stories'][stid]['state']} → {doc_s}")
                state["entities"]["stories"][stid]["state"] = doc_s
        else:
            changes.append(f"STORY {stid}: (新增) → {doc_s}")
            state["entities"]["stories"][stid] = {"state": doc_s, "epic": "?", "spec": "?"}
    if changes:
        print(f"📝 同步了 {len(changes)} 个变更:")
        for c in changes:
            print(f"  - {c}")
        save_state(state)
    else:
        print("✅ 已是最新，无需同步")
    return changes


def cmd_list(by_state=False, by_type=False):
    state = load_state()
    if by_state:
        groups = {}
        for etype in ["epics", "specs", "stories"]:
            for eid, e in state["entities"].get(etype, {}).items():
                s = e["state"]
                if s not in groups:
                    groups[s] = []
                groups[s].append(f"{etype[:-1].upper()} {eid}")
        for s in sorted(groups.keys()):
            print(f"\n[{s}]")
            for item in sorted(groups[s]):
                print(f"  {item}")
    elif by_type:
        for etype in ["epics", "specs", "stories"]:
            print(f"\n--- {etype.upper()} ---")
            for eid, e in sorted(state["entities"].get(etype, {}).items()):
                print(f"  {eid:14s} [{e['state']:10s}]")
    else:
        for etype in ["epics", "specs", "stories"]:
            for eid, e in sorted(state["entities"].get(etype, {}).items()):
                print(f"{etype[:-1].upper():5s} {eid:14s} [{e['state']:10s}]")


def cmd_history():
    state = load_state()
    hist = state.get("history", [])
    if not hist:
        print("暂无历史记录")
        return
    for h in hist:
        frm = h.get('from') or '—'
        print(f"  {h.get('date','')} | {h['entity']:14s} | {frm:10s} → {h['to']:10s} | {h.get('reason','')}")


def init_state():
    if STATE_FILE.exists():
        print(f"⚠️  文件已存在: {STATE_FILE}")
        yn = input("  覆盖? (y/N): ")
        if yn.lower() != "y":
            print("  取消")
            return
    doc_states = get_doc_states()
    print(f"  扫描到 {len(doc_states['epics'])} EPICs, {len(doc_states['specs'])} SPECs, {len(doc_states['stories'])} STORYS")
    print("  请使用 python3 scripts/project-state.py scan 同步状态")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    cmds = {
        "status": cmd_status, "verify": cmd_verify, "scan": lambda: sys.exit(1 if cmd_scan() > 0 else 0),
        "gate": lambda: (len(sys.argv) >= 4 and cmd_gate(sys.argv[2], sys.argv[3])) or sys.exit(1),
        "transition": cmd_transition if len(sys.argv) >= 4 else (print("用法: transition <entity> <to> [reason]") or sys.exit(1)),
        "sync": cmd_sync, "list": lambda: cmd_list(**{"--by-state": bool("--by-state" in sys.argv), "--by-type": bool("--by-type" in sys.argv)}),
        "history": cmd_history, "init": init_state,
    }
    if cmd in ["gate"]:
        (lambda: (len(sys.argv) >= 4 and cmd_gate(sys.argv[2], sys.argv[3]) or sys.exit(1)))()
    elif cmd in ["transition"]:
        if len(sys.argv) < 4:
            print("用法: transition <entity> <to> [reason]")
            sys.exit(1)
        reason = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        cmd_transition(sys.argv[2], sys.argv[3], reason)
    elif cmd in cmds:
        cmds[cmd]()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)
