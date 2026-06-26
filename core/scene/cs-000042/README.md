# Stickman IK FK Template

A compact MotionLoom template that keeps FK and IK visually separated. The first
half shows an FK arm driven by parent-child rotations; the second half fades to a
two-bone IK arm where the wrist follows a target marker.

## What it demonstrates

- `Skeleton` with a direct `shoulder -> elbow -> wrist` chain.
- FK animation as nested `Group` rotations for shoulder and elbow.
- IK animation as an `Action` with a moving `IK` target.
- Phase gating with opacity curves so FK and IK do not appear on the same screen.

## Notes

This example is intended as a clean IK/FK template: FK controls are visible only
in the first phase, and the IK target plus solved rig are visible only in the
second phase.
