# Solar Eclipse Corona 7s

A dramatic MotionLoom DSL showcase of a total solar eclipse. The moon passes in
front of the sun, revealing the blazing corona, solar flares, and the diamond ring
effect. Stars appear during totality, and a lens flare completes the cinematic look.

## Animation Timing

| Time | Phase | Description |
|------|-------|-------------|
| 0-2.5s | Partial Phase | The sun shines brightly with surface granulation and sunspots. The moon enters from the left. Lens flare and HUD visible. |
| 2.5-3s | Diamond Ring (ingress) | A brilliant diamond ring flash appears at the moon's edge just before totality. Stars begin to appear. |
| 3-5s | Totality | The moon covers the sun completely. Corona rays, solar flares, and prominence arcs blaze outward. "TOTALITY" title reveals. Gaussian blur softens the corona. |
| 5-5.3s | Diamond Ring (egress) | A second diamond ring flash marks the end of totality. Stars fade. Corona disappears. |
| 5.3-7s | Exit | The moon exits to the right. The sun re-emerges with full brightness. Lens flare returns. |

## Visual Style

- **Deep night sky** gradient from `#020108` to `#080630`
- **Sun**: Radial gradient surface with granulation spots and darker sunspots
- **Moon**: Solid black disc with subtle surface texture craters, soft shadow edge
- **Corona**: 48 radial rays + 24 stream particles + inner/outer glow gradients
- **Solar flares**: 12 path-based flame arcs + 8 prominence loops + 16 streak lines
- **Diamond ring**: Bright point of light with horizontal streak, appears at 2.9s and 5.1s
- **Stars**: 60 twinkling field stars + 10 bright stars, visible only during totality
- **Lens flare**: Cross-shaped streak with offset flare circles
- **HUD**: Monospace text readout in top-left corner

## Post-Processing

- **HSLA overlay** — Hue shifts to warm orange before/after totality, cools during totality. Saturation drops and lightness dims during the dark phase.
- **Glow bloom** — Intensity ramps from 0.8 to 2.6 during totality for maximum corona brightness
- **Gaussian 5-tap blur** — Soft blur during totality (sigma 0 to 2.5) for atmospheric corona diffusion

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000010/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000010/main.motionloom
```
