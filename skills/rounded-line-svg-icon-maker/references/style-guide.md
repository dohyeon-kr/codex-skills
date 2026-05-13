# Rounded Line SVG Icon Style Guide

## Target Aesthetic

- Monochrome outline icon set.
- 24x24 viewBox with an optical 20x20 drawing area.
- Rounded terminals and joins.
- Stroke weight around 2px.
- Minimal detail, high recognizability, and strong small-size readability.
- Neutral UI icon tone, similar to Lucide, Feather, Heroicons outline, or modern app toolbar icon sets.

## Geometry

- Use simple strokes first: lines, polylines, circles, rounded rectangles, and compact paths.
- Place major vertical and horizontal strokes on whole or half coordinates.
- Keep icon bounds usually between x/y 3 and 21.
- Use symmetry where the concept supports it, but adjust optically rather than forcing mathematical symmetry.
- Use arcs and Bezier curves sparingly; when used, keep them smooth and readable.

## Stroke

- Default root attributes:

```svg
fill="none"
stroke="currentColor"
stroke-width="2"
stroke-linecap="round"
stroke-linejoin="round"
```

- Do not use filled paths to fake stroke weight.
- Do not mix multiple stroke widths unless the user explicitly asks for expressive variation.

## Detail Density

- A simple icon should have 1-3 elements.
- A medium object icon should have 3-6 elements.
- Avoid more than 8 visible stroke elements unless the concept genuinely needs a grid or list.
- Replace literal details with symbolic marks. For example, a document image can use a rectangle plus a small circle and mountain stroke.

## Variants

- `off`: add a diagonal slash.
- `add`: add a plus sign near the key object.
- `remove`: add a minus sign.
- `check`: add a small check mark.
- `alert`: add a tiny dot or exclamation stroke.
- `filled`: avoid unless the user explicitly asks; this skill defaults to outline icons.

## Common Mistakes

- Adding a white or transparent background rectangle.
- Using `stroke="#000"` instead of `currentColor` in reusable UI assets.
- Leaving generated SVG path data with many decimal places.
- Using text nodes for letters or labels.
- Drawing too many tiny internal details that disappear at 16px.
- Using square caps or miter joins, which breaks the rounded style.
