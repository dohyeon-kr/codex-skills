---
name: visual-regression-guard
description: Use whenever a code change can ripple into the rendered UI of pages you are not currently editing — design token edits, theme/palette/typography changes, shared CSS module edits, common component refactors, breakpoint additions, third-party UI lib upgrades, font/asset CDN bumps. Runs in two phases — (1) **before** the change, capture baseline screenshots of every plausibly-affected screen; (2) **after** the change, re-capture the same screens and diff. If diffs exceed threshold, walks a 4-step recovery (locate → hypothesize → bisect → route to the responsible skill). Distinct from `visual-design-audit` (which judges absolute quality) and `visual-reference-compare` (which compares against an external reference) — this skill compares "after" against "before by the same author." Triggers on any blast-radius > 1 change and on user prompts like "다른 페이지에 영향 없는지 확인해 / 회귀 잡아줘".
---

# Visual Regression Guard Skill

> Most visual regressions ship because nobody captured the "before."
> This skill turns "did this break anything else?" into a tractable two-phase workflow with a recovery procedure.

---

## 1. When to fire

**Fire — pre-change baseline phase** when the upcoming edit has **blast radius > 1 screen**. If you're about to touch one of these, baseline first.

| Trigger | Why it ripples |
|---|---|
| Design token edit (any `:root` variable that components consume) | Every consumer re-renders differently |
| Theme / palette swap | Whole visual surface |
| Shared CSS module edit (used in 2+ places) | Every importer |
| Common component refactor (Button, Card, Header, Modal, etc.) | Every call site |
| Breakpoint addition / change in responsive CSS | Every layout at that viewport |
| Third-party UI lib upgrade (any minor+) | Anywhere the lib styles bleed |
| Font / asset CDN change | Every text or asset surface |
| Global selector change (`body`, `*`, `:where(button)`, etc.) | Anything that matches |

**Skip** when:
- Change is scoped to a single component CSS module and not imported elsewhere
- Change is JS-only with no visual surface
- A reference image is supplied and `visual-reference-compare` is already running (still recommended in addition, but lower priority)

---

## 2. Phase 1 — capture baseline (before the change)

Do this **before the first edit**, not after. If you start editing first you've already lost the baseline.

### 2.1 List the affected screens

The affected-screen list is derived mechanically from the trigger:

- **Token** edit → grep the token across the repo. Every importing file owns at least one screen.
- **Shared CSS module** edit → import graph. Every importer + every page importing those.
- **Common component** edit → call-site grep.
- **Breakpoint** change → every page that has a layout at that viewport.
- **Font CDN / theme swap** → every page (treat as the whole surface).

When the answer is "every page," pick the **3-5 highest-blast-radius pages as sentinels**: the home/landing, a primary list, a primary detail, settings, and one mobile-heavy page. These act as the regression alarm.

### 2.2 Capture each screen

Default tool order:

1. **Inside cmux** → `cmux browser surface:N screenshot --out <path>`
2. **Otherwise** → `agent-browser`, Playwright, or the `screenshot` skill

For each screen, capture:
- **Each breakpoint** the change might touch (desktop, tablet, mobile — pick three concrete pixel widths and stick to them)
- **The default state** at minimum; key interactive states (hover/focus, empty, populated) if the change touches them
- **A pinned scroll position** (record it — see §2.3)

### 2.3 Pin the comparison conditions

Without these, the after-diff will be full of false positives from random noise.

| Knob | Pin to |
|---|---|
| Viewport size | exact px (do not rely on "browser default") |
| Scroll position | `0,0` unless the screen requires inner scroll (see `visual-design-audit` §2-A) |
| DPR | same in both phases |
| Theme | same (light/dark) |
| Locale | same |
| Time-dependent UI | freeze clock or capture a fixed snapshot |
| Network state | populated / cached / empty — same in both phases |
| Font load | wait for `document.fonts.ready` before capture |

### 2.4 Store baselines

The **shape** is universal; the storage choice is project-by-project:

```
<repo>/screenshots/baseline/<branch-or-sha>/<screen-slug>__<breakpoint>__<state>.png
```

