Now let me look at the renders.

# Village Kit Expansion: New House Types, Village Buildings and Modular Pieces
*Written from the modular-kit-architect side: the aim is the fewest new meshes that unlock the most distinct buildings, all on the existing 3 m grid with clean seams.*

---

## 0. Summary

- The kit is already strong at walls, roofs and corners. Four limits hold it back, and every item below targets one of them:
  1. **Every roof must be 6 m deep with an overhanging gable.** Houses one bay long don't work (`build_house_v(n=1)` places only one gable), rowhouses can't share walls, and houses of different heights can't abut.
  2. **Only timber can go above the ground floor.** There is no stone upper storey, so there are no stone merchant houses, tower houses, warehouses or keeps.
  3. **No low-tier or frontier construction.** There are no wattle, log or plank walls and no raised foundations, so the colony has no early-game look.
  4. **No water, defence or construction-stage pieces.**
- I propose **14 piece families**: about **105 structural meshes plus about 40 prop meshes**. They unlock **12 new house types and 28 new village buildings or features**.
- **Phase A is about 33 meshes**: stone upper storey, parapet gables, T/X roof junctions, commerce modules, open bays and construction-stage flags. On its own it unlocks rowhouse terraces, gable-front townhouses, merchant houses, warehouses, market hall, guildhall, the cruciform church, and construction stages for every building, old and new.
- **No new texture sets are needed.** Everything reuses the existing material slots. Two style tints are added: plaster "Daub" and a "masonry" slot for the reworked stone.

| Family | Meshes | Effort | Buildings unlocked |
|---|---|---|---|
| F1 Stone upper storey | 7 | S | 9 |
| F2 Parapet / stepped gables | 3 | S–M | 8 |
| F3 Roof junctions T / X | 2 | S | 4 |
| F4 Commerce modules (shop, cart door, loft, hoist dormer) | 5 | M | 10 |
| F5 Open bays | 5 | S | 7 |
| F6 Low wattle + cruck + louver | 8 | M | 6 |
| F7 Log + plank sets | 10 | S–M | 9 |
| F8 Raised foundations + basement | 8 | S | 5 |
| F9 Round towers + battlements | 15 | M | 9 |
| F10 Palisade + curtain wall | 12 | M–L | 4 |
| F11 Water (dock, quay, bridges, wheel) | 14 | M | 6 |
| F12 Gallery, stairs, hatch, skylight, terrain connectors | 8 | S | 8 |
| F13 Construction stages | 10 | S | all |
| F14 Colony props (stockpiles, workstations) | ~40 | S each | 20 |

Effort scale: **S** is under about 100 lines or half a day, usually a flag or parameter on an existing generator. **M** is 0.5–2 days of new generator code. **L** is more than 2 days, usually intersecting or curved surfaces with many parts.

---

## 1. Kit contract (rules every new piece follows)

### 1.1 Constants
Existing: `CELL=3.0 H1=3.0 H2=2.8 HB=4.2 HC=4.5`, `RIDGE=roof_z(0)=4.19` above wall top. The eave tip is −0.31 below wall top and 1.35 m outside the wall line. Gable overhang is 0.95 (`GX−1.5`).

New:

| Const | Value | Meaning |
|---|---|---|
| `H0` | 2.2 | low wall (hovel, longhouse) |
| `RAISE` | 0.8 | staddle-stone floor height |
| `RAISE_P` | 1.2 | pile/stilt floor height |
| `ZW` | 5.8 (= H1+H2) | town-wall walk level; matches the 3rd-level floor of every building and tower |
| `TSTEP` | 1.5 (assumption: take it from the terrain track) | terrain height step; 2 steps = 1 storey |
| `WZ` | −TSTEP | water surface relative to bank ground; all water pieces have origin at bank ground on the cell edge |
| `BR_Z` | 0.6 | bridge deck top above bank ground |

### 1.2 Outer face planes (wall-local y) and matching gable face `XF`

| Wall family | H | Outer face y | Gable piece face `XF` |
|---|---|---|---|
| Stone (ground) | 3.0 | −0.25 (batter to −0.33) | `Roof_Gable_Stone` 1.5+0.30, **Parapet 1.5+0.25** |
| StoneU (new upper) | 2.8 | −0.25 | Parapet 1.5+0.25 |
| Plaster (ground) | 3.0 | −0.24 | (timber above) |
| Timber (upper) | 2.8 | −0.40 (jetty) | timber 1.5+0.40 |
| Wattle (new) | 2.2 | −0.20 | cruck 1.5+0.22 |
| Log (new) | 3.0 | −0.16 | planks 1.5+0.26 (0.10 proud, accepted) |
| Plank (new) | 3.0 | −0.20 | planks 1.5+0.26 |
| Barn | 4.2 | −0.20 | planks 1.5+0.26 |
| Open (new) | 3.0 / 4.2 | post face −0.25 | n/a |
| Chapel | 4.5 | −0.30 | stone 1.5+0.30 |

**Rule:** a Parapet may only sit above a stone storey (Stone or StoneU). Over a jettied timber storey its face would sit 0.15 m behind the wall below; use `Roof_Gable` there, unless the end is hidden, for example by a tower.

### 1.3 Seam and grid rules
- **R1 Pivots.** Wall modules: 3 m, centred on a cell edge, outer face −Y, pivot at the edge centre at the level's base z. Corners sit at vertices with outer faces −X/−Y. Inner corners have the empty quadrant at +X+Y. Roofs sit at the bay centre, ridge along X, z = wall top.
- **R2 Ownership.** Thin shared elements (posts, stud rows) follow the existing *left-edge* rule, and a corner or end piece closes the run. **Massive** shared elements (bridge piers, merlon/crenel pattern, parapet coping) are **split at the seam**: each module owns its half, so pieces never overlap coplanar.
- **R3 Pattern periods must divide 3.0.** Merlons 1.5, corbels 0.6, planks 0.3, logs 0.3. Randomness is seeded by course index or rounded local x, never by piece, so identical pieces tile.
- **R4 Seam-safe wobble.** See 2.1.
- **R5 Terrain skirt.** Anything touching ground extends below z=0: walls and plinths to −1.0; palisade logs to −1.2; piles and piers to the stated depth.
- **R6 Naming drives the assembler.** Use `SM_VK_Wall_{Family}[_Door|_Window|_Shop|_CartDoor|_Loft|_Mullion|_Byre]`, `SM_VK_Corner_{Family}` and `SM_VK_InnerCorner_{Family}`, so `_pieces()` and the new assembler resolve families by string.
- **R7 Materials are append-only.** Never reorder `kit_mats()`; every existing mesh's `material_index` depends on it. New pieces use existing slots. At most one optional flat slot `ORE` goes at index 45.
- **R8 Animated parts are separate meshes** with the pivot on the axis. Set `o["spin_axis"]` (wheel, sails) or `o["hinge_axis"]` (gate leaves), as `build_windmill` already does.
- **R9 Sockets and nav tags for Unity.** Child empties `SOCKET_Door` (forward = outward), `SOCKET_Smoke`, `SOCKET_Light`, `SOCKET_Work` (job spot), `SOCKET_Goods` and `SOCKET_Sign`. Each piece also gets `o["nav"]` = `block | walk | door`. Docks, bridges, galleries and wall-walks are `walk`. Walls are `block`.

---

## 2. Code changes before any new art (no new meshes)

**2.1 Seam-safe wobble** in `Kit.finish`. The current y-wobble envelope `sin(pi*clamp(z,0,6)/6)` is at its maximum (1.0) at z=3.0. The top edge of a ground wall therefore doesn't match the bottom edge of anything stacked flush on it. Timber hides this behind the jetty; stone-on-stone won't.
```
env = sin(pi*clamp(z,0,wh)/wh)            # wh = piece height (H0/H1/H2/HB), 0 at bottom and top
v.co.y += 0.035*sin(2*pi*x/CELL+0.9)*env
v.co.x += 0.02*sin(2*pi*z/2.3+0.4)*env    # x-wobble also enveloped, so corners close when stacked
```
Pass `wh` through each spec's kwargs. It changes nothing visible on the existing jettied houses.

