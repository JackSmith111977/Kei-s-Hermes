# README 对齐验证与 CI 集成模式

> 来源: hermes-cap-pack 项目实战 (2026-05-14)
> 适用于: 任何需要自动化验证 README 模板符合性的项目

## 问题

AI 友好 README 需要保持与项目实际状态一致（版本号、测试数、功能列表等），但手动维护容易漂移。需要一个可编程的验证器 + CI 门禁来保证 README 始终对齐。

## 解决方案：验证器三层架构

### 层次设计

```
validate-readme.py
├── P0 阻塞 (blocking)  → 版本号、测试数、仓库地址等 MUST
├── P1 警告 (warning)   → CLI 表格、FAQ、前置条件等 SHOULD
└── P2 格式 (info)      → 行长度、编号格式等 COULD
```

### 规则设计模式

每条规则是四元组：`(名称, 检查类型, 模式/函数, 严重度)`

| 检查类型 | 模式/函数示例 | 用途 |
|:---------|:--------------|:------|
| `contains` | `"# 一、项目身份"` | 精确文本匹配，检查章节是否存在 |
| `regex` | `r"\*\*版本\*\*.*\`[\d\.]+\`"` | 正则匹配，适应格式变化 |
| `custom` | `check_version_consistency` | 自定义函数，跨文件比对 |

### 自定义检查函数模式

```python
def check_version_consistency(content: str, readme_path: Path) -> list[str]:
    """检查 README 版本号与 pyproject.toml 一致"""
    # 从 pyproject.toml 读取版本
    # 从 README 用正则提取版本
    # 比较，返回不一致列表
```

### 退出码约定

| 退出码 | 含义 | CI 行为 |
|:------:|:-----|:---------|
| 0 | 全部通过 | ✅ 继续 |
| 1 | 有警告通过 | ✅ 继续（non-blocking） |
| 2 | 有阻塞失败 | ❌ 阻断 |

## CI 集成模式

在 `.github/workflows/ci.yml` 的 lint job 末尾添加：

```yaml
- name: 📖 README alignment check
  run: python3 scripts/validate-readme.py
```

**为什么放在 lint job 而不是独立 job**：README 检查轻量、无外部依赖，与 Python 语法检查属于同一级别。

## 模板文件结构

```
项目根目录/
├── README.md                          # 主 README（模板实例）
└── docs/templates/README-template.md  # AI 友好 README 模板
```

### 模板的核心章节

```
一、项目身份        → 元信息表格
二、快速安装        → 前置条件 + 多路径安装 + 验证
三、核心能力        → 模块/功能列表
四、CLI 参考        → 三列命令表格 + 验证
五、高级用法/配置   → 可脚本化的配置项
六、FAQ/排错        → 三列排错表
七、API/编程使用     → 代码示例
八、开发指南        → 测试 + 目录结构
九、贡献指南        → 贡献方式
十、相关项目        → 关联项目
模板元信息           → template 版本追踪
```

## 已知陷阱

### 1. 版本号漂移

`pyproject.toml` 版本更新后 README 版本号未同步。  
**解法**: `validate-readme.py` 的 `check_version_consistency` 自定义检查 + `--fix` 自动修复。

### 2. Git 提交时README未同步

功能变更后 README 未更新对应的 CLI 命令示例或配置说明。  
**解法**: CI 中 `project-state.py verify` 和 `validate-readme.py` 并行检查，功能变更（新 Story/Spec）如果新增了 CLI 命令但 README 没更新，会被 CI 发现。

### 3. 模板符合率幻觉

100% 符合验证规则 ≠ README 写得好。  
**解法**: 验证规则只覆盖结构层（该有的都有），内容质量靠人工 review。建议在 REVIEW 门禁中增加 README 审查步骤。

## 实战参考

完整实现见 hermes-cap-pack 项目：
- `scripts/validate-readme.py` — 18 项检查，含版本一致性 + 超长行检测
- `.github/workflows/ci.yml` — CI 集成步骤
- `docs/templates/README-template.md` — 可复用的 AI 友好 README 模板
