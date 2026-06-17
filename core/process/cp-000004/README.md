# Process Glow Bloom Alias

ID: `cp-000004`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, bloom, glow

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, glow_bloom

## Teaches

- Use `effect="glow_bloom"` as the explicit compatibility alias for bloom/glow.
- Keep alias examples split because one Pass has exactly one effect value.
- Control the post-process halo with `threshold`, `intensity`, and `sigma`.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
