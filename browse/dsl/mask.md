# DSL Pattern: mask

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [s-000027](../../showcase/s-000027/) | showcase | scene | Masked Typography Text 2s | scene, mask, group-mask, typography, luma-matte | Use a color precompose as source and a white TEXT precompose as luma matte.<br>Keep the scene static and primitive-only for direct GPU live preview testing. |
| [cp-000016](../../core/process/cp-000016/) | core | process | Process Pass Mask | process, gpu-pipeline, mask, pass-mask, luma-mask | Use mask="..." on <Pass> to limit a process effect to a mask texture.<br>Use maskMode="luma" when the mask texture is black and white. |
