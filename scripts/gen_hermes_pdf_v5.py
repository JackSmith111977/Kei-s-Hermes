#!/usr/bin/env python3
"""Generate Hermes Agent Architecture PDF v5 - Dark Theme with Highlight Accents"""

__version__ = "5.0.0"
__date__ = "2026-05-03"
__author__ = "小喵 AI"

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, Image, NextPageTemplate, PageTemplate, Frame
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import os

# ═══ 字体注册 ═══
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
BODY_FONT = "STSong-Light"
BOLD_FONT = "STSong-Light"
CODE_FONT = "Helvetica"

# ═══ 色板 ═══
PRIMARY = HexColor('#1a1a2e')
SECONDARY = HexColor('#16213e')
ACCENT = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f8f9fa')
MED_GRAY = HexColor('#6c757d')
DARK_TEXT = HexColor('#212529')
CODE_BG = HexColor('#f4f4f4')
BORDER = HexColor('#dee2e6')

OUTPUT_PATH = f'/home/ubuntu/.hermes/Hermes_Agent_Deep_Architecture_v{__version__}.pdf'

# ═══ 辅助函数 ═══
def esc(text):
    """Escape XML special characters for reportlab Paragraph"""
    if text is None:
        return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def S(name, **kw):
    return ParagraphStyle(name, fontName=BODY_FONT, **kw)

def hr(color=HIGHLIGHT, width=20, thickness=1.5):
    """Horizontal rule with highlight color"""
    return HRFlowable(width=f"{width}%", thickness=thickness, color=color,
                       spaceBefore=3*mm, spaceAfter=4*mm)

def make_table(data, col_widths, header_color=PRIMARY, row_colors=None, font_size=8):
    """Create a styled table with proper CJK text wrapping"""
    body_style = S('BodyTable', fontSize=font_size, leading=font_size+4,
                   textColor=DARK_TEXT, alignment=TA_LEFT)
    header_style = S('HeaderTable', fontSize=font_size, leading=font_size+4,
                     textColor=white, alignment=TA_CENTER)

    processed_data = []
    for i, row in enumerate(data):
        processed_row = []
        for cell in row:
            if isinstance(cell, str):
                style = header_style if i == 0 else body_style
                processed_row.append(Paragraph(esc(cell), style))
            else:
                processed_row.append(cell)
        processed_data.append(processed_row)

    t = Table(processed_data, colWidths=col_widths, repeatRows=1)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3*mm),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
    ]
    if row_colors:
        for i, c in enumerate(row_colors):
            if i + 1 < len(data):
                style.append(('BACKGROUND', (0, i+1), (-1, i+1), c))
    else:
        style.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]))
    t.setStyle(TableStyle(style))
    return t

def add_image(filepath, max_width=160*mm, caption=None):
    """Add image with optional caption"""
    elements = []
    if os.path.exists(filepath):
        img = Image(filepath)
        aspect = img.imageWidth / max(img.imageHeight, 1)
        if aspect > 1:
            img.drawWidth = max_width
            img.drawHeight = max_width / aspect
        else:
            img.drawHeight = max_width * 0.6
            img.drawWidth = max_width * 0.6 * aspect
        elements.append(img)
        elements.append(Spacer(1, 2*mm))
    else:
        elements.append(Paragraph(
            f'<i>[图片未找到: {os.path.basename(filepath)}]</i>',
            S('NoImg', fontSize=8, textColor=MED_GRAY)))
    if caption:
        cap_style = S('Caption', fontSize=8, textColor=MED_GRAY,
                      alignment=TA_CENTER, spaceAfter=4*mm)
        elements.append(Paragraph(esc(caption), cap_style))
    return elements

def code_block(code_text, caption="代码示例", font_size=7.5):
    """Render a code block with background and monospace font"""
    code_style = ParagraphStyle('Code', fontName=CODE_FONT, fontSize=font_size,
                   leading=font_size + 3, textColor=DARK_TEXT,
                   backColor=CODE_BG, borderColor=BORDER, borderWidth=0.5,
                   borderPadding=3*mm, spaceBefore=3*mm, spaceAfter=3*mm,
                   leftIndent=2*mm, rightIndent=2*mm)
    caption_style = ParagraphStyle('CodeCaption', fontSize=8, textColor=MED_GRAY,
                      spaceBefore=1*mm, spaceAfter=0, leftIndent=2*mm)

    elements = []
    if caption:
        elements.append(Paragraph(f'<b>{esc(caption)}</b>', caption_style))
    elements.append(Paragraph(esc(code_text), code_style))
    elements.append(Spacer(1, 2*mm))
    return elements

# ═══ 样式定义 ═══
H1 = S('H1', fontSize=18, leading=24, textColor=PRIMARY,
       spaceBefore=10*mm, spaceAfter=3*mm)
H2 = S('H2', fontSize=13, leading=18, textColor=ACCENT,
       spaceBefore=6*mm, spaceAfter=2*mm)
BODY = S('Body', fontSize=9.5, leading=15, textColor=DARK_TEXT,
         spaceAfter=3*mm, alignment=TA_JUSTIFY)
BULLET = S('Bullet', fontSize=9.5, leading=15, textColor=DARK_TEXT,
           spaceAfter=2*mm, leftIndent=15*mm, bulletIndent=8*mm)


