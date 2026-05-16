#!/usr/bin/env python3
"""生成夜间自习引擎 v3.0 配置 + KB 骨架 — 覆盖全部 18 个领域 (映射全部 17 cap-pack packs)

用法: python3 generate-night-study-config.py
输出: ~/.hermes/config/night_study_config_v3.json
      ~/.hermes/night_study/knowledge_base/{domain}.json (如缺失)
"""

import json, pathlib, datetime

CONFIG_DIR = pathlib.Path.home() / ".hermes" / "config"
KB_DIR = pathlib.Path.home() / ".hermes" / "night_study" / "knowledge_base"
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

DOMAINS = [
    # ── 已有领域（保留 + 增强） ──
    {
        "id": "ai_tech",
        "name": "AI与前沿技术",
        "keywords": "AI agents, LLM new models, ML papers, ICLR/NeurIPS, agentic AI, open source models, benchmarks",
        "target_skill": "ai-trends",
        "priority": 0.95,
        "schedule_interval_hours": 2,
        "cap_pack": ["learning-engine"],
        "freshness_score": 0.5,
        "review_schedule": {"l1": NOW[:10], "l2": NOW[:10], "l3": NOW[:10]},
        "learning_history": {"total_sessions": 0, "avg_quality": 0.5, "last_loop_count": 0, "consecutive_failures": 0}
    },
    {
        "id": "dev_tools",
        "name": "开发工具与语言",
        "keywords": "Python, TypeScript, Rust, Go, Node.js, new frameworks, DevOps tools, language updates",
        "target_skill": "python-env-guide",
        "priority": 0.85,
        "schedule_interval_hours": 4,
        "cap_pack": ["developer-workflow"],
        "freshness_score": 0.5
    },
    {
        "id": "anime_acg",
        "name": "二次元与文娱",
        "keywords": "anime, manga, game industry, ACG culture, bangumi, gaming news",
        "target_skill": "bangumi-recommender",
        "priority": 0.4,
        "schedule_interval_hours": 12,
        "cap_pack": ["social-gaming"],
        "freshness_score": 0.5
    },
    {
        "id": "productivity",
        "name": "效率与工作方法论",
        "keywords": "knowledge management, workflow automation, productivity tools, AI workflows, automation patterns",
        "target_skill": "memory-management",
        "priority": 0.75,
        "schedule_interval_hours": 6,
        "cap_pack": ["learning-engine"],
        "freshness_score": 0.5
    },

    # ── 新增领域（映射 cap-pack 包） ──
    {
        "id": "agent_orchestration",
        "name": "Agent 编排与集成",
        "keywords": "multi-agent, agent orchestration, Hermes, OpenCode, Claude Code, Codex, subagent, message injection, ACP protocol",
        "target_skill": "hermes-agent",
        "priority": 0.9,
        "schedule_interval_hours": 3,
        "cap_pack": ["agent-orchestration"],
        "freshness_score": 0.5
    },
    {
        "id": "creative_design",
        "name": "创意设计与视觉",
        "keywords": "architecture diagram, ASCII art, image generation, concept diagrams, Excalidraw, pixel art, meme, comfyui, manim, p5js, visual aesthetics",
        "target_skill": "architecture-diagram",
        "priority": 0.5,
        "schedule_interval_hours": 24,
        "cap_pack": ["creative-design"],
        "freshness_score": 0.5
    },
    {
        "id": "devops_monitoring",
        "name": "运维与监控",
        "keywords": "Docker, Linux ops, process management, project startup, webhook, Kanban, proxy monitor, cron job",
        "target_skill": "linux-ops-guide",
        "priority": 0.7,
        "schedule_interval_hours": 8,
        "cap_pack": ["devops-monitor"],
        "freshness_score": 0.5
    },
    {
        "id": "doc_generation",
        "name": "文档生成与排版",
        "keywords": "PDF layout, WeasyPrint, ReportLab, HTML presentation, PPTX generation, Markdown, LaTeX, EPUB, doc design",
        "target_skill": "pdf-layout",
        "priority": 0.6,
        "schedule_interval_hours": 12,
        "cap_pack": ["doc-engine"],
        "freshness_score": 0.5
    },
    {
        "id": "github_ecosystem",
        "name": "GitHub 生态与协作",
        "keywords": "Git, GitHub, PR workflow, code review, issues, project management, CI/CD, Actions, releases",
        "target_skill": "github-pr-workflow",
        "priority": 0.7,
        "schedule_interval_hours": 8,
        "cap_pack": ["github-ecosystem"],
        "freshness_score": 0.5
    },
    {
        "id": "learning_methodology",
        "name": "学习与研究系统",
        "keywords": "learning workflow, deep research, arxiv, knowledge precipitation, blog watching, LLM wiki, knowledge base",
        "target_skill": "learning-workflow",
        "priority": 0.85,
        "schedule_interval_hours": 4,
        "cap_pack": ["learning-engine", "learning-workflow"],
        "freshness_score": 0.5
    },
    {
        "id": "media_audio_video",
        "name": "音视频与媒体处理",
        "keywords": "music generation, audio visualization, GIF search, Spotify, YouTube, media processing",
        "target_skill": "heartmula",
        "priority": 0.3,
        "schedule_interval_hours": 24,
        "cap_pack": ["media-processing"],
        "freshness_score": 0.5
    },
    {
        "id": "messaging_comm",
        "name": "消息通信与推送",
        "keywords": "Feishu, Lark, WeChat, email, social broadcast, webhook, message push, platform integration",
        "target_skill": "feishu",
        "priority": 0.7,
        "schedule_interval_hours": 8,
        "cap_pack": ["messaging"],
        "freshness_score": 0.5
    },
    {
        "id": "metacognition_system",
        "name": "元认知与系统自省",
        "keywords": "self-analysis, capability map, skill creation, architecture design, design philosophy, skill publishing",
        "target_skill": "self-capabilities-map",
        "priority": 0.6,
        "schedule_interval_hours": 12,
        "cap_pack": ["metacognition"],
        "freshness_score": 0.5
    },
    {
        "id": "network_proxy",
        "name": "网络与代理",
        "keywords": "Clash, mihomo, proxy configuration, proxy finder, web access, network routing",
        "target_skill": "clash-config",
        "priority": 0.5,
        "schedule_interval_hours": 12,
        "cap_pack": ["network-proxy"],
        "freshness_score": 0.5
    },
    {
        "id": "quality_governance",
        "name": "质量治理与合规",
        "keywords": "SQS scoring, quality gates, health check, CHI, lifecycle audit, compliance, governance engine",
        "target_skill": "skill-creator",
        "priority": 0.65,
        "schedule_interval_hours": 8,
        "cap_pack": ["quality-assurance", "skill-quality"],
        "freshness_score": 0.5
    },
    {
        "id": "security_audit",
        "name": "安全审计与防护",
        "keywords": "commit quality, 1Password, OSINT, Sherlock, red team, delete safety, security scanning",
        "target_skill": "commit-quality-check",
        "priority": 0.6,
        "schedule_interval_hours": 12,
        "cap_pack": ["security-audit"],
        "freshness_score": 0.5
    },
    {
        "id": "financial_analysis",
        "name": "金融数据分析",
        "keywords": "akshare, stock market, technical indicators, matplotlib charts, financial reports, quantitative analysis",
        "target_skill": "financial-analyst",
        "priority": 0.3,
        "schedule_interval_hours": 24,
        "cap_pack": ["financial-analysis"],
        "freshness_score": 0.5
    },
    {
        "id": "social_gaming",
        "name": "社交游戏与娱乐",
        "keywords": "Minecraft server, Pokemon emulator, game server management, gaming automation, bangumi",
        "target_skill": "minecraft-modpack-server",
        "priority": 0.25,
        "schedule_interval_hours": 48,
        "cap_pack": ["social-gaming"],
        "freshness_score": 0.5
    }
]

