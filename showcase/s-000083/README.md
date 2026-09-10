# S83 — MotionLoom / Rose Copper

A silent burgundy-and-rose-copper motion study: 1920 × 1080, 30 fps, 20 seconds (600 frames). The title reads MOTIONLOOM, with the subtitle ROSE COPPER / LIGHT IN MOTION. No external image, model or audio assets are required. The browser host must register a font, as in the Landing Page.

## Visual sequence

- 0–4 s: fade from black, soft-to-sharp reveal and serif title.
- 4–8 s: lateral drift and gradual push across the evolving surface.
- 8–11.5 s: closer inspection with a blur-based focus pull.
- 11.5–16 s: ease back out with foreground rose-copper motes.
- 16–20 s: title reprise and fade to black.

## Implementation

`main.motionloom` is the source of truth. The new `procedural_surface` GPU Process generates domain-warped noise, folded relief, gold veins and pools per pixel. Finite-difference normals drive internal metallic-looking lighting. Native WGPU and WASM share the same WGSL and parameter evaluator. Evolution is sampled from absolute time, so random seeking does not accumulate simulation state.

The surface lives in one Scene; titles, motes and vignette live in a transparent second Scene and are composited afterward with `over`. Bloom and animated blur finish the image. `main2.motionloom` preserves the previous vector-contour version.

## Limits

The surface uses opt-in `flowStrength: "1"`: directional ribbons with analytic transport and coherent shear, rather than the original isotropic wrinkles. Lower relief and thinner copper edges reduce the embossed-metal appearance. Surface-only Gaussian blur rests at sigma 1.2, rising to 4.5 during the focus pull. Titles remain outside this blur pass. This is not physical fluid simulation or motion blur. Omit `flowStrength` to restore the original shader mode.

This is a 2D image effect with virtual relief, not mesh geometry, physical fluid simulation or Camera3D lighting. Output currently follows the RGBA8 compositor contract, not true HDR. Blur approximates focus; it is not depth-buffer DOF. CPU-only rendering fails explicitly. Standalone WASM Process masks are unsupported for this effect; use input alpha. S83 uses Scene-level Effects, not Group-level Effects. Other effects and existing DSL syntax remain unchanged.

## Preview / export

From the Anica repository:

```sh
target/debug/examples/wgpu_live_preview ../motionloom-example/showcase/s-000083/main.motionloom
target/debug/examples/render_file_video ../motionloom-example/showcase/s-000083/main.motionloom /tmp/s83-motionloom-rose-copper-1080p.mp4 gpu
```

See `VERIFICATION.md` for native/browser checks and measured limits. No Git push was performed.
