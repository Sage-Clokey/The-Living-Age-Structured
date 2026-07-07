"""
Build Full Paper PDF from Markdown Parts
=========================================
Combines all paper_parts/*.md files into a single styled PDF
with embedded figures and proper section numbering.

Usage:
    python paper/builders/build_paper_pdf.py

BME 129C Capstone — Sage Clokey — Spring 2026
"""

import re
from pathlib import Path
import markdown
from weasyprint import HTML

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARTS_DIR = PROJECT_ROOT / "paper" / "paper_parts"
FIG_DIR = PROJECT_ROOT / "paper" / "figures"
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

# Map figure numbers to image files (prefer annotated versions)
FIGURE_MAP = {
    "Figure 1.":  "layer1_topology_annotated.png",
    "Figure 2.":  "layer1b_single_cell_economy_annotated.png",
    "Figure 3.":  "layer1b_price_signals_annotated.png",
    "Figure 4.":  "layer2_economy_annotated.png",
    "Figure 5.":  "layer2_fba_analysis_annotated.png",
    "Figure 6.":  "layer2_fba_perturbation_annotated.png",
    "Figure 7.":  "layer3_trade_network_annotated.png",
    "Figure 8.":  "price_system_of_the_cell.png",
    "Figure 9.":  "immune_shm_hotspots_annotated.png",
    "Figure 10.": "immune_vdj_bias_annotated.png",
    "Figure 11.": "immune_public_clonotypes_annotated.png",
    "Figure 12.": "immune_distributed_summary_annotated.png",
    "Figure 13.": "genome_mutation_hotspots_annotated.png",
    "Figure 14.": "genome_tissue_specialization_annotated.png",
    "Figure 15.": "genome_convergent_evolution_annotated.png",
    "Figure 16.": "genome_distributed_summary_annotated.png",
    "Figure 17.": "viral_genome_composition.png",
    "Figure 18.": "viral_syncytin_conservation.png",
    "Figure 19.": "viral_phage_network.png",
    "Figure 20.": "viral_gut_virome.png",
    "Figure 21.": "viral_erv_regulatory.png",
    "Figure 22.": "viral_autoimmune_rise.png",
    "Figure 23.": "viral_communication_summary.png",
}

# Section number mapping for headings
SECTION_NUMBERS = {
    "Abstract": None,  # no number
    "Introduction": "1",
    "Methods": "2",
    "Results: The Knowledge Is Distributed": "3",
    "Discussion": "4",
    "References": None,  # no number
}

CSS = r"""
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

/* Paper title */
h1.paper-title {
    font-size: 20pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0.3in;
    margin-bottom: 0.15in;
    color: #1a1a1a;
}

/* Section headings (Abstract, 1. Introduction, etc.) */
h1.section-heading {
    font-size: 14pt;
    font-weight: bold;
    text-align: left;
    margin-top: 0.3in;
    margin-bottom: 0.12in;
    color: #1a1a1a;
    page-break-after: avoid;
}

.author-block {
    text-align: center;
    margin-bottom: 0.2in;
    font-size: 11pt;
    line-height: 1.4;
}

.author-block p {
    text-indent: 0;
    text-align: center;
}

h2 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 0.2in;
    margin-bottom: 0.08in;
    color: #1a1a1a;
    page-break-after: avoid;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    margin-top: 0.15in;
    margin-bottom: 0.06in;
    color: #1a1a1a;
    page-break-after: avoid;
}

p {
    text-align: justify;
    margin-bottom: 0.06in;
    margin-top: 0;
    text-indent: 0.3in;
    orphans: 3;
    widows: 3;
}

h1 + p, h2 + p, h3 + p, h4 + p,
.author-block + p,
.figure-block + p {
    text-indent: 0;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

ul, ol {
    margin-left: 0.3in;
    margin-bottom: 0.08in;
}

li {
    margin-bottom: 0.03in;
}

li p {
    text-indent: 0;
    margin-bottom: 0.02in;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.12in 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #f0f0f0;
    border: 1px solid #999;
    padding: 3pt 5pt;
    text-align: left;
    font-weight: bold;
    font-size: 8pt;
}

td {
    border: 1px solid #ccc;
    padding: 2pt 5pt;
    text-align: left;
    vertical-align: top;
    font-size: 8pt;
}

tr:nth-child(even) td {
    background-color: #fafafa;
}

code {
    font-family: "Courier New", monospace;
    font-size: 9pt;
    background-color: #f4f4f4;
    padding: 1pt 3pt;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 0.2in 0;
}

/* Section breaks */
.section-break {
    page-break-before: always;
}

/* Figures */
.figure-block {
    text-align: center;
    margin: 0.2in 0;
    page-break-inside: avoid;
}

.figure-block img {
    max-width: 100%;
    max-height: 5.5in;
    display: block;
    margin: 0 auto;
}

.figure-caption {
    font-size: 9.5pt;
    text-align: justify;
    text-indent: 0;
    margin-top: 0.06in;
    margin-bottom: 0.15in;
    line-height: 1.35;
    color: #333;
}

/* References */
.references p {
    text-indent: -0.4in;
    padding-left: 0.4in;
    margin-bottom: 0.05in;
    font-size: 10pt;
}
"""


