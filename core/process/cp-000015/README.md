# CP-000015 — Paper Texture Overlay

This example shows `effect="texture_overlay"` as a Layer FX process.

Use `main.motionloom` in Anica Layer FX. It expects the selected layer as
`input:clip0`, applies a procedural paper texture, and presents the result.

Parameters:

- `kind`: `paper`, `noise`, `film_grain`, or `scanlines`.
- `scale`: texture frequency.
- `strength`: overlay strength from `0.0` to `1.0`.
- `contrast`: texture contrast.
- `seed`: deterministic pattern offset.

`main_with_scene.motionloom` is a standalone preview version with a built-in
paper card scene and a `<Texture />` definition for the scene-side DSL surface.
