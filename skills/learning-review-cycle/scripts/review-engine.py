#!/usr/bin/env python3
"""
learning-review-engine.py - 学习 Review 引擎 v1.0
自驱动循环的核心执行器：
1. 扫描所有 skill 的新鲜度
2. 检查学习历史
3. 管理缺口队列
4. 生成周报/月报/总结报告
5. 自动触发学习任务

用法:
  python3 review-engine.py scan           # 扫描所有 skill 新鲜度
  python3 review-engine.py weekly         # 生成学习周报
  python3 review-engine.py monthly        # 生成学习月报
  python3 review-engine.py gap-add <type> <desc>  # 添加知识缺口
  python3 review-engine.py gap-list       # 列出所有缺口
  python3 review-engine.py summary        # 生成单次学习总结
"""

import os
import sys
import json
import glob
import re
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# ======== 路径常量 ========
HOME = os.path.expanduser("~")
SKILLS_DIR = os.path.join(HOME, ".hermes", "skills")
LEARNING_DIR = os.path.join(HOME, ".hermes", "learning")
REPORTS_DIR = os.path.join(LEARNING_DIR, "reports")
REVIEWS_DIR = os.path.join(LEARNING_DIR, "reviews")
GAP_QUEUE_FILE = os.path.join(LEARNING_DIR, "gap_queue.json")
HISTORY_FILE = os.path.join(HOME, ".hermes", "learning_history.json")
STATE_FILE = os.path.join(HOME, ".hermes", "learning_state.json")

# 新鲜度评分参数
FRESHNESS_BASE = 50
FRESHNESS_RECENT_30 = 10
FRESHNESS_RECENT_7 = 20
FRESHNESS_DECAY_30 = -5
FRESHNESS_DECAY_90 = -15
FRESHNESS_FREQ_HIGH = 5
FRESHNESS_FREQ_LOW = 2

# 阈值
FRESHNESS_CHECK = 60
FRESHNESS_UPDATE = 40
FRESHNESS_URGENT = 20


def ensure_dirs():
    """确保输出目录存在"""
    for d in [REPORTS_DIR, REVIEWS_DIR, LEARNING_DIR]:
        os.makedirs(d, exist_ok=True)


