# Anime Inferno Eye

A single stylized anime eye rebuilt from MotionLoom paths. It uses an asymmetric sharp eye aperture, a dark violet-red upper lid, a clipped orange fire iris, a vertical pupil, warm lower-iris light, and layered corneal highlights.

The eye remains fixed. Only the procedural flame texture, flame band offset, and iris glow move subtly so the design stays readable while feeling alive.

## What this showcase demonstrates

- A complete anime eye assembled from editable Path, Circle, and Group nodes.
- Mask feather and expansion keeping the iris and highlights inside the eye aperture.
- Universal procedural material applied only to the iris.
- EdgeSoftness, EdgeRoughness, and ColorBleed applied as one hand-drawn edge stack.
- Independently adjustable groups for the eye, sclera, iris, pupil, highlights, and eyelid frame.

## Preview command

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000051/main.motionloom
```
