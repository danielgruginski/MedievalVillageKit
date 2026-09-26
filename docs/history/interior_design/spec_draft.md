# Interior Kit (VKI): verdict on the three proposals and the final spec

I checked the facts this spec depends on in the code: `vk_helpers.py` (`TILE`, `tex_mat`, `kit_mats`, variants, `Kit`, `grid_cut`, `window_frame`, `merge_kit`, `place`, `full_rebuild`, `build_smithy`, `smith_toolwall`, `prop_lantern`), `vk_mat.py`, `ws_common.py`, `vk_kit.py`, `vk_render.py`, `kit_sync.py`, `vk_tex2.py`, `vk_mod_industry.ind_bellows`, `vk_mod_town.twn_flat_wobble`, and the archived render-settings logs. I also looked at `blacksmith.jpg` and `tavern.jpg`. I made no Blender calls and edited no files.

---

## 0. Verdict

### 0.1 Scores (1–10)

| | Concreteness | Correct vs code | Fit to decisions and the WoW look | Risk (10 = low) | **Overall** |
|---|---|---|---|---|---|
| **P1 gameplay** | 9: verified camera maths, fit/follow rule, link model, executable plans, reachability QA | 7: doors and windows collide with its own posts; no node-zone rule; its layouts break its own occlusion rules | 8 | 6: core edits to `kit_mats`/`finish`, specs added to `EXTRA_SPECS` | **8** |
| **P2 architect** | 9: node zones, coverage inequalities, seam rule, role slots, harness T1–T13 | 7: occlusion strip wrong (0.42 m); stair-down descends away from the camera; role-slot defaults render stone as plaster | 7: 124 structural masters including a needless F28 set; 0.80 m doors; sills above the cut, so windows vanish from near walls | 8: no core edits, separate prefix and rebuild | **8** |
| **P3 art** | 8: palettes, scale table, lighting, FX, dressing, prioritised lists | 7: 1.1–1.2 m doors cannot fit between its own node posts; mixed thicknesses with no coverage rule | 9: best reading of the style (caps as real members, sills at 1.00, lit exits, GlowIn) | 6: geometry system under-specified | **7.5** |

**What the final spec takes from each:**
- **P1:** camera maths and fit/follow, the link-id and spawn model, the room plans (repaired), the height-budget rules, "stairs are used, not climbed", the stair direction rule, and BFS/link QA.
- **P2:** full-length walls with proud posts, the node zone, the coverage inequalities, the end-pinned outward-only crc32 wobble, role slots, the separate `SM_VKI_` registry with no core edits, prop-copying rebuild, reserved heights, and the harness.
- **P3:** cut caps as real architectural members, window sills at 1.00, doorways in cut walls without leaves plus a daylight spill, scale exaggeration, the value/palette structure, graded GlowIn, window spots, Day/Night presets, the repetition defences, and the furniture lists.
- **Survey B:** the texture recipes, implemented as copies rather than edits to the exterior generators.

### 0.2 Claims that are wrong

1. **Task's KNOWN FACTS: "renders use the Standard view transform."** `VillageKit` is AgX, look "AgX - Medium High Contrast", exposure −0.2. Evidence: `archive/script_logs/agents/valley-rereview/agent-ac910b8221bab24cf.py` L410 and `main_session/blender_calls_part01.py` L14368. `tools/render_showcase.py` uses Standard only when converting the PNGs to JPEG. (A memory note from the diffusion work recommends Standard; §10 lists this as an open question.)
2. **P2 §2.3: "about 0.42 m inside the room face is hidden".** The hidden strip starts at the wall's room-side top edge, not its outer edge. Hidden depth is h/tan φ plus the cap overhang: 0.72 m at 55° and 0.86 m at 50° (screen centre).
3. **P2 §6: `Floor_StairDown` descends along +Y.** The risers then face away from the camera, and the piece is back to front relative to a flight that rises north into the head wall. The correct pairing is P1's: the lower floor rises north, and the upper floor's hole has its top at the north and descends toward −Y.
4. **P1 §4.1: 1.0 m doors (frames at x 0.17–0.25) and windows at x 0.2–1.3 in a 1.5 m piece.** These overlap P1's own 0.54 m posts (±0.27) at the adjacent nodes. P1 has no opening-zone rule.
5. **P3 §3.2: clear doors of 1.1–1.2 m in a 1.5 m piece.** With 0.60 m quoin columns or 0.30 m posts at the nodes, at most about 0.84–0.9 m remains. P3's per-family thicknesses (0.12, 0.30, 0.50, 0.60) come with no junction coverage rule.
6. **P1 §1.1 table note: floor hidden "measured from the object's camera-side face".** It should be measured from the far (room-side) top edge. P1's numbers are nevertheless applied correctly.
7. **P1 §6.3: `Prop_ToolWall` at "cell centre + (0, +0.46)".** The board's back is at local y −0.01 (`smith_toolwall`), so on a 0.50 m wall the origin belongs at wall line − 0.24 (cell centre + 0.51). P1's value leaves a 5 cm gap. `Prop_Lantern`'s back plate reaches y +0.10, so its origin sits 0.10 in front of the face.
8. **P1's plans break its own ≤1.2 m rule:**
   - cottage: the ladder at (0,2) stands in front of the loom;
   - tavern kitchen: the barrel at (6,5) stands in front of the trapdoor;
   - tavern hall: 1.2 m settles directly in front of the hearth;
   - smithy: the weapon rack at (6,3) stands in front of the workbench;
   - tavern F1: the box bed at (8,1)–(8,2) hides the corridor.
9. **P2 §9: role slot WALL_IN defaults to PlasterIn White for every family.** Every stone or ashlar master would render as plaster unless each instance carried a style. Fixed below with per-master slot defaults.
10. **P1/P2: "`ws_build` copies custom properties".** It does (`ws_common` L83), but it makes no difference: builders receive only a `Kit`, so the temporary object carries only `kit`/`cell_m`. Master metadata needs its own channel (`k.meta` below).
11. **P2 §1: the Unity axis mapping "(x,y,z)→(x,z,y), rotation signs invert" is an assumption.** The FBX importer also mirrors one axis for handedness. Establish the mapping with `SM_VKI_Test_Axis` before relying on it.
12. **Survey B's recipes call parameters that do not exist:**
    - `vk_tex2.gen_ashlar(S, seed, tile, depth)` has no `out_prefix`, `nrow` or `blocks`;
    - `gen_plaster` has no `cracks` or `out_prefix`;
    - `gen_wattle` has no `nst` or `nrod`;
    - `gen_stoneblock` has no `lichen` or `cracks`;
    - `gen_stone` hard-codes 7 courses and always adds moss and lichen.

    Survey B knew edits were needed. This spec copies the generators instead, so exterior textures cannot drift.
13. **Surveys: "GLOW clips to white under Standard".** The white forge coals in `blacksmith.jpg` are under AgX. The cause is `M_VK_Glow`: a legacy flat material at emission 4.0 with no `MAT_MAP` entry.

---

## 1. Camera and cut height

**Reference camera** (Unity target, and every verification render):

| Setting | Value |
|---|---|
| Yaw | fixed, looking +Y (north is the top of the screen) |
| Pitch | **50°** below the horizon |
| Field of view | vertical 30° (Blender `lens=38` on the default 36 mm AUTO sensor at 16:9) |
| Distance D | **18 m** to the look-at point (zoom 14–22) |
| Clip | near 0.5, far 80 |

In Blender the camera sits at `target + (0, −11.57, +13.79)` for D = 18.

**Why 50° rather than 55°:**
- It matches the colony camera (40 m, 50°) that every prop and texture was judged at, and it needs only one sprite pitch if characters turn out to be sprites.
- A 3 m far wall projects to 1.93 m (1.72 m at 55°), which leaves more room for far-wall dressing.
- The cost is 0.14 m more floor hidden behind a cut wall.
- 55° is the tuning ceiling. Every rule below holds from 50° to 60°.

**Framing at D = 18:**
- Floor visible along Y runs from −5.14 to +8.12 m around the target. Width at the target is 17.1 m.
- About 112 px/m at 1080p. A 1.8 m character is about 130 px; a 1.5 m cell is about 168 × 129 px.
- Textures at 683 px/m sit about 2.5 mip levels down, so painted features must be at least 3 cm and joints at least 6 mm.

**Fit or follow:**
- Fit: D_fit = (L + 1.5 + 1.428·h) / 0.737 and D ≥ (W + 1) / 0.778, where L is room depth, W width and h far-wall height. Rooms with D_fit ≤ 18.5 use a locked camera at D_fit.
- Otherwise follow: the look-at point is the player, clamped to x ∈ [x_W+3, x_E−3] and y ∈ [y_S+2, y_N−2].

**Occlusion:** an object of height h hides floor for h/tan φ beyond its room-side top edge. φ is 50° at the screen centre and ranges from 35° (top of frame) to 65° (bottom).

**Cut height: `CUT_H = 1.00` m to the top of the cap, for every family and every storey.**
- It hides 0.47–0.86 m of floor (0.86 at the screen centre, cap overhang included).
- 0.8 m reads as a fence. 1.2 m hides a whole row.

**Layout rules that follow from this:**
- R-occ1: nothing interactable at floor level (trapdoor, stair hole, dropped item) within 0.9 m of a cut wall's room face.
- R-occ2: props taller than 1.2 m only against a full north wall, or on a side wall where the cell north of them is neither a lane nor an interactable.
- R-occ3: nothing above 2.0 m over walk lanes. Optional overhead items carry `vki_cam_fade`.
- R-occ4: wall-mounted dressing only on full walls (`vki_mount="wall_full"`).

---

## 2. Grid and wall system

### 2.1 Coordinates and constants

- **Grid.** `IG = 1.5`. Nodes sit at (1.5i, 1.5j). Each scene's origin is its SW node, and the floor top is at z = 0 on every storey (one scene per floor). Cell (c, r) has its centre at (0.75 + 1.5c, 0.75 + 1.5r). Row 0 is the camera (south) side.
- **Wall piece.** The origin is the start node on the centreline at z = 0. The piece spans local x ∈ [0, L], L ∈ {1.5, 3.0}. The room face (A) is local −Y (the exterior "show face is −Y" rule); face B is +Y.
- **Perimeter placement, clockwise seen from above:**

  | Wall | Rotation | Origin |
  |---|---|---|
  | North | 0 | W end |
  | East | −90 | N end |
  | South | 180 | E end |
  | West | +90 | S end |

  For partitions the direction only decides which side is A and which is B.
