"""
Build 4-Page Summary Paper PDF (with key figures)
===================================================
Converts paper_parts/paper_4page.md into a compact PDF
with embedded figures.

Usage:
    python paper/builders/build_4page_pdf.py

BME 129C Capstone — Sage Clokey — Spring 2026
"""

import re
from pathlib import Path
import markdown
from weasyprint import HTML

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MD_PATH = PROJECT_ROOT / "paper" / "paper_parts" / "paper_4page.md"
FIG_DIR = PROJECT_ROOT / "paper" / "figures"
OUT_PATH = PROJECT_ROOT / "paper" / "deliverables" / "the_living_architecture_4page.pdf"

# Map figure numbers to image files
FIGURE_MAP = {
    "Figure 1.": "layer1_topology_annotated.png",
    "Figure 2.": "layer2_economy_annotated.png",
    "Figure 3.": "layer2_fba_analysis_annotated.png",
    "Figure 4.": "immune_distributed_summary_annotated.png",
    "Figure 5.": "genome_distributed_summary_annotated.png",
}

CSS = r"""
@page {
    size: letter;
    margin: 0.75in 0.75in 0.75in 0.75in;
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        color: #555;
    }
}

body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 9pt;
    line-height: 1.25;
    color: #1a1a1a;
    max-width: 100%;
}

h1 {
    font-size: 15pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0.15in;
    margin-bottom: 0.08in;
    color: #1a1a1a;
}

h2 {
    font-size: 10.5pt;
    font-weight: bold;
    margin-top: 0.12in;
    margin-bottom: 0.05in;
    color: #1a1a1a;
    page-break-after: avoid;
}

h3 {
    font-size: 9.5pt;
    font-weight: bold;
    margin-top: 0.08in;
    margin-bottom: 0.03in;
    color: #1a1a1a;
    page-break-after: avoid;
}

/* Author block */
h1 + p, h1 + p + p, h1 + p + p + p {
    text-align: center;
    text-indent: 0;
    margin-bottom: 0.02in;
    font-size: 9.5pt;
}

p {
    text-align: justify;
    margin-bottom: 0.03in;
    margin-top: 0;
    text-indent: 0.25in;
    orphans: 3;
    widows: 3;
}

h1 + p, h2 + p, h3 + p,
.figure-block + p {
    text-indent: 0;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.06in 0;
    font-size: 7.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #f0f0f0;
    border: 1px solid #999;
    padding: 1.5pt 3pt;
    text-align: left;
    font-weight: bold;
    font-size: 7pt;
}

td {
    border: 1px solid #ccc;
    padding: 1pt 3pt;
    text-align: left;
    vertical-align: top;
    font-size: 7pt;
}

tr:nth-child(even) td {
    background-color: #fafafa;
}

/* Figures */
.figure-block {
    text-align: center;
    margin: 0.1in 0;
    page-break-inside: avoid;
}

.figure-block img {
    max-width: 100%;
    max-height: 2.6in;
    display: block;
    margin: 0 auto;
}

.figure-caption {
    font-size: 8.5pt;
    text-align: justify;
    text-indent: 0;
    margin-top: 0.04in;
    margin-bottom: 0.08in;
    line-height: 1.25;
    color: #333;
}

/* References */
.references p {
    text-indent: -0.35in;
    padding-left: 0.35in;
    margin-bottom: 0.02in;
    font-size: 8pt;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 0.08in 0;
}
"""


def inject_figures(html: str) -> str:
    """Replace figure caption paragraphs with image + caption blocks."""
    for fig_key, fig_file in FIGURE_MAP.items():
        img_path = FIG_DIR / fig_file
        if not img_path.exists():
            print(f"  [MISS] {fig_file}")
            continue

        abs_path = img_path.resolve().as_uri()
        escaped_key = re.escape(fig_key)
        pattern = rf'<p>\s*<strong>{escaped_key}</strong>\s*(.*?)</p>'

        def replacement(m, _abs=abs_path, _key=fig_key):
            caption_text = m.group(1)
            return (
                f'<div class="figure-block">'
                f'<img src="{_abs}" alt="{_key.strip(".")}">'
                f'<p class="figure-caption"><strong>{_key}</strong> {caption_text}</p>'
                f'</div>'
            )

        html = re.sub(pattern, replacement, html, count=1, flags=re.DOTALL)

    return html


def build():
    print("=" * 50)
    print("  BUILDING 4-PAGE SUMMARY PDF (with figures)")
    print("=" * 50)

    text = MD_PATH.read_text(encoding="utf-8").strip()

    # Split off references section for special styling
    if "## References" in text:
        main_text, ref_text = text.split("## References", 1)
        ref_text = "## References" + ref_text
    else:
        main_text = text
        ref_text = ""

    md = markdown.Markdown(extensions=["tables", "smarty"])
    body = md.convert(main_text)

    if ref_text:
        md.reset()
        ref_html = md.convert(ref_text)
        ref_html = f'<div class="references">{ref_html}</div>'
        body += "\n" + ref_html

    # Inject figures
    body = inject_figures(body)
    fig_count = body.count('class="figure-block"')
    print(f"  Figures embedded: {fig_count}")

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

    # Save HTML
    html_path = OUT_PATH.with_suffix(".html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(full_html, encoding="utf-8")
    print(f"  HTML: {html_path}")

    # Generate PDF
    print("  Generating PDF...")
    HTML(string=full_html, base_url=str(FIG_DIR)).write_pdf(str(OUT_PATH))
    print(f"  PDF:  {OUT_PATH}")

    print("=" * 50)
    print("  COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    build()
