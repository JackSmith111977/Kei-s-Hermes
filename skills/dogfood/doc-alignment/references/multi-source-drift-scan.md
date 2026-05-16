# 多源漂移扫描实战记录

> **来源**: 2026-05-16 hermes-cap-pack v1.0.0 发布前审计
> **涉及的 skill**: doc-alignment §Phase 2 (v3.3+)

## 发现的多源漂移汇总

| # | 数据源漂移 | 严重度 | 发现方式 | 修复 |
|:--|:----------|:------:|:---------|:-----|
| 1 | EPIC-006.md 说 `status: draft` 但 12/12 Stories 已实现 | 🔴 阻塞 | EPIC doc header vs 实际代码 | 更新到 `implemented` |
| 2 | project-state.yaml 说 EPIC-005 completed_count=14，实际 15 个 Story | 🔴 阻塞 | YAML 计数 vs `find stories/` 文件数 | 修正为 15 |
| 3 | README.md 说 `141 ✅` 测试，实际 `202 passed` | 🔴 阻塞 | `pytest --collect-only` vs `grep '测试' README.md` | 6 处引用全部更新 |
| 4 | project-report.json 说 `141 ✅` 测试 | 🔴 阻塞 | JSON 字段 vs 实际 pytest 结果 | 更新到 202 |
| 5 | CHANGELOG.md 只到 v0.7.1，实际版本 v0.9.1 | 🟡 警告 | CHANGELOG 头部 vs `git log --oneline` | 补写 3 个缺失版本 + v1.0.0 |
| 6 | PROJECT-PANORAMA.html 的 KPI+测试表+文档表全部过时 | 🟡 警告 | HTML KPI 值 vs 实际数据 | 更新 10+ 处 HTML 元素 |
| 7 | pyproject.toml 版本 0.9.1 → 需 bump 到 1.0.0 | 🟢 | 语义版本映射规则 | major bump |

## 修复策略

### 按数据源分层修复

```text
第一层（数据源准确度）:
  project-state.yaml → EPIC-005 completed_count: 14→15
  project-state.yaml → EPIC-006 state: draft→implemented

第二层（文档准确性）:
  docs/EPIC-005.md: 补完 SDD 流程行 + 完成情况行
  docs/EPIC-006.md: status draft→implemented, 补完成行
  CHANGELOG.md: 补全 0.8.0/0.9.0/0.9.1/1.0.0

第三层（展示层同步）:
  README.md: 版本号 + 测试数 + schema 版本
  PROJECT-PANORAMA.html: KPI 卡片 + 测试表 + 文档统计 + Footer
  project-report.json: version + 测试数
  pyproject.toml: version + last_bump
```

### 批量同步命令

```bash
# 快速版本号批量同步
find . -maxdepth 2 \( -name "README.md" -o -name "*.html" -o -name "project-report.json" \) \
  | xargs grep -l "0.9.1" 2>/dev/null \
  | xargs sed -i 's/0.9.1/1.0.0/g'

# 更新团队标签
grep -r "EPIC-005 🆕" . --include="*.md" --include="*.html" -l 2>/dev/null \
  | xargs sed -i 's/EPIC-005 🆕/EPIC-005+006 🆕/g'
```

## 陷阱总结

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 用 `replace_all=True` 替换测试数 | 误伤其他 KPI 卡片的值（17→202, 53→202） | 建唯一匹配上下文 `141 total · 全绿 ✅`，而非裸 `141` |
| 忽略非代码文件（CHANGELOG, HTML, README）的版本引用 | 版本号不一致持续到下次发布才发现 | 运行「六源交叉审计」全部 6 个数据源 |
| EPIC 文档的 `status` 和 project-state.yaml 各自维护 | 两个系统状态漂移 | 发布前逐 EPIC 对照检查：`grep "status:"` vs `yaml['state']` |

## 参考

- doc-alignment §Phase 2 — 发布前多源漂移检测协议
- doc-alignment §实战案例 — cap-pack v1.0.0 发布记录
