# CP-000014 — Fixed HSLA Overlay Layer FX

This example shows the smallest normal Layer FX process for a fixed HSLA color
wash.

Use `main.motionloom` in Anica Layer FX. It expects the selected layer as
`input:clip0`, converts it into a process texture, applies
`effect="hsla_overlay"`, and presents the result.

Parameters:

- `hue`: `0.0` to `360.0` degrees.
- `saturation`: overlay saturation amount.
- `lightness`: overlay lightness amount.
- `alpha`: overlay opacity.

`main_with_scene.motionloom` is a standalone preview version with a built-in
scene source.
