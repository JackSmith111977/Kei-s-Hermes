#!/usr/bin/env python3
"""
Hermes Agent 深度架构指南 v5.0 — 正常舒适版
智能分页 + 正常排版 + WQY ZenHei（无黑块）
"""

__version__ = "5.0.0"
__date__ = "2026-05-03"
__author__ = "小喵 AI"

import os, sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 注册 WQY ZenHei（唯一中文字体，无黑块）──
WQY_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
pdfmetrics.registerFont(TTFont('WQY', WQY_PATH, subfontIndex=0))
FONT = 'WQY'

# ── 正常配色（深色科技风）──
PRI = HexColor('#1a1a2e')
ACC = HexColor('#0f3460')
HIG = HexColor('#e94560')
BG_LIGHT = HexColor('#f8f9fa')
BG_CODE = HexColor('#f0f0f2')
BDR = HexColor('#d0d0d0')
GRAY = HexColor('#666666')
DK = HexColor('#222222')

# ── 资源路径 ──
ASSETS = os.path.expanduser("~/.hermes/pdf_assets")
OUT = os.path.expanduser(f"~/.hermes/Hermes_Agent_Deep_Architecture_v{__version__}.pdf")

def esc(t):
    if not t: return ""
    return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def S(name, **kw):
    return ParagraphStyle(name, fontName=FONT, **kw)

def HR(w=20, t=1.5, c=HIG):
    return HRFlowable(width=f"{w}%", thickness=t, color=c, spaceBefore=2*mm, spaceAfter=2*mm)

def T(data, cw, hc=PRI, fs=9):
    """标准表格"""
    bs = S('Tb', fontSize=fs, leading=fs*1.5, textColor=DK)
    hs = S('Th', fontSize=fs, leading=fs*1.5, textColor=white)
    pd = [[Paragraph(esc(c), hs) if r==0 else Paragraph(esc(c), bs) for c in row] for r,row in enumerate(data)]
    st = [
        ('BACKGROUND',(0,0),(-1,0),hc),
        ('TEXTCOLOR',(0,0),(-1,0),white),
        ('BOX',(0,0),(-1,-1),0.5,BDR),
        ('INNERGRID',(0,0),(-1,-1),0.3,BDR),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),2.5*mm),
        ('BOTTOMPADDING',(0,0),(-1,-1),2.5*mm),
        ('LEFTPADDING',(0,0),(-1,-1),2.5*mm),
        ('RIGHTPADDING',(0,0),(-1,-1),2.5*mm),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[white, BG_LIGHT]),
    ]
    t = Table(pd, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(st))
    return t

def IMG(path, mw=150*mm, cap=None):
    """自适应图片"""
    e = []
    if not os.path.exists(path):
        e.append(Paragraph(f'<i>[缺失: {os.path.basename(path)}]</i>', S('E', fontSize=9, textColor=GRAY)))
        return e
    img = Image(path)
    asp = img.imageWidth / img.imageHeight
    if asp > 1:
        img.drawWidth, img.drawHeight = mw, mw/asp
    else:
        img.drawHeight, img.drawWidth = mw*0.7, mw*0.7*asp
    ct = Table([[img]], colWidths=[170*mm])
    ct.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    e += [Spacer(1,2*mm), ct]
    if cap: e.append(Paragraph(esc(f"图：{cap}"), S('Ca', fontSize=8, textColor=GRAY, alignment=TA_CENTER)))
    e.append(Spacer(1,3*mm))
    return e

def CODE(text, lang="", fs=8):
    """标准代码块（直接用 ParagraphStyle 避免 fontName 冲突）"""
    e = []
    if lang:
        e.append(Paragraph(f'▎{esc(lang)}', S('Cl', fontSize=7, textColor=GRAY, spaceBefore=1.5*mm)))
    e.append(Paragraph(
        "<br/>".join(esc(l) for l in text.split('\n')),
        ParagraphStyle('Cc', fontName='WQY', fontSize=fs, leading=fs*1.5, textColor=DK,
          backColor=BG_CODE, borderPadding=(3*mm,2*mm,3*mm,2*mm),
          leftIndent=4*mm, spaceBefore=0.5*mm, spaceAfter=2.5*mm)))
    return e

