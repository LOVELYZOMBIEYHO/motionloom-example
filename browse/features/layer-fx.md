# Feature: layer-fx

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cp-000001](../../core/process/cp-000001/) | core | process | Process Brightness | process, brightness, layer-fx | Use brightness as a Layer FX Process pass.<br>Set brightness to 1.0 for identity, or 1.3 for a brighter image. |
| [cp-000011](../../core/process/cp-000011/) | core | process | Process Opacity | process, gpu-pipeline, opacity, alpha, layer-fx | Use effect="opacity" for whole-layer alpha control.<br>Use a fixed opacity value for static transparency or partial layer reveal. |
| [cp-000012](../../core/process/cp-000012/) | core | process | Process HSLA Overlay | process, gpu-pipeline, color, hsla_overlay, tint | Use effect="hsla_overlay" for a fixed color wash and tinting.<br>Control hue, saturation, lightness, and alpha independently. |
| [cp-000015](../../core/process/cp-000015/) | core | process | Paper Texture Overlay | process, gpu-pipeline, texture-overlay, paper-texture, layer-fx | Use effect="texture_overlay" for procedural paper/grain texture.<br>Use <Texture /> in <Defs> as the scene-side texture metadata surface. |
| [cpt-000002](../../core/process_with_time/cpt-000002/) | core | process_with_time | Process With Time Opacity Pulse | process, gpu-pipeline, opacity, alpha, layer-fx | Use effect="opacity" with curve(...) for fades, pulses, and beat-style visibility changes.<br>Keep timed process examples separate from static core process examples. |
| [cpt-000003](../../core/process_with_time/cpt-000003/) | core | process_with_time | Process With Time HSLA Overlay | process, gpu-pipeline, color, hsla_overlay, tint | Use effect="hsla_overlay" with curve(...) for animated color wash and tinting.<br>Keep timed process examples separate from static core process examples. |
