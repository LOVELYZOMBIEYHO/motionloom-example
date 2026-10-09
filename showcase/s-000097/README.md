# S97 — Winding Mountain Road

`main.motionloom` is a 24-second, 1920×1080, 24 fps forest exploration. It
keeps S97's road, carved mountain slope and existing camera route, using S96
as the material-quality reference. Every runtime asset is local to S97;
S96 and S99 source files are unchanged.

## Forest and surface detail

- **38 full 3D roadside trees** keep the S99 tapered branches, petioles and
  2,200 curved leaves per tree. Bark has a local circular UV wrap and the
  leaves have individual surface UVs with fine venation. Geometry and normals
  match the prior S99-derived GLBs exactly; detailed texture data replaces
  their plain colors.
- **6,029 distant trees** retain S96's alpha-masked whole-tree crossed cards
  and add three curved, tilted foliage layers using the same species texture.
  Transparent branch edges provide overhead coverage without solid crown caps.
  These are simplified distant trees, not detailed individual leaves or
  automatic runtime LOD. The original 2,048 core tree transforms
  are preserved; another 4,019 trees extend coverage beyond the old terrain edge.
- **16,000 grass tufts** use the two original S96 alpha-masked grass textures,
  positioned with the native Scatter sampling rules and the original exclusion
  map. The road remains clear. The grass and distant trees are static material
  batches rather than thousands of small runtime draws.
- **Smooth float32 terrain** keeps the carved road bench and slope while
  removing the old RGBA8 heightmap's visible staircase. All 2,978 shared
  boundary vertices, normals and UVs match the surrounding terrain ring.
  Original S96 grass-ground color and normal textures repeat every five
  site metres, with a restrained material tint. The invisible quarter-LOD
  TerrainAsset remains only as the
  placement surface for the rock Scatter.
- **Mossy rock textures** and dry asphalt with square texture tiles replace
  the plain ground and boulders. Warm sunlight, an open sky environment and
  restrained aerial haze supply the current illumination.

The distant forest contains 1,326,380 triangles in three material primitives;
the understory contains 64,000 triangles in two. The near trees contain
3,077,240 triangles in total. Static batching reduces draw submissions; it
does not remove geometry or establish a measured realtime/browser frame rate.

## Camera exploration

| Time | View |
| --- | --- |
| 0–4 s | Aerial overview descending to an oblique forest view |
| 4–11 s | Approach the selected roadside tree and surrounding grove |
| 11–20 s | Orbit across the road-facing side to inspect trunk, branches and crown |
| 20–24 s | Move toward the upper branches and individual leaves |

The camera's position, target and FOV curves are unchanged from the previous
24-second exploration. The selected tree is original seed-97 placement 107.
`authoring/camera-exploration.json` records that earlier route and source
fingerprint. The current forest detail selection is recorded separately in
`authoring/s96-forest-layout.json` and `authoring/s96-tree-layout.json`.

Current lighting captures and analysis are in `evidence/lighting/`.
The earlier material study remains in `evidence/s96-quality/`; earlier route
captures in `evidence/camera-exploration/` and tree trials in
`evidence/tree-replacement/` refer to their own source fingerprints.
Each `source-before.motionloom` is a historical snapshot relative to the S97
root, not a standalone scene in its evidence folder. DSL analysis confirms
syntax and supported behavior; visual review is separate.

## Shared daylight lighting

The same main DSL supplies both WGPU Preview and Weaver:

- `DirectionalLight s97_sun` emits warm sunlight along `[-0.56,-0.66,-0.50]`
  at intensity `3.2`. Preview shadow strength is `0.80`; Weaver uses physical
  shadow occlusion.
- `EnvironmentLight s97_daylight` uses the local
  `assets/environment/sunny-forest-sky.png` for visible sky and environment
  illumination at intensity `0.32`. Rotation `-116.5` approximately aligns
  the image's sun azimuth with the directional key light. This is an LDR
  panorama, not calibrated HDR solar radiance.
- Bounded `AtmosphereFog` at density `0.008` adds aerial depth without fogging
  the sky background. `AmbientOcclusion` strengthens preview contact shading;
  Weaver derives occlusion from traced rays and ignores preview-only AO.
  Volumetric shafts are omitted: the current preview implementation produced
  excessive additive haze in this scene.
- `filmic_physical_v1` and `filmic_aces_v1` retain neutral style specular,
  ambient color and white balance, so Weaver can accept the authored style
  explicitly. Imported material roughness and specular factors still apply.

