# Process HSLA Overlay

ID: `cp-000012`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, color, hsla_overlay, tint, layer-fx

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, hsla_overlay, curve

## Teaches

- Use `effect="hsla_overlay"` for animated color wash and tinting.
- Control `hue`, `saturation`, `lightness`, and `alpha` independently.
- Use low alpha for grading and higher alpha for stylized color pulses.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
