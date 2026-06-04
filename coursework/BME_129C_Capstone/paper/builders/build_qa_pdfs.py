"""Build PDF versions of the capstone Q&A documents using markdown + weasyprint."""

from pathlib import Path
import markdown
from weasyprint import HTML

PAPER_DIR = Path(__file__).resolve().parent.parent

CSS = """
@page {
    size: letter;
    margin: 1in;
}
body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
}
h1 {
    font-size: 18pt;
    margin-top: 0;
    border-bottom: 2px solid #2c5f2d;
    padding-bottom: 6pt;
    color: #2c5f2d;
}
h2 {
    font-size: 14pt;
    margin-top: 24pt;
    color: #2c5f2d;
}
h3 {
    font-size: 12pt;
    margin-top: 18pt;
    color: #333;
}
hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 24pt 0;
}
code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10pt;
    background: #f4f4f4;
    padding: 1px 4px;
    border-radius: 3px;
}
blockquote {
    border-left: 3px solid #2c5f2d;
    margin-left: 0;
    padding-left: 12pt;
    color: #555;
}
ul, ol {
    margin-left: 0;
    padding-left: 20pt;
}
li {
    margin-bottom: 4pt;
}
strong {
    color: #1a1a1a;
}
"""


def md_to_pdf(md_path: Path, pdf_path: Path):
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    full_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{CSS}</style>
</head><body>{html_body}</body></html>"""
    HTML(string=full_html).write_pdf(str(pdf_path))
    print(f"  {pdf_path.name} ({pdf_path.stat().st_size / 1024:.0f} KB)")


def main():
    print("Building Q&A PDFs...")
    writing = PAPER_DIR / "writing"
    deliverables = PAPER_DIR / "deliverables"
    md_to_pdf(
        writing / "capstone_QA_full.md",
        deliverables / "capstone_QA_full.pdf",
    )
    md_to_pdf(
        writing / "capstone_QA_bullets.md",
        deliverables / "capstone_QA_bullets.pdf",
    )
    md_to_pdf(
        writing / "capstone_summary_3page.md",
        deliverables / "capstone_summary_3page.pdf",
    )
    print("Done.")


if __name__ == "__main__":
    main()
