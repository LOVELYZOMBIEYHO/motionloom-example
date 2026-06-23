# s-000033 Bass Pulse Six-Line RGB Glitch Portrait

Portrait RGB glitch typography promo cut into six `1.5s` text hits for fast DnB / club audio.

- Duration: `9s`.
- Canvas: `1080x1920`.
- Text beats: `AFRAID?`, `OF FAILING?`, `DON'T WORRY`, `MOVE ANYWAY`, `NO EXCUSES`, `JUST DO IT!`.
- Adds scanline movement, side meter bars, RGB split jitter, beat flashes, radial pulses, and heavier glow.
- Uses deterministic `sin(...)`, `random(...)`, and `curve(...)`; no audio analysis is required.

Run:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000033/main.motionloom
```
