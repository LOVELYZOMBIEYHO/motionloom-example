# Astronomer's Celestial Atlas 7s

A vintage MotionLoom DSL showcase of an aged celestial star chart coming to life
under candle light. A compass rose draws itself in the corner, three constellations
trace their paths across the navy parchment, and gold dust motes drift through
the warm candle glow. The title "CELESTIAL" reveals with a starlight sweep.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0-1s | Parchment Appears | Aged navy parchment fades in. Candle glow begins. Chart texture and ticks visible. |
| 1-2.5s | Compass Rose | Compass rose draws itself via path trim — outer ring, cardinal star, diagonals, N/E/S/W labels. |
| 2-4.5s | Constellations Draw | Three constellation patterns trace their connecting lines via trimEnd animation. Stars appear at vertices. |
| 4.5-7s | Title Reveal | "CELESTIAL" title reveals with starlight sweep. Subtitle "AND THE CELESTIAL ATLAS" appears. Warm vignette. |

## Visual Style

- **Aged navy parchment** background (`#1a1438`) with radial gradient
- **Gold/amber palette**: warm gold, cream highlight, deep ink navy
- **Compass rose**: path-trimmed cardinal star + rings + N/E/S/W labels
- **3 constellations**: "The Hunter", "The Crown", "The Serpent" — each with path-trimmed connecting lines and glowing star vertices
- **40 background stars**: tiny twinkling dots with procedural jitter
- **Candle light**: two warm radial glows in lower corners with flickering opacity
- **Gold dust motes**: 28 drifting particles with cosmic dust gradient
- **Ink notes**: monospace astronomical coordinates (LAT, LON, EPOCH, DECL)

## Light Effects (shared with s-000002)

- **Starlight sweep** — horizontal gradient rect sweeping across the title (like `gold_sweep`)
- **Chart scratch** — vertical gradient texture scratches (like `film_scratch`)
- **Warm flicker vignette** — `sin($time.sec*12.0)` pulsing cream overlay
- **Triple-layer title text** — dark shadow + warm gold body + cream highlight
- **Bloom process** — `effect="bloom"` threshold 0.12, intensity 2.05, sigma 18.0
- **Candle glow** — radial gradient circles with sin-based flicker
- **Ink splatter atmosphere** — dark radial gradients for depth

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000013/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000013/main.motionloom
```
