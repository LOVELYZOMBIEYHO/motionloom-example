# Group Mask Feather And Expansion

This example compares three Group masks using the same circular matte.

- `maskExpansion="-28"` contracts the visible region.
- `maskExpansion="0"` keeps the original matte boundary.
- `maskExpansion="28"` expands the visible region.
- `maskFeather="18"` softens the boundary after expansion is applied.

Both properties accept MotionLoom numeric expressions and curves.