- **Floors** have their origin at the min-corner node and are **never rotated**. Stairs and trapdoors have their origin at the min-corner node. Posts sit centred on their node.
- **Props** have their origin at the footprint centre (floor level), with the back at local +Y. They snap to 0.75. Wall-mounted props use the wall convention (origin on the grid line at the start node, back against y = −0.25).

| Constant | Value |
|---|---|
| `T` (thickness) | Class **O** = 0.50 (Timber, Stone, Ashlar). Class **P** = 0.30 (Wattle, Board). |
| `H_FULL` | Timber 3.0 · Stone 3.0 · Board 3.0 · Wattle 2.4 · Ashlar 4.5. No 2.8 set: upper floors use 3.0 so props stay universal. |
| `PROUD` | 0.02: caps, skirtings, oak members and string courses stand 0.02 beyond the body, giving half-widths O 0.27 / P 0.17 |
| `POST_HW` | O 0.30 / P 0.20; bevel ≤ 0.02; top = wall top + 0.04 |
| `NODE_FLAT` | 0.32: no deformation within this distance of any node |
| `OPEN_MIN` | 0.33: clear openings lie in x ∈ [0.33, L−0.33] |
| Surround zone | frames and jambs may occupy x ∈ [0.25, 0.33], with \|y\| ≤ 0.29 (O) or 0.19 (P), and stay below the post top |
| `FOOT_Z` | −0.30: wall bodies continue below the floor as a section footing |
| Reserved heights | 0 floor · 0.015 sill strip · 0.02 hearth apron · 0.03 threshold · 0.16 skirting top · 0.20 dais · 0.80 table top · 0.90–1.00 cut cap · 1.04 cut post top · H−0.12…H full cap · H+0.04 full post top |

Horizontal faces of different piece classes never share a height where they overlap.

### 2.2 Families (chosen for this round)

