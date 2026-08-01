# Nova City: MotionLoom Capability Showcase

A twenty-second MotionLoom DSL companion piece to the City 2050 documentary.
Four timed sections exercise the reusable building blocks of the film: a
component gallery, an era gallery, a transition lab, and a stress test with a
debug overlay.

## What this showcase demonstrates

- Component gallery: all four reusable components
  (`sensor_glyph_component`, `building_module_component`,
  `hud_corner_component`, `route_node_component`) instanced with `Use`, plus
  labeled bar, line, and radial chart groups, a sensor network, and a
  subtitle panel.
- Era gallery: five era cards in a timed sequence, each with a distinct
  palette, density, chart geometry, and texture treatment, over a route-node
  timeline rail with a moving progress node.
- Transition lab: CRT geometry glitch (seeded slices plus a
  `ChromaticAberration` filter curve), a curve-driven digital scan mask, an
  `AnimationTarget property="d"` map morph, and an energy pulse with a
  whiteout flash.
- Stress test: nested `Repeat` grids of 25 x 20 building instances (500) and
  40 x 25 sensor dots (1000), eight animated routes from a rotating `Repeat`,
  and a camera push across the field.
- Debug overlay with fixed labels (`CURRENT TIME`, `ACTIVE SECTION`,
  `CURRENT ERA`, `BUILDING INSTANCES`, `SENSOR INSTANCES`,
  `RENDER LOAD ESTIMATE`) and numeric progress geometry instead of animated
  text.

## Preview

Render representative frames from the `anica` repository:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000059/main.motionloom /tmp/s-000059.png 120 cpu
```

Frame `120` is the completed component gallery; `210` is the era gallery,
`345` is the transition lab, and `555` is the stress test at 30 fps.

For the live GPU path:

```sh
cargo run --release -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/showcase/s-000059/main.motionloom
```
