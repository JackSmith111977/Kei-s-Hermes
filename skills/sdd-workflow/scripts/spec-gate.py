#!/usr/bin/env python3
"""
spec-gate.py v1.0 — SDD 门禁检查器

检查当前任务是否满足 SDD 工作流要求。在开发前必须运行。

用法:
  python3 spec-gate.py check <task_description>   # 检查是否需要 SDD
  python3 spec-gate.py enforce <task_description> # 强制门禁（阻塞则 exit 1）
  python3 spec-gate.py verify <story_id>          # 验证 Spec 文档完整性

输出格式（JSON）:
  {
    "gate": "spec-approval",
    "passed": true/false,
    "story_id": "xxx" or null,
    "status": "approved" or null,
    "blockers": ["原因1", ...],
    "message": "人类可读消息"
  }
"""

import json, os, sys, re

STATE_FILE = os.path.expanduser("~/.hermes/sdd_state.json")
HERMES_HOME = os.path.expanduser("~/.hermes")


def load_sdd_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}


def find_matching_story(state, task_description):
    """
    在 state 中查找匹配 task_description 的 Story。
    匹配策略：title 或 story_id 包含 task 关键词
    """
    task_lower = task_description.lower()
    # 提取关键词（去掉常见停用词）
    keywords = set(re.findall(r'[a-zA-Z0-9\u4e00-\u9fff_\-]+', task_lower))
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'up', 'about', 'into', 'over', 'after', 'and', 'or', 'not',
                  'this', 'that', 'these', 'those', 'it', 'its', '的', '了',
                  '是', '在', '有', '和', '就', '不', '人', '都', '一',
                  '一个', '上', '也', '很', '到', '说', '要', '去', '你',
                  '会', '着', '没有', '看', '好', '自己', '之'}
    keywords = keywords - stop_words

    best_match = None
    best_score = 0

    for sid, spec in state.items():
        title_lower = spec.get('title', '').lower()
        title_words = set(re.findall(r'[a-zA-Z0-9\u4e00-\u9fff_\-]+', title_lower))

        # Jaccard 相似度
        if keywords and title_words:
            intersection = keywords & title_words
            union = keywords | title_words
            score = len(intersection) / len(union) if union else 0

            # bonus: story_id 或 title 直接包含 task 的关键短语
            for kw in keywords:
                if len(kw) >= 3 and kw in title_lower:
                    score += 0.3
                if len(kw) >= 3 and kw in sid.lower():
                    score += 0.2

            if score > best_score:
                best_score = score
                best_match = (sid, spec)

    # 阈值 0.15（宽松匹配，宁可误报也不要漏报）
    if best_match and best_score >= 0.15:
        return best_match[0], best_match[1], best_score
    return None, None, 0


def check_sdd_required(task_description):
    """
    判断任务是否需要 SDD。
    简单任务（修复错别字、改配置）不需要 SDD；
    复杂任务（新功能、架构变更、创建/编辑 Skill）需要 SDD。
    """
    simple_patterns = [
        r'fix|修复|typo|错字|拼写|format|格式',
        r'refactor|重构.*小|小.*重构',
        r'config|配置.*改|改.*配置',
        r'docs?更新|更新.*文档|update.*doc',
        r'rename|重命名|move|移动',
    ]
    task_lower = task_description.lower()
    for pattern in simple_patterns:
        if re.search(pattern, task_lower):
            return False

    # 显式需要 SDD 的场景
    sdd_triggers = [
        r'feature|功能|新.*能力',
        r'story|spec|sdd|epic',
        r'skill.*(create|edit|update|delete|patch)',
        r'创建.*skill|编辑.*skill|更新.*skill',
        r'architect|架构|设计.*方案',
        r'capability.*pack|能力包',
        r'模块化|模块.*拆分|模块.*设计',
    ]
    for pattern in sdd_triggers:
        if re.search(pattern, task_lower):
            return True

    # 默认：不确定时要求 SDD（安全策略）
    return True