# ── 第1章 ──
def build_chapter1():
    story = []
    story.append(Paragraph('<b>第 1 章　Hermes Agent 概览</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>1.1　什么是 Hermes Agent</b>', H2))
    story.append(Paragraph(
        'Hermes Agent 是由 Nous Research 开发的开源 AI Agent 框架，以希腊信使神 Hermes 命名，象征其信息传递与连接的核心使命。'
        '它是一个生产级 AI Agent 系统，支持通过多个消息平台（Telegram、Discord、微信、飞书、WhatsApp、Signal 等）进行交互，'
        '具备工具调用、持久化记忆、定时任务、上下文压缩和多模型切换等能力。', BODY))

    story.append(Paragraph('<b>1.2　核心特性</b>', H2))
    features = [
        ["特性", "描述"],
        ["多平台网关", "20+ 消息平台统一接入（Telegram、Discord、微信、飞书等）"],
        ["工具调用循环", "自动执行工具调用直至任务完成，支持并行工具调用"],
        ["持久化记忆", "SQLite + FTS5 全文搜索，跨会话记忆保留"],
        ["上下文压缩", "长对话智能摘要压缩，保护头尾关键消息"],
        ["定时任务", "Cron 表达式、间隔调度、一次性任务"],
        ["多模型支持", "OpenAI、Anthropic、Google、本地模型统一接口"],
        ["智能错误恢复", "分类错误类型，自动降级/重试/模型切换"],
        ["技能系统", "可插拔技能模块，支持动态加载和缓存"],
        ["MCP 集成", "支持模型上下文协议标准"],
        ["子 Agent 委派", "支持并行子 Agent 任务分发"],
    ]
    story.append(make_table(features, [30*mm, 105*mm], PRIMARY, None, 8))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph('<b>1.3　与其他 AI Agent 的对比</b>', H2))
    compare = [
        ["维度", "Hermes", "AutoGPT", "LangChain Agent", "Claude Code"],
        ["平台集成", "20+ 平台", "仅 CLI", "API 级", "仅 CLI"],
        ["记忆系统", "双层（语义+情节）", "向量存储", "外挂可选", "无"],
        ["上下文压缩", "智能 LLM 摘要", "无", "有（基础）", "无"],
        ["工具注册", "声明式自动发现", "手动定义", "手动组合", "内建"],
        ["错误恢复", "12+ 类型分类恢复", "基础重试", "基础重试", "基础重试"],
        ["技能系统", "SKILL.md 即插即用", "无", "无", "无"],
        ["多模型 Fallback", "支持链式切换", "单模型", "支持", "单模型"],
    ]
    story.append(make_table(compare, [22*mm, 32*mm, 28*mm, 28*mm, 28*mm], PRIMARY, None, 7.5))
    story.append(PageBreak())
    return story


# ── 第2章 ──
def build_chapter2():
    story = []
    story.append(Paragraph('<b>第 2 章　系统架构总览</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>2.1　六层模块化架构</b>', H2))
    story.append(Paragraph(
        'Hermes Agent 采用六层模块化架构，每层职责单一，通过定义良好的接口通信。'
        '从底层的消息接入到顶层的 Agent 核心，各层之间通过标准数据格式交互。', BODY))

    arch_layers = [
        ["层级", "模块", "职责", "关键文件"],
        ["L1 消息接入", "gateway/platforms/", "多平台消息收发", "telegram.py, discord.py"],
        ["L2 会话管理", "gateway/session.py", "会话生命周期", "session.py, state.db"],
        ["L3 Agent 核心", "run_agent.py", "对话循环、工具调用", "run_agent.py"],
        ["L4 工具执行", "tools/registry.py", "工具定义、注册", "registry.py"],
        ["L5 提示词构建", "prompt_builder.py", "系统提示词组装", "prompt_builder.py"],
        ["L6 基础设施", "cron/, config.yaml", "定时任务、配置", "jobs.py, cli.py"],
    ]
    colors = [HexColor('#e3f2fd'), HexColor('#e8f5e9'), HexColor('#fff3e0'),
              HexColor('#f3e5f5'), HexColor('#fce4ec'), HexColor('#e0f2f1')]
    story.append(make_table(arch_layers, [22*mm, 35*mm, 45*mm, 35*mm], PRIMARY, colors, 7.5))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph('<b>2.2　核心数据流</b>', H2))
    story.append(Paragraph(
        '完整的消息处理流程：平台适配器接收消息 → 会话管理器恢复上下文 → Agent 核心构建系统提示词 → '
        'LLM 推理生成工具调用 → 工具执行器调度执行 → 结果返回 Agent → 循环直至完成 → 响应返回平台适配器 → 发送给用户。'
        '每个环节都有完善的错误处理和恢复机制。', BODY))

    story.append(Paragraph('<b>2.3　设计模式</b>', H2))
    patterns = [
        '▪ 单例模式：ToolRegistry 确保全局唯一的工具注册',
        '▪ 策略模式：ContextEngine 支持多种上下文处理策略',
        '▪ 观察者模式：Gateway 使用 asyncio 事件循环处理多平台并发消息',
        '▪ 工厂模式：平台适配器通过工厂方法创建',
        '▪ 责任链模式：错误分类器按优先级链匹配错误类型',
        '▪ 模板方法模式：run_agent.py 定义 Agent 执行骨架',
    ]
    for p in patterns:
        story.append(Paragraph(p, BULLET))
    story.append(PageBreak())
    return story


# ── 第3章 ──
def build_chapter3():
    story = []
    story.append(Paragraph('<b>第 3 章　核心循环（Core Loop）</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>3.1　run_conversation() 循环</b>', H2))
    story.append(Paragraph(
        'run_agent.py（12,002 行）是实现完整 ReAct（推理 + 行动）循环的核心引擎。'
        '它接收用户消息，构建提示词，调用 LLM，解析工具调用，执行工具，将结果追加到对话历史，'
        '重复直至 LLM 不再请求工具调用。', BODY))

    story.append(Paragraph('核心循环步骤：', BODY))
    loop_steps = [
        '1. 接收消息：从会话管理器获取当前消息和对话历史',
        '2. 构建提示词：组装系统提示词（身份 + 平台提示 + 记忆 + 技能）',
        '3. 注入记忆：通过 MemoryManager 预取相关记忆并注入提示词',
        '4. LLM 推理：使用消息历史和工具定义调用 LLM API',
        '5. 解析响应：检查 finish_reason，判断是否需要工具调用',
        '6. 执行工具：并行执行所有工具调用，收集结果',
        '7. 追加结果：将工具结果添加到对话历史',
        '8. 检查压缩：上下文超过阈值时触发上下文压缩',
        '9. 循环/返回：如果 LLM 请求更多工具调用则返回步骤 4，否则返回最终响应',
    ]
    for step in loop_steps:
        story.append(Paragraph(step, BULLET))

    story.append(Paragraph('<b>3.2　消息格式</b>', H2))
    story.append(Paragraph(
        '消息采用 OpenAI 兼容格式，包含角色（system/user/assistant/tool）、'
        '内容（文本或多模态）、工具调用（tool_calls）和工具结果（tool_call_id）。'
        '系统提示词在对话开始时注入，用户消息和助手响应交替排列。', BODY))

    story.extend(code_block(
        '# 消息格式示例\n'
        'messages = [\n'
        '    {"role": "system", "content": "你是 Hermes Agent..."},\n'
        '    {"role": "user", "content": "帮我查一下天气"},\n'
        '    {"role": "assistant", "content": "",\n'
        '     "tool_calls": [{"id": "call_1", "type": "function",\n'
        '                    "function": {"name": "web_search", "arguments": "..."}}]},\n'
        '    {"role": "tool", "content": "北京天气晴朗", "tool_call_id": "call_1"},\n'
        ']', "OpenAI 消息格式", 7.5))

    story.append(Paragraph('<b>3.3　工具调用流程</b>', H2))
    story.append(Paragraph(
        '当 LLM 返回 tool_calls 时，Agent 解析每个工具调用的名称和参数，并行执行所有工具，'
        '收集执行结果并作为 tool 角色消息追加到对话历史。'
        '工具执行器支持超时控制、错误处理和前置条件检查。', BODY))

    story.append(Paragraph('<b>3.4　关键代码路径</b>', H2))
    story.append(Paragraph(
        'SafeWriter 包装 stdout/stderr 防止管道断裂崩溃；jittered_backoff 实现指数退避 + 抖动避免惊群效应；'
        'classify_api_error 将 API 错误分类为 12+ 种类型并提供恢复建议；'
        'enforce_turn_budget 控制每轮工具输出量，防止上下文膨胀。', BODY))
    story.append(PageBreak())
    return story


