# Audio Spectrum

A stylized audio spectrum scene using deterministic random motion to mimic reactive frequency activity.

## Teaches

- Repeated frequency bars with per-frame procedural movement.
- Gradient bar fills, reflections, labels, and stage lighting.
- Scene-only audio-reactive visual language without requiring real audio input.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000019/main.motionloom /tmp/frame.png 0 cpu
```
