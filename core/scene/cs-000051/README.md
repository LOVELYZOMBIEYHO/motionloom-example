# Advanced Component Composition

The smallest complete example combining enum and boolean parameters, a derived value, and replaceable Component content.

## What it demonstrates

- `type="enum"` restricts an accent to a declared value set.
- `type="boolean"` lowers `true` and `false` to numeric `1` and `0`.
- `Derived` calculates reusable attribute expressions in declaration order.
- `Slot` provides default artwork and `Fill` replaces it for one `Use` instance.

Parameterized components lower to ordinary nested Groups, preserving the existing CPU and WebGPU scene render paths.
