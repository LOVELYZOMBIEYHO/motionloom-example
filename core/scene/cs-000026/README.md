# Character 1 Humanoid Action

ID: `cs-000026`  
Type: `core`  
Domain: `scene`

## Features

GLB asset, skinned model, humanoid profile, retarget mapping, embedded action,
action playback, true 3D

## Canonical pipeline

```text
ModelAsset → ModelProfile → Action → ApplyAction
```

`AnimationAsset` is the low-level raw clip container. `Action` wraps its
embedded `Walk_Loop` clip as a portable executable motion, and `ApplyAction`
references only that Action id.

## Teaches

- Load the canonical `character1.glb` from the repository's raw GitHub URL.
- Map its Quaternius joints to MotionLoom `humanoid_v1` through `ModelProfile`.
- Keep raw animation data behind `AnimationAsset` and expose it through a
  canonical `Action`.
- Apply the same deterministic walk loop in native, browser, and WASM hosts.

## Asset

`character1.glb` is Quaternius Universal Animation Library 1 content released
under CC0.

## Use in Anica

Open `main.motionloom`, copy all content, then paste it into the Anica
MotionLoom page.
