# S95 — Native MotionLoom Great White Shark

This revision builds one shark assembly entirely from native `MeshAsset` and `PrimitiveAsset` geometry. It uses no Blender, bpy, bmesh, imported model, GLB, ModelAsset, or external geometry library. Standard-library Python writes explicit MotionLoom DSL; the MotionLoom APIs perform analysis, evaluation, proposal validation, topology inspection and GPU rendering.

## Open

- `main.motionloom`: 13s underwater film. A thin letterspaced title fades in
  over deep water with drifting fish schools and bioluminescent jellyfish,
  then the shark charges the camera along its Z axis; the sea life is knocked
  left and right by its bow wave, the jaw opens and the frame cuts to black
  before the end card. PBR surface with a derived skin normal map, filmic ACES
  tone mapping, `filmic_bokeh_v1` depth of field focused on the head, a
  procedural `texture/underwater-env.png` environment light for image-based
  water lighting, a surface spotlight with the shark's own shadow, and TAA.
  `main3.motionloom` keeps the static three-quarter presentation revision and
  `main4.motionloom` the first film cut.
- `preview-side.motionloom`, `preview-front.motionloom`, `preview-top.motionloom`, `preview-bottom.motionloom`: inspectable camera views.
- `preview-clay.motionloom`: untextured geometry inspection.
- `authoring/native-v2/preview.html`: before/after and six native renders.
- `authoring/native-v2/original-main.motionloom`: untouched original S95 backup.

## Geometry and appearance

Explicit body and head surfaces, independently shaped lenticular pectoral/dorsal/pelvic/anal/caudal fins, five gill lines on each side, gumlines and individual pointed teeth are MeshAssets. Eye surfaces, nostrils and the dark mouth lining are ellipsoid PrimitiveAssets. Fin seam vertices are welded, eliminating collapsed edge faces. Catmull-Clark subdivision is supplied by MotionLoom.

The supplied four-view reference is reused through native ImageAsset / MaterialAsset UVs. Head UVs project the front panel; body and fins sample the side panel. No new reference images or missing views were generated. Head/body UV seams and projected texture distortion remain visible from some angles.

## Validation and limits

Classification: `partial_multiview_fit`. Left, front, top and bottom references are available; right/rear geometry uses a bilateral symmetry assumption. The reference top/bottom tail silhouette is inconsistent with a strictly vertical tail viewed from above/below, so this model preserves a vertical shark tail.

This is a **part assembly**, not a fully welded watertight export. The head/body UV seam and mouth have open boundaries. Fin roots intentionally overlap the body. Native topology checks found no degenerate faces or self-intersections within the inspected head, body, dorsal, left pectoral and upper tail assets. This does not certify the complete assembly as a single manifold surface.

The real analyzeImageReference API was executed for all four references. The evaluateMeshAssetReference API measures a neutral aggregate of the head, body and major fins, with subdivision disabled; separate primitive details are inspected in GPU renders. The attempted applyMeshAssetProposal was rejected for degenerate seam faces and assembly self-intersections. It was not accepted or bypassed. Fin seam topology was subsequently revised and a new baseline established; overlapping assembly parts still prevent certifying a unified mesh fit.

The configured fitting quality gates are **not passed**. Old S95 scores and new scores are not directly comparable: the camera calibration and corrected semantic bindings differ. This delivery improves the authored shape and native visual presentation, and does not claim exact four-view reconstruction or successful convergence of a unified control cage.

## Reproduce

From the workspace root:

```sh
python3 motionloom-example/showcase/s-000095/authoring/native-v2/build_native.py
./anica/target/debug/examples/render_file_frame motionloom-example/showcase/s-000095/main.motionloom /tmp/s95.png 0 gpu
```

Rendering uses the native GPU profile. `reference_workflow.py` prepares the native API analysis requests and neutral evaluation scene. All new reports live under `authoring/native-v2`; the previous author's fitting history remains unchanged.
