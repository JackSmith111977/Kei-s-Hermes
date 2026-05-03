#!/usr/bin/env python3
"""
小喵的 Cron → 微信 转发守护进程
读取 cron local 输出，通过 gateway API 转发到微信
"""
import time
import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime

CRON_OUTPUT_DIR = Path.home() / ".hermes" / "cron" / "output"
JOBS_FILE = Path.home() / ".hermes" / "cron" / "jobs.json"
STATE_FILE = Path.home() / ".hermes" / "cron" / "forwarder_state.json"
POLL_INTERVAL = 30  # 每30秒检查一次

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"sent_hashes": [], "last_check": None}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_file_hash(filepath):
    content = filepath.read_bytes()
    return hashlib.md5(content).hexdigest()[:12]

def read_job_origin(job_id):
    """从 jobs.json 读取投递目标"""
    if not JOBS_FILE.exists():
        return None
    data = json.loads(JOBS_FILE.read_text())
    jobs = data.get("jobs", [])
    if isinstance(jobs, list):
        for job in jobs:
            if job.get("id") == job_id:
                return job.get("origin")
    elif isinstance(jobs, dict):
        job = jobs
        if job.get("id") == job_id:
            return job.get("origin")
    return None

def forward_via_gateway(content: str, target: str) -> bool:
    """
    通过 Hermes gateway 的内部 API 发送消息到微信
    使用 gateway 的 HTTP API（如果可用）或直接调用 CLI
    """
    import subprocess
    try:
        # 尝试用 hermes CLI 发送
        result = subprocess.run(
            ["hermes", "send", "--target", target, "--message", content],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True
        print(f"[转发失败] CLI 返回: {result.stderr[:200]}")
    except Exception as e:
        print(f"[转发失败] {e}")
    return False

def main():
    print(f"🐱 小喵的 Cron→微信 转发守护进程启动")
    print(f"   监控目录: {CRON_OUTPUT_DIR}")
    print(f"   轮询间隔: {POLL_INTERVAL}s")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("---")

    state = load_state()

    while True:
        try:
            if not CRON_OUTPUT_DIR.exists():
                time.sleep(POLL_INTERVAL)
                continue

            # 扫描所有 cron job 输出目录/文件
            for item in CRON_OUTPUT_DIR.iterdir():
                if item.is_dir():
                    # 这是一个 job_id 目录，扫描其中的输出文件
                    for output_file in sorted(item.iterdir(), key=lambda f: f.stat().st_mtime):
                        file_hash = get_file_hash(output_file)
                        if file_hash in state["sent_hashes"]:
                            continue

                        # 读取内容
                        content = output_file.read_text(encoding="utf-8", errors="replace").strip()
                        if not content:
                            state["sent_hashes"].append(file_hash)
                            continue

                        # 获取投递目标
                        job_id = item.name
                        origin = read_job_origin(job_id)
                        if not origin:
                            print(f"  [跳过] {job_id}: 无投递目标")
                            state["sent_hashes"].append(file_hash)
                            continue

                        target = origin.get("chat_id", "")
                        platform = origin.get("platform", "weixin")

                        print(f"  [转发] {job_id} → {platform}:{target}")
                        print(f"         内容: {content[:80]}...")

                        # 截断过长消息（微信单条限制）
                        if len(content) > 2000:
                            content = content[:2000] + "\n...(已截断)"

                        success = forward_via_gateway(content, f"{platform}:{target}")
                        if success:
                            print(f"         ✅ 发送成功")
                        else:
                            print(f"         ❌ 发送失败，下次重试")

                        state["sent_hashes"].append(file_hash)
                        state["last_check"] = datetime.now().isoformat()
                        save_state(state)

                elif item.is_file() and item.suffix in (".txt", ".md", ".json"):
                    # 直接输出的文件
                    file_hash = get_file_hash(item)
                    if file_hash in state["sent_hashes"]:
                        continue
                    content = item.read_text(encoding="utf-8", errors="replace").strip()
                    if content:
                        print(f"  [文件] {item.name}: {content[:60]}...")
                        state["sent_hashes"].append(file_hash)

            # 清理过期的 hash 记录（保留最近100条）
            if len(state["sent_hashes"]) > 100:
                state["sent_hashes"] = state["sent_hashes"][-100:]

        except KeyboardInterrupt:
            print("\n🐱 转发守护进程已停止")
            break
        except Exception as e:
            print(f"[错误] {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
