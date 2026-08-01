# Declarative Layout Gallery

An eight-second gallery of the first declarative scene layout modes: row, column, and grid.

## Highlights

- Children contain only their local artwork; the container calculates placement.
- Row and column examples demonstrate editorial data composition.
- The final grid arranges six different MotionLoom capabilities without child-level position bookkeeping.
- Layouts lower to nested Groups and can be animated by wrapping them in standard timeline Groups.

Render representative frames:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000062/main.motionloom /tmp/s-000062-row.png 30 cpu
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000062/main.motionloom /tmp/s-000062-grid.png 180 cpu
```
