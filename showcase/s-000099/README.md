# S99 — HOUSE 99

`main.motionloom` presents a modern city residence in 44 seconds at 24 fps.
Its logical canvas is 3840×2160 and its current output is 1920×1080.
`SHOWCASE99` combines a native 2D plan, rising walls with actual door
and window voids, a roof assembly, furnished interior cameras, and a dusk
exterior. Architecture, furniture, lamp housings and planting are controlled
directly by MotionLoom DSL through `GeometryAsset`, `MeshAsset`, `Vertex`,
`Face`, `CompoundAsset`, `Instance` and `Model`. Native meshes give the planting
branch structure and individually shaped leaves; native compound geometry gives
the surrounding buildings recessed windows, balconies and roof equipment.
There are no imported model files or external model-editing steps; Blender is
not used or required.

## Compact DSL

Before the realism revision, the compact source had **6,223 lines and 12.03 MB**,
down from the earlier 9,024-line, 18.06 MB version. As in S98, identical
geometry is declared once and referenced by multiple material-bound
`MeshAsset`s. The east street tree reuses the west tree's material-batched
canopy with a 137° rotation; the eight garden planters use four deterministic
forms twice each. This reduces explicit botanical cages from 78 to 52 while
retaining all **5,690 visible leaves** and, in that historical revision, the same
386,810 visible triangles.
Leaves remain curved native MeshAsset surfaces; no generic procedural tree or
external model replaces them. The four background buildings now combine
ordinary boxes by material into 44 native MeshAsset Models; rounded and
rotated parts stay in their CompoundAssets. Historical strict WGPU draw calls
fell from 2,442 to 770 without changing that revision's visible triangle count. City mesh data
adds about 2.33 MB compared with the 9.69 MB geometry-reuse source, but the
previous batching revision made the document 606 lines shorter and improved
1080p playback. The material revision adds 51 finish/UV declarations; the indoor
lighting revision adds fixed fixtures and optional bake/mirror bindings. The
realism revision adds the bounded furniture geometry and lighting/material
controls described below; the figures above are historical, not its final
render counters. The current source has **35,866 lines and 13.94 MB**
(13,937,461 bytes). Run `scripts/build_showcase.py` followed by
`scripts/realism_upgrade.py` to rebuild the current DSL. The older
`scripts/verify_optimization.py` records the earlier topology counts and locked
tag stream; `scripts/verify_realism_upgrade.py` protects the current revision
against its separate immutable baseline.
No per-leaf `Instance` or distance LOD was added; all leaf silhouettes remain.

[Archived native 4K showcase](evidence/showcase99-4k.mp4), recorded before the
material/HDR, indoor-lighting and realism revisions. The current revision uses
selected stills; no complete video is produced.

![HOUSE 99 exterior from the archived indoor-lighting review](evidence/lighting-upgrade/after/frame-0360.png)

## Furniture, material layers and finite lights — 2026-10-06

The new revision rounds chair and stool shells, gives sofa pads and pillows
bounded seams/compression, and adds shallow authored folds to the bed throw and
towel. Eleven shared GeometryAssets affect 22 existing furniture models, with
15,822 unique UV-chart vertices and 27,576 unique triangles. All model transforms,
the house, planting, city context, seven cameras, seven animation channels and
the 2D plan remain protected. The sofa-seat underside alone has an approved
30 mm extension to meet its base; visible tops and footprints stay fixed.

Existing CC0 PBR maps retain their metre-scaled UVs. Opt-in sheen supplements
fabric and a restrained clearcoat supplements wood; the fabric source remains
a fine polyester weave, not a scanned linen material. The sun has a 0.5° disk,
the two pendants are downward 0.18×0.18 m rectangle sources, and four local lamps
have 0.025 m source radii. Independent light shadows and a new diffuse bake use
these controls with the existing day/dusk timing. Between 37 and 40 seconds,
the `#FFF4E4` sun changes intensity 2.8→0.28 and the HDR environment 1.1→0.2.
Each pendant changes 37.03704→185.18519, equivalent to 1.2→6 after its 0.0324 m²
area factor; living, primary-bedroom and bathroom lamps change 1.8→7, 1→4 and
1.5→6. Light colors in `perLight` mode use canonical RGB and exact sRGB-to-linear
conversion consistently in rendering and baking. All 22 existing PBR/HDR files,
including previews and provenance, retain their archived file hashes.
Authored folds are not cloth
simulation, and finite-source real-time shadows remain bounded approximations.

