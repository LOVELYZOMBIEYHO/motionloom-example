# S81 — NEXT IN LINE

A 60-second English-language horror promo set in the existing Night Owl convenience store. The penguin and frog discover a receipt that predicts their next actions, try to escape, and become the store's newest merchandise.

Open `preview.mp4` for the rendered edit and `main.motionloom` for the complete editable scene. 1280 × 720, 24 fps, 1,440 frames. The export includes a cut and automated horror score.

## Story and shot timing

| Time | Beat |
| --- | --- |
| 0–5.5 s | Warm storefront advertising, coffee insert, then a lit empty bay marked “RESERVED / ARRIVAL 00:48”; two silhouettes flicker inside. |
| 5.5–9 s | Checkout two-shot; a paper prop advances from the printer. |
| 9–14 s | Vector receipt insert predicts “00:17 / CAN DROPS”. |
| 14–19 s | Visible store clock; the red can falls at 17 seconds. |
| 19–23 s | First event confirmed; receipt predicts “00:26 / LIGHTS OUT”. |
| 23–29 s | Ceiling shot, blackout at 26 seconds, screen-lit aftermath. |
| 29–33 s | Receipt predicts “00:48 / CUSTOMER EXITS”. |
| 33–41 s | Characters run toward the entrance; exterior cut then reappearance inside the shop. |
| 41–45 s | “CUSTOMER EXITS” is crossed out and replaced by “CUSTOMERS STOCKED”. |
| 45–48 s | Countdown and retreat. |
| 48–53 s | Both characters become miniature, motionless shelf merchandise: “NIGHT SHIFT FRIENDS”. |
| 53–58 s | Store advertisement returns, followed by NEXT IN LINE title and COMING SOON. |
| 58–60 s | Final receipt: “NEXT CUSTOMER / YOU.” |

## Assets and soundtrack

The store, surrounding street, rain, penguin and frog reuse S81's existing PrimitiveAsset/CompoundAsset geometry. New printer, paper, can and display bay are native primitives. Receipts, torn edge, barcodes, correction lines and signage are authored with Text, Rect and SVG-style Path nodes directly in the DSL.

All former external ImageAsset URLs, normal-texture references and HDR environment lighting have been removed from the main film. No outsourced visual assets, GLB imports, Python asset generator or baked image inserts are used. All on-screen copy is English. The pre-existing `main2.motionloom` alternative is not part of this film and was left unchanged.

The sole external-origin asset is Rafael Krux's **Horror Suspense**, downloaded from Wikimedia Commons and originally published through FreePD. It is dedicated to the public domain under CC0 1.0. The Ogg Vorbis source is vendored at `assets/audio/rafael-krux-horror-suspense.ogg`; full URLs, checksum and licence notes are in `assets/audio/LICENSE.md`.

The score is edited in MotionLoom as four source trims rather than a continuous needle-drop. `AudioTarget gainDb` keys build pressure into the 17-second can drop, cut to near-silence at the 26-second blackout, restart the pursuit, punctuate the 48-second transformation, and use the composition's late climax as a two-second sting under “YOU.”

Animation is hand-authored transform blocking, not skeletal acting or physical simulation. The exit loop and transformation use deliberate cuts. The paper close-ups and product label are screen-space graphic inserts rather than texture-mapped text. Rain is procedural geometry; no physically simulated reflections are claimed.

## Verification and reproduction

The source passes native-WebGPU authoring analysis with zero warnings/errors. Visual review uses native GPU frames and a temporal contact sheet. MotionLoom decodes and mixes the score, then the existing FFmpeg export path muxes AAC audio into the MP4.

From the sibling anica checkout:

```sh
cargo run -p motionloom --example authoring_report -- \
  ../motionloom-example/showcase/s-000081/main.motionloom native-webgpu

ANICA_FFMPEG=/opt/homebrew/bin/ffmpeg cargo run -p motionloom --example render_file_video -- \
  ../motionloom-example/showcase/s-000081/main.motionloom \
  ../motionloom-example/showcase/s-000081/preview.mp4 gpu
```

Choose the FFmpeg location appropriate for your machine. Use a renderer build containing the homogeneous near-plane clipping fix used for S88. This film uses MotionLoom's `AudioAsset`, `AudioClip` and `AudioTarget` syntax; no engine code was changed specifically for S81.

The standalone native `wgpu_live_preview` now plays the same prepared soundtrack
through the default audio device. It resolves the Ogg path from this showcase
directory, so run it from the sibling Anica checkout with the `.motionloom` path
shown above.
