# Skill 自动关联与合并 — 集成指南

## 如何集成到学习流程

### 在 learning-workflow 的 STEP 6 后添加：

```bash
# 第 7 步：自动关联新创建的 skill
if [ -n "$NEW_SKILL_NAME" ]; then
    echo "🔗 自动关联 skill: $NEW_SKILL_NAME"
    python3 ~/.hermes/scripts/skill-auto-link.py auto-link "$NEW_SKILL_NAME"
fi
```

### 在 skill-creator 的创建流程后添加：

```python
# skill 创建完成后，自动执行关联
import subprocess
result = subprocess.run(
    ["python3", os.path.expanduser("~/.hermes/scripts/skill-auto-link.py"),
     "auto-link", skill_name],
    capture_output=True, text=True
)
print(result.stdout)
```

### 定时全量扫描（可选）

```bash
# 每周日 0 点执行全量扫描
0 0 * * 0 python3 ~/.hermes/scripts/skill-auto-link.py full-scan >> ~/.hermes/logs/auto-link.log 2>&1
```

## 命令速查

| 命令 | 用途 | 
|:----|:-----|
| `skill-auto-link.py auto-link <name>` | 为新 skill 自动关联 |
| `skill-auto-link.py auto-link <name> --dry-run` | 预览关联建议 |
| `skill-auto-link.py merge-detect [threshold=70]` | 检测重合 skill |
| `skill-auto-link.py full-scan` | 全量扫描 |
| `skill-auto-link.py report` | 生成关联报告 |
| `skill-auto-link.py score <a> <b>` | 查两个 skill 的关联度 |
