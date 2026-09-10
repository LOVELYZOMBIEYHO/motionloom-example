# S83 procedural surface verification

## Directional-flow follow-up

The Rose Copper revision enables optional `flowStrength=1`, with lower relief, thinner veins and analytic directional transport. The default remains zero, preserving the legacy field. Native export completed all 600 frames at `/tmp/s83-directional-flow.mp4`. The shared WASM package was rebuilt and Landing Page build passed. Browser checks passed for random seek, amount-zero bypass and alpha preservation. A native/browser comparison of the updated 640 × 360 flow fixture at frame 90 had max byte difference 1 and mean 0.00031033. Rust tests: 532 passed in the sandbox; the sole local-server permission failure passed when rerun with network binding allowed (533 total). Clippy with `-D warnings` passed. This is analytic flow, not physical fluid simulation. The earlier measurements below describe the original relief revision.

Validated locally on 2026-09-04. No remote deployment or Git push was performed.

## Build and regression checks

- `cargo fmt --all --check`: passed.
- `cargo clippy -p motionloom --all-targets --offline -- -D warnings`: passed.
- `cargo test -p motionloom --lib --offline`: 532 passed, zero failed.
- Native frame/video/schema examples: built successfully.
- `npm run build:motionloom-wasm`: completed; generated package refreshed. The WASM build still reports pre-existing unused DevicePoller methods and a package LICENSE-file notice.
- Landing Page `npm run build`: passed, zero errors/warnings, four existing/generated-code hints.
- `git diff --check` in Anica: passed.

## Render checks

Native Metal exported all 600 frames. ffprobe confirms H.264, 1920 × 1080, 30 fps, 20 seconds, no audio stream. Local output: `/tmp/s83-liquid-relief-1080p.mp4`.

A local browser harness loaded the rebuilt WASM package and the actual S83 DSL. It rendered frames 0, 90, 240, 345, 480, 599 and 90 again to a WebGPU canvas. The visible frame 90 was inspected. The harness registered a local Georgia font using the existing `add_font` API; without a font, this isolated harness hit the existing cosmic-text no-default-font panic. The production Landing Page already has a font-registration path. Public GitHub Pages playback was not tested or deployed.

The 640 × 360 minimal procedural-surface example was rendered at frame 90 in native Metal and browser WebGPU, then compared as 921,600 RGBA bytes:

- Maximum absolute byte difference: 1 (out of 255).
- Mean absolute byte difference: 0.00020942.
- Bytes differing by more than 2: zero.
- Browser random seek 90 → 60 → 90: identical bytes.
- `amount=0` versus an unprocessed transparent/partially opaque source: identical bytes.
- Processed versus source alpha: identical bytes, including transparent regions.

The small cross-backend rounding difference is not an exact-bit guarantee across all GPUs. The fixed-seed, absolute-time evaluator itself is deterministic and has a 30/60 fps equivalence unit test.

## Performance interpretation

In one warmed browser run, the seven S83 canvas submissions took 5.8, 4.7, 1.3, 1.0, 1.1, 1.3 and 1.2 ms of wall time. These are API submission measurements, not GPU timestamps, display FPS or a sustained benchmark. Native surface pipelines and reusable output textures are cached. The standalone WASM Process helper retains its existing per-call renderer lifetime.

## Scope and remaining limits

The DSL remains the source of truth. No `world/render.rs` change was made. The new effect is a 2D GPU surface with virtual normals: not a fluid simulation, mesh displacement, HDR upgrade or depth-buffer DOF. CPU rendering is explicitly unsupported. The showcase uses Scene-level Effects and two-Scene GPU composition. Existing Group-level effect behavior was not expanded. The previous S83 vector version is preserved as `main2.motionloom`.
