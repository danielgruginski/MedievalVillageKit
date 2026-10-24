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
  62 % of its length (the halves meet inside the arm until Destroyed snaps it), and (2026-10-23, HANDOFF 141) a basket
  of stones on the rear cross beam's +X end, beside the windlass (`_basket`: a burlap lathe closed on top by a
  stone-faced heap, three stones on the heap; 204 triangles, rides the Frame bone). 2,232 triangles, 1,220 vertices; the
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
| Load | 150 / 5.0 | no | the rope swung up over the drum and run out to the arm over 56 frames, the windlass easing up to 2.5 turns a second and back to rest as it pays out; eight heaves wind the arm down onto the drum (the windlass turns with the rope's length); the next stone, grown to size unseen inside the basket's closed body (frames 98-104), is lifted straight out of the heap (106-118), swung over and set down in the cup (139); ends on IdleLoaded | Hooked 1.9, Loaded 4.633 |
| Throw | 45 / 1.5 | no | trigger, the hook lets go, the arm whips up in 6 frames, the stone leaves at Release (hidden from then: Stone bone scaled to 0.001), slams the stop, bounces, the back of the frame kicks up 4 deg; ends on Idle | Release 0.233, Slam 0.333 |
| Hit | 18 / 0.6 | no | shoved back 7 cm (wheels turn with it), the front bucks up 2.5 deg, arm rattles; ends on Idle | |
| Destroyed | 44 / 1.467 | no | the front-left wheel slides off its axle and falls flat, the frame tips 9 deg onto that corner, the arm snaps: the stump falls back, the tip topples over the pad and lands in front; holds | Break 0.167, Snap 0.4 |

  Burnt look for the wreck: a material swap, not a mesh (the Unity setup's `M_VKU_WoodCharred` = M_VKI_WoodDark x 0.46,
  on `VKU_SiegeCatapult_Charred.prefab`). The static `SM_VKI_Prop_Siege_Catapult_Burnt` (ash bed, embers) is a
  different arrangement: swapping to it after Destroyed would pop.
- **Load in numbers** (2026-10-23, Daniel: "Do the number 4"; HANDOFF 141): the rope's run-out is 3.34 turns of the
  windlass. Before: 28 frames from a standing start at 7.0 turns a second (84 deg a frame, past the 45 deg at which the
  four-spoke cross strobes), mean 3.6. Now: 56 frames, eased 0 -> 2.51 -> 0 (35 deg a frame at most in the whole clip),
  mean 1.8. The heaves start 22 frames later and pause less between pulls (0.7 frames instead of 2.75): their peaks
  2.79 -> 2.92 turns a second, mean 1.27 -> 1.61. Hooked moved 1.2 -> 1.9 s; Loaded (4.633 s) and the length kept.
  A truly hand-paced windlass (~1 turn a second) would need Load at 6+ s: 7.1 turns of the drum fit in 5 s only this
  way. Chart: `renders/units/siege_catapult/windlass_speed_before_after.png`.
- **Checks** (`check`): lowest vertex per clip (Idle/IdleLoaded/Load +8.5 mm = the 14-sided wheel's flat, Move 0.0,
  Throw +3.2, Hit -0.3, Destroyed 0.0 mm); Move traced from the keys (skeleton in place, Motion straight along -Y,
  slip); moving parts against the fixed ones frame by frame (triangle overlaps: none in any clip); the socket at
  Release; `reimport` reads the written FBX back (13 bones, Motion unparented, one mesh, UVs, `Col`; Move's Motion
  -2.1363 m, wheel 45 deg per 8 frames; Throw's Stone scale 1 -> 0.001 at frame 7). Since 2026-10-23 also
  `check_load`: the windlass's speed from the keys (payout / heaves), the stone inside the basket's closed body in
  every frame it is not full size (rays from each of its vertices
  leave through the basket's own faces: none fail), the spokes through a whole turn against the basket (no hit, closest
  44.9 mm); `check_overlaps` adds Load's stone against the arm on its way in (only more than the seated stone's own
  5-triangle contact with its cup counts) and lists the stone passing through the heap's stones as it is lifted out
  (frames 111-117) apart as `Load_by_design`; `reimport` adds Load (the windlass at most 35 deg a frame) and reads the
  stone's keys from a scratch copy of Load whose default pose is frame 106 (Blender's importer takes a scaled bone's
  default as its rest: the delivered file's default is frame 0 with the stone hidden at 0.001, read 1000x; Unity plays
  the keys): cup 0.001 at 97, basket 0.001 at 98-100, full size there at 104, lifted to 1.47 m at 118, (0.34, 1.91,
  1.75) at 127, seated (0, 1.991, 1.481) at 139.

### Running it

```
# stage 1, the parts from the kit's builder (the kit's .blend is opened, never saved; also checks the static pieces'
# mesh hashes against HEAD's vki_props_orc)
blender -b blender/medievalDiorama.blend --python tools/unit_catapult_run.py -- parts
# stage 2, in the unit's own file blender/vku_siege_catapult.blend
blender -b blender/vku_siege_catapult.blend --python tools/unit_catapult_run.py -- rig clips check renders export reimport save
```

Stage 1 rewrites `blender/vku_siege_catapult.blend` (parts, stone, ground, lights), so stage 2 must follow with `rig
clips`. `renders only=views,throw,...` renders a subset (also `windlass`, `stone`, `gameload`: the run-out close up,
the stone's way close up and as copies in one picture, the 22 m camera on Load). Renders go to
`renders/units/siege_catapult/`; the export to the package's `Art/Units/SiegeCatapult/` (live: the open editor imports
it, so export when Unity isn't playing) -- or, with `export_dir=<folder>` (relative: to the repo) or the env var
`VKU_EXPORT_DIR`, to a staging folder laid out the same way (`<folder>/VKU_SiegeCatapult.fbx`, `<folder>/Anims/...`)
whose files are then copied over the package's (their `.meta` files stay). `export` and `reimport` both use it:

```
blender -b blender/vku_siege_catapult.blend --python tools/unit_catapult_run.py -- rig clips check renders export reimport save export_dir=renders/units/siege_catapult_export/SiegeCatapult
```

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

The setup takes the clips' events from `Anims/siegecatapult_clips.json`, so a moved event (Load's Hooked, 1.2 -> 1.9 s
on 2026-10-23) needs no code change: re-run Build Siege Catapult after the new files are in. Its lineup samples Load at
2.0 s, which is now the rope just hooked to the upright arm (it was halfway through the heaves).
