"""Build project proposal PDF from markdown using WeasyPrint."""

import markdown
from weasyprint import HTML
from pathlib import Path

DIR = Path(__file__).parent
MD_FILE = DIR / "project_proposal.md"
PDF_FILE = DIR / "project_proposal.pdf"

md_text = MD_FILE.read_text(encoding="utf-8")
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

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
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #1a1a1a;
    }}
    h1 {{
        font-size: 18pt;
        text-align: center;
        margin-bottom: 0.2em;
        color: #000;
    }}
    h2 {{
        font-size: 14pt;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        border-bottom: 1px solid #ccc;
        padding-bottom: 0.2em;
        color: #1a1a1a;
    }}
    h3 {{
        font-size: 12pt;
        margin-top: 1.2em;
        margin-bottom: 0.4em;
        color: #333;
    }}
    p {{
        text-align: justify;
        margin-bottom: 0.8em;
    }}
    strong {{
        color: #000;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        font-size: 10pt;
    }}
    th {{
        background-color: #2c3e50;
        color: white;
        padding: 8px 10px;
        text-align: left;
        font-weight: bold;
    }}
    td {{
        padding: 6px 10px;
        border-bottom: 1px solid #ddd;
    }}
    tr:nth-child(even) td {{
        background-color: #f8f9fa;
    }}
    ul, ol {{
        margin-bottom: 0.8em;
    }}
    li {{
        margin-bottom: 0.3em;
    }}
    hr {{
        border: none;
        border-top: 2px solid #2c3e50;
        margin: 1.5em 0;
    }}
    blockquote {{
        border-left: 3px solid #2c3e50;
        margin: 1em 0;
        padding: 0.5em 1em;
        color: #555;
        font-style: italic;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

HTML(string=full_html).write_pdf(str(PDF_FILE))
print(f"PDF written to {PDF_FILE}")
