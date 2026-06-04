"""
Build Full Paper PDF from Markdown Parts
=========================================
Combines all paper_parts/*.md files into a single styled PDF.

Usage:
    python paper/builders/build_paper_pdf.py

BME 129C Capstone — Sage Clokey — Spring 2026
"""

from pathlib import Path
import markdown
from weasyprint import HTML

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARTS_DIR = PROJECT_ROOT / "paper" / "paper_parts"
OUT_PATH = PROJECT_ROOT / "paper" / "deliverables" / "the_living_architecture_full.pdf"

# Order of sections
SECTIONS = [
    "Title.md",
    "Authors.md",
    "Abstract.md",
    "Introduction.md",
    "Methods.md",
    "Results+Figures.md",
    "Discussion.md",
    "References.md",
]

CSS = """
@page {
    size: letter;
    margin: 1in 1in 1in 1in;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #555;
    }
}

body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
    max-width: 100%;
}

h1 {
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0.3in;
    margin-bottom: 0.15in;
    color: #1a1a1a;
    page-break-after: avoid;
}

/* Title gets bigger */
h1:first-of-type {
    font-size: 22pt;
    margin-top: 1.5in;
    margin-bottom: 0.3in;
}

/* Author block */
.author-block {
    text-align: center;
    margin-bottom: 0.5in;
    font-size: 11pt;
    line-height: 1.6;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    margin-top: 0.25in;
    margin-bottom: 0.1in;
    color: #1a1a1a;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: bold;
    margin-top: 0.2in;
    margin-bottom: 0.08in;
    color: #1a1a1a;
    page-break-after: avoid;
}

p {
    text-align: justify;
    margin-bottom: 0.08in;
    text-indent: 0.3in;
    orphans: 3;
    widows: 3;
}

/* No indent after headings or for first paragraph */
h1 + p, h2 + p, h3 + p, h4 + p {
    text-indent: 0;
}

blockquote p {
    text-indent: 0;
    font-style: italic;
    margin-left: 0.5in;
    margin-right: 0.5in;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

ul, ol {
    margin-left: 0.3in;
    margin-bottom: 0.1in;
}

li {
    margin-bottom: 0.04in;
}

li p {
    text-indent: 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.15in 0;
    font-size: 9pt;
    page-break-inside: avoid;
}

th {
    background-color: #f0f0f0;
    border: 1px solid #999;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: bold;
}

td {
    border: 1px solid #ccc;
    padding: 3pt 6pt;
    text-align: left;
    vertical-align: top;
}

tr:nth-child(even) td {
    background-color: #fafafa;
}

code {
    font-family: "Courier New", monospace;
    font-size: 9.5pt;
    background-color: #f4f4f4;
    padding: 1pt 3pt;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 0.3in 0;
}

/* Section breaks */
.section-break {
    page-break-before: always;
}

/* References section - no indent, hanging indent style */
.references p {
    text-indent: -0.4in;
    padding-left: 0.4in;
    margin-bottom: 0.06in;
}

/* Figure captions */
.figure-caption {
    font-size: 10pt;
    margin-top: 0.05in;
    margin-bottom: 0.15in;
}
"""


def build_html():
    """Combine all markdown sections into styled HTML."""
    md = markdown.Markdown(extensions=["tables", "smarty"])

    html_parts = []

    for i, filename in enumerate(SECTIONS):
        filepath = PARTS_DIR / filename
        if not filepath.exists():
            print(f"  [SKIP] {filename} not found")
            continue

        text = filepath.read_text(encoding="utf-8").strip()
        if not text:
            print(f"  [SKIP] {filename} is empty")
            continue

        # Convert markdown to HTML
        md.reset()
        section_html = md.convert(text)

        # Special handling for Authors — wrap in centered block
        if filename == "Authors.md":
            # Remove the <h1>Authors</h1> heading, wrap content in centered div
            section_html = section_html.replace("<h1>Authors</h1>", "")
            section_html = f'<div class="author-block">{section_html}</div>'

        # Add section break before major sections (not Title/Authors/Abstract)
        if filename in ("Introduction.md", "Methods.md", "Results+Figures.md",
                        "Discussion.md", "References.md"):
            section_html = f'<div class="section-break"></div>{section_html}'

        # Mark References section for special styling
        if filename == "References.md":
            section_html = f'<div class="references">{section_html}</div>'

        html_parts.append(section_html)
        print(f"  [OK] {filename}")

    body = "\n\n".join(html_parts)

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

    return full_html


def main():
    print("=" * 60)
    print("  BUILDING FULL PAPER PDF")
    print("=" * 60)
    print()

    html = build_html()

    # Save intermediate HTML for debugging
    html_path = OUT_PATH.with_suffix(".html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    print(f"\n  HTML saved to: {html_path}")

    # Generate PDF
    print("  Generating PDF...")
    HTML(string=html).write_pdf(str(OUT_PATH))
    print(f"  PDF saved to: {OUT_PATH}")

    print("\n" + "=" * 60)
    print("  COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
