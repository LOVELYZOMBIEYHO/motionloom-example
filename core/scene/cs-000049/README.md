# Seeded Repeat Variation

The smallest complete deterministic scatter example.

## What it demonstrates

- `distribution="scatter"` places repeated children inside `bounds`.
- `seed` makes the generated positions stable across renders.
- `scaleRange`, `rotationRange`, and `opacityRange` add controlled variation.

Scatter repeat currently requires a literal `count` and literal range values. It is lowered to ordinary GPU-native groups during parsing.
