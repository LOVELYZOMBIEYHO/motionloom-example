# Feature: glb

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000026](../../core/scene/cs-000026/) | core | scene | Character 1 Humanoid Action | assets, glb, true-3d, skinned-model, humanoid-retarget | Load the canonical Character 1 GLB through a repository-hosted ModelAsset.<br>Map Quaternius joints to humanoid_v1 through a reusable ModelProfile. |
| [cs-000060](../../core/scene/cs-000060/) | core | scene | GLB Draco Model in a Unified Scene | scene, assets, gltf, glb, draco | Declare a Draco-compressed GLB once in the Graph Assets block.<br>Render true 3D inside a Scene CompositeGroup without using the removed World tag. |
| [s-000066](../../showcase/s-000066/) | showcase | scene | iPhone Titanium Reveal | scene, assets, glb, true-3d, material-binding | Bind a resolution-independent MotionLoom Scene to a named GLB screen material as a live texture.<br>Animate a repository-hosted phone GLB and Camera3D with typed AnimationTarget keyframes. |
| [s-000068](../../showcase/s-000068/) | showcase | scene | Quaternius Night Walk | scene, assets, glb, true-3d, skinned-model | Load one repository-hosted Quaternius GLB as both a skinned model and a raw animation clip container.<br>Wrap an embedded Walk_Loop clip in a canonical Action and let ApplyAction reference only that Action id. |
| [s-000070](../../showcase/s-000070/) | showcase | scene | Character 1 Complete Action Library | scene, assets, glb, true-3d, skinned-model | Expose all 43 clips embedded in one canonical Character 1 GLB as executable Action nodes.<br>Number the complete clip catalogue monotonically from 01 through 43 without resets or duplicates. |
| [s-000072](../../showcase/s-000072/) | showcase | scene | Cinematic Lighting / HDRI Lab | scene, assets, true-3d, glb, camera-3d | Bind a Radiance HDR equirectangular image as the visible environment and IBL source.<br>Separate background, diffuse and roughness-aware specular environment contributions. |
