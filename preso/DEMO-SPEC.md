# /akka:demo Skill — Complete Specification

This document is the authoritative reference for the `/akka:demo` skill. It captures all
architecture decisions, assembly rules, CSS/JS patterns, mode behaviors, and bugs
discovered during development and testing. When implementing the skill, follow this
document precisely — do not invent alternatives to what is specified here.

---

## 1. What the Skill Does

`/akka:demo` generates a personalized, self-contained Akka sales presentation as a
single HTML file. It combines:

1. The full Akka platform sales deck (`base.html`)
2. A project-specific Demo Showcase section appended after the sales deck

The output opens in any browser, presents full-screen, and requires no server or build
tool to view. A salesperson can email it, share it via Drive, or present it live.

---

## 2. Output Files

All output goes to the project root or the directory specified by `--output`.

| Mode | Default filename | Demo section | Presenter |
|------|-----------------|--------------|-----------|
| live | `demo-presentation.html` | Yes, live iframe | Yes |
| overview | `demo-presentation-overview.html` | No | No |
| shareable | `demo-presentation-shareable.html` | Yes, static cards | Yes |
| hands-on | `demo-presentation-hands-on.html` | Yes, run guide | Yes |

When generating for `samples/social-proofing-agent/`, the resilience iframe path must be
corrected (see §8.2).

---

## 3. Template System Architecture

Assembly is template-based. Claude reads four files from `preso/templates/` and
performs string substitution. There is no Node.js, no build step, no runtime dependency.

### Template files

```
preso/templates/
  base.html    — Full Akka sales presentation with 5 insertion markers
  demo.css     — All demo section CSS, scoped under #demo-section
  demo.js      — All demo section JS (tab switching, SVG, keyboard nav)
  demo.html    — Demo section HTML structure with {{PLACEHOLDER}} markers
```

### Insertion markers in base.html

| Marker | Location | What gets inserted |
|--------|----------|--------------------|
| `{{PRESENTER_NAME}}` | Title slide `.title-presenter` anchor text | Presenter name string |
| `{{PRESENTER_TITLE}}` | Title slide `.title-presenter-title` | Presenter title string |
| `{{PRESENTER_LINKEDIN}}` | Title slide `.title-presenter` href | LinkedIn URL or `#` |
| `<!-- DEMO_CSS_MARKER -->` | Just before `</style>` | Full contents of `demo.css` |
| `<!-- DEMO_HTML_MARKER -->` | Between `</div>` (s9-wrapper close) and `<section id="closing">` | Substituted `demo.html` |
| `/* DEMO_JS_MARKER */` | Just before `</script>` | Full contents of `demo.js` |

The views array in base.html already contains:
```javascript
document.getElementById('demo-wrapper'),
```
between `s9-wrapper` and `closing`. No further JS changes are needed at assembly time.

### Placeholders in demo.html

| Placeholder | Content |
|-------------|---------|
| `{{DEMO_TITLE}}` | Project name HTML, e.g. `Social Proofing <span class="accent">Agent</span>` |
| `{{DEMO_DESCRIPTION}}` | One-paragraph project description (HTML entities OK) |
| `{{REQUIREMENTS_HTML}}` | One or more `<li>` items for the Brief tab requirements list |
| `{{BUILD_TIME}}` | Spec-to-system time, e.g. `"35m"` |
| `{{LOC}}` | Total Java LOC formatted with comma, e.g. `"1,800"` |
| `{{APP_HEADLINE}}` | App tab h2 HTML |
| `{{APP_DESCRIPTION}}` | App tab one-sentence description |
| `{{APP_CONTENT_HTML}}` | Mode-specific app frame (see §5) |
| `{{APP_STATS_HTML}}` | One or more `.app-stat` divs |
| `{{ARCH_SUMMARY_HTML}}` | Six `.arch-summary-stat` divs |
| `{{COMPONENTS_TABLE_HTML}}` | Full component table inner HTML (groups + rows + details) |
| `{{REPO_URL}}` | Git repo URL for Tab 6 step 3 terminal |
| `{{SEQUENCE_DATA_JSON}}` | JSON object `{participants:[...], messages:[...]}` |

**CRITICAL:** Do NOT put `{{COMPONENTS_TABLE_HTML}}` or `{{REPO_URL}}` or
`{{SEQUENCE_DATA_JSON}}` inside any HTML comment block. The component table HTML
contains `-->` sequences (HTML comments like `<!-- Design Views -->`), which will
prematurely close any outer HTML comment and cause the substituted content to render
as visible raw text on screen. The `demo.html` template has NO comment block at the top
for this reason.

