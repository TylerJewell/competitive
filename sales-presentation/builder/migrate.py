#!/usr/bin/env python3
"""
migrate.py — One-shot migration from preso/templates/base.html into sales-presentation/.

Extracts:
  - shell/shell.html       : HTML scaffold (head, body open/close, style/script tags)
  - shell/shared.css       : Reset, :root vars, keyframes (before first section marker)
  - shell/nav.js           : Keyboard view-jump navigation JS
  - slides/XX-name/slide.css  : Per-section CSS
  - slides/XX-name/slide.html : Per-section HTML fragment
  - slides/XX-name/slide.js   : Per-section JS fragment
  - slides/XX-name/meta.json  : Metadata (nav_id, spacers, scroll heights, images)
  - builder/slide-registry.json
  - builder/image-registry.json
  - presenters/tyler.json

Usage:
  python3 builder/migrate.py                          # from base.html (approved)
  python3 builder/migrate.py --source base-draft.html # from draft (after splice)
"""
import re, os, json, shutil, argparse

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # sales-presentation/
COMP    = os.path.dirname(ROOT)                                          # competition/

parser = argparse.ArgumentParser(description='Migrate base.html into slide files')
parser.add_argument('--source', default='base.html',
    help='Source file in preso/templates/ (default: base.html)')
args = parser.parse_args()

SRC     = os.path.join(COMP, 'preso', 'templates', args.source)
SLIDES  = os.path.join(ROOT, 'slides')
SHELL   = os.path.join(ROOT, 'shell')
BUILDER = os.path.join(ROOT, 'builder')

def read(path):
    with open(path, 'r', encoding='utf-8') as f: return f.read()

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f: f.write(content)

def write_json(path, obj):
    write(path, json.dumps(obj, indent=2) + '\n')

# ─────────────────────────────────────────────────────────────────
# Section definitions — drives all extraction
# ─────────────────────────────────────────────────────────────────
SECTIONS = [
    {
        'folder':      '00-title',
        'css_marker':  'section-0-title',
        'nav_id':      'title',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '100vh' },
        'reveals': { 'scroll_progress': None, 'intersection': [] },
        'images': []
    },
    {
        'folder':      '01-hero',
        'css_marker':  'section-1-hero',
        'nav_id':      'hero',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '140vh' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [{ 'selector': '.hero-stats', 'threshold': 0.6 }]
        },
        'images': []
    },
    {
        'folder':      '02-types',
        'css_marker':  'section-2-types',
        'nav_id':      'st-wrapper',
        'pre_spacer':  20,
        'scroll': { 'envelope_vh': 'calc(100vh * 1.6)' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [{ 'selector': '#st-sticky', 'threshold': 0.0 }]
        },
        'images': []
    },
    {
        'folder':      '03-complexity',
        'css_marker':  'section-3-complexity',
        'nav_id':      's2-wrapper',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '300vh' },
        'reveals': {
            'scroll_progress': { 'attribute': 'data-s2', 'max_steps': 2 },
            'intersection': [
                { 'selector': '[data-s2]', 'threshold': 0.15 },
                { 'selector': '.s2-diagram', 'threshold': 0.8 }
            ]
        },
        'images': []
    },
    {
        'folder':      '04-platform',
        'css_marker':  'section-4-platform',
        'nav_id':      's4-wrapper',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '180vh' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [{ 'selector': '.s4-reveal', 'threshold': 0.15 }]
        },
        'images': ['akka-platform.png']
    },
    {
        'folder':      '05-devzero',
        'css_marker':  'section-5-devzero',
        'nav_id':      's5-wrapper',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '140vh' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [{ 'selector': '.s5-reveal', 'threshold': 0.15 }]
        },
        'images': []
    },
    {
        'folder':      '06-resilience',
        'css_marker':  'section-6-resilience',
        'nav_id':      's6-wrapper',
        'pre_spacer':  30,
        'scroll': { 'envelope_vh': '140vh' },
        'reveals': { 'scroll_progress': None, 'intersection': [] },
        'images': []
    },
    {
        'folder':      '07-governance',
        'css_marker':  'section-7-governance',
        'nav_id':      's7-problem',
        'pre_spacer':  0,
        'scroll': {
            'problem_envelope_vh': '140vh',
            'answer_envelope_vh':  '140vh'
        },
        'reveals': {
            'scroll_progress': { 'attribute': 'data-s7', 'max_steps': 5 },
            'intersection': [{ 'selector': '.s7-reveal', 'threshold': 0.15 }]
        },
        'images': [
            'governance-posture.png', 'interaction-log.png',
            'control-detail.png', 'policy-authoring.png',
            'policy-sandbox.png', 'audit.png'
        ]
    },
    {
        'folder':      '08-customers',
        'css_marker':  'section-customers',
        'nav_id':      'cust-wrapper',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '200vh' },
        'reveals': {
            'scroll_progress': { 'attribute': None, 'note': 'custom scroll-driven progress, see slide.js' },
            'intersection': []
        },
        'images': [
            'customers/manulife.jpg', 'customers/tubi.jpg',
            'customers/swiggy.png',   'customers/johndeere.png',
            'customers/dojo.png'
        ]
    },
    {
        'folder':      '09-packages',
        'css_marker':  'section-packages',
        'nav_id':      'pkg-wrapper',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': 'calc(100vh + 300px)' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [
                { 'selector': '.pkg-reveal', 'threshold': 0.15 },
                { 'selector': '.pkg-tier',   'threshold': 0.15 }
            ]
        },
        'images': []
    },
    {
        'folder':      '10-partners',
        'css_marker':  'section-y-partners',
        'nav_id':      's9-wrapper',
        'pre_spacer':  12,
        'scroll': { 'envelope_vh': '140vh' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [{ 'selector': '.s9-reveal', 'threshold': 0.15 }]
        },
        'images': []
    },
    {
        'folder':      '11-closing',
        'css_marker':  'section-z-closing',
        'nav_id':      'closing',
        'pre_spacer':  0,
        'scroll': { 'envelope_vh': '100vh' },
        'reveals': {
            'scroll_progress': None,
            'intersection': [{ 'selector': '.closing-reveal', 'threshold': 0.15 }]
        },
        'images': []
    },
]

