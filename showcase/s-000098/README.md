# S98 — Realistic 3D red apple

`main.motionloom` is a 1080×1920 portrait, 24 fps, 20-second showcase.

- 0–2 seconds: textured apple.
- 2–4 seconds: gray wireframe.
- 4–6 seconds: white clay.
- 6–12 seconds: breakaway shell, airborne flip, and hero return.
- 12–14.6 seconds: the apple rocks and rolls forward; the camera approaches the peel and passes beside the fruit.
- 14.6–15.8 seconds: the camera looks ahead at the black background, with the same apple behind it and out of view.
- 15.8–18.5 seconds: the camera turns back toward the apple as it completes its roll and settles.
- 18.5–20 seconds: hold the opening camera composition for the loop.

The apple body and stem are UV-mapped meshes authored directly in the DSL. The five images in `assets/` supply peel color, peel normal detail, peel roughness, stem color, and an invisible soft studio environment. The visible background is pure black. No enclosing backdrop geometry blocks the environment or directional lights, keeping WGPU Preview and Weaver lighting close.

The ending uses a single rigid apple. Rotation, travel and vertical position are sampled from its body and stem silhouette so the model follows its original ground contact trajectory. Camera and fill light translate with the fruit, ending at the opening view relative to its new position. There are no water beads or replacement apples.

Run WGPU Preview or render `main.motionloom` directly from this directory. The composition does not depend on the removed authoring or evidence files.

Camera optics are authored in the DSL and shared by WGPU Preview and Weaver.
The gray wireframe and white clay shots explicitly disable depth of field.
Textured hero/action shots use a 50 mm lens at f/8 and camera-target autofocus
with a surface focus offset. The rolling macro shot animates `focusDistance`
to the visible peel and stops down to f/16; its last focus value matches the
opening shot. FOV, camera movement, geometry and textures retain the approved
composition. `maxBlur="24"` is the WGPU preview radius budget; Weaver traces
the physical aperture. Export without focus flags to follow these settings.
