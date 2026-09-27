# AgentIsOK dimensional material study

Generated with the built-in image generator on September 27, 2026. The selected studio concept is [agentisok-studio-concept.png](agentisok-studio-concept.png). It informed the satin gold, emerald finish, and edge lighting of the scalable SVG masters. This is an exploration render; the SVG masters are defined by the existing letter geometry in [generate.py](generate.py).

The input logo was the original flat mark, now preserved as [agentisok-mark-light-flat.png](agentisok-mark-light-flat.png). The second input was Univeracity's gold/green logo as a material reference. Absolute input paths below record the generation environment; the Univeracity reference is not bundled in this repository.

## Material prompt

```text
Use case: style-transfer / logo-brand.
Asset type: polished dimensional logo master for AgentIsOK.
Input images: Image 1 (/projects/agentisok/assets/brand/agentisok-mark-light.png) is the exact logo edit target. Image 2 (/projects/univeracity/assets/logo-on-white.png) is a reference only for gold and emerald materials and clean beveled edges.
Primary request: Polish Image 1 while preserving its recognizable composition and exact letter shapes: gold uppercase A and I on the top line; deep forest-green uppercase O and K on the bottom line; emerald check sweeping through the gap between the lines and rising to the upper right. Keep the A, I, O, K, and check silhouettes, letter spacing, optical weight, relative sizes and orthographic/front-facing composition as close to Image 1 as possible. The I is a simple vertical bar. Do not join I and K. The check must remain distinct from all four letters.
Style/materials: beautifully crafted premium shallow-relief emblem; soft satin metallic gold for AI, rich dark green graphite-like satin for OK, emerald enamel for the check. Subtle 3D depth, precise narrow chamfered bevels, coherent highlights from a soft light above-left, smooth tonal surfaces. Front faces remain broad and readable; extrusion is restrained and visible along lower-right edges. Match the polished gold and green family in Image 2 without copying its U logo. Avoid excessive glossy reflections or busy textures.
Composition: one centered standalone mark, front view without perspective rotation, generous equal clear margin, no wordmark or slogan, no props or environment. High-resolution clean edges.
Background: genuinely transparent alpha background. No checkerboard drawn into the image, no white backdrop, no floor, no ground shadow.
Text (verbatim): top "AI", bottom "OK" only, no extra text.
Constraints: Preserve the existing AgentIsOK identity. No new shapes, shields, circles, sparkles, rays, gradients outside the mark, lens flare, heavy shadow, mockup framing, or watermark. The green check crosses the interline space in the same position and direction as the original.
```

## Edge-cleanup trial

A second edit explored cleaner export edges. The initial material study was retained as the concept; the SVG masters provide deterministic edge construction.

```text
Use case: precise-object-edit / logo-brand.
Edit target: the supplied polished dimensional AgentIsOK mark.
Primary request: Clean the transparent export edges ONLY. Remove every stray yellow, red, green or white pixel, speck, fringe, halo or detached fragment outside the actual letter and check silhouettes. The current export has some colored flecks around the gold A/I and in the otherwise empty area around the check; all of those must become fully transparent. Make the edges impeccably crisp and smoothly anti-aliased.
Preserve exactly: the four letters AI above OK, spacing, shapes, green check position, gold metallic face material, dark green OK material, emerald check material, chamfer widths, shallow 3D depth, highlights, orthographic front view, size and composition.
Background: actual alpha transparency, no drawn checkerboard or solid backdrop.
Constraints: This is a meticulous cleanup pass, not a redesign. No new text, shadows, glows, objects, textures, or extra geometry. Broad clean faces, precise polished bevels, and clean holes/counters. Preserve the intended low-contrast satin surface shading, but eliminate all image-generation debris beyond the contours.
```
