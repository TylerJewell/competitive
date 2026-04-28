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
parser.add_argument('--keep-presenter-placeholders', action='store_true',
    help='Leave {{PRESENTER_*}} placeholders in the output instead of clearing them. '
         'Use when building a base.html template that will be substituted later '
         '(e.g. for the /akka:demo plugin bundle).')
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

    # ── Demo slide: mode-specific substitutions ──────────────────────────────
    if entry['id'] == '12-demo':
        SERVICE_URL = 'http://localhost:9004'
        REPO_URL    = 'https://github.com/aklikic/social-proofing-agent'

        def app_content_live():
            return f'''<div class="app-frame">
        <div class="app-chrome"><div class="app-url">{SERVICE_URL}</div></div>
        <div class="app-body" style="height:420px;padding:0;">
          <iframe src="{SERVICE_URL}" style="width:100%;height:100%;border:none;" title="Social Proofing Agent"></iframe>
        </div>
      </div>'''

        def app_content_shareable():
            return '''<div class="app-frame">
        <div class="app-chrome"><div class="app-url">Social Proofing Agent — Demo Screenshots</div></div>
        <div class="app-body" style="height:420px; display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:16px; background:#0A0A0A; overflow:auto;">
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#F97316; font-weight:700; letter-spacing:.06em;">SCARCITY</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">PlayStation 6</div>
            <div style="font-size:12px; color:#aaa;">Electronics &amp; Tech</div>
            <div style="margin-top:auto; background:#1A0800; border:1px solid #F97316; border-radius:4px; padding:6px 10px; font-size:11px; color:#F97316;">Only 3 left in stock!</div>
            <div style="font-size:10px; color:#555;">&#128065; 247 &nbsp; &#128722; 12 &nbsp; &#128230; 3</div>
          </div>
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#7EC8E3; font-weight:700; letter-spacing:.06em;">TRENDING</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">LEGO Star Wars Set</div>
            <div style="font-size:12px; color:#aaa;">Toys</div>
            <div style="margin-top:auto; background:#001A1A; border:1px solid #7EC8E3; border-radius:4px; padding:6px 10px; font-size:11px; color:#7EC8E3;">Trending now — 89 views this hour</div>
            <div style="font-size:10px; color:#555;">&#128065; 89 &nbsp; &#128722; 5 &nbsp; &#128230; 15</div>
          </div>
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#F5C518; font-weight:700; letter-spacing:.06em;">VALIDATION</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">Weber Spirit BBQ</div>
            <div style="font-size:12px; color:#aaa;">Home &amp; Garden</div>
            <div style="margin-top:auto; background:#1A1600; border:1px solid #F5C518; border-radius:4px; padding:6px 10px; font-size:11px; color:#F5C518;">Bought 47 times today</div>
            <div style="font-size:10px; color:#555;">&#128065; 312 &nbsp; &#128722; 47 &nbsp; &#128230; 18</div>
          </div>
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#888; font-weight:700; letter-spacing:.06em;">NONE</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">Dulux White Paint 5L</div>
            <div style="font-size:12px; color:#aaa;">Home &amp; Garden</div>
            <div style="margin-top:auto; padding:6px 10px; font-size:11px; color:#555; font-style:italic;">Below threshold — no message</div>
            <div style="font-size:10px; color:#555;">&#128065; 4 &nbsp; &#128722; 1 &nbsp; &#128230; 100</div>
          </div>
        </div>
      </div>'''

        MODE_APP = {
            'live': {
                'headline':    'A complete <span class="accent">social proofing system</span>',
                'description': 'Fully functional from first run — ingestion APIs, AI agent pipeline, cached entity reads, SSE streaming, and a live demo UI. Not a scaffold. Not a prototype. A system.',
                'content':     app_content_live(),
            },
            'shareable': {
                'headline':    'A complete <span class="accent">social proofing system</span>',
                'description': 'Four products, four strategies — AI selects the right message for each based on real-time signals. Sub-10ms cached reads, zero LLM calls on the read path.',
                'content':     app_content_shareable(),
            },
            'hands-on': {
                'headline':    'Run it <span class="accent">yourself</span>',
                'description': 'Clone the repo, set your LLM key, and have a working social proofing system in under 5 minutes.',
                'content':     f'''<div class="try-steps" style="max-width:640px;">
        <div class="try-step"><div class="try-step-num">01</div><div class="try-step-content">
          <div class="try-step-title">Prerequisites</div>
          <div class="mini-term"><div><span class="prompt">$ </span><span class="cmd">java -version</span></div><div><span class="prompt">$ </span><span class="cmd">mvn -version</span></div></div>
        </div></div>
        <div class="try-step"><div class="try-step-num">02</div><div class="try-step-content">
          <div class="try-step-title">Clone and build</div>
          <div class="mini-term"><div><span class="prompt">$ </span><span class="cmd">git clone {REPO_URL}</span></div><div><span class="prompt">$ </span><span class="cmd">cd social-proofing-agent && mvn compile -q</span></div></div>
        </div></div>
        <div class="try-step"><div class="try-step-num">03</div><div class="try-step-content">
          <div class="try-step-title">Set your key and run</div>
          <div class="mini-term"><div><span class="prompt">$ </span><span class="cmd">export GOOGLE_AI_GEMINI_API_KEY=your-key</span></div><div><span class="prompt">$ </span><span class="cmd">akka local run</span></div></div>
        </div></div>
      </div>''',
            },
        }

        app = MODE_APP.get(args.mode, MODE_APP['shareable'])

        # Component table is populated by the /akka:demo plugin via project introspection
        components_table_html = '<!-- component table -->'

        SEQUENCE_DATA_JSON = r'''{
  "participants": [
    {"id": "gatling", "name": "Gatling",         "ext": true},
    {"id": "iep",     "name": "Ingestion\nEP",   "ext": false},
    {"id": "pe",      "name": "Product\nEntity",  "ext": false, "color": "#F5C518"},
    {"id": "co",      "name": "Consumer",          "ext": false, "color": "#F97316"},
    {"id": "ag",      "name": "Agent",             "ext": false, "color": "#7EC8E3"},
    {"id": "llm",     "name": "LLM",               "ext": true},
    {"id": "spep",    "name": "SocialProof\nEP",  "ext": false},
    {"id": "browser", "name": "Browser",           "ext": true}
  ],
  "messages": [
    {"region": "Signal Ingestion",     "color": "#2196F3"},
    {"from": 0, "to": 1, "label": "POST /ingestion/views",  "dashed": false},
    {"from": 1, "to": 2, "label": "recordViews(50)",         "dashed": false},
    {"from": 2, "to": 1, "label": "viewCount: 247",          "dashed": true},
    {"region": "Aggregation + Agent",  "color": "#FF9800"},
    {"from": 2, "to": 3, "label": "SignalsAggregated",        "dashed": true},
    {"from": 3, "to": 4, "label": "generateMessage(signals)", "dashed": false},
    {"from": 4, "to": 2, "label": "getProductDetails",        "dashed": false},
    {"from": 2, "to": 4, "label": "{Electronics, stock: 3}",  "dashed": true},
    {"from": 4, "to": 5, "label": "prompt + signals",         "dashed": false},
    {"from": 5, "to": 4, "label": "\"Only 3 left!\"",         "dashed": true},
    {"from": 3, "to": 2, "label": "cacheSocialProof",         "dashed": false},
    {"region": "Cached Read (no LLM)", "color": "#4CAF50"},
    {"from": 7, "to": 6, "label": "GET /social-proof",        "dashed": false},
    {"from": 6, "to": 2, "label": "getSocialProof()",         "dashed": false},
    {"from": 2, "to": 6, "label": "{msg, SCARCITY}",          "dashed": true},
    {"from": 6, "to": 7, "label": "200 OK",                   "dashed": true}
  ]
}'''

        demo_subs = {
            '{{DEMO_TITLE}}':            'Social Proofing <span class="accent">Agent</span>',
            '{{DEMO_DESCRIPTION}}':      'An e-commerce retailer needed AI-powered social proof messages on product pages — &ldquo;Only 3 left!&rdquo; or &ldquo;Bought 12 times in the last hour&rdquo; — generated intelligently from real-time signals, with sub-10ms cached reads at scale.',
            '{{REQUIREMENTS_HTML}}':     '<li>Ingest pre-aggregated view counts and order events from analytics</li><li>AI agent selects optimal strategy (URGENCY, VALIDATION, SCARCITY, TRENDING)</li><li>Generate natural, category-aware copy under 60 characters</li><li>Cache messages in entity state — zero LLM calls on read path</li><li>Real-time SSE streaming for live UI updates</li>',
            '{{BUILD_TIME}}':            '35m',
            '{{LOC}}':                   '1,800',
            '{{APP_HEADLINE}}':          app['headline'],
            '{{APP_DESCRIPTION}}':       app['description'],
            '{{APP_CONTENT_HTML}}':      app['content'],
            '{{APP_STATS_HTML}}':        '<div class="app-stat"><div class="app-stat-num">8</div><div class="app-stat-label">API endpoints</div></div><div class="app-stat"><div class="app-stat-num">1</div><div class="app-stat-label">Entity</div></div><div class="app-stat"><div class="app-stat-num">5</div><div class="app-stat-label">Event types</div></div><div class="app-stat"><div class="app-stat-num">1</div><div class="app-stat-label">Agent</div></div><div class="app-stat"><div class="app-stat-num">1</div><div class="app-stat-label">View</div></div>',
            '{{ARCH_SUMMARY_HTML}}':     '<div class="arch-summary-stat"><div class="arch-summary-num">15</div><div class="arch-summary-label">Components</div></div><div class="arch-summary-stat"><div class="arch-summary-num">5</div><div class="arch-summary-label">Event Types</div></div><div class="arch-summary-stat"><div class="arch-summary-num">8</div><div class="arch-summary-label">API Endpoints</div></div><div class="arch-summary-stat"><div class="arch-summary-num">1</div><div class="arch-summary-label">Agent</div></div>',
            '{{COMPONENTS_TABLE_HTML}}': components_table_html,
            '{{REPO_URL}}':              REPO_URL,
            '{{SEQUENCE_DATA_JSON}}':    SEQUENCE_DATA_JSON,
        }
        for k, v in demo_subs.items():
            html = html.replace(k, v)
            js   = js.replace(k, v)

        # hands-on: strip Tab 6 nav + panel (redundant with run guide in App tab)
        if args.mode == 'hands-on':
            html = re.sub(r'<!-- TAB6-NAV-START -->.*?<!-- TAB6-NAV-END -->',   '', html, flags=re.DOTALL)
            html = re.sub(r'<!-- TAB6-PANEL-START -->.*?<!-- TAB6-PANEL-END -->', '', html, flags=re.DOTALL)

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
elif args.keep_presenter_placeholders:
    # Plugin-template build: keep placeholders intact for downstream substitution.
    pass
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

# logos/
if os.path.exists(logos_dst):
    shutil.rmtree(logos_dst)
shutil.copytree(os.path.join(assets_src, 'logos'), logos_dst)

# resilience/ iframe dependency
resilience_src = os.path.join(ROOT, 'assets', 'resilience')
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
