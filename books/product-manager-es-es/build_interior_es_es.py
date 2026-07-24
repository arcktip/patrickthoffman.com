#!/usr/bin/env python3
"""
build_interior_es_es.py
Build KDP print interior PDF for the Spanish (Spain) edition of "Product Manager?"
Output: ../../_kdp/product-manager-interior-es-es.pdf

Requires: weasyprint >= 69, pip install weasyprint
Run from: books/product-manager-es-es/
"""

import os, re
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# ── Paths ────────────────────────────────────────────────────────────────────
HERE     = Path(__file__).parent.resolve()
ASSETS   = HERE.parent / "product-manager"   # shared CSS, images, libs
OUT_DIR  = HERE.parent.parent / "_kdp"
OUT_PDF  = OUT_DIR / "product-manager-interior-es-es.pdf"
OUT_DIR.mkdir(exist_ok=True)

# ── Chapter order ─────────────────────────────────────────────────────────────
CHAPTERS = [
    "thanks.html",
    "index.html",
    "what-pms-do.html",
    "traits.html",
    "how-pms-think.html",
    "peers.html",
    "tools.html",
    "do-you-like-it.html",
    "paths.html",
    "next.html",
    "appendix.html",
    "references.html",
    "author.html",
]

# ── Print CSS (injected on top of site CSS) ───────────────────────────────────
PRINT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@400;500&display=swap');

/* KDP trim: 6×9 in */
@page {
    size: 6in 9in;
    margin: 0.875in 0.75in 0.875in 0.875in;
    @bottom-center {
        content: counter(page);
        font-family: 'DM Sans', sans-serif;
        font-size: 9pt;
        color: #888;
    }
}

/* First page of each chapter — no page number */
@page :first {
    @bottom-center { content: none; }
}

/* Reset screen chrome */
body { margin: 0; padding: 0; background: white !important; }
.pth-site-nav, .book-summary, .book-header,
.navigation, #pth-menu-btn { display: none !important; }

.book, .book-body, .body-inner,
.page-wrapper, .page-inner { all: unset; display: block; }

/* Typography */
.page-inner section, section.normal {
    max-width: 100%;
    margin: 0;
    padding: 0;
    font-family: 'DM Sans', sans-serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1C1C1E;
}

h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 900 !important;
    font-size: 22pt !important;
    line-height: 1.2 !important;
    margin-top: 0.5in !important;
    margin-bottom: 0.3in !important;
    page-break-before: always;
    color: #1C1C1E !important;
}

h1:first-child { page-break-before: avoid; margin-top: 0.2in !important; }

h2 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    font-size: 14pt !important;
    margin-top: 0.35in !important;
    margin-bottom: 0.12in !important;
    color: #1C1C1E !important;
}

h3 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    font-size: 11.5pt !important;
    font-style: italic;
    margin-top: 0.25in !important;
    margin-bottom: 0.08in !important;
    color: #333 !important;
}

p { margin: 0 0 0.55em 0; orphans: 3; widows: 3; }

/* Block quotes */
blockquote {
    border-left: 3px solid #1a3a8a;
    background: #F0F2F5;
    padding: 0.5em 0.75em;
    margin: 1em 0;
    border-radius: 0 6px 6px 0;
}
blockquote p {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 10.5pt;
    color: #555;
    margin: 0;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9.5pt;
    margin: 1em 0;
    page-break-inside: avoid;
}
th {
    background: #0a1428 !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    padding: 0.4em 0.5em;
    text-align: left;
}
td {
    padding: 0.35em 0.5em;
    vertical-align: top;
    border-bottom: 1px solid #D1D5DB;
}
tr:nth-child(even) td { background: #F0F2F5; }

/* Images */
.chapter-sketch {
    text-align: center;
    margin: 1em 0;
    page-break-inside: avoid;
}
.chapter-sketch img {
    max-width: 90%;
    max-height: 3.5in;
}
.author-photo {
    float: right;
    width: 1.8in;
    margin: 0 0 0.5em 0.75em;
    border-radius: 4px;
}

/* HR */
hr {
    border: none;
    border-top: 1px solid #D1D5DB;
    margin: 1em 0;
}

/* Anchor links — hide in print */
.anchor-section { display: none !important; }

/* Calendar day bullets (chapter 6) */
p.calendar-day {
    padding-left: 1.3em;
    text-indent: -1.3em;
    margin: 0.2em 0;
}
p.calendar-day::before { content: "• "; }

/* References */
.csl-bib-body { font-size: 10pt; }
.csl-entry { margin-bottom: 0.4em; }

/* Author bio */
.author-bio { overflow: hidden; }
"""

# ── Merge all chapters into one HTML document ─────────────────────────────────
def extract_body(html_path: Path) -> str:
    """Extract the <section class='normal'> content from a chapter file."""
    text = html_path.read_text(encoding="utf-8")
    # Find content between <section class="normal" ...> and </section>
    m = re.search(r'<section[^>]*class="normal"[^>]*>(.*?)</section>', text, re.DOTALL)
    if m:
        return m.group(1)
    # Fallback: grab div#... inside page-inner
    m2 = re.search(r'<div class="page-inner">(.*?)</div>\s*</div>\s*</div>\s*</div>', text, re.DOTALL)
    if m2:
        return m2.group(1)
    return f"<p>⚠️ Could not extract content from {html_path.name}</p>"


combined_parts = []
for ch in CHAPTERS:
    ch_path = HERE / ch
    if not ch_path.exists():
        print(f"  ⚠️  Missing: {ch}")
        continue
    content = extract_body(ch_path)
    combined_parts.append(f"\n<!-- === {ch} === -->\n{content}\n")

full_body = "\n".join(combined_parts)

# Fix relative image paths: ../product-manager/images/ → absolute file:// path
images_dir = ASSETS / "images"
full_body = full_body.replace(
    "../product-manager/images/",
    images_dir.as_uri() + "/"
)

MERGED_HTML = f"""<!DOCTYPE html>
<html lang="es" xml:lang="es">
<head>
  <meta charset="utf-8" />
  <title>¿Product Manager?</title>
</head>
<body>
{full_body}
</body>
</html>"""

# ── Render ────────────────────────────────────────────────────────────────────
font_config = FontConfiguration()
css = CSS(string=PRINT_CSS, font_config=font_config)

print(f"Rendering Spanish (Spain) PDF → {OUT_PDF}")
html = HTML(string=MERGED_HTML, base_url=str(HERE))
html.write_pdf(str(OUT_PDF), stylesheets=[css], font_config=font_config)
print(f"Done. Output: {OUT_PDF}")
