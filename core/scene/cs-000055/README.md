# Universal Layer Puppet

This is the smallest complete universal Puppet Warp example.

- `target="@layer"` selects the current Layer instead of a Group id.
- `capture="before"` captures all earlier visual siblings exactly once.
- The two pins deform that captured surface; later siblings remain normal overlays.
- Existing `target="GROUP_ID"` Puppet Warp syntax remains available for isolated parts.

Place a universal Puppet directly inside a `Layer`. MotionLoom rejects `@layer`
without `capture="before"` so capture order is explicit and deterministic.
