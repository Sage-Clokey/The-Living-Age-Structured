#!/usr/bin/env python3
"""
Convert all new .md chapters to PDFs and generate updated HTML visualization data.
"""
import os
import glob
import markdown
from weasyprint import HTML

TRILOGY_ROOT = os.path.dirname(os.path.abspath(__file__))

# Styled HTML template for PDF generation
PDF_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Jost:wght@300;400;500&display=swap');

body {{
    font-family: 'Jost', Helvetica, Arial, sans-serif;
    font-weight: 300;
    font-size: 11pt;
    line-height: 1.8;
    color: #1a1a1a;
    max-width: 6.5in;
    margin: 0.75in auto;
    padding: 0;
}}

h1 {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 400;
    font-size: 24pt;
    color: #1a1a1a;
    letter-spacing: 0.06em;
    margin-top: 0;
    margin-bottom: 8pt;
    line-height: 1.2;
    text-align: center;
}}

h2 {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 400;
    font-size: 16pt;
    color: #2a5a2e;
    letter-spacing: 0.04em;
    margin-top: 36pt;
    margin-bottom: 12pt;
    line-height: 1.3;
    border-bottom: 0.5pt solid #ddd;
    padding-bottom: 6pt;
}}

p {{
    font-size: 11pt;
    line-height: 1.85;
    margin-bottom: 14pt;
    text-align: justify;
}}

em {{
    font-style: italic;
    color: #6a5a2a;
}}

strong {{
    font-weight: 500;
}}

blockquote {{
    border-left: 2pt solid #2a5a2e;
    padding: 8pt 16pt;
    margin: 20pt 0;
    background: #f8f8f4;
}}

blockquote p {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-style: italic;
    font-size: 11pt;
    color: #555;
    margin-bottom: 0;
}}

hr {{
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 28pt 0;
}}

ul, ol {{
    padding-left: 20pt;
    margin-bottom: 14pt;
}}

li {{
    font-size: 11pt;
    line-height: 1.75;
    margin-bottom: 6pt;
}}

@page {{
    size: letter;
    margin: 0.75in;
}}
</style>
</head>
<body>
{content}
</body>
</html>"""


def find_md_chapters():
    """Find all .md chapter files in the trilogy."""
    patterns = [
        os.path.join(TRILOGY_ROOT, "Book I*", "Part*", "Chapter*.md"),
        os.path.join(TRILOGY_ROOT, "Book II*", "Part*", "Chapter*.md"),
        os.path.join(TRILOGY_ROOT, "Book III*", "Part*", "Chapter*.md"),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return sorted(files)


def md_to_pdf(md_path):
    """Convert a markdown file to PDF."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML
    html_body = markdown.markdown(md_text, extensions=['extra'])

    # Wrap in styled template
    full_html = PDF_TEMPLATE.format(content=html_body)

    # Generate PDF path (same name, .pdf extension)
    pdf_path = md_path.rsplit('.', 1)[0] + '.pdf'

    # Convert to PDF
    HTML(string=full_html).write_pdf(pdf_path)
    return pdf_path


def main():
    md_files = find_md_chapters()
    print(f"Found {len(md_files)} markdown chapters to convert:\n")

    for md_path in md_files:
        rel = os.path.relpath(md_path, TRILOGY_ROOT)
        # Skip if PDF already exists AND md is not newer
        pdf_path = md_path.rsplit('.', 1)[0] + '.pdf'
        if os.path.exists(pdf_path):
            md_time = os.path.getmtime(md_path)
            pdf_time = os.path.getmtime(pdf_path)
            if pdf_time >= md_time:
                print(f"  SKIP (up to date): {rel}")
                continue

        print(f"  Converting: {rel}")
        try:
            result = md_to_pdf(md_path)
            size_kb = os.path.getsize(result) / 1024
            print(f"    -> {os.path.basename(result)} ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\nDone! Converted markdown chapters to PDF.")


if __name__ == "__main__":
    main()
