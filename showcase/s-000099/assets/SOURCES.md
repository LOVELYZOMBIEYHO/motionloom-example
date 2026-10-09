# S99 asset sources

All house, furniture, light-housing, planting and city geometry is authored in
`scripts/build_showcase.py`, `scripts/vegetation.py` and `scripts/city_context.py`,
then emitted into `main.motionloom` as native MotionLoom DSL. S99 has no imported
GLB, FBX, OBJ or other external model file, and no Blender dependency.

The procedural planting is original native `MeshAsset` geometry: swept tapered
trunks and branches, petioles, curved pointed leaf blades and raised midribs on
the pot plants. Pots and soil are also authored geometry. The planting uses
scalar PBR materials with foliage colour variation and has no external model
or plant-texture dependency. Its forms and natural proportions are authored
rather than botanical species identification or measured scans.
`../evidence/planting-geometry.json` binds the 14 planting assemblies and 5,690
individual leaves to the exact DSL source hash, with topology totals and bounds.

The four context buildings are original `GeometryAsset`/`CompoundAsset`
assemblies. Their window openings, recessed opaque panes, frames, balconies,
parapets and roof equipment use native geometry and scalar PBR materials, with
no imported building model, facade texture or transmission glass dependency.
The main house geometry, furniture, camera paths and light placement remain the
established S99 design. `scripts/verify_material_upgrade.py` compares all 501
models and the protected scene semantics across the current surface/HDR revision;
the older material-preserving checker documents the earlier planting revision.

## Current CC0 material and environment assets

