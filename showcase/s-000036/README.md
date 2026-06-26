# s-000036 Stickman Five Finger FK Rig

A MotionLoom showcase for a stickman hand with five FK-controlled fingers.
The enlarged right hand uses one palm, five fingers, and three phalanx bones per finger.

- Duration: `5s`.
- Canvas: `1280x720`.
- Uses `Skeleton`, `Bone`, `Action`, `Pose`, `Character`, `Part`, and `ApplyAction`.
- Demonstrates open hand, counting pose, fist curl, spread, and wave timing.

Run:

```bash
cargo run -p motionloom --example render_file_frame -- ../motionloom-example/showcase/s-000036/main.motionloom /tmp/s-000036-frame.png 75 cpu
```
