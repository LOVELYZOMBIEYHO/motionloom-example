# DSL Pattern: opacity

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000041](../../core/scene/cs-000041/) | core | scene | Ordered Group Effect Stack | scene, group, filter, blur, opacity | Attach an ordered list of Filter ids to a Group with the effects attribute.<br>Apply Blur, ColorMatrix, and Opacity filters to the complete composited Group rather than each child. |
| [cp-000011](../../core/process/cp-000011/) | core | process | Process Opacity | process, gpu-pipeline, opacity, alpha, layer-fx | Use effect="opacity" for whole-layer alpha control.<br>Use a fixed opacity value for static transparency or partial layer reveal. |
| [cpt-000002](../../core/process_with_time/cpt-000002/) | core | process_with_time | Process With Time Opacity Pulse | process, gpu-pipeline, opacity, alpha, layer-fx | Use effect="opacity" with curve(...) for fades, pulses, and beat-style visibility changes.<br>Keep timed process examples separate from static core process examples. |
