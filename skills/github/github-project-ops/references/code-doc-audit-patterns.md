# 代码-文档一致性审计模式库

> **适用场景**：当需要系统性审计项目代码与文档的一致性（发布前检查、质量审计、代码Review前自检）时使用。
> **核心原则**：不要凭记忆判断文档是否准确——逐项对比代码和文档的原始数据。
> **经验来源**：SRA Agent 项目 v1.1.0 发布前深度审计实战。

---

## 目录

- [模式 A：CLI 命令表审计](#模式-acli-命令表审计)
- [模式 B：API 端点审计](#模式-bapi-端点审计)
- [模式 C：算法参数审计](#模式-c算法参数审计)
- [模式 D：版本号一致性扫描](#模式-d版本号一致性扫描)
- [模式 E：项目结构图审计](#模式-e项目结构图审计)
- [报告模板](#报告模板)

---

## 模式 A：CLI 命令表审计

**目标**：找出 README 中 CLI 命令表的遗漏和错误。

### 第一步：从代码提取实际命令列表

```bash
# 方法 1：argparse 方式（add_parser）
grep -n "add_parser\|add_subparsers" cli.py | grep -v "^#" | grep -v "import"

# 方法 2：COMMANDS dict 方式
grep -A30 "COMMANDS\s*=" cli.py | grep '^\s*"'

# 方法 3：CLI docstring 方式
head -40 cli.py | grep "^#\|^\s*sra "

# 方法 4：help 函数输出
grep -A30 "def print_help\|def help" cli.py | grep "^\s*print\|^\s*  sra"
```

### 第二步：从 README 提取声称的命令列表

```bash
# 从表格提取
grep -A30 "^| 命令" README.md | grep -E "^\|.*\|" | grep -v "^| 命令\|^|---"
```

### 第三步：对比

| 结果 | 含义 | 严重度 |
|:-----|:------|:------:|
| 代码有，READ ME 无 | **遗漏** — README 需要补全 | 🟡 P1 |
| README 有，代码无 | **虚假声明** — 可能已删除的功能 | 🔴 P0 |
| help 中版本号与 pyproject.toml 不一致 | **版本号偏差** | 🟡 P1 |

**实战发现**（SRA 项目）：README 只列出 7 个命令，代码实际有 16 个，遗漏了 restart/attach/query/refresh/record/config/install/adapters/help。

---

## 模式 B：API 端点审计

**目标**：找出 API 文档中端点的遗漏和错误。

### 第一步：从服务器代码提取实际端点

```bash
# Flask/FastAPI
grep -n "route\|@app\.\|\.add_url_rule\|@router\.\|\.get\|\.post\|\.put\|\.delete" server.py | grep "def"

# Python 标准库 http.server
# 在 do_GET/do_POST 中查找 self.path 比较分支
grep -n "def do_GET\|def do_POST\|def do_PUT\|def do_DELETE" daemon.py
# 然后查看每个 handler 中的路径路由
grep -B1 -A5 "def do_GET\|def do_POST" daemon.py | grep -E "self\.path|endpoint|elif|if "
```

### 第二步：从 README 提取端点表

```bash
grep -A20 "^| 端点" README.md | grep -E "^\|.*\|" | grep -v "^| 端点\|^|---"
```

### 第三步：检查 HTTP 方法

确认 README 中标明的 HTTP 方法（GET/POST）与实际 handler 匹配：
- `do_GET` → GET 方法
- `do_POST` → POST 方法

### 典型发现

| 问题 | 示例 | 严重度 |
|:-----|:------|:------:|
| 文档声称存在但代码无 | README 有 `/targets` 但代码不存在 | 🔴 P0 |
| 文档未列出但代码存在 | 代码有 `/status`、`/record`、`/refresh` 但 README 无 | 🟡 P1 |
| HTTP 方法错误 | README 写 GET 但代码用 POST | 🔴 P0 |

---

## 模式 C：算法参数审计

**目标**：验证文档中声明的加权参数、阈值、常量是否与实际代码一致。

### 第一步：从代码提取关键常量

```bash
# 权重常量
grep -n "WEIGHT_\|_WEIGHT\|\bWEIGHT\b\|_THRESHOLD\|_FACTOR\|_LIMIT\|_BOOST\|_RATE" matcher.py advisor.py 2>/dev/null

# 硬编码阈值
grep -n "high_threshold\|medium_threshold\|threshold\|confidence\|if.*score.*>=\|if.*>=" daemon.py 2>/dev/null

# 默认值
grep -n "default\|DEFAULT\|_DEFAULT" config.py daemon.py 2>/dev/null

# 评分规则（查找常量定义）
grep -nE "^\s+(SCORE|MATCH|LEX|SEM|SCENE|CAT)\s*=" matcher.py 2>/dev/null
grep -nE "^\s+[A-Z_]{3,}\s*=\s*\d+" matcher.py 2>/dev/null
```

### 第二步：从设计文档提取声称的参数

```bash
grep -n "×\|%\|权重\|阈值\|threshold\|weight\|factor\|fator\|boost\|score\|得分" docs/DESIGN.md docs/RUNTIME.md 2>/dev/null
```

### 第三步：逐项对比并评分

| 对比结果 | 说明 | 严重度 |
|:---------|:------|:------:|
| 值完全一致 | ✅ 文档准确 | — |
| 值不一致 | ❌ 文档错误 | 🔴 P0 |
| 代码有但文档无 | ❌ 文档遗漏 | 🟡 P1 |
| 文档有但代码无 | ❌ 可能已删除或重构 | 🟡 P1 |

### 实战发现

- **SRA 项目**：四维匹配权重 `WEIGHT_LEXICAL=0.40, WEIGHT_SEMANTIC=0.25, WEIGHT_SCENE=0.20, WEIGHT_CATEGORY=0.15` 与 DESIGN.md 声明的 40%/25%/20%/15% 完全一致 ✅
- 但代码有 `SHORT_QUERY_BOOST=1.6`（短查询提升因子）和场景频率加分逻辑，DESIGN.md 未记录 ❌

---

## 模式 D：版本号一致性扫描

**目标**：找出项目中所有引用版本号的地方，确保一致性。

### 扫描命令

```bash
# 扫描所有包含版本号的文件
grep -rn "version\|v[0-9]\.[0-9]\.[0-9]" --include="*.py" --include="*.md" \
  --include="*.toml" --include="*.json" --include="*.yaml" --include="*.yml" . | \
  grep -v __pycache__ | grep -v ".git/" | grep -v "egg-info" | grep -v ".pytest_cache"
```

### 必须一致的 3 个位置

| 文件 | 行 | 检查 |
|:-----|:---|:------|
| `pyproject.toml` | `version = "X.Y.Z"` | ✅ 必须与 PyPI 一致 |
| `__init__.py` | `__version__ = "X.Y.Z"` | ✅ 必须与 pyproject.toml 一致 |
| `setup.py`（如有） | `version=` | ✅ 应从 __init__.py 读取 |

### 常见遗漏点

| 位置 | 示例 | 风险 |
|:-----|:------|:-----|
| `cli.py` help 输出 | `print("App v1.0")` | 硬编码旧版本号 |
| `cli.py` 默认值 | `stats.get('version', '1.0.0')` | 降级默认值未更新 |
| `SECURITY.md` 版本表 | `\| v1.0.x \| ✅ \|` | 缺少新版行 |
| `docs/` 文档中版本号 | 文档中引用的版本号 | 多处分散，容易遗漏 |
| CHANGELOG.md | 标题版本号 | 与新版本对齐 |

---

## 模式 E：项目结构图审计

**目标**：确保 README 或 docs/ 中的项目目录树与实际文件树一致。

### 第一步：生成实际文件树

```bash
find . -not -path "./.git/*" -not -path "*/__pycache__/*" \
  -not -path "*.egg-info/*" -not -path "./dist/*" \
  -not -path "./build/*" -not -path "./.pytest_cache/*" | sort
```

### 第二步：提取文档中的结构图

```bash
# 从 README 中提取代码块内的目录树
grep -A40 "^\`\`\`" README.md | grep -B1 "├──\|└──\|│"
```

### 第三步：逐行对比

| 检查项 | 说明 |
|:-------|:------|
| 遗漏的目录 | 实际新增了但结构图没更新（如 adapters/、runtime/） |
| 已删除的文件 | 结构图中有但实际已不存在的文件 |
| 顺序 | 建议按字母序排列，不要随意排序 |

### 实战发现

SRA 项目结构图可能遗漏了 `adapters/`、`runtime/` 等后来新增的模块目录。

---

## 报告模板

完成审计后，按以下模板输出报告：

```markdown
## 代码-文档一致性审计报告

### 🔴 P0（必须修复）

| # | 模式 | 问题 | 位置 |
|:-:|:----|:-----|:-----|
| 1 | B | 文档声称端点 X 但代码不存在 | README.md |
| 2 | C | 文档声明权重 Y 但代码实际为 Z | docs/DESIGN.md |

### 🟡 P1（建议修复）

| # | 模式 | 问题 | 位置 |
|:-:|:----|:-----|:-----|
| 1 | A | README 遗漏 N 个 CLI 命令 | README.md |
| 2 | D | help 输出版本号 vs 实际版本 | cli.py L359 |

### 🟢 P2（轻微）

| # | 模式 | 问题 | 位置 |
|:-:|:----|:-----|:-----|
| 1 | E | 结构图未包含新模块目录 | README.md |

### 一致性评分

| 维度 | 得分 | 说明 |
|:-----|:----:|:-----|
| 代码准确性 | X% | 代码质量、命名、结构 |
| 文档完整性 | X% | 是否覆盖所有功能 |
| 文档时效性 | X% | 是否反映最新代码 |
| 元数据一致性 | X% | 版本号/许可证/描述 |

**综合评分**：**X%** — 🟢/🟡/🔴（≥90/70-89/<70）
**结论**：{通过 / 修复后发布 / 禁止发布}
```
