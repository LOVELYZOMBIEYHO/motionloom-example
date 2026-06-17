# Process Tone Map

ID: `cp-000009`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, color, tone_map, grading

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, tone_map

## Teaches

- Use `effect="tone_map"` for exposure, contrast, shoulder, gamma, and saturation.
- Use tone mapping after glow/bloom to control highlights.
- Use `main_with_scene.motionloom` as a blown-highlight test chart for checking highlight rolloff.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
