# S74 — Primitive Stair Pavilion

This eight-second architectural showcase builds a complete stone stair pavilion
from first-class typed `PrimitiveAsset` geometry, then sends the canonical
Character 1 up all eleven steps. A Radiance HDR courtyard supplies environment
light and reflections while simplified 3D courtyard architecture adds scale,
parallax and shadow-receiving surfaces.

## What this example teaches

- Reuse one typed box asset across eleven precisely aligned stair treads.
- Use `MaterialAsset shading="pbr"` to apply `Texture_Stone.jpg` as a lit
  base-color texture instead of a screen-space texture overlay.
- Share project-owned generated base color, tangent-space normal, packed
  metallic/roughness and AO maps across the courtyard, plaster walls,
  weathered wall bases, glazing and every brushed-metal architectural part.
- Add deterministic per-instance UV variation so eleven reused steps do not
  sample an identical patch of stone.
- Round visible step, landing, rail and canopy edges while retaining the exact
  original box colliders used by the character controller.
- Build nosing, recessed joints, rail base plates, connectors and bolts from
  additional non-colliding typed primitives.
- Use wedges as structural stair stringers instead of encoding geometry in a
  `src` string.
- Assemble railings from shared cylinders and inclined box handrails.
- Combine all six v1 shapes: box, sphere, plane, cylinder, cone and wedge.
- Dress a primitive-only scene with PBR lighting, shadows, ambient occlusion,
  contact shadows and ACES color management.
- Wrap `Texture_Wood.jpg` around the cylinder UVs to give both courtyard tree
  trunks rough, vertically tiled PBR bark instead of a flat brown color.
- Reuse one compound primitive tree with visible branching, three foliage
  tones and twenty-seven alpha-masked leaf clusters; reuse the same foliage
  atlas in compound shrubs, then vary seed, rotation, scale and tint so neither
  trees nor planters read as repeated green spheres.
- Build each practical lamp from a metal collar, translucent glass globe and
  emissive core whose position matches the warm landing light.
- Add non-colliding wall plinths, drains, paving seams, glass clamps, welds and
  canopy trim without making the character controller solve detailed meshes.
- Combine HDR image-based lighting with a directional key, warm platform
  practical, cyan character rim and rectangular fill light.
- Finish the HDR scene with restrained bloom and deterministic film grain.
- Combine an in-place `Walk_Loop` action with a measured root position path so
  the 1.8 m-tall Character 1 rises exactly 0.32 m per tread and reaches the
  upper landing without sinking below the primitive surfaces.
- Alternate short weight-bearing plateaus with quick eased rises instead of
  moving the root along one continuous slope; a 3 cm sole clearance protects
  the animated toe swing from intersecting each riser.
- Use neutral stone, brushed metal, warm sunset light and restrained cool
  accents while preserving tread silhouette and contact readability.

The upper landing, canopy, paired columns, lamps, mullioned glazing, planters,
shrubs and trees make the result a courtyard rather than an isolated geometry
test. The explicit model placement and root animation keys keep every
architectural measurement and character step height easy to inspect and modify.

## Multi-camera composition

`main.motionloom` keeps one complete Character 1 and one continuous stair-walk
action across four editorial shots. From 0–3 s, a head-bone `Anchor` drives a
first-person `Camera3D`, whose `hiddenBones={["s74_walker:head"]}` selector hides
only the owner's head from that camera while preserving its body and shadow.
At 3 s, `activeCamera` cuts to a third-person follow shot and the complete head
returns. At 5 s, it cuts to a front-facing close shot from a fixed world-space
camera ahead of the still-forward-walking character. A world-space `Anchor`
tracks the character's upper body as the camera target, so only the camera angle
changes and the reverse shot reveals a genuinely different background. The
camera cuts use existing `AnimationTarget` and `Key` features; camera-local bone
visibility is expressed through `Camera3D.hiddenBones`.

At frame 180 (6 s), the edit restores the original pre-multi-camera S74
overview: `position={[12.8,5.75,14.6]}`, `target={[0,2.05,-1.65]}` and
`fov="35"`. The landing extends rearward from 3.4 m to 7.0 m while preserving
its original stair-facing edge. During the final two seconds the walk action
continues and the character advances about 3.3 m across that collider-owning
platform, rather than walking in place. Extended side rails and rear support
posts finish the longer platform in the establishing shot.

## Realism baseline and resource budget

The baseline was checked at frame 0 (first person), frame 90 (third person) and
frame 170 (front close-up). Its strongest artificial cues were uniformly flat
ground and walls, plastic-looking rails, colour-panel glass, sphere shrubs,
solid primitive foliage and lamps without a visible light source. The realism
pass addresses those cues without changing the stair dimensions, colliders,
character path or camera schedule.

All runtime textures are project-owned assets generated specifically for this
showcase: pale stair stone, vertical tree bark, courtyard concrete, mineral
plaster, brushed architectural metal, restrained glass roughness, weathered
concrete and a transparent broad-leaf cluster. No Texturelabs source or
Texturelabs-derived map remains in the repository. The exact generation briefs
and asset roles are recorded in `assets/ASSET_PROVENANCE.md`.

The three foliage materials share one generated transparent cluster; mapping a
complete rectangular atlas onto every plate would make a distant crown read as
stacked cards. Derived normal, metallic/roughness and AO images are 512 px. The
deterministic `tools/build-project-pbr-textures.sh` script rebuilds those maps
from the generated project-owned base images and strips ancillary metadata.
All instances reference shared
`ImageAsset` and `MaterialAsset` resources, so the renderer decodes each map
once. The validated scene decodes 21 textures (55,734,784 bytes), then renders
all 239 subsequent warm frames without further texture decoding.

The final acceptance run renders frames 0–239 in one renderer instance. It
confirms all four `Camera3D` cuts, the unchanged step-contact walk, stable
texture sampling and a clean authoring report with no ignored attributes,
unknown tags or missing assets.
