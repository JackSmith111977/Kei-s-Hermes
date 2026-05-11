# 搜索次数节省策略指南

> **核心目标**：通过缓存、语义检测等手段，减少重复的 API 调用，节省成本并提升响应速度。
>
> **基于研究**：AgentOpt (arxiv 2604.06296), GPTCache, LLM Cost Optimization Blog

---

## 一、三级缓存架构

### 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Hermes Web Cache                              │
├─────────────────────────────────────────────────────────────────────┤
│  Level 1: Response Cache                                             │
│  ├─ 完整 API 响应缓存                                                 │
│  ├─ Key: request_hash (tool + normalized_params)                    │
│  ├─ TTL: 1h (动态) / 24h (静态) / 7d (稳定知识)                        │
│  └─ 预估节省: 35-40%                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Level 2: Semantic Cache                                             │
│  ├─ 语义相似 Query 缓存                                               │
│  ├─ Key: embedding vector                                            │
│  ├─ Threshold: 0.85 (cosine similarity)                             │
│  ├─ TTL: 24h                                                         │
│  └─ 预估节省: 61-68%                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Level 3: Retrieval Cache                                            │
│  ├─ RAG 检索结果缓存                                                  │
│  ├─ Key: query_cluster_hash                                         │
│  ├─ TTL: 6-24h                                                       │
│  └─ 预估节省: 20-30%                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、Request Cache（精确缓存）

### 适用工具

| 工具 | 缓存策略 | TTL | 预估命中率 |
|------|---------|-----|-----------|
| `web_search` | 全参数哈希 | 24h (默认) / 1h (news) | 35% |
| `web_extract` | URL 哈希 | 24h | 40% |
| `web_crawl` | URL + instructions 哈希 | 3d | 50% |
| `browser_navigate` | URL 哈希 | 1h | 30% |
| `mcp_tavily_*` | 全参数哈希 | 24h | 40% |

### 缓存键生成规则

```python
import hashlib
import json

def generate_cache_key(tool_name, params):
    """生成缓存键
    
    原理：
    1. 移除随机性参数（session_id, timestamp）
    2. 排序字典键（确保相同内容生成相同哈希）
    3. 使用 SHA256 截断前 16 位
    """
    exclude_keys = ["session_id", "timestamp", "random_seed", "request_id"]
    normalized_params = {
        k: v for k, v in params.items() 
        if k not in exclude_keys
    }
    
    # 特殊处理：query normalization
    if "query" in normalized_params:
        normalized_params["query"] = normalize_query(
            normalized_params["query"]
        )
    
    cache_payload = {
        "tool": tool_name,
        "params": normalized_params
    }
    
    return hashlib.sha256(
        json.dumps(cache_payload, sort_keys=True).encode()
    ).hexdigest()[:16]

def normalize_query(query):
    """Query normalization
    
    1. 移除多余空格
    2. 统一大小写（根据场景）
    3. 移除无意义的修饰词（可选）
    """
    return query.strip().lower()
```

### TTL 策略

| 内容类型 | TTL | 依据 |
|---------|-----|------|
| **新闻/时事** | 1h | 时效性要求高 |
| **API 文档** | 7d | 相对稳定 |
| **百科/知识** | 7d | 长期稳定 |
| **技术博客** | 24h | 中等时效 |
| **价格/行情** | 1h | 频繁变动 |

### 实现代码模板

```python
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class WebRequestCache:
    """基于 SQLite 的请求缓存"""
    
    DB_PATH = Path.home() / ".hermes" / "cache" / "web_cache.db"
    
    TTL_CONFIG = {
        "web_search:news": timedelta(hours=1),
        "web_search:docs": timedelta(days=7),
        "web_search:default": timedelta(hours=24),
        "web_extract": timedelta(hours=24),
        "web_crawl": timedelta(days=3),
        "browser_navigate": timedelta(hours=1),
    }
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                tool TEXT,
                params TEXT,
                result TEXT,
                timestamp TEXT,
                ttl_seconds INTEGER
            )
        """)
        conn.commit()
        conn.close()
    
    def get(self, tool_name, params):
        """获取缓存"""
        key = generate_cache_key(tool_name, params)
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.execute(
            "SELECT result, timestamp, ttl_seconds FROM cache WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result, timestamp_str, ttl_seconds = row
            timestamp = datetime.fromisoformat(timestamp_str)
            if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                return json.loads(result)  # Cache hit
        
        return None  # Cache miss or expired
    
    def set(self, tool_name, params, result, ttl=None):
        """设置缓存"""
        key = generate_cache_key(tool_name, params)
        
        # 决定 TTL
        if ttl is None:
            ttl_key = f"{tool_name}:{params.get('topic', 'default')}"
            ttl = self.TTL_CONFIG.get(ttl_key, timedelta(hours=24))
        
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?, ?, ?)",
            (key, tool_name, json.dumps(params), json.dumps(result),
             datetime.now().isoformat(), int(ttl.total_seconds()))
        )
        conn.commit()
        conn.close()
    
    def invalidate(self, tool_name=None, params=None):
        """失效缓存"""
        conn = sqlite3.connect(self.DB_PATH)
        if tool_name and params:
            key = generate_cache_key(tool_name, params)
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        elif tool_name:
            conn.execute("DELETE FROM cache WHERE tool = ?", (tool_name,))
        else:
            conn.execute("DELETE FROM cache")
        conn.commit()
        conn.close()
    
    def cleanup_expired(self):
        """清理过期缓存"""
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute("""
            DELETE FROM cache WHERE 
            datetime(timestamp) + ttl_seconds < datetime('now')
        """)
        deleted = conn.total_changes
        conn.commit()
        conn.close()
        return deleted
```

