# Process Gaussian 5-Tap Blur

ID: `cp-000007`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, blur, gaussian_5tap_blur

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, gaussian_5tap_blur

## Teaches

- Use `effect="gaussian_5tap_blur"` for a full 5-tap Gaussian blur (horizontal + vertical).
- Control blur strength with `sigma`.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