[Realism evidence and rebuild contract](evidence/realism-upgrade/README.md)
records the exact baseline, furniture allowlist, material/light values and
selected 1920×1080 Cinematic still workflow. Semantic preservation passes all
501 models, with geometry changes limited to the 22 allowlisted models and
479 unchanged models. The final review completed 16 fixed 1920×1080 Cinematic
before/after stills, with a pixel-identical opening plan, and three twelve-frame
consecutive samples. The two-state bake and all 11 generated files match the
final scene and provenance. Native preview successfully sought the kitchen,
bathroom and dusk frames. There were 735 passing tests and five ignored library
tests, plus successful WASM, Weaver-feature and integration-target compilation.

[Current before/after comparison](evidence/realism-upgrade/before-after.png),
[short temporal review](evidence/realism-upgrade/temporal-contact-sheet.png) and
[completion record](evidence/realism-upgrade/completion-report.json) are separate
from the archived image above. Fixed 1080p Balanced samples show 1.69–2.70×
submission cost versus the archived scene; all 49 measured shadow views were
cached. These CPU/queue/submission observations do not certify playback FPS.
The active material layers are implemented in the native/WASM renderer;
WASM runtime pixels were not tested, and the Weaver offline exporter explicitly
rejects active sheen/clearcoat. No full movie was exported.

## Material and HDR revision — 2026-10-06 (archived evidence)

Wood, stone, plaster and upholstery now use matching CC0 PBR datasets rather
than base-colour-only finishes. Wood, floor stone and fabric share colour,
OpenGL normal and packed AO/roughness/metallic maps. Plaster uses scanned normal
and roughness with a clean authored wall tint. The worktop uses separate seamless
colour, normal and roughness maps, avoiding the floor stone's grout. Painted
cabinets, book covers and artwork remain separate materials from fabric.
Normal and AO strength are deliberately restrained; roughness-map factors are
one, so the texture variation is retained.

Geometry UVs use local metres. Oak tiles cover 0.5 m, walnut 1 m, floor stone
1.5 m and plaster 1 m. Upholstery uses an approximately 0.266 m weave tile;
rugs and towels use smaller authored repeats. The fabric source is Poly Haven's
fine polyester weave, not a measured linen or terry-cloth scan. These variants
add surface detail but do not add fibres, folds or displacement geometry.
Tall entry joinery and island flutes use tinted oak with vertical grain;
horizontal walnut finishes retain their U-aligned source grain. Rectangular
lampshades use face-projected UVs to keep their weave proportional. The worktop
tile is an authored approximately 1.8 m scale, because its source has no supplied
physical dimensions.

The previous LDR environment is replaced with a real 2048×1024 RGBE HDR sky:
Poly Haven's Kloofendal Overcast (Pure Sky). Its source data contains radiance
above one and is kept unmodified. Environment rotation, diffuse/specular energy,
window fill, room lights and ambient lift are calibrated together; the authored
sun and the existing day-to-dusk timing are retained. All maps are local assets;
no engine changes were required. Source links, CC0 terms, channel contracts and
verified file hashes are in [assets/SOURCES.md](assets/SOURCES.md),
[PBR provenance](assets/pbr-v2/provenance.json) and
[HDR provenance](assets/environment-v2/manifest.json).

[Before/after stills](evidence/material-upgrade/before-after.png) compare the same
camera, frame, fixed 1080p resolution and Cinematic profile.
[Separate material and lighting comparisons](evidence/material-upgrade/ablation.png)
show baseline, material-only, environment/light-only and combined results.
[Close material stills](evidence/material-upgrade/swatches/material-detail.png)
reuse the actual scene finishes under raking light.

