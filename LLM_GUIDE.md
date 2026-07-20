# MotionLoom Example Guide for LLMs

Read the canonical crate guide first:
[`../anica/crates/motionloom/LLM_AUTHORING.md`](../anica/crates/motionloom/LLM_AUTHORING.md).

## Choosing an Example Family

- `core/`: minimal examples that teach one feature or one coherent feature set.
- `showcase/`: polished compositions and end-to-end creative demonstrations.
- Find the nearest core example before generating a new script. Reuse its
  grammar and replace its creative content.

## Stable Authoring Rules

- Preserve `Graph -> Scene -> Timeline -> Track -> Sequence -> Layer` for scene
  content. Do not create convenience shorthand.
- Use stable semantic IDs for anything animated, referenced, selected, or
  edited by UI.
- Demonstrate the feature directly; do not add unrelated effects merely to make
  a core example look more complex.
- Keep showcase scripts readable by grouping related artwork and naming major
  controls or animated parts.
- Prefer one animation system per property: `curve(...)` or
  `AnimationTarget`, never both.
- Use real masks for clipping and reveals instead of fragile opacity swaps.
- Do not publish maturity labels such as `LEVEL7` or `LEVEL8` in IDs, captions,
  filenames, or metadata.

## Example Metadata

- Keep the directory naming convention for its family.
- Update `example.json` when that family uses metadata.
- Describe the demonstrated feature, not implementation history.
- Keep titles and descriptions useful to search, datasets, and future LLMs.

## Validation

From the `anica` repository:

```sh
cargo run -p motionloom --example render_file_frame -- \
  ../motionloom-example/path/to/main.motionloom /tmp/frame.png 0 cpu
```

For GPU-specific behavior:

```sh
cargo run --release -p motionloom --example wgpu_live_preview -- \
  ../motionloom-example/path/to/main.motionloom
```

## Submission Checklist

- The script parses and renders.
- The example belongs in the chosen family.
- IDs are stable and references resolve.
- The core concept is visible without reading comments.
- The script contains no unsupported syntax or duplicate attributes.
- Documentation or metadata is updated when the example introduces a new
  public feature.
