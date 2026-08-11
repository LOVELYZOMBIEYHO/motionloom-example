# Spartan Deck Vault

Showcase 70 is a 3.2-second 3D action sequence. MotionLoom retargets one
`Jump_Over` clip onto canonical Character 1, aligns the performance to semantic
points on a scanned vessel environment, and presents it through three timed
camera cuts.

## What it demonstrates

- GitHub raw loading of canonical `character1.glb`;
- a separate raw `AnimationAsset` wrapped by an executable humanoid `Action`;
- action markers for takeoff, contact, and landing;
- `ModelProfile` retargeting and calibrated bone axes;
- `Environment`, semantic `Surface`, and local `Anchor` declarations over a GLB
  environment;
- target-matched root motion, automatic grounding, foot lock, and a full-body
  action mask;
- three `Camera3D` nodes selected through
  `AnimationTarget property="activeCamera"`;
- bloom and film grain after the complete Scene render.

## Assets

- Character 1 is the shared CC0 Quaternius humanoid stored at
  `assets/sample_assets/characters/character1/character1.glb`.
- `assets/actions/Jump Over.glb` supplies the imported action clip.
- `assets/environment/mv_spartan.glb` supplies the vessel environment.

The action and environment are kept separate from Character 1 so another
compatible humanoid or environment can reuse the choreography. Confirm the
provenance and redistribution terms of imported action and environment assets
before publishing them outside this example repository.

Load **Showcase 70** in the MotionLoom Graph UI to preview `main.motionloom`.
