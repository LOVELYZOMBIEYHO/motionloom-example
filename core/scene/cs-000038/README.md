# Scene Camera And Layer3D Separation

Shows the intended split between `Scene Camera` and `Layer3D`.

- `Scene Camera` lives in `<Track role="camera">` and moves the world-space view.
- `Layer3D` is a flat 2.5D layer/card inside the scene, with `z`, `rotationX`,
  `rotationY`, `rotationZ`, and `perspective`.
- Do not call `Layer3D` a 2.5D camera; it is the object/layer transform.
