# S72 — Cinematic Lighting / HDRI Lab

This eight-second WebGPU showcase demonstrates MotionLoom's complete public
Scene 3D lighting stack. A Radiance HDR equirectangular environment supplies a
visible background, diffuse image-based lighting and roughness-aware specular
reflections. A shadow-casting directional key, warm point practical, cool spot
rim and rectangular softbox add controllable cinematic shaping.

The same 3D island also enables ambient occlusion, contact shadow controls and
ACES color management. `AnimationTarget` rotates the HDRI and animates direct
light intensity and exposure without introducing a second animation grammar.

## What this example teaches

- Load `.hdr` or `.exr` through `ImageAsset` and bind it with `EnvironmentLight`.
- Control IBL background, diffuse and specular contributions independently.
- Combine directional, point, spot and rectangular area lights.
- Enable the primary directional shadow map with `castShadow`.
- Add AO and contact darkening without baking it into model textures.
- Finish HDR shading with exposure, white balance, contrast and ACES.
- Animate registered lighting properties through `AnimationTarget`.

The HDR environment is generated from the included source SVG in linear color
space with values above `1.0`; converting an integer SVG raster directly to
Radiance without color-space conversion can produce an almost-black IBL map.
The executable DSL loads both the HDR environment and Character 1 from this
repository's GitHub Raw URLs so the example remains usable outside a local
checkout.
