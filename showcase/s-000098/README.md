# S98 — Realistic 3D red apple

`main.motionloom` is a 1920×1080, 24 fps, 12-second showcase. The first two seconds show a textured 3D apple; the next four seconds show the same body in gray wireframe and white clay. The final six seconds animate a breakaway shell, a spinning apple, droplets, and a return to the hero view.

The apple body and stem are UV-mapped meshes authored directly in the DSL. The five images in `assets/` supply peel color, peel normal detail, peel roughness, stem color, and an invisible soft studio environment. The environment lights the model while the visible background remains black.

Run WGPU Preview or render `main.motionloom` directly from this directory. The composition does not depend on the removed authoring or evidence files.