There is no closed sky sphere in the main scene. An opaque emissive sphere
blocks external environment and sun rays in Weaver even when preview omits
its shadow. The original extracted sky asset is retained only for historical
study. Both renderers consume the same lighting, but preview approximates
indirect illumination while Weaver traces it; their pixels and shadow softness
are not expected to match exactly.

Use the native `cinematic` profile to enable preview screen-space GI,
reflections and a 2048-pixel shadow map. It is a host setting, separate from
DSL anti-aliasing quality. Weaver smoke evidence is a low-sample compatibility
check, not a converged offline beauty render.

## Rebuild local assets

Run from this S97 directory, in this order:

```sh
python3 assets/reference-forest/extract_reference_forest.py
python3 authoring/s96_terrain.py
python3 authoring/s96_near_tree.py
python3 authoring/s96_understory.py
python3 authoring/s96_forest.py
python3 authoring/s96_tree_batch.py
```

The first two scripts read S96's licensed GLB to extract source data; they
never modify it. Playback needs no sibling showcase. The near-tree script
uses only S97's local preserved S99 cages, derived GLBs and texture images.
`tree-layout-source.json` preserves the original 2,048 seed-97 transforms.
`--near-radius` on `s96_forest.py` controls the authored roadside detail area;
rebuild the static tree batch afterward. This is an authoring choice, not
camera-driven runtime LOD.

From the workspace root:

```sh
motionloom/target/debug/examples/authoring_report \
  motionloom-example/showcase/s-000097/main.motionloom wasm-webgpu
cargo run --manifest-path motionloom/Cargo.toml --release -p motionloom \
  --example wgpu_live_preview -- --profile cinematic \
  motionloom-example/showcase/s-000097/main.motionloom
```

To render the same scene offline, from the workspace root:

```sh
cargo run --manifest-path motionloom/Cargo.toml --release -p motionloom \
  --features weaver --example weaver_frame -- \
  motionloom-example/showcase/s-000097/main.motionloom \
  --scene-id S97WindingRoad --style s97_forest_pbr --frame 192 \
  --size 640x360 --samples 64 --out /tmp/s97-weaver
```

## Asset credits and authoring evidence

S96-derived tree, grass, ground, rock and historical sky images come from
**"landscape forest & mountains" by dasy444**, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source:
[Sketchfab model](https://sketchfab.com/3d-models/landscape-forest-mountains-94809d21d7aa4cfe9b658a111b35a42c).
Extraction, normalization, placement, added foliage geometry and static batching
are S97 changes. Original embedded image bytes remain unchanged. Detailed
credits, material mappings and preservation checks live in
`assets/reference-forest/README.md`, `provenance.json` and `validation.json`.

The current sunny sky is reused byte-for-byte from MotionLoom showcase S77.
Embedded C2PA metadata identifies AI generation by gpt-image 2.0 / OpenAI
Media Service API, dated 2026-08-30. This metadata was inspected, not
cryptographically verified. The asset is separate from the S96 CC BY credit;
its source and fingerprint are recorded in `authoring/lighting-source.json`.

The new opaque leaf-surface texture `assets/materials/s97-leaf-detail.png`
was generated with the built-in image_gen tool. Its prompt asks for a flat,
edge-to-edge broadleaf surface with a vertical central midrib, fine secondary
veins and natural moss/olive-green variation under diffuse neutral light;
the 3D mesh supplies the leaf outline and curvature. The prompt and output
fingerprint are in `authoring/leaf-texture-provenance.json`. Existing S97 bark
and asphalt images remain unchanged. No texture is described as a measured
physical scan.

Geometry, texture and UV checks are recorded in
`authoring/s97-near-tree-textured-report.json`,
`authoring/s96-terrain-provenance.json`,
`authoring/s96-understory-report.json` and
`authoring/s96-tree-batch-report.json`.

## Earlier trials

`aerial-comparison.motionloom` retains the 12-second aerial trial of 2,048
full S99 trees. `stress-10760.motionloom` retains the 10,760-tree full-detail
stress scene, with 871,344,800 tree triangles and the previous aerial camera.
`main2.motionloom` retains the earlier primitive-crown version. These comparison
files are unchanged by the S96 material study.

The exact local S99 cages are preserved in
`assets/trees/s99-street-tree.motionloom`; six original derived GLBs were
exported with MotionLoom's `extract_scene_geometry()` and
`export_scene_glb()` APIs. `authoring/s99-tree-provenance.json` records that
trial. Its reproduction script `authoring/s99_forest.py` is historical and
replaces the tree setup when run; use a separate output document to preserve
the current S96-based main scene. The older camera/road fitting tools and
reference image remain available under `authoring/` and `reference/`.
