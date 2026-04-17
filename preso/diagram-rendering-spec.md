# Diagram Rendering Specification

## Purpose

This spec defines how Akka Specify design diagrams (mermaid source) are rendered as styled HTML/SVG within the demo showcase. The goal is consistent, readable, on-brand rendering across any project — replacing mermaid's default output with hand-crafted visuals that match the Akka sales presentation aesthetic.

Mermaid's default rendering produces inconsistent sizing, ugly curved arrows, garish colors, and poor readability on dark backgrounds. We bypass mermaid rendering entirely and instead **parse the mermaid source** and render using our own HTML/CSS or SVG system.

---

## Design Principles

1. **All connection lines are orthogonal** — right angles only, no diagonals, no curves
2. **Dark theme** — black/dark gray backgrounds, white text, yellow accents
3. **Compressed width** — diagrams must fit within the available panel width (~700-900px) without horizontal scrolling
4. **Vertical scroll OK** — diagrams can extend vertically; the container scrolls
5. **Consistent spacing** — uniform gaps between nodes, uniform padding within nodes
6. **Readable at glance** — node labels must be legible at 12-13px; connection labels at 10-11px
7. **Component-type coloring** — colors match the demo showcase's component type palette

---

## Color Palette

### Node fills (by component/actor type)

| Type | Fill | Border | Text |
|------|------|--------|------|
| Event Sourced Entity | `#1A1600` | `#F5C518` | `#fff` |
| Key-Value Entity | `#001A04` | `#28C840` | `#fff` |
| Workflow | `#00081A` | `#1E90FF` | `#fff` |
| View | `#0D001A` | `#A855F7` | `#fff` |
| Consumer | `#1A0A00` | `#F97316` | `#fff` |
| Agent | `#001A1A` | `#7EC8E3` | `#fff` |
| Endpoint / API | `#141414` | `#fff` | `#fff` |
| Domain Object | `#0A0A1A` | `#82AAFF` | `#fff` |
| External / Out of Scope | `#1A1A1A` | `#666` (dashed) | `#999` |
| Actor (human) | `#1A1600` | `#F5C518` | `#000` |
| Primary feature (P1) | `#1A1600` | `#F5C518` | `#fff` |
| Secondary feature (P2) | `#141414` | `#333` | `#fff` |
| Tertiary feature (P3) | `#1A1A1A` | `#555` | `#fff` |

### Connection lines

| Type | Color | Style |
|------|-------|-------|
| Command / direct call | `#F5C518` | solid, 1.5px |
| Event stream | `#A855F7` | dashed `6 4`, 1px |
| External / async | `#666` | dashed `4 4`, 1px |
| Data flow (default) | `#555` | solid, 1px |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Node label | Instrument Sans | 12px | 600 | (per type) |
| Node sublabel / type | Instrument Sans | 9px | 600 | (type color, uppercase) |
| Connection label | Instrument Sans | 10px | 500 | `#888` |
| Subgraph title | Instrument Sans | 10px | 700 | `#F5C518`, uppercase, `letter-spacing: 2px` |
| Step numbers on arrows | SF Mono | 10px | 700 | `#F5C518` |

---

## Diagram Types

### 1. User Journey (flowchart TD — top-down)

**Source pattern:** `flowchart TD` with nodes representing features/phases, connected by dependency arrows.

**Rendering approach:** Vertical flow, one column or two columns if width allows.

