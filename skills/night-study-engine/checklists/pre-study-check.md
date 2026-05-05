# 🌙 夜间学习前检查清单

## 环境检查
- [ ] `~/.hermes/config/night_study_config_v2.json` 存在且有效
- [ ] `~/.hermes/night_study/knowledge_base/` 目录存在
- [ ] `~/.hermes/logs/night_study_sessions/` 目录存在
- [ ] Tavily MCP 搜索可用（运行 `mcp_tavily_tavily_search` 测试）
- [ ] 代理配置正常（`http.proxy=http://127.0.0.1:7890`）

## 领域选择检查
- [ ] 运行 `select_domain.py` 获取当前最需要的领域
- [ ] 检查该领域上次学习时间（避免重复学习）
- [ ] 检查是否有间隔复习到期的概念

## 学习质量准备
- [ ] 准备搜索关键词（从配置中读取 keywords）
- [ ] 准备目标 skill（从配置中读取 target_skill）
- [ ] 确认 learning-workflow 流程可用

## 产出准备
- [ ] 确认目标 skill 存在（如果不存在，创建新的）
- [ ] 准备结构化日志模板
- [ ] 准备 Knowledge Base 更新脚本

## 失败恢复准备
- [ ] 如果搜索无结果 → 准备替代关键词
- [ ] 如果网页无法访问 → 准备备用来源
- [ ] 如果质量评分 < 60 → 准备 Loop N+1 流程
- [ ] 如果超时 → 准备"未完成"标记

## 完成后检查
- [ ] Artifact 是否产出（Skill/Memory/Guide）
- [ ] Knowledge Base 是否更新
- [ ] 结构化日志是否写入
- [ ] 汇总日志是否追加
