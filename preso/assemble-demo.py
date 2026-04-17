#!/usr/bin/env python3
"""
One-shot assembler for social-proofing-agent demo presentation.
Reads preso/templates/, substitutes project data, writes output.

Usage:
  python preso/assemble-demo.py                    # live mode (default)
  python preso/assemble-demo.py --mode overview    # sales deck only, no presenter
  python preso/assemble-demo.py --mode shareable   # demo with screenshot gallery
  python preso/assemble-demo.py --mode hands-on    # demo with run-it-yourself guide
  python preso/assemble-demo.py --mode live        # demo with live iframe (default)
"""
import re, os, sys, argparse

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

parser = argparse.ArgumentParser()
parser.add_argument('--mode', default='live',
                    choices=['live', 'overview', 'shareable', 'hands-on'])
args = parser.parse_args()
MODE = args.mode

def read(path):
    with open(path, 'r', encoding='utf-8') as f: return f.read()

# ── Load templates ──────────────────────────────────────────────
base       = read(os.path.join(BASE, 'templates', 'base.html'))
demo_css   = read(os.path.join(BASE, 'templates', 'demo.css'))
demo_js    = read(os.path.join(BASE, 'templates', 'demo.js'))
demo_tmpl  = read(os.path.join(BASE, 'templates', 'demo.html'))
integrated = read(os.path.join(BASE, 'akka-sales-integrated.html'))

# ── Extract component table from working reference ───────────────
m = re.search(r'<div class="comp-table">(.*?)</div><!-- /comp-table -->', integrated, re.DOTALL)
components_table_html = m.group(1).strip() if m else '<!-- component table not found -->'

# ── Project-specific data (same for all modes) ───────────────────
PRESENTER_NAME     = "Tyler Jewell"
PRESENTER_TITLE    = "CEO, Akka"
PRESENTER_LINKEDIN = "https://www.linkedin.com/in/tylerjewell/"
SERVICE_URL        = "http://localhost:9004"
REPO_URL           = "https://github.com/aklikic/social-proofing-agent"

DEMO_TITLE = 'Social Proofing <span class="accent">Agent</span>'

DEMO_DESCRIPTION = (
    "An e-commerce retailer needed AI-powered social proof messages on product pages — "
    "&ldquo;Only 3 left!&rdquo; or &ldquo;Bought 12 times in the last hour&rdquo; — "
    "generated intelligently from real-time view counts, order signals, and inventory levels, "
    "with sub-10ms cached reads at scale."
)

REQUIREMENTS_HTML = """
          <li>Ingest pre-aggregated view counts and order events from external analytics</li>
          <li>AI agent selects optimal strategy (URGENCY, VALIDATION, SCARCITY, TRENDING) based on signals</li>
          <li>Generate natural, category-aware copy under 60 characters</li>
          <li>Cache messages in entity state — zero LLM calls on the read path</li>
          <li>Real-time SSE streaming for live UI updates</li>
          <li>Suppress messages when activity falls below threshold</li>
"""

BUILD_TIME = "35m"
LOC        = "1,800"

APP_STATS_HTML = """
        <div class="app-stat"><div class="app-stat-num">8</div><div class="app-stat-label">API endpoints</div></div>
        <div class="app-stat"><div class="app-stat-num">1</div><div class="app-stat-label">Entity</div></div>
        <div class="app-stat"><div class="app-stat-num">5</div><div class="app-stat-label">Event types</div></div>
        <div class="app-stat"><div class="app-stat-num">1</div><div class="app-stat-label">Agent</div></div>
        <div class="app-stat"><div class="app-stat-num">1</div><div class="app-stat-label">View</div></div>
        <div class="app-stat"><div class="app-stat-num">1,800</div><div class="app-stat-label">LOC</div></div>
"""

ARCH_SUMMARY_HTML = """
            <div class="arch-summary-stat"><div class="arch-summary-num">15</div><div class="arch-summary-label">Components</div></div>
            <div class="arch-summary-stat"><div class="arch-summary-num">5</div><div class="arch-summary-label">Event Types</div></div>
            <div class="arch-summary-stat"><div class="arch-summary-num">8</div><div class="arch-summary-label">API Endpoints</div></div>
            <div class="arch-summary-stat"><div class="arch-summary-num">5</div><div class="arch-summary-label">Design Views</div></div>
            <div class="arch-summary-stat"><div class="arch-summary-num">1</div><div class="arch-summary-label">Agent</div></div>
            <div class="arch-summary-stat"><div class="arch-summary-num">1,800</div><div class="arch-summary-label">LOC</div></div>
"""

