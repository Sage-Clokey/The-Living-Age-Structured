"""
Build Statement Fellowship Complete Fill-Out PDF
==================================================
Converts statement_fellowship_complete_fillout.md into a styled PDF.

Usage:
    python3 sfl/build_complete_fillout_pdf.py
"""

from pathlib import Path
import markdown
from weasyprint import HTML

SFL_DIR = Path(__file__).resolve().parent
MD_PATH = SFL_DIR / "statement_fellowship_complete_fillout.md"
OUT_PDF = SFL_DIR / "statement_fellowship_complete_fillout.pdf"

CSS = r"""
@page {
    size: letter;
    margin: 0.85in 0.9in 0.85in 0.9in;
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        color: #888;
    }
}

body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #1a1a1a;
}

h1:first-of-type {
    font-size: 22pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0.1in;
    margin-bottom: 0.05in;
    color: #1a1a1a;
    letter-spacing: 0.5pt;
}

h1:first-of-type + p {
    text-align: center;
    text-indent: 0;
    font-size: 10.5pt;
    color: #444;
    font-style: italic;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 0.3in;
    margin-bottom: 0.1in;
    color: #1a1a1a;
    border-bottom: 1.5pt solid #2a5a3a;
    padding-bottom: 0.04in;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 0.18in;
    margin-bottom: 0.06in;
    color: #2a5a3a;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    font-weight: bold;
    margin-top: 0.12in;
    margin-bottom: 0.04in;
    color: #333;
    page-break-after: avoid;
}

p {
    text-align: justify;
    margin-bottom: 0.07in;
    margin-top: 0;
    text-indent: 0;
    orphans: 3;
    widows: 3;
}

strong { font-weight: bold; }
em { font-style: italic; }

ul, ol {
    margin-left: 0.25in;
    margin-bottom: 0.08in;
    margin-top: 0.04in;
}

li { margin-bottom: 0.04in; }
li p { text-indent: 0; margin-bottom: 0.02in; }

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 0.2in 0;
}

blockquote {
    border-left: 3pt solid #2a5a3a;
    margin: 0.1in 0 0.1in 0.15in;
    padding: 0.04in 0 0.04in 0.15in;
    color: #333;
    font-style: italic;
}

blockquote p { text-indent: 0; font-style: italic; }

code {
    font-family: "Courier New", monospace;
    font-size: 9pt;
    background-color: #f4f4f4;
    padding: 1pt 3pt;
}
"""


def main():
    print("Building Statement Fellowship Complete Fill-Out PDF...")

    text = MD_PATH.read_text(encoding="utf-8")

    md = markdown.Markdown(extensions=["tables", "smarty"])
    body = md.convert(text)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

    html_path = OUT_PDF.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")
    print(f"  HTML: {html_path}")

    HTML(string=full_html).write_pdf(str(OUT_PDF))
    print(f"  PDF:  {OUT_PDF}")
    print("Done.")


if __name__ == "__main__":
    main()
