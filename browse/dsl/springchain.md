# DSL Pattern: springchain

| ID | Type | Domain | Title | Features | Teaches |
|---|---|---|---|---|---|
| [cs-000057](../../core/scene/cs-000057/) | core | scene | Parent-Linked Chain Puppet | scene, puppet-warp, puppet-pin, mesh-topology, spring-chain | Create a serial root-to-tip pin hierarchy with explicit parent ids.<br>Preserve each authored segment length while moving the final control. |
| [s-000053](../../showcase/s-000053/) | showcase | scene | Monochrome Anime Bob Hair Dynamics | scene, anime, portrait, hair, spring-chain | Construct a high-contrast anime bob from editable silhouette, bang, side-lock, and shine paths.<br>Use Wind, Collider, and SpringChain to animate flyaways and face locks without destabilizing the main haircut. |
| [s-000065](../../showcase/s-000065/) | showcase | scene | Fox Tail Chain Puppet | scene, puppet-warp, puppet-pin, mesh-topology, spring-chain | Rig a fox tail with a non-branching parent-linked pin chain.<br>Move one tip controller while fixed-length segments follow. |
| [csim-000001](../../core/simulation/csim-000001-gravity/) | core | simulation | Gravity Dynamic Curve | gravity, dynamic-curve | Apply a named deterministic Gravity resource to a Curve. |
| [csim-000002](../../core/simulation/csim-000002-wind/) | core | simulation | Wind Dynamic Curve | wind, turbulence | Reference a Wind resource from a SpringChain. |
| [csim-000003](../../core/simulation/csim-000003-attraction/) | core | simulation | Attraction Force | attraction | Pull a dynamic curve toward an attraction point. |
| [csim-000004](../../core/simulation/csim-000004-circle-collision/) | core | simulation | Circle Collision | circle-collision | Project dynamic curve particles outside a circle collider. |
| [csim-000005](../../core/simulation/csim-000005-capsule-collision/) | core | simulation | Capsule Collision | capsule-collision | Collide a dynamic curve with a capsule segment. |
| [csim-000006](../../core/simulation/csim-000006-distance-constraint/) | core | simulation | Distance Constraint | distance-constraint | Preserve rest lengths through iterative distance constraints. |
| [csim-000008](../../core/simulation/csim-000008-spring-chain/) | core | simulation | Spring Chain Hair Guide | spring-chain, hair | Drive a hair guide with gravity, wind and head collision. |
