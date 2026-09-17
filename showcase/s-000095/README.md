# S95 — Below the Surface: Native Shark Film

The current `main.motionloom` is a 25-second, 1200×800, 24 fps underwater film. The shark uses explicit MeshAsset cages and PrimitiveAsset details; the main document contains no ModelAsset or imported GLB. `main2.motionloom` is an alternative and does not supply schema.json.

Head, jaw, body, fins, gills, gum and teeth are separately authored meshes, with Catmull–Clark subdivision on selected cages. Materials reference images under `texture/`, including reference imagery and a normal map. Model transform curves animate the assembly rather than a skeletal swim clip. Separate parts do not imply a single welded manifold mesh.

Opening titles and underwater sea-life graphics lead into the shark motion and jaw beat, a black cut around 20.66 seconds, then an end card. The camera animates its target and roll, with depth of field focused on `@shark_head_model`. Environment, spot and directional lights, atmosphere fog, filmic shading, TAA and overlays establish the look. An AudioClip schedules `audio/below-the-surface.wav` for 25 seconds.

Keep local texture and audio resources beside the document. Earlier GLB-swap instructions, removed authoring scripts and deleted preview documents do not describe this revision. No current reference-fit convergence, unified topology certification or performance benchmark is claimed.

From the Anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000095/main.motionloom
```

`main.motionloom` is the executable source of truth. `schema.json` is generated from it. Authoring/schema analysis checks DSL structure, not visual quality, resource availability or performance.
