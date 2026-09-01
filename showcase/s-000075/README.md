# S75 — Native Primitive Humanoid

This twelve-second showcase builds and animates a complete stylized humanoid
from 35 typed primitive instances. It contains no GLB, FBX, image texture, or
external animation dependency. Its canonical `humanoid_v1` motions are copied
verbatim from `anica-landing-page/public/motionloom-actions/actions`, wrapped
as standalone libraries, and selectively imported by namespace.

## What this example tests

- Add `capsule` to the first-class PrimitiveAsset geometry and automatic
  collider contracts.
- Bind an existing `CompoundAsset` to an existing `Skeleton` with `rig`, then
  attach each Instance to a canonical humanoid Bone.
- Use `Skeleton space="3d"` with local XYZ positions while preserving the
  established 2D Skeleton syntax.
- Reuse the landing page's standard walk, listening idle, wave greeting, and
  standard run Action Editor code through four selective `ActionLibrary`
  declarations.
- Keep all 35 visual pieces non-colliding and give the parent Model one simple
  kinematic capsule RigidBody.
- Give the back wall a solid PrimitiveAsset collider and static RigidBody. The
  final run stops with clearance for both the capsule and animated limbs, then
  returns to idle; every Camera3D remains on the visible side of the wall.
- Share 24 retained primitive meshes/materials across 35 parts and all 360
  frames. The representative native render reports 39 draw calls, zero image
  decodes.
- Cut from a wide walk view to idle profile, face/body wave detail, and a wall
  approach view without rebuilding or importing the character.

## Runtime contract

Bone rest positions and rotations are local to their parent. Action
`rotationX/Y/Z` channels are additive; canonical semantic channels map
forward/bend to X, turn/twist to Y, and side to Z. Instance offsets are then
applied in bone space before the parent Model transform. The identical matrices
feed normal PBR and shadow rendering. Scheduled ApplyAction windows select the
active native clip at the current frame. The parent capsule opts into
`continuousCollision`, so its timeline target is swept against the solid floor
and wall before the 35 visual children are expanded.

## Validation

The authoring report is `clean` with no errors, warnings, ignored attributes,
or missing assets. Native Metal renders are checked across walk, idle, wave,
run, and the final wall-safe idle. Parser, capsule mesh, scheduled native-rig
actions, 3D hierarchy sampling, native compilation, and wasm32 compilation are
covered by the crate validation commands documented in the project handoff.
