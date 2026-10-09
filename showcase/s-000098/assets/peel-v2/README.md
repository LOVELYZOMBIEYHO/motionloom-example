# Apple peel v2

These opaque 2:1 atlases were generated with the built-in ImageGen tool for the S98 apple. They replace the old full-width yellow crown band and long stripe pattern with red peel, short pigment mottling, and irregular small lenticels. The original assets remain in the parent folder.

- `albedo.png`: diffuse color only.
- `normal.png`: OpenGL tangent-space normal map. Keep its material strength restrained.
- `roughness.png`: green-channel roughness data; the generated median is approximately 0.588.

All three selected files are 1774 by 887 RGB PNGs. Their pixels were copied from the generated outputs without postprocessing. Companion maps use the same albedo reference, but exact registration and seamlessness are not guaranteed by image generation. See `metrics.json` for quantitative edge and value checks, and `provenance.json` plus the prompt files for generation details.

Exact built-in ImageGen prompts: [albedo](albedo-prompt.txt), [normal](normal-prompt.txt), and [roughness](roughness-prompt.txt). Saved outputs: [albedo](albedo.png), [normal](normal.png), and [roughness](roughness.png).

The atlas proportion matches the approximate circumference-to-meridian ratio of the apple. It is intended to accompany a profile resampled by arc length, keeping lenticels closer to round on the surface. A texture alone cannot fix profile-index UV stretching.