# ── 第4章 ──
def build_chapter4():
    story = []
    story.append(Paragraph('<b>第 4 章　Provider 与 Fallback 机制</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>4.1　Provider Fallback 链</b>', H2))
    story.append(Paragraph(
        'Hermes 支持多 Provider 配置，当主 Provider 失败时自动切换到备用 Provider。'
        'Fallback 链在 config.yaml 中定义，每个 Fallback 提供者指定 provider、model、base_url 和 key_env。'
        '切换逻辑在 _try_activate_fallback() 中实现。', BODY))

    story.extend(code_block(
        '# 安全的 fallback 配置（v5.0）\n'
        'fallback_providers:\n'
        '- provider: custom_longCat\n'
        '  model: LongCat-2.0-Preview\n'
        '  base_url: https://api.longcat.chat/openai\n'
        '  key_env: CUSTOM_LONGCAT_API_KEY   # 引用 .env 文件\n'
        '- provider: deepseek\n'
        '  model: deepseek-v4-flash\n'
        '  base_url: https://api.deepseek.com/v1\n'
        '  key_env: DEEPSEEK_API_KEY', "YAML 配置示例", 7.5))

    story.append(Paragraph('<b>4.2　Credential Pool（凭证池）</b>', H2))
    story.append(Paragraph(
        'Credential Pool 通过 auth.json 持久化存储凭证状态。每条凭证包含 source、auth_type、'
        'access_token、base_url、last_status 和 last_status_at。'
        '当 Key 耗尽时自动触发 fallback 链，支持 429 速率限制的冷却恢复。', BODY))

    story.append(Paragraph('<b>4.3　429 处理逻辑</b>', H2))
    story.append(Paragraph(
        '当遇到 429 速率限制时，系统执行指数退避 + 抖动策略：第一次等待 1 秒，第二次 2 秒，第三次 4 秒……'
        '同时触发凭证轮换，从凭证池中获取下一个可用 Key。'
        '所有 Key 都耗尽时，标记当前 Provider 为降级状态并切换到 Fallback Provider。', BODY))

    story.append(Paragraph('<b>4.4　主/备模型切换</b>', H2))
    story.append(Paragraph(
        '当所有 Provider 和凭证都不可用时，系统执行模型降级：从高性能模型切换到低成本模型，'
        '确保服务不中断。降级状态通过 health check 定期尝试恢复，可用时自动切回主模型。', BODY))
    story.append(PageBreak())
    return story


# ── 第5章 ──
def build_chapter5():
    story = []
    story.append(Paragraph('<b>第 5 章　工具系统</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>5.1　工具注册机制</b>', H2))
    story.append(Paragraph(
        'registry.py（482 行）实现线程安全的单例工具注册中心。每个工具通过 ToolEntry 自我描述：'
        '名称、工具集、schema（JSON Schema）、handler（异步函数）、check_fn（前置检查）、'
        'requires_env（所需环境变量）等。', BODY))

    story.extend(code_block(
        '# 工具注册示例\n'
        '@registry.register(\n'
        '    name=\"web_search\",\n'
        '    toolset=\"web\",\n'
        '    description=\"搜索互联网获取最新信息\",\n'
        '    schema={...},\n'
        '    requires_env=[\"SERP_API_KEY\"],\n'
        ')\n'
        'async def web_search(query: str):\n'
        '    \"\"\"执行 Web 搜索\"\"\"\n'
        '    ...', "Python 代码示例", 7.5))

    story.append(Paragraph('<b>5.2　16+ 工具列表</b>', H2))
    tool_cats = [
        ["分类", "工具", "用途"],
        ["文件操作", "read_file, write_file, patch, search_files", "文件读写与搜索"],
        ["终端", "terminal, process", "Shell 命令执行"],
        ["Web 搜索", "web_search, web_extract", "互联网信息获取"],
        ["浏览器", "browser_navigate, browser_click, browser_snapshot", "浏览器自动化"],
        ["代码执行", "execute_code, delegate_task", "代码运行与子代理"],
        ["视觉", "vision_analyze, image_generate", "图像分析与生成"],
        ["记忆", "memory, session_search", "记忆存储与检索"],
        ["消息", "send_message, text_to_speech", "消息发送与语音"],
        ["技能", "skill_view, skill_manage, skills_list", "技能管理"],
        ["调度", "cronjob", "定时任务调度"],
    ]
    story.append(make_table(tool_cats, [25*mm, 65*mm, 48*mm], PRIMARY, None, 7.5))

    story.append(Paragraph('<b>5.3　MCP 客户端</b>', H2))
    story.append(Paragraph(
        'MCP（Model Context Protocol）客户端通过 mcp_tool.py 集成，支持动态外部工具服务器注册。'
        '当 MCP 服务器添加或删除工具时，注册中心自动更新并向 LLM 暴露新工具定义。', BODY))

    story.append(Paragraph('<b>5.4　工具安全与审批</b>', H2))
    story.append(Paragraph(
        'approval.py 维护命令黑名单/白名单系统。高危操作触发审批流程——CLI 模式弹窗确认，'
        'Gateway 模式自动拒绝。commmand_allowlist 配置在 config.yaml 中定义。', BODY))
    story.append(PageBreak())
    return story


