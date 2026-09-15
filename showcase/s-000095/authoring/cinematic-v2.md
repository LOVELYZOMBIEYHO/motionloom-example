# Below the Surface — cinematic revision

The 25-second `main.motionloom` uses the existing shark MeshAssets and native
MotionLoom animation, PBR, TAA, camera and audio rendering.

## Timing

- 0–4 s: title over deep blue water.
- 4–7.2 s: distant right-to-left silhouette.
- 8–12.3 s: closer left-to-right pass.
- 12.3–16.8 s: empty water; the shark changes position while fully concealed.
- 16.8–20.6 s: frontal emergence, acceleration and brief jaw opening.
- 20.66 s: black; original synthesized impact and subsequent bubbles.
- 21.5–24.85 s: end title and “You were never alone.”

## Assets and implementation

`texture/mouth-reference.png` is an unchanged copy of the supplied mouth sheet.
The recessed mouth surface samples its upper-right palate panel through UVs;
it does not use a generated replacement image. A low emissive texture contribution
keeps the tissue readable under the scene's limited interior lighting. This is an
artistic lighting approximation, not physically emissive tissue.

`audio/below-the-surface.wav` is original synthesized stereo sound design:
filtered noise and oscillators for water, breathing-like pulses, a pass, impact
and bubbles. The AudioAsset/AudioClip in main exports through MotionLoom's audio
path. It is not a recorded diver or licensed film soundtrack.

The depth transition uses an animated water-coloured screen veil before the
vignette and motes. It fully conceals shot resets; it is not volumetric absorption.
The geometry remains the existing assembly, with a small native Rust-authored
textured mouth surface and jaw animation. No Blender or external model import.

## Verification and limitations

Rendered all 600 frames with the GPU/FFmpeg exporter at 1200×800, 24 fps.
Checked the side pass, empty transition including frame 374, frontal approach,
mouth and end card. The MP4 contains a 48 kHz stereo AAC soundtrack.

The mouth is a simplified recessed surface, not an anatomical reconstruction.
Teeth regularity, cheek seams and the body reference texture still limit realism.
