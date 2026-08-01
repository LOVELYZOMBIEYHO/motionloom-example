# Declarative Layout

The smallest complete automatic scene layout example.

## What it demonstrates

- `Layout mode="grid"` positions six children automatically.
- `columns`, `itemWidth`, `itemHeight`, and `gap` define the layout geometry.
- The `Layout` itself accepts standard group transforms such as `x`, `y`, `scale`, and `opacity`.

The MVP supports `row`, `column`, and `grid`. Layout nodes are lowered to ordinary nested groups during parsing.
