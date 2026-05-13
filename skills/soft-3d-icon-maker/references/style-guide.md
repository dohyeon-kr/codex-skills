# Soft 3D Object Icon Style Guide

## Core Look

- Rounded, inflated, toy-like 3D objects with chunky proportions.
- Smooth clay/plastic material with low-to-medium gloss.
- Pastel color blocking with a few darker accents for readability.
- Soft studio lighting from the upper left or front-left.
- Subtle ambient occlusion inside seams and under overlapping parts.
- Clean isolated object silhouette that remains readable at small icon sizes.
- RGBA PNG output with background/canvas alpha 0, generous padding, and no environment.

## Composition

- Use one object per icon unless the user asks for a grouped object.
- Center the object and keep it fully inside frame.
- Prefer a three-quarter view for objects with depth.
- Use front or near-front view for flat objects, symbols, screens, papers, and signs.
- Preserve recognizability by exaggerating the largest identifying shapes.

## Color

- Use 3-5 colors per icon.
- Prefer soft whites, butter yellow, coral, sky blue, mint, lavender, peach, tan, navy, and charcoal.
- Keep saturation cheerful but not neon.
- Avoid monochrome palettes unless the user explicitly requests one.

## Detail Level

- Replace tiny text with simple emblem-like marks or raised grooves.
- Use large seams, bevels, buttons, handles, holes, or bands as readable features.
- Avoid busy realistic texture, grime, scratches, labels, brand marks, and micro-detail.

## Lighting And Edges

- Use soft shadows only as object self-shadowing, not a ground shadow.
- Keep edges crisp enough for alpha extraction.
- Keep solid object interiors fully opaque with alpha 1; only antialiased edge pixels should use partial alpha.
- Do not include an opaque white, colored, gradient, studio, or square-tile background.
- Never use a gray checkerboard pattern to represent transparency. A checkerboard visible in the PNG is a failed output, not alpha transparency.
- Avoid transparent, glassy, hairy, smoky, liquid, or fuzzy materials unless the user explicitly requests them; these are harder to cut out cleanly.

## Negative Prompt Additions

Use these when quality drifts:

```text
Avoid flat vector illustration, photorealistic product photo, hard metal realism, busy background, floor plane, cast shadow, text, logo, watermark, thin outlines, sharp spikes, tiny labels, cropped edges, green fringe, jagged alpha edge, checkerboard transparency pattern.
```