def inject_figures(html: str) -> str:
    """Replace figure caption paragraphs with image + caption blocks."""
    for fig_key, fig_file in FIGURE_MAP.items():
        img_path = FIG_DIR / fig_file
        if not img_path.exists():
            continue

        abs_path = img_path.resolve().as_uri()

        # Match <p><strong>Figure N.</strong> caption text</p>
        # The markdown renders **Figure N.** as <strong>Figure N.</strong>
        escaped_key = re.escape(fig_key)
        pattern = rf'<p>\s*<strong>{escaped_key}</strong>\s*(.*?)</p>'

        def replacement(m):
            caption_text = m.group(1)
            return (
                f'<div class="figure-block">'
                f'<img src="{abs_path}" alt="{fig_key.strip(".")}">'
                f'<p class="figure-caption"><strong>{fig_key}</strong> {caption_text}</p>'
                f'</div>'
            )

        html = re.sub(pattern, replacement, html, count=1, flags=re.DOTALL)

    return html


def number_sections(html: str) -> str:
    """Add section numbers and proper CSS classes to h1 headings."""
    # Number the h2 subsections within each major section
    # First, handle h1 section headings
    for heading, number in SECTION_NUMBERS.items():
        if number:
            html = html.replace(
                f'<h1>{heading}</h1>',
                f'<h1 class="section-heading">{number}. {heading}</h1>'
            )
        else:
            html = html.replace(
                f'<h1>{heading}</h1>',
                f'<h1 class="section-heading">{heading}</h1>'
            )

    # Mark the paper title
    html = re.sub(
        r'<h1>(The Living Architecture:.*?)</h1>',
        r'<h1 class="paper-title">\1</h1>',
        html
    )

    # Mark Conclusion heading
    html = html.replace(
        '<h2>Conclusion:',
        '<h2>5. Conclusion:'
    )

    return html


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

        md.reset()
        section_html = md.convert(text)

        # Authors block
        if filename == "Authors.md":
            section_html = section_html.replace("<h1>Authors</h1>", "")
            section_html = f'<div class="author-block">{section_html}</div>'

        # Section breaks before major sections
        if filename in ("Introduction.md", "Methods.md", "Results+Figures.md",
                        "Discussion.md", "References.md"):
            section_html = f'<div class="section-break"></div>{section_html}'

        # References styling
        if filename == "References.md":
            section_html = f'<div class="references">{section_html}</div>'

        html_parts.append(section_html)
        print(f"  [OK] {filename}")

    body = "\n\n".join(html_parts)

    # Post-process: inject figures and number sections
    body = inject_figures(body)
    body = number_sections(body)

    # Count figures injected
    fig_count = body.count('class="figure-block"')
    print(f"\n  Figures embedded: {fig_count}")

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
    print("  BUILDING FULL PAPER PDF (with figures)")
    print("=" * 60)
    print()

    html = build_html()

    # Save intermediate HTML
    html_path = OUT_PATH.with_suffix(".html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML saved to: {html_path}")

    # Generate PDF
    print("  Generating PDF (this may take a moment with figures)...")
    HTML(string=html, base_url=str(FIG_DIR)).write_pdf(str(OUT_PATH))
    print(f"  PDF saved to: {OUT_PATH}")

    print("\n" + "=" * 60)
    print("  COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