### Assembly order

```python
# 1. Load all templates
base, demo_css, demo_js, demo_tmpl = read each file

# 2. Build demo HTML: substitute all {{PLACEHOLDER}} into demo_tmpl
demo_html = demo_tmpl
for k, v in subs.items():
    demo_html = demo_html.replace(k, v)

# 3. Apply mode-specific post-processing to demo_html (hands-on: strip Tab 6)

# 4. Assemble into base
output = base
output = output.replace('{{PRESENTER_NAME}}', ...)
output = output.replace('{{PRESENTER_TITLE}}', ...)
output = output.replace('{{PRESENTER_LINKEDIN}}', ...)
output = output.replace('<!-- DEMO_CSS_MARKER -->', demo_css)
output = output.replace('<!-- DEMO_HTML_MARKER -->', demo_html)
output = output.replace('/* DEMO_JS_MARKER */', demo_js)

# 5. Apply path fixes
output = output.replace('src="resilience/resilience.html"',
                         'src="../../preso/resilience/resilience.html"')

# 6. Write output
```

Always use `encoding='utf-8'` for all file reads and writes. Windows default encoding
(cp1252) will corrupt the output.

---

## 4. Mode Behaviors

### 4a. live (default)

- Presenter info: included
- Demo section: included, App tab has live `<iframe src="SERVICE_URL">`
- Tab 6 (Try It Yourself): included
- Use when: presenting live to a customer with the service running locally

**APP_CONTENT_HTML:**
```html
<div class="app-frame">
  <div class="app-chrome">
    <div class="app-url">http://localhost:PORT</div>
  </div>
  <div class="app-body" style="height:420px;padding:0;">
    <iframe src="http://localhost:PORT" style="width:100%;height:100%;border:none;"
            title="PROJECT NAME"></iframe>
  </div>
</div>
```

### 4b. overview

- Presenter info: removed entirely (the `.title-presenter` div is stripped from output)
- Demo section: not included (all three markers replaced with empty string)
- `document.getElementById('demo-wrapper'),` line also removed from views array JS
- Tab 6: not applicable
- Use when: generic "What is Akka?" deck with no specific POC

**Presenter removal:** Use regex to strip the div, not simple string replacement,
because the LinkedIn URL in the href would otherwise leave a broken anchor:
```python
output = re.sub(r'\s*<div class="title-presenter">.*?</div>\s*', '\n',
                output, flags=re.DOTALL)
# Then also remove the views array line:
output = output.replace("    document.getElementById('demo-wrapper'),\n", '')
```

### 4c. shareable

- Presenter info: included
- Demo section: included, App tab shows static product cards (no iframe)
- Tab 6 (Try It Yourself): included
- Use when: leaving behind a presentation the recipient will browse offline

**APP_CONTENT_HTML:** A 2×2 grid showing four products with representative social proof
messages for each strategy type (SCARCITY, TRENDING, VALIDATION, NONE). Uses inline
styles only — no CSS classes from demo.css needed for the cards themselves. Each card
shows: strategy label, product name, category, social proof message/banner, and stats.

The grid uses `display:grid; grid-template-columns:1fr 1fr; gap:12px` inside an
`.app-body` div styled with `height:420px; overflow:auto; background:#0A0A0A`.

### 4d. hands-on

- Presenter info: included
- Demo section: included, App tab shows step-by-step run guide
- Tab 6 (Try It Yourself): **removed** (redundant with App tab run guide)
- Use when: packaging for a recipient to clone and run themselves

**Tab 6 removal:** The demo.html template has explicit markers around Tab 6 elements:
```html
<!-- TAB6-NAV-START -->
<div class="nav-tab" data-tab="5">...</div>
<!-- TAB6-NAV-END -->
```
and:
```html
<!-- TAB6-PANEL-START -->
<div class="tab-panel" data-panel="5">...</div>
<!-- TAB6-PANEL-END -->
```

Remove them with:
```python
demo_html = re.sub(r'<!-- TAB6-NAV-START -->.*?<!-- TAB6-NAV-END -->',
                   '', demo_html, flags=re.DOTALL)
demo_html = re.sub(r'<!-- TAB6-PANEL-START -->.*?<!-- TAB6-PANEL-END -->',
                   '', demo_html, flags=re.DOTALL)
```

