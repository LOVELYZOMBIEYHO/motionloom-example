# CP-000016 — Process Pass Mask

This example shows pass-level masking for process effects.

Use `main.motionloom` in Anica Layer FX. It expects the selected layer as
`input:clip0`, generates a soft center mask as a scene texture, then applies a
brightness pass only where the mask is bright.

Key DSL:

- `mask="mask_tex"` references another process resource.
- `maskMode="luma"` uses the mask texture brightness as alpha.
- `maskInvert="true"` can invert the mask when needed.

`main_with_scene.motionloom` is a standalone preview version with a built-in
source scene.
