#!/usr/bin/env python3
"""生成 Hermes Agent 架构指南 PDF - 中文版"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

def find_cjk_fonts():
    """查找中文字体，优先 TrueType (.ttf)，排除 CFF/OTF 轮廓的 .ttc"""
    import struct
    search_paths = [
        "/usr/share/fonts/truetype/wqy/",
        "/usr/share/fonts/truetype/noto/",
        "/usr/share/fonts/noto-cjk/",
        "/usr/share/fonts/opentype/noto/",  # 放最后，因为多是 CFF
    ]
    regular = bold = None
    for sp in search_paths:
        if not os.path.exists(sp):
            continue
        for f in os.listdir(sp):
            fp = os.path.join(sp, f)
            fl = f.lower()
            # 跳过非 ttf/ttc 文件
            if not (f.endswith('.ttf') or f.endswith('.ttc')):
                continue
            # 快速检测：CFF 轮廓的 TTC 文件跳过
            if f.endswith('.ttc') and _is_cff_ttc(fp):
                continue
            if 'cjk' in fl or 'wqy' in fl or 'notosanssc' in fl:
                if 'bold' in fl and not bold:
                    bold = fp
                elif 'regular' in fl and not regular:
                    regular = fp
                elif not regular:
                    regular = fp
    if not regular:
        for sp in search_paths:
            if not os.path.exists(sp):
                continue
            for f in os.listdir(sp):
                fp = os.path.join(sp, f)
                if 'DejaVuSans' in f and f.endswith('.ttf'):
                    regular = fp
                    bold = os.path.join(sp, f.replace('Sans', 'Sans-Bold'))
                    return regular, bold
    return regular, bold

def _is_cff_ttc(filepath):
    """检测 TTC 文件是否包含 CFF 轮廓（reportlab 不支持）"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(4)
            if header != b'ttcf':
                return False
            # 读取第一个 subfont 的 offset table
            f.read(4)  # numFonts
            first_offset = struct.unpack('>I', f.read(4))[0]
            f.seek(first_offset)
            sf_version = f.read(4)
            # CFF 轮廓的 sfVersion 是 0x4F54544F ('OTTO')
            return sf_version == b'OTTO'
    except:
        return False

# ═══ 字体注册 ═══
# 使用 CIDFont 支持完整的 CJK 字符集（避免黑色方块问题）
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
BODY_FONT = "STSong-Light"
BOLD_FONT = "STSong-Light"  # CIDFont 不支持 bold，通过样式区分层次

PRIMARY = HexColor('#1a1a2e')
SECONDARY = HexColor('#16213e')
ACCENT = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f8f9fa')
MEDIUM_GRAY = HexColor('#6c757d')
DARK_TEXT = HexColor('#212529')
CODE_BG = HexColor('#f4f4f4')
BORDER_COLOR = HexColor('#dee2e6')

def S(name, **kw):
    return ParagraphStyle(name, fontName=BODY_FONT, **kw)
# SB 已废弃：wqy-zenhei.ttc 不支持 bold/italic 属性映射
# 统一使用 S()，通过字号和颜色区分层次
def SB(name, **kw):
    return ParagraphStyle(name, fontName=BODY_FONT, **kw)
def esc(text):
    if not text: return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def h1(t): return Paragraph(esc(t), h1_style)
def h2(t): return Paragraph(esc(t), h2_style)
def h3(t): return Paragraph(esc(t), h3_style)
def body(t): return Paragraph(esc(t), body_style)
def bullet(t): return Paragraph(f'&#8222; {esc(t)}', bullet_style)
def sp(h=3*mm): return Spacer(1, h)
def hr(color=BORDER_COLOR, thickness=1, width="100%"):
    return HRFlowable(width=width, thickness=thickness, color=color, spaceAfter=3*mm, spaceBefore=2*mm)

def make_table(data, col_widths, header_color=PRIMARY, row_colors=None, font_style=None):
    # 将所有字符串单元格转换为 Paragraph 对象，确保使用中文字体
    if font_style is None:
        font_style = body_style
    processed_data = []
    for row in data:
        processed_row = []
        for cell in row:
            if isinstance(cell, str):
                processed_row.append(Paragraph(esc(cell), font_style))
            else:
                processed_row.append(cell)
        processed_data.append(processed_row)
    
    t = Table(processed_data, colWidths=col_widths)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3*mm),
    ]
    if row_colors:
        for i, c in enumerate(row_colors):
            style.append(('BACKGROUND', (0, i+1), (-1, i+1), c))
    else:
        style.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]))
    t.setStyle(TableStyle(style))
    return t

