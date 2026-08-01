# Universal Layer Puppet Character

This showcase deforms a complete character Layer without targeting an artwork
Group.

- `target="@layer" capture="before"` captures the title and character exactly once.
- A local bone topology affects the raised arm while `preserveOutside="true"`
  keeps the rest of the captured character intact.
- Shoulder, elbow, and wrist pins use the same rigid two-bone solver as Isolate
  Part rigs.
- The labels after `PuppetWarp` remain normal, undeformed overlays.

Group-target Puppet Warp remains the correct mode when the source already has a
clean semantic arm, hair, eye, or clothing Group.
