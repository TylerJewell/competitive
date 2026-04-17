---
description: Generate a personalized demo presentation from an Akka project. Introspects the project, builds the app, and produces an interactive HTML sales presentation with the demo embedded.
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

You **MUST** consider the user input before proceeding (if not empty).
If the user provides a GitHub repo URL, clone it first, then run the demo generation from that directory.

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

This is the main output step. Generate a single HTML file by following the **integration recipe**.

#### 5a. Load the base presentation

Read the base sales presentation template. This is the `akka-sales-presentation.html` file which contains the full Akka story (title, hero, social proof, complexity, platform, dev zero, resilience, governance, customers, packages, partners, closing).

#### 5b. Generate the demo CSS

Take all CSS from the demo showcase template. Scope every selector under `#demo-section` to prevent bleed into the main presentation:

```css
#demo-section .showcase { display: flex; height: 100vh; position: relative; }
#demo-section .nav { width: 180px; flex-shrink: 0; /* ... */ }
#demo-section .content { flex: 1; min-width: 0; /* ... */ }
/* ... all other demo styles scoped ... */
```

Append this CSS at the end of the presentation's `<style>` block.

#### 5c. Generate the demo HTML

Build the demo section HTML with these tabs:

**Tab 1: The Brief**
- Title from spec.md first heading
- Description from spec.md first paragraph
- Requirements from spec.md bullet lists
- Stats: build time (measured or estimated), "1 engineer", LOC count

**Tab 2: The App**
- If service is running: embed iframe to the service URL
- If not running: show two buttons:
  - "Check Setup" — styled button that tells user to run `/akka:setup`
  - "Start App" — styled button that tells user to run `/akka:build`
  - Status indicator showing current state (not started / building / running / error)
- Stats bar: endpoint count, entity types, event types, agent count, view count, LOC

**Tab 3: The Architecture**
- Summary stats grid (component count, event types, endpoints, design views, LOC)
- Expandable component table with all components grouped by type
- Each row expands to show description + syntax-highlighted source code
- Design views show rendered diagrams:
  - User Journey: phase-priority flow nodes
  - Actor-Goal: styled table (Actor | Goal | Components | External)
  - Entity Map: entity relationship boxes with arrows
  - Component Graph: layered bands (External → API → Application) with SVG connector lines
  - Sequence Diagram: full SVG lifeline diagram with participants and colored regions

**Tab 4: The Platform** — same as template (multi-tenant, API control plane, SDLC, best practices)

**Tab 5: Ship It** — same as template (deploy options, certifications, cost comparison)

**Tab 6: Try It Yourself** — customized with the project's repo URL in step 3

#### 5d. Insert the demo HTML

Insert between the last presentation section (`</div>` after s9-wrapper) and `<section id="closing">`:

```html
<div id="demo-wrapper" style="height:200vh; position:relative;">
<div id="demo-section" style="position:sticky; top:0; height:100vh; overflow:hidden;">
<div class="showcase" style="display:flex; height:100%;">
  <!-- nav + content -->
</div>
</div>
</div>
```

**CRITICAL integration rules** (from integration-recipe.md):
- Wrapper height: `200vh` (one viewport of scroll anchor)
- Sticky top: `0` (NO top nav bar offset)
- Showcase: `display: flex` (NOT block — sidebar breaks otherwise)
- Nav: regular sidebar (NOT floating — floating overlaps content)
- Nav footer: `display: none` (saves vertical space)
- Nav tabs: compact padding (`10px 16px`) so all 6 fit in viewport
- Do NOT add a top navigation bar (breaks all sticky sections)

#### 5e. Generate the demo JS

Append to the presentation's `<script>` block:
1. Demo tab switching (scoped to `#demo-section`)
2. Component expandable row toggle with chevron injection
3. Sequence diagram SVG rendering (measures container width dynamically)
4. Component graph SVG connector line drawing with auto-measured source widths
5. MutationObserver to re-draw SVG when detail panels open
6. Install method tab switching (for Try It Yourself tab)
7. Demo keyboard handling (1-6 keys when demo is in viewport)

#### 5f. Update view-jump navigation

Add `document.getElementById('demo-wrapper')` to the `views` array, between `s9-wrapper` and `closing`.

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