**2.2 Height-parameterised wall generators.** Add an `H` argument to `wall_stone_plain`, `wall_stone_window`, `corner_stone`, `inner_corner_stone`, `plaster_ground` and `barn_wall`, plus `plinth=True/False` and a `base_h` argument (the stone sill height for barn walls, 0.7 today). Most new wall families below are then parameter calls.

**2.3 Family table and a generic footprint assembler.** This generalises `build_house_v`, `build_L_v` and `_assemble`:
```
FAM_H = {"Stone":H1,"Plaster":H1,"StoneU":H2,"Timber":H2,"Wattle":H0,"Log":H1,"Plank":H1,
         "Open":H1,"OpenTall":HB,"Barn":HB,"Chapel":HC,"Basement":TSTEP}
def plan_edges(cells):                         # cells = set of (i,j), 3 m grid
    walls=[]; corners=[]; inner=[]
    for (i,j) in cells:
        for di,dj,rot in ((0,-1,0),(1,0,90),(0,1,180),(-1,0,-90)):
            if (i+di,j+dj) not in cells:
                walls.append(((i+.5+di*.5)*CELL,(j+.5+dj*.5)*CELL,rot))
    for each grid vertex v: n = occupied cells among its 4
        n==1 -> corners.append((v, rot of the occupied quadrant: NE 0, NW 90... (as today))
        n==3 -> inner.append((v, rot = angle of the empty quadrant: NE 0, NW 90, SW 180, SE -90))
    return walls, corners, inner
def build(coll, origin, cells, levels, roof_plan, style, chars, found=None):
    z = {"staddle":RAISE,"piles":RAISE_P}.get(found,0.0)   # + place Found_* / Found_Deck
    for li,fam in enumerate(levels):           # fam may also be a fn(edge)->fam for mixed facades
        for (x,y,rot) in walls: place_v(coll, piece(fam, chars(li,x,y,rot)), x,y,z,rot,origin,style)
        corners / inner -> SM_VK_Corner_{fam} / SM_VK_InnerCorner_{fam}
        z += FAM_H[fam]
    place_roof(roof_plan, z); return recipe
```
Chars: `. W D` (existing), `A` arcade, **`S` shop, `C` cart door, `L` loft, `M` mullion, `B` byre, `V` basement vent**. A family missing a char falls back (`S`→`W`, `M`→`W`, `L`→`W`).

**2.4 Roof planner.** Wings are given explicitly as `(start cell, axis, length)`, as `build_L_v` does today. Each bay is classified by how many wing arms continue from it:

| Arms | Piece |
|---|---|
| end bay | `Roof_Gable[_Kind]` / `Roof_Hip` / **`Roof_Mid` + `Roof_Parapet[_Stepped]`** / thatch equivalents |
| 2 straight | `Roof_Mid` |
| 2 at 90° | `Roof_LCorner` (existing) |
| 3 | **`Roof_T`** (new) |
| 4 | **`Roof_X`** (new) |

Thatch gets no junction pieces; T and X roofs are tile only.

**2.5 Style additions.** Add `VARIANT_MATS["plaster"]["Daub"] = ("T_VK_Plaster",(0.82,0.66,0.48))`. Add a new kind `"masonry"` (`SLOT["masonry"]=STONE`, base `M_VK_Stone`) with variants Grey (default), Warm `(1.08,0.96,0.82)`, Dark `(0.72,0.76,0.82)` and Mossy (via `mossy_material`). These tints sit on top of whatever the stone rework produces. `random_style()` gets a `tier` key that picks families (see §4).

**2.6 Recipe export for Unity.** The assembler already produces a list of `(piece, pos, rot, style)`. Also dump it as JSON per building, together with `cells`, `levels`, sockets and `stage` tags. Unity then rebuilds prefabs, swaps recipes for **house-tier upgrades on the same footprint** and plays **construction stages** (F13) as recipe diffs.

---

## 3. New modular piece families

### F1 Stone upper storey, H2 = 2.8 (7 meshes, S)
| Piece | Key numbers | Built from |
|---|---|---|
| `SM_VK_Wall_StoneU` | 3.0×0.5×2.8, face −0.25. ASHLAR string course 3.0×0.34×0.20 at z 0–0.20, standing to −0.34 (hides the stacking seam). `wall_rocks` n=5 over z 0.4–2.6 | `stone_panel(-1.5,1.5,0,H2)` with no `plinth` or `batter` |
| `SM_VK_Wall_StoneU_Window` | opening x ±0.5, z 0.8–2.1, shutters, rock lintel 1.5×0.22×0.30 at z 2.5 | `wall_stone_window` with z shift |
| `SM_VK_Wall_StoneU_Mullion` | cross window x ±0.65, z 0.7–2.3. ASHLAR surround 0.16, mullion 0.12 at x=0, transom 0.12 at z=1.75. Hood mould 1.7×0.14×0.14 at z=2.45 with 0.25 drops. No shutters | boxes + WINDOW quad |
| `SM_VK_Wall_StoneU_Loft` | loading door x ±0.6, z 0–2.2, leaf open 100° outward. Hoist beam 0.22²×1.6 at z 2.55; pulley `ring` r 0.12; rope 1.4; optional hanging sack | shared `hoist(k,z)` helper (also used by F4) |
| `SM_VK_Wall_StoneU_Door` | door 1.0×2.1 with flat rock lintel (target of `Stair_Stone` / `Stair_Ext`) | simplified `wall_stone_door` |
| `SM_VK_Corner_StoneU` | quoins z 0.2–2.8 + L-return of the string course | `corner_stone(H=H2)` with no base rock |
| `SM_VK_InnerCorner_StoneU` | | `inner_corner_stone(H=H2)` |

Stacking: StoneU goes only on Stone or StoneU. Timber may go on StoneU; the jetty at −0.40 works exactly as it does over `Wall_Stone`.

### F2 Parapet gables and firewalls (3 meshes, S–M)
This one piece fixes three problems: single-bay houses, terraces, and houses of different heights abutting.

