# S81 — Night Owl / Rain-night convenience store

Narrative pass: the S79 penguin waits for its frog friend, leads it into shelter,
answers a happy hop with a small bow, and watches the rain together.
The established architecture and toon style are retained. There is no Character1.

The current revision follows the user's September 3 corner-store reference:
dark tiled upper storeys, inset windows, a warm wraparound lightbox with orange
and green bands, poster-covered glazing, a blue vending machine, recycling bins,
delivery crates, a parked bicycle, utility poles and overhead cables. The opening
camera is closer to street height. The reference image itself is not redistributed.

## Shot layout

| Time | Camera study |
| --- | --- |
| 0–5 s | Exterior push; penguin waits while frog hops closer |
| 5–13 s | Penguin waddles and frog hops through the open entrance |
| 13–19 s | Two-shot from the doorway; greeting hop and answering bow |
| 19–24 s | Both turn toward the rainy window; restrained depth of field |
| 24–30 s | Exterior pull-back looking into the store |

The 30-second graph is authored at 30 FPS and 1280 × 720.

## Scene contents

- Four-sided convenience-store shell, glazing and open central doorway.
- Wraparound cream lightbox, orange/green stripes and metal canopy seams.
- Tiled upper-storey facade, windows, rear service door, grille and crates.
- Refrigerated back-wall cases and two stocked wall aisles; central stand removed for clearance.
- Checkout counter, register, coffee unit, tiled floor and modular ceiling.
- Forecourt bench, bin, bollards, parking markings and exterior rain volumes.
- Two compact parked cars, additional marked bays, wheel stops, a pedestrian
  crossing, cones and a parking sign, with the central entrance kept clear.
- Four planted islands and six low-detail background buildings with window
  strips, rooftop equipment and perimeter rails to give the store a neighborhood.
- Small glossy road patches; these are surface accents, not simulated puddles.

`Scene.renderStyle="s81_cinema"` uses three-step toon shading, restrained specular,
slightly boosted saturation and ACES grading,
cool exterior light and warmer interior lamps. This is a procedural look study,
not a photorealistic finished commercial or a ray-traced reflection demo.

## Assets and scope

Environment geometry is authored with PrimitiveAsset and Model nodes in this file.
Penguin and frog geometry/materials are copied from S79 with S81-specific IDs.
Their CompoundAssets use scene-authored translation, hop, sway, bow and heading
keyframes: simple whole-body animation, not an articulated skeletal walk or IK.
No GLB, humanoid profile or ActionLibrary is required for these two characters.
Three normal maps reuse the existing S73 project textures via GitHub raw URLs:
plaster, weathered concrete and brushed metal. The S72 project HDR provides
image-based material lighting with its background hidden. Browser hosts must preload these
ImageAsset URIs using the existing asset-loading path.

No previous showcase, shared action library, character asset or engine source
is changed by this scene.

## Validation status

The animal revision parses and analyzes without warnings. Representative native
WGPU frames are rendered for the entrance, greeting and window shots.
The five-shot edit replaces the old 360-degree study and avoids reverse-facing
interior camera quadrants. The previously observed near-plane renderer problem
is not fixed by this scene change. The earlier Character1 revision passed browser
WASM seek tests; that is not a new browser validation of this animal revision.
This is not a frame-by-frame collision or pixel-parity certification.
The current lighting remains stylized; photoreal wet reflections are not claimed.

Run from the anica repository:

```sh
cargo run -p motionloom --example wgpu_live_preview -- ../motionloom-example/showcase/s-000081/main.motionloom
```
