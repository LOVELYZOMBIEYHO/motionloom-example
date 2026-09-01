# S76 — Landing Page Action Locomotion Reel

This twenty-second showcase drives an imported GLB entirely with Action Editor
code copied verbatim from `anica-landing-page/public/motionloom-actions/actions`.
The character walks onto a runway, waves, runs out, and settles into idle.

## What this example tests

- Keep authored reusable motion outside the main scene DSL.
- Select the landing page's standard walk, wave greeting, standard run, and
  listening idle without copying dense poses into the showcase graph.
- Resolve one relative source in native preview and through the existing WASM
  byte resolver.
- Cache the hydrated action graph across frames.
- Preserve the established `Action`, `ApplyAction`, and humanoid retargeting
  behavior without introducing an `ActionAsset` type.

## File contract

The library file has an `ActionLibrary` root and authored `Action` children.
The scene declaration supplies its own namespace and explicit selection list:

```xml
<ActionLibrary id="run"
               src="../../assets/action_libraries/landing_page/run-standard.motionloom"
               actions={["run_standard_loop"]} />
```

An `ApplyAction` then references `run.run_standard_loop`. The external source file can
grow independently while this showcase remains compact and readable.
