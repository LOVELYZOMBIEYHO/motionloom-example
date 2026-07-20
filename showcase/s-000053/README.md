# Monochrome Anime Bob Hair Dynamics

A six-second MotionLoom portrait that builds a graphic black-and-white bob haircut entirely from editable vector paths and dynamic curves.

The large rear silhouette and filled side locks preserve the designed manga shape. Lightweight face locks, outer tips, and flyaway strands use `SpringChain`, a shared `Wind`, and an elliptical head `Collider` for secondary movement without turning the whole hairstyle into loose physics.

## What this showcase demonstrates

- Layered rear hair, bangs, side locks, shine shapes, facial details, and collar artwork.
- Restrained transform curves on filled hair groups.
- Six spring-driven curves with pinned roots and head collision.
- One reusable wind definition with turbulence.
- A clean separation between designed silhouette motion and strand simulation.

## Preview

From the `anica` repository:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/showcase/s-000053/main.motionloom /tmp/s-000053.png 90 cpu
```

