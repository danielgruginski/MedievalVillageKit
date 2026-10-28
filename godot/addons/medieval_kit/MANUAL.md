# Medieval Village Kit for Godot: manual

How the addon's systems work and what a game has to do to use them (Godot 4.7, .NET / C#). The addon is the Godot side
of the kit's Unity package and offers the same systems; where Godot works differently, it says so. Everything is in
the `MedievalKit` namespace.

Contents:

1. [Getting started](#1-getting-started)
2. [Levels and travel](#2-levels-and-travel)
3. [The camera](#3-the-camera-kitcamera)
4. [The see-through](#4-the-see-through)
5. [Click to move and the walker](#5-click-to-move-and-the-walker)
6. [Usable things](#6-usable-things-interactable)
7. [Fires](#7-fires)
8. [Missiles, the ground, walkways](#8-missiles-the-ground-walkways)
9. [Creature silhouettes](#9-creature-silhouettes)
10. [Hooks a game fills](#10-hooks-a-game-fills)
11. [Checks from the command line](#11-checks-from-the-command-line)
12. [What the Godot addon does not have](#12-what-the-godot-addon-does-not-have)

## 1. Getting started

What is where in the project:

| Path | What |
|---|---|
| `res://addons/medieval_kit/` | the addon: `Runtime/` (levels, travel, the see-through, fires...), `Walker/` (the camera, click to move, the walkers, the demo), `Shaders/` (KitLit and its variants, the terrain, the silhouettes), `FX/` (the fire's flipbooks), `Editor/` (import, build, tests) |
| `res://kit/models/` | the pieces (.glb), each imported as a `KitPiece` with its colliders |
| `res://kit/materials/`, `res://kit/textures/` | the shared materials (KitLit) and their textures |
| `res://kit/layouts/` | the built levels (`<name>.tscn`, each with its navmesh `<name>_nav.res`) |
| `res://kit/structures/` | the premade structures (a smithy, a brewery...: `KitStructure`) |
| `res://kit/world.tres` | the world graph (`KitWorld`): which level links to which, and the start |
| `res://kit/see_through_caps.res` | the see-through's caps, baked (section 4) |

1. **Enable the plugin** (Project > Project Settings > Plugins > Medieval Kit). The first time it adds two global
   shader uniforms (`kit_see_through`, `kit_see_through_args`) and raises the instance-uniform buffer to 1,048,576
   (every kit material has instance uniforms, and Godot gives each instance 16 slots). It asks for a restart:
   Project > Reload Current Project. Without these settings the kit's shaders do not compile.
2. **Build the C#** (the Build button, or `dotnet build` in the project folder).
3. **Play.** The project's main scene is the demo (`Walker/kit_demo.tscn`): pick a level and walk it with WASD (E at a
   door), Tab through Blender's camera views, F for a free camera.
4. **Walk a level with the kit's own walker**: Project > Tools > Medieval Kit: Play From Start Level (the valley
   town, the start of the example world: 20 levels linked by doors, stairs, a mine adit and a sewer grate), or open a
   level from `res://kit/layouts/` and use Medieval Kit: Walk This Level. Where the level has a navmesh you get
   `KitWalker` (click to walk, click a door to go through, the kit's camera with the see-through on); elsewhere the
   WASD `KitTestWalker`. Nothing is saved into the level.

The other menu items: Check Pieces (every imported piece against the kit's data), Build Layouts (the levels again
from `res://kit/data/layouts/`; bake the caps again after it, section 4).

## 2. Levels and travel

- **`KitLevel`** is a level's root (Blender's camera settings in `Props`, the world graph in `World`). When it first
  stands in the tree it sets itself up, once: its pieces' bounds for the see-through, its structures as see-through
  buildings with their cuts and caps, its kit fires lit (`LightFires`, on), its walkway decks (section 8). Two
  switches turn that off for a game that does its own: `KitLevel.SetUpSeeThrough`, `KitLevel.LightFires`.
- **`KitLink`** (an Area3D) is a way out: a door, a stair, a passage, a cave mouth. `Target` is a level name,
  `"@return"` (back the way the walker came in: a building's door) or `"@deep"` (the world's open end: leads nowhere
  yet). `WalkInto` links (a road's end at the map's edge) are taken by walking into them.
- **`KitSpawn`** is where a walker arrives (`SpawnId`: the link's id on the other side).
- **`KitNavMesh`** is the level's baked walkable surface (a NavigationRegion3D on the kit walker's size: radius 0.3,
  height 1.8, step 0.35).
- **`KitTravel`** moves the walker between levels: `Go(link)`, `GoTo(level, spawn)` (a teleport, a respawn),
  `Reload(level, spawn)` (a fresh load: New Game, Load). `KitTravel.SetWalker(node)` registers the walker (it must
  live outside the levels, under the tree's root). With `Preload` on, the levels one link away are loaded in the
  background and held, so a door is an instant cut; a level not held yet loads behind a short fade. Events:
  `Arrived(level, spawn)`, `Leaving(link)`. `KitTravel.ScenePath` maps a level name to its scene (a game can map its
  own).

## 3. The camera (`KitCamera`)

The pieces are painted to be seen from one side: looking north (Godot -Z), 50 degrees down. `KitCamera` (a Camera3D)
holds that view and never turns.

- **Follow**: add it anywhere (it is top level) and set `Target` to the walker. It follows with a lag (`Smooth`) and
  cuts to the target when a level arrives through `KitTravel`. `Snap()` makes the same cut on demand (after a
  teleport).
- **Zoom**: the mouse wheel moves `Distance` between `ZoomNear` and `ZoomFar` (not while `KitPointer.Blocked` says the
  pointer is on the game's UI).
- **Take-over**: when a level comes in it makes itself current, with its own audio listener at the target ("Ears"),
  and tells the game whether the level is outdoors (`Entered` hook: a level with a node in the `kit_village` group).
- **Shadows**: the shadowed DirectionalLight3Ds' shadow distance is fitted to what the view reaches, and put back
  when the camera goes.
- **Border** (`KeepInBorder`, off): the view stops short of the level's edge, using a `KitMapFrame` from the
  `MapFrameOf` hook and `KitWalkWindow`.

Settings: `Pitch`, `Distance`, `ZoomNear` / `ZoomFar`, `ViewFov`, `Smooth`; the see-through's in the next section.

## 4. The see-through

When the walker goes behind a house, a wall or a structure, what stands between the camera and the walker opens in a
round hole round its chest. Four parts work together:

1. **The shader** (every kit material: `Shaders/kit_see_through.gdshaderinc`). It reads the two global uniforms:
   `kit_see_through` = the hole's centre (the walker's chest, xyz) and radius (w; 0 = off), and
   `kit_see_through_args` = the walker's feet height, the height kept whole over them, a margin in front of the
   walker, and the half-width of the wedge from the camera to its body. Only surfaces in that wedge open, never
   below the kept height.
2. **The marks** on each piece (`KitSeeThrough`). Godot has no per-renderer layers and gives a shader no object
   bounds, so both are instance uniforms on each GeometryInstance3D: `kit_layers` (the marks) and `kit_bmin` /
   `kit_bmax` (its world box, set by `KitSeeThrough.Bound` when the level stands). A level's structures
   (`KitStructure`, or a layout's `VKX_ST_` group) become **buildings** (`KitSeeThrough.SetUpLevel`, called by
   `KitLevel`): a building's pieces open together, decided each frame. `KitSeeThrough.Loose(group)` (trees, rocks,
   props: open down to the feet) and `KitSeeThrough.Runs(group)` (walls placed as props, opening in runs) are there
   for a game's own levels; the kit's village builder will call them (section 12).
3. **The caps**. Each building piece is cut 1.4 m over its building's floor, and a cap (the piece's own
   cross-section at the cut, filled) closes the stub, so you never see inside a wall (`KitSeeThroughCaps`). The cap
   meshes are **baked**: `kit_cli -- bakecaps` (section 11) writes `res://kit/see_through_caps.res`; bake again after
   rebuilding the layouts or re-exporting pieces. A piece the bank lacks gets its cap made in play, a few
   milliseconds a frame (Godot reads the mesh back from the GPU: a stall), and the game prints a reminder to bake. A
   pool of 96 cap meshes is laid each frame over the pieces in the hole's reach. Behind the caps, the one-sided kit
   materials' back faces are filled too (`KitLitCap`, each material's next pass).
4. **The driver** (`KitCamera`). Each frame it sets the globals round its `Target` (`KitSeeThrough.Set(hole, args)`).
   With `SeeThroughWhenHidden` (on) it opens the hole only while kit pieces really hide the walker:
   `KitSeeThroughProbe` (a 32 x 40 SubViewport) renders the walker's upper body a few times a second and reads back how
   much of it is covered. The hole opens over `SeeThroughOpenTime` once more than `SeeThroughCoverOpen` (12%) is
   hidden, and shuts over `SeeThroughShutTime` once under `SeeThroughCoverShut` (4%) for `SeeThroughHold` seconds.

**What a game must do:** use `KitCamera` (or a subclass) with `Target` set. A game with its own camera can drive the
hole by calling `KitSeeThrough.Set(hole, args)` each frame and `KitSeeThroughCaps.LayPool(camera)` after it (see
`KitCamera.SeeThrough` for the values), and `Set(Vector4.Zero, ...)` when it stops.

Things a character carries drawn with kit materials (a weapon, a shield): `KitSeeThrough.Keep(node)`, so they are
never cut. Pointer picking through the hole: `KitSeeThrough.Opened(point, distance, rayFrom, rayDir, collider)` (or
`KitClickToMove.Opened(hit, ray)`) says whether a ray hit lies in what the hole has opened. Read the hole back from
`KitSeeThrough.Hole` / `Args`, not from the RenderingServer (Godot reads globals back only in the editor).

Settings on `KitCamera`: `SeeThroughRadius` (2.4 m), `KeepBelow` (1.4 m, the caps' cut), `SeeThroughBody` (0.2 m;
keep it under the walker's radius), `SeeThroughNear` (0.25 m), and the hidden check's thresholds and times above.

## 5. Click to move and the walker

**`KitClickToMove`** is a walker's legs, Diablo-style, on the level's navmesh. It is a child node of the walker's body
(any Node3D), which it moves; it registers that body as KitTravel's walker and turns preloading on.

- **Click** the ground to walk there; **hold** the left button to keep walking toward the cursor. The point walked to
  is the floor under the cursor the walker can reach: the ray looks past crates, roofs and what the see-through has
  opened to the floor behind; over a roof or a wall it walks up beside it. While held, the way round an obstacle is
  kept (no swinging between left and right of a crate).
- **Ways out**: click a `KitLink` to walk to it and take it (`KitTravel.Go`); road ends (`WalkInto`) are taken by
  walking on into them, once the walker has stepped clear of the one it arrived by.
- **Usable things** (section 6): click to walk up and use.
- For a game's UI: `Hover` (the way out under the cursor), `HoverThing`, `Using`, the `Clicked` event (the point a
  click sent the walker to). From code: `MoveTo(point)`, `Interact(link)`, `Interact(thing)`.
- Clicks the game's GUI takes never reach it (they arrive through `_UnhandledInput`); `KitPointer.Blocked` covers UI
  drawn some other way.
- Movement: Godot's NavigationAgent3D cannot take a way worked out ahead (the held button needs one), so the walker
  follows its own way along the navmesh: `Speed` 4.5 m/s, `Acceleration` 30, `TurnSpeed` 720 degrees a second,
  `StoppingDistance` 0.05.
- `Pointer(out screen, out press, out held)` is virtual: a gamepad cursor or a test (`Editor/KitClickTest.cs`'s
  `KitTestLegs`) brings its own pointer.

**`KitWalker`** is the kit's stand-in player: `KitWalker.Spawn(transform)` puts a capsule with `KitClickToMove` legs and
a `KitCamera` under the tree's root, with a line of help and the door's prompt at the cursor. A game brings its own
player: its body, a `KitClickToMove` (or a subclass) as a child, a `KitCamera` targeting it.

## 6. Usable things (`Interactable`)

Something the player clicks to use: a find to loot, someone to talk to, a campfire, a sign. Subclass `Interactable`
(an abstract Node3D; it is in `Interactable.All` while in the tree) and give it `Label` and `Use()`. Optional:
`Cursor`, `Priority` (wins under the same click: talk 30, loot 20, campfire 10, sign 0), `UsePoint` (where the walker
walks to), `UseRadius` (1.5 m), `PickRadius` (0.8 m: a ground click this near counts as on it), `CanUse`, and for the
HUD `LabelPoint`, `Nameplate`, `Badge`, `Bubble` / `BubbleRange`, `Glint`.

A prop that stands for a usable thing kept elsewhere (a dead goblin's body for its loot on a marker): put a `UseVia`
node as a child of the prop's collision body and set its `Thing`; the cursor on the prop is on the thing.
`Interactable.Under(collider, point)` is the click's choice, for a game's own picking.

## 7. Fires

`Fire` makes fires out of `FireFx`'s parts (flames from an 8 x 8 flipbook, an additive core, a glow, embers, a smoke
column, a flickering light):

| Call | What |
|---|---|
| `Fire.Steady(parent, at, patch, scale, sparks, smoke)` | a fire that stays: a torch (scale 0.18), a hearth (0.32), a bonfire (1.1) |
| `Fire.Blaze(parent, box, spots, scale, from)` | a thing set alight: catching at the spot nearest `from` and spreading spot by spot |
| `Fire.Collapse(fire, seconds)` | a blaze falling in (sparks, big puffs, the flames going out highest first), then gone |
| `Fire.Douse(fire, seconds)` | any fire dying down |
| `Fire.Smoulder(parent, box, age, spots)` | what is left: flames dying over half a minute, smoke thinning to a wisp |
| `Fire.Burst(at, radius)` | a fire circle going off on the ground |
| `Fire.Splash(at, size)` | a bolt of fire bursting where it lands |
| `FireFx.Smoulder(parent, position, scale)` | a stump smouldering on burnt land (smoke, a spark now and then) |

Each goes under the parent it is given (the one-off ones under the current scene), so it leaves with its level.

**The kit's own fires** (`KitFires`): torches, braziers, hearths, fireplaces, fire pits and the bonfire are lit when
their level stands: flames at the piece's glowing flame mesh (its `M_VKI_GlowIn` surfaces), the mesh turned to coals
(or hidden: a brazier's and the bonfire's cones), and the nearest of the level's fire lights (`LIT_..._torch`,
`_brazier`, `_hearth`...) flickering, or a light of its own when there is none within 3 m. A game with its own
campfires sets `KitLevel.LightFires = false` and calls `KitFires.Light(piece, lights, notNear)` per piece, skipping
spots where its own fires burn.

**`FireFlicker`** wavers any light: add it as a child of a Light3D. `Level` scales it (a fire still catching),
`FadeOut(seconds)` dims it, `Tint` and `Depth` set how much it changes.

Godot notes: each part is a GPUParticles3D. Its rate is a share of its maximum over its lifetime
(`FireFx.Rate(part, perSecond)`); "already burning when first seen" is the part's preprocess (`FireFx.Warm`); a level
held out of the tree keeps its particles where they were. Light energy is Unity's intensity x `FireFx.LightScale` (0.5).
Sounds: the kit has none; set `Fire.SoundLoop` and `Fire.SoundAt` (section 10).

## 8. Missiles, the ground, walkways

- **`Missile.Fly(model, from, to, speed, spin, rotation, scale, arrived)`**: a copy of a prop (a scene, or a node
  duplicated) on a shallow arc, an arrow along its flight, a thrown blade spinning end over end (`spin`: turns a
  second); `arrived` is called when it lands (the hit is the thrower's to settle), and it lies there a moment.
  `FlyOrb` is gone the moment it lands; a child implementing `IMissileLanding` gets `Landed()` first (a spell's orb
  bursting). `Bend(side)` makes it weave.
- **`KitGround.Floor(point, ignore)`**: the floor under a point (the nearest surface from 1.2 m above to 1.8 m below,
  skipping colliders `ignore` rejects). **`KitGround.Scatter(at, spread, n, seed, ignore)`**: spots for n things round
  a point on the navmesh, apart from each other, each with a yaw (dropped loot).
- **`KitWalkways`**: walkable tops the navmesh bake leaves out (a warcamp's walkway decks have no collider). Set
  `KitWalkways.Names` to the deck pieces' names; each level then gives every matching mesh a body over its top (to
  click and stand on) and one navmesh region over all of them (`KitLevel` calls `KitWalkways.Ensure`).

## 9. Creature silhouettes

Live creatures hidden by a wall, a rock or a roof show where they are hidden as a flat translucent red, so they can be
seen and clicked. Call `CreatureSilhouettes.Tag(creature, true)` when a creature spawns and `Tag(creature, true, false)`
when it dies; tag the player with `Tag(player, false)` so a rat behind the player does not show through the player.
Tagged bodies are also kept whole by the see-through. Settings: `CreatureSilhouettes.Colour`, `Pull` (0.35 m: nearer
than this does not hide), `FeetPull` (0.6 on a level with grass: paws among the blades; 0 in caves).

Godot notes: Godot has no render pass over chosen objects, so each mesh gets a material overlay (`Shaders/
CreatureSilhouetteMark` with `CreatureSilhouetteFill` as its next pass: Godot 4.7's stencil and inverted depth
test). An overlay a creature already had is replaced.

## 10. Hooks a game fills

Static hooks the addon calls back through (set them early, e.g. in an autoload's `_Ready`):

| Hook | What it answers | Unset |
|---|---|---|
| `KitPointer.Blocked(screen)` | the pointer is on the game's UI (no zoom, no walking) | never blocked |
| `KitCamera.MapFrameOf(level)` | the level's `KitMapFrame`, for the border | no border |
| `KitCamera.Entered(outdoors)` | a level came in (start its ambience) | nothing |
| `Fire.SoundLoop(id, node, volume, pitch)` | a fire's loop on a node (`fire_loop`, `blaze_loop`) | silent |
| `Fire.SoundAt(id, point, volume, pitch)` | a one-shot (`fire_spray`, `spell_hit`, `earth`) | silent |
| `KitWalkways.Names()` | the deck pieces' names | no decks |
| `KitTravel.ScenePath(level)` | a level's scene | `res://kit/layouts/<level>.tscn` |

Switches: `KitLevel.SetUpSeeThrough`, `KitLevel.LightFires`, `KitTravel.Preload`, `KitSeeThroughCaps.FlushMs`.

`KitClickToMove`'s virtual members, for a game's rules on top (creatures to fight, closed ways that say why they do
not go, door sounds):

| Member | Default |
|---|---|
| `Under(hits, ray, camera)` | sets `HoverThing` or `Hover` (whichever is nearer along the ray) |
| `Press(hits, ray)` | uses the thing or takes the way under the cursor; false walks to the floor |
| `Take(link)` | `KitTravel.Go(link)` |
| `Offers(link)` | the link leads somewhere (`KitClickToMove.Leads`) |
| `PassesThrough(hit, ray)` | the see-through has opened it |
| `Halted` | false (true: no hover, no walking: dead, mid-swing) |
| `ReadsPointer`, `TakesClicks` | true |
| `Walking()`, `Went(link)`, `ClearHover()` | nothing / nothing / clears `Hover` and `HoverThing` |
| `Pointer(out screen, out press, out held)` | the mouse |

One Godot rule for C# code that walks the scene tree every frame: `FindChildren` and `GetChildren` hand back Godot
arrays, and one left to .NET's finalizer can be freed after the engine has shut down, crashing the game on quit. The
addon uses `KitNodes.Below(root, type)` and `KitNodes.Children(node)` instead, which leave none.

## 11. Checks from the command line

With the .NET build of Godot, after `dotnet build`, in the project folder:

```
godot --headless --path . --script res://addons/medieval_kit/Editor/kit_cli.gd -- <command>
```

| Command | What | Window |
|---|---|---|
| `check [piece ...]` | every imported piece against the kit's data (bounds, materials, colliders) | headless |
| `build <layout> ...` | the world graph and these levels, each with its navmesh and walk check | headless |
| `structures [name ...]` | the premade structures | headless |
| `bakecaps [layout ...]` | the see-through's caps of every built level (or these) | headless |
| `travel` | every link of every world level taken, with preloading | headless |
| `capture <layout> <out> [WxH] [asbuilt]` | the layout's Blender cameras rendered | a window |
| `seethrough <layout> <out>` | a stand-in behind each building: the hole, the caps, shots on and off | a window |
| `clickwalk <layout> <out>` | the walker: a floor click, the button held, a wall click, the doors and a round trip | a window |
| `systems <out>` | fires, a blaze, a missile, a silhouette, a usable thing, a walkway deck | a window |

The window ones need a display (drop `--headless`); each writes a log and shots to `<out>` and quits.

## 12. What the Godot addon does not have

- **The z-fight watch** (Unity's F8 tool that logs surfaces fighting in play) is not part of the Godot addon. The
  kit's pieces are checked for z-fighting in Blender, at the source.
- **The village builder** (Unity's `KitVillage`: outdoor maps from a layout, with loose nature and props, wall runs,
  a house's floor under the hole and its box) is not ported yet. Until it is, `KitSeeThrough.SetUpLevel` takes a
  level's structures as buildings, and `KitClickToMove` has no stand-in for a house whose door faces away from the
  camera (Unity's `hiddenDoor`).
- **Chain streaming** (Unity's `KitChainStreamer`: maps streamed as one world) is not ported yet; `KitTravel` moves
  between whole levels.
