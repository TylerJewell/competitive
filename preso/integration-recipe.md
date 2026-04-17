# Demo Integration Recipe

Exact steps to integrate a demo showcase into the Akka sales presentation. Derived from manual testing — documents what works and what doesn't.

## What Worked

The demo section uses the **same layout pattern as the standalone demo** — a flex container with a sidebar nav and content area. No floating nav, no position:fixed tricks, no special overrides. The presentation's existing sticky wrapper pattern handles anchoring.

## What Failed (Don't Do These)

1. **Floating nav overlay** — `position: fixed` nav with `backdrop-filter: blur`. The nav overlaps content, padding calculations break, and the content gets squeezed into a narrow column. The standalone sidebar layout works; don't fight it.

2. **Top nav bar** — A `position: fixed` bar across the top breaks every sticky section in the presentation. All sections use `position: sticky; top: 0` and a top nav at 36px pushes content behind it. Would require changing `top: 0` to `top: 36px` on ~12 sticky elements and recalculating all wrapper heights. Not worth it without a full rework.

3. **CSS variable conflicts** — The demo uses `--nav-width`, `--green`, `--blue`, etc. that don't exist in the presentation's `:root`. Either define them or use literal values. Scope everything under `#demo-section`.

4. **`display: block` on `.showcase`** — Breaks the sidebar+content flex layout. Must be `display: flex`.

5. **Measuring text widths on hidden elements** — The sequence diagram JS measures container width, but if the detail panel is hidden (`display: none`) when the script runs, it gets 0. Use a MutationObserver or re-render on panel open.

## Integration Steps

### Step 1: Prepare the CSS

Extract ALL CSS from the demo HTML file. Prefix every selector with `#demo-section` to prevent bleed:

```
#demo-section .showcase { ... }
#demo-section .nav { ... }
#demo-section .tab-panel { ... }
```

**Critical rules that must be present:**

```css
/* Layout — must be flex, not block */
#demo-section .showcase {
  display: flex;
  height: 100vh;
  position: relative;
}

/* Sidebar — use a real sidebar, not floating */
#demo-section .nav {
  width: 180px;
  flex-shrink: 0;
  background: #0A0A0A;
  border-right: 1px solid #1C1C1C;
  display: flex;
  flex-direction: column;
  padding: 16px 0 12px;
  position: relative;
  z-index: 10;
  overflow: hidden;
}

/* Content fills remaining space */
#demo-section .content {
  flex: 1; min-width: 0;
  position: relative;
  overflow: hidden;
  height: 100vh;
}

/* Hide nav footer in integrated mode */
#demo-section .nav-footer { display: none; }
```

**Nav tab compactness** (must fit 6 tabs in 100vh):
```css
#demo-section .nav-tab {
  padding: 10px 16px;
  gap: 10px;
}
#demo-section .nav-logo svg { height: 18px; }
```

Append the demo CSS at the end of the presentation's `<style>` block, before `</style>`.

### Step 2: Insert the HTML

Insert between the last content section and `<section id="closing">`:

```html
<!-- Demo Section -->
<div id="demo-wrapper" style="height:200vh; position:relative;">
<div id="demo-section" style="position:sticky; top:0; height:100vh; overflow:hidden;">
<div class="showcase" style="display:flex; height:100%;">
  <!-- Paste the <nav class="nav"> and <div class="content"> from the demo file -->
  <!-- Keep all tab panels, component data, diagrams, etc. -->
</div>
</div>
</div>
```

**Key values:**
- Wrapper height: `200vh` (gives one viewport of scroll anchor — enough for presenter to navigate tabs)
- Sticky top: `0` (no top nav bar to offset)
- Sticky height: `100vh` (fills the viewport)
- Showcase display: `flex` (sidebar + content side by side)

### Step 3: Insert the JavaScript

Append ALL demo JS at the end of the presentation's `<script>` block, before `</script>`. Must include:

1. **Demo tab switching** — scope selectors to `#demo-section .nav-tab` and `#demo-section .tab-panel`
2. **Component expandable row toggle** — scope to `#demo-section .comp-row`
3. **Chevron injection** — append chevrons to rows via JS
4. **Sequence diagram SVG rendering** — targets `#demo-section #seqDiagram`
5. **Component graph SVG connector lines** — for `#demo-section .dg-conn-tree`
6. **MutationObserver for re-rendering** — re-draw SVG lines when detail panels open
7. **Source column width measurement** — for `#demo-section .dg-conn-from`
8. **Install method tab switching** — for the Try It Yourself tab

**Do NOT include:**
- Top nav bar JS
- Floating nav visibility toggle JS
- Any JS that adds `position: fixed` elements

### Step 4: Update view-jump navigation

Add `document.getElementById('demo-wrapper')` to the `views` array in the existing view-jump navigation script. Insert it before `'closing'`:

```javascript
const views = [
  // ... existing views ...
  document.getElementById('s9-wrapper'),
  document.getElementById('demo-wrapper'),  // <-- add this
  document.getElementById('closing')
].filter(Boolean);
```

### Step 5: Handle keyboard conflicts

The demo uses number keys 1-6 to switch tabs. The presentation uses ArrowRight/ArrowLeft to jump views. These must coexist:

- Number keys 1-6 should only activate when the demo section is in the viewport
- ArrowRight/ArrowLeft continue to work for view jumping (including jumping into/out of the demo)
- Use `getBoundingClientRect()` on `#demo-wrapper` to check if in view before handling number keys

## Customization Variables

For personalized presentations, replace these values:

| Variable | Location | Example |
|----------|----------|---------|
| Presenter name | `<section id="title">` .title-presenter a | Tyler Jewell |
| Presenter title | `.title-presenter-title` | CEO, Akka |
| LinkedIn URL | `.title-presenter a[href]` | linkedin.com/in/... |
| Demo repo URL | Try It Yourself tab, step 3 | github.com/akka/demo-... |
| Demo title | Tab 1 headline | Social Proofing Agent |
| Demo description | Tab 1 .tab-desc | An e-commerce retailer... |
| Demo stats | Tab 1 .brief-bar | 35m, 1 engineer, 1,800 LOC |
| Component data | COMP_DATA JS object | All source code blocks |
| Diagram data | Inline HTML in design view details | Component graph, sequence, etc. |

## File Size Expectations

| Component | Lines |
|-----------|-------|
| Base presentation | ~3,200 |
| Demo CSS (scoped) | ~400 |
| Demo HTML | ~800 |
| Demo JS | ~700 |
| **Total** | ~5,100 |

## Testing Checklist

After integration, verify:

- [ ] All original presentation sections render correctly (scroll through entire presentation)
- [ ] Arrow left/right jumps between views including demo
- [ ] Demo section anchors (sticks) when scrolling through its wrapper
- [ ] Demo sidebar shows all 6 tabs, all fit within viewport height
- [ ] Each demo tab switches correctly (click + number keys 1-6)
- [ ] Architecture tab: expandable rows work, chevrons rotate
- [ ] Architecture tab: component graph SVG lines render correctly
- [ ] Architecture tab: sequence diagram renders full-width with readable fonts
- [ ] Scrolling past the demo reaches the closing slide
- [ ] No CSS bleed from demo styles into presentation sections
- [ ] No JS errors in console
