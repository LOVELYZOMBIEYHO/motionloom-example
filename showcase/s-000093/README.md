# S93 — PBR Anti-Aliasing Matrix

This is a controlled anti-aliasing comparison built from the S89 courtyard
composition. The camera, physical surface shading, geometry, lighting, fog and
output size remain unchanged while `Scene.renderStyle` changes every two
seconds. It references S89's existing detailed GLBs and sky by relative path so
the repository does not duplicate roughly 40 MB of identical assets.

The requested matrix contains five methods and four quality levels, so the
complete comparison is 20 cells and lasts 40 seconds:

| Method | Low | Medium | High | Ultra |
| --- | --- | --- | --- | --- |
| FXAA | fast | balanced | precise | precise |
| SMAA | basic | edge + blend | full 3-pass intent | full 3-pass intent |
| MSAA | 2x | 2x | 4x | 8x |
| TAA | no jitter | 2 phases | 4 phases | 8 phases |
| SSAA | 1.25x | 1.5x | 2x | 4x |

Each RenderStyle contains only `SurfaceStyle shading="physical"` and one
`AntiAliasingStyle`. `sharpness="0"` prevents post-AA sharpening from changing
the comparison. Depth of field is also disabled.

The DSL records portable rendering intent. In the current immediate renderer,
FXAA, compact spatial morphology AA and TAA have native paths. MSAA and SSAA
report and use the authored `smaa` fallback until the backend gains multisample
attachments and internal-resolution rendering. This means S93 can already test
parsing, switching, TAA phase behaviour and fallback diagnostics, but it must not
be presented as visual proof of native MSAA or SSAA yet.

FXAA Low, Medium and High/Ultra use fast, balanced and precise shader tiers.
SMAA Low, Medium and High/Ultra use basic, edge-and-blend and wider-search tiers.
High and Ultra are intentionally identical for those two methods, matching the
table. MSAA/SSAA fallback retains the requested quality tier, although it cannot
reproduce native sample-count differences yet.

Run the immediate preview from the Anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000093/main.motionloom
```
