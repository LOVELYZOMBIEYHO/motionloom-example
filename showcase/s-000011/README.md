# Phoenix Ascension Ember Storm 7s

A fiery MotionLoom DSL showcase of a phoenix rising from ash and ember. The
phoenix emerges from a glowing ignition core, spreads flame-trimmed wings, and
soars upward surrounded by a storm of rising embers. The title "PHOENIX" reveals
with an ember-colored light sweep.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0-1.5s | Ashes & Smoke | Dark ember bed with smoke pillars rising. Ignition core begins to glow. Ember spark trail rises. |
| 1.5-3s | Ignition | The phoenix body draws itself via path trim. Head crest appears. Wings begin to spread. |
| 3-5s | Ascension | Full wings spread with 7 feathers each. Tail flames extend. Phoenix rises upward. Ember storm peaks. |
| 5-7s | Title Reveal | "PHOENIX" title reveals with ember sweep light pass. Subtitle "FROM THE EMBERS REBORN" appears. Warm flicker vignette. |

## Visual Style

- **Deep ember black** background (`#0a0404`) with radial ember base glow
- **Fire palette**: white-gold core, amber, orange, deep red, charcoal
- **Phoenix body**: flame-shaped path with gradient fill
- **Wings**: 7 feathers per side via `Repeat` + `rotationStep`, each with `trimEnd` draw-on animation
- **Tail**: 5 flame paths fanning downward
- **Ember storm**: 40 rising ember particles + 28 spark particles with procedural jitter
- **Smoke clouds**: warm gray radial gradients rising and dissipating

## Light Effects (shared with s-000002)

- **Ember sweep** — horizontal gradient rect sweeping across the title (like `gold_sweep`)
- **Ember scratch** — vertical gradient texture scratches (like `film_scratch`)
- **Warm flicker vignette** — `sin($time.sec*16.0)` pulsing orange overlay
- **Triple-layer title text** — dark shadow + warm orange body + gold highlight
- **Bloom process** — `effect="bloom"` threshold 0.14, intensity 2.15, sigma 18.0
- **Atmospheric smoke** — radial gradient clouds for depth

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000011/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000011/main.motionloom
```
