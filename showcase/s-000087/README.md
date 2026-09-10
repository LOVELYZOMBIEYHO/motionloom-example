# S87 — The Wind Carries the Paper Away

30-second, dialogue-free MotionLoom CEL animatic featuring Character1.

- `review.html`: video, 13 rendered storyboard frames, shot seeking, and download links.
- `animatic.mp4`: 960×540 / 12 fps / 30 seconds, with a composite guide soundtrack.
- `main.motionloom`: 1280×720 / 24 fps / 30 seconds, ready to open in MotionLoom.
- `main4.motionloom`: the same scene, camera, and paper timeline, with both main characters using the user-provided Meshy Ashen Wanderer textured model.
- `animatic.motionloom`: the lightweight preview export.
- `STORYBOARD.md`: story, characters, setting, full shot list, sound direction, and polish notes.
- `storyboard.csv`, `shots.json`: edit timing, camera coordinates, and FOV.
- `guide-music.wav`, `guide-sfx.wav`, `audio-cues.csv`: separate guide audio and timing data.

This is production-ready blocking / animatic work, not a finished short at reference-image quality. Character1 has no facial features, hairstyle, cloth simulation, or expression morphs. The drawing paper uses world-space paths; hand-to-paper contact, the bend to pick it up, the first stroke, and facial performance still need refinement. `STORYBOARD.md` separates performance goals from what is currently implemented.

`main4.motionloom` uses the original `assets/Meshy_AI_Ashen_Wanderer_0906072317_texture.glb` ModelAsset for two instances named artist and reader. The source is one static mesh of about 1.95 million triangles with three 2048×2048 textures and materials, but no skeleton, skin, or animation clips. MAIN4 therefore uses whole-object position, orientation, tilt, and slight scale changes to convey the paper chase and pickup rhythm. MotionLoom keeps shared vertices, uses indexed drawing, and automatically splits large geometry into safe GPU buffer chunks; the approximately 195k-face `_runtime.glb` is retained as a portable fallback. Both characters share geometry and texture GPU resources, while background pedestrians and the extra geometry outline pass remain disabled.

## Preview

Open this directory through any static file server and browse to `review.html`; you can also open the video directly or load `main.motionloom` in MotionLoom.

## Rebuild

Run from the workspace root; Python uses only the standard library:

```sh
python3 motionloom-example/showcase/s-000087/build.py
```

Build the MotionLoom examples from inside `anica`:

```sh
cargo build -p motionloom --example authoring_report --example render_file_frame_gpu --example render_file_video
```

From the workspace root, a working GPU and FFmpeg are required:

```sh
anica/target/debug/examples/authoring_report motionloom-example/showcase/s-000087/main.motionloom
ANICA_FFMPEG=/opt/homebrew/bin/ffmpeg anica/target/debug/examples/render_file_video "$PWD/motionloom-example/showcase/s-000087/animatic.motionloom" "$PWD/motionloom-example/showcase/s-000087/animatic-silent.mp4" gpu
/opt/homebrew/bin/ffmpeg -y -i motionloom-example/showcase/s-000087/animatic-silent.mp4 -i motionloom-example/showcase/s-000087/guide-mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 160k -t 30 -movflags +faststart motionloom-example/showcase/s-000087/animatic.mp4
```

Replace the FFmpeg path on other machines. To export 24 fps at 720p, use `main.motionloom` as the render source. Representative frames for each shot are recorded in `shots.json`; regenerate one with `render_file_frame_gpu SOURCE OUTPUT FRAME 0`.

## Asset provenance

All characters originate from `../../assets/sample_assets/characters/character1/character1.glb`. The repository file `../../assets/action_libraries/landing_page/ASSET_PROVENANCE.md` records Character1 / Quaternius Universal Animation Library 1 as CC0 1.0.

`assets/character1-artist.glb` and `assets/character1-reader.glb` only change `baseColorFactor` in `materials`; BIN blocks, geometry, skeleton, and animation content remain unchanged. `build.py` can rebuild them from the original. The animation reuses Sitting_Idle_Loop, Sitting_Exit, Jog_Fwd_Loop, Idle_Loop, Walk_Loop, and PickUp_Table; the paper-holding arm pose is an additive pose created for this showcase.

The park and sketch are procedurally generated geometry in this example. Reference images were used only for creative direction and are not composited into the video background. The repository retains the generated original guide audio and does not use external music.
