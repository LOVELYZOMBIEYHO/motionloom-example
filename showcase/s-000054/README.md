# Profile-Driven Anime Character Rig

A six-second character-rig showcase built around an `anime_6_head` proportion profile. The same semantic rig drives editable vector artwork, an idle action, validation data, and a visible editor-style construction overlay.

## What this showcase demonstrates

- A complete semantic skeleton from root and pelvis through hands and feet.
- Face, torso, limb, and silhouette landmarks separated from artwork geometry.
- Machine-checkable measures, ratios, regions, symmetry, and joint constraints.
- Named guides and controls suitable for IK and host-editor manipulation.
- A reusable `Action` and `Pose` applied to a vector `Character`.
- A visible validation overlay that explains the six-head profile on screen.

## Preview

From the `anica` repository:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000054/main.motionloom /tmp/s-000054.png 90 cpu
```

