# Medieval Village Kit for Godot: manual

How the addon's systems work and what a game has to do to use them (Godot 4.7, .NET / C#). The addon is the Godot side
of the kit's Unity package and offers the same systems; where Godot works differently, it says so. Everything is in
the `MedievalKit` namespace.

**How this was tested.** The Godot addon was written and tested by an AI coding assistant (Claude), directed by the
kit's author. Every system here has an automated check (section 13) that drives it in the kit's own levels the way a
player would (clicks, held buttons, doors, a stand-in behind buildings) and reads the results back from logs, pixels
and screenshots; those checks pass. **None of it has been played by a person in Godot yet.** The Unity systems it
ports were also played by a person, in the author's own Unity game (see the Unity package's manual), so the rules are
proven there; how they were carried over to Godot is checked only by the AI's tests. If something behaves oddly,
please say so.

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
10. [Rooms, generators, houses and chains](#10-rooms-generators-houses-and-chains)
11. [Outdoor maps (`KitVillage`)](#11-outdoor-maps-kitvillage)
12. [Hooks a game fills](#12-hooks-a-game-fills)
13. [Checks from the command line](#13-checks-from-the-command-line)
14. [What the Godot addon does not have](#14-what-the-godot-addon-does-not-have)

## 1. Getting started

What is where in the project:

| Path | What |
|---|---|
| `res://addons/medieval_kit/` | the addon: `Runtime/` (levels, travel, the see-through, fires...), `Walker/` (the camera, click to move, the walkers, the demo), `Shaders/` (KitLit and its variants, the terrain, the silhouettes), `FX/` (the fire's flipbooks), `Editor/` (import, build, tests) |
| `res://kit/models/` | the pieces (.glb), each imported as a `KitPiece` with its colliders |
| `res://kit/materials/`, `res://kit/textures/` | the shared materials (KitLit) and their textures |
| `res://kit/layouts/` | the built levels (`<name>.tscn`, each with its navmesh `<name>_nav.res`) |
| `res://kit/structures/` | the premade structures (a smithy, a brewery...: `KitStructure`) |
| `res://kit/examples/` | outdoor maps built from the addon's `Examples/*_layout.json` (section 11) |
| `res://kit/world.tres` | the world graph (`KitWorld`): which level links to which, and the start |
| `res://kit/see_through_caps.res` | the see-through's caps, baked (section 4) |

1. **Enable the plugin** (Project > Project Settings > Plugins > Medieval Kit; the kit's own project has it on).
   In a project of your own, the first time it adds the global shader uniforms (`kit_see_through`,
   `kit_see_through_args` and the shroud's four, `kit_shroud_...`) and raises the instance-uniform buffer to 1,048,576
   (every kit material has instance uniforms, and Godot gives each instance 16 slots). It asks for a restart:
   Project > Reload Current Project. Without these settings the kit's shaders do not compile. The plugin also holds
   the pieces' import script (`Editor/KitImport.cs`): keep it enabled.
2. **Build the C#** (the Build button, or `dotnet build` in the project folder).
3. **Play.** The project's main scene is the demo (`Walker/kit_demo.tscn`): pick a level and walk it with WASD (E at a
   door), Tab through Blender's camera views, F for a free camera. The outdoor maps of `res://kit/examples/` are at the
   end of its list.
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
   for a game's own levels; the kit's village builder calls them for its trees, props and wall runs (section 11).
3. **The caps**. Each building piece is cut 1.4 m over its building's floor, and a cap (the piece's own
   cross-section at the cut, filled) closes the stub, so you never see inside a wall (`KitSeeThroughCaps`). The cap
   meshes are **baked**: `kit_cli -- bakecaps` (section 13) writes `res://kit/see_through_caps.res`; bake again after
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
- **Houses round the back**: on an outdoor map, a house whose door faces away from the camera (within `HiddenDoor`,
  72 degrees, of the camera's heading) stands for its door: the cursor on its walls or roof is on the door, and a
  click walks round to it and goes in. A house with its door in view keeps the click (the floor behind it). 0 turns
  this off; 180 makes every house with a door answer.
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
Sounds: the kit has none; set `Fire.SoundLoop` and `Fire.SoundAt` (section 12).

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

## 10. Rooms, generators, houses and chains

The level-building side of the kit, ported line for line from the Unity package (its
`Documentation~/LEVEL_BUILDING.md` is the long guide; everything there holds here with the Godot names below). The
fields keep the Unity kit's names, so code written against one reads the same against the other:
`room.dungeon.seed = 42; room.RandomDungeon();`.

**Same seed, same level.** A generator given the same settings and seed builds the same level in both engines: the
plan, the record, every piece and its place, the spawns, links and encounters (checked on 1,000 generated plans and on
48 fully built levels against the Unity editor, and 20 houses; `tools/rooms_parity.py`). Two things make that hold,
for anyone changing the code: Unity's Mono and .NET differ in one LINQ case (`ToList` / `ToArray` straight after an
`OrderBy` of a single element skips its key in .NET; with a random key that shifts every draw after it), so the
generators list a random order with `ToListKeyed()`; and Unity's maths (`MedievalKit.UnityMath`: Mathf, Vector2) is
used as Unity computes it, aliased in the generator files. Records are JSON (`System.Text.Json.Nodes`); read a node
with `KitJson`'s `.F()`, `.I()`, `.S()`, `.B()` (and `.Fq()`... for missing values), never with a cast:
`(float)node` throws when the number was made in memory as a double.

**A room from a plan (`KitRoom`).** A `Node3D` (a tool script) that builds a room from an ASCII plan and a room
record: walls by family and height, posts, floors, exits with their doors, stairs, gates, passages, pits, furniture
from the plan's codes or the record's props, debris, encounters, markers, portals, the pieces' lights. Plan space is
the Blender kit's (x east, y north, z up, the plan's south-west corner at the origin; one cell 1.5 m, row 0 the
south / camera side); the node's local space is `(x, z, -y)`, a turn `rot` about Blender z a turn of `rot` about y.

```csharp
var room = new KitRoom { Name = "Crypt" };
AddChild(room);                         // in the tree (its pieces' links and lights go under it)
room.dungeon.theme = "Crypt"; room.dungeon.seed = 42;
room.RandomDungeon();                   // fills room.plan / room.record and builds
foreach (var n in room.notes) GD.Print(n);   // what the build could not place: read them
```

In the editor: add a KitRoom to a scene, set a generator's settings in the inspector (`cave`, `dungeon`, `sewer`,
`interior`, `connector`) and press Random Cave / Random Dungeon / ...; or type a preset's name (`VKI_Tavern_F0`) and
press Load Preset, edit `plan` and `record`, press Generate. The pieces are instanced scenes owned by the edited scene,
so save it like any other. `KitRoom.Spawn` makes each piece (a game may pool them).

| Generator | Call | Settings (resource) |
|---|---|---|
| Caves (maze or open, chasm with rope bridges, pools, crystals, finds, encounters) | `RandomCave()` | `KitCaveOptions` |
| Dungeons (Dungeon, Crypt, Warren, Hideout: themed rooms, set-pieces, an encounter per room, a lair) | `RandomDungeon()` | `KitDungeonOptions` |
| Town sewers (brick tunnels over channels, cisterns, grottoes, the ladder up, the way down) | `RandomSewer()` | `KitSewerOptions` |
| House floors (Cottage, Townhouse, Tavern, Workshop: hall, hearth, side rooms, a bar, books) | `RandomInterior()` | `KitInteriorOptions` |
| Connectors (a short passage between two maps of a chain) | `RandomConnector()` | `KitConnectorOptions` |

The rules (plan tokens, families, styles, the kit's own rooms as presets) are `KitInteriorRules.Default`, read from
`res://kit/data/interior_rules.json`; a copy pointed to by a `KitInteriorRules` resource on `rules` customises them.
A name the kit does not have (a game's own piece in a cave's finds, `Goblin_Dead_1`) is looked up through
`KitInteriorRules.External`.

**Houses (`KitHouseGenerator`).** A village house of kit pieces under the node: `cells` x 2 bays (or an L: `shape`,
`armCells`, `wingCells`), `stories`, `seed`, a random style or a given one (`ground`, `plaster`, `shutter`, `roof`),
the front and back bays (`"WDW"`), chimney, dormers, dressing. Generate / Reroll / Clear in the inspector; the rules
are `res://kit/data/house_rules.json` (`KitHouseRules`). `kit_cli houses` writes a set of random houses as scenes and
a showcase to `res://kit_houses/`.

**Chains: one continuous world.** A `KitChain` resource lists maps (`KitChainMap`: a generated cave or dungeon, or a
hand-made plan whose record has `portals` with their `at`); each map after the first joins an earlier one through a
connector between that map's portal and its own `inPortal`. `KitChainTools.Bake` (kit_cli `chains bake
<chain.tres>`) builds every piece lined up on its portals, refuses overlaps and portals that lead nowhere, walks the
whole chain on one navmesh, saves each piece as a scene in a folder named after the chain, fills the chain's
`pieces` and writes `<chain>_Play.tscn`: the dungeon light, a `KitChainStreamer`, one navmesh over every piece and a
WASD walker. The streamer keeps the walker's piece and its neighbours in the tree (loaded in the background, one at a
time) and frees what is two joins away. A link from elsewhere into the chain targets the play scene with an arrival
spawn's id: `KitTravel` hands it to the streamer, which loads that piece first and places the walker. A game's own
additions to the baked pieces go in `KitChain.AfterBake`, so a re-bake keeps them. `kit_cli chains sample` makes and
bakes the sample chain (a maze cave, a dungeon, an open cave, a side cave on a branch).

**The navmesh of a room** is baked like a level's (`KitNavMesh.Bake`): from the solid colliders, the kit's walker.
Godot's parser sees a box collider's faces, not its volume, so the floor inside a box taller than the walker (a
hearth's 2.2 m block) would stay walkable, an island sealed in the box; the bake adds every such box as an
obstruction too, as Unity's solid colliders are.

**Checks** (section 13): `rooms golden` rebuilds the kit's own Blender rooms and compares them with Blender's export
(17 of 19 the same; Smithy and Townhouse_F1 differ by the known 0.3 m prop slides, as in Unity); `rooms validate`
walk-tests seeds of every generator (every spawn, link and encounter point and every floor cell on the first spawn's
island); `chains validate` walks the sample chain end to end; `chains stream` runs a baked chain's play scene and
checks what the streamer holds in each piece; `shot` renders any scene top-down and from the game's camera, to look
at what was built.

## 11. Outdoor maps (`KitVillage`)

A village, hamlet, road, wood, camp or harbour from a layout: a JSON file of the map's size, seed, ground (relief,
rim, terrain tiers with cliffs and ramps, the sea and its quays), roads and paved areas, buildings (kit structures or
generated houses, `"house": {cells, stories, seed, shape}`), gardens, props, fences, trees, the forest round the
clearing, scatter, grass, and the game's things: spawns, links, markers, encounters, exits. The layout format is the
Unity kit's, unchanged: the Unity package's `Documentation~/LEVEL_BUILDING.md` section 5.7 describes every key, and a
layout written for one engine builds in the other. Two examples ship in `Examples/`: `Hamlet_layout.json` (a clearing
in a forest) and `HarbourTest_layout.json` (the sea, quays, moored boats, a lighthouse).

**Same rules, not the same numbers.** The Godot builder follows the Unity kit's rules (where the forest stands, how
the roads are painted, where the grass grows, what the walk test asks), and a layout gives the same map in its
plan: the buildings, roads, terrain, links and markers where the layout puts them. The random parts (which tree,
where a fern falls, the blades of grass) are not drawn in the same order as Unity's, so the two engines' forests and
scatter differ in detail.

**Building one.** From the command line (headless):

```
godot --headless --path . --script res://addons/medieval_kit/Editor/kit_cli.gd -- rooms village <layout.json> <scene.tscn>
```

builds the layout into a new scene (`KitVillageTools.BuildVillage`): a `KitLevel` root named after the map, a
`KitVillage` under it, the sun and sky of `VK_ValleyTown`, a camera at the arrival, the navmesh baked and the walk
test run. The ground's mesh, control map and materials are saved beside the scene in `<map>_Ground/`. In the editor:
add a `KitVillage` to a scene, paste the layout into `layout`, press **Build** (or **Clear**); then bake its navmesh
(`KitVillageTools.Bake`) like the command does. Read the report's notes: a building on a road, a prop that found no
piece, a building past the forest's wall.

What a build makes, under the `KitVillage`:

| Node | What |
|---|---|
| `Ground` | the ground mesh `Ground` (one mesh: its relief and the pads under buildings; a trimesh body `GroundBody`), `Terrain` (the tiers' cliffs, ramps and stairs merged into one mesh and body), `Sea` and its `SeaMask`, the `Grass` |
| `Buildings` | one node per building, named by its id; each has a `Box` body over its walls (4 m high), the building's only collider |
| `Props`, `Nature`, `Walls` | props and fences; trees, the forest and scatter; the invisible wall round the clearing (`WallBodies`), broken by the roads |
| `Logic` | links (`LNK_<id>`, a door's trigger with its arrival spawn), spawns, markers (`MRK_<role>_<id>`), encounters, exits |
| `KitNavMesh` | the baked navmesh (by `rooms village` or `KitVillageTools.Bake`) |

The ground's material is `KitTerrain` with this map's control map (roads, paving, dirt and sand painted in; row 0 of
the image is the map's north). `KitVillage.Spawn` makes each piece (a game may pool them).

**Grass (`KitGrass`).** Clumps of five to seven blades on a jittered grid, thinning where the ground turns to dirt or
paving, out at the forest's edge, on steep ground and under buildings, props and trees; taller in patches, darker in
the forest's shade. The layout's `"grass"` sets `spacing`, `height` [min, max], `edge`, `shadows` and `tip` (the
blades' tip colour: a burnt land's dull straw); `"grass": false` turns it off. The clumps are one byte array on the
`KitGrass` node, drawn in 16 m chunks (a MultiMesh each, made when the node enters the tree, not saved); each blade's
shape, sway in the wind and parting round the walker are worked out in the shader (`Shaders/KitGrass.gdshader`:
`wind`, `wind_strength`, `push_radius`, `push_strength`, `root_dark`, `translucency`). The blades take their colour
from the ground's grass (`grass_map`, `macro_map`, `grass_sat` copied from the ground material). Settings on the node:
`reach` (90 m: chunks further than this are not drawn), `castShadows`, `minHeight` / `maxHeight`. Godot: there is no
compute cull as in Unity; Godot's own culling drops whole chunks out of view or past `reach`.

**The sea.** Water quads over the sea's cells with `Materials/KitSea.tres` (`Shaders/KitSea.gdshader`: ripples, depth
colour from the depth buffer, refraction, foam along shores and quays, glints). A moored boat's hull is kept dry by a
`KitWaterMask` mesh at its waterline (`Materials/KitWaterMask.tres`): it writes the stencil, and the sea is not drawn
there. Quays, water stairs and the sea's bed come from the terrain's tiles.

**Navmesh and walk test.** `KitVillageTools.Bake` bakes on 0.1 m cells. It leaves out the forest beyond the
clearing's walls from floor to sky, and the ground under the raised terrain up to a metre (the tiers' tops and ramps
stay). It also leaves out the sea's bed and drowned shore up to just under the water (quays and water stairs stay) and
the crop beds. Islands under 2 m² are dropped for every navmesh the kit bakes, as Unity's are: the top of a sack pile,
a chest or a fire pit is not floor. The walk test (`KitVillageTools.WalkVillage`) checks that every spawn, marker
and encounter point on the ground is reached from the arrival. A marker in a cage is a prisoner, so it is skipped,
and so is an encounter point lifted off the ground (archers on a walkway). It also checks that probes just beyond the
forest's wall are not reached ("the forest leaks at ..."). Doors and breakables count as open; a second bake with
them shut lists what they close off.

**See-through.** A `KitLevel` holding a village sets its see-through up from the village
(`KitVillage.SetUpSeeThrough`). Each building opens as one: it is cut at its ground floor, and a plank floor is drawn in
the hole so the walker behind it is seen standing on something. Trees, bushes and loose props are cut on their own,
and wall and fence runs as runs. `KitSeeThrough.SetUpLevel` leaves a village's structures to it.

**The shroud (`KitShroud`).** For underground levels: the rock away from where the walker can go darkens with that
distance, black a few metres in, so the rock between passages fades into the dark. Put a `KitShroud` node in the
level's scene; a chain's play scene has one (`chains bake` keeps the one already there, as it was tuned). While it is
in the tree it reads the navmesh near the level's floor into a distance field, rebuilt on each arrival, and every
KitLit material darkens by it. Settings (live): `darkFrom` (0.2 m), `blackAt` (3 m), `topLight` (0.4, the light the
rock tops keep), `cell` (0.5 m), `floorBand` (1.6 m).

## 12. Hooks a game fills

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
| `KitRoom.Spawn(scene)`, `KitHouseGenerator.Spawn(scene)`, `KitVillage.Spawn(scene)` | makes a piece (pooling) | `Instantiate` |
| `KitInteriorRules.External(name)` | a piece the kit does not have (a game's own) | none |
| `KitChain.AfterBake(chain)` | the game's additions to a chain's baked pieces | nothing |

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

## 13. Checks from the command line

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
| `gfx <out>` | grass (heights, tints, shadows, parting round the walker), the sea and a boat's water mask, the shroud on and off | a window |
| `rooms golden [log]` | the kit's Blender rooms rebuilt by KitRoom against Blender's export | headless |
| `rooms validate [which] [count] [first seed]` | seeds of each generator (`cave`, `dungeon`, `sewer`, `connector`, `interior`, `all`) built and walk-tested | headless |
| `rooms dump <which> <count> <first seed> <out.jsonl>` | the generators' levels as JSON, to diff with the Unity kit's (`tools/rooms_parity.py`) | headless |
| `rooms village <layout.json> <scene.tscn>` | an outdoor map built from its layout, baked, walk-tested and saved | headless |
| `houses [count] [first seed]` | random houses as scenes and a showcase in `res://kit_houses/` | headless |
| `chains sample <chain.tres> [seed]`, `chains bake <chain.tres>` | the sample chain made and baked; a chain baked | headless |
| `chains validate [count] [first seed]`, `chains stream <play.tscn>` | the sample chain walked end to end; the streamer over a baked chain | headless |
| `shot <scene.tscn> <out prefix> [WxH] [node\|x,y [radius]]` | any scene rendered top-down and from the game's camera; with a node's name or a plan point, both views close round it (radius 15 m) | a window |

The window ones need a display (drop `--headless`); each writes a log and shots to `<out>` and quits.

## 14. What the Godot addon does not have

- **The z-fight watch** (Unity's F8 tool that logs surfaces fighting in play) is not part of the Godot addon. The
  kit's pieces are checked for z-fighting in Blender, at the source.
- **Outdoor-map generators** (whole villages, roads or woods generated from a seed) exist in neither engine: outdoor
  maps are built from layouts written by hand (or by a tool of your own).
- **The grass's compute cull** (Unity draws its grass through a compute shader that culls each clump): Godot culls the
  grass by 16 m chunks instead.
