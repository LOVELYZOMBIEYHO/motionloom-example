# Full-Character Puppet Rig Progression

This showcase explores three ways to rig the same imported full-body character
while keeping the editable result in MotionLoom DSL.

- `main.motionloom` is the polished single-arm demonstration. It uses an
  explicit two-bone mesh with shoulder and elbow seam-completion triangles.
- `main2.motionloom` captures the complete character as one alpha mesh and
  exposes fourteen independent position pins.
- `main3.motionloom` provides five selectable two-bone rigs for the head and
  neck, both arms, and both legs. Each rig uses an explicit local topology so
  large poses do not cut white holes into the character.

The files are intentionally kept together: they demonstrate the trade-off
between a single-purpose authored topology, an unrestricted full-surface mesh,
and full-body Bone Pin controls.

## Preview

Load any of the three `.motionloom` files in the MotionLoom Graph UI. In
`main3.motionloom`, open **Puppet Warp → Limb IK** and switch the Active Limb to
pose all five bone solvers.
