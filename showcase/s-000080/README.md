# S80 — Scene RenderStyle

Load `main.motionloom` for a 30-second comparison of 20 RenderStyle recipes.
Each recipe lasts 1.5 seconds (45 frames at 30 FPS), with a discrete cut and
synchronized number, name and description. Pause or seek to inspect a recipe.
Geometry, materials, camera, key light and background stay fixed; surface
shading, ambient multipliers and post grading change through RenderStyle.

These are 20 authored recipes built from four existing shading modes, not 20
new rendering algorithms. Physical means PBR shading, not photorealistic assets.
Matte Illustration and Muted Storybook are descriptive looks, not brush shaders.

| Time | Recipe | Main difference |
| --- | --- | --- |
| 0–1.5s | Physical / PBR | Original material response |
| 1.5–3s | Soft Stylized | Wrapped diffuse, reduced highlights |
| 3–4.5s | Toon 2-Step | Two light bands |
| 4.5–6s | Toon 3-Step | Three light bands |
| 6–7.5s | Toon 5-Step | Five light bands |
| 7.5–9s | Bright Anime | Four bands, vivid grade |
| 9–10.5s | Pastel | Soft contrast, desaturation |
| 10.5–12s | Matte Illustration | Matte surface, Reinhard rolloff |
| 12–13.5s | Vivid Graphic | Two bands, saturated surfaces |
| 13.5–15s | Muted Storybook | Muted warm grade |
| 15–16.5s | Warm Amber | Warm ambient and white balance |
| 16.5–18s | Cool Blue | Cool ambient and white balance |
| 18–19.5s | Low-Key | Lower exposure, deep shadows |
| 19.5–21s | High-Key | Bright diffuse, low contrast |
| 21–22.5s | Monochrome | Grey grade, original material response |
| 22.5–24s | Graphic Monochrome | Grey grade, two light bands |
| 24–25.5s | Soft Clay | Uniform clay material |
| 25.5–27s | Sculpt Clay | Clay with stronger form contrast |
| 27–28.5s | Rim Accent | Strong rim, darker interior |
| 28.5–30s | Dream Rim | Soft grade and luminous surface rim |

The planned Dream Glow was renamed Dream Rim: a native A/B at frame 877 with
style bloom intensity 0 versus 0.55 produced identical pixels on this dynamic
Scene path. This example therefore does not claim working bloom or retain a
no-op bloom setting. Investigating that runtime limitation is separate work.

For isolated baseline comparisons, the unchanged `physical.motionloom`,
`stylized.motionloom`, `toon.motionloom` and `clay.motionloom` remain available.

Each file uses a Scene-level RenderStyle reference and shared RenderQuality
definition. No World DSL tag, remote assets or pre-rendered style images are
used. The styles execute on the shared native WGPU / WASM WebGPU renderer.

The files are deliberately standalone: cross-Scene post-process transitions
are not required to compare these surface styles. They require a WASM build
that includes dynamic Scene RenderStyle support; an older published bundle
cannot parse them. No new WASM API or renderer feature is needed for these
additional recipes.

## Verification

- Analyzer: clean; schema.json regenerated from the final main.motionloom.
- Native GPU: representative frames at `22 + 45 * index`, for index 0–19.
- Browser WebGPU: 20 distinct scene-only pixel hashes (labels excluded).
- Browser WebGPU: exact output checks on both sides of all 19 cuts (38 frames),
  plus 9 random/backward/end-to-start seeks and direct canvas presentation.
- Retained 3D geometry resources: 14 before and after the style/seek sequence.
  This is not a total-memory measurement or a cross-device FPS guarantee.
- No changes to S1–S79, engine code or the standalone S80 comparisons.
