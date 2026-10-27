# Medieval Village Kit for Unity: manual

How the package's systems work and what a game has to do to use them. It is being written as each system lands
in the package (FULL_PORT_PLAN phase 8). For building levels (rooms from plans, the generators, chains, the walk
tests) see [LEVEL_BUILDING.md](LEVEL_BUILDING.md).

Contents:

1. [Walking a level in five minutes](#1-walking-a-level-in-five-minutes)
2. [The camera](#2-the-camera-kitcamera)
3. [The see-through](#3-the-see-through)
4. [Click to move](#4-click-to-move-kitclicktomove)
5. [Hooks a game fills](#5-hooks-a-game-fills)
6. To come: pieces and their data, levels and the world graph, fires, the map frame and the minimap, the shroud,
   the generators' recipes, the tests.

## 1. Walking a level in five minutes

1. Tools > Medieval Kit > Build All (materials, prefabs, levels): makes the level scenes and `KitWorld.asset`.
2. Tools > Medieval Kit > Navigation > Bake Active Scene (or Bake Selected Scenes) for the levels you want to walk.
3. Tools > Medieval Kit > Play From Start Level, or open a level and use Walk This Level.

Where the level has a navmesh at its first spawn you get **KitWalker**: a capsule that walks where you click (or
hold the left button), goes through a door you click, and is followed by the kit's camera with the see-through on.
Without a navmesh you get **KitTestWalker** (WASD, E to take a way out). Nothing is saved into the scene: both are
made in play mode. Look Around This Level plays with no walker: Tab steps through the level's cameras, F flies.

## 2. The camera (`KitCamera`)

The pieces are painted to be seen from one side: looking north (Unity -Z), 50 degrees down. `KitCamera` holds that
view and never turns.

- **Follow**: put it on a GameObject (it adds a Camera) and set `target` to the walker. It follows with a lag
  (`smooth`), on unscaled time (it keeps following while the game is paused), and cuts to the target when a level
  arrives through `KitTravel` (no glide across a door). `Snap()` makes the same cut on demand (after a teleport).
- **Zoom**: the mouse wheel moves `distance` between `near` and `far`.
- **Take-over**: when a level comes in, its own cameras and audio listeners are switched off (their post-processing
  setting is copied). The listener ("Ears") stands at the target's head, not 22 m up at the camera. The backdrop is
  the sky in a level built as a village (a `KitVillage` and a skybox) and black elsewhere (rooms, caves: the sky
  would show through gaps and through the see-through's hole).
- **Shadows**: URP's shadow distance is fitted to what the view reaches (about 39 m at the default zoom), and put
  back when the camera goes.
- **Border** (`keepInBorder`, off by default): the view stops short of the level's edge, using a `KitMapFrame`
  (a top-down picture of the level with its walk grid) from the `MapFrameOf` hook and `KitWalkWindow`.

Settings you may want to change: `pitch`, `distance`, `near` / `far`, `fov`, `smooth`. The see-through's settings
are in the next section.

## 3. The see-through

When the walker goes behind a house, a tree or a wall, what stands between the camera and the walker opens in a
round hole round its chest. Three parts work together:

1. **The shader** (every kit material, `Shaders/KitSeeThrough.hlsl`). It reads two global vectors:
   `_KitSeeThrough` = the hole's centre (the walker's chest, xyz) and radius (w; 0 = off), and
   `_KitSeeThroughArgs` = the walker's feet height, the height kept whole over them, a margin in front of the walker,
   and the half-width of the wedge from the camera to its body. Only surfaces in that wedge open (a wall beside the
   walker stays whole), and never below the kept height (the ground and the walls' feet stay).
2. **The level's marks** (`KitSeeThrough`, set by `KitVillage` when an outdoor level starts; nothing is saved in the
   scene). Rendering-layer bits on each renderer: *loose* pieces (trees, bushes, rocks, props) open down to the feet;
   a *building's* pieces open together (a house opens as one, decided each frame); walls laid as props (a town wall,
   a palisade) open in runs. Each piece is also *cut* at 1.4 m over its base, and a *cap* (the piece's own
   cross-section, filled) closes the stub so you never see inside a wall. The caps are baked (Tools > Medieval Kit >
   Bake See-through Caps, and before every player build); a piece changed since the bake gets its cap made in play.
3. **The driver** (`KitCamera`). Each frame it sets the two globals round its `target`. With
   `seeThroughWhenHidden` (on by default) it opens the hole only while kit pieces really hide the walker:
   `KitSeeThroughProbe` renders a small picture of the walker's upper body about every other frame and reads back
   how much of it is covered. The hole opens over `seeThroughOpenTime` once more than `seeThroughCoverOpen` (12%) is
   hidden, and shuts over `seeThroughShutTime` once under `seeThroughCoverShut` (4%) for `seeThroughHold` seconds,
   so it does not flicker at an edge.

**What a game must do:** use `KitCamera` (or a subclass of it) as its camera with `target` set. Without a driver the
globals stay zero and everything is drawn whole. A game with its own camera can drive the hole itself by setting the
two globals each frame (see `KitCamera.SeeThrough` for the values) and zeroing `_KitSeeThrough` when it stops.

Things a game carries (a weapon, a shield, a held prop) are drawn with kit materials too; mark them with
`KitSeeThrough.Keep(gameObject)` so they are never cut.

Pointer picking through the hole: `KitSeeThrough.Opened(hit, ray)` says whether a ray hit lies in what the hole has
opened, so a click can reach the floor behind a roof (`KitClickToMove` uses it).

Settings on `KitCamera`: `seeThroughRadius` (2.4 m), `keepBelow` (1.4 m, matches the caps' cut), `seeThroughBody`
(0.2 m; keep it under the navmesh agent's radius), `seeThroughNear` (0.25 m), and the hidden check's thresholds
and times above.

## 4. Click to move (`KitClickToMove`)

Diablo-style legs on Unity's navmesh (needs a `NavMeshAgent` on the walker and a baked navmesh).

- **Click** the ground to walk there; **hold** the left button to keep walking toward the cursor. The point walked
  to is the floor under the cursor the walker can reach: the ray looks past crates, stalls, roofs and what the
  see-through has opened to the floor behind; over a roof or a rock it walks up beside it. While held, the way round
  an obstacle is kept (no swinging between left and right of a crate).
- **Ways out** (`KitLink`: a door, a stair, a cave mouth): click to walk to it and take it (`KitTravel.Go`). A house
  whose door faces away from the camera (`hiddenDoor`, 72 degrees) stands for its door: the cursor on its walls or
  roof is on the door. A road's end at the map's edge (`walkInto`) is taken by walking on into it, once the walker has
  stepped clear of the one it arrived by.
- **Usable things** (`Interactable`, or a prop pointing at one with `UseVia`): click to walk up and `Use()` it.
- `Hover` (the way out under the cursor), `HoverThing`, `Using`, and the `Clicked` event (the point a click sent the
  walker to, for a ground marker) are there for a game's UI. `MoveTo(point)`, `Interact(link)` and
  `Interact(thing)` order it from code.

It registers its object as KitTravel's walker (tag Player, kept across scene loads) and turns KitTravel's preloading
on, so the levels one link away are held ready and a door is an instant cut.

## 5. Hooks a game fills

The package calls back into the game through static hooks (set them early, e.g. in a
`[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` method) and through subclasses.

| Hook | What it answers | Unset |
|---|---|---|
| `KitPointer.Blocked(screen)` | the pointer is on the game's UI (no zoom, no walking) | never blocked |
| `KitCamera.MapFrameOf(level)` | the level's `KitMapFrame`, for the border | no border |
| `KitCamera.Keeps(camera)` | a camera the take-over must leave on (a character preview) | all switched off |
| `KitCamera.Entered(outdoors)` | a level came in (start its ambience) | nothing |

`KitClickToMove`'s virtual members, for a game's rules on top (MedievalSetting's `ClickToMove` adds creatures to
fight, closed ways that say why they do not go, a travel map at a road's end, door sounds and a party):

| Member | Default |
|---|---|
| `Under(hits, ray, camera)` | sets `HoverThing` or `Hover` (whichever is nearer along the ray) |
| `Press(hits, ray)` | uses the thing or takes the way under the cursor; false walks to the floor |
| `Take(link)` | `KitTravel.Go(link)` |
| `Offers(link)` | the link leads somewhere (`KitClickToMove.Leads`: a target, not the open end `@deep`) |
| `PassesThrough(hit, ray)` | the see-through has opened it |
| `Halted` | false (true: no hover, no walking, e.g. dead or mid-swing) |
| `ReadsPointer`, `TakesClicks` | true |
| `Walking()`, `Went(link)`, `ClearHover()` | nothing / nothing / clears `Hover` and `HoverThing` |

A subclass keeps the base's serialized fields, so switching a component to it keeps its settings.
