# S97 — Winding Mountain Road

`main.motionloom` is a 12-second, 1920×1080, 24 fps aerial drift rebuilt from
`reference/reference.png` (a photo of hairpin switchbacks cut into a forested
mountainside). Everything is authored from primitives — a heightfield
`TerrainAsset`, a shared `CurveAsset` with six `SweepAsset` results, and `CompoundAsset`
trees — with no imported GLBs. Four generated base-color textures provide the
first authored-material checkpoint; geometry, placement, lighting and camera
remain entirely MotionLoom-authored.

## Why the document is authored at 1:20

The scene is built in "site metres" (a 254×143 m footprint) but emitted at
`SCALE = 0.05`. The engine's directional-light shadow volume is a fixed 28 m
box that only auto-fits rigid scenes under 14 m, and `Camera3D` clamps its
field of view to a 10° minimum, which forces the aerial camera ~41 m away. At
1:20 everything stays inside the shadow volume, AO and shadow texels stay
crisp, and the projection, framing and depth resolution are unchanged because
all ratios are preserved.

## Contents

- `assets/terrain/s97-height.png` — 954×537 heightmap (8-bit RGBA, `lod="full"`,
  chunks `[8,5]`). The generator bakes the carved road bench, cut and fill
  blends into the map.
- `assets/terrain/s97-rock-density.png` — linear placement mask derived from
  distance to the road cut and cut-bank height; it concentrates authored rock
  variants around exposed slopes without storing hundreds of Model nodes.
- `assets/materials/*-basecolor.png` — ImageGen-assisted, source-neutral
  forest ground, asphalt, bark and foliage albedo references. They contain no
  baked lighting by design. They are base color only, not fabricated normal,
  displacement, roughness or AO measurements.
- `assets/materials/asphalt-roughness.png` — an explicitly authored linear
  grayscale roughness mask derived from the asphalt study. The road selects
  `roughnessChannel="luminance"`, exercising the same typed channel-remap
  contract used by native/WASM preview and Weaver.
- Road — one 175-control-point `CurveAsset`, simplified from 899 dense fitted
  samples with a maximum 0.004 scene-unit centreline deviation, drives six
  reusable `SweepAsset` definitions: crowned
  asphalt (#63696F, 5.5 m wide), two painted edge lines, a broken centre line,
  and raised metallic guardrails. Paint is lifted 0.24 m so the renderer can
  resolve it at this viewing distance.
- Forest — six tree assemblies (narrow/tall/widow conifers, two-blob and
  three-blob broadleaves) combining cylinder trunks with low-resolution cone
  and sphere foliage. One deterministic `Scatter` places 10,760 weighted
  variants on the TerrainAsset, using a generated linear exclusion mask to
  keep the road corridor clear. Generated instances have runtime identities;
  the document does not contain 10,760 authored `Model` ids.
- Cut banks — three low-poly rock variants use a second deterministic Scatter
  driven by the generated density map. This adds 720 pieces of slope detail
  without a second explicit object list.
- Lighting — warm sun with shadows (0.82 strength), cool fill, AO 0.55,
  ambient 0.21, subtle linear aerial haze, ACES tone mapping, and ultra TAA
  with SMAA fallback. The Scene explicitly selects `s97_forest_pbr`; the
  declared style is not left as an unused resource.

## Authoring pipeline (`authoring/`)

- `analyze_reference.py` — dependency-free PNG codec, brightness masks,
  largest-component filtering, chamfer distance transform and a ridge walk
  that traces the road centreline from the photo (`trace`/`mask` CLI).
- `road-path.json` — the 105 traced waypoints in image pixels plus measured
  half-widths; `road-offsets.json` holds per-waypoint corrections.
- `build_scene.py` — generates the heightmap and forest-exclusion mask, carves
  the bench, simplifies the fitted 3D centreline, emits shared curve/profile
  sweeps, and writes the compact Scatter-based
  `main.motionloom`. It also has `probe` and `markers` modes for calibration.
- `fit_road.py` — renders the probe ribbon, measures its offset from the
  traced centreline, and iterates the per-waypoint corrections back into
  `road-offsets.json` (currently 3.5 px mean residual at 1920×1080).
- `camera.json` — fitted camera parameters (distance 807.3 site m → 40.4 m
  scaled, fov 10°, 5° tilt).

Rebuild and render:

```sh
python3 motionloom-example/showcase/s-000097/authoring/build_scene.py
anica/target/release/examples/render_file_frame \
  motionloom-example/showcase/s-000097/main.motionloom /tmp/frame.png 0 gpu
```

`authoring_report` (below) validates the DSL; it does not judge reference
likeness.

This revision is the S97-B base-color checkpoint for the native outdoor-quality
ladder. S97-A established compact deterministic placement; S97-B adds reusable
albedo detail while keeping honest scalar roughness values. The next visual
checkpoint should use measured or deliberately authored normal/ORM data rather
than deriving fake physical maps from color.

The Scatter migration first reduced `main.motionloom` from 24,352 lines /
2,686,806 bytes / 10,764 authored Models to 17,451 lines. The subsequent
CurveAsset/SweepAsset migration reduces it again to 383 lines while retaining
seven authored Models and two Scatters. Asphalt, edge paint, exact-distance
dashes and both guardrails now reference one spatial curve; the DSL contains
no expanded road vertices, faces or duplicated guardrail paths.

The four base-color prompts requested seamless, orthographic material studies
under diffuse neutral lighting: mossy forest soil with leaf litter, weathered
mountain asphalt, mature conifer bark, and dense mixed forest foliage. ImageGen
outputs were copied into `assets/materials/`; the original generated files are
retained outside the repository by the authoring environment.
The asphalt roughness pass reused the asphalt image as a spatial reference,
requested flat grayscale data with a roughly 0.72–0.92 dry-road range, and was
iterated once after inspection; its measured channel mean is approximately
0.775. It is deliberately authored data, not a claimed physical scan.

```sh
anica/target/release/examples/authoring_report \
  motionloom-example/showcase/s-000097/main.motionloom
```
