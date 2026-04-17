---
description: Generate personalized Akka sales presentations. Supports 4 modes — generic pitch, sales leave-behind, live SA demo, customer self-serve. Run `/akka:demo help` for usage.
handoffs:
  - label: Check Setup
    agent: akka.setup
    prompt: Verify that this machine has all required tools (Java, Maven, Akka CLI) for running the demo.
    send: true
  - label: Build & Run App
    agent: akka.build
    prompt: Build and run the service locally so we can embed it in the demo presentation.
    send: true
  - label: Run Resilience Tests
    agent: akka.reliability
    prompt: Start resilience testing against the running service.
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding.

### Help Mode

If `$ARGUMENTS` is `help` or `--help`, print this usage guide and stop:

```
/akka:demo — Generate interactive Akka presentations

MODES:
  --mode overview       Standard Akka platform presentation
  --mode shareable      Offline-ready presentation with project showcase
  --mode live           Presentation with embedded running app (default)
  --mode hands-on       Presentation with setup guide for the recipient to run it

OPTIONS:
  --presenter NAME      Your name on the title slide
  --presenter-title T   Your title
  --for NAME            Who this presentation is for
  --logo PATH           Their logo image
  --project PATH        Path to Akka project (default: current directory)
  --repo URL            Git repo URL (for hands-on mode)
  --output PATH         Output file (default: ./demo-presentation.html)
  --port PORT           Override service port detection

EXAMPLES:
  /akka:demo                                    Interactive setup
  /akka:demo --mode overview                    Standard platform presentation
  /akka:demo --for "NTT Data"                   Live demo for NTT Data
  /akka:demo --mode shareable --for "Manulife"  Shareable with screenshots
  /akka:demo --mode hands-on --repo <url>       Hands-on package
```

### Interactive Mode

If `$ARGUMENTS` is empty or missing required values, prompt the user interactively:

First, briefly explain what `/akka:demo` does:

> This skill generates an interactive presentation showcasing Akka and (optionally) a specific project you've built. You can personalize it, include a live app, or package it for someone else to explore — without the live app — on their own.

Then ask:

1. **"What kind of presentation do you need?"**
   - **Overview** — "What is Akka?" presentation, no project-specific content → `--mode overview`
   - **Shareable** — A presentation with a project showcase someone can browse offline (screenshots, architecture, code) → `--mode leave-behind`
   - **Live** — A presentation with your running app embedded for a live walkthrough → `--mode live`
   - **Hands-on** — A presentation packaged for the recipient to clone the project and run it themselves → `--mode customer`

2. **"Your name?"** (skip for overview) — default: git user name
3. **"Your title?"** (skip for overview) — default: blank
4. **"Who are you presenting to?"** (skip for overview) — the person or team receiving the presentation
5. **"Recipient's logo?"** (optional) — path to an image file
6. **"Project directory?"** (skip for overview) — default: current directory
7. **"Repository URL?"** (hands-on mode only) — the repo the recipient will clone

After collecting all answers, show a confirmation summary before generating:

```
Ready to generate:

  Mode        Live
  Presenter   Alex Klikic, Solutions Architect, Akka
  For         NTT Data
  Project     ./samples/social-proofing-agent
  Output      ./demo-presentation.html

Generate? [Y/n]
```

If the user confirms (or presses Enter), proceed. If they say no, cancel and let them re-run with different options.

### Argument Parsing

If `$ARGUMENTS` contains flags, parse them:
- `--mode VALUE` — one of: overview, shareable, live, hands-on
- `--presenter VALUE` — your name
- `--presenter-title VALUE` — your title
- `--for VALUE` — who this presentation is for
- `--logo VALUE` — path to their logo image
- `--project VALUE` — path to Akka project directory
- `--repo VALUE` — git repo URL (hands-on mode)
- `--output VALUE` — output file path
- `--port VALUE` — service port override

A bare path argument (no flag) is treated as `--project`.
A bare URL argument (starts with http) is treated as `--repo` and implies cloning.

**Legacy flag aliases** (for backward compatibility):
- `--customer` → `--for`
- `--customer-logo` → `--logo`
- `generic` → `overview`
- `leave-behind` → `shareable`
- `customer` → `hands-on`

## Purpose

The `/akka:demo` command generates a **personalized, interactive sales presentation** from any Akka project. It introspects the project's components, design artifacts, and source code, then produces a single HTML file that combines the Akka sales presentation with an embedded demo showcase.

The output is a self-contained HTML file that a salesperson can open in any browser and present full-screen — the complete Akka story ending with a live, interactive exploration of the customer's specific POC.

## Outline

1. **Locate project** — find or clone the Akka project
2. **Introspect** — scan all components, design artifacts, and source code
3. **Check environment** — verify Java/Maven/Akka CLI are available (run setup if needed)
4. **Build & start** — compile and run the service locally
5. **Generate presentation** — assemble the HTML from templates + introspected data
6. **Report** — show the user what was generated and how to present it

