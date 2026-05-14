# SRA 源码架构深度解析

> 深度学习时间: 2026-05-14
> 来源: skill_advisor/ 源码逐文件阅读
> 版本: 2.0.3

---

## 一、项目结构

```
skill_advisor/
├── __init__.py          # 包入口：暴露 SkillAdvisor + SRaDDaemon
├── _version.py          # setuptools-scm 自动版本
├── cli.py               # CLI 全部子命令（~880行）
├── advisor.py           # SkillAdvisor 引擎（核心入口）
├── matcher.py           # 四维匹配引擎
├── indexer.py           # 技能索引构建
├── memory.py            # 场景记忆持久化
├── skill_map.py         # 技能映射工具
├── synonyms.py          # 同义词字典
├── adapters/
│   └── __init__.py      # Agent 适配器（hermes/claude/codex/opencode/generic）
└── runtime/
    ├── config.py        # 配置管理（加载/保存/Schema校验）
    ├── daemon.py        # 守护进程（Socket + HTTP 双协议）
    ├── force.py         # 运行时力度体系（4级注入）
    ├── commands.py      # daemon start/stop/status/restart
    ├── dropin.py        # 即插即用安装
    ├── lock.py          # 文件锁机制
    ├── validate_core.py # 技能验证核心
    └── endpoints/
        └── validate.py  # 验证端点
```

## 二、守护进程架构 (daemon.py)

```
┌─────────────────────────────────────────────────┐
│                  SRaDDaemon                      │
│                                                   │
│  ┌─────────────────┐   ┌──────────────────┐      │
│  │ Unix Socket     │   │ HTTP Server      │      │
│  │ /tmp/srad.sock  │   │ :8536            │      │
│  ├─────────────────┤   ├──────────────────┤      │
│  │ IPC 协议         │   │ REST API:        │      │
│  │ {action, params} │   │ /health          │      │
│  │ recommend        │   │ /recommend POST  │      │
│  │ stats            │   │ /refresh POST    │      │
│  │ refresh          │   │ /stats GET       │      │
│  │ record           │   │ /force GET/POST  │      │
│  │ coverage         │   │ /validate POST   │      │
│  └─────────────────┘   └──────────────────┘      │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │         SkillAdvisor Engine              │    │
│  │  Indexer → Matcher → Memory              │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Auto-Refresh Loop (configurable)        │    │
│  │  + Force Level Manager                   │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

**关键设计**：
- 双协议 API：Unix Socket（IPC，更快）+ HTTP（外部访问）
- 自动索引刷新：定时（auto_refresh_interval）+ 文件变更监听（watch_skills_dir）
- 力度管理器：运行时动态切换，无需重启
- 所有注入点均为非阻塞（info/warning 级别，无 block）

## 三、推荐引擎流程 (advisor.py)

```
recommend(query, top_k=3)
  ↓
1. _ensure_index() → Indexer 懒加载/构建
2. extract_keywords(query) → 分词 + 去停用词
3. expand_with_synonyms(words) → 同义词扩展
4. 遍历所有技能（203个） → Matcher.score() 四维评分
5. 过滤: score >= THRESHOLD_WEAK(40)
6. 排序取 top_k → 构建建议(contract)
7. 返回: {recommendations, processing_ms, skills_scanned, contract}
```

### 阈值定义

```python
THRESHOLD_STRONG = 80  # 强推荐 → required_skills
THRESHOLD_WEAK = 40    # 弱推荐 → optional_skills
```

### should_auto_load 判定

```python
should_auto_load = (max_score >= THRESHOLD_STRONG and len(required) > 0)
```

即：只有当至少一个 skill 得分 ≥ 80 时，才自动加载。
当前 SRA 运行中最高分仅 60.5（medium），所以 `should_auto_load` 始终为 false。

### recheck() — 上下文漂移检测

```python
recheck(conversation_summary, loaded_skills, top_k=5)
# 1. recommend() → 获取推荐结果
# 2. 对比已加载 skill 列表 → 找出 missing
# 3. 计算 drift_score = len(missing) / len(recs)
# 4. has_drift = missing > 0 AND drift_score >= 0.2
```

用于长任务中定期检测是否需要换 skill（omni 级别启用）。

## 四、四维匹配引擎 (matcher.py)

### 权重配置

```python
WEIGHT_LEXICAL = 0.40    # 词法
WEIGHT_SEMANTIC = 0.25   # 语义
WEIGHT_SCENE = 0.20      # 场景
WEIGHT_CATEGORY = 0.15   # 类别
```

### 词法匹配细节

| 子匹配 | 分值 | 条件 |
|--------|:----:|------|
| name 精确 | 30 | w == skill_name 或 skill_name in w |
| name 部分 | 20 | len(w) ≥ 3 且 w in skill_name |
| trigger 匹配 | 25 | w in triggers |
| tag 匹配 | 15 | w in tags |
| 描述匹配 | 8 | len(w) ≥ 2 且 w in description |
| match_text 匹配 | 3 | w in match_text |
| 同义词精确 | 25 | 同义词 in name/trigger/tags |
| 同义词宽泛 | 12 | 同义词 in description/match_text |

### SQS 质量加权

```python
def _quality_modifier(sqs: float) -> float:
    if sqs >= 80: return 1.0
    elif sqs >= 60: return 0.9
    elif sqs >= 40: return 0.7
    else: return 0.4  # sqs < 40
# 无评分时默认 50 → modifier = 0.7
```

**重要**：即使 skill 的词法匹配得分很高（如 60），如果 SQS 只有 40 分，最终得分 = 60 × 0.7 = 42，刚好踩在 weak 线上。

## 五、运行时力度体系 (force.py)

| 等级 | 注入点 | 工具监控 | 周期性 |
|:----|:-------|:---------|:------:|
| **🐣 basic** | on_user_message | 无 | ❌ |
| **🦅 medium** | on_user_message + pre_tool_call | write_file/patch/terminal/execute_code | ❌ |
| **🦖 advanced** | on_user_message + pre_tool_call + post_tool_call | __all__ | ❌ |
| **🐉 omni** | 全部 + periodic | __all__ | ✅ 每 N 轮 |

**注入点含义**：
- `on_user_message`：用户消息时注入 SRA 推荐上下文
- `pre_tool_call`：工具调用前检查是否需要加载技能
- `post_tool_call`：工具调用后核查上下文是否漂移
- `periodic`：周期性重注入（防漂移，omni 独有）

## 六、常用 CLI 命令的代码路径

| 命令 | 文件:行号 | 关键逻辑 |
|:-----|:---------|:---------|
| `sra start` | commands.py: cmd_start | 写 PID + 锁文件，fork 子进程 |
| `sra stop` | commands.py: cmd_stop | 读 PID → kill → 清理 |
| `sra attach` | commands.py: cmd_attach | 前台运行 daemon.start() |
| `sra recommend` | cli.py:66 | Socket 请求 → 降级本地 SkillAdvisor |
| `sra config set` | cli.py:281 | 类型推断 + 嵌套 key（点号） + save |
| `sra force set` | cli.py:344 | ForceLevelManager.set_level() |
| `sra coverage` | cli.py:147 | advisor.analyze_coverage() |
| `sra stats` | cli.py:114 | daemon stats + uptime |
| `sra upgrade` | cli.py:494 | git clone 最新版 + pip install |
