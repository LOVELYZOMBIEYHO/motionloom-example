# S98 — Realistic 3D red apple

`main.motionloom` is a 1080×1920 portrait, 24 fps, 20-second showcase.

- 0–2 seconds: textured apple.
- 2–4 seconds: gray wireframe.
- 4–6 seconds: white clay.
- 6–12 seconds: breakaway shell, airborne flip, and hero return.
- 12–14.6 seconds: the apple rocks and rolls forward; the camera approaches the peel and passes beside the fruit.
- 14.6–15.8 seconds: the camera looks ahead at the black background, with the same apple behind it and out of view.
- 15.8–18.5 seconds: the camera turns back toward the apple as it completes its roll and settles.
- 18.5–20 seconds: hold the opening camera composition for the loop.

The apple body is generated from one reusable `Revolve/Profile` definition. `RadialWave` adds five shoulder lobes, and `DisplaceNoise` adds subtle shape variation with fixed seed `98`. The stem keeps its compact authored mesh. `UV mode="profileParameter"` retains the peel rows and angular offset when profile widths are edited. The five images in `assets/` supply peel color, peel normal detail, peel roughness, stem color, and an invisible soft studio environment. The visible background is pure black. No enclosing backdrop geometry blocks the environment or directional lights, keeping WGPU Preview and Weaver lighting close.

The ending uses a single rigid apple. Rotation, travel and vertical position are sampled from its body and stem silhouette so the model follows its original ground contact trajectory. Camera and fill light translate with the fruit, ending at the opening view relative to its new position. There are no water beads or replacement apples.

Run WGPU Preview or render `main.motionloom` directly from this directory. The composition does not depend on the removed authoring or evidence files.

Camera optics are authored in the DSL and shared by WGPU Preview and Weaver.
The gray wireframe and white clay shots explicitly disable depth of field.
Textured hero/action shots use a 50 mm lens at f/8 and camera-target autofocus
with a surface focus offset. The rolling macro shot animates `focusDistance`
to the visible peel and stops down to f/16; its last focus value matches the
opening shot. FOV, camera movement, geometry and textures retain the approved
composition. `maxBlur="24"` is the WGPU preview radius budget; Weaver traces
the physical aperture. Export without focus flags to follow these settings.

## Shared parametric geometry

The profile is sampled into a 32-segment control surface. The textured, gray and white bodies share its subdivided geometry. `Wireframe` derives the gray grid from the same control surface. All 24 breakaway pieces use `Partition` to select regions of the body, then `MeshTransform` restores each original animation pivot. The white stem shell reuses the stem geometry. Materials, lights, camera curves and animation IDs are unchanged.

`main.motionloom` and `main2.motionloom` use this same geometry pipeline.

## Original audio for the 20-second Short

The two `AudioClip` tracks in both scripts pair a quiet, 120 BPM electronic
score with separate synchronized foley. The score follows the material-study
cuts; the foley marks the wireframe at 2s, clay at 4s, shell release at 6s,
camera sweep and rolling motion after 12s, and final settle around 18.2s.
Both tracks fade at the loop seam. The audio is stereo, 48 kHz Ogg Vorbis and
is included when MotionLoom exports the composition with audio enabled.
`assets/audio/s98-preview-mix.ogg` is a standalone listening copy at the same
relative levels as the two DSL clips; it is not loaded by the scene.

`assets/audio/generate.py` is the complete source for both audio files. It
synthesizes every tone and sound effect from mathematical oscillators and
seeded noise; no third-party recording, sample, song, or sound library is used.
The included tracks may be used with this S98 video on YouTube Shorts without
third-party music attribution or licensing. This provenance avoids relying on
an online track labeled “no copyright”; YouTube can still make a mistaken
Content ID match, so check the upload in Studio before publishing.

To regenerate the files, run `python3 assets/audio/generate.py` using a Python
environment with NumPy and FFmpeg with `libvorbis` available on `PATH`.
