# Advanced Declarative Layout

The smallest complete grid showing explicit container size, padding, independent gaps, alignment, justification, and cell spans.

## What it demonstrates

- `padding` creates internal space without changing child coordinates.
- `rowGap` and `columnGap` control both axes independently.
- `justify="spaceBetween"` distributes free horizontal space.
- `align="center"` centers the grid in the available vertical space.
- `layoutSpan` reserves two cells for selected children.

Layout lowers to nested Groups before rendering and remains compatible with standard scene animation and GPU rendering.
