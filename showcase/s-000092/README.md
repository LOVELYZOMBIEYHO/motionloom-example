# S92 — The Last Baton

A 12-second, 1280×720, 24 fps golden-hour film of a solo 100 m sprint finish.
One Character1 runner storms the home straight at 18.3 km/h, breaks the tape at
a procedural finish arch and decelerates through the line. Every hero prop —
the baton, the runner cap mesh, both arch posts and the sagging crown — is
modeled **entirely from `MeshAsset` control cages**: no GLB, no external mesh
files. The bowl, straight and finish have been re-staged so the sprint cadence
matches the ground speed and the finish lands inside the engine's shadow box.

## The MeshAsset showcase

This example exists to teach cage authoring end to end. Each prop is one
`<MeshAsset>` block of `<Vertex position={[x,y,z]} />` + `<Face indices={[...]} />`
lines with a catmull-clark subdivision level:

| Prop | Cage technique | Verts | Faces |
| --- | --- | --- | --- |
| Baton core | 6 swept rings tapered tip→belly→tip, triangulated end caps, **pinned** tip rings | 48 | 42 |
| Baton grip | 3 rings, fatter middle, pinned caps (a second asset snapped to the same socket) | 24 | 18 |
| Runner cap | crown triangle fan + two rings + brim band; **pinned** brim keeps the visor flat | 30 | 28 |
| Arch posts | 6 levels of 8-vertex rings; per-level x-offset bends the column inward | 48 | 42 |
| Arch crown | tube swept along x with drooping end rings, pinned at the post joints | 40 | 34 |

Rules shown in practice:

- Vertices live in **asset-local** meters; faces are zero-based indices.
- `pinned="true"` holds silhouette-critical vertices (sharp tips, flat brims,
  column joints) while the rest of the cage relaxes under subdivision.
- One `material=` per cage: the red grip is a second small MeshAsset snapped to
  the same palm socket instead of a multi-material escape hatch.
- Colour variants stay **copy-and-recolour** — a cage is just text, so
  variants are diffs, not new pipeline features.

## Props on a moving skeleton

Two `Attachment` blocks bind the baton to canonical humanoid bones:

- the baton (core + grip, two `Model`s, one socket each) snaps to
  `s92_hero_a.hand_r`, so it rides every arm swing.

## Acting: the standard sprint into the slow-run coast-down

The solo actor uses one `ModelProfile` (`character1.glb` → `humanoid_v1`) and
timed `ApplyAction` imports:

| Time | Hero (lane z=0) |
| --- | --- |
| 0 – 10.353 s | `sprint_standard_loop` loop, speed 1.0 (one second past the tape) |
| 10.353 – 10.553 s | `sprint_to_slow_run_handoff`, an authored 0.2 s crossfade Action |
| 10.553 s → end | `slow_run_standard_loop` loop |

All three beats use `blendIn="0s"`: MotionLoom's override merge ramps a partial
weight from the rig's rest pose, so a non-zero `blendIn` on a full-body
locomotion Action leaks a T-pose. The handoff Action
(`assets/action_libraries/landing_page/sprint-to-slow-run.motionloom`) carries
the 0.2 s morph between the sprint pose at the cut and the slow-run start pose
instead, and the runtime plays it at full weight.

`slow_run_standard_loop` is a converted Mixamo "Slow Run" clip: see
`assets/action_libraries/landing_page/slow-run-standard.motionloom`, converted
with `motionloom-action-tool convert --target-model character1.glb
--target-profile character1-scene.motionloom --target-profile-id
character1_profile --target-height 1.82`. Both clips are played at their
authored root speeds — 5.084 m/s (18.3 km/h) and 2.639 m/s (9.5 km/h) — which
were measured from each clip's own root travel and are the speeds at which the
feet plant without sliding.

Both loops are **`rootMotion="in_place"`**: the skeleton holds its stride while
deterministic `AnimationTarget` position keys carry the runner down the track at
5.084 m/s (−45.55 → 2.0 m at the tape), one more second at race pace, then a 0.2 s
brake (aligned with the handoff Action) into the 2.639 m/s jog and 11.68 m. `ground="s92_track_top"` with
`floorSnap` and a kinematic collider keeps every sole on the rubber.

## The edit

Four shots using three cameras, cut with discrete `activeCamera` keys — 3 seconds each:

1. **0 – 3 s** first-person sprint down the straight. The POV camera rides the
   head with a stride-frequency bob and roll, and `hiddenBones` removes the
   runner's own head and upper chest from this camera only;
2. **3 – 6 s** infield photographer pan: a 34 mm dolly that tracks the
   sprinter across the frame with the full grandstand behind him;
3. **6 – 9 s** back to first person for the run at the tape;
4. **9 – 12 s** finish camera in front of the arch, easing back to watch him
   break the line, hold race pace for a beat, then roll into the slow run and
   jog toward the lens.

## Render style

The scene ships three named `<RenderStyle>` presets and switches with the
`renderStyle` attribute on the scene root:

| id | look |
| --- | --- |
| `s92_pbr` (active) | physical shading, no grade override (the island's ACES golden-hour ColorManagement applies), plus `AntiAliasingStyle method="taa" quality="ultra" fallback="smaa" sharpness="0.06"` - the film renders with the engine's top temporal AA (8 jitter phases) |
| `s92_cel` | cel shading, 3 steps, hard cel shadow (`shadowFeather="0.015"`, cool `shadowColor="#39406B"`), hard shadow-map filtering |
| `s92_tone2` | two-step toon surface + duotone grade (violet shadows, warm highlights) |
| *(attribute removed)* | the natural ACES golden-hour grade |

Cel-shadow knobs: `shadowThreshold` (shadow area), `shadowFeather`
(`0.001` = razor edge), `shadowColor`, `shadingSteps`, and the
`<LightingStyle shadowStyle>` flag. An `<OutlineStyle enabled="true" ...>` adds
ink lines if the full cel package is wanted.

## Light and finish

A low warm sun key (the only shadow map), cool sky fill, a point lamp over the
finish, AO, contact shadows and a warm exponential haze build the golden hour.
ACES runs at 5200 K; the `glow_bloom` pass is keyframed to flare through the
tape break and settle during the coast-down; deterministic film grain (seed 92)
and a vignette close the image. Two seeded `Repeat mode="volume"` systems rain
gold and pink confetti over the finish area, and the crowd on the concrete
tiers is instanced from one `CompoundAsset` silhouette.

## Verification

Verified 2026-09-15 against the committed engine, Apple M2,
`SceneRenderProfile::Gpu`.

- Parse + render: the authoring analyzer reports `clean` / renderable, and the
  full 288-frame (12 s) export runs clean via `render_file_video`.
- Inspected frames: 24 and 60 (POV with hidden head, clear corridor), 108
  (photographer pan with the grandstand), 226 (tape break with the runner's
  cast shadow through the line), 240 and 287 (arch, title card, coast-down)
  all match the four-shot intent. The 0.2 s handoff was verified frame by frame
  across the cut (frames 246-262).
- **Staging sits inside the engine's fixed shadow box.** The directional
  light's shadow map is a 28 m box centred on world (0, 2, 0); anything outside
  it drops its cast shadow. The run is therefore staged from −45.55 m to 2.0 m
  at the tape (47.55 m of straight) so the tape break and the whole finish
  camera live inside the box — the runner casts a long golden-hour shadow
  through the line. The old far-end stand slabs and end-tier wedges crossed the
  track at x ≈ −32…−41 and were off the travelled corridor before; they are
  dropped from the staging so the corridor and the POV camera stay clear.
- The straight is a 68 m bed centred at x=−19 with the finish arch, banner,
  lamp and confetti volume at x=2.0; the grandstand, masts, flood banks and
  crowd rows already cover the staging.
- **Sky texture.** `assets/sky.png` (a hazy cloud photograph, cropped to its
  sky half and pre-scaled to 1740x503) is drawn as an `<Image>` over the
  gradient in the screen-space sky layer, drifting ~8 px/s and held at 0.78
  opacity so the warm gradient underneath keeps the golden-hour grade. Swap the
  file to change the sky; the node draws it 1:1, so keep the size or edit
  `scale`.
- **Sky.** A screen-space cloud deck (soft radial-gradient `Circle` clusters
  under a warm haze band) sits between the sky gradient and the sun glow, and
  each cluster drifts at its own constant speed (90-250 px over the film, plus
  a small vertical drift) so the sky reads as moving air and the layers give a
  cheap parallax. Drift is keyed `linear` from frame 0: an `ease_in_out` curve
  over the whole film starts at zero velocity and the clouds look pinned during
  the first POV shot. Note: `Ellipse` and gradient-filled `Path` nodes do not
  draw on the GPU 2D path in this build, so the clouds are clustered circles.
- **Crowd trimming.** The bowl's end-stand crowd rows sat on tier slabs the
  corridor clearing removed, and from the low start camera they silhouetted
  above the roofline reading as floating figures. The five field-side rows
  (z > −12, standing on the infield edge) and the three back rows (y > 5 m,
  over the roofline) are dropped; the tier rows inside the grandstand stay.
- **Infield dressing.** Three hurdles, a long-jump sand pit with a take-off
  board, two starting blocks at the old start, eight lane cones, two officials'
  benches and a press tripod fill the empty apron beside the track.
- The slow-run clip was converted offline with `motionloom-action-tool`
  (ufbx evaluation, Character1 target profile). The source FBX is not
  redistributed: only `slow-run-standard.motionloom` exists under the action
  folders.
- MeshAsset cages: the baton, the arch post/crown and the banner draw through
  the modern `<Scene>` 3D path; pinned vertices keep tips and column joints
  crisp at subdivision levels 1-2.
- The baton `Attachment`/`Socket` pair (baton -> `hand_r`) is authored like
  s91's sword grip; at this revision the modern `<Scene>` path parses but does
  not yet apply attachments, so the baton renders at its declared start-line
  position until the WIP scene-attachment pass lands. The film does not depend
  on the attachment for its blocking.
