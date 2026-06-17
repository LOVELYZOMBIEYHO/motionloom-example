# Process Bloom Alias

ID: `cp-000002`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, bloom, glow

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, bloom

## Teaches

- Use `effect="bloom"` as a Process post-pass alias.
- Apply bloom to an incoming layer FX source with `Input from="input:clip0"`.
- Control bloom with `threshold`, `intensity`, and `sigma`.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
