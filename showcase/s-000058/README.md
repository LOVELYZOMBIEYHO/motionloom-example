# Quick Puppet Pre-Rigged Arm IK

A deliberately small Puppet Warp test scene containing one arm and one
pre-authored three-point rig.

## Use it in the MotionLoom playground

1. Load `showcase 58`.
2. Open `Puppet Warp`.
3. Keep `Quick Puppet` selected.
4. Drag `character_art_arm_control_pin` at the wrist.

The shoulder pin is fixed. MotionLoom's bone solver updates the elbow
automatically while preserving the authored upper-arm and forearm lengths.
`Limb Width` controls the generated local mesh instead of applying a large
soft-deformation radius across the whole character.

If the DSL has been edited into an invalid rig, press `Reset Quick Rig` and
place the pins again in shoulder → elbow → wrist order. Quick Puppet writes
`solver="bones"`, pin roles, explicit vertex bone bindings, and the local
triangulated mesh into the DSL.

## Purpose

This example separates UI and IK behaviour from SVG segmentation. If this arm
works but an imported character does not, the remaining problem is the
character's target Group or path separation rather than the controller.

Render the rest frame:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000058/main.motionloom \
  /tmp/s-000058-arm.png 0 cpu
```
