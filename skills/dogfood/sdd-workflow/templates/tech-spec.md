# 📋 技术版本规约 (Tech Spec) — {Story ID}

> **关联 Spec**: {Spec 路径} · **架构设计**: {Arch 路径}
> **版本**: 1.0.0 · **更新**: {日期}

---

## 一、技术栈版本清单

| 技术 | 版本 | 用途 | API 参考文档 |
|:-----|:----:|:-----|:-------------|
| Python | 3.11.9 | 运行时 | https://docs.python.org/3.11/ |
| FastAPI | 0.110.0 | API 框架 | https://fastapi.tiangolo.com/0.110/ |
| SQLAlchemy | 2.0.30 | ORM | https://docs.sqlalchemy.org/en/20/ |
| Pydantic | 2.7.0 | 数据校验 | https://docs.pydantic.dev/2.7/ |
| pytest | 8.2.0 | 测试框架 | https://docs.pytest.org/en/8.2/ |
| ... | ... | ... | ... |

> **规则**: 版本必须精确锁定（不用 `^` / `~` / `latest`），API 参考指向版本对应的文档页。

---

## 二、依赖清单

### Python 依赖

```text
# requirements.txt 或 pyproject.toml 中提取
package_a==1.2.3
package_b==4.5.6
```

### 系统依赖

| 依赖 | 版本要求 | 检查命令 |
|:-----|:---------|:---------|
| Node.js | ≥ 18.0.0 | `node --version` |
| Docker | ≥ 24.0 | `docker --version` |

### 外部服务

| 服务 | API 版本 | 认证方式 | 端点 |
|:-----|:---------|:---------|:-----|
| OpenAI | 2024-02 | Bearer Token | `https://api.openai.com/v1/` |

---

## 三、API 契约版本对照

| 接口 | 版本 | 规范文件 | 说明 |
|:-----|:----:|:---------|:------|
| `/api/v1/users` | OpenAPI 3.1 | `docs/api/users.openapi.yaml` | 用户管理 |
| WebSocket Events | 无版本 | `docs/api/events.md` | 实时事件 |

---

## 四、版本变更历史

| 日期 | 变更 | 技术 | 旧版本 → 新版本 | 影响范围 |
|:-----|:-----|:-----|:---------------|:---------|
| — | — | — | — | — |
