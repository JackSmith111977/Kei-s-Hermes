#!/usr/bin/env python3
"""
File Index Generator for Hermes Agent System
生成 FILE_INDEX.md（人类可读）和 FILE_INDEX.json（机器可读）

用法:
    python3 file-index.py [目录路径] [--output-dir 输出目录]
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path


# 要排除的目录和文件
EXCLUDE_DIRS = {
    '__pycache__', '.git', 'node_modules', '.venv', 'venv',
    'cache', '.cache', 'audio_cache', 'sessions', 'logs'
}

EXCLUDE_FILES = {
    '.env', 'auth.json', 'state.db', 'state.db-wal', 'state.db-shm',
    'auth.lock', 'gateway.pid', 'channel_directory.json',
    'feishu_seen_message_ids.json', 'processes.json'
}

# 文件类型映射
TYPE_MAP = {
    '.pdf': 'pdf', '.docx': 'docx', '.pptx': 'pptx', '.xlsx': 'xlsx',
    '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.gif': 'image', '.svg': 'image',
    '.html': 'html', '.htm': 'html',
    '.py': 'script', '.sh': 'script',
    '.md': 'markdown', '.txt': 'text',
    '.yaml': 'config', '.yml': 'config', '.toml': 'config', '.json': 'config',
    '.json': 'data', '.db': 'data',
    '.js': 'code', '.ts': 'code',
}

# 分类映射
CATEGORY_MAP = {
    'pdf': 'output/pdf',
    'docx': 'output/documents',
    'pptx': 'output/documents',
    'xlsx': 'output/documents',
    'image': 'output/images',
    'html': 'output/html',
    'script': 'scripts',
    'config': 'config',
    'markdown': 'docs',
}


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_file_type(filename):
    """获取文件类型"""
    ext = Path(filename).suffix.lower()
    return TYPE_MAP.get(ext, 'other')


def get_category(file_type):
    """获取文件分类"""
    return CATEGORY_MAP.get(file_type, 'other')


def is_important(path, filename):
    """判断文件是否重要"""
    important_files = {
        'SOUL.md', 'MEMORY.md', 'FILE_INDEX.md', 'FILE_INDEX.json',
        'config.yaml', 'TASK_QUEUE.md'
    }
    if filename in important_files:
        return True
    if path.startswith('skills/') and filename == 'SKILL.md':
        return True
    return False


def generate_description(filename, file_type, rel_path):
    """生成文件描述"""
    name = Path(filename).stem
    # 转换连字符和 underscores 为可读名称
    desc = name.replace('-', ' ').replace('_', ' ').strip()
    desc = desc.title()
    if file_type == 'script':
        return f"Script: {desc}"
    elif file_type == 'pdf':
        return f"PDF Document: {desc}"
    elif file_type == 'image':
        return f"Image: {desc}"
    elif file_type == 'config':
        return f"Configuration: {desc}"
    elif filename == 'SKILL.md':
        parent = Path(rel_path).parent.name
        return f"Skill: {parent}"
    return desc


def scan_directory(root_dir):
    """扫描目录，返回文件列表"""
    files = []
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 排除目录
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)

            # 跳过 skill 内部的文件（只记录 SKILL.md）
            if '/references/' in rel_path or '/templates/' in rel_path:
                if filename != 'SKILL.md':
                    continue

            try:
                stat = os.stat(filepath)
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
            except OSError:
                continue

            file_type = get_file_type(filename)
            category = get_category(file_type)
            important = is_important(rel_path, filename)

            files.append({
                'path': rel_path,
                'name': filename,
                'type': file_type,
                'category': category,
                'size_bytes': size,
                'size_human': format_size(size),
                'modified': modified,
                'description': generate_description(filename, file_type, rel_path),
                'important': important
            })
            total_size += size

    return files, total_size


def generate_tree(files, root_dir, max_depth=3):
    """生成目录树"""
    tree_lines = []
    dirs_seen = set()

    # 先构建树结构
    tree = {}
    for f in files:
        parts = f['path'].split(os.sep)
        current = tree
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = f  # 文件节点

    def render_tree(node, prefix='', is_last=True, depth=0):
        if depth > max_depth:
            return

        items = sorted(node.items(), key=lambda x: (isinstance(x[1], dict), x[0]))
        for i, (name, value) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            connector = '└── ' if is_last_item else '├── '

            if isinstance(value, dict):
                # 检查是否是文件节点（有 'type' 键）还是目录节点
                if 'type' in value:
                    # 文件节点
                    icon = '📄'
                    if value.get('type') == 'pdf': icon = '📕'
                    elif value.get('type') == 'image': icon = '🖼️'
                    elif value.get('type') == 'script': icon = '⚙️'
                    elif value.get('type') == 'config': icon = '⚙️'
                    elif value.get('type') == 'markdown': icon = '📝'
                    elif value.get('important'): icon = '⭐'
                    tree_lines.append(f"{prefix}{connector}{icon} {name} ({value.get('size_human', '?')})")
                else:
                    # 目录节点
                    tree_lines.append(f"{prefix}{connector}📁 {name}/")
                    extension = '    ' if is_last_item else '│   '
                    render_tree(value, prefix + extension, is_last_item, depth + 1)
            else:
                tree_lines.append(f"{prefix}{connector}📄 {name}")

    tree_lines.append(f"~/.hermes/")
    render_tree(tree)
    return '\n'.join(tree_lines)


def generate_markdown_index(files, total_size, root_dir):
    """生成 FILE_INDEX.md"""
    tree = generate_tree(files, root_dir)

    # 按类型统计
    type_counts = {}
    category_counts = {}
    for f in files:
        type_counts[f['type']] = type_counts.get(f['type'], 0) + 1
        category_counts[f['category']] = category_counts.get(f['category'], 0) + 1

    # 重要文件清单
    important_files = [f for f in files if f.get('important')]

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    md = f"""# 📁 Hermes 文件索引