All datasets below are CC0-1.0 and are stored as unmodified provider bytes.
No ImageGen was needed for this revision. Maps are local to S99 and are shared
across finish variants. [provenance.json](pbr-v2/provenance.json) records authors,
download URLs, source dimensions, channel meanings, provider integrity checks and
SHA-256 for every map. The providers' license pages are
[Poly Haven](https://polyhaven.com/license) and
[ambientCG](https://docs.ambientcg.com/license/).

| Dataset / local directory | Source | Scene use / scale |
| --- | --- | --- |
| `pbr-v2/white_oak_veneer` | [Poly Haven pale oak](https://polyhaven.com/a/white_oak_veneer) | Floorboards, oak furniture, tinted vertical entry joinery and island flutes; 0.5 m tile |
| `pbr-v2/walnut_veneer_02` | [Poly Haven walnut](https://polyhaven.com/a/walnut_veneer_02) | Horizontal walnut furniture and joinery; 1 m tile |
| `pbr-v2/marble_01` | [Poly Haven marble floor](https://polyhaven.com/a/marble_01) | Floor and exterior stone; 1.5 m tile |
| `pbr-v2/white_plaster_02` | [Poly Haven plaster](https://polyhaven.com/a/white_plaster_02) | Wall and ceiling normal/ARM detail with a clean authored tint; 1 m tile |
| `pbr-v2/terlenka` | [Poly Haven polyester weave](https://polyhaven.com/a/terlenka) | Tinted upholstery, bedding, rug, towel and shade finishes; source tile approximately 0.266 m |
| `pbr-v2/marble012` | [ambientCG Marble012](https://ambientcg.com/view?id=Marble012) | Seamless worktop colour/normal/roughness; authored approximately 1.8 m tile |
| `environment-v2/kloofendal_overcast_puresky_2k.hdr` | [Poly Haven sky, Greg Zaal](https://polyhaven.com/a/kloofendal_overcast_puresky) | Invisible daylight IBL, 2048×1024 linear RGBE HDR |

Poly Haven material sets use OpenGL +Y tangent-space normal maps and ARM packed
as R=AO, G=roughness, B=metallic. AmbientCG worktop uses a separate R-channel
roughness image and no AO map. Colour images use sRGB; normal, ARM, roughness and
HDR ImageAssets use linear-sRGB. Nonmetals use metallic=0, while roughness=1
allows the selected texture values to retain their variation. Geometry UVs are
metre-based; material textureScale applies repeats per metre. Pale oak grain is
along image V and walnut along U. Rectangular lamp frustums use box projection.

Weave finishes are artistic uses of one fine polyester texture, not claims of
linen, terry-cloth scans or resolved fibres. Plaster albedo is retained in the
dataset but intentionally unused to avoid baked dirt. Marble012 has no supplied
physical dimensions, so its worktop scale is authored. Normal/AO strengths and
fabric tints are authored parameters; no source map is modified.

[environment-v2/manifest.json](environment-v2/manifest.json) records the HDR's
license, hash, full float decode validation and radiance statistics. This is a
real HDR source with values above one. Its local PNG preview is display-only.
Scene calibration uses day intensity 0.75, diffuse 0.85, specular 0.4 and rotation
−90.33°, with environment energy fading to 0.2 by 40 seconds. The source does not
provide local probes, indoor occlusion or multi-bounce GI.

## Generated indoor lighting assets

`lighting-v3/s99-lighting.json` and ten `lighting-v3/reflections/*.hdr` files are
computed from this authored scene, the existing CC0 maps/HDR, and the options in
`scripts/lighting_bake_options.json`. They are generated transport data, not
additional downloaded datasets or ImageGen imagery. No source map is edited.
`lighting-v3/provenance.json` records source/options SHA-256, separate bake
fingerprints, file hashes and probe validity. The existing provider terms above
remain the provenance for the inputs. Three diffuse bounces and a straight
thin-sheet glass approximation do not constitute measured room light or a full
physical path-traced solution.

The upgrade's preservation checker is `scripts/verify_lighting_upgrade.py`;
it permits the explicit light topology and glass/mirror changes while protecting
all models, UVs, non-glass materials, cameras, animation and overlays.

## Retained legacy raster assets

The four raster files below are byte-identical copies of assets already in
this workspace's MotionLoom showcases. Their original relative repository
paths and SHA-256 values identify the copied bytes; filenames describe their
role here and are not claims of measured material data.

| S99 file | Original path in `motionloom-example/` | SHA-256 |
| --- | --- | --- |
| `textures/oak.png` | `showcase/s-000089/assets/pbr/wood-base.png` | `5d5711c61faf053780d843a841dd5c9f54bcdeb5bc12b3c79af74daf2eeccf26` |
| `textures/stone.jpg` | `showcase/s-000073/assets/textures/Texture_Stone.jpg` | `5063e45ccd98ab3686936b55e6fba236d84b1b1261048d83ab3f285b1f0f9faf` |
| `textures/plaster.jpg` | `showcase/s-000073/assets/textures/pbr/plaster_base.jpg` | `b697cfdd2e8ead5853c950b1d9551472c25d753fd3575ea07f0ed59217146f48` |
| `textures/daylight-environment.png` | `showcase/s-000098/assets/studio-natural-environment.png` | `dc6261877ea179f0f582ff806cc85561929988d6712513cd59e7fee57bd7ea1a` |

The first three were reused base-color images in the pre-upgrade scene. Its wood and stone were given
authored color tints and scalar roughness; the name `oak.png` denotes the house
palette, not a botanically identified or physically scanned wood species.
S89's [material provenance](../../s-000089/assets/pbr/README.md) records built-in
image generation for the wood base color. Its requested seamless, uniformly lit
appearance is an artistic brief, not a guarantee or a measured material scan.
S73's [asset provenance](../../s-000073/assets/ASSET_PROVENANCE.md) records
project-specific OpenAI image generation on 2026-08-23 and subsequent resizing
and re-encoding for the stone and plaster sources. S99 copies these base images
only and does not claim measured normal, roughness or displacement maps.

The fourth is the existing S98 studio environment image previously reused for diffuse
and specular image-based lighting. Its S99 filename describes its use; it is
an LDR PNG, not an HDR capture. S98's [README](../../s-000098/README.md) describes
its role as an invisible soft studio environment. A separate generation or
upstream license record was not found for that image during S99 authoring.

This legacy section records local provenance and byte identity. It does not assert
an additional license, public-domain status or third-party ownership terms.
The user attachment supplied the general plan-to-house presentation brief,
not an architectural drawing, texture or geometry source. Assumed dimensions
and the invented floor plan are documented in `../README.md`.