## Detailed Steps

### Step 1: Locate the Project

If the user provides a **GitHub URL** as `$ARGUMENTS`:
1. Create a working directory if needed
2. Clone the repo: `git clone <url> .` (or into a subdirectory)
3. `cd` into the cloned directory

If the user provides a **local path**:
1. Verify the path exists and contains a `pom.xml` or `build.gradle`

If **no arguments**:
1. Use the current working directory
2. Verify it's an Akka project (has `pom.xml` with akka-sdk dependency)

### Step 2: Introspect the Project

Scan the project to build a complete component inventory:

#### 2a. Find spec and design artifacts

Call `akka_sdd_list_specs` to find features. For each feature, read:
- `spec.md` — extract title, description, requirements
- `spec-diagrams.md` — extract mermaid diagram sources (User Journey, Actor-Goal, Entity Map)
- `plan-diagrams.md` — extract mermaid diagram sources (Component Graph, Sequence Diagram)
- `plan.md` — extract component design decisions

#### 2b. Scan Java source files

Use Glob to find all `*.java` files under `src/main/java/`. For each file:

1. Read the file content
2. Classify the component type by looking for:
   - `extends EventSourcedEntity` → Event Sourced Entity
   - `extends KeyValueEntity` → Key-Value Entity
   - `extends Workflow` → Workflow
   - `extends View` → View
   - `extends Consumer` → Consumer
   - `extends Agent` → Agent
   - `@HttpEndpoint` → HTTP Endpoint
   - `extends TimedAction` → Timed Action
   - `record` or `enum` or `sealed interface` in domain package → Domain Object

3. Extract key metadata:
   - Class name
   - `@Component(id = "...")` or `@ComponentId("...")` value
   - For entities: event types (from sealed interface), command handler methods
   - For views: `@Query` methods, `@Consume.From*` subscriptions
   - For consumers: `@Consume.From*` subscriptions
   - For agents: system message, response type
   - For endpoints: `@Get`, `@Post`, `@Put` routes

4. Extract a **representative code snippet** (20-40 lines) showing the most interesting part:
   - For entities: the event types + one command handler + one event handler
   - For agents: the system message + generateMessage method signature
   - For consumers: the onEvent method
   - For views: the record type + query methods
   - For endpoints: the route methods
   - For domain objects: the full record/enum definition

5. Apply syntax highlighting using these CSS classes in `<span>` tags:
   - `.kw` — keywords (public, class, record, return, var, if, new, etc.)
   - `.ty` — types (String, Effect, ProductState, etc.)
   - `.st` — string literals
   - `.cm` — comments
   - `.an` — annotations (@Component, @CommandHandler, etc.)
   - `.fn` — method names
   - `.num` — numeric literals

#### 2c. Count totals

Calculate:
- Total components (excluding domain objects from count)
- Event types count
- API endpoints count (sum of all @Get/@Post/@Put/@Delete methods)
- Design views count (from mermaid diagrams found)
- Lines of code (sum of all Java file line counts)

### Step 3: Check Environment

Call `akka_local_status` to check if the runtime is already running.

If not running, inform the user that `/akka:setup` should be run to verify the environment. The generated presentation will include "Check Setup" and "Start App" buttons in the App tab that trigger these skills.

### Step 4: Build & Start (Optional)

If the environment is ready:
1. Run `akka_maven_compile` to compile
2. If successful, run `akka_local_start` (if not already running)
3. Run `akka_local_run_service` to start the service
4. Use `akka_local_status` to find the service URL and port
5. Record the URL for embedding in the App tab

If the user doesn't want to build now, the presentation is still generated — the App tab shows "Start App" button instead of a live iframe.

### Step 5: Generate the Presentation HTML

This is the main output step. Assemble a single HTML file from the template files in `preso/templates/`. Do **not** synthesize CSS, JS, or structural HTML from scratch — read the templates and substitute placeholders.

#### 5a. Load the base template

Read `preso/templates/base.html`. This is the full sales presentation with these markers already in place:
- `{{PRESENTER_NAME}}` / `{{PRESENTER_TITLE}}` / `{{PRESENTER_LINKEDIN}}` — title slide
- `<!-- DEMO_CSS_MARKER -->` — just before `</style>`
- `<!-- DEMO_HTML_MARKER -->` — between s9-wrapper and `<section id="closing">`
- `document.getElementById('demo-wrapper'),` — already in the views array
- `/* DEMO_JS_MARKER */` — just before `</script>`

#### 5b. Substitute presenter info

Replace in the loaded HTML:
- `{{PRESENTER_NAME}}` → presenter name (from `--presenter` or git user)
- `{{PRESENTER_TITLE}}` → presenter title (from `--presenter-title` or blank)
- `{{PRESENTER_LINKEDIN}}` → LinkedIn URL if known, else `#`

