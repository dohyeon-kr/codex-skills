---
name: visual-design-audit
description: Use at the end of any UI work — right before reporting "done" or opening a PR — to audit a rendered screen against two axes (심미성 / 유저 편의성). Captures viewport screenshots via cmux / agent-browser / playwright, then walks 16 lenses derived from Refactoring UI, NN/g 10 Heuristics, WCAG, Apple HIG, A List Apart, and Don Norman's "Design of Everyday Things." Enforces measurement (`getBoundingClientRect`, contrast, target-size in numbers) over eyeball judgment, with explicit guards for inner-scroll-container traps, carousel/swipe padding parity, page-vertical symmetry, and flex content-size shrinking. Returns a prioritized punch list with severity + lens + measured deltas + recommended fix. Distinct from `visual-reference-compare` — that skill compares a render against a supplied reference image; this skill judges whether the render is good design on its own terms. Triggers when no reference is supplied, when the user says "디자인 어때 / 괜찮아 보여 / 검토해줘 / 패딩 안 맞는 거 확인해", and as the standard final gate after frontend work.
---

# Visual Design Audit Skill

> Build passing ≠ design good. The render must be **seen and judged** before shipping.
> This skill walks the screen against two axes — **심미성**(aesthetic quality) and **유저 편의성**(usability) — using 16 lenses from canonical design literature.

---

## 1. When to fire

**Always fire** at one of these moments:

