# Puppet Warp Pin Dance

An eight-second MotionLoom DSL showcase that deforms one editable character as a continuous surface. It uses target-based Puppet Warp rather than a conventional joint hierarchy or disconnected body-part transforms.

## What this showcase demonstrates

- `PuppetWarp.target="loom_puppet"` turns the complete character group into one deformable surface.
- `PuppetPin.bindTo` derives rest positions from semantic groups inside the artwork.
- Fixed hip and foot pins keep the pose grounded while animated head and hand targets create expressive motion.
- Gaussian and smooth falloffs demonstrate how radius and strength shape the deformation field.
- Colored target rings remain outside the warp, exposing the otherwise invisible animation controls.
- Artwork, anchors, curves, and overlays are all native MotionLoom DSL with no image assets.

## Preview

Render a representative frame from the `anica` repository:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000057/main.motionloom /tmp/s-000057.png 60 cpu
```

Frame `60` is the two-second pose at 30 fps.

For the live GPU path:

```sh
cargo run --release -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000057/main.motionloom
```