**Layout:**
```
┌─────────────────────────────────────────────┐
│  USER JOURNEY                               │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────┐                       │
│  │  P1: Ingest      │                       │
│  │  View Counts     │──────┐                │
│  └──────────────────┘      │                │
│           │                │                │
│           ▼                ▼                │
│  ┌──────────────────┐  ┌─────────────────┐  │
│  │  P1: View Social │  │ P2: AI Strategy │  │
│  │  Proof           │  │ Selection       │  │
│  └──────────────────┘  └─────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

**Node style:**
- Rounded rectangle: `border-radius: 8px`
- Padding: `10px 16px`
- Min-width: `160px`
- Max-width: `220px`
- Color based on phase priority (P1=yellow, P2=dark, P3=gray)

**Connections:**
- Orthogonal lines only
- Arrows: small filled triangle, 6px
- Labels on connection lines centered on the horizontal/vertical segment
- When a line needs to route around nodes, use L-shaped or Z-shaped paths

---

### 2. Actor-Goal (flowchart LR — left-to-right)

**Source pattern:** `flowchart LR` with subgraphs for actors, system goals, and external systems.

**Rendering approach:** Three-column table layout.

**Layout:**
```
┌──────────────┬────────────────────────────┬──────────────────┐
│   ACTORS     │    SYSTEM GOALS            │   EXTERNAL       │
├──────────────┼────────────────────────────┼──────────────────┤
│              │                            │                  │
│ ┌──────────┐ │ ┌────────────────────────┐ │ ┌──────────────┐ │
│ │ Customer │─┼─│ See social proof       │ │ │ Analytics    │ │
│ └──────────┘ │ ├────────────────────────┤ │ │ Platform     │ │
│              │ │ Ingest view counts     │─┼─│ (out of      │ │
│ ┌──────────┐ │ ├────────────────────────┤ │ │  scope)      │ │
│ │ Demo     │─┼─│ AI selects strategy    │ │ └──────────────┘ │
│ │ Presenter│ │ ├────────────────────────┤ │                  │
│ └──────────┘ │ │ Browse product grid    │ │ ┌──────────────┐ │
│              │ ├────────────────────────┤ │ │ LLM Provider │ │
│              │ │ Populate with traffic  │ │ │ (out of      │ │
│              │ └────────────────────────┘ │ │  scope)      │ │
│              │                            │ └──────────────┘ │
└──────────────┴────────────────────────────┴──────────────────┘
```

**Alternative (table-based):** For cleaner rendering, actor-goal can be a styled table:

| Actor | Goal | System Component | External Dependency |
|-------|------|-----------------|---------------------|
| Customer | See social proof on product page | ProductEntity → SocialProofEndpoint | — |
| Demo Presenter | Browse product grid with live updates | SocialProofView → DemoUIEndpoint | — |
| Demo Presenter | Populate demo with synthetic traffic | IngestionEndpoint → ProductEntity | — |
| (System) | AI selects strategy and generates copy | SocialProofAgent | LLM Provider |
| (Analytics) | Send view counts | IngestionEndpoint → ProductEntity | Analytics Platform |

Use the table approach when there are more than 5 actor-goal pairs.

---

### 3. Entity Map (flowchart TD — simple)

**Source pattern:** `flowchart TD` with 2-6 entity nodes and relationship arrows.

**Rendering approach:** Compact horizontal or vertical layout depending on count.

**Layout (≤4 entities):** Horizontal row
```
┌──────────┐     ┌───────────────────┐     ┌──────────────────┐
│ Product  │────▶│ Social Proof Msg  │     │ Demo Catalog     │
│          │     │                   │     │                  │
│ ESE      │     │ value object      │     │ KVE              │
└──────────┘     └───────────────────┘     └──────────────────┘
       ▲                                          │
       └──────────────────────────────────────────┘
                   "defines"
```

**Layout (>4 entities):** Two-row grid or vertical list

**Node style:**
- Top section: entity name (bold, 14px)
- Bottom section: component type label (9px, uppercase, type color)
- Border color matches component type
- Relationship labels on connection lines

---

### 4. Component Graph (flowchart TD — complex)

**Source pattern:** `flowchart TD` with subgraphs (External, API Layer, Application Layer) and numbered step arrows.

**Rendering approach:** Layered horizontal bands, top to bottom.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  EXTERNAL                                                    │
│  ┌─────────┐   ┌──────────────┐   ┌─────────┐              │
│  │ Gatling  │   │ LLM Provider │   │ Browser │              │
│  └────┬─────┘   └──────────────┘   └────┬────┘              │
├───────┼─────────────────────────────────┼────────────────────┤
│  API LAYER                              │                    │
│  ┌────▼──────┐ ┌────────────┐ ┌────────▼───┐ ┌───────────┐ │
│  │ Product   │ │ Ingestion  │ │ SocialProof│ │ DemoUI    │ │
│  │ Endpoint  │ │ Endpoint   │ │ Endpoint   │ │ Endpoint  │ │
│  └────┬──────┘ └─────┬──────┘ └─────┬──────┘ └───────────┘ │
├───────┼──────────────┼──────────────┼────────────────────────┤
│  APPLICATION LAYER   │              │                        │
│  ┌────▼──────────────▼───┐   ┌─────▼──────┐                │
│  │   ProductEntity       │   │ SocialProof │                │
│  │   (Event Sourced)     │◄──│ Consumer    │                │
│  └───────┬───────────────┘   └──────┬──────┘                │
│          │                          │                        │
│  ┌───────▼───────┐   ┌─────────────▼──────┐                │
│  │ SocialProof   │   │ SocialProof        │                │
│  │ View          │   │ Agent              │                │
│  └───────────────┘   └────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

**Subgraph bands:**
- Full width, separated by `1px solid #1C1C1C` horizontal lines
- Subgraph label: top-left, yellow uppercase, 10px
- Background: slightly different shade per layer (`#0A0A0A`, `#0D0D0D`, `#080808`)

**Numbered steps:**
- Arrow labels show step numbers: `①`, `②`, etc.
- Number in yellow circle (10px) centered on the connection line
- If too many steps, show in a legend below the diagram instead

---

### 5. Sequence Diagram

**Source pattern:** `sequenceDiagram` with participants, messages, and `rect` regions.

