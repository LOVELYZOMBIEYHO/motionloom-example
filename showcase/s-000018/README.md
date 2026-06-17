# Volcanic Genesis 20s

A five-shot elemental sequence with magma chambers, eruption plumes, lava rivers, ash lightning, and a newborn-island finale.

## Five Shots

| Time | Shot | Description |
|------|------|-------------|
| 0-4s | **MAGMA HEART** | Subterranean magma core pulses below dark rock. |
| 3.5-8s | **ERUPTION** | The volcano cone opens with fire jets and smoke. |
| 7.5-12s | **LAVA RIVERS** | Glowing lava streams cut through black terrain. |
| 11.5-16s | **ASH LIGHTNING** | Ash clouds flash with branching lightning. |
| 15.5-20s | **NEW LAND** | The final island silhouette rises under orange glow. |

## Visual Style

- Five distinct timed compositions inside one MotionLoom scene.
- Smooth opacity crossfades plus brief white transition flashes.
- GPU-friendly scene primitives: gradients, paths, text, repeat fields, and numeric curves.
- Bloom process at the end for stylized glow.

## Run

```bash
cargo run -p motionloom --example render_file_frame -- \
  showcase/s-000018/main.motionloom /tmp/frame.png 0 cpu
```

GPU preview:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- \
  showcase/s-000018/main.motionloom
```
