# S90 — Leather Shoe Render-Style Reel

`main.motionloom` is a 16-second, 1280×720, 24 fps comparison on the same imported shoe and meadow. A fixed camera and lighting rig are kept while `AnimationTarget` switches the scene render style every two seconds: filmic physical, physical, stylized, toon, clay, cel, ink wash and diagnostic grey.

Local `ModelAsset` GLBs supply the shoe and meadow. The shoe uses `scaleMode="none"` and `scale="0.01"`; embedded textures provide its surface detail. `assets/meadow_daylight.exr` supplies environment lighting and background. A directional sun, AO and contact shadows establish depth. The camera declares depth of field but `maxBlur="0"` disables visible defocus. This showcase teaches style switching and imported PBR assets, not procedural DSL modeling.

Run from the Anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000090/main.motionloom
```

`schema.json` is generated from the current executable document. Schema analysis checks DSL structure; it does not establish visual equivalence or performance.