| Option | When |
|---|---|
| **`/tmp` ephemeral** | Solo PR, one-shot. Baseline lives only for the session. Zero infra. |
| **Repo-tracked under `screenshots/baseline/`** + `.gitignore` exception | Team workflow, baselines are part of the audit trail. Use `git lfs` if PNGs accumulate. |
| **External (object storage)** | CI-only, large repos, history retention needed |

Always record the **base commit sha** alongside the baseline. Without sha, "what was the before" is recoverable only by memory.

---

## 3. Phase 2 — re-capture and diff (after the change)

### 3.1 Re-capture

Same screens, same conditions as §2.3. **Verify** the pinned conditions matched (especially viewport + scroll + font-load) before reading the diff.

### 3.2 Diff

Three modes, in order of effort:

**Mode A — side-by-side visual** (manual, no tooling)
Open before / after PNGs in a viewer that supports A/B toggle. Look for movement. Fast for ≤ 5 screens. Sufficient for solo workflows.

**Mode B — pixel diff with tolerance** (lightweight)
`pixelmatch` (Node), `Resemble.js`, or `compare` (ImageMagick) with a 0.1–1% threshold (anti-aliasing tolerance). Outputs a third "diff" PNG with red pixels where they differ.

```bash
pnpm dlx pixelmatch --threshold 0.1 baseline.png after.png diff.png
# exit code != 0 → diff exceeded threshold
```

**Mode C — semantic diff with DOM measurement**
Compare `getBoundingClientRect()` of identified components instead of pixels. More robust to font-rendering noise; less robust to background / decorative changes. Best when paired with Mode B.

```js
const items = document.querySelectorAll('[data-snapshot-key]');
JSON.stringify(Array.from(items).map(el => ({
  key: el.dataset.snapshotKey,
  ...el.getBoundingClientRect().toJSON()
})));
```

Compare the JSON; deltas beyond threshold (e.g., width Δ ≥ 4px) are regressions.

### 3.3 Classify each diff

For each red region or rect delta:

| Category | Example | Action |
|---|---|---|
| **Intended** | The change you set out to make actually showed up here too | Accept; update baseline |
| **Acceptable noise** | Anti-aliasing, sub-pixel font hint shift, animation frame | Tighten threshold or mask the region |
| **Regression** | Layout broke, contrast dropped, text wrapped differently, padding changed | Recovery — §4 |

---

## 4. Recovery (when you find a regression)

A 4-step procedure. Don't skip steps even if step 1 looks obvious.

### 4.1 Locate — where exactly

- Which component? (point at the red region; cross-reference with `data-snapshot-key` if you instrumented it)
- Which CSS rule? (DevTools inspect → computed styles → find the source)
- Which token / class is responsible?

### 4.2 Hypothesize — root cause family

Most visual regressions fit one of these families. Name the family **before** opening the diff PNG; it sharpens the search:

| Family | Symptom | Likely cause |
|---|---|---|
| **Token ripple** | Many screens shifted in the same direction (all type bigger, all spacing wider) | The token you changed propagates here too |
| **Cascade leak** | Only one obscure place broke | Selector specificity changed; a rule that used to apply doesn't, or vice versa |
| **Layout shift** | A card moved / overlapped / cropped | Sizing ownership changed; `min-width: 0`, `align-items: stretch`, `flex-direction` |
| **Wrap shift** | Text reflowed differently | font-size / line-height / letter-spacing / max-width / `word-break` |
| **Asset miss** | Image broken or off-position | path / base prefix, lazy load timing, CDN failure |
| **Breakpoint cliff** | Specific viewport broke | A new `@media` matched an unintended layout |
| **State mismatch** | Hover / focus / disabled differs | Pseudo-class or `:where()` change |
| **Theme mismatch** | One theme breaks but the other doesn't | A semantic color resolved to the wrong primitive |

### 4.3 Bisect — narrow to the change

If the cause isn't obvious from step 4.2:

```bash
# Find the first commit where the screenshot differs
git bisect start
git bisect bad HEAD                # current = bad
git bisect good <known-good-sha>   # phase-1 baseline sha
# For each step, the test command is: re-capture the screen and pixelmatch
git bisect run <script-that-captures-and-pixelmatches>
```

Even without `bisect run` automation, manual bisect over 5-10 commits beats reading 200 lines of CSS by eye.

### 4.4 Route — to the responsible skill

This skill detects and locates. **The fix lives in the responsible skill.**

