# Anime Portrait Hair Warp and Blink Rig

A four-second portrait showcase that turns imported editable anime vector paths into a small semantic deformation rig. Hair movement, left-eye blinking, right-eye blinking, transparent cutouts, and hand-drawn facial details remain native MotionLoom DSL.

## What this showcase demonstrates

- `HAIR_GROUP`, `LEFT_EYE_GROUP`, and `RIGHT_EYE_GROUP` as editable semantic artwork regions.
- Root and tip pins that sway selected hair while keeping the scalp stable.
- Explicit `MeshTopology`, `Vertex`, and `Triangle` data for two eye deformation meshes.
- Coordinated top and bottom eyelid pins that close each eye onto a controlled line.
- Skin backfills and final eyelid overlays for a clean full blink.
- A `Precompose` inverse alpha matte that reveals the live graph background through source-art cutouts.
- Additional nose and mouth strokes kept in their own drawing-tools layer.

## Preview

From the `anica` repository:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000055/main.motionloom /tmp/s-000055.png 30 cpu
```

Frame `30` is the first blink at one second and is useful for checking both eyelids and the deformation meshes.

