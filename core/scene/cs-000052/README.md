# Weighted Repeat Variants

The smallest complete example of deterministic weighted artwork selection and property variation.

## What it demonstrates

- `Variants choose="weighted"` selects circles, squares, and triangles by weight.
- A fixed seed reproduces the same choices on every parse and render.
- `Vary values` changes color while `Vary range` controls scale, rotation, and opacity.

Advanced Repeat nodes lower to ordinary instance Groups, so no renderer-specific random implementation is required.