The reviewed material-phase source analyzed clean. The material-specific preservation check
passes all 501 models, 7 cameras, 7 animation channels, overlays, topology,
positions and Graph settings against the pre-upgrade snapshot. The opening
plan is pixel-identical. Eight representative house stills and three dusk
transition samples were reviewed; no complete video was exported. See
[validation-report.json](evidence/material-upgrade/validation-report.json).

The new texture data increases retained texture resources from 7 to 31 in the
warmed review. Matched short Balanced timing samples are recorded in the
validation report; these are submission measurements, not a playback-FPS
guarantee or evidence that PBR textures accelerate rendering. Cinematic enables
the existing screen-space indirect light/reflection approximations. The HDR
itself does not introduce local reflection probes or multi-bounce indoor GI.
The following indoor revision adds those features; the archived material evidence remains unchanged.

| Time | View |
| --- | --- |
| 0–6.5 s | Dimensioned 2D plan with public and private circulation |
| 6.5–13 s | Axonometric wall rise and roof assembly |
| 13–19 s | South terrace and street-facing exterior |
| 19–26 s | Living room with books, linen, reading lamp and open garden bay |
| 26–32 s | Kitchen island, worktop and four-seat dining area |
| 32–36 s | Primary bedroom in the separate private wing |
| 36–39 s | Bathroom, vanity, shower and high privacy window |
| 39–44 s | The same house at dusk |

The room arrangement stays fixed across shots. The roof underside remains a
physical ceiling during the interior views. Camera cuts use the Scene's
`activeCamera` animation channel; short position moves add depth without
changing the house layout. Seven fixed analytic lights now follow the sun and visible fixtures. Their intensity
changes at dusk; room lights stay at their physical fixture locations.

## Logical and output resolution

This showcase keeps `size={[3840,2160]}` for its authored coordinates and sets
`renderSize={[1920,1080]}` for the current output. Screen layers use `scale="2"`
to preserve the original 1920×1080 artwork coordinates and layout. The GPU
renderer fits each 3D island to the actual output resolution before compositing;
otherwise this combination renders the 3D island at 4K and downsamples it,
spending 4K GPU memory and shading time on a 1080p frame. The house, furniture,
cameras and geometry kept their original values in that resolution-only change.
The later material/HDR and realism revisions update the explicitly documented
surface, furniture and lighting details.

The linked `showcase99-4k.mp4` and 4K evidence files document the earlier
3840×2160 output, before the current output-resolution and material/HDR changes.
Anica’s embedded preview quality defaults to the UI’s 360p setting. For external
previews, Anica sends a quality override only outside the Script protocol.
The standalone `wgpu_live_preview` CLI defaults to Full and uses the DSL
`renderSize` (or `size` when `renderSize` is absent); adaptive resolution is opt-in.
Inspect frames at their output resolution to assess pixel detail.

### Historical 1080p WGPU playback cost before the material/HDR revision

On the same Apple M2 GPU, the strict WGPU exterior shot at frame 360 went from
**68.5 to 49.8 ms/frame** (about **14.6 to 20.1 FPS**) over 24 successive
warmed frames after city material batching. The kitchen at frame 660 went from
**70.6 to 53.3 ms/frame** (about **14.2 to 18.8 FPS**). The 3D render-target
allocation in the exterior warm run fell from about 573 MB to 150 MB after
fitting the island to 1080p. Draw calls fell from 2,442 to 770 with the same
386,810 visible triangles; CPU scene traversal still limits playback. The 24 FPS DSL
timeline is an export rate, not a guarantee that this machine can display the
scene live at 24 FPS. See `evidence/wgpu-1080-performance.json` for the measured
frames and method.

### Earlier 4K WGPU playback cost

