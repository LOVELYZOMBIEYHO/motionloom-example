# S70 — Character 1 Action Gauntlet

This 54-second WebGPU showcase turns the canonical `character1.glb` into a
complete animation-library reel without editing the source model. Character 1
provides one humanoid skeleton and 43 embedded clips; MotionLoom exposes every
clip as a typed `Action` node and schedules it through `ApplyAction`.

The reel is completely linear: `01 / A_TPOSE` starts at zero, every following
entry advances by one, and `43 / WALK LOOP` closes the graph. Each clip gets an
equal 1.4-second action window with a 0.12-second crossfade. Exact source clip
names remain visible in the HUD; numbering never resets or repeats.

The 3D island also declares a finite box `Surface` and deterministic
`Physics`. Character 1 opts into `gravity="scene"` with a kinematic collider.
Because the performance has active `ApplyAction` choreography, the authored
root path continues to own deliberate jumps while Physics prevents floor
penetration and keeps grounded phases aligned with the stage. The visible
20-by-20 blue floor uses the same 0.08-thick box as collision, so its rendered
top surface is direct evidence of the physical ground rather than decoration.

## What this example teaches

- Reuse one canonical GLB as both `ModelAsset` and raw `AnimationAsset` source.
- Enumerate and play all 43 embedded animation clips in their exact GLB order.
- Wrap embedded clips in executable `Action` nodes.
- Crossfade many `ApplyAction` phases without exposing raw clip ids downstream.
- Combine upper- and lower-body clips through body masks.
- Keep clip animation in-place and author root choreography separately.
- Layer semantic bone channels over baked animation.
- Direct four `Camera3D` nodes through a typed `activeCamera` channel.
- Ground an action-driven humanoid on a finite box `Surface` through Scene
  `Physics`, without flattening its authored jump arc.
- Finish the scene through an explicit bloom and grain texture pipeline.

The model asset is loaded from the repository's canonical GitHub raw URL, so
the same DSL can run in the desktop renderer and in the browser showcase.
