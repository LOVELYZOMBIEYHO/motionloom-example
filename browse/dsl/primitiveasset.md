# DSL Pattern: primitiveasset

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [s-000072](../../showcase/s-000072/) | showcase | scene | Cinematic Lighting / HDRI Lab | scene, assets, true-3d, glb, camera-3d | Bind a Radiance HDR equirectangular image as the visible environment and IBL source.<br>Separate background, diffuse and roughness-aware specular environment contributions. |
| [s-000073](../../showcase/s-000073/) | showcase | scene | Primitive Stair Pavilion | scene, assets, true-3d, skinned-model, humanoid-action | Build a complete architectural staircase from reusable typed PrimitiveAsset geometry and first-class PBR MaterialAsset resources.<br>Reuse one beveled visual box and its unchanged simple collider across eleven deterministic stone-textured steps. |
| [s-000074](../../showcase/s-000074/) | showcase | scene | Rain-Night Metro Ascent | scene, assets, true-3d, skinned-model, humanoid-action | Turn one reusable collider-owning primitive stair assembly into a cinematic rainy metro exit without introducing scene-specific DSL tags.<br>Share existing wet concrete, plaster, weathered concrete and brushed-metal PBR textures across station architecture and street dressing. |
| [csim-000013](../../core/simulation/csim-000013-rigid-body-3d/) | core | simulation | Rigid Body 3D Contract | rigid-body | Declare typed primitive geometry and derive static or dynamic 3D colliders with shape=auto. |
| [s-000071](../../showcase/s-000071/) | showcase | simulation | Rigid Body Drop Lab | scene, true-3d, scene-physics, scene-gravity, rigid-body | Use one RigidBody tag with an explicit 3D dimension and body type.<br>Build an arena from static colliders and an authored kinematic collider. |