# ─────────────────────────────────────────────────────────────────
# Load source
# ─────────────────────────────────────────────────────────────────
src = read(SRC)
lines = src.splitlines(keepends=True)
print(f'Loaded {SRC}: {len(lines)} lines')

# ─────────────────────────────────────────────────────────────────
# Helper: extract text between two string anchors (first occurrence)
# ─────────────────────────────────────────────────────────────────
def between(text, start, end, after=0):
    s = text.find(start, after)
    if s == -1: return '', -1, -1
    e = text.find(end, s + len(start))
    if e == -1: return '', -1, -1
    return text[s + len(start):e].strip(), s, e + len(end)

def find_nth(text, pattern, n=1):
    """Return position of nth occurrence of pattern."""
    pos = 0
    for _ in range(n):
        pos = text.find(pattern, pos)
        if pos == -1: return -1
        pos += 1
    return pos - 1

# ─────────────────────────────────────────────────────────────────
# 1. Extract CSS blocks
# ─────────────────────────────────────────────────────────────────
style_start = src.find('<style>')
style_end   = src.find('</style>')
all_css     = src[style_start + len('<style>'):style_end]

# Shared CSS: everything before the first section marker
first_marker = f'/* ── {SECTIONS[0]["css_marker"]} ── */'
shared_css_end = all_css.find(first_marker)
shared_css = all_css[:shared_css_end].strip()

# Per-section CSS: between consecutive markers
# Build ordered list of (marker_pos, section_index)
marker_positions = []
for i, sec in enumerate(SECTIONS):
    m = f'/* ── {sec["css_marker"]} ── */'
    pos = all_css.find(m)
    if pos == -1:
        print(f'  WARNING: CSS marker not found for {sec["folder"]}: {m}')
    marker_positions.append((pos, i, m))

# Also find DEMO_CSS_MARKER as the terminal boundary
demo_css_pos = all_css.find('/* ── DEMO_CSS_MARKER ── */')
if demo_css_pos == -1:
    demo_css_pos = len(all_css)

marker_positions.append((demo_css_pos, len(SECTIONS), ''))
marker_positions.sort()