SEQUENCE_DATA_JSON = """{
  "participants": [
    {"id": "gatling", "name": "Gatling",         "ext": true},
    {"id": "iep",     "name": "Ingestion\\nEP",   "ext": false},
    {"id": "pe",      "name": "Product\\nEntity",  "ext": false, "color": "#F5C518"},
    {"id": "co",      "name": "Consumer",          "ext": false, "color": "#F97316"},
    {"id": "ag",      "name": "Agent",             "ext": false, "color": "#7EC8E3"},
    {"id": "llm",     "name": "LLM",               "ext": true},
    {"id": "spep",    "name": "SocialProof\\nEP",  "ext": false},
    {"id": "browser", "name": "Browser",           "ext": true}
  ],
  "messages": [
    {"region": "Signal Ingestion",        "color": "#2196F3"},
    {"from": 0, "to": 1, "label": "POST /ingestion/views",  "dashed": false},
    {"from": 1, "to": 2, "label": "recordViews(50)",         "dashed": false},
    {"from": 2, "to": 1, "label": "viewCount: 247",          "dashed": true},
    {"region": "Aggregation + Agent",     "color": "#FF9800"},
    {"from": 2, "to": 3, "label": "SignalsAggregated",        "dashed": true},
    {"from": 3, "to": 4, "label": "generateMessage(signals)", "dashed": false},
    {"from": 4, "to": 2, "label": "getProductDetails",        "dashed": false},
    {"from": 2, "to": 4, "label": "{Electronics, stock: 3}",  "dashed": true},
    {"from": 4, "to": 5, "label": "prompt + signals",         "dashed": false},
    {"from": 5, "to": 4, "label": "\\"Only 3 left!\\"",       "dashed": true},
    {"from": 3, "to": 2, "label": "cacheSocialProof",         "dashed": false},
    {"region": "Cached Read (no LLM)",    "color": "#4CAF50"},
    {"from": 7, "to": 6, "label": "GET /social-proof",        "dashed": false},
    {"from": 6, "to": 2, "label": "getSocialProof()",         "dashed": false},
    {"from": 2, "to": 6, "label": "{msg, SCARCITY}",          "dashed": true},
    {"from": 6, "to": 7, "label": "200 OK",                   "dashed": true}
  ]
}"""

# ── Mode-specific App tab content ────────────────────────────────

def app_content_live():
    return f"""<div class="app-frame">
        <div class="app-chrome">
          <div class="app-url">{SERVICE_URL}</div>
        </div>
        <div class="app-body" style="height:420px;padding:0;">
          <iframe src="{SERVICE_URL}" style="width:100%;height:100%;border:none;" title="Social Proofing Agent"></iframe>
        </div>
      </div>"""

def app_content_shareable():
    return """<div class="app-frame">
        <div class="app-chrome">
          <div class="app-url">Social Proofing Agent — Demo Screenshots</div>
        </div>
        <div class="app-body" style="height:420px; display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:16px; background:#0A0A0A; overflow:auto;">
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#F97316; font-weight:700; letter-spacing:.06em;">SCARCITY</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">PlayStation 6</div>
            <div style="font-size:12px; color:#aaa;">Electronics &amp; Tech</div>
            <div style="margin-top:auto; background:#1A0800; border:1px solid #F97316; border-radius:4px; padding:6px 10px; font-size:11px; color:#F97316;">Only 3 left in stock!</div>
            <div style="font-size:10px; color:#555;">👁 247 &nbsp; 🛒 12 &nbsp; 📦 3</div>
          </div>
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#7EC8E3; font-weight:700; letter-spacing:.06em;">TRENDING</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">LEGO Star Wars Set</div>
            <div style="font-size:12px; color:#aaa;">Toys</div>
            <div style="margin-top:auto; background:#001A1A; border:1px solid #7EC8E3; border-radius:4px; padding:6px 10px; font-size:11px; color:#7EC8E3;">Trending now — 89 views this hour</div>
            <div style="font-size:10px; color:#555;">👁 89 &nbsp; 🛒 5 &nbsp; 📦 15</div>
          </div>
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#F5C518; font-weight:700; letter-spacing:.06em;">VALIDATION</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">Weber Spirit BBQ</div>
            <div style="font-size:12px; color:#aaa;">Home &amp; Garden</div>
            <div style="margin-top:auto; background:#1A1600; border:1px solid #F5C518; border-radius:4px; padding:6px 10px; font-size:11px; color:#F5C518;">Bought 47 times today</div>
            <div style="font-size:10px; color:#555;">👁 312 &nbsp; 🛒 47 &nbsp; 📦 18</div>
          </div>
          <div style="background:#111; border:1px solid #222; border-radius:6px; padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:10px; color:#888; font-weight:700; letter-spacing:.06em;">NONE</div>
            <div style="font-size:13px; color:#fff; font-weight:600;">Dulux White Paint 5L</div>
            <div style="font-size:12px; color:#aaa;">Home &amp; Garden</div>
            <div style="margin-top:auto; padding:6px 10px; font-size:11px; color:#555; font-style:italic;">Below threshold — no message</div>
            <div style="font-size:10px; color:#555;">👁 4 &nbsp; 🛒 1 &nbsp; 📦 100</div>
          </div>
        </div>
      </div>"""