For **overview mode**: remove the entire `.title-presenter` div (no presenter on generic deck).

#### 5c. Build the demo section substitutions

Read `preso/templates/demo.html`. Replace these placeholders with project-specific content from the introspection in Step 2:

| Placeholder | Source |
|-------------|--------|
| `{{DEMO_TITLE}}` | Project name HTML, e.g. `Social Proofing <span class="accent">Agent</span>` |
| `{{DEMO_DESCRIPTION}}` | spec.md first paragraph, or project name + component summary |
| `{{REQUIREMENTS_HTML}}` | `<li>` items from spec.md bullet lists |
| `{{BUILD_TIME}}` | Measured build time, or estimate (e.g. `"35m"`) |
| `{{LOC}}` | Total Java line count (formatted with comma) |
| `{{APP_HEADLINE}}` | Mode-specific headline HTML |
| `{{APP_DESCRIPTION}}` | Mode-specific one-sentence description |
| `{{APP_CONTENT_HTML}}` | Mode-specific app frame (see below) |
| `{{APP_STATS_HTML}}` | `.app-stat` divs: endpoints, entities, events, agents, views, LOC |
| `{{ARCH_SUMMARY_HTML}}` | Six `.arch-summary-stat` divs: components, events, endpoints, design views, agents, LOC |
| `{{COMPONENTS_TABLE_HTML}}` | Full component table HTML (groups + rows + details with syntax-highlighted code) |
| `{{REPO_URL}}` | Git repo URL for Try It Yourself step 3 |
| `{{SEQUENCE_DATA_JSON}}` | JSON `{participants:[...], messages:[...]}` from plan-diagrams.md sequence data |

**`{{APP_CONTENT_HTML}}` by mode:**
- **live**: `<div class="app-frame">` with iframe to `{{SERVICE_URL}}` if running, or boot terminal with polling if not
- **shareable**: `<div class="app-frame">` with screenshot gallery placeholder
- **hands-on**: Run It Yourself step-by-step guide replacing the app frame entirely
- **overview**: Tab 2 is omitted

#### 5d. Assemble the output HTML

1. Replace `<!-- DEMO_CSS_MARKER -->` with the full contents of `preso/templates/demo.css`
2. Replace `<!-- DEMO_HTML_MARKER -->` with the substituted `demo.html` content
3. Replace `/* DEMO_JS_MARKER */` with the full contents of `preso/templates/demo.js`

The views array already contains `demo-wrapper` — no further JS changes needed.

#### 5e. Mode-specific tab adjustments

- **overview**: No demo section at all — skip steps 5c/5d entirely. Output is just `base.html` with presenter info substituted.
- **hands-on**: Remove Tab 6 (Try It Yourself) from the nav and panels — it's redundant with the run guide in Tab 2.
- **shareable** / **live**: All 6 tabs included as-is.

### Step 6: Write Output and Report

Write the generated HTML to `./demo-presentation.html` in the project root (or the path specified by the user).

Report to the user:

```
Done.

What's next:

  Presentation    open demo-presentation.html
  Live App        http://localhost:{port}
  Console         http://localhost:9889
  Resilience      /akka:reliability
  Deploy          /akka:deploy
```

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

## Key Rules

1. **The sales presentation's design ALWAYS wins** in any conflict with demo styling.
2. **Scope all demo CSS** under `#demo-section` — no unscoped selectors.
3. **Never add a top navigation bar** — it breaks every sticky section in the presentation.
4. **Never use floating/fixed nav** for the demo sidebar — use a regular flex sidebar.
5. **Terminal-style headers** — no red/yellow/green browser dots anywhere.
6. **The demo section must scroll-anchor** — uses the same wrapper+sticky pattern as every other presentation section.
7. **Arrow key navigation must include** the demo-wrapper in the views array.
8. **Number keys 1-6** should only switch demo tabs when the demo section is in the viewport.

## Customization Variables

The skill should accept these optional parameters (via `$ARGUMENTS` or interactive prompts):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--title` | From spec.md | Presentation demo title |
| `--presenter` | "Tyler Jewell" | Presenter name on title slide |
| `--presenter-title` | "CEO, Akka" | Presenter title |
| `--output` | ./demo-presentation.html | Output file path |
| `--no-build` | false | Skip build step |
| `--port` | auto-detect | Service port override |

## Error Handling

- **No pom.xml found**: Tell the user this doesn't appear to be an Akka project. Suggest running `/akka:setup` first.
- **No specs found**: Generate the presentation without the Brief tab's spec content. Use project name and component inventory as fallback.
- **No diagrams found**: Skip the Design Views section in the Architecture tab. Component code viewer still works.
- **Build fails**: Generate the presentation anyway. The App tab shows the error and suggests `/akka:build` to fix.
- **No Java files found**: Error — cannot generate a demo without components.
