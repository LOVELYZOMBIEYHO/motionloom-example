# Clockwork Universe 20s

A five-shot cosmic machine sequence with brass gears, orbital clocks, star map rings, mechanical eclipses, and a universe-core finale.

## Five Shots

| Time | Shot | Description |
|------|------|-------------|
| 0-4s | **BRASS WAKE** | Large gears emerge over a star field. |
| 3.5-8s | **ORRERY** | Planets orbit inside nested rings. |
| 7.5-12s | **STAR CLOCK** | A celestial clock face draws hands and tick marks. |
| 11.5-16s | **ECLIPSE ENGINE** | Mechanical shutters close over a glowing eclipse. |
| 15.5-20s | **UNIVERSE CORE** | All rings converge into a bright clockwork title. |

## Visual Style

- Five distinct timed compositions inside one MotionLoom scene.
- Smooth opacity crossfades plus brief white transition flashes.
- GPU-friendly scene primitives: gradients, paths, text, repeat fields, and numeric curves.
- Bloom process at the end for stylized glow.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000017/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000017/main.motionloom
```