> **自动生成，请勿手动编辑**。运行 `python3 ~/.hermes/skills/file-system-manager/scripts/file-index.py` 更新。
>
> 生成时间: {now}
> 总文件数: {len(files)}
> 总大小: {format_size(total_size)}

## 目录树

```
{tree}
```

## 文件类型统计

| 类型 | 数量 |
|:---|:---|
"""
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        md += f"| {t} | {c} |\n"

    md += f"""
## 分类统计

| 分类 | 数量 |
|:---|:---|
"""
    for c, n in sorted(category_counts.items(), key=lambda x: -x[1]):
        md += f"| {c} | {n} |\n"

    if important_files:
        md += f"""
## ⭐ 重要文件

| 路径 | 类型 | 大小 | 最后修改 | 说明 |
|:---|:---|:---|:---|:---|
"""
        for f in important_files:
            md += f"| `{f['path']}` | {f['type']} | {f['size_human']} | {f['modified']} | {f['description']} |\n"

    return md


def generate_json_index(files, total_size):
    """生成 FILE_INDEX.json"""
    return {
        'generated_at': datetime.now().isoformat(),
        'total_files': len(files),
        'total_size_bytes': total_size,
        'total_size_human': format_size(total_size),
        'files': files
    }


def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/.hermes')
    output_dir = None

    # 解析参数
    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    if not os.path.isdir(root_dir):
        print(f"❌ 目录不存在: {root_dir}")
        sys.exit(1)

    print(f"📁 扫描目录: {root_dir}")
    files, total_size = scan_directory(root_dir)
    print(f"✅ 找到 {len(files)} 个文件，总大小 {format_size(total_size)}")

    # 生成 FILE_INDEX.md
    md_content = generate_markdown_index(files, total_size, root_dir)
    md_path = os.path.join(output_dir or root_dir, 'FILE_INDEX.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"📝 已生成: {md_path}")

    # 生成 FILE_INDEX.json
    json_content = generate_json_index(files, total_size)
    json_path = os.path.join(output_dir or root_dir, 'FILE_INDEX.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, indent=2, ensure_ascii=False)
    print(f"📊 已生成: {json_path}")

    print(f"\n✅ 索引生成完成！")


if __name__ == '__main__':
    main()