def load_json(path, default=None):
    """安全加载 JSON"""
    if default is None:
        default = {} if path.endswith("gap_queue.json") else []
    if not os.path.exists(path):
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def save_json(path, data):
    """安全保存 JSON"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 2:
            try:
                meta = yaml.safe_load(parts[1])
                return meta or {}
            except:
                pass
    return {}


def get_file_mtime(path):
    """获取文件修改时间"""
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts)
    except:
        return None


def compute_freshness(name, version, mtime, recent_modifications):
    """
    计算 skill 的新鲜度评分
    公式：基础分(50) + 版本活跃度(30) - 时间衰减(20) + 使用加分(20)
    """
    score = FRESHNESS_BASE
    
    # 版本活跃度：检查最近修改时间
    if mtime:
        days_ago = (datetime.now() - mtime).days
        if days_ago <= 7:
            score += FRESHNESS_RECENT_7
        elif days_ago <= 30:
            score += FRESHNESS_RECENT_30
        
        # 时间衰减
        if days_ago > 90:
            score += FRESHNESS_DECAY_90
        elif days_ago > 30:
            score += FRESHNESS_DECAY_30
    
    # 使用加分：检查是否在最近修改列表中
    if name in recent_modifications:
        score += FRESHNESS_FREQ_HIGH
    
    return max(0, min(100, score))


def get_freshness_status(score):
    """获取新鲜度状态"""
    if score >= FRESHNESS_CHECK:
        return "✅ 健康", "无需处理"
    elif score >= FRESHNESS_UPDATE:
        return "⚠️ 待检查", "建议查看是否需要更新"
    elif score >= FRESHNESS_URGENT:
        return "🔴 建议更新", "内容可能过时，建议刷新"
    else:
        return "🚨 紧急更新", "内容严重过时，必须更新"


def scan_skills():
    """扫描所有 skill 的新鲜度"""
    ensure_dirs()
    
    # 获取所有 SKILL.md
    sk_files = glob.glob(os.path.join(SKILLS_DIR, '**/SKILL.md'), recursive=True)
    
    # 获取最近修改的 skill 列表（近 30 天）
    recent_modifications = set()
    cutoff = datetime.now() - timedelta(days=30)
    
    results = []
    for f in sk_files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                content = fh.read()
            
            meta = parse_frontmatter(content)
            name = meta.get('name', os.path.basename(os.path.dirname(f)))
            version = meta.get('version', '0.0.0')
            
            mtime = get_file_mtime(f)
            if mtime and mtime > cutoff:
                recent_modifications.add(name)
            
            freshness = compute_freshness(name, version, mtime, recent_modifications)
            status, suggestion = get_freshness_status(freshness)
            
            results.append({
                'name': name,
                'version': version,
                'path': f,
                'mtime': mtime.isoformat() if mtime else 'unknown',
                'freshness': freshness,
                'status': status,
                'suggestion': suggestion,
            })
        except Exception as e:
            results.append({
                'name': os.path.basename(os.path.dirname(f)),
                'version': '?',
                'path': f,
                'mtime': 'unknown',
                'freshness': 0,
                'status': '❌ 读取失败',
                'suggestion': str(e),
            })
    
    # 按新鲜度排序
    results.sort(key=lambda x: x['freshness'])
    
    return results


def load_gap_queue():
    """加载缺口队列"""
    return load_json(GAP_QUEUE_FILE, {"gaps": [], "last_review": "", "auto_learn_enabled": True})


def save_gap_queue(queue):
    """保存缺口队列"""
    save_json(GAP_QUEUE_FILE, queue)


def add_gap(gap_type, description, priority="medium", source="manual", skill=None):
    """添加知识缺口"""
    queue = load_gap_queue()
    
    # 检查是否已有类似缺口（7 天内不重复）
    now = datetime.now()
    for existing in queue["gaps"]:
        if existing["status"] == "pending":
            created = datetime.fromisoformat(existing["created_at"])
            if (now - created).days < 7:
                if existing["description"] == description:
                    print(f"⏭️  跳过重复缺口（7天内已有）: {description}")
                    return
    
    gap = {
        "id": f"gap_{len(queue['gaps']) + 1:03d}",
        "created_at": now.isoformat(),
        "type": gap_type,
        "source": source,
        "skill": skill,
        "description": description,
        "priority": priority,
        "status": "pending",
        "suggested_action": {
            "knowledge_outdated": "创建刷新学习任务",
            "knowledge_missing": "创建新学习任务",
            "knowledge_conflict": "创建对比验证任务",
            "tool_broken": "创建替代方案研究"
        }.get(gap_type, "待定")
    }
    
    queue["gaps"].append(gap)
    save_gap_queue(queue)
    print(f"✅ 缺口已添加: [{gap_type}] {description}")


def list_gaps():
    """列出所有缺口"""
    queue = load_gap_queue()
    gaps = queue.get("gaps", [])
    
    if not gaps:
        print("📭 无知识缺口")
        return
    
    pending = [g for g in gaps if g["status"] == "pending"]
    completed = [g for g in gaps if g["status"] == "completed"]
    
    print(f"📋 知识缺口队列（共 {len(gaps)}，待处理 {len(pending)}，已完成 {len(completed)}）")
    print()
    
    if pending:
        print("⏳ 待处理：")
        for g in sorted(pending, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3)):
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(g["priority"], "⚪")
            created = g.get("created_at", "")[:16]
            print(f"  {icon} [{g['priority']}] {g['description']}")
            print(f"     类型: {g['type']} | 创建: {created} | 建议: {g['suggested_action']}")
    
    if completed:
        print()
        print("✅ 已处理：")
        for g in completed[-5:]:
            print(f"  ✅ {g['description']}")


def load_learning_history():
    """加载学习历史"""
    return load_json(HISTORY_FILE, [])


def generate_weekly_report():
    """生成学习周报"""
    ensure_dirs()
    history = load_learning_history()
    
    # 计算本周范围
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    # 筛选本周的学习记录
    weekly = []
    for h in history:
        created = h.get("completed_at", h.get("created_at", ""))
        if created:
            try:
                dt = datetime.fromisoformat(created)
                if monday <= dt <= sunday:
                    weekly.append(h)
            except:
                pass
    
    # 扫描 skill 新鲜度
    skills = scan_skills()
    
    # 生成报告
    week_num = today.isocalendar()[1]
    report = f"""# 📚 学习周报 W{week_num}
