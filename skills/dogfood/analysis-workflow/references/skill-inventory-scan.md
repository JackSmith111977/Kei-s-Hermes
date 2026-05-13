# Hermes/Agent Skill 库存扫描方法论

> **适用场景**: 统计任意 Agent 平台（Hermes / OpenCode / Claude Code）的 skill 总量、分布、归属分类
> **来源**: cap-pack EPIC-003 规划 (2026-05-13) — 发现 skill 目录可能有递归嵌套
> **核心教训**: `ls -d` 只数顶层目录，漏掉了深层嵌套的子 skill（最初只数到 85，实际 351）

---

## 一、扫描命令

### 正确的扫描方式（递归）

```bash
# 1. 真实 skill 总数（每个 SKILL.md = 一个 skill）
find ~/.hermes/skills/ -name "SKILL.md" -type f | wc -l

# 2. 按顶层分类目录分组统计
for d in ~/.hermes/skills/*/; do
  name=$(basename "$d")
  count=$(find "$d" -name "SKILL.md" -type f | wc -l)
  echo "$name: $count"
done | sort -t: -k2 -rn

# 3. 检查深层嵌套结构
for d in ~/.hermes/skills/*/; do
  name=$(basename "$d")
  subs=$(find "$d" -mindepth 1 -maxdepth 1 -type d | wc -l)
  if [ "$subs" -gt 5 ]; then
    echo "  📂 $name: $total skills (${subs} subcategories — has nested structure!)"
  fi
done
```

### ⚠️ 常见陷阱

| 错误方式 | 结果 | 根因 |
|:---------|:-----|:------|
| `ls -d skills/*/ | wc -l` | 只数到 85（实为 351） | 只数顶层目录，漏掉深层嵌套的子 skill（如 dogfood 含 20+，bmad-method 曾含 153） |
| `find skills/ -type d | wc -l` | 过多 | 数的是目录数，不是 SKILL.md 数 |
| `skills_list` API | 可能不完整 | API 可能不暴露内部子 skill |

**经验法则**: **永远用 `find -name "SKILL.md" -type f` 统计 skill 数量**。这是唯一可靠的计数方式。

---

## 二、分布分析

### 查看哪些分类占大头

```bash
# 按 skill 数量排序，只看占比 > 5% 的大头
total=$(find ~/.hermes/skills/ -name "SKILL.md" -type f | wc -l)
for d in ~/.hermes/skills/*/; do
  name=$(basename "$d")
  count=$(find "$d" -name "SKILL.md" -type f | wc -l)
  pct=$(awk "BEGIN {printf \"%.1f\", $count/$total*100}")
  if [ "$(awk "BEGIN {print ($count/$total > 0.05)}")" = "1" ]; then
    echo "  🥇 $name: $count ($pct%)"
  fi
done | sort -t: -k2 -rn
```

### 识别单 skill 目录（可能为安装产物）

```bash
for d in ~/.hermes/skills/*/; do
  count=$(find "$d" -name "SKILL.md" -type f | wc -l)
  if [ "$count" -eq 1 ] && [ -z "$(find "$d" -mindepth 1 -maxdepth 1 -type d)" ]; then
    echo "  单 skill: $(basename "$d")"
  fi
done
```

---

## 三、映射到分类体系

当需要将 Hermes skill 映射到自定义模块体系（如 cap-pack 的 18/20 模块）时：

```bash
# 按模块分组的手工映射表
# 格式: module_name: directory1,directory2,...
cat <<'MAPPING' | while IFS=: read module dirs; do
  total=0
  IFS=',' read -ra ADDR <<< "$dirs"
  for dir in "${ADDR[@]}"; do
    d="$HOME/.hermes/skills/$dir"
    [ -d "$d" ] && count=$(find "$d" -name "SKILL.md" -type f | wc -l) && total=$((total+count))
  done
  echo "$module: ~$total skills"
MAPPING
```

---

## 四、与 cap-pack 扫描结合

cap-pack 项目中的 skill 扫描场景：

```bash
# 1. 扫描已提取 pack 与实际 skill 的差距
cd ~/projects/hermes-cap-pack
for pack in packs/*/; do
  name=$(basename "$pack")
  if [ -f "$pack/cap-pack.yaml" ]; then
    declared=$(grep -c "^  - id:" "$pack/cap-pack.yaml")
    actual=$(find "$pack/SKILLS" -name "SKILL.md" -type f 2>/dev/null | wc -l)
    echo "$name: declared=$declared actual=$actual"
  fi
done

# 2. 识别未打包的 Hermes skill
hermes_skills=$(mktemp)
find ~/.hermes/skills/ -name "SKILL.md" -type f | sed 's/.*\/skills\/\(.*\)\/SKILL.md/\1/' > "$hermes_skills"
# 与已提取的对比...
```