On an Apple M2 GPU, the earlier 4K frame-time cost was dominated by the rectangular fill light's
four PBR samples per pixel. Reducing the four background buildings from about
1,900 individual parts to material-batched meshes reduced draw calls but did
not materially improve sustained *4K* FPS. The same batching is now adopted
for 1080p output, where it does improve FPS. The
MotionLoom renderer now uses two diagonal samples nearby and one centre sample
far away in its Balanced preview profile, while Cinematic and Ultra retain the
original four samples. That earlier 3840×2160 output and the showcase's trees,
buildings and interior layout were unchanged in the measured 4K revision.

Representative sustained 4K texture-frame times on that GPU were approximately
134→117 ms at 15 s (exterior), 217→195 ms at 27.5 s (kitchen), and 207→190 ms
at 35 s (bedroom). Those are about 7.5→8.5, 4.6→5.1, and 4.8→5.3 FPS,
respectively; hardware, thermal state, preview host and shot affect FPS. The
kitchen comparison changed RGB channels by an average 0.84/255, with the room
and furniture visually intact. `evidence/wgpu-performance.json` records the
historical method and measurements. Native 4K live playback was below the DSL's
24 FPS timeline rate on this machine; the completed 4K video remains a full
24 FPS export.

The native 4K fix changes only Graph resolution and screen-layer transforms.
Use `verify_preservation.py verify --allow-resolution-change` to compare against
the approved 1080p baseline while requiring the same aspect ratio and retaining
all protected scene semantics.

## Planting and city context

The planting uses deterministic native `MeshAsset` surfaces with tapered trunks,
branch junctions and petioles. Individual leaves have pointed tips, curved and
cupped blades, varied directions and proportionate sizes. Broad-leaf pot plants
also have raised midribs. These are authored botanical forms with natural
proportions rather than identified or scanned species. Several foliage materials
provide tonal variation without external plant textures.

| Planting assembly | Count | Leaves per assembly | Total leaves |
| --- | --- | --- | --- |
| Street trees | 2 | 2,200 | 4,400 |
| Lounge, terrace and entry pots | 3 | 36 | 108 |
| Garden planting groups | 8 | 144 | 1,152 |
| Dining vase sprigs | 1 | 30 | 30 |
| **Total** | **14** | — | **5,690** |

`evidence/planting-geometry.json` records each assembly's leaf count, emitted
vertices, faces, local bounds and placement, together with the exact source
SHA-256. There are 2,914 distinct authored leaf forms instanced as 5,690 visible
leaves through shared material batches. The scene still draws the original
167,572 plant vertices and 122,984 faces, while the DSL stores only 88,086
unique `Vertex` and 65,189 unique `Face` tags. Each emitted `MeshAsset` stays
within the engine's 30,000-vertex and 30,000-face cage limits.

The four surrounding buildings retain their original centres and ground
footprints. Their facade solids form real openings around recessed opaque window
planes, separate frames, mullions and projecting sills. Recessed balconies add
guards and repeated balusters, while roof parapets, HVAC grilles, vents and solar
panels give the skyline smaller-scale detail. Balconies and equipment remain
within each original X/Z footprint; roof details extend at most 0.64 m above the
original massing. Background windows use dark opaque PBR materials with distinct
roughness and colour, without transmission.

The background roofs and plinths avoid overlapping coplanar surfaces that
previously flickered during camera moves. Roof decks sit 25 mm above the facade
tops, slab bands sit 8 mm above adjoining masonry tops, and the plinth sides
recess 20 mm behind the facade piers. Plinth bottoms meet the site surface.
`scripts/verify_city_surfaces.py` checks the actual DSL compound instances:
the four roof/plinth assemblies now have zero coplanar material conflicts within 0.1 mm,
compared with 242 in the pre-fix scene. Lighting and TAA settings are preserved.

The earlier planting and context revision preserved the main house, room layout,
furniture, lamp housings, cameras, lighting, textures and animation channels.
Its semantic preservation check passed 364 protected models and their referenced
geometry/materials, with cameras and light resources unchanged. Generated asset
numbering can change without changing those protected objects.

