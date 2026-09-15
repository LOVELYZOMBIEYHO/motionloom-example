# S92 — The Last Baton

A 14-second, 1280×720, 24 fps golden-hour film of a relay finish. Two
Character1 runners storm the home straight, the hero breaks the tape at a
procedural finish arch, decelerates and raises his baton while his rival
closes in. Every hero prop — the baton, both runner caps, both arch posts and
the sagging crown — is modeled **entirely from `MeshAsset` control cages**: no
GLB, no external mesh files.

## The MeshAsset showcase

This example exists to teach cage authoring end to end. Each prop is one
`<MeshAsset>` block of `<Vertex position={[x,y,z]} />` + `<Face indices={[...]} />`
lines with a catmull-clark subdivision level:

| Prop | Cage technique | Verts | Faces |
| --- | --- | --- | --- |
| Baton core | 6 swept rings tapered tip→belly→tip, ngon end caps, **pinned** tip rings | 48 | 42 |
| Baton grip | 3 rings, fatter middle, pinned caps (a second asset snapped to the same socket) | 24 | 18 |
| Runner caps | crown triangle fan + two rings + brim band; **pinned** brim keeps the visor flat | 30 | 28 |
| Arch posts | 6 levels of 8-vertex rings; per-level x-offset bends the column inward | 48 | 42 |
| Arch crown | tube swept along x with drooping end rings, pinned at the post joints | 40 | 34 |

Rules shown in practice:

- Vertices live in **asset-local** meters; faces are zero-based indices.
- `pinned="true"` holds silhouette-critical vertices (sharp tips, flat brims,
  column joints) while the rest of the cage relaxes under subdivision.
- One `material=` per cage: the red grip is a second small MeshAsset snapped to
  the same palm socket instead of a multi-material escape hatch.
- Colour variants (red vs blue cap) are **copy-and-recolour** — a cage is just
  text, so variants are diffs, not new pipeline features.

## Props on a moving skeleton

Two `Attachment` blocks bind the props to canonical humanoid bones:

- the baton (core + grip, two `Model`s, one socket each) snaps to
  `s92_hero_a.hand_r`, so it rides every arm swing;
- the caps snap to each runner's `head` bone, so the visor tracks the forward
  lean of the sprint and lifts back during the victory wave.

## Acting: four landing-page actions, three beats

Both actors share one `ModelProfile` (`character1.glb` → `humanoid_v1`). The
finish is choreographed purely with timed `ApplyAction` imports:

| Time | Hero (lane z=0) | Rival (lane z=1.2) |
| --- | --- | --- |
| 0 – ~7 | `run-standard` loop, speed 0.85 | `run-standard` loop, speed 0.83 |
| ~7 – ~8.2 | `standard-walk` stop blend-out | walk stop |
| ~8.1 → end | `wave-greeting` (slow, looping) = the baton lift | `listening-idle` = catching breath |

The run loops are **`rootMotion="in_place"`**: the skeleton holds its stride
while deterministic `AnimationTarget` position keys carry the runners down the
track (hero −3.8 → 8.2 m at the tape, decelerating to a stop at 10.55 m; rival
one beat behind and stopping alongside). `ground="s92_track_top"` with
`floorSnap` and a kinematic collider keeps every sole exactly on the rubber.

## The edit

Three cameras, cut with discrete `activeCamera` keys:

1. **0 – 4.3 s** side tracking shot at hip height, trucks with the hero;
2. **4.3 – 8.5 s** arch camera looking back into the low sun as the tape
   breaks and the rival crosses;
3. **8.5 – 14 s** victory push-in while the baton rises and the title card
   settles in.

## Light and finish

A low warm sun key (the only shadow map), cool sky fill, a point lamp over the
finish, AO, contact shadows and a warm exponential haze build the golden hour.
ACES runs at 5200 K; the `glow_bloom` pass is keyframed to flare through the
tape break and open up for the raise; deterministic film grain (seed 92) and a
vignette close the image. Two seeded `Repeat mode="volume"` systems rain gold
and pink confetti over the finish area, and the crowd on the concrete tiers is
instanced from one `CompoundAsset` silhouette.

## Verification

Verified 2026-09-14 against the committed engine (`dc65dfe`), Apple M2,
`SceneRenderProfile::Gpu`, warm frame ≈ 39 ms, 136 draw calls, ~39k visible
triangles.

- Parse + render: `render_file_frame_gpu` succeeds end to end; frames 30 (side
  truck), 103 (tape break), 205 (stop + wave blend), 316 (victory push-in) were
  inspected; the full 336-frame export runs clean.
- MeshAsset cages: all six cages weld, subdivide and draw through the
  modern `<Scene>` 3D path (the arch post/crown/baton are visibly correct in
  frame). The end-cap triangle fans and pinned vertices keep tips, brims and
  column joints crisp at subdivision levels 1–2.
- Action sequencing / cameras / grade / confetti: all confirmed in rendered
  frames.
- Authoring analyzer reports `needs-repair` with **only** the 12
  `UNKNOWN_TAG Attachment/Socket/Attach` items — the same class of
  analyzer-lag the committed s91 also exhibits at this revision.
- **Pending the in-flight scene-render attachment work**: the four
  `Attachment` blocks (baton → `hand_r`, caps → `head`) are authored exactly
  like s91's sword grip. At the committed revision the modern `<Scene>` path
  parses but does not yet apply attachments, so the props render at their
  declared start-line positions instead of riding the bones; they snap to the
  skeleton once the WIP scene-attachment pass lands.
