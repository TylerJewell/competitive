#!/usr/bin/env python3
"""
Assembles the Akka sales presentation from slide files.

Usage:
  python3 builder/build.py                         # all slides, overview mode
  python3 builder/build.py --mode shareable        # filter by mode
  python3 builder/build.py --presenter tyler       # personalise with presenter data
  python3 builder/build.py --out myfile.html       # custom output path

Output: generated/<mode>/index.html  (default)
"""

import json, os, sys, argparse, re, shutil
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inline_external import process as inline_external

BASE    = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(BASE)
COMP    = os.path.dirname(ROOT)
SLIDES  = os.path.join(ROOT, 'slides')
SHELL   = os.path.join(ROOT, 'shell')
GEN     = os.path.join(ROOT, 'generated')
PRESENTERS = os.path.join(ROOT, 'presenters')

# ── helpers ──────────────────────────────────────────────────────────────────

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ── CLI ──────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description='Build Akka sales presentation')
parser.add_argument('--mode', default='overview',
    choices=['overview', 'shareable', 'live', 'hands-on'],
    help='Presentation mode (default: overview)')
parser.add_argument('--presenter', default=None,
    help='Presenter JSON file stem in presenters/ (e.g. "tyler")')
parser.add_argument('--out', default=None,
    help='Output file path (default: generated/<mode>/index.html)')
args = parser.parse_args()

out_path = args.out or os.path.join(GEN, args.mode, 'index.html')

# ── Load registry ─────────────────────────────────────────────────────────────

registry = read_json(os.path.join(BASE, 'slide-registry.json'))

# ── Load shell ────────────────────────────────────────────────────────────────

shell_template = read(os.path.join(SHELL, 'shell.html'))
shared_css     = read(os.path.join(SHELL, 'shared.css'))
nav_js         = read(os.path.join(SHELL, 'nav.js'))
kiosk_js       = read(os.path.join(SHELL, 'kiosk.js'))

# ── Load presenter data ───────────────────────────────────────────────────────

presenter = {}
if args.presenter:
    pfile = os.path.join(PRESENTERS, f'{args.presenter}.json')
    if os.path.exists(pfile):
        presenter = read_json(pfile)
    else:
        print(f'Warning: presenter file not found: {pfile}')

# ── Assemble slides ───────────────────────────────────────────────────────────

slides_css_parts  = []
slides_html_parts = []
slides_js_parts   = []
head_script_tags  = []   # CDN scripts collected from external inlines

included = 0
skipped  = 0

for entry in registry['slides']:
    slide_dir = os.path.join(ROOT, entry['folder'])
    meta = read_json(os.path.join(slide_dir, 'meta.json'))

    # Mode filter
    if args.mode not in meta.get('include_in', ['overview']):
        skipped += 1
        continue

    included += 1

    # Pre-spacer injection
    pre_spacer = meta.get('pre_spacer', 0)
    if pre_spacer and str(pre_spacer) != '0':
        unit = 'vh' if isinstance(pre_spacer, int) else ''
        spacer = f'<div style="height:{pre_spacer}{unit};background:var(--black)"></div>\n'
    elif isinstance(pre_spacer, str) and pre_spacer.endswith('px'):
        spacer = f'<div style="height:{pre_spacer};background:var(--black)"></div>\n'
    else:
        spacer = ''

    css  = read(os.path.join(slide_dir, 'slide.css'))
    html = read(os.path.join(slide_dir, 'slide.html'))
    js   = read(os.path.join(slide_dir, 'slide.js'))

    # External inline: replace <iframe> placeholder with inlined HTML/CSS/JS
    ext_cfg = meta.get('external_inline')
    if ext_cfg:
        src_path = os.path.normpath(os.path.join(slide_dir, ext_cfg['source']))
        if os.path.exists(src_path):
            inlined = inline_external(
                src_path,
                wrapper_id=ext_cfg['wrapper_id'],
                root_id=ext_cfg.get('root_id', 'root')
            )
            placeholder = ext_cfg.get('iframe_placeholder', '')
            iframe_tag  = f'<iframe src="{placeholder}"' if placeholder else ''
            if iframe_tag and iframe_tag in html:
                # Find the full <iframe ...></iframe> or self-closing and replace it
                html = re.sub(
                    r'<iframe\s[^>]*' + re.escape(placeholder) + r'[^>]*>(?:</iframe>)?',
                    inlined.html,
                    html
                )
            else:
                html += '\n' + inlined.html  # fallback: append

            css += '\n\n/* ── external inline: ' + ext_cfg['source'] + ' ── */\n' + inlined.css
            if inlined.js.strip():
                js  += '\n\n/* ── external inline: ' + ext_cfg['source'] + ' ── */\n' + inlined.js

            for tag in inlined.head_scripts:
                if tag not in head_script_tags:
                    head_script_tags.append(tag)
            print(f'  Inlined external: {os.path.basename(src_path)} -> #{ext_cfg["wrapper_id"]}')
        else:
            print(f'  WARNING: external source not found: {src_path}')

    slides_css_parts.append(f'/* ── {entry["id"]} ── */\n{css}')
    slides_html_parts.append(spacer + html)
    if js.strip():
        slides_js_parts.append(f'/* ── {entry["id"]} ── */\n{js}')

