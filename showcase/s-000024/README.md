# Green Screen Subscribe Animation 5s

A green-screen subscribe/like/bell animation built entirely with MotionLoom scene primitives.

## Timeline

| Time | Action |
|------|--------|
| 0.0s | Green-screen background and white control panel appear. |
| 0.9s | Cursor moves to the like icon. |
| 1.3s | Like icon turns blue and the underline expands. |
| 2.7s | Cursor clicks the subscribe button. |
| 2.9s | Red subscribe button changes to grey subscribed state. |
| 3.9s | Cursor clicks the bell. |
| 4.0s | Bell turns active grey and rings with side motion lines. |
| 4.7s | Animation fades out. |

## Notes

- Uses a chroma-green `Background` for keying in video editors.
- No external images or logo assets are required.
- The design is generic and original; it does not include any licensed YouTube logo.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000024/main.motionloom /tmp/frame.png 45 cpu
```
