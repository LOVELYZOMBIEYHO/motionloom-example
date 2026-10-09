# S98 — Realistic 3D red apple

`main.motionloom` is a 1080×1920 portrait, 60 fps, 20-second showcase.

- 0–2 seconds: textured apple.
- 2–4 seconds: gray wireframe.
- 4–6 seconds: white clay.
- 6–12 seconds: breakaway shell, airborne flip, and hero return.
- 12–14.6 seconds: the apple rocks and rolls forward; the camera approaches the peel and passes beside the fruit.
- 14.6–15.8 seconds: the camera looks ahead at the black background, with the same apple behind it and out of view.
- 15.8–18.5 seconds: the camera turns back toward the apple as it completes its roll and settles.
- 18.5–20 seconds: hold the opening camera composition for the loop.

The apple body is generated from one reusable `Revolve/Profile` definition. `RadialWave` adds five shoulder lobes, and `DisplaceNoise` adds subtle shape variation with fixed seed `98`. The stem keeps its compact authored mesh. `main.motionloom` uses the refined crown and arc-spaced profile described below, generated peel maps in `assets/peel-v2/`, the original stem image, and the HDR studio environment. Earlier images remain in `assets/` for previous variants. The visible background is pure black, with no enclosing backdrop or ground geometry.

The ending uses a single rigid apple. Rotation, travel and vertical position are sampled from its body and stem silhouette so the model follows its original ground contact trajectory. Camera and softboxes translate with the fruit, ending at the opening view relative to its new position. There are no water beads or replacement apples.

Run the current WGPU Preview with the Cinematic or Ultra host profile, or render `main.motionloom` directly from this directory. The composition does not depend on the optional evidence or review scripts.

## Studio lighting and peel realism

This revision uses existing DSL tags and the recently added renderer properties:

- `LightingStyle shadowMode="perLight"` gives each direct emitter independent visibility. Ambient fill is reduced from `0.19` to `0.025`.
- The large key softbox uses intensity `4.2`, the fill `0.65`, and the rear strip `0.8`. All three use `castShadow="true"`. The directional light is reduced to `0.25`, with `angularDiameter="6"` and full shadow strength.
- An invisible, unmodified 2K [Studio Small 03 HDRI by Greg Zaal / Poly Haven](https://polyhaven.com/a/studio_small_03), licensed CC0, replaces the LDR environment in `main.motionloom`. Environment intensity is `0.75`, diffuse `0.25`, specular `0.10`, and rotation `25` degrees. Reflection strength is intentionally restrained to preserve the red peel rather than whitening the crown. Download provenance and checksum are in `assets/environment-v2/provenance.json`.
- The peel uses base IOR `1.45` and a thin wax layer with `clearcoat="0.16" clearcoatRoughness="0.24"`. Stem emission is removed. The latest peel-map settings are described below.
- The rolling key and rim reuse the original fill's translation samples, with numeric offsets baked into their curve keys. Camera, body motion, audio, duration and output dimensions are unchanged. `main2.motionloom` remains the earlier variant; the user-created `main3.motionloom` retains the lighting-only revision.

There is no static irradiance bake on the moving apple. This revision does not add subsurface scattering. Active clearcoat is supported by the current native/WebGPU renderer but is explicitly unsupported by Weaver. Use the unchanged `main2.motionloom` for the earlier Weaver material path.

Selected native GPU stills for the lighting-only revision are in `evidence/realism-upgrade/`; the latest crown and texture comparison is in `evidence/shape-texture-upgrade/`. The reviews use the same Cinematic profile and full 1080×1920 output; each still gets a fresh renderer and eight TAA settling samples at its exact frame. `scripts/realism_review.rs` uses `motionloom::api` to reproduce these captures. No complete video was exported.

## Refined crown and generated peel projection

The crown means the shoulder and concave socket around the stem. The earlier socket had a wide, bowl-like rim. Its profile lip radius is reduced from approximately `0.484` to `0.313` before tessellation, and the brown calyx disk radius changes from `0.125` to `0.075`. The stem attachment, lower-body silhouette and profile height remain close to their earlier positions. A smooth Catmull-Rom profile and restrained shoulder lobes replace the broad dish-like rim.

The 55 profile controls are respaced along meridian distance. With the existing `UV mode="profileParameter" offset={[0.2,0]}`, this gives approximately uniform meridian texel spacing without a new UV mode or tag. The image top maps to the stem socket; the image bottom maps to the blossom end. The coarse source remains 32 angular segments and 28 meridian samples for the wireframe. Textured, gray, white and breakaway bodies use Catmull-Clark level 2 for a finer curved surface, producing 27,648 body triangles. All 24 existing UV partition ranges still cover that surface.

`assets/peel-v2/` contains three new 2:1 atlases generated with the built-in ImageGen tool: diffuse albedo, tangent-space OpenGL normal, and roughness. Their actual size is 1774×887. The red peel has short irregular pigment mottling and small lenticels, without the old full-width yellow crown band or baked studio highlight. The 2:1 proportion better matches circumference versus meridian distance, keeping belly lenticels closer to round. The roughness map is sampled through G with material factor `0.80` (median effective roughness about `0.47`), and normal scale is `0.32`.

Exact prompts, checksums, source paths and map statistics are saved beside the images. AI-generated edge continuity and companion-map registration are approximate; they are not physically measured maps. Original texture files, `main2.motionloom`, `main3.motionloom`, light settings, camera curves, animation timing and audio remain unchanged.

Camera optics are authored in the DSL and shared by WGPU Preview and Weaver.
The gray wireframe and white clay shots explicitly disable depth of field.
Textured hero/action shots use a 50 mm lens at f/8 and camera-target autofocus
with a surface focus offset. The rolling macro shot animates `focusDistance`
to the visible peel and stops down to f/16; its last focus value matches the
opening shot. FOV and camera movement retain the approved
composition. `maxBlur="24"` is the WGPU preview radius budget; Weaver traces
the physical aperture. Export without focus flags to follow these settings.

## Shared parametric geometry

The profile is sampled into a 32-segment control surface. The textured, gray and white bodies share its subdivided geometry. `Wireframe` derives the gray grid from the same coarse control surface. All 24 breakaway pieces use `Partition` to select regions of the body, then `MeshTransform` restores each original animation pivot. The white stem shell reuses the stem geometry. The crown revision preserves camera curves and model animation IDs.

Earlier variants retain their earlier profile and subdivision settings.

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
