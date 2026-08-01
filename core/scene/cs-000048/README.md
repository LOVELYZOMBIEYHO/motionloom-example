# Parametric Component

The smallest complete example of typed parameters on a reusable MotionLoom `Component`.

## What it demonstrates

- `Param` declares `number` and `color` inputs.
- `param("name")` binds a component attribute to an input.
- `Use.params` creates short, medium, and tall instances without copying the artwork.

Parameterized uses are lowered to ordinary MotionLoom scene groups during parsing, so the existing CPU and WebGPU scene renderers can draw them.
