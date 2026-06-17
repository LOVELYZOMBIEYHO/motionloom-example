## MotionLoom Example Authoring Rules

These rules apply to all MotionLoom example scripts in this directory.

## DSL Syntax Rules

- Keep examples parseable by the current MotionLoom parser. Do not invent new
  syntax for visual convenience.
- `curve(...)` points must use numeric keyframe values only:
  `curve("time:value[:ease], time:value[:ease]")`.
- Do not put `random(...)`, `sin(...)`, `cos(...)`, `floor(...)`, or other
  function calls inside a `curve(...)` keyframe value.
- Use `curve(...)` for smooth deterministic numeric interpolation.
- Use standalone expressions for procedural jitter, for example:
  `x="random(-26,26,floor($time.sec*2)+17) + 28*sin($time.sec*0.8)"`.
- Do not use `$index` in scene expressions unless the parser/runtime explicitly
  supports it. Use `Repeat` attributes such as `xStep`, `yStep`, `rotationStep`,
  and `opacityStep` for per-instance variation.
- Do not animate string attributes such as `Text.value` or `Path.d` with
  `curve(...)`. Use fixed strings/paths plus opacity, transform, trim, or other
  numeric properties.
- Do not duplicate attributes on one node. For example, do not write both
  `x="600"` and `x={curve(...)}` on the same element.
- Keep `<Present ... />` as the final direct child of `<Graph>`.

## Before Submitting an Example

- Prefer validating with:
  `cargo run -p motionloom --example render_file_frame -- <script> /tmp/frame.png 0 cpu`
- If the example needs the GPU path, also test with:
  `cargo run --release -p motionloom --example wgpu_live_preview -- <script>`