section_css = {}
for idx, (pos, sec_idx, marker) in enumerate(marker_positions[:-1]):
    if sec_idx >= len(SECTIONS): continue
    next_pos = marker_positions[idx + 1][0]
    css_block = all_css[pos + len(marker):next_pos].strip()
    section_css[SECTIONS[sec_idx]['folder']] = css_block

print(f'Extracted CSS for {len(section_css)} sections')

# ─────────────────────────────────────────────────────────────────
# 2. Extract JS blocks
# ─────────────────────────────────────────────────────────────────
script_start = src.find('<script>')
script_end   = src.rfind('</script>')
all_js       = src[script_start + len('<script>'):script_end]

# Find section JS markers (same pattern as CSS)
js_marker_positions = []
for i, sec in enumerate(SECTIONS):
    m = f'/* ── {sec["css_marker"]} ── */'
    pos = all_js.find(m)
    js_marker_positions.append((pos, i, m))

# Keyboard nav comes after all section JS; find it
nav_marker = '/* ── view-jump navigation ── */'
nav_pos = all_js.find(nav_marker)
if nav_pos == -1:
    # Fallback: find the views array
    nav_pos = all_js.find('const views = [')
    if nav_pos == -1:
        nav_pos = all_js.find("'s5-wrapper'")

# DEMO_JS_MARKER as terminal
demo_js_pos = all_js.find('/* DEMO_JS_MARKER */')
if demo_js_pos == -1:
    demo_js_pos = len(all_js)

# Terminal boundary for section JS is nav or kiosk
terminal_js = min(p for p in [nav_pos, demo_js_pos] if p != -1)

js_marker_positions.append((terminal_js, len(SECTIONS), ''))
js_marker_positions = [(p, i, m) for p, i, m in js_marker_positions if p != -1]
js_marker_positions.sort()

section_js = {}
for idx, (pos, sec_idx, marker) in enumerate(js_marker_positions[:-1]):
    if sec_idx >= len(SECTIONS): continue
    next_pos = js_marker_positions[idx + 1][0]
    js_block = all_js[pos + len(marker):next_pos].strip()
    if js_block:
        section_js[SECTIONS[sec_idx]['folder']] = js_block

# Extract keyboard nav JS
nav_js = all_js[terminal_js:demo_js_pos].strip()

# Extract kiosk JS (after demo marker to end)
kiosk_js = all_js[demo_js_pos:].replace('/* DEMO_JS_MARKER */', '').strip()

print(f'Extracted JS for {len(section_js)} sections')

# ─────────────────────────────────────────────────────────────────
# 3. Extract HTML blocks
# ─────────────────────────────────────────────────────────────────
body_start = src.find('<body>')
demo_html_marker = '<!-- DEMO_HTML_MARKER -->'
script_start = src.find('\n<script>', body_start)
body_html = src[body_start + len('<body>'):script_start]

# Build list of (nav_id, section_index) ordered by position
html_positions = []
for i, sec in enumerate(SECTIONS):
    nav_id = sec['nav_id']
    search = f'<div id="{nav_id}"'
    pos = body_html.find(search)
    if pos == -1:
        # Try with space or newline after id
        search = f"id=\"{nav_id}\""
        pos = body_html.find(search)
        if pos == -1:
            print(f'  WARNING: HTML nav_id not found for {sec["folder"]}: {nav_id}')
            pos = -1
        else:
            # Find the opening < before this
            pos = body_html.rfind('<', 0, pos)
    html_positions.append((pos, i))

html_positions = [(p, i) for p, i in html_positions if p != -1]
html_positions.sort()
html_positions.append((len(body_html), len(SECTIONS)))

section_html = {}
for idx, (pos, sec_idx) in enumerate(html_positions[:-1]):
    next_pos = html_positions[idx + 1][0]
    sec = SECTIONS[sec_idx]

    # The raw block may include a pre-spacer div before it
    raw = body_html[pos:next_pos].strip()

    # Strip any leading spacer div (height:Nvh black) that belongs to THIS section's pre_spacer
    # (those are injected by the builder, not stored in slide.html)
    spacer_pat = re.compile(r'^<div\s+style="height:\d+vh[^"]*"[^>]*>\s*</div>\s*', re.DOTALL)
    raw = spacer_pat.sub('', raw)

    # Also strip HTML comments that are just section labels
    raw = re.sub(r'<!--\s*Phase \d+.*?-->\s*', '', raw).strip()

    section_html[sec['folder']] = raw

