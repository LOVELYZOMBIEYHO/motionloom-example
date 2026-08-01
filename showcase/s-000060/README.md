# Parametric City

One reusable tower component produces five distinct silhouettes by binding geometry and color parameters at each `Use` site.

## Highlights

- Typed `Param` declarations live beside the component artwork.
- Each `Use.params` block changes width, height, top position, body color, and accent color.
- Internal repeated windows also inherit the accent parameter.
- The parameterized instances are lowered to normal scene groups, keeping both CPU and WebGPU rendering available.

Render frame 120:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000060/main.motionloom /tmp/s-000060.png 120 cpu
```
