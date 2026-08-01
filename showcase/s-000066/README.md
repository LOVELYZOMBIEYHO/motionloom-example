# Anica Motion 26s Product Launch Showcase

This showcase presents a 26.26-second Anica product launch authored entirely
with MotionLoom curves, native vector artwork, and GPU render passes.

## Timeline

1. **0.00–3.10s — Launch identity:** RGB energy fields introduce Anica Motion.
2. **3.10–6.48s — HTML-in-canvas:** a glass interface card enters and exits
   while the phone chapter begins underneath it at 5.58 seconds.
3. **5.58–9.62s — Device demonstration:** a local true-3D device, a reconstructed
   product interface, and a DSL-authored pointer animate together.
4. **9.66–13.50s — Prompt workflow:** the command and AI scene request appear
   in the cream desktop interface.
5. **13.50–17.02s — RGB capability cut:** layered chromatic typography and
   scan-line accents form the high-energy transition.
6. **17.02–26.26s — Portal and catalog:** the portal expands into the final
   Anica identity and call to action.

## Assets and compatibility

The device uses the checked-in `assets/iphone.glb` model and loads it from the
MotionLoom example repository's raw GitHub URL so browser and WASM previews can
resolve it after publication. The pointer, Anica identity mark, animated color
fields, shapes, and text are authored directly in MotionLoom DSL.

The phone model is **Apple iPhone 15 Pro Max Black** by
[polyman](https://sketchfab.com/Polyman_3D), sourced from
[Sketchfab](https://sketchfab.com/3d-models/apple-iphone-15-pro-max-black-df17520841214c1792fb8a44c6783ee7)
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product and
company names belong to their respective owners; their inclusion identifies
the attributed 3D asset only and does not imply endorsement.

## Architecture demonstrated

- graph-level repository-hosted Draco GLB `ModelAsset`
- one ordered Scene containing screen-space and true-3D passes
- deterministic `compositeOrder`
- a depth-enabled 3D `CompositeGroup` with `Camera3D` and `Model`
- numeric curves for every chapter transition
- Process-level bloom and film-grain effects after the complete Scene render

Load **Showcase 66** in the MotionLoom Graph UI to preview it.
