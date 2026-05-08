#!/usr/bin/env python3
"""
reflection-gate.py v1.0 — 反射门禁检查系统
自动化执行 R1/R2/R3 中间反思 + Quality Gate 质量门禁

用法:
  python3 reflection-gate.py r1 <task_id>         # R1 搜索质量检查
  python3 reflection-gate.py r2 <task_id>         # R2 理解深度检查
  python3 reflection-gate.py r3 <task_id>         # R3 提炼完整性检查
  python3 reflection-gate.py quality <task_id>    # STEP 5.5 质量门禁

输出: JSON 到 stdout，exit code = 0 通过, 1 失败
"""

import json
import os
import re
import sys
from datetime import datetime

# ============================================================
# 路径常量
# ============================================================
STATE_FILE = os.path.expanduser("~/.hermes/learning_state.json")
ARTIFACT_DIR = os.path.expanduser("~/.hermes/learning")

QUALITY_WEIGHTS = {
    "信息覆盖度": 30,
    "交叉验证得分": 25,
    "可操作性": 25,
    "结构完整度": 20,
}
MAX_L2_LOOPS = 2   # R1/R2/R3 各最多 2 次
MAX_L3_LOOPS = 3   # QG 最多 3 次

# ============================================================
# 工具函数
# ============================================================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE) as f:
            raw = json.load(f)
        if isinstance(raw, dict) and all(isinstance(v, dict) and "steps" in v for v in raw.values()):
            return raw
        return {}
    except (json.JSONDecodeError, IOError):
        return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def resolve_task(task_id=None):
    """解析任务，返回 (task_id, task_state)"""
    state = load_state()
    if not state:
        print(json.dumps({"error": "无活跃学习任务"}, ensure_ascii=False))
        sys.exit(1)
    if task_id:
        if task_id not in state:
            print(json.dumps({"error": f"未找到任务：{task_id}"}, ensure_ascii=False))
            sys.exit(1)
        return task_id, state[task_id]
    # 使用最新任务
    sorted_tasks = sorted(state.items(), key=lambda x: x[1].get("created_at", ""), reverse=True)
    return sorted_tasks[0]

def read_artifact(relative_path):
    """读取产出物文件内容"""
    path = os.path.join(ARTIFACT_DIR, relative_path)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return f.read()

def increment_loop(task_state, gate_name):
    """增加循环计数，返回 (new_count, is_blocked)"""
    loop_count = task_state.setdefault("loop_count", {"r1": 0, "r2": 0, "r3": 0, "qg": 0})
    max_limit = MAX_L3_LOOPS if gate_name == "qg" else MAX_L2_LOOPS
    current = loop_count.get(gate_name, 0)
    current += 1
    loop_count[gate_name] = current
    is_blocked = current > max_limit
    return current, is_blocked

def output_result(gate, passed, score, failures, recommendation, loop_info=None):
    """标准JSON输出"""
    result = {
        "gate": gate,
        "passed": passed,
        "score": score,
        "failures": failures,
        "recommendation": recommendation,
        "timestamp": datetime.now().isoformat(),
    }
    if loop_info:
        result["loop"] = loop_info
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if passed else 1)


# ============================================================
# R1: 搜索质量检查 (RETRIEVE_CHECK)
# ============================================================

