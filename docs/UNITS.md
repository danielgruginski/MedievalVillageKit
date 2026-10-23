# Animated units

Kit pieces that move: rigged, animated versions of kit props for a game's units. Static pieces stay as they are; a
unit is a separate asset built from the same builder code (the builder tags its parts, the unit pipeline splits and
rigs them). First unit: the siege catapult (2026-10-23, HANDOFF 140).

## Siege catapult (`VKU_SiegeCatapult`)

The orcs' onager (`vki_props_orc.vki_orc_catapult`, static `SM_VKI_Prop_Siege_Catapult` / `_Burnt`) as a field unit
for the RPG. Daniel (2026-10-23): "Do these tasks you mentioned" -- a rigged throwing arm and wheels, a load-and-throw
clip; model, rig, clips and export, no game wiring.

- **Geometry:** the static's own. `vki_orc_catapult` calls `vki_orc_part(k, name)` after each part (a no-op on a plain
  `VKIKit`: the static pieces hash the same before and after); `src/units/vku_siege_catapult.py` builds it with a
  tagging kit and splits frame, four wheels, arm, stone in the cup and windlass. Left out: the lashing rope and the
  stones stacked on the ground. Added: a rope from the windlass (stretched by its bone) and a cut across the arm at
  62 % of its length (the halves meet inside the arm until Destroyed snaps it). 2,028 triangles, 1,110 vertices; the
  kit's materials (M_VK_Wood, M_VK_Iron, M_VK_Burlap, M_VK_Void, M_VKI_StoneBlockIn) and vertex colours, one UV set,
  no texture of its own. The projectile `SM_VKU_CatapultStone`: the cup's stone, 20 triangles, r ~0.17 m.
- **Rig (Generic, 13 bones):** `Root` (skeleton parent, never moves) and `Motion` (its sibling, root motion only;
  both point up with +Z to the front, so Motion imports with identity orientation); under Root: `Frame` ->
  `Wheel_FL/FR/BL/BR` (the engine's own left is +X in Blender, -X in Unity), `Arm` (on the skein's axle) -> `Arm_Tip`
  -> `Socket_Projectile`, `Stone`; `Windlass`; `Rope`. Every vertex weighted 1.0 to one bone. Bind pose = the static
  piece (arm drawn back, stone in the cup, the rope hanging loose).
- **Socket_Projectile:** at the stone's centre; its +Z (Unity forward) points out of the cup, so at Throw's `Release`
  event it is the stone's launch direction (47.6 deg up, toward the front), its +Y runs along the arm.
- **Clips (30 fps):**

| Clip | Frames / s | Loop | What | Events |
|---|---|---|---|---|
| Idle | 90 / 3.0 | yes | arm resting against the padded stop, a slight creak, the loose rope sways | |
| IdleLoaded | 60 / 2.0 | yes | drawn back on the windlass, stone in the cup, the arm strains a hair | |
| Move | 64 / 2.133 | yes | root motion 1.0014 m/s straight ahead (2.1363 m a loop), wheels one full turn a loop (v = w r, slip 1e-5 m/s), arm rattles, rope swings | |
| Load | 150 / 5.0 | no | the rope swung over the drum and run out to the arm (the windlass pays out), eight heaves wind the arm down onto the drum (the windlass turns with the rope's length), the stone drops into the cup; ends on IdleLoaded | Hooked 1.2, Loaded 4.633 |
| Throw | 45 / 1.5 | no | trigger, the hook lets go, the arm whips up in 6 frames, the stone leaves at Release (hidden from then: Stone bone scaled to 0.001), slams the stop, bounces, the back of the frame kicks up 4 deg; ends on Idle | Release 0.233, Slam 0.333 |
| Hit | 18 / 0.6 | no | shoved back 7 cm (wheels turn with it), the front bucks up 2.5 deg, arm rattles; ends on Idle | |
| Destroyed | 44 / 1.467 | no | the front-left wheel slides off its axle and falls flat, the frame tips 9 deg onto that corner, the arm snaps: the stump falls back, the tip topples over the pad and lands in front; holds | Break 0.167, Snap 0.4 |

  Burnt look for the wreck: a material swap, not a mesh (the Unity setup's `M_VKU_WoodCharred` = M_VKI_WoodDark x 0.46,
  on `VKU_SiegeCatapult_Charred.prefab`). The static `SM_VKI_Prop_Siege_Catapult_Burnt` (ash bed, embers) is a
  different arrangement: swapping to it after Destroyed would pop.
- **Checks** (`check`): lowest vertex per clip (Idle/IdleLoaded/Load +8.5 mm = the 14-sided wheel's flat, Move 0.0,
  Throw +3.2, Hit -0.3, Destroyed 0.0 mm); Move traced from the keys (skeleton in place, Motion straight along -Y,
  slip); moving parts against the fixed ones frame by frame (triangle overlaps: none in any clip); the socket at
  Release; `reimport` reads the written FBX back (13 bones, Motion unparented, one mesh, UVs, `Col`; Move's Motion
  -2.1363 m, wheel 45 deg per 8 frames; Throw's Stone scale 1 -> 0.001 at frame 7).

### Running it

```
# stage 1, the parts from the kit's builder (the kit's .blend is opened, never saved; also checks the static pieces'
# mesh hashes against HEAD's vki_props_orc)
blender -b blender/medievalDiorama.blend --python tools/unit_catapult_run.py -- parts
# stage 2, in the unit's own file blender/vku_siege_catapult.blend
blender -b blender/vku_siege_catapult.blend --python tools/unit_catapult_run.py -- rig clips check renders export reimport save
```

Stage 1 rewrites `blender/vku_siege_catapult.blend` (parts, stone, ground, lights), so stage 2 must follow with `rig
clips`. `renders only=views,throw,...` renders a subset. Renders go to `renders/units/siege_catapult/`; the export to
the package's `Art/Units/SiegeCatapult/` (live: the open editor imports it, so export when Unity isn't playing).

### Unity

Live in the package since 2026-10-23 (it was first staged in `Units~` folders, which Unity skips: the package is
referenced by MedievalSetting through a `file:` path, so anything under it is imported and compiled by the open
editor): `Runtime/Units/KitUnitEvents.cs`, `Editor/Units/KitSiegeCatapultSetup.cs`, `Art/Units/SiegeCatapult/`.
**Tools > Medieval Kit > Units > Build Siege Catapult** (needs the kit's materials: Build Materials). It builds into
`Generated/Units/SiegeCatapult/`: `AC_VKU_SiegeCatapult.controller` (Idle default; bool Moving; triggers Load, Throw,
Hit, Destroyed: Idle <-> Move, Idle -> Load -> IdleLoaded -> Throw -> Idle, Idle/Move -> Hit -> Idle, any -> Destroyed),
`VKU_SiegeCatapult.prefab` (Animator, root motion off, `KitUnitEvents` receiving `OnUnitEvent`),
`VKU_SiegeCatapult_Charred.prefab`, `M_VKU_WoodCharred.mat`, `VKU_CatapultStone.prefab` (mesh, sphere collider,
45 kg rigidbody). Report and preview-scene renders: `Logs/MedievalKit/SiegeCatapult/` (`setup_report.txt`,
`lineup.png`, `throw_close.png`, `lineup_game_22m.png`).