| Piece | Key numbers |
|---|---|
| `SM_VK_Roof_Parapet` | Placed at a bay seam or gable wall line, at wall top. Body x ∈ [−0.25, 0.25] (equals the end wall's thickness), y ∈ [−3.25, 3.25]. z from −0.4 (tucked into the wall) up to `roof_z(|y|)+0.35`. ASHLAR coping stones 0.62 wide × 0.16 thick, 7 per side (reuse the coping loop from `gable_special('stone')`). Apex block 0.6×0.6×0.5 + lathe ball finial. **Kneelers** at y = ±(3.25…4.45): 0.62-wide corbelled blocks with top `roof_z(ay)+0.35` and corbel bottom at z −0.9, closing the eave ends. Symmetric, so rotation 0 and 180 are identical. |
| `SM_VK_Roof_Parapet_Stepped` | Same body, crow-stepped top: 6 steps per side, each 0.54 wide horizontally, flat top at `roof_z(outer ay of step)+0.45`, ASHLAR cap. Pinnacle 0.8×0.8×0.9 at the ridge. |
| `SM_VK_Roof_Parapet_Chimney` | Parapet + party chimney stack 1.1(x)×0.9(y) centred on the seam, from RIDGE−0.8 to RIDGE+1.4, with 3 clay pots (reuse `chimney()` pots). Serves both neighbouring houses. |

Recipes:
- **Single-bay house:** `Roof_Mid` + `Roof_Parapet` at x=±1.5. The end wall faces at ±1.75 match the parapet faces.
- **Height step:** the taller lot gets its end-wall modules for the levels above the lower lot, plus a Parapet at its own top. The lower roof simply ends at the seam. Its ridge (top_low+4.19) always stays below the taller parapet (top_low+2.8+roof_z+0.35) for every |y| ≤ 3.25, so it is hidden.

### F3 Roof junctions (2 meshes, S)
Both derive from `roof_L_corner` in about 30 lines each.
- **`SM_VK_Roof_T`**: junction square x ∈ [−3, 3], y ∈ [−EAVE, 3]. Wing A runs through ±X and wing B leaves toward +Y. `z = zA(y)` for y ≤ 0, `max(zA(y), zB(|x|))` for y > 0 (valleys on both sides). No gable, no `merge_kit(gable_end)`. `eave_tabs` run along y = −EAVE for x ∈ [−3, 3]. Neighbours: `Roof_Mid` at x = ±4.5 (rot 0) and at y = 4.5 (rot 90).
- **`SM_VK_Roof_X`**: square [−3, 3]², `z = max(zA(|y|), zB(|x|))`, four valleys, no eaves. Triangulate each quad along its quadrant's valley diagonal: `(0,2)` split where x·y ≥ 0, `(1,3)` otherwise.
- Seam note: the valley past each inner corner, from (3,3) to (4.35,4.35), comes for free. The two neighbouring `Roof_Mid` eaves overlap there and their intersection is the valley, so no flap geometry is needed. The same holds for the existing LCorner.

### F4 Commerce modules (5 meshes, M)
| Piece | Key numbers |
|---|---|
| `SM_VK_Wall_Stone_Shop` / `SM_VK_Wall_Plaster_Shop` | Opening x ±1.1, z 0.85–2.25. **Stall-board counter**: plank 2.1×0.65×0.08 hinged at z 0.85, folded flat outward to y −0.9, on 2 iron brackets. **Canopy shutter**: 2.1×0.8 hinged at (y −0.28, z 2.30), angled 20° down, tip at y −1.03, z 2.03, with 2 iron prop rods. Interior: VOID quad at y +0.35, a shelf at z 1.55 with 5 clay jars/crates. `SOCKET_Goods` at (0, −0.6, 0.95); `SOCKET_Sign` at (1.2, −0.3, 2.9) for the existing `Sign_*`. Stone version: rock lintel 2.6×0.3×0.32 (as in `wall_stone_window`). Plaster version: posts at ±1.18 + head beam (as in `plaster_ground` "W"). Don't combine with the existing `Awning`. |
| `SM_VK_Wall_Stone_CartDoor` | Opening x ±1.2. Segmental arch: spring 2.0, crown 2.45, radius 1.825, centre z 0.625. Voussoir ring 0.35 thick, top at 2.8 (clear of the jetty belt beam at 3.0). Two PLANKS leaves 1.18×2.4, right leaf open 70° inward over VOID. Two guard stones (lathe cones r 0.22, h 0.55) at x ±1.35, y −0.35. Copy of `wall_stone_door`. |
| `SM_VK_Wall_Timber_Loft` | Timber upper module: door x ±0.6, z 0.3–2.3, leaf open against the wall. `hoist()` beam at z 2.55, projecting 1.6. |
| `SM_VK_Roof_Dormer_Hoist` | `dormer()` with door + open leaf replacing the window; hoist beam 1.2 out from the dormer apex. |

Stacking `CartDoor` → `Loft` → `Dormer_Hoist` in one bay gives the classic Hanseatic warehouse "hoist column".

### F5 Open bays (5 meshes, S)
| Piece | Key numbers |
|---|---|
| `SM_VK_Wall_Open` | Post 0.30×0.30 at x −1.5 (face −0.25) on a ROCK pad 0.55×0.55×0.30. Head beam 3.0×0.36×0.34, top exactly at H1 (the timber upper sits on it). Two knee braces from post z H1−1.0 to beam x −0.7. |
| `SM_VK_Corner_Open` / `SM_VK_InnerCorner_Open` | Post 0.34 + braces in both directions |
| `SM_VK_Wall_OpenTall` / `SM_VK_Corner_OpenTall` | Same at HB = 4.2, plus mid rail at 2.4. Barn roofs sit on it. |

### F6 Low wattle-and-daub set + cruck gable + louver (8 meshes, M)
| Piece | Key numbers |
|---|---|
| `SM_VK_Wall_Wattle` | ROCK footing 0.35 high (`plinth` scaled). Sill beam 3.0×0.26×0.18 at z 0.44. Crooked round posts (`_cyl` r 0.11, ±3° lean) at x −1.5 and 0. Top plate at H0−0.1. Daub infill (PLASTER, "Daub" tint) y −0.20…0.12. Two "daub-loss" recesses 0.5×0.4 showing woven wattle (4 stakes r 0.02 + 5 sine-weaving tubes r 0.025). |
| `_Window` | Unglazed 0.6×0.5 at z 1.0–1.5, top-hinged plank shutter propped open, VOID behind |
| `_Door` | 0.9×1.75 ledged-and-braced plank door |
| `_Byre` | 2.0×1.9 opening, 2 half-leaves (one open), HAY on the threshold |
| `SM_VK_Corner_Wattle`, `SM_VK_InnerCorner_Wattle` | Post r 0.14 + footing rocks |
| `SM_VK_RoofThatch_Gable_Cruck` | `roof_thatch_gable_kind("cruck")`: `gable_end` with XF 1.5+0.22, TRI = PLASTER. **Two cruck blades**, each a cubic Bézier through (|y|, z) = (2.75, −H0), (3.05, 0.4), (1.6, RIDGE−1.2), (0.1, RIDGE−0.35): 8 box segments of 0.26×0.20 at x = XF+0.08, plus a collar at 0.55·RIDGE and a tie beam at z 0. Blades reach the ground, so this piece is only valid on H0 walls. |
| `SM_VK_Roof_Louver` | Ridge smoke louver: body 0.8×0.9×0.75 at base RIDGE−0.3, 3 tilted slats per long side over VOID, 2 PLANKS roof boards 1.2×0.75 at 45°, finial. `SOCKET_Smoke` at RIDGE+1.0. Fits tile and thatch Mid bays. |

Geometry note: at H0 the eave lip underside is at about 1.4 m, so **doors go on gable ends only**.

### F7 Log and plank sets, H1 (10 meshes, S–M)
- **`SM_VK_Wall_Log`**: 10 courses, log r 0.16, centres z = 0.16 + 0.3·i (top 3.02), spanning exactly x ±1.5, face −0.16. Radius jitter ±0.015 seeded by course only (seam-safe). Cream chinking strips 3.0×0.12×0.08. ROCK footing.
- **`_Window`**: x ±0.55, z 1.0–2.0, via `window_frame(face=-0.16)`.
- **`_Door`**: x ±0.55, z 0–2.1.
- **`SM_VK_Corner_Log`**: per course, an X stub (x −0.45…0.05) and a Y stub (y −0.45…0.05), with ENDGRAIN caps. This reads as a saddle notch.
- **`SM_VK_InnerCorner_Log`**
- **`SM_VK_Wall_Plank`, `_Door`, `_Window`, `SM_VK_Corner_Plank`, `SM_VK_InnerCorner_Plank`**: `barn_wall(k, kind, H=H1, base_h=0.35)`. Board-and-batten at face −0.20.
- Gables: the existing `Roof_Gable_Planks` and `RoofThatch_Gable_Planks` (0 new roof meshes). Optional `gable_end(kind='log')` with shortened log courses: 2 more meshes.

### F8 Raised foundations and basement (8 meshes, S)
| Piece | Key numbers |
|---|---|
| `SM_VK_Found_Staddle` | Staddle stones at x −1.5 and 0. Lathe ROCK stem r 0.20→0.14 over z 0–0.5, cap disc r 0.45 over z 0.5–0.62. Sill beam 3.0×0.30×0.20, top at RAISE = 0.8. Walls go on at z 0.8. |
| `SM_VK_Found_Staddle_Corner` | Staddle at the vertex + sill stubs |
| `SM_VK_Found_Piles` / `_Corner` | Timber piles r 0.15 from z −3.0 to RAISE_P = 1.2, X-braces between piles in the edge plane, MOSS band at the water line |
| `SM_VK_Found_Deck` | One per footprint cell: PLANKS 3×3×0.08 with top at the raise height, 3 joists, centre staddle/pile, dark underside |
| `SM_VK_Found_Steps` | 1.2 wide, 4 steps (0.8) or 6 steps (1.2) |
| `SM_VK_Wall_Stone_Basement` (+ `_Vent`) / `SM_VK_Corner_Stone_Basement` | H = TSTEP. Stone with 1–2 barred vents 0.6×0.35. Used on slopes (see H12). |

### F9 Round towers and battlements (15 meshes, M)
Towers reuse the `windmill()` technique: a lathe or cylinder body with window and door frames overlaid on the surface, no boolean cuts. UVs are cylindrical: U = angle·R / TILE, V = z / TILE.

**Small tower, R = 2.0 (Ø 4.0), 24 segments.** R = 2.0 is chosen so both a house's gable corner (1.65 m from the vertex) and its hip corner (1.91 m) disappear inside the tower.
- **`SM_VK_TowerS_Base`**: H1 tall, plinth ring R+0.25 × 0.45, about 20 tangential `rock()` blocks, one slit window 0.15×0.9.
- **`_Base_Door`**: adds a door 0.9×2.0 with stone jambs.
- **`SM_VK_TowerS_Mid`**: H2 tall, ASHLAR string ring R+0.08 × 0.18, two windows 0.6×1.0 at −60° and +120°.
- **`SM_VK_TowerS_Mid_Dovecote`**: band of 40 pigeon holes 0.15×0.12 (VOID) with ledges.
- **`SM_VK_TowerS_Cone`**: bell-cast lathe in ROOF, so roof style variants apply. Profile (r, z) = (2.6, −0.15), (2.25, 0.1), (1.9, 0.6), (1.2, 1.75), (0.55, 3.0), (0.06, 4.4): about 35° at the kick, 71° at the tip. WOOD soffit and finial, reusing the cupola's weathervane.

Placement:
- **Outer corner:** the tower centre replaces the `Corner_*` pieces at every level. The tower must rise **2 × H2 above the wall top** so the cone eave clears the main roof: at the cone's innermost point the roof is +3.6 m, and the cone eave sits at +5.45.
- **Inner corner (stair tower):** centre at the concave vertex, replacing the `InnerCorner_*` pieces.

**`SM_VK_Bartizan`** (corbelled turret):
- R 0.95. Corbel lathe (0.2, −1.4) → (0.5, −1.1) → (0.55, −1.0) → (0.75, −0.7) → (0.8, −0.6) → (0.95, −0.3) in ASHLAR.
- Body z −0.3 to 3.3 with 3 slits; cone is the TowerS profile × 0.475.
- Origin at the building's outer vertex, body centre at (−0.35, −0.35).
- Origin z = top − 1.5 when a crenel parapet is present, otherwise the base of the top storey. Don't combine it with overhanging hip eaves.

**Large tower, R = 2.9, 32 segments (wall and gate towers)**, centred on a vertex of the wall line:
- `SM_VK_TowerL_Base`: H1, batter flare R+0.4 at z 0 tapering to R at 1.5, door.
- `SM_VK_TowerL_Mid`: H2, 3 arrow slits.
- `SM_VK_TowerL_WalkDoor`: H2, two 1.0×2.2 doors facing ±X. Stacked as Base + Mid + WalkDoor, the doors sit at world z = ZW = 5.8.
- `SM_VK_TowerL_Crenel`: flat top, 12 merlons 0.9 wide.
- `SM_VK_TowerL_Cone`: TowerS profile × 1.45.
- Cheap alternative: the existing `SM_VK_GuardTower`, after changing its `h1` from 6.0 to 5.8 so its hoarding floor meets ZW.

**Battlements for any 0.5 m stone wall:**
- **`SM_VK_Parapet_Crenel`**: 3 m. Corbel table of 5 corbels at x = −1.2, −0.6, 0, 0.6, 1.2 (period 0.6). Breastwork y −0.45…0.0, z 0–0.9. Merlons 0.9 wide centred at x ±0.75, z 0.9–1.7; crenels 0.6 wide (period 1.5, and the crenel at the seam is split 0.3 + 0.3). ASHLAR coping; WOOD rain spout at x = 0.
- `SM_VK_Parapet_Crenel_Corner`: L-shaped corner merlon 1.2×1.2.
- `SM_VK_Roof_Flat` (+ `_Hatch`): one per cell, 3×3 ROCK-flag deck 0.08 thick, 1% drain slope.
- `SM_VK_Roof_Pyramid_Inset`: for 2×2 tops inside a parapet. Base 5.5×5.5, 52° pitch, height 3.5, 4-segment cone (the `guard_tower` method), finial.

### F10 Fortification (12 meshes, M–L)
**Palisade (early-game defence):**
- `SM_VK_Palisade`: 3 m. 10 logs at x = −1.35 + 0.3·i, r 0.14–0.17, top 3.3–3.8, bottom −1.2. BARK_PINE body with a sharpened WOOD cone tip 0.45. Inner rails 3.0×0.14×0.2 at y +0.22, z 1.0 and 2.7, with BURLAP lashings. SOIL berm wedge on the outer side, 1.0 deep × 0.4 high.
- `SM_VK_Palisade_Corner`: 3 logs r 0.2.
- `SM_VK_Palisade_Walk`: inner fighting deck, PLANKS 3.0×1.2, top at 2.1, posts at x −1.5, y 0.35 and 1.4 down to −0.8, with braces. The palisade itself is the breastwork: 1.2–1.7 above the deck.
- `SM_VK_Palisade_Gate`: 6 m (x ±3). Posts r 0.26 × 5.0 at x ±2.25, clear opening 4.2. Lintel walk PLANKS at z 4.0, 1.4 deep, with log breastwork 1.1. Two logs of fill at each side.
- `SM_VK_Palisade_GateLeaf`: separate mesh, 2.1×3.2, logs r 0.13 + 3 battens + diagonal brace; pivot on the hinge.
- `SM_VK_Palisade_Tower`: 3×3 m. Posts r 0.2 at (±1.35, ±1.35) up to 6.2, X-bracing in the lower 4 m, platform at 4.2 with log breastwork 1.2, 4-segment pyramid roof in ROOF, ladder.

**Stone curtain wall (late-game defence):**
- `SM_VK_Curtain`: 3 m. Thickness 1.5 (y ±0.75), body from z −1.0 to ZW = 5.8. Talus wedge standing 0.3 outward over z −1.0…1.2. Wall-walk ASHLAR flags y −0.3…0.75 at ZW. Outer breastwork y −0.75…−0.3, z ZW…ZW+0.9. Merlons 0.9 wide centred at x ±0.75, up to ZW+1.7, each with an arrow slit 0.1×0.55. VOID putlog holes on the inner face.
- `SM_VK_Curtain_Corner` / `_InnerCorner`: 1.5×1.5 corner with a corner merlon.
- `SM_VK_Curtain_Stair`: 6 m add-on on the inner face (y 0.75…1.85). 20 steps, rise 0.29, tread 0.29, solid masonry below. A 9 m / 30-step variant (rise 0.193) is available if pathing needs ≤ 35°.
- `SM_VK_Curtain_Gate`: 6 m. Round arch x ±1.8, spring 2.6, crown 4.4. ASHLAR voussoirs 0.45 thick. `arch_soffit` through the full 1.5 m depth. Raised IRON portcullis whose spikes show at z 3.8–4.4. Machicolation corbels over the arch; merlon pattern continues on top.
- `SM_VK_Curtain_GateLeaf`: animated, hinge pivot.
- `SM_VK_Gate_Hoarding`: roofed timber gallery 6.0×2.4 over the gate walk, lean roof in ROOF (reuse the `guard_tower` hoarding loop).

### F11 Water set (14 meshes, M)
All water pieces have origin at **bank ground on the cell edge**, with the water surface at WZ = −1.5.

| Piece | Key numbers |
|---|---|
| `SM_VK_Dock_Deck` | Cell 3×3, deck top at WZ+0.7 = −0.8. PLANKS along X, 3.0×0.28×0.06, 10 per cell. Stringers along Y at x −1.3, 0, 1.3. Piles r 0.15 at (±1.3, ±1.3) from −4.5 to the deck, MOSS band WZ−0.15…WZ+0.2, X-braces. Every cell has its own 4 piles, so any L/T/grid shape tiles; doubled piles at seams read as bents. |
| `SM_VK_Dock_Rail` | Edge piece: posts at x −1.5, 1.0 tall, BURLAP rope catenary |
| `SM_VK_Dock_End` | 2 lathe bollards r 0.18, ladder down to WZ−1.0, lamppost (`prop_lamppost`) |
| `SM_VK_Dock_Ramp` | Planks rising from deck (−0.8) to bank (0.0) over 3 m |
| `SM_VK_Quay_Wall` | Stone embankment: face at −0.25 (water side), z WZ−2.0 to 0, ASHLAR coping 0.6×0.15, iron mooring ring at WZ+1.0, algae band |
| `SM_VK_Quay_Corner` / `SM_VK_Quay_Stair` | Stair: 6 steps cut along the face, down to WZ |
| `SM_VK_Bridge_Wood_Span` | 3 m along X (road axis). Deck 4.0 wide, top BR_Z = 0.6. PLANKS across Y, 10 per span. Stringers 0.25×0.35 at y −1.4, 0, 1.4. **Bent** at x −1.5: posts r 0.15 at y −1.6, 0, 1.6 from −4.5 to 0.2, cap beam, X-braces. Rails: posts at x −1.5 and 0, top rail +1.05, mid rail +0.55. |
| `SM_VK_Bridge_Wood_End` | Final bent + end rail posts (left-edge rule) |
| `SM_VK_Bridge_Wood_Ramp` | 0 → 0.6 over 3 m on sleeper stones |
| `SM_VK_Bridge_Stone_Span` | 3 m along X, deck 4.2 wide (clear 3.5). **Half-piers** x ∈ [−1.5, −1.1] and [1.1, 1.5] (seam-split, R2). Semicircular arch r 1.1, spring −1.3, intrados crown −0.2 (1.3 above water). Voussoir ring 0.4 (`arch_ring`), `arch_soffit`. Half cutwater noses 0.8 beyond y ±2.1 from −4.5 to −0.9 with sloped caps. Parapets 0.35 thick × 0.8 above the deck, coping 0.45×0.15. ROCK-flag deck. |
| `SM_VK_Bridge_Stone_Ramp` | Solid abutment 0 → 0.6, flared parapets ending in posts, flat half-pier face at its +X edge |
| `SM_VK_WaterWheel` (rotates) | R 2.2, width 1.0 (local Y). 16 paddles 0.7×1.0×0.06 in PLANKS. Two rims via `ring` (r 1.95–2.2, depth 0.12) at y ±0.5. 8 spokes per rim, hub r 0.35, axle r 0.18 from y −0.7 to +1.6 into the wall. Pivot at the axle; `spin_axis="local Y"`. |
| `SM_VK_WaterWheel_Mount` | Axle at WZ+1.7 = +0.2, wheel plane at y −1.3 from the wall line. Two posts + bearing block. Race channel 1.4 wide × 5.0 long, floor WZ−0.7, boards up to WZ+0.4. |

### F12 Facade and circulation extras (8 meshes, S)
- **`SM_VK_Wall_Gallery`** (tileable upper walkway): deck PLANKS y −1.4…−0.4 with top at the level base, sized so it stays under the 1.35 m eave. Knee brackets at x −1.5 from z −0.9, so no ground posts get in the way of pathing. Rail 1.0 with balusters every 0.16 (code from `balcony()`).
- **`SM_VK_Gallery_Corner`**, **`SM_VK_Gallery_End`**.
- **`SM_VK_Stair_Stone`**: `ext_stair` layout (run 2.7, rise H1, 12 steps of 0.25) on a solid STONE wedge (`grid_cut`), ROCK treads 0.18 overhanging 0.04, low ASHLAR-coped parapet, landing 1.5 at the next cell's door.
- **`SM_VK_Prop_CellarHatch`**: stone curb 1.6×1.4×0.35 against the wall, two plank leaves 0.75×1.35 at 30° with iron straps and ring pulls. An `_Open` variant shows VOID steps.
- **`SM_VK_Roof_Skylight`**: sits on `Roof_Mid` at ay = 1.5. Curb 0.9×0.8 following the slope, WINDOW quad, IRON flashing.
- **`SM_VK_Stair_Terrain`**: 3.0 wide, rises TSTEP over 3.0: 6 steps of 0.25 rise × 0.5 tread. Cheek walls 0.4, clear width 2.2.
- **`SM_VK_Wall_Retaining`**: 3 m, H = TSTEP, stone with coping + weep holes. For terraced plots. This is a *built* overlay of a terrain cliff edge, so agree on edge ownership with the terrain track.

### F13 Construction stages (10 meshes, S; mostly flags on existing generators)
| Piece | How |
|---|---|
| `SM_VK_Found_Outline` / `_Corner` | `plinth()` only + stakes and string lines |
| `SM_VK_Wall_Stone_Half` | Stone wall to z 1.4 with a ragged `rock()` top |
| `SM_VK_Wall_Timber_Skel`, `SM_VK_Wall_Plaster_Skel` | `timber_frame(..., infill=False)` / `plaster_ground(..., infill=False)` |
| `SM_VK_Roof_Mid_Rafters`, `SM_VK_Roof_Gable_Rafters` | Along the `roof_profile()` line: rafters 0.12×0.18 every 0.6, battens 0.04×0.06 every 0.35 on the lower half, ridge beam; no tiles |
| `SM_VK_Scaffold_Bay` | 3 m × one storey. Poles r 0.07 at x −1.5, y −1.3; ledgers at 2 lifts; putlogs into the wall; PLANKS deck 3.0×0.9; lashings; ladder variant |
| `SM_VK_Scaffold_Corner` | |
| `SM_VK_Prop_ConstructionPile` | Timbers + ASHLAR blocks + mortar tub + wheelbarrow |

Stages per recipe:
0. Outline
1. Ground walls as Half/Skel + scaffold
2. All walls + rafters + scaffold
3. Final

Every building, old and new, gets construction visuals for free.

### F14 Colony props (about 40 meshes, S each)
- **Stockpiles** at 1.5×1.5 m (4 per cell), in 3 fill levels (0.4 / 0.8 / 1.2 m high). One `stockpile(kind, fill)` generator per kind:
  - Logs: cylinders between 2 stakes
  - Planks: boards on bearers with spacers
  - Stone: ASHLAR blocks 0.5×0.35×0.35
  - Ore: ROCK heap + STEEL flecks
  - Grain: `prop_sacks` sacks on a pallet
  - Crates, Barrels (`barrel()`), Hay
  - Ingots: IRON bars in a crib
  - Firewood
- **Workstations** (each carries a `SOCKET_Work`):
  - ChoppingBlock: `make_stump` + axe
  - Sawhorse
  - SawFrame: frame 2.4 high, STEEL blade, 4.5 m log carriage
  - SawTrestle
  - MasonBench
  - TreadwheelCrane (M): wheel R 1.8 × 1.0, A-frame, 4.5 m jib, hanging block
  - BrewKettle: BRONZE lathe r 0.7 on a STONE hearth with GLOW
  - MashTun: `_cyl` staves r 0.9, 3 IRON hoops
  - DyeVats: 3 vats r 0.55 with CLOTH_A / YELLOW / WATER liquid discs
  - HideRack
  - FishRack: A-frame 3 m, 24 flattened icosphere fish
  - Nets: bundles + CLAY floats on a frame
  - Rowboat (S–M): 7 lofted U-sections, 3.6×1.3×0.55
  - Skeps: HAY lathe domes on a sheltered bench
  - HerbRack: CROPS cards hung upside down
  - Workbench, PotteryWheel
  - PotteryKiln: `bread_oven` body + 3 vents
  - CharcoalMound: SOIL dome r 1.6 × 1.2, GLOW vents, `SOCKET_Smoke`
  - TrainingDummy, ArcheryTarget: HAY boss + `ring` bands
  - MineCart; Rails_Straight: 3 m, sleepers every 0.6, gauge 0.9; Rails_End
  - **MineEntrance** (M): timber portal 3.2 × 3.0, 3 frames stepping 1.2 m back into VOID, lagging, rock collar from vk_nature `boulder()`
- **Civic and settlement**:
  - Tent: A-frame 2.2×3.0×1.9 in CLOTH_B
  - Campfire: 8 stones r 0.55, GLOW, tripod pot
  - Stocks, Pillory: on a 3×3×0.8 platform
  - MarketCross: 3 octagonal ASHLAR steps (r 1.6 / 1.2 / 0.8 × 0.3) + 3.0 shaft
  - WayShrine, Maypole (pole + CLOTH ribbons + flower crown)
  - Outhouse: 1.2×1.2×2.2, crescent VOID
  - Pigsty: 3×3 low stone pen + thatch lean shelter
  - Hedge: 3 m, foliage cards on a core, 1.3 high
  - Fence_Wattle: 3 m, 9 stakes + sine-woven tubes

---

## 4. New house types

The tiers are designed to share footprints, so an upgrade swaps the recipe in place: Hovel (2×2) → Cottage (existing 2×2) → House (2×2, 2 storeys) → Tower house (2×2), and Longhouse (5×2) → Merchant house or warehouse.

**H1 Settler tent.** Tier 0, holds 2, placed on day 1.
- Footprint: 1×1.
- Pieces: `Prop_Tent`, `Prop_Campfire`, plus `Crates` and `Sacks` (existing).
- Effort: S.

**H2 Hovel / cruck cottage.** Tier 1, holds 4; cheapest permanent home.
- Footprint: 2×2 (6×6).
- Levels: `["Wattle"]` (H0 2.2). Front `W.`, back `..`, west end `D.`, east end `.W`.
- Roof: `RoofThatch_Gable_Cruck` ×2 (for n=2 both bays are gable bays). `Roof_Louver` on bay 0, no chimney. Style plaster = Daub.
- Look: tiny walls under a huge roof with a 6.4 m ridge and curved cruck blades on the gables. Dressed with `Fence_Wattle`, `Woodpile` and `Chickens`.
- New pieces: F6. Effort: S after F6.

**H3 Log cabin.** Tier 1 frontier home, holds 4.
- Footprint: 2×2 or 3×2.
- Levels: `["Log"]`. Roof: `RoofThatch_Gable_Planks` / `Roof_Gable_Planks`. Existing `Chimney` and `Porch`.
- New pieces: F7. Effort: S.

**H4 Longhouse.** Tier 2 communal house (8) + byre (livestock). The Barracks-A variant is in B19.
- Footprint: 5×2 (15×6); 4–6 bays allowed.
- Levels: `["Wattle"]` or `["Log"]`. Long sides `W.W.W`. West gable `D`, east gable `B`.
- Roof: `RoofThatch_Gable_Cruck` + `RoofThatch_Mid` ×3 + `RoofThatch_Gable_Cruck`, with `Roof_Louver` on bays 1 and 3.
- Pen of `Fence` 3×2 cells at the byre end, with `Trough` and `HayBale`.
- New pieces: F6. Effort: S.

**H5 Rowhouse terrace.** Tier 3 urban housing; shop lots count as trade buildings.
- Footprint: lots of 1–2 bays × 2 deep, terraces of 3–8 lots.
- Per lot: levels `["Stone"|"Plaster","Timber"(,"Timber")]`, ground chars from `S D W C`, `Roof_Mid` per bay, `Dormer` / `Skylight`.
- At seams:
  - Same height and same roof variant: nothing (60%) or `Roof_Parapet` (40%).
  - Different roof variant: Parapet is mandatory.
  - Different height: the taller lot gets end modules and corners for its extra levels + its own Parapet.
  - `Roof_Parapet_Chimney` on about 50% of seams.
- Terrace ends: `Roof_Gable` (free end) or `Roof_Parapet_Stepped`.
- New pieces: F2 + F4 shop, plus a `build_row(lots)` assembler. Effort: M.

**H6 Gable-front townhouse.** Tier 3.
- Footprint: 2 wide × 3 deep (6 m frontage), rotated so the gable faces the street. It needs a **1-cell alley** to the next house because of the 1.35 m eaves (good for barrels, stairs and pathing).
- Levels: `["Stone","Timber","Timber"]`. Street gable end `SD`. Street bay `Roof_Gable` (timber gable window; the corner dragon beams give jetties on the gable face). Back bay `Roof_Hip`. `Roof_Dormer_Hoist` on one slope. Optional `Wall_Timber_Oriel` on the street gable.
- New pieces: none beyond the `ends` chars (the old code picks end walls at random) and the F4 shop. Effort: S.

**H7 Corner house.** Tier 3–4 street-corner landmark (+appeal).
- Footprint: 3×2 plus a Ø4.0 tower at the corner vertex.
- Levels: `["Stone","Timber"(,"Timber")]`. At the street corner, instead of `Corner_*`: `TowerS_Base_Door` (door at 225°) + `TowerS_Mid` × (storeys − 1) + `TowerS_Mid` ×2 above wall top + `TowerS_Cone`.
- Roof: `Roof_Hip` at the tower end, `Roof_Gable` at the other. Doors on both street faces.
- New pieces: F9. Effort: S.

**H8 Stone merchant house.** Tier 4 housing + shop + small storage.
- Footprint: 3×2. Eaves at 8.6 m, ridge 12.8 m.
- Levels: `["Stone","StoneU","StoneU"]`. Street: ground `SCD`, level 1 `MMM`, level 2 `WLW`.
- Roof: `Roof_Mid` ×3 + `Roof_Parapet_Stepped` ×2 (Flemish crow-steps), `Roof_Dormer_Hoist` above the loft bay, existing `Chimney`.
- Extras: `Prop_CellarHatch`, `Sign_*`, `Lantern`. Masonry: Warm.
- New pieces: F1, F2, F4. Effort: S.

**H9 Tower house.** Tier 4 elite or defensive home; garrison 2, stores valuables.
- Footprint: 2×2, walls to 11.4 m.
- Levels: `["Stone","StoneU","StoneU","StoneU"]`. Ground `D` + slits.
- Defensive first-floor entrance: `Wall_StoneU_Door` + `Stair_Stone`.
- Variant A: `Roof_Hip` ×2 (pyramid, ridge 15.6), `Chimney`.
- Variant B: `Parapet_Crenel` ×8 + `Parapet_Crenel_Corner` ×4 + `Roof_Flat` ×4 + `Roof_Pyramid_Inset` + `Bartizan` ×2 on diagonal corners at z = top − 1.5.
- New pieces: F1, F9. Effort: S (A) / M (B).

**H10 Manor house.** Tier 5 lord's residence (admin, prestige).
- Footprint: L plan, `build_L`-style with a = 2, b = 2 (two 12 m wings).
- Levels: `["Stone", fn(edge)→"StoneU" on wing A / "Timber" on wing B]`.
- Stair tower: TowerS stack at the inner vertex (3, 3) rising 2 segments above the wall top + cone.
- `Wall_Gallery` on the courtyard face of wing B.
- Roof: `Roof_LCorner` + Mids + `Roof_Parapet_Stepped` at the A end + `Roof_Gable` at the B end, 2 chimneys, dormers.
- Forecourt: `LowWall` ring with `LowWall_Lychgate` as gate, `Fountain`, `GardenBed`, `Hedge`.
- New pieces: F1, F2, F9, F12. Effort: M.

**H11 Stilt house.** Tier 1–2, fisher or marsh family.
- Footprint: 2×2 over water.
- `Found_Piles` + `Found_Deck` ×4, levels `["Plank"]` at z 1.2, `RoofThatch_Gable_Planks`, `Dock_Deck` walkway to the shore, ladder.
- New pieces: F7, F8. Effort: S.

**H12 Hillside house** (any tier on a terrain step).
- Cells on the lower level with the back wall line on the cliff edge.
- Levels: `["Basement","Stone","Timber"]`. The basement front is `V.V`; its back is buried against the cliff.
- The ground floor at z = TSTEP is reached by `Stair_Stone` from the street; a back door opens onto the upper plateau.
- New pieces: F8 basement. Effort: S. Needs the terrain track's step height and straight axis-aligned cliff edges.

---

## 5. New village buildings and features

### Production
**B1 Woodcutter's lodge** (trees → logs).
- Site: 3×3.
- H3 cabin + `LeanTo_Thatch` + `Stockpile_Logs` ×2, `ChoppingBlock`, `Sawhorse`, `Woodpile`.
- New: 3 props. Effort: S.

**B2 Sawmill** (logs → planks, water-powered).
- Footprint: 3×2 on the bank.
- Levels: `OpenTall` on the front and river end, `Barn` on the rest. `Corner_OpenTall` / `Corner_Barn`. Roof at HB: `Roof_Gable_Planks` ×2 + `Roof_Mid`.
- `WaterWheel` + `Mount` on the river end; `SawFrame` inside; `Quay_Wall`; plank and log stockpiles.
- New: F5, F11, SawFrame. Effort: M.

**B3 Watermill** (grain → flour).
- Footprint: 2×2 or 3×2.
- Levels: `["Stone","Timber"]`. Hoist column: `CartDoor` → `Timber_Loft`. `WaterWheel` on the end wall; `Quay_Wall`; `Sacks`, `Cart`.
- Effort: S after F4 and F11.

**B4 Stonemason's yard and quarry.**
- Yard 3×3 + H3/plank lodge with `LeanTo`.
- Quarry face from `Rock_Outcrop` / `boulder()` against a terrain cliff. `TreadwheelCrane`, `MasonBench` ×2, `Stockpile_Stone`.
- Effort: M (crane).

**B5 Mine** (ore / coal).
- `MineEntrance` in a cliff at least 2 steps (3.0 m) high, `Rails_Straight` ×n + `Rails_End`, `MineCart`, `Stockpile_Ore`, log-cabin office, spoil heap (`Rock_Pebbles`).
- Effort: M.

**B6 Brewery with oast kiln** (grain → ale for the tavern).
- House 3×2 `["Stone","Timber"]`. The kiln end uses `Roof_Parapet`, which is hidden inside the tower.
- Kiln: TowerS stack centred at (L/2 + 1.75, 0): Base + Mid ×2 + new **`SM_VK_Roof_OastCowl`** (steep TowerS cone + white-boarded cowl 1.0×0.9×1.2 in PAPER with a WOOD vane).
- Props: `MashTun`, `BrewKettle`, `BarrelStack`.
- Effort: M.

**B7 Tannery and dye works** (hides → leather, wool → cloth).
- 2×2 plaster house + `Wall_Open` ×2 shed with `LeanTo` + riverside yard.
- `DyeVats` ×2, `HideRack` ×2, existing `Laundry` recoloured through the cloth style.
- Effort: S.

**B8 Fishery and smokehouse.**
- H11 stilt hut + `Dock_Deck` ×3–6 + `Dock_End` + `Rowboat`.
- Smokehouse: 2×2 log hut + `Roof_Louver` + `FishRack` ×2, `Nets`.
- Effort: S–M.

**B9 Carpenter / cooper / wheelwright** (planks → furniture, barrels, carts).
- 3×2, ground `Open` on the 2 front bays and Plaster elsewhere, `Timber` above (workshop below, living above).
- `Workbench`, `Sawhorse`, plank stockpile, loose barrel staves and cart wheels (from `barrel()` / `prop_cart`).
- Effort: S.

**B10 Kilns.**
- Charcoal burner camp: `CharcoalMound` + Tent/Hovel + logs.
- Potter: 2×2 house + `PotteryKiln` + `PotteryWheel` + CLAY lathe pots on shelves.
- Effort: S.

**B11 Apiary and herbalist** (honey/wax, medicine).
- Hovel or cottage + existing `Crop_Lavender` + `Skeps` ×2 + `HerbRack` + existing `Sign_Potion`.
- Effort: S.

**B12 Farmstead additions.**
- `Pigsty` (3×3); sheepfold (`LowWall` ring of 3×3 cells + `LowWall_Post` + `FenceGate`).
- Dovecote: `TowerS_Base` + `TowerS_Mid_Dovecote` + `TowerS_Cone`.
- Effort: S.

### Storage and trade
**B13 Granary on staddles** (spoilage and rodent protection).
- Footprint: 2×2.
- `Found_Staddle` (+ corners) + `Found_Deck` ×4, levels `["Plank"]` at z 0.8, `RoofThatch_Gable_Planks` ×2, `Found_Steps`.
- Effort: S.

**B14 Warehouse** (bulk storage, trade capacity).
- Footprint: 4×2, quay or street.
- Levels: `["Stone","StoneU","Timber"]`. Ground `CDCD`, level 1 `LWLW`, level 2 `LWLW`; hoist dormers above the L bays; `Roof_Parapet_Stepped` ends.
- Crate, barrel and sack stockpiles.
- Effort: S.

**B15 Market hall** (covered market, works in rain).
- Footprint: 4×2.
- Levels: `["Open","Timber"]`, all ground edges open. Roof: `Roof_Hip` ×2 + `Roof_Mid` ×2 + existing `Roof_Cupola`.
- Existing `Stair_Ext` to a `Wall_Timber_Door`. Tables, crates and stockpiles underneath. `MarketStall` does not fit: it is 3.1 m tall, the floor above is at 3.0.
- Effort: S.

**B16 Stockpile yard** (generic storage zone).
- 3×3-cell yard with `Fence` / `FenceGate`, 4 stockpile slots per cell; the fill level mirrors inventory.

- Effort: S (M for all 10 stockpile kinds).

**B17 Guildhall** (guild crafts, research, tax).
- T plan. Main wing is 6 bays on the street: `Gable, Mid, Roof_T (2 bays), Mid, Gable` = 18 m. A rear cross wing leaves from the T square: 2 cells for the junction + 2 cells = 12 m deep.
- Levels: `["Stone","Timber","Timber"]`. Street front: existing `Wall_Arcade` on the 4 central bays, `D` at the ends. Existing `Balcony` at the centre.
- Roof: `Roof_Gable` at the street ends (timber above timber, so no parapet), `Roof_T`, `Roof_Mid`, `Roof_Gable` at the rear end, `Roof_Cupola` on a Mid bay.
- `Wall_Gallery` along both courtyard faces formed by the T.
- New: F3, F12. Effort: M (T-plan assembler).

### Civic and services
**B18 Cruciform church** (upgrade from the chapel, faith tier 2).
- Footprint: 8 cells long × 4 wide (24×12). Nave 4×2 + crossing 2×2 + one-bay transept arms + chancel 2×2.
- Walls: existing `Chapel_Wall/_Plain/_Door/Chapel_Corner` (HC 4.5) + new **`SM_VK_Chapel_InnerCorner`** (S) at the 4 concave vertices.
- Roof: **`Roof_X`** over the crossing. Nave: `Roof_Mid` ×3 + `Roof_Gable_Stone` at the west end. Each 1-bay transept is a single `Roof_Gable_Stone` (one bay can be its own gable bay). Chancel: `Roof_Mid` + `Roof_Hip` (apse-like end).
- Bell tower, either option:
  - `BellTower` freestanding at the west end, as `build_chapel` does.
  - Centred on the crossing, lifted 1.0 m so the belfry at 9.1 clears the ridge at HC + 4.19 = 8.69. The shaft is hidden inside.
- Effort: M.

**B19 Barracks and training yard** (military housing for 8, skill training).
- H4 longhouse (Log/Plank) or a 4×2 `["Stone","Timber"]` block.
- Yard 3×3 fenced with `Palisade` or `LowWall`: `TrainingDummy` ×3, `ArcheryTarget` ×2, existing `WeaponRack`, `Campfire`.
- Effort: S.

**B20 Civic props.**
- `Stocks`, `Pillory` (justice), `MarketCross` (plaza centrepiece, sets the market radius), `WayShrine` (+mood on roads), `Maypole` (festival), `Outhouse` (hygiene need), `Hedge`, `Fence_Wattle`.
- Effort: S each.

### Defence
**B21 Palisade line** (defence tier 1).
- `Palisade` runs along cell edges, `Palisade_Corner` at vertices, `Palisade_Walk` behind defended stretches, `Palisade_Gate` + 2 × `Palisade_GateLeaf` across roads (4.2 m opening).
- `Palisade_Tower` occupies the cell just inside the line, with its outer posts on the line.
- Effort: S–M.

**B22 Stone town wall** (defence tier 2).
- `Curtain` on cell edges. The 1.5 m thickness straddles the edge, so both half-cells are blocking.
- `TowerL` stacks at vertices every 3–5 modules and at corners: Base + Mid + WalkDoor + Crenel or Cone. The doors land at ZW = 5.8.
- `Curtain_Stair` about every 30 m; `Curtain_Corner` where there is no tower.
- Effort: M–L.

**B23 Gatehouse.**
- `Curtain_Gate` (6 m) + 2 TowerL stacks at x ±3 + `Gate_Hoarding` + 2 × `Curtain_GateLeaf`.
- Upgrade path: `Palisade_Gate` → Gatehouse on the same 2-cell span.
- Effort: M.

**B24 Keep** (stronghold, treasury, last refuge).
- Footprint: 3×3 (9×9). Flat roofs remove the 6 m depth limit.
- Levels: `["Stone","StoneU","StoneU","StoneU"]`. `Roof_Flat` ×9 + `Parapet_Crenel` around the perimeter.
- TowerS stacks at all 4 corners, rising 1 segment above the wall top, each with a cone (Stormwind-keep silhouette). First-floor entrance via `Stair_Stone`.
- Effort: M.

### Infrastructure
**B25 Bridges.**
- Recipe: `Ramp` + `Span` × n + `Ramp` rotated 180. The wooden version adds `Bridge_Wood_End` at the far side.
- Upgrade: wood (tier 1) → stone (tier 2) on the same cells.
- Existing `LampPost` on the parapet ends of stone bridges.
- Effort: covered by F11.

**B26 Docks and harbour.**
- `Dock_Deck` grid, `Dock_Rail` on open edges, `Dock_End` at pier heads, `Dock_Ramp` to the bank. `Quay_Wall` and `Quay_Stair` along built banks.
- B14 Warehouse on the quay; `TreadwheelCrane` as the harbour crane; `Rowboat`, `Nets`, `BarrelStack`.
- Effort: S once F11 exists.

**B27 Construction sites.**
- Every recipe gets stages 0–3 (F13) + `Prop_ConstructionPile`.
- Unity swaps stage prefabs from the recipe JSON.
- Effort: S (flags) + one pass over the assembler.

**B28 Terrain connectors.**
- `Stair_Terrain` between terrain levels, `Wall_Retaining` for terraced gardens and plots, the H12 basement, and quays at water edges.
- Must be agreed with the terrain track: step height, which side of a cliff edge a built wall occupies, and whether cliff tiles get built-over variants.
- Effort: S.

---

## 6. Reuse matrix (new families × key buildings)

Columns:

| Code | Building | Code | Building |
|---|---|---|---|
| Hov | Hovel | Gra | Granary |
| Long | Longhouse | Ware | Warehouse |
| Row | Rowhouse terrace | MHall | Market hall |
| Corn | Corner house | Guild | Guildhall |
| Merch | Merchant house | Church | Cruciform church |
| TowH | Tower house | Walls | Town wall |
| Man | Manor | Gate | Gatehouse |
| Saw | Sawmill | Keep | Keep |
| Mill | Watermill | Dock | Docks and harbour |

| Family | Hov | Long | Row | Corn | Merch | TowH | Man | Saw | Mill | Gra | Ware | MHall | Guild | Church | Walls | Gate | Keep | Dock |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 StoneU | | | ○ | | ● | ● | ● | | | | ● | | | | | | ● | |
| F2 Parapet | | | ● | | ● | ○ | ● | | | | ● | | | | | | | |
| F3 Roof T/X | | | | | | | ○ | | | | | | ● | ● | | | | |
| F4 Commerce | | | ● | ○ | ● | | | | ● | | ● | | ○ | | | | | ○ |
| F5 Open bays | | | | | | | | ● | | | | ● | | | | | | |
| F6 Wattle/cruck | ● | ● | | | | | | | | | | | | | | | | |
| F7 Log/plank | | ○ | | | | | | ● | | ● | | | | | | | | ● |
| F8 Foundations | | | | | | | | | | ● | | | | | | | | ● |
| F9 Towers/crenel | | | | ● | | ● | ● | | | | | | | ○ | ● | ● | ● | |
| F10 Fortification | | | | | | | | | | | | | | | ● | ● | | |
| F11 Water | | | | | | | | ● | ● | | ○ | | | | | | | ● |
| F12 Gallery/stairs | | | | | | ● | ● | | | | | ○ | ● | | ○ | | ● | |
| F13 Construction | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |

● = required, ○ = optional or variant.

---

## 7. Build order

**Phase A: urban and commerce core (about 33 meshes).**
1. §2.1 wobble envelope and §2.2 height parameters.
2. §2.3 assembler + family table + chars.
3. F1 (7), F2 (3), F3 (2), F4 (5), F5 (5), F13 (10).
4. §2.6 recipe JSON.
- Unlocks: H5, H6, H8, B3 (without the wheel), B14, B15, B17, B18, plus construction stages for all 146 existing and all new pieces.

**Phase B: early-game and peasant tier (about 26 meshes + about 12 props).**
- F6 (8), F7 (10), F8 (8), and props: Tent, Campfire, Stockpile_Logs/Planks/Grain, ChoppingBlock, Sawhorse, Fence_Wattle, Outhouse, TrainingDummy, ArcheryTarget.
- Unlocks: H1, H2, H3, H4, H11, H12, B1, B13, B19.

**Phase C: height and defence (about 27 meshes).**
- F9 (15), then F10 (12).
- Unlocks: H7, H9, H10, B6, B12 dovecote, B21–B24.

**Phase D: water (14 meshes).**
- F11.
- Unlocks: B2, B3 (full), B8, B25, B26.

**Phase E: production props and connectors (about 28 meshes).**
- The rest of F14, F12 (8), `Chapel_InnerCorner`, `Roof_OastCowl`.
- Unlocks: B4, B5, B7, B9, B10, B11, B16, B20, B28.

After each phase, render a catalog sheet in the style of `catalog_walls.png` and one assembled example per new type. Check the seams listed in §8 in close-up renders.

---

## 8. Seams and risks to verify

1. **Stone-on-stone stacking:** after the §2.1 envelope change, check that `Wall_StoneU` on `Wall_Stone` shows no step at z = 3.0 (a 0.035 m y-offset would show without it). The string course is the backup cover.
2. **Parapet over timber:** its face sits 0.15 behind a jettied wall. The assembler must fall back to `Roof_Gable` unless the end is hidden by a tower.
3. **Height-stepped terraces:** the lower roof's cut end is exposed for |y| 3.25–4.35 (eave zone). Acceptable, or add `end_caps=(False, True)` to that bay's `roof_slab`, which is already supported.
4. **Round towers at corners:** R must stay ≥ 1.91 (the hip-corner distance). TowerS must rise 2 × H2 above the wall top so the cone clears the main roof. Remove `Corner_*` / `InnerCorner_*` wherever a tower replaces them.
5. **Gable-front neighbours:** they need a 1-cell alley (eaves stand 1.35 m out, twice = 2.7 m).
6. **Hovel eaves:** the lip underside is about 1.4 m at H0, so wattle doors go only on gable ends. The assembler should reject `D` / `B` on eave-side edges for the Wattle family.
7. **Thatch has no T/X junction pieces:** the roof planner switches T/X-plan buildings to tile.
8. **Seam-split elements** (bridge half-piers, crenels at x = ±1.5, parapet coping) must not overlap coplanar. Thin posts keep the left-edge rule and need an end or corner piece: `Bridge_Wood_End`, `Gallery_End`, `Corner_Open`.
9. **Material list is append-only** (`kit_mats()`, currently 45 slots).
10. **FBX export:** every kit mesh currently carries all 45 slots. Strip unused slots on the export copy, or Unity may create empty submeshes and break batching. Consider atlasing the flat-colour materials into one palette texture.
11. **Animated parts are separate meshes** with axis pivots: `WaterWheel`, the gate leaves, `Windmill_Sails` (already done).
12. **Terrain interface (agree with the terrain track):**
    - Terrain cell = 3 m = CELL, with corners on kit vertices.
    - Building footprints need flat cells (all corners at the same height).
    - The value of TSTEP.
    - The WZ water level below the bank.
    - Straight axis-aligned cliff edges for basements, quays and mine entrances.
    - Every ground piece carries a skirt to −1.0 or deeper, so small terrain mismatches never open gaps.