# s-000035 High Detail Bishoujo Eye Gaze Squint

High-detail anime eye animation with a left gaze, return-to-center timing, and a controlled squint.

- Duration: `2s`.
- Canvas: `640x420`.
- Moves the eye and iris left, returns to center, then narrows into a squint.
- Uses layered iris gradients, sparkles, lashes, skin shading, and deterministic `curve(...)` animation.

Run:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000035/main.motionloom
```