| Family | Route to |
|---|---|
| Layout shift / wrap shift in CSS | `css-judgment` |
| Asset miss / broken image / missing icon | `image-asset-strategy` |
| Token ripple wider than expected | `documentation-and-adrs` to record decision + scope; then `css-judgment` for per-call-site review |
| Quality regression (looks worse despite "working") | `visual-design-audit` to re-walk the lenses on the affected screen |

Do not patch in this skill.

---

## 5. Anti-patterns

- ❌ Editing first, then asking "what broke?" — you've lost the baseline. Re-baseline-then-revert is far more expensive than baseline-then-edit.
- ❌ Capturing baseline at a different viewport / DPR / scroll than the after-shot — every difference will look like a regression.
- ❌ Capturing only the screen you're editing. Token / shared-CSS / common-component edits ripple to screens you aren't looking at — those are the regressions you'll ship.
- ❌ Calling a diff "noise" without checking. Sub-pixel shifts are noise; a card that moved 8px is not.
- ❌ Accepting a regression because "the new look is fine too" — that's a different decision. Decide explicitly: keep + update baseline + record the intent, or revert.
- ❌ Patching the regression at the call site when the cause is the token — you'll repeat the patch at every other call site.
- ❌ Skipping the bisect for "I know what it is" — being wrong once costs more than running bisect always.

---

## 6. Tooling fallback chain

| Available | Capture | Diff |
|---|---|---|
| Inside cmux | `cmux browser ... screenshot` | `pixelmatch` if installed, else manual side-by-side |
| Outside cmux, Node available | `agent-browser` / Playwright | `pixelmatch` / `resemblejs` |
| Anywhere | `screenshot` skill | manual side-by-side |

The skill does not require a specific tool. The **discipline** of phase-1 capture and phase-2 comparison is the value, not any one tool.

---

## 7. Storage discipline

The fastest setup that scales:

```
screenshots/
  baseline/
    <ISO-date>-<short-sha>/
      <screen-slug>__<viewport>__<state>.png
  diff/                       # ephemeral, gitignored
    <ISO-date>-<short-sha>/
      <screen-slug>__<viewport>__<state>__diff.png
```

Update baseline only when:
- An **intended** visual change shipped — refresh that screen's baseline + record the commit sha + one-line reason
- A new screen entered the sentinel list

Do not auto-refresh on every PR — that defeats the purpose. Baselines lag intentionally.

---

## 8. Reporting

```
# Visual Regression Guard — <change description>

## Baseline
- Captured: <date>, base sha <abc1234>
- Screens (N=…): <list with viewport / state>

## After
- Re-captured: <date>, head sha <def5678>
- Conditions matched: ✓ (viewport / scroll / DPR / font-load)

## Diff results
- Mode used: <A side-by-side | B pixelmatch | C DOM measurement>
- Screens with diff > threshold:
  - <screen> @ <viewport>: <% pixel diff> — classified as <intended | noise | regression>

## Regressions
### <screen> @ <viewport>
- Family: <token ripple | cascade leak | layout shift | wrap shift | asset miss | breakpoint cliff | state mismatch | theme mismatch>
- Located: <component / CSS rule / token>
- Routed to: <skill name>
- Status: <fixed in commit … | open punch list item>

## Outstanding
- Baseline refreshes pending: <list>
- Skipped screens: <list with reason>
```

---

## 9. Relation to sibling skills

| Skill | Relation |
|---|---|
| `visual-design-audit` | Different axis. Audit asks "is this **good** design?" Guard asks "is this **the same** as before (except where I intended)?" Both run at end-of-task. |
| `visual-reference-compare` | Same shape, different baseline source. Compare uses **external reference image**; Guard uses **your own pre-change capture**. Run together when both apply. |
| `css-judgment` | The most common landing for "where to fix" — layout / wrap / sizing-ownership families. |
| `image-asset-strategy` | Asset-miss regressions route here. |
| `documentation-and-adrs` | When a token change had wider blast radius than expected, record the decision + scope here so the next change has the intent visible. |

---

## 10. The one-line rule

> If your change can be felt by a screen you're not currently looking at, capture before you start editing.

That single discipline removes most visual regressions before they happen. The rest of this skill is just procedure for when the discipline pays off.