def check_r1(task_id=None):
    """检查搜索质量"""
    tid, task_state = resolve_task(task_id)
    
    # 递增循环计数
    loop_count, is_blocked = increment_loop(task_state, "r1")
    
    if is_blocked:
        save_state(load_state() | {tid: task_state})
        output_result(
            "r1", False, 0,
            [{"check": "循环上限", "detail": f"R1 已达上限 {MAX_L2_LOOPS} 次", "severity": "fatal"}],
            "请手动评估是否继续，或扩大搜索范围后重试",
            {"current": loop_count, "max": MAX_L2_LOOPS}
        )
    
    # 读取搜索结果
    content = read_artifact("raw_search_results.md")
    if not content:
        output_result(
            "r1", False, 0,
            [{"check": "文件缺失", "detail": "raw_search_results.md 不存在", "severity": "fatal"}],
            "请先完成 STEP 1 搜索"
        )
    
    # 读取知识图谱获取子主题数
    km_content = read_artifact("knowledge_map.md")
    
    # ---- 分析 ----
    sources = extract_sources(content)
    failures = []
    score = 0
    
    # 1. 数量检查 (25分)
    if len(sources) >= 3:
        score += 25
    else:
        failures.append({
            "check": "数量",
            "detail": f"只有 {len(sources)} 个来源，需要 ≥3 个",
            "severity": "high"
        })
    
    # 2. 权威性检查 (25分)
    official_domains = [".gov", ".edu", "github.com", "revealjs.com", "sli.dev",
                        "marp.app", "weasyprint.org", "python.org", "npmjs.com",
                        "mozilla.org", "w3.org", "developer.mozilla.org",
                        "docs.", "official", "官网"]
    has_official = any(
        any(d in s["url"].lower() for d in official_domains) 
        for s in sources
    )
    if has_official:
        score += 25
    else:
        failures.append({
            "check": "权威性",
            "detail": "缺少官方文档或权威来源",
            "severity": "high"
        })
    
    # 3. 覆盖度检查 (25分)
    # 从 knowledge_map.md 提取子主题
    subtopics = extract_subtopics(km_content or "")
    covered = count_covered_subtopics(content, subtopics)
    if subtopics:
        coverage_ratio = covered / len(subtopics)
    else:
        coverage_ratio = 1.0  # 没有子主题时默认通过
    
    if coverage_ratio >= 0.7:
        score += 25
    elif coverage_ratio >= 0.4:
        score += 15
        failures.append({
            "check": "覆盖度",
            "detail": f"只覆盖了 {covered}/{len(subtopics)} 个子主题 ({coverage_ratio:.0%})",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "覆盖度",
            "detail": f"严重不足：仅覆盖 {covered}/{len(subtopics)} 个子主题 ({coverage_ratio:.0%})",
            "severity": "high"
        })
    
    # 4. 时效性检查 (25分)
    # 简单检查：内容是否包含2024/2025/2026等年份
    years_found = re.findall(r'20[0-9]{2}', content)
    recent_years = [y for y in years_found if int(y) >= 2024]
    if recent_years:
        score += 25
    else:
        # 放宽：检查是否有版本号或发布日期
        has_version = bool(re.search(r'v\d+\.\d+|版本[\s\d.]+|[\d]{4}-[\d]{2}', content))
        if has_version:
            score += 15
        failures.append({
            "check": "时效性",
            "detail": "未检测到 2024-2026 年的内容，信息可能过时",
            "severity": "medium"
        })
    
    passed = score >= 60
    
    # 保存状态
    state = load_state()
    state[tid] = task_state
    save_state(state)
    
    # 生成建议
    main_failure = ""
    if failures:
        main_failure = failures[0]["detail"][:60]
    
    if score < 40:
        recommendation = f"回到 STEP 0 细化拆分主题（{main_failure}）"
    elif score < 60:
        recommendation = f"回到 STEP 1 补充搜索（{main_failure}）"
    else:
        recommendation = "通过，进入 STEP 2 深度阅读"
    
    output_result(
        "r1", passed, score, failures, recommendation,
        {"current": loop_count, "max": MAX_L2_LOOPS}
    )


# ============================================================
# R2: 理解深度检查 (COMPREHEND_CHECK)
# ============================================================

