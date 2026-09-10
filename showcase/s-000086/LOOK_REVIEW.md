# S86 cel look revision

The authored main.motionloom is the source of truth. The archived explicit-cage generator and its review script have been removed.

Skin emission was removed. Cel lighting, a white comparison background, restrained outlines, separate upper eyelids, a new eye color texture, local mouth UV correction, and ear detail placement are authored in the DSL. Neck and ear outlines are disabled to avoid geometry hull artifacts.

Native GPU verification: frame 0 (front) and frame 180 (side), 900 x 1000. See cel-preview-front-v3.png and cel-preview-side-v3.png. This verifies rendering, not real-time performance or WASM parity.

Known limits: the face atlas still has back-side UV overlap; mouth and eye outlines retain small artifacts, the ear remains an ellipsoid blockout, and the side jaw is still angular. Previous topology/UV signatures are stale after this edit.

The new character-eye-cel-v3.png was generated with the built-in image generator. Prompt: flat 5:3 anime eye texture, white sclera extending to all edges, centered violet iris, dark oval pupil, restrained cel colors, one upper-left catchlight and a pale lower crescent; no skin, lids, text, glass refraction or gray background. The original generated PNG is copied unchanged into this directory.

## Fixed-light turntable

main.motionloom now holds the camera and both directional lights fixed. All 16 model components rotate together around world Y: hold front at 0–2 seconds, turn through -360 degrees over 2–18 seconds, hold front at 18–20 seconds. RotationY keys and rotated position offsets keep ears, eyes, and eyelids attached. GPU frames 0, 120, and 180 were rendered and visually checked; neck and ear shadows change relative to the character. Evidence: turntable-front.png, turntable-quarter.png, turntable-side.png. The cel-preview images above record the previous camera orbit.