# ── 第6章 ──
def build_chapter6():
    story = []
    story.append(Paragraph('<b>第 6 章　记忆系统</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>6.1　Memory 管理（持久记忆）</b>', H2))
    story.append(Paragraph(
        '记忆系统有两层架构：语义记忆通过 memory 工具存储用户偏好和环境事实；'
        '情节记忆通过 hermes_state.py SQLite 数据库存储完整会话历史，支持 FTS5 全文搜索。', BODY))

    story.append(Paragraph(
        'memory_manager.py（373 行）协调内置记忆提供者和最多一个外部插件提供者。'
        '关键约束：只能注册一个外部记忆提供者，防止工具 Schema 膨胀和后端冲突。'
        '内置提供者始终优先注册且不可移除。', BODY))

    story.append(Paragraph('<b>6.2　Session Search / 会话搜索</b>', H2))
    story.append(Paragraph(
        '会话搜索基于 SQLite FTS5 全文搜索引擎，支持跨会话的关键词搜索。'
        '搜索范围包括所有非压缩的消息内容，搜索结果包含上下文片段和会话元数据。'
        '搜索由 Auxiliary AI 服务驱动，超时 30 秒。', BODY))

    story.append(Paragraph('<b>6.3　上下文压缩（Context Compression）</b>', H2))
    story.append(Paragraph(
        'context_compressor.py（1,229 行）实现智能上下文压缩。核心策略：'
        '保护头部和尾部的关键消息，对中间历史消息使用 LLM 摘要。', BODY))

    story.append(Paragraph('压缩算法流程：', BODY))
    compress_steps = [
        '1. 工具输出剪枝：用摘要替换旧的大型工具输出（无需 LLM 调用）',
        '2. 保护头部：系统提示词 + 前 3 条消息保持完整',
        '3. 保护尾部：按 token 预算保护最近消息（约 20K tokens）',
        '4. 去重：识别并合并重复的工具输出',
        '5. LLM 摘要：使用结构化模板摘要中间消息',
        '6. 迭代更新：后续压缩时更新之前的摘要',
    ]
    for step in compress_steps:
        story.append(Paragraph(step, BULLET))

    story.append(Paragraph('<b>6.4　记忆 Token 策略</b>', H2))
    story.append(Paragraph(
        '记忆上下文通过 <memory-context> 围栏标签注入，附带系统注释"非新用户输入"，'
        '防止模型将召回的记忆当作新用户输入。记忆 Token 消耗计入上下文窗口预算，'
        '通过 max_memory_tokens 配置控制。', BODY))
    story.append(PageBreak())
    return story


# ── 第7章 ──
def build_chapter7():
    story = []
    story.append(Paragraph('<b>第 7 章　技能系统（Skills）</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>7.1　Skill 目录结构</b>', H2))
    story.append(Paragraph(
        '技能系统提供可插拔的能力扩展机制。每个技能是一个 SKILL.md 文件，'
        '包含触发条件、执行步骤和注意事项。技能存储在 ~/.hermes/skills/ 目录下。', BODY))

    story.extend(code_block(
        '~/.hermes/skills/\n'
        '├── pdf-layout/\n'
        '│   └── SKILL.md     # PDF 布局技能\n'
        '├── translate-md/\n'
        '│   └── SKILL.md     # 翻译技能\n'
        '├── code-review/\n'
        '│   └── SKILL.md     # 代码审查技能\n'
        '└── ...', "目录结构", 7.5))

    story.append(Paragraph('<b>7.2　自动发现与加载</b>', H2))
    story.append(Paragraph(
        '技能自动发现机制：启动时扫描 ~/.hermes/skills/ 目录下的所有 SKILL.md 文件。'
        '加载时解析 YAML frontmatter 获取技能名称、描述和触发条件。'
        '技能内容被缓存以避免重复读取，文件修改时缓存自动失效。', BODY))

    story.append(Paragraph('<b>7.3　索引 Skill 与原子 Skill</b>', H2))
    story.append(Paragraph(
        '索引 Skill（Index Skill）：一组技能的集合，用于在提示词中引用多个技能。'
        '原子 Skill（Atomic Skill）：单个独立技能，包含完整的执行步骤和触发条件。'
        'Skill Manager（skill_manager.py）管理技能生命周期，支持 skill_view、skill_manage 等工具。', BODY))

    story.append(Paragraph('<b>7.4　Skill Creator 流程</b>', H2))
    story.append(Paragraph(
        'skill-creator 交互式流程引导用户创建新技能：'
        '输入名称 → 选择类型 → 编写步骤 → 保存 SKILL.md。'
        '支持 9 种技能类型（库和 API 参考、产品验证、数据分析、代码生成等）和 '
        '5 种模式（Tool Wrapper、Generator、Reviewer、Inversion、Pipeline）。', BODY))
    story.append(PageBreak())
    return story


# ── 第8章 ──
def build_chapter8():
    story = []
    story.append(Paragraph('<b>第 8 章　消息平台网关</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>8.1　Gateway 架构</b>', H2))
    story.append(Paragraph(
        'gateway/run.py（11,015 行）是网关主入口，管理所有已配置平台适配器的生命周期。'
        '使用 asyncio 事件循环处理多平台并发消息，每个平台适配器在各自的协程中运行。', BODY))

    story.append(Paragraph('Gateway 生命周期：', BODY))
    gw_steps = [
        '1. SSL 证书检测：自动检测系统 CA 证书位置',
        '2. 环境变量加载：从 ~/.hermes/.env 加载',
        '3. Agent 缓存初始化：LRU 缓存，最多 128 个 Agent 实例',
        '4. 平台适配器启动：为每个平台启动独立的消息监听协程',
        '5. 消息路由循环：接收消息 → 查找/创建会话 → 调用 Agent → 返回响应',
        '6. 优雅关闭：SIGTERM 时保存所有会话状态并关闭连接',
    ]
    for step in gw_steps:
        story.append(Paragraph(step, BULLET))

    story.append(Paragraph('<b>8.2　支持平台一览</b>', H2))
    platforms = [
        ["平台", "适配器", "协议", "状态"],
        ["Telegram", "telegram.py", "Bot API", "✅ 稳定"],
        ["Discord", "discord.py", "Gateway API", "✅ 稳定"],
        ["Slack", "slack.py", "RTM API", "✅ 稳定"],
        ["微信", "weixin.py", "iLink Bot API", "✅ 稳定"],
        ["飞书", "feishu.py", "开放 API", "✅ 稳定"],
        ["WhatsApp", "whatsapp.py", "Cloud API", "✅ 稳定"],
        ["Signal", "signal.py", "REST API", "✅ 稳定"],
        ["Mattermost", "mattermost.py", "WebSocket", "✅ 稳定"],
        ["Matrix", "matrix.py", "CS API", "✅ 稳定"],
        ["钉钉", "dingtalk.py", "开放 API", "✅ 稳定"],
        ["QQ Bot", "qqbot.py", "频道 API", "✅ 稳定"],
        ["邮件", "email.py", "IMAP/SMTP", "✅ 稳定"],
        ["短信", "sms.py", "Twilio API", "✅ 稳定"],
    ]
    story.append(make_table(platforms, [25*mm, 30*mm, 50*mm, 30*mm], PRIMARY, None, 7.5))

    story.append(Paragraph('<b>8.3　消息路由与分发</b>', H2))
    story.append(Paragraph(
        '每个消息携带完整的追踪信息：platform、chat_id、user_id、chat_type（私信/群组/频道/话题）、thread_id。'
        '路由系统根据追踪信息将响应投递到正确位置，支持话题/线程消息的上下文关联。', BODY))

    story.append(Paragraph('<b>8.4　话题/线程管理</b>', H2))
    story.append(Paragraph(
        '平台原生话题/线程（如 Telegram 话题、Discord 线程）被映射为独立的会话上下文。'
        '每个话题拥有独立的对话历史和上下文窗口，互不干扰。'
        '跨话题的消息分发通过 session_id 和 thread_id 联合索引。', BODY))
    story.append(PageBreak())
    return story

