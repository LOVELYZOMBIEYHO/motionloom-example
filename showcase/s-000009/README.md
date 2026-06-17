# Lotus Bloom Meditation 6s

A serene MotionLoom DSL showcase of a golden lotus flower blooming from its center
outward, surrounded by a sacred geometry mandala. Three concentric petal rings
unfold with path trim animation while golden particles rise and halo rings expand.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0-1s | Awakening | Mandala background fades in. Center glow begins. Sacred geometry rings appear. |
| 1-2.5s | Inner Bloom | Inner petals (6) bloom first with trim animation. Stamens extend outward. |
| 2.5-4s | Full Bloom | Middle petals (8) and outer petals (12) bloom in sequence. Halo rings expand. |
| 4-6s | Radiance | Golden particles rise. All petals gently rotate. "LOTUS BLOOM" title reveals. |

## Visual Style

- **Deep purple-black** background (`#0a0612`) with radial center glow
- **Three petal rings**: outer (12 petals, deep gold), middle (8 petals, bright gold), inner (6 petals, light gold)
- **Sacred geometry mandala**: 4 concentric dashed circles, 36 radial rays, 24 dots, 12 rotating lotus marks
- **Golden center** with 16 stamen lines tipped with glowing dots
- **Rising gold particles** with procedural jitter and upward drift
- **Expanding halo rings** in gold and amber
- **Vignette** for focused center composition

## Petal Animation

Each petal ring uses `Path` with `trimStart` and `trimEnd` curves:
- Petals start at `trimEnd=0` (invisible) and animate to `trimEnd=1` (fully drawn)
- Rings bloom in sequence: inner (0.8s) → middle (0.5s) → outer (0.3s)
- Subtle rotation on each ring creates organic movement

## Post-Processing

- **HSLA overlay** — Warm golden hue shift (40 to 30), subtle saturation boost
- **Glow bloom** — Threshold 0.38, intensity animated 0.6 to 1.6 to 1.0

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000009/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000009/main.motionloom
```
