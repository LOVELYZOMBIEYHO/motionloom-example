# Feature: layer-fx

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cp-000001](../../core/process/cp-000001/) | core | process | Process Brightness | process, brightness, layer-fx | Use brightness as a Layer FX Process pass.<br>Set brightness to 1.0 for identity, or 1.3 for a brighter image. |
| [cp-000011](../../core/process/cp-000011/) | core | process | Process Opacity Pulse | process, gpu-pipeline, opacity, alpha, layer-fx | Use effect="opacity" for whole-layer alpha control.<br>Animate opacity with curve(...) for fades, pulses, and beat-style visibility changes. |
| [cp-000012](../../core/process/cp-000012/) | core | process | Process HSLA Overlay | process, gpu-pipeline, color, hsla_overlay, tint | Use effect="hsla_overlay" for animated color wash and tinting.<br>Control hue, saturation, lightness, and alpha independently. |
| [cp-000013](../../core/process/cp-000013/) | core | process | Fixed Opacity Layer FX | process, gpu-pipeline, opacity, alpha, layer-fx | Use effect="opacity" for fixed whole-layer alpha control.<br>Use opacity in the 0.0-1.0 range; this example uses 0.3. |
| [cp-000014](../../core/process/cp-000014/) | core | process | Fixed HSLA Overlay Layer FX | process, gpu-pipeline, hsla-overlay, color-wash, layer-fx | Use effect="hsla_overlay" for a fixed color wash over a layer.<br>Control hue, saturation, lightness, and alpha with numeric process params. |
| [cp-000015](../../core/process/cp-000015/) | core | process | Paper Texture Overlay | process, gpu-pipeline, texture-overlay, paper-texture, layer-fx | Use effect="texture_overlay" for procedural paper/grain texture.<br>Use <Texture /> in <Defs> as the scene-side texture metadata surface. |
| [cp-000016](../../core/process/cp-000016/) | core | process | Process Pass Mask | process, gpu-pipeline, mask, pass-mask, luma-mask | Use mask="..." on <Pass> to limit a process effect to a mask texture.<br>Use maskMode="luma" when the mask texture is black and white. |