# ── 正常舒适的样式（20mm 边距）──
H1 = S('H1', fontSize=20, leading=26, textColor=PRI, spaceBefore=10*mm, spaceAfter=2*mm)
H2 = S('H2', fontSize=14, leading=19, textColor=PRI, spaceBefore=6*mm, spaceAfter=1.5*mm)
H3 = S('H3', fontSize=11, leading=15, textColor=ACC, spaceBefore=4*mm, spaceAfter=1*mm)
B = S('Bd', fontSize=9.5, leading=15, textColor=DK, spaceAfter=2.5*mm, alignment=TA_JUSTIFY)
CAPTION = S('Ca', fontSize=8, leading=11, textColor=GRAY, alignment=TA_CENTER)

def IMG(path, mw=140*mm, cap=None):
    """自适应图片"""
    e = []
    if not os.path.exists(path):
        e.append(Paragraph(f'<i>[缺失: {os.path.basename(path)}]</i>', S('E', fontSize=8, textColor=GRAY)))
        return e
    img = Image(path)
    asp = img.imageWidth / img.imageHeight
    if asp > 1: img.drawWidth, img.drawHeight = mw, mw/asp
    else: img.drawHeight, img.drawWidth = mw*0.65, mw*0.65*asp
    ct = Table([[img]], colWidths=[170*mm])
    ct.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    e += [Spacer(1,2*mm), ct]
    if cap: e.append(Paragraph(esc(f"图：{cap}"), S('Ca', fontSize=7.5, textColor=GRAY, alignment=TA_CENTER)))
    e.append(Spacer(1,2*mm))
    return e

def CODE(text, lang="", fs=7):
    """紧凑代码块"""
    e = []
    if lang:
        e.append(Paragraph(f'▎{esc(lang)}', S('Cl', fontSize=6.5, textColor=GRAY, spaceBefore=1*mm)))
    e.append(Paragraph(
        "<br/>".join(esc(l) for l in text.split('\n')),
        ParagraphStyle('Cc', fontName='WQY', fontSize=fs, leading=fs*1.5, textColor=DK,
          backColor=BG_CODE, borderPadding=(2*mm,1.5*mm,2*mm,1.5*mm),
          leftIndent=3*mm, spaceBefore=0.5*mm, spaceAfter=2*mm)))
    return e

# ── 紧凑样式 (15mm 边距, 更小字号) ──
H1 = S('H1', fontSize=16, leading=21, textColor=PRI, spaceBefore=5*mm, spaceAfter=1.5*mm)
H2 = S('H2', fontSize=12, leading=16, textColor=PRI, spaceBefore=4*mm, spaceAfter=1*mm)
H3 = S('H3', fontSize=10, leading=14, textColor=ACC, spaceBefore=3*mm, spaceAfter=0.5*mm)
B = S('Bd', fontSize=8.5, leading=13, textColor=DK, spaceAfter=1.5*mm, alignment=TA_JUSTIFY)
BI = S('Bi', fontSize=8.5, leading=13, textColor=ACC, spaceAfter=1*mm, leftIndent=3*mm,
       borderPadding=(1*mm,0.5*mm,1*mm,0.5*mm), backColor=HexColor('#eef0ff'))
NOTE = S('Nt', fontSize=8, leading=12, textColor=ACC, leftIndent=3*mm,
          borderPadding=(1*mm,0.5*mm,1*mm,0.5*mm), backColor=HexColor('#f0f4ff'), spaceBefore=1*mm, spaceAfter=1*mm)

