# 知识管线升级验证方法论

> 每次升级 knowledge 相关 skill 后，按此 5 阶段流程验证。
> 已验证：2026-05-09 knowledge-routing v3.1→v3.2 + 4 skill 配套升级

## 五阶段验证流程

### Phase 1: 管线健康扫描

```bash
# 1. 版本一致性 — 确认所有关联 skill 版本号与升级日期一致
for f in ~/.hermes/skills/*/SKILL.md ~/.hermes/skills/dogfood/*/SKILL.md; do
  name=$(basename $(dirname $f))
  ver=$(grep "^version:" "$f" 2>/dev/null | head -1 | tr -d ' ')
  mtime=$(stat -c "%y" "$f" | cut -d. -f1)
  echo "$name → $ver (${mtime%% *})"
done

# 2. 脚本可用性 — 新引入的脚本必须跑 --help 验证
python3 ~/.hermes/scripts/knowledge-ingest.py --help

# 3. L2/L3 存量统计 — 验证写入目标可用
find ~/.hermes/experiences/active -name "*.md" | wc -l
for t in concepts entities summaries analyses; do
  find ~/.hermes/brain/wiki/$t -name "*.md" 2>/dev/null | wc -l
done
```

### Phase 2: 深度分析（交叉引用 + 缺口发现）

检查清单：
- [ ] 每个 skill 是否引用了 `knowledge-ingest.py` 或 `knowledge-routing`？
- [ ] 交叉引用版本号是否一致？
- [ ] 管线各阶段是否闭环？（学习→路由→执行→Review→生命周期）
- [ ] 是否有明显功能缺口？

### Phase 3: 路由判断（走 knowledge-routing 决策树）

五维决策树：
1. 知识类型（命题 vs 程序）
2. 复用频率（1次 vs 2-3次 vs 3次+）
3. 知识深度（浅→L2 / 深→L3）
4. 抽象层次（concepts/entities/summaries/analyses）
5. 环境适配（Memory 容量、重复页面检查）

### Phase 4: 脚本执行（knowledge-ingest.py）

```bash
# ⚠️ 内容必须用文件传，不支持 heredoc！
echo "..." > /tmp/content.md
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type experience --title "标题" \
  --content @/tmp/content.md \
  --reusability high --confidence 4
```

### Phase 5: 验证索引

```bash
# 验证文件存在
cat ~/.hermes/experiences/active/exp-{date}-*.md | head -5

# 验证索引更新
tail -5 ~/.hermes/experiences/index.md
tail -5 ~/.hermes/brain/index.md
tail -3 ~/.hermes/brain/log.md
```

## 评分体系

| 维度 | 权重 | 说明 |
|:----|:----:|:-----|
| 版本一致性 | 20 | 所有关联 skill 同日期更新 |
| 脚本可用性 | 15 | 新脚本功能正常 |
| L2 积累 | 15 | 经验文件完整 |
| L3 丰富度 | 15 | Brain 页面完整 |
| 交叉引用 | 15 | 各 skill 互相引用正确 |
| 管线闭环 | 10 | 学习→路由→执行→Review→生命周期完整 |
| **总分** | **90** | **≥80优秀 / ≥60良好 / ≥40中等** |

## 常见缺口模式

| 模式 | 严重度 | 检测方法 |
|:----|:------:|:---------|
| L2→L3 自动升级缺失 | 🟡 中 | auto-detect 只扫描 learning/reviews/，不扫描 experiences/ |
| 间隔复习未注册 | 🟡 中 | learning-workflow 提及 1/7/30 天但 cron 未注册 |
| KNOWLEDGE_INDEX 未更新 | 🟢 低 | 检查 KNOWLEDGE_INDEX.md 尾部是否有新条目 |
| 文件名含中文字符 | 🟢 低 | slug 含中文可能影响跨平台兼容性 |

---

*建立: 2026-05-09 · 对应 knowledge-routing v3.2 验证*
