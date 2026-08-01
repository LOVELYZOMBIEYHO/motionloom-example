# Bone Puppet Two-Bone IK

This is the smallest complete rigid-limb example.

- `solver="bones"` switches Puppet Warp from soft radial deformation to two-bone IK.
- The three pins use `role="anchor"`, `role="joint"`, and `role="control"`.
- `bone="upper|forearm|hand|joint"` assigns each mesh vertex to a rigid region.
- `stretch="0"` keeps the authored segment lengths.
- The wrist target is animated; the elbow is solved by MotionLoom.

Use `preserveOutside="true"` when the target is a complete character and the
topology only encloses one limb. Leave it false for an already isolated arm.
