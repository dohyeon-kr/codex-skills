---
name: css-judgment
description: Use when modifying CSS — adjusting padding/margin/gap/width/height/position/z-index/overflow, hover/focus/responsive states, or directly using primitive tokens (raw spacing, raw colors). Guides the judgment of CSS work rather than the syntax. Determines sizing ownership (outer layout vs inner content), preserves the box model, enforces token hierarchy, and catches observable anti-patterns: child margin for sibling spacing, intentionless `flex:1` or `width:100%`, raw px / one-off token combinations, gradient hex composition at call sites, `margin: auto` for large-area distribution. For image assets (faces, photos, composite illustrations) trigger image-asset-strategy first; for post-work visual comparison trigger visual-reference-compare.
---

# CSS Judgment Skill

CSS is not a combination of properties but a design of **responsibility, language, and scope**.
Work with intent, not pixels.

Three lenses:
1. **Layout responsibility** — who owns sizing, spacing, alignment
2. **Design language** — does this follow the system's meaning units
3. **Blast radius** — how far does this change reach

Phase split:
- Pre-work asset decisions → **image-asset-strategy** skill
- CSS judgment during work → this skill
- Post-work reference comparison → **visual-reference-compare** skill

---

## 1. Pre-edit Self-questions

If any answer is "I don't know," stop and **read** the code before writing.

### Pre-flight: image-asset-strategy gate (must pass before CSS work)

If the task started from a **design reference image / mockup / Figma URL** and that reference contains any photographic or composite visual asset — human face, model figure, product photo, hero shot, editorial visual, 3D-rendered cluster, illustration, brand mark, **or a custom-styled icon set** — **stop and run `image-asset-strategy` first**. Do not begin writing layout / styling code, and especially do not type `<svg>` for any of those slots, before the asset catalog has been produced and the routing decision is made.

The default routing decision for assets is **delegate to Codex via `/codex:rescue`** (Codex owns `imagegen`). Placeholders are a fallback that must carry an explicit reason in the final report. Don't pre-emptively reach for the placeholder while you're still in the CSS skill.

If you find yourself already drawing a face with `<circle>` + `<path>`, or mocking a product photo with stacked SVG shapes, or replicating a custom icon style by hand — that's a sign this gate was skipped. Stop, revert that draft, and run `image-asset-strategy` now.

### Sizing ownership (first CSS question)

Who decides this element's size?

- **Outer-layout-driven** (cards, grid cells, nav, screen areas) — content fits the container. Pattern: parent `padding` + `display: flex/grid`, children `flex: 1` or `grid 1fr`. Children that should be square use `aspect-ratio: 1`. **Do not pin fixed px on the children.**
- **Inner-content-driven** (button labels, chips, text) — content size determines it. Children use `fit-content`; parent only aligns via `gap`.
- **Scroll/carousel item** — when the parent is a horizontal/vertical scroller and children appear N-at-a-time in the viewport, an **intentional fixed size + `flex-shrink: 0`** is correct. Still keep the fixed value in a semantic token (`--size-card-product`) rather than raw px scattered in components.

Failing to make this decision leads to bugs like "fixed 48px child collides with container distribution and erases padding."

### Layout context

- This element: `block` / `flex item` / `grid item` / `absolute`?
- External spacing ownership: parent `gap` (default) vs child `margin` (only clear exceptions like overlap)
- Introducing `overflow` / `z-index` / `position`? State the intent in one sentence.
- **Fill properties** (`flex: 1`, `width: 100%`, `height: 100%`) — have you confirmed the parent's `flex-direction`? In a column parent, `flex: 1` expands vertically.
- **`margin-*: auto`** to push a child? Fine for small-area push. Large-area distribution (e.g., pushing a footer to the bottom) belongs in the parent via `justify-content: space-between` or `grid-template-rows: auto 1fr auto` — the child should not carry layout decisions.

### Design language

- Can the value (color, spacing, size) be expressed via a **semantic token**? If not, via a **component variant**?
- **Gradients / multi-stop color compositions** are part of the design language too. Do not compose `linear-gradient(155deg, #ff9a4f 0%, #ff7a1a 55%, #e85a06 100%)` at the call site each time — give gradients semantic tokens (`--surface-card-citrus-gradient`) or trap them inside variant CSS.
- Neither works? That's a signal the system lacks expressive vocabulary. Don't apply CSS; **propose a contract** instead.

### Blast radius

