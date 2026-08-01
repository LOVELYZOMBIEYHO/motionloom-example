# Fox Tail Chain Puppet

This showcase rigs a fox tail as a non-branching parent-linked chain.

- `PuppetWarp solver="chain"` preserves the authored tail surface while its
  controls follow a fixed root-to-tip hierarchy.
- `MeshTopology` defines the tail strip explicitly with paired upper and lower
  vertices.
- Parent-linked `PuppetPin` nodes keep segment lengths stable.
- The animated tip controller drives the main motion, while `SpringChain`
  supplies deterministic follow-through and overlap.

Load `main.motionloom` in the MotionLoom Graph UI and drag the final control pin
to pose the complete chain.
