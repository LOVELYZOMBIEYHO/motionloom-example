# S89 material assets

Created with the built-in image-generation tool for this showcase. The tool did
not expose a model selector, so these are not claimed to be IMAGE2.5 outputs.
The reference image supplied visual direction only and is not bundled.

## Map contract

- `wood-base.png`, `stone-base.png`, `bronze-base.png`: AI-generated base colour,
  requested as uniformly lit seamless surfaces. Tileability and absence of baked
  shading are goals, not guaranteed properties of generated pixels.
- `*-normal.png`: tangent-space normal approximations from periodic analytic
  height fields in `build.py`, not depth recovered from the albedo.
- `*-roughness-metallic.png`: linear glTF packed maps; G is roughness, B is one
  multiplied by the material's metallic factor (zero wood/stone, 0.7 bronze).
  R is unused. These are artistic estimates, not measured material response.

The detail GLBs embed all maps. Colour textures use the renderer's colour path;
normal and packed maps are data. Do not treat generated colour-map brightness as
physical height. Current normal detail deliberately stays shallow.

## Generation prompts

### Wood

Use case: photorealistic-natural. Asset type: seamless square PBR base-color/albedo texture for a real 3D weathered timber column in a Chinese temple. Entire image is close orthographic straight-on continuous dark warm reddish-brown hardwood surface. Fine longitudinal grain running vertically, subtle pores and scratches, old rubbed satin varnish, occasional tiny fissures, rich natural grain with restrained variation. This is an unlit scanned-material-like ALBEDO MAP, not a scene or a photo of a board. Flat diffuse uniform illumination, no cast shadows, no directional highlights, no perspective, no frames, no text, no panels or planks, no large knots, no objects. Seamlessly tileable on all edges. Wood fills every pixel. Square 1024x1024.

### Stone

Use case: photorealistic-natural. Asset type: seamless square PBR base-color/albedo texture for pale grey limestone paving in an old Chinese courtyard. Entire image is close orthographic continuous light warm-grey fine-grained limestone surface, subtle mineral inclusions, tiny weathered pits, fine pale veins and barely visible hairline cracks. Realistic tactile stone, understated colour variation, no broad high-contrast marble swirls. UNLIT SCANNED-MATERIAL-LIKE ALBEDO MAP. Uniform diffuse lighting, no directional light or shadows. No tiles, no grout, no objects, no perspective, no borders, no text. Seamlessly tileable all edges. Stone fills every pixel. Square 1024x1024.

### Bronze

Use case: photorealistic-natural. Asset type: seamless square PBR base-color/albedo texture for aged brass temple lantern fittings. Entire image is continuous muted warm golden bronze metal surface with fine micro scratches, subtle rubbed wear, tiny dark-brown oxidation speckles, extremely sparse muted green patina, no relief ornaments. UNLIT BASE COLOR MAP, not a rendered metal sphere. Even flat illumination, no baked reflections, no hotspots, no directional shadows, no objects, no border, no text, no perspective. Seamlessly tileable on all edges. Surface fills every pixel. Square 1024x1024.

The requested resolution is preserved above as provenance; actual output sizes
are those encoded in the supplied PNGs. Rebuilding technical maps does not rerun
image generation and leaves these base-colour originals unchanged.