def verify_spec_document(story_id, spec):
    """验证 Spec 文档是否存在并包含必需字段"""
    blockers = []

    # 检查 spec_path
    spec_path = spec.get('spec_path')
    if not spec_path or not os.path.exists(spec_path):
        blockers.append(f"Spec 文档不存在: {spec_path or '未设置路径'}")

    # 检查必需字段
    spec_obj = None
    if spec_path and os.path.exists(spec_path):
        try:
            with open(spec_path) as f:
                content = f.read()
            # 检查 YAML frontmatter 中的必需字段
            fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if fm_match:
                fm = fm_match.group(1)
                for field in ['story', 'title', 'status', 'acceptance_criteria']:
                    if f'{field}:' not in fm:
                        blockers.append(f"缺少必需字段: {field}")
            else:
                blockers.append("缺少 YAML frontmatter")
        except:
            blockers.append(f"无法读取 Spec 文档: {spec_path}")

    return blockers


def cmd_check(task_description):
    """检查任务是否需要 SDD，以及是否有对应的 Spec"""
    state = load_sdd_state()
    needs_sdd = check_sdd_required(task_description)

    result = {
        "gate": "sdd-check",
        "passed": True,
        "needs_sdd": needs_sdd,
        "story_id": None,
        "status": None,
        "blockers": [],
        "message": "",
    }

    if not needs_sdd:
        result["message"] = f"✅ 简单任务 '{task_description}'，不需要 SDD"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return True

    # 查找匹配的 Story
    story_id, spec, score = find_matching_story(state, task_description)

    if not story_id:
        result["passed"] = False
        result["blockers"].append(f"未找到匹配 '{task_description}' 的 Story")
        result["message"] = f"❌ 需要 SDD 但未找到匹配 Story。请先创建 Story。"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return False

    result["story_id"] = story_id
    result["status"] = spec["status"]
    result["match_score"] = round(score, 2)

    # 检查状态是否允许开发
    allowed_states = ["approved", "architect", "plan", "implement"]
    if spec["status"] not in allowed_states:
        result["passed"] = False
        result["blockers"].append(
            f"Story '{story_id}' 状态为 '{spec['status']}'，"
            f"需要进入 approved/architect/plan/implement 才能开发"
        )

    if result["passed"]:
        result["message"] = f"✅ Story '{story_id}' ({spec['status']}) 可以开发"
    else:
        result["message"] = f"❌ 门禁未通过"

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result["passed"]


def cmd_enforce(task_description):
    """强制门禁：未通过则 exit 1"""
    ok = cmd_check(task_description)
    if not ok:
        sys.exit(1)


def cmd_verify(story_id):
    """验证 Spec 文档完整性"""
    state = load_sdd_state()
    spec = state.get(story_id)

    result = {
        "gate": "sdd-verify",
        "passed": True,
        "story_id": story_id,
        "status": spec["status"] if spec else None,
        "blockers": [],
        "message": "",
    }

    if not spec:
        result["passed"] = False
        result["blockers"].append(f"Story '{story_id}' 不存在")
        result["message"] = f"❌ Story '{story_id}' 不存在"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return False

    # 验证状态
    result["status"] = spec["status"]

    # 验证文档
    doc_blockers = verify_spec_document(story_id, spec)
    result["blockers"].extend(doc_blockers)

    # 验证状态机合法性
    if spec["status"] not in ["draft", "review", "approved", "architect",
                              "plan", "implement", "completed", "archived"]:
        result["blockers"].append(f"非法状态: {spec['status']}")

    if result["blockers"]:
        result["passed"] = False
        result["message"] = f"❌ 发现 {len(result['blockers'])} 个问题"
    else:
        result["message"] = f"✅ Story '{story_id}' 验证通过"

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result["passed"]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    value = sys.argv[2]

    if action == "check":
        cmd_check(value)
    elif action == "enforce":
        cmd_enforce(value)
    elif action == "verify":
        cmd_verify(value)
    else:
        print(f"❌ 未知操作: {action} (可用: check, enforce, verify)")
        sys.exit(1)


if __name__ == "__main__":
    main()
