# PyPI Trusted Publisher 配置与排错指南

> 2026-05-11 实战记录 — SRA Agent v1.4.0 发布失败调试

## 背景

SRA Agent 使用 GitHub Actions 的 **Trusted Publishing (OIDC)** 方式自动发布到 PyPI。当 push git tag `v1.4.0` 时，CI 触发 `release.yml` 中的 `publish-pypi` job，使用 `pypa/gh-action-pypi-publish@release/v1` 通过 OIDC 认证发布。

## 错误现象

```
❌ Trusted publishing exchange failure
invalid-publisher: valid token, but no corresponding publisher
sub: repo:JackSmith111977/Hermes-Skill-View:environment:pypi
```

GitHub Release（`github-release` job）成功，但 PyPI 发布失败。

## OIDC 原理

GitHub Actions 的 OIDC token 包含以下字段（由 PyPI 验证）：

| OIDC Claim | 来源 | PyPI 表单字段 |
|:-----------|:-----|:--------------|
| `repository_owner` | GitHub 仓库 owner | Owner |
| `repository` | GitHub 仓库名 | Repository name |
| `workflow` | workflow 文件名 | Workflow name |
| `pypi-project-name` | PyPI 项目名 | PyPI Project Name |

PyPI 的 Trusted Publisher 配置就是**预先注册**一组 `(owner, repository, workflow, pypi-project-name)` 组合。当 GitHub Actions 发起 OIDC 认证时，PyPI 对比 OIDC token 里的 claims 是否匹配已注册的配置——**全部精确匹配**才允许发布。

## 字段对照表

| PyPI 表单字段 | OIDC token 中的值 | 数据来源 |
|:--------------|:------------------|:---------|
| PyPI Project Name | `sra-agent` | `pyproject.toml` → `[project].name` |
| Owner | `JackSmith111977` | `git remote -v` → GitHub 用户名 |
| Repository name | `Hermes-Skill-View` | `git remote -v` → 仓库名 |
| Workflow name | `release.yml` | `.github/workflows/release.yml` |

> ⚠️ **常见误区**：
> - ❌ Owner 填成 PyPI 用户名 → 应该是 **GitHub** 用户名
> - ❌ Owner 填成 pyproject.toml 中的 author 名（如 `Kei`）
> - ❌ PyPI Project Name 填成 README 中的项目名（如 `Skill View`）→ 应该从 pyproject.toml 获取
> - ❌ Workflow name 填成通用名 `workflow.yml` → 必须精确匹配实际文件名

## 调试命令

在修复前验证字段值：

```bash
# 1. PyPI Project Name
grep "^name = " pyproject.toml | sed 's/name = "\(.*\)"/\1/'

# 2. Owner (GitHub)
git remote -v | head -1 | sed 's/.*github.com.\(.*\)\/.*/\1/'

# 3. Repository name
basename $(git rev-parse --show-toplevel)

# 4. Workflow name
ls .github/workflows/release.yml

# 5. 验证 release.yml 中的 environment 名称（应与 PyPI 配置一致）
grep -A2 "environment:" .github/workflows/release.yml
# 预期输出: name: pypi
```

## 验证 CI 配置一致性

检查 `release.yml` 中的 environment 设置：

```yaml
# 必须与 PyPI Trusted Publisher 配置一致
publish-pypi:
  name: 🚀 Publish to PyPI
  needs: [build]
  runs-on: ubuntu-latest
  environment:
    name: pypi          # ← 这个 environment 名要在 GitHub 仓库设置中创建
    url: https://pypi.org/p/sra-agent   # ← 指向正确的 PyPI 项目 URL
```

GitHub 仓库中需要存在名为 `pypi` 的 Environment（Settings → Environments → 新建 `pypi`）。

## 重试流程（发布失败后）

```bash
# 1. 删除已推送的 tag（避免 tag 冲突）
git tag -d v1.4.0
git push origin :refs/tags/v1.4.0

# 2. 重新打 tag
git tag v1.4.0
git push origin v1.4.0

# 3. 在 GitHub Actions 页面查看 CI 重新执行
# 或通过 CLI:
gh run list --workflow=release.yml
```

## 其他已知陷阱

### 陷阱 A: PyPI 项目不存在
如果 `sra-agent` 项目还未在 PyPI 上创建，Trusted Publisher 配置会失败。解决方案：
1. 手动 `twine upload` 或先通过 API token 发布一次初始版本
2. 项目存在后，再配置 Trusted Publisher 用于后续版本

### 陷阱 B: GitHub Environment 不存在
如果 `release.yml` 中引用了一个不存在的 Environment（如 `pypi`）：
- GitHub Actions 会尝试自动创建 Environment（但可能缺少审批设置）
- 推荐在 GitHub 仓库 Settings → Environments 中手动创建

### 陷阱 C: Workflow permissions 不足
在 `release.yml` 顶部必须包含：
```yaml
permissions:
  id-token: write   # OIDC 需要
  contents: write   # GitHub Release 需要
```

缺少 `id-token: write` 会导致 OIDC 认证失败。
