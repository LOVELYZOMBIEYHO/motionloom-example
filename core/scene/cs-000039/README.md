# Scene Process Pass Mask

ID: `cs-000039`  
Type: `core`  
Domain: `scene`

## Files

- `main.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

scene, process, gpu-pipeline, mask, pass-mask, luma-mask

## DSL

Graph, Background, Scene, Defs, LinearGradient, RadialGradient, Timeline, Track, Sequence, Layer, Rect, Circle, Text, Process, Tex, Pass, Present, mask, maskMode

## Teaches

- Use `mask="..."` on `<Pass>` to limit a process effect to a mask texture.
- Use `maskMode="luma"` when the mask texture is black and white.
- Keep process-pass-mask examples with Scene examples when the graph depends on scene textures.
