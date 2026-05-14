# 四种工作流集成 project-state-machine 详细指南

> 此文是所有技能的集成参考。跨技能变更必须保证 all-or-nothing。

---

## 1. sdd-workflow 集成

### 集成点

| 位置 | 操作 | 门禁 |
|:-----|:------|:------|
| 每次 `spec-state.py` 命令前 | `project-state.py verify` | exit 1 阻断 |
| 每次 `spec-state.py` 命令后 | `project-state.py sync` | 自动纠偏 |
| 开发前强制流程 Step 2 | `project-state.py status` | 信息展示 |

### 添加的铁律

```
铁律: 每次 Spec 状态变更后必须同步 project-state.yaml
  → python3 scripts/project-state.py sync
```

---

## 2. generic-dev-workflow 集成

### 集成点

Step 7（提交与对齐）中添加新子步骤：

```text
7.4 项目状态同步 (project-state-machine skill)
  → cd <project-dir>
  → python3 scripts/project-state.py sync
  → python3 scripts/project-state.py verify
7.5 Git 提交
```

### 添加的铁律

```
铁律: 每次开发完成后同步 project-state.yaml
  后果: 状态机与开发实际脱节 (project-state-machine skill)
```

---

## 3. generic-qa-workflow 集成

### 集成点

L4（发布门禁）中添加步骤 5：

```text
# === 5. 项目状态一致性 ===
echo "=== State ==="
python3 scripts/project-state.py verify 2>/dev/null || echo "⚠️  project-state.py not available (optional gate)"
```

### 阻断条件

如果 `project-state.py` 存在且 verify 失败 → 阻断发布。

---

## 4. project-startup-workflow 集成

### 集成点

新增 Phase 4.5:

```text
### Phase 4.5: 状态机初始化 (project-state-machine skill)

当项目已有 SDD 文档结构后，初始化统一状态机：

1. 复制模板：
   cp ~/.hermes/skills/dogfood/project-state-machine/templates/project-state.yaml docs/
2. 安装脚本：
   cp ~/.hermes/skills/dogfood/project-state-machine/scripts/project-state.py scripts/
3. 编辑 docs/project-state.yaml → 填入项目信息
4. 同步文档状态：
   python3 scripts/project-state.py sync
5. 验证：
   python3 scripts/project-state.py verify
```

### 检查清单新增

```text
Phase 4.5: 状态机
  [ ] docs/project-state.yaml 已创建并配置
  [ ] 所有实体状态已同步
  [ ] python3 scripts/project-state.py verify ✅
```
