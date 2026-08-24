# S73/S74 Generated Texture Provenance

The raster sources in `textures/` and `textures/pbr/` were generated expressly
for the MotionLoom example project with OpenAI's built-in image generation tool
on 2026-08-23. They replace all previously downloaded Texturelabs files and all
maps derived from those files.

The generation briefs requested the following original, unbranded assets:

- seamless pale neutral-gray granite with fine mineral grains;
- seamless mature courtyard-tree bark with vertical ridges;
- seamless lightly weathered courtyard concrete;
- seamless fine mineral exterior plaster;
- seamless satin brushed architectural metal;
- seamless restrained weathered exterior concrete;
- seamless low-contrast glass roughness variation with faint cleaning marks;
- one broad-leaf branch cluster on a genuine transparent background.

Every brief explicitly excluded text, logos, watermarks, borders and recognizable
objects. Base images were resized and re-encoded with ImageMagick. Normal,
metallic/roughness and AO maps were derived deterministically by
`tools/build-project-pbr-textures.sh` exclusively from these generated sources.
The script strips image profiles, comments and ancillary PNG metadata.

These files are project assets, not copies or edits of Texturelabs resources.
