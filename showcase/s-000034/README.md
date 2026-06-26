# s-000034 Dual Eye Gaze Blink

Two stylized eyes move their gaze outward and inward, then blink together with coordinated eyelid overlays.

- Duration: `5s`.
- Canvas: `1320x768`.
- Uses reusable eye components for mirrored left and right eyes.
- Combines iris travel, squash at gaze extremes, grid deformation, and blink opacity timing.
- Uses deterministic `curve(...)` animation for gaze, deformation, blink compression, and background opacity.

Run:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000034/main.motionloom
```
