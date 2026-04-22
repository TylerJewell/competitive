# `/akka:demo` Skill — Specification

## Overview

The `/akka:demo` skill generates **personalized Akka sales presentations** tailored to four distinct personas. It can produce a generic company pitch, a sales leave-behind with simulated demos, a live SA presentation with an embedded running app, or a customer self-serve package with setup instructions.

The output is always a self-contained HTML file (or ZIP with assets) that works offline in any browser.

---

## Personas & Modes

### Mode: `generic` — Company Pitch Deck
**Persona:** Anyone at Akka giving the standard pitch
**Output:** The base sales presentation with no personalization
- No presenter name/title on title slide
- No demo section — just the core Akka story
- Rarely changes — maintained manually in the competitive repo
- Single HTML file, works offline

**Usage:**
```
/akka:demo --mode generic
```

### Mode: `leave-behind` — Sales Rep Leave-Behind
**Persona:** Sales rep sending the presentation to a prospect after a meeting
**Output:** Personalized presentation with a simulated demo
- Rep's name/title on the title slide
- Customer's name and logo on the demo section header
- Demo App tab shows **pre-captured screenshots or video** — not a live app
- Architecture tab populated from a reference project (or a real POC if available)
- Works completely offline — no localhost, no Akka Specify needed by the recipient
- 6 tabs: Brief, App (screenshots), Architecture, Platform, Ship It, Try It Yourself

**Usage:**
```
/akka:demo --mode leave-behind \
  --presenter "Jane Smith" \
  --presenter-title "Account Executive, Akka" \
  --customer "Manulife" \
  --customer-logo ./manulife-logo.png
```

**Optional:** Point at a real project for architecture data:
```
/akka:demo --mode leave-behind \
  --presenter "Jane Smith" \
  --customer "Manulife" \
  --project ./path/to/poc
```

### Mode: `live` (default) — SA Live Presentation
**Persona:** Solution architect presenting a live POC demo to a customer
**Output:** Presentation with live embedded app, self-hosted by the Akka service
- SA's name/title on the title slide
- Customer's name/logo on the demo section
- Demo App tab embeds an **iframe pointing to `http://localhost:PORT/`** — the app's `index.html`, served from the same Akka service's static-resources directory
- The presentation itself (`demo.html`) is written to the project's `src/main/resources/static-resources/` and served at `http://localhost:PORT/demo.html`
- Uses `/akka:build` to compile and start the service before generating
- Architecture tab introspected from the current project
- 6 tabs: Brief, App (live iframe), Architecture, Platform, Ship It, Try It Yourself

**Usage** (from inside the POC project directory):
```
/akka:demo \
  --presenter "Alex Klikic" \
  --presenter-title "Solutions Architect, Akka" \
  --customer "NTT Data"
```

### Mode: `customer` — Customer Self-Serve Package
**Persona:** Customer who received the presentation and wants to run the POC themselves
**Output:** Presentation with run-it-yourself instructions replacing the App tab
- SA's name/title remains (they gave the original presentation)
- Customer's name/logo remains
- App tab replaced with **"Run It Yourself"** — step-by-step guide to install tools, clone the repo, build, and launch
- No Try It Yourself tab (redundant with the run guide)
- No localhost dependencies — works offline
- 5 tabs: Brief, Run It Yourself, Architecture, Platform, Ship It

**Usage:**
```
/akka:demo --mode customer \
  --presenter "Alex Klikic" \
  --presenter-title "Solutions Architect, Akka" \
  --customer "NTT Data" \
  --repo https://github.com/akka/demo-social-proofing
```

---

## Interactive Mode

When invoked with **no arguments**, the skill walks the user through configuration interactively:

```
/akka:demo
```

The skill asks:

1. **"What type of presentation?"**
   - Generic pitch deck (no customization)
   - Sales leave-behind (for sending to prospects)
   - Live demo presentation (I'll present with a running app)
   - Customer self-serve (send to customer to run themselves)

2. **"Presenter name?"** (skipped for generic)
   - Default: git user name

3. **"Presenter title?"** (skipped for generic)
   - Default: blank

4. **"Customer name?"** (skipped for generic)
   - Required for leave-behind, live, customer modes

5. **"Customer logo?"** (optional)
   - Path to an image file

6. **"Project directory?"** (skipped for generic)
   - Default: current directory
   - For leave-behind without a project: uses bundled reference demo

7. **"Repository URL?"** (customer mode only)
   - The URL the customer will clone

---

## Help

When invoked with `help`:

```
/akka:demo help
```

The skill outputs:

```
/akka:demo — Generate personalized Akka sales presentations

MODES:
  --mode generic        Company pitch deck, no personalization
  --mode leave-behind   Sales leave-behind with simulated demo
  --mode live           Live presentation with running app (default)
  --mode customer       Customer self-serve with run guide

OPTIONS:
  --presenter NAME      Presenter name on title slide
  --presenter-title T   Presenter title (e.g. "Solutions Architect, Akka")
  --customer NAME       Customer name for demo section
  --customer-logo PATH  Path to customer logo image
  --project PATH        Path to Akka project (default: current directory)
  --repo URL            Git repo URL (for customer mode clone instructions)
  --output PATH         Output file path (default: ./demo-presentation.html)
  --port PORT           Override service port detection

EXAMPLES:
  /akka:demo                                    Interactive mode
  /akka:demo --mode generic                     Generic pitch deck
  /akka:demo --customer "Manulife"              Live demo for Manulife
  /akka:demo --mode leave-behind --customer X   Leave-behind for prospect X
  /akka:demo --mode customer --repo <url>       Customer self-serve package
```

---

## Parameters Reference

| Parameter | Required | Default | Modes | Description |
|-----------|----------|---------|-------|-------------|
| `--mode` | No | `live` | all | Presentation mode |
| `--presenter` | No | git user or blank | leave-behind, live, customer | Presenter name |
| `--presenter-title` | No | blank | leave-behind, live, customer | Presenter title |
| `--customer` | Yes* | — | leave-behind, live, customer | Customer/account name |
| `--customer-logo` | No | — | leave-behind, live, customer | Path to logo image |
| `--project` | No | cwd | leave-behind, live, customer | Path to Akka project |
| `--repo` | Yes** | — | customer | Git repo URL for clone instructions |
| `--output` | No | live: `{project}/src/main/resources/static-resources/demo.html`; other: `./demo-presentation.html` | all | Output file path |
| `--port` | No | auto-detect | live | Service port override |

\* Required for non-generic modes
\** Required for customer mode

---

## What the Skill Does

### Phase 1: Parse Arguments
Parse `$ARGUMENTS` for flags. If no arguments or missing required values, enter interactive mode and prompt the user.

### Phase 2: Project Introspection (skip for generic mode)
Scan the Akka project and extract:

- **Spec data** — title, description, requirements from `spec.md`
- **Design artifacts** — mermaid diagrams from `spec-diagrams.md` and `plan-diagrams.md`
- **Components** — full inventory by type:
  - Event Sourced Entities (with event types, command handlers)
  - Key-Value Entities (with state types)
  - Workflows (with step definitions)
  - Views (with query methods, subscriptions)
  - Consumers (with event subscriptions)
  - Agents (with system messages)
  - Endpoints (HTTP routes)
  - Timed Actions
  - Domain Objects (records, enums, sealed interfaces)
- **Source code** — representative 20-40 line snippets per component, syntax-highlighted
- **Totals** — component count, event types, API endpoints, LOC

### Phase 3: Detect Running Service (live mode only)
1. Use the **Build & Run App** handoff to compile and start the service — do not call Maven or Akka runtime tools manually
2. After the handoff, call `akka_local_status` to confirm the service is running and retrieve the port
3. Record `SERVICE_URL` (e.g. `http://localhost:9004`) and `STATIC_DIR` = `{PROJECT_DIR}/src/main/resources/static-resources/`
4. If build failed, continue anyway — App tab will show error and suggest `/akka:build`

### Phase 4: Generate Presentation

#### For `generic` mode:
- Copy base `akka-sales-presentation.html`
- Remove presenter name/title/LinkedIn from title slide
- Output the file

#### For `leave-behind`, `live`, `customer` modes:
Follow the **integration recipe** (see `integration-recipe.md`):

1. Start with base presentation HTML
2. Replace presenter info on title slide
3. Inject demo CSS (scoped under `#demo-section`)
4. Build demo section HTML with mode-appropriate tabs:
   - **leave-behind**: App tab = screenshot gallery
   - **live**: App tab = boot terminal + iframe with auto-detect
   - **customer**: App tab = "Run It Yourself" step-by-step guide
5. Insert demo HTML between partners section and closing slide
6. Inject demo JS (tab switching, expandable rows, SVG diagrams, boot terminal)
7. Add `demo-wrapper` to view-jump navigation array

**CRITICAL integration rules:**
- Wrapper: `height:200vh; position:relative`
- Sticky: `top:0; height:100vh`
- Showcase: `display:flex` (NOT block)
- Nav: regular sidebar 180px (NOT floating/fixed)
- Nav footer: hidden
- All CSS scoped under `#demo-section`
- No top navigation bar
- No browser chrome dots (terminal-style headers only)

### Phase 5: Write Output

**live mode** — write into the project's Akka static-resources directory so the running service can serve the files:
1. Write `demo.html` to `{PROJECT_DIR}/src/main/resources/static-resources/demo.html`
2. Copy plugin assets (`images/`, `logos/`, `resilience/`) into `static-resources/`
3. Call `akka_local_run_service` to restart the service — Akka reads static files from the compiled classpath (`target/classes/`), so a restart is required for the new files to take effect
4. Presentation is then accessible at `http://localhost:PORT/demo.html`; the app runs at `http://localhost:PORT/`

**All other modes**:
- Write HTML to `--output` path (default: `./demo-presentation.html`)
- Copy plugin assets alongside the output file
- For leave-behind/customer modes with images, create a zip with HTML + assets

### Phase 6: Report

```
Done.

  Mode            {mode}
  Presenter       {name}
  Customer        {customer}
  Components      {count} discovered
  Output          {path}

What's next:

  Presentation    http://localhost:{port}/demo.html   (live mode — served by Akka)
  Presentation    open {path}                         (other modes)
  Live App        http://localhost:{port}/            (live mode only)
  Console         http://localhost:9889               (live mode only)
  Resilience      /akka:reliability                   (live mode only)
  Deploy          /akka:deploy                        (live mode only)
```

---

## Tab Configuration by Mode

| Tab | generic | leave-behind | live | customer |
|-----|---------|-------------|------|----------|
| Brief | — | From spec.md | From spec.md | From spec.md |
| App | — | Screenshots/video | iframe → `http://localhost:PORT/` (app from same static-resources) | Run It Yourself guide |
| Architecture | — | Component explorer | Component explorer | Component explorer |
| Platform | — | Multi-tenant, API, SDLC, best practices | Same | Same |
| Ship It | — | Deploy options, certs, cost | Same | Same |
| Try It Yourself | — | Install + /akka:demo instructions | Same | — (removed) |
| **Total tabs** | **0** | **6** | **6** | **5** |

---

## Diagram Rendering Rules

When rendering mermaid diagrams to HTML, follow these rules:

1. **No mermaid.js dependency** — render to static HTML/CSS/SVG at generation time
2. **All connection lines are orthogonal** — right angles only, no curves, no diagonals
3. **Use SVG for connector lines** — `shape-rendering: crispEdges` for pixel-perfect 1px lines
4. **Component-type coloring**:
   - Event Sourced Entity: yellow `#F5C518` border, `#1A1600` fill
   - Key-Value Entity: green `#28C840` border, `#001A04` fill
   - Workflow: blue `#1E90FF` border, `#00081A` fill
   - View: purple `#A855F7` border, `#0D001A` fill
   - Consumer: orange `#F97316` border, `#1A0A00` fill
   - Agent: teal `#7EC8E3` border, `#001A1A` fill
   - Endpoint: white `#fff` border, `#141414` fill
   - External: gray `#666` dashed border, `#1A1A1A` fill
5. **Sequence diagram**: SVG with vertical dashed lifelines, horizontal arrows, colored region bands. Dynamically size columns to fill available width. Font sizes: 11px headers, 10px labels.
6. **Component graph**: Layered bands (External → API → Application). Connections grouped by source with SVG tree connectors. Auto-measure source name widths for alignment.
7. **Flow color coding**: Blue `#2196F3` = ingestion, Amber `#FF9800` = processing, Green `#4CAF50` = delivery.

---

## Key Design Rules

1. **Sales presentation design ALWAYS wins** in any conflict with demo styling.
2. **Scope all demo CSS** under `#demo-section` — no unscoped selectors.
3. **Never add a top navigation bar** — it breaks every sticky section.
4. **Never use floating/fixed nav** for the demo sidebar — use a regular flex sidebar.
5. **Terminal-style headers** — no red/yellow/green browser dots.
6. **The demo section must scroll-anchor** using wrapper+sticky pattern.
7. **Arrow keys** include demo-wrapper in the view-jump array.
8. **Number keys 1-6** only switch demo tabs when demo section is in viewport.
9. **Images** must be accessible from the output file location (symlink, copy, or embed as base64).

---

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No pom.xml found | Error: not an Akka project. Suggest `/akka:setup`. |
| No specs found | Use project name + component inventory as fallback for Brief tab. |
| No diagrams found | Skip Design Views in Architecture tab. Code viewer still works. |
| No Java files found | Error: cannot generate demo without components. |
| Build fails | Generate presentation anyway. App tab shows error + suggests `/akka:build`. |
| No service running (live mode) | App tab shows boot terminal with polling. |
| Customer logo file not found | Skip logo, warn user. |

---

## Template Source — Public Repo

Templates are not bundled with the plugin install. They live in a public GitHub repo so every `/akka:demo` invocation gets the latest slide content, copy, and design.

```
Repo:      https://github.com/tylerjewell/sales-presentation
Cache:     ~/.akka/sales-presentation/
```

On every run the plugin does:
1. `git clone` the repo if not already cached, or `git pull --ff-only` to update
2. Run `python3 CACHE_DIR/builder/build.py --mode overview` to assemble the current base deck into `~/.akka/sales-presentation/generated/_plugin/base.html`
3. Python 3 is required — if unavailable the plugin stops with an install prompt

No template files are committed to the plugin. The plugin directory contains only `demo.md` and `SPEC.md`.

**Template file paths (post-clone + build):**
```
~/.akka/sales-presentation/generated/_plugin/base.html   — assembled sales deck (markers intact)
~/.akka/sales-presentation/slides/12-demo/slide.css      — demo section CSS
~/.akka/sales-presentation/slides/12-demo/slide.html     — demo HTML with {{PLACEHOLDER}} markers
~/.akka/sales-presentation/slides/12-demo/slide.js       — tab switching, SVG diagrams, keyboard nav
```

## Output Size Expectations

| Mode | Approximate Lines | File Size |
|------|-------------------|-----------|
| generic | ~3,200 | ~200KB |
| leave-behind | ~5,200 | ~300KB + images |
| live | ~5,200 | ~300KB |
| customer | ~4,800 | ~280KB |