## Dimensions and assumptions

This is a conceptual two-bedroom, single-storey dwelling for an assumed urban
site. Dimensions are authored in metres, with +Y up, +X east and +Z south.
Floor level is approximately Y=0 and wall height is 3.0 m. No site survey,
engineering, code compliance or accessibility determination is supplied.

The nominal plan is 12×8 m: exterior wall **centrelines** are X=−6/+6 and
Z=−4/+4. The plan's 96 m² caption is the assumed rectangle between those
centrelines, not a measured gross or usable floor area. The 0.18 m exterior
walls extend beyond the centrelines, giving approximately 12.18×8.18 m bounding
extents; the 12.2×8.2 m slab and roof overhangs are separate dimensions.

| Zone | X limits | Z limits |
| --- | --- | --- |
| Open kitchen / dining / living | −6 to 1.5 | −4 to 4 |
| Private hall | 1.5 to 2.7 | −4 to 4 |
| Guest / study | 2.7 to 6 | −4 to −1.3 |
| Bathroom | 2.7 to 6 | −1.3 to 1.1 |
| Primary bedroom | 2.7 to 6 | 1.1 to 4 |

These limits are partition centrelines. The nominal 1.2 m hall has about 1.06 m
between the faces of its 0.14 m walls. Room door voids are 0.90 m wide and
2.25 m high; 0.86 m leaves are held open. The public-to-private passage and
south entry voids are each 1.10 m wide. These are modeled opening dimensions,
not certified finished clear widths.

Approximate furniture gaps in the authored geometry are 0.79 m between the
kitchen counter and island worktops, 0.46 m between sofa arms and coffee table,
0.78 m between coffee table and south wall, and 0.71 m at the primary bed's
west foot aisle. The primary bed runs east–west with its headboard east. The
guest foot gap is about 0.53 m and the primary wardrobe-to-mattress gap about
0.51 m. The primary mattress's south side has only about 0.26 m clearance;
the bed is approached from its north and west sides. This compact edge remains
a design constraint to reconsider for a real dwelling.
Door swings, chairs and fittings require a separate detailed usability review.

## Source and rebuild

- `main.motionloom` — complete portable DSL document; all raster assets use
  paths relative to this directory.
- `scripts/build_showcase.py` — deterministic base geometry, materials, cameras,
  animation and composition generator; run `realism_upgrade.py` afterwards.
- `scripts/realism_upgrade.py` — applies the approved furniture geometry,
  material layers and finite-source calibration from the preserved baseline.
- `scripts/realism_geometry.py` and `scripts/realism_geometry_allowlist.json` —
  deterministic bounded furniture cages and the exact 22-model allowlist.
- `scripts/verify_realism_upgrade.py` — protects all 501 model transforms,
  non-allowlisted geometry, cameras, timeline and 2D overlays.
- `scripts/build_realism_evidence.py` — prepares isolated archived/current
  review inputs and assembles source-bound static comparisons.
- `scripts/material_upgrade.py` — shared PBR datasets, finish routing and
  metre-scaled UV policy.
- `scripts/build_material_swatches.py` — regenerates the portable close material
  fixture `scripts/material-swatches.motionloom` from the canonical finishes.
- `scripts/material_review.rs` — strict GPU API still/timing harness with
  explicit quality profile, fixed resolution and temporal warmup; its measured
  submission samples exclude PNG/readback work.
- `scripts/build_material_evidence.py` — verifies the reviewed source hashes,
  CC0 map/HDR bytes and material channel/UV bindings, then assembles labelled
  static comparisons and `validation-report.json` (Pillow and NumPy required).
- `scripts/verify_material_upgrade.py` — preserves all 501 models, geometry,
  cameras, animation and overlays while permitting material/UV and explicit
  lighting calibration changes against the immutable pre-upgrade snapshot.
- `scripts/vegetation.py` — native mesh construction for tapered branches,
  petioles, curved pointed leaves, raised midribs, pots and soil.