# ── 第9章 ──
def build_chapter9():
    story = []
    story.append(Paragraph('<b>第 9 章　定时任务</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>9.1　Cron 调度器</b>', H2))
    story.append(Paragraph(
        'Hermes 内置了 Cron 调度器（cron/ 目录），支持按时间间隔或 Cron 表达式调度任务。'
        '任务可以投递到任意已连接的消息平台，或者在本地执行文件操作。', BODY))
    story.extend(code_block(
        '# 使用 cronjob 工具创建任务\n'
        '# 每 40 分钟汇报一次\n'
        "cronjob(action='create', prompt='...',\n"
        "        schedule='40m',\n"
        "        deliver='feishu:chat_id')\n"
        '# 每天 12:00 部署\n'
        "cronjob(action='create', prompt='...',\n"
        "        schedule='0 12 * * *')", "Python 调用示例", 8))

    story.append(Paragraph('<b>9.2　静默机制（SILENT）</b>', H2))
    story.append(Paragraph(
        '定时任务支持静默时段。通过任务 prompt 中注入 [SILENT] 标记，'
        'Agent 在指定时间段（如 00:00-07:59）返回 [SILENT] 即可抑制投递。'
        '这种方式无需配置多组 Cron 表达式，灵活且简洁。', BODY))

    story.append(Paragraph('<b>9.3　部署脚本</b>', H2))
    story.append(Paragraph(
        '每天 12:00 和 00:00，Hermes 自动执行 deploy-upload.sh，'
        '将 ~/.hermes/ 中的配置、Skills、脚本同步到 /tmp/hermes-catgirl-deploy/ '
        '目录的 Git 仓库，并通过代理推送到 GitHub。'
        '所有敏感文件（.env、auth.json、state.db、sessions/ 等）已被 .gitignore 排除。', BODY))
    story.append(PageBreak())
    return story


# ── 第10章 ──
def build_chapter10():
    story = []
    story.append(Paragraph('<b>第 10 章　子代理与并行</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>10.1　子代理架构</b>', H2))
    story.append(Paragraph(
        'Hermes 的子代理（delegate_task）机制允许 Agent 在对话中派发独立任务给子 Agent 执行。'
        '每个子 Agent 拥有独立的上下文窗口、终端会话和工具集，返回结果摘要给父 Agent。', BODY))

    story.extend(code_block(
        '# 派发并行任务\n'
        "results = delegate_task(\n"
        "    tasks=[\n"
        '        {"goal": "研究 A", "toolsets": ["web"]},\n'
        '        {"goal": "分析 B", "toolsets": ["terminal", "file"]},\n'
        "    ]\n"
        ")  # 两个任务同时运行", "Python 调用示例", 8))

    story.append(Paragraph('<b>10.2　适用范围</b>', H2))
    use_cases = [
        "▪ 推理密集型子任务（Debug、代码审查、研究综合）",
        "▪ 会冲刷父 Agent 上下文的中间数据处理",
        "▪ 并行的独立工作流（同时研究 A 和 B）",
    ]
    for u in use_cases:
        story.append(Paragraph(u, BODY))

    story.append(Paragraph('<b>10.3　限制与注意事项</b>', H2))
    limits = [
        "▪ 子 Agent 共享父 Agent 的 IterationBudget",
        "▪ 子 Agent 不能调用 delegate_task、clarify、memory、execute_code",
        "▪ 子 Agent 不知道父 Agent 的对话历史——所有上下文必须通过 context 参数传入",
        "▪ 最多 3 个并行任务",
    ]
    for l in limits:
        story.append(Paragraph(f'▪ {esc(l)}', BODY))
    story.append(PageBreak())
    return story


# ── 第11章 ──
def build_chapter11():
    story = []
    story.append(Paragraph('<b>第 11 章　安全机制</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>11.1　敏感命令审批</b>', H2))
    story.append(Paragraph(
        'approval.py 维护了一个命令黑名单/白名单系统。当 Agent 试图执行高危操作时，'
        '系统会触发审批流程——CLI 模式弹出审批框，Gateway 模式自动拒绝。', BODY))

    story.extend(code_block(
        '# 命令白名单（config.yaml）\n'
        'command_allowlist:\n'
        '- shell command via -c/-lc flag\n'
        '- force kill processes\n'
        '- delete in root path\n'
        '- kill hermes/gateway process\n'
        '- recursive delete', "YAML 配置", 8))

    story.append(Paragraph('<b>11.2　TIRITH 策略引擎</b>', H2))
    story.append(Paragraph(
        'TIRITH 是 Hermes 内置的策略即代码引擎。它在工具调用前进行安全检查，'
        '可以检测并阻止不合规的操作。tirith_fail_open: true 确保在策略引擎故障时不会误杀正常请求。', BODY))

    story.append(Paragraph('<b>11.3　隐私保护</b>', H2))
    privacy = [
        "▪ redact_pii：自动脱敏输出中的个人身份信息",
        "▪ 敏感命令需审批：CLI/Gateway 双重安全策略",
        "▪ webhook 过滤：website_blocklist 支持域名拦截",
        "▪ 日志不记录敏感信息：secrets redacted 在日志中自动替换",
    ]
    for p in privacy:
        story.append(Paragraph(f'▪ {esc(p)}', BODY))
    story.append(PageBreak())
    return story