- Final step of any UI work, before "complete" / PR open
- After a token / theme / typography change that touches multiple components
- Before declaring a design system migration "done"
- When the user asks "디자인 어때 / 괜찮아 보여 / 디자인 검토해줘"
- When you have no reference image (if you have one, run `visual-reference-compare` in addition — they're complementary, not duplicate)

**Skip** when:
- The change is non-visual (data layer, build config, docs only)
- A more specialized skill has already covered this surface (e.g., `visual-reference-compare` was just run on the same screen with a reference)
- The user explicitly says "skip the visual check"

---

## 2. Capture

Use the available tooling in this order:

1. **Inside cmux** → `cmux-browser` skill (`cmux browser surface:N screenshot /tmp/x.png`)
2. **Without cmux** → `agent-browser`, Playwright, or the `screenshot` skill
3. **Always capture multiple breakpoints**:
   - **Desktop** ≥ 1280px (the layout the design probably started from)
   - **Tablet** ~ 768px (one or two columns collapse here)
   - **Mobile** ~ 393px (Pretendard / Hangul wrap behavior changes)
4. **Always capture key states** when relevant:
   - default / hover / focus-visible / active / disabled
   - empty / loading / error
   - first-load vs. populated (skeleton vs. content)
5. **Capture at 1× and 2× DPR** if the design relies on hairlines / fine typography.

Don't audit from memory. The whole point is *seeing*.

### 2-A. Find the real scroll container before screenshotting

A surprisingly common time-sink: you call `window.scrollTo(0, 0)` or `cmux browser scroll --y 0`, the viewport doesn't move, you screenshot, and the screenshot shows the middle of the screen — not the top. Cause: the page isn't scrolling `window`. It's scrolling an **inner container** (e.g., a phone-frame `<section aria-label="홈"> > <div>` with `overflow: auto`).

**Detection order** before the first screenshot:

```js
// 1. Is window scroll actually moving?
({ winY: window.scrollY, docH: document.documentElement.scrollHeight, vh: innerHeight })

// 2. If winY stays 0 / docH ≈ vh but content is clearly longer, look for inner scroll
Array.from(document.querySelectorAll('*'))
  .filter(el => el.scrollHeight > el.clientHeight + 4 && getComputedStyle(el).overflowY !== 'visible')
  .map(el => ({ tag: el.tagName, label: el.getAttribute('aria-label'), sh: el.scrollHeight, ch: el.clientHeight }))
```

Then scroll the **real container** by reference, not `window`:

```js
const real = document.querySelector('section[aria-label="홈"] > div'); // or whatever your selector
real.scrollTo({ top: 0, behavior: 'instant' });
```

Mobile-app-style designs hosted in a fixed-phone-frame container almost always need this. Skip this step and every screenshot will be the wrong region of the page.

### 2-B. Verify scroll position succeeded

After every scroll, **re-read `scrollTop`** before screenshotting. `cmux browser scroll --y 0` can silently no-op if the wrong element is the scroll root. One line of paranoia saves a full pass of audit.

---

## 3. The two axes

| Axis | Question | Outcome |
|---|---|---|
| 심미성 (Aesthetics) | "이 화면을 처음 본 사람이 시각적으로 정돈됐다고 느끼는가?" | hierarchy / rhythm / balance / palette |
| 유저 편의성 (Usability) | "처음 본 사람이 다음에 뭘 해야 할지 즉시 알고, 그렇게 할 수 있는가?" | affordance / contrast / target size / status |

**Both must pass.** Beautiful but unusable, or usable but ugly, is a fail.

---

## 4. 심미성 lenses (6)

### 4.1 Visual hierarchy — *Refactoring UI* ch. 2

> "Hierarchy isn't about making things bigger; it's about making important things stand out."

Check:
- Is there a clear **first thing the eye lands on**? (hero / primary headline)
- Are H1 → H2 → body **at least 1.5× step** in size, or compensated by weight / color?
- Is body text bolder/darker than secondary/meta text?
- **Are size + weight + color used together** (not size alone)?

Bad signals:
- All headings the same size; only color separates them
- Body text gray-on-white (`#aaa` on `#fff`) — fails WCAG AA + flattens hierarchy
- 16px body, 18px H3 — almost no perceived difference
- Multiple "primary" buttons competing

Good ref: Stripe docs, Linear changelog, Vercel marketing — body at 17-19px, headlines at 32-56px with strong weight contrast.

### 4.2 Spacing rhythm — *Refactoring UI* ch. 3, *Every Layout*, *8-Point Grid (Bryn Jackson)*

> "Start with too much whitespace and remove until it feels right — not the other way."

Check:
- Are spacings drawn from a **scale** (4 / 8 / 12 / 16 / 24 / 32 / 40…) or arbitrary px?
- Does the scale follow an **8pt grid** (multiples of 8) with optional **4pt baseline grid** for typography? — industry standard for scalability across DPRs.
- Is **vertical rhythm consistent across sections** (e.g., every section uses the same large spacer)?
- Is `gap` used on parent containers, not `margin` on every child?
- Does the screen have **breathing room** at the page edges (≥ 24px on mobile, ≥ 40px on desktop)?
- Is `line-height` a **multiple of the base unit** (e.g., 24px line-height for 16px text on an 8pt grid)?
- **Micro vs macro spacing ratio** — micro (gaps inside a card / between paragraph lines) should be ≈ 1/3 of macro (gaps between sections). If a card's internal padding equals the gap between cards, the cards visually merge.

Bad signals:
- One section has 56px below, the next has 32px, the next has 48px — random
- Cards crammed against each other with no separation
- Page content touches the viewport edge
- Internal card padding == external card gap → cards visually bleed into one mass
- 1px / 3px / 7px-style spacings → not on any scale

Good ref: Apple newsroom, Notion docs — generous, rhythmic spacing.

### 4.3 Color & contrast — *Refactoring UI* ch. 4, *WCAG 2.2*

> "Use a small set of semantic colors. Don't decorate with color; communicate with it."

Check:
- Palette size: ≤ 3 brand colors + neutrals + 2-3 status (success/warning/danger)?
- Body text vs. background contrast ≥ **4.5:1** (WCAG AA), large text ≥ **3:1**?
- Interactive elements visually distinct from static ones?
- Does color encode meaning (status, action) consistently?

Quick in-page contrast probe (run in console / cmux eval — no DevTools needed):

```js
function relLum(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const t = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  return 0.2126 * t(r) + 0.7152 * t(g) + 0.0722 * t(b);
}
function ratio(fgHex, bgHex) {
  const a = relLum(fgHex), b = relLum(bgHex);
  return ((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toFixed(2);
}
// Example: ratio('#5e6470', '#f6f4ef') → "5.83" (passes AA body)
```

Flag any text where measured ratio < required threshold and route to `css-judgment` for a token-level fix (not a one-off color override at the call site).

Bad signals:
- 14px gray-on-gray text "for elegance" — fails AA
- Brand color used for everything (buttons, links, dividers, icons) — semantics dilute
- Hover state same color as default — no feedback

Tools: macOS `Digital Color Meter` / Chrome DevTools "Contrast" / `npx pa11y <url>`.

### 4.4 Alignment, balance & visual tension — *Don Norman*, *Refactoring UI*, *Smashing (compositional balance)*

> "Optical alignment trumps mathematical alignment. Symmetric balance is calm; asymmetric balance is alive."

**Tension & focal point** (composition layer):
- Is there **one clear focal point** the eye lands on first, and is it deliberately placed (not center-by-default)?
- If the composition is asymmetric, are the visual weights balanced (one heavy element vs. several lighter ones / dense vs. spacious / dark vs. light)?
- Are there **leading lines** (image edges, type baselines, dividers) that guide the eye to the focal point?
- Is there at least one **dominant axis** the layout commits to (vertical column for editorial, diagonal for energetic, horizontal for narrative)? "Floats randomly" reads as undesigned.
- Are complementary contrasts present where tension is wanted (light vs. dark, dense vs. sparse, large vs. small, color vs. mono)? Same-weight everywhere = flat.

**Alignment (measurement layer):**

Check:
- Are siblings (cards, list items) **left-edge aligned**? (measure with `getBoundingClientRect().left` — *do not eyeball*)
- Are cards in a grid **same height** (or intentionally different — never accidentally)?
- Are cards in a grid **same width**? (a single card narrower than its peers usually means it didn't fill its grid cell — child needs `width: 100%` or grid template fix)
- Is whitespace distributed (no card stretched into empty band)?
- Does the overall composition have a **clear focal point** (eye anchor)?
- **Section vertical padding symmetry** — the gap above and below the page content should match unless deliberately asymmetric. Measure `frame.getBoundingClientRect()` vs. `firstSection.getBoundingClientRect().top` and `lastSection.getBoundingClientRect().bottom`. A page with `padding-top: 32px / padding-bottom: 16px` reads as "the designer forgot."

Bad signals:
- One card stretches to match a sibling and gains an empty trailing band → **`align-items: stretch` smell**, see `css-judgment` Example 8
- Two-column grid with one column overflowing → **`min-width: 0` smell**, see `css-judgment` Example 5
- Card narrower than its peers in the same row → **flex/grid child not filling its track** (the `<button>` shrinking to label width is the most common variant — `<button>` defaults to inline-block sizing, so even inside `flex-direction: column` it shrinks to its content; force with `width: 100%` or `align-items: stretch` on the parent)
- Centered headings but left-aligned body inside the same container
- Page top padding ≠ page bottom padding (asymmetric without intent)

### 4.5 Typography quality — *A List Apart*, *Refactoring UI*

> "Get the body right first. Everything else is fine-tuning."

Check (English/Latin):
- Body 16-19px / line-height 1.5-1.7 / max-width 65-75 char
- Headings tighter line-height (1.05-1.2) / slightly negative letter-spacing
- One or two type families max (sans for UI; serif/mono for editorial accents)

Check (Korean):
- **Run `korean-typography` skill** for the full checklist (Pretendard, line-height 1.7+, word-break: keep-all, 받침 충돌 가드)

Bad signals:
- Body < 15px (Latin) / < 16px (Korean) — looks small even when "design article said so"
- All text in the same weight (visual monotony)
- Justified text with awkward gaps
- Long URL / 어절 forcing horizontal scroll → missing `overflow-wrap: break-word`

### 4.6 Image use & composition — *A List Apart*, *Refactoring UI*, editorial photography best practices

> "An image is a co-author of the headline. If it doesn't argue for the page, it's filler."

Check:
- **Aspect ratio**: hero ≥ **1.7:1** (16:9 baseline) on desktop, taller crop (4:5 or 3:4) on mobile. Aspect should be a design decision, not a CMS upload accident.
- **Focal point**: subject in the **rule-of-thirds** anchor, not always center. If text overlays the image, the focal point and the text occupy **different thirds**.
- **Text-over-image contrast**: WCAG 4.5:1 against the **actual pixels behind the text** (not the average). Use a dim overlay or vignette if the image is busy.
- **Photographic vs. illustration choice**: editorial moodshot for emotion, illustration for abstract concepts, photography for product. Don't mix all three on one page without a clear hierarchy of voice.
- **Mobile crop survives**: the desktop hero usually crops to mobile with the right 30% lost. Verify the focal point still reads at the mobile crop.
- **Image-to-text ratio per fold**: an entirely-text fold reads as a wall; an entirely-image fold reads as advertising. Aim for **roughly 40-60% image weight** in editorial sections, 0% in dense info sections — but pick deliberately, not by accident.
- **Loading strategy**: hero `loading="eager"` + `fetchpriority="high"`; below-fold `loading="lazy"`. Mis-set lazy on hero = visible pop-in.

Bad signals:
- Hero is a generic stock photo of laptops/handshakes — no editorial voice
- Text sits awkwardly over a busy region of the image (no overlay, no contrast)
- Every image is the same 16:9 aspect and same focal placement — visual monotony
- Hero focal point gets cropped out on mobile

### 4.7 Proportion & negative space — *Vanseo Design (golden section)*, *A List Apart (modular typography)*, *IxDF (white space)*

> "Whitespace is not absence; it is composition. Proportion is not aesthetics; it is structure."

**Proportion & modular scale:**
- Type sizes drawn from a **modular scale ratio** (1.250 Major Third / 1.333 Perfect Fourth / 1.5 Augmented Fourth / 1.618 Golden Ratio)? Each step is a deliberate multiple, not a guess.
- Body / lede / heading sizes preserve the ratio across breakpoints?
- Hero column-to-side-column width ratio reads as intentional (e.g., 1.618 : 1 for golden, 1.2 : 1 for near-equal, 2 : 1 for emphasis)?

**Negative space (Micro vs Macro):**
- **Macro whitespace** (between major sections, page margins, around hero) — generous, defines the page's calm
- **Micro whitespace** (between lines, around paragraph, inside cards) — tight enough that grouping is preserved
- **Ratio**: micro ≈ 1/3 of macro. If they're equal, every group blurs into the next.
- **Gestalt proximity check**: items in the same group should be visually closer to each other than to items in a different group.
- **Page edge margins** scale with viewport (e.g., 16-24px mobile / 40-80px desktop / centered max-width ≤ 1200px on ultra-wide).

Bad signals:
- Type sizes are 15 / 16 / 18 / 22 / 24 / 28 / 36 — no consistent ratio, looks like trial-and-error
- Section spacing == card spacing == paragraph spacing — everything blurs together (Gestalt proximity broken)
- Page margins are 0 — content hugs viewport edge, no breathing room
- Excessive whitespace **inside** cards but cards crammed against each other (proportion inverted)
- Hero columns split 50/50 by default — perfectly symmetric is often the least interesting choice

### 4.8 Distinctiveness — *frontend-design* skill alignment

> "Avoid the generic AI aesthetic: centered hero / 3-card grid / purple gradient / 'Get Started' CTA."

Check:
- Does the screen have a **point of view** (a specific style choice you can name)?
- Or does it look like every other AI-generated landing page?
- Is at least one element doing something **unexpected but intentional** (asymmetry, oversized number, editorial pull-quote, photographic moodshot)?

Bad signals:
- Three identical cards in a row, each with icon + title + paragraph + "Learn more"
- Hero is centered headline + subhead + gradient button + gradient blob in background
- Purple-to-pink gradient with no other color discipline

If the screen feels generic, that's not a polish issue — it's a *design* issue. Surface it.

---

## 5. 유저 편의성 lenses (6)

Based on **Nielsen Norman Group's 10 Usability Heuristics** (Jakob Nielsen, 1994 → still definitive), distilled to the six that show up in screenshots:

### 5.1 Affordance — *Don Norman, "Design of Everyday Things"*

> "An object's appearance should suggest how it's used."

Check:
- Is every clickable element **visually distinct** from static text? (color / underline / button shape)
- Do buttons look pressable (filled or outlined, not just text)?
- Is the **primary action** the most prominent thing on the screen?
- Are icons accompanied by labels (unless they're universally recognized — search, close, menu)?

Bad signals:
- Inline link looks identical to body text
- "Button" is just colored text, no shape
- Two buttons with the same weight ("Cancel" vs "Submit" both gray outline)

### 5.2 Visibility of system status — *NN/g #1*

> "The system should always keep users informed about what is going on, through appropriate feedback within reasonable time."

Check:
- Is loading state visible (skeleton / spinner / progress)?
- Is success/error feedback visible (toast / banner / inline message)?
- Does the URL / breadcrumb / page title reflect where you are?
- Is selected/active state obvious (nav highlight, tab active border)?

Bad signals:
- Click button → nothing happens for 2s, no feedback
- Form submits silently with no confirmation
- Active nav item indistinguishable from inactive

### 5.3 Touch target & hit area — *Apple HIG / Material Design*

> "Touch targets should be at least 44×44 pt (iOS) / 48×48 dp (Android)."

Check:
- Every interactive element ≥ **44×44 pt** (use DevTools to measure)?
- Adequate spacing between adjacent targets (≥ 8 pt) to prevent mis-taps?
- Are touch targets sized for the **action's importance** (primary CTA bigger than secondary)?

Bad signals:
- Icon-only buttons at 24×24 — too small for thumbs
- Two checkboxes 4px apart — adjacent taps overlap

### 5.4 Readability — *A List Apart*, *WCAG 2.2*

> "If users can't comfortably read your text, nothing else matters."

Check (overlap with 심미성 4.5):
- Body ≥ 16-17px (한글이면 17px+)
- Contrast ≥ 4.5:1 (or 3:1 for large/heading text)
- Line length 45-75 char (`max-width: ~65ch` rule of thumb)
- Line-height 1.5+ (한글 1.7+)
- Not all-caps for body (only short labels)

Bad signals:
- Cramped body filling the entire viewport width (95 char per line)
- Gray text on colored card background → low contrast
- Hangul body at 14px — under-sized for the script

### 5.5 Navigation clarity — *NN/g #6, #4*

> "Show users what they're looking at, what they can do, and how they can get back."

Check:
- Is there always a way back? (header logo, breadcrumb, browser back works)
- Is the current section/tab visibly marked?
- Are nav items grouped logically (no surprise ordering)?
- Does the layout follow platform conventions (e.g., bottom nav on mobile, sidebar on desktop)?

Bad signals:
- Hash routing breaks browser back button
- Tab UI without a clear "current" state
- Floating CTA covers content with no way to dismiss

### 5.6 Carousel / horizontal scroll — *Apple HIG (Scroll Views), Material (Horizontal scrollers)*

> "The first item in a horizontal scroller should align with the rest of the page's content edge — and the last item should have the same trailing breathing room as the leading one."

Check:
- **First card's left edge** = the page content's left edge? (use `getBoundingClientRect().left` on the first card vs. the page frame's content edge)
- **`scroll-padding-inline-start` / `padding-inline-start`** on the scroller? Without it, when a user swipes back, the first card snaps flush to the viewport edge with zero breathing room.
- **Last card's right edge** has the same breathing room as the first card's left? Or is it amputated by `overflow: hidden`?
- **Scroll snap** behaves on slow swipe? Not jumping past the intended card?

Bad signals:
- First card touches the viewport edge (no leading padding) — most common; very visible on mobile
- Last card's right edge is exactly at viewport edge → user can't tell if there's more
- `overflow-x: auto` without `scroll-padding` → snap brings cards flush to edge
- Different padding on left vs. right of the strip

Fix recipe (CSS):
```css
.carousel {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  /* leading / trailing breathing room */
  padding-inline: var(--space-lg);
  /* preserve breathing room on snap-back */
  scroll-padding-inline: var(--space-lg);
}
.carousel > * { scroll-snap-align: start; }
```

### 5.7 Micro-interaction & feedback — *Apple HIG (Animation), NN/g #1*

> "A polished UI has motion. Not flashy motion — confirmation motion."

Check:
- Every interactive element has a **visible state change** on hover (desktop) and active/press (mobile)? (subtle color shift, scale 0.97 on press, border emphasis — pick a small, consistent vocabulary)
- Cards / buttons feel "alive" on hover, or are they static rectangles?
- **Critical feedback motions are present**: progress bar fill animation, save toast slide-in, optimistic UI update, skeleton shimmer
- **Restraint**: motion ≤ 200ms (NN/g), `prefers-reduced-motion` respected, no decorative loops competing with content

Bad signals:
- Buttons are visually inert until clicked (no hover, no press) — feels unresponsive
- All motion happens in 800ms eases — feels sluggish
- Decorative parallax / scroll-jacking on a content site — distracting
- `:hover` defined but no `:focus-visible` — keyboard users get nothing

Patterns to add (light, default these in):
```css
.interactiveCard {
  border: 1px solid var(--border-card);
  transition:
    transform 0.12s ease,
    background-color 0.12s ease,
    border-color 0.12s ease,
    border-width 0.12s ease;
}
.interactiveCard:hover {
  background-color: var(--surface-hover);
  /* Hover border 강화: 두꺼워지고 theme color로 — 카드가 '집어지는' 느낌 */
  border: 2px solid var(--accent-brand);
  /* 두께가 1→2px로 늘면 1px만큼 contents가 밀려나므로 padding을 1px 줄여 보정 */
  padding: calc(var(--space-md) - 1px);
}
.interactiveCard:active { transform: scale(0.98); }
.interactiveCard:focus-visible { outline: 2px solid var(--accent-focus); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  .interactiveCard { transition: none; }
  .interactiveCard:active { transform: none; }
}
```

Hover의 visual weight 변화는 두 가지 같이 가야 자연스럽다:
- **color shift**(미세한 배경 톤 변화)
- **border 강화**(두께 +1px + theme accent color)

color shift만 있으면 평평하고, border만 두꺼워지면 보더가 갑자기 튀어나온다. 둘이 동시에 변할 때 카드가 "들려" 보인다.

### 5.8 Empty / error / edge states — *NN/g #9*

> "Help users recognize, diagnose, and recover from errors."

Check:
- Empty state has a **prompt** ("아직 데이터가 없어요 → 첫 항목 만들기"), not a blank page
- Error state explains what went wrong + what to do (not "Error 500")
- Loading state doesn't block the entire UI if avoidable (skeleton over spinner)
- 404 / unauthorized has a path back

Bad signals:
- Empty list with no message
- "Something went wrong" with no detail or retry
- Full-screen spinner for every action

---

## 6. Audit procedure

For each captured screenshot:

1. **First impression (10s)** — Note your gut reaction in one sentence. *"What do I see first? What feels off?"* This single sentence often surfaces the real issue faster than checklists.
2. **Walk the 16 lenses** — Don't skip ones that feel "obviously fine." The skip is where regressions hide.
3. **Measure — don't eyeball.** This is the single biggest lift in audit quality. Open the page in cmux/playwright and pull numbers, then compare to thresholds:

   ```js
   // Page frame / canvas
   const frame = document.querySelector('section[aria-label="..."]');
   frame.getBoundingClientRect();

   // Every card in a row — check left/width parity
   const cards = document.querySelectorAll('[role="listitem"]');
   Array.from(cards).map(c => {
     const r = c.getBoundingClientRect();
     return { top: r.top, left: r.left, width: r.width, height: r.height };
   });

   // Vertical padding symmetry on the page
   const first = document.querySelector('section:first-of-type');
   const last  = document.querySelector('section:last-of-type');
   ({ top: first.getBoundingClientRect().top, bottomGap: innerHeight - last.getBoundingClientRect().bottom });

   // Touch target sizes
   Array.from(document.querySelectorAll('button, a, [role="button"]')).map(el => {
     const r = el.getBoundingClientRect();
     return { label: el.textContent?.slice(0,20), w: r.width, h: r.height };
   }).filter(b => b.w < 44 || b.h < 44);

   // Contrast (rough — use DevTools "Contrast" for the official measurement)
   getComputedStyle(document.querySelector('p')).color;
   ```

   Patterns to compare against:
   - All cards in a row → `width` should be equal (±1px). Unequal means a child didn't fill its grid cell.
   - All cards in a row → `left` should be equal (or in monotonic carousel order).
   - Vertical padding symmetry → top gap vs. bottom gap within 4px.
   - Touch targets < 44×44 → flag.
   - Body text contrast < 4.5:1 → flag.

4. **Note severity per finding**:
   - **blocker** — fails WCAG, breaks usability, unreadable text, broken layout (overflow / cropping)
   - **major** — clear UX issue but doesn't break the screen (low contrast, missing feedback, ambiguous CTA)
   - **minor** — style inconsistency, slightly off rhythm, could be more distinctive
   - **nit** — pure preference, ignore unless many accumulate
5. **For each finding** include: severity / axis / lens / location (component or screenshot region) / **measured numbers** / recommended fix / reference (which article / heuristic).

> "정렬이 안 맞아 보여" 는 약함. "Card 3의 width가 156px인데 나머지 4개는 168px — `<button>`이 flex column 안에서 콘텐츠 폭으로 줄어듦. `width: 100%` 추가." 가 강함.

### 6.1 Self-critique loop (강제)

스크린샷을 본 직후, 다음 한 줄을 **반드시** 적는다 — "approve 직전 마지막 솔직한 평가":

> *"내가 이 화면을 처음 보는 사람이라면, '이 부분은 디자인이 좀 약하다'고 말할 곳은 어디인가?"*

찾았다면 그 위치를 **major 이상**으로 분류한다. 자가 critique 없이 "다 괜찮다"로 끝나는 audit은 lens를 walk했더라도 실패한 audit이다. 이 한 줄은 보통 디자인 자체의 결함(레이아웃 결정 / 카드 컨셉 / 정보 위계)을 노출하며, 그건 css-judgment로는 못 잡고 **재설계로만** 잡힌다.

재설계가 필요하다고 판단되면 해당 컴포넌트는 `frontend-design` 스킬로 라우팅하고 "redesign 후보" 로 보고에 명시.

---

## 7. Report format

```
# Visual Design Audit — <screen / route>

## First impression
<one sentence>

## Findings (sorted by severity)

### blocker — <axis> — <lens>
- Location: <component path or screenshot annotation>
- Issue: <what's wrong, measured if possible>
- Fix: <specific css/component change>
- Ref: <article / heuristic / `css-judgment` Example N>

### major — ...

### minor — ...

## Passed lenses
- <lens>: ✓ <why it's good — short>
- ...

## Outstanding
<questions, scope creep risks, things needing user input>
```

Keep findings **specific and measurable**. "여백이 너무 많다" 는 약함. "heroCard 하단에 240px 빈 band, `align-items: stretch` 결과 — `align-self: start`로 fix" 는 강함.

---

## 8. Anti-patterns (audit itself)

- ❌ "Looks good to me" — that's not an audit. Walk the lenses.
- ❌ Skipping mobile capture because "desktop looks fine"
- ❌ Approving without measuring contrast / size when the issue is on that lens
- ❌ Lumping all findings as "minor"
- ❌ Suggesting fixes outside the screen (refactor X, rebuild Y) — stay on what the screenshot shows
- ❌ Writing the report without the screenshots inline / referenced
- ❌ **Screenshotting without verifying scroll position succeeded** — `cmux browser scroll --y 0` silently no-ops if the page uses an inner scroll container. Always re-read `scrollTop` after a scroll command. See §2-A / §2-B.
- ❌ **Eyeballing alignment / width / padding parity** — these are number questions. Use `getBoundingClientRect()`; report exact px deltas. "Looks off" is not a finding.
- ❌ **Drawing missing icons by hand inside the audit** — if a screenshot reveals empty/broken icon slots or fake-photo SVGs, route through `image-asset-strategy` → `/codex:rescue` (Codex owns `imagegen`, can run with `--write` to land files directly). Do not "just sketch a placeholder."
- ❌ **Stopping at the first finding** — full-pass the lenses even if you find a blocker early. Subsequent findings often share a root cause and fix together.

---

## 9. Relation to sibling skills

| Skill | Relation |
|---|---|
| `visual-reference-compare` | Comparison against a **supplied reference image**. Run this skill **in addition** when you have a reference, not instead. |
| `css-judgment` | Where most of the recommended fixes will land. The audit *finds* issues; css-judgment *guides the fix*. Example 5 / 8 / 9 are common targets. |
| `korean-typography` | When body is Hangul, defer the typography lens (4.5 / 5.4) to its checklist. |
| `image-asset-strategy` | If the audit finds a fake SVG face / product / hero, route it back through asset-strategy → Codex / `imagegen`. |
| `frontend-design` | Distinctiveness lens (4.6) — if audit flags "looks AI-generic," the next iteration goes through frontend-design's "avoid generic aesthetic" guide. |
| NN/g 10 Heuristics | https://www.nngroup.com/articles/ten-usability-heuristics/ — the canonical reference for §5 lenses. |
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ — color contrast and target size compliance. |
| Apple HIG / Material Design | Platform conventions for touch target, navigation, gestures. |
| Refactoring UI | https://www.refactoringui.com/ — the canonical reference for §4 lenses. |

---

## 10. When the audit blocks ship

If you find ≥ 1 **blocker**, do not approve. Either:
- Fix it now (route to `css-judgment` / `korean-typography` / etc.)
- Or report it clearly and ask the user before shipping

If you find only **major / minor / nit**, list them in the punch list and let the user decide what to ship-now vs. file-for-later.

---

## 11. References (one-line each)

- **Refactoring UI** — Wathan & Schoger. Visual hierarchy, spacing, color, typography. Highest density of actionable advice.
- **NN/g 10 Usability Heuristics** — Nielsen. The default usability vocabulary.
- **The Design of Everyday Things** — Norman. Affordance, signifier, feedback.
- **A List Apart** — typography, readability essays (Tim Brown's "More Meaningful Typography" etc.).
- **WCAG 2.2** — color contrast, text size, target size compliance.
- **Apple Human Interface Guidelines** — touch target, platform conventions.
- **Material Design 3 Guidelines** — touch target, motion, accessibility.
- **Every Layout** — Bell & Andrew. CSS layout primitives and rhythm.
- **Tufte, Edward** — *Visual Display of Quantitative Information*. Density, signal/noise.
- **8-Point Grid (Bryn Jackson, Spec.fm)** — multiples-of-8 spacing scale + 4pt baseline grid for typography.
- **Modular scale (Tim Brown / A List Apart)** — type sizes drawn from a ratio (1.250 / 1.333 / 1.5 / 1.618).
- **Golden ratio in UI (Figma resource library, NN/g)** — 1.618 as a column / typography / button proportion.
- **Negative space in design (IxDF)** — micro vs macro whitespace; micro ≈ 1/3 of macro; Gestalt proximity for grouping.
- **Compositional balance (Smashing Magazine)** — symmetric vs. asymmetric balance; visual tension via weight contrast and leading lines.
- **Hero image best practices (Shopify / Squarespace blog)** — 16:9 baseline, mobile crop survival, focal at rule-of-thirds, text/image contrast.
- **한국 디자인 블로그** — toss / 카카오디자인 / 우아한형제들 / karrot — Hangul-aware patterns to compare against.
