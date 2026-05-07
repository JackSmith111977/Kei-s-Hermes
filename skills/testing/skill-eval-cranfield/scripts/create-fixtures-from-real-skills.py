#!/usr/bin/env python3
"""
从真实 SKILL.md 库批量提取 YAML frontmatter 并创建测试 Fixture。

用法:
    python3 scripts/create-fixtures-from-real-skills.py

输出:
    tests/fixtures/skills/      — 按类别组织的 SKILL.md（用于 SkillAdvisor 加载）
    tests/fixtures/skills_yaml/ — 独立 YAML 文件 + _all_yamls.json（用于查询生成）
"""
import os, yaml, glob, json

SKILLS_SRC = os.path.expanduser("~/.hermes/skills")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "skills")
YAML_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "skills_yaml")

def main():
    skill_files = sorted(glob.glob(os.path.join(SKILLS_SRC, "**/SKILL.md"), recursive=True))
    print(f"📊 源技能库: {len(skill_files)} 个 SKILL.md")

    os.makedirs(FIXTURES_DIR, exist_ok=True)
    os.makedirs(YAML_DIR, exist_ok=True)

    has_yaml = 0
    all_yamls = []

    for sf in skill_files:
        rel = os.path.relpath(sf, SKILLS_SRC)
        parts = rel.split(os.sep)
        cat = parts[0]
        name = parts[-2]

        with open(sf) as f:
            content = f.read()

        lines = content.split("\n")
        if not lines or lines[0].strip() != "---":
            continue  # 跳过无 frontmatter 的 skill

        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if not end:
            continue

        yaml_text = "\n".join(lines[1:end])
        ydata = yaml.safe_load(yaml_text)
        if not isinstance(ydata, dict):
            continue

        has_yaml += 1
        ydata["_source_path"] = rel
        ydata["_source_name"] = name
        all_yamls.append(ydata)

        # 保存 SKILL.md fixture（类别名中 '/' 用 '__' 替代）
        cat_clean = "/".join(parts[:-1]).replace(" ", "-")
        fixture_dir = os.path.join(FIXTURES_DIR, cat_clean, name)
        os.makedirs(fixture_dir, exist_ok=True)
        with open(os.path.join(fixture_dir, "SKILL.md"), "w") as f:
            f.write("---\n")
            yaml.dump(
                {k: v for k, v in ydata.items() if not k.startswith("_")},
                f, allow_unicode=True, default_flow_style=False, sort_keys=False,
            )
            f.write("---\n")
            f.write(f"# {name}\n\n{ydata.get('description', '')}\n")

        # 保存独立 YAML
        safe_name = rel.replace("/", "__").replace(".md", "")
        with open(os.path.join(YAML_DIR, f"{safe_name}.yaml"), "w") as f:
            yaml.dump(ydata, f, allow_unicode=True, default_flow_style=False)

    # 保存合并 JSON
    with open(os.path.join(YAML_DIR, "_all_yamls.json"), "w") as f:
        json.dump(all_yamls, f, ensure_ascii=False, default=str, indent=2)

    print(f"✅ 有 YAML: {has_yaml}")
    print(f"📁 Fixtures: {FIXTURES_DIR} ({len(all_yamls)} skills)")
    print(f"📁 YAML 源: {YAML_DIR}")
    print(f"\n💡 在测试中验证真实数据:")
    print(f'   assert len(advisor.indexer.get_skills()) >= 300,')

if __name__ == "__main__":
    main()
