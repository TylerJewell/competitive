# `/akka:demo` Skill — Specification

## Overview

The `/akka:demo` skill is an Akka Specify plugin command that generates a **personalized, self-contained sales presentation** from any Akka project. It takes the base Akka sales presentation, introspects the current project, and produces a single HTML artifact where the demo is seamlessly integrated as a view within the presentation — not bolted on, but woven into the narrative.

The output is a single file (or ZIP with assets) that a salesperson can open in any browser, present full-screen, and walk a prospect through the complete Akka story culminating in a live, running demo of the prospect's specific use case.

---

## What the Skill Does

When a salesperson runs `/akka:demo` inside a project directory:

### Phase 1: Project Introspection
The skill scans the Akka project and extracts:

- **Project metadata** — service name, description (from `pom.xml` / `build.gradle` or spec.md)
- **Domain objects** — all record/class definitions in the domain package
- **Components** — complete inventory by type:
  - Event Sourced Entities (with event types and command handlers)
  - Key-Value Entities (with state types and command handlers)
  - Workflows (with step definitions)
  - Views (with query methods and source subscriptions)
  - Consumers (with event subscriptions and produce targets)
  - Endpoints (HTTP/gRPC routes)
  - Timed Actions (with schedules)
- **Design artifacts** — any mermaid files in the project:
  - `user-journey.mmd`
  - `actor-goal.mmd`
  - `entity-map.mmd`
  - `component-graph.mmd`
  - `*-sequence.mmd`
  - Any other `.mmd` files
- **Source code** — the actual generated source for each component (for the code viewer)
- **Spec summary** — from `spec.md` if present (use case description, requirements)
- **Build stats** — lines of code, component counts, event type counts

### Phase 2: Build & Launch
The skill orchestrates the local development environment:

1. Runs `/akka:build` — compiles the project, runs tests, starts the local runtime
2. Detects the HTTP port the service is running on (from `application.conf` dev-mode settings)
3. Identifies the frontend/UI entry point if one exists:
   - Checks for `src/main/resources/static/index.html`
   - Checks for a frontend dev server (React/Vue/Angular on a separate port)
   - Checks for any `@HttpEndpoint` that serves HTML
   - Falls back to the API endpoint list if no UI exists
4. Runs `/akka:reliability` — launches the resilience testing dashboard
5. Records all running URLs:
   - Service API base URL (e.g., `http://localhost:9000`)
   - UI URL if available (e.g., `http://localhost:9000/app` or `http://localhost:3000`)
   - Akka Console URL (`http://localhost:9889`)
   - Resilience dashboard URL (`http://localhost:9889/resilience`)

### Phase 3: Presentation Generation
The skill assembles the personalized presentation:

