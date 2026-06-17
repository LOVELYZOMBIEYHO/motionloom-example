# Aurora Borealis Symphony 8s

A cinematic MotionLoom DSL showcase of flowing northern lights dancing over a
mountain lake under a starry sky. Layered aurora curtains in green, teal, violet,
and pink drift across the screen while stars twinkle, a moon glows, and the lake
below reflects the colors.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0-1.5s | Night Falls | Sky gradient and star field fade in. Moon appears. Aurora begins to glow. |
| 1.5-4s | Green Curtain | The primary green aurora curtain flows across the sky. Teal accents build. |
| 4-6.5s | Full Spectrum | Violet and pink aurora curtains join. Light rays radiate. Particles float. |
| 6.5-8s | Title Reveal | "AURORA BOREALIS" title fades in with a glowing underline. Aurora softens. |

## Visual Style

- **Deep night sky** gradient from `#01030f` to `#0a1648`
- **Four aurora layers**: green, teal, violet, and pink flowing curtains
- **Mountain silhouettes** in three depth layers
- **Lake reflection** with shimmering horizontal lines and mirrored aurora
- **90 twinkling stars** plus 14 bright glowing stars
- **Glowing moon** with soft radial halo
- **Radial light rays** emanating from the aurora center
- **Floating particles** with procedural jitter

## Post-Processing

- **HSLA overlay** — Animated hue shift (160-200), saturation boost, lightness lift
- **Glow bloom** — Threshold 0.32, intensity animated 0.8 to 1.8 to 1.0

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000008/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000008/main.motionloom
```