def app_content_hands_on():
    return f"""<div class="try-steps" style="max-width:640px;">
        <div class="try-step">
          <div class="try-step-num">01</div>
          <div class="try-step-content">
            <div class="try-step-title">Prerequisites</div>
            <div class="try-step-desc">Java 21+, Maven 3.9+, and the Akka CLI.</div>
            <div class="mini-term">
              <div><span class="prompt">$ </span><span class="cmd">java -version</span></div>
              <div><span class="prompt">$ </span><span class="cmd">mvn -version</span></div>
              <div><span class="prompt">$ </span><span class="cmd">curl -sL https://doc.akka.io/install-cli.sh | bash</span></div>
            </div>
          </div>
        </div>
        <div class="try-step">
          <div class="try-step-num">02</div>
          <div class="try-step-content">
            <div class="try-step-title">Clone and build</div>
            <div class="mini-term">
              <div><span class="prompt">$ </span><span class="cmd">git clone {REPO_URL}</span></div>
              <div><span class="prompt">$ </span><span class="cmd">cd social-proofing-agent</span></div>
              <div><span class="prompt">$ </span><span class="cmd">mvn compile -q</span></div>
            </div>
          </div>
        </div>
        <div class="try-step">
          <div class="try-step-num">03</div>
          <div class="try-step-content">
            <div class="try-step-title">Set your LLM key and run</div>
            <div class="mini-term">
              <div><span class="prompt">$ </span><span class="cmd">export ANTHROPIC_API_KEY=sk-ant-...</span></div>
              <div><span class="prompt">$ </span><span class="cmd">akka local run</span></div>
              <div><span class="prompt">$ </span><span class="cmd">open http://localhost:9000</span></div>
            </div>
          </div>
        </div>
        <div class="try-step">
          <div class="try-step-num">04</div>
          <div class="try-step-content">
            <div class="try-step-title">Add products and trigger social proof</div>
            <div class="try-step-desc">Open the app, click ⚙ and hit <strong>Add All 4</strong>, then send some views to trigger the AI agent.</div>
          </div>
        </div>
      </div>"""

# ── Mode-specific headlines ───────────────────────────────────────
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
        'content':     app_content_hands_on(),
    },
}

# ── Build demo section (skipped for overview) ────────────────────
if MODE == 'overview':
    demo_html_final = ''
    demo_css_final  = ''
    demo_js_final   = ''
