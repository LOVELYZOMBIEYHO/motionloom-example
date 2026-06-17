# s-000007 — Neon Collapse

A 5-second cinematic animation (1920×1080, 30fps) of a futuristic neon
cyberpunk city being consumed by a black hole. The camera hovers low over the
streets as gravity tears buildings, traffic trails, holographic panels, and
rain into a spiraling vortex of cyan, magenta, and violet light.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0–1s | Calm Before the Storm | Slow camera push-in over the rain-soaked city. Neon signs pulse, traffic trails streak, and holographic UI panels float. |
| 1–2.5s | Event Horizon | A black hole forms in the sky. An accretion disk ignites, lens distortion begins, and skyscrapers start bending toward the center. |
| 2.5–4s | Spiral Pull | Gravity intensifies. Buildings spiral inward, light trails wrap around the singularity, UI panels fragment into pixels, and the entire city compresses. |
| 4–5s | Collapse | Everything collapses into a single bright point. A white flash burns across the screen, revealing a clean black void. |

## Visual Style

- **Ultra high contrast** cyberpunk palette
- Deep space black (`#030207`) through dark violet (`#120a2a`)
- Neon cyan (`#00F0FF`), magenta (`#FF00AA`), and violet (`#9D00FF`)
- Cinematic glow, volumetric haze, and heavy vignette
- Layered parallax with 5 depth planes
- Smooth easing and deterministic particle motion

## Layers & Effects

- **Sky** — Gradient night sky with 80 distant stars
- **Far city** — 32 receding buildings with cyan window lights
- **Mid city** — 18 buildings with neon signs and window grids
- **Traffic trails** — 20 animated cyan light streaks that curve toward the center
- **Holographic UI panels** — 3 futuristic data panels that fragment into pixels
- **Near city silhouettes** — Dark foreground buildings with neon edges
- **Rain** — 60 falling streaks with screen blend
- **Black hole** — Event horizon, accretion disk, and lens glow with 180° rotation
- **Vignette & flash** — Animated vignette plus final white flash to black

## Post-Processing

- **HSLA overlay** — Animated hue shift toward cyan/violet, saturation boost,
  and lightness lift during the collapse
- **Bloom** — `glow_bloom` with animated intensity (1.0 → 2.6 → 0.0)

## Run

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000007/main.motionloom
```

Or render a single CPU frame for validation:

```bash
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000007/main.motionloom /tmp/frame.png 0 cpu
```
