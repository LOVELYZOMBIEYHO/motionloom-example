# s-000028 Layer3D Neon Gallery

This showcase demonstrates Scene `Layer3D` with a static neon city background.

- Background remains fixed so depth changes are easy to compare.
- Cards use `z`, `rotationX`, `rotationY`, and `perspective`.
- All visible artwork is still normal 2D scene content; `Layer3D` projects it like a flat card in 2.5D space.

Run:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000028/main.motionloom
```
