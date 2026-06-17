# Process Light Sweep

ID: `cp-000010`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, light, light_sweep, highlight

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, light_sweep

## Teaches

- Use `effect="light_sweep"` for an animated directional highlight.
- Control sweep position, angle, width, softness, intensity, and color.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
