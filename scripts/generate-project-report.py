#!/usr/bin/env python3
"""
项目报告生成器 — 数据驱动的 PROJECT-PANORAMA.html 生成器

用法:
  python3 generate-project-report.py --data docs/project-report.json --output PROJECT-PANORAMA.html
  python3 generate-project-report.py --data docs/project-report.json --verify   # 验证模式

设计哲学:
  - 零外部依赖（仅 Python 标准库）
  - 数据驱动：改 1 处 JSON 全同步
  - 跨项目复用：所有项目共用同一生成器
  - 可与 doc-alignment 工作流无缝集成

数据格式: docs/project-report.json
"""

import argparse
import json
import os
import sys
from datetime import datetime


# ═══════════════════════════════════════════════════════════
# HTML 模板组件
# ═══════════════════════════════════════════════════════════

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif;
  background: #0d1117; color: #e6edf3; line-height: 1.6; padding: 40px 20px;
}
.container { max-width: 960px; margin: 0 auto; }
/* Header */
.header { text-align: center; padding: 60px 0 40px; border-bottom: 1px solid #30363d; margin-bottom: 40px; }
.header h1 { font-size: 2.4em; background: linear-gradient(135deg, #58a6ff, #bc8cff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
.header .subtitle { color: #8b949e; font-size: 1.1em; }
.badge { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.85em; margin: 12px 4px 0; }
.badge-blue { background: #1f6feb33; color: #58a6ff; border: 1px solid #1f6feb66; }
.badge-green { background: #3fb95033; color: #3fb950; border: 1px solid #3fb95066; }
.badge-orange { background: #d2992233; color: #d29922; border: 1px solid #d2992266; }
.badge-purple { background: #bc8cff33; color: #bc8cff; border: 1px solid #bc8cff66; }
/* Sections */
section { background: #161b22; border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; border: 1px solid #30363d; }
section h2 { font-size: 1.4em; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #30363d; display: flex; align-items: center; gap: 10px; }
section h2 .icon { font-size: 1.2em; }
section h3 { font-size: 1.1em; margin: 20px 0 12px; color: #58a6ff; }
section h4 { font-size: 0.95em; margin: 14px 0 8px; color: #39d2c0; }
/* Grid */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; } }
.card { background: #1c2333; border-radius: 8px; padding: 16px; border: 1px solid #30363d; }
.card .label { font-size: 0.8em; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.card .value { font-size: 1.6em; font-weight: 600; }
.card .sub { font-size: 0.85em; color: #8b949e; margin-top: 2px; }
/* Tables */
table { width: 100%; border-collapse: collapse; font-size: 0.9em; margin: 12px 0; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #21262d; }
th { background: #1c2333; color: #8b949e; font-weight: 600; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; position: sticky; top: 0; }
tr:hover td { background: #1c233366; }
code { background: #1c2333; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; font-family: 'JetBrains Mono','Fira Code',monospace; color: #f778ba; }
/* Architecture layers */
.arch-layer { background: #1c2333; border-radius: 8px; padding: 14px; border: 1px solid #30363d; margin: 4px 0; }
.arch-layer .label { font-size: 0.8em; color: #8b949e; margin-bottom: 8px; }
.arch-arrow { text-align: center; color: #8b949e; font-size: 0.9em; padding: 4px 0; }
.arch-module { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 0.85em; margin: 2px; }
.am-cli { background: #1f6feb33; color: #58a6ff; border: 1px solid #1f6feb44; }
.am-http { background: #3fb95033; color: #3fb950; border: 1px solid #3fb95044; }
.am-socket { background: #d2992233; color: #d29922; border: 1px solid #d2992244; }
.am-core { background: #bc8cff33; color: #bc8cff; border: 1px solid #bc8cff44; }
.am-data { background: #f778ba33; color: #f778ba; border: 1px solid #f778ba44; }
/* Stats grid */
.stat-card { text-align: center; padding: 20px; background: #1c2333; border-radius: 8px; border: 1px solid #30363d; }
.stat-card .number { font-size: 2.2em; font-weight: 700; }
.stat-card .stat-label { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
/* File tree */
.file-tree { font-family: 'JetBrains Mono','Fira Code',monospace; font-size: 0.85em; line-height: 1.8; background: #1c2333; padding: 16px; border-radius: 8px; border: 1px solid #30363d; overflow-x: auto; }
.file-tree .comment { color: #8b949e; }
/* Progress bar */
.progress-bar { height: 8px; background: #21262d; border-radius: 4px; overflow: hidden; margin: 8px 0; }
.progress-bar .fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
/* Responsive */
@media print { body { padding: 0; } section { break-inside: avoid; } }
"""


def _tablerow(cells, header=False):
    """生成 HTML 表格行"""
    tag = "th" if header else "td"
    return "  <tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"


def _card(label, value, sub=""):
    """生成统计卡片"""
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div>{sub_html}</div>'


def _badge(text, style="blue"):
    """生成徽章"""
    return f'<span class="badge badge-{style}">{text}</span>'


def _layer(name, modules, cls="am-cli"):
    """生成架构层 HTML"""
    mods = "".join(f'<span class="arch-module {cls}">{m}</span>' for m in modules)
    return f'<div class="arch-layer"><div class="label">{name}</div><div style="text-align:center;padding:8px 0;">{mods}</div></div>'


def _arrow(text="⬇ 委托 ⬇"):
    return f'<div class="arch-arrow">{text}</div>'


# ═══════════════════════════════════════════════════════════
# 核心生成函数
# ═══════════════════════════════════════════════════════════

def generate_html(data: dict) -> str:
    """从数据字典生成完整 HTML 报告"""
    p = data.get("project", {})
    arch = data.get("architecture", {})
    api = data.get("api_endpoints", {})
    cli = data.get("cli_commands", [])
    epics = data.get("epics", [])
    tests = data.get("tests", {})
    sprint_history = data.get("sprint_history", [])
    footer_text = data.get("footer", "由 generate-project-report.py 自动生成")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    ver = p.get("version", "0.0.0")

    # ── Project cards ──
    overview_cards = ""
    for item in p.get("overview_cards", []):
        overview_cards += _card(item.get("label", ""), item.get("value", ""), item.get("sub", ""))

    # ── Info table ──
    info_rows = ""
    for row in p.get("info_table", []):
        info_rows += _tablerow([row.get("attr", ""), row.get("value", "")])

    # ── Architecture layers ──
    layers_html = ""
    layer_specs = []
    for i, layer in enumerate(arch.get("layers", [])):
        cls = ["am-cli", "am-core", "am-data"][i if i < 3 else 2]
        layers_html += _layer(layer.get("name", ""), layer.get("modules", []), cls)
        direction = layer.get("direction")
        if direction:
            arrow_map = {"delegate": "⬇ 委托 ⬇", "read-write": "⬇ 读写 ⬇", "call": "⬇ 调用 ⬇"}
            layers_html += _arrow(arrow_map.get(direction, "⬇ ⬇"))

    # ── Module table ──
    module_rows = ""
    for mod in arch.get("module_table", []):
        methods = ", ".join(f"<code>{m}</code>" for m in mod.get("methods", []))
        new_flag = mod.get("new_in")
        name_cell = mod["module"]
        desc_cell = mod.get("desc", "")
        if new_flag:
            name_cell = f'<span style="color:var(--cyan);">{name_cell}</span>'
            desc_cell = f'<span style="color:var(--cyan);">{desc_cell} 🆕 {new_flag}</span>'
        module_rows += _tablerow([
            name_cell,
            f"<code>{mod['file']}</code>",
            desc_cell,
            methods,
        ])

    # ── HTTP Endpoints ──
    http_rows = ""
    for ep in api.get("http", []):
        method = ep.get("method", "GET")
        color = {"GET": "#3fb950", "POST": "#d29922", "DELETE": "#f85149", "PUT": "#58a6ff"}.get(method, "#8b949e")
        sprint_label = ep.get("sprint", "")
        sprint_tag = _badge(sprint_label, "green") if "🆕" in sprint_label else sprint_label
        http_rows += _tablerow([
            f'<span style="color:{color};font-weight:600;">{method}</span>',
            f"<code>{ep['path']}</code>",
            ep.get("desc", ""),
            sprint_tag,
        ])

    # ── Socket Actions ──
    socket_rows = ""
    for sa in api.get("socket_actions", []):
        new_flag = " 🆕" if sa.get("new") else ""
        socket_rows += _tablerow([
            f"<code>{sa['action']}</code>",
            f"<code>{sa.get('params', '')}</code>",
            f"{sa.get('desc', '')}{new_flag}",
            sa.get("sprint", ""),
        ])

    # ── CLI Commands ──
    cli_sections = {"daemon": "守护进程管理", "query": "查询命令", "management": "管理命令"}
    cli_html = ""
    for section_key, section_label in cli_sections.items():
        section_cmds = [c for c in cli if c.get("section") == section_key]
        if not section_cmds:
            continue
        rows = ""
        for c in section_cmds:
            style = ' style="color:var(--cyan);"' if c.get("new") else ""
            label = f'<code{c.get("new") and style or ""}>{c["cmd"]}</code>'
            desc = f'<span{c.get("new") and style or ""}>{c["desc"]}</span>'
            rows += _tablerow([label, desc])
        cli_html += f"""
<h3>{section_label}</h3>
<table>
  <tr><th>命令</th><th>说明</th></tr>
{rows}
</table>"""

    # ── EPIC / Story Status ──
    epic_sections = ""
    for epic in epics:
        stories = epic.get("stories", [])
        completed = [s for s in stories if s.get("status") == "completed"]
        pending = [s for s in stories if s.get("status") != "completed"]
        total = len(stories)
        done = len(completed)
        pct = round(done / total * 100) if total > 0 else 0

        bar_color = "#3fb950" if pct >= 80 else ("#d29922" if pct >= 50 else "#f85149")

        story_rows = ""
        for s in stories:
            pri_color = {"P0": "var(--red)", "P1": "var(--orange)", "P2": "var(--text2)"}.get(s.get("pri", ""), "var(--text2)")
            status_icon = "✅" if s.get("status") == "completed" else "📋"
            sprint_badge = f'<span class="badge badge-blue" style="font-size:0.75em;">{s.get("sprint", "")}</span>' if s.get("sprint") else ""
            story_rows += _tablerow([
                f"<code>{s['id']}</code>",
                f"{status_icon} {s['name']}",
                f'<span style="color:{pri_color};">{s.get("pri", "")}</span>',
                sprint_badge,
            ])

        epic_sections += f"""
<h3>{epic.get("name", "")} ({done}/{total})</h3>
<div class="progress-bar"><div class="fill" style="width:{pct}%;background:{bar_color};"></div></div>
<table>
  <tr><th>ID</th><th>Story</th><th>优先级</th><th>Sprint</th></tr>
{story_rows}
</table>"""

    # ── Test Stats ──
    test_passing = tests.get("passing", 0)
    test_total = tests.get("total", 0)
    test_duration = tests.get("duration_seconds", 0)
    test_coverage = tests.get("coverage_pct")
    test_files = tests.get("files", [])

    test_bar_color = "#3fb950" if test_passing == test_total else "#d29922"
    test_files_str = ", ".join(f"<code>{f}</code>" for f in test_files)

    # ── Sprint History ──
    sprint_rows = ""
    for sh in sprint_history:
        sprint_rows += _tablerow([
            sh.get("sprint", ""),
            sh.get("version", ""),
            sh.get("date", ""),
            str(sh.get("stories_completed", 0)),
            sh.get("tests_growth", ""),
        ])

    # ── Assemble ──
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p.get("name", "Project")} — 项目全貌</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">

<!-- ═══════ HEADER ═══════ -->
<div class="header">
  <h1>{p.get("icon", "🔮")} {p.get("name", "Project")}</h1>
  <div class="subtitle">{p.get("description", "")}</div>
  <div>
    {_badge(f"v{ver}", "blue")}
    {_badge(f"{test_passing} tests", "orange")}
    {_badge("MIT License", "green")}
  </div>
  <div style="margin-top:8px;color:#8b949e;font-size:0.85em;">
    生成于 {now} | {footer_text}
  </div>
</div>

<!-- ═══════ PROJECT OVERVIEW ═══════ -->
<section>
<h2><span class="icon">📋</span> 项目概览</h2>
<div class="grid-3">
{overview_cards}
</div>
<div style="margin-top:12px;">
<p><strong>{p.get("name", "")}</strong> {p.get("long_description", "")}</p>
<br>
<table>
  <tr><th>属性</th><th>值</th></tr>
{info_rows}
</table>
</div>
</section>

<!-- ═══════ ARCHITECTURE ═══════ -->
<section>
<h2><span class="icon">🏗️</span> 三层架构</h2>
{layers_html}
<h3>核心模块职责</h3>
<table>
  <tr><th>模块</th><th>文件</th><th>职责</th><th>关键方法</th></tr>
{module_rows}
</table>
</section>

<!-- ═══════ API ENDPOINTS ═══════ -->
<section>
<h2><span class="icon">🔌</span> 全部 API 端点</h2>

<h3>HTTP API (port {api.get("http_port", "?")})</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th><th>Sprint</th></tr>
{http_rows}
</table>

<h3>Unix Socket API (~/.sra/srad.sock)</h3>
<table>
  <tr><th>Action</th><th>Params</th><th>说明</th><th>Sprint</th></tr>
{socket_rows}
</table>
</section>

<!-- ═══════ CLI COMMANDS �══════ -->
<section>
<h2><span class="icon">💻</span> CLI 命令全集</h2>
{cli_html}
</section>

<!-- ═══════ EPIC STATUS �══════ -->
<section>
<h2><span class="icon">📊</span> EPIC & Story 状态</h2>
{epic_sections}
</section>

<!-- ═══════ TEST COVERAGE ═══════ -->
<section>
<h2><span class="icon">🧪</span> 测试覆盖</h2>
<div class="grid-3">
  <div class="stat-card">
    <div class="number" style="color:var(--green);">{test_passing}</div>
    <div class="stat-label">通过测试</div>
  </div>
  <div class="stat-card">
    <div class="number">{test_total}</div>
    <div class="stat-label">总测试</div>
  </div>
  <div class="stat-card">
    <div class="number" style="color:var(--accent);">{test_duration}s</div>
    <div class="stat-label">运行时间</div>
  </div>
</div>
<div class="progress-bar"><div class="fill" style="width:{test_passing/test_total*100 if test_total > 0 else 0}%;background:{test_bar_color};"></div></div>
<div style="margin-top:12px;color:#8b949e;font-size:0.9em;">
  <strong>测试文件:</strong> {test_files_str}
</div>
</section>

<!-- ═══════ SPRINT HISTORY ═══════ -->
<section>
<h2><span class="icon">🏃</span> Sprint 历史</h2>
<table>
  <tr><th>Sprint</th><th>版本</th><th>日期</th><th>完成的 Story</th><th>测试增长</th></tr>
{sprint_rows}
</table>
</section>

<!-- ═══════ FOOTER ═══════ -->
<div style="text-align:center;padding:30px;color:#8b949e;font-size:0.85em;">
  <p>🔮 <strong>{p.get("name", "Project")}</strong> v{ver}</p>
  <p>由 <code>generate-project-report.py</code> 于 {now} 生成</p>
</div>

</div>
</body>
</html>"""

    return html


# ═══════════════════════════════════════════════════════════
# 验证模式
# ═══════════════════════════════════════════════════════════

def verify(data: dict) -> list:
    """验证数据与代码的一致性，返回漂移报告"""
    issues = []
    p = data.get("project", {})
    ver = p.get("version", "")

    # 检查版本号一致性（尝试读取 __init__.py）
    init_py = os.path.join(os.getcwd(), "skill_advisor", "__init__.py")
    if os.path.exists(init_py):
        with open(init_py) as f:
            content = f.read()
        for line in content.splitlines():
            if "__version__" in line and f'"{ver}"' not in line and f"'{ver}'" not in line:
                actual = line.split("=")[-1].strip().strip('"').strip("'")
                if actual != ver:
                    issues.append(f"版本号漂移: project-report 中为 {ver}，但 __init__.py 中为 {actual}")

    # 检查测试数量
    tests = data.get("tests", {})
    test_dir = os.path.join(os.getcwd(), "tests")
    if os.path.isdir(test_dir):
        py_files = [f for f in os.listdir(test_dir) if f.endswith(".py") and f.startswith("test_")]
        declared_files = tests.get("files", [])
        missing = [f for f in py_files if f not in declared_files and f != "__init__.py"]
        if missing:
            issues.append(f"测试文件缺失: project-report 中未声明 {missing}")

    return issues


# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="项目报告生成器")
    parser.add_argument("--data", required=True, help="project-report.json 路径")
    parser.add_argument("--output", default="PROJECT-PANORAMA.html", help="输出 HTML 路径")
    parser.add_argument("--verify", action="store_true", help="验证模式：检查数据与代码的一致性")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"❌ 数据文件不存在: {args.data}")
        sys.exit(1)

    with open(args.data) as f:
        data = json.load(f)

    if args.verify:
        issues = verify(data)
        if issues:
            print("⚠️  发现以下漂移问题:")
            for i in issues:
                print(f"  • {i}")
            sys.exit(1 if any("版本号" in i for i in issues) else 0)
        else:
            print("✅ 数据与代码状态一致")
        return

    html = generate_html(data)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)
    print(f"✅ 报告已生成: {args.output}")
    print(f"   版本: v{data.get('project', {}).get('version', '?')}")
    print(f"   测试: {data.get('tests', {}).get('passing', '?')}/{data.get('tests', {}).get('total', '?')}")


if __name__ == "__main__":
    main()
