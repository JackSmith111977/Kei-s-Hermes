# install-pack.py v2.0 — 多 Agent CLI 实战记录

> **2026-05-14 新增** | 基于 SPEC-1-5 (STORY-1-5-4) 实现

## 背景

install-pack.py v1.0 仅支持 Hermes 目标，直接使用 `shutil.copytree` 操作文件系统。
v2.0 重构为适配器模式，支持 `--target hermes|opencode|auto`。

## 架构决策记录

### ADR-001: Adapter Registry 而非类继承

**决策**: 用 dict 注册表（`ADAPTERS = {"hermes": HermesAdapter, ...}`）而非基类继承。

**理由**:
- 注册表可动态扩展（无需修改 CLI 代码即可添加新 Agent）
- 每个适配器独立实现 `AgentAdapter` Protocol（duck typing）
- `detect_available()` 通过注册表统一遍历

### ADR-002: 兼容旧用法优先

**决策**: 同时支持 `install-pack.py <pack-dir>`（旧用法）和 `install-pack.py status`（新子命令）。

**理由**: 不破坏已有工作流。通过检查 `sys.argv[1]` 是否属于子命令集合来判断。

### ADR-003: install() API 必须统一

**决策**: 所有适配器的 `install()` 签名必须完全一致。

```python
def install(self, pack: CapPack, dry_run: bool = False, skip_deps: bool = False) -> AdapterResult:
```

**经验教训**: OpenCodeAdapter 最初缺少 `skip_deps` 参数，`--target auto` 调用时报 `TypeError: unexpected keyword argument 'skip_deps'`。

## 关键文件

| 文件 | 说明 |
|:-----|:------|
| `scripts/install-pack.py` | CLI 主入口 (v2.0) |
| `scripts/adapters/__init__.py` | 适配器包 |
| `scripts/adapters/hermes.py` | HermesAdapter — 含完整验证门禁 |
| `scripts/adapters/opencode.py` | OpenCodeAdapter — 含格式转换 |
| `scripts/tests/test_hermes_adapter.py` | `TestMultiAgentInstall` 测试类 |

## 测试覆盖

| 测试 | 验证点 |
|:-----|:--------|
| `test_hermes_target` | `--target hermes` 安装到模拟 ~/.hermes/ |
| `test_opencode_format_conversion` | OpenCode 格式转换（frontmatter 字段映射） |
| `test_opencode_uninstall` | OpenCode 卸载不崩溃 |
| `test_cli_auto_detection` | `detect_available()` 能正确检测 |
