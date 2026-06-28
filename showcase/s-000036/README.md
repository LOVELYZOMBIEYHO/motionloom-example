# Standing Character Vector

A standing character built from MotionLoom scene primitives. The example keeps
each major body part in a named group, then animates the right arm with simple
FK-style parent-child rotations.

## What it demonstrates

- `Character` as a container for full-body vector artwork.
- `Group` nodes for legs, arms, torso, neck, head, hair, and face details.
- `Path`, `Rect`, and `Ellipse` primitives for a complete stylized character.
- A waving right arm driven by shoulder, forearm, and hand rotation curves.
- MotionLoom-compatible `Ellipse x/y rx/ry` syntax converted from SVG-style
  `cx/cy rx/ry` input.
