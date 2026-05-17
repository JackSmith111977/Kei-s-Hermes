#!/usr/bin/env python3
"""
fs-audit.py — 文件系统规范审计引擎

Hermes Shell Hooks 系统调用。从 stdin 读取 JSON，执行规范检查，
输出结果到 stdout。

协议:
  输入: 单行 JSON {"hook_event_name", "tool_name", "tool_input", "result", "session_id"}
  输出: JSON {"action": "block", "message": "..."} 或 {"audited": true, ...}
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 配置 ───────────────────────────────────────────────────────────────
HERMES_HOME = os.path.expanduser(os.environ.get("HERMES_HOME", "~/.hermes"))
AUDIT_LOG = os.path.join(HERMES_HOME, "data", "fs-audit", "audit.log")
RULES_FILE = os.path.join(HERMES_HOME, "scripts", "fs-enforce", "rules.yaml")

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# 保护路径（相对于 HERMES_HOME）
PROTECTED_PATHS = [
    "AGENTS.md",
    "SOUL.md",
    "config/config.yaml",
    "state.db",
]

# 禁止的文件名（全小写比较）
FORBIDDEN_NAMES = {"test.txt", "output.json", "file.py", "new_1.md",
                   "untitled.md", "tmp.txt", "index.html"}

# 禁止字符
FORBIDDEN_CHARS = set(' \\:*?"<>|')


def load_rules() -> dict:
    """加载 rules.yaml，出错时返回空字典。"""
    try:
        import yaml
        with open(RULES_FILE) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def is_protected(real_path: str) -> str | None:
    """检查路径是否在保护列表中。返回保护路径名或 None。"""
    for p in PROTECTED_PATHS:
        target = os.path.realpath(os.path.join(HERMES_HOME, p))
        if real_path == target:
            return p
    return None


def check_naming(basename: str) -> list[str]:
    """检查文件名是否符合规范。返回违规列表。"""
    issues = []
    if " " in basename:
        issues.append("文件名含空格")
    for c in FORBIDDEN_CHARS:
        if c in basename:
            issues.append(f"文件名含禁止字符 '{c}'")
            break
    if basename.lower() in FORBIDDEN_NAMES:
        issues.append("禁止的文件名")
    if len(basename) > 120:
        issues.append("文件名超长(>120字符)")
    if "." in basename:
        ext = basename.rsplit(".", 1)[1]
        if ext != ext.lower():
            issues.append("扩展名未小写")
    return issues


def check_scope(first_dir: str, ext: str) -> list[str]:
    """检查目录归属。返回违规列表。"""
    issues = []
    # scripts/ 只放 .py 和 .sh
    if first_dir == "scripts" and ext not in (".py", ".sh", ".bash", ""):
        issues.append(f"{ext} 文件不应放在 scripts/")
    # skills/ 只放 .md
    if first_dir == "skills" and ext != ".md":
        issues.append(f"{ext} 文件不应放在 skills/")
    # config/ 只放 .yaml 和 .json
    if first_dir == "config" and ext not in (".yaml", ".yml", ".json", ""):
        issues.append(f"{ext} 文件不应放在 config/")
    # cache/ 不应放 .md
    if first_dir == "cache" and ext == ".md":
        issues.append(f".md 文件不应放在 cache/")
    return issues


def extract_path(tool_name: str, tool_input: dict) -> str:
    """从工具参数中提取文件路径。"""
    path = (tool_input or {}).get("path", "") or ""
    if path:
        return path
    if tool_name == "terminal":
        cmd = (tool_input or {}).get("command", "") or ""
        for token in cmd.split():
            expanded = os.path.expanduser(token)
            if expanded.startswith(("/home/", "/tmp/", os.path.expanduser("~"))):
                return token
    return ""


def audit(tool_name: str, path: str, args: dict, result: str,
          session_id: str, hook_event: str) -> dict | None:
    """执行审计检查，返回 block 指令或 None。"""
    if tool_name not in ("write_file", "patch", "terminal"):
        return {"skipped": True, "reason": "not_file_operation"}

    path = extract_path(tool_name, args)
    if not path:
        return {"skipped": True, "reason": "no_path"}

    expanded = os.path.expanduser(path)
    real_path = os.path.realpath(expanded) if os.path.exists(expanded) else expanded

    # ── 检查1: 保护路径 ──
    protected = is_protected(real_path)
    if protected:
        entry = {
            "ts": NOW, "hook_event": hook_event, "tool": tool_name,
            "path": path, "real_path": real_path,
            "verdict": "BLOCKED", "reason": f"protected_path:{protected}",
            "session": session_id,
        }
        _append_log(entry)
        if hook_event == "pre_tool_call":
            return {"action": "block", "message": f"禁止写入保护路径: {protected}"}
        return {"audited": True, "verdict": "BLOCKED", "reason": "protected_path"}

    # ── 检查2: 命名规范 ──
    basename = os.path.basename(real_path)
    naming_issues = check_naming(basename)
    if naming_issues and hook_event == "pre_tool_call":
        msg = "文件命名违规: " + "; ".join(naming_issues)
        entry = {
            "ts": NOW, "hook_event": hook_event, "tool": tool_name,
            "path": path, "real_path": real_path,
            "verdict": "BLOCKED", "reason": "naming:" + ",".join(naming_issues),
            "session": session_id,
        }
        _append_log(entry)
        return {"action": "block", "message": msg}

    # ── 检查3: 目录归属 ──
    scope_issues = []
    if real_path.startswith(HERMES_HOME):
        rel = real_path[len(HERMES_HOME):].lstrip("/")
        first_dir = rel.split("/")[0] if "/" in rel else ""
        ext = os.path.splitext(basename)[1].lower()
        scope_issues = check_scope(first_dir, ext)

    if scope_issues and hook_event == "pre_tool_call":
        msg = "目录归属违规: " + "; ".join(scope_issues)
        entry = {
            "ts": NOW, "hook_event": hook_event, "tool": tool_name,
            "path": path, "real_path": real_path,
            "verdict": "BLOCKED", "reason": "scope:" + ",".join(scope_issues),
            "session": session_id,
        }
        _append_log(entry)
        return {"action": "block", "message": msg}

    # ── 审计日志（PASS/WARN） ──
    verdict = "PASS" if not naming_issues else "WARN"
    entry = {
        "ts": NOW, "hook_event": hook_event, "tool": tool_name,
        "path": path, "real_path": real_path,
        "relative_to_home": real_path[len(HERMES_HOME):] if real_path.startswith(HERMES_HOME) else "",
        "verdict": verdict,
        "naming_issues": naming_issues,
        "scope_issues": scope_issues,
        "session": session_id,
        "result_preview": (result or "")[:200],
    }
    _append_log(entry)
    return {"audited": True, "verdict": verdict}


def _append_log(entry: dict) -> None:
    """追加一条审计日志。"""
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 日志写入失败不中断主流程


def main() -> None:
    raw = sys.stdin.read()
    if not raw or raw.strip() in ("", "null"):
        json.dump({}, sys.stdout)
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        json.dump({"error": "invalid_json"}, sys.stdout)
        return

    result = audit(
        tool_name=data.get("tool_name", ""),
        path=data.get("tool_input", {}).get("path", ""),
        args=data.get("tool_input", {}),
        result=data.get("result", ""),
        session_id=data.get("session_id", ""),
        hook_event=data.get("hook_event_name", ""),
    )
    json.dump(result or {}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