# Fill default review/learning fields for new domains
for d in DOMAINS:
    d.setdefault("review_schedule", {"l1": NOW[:10], "l2": NOW[:10], "l3": NOW[:10]})
    d.setdefault("learning_history", {"total_sessions": 0, "avg_quality": 0.5, "last_loop_count": 0, "consecutive_failures": 0})
    d.setdefault("knowledge_gaps_filled", [])
    d.setdefault("last_updated", NOW)

CONFIG = {
    "version": "3.0",
    "created": NOW,
    "note": "领域由 generate-night-study-config.py 自动生成，映射全部 17 个 cap-pack 包为 18 个学习领域",
    "domains": DOMAINS,
    "discovery_rules": {
        "stale_skill_threshold_days": 30,
        "gap_cluster_threshold": 3,
        "auto_create_domain": True,
        "cap_pack_sync": {
            "enabled": True,
            "source_dir": str(pathlib.Path.home() / "Hermes-Cap-Pack" / "packs"),
            "auto_add_new_packs": True
        }
    },
    "quality_threshold": {
        "min_score": 60,
        "artifact_required": True,
        "min_loops": 1,
        "max_loops": 3,
        "progressive_levels": True
    },
    "adaptive_scheduling": {
        "enabled": True,
        "max_domains_per_session": 3,
        "history_window_days": 30,
        "performance_weight": 0.4,
        "freshness_weight": 0.6,
        "consecutive_failure_penalty": 0.2,
        "review_backlog_weight": 0.15
    },
    "experience_extraction": {
        "enabled": True,
        "save_to_experiences": True,
        "auto_update_skill_refs": True,
        "min_confidence": 3
    },
    "logging": {
        "jsonl_dir": "~/.hermes/logs/night_study_sessions/",
        "summary_log": "~/.hermes/logs/night_study.log"
    },
    "knowledge_base_dir": "~/.hermes/night_study/knowledge_base/"
}

# Write config
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
config_path = CONFIG_DIR / "night_study_config_v3.json"
json.dump(CONFIG, open(config_path, "w"), ensure_ascii=False, indent=2)
print(f"✅ Config written: {config_path}")

# Create KB files for new domains
KB_DIR.mkdir(parents=True, exist_ok=True)
existing_kbs = {f.stem for f in KB_DIR.glob("*.json") if f.stem != "references"}
for d in DOMAINS:
    kid = d["id"]
    kb_path = KB_DIR / f"{kid}.json"
    if kid not in existing_kbs:
        kb_data = {
            "domain": kid,
            "domain_name": d["name"],
            "last_updated": NOW,
            "concepts": {},
            "open_questions": [],
            "session_log": []
        }
        json.dump(kb_data, open(kb_path, "w"), ensure_ascii=False, indent=2)
        print(f"  🆕 KB created: {kb_path}")
    else:
        print(f"  ✅ KB exists: {kb_path}")

print(f"\n📊 总计: {len(DOMAINS)} 个领域")
print(f"   {'+'.join(str(len([s for s in DOMAINS if s['cap_pack'].count(p)])) for p in set(sum([d['cap_pack'] for d in DOMAINS], [])))} = 覆盖全部 cap-pack")
