# Process With Time Light Sweep

ID: `cpt-000001`  
Type: `core`  
Domain: `process_with_time`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, light, light_sweep, highlight, curve-animation

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, light_sweep, curve

## Teaches

- Use `effect="light_sweep"` with `curve(...)` to animate sweep position.
- Keep timed process examples separate from static core process examples.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