**NEVER** try to remove Tab 6 by matching the `<div class="nav-tab" data-tab="5">`
opening tag with a greedy or non-greedy dot-star regex. These divs have nested child
divs; `.*?</div>` matches the first inner div's closing tag, not the outer one. This
leaves broken partial HTML that destroys the content area layout (all tab content goes
blank).

**APP_CONTENT_HTML for hands-on:** A `.try-steps` div with 4 numbered steps:
1. Prerequisites (Java 21+, Maven 3.9+, Akka CLI install command)
2. Clone and build (git clone, cd, mvn compile)
3. Set LLM key and run (export key, akka local run, open URL)
4. Add products and trigger social proof (prose instructions)

---

## 5. Demo Section HTML Structure

The demo section must follow this exact wrapper pattern:

```html
<div id="demo-wrapper" style="height:200vh; position:relative;">
<div id="demo-section" style="position:sticky; top:0; height:100vh; overflow:hidden;">
<div class="showcase" style="display:flex; height:100%;">
  <nav class="nav">...</nav>
  <div class="content">
    <div class="tab-panel active" data-panel="0">...</div>
    <div class="tab-panel" data-panel="1">...</div>
    ...
  </div>
</div>
</div>
</div>
```

**Critical layout rules:**
- `demo-wrapper`: `height:200vh; position:relative` — provides the scroll anchor distance
- `demo-section`: `position:sticky; top:0` — NO offset for top nav (there is no top nav)
- `showcase`: `display:flex` — MUST be flex, not block; sidebar collapses otherwise
- `nav`: regular sidebar in flex flow — NOT floating, NOT fixed
- `content`: `position:relative; overflow:hidden; height:100vh` (from demo.css)
- `tab-panel`: `position:absolute; inset:0; opacity:0; pointer-events:none` for inactive;
  `opacity:1; pointer-events:auto` for `.active` (from demo.css)

Tab panels use `position:absolute; inset:0` to occupy the same space, with opacity
toggling visibility. This only works if `.content` has `position:relative`. If the
content div loses `position:relative`, all panels stack vertically and all content
shows at once.

**Do NOT:**
- Add a top navigation bar — it breaks all sticky sections in the presentation
- Use `position:fixed` or `position:floating` for the demo nav
- Use `display:none` / `display:block` for tab panel switching (opacity approach is
  intentional — allows CSS transitions)

---

## 6. Component Table

The component table (`{{COMPONENTS_TABLE_HTML}}`) is the inner HTML of:
```html
<div class="comp-table">
  {{COMPONENTS_TABLE_HTML}}
</div><!-- /comp-table -->
```

For the social-proofing-agent project, it is extracted from `preso/akka-sales-integrated.html`
using:
```python
m = re.search(r'<div class="comp-table">(.*?)</div><!-- /comp-table -->', integrated, re.DOTALL)
components_table_html = m.group(1).strip()
```

The closing `<!-- /comp-table -->` marker must exist in the source file for this to work.

**Component table structure:**
```html
<!-- Group header -->
<div class="comp-group-header">
  <span class="dot" style="background:COLOR"></span>
  <span class="comp-group-count">(N)</span>
  <span style="color:COLOR">Group Name</span>
</div>

<!-- Row (collapsed by default) -->
<div class="comp-row" data-comp="KEY">
  <span class="comp-row-dot" style="background:COLOR"></span>
  <span class="comp-row-name">Name</span>
  <span class="comp-row-type">Type</span>
  <span class="comp-row-desc">Short description</span>
</div>

<!-- Detail panel (hidden until row clicked) -->
<div class="comp-detail" data-detail="KEY">
  <div class="comp-detail-desc">Longer description.</div>
  <div class="comp-detail-code">
    <div class="comp-detail-code-bar">FileName.java</div>
    <div class="comp-detail-code-body">...syntax-highlighted HTML...</div>
  </div>
</div>
```

**comp-detail visibility:** Controlled by CSS `display:none` (default) and
`display:block` for `.comp-detail.open`. The JS in `demo.js` adds/removes the `open`
class on click. comp-detail elements are NEVER open by default. If they appear visible
on load, the CSS is not being applied.

**Chevron injection:** demo.js appends a `<span class="comp-row-chevron">▶</span>` to
each `.comp-row` at runtime. Do not hardcode chevrons in the HTML.

---

