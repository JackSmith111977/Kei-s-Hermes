---
name: bangumi-recommender
description: "Bangumi API integration for anime recommendation, calendars, and search."
version: 1.0.0
triggers: ["番剧推荐", "新番", "Bangumi", "Anime", "番组表"]
metadata:
  hermes:
    tags: [anime, bangumi, recommendation]
    category: entertainment
    skill_type: generator
    design_pattern: tool_wrapper
---

# 番剧推荐助手 (Bangumi Recommender)

## 核心能力
1.  **新番表 (Calendar)**: 获取当季每周新番放送列表。
2.  **排行榜 (Ranking)**: 获取 Bangumi 历史高分番剧。
3.  **搜索 (Search)**: 根据关键词或标签搜索番剧。

## 使用方法
使用 `terminal` 调用 Python 脚本：
`/usr/bin/python3.12 ~/.hermes/skills/bangumi-recommender/scripts/query_bangumi.py <action> [query]`

*   **actions**:
    *   `calendar`: 获取本周新番表。
    *   `rank`: 获取排行榜。
    *   `search <keyword>`: 搜索番剧。

## 🚩 Red Flags
*   **User-Agent 是必须的**: 脚本已内置，严禁移除。
*   **ID 类型**: 注意区分 `subject_id` (条目) 和 `person_id` (人物)。
