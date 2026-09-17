# S94 — Image-Reference MeshAsset Head

`main.motionloom` is an eight-second, 720×900, 24 fps clay head turntable. The main head is an explicit `MeshAsset` control cage; separate cages form eyebrows, mouth line, ear shells and recessed ear bowls. PrimitiveAssets supply the eyeballs and irises. No imported model is used.

A fixed camera observes a 360-degree Y rotation. `AnimationTarget` nodes rotate the head and mesh parts; position expressions orbit the eyes and separate rotation targets orient the irises. Physical shading, rectangle area lights, a directional light and AO reveal the surface shape. MSAA High is requested with an SMAA fallback; backend diagnostics are required before claiming native MSAA.

The `authoring/` directory contains reference sets, candidates and fitting summaries. The latest feature summary records reference-panel disagreements, simplified ear anatomy and a reproducible sculpt-script workflow rather than a complete topology-proposal API trace. Those records do not certify the current complete assembly's reference fit or watertightness.

Run from the Anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000094/main.motionloom
```

`main.motionloom` is the executable source of truth; `schema.json` describes its actual tags and attributes.
