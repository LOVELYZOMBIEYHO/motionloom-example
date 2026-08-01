# GLB Draco Model in a Unified Scene

This minimal example declares the supplied iPhone as a `ModelAsset`, renders it
inside a `space="3d"` `CompositeGroup`, and composites a screen-space caption
through the same Scene Render Pass DAG.

It demonstrates the public Scene architecture only; no `<World>` tag is
required. The existing Process effect pipeline remains unchanged.
