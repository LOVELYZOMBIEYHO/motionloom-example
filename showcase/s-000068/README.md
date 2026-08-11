# Quaternius Night Walk

Showcase 68 is a 16-second humanoid locomotion example built around MotionLoom's
canonical CC0 `character1.glb` and its embedded `Walk_Loop` clip. The first
half is a side-on city walk; the second is a frontal approach.

## What it demonstrates

- one raw GitHub-hosted GLB used as both `ModelAsset` and `AnimationAsset`;
- `AnimationAsset` as the raw clip container, an executable `Action` as the
  canonical motion layer, and `ApplyAction` referencing only the Action id;
- a reusable `ModelProfile`, humanoid retarget map, and calibrated bone axes;
- the same in-place walk action applied to two Scene model instances;
- two camera compositions and two directionally appropriate moving street
  backgrounds inside one deterministic timeline;
- portable CC0 assets suitable for local, browser, WASM, and published demos.

## Asset and attribution

The shared `assets/sample_assets/characters/character1/character1.glb` comes
from Quaternius' Universal Animation Library 1 and is released under CC0. The
script loads this canonical Character 1 asset through its raw GitHub URL.

Load **Showcase 68** in the MotionLoom Graph UI to preview `main.motionloom`.
