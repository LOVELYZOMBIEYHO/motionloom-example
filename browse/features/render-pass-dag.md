# Feature: render-pass-dag

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000059](../../core/scene/cs-000059/) | core | scene | Unified Scene Composite Order and Process Effect | scene, composite-order, composite-group, effect-scope, process-effect | Order 2D passes with compositeOrder inside one Scene.<br>Create an explicit offscreen CompositeGroup without introducing a second render domain. |
| [cs-000060](../../core/scene/cs-000060/) | core | scene | GLB Draco Model in a Unified Scene | scene, assets, gltf, glb, draco | Declare a Draco-compressed GLB once in the Graph Assets block.<br>Render true 3D inside a Scene CompositeGroup without using the removed World tag. |
