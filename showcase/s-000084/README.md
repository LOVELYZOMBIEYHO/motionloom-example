# S84 — Cel Shading comparison

20 seconds, 30 FPS, 1980×1080. The same geometry, camera and lighting are used
for the first four comparisons:

- 0–3s: Physical.
- 3–6s: Toon.
- 6–9s: Cel Shading with black geometry outlines.
- 9–12s: Cel Shading without outlines.
- 12–20s: Cel Shading with camera distance changes and a moving occluder.

Character1 uses its original Quaternius CC0 Walk_Loop. All character references
are GitHub raw URLs; browser hosts must preload ModelAsset and AnimationAsset.
The primitive bust illustrates a masked face outline, a warm face-shadow ramp
and a tangent hair highlight. Its authored control PNG is also embedded as a
data URL, so an unpublished asset URL cannot prevent local preview.
Original showcases and GLB files are unchanged.

Requires the updated MotionLoom native or WASM GPU renderer. These are geometric
silhouette outlines, not screen-space edge detection. Control R is outline
width, G is the artist-authored face threshold/SDF ramp, B is hair-highlight
weight. This demo map is an original synthetic test map, not a realistic face.
No transparent-hair-card outline or automatic face-map generation is claimed.

## Verification (2026-09-04)

- Native library: 533 tests passed.
- RenderStyle integration: 14 tests passed, including the opaque Character1 GLB outline regression, native GPU masks, face
  shadow maps, disabled outlines, invalid slots and S1–S79 parsing.
- cargo fmt --check and clippy --all-targets -- -D warnings passed.
- Release WASM rebuilt; actual WebGPU browser rendered frames
  30, 120, 210, 300, 420, 510, then 210 again. Repeated-frame pixels matched.
- Native and WASM frame 210 matched exactly in the 960×370 3D comparison crop
  (y=110–479, RGB); text regions were excluded because host font loading differs.
- Browser warm render/readback observations were 5.6–14.7 ms; first frame
  including initialization was 1231 ms. These are not sustained FPS/GPU timings.

Performance scope: outlines reuse existing instanced/skinned draw resources
but add one geometry pass. A cached 12-byte outline-normal channel is added
per vertex and one control texture binding per material draw. The existing
draw_calls statistic counts input draws, not all shadow/outline pass submissions.
No claim of zero overhead or production-scale crowd performance is made.
