# S75 — Rain-Night Metro Ascent

This nine-second cinematic test turns the reusable primitive staircase into a
rainy underground-station exit. Character 1 climbs from the lower concourse,
passes wet walls and illuminated poster cases, then continues across a puddled
street-level pavement while the edit cuts through first-person, stair-follow
and street-establishing cameras.

## What this example tests

- Reuse typed `PrimitiveAsset` boxes as ten collider-owning stair treads while
  keeping nosings, drains, stains, posters and façade dressing non-colliding.
- Keep one kinematic Character 1 and one looping walk action alive across all
  three `Camera3D` shots.
- Use matched, deterministic stair-synchronised `Camera3D` position and target
  keys for the 0–3 s first-person camera. Its camera-local `hiddenBones`
  selects the owner's `hips` root so no skinned body surface can cross the
  near plane; animation, collision and shadow casting remain active.
- Cut at 3 s to an interior stair-follow shot which restores the complete
  character, then at 6 s to a street-side wide shot facing back toward the
  metro entrance.
- Share the existing S74 wet concrete, plaster, weathered concrete and brushed
  metal PBR resources instead of duplicating texture files.
- Combine low-roughness wet paving, transparent puddle planes, wall-water
  stains, drain grates and a curb to establish recent rainfall.
- Build the station enclosure, canopy, glazing, rails, posts, bollards, poster
  cases and distant building masses entirely from reusable typed primitives.
- Replace the original oversized demonstration roof with a short landing-only
  canopy, separate fascia, edge beams, structural columns, rain gutter,
  downpipes, wall caps and a layered metro roundel/label sign so the entrance
  keeps believable public-space proportions.
- Replace the placeholder roundel and bar glyphs with a full-UV station artwork
  derived from the shared official Anica logo, carrying the readable message
  `Welcome to Anica Station !` on a bevelled architectural sign backing.
  The artwork pipeline blooms the official logo first, composites the station
  wording afterwards, and supplies a separate black-field emissive mask so the
  3D sign never turns the wording into a glowing sticker.
- Give the entrance a structural portal and add façade joints, service door,
  utility box, transmissive poster glazing and interior shelf silhouettes so
  the opening reads as part of an occupied building rather than a freestanding
  stair prop.
- Split each long entrance glass wall into three framed single-surface panes.
  Their shared PBR material uses transmission, IOR, optical thickness and
  attenuation with automatic non-writing transparent depth behavior, keeping
  Character 1 visible behind glass throughout the side-camera shot.
- Extend the street into foreground, middle ground and background using framed
  façades, storefront glass, awnings and recessed dark/warm/cool window modules.
  Every window combines a reveal, metal frame, transmissive wet outer pane and
  deeper interior layer so oblique views have real parallax instead of a flat
  emissive card. Street lamps, distant towers and a primitive-built passing
  vehicle complete the depth. Tactile paving,
  slab seams, a patterned manhole, hydrant, bin and street sign supply human
  scale at ground level.
- Place three additional non-colliding skyline masses and sparse warm/cool
  window strips beyond the entrance, so the camera cuts reveal real parallax
  and several depth planes rather than stopping at the HDR background.
- Apply two purpose-made portrait poster textures to full-UV double-sided planes
  inside metal display frames, preserving readable `NIGHT CITY` and
  `ECHO STATION` artwork instead of using single-colour emissive panels.
- Layer cyan, magenta and amber practical lighting over low-intensity HDR image
  lighting and a cool shadow-casting moon key.
- Simulate a passing vehicle-light sweep with three timed `SpotLight` intensity
  curves, avoiding unsupported light-position animation.
- Use three deterministic `Repeat mode="volume"` rain layers in world space,
  with shorter near/mid/far streak geometry, camera parallax, depth testing and
  bounds beginning beyond the canopy edge. Keep only seven faint screen-space
  drops for lens proximity, then add animated canopy runoff, alpha-ring puddle
  ripples, compound splash crowns and restrained low mist.
- Reuse one compact alpha rivulet sheet across all six entrance panes with
  slight orientation and vertical-drift variation. Shared sticker/repair art,
  wall scratches, paper scraps and drain-side leaf clusters add restrained
  evidence of maintenance and daily use without adding colliders.
- Reduce stair and paving normal frequency, material variation and specular
  peaks while retaining bounded puddle reflections and the timed vehicle-light
  sweep. The passing car now also carries red tail lamps and a restrained red
  reflection sequence.
- Finish the HDR scene through ACES colour management, bloom and deterministic
  film grain.

## Camera schedule

- **0–3 s / frames 0–89:** character first-person stair ascent; the owner's
  beauty pass is camera-locally excluded while animation, collision and shadow
  casting remain.
- **3–6 s / frames 90–179:** close interior follow angle from the right side of
  the stair, under the canopy, with the complete character visible and a
  restrained forward dolly that never overtakes the actor.
- **6–9 s / frames 180–269:** street-level establishing view looking back at
  the exit as the character continues walking forward across the upper paving;
  a road-level car briefly crosses the lower foreground and then clears frame.

## Resource and validation notes

The cold representative-frame run decodes 21 textures (46,587,904 bytes).
The seven repository-hosted runtime decodes are the two 1024×1536 poster artworks,
the 1600×240 station sign, its 1600×240 logo-only emissive mask, one 512×256
ripple sprite, one 512×1024 rivulet sheet and one 512×512 human-trace sheet.
The logo-bloom intermediate is used only while authoring the final station-sign
artwork. All concrete, plaster, weathered concrete and metal maps remain shared
with S74. After preload, warm frames do not decode those resources again. The
rain volumes add no texture decode beyond the one shared ripple sprite:
their three retained primitive meshes and materials are shared while only
seeded transforms change. Transmission adds one reusable 1920×1080
RGBA8 opaque-scene snapshot (about 7.9 MiB) and one GPU texture copy per frame;
it adds no image decode and no per-pane render target. The authoring analyzer reports `clean`:
parsing and compilation both succeed with zero errors and zero warnings.

The visual baseline was checked at frames 0, 30, 89, 90, 120, 179, 180, 225
and 269. Those frames cover the moving first-person view, both camera-cut
boundaries, full-character stair follow, vehicle pass and wet street overview.
Frame 120 is an explicit transparent-depth regression point: the complete GLB
must remain visible while the camera grazes the right entrance glazing.
The final acceptance render covers all 270 frames in one GPU
renderer instance to exercise both camera cuts, the character's continuous
collider-driven ascent, the primitive vehicle and timed light sweep, and the
transition onto the street collider. Camera-cut boundary frames 89/90 and
179/180 preserve one continuous character, while frame 269 confirms that the
walk continues through the extended street shot.
