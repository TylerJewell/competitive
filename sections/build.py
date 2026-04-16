#!/usr/bin/env python3
"""
Combines section HTML files into a single integrated presentation.

Each section file uses marker comments to delimit extractable regions:
  /* SHARED-CSS */  ... /* /SHARED-CSS */
  /* SECTION-CSS */ ... /* /SECTION-CSS */
  <!-- SECTION-HTML --> ... <!-- /SECTION-HTML -->
  /* SECTION-JS */  ... /* /SECTION-JS */

The shared CSS is emitted once (from _shared.css). Section CSS, HTML, and JS
are concatenated in file-order into the final document.

Usage: python sections/build.py
Output: akka-sales-presentation.html (in parent directory)
"""

import re
from pathlib import Path

SECTIONS_DIR = Path(__file__).parent
OUT_DIR  = SECTIONS_DIR.parent / "preso"
OUT_FILE = OUT_DIR / "akka-sales-presentation.html"

# Ordered list of section files
SECTION_FILES = sorted(SECTIONS_DIR.glob("section-*.html"))


def extract(text, open_tag, close_tag):
    """Extract content between marker comments (exclusive of markers)."""
    pattern = re.compile(
        re.escape(open_tag) + r"\s*\n(.*?)\n\s*" + re.escape(close_tag),
        re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


def build():
    shared_css = (SECTIONS_DIR / "_shared.css").read_text(encoding="utf-8")

    all_css = []
    all_html = []
    all_js = []

    for f in SECTION_FILES:
        text = f.read_text(encoding="utf-8")
        css = extract(text, "/* SECTION-CSS */", "/* /SECTION-CSS */")
        html = extract(text, "<!-- SECTION-HTML -->", "<!-- /SECTION-HTML -->")
        js = extract(text, "/* SECTION-JS */", "/* /SECTION-JS */")

        # Fix relative paths: ../<asset> -> <asset> (sections/ -> root)
        rewrites = {
            '../logos/': 'logos/',
            '../images/': 'images/',
            '../resilience.html': 'resilience/resilience.html',
        }
        for prefix, target in rewrites.items():
            css = css.replace(prefix, target)
            html = html.replace(prefix, target)
            js = js.replace(prefix, target)

        section_name = f.stem  # e.g. "section-1-hero"
        all_css.append(f"/* ── {section_name} ── */\n{css}")
        all_html.append(html)
        all_js.append(f"/* ── {section_name} ── */\n{js}")

    combined = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Akka — The Agentic Systems Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>

{shared_css}

{chr(10).join(all_css)}

</style>
</head>
<body>

{chr(10).join(all_html)}

<script>
{chr(10).join(all_js)}
</script>
</body>
</html>
"""

    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_text(combined, encoding="utf-8")
    print(f"Built {OUT_FILE} from {len(SECTION_FILES)} sections")
    for f in SECTION_FILES:
        print(f"  - {f.name}")


if __name__ == "__main__":
    build()
