# Procedural Elements Lab

One WebGPU showcase generates cloud, fire, lava, steam, flowing water, and two universal organic material samples without image textures or Base64 assets.

Each element has its own named Group, procedural Noise definition, animated evolution, and reusable Material. Different displacement, texture amount, roughness, and specular values turn the same universal system into five distinct surfaces.

The example uses distinct generic noise families rather than recoloring one FBM texture: domain-warped `flow` for flame and steam, `ridged` noise for lava, and layered `waves` for water. Generic Filter stacks soften fire and steam without introducing element-specific renderer nodes.

The final row demonstrates the same universal material system on a Group and directly on a Path. `organic_group_noise` / `organic_group_material` and `organic_path_noise` / `organic_path_material` are intentionally separate, so every texture, displacement, roughness, specular, seed, and animation value can be tuned independently.