**Rendering approach:** Custom HTML table-like layout with vertical participant lifelines and horizontal message arrows.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Signal Ingestion                                (yellow)    │
│                                                              │
│  Gatling ──────POST /ingestion──────▶ IngestionEP           │
│                                           │                  │
│                              recordViews  │                  │
│                                           ▼                  │
│                                      ProductEntity           │
│                                           │                  │
│                              viewCount:247│                  │
│                                           ▼                  │
│                                      IngestionEP             │
├──────────────────────────────────────────────────────────────┤
│  Aggregation + Agent                        (gray)           │
│                                                              │
│  ProductEntity ──events──▶ Consumer                          │
│                                │                             │
│                   generateMsg  │                             │
│                                ▼                             │
│                           Agent ──prompt──▶ LLM              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  Cached Read                                (green)          │
│                                                              │
│  Browser ──GET──▶ SocialProofEP ──read──▶ ProductEntity     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Participant headers:**
- Fixed at top of the diagram area
- Each participant is a box: `background: #141414`, `border: 1px solid #333`, `border-radius: 6px`
- Participant name: 11px, bold
- Below each header: a thin vertical dashed line (`1px dashed #222`) running the full height

**Messages:**
- Horizontal arrows between lifelines
- Solid arrow for synchronous calls
- Dashed arrow for async/responses
- Label centered above the arrow line
- Arrow head: small filled triangle

**Rect regions:**
- Full-width colored band behind message groups
- Very subtle fill: `rgba(color, 0.06)` with left border `3px solid color`
- Region label in top-left: 10px, bold, region color

---

## Rendering Implementation

### Approach: HTML/CSS (not SVG)

Use HTML `div` elements with CSS for layout rather than SVG. Reasons:
- Easier text wrapping and sizing
- CSS grid/flexbox handles layout naturally
- Scrolling works out of the box
- Responsive to container width changes
- Easier to maintain and template

### Node HTML Template
```html
<div class="dg-node dg-type-ese">
  <div class="dg-node-type">Event Sourced Entity</div>
  <div class="dg-node-name">ProductEntity</div>
</div>
```

### Connection HTML Template
Connections are drawn using positioned `div` elements with borders:
```html
<div class="dg-conn dg-conn-v" style="left:150px; top:60px; height:40px;">
  <div class="dg-conn-arrow"></div>
</div>
<div class="dg-conn dg-conn-h" style="left:150px; top:100px; width:200px;">
  <div class="dg-conn-label">events</div>
</div>
```

### CSS Classes
```css
.dg-node {
  background: var(--fill);
  border: 1.5px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 14px;
  min-width: 140px;
  max-width: 220px;
  text-align: center;
}
.dg-node-type {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 600;
  color: var(--border-color);
  margin-bottom: 2px;
}
.dg-node-name {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}
.dg-conn-v {
  position: absolute;
  width: 1.5px;
  background: var(--line-color);
}
.dg-conn-h {
  position: absolute;
  height: 1.5px;
  background: var(--line-color);
}
.dg-conn-label {
  font-size: 10px;
  color: #888;
  position: absolute;
  white-space: nowrap;
}
```

### Subgraph / Layer Band
```css
.dg-layer {
  border-bottom: 1px solid #1C1C1C;
  padding: 16px 20px;
  position: relative;
}
.dg-layer-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700;
  color: #F5C518;
  margin-bottom: 12px;
}
```

---

## Mermaid-to-HTML Parser Requirements

The `/akka:demo` skill must include a parser that:

1. **Reads mermaid source** — extracts nodes, edges, subgraphs, styles, participants, messages
2. **Classifies diagram type** — flowchart TD, flowchart LR, sequenceDiagram
3. **Maps node styles to component types** — using the `style` declarations and `fill` colors to determine type (ESE, KVE, View, etc.)
4. **Computes layout** — positions nodes in a grid based on connections and subgraph membership
5. **Generates HTML** — outputs the diagram as styled HTML divs (not SVG, not mermaid rendering)
6. **Handles edge cases:**
   - Nodes with long labels: truncate with ellipsis or wrap to two lines
   - Many connections from one node: fan out vertically
   - Subgraph nesting: flatten to layer bands
   - Bidirectional connections: two parallel lines with small offset

### Layout Algorithm (simplified)

1. **Topological sort** — order nodes by dependency
2. **Layer assignment** — assign each node to a row (respecting subgraph boundaries)
3. **Column assignment** — distribute nodes across columns within each row, minimizing edge crossings
4. **Edge routing** — for each edge, compute an orthogonal path (vertical down from source, horizontal to target column, vertical down to target)
5. **Render** — output HTML with absolute positioning within a relative container

---

## Integration with Demo Showcase

Each rendered diagram replaces the placeholder content in the Architecture tab's Design Views section. When a user clicks a design view item in the component list:

1. The `DIAGRAM_DATA` entry for that view contains the pre-rendered HTML string
2. The `archDiagramBody` container receives the HTML via `innerHTML`
3. The diagram container scrolls vertically if the content exceeds viewport height
4. No external JavaScript dependencies are needed at presentation time (all rendering is done at generation time by the skill)
