# Pinwheel zDepth Layer Sorting 4s

A compact scene-only MotionLoom demo showing how `Layer zDepth` changes the draw order of overlapping shapes.

## Timeline

| Time | Action |
|------|--------|
| 0.0s | Four colored pinwheel blades appear around the center. |
| 0.0s-4.0s | Each blade rotates slightly while retaining its layer depth order. |
| 4.0s | Scene holds on the final sorted pinwheel layout. |

## Notes

- Scene-only example; no process pass or external assets.
- Negative `zDepth` layers render closer than positive `zDepth` layers.
- Useful as a small visual test for layer ordering and zDepth behavior.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000001/main.motionloom /tmp/s-000001.png 60 cpu
```
