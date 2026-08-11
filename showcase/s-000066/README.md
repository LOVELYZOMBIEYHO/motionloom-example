# iPhone Titanium Reveal

Showcase 66 is a 12-second, 4K-ready product film built from one true-3D phone,
two MotionLoom Scenes, and an explicit GPU post-process chain.

## What it demonstrates

- a repository-hosted iPhone GLB loaded through a raw GitHub URL;
- a 430×932 MotionLoom Scene bound directly to the GLB screen material;
- animated model position, rotation, scale, and exposure through
  `AnimationTarget`;
- animated `Camera3D` position, target, and field of view;
- metallic/roughness, normal, emissive, and specular PBR rendering from the GLB;
- four product-film chapters with deterministic typography and camera motion;
- animated bloom and film grain in an explicit `Process` texture pipeline.

## Asset and attribution

The checked-in `assets/iphone.glb` is loaded from the MotionLoom example
repository's raw GitHub URL so the same script works in local, browser, WASM,
and published showcase environments.

The phone model is **Apple iPhone 15 Pro Max Black** by
[polyman](https://sketchfab.com/Polyman_3D), sourced from
[Sketchfab](https://sketchfab.com/3d-models/apple-iphone-15-pro-max-black-df17520841214c1792fb8a44c6783ee7)
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product and
company names belong to their respective owners; their inclusion identifies
the attributed 3D asset only and does not imply endorsement.

Load **Showcase 66** in the MotionLoom Graph UI to preview `main.motionloom`.
