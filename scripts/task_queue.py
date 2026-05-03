#!/usr/bin/env python3
"""小喵任务队列管理器"""

import os, sys, datetime

QUEUE_FILE = os.path.expanduser("~/.hermes/TASK_QUEUE.md")

def read_queue():
    if not os.path.exists(QUEUE_FILE):
        return [], []
    pending, done = [], []
    with open(QUEUE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('==='):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                status = parts[1].upper()
                if status == 'DONE':
                    done.append(parts)
                else:
                    pending.append(parts)
    return pending, done

def write_queue(pending, done):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        "# 小喵任务队列 (Task Queue)",
        f"# 最后更新: {now}",
        "# 格式：ID | 状态 | 优先级 | 任务描述 | 备注",
        "",
        "# === 当前任务队列 ===",
    ]
    for t in pending:
        lines.append(' | '.join(t))
    lines.extend(["", "# === 已完成任务存档 ==="])
    for t in done[-20:]:  # 只保留最近20条
        lines.append(' | '.join(t))
    with open(QUEUE_FILE, 'w') as f:
        f.write('\n'.join(lines) + '\n')

def show():
    pending, done = read_queue()
    print("📋 任务队列")
    print(f"   待完成: {len(pending)} | 已完成: {len(done)}")
    for t in pending:
        status_icon = {"PENDING":"⏳","IN_PROGRESS":"🔄","FAILED":"❌"}.get(t[1],"❓")
        print(f"   {status_icon} [{t[2]}] {t[3]}")
    if done:
        print(f"\n   最近完成:")
        for t in done[-5:]:
            print(f"   ✅ {t[3]}")

def add(task_desc, priority="P2"):
    pending, done = read_queue()
    tid = f"T{len(pending)+len(done)+1:03d}"
    pending.append([tid, "PENDING", priority, task_desc, ""])
    write_queue(pending, done)
    print(f"✅ 已添加任务 {tid}: {task_desc}")

def start(tid):
    pending, done = read_queue()
    for t in pending:
        if t[0] == tid:
            t[1] = "IN_PROGRESS"
            write_queue(pending, done)
            print(f"🔄 开始执行: {t[3]}")
            return
    print(f"❌ 未找到任务 {tid}")

def complete(tid, note=""):
    pending, done = read_queue()
    for i, t in enumerate(pending):
        if t[0] == tid:
            t[1] = "DONE"
            if note: t[4] = note
            done.append(pending.pop(i))
            write_queue(pending, done)
            print(f"✅ 已完成: {t[3]}")
            return
    print(f"❌ 未找到任务 {tid}")

def fail(tid, reason=""):
    pending, done = read_queue()
    for t in pending:
        if t[0] == tid:
            t[1] = "FAILED"
            t[4] = reason
            write_queue(pending, done)
            print(f"❌ 失败: {t[3]} — {reason}")
            return

if __name__ == '__main__':
    if len(sys.argv) < 2:
        show()
    elif sys.argv[1] == 'add':
        add(sys.argv[2] if len(sys.argv) > 2 else "新任务", sys.argv[3] if len(sys.argv) > 3 else "P2")
    elif sys.argv[1] == 'start':
        start(sys.argv[2])
    elif sys.argv[1] == 'done':
        complete(sys.argv[2], sys.argv[3] if len(sys.argv) > 2 else "")
    elif sys.argv[1] == 'fail':
        fail(sys.argv[2], sys.argv[3] if len(sys.argv) > 2 else "")
    elif sys.argv[1] == 'show':
        show()
