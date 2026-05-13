---
name: rounded-line-svg-icon-maker
description: Create clean monochrome rounded-line SVG icons in a Lucide/Heroicons-style outline aesthetic. Use when Codex needs to produce, adapt, or review vector SVG icons with 24x24 viewBox, stroked paths, rounded caps and joins, no fills, currentColor support, compact markup, and consistent icon-set geometry.
---

# Rounded Line SVG Icon Maker

## Overview

Create SVG icons that match a modern rounded outline set: black or `currentColor` strokes, simple geometric silhouettes, 24x24 grid, thick rounded strokes, no filled shapes, and no raster image data.

Read `references/style-guide.md` before making a new icon set or when matching the provided reference image closely.

## Workflow

1. Identify the concept, target size, and whether the output is a single SVG, React component, or multiple files.
2. Sketch the icon as 2-5 primary strokes on a 24x24 grid. Favor simple recognizable metaphors over literal detail.
3. Write the SVG directly. Use `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, `stroke-linecap="round"`, and `stroke-linejoin="round"`.
4. Keep paths aligned to whole or half coordinates. Leave at least 2 units of optical padding unless the existing icon set requires a different grid.
5. Validate the SVG with `scripts/validate_svg_icon.py` when writing a file.
6. If the icon is part of an existing library, match the local component/API pattern exactly.

## SVG Template

Use this structure by default:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="..." />
  <path d="..." />
</svg>
```

For accessible standalone SVGs, replace `aria-hidden="true"` with:

```svg
<title>Icon name</title>
```

and add `role="img"` on the root.

## Style Rules

- Use outline-only geometry. Do not use filled blobs, gradients, shadows, filters, masks, embedded images, or text.
- Prefer `path`, `line`, `polyline`, `polygon`, `circle`, `rect`, and `ellipse`.
- Use one visual weight across the icon. Default to 2px stroke; use 1.75px only when matching an existing lighter set.
- Use rounded endpoints and rounded joins for the hand-drawn but precise feel shown in the reference.
- Make corners soft but not bubbly. The style should feel utilitarian, crisp, and UI-ready.
- Use small filled-looking details only by drawing tiny outline circles or short strokes, not actual fills.
- Avoid excessive path precision. Trim generated decimals to at most one decimal unless a curve needs more.

## Composition Patterns

- Directional icons: use simple arrows with open heads and round caps.
- Objects: combine one enclosing silhouette with 1-3 internal detail strokes.
- Badges or status variants: add a small circle, slash, check, plus, minus, or dot while preserving the base icon silhouette.
- Text-like icons: use simple letterform strokes only when the requested icon is explicitly typography-related.
- Disabled or muted variants: draw a diagonal slash from upper-left to lower-right, with enough separation from the main contour.

## Validation Checklist

Before delivery, confirm:

- The SVG has `viewBox="0 0 24 24"`.
- The root uses `fill="none"` and `stroke="currentColor"` unless the user requested a fixed color.
- Stroke caps and joins are round.
- The icon remains legible at 16px.
- No raster data, base64, gradients, filters, external references, or accidental background rectangles are present.
- The filename is lowercase hyphen-case, such as `baby-face.svg` or `notification-off.svg`.

## Useful Command

When a file exists, run:

```bash
python scripts/validate_svg_icon.py path/to/icon.svg
```

The script checks common structural issues. It does not replace visual review.
