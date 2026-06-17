# Samurai Ink Storm 20s

A five-shot sumi-e action title sequence with ink clouds, samurai silhouette, cherry petals, katana slashes, and a red-white finale.

## Five Shots

| Time | Shot | Description |
|------|------|-------------|
| 0-4s | **INK RISES** | Black sumi ink blooms over paper grain with drifting dust and red accents. |
| 3.5-8s | **THE WARRIOR** | A samurai silhouette resolves from smoke with katana and armor lines. |
| 7.5-12s | **CHERRY STORM** | Petals fall across a branch while the scene shifts pink-red. |
| 11.5-16s | **KATANA SLASH** | Three trim-animated slash paths cut across the frame with impact glow. |
| 15.5-20s | **FINAL SEAL** | The title SAMURAI INK STORM appears inside particles and burst light. |

## Visual Style

- Five distinct timed compositions inside one MotionLoom scene.
- Smooth opacity crossfades plus brief white transition flashes.
- GPU-friendly scene primitives: gradients, paths, text, repeat fields, and numeric curves.
- Bloom process at the end for stylized glow.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000016/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000016/main.motionloom
```
