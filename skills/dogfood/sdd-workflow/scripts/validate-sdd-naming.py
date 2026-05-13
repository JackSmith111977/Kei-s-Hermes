#!/usr/bin/env python3
"""
validate-sdd-naming.py v1.0 — SDD 文档命名规范门禁检查

检查项目文档是否符合 SDD 统一命名规范：
  EPIC-{n}.md                        (如 EPIC-001)
  SPEC-{epic}-{seq}.md               (如 SPEC-1-4)
  STORY-{epic}-{spec}-{seq}.md       (如 STORY-1-4-3)
  ARCH-{epic}-{spec}-{seq}.md        (如 ARCH-1-4-3)
  TECH-{epic}-{spec}-{seq}.md        (如 TECH-1-4-3)

用法:
  python3 validate-sdd-naming.py [--dir <项目路径>] [--json] [--fix]

选项:
  --dir <path>   项目根目录（默认: ~/projects/hermes-cap-pack）
  --json         JSON 格式输出（用于 CI 集成）
  --fix          自动修复可检测的违规（如文件名与内部 ID 不一致）
  --ci           严格模式，exit code=1 时阻止 CI 通过

输出: 命名规范合规报告，exit code=0（通过）/ 1（有违规）
"""

import os
import re
import sys
import json
import glob

# ── 命名规范正则 ──

# EPIC: EPIC-001.md, EPIC-001-feasibility.md（允许带描述）
RE_EPIC = re.compile(r'^EPIC-(\d{3})(?:-.+)?\.md$')
# SPEC: SPEC-1-4.md, SPEC-2-1.md
RE_SPEC = re.compile(r'^SPEC-(\d+)-(\d+)\.md$')
# STORY: STORY-1-4-3.md, STORY-2-2-1.md
RE_STORY = re.compile(r'^STORY-(\d+)-(\d+)-(\d+)\.md$')
# ARCH: ARCH-1-4-3.md
RE_ARCH = re.compile(r'^ARCH-(\d+)-(\d+)-(\d+)\.md$')
# TECH: TECH-1-4-3.md
RE_TECH = re.compile(r'^TECH-(\d+)-(\d+)-(\d+)\.md$')

# 旧格式正则（违规检测用）
RE_OLD_EPIC = re.compile(r'^EPIC-\d{3}-.+\.md$')       # EPIC-001-feasibility.md（允许保留描述）
RE_OLD_SPEC = re.compile(r'^SPEC-\d{3}-.+\.md$')       # SPEC-001-splitting.md（旧格式）
RE_OLD_STORY = re.compile(r'^STORY-\d{3}-.+\.md$')     # STORY-001-splitting.md（旧格式）
RE_OLD_STORY_2 = re.compile(r'^STORY-\d+-\d+\.md$')    # STORY-1-1.md（缺少 spec 层级）
# PLAN 格式（允许带描述，但应放在 plans/ 目录）
RE_PLAN = re.compile(r'^EPIC-\d{3}-.+\.md$')           # EPIC-003-phase1-decomposition

# 所有有效的文档类型
VALID_DOC_TYPES = {
    'EPIC': RE_EPIC,
    'SPEC': RE_SPEC,
    'STORY': RE_STORY,
    'ARCH': RE_ARCH,
    'TECH': RE_TECH,
}

# 模板文件白名单（不检查命名规范）
TEMPLATE_WHITELIST = {
    'STORY-TEMPLATE.md',
}


def scan_docs(project_root):
    """扫描项目 docs/ 目录，收集所有文档文件"""
    docs_dir = os.path.join(project_root, 'docs')
    if not os.path.isdir(docs_dir):
        stories_dir = os.path.join(project_root, 'docs', 'stories')
        if os.path.isdir(stories_dir):
            docs_dir = os.path.join(project_root, 'docs')
        else:
            return [], [], [], [], [], [], []

    epic_files = []
    spec_files = []
    story_files = []
    other_docs = []
    arch_files = []
    tech_files = []
    old_format_files = []  # 旧格式文件（等迁移）
    plan_files = []  # PLAN 文件（在 plans/ 目录下）

    for root, dirs, files in os.walk(docs_dir):
        for f in files:
            if not f.endswith('.md'):
                continue
            if f in TEMPLATE_WHITELIST:
                continue

            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, project_root)
            is_plans_dir = 'plans' in root.split(os.sep)

            # 先匹配新格式
            if RE_EPIC.match(f):
                epic_files.append((f, full_path, rel_path))
            elif RE_SPEC.match(f):
                spec_files.append((f, full_path, rel_path))
            elif RE_STORY.match(f):
                story_files.append((f, full_path, rel_path))
            elif RE_ARCH.match(f):
                arch_files.append((f, full_path, rel_path))
            elif RE_TECH.match(f):
                tech_files.append((f, full_path, rel_path))
            # PLAN 文件（在 plans/ 目录下，EPIC-{n}-{desc} 格式）
            elif is_plans_dir and RE_PLAN.match(f):
                plan_files.append((f, full_path, rel_path))
            # 再匹配旧格式（用于迁移检测）
            elif RE_OLD_SPEC.match(f) or RE_OLD_STORY.match(f) or RE_OLD_STORY_2.match(f):
                old_format_files.append((f, full_path, rel_path))
            else:
                other_docs.append((f, full_path, rel_path))

    return epic_files, spec_files, story_files, arch_files, tech_files, old_format_files, other_docs, plan_files


