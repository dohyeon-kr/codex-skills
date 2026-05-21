# Codex Skills

Shared Codex skills — generation helpers + design judgment + visual verification.

## Skills

### Generation
- `soft-3d-icon-maker` — creates soft, rounded 3D object icons as transparent PNGs.
- `rounded-line-svg-icon-maker` — creates rounded outline SVG icons with 24x24 geometry.

### Design judgment (during work)
- `css-judgment` — guides judgment when modifying CSS (sizing ownership, design language, blast radius). Catches grid/flex anti-patterns: child margin for sibling spacing, intentionless `flex:1` / `width:100%`, raw px scatter, gradient composition at call sites, sticky `z-index` + content-reserve, flex column scroll-container squashing children, per-layout breakpoint mismatch, UA-default `<ol>` / `<ul>` reset.
- `korean-typography` — Hangul-first typography decisions (Pretendard, line-height 1.7±, `word-break: keep-all`, modular scale, 받침 충돌 가드). Replaces Latin defaults imported from Stripe/Linear/Smashing/Refactoring UI.

### Visual verification (end of work)
- `visual-design-audit` — 16-lens audit (8 aesthetic + 8 usability) using Refactoring UI / NN/g 10 Heuristics / WCAG / Apple HIG / A List Apart / 8pt grid / modular scale / negative space (IxDF) / compositional balance (Smashing). Captures screenshots, measures with `getBoundingClientRect`, enforces self-critique loop.
- `visual-regression-guard` — runs before/after a blast-radius > 1 change (token / theme / shared CSS / common component / breakpoint / external CDN). Phase 1 captures baseline; Phase 2 re-captures and diffs; recovery is a 4-step procedure (locate → hypothesize → bisect → route to the responsible skill).

## Install

Copy the skill folders into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/css-judgment              ~/.codex/skills/
cp -R skills/korean-typography         ~/.codex/skills/
cp -R skills/visual-design-audit       ~/.codex/skills/
cp -R skills/visual-regression-guard   ~/.codex/skills/
cp -R skills/soft-3d-icon-maker        ~/.codex/skills/
cp -R skills/rounded-line-svg-icon-maker ~/.codex/skills/
```

## Invoke

Generation skills use the `$skill-name` prefix:

```text
$soft-3d-icon-maker Create a transparent PNG icon of a pencil.
$rounded-line-svg-icon-maker Create a rounded outline SVG icon of a camera.
```

Judgment / verification skills fire automatically when their triggers (front-matter `description`) match the work context — no explicit invocation needed, but you can also point at them by name:

```text
Use visual-design-audit on the landing page screenshot before reporting done.
Run visual-regression-guard around the token edit you're about to make.
Apply korean-typography defaults to the new prose component.
Walk css-judgment over this layout change.
```

## Sync source

These skills mirror `dohyeon-kr/ai-web-design-study` (the research project's `.claude/skills/`). New patterns are first captured there, then synced here for Codex reuse.
