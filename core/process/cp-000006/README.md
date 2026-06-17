# Process Gaussian 5-Tap Vertical

ID: `cp-000006`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, blur, gaussian_5tap_v

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, gaussian_5tap_v

## Teaches

- Use `effect="gaussian_5tap_v"` for a vertical 5-tap Gaussian blur pass.
- Control blur strength with `sigma`.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
