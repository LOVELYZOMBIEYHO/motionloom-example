# Winter Aurora Cathedral 20s

A 20-second five-shot MotionLoom DSL showcase of a frozen Gothic cathedral under
the northern lights. Each shot is a completely different visual scene with smooth
opacity crossfades and white-flash transitions between them.

## Five Shots

| Time | Shot | Description |
|------|------|-------------|
| 0-4s | **MIDNIGHT** | Starry night sky with 12 bright stars, glowing moon, first snowflakes. Constellation draws itself via path trim. Text: "62°N LATITUDE". |
| 3.5-8s | **THE AURORA** | Three aurora curtains (green, teal, violet) flowing across the sky. 24 radial light rays. Floating particles. Text: "KP INDEX 7.2". |
| 7.5-12s | **STAINED LIGHT** | Close-up of a Gothic rose window with 4 stained glass color layers, 12 spokes, 12 dot details. Two side windows with pointed arches. Light shafts. Text: "ROSE WINDOW 12C." |
| 11.5-16s | **FROZEN** | Heavy snowfall (60 flakes + 20 large). 16 ice crystal paths draw themselves via trim. Frost breath particles rising. Snow ground accumulating. Text: "-32°C WIND CHILL". |
| 15.5-20s | **CATHEDRAL FINALE** | Full Gothic cathedral silhouette with rose window and side windows glowing. Aurora curtains behind. Burst glow. "WINTER AURORA CATHEDRAL" title reveal. |

## Visual Style

- **Five completely different compositions** — each shot has unique elements, layout, and color focus
- **Shot transitions**: opacity crossfade + brief white flash at 4s, 8s, 12s, 16s
- **Night palette**: deep blue-black, aurora green/teal/violet, stained glass warm/cool/violet, ice white-blue
- **Rose window**: 4-layer stained glass (warm, cool, violet, warm center) with 12 spokes and dot details
- **Gothic cathedral**: pointed-arch stone silhouette with rose window + 2 side windows
- **Constellation**: path-trimmed connecting lines with star vertices
- **Ice crystals**: path-based diamond shapes with trim draw-on animation
- **80 snowflakes** with sinusoidal horizontal drift
- **HUD text**: scene-specific readout + title on each shot
- **Bloom process** — threshold 0.12, intensity 2.05, sigma 18.0

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000015/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000015/main.motionloom
```
