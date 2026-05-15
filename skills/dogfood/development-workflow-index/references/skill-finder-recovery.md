# skill_finder.py 恢复指南

> 场景: pre_flight 通过后，skill_finder.py 无法运行，报 `NameError: name 'script_name' is not defined`
> 根因: 核心脚本被意外覆盖为 91 字节 stub 文件

## 检测

```bash
# 检查文件大小
wc -c ~/.hermes/skills/learning-workflow/scripts/skill_finder.py
# 若输出 "91 /path/to/skill_finder.py" → 已 stub

# 查看文件头
head -3 ~/.hermes/skills/learning-workflow/scripts/skill_finder.py
# 正常文件 > 2000 字节，stub 内容只剩 print(f'{script_name} OK')
```

## 恢复

从任意未损坏的 profile 备份复制：

```bash
# 方法 1: 从 research profile 恢复（推荐）
cp ~/.hermes/profiles/research/skills/learning-workflow/scripts/skill_finder.py \
   ~/.hermes/skills/learning-workflow/scripts/skill_finder.py

# 方法 2: 从 experiment profile 恢复（备选）
cp ~/.hermes/profiles/experiment/skills/learning-workflow/scripts/skill_finder.py \
   ~/.hermes/skills/learning-workflow/scripts/skill_finder.py
```

恢复后验证：

```bash
python3 ~/.hermes/skills/learning-workflow/scripts/skill_finder.py "test"
# 应输出技能推荐
```

## 预防

- 不要用 `write_file` / `patch` 直接修改 `~/.hermes/skills/learning-workflow/scripts/` 下的文件
- 若必须修改，先 `cp` 备份，修改后 `wc -c` 确认文件大小正常
- 核心脚本应 git commit 到仓库，以便 `git checkout` 恢复
