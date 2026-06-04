#!/usr/bin/env python3
"""Convert telehealth debate prep markdown to PDF."""

import markdown
from weasyprint import HTML

INPUT = "telehealth_debate_prep.md"
OUTPUT = "telehealth_debate_prep.pdf"

with open(INPUT, "r", encoding="utf-8") as f:
    md_text = f.read()

html_body = markdown.markdown(md_text, extensions=["tables", "extra"])

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: letter;
        margin: 1in;
    }}
    body {{
        font-family: Arial, Helvetica, sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #1a1a1a;
    }}
    h1 {{
        font-size: 18pt;
        border-bottom: 2px solid #333;
        padding-bottom: 6px;
        margin-top: 24px;
    }}
    h2 {{
        font-size: 14pt;
        color: #2a2a2a;
        margin-top: 20px;
        border-bottom: 1px solid #ccc;
        padding-bottom: 4px;
    }}
    h3 {{
        font-size: 12pt;
        color: #333;
        margin-top: 16px;
    }}
    blockquote {{
        border-left: 3px solid #666;
        padding-left: 12px;
        margin-left: 0;
        color: #444;
        font-style: italic;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
    }}
    th, td {{
        border: 1px solid #999;
        padding: 6px 10px;
        text-align: left;
        font-size: 10pt;
    }}
    th {{
        background-color: #e8e8e8;
        font-weight: bold;
    }}
    hr {{
        border: none;
        border-top: 1px solid #ccc;
        margin: 20px 0;
    }}
    strong {{
        color: #111;
    }}
    ol, ul {{
        margin-left: 20px;
    }}
    li {{
        margin-bottom: 4px;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=full_html).write_pdf(OUTPUT)
print(f"PDF written to {OUTPUT}")
