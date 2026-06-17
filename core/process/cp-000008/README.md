# Process Glow Stack

ID: `cp-000008`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: single Process / layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, gpu-pipeline, light, glow_stack, bloom

## DSL

Graph, Background, Process, Input, Tex, Pass, Present, glow_stack

## Teaches

- Use `effect="glow_stack"` for cinematic multi-radius glow.
- Control glow threshold, intensity, radii, and tint.

## Use In Anica

For layer FX, open `main.motionloom`, copy all content, then paste it into the Anica Layer FX MotionLoom script field.
