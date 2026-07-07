#!/usr/bin/env python3
"""Convert BME80G Final Part II filled template markdown to PDF."""

import markdown
from weasyprint import HTML

INPUT = "BME80G_Final_PartII_Filled.md"
OUTPUT = "BME80G_Final_PartII_Filled.pdf"

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
        line-height: 1.35;
        color: #1a1a1a;
    }}
    h1 {{
        font-size: 16pt;
        text-align: center;
        border-bottom: 2px solid #333;
        padding-bottom: 6px;
        margin-top: 0;
        margin-bottom: 4px;
    }}
    h2 {{
        font-size: 13pt;
        color: #1a1a1a;
        margin-top: 18px;
        margin-bottom: 6px;
        border-bottom: 1px solid #999;
        padding-bottom: 3px;
    }}
    h3 {{
        font-size: 11pt;
        color: #333;
        margin-top: 12px;
        margin-bottom: 4px;
    }}
    p {{
        margin-top: 4px;
        margin-bottom: 6px;
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
        margin: 8px 0;
    }}
    th, td {{
        border: 1px solid #999;
        padding: 5px 8px;
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
        margin: 14px 0;
    }}
    strong {{
        color: #111;
    }}
    ol, ul {{
        margin-left: 18px;
        margin-top: 4px;
        margin-bottom: 6px;
    }}
    li {{
        margin-bottom: 3px;
    }}
    em em {{
        /* bold+italic for thesis */
        font-style: italic;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=full_html).write_pdf(OUTPUT)
print(f"PDF written to {OUTPUT}")