# ── 第12章 ──
def build_chapter12():
    story = []
    story.append(Paragraph('<b>第 12 章　配置系统</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>12.1　配置文件结构</b>', H2))
    story.append(Paragraph(
        'Hermes 的配置分为两个文件：', BODY))
    story.append(Paragraph(
        '▪ <b>config.yaml</b>：模型、Provider、工具、终端、平台等所有非敏感设置', BODY))
    story.append(Paragraph(
        '▪ <b>.env</b>：所有 API Key 和安全凭证（不提交到版本控制）', BODY))

    story.extend(code_block(
        '~/.hermes/\n'
        '├── config.yaml    # 非敏感设置\n'
        '├── .env           # 敏感凭证（已 .gitignore）\n'
        '├── .gitignore     # 安全防护\n'
        '├── skills/        # 自定义技能\n'
        '├── cron/          # 定时任务输出\n'
        '├── cache/         # 缓存目录\n'
        '└── scripts/       # 工具脚本', "目录结构", 7.5))

    story.append(Paragraph('<b>12.2　Fallback Provider 配置</b>', H2))
    story.append(Paragraph(
        '在 v5.0 中，fallback 配置经过了重要的安全优化。'
        '所有 API Key 从 key_env 引用 .env 文件（而非内联在 config.yaml 中），'
        '同时源码 run_agent.py 的 _try_activate_fallback() 已 patch 支持 key_env 解析。', BODY))

    story.extend(code_block(
        '# v5.0 安全的 fallback 配置\n'
        'fallback_providers:\n'
        '- provider: custom_longCat\n'
        '  model: LongCat-2.0-Preview\n'
        '  base_url: https://api.longcat.chat/openai\n'
        '  key_env: CUSTOM_LONGCAT_API_KEY   # 安全！\n'
        '- provider: deepseek\n'
        '  model: deepseek-v4-flash\n'
        '  base_url: https://api.deepseek.com/v1\n'
        '  key_env: DEEPSEEK_API_KEY         # 安全！', "YAML 配置", 7.5))

    story.append(Paragraph('<b>12.3　凭证池管理</b>', H2))
    story.append(Paragraph(
        'credential_pool 通过 auth.json 持久化存储凭证状态。'
        '每条凭证记录包含：source（来源）、auth_type（认证类型）、'
        'access_token（令牌）、base_url（端点）、'
        'last_status（最后状态）和 last_status_at（时间戳）。'
        '凭证在没有可用 Key 时自动触发 fallback 链。', BODY))
    story.append(PageBreak())
    return story


# ── 第13章 ──
def build_chapter13():
    story = []
    story.append(Paragraph('<b>第 13 章　Auxiliary AI 服务</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph(
        'Auxiliary 服务是 Hermes 的"辅助 AI 大脑"，用于处理 Agent 主循环之外的任务。'
        '它们通过 auxiliary_client.py 路由，使用独立的 Provider 配置。', BODY))

    aux_services = [
        ["服务", "用途", "超时"],
        ["Vision", "图片分析与理解", "120s"],
        ["Web Extract", "网页内容提取", "360s"],
        ["Compression", "上下文自动压缩", "120s"],
        ["Session Search", "历史会话检索", "30s"],
        ["Title Generation", "对话标题生成", "30s"],
        ["Skills Hub", "技能商店搜索", "30s"],
    ]
    story.append(make_table(aux_services, [30*mm, 60*mm, 25*mm], PRIMARY, None, 8))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph('<b>13.1　视觉分析（Vision）</b>', H2))
    story.append(Paragraph(
        'Vision 服务支持分析本地图片和网络图片，返回详细的图像描述（可回答特定问题）。'
        '底层使用 vision_analyze 工具，支持 provider: auto 自动路由，'
        '也支持指定特定模型（如 GPT-4o、Claude Vision 等）。', BODY))

    story.append(Paragraph('<b>13.2　压缩引擎</b>', H2))
    story.append(Paragraph(
        'Compression 服务在上下文压缩过程中扮演关键角色。'
        '当上下文大小超过 threshold（50%）时，自动调用辅助 AI 对早期对话进行智能摘要，'
        '将压缩后的摘要替换原始消息，以达到 target_ratio（20%）的目标。', BODY))

    story.append(PageBreak())
    return story


# ── 第14章 ──
def build_chapter14():
    story = []
    story.append(Paragraph('<b>第 14 章　模型与 Token 管理</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>14.1　上下文长度管理</b>', H2))
    story.append(Paragraph(
        'Hermes 通过 model_metadata.py 管理各模型的上下文长度。'
        '当估算的 Token 超过模型限制时，自动触发上下文压缩或截断。'
        '这避免了因上下文溢出导致的 400 错误。', BODY))

    story.append(Paragraph('<b>14.2　Token 估算</b>', H2))
    story.append(Paragraph(
        'Token 估算有两条路径：', BODY))
    story.append(Paragraph(
        '▪ <b>tiktoken 路径</b>：对支持 tiktoken 的模型（GPT 系列），使用精确 Token 计数', BODY))
    story.append(Paragraph(
        '▪ <b>启发式路径</b>：对其他模型，使用字符数 × 系数（通常为 0.25-0.33）估算', BODY))

    story.append(Paragraph('<b>14.3　Prompt Caching</b>', H2))
    story.append(Paragraph(
        '对于支持 Prompt Caching 的 Provider（如 Anthropic），'
        'Hermes 会自动利用缓存技术加速重复的系统提示词。'
        'Skill slash 命令通过用户消息注入而非系统提示词，以保持缓存命中率。', BODY))

    story.append(Paragraph('<b>14.4　Reasoning Effort</b>', H2))
    story.append(Paragraph(
        '支持 reasoning_effort 配置（当前为 medium）。'
        '这对于需要深度推理的任务非常有用，'
        '但会增加响应延迟和 Token 消耗。', BODY))
    story.append(PageBreak())
    return story


