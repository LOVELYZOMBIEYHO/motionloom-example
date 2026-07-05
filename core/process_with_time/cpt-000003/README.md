# Process With Time HSLA Overlay

ID: `cpt-000003`  
Type: `core`  
Domain: `process_with_time`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, color, hsla_overlay, tint, layer-fx, curve-animation

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, hsla_overlay, curve

## Teaches

- Use `effect="hsla_overlay"` with `curve(...)` for animated color wash and tinting.
- Keep timed process examples separate from static core process examples.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
