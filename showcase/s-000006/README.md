# s-000006 — Infinite Museum of Time

A 5-second cinematic animation (1920×1080, 30fps) featuring an infinite museum
corridor filled with clocks from different eras. The camera flies forward through
the corridor as time itself unravels.

## Animation Phases

| Time | Phase | Description |
|------|-------|-------------|
| 0–1s | Elegant Entry | Slow camera movement through the corridor. Clocks tick asynchronously on the walls. Dust particles float in the museum light. |
| 1–2s | Time Reversal | All clock hands begin spinning backward. Digital numbers glitch and reverse. The atmosphere shifts. |
| 2–3.5s | Temporal Fracture | The corridor stretches into impossible perspective. Walls split into time-slice panels showing Ancient, Victorian, Modern, and Future eras. |
| 3.5–4.5s | Vortex | Hundreds of clock faces detach and orbit around the camera in a swirling vortex. Pocket watches, digital displays, holographic clocks, and sundials spin through space. |
| 4.5–5s | The Freeze | Time stops. All elements shatter into still fragments. The final frame reveals one glowing timestamp: **00:00**. |

## Visual Style

- **Surreal, high-end museum aesthetic**
- Deep shadows and dark marble tones (`#0a0505`, `#1a0f0a`, `#2d1b0e`)
- Gold accents and details (`#d4af37`, `#FFD700`)
- Museum lighting with radial glows
- Subtle dust particles floating throughout
- Cinematic perspective with receding corridor frames

## Clock Types

1. **Grandfather clock** — Classic wall clock with gold Roman numerals
2. **Roman numeral clock** — Ornate circular face on the right wall
3. **Pocket watch** — Silver suspended clock with chain, spinning backward
4. **Digital clock** — Green LED-style display with scrambling numbers
5. **Holographic clock** — Cyan neon rings with dashed orbital lines
6. **Sundial** — Ancient bronze disc with golden gnomon

## Effects

- **Recursive corridor illusion** — Receding rectangular frames create infinite depth
- **Rotating clock hands** — Each hand rotates at different speeds via `curve()` animation
- **Number scrambling** — Digital clock shows glitching time values
- **Time-slice panels** — Four era panels slide in with opacity/scale transitions
- **3D-like perspective** — Scale transforms combined with depth opacity
- **Particle dust** — 24+ floating particles with `$index`-based position expressions
- **Glass cracks** — Fragment lines burst outward during the freeze
- **Vortex motion** — 16+ orbiting clock faces with radial displacement

## Post-Processing

- **HSLA overlay** — Warm golden hue shift, subtle saturation boost
- **Bloom** — Threshold 0.40, intensity animated from 0.8 to 2.2 during the vortex
- **Gaussian blur** — Not used; bloom alone provides the atmospheric glow

## Run

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- --print-stats ../motionloom-example/showcase/s-000006/main.motionloom
```
