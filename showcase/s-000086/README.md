# S86 — Reference-led anime head

`main.motionloom` is the authoritative 20-second clay head and Hair Card orbit.
The accepted head silhouette is expressed as a compact
`HeadAsset topology="facialCage"`. `HeadProfile`, `HeadDome`, and `FaceLayout`
hold the editable design; `FacialCage generatorVersion="1"` expands them in the
MotionLoom Rust runtime into one welded head, orbital, eyelid, mouth, and nose
control cage.

The generated baseline is intentionally pinned:

- 25,024 control vertices
- 25,336 control faces
- 22,596 pinned vertices
- Catmull–Clark subdivision level 1
- zero open and non-manifold edges

The eight `HairAsset` groups remain separate editable geometry. The camera is
fixed for the first two seconds, orbits at a constant sampled radius until 18
seconds, and holds again. No GLB is needed at playback.

## Open, inspect, and export

From the sibling `anica` checkout:

```sh
cargo run -p motionloom --example render_file_frame_gpu -- \
  ../motionloom-example/showcase/s-000086/main.motionloom /tmp/s86.png 0 0

cargo run -p motionloom --example inspect_control_cage -- \
  ../motionloom-example/showcase/s-000086/main.motionloom s86_head /tmp/s86-head

cargo run -p motionloom --example check_scene_uvs -- \
  ../motionloom-example/showcase/s-000086/main.motionloom /tmp/s86-uv S86AnimeHead 0 512

cargo run -p motionloom --example export_scene_glb -- \
  ../motionloom-example/showcase/s-000086/main.motionloom /tmp/s86.glb S86AnimeHead 0
```

`inspect_control_cage` exports the generated control cage and actual runtime
surface as OBJ and prints machine-readable topology measurements. Scene GLB
export ignores cameras, lights, background, RenderStyle, and screen effects in
its working snapshot; they remain in the source DSL.

## Two levels of geometry authoring

The compact head is preferred while its semantic parameters can represent the
design. For geometry that cannot be described semantically, use either:

```xml
<HeadAsset id="custom_head" material="skin" archetype="humanoid" topology="explicit">
  <HeadShape size={[1,1,1]} />
  <HeadCage subdivision="1">
    <Vertex position={[0,0,0]} uv={[0.5,0.5]} pinned="true" />
    <Face indices={[0,1,2,3]} />
  </HeadCage>
</HeadAsset>
```

or the generic `MeshAsset` with the same `Vertex` and `Face` children. Both
compile to `ControlCageNode`. The generic form can
represent heads, clothing, body parts, or arbitrary custom surfaces without
adding body-specific semantics prematurely.

The former eye-specific cage tags were removed. `main.motionloom` demonstrates
the maintained compact head representation. The archived explicit-cage Python
generators have been removed; the authored DSL is now the source of truth.

## Reference and review limits

The clean front, left, and back turnaround constrains the head fit. Hair obscures
parts of the cranium, and no calibrated three-quarter reference exists, so the
three-quarter view is a held-out visual check rather than proof of exact likeness.
The current model has no facial rig, automatic retopology, blink, lip sync, hair
dynamics, or production-ready texture atlas. UV diagnostics and GLB files are
derived inspection outputs; changing them does not change the DSL model.