# ═══════════════════════════════════════
# 封面
# ═══════════════════════════════════════
def COVER():
    e = [Spacer(1,25*mm)]
    e.append(Paragraph('<b>Hermes Agent</b>', S('Ct', fontSize=28, leading=34, textColor=PRI, alignment=TA_CENTER)))
    e.append(Paragraph('<b>深度架构指南</b>', S('Cs', fontSize=18, leading=24, textColor=HIG, alignment=TA_CENTER)))
    e.append(Spacer(1,6*mm))
    e.append(HRFlowable(width="50%", thickness=1.5, color=HIG, spaceBefore=2*mm, spaceAfter=2*mm))
    e.append(Spacer(1,4*mm))
    e.append(Paragraph(
        '从核心循环到工具系统 · Provider 管理 · 记忆系统 · 技能体系 · 平台网关 · 运维部署',
        S('Cd', fontSize=10, leading=15, textColor=GRAY, alignment=TA_CENTER)))
    e.append(Spacer(1,10*mm))
    # 信息
    def il(k,v): return [Paragraph(f'<b>{esc(k)}</b>', S('il', fontSize=9, textColor=GRAY, alignment=TA_RIGHT)),
                          Paragraph(esc(v), S('iv', fontSize=9, textColor=DK))]
    info = Table([il("版本", f"v{__version__}"), il("日期", __date__),
                  il("作者", __author__), il("技术栈", "ReportLab + WQY + Mermaid CLI")],
                 colWidths=[30*mm, 70*mm])
    info.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                               ('TOPPADDING',(0,0),(-1,-1),1.5*mm),('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm)]))
    ct = Table([[info]], colWidths=[160*mm])
    ct.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')]))
    e.extend([Spacer(1,15*mm), ct, PageBreak()])
    return e

def TOC():
    e = [Paragraph('<b>目 录</b>', H1), HR(15,1.5), Spacer(1,2*mm)]
    chs = [("1","Hermes Agent 概览"),("2","系统架构总览"),("3","核心循环"),
           ("4","Provider 与 Fallback 机制"),("5","工具系统"),("6","记忆系统"),
           ("7","技能系统"),("8","消息平台网关"),("9","定时任务"),
           ("10","子代理与并行"),("11","安全机制"),("12","配置系统"),
           ("13","Auxiliary AI 服务"),("14","模型与 Token 管理"),("15","开发与调试"),
           ("16","部署与运维"),("","附录")]
    for n,t in chs:
        p = f"<b>{n}. {esc(t)}</b>" if n else f"<b>{esc(t)}</b>"
        e.append(Paragraph(p, S('Tc', fontSize=9.5, leading=15, textColor=DK, leftIndent=5*mm if not n else 0)))
    e.append(PageBreak())
    return e

def CH1():
    e = [Paragraph('<b>第 1 章　Hermes Agent 概览</b>', H1), HR()]
    e.append(Paragraph('Hermes Agent 由 Nous Research 开发，是一个生产级 AI Agent 系统。它以希腊信使神 Hermes 命名，'
                       '支持通过 CLI、Telegram、Discord、微信、飞书、WhatsApp、Signal 等多平台交互，'
                       '具备工具调用、持久化记忆、定时任务、上下文压缩、多模型切换等核心能力。', B))
    e.append(Paragraph('<b>1.1　核心特性</b>', H2))
    e.append(T([
        ["特性","描述","实现"],
        ["多平台网关","20+ 消息平台统一接入","Gateway + Adapter"],
        ["工具调用循环","自动执行工具直至完成","registry + function_call"],
        ["持久化记忆","SQLite + FTS5 跨会话检索","memory + session_search"],
        ["上下文压缩","长话自动压缩 Token","context_compressor"],
        ["Provider 容灾","主备模型自动切换","fallback_providers"],
        ["子代理并行","独立上下文执行子任务","delegate_task"],
        ["技能体系","可插拔专业知识包","SKILL.md 自动发现"],
        ["定时任务","Cron 调度 · 多目标投递","cronjob + scheduler"],
        ["安全机制","敏感命令审批 + TIRITH","approval + tirith"],
        ["MCP 支持","标准化外部工具协议","MCP Client"],
    ],[25*mm,58*mm,45*mm], PRI, 9))
    e.append(Spacer(1,2*mm))

    e.append(Paragraph('<b>1.2　适用场景</b>', H2))
    e.append(T([
        ["场景","示例","推荐平台"],
        ["代码开发","Debug/重构/文档","CLI/VS Code"],
        ["办公助手","邮件/文档/报告","飞书/Discord"],
        ["信息搜集","搜索/抓取/监控","Telegram"],
        ["自动化运维","定时脚本/部署","CLI/Cron"],
        ["学习研究","论文/调研/整理","任意平台"],
    ],[25*mm,60*mm,45*mm], PRI, 9))
    e.append(PageBreak())
    return e

def CH2():
    e = [Paragraph('<b>第 2 章　系统架构总览</b>', H1), HR()]
    e.append(Paragraph('Hermes 采用五层分层架构，每层职责清晰、接口明确：用户层 → 网关层 → 核心层 → Provider 层 → 工具层。', B))
    e.extend(IMG(os.path.join(ASSETS,'arch_overview.png'), 145*mm, "整体架构图"))
    e.append(Paragraph('<b>2.1　数据流路径</b>', H2))
    for s in ["用户 → Gateway 接收 → Session 恢复 → Agent 循环 → Provider 调用 → 工具执行 → 结果返回"]:
        e.append(Paragraph(f'▪ {esc(s)}', B))
    e.append(Paragraph('<b>2.2　关键设计</b>', H2))
    e.append(T([
        ["决策项","选择","理由"],
        ["循环模式","同步","避免回调地狱，简化错误处理"],
        ["消息格式","OpenAI Chat","广泛兼容各类 Provider"],
        ["工具加载","注册制","运行时动态加载"],
        ["技能存储","Markdown 文件","Git 友好，零依赖"],
        ["状态存储","SQLite","单文件，易备份迁移"],
    ],[25*mm,30*mm,75*mm], PRI, 9))
    e.append(PageBreak())
    return e

def CH3():
    e = [Paragraph('<b>第 3 章　核心循环</b>', H1), HR()]
    e.append(Paragraph('run_conversation() 是 Hermes 的心脏——一个完全同步的循环。每次迭代调用 Provider API、处理工具响应，直到模型返回文本或达到迭代限制。', B))
    e.extend(IMG(os.path.join(ASSETS,'core_loop.png'), 110*mm, "核心循环流程"))
    e.append(Paragraph('<b>3.1　消息格式</b>', H2))
    e.extend(CODE('messages = [\n'
        '  {"role":"system","content":"系统提示..."},\n'
        '  {"role":"user","content":"用户消息"},\n'
        '  {"role":"assistant","content":"回复","tool_calls":[...]},\n'
        '  {"role":"tool","content":"结果","tool_call_id":"..."},\n'
        ']', "JSON"))
    e.append(Paragraph('<b>3.2　关键代码</b>', H2))
    e.extend(CODE(
        'while api_count < max_iterations:\n'
        '    resp = client.chat.completions.create(\n'
        '        model=model,messages=messages,tools=schemas\n'
        '    )\n'
        '    if resp.tool_calls:\n'
        '        for tc in resp.tool_calls:\n'
        '            result = handle_function_call(tc.name,tc.args)\n'
        '            messages.append(tool_result(result))\n'
        '    else:\n'
        '        return resp.content', "Python 伪代码"))
    return e

def CH4():
    e = [Paragraph('<b>第 4 章　Provider 与 Fallback</b>', H1), HR()]
    e.append(Paragraph('Provider 层通过 resolve_provider_client() 统一路由，支持任意 OpenAI 兼容端点和多级 Fallback 链。', B))
    e.extend(CODE(
        'providers:\n'
        '  qwencode:\n'
        '    base_url: https://coding.dashscope.aliyuncs.com/v1\n'
        '    key_env: QWENCODE_API_KEY\n'
        '    model: qwen3.6-plus\n'
        'fallback_providers:\n'
        '  - provider: custom_longCat\n'
        '    model: LongCat-2.0-Preview\n'
        '    key_env: CUSTOM_LONGCAT_API_KEY\n'
        '  - provider: deepseek\n'
        '    model: deepseek-v4-flash\n'
        '    key_env: DEEPSEEK_API_KEY', "YAML"))
    e.extend(IMG(os.path.join(ASSETS,'fallback_flow.png'), 145*mm, "Fallback 容灾"))
    e.append(Paragraph('<b>4.1　429 处理优先级</b>', H2))
    e.append(T([
        ["优先级","操作","条件"],
        ["最高","凭证池换 Key","有其他 API Key 时"],
        ["高","Fallback LongCat","池耗尽后"],
        ["中","Fallback DeepSeek","LongCat 失败"],
        ["低","指数退避","全部失败后等待"],
    ],[20*mm,35*mm,75*mm], PRI, 9))
    return e

def CH5():
    e = [Paragraph('<b>第 5 章　工具系统</b>', H1), HR()]
    e.append(Paragraph('工具通过 tools/registry.py 注册。每个工具 import 时调用 registry.register()，运行时由 model_tools.py 统一发现。', B))
    e.append(Paragraph('<b>5.1　核心工具</b>', H2))
    e.append(T([
        ["工具","功能","参数"],
        ["terminal","执行 Shell","command, timeout"],
        ["read_file","读取文件","path, offset"],
        ["write_file","写入文件","path, content"],
        ["search_files","搜索文件","pattern, target"],
        ["patch","查找替换","path, old, new"],
        ["session_search","会话搜索","query, limit"],
        ["memory","持久记忆","action, target"],
        ["execute_code","Python 沙箱","code"],
        ["delegate_task","子代理","goal, toolsets"],
        ["cronjob","定时任务","action, prompt"],
        ["image_generate","AI 生图","prompt"],
        ["browser_*","浏览器自动","url, click等"],
    ],[25*mm,45*mm,50*mm], PRI, 9))
    return e

def CH6():
    e = [Paragraph('<b>第 6 章　记忆系统</b>', H1), HR()]
    e.append(Paragraph('Hermes 的记忆分为两层：持久记忆（跨会话）和会话搜索（FTS5 全文索引）。', B))
    e.append(T([
        ["记忆类型","存储","注入时机","保留策略"],
        ["用户画像","memory(user)","每次会话","主动更新"],
        ["工作记忆","memory(memory)","每次会话","Agent 更新"],
        ["会话历史","SQLite DB","按需检索","自动过期"],
        ["上下文缓存","压缩引擎","长话自动","LRU 淘汰"],
    ],[25*mm,30*mm,35*mm,40*mm], PRI, 9))
    e.append(Paragraph('<b>6.1　上下文压缩</b>', H2))
    e.append(Paragraph('context_compressor 在会话超过 50% Token 上限时自动触发，使用 AI 摘要压缩早期对话，目标压缩比 20%，最后 20 条消息始终保留。', B))
    e.extend(CODE(
        'compression:\n'
        '  enabled: true\n'
        '  threshold: 0.5\n'
        '  target_ratio: 0.2\n'
        '  protect_last_n: 20', "YAML"))
    return e

def CH7():
    e = [Paragraph('<b>第 7 章　技能系统</b>', H1), HR()]
    e.append(Paragraph('Skill 是 Hermes 的"可复用专业知识包"。每个 Skill 包含 SKILL.md 文件，描述了在特定场景下的知识、工作流和注意事项。', B))
    e.extend(IMG(os.path.join(ASSETS,'skills_flow.png'), 130*mm, "Skills 流程"))
    e.append(T([
        ["类型","描述","示例"],
        ["索引","聚合原子 Skill 的入口","doc-design"],
        ["原子","单一领域知识包","pdf-layout, feishu"],
        ["学习","学习方法论 Meta","learning"],
        ["元 Skill","管理其他 Skill","skill-creator"],
    ],[22*mm,55*mm,55*mm], PRI, 9))
    return e

def CH8():
    e = [Paragraph('<b>第 8 章　消息平台网关</b>', H1), HR()]
    e.append(Paragraph('Gateway（gateway/run.py）是多平台消息路由中枢。每个平台通过 Adapter 接口接入，负责认证、消息格式转换、文件处理和会话管理。', B))
    e.append(T([
        ["平台","独特功能","限制"],
        ["Telegram","话题分组 BotCommand","50MB 文件"],
        ["Discord","斜杠命令 自动线程","2000 字符"],
        ["飞书","富文本 多维表格","API 频率"],
        ["微信","公众号回复","被动窗口期"],
        ["Signal","端到端加密","群组受限"],
        ["WhatsApp","广泛用户基础","格式受限"],
    ],[25*mm,55*mm,50*mm], PRI, 9))
    return e

def CH9():
    e = [Paragraph('<b>第 9 章　定时任务</b>', H1), HR()]
    e.append(Paragraph('Hermes 内置 Cron 调度器，支持间隔/Cron 表达式，可投递到任意平台。', B))
    e.extend(CODE(
        "# 每 40 分钟飞书播报\n"
        "cronjob(action='create', prompt='汇报...',\n"
        "        schedule='40m',\n"
        "        deliver='feishu:chat_id')\n"
        "# 每天 12:00 部署\n"
        "cronjob(action='create', prompt='部署...',\n"
        "        schedule='0 12 * * *')", "Python"))
    e.append(Paragraph('<b>9.1　静默机制</b>', H2))
    e.append(Paragraph('通过 prompt 中注入 [SILENT] 标记，00:00-07:59 返回 [SILENT] 抑制投递，无需多组 Cron 表达式。', B))
    return e

def CH10():
    e = [Paragraph('<b>第 10 章　子代理与并行</b>', H1), HR()]
    e.append(Paragraph('delegate_task 允许 Agent 派发独立任务给子 Agent，各拥有独立上下文和终端。', B))
    e.extend(CODE(
        "results = delegate_task(\n"
        '    tasks=[\n'
        '        {"goal":"研究A","toolsets":["web"]},\n'
        '        {"goal":"分析B","toolsets":["terminal"]},\n'
        "    ]\n"
        ")  # 并行执行", "Python"))
    e.append(Paragraph('<b>10.1　限制</b>', H2))
    for l in ["共享父 Agent 的迭代预算","不能调用 delegate_task/clarify/memory","需通过 context 传参","最多 3 个并行"]:
        e.append(Paragraph(f'▪ {esc(l)}', B))
    return e

def CH11():
    e = [Paragraph('<b>第 11 章　安全机制</b>', H1), HR()]
    e.append(Paragraph('Hermes 内置多层安全防护。approval.py 维护高危命令审批，TIRITH 策略引擎在运行时对工具调用进行安全策略检查。', B))
    e.extend(CODE(
        'command_allowlist:\n'
        '- shell command via -c/-lc flag\n'
        '- delete in root path\n'
        '- kill hermes/gateway process', "YAML"))
    e.append(Paragraph('隐私保护：redact_pii 自动脱敏；website_blocklist 支持域名拦截；日志中 secrets 自动替换。', B))
    # CH11 → CH12：配置系统是新板块，保留分页
    e.append(PageBreak())
    return e

def CH12():
    e = [Paragraph('<b>第 12 章　配置系统</b>', H1), HR()]
    e.append(Paragraph('配置分为 config.yaml（非敏感）和 .env（敏感凭证）。v5.0 中所有 Key 已迁入 .env，通过 key_env 引用。', B))
    e.extend(CODE(
        '~/.hermes/\n'
        '├── config.yaml    # 非敏感设置\n'
        '├── .env           # 凭证（已 .gitignore）\n'
        '├── .gitignore     # 安全防护\n'
        '├── skills/        # 自定义技能\n'
        '├── cron/          # 定时任务\n'
        '└── scripts/       # 工具脚本', "目录结构"))
    e.append(Paragraph('凭证池通过 auth.json 持久化凭证状态，含 source/auth_type/access_token/base_url/last_status。耗尽后自动触发 Fallback。', B))
    e.append(PageBreak())
    return e

def CH13():
    e = [Paragraph('<b>第 13 章　Auxiliary AI 服务</b>', H1), HR()]
    e.append(Paragraph('Auxiliary 是 Hermes 的"辅助 AI 大脑"，处理主循环之外的专用任务。', B))
    e.append(T([
        ["服务","用途","超时"],
        ["Vision","图片分析","120s"],
        ["Web Extract","网页提取","360s"],
        ["Compression","上下文压缩","120s"],
        ["Session Search","历史检索","30s"],
        ["Title Gen","标题生成","30s"],
    ],[30*mm,55*mm,25*mm], PRI, 9))
    return e

def CH14():
    e = [Paragraph('<b>第 14 章　模型与 Token 管理</b>', H1), HR()]
    e.append(Paragraph('model_metadata.py 管理各模型的上下文长度。Token 估算有两种路径：tiktoken（精确计数）和启发式（字符×系数）。', B))
    e.append(Paragraph('Prompt Caching：对支持缓存的 Provider 自动利用。Skill 通过用户消息注入以保持缓存命中率。reasoning_effort 支持 medium。', B))
    return e

def CH15():
    e = [Paragraph('<b>第 15 章　开发与调试</b>', H1), HR()]
    e.append(Paragraph('基于 Python 3.12+，同步循环模式。约 3000 测试覆盖核心循环、凭证池、配置验证、CLI 命令和 Gateway。', B))
    e.extend(CODE(
        'cd ~/.hermes/hermes-agent\n'
        'source venv/bin/activate\n'
        'pytest tests/ -x -v\n'
        'python cli.py --dev', "Bash"))
    e.append(Paragraph('ACP 集成支持 VS Code / Zed / JetBrains 等 IDE。persistent_shell 确保终端状态跨调用保持。', B))
    return e

def CH16():
    e = [Paragraph('<b>第 16 章　部署与运维</b>', H1), HR()]
    e.append(T([
        ["后端","场景","特点"],
        ["local","日常使用","零配置"],
        ["docker","容器化","环境隔离"],
        ["ssh","远程","无需安装 Agent"],
        ["modal","云沙箱","按需计费"],
        ["daytona","工作空间","即服务"],
    ],[22*mm,55*mm,55*mm], PRI, 9))
    e.append(Paragraph('Gateway 支持 restart_drain_timeout(60s) 优雅重启。添加平台配置后重启 Gateway 即可生效，遵循"配置即声明"原则。', B))
    e.append(PageBreak())
    return e

def APPENDIX():
    e = [Paragraph('<b>附录</b>', H1), HR()]
    e.append(Paragraph('<b>A.1　版本历史</b>', H2))
    e.append(T([
        ["版本","日期","变更"],
        ["v5.0.0","2026-05-03","Mermaid 图 · key_env 安全 · 16 章"],
        ["v4.0.0","2026-04-20","模块化 Skill · V4 引擎"],
        ["v3.0.0","2026-04-10","飞书集成 · 定时任务"],
        ["v2.0.0","2026-03-25","Fallback · 凭证池 · Gateway"],
        ["v1.0.0","2026-03-01","初版架构介绍"],
    ],[15*mm,25*mm,90*mm], PRI, 9))
    e.append(Spacer(1,3*mm))
    e.append(Paragraph('<b>A.2　术语表</b>', H2))
    e.append(T([
        ["术语","解释"],
        ["ACP","Agent 通信协议"],
        ["Credential Pool","多 API Key 缓冲区"],
        ["Gateway","多平台路由中枢"],
        ["MCP","模型上下文协议"],
        ["Provider","LLM 服务提供商"],
        ["Skill","可复用专业知识包"],
    ],[30*mm,100*mm], PRI, 9))
    e.append(Spacer(1,5*mm))
    e.append(HRFlowable(width="50%", thickness=1, color=HIG, spaceBefore=2*mm, spaceAfter=2*mm))
    e.append(Paragraph('<i>本文档由小喵 AI 使用 ReportLab + WQY + Mermaid CLI 自动生成</i>',
                        S('Fs', fontSize=8, textColor=GRAY, alignment=TA_CENTER)))
    return e

# ═══════════════════════════════════════
# 页眉页脚
# ═══════════════════════════════════════
def HF(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(15*mm, A4[1]-10*mm, "Hermes Agent 深度架构指南")
    canvas.drawRightString(A4[0]-15*mm, A4[1]-10*mm, datetime.now().strftime("%Y-%m-%d"))
    canvas.setStrokeColor(BDR)
    canvas.setLineWidth(0.3)
    canvas.line(15*mm, A4[1]-12*mm, A4[0]-15*mm, A4[1]-12*mm)
    canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
    pn = canvas.getPageNumber()
    canvas.drawCentredString(A4[0]/2, 7*mm, f"— {pn} —")
    canvas.drawRightString(A4[0]-15*mm, 7*mm, f"v{__version__}")
    canvas.restoreState()

def FP(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GRAY)
    canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
    pn = canvas.getPageNumber()
    canvas.drawCentredString(A4[0]/2, 7*mm, f"— {pn} —")
    canvas.restoreState()

# ═══════════════════════════════════════
# 主入口
# ═══════════════════════════════════════
def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm, topMargin=16*mm, bottomMargin=16*mm,
        title='Hermes Agent 深度架构指南', author=__author__,
        subject='Hermes Agent 完整技术架构解析（16章 + 附录）',
        keywords=['Hermes','AI Agent','架构','ReportLab','WQY'])

    story = []
    story.extend(COVER())
    story.extend(TOC())
    story.extend(CH1()); story.extend(CH2()); story.extend(CH3()); story.extend(CH4())
    story.extend(CH5()); story.extend(CH6()); story.extend(CH7()); story.extend(CH8())
    story.extend(CH9()); story.extend(CH10()); story.extend(CH11()); story.extend(CH12())
    story.extend(CH13()); story.extend(CH14()); story.extend(CH15()); story.extend(CH16())
    story.extend(APPENDIX())

    doc.build(story, onFirstPage=FP, onLaterPages=HF)
    sz = os.path.getsize(OUT)/1024
    print(f"✅ PDF 生成成功！({sz:.0f}KB, {doc.page}页)")

if __name__ == "__main__":
    build()
