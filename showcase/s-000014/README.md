# Deep Sea Bioluminescence 20s

A 20-second five-shot MotionLoom DSL showcase of a journey from the ocean surface
into the glowing abyss. Each shot is a completely different visual scene with
smooth opacity crossfades and white-flash transitions between them.

## Five Shots

| Time | Shot | Description |
|------|------|-------------|
| 0-4s | **THE SURFACE** | Bright ocean surface with caustic light glow, 7 light rays, first jellyfish drifting, bubbles rising. Depth readout: 0M. |
| 3.5-8s | **DESCENDING** | Mid-water with fading light from above. Violet + cyan jellyfish, dense plankton swirl, rising bubbles. Depth readout: 200M. |
| 7.5-12s | **TWILIGHT ZONE** | Giant jellyfish close-up center with tentacle details. 32-particle bioluminescent swirl orbiting. Two small jellies floating. Depth readout: 1000M. |
| 11.5-16s | **THE REEF** | Seafloor coral formations with warm orange glow. Coral branch paths. Small jellies above reef. Warm particle drift. Depth readout: 3000M. |
| 15.5-20s | **THE ABYSS** | Near-black void. Abyssal core ignites with 32 radial rays and 40 converging particles. Burst glow. "DEEP SEA BIOLUMINESCENCE" title reveal. |

## Visual Style

- **Five completely different compositions** — each shot has unique elements, layout, and color focus
- **Shot transitions**: opacity crossfade + brief white flash at 4s, 8s, 12s, 16s
- **Bioluminescent palette**: cyan, teal, violet, blue, warm coral orange
- **4 jellyfish types** with path-based tentacles and radial glow halos
- **80 plankton particles** with procedural jitter
- **Abyss core**: white-hot center with orange halo and 32 radial rays
- **HUD text**: depth readout + scene title on each shot
- **Bloom process** — threshold 0.12, intensity 2.05, sigma 18.0

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000014/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000014/main.motionloom
```