- Have you considered every call site this change touches?
- Are you modifying common components or layout primitives?

(Visual comparison belongs in the post-work **visual-reference-compare** skill.)

---

## 2. Core Principles

1. **Parent owns spacing** — sibling gaps via parent `gap`. Child margin is allowed only for **named exceptions**: (a) overlap (stacked avatars with `margin-left: -10px`), (b) fine push with `margin: auto` (small alignment nudge — large-area distribution stays in the parent), (c) **bleed pattern** — `margin: 0 calc(var(--space-md) * -1)` on a horizontal-scroll row to break the parent's padding and run edge-to-edge. Anything else is a smell.
2. **Token hierarchy** — `Component variant > Semantic token > Primitive token`. Direct primitive use means proposing a new semantic.
   - Beyond spacing/color/radius, **width/height/offset px** for intended widget intrinsic sizes (touch target, icon size) should default to semantic tokens (`--size-touch-min`, `--size-icon-md`). Clear exceptions like 1px borders or -1px overlaps are fine.
   - **Gradients / multi-stop colors** belong in tokens or variant CSS — no composition at call sites.
3. **State intent when changing layout properties** — `display` / `position` / `overflow` / `z-index` only when you can name the intent in one sentence.
4. **Fill properties are a patch signal** — find the real cause before stamping `width: 100%`, `flex: 1`, or `height: 100%`. The #1 cause of flex items refusing to shrink is a missing `min-width: 0`.
5. **Preserve the box model** — declared `padding` / `border` / `margin` must remain. When child total size exceeds container inner width, padding gets visually consumed. Don't shrink children to fit; **redesign with relative distribution** (flex:1 / grid 1fr).
6. **Don't fake photographic assets or custom-styled icons with raw SVG** — faces/photos/composite illustrations/custom icon families drawn from circles and paths become awkward placeholders. Asset decisions go to **image-asset-strategy**, whose default route is **delegate to Codex via `/codex:rescue`** (Codex owns the `imagegen` pipeline). Only canonical trivial UI glyphs (search, home, menu, chevron, well-known social logos) stay as inline SVG.
7. **Report system-level problems** — repeated patterns, missing semantics, one-context-only components: don't keep stamping CSS, propose a token/variant/contract addition.
8. **CSS unit hierarchy** — `rem` for text and UI density, `px` for visual crispness, `%`/`vw`/`vh`/`fr` for layout proportions, `em` for spacing that should scale with the component's own font size. Don't unify everything in rem or everything in px.
   - **rem**: `font-size`, `line-height`, `padding`, `margin`, `gap`, `border-radius`. Respects users who change the browser default font size (accessibility).
   - **px**: `border-width`, hairlines, icon stroke, sub-pixel alignment, 1px overlaps.
   - **%, vw/vh, fr**: layout proportions (grid `1fr 1fr`, viewport-based `100vh`, etc.).
   - **em**: spacing that should follow the component's own `font-size` (e.g., button horizontal padding scaling with label text).

---

## 3. Anti-patterns (stop on sight)

