# AnimationTarget Control Room

Showcase 67 is a 12-second, editor-first demonstration of MotionLoom's typed
`AnimationTarget` system. The visual is intentionally presented as a live
control room: every major channel family is visible, labelled, and stored as
explicit keys in the same `.motionloom` document.

## What it demonstrates

- reusable numeric channels for transform, opacity, shape dimensions, camera,
  Puppet Pin, Skeleton Bone, and particle simulation properties;
- typed RGBA interpolation for `color`, `fill`, and text styling;
- editable SVG path morphing through `property="d"`;
- discrete/hold sampling for `Text.value` phase and readout changes;
- Vector3 interpolation for a true-3D model position;
- 3D scalar channels for rotation, scale, exposure, and camera field of view;
- Process parameter animation through `params.intensity` and `params.sigma`;
- deterministic channel precedence suitable for visual-editor and LLM
  read-modify-write workflows.

## Timeline

1. **0–3s — Numeric channels:** transforms, opacity, shape width, radius, and
   camera motion establish the control-room layout.
2. **3–6s — Typed visual values:** the center mark morphs its path and blends
   colors while text switches through discrete keys.
3. **6–9s — Rig and simulation:** Puppet Pin, Skeleton Bone, and particle rate
   channels move through the same target abstraction.
4. **9–12s — GPU graph:** the true-3D device, camera FOV, exposure, bloom
   intensity, and bloom sigma finish the cycle.

## Compatibility

The showcase uses only additive `AnimationTarget` capabilities. Existing inline
`curve(...)` syntax and older target properties remain supported by the engine;
an editor can inspect or patch any channel without rewriting the rest of this
file.

The device GLB is loaded from Showcase 66's repository-hosted attributed asset.
See that showcase's README for the original model credit and license.

Load **Showcase 67** in the MotionLoom Graph UI to preview it.
