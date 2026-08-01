# Deterministic Variation Fields

Three procedural fields demonstrate the first Repeat Variation MVP: deterministic scatter plus per-instance scale, rotation, and opacity ranges.

## Highlights

- 150 sensor instances, 90 shards, and 80 signal triangles.
- Each field owns an explicit seed and bounds rectangle.
- No `$index`, runtime data object, or nondeterministic random source is required.
- Scatter repeats lower to normal scene groups and remain compatible with the existing render path.

Render frame 120:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000061/main.motionloom /tmp/s-000061.png 120 cpu
```