def check_file_internal_id(filename, full_path, doc_type):
    """检查文件内部 story_id 或 epic_id 是否与文件名一致"""
    violations = []
    try:
        with open(full_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
    except Exception as e:
        return [{'file': filename, 'type': doc_type, 'issue': f'无法读取文件: {e}'}]

    file_stem = filename.replace('.md', '')

    # 检查 YAML frontmatter 中的 id 字段
    id_patterns = {
        'story_id': r'\*\*story_id\*\*:\s*`([^`]+)`',
        'epic_id': r'\*\*epic_id\*\*:\s*`([^`]+)`',
        # EPIC-002 风格的 frontmatter
        'story_id_alt': r'story:\s*"([^"]+)"',
        # SPEC 标题
        'spec_title': r'^# SPEC-(\d+-\d+)',
        'story_title': r'^# STORY-(\d+-\d+-\d+)',
    }

    for field, pattern in id_patterns.items():
        matches = re.findall(pattern, content)
        for m in matches:
            expected = file_stem
            # EPIC 特殊处理：EPIC-003-module-extraction.md → 内部 epic_id: EPIC-003 ✅（允许描述后缀）
            if doc_type == 'EPIC' and field == 'epic_id':
                epic_base = re.match(r'EPIC-\d{3}', file_stem)
                if epic_base and m == epic_base.group(0):
                    continue  # 允许 EPIC-003-module-extraction ↔ EPIC-003
                if m != expected and m != expected.replace('EPIC-', ''):
                    violations.append({
                        'file': filename,
                        'type': doc_type,
                        'issue': f'内部 epic_id `{m}` 与文件名 `{expected}` 不一致',
                    })
            elif field in ('story_id', 'story_id_alt') and m != expected:
                violations.append({
                    'file': filename,
                    'type': doc_type,
                    'issue': f'内部 story_id `{m}` 与文件名 `{expected}` 不一致',
                })
            elif field in ('spec_title', 'story_title'):
                file_id = file_stem.split('-', 1)[1] if '-' in file_stem else file_stem
                if m != file_id:
                    violations.append({
                        'file': filename,
                        'type': doc_type,
                        'issue': f'内部标题 ID `{m}` 与文件名 ID `{file_id}` 不一致',
                    })

    return violations


def check_old_format(filename, full_path):
    """检测旧格式文件"""
    result = []
    if RE_OLD_EPIC.match(filename):
        # EPIC 文件允许带描述（顶层入口，方便识别）
        pass
    if RE_OLD_SPEC.match(filename):
        result.append({
            'file': filename,
            'type': 'SPEC',
            'issue': '旧格式：SPEC-{n}-{desc}，应改为 SPEC-{epic}-{seq}',
            'severity': 'error',
        })
    if RE_OLD_STORY.match(filename):
        result.append({
            'file': filename,
            'type': 'STORY',
            'issue': '旧格式：STORY-{n}-{desc}，应改为 STORY-{epic}-{spec}-{seq}',
            'severity': 'error',
        })
    if RE_OLD_STORY_2.match(filename) and not RE_STORY.match(filename):
        result.append({
            'file': filename,
            'type': 'STORY',
            'issue': '旧格式：STORY-{epic}-{seq}（缺少 SPEC 层级），应改为 STORY-{epic}-{spec}-{seq}',
            'severity': 'error',
        })
    return result


def check_spec_epic_consistency(spec_files, epic_files):
    """检查 SPEC 文件引用的 EPIC 是否真实存在"""
    violations = []
    # 已有的 EPIC 编号
    epic_ids = set()
    for fname, _, _ in epic_files:
        m = RE_EPIC.match(fname)
        if m:
            epic_ids.add(m.group(1))

    for fname, _, _ in spec_files:
        m = RE_SPEC.match(fname)
        if m:
            epic_num = m.group(1)
            # EPIC 编号可能带前导零也可能不带
            if epic_num not in epic_ids and epic_num.zfill(3) not in epic_ids:
                violations.append({
                    'file': fname,
                    'type': 'SPEC',
                    'issue': f'引用的 EPIC 编号 {epic_num} 无对应 EPIC 文件',
                    'severity': 'warning',
                })

    return violations


def check_orphan_stories(story_files, spec_files):
    """检查 Story 是否都在 SPEC 目录中有对应的 SPEC"""
    spec_ids = set()
    for fname, _, _ in spec_files:
        m = RE_SPEC.match(fname)
        if m:
            spec_ids.add(f'{m.group(1)}-{m.group(2)}')

    violations = []
    for fname, _, _ in story_files:
        m = RE_STORY.match(fname)
        if m:
            spec_id = f'{m.group(1)}-{m.group(2)}'
            if spec_id not in spec_ids:
                violations.append({
                    'file': fname,
                    'type': 'STORY',
                    'issue': f'引用的 SPEC {spec_id} 无对应 SPEC 文件',
                    'severity': 'warning',
                })

    return violations


def analyze(project_root):
    """执行完整命名规范分析"""
    result = {
        'project': project_root,
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'total_files': 0,
            'valid': 0,
            'violations': 0,
            'warnings': 0,
        },
        'files': {},
        'violations': [],
        'warnings': [],
    }

    epic_files, spec_files, story_files, arch_files, tech_files, old_format_files, other_docs, plan_files = scan_docs(project_root)

    # 统计各类文件
    all_files = epic_files + spec_files + story_files + arch_files + tech_files + old_format_files + plan_files
    result['summary']['total_files'] = len(all_files) + len(other_docs)

    # 检查旧格式（包括旧格式文件分类中的和常见的）
    for fname, fpath, rel_path in old_format_files:
        old_issues = check_old_format(fname, fpath)
        for issue in old_issues:
            if issue['severity'] == 'error':
                result['violations'].append(issue)
                result['summary']['violations'] += 1
            else:
                result['warnings'].append(issue)
                result['summary']['warnings'] += 1

    # 检查内部一致性
    doc_type_map = {}
    for fname, fpath, _ in epic_files:
        doc_type_map[(fname, fpath)] = 'EPIC'
    for fname, fpath, _ in spec_files:
        doc_type_map[(fname, fpath)] = 'SPEC'
    for fname, fpath, _ in story_files:
        doc_type_map[(fname, fpath)] = 'STORY'
    for fname, fpath, _ in arch_files:
        doc_type_map[(fname, fpath)] = 'ARCH'
    for fname, fpath, _ in tech_files:
        doc_type_map[(fname, fpath)] = 'TECH'

    for (fname, fpath), dtype in doc_type_map.items():
        internal_issues = check_file_internal_id(fname, fpath, dtype)
        for issue in internal_issues:
            result['violations'].append(issue)
            result['summary']['violations'] += 1

    # 检查 SPEC → EPIC 一致性
    spec_epic_issues = check_spec_epic_consistency(spec_files, epic_files)
    for issue in spec_epic_issues:
        result['warnings'].append(issue)
        result['summary']['warnings'] += 1

    # 检查 STORY → SPEC 一致性
    orphan_issues = check_orphan_stories(story_files, spec_files)
    for issue in orphan_issues:
        result['warnings'].append(issue)
        result['summary']['warnings'] += 1

    # 统计有效文件
    result['summary']['valid'] = (
        len(epic_files) + len(spec_files) + len(story_files) +
        len(arch_files) + len(tech_files)
    )

    # 文件详细清单
    categorize = {
        'epic': [f[0] for f in epic_files],
        'spec': [f[0] for f in spec_files],
        'story': [f[0] for f in story_files],
        'arch': [f[0] for f in arch_files],
        'tech': [f[0] for f in tech_files],
        'plan': [f[0] for f in plan_files],
        'old_format': [f[0] for f in old_format_files],
        'other': [f[0] for f in other_docs],
    }
    result['files'] = categorize

    return result


