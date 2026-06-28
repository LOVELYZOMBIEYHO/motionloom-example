# AnimationTarget Advanced Targets

This core scene extends `AnimationTarget` beyond basic transform properties.

## What it demonstrates

- `Pin` `x` and `y` targets for Puppet-style deformation.
- `Path` `d` targets that compile into the existing `morph(...)` path pipeline.
- Skeleton `Bone` `rotation` targets that flow through the existing rig and `ApplyAction` pipeline.
- A UI-friendly data model: each editable channel is addressed by `node + property + frame`.