## 7. Sequence Diagram

The sequence diagram is rendered as SVG at runtime by code in `demo.js`. It reads from:
```javascript
window.DEMO_SEQUENCE_DATA
```

This variable is set by a `<script>` tag at the bottom of `demo.html`:
```html
<script>window.DEMO_SEQUENCE_DATA = {{SEQUENCE_DATA_JSON}};</script>
```

**Data format:**
```json
{
  "participants": [
    {"id": "string", "name": "Display\nName", "ext": true|false, "color": "#HEX"}
  ],
  "messages": [
    {"region": "Region Label", "color": "#HEX"},
    {"from": INDEX, "to": INDEX, "label": "message text", "dashed": true|false}
  ]
}
```

- `ext: true` → dashed border, gray color (external system)
- `ext: false` → solid border, component color
- `color` on participant: border and text color for internal components
- `region` entries create colored horizontal separator bands with labels
- `dashed: true` on messages → dashed arrow line (response); `false` → solid (request)
- `name` supports `\n` for two-line participant headers

**Rendering behavior:**
- Container width measured from `#seqDiagram` offsetWidth at render time
- Column width = `Math.floor(availW / N)` where N = participant count
- Minimum container width: 600px (falls back to 900px if narrower)
- Font: 11px headers, 10px message labels
- Lifelines: vertical dashed `#222` lines
- Arrows: solid or dashed horizontal `#555` lines with filled `#555` arrowheads
- Labels: centered on arrow with `#070707` background rect for readability
- Region bands: subtle horizontal rule at 20% opacity

---

## 8. Known Bugs and Fixes

### 8.1 s5 "Describe What You Want" right-column cards (base.html)

**Symptom:** When scrolling DOWN through the s5 section, the spec card and arch card on
the right column remain blank. When scrolling back UP from below, both cards appear
immediately.

**Root cause:** The forward animation path (`s5State === 'forward'`) reveals cards only
when the terminal animation reaches specific `fireTrigger` steps. Users scrolling
quickly pass through the section before those steps complete. The reverse path
(`s5State === 'reverse'`) fills both cards immediately via `fillTerminalFull()`.

**Fix (in base.html `checkS5()`):** Added scroll-progress-based card reveal for the
forward state, so fast scrollers see cards at the appropriate scroll position regardless
of animation state:
```javascript
if (s5State === 'forward' && anchored) {
  if (progress >= 0.35 && !specCard.classList.contains('show')) {
    specCard.classList.add('show');
    if (revealIdx < 1) revealIdx = 1;
  }
  if (progress >= 0.65 && !archCard.classList.contains('show')) {
    archCard.classList.add('show');
    if (revealIdx < 2) revealIdx = 2;
  }
}
```

### 8.2 Resilience iframe broken path

**Symptom:** The resilience section (`s6`) shows "page may have been moved" when the
output HTML is not in the same directory as the base template.

**Root cause:** `base.html` uses `src="resilience/resilience.html"` — a path relative to
`preso/`. When output goes to `samples/social-proofing-agent/`, the iframe needs to
traverse two levels up.

**Fix (in assembler, after all replacements):**
```python
output = output.replace(
    'src="resilience/resilience.html"',
    'src="../../preso/resilience/resilience.html"'
)
```

For outputs in other locations, adjust the prefix accordingly. A future improvement is
to make this a `{{RESILIENCE_PATH}}` placeholder in base.html.

### 8.3 Architecture tab showing raw text dump ("gibberish")

**Symptom:** After opening the presentation, the Architecture tab shows a wall of raw
text including the component table HTML, the repo URL, and the sequence JSON.

**Root cause:** The original `demo.html` had a comment block at the top documenting all
placeholders, including `{{COMPONENTS_TABLE_HTML}}`. After substitution, the component
table HTML (which contains `<!-- Design Views -->` and other HTML comments with `-->`)
was injected into the comment block. The first `-->` in the injected content closed the
outer HTML comment prematurely, causing everything after it — repo URL, JSON, etc. —
to render as visible text.

**Fix:** Removed the comment block from `demo.html` entirely. Placeholder documentation
lives in this spec document instead.

**Rule:** Never put `{{COMPONENTS_TABLE_HTML}}` (or any substitution that produces HTML
with comments) inside an HTML comment block.

### 8.4 Hands-on Tab 6 removal breaking layout

