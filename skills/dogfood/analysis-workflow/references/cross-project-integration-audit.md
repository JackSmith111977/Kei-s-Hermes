# 跨项目集成审计方法论

> 2026-05-15 从 SRA 自动注入审计中提炼的模式。适用场景：验证项目 A 是否真的与项目 B 集成了。

## 适用场景

| 场景 | 示例 |
|:-----|:------|
| 文档称「A 已集成到 B」但怀疑未实现 | SRA 文档称自动注入到 Hermes |
| EPIC AC 涉及外部项目 | 「Hermes pre_tool_call hook 集成」 |
| 安装/集成脚本存在但不确定是否运行过 | `install-hermes-integration.sh` |
| 架构图显示连接但代码无消费者 | force.py → Hermes hook |

## 五步审计法

### Step 1: 库存清点 — 确认「宣称的」集成链

从文档中提取完整的集成调用链：

```text
[用户消息]
    ↓
[宣称: run_agent.py 中 _query_sra_context() 被调用]
    ↓
[宣称: HTTP POST :8536/recommend]
    ↓
[SRA Daemon 处理]
    ↓
[宣称: [SRA] 上下文注入到消息前]
```

**产出**: 完整的调用链流程图，每个节点标注「宣称的位置」。贴到文件中，不要留在对话上下文中。

### Step 2: 代码存在性检查 — 检查每一环的代码

对 Step 1 的每个节点，在对应代码库中搜索：

```bash
# 搜索关键函数/类/端点
grep -rn "_query_sra_context" ~/.hermes/hermes-agent/ --include="*.py"
grep -rn "sra\|SRA\|recommend\|8536" ~/.hermes/hermes-agent/run_agent.py
grep -rn "pre_tool_call.*sra\|sra.*validate" ~/.hermes/hermes-agent/model_tools.py

# 搜索插件目录
ls ~/.hermes/hermes-agent/plugins/sra-guard/ 2>/dev/null

# 搜索配置文件中的集成引用
grep -rn "sra\|SRA\|8536" ~/.hermes/config.yaml
```

**判断标准**:
| 结果 | 含义 |
|:-----|:------|
| 函数/类存在 | ✅ 代码存在 |
| 有匹配但仅注释/字符串 | ⚠️ 可能只是提及，非实际使用 |
| 无匹配 | ❌ 代码从未存在 |
| 只在文档/补丁文件中存在 | ❌ 设计了但未执行（没打补丁） |

### Step 3: 调用链追踪 — 检查消费者是否存在

对于定义了接口/端点的模块，检查是否有消费者：

```bash
# 对于 force.py 定义了 injection_points
# 搜索调用 force_manager 的代码
grep -rn "force_manager\|is_injection_point_active" ~/projects/sra/ --include="*.py"

# 对于 daemon.py 定义了 /validate 端点
# 搜索调用 /validate 的代码
grep -rn "/validate\|\"validate\"\|validate_tool_call" ~/.hermes/hermes-agent/ --include="*.py"
```

**关键问题**: 如果 A 定义了接口但 B 从未调用 → A 和 B 之间不存在集成。这是最常见的「幻影集成」模式。

### Step 4: 安装/部署检验 — 检查集成是否实际被执行过

```bash
# 检查备份文件（补丁在安装前会备份原始文件）
ls -la ~/.hermes/hermes-agent/run_agent.py.sra-backup 2>/dev/null

# 检查安装日志
grep -i "sra.*install\|install.*sra\|hermes.*integration" ~/.hermes/logs/agent.log 2>/dev/null

# 检查是否为 print-only 命令
grep -A5 "def cmd_install" ~/projects/sra/skill_advisor/cli.py
# 如果看到 print("步骤 1...") 而不是实际文件操作 → 伪安装
```

### Step 5: AC 审计 — 检查 Epic/Story 验收标准的实际完成情况

```bash
# 1. 提取所有涉及外部项目的 AC
grep -n "Hermes.*\|hermes.*\|plugin.*\|agent.*" docs/EPIC-*.md | grep '\[x\]'

# 2. 逐条在外部项目中验证代码存在性
# 对于「Hermes pre_tool_call hook 集成」:
# 验证: ls ~/.hermes/hermes-agent/plugins/sra-guard/ 2>/dev/null
# 验证: grep -rn "sra_guard\|SRA" ~/.hermes/hermes-agent/hermes_cli/ --include="*.py"

# 3. 标记实际完成状态
echo "=== AC 实际完成状态（跨项目验证后）==="
python3 scripts/ac-audit.py dashboard docs/EPIC-*.md
# 如果 ac-audit.py 报告 100% 但 Step 2 中有缺失 → AC 审计工具本身有盲点
```

## 三类文档漂移

| 类型 | 特征 | 发现方法 | 修复方向 |
|:-----|:------|:---------|:---------|
| **幻影功能** | 文档描述的代码从未存在过 | Step 2: 代码存在性检查 | 删除文档或创建代码 |
| **幻影集成** | 文档称 A↔B 已连接，实际无消费者 | Step 3: 调用链追踪 | 用 B 侧 hook/plugin 系统替代 patch |
| **幻影 AC** | AC 标记 ✅ 但代码未实现 | Step 5: AC 外延验证 | 增强 AC 审计为双向检查 |

## 实战模板：跨项目集成快速诊断

```bash
#!/bin/bash
# 快速诊断项目 A 到项目 B 的集成状态
# 用法: bash cross-project-audit.sh <project_a_dir> <project_b_dir> <integration_keyword>

PROJECT_A="$1"
PROJECT_B="$2"
KW="${3:-sra}"

echo "=== 跨项目集成诊断: $KW ==="
echo ""

echo "1️⃣  A 侧：查找声称集成的代码"
grep -rn "$KW" "$PROJECT_A/docs/" --include="*.md" | grep -i 'integrat\|hook\|plugin\|auto\|inject' | head -10

echo ""
echo "2️⃣  B 侧：查找 $KW 相关代码"
grep -rn "$KW" "$PROJECT_B/" --include="*.py" 2>/dev/null | grep -v __pycache__ | grep -v ".pyc" | head -20

echo ""
echo "3️⃣  B 侧：查找 $KW 相关配置"
grep -rn "$KW" "$PROJECT_B/" -name "*.yaml" -o -name "*.yml" -o -name "*.json" 2>/dev/null | head -10

echo ""
echo "4️⃣  安装状态检查"
# 补丁备份文件
find "$PROJECT_B" -name "*.sra-backup" -o -name "*.bak" 2>/dev/null | head -5
# 插件目录
find "$PROJECT_B" -path "*/plugins/$KW*" -type d 2>/dev/null | head -5

echo ""
echo "=== 诊断结论 ==="
echo "如果在 A 侧找到文档但 B 侧无代码 → 幻影集成"
echo "如果在 A 侧找到文档且在 B 侧有代码 → 集成已实现"
echo "如果在 A 侧找到文档且 B 侧只有配置引用 → 部分集成（可能未生效）"
```

## 与 analysis-workflow 其他模式的关系

| 模式 | 关系 |
|:-----|:------|
| §2 分块策略 | Step 1-5 的每个步骤应独立处理，不混在一个上下文中 |
| §3 Map-Reduce | 多项目审计时，每项目用独立子任务并行检查 |
| §8 并行子代理审计 | 复杂跨项目集成可用 4 层并行（架构/代码/测试/文档）分别扫描 |
| skill-inventory-scan | 检查 B 项目是否实际加载了 A 项目的 skill |