def check_r2(task_id=None):
    """检查深度阅读质量"""
    tid, task_state = resolve_task(task_id)
    
    # 递增循环计数
    loop_count, is_blocked = increment_loop(task_state, "r2")
    
    if is_blocked:
        save_state(load_state() | {tid: task_state})
        output_result(
            "r2", False, 0,
            [{"check": "循环上限", "detail": f"R2 已达上限 {MAX_L2_LOOPS} 次", "severity": "fatal"}],
            "请手动评估是否继续",
            {"current": loop_count, "max": MAX_L2_LOOPS}
        )
    
    # 读取阅读笔记
    content = read_artifact("reading_notes.md")
    if not content:
        output_result(
            "r2", False, 0,
            [{"check": "文件缺失", "detail": "reading_notes.md 不存在", "severity": "fatal"}],
            "请先完成 STEP 2 深度阅读"
        )
    
    failures = []
    score = 0
    lines = content.split('\n')
    
    # 1. 核心概念检查 — 是否有"用自己的话"的证据 (25分)
    # 关键词：发现、总结、核心是、本质、关键在于、理解为
    paraphrase_keywords = ['核心', '本质', '关键在于', '理解为', '总结', '发现',
                           '核心概念', '原理', '架构', '核心理念', '关键是']
    has_paraphrase = any(kw in content for kw in paraphrase_keywords)
    # 另外检查：是否有足够多的分析性内容（非引用行占比）
    quote_lines = sum(1 for l in lines if l.startswith('> ') or 'https://' in l)
    total_content = max(len(lines), 1)
    paraphrase_ratio = 1 - (quote_lines / total_content)
    
    if has_paraphrase and paraphrase_ratio > 0.5:
        score += 25
    elif has_paraphrase or paraphrase_ratio > 0.5:
        score += 15
        failures.append({
            "check": "核心概念",
            "detail": "有自己的理解但不够充分（引用占比过高）",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "核心概念",
            "detail": "缺乏自己的理解，看起来像直接复制粘贴",
            "severity": "high"
        })
    
    # 2. 可操作性检查 — 是否有代码/命令/操作步骤 (25分)
    has_code = bool(re.search(r'```|`[^`]+`|用法|步骤\d|命令|如何|方法', content))
    has_examples = bool(re.search(r'示例|举例|比如|例如|template|模板', content))
    
    if has_code and has_examples:
        score += 25
    elif has_code or has_examples:
        score += 15
        failures.append({
            "check": "可操作性",
            "detail": "有代码或示例但不够完整",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "可操作性",
            "detail": "缺少代码示例和操作说明",
            "severity": "high"
        })
    
    # 3. 完整性检查 — 是否覆盖了搜索结果的要点 (25分)
    total_para = sum(1 for l in lines if l.strip() and not l.startswith('#') and not l.startswith('>'))
    min_acceptable = 5  # 至少 5 个有效段落
    if total_para >= 15:
        score += 25
    elif total_para >= 10:
        score += 20
    elif total_para >= min_acceptable:
        score += 15
        failures.append({
            "check": "完整性",
            "detail": f"只有 {total_para} 个有效段落，可能遗漏了部分内容",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "完整性",
            "detail": f"严重不足：仅 {total_para} 个有效段落 (最低 {min_acceptable})",
            "severity": "high"
        })
    
    # 4. 交叉验证检查 — 是否有多个来源的对比 (25分)
    urls_count = len(re.findall(r'https?://[^\s\)\]>"]+', content))
    if urls_count >= 3:
        score += 25
    elif urls_count >= 1:
        score += 15
        failures.append({
            "check": "交叉验证",
            "detail": f"仅引用 {urls_count} 个来源，建议 ≥3 个独立来源交叉验证",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "交叉验证",
            "detail": "没有引用任何来源，无法确认信息可信度",
            "severity": "high"
        })
    
    passed = score >= 60
    
    # 保存状态
    state = load_state()
    state[tid] = task_state
    save_state(state)
    
    if score < 40:
        recommendation = "回到 STEP 1 重新搜索更易懂的资料"
    elif score < 60:
        recommendation = "回到 STEP 2 重新阅读，重点关注实践部分"
    else:
        recommendation = "通过，进入 STEP 3 知识提炼"
    
    output_result(
        "r2", passed, score, failures, recommendation,
        {"current": loop_count, "max": MAX_L2_LOOPS}
    )


