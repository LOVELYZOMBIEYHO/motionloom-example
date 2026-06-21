# s-000027 Masked Typography Text

This showcase keeps the scene deliberately simple: black background, huge `TEXT`,
and sunset-like color bands clipped through a luma matte.

- Uses primitive block letters as the `TEXT` matte.
- Uses a color precompose as the source plate.
- Avoids process passes, unsupported blend modes, animation, and external assets.

Run:

```bash
cargo run --release -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000027/main.motionloom
```
