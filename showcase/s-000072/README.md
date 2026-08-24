# S72 — Rigid Body Drop Lab

This five-second WebGPU showcase demonstrates MotionLoom's unified 3D
`RigidBody` contract. One Scene contains static arena walls, an authored
kinematic pedestal and eight closely staged dynamic objects simulated by the
same fixed-step `Physics` context. Their lower, converging spawn positions make
the collision sequence denser and reach the settling phase sooner.

The objects use cube, tower, slab, bar and brick proportions together with
different mass, friction, restitution, damping, initial velocity and angular
velocity. The small lime object travels at high
speed with `continuousCollision="true"`, exercising adaptive collision
substeps instead of passing through the opposite wall.

Each dynamic body uses `shape="auto"`. MotionLoom derives the effective box
collider from the same authored Model bounds and scale used by rendering, so
the visible object and its physics shape share one transform contract.

Dynamic orientation is integrated as a quaternion. Shape-derived inertia,
normal and tangential contact impulses, rolling friction and persistent
linear-plus-angular sleep thresholds allow each body to bounce and tumble,
then become completely still after sustained rest.

No `AnimationTarget` or `ApplyAction` controls the dynamic Models. Physics is
their only transform owner, which keeps preview, scrubbing and export
deterministic. Static initial poses are eligible for retained timeline baking,
so every rendered frame reads the prepared simulation result directly.

## What this example teaches

- Use one `<RigidBody>` tag for every 3D body type.
- Keep `dimension="3d"` and `type` explicit for schema-driven authoring.
- Share gravity, fixed step and solver iterations through `<Physics>`.
- Use static bodies for floors and containment walls.
- Use kinematic bodies for authored non-dynamic collision geometry.
- Compare light/bouncy and heavy/high-friction dynamic behavior.
- Use `rollingFriction` to dissipate residual spin at supported contacts.
- Gate bounce with `restitutionThreshold` to avoid micro-bouncing at rest.
- Require both linear and angular stillness for `sleepTime` before sleeping.
- Enable CCD for fast objects.
- Use `shape="auto"` when the rendered Model bounds are the desired collider.
- Use `PhysicsDebug` for collider, contact-manifold, sweep and correction evidence.
- Avoid assigning animation and dynamic physics to the same transform.

All visible 3D assets use first-class typed `PrimitiveAsset` declarations. The
environment light uses an inline one-pixel data URI, so the Showcase remains
self-contained and requires no network asset download.
