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

## 📅 2026 年新番与 ACG 资讯

> 最后更新：2026-05-04（夜自习自动更新）

### 2026 春季番 (Spring 2026, 4月开播)

**重点关注作品**：
- **Dorohedoro Season 2** — 4月1日开播，暗黑奇幻续作
- **The Beginning After the End Season 2** — 4月1日开播
- **Witch Hat Atelier (魔法帽的工坊)** — 周一档 (CR)
- **Re: Zero - Starting Life in Another World** — 持续放送中
- **Dr. Stone: Science Future** — 春季续作

**周一档完整列表**：Farming Life in Another World S2、The Klutzy Class Monitor、Observation Log of My Fiancee Who Calls Herself a Villainess、Release that Witch (donghua)、Witch Hat Atelier

**周二档完整列表**：Eren the Southpaw、Even a Replica Can Fall in Love、Food Diary of Miss Maid、I Made Friends With the Second Prettiest Girl、Liar Game、Marriagetoxin、Most Heretical Last Boss Queen 等

### 2026 年度备受期待新作

- **Jujutsu Kaisen Season 3** — MAPPA 制作，Culling Game 篇 + Perfect Preparation 篇
- **My Hero Academia: Vigilantes** — 正传前传衍生动画，讲述 Koichi Haimawari 的故事
- **Hana-Kimi (花ざかりの君たちへ)** — Hisaya Nakajo 经典少女漫画首次动画化
- **Fate/Strange fake** — A-1 Pictures 制作
- **Daemons of the Shadow Realm** — 暗黑奇幻新作，预计 2026 年 4 月播出
- **Danganronpa 2×2** — 游戏新作，含原创剧情分支
- **Invincible VS** — 3v3 格斗游戏，原作编剧参与叙事设计
- **Avatar Legends: The Fighting Game** — 基于降世神通宇宙的格斗游戏

### Viz Media 2026 新漫画计划
Viz Media 在 2026 年公布了多个新漫画项目，涵盖多种类型。