# ── Apply presenter substitutions ─────────────────────────────────────────────

def apply_presenter(html, p):
    for key, value in p.items():
        html = html.replace(f'{{{{PRESENTER_{key.upper()}}}}}', value)
    return html

slides_html_combined = '\n\n'.join(slides_html_parts)
if presenter:
    slides_html_combined = apply_presenter(slides_html_combined, presenter)
else:
    # No presenter: clear all PRESENTER_ placeholders so no raw {{...}} leak into output
    slides_html_combined = re.sub(r'\{\{PRESENTER_[A-Z_]+\}\}', '', slides_html_combined)

# ── Build final HTML ──────────────────────────────────────────────────────────

result = shell_template
result = result.replace('{{SHARED_CSS}}', shared_css)
result = result.replace('{{SLIDES_CSS}}',  '\n\n'.join(slides_css_parts))
result = result.replace('{{SLIDES_HTML}}', slides_html_combined)
result = result.replace('{{SLIDES_JS}}',   '\n\n'.join(slides_js_parts))
result = result.replace('{{NAV_JS}}',      nav_js)
result = result.replace('{{KIOSK_JS}}',    kiosk_js)

# Inject CDN scripts from external inlines just before </head>
if head_script_tags:
    injection = '\n'.join(head_script_tags) + '\n'
    result = result.replace('</head>', injection + '</head>', 1)

# ── Write output ──────────────────────────────────────────────────────────────

write(out_path, result)

# Copy assets alongside HTML so relative paths work when opening in a browser
out_dir = os.path.dirname(out_path)
assets_src = os.path.join(ROOT, 'assets')

images_dst = os.path.join(out_dir, 'images')
logos_dst  = os.path.join(out_dir, 'logos')

# images/ flat + customers/ subdir
if os.path.exists(images_dst):
    shutil.rmtree(images_dst)
shutil.copytree(os.path.join(assets_src, 'images'), images_dst)

# Customers subdir (referenced as images/customers/*.png)
customers_src = os.path.join(os.path.dirname(os.path.dirname(assets_src)),
                             'preso', 'images', 'customers')
if os.path.exists(customers_src):
    shutil.copytree(customers_src, os.path.join(images_dst, 'customers'),
                    dirs_exist_ok=True)

# logos/
if os.path.exists(logos_dst):
    shutil.rmtree(logos_dst)
shutil.copytree(os.path.join(assets_src, 'logos'), logos_dst)

# resilience/ iframe dependency
resilience_src = os.path.join(COMP, 'preso', 'resilience')
resilience_dst = os.path.join(out_dir, 'resilience')
if os.path.exists(resilience_src):
    if os.path.exists(resilience_dst):
        shutil.rmtree(resilience_dst)
    shutil.copytree(resilience_src, resilience_dst)

size_kb = os.path.getsize(out_path) // 1024
print(f'Mode:      {args.mode}')
print(f'Slides:    {included} included, {skipped} skipped')
if presenter:
    print(f'Presenter: {args.presenter}')
print(f'Output:    {out_path}')
print(f'Size:      {size_kb} KB  ({result.count(chr(10)):,} lines)')
print(f'Assets:    images/ and logos/ copied to {out_dir}/')
