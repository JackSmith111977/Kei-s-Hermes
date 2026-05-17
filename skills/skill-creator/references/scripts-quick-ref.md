# Script Suite Quick Reference — skill-creator v6.0+

> Companion reference for the new quality management scripts shipped with skill-creator v6.0.
> Created 2026-05-17 during the SQS v2.0 + lifecycle management upgrade.

## Overview

skill-creator v6.0 ships 7 scripts in `scripts/`. This document is the usage quick reference.

## 1. `skill-quality-score.py` v2.0

**Purpose**: SQS v2.0 quality scoring — 7 dimensions × 20 pts = 140

**Usage**:
```bash
# Score a single skill
python3 skill-quality-score.py <skill-name>

# Verbose with dimension breakdown
python3 skill-quality-score.py <skill-name> --verbose

# Full audit (all skills)
python3 skill-quality-score.py --audit

# Audit with threshold
python3 skill-quality-score.py --audit --threshold 70

# JSON output
python3 skill-quality-score.py <skill-name> --json
```

**Output levels**:
- 🟢 Excellent: 119-140 — directly deployable
- 🟡 Good: 98-118 — optimize weak dimensions
- 🟠 Needs work: 70-97 — must improve before deploy
- 🔴 Failing: <70 — prohibited from deploy

## 2. `quality-gate.py`

**Purpose**: Pre-operation gate for create/edit/delete. Called by `pre_flight.py`.

**Usage**:
```bash
# Check before creating
python3 quality-gate.py create <skill-name>

# Check before editing
python3 quality-gate.py edit <skill-name>

# Check before deleting
python3 quality-gate.py delete <skill-name>

# Just check (no action)
python3 quality-gate.py check <skill-name> --json
```

**Checks performed**:
1. SQS score ≥ threshold (create: 50, edit: 30)
2. YAML frontmatter completeness
3. Broken `depends_on` references
4. File naming violations
5. Delete: verify no referrers

## 3. `skill-lifecycle-audit.py` v2.0

**Purpose**: Lifecycle audit + auto-archive for deprecated skills.

**Usage**:
```bash
# Audit single skill
python3 skill-lifecycle-audit.py <skill-name>

# Full audit
python3 skill-lifecycle-audit.py --audit

# HTML report
python3 skill-lifecycle-audit.py --audit --html

# View lifecycle state
python3 skill-lifecycle-audit.py status [skill-name]

# Auto-archive deprecated (>30 days)
python3 skill-lifecycle-audit.py auto-archive
```

## 4. `skill-deprecation-gate.py`

**Purpose**: Safety check before deprecating or deleting a skill.

**Usage**:
```bash
# Check before deprecation
python3 skill-deprecation-gate.py pre-deprecate <skill-name>

# Check before deletion
python3 skill-deprecation-gate.py pre-delete <skill-name>

# Just check
python3 skill-deprecation-gate.py check <skill-name> --json
```

**Checks**: referrers, lifecycle status, backup existence, last-modified freshness.

## 5. `skill-state-manager.py`

**Purpose**: Unified lifecycle state management CLI.

**Usage**:
```bash
# List all states
python3 skill-state-manager.py list

# View single skill status
python3 skill-state-manager.py status <skill-name>

# Set status
python3 skill-state-manager.py set <skill-name> <status> --reason "..."

# Quick actions
python3 skill-state-manager.py deprecate <skill-name> --reason "..."
python3 skill-state-manager.py archive <skill-name>
python3 skill-state-manager.py revive <skill-name>

# Batch operation (dry-run first!)
python3 skill-state-manager.py batch "sqs<50" "under_review" --dry-run
```

**Valid statuses**: `active` → `under_review` → `frozen` → `deprecated` → `archived`

## 6. `skill-health-check.py` (in `~/.hermes/scripts/fs-enforce/`)

**Purpose**: Integrated into daily cron reports. Checks field coverage health.

**Usage**:
```bash
python3 ~/.hermes/scripts/fs-enforce/skill-health-check.py
```

**Output**: Total skills, frontmatter coverage, depends_on coverage, triggers richness, stale count.

## 7. `dependency-scan.py`

**Purpose**: Dependency graph scanner. Detects `depends_on` and `referenced_by` chains.

**Usage**:
```bash
# Full scan
python3 dependency-scan.py

# Target mode
python3 dependency-scan.py --target <skill-name>

# JSON output
python3 dependency-scan.py --json
```

## Integration Pattern (combined workflow)

```bash
# Full quality-gated workflow for modifying a skill:
# 1. Pre-check
python3 quality-gate.py check <skill> --json

# 2. Audit current state
python3 skill-lifecycle-audit.py <skill> | head -5

# 3. Modify (via skill_manage or patch)

# 4. Re-verify
total=$(python3 skill-quality-score.py <skill> --json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['sqs_total'])")
echo "New SQS: $total/140"

# 5. Check lifecycle if needed
python3 skill-state-manager.py status <skill>
```