- `scripts/city_context.py` — four native buildings with material-batched
  facades, compound details, recessed windows, balconies and roof equipment.
- `scripts/compact_dsl.py` — shares duplicate geometry and groups generated
  cage tags without altering the authored scene.
- `scripts/plan.motionloom.fragment` — native 2D plan artwork included by the
  generator; its coordinate map is `(1200 + 70×X, 510 + 70×Z)`.
- `scripts/layout.json` — generated wall solids, nominal room limits and door
  openings for comparing plan and 3D geometry.
- `scripts/verify_geometry.py` — independent checks of emitted wall voids,
  camera endpoints and room door leaves.
- `scripts/verify_city_surfaces.py` — checks actual DSL roof and plinth faces
  for material conflicts on planes within 0.1 mm of one another.
- `scripts/verify_preservation.py` — semantic comparisons of protected house
  geometry, furniture, materials, texture bytes, cameras, lighting and animation,
  independent of generated asset IDs.
- `assets/SOURCES.md` — native geometry provenance, CC0 datasets, legacy texture origins and
  SHA-256 identifiers.
- `evidence/planting-geometry.json` — source-bound leaf counts, mesh topology
  totals, planting positions and bounds.
- `evidence/vegetation-check.json` — mesh limits, winding, branch orientation,
  leaf attachment, tree clearance and camera translation checks.
- `evidence/preservation-check.json` — comparisons against the bundled
  `scripts/preservation-baseline.json` from the approved interior revision.
- `evidence/resolution-check.json` — native 4K versus output-only 4K GPU checks.
- `evidence/optimization-check.json` — byte and line reduction, shared
  geometry references and deterministic topology checks.
- `evidence/reuse-gpu-check.json` — strict 4K GPU before/after frame and
  rendering-cost measurements at representative times.
- `evidence/wgpu-1080-performance.json` — historical 1080p strict WGPU frame
  measurements after the 3D island target-resolution fix.
- `evidence/vegetation-reuse-check.json` — shared cage, leaf-count and
  rotated-tree clearance checks against the earlier full vegetation audit.
- `evidence/city-surface-check.json` — four background roof/plinth assemblies
  checked for coplanar material conflicts in the current DSL.
- `scripts/lighting_bake_options.json` — five room grids, day/dusk frames and deterministic CPU bake settings.
- `scripts/lighting_review.rs` — selected GPU stills, consecutive frames and warmed submission measurements.
- `scripts/verify_lighting_upgrade.py` — checks all 501 models, UVs, non-glass materials, cameras, overlays and seven original animation channels against the archived material-phase source.
- `scripts/build_lighting_evidence.py` — assembles source-bound static lighting/mirror comparisons and validation metrics.
- `assets/lighting-v3/` — generated two-state irradiance JSON and ten linear HDR room captures.
- `scripts/bake_lighting.py` — CPU bake wrapper; refreshes lighting provenance
  and accepts `--evidence` to keep each review phase separate.
- `evidence/lighting-upgrade/` — archived indoor-lighting validation; no complete video export.
- `evidence/realism-upgrade/` — current baseline, preservation and furniture
  evidence; native still validation is recorded here when complete.
- `schema.json` — generated learning schema for the syntax demonstrated here.
- `evidence/material-upgrade/` — archived material-phase source-bound stills, ablations,
  preservation, opening-plan comparison and short timing measurements. The
  compressed pre-upgrade DSL is retained as `baseline-scene.motionloom.gz`.
- `evidence/` — rendered checkpoints and export evidence. The geometry-reuse
  version has its own 4K export and updated decoded checkpoints.

From the workspace root, regenerate the document, layout and planting geometry
report after updating the generator, plan fragment or native geometry modules:

```sh
python3 motionloom-example/showcase/s-000099/scripts/build_showcase.py
python3 motionloom-example/showcase/s-000099/scripts/realism_upgrade.py
python3 motionloom-example/showcase/s-000099/scripts/verify_geometry.py
python3 motionloom-example/showcase/s-000099/scripts/verify_city_surfaces.py
python3 motionloom-example/showcase/s-000099/scripts/verify_vegetation_reuse.py
python3 motionloom-example/showcase/s-000099/scripts/verify_realism_upgrade.py verify
python3 motionloom-example/showcase/s-000099/scripts/build_material_swatches.py
```

`verify_optimization.py` and the old material-preserving baseline lock the
earlier complete tag/material stream. Their historical evidence remains intact;
the archived material revision uses `verify_material_upgrade.py` with an
independent immutable baseline rather than rewriting those locks.

The material review harness accepts:

```text
material_review <script> <asset-root> <output-directory> <profile> <comma-separated-frames>
  [--benchmark=660,360] [--warm=8] [--analyze-only]
```

It uses the public MotionLoom API and can be compiled with the release library
and its `pollster`/`serde_json` dependencies. Current house evidence uses
`cinematic` with frames `0,360,528,660,840,880,984,1055`; short timing samples
use `balanced`. Asset root is this S99 directory; for the portable swatch
fixture it is `scripts/`. Every review report records its exact source SHA.
The figure builder requires those source-bound reports before assembling
comparisons, and does not invoke video export.

Before making a later planting or context revision, take a semantic snapshot
before editing and verify it after rebuilding:

```sh
python3 motionloom-example/showcase/s-000099/scripts/verify_preservation.py \
  snapshot --baseline /tmp/s99-before.json
# Edit the planting/context modules, then rebuild main.motionloom.
python3 motionloom-example/showcase/s-000099/scripts/verify_preservation.py \
  verify --baseline /tmp/s99-before.json
```

The earlier native 4K GPU export contains 1,056 H.264 frames at 3840×2160,
24 fps. Ten checkpoints decoded from that video were inspected. Its authoring
analysis had zero errors and warnings. The archived indoor-lighting 1080p source analyzed
clean and passed the geometry check for 12 wall voids and 19 camera endpoints,
the city roof/plinth conflict check, and the indoor-lighting preservation
check for all 501 models.
The reused vegetation cages retain the prior nine structural checks.
`evidence/evaluation.json` records the earlier 4K export and checkpoint hashes;
the historical 1080p measurements are in `evidence/wgpu-1080-performance.json`;
archived material/HDR review evidence is in `evidence/material-upgrade/`;
archived indoor-lighting evidence is in `evidence/lighting-upgrade/`;
the current review is recorded separately in `evidence/realism-upgrade/`.

From `motionloom/`, generate only S99's learning schema and authoring analysis:

```sh
cargo run --release -p motionloom --example build_showcase_schemas -- \
  ../motionloom-example/showcase/s-000099
```

Inspect representative strict GPU frames. Frame numbers are zero-based; frame
480 is 20 seconds at 24 fps:

```sh
cargo run --release -p motionloom --example render_file_frame_gpu -- \
  ../motionloom-example/showcase/s-000099/main.motionloom \
  /tmp/s99-living.png 480 3
```

Render the 44-second video with the native GPU profile and the project's
FFmpeg runtime:

```sh
cargo run --release -p motionloom --example render_file_video -- \
  ../motionloom-example/showcase/s-000099/main.motionloom \
  /tmp/s99-house.mp4 gpu
```

## Indoor bounce, glass and reflections — 2026-10-06 (archived evidence)

`BakedLighting` loads five room volumes with 384 probes in each of two states.
The CPU solver traces three diffuse surface bounces against actual scene
geometry, texture colours, fixed lights and the HDR sky. Directional depth
moments limit cross-wall interpolation; invalid probes are excluded. The bake
fades in after the construction reveal and blends day to dusk from 37–40 s.
Room irradiance replaces unoccluded global diffuse IBL, and additional SSGI is
suppressed. Ten HDR captures supply box-projected local specular reflections.

