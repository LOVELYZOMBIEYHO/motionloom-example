# DSL Pattern: process

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cp-000001](../../core/process/cp-000001/) | core | process | DSL Process Basic | process | Define the smallest Process graph with one pass. |
| [cp-000002](../../core/process/cp-000002/) | core | process | Process Bloom Alias | process, gpu-pipeline, bloom, glow | Use effect="bloom" as a Process post-pass alias for layer FX.<br>Feed the selected layer into Process with Input from="input:clip0". |
| [cp-000003](../../core/process/cp-000003/) | core | process | Process Glow Alias | process, gpu-pipeline, bloom, glow | Use effect="glow" as a readable alias for Process bloom in layer FX.<br>Keep one alias per Pass so examples are searchable and unambiguous. |
| [cp-000004](../../core/process/cp-000004/) | core | process | Process Glow Bloom Alias | process, gpu-pipeline, bloom, glow | Use effect="glow_bloom" as the explicit compatibility alias for bloom/glow in layer FX.<br>Keep alias examples split because one Pass has exactly one effect value. |
| [cm-000001](../../core/composition/cm-000001/) | core | composition | Scene World Process Composition Basic | scene, world, process, text, shape | Mix Scene, World, and Process graph families in one composition graph.<br>Use Scene and World outputs as Process textures, then present the final Process from the Graph root. |
