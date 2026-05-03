#!/usr/bin/env python3
"""Generate Hermes Agent Architecture PDF - Professional Chinese Report"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import os, glob

# ── Font registration ──
def find_cjk_fonts():
    search_paths = [
        "/usr/share/fonts/truetype/noto/",
        "/usr/share/fonts/opentype/noto/",
        "/usr/share/fonts/noto-cjk/",
        "/usr/share/fonts/truetype/wqy/",
        "/usr/share/fonts/truetype/dejavu/",
    ]
    regular = bold = None
    for sp in search_paths:
        if not os.path.exists(sp):
            continue
        for f in os.listdir(sp):
            fp = os.path.join(sp, f)
            fl = f.lower()
            if 'cjk' in fl or 'wqy' in fl or 'notosanssc' in fl:
                if 'bold' in fl and not bold:
                    bold = fp
                elif 'regular' in fl and not regular:
                    regular = fp
                elif not regular:
                    regular = fp
            elif 'notosans' in fl and 'sc' in fl:
                if 'bold' in fl and not bold:
                    bold = fp
                elif not regular:
                    regular = fp
    if not regular:
        for sp in search_paths:
            if not os.path.exists(sp):
                continue
            for f in os.listdir(sp):
                if 'DejaVuSans' in f and f.endswith('.ttf'):
                    regular = os.path.join(sp, f)
                    bold = os.path.join(sp, f.replace('Sans', 'Sans-Bold'))
                    return regular, bold
    return regular, bold

cjk_regular, cjk_bold = find_cjk_fonts()

if cjk_regular and os.path.exists(cjk_regular):
    pdfmetrics.registerFont(TTFont('CJK', cjk_regular))
    if cjk_bold and os.path.exists(cjk_bold):
        pdfmetrics.registerFont(TTFont('CJKBold', cjk_bold))
    else:
        pdfmetrics.registerFont(TTFont('CJKBold', cjk_regular))
    BODY_FONT = 'CJK'
    BOLD_FONT = 'CJKBold'
else:
    BODY_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'

# ── Color Palette ──
PRIMARY = HexColor('#1a1a2e')
SECONDARY = HexColor('#16213e')
ACCENT = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f8f9fa')
MEDIUM_GRAY = HexColor('#6c757d')
DARK_TEXT = HexColor('#212529')
SECTION_BG = HexColor('#e8f4f8')
CODE_BG = HexColor('#f4f4f4')
BORDER_COLOR = HexColor('#dee2e6')

W, H = A4

def S(name, font_name=None, **kw):
    if font_name is None:
        font_name = BODY_FONT
    return ParagraphStyle(name, fontName=font_name, **kw)

def SB(name, **kw):
    return ParagraphStyle(name, fontName=BOLD_FONT, **kw)

def escape_xml(text):
    """Escape XML special characters for reportlab Paragraph"""
    if text is None:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def b(text):
    """Bold text helper"""
    return f'<b>{escape_xml(text)}</b>'

def para(text, style=None):
    """Create a Paragraph, auto-escaping text"""
    if style is None:
        style = body_style
    return Paragraph(escape_xml(text), style)

def sp(h=3*mm):
    return Spacer(1, h)

def hr(color=BORDER_COLOR, thickness=1, width="100%"):
    return HRFlowable(width=width, thickness=thickness, color=color, spaceAfter=3*mm, spaceBefore=2*mm)

def h1(text):
    return Paragraph(escape_xml(text), h1_style)

def h2(text):
    return Paragraph(escape_xml(text), h2_style)

def h3(text):
    return Paragraph(escape_xml(text), h3_style)

def body(text):
    return Paragraph(escape_xml(text), body_style)

def bullet(text):
    return Paragraph(f'&#8222; {escape_xml(text)}', bullet_style)

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title='Hermes Agent Architecture Guide',
        author='Xiaomiao AI'
    )

    # ── Styles ──
    global title_style, subtitle_style, h1_style, h2_style, h3_style
    global body_style, bullet_style, code_style
    
    title_style = SB('Title2', fontSize=28, leading=34,
        textColor=PRIMARY, spaceAfter=6*mm, alignment=TA_CENTER)
    subtitle_style = S('Subtitle', fontSize=14, leading=20,
        textColor=MEDIUM_GRAY, spaceAfter=20*mm, alignment=TA_CENTER)
    h1_style = SB('H1', fontSize=20, leading=26,
        textColor=PRIMARY, spaceBefore=12*mm, spaceAfter=4*mm)
    h2_style = SB('H2', fontSize=15, leading=20,
        textColor=ACCENT, spaceBefore=8*mm, spaceAfter=3*mm)
    h3_style = SB('H3', fontSize=12, leading=16,
        textColor=SECONDARY, spaceBefore=5*mm, spaceAfter=2*mm)
    body_style = S('Body2', fontSize=10, leading=16,
        textColor=DARK_TEXT, spaceAfter=3*mm, alignment=TA_JUSTIFY)
    bullet_style = S('Bullet', fontSize=10, leading=15,
        textColor=DARK_TEXT, spaceAfter=2*mm, leftIndent=10*mm, bulletIndent=5*mm)
    code_style = ParagraphStyle('Code', fontName='Courier', fontSize=8, leading=12,
        textColor=DARK_TEXT, spaceAfter=2*mm,
        backColor=CODE_BG, borderPad=3*mm)

    story = []

    # ═══════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════
    story += [sp(40*mm), para("", title_style), h1("Hermes Agent"), 
              para("Architecture Deep Dive & Design Philosophy", subtitle_style),
              sp(10*mm), hr(HIGHLIGHT, 2, "60%"),
              para("May 2026 - by Xiaomiao", S('Date', fontSize=11, textColor=MEDIUM_GRAY, alignment=TA_CENTER)),
              sp(15*mm)]
    
    # Version info box
    box_style = S('Box', fontSize=9, textColor=DARK_TEXT)
    info_data = [
        [para("Version", SB('Box', fontSize=9, textColor=DARK_TEXT)), para("v1.0.0", box_style)],
        [para("Date", SB('Box', fontSize=9, textColor=DARK_TEXT)), para("2026-05-03", box_style)],
        [para("Codebase", SB('Box', fontSize=9, textColor=DARK_TEXT)), para("12,000+ lines Python", box_style)],
        [para("Architecture", SB('Box', fontSize=9, textColor=DARK_TEXT)), para("6-layer modular design", box_style)],
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

    # ═══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════
    story.append(h1("Table of Contents"))
    story.append(hr())
    
    toc_items = [
        ("1", "Project Overview", "What is Hermes Agent? Core design philosophy"),
        ("2", "Architecture Design", "Six-layer architecture, data flow, design patterns"),
        ("3", "Core Modules", "run_agent.py, model_tools.py, registry.py deep dive"),
        ("4", "Agent Runtime Loop", "Conversation loop, tool execution, error recovery"),
        ("5", "Tool System", "Tool registry, toolsets, MCP integration"),
        ("6", "Prompt Building", "System prompt assembly, context files, security scanning"),
        ("7", "Context Compression", "Compression algorithm, tool output pruning, iterative summarization"),
        ("8", "Memory System", "MemoryManager, persistent storage, FTS5 search"),
        ("9", "Session Management", "Session model, SQLite storage, session lineage"),
        ("10", "Gateway & Platform Integration", "Gateway architecture, multi-platform adapters, message routing"),
        ("11", "Cron Jobs", "Job scheduling, delivery mechanism, state management"),
        ("12", "Error Classification & Failover", "Error taxonomy, smart degradation, retry strategies"),
        ("13", "Configuration System", "config.yaml structure, environment variables, multi-model support"),
        ("14", "Skills System", "Skill discovery, loading, caching mechanism"),
        ("15", "Design Philosophy Summary", "Architecture highlights, best practices, reusable patterns"),
    ]
    toc_style = S('TOC', fontSize=11, leading=18, textColor=ACCENT, spaceAfter=1*mm)
    for num, title, desc in toc_items:
        story.append(Paragraph(f'<b>{num}. {escape_xml(title)}</b>  --  {escape_xml(desc)}', toc_style))
    
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 1
    # ═══════════════════════════════════════════
    story.append(h1("1. Project Overview"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent is an open-source AI Agent framework developed by Nous Research, named after the Greek messenger god Hermes, symbolizing its core mission of information transfer and connection. It is a production-grade AI Agent system that supports interaction through multiple messaging platforms (Telegram, Discord, WeChat, Feishu, WhatsApp, Signal, etc.), with capabilities including tool calling, persistent memory, scheduled tasks, context compression, and multi-model switching."))
    story.append(h2("1.1 Core Positioning"))
    story.append(body("Hermes Agent is designed as a universal AI Assistant Runtime: not just a chatbot framework, but a complete Agent operating system providing full-pipeline capabilities from message intake, session management, tool execution to response delivery."))
    story.append(h2("1.2 Key Capabilities"))
    
    feat_data = [
        [para("Capability", SB('FH', fontSize=9, textColor=white)), para("Description", SB('FH', fontSize=9, textColor=white))],
        ["Multi-platform Gateway", "20+ messaging platforms (Telegram, Discord, WeChat, Feishu, WhatsApp, etc.)"],
        ["Tool Calling Loop", "Auto-execute tool calls until task completion, supports parallel tool calls"],
        ["Persistent Memory", "SQLite + FTS5 full-text search, cross-session memory retention"],
        ["Context Compression", "Intelligent summary compression for long conversations"],
        ["Scheduled Tasks", "Cron expressions, interval scheduling, one-shot tasks"],
        ["Multi-model Support", "OpenAI, Anthropic, Google, local models via unified interface"],
        ["Smart Error Recovery", "Classified error types with automatic degradation/retry/model switching"],
        ["Skills System", "Pluggable skill modules with dynamic loading and caching"],
        ["MCP Integration", "Model Context Protocol standard support"],
        ["Sub-agent Delegation", "Parallel sub-agent task distribution support"],
    ]
    feat_table = Table(feat_data, colWidths=[45*mm, 115*mm])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
    ]))
    story.append(feat_table)
    story.append(sp(3*mm))
    story.append(h2("1.3 Tech Stack"))
    story.append(body("Built with Python 3.12+, core dependencies include OpenAI SDK (compatible with multiple backends), SQLite (state storage), aiohttp (async HTTP), python-dotenv. The codebase is ~12,000 lines, organized into agent/, gateway/, tools/, cron/, and other modules."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 2
    # ═══════════════════════════════════════════
    story.append(h1("2. Architecture Design"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent uses a six-layer modular architecture with single-responsibility layers communicating through well-defined interfaces."))
    story.append(h2("2.1 Six-Layer Overview"))
    
    arch_data = [
        [para("Layer", SB('AH', fontSize=9, textColor=white)), para("Module", SB('AH', fontSize=9, textColor=white)), para("Responsibility", SB('AH', fontSize=9, textColor=white)), para("Key Files", SB('AH', fontSize=9, textColor=white))],
        ["L1 Message Intake", "gateway/platforms/", "Multi-platform message receive/send", "telegram.py, discord.py, weixin.py"],
        ["L2 Session Management", "gateway/session.py / hermes_state.py", "Session lifecycle, message persistence", "session.py, state.db"],
        ["L3 Agent Core", "run_agent.py / agent/", "Conversation loop, tool calling, error recovery", "run_agent.py, error_classifier.py"],
        ["L4 Tool Execution", "tools/ / toolsets.py", "Tool definition, registration, execution dispatch", "registry.py, terminal_tool.py"],
        ["L5 Prompt Building", "agent/prompt_builder.py", "System prompt assembly, context injection", "prompt_builder.py"],
        ["L6 Infrastructure", "cron/ / hermes_cli/ / config.yaml", "Scheduled tasks, CLI, config management", "jobs.py, cli.py"],
    ]
    colors = [HexColor('#e3f2fd'), HexColor('#e8f5e9'), HexColor('#fff3e0'), HexColor('#f3e5f5'), HexColor('#fce4ec'), HexColor('#e0f2f1')]
    arch_table = Table(arch_data, colWidths=[28*mm, 35*mm, 50*mm, 47*mm])
    tbl_style = [
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 2*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2*mm),
    ]
    for i, c in enumerate(colors):
        tbl_style.append(('BACKGROUND', (0, i+1), (-1, i+1), c))
    arch_table.setStyle(TableStyle(tbl_style))
    story.append(arch_table)
    story.append(sp(4*mm))

    story.append(h2("2.2 Core Data Flow"))
    story.append(body("The complete message processing flow: Platform adapter receives message -> Session manager restores context -> Agent core builds system prompt -> LLM inference generates tool calls -> Tool executor dispatches execution -> Results return to Agent -> Loop until complete -> Response returns to platform adapter -> Sends to user. Each step has comprehensive error handling and recovery."))
    story.append(h2("2.3 Design Patterns"))
    patterns = [
        ("Singleton", "ToolRegistry ensures globally unique tool registry"),
        ("Strategy", "ContextEngine supports multiple context processing strategies"),
        ("Observer", "Gateway uses asyncio event loop for multi-platform concurrent messages"),
        ("Factory", "Platform adapters created via factory methods"),
        ("Chain of Responsibility", "Error classifier matches error types in priority chain"),
        ("Template Method", "run_agent.py conversation loop defines Agent execution skeleton"),
        ("Decorator", "Tool registration via registry.register() decorator"),
    ]
    for name, desc in patterns:
        story.append(bullet(f"{name}: {desc}"))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 3: Core Modules
    # ═══════════════════════════════════════════
    story.append(h1("3. Core Module Deep Dive"))
    story.append(hr(HIGHLIGHT))
    story.append(h2("3.1 run_agent.py -- Agent Main Loop"))
    story.append(body("run_agent.py (12,002 lines) is the core engine implementing the complete ReAct (Reasoning + Acting) loop: receive user message -> build prompt -> call LLM -> parse tool calls -> execute tools -> append results to conversation history -> repeat until LLM stops requesting tool calls."))
    story.append(body("Key designs: SafeWriter wraps stdout/stderr to prevent pipe breakage crashes; jittered_backoff implements exponential backoff + jitter to avoid thundering herd; classify_api_error categorizes API errors into 12+ types with recovery suggestions."))
    story.append(h2("3.2 model_tools.py -- Tool Orchestration Layer"))
    story.append(body("model_tools.py (611 lines) is the thin orchestration layer providing three core APIs: get_tool_definitions() returns JSON schemas for all tools; handle_function_call() routes tool calls to handlers; check_toolset_requirements() validates toolset prerequisites."))
    story.append(h2("3.3 tools/registry.py -- Tool Registry"))
    story.append(body("registry.py (482 lines) implements a thread-safe singleton tool registry. Each tool describes itself via ToolEntry (name, toolset, JSON Schema, handler, env requirements). Uses threading.RLock for concurrent read/write protection with _snapshot_* methods for stable reads."))
    story.append(body("Discovery mechanism: discover_builtin_tools() scans tools/*.py files via AST analysis for registry.register() calls, auto-registering built-in tools. New tools only need to create a file in tools/ and call register()."))
    story.append(h2("3.4 toolsets.py -- Toolset Grouping"))
    story.append(body("toolsets.py (745 lines) defines toolset concepts for grouping related tools. The _HERMES_CORE_TOOLS list contains 30+ core tools covering web search, terminal, file management, browser automation, and skill systems. Supports toolset composition and dynamic resolution."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 4: Agent Runtime Loop
    # ═══════════════════════════════════════════
    story.append(h1("4. Agent Runtime Loop"))
    story.append(hr(HIGHLIGHT))
    story.append(body("The Agent runtime loop is the most critical component. The AIAgent class in run_agent.py implements the full conversation loop: initialization -> build system prompt -> conversation loop -> error recovery -> response output."))
    story.append(h2("4.1 Conversation Loop Steps"))
    loop_steps = [
        "1. Receive Message: Get current message and conversation history from session manager",
        "2. Build Prompt: Assemble system prompt (identity + platform hints + memory + skills + context files)",
        "3. Inject Memory: Prefetch relevant memories via MemoryManager and inject into prompt",
        "4. LLM Inference: Call OpenAI-compatible API with message history and tool definitions",
        "5. Parse Response: Check finish_reason, determine if tool calls needed",
        "6. Execute Tools: Execute all tool calls in parallel, collect results",
        "7. Append Results: Add tool results to conversation history",
        "8. Check Compression: Trigger context compression if context exceeds threshold",
        "9. Loop/Return: If LLM requests more tool calls go back to step 4, otherwise return final response",
    ]
    for step in loop_steps:
        story.append(bullet(step))
    story.append(sp(2*mm))
    story.append(h2("4.2 Error Recovery"))
    story.append(body("Multi-layer error recovery: API Error Classifier categorizes errors into 12+ types (auth failures, rate limits, server errors, context overflow, etc.), each with different recovery strategies: retry, credential rotation, model fallback, context compression, or abort. Exponential backoff + jitter prevents thundering herd from concurrent retries."))
    story.append(h2("4.3 Tool Budget Control"))
    story.append(body("To prevent infinite tool calling loops, a Tool Budget mechanism limits max tool calls per conversation turn, forcing loop termination when exceeded. enforce_turn_budget controls per-turn tool output volume to prevent oversized outputs from bloating context."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 5: Tool System
    # ═══════════════════════════════════════════
    story.append(h1("5. Tool System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("The tool system uses declarative registration: each tool self-registers via registry.register() with name, toolset, JSON Schema, handler, etc. The core toolset contains 30+ built-in tools covering file operations, terminal commands, web search, browser automation, and code execution."))
    story.append(h2("5.1 ToolEntry Data Structure"))
    story.append(body("Each tool describes itself via ToolEntry: name, toolset, schema (JSON Schema), handler (async function), check_fn (prerequisite check), requires_env (env vars needed), is_async, description, emoji."))
    story.append(h2("5.2 Core Tool Categories"))
    tool_cats = [
        ("File Operations", "read_file, write_file, patch, search_files"),
        ("Terminal", "terminal, process"),
        ("Web Search", "web_search, web_extract"),
        ("Browser Automation", "browser_navigate, browser_click, browser_snapshot, browser_type..."),
        ("Code Execution", "execute_code, delegate_task"),
        ("Vision", "vision_analyze, image_generate"),
        ("Memory", "memory, session_search"),
        ("Task Planning", "todo, clarify"),
        ("Messaging", "send_message, text_to_speech"),
        ("Skills", "skill_view, skill_manage, skills_list"),
        ("Scheduling", "cronjob"),
    ]
    for cat, tools in tool_cats:
        story.append(bullet(f"{cat}: {tools}"))
    story.append(h2("5.3 MCP Integration"))
    story.append(body("The system supports Model Context Protocol (MCP) for dynamic external tool server registration. MCP tools integrate via mcp_tool.py, and the registry supports dynamic refresh -- when MCP servers add/remove tools, the registry auto-updates and exposes new tool definitions to the LLM."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 6: Prompt Building
    # ═══════════════════════════════════════════
    story.append(h1("6. Prompt Building System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("prompt_builder.py (1,115 lines) assembles the Agent system prompt. All functions are stateless -- deterministic output for given input, making prompt building testable and cacheable. The system prompt is composed from multiple fragments."))
    story.append(h2("6.1 System Prompt Components"))
    prompt_parts = [
        ("Identity", "DEFAULT_AGENT_IDENTITY -- Hermes base personality and behavioral guidelines"),
        ("Platform Hints", "PLATFORM_HINTS -- Platform-specific interaction guides (17+ platforms)"),
        ("Memory Guidance", "MEMORY_GUIDANCE -- When/how to use the memory system"),
        ("Session Search", "SESSION_SEARCH_GUIDANCE -- Guide for searching historical sessions"),
        ("Skills Guidance", "SKILLS_GUIDANCE -- Guide for using and creating skills"),
        ("Tool Enforcement", "TOOL_USE_ENFORCEMENT_GUIDANCE -- Force Agent to use tools, not describe plans"),
        ("Model-specific", "OPENAI_MODEL_EXECUTION_GUIDANCE / GOOGLE_MODEL_OPERATIONAL_GUIDANCE"),
        ("Context Files", "AGENTS.md, SOUL.md, .hermes.md project-level context"),
        ("Environment Hints", "WSL / Docker runtime environment awareness"),
        ("Language Detection", "Auto-detect user language and adjust response language"),
    ]
    for name, desc in prompt_parts:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("6.2 Context File Security Scanning"))
    story.append(body("Before injecting context files (AGENTS.md, SOUL.md, etc.) into the system prompt, prompt_builder.py performs security scanning for prompt injection attacks: checks for invisible Unicode characters (zero-width, bidirectional override) and threat patterns (like 'ignore previous instructions'). Threat content is blocked and replaced with warnings."))
    story.append(h2("6.3 Model-Specific Adaptation"))
    story.append(body("Different model families receive specific execution guidance: OpenAI/GPT models get detailed execution discipline (tool persistence, mandatory tool use, prerequisite checks, validation steps); Google/Gemini get operational instructions (absolute paths, dependency checks, parallel tool calls); GPT-5/Codex use 'developer' role instead of 'system' role for higher instruction-following weight."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 7: Context Compression
    # ═══════════════════════════════════════════
    story.append(h1("7. Context Compression System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("context_compressor.py (1,229 lines) implements intelligent context compression to solve context window overflow in long conversations. Core idea: protect head and tail critical messages, use LLM summarization for middle historical messages."))
    story.append(h2("7.1 Compression Algorithm Flow"))
    compress_steps = [
        "1. Tool Output Pruning (pre-pass): Replace old, large tool outputs with informative summaries (not generic placeholders), no LLM call",
        "2. Protect Head Messages: System prompt + first N messages kept intact (default: first 3)",
        "3. Protect Tail Messages: Protect recent messages by token budget (default: ~20K tokens)",
        "4. Deduplication: Identify and merge duplicate tool outputs (e.g., reading same file multiple times)",
        "5. LLM Summarization: Use structured template to summarize middle messages",
        "6. Iterative Update: Update previous summaries on subsequent compression instead of regenerating",
    ]
    for step in compress_steps:
        story.append(bullet(step))
    story.append(h2("7.2 Anti-Bounce Protection"))
    story.append(body("To prevent ineffective compression loops (compressing only 1-2 messages each time), anti-bounce protection skips compression if the last two compressions both saved less than 10%, suggesting the user /new to start a fresh session. A 600-second cooldown prevents repeated attempts when summarization service is unavailable."))
    story.append(h2("7.3 Structured Summary Template"))
    story.append(body("LLM-generated summaries follow a structured template covering: Completed Work, Current State, Unresolved Issues, Remaining Work. Summaries are prefixed with 'CONTEXT COMPACTION -- REFERENCE ONLY' to prevent the model from treating historical summaries as current instructions."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 8: Memory System
    # ═══════════════════════════════════════════
    story.append(h1("8. Memory System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("The memory system has two layers: Semantic Memory via the memory tool stores user preferences and environmental facts; Episodic Memory via hermes_state.py SQLite database stores complete session history with FTS5 full-text search."))
    story.append(h2("8.1 MemoryManager"))
    story.append(body("memory_manager.py (373 lines) orchestrates built-in memory providers and up to one external plugin provider. Key constraint: only one external memory provider can register to prevent tool schema expansion and backend conflicts. The built-in provider always registers first and cannot be removed."))
    story.append(body("Memory context is injected via <memory-context> fence tags with system annotation 'NOT new user input', preventing the model from treating recalled memories as new user input. This fence design effectively prevents memory pollution."))
    story.append(h2("8.2 SQLite State Storage"))
    story.append(body("hermes_state.py (1,443 lines) implements SQLite-backed persistent state storage. Key designs: WAL mode supports multi-reader + single-writer concurrency; FTS5 virtual table enables cross-session full-text search; parent_session_id chain supports compression-triggered session splitting; application-level random jitter retry resolves WAL write contention. Database path: ~/.hermes/state.db, schema version 6."))
    story.append(h2("8.3 Supported Memory Plugins"))
    story.append(body("Supported plugins: mem0, Hindsight, Supermemory, ReteroDB, OpenViking, Holographic Memory, Honcho, ByteRover."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 9: Session Management
    # ═══════════════════════════════════════════
    story.append(h1("9. Session Management"))
    story.append(hr(HIGHLIGHT))
    story.append(body("gateway/session.py (1,257 lines) implements complete session lifecycle management. Each session is described by SessionSource (platform, chat ID, user ID, chat type), supporting DM, group, channel, and thread types."))
    story.append(h2("9.1 Session Tracing"))
    story.append(body("Each message carries complete tracing info: platform, chat_id, user_id, chat_type (DM/group/channel/thread), thread_id. Used for routing responses to correct locations, injecting context into system prompts, and tracking scheduled task delivery sources."))
    story.append(h2("9.2 PII Protection"))
    story.append(body("Session storage implements PII hashing: sensitive identifiers like user_id and chat_id are SHA-256 hashed (keeping first 12 hex chars) before storage, maintaining unique session identification without exposing raw user information."))
    story.append(h2("9.3 Session Reset Strategies"))
    story.append(body("Multiple reset strategies supported: Manual reset (/new command), idle timeout reset (configurable), context overflow reset (auto-triggers /new with summary preservation). parent_session_id chains maintain session continuity across resets."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 10: Gateway
    # ═══════════════════════════════════════════
    story.append(h1("10. Gateway & Platform Integration"))
    story.append(hr(HIGHLIGHT))
    story.append(body("gateway/run.py (11,015 lines) is the gateway main entry point managing all configured platform adapter lifecycles. Uses asyncio event loop for multi-platform concurrent message handling, with each platform adapter running in its own coroutine."))
    story.append(h2("10.1 Supported Platforms"))
    story.append(body("20+ supported platforms: Telegram, Discord, WhatsApp, Signal, Slack, Mattermost, Matrix, iMessage (BlueBubbles), WeChat (Weixin), Enterprise WeChat (WeCom), Feishu (Lark), DingTalk, QQ Bot, Yuanbao, Email, SMS, Home Assistant, API Server, Webhook."))
    story.append(h2("10.2 Gateway Lifecycle"))
    gw_steps = [
        "1. SSL Certificate Detection: Auto-detect system CA certificate location (supports NixOS)",
        "2. Environment Variable Loading: Load from ~/.hermes/.env",
        "3. Agent Cache Initialization: LRU cache, max 128 Agent instances, 1-hour idle TTL",
        "4. Platform Adapter Startup: Start independent message listening coroutines for each platform",
        "5. Message Routing Loop: Receive message -> Find/Create session -> Invoke Agent -> Return response",
        "6. Graceful Shutdown: Save all session state and close connections on SIGTERM",
    ]
    for step in gw_steps:
        story.append(bullet(step))
    story.append(h2("10.3 Platform Adapter Architecture"))
    story.append(body("Each platform adapter implements a unified interface: connect(), listen(), send(), disconnect(). Adapters handle platform-specific protocols (Telegram Bot API, Discord Gateway, WeChat iLink Bot API, etc.), converting platform messages to internal format."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 11: Cron Jobs
    # ═══════════════════════════════════════════
    story.append(h1("11. Cron Job System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("cron/jobs.py (776 lines) implements a complete scheduled task system. Jobs stored in ~/.hermes/cron/jobs.json, output saved to ~/.hermes/cron/output/{job_id}/."))
    story.append(h2("11.1 Schedule Types"))
    sched_types = [
        ("One-shot", "Execute once after specified delay (e.g., '30m', '2h', ISO timestamp)"),
        ("Interval", "Repeat at fixed intervals (e.g., 'every 30m', 'every 2h')"),
        ("Cron Expression", "Standard 5-field cron expressions (e.g., '0 9 * * *')"),
    ]
    for name, desc in sched_types:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("11.2 Job Delivery"))
    story.append(body("Job results support multiple delivery modes: origin (return to creating chat), local (save to file only), specified platform (e.g., telegram:chat_id). Pre-execution scripts supported via script parameter for data collection and change detection."))
    story.append(h2("11.3 Fault Tolerance"))
    story.append(body("One-shot jobs have a 120-second grace window. Interval jobs have grace period of half the interval (120s to 2h), allowing catch-up after short misses but fast-forwarding after long misses to prevent job backlog. threading.Lock protects concurrent jobs.json reads/writes."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 12: Error Classification
    # ═══════════════════════════════════════════
    story.append(h1("12. Error Classification & Failover"))
    story.append(hr(HIGHLIGHT))
    story.append(body("error_classifier.py (829 lines) implements structured API error classification, replacing scattered string-matching with a centralized classifier that the main retry loop consults for every API failure."))
    story.append(h2("12.1 Error Taxonomy"))
    error_types = [
        ("auth / auth_permanent", "Auth failures (401/403) -> refresh/rotate credentials or abort"),
        ("rate_limit", "Rate limiting (429) -> backoff then rotate credentials"),
        ("billing", "Quota exhausted (402) -> rotate credentials immediately"),
        ("overloaded / server_error", "Server errors (500/503/529) -> backoff retry"),
        ("timeout", "Connection/read timeout -> rebuild client then retry"),
        ("context_overflow", "Context too large -> trigger context compression, not failover"),
        ("payload_too_large", "Request too large (413) -> compress payload"),
        ("model_not_found", "Model not found (404) -> fallback to different model"),
        ("format_error", "Bad request format (400) -> abort or fix and retry"),
        ("thinking_signature", "Anthropic thinking block signature invalid"),
        ("unknown", "Unclassifiable -> backoff retry"),
    ]
    for name, desc in error_types:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("12.2 ClassifiedError Data Class"))
    story.append(body("Classification results are encapsulated as ClassifiedError: reason (FailoverReason enum), status_code, provider, model, message, error_context (dict), and recovery hints (retryable, should_compress, should_rotate_credential, should_fallback). The retry loop checks these hints directly."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 13: Configuration
    # ═══════════════════════════════════════════
    story.append(h1("13. Configuration System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Hermes Agent uses multi-layer configuration: config.yaml (master) -> .env (environment) -> CLI args. Main config at ~/.hermes/config.yaml contains all sections for models, gateway, tools, sessions, etc."))
    story.append(h2("13.1 Configuration Sections"))
    config_sections = [
        ("model", "Default model, model list, provider configuration"),
        ("gateway", "Enabled platforms, Home Channels, session reset policies"),
        ("tools", "Toolset config, MCP server configuration"),
        ("session", "Session timeout, context compression thresholds"),
        ("cron", "Scheduled task global configuration"),
        ("display", "UI theme, spinner style"),
        ("plugins", "Memory plugins, context engine plugins"),
        ("skills", "Skill directories, disabled list"),
    ]
    for name, desc in config_sections:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("13.2 Multi-Model Support"))
    story.append(body("Unified OpenAI-compatible interface supports multiple backends: OpenAI (GPT-4/GPT-5), Anthropic (Claude), Google (Gemini), OpenRouter, Ollama (local). Each provider configures independent base_url, api_key, timeout, and model-specific parameters. Per-model context window and pricing supported."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 14: Skills System
    # ═══════════════════════════════════════════
    story.append(h1("14. Skills System"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Skills are pluggable knowledge modules, essentially directories containing SKILL.md files. Each skill defines workflows, API endpoints, tool commands, and quality standards for specific task types. The skill scanner traverses ~/.hermes/skills/ and built-in skill directories."))
    story.append(h2("14.1 Skill Discovery & Loading"))
    story.append(body("Discovery: iter_skill_index_files() scans all skill directories, reading YAML frontmatter from each SKILL.md (name, description, allowed-tools, metadata) to generate a skill index. The system prompt injects the skill index so the Agent knows available skills. When a skill matches the current task, skill_view() loads the full content."))
    story.append(h2("14.2 Skill Caching"))
    story.append(body("Skill prompts use an OrderedDict LRU cache (max 8 entries) to avoid re-scanning the filesystem each conversation. Cache keys include skill directory snapshot version, auto-invalidating when skill files change."))
    story.append(h2("14.3 Skill Categories"))
    story.append(body("20+ built-in skill categories: autonomous-ai-agents, creative, data-science, devops, doc-design, email, gaming, github, mcp, media, mlops, note-taking, productivity, red-teaming, research, smart-home, social-media, software-development, web-access, yuanbao."))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # Chapter 15: Design Philosophy
    # ═══════════════════════════════════════════
    story.append(h1("15. Design Philosophy Summary"))
    story.append(hr(HIGHLIGHT))
    story.append(body("Through deep source code study, we can extract the following core design philosophies and architectural highlights:"))
    story.append(h2("15.1 Architecture Highlights"))
    highlights = [
        ("Clear Layering", "Six-layer architecture with single-responsibility layers"),
        ("Defensive Programming", "SafeWriter, context file security scanning, PII hashing, anti-bounce compression"),
        ("Resilient Design", "12+ error types with auto-recovery, exponential backoff + jitter, multi-model fallback"),
        ("Zero-config Extension", "Tools auto-discovered via AST analysis, new tools need zero configuration"),
        ("Platform Agnostic", "Unified message abstraction supports 20+ platforms"),
        ("Persistence First", "SQLite WAL + FTS5, all state persisted to disk"),
        ("Context Aware", "Smart compression protects key context, fence tags prevent memory pollution"),
        ("Observability", "Detailed logging, token usage tracking, cost estimation"),
    ]
    for name, desc in highlights:
        story.append(bullet(f"{name}: {desc}"))
    story.append(h2("15.2 Best Practices"))
    practices = [
        "All prompt-building functions are stateless (pure functions), testable and cacheable",
        "Uses RLock instead of Lock for registry, supporting same-thread reentrancy",
        "WAL mode SQLite + application-level random jitter retry for write contention",
        "Context compression summaries explicitly marked 'REFERENCE ONLY'",
        "Tool budget mechanism prevents infinite loops, graceful degradation instead of hard crashes",
        "Skills use lazy loading, only loaded when needed",
        "Environment variables loaded from ~/.hermes/.env, overriding shell exports",
    ]
    for p in practices:
        story.append(bullet(p))
    story.append(h2("15.3 Reusable Patterns"))
    story.append(body("For developers building similar AI Agent systems, Hermes Agent provides these reusable patterns: (1) Registry Pattern -- decorator/self-registration for automatic tool discovery; (2) Fence Tags -- XML tags to distinguish different prompt content types; (3) Structured Error Classification -- unified classifier + recovery strategy; (4) Progressive Context Compression -- prune first (no LLM) then summarize (with LLM); (5) Multi-Platform Adapter -- unified interface + platform-specific implementation."))

    story.append(sp(10*mm))
    story.append(hr(HIGHLIGHT, 2, "60%"))
    story.append(para("End of Document -- by Xiaomiao", S('End', fontSize=11, textColor=MEDIUM_GRAY, alignment=TA_CENTER)))

    # ── Build ──
    doc.build(story)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    out = os.path.expanduser("~/.hermes/Hermes_Architecture_Guide.pdf")
    build_pdf(out)
