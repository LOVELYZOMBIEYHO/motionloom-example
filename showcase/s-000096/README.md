# S96 — Landscape, Forest and Mountains

`main.motionloom` is a 15-second, 1920×1080, 24 fps morning → dusk → night montage of `assets/landscape_forest__mountains.glb`. Geometry is imported; this example teaches camera sequencing, lighting, render styles and material binding.

`S96Landscape` contains three 5-second `Sequence` blocks with `out="hide"`, each owning a camera, light rig and model instance. Camera curves use local Sequence time, repeating the same low meadow flight. `AnimationTarget` switches `renderStyle` at 5 and 10 seconds (frames 120 and 240).

The three styles use physical shading, specular 0.20 and TAA Ultra with SMAA fallback. Morning uses warm neutral illumination; dusk adds amber grading and bloom 0.14; night uses blue illumination and zero styled bloom. A texture Scene plus `MaterialBinding` replaces night sky-dome material `Material.011` with `texture/s96-night-sky.jpg`. This is texture replacement, not a physically simulated day/night sky. A fourth neutral `s96_weaver` style exists only for the opt-in Weaver offline path tracer, which rejects the preview-only `specular="0.20"` override.

Every camera declares physical depth of field (`depthOfField`, `focusDistance="20"`, `focalLength="25.06"`, `fStop="4"`, `maxBlur="10"`) so the immediate preview matches the physical thin-lens framing Weaver derives from the same FOV.

The camera keeps the original montage's slow per-second pace: within each short segment it drifts only a very short distance from `(2.5, 0.85, 7.5)` instead of rushing the whole path, with animated target and field of view; landscape geometry stays stationary. The document is maintained directly in `main.motionloom`.

## Asset credits

`assets/landscape_forest__mountains.glb` — "landscape forest & mountains" by
[dasy444](https://sketchfab.com/dasy444), downloaded from Sketchfab, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source:
<https://sketchfab.com/3d-models/landscape-forest-mountains-94809d21d7aa4cfe9b658a111b35a42c>.
The night-sky replacement `texture/s96-night-sky.jpg` is a derivative of the
model's own sky painting.

Run from the Anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000096/main.motionloom
```

`schema.json` is generated from the current executable document. Analysis checks DSL structure, not visual quality or runtime performance.
