# Inferno Anime Eye with Fire Noise Iris

A single dramatic anime eye with a flame-colored iris, mangekyou-style tomoe, and bright corneal highlights. The iris internal texture comes from the same procedural fire noise used in `s-000050`.

The iris group uses a `fire_material` driven by a flowing `fire_noise` definition: the texture amount, displacement, roughness, and specular values are tuned so the orange-yellow flame surface appears to breathe and ripple inside the eye. The rest of the eye is built from standard MotionLoom primitives: masked sclera, pupil, corneal highlights, eyelids, and lashes.

## What this showcase demonstrates

- Reusing a procedural noise/material pair from a previous showcase as a live iris texture.
- Layering flame gradients, fire-noise displacement, and hand-drawn flame tongues under corneal highlights.
- Coordinating gaze shifts, slow iris rotation, and a single blink via `curve` and `morph`.
- Keeping the eye masked so iris contents stay inside the aperture during animation.

## Preview command

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000051/main.motionloom
```