# ============================================================
# R3: 提炼完整性检查 (EXTRACT_CHECK)
# ============================================================

def check_r3(task_id=None):
    """检查知识提炼质量"""
    tid, task_state = resolve_task(task_id)
    
    loop_count, is_blocked = increment_loop(task_state, "r3")
    
    if is_blocked:
        save_state(load_state() | {tid: task_state})
        output_result(
            "r3", False, 0,
            [{"check": "循环上限", "detail": f"R3 已达上限 {MAX_L2_LOOPS} 次", "severity": "fatal"}],
            "请手动评估是否继续",
            {"current": loop_count, "max": MAX_L2_LOOPS}
        )
    
    content = read_artifact("extracted_knowledge.md")
    if not content:
        output_result(
            "r3", False, 0,
            [{"check": "文件缺失", "detail": "extracted_knowledge.md 不存在", "severity": "fatal"}],
            "请先完成 STEP 3 知识提炼"
        )
    
    failures = []
    score = 0
    
    # 所需的结构要素
    required_sections = {
        "核心概念": ["核心理念", "核心概念", "本质", "原理", "概述"],
        "操作步骤": ["步骤", "操作", "用法", "方法", "流程", "安装", "启动", "命令"],
        "方案对比": ["对比", "比较", "vs", "VS", "区别", "选择"],
        "避坑指南": ["避坑", "注意", "陷阱", "常见错误", "⚠️", "❌", "Red Flag"],
        "代码示例": ["```", "示例", "模板", "例子"],
    }
    
    section_score = 0
    for section, keywords in required_sections.items():
        if any(kw in content for kw in keywords):
            section_score += 1
    
    # 1. 结构完整性 (25分)
    if section_score >= 5:
        score += 25
    elif section_score >= 4:
        score += 20
        failures.append({
            "check": "结构完整性",
            "detail": f"缺少部分核心章节（覆盖 {section_score}/5）",
            "severity": "medium"
        })
    elif section_score >= 3:
        score += 15
        failures.append({
            "check": "结构完整性",
            "detail": f"核心章节不完整（仅 {section_score}/5）",
            "severity": "high"
        })
    else:
        failures.append({
            "check": "结构完整性",
            "detail": f"严重缺失：仅 {section_score}/5 个核心章节",
            "severity": "high"
        })
    
    # 2. 可操作性 — 有可直接执行的代码/命令 (25分)
    code_blocks = len(re.findall(r'```', content)) // 2
    has_command = bool(re.search(r'(?:```|`[^`]{3,}`)[^`]*?(?:bash|sh|python|html|js|css|cmd)', content, re.IGNORECASE))
    
    if code_blocks >= 3 and has_command:
        score += 25
    elif code_blocks >= 1:
        score += 15
        failures.append({
            "check": "可操作性",
            "detail": f"有代码块 ({code_blocks} 个) 但缺少语言标注或命令示例",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "可操作性",
            "detail": "无可执行的代码或命令，无法指导实践",
            "severity": "high"
        })
    
    # 3. 结构格式 — 有标题层级 (25分)
    h2_count = len(re.findall(r'^##\s', content, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s', content, re.MULTILINE))
    
    if h2_count >= 4:
        score += 25
    elif h2_count >= 2:
        score += 15
        failures.append({
            "check": "格式结构",
            "detail": f"只有 {h2_count} 个二级标题，建议 ≥4 个",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "格式结构",
            "detail": f"标题层级严重不足 ({h2_count} 个 h2)",
            "severity": "high"
        })
    
    # 4. 应用场景 — 有使用场景说明 (25分)
    scene_keywords = ["适用", "场景", "推荐", "适合", "使用情况", "选型", "选择"]
    has_scene = any(kw in content for kw in scene_keywords)
    
    if has_scene:
        score += 25
    else:
        failures.append({
            "check": "应用场景",
            "detail": "缺少使用场景或选型建议",
            "severity": "medium"
        })
    
    passed = score >= 60
    
    state = load_state()
    state[tid] = task_state
    save_state(state)
    
    if score < 40:
        recommendation = "回到 STEP 2 重新阅读，补充缺失的结构要素"
    elif score < 60:
        recommendation = "回到 STEP 3 重新提炼，完善结构和代码示例"
    else:
        recommendation = "通过，进入 STEP 4 Skill 脚手架"
    
    output_result(
        "r3", passed, score, failures, recommendation,
        {"current": loop_count, "max": MAX_L2_LOOPS}
    )


# ============================================================
# STEP 5.5: 质量门禁评分 (Quality Gate)
# ============================================================

def check_quality(task_id=None):
    """STEP 5.5 质量门禁 — 综合评分"""
    tid, task_state = resolve_task(task_id)
    
    loop_count, is_blocked = increment_loop(task_state, "qg")
    
    if is_blocked:
        save_state(load_state() | {tid: task_state})
        output_result(
            "quality", False, 0,
            [{"check": "循环上限", "detail": f"QG 已达上限 {MAX_L3_LOOPS} 次", "severity": "fatal"}],
            "请手动评估，或考虑缩小学习范围",
            {"current": loop_count, "max": MAX_L3_LOOPS}
        )
    
    # 读取所有产出物
    km = read_artifact("knowledge_map.md") or ""
    search = read_artifact("raw_search_results.md") or ""
    reading = read_artifact("reading_notes.md") or ""
    extracted = read_artifact("extracted_knowledge.md") or ""
    
    failures = []
    score = 0
    
    # 1. 信息覆盖度 (30分)
    subtopics = extract_subtopics(km)
    if subtopics:
        covered = count_covered_subtopics(search + reading + extracted, subtopics)
        coverage = covered / len(subtopics)
    else:
        coverage = 1.0
    
    if coverage >= 0.8:
        score += 30
    elif coverage >= 0.6:
        score += 20
        failures.append({
            "check": "信息覆盖度",
            "detail": f"覆盖 {covered}/{len(subtopics)} 子主题 ({coverage:.0%})",
            "severity": "medium"
        })
    elif coverage >= 0.4:
        score += 10
        failures.append({
            "check": "信息覆盖度",
            "detail": f"覆盖不足 {covered}/{len(subtopics)} ({coverage:.0%})",
            "severity": "high"
        })
    else:
        failures.append({
            "check": "信息覆盖度",
            "detail": f"严重不足 {covered}/{len(subtopics)} ({coverage:.0%})",
            "severity": "high"
        })
    
    # 2. 交叉验证得分 (25分)
    total_urls = len(re.findall(r'https?://[^\s\)\]>"]+', reading + extracted))
    if total_urls >= 5:
        score += 25
    elif total_urls >= 3:
        score += 18
    elif total_urls >= 1:
        score += 10
        failures.append({
            "check": "交叉验证得分",
            "detail": f"仅 {total_urls} 个来源引用",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "交叉验证得分",
            "detail": "无来源引用，无法交叉验证",
            "severity": "high"
        })
    
    # 3. 可操作性 (25分)
    code_blocks = len(re.findall(r'```', reading + extracted)) // 2
    has_steps = bool(re.search(r'步骤|STEP|Step|用法|如何|安装|配置|命令', reading + extracted))
    
    if code_blocks >= 3 and has_steps:
        score += 25
    elif code_blocks >= 1 or has_steps:
        score += 15
        failures.append({
            "check": "可操作性",
            "detail": "有操作指引但缺少代码示例",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "可操作性",
            "detail": "缺少操作步骤和代码示例",
            "severity": "high"
        })
    
    # 4. 结构完整度 (20分)
    h2_total = len(re.findall(r'^##\s', reading + extracted, re.MULTILINE))
    h3_total = len(re.findall(r'^###\s', reading + extracted, re.MULTILINE))
    has_table = bool(re.search(r'\|[^|]+\|[^|]+\|', reading + extracted))
    
    structure_factors = (h2_total >= 3) + (h3_total >= 2) + has_table
    if structure_factors >= 3:
        score += 20
    elif structure_factors >= 2:
        score += 15
    elif structure_factors >= 1:
        score += 10
        failures.append({
            "check": "结构完整度",
            "detail": f"结构要素不足（h2={h2_total}, h3={h3_total}, table={has_table}）",
            "severity": "medium"
        })
    else:
        failures.append({
            "check": "结构完整度",
            "detail": "完全没有结构（无标题层级、无表格）",
            "severity": "high"
        })
    
    passed = score >= 60
    passed_with_warning = score >= 40 and score < 60
    
    state = load_state()
    state[tid] = task_state
    save_state(state)
    
    if passed:
        if score >= 80:
            recommendation = "✅ 通过，进入 STEP 6 反思"
        else:
            recommendation = "⚠️ 通过但需标记'待改进'，进入 STEP 6 反思"
    elif passed_with_warning:
        recommendation = f"回到 STEP 1-4 补充（得分 {score}，低于 60）"
    else:
        recommendation = f"回到 STEP 0 重新规划（得分 {score}，严重不足）"
    
    output_result(
        "quality", passed, score, failures, recommendation,
        {"current": loop_count, "max": MAX_L3_LOOPS}
    )


# ============================================================
# 解析辅助函数
# ============================================================

def extract_sources(content):
    """从 raw_search_results.md 提取来源列表"""
    sources = []
    lines = content.split('\n')
    current_title = ""
    current_url = ""
    
    for i, line in enumerate(lines):
        url_match = re.search(r'https?://[^\s\)\]>"]+', line)
        if url_match:
            current_url = url_match.group(0).rstrip('.)')
            # 向上找标题
            for j in range(i-1, max(i-5, -1), -1):
                if lines[j].startswith('## ') or lines[j].startswith('# '):
                    current_title = lines[j].lstrip('#').strip()
                    break
            sources.append({
                "title": current_title,
                "url": current_url,
                "line": i + 1
            })
    
    return sources


def extract_subtopics(content):
    """从 knowledge_map.md 提取子主题列表"""
    subtopics = []
    in_subtopic_section = False
    for line in content.split('\n'):
        if re.match(r'^##?\s+子主题', line):
            in_subtopic_section = True
            continue
        if in_subtopic_section:
            # 匹配数字列表：1. **xxx** 或 - xxx
            m = re.match(r'^\s*(?:\d+[\.\)]|[-*])\s+\*{0,2}([^*\n]+?)\*{0,2}', line)
            if m:
                subtopics.append(m.group(1).strip().rstrip('—').strip())
            elif line.startswith('## ') and '子主题' not in line:
                break
    return subtopics


def count_covered_subtopics(content, subtopics):
    """计算子主题在搜索结果中被覆盖的数量"""
    if not subtopics:
        return 0
    covered = 0
    for subtopic in subtopics:
        # 提取关键词（取前 15 个字符）
        keyword = subtopic.split('—')[0].split('：')[0].strip()[:20]
        if keyword and keyword.lower() in content.lower():
            covered += 1
    return covered


# ============================================================
# CLI 分发
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 reflection-gate.py {r1|r2|r3|quality} [task_id]")
        print()
        print("  检查点门禁:")
        print("    r1 <task_id>   — R1 搜索质量检查 (RETRIEVE_CHECK)")
        print("    r2 <task_id>   — R2 理解深度检查 (COMPREHEND_CHECK)")
        print("    r3 <task_id>   — R3 提炼完整性检查 (EXTRACT_CHECK)")
        print("    quality <task_id> — STEP 5.5 质量门禁评分")
        sys.exit(1)
    
    gate = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if gate == "r1":
        check_r1(task_id)
    elif gate == "r2":
        check_r2(task_id)
    elif gate == "r3":
        check_r3(task_id)
    elif gate == "quality":
        check_quality(task_id)
    else:
        print(json.dumps({"error": f"未知门禁: {gate}"}, ensure_ascii=False))
        sys.exit(1)