---

## 三、Semantic Cache（语义缓存）

### 适用场景

| 场景 | 示例 | 是否适合 |
|------|------|---------|
| 客服问答 | "退货政策是什么" vs "如何退货" | ✅ 高度适合 |
| 技术搜索 | "Python 安装" vs "怎么安装 Python" | ✅ 高度适合 |
| 创意写作 | 各种不同的写作请求 | ❌ 不适合 |
| 个性化推荐 | 用户特定上下文查询 | ❌ 不适合 |

### 实现代码模板

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sqlite3
import json
from datetime import datetime, timedelta

class SemanticQueryCache:
    """基于语义相似度的查询缓存"""
    
    DB_PATH = Path.home() / ".hermes" / "cache" / "semantic_cache.db"
    DEFAULT_THRESHOLD = 0.85
    DEFAULT_TTL = timedelta(hours=24)
    
    # 轻量级 embedding 模型推荐
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # ~80MB, 快速
    
    def __init__(self, threshold=None):
        self.threshold = threshold or self.DEFAULT_THRESHOLD
        self.model = SentenceTransformer(self.EMBEDDING_MODEL)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_cache (
                id INTEGER PRIMARY KEY,
                query TEXT,
                embedding BLOB,
                result TEXT,
                timestamp TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON semantic_cache(timestamp)
        """)
        conn.commit()
        conn.close()
    
    def encode(self, query):
        """将查询编码为向量"""
        return self.model.encode(query, normalize_embeddings=True)
    
    def find_similar(self, new_query):
        """查找语义相似的缓存查询"""
        new_embedding = self.encode(new_query)
        
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.execute(
            "SELECT query, embedding, result, timestamp FROM semantic_cache"
        )
        rows = cursor.fetchall()
        conn.close()
        
        best_match = None
        best_similarity = 0
        
        for query, embedding_blob, result, timestamp_str in rows:
            # 检查 TTL
            timestamp = datetime.fromisoformat(timestamp_str)
            if datetime.now() - timestamp > self.DEFAULT_TTL:
                continue  # Expired
            
            # 计算 cosine similarity
            cached_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            similarity = np.dot(new_embedding, cached_embedding)
            
            if similarity > self.threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    "query": query,
                    "result": json.loads(result),
                    "similarity": similarity
                }
        
        return best_match
    
    def add(self, query, result):
        """添加新查询到缓存"""
        embedding = self.encode(query)
        embedding_blob = embedding.astype(np.float32).tobytes()
        
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute(
            "INSERT INTO semantic_cache VALUES (?, ?, ?, ?, ?, ?)",
            (None, query, embedding_blob, json.dumps(result),
             datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_or_compute(self, query, compute_fn):
        """获取缓存或计算新结果"""
        cached = self.find_similar(query)
        if cached:
            return cached["result"], cached["similarity"], True  # Hit
        
        result = compute_fn()
        self.add(query, result)
        return result, 0, False  # Miss
```

### Threshold 选择指南

| Threshold | 特点 | 适用场景 |
|-----------|------|---------|
| **0.95** | 极严格，几乎精确匹配 | 高准确性要求 |
| **0.90** | 严格，相似度高 | 技术文档搜索 |
| **0.85** | 平衡（推荐） | 客服问答、通用搜索 |
| **0.80** | 宽松，可能误匹配 | 大流量、高缓存需求 |
| **0.75** | 过宽松，不建议 | 可能返回错误答案 |

---

## 四、缓存检查流程

### Agent 执行流程（插入缓存检查）

```
用户请求 → 需要联网操作？
             ↓
         加载 web-access skill
             ↓
         [缓存检查 - 新增步骤]
         ├─ L1 Response Cache 检查
         │   ├─ Hit → 直接返回缓存结果 ✅
         │   └─ Miss ↓
         ├─ L2 Semantic Cache 检查
         │   ├─ Hit (similarity > 0.85) → 返回相似缓存 ✅
         │   └─ Miss ↓
         └─ 执行 API 调用
             ↓
         存储结果到 L1 + L2 缓存
             ↓
         返回结果给用户
```

### Agent 代码位置

在 `run_agent.py` 的 `handle_function_call()` 函数前插入缓存检查：

```python
# 位置：~/.hermes/hermes-agent/run_agent.py
# 在 handle_function_call 之前

def handle_tool_call_with_cache(tool_name, tool_args, task_id):
    """带缓存的工具调用处理"""
    
    # Step 1: 检查是否为可缓存工具
    CACHEABLE_TOOLS = ["web_search", "web_extract", "web_crawl", 
                       "browser_navigate", "mcp_tavily_*"]
    
    if tool_name in CACHEABLE_TOOLS or tool_name.startswith("mcp_tavily"):
        
        # Step 2: L1 Response Cache 检查
        cached_result = web_request_cache.get(tool_name, tool_args)
        if cached_result:
            log_cache_hit(tool_name, "L1_response")
            return cached_result
        
        # Step 3: L2 Semantic Cache 检查（仅对搜索类工具）
        if tool_name in ["web_search", "mcp_tavily_tavily_search"]:
            semantic_match = semantic_query_cache.find_similar(
                tool_args.get("query", "")
            )
            if semantic_match:
                log_cache_hit(tool_name, "L2_semantic", 
                              semantic_match["similarity"])
                return semantic_match["result"]
    
    # Step 4: 执行实际工具调用
    result = handle_function_call(tool_name, tool_args, task_id)
    
    # Step 5: 存储到缓存（仅成功结果）
    if result and not result.get("error"):
        web_request_cache.set(tool_name, tool_args, result)
        
        if tool_name in ["web_search", "mcp_tavily_tavily_search"]:
            semantic_query_cache.add(
                tool_args.get("query", ""), result
            )
    
    return result
```

---

## 五、统计与监控

### 关键指标

| 指标 | 计算公式 | 目标值 |
|------|---------|-------|
| **L1 命中率** | L1_hits / total_requests | > 35% |
| **L2 命中率** | L2_hits / (total - L1_hits) | > 60% |
| **总节省率** | (L1_hits + L2_hits) / total | > 50% |
| **平均延迟** | cached_latency / uncached_latency | < 10% |
| **缓存大小** | DB 文件大小 | < 100MB |

### 日志记录

```python
def log_cache_hit(tool_name, cache_level, similarity=None):
    """记录缓存命中"""
    import logging
    logger = logging.getLogger("hermes.cache")
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "cache_level": cache_level,
        "similarity": similarity,
        "event": "cache_hit"
    }
    logger.info(json.dumps(log_data))

def log_cache_miss(tool_name, reason):
    """记录缓存未命中"""
    import logging
    logger = logging.getLogger("hermes.cache")
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "reason": reason,
        "event": "cache_miss"
    }
    logger.info(json.dumps(log_data))
```

---

## 六、避坑指南

### 常见陷阱

| 陷阱 | 表现 | 解决方案 |
|------|------|---------|
| **缓存过期信息** | 返回过时答案 | TTL 策略 + 手动失效 |
| **语义误匹配** | 返回无关答案 | Threshold 调高 + 人工审核 |
| **缓存污染** | 错误答案被缓存 | 结果质量检查 |
| **缓存膨胀** | DB 过大 | 定期清理 + 上限设置 |
| **上下文混淆** | 不同对话相同 Query 返回错误 | Context-aware caching |

### 不适合缓存的场景

| 场景 | 原因 | 替代方案 |
|------|------|---------|
| 创意写作 | 每次请求独特 | 不缓存 |
| 实时数据 | 秒级变化 | TTL = 1min 或不缓存 |
| 个性化推荐 | 用户特定 | Per-user cache |
| 高安全要求 | 数据敏感 | 内存缓存 + 加密 |

---

## 七、参考文献

1. **AgentOpt (arxiv 2604.06296)** - Client-side LLM Agent Optimization
2. **GPTCache** - Semantic Cache for LLM Queries (https://github.com/zilliztech/GPTCache)
3. **Prompt Caching (arxiv 2502.07776)** - Auditing Prompt Caching in APIs
4. **LLM Cost Optimization Blog** - 8 Strategies That Cut API Spend by 80%

---

## 八、快速实施检查清单

- [ ] 创建 `~/.hermes/cache/` 目录
- [ ] 实现 `WebRequestCache` 类
- [ ] 在 `web_search` 调用前插入 L1 缓存检查
- [ ] 配置 TTL 策略
- [ ] 添加缓存命中日志
- [ ] 实现定期清理脚本
- [ ] （可选）实现 `SemanticQueryCache`
- [ ] （可选）安装 `sentence-transformers`