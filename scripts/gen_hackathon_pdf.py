#!/usr/bin/env python3
import markdown
from weasyprint import HTML, CSS
import os

# Read the markdown file
md_path = "/home/ubuntu/.hermes/hackathon_report_final.md"
pdf_path = "/home/ubuntu/.hermes/Hackathon_Solutions.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Convert markdown to HTML
html_body = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

# Wrap in a full HTML document with CSS for styling
html_doc = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: 2cm 1.5cm;
        @bottom-center {{ content: "Page " counter(page) " of " counter(pages); font-size: 9pt; color: gray; }}
        @top-center {{ content: "美团 AI Hackathon 创新方案策划指南"; font-size: 10pt; color: gray; }}
    }}
    body {{
        font-family: "WenQuanYi Zen Hei", "Source Han Sans CN", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
        line-height: 1.6;
        font-size: 11pt;
        color: #333;
    }}
    h1 {{
        color: #ff6b6b;
        border-bottom: 2px solid #ff6b6b;
        padding-bottom: 0.5em;
        margin-top: 2em;
        font-size: 24pt;
        page-break-before: always;
    }}
    h1:first-of-type {{
        page-break-before: auto;
    }}
    h2 {{
        color: #4A90D9;
        border-left: 5px solid #4A90D9;
        padding-left: 10px;
        margin-top: 1.5em;
        font-size: 18pt;
    }}
    h3 {{
        color: #333;
        background-color: #f4f4f4;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 14pt;
        margin-top: 1.5em;
        page-break-inside: avoid;
    }}
    h4 {{
        color: #555;
        margin-top: 1em;
        font-size: 12pt;
    }}
    p {{
        margin-bottom: 0.8em;
        text-align: justify;
    }}
    ul, ol {{
        margin-bottom: 1em;
    }}
    code {{
        background-color: #eee;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: "Consolas", "Monaco", monospace;
        font-size: 0.9em;
    }}
    pre {{
        background-color: #2d2d2d;
        color: #f8f8f2;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        font-family: "Consolas", "Monaco", monospace;
        font-size: 9pt;
    }}
    strong {{
        color: #000;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1em;
    }}
    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #4A90D9;
        color: white;
    }}
    hr {{
        border: 0;
        border-top: 1px solid #ccc;
        margin: 2em 0;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

# Generate PDF
try:
    HTML(string=html_doc).write_pdf(pdf_path)
    print(f"✅ PDF generated successfully at: {pdf_path}")
except Exception as e:
    print(f"❌ Error generating PDF: {e}")
