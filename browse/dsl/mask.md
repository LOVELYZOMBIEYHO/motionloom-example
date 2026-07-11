# DSL Pattern: mask

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000039](../../core/scene/cs-000039/) | core | scene | Scene Process Pass Mask | scene, process, gpu-pipeline, mask, pass-mask | Use mask="..." on <Pass> to limit a process effect to a mask texture.<br>Use maskMode="luma" when the mask texture is black and white. |
| [cs-000040](../../core/scene/cs-000040/) | core | scene | Group Mask Feather And Expansion | scene, mask, group-mask, edge-smoothing, gpu-friendly | Use maskExpansion with a positive value to grow a Group mask or a negative value to contract it.<br>Use maskFeather after expansion to soften the final alpha boundary. |
| [s-000027](../../showcase/s-000027/) | showcase | scene | Masked Typography Text 2s | scene, mask, group-mask, typography, luma-matte | Use a color precompose as source and a white TEXT precompose as luma matte.<br>Keep the scene static and primitive-only for direct GPU live preview testing. |
| [s-000048](../../showcase/s-000048/) | showcase | scene | Dual Cursed Eye Path Animation | scene, anime, eyes, eye, path | Build a dramatic dual-eye anime-style shot with only MotionLoom Path, Circle, Line, and Group primitives.<br>Mask the animated iris groups so large rotating Path details stay inside the eye shape. |