print(f'Extracted HTML for {len(section_html)} sections')

# ─────────────────────────────────────────────────────────────────
# 4. Extract shell template
# ─────────────────────────────────────────────────────────────────
# Head: everything from <!DOCTYPE> to </style>
head_block = src[:style_start].strip()
closing_head = src[style_end + len('</style>'):body_start].strip()

shell = f"""{head_block}
<style>
{{{{SHARED_CSS}}}}

{{{{SLIDES_CSS}}}}
<!-- DEMO_CSS_MARKER -->
</style>
{closing_head}
<body>
{{{{SLIDES_HTML}}}}
<!-- DEMO_HTML_MARKER -->
<script>
{{{{SLIDES_JS}}}}

{{{{NAV_JS}}}}

{{{{KIOSK_JS}}}}
/* DEMO_JS_MARKER */
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────
# 5. Write all files
# ─────────────────────────────────────────────────────────────────
write(os.path.join(SHELL, 'shell.html'), shell)
write(os.path.join(SHELL, 'shared.css'), shared_css)
write(os.path.join(SHELL, 'nav.js'), nav_js)
write(os.path.join(SHELL, 'kiosk.js'), kiosk_js)
print('Written shell files')

for sec in SECTIONS:
    folder = sec['folder']
    slide_dir = os.path.join(SLIDES, folder)

    write(os.path.join(slide_dir, 'slide.css'),
          section_css.get(folder, f'/* No CSS extracted for {folder} */'))

    write(os.path.join(slide_dir, 'slide.html'),
          section_html.get(folder, f'<!-- No HTML extracted for {folder} -->'))

    write(os.path.join(slide_dir, 'slide.js'),
          section_js.get(folder, ''))

    meta = {
        'id':         folder,
        'nav_id':     sec['nav_id'],
        'pre_spacer': sec['pre_spacer'],
        'scroll':     sec['scroll'],
        'reveals':    sec['reveals'],
        'images':     sec['images'],
        'include_in': ['overview', 'shareable', 'live', 'hands-on']
    }
    write_json(os.path.join(slide_dir, 'meta.json'), meta)

print(f'Written {len(SECTIONS)} slide folders')

# ─────────────────────────────────────────────────────────────────
# 6. Slide registry
# ─────────────────────────────────────────────────────────────────
registry = {
    'slides': [
        { 'id': sec['folder'], 'folder': f'slides/{sec["folder"]}' }
        for sec in SECTIONS
    ]
}
write_json(os.path.join(BUILDER, 'slide-registry.json'), registry)
print('Written slide-registry.json')

# ─────────────────────────────────────────────────────────────────
# 7. Image registry
# ─────────────────────────────────────────────────────────────────
all_images = {}
for sec in SECTIONS:
    for img in sec['images']:
        if img not in all_images:
            all_images[img] = {
                'path': f'assets/images/{img}',
                'alt': img.replace('-', ' ').replace('.png', '').replace('.jpg', '').title(),
                'used_in': [],
                'status': 'live-screenshot' if 'customers' not in img else 'designed-asset',
                'notes': ''
            }
        all_images[img]['used_in'].append(sec['folder'])

write_json(os.path.join(BUILDER, 'image-registry.json'), all_images)
print(f'Written image-registry.json ({len(all_images)} images)')

# ─────────────────────────────────────────────────────────────────
# 8. Presenter config
# ─────────────────────────────────────────────────────────────────
tyler = {
    'name':     'Tyler Jewell',
    'title':    'CEO, Akka',
    'linkedin': 'https://www.linkedin.com/in/tylerjewell/',
    'slug':     'tyler'
}
write_json(os.path.join(ROOT, 'presenters', 'tyler.json'), tyler)
print('Written presenters/tyler.json')

# ─────────────────────────────────────────────────────────────────
# 9. .gitignore
# ─────────────────────────────────────────────────────────────────
gitignore = "generated/\n__pycache__/\n*.pyc\n"
write(os.path.join(ROOT, '.gitignore'), gitignore)

print('\nMigration complete.')
