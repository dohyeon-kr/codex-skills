---
name: soft-3d-icon-maker
description: Create soft, rounded 3D object icon assets as transparent PNGs in a cute clay-render, toy-render, emoji-like, or sticker-style aesthetic. Use when Codex needs to generate one or more raster icons of any object category with pastel color blocking, inflated forms, soft studio lighting, polished material, and clean alpha backgrounds.
---

# Soft 3D Icon Maker

## Overview

Create transparent PNG icons of any object in a soft 3D toy-render style: rounded shapes, chunky proportions, pastel color blocking, subtle bevels, gentle studio lighting, and clean object silhouettes.

Read `references/style-guide.md` when composing detailed prompts or judging whether a result matches the intended look.

## Workflow

1. Identify the icon subject list, count, intended size, and whether each subject should be a separate PNG or arranged as one sheet.
2. Use the `imagegen` skill for raster generation. Prefer one `image_gen` call per distinct icon when the user needs individual assets.
3. Ask for transparent PNG output. If the active image-generation path does not support native transparency, generate on a perfectly flat chroma-key background and remove it with the imagegen chroma-key helper.
4. Keep every icon centered with generous padding, a single object focus, no labels, no watermark, no background scene, and no cast shadow that depends on a floor.
5. Validate the final PNG: alpha channel exists, corners are transparent, edges are clean, subject is not cropped, and the style remains consistent across the set.

## Prompt Pattern

Use this prompt as the base and adapt only the subject-specific line:

```text
Create a single soft rounded 3D icon of <subject>.
Style: cute toy-like clay render, inflated rounded forms, smooth bevels, pastel color blocking, polished plastic-and-clay material, subtle ambient occlusion, soft studio lighting, crisp silhouette, cohesive premium 3D icon pack aesthetic.
Composition: centered isolated object, three-quarter view, readable at small sizes, generous transparent padding, no background scene.
Output: transparent background PNG with clean alpha edges.
Avoid: text, labels, logos, watermark, hard realism, flat vector style, thin details, sharp corners, busy texture, dramatic shadows, floor plane, cropped edges.
```

For a set, add:

```text
Keep all icons visually consistent: same camera angle, lighting direction, material softness, saturation level, scale, and edge thickness.
```

## Style Controls

- Use the user's requested object category directly. The style can apply to tools, food, office supplies, devices, toys, household items, nature objects, symbols, app concepts, or themed icon packs.
- Prefer simple forms over literal detail. Make the object readable through silhouette, color blocking, and a few large features rather than tiny marks or text.
- Use 3-5 main colors per icon, with soft warm whites, sky blues, coral reds, butter yellows, mint greens, lavender, tan, charcoal, or navy accents as appropriate to the object.
- Use a three-quarter camera angle for objects with depth; use near-front views only for very flat subjects such as maps or passports.
- Avoid realistic surface grime, complex micro-texture, photorealistic environments, and tiny text that image models will garble.

## Transparent PNG Handling

If native transparent output is available, request `transparent background PNG` directly.

If using chroma-key removal, include this in the generation prompt:

```text
Place the icon on a perfectly flat solid #00ff00 chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Do not use #00ff00 anywhere in the subject.
```

After background removal, verify:

- The file is PNG with an alpha channel.
- All four corners are fully transparent.
- Semi-transparent edge pixels look smooth, not green-fringed.
- The icon still has soft object shading but no separate ground shadow.

## Delivery

Save final selected assets with descriptive names such as `soft-3d-camera.png`, `soft-3d-pencil.png`, or `soft-3d-teacup.png`. For sets, use a consistent filename prefix and report the saved paths.
