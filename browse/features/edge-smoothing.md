# Feature: edge-smoothing

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000040](../../core/scene/cs-000040/) | core | scene | Group Mask Feather And Expansion | scene, mask, group-mask, edge-smoothing, gpu-friendly | Use maskExpansion with a positive value to grow a Group mask or a negative value to contract it.<br>Use maskFeather after expansion to soften the final alpha boundary. |
| [cs-000043](../../core/scene/cs-000043/) | core | scene | Edge Softness | scene, filter, edge, edge-smoothing, soft-edge | Soften only vector alpha boundaries without blurring the complete fill.<br>Protect opaque interiors with preserveInterior. |
| [s-000051](../../showcase/s-000051/) | showcase | scene | Anime Inferno Eye with Hand-Drawn Edges | scene, anime, eye, fire, procedural-texture | Build a fixed anime eye with a flame-colored procedural iris and vertical pupil.<br>Apply EdgeSoftness, EdgeRoughness, and ColorBleed as an ordered hand-drawn treatment stack. |
| [ct-000012](../../core/text/ct-000012/) | core | text | Text AA Soft Edge Blur | text, antialias, edge-smoothing, soft-edge, blur | Use renderScale auto for cleaner default text rasterization.<br>Use antialias presets and softEdge or edgeSmoothing to reduce hard pixel edges. |
