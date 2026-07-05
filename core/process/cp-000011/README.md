# Process Opacity

ID: `cp-000011`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, opacity, alpha, layer-fx

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, opacity

## Teaches

- Use `effect="opacity"` for whole-layer alpha control.
- Use a fixed `opacity` value for partial layer reveal.
- In Anica Layer FX, this is useful for static transparency or previewing alpha composition.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