# ── 第15章 ──
def build_chapter15():
    story = []
    story.append(Paragraph('<b>第 15 章　开发与调试</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>15.1　开发环境</b>', H2))
    story.append(Paragraph(
        'Hermes Agent 的开发环境基于 Python 3.12+，核心循环使用同步模式。'
        '开发时使用 source venv/bin/activate 激活环境，'
        '运行 hermes --dev 进入开发模式（更多日志输出）。', BODY))

    story.extend(code_block(
        '# 开发环境激活\n'
        'cd ~/.hermes/hermes-agent\n'
        'source venv/bin/activate\n'
        '# 运行测试\n'
        'pytest tests/ -x -v\n'
        '# 运行 CLI 开发模式\n'
        'python cli.py --dev', "Bash 命令", 8))

    story.append(Paragraph('<b>15.2　ACP 集成</b>', H2))
    story.append(Paragraph(
        'Hermes 支持 ACP（Agent Communication Protocol），允许 VS Code、Zed、JetBrains '
        '等 IDE 集成。ACP 通过标准输入输出进行通信，支持子 Agent 派发、工具调用等功能。', BODY))

    story.append(Paragraph('<b>15.3　测试套件</b>', H2))
    story.append(Paragraph(
        '项目包含约 3000 个自动化测试，覆盖：', BODY))
    tests = [
        "▪ 核心循环（run_agent）：Fallback 逻辑、上下文压缩、工具调度",
        "▪ 凭证池（credential_pool）：Key 轮换、耗尽检测、冷却恢复",
        "▪ 配置验证（config_validation）：Provider 配置、Fallback 链",
        "▪ CLI 命令（cli）：Slash 命令、皮肤引擎、技能系统",
        "▪ Gateway：各平台消息收发、会话管理",
    ]
    for t in tests:
        story.append(Paragraph(f'▪ {esc(t)}', BODY))
    story.append(PageBreak())
    return story


# ── 第16章 ──
def build_chapter16():
    story = []
    story.append(Paragraph('<b>第 16 章　部署与运维</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>16.1　终端后端</b>', H2))
    story.append(Paragraph(
        'Hermes 支持多种终端后端，满足不同部署场景：', BODY))
    backends = [
        ["后端", "适用场景", "特点"],
        ["local", "本地开发与日常使用", "零配置，直接使用"],
        ["docker", "容器化部署", "环境隔离，可重现"],
        ["ssh", "远程服务器", "无需安装 Agent"],
        ["modal", "云沙箱", "按需计费，自动扩缩"],
        ["daytona", "工作空间", "开发环境即服务"],
    ]
    story.append(make_table(backends, [22*mm, 55*mm, 59*mm], PRIMARY, None, 8))

    story.append(Paragraph('<b>16.2　Gateway 运维</b>', H2))
    story.append(Paragraph(
        'Gateway 支持 restart_drain_timeout（60s）优雅重启，'
        '以及 gateway_timeout（1800s）请求超时。'
        '平台接入遵循"配置即声明"原则——添加平台配置后重启 Gateway 即可生效。', BODY))

    story.append(Paragraph('<b>16.3　性能优化建议</b>', H2))
    tips = [
        "▪ 使用 Prompt Caching 加速系统提示词",
        "▪ 调整 compression.threshold 控制压缩频率",
        "▪ 为不同模型设置合适的 timeout_seconds",
        "▪ 使用 credential_pool 减少 429 导致的延迟",
        "▪ 合理利用子代理并行处理独立任务",
    ]
    for t in tips:
        story.append(Paragraph(f'▪ {esc(t)}', BODY))
    story.append(PageBreak())
    return story


# ── 附录 ──
def build_appendix():
    story = []
    story.append(Paragraph('<b>附录</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    story.append(Paragraph('<b>A.1　版本历史</b>', H2))
    versions = [
        ["版本", "日期", "变更内容"],
        ["v5.0.0", "2026-05-03", "全面重构：Mermaid 架构图、key_env 安全修复、16章深度内容"],
        ["v4.0.0", "2026-04-20", "模块化 Skill 架构、缩略设计模式、高性能 V4 引擎"],
        ["v3.0.0", "2026-04-10", "新增飞书平台集成、定时任务系统"],
        ["v2.0.0", "2026-03-25", "Provider Fallback、凭证池、Gateway 架构"],
        ["v1.0.0", "2026-03-01", "初版：Hermes Agent 基础架构介绍"],
    ]
    story.append(make_table(versions, [18*mm, 28*mm, 90*mm], PRIMARY, None, 8))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph('<b>A.2　参考资源</b>', H2))
    refs = [
        "▪ Hermes Agent 源码：https://github.com/NousResearch/hermes-agent",
        "▪ ReportLab 官方文档：https://docs.reportlab.com/",
        "▪ Mermaid CLI：npm install -g @mermaid-js/mermaid-cli",
        "▪ python-pptx 文档：https://python-pptx.readthedocs.io/",
    ]
    for r in refs:
        story.append(Paragraph(r, BODY))

    story.append(Paragraph('<b>A.3　术语表</b>', H2))
    terms = [
        ["术语", "解释"],
        ["ACP", "Agent Communication Protocol，Agent 间通信协议"],
        ["Credential Pool", "凭证池，管理多个 API Key 的缓冲区"],
        ["Fallback Chain", "Provider 容灾切换链"],
        ["Gateway", "多平台消息路由中枢"],
        ["MCP", "Model Context Protocol，模型上下文协议"],
        ["Provider", "LLM API 服务提供商"],
        ["Skill", "可复用的专业知识包（SKILL.md）"],
        ["TIRITH", "内置安全策略引擎"],
    ]
    story.append(make_table(terms, [35*mm, 100*mm], PRIMARY, None, 8))

    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(width="60%", thickness=1, color=HIGHLIGHT, spaceBefore=3*mm, spaceAfter=3*mm))
    story.append(Paragraph(
        '<i>本文档由小喵 AI 使用 ReportLab + Mermaid CLI 自动生成</i>',
        S('Footer', fontSize=9, textColor=MED_GRAY, alignment=TA_CENTER)))
    return story


