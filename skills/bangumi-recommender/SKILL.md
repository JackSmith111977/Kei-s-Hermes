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

> 最后更新：2026-05-07（夜自习自动更新）

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

### Kodansha USA 2026 春季漫画发行
Kodansha USA 在 Anime Expo 上宣布了 2026 春季新漫画发行计划，包含多部类型丰富的作品。

### 2026 年夏季番 (Summer 2026, 7月开播) — 📊 MAL 热度排行

> **数据来源**: MyAnimeList | **更新**: 2026-05-06 (夜自习)

#### 🔥 最受期待续作 (按会员数排序)

| 作品 | 工作室 | 会员数 | 开播日期 | 类型 |
|------|--------|--------|----------|------|
| **Youjo Senki II** (幼女战记 S2) | Nut | **196K** | Jul 2026 | 异世界/军事 |
| **Mushoku Tensei III** (无职转生 S3) | Studio Bind | **169K** | Jul 6 | 异世界/冒险 |
| **Bleach: Sennen Kessen-hen - Kashin-tan** | Pierrot Films | **77K** | Jul 2026 | 战斗/完结篇 |
| **Grand Blue Season 3** | Saber Works | **45K** | Jul 2026 | 搞笑/青年 |
| **Skeleton Knight in Another World II** | Aura Studio | **41K** | Jul 2026 | 异世界 |
| **Clevatess Season 2** | Lay-duce | **33K** | Jul 2026 | 动作/奇幻 |
| **The 100 Girlfriends S3** | Bibury | **28K** | Jul 2026 | 搞笑/后宫 |
| **The Elusive Samurai S2** | CloverWorks | **27K** | Jul 2026 | 历史/搞笑 |
| **You and I Are Polar Opposites S2** | Lapin Track | **13K** | Jul 5 | 恋爱/校园 |

#### ✨ 夏季新作亮点

| 作品 | 工作室 | 会员数 | 类型亮点 |
|------|--------|--------|----------|
| **Kimi ga Shinu made Koi wo Shitai** | ROLL2 | 35K | 女校百合/战争孤儿设定 |
| **Super no Ura de Yani Suu Futari** | Asahi Production | 24K | 成人恋爱/便利店日常 |
| **Koukaku Kidoutai (TV)** | **Science SARU** | 24K | 攻壳机动队全新动画 |
| **Nijusseiki Denki Mokuroku** | **Kyoto Animation** | 20K | 历史/蒸汽朋克 |
| **Black Torch** | 100studio | 16K | 动作/妖怪/少年 |
| **Tai-Ari deshita** (大小姐不玩格斗游戏) | Diomedéa | 16K | 搞笑百合/格斗游戏 |
| **Tenmaku no Jaadugar** | Science SARU | 13K | 蒙古帝国历史剧 |

#### 🎬 夏季剧场版

- **Mahou Shoujo Madoka★Magica Movie 4: Walpurgis no Kaiten** — 魔圆新剧场版
- **Chiikawa Movie: Ningyo no Shima no Himitsu** — 小可爱剧场版
- **Crayon Shin-chan Movie 34** — 蜡笔小新新作
- **Sword Art Online: Unanswered//butterfly** — SAO 新剧场版

---

### 📈 2026 动漫行业趋势洞察 (Bushiroad 报告)

> **数据来源**: Bushiroad Anime Data Insights Lab | **发布**: 2026-01-17

#### 八大核心趋势

1. **怀旧 IP 主导** — 90s/00s 作品重制成为主流
   - 确认重制：Magic Knight Rayearth、High School! Kimengumi
   - 30-40岁粉丝有消费能力 + 文化记忆

2. **风险规避** — 原创内容减少，续作/remake 更安全
   - 全球竞争让原创 IP 更难成功

3. **短视频发现机制** — TikTok/YouTube Shorts 成核心
   - OP/ED 视频正在失去推广效果
   - 短内容用于早期吸引 + 持续互动

4. **后播出热度** — 播出后讨论驱动传播
   - 案例：Takopi's Original Sin 通过讨论/理论分析持续升温

5. **全球市场扩张** — Netflix 番剧用户 **150M+**
   - 海外流媒体覆盖日本制作成本 ≥ 70%

6. **类型饱和危机**
   - 过饱和：少年热血、战斗、异世界转生
   - 部分作品专为海外市场制作（非日本受众）

7. **年轻观众流失** — 日本年轻人对类型重复感到厌倦
   - Hideaki Anno、Tomohiko Ito 早已指出创意滑坡

8. **竞争加剧** — 与非虚构内容/现实娱乐争夺注意力

#### 日本全球扩张战略

- **目标**: 2033 年实现万亿级全球产业
- **重点市场**: 印度 (11%→41% 观众增长)、中国
- **案例**: Demon Slayer: Infinity Castle 破票房纪录