- ❌ **Faking a photographic asset or custom icon with raw SVG primitives** — `<svg>` `<circle>` `<rect>` `<path>` arrangements to stand in for a **human face / model figure / product photo / hero image / editorial moodshot / 3D object cluster / illustration / brand mark / custom-styled icon set**. Route to `image-asset-strategy` → Codex via `/codex:rescue`. This anti-pattern is the most frequent cause of session restarts in UI work; do not even draft "a quick SVG version for now."
- ❌ Child `margin-bottom` / `margin-right` for sibling spacing (`margin: auto` for fine push and **bleed pattern** — `margin: 0 calc(var(--space-md) * -1)` to break parent padding for a full-bleed row — are the named exceptions; large-area distribution still belongs in the parent)
- ❌ Arbitrary px (`padding: 7px`, `width: 250px`, `top: -22px`) — raw px scattered without semantic tokens
- ❌ One-off primitive token combinations (`var(--space-3) var(--space-5)`)
- ❌ Multi-stop gradient hex composition at the call site (`linear-gradient(155deg, #ff9a4f 0%, #ff7a1a 55%, #e85a06 100%)`)
- ❌ Intentionless `flex: 1` — stamping it without checking parent `flex-direction`
- ❌ Fixed-size children + `space-around`/`space-between` + `flex-shrink: 0` → container overflow → padding erased
- ❌ `width: 100%` / `height: 100%` patching a layout problem
- ❌ `gap` + `justify-content: space-around` simultaneously (distribution conflict)
- ❌ `margin: auto` for large-area distribution (footer-to-bottom push) — use parent `justify-content` or `grid-template-rows`
- ❌ Raw `z-index` numbers, intentionless `overflow: hidden`, `!important`
- ❌ Changing `display` / `position` on shared components
- ❌ Bypassing a semantic token with a primitive
- ❌ Unifying text/UI density in px (rem territory) or 1px hairlines in rem (px territory)
- ❌ **Grid item without `min-width: 0`** when an inner child can be wider than the track (long text, `<pre>` code block, image, mono-spaced URL). The grid track refuses to shrink → the whole grid overflows the viewport, cropping the right edge silently. Same root cause as Example 5 (flex), but the symptom is "section is wider than viewport" instead of "child won't shrink."
- ❌ **`align-items: stretch` (default) + sibling-with-shorter-content** in grid/flex → the shorter card stretches to the taller sibling and grows an awkward empty band of background. Either let the shorter card keep its intrinsic height (`align-self: start`) or rebalance content so both sides are visually full.
- ❌ **Choosing the responsive breakpoint by the wrong child** — a 2-col grid where one child is a long code block needs a wider breakpoint than a 2-col grid where both children are short text. A single "all 2-col layouts collapse at 900px" rule will leave the heavier layout broken between 900 and ~1024px. Decide per-layout, not per-skill.
- ❌ **Forgetting to reset browser-default `<ol>` / `<ul>` styling** when using them as design containers — `<ol>` ships with `padding-inline-start: ~40px` + numeric markers, `<ul>` ships with `padding-inline-start: ~40px` + disc markers. If you're treating the list as a flex/grid card stack (markers replaced by your own indices, alignment owned by the parent), you must reset: `margin: 0; padding: 0; list-style: none;`. Symptom: card stack pushed inward by ~40px on the leading edge, no apparent rule to point at — because it's a UA default, not your stylesheet.
- ❌ **Flex column scroll-container with content overflow → siblings get squashed** — a scroll container declared as `display: flex; flex-direction: column; overflow: auto` will let the default `flex-shrink: 1` collapse short-but-important children (a hero, a sticky header) down to their min-content height once the total content exceeds the container. The hero looks fine in dev when content is short, then "disappears" (collapses to 36px) once you add the rest of the page. Fix: mark every non-scrolling child with `flex-shrink: 0`, or switch the container to `display: block` + `min-height` if scroll is the only reason flex was chosen.
- ❌ **Sticky element without an explicit `z-index`** — `position: sticky` does **not** create a stacking context that floats above siblings by default. Once a later section (a banner, a modal-like card, a toast) introduces its own stacking context or its own positioned children, the sticky nav silently slides under them. Always pair `position: sticky` with `z-index: <value above any sibling stacking context>`.
- ❌ **Introducing a sticky / fixed bar without reserving content padding for it** — adding a sticky bottom nav of height 64px without adding `padding-bottom: 64px` (or its safe-area equivalent) to the scroll content means the **last screenful of content sits under the nav and is permanently hidden**. The bug rarely shows up in dev because designers always scroll to the top. Same trap with sticky top headers and the first viewport.

---

## 4. Examples

### Example 1 — Misjudged sizing ownership

A card holds three icon buttons. Children pinned at `width: 44px; flex-shrink: 0`, parent at `padding: 16px; space-around; gap: 12px`. The card's inner width (141px) is smaller than children+gap (156px) → children overflow right → **right padding visually becomes 0**.

**Bad**
```css
.card { padding: 16px; display: flex; justify-content: space-around; gap: 12px; }
.iconButton { width: 44px; height: 44px; flex-shrink: 0; }
```

**Good** (box model preserved; children fit the container)
```css
.card { padding: 12px; display: flex; align-items: center; gap: 4px; }
.iconButton { flex: 1; aspect-ratio: 1; /* parent decides size */ }
```

Judgment: "Card design is the anchor" → outer layout owns sizing → children get `flex: 1` + `aspect-ratio: 1`, not fixed px.

### Example 2 — `margin: auto` for large-area distribution

**Bad**
```css
.screen { display: flex; flex-direction: column; }
.navHolder { margin-top: auto; } /* child carries the layout decision */
```

**Good**
```css
.screen { display: grid; grid-template-rows: auto 1fr auto; }
/* or display: flex + justify-content: space-between */
```

