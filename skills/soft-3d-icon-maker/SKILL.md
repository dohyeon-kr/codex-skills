---
name: soft-3d-icon-maker
description: Create soft, rounded 3D object icon assets as transparent PNGs in a cute clay-render, toy-render, emoji-like, or sticker-style aesthetic. Use when Codex needs to generate one or more raster icons of any object category with pastel color blocking, inflated forms, soft studio lighting, polished material, and clean alpha backgrounds.
---

# Soft 3D Icon Maker

## Overview

Create soft 3D toy-render icons of any object, then deliver them as transparent PNGs by removing a flat solid-color background in post-processing. The visual icon comes from image generation; alpha handling is a cleanup step.

Read `references/style-guide.md` when composing detailed prompts or judging whether a result matches the intended look.

## Workflow

1. Identify the icon subject list, count, intended size, and whether each subject should be a separate PNG or arranged as one sheet.
2. Preserve the visual goal first: a polished soft 3D icon with rounded toy-like forms, clay/plastic material, readable object identity, and object-specific details. Do not simplify the icon into flat vector shapes just to make alpha extraction easier.
3. Use the `imagegen` skill for raster generation. Generate the finished-looking icon on a perfectly flat solid chroma-key background, not on a requested transparent or checkerboard background. Prefer one `image_gen` call per distinct icon when the user needs individual assets.
4. Copy the generated source image into the workspace, then use the imagegen chroma-key helper to remove only the solid background and write the final RGBA PNG.
5. Keep every icon centered with generous padding, a single object focus, no labels, no watermark, no background scene, and no cast shadow that depends on a floor.
6. Validate the final PNG: subject fidelity first, then style fidelity, then alpha channel. Alpha correctness is not a reason to accept a visually weak icon.

## Prompt Pattern

Use this prompt as the base and adapt only the subject-specific line:

```text
Create a single soft rounded 3D icon of <subject>.
Style: cute toy-like clay render, inflated rounded forms, smooth bevels, polished plastic-and-clay material, soft studio lighting, subtle ambient occlusion, tactile 3D depth, cohesive premium 3D icon pack aesthetic.
Subject fidelity: include the object's defining shapes, proportions, accessories, and color patches at a simplified but recognizable 3D icon level. Keep details chunky and molded, not flat or line-art.
Composition: centered isolated object, three-quarter view, readable at small sizes, generous transparent padding, no background scene.
Generation background: perfectly flat solid #00ff00 chroma-key background for later removal; one uniform color, no shadows, gradients, checkerboard, texture, reflections, floor plane, or lighting variation. Do not use #00ff00 anywhere in the subject.
Final output: RGBA PNG after chroma-key removal. Background/canvas pixels must be fully transparent with alpha 0. The icon object itself should remain opaque with alpha 1, with only antialiased edge pixels using partial alpha. Clean alpha edges, no colored backdrop.
Avoid: text, labels, logos, watermark, hard realism, flat vector style, thin details, sharp corners, busy texture, dramatic shadows, floor plane, cropped edges, checkerboard transparency pattern.
```

For a set, add:

```text
Keep all icons visually consistent: same camera angle, lighting direction, material softness, saturation level, scale, and edge thickness.
```

## Style Controls

- Use the user's requested object category directly. The style can apply to tools, food, office supplies, devices, toys, household items, nature objects, symbols, app concepts, or themed icon packs.
- Prefer simple forms over tiny literal detail, but keep enough object-specific features that the result clearly matches the requested object or reference. Make the object readable through silhouette, color blocking, large molded features, accessories, and pose.
- Use 3-5 main colors per icon, with soft warm whites, sky blues, coral reds, butter yellows, mint greens, lavender, tan, charcoal, or navy accents as appropriate to the object.
- Use a three-quarter camera angle for objects with depth; use near-front views only for very flat subjects such as maps or passports.
- Avoid realistic surface grime, complex micro-texture, photorealistic environments, and tiny text that image models will garble.

## Reference Fidelity

When the user provides a reference image, treat it as visual direction for the icon's subject design, not just as a style hint. Extract the large readable traits: silhouette, pose, major color blocks, accessories, facial expression, and material feel. Preserve those traits in soft 3D form before considering transparency cleanup.

For a lucky cat or maneki-neko reference, include the defining elements unless the user asks otherwise: rounded seated body, oversized rounded head, raised paw, closed smiling eyes, small pink nose, short molded whiskers, red collar, gold bell, gold coin or plaque, cream body, orange and dark gray calico patches, pink inner ears, and soft clay/plastic bevels.

## Transparent PNG Handling

Built-in `image_gen` does not expose a guaranteed native transparent-background control. For transparent PNG deliverables, the default path is:

1. Generate with `imagegen` on a flat solid chroma-key background.
2. Copy the generated source image from `$CODEX_HOME/generated_images/...` into the workspace.
3. Remove the chroma-key background with the imagegen helper.
4. Validate actual PNG alpha pixels.

Prompt the generation step like this:

```text
Create the icon on a perfectly flat solid #00ff00 chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Keep the subject fully separated from the background with crisp edges and generous padding. Do not use #00ff00 anywhere in the subject.
```

Run the imagegen chroma-key helper after generation:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input <source> \
  --out <final.png> \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

Use `#ff00ff` instead of `#00ff00` when the subject is green or contains green edge details.

Do not hand-draw, vectorize, or recreate the icon with Python/canvas/SVG just to satisfy alpha. If alpha removal fails but the visual icon is good, retry chroma-key removal settings or regenerate with a flatter solid background.

If a true/native transparency path is explicitly available, it is acceptable to request `RGBA PNG with background alpha 0` directly, but still validate the actual pixels before delivery. Do not use a visible checkerboard as a transparency substitute.

After background removal or native transparent generation, verify:

- The file is PNG with an alpha channel.
- All four corners are fully transparent, with alpha 0 rather than an opaque white or colored background.
- The main object is opaque, with alpha 1 across solid interior pixels.
- Semi-transparent edge pixels look smooth, not green-fringed.
- The icon still has soft object shading but no separate ground shadow.
- A visible checkerboard pattern is invalid. It means the checkerboard was rendered into the image pixels, not encoded as alpha.

## Delivery

Save final selected assets with descriptive names such as `soft-3d-camera.png`, `soft-3d-pencil.png`, or `soft-3d-teacup.png`. For sets, use a consistent filename prefix and report the saved paths.
