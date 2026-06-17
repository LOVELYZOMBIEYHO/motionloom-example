# Autumn Lantern Shrine Night 7s

A serene MotionLoom DSL showcase of a Japanese shrine at night, illuminated by
glowing paper lanterns under an autumn moon. Maple leaves drift downward through
warm amber light as the torii gate stands silhouetted against the indigo sky.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0-1s | Night Falls | Indigo sky gradient appears. Moon rises. Stars twinkle. Torii gate fades in. |
| 1-3s | Lanterns Light | Paper lanterns illuminate one by one — left, right, then the central lantern. Halos expand. |
| 3-5s | Maple Fall | Red and gold maple leaves begin falling with rotation. Incense smoke rises. Lantern glow flickers. |
| 5-7s | Title Reveal | "AUTUMN" title reveals with amber light sweep. Subtitle "AND THE LANTERN NIGHT" appears. Warm vignette. |

## Visual Style

- **Deep indigo night** background (`#0a0820`) with radial navy gradient
- **Amber palette**: warm white, gold, orange, deep red-brown
- **Torii gate**: silhouette path with traditional Japanese shrine shape
- **5 paper lanterns**: elliptical bodies with radial glow halos, hanging from strings
- **Central lantern**: largest, with flickering inner glow via `sin($time.sec*4.0)`
- **Maple leaves**: 18 red + 14 gold path-based leaves with rotation and downward drift
- **Moon**: soft glowing disc with halo
- **Incense smoke**: blue-gray radial gradients rising

## Light Effects (shared with s-000002)

- **Lantern sweep** — horizontal gradient rect sweeping across the title (like `gold_sweep`)
- **Light scratch** — vertical gradient texture scratches (like `film_scratch`)
- **Warm flicker vignette** — `sin($time.sec*14.0)` pulsing amber overlay
- **Triple-layer title text** — dark shadow + warm gold body + highlight
- **Bloom process** — `effect="bloom"` threshold 0.13, intensity 2.10, sigma 18.0
- **Lantern glow halos** — radial gradient circles with screen blend
- **Atmospheric smoke** — incense cloud radial gradients

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000012/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000012/main.motionloom
```
