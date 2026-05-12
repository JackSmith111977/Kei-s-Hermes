#!/usr/bin/env python3
"""
SRA QA Status Checker v1.0

Usage:
    python3 scripts/qa-status.py                    # All gates (from project root)
    python3 scripts/qa-status.py --gates L0,L1      # Selected gates
    python3 scripts/qa-status.py --gates L0,L1,L2,L3,L4 --json  # JSON output

Exit code:
    0 = all required gates pass
    1 = one or more gates fail
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def run_cmd(cmd: list[str], cwd: str, timeout: int = 60) -> dict:
    """Run a command and return result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": f"Timeout after {timeout}s"}
    except FileNotFoundError as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


# ── Gate checkers ──────────────────────────────────────


def check_l0(project_dir: str) -> dict:
    """L0: ruff lint + fixture integrity."""
    results = {"ruff": None, "fixtures": None}

    # ruff check
    r = run_cmd(["ruff", "check", "skill_advisor/", "tests/"], cwd=project_dir, timeout=30)
    results["ruff"] = {
        "status": "pass" if r["returncode"] == 0 else "fail",
        "detail": (r["stdout"].strip() or r["stderr"].strip())[:200],
    }

    # fixture integrity
    fixtures_dir = os.path.join(project_dir, "tests", "fixtures", "skills")
    if os.path.isdir(fixtures_dir):
        count = sum(1 for root, _, files in os.walk(fixtures_dir) for f in files if f == "SKILL.md")
        results["fixtures"] = {
            "status": "pass" if count >= 300 else "fail",
            "detail": f"{count} SKILL.md files (threshold: 300)",
        }
    else:
        results["fixtures"] = {"status": "skip", "detail": "Fixture dir not found"}

    return results


def check_l1(project_dir: str) -> dict:
    """L1: Full pytest."""
    r = run_cmd(
        ["python", "-m", "pytest", "tests/", "-q", "--tb=short", "-o", "addopts="],
        cwd=project_dir, timeout=120,
    )
    lines = [l for l in r["stdout"].split("\n") if l.strip()]
    summary = lines[-1] if lines else ""

    if "failed" in summary:
        for part in summary.split():
            if part.isdigit():
                return {"status": "fail", "detail": summary}
    elif "passed" in summary:
        return {"status": "pass", "detail": summary}
    else:
        return {"status": "error" if r["returncode"] != 0 else "pass", "detail": summary or r["stderr"]}


def check_l2(project_dir: str) -> dict:
    """L2: Integration tests."""
    integration_files = [
        "tests/test_daemon_http.py",
        "tests/test_cli.py",
        "tests/test_adapters.py",
        "tests/test_contract.py",
        "tests/test_dropin.py",
        "tests/test_validate.py",
    ]
    existing = [f for f in integration_files if os.path.exists(os.path.join(project_dir, f))]
    if not existing:
        return {"status": "skip", "detail": "No integration test files found"}

    r = run_cmd(
        ["python", "-m", "pytest"] + existing + ["-q", "--tb=short", "-o", "addopts="],
        cwd=project_dir, timeout=120,
    )
    summary = [l for l in r["stdout"].split("\n") if l.strip()][-1:] if r["stdout"] else [""]
    return {"status": "pass" if r["returncode"] == 0 else "fail", "detail": summary[0] if summary else r["stderr"]}


def check_l3(project_dir: str) -> dict:
    """L3: System tests (concurrency, stress)."""
    system_files = [
        "tests/test_concurrency.py",
        "tests/test_force.py",
        "tests/test_singleton.py",
    ]
    existing = [f for f in system_files if os.path.exists(os.path.join(project_dir, f))]
    if not existing:
        return {"status": "skip", "detail": "No system test files found"}

    r = run_cmd(
        ["python", "-m", "pytest"] + existing + ["-q", "--tb=short", "-o", "addopts="],
        cwd=project_dir, timeout=120,
    )
    return {"status": "pass" if r["returncode"] == 0 else "fail", "detail": (r["stdout"].strip() or r["stderr"].strip())[:200]}


def check_l4(project_dir: str) -> dict:
    """L4: Version + CHANGELOG + build verification."""
    results = {"version": None, "changelog": None, "import_check": None}

    # Version check
    r = run_cmd(
        ["python", "-c", "from skill_advisor import __version__; print(__version__)"],
        cwd=project_dir, timeout=10,
    )
    version = r["stdout"].strip()
    results["version"] = {"status": "pass" if version else "fail", "detail": version or r["stderr"]}

    # CHANGELOG check
    changelog_path = os.path.join(project_dir, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        r = run_cmd(["grep", "-c", "^## ", "CHANGELOG.md"], cwd=project_dir, timeout=5)
        count = r["stdout"].strip()
        results["changelog"] = {
            "status": "pass" if r["returncode"] == 0 and count and int(count) > 0 else "warn",
            "detail": f"{count} release entries" if count else "No entries found",
        }
    else:
        results["changelog"] = {"status": "skip", "detail": "CHANGELOG.md not found"}

    # Import smoke test
    r = run_cmd(
        ["python", "-c", "from skill_advisor.advisor import SkillAdvisor; print('import ok')"],
        cwd=project_dir, timeout=10,
    )
    results["import_check"] = {
        "status": "pass" if r["returncode"] == 0 else "fail",
        "detail": r["stdout"].strip() or r["stderr"].strip(),
    }

    return results


# ── Main ───────────────────────────────────────────────


GATE_CHECKERS = {
    "L0": check_l0,
    "L1": check_l1,
    "L2": check_l2,
    "L3": check_l3,
    "L4": check_l4,
}

GATE_NAMES = {
    "L0": "Static Analysis (ruff + fixtures)",
    "L1": "Unit Tests (pytest full suite)",
    "L2": "Integration Tests (HTTP/CLI/adapters)",
    "L3": "System Tests (concurrency/stress)",
    "L4": "Release Gate (version/CHANGELOG/build)",
}


def main():
    parser = argparse.ArgumentParser(description="SRA QA Status Checker")
    parser.add_argument("--gates", default="L0,L1,L2", help="Comma-separated gates (default: L0,L1,L2)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--project-dir", default=".", help="SRA project root directory")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isfile(os.path.join(project_dir, "pyproject.toml")):
        print(f"❌ No pyproject.toml found in {project_dir}")
        sys.exit(1)

    gates = [g.strip().upper() for g in args.gates.split(",")]
    results = {}
    all_pass = True

    for gate in gates:
        if gate in GATE_CHECKERS:
            results[gate] = GATE_CHECKERS[gate](project_dir)
            if results[gate].get("status") == "fail":
                all_pass = False
        else:
            results[gate] = {"status": "error", "detail": f"Unknown gate: {gate}"}
            all_pass = False

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": "sra-agent",
        "gates": results,
        "summary": "✅ All gates pass" if all_pass else "❌ One or more gates fail",
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  SRA QA Status Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        for gate in gates:
            g = results.get(gate, {})
            status_icon = {"pass": "✅", "fail": "❌", "skip": "⏭️", "warn": "⚠️", "error": "🛑"}
            icon = status_icon.get(g.get("status", ""), "❓")
            name = GATE_NAMES.get(gate, gate)
            print(f"  {icon} {gate} — {name}")
            detail = str(g.get("detail", ""))[:120]
            print(f"     {detail}")
            print()

        print(f"  {'='*40}")
        print(f"  {report['summary']}")
        print(f"  {'='*40}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
