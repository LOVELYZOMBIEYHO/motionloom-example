# MotionLoom Examples

MotionLoom examples are organized for both human browsing and AI DSL learning.

The repo keeps two example families separate:

- `core/`: minimal, single-purpose or domain-focused examples for learning MotionLoom structure.
- `showcase/`: polished product films, motion studies, and YouTube / Shorts style examples.

## Core Domains

- `core/scene/` uses `cs-000001` IDs for 2D Scene / Timeline examples.
- `core/world/` contains `cw-000001` legacy compatibility fixtures. Do not use
  `<World>` when authoring new DSL; place 3D content in a Scene `space="3d"`
  track.
- `core/process/` uses `cp-000001` IDs for GPU Process pipeline examples.
- `core/composition/` uses `cm-000001` IDs for examples that combine Scene and
  Process graph behavior.

## Composition Rule

`core/composition/` is not a general "nice layout" category. It is for examples
that combine Scene output and explicit Process dependencies or passes.

Scene-only title animation, text effects, layout, audio spectrum, masks, gradients, and transitions stay in `core/scene/` even when they combine many Scene nodes.

## Naming Rule

- Scene: `cs-000001`, `cs-000002`, ...
- Legacy World compatibility fixtures: `cw-000001`, `cw-000002`, ...
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
- `dataset/showcase.jsonl`: all showcase metadata, one record per line.
- `dataset/by-domain.json`: Scene / legacy World / Process / Composition lookup.
- `dataset/by-feature.json`: feature lookup.
- `dataset/by-dsl.json`: DSL structure lookup.

## Showcase Dataset Contract

A showcase is a linked set of artifacts, not only a DSL file:

```text
showcase/s-XXXXXX/
├── README.md          human-facing explanation
├── example.json       intent and retrieval metadata
├── schema.json        generated per-example syntax description
├── main.motionloom    executable source of truth
├── assets/            optional portable assets
└── evidence/          optional verified render evidence
```

The first four files are required for every showcase. `assets/` is present only
when the document needs local portable files. `evidence/` is the recommended
location for future training and visual-regression artifacts; existing
showcases are not required to contain it yet.

### Artifact ownership

| Artifact | Maintained by | Purpose |
| --- | --- | --- |
| `README.md` | Human | Explain the creative result and important techniques |
| `example.json` | Human or dataset curator | Search, retrieval, intent, features, and teaching labels |
| `schema.json` | MotionLoom generator | Describe syntax actually demonstrated by `main.motionloom` |
| `main.motionloom` | Human, editor, or LLM | Canonical executable composition |
| Authoring report | MotionLoom analyzer | Validate one exact DSL revision and recommend repairs |
| Render evidence | Renderer plus reviewer | Verify the visual result against the intended outcome |

Do not edit `schema.json` manually. Regenerate it whenever `main.motionloom`
changes. An authoring report is normally generated on demand and does not need
to be committed beside every clean showcase. If reports are stored for
post-training or regression data, record the source revision or content hash.

### Agent and training flow

```text
example.json
    └── retrieve an example matching the requested intent

schema.json
    └── discover the syntax demonstrated by that example

main.motionloom
    └── learn, generate, or edit the complete composition

motionloom_analyze_script_json()
    └── detect errors and return machine-readable repair suggestions

render evidence
    └── verify that the valid DSL also satisfies the visual intent
```

For a post-training record, link the prompt, example ID, source DSL, authoring
report, and render evidence. A record is invalid if its report or evidence was
produced from a different DSL revision.

Recommended evidence layout:

```text
evidence/
├── frame-opening.png
├── frame-middle.png
├── frame-final.png
└── evaluation.json
```

`evaluation.json` should identify the source revision, render target, output
size, sampled times or frame numbers, and the accepted visual criteria. Video
or additional frames may be included when still images cannot demonstrate the
motion behavior.

## Per-showcase Learning Schema

Every `showcase/s-XXXXXX/` directory contains:

- `main.motionloom`: the complete portable DSL document.
- `example.json`: searchable example metadata.
- `README.md`: human-facing explanation.
- `schema.json`: the exact language slice demonstrated by that script.

`schema.json` lists the used tags and attributes, representative authored
values, animation capability, animation properties, and asset kinds. It helps
an LLM learn from one showcase; it is not a validation report for a newly
generated script.

After editing or adding showcases from this workspace, regenerate all learning
schemas with:

```sh
cargo run -p motionloom --example build_showcase_schemas -- ../motionloom-example/showcase
```

For generated DSL, separately call `motionloom_analyze_script_json()` after
every revision. That report contains errors, warnings, effective behavior, and
recommended repairs for the LLM feedback loop.
