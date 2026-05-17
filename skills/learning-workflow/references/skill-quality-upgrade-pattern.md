# SQS-Driven Skill Quality Upgrade Pattern

> Created 2026-05-17 | Applies to: learning-workflow + skill-creator integration
> Origin: Phase 3-E of filesystem specification enforcement

## When to Use

When you need to systematically upgrade skill quality across the library. Not a single skill edit — a **scaled, data-driven improvement campaign** driven by SQS v2.0 scores.

## Prerequisites

- SQS v2.0 scoring system installed (`skill-quality-score.py` v2.0)
- Quality gate installed (`quality-gate.py`)
- Lifecycle management installed (`skill-state-manager.py`)

## Workflow

### Phase 1: Grade & Prioritize

```bash
# Run full SQS audit
cd ~/.hermes/skills/skill-creator/scripts
python3 skill-quality-score.py --audit
```

Extract tiered priority list:
- **S-tier** (<70): Full deep upgrade needed
- **A-tier** (70-97): Targeted dimension fixes
- **B-tier** (98-118): Lightweight trigger/checklist additions

### Phase 2: Deep Learning Upgrade per Skill

For each S/A-tier skill:

```
skill_view(skill) + SQS --verbose  →  identify weak dimensions
    │
    ├── Type A「Content Enhancement」: needs Red Flags / code examples
    │   └── learning-workflow: search best practices → adapt → apply
    ├── Type B「Structural」: needs references/scripts/checklists
    │   └── direct operation: mkdir + move files
    └── Type C「Discoverability」: needs triggers/tags
        └── read standard → add to frontmatter
    │
    ├── quality-gate check (pre-validate)
    ├── apply changes
    └── quality-gate check (post-validate) + SQS diff
```

### Phase 3: Verify & Close

```bash
# Full regression audit
python3 skill-quality-score.py --audit

# Lifecycle audit with HTML report
python3 skill-lifecycle-audit.py --audit --html

# Track progress
python3 skill-state-manager.py list
```

## Key Metrics

| Metric | Target |
|--------|--------|
| S-tier count | 0 |
| Average SQS | ≥ 98/140 |
| S2 Structure avg | ≥ 15/20 |
| Zero-subdir skills | 0 |

## Example: Full Campaign Log (2026-05-17)

```
Phase 3 execution:
  P3A-T1: 76 zero-subdir skills → created references/ + scripts/
  P3A-T2: 10 skills → moved extra .md to references/
  P3B-T1: 9 single-category skills → merged into standard categories
  P3C-T1: 13 learning logs → archived/relocated
  P3E-T1~T3: 13 S-tier skills → deep upgraded (all passed threshold)
  Result: S-tier 13→0, zero-subdir 37%→0%, S2 avg +1.6
```
