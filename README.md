# MotionLoom Examples

MotionLoom examples are organized for both human browsing and AI DSL learning.

The repo keeps two example families separate:

- `core/`: minimal, single-purpose or domain-focused examples for learning MotionLoom structure.
- `showcase/`: reserved for polished YouTube / Shorts style examples. This folder is intentionally empty for now.

## Core Domains

- `core/scene/` uses `cs-000001` IDs for 2D Scene / Timeline examples.
- `core/world/` uses `cw-000001` IDs for 3D World examples.
- `core/process/` uses `cp-000001` IDs for GPU Process pipeline examples.
- `core/composition/` uses `cm-000001` IDs only for examples that mix Scene + World + Process.

## Composition Rule

`core/composition/` is not a general "nice layout" category. It is only for examples that combine graph families, for example a Scene output plus a World output passed through a Process graph.

Scene-only title animation, text effects, layout, audio spectrum, masks, gradients, and transitions stay in `core/scene/` even when they combine many Scene nodes.

## Naming Rule

- Scene: `cs-000001`, `cs-000002`, ...
- World: `cw-000001`, `cw-000002`, ...
- Process: `cp-000001`, `cp-000002`, ...
- Composition: `cm-000001`, `cm-000002`, ...

IDs are stable. Category and feature discovery is handled by metadata and generated browse files, not by renaming folders.

## How To Use In Anica

1. Open Anica.
2. Go to the VFX / MotionLoom page.
3. Open any `main.motionloom` file.
4. Copy the full content.
5. Paste it into the MotionLoom editor.
6. Preview or render.

## Browse

- [All Examples](browse/all.md)
- [Domain Index](browse/domains.md)
- [Feature Index](browse/features.md)
- [DSL Pattern Index](browse/dsl.md)
- [Core Examples](browse/core.md)
- [Showcase Examples](browse/showcase.md)

## Dataset

- `dataset/examples.jsonl`: all examples, one per line.
- `dataset/core.jsonl`: current core examples.
- `dataset/showcase.jsonl`: empty until showcase examples are added.
- `dataset/by-domain.json`: Scene / World / Process / Composition lookup.
- `dataset/by-feature.json`: feature lookup.
- `dataset/by-dsl.json`: DSL structure lookup.