**生成时间**：{today.strftime('%Y-%m-%d %H:%M')}
**周期**：{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')}

## 📊 本周学习统计
- 完成了 **{len(weekly)}** 个学习任务
- Skill 总数：**{len(skills)}** 个

## ✅ 本周完成
"""
    
    if weekly:
        for h in weekly:
            topic = h.get("topic", "未知")
            progress = h.get("final_progress", 100)
            report += f"- ✅ **{topic}** — {progress}%\n"
    else:
        report += "- （本周无学习活动）\n"
    
    # 检查需要更新的 skill
    needs_update = [s for s in skills if s['freshness'] < FRESHNESS_UPDATE]
    if needs_update:
        report += f"""
## ⚠️ 建议更新的 Skill（{len(needs_update)} 个）
| Skill | 版本 | 新鲜度 | 建议 |
|-------|------|--------|------|
"""
        for s in needs_update[:10]:
            report += f"| {s['name']} | {s['version']} | {s['freshness']} | {s['suggestion']} |\n"
    
    # 检查缺口
    queue = load_gap_queue()
    pending_gaps = [g for g in queue.get("gaps", []) if g["status"] == "pending"]
    if pending_gaps:
        report += f"""
## 📌 待处理知识缺口（{len(pending_gaps)} 个）
"""
        for g in pending_gaps[:5]:
            report += f"- [{g['priority']}] {g['description']}\n"
    
    # 保存报告
    filename = f"weekly_{today.strftime('%Y%m%d')}.md"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(report)
    
    print(f"✅ 学习周报已生成：{filepath}")
    print()
    print(report[:500] + "...\n" if len(report) > 500 else report)
    
    return report


def generate_monthly_report():
    """生成学习月报"""
    ensure_dirs()
    history = load_learning_history()
    today = datetime.now()
    
    # 本月范围
    month_start = today.replace(day=1)
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
    
    # 筛选本月记录
    monthly = []
    for h in history:
        created = h.get("completed_at", h.get("created_at", ""))
        if created:
            try:
                dt = datetime.fromisoformat(created)
                if month_start <= dt <= month_end:
                    monthly.append(h)
            except:
                pass
    
    # 深度扫描
    skills = scan_skills()
    
    # 分析 skill 健康状况
    healthy = [s for s in skills if s['freshness'] >= FRESHNESS_CHECK]
    check = [s for s in skills if FRESHNESS_UPDATE <= s['freshness'] < FRESHNESS_CHECK]
    update = [s for s in skills if s['freshness'] < FRESHNESS_UPDATE]
    
    report = f"""# 📚 学习月报 {today.strftime('%Y年%m月')}
**生成时间**：{today.strftime('%Y-%m-%d %H:%M')}

## 📊 月度统计
- 任务总数：**{len(monthly)}**
- Skill 总数：**{len(skills)}**
- Skill 健康：✅ {len(healthy)} / ⚠️ {len(check)} / 🔴 {len(update)}

## 🏆 本月完成
"""
    if monthly:
        for h in monthly[-20:]:
            topic = h.get("topic", "未知")
            progress = h.get("final_progress", 100)
            report += f"- ✅ **{topic}** — {progress}%\n"
    else:
        report += "- （本月无学习活动）\n"
    
    if update:
        report += f"""
## 📈 Skill 健康报告（需要更新）
| Skill | 版本 | 新鲜度 | 建议 |
|-------|------|--------|------|
"""
        for s in update[:15]:
            report += f"| {s['name']} | {s['version']} | {s['freshness']} | {s['suggestion']} |\n"
    
    # 缺口分析
    queue = load_gap_queue()
    pending_gaps = [g for g in queue.get("gaps", []) if g["status"] == "pending"]
    high_priority = [g for g in pending_gaps if g["priority"] == "high"]
    
    if high_priority:
        report += f"""
## 🎯 下月学习计划
"""
        for i, g in enumerate(high_priority[:3], 1):
            report += f"{i}. **优先级 {i}**：{g['description']} — {g['suggested_action']}\n"
    
    # 保存
    filename = f"monthly_{today.strftime('%Y%m')}.md"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(report)
    
    print(f"✅ 学习月报已生成：{filepath}")
    print()
    print(report[:500] + "...\n" if len(report) > 500 else report)
    
    return report


def generate_learning_summary(topic, mode="快速", duration=10, output="笔记"):
    """生成单次学习总结"""
    ensure_dirs()
    today = datetime.now()
    
    summary = f"""# 📝 学习总结：{topic}

## 📋 基本信息
- **日期**：{today.strftime('%Y-%m-%d %H:%M')}
- **模式**：{mode}
- **耗时**：{duration} 分钟
- **产出**：{output}

## 🎯 学到了什么
<!-- 由调用者填写 -->

## 💡 方法论反思
<!-- 由调用者填写 -->

## 📌 下步建议
<!-- 由调用者填写 -->

---
*由 learning-review-cycle 自动生成*
"""
    
    # 保存
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', topic)[:50]
    filename = f"summary_{today.strftime('%Y%m%d_%H%M')}_{safe_name}.md"
    filepath = os.path.join(REVIEWS_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(summary)
    
    print(f"✅ 学习总结模板已生成：{filepath}")
    return summary


def auto_learn_check():
    """
    检查是否可以自动触发学习
    规则：高优先级缺口 ≥ 3 个 → 自动学习 top 3
    """
    queue = load_gap_queue()
    pending = [g for g in queue.get("gaps", []) if g["status"] == "pending"]
    high = [g for g in pending if g["priority"] == "high"]
    
    if not queue.get("auto_learn_enabled", True):
        print("⏸️  自动学习已暂停")
        return []
    
    if len(high) >= 3:
        print(f"🚀 检测到 {len(high)} 个高优先级缺口，建议自动学习 top 3")
        suggestions = []
        for g in high[:3]:
            suggestions.append(g["description"])
            g["status"] = "auto_learning"
        
        save_gap_queue(queue)
        return suggestions
    
    return []


def main():
    if len(sys.argv) < 2:
        print("用法: python3 review-engine.py {scan|weekly|monthly|gap-add|gap-list|summary|auto-check}")
        print()
        print("  scan        扫描所有 skill 的新鲜度")
        print("  weekly      生成学习周报")
        print("  monthly     生成学习月报")
        print("  gap-add <type> <desc>  添加知识缺口")
        print("  gap-list    列出所有缺口")
        print("  summary     生成学习总结模板")
        print("  auto-check  检查是否需要自动学习")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "scan":
        results = scan_skills()
        print(f"🔍 Skill 新鲜度扫描完成（共 {len(results)} 个）")
        print()
        
        needs_attention = [r for r in results if r['freshness'] < FRESHNESS_CHECK]
        for r in needs_attention[:20]:
            print(f"  {r['status']} {r['name']} v{r['version']} ({r['freshness']})")
        
        if not needs_attention:
            print("  ✅ 所有 skill 状态良好！")
        
        # 保存扫描结果
        scan_file = os.path.join(REVIEWS_DIR, f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        save_json(scan_file, results)
        print(f"\n📄 扫描结果已保存：{scan_file}")
        
    elif action == "weekly":
        generate_weekly_report()
        
    elif action == "monthly":
        generate_monthly_report()
        
    elif action == "gap-add":
        if len(sys.argv) < 4:
            print("用法: review-engine.py gap-add <type> <description>")
            print("  type: knowledge_outdated, knowledge_missing, knowledge_conflict, tool_broken")
            sys.exit(1)
        gap_type = sys.argv[2]
        # 支持多词描述（从第 3 个参数到最后一个参数前，如果priority存在的话）
        # priority 是可选的，在最后，用小写字母表示
        desc_parts = sys.argv[3:]
        # 检查最后一个参数是否是优先级关键词
        if len(desc_parts) > 1 and desc_parts[-1] in ("high", "medium", "low"):
            priority = desc_parts[-1]
            desc = " ".join(desc_parts[:-1])
        else:
            priority = "medium"
            desc = " ".join(desc_parts)
        add_gap(gap_type, desc, priority)
        
    elif action == "gap-list":
        list_gaps()
        
    elif action == "summary":
        topic = sys.argv[2] if len(sys.argv) > 2 else "未命名主题"
        mode = sys.argv[3] if len(sys.argv) > 3 else "快速"
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        output = sys.argv[5] if len(sys.argv) > 5 else "笔记"
        generate_learning_summary(topic, mode, duration, output)
        
    elif action == "auto-check":
        suggestions = auto_learn_check()
        if suggestions:
            print("💡 建议自动学习：")
            for s in suggestions:
                print(f"  - {s}")
        else:
            print("⏳ 未达到自动学习阈值（需要 ≥ 3 个高优先级缺口）")
        
    else:
        print(f"🚨 未知操作：{action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
