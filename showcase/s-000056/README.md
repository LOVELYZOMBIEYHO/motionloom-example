# Neon Loading Uplink

A focused seven-second cyberpunk loading scene with a perspective tunnel, three-dot loading indicator, progress bar, animated uplink beacon, deterministic RGB glitches, and scan-line tears.

The scene first applies `ChromaticAberration` through a reusable filter. Its output then enters a GPU `Process` where a Bloom pass creates the final cyan-magenta glow.

## What this showcase demonstrates

- A complete loading interface made from `Text`, `Rect`, `Circle`, `Path`, and `Group` nodes.
- Independent repeating opacity curves for three loading dots.
- One timeline coordinating progress, tunnel motion, glitch slices, and scan lines.
- Scene-level chromatic separation plus deterministic RGB echo geometry.
- A Scene-to-Process pipeline using `Tex`, `Pass`, and `Present`.

## Preview

From the `anica` repository, use the GPU path for the final Bloom process:

```sh
cargo run --release -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000056/main.motionloom
```

