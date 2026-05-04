#!/usr/bin/env python3
"""
skill_finder_v2.py - 增强版 Agent Skill 发现雷达
用法:
  python3 ~/.hermes/skills/learning-workflow/scripts/skill_finder_v2.py "我想画个架构图"
  
改进:
  1. 全文索引（不仅扫描元数据，还扫描 SKILL.md 正文）
  2. TF-IDF 风格加权（词频 * 逆文档频率）
  3. 同义词扩展（内置常见映射表）
  4. 触发词短语匹配（支持完整短语而不只是子串）
  5. 缓存机制（避免重复解析 SKILL.md）
"""

import os
import sys
import glob
import json
import hashlib
import math
from pathlib import Path
from collections import Counter

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")
CACHE_FILE = os.path.expanduser("~/.hermes/.skill_index_cache.json")

# 同义词扩展映射表（中英双语）
SYNONYMS = {
    "画图": ["draw", "diagram", "chart", "graph", "可视化", "图表", "绘图"],
    "架构": ["architecture", "design", "system", "结构", "设计"],
    "架构图": ["architecture", "diagram", "architecture diagram", "架构设计"],
    "文档": ["document", "doc", "pdf", "word", "docx", "文档生成"],
    "搜索": ["search", "crawl", "scrape", "fetch", "抓取", "爬取", "网页"],
    "邮件": ["email", "mail", "message", "消息", "email"],
    "定时": ["schedule", "cron", "timer", "定时任务", "计划", "周期性"],
    "部署": ["deploy", "publish", "upload", "发布", "上传", "同步"],
    "测试": ["test", "verify", "check", "validate", "验证", "单元测试"],
    "学习": ["learn", "study", "research", "train", "研究", "训练", "探索"],
    "文件": ["file", "organize", "manage", "整理", "管理", "分类"],
    "代理": ["proxy", "mihomo", "clash", "sing-box", "代理配置"],
    "翻译": ["translate", "convert", "转换", "翻译"],
    "ppt": ["powerpoint", "presentation", "幻灯片", "演示", "pptx"],
    "excel": ["spreadsheet", "excel", "表格", "xlsx", "电子表格"],
    "视频": ["video", "animation", "manim", "动画", "视频"],
    "像素": ["pixel", "pixel-art", "像素画", "retro"],
    "ASCII": ["ascii", "ascii-art", "字符画", "文本艺术"],
    "歌曲": ["song", "music", "歌曲", "歌词", "suno"],
    "落地页": ["landing page", "web design", "网页设计", "stripe style"],
    "手绘": ["excalidraw", "hand-drawn", "手绘风格", "草图"],
    "信息图": ["infographic", "baoyu", "信息图", "可视化摘要"],
}


def load_cache():
    """加载缓存"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_cache(cache_data):
    """保存缓存"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except:
        pass


def compute_file_hash(filepath):
    """计算文件哈希用于缓存失效检测"""
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            h.update(f.read())
        return h.hexdigest()
    except:
        return None


def load_skill_full(skill_path, cache):
    """加载技能全文（带缓存）"""
    file_hash = compute_file_hash(skill_path)
    cache_key = f"{skill_path}:{file_hash}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    # 解析 SKILL.md
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        meta = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                import yaml
                meta = yaml.safe_load(parts[1]) or {}
                body = parts[2] if len(parts) > 2 else ""
        
        # 提取关键词：元数据 + 正文前 1000 字符
        text = f"{meta.get('name', '')} {meta.get('description', '')} {body[:1000]}".lower()
        
        result = {
            'meta': meta,
            'text': text,
            'triggers': meta.get('triggers', []),
            'name': meta.get('name', 'Unknown'),
        }
        
        cache[cache_key] = result
        return result
    except Exception as e:
        return None


def expand_query(query):
    """扩展查询词（同义词 + 中英文分词）"""
    import re
    
    # 中英文混合分词
    # 1. 提取英文单词（连续字母/数字/连字符）
    english_words = re.findall(r'[a-zA-Z0-9_-]+', query.lower())
    
    # 2. 提取中文字符（逐个字符或2-3字短语）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', query.lower())
    chinese_words = []
    for ch_text in chinese_chars:
        # 添加整个中文短语
        chinese_words.append(ch_text)
        # 添加2-3字组合
        for i in range(len(ch_text)):
            for j in range(2, 4):  # 2-3字词
                if i + j <= len(ch_text):
                    chinese_words.append(ch_text[i:i+j])
    
    # 合并所有词
    all_words = set(english_words + chinese_words)
    
    # 同义词扩展
    expanded = set(all_words)
    for word in list(expanded):
        if word in SYNONYMS:
            expanded.update(SYNONYMS[word])
    
    return list(expanded)


