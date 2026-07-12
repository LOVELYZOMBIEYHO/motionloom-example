# Cosmic Prism Glass Eye

A procedural pink-violet anime eye inspired by cosmic lens photography. The iris uses polar-coordinate noise, radial fibers, deterministic star particles, glass refraction, chromatic dispersion, vertical light streaks, and highlight compression.

The artwork contains no embedded reference image. Eye aperture masking keeps the optical layers inside the sclera, while the eye frame, iris, particles, rays, highlights, and cornea remain independently adjustable.

The surrounding skin uses separate low-frequency displacement and cellular pore noise. Eye-socket, under-eye, and corner color modeling are independent groups, while the eyebrow is built from a thin base plus filled tapered hair paths instead of one heavy vector block.

## Preview

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000052/main.motionloom
```
