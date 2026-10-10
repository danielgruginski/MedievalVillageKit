# Building levels with the Medieval Village Kit

A guide for whoever builds levels with this package, written so that an AI agent driving the Unity editor can follow
it step by step. It covers rooms typed as ASCII plans, the random generators (caves, dungeons, house floors,
connectors), chains of maps streamed into one continuous world, outdoor maps (villages) from layouts, and the checks
to run before calling a level done.
Everything here is runtime C# in `Runtime/Rooms/` plus editor tools in `Editor/`; nothing needs Blender.

Read sections 1 and 2 first. The rest is reference.

## 1. Ground rules

1. **Never replace, close or save over a scene someone has open.** Build in a new scene opened *additively* beside
   the open ones, make it active while you work, then restore the previously active scene and close or save yours
   (template in 2.3). Check `scene.isDirty` before touching an open scene. Use the camera of the scene you built,
   never `Camera.main` (with several scenes loaded it may be someone else's).
2. **The camera looks north.** The game camera has a fixed yaw looking north (+y in plan space, up on screen), pitch
   about 50 degrees. So:
   - south walls and partitions are *cut* (low), north walls *full*; tall props belong against north walls;
   - doors, exits and portals read best on the north–south axis (in east–west walls), **north best**: an
     opening in an east or west wall is seen edge-on and hides;
   - the south row of a map is the camera side.
3. **Openings are at least 2 cells wide** (1 cell = 1.5 m). The rock tiles' lobes close a one-cell gap, so a
   one-cell corridor or doorway in rock is not walkable. Agents (monsters, the player) must stay at or under
   about 0.35 m radius: kit doors leave 0.84 m, the rope bridge 0.88 m.
4. **Validate every change** with the walk tests (section 6) and report the numbers. A level is done when every
   spawn, encounter point and floor cell is reachable.
5. **Look at it.** Render the result (6.4) and judge it before saying it is good; the walk test cannot see a
   floating prop or an ugly seam.

## 2. Driving the kit from code

### 2.1 Assemblies

- `MedievalKit.Runtime` (namespace `MedievalKit`): `KitRoom`, the generators, `KitPortal`, `KitChain`,
  `KitChainStreamer`, `KitSpawn`, `KitLink`, `KitEncounter`, `KitPortalMarker`...
- `MedievalKit.Editor` (namespace `MedievalKit.Editor`): `KitRoomTools` (showcases, walk tests, validation, golden
  test), `KitChainTools` (chains, bake), `KitBuilder` (Build All: materials, prefabs, rules).

An editor script in your own assembly that references both can call everything directly. A sandboxed script runner
that does not reference them (such as an assistant's "run command" tool) can reach them by reflection:

```csharp
var asms  = System.AppDomain.CurrentDomain.GetAssemblies();
var tools = asms.Select(a => a.GetType("MedievalKit.Editor.KitRoomTools")).First(t => t != null);
var room  = asms.Select(a => a.GetType("MedievalKit.KitRoom")).First(t => t != null);
string report = (string)tools.GetMethod("ValidateGenerators").Invoke(null, new object[] { 20, "all", 1 });
```

Some sandboxes block `BindingFlags`, `System.Diagnostics` or `Regex`; everything below is reachable through public
members (`GetField(name)`, `GetMethod(name)` with default flags).

### 2.2 The rules asset

Every `KitRoom` needs the rules asset (plan tokens, styles, prefabs by name):

```csharp
var rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(KitRoomTools.RulesAsset);
// = "Packages/com.danielgruginski.medievalkit/Generated/KitInteriorRules.asset"; missing: Tools > Medieval Kit > Build All
```

### 2.3 Building in a scene of your own

```csharp
var active = SceneManager.GetActiveScene();
var scene  = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
EditorSceneManager.SaveScene(scene, "Assets/Levels/_work.unity");   // titled at once: Unity refuses to make another
                                                                     // new scene beside an untitled one with changes
SceneManager.SetActiveScene(scene);
try
{
    var go = new GameObject("Crypt level");
    var kr = go.AddComponent<KitRoom>();
    kr.rules = rules;
    kr.dungeon.theme = "Crypt"; kr.dungeon.seed = 42;
    kr.RandomDungeon();                       // fills kr.plan / kr.record and builds
    foreach (var n in kr.notes) Debug.Log(n); // problems the build found: read them
    EditorSceneManager.SaveScene(scene, "Assets/Levels/Crypt42.unity");
}
finally
{
    SceneManager.SetActiveScene(active);
    EditorSceneManager.CloseScene(scene, true);
}
```

`KitRoom` also works at runtime (it instantiates with `KitRoom.Spawn`; the editor keeps prefab links).

## 3. Space and the plan grid

- **Cells** are 1.5 m. A cell is `(c, r)`: `c` counts east from 0, `r` counts north from 0; row 0 is the south
  (camera) side. Nodes (cell corners) sit on multiples of 1.5 m; walls run along grid lines from node to node.
- **Plan space** is the Blender kit's: x east, y north, z up, metres, origin at the map's south-west node. The
  `KitRoom` transform's local space is `(-x, z, -y)`; a rotation `rot` about plan z is local `Euler(0, -rot, 0)`.
  So a cell's centre is local `(-(1.5c + 0.75), 0, -(1.5r + 0.75))`.
- **Bearings** (spawn facing, `KitSpawn.FromBearing`): 0 north, 90 east, 180 south, 270 west.
- **Maps are never turned.** Every generated map keeps north up; chains rely on it.

### 3.1 The plan text

```
      0  1  2  3  4
     +##+##+WW+##+##+          <- grid line j = 5 (the north wall): 2-char tokens between '+' nodes
   4 #BX BX CH PN PN#          <- row r = 4: [1-char wall token][2-char cell code] per cell, a last wall token
     +              +
   3 #.. .. .. .. ..#
     +              +
   2 Wbd .. HH .. ..#          <- 'W': a window in the west wall at row 2
     +              +
   1 #bd .. .. TB TB#
     +              +
   0 tWP .. Sf .. jat          <- 't': the rakes (side walls sloping down to the cut south wall)
     +==+==+ee+==+ww+          <- the south wall: cut ('=='), the exit ('ee'), a cut window ('ww')
```

The first line numbers the columns. Lines with `+` are grid lines: an east–west wall token (2 characters) per cell
along it. Other lines are cell rows, north first: a north–south wall token (1 character) before each cell and after
the last, and the cell's 2-character code. Blank tokens mean no wall.

East–west tokens (on `+` lines; upper case is full height, lower case cut):

| Token | Piece | | Token | Piece |
|---|---|---|---|---|
| `##` / `==` | plain wall, full / cut | | `WW` / `ww` | window |
| `dd` | door (cut) | | `ee` / `EE` | exit / wide exit (cut) |
| `OO` / `oo` | open gap | | `PP` | passage (a scene link) |
| `XX` / `xx` | breach | | `gg` | barred gate |
| `FF` | the special (fireplace, hearth, forge) | | `LL` `LT` `ll` | lancet windows |
| `NN` / `nn` | niche | | `||` | bars |
| `rr` | rail | | `S1`-`S4`, `s1` `s2` | named pieces |

North–south tokens (in cell rows): `#` / `:` plain full / cut, `W` / `w` window, `d` door, `O` / `o` gap,
`P` passage, `X` / `x` breach, `g` barred gate, `L` / `l` lancet, `N` / `n` niche, `|` bars, `r` rail, `t` rake,
`1`-`4` named.

### 3.2 Cell codes

- `..` empty floor.
- Furniture: two-letter codes (`TB` trestle table, `BX` box bed, `CH` chest, `PN` pantry shelves, `ba` barrel,
  `tb` small table...). The full list is `rules.Json["codes"]` (piece name -> code). A block of one code takes the
  largest piece of that code that fits, centred on the block; pieces at a wall turn their back to it.
- Lower-case codes of flat things (`br` bedroll, `st` straw, `gc` coins, `bo` bones, `rf` refuse, `rg` rug, `ts`
  tomb slab) are walked over.
- Cave maps (record `"cave": true`): `##` rock, `vv` chasm, `==` rope-bridge deck, `ss` stream, `ww` sewer channel,
  `ll` lava, `~~` pool (a pit piece), `Sx` a tunnel's mouth.
- `Ss` a stair's arrival cell. `@@` a cell held by a set-piece the record places (section 5.3).

## 4. The room record

A JSON object. Unknown keys are ignored.

| Key | Meaning |
|---|---|
| `building`, `floor` | labels (`floor`: 0 ground, negative underground) |
| `preset` | lighting and window styles: `Day`, `Night`, `Cavern`, `Dungeon` |
| `family` | `{"perimeter": F, "partition": F}`, F one of Timber, Stone, Board, Wattle, Ashlar, Dungeon, Ancient, Cave, Dwarf, Mine, Sewer, Bars |
| `zones` | `{name: {"cells": "rest" or [[c0, c1, r0, r1], ...], "floor": style, "wall": style}}`; the first zone listed wins where zones overlap |
| `links` | `[[id, kind, target, arrive]]`: scene links (`kind`: exit, passage, stair_up, stair_down, lift; `target`: a scene, `@return`, `@deep`; `arrive`, optional: the spawn id one lands on there, 5.8) |
| `stairs` | `[[kind, x, y, rot, link_id, variant]]`: `Up` / `Down`, the footprint's corner at its foot, plan metres; `rot` 0 / 90 / -90 (never 180); `variant` `RailR` (timber, the default), `Stone`, or `StoneL`. The wall runs along the stair's local x = 0 side, and its rail side (x = 1.5) must stay clear of walls; for a flight with its wall on its right going up, use the mirrored `StoneL` (else the lip lies in the wall's coping and z-fights with it) |
| `props` | `[[name, x, y, rot, style, mount, opts]]`: `mount` floor / wall_floor / wall_hung / table / edge; `opts` `{"on": true}` (stand on the table at x, y), `"hug"`, `"z"`, `"link"` |
| `props_from_codes` | `true`: the plan's codes furnish too (codes first, then the record's props) |
| `pits`, `sills`, `special`, `passages`, `door_leaves` | as in the kit's rooms (`rules.Room("VKI_...")` for examples) |
| `cave` | `true`: the plan is a cell map in rock (rock tiles, chasms, streams, channels) |
| `tunnels`, `tunnel_kinds` | cave maps: a tunnel tile and its link on a node, `{"i|j": link_id}` |
| `debris` | `{"density": 0..1, "seed": n}`: loose debris by zone theme |
| `encounters` | `[{id, room, creature, budget, boss, depth, box: [x0, y0, x1, y1], points: [[x, y]]}]` -> `KitEncounter` |
| `portals` | `[{id, side, at, width, target, seam}]`: openings into the next map of a chain (5.5) |
| `markers` | `[{id, role, at: [x, y], facing, note}]`: `KitMarker`s for the game (`vki_role` loot, npc...; a cave's finds write these) |
| `generated` | which generator and settings made it |

For a hand-made room, start from a kit room: `kr.LoadPreset("VKI_Hovel_F0")` copies its plan and record into the
component; edit them, then `kr.Generate()`.

## 5. Recipes

### 5.1 Random levels

Set the component's options, then call its `Random...()` method. Same settings and seed, same level.

| Call | Options (`kr.cave`, `kr.dungeon`, `kr.interior`, `kr.connector`) |
|---|---|
| `RandomCave()` | `layout` Maze (chambers, winding tunnels, loops, dead ends, alcove finds) / Open; `nc`, `nr` (28 x 20); `seed`; `chasm`, `chasmFork`, `chasmWidth`; `pools`; `props` (how many dressing pieces) and `dressing` (which: `"EggSacs:es,Cocoon:co"`, piece:code pairs placed in turn); `finds` (the alcoves' finds, same format; every find but an Overlay_ is marked as loot) and `extraFinds` (that many more along the walls); `debris`; `poi` (e.g. `POI_WyrmBones`); `creature` and `encounters` (5.4); `portals` |
| `RandomDungeon()` | `theme` Dungeon / Crypt / Warren (all goblins) / Hideout (all bandits: guard posts, stores of plunder and cells walled into rock, rough tunnels between); `rooms` (8); `pockets` (share of natural cave rooms); `loops`; `debris`; `seed`; `portals`; with portals, `exit` / `exitId` / `exitArrive`: a stair up out of the chain to a scene (a camp above), far from the way in (in the lair; a Hideout's in the deepest room but the lair, a room with no encounter: its front door, so who comes down it is not met by a boss appearing at the stair's foot). A Hideout marks its plunder for the game: the lair's treasure chest `strongbox`, a crate or barrel or two in each store room and a guard post's chest `plunder<n>` (record markers, role `loot`, the piece in the note) |
| `RandomInterior()` | `kind` Cottage / Townhouse / Tavern / Workshop; `seed`; `nc`, `nr` (0: by kind) |
| `RandomConnector()` | `from`, `to` (edges), `length`, `width`, `fromAt`, `toAt`, `style` Cave / Dungeon, `seed` |

What they make: caves with a chasm crossed by rope bridges, ledges, pools, crystals and finds; dungeons with a great
hall and themed rooms (guards, cells, crypt, store, shrine, warren, lair) with set-pieces, torches, pillars, an
encounter per room harder with depth (the lair holds the boss), a stair up and a stair down when the level stands
alone; house floors with a hall and hearth, side rooms, a tavern bar, kitchen, bedroom, lanterns.

### 5.2 A room from a plan

Write `kr.plan` (3.1) and `kr.record` (4), call `kr.Generate()`, then read `kr.notes`: every wall token it could not
place, prop without a prefab, post it could not fit is listed there. Walls on the outer frame are the perimeter
family; walls inside are partitions. Keep a free cell on both sides of every door.

**As a level of its own.** Keep the plan and record as files side by side, `<name>.plan.txt` and
`<name>.record.json`, and build them into a scene:

```csharp
string report = KitRoomTools.BuildRoomScene("Assets/World/Inn.plan.txt", "Assets/World/Inn.record.json", "Assets/World/Inn.unity");
// or select the .plan.txt and use Tools > Medieval Kit > Rooms > Build Room From Selected Plan
```

It builds additively in a scene of its own (refuses if that scene is open), lights it like a kit level (the record's
`Dungeon` / `Cavern` presets like VKI_Dungeon_B1, else VKI_Tavern_F0), adds a camera and walk-tests it; the report is
the walk test's line and then the build's notes. Starting from a kit room: copy `rules.Plan("VKI_Tavern_F0")` and
`rules.Room("VKI_Tavern_F0")` into the files and edit them (`Data/interior_rules.json` holds them all). Worked
examples, in the MedievalSetting project's `Assets/MedievalKitWorld`: `Hamlet_Inn` (the kit's tavern with a storeroom
and a stair down added), `Hamlet_Inn_F1`, and `Hamlet_Cellar` (a cave map: dressed vaults, a breach, a portal).

**A walled room inside rock** (a cellar, a crypt, a mine office) is a cave map (`"cave": true`) whose rooms are
floor cells with wall tokens on the grid lines between floor and rock, as the dungeon generator writes them: a rock
cell north of the floor gets `##` (or `==` where open floor lies one or two cells beyond it, so the rock tile behind
is low), rock to the south always `==`, rock to the east or west `#` (or `:`). Natural cave cells get no wall tokens.
`XX` on a room's wall opens a breach into the natural cave beyond. Family `{"perimeter": "Cave", "partition":
"Dungeon"}`, `"partition_wall": "zone"`.

### 5.3 Furniture

- **From codes** (quickest): write codes into the plan. `KitFurnisher` (generators) places them along walls or in
  the middle, a cell apart, and only where every walkable cell stays reachable from the ways in.
- **From the record**: `props` with mounts. `wall_floor` backs onto the wall behind it (the side its back faces:
  rot 0 north, 180 south, 90 west, -90 east) and slides off posts; `wall_hung` goes on a full wall's face; `table`
  props stand on the table placed at the same x, y.
- **Set-pieces** (`KitSetPieces`, for generator code): a bar (counters, cask racks behind, an end piece and the
  barkeep's way in), an altar or a hoard between statues and braziers, pillars on grid nodes (four cells keep
  walking room), wall-hung pieces, table dressing, a piece beside another (a chest by a bed). They hold their cells
  with `@@` and keep the room connected.
- `kr.CodesToRecord()` turns the plan's codes into record props, to edit by hand.

### 5.4 Encounters

`KitEncounter` components (under the room's `Logic`) carry `encounterId`, `roomType`, `creature` (bandit, rat,
undead, cultist, goblin, boss), `budget`, `depth`, `boss`, `size` and child `Spawn_n` points. The kit marks where and
how hard; spawning monsters and combat are the game's.

Who writes them: the dungeon generator (one per room, the creature by the room's theme; a Warren's all goblins), the
cave generator when its `creature` is set (`encounters` of them spread through the cave at least six steps from the
way in, the budget growing with the walk from it; a list, `"spider,centipede"`, runs from the way in to the deep end;
with a `poi`, the boss's lair there), outdoor maps (`encounters` in their layout, 5.7) and hand-made records
(`encounters` in 4). The walk tests check that every spawn point on the ground can be reached.

**Loot.** A cave's finds (`finds`, `extraFinds`) are each marked with a `KitMarker` (`vki_role` "loot", `vki_note` the
piece) for the game to make a container of. Finds and props may name the game's own prefabs: a name the kit does not
have is looked up among the project's prefabs (the editor searches `Assets/`; a game sets
`KitInteriorRules.External`). Example: MedievalSetting's dead goblins, `Goblin_Dead_1`..`4` (the Goblins pipeline's
Tools > Goblins > Bake Dead Goblins), in its rat cave.

### 5.5 Chains: one continuous world

Maps join through **connectors**: short passages built while one walks through them, so the next map is loaded when
one reaches it. Nothing fades; the floor runs on.

**Portals.** A map's way out is a `KitPortal` in its generator's `portals` list:

```csharp
kr.cave.portals = new List<KitPortal> { new KitPortal { id = "north", side = "N" } };   // at = -1: generator picks
kr.dungeon.portals = new List<KitPortal>
{
    new KitPortal { id = "south", side = "S" },              // the first portal is the way in (depth counts from it)
    new KitPortal { id = "east",  side = "E", at = 14 },     // at: the opening's first cell along its edge
};
```

The generator opens the edge there (`width` cells, 2 by default), runs a straight way in for 3 cells, then on to the
level's floor, and records the result in `R["portals"]`. `KitRoom` puts a `KitPortalMarker` (forward = out of the
map) on the middle of each opening and a `KitSpawn` named after the portal 2.25 m inside. A dungeon with portals has
no stairs; its first portal is the way in.

**Rules for portals.**
- Prefer north and south edges, north best (1.2). East and west work but read worse.
- Leave `KitPortal.Margin` (2) cells of edge either side of an opening: at the seam both maps agree those are cut rock.
- The two portals a connector joins must have the same width.
- A connector cannot turn back: the two portals it joins must not face the same way. It can go straight (out N,
  in S) or round a corner (out E, in S).
- Every portal leads somewhere: each is joined exactly once (an unjoined one would open the map's edge onto nothing,
  so Bake refuses).

**A chain asset.** Assets > Create > Medieval Kit > Chain, or in code:

```csharp
var chain = ScriptableObject.CreateInstance<KitChain>();
AssetDatabase.CreateAsset(chain, "Assets/Chains/Underworld.asset");
chain.maps = new List<KitChain.Map>
{
    new KitChain.Map { id = "caves", kind = KitChain.Kind.Cave, inPortal = "", outPortal = "north",
        cave = new KitCaveGenerator.Options { seed = 3, portals = { new KitPortal { id = "north", side = "N" } } } },
    new KitChain.Map { id = "crypt", kind = KitChain.Kind.Dungeon, inPortal = "south", outPortal = "north",
        dungeon = new KitDungeonGenerator.Options { seed = 7, theme = "Crypt",
            portals = { new KitPortal { id = "south", side = "S" }, new KitPortal { id = "north", side = "N" } } },
        connector = new KitConnectorGenerator.Options { length = 12, seed = 7 } },   // the passage from "caves"
    new KitChain.Map { id = "grotto", kind = KitChain.Kind.Cave, inPortal = "west",
        attachTo = "caves", attachPortal = "east",                                     // a branch off the first map
        cave = new KitCaveGenerator.Options { seed = 9, nc = 18, nr = 14,
            portals = { new KitPortal { id = "west", side = "W" } } } },
};
chain.maps[0].cave.portals.Add(new KitPortal { id = "east", side = "E" });         // "caves" needs that exit too
string report = KitChainTools.Bake(chain);
```

Each map after the first joins an earlier map: the one named in `attachTo` (empty: the map before it in the list)
through that map's `attachPortal` (empty: its `outPortal`). A connector runs from that portal to this map's `inPortal`
(its edges follow the two portals; `connector` sets its length, seed and style). So the maps form a tree: a map may
have several exits, each starting a branch; a branch never rejoins. **Bake** (also Tools >
Medieval Kit > Chains > Bake Selected Chain) builds every piece lined up in world space, refuses if pieces overlap
or a portal is missing, walk-tests the whole chain, saves each piece as a scene in a folder named after the asset,
fills `chain.pieces` (scene, position, footprint, neighbours), adds the scenes to the build settings and writes
`<chain>_Play.unity`: the sun of VKI_Dungeon_B4, a `KitChainStreamer`, a `KitShroud` (on a re-bake, with the
settings the old play scene's shroud was tuned to) and a test walker (WASD) to try it.

**Streaming.** `KitChainStreamer` (in the scene holding the player, the camera and the sun) loads the piece the
walker stands in and the pieces joined to it (`reach` 1; at a fork, every branch's connector), one scene at a time and additively, and unloads pieces two joins
away. Walking into a connector loads the map beyond it. The pieces bring their own lights; give the persistent scene
the sun and post-processing.

**Seams.** Where a connector meets a map, the map builds the rock tiles on the seam line and the connector leaves
them out; the cells beside the opening are cut rock in both. Two big maps never touch directly: always a connector
between them.

**Laying out branches.** Pieces must not overlap in the world. Branches heading the same way from nearby exits can
collide (Bake names the pieces that overlap): move an exit along its edge (`at`), lengthen a connector, or send a
branch off another edge. North and south exits keep a chain marching north; east and west ones fan it out.

**Current limits.** Branches never rejoin (no loops); connectors are level (no stairs between heights); the navmesh is not baked across pieces (a game needs one built over the loaded pieces at runtime, or
NavMeshLinks at the seams); there is no ruins generator yet (the Ancient wall family and breaches exist for
hand-made ruins).

Example: Tools > Medieval Kit > Chains > Create Sample Chain makes `Assets/MedievalKitChains/SampleChain.asset`
(maze cave -> dungeon -> open cave, one connector straight, one turning; a side cave branching off the first cave's
east exit) and bakes it.

**Hand-made maps in a chain.** A map of kind `Plan` is a plan and record you wrote (5.2), as files (`planFile`,
`recordFile`: TextAssets) or text (`plan`, `record`). It must be a cave map; its portals are the record's `portals`,
each with its `at` set (the opening's first cell along the edge), the opening's cells open floor for three cells in
from the edge (`KitPortal.Approach`) and the `Margin` (2) cells either side of it rock. Bake refuses a portal
without `at`.

```csharp
new KitChain.Map { id = "cellar", kind = KitChain.Kind.Plan, outPortal = "north",
    planFile = AssetDatabase.LoadAssetAtPath<TextAsset>("Assets/World/Cellar.plan.txt"),
    recordFile = AssetDatabase.LoadAssetAtPath<TextAsset>("Assets/World/Cellar.record.json") },
```

**Into a chain by a scene link.** A stair, door or passage elsewhere can lead into a chain: its target is the chain's
play scene (`<chain>_Play`), its `arrive` a spawn in one of the chain's pieces (a stair's spawn is named after its
link). `KitTravel` loads the play scene and hands the arrival to the `KitChainStreamer`, which loads that piece first
and puts the walker there (Bake records each piece's spawns in `chain.pieces[i].spawns`). The way back is an ordinary
link in that piece. Example: MedievalSetting's `Assets/MedievalKitWorld/HamletCellar.asset`: the inn's cellar
(hand-made) -> a rat cave (generated, rats, the Rat King's lair) -> a cave network, entered by the inn's stair down.

### 5.6 Showcases

Tools > Medieval Kit > Rooms > Build Room / Cave / Dungeon / Interior Showcase write scenes under
`Assets/MedievalKitRooms/` to look at the generators' range. In code, `KitRoomTools.BuildCaveShowcase(true)`
(likewise Dungeon, Interior) builds additively: the new scene is active when it returns; restore yours and close it.

### 5.7 Outdoor maps: villages, hamlets, farmsteads (`KitVillage`)

The outdoor counterpart of `KitRoom`: a layout (JSON, plan metres, x east, y north, origin at the map's south-west
corner) becomes a scene. Worked example: `Documentation~/examples/Hamlet_layout.json` (a hamlet in a forest clearing:
green, inn, chapel and graveyard, market, captain's post, cottages, gardens, farm, three road exits).

```csharp
string report = KitVillageTools.BuildVillage("Assets/World/Hamlet_layout.json", "Assets/World/Hamlet.unity");
// or select the layout and use Tools > Medieval Kit > World > Build Village From Selected Layout
```

It builds in a scene of its own (refuses if that scene is open), saves the ground's mesh, control map and material
next to the scene, copies VK_ValleyTown's sun, puts a camera at the start spawn, walk-tests the map and returns a
report: read every line. Overlaps, a building on a road or past the forest's wall, missing pieces are all listed.

Worked examples beside the hamlet in MedievalSetting's `Assets/MedievalKitWorld`: `Woods_layout.json` (a path through
glades: a woodcutter's camp, a wolf den up a side trail, a goblin lookout) and `Warcamp_layout.json` (a palisade ring
with a gate between two `Goblin_Watchtower`s standing astride the wall, walkways behind the south wall ending at the
towers, goblin tents round a `Goblin_Bonfire`, the `Goblin_ChiefTent`, cages, a cave mouth down into the tunnels).
Props take `scale` and a `swap` of materials by name (`{"M_VK_RoofRed": "M_VK_Thatch"}`); a layout-level `swap` is the
whole map's palette, its forest, undergrowth, scatter and single trees too (a burnt land: `{"M_VK_RockMossy": "M_VK_Rock",
"M_VK_BarkMossy": "M_VK_BarkOak"}`).

**What it makes.** The ground: a mesh with the kit's terrain material, a gentle relief rising into the forest, a level
pad under each building; roads, paved and trodden areas and doorsteps are painted into the material's control map
along curves (no tile grid anywhere). Buildings turned so their door faces the point you give; props, fences along
curves, gardens, single trees; the forest round the clearing (with undergrowth, straggler trees fraying its edge and
a margin of forest drawn beyond the map's edge so the view never ends in nothing); scatter (flowers, grass, rocks);
spawns, markers and exits. Colliders: building walls, a building's own dressing outside them (barrels, tables and
stools, troughs, hay, carts, its yard's fence, a lean-to, a bell tower; not its porch or gate) and props (`KitSolid.Box`:
boxes over what one bumps into, the faces below 1.2 m part by part -- a signpost's post, not its arms), fences, tree
trunks, the solid undergrowth and scatter (a round core for bushes, a box for rocks), and invisible walls. Trees and
stumps, in the forest, as scatter or as props, stand on their trunks only (`KitSolid.Trunk`: a capsule of 0.45 m, a
burnt tree 0.4; a stump 0.5, a burnt stump 0.32); the box an interior prop's export brings (the burnt trees' and
stump's, over the whole crown or root spread) is dropped at build, so the roots are walked over and the strips of
burnt wood stay open. The walls are
the outline of the walkable ground (the clearings up to `wallAt`, a little inside the forest, and a band along every
road) found on a one-metre grid and walled a cell thick, so road junctions and glades of any shape close; and the map's
border. Soft pieces stay walkable (plants, `Deco_` weeds and ivy, crops, flower boxes, chickens, ladders, overlays,
piers, decks, steps: `KitSolid.IsSoft`). The navmesh is baked from colliders, so a piece without one is walked through.

**Layout keys** (all optional but `size`):

| Key | Meaning |
|---|---|
| `name`, `seed`, `start` | the root's name, the random seed, the spawn the walk test starts from |
| `size`, `margin` | the map in metres (walkable, walled); forest drawn this far beyond it (24) |
| `relief`, `rim` | the ground's gentle relief (m), how much it rises into the forest (m) |
| `clearing` | `{centre, radius: [rx, ry], lumps}`: the lumpy oval the forest surrounds |
| `roads` | `[{id, width, surface: dirt / cobble, points: [[x, y], ...]}]`: smooth curves through the points; run them past the map's edge for exits |
| `areas` | `[{id, centre, radius, lumps, surface}]`: a green, a farmyard (lumpy ovals painted cobble or dirt) |
| `clearings` | instead of `clearing`: several lumpy ovals (glades along a path through woods); walls and forest follow their union |
| `buildings` | `[{id, structure: "Inn" or house: {cells, stories, seed, shape}, at, face: [x, y] or rot, door: {target, arrive, prompt}}]`: structures are the package's `Generated/Structures` (Inn, Chapel, GuardTower, Stable, Barn, Pigsty, Woodcutter, Smithy, Hovel_*, ...) or any kit piece (a cave mouth, `Entrance_CaveMouth` -- dry, for open ground -- or the valley's `Entrance_SpringCave` with its trickle: the piece itself is the door); houses come from the house generator |
| `gardens` | `[{id, at, rot, beds: [cols, rows], crops: [...], fence, gate: N/E/S/W, gatePiece}]`: crop beds (Crop_Cabbage, Carrot, Pumpkin, Lavender, Wheat) fenced |
| `props` | `[{piece, at, face or rot, collide}]`: any kit piece by name (`MarketStall_Tinker`, `Prop_Well`, `Grave_Cross`, `Animal_Horse`...) |
| `fences` | `[{piece, points, gate, gateAt: [fractions], gateDoor, gateDoorFlip, along: [{piece, at: [fractions], rot, collide}], closed, offset, flip, collide, smooth}]`: pieces laid along a curve (`Prop_Fence`, `Deco_Hedge`, `Palisade_Straight`, `Palisade_Walk`), each stretched to fit its run; a gate keeps its own width; `gateDoor` puts doors in each gate's frame at its transform (`Goblin_Gate` in a `Palisade_Gate`: closed and breakable, the way in until the game breaks it); `along` stands pieces on the line at fractions of it, turned as its pieces are (a `Palisade_Ladder` on a walkway's line leans on its deck); `closed` makes a ring (a palisade); `offset` shifts the line sideways (left of the way it runs: a walkway behind a wall) |
| `trees` | `[{piece, at, scale, rot}]`: single trees inside the village |
| `forest` | `{spacing, edge, wallAt, keepRoad, keepBuilt, stragglers, species: [[piece, weight]], undergrowth: [[piece, weight]], undergrowthSpacing}` |
| `scatter` | `[{pieces: [[piece, weight]], count, keep, spacing}]`: dressing in the clearing, off roads and buildings |
| `spawns` | `[{id, at, facing}]`: `KitSpawn`s (facing as a bearing: 0 north, 90 east) |
| `markers` | `[{id, role, at, facing, note}]`: `KitMarker`s for the game (`role`: npc, respawn...; read their `vki_role`, `vki_marker_id`) |
| `grass` | grass blades over the grass (on by default; `false` turns them off; `{spacing, height: [min, max], edge, shadows}`): a clump every 0.5 m, thinning on roads, paving and steep ground and at the forest's edge, clear of everything placed; drawn on the GPU (`KitGrass`: a compute shader culls the clumps per camera, the vertex shader builds the blades; they take the ground's grass colour, sway, part round the walker, cast small shadows) |
| `ground` | the terrain material: a material asset path (`Assets/.../M_BurntMarch_Terrain.mat`) or a kit material's name; default `M_VK_Terrain`. A copy of `M_VK_Terrain` with its own grass and dirt maps gives a map its own ground (a burnt land: scorched grass, ash); the grass blades take its grass map too |
| `encounters` | `[{id, creature, budget, boss, points: [[x, y, h]], note}]`: `KitEncounter`s; `h` lifts a point off the ground (archers on a walkway or a watchtower; the walk test leaves out points more than 0.5 m over the terrain) |
| `exits` | `[{id, road, end: start / end, target, arrive, prompt}]`: a `KitLink` where the road leaves the map, a spawn of the same id inside it |

**Rules of thumb.**
- Keep the camera in mind: tall buildings (chapel, inn) toward the north, low ones and open ground on the south;
  exits on the north and south edges.
- Give every building a `face` (usually a point on its road or the green): it turns the door toward it, and the
  door gets a doorstep and, with `door`, a link and a spawn.
- Stay inside the clearing: the report names buildings that reach past the forest's wall; widen the clearing or move
  them in. Leave 3-5 m between buildings and from roads.
- The kit's buildings are big (inn 17 x 10 m, chapel 18 x 9, barn 17 x 14; houses 3 m per cell): sketch at that scale.
- Organic comes from curves and turns: roads through 4-7 points, buildings at many angles, lumpy areas, stragglers;
  avoid placing things on a grid.

**Checking.** `KitVillageTools.WalkVillage(village)` (run by `BuildVillage`): from the start spawn, every spawn,
marker and encounter point on the ground reachable, and points in the forest beyond the wall not; "ok" first when all
is well, and any problem logged as an error. A marker shut in a cage (a piece named `*Cage*`) is a prisoner and not a
problem. `BuildVillage` repairs as it goes: an encounter point that is not reached (beside the wall, on an island: a
creature put there never comes) moves to the nearest spot within 3 m on the reached ground, half a metre clear of
everything, with a warning naming it ("ambush_rocks/Spawn_0 at (97, 73) not reached: moved 2.5 m to (95.1, 71.4)") -- move
the layout's point too, so the next build needs no repair. The bake then lists the navmesh's islands (below, 5.9).
Then render it (6.4) from above and at the game's angle.

**Breakables.** A piece whose metadata has `vki_breakable` (`KitPiece.Get("vki_breakable")`, e.g. `Goblin_Gate`) blocks
until the game breaks it; `vki_broken` names the piece to swap in at the same transform (`Goblin_Gate_Broken`). The
walk test counts breakables as broken (what lies behind them must be reachable), then rebuilds the navmesh with them
whole and lists what they shut off: "behind the breakables (...): 16 of 17 -- ...". A breakable that shuts nothing
off ("there is a way round") does not keep anyone out: close the gaps (a palisade ring, the forest's wall). The
warcamp's gate shuts off the whole camp from the road (its cave way in arrives inside, from the tunnels).

A building's `door` is `{target, arrive, prompt}`: the link takes the building's id, a spawn of that id stands 1.8 m
out from the door (where one comes back out), and `arrive` names the spawn inside the target (an interior's front
door spawn is `front`).

### 5.8 Linking levels (scene links)

A `KitLink` (doors, stairs, passages, tunnels, a village's exits) loads its `target` scene with `KitTravel.Go(link)`
and puts the walker on a spawn there:

1. the link's `arrive` (a record link's fourth element, a village door's `arrive`), else
2. the kit world's rule for the kit's own levels (the target's one link back), else
3. the spawn named like the link: both ends of a stair share its id, so `["cellar", "stair_down", "Cellar"]` in one
   room and `["cellar", "stair_up", "Inn"]` in the other need no `arrive`.

`@return` goes back the way one came: arriving on a door whose own target is `@return` (the kit's interiors) remembers
where one came from. `@deep` means no level yet (the link does nothing). Every target must be in the build settings.
Plan the joins as a graph before building: each link's id, target and arrival spawn, both ways. The hamlet's:
village `inn` door -> `Hamlet_Inn` / `front`; its `front` -> `Hamlet` / `inn`; `stairA` up and down between the inn's
floors; `cellar` down -> `HamletCellar_Play` / `cellar` (a chain, 5.5) and back up -> `Hamlet_Inn` / `cellar`; the
chapel door -> the kit's `VKI_Chapel_F0` / `front`, whose `@return` comes back to the door; the forest track `forest`
-> `Woods` / `south`, its `north` -> `Warcamp` / `south` and back; the camp's cave mouth `cave` -> `HamletCellar_Play` /
`camp` (the warren's stair, the chain's far end), whose stair `camp` -> `Warcamp` / `cave`.

A village's road exits are taken by walking into them (`KitLink.walkInto`); doors and stairs by using them.

**Instant cuts (`KitTravel.Preload = true`; a game turns it on).** The levels the current one links to are loaded
beside it in the background and held switched off (their roots inactive: unseen, no colliders, lights or navmesh); a
link to a held level is an instant cut (the level left is switched off, the target on and made the active scene, the
walker placed). The level left stays held while it is one link away (the hamlet holds the inn, the chapel and the
woods; inside the inn, the hamlet), else it is unloaded. A level not held yet, a chain's play scene (it streams its
own pieces) and the way out of a chain load the plain way behind a short fade (`KitTravel.FadeSeconds`). Keep the
level names unique: the held levels are found by name.

### 5.9 Navigation (NavMeshAgents)

Every level carries its walkable surface for the game's agents (a click-to-move player, monsters): `KitNavMesh`, a
root holding the NavMeshData baked from the level's colliders the way the walk tests see them (doors that open and
breakables passable, triggers ignored), added while the level is switched on. It is baked when an outdoor map
(`BuildVillage`, 0.1 m voxels), a room (`BuildRoomScene`, 0.05 m) or a chain (`KitChainTools.Bake`: one surface over
all the pieces, in the play scene, so paths run into pieces not streamed in yet) is built; scenes made before:
`KitNavBake.BakeScenes(paths)`, `KitNavBake.BakeChain(chain)`, or Tools > Medieval Kit > Navigation. The surface is for
the project's default agent type (id 0) with the kit's walker (radius 0.3, height 1.8, step 0.35): leave a
NavMeshAgent on its default type and give it radius 0.3. Breakables (`vki_breakable`) carve themselves out with a
NavMeshObstacle each until the game swaps the broken piece in. Put a walker on a spot with `KitTravel.Place` (it warps an
agent). The walk tests switch the carving off while they run.

An outdoor map's bake leaves out everything beyond its invisible walls: `KitVillage.Outside()` (the one-metre cells off
the walls' grid, the walls' own cells and the forest drawn round the map, as rectangles) goes in as Not Walkable volumes,
so the forest carries no navmesh for a spawn by the wall to snap to, or a wander or a click to land on (before, it was
bigger than the map's own: two thirds of the burnt march's). Interiors, caves and chains are baked as before. The bake
of an outdoor map also reports its islands (`KitVillageTools.Islands`): the pieces of navmesh apart from the one walked
from the start spawn, on the ground (inside buildings, a cage, the siege tower, a pocket among trunks) and on top of
things (rocks, roofs, walkways), with the largest; a spawn, marker or encounter point whose nearest navmesh within
1.5 m (where a creature is put down) is an island is a warning, unless it is meant to be there (an encounter point
lifted off the ground: archers on a walkway or a tower, a lookout; a marker in a cage).

**See-through.** The kit's shader (KitLit, every kit material) can open a hole round the game's walker: what stands
between the camera and the walker (in a cone to a disc round its chest, above its knees, and in front of it along the
camera's level heading -- not along the line of sight: the camera looks down, so a wall the walker stands before
reaches nearer the camera above the walker's head, yet stays whole) dithers away with a soft rim, shadows staying. Off until the game sets two globals each frame: `_KitSeeThrough` (xyz the walker's
chest, w the hole's radius at the walker; 0 off) and `_KitSeeThroughArgs` (x the walker's feet height, y the height
kept above the feet -- the ground, low and cut walls --, z how far in front of the walker, level, things are kept: an
eave over it, a post beside it). The depth passes
clip too (SSAO and depth priming see the same hole). MedievalSetting's `GameCamera` sets them (radius 2.4, keep 1.4).

## 6. Checking your work

### 6.1 Generators

`KitRoomTools.ValidateGenerators(count, which, firstSeed)` (`which`: cave, dungeon, connector, interior, all; menu
Rooms > Validate Generators) builds each seed in a temporary scene and walk-tests it. Report its lines, e.g.
`dungeon Crypt: 60/60 seeds walkable`. Any failing seed is listed with `(reached/spawns, floor reached/cells)`.

`KitChainTools.ValidateChains(count, firstSeed)` (menu Rooms > Validate Chains) does the same for the sample chain,
walking from the first map's spawn to every spawn of every piece across the seams.

### 6.2 One room

- `KitRoomTools.WalkTest(0.3f, 0.05f, room.transform)`: bakes a navmesh from that room's colliders (radius 0.3, 0.05 m
  voxels; openable doors left out), paths from its first spawn to every spawn, encounter point and floor cell.
  Results in `KitRoomTools.LastWalk`.
- `KitRoomTools.WalkMap(room)`: the plan as text marked by the navmesh, to see *where* it fails: `o` reachable,
  `x` navmesh but cut off, `.` no navmesh, `#` rock, `~` chasm, `=` bridge, `S` / `s` spawn reached / not, `*`
  furniture.
- `KitChainTools.WalkChain(rooms)`: the same across several pieces at once.
- `KitVillageTools.WalkVillage(village)`: an outdoor map (5.7); spawns and markers reached, the forest sealed.

### 6.3 The kit's own rooms

Rooms > Golden Test rebuilds the 19 Blender rooms and compares them with Blender's export
(`Logs/MedievalKit/room_test.txt`). Run it after changing shared code (`KitRoom*`, `KitRoomLayout`, `KitCaveLayout`):
structure must match; two rooms (Smithy, Townhouse_F1) differ by known 0.3 m prop slides.

### 6.4 Looking

Render with a camera you create in your own scene, pointed down for the layout or at the game's 50-degree pitch
looking north for the look:

```csharp
cam.orthographic = true; cam.transform.rotation = Quaternion.Euler(90f, 180f, 0f);   // top-down, north up
// or: cam.transform.rotation = Quaternion.Euler(55f, 180f, 0f); fieldOfView 40; back off along -forward
var rt = new RenderTexture(1400, 1000, 24); cam.targetTexture = rt; cam.Render();
RenderTexture.active = rt; tex.ReadPixels(new Rect(0, 0, 1400, 1000), 0, 0); /* EncodeToPNG, save */
```

Showcase scenes all sit at the world origin: if another one is open, move yours away before rendering or both show.
Set `cam.useOcclusionCulling = false` on a camera made for one render: a fresh camera can cull nearly everything
(the shadows still draw, the objects do not). Rendering a scene someone has open: make the camera with
`EditorUtility.CreateGameObjectWithHideFlags(name, HideFlags.HideAndDontSave, typeof(Camera))` so their scene
stays clean, and destroy it after.

## 7. Gotchas

- `new JArray(otherJArray)` copies its items instead of nesting it: build `var a = new JArray(); a.Add(inner);`.
- `KitRoom.Generate()` clears the component's children first: never parent anything you want to keep under it.
- A wall-mounted prop is slid back to the wall behind it, however far: give it the rotation of the wall it should
  back onto, or it crosses the room.
- Furniture in front of a doorway or in a one-cell corridor fails the walk test; the generators guard this, hand-made
  plans do not.
- Rock outside a cave map is assumed, and so is cut rock beside a portal's opening (5.5).
- Generated levels use `System.Random`: not the Blender kit's maps for the same seed.
- Kit materials expect no environment reflection (Lighting > Environment Reflections: Custom, intensity 0, as every
  kit level has). Build scenes with the kit's tools (they copy it) or set it yourself: Unity's default sky
  reflection washes leaves and painted wood blue-white.
- Chests and dressers share the shutters' "shutter" style slot. In Unity they are plain wood by default (the
  user's call; Blender paints them teal); a prop's style column (`{"shutter": "Red"}`: Teal, Red, Green, Blue, their
  Worn versions, Natural) paints one, a record's `window_style` restyles only the windows' shutters.
- Walk-test a room right after building it: a room loaded from a saved scene has no layout in memory, so the island
  check counts its stairs' own cells as unreachable floor.

## 8. Where things are

| File | What |
|---|---|
| `Runtime/Rooms/KitRoom.cs` (+ `.Props`, `.Debris`) | the component: build, furniture, debris, links, spawns, portals, lights |
| `Runtime/Rooms/KitRoomLayout.cs`, `KitCaveLayout.cs` | plan parsing, wall layout, cave tiles, seams |
| `Runtime/Rooms/KitCaveGenerator.cs` / `KitDungeonGenerator.cs` / `KitInteriorGenerator.cs` / `KitConnectorGenerator.cs` | the generators |
| `Runtime/Rooms/KitPortal.cs`, `KitSetPieces.cs`, `KitFurnisher.cs` | portals, set-pieces, furniture placement |
| `Runtime/KitChain.cs`, `KitChainStreamer.cs`, `KitPortalMarker.cs` | chains and streaming |
| `Runtime/World/KitVillage.cs`, `Editor/KitVillageEditor.cs` | outdoor maps from layouts: build, walk test |
| `Runtime/KitLink.cs`, `KitTravel.cs`, `KitSpawn.cs`, `KitEncounter.cs` | scene links (and the preloading for instant cuts), spawns, encounters |
| `Runtime/KitNavMesh.cs`, `Editor/KitNavBake.cs` | a level's baked navmesh for agents; the baking |
| `Shaders/KitLit.shader`, `KitSeeThrough.hlsl` | the kit's lit shader; the see-through round the walker |
| `Runtime/World/KitGrass.cs`, `KitVillage.Grass.cs`, `Shaders/KitGrass.shader`, `KitGrassInput.hlsl`, `Runtime/Resources/KitGrassCull.compute` | GPU grass: the clump list, the cull, the blades |
| `Editor/KitRoomEditor.cs` | `KitRoomTools`: a hand-made room as a scene (`BuildRoomScene`), showcases, walk tests, validation, golden test; the KitRoom inspector |
| `Editor/KitChainEditor.cs` | `KitChainTools`: bake, sample chain, chain validation |