def print_report(result, json_output=False):
    """打印人类可读的报告"""
    if json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result['summary']['violations'] > 0

    s = result['summary']
    print(f"\n{'='*60}")
    print(f"  📋 SDD 文档命名规范门禁报告")
    print(f"  📂 项目: {result['project']}")
    print(f"  🕐 时间: {result['timestamp']}")
    print(f"{'='*60}")

    # 文件统计
    print(f"\n📊 文件统计:")
    for cat, files in result['files'].items():
        if files:
            print(f"  {cat}: {len(files)}")

    # 合规 vs 违规
    if s['violations'] == 0 and s['warnings'] == 0:
        print(f"\n✅ 全部 {s['valid']} 个文档命名规范合规！")
        return False

    if s['violations'] > 0:
        print(f"\n🔴 违规 ({s['violations']}):")
        for v in result['violations']:
            print(f"  ❌ [{v['type']}] {v['file']}: {v['issue']}")

    if s['warnings'] > 0:
        print(f"\n🟡 警告 ({s['warnings']}):")
        for w in result['warnings']:
            print(f"  ⚠️  [{w['type']}] {w['file']}: {w['issue']}")

    return s['violations'] > 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description='SDD 文档命名规范门禁检查')
    parser.add_argument('--dir', default=os.path.expanduser('~/projects/hermes-cap-pack'),
                        help='项目根目录')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    parser.add_argument('--ci', action='store_true', help='严格模式，违规时 exit code=1')
    args = parser.parse_args()

    result = analyze(args.dir)
    has_violations = print_report(result, json_output=args.json)

    if has_violations and args.ci:
        print(f"\n🛑 CI 门禁拦截：存在 {result['summary']['violations']} 个命名规范违规")
        sys.exit(1)
    elif has_violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
