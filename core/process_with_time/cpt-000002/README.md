# Process With Time Opacity Pulse

ID: `cpt-000002`  
Type: `core`  
Domain: `process_with_time`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, opacity, alpha, layer-fx, curve-animation

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, opacity, curve

## Teaches

- Use `effect="opacity"` with `curve(...)` for fades, pulses, and beat-style visibility changes.
- Keep timed process examples separate from static core process examples.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
