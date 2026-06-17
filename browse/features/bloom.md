# Feature: bloom

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [s-000002](../../showcase/s-000002/) | showcase | scene | Aged Magic Book Title Reveal 7s | scene, process, bloom, gradient, text | Combine a scene source with a bloom process pass.<br>Use layered gradients, paths, and typography for a fantasy title reveal. |
| [s-000005](../../showcase/s-000005/) | showcase | scene | ANICA Core Overload Reactor Explosion 10s | scene, process, bloom, glow, gradient | Create a high-energy logo reactor explosion with scene layers and post passes.<br>Chain hsla_overlay, glow_bloom, and gaussian blur in a GPU process pipeline. |
| [s-000006](../../showcase/s-000006/) | showcase | scene | Infinite Museum of Time 5s | scene, process, bloom, gradient, text | Build a cinematic time-museum scene with clocks, panels, dust, and vortex motion.<br>Use HSLA and bloom post-processing for warm atmospheric grading. |
| [s-000007](../../showcase/s-000007/) | showcase | scene | Neon Collapse 5s | scene, process, bloom, glow, gradient | Create a cyberpunk black-hole collapse with layered city planes and neon glows.<br>Use bloom and HSLA process passes for high-contrast sci-fi grading. |
| [cp-000002](../../core/process/cp-000002/) | core | process | Process Bloom Alias | process, gpu-pipeline, bloom, glow | Use effect="bloom" as a Process post-pass alias for layer FX.<br>Feed the selected layer into Process with Input from="input:clip0". |
| [cp-000003](../../core/process/cp-000003/) | core | process | Process Glow Alias | process, gpu-pipeline, bloom, glow | Use effect="glow" as a readable alias for Process bloom in layer FX.<br>Keep one alias per Pass so examples are searchable and unambiguous. |
| [cp-000004](../../core/process/cp-000004/) | core | process | Process Glow Bloom Alias | process, gpu-pipeline, bloom, glow | Use effect="glow_bloom" as the explicit compatibility alias for bloom/glow in layer FX.<br>Keep alias examples split because one Pass has exactly one effect value. |
| [cp-000008](../../core/process/cp-000008/) | core | process | Process Glow Stack | process, gpu-pipeline, light, glow_stack, bloom | Use effect="glow_stack" for cinematic multi-radius glow.<br>Control glow threshold, intensity, radii, and tint. |