def compute_idf(all_texts, term):
    """计算逆文档频率"""
    doc_count = len(all_texts)
    term_count = sum(1 for text in all_texts if term in text)
    if term_count == 0:
        return 0
    return math.log(doc_count / term_count)


def score_skill_v2(query, skill_data, idf_cache):
    """增强版评分算法"""
    query_words = expand_query(query)
    query_lower = query.lower()
    score = 0
    
    skill_name = skill_data['name'].lower()
    skill_text = skill_data['text']
    triggers = skill_data['triggers']
    
    # 1. 名称精确匹配 (Weight 100)
    if skill_name in query_lower or query_lower in skill_name:
        score += 100
    
    # 2. 触发词匹配 (Weight 80 per trigger)
    for trigger in triggers:
        trigger_lower = trigger.lower()
        # 完整短语匹配
        if trigger_lower in query_lower:
            score += 80
        # 触发词包含查询词
        elif query_lower in trigger_lower:
            score += 60
        # 部分关键词匹配
        else:
            for word in query_words:
                if len(word) > 1 and word in trigger_lower:
                    score += 20
    
    # 3. TF-IDF 风格正文匹配
    for word in query_words:
        if len(word) < 2:
            continue
        
        # 词频
        tf = skill_text.count(word)
        if tf > 0:
            # 逆文档频率（近似）
            idf = idf_cache.get(word, 1.0)
            score += tf * idf * 5
    
    # 4. 描述词匹配 (Weight 15 per word)
    desc = skill_data['meta'].get('description', '').lower()
    for word in query_words:
        if len(word) > 1 and word in desc:
            score += 15
    
    return score


def build_idf_cache(all_skills_text):
    """构建 IDF 缓存"""
    idf = {}
    all_terms = set()
    for text in all_skills_text:
        words = text.split()
        all_terms.update(words)
    
    for term in all_terms:
        doc_count = len(all_skills_text)
        term_count = sum(1 for text in all_skills_text if term in text)
        if term_count > 0:
            idf[term] = math.log(doc_count / term_count)
    
    return idf


def main():
    if len(sys.argv) < 2:
        print("用法: skill_finder_v2.py '查询词'")
        sys.exit(1)
    
    query = sys.argv[1]
    cache = load_cache()
    results = []
    all_texts = []
    
    # 第一遍：加载所有技能
    sk_files = glob.glob(os.path.join(SKILLS_DIR, '**/SKILL.md'), recursive=True)
    
    for f in sk_files:
        data = load_skill_full(f, cache)
        if data:
            results.append({
                'data': data,
                'path': f,
            })
            all_texts.append(data['text'])
    
    # 构建 IDF 缓存
    idf_cache = build_idf_cache(all_texts)
    
    # 第二遍：评分
    scored = []
    for r in results:
        s = score_skill_v2(query, r['data'], idf_cache)
        if s > 0:
            scored.append({
                'score': s,
                'name': r['data']['name'],
                'desc': r['data']['meta'].get('description', 'No description'),
                'path': r['path'],
            })
    
    # 排序
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    # 输出
    print(f"🔍 增强扫描完成！查询: '{query}'")
    print(f"📊 共扫描 {len(results)} 个 Skill，{len(scored)} 个匹配\n")
    
    found_good = False
    for i, r in enumerate(scored[:5]):
        icon = "✅" if r['score'] >= 50 else "💡" if r['score'] >= 20 else "❓"
        print(f"{i+1}. {icon} {r['name']} (匹配度：{r['score']:.0f})")
        print(f"   📄 {r['desc']}")
        print(f"   📂 {r['path']}")
        print()
        if r['score'] >= 50:
            found_good = True
    
    if not found_good:
        print("⚠️ 未找到高匹配度 Skill，建议使用 learning-workflow 联网搜索。")
    
    # 保存缓存
    save_cache(cache)


if __name__ == "__main__":
    main()
