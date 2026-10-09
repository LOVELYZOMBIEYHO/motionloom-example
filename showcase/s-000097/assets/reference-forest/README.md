# S97 reference forest assets

These assets are derived from **"landscape forest & mountains" by dasy444**,
licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The original model is available on
[Sketchfab](https://sketchfab.com/3d-models/landscape-forest-mountains-94809d21d7aa4cfe9b658a111b35a42c),
and the original file remains unchanged in
`showcase/s-000096/assets/landscape_forest__mountains.glb`.

`extract_reference_forest.py` reproduces the derived GLBs, all 14 original
embedded images, and `provenance.json`. Images are copied byte for byte:
there is no image generation, repainting, color correction, or alpha editing.
The provenance records the original file hash, material/image mappings, source
and canonical bounds, transforms, and derived file hashes.

## Original crossed cards

Each plant retains the original **8 vertices and 4 triangles**, comprising two
intersecting rectangles. Original UVs, indices, sampler settings, alpha cutoffs,
roughness, double-sided settings and image bytes are preserved. Positions and
normals are rotated so source `-Z` becomes canonical `+Y`; positions are then
uniformly resized and grounded at `Y=0`. Original scene placements are discarded.

Dimensions below describe the rectangular cards, including transparent margins;
they do not describe the opaque silhouette alone. Tree names describe colors,
not identified species. Coordinates are metres.

| Asset | Source mesh / material / image | Canonical dimensions X × Y × Z | Bounds X/Z and Y |
| --- | --- | --- | --- |
| `tree-dark-green.glb` | 3 / Material.004 / 4 | 8 × 8 × 8 | X/Z ±4; Y 0–8 |
| `tree-blue-green.glb` | 4 / Material.005 / 5 | 9 × 9 × 9 | X/Z ±4.5; Y 0–9 |
| `tree-light-green.glb` | 5 / Material.006 / 6 | 7 × 7 × 7 | X/Z ±3.5; Y 0–7 |
| `grass-long-blades.glb` | 1 / Material.002 / 2 | 1 × 1 × 1 | X/Z ±0.5; Y 0–1 |
| `grass-compact-tuft.glb` | 2 / Material.003 / 3 | 0.8 × 0.8 × 0.8 | X/Z ±0.4; Y 0–0.8 |

All five materials use `alphaMode="MASK"` and `doubleSided=true`. Their
original alpha cutoffs are approximately 0.643435, 0.801334, 0.528048,
0.497683 and 0.619143 respectively; roughness is 0.821115 and metallic is 0.
The original card materials have no normal textures. A model instance at the
S97 site scale `0.05` has tree heights 0.4, 0.45 and 0.35 engine units.

## Authored aerial foliage additions

`tree-dark-green-canopy.glb`, `tree-blue-green-canopy.glb` and
`tree-light-green-canopy.glb` retain the exact original cards and add three
open, irregularly curved foliage sheets at different upper branch heights.
Every augmented asset has **155 vertices and 220 triangles**, of which 216
triangles belong to the additions. The two geometry primitives reuse a single
original tree material and its original embedded image: Material.004/image4,
Material.005/image5, or Material.006/image6 respectively. Original alpha MASK
cutoffs, double-sided settings, roughness and sampler remain unchanged.

The added geometry uses cropped source UVs to omit the bare trunk. U retains
its full 0–1 range to preserve transparent branch edges; V crops are 0.32–0.985,
0.28–0.99 and 0.27–0.98. Three different rotations, gentle irregular bends and
slight tilts give overhead coverage while alpha holes preserve wispy silhouettes.
These additions contain no opaque aerial canopy cap, no image7 or normal8,
and no additional material. Image pixels are never edited.

The additions are authored S97 approximations, not original S96 geometry.
They supply low-cost distant aerial coverage and retain the original side
silhouettes. Close inspection can still reveal the layered card geometry; use
detailed 3D trees at roadside camera distances. Bounds, layer dimensions,
heights and UV crops are recorded in `provenance.json`.

## Sky dome

`mountain-sky-dome.glb` preserves source mesh 3686, original UVs and 960
triangles, Material.011's double-sided base color and emissive material, and
embedded image 13. The source is a deformed radius-100 sphere with its lower hemisphere compressed. The
derived dome is centered on its spherical origin and has **radius 45** engine
units. It keeps the source parent rotation and discards the source translation.
Bounds are approximately `[-45,-12.66794,-45]` to `[45,45,45]`.

Keep a camera inside the dome. Bounding-box midpoint and spherical center differ
because the original lower hemisphere is compressed. Its bottom is closed;
placing that bottom above the terrain can hide an aerial view.
This is the original painted mountain/sky image; its source lighting is visible
in the image. The extraction does not simulate atmospheric lighting.

## Texture and material mapping

| Source material | Source base-color image | Other images | Role |
| --- | --- | --- | --- |
| Material.001 | 0 | Normal 1 | Opaque ground surface |
| Material.002 | 2 | Alpha in image 2 | Long grass crossed cards |
| Material.003 | 3 | Alpha in image 3 | Compact grass crossed cards |
| Material.004 | 4 | Alpha in image 4 | Dark green whole-tree cards |
| Material.005 | 5 | Alpha in image 5 | Blue green whole-tree cards |
| Material.006 | 6 | Alpha in image 6 | Light green whole-tree cards |
| Material.007 | 7 | Normal 8 | Opaque aerial forest canopy surface |
| Material.008 | 9 | Normal 10 | Opaque landscape surface |
| Material.009 | 11 | Normal 12 | Opaque landscape surface |
| Material.011 | 13 | Emission 13 | Mountain/sky dome |

External copies are named `textures/s96-image-00.jpg` through
`textures/s96-image-13.jpg`, preserving each image's original PNG/JPEG format.
Each standalone GLB also embeds its own required images. No dedicated opaque
bark material or bark texture exists in the source. Bark appears within the
alpha-masked whole-tree images; image 7 is canopy, not bark.

## Verification

`asset-preview.motionloom` provides an oblique diagnostic at frame 0 and an
overhead diagnostic at frame 12 of the augmented trees and original grass.
It is separate from S97's main scene. Native GPU renders of the curved alpha foliage were inspected at both angles;
current evidence is `/private/tmp/s97-alpha-canopy-oblique.png` and
`/private/tmp/s97-alpha-canopy-overhead.png`. The older `preview-*.png` and
`validation.json` describe the superseded opaque cap prototype. Current checks
for exact original cards, material, image preservation and valid new geometry
are recorded under `alphaCanopyValidation` in `provenance.json`.