Judgment: Pinning the footer to the bottom is a layout decision → express it in the parent.

### Example 3 — List item gap (parent gap)

**Bad**
```tsx
<Item style={{ marginBottom: 12 }} />
<Item style={{ marginBottom: 12 }} />
<Item /> {/* :last-child cleanup — patch-on-patch */}
```

**Good**
```tsx
<List gap="md"><Item /><Item /><Item /></List>
```

### Example 4 — Composing a gradient at the call site

**Bad**
```css
.card[data-surface='citrus'] {
  background: linear-gradient(155deg, #ff9a4f 0%, #ff7a1a 55%, #e85a06 100%);
}
.card[data-surface='mango'] {
  background: linear-gradient(155deg, #fcd35e 0%, #f7b32b 55%, #d88d11 100%);
}
```

**Good**
```css
:root {
  --surface-card-citrus: linear-gradient(155deg, #ff9a4f 0%, #ff7a1a 55%, #e85a06 100%);
  --surface-card-mango:  linear-gradient(155deg, #fcd35e 0%, #f7b32b 55%, #d88d11 100%);
}
.card[data-surface='citrus'] { background: var(--surface-card-citrus); }
.card[data-surface='mango']  { background: var(--surface-card-mango); }
```

Judgment: Gradients are part of the design language. Reserve the chance to reuse the same tone elsewhere; keep it tokenized.

### Example 5 — flex / grid item refusing to shrink

Default `min-width: auto` on flex and grid items lets the item demand the intrinsic width of its widest descendant. A long URL, a `<pre>` block, an `<input>`, a mono-spaced API path — any one of them can pin the item open, forcing the whole layout wider than the viewport.

**Bad** (flex symptom)
```css
.child { width: 100%; }       /* symptom patch */
.parent { overflow: hidden; }  /* hides it by clipping */
```

**Bad** (grid symptom — same root cause)
```css
.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.layout > .code-column pre { /* long code block */ }
/* → section overflows viewport on smaller screens; right edge cropped */
```

**Good** (both)
```css
.layout > * { min-width: 0; }
```

The fix is one line. The detection is the hard part — **right edge cropped or horizontal scroll appearing at unexpected widths is the symptom; check grid/flex children for `min-width: 0` first**, before reaching for `overflow-x: hidden` (which only hides the bug).

### Example 8 — Grid stretch + short sibling = empty band

A hero is `display: grid; grid-template-columns: 1.2fr 1fr; align-items: stretch` (the default). The left column has a long headline + paragraph + buttons. The right column is a small quote card with three lines. Stretch makes the card grow to match the left column → an awkward empty background band appears below the quote.

**Bad**
```css
.hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  /* align-items: stretch is the default — card stretches and gains empty space */
}
```

**Good — option A** (let the smaller card keep its intrinsic height)
```css
.hero { display: grid; grid-template-columns: 1.2fr 1fr; align-items: start; }
.heroCard { align-self: start; } /* explicit, even if redundant with align-items */
```

