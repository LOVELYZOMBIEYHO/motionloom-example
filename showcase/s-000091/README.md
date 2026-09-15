# S91 — Hanamachi: A Japanese Canal Town

An 18-second, 1280×720, 24 fps scenic film of a canal town on a clear day.
The first 3.5 seconds hold the high overlook of the whole town; the film then
cuts to the centre of the street where **a Character1 swordmaster** performs the
Great Sword Casting routine.

## The sword performance

- **Character1 is the actor**: the canonical `character1.glb` performs through
  a `ModelProfile` at `scaleMode="normalize_height"`.
- **FBX → MotionLoom DSL**: `assets/Great Sword Casting.fbx` (Mixamo, 4.78 s)
  was converted offline by `motionloom-action-tool` in target-bound mode against
  the Character1 rig. The result is a MotionLoom `Action`
  (`assets/actions/great_sword_casting.motionloom`, 513 canonical poses) and is
  scheduled through `ActionLibrary`.
- **Sword**: the prop is built entirely from MotionLoom `PrimitiveAsset`
  geometry: bevelled blade and edge strips, a four-sided point, bronze guard,
  wrapped grip and pommel. One Graph-level `Attachment` aligns the sword's
  primary `main_grip` Socket with Character1's canonical `hand_r`, then the
  existing two-bone IK solver moves `hand_l` to `support_grip`. The prop needs
  neither a copied Skeleton nor a second ApplyAction.
- The performer loops the routine for the remaining 14.5 s and the camera cuts
  from the town overlook to a street-level shot at 3.5 s.
- **Root motion carries the crouch**: the `ApplyAction` uses
  `rootMotion="clip"`. The converted clip keeps its `hips` translation
  (a 0.33 m drop and 0.44 m lunge that returns to the start each loop); with
  `rootMotion="in_place"` that translation is zeroed, so the crouch collapses
  into a leg tuck and the figure appears to float upward as the sword swings
  down. With `clip` the performer crouches and bows into the cast while the
  head drop reads correctly (e.g. frame 260: hips 0.85 → 0.52 m).
- **Stage and grounding**: the performer stands on the near-bank road at the
  bottom of the opening composition (`position={[0,0.0,13.1]}`), between the
  canal-side railing and the foreground pavement. An invisible `Surface` marks
  that pavement top (`y=0`) and the `ApplyAction` binds to it with
  `ground="s91_stage_ground" floorSnap="0.25" safeMargin="0.01"
  sweepStep="0.03"`; with `collision="kinematic"` on the model the solver
  reports `grounded=true`, `ground_hit=0.0` and zero correction, so the soles
  rest exactly on the road with no clipping.

## The town

- **Torii gate and shrine** on a terraced hill reached by a flight of stone
  steps, flanked by stone lanterns.
- **Machiya wooden houses** with hip-and-gable tiled roofs, noren curtains,
  lattice windows, shop awnings and hanging signboards along a shopping street.
- **Canal with stone banks** crossed by a small arched bridge; ripples breathe
  outward across the water in four phase-shifted cycles.
- **Sakura trees** line both banks, their blossom foliage animated by the
  vegetation wind solver.
- **Utility poles with sagging wires** and two **vending machines** anchor the
  street; paper lanterns hang from an eave wire and sway in the breeze.
- **Mountain range with Mount Fuji** closes the horizon, layered into
  exponential haze.

## Living environment

| Motion | Implementation |
| --- | --- |
| Falling sakura petals | two `Repeat mode="volume"` systems (near and far) with drift |
| Swaying lanterns | per-lantern `AnimationTarget` sway with staggered phases |
| Water ripples | expanding `CompoundAsset` ring segments with scale animation |
| Chimney smoke | volume repeat of soft translucent puffs rising from a chimney |
| Drifting clouds | compound cloud models on slow linear position tracks |
| Wind in the plants | `VegetationAsset wind="true"` on trees, shrubs and grass |

## Light and finish

A warm shadow-casting sun key, a cool sky fill, ambient occlusion, contact
shadows and an exponential fog lay out the depth. ACES colour management,
a restrained bloom and deterministic film grain complete the image. The
opening camera holds a high overlook with a very slow settle before the cut to
the performer.

## Verification

The authoring analyzer reports `clean` with zero errors and zero warnings. The
target-bound converter reports 0.7704 mm maximum positional reconstruction
error and 0.0990° maximum rotational reconstruction error across the generated
Action poses.
