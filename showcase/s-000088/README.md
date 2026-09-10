# S88 — Canyon Duel

A 30-second, 1280×720, 24 fps MotionLoom camera-blocking reference. Open `preview.mp4` for the rendered film and `main.motionloom` for the editable scene. This is previz, not final animation.

The emphasis is shot scale, foreground parallax, continuous travel and readable changes of lead. Red and blue cars follow a shared winding canyon route, covering approximately 570 metres without stopping at keyframes. Their headings follow the road tangent. The road is one continuous ribbon, with faceted canyon walls and simple car meshes.

| Time | Camera | Intent |
| --- | --- | --- |
| 0–4 s | Entry | Descend from a high rear view into the chase. |
| 4–8 s | Front | Reverse tracking facing both cars as red takes the lead. |
| 8–11 s | Left side | Parallel tracking shows vehicle profiles and the gap. |
| 11–14 s | Quarter | Blue-car rear-quarter foreground with red visible ahead. |
| 14–18 s | Overhead | Reveal the bend and re-establish geography before crossing the race axis. |
| 18–22 s | Right side | Opposite-side tracking shows blue taking the lead. |
| 22–26 s | Bumper | Low rear chase restores foreground speed and scale. |
| 26–30 s | Runout | Front three-quarter crane rises and pulls away. |

`shots.json` records the cut times. Front, rear, side and overhead views provide distinct coverage; both cars remain part of the composition. The rear-quarter insert keeps blue prominent while preserving a separate sightline to red ahead. Cuts are intentional. MotionLoom evaluates all camera and vehicle animation and renders the GLB geometry.

## Rebuild and render

`build.py` uses only Python's standard library. It generates the three local GLB assets and explicit 8 Hz linear transform keys in `main.motionloom`. Edit its route, shot functions or geometry dimensions, then run `python3 build.py`.

From the sibling `anica` checkout:

```sh
cargo run -p motionloom --example authoring_report -- \
  ../motionloom-example/showcase/s-000088/main.motionloom native-webgpu
ANICA_FFMPEG=/opt/homebrew/bin/ffmpeg cargo run -p motionloom --example render_file_video -- \
  ../motionloom-example/showcase/s-000088/main.motionloom \
  ../motionloom-example/showcase/s-000088/preview.mp4 gpu
```

Use an FFmpeg path appropriate to your machine. The native GPU renderer requires a graphics adapter. This scene requires the accompanying homogeneous near-plane clipping fix in `anica/crates/motionloom/src/world/render.rs`; older builds can incorrectly project terrain behind the camera over the foreground. Rebuild the renderer/application before viewing the source live.

## Scope and verification

The models intentionally remain blockouts. Wheel spin, suspension, physical tyre dynamics, dust, audio, motion blur and final materials are not authored. The camera plan is a cinematic reference, not final AAA animation quality.

The delivered video is rendered through MotionLoom's native GPU path and FFmpeg. Authoring analysis reports no errors or warnings. Temporal contact-sheet review covers the full sequence; shader validation covers the world projection and depth-of-field shader, whose depth reconstruction was updated alongside the projection.