def hp(t, style=None):
    if style is None: style = body_style
    return Paragraph(esc(t), style)

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title='Hermes Agent 架构指南',
        author='小喵 AI'
    )

    global title_style, subtitle_style, h1_style, h2_style, h3_style, body_style, bullet_style
    title_style = SB('Title2', fontSize=28, leading=34, textColor=PRIMARY, spaceAfter=6*mm, alignment=TA_CENTER)
    subtitle_style = S('Subtitle', fontSize=14, leading=20, textColor=MEDIUM_GRAY, spaceAfter=20*mm, alignment=TA_CENTER)
    h1_style = SB('H1', fontSize=20, leading=26, textColor=PRIMARY, spaceBefore=12*mm, spaceAfter=4*mm)
    h2_style = SB('H2', fontSize=15, leading=20, textColor=ACCENT, spaceBefore=8*mm, spaceAfter=3*mm)
    h3_style = SB('H3', fontSize=12, leading=16, textColor=SECONDARY, spaceBefore=5*mm, spaceAfter=2*mm)
    body_style = S('Body2', fontSize=10, leading=16, textColor=DARK_TEXT, spaceAfter=3*mm, alignment=TA_JUSTIFY)
    bullet_style = S('Bullet', fontSize=10, leading=15, textColor=DARK_TEXT, spaceAfter=2*mm, leftIndent=10*mm, bulletIndent=5*mm)

    story = []

    # ═══ 封面 ═══
    story += [sp(40*mm), hp("Hermes Agent", title_style),
              hp("架构深度解析与设计哲学", subtitle_style),
              sp(10*mm), hr(HIGHLIGHT, 2, "60%"),
              hp("2026年5月 - 小喵出品", S('Date', fontSize=11, textColor=MEDIUM_GRAY, alignment=TA_CENTER)),
              sp(15*mm)]

    info_data = [
        [hp("版本", SB('Box', fontSize=9)), hp("v1.0.0", S('Box', fontSize=9))],
        [hp("日期", SB('Box', fontSize=9)), hp("2026-05-03", S('Box', fontSize=9))],
        [hp("代码规模", SB('Box', fontSize=9)), hp("12,000+ 行 Python", S('Box', fontSize=9))],
        [hp("架构", SB('Box', fontSize=9)), hp("六层模块化设计", S('Box', fontSize=9))],
    ]
    info_table = Table(info_data, colWidths=[40*mm, 60*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 4*mm),
    ]))
    story.append(info_table)
    story.append(PageBreak())

    # ═══ 目录 ═══
    story.append(h1("目录"))
    story.append(hr())
    toc_items = [
        ("1", "项目概览", "Hermes Agent 是什么？核心设计理念"),
        ("2", "架构设计", "六层架构、数据流、设计模式"),
        ("3", "核心模块", "run_agent.py、model_tools.py、registry.py 深度解析"),
        ("4", "Agent 运行时循环", "对话循环、工具执行、错误恢复"),
        ("5", "工具系统", "工具注册、工具集、MCP 集成"),
        ("6", "提示词构建", "系统提示词组装、上下文文件、安全扫描"),
        ("7", "上下文压缩", "压缩算法、工具输出剪枝、迭代摘要"),
        ("8", "记忆系统", "MemoryManager、持久化存储、FTS5 搜索"),
        ("9", "会话管理", "会话模型、SQLite 存储、会话链"),
        ("10", "网关与平台集成", "网关架构、多平台适配器、消息路由"),
        ("11", "定时任务", "任务调度、投递机制、状态管理"),
        ("12", "错误分类与故障转移", "错误分类体系、智能降级、重试策略"),
        ("13", "配置系统", "config.yaml 结构、环境变量、多模型支持"),
        ("14", "技能系统", "技能发现、加载、缓存机制"),
        ("15", "设计哲学总结", "架构亮点、最佳实践、可复用模式"),
    ]
    toc_style = S('TOC', fontSize=11, leading=18, textColor=ACCENT, spaceAfter=1*mm)
    for num, title, desc in toc_items:
        story.append(Paragraph(f'<b>{num}. {esc(title)}</b>  --  {esc(desc)}', toc_style))
    story.append(PageBreak())

    # ═══ 第1章 ═══
    story.append(h1("1. 项目概览"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent 是由 Nous Research 开发的开源 AI Agent 框架，以希腊信使神 Hermes 命名，象征其信息传递与连接的核心使命。它是一个生产级 AI Agent 系统，支持通过多个消息平台（Telegram、Discord、微信、飞书、WhatsApp、Signal 等）进行交互，具备工具调用、持久化记忆、定时任务、上下文压缩和多模型切换等能力。"))
    story.append(h2("1.1 核心定位"))
    story.append(body("Hermes Agent 被设计为通用 AI 助手运行时：不仅是聊天机器人框架，而是一个完整的 Agent 操作系统，提供从消息接入、会话管理、工具执行到响应投递的全流水线能力。"))
    story.append(h2("1.2 核心能力"))

    feat_data = [
        [hp("能力", SB('FH', fontSize=9, textColor=white)), hp("描述", SB('FH', fontSize=9, textColor=white))],
        ["多平台网关", "20+ 消息平台（Telegram、Discord、微信、飞书、WhatsApp 等）"],
        ["工具调用循环", "自动执行工具调用直至任务完成，支持并行工具调用"],
        ["持久化记忆", "SQLite + FTS5 全文搜索，跨会话记忆保留"],
        ["上下文压缩", "长对话智能摘要压缩"],
        ["定时任务", "Cron 表达式、间隔调度、一次性任务"],
        ["多模型支持", "OpenAI、Anthropic、Google、本地模型统一接口"],
        ["智能错误恢复", "分类错误类型，自动降级/重试/模型切换"],
        ["技能系统", "可插拔技能模块，支持动态加载和缓存"],
        ["MCP 集成", "支持模型上下文协议标准"],
        ["子 Agent 委派", "支持并行子 Agent 任务分发"],
    ]
    story.append(make_table(feat_data, [45*mm, 115*mm]))
    story.append(sp(3*mm))
    story.append(h2("1.3 技术栈"))
    story.append(body("基于 Python 3.12+ 构建，核心依赖包括 OpenAI SDK（兼容多后端）、SQLite（状态存储）、aiohttp（异步 HTTP）、python-dotenv。代码库约 12,000 行，按 agent/、gateway/、tools/、cron/ 等模块组织。"))
    story.append(PageBreak())

    # ═══ 第2章 ═══
    story.append(h1("2. 架构设计"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent 采用六层模块化架构，每层职责单一，通过定义良好的接口通信。"))
    story.append(h2("2.1 六层架构概览"))

    arch_data = [
        [hp("层级", SB('AH', fontSize=9, textColor=white)), hp("模块", SB('AH', fontSize=9, textColor=white)), hp("职责", SB('AH', fontSize=9, textColor=white)), hp("关键文件", SB('AH', fontSize=9, textColor=white))],
        ["L1 消息接入", "gateway/platforms/", "多平台消息收发", "telegram.py, discord.py, weixin.py"],
        ["L2 会话管理", "gateway/session.py / hermes_state.py", "会话生命周期、消息持久化", "session.py, state.db"],
        ["L3 Agent 核心", "run_agent.py / agent/", "对话循环、工具调用、错误恢复", "run_agent.py, error_classifier.py"],
        ["L4 工具执行", "tools/ / toolsets.py", "工具定义、注册、执行分发", "registry.py, terminal_tool.py"],
        ["L5 提示词构建", "agent/prompt_builder.py", "系统提示词组装、上下文注入", "prompt_builder.py"],
        ["L6 基础设施", "cron/ / hermes_cli/ / config.yaml", "定时任务、CLI、配置管理", "jobs.py, cli.py"],
    ]
    colors = [HexColor('#e3f2fd'), HexColor('#e8f5e9'), HexColor('#fff3e0'), HexColor('#f3e5f5'), HexColor('#fce4ec'), HexColor('#e0f2f1')]
    story.append(make_table(arch_data, [28*mm, 35*mm, 50*mm, 47*mm], row_colors=colors))
    story.append(sp(4*mm))
    story.append(h2("2.2 核心数据流"))
    story.append(body("完整的消息处理流程：平台适配器接收消息 → 会话管理器恢复上下文 → Agent 核心构建系统提示词 → LLM 推理生成工具调用 → 工具执行器调度执行 → 结果返回 Agent → 循环直至完成 → 响应返回平台适配器 → 发送给用户。每个环节都有完善的错误处理和恢复机制。"))
    story.append(h2("2.3 设计模式"))
    patterns = [
        ("单例模式", "ToolRegistry 确保全局唯一的工具注册"),
        ("策略模式", "ContextEngine 支持多种上下文处理策略"),
        ("观察者模式", "Gateway 使用 asyncio 事件循环处理多平台并发消息"),
        ("工厂模式", "平台适配器通过工厂方法创建"),
        ("责任链模式", "错误分类器按优先级链匹配错误类型"),
        ("模板方法模式", "run_agent.py 对话循环定义 Agent 执行骨架"),
        ("装饰器模式", "通过 registry.register() 装饰器注册工具"),
    ]
    for name, desc in patterns:
        story.append(bullet(f"{name}: {desc}"))
    story.append(PageBreak())

    # ═══ 第3章 ═══
    story.append(h1("3. 核心模块深度解析"))
    story.append(hr(HIGHLIGHT))
    story.append(h2("3.1 run_agent.py -- Agent 主循环"))
    story.append(body("run_agent.py（12,002 行）是实现完整 ReAct（推理 + 行动）循环的核心引擎：接收用户消息 → 构建提示词 → 调用 LLM → 解析工具调用 → 执行工具 → 将结果追加到对话历史 → 重复直至 LLM 不再请求工具调用。"))
    story.append(body("关键设计：SafeWriter 包装 stdout/stderr 防止管道断裂崩溃；jittered_backoff 实现指数退避 + 抖动避免惊群效应；classify_api_error 将 API 错误分类为 12+ 种类型并提供恢复建议。"))
    story.append(h2("3.2 model_tools.py -- 工具编排层"))
    story.append(body("model_tools.py（611 行）是轻量编排层，提供三个核心 API：get_tool_definitions() 返回所有工具的 JSON Schema；handle_function_call() 路由工具调用到处理器；check_toolset_requirements() 验证工具集前置条件。"))
    story.append(h2("3.3 tools/registry.py -- 工具注册中心"))
    story.append(body("registry.py（482 行）实现线程安全的单例工具注册中心。每个工具通过 ToolEntry（名称、工具集、JSON Schema、处理器、环境需求）自我描述。使用 threading.RLock 实现并发读写保护，_snapshot_* 方法提供稳定读取。"))
    story.append(body("发现机制：discover_builtin_tools() 通过 AST 分析扫描 tools/*.py 文件中的 registry.register() 调用，自动注册内置工具。新工具只需在 tools/ 创建文件并调用 register() 即可。"))
    story.append(h2("3.4 toolsets.py -- 工具集分组"))
    story.append(body("toolsets.py（745 行）定义工具集概念用于分组相关工具。_HERMES_CORE_TOOLS 列表包含 30+ 个核心工具，涵盖 Web 搜索、终端、文件管理、浏览器自动化和技能系统。支持工具集组合和动态解析。"))
    story.append(PageBreak())

    # ═══ 第4章 ═══
    story.append(h1("4. Agent 运行时循环"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Agent 运行时循环是最关键的组件。run_agent.py 中的 AIAgent 类实现完整对话循环：初始化 → 构建系统提示词 → 对话循环 → 错误恢复 → 响应输出。"))
    story.append(h2("4.1 对话循环步骤"))
    loop_steps = [
        "1. 接收消息：从会话管理器获取当前消息和对话历史",
        "2. 构建提示词：组装系统提示词（身份 + 平台提示 + 记忆 + 技能 + 上下文文件）",
        "3. 注入记忆：通过 MemoryManager 预取相关记忆并注入提示词",
        "4. LLM 推理：使用消息历史和工具定义调用 OpenAI 兼容 API",
        "5. 解析响应：检查 finish_reason，判断是否需要工具调用",
        "6. 执行工具：并行执行所有工具调用，收集结果",
        "7. 追加结果：将工具结果添加到对话历史",
        "8. 检查压缩：上下文超过阈值时触发上下文压缩",
        "9. 循环/返回：如果 LLM 请求更多工具调用则返回步骤 4，否则返回最终响应",
    ]
    for step in loop_steps:
        story.append(bullet(step))
    story.append(sp(2*mm))
    story.append(h2("4.2 错误恢复"))
    story.append(body("多层错误恢复：API 错误分类器将错误分类为 12+ 种类型（认证失败、速率限制、服务器错误、上下文溢出等），每种类型有不同的恢复策略：重试、凭证轮换、模型回退、上下文压缩或中止。指数退避 + 抖动防止并发重试的惊群效应。"))
    story.append(h2("4.3 工具预算控制"))
    story.append(body("为防止无限工具调用循环，工具预算机制限制每轮对话的最大工具调用次数，超出时强制终止循环。enforce_turn_budget 控制每轮工具输出量，防止输出过大导致上下文膨胀。"))
    story.append(PageBreak())

    # ═══ 第5章 ═══
    story.append(h1("5. 工具系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("工具系统采用声明式注册：每个工具通过 registry.register() 自我注册，包含名称、工具集、JSON Schema、处理器等。核心工具集包含 30+ 个内置工具，涵盖文件操作、终端命令、Web 搜索、浏览器自动化和代码执行。"))
    story.append(h2("5.1 ToolEntry 数据结构"))
    story.append(body("每个工具通过 ToolEntry 自我描述：名称、工具集、schema（JSON Schema）、handler（异步函数）、check_fn（前置检查）、requires_env（所需环境变量）、is_async、描述、emoji。"))
    story.append(h2("5.2 核心工具分类"))
    tool_cats = [
        ("文件操作", "read_file, write_file, patch, search_files"),
        ("终端", "terminal, process"),
        ("Web 搜索", "web_search, web_extract"),
        ("浏览器自动化", "browser_navigate, browser_click, browser_snapshot, browser_type..."),
        ("代码执行", "execute_code, delegate_task"),
        ("视觉", "vision_analyze, image_generate"),
        ("记忆", "memory, session_search"),
        ("任务规划", "todo, clarify"),
        ("消息", "send_message, text_to_speech"),
        ("技能", "skill_view, skill_manage, skills_list"),
        ("调度", "cronjob"),
    ]
    for cat, tools in tool_cats:
        story.append(bullet(f"{cat}: {tools}"))
    story.append(h2("5.3 MCP 集成"))
    story.append(body("系统支持模型上下文协议（MCP）用于动态外部工具服务器注册。MCP 工具通过 mcp_tool.py 集成，注册中心支持动态刷新——当 MCP 服务器添加/删除工具时，注册中心自动更新并向 LLM 暴露新工具定义。"))
    story.append(PageBreak())

    # ═══ 第6章 ═══
    story.append(h1("6. 提示词构建系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("prompt_builder.py（1,115 行）组装 Agent 系统提示词。所有函数均为无状态——给定输入产生确定性输出，使提示词构建可测试和可缓存。系统提示词由多个片段组合而成。"))
    story.append(h2("6.1 系统提示词组件"))
    prompt_parts = [
        ("身份定义", "DEFAULT_AGENT_IDENTITY -- Hermes 基础人格和行为准则"),
        ("平台提示", "PLATFORM_HINTS -- 平台特定交互指南（17+ 平台）"),
        ("记忆引导", "MEMORY_GUIDANCE -- 何时/如何使用记忆系统"),
        ("会话搜索", "SESSION_SEARCH_GUIDANCE -- 搜索历史会话的指南"),
        ("技能引导", "SKILLS_GUIDANCE -- 使用和创建技能的指南"),
        ("工具执行强化", "TOOL_USE_ENFORCEMENT_GUIDANCE -- 强制 Agent 使用工具而非描述计划"),
        ("模型特定", "OPENAI_MODEL_EXECUTION_GUIDANCE / GOOGLE_MODEL_OPERATIONAL_GUIDANCE"),
        ("上下文文件", "AGENTS.md, SOUL.md, .hermes.md 项目级上下文"),
        ("环境提示", "WSL / Docker 运行时环境感知"),
        ("语言检测", "自动检测用户语言并调整响应语言"),
    ]
    for name, desc in prompt_parts:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("6.2 上下文文件安全扫描"))
    story.append(body('在将上下文文件（AGENTS.md、SOUL.md 等）注入系统提示词之前，prompt_builder.py 执行安全扫描检测提示词注入攻击：检查不可见 Unicode 字符（零宽字符、双向覆盖）和威胁模式（如"忽略之前的指令"）。威胁内容被拦截并替换为警告。'))
    story.append(h2("6.3 模型特定适配"))
    story.append(body("不同模型系列接收特定的执行指导：OpenAI/GPT 模型获得详细的执行规范（工具持久化、强制工具使用、前置检查、验证步骤）；Google/Gemini 获得操作指令（绝对路径、依赖检查、并行工具调用）；GPT-5/Codex 使用 developer 角色替代 system 角色以获得更高的指令遵循权重。"))
    story.append(PageBreak())

    # ═══ 第7章 ═══
    story.append(h1("7. 上下文压缩系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("context_compressor.py（1,229 行）实现智能上下文压缩，解决长对话中的上下文窗口溢出问题。核心思想：保护头部和尾部的关键消息，对中间历史消息使用 LLM 摘要。"))
    story.append(h2("7.1 压缩算法流程"))
    compress_steps = [
        "1. 工具输出剪枝（预扫描）：用信息丰富的摘要替换旧的大型工具输出（非通用占位符），无需 LLM 调用",
        "2. 保护头部消息：系统提示词 + 前 N 条消息保持完整（默认：前 3 条）",
        "3. 保护尾部消息：按 token 预算保护最近消息（默认：约 20K tokens）",
        "4. 去重：识别并合并重复的工具输出（如多次读取同一文件）",
        "5. LLM 摘要：使用结构化模板摘要中间消息",
        "6. 迭代更新：在后续压缩时更新之前的摘要而非重新生成",
    ]
    for step in compress_steps:
        story.append(bullet(step))
    story.append(h2("7.2 防回弹保护"))
    story.append(body("为防止无效压缩循环（每次仅压缩 1-2 条消息），防回弹保护在最近两次压缩节省率均低于 10% 时跳过压缩，建议用户 /new 开始新会话。600 秒冷却时间防止摘要服务不可用时重复尝试。"))
    story.append(h2("7.3 结构化摘要模板"))
    story.append(body('LLM 生成的摘要遵循结构化模板，涵盖：已完成工作、当前状态、未解决问题、剩余工作。摘要以"CONTEXT COMPACTION -- REFERENCE ONLY"为前缀，防止模型将历史摘要当作当前指令。'))
    story.append(PageBreak())

    # ═══ 第8章 ═══
    story.append(h1("8. 记忆系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("记忆系统有两层：语义记忆通过 memory 工具存储用户偏好和环境事实；情节记忆通过 hermes_state.py SQLite 数据库存储完整会话历史，支持 FTS5 全文搜索。"))
    story.append(h2("8.1 记忆管理器"))
    story.append(body("memory_manager.py（373 行）协调内置记忆提供者和最多一个外部插件提供者。关键约束：只能注册一个外部记忆提供者，防止工具 Schema 膨胀和后端冲突。内置提供者始终优先注册且不可移除。"))
    story.append(body('记忆上下文通过 <memory-context> 围栏标签注入，附带系统注释"非新用户输入"，防止模型将召回的记忆当作新用户输入。此围栏设计有效防止记忆污染。'))
    story.append(h2("8.2 SQLite 状态存储"))
    story.append(body("hermes_state.py（1,443 行）实现 SQLite 支持的持久化状态存储。关键设计：WAL 模式支持多读者 + 单写者并发；FTS5 虚拟表支持跨会话全文搜索；parent_session_id 链支持压缩触发的会话分裂；应用层随机抖动重试解决 WAL 写竞争。数据库路径：~/.hermes/state.db，Schema 版本 6。"))
    story.append(h2("8.3 支持的记忆插件"))
    story.append(body("支持插件：mem0、Hindsight、Supermemory、ReteroDB、OpenViking、Holographic Memory、Honcho、ByteRover。"))
    story.append(PageBreak())

    # ═══ 第9章 ═══
    story.append(h1("9. 会话管理"))
    story.append(hr(HIGHLIGHT))
    story.append(body("gateway/session.py（1,257 行）实现完整的会话生命周期管理。每个会话由 SessionSource（平台、聊天 ID、用户 ID、聊天类型）描述，支持私信、群组、频道和话题类型。"))
    story.append(h2("9.1 会话追踪"))
    story.append(body("每条消息携带完整的追踪信息：平台、chat_id、user_id、chat_type（私信/群组/频道/话题）、thread_id。用于将响应路由到正确位置、向系统提示词注入上下文、追踪定时任务投递来源。"))
    story.append(h2("9.2 隐私信息保护"))
    story.append(body("会话存储实现 PII 哈希：user_id 和 chat_id 等敏感标识符在存储前经过 SHA-256 哈希处理（保留前 12 个十六进制字符），在不暴露原始用户信息的情况下保持唯一会话标识。"))
    story.append(h2("9.3 会话重置策略"))
    story.append(body("支持多种重置策略：手动重置（/new 命令）、空闲超时重置（可配置）、上下文溢出重置（自动触发 /new 并保留摘要）。parent_session_id 链在重置间保持会话连续性。"))
    story.append(PageBreak())

    # ═══ 第10章 ═══
    story.append(h1("10. 网关与平台集成"))
    story.append(hr(HIGHLIGHT))
    story.append(body("gateway/run.py（11,015 行）是网关主入口，管理所有已配置平台适配器的生命周期。使用 asyncio 事件循环处理多平台并发消息，每个平台适配器在各自的协程中运行。"))
    story.append(h2("10.1 支持的平台"))
    story.append(body("支持 20+ 平台：Telegram、Discord、WhatsApp、Signal、Slack、Mattermost、Matrix、iMessage（BlueBubbles）、微信、企业微信、飞书、钉钉、QQ Bot、元宝、邮件、短信、Home Assistant、API 服务器、Webhook。"))
    story.append(h2("10.2 网关生命周期"))
    gw_steps = [
        "1. SSL 证书检测：自动检测系统 CA 证书位置（支持 NixOS）",
        "2. 环境变量加载：从 ~/.hermes/.env 加载",
        "3. Agent 缓存初始化：LRU 缓存，最多 128 个 Agent 实例，1 小时空闲 TTL",
        "4. 平台适配器启动：为每个平台启动独立的消息监听协程",
        "5. 消息路由循环：接收消息 → 查找/创建会话 → 调用 Agent → 返回响应",
        "6. 优雅关闭：在 SIGTERM 时保存所有会话状态并关闭连接",
    ]
    for step in gw_steps:
        story.append(bullet(step))
    story.append(h2("10.3 平台适配器架构"))
    story.append(body("每个平台适配器实现统一接口：connect()、listen()、send()、disconnect()。适配器处理平台特定协议（Telegram Bot API、Discord Gateway、微信 iLink Bot API 等），将平台消息转换为内部格式。"))
    story.append(PageBreak())

    # ═══ 第11章 ═══
    story.append(h1("11. 定时任务系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("cron/jobs.py（776 行）实现完整的定时任务系统。任务存储在 ~/.hermes/cron/jobs.json，输出保存到 ~/.hermes/cron/output/{job_id}/。"))
    story.append(h2("11.1 调度类型"))
    sched_types = [
        ("一次性", "在指定延迟后执行一次（如 30m、2h、ISO 时间戳）"),
        ("间隔", "按固定间隔重复（如 every 30m、every 2h）"),
        ("Cron 表达式", "标准 5 域 Cron 表达式（如 0 9 * * *）"),
    ]
    for name, desc in sched_types:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("11.2 任务投递"))
    story.append(body("任务结果支持多种投递模式：origin（返回创建对话）、local（仅保存到文件）、指定平台（如 telegram:chat_id）。通过 script 参数支持预执行脚本，用于数据收集和变化检测。"))
    story.append(h2("11.3 容错机制"))
    story.append(body("一次性任务有 120 秒的宽限期。间隔任务的宽限期为间隔的一半（120 秒至 2 小时），允许短期错过后的补执行，但在长期错过后快进以防止任务积压。threading.Lock 保护并发 jobs.json 读写。"))
    story.append(PageBreak())

    # ═══ 第12章 ═══
    story.append(h1("12. 错误分类与故障转移"))
    story.append(hr(HIGHLIGHT))
    story.append(body("error_classifier.py（829 行）实现结构化 API 错误分类，用集中式分类器替代分散的字符串匹配，主重试循环在每次 API 失败时查询该分类器。"))
    story.append(h2("12.1 错误分类体系"))
    error_types = [
        ("认证失败", "401/403 → 刷新/轮换凭证或中止"),
        ("速率限制", "429 → 退避后轮换凭证"),
        ("计费", "402 → 立即轮换凭证"),
        ("过载/服务器错误", "500/503/529 → 退避重试"),
        ("超时", "连接/读取超时 → 重建客户端后重试"),
        ("上下文溢出", "上下文过大 → 触发上下文压缩，非故障转移"),
        ("载荷过大", "413 → 压缩载荷"),
        ("模型未找到", "404 → 回退到不同模型"),
        ("格式错误", "400 → 中止或修复后重试"),
        ("思考签名", "Anthropic 思考块签名无效"),
        ("未知", "无法分类 → 退避重试"),
    ]
    for name, desc in error_types:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("12.2 分类错误数据类"))
    story.append(body("分类结果封装为 ClassifiedError：reason（FailoverReason 枚举）、status_code、provider、model、message、error_context（字典）和恢复提示（retryable、should_compress、should_rotate_credential、should_fallback）。重试循环直接检查这些提示。"))
    story.append(PageBreak())

    # ═══ 第13章 ═══
    story.append(h1("13. 配置系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent 使用多层配置：config.yaml（主配置）→ .env（环境变量）→ CLI 参数。主配置 ~/.hermes/config.yaml 包含模型、网关、工具、会话等所有章节。"))
    story.append(h2("13.1 配置章节"))
    config_sections = [
        ("model", "默认模型、模型列表、提供者配置"),
        ("gateway", "启用平台、Home Channels、会话重置策略"),
        ("tools", "工具集配置、MCP 服务器配置"),
        ("session", "会话超时、上下文压缩阈值"),
        ("cron", "定时任务全局配置"),
        ("display", "UI 主题、旋转器样式"),
        ("plugins", "记忆插件、上下文引擎插件"),
    ]
    for name, desc in config_sections:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("13.2 环境变量"))
    story.append(body("所有配置项均可通过环境变量覆盖，前缀为 HERMES_。例如：HERMES_MODEL=gpt-4、HERMES_GATEWAY__TELEGRAM__ENABLED=true。优先级：CLI 参数 > 环境变量 > config.yaml。"))
    story.append(h2("13.3 多模型支持"))
    story.append(body("支持 OpenAI、Anthropic、Google Gemini、Mistral、Groq、Together、Ollama 等主流模型提供者。每个提供者可配置 API Key、base URL、模型列表。支持故障转移时自动切换到备用模型。"))
    story.append(PageBreak())

    # ═══ 第14章 ═══
    story.append(h1("14. 技能系统"))
    story.append(hr(HIGHLIGHT))
    story.append(body("技能系统提供可插拔的能力扩展机制。每个技能是一个 SKILL.md 文件，包含触发条件、执行步骤、注意事项。技能存储在 ~/.hermes/skills/ 目录下。"))
    story.append(h2("14.1 技能发现与加载"))
    story.append(body("技能自动发现：扫描 ~/.hermes/skills/ 目录下的所有 SKILL.md 文件。加载时解析 YAML frontmatter 获取技能名称、描述、触发条件。技能内容注入到系统提示词中，指导 Agent 的行为。"))
    story.append(h2("14.2 技能缓存"))
    story.append(body("技能内容被缓存以避免重复读取。当技能文件修改时，缓存自动失效。缓存键基于文件路径和修改时间。"))
    story.append(h2("14.3 技能类型"))
    story.append(body("9 种技能类型：库和 API 参考、产品验证、数据分析、代码生成、文档生成、代码审查、部署、团队规范、调研整理。5 种模式：Tool Wrapper、Generator、Reviewer、Inversion、Pipeline。"))
    story.append(PageBreak())

    # ═══ 第15章 ═══
    story.append(h1("15. 设计哲学总结"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent 的设计哲学可以概括为：简洁而不简单，灵活而不混乱，强大而不臃肿。"))
    story.append(h2("15.1 架构亮点"))
    highlights = [
        ("六层模块化", "每层职责单一，通过定义良好的接口通信，易于测试和维护"),
        ("ReAct 循环", "Reasoning + Acting 的循环模式，让 Agent 能够自主分解和执行复杂任务"),
        ("智能错误恢复", "12+ 种错误类型分类，每种有针对性恢复策略，而非简单的重试"),
        ("上下文压缩", "保护头尾关键消息 + LLM 摘要中间历史，解决长对话上下文溢出"),
        ("双层记忆", "语义记忆存储偏好，情节记忆存储历史，FTS5 全文搜索跨会话召回"),
        ("多平台统一", "20+ 平台适配器共享统一的会话管理和 Agent 核心"),
        ("声明式工具注册", "新工具只需创建文件并调用 register()，零配置集成"),
    ]
    for name, desc in highlights:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("15.2 最佳 practices"))
    best_practices = [
        "优先使用已有工具，而非编写新代码",
        "长时间任务必须使用任务队列并定期汇报进度",
        "错误恢复时先分类再处理，避免盲目重试",
        "上下文接近阈值时主动触发压缩，而非等待溢出",
        "记忆存储用户偏好和环境事实，不存储临时任务状态",
    ]
    for i, bp in enumerate(best_practices, 1):
        story.append(bullet(f"{i}. {bp}"))
    story.append(h2("15.3 可复用模式"))
    story.append(body("Hermes Agent 中提炼的可复用模式：Agent 运行时循环（可复用于任何需要工具调用的场景）、上下文压缩（可复用于任何长文本处理场景）、错误分类器（可复用于任何需要重试的 API 调用）、工具注册中心（可复用于任何插件化系统）。"))

    doc.build(story)
    print(f"PDF 生成成功: {output_path}")

build_pdf('/home/ubuntu/.hermes/Hermes_Architecture_Guide_CN.pdf')
