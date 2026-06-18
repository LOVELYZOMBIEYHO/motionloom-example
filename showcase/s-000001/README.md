# ANICA Cyberpunk City Reveal 7s

A scene-only MotionLoom cyberpunk city poster reveal inspired by vertical neon city compositions.

## Timeline

| Time | Action |
|------|--------|
| 0.0s | Foggy city and towers appear. |
| 0.6s | ANICA title glows in at the top. |
| 1.0s | Slow camera drift starts. |
| 2.0s | Rain, windows, billboards, and debris create motion. |
| 7.0s | Scene holds as a short cinematic loop. |

## Notes

- No external images, logos, or licensed assets.
- The ANICA logo text is original DSL text, not an imported image.
- Built from `Rect`, `Path`, `Text`, `Repeat`, gradients, and timed camera motion.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000001/main.motionloom /tmp/s-000001.png 90 cpu
```