The old broad window fill and moving room fill are replaced by the sun and six
fixed lamp sources. Lamp power/range are authored presentation values, not a
measured lux design. Reading-light sources sit just below/beside their opaque
housings so their own closed geometry does not hide the point source.
Glass uses camera-consistent thin-slab refraction, once-per-volume absorption,
and successive back-to-front transmission snapshots. Uncovered rays see the HDR sky
even when its direct camera background is hidden. The bathroom mirror now
uses an opaque metallic material and `PlanarReflection` with an actual reflected
camera, including offscreen objects. Window/mirror roughness is 0.04, the
MaterialAsset parser's lower bound; shower glass uses 0.065.

The upgrade preserves geometry, furniture, UVs, cameras, the original timeline
and overlays. The local validation report (`evidence/lighting-upgrade/validation-report.json`)
and local controlled comparison (`evidence/lighting-upgrade/comparison.png`) bind their
stills to exact source/asset hashes. The comparison's previous-scene column is
rendered with the current engine, and its global-only column disables the bake
in the current authored scene. The mirror inspection changes only a temporary
review camera; it does not change `main.motionloom`.

From `motionloom/`, rebuild the current assets and their provenance, or check
dependencies without exporting video:

```sh
python3 ../motionloom-example/showcase/s-000099/scripts/bake_lighting.py --build \
  --evidence ../motionloom-example/showcase/s-000099/evidence/realism-upgrade
# Recompute geometry/material/texture/light dependencies without tracing.
cargo run --release --example bake_scene_lighting -- \
  ../motionloom-example/showcase/s-000099/main.motionloom \
  ../motionloom-example/showcase/s-000099/scripts/lighting_bake_options.json \
  ../motionloom-example/showcase/s-000099/assets/lighting-v3/s99-lighting.json --validate
python3 ../motionloom-example/showcase/s-000099/scripts/verify_realism_upgrade.py verify
```

The archived indoor-lighting native GPU path was checked with stills and short
consecutive samples. It did not produce a complete video. Its warmed Balanced samples
measured kitchen submission time at approximately 73 ms before and 126 ms after;
bathroom 78 ms before and 125 ms after. These include CPU preparation and queue
backpressure, exclude readback/PNG work, and are not complete GPU times or certified
playback FPS. See the engine's
[indoor lighting contract](../../../motionloom/docs/BAKED_LIGHTING.md) for portable
schema, validation, cache guards and host budgets.

## Renderer scope

WGPU Preview is the reference for this presentation. It uses seven fixed
direct lights, visibility-filtered baked diffuse transport, local reflection
probes and one bathroom planar mirror. The current opt-in per-light mode supplies
independent bounded shadow visibility for the sun and local sources;
emissive lamp surfaces provide visible sources. AO and contact shadows remain
approximations. Baked geometry is static at the sampled day/dusk states and
requires rebaking after source/material/lighting changes. A source guard rejects
stale authoring; `--validate` also verifies evaluated texture bytes and options.

Three diffuse bounces and interpolated probes do not solve glossy interreflection,
caustics or arbitrary moving geometry. Box-projected reflections approximate
parallax; the planar mirror uses its actual reflected camera with one recursion
level. Thin-sheet glass still depends on screen-space background data, so
intersecting panes, concave solid refraction and offscreen refraction remain
approximate. The optional Weaver physical-transmission path is unsupported and
is not validated by this revision. Native tests and a WASM compile check do not
claim browser GPU pixel parity or Blender/Cycles parity.

The CPU preview is not a visual reference for the physical 3D shader path.
The video is an authored sequence of interior and exterior views, not an
interactive walkthrough export or a promised photorealistic architectural
render. See the engine's [immediate preview contract](../../../motionloom/docs/IMMEDIATE_PREVIEW.md)
and [Weaver limitations](../../../motionloom/src/weaver/README.md)
for renderer-specific behavior.

## Local review artifacts

The `evidence/` directories mentioned above contain generated local review
artifacts and historical exports. They are not distributed in this repository;
the authored scenes, runtime assets and reproduction scripts are included.
