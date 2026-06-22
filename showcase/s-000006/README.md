# s-000006 — Time Engine Museum

A 5-second cinematic scene (1920×1080, 30fps) built around one clear subject:
a large central **Time Engine** clock inside a dark museum hall.

## What Changed

The previous version had many small clocks and panels but no dominant focal
point. This version keeps the same time-museum idea, but organizes the frame
around a readable composition:

- **Center:** a large golden mechanical clock engine.
- **Left:** an ancient clock display case.
- **Right:** a future digital clock display case.
- **Foreground:** orbiting relic clocks, dust, and a sweeping time beam.
- **Final beat:** the scene freezes on `00:00`.

## Animation Phases

| Time | Phase | Description |
|------|-------|-------------|
| 0–1s | Museum Reveal | Title fades in and the central Time Engine scales into view. |
| 1–2s | Engine Activation | Clock hands begin moving and the side exhibits become readable. |
| 2–4.3s | Temporal Sweep | A bright time beam crosses the machine while orbiting clock relics rotate. |
| 4.3–5s | Time Freeze | The machine locks to `00:00` and the final `TIME STOPS` stamp appears. |

## Visual Style

- Dark bronze museum hall.
- Gold clock face as the main subject.
- Cyan future exhibit balanced against warm ancient clock tones.
- Warm HSLA grade and bloom pass for cinematic glow.

## Run

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- --print-stats ../motionloom-example/showcase/s-000006/main.motionloom
```