---

### 🎯 2026 十大挑战新作 (vs 王牌续作)

> **背景**: 2026 是"史上最拥挤档期" — JJK S3/Frieren S2/Oshi no Ko S3/Re:Zero S4 同年播出

| 作品 | 工作室 | 突破点 |
|------|--------|--------|
| **Witch Hat Atelier** | Bug Films | Eisner/Harvey 双奖得主，Ghibli 级视觉 |
| **Kagurabachi** | Cygames Pictures | "首个 meme-to-mainstream 成功案例" |
| **The Darwin Incident** | Bellnox Films | 漫画大赏得主，人猿杂交题材 |
| **Akane-banashi** | 未定 | Jump 非战斗叙事战略扩张（落语题材） |
| **Ikoku Nikki** | Studio Shuka | Kensuke Ushio 配乐，"艺术剧场动画"定位 |
| **You and I Are Polar Opposites** | Lapin Track | **完整改编优势** — 原作已完结 |
| **MAO** | Sunrise | 高桥留美子新作，NHK 播出保底收视 |
| **The Case Book of Arne** | Silver Link | Gothic 吸血鬼侦探，稳定周播定位 |
| **Always a Catch!** | TROYCA | CR 独占，体能女主新趋势 |
| **Tamon's B-Side** | J.C.Staff | Kadokawa 多媒体战略（偶像 IP） |

---

### FromSoftware / Kadokawa 2026 企划
FromSoftware 与母公司 Kadokawa 公布了 2026 年多个重要企划里程碑，包括 Elden Ring 系列新内容。

### 🚨 行业动态 (2026-05)

- **Studio KAI 破产危机** — 亏损 ¥565M，动漫工作室破产潮的一部分
- **Wit Studio AI 争议** — 《小书痴的下克上 S3》OP 背景使用生成式 AI，后重绘替换
- **Studio Ghibli × TOHO** — 全国经典剧场重映活动（千与千寻/哈尔的移动城堡）
- **Kadokawa Creators** — 新工作室培养年轻创作者，应对行业高流失率
- **Naruto 全球分化** — 全球 Top5，日本仅第15；本土偏爱柯南/海贼/龙珠
- **Spring 2026 突破作** — *Daemons of the Shadow Realm* 领跑日本收视

---

### 🔥 2026年5月重大新闻 (May 2026)

> **更新**: 2026-05-07 (夜自习)

#### 五等分的新娘新动画项目 (May 2)
- **官方宣布**: 「五等分的新娘」新动画项目正式启动
- **两项企划**:
  1. 小说版动画化 — 原作者 Negi Haruba 监修的完整续作
  2. 原作未动画化章节改编 — 补完粉丝期待的场景
- **累计发行**: 2000万册+（截至2026年5月）

#### One Piece Netflix 重制版 (May 5)
- **定档**: 2027年2月
- **制作**: Wit Studio
- **覆盖范围**: East Blue篇前50章 → 7集 300分钟
- **首集上映**: World Tour 2026 夏季开始先行放映
- **特色**: 从风车村 Partys Bar 场景开始，重绘经典

#### Kagurabachi 动画化确认 (April 27)
- **开播**: 2027年4月
- **制作**: Cypic (Umamusume: Cinderella Gray 同团队)
- **导演**: Tetsuya Takeuchi | **角色设计**: Keigo Sasaki
- **声优**: Taihi Kimura (主角 Chihiro Rokuhira)
- **累计发行**: 400万册+ (Vol.11)
- **World Tour**: 2026夏季先行20分钟，日本首映完整第1集

#### Summer 2026 中季评价 (Mid-Season)
- **领跑**: Bleach TYBW - The Calamity 压倒性热度
- **黑马**: Black Torch 稳步升温，超出预期
- **稳定**: Mushoku Tensei S3、Youjo Senki II 保持高质量
- **争议**: The Detective Is Already Dead S2 节奏问题

#### Magical Girl Nanoha 回归
- **系列**: Mahou Shoujo Lyrical Nanoha EXCEEDS: Gun Blaze Vengeance
- **意义**: 十年后首次TV系列回归
- **设定**: 更暗黑风格，对抗"Invasion Species"外星威胁
- **制作**: Seven ARCS

---

### 📅 2027 年重点项目预告

| 作品 | 开播时间 | 工作室 | 类型 | 备注 |
|------|----------|--------|------|------|
| **Kagurabachi** | 2027年4月 | Cypic | 动作/超自然 | Jump新生代旗舰 |
| **One Piece Netflix重制** | 2027年2月 | Wit Studio | 冒险 | East Blue 50章 |
| **Re:Zero S4** | 待定 | White Fox | 异世界 | MAL Top 5 |
| **Dungeon Meshi S2** | 待定 | Trigger | 奇幻/美食 | 原作完结 |