# ── 页眉页脚 ──
def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(BODY_FONT, 7.5)
    canvas.setFillColor(MED_GRAY)

    # 页眉
    canvas.drawString(20*mm, A4[1] - 12*mm, "Hermes Agent 深度架构指南")
    today = datetime.now().strftime("%Y-%m-%d")
    canvas.drawRightString(A4[0] - 20*mm, A4[1] - 12*mm, today)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, A4[1] - 15*mm, A4[0] - 20*mm, A4[1] - 15*mm)

    # 页脚
    canvas.line(20*mm, 14*mm, A4[0] - 20*mm, 14*mm)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(A4[0] / 2, 8*mm, f"— {page_num} —")
    canvas.drawRightString(A4[0] - 20*mm, 8*mm, f"v{__version__}")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(BODY_FONT, 7.5)
    canvas.setFillColor(MED_GRAY)
    canvas.line(20*mm, 14*mm, A4[0] - 20*mm, 14*mm)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(A4[0] / 2, 8*mm, f"— {page_num} —")
    canvas.restoreState()


# ── 封面 ──
def build_cover():
    story = []
    story.append(Spacer(1, 35*mm))
    story.append(Paragraph(
        'Hermes Agent',
        S('CoverTitle', fontSize=30, leading=38, textColor=PRIMARY,
          spaceAfter=6*mm, alignment=TA_CENTER)))
    story.append(Paragraph(
        '深度架构指南',
        S('CoverSub', fontSize=18, leading=24, textColor=ACCENT,
          spaceAfter=10*mm, alignment=TA_CENTER)))
    story.append(hr(HIGHLIGHT, 40, 2))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        f'版本 v{__version__}',
        S('CoverVer', fontSize=11, textColor=MED_GRAY,
          spaceAfter=2*mm, alignment=TA_CENTER)))
    story.append(Paragraph(
        f'发布日期: {__date__}',
        S('CoverDate', fontSize=11, textColor=MED_GRAY,
          spaceAfter=2*mm, alignment=TA_CENTER)))
    story.append(Spacer(1, 10*mm))

    info_data = [
        [Paragraph('<b>作者</b>', S('InfoLabel', fontSize=9, textColor=DARK_TEXT)),
         Paragraph(esc(__author__), S('InfoVal', fontSize=9, textColor=MED_GRAY))],
        [Paragraph('<b>仓库</b>', S('InfoLabel', fontSize=9, textColor=DARK_TEXT)),
         Paragraph('github.com/NousResearch/hermes-agent', S('InfoVal', fontSize=9, textColor=MED_GRAY))],
        [Paragraph('<b>代码规模</b>', S('InfoLabel', fontSize=9, textColor=DARK_TEXT)),
         Paragraph('12,000+ 行 Python', S('InfoVal', fontSize=9, textColor=MED_GRAY))],
        [Paragraph('<b>架构</b>', S('InfoLabel', fontSize=9, textColor=DARK_TEXT)),
         Paragraph('六层模块化设计', S('InfoVal', fontSize=9, textColor=MED_GRAY))],
    ]
    info_table = Table(info_data, colWidths=[35*mm, 60*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 4*mm),
    ]))
    story.append(info_table)
    story.append(PageBreak())
    return story


# ── 目录 ──
def build_toc():
    story = []
    story.append(Paragraph('<b>目录</b>', H1))
    story.append(hr(HIGHLIGHT, 20, 1.5))

    toc_items = [
        ("1", "Hermes Agent 概览", "什么是 Hermes Agent、核心特性、对比分析"),
        ("2", "系统架构总览", "六层架构、核心数据流、设计模式"),
        ("3", "核心循环（Core Loop）", "对话循环、消息格式、工具调用流程"),
        ("4", "Provider 与 Fallback 机制", "Fallback 链、凭证池、429 处理"),
        ("5", "工具系统", "工具注册、16+ 工具列表、MCP 集成"),
        ("6", "记忆系统", "持久记忆、会话搜索、上下文压缩"),
        ("7", "技能系统（Skills）", "Skill 目录、自动发现、Skill Creator"),
        ("8", "消息平台网关", "Gateway 架构、20+ 平台、消息路由"),
        ("9", "定时任务", "Cron 调度器、静默机制、部署脚本"),
        ("10", "子代理与并行", "子代理架构、适用范围、注意事项"),
        ("11", "安全机制", "命令审批、TIRITH 策略引擎、隐私保护"),
        ("12", "配置系统", "config.yaml、Fallback 配置、凭证池管理"),
        ("13", "Auxiliary AI 服务", "Vision、Web Extract、压缩引擎"),
        ("14", "模型与 Token 管理", "上下文长度、Token 估算、Prompt Caching"),
        ("15", "开发与调试", "开发环境、ACP 集成、测试套件"),
        ("16", "部署与运维", "终端后端、Gateway 运维、性能优化"),
    ]
    toc_style = S('TOC', fontSize=10, leading=16, textColor=DARK_TEXT, spaceAfter=1*mm)
    for num, title, desc in toc_items:
        story.append(Paragraph(
            f'<b>第 {num} 章　{esc(title)}</b>  —  {esc(desc)}', toc_style))
    story.append(PageBreak())
    return story


# ── 主入口 ──
def build_pdf(output_path=OUTPUT_PATH):
    print(f"📄 生成 PDF: {output_path}")
    print(f"📚 版本: v{__version__} | 日期: {__date__}")

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title='Hermes Agent 深度架构指南',
        author=__author__,
        subject='Hermes Agent 完整技术架构解析（16章 + 附录）',
        creator=f'reportlab + pdf-layout skill + Mermaid CLI',
        keywords=['Hermes', 'AI Agent', '架构', 'Python', 'ReportLab', 'Mermaid'],
    )

    story = []
    # 封面
    story.extend(build_cover())
    # 目录
    story.extend(build_toc())
    # 正文
    story.extend(build_chapter1())
    story.extend(build_chapter2())
    story.extend(build_chapter3())
    story.extend(build_chapter4())
    story.extend(build_chapter5())
    story.extend(build_chapter6())
    story.extend(build_chapter7())
    story.extend(build_chapter8())
    story.extend(build_chapter9())
    story.extend(build_chapter10())
    story.extend(build_chapter11())
    story.extend(build_chapter12())
    story.extend(build_chapter13())
    story.extend(build_chapter14())
    story.extend(build_chapter15())
    story.extend(build_chapter16())
    story.extend(build_appendix())

    # 构建（首页不同页眉，后续页标准页眉）
    doc.build(story, onFirstPage=first_page, onLaterPages=header_footer)
    print(f"✅ PDF 生成成功！({os.path.getsize(output_path)/1024:.0f}KB)")
    return output_path


if __name__ == "__main__":
    build_pdf()