**Symptom:** After removing Tab 6 with a regex on the raw div tags, the demo section
renders with a blank content area. Tab 6 nav item partially remains (icon removed,
label text visible as unstyled text).

**Root cause:** The nav-tab and tab-panel divs have nested child divs. Matching
`<div class="nav-tab" data-tab="5">.*?</div>` with `re.DOTALL` stops at the first
inner `</div>` (the icon div's close), leaving broken partial HTML. The panel regex had
a similar problem and consumed too much, eating closing tags from the parent structure.

**Fix:** Added explicit HTML comment markers in demo.html around each Tab 6 element:
```html
<!-- TAB6-NAV-START -->
<div class="nav-tab" data-tab="5">...</div>
<!-- TAB6-NAV-END -->

<!-- TAB6-PANEL-START -->
<div class="tab-panel" data-panel="5">...</div>
<!-- TAB6-PANEL-END -->
```
Removal then uses safe marker-based regex:
```python
demo_html = re.sub(r'<!-- TAB6-NAV-START -->.*?<!-- TAB6-NAV-END -->',
                   '', demo_html, flags=re.DOTALL)
demo_html = re.sub(r'<!-- TAB6-PANEL-START -->.*?<!-- TAB6-PANEL-END -->',
                   '', demo_html, flags=re.DOTALL)
```

**Rule:** Never remove HTML elements with nested divs using dot-star regex against the
raw tag. Always use dedicated markers.

---

## 9. CSS Scoping Rules

All CSS in `demo.css` must be scoped under `#demo-section`:

```css
/* CORRECT */
#demo-section .comp-detail { display: none; }
#demo-section .nav { width: 180px; ... }

/* WRONG — leaks into main presentation */
.comp-detail { display: none; }
.nav { width: 180px; ... }
```

**Why:** The base presentation has its own classes. Unscoped selectors from demo.css
will override presentation styles silently. The sales presentation's design always wins
over demo styling in any conflict.

**Exception:** `#demo-section` itself and the wrapper divs (`#demo-wrapper`) are
top-level and do not need scoping.

---

## 10. JavaScript Architecture

`demo.js` is injected at `/* DEMO_JS_MARKER */` and runs after the full document is
parsed. It is wrapped in an IIFE. All selectors are scoped to `#demo-section`.

**Tab switching (two systems):**

1. Click handler on `.nav-tab` elements — sets `active` class on corresponding panel
2. Keyboard handler (`1`–`6` keys) — only fires when demo section is in viewport,
   determined by checking `demo-wrapper` bounding rect against `window.innerHeight * 0.5`

**Keyboard guard:**
```javascript
function isDemoActive() {
  var rect = demoWrapper.getBoundingClientRect();
  return rect.top < window.innerHeight * 0.5 && rect.bottom > window.innerHeight * 0.5;
}
```
This prevents number keys from switching demo tabs while the user is in a different
presentation section.

**Component row expand/collapse:**
- JS injects `<span class="comp-row-chevron">▶</span>` into each `.comp-row` at load
- Click on row: adds `expanded` class to row, `open` class to matching `.comp-detail`
- Clicking an already-open row closes it (toggle behavior)
- Only one row can be open at a time — clicking a new row closes the previous one

**SVG connector lines (component graph):**
- `drawDemoConnectors()` runs on load and is re-triggered by MutationObserver when
  any `.comp-detail` opens
- Measures `.dg-conn-tree` height, creates SVG with trunk line and branch arrows
- Uses `shape-rendering: crispEdges` for pixel-perfect 1px lines

**Sequence diagram:**
- Reads `window.DEMO_SEQUENCE_DATA` set by inline `<script>` in demo.html
- Measures `#seqDiagram` container width at render time
- Returns early if `!data` — graceful no-op if JSON was not injected

---

## 11. Component Type Color Codes

These colors are used consistently for component type indicators throughout the
component table (dot, row highlight) and component graph diagram:

| Type | Border/Dot color | Background fill |
|------|-----------------|-----------------|
| Event Sourced Entity | `#F5C518` (yellow) | `#1A1600` |
| Key-Value Entity | `#28C840` (green) | `#001A04` |
| Workflow | `#1E90FF` (blue) | `#00081A` |
| View | `#A855F7` (purple) | `#0D001A` |
| Consumer | `#F97316` (orange) | `#1A0A00` |
| Agent | `#7EC8E3` (teal) | `#001A1A` |
| Endpoint | `#fff` (white) | `#141414` |
| External | `#666` (gray, dashed) | `#1A1A1A` |
| Design View | `#4EC9B0` (teal-green) | — |
| Domain Object | `#82AAFF` (blue-gray) | — |

Flow color coding for connection groups:
- Ingestion: `#2196F3` (blue)
- Processing: `#FF9800` (amber)
- Delivery: `#4CAF50` (green)

---

## 12. Diagram Types in Architecture Tab

Five design views are shown in the component table Design Views group:

### User Journey
HTML structure with `.dg-journey-nodes` containing `.dg-journey-row` elements.
Each row has two `.dg-journey-node` spans (with phase class `dg-journey-p1/p2/p3`)
connected by a `.dg-journey-arrow` span. A legend shows P1/P2/P3 color coding.

Phase colors:
- P1 (core): `#2196F3`
- P2 (enhanced): `#FF9800`
- P3 (demo): `#4CAF50`

### Actor-Goal
HTML `<table class="dg-ag-table">` with columns: Actor, Goal, Components, External.
Static HTML table, no JS rendering.

### Entity Map
`.dg-entity-map` with `.dg-node` elements colored by component type, connected by
SVG arrows. Includes a note div with entity state description below.

### Component Graph
Layered `.dg-layer` divs (External, API Layer, Application Layer) each containing
`.dg-layer-nodes` with `.dg-node` elements. Between layers, `.dg-connections` divs
contain `.dg-conn-group` elements with `.dg-conn-tree` for SVG connector rendering.

The SVG lines are drawn dynamically by `drawDemoConnectors()` in demo.js.

### Sequence Diagram
Rendered entirely by JS into `<div id="seqDiagram">` from `window.DEMO_SEQUENCE_DATA`.
See §7 for data format and rendering behavior.

---

## 13. Skill Invocation Flow

When `/akka:demo` is invoked, Claude should follow these steps:

**Step 1: Determine project location**
- If argument is a GitHub URL: clone the repo
- If argument is a local path: verify `pom.xml` exists
- If no argument: use current working directory

**Step 2: Introspect the project**
- Find spec artifacts (`spec.md`, `plan-diagrams.md`, etc.) via `akka_sdd_list_specs`
- Glob all `*.java` files under `src/main/java/`
- Classify each by component type (entity/consumer/agent/view/endpoint/etc.)
- Extract representative code snippets with syntax highlighting
- Count totals: components, events, endpoints, LOC

**Step 3: Determine mode**
- From `--mode` flag or interactive prompt
- Default: `live`

**Step 4: Check environment (live mode only)**
- `akka_local_status` — if not running, the App tab shows "Start App" guide instead of iframe
- Do not call `akka_local_start` if status already shows `"started"`

**Step 5: Build APP_CONTENT_HTML for the mode**
- `live`: iframe to service URL (detect port from `akka_local_status`)
- `overview`: not needed
- `shareable`: static product cards representing the project's domain
- `hands-on`: step-by-step run guide with the project's repo URL and port

**Step 6: Generate SEQUENCE_DATA_JSON**
Extract from `plan-diagrams.md` sequence diagram source. Convert mermaid participant
and message syntax to the JSON format expected by demo.js (see §7).

**Step 7: Generate COMPONENTS_TABLE_HTML**
Build the full HTML structure (see §6) from the introspected component list.
Group by type. For each component, include a code detail panel with syntax-highlighted
source snippet.

**Step 8: Assemble output**
Follow the assembly order in §3 exactly. Apply all path fixes.

**Step 9: Write and report**
Write output file. Print location, size, and next steps.

---

## 14. Files Touched by This System

```
preso/
  DEMO-SPEC.md                  ← this document
  assemble-demo.py              ← one-shot assembler (social-proofing-agent hardcoded)
  akka-sales-integrated.html   ← reference: working integrated version (source of comp table)
  akka-sales-presentation.html ← original sales deck (base.html was derived from this)
  templates/
    base.html                   ← sales deck + 5 insertion markers
    demo.css                    ← all #demo-section CSS
    demo.js                     ← all demo section JS
    demo.html                   ← demo section HTML with {{PLACEHOLDER}} markers + TAB6 markers
  resilience/
    resilience.html             ← standalone resilience demo (iframe'd in s6)

samples/social-proofing-agent/
  demo-presentation.html        ← live mode output
  demo-presentation-overview.html
  demo-presentation-shareable.html
  demo-presentation-hands-on.html
```
