# DSL Pattern: background

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000036](../../core/scene/cs-000036/) | core | scene | Pinwheel Layer zDepth Logo | zdepth, layer, shape, curve-animation, logo-motion | zDepth uses camera-space depth: negative is closer, positive is farther.<br>Use Layer zDepth for 3D-style ordering: larger positive values are farther and draw first. |
| [cs-000037](../../core/scene/cs-000037/) | core | scene | DSL FaceJaw Basic | facejaw, path, curve-animation, shape | Use <FaceJaw> to generate a character jaw or face-outline path from simple face-shape parameters.<br>Use closed=false for an open jaw curve, or closed=true with fill for a filled face/jaw shape. |
| [cp-000002](../../core/process/cp-000002/) | core | process | Process Bloom Alias | process, gpu-pipeline, bloom, glow | Use effect="bloom" as a Process post-pass alias for layer FX.<br>Feed the selected layer into Process with Input from="input:clip0". |
| [cp-000003](../../core/process/cp-000003/) | core | process | Process Glow Alias | process, gpu-pipeline, bloom, glow | Use effect="glow" as a readable alias for Process bloom in layer FX.<br>Keep one alias per Pass so examples are searchable and unambiguous. |
| [cp-000004](../../core/process/cp-000004/) | core | process | Process Glow Bloom Alias | process, gpu-pipeline, bloom, glow | Use effect="glow_bloom" as the explicit compatibility alias for bloom/glow in layer FX.<br>Keep alias examples split because one Pass has exactly one effect value. |
| [cm-000001](../../core/composition/cm-000001/) | core | composition | Scene World Process Composition Basic | scene, world, process, text, shape | Mix Scene, World, and Process graph families in one composition graph.<br>Use Scene and World outputs as Process textures, then present the final Process from the Graph root. |
| [ct-000001](../../core/text/ct-000001/) | core | text | Text Pill Box | text, text-box, text-gap | Use Text box="pill" to create an auto-sized rounded background behind text.<br>Use fontWeight and textGap to tune bold condensed title-card typography. |