1. Takes the base `akka-sales-presentation.html` as the template
2. Injects a **top navigation bar** into the presentation (see Navigation section below)
3. Generates the **Demo Showcase view** with all tabs populated from introspection data
4. Embeds the running app's UI as an iframe in the "The App" tab
5. Renders all mermaid design views into styled SVGs (using the presentation's dark theme)
6. Generates syntax-highlighted code blocks for every component
7. Populates "The Brief" tab from `spec.md` content
8. Populates build stats (LOC, component counts, build time)
9. Writes the final HTML to `./demo-showcase.html` (or a specified output path)

---

## Presentation Navigation

### Top Navigation Bar

The base sales presentation currently uses scroll-based navigation with sticky sections. The `/akka:demo` output adds a **minimal top navigation bar** that provides direct access to any view:

```
+----------------------------------------------------------------------+
| AKKA   |  Story  |  Platform  |  Dev Zero  |  ★ Demo  |  Customers  |
+----------------------------------------------------------------------+
|                                                                      |
|                     [current view content]                           |
|                                                                      |
+----------------------------------------------------------------------+
```

**Design:**
- Fixed position at top, `height: 40px`
- Background: `rgba(0, 0, 0, 0.85)` with `backdrop-filter: blur(12px)`
- Only appears after scrolling past the title slide (hidden on title)
- Akka logo on the left (small, 20px height)
- View labels as horizontal tabs, spaced evenly
- Active view highlighted with yellow underline (`var(--yellow)`, 2px)
- The "Demo" tab has a subtle accent (star icon or yellow dot) to draw attention
- Clicking a tab smooth-scrolls to that section OR (for the demo) enters the demo view
- Auto-updates active state based on scroll position
- Fades out when entering the demo view (replaced by demo's own floating nav)

### View Labels (mapped to existing sections)

| Nav Label | Section | Notes |
|-----------|---------|-------|
| Story | Title + Hero + Social Proof | Opening narrative |
| Challenge | Complexity section | "Along came agentic AI" |
| Platform | Akka Platform section | "Akka is an Agentic AI Platform" |
| Dev Zero | Dev Zero demo | Terminal animation |
| **Demo** | **Demo Showcase** | **Generated from project** |
| Resilience | Resilience section | Chaos engineering |
| Governance | Governance section | Policy & compliance |
| Customers | Customer stories | Manulife, Tubi, etc. |
| Packages | Pricing tiers | Starter, Growth, Enterprise |
| Partners | Partner ecosystem | Deloitte, NTT, etc. |

The exact labels can be configured. The demo tab is always present when `/akka:demo` has generated output.

---

## Demo Showcase — Floating Left Nav

When the demo view is active, the hard left sidebar from the standalone prototype transforms into a **floating navigation** that matches the sales presentation's aesthetic:

### Design
- **Position:** Fixed, left side, vertically centered
- **Width:** Auto (minimal, icon + short label)
- **Background:** `rgba(10, 10, 10, 0.9)` with `backdrop-filter: blur(12px)`
- **Border:** `1px solid rgba(255, 255, 255, 0.06)`, `border-radius: 12px`
- **Shadow:** `0 8px 32px rgba(0, 0, 0, 0.4)`
- **Margin from edge:** `24px`
- **Behavior:**
  - Appears when entering the demo view
  - Collapses to icons-only by default on smaller screens
  - Expands to show labels on hover
  - Active tab has yellow left accent bar
  - Fades out when scrolling past the demo view

### Tab Items
Each tab is a small pill:
```
  ┌──────────────────┐
  │ 📄  The Brief    │  ← active (yellow left bar)
  │ 🖥  The App      │
  │ ⚙  Architecture │
  │ 🔲  Platform     │
  │ 🚀  Ship It      │
  │ ⌨  Try It       │
  └──────────────────┘
```

Icons are SVG (matching the current nav icons). Labels appear on hover or when expanded.

### Content Area
- The demo content occupies the full viewport (100vh, 100vw minus the floating nav)
- Tab content transitions use horizontal slide (same as standalone)
- Each tab's content is generated from the project introspection

---

## Architecture Tab — Auto-Generation

The Architecture tab is the most complex to generate. The skill must:

### Design Views (Mermaid Rendering)

For each `.mmd` file found in the project, the skill:

1. Reads the mermaid source
2. Renders it to SVG using a mermaid renderer configured with the presentation's dark theme:
   ```javascript
   mermaid.initialize({
     theme: 'dark',
     themeVariables: {
       primaryColor: '#F5C518',
       primaryTextColor: '#fff',
       primaryBorderColor: '#F5C518',
       lineColor: '#555',
       secondaryColor: '#141414',
       tertiaryColor: '#0A0A0A',
       background: '#0A0A0A',
       mainBkg: '#141414',
       nodeBorder: '#F5C518',
       fontFamily: 'Instrument Sans, sans-serif'
     }
   });
   ```
3. Embeds the rendered SVG directly in the HTML (no external dependency needed at presentation time)
4. The SVG is styled to fit the diagram frame with proper padding and centering

### Component Code Extraction

For each component discovered during introspection:

1. Read the source file
2. Extract the class/record definition
3. Apply syntax highlighting using the presentation's color classes:
   - `.kw` (keywords) — `#C792EA`
   - `.ty` (types) — `#FFCB6B`
   - `.st` (strings) — `#C3E88D`
   - `.cm` (comments) — `#546E7A`
   - `.an` (annotations) — `#F5C518`
   - `.fn` (functions) — `#82AAFF`
   - `.num` (numbers) — `#F78C6C`
4. Generate the `COMP_DATA` JavaScript object with all component entries
5. Generate the `DIAGRAM_DATA` JavaScript object with rendered SVG content

### Component List Generation

The left nav component list is auto-generated from the introspection data, grouped by type. The order is:

1. Design Views (from `.mmd` files)
2. Domain Objects (records/classes in domain package)
3. Event Sourced Entities
4. Key-Value Entities
5. Workflows
6. Views
7. Consumers
8. Endpoints
9. Timed Actions

Each item includes metadata (event count, step count, query type, etc.) extracted from the source.

---

## The App Tab — Live Embed

The "The App" tab embeds the running application:

### If a UI exists:
- Renders an `<iframe>` pointed at the detected UI URL
- The iframe has the browser chrome frame (dark dots, URL bar) from the standalone prototype
- A small banner below the iframe shows: "Live application running at {url}"
- A "Open in new tab" link for full interaction

### If no UI exists (API-only service):
- Shows the API endpoint list in a styled card layout
- Each endpoint is clickable and shows a pre-filled `curl` command
- A terminal-style panel shows example request/response pairs
- Links to the Akka Console at `localhost:9889` for visual exploration

---

## The Brief Tab — Auto-Population

If `spec.md` exists in the project:
- **Title:** Extracted from the first `#` heading
- **Description:** First paragraph after the heading
- **Requirements:** Extracted from any bullet list in the spec
- **Build time:** Measured during Phase 2 (actual compile + start time)

If no `spec.md` exists:
- **Title:** Derived from the Maven/Gradle artifact name
- **Description:** "A distributed system built with Akka Specify"
- **Requirements:** Auto-generated from the component inventory ("Event-driven order processing with 6 event types, 3 workflows, and 5 queryable views")

---

## Output Format

### Single HTML (default)
- All CSS, JS, SVGs, and component data inlined
- Images referenced from the base presentation are embedded as base64 or referenced from a CDN
- The file is self-contained and works offline
- Approximate size: 2-5 MB (depending on images)

### ZIP (with `--zip` flag)
- HTML file + images directory + assets
- Smaller HTML file since images are external
- Better for email/sharing

### Output location
- Default: `./demo-presentation.html` in the project root
- Configurable: `/akka:demo --output /path/to/output.html`

---

## Skill Interface

```
/akka:demo                          # Generate with defaults
/akka:demo --title "Order System"   # Override presentation title
/akka:demo --output ./my-demo.html  # Custom output path
/akka:demo --zip                    # Output as ZIP
/akka:demo --no-build               # Skip build (use already-running service)
/akka:demo --no-resilience          # Skip resilience setup
/akka:demo --port 9001              # Override service port detection
/akka:demo --ui-url http://...      # Override UI URL detection
```

### Prerequisites
- Akka project with at least one component
- Akka CLI installed (`akka` command available)
- Java/Maven or Gradle for build
- Docker (for local runtime)

### Error Handling
- If build fails: report error, offer to generate presentation without live embed
- If no components found: error with suggestion to run `/akka:specify` first
- If port conflict: suggest alternative port or use `--port` flag

---

## Integration Points

### With existing Akka Specify skills
- Uses `/akka:build` for compilation and local runtime management
- Uses `/akka:reliability` for resilience dashboard setup
- Reads design artifacts generated by `/akka:specify` and `/akka:plan`
- Can re-run `/akka:tasks` output as architecture documentation

### With the sales presentation
- The base presentation template is maintained in the `competitive` repo
- `/akka:demo` fetches the latest template from a known URL or uses a bundled version
- The generated output preserves all existing presentation sections
- The demo view is inserted at a configurable position (default: after Dev Zero, before Resilience)

### With CI/CD
- Can be run in CI to generate updated presentations on each commit
- `--no-build` mode for generating from pre-built artifacts
- Output can be deployed to a static hosting service for sharing

---

## Future Extensions

1. **Multi-demo support** — Multiple demo tabs for different use cases within one presentation
2. **Live metrics** — If the service is running, show real-time metrics in the presentation
3. **Recording mode** — Record a demo walkthrough as a video embedded in the presentation
4. **Audience customization** — `--audience technical|executive|developer` adjusts which tabs are shown and the depth of content
5. **A/B presentation** — Side-by-side comparison of two approaches (e.g., "without Akka" vs "with Akka")
6. **Export to PDF** — Generate a static PDF version for offline sharing (using the existing `render-pdf.mjs` tooling)
