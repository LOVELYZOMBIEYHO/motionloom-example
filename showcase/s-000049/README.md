# Realistic Hazel Eye Path Study

This showcase draws a realistic close-up eye with editable MotionLoom DSL primitives rather than an image asset.

- The sclera combines a natural gradient, warm lower reflection, cast shadow, and branching veins.
- The hazel iris uses radial gradients plus individually editable Path fibres.
- Corneal depth, reflected highlights, waterline, tear duct, eyelids, eyebrow, and eyelashes are separate named groups.
- The eye contents are clipped by a reusable aperture mask so iris and highlight details remain inside the eyelids.
- Variable-width Path strokes taper veins, iris fibres, and eyelashes from root to tip.
- The corneal reflection ring uses a compound Path with `booleanOp="subtract"`.
- `offsetPath`, `normalize`, mask expansion, and mask feather keep the waterline and aperture edges controlled without raster assets.
- The aperture, sclera, and lash lines use adaptive `morph()` keyframes for a short natural blink. MotionLoom normalizes different Path command layouts and point counts before interpolation.
- Closed morph contours automatically match winding direction and start-point correspondence, preventing the eye shape from twisting or collapsing between keyframes.
- Skin/socket and iris/cornea use separate procedural Noise and Material resources. Their scale, seed, texture amount, displacement, roughness, and specular values can be tuned independently.