| Family | Class | H | Room face default (`WALL_A`) | Base | Cut cap at 0.90–1.00 | Full top | Node post | Used in |
|---|---|---|---|---|---|---|---|---|
| **Timber** (the main family) | O | 3.0 | PlasterIn Cream, 0.02 behind oak; stud at 0.75 of every span; B variant adds a curved brace above 1.2 m only | oak sole plate 0–0.16 | oak mid-rail; top face `CAP` = Hewn; the **same rail runs on Full walls**, so transitions are seamless | oak head plate | oak post; top face ENDGRAIN | cottage, townhouse, tavern, guest floor |
| **Stone** (rubble) | O | 3.0 | StoneIn (tinted like the exterior's stone style) | none | StoneBlockIn coping in 0.75 units with V-joints | same coping | quoin pier: stacked StoneBlockIn blocks inside ±0.30 | smithy, cellar, hearth walls, stone ground floors. **Limewashed masonry** = Stone A pieces with `wall_a=Plaster*`; the arches stay dressed stone. |
| **Ashlar** | O | 4.5 | AshlarIn | none (the stone bench is a separate prop) | DRESS string course, weathered top, max 1.00; also present on Full walls, plus a second string course at 3.0 and a cornice as the cap | cornice | clustered respond (half-shafts inside the envelope) | chapel |
| **Wattle** | P | 2.4 | PlasterIn Daub, pillowed; B variant shows a bare WattleIn patch above 1.2 m | oak sole beam 0–0.20 | hewn oak rail | sagging wall plate (sag ≤ 0.03, zero at nodes); soot in `vki_dark` above 1.4 m | crooked hewn post, bow ≤ 0.02 inside the envelope; ENDGRAIN top | hovel |
| **Board** | P | 3.0 | BoardsV (the Boards_NS texture on walls, so boards run vertically and light still comes from above) | none | Hewn rail | Hewn rail | oak post | guest rooms, stores, light partitions |

- **Deferred:** Log and StoneUp families (cabins and stone upper storeys are a later round).
- **Why two thicknesses:** thick perimeter walls against thin partitions read like an architectural plan from above. On class O walls, every existing wall prop built for a face at −0.25 mounts unchanged. On class P walls the placer adds +0.10 (`vki_back_y`).

**Cross-section per piece (O / P):**

| Element | O | P | z |
|---|---|---|---|
| Body (A face `WALL_A`, B face `WALL_B`, ends `WALL_A`) | ±0.25 | ±0.15 | −0.30 to cap bottom |
| Skirting / sole | ±0.27 | ±0.17 | 0–0.16 (Timber and Wattle only) |
| Cut cap | ±0.27 | ±0.17 | 0.90–1.00 |
| Full cap | ±0.27 | ±0.17 | H−0.12 to H |

The top faces of caps and posts are the `CAP` "section" surface, so the room outline reads as a pale line.

### 2.3 Junctions and free ends

Walls always run the full distance from node to node. Collinear pieces simply butt together.

| Situation at a node | Piece |
|---|---|
| Straight run, same family, class and height | nothing. The assembler puts a `Post_*_Mid` at every node for Timber, Wattle, Board and (optionally) Ashlar, for structural rhythm. |
| L, T or X junction, free end, height change, class or family change | `Post_<fam>_Corner` of the thickest class present, at the tallest wall-end height present (a rake contributes its end height) |
| P partition teeing into an O wall | O Corner post (the P stem, ±0.17, sits inside ±0.30) |

**Coverage (checked by test T4):**

| Condition | O | P |
|---|---|---|
| post ≥ cap + 0.03 | 0.30 ≥ 0.27 + 0.03 | 0.20 ≥ 0.17 + 0.03 |
| chamfered arris covers the cap corner: 2·post − bevel ≥ 2·cap + 0.03 | 0.58 ≥ 0.57 | 0.38 ≥ 0.37 |
| post ≤ `NODE_FLAT` | yes | yes |

**Posts are rigid:** no jitter, and no round posts in the Corner role. Wall end faces use `WALL_A`, so an end left without a post still reads as plaster wrapping round the end; the validator only warns about it.

### 2.4 Full, cut and rake

- Every wall shape exists as `_Full` and `_Cut` (the user's decision). They share footprint, origin, collider, grid cuts, UVs and wobble below 0.65 m. The cut piece is exactly the lower metre of the full one plus its cap.
- `vki_cut_pair` names the twin, which enables a one-click toggle in Unity. Shapes that have no cut version (Slit, Niche, fireplaces, LancetTall) name `Plain_150A_Cut` as their pair.
- **Rake** (`Rake_150_L/R`): the top slopes from 1.00 at the low end to H at the high end. It is the default south-most piece of a full N–S wall that meets a cut south wall: `L` on west walls, `R` on east walls. The alternative is a full-height Corner post (a "proscenium pillar"); the core look test decides which is the default.
- **Default wall heights**, which the designer can override per wall:
  - the north wall is Full;
  - N–S walls are Full, with a Rake at the south end;
  - the south perimeter and every E–W partition with walkable floor north of it are Cut.

### 2.5 Walls meeting floors

- Floor slabs span z −0.10…0 and end exactly on grid lines. Wall bodies go down to −0.30 and pass through the slab edge, so the solids intersect and no faces are coplanar.
- Skirtings sit on top of the floor. Their bottom faces are coplanar with the floor but face the opposite way and are hidden.
- A floor edge is always under a wall body (≥ 0.15 m of cover), a threshold (built into every door piece, |y| ≤ cap half-width, z 0–0.03) or `Floor_Sill_150` (0.20 wide, z 0–0.015). **Floor materials may therefore change only on grid lines.**
- The part of the body below z = 0 fades to black in vertex colour. Seen from the camera, the south perimeter wall then reads as a diorama section standing on its footing in the void.

### 2.6 Seam rule (replaces the 3 m wobble)

`VKIKit.finish` applies **no global wobble**. Wall builders call this last, before finishing:

```python
def vki_wobble(k, L, fam, variant, holes, top_body_fn, pins=()):
    A = VKI_AMP[fam]            # Timber .012  Stone .022  Ashlar .010  Wattle .020  Board 0
    for v in k.bm.verts:
        if not v[k.body] or abs(abs(v.co.y) - k.T/2) > 1e-4: continue       # only the two body faces
        x, z = v.co.x, v.co.z
        e  = min(smoothstep(0.32, 0.57, abs(x - n)) for n in (0.0, 1.5, 3.0) if n <= L+1e-6)   # zero within 0.32 of every node, including the middle node of a 300
        e *= min([smoothstep(0.0, 0.10, abs(x - p)) for p in pins] or [1.0])  # Timber: pin at the studs
        e *= min([smoothstep(0.0, 0.15, vki_rect_dist(x, z, h)) for h in holes] or [1.0])
        tb = top_body_fn(x)                                                   # cap bottom (sloped on rakes)
        zf = smoothstep(0.16, 0.41, z) * smoothstep(tb, tb - 0.25, z)
        span = int(min(x, L-1e-6) // 1.5)
        seed = zlib.crc32(f"{fam}|{variant if span == 0 else VKI_SECOND[variant]}".encode())
        v.co.y += math.copysign(A * e * zf * vki_vnoise((x - 1.5*span)/0.8, z/0.8, seed), v.co.y)  # outward only
```

- **Ends are flat and identical**, so any two pieces meet exactly whatever their rotation, length, kind or height.
- **No x or z motion.** Caps stay at exactly 1.00 and H, and jambs stay vertical.
- **Outward only:** a prop flush against the nominal face can never show a gap behind it.
- **A 300 piece is exactly 150A ⊕ 150B** (`VKI_SECOND["A"] = "B"`), so a designer can swap one for the other with no visible change.
- **Seeds come from crc32**, never Python's `hash()` of strings, so rebuilds are deterministic across sessions.
- **Vertex density:** `grid_cut(k, vs, step=0.25)` on body panels. Origins sit on nodes, so every piece of a family has identical vertex columns.
- Posts, caps, frames, floors and props do not wobble. `jitter` is allowed only on boxes that touch neither a piece end nor a post envelope.

### 2.7 UV rules

- **World-locked slots** (`FLOOR`, `WALL_A`, `WALL_B`, `BRICK`) use tile t = 1.5 and **zero offset**. `VKIKit.box` skips the centre-hash offset for them (the exterior `Kit.box` applies it even to PLASTER at bevel 0).
- Because origins sit on the lattice, local planar UVs equal world UVs modulo 1. Both wall faces stay continuous under 180° rotations. The proof: a rot-0 −Y face and a rot-180 +Y face both give u = −X_world/t + an integer.
- v = z/t, so Cut equals Full below the cap.
- **Jointed by design:** caps (0.75 m coping units, and timber rails that butt at nodes), posts, reveals, and the insides of hearths.
- **Floors are placed at rotation 0 only** (`vki_rot_lock="world0"`). Plank direction comes from the style (`Boards_NS` / `Boards_EW`).

### 2.8 Vertex colour

`VKIKit.finish(grime=…)` writes `Col` itself. It never uses `Kit.finish`, which would overwrite everything with the 0.62→0.9 m band and leave a 1 m cut wall almost entirely inside it.

| Surface | g |
|---|---|
| Walls and posts, z ≥ 0 | 0.75 + 0.25·smoothstep(0, 0.6, z) |
| Walls, z < 0 (section footing) | 0.75·(0.45 + 0.55·(z+0.30)/0.30), which is 0.34 at −0.30 |
| `CAP` faces with n.z > 0.7 | 1.0 |
| Floors (`grime="floor"`) | 1.0 |
| Props (`grime="prop"`) | 0.85 + 0.15·smoothstep(0, 0.3, z) |
| Undersides (n.z < −0.6) | ×0.72 |
| All faces, last | ×(1 − `vki_dark`), for soot, reveals, fireboxes and hearth fans |
| GLOW faces | `Col = vki_heat` (0 at the rim, 1 at the core), which drives GlowIn's gradient |

**Custom vertex layers:**
- `vki_body` (int), `vki_dark` (float) and `vki_heat` (float) all default to 0, which is neutral.
- Geometry merged through `merge_kit` from plain `Kit` sub-kits is therefore safe.
- `finish` honours a builder's `f.smooth` flag (it does not reset smoothing by material index).

---

## 3. Structure piece list

**Naming:** `SM_VKI_<Class>_<Family>_<Kind>_<Len>[_<Var>]_<Full|Cut>`, with lengths in cm.
- The prefix is `SM_VKI_`, not `SM_VK_`. That keeps these pieces out of `full_rebuild`/`EXTRA_SPECS` by construction.
- Helper and function prefix: `vki_`.

### 3.1 Walls and posts

| Kind | Timber | Stone | Ashlar | Wattle | Board | Notes |
|---|---|---|---|---|---|---|
| `Plain_150A` Full/Cut | ✔✔ | ✔✔ | ✔✔ (no B) | ✔✔ | ✔✔ | |
| `Plain_150B` Full (its cut pair is 150A_Cut) | ✔ brace | ✔ pop-out stones above 1.2, keyed to `T_VKI_StoneIn_stones.json` | – | ✔ bare patch | – | |
| `Plain_300` Full/Cut | ✔✔ | ✔✔ | ✔✔ | ✔✔ | ✔✔ | = A ⊕ B |
| `Window_150` Full/Cut | ✔✔ | ✔✔ (round head) | `Lancet_150` ✔✔ | ✔✔ unglazed | – | |
| `LancetTall_150` Full | – | – | ✔ | – | – | the centre of the chapel's triple lancet |
| `Slit_150` Full | – | ✔ | – | – | – | smithy, cellar |
| `Door_150` Full/Cut | ✔✔ | ✔✔ (round arch) | ✔✔ (pointed) | ✔✔ | ✔✔ | |
| `DoorWide_300` Full/Cut | ✔✔ | ✔✔ (segmental arch) | ✔✔ (pointed, 1.60 clear) | – | – | |
| `Niche_150` Full | – | ✔ | ✔ | – | – | |
| `Rake_150_L/R` | ✔✔ | ✔✔ | ✔✔ | ✔✔ | – | |
| Specials (Full only) | `Fireplace_300` | `Hearth_300`, `Forge_300` | – | – | – | |
| `Post_<fam>_Corner` Full/Cut | ✔✔ | ✔✔ | ✔✔ | ✔✔ | ✔✔ | |
| `Post_<fam>_Mid` Full/Cut | ✔✔ | – | Full only | ✔✔ | ✔✔ | |
| **Count** | **18** | **19** | **17** | **15** | **10** | **79 total** |

Full names follow the pattern, e.g. `SM_VKI_Wall_Timber_Door_150_Cut` and `SM_VKI_Post_Stone_Corner_Full`.

### 3.2 Openings (piece-local; room on −Y)

| Kind | Clear opening | Detail |
|---|---|---|
| Door (Timber, Stone, Board) | x 0.33–1.17 (0.84) × 2.20 | Timber/Board: oak frame and lintel 2.20–2.38. Stone: round arch, spring 1.78, crown 2.20, voussoirs in STONE_BLOCK_IN within x 0.25–1.25. |
| Door (Wattle) | 0.84 × 2.00 | crooked lintel |
| Door (Ashlar) | `lancet_pts(0.33, 1.17, 0, 1.85)`, apex ≈ 2.45 | DRESS surround |
| Door, all | | threshold 0.03 built in; leaf socket (0.33, −T/2+0.05, 0); `vki_leaf_open_deg=100` toward −Y |
| **Door_Cut** | same | jambs end at 1.00 with the cap wrapping the reveal; threshold; **no leaf by default** |
| DoorWide_300 | x 0.60–2.40 (1.80) × 2.40 | Stone: segmental crown 2.55. Ashlar: x 0.70–2.30 (1.60), spring 2.20, apex ≈ 3.44, the same as the exterior chapel door. |
| Window (Timber, Stone) | glass x 0.45–1.05 at y +0.10, splayed to x 0.33–1.17 at face A; **sill top 1.00**, head 2.25 | Glass is a closed 0.02 box in the WINDOW slot, which becomes Window_Day on every VKI master. Timber: oak lintel, and interior shutters folded into the splay (SHUTTER slot, so they take the exterior shutter style). Stone: round head, StoneBlockIn sill. |
| **Window_Cut** | | cut plain wall whose cap over x 0.33–1.17 is replaced by a sill slab ±0.33, top 1.00, paler, so the window still reads in the near wall; plus a light-pool anchor |
| Window (Wattle) | x 0.45–1.05, z 1.00–1.60, unglazed | 2 rods; top-hung board shutter propped open 55° inward, inside the zone; a daylight card at y +0.10 (WINDOW slot → `M_VKI_Daylight`) |
| Lancet / LancetTall | glass x 0.45–1.05 at y +0.15; sill 1.00; spring 3.00 / 3.30 (apex ≈ 3.55 / 3.90); splayed to 0.33–1.17 | STAINED → Stained_In; DRESS surround inside the zone |
| Slit | glass x 0.66–0.84, z 1.20–2.30; splayed to 0.40–1.10 | |
| Niche | x 0.45–1.05, z 1.00–1.70, 0.20 deep, with a shelf | |
| Fireplace_300 (Timber) | firebox x 0.90–2.10, z 0–1.00, back at y −0.20 | Chimney breast x 0.40–2.60 projecting to y −0.85: plaster hood (`WALL_A`), oak bressumer at 1.4, brick firebox (BRICK). Also: hearthstone x 0.35–2.65, y −1.45…−0.85, z 0–0.03; crane and cauldron, firedogs, logs, GLOW embers; soot fan in `vki_dark`. Light socket (1.5, −0.6, 0.5). |
| Hearth_300 (Stone) | firebox x 0.50–2.50 × 1.20 | inglenook-style breast; spit with a goods-atlas roast, cauldron, settle-free hearth slab; 2 sockets |
| Forge_300 (Stone) | raised hearth x 0.40–2.60, y −1.45…−0.25, top 0.85 | Built from `smithy_chimney`'s hearth: coal bed with graded GLOW, hood tapering into the wall top, tuyere on the −X side, fire irons, bucket. Sockets: forge (1.5, −0.85, 1.3) at 450–900 W, bed glow at 0.95 m, 150 W. |

### 3.3 Floors, links, leaves and other structure

| Piece | Footprint / origin | Notes | Owner |
|---|---|---|---|
| `SM_VKI_Floor_150`, `_300`, `_600` | [0,S]², min-corner node, any node | slab z −0.10…0, no bevel, `FLOOR` slot, `grime="floor"`, `rot_lock world0`, ≤ 24 tris | core |
| `SM_VKI_Floor_Sill_150` | along +X, centred on a grid line | oak or StoneBlockIn strip 0.20 × 0.015 | core |
| `SM_VKI_Floor_Dais_150`, `_300` | min corner | top 0.20 (buries the skirting); nosing STONE_BLOCK_IN or DRESS with a pale chamfer | PKG-L |
| `SM_VKI_Floor_HearthApron_300x150` | min corner | flags, soot fan, ash spill, z 0–0.02 | PKG-L |
| `SM_VKI_Stair_Up_150x450_RailR/L` | min corner; rot 0 rises along +Y; allowed rotations 0 / ±90, **never 180** | 15 risers × 0.20 = 3.00, going 0.28, flight x 0.27–1.25 against the wall, closed spandrel, rail 0.95 on the open side (R = rail on +X), pale nosings. Top two treads darkened 0.6 in `vki_dark`, plus a 1.5 × 0.6 upper-floor lip at z 3.0 over the top against the far wall. **Used, not climbed.** | PKG-L |
| `SM_VKI_Stair_Down_150x450_RailR/L` | same origin and rotation as the Up piece it pairs with | Hole x 0.27–1.27, y 0.10–4.25, framed by oak trimmers (WOOD, no `FLOOR` faces). Treads descend **from the north end toward −Y** to −2.0, with a VOID pit below; risers face the camera. Rails on the open side of the two southern cells and across the south end; the top cell's open side is left open for arrival. | PKG-L |
| `SM_VKI_Ladder_Up_H24`, `_H30` | wall-backed, cell centre | ladder to the wall top with a dark loft or hatch lip | PKG-L |
| `SM_VKI_Trapdoor_150` | min corner, rot 0 | 0.9 × 0.9 hatch with the leaf standing open toward +Y (away from the camera); rungs into VOID; the rest of the cell uses the `FLOOR` slot | PKG-L |
| `SM_VKI_Apron_300x150` | centred on the exit's grid segment, outside | exterior ground (styles Cobble, Dirt, Grass via `floor`), fading to black over the outer 0.5 m; doorstone | PKG-L |
| `SM_VKI_Beam_Stubs_150` | wall-mounted | two oak joist ends 0.16 × 0.20 projecting 0.20 at z H−0.30, x 0.45 and 1.05; implies a ceiling | PKG-L |
| `SM_VKI_Leaf_Plank_Full` / `_Cut` | hinge at the origin, extends +X | 0.84 × 2.20 / 0.84 × 0.95 (capped top), 0.08 thick, strap hinges 0.08; `hinge_axis="local Z"` | core |
| `SM_VKI_Leaf_Arch_Full` | same | stone round-headed door leaf | PKG-S |
| `SM_VKI_Leaf_Wide_L_Full` / `_R_Full` | same | 0.90 × 2.40 each | PKG-S |
| `SM_VKI_Leaf_Wattle_Full` | same | hurdle leaf, 0.84 × 2.00 | PKG-W |
| `SM_VKI_Leaf_Lancet_Full` | same | pointed leaf | PKG-W |
| `SM_VKI_Leaf_LancetWide_L_Full` / `_R_Full` | same | pointed double leaves | PKG-W |
| `SM_VKI_FX_DoorSpill` | exit segment | 1.2 × 1.6 floor trapezoid, FX slot | PKG-L |
| `SM_VKI_FX_WindowPool` | per window | floor light pool, FX slot | PKG-L |
| `SM_VKI_FX_Shaft_Window` | per window | tapered prism, P2 | PKG-L |
| `SM_VKI_Test_Axis` | | red +X, green +Y, blue +Z; **not shipped** | core |

Structure total: 79 walls and posts + 4 core floors + 9 links (Up/Down ×4, 2 ladders, trapdoor, apron) + 2 dais + hearth apron + beam stubs + 8 leaves + 3 FX ≈ **107 masters**, plus the test piece.

**Master metadata:**
- Builders write `k.meta`. `VKIKit.finish` stores it on the object as `vki_*` custom properties (JSON strings for lists and dicts), and `vki_rebuild` copies it to the master.
- The source of truth is code; a JSON export comes later with the FBX export.

| Property | Values / example |
|---|---|
| `kit`, `grid_m` | "VillageInterior", 1.5 |
| `vki_class` | wall / post / floor / link / leaf / prop / fx |
| `vki_family`, `vki_kind`, `vki_len`, `vki_height` | family name, kind, length, "Full" / "Cut" / "Rake" |
| `vki_thick`, `vki_origin`, `vki_rot_lock` | |
| `vki_footprint` | "x0,y0,x1,y1" |
| `vki_fp_cells` | "w,d" |
| `vki_collider` | boxes; walls: body footprint, z 0–2.2 for **both** Full and Cut |
| `vki_nav` | block / walk / none |
| `vki_cut_pair`, `vki_opening` | |
| `vki_leaf_socket`, `vki_leaf_open_deg` | |
| `vki_trigger`, `vki_spawn_local` | defaults for link pieces |
| `vki_lights` | socket list |
| `vki_fx` | anchor list |
| `vki_mount`, `vki_mount_zmin`, `vki_back_y` | mounting rules |
| `vki_use` | use points [(x, y, facing_deg), …] |
| `vki_uv_lock` | |
| `hinge_axis` | leaves, lids, flaps |

---

## 4. Textures and materials

### 4.1 Slots

`VKIKit.finish` appends `kit_mats()` (55 slots) plus `vki_mats()` (11), giving **66 slots**.

| Index | Slot | Tile | Notes |
|---|---|---|---|
| 55 | `FLOOR` | 1.5, world-locked | style key `floor` |
| 56 | `WALL_A` | 1.5, world-locked | style key `wall_a` |
| 57 | `WALL_B` | 1.5, world-locked | style key `wall_b`; defaults to the same material as `WALL_A` |
| 58 | `CAP` | 1.2, grain along the long axis | style key `cap` |
| 59 | `STONE_BLOCK_IN` | 1.5 | |
| 60 | `BRICK` | 1.5, world-locked | |
| 61 | `STRAW` | 1.5 | |
| 62 | `ASH` | 0.75 | |
| 63 | `TEXTILE` | own UVs | |
| 64 | `WAX` | 1.0 | |
| 65 | `FX` | own 0–1 UVs | |

**Per-master slot defaults** (`k.slot_mats`) are baked into each master's material list. That is how a Stone master shows StoneIn in its `WALL_A` slot with no style applied.

**Every VKI master also overrides four exterior slots:**
- `GLOW` → `M_VKI_GlowIn`
- `WINDOW` → `M_VKI_Window_Day`
- `STAINED` → `M_VKI_Stained_In`
- `DRESS` → `M_VKI_Dress`

**Whitelisted per-master overrides:** `WATER` (→ WaterMurky or Ale), `WOOD`, `PLANKS`, `SHUTTER`, `CLOTH_A`, `CLOTH_B`.

**Banned on VKI masters** (exterior weathering or wrong tile): STONE, PLASTER, ASHLAR, FIELDSTONE, WATTLE, STONE_BLOCK, ROCK, MOSS, ROCK_MOSSY. `rock()` must be passed `mi=STONE_BLOCK_IN`.

**Variants** (Blender):
- `vki_variant_mesh(piece, style)` → `VARI_<crc32(piece + sorted style JSON)>`. The mesh carries `vki_base` and `vki_style` properties, so a refresh never depends on hashes.
- `VKI_SLOT`: floor 55, wall_a 56, wall_b 57, cap 58, wood 2, planks 23, shutter 10, cloth 11, cloth_b 12, window 4, glow 9, water 18.
- **Existing exterior props placed indoors** get `{glow: GlowIn, window: Window_Day}`. That removes the white blobs on `Prop_Lantern`, `Prop_Forge` and `Prop_Campfire`.
- `vki_refresh_variants()` must run after any exterior `full_rebuild`, which only refreshes `VAR_*` meshes.
- In Unity a style becomes a prefab variant with one material override.

### 4.2 Generators

New text `vki_tex` (`src/textures/vki_tex.py`), executed after `vk_tex`, `vk_texgen`, `vk_tex2` and `vk_mat`:
- **Copies, never edits, of the exterior generators**, so exterior textures stay bit-identical.
- Paint at S = 2048, store at 1024 via `down2`.
- `write_set(prefix, bc, h, R, depth, T, ao=cavity_ao(h,(2,6,18),(2.0,1.5,0.8),0.45), ao_in_albedo≈0.35)`.
- `paint_form_light` at a light touch (hig 0.10–0.15, log 0.16–0.22, post 0.2–0.3).
- No moss or lichen. Lines at least 1 cm; at least 12 elements per tile; no standout feature.
- One generator per MCP call.

| Output | Function (params) | T | Recipe |
|---|---|---|---|
| `T_VKI_Boards_NS`, `_EW`, `_NS_B/_C`, `_EW_B/_C` | `vki_gen_floorboards(S=2048, seed=611, T=1.5, depth=.02, nb=6, orient="NS", variant=0)` | 1.5 | 6 boards of 0.25 m; 2 butt joints per board per tile, joints ≥ 0.12 m apart; treenails only at joints (no nail rows); 25% knots of 1.5–2.5 cm; 8% old-grey boards; ramp `#3A2414 / #74492A / #A07448`; gaps `#2A1C12`. EW transposes the layout **before** painting. Variants B and C redraw only interior segments (edge-locked). |
| `T_VKI_PlasterIn` | `vki_gen_plaster_in(S=1024, seed=23, T=1.5, depth=.015, blot=.2)` | 1.5 | `gen_plaster` with **no cracks** and no brick patches |
| `T_VKI_StoneIn` (+ `_stones.json`) | `vki_gen_stone_in(L=stone_layout(10, T=1.5, lacing=False, NC=4), mortar="#857B6C")` | 1.5 | `gen_stone` with courses = `len(L['H'])` (about 0.375 m), moss and lichen steps removed |
| `T_VKI_AshlarIn` / `T_VKI_Flagstone` | `vki_gen_blocks(seed=14 / 15, T=1.5, nrow=3, blocks=(3,2,3) / (2,3,2), pal, mortar, chip)` | 1.5 | generalised `vk_tex2.gen_ashlar`: 0.5 m courses; flags 0.5–0.75 m with dark mortar about 8 mm |
| `T_VKI_FlagRustic` | `vki_gen_flagrustic(seed=33, T=1.5, aspect=1.0, prot=(.010,.018), joint="#4A3A2C")` | 1.5 | `gen_fieldstone` without moss or lichen; packed-earth joints with pebbles |
| `T_VKI_Earth` / `T_VKI_EarthSooty` | `vki_gen_earthfloor(seed=456, T=1.5, rushes=1.0/0.2, soot=0/1)` | 1.5 | `gen_dirt_v2` without grass; rushes 0.12–0.32 m long with drop shadows; strewing herbs. Sooty adds charcoal specks, ash haze and iron-scale flakes. |
| `T_VKI_StrawBed` | `vki_gen_strawbed(seed=97, T=1.5)` | 1.5 | about 900 flat strands; calm (not `gen_straw`) |
| `T_VKI_WattleIn` | `vki_gen_wattle_in(T=1.5, nst=6, nrod=28)` | 1.5 | both counts even so the weave wraps |
| `T_VKI_StoneBlockIn` | `vki_gen_stoneblock_in(seed=18, T=1.5)` | 1.5 | no lichen, no crack |
| `T_VKI_Brick` | `vki_gen_brick(seed=621, T=1.5, nr=20, nbk=6)` | 1.5 | running bond, `nr` even; 10% overfired bricks; soot goes in vertex colour |
| `T_VKI_Ash` | `vki_gen_ash(S=1024, seed=631, T=0.75)` | 0.75 | no embers (embers are GLOW geometry) |
| `T_VKI_Textiles` (PKG-L) | `vki_gen_textiles_atlas(S=2048, seed=950)` in text `vki_textiles` | own UVs | 2 × 4 cells, each 2:1: rug_madder, rug_indigo, runner (periodic in u), hanging_heraldic, tapestry_millefleur, quilt_patch, blanket_wool, altar_frontal. The cell order `VKI_TEXTILE_CELLS` and `vki_textile_map()` live in core. |

### 4.3 Materials

Built by `vki_mats()` and `VKI_MAT_MAP`:
- If a texture is missing, the material is a flat placeholder.
- `vki_apply_mats()` rebuilds only the VKI entries in place. **Never call `apply_pbr_all`.**

| Style key | Name → texture / tint |
|---|---|
| floor | Boards_NS (default), Boards_EW, Boards_NS/EW_B/_C; BoardsDark_NS/EW (.70,.62,.58); BoardsPale_NS/EW (1.10,1.05,.95); Flag; FlagWarm (1.04,1,.93); FlagRustic; Earth; EarthSooty; Straw; Apron Cobble/Dirt/Grass (existing terrain `_BC` images, if tile-safe) |
| wall_a / wall_b | PlasterWhite (1.08,1.08,1.10), PlasterCream (1,1,1), PlasterDaub (.80,.65,.47), PlasterOchre (1.03,.84,.56), PlasterRed (.78,.42,.33); StoneIn plus Warm/Cool/Dark (mirroring the exterior stone styles); AshlarIn; WattleIn; BoardsV; Brick |
| cap | Hewn (existing `M_VK_Hewn`), StoneBlockIn, Dress, PlasterDaub |
| wood | Oak (`M_VK_Wood`), Dark (`M_VKI_WoodDark`, tint .62,.55,.50) |
| overrides | GlowIn, Window_Day, Daylight, Stained_In, Dress, WaterMurky, Ale |

| Material | Definition |
|---|---|
| `M_VKI_GlowIn` | emission = mix((.85,.28,.05), (1.0,.72,.30), Col.r); strength 1.2→2.2; dark base colour |
| `M_VKI_Window_Day` | `lit_window_material("M_VKI_Window_Day", warm=(.78,.86,1.0), strength=1.0)` |
| `M_VKI_Daylight` | flat emissive (.80,.86,.95) at 0.8 |
| `M_VKI_Stained_In` | `pbr_material(prefix="T_VK_Stained", emission=1.8)` |
| `M_VKI_Dress` | `T_VKI_StoneBlockIn` × `DRESS_TINT` |
| `M_VKI_Wax` | flat (.93,.88,.74), roughness .5; also the foam on tankards |
| `M_VKI_Ale` | flat (.45,.28,.08) |
| `M_VKI_WaterMurky` | `T_VK_Water` × (.55,.50,.40) |
| `M_VKI_FX_Light` | emission (1,.93,.78) × (1−v)² at 0.6, alpha-blended 0.15, no shadows. Set the blend mode by reading the valid enum values at runtime. |

**Reused unchanged:** Wood, Planks (furniture only), PaintedWood shutters, Iron, Bronze, Steel, Cloth tints, Burlap, Paper, Goods atlas, Water, EndGrain, Bark, Coal, Hide, Void, Hewn, Clay.

**Palette targets:**
- Floor luma 0.25–0.45, low saturation.
- Limewash 0.60–0.80.
- Caps 0.45–0.60, which must be ≥ floor + 0.15 (test T12).
- Only textiles, painted wood, glass and fire are saturated.

---

## 5. Furniture and dressing

**Conventions:**
- Build to P3's exaggerated scale:

  | Element | Kit size |
  |---|---|
  | Table top | 0.10 thick at 0.80 |
  | Form seat | 0.08 thick at 0.48 |
  | Legs | 0.12–0.14, splayed 5–8° |
  | Mattress | 0.25 |
  | Straps | 0.045 |
  | Candles | Ø 0.06 × 0.20 |
  | Tankard | 0.16 |
  | Round things | 16 segments |

- Pale HEWN edge bevels on tops.
- Tops get the detail budget. Floor contact is flat, with no jitter on feet.
- `grime="prop"`.
- Footprints are in cells (`vki_fp_cells`). Wall-backed props put their back at local y = +(d·0.75 − 0.25).
- Table dressing has its origin at the table-top surface (z 0.80).

**Budgets:**

| Category | Tris |
|---|---|
| Furniture | ≤ 1500 (hard limit 2000) |
| Dressing | ≤ 400 |
| Hero pieces | ≤ 6000 |

### 5.1 Homes (PKG-H, text `vki_props_home`)

| Priority | Pieces (W × D × H, footprint) |
|---|---|
| **P1** | `Table_Trestle_300` 3.0×0.9×0.80 (2×1) · `Table_Trestle_150` 1.5×0.9×0.80 (1×1) · `Table_Small` 1.1×0.75×0.78 · `Form_300` / `Form_150` ×0.35×0.48 · `Settle_300` 3.0×0.6×1.2 (2×1) · `Chest` 1.1×0.6×0.65 (SHUTTER panels) · `Bed_Straw` 0.9×2.0×0.45 (1×2) · `Bed_Box` 1.2×2.1×1.8 (1×2, north or side wall only) · `Bed_HalfTester` 1.7×2.3×2.2 (2×2, canopy over the head only) · `Shelf_Wall_150` (wall, boards at 1.3/1.7) · `PegRail_150` (wall, 1.7) · `Dresser_130` 1.3×0.5×1.9 · `Pantry_Shelves_300` 2.9×0.5×1.9 (2×1, goods atlas) · `Barrel` r0.4×1.0 · `Barrel_Water` · `Crate` 0.75³ · `Jars_Cluster` 0.9×0.6×0.7 · `LogBasket` 0.8×0.6×0.6 · `Firewood_150` · `Hearth_Open` 1.3×1.3×1.2 (1×1: kerb, ASH bed, graded GLOW embers, logs, tripod pot, light socket) · `Desk_Merchant` 1.5×0.75×1.1 · `Counter_Shop_300` 3.0×0.75×1.0 (`ShopGoods_*` snap at z 1.0) · `Tapestry_300` (wall, rod at 2.8) · `TableDress_Meal_A/B` |
| **P2** | `Barrel_Lying` · `Washstand` · `Aumbry` · `Chair_Box` · `Strongbox` · `Quern` · `WaterPail` · `Basket_Apples` / `_Wool` · `Hurdle_150` · `Manger_150` |
| **P3** | `Cradle` · `ButterChurn` · `WashTub` |

### 5.2 Tavern and lighting (PKG-T, text `vki_props_tavern`)

| Priority | Pieces |
|---|---|
| **P1** | `Bar_Counter_150` 1.5×0.7×1.05 (dark plank front, 0.12 top with a pale front edge, foot rail) · `Bar_End_150` (flap, `hinge_axis="local Y"`) · `Bar_Corner_150` · `CaskRack_150` 1.3×0.9×1.2 (taps toward −Y) · `Table_Barrel` Ø0.9×1.05 · `TableDress_Tavern_A/B/C` (tankards with WAX foam discs, platter, dice) · `Oven_150` 1.3×1.3×1.9 (brick dome, GlowIn mouth, flue into the wall) · `Kitchen_Worktable_150` 1.5×0.8×0.85 · `Candle_Plate` · `Candlestick` · `CandleCluster` · `Sconce_Wall` · `Lantern_Wall` (GlowIn) |
| **P2** | `Stillage_300` · `BackBar_300` · `MeatRail_150` (wall, 2.2) · `NoticeBoard` |
| **P3** | `Chandelier_Wheel` (`vki_cam_fade`) · `Trophy_Antlers` |

### 5.3 Smithy and workshops (PKG-S, text `vki_props_smithy`)

| Priority | Pieces |
|---|---|
| **P1** | `Workbench_300` 3.0×0.8×0.9 (leg vice) · `QuenchTrough_150` 1.5×0.6×0.7 (STONE_BLOCK_IN; WATER→WaterMurky) · `CoalBin_150` 1.5×0.9×0.7 (bevelled flat-shaded lumps, not subdivision-1 icospheres) · `IronStock_150` 1.5×0.6×1.2 · `ToolWall_150` (wall, board 1.1–2.3) |
| **P2** | `GoodsRack_Smith_150` 1.5×0.4×1.8 · `Workbench_Carpenter` · `PoleLathe` |

### 5.4 Chapel (PKG-L, text `vki_props_chapel`)

| Priority | Pieces |
|---|---|
| **P1** | `Pew_300` 3.0×0.6×0.95 (dark oak, poppyheads, kneeler) · `Altar_150` 1.8×0.9×1.0 (DRESS block, textile frontal, linen, cross, 2 candlesticks) · `AltarRail_150` (edge piece on the dais, y 0.02–0.32) · `CandleStand_Pricket` Ø0.6×1.4 · `Lectern` 0.6×0.6×1.3 · `Font` Ø1.0×1.1 · `VotiveRack` 1.0×0.4×1.0 · `Sedilia_150` |
| **P2** | `Pew_150` · `WallBench_150` (stops 0.33 short of nodes) · `Rug_225x150` · `FurRug` |
| **P3** | `Retable_300` (needs a painted atlas cell) · `Statue` |

**Overlays**, also PKG-L: `Rug_300x200`, `Runner_300` (chains along the aisle), `RushMat` (at every exit). These are 2–4 cm real geometry with 1 cm bevels, textured from the textile atlas.

### 5.5 Existing props reused by name

Masters stay in `VK_Pieces`. Mount offsets live in `VKI_REUSE`:

| Piece | Footprint | Mounting / note |
|---|---|---|
| `Prop_Loom` | 2×2 | north wall |
| `Prop_SpinningWheel` | 1×1 | |
| `Prop_Anvil` | 1×1 | |
| `Prop_Bellows` (industry version) | 2×1 | nozzle is −X, so place at rot 180 west of a forge |
| `Prop_Grindstone` | 1×1 | |
| `Prop_WeaponRack`, `Prop_ArmorStand` | 1×1 | north wall |
| `Prop_AleCask` | 1×2 | |
| `Prop_BarrelStack` | 2×1 | side wall |
| `Prop_Sacks`, `Pile_Sacks_1` | 1×1 | |
| `Prop_DryingRack_Herbs` / `_Meat`, `Prop_BreadRack` | | |
| `Prop_ShopGoods_*` | | z 1.0 |
| `Prop_Bedroll`, `Prop_Stool` | | |
| `Prop_Lantern` | | origin 0.10 in front of the face |
| `Banner_Wall` | | origin on the grid line |
| `Prop_ToolWall` | | origin at grid line − 0.24 |

---

## 6. Showcase interiors

**Legend.** Each cell is 2 characters.

| E–W walls (on `+` lines) | N–S walls (between cells) | Meaning |
|---|---|---|
| `##` | `#` | Full |
| `==` | `:` | Cut |
| `WW` / `ww` | `W` | Window Full / Cut |
| `DD` / `dd` | `D` | Door Full / Cut |
| `ee` | – | exit: Door_150_Cut + Apron + DoorSpill + RushMat + link |
| `ee+ee` | – | DoorWide_300_Cut exit |
| `FF+FF` | – | Fireplace / Hearth / Forge (300) |
| `SS` | `S` | Slit |
| `LL` / `LT` / `ll` | `L` | Lancet / LancetTall / Lancet Cut |
| `rr` | `r` | rail (rails are part of the stair pieces; `rr` on the chapel dais is AltarRail) |
| – | `t` | Rake, low end at the south |

`+` marks a node; the assembler places posts by the §2.3 rule.

**Cells:**
- Spawns: `Sf` front, `Ss` stair, `Sc` cellar.
- Stairs and access: `^^` stair up, `vv` stair down, `td` trapdoor, `LA` ladder.
- Hearths and furniture: `fp`/`fg` hearth zone of the wall piece; `HH` open hearth; `BD` box bed or half-tester; `bd` straw bed; `CH` chest; `DR` dresser; `SH` wall shelf; `PN` pantry shelves; `TB` table set; `tb` small table; `bn` form or settle; `bt` barrel table; `rg` rug; `WP` log basket; `ba` barrel; `bx` crate; `sk` sacks.
- Crafts, tavern and smithy: `SW` spinning wheel; `LM` loom; `CT` bar counter; `CE` bar end with flap; `CK` cask; `OV` oven; `WB` workbench or worktable; `BS` barrel stack; `BL` bellows; `QT` quench trough; `CO` coal bin; `AN` anvil; `GS` grindstone; `WR` weapon rack; `AS` armour stand; `ir` iron stock.
- Chapel: `PW` pew; `AL` altar; `cd` pricket stand; `LC` lectern; `sd` sedilia; `FT` font; `vr` votive rack.

**Hovel: `VKI_Hovel_F0`.** 5×5 cells (7.5 × 7.5 m). Wattle, daub. Floor Earth. Fit camera, D = 17.
```
      0  1  2  3  4
     +##+WW+##+WW+##+
   4 #PN sk CH BD BD#
     +              +
   3 W.. .. .. .. SH#
     +              +
   2 #TB .. HH .. ..#
     +              +
   1 #TB .. .. .. ..#
     +              +
   0 tWP .. Sf bd bdt
     +==+==+ee+==+ww+
```

**Cottage: `VKI_Cottage_F0`.** 6×5 cells (9 × 7.5 m). Timber, PlasterCream or Daub, following the exterior. Hall FlagRustic, bedroom Boards_NS. Fit, D = 18.
```
      0  1  2  3  4  5
     +##+WW+FF+FF+##+WW+
   4 #LM LM fp fp#DR BD#
     +           +     +
   3 #LM LM rg rgD.. BD#
     +           +     +
   2 #.. .. .. ..tCH ..W
     +           +==+==+
   1 #TB TB .. SW .. PN#
     +                 +
   0 tTB TB Sf .. .. bat
     +==+ww+ee+==+ww+==+
```

**Townhouse, ground floor: `VKI_Townhouse_F0`.** 7×5 cells. Timber, PlasterWhite; the kitchen's walls take `wall_a=StoneIn`. Floors: entry and hall Flag; shop Boards_EW; kitchen FlagRustic. The stair `Stair_Up_150x450_RailR` sits at rot 0, origin (0, 3.0).
```
      0  1  2  3  4  5  6
     +##+WW+FF+FF+WW+##+WW+
   4 #^^rDR fp fp bn#PN OV#
     +  +           +     +
   3 #^^r.. rg rg bnD.. ..W
     +  +           +     +
   2 #^^r.. TB TB ..tba WB#
     +  +     +==+==+==+==+
   1 #Ss .. ..D.. CT CT SH#
     +        +           +
   0 tCH Sf ..tbx .. .. bxt
     +==+ee+==+==+ww+ww+==+
```

**Townhouse, upper floor: `VKI_Townhouse_F1`.** Timber, PlasterCream. Solar Boards_NS, bedchamber BoardsDark_NS. `Stair_Down_150x450_RailR` uses the same origin and rotation as the stair below.
```
      0  1  2  3  4  5  6
     +##+WW+##+WW+##+WW+##+
   4 #vv Ss LM LM#DR BD BD#
     +  +        +        +
   3 #vvr.. LM LM#.. BD BDW
     +  +        +        +
   2 #vvr.. .. ..D.. .. CH#
     +rr+        +        +
   1 #SW .. TB TB#.. .. tb#
     +           +        +
   0 tCH .. .. ..t.. bd bdt
     +==+ww+==+==+==+ww+==+
```

**Tavern, ground floor: `VKI_Tavern_F0`.** 9×7 cells (13.5 × 10.5 m). Follow camera, D = 18.
- Walls: Timber, PlasterCream, wood Dark. The hearth is the Stone `Hearth_300`, with Corner posts where the family changes.
- Floors: hall BoardsDark_EW; Flag on cells (1–4, 5–6), behind the bar (8, 0–3) and in the kitchen.
- Bar: counters face west.
```
      0  1  2  3  4  5  6  7  8
     +##+##+FF+FF+WW+##+WW+##+##+
   6 #^^rWP fp fp WP DR#td PN OV#
     +  +              +        +
   5 #^^r.. bn bn tb ..tSc .. WB#
     +  +              +==+dd+==+
   4 #^^rtb .. .. .. .. .. .. ..#
     +  +                       +
   3 #Ss TB TB .. TB TB .. CE CK#
     +                          +
   2 #bt TB TB .. TB TB .. CT CK#
     +                          +
   1 W.. .. .. .. .. .. .. CT CK#
     +                          +
   0 tbx .. .. .. Sf .. .. CT bxt
     +==+ww+==+==+ee+==+ww+==+==+
```

**Tavern guest floor: `VKI_Tavern_F1`.** Perimeter Timber; partitions Board. Corridor BoardsDark_EW, rooms Boards_NS.
```
      0  1  2  3  4  5  6  7  8
     +##+##+WW+##+##+##+WW+##+##+
   6 #vv Ss#CH BD BD#DR CH BD BD#
     +  +  +        +           +
   5 #vvr..D.. .. tb#.. .. BD BDW
     +  +  +        +           +
   4 #vvr..t.. .. ..t.. .. .. tb#
     +rr+  +==+==+==+==+dd+==+==+
   3 #.. .. .. .. .. .. .. .. ..#
     +==+dd+==+==+dd+==+==+dd+==+
   2 Wbd .. bd#bd .. bd#bd .. bdW
     +        +        +        +
   1 #bd .. bd#bd .. bd#bd .. bd#
     +        +        +        +
   0 tCH .. tbttb CH ..ttb .. CHt
     +==+ww+==+==+ww+==+==+ww+==+
```

**Tavern cellar: `VKI_Tavern_B1`.** 6×5 cells. Stone (Dark), FlagRustic. The scene origin corresponds to F0 (4.5, 3.0), so the ladder cell (3,4) lies under the trapdoor at F0 (6,6).
```
      0  1  2  3  4  5
     +##+SS+##+##+##+##+
   4 #CK CK CK LA PN PN#
     +                 +
   3 #CK CK CK Sc .. ..S
     +                 +
   2 #BS .. .. .. .. bx#
     +                 +
   1 #BS .. .. .. .. bx#
     +                 +
   0 t.. sk sk .. .. bat
     +==+==+==+==+==+==+
```

**Smithy: `VKI_Smithy_F0`.** 7×5 cells. Stone (Dark); the store partitions are Board.
- Floor EarthSooty, with FlagRustic on cells (1–5, 2–4) bounded by sill strips.
- Work cells (3,3) and (4,3) run forge → anvil → quench laterally, so nothing hides the smith.
- The bellows sit at rot 180. `WB` is `Workbench_300` along the east wall, with `ToolWall_150` above it.
- The exit is a DoorWide; `Sf` lies on its centre line, x = 6.0.
```
      0  1  2  3  4  5  6
     +##+WW+##+FF+FF+WW+##+
   4 #WR BL BL fg fg CO AS#
     +                    +
   3 #.. .. AN .. .. QT WB#
     +                    +
   2 W.. .. .. .. .. .. WB#
     +==+==+              +
   1 #bx irD.. .. .. GS ..#
     +     +              +
   0 tsk skt.. .. Sf .. ..t
     +==+==+==+ee+ee+ww+==+
```

**Chapel: `VKI_Chapel_F0`.** 7×11 cells (10.5 × 16.5 m). Follow camera.
- Ashlar. Nave floor FlagWarm with `Runner_300` down column 3. Dais (+0.20) on rows 8–10, floored Flag with DRESS nosing.
- The triple lancet on the north wall is centred on the aisle. The altar rail has a gap at the aisle.
```
      0  1  2  3  4  5  6
     +##+##+LL+LT+LL+##+##+
  10 #CH cd .. AL .. cd sd#
     +                    +
   9 L.. .. .. .. .. .. ..L
     +                    +
   8 #.. .. .. .. LC .. ..#
     +rr+rr+rr+  +rr+rr+rr+
   7 #.. .. .. .. .. .. ..#
     +                    +
   6 L.. PW PW .. PW PW ..L
     +                    +
   5 #.. PW PW .. PW PW ..#
     +                    +
   4 L.. PW PW .. PW PW ..L
     +                    +
   3 #.. PW PW .. PW PW ..#
     +                    +
   2 L.. PW PW .. PW PW ..L
     +                    +
   1 #.. PW PW .. PW PW ..#
     +                    +
   0 tFT .. .. Sf .. vr ..t
     +==+ll+==+ee+==+ll+==+
```

**Links:**

| Scene | Link id → target |
|---|---|
| Hovel, Cottage, Smithy, Chapel | `front` → `@return` |
| Townhouse_F0 | `front` → `@return`; `stairA` → `VKI_Townhouse_F1` |
| Townhouse_F1 | `stairA` → `VKI_Townhouse_F0` |
| Tavern_F0 | `front` → `@return`; `stairA` → `VKI_Tavern_F1`; `cellar` → `VKI_Tavern_B1` |
| Tavern_F1 | `stairA` → `VKI_Tavern_F0` |
| Tavern_B1 | `cellar` → `VKI_Tavern_F0` |

**Which exterior uses which interior** (the stamping happens later, with the export):

| Exterior builder | Interior |
|---|---|
| `build_hovel` | Hovel |
| `build_house_v`, 1 storey | Cottage |
| `build_house_v` with 2+ storeys, and the town houses | Townhouse |
| `build_inn`, `build_tavern` | Tavern |
| `build_smithy` | Smithy (its exterior door is blocked by `Smithy_Chimney`; that is a separate exterior fix) |
| `build_chapel` | Chapel |

**Blender layout:**
- One scene per floor, as named above, plus `VKI_Test` (seam rigs) and `VKI_LookTest`.
- Each scene has collections `VKI_<S>_Shell`, `_Props`, `_Logic` (spawns, root, light and FX anchors) and `_Lights`, all under its own scene collection. Always pass an explicit collection: `vcol` defaults to the VillageKit scene.
- Scenes copy VillageKit's engine, EEVEE settings and view transform/look/exposure. Each gets its own world, `W_VKI_Day` / `W_VKI_Night`: camera rays see void `#0B0908` via Light Path "Is Camera Ray"; lighting colour per preset. **Never edit `MC_World` or `VK_Sun`.**
- Scenes are rebuilt entirely by `vki_build_scene(name)` / `vki_build_all()`. Never hand-edit them.

**Unity metadata:**

| Where | Properties |
|---|---|
| Link instances | `vki_link` (exit / door / stair_up / stair_down / ladder_up / trapdoor), `vki_link_id`, `vki_target` (scene or `@return`), `vki_prompt`, `vki_trigger` "[cx,cy,cz,sx,sy,sz]" in piece-local coordinates, `vki_facing_min`=60 |
| Spawn empties `SPN_<id>` (single arrow) | `vki_spawn_id`, `vki_facing_deg` as a compass value (0 = +Y north, 180 = toward the camera) |
| `VKI_Root` | `vki_building`, `vki_floor`, `vki_cam_mode`, `vki_cam_dist`, `vki_cam_pitch`=50, `vki_cam_yaw`=0, `vki_bounds`, `vki_default_spawn` |
| `LGT_*` empties | `vki_light` JSON {type, color, intensity (relative), range, flicker, shadows, blender_w} |
| `FXA_*` empties | `vki_fx` (fire_small / fire_large / forge_sparks / candle / smoke / dust_motes / steam) |

**Trigger and spawn defaults:**

| Link | Trigger | Spawn |
|---|---|---|
| Door | (0.75, −0.65, 1.0), size (0.9, 0.8, 2.0) | (0.75, −1.35, 0), facing into the room |
| Stair_Up | a 0.55 m band at the first riser | centre of the cell south of the flight, facing 180 |
| Stair_Down | the open side of the top cell | the cell beside the top, facing away from the hole |
| Trapdoor / ladder | the cell's south half | the cell south of it, facing 0 |

Spawns always lie outside their trigger.

**Lighting** (Blender; starting values, tuned in the look test):

| Light | Setting |
|---|---|
| `VKI_Key_Day` / `_Night` | SUN, elevation 62°, from the SSW, angle 8°, shadows on, strength 0.4–1.0 by preset. Shadows on vs off is A/B tested in the core look test. |
| `VKI_Fill` | SUN 0.5, shadowless, along the view direction |
| Hearth | POINT (1, .52, .22), 200–500 W |
| Forge | 450–900 W plus a 150 W bed glow |
| Candles | 10–40 W |
| Windows | SPOT (.82, .88, 1.0), 350 W, 60° cone, 2 m outside, aimed through the opening |
| Lancets | spots tinted by the glass |
| Exit apron | cool area light |

- Presets: Tavern uses Night; everything else uses Day.
- All sockets come from the masters' `vki_lights`. The same data spawns Blender lights and the `LGT_` empties Unity will use.

---

## 7. Code organisation

Folder `src/interior/`. `kit_sync` scans `src/**` recursively and requires unique basenames. Everything is separate from `KIT_MODULES`/`EXTRA_SPECS`/`full_rebuild`. **There are no core edits.**

| Text | Owner | Contents |
|---|---|---|
| `vki_core` | core | Constants and slots; `VKIKit(Kit)` (`box`/`project`/`finish` as §2 and §4); `vki_mats`, `VKI_MAT_MAP`, `vki_apply_mats`; `VKI_SLOT`, `VKI_STYLE_MATS`, `vki_variant_mesh`, `vki_refresh_variants`; `vki_wobble`, `vki_vnoise`, `vki_textile_map`, `VKI_TEXTILE_CELLS`; `VKI_SPECS=[]` holding tuples `(name, fn, finish_kw, pkg)`; `vki_rebuild(names)` (builds into a temporary object, copies geometry, materials and props into the existing master, creates new masters hidden in `VKI_Pieces` under VillageKit, refreshes `VARI_*`); `vki_adopt(names)`; `vki_place(coll, piece, x, y, rot=0, z=0, style=None, **props)` (lattice and rot-lock asserts, name `piece+"_inst"`); `vki_scene`, `vki_rig`, `vki_shot(scene, name, target, mode="game"/"plan", D=18)` (temporary ortho for plans, restores the camera, renders to `renders/interior/<scene>/`); `vki_ns()`; `vki_ws(agent)`, `vki_ws_build(agent, names)`, `vki_ws_shot` |
| `vki_tex` | core | generators (§4.2); executed on demand, not part of `vki_ns` |
| `vki_test` | core | harness (§9) |
| `vki_fam_timber`, `vki_floors` | core | reference family, floors, `Leaf_Plank`, `Test_Axis` |
| `vki_fam_stone`, `vki_fam_board`, `vki_props_smithy` | PKG-S | |
| `vki_fam_wattle`, `vki_fam_ashlar` | PKG-W | |
| `vki_links`, `vki_textiles`, `vki_props_chapel` | PKG-L | |
| `vki_props_home` | PKG-H | |
| `vki_props_tavern` | PKG-T | |
| `vki_rooms` | assembly | `VKI_PLANS` (the §6 strings verbatim), `VKI_ROOMS` (families, styles, links, overrides), `VKI_CODES`, parser and assembler, `vki_check`, `vki_build_all` |

**Loader:**
```python
def vki_ns():
    g = {}; exec(bpy.data.texts["vk_kit"].as_string(), g); g = g["vk_kit_ns"](terrain=False)   # kit + 8 modules
    for t in VKI_TEXTS:                         # pre-declared by core, in load order
        if t in bpy.data.texts: exec(bpy.data.texts[t].as_string(), g)   # missing package texts are skipped
    return g
```

**Workshop helpers:**
- `vki_ws(agent)` calls `ws_scene("vki_"+agent)`, then: assigns `W_VKI_Day`, hides the `_Ground` plane (z = 0 z-fights with floors), unlinks `VK_Sun` from **that** scene only, and links `VKI_Key`/`VKI_Fill`.
- `vki_ws_build` is `ws_build` with `VKIKit`, `VKI_SPECS` filtered to the package, the `SM_VKI_` check and the ownership guard. It exists because `ws_build` hard-codes `g["Kit"]` and asserts `SM_VK_`.

---

## 8. Build plan

**Working agreements (from HANDOFF):**
- Verify visually at full resolution after every change.
- The coordinator saves the .blend after each completed step. Package engineers never save.
- No Unity export until the user asks.
- Push only your own texts (`push([...names])`).

### (a) Core stage (one engineer, sequential)

| Step | Deliverable | Acceptance |
|---|---|---|
| C1 | `vki_core`, the `vki_test` skeleton, `SM_VKI_Test_Axis`, `VKI_Test` scene | T1, T7, T8, T10, T14 pass on a smoke piece. T15 exterior invariance: the hashes of `SM_VK_Wall_Stone`, `SM_VK_Wall_Timber`, `SM_VK_Wall_Wattle`, `SM_VK_Chapel_Wall` and `SM_VK_Prop_Table` (vertices, UVs, Col, material names), plus the node trees of `M_VK_Glow`, `M_VK_Window` and `MC_World`, are unchanged after `vki_ns()` + `vki_rebuild()`. Two consecutive rebuilds give identical hashes. |
| C2 | Every §4.2 texture except Textiles, plus all §4.3 materials; `vki_apply_mats()` | One generator per call. A 3×3 tiling render per texture shows no visible seam and no standout feature. Floor luma 0.25–0.45, limewash 0.60–0.80. B/C board variants tile against A in all 8 neighbour configurations. |
| C3 | The Timber family (18), Floors (4: 150/300/600 + Sill), `Leaf_Plank_Full/_Cut`, the rig, `VKI_LookTest` (a 6×5 Timber room with every Timber kind, a partition, Boards/Flag floors, placeholder existing props) | T1–T14 pass. Seam-board renders (ortho top at 2 px/cm, and the game camera). Look-test renders: game and plan, Day and Night, shadows on and off, rake vs post. |
| **Gate** | **Show the look test to the user**: cut and full look, camera, lighting, rake vs post | Decisions recorded in the spec |
| C4 | Freeze: write `docs/INTERIOR_KIT.md` (this spec plus the gate decisions); push texts; save | |

### (b) Parallel packages (up to 5 engineers, one shared Blender)

**Rules for every package:**
- Own texts and scene `WS_vki_<pkg>` only. Never edit `vki_core`, `vki_tex`, `vki_test` or any other text.
- Never call `vki_rebuild`, `vki_adopt`, `full_rebuild`, `apply_pbr_all` or any `gen_*`. The only exception: PKG-L runs `vki_gen_textiles_atlas`, which writes only `T_VKI_Textiles*`.
- No save. No `bpy.ops` except rendering. Calls under about 20 s (build at most about 6 pieces per call).
- Slots 0–65 and the whitelisted overrides only. Names from the assigned list only.
- **Hand-in:** `vki_test_pieces(names)` returns `{}`; a catalog render at full resolution; `ws_stats` inside the budgets.

| Package | Exact pieces | Specific acceptance checks |
|---|---|---|
| **PKG-S**: stone, board, smithy props | Stone (19): Plain_150A F/C, Plain_150B F, Plain_300 F/C, Window_150 F/C, Slit_150 F, Door_150 F/C, DoorWide_300 F/C, Niche_150 F, Rake_150_L/R, Hearth_300 F, Forge_300 F, Post_Stone_Corner F/C · Board (10): Plain_150 F/C, Plain_300 F/C, Door_150 F/C, Post_Board_Corner F/C, Post_Board_Mid F/C · Leaf_Arch_Full, Leaf_Wide_L/R_Full · smithy props P1 (5) | T4 rigs: Stone L, T, X and end joints; P-into-O tee. Pop-out stones stay inside the zone and match the painted stones in an ortho close-up. GlowIn in Forge and Hearth: clip check below 0.5%. |
| **PKG-W**: wattle and ashlar | Wattle (15): Plain_150A F/C, Plain_150B F, Plain_300 F/C, Window_150 F/C, Door_150 F/C, Rake_150_L/R, Post_Wattle_Corner F/C, Post_Wattle_Mid F/C · Ashlar (17): Plain_150 F/C, Plain_300 F/C, Lancet_150 F/C, LancetTall_150 F, Door_150 F/C, DoorWide_300 F/C, Niche_150 F, Rake_150_L/R, Post_Ashlar_Corner F/C, Post_Ashlar_Mid F · Leaf_Wattle_Full, Leaf_Lancet_Full, Leaf_LancetWide_L/R_Full | Wattle sag and post bow stay inside the envelope (T3, T13). Soot band present. The triple-lancet render reads with the glass unclipped. Lancet end profiles equal Plain. |
| **PKG-L**: links, textiles, chapel | Stair_Up_150x450_RailR/L, Stair_Down_150x450_RailR/L, Ladder_Up_H24/H30, Trapdoor_150, Apron_300x150, Floor_Dais_150/300, Floor_HearthApron_300x150, Beam_Stubs_150, FX_DoorSpill, FX_WindowPool, (FX_Shaft_Window, P2), Rug_300x200, Runner_300, RushMat · `T_VKI_Textiles` + `M_VKI_Textiles` · chapel props P1 (8) | An up/down pair rendered one above the other: same origin; down-stair risers visible from the game camera; trigger and spawn boxes not overlapping. Runner segments chain seamlessly. Atlas cells padded (no bleed at mip 3). |
| **PKG-H**: homes | §5.1 P1 list (≈28), then P2 | Footprints match `vki_fp_cells`. Wall-backed backs sit flush (gap ≤ 0, embed ≤ 0.05). Table dressing snaps at 0.80. Beds read from above (quilt visible under the half-tester). |
| **PKG-T**: tavern and lighting | §5.2 P1 list (≈13), then P2 | Bar pieces join with continuous tops at 1.5 m. Flap `hinge_axis` correct. Foam discs readable at D = 18. Every lighting prop carries `vki_lights` sockets. |

### (c) Assembly (one engineer)

1. `vki_adopt` all package masters into `VKI_Pieces`, then `vki_rebuild()` everything. T15 still passes.
2. Write `vki_rooms` and build the 9 scenes with `vki_build_all()`.
3. `vki_check(scene)` returns `[]` for every scene.
4. Render per scene: fit shot, or 2–3 follow positions; plan; Day and Night where relevant.
5. Save.

### (d) Review

1. Inspect every render at full resolution: seams, junctions, occlusion, glow clipping, repetition, exterior/interior pairs (the building's exterior shot next to its interior).
2. Fix, then show the user.
3. Update `KIT_README` (interior section), regenerate `PIECES.md`, update `HANDOFF.md`.
4. Save. Commit when the user asks.

---

## 9. Acceptance tests

### Automated (`vki_test_all()` returns `{}`)

| Test | What passes |
|---|---|
| T1 bounds | Walls: x ∈ [0, L] ± 1e-5, \|y\| ≤ 0.33, z ∈ [−0.30, H]. Posts inside ±`POST_HW`, top at H + 0.04. Floors inside [0, S]², z ∈ [−0.10, 0] (dais 0.20). |
| T2 end profiles | Boundary vertices at x = 0 and x = L equal the family's canonical `Plain_150A` profile at that height (1e-5). Full equals Cut for z ≤ 0.65. A rake's low end equals Cut and its high end equals Full. |
| T3 node zone | Within 0.32 of a node, geometry is either the plain cross-section or inside the surround envelope. No clear-opening edge nearer than 0.33. |
| T4 coverage rigs | L, T, X, free end, Full→Cut step, P-into-O tee, for every family: every wall vertex in the node square lies inside the post (margin 0.005), and 2 cm vertical ray grids over each node hit only post faces first. |
| T5 coplanar | BVH overlap between rig objects: no same-facing triangle pairs with n·n > 0.999 and plane distance < 1e-4. |
| T6 UV continuity | 150\|300\|150 runs at rot 0/180/0, Full next to Cut, floors at odd and even nodes, B/C variants: world-locked loops coincide modulo 1 (1e-4). |
| T7 closed solids | Every edge has 2 faces (whitelist: none; glass is a closed box). |
| T8 normals | 0 flipped faces after recalculating on a copy. |
| T9 budgets | Wall_150 Full ≤ 1500, Wall_300 Full ≤ 2500, Cut ≤ 700 / 1200, posts ≤ 400, floor ≤ 24, specials ≤ 6000, leaves ≤ 800, props per §5, scene ≤ 150k. |
| T10 metadata | Required `vki_*` properties present. `vki_cut_pair` exists and is reciprocal. Footprint matches the bbox. Trigger lies on the room side. Name matches the regex. |
| T11 placement | Structure on the 1.5 lattice, props on 0.75; rotations multiples of 90; `world0` pieces at rot 0; `Stair_Up` never at rot 180. |
| T12 room rules | Posts where §2.3 requires them. Floor coverage has no gaps or overlaps (stair and trapdoor cells excepted). Window/Lancet/Niche/specials and wall props with `vki_mount_zmin` > 1 only in Full runs. Every scene has at least one link with a valid target and a matching `SPN_<id>`. Up/down stair pairs share origin and rotation. BFS (capsule r 0.3 on a 0.25 m raster) reaches every use point and trigger from every spawn. R-occ1–3 are warnings. Cap luma ≥ floor luma + 0.15. |
| T13 wobble | \|Δy\| ≤ A. Zero within 0.32 of nodes and pins, at z ≤ 0.16 and within 0.25 of the cap. The body stays inside the cap half-width − 0.005. |
| T14 materials | 66 slots; no face index ≥ 66; no banned slot; the GLOW/WINDOW/STAINED/DRESS overrides present on every VKI master. |
| T15 exterior invariance | As in C1, run after every rebuild. |
| T16 determinism | Rebuilding twice gives identical vertex, UV and Col hashes. |
| T17 render clip | In each render, fewer than 0.5% of pixels have min(RGB) ≥ 0.98 inside GlowIn/Window masks (checked on the PNG via `bpy.data.images`). |

### Visual

1. **Seam boards per family:** straight runs, all junction rigs, Full/Cut/Rake transitions, 2×2 floor-tile junctions with A/B/C mixed. Ortho plus game camera, inspected at full resolution. Look for: no steps, UV jumps or lighting seams; a pale, continuous cap outline.
2. **Look test** (Day/Night): cut caps read as real members; the near-zone hides what the maths says; limewash is even with no repeating marks; light pools and the exit spill are visible.
3. **Per showcase scene, in game view and plan:**
   - walkways read as walkways;
   - nothing interactable is hidden behind something taller;
   - tall props stand against far walls;
   - fire is the brightest thing on screen and the windows come second (cool);
   - no 1.5 m repetition shows (at most 60% of the visible floor is plain base tile).
4. **Exterior/interior pairs:** palette, family and shutter colour continue from outside to inside.
5. **Stairs:** the up flight reads as going through the ceiling; the down hole shows its risers.

---

## 10. Open questions for the user

1. **Characters:** live 3D or pre-rendered sprites? If sprites, the interior pitch must equal the sprite pitch; this spec assumes 50°.
2. **Camera yaw:** fixed indoors? The cut walls are authored for one view direction.
3. **View transform:** the kit renders in AgX Medium High Contrast (−0.2). An earlier project note says AgX washes out flat stylised colour and recommends Standard. Keep AgX for consistency this round?
4. **Smithy exterior:** fix its blocked door (`front="WD"`, or a trigger under the canopy) now, or with the export work?
5. **Upper floors:** is one interior template per building type enough for this round, with the cottage loft (`VKI_Cottage_F1`) left for later?

**Relevant files:**
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_helpers.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_mat.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_kit.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_render.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\workshop\ws_common.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_tex2.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\kit_sync.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\archive\script_logs\agents\valley-rereview\agent-ac910b8221bab24cf.py`