# Process Brightness

ID: `cp-000001`  
Type: `core`  
Domain: `process`

## Files

- `main.motionloom`: Layer FX version using `input:clip0`.
- `main_with_scene.motionloom`: standalone Scene + Process version for direct preview/render testing.

## Features

process, brightness, layer-fx

## DSL

process, brightness

## Teaches

- Use `brightness` as a MotionLoom Process pass.
- `brightness: "1.0"` is identity; `brightness: "1.3"` brightens by +0.3.
- Use `Input from="input:clip0"` for Anica Layer FX usage.

## Use In Anica

Open Layer FX Template Picker, choose `cp-000001 Process Brightness`, then insert it into the selected Layer FX.
