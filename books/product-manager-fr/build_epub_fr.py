#!/usr/bin/env python3
"""
build_epub_fr.py
Build EPUB for the French edition of "Product Manager?"
Output: ../../_kdp/product-manager-fr.epub

Requires: ebooklib, pip install ebooklib
Run from: books/product-manager-fr/
"""

import os, re, shutil
from pathlib import Path
from ebooklib import epub

# ── Paths ─────────────────────────────────────────────────────────────────────
HERE     = Path(__file__).parent.resolve()
ASSETS   = HERE.parent / "product-manager"
OUT_DIR  = HERE.parent.parent / "_kdp"
OUT_EPUB = OUT_DIR / "product-manager-fr.epub"
OUT_DIR.mkdir(exist_ok=True)

# ── Chapter order and titles ───────────────────────────────────────────────────
CHAPTERS = [
    ("thanks.html",        "Remerciements",                   None),
    ("index.html",         "Préface",                         None),
    ("what-pms-do.html",   "Chapitre 1. Que font vraiment les PM ?",  "1"),
    ("traits.html",        "Chapitre 2. Les qualités que l'IA ne remplace pas",        "2"),
    ("how-pms-think.html", "Chapitre 3. Comment pensent les PM",                  "3"),
    ("peers.html",         "Chapitre 4. Collègues et rapports de force",         "4"),
    ("tools.html",         "Chapitre 5. Les outils — mais l'essentiel est ailleurs", "5"),
    ("do-you-like-it.html","Chapitre 6. Ce métier vous plairait-il ?",        "6"),
    ("paths.html",         "Chapitre 7. Y entrer, en sortir",             "7"),
    ("next.html",          "Chapitre 8. Et maintenant ?",                       "8"),
    ("appendix.html",      "Chapitre 9. Annexe : lire la salle en 2026",                       "9"),
    ("references.html",    "Références",                        None),
    ("author.html",        "À propos de l'auteur",                        None),
]

# ── Inline CSS for EPUB ────────────────────────────────────────────────────────
EPUB_CSS = """
body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1em;
    line-height: 1.65;
    color: #1C1C1E;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 1.6em;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-before: always;
}

h2 {
    font-size: 1.2em;
    font-weight: bold;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
}

h3 {
    font-size: 1.05em;
    font-weight: bold;
    font-style: italic;
    margin-top: 1em;
    margin-bottom: 0.3em;
}

p {
    margin: 0 0 0.6em 0;
    text-align: justify;
}

blockquote {
    border-left: 3px solid #1a3a8a;
    background: #f5f5f5;
    padding: 0.5em 0.75em;
    margin: 1em 0;
    font-style: italic;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9em;
    margin: 1em 0;
}

th {
    background: #0a1428;
    color: white;
    padding: 0.4em 0.5em;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 0.35em 0.5em;
    vertical-align: top;
    border-bottom: 1px solid #ccc;
}

tr:nth-child(even) td { background: #f5f5f5; }

.chapter-sketch img {
    max-width: 100%;
    display: block;
    margin: 1em auto;
}

.author-photo {
    float: right;
    max-width: 40%;
    margin: 0 0 0.5em 0.75em;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 1em 0;
}

.anchor-section { display: none; }

p.calendar-day {
    padding-left: 1.3em;
    text-indent: -1.3em;
    margin: 0.2em 0;
}
p.calendar-day::before { content: "• "; }

.csl-entry { margin-bottom: 0.5em; }
"""


def extract_section(html_path: Path) -> str:
    """Extract main content section from a chapter HTML file."""
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r'<section[^>]*class="normal"[^>]*>(.*?)</section>', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return f"<p>⚠️ Could not extract: {html_path.name}</p>"


def fix_image_paths(content: str, images_dir: Path) -> str:
    """Replace ../product-manager/images/ with epub image filenames."""
    return re.sub(
        r'\.\./product-manager/images/([^"\']+)',
        r'images/\1',
        content
    )


# ── Build EPUB ─────────────────────────────────────────────────────────────────
book = epub.EpubBook()
book.set_identifier("patrickthoffman-product-manager-fr-2026")
book.set_title("Product Manager ?")
book.set_language("fr")
book.add_author("Patrick T. Hoffman")
book.add_metadata("DC", "description",
    "Un guide sans fard pour savoir si le product management est fait pour vous — écrit après que l'IA a changé ce métier.")
book.add_metadata("DC", "rights", "Copyright © 2026 Patrick T. Hoffman")

# Add CSS
style = epub.EpubItem(uid="style", file_name="style/book.css",
                      media_type="text/css", content=EPUB_CSS)
book.add_item(style)

# Add images
images_dir = ASSETS / "images"
image_items = {}
if images_dir.exists():
    for img_path in images_dir.iterdir():
        if img_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            ext = img_path.suffix.lower()
            mt = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                  "png": "image/png", "gif": "image/gif",
                  "webp": "image/webp"}.get(ext.lstrip("."), "image/jpeg")
            img_data = img_path.read_bytes()
            img_item = epub.EpubItem(
                uid=f"img_{img_path.stem}",
                file_name=f"images/{img_path.name}",
                media_type=mt,
                content=img_data
            )
            book.add_item(img_item)
            image_items[img_path.name] = img_item

# Build chapters
epub_chapters = []

for filename, title, chapter_num in CHAPTERS:
    ch_path = HERE / filename
    if not ch_path.exists():
        print(f"  ⚠️  Missing: {filename}")
        continue

    content = extract_section(ch_path)
    content = fix_image_paths(content, images_dir)

    chapter_html = f"""<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">
<head>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="../style/book.css"/>
</head>
<body>
{content}
</body>
</html>"""

    uid = filename.replace(".html", "")
    ch = epub.EpubHtml(title=title, file_name=f"chapters/{filename}",
                       lang="fr", uid=uid)
    ch.content = chapter_html
    ch.add_item(style)
    book.add_item(ch)
    epub_chapters.append(ch)

# Table of contents
toc_entries = []
for ch_item, (filename, title, _) in zip(epub_chapters, CHAPTERS):
    toc_entries.append(epub.Link(f"chapters/{filename}", title, filename.replace(".html", "")))

book.toc = toc_entries
book.add_item(epub.EpubNcx())

nav = epub.EpubNav()
book.add_item(nav)

book.spine = [nav] + epub_chapters

# Write
print(f"Writing French EPUB → {OUT_EPUB}")
epub.write_epub(str(OUT_EPUB), book, {"epub3_pages": False})
print(f"Done. Output: {OUT_EPUB}")
size_kb = OUT_EPUB.stat().st_size // 1024
print(f"Size: {size_kb:,} KB")