**Good — option B** (rebalance: push the card's footnote to the bottom so the empty space becomes a deliberate gap)
```css
.heroCard { display: flex; flex-direction: column; }
.heroCardFootnote { margin-top: auto; }
```

**Good — option C** (the empty space is real because the right card is too thin — add a second piece of content there: a signature, a related link, a date stamp). Layout choices are content choices.

Judgment rule: when one child of an `align-items: stretch` parent is consistently shorter, ask *"is the gap because of layout default or because the content is genuinely missing?"* before patching.

### Example 10 — Flex column scroll-container squashing a child

A mobile-shaped page uses an inner scroll container for the hero / list / banners. Initial dev shows a tall hero. Add more sections; reload. The hero is now 36px tall — **squashed** — because:

**Bad**
```css
.scroll {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  height: 100%;
}
/* hero, list, banner are all flex items with the default flex-shrink: 1 */
```

Once total content height > container height, every flex item gets pro-rata shrunk. The hero, which has no `flex-shrink: 0`, collapses first.

**Good**
```css
.scroll {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  height: 100%;
}
.hero, .stickyHeader { flex-shrink: 0; }  /* must keep intrinsic height */
.list { /* this one is the one that should shrink/grow */ }
```

Or, if scroll was the only reason for flex:

```css
.scroll { display: block; overflow-y: auto; height: 100%; }
```

Judgment rule: **a scroll container made of `display: flex; flex-direction: column` opts every child into mutual shrinking** — make the opt-out explicit on every child that must hold its own height.

### Example 11 — Sticky bar without z-index / without content reserve

A bottom nav: `position: sticky; bottom: 0;`. Looks fine on a calm page. Later a `NEW` promo banner with its own `transform` or `position: relative` is added mid-page. Now scrolling brings the banner *over* the nav — the banner has an implicit stacking context that beats the unspecified `z-index: auto` of the nav.

**Bad**
```css
.bottomNav { position: sticky; bottom: 0; }
.promoBanner { transform: translateZ(0); /* or any positioned child */ }
```

**Good — two fixes, both needed**
```css
.bottomNav {
  position: sticky;
  bottom: 0;
  z-index: 20;        /* above any sibling stacking context */
}
.scrollContent {
  padding-bottom: calc(64px + env(safe-area-inset-bottom));
  /* reserve the nav's height so the last section isn't trapped under it */
}
```

Judgment rule: every `position: sticky` / `position: fixed` introduces **two** debts — declare `z-index`, and reserve space at the opposite edge so content isn't permanently hidden.

### Example 9 — Per-layout breakpoint, not per-skill breakpoint

A landing page has four `display: grid` 2-column layouts: hero (1.2fr 1fr, both short), risk matrix (1fr 1fr, both short cards), skill structure (1.05fr 1fr, **one column is a long code block**), conclusion (1fr 1fr, both short). Defining one `@media (max-width: 900px) { all-of-them: 1fr }` looks tidy but leaves skill-structure broken between 900px and ~1024px — the code column overflows because it cannot shrink below its intrinsic content width.

**Bad** (one breakpoint for all)
```css
@media (max-width: 900px) {
  .hero, .riskGrid, .skillLayout, .conclusion { grid-template-columns: 1fr; }
}
```

**Good** (the heavier layout collapses earlier)
```css
@media (max-width: 1024px) {
  .skillLayout { grid-template-columns: 1fr; }  /* contains a long code block */
}
@media (max-width: 900px) {
  .hero, .riskGrid, .conclusion { grid-template-columns: 1fr; }
}
```

Judgment rule: breakpoints follow **content**, not **design consistency**. If you reuse one breakpoint, the layout with the heaviest column will silently break first.

### Example 6 — Face avatar (visual asset)

**Bad**: `<svg>` with `<circle>` + `<path>` mimicking a face → an awkward placeholder.

**Good**: route through **image-asset-strategy**. From Claude Code, **delegate to Codex via `/codex:rescue`** (Codex owns `imagegen` and will produce + wire the asset). From inside Codex, invoke `imagegen` directly. Placeholder + report only if Codex routing is genuinely blocked (user veto, unauthenticated setup) — and surface the reason explicitly.

### Example 7 — Custom-styled icon set

A nav has 5 icons in a duotone peach/coral style that matches the design's brand language.

**Bad**: hand-drawing each icon with `<path d="...">` from memory, trying to approximate the duotone effect with two stacked `<path>` elements per icon.

**Good**: catalog all 5 icons in `image-asset-strategy` as a single asset slot ("custom nav icon set, 24x24, duotone peach/coral, matching reference style"), then batch-delegate to Codex via one `/codex:rescue` call. The set will be coherent because it was generated together; piecemeal hand-drawing tends to drift between icons.

---

## 5. Verification

After edits, you should be able to answer:

1. **Reuse safety** — does the component still behave correctly placed in another container?
2. **State matrix** — hover/focus/disabled/loading/empty handled consistently?
3. **Token hygiene** — every value (spacing/color/gradient/size) expressible as variant or semantic? No raw scatter?
4. **Blast radius** — no visual regression at any importing call site?

For visual / measurement comparison against a reference image, hand off to **visual-reference-compare**.

---

## 6. Reporting

Lead with **what you decided**, not what you changed.

```
Decision: <sizing ownership / responsibility shift / variant addition / etc.>
Why: <why not the alternatives>
Changes: <files + core change>
Verification: <viewports / states / measurements>
Outstanding: <placeholder gaps / follow-ups / concerns>
```

Always list placeholder gaps under "Outstanding".

---

## 7. Skip conditions

- The user gave a precise file/line directive that doesn't conflict with these principles.
- Pure typo / string-only edits unrelated to visual or layout concerns.
- Drawing a simple UI icon already registered in the design system (the ✅ case in principle 6).
