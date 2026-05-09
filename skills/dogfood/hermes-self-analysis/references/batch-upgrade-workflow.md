# Hermes 批次升级工作流

> 最后更新: 2026-05-09 | 基于 Batch 1-3 实战经验

## 核心原则

批次升级 = 先审计 → 分批次 → 逐项验证 → 更新记忆+skill

## 审计命令 (全量扫描)

```bash
hermes tools list                     # 查看已禁用工具集
hermes plugins list                    # 查看未启用插件
hermes status | grep "not"            # 查看未配置项目
hermes config check                    # 配置健康检查
hermes memory status                   # 记忆提供商
hermes mcp list                        # MCP 服务器
hermes profile list                    # 多 Profile
hermes curator status                  # Curator 状态
hermes skills browse --source official # 官方 skill (4 页)
hermes --help                          # 全部 CLI 子命令
```

## 批次分级策略

| 批次 | 类型 | 需要什么 | 风险 |
|:---:|:---|:---|:---:|
| 1 | 配置开关 + 内置工具 | 无 | 低 |
| 2 | CLI 探索 + 安全配置 | 无 | 低 |
| 3 | 外部服务 + API Key | 主人提供 Key / 配置 | 中 |
| 4 | 消息平台 | API Token | 中 |
| 5 | 架构级探索 | 学习时间 | 高 |

## 经验教训

### 工具集/插件启用
- `hermes tools enable <name>` — **无需确认**, 直接成功 ✅
- `hermes plugins enable <name>` — **无需确认**, 直接成功 ✅
- `hermes skills install <name>` — **需要 `--yes` 或 `yes |`** 跳过确认 ⚠️

### 已知限制
- `hermes-achievements` 和 `observability/langfuse` 插件在 Hermes v0.10.0 未打包
- OpenRouter SSL 错误 → `model_catalog.enabled: true` 在国内网络下同步失败
- Profile 完全隔离 (记忆/技能/env 不共享)
- 网关重启需要主人手动执行

### 最佳实践
1. 每个变更后立即验证 (`hermes config check` 或 `hermes tools list`)
2. 备份先于批量变更 (`hermes backup -q`)
3. 每个批次完成后更新记忆 + self-capabilities-map
4. 主 skill (self-capabilities-map) + 参考文件 (此文件) 都要更新
