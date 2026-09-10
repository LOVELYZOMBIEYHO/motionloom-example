# S82 — Ashen Reeds

An original, Sekiro-inspired menu animation study, targeting the upper-left
reference's restrained blue-grey palette, silver reeds, close sword, mist and
small serif interface. No game logos, screenshots, textures or models are included.

## Playback

- 1280 × 720, 30 FPS, 16 seconds (480 frames).
- 0–6 s: menu idle, layered reed and cloud drift.
- 6–6.8 s: options panel fades/slides in and the menu dims.
- 6.8–11.8 s: options hold.
- 11.8–12.6 s: options close.
- 12.6–16 s: return to idle.
- Background motion uses a shared approximately 16-second sine period.
- All paths and keys live in main.motionloom; there are no external assets.

From the Anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000082/main.motionloom
```

## What this actually tests

This is **2.5D vector composition**, not a 3D vegetation benchmark. It tests
dense editable paths, depth bands, time expressions, gradient fog approximations,
typography, a faceted sword silhouette, scripted panel transitions and film grain.
The options are demonstration graphics, not wired settings or clickable controls.
In particular, the displayed DOF toggle is not an active Camera3D DOF setting.

## Gap ledger

### Missing or limited specialized capabilities in the inspected implementation

1. **Specialized silvergrass/plume geometry.** Vegetation V1 has generic grass,
   but no dedicated feathery seed-head morphology. The study authors awns as paths.
   This is not evidence that a custom mesh could not represent them.
2. **Fine foliage lighting.** No dedicated thin-fiber/plume scattering model was
   identified in the inspected 3D surface shader. Layered colours approximate the
   silver backlit appearance; they are not a scattering simulation.
3. **Detailed volumetric mist.** Existing AtmosphereFog provides analytic distance,
   height and bounded-volume attenuation. It does not provide the textured,
   self-shadowing rolling fog sought for this reference. Moving radial gradients
   are used here instead.

### Authoring choices, not missing engine features

4. **Sword shading.** The sword is vector geometry with a painted gradient.
   MotionLoom already has 3D primitives, GLB and PBR; this study does not exercise
   them and cannot establish a limitation in metal rendering.
5. **Wind and depth.** Bands translate at different phases; individual stalks do
   not bend physically. Existing vegetation wind was not used. There is no actual
   3D grass occlusion, contact, volumetric parallax or camera orbit in this scene.
6. **Depth of field.** MotionLoom has Camera3D DOF. These 2D paths do not supply
   the corresponding 3D scene depth, so this study uses tonal separation instead.
7. **Interaction.** Panel states are timeline-authored. Interactive input/settings
   would require host integration; they are deliberately not implemented here.

The result approaches the composition and mood, but **does not match the
reference's soft, dense, physically lit vegetation realism**. More intricate
vector art alone would not prove that the underlying 3D rendering gaps are solved.

## Validation

Native GPU frame renders inspected at frames 0, 240 and 479: idle, options open,
and loop return. Parser and generated showcase schema checked. Browser/WASM
playback and sustained playback FPS have not been measured.

Only S82 is added; no engine or earlier showcase is changed by this study.