else:
    app = MODE_APP[MODE]
    demo_html = demo_tmpl
    subs = {
        '{{DEMO_TITLE}}':            DEMO_TITLE,
        '{{DEMO_DESCRIPTION}}':      DEMO_DESCRIPTION,
        '{{REQUIREMENTS_HTML}}':     REQUIREMENTS_HTML,
        '{{BUILD_TIME}}':            BUILD_TIME,
        '{{LOC}}':                   LOC,
        '{{APP_HEADLINE}}':          app['headline'],
        '{{APP_DESCRIPTION}}':       app['description'],
        '{{APP_CONTENT_HTML}}':      app['content'],
        '{{APP_STATS_HTML}}':        APP_STATS_HTML,
        '{{ARCH_SUMMARY_HTML}}':     ARCH_SUMMARY_HTML,
        '{{COMPONENTS_TABLE_HTML}}': components_table_html,
        '{{REPO_URL}}':              REPO_URL,
        '{{SEQUENCE_DATA_JSON}}':    SEQUENCE_DATA_JSON,
    }
    for k, v in subs.items():
        demo_html = demo_html.replace(k, v)

    # Hands-on: strip Tab 6 nav item and panel (redundant with run guide in App tab)
    if MODE == 'hands-on':
        demo_html = re.sub(r'<!-- TAB6-NAV-START -->.*?<!-- TAB6-NAV-END -->',
                           '', demo_html, flags=re.DOTALL)
        demo_html = re.sub(r'<!-- TAB6-PANEL-START -->.*?<!-- TAB6-PANEL-END -->',
                           '', demo_html, flags=re.DOTALL)

    demo_html_final = demo_html
    demo_css_final  = demo_css
    demo_js_final   = demo_js

# ── Assemble final HTML ──────────────────────────────────────────
output = base

# Presenter info
if MODE == 'overview':
    # Remove the presenter block entirely
    output = re.sub(r'\s*<div class="title-presenter">.*?</div>\s*', '\n',
                    output, flags=re.DOTALL)
    output = output.replace('{{PRESENTER_NAME}}',     '')
    output = output.replace('{{PRESENTER_TITLE}}',    '')
    output = output.replace('{{PRESENTER_LINKEDIN}}', '#')
    # Remove demo-wrapper from views array (filter(Boolean) handles null but cleaner to remove)
    output = output.replace("    document.getElementById('demo-wrapper'),\n", '')
else:
    output = output.replace('{{PRESENTER_NAME}}',     PRESENTER_NAME)
    output = output.replace('{{PRESENTER_TITLE}}',    PRESENTER_TITLE)
    output = output.replace('{{PRESENTER_LINKEDIN}}', PRESENTER_LINKEDIN)

# Inject demo section (empty strings for overview = markers removed cleanly)
output = output.replace('<!-- DEMO_CSS_MARKER -->',  demo_css_final)
output = output.replace('<!-- DEMO_HTML_MARKER -->', demo_html_final)
output = output.replace('/* DEMO_JS_MARKER */',      demo_js_final)

# Fix resilience iframe path — base.html path is relative to preso/
# output lives two levels deeper (samples/social-proofing-agent/)
output = output.replace(
    'src="resilience/resilience.html"',
    'src="../../preso/resilience/resilience.html"'
)

# ── Write output ─────────────────────────────────────────────────
suffix = '' if MODE == 'live' else f'-{MODE}'
out_path = os.path.join(ROOT, 'samples', 'social-proofing-agent',
                        f'demo-presentation{suffix}.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(output)

size_kb = os.path.getsize(out_path) // 1024
print(f"Mode:    {MODE}")
print(f"Written: {out_path}")
print(f"Size:    {size_kb} KB")
print(f"Lines:   {output.count(chr(10))}")

# Sanity checks
checks = [
    ('Resilience path fixed', '../../preso/resilience' in output),
]
if MODE != 'overview':
    checks += [
        ('Demo CSS injected',  '#demo-section .showcase' in output),
        ('Demo HTML',          'id="demo-wrapper"' in output),
        ('Demo JS',            'DEMO SECTION JS' in output),
        ('Sequence data',      'DEMO_SEQUENCE_DATA' in output),
        ('Repo URL',           REPO_URL in output),
        ('Component table',    'comp-row' in output),
    ]
if MODE == 'live':
    checks.append(('Iframe live app', SERVICE_URL in output))
if MODE == 'overview':
    checks.append(('No demo section',  'id="demo-wrapper"' not in output))
    checks.append(('No presenter div', 'class="title-presenter"' not in output))
if MODE == 'hands-on':
    checks.append(('No Tab 6 nav',    'data-tab="5"' not in output))
if MODE == 'shareable':
    # App tab has static cards, not a live iframe
    checks.append(('Screenshot cards', 'Only 3 left in stock' in output))
    checks.append(('No live iframe',   f'src="{SERVICE_URL}"' not in output))

print()
for name, ok in checks:
    print(f"  {'OK' if ok else 'FAIL'}  {name}")
