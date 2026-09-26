# Interior Kit (VKI): final spec

This spec stands on its own. Engineers can implement it without reading the draft or the critiques. All paths are relative to `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\`. Lengths are in metres, angles in degrees, and "local" means piece-local coordinates.

---

## 0. Status, verified facts, rejected critique points

**The user's decisions are fixed:**
- Walls near the camera are cut-away pieces. Every wall comes as `_Full` and `_Cut` (1.00 m), and the designer picks one per wall.
- The grid is 1.5 m. Walls come in 1.5 and 3.0 m lengths, and one opening fills one 1.5 m piece.
- Scope this round: homes, the tavern/inn, the smithy and workshops, and the chapel.
- Each floor is its own scene, and stairs work like doors.
- Interiors may be larger than their exteriors.

**Checked in code, and overriding earlier notes:**
1. **View transform.** `VillageKit` renders with AgX, look "AgX - Medium High Contrast", exposure −0.2. It is not Standard. `tools/render_showcase.py` uses Standard only when converting PNG to JPEG.
2. **Why glow clips white.** The white glow in `blacksmith.jpg` comes from `M_VK_Glow`, a legacy flat material with emission 4.0. It is not caused by the view transform.
3. **Material slots.** `kit_mats()` returns 55 slots, with `M_VK_Hewn` last (`vk_helpers.py` L47–70). `docs/PIECES.md` still says 52.
4. **Rebuild resolution.** `_late()` resolves builders through `globals()` (L1465). `all_specs()` puts core specs first and module `EXTRA_SPECS` after, so `SM_VK_Prop_Bellows` is always `ind_bellows`, with the nozzle toward −X.
5. **`ws_build` (ws_common L55–85):**
   - It asserts the `SM_VK_` prefix.
   - It resets `use_smooth` by material index, which drops GOODS smoothing.
   - It re-projects all-zero-UV faces with `Kit.project`, where TILE only covers slots 0–54.
   - It copies tmp custom properties, but a builder only ever receives a `Kit`.
6. **Helpers that default to slots banned on VKI masters:**
   - `window_frame` has a STONE sill.
   - `smithy_chimney` is all STONE and STONE_BLOCK.
   - `stone_panel` and `plinth` default to STONE.
   - `rock` defaults to STONE_BLOCK.
7. **API facts:**
   - `pbr_material(mat, prefix, …)` takes a material object first.
   - `lit_window_material(name, warm, strength)` exists.
   - `lancet_pts` rises 0.7746·w above the spring.
   - `gen_stone` has 7 courses hard-coded at L161 and writes only stones with w·h > 0.25 m² to `_stones.json`.
   - `wall_rocks` maps x = ((−3u+1.5) mod 3) − 1.5.
8. **Colour layers and file size:**
   - `Kit` creates `Col` with `bm.loops.layers.color`, a byte colour layer (sRGB bytes).
   - `write_set` writes and packs 5 maps.
   - The .blend is already 400 MB.
9. **Exterior references:**
   - The inn is Stone ground floor, plaster Ochre, shutters Red.
   - The smithy is Stone "Dark", with `front="DW"`, and its forge chimney stands in front of the door.
   - The timber door leaf is 1.0 m wide.
   - The toolwall board's back is at local y −0.01, and the lantern back plate reaches +0.10.
   - `T_VK_Cobble` and the other terrain textures use T = 4.0.

**Rejected or replaced critique points:**

| Point | Decision and reason |
|---|---|
| Add Board `Rake_150_L/R` (both critiques) | Not needed. Every partition is now Cut by default, which also fixes sideways occlusion. No perimeter wall is Board. |
| `Door_150_W`, a 1.10 m wide door | Not adopted. One opening per family keeps T2/T3 simple, and thin Mid posts now leave a 0.21 m frame. |
| `Door_150_CutFrame`, full-height jambs and lintel in near walls | Not adopted. At 50° a lintel at 2.3 m hides knee height at the 1.6 m spawn. The exit is instead a closed cut leaf the player "presses". |
| Add `Plain_150B_Cut` (3 masters) | Replaced by a seed blend: below z 0.65 every piece uses wobble seed A. Full = Cut, and `300_Cut` = `150A_Cut ⊕ 150A_Cut`, with no new masters. |
| Edge-locked B/C floor variants and an A\|B\|C atlas | Replaced by 3.0 m-period floor textures with parity-quadrant 150 pieces. That breaks the 1.5 m repeat with no shader and no variant bookkeeping. |
| "Size props to n·1.5 − 0.30" alone | Wrong on its own: it fails between two walls (clear width 1.5n − 0.57). Adopted together with a `hug` placement rule (§5). |
| "Bellows depends on which builds last" | Wrong. The order is fixed, as in fact 4 above. |
| Tavern cellar fixes, trapdoor leaf, cellar racks | Moot. Cellar, trapdoor and ladder are deferred (§3). |
| Chapel D = 22 follow camera with look-ahead | Replaced by an 8×6 chapel with a fit camera at D 21.9. The critique's apex heights used the draft's wrong 3.90; the correct value is 3.765. |

---

## 1. Camera and cut height

**Reference camera** (the Unity target and every verification render):

| Setting | Value |
|---|---|
| Yaw | Fixed, looking +Y (north is up on screen) |
| Pitch | 50° |
| Vertical FOV | 29.8° (Blender `lens=38`, 36 mm AUTO sensor, 16:9) |
| Distance D | 14–22 m |
| Clip | near 0.5, far 80 |
| Camera position | target + (0, −0.643·D, +0.766·D) |

- At D = 18 the camera sits at (0, −11.57, 13.79) from the target.
- Frame edges hit the floor at y_t − 0.2856·D (bottom, ray at 65°) and y_t + 0.451·D (top, ray at 35°).
- The top of a wall of height h is in frame when y_wall ≤ y_t + 0.451·D − 1.428·h.
- Width at the bottom edge is 0.773·D.
- Scale is about 112 px/m at D = 18 (1080p), scaling as 18/D.

**Choosing fit or follow:**
- D_fit = (L + 1.5 + 1.428·h_fit) / 0.737, where L is room depth.
- Also D_fit ≥ (W + 1)/0.778, where W is room width.
- h_fit is 3.0 for 3 m walls, 2.4 for Wattle, and the tallest north-wall feature + 0.2 for Ashlar (3.97).
- If D_fit ≤ 22: fixed camera at D = max(D_fit, 14), target x = room centre, y_t = y_S − 1.5 + 0.2856·D.
- Otherwise follow the player:
  - target = player + (0, 2.0);
  - clamp x to [x_W − 0.5 + 0.387·D, x_E + 0.5 − 0.387·D], using the room centre if that range is empty;
  - clamp y to [y_S − 1.5 + 0.2856·D, y_N − 0.451·D + 1.428·h_fit].
- Every showcase scene in §6 is a fit scene.

**Occlusion:**
- Along the view, an object of height h hides floor for h/tan φ beyond its room-side top edge. φ is 50° at screen centre, 35° at the top of the frame and 65° at the bottom.
- Sideways, a wall at lateral offset dx from the camera hides floor h·dx/(0.766·D − h) beyond itself.

**Cut height:** `CUT_H = 1.00` to the top of the cap, for every family and storey. A cut wall hides 0.47–1.45 m of floor (0.86 m at screen centre).

**Layout rules** (automated by T12 and T19):

| Rule | Content |
|---|---|
| R-occ1 | No floor-level interactable (stair hole, dropped item) within 1.5 m of a Cut wall's room face. |
| R-occ2 | Props taller than 1.25 m only against a Full north wall, or where T19 shows no hidden use point, trigger or spawn. |
| R-occ3 | Nothing above 2.0 m over walk lanes. Optional overhead items carry `vki_cam_fade=1`. |
| R-occ4 | Wall-mounted dressing only on Full walls (`vki_mount="wall_hung"` requires a Full host). |
| R-occ5 | Within 0.9 m of a Cut wall's room face: only props ≤ 0.75 m tall, or free-standing props that read from their top. |
| R-occ6 | No prop taller than 1.00 m within 0.9 m of a Window or Lancet room face, across the opening's width. This is a warning; `vki_warn_ok="window"` accepts it deliberately. |

**Default wall heights** (the designer can override any wall):
- North perimeter wall: Full.
- Side perimeter walls: Full, with the south-most piece a Rake or pillar (§2.4).
- South perimeter wall: Cut.
- **Every partition, E–W or N–S: Cut.**

---

## 2. Grid and wall system

### 2.1 Coordinates and constants

**Grid and origins:**
- `IG = 1.5`. Nodes sit at (1.5i, 1.5j).
- Each scene's origin is its SW node. The floor top is at z = 0 on every storey.
- Cell (c, r) has its centre at (0.75 + 1.5c, 0.75 + 1.5r). Row 0 is the camera (south) side.
- An "even node" has coordinates that are multiples of 3.0.

**Wall pieces:**
- The origin is the start node, on the centreline at z = 0. The piece spans local x ∈ [0, L], L ∈ {1.5, 3.0}.
- Face A (the room side) is local −Y; face B is +Y.
- Perimeter placement, clockwise from above:

  | Wall | Rotation | Origin |
  |---|---|---|
  | North | 0 | W end |
  | East | −90 | N end |
  | South | 180 | E end |
  | West | +90 | S end |

- Partitions may use either direction; the assembler assigns face styles by zone (§6).

**Other pieces:**
- Floors: origin at the min-corner node, rotation 0 only (§2.7).
- Stairs: origin at the min-corner node.
- Posts: centred on their node.
- Props: origin at the footprint centre at floor level, back toward local +Y, front toward −Y (§5).

**Constants:**

| Constant | Value |
|---|---|
| Thickness `T` | Class **O** 0.50 (Timber, Stone, Ashlar). Class **P** 0.30 (Wattle, Board). |
| `H_FULL` | Timber 3.0 · Stone 3.0 · Board 3.0 · Wattle 2.4 · Ashlar 4.5. Upper floors also use 3.0. |
| `PROUD` | 0.03. Caps, rails, skirtings and oak members reach `CAP_HW` = O 0.28 / P 0.18. |
| `POST_HW` (Corner posts, square) | O 0.31 / P 0.21, bevel ≤ 0.02 |
| Mid posts (thin) | ±0.12 along the wall × ±0.31 across (P: ±0.10 × ±0.21) |
| Post z range | −0.30 to wall top + 0.04 |
| `NODE_FLAT` | 0.32. No deformation within this distance of a piece-end node. |
| `OPEN_MIN` | 0.33. Clear openings lie in x ∈ [0.33, L − 0.33]. |
| Surround envelope | Frames, jambs and voussoirs may occupy x ∈ [0.02, 0.33] from each end node, \|y\| ≤ POST_HW − 0.01 (O 0.30 / P 0.20), z ≤ post top. |
| `FOOT_Z` | −0.30. Wall bodies continue below the floor as a section footing. |
| Proud line | O 0.285 / P 0.185 from the wall line. Floor-standing wall-backed props put their back here. |

**Reserved heights** for faces that overlap in plan:

| z | Surface |
|---|---|
| 0 | floor top |
| 0.015 | `Floor_Sill` |
| 0.025 | overlays (rugs, runners, rush mats) |
| 0.03 | door thresholds, hearthstones |
| 0.16 | skirting and sole-plate top |
| 0.20 | dais top |
| 0.88–1.00 | cut cap band (the cap top may sag to 0.98) |
| 1.04 | cut post top |
| H − 0.12…H | full cap |
| H + 0.04 | full post top |

Structure pieces never share a horizontal face height where they overlap in plan. Props never intersect structure (T12 clash check), so their heights are free.

### 2.2 Families

| Family | Class | H | `WALL_A` default | Base | Cut cap 0.90–1.00 | Full top | Posts |
|---|---|---|---|---|---|---|---|
| **Timber** | O | 3.0 | PlasterCream on body ±0.25; oak members at ±0.28 | oak sole plate 0–0.16 | oak mid-rail, top face `CAP` (Hewn); the same rail runs on Full walls | oak head plate | oak Corner post; thin oak Mid post; top faces ENDGRAIN |
| **Stone** (rubble) | O | 3.0 | StoneIn | none | StoneBlockIn coping in 0.75 m units, V-joints | same coping | Corner: quoin pier of stacked StoneBlockIn blocks. Mid: thin dressed pilaster. |
| **Ashlar** | O | 4.5 | AshlarIn | none | DRESS string course with weathered top (also on Full walls) | second string course at 2.90–3.00, cornice at H−0.12…H | Corner: clustered respond. Mid: shaft respond, Full only. |
| **Wattle** | P | 2.4 | PlasterDaub, pillowed | oak sole beam 0–0.16 | hewn oak rail | sagging wall plate | Corner: crooked hewn post, bow ≤ 0.02 inside the envelope. Mid: thin hewn post. |
| **Board** | P | 3.0 | BoardsV | none | Hewn rail | Hewn rail | oak Corner and Mid posts |

**Timber:**
- Studs 0.12 wide sit at x 0.75 (and 2.25 on 300 pieces).
- Every piece end carries a **half-stud** (x 0–0.06 and L−0.06…L), so each node shows one full stud whatever the split.
- Studs run from 0.16 to the cap bottom, passing the mid-rail on Full walls.
- `_B`: a curved brace above z 1.2 only.

**Stone:**
- `_B`: pop-out stones above 1.2, each at most 0.06 proud.
- Limewashed masonry is Stone pieces with a Plaster `wall_a` style; arches and coping stay dressed stone.

**Ashlar** has no B variant and uses pillars instead of rakes (§2.4).

**Wattle:**
- Wall-plate sag is ≤ 0.02, zero within NODE_FLAT.
- Soot above 1.4 is written to `vki_dark`.
- `_B`: a bare `INFILL` (WattleIn) patch above 1.2.

**Board** uses its default BoardsV, or a Plaster style for lath-and-plaster partitions.

**Cross-section per piece:**

| Element | O | P | z |
|---|---|---|---|
| Body: A face `WALL_A`, B face `WALL_B`, end faces `WALL_A` | ±0.25 | ±0.15 | −0.30 to cap bottom |
| Skirting / sole (Timber, Wattle) | ±0.28 | ±0.18 | 0–0.16 |
| Cut cap | ±0.28 | ±0.18 | 0.90–1.00 |
| Full cap | ±0.28 | ±0.18 | H−0.12…H |

The top faces of caps and posts use `CAP`, so the room outline reads as a pale line.

**Deferred this round:** the Log and StoneUp families.

### 2.3 Junctions and posts

Walls always run node to node, and collinear pieces butt together.

| Situation at a node | Post |
|---|---|
| L, T or X junction | **`Post_<fam>_Corner`**, required. A missing one is an **error** (T12). |
| Straight run with a height change, family change or class change | **`Post_<fam>_Mid`**, required (error) |
| Free end | `Post_<fam>_Mid` (**warning** if missing) |
| Straight run, same family and height, at an **even** node (x or y a multiple of 3.0) | Rhythm `Post_<fam>_Mid`, optional. Timber, Wattle and Board by default; Ashlar on the chapel's side walls. **Skipped** where a wall-backed or wall-hung prop, or a stair, spans the node. |

- **Post family by priority:** Stone > Ashlar > Timber > Wattle > Board. Use the thickest class present.
- **Post height:** the tallest wall-end height present. A rake contributes its end height.
- **P into O:** a P partition teeing into an O wall takes an O Corner post. The P stem (±0.18) lies inside ±0.31.

**Coverage** (T4):

| Check | O | P |
|---|---|---|
| POST_HW ≥ CAP_HW + 0.03 | 0.31 ≥ 0.31 | 0.21 ≥ 0.21 |
| 2·POST_HW − bevel ≥ 2·CAP_HW + 0.03 | 0.60 ≥ 0.59 | 0.40 ≥ 0.39 |
| POST_HW ≤ NODE_FLAT | 0.31 ≤ 0.32 | 0.21 ≤ 0.32 |

- Mid posts cover the end plane (|y| ≤ 0.31) of a height or family step.
- Posts are rigid: no jitter and no round Corner posts.
- A door next to a Corner post uses the post as its jamb; 0.02 m of frame shows.

### 2.4 Full, Cut, Rake and pillar

- Every wall shape exists as `_Full` and `_Cut`.
  - They share footprint, origin, collider, grid cuts, UVs and (below 0.65) wobble.
  - The Cut piece is exactly the lower metre of the Full piece plus its cap.
- **Pairs:**
  - `vki_cut_pair` holds the reciprocal twin.
  - Pieces without a twin carry a one-way `vki_cut_to`: `Plain_150B_Full` → `Plain_150A_Cut`, and Rakes → `Plain_150A_Cut`.
  - Specials have real Cut twins (§3.2).
- **Rake** (`Rake_150_L/R`: Timber, Stone and Wattle only):
  - The Cut profile holds for x ≤ 0.32 from the low end, and the Full profile for x ≥ 1.18. The cap slopes only between: 66.7° for Timber and Stone, 58.4° for Wattle.
  - `_L` has its low end at local x = 0 (west walls). `_R` has it at x = L (east walls).
  - It is the south-most piece of a side perimeter wall that meets the Cut south wall. The SW/SE Corner posts are then Cut height.
- **Pillar:** the alternative to the rake. The side wall's south-most piece is Full plain and the SW/SE Corner post is Full.
  - Ashlar always uses the pillar.
  - For the other families, look gate G1 picks rake or pillar as the default.

### 2.5 Walls meeting floors

- Floor slabs span z −0.10…0 and end exactly on grid lines.
- Wall bodies go down to −0.30 and pass through the slab edge. Skirting bottoms are coplanar with the floor top but face the opposite way and are hidden.
- A floor edge is always covered by one of:
  - a wall body (≥ 0.15 m of cover);
  - a door threshold (built into every door piece; |y| ≤ CAP_HW, z 0–0.03);
  - `Floor_Sill_150` (0.20 wide, z 0–0.015, allowed at rot 0 or 90).
- **Floor materials change only on grid lines.**
- The part of a body below z = 0 fades to black in vertex colour. The south wall then reads as a diorama section standing on its footing over the void.

### 2.6 Seam rule (wobble)

`VKIKit.finish` applies no global wobble. Wall builders call this last, on body faces only:

```python
VKI_AMP = {"Timber":.012, "Stone":.020, "Ashlar":.010, "Wattle":.020, "Board":0.0}
VKI_SECOND = {"A":"B", "B":"A"}
def vki_wobble(k, L, fam, variant, holes, top_body_fn, pins=()):
    A = VKI_AMP[fam]
    for v in k.bm.verts:
        if not v[k.body] or abs(abs(v.co.y) - k.T/2) > 1e-4: continue
        x, z = v.co.x, v.co.z
        e  = min(smoothstep(0.32, 0.57, abs(x-n)) for n in (0.0, 1.5, 3.0) if n <= L+1e-6)
        e *= min([smoothstep(0.0, 0.10, abs(x-p)) for p in pins] or [1.0])        # Timber studs
        e *= min([smoothstep(0.0, 0.15, vki_rect_dist(x, z, h)) for h in holes] or [1.0])
        tb = top_body_fn(x)                                                        # cap bottom (sloped on rakes)
        zf = smoothstep(0.16, 0.41, z) * smoothstep(tb, tb-0.25, z)
        span = int(min(x, L-1e-6) // 1.5)
        var  = variant if span == 0 else VKI_SECOND[variant]
        sA   = zlib.crc32(f"{fam}|A".encode()); sV = zlib.crc32(f"{fam}|{var}".encode())
        u, w = (x-1.5*span)/0.8, z/0.8
        n = lerp(vki_vnoise(u, w, sA), vki_vnoise(u, w, sV), smoothstep(0.65, 1.0, z))
        v.co.y += math.copysign(A * e * zf * n, v.co.y)                           # outward only
```

**Properties:**
- Ends are flat and identical, so pieces meet exactly whatever their rotation, length or height.
- There is no x or z motion.
- The wobble moves outward only, so props flush with the nominal face never show a gap behind them.
- Below z 0.65 every piece uses seed A. That makes Full = Cut, `Plain_300 = 150A ⊕ 150B` above 1.0, and `300_Cut = 150A_Cut ⊕ 150A_Cut`.
- T13 margin: body + A ≤ CAP_HW − 0.005 (0.27 ≤ 0.275; 0.17 ≤ 0.175).
- Seeds use crc32, never Python's `hash()` of strings.

**Vertex density:** `grid_cut(k, vs, step=0.25)` on body panels. Origins sit on nodes, so every piece of a family has identical vertex columns.

**Cap sag** (end-pinned, zero within NODE_FLAT): Timber rails 0.010, Wattle rail and plate 0.020, others 0. Stone coping units get ±0.006 height jitter per 0.75 m unit, with the end units fixed.

**Other members:** posts, frames, floors and props do not wobble. `jitter` is allowed only on boxes that touch neither a piece end nor a post envelope.

**Look gate G1** compares wobble on and off, and sag on and off, in an A/B render.

### 2.7 UV rules

**World-locked slots** use zero UV offset (`VKIKit.box` skips the centre-hash offset for them):

| Slot | Tile t |
|---|---|
| `WALL_A`, `WALL_B`, `INFILL` | 1.5 |
| `FLOOR` | 3.0 |

- **Walls:** origins sit on the lattice and 1.5/t is an integer, so local planar UVs equal world UVs modulo 1. Both faces stay continuous under 180° rotation, and v = z/t, so Cut = Full below the cap.
- **Floors** have a 3.0 m period, so floor pieces obey parity:
  - `Floor_300`, `Floor_600` and `Floor_Dais_300` may sit only at even nodes.
  - 1.5 m tiles come as four masters `Floor_150_Q00/Q10/Q01/Q11`, whose UVs are offset by (i mod 2, j mod 2)·0.5 of the node index they are placed at.
  - The assembler covers each floor zone greedily: 600, then 300 (both at even nodes), then Q150.
- Floors are rotation 0 only (`vki_rot_lock="world0"`). Plank direction comes from the style (`Boards_NS` / `Boards_EW`).
- **Jointed by design:** caps (0.75 m coping units, rails butting at nodes), posts, reveals and hearth interiors.
- `VKIKit.project` reads `VKI_TILE` for slots ≥ 55 before falling back to `TILE`.

### 2.8 Vertex colour

`VKIKit.finish(name, coll, grime)` writes `Col` itself and never calls `Kit.finish`. `grime` is `"wall"`, `"floor"`, `"prop"` or `"none"`.

**`Col` is a byte (sRGB) layer.** The values below are display-space; the shader linearises them, so 0.75 displays as about 0.52 linear. Confirm this with one test quad in C1.

| Surface | g |
|---|---|
| Walls and posts, z ≥ 0 | 0.75 + 0.25·smoothstep(0, 0.6, z) |
| Walls, z < 0 (footing) | 0.75·(0.45 + 0.55·(z+0.30)/0.30) |
| `CAP` faces with n.z > 0.7 | 1.0 |
| Floors | 1.0 |
| Props | 0.85 + 0.15·smoothstep(0, 0.3, z) |
| Undersides (n.z < −0.6) | ×0.72 |
| All faces, last | ×(1 − `vki_dark`) |

**Build layers:**
- `vki_body` (int, per vertex) and `vki_dark` (float) default to 0 and are **removed after finish**.
- `vki_heat` (float, 0 at the rim to 1 at the core) is written by builders on GLOW faces. Finish stores it as the float attribute **`vki_rim` = 1 − heat**.
- GlowIn reads `vki_rim` through an Attribute node. A missing attribute reads 0, which is full core colour, so reused exterior props glow correctly.
- At export (later), `vki_rim` is baked to UV2 or `Col.a`.

**Smoothing:** finish honours the builder's `f.smooth` and does not reset smoothing by material index.

---

## 3. Structure piece list

- **Naming:** `SM_VKI_<Class>_<Family>_<Kind>_<Len>[_<Var>]_<Full|Cut>`, with lengths in cm.
- **Helper and global prefix:** `vki_` / `VKI_`. The `SM_VKI_` prefix keeps these pieces out of `full_rebuild` and `EXTRA_SPECS`.

### 3.1 Walls and posts

| Kind | Timber | Stone | Ashlar | Wattle | Board |
|---|---|---|---|---|---|
| `Plain_150A` F/C | ✔✔ | ✔✔ | ✔✔ | ✔✔ | ✔✔ |
| `Plain_150B` F | ✔ brace | ✔ pop-outs | – | ✔ INFILL patch | – |
| `Plain_300` F/C | ✔✔ | ✔✔ | ✔✔ | ✔✔ | ✔✔ |
| `Window_150` F/C | ✔✔ | ✔✔ round head | `Lancet_150` ✔✔ | ✔✔ unglazed | – |
| `LancetTall_150` F | – | – | ✔ | – | – |
| `Door_150` F/C | ✔✔ | ✔✔ round arch | – | ✔✔ | ✔✔ |
| `DoorWide_300` F/C | – | ✔✔ segmental | ✔✔ pointed | – | – |
| `Rake_150_L/R` | ✔✔ | ✔✔ | – (pillar) | ✔✔ | – |
| Specials F/C | `Fireplace_300` ✔✔ | `Hearth_300` ✔✔, `Forge_300` ✔✔ | – | – | – |
| `Post_<fam>_Corner` F/C | ✔✔ | ✔✔ | ✔✔ | ✔✔ | ✔✔ |
| `Post_<fam>_Mid` F/C | ✔✔ | ✔✔ | F only | ✔✔ | ✔✔ |
| **Count** | **17** | **21** | **12** | **15** | **10** |

That is **75** wall and post masters.

- **Plain_150B:** the variant detail (brace, pop-outs, patch) is only above z 1.2. The pop-outs are keyed to `T_VKI_StoneIn_stones.json` (§4.2).
- **Deferred, not built this round:** Slit, Niche, Timber/Board DoorWide, Ashlar Door_150, Stair RailL, Ladder, Trapdoor, cellar pieces, Beam_Stubs, HearthApron, FX_Shaft.

### 3.2 Openings and specials

All values are piece-local, with the room on −Y. Every opening edge lies in x ∈ [0.33, L−0.33]; surrounds stay inside the §2.1 envelope.

**Doors:**

| Door | Clear opening | Detail |
|---|---|---|
| Timber / Board | x 0.33–1.17 (0.84) × 2.20 | oak frame, lintel 2.20–2.38 |
| Stone | 0.84 wide, round arch, spring 1.78, crown 2.20 | STONE_BLOCK_IN voussoirs 0.25–0.29 deep within x 0.04–1.46, \|y\| ≤ 0.30 |
| Wattle | 0.84 × 2.00 | crooked lintel |

- Every door has a threshold at z 0–0.03, \|y\| ≤ CAP_HW.
- Leaf socket at (0.33, −T/2 + 0.05, 0); `vki_leaf_open_deg=90`, opening toward −Y.
- **`Door_150_Cut`:** jambs end at 1.00 with the cap wrapping the reveal, plus the threshold. Used as an **exit**, it carries a `Leaf_Plank_Cut`, closed by default (look gate G1: closed or ajar 30° with `FX_DoorSpill`).

**Wide doors:**

| Door | Clear opening | Detail |
|---|---|---|
| Stone `DoorWide_300` | x 0.60–2.40 (1.80); spring 2.40, segmental crown 2.55 | |
| Ashlar `DoorWide_300` | `lancet_pts(0.70, 2.30, 0, 2.20)`, apex 3.44 | DRESS orders |

The Cut versions keep the lower metre; exits carry `Leaf_Wide_Cut_L` and `_R`.

**Windows:**

| Window | Glass / opening | Sill, head, detail |
|---|---|---|
| Timber, Stone | glass x 0.45–1.05 at y +0.10, a closed 0.02 box in the WINDOW slot; splayed to x 0.33–1.17 at face A | sill top 1.00, head 2.25. Timber: oak lintel; interior shutters folded into the splay (SHUTTER). Stone: round head; STONE_BLOCK_IN sill. |
| Wattle | x 0.45–1.05, z 1.00–1.60, unglazed | 2 rods; top-hung board shutter propped open 55° inward, inside the zone; daylight card at y +0.10 (per-master WINDOW → `M_VKI_Daylight`) |
| `Window_Cut` (all) | cut plain wall | the cap over x 0.33–1.17 becomes a sill slab \|y\| ≤ 0.30, top 1.00, CAP or STONE_BLOCK_IN, paler; plus a light-pool anchor |

**Lancets (Ashlar):**

| Piece | Glass | Spring | Glass apex | Splay |
|---|---|---|---|---|
| `Lancet_150` | x 0.45–1.05 at y +0.15, STAINED | 3.00 | 3.465 | to 0.33–1.17, apex 3.65 |
| `LancetTall_150` | same | 3.30 | 3.765 | apex 3.95 |

Sill 1.00, DRESS surround. `Lancet_150_Cut` is `Window_Cut` with a DRESS sill.

**Specials:**

- **`Fireplace_300` (Timber):**
  - Firebox x 0.90–2.10, z 0–1.00, back at y −0.20.
  - Breast x 0.40–2.60, projecting to y −0.85: plaster hood (`WALL_A`), oak bressumer at 1.40, BRICK firebox, breast top at H + 0.04 in `CAP`.
  - Hearthstone x 0.35–2.65, y −1.45…−0.85, z 0–0.03.
  - Crane and cauldron, firedogs, logs, GLOW embers (`vki_heat`), soot fan (`vki_dark`).
  - Light socket (1.5, −0.6, 0.5); FX `fire_small` at (1.5, −0.5, 0.2).
  - **Cut:** breast cut at 1.00 with a CAP top; oak lintel 0.90–1.00 over a 0.90 mouth; firebox and hearth intact.
- **`Hearth_300` (Stone):**
  - Firebox x 0.50–2.50, 1.20 high.
  - Breast x 0.35–2.65 to y −1.00; slab y −1.45…−1.00, z 0–0.03.
  - Spit with a goods-atlas roast (GOODS `meat`), cauldron.
  - Socket (1.5, −0.7, 0.5); FX `fire_large`.
  - **Cut:** as the Fireplace rule.
- **`Forge_300` (Stone):**
  - Raised hearth x 0.40–2.60, y −1.45…−0.25, top 0.85.
  - Coal bed with graded GLOW; tuyere on the −X side; fire irons; bucket.
  - Hood tapering into the wall top (Full only).
  - Re-implemented in STONE_IN and STONE_BLOCK_IN; do not call `smithy_chimney`.
  - Sockets: forge (1.5, −0.85, 1.3) and bed glow (1.5, −0.85, 0.95).
  - **Cut:** hearth, coal bed and irons kept, hood removed.

### 3.3 Floors, links, leaves and other structure

| Piece | Footprint / origin | Notes | Owner |
|---|---|---|---|
| `Floor_150_Q00/Q10/Q01/Q11` | [0,1.5]², min corner | slab z −0.10…0, no bevel, `FLOOR`, `grime="floor"`, world0, ≤ 12 tris; parity UV offset | core |
| `Floor_300`, `Floor_600` | min corner, even nodes | same | core |
| `Floor_Sill_150` | centred on a grid segment, rot 0 or 90 | oak (WOOD) or STONE_BLOCK_IN strip, 0.20 × 0.015; no FLOOR faces | core |
| `Stair_Up_150x450_RailR` | min corner; rot 0 rises +Y; rot 0/±90, **never 180** | see below | PKG-L |
| `Stair_Down_150x450_RailR` | same origin and rotation as its Up | see below | PKG-L |
| `Apron_300x150` | outside the exit, 3.0 × 1.5 centred on the opening, beyond the outer face | exterior ground in the FLOOR slot, **own UVs at t 4.0** (styles `ApronCobble/Dirt/Grass`); fades to black over the outer 0.5 m; STONE_BLOCK_IN doorstone | core |
| `Floor_Dais_300` | min corner, even nodes | top 0.20, FLOOR top, DRESS nosing on the −Y edge only with a pale chamfer | PKG-L |
| `Leaf_Plank_Full` / `_Cut` | hinge at the origin, extends +X | 0.84 × 2.20 / 0.84 × 0.95 with a CAP top, 0.08 thick, iron straps and ring; `hinge_axis="local Z"` | core |
| `Leaf_Wide_Cut_L` / `_R` | same | 0.90 × 0.95 each | PKG-S |
| `FX_WindowPool` | per window | floor light pool, FX slot | PKG-L |
| `FX_DoorSpill` | exit segment | 1.2 × 1.6 trapezoid; built only if G1 picks ajar | PKG-L |
| `SM_VKI_Test_Axis` | | red +X, green +Y, blue +Z; not shipped | core |

**`Stair_Up_150x450_RailR`:**
- It needs a wall along local x = 0 and along y = 4.5, and **no wall on its +X side**. Rhythm posts are skipped along its wall.
- Flight x 0.33–1.27.
- 15 risers × 0.200 = 3.00. The first riser is at y 0.00; 14 goings × 0.2586 = 3.62.
- Closed spandrel (WOOD) on +X, stringer on the wall side, handrail on +X at 0.95 above the pitch line, pale HEWN nosings. The top two treads have `vki_dark` 0.6.
- Lip x 0.33–1.50, y 3.62–4.215, z 2.80–3.00, with a darkened underside.
- **No FLOOR faces.** The room floor is laid under the whole footprint.
- Trigger: local centre (0.80, 0.30, 1.0), size (0.94, 0.55, 2.0). Spawn at (0.75, −0.75), facing 180.

**`Stair_Down_150x450_RailR`:**
- It covers its footprint, so no room floor goes under it.
- Hole x 0.33–1.27, y 0.10–3.62.
- Oak trimmers (top z 0, WOOD) fill x 0.28–0.33 and 1.27–1.50, and y 0–0.10. A PLANKS landing covers x 0.33–1.50, y 3.62–4.215. There are **no FLOOR faces**, so floor parity does not apply.
- Treads descend **from the north end toward −Y**, from z −0.20 to −2.0; risers face the camera. A closed VOID box (z −2.4…−2.0) sits beneath.
- Rails at 0.95: along +X over y 0.10–3.0, and across the south end.
- Trigger: x 1.27–1.70, y 2.90–4.21, z 0–2 (it extends into the neighbour cell). Spawn at (2.25, 3.75), facing 90.

**Budget:** 75 walls and posts + 4 leaves + 7 floors + 2 stairs + apron + dais + 2 FX = **92 structure masters**, plus the test piece.

### 3.4 Master metadata

Builders fill `k.meta`. `VKIKit.finish` stores it as `vki_*` custom properties (JSON strings for lists and dicts). `vki_rebuild` copies it to the master, and **`vki_place` copies it onto each instance**, so FBX exports carry it.

| Property | Values |
|---|---|
| `kit`, `grid_m` | "VillageInterior", 1.5 |
| `vki_class` | wall / post / floor / link / leaf / prop / overlay / fx |
| `vki_family`, `vki_kind`, `vki_len`, `vki_height` | family name, kind, length; "Full" / "Cut" / "Rake" |
| `vki_thick`, `vki_origin`, `vki_rot_lock` | |
| `vki_footprint` | "x0,y0,x1,y1" (T1 uses it) |
| `vki_fp_cells` | "w,d" |
| `vki_collider` | boxes; walls use the body footprint at z 0–2.2 for both Full and Cut |
| `vki_nav` | block / walk / none |
| `vki_cut_pair` or `vki_cut_to` | |
| `vki_opening` | |
| `vki_leaf_socket`, `vki_leaf_open_deg`, `vki_leaf_state` | |
| `vki_trigger`, `vki_spawn_local`, `vki_prompt_local` | doors: (0.75, −0.30, 1.40) |
| `vki_lights`, `vki_fx` | socket lists |
| `vki_mount` | floor / wall_floor / wall_hung / table |
| `vki_mount_zmin`, `vki_mount_zmax`, `vki_mount_ref` | `vki_mount_ref="top"`: the placer sets z = H − offset |
| `vki_back_y` | back plane |
| `vki_use` | use points [(x, y, facing), …] |
| `vki_uv_lock` | |
| `vki_post_rule` | which posts a Full ↔ Cut toggle must swap, for the later Unity tool |
| `hinge_axis` | leaves, lids, flaps |

---

## 4. Textures and materials

### 4.1 Slots

`VKIKit.finish` appends `kit_mats()[:55] + vki_mats()` for **67 slots**, after asserting `kit_mats()[54].name == "M_VK_Hewn"`.

| Index | Slot | Tile | World-locked | Style key |
|---|---|---|---|---|
| 55 | `FLOOR` | 3.0 | yes | `floor` |
| 56 | `WALL_A` | 1.5 | yes | `wall_a` |
| 57 | `WALL_B` | 1.5 | yes | `wall_b` (defaults to `WALL_A`'s material) |
| 58 | `CAP` | 1.2, grain along the long axis | no | `cap` |
| 59 | `STONE_BLOCK_IN` | 1.5 | no | |
| 60 | `BRICK` | 1.5 | no | |
| 61 | `STRAW` | 1.5 | no | |
| 62 | `ASH` | 0.75 | no | |
| 63 | `TEXTILE` | own UVs | no | |
| 64 | `WAX` | 1.0 | no | |
| 65 | `FX` | own 0–1 UVs | no | |
| 66 | `INFILL` | 1.5 | yes | `infill` (default WattleIn) |

In `VKIKit.project`, faces in the `WALL_A`/`WALL_B` slot with |n.z| > 0.7 on Stone or Ashlar masters switch to `STONE_BLOCK_IN`.

**Per-master material defaults (`k.slot_mats`)** are baked into each master's material list.
- Every VKI master:
  - GLOW → `M_VKI_GlowIn`
  - WINDOW → `M_VKI_Window_Day`
  - STAINED → `M_VKI_Stained_In`
  - DRESS → `M_VKI_Dress`
- Stone masters: `WALL_A` → StoneIn. Ashlar masters: AshlarIn. Board masters: BoardsV.
- Furniture: PLANKS → `M_VKI_WoodScrubbed`.
- Wattle windows: WINDOW → `M_VKI_Daylight`.

**Whitelisted per-master overrides:** WATER, WOOD, PLANKS, SHUTTER, CLOTH_A, CLOTH_B, WINDOW.

**Banned on VKI masters:** STONE, PLASTER, ASHLAR, FIELDSTONE, WATTLE, STONE_BLOCK, ROCK, MOSS, ROCK_MOSSY. Always pass `mi=STONE_BLOCK_IN` to `rock()`.

**Variants:**
- `vki_variant_mesh(piece, style)` creates `VARI_<crc32(piece + sorted style JSON)>`. The mesh carries `vki_base` and `vki_style` properties, and slot indices are guarded against `len(me.materials)`.
- `VKI_SLOT`: floor 55, wall_a 56, wall_b 57, cap 58, infill 66, wood 2, planks 23, shutter 10, cloth 11, cloth_b 12, window 4, stained 20, glow 9, water 18.
- Reused exterior props get `{glow: GlowIn, window: Window_Day}` (Night scenes: `window: Window_Night`).
- Night scenes also apply `{window: Window_Night, stained: Stained_Night}` to VKI masters.
- `vki_refresh_variants()` must run after any exterior `full_rebuild`, which only refreshes `VAR_*`.
- In Unity, a style becomes a prefab variant with material overrides.

### 4.2 Generators

New text `vki_tex` (`src/textures/vki_tex.py`), executed after `vk_tex`, `vk_texgen`, `vk_tex2` and `vk_mat`.

**Rules:**
- **Copy, never edit,** the exterior generators, so exterior textures stay bit-identical.
- Paint at S = 2048 and store at 1024 via `down2`.
- `vki_write_set` writes and packs **only `_BC`, `_N` and `_R`**, with `ao=cavity_ao(h,(2,6,18),(2.0,1.5,0.8),0.45)` and `ao_in_albedo` 0.35.
- `paint_form_light` with a light touch: hig 0.10–0.15, log 0.16–0.22, post 0.2–0.3.
- No moss or lichen. Lines at least 1 cm; at least 12 elements per tile; no standout feature.
- One generator per MCP call.

| Output | Function | T | Recipe |
|---|---|---|---|
| `T_VKI_Boards_NS`, `_EW` | `vki_gen_floorboards(seed=611, T=3.0, depth=.02, nb=12, joints=3, orient)` | 3.0 | 12 boards of 0.25 m. 3 butt joints per board per tile, ≥ 0.12 m from joints on neighbouring boards; redraw until true. Treenails 8 mm only at joints. Knots on 20% of segments (1.5–2.5 cm); 8% old-grey segments. Ramp `#3A2414 / #74492A / #A07448`; segment tint U(.88, 1.08); gaps `#2A1C12`. EW `swapaxes` the layout before painting. |
| `T_VKI_BoardsV` | same, `T=1.5, nb=6, joints=0` | 1.5 | vertical wall boards (the Board family) |
| `T_VKI_Flagstone` | `vki_gen_blocks(seed=15, T=3.0, nrow=6, blocks=(4,6,5,4,6,5), pal=("S1","S2","S4"), mortar="#5E564C", chip=.5)` | 3.0 | a copy of `vk_tex2.gen_ashlar`: 0.5 m rows, flags 0.5–0.75 m, mortar about 8 mm |
| `T_VKI_AshlarIn` | `vki_gen_blocks(seed=14, T=1.5, nrow=3, blocks=(3,2,3))` | 1.5 | pale S2 blocks, 0.5 m courses |
| `T_VKI_FlagRustic` | `vki_gen_flagrustic(seed=33, T=3.0, aspect=1.0, prot=(.010,.018), joint="#4A3A2C")` | 3.0 | a copy of `gen_fieldstone` without moss or lichen; packed-earth joints with pebbles |
| `T_VKI_Earth` / `_EarthSooty` | `vki_gen_earthfloor(seed=456, T=3.0, rushes=1.0/0.2, soot=0/1)` | 3.0 | a copy of `gen_dirt_v2` without grass. Rushes 0.12–0.32 m long, 4–7 mm wide, with drop shadows; strewing herbs. Sooty adds charcoal specks, ash haze and iron-scale flakes. |
| `T_VKI_PlasterIn` | `vki_gen_plaster_in(seed=23, T=1.5, depth=.015, blot=.2)` | 1.5 | a copy of `gen_plaster` with no cracks and no brick patches |
| `T_VKI_StoneIn` + `_stones.json` | `vki_gen_stone_in(L=stone_layout(10, T=1.5, lacing=False, NC=4), mortar="#857B6C")` | 1.5 | a copy of `gen_stone`: courses = `len(L['H'])` (about 0.375 m), moss and lichen steps removed. The JSON keeps stones with w·h > **0.08** m². |
| `T_VKI_WattleIn` | `vki_gen_wattle_in(T=1.5, nst=6, nrod=28)` | 1.5 | both counts even, so the weave wraps |
| `T_VKI_StoneBlockIn` | `vki_gen_stoneblock_in(seed=18, T=1.5)` | 1.5 | no lichen, no crack |
| `T_VKI_Brick` | `vki_gen_brick(seed=621, T=1.5, nr=20, nbk=6)` | 1.5 | running bond, `nr` even, 8 mm joints `#9C9284`, 10% overfired `#5C3324`; soot goes in vertex colour |
| `T_VKI_Ash` | `vki_gen_ash(S=1024, seed=631, T=0.75)` stored at 512 | 0.75 | no embers (embers are GLOW geometry) |
| `T_VKI_StrawBed` | `vki_gen_strawbed(seed=97, T=1.5)` | 1.5 | about 900 flat strands, calm; for the STRAW slot |
| `T_VKI_Textiles` | `vki_gen_textiles_atlas(S=2048, seed=950)` in text `vki_textiles` (core) | own UVs | 2 × 4 cells of 2:1, padded for mip 3: rug_madder, rug_indigo, runner (periodic in u), hanging_heraldic, tapestry_millefleur, quilt_patch, blanket_wool, altar_frontal. `VKI_TEXTILE_CELLS` and `vki_textile_map()` live in `vki_core`. |

**Pop-out stones:**
- Mapping: x = (−1.5u) mod 1.5, z = 1.5v (+1.5k).
- Keep stones ≥ 0.32 + w/2 from nodes.
- Depth ≤ 0.06, at 0.9 w × 0.9 h.

### 4.3 Materials

`vki_mats()` and `VKI_MAT_MAP` build these. A missing texture gives a flat placeholder. `vki_apply_mats(names=None)` rebuilds VKI entries in place. **Never call `apply_pbr_all`.**

| Style key | Name → texture / tint |
|---|---|
| floor | Boards_NS (default), Boards_EW, BoardsDark_NS/EW (.86,.80,.76), BoardsPale_NS/EW (1.10,1.05,.95), Flag, FlagWarm (1.04,1,.93), FlagRustic, Earth, EarthSooty, ApronCobble / ApronDirt / ApronGrass (`T_VK_Cobble/Dirt/Grass`, apron only) |
| wall_a / wall_b | PlasterWhite (1.08,1.08,1.10), PlasterCream (1,1,1), PlasterDaub (.80,.65,.47), PlasterOchre (1.03,.84,.56), PlasterRed (.78,.42,.33); StoneIn; StoneInWarm / Cool (the exterior stone tints); AshlarIn; WattleIn; BoardsV; Brick |
| cap | Hewn (existing `M_VK_Hewn`), StoneBlockIn, Dress, PlasterDaub |
| wood | Oak (`M_VK_Wood`), Dark (`M_VKI_WoodDark`, T_VK_Wood × (.62,.55,.50)) |
| planks | Scrubbed (`M_VKI_WoodScrubbed`, T_VK_Planks × (1.30,1.25,1.15)), Planks |

| Material | Definition |
|---|---|
| `M_VKI_GlowIn` | Base colour dark (.08,.04,.02). Emission = mix((1.0,.72,.30), (.85,.28,.05), Attribute `vki_rim`), strength = 2.2 − 1.0·rim. |
| `M_VKI_Window_Day` | `lit_window_material("M_VKI_Window_Day", warm=(.78,.86,1.0), strength=1.0)` + shadow transparency |
| `M_VKI_Window_Night` | `lit_window_material("M_VKI_Window_Night", warm=(.45,.55,.85), strength=0.35)` + shadow transparency |
| `M_VKI_Daylight` | flat emissive (.80,.86,.95) at 0.8 + shadow transparency |
| `M_VKI_Stained_In` / `_Night` | `pbr_material(bpy.data.materials.new(name), "T_VK_Stained", emission=1.8 / 0.4)` + shadow transparency |
| `M_VKI_Dress` | `T_VKI_StoneBlockIn` × `DRESS_TINT` |
| `M_VKI_Wax` | flat (.93,.88,.74), roughness .5; also tankard foam |
| `M_VKI_Ale` | flat (.45,.28,.08) (WATER override on tankards) |
| `M_VKI_WaterMurky` | `T_VK_Water` × (.55,.50,.40) |
| `M_VKI_FX_Light` | emission (1,.93,.78)·(1−v)² at 0.6, alpha 0.15, no shadow; read blend-mode enums at runtime |

- **Shadow transparency:** a Mix Shader driven by Light Path "Is Shadow Ray" into a Transparent BSDF, plus `use_transparent_shadow=True` wherever the property exists (check `bl_rna` first). Without it, the window spots cannot pass through the glass.
- **Reused unchanged:** Wood, Planks, PaintedWood shutters, Iron, Bronze, Steel, Cloth tints, Burlap, Paper, Goods atlas, Water, EndGrain, Bark, Coal, Hide, Void, Hewn, Clay.

**Palette targets** (checked in T12 and the renders):

| Target | Value |
|---|---|
| Floor BC luma | 0.25–0.45 |
| Wall luma | ≥ 0.35 |
| Limewash | 0.60–0.80 |
| Caps | 0.45–0.60 and ≥ floor + 0.15 |
| Prop top faces | luma differs from the floor style by ≥ 0.12 |

Only textiles, painted wood, glass and fire are saturated.

---

## 5. Furniture and dressing

### Conventions

**Scale** (exaggerated for readability):

| Element | Kit size |
|---|---|
| Table top | 0.10 thick at 0.80 |
| Form seat | 0.08 at 0.48 |
| Legs | 0.12–0.14, splayed 5–8° |
| Mattress | 0.25 |
| Straps | 0.045 |
| Candles | Ø 0.06 × 0.20 |
| Tankard | 0.16 |
| Round things | 16 segments |

- Tops get the detail budget and pale HEWN edge bevels. Floor contact is flat, with no jitter on feet.
- `grime="prop"`. Small food uses the goods atlas, never flat colours.

**Mounts:**

| `vki_mount` | Rule |
|---|---|
| `floor` | free-standing. Size ≤ 1.5n − 0.10; must stay ≥ 0.005 clear of every wall and post envelope. |
| `wall_floor` | the back sits on the proud line (0.285 O / 0.185 P from the wall line); the placer computes it, and `vki_back_y` records it. Width ≤ 1.5n − 0.30, depth ≤ 1.5d − 0.30. |
| `wall_hung` | on the face (±0.25 / ±0.15) and only between z 1.02 and H − 0.14; Full walls only. |
| `table` | origin at the table-top surface. |

**Placement:**
- Props snap to the 0.75 lattice.
- **`hug`:** when a side wall's proud line would be crossed, the placer slides the prop along its wall by the minimum amount, at most 0.30, and records `vki_hug`. T11 allows off-lattice positions only with `vki_hug`.
- Reused props are positioned from their master bbox: bbox centre on the lattice point, back = bbox max y after rotation. Their origins therefore do not matter.

**Rotation:** rot 0 has the back toward +Y and the front toward −Y. rot 90 has the back toward west, −90 toward east, 180 toward south.

**Budgets:**

| Category | Tris |
|---|---|
| Furniture | ≤ 1500 (hard limit 2000) |
| Dressing, overlays | ≤ 400 |
| Hero pieces | ≤ 6000 |

### 5.1 Homes (PKG-H, text `vki_props_home`)

**P1** (W × D × H, mount):
- **Tables and seats:**
  - `Table_Trestle_300` 2.70×0.90×0.80, floor
  - `Table_Trestle_150` 1.20×0.90×0.80, floor
  - `Table_Small` 1.10×0.75×0.78, floor
  - `Form_300` 2.70×0.35×0.48, floor
  - `Form_150` 1.20×0.35×0.48, floor
- **Storage:**
  - `Chest` 1.10×0.60×0.65, wall_floor; SHUTTER panels, iron straps; lid `hinge_axis="local X"`
  - `Dresser` 1.20×0.50×1.90, wall_floor; CLAY plates, jugs
  - `Shelf_Wall_150` 1.20×0.30, boards at 1.30 and 1.70, wall_hung, zmin 1.2
  - `Pantry_Shelves_300` 2.70×0.50×1.90, wall_floor; goods atlas
  - `Barrel` r 0.40×1.00, floor
  - `Barrel_Water` r 0.40×1.00 with a ladle, WATER top, floor
  - `Crate` 0.75×0.75×0.75, floor
  - `Jars_Cluster` 0.90×0.60×0.70, wall_floor
  - `LogBasket` 0.80×0.60×0.60, floor
- **Beds:**
  - `Bed_Straw` 0.90×2.00×0.45, long along Y, head +Y; STRAW mattress, TEXTILE blanket_wool; floor
  - `Bed_Box` 2.40×1.20×1.80, wall_floor, 2×1; opening −Y, quilt_patch visible through it
  - `Bed_HalfTester` 1.70×2.30×2.20, wall_floor, 2×2; canopy 0.9 deep over the head only; quilt_patch
- **Hearth and kitchen:**
  - `Hearth_Open` 1.30×1.30×1.20, floor: kerb STONE_BLOCK_IN, ASH bed, GLOW embers with `vki_heat`, logs, tripod pot; socket (0, 0, 0.5) 250 W; FX `fire_small`
  - `Oven_150` 1.20×1.20×1.90, wall_floor: BRICK dome, GlowIn mouth, flue into the wall; socket 150 W
  - `Worktable_150` 1.20×0.75×0.85, wall_floor; goods dressing
- **Other:**
  - `Desk_Merchant` 1.50×0.75×1.10, floor; PAPER ledgers
  - `TableDress_Meal_A/B`, table mount: goods-atlas bread, cheese, ham, a CLAY jug

**P2:** Barrel_Lying, Washstand, Chair_Box, Strongbox, Quern, WaterPail, Basket_Apples / Basket_Wool, Tapestry_300 (`vki_mount_ref="top"`, rod at H − 0.25), PegRail_150, Settle_300 (never south of a hearth or an interactable), Hurdle_150, Manger_150.

**P3:** Cradle, ButterChurn, WashTub.

### 5.2 Tavern and lighting (PKG-T, text `vki_props_tavern`)

**P1:**
- `Bar_Counter_150`: 1.50×0.70×1.05. A chain piece whose tops butt at local x ±0.75. Dark plank front (WOOD → Dark), 0.12 Scrubbed top with a pale front edge, foot rail; front −Y.
- `Bar_End_150`: spans local x ∈ [−0.45, 0.75]; its +X end butts a counter. Hinged 0.8 flap, `hinge_axis="local Y"`.
- `CaskRack_150`: 1.20×0.90×1.20, wall_floor. Two casks on a cradle, BRONZE taps toward −Y, drip tub.
- `Table_Barrel`: Ø 0.90 × 1.05, floor.
- `TableDress_Tavern_A/B/C`: tankards (0.16) with WAX foam discs and WATER → Ale; goods-atlas platter; a `Candle_Plate` with socket 15 W, FX `candle`. No dice.
- `Lantern_Wall`: 0.30×0.45×0.60, wall_hung, zmin 1.9. GLOW with `vki_heat`; socket 60 W.
- `Candle_Plate`: Ø 0.14 with a WAX candle; socket 15 W.
- `Candlestick`: BRONZE, 0.30 tall; socket 15 W.

**P2:** Stillage_300, BackBar_300, MeatRail_150, NoticeBoard, Sconce_Wall, CandleCluster.

**P3:** Chandelier_Wheel (`vki_cam_fade`), Trophy_Antlers.

### 5.3 Smithy and workshops (PKG-S, text `vki_props_smithy`)

**P1:**
- `Workbench_300` 2.70×0.80×0.90, wall_floor; leg vice.
- `QuenchTrough_150` 1.20×0.60×0.70, floor; STONE_BLOCK_IN, WATER → WaterMurky.
- `CoalBin_150` 1.20×0.90×0.70, wall_floor; bevelled flat-shaded COAL lumps.
- `IronStock_150` 1.20×0.60×1.20, wall_floor.
- `ToolWall_150` 1.20×0.14, board 1.10–2.30, wall_hung.
- `GoodsRack_150` 1.20×0.40×1.80, wall_floor; iron pots, tools, turned bowls.
- `Workbench_Carpenter` 2.40×0.90×0.95, wall_floor; planes, shavings.
- `PoleLathe` 2.40×0.90×2.20, wall_floor; spring pole.

### 5.4 Chapel and overlays (PKG-L, text `vki_props_chapel`)

**Chapel P1:**
- `Pew_300`: 2.70×0.55×0.80, floor. Seat at 0.46 facing local −Y. Open back: posts plus one pale HEWN rail at 0.72–0.80, raked 10°. Poppyhead ends; kneeler. Placed at rot 180 so it faces north.
- `Altar_300`: 1.80×0.90×1.05, footprint 2×1. DRESS block, TEXTILE altar_frontal, CLOTH_A linen, BRONZE cross, 2 built-in `Candlestick`s.
- `AltarRail_150`: 1.50×0.30×0.75, an edge piece with origin at its start node on the dais edge, occupying y 0.02–0.32; chains along X.
- `CandleStand_Pricket`: Ø 0.60 × 1.40; socket 30 W.
- `Lectern`: 0.60×0.60×1.30.
- `Font`: Ø 1.00 × 1.10.
- `VotiveRack`: 1.00×0.40×1.00, wall_floor, 12 candles; socket 30 W.

**Chapel P2:** Pew_150, WallBench_150, Sedilia_150, FurRug. **P3:** Retable_300, Statue.

**Overlays** (TEXTILE or STRAW, z 0–0.025, 1 cm bevels; never across a sill or threshold):
- `Rug_300x150` 2.60×1.30
- `Runner_300` 3.00×1.00 and `Runner_150` 1.50×1.00, periodic in u so they chain
- `RushMat` 1.20×0.80, STRAW, inside every exit

### 5.5 Existing props reused by name

Masters stay in `VK_Pieces`. Position comes from the bbox, and style `{glow: GlowIn, window: Window_Day}` is applied.

| Piece | Footprint | Note |
|---|---|---|
| `Prop_Loom` | 2×2 | wall_floor north, weaver faces −Y |
| `Prop_SpinningWheel` | 1×1 | |
| `Prop_Stool` | 1×1 | |
| `Prop_Bellows` | 2×1 | industry version, nozzle −X; rot 180 west of a forge |
| `Prop_Anvil` | 1×1 | |
| `Prop_WeaponRack` | 1×1 | wall_floor, hug |
| `Prop_Grindstone` | 1×1 | wall_floor |
| `Prop_BarrelStack` | 2×1 | wall_floor |
| `Prop_Sawhorse` | 1×1 | |

---

## 6. Showcase interiors

### Plan legend

- `+` is a node; the assembler places posts by the §2.3 rules.
- **E–W walls**, one token per cell on node rows:
  - `##` Full, `==` Cut, `WW` window Full, `ww` window Cut
  - `dd` doorway Cut (no leaf)
  - `ee` exit: Door_150_Cut + closed Leaf_Plank_Cut + Apron_300x150 + RushMat + link `front`
  - `EE EE` wide exit: DoorWide_300_Cut + Leaf_Wide_Cut_L/R + Apron + RushMat
  - `FF FF` the scene's special 300 piece
  - `LL` / `LT` Lancet / LancetTall Full, `ll` Lancet Cut
- **N–S walls**, one character between cells:
  - `#` Full, `:` Cut, `W` window Full, `d` doorway Cut
  - `t` Rake (perimeter only)
  - `r` stair rail (part of the stair, no wall)
  - a space: no wall
- **Cell codes are a generated view** (`vki_check` compares them). **The prop list is the source of truth:** `Piece (x, y) rot`. For wall_floor props the placer snaps the back and applies hug.

**Cell codes:**
- `^^` stair up, `vv` stair down
- `Sf` front spawn, `Ss` stair spawn
- `BX` box bed, `HT` half-tester, `bd` straw bed, `CH` chest, `DR` dresser, `PN` pantry, `SH` shelf or sawhorse
- `TB` table set, `tb` small or barrel table, `fm` form, `rg` rug, `WP` log basket, `ja` jars, `ba` barrel, `bx` crate, `KW` worktable, `OV` oven, `HH` open hearth, `fp`/`fg` special hearth zone
- `LM` loom, `SW` spinning wheel, `CT` counter, `CE` bar end, `CK` cask rack, `BS` barrel stack, `DK` desk
- `WR` weapon rack, `BL` bellows, `AN` anvil, `QT` quench, `CO` coal bin, `GR` goods rack, `GS` grindstone, `WB` workbench, `ir` iron stock, `PL` pole lathe
- `PW` pew, `AL` altar, `cd` pricket, `LC` lectern, `FT` font, `vr` votive rack

**Scene rules:**
- Every door has a free cell on both sides.
- Spawns lie ≥ 0.2 m outside every trigger.
- Exit spawns sit at local (0.75, −1.60) (wide doors: (1.5, −1.60)), facing 0 (compass: 0 = +Y, 180 = toward the camera).

### Scene overview

| Scene | Size (cells, m) | Families | Camera D | Preset |
|---|---|---|---|---|
| Hovel_F0 | 5×5 (7.5×7.5) | Wattle | fit 16.9 | Day |
| Cottage_F0 | 6×5 (9×7.5) | Timber, Board partitions | fit 18.0 | Day |
| Townhouse_F0 | 7×5 (10.5×7.5) | Stone (limewashed) | fit 18.0 | Day |
| Townhouse_F1 | 7×5 | Timber, Board partition | fit 18.0 | Day |
| Tavern_F0 | 9×6 (13.5×9) | Stone (limewashed) | fit 20.1 | Night |
| Tavern_F1 | 9×6 | Timber, Board partitions | fit 20.1 | Night |
| Smithy_F0 | 7×5 | Stone, Board store | fit 18.0 | Day |
| Workshop_F0 | 6×5 | Timber | fit 18.0 | Day |
| Chapel_F0 | 8×6 (12×9) | Ashlar | fit 21.9 (h_fit 3.97) | Day |

### Hovel: `VKI_Hovel_F0`

- **Zone** `all`: floor Earth, wall PlasterDaub.
- **Posts:** Wattle.

```
      0  1  2  3  4
     +##+##+WW+##+##+
   4 #BX BX CH PN PN#
     +              +
   3 #.. .. .. .. ..#
     +              +
   2 Wbd .. HH .. ..#
     +              +
   1 #bd .. .. TB TB#
     +              +
   0 tWP .. Sf .. jat
     +==+==+ee+==+ww+
```

**Props:**
- `Bed_Box` (1.5, 6.75) 0
- `Chest` (3.75, 6.75) 0
- `Pantry_Shelves_300` (6.0, 6.75) 0, hug
- `Bed_Straw` (0.75, 3.0) 0
- `Hearth_Open` (3.75, 3.75) 0
- `Table_Trestle_150` (6.0, 2.25) 0
- `Form_150` (6.0, 1.5) 0 and (6.0, 3.0) 0
- `TableDress_Meal_A` (6.0, 2.25) z 0.80
- `LogBasket` (0.75, 0.75) 0
- `Jars_Cluster` (6.75, 0.75) 180

**Spawn** `front` (3.75, 1.60).

### Cottage: `VKI_Cottage_F0`

- **Zones:**
  - hall: cols 0–3 all rows, plus cols 4–5 rows 0–1; FlagRustic / PlasterCream
  - bed: cols 4–5 rows 2–4; Boards_NS / PlasterCream
- **Walls:** perimeter Timber; partitions Board with PlasterCream (lath and plaster).
- **Special:** FF = `Fireplace_300`.

```
      0  1  2  3  4  5
     +##+##+FF+FF+##+##+
   4 #LM LM fp fp:BX BX#
     +           +     +
   3 #LM LM rg rg:.. CH#
     +           +     +
   2 #SH .. .. ..d.. ..W
     +           +==+==+
   1 #PN TB TB .. .. ..W
     +                 +
   0 tPN TB TB Sf .. WPt
     +==+ww+==+ee+==+ww+
```

**Props:**
- `Prop_Loom` (1.5, 6.0) 0
- `Rug_300x150` (4.5, 5.25)
- `Prop_Stool` (3.75, 5.25) and (5.25, 5.25)
- `Bed_Box` (7.5, 6.75) 0
- `Chest` (8.25, 5.25) −90
- `Shelf_Wall_150` on the west wall, segment y 3.0–4.5
- `Pantry_Shelves_300` (0.75, 1.5) 90
- `Table_Trestle_300` (3.0, 1.5) 0
- `Form_300` (3.0, 0.75) and (3.0, 2.25)
- `TableDress_Meal_A` (3.0, 1.5)
- `LogBasket` (8.25, 0.75) 0

**Spawn** `front` (5.25, 1.60).

### Townhouse ground floor: `VKI_Townhouse_F0`

- **Zones:**
  - hall: cols 0–4 all rows, plus cols 5–6 rows 0–1; Flag / PlasterWhite
  - kitchen: cols 5–6 rows 2–4; FlagRustic / StoneIn
- **Walls:** perimeter and kitchen partitions Stone (O).
- **Special:** FF = `Hearth_300`.
- **Link:** `Stair_Up_150x450_RailR` at (0, 3.0), rot 0.

```
      0  1  2  3  4  5  6
     +##+WW+FF+FF+##+##+##+
   4 #^^rWP fp fp DR:OV ba#
     +  +           +     +
   3 #^^r.. rg rg ..d.. KWW
     +  +           +     +
   2 #^^r.. TB TB ..:.. ba#
     +  +           +==+==+
   1 #Ss .. TB TB .. DK DK#
     +                    +
   0 tCH Sf .. .. .. .. bxt
     +==+ee+==+==+ww+==+ww+
```

**Props:**
- `Chest` (0.75, 0.75) 90
- `LogBasket` (2.25, 6.75) 0
- `Table_Trestle_300` (4.5, 3.0) 0
- `Form_300` (4.5, 2.25) and (4.5, 3.75)
- `TableDress_Meal_B` (4.5, 3.0)
- `Rug_300x150` (4.5, 5.25)
- `Dresser` (6.75, 6.75) 0, hug
- `Desk_Merchant` (9.0, 2.25) 0
- `Crate` (9.75, 0.75) 180
- `Oven_150` (8.25, 6.75) 0, hug
- `Barrel_Water` (9.75, 6.75) 0
- `Worktable_150` (9.75, 5.25) −90
- `Barrel` (9.75, 3.75) 0

**Spawns:** `front` (2.25, 1.60); `stairA` (0.75, 2.25), facing 180.

### Townhouse upper floor: `VKI_Townhouse_F1`

- **Zones:**
  - solar: cols 0–4; Boards_NS / PlasterCream
  - chamber: cols 5–6; Boards_NS / PlasterCream
- **Walls:** perimeter Timber; partition x = 7.5 is Board with PlasterCream.
- **Link:** `Stair_Down_150x450_RailR` at (0, 3.0), rot 0.
- **No exit.**

```
      0  1  2  3  4  5  6
     +##+WW+##+##+WW+##+##+
   4 #vv Ss LM LM CH:HT HT#
     +  +           +     +
   3 #vvr.. LM LM ..:HT HT#
     +  +           +     +
   2 #vvr.. .. .. ..d rg rgW
     +rr+           +     +
   1 #SW .. tb .. ..:.. CH#
     +              +     +
   0 t.. .. .. .. ..:.. ..t
     +==+ww+==+==+==+ww+==+
```

**Props:**
- `Prop_Loom` (4.5, 6.0) 0
- `Chest` (6.75, 6.75) 0, hug
- `Bed_HalfTester` (9.0, 6.0) 0
- `Rug_300x150` (9.0, 3.75)
- `Chest` (9.75, 2.25) −90
- `Prop_SpinningWheel` (0.75, 2.25) 0
- `Table_Small` (3.75, 2.25) 0
- `Prop_Stool` (3.75, 1.5) and (3.75, 3.0)
- `Candle_Plate` on the table

**Spawn** `stairA` (2.25, 6.75), facing 90.

### Tavern ground floor: `VKI_Tavern_F0`

- **Zones:**
  - hall: Boards_EW / PlasterOchre
  - hearth: cols 2–3 rows 4–5; Flag
  - bar: cols 7–8 rows 0–3; Flag
  - kitchen: cols 7–8 rows 4–5; FlagRustic
- **Walls:** perimeter and kitchen partitions Stone (O).
- **Special:** FF = `Hearth_300`, instance style `wall_a=StoneInWarm`.
- **Link:** `Stair_Up_150x450_RailR` at (0, 4.5), rot 0.

```
      0  1  2  3  4  5  6  7  8
     +##+##+FF+FF+WW+##+##+##+##+
   5 #^^rWP fp fp .. BS BS:OV KW#
     +  +                 +     +
   4 #^^r.. fm fm tb .. ..d.. baW
     +  +                 +==+==+
   3 #^^r.. .. .. .. .. .. CE ..#
     +                          +
   2 #Ss TB TB .. TB TB .. CT CK#
     +                          +
   1 W.. TB TB .. TB TB .. CT CK#
     +                          +
   0 tbx .. .. Sf .. .. .. .. bxt
     +==+ww+==+ee+==+==+ww+==+==+
```

**Props:**
- Hearth area:
  - `LogBasket` (2.25, 8.25) 0
  - `Form_300` (4.5, 6.0) 0
  - `Prop_BarrelStack` (9.0, 8.25) 0
  - `Table_Barrel` (6.75, 6.75) with `TableDress_Tavern_C`
- Table sets:
  - `Table_Trestle_300` (3.0, 3.0) and (7.5, 3.0)
  - `Form_300` at (3.0, 2.25), (3.0, 3.75), (7.5, 2.25), (7.5, 3.75)
  - `TableDress_Tavern_A` / `_B` on the tables
- Bar:
  - `Bar_Counter_150` (11.25, 2.25) −90 and (11.25, 3.75) −90
  - `Bar_End_150` (11.25, 5.25) −90
  - `CaskRack_150` (12.75, 2.25) −90 and (12.75, 3.75) −90
- Crates: `Crate` (0.75, 0.75) 180 and (12.75, 0.75) 180
- Kitchen:
  - `Oven_150` (11.25, 8.25) 0, hug
  - `Worktable_150` (12.75, 8.25) 0, hug
  - `Barrel_Water` (12.75, 6.75) −90
- `Lantern_Wall` on:
  - the north wall, segments x 1.5–3.0 and 7.5–9.0;
  - the west wall, y 3.0–4.5;
  - the east wall, y 1.5–3.0 and 3.0–4.5.

**Spawns:** `front` (5.25, 1.60); `stairA` (0.75, 3.75), facing 180.

**Sills:** x = 3.0 and x = 6.0 (y 6.0–7.55); y = 6.0 (x 3.0–6.0); x = 10.5 (y 0–6.0).

### Tavern guest floor: `VKI_Tavern_F1`

- **Zones:**
  - corridor: row 3 plus the landing, col 1 rows 4–5; Boards_EW / PlasterOchre
  - rooms: Boards_NS
- **Walls:** perimeter Timber (SHUTTER Red); partitions Board (BoardsV).
- **Link:** `Stair_Down_150x450_RailR` at (0, 4.5), rot 0.
- The partition at y = 4.5 starts at x = 1.5, with a Mid post at its free end. The stair's south rail closes col 0.

```
      0  1  2  3  4  5  6  7  8
     +##+##+##+##+WW+##+WW+##+##+
   5 #vv Ss:BX BX CH:DR CH HT HT#
     +  +  +        +           +
   4 #vvr..:tb .. ..:.. .. HT HT#
     +  +  +==+dd+==+dd+==+==+==+
   3 #vvr.. .. .. .. .. .. .. ..W
     +  +==+dd+==+==+dd+==+==+dd+
   2 #bd .. bd:bd .. bd:bd .. bd#
     +        +        +        +
   1 Wbd .. bd:bd .. bd:bd .. bdW
     +        +        +        +
   0 t.. CH ..:.. CH ..:.. CH ..t
     +==+ww+==+==+ww+==+==+ww+==+
```

**Props:**
- Room N1:
  - `Bed_Box` (4.5, 8.25) 0
  - `Chest` (6.75, 8.25) 0
  - `Table_Small` (3.75, 6.75) 0 with a `Candle_Plate`
- Room N2:
  - `Dresser` (8.25, 8.25) 0, hug
  - `Chest` (9.75, 8.25) 0
  - `Bed_HalfTester` (12.0, 7.5) 0
- South rooms:
  - `Bed_Straw` at (0.75, 3.0), (3.75, 1.5), (5.25, 1.5), (8.25, 1.5), (9.75, 1.5), (12.75, 1.5), all rot 0
  - `Chest` (2.25, 0.75), (6.75, 0.75), (11.25, 0.75), all 180, each with a `Candle_Plate`
- `Lantern_Wall` on the north wall, segments x 3.0–4.5 and 7.5–9.0.

**Spawn** `stairA` (2.25, 8.25), facing 90.

### Smithy: `VKI_Smithy_F0`

- **Zones:**
  - main: EarthSooty / StoneIn (default tint, not Dark)
  - forge: cols 3–4 rows 2–4; FlagRustic
  - store: cols 0–1 rows 0–1; EarthSooty, Board partitions (BoardsV)
- **Special:** FF = `Forge_300`.
- **Exit:** `EE EE` at cols 3–4.

```
      0  1  2  3  4  5  6
     +##+##+##+FF+FF+WW+##+
   4 #WR .. BL fg fg CO GR#
     +                    +
   3 #GS .. AN .. .. QT ..#
     +                    +
   2 W.. .. .. .. .. .. WB#
     +==+==+              +
   1 #ir ..d.. .. .. .. WB#
     +     +              +
   0 tbx bx:.. EE EE .. ..t
     +==+==+==+EE+EE+ww+==+
```

**Props:**
- Along the north wall:
  - `Prop_WeaponRack` (0.75, 6.75) 0, hug
  - `Prop_Bellows` (3.75, 6.75) 180
  - `CoalBin_150` (8.25, 6.75) 0
  - `GoodsRack_150` (9.75, 6.75) 0, hug
- Work area:
  - `Prop_Anvil` (3.75, 5.25) 0
  - `QuenchTrough_150` (8.25, 5.25) 0
  - `Prop_Grindstone` (0.75, 5.25) 90
- East wall:
  - `Workbench_300` (9.75, 3.0) −90
  - `ToolWall_150` on the east wall, y 1.5–3.0 and 3.0–4.5
- Store:
  - `IronStock_150` (0.75, 2.25) 90
  - `Crate` (0.75, 0.75) 180 and (2.25, 0.75) 180

**Spawn** `front` (6.0, 1.60). The work cells (3,3) and (4,3) lie between anvil, forge and quench.

### Workshop: `VKI_Workshop_F0`

- **Zone** `all`: FlagRustic / PlasterWhite.
- **Walls:** Timber.

```
      0  1  2  3  4  5
     +##+WW+##+WW+##+##+
   4 #WB WB GR .. PL PL#
     +                 +
   3 #.. .. .. .. .. ..W
     +                 +
   2 W.. SH .. HH .. ..#
     +                 +
   1 #ba .. .. .. .. bx#
     +                 +
   0 tbx .. Sf .. WP bxt
     +==+ww+ee+==+ww+==+
```

**Props:**
- North wall:
  - `Workbench_Carpenter` (1.5, 6.75) 0, hug
  - `ToolWall_150` on the north wall, x 0–1.5, and on the west wall, y 4.5–6.0
  - `GoodsRack_150` (3.75, 6.75) 0
  - `PoleLathe` (7.5, 6.75) 0, hug
- Floor:
  - `Prop_Sawhorse` (2.25, 3.75) 0
  - `Hearth_Open` (5.25, 3.75) 0
- Storage:
  - `Barrel` (0.75, 2.25) 0
  - `Crate` (0.75, 0.75) 180, (8.25, 2.25) 0, (8.25, 0.75) 180
  - `LogBasket` (6.75, 0.75) 0

**Spawn** `front` (3.75, 1.60).

### Chapel: `VKI_Chapel_F0`

- **Zones:**
  - nave: rows 0–3; FlagWarm / AshlarIn
  - dais: rows 4–5; `Floor_Dais_300` at (0,6), (3,6), (6,6), (9,6), style Flag
- **Walls:** SW/SE Full pillars; Ashlar Mid responds on the side walls at y 3.0 and 6.0.
- **Exit:** `EE EE` at cols 3–4.

```
      0  1  2  3  4  5  6  7
     +##+##+LL+LT+LT+LL+##+##+
   5 #CH .. cd .. .. cd .. ..#
     +                       +
   4 #.. .. .. AL AL LC .. ..#
     +rr+rr+rr+     +rr+rr+rr+
   3 L.. PW PW .. .. PW PW ..L
     +                       +
   2 #.. PW PW .. .. PW PW vr#
     +                       +
   1 L.. PW PW .. .. PW PW ..L
     +                       +
   0 #FT .. .. EE EE .. .. ..#
     +==+ll+==+EE+EE+==+ll+==+
```

**Props:**
- Pews: `Pew_300` at (3.0, y) and (9.0, y) for y ∈ {2.25, 3.75, 5.25}, rot 180.
- `AltarRail_150` along y = 6.0 from x 0, 1.5, 3.0, 7.5, 9.0 and 10.5, rot 0. The gap at x 4.5–7.5 is the aisle.
- On the dais (z 0.20):
  - `Altar_300` (6.0, 7.5) 0, with `vki_warn_ok="window"`
  - `CandleStand_Pricket` (3.75, 8.25) and (8.25, 8.25)
  - `Lectern` (8.25, 6.75)
  - `Chest` (0.75, 8.25) 90
- Nave:
  - `Font` (0.75, 0.75), hug
  - `VotiveRack` (11.25, 3.75) −90
  - `Runner_150` (6.0, 2.25) and `Runner_300` (6.0, 4.5)

**Spawn** `front` (6.0, 1.60).

### Links

| Scene | Link id → target |
|---|---|
| Hovel, Cottage, Smithy, Workshop, Chapel | `front` → `@return` |
| Townhouse_F0 | `front` → `@return`; `stairA` → `VKI_Townhouse_F1` |
| Townhouse_F1 | `stairA` → `VKI_Townhouse_F0` |
| Tavern_F0 | `front` → `@return`; `stairA` → `VKI_Tavern_F1` |
| Tavern_F1 | `stairA` → `VKI_Tavern_F0` |

### Which exterior uses which interior

The stamping itself happens later, with the export.

| Interior | Exterior builders |
|---|---|
| Hovel | `build_hovel`, `build_longhouse` (people end), `build_logcabin`, `build_woodcutter`, `build_forester_hut`, `build_fisher_hut` |
| Cottage | 1-storey `build_house_v` / `build_house` / `build_L_v` / `build_L_house` |
| Townhouse | 2+ storey versions of the above, `build_merchant_house`, `build_townhouse_gablefront`, `build_corner_house`, `build_terrace`, `build_skyline_street` units, `build_tower_house` |
| Tavern | `build_inn`, `build_tavern`. The inn's third storey is not enterable. |
| Smithy | `build_smithy`, `build_blacksmith` |
| Workshop | `build_pottery`, `build_tannery`, `build_dyers_yard`, `build_brewery`, `build_bakery`, `build_watermill`, `build_windmill`, `build_smokehouse` |
| Chapel | `build_chapel` |

Every other builder is **not enterable this round**.

### Blender layout

- One scene per floor as named above, plus `VKI_Test` (seam rigs) and `VKI_LookTest`.
- Collections per scene: `VKI_<S>_Shell`, `_Props`, `_Logic` (spawns, root, light and FX anchors) and `_Lights`. Always pass an explicit collection.
- Scenes copy VillageKit's engine, EEVEE settings and view transform/look/exposure.
- Worlds `W_VKI_Day` / `W_VKI_Night`: camera rays see void `#0B0908` (Light Path "Is Camera Ray"); lighting colour per preset.
- **Never edit `MC_World` or `VK_Sun`.**
- Scenes are rebuilt only by `vki_build_scene(name)` / `vki_build_all()`.

### Unity metadata

| Where | Properties |
|---|---|
| Link instances | `vki_link` (exit / stair_up / stair_down), `vki_link_id`, `vki_target`, `vki_prompt`, `vki_trigger` "[cx,cy,cz,sx,sy,sz]" in piece-local coordinates, `vki_facing_min`=60 |
| Spawn empties `SPN_<id>` (single arrow) | `vki_spawn_id`, `vki_facing_deg` |
| `VKI_Root` | `vki_building`, `vki_floor`, `vki_cam_mode`, `vki_cam_dist`, `vki_cam_target`, `vki_cam_pitch`=50, `vki_cam_yaw`=0, `vki_bounds`, `vki_default_spawn` |
| `LGT_*` empties | `vki_light` JSON {type, color, intensity, range, flicker, shadows, blender_w} |
| `FXA_*` empties | `vki_fx` |

**Trigger and spawn defaults:**

| Link | Trigger (local) | Spawn (local) |
|---|---|---|
| Door exit | centre (0.75, −0.65, 1.0), size (0.9, 0.8, 2.0) | (0.75, −1.60), facing into the room |
| Wide exit | (1.5, −0.65, 1.0), size (1.9, 0.8, 2.0) | (1.5, −1.60) |
| Stair_Up | as §3.3 | (0.75, −0.75), facing 180 |
| Stair_Down | as §3.3 | (2.25, 3.75), facing 90 |

### Lighting

Start values; tune them in G1.

| Light | Day | Night |
|---|---|---|
| `VKI_Key` (SUN, elevation 62°, from the SSW, angle 8°, shadows as G1 decides) | 1.0 | 0.35 moon (.62, .70, 1.0) |
| `VKI_Fill` (SUN, shadowless, along the view direction) | 0.5 | 0.2 |
| Window spots (60° cone, 2 m outside, aimed through the opening) | 350 W (.82, .88, 1.0) | 60 W (.62, .70, 1.0) |

- **Lancets:** spots tinted by the glass.
- **Exit apron:** a cool AREA light.
- **Sockets:** hearth 250–400 W (1, .52, .22); forge 450–900 W (1, .45, .15) plus 150 W bed glow; oven 150 W; lantern 60 W; candles 15–30 W.
- All sockets come from the masters' `vki_lights`. The same data creates the Blender lights and the Unity `LGT_` empties.

---

## 7. Code organisation

- **Folder:** `src/interior/`. `kit_sync` scans recursively and needs unique basenames.
- There are **no edits** to `vk_helpers`, `vk_mat`, `vk_kit`, `KIT_MODULES`, `EXTRA_SPECS` or exterior generators.

| Text | Owner | Contents |
|---|---|---|
| `vki_core` | core | Constants, slots and `VKI_TILE`. `VKIKit(Kit)` with `box` (world-locked zero offset), `project` (VKI_TILE, coping switch), `finish` (§2.8 and §4.1). `vki_mats`, `VKI_MAT_MAP`, `vki_apply_mats`. `VKI_SLOT`, `VKI_STYLE_MATS`, `vki_variant_mesh`, `vki_refresh_variants`. `vki_wobble`, `vki_vnoise`, `vki_textile_map`, `VKI_TEXTILE_CELLS`. `VKI_SPECS=[]` holding `(name, fn, finish_kw, pkg)`. `VKI_REUSE`. `VKI_TEXTS` (load order). `vki_ns()`, `vki_rebuild(names)`, `vki_adopt(names)`, `vki_place(coll, piece, x, y, rot=0, z=0, style=None, mount=None, **props)`. `vki_scene`, `vki_rig`, `vki_shot(scene, name, mode="game"/"plan", D=None)` (temporary ortho for plans; restores the camera; renders to `renders/interior/<scene>/`). `vki_ws(agent)`, `vki_ws_build(agent, names)`, `vki_ws_shot`. |
| `vki_tex`, `vki_textiles` | core | generators (§4.2); executed on demand, not part of `vki_ns` |
| `vki_test` | core | harness (§9) |
| `vki_fam_timber`, `vki_floors` | core | Timber family, floors, sills, `Leaf_Plank_*`, `Apron_300x150`, `RushMat`, `Rug_300x150`, `Test_Axis` |
| `vki_fam_stone`, `vki_fam_board`, `vki_props_smithy` | PKG-S | |
| `vki_fam_wattle`, `vki_fam_ashlar` | PKG-W | |
| `vki_links`, `vki_props_chapel` | PKG-L | |
| `vki_props_home` | PKG-H | |
| `vki_props_tavern` | PKG-T | |
| `vki_rooms` | assembly | `VKI_PLANS` (the §6 ASCII), `VKI_ROOMS[scene]`, the parser and assembler, `vki_check`, `vki_build_all` |

**`VKI_ROOMS[scene]` holds:**
- `size`, `family` (perimeter and partition)
- `zones` {name: {cells, floor, wall, cap}}
- `specials`, `props` [(piece, x, y, rot, style, mount)]
- `spawns`, `links`, `camera`, `preset`

**Rebuild behaviour:**
- `vki_rebuild` builds into a temporary object, then copies geometry, materials and properties into the existing master. New masters are created hidden in `VKI_Pieces`.
- It then refreshes `VARI_*`.
- Neither `vki_rebuild` nor `vki_ws_build` copies `ws_build`'s smoothing loop.

**Bootstrap and loader:**
```python
g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"]()
# vki_ns(): g=vk_kit_ns(terrain=False) from text vk_kit; exec vki_core into g; then each VKI_TEXTS entry present, in order
```

**Workshop scenes:**
- `vki_ws(agent)` calls `ws_scene("vki_"+agent)`, assigns `W_VKI_Day`, hides `_Ground`, unlinks `VK_Sun` from that scene only, and links `VKI_Key`/`VKI_Fill`.
- `vki_ws_build` is `ws_build` with `VKIKit`, the package's `VKI_SPECS`, an `SM_VKI_` check and the ownership guard.

---

## 8. Build plan

**Working agreements:**
- Verify at full resolution after every change.
- The coordinator saves the .blend after each completed step. Package engineers never save.
- No Unity export.
- Push only your own texts.
- Report to the user at the two gates; do not expand scope unasked.

### (a) Core stage (one engineer, sequential)

| Step | Deliverable | Acceptance |
|---|---|---|
| C1 | `vki_core`, the `vki_test` skeleton, `Test_Axis`, `VKI_Test`; the sRGB `Col` test quad | T1, T7, T8, T10, T14, T15, T18 pass on a smoke piece |
| C2 | All §4.2 textures including Textiles, all §4.3 materials, `vki_apply_mats()` | One generator per call. A 3×3 tiling render per texture shows no seam and no standout feature. Palette targets met. Window spot passes through the glass. |
| C3 | Timber family (17); floors (7); `Leaf_Plank_Full/_Cut`; `Apron`, `RushMat`, `Rug_300x150`; the rigs; `VKI_LookTest` (a 6×5 Timber room with every Timber kind, a Board partition, Boards and Flag floors, reused props) | T1–T4, T6–T14 and T18 pass. Seam-board renders (ortho top at 2 px/cm, and the game camera). |
| **Gate G1** | Show the user the look test | Decisions to record: rake vs pillar; closed vs ajar exit leaf; wobble and sag on/off; key shadows on/off; Day/Night levels; door width |
| C4 | **Vertical slice:** the Cottage complete. `Fireplace_300` F/C by core; the Cottage's PKG-H props (Bed_Box, Chest, Shelf_Wall_150, Pantry_Shelves_300, Table_Trestle_300, Form_300, LogBasket, TableDress_Meal_A) by one PKG-H engineer; assembler MVP in `vki_rooms` | `vki_check` returns `[]`; T12 and T19 pass; game and plan renders, Day and Night |
| **Gate G2** | Show the user the cottage slice | Go-ahead for the fan-out |
| C5 | Freeze: write `docs/INTERIOR_KIT.md` (this spec plus gate decisions); push texts; save | |

### (b) Parallel packages (up to 5 engineers, one Blender)

**Rules for every package:**
- Own only your texts and scene `WS_vki_<pkg>`.
- **Read-only for you:** `vki_core`, `vki_tex`, `vki_textiles`, `vki_test`, every `M_VKI_*` and `T_VKI_*`, `W_VKI_*`, `VKI_Key`, `VKI_Fill`.
- Never call `vki_rebuild`, `vki_adopt`, `vki_apply_mats`, `full_rebuild`, `apply_pbr_all` or any generator.
- No save. No `bpy.ops` except rendering. Calls under about 20 s (at most about 6 pieces per call).
- Slots 0–66 and the whitelisted overrides only. Names from your list only.
- **Hand-in:** `vki_test_pieces(names)` returns `{}`; a full-resolution catalog render; `ws_stats` inside the budgets.
- Fixes after adoption go through the coordinator's `vki_rebuild`.

| Package | Pieces | Specific checks |
|---|---|---|
| **PKG-S** | Stone (21), Board (10), `Leaf_Wide_Cut_L/R`, §5.3 P1 (8) | T4 rigs (Stone L/T/X/end, P into O). Pop-out stones match the painted stones in an ortho close-up. Forge and Hearth clip check (T17 on a rig render). |
| **PKG-W** | Wattle (15), Ashlar (12) | Sag and bow stay inside the envelope (T3, T13). Soot band present. The triple-lancet render reads, with the glass unclipped. |
| **PKG-L** | `Stair_Up/Down_150x450_RailR`, `Floor_Dais_300`, `FX_WindowPool`, (`FX_DoorSpill` if G1 picks ajar), `Runner_300`, `Runner_150`, §5.4 chapel P1 (7) | An up/down pair at the same origin: down risers visible from the game camera; no stair vertex inside any wall or post envelope; triggers and spawns separated. Runners chain seamlessly. |
| **PKG-H** | the rest of §5.1 P1 (≈15), then P2 | Footprints equal `vki_fp_cells`. Backs on the proud line (gap ≤ 0.005). Table dressing snaps at 0.80. Beds read from above. |
| **PKG-T** | §5.2 P1 (8), then P2 | Bar tops continuous at 1.5 m. Flap `hinge_axis` correct. Foam discs readable at D = 20. Every lighting prop has `vki_lights`. |

### (c) Assembly (one engineer)

1. `vki_adopt` everything, then `vki_rebuild()`.
2. Build the 9 scenes with `vki_build_all()`.
3. `vki_check` returns `[]` for every scene.
4. Run T5, T15, T16, T17 and T19.
5. Render each scene: fit shot and plan, Day and Night where relevant.
6. Save.

### (d) Review

1. Inspect every render at full resolution: seams, junctions, occlusion, glow clipping, repetition, and exterior/interior pairs.
2. Fix, then show the user.
3. Update `KIT_README` (interior section), regenerate `PIECES.md` (fixing its slot count) and update `HANDOFF.md`.
4. Save. Commit only when the user asks.

---

## 9. Acceptance tests

### Automated

`vki_test_all()` returns `{}`. T5, T16, T17 and T19 run at the assembly stage.

| Test | What passes |
|---|---|
| **T1 bounds** | Geometry lies within `vki_footprint` ± 1e-5. Walls: z ∈ [−0.30, H] (specials to H + 0.04); pop-outs ≤ 0.06 proud. Posts inside their envelope, z ∈ [−0.30, H + 0.04]. Floors inside [0,S]², z ∈ [−0.10, 0]; dais top 0.20. |
| **T2 end profiles** | Boundary vertices at x = 0 and x = L equal the family's `Plain_150A` profile at that height (1e-5). Full = Cut for z ≤ 0.65. A rake equals Cut for x ≤ 0.32 from the low end and Full near the high end. |
| **T3 node zone** | Within 0.32 of a piece-end node, geometry is the plain section or lies inside the envelope x ∈ [0.02, 0.33], \|y\| ≤ POST_HW − 0.01, z ≤ post top. Clear openings lie in [0.33, L − 0.33]. |
| **T4 coverage rigs** | L, T, X, free end, Full→Cut step, family step, P-into-O tee, per family: wall vertices in the node square lie inside the post (margin 0.005), and 2 cm vertical ray grids over each node hit post faces first. |
| **T5 coplanar** | No same-facing triangle pairs with n·n > 0.999 and plane distance < 1e-4 between rig or scene objects, except pairs whose overlap centroid lies inside a post box. |
| **T6 UV continuity** | Walls in 150\|300\|150 runs at rot 0/180/0, and Full next to Cut: world-locked loops coincide modulo 1 (1e-4). Floors: Q150 parity and 300/600 at even nodes tile continuously. |
| **T7 closed solids** | Every edge has exactly 2 faces. |
| **T8 normals** | 0 flipped faces after recalculating on a copy. |
| **T9 budgets** | Wall_150 Full ≤ 1500, Wall_300 Full ≤ 2500, Cut ≤ 700 / 1200, posts ≤ 400, floor ≤ 12 (Q) / 24, specials ≤ 6000, leaves ≤ 800, props per §5, scene ≤ 150k. |
| **T10 metadata** | Required `vki_*` properties present. Name matches `^SM_VKI_…`. `vki_cut_pair` reciprocal; `vki_cut_to` targets exist. Footprint = bbox. Triggers on the room side. |
| **T11 placement** | Structure on the 1.5 lattice. FLOOR-face pieces at even nodes, or Q parity matching their node. Props on 0.75 unless `vki_hug`. Rotations are multiples of 90; `world0` pieces at 0; `Stair_Up` never at 180; up/down pairs share origin and rotation. |
| **T12 room rules** | **Errors:** a missing post at L/T/X or a height/family step (free ends warn); floor coverage gaps or overlaps (Stair_Down footprints excepted); a door without free cells on both sides; a spawn capsule (r 0.3) within 0.2 m of a trigger; a prop intersecting a wall/post envelope or another prop; Window/Lancet/Special/wall_hung props on Cut runs; `vki_mount_zmax` above the host wall's H − 0.14; a missing link or `SPN_<id>`; BFS (capsule r 0.3 on a 0.25 m raster; dais step ≤ 0.25) failing to reach every use point and trigger from every spawn. **Palette:** cap luma ≥ floor + 0.15; prop-top vs floor luma difference ≥ 0.12. **Warnings:** R-occ1–6. |
| **T13 wobble** | \|Δy\| ≤ A. Zero within 0.32 of nodes and pins, at z ≤ 0.16 and within 0.25 of the cap. Body stays within CAP_HW − 0.005. |
| **T14 materials** | 67 slots, and `kit_mats()[54].name == "M_VK_Hewn"`. No face index ≥ 67; no banned slot. The GLOW/WINDOW/STAINED/DRESS overrides are present on every VKI master. |
| **T15 exterior invariance** | Hashes (vertices, UVs, Col, material names) of **all** `SM_VK_*` masters, plus the node trees of `M_VK_Glow`, `M_VK_Window` and `MC_World`, are unchanged after `vki_ns()` + `vki_rebuild()`. |
| **T16 determinism** | Two rebuilds give identical vertex, UV and Col hashes. |
| **T17 render clip** | In each render, fewer than 0.3% of pixels have min(RGB) ≥ 0.98, measured on the PNG through `bpy.data.images`. |
| **T18 namespace** | `ast` over every VKI text: top-level names start with `vki_`/`VKI_` or are `VKIKit`, and none appears in `vk_kit_ns(terrain=False)`. |
| **T19 visibility** | For the scene camera (fit target, or a 1.5 m grid inside the follow clamp), `scene.ray_cast` to every `vki_use` point, trigger centre and spawn at z 0.5: the first hit lies within 0.3 m of the point. |

### Visual

1. **Seam boards per family:** straight runs, junction rigs, Full/Cut/Rake transitions and floor parity junctions, in ortho and the game camera, inspected at full resolution. Look for: no steps, UV jumps or lighting seams; a pale, continuous cap outline.
2. **Look test** (Day and Night):
   - cut caps read as real members;
   - the hidden near strip matches §1;
   - limewash is even, with no repeating marks;
   - window pools are brighter than the mean floor;
   - the exit leaf reads as a door.
3. **Per scene, in game view and plan:**
   - walkways read as walkways;
   - nothing interactable is hidden;
   - tall props stand against far walls;
   - fire is the brightest thing on screen and the windows come second (cool);
   - no 3 m repetition is visible;
   - mean walkable-floor luma ≥ 0.25 by Day and ≥ 0.15 by Night.
4. **Exterior/interior pairs:** palette, family and shutter colour continue from outside to inside (e.g. inn: stone ground floor with Ochre limewash, Red shutters).
5. **Stairs:** the up flight reads as rising through the ceiling, and the down hole shows its risers.

---

## Open questions for the user

1. **Characters:** will they be live 3D or pre-rendered sprites? If sprites, the interior pitch must match the sprite pitch. This spec locks 50°, the colony camera's pitch.
2. **Camera indoors:** is yaw fixed and zoom allowed only within 14–22 m? Cut walls are authored for a camera looking north.
3. **View transform:** keep AgX Medium High Contrast (−0.2) to match the exterior renders, or switch the interior scenes to Standard? An earlier project note says AgX washes out flat stylised colour.
4. **Enterable buildings this round:** is the §6 mapping right? It leaves out barns, granaries, stables and the town hall, the inn's third storey, a cottage loft and a tavern cellar, all deferred.
5. **Smithy exterior:** its only door is blocked by the forge chimney. Fix it now (door moved to bay 1, `front="WD"`) or together with the export work?

---

## 10. Amendments after the core stage (2026-09-26)

Everything below overrides the sections it names. Each line gives the change and, after the dash, the reason. Package engineers build to this section where it differs from §0–§9. Code references are in `src/interior/`.

### 10.1 Geometry rules for every wall family

- **End planes are open (§2.2, §9 T7).** `VKIKit.finish` deletes the outward-facing faces of every `vki_class="wall"` piece that lie in its end planes x = 0 and x = L (`vki_open_wall_ends`; the master gets `vki_open_ends=1`) — every wall end is covered by a post or butts a neighbour with the identical profile (T2), and the end faces were coplanar with the half-stud / sole / cap end faces of the same piece (10–26 same-facing overlaps per wall, z-fighting at any free end).
- **A free wall end without a post is an ERROR (§2.3, §9 T12)**, no longer a warning — an open end plane shows the hollow inside of the wall. T12 now checks all post rules at object level (`vki_t12_posts`): L/T/X needs a Corner post, a height/family/class step or a free end needs a post, and the post is at least as tall as the tallest wall end at its node.
- **No same-facing coplanar faces inside one master (new test T5S).** Same-facing faces in one plane that overlap by more than 1e-6 m² are an error, buried or not; the only exception is a wall's end planes — hidden duplicates show the moment a neighbour changes, and the coordinator saw z-fighting in the catalog.
- **Tuck rule:** a member that butts into a cap, plate or lintel runs 5 mm into it (`VKI_TIM_TUCK`): studs, half-studs and cripple studs, the rake stud and rail stub, the fireplace throat; door sole plates and Full rail stubs run 1 cm under the jambs — so no end face shares a plane with a body top or a pier end (T5S).
- **Where two members must stay flush but share a face plane, separate them by ≥ 5 mm or trim one:** the Timber rake's sloped rafter is at |y| ≤ 0.275 (5 mm behind the flats, studs and rails, still inside CAP_HW); inside the fireplace breast the mid-rail is only its proud strip y 0.25–0.28; the firebox floor slab's bottom is at z −0.005; the leaf's ring pull leans 8° off the plank — each pair lay in one plane before.
- Curved members built as one strip (the 150B brace, `vki_band`) have several coplanar quads whose bounding rectangles overlap; they do not overlap in area — T5S (exact polygon clipping) is the reference, not a bounding-rectangle scan.

### 10.2 Timber pieces (§2.2, §3.2)

- **Door threshold is DRESS** (Full and Cut; C3 had made it oak, §3.2 named no material) — the dark oak board read as a solid dark rectangle in plan; dressed stone reads as a doorstep.
- **Door_150_Cut:** each jamb stops at 0.905 under one continuous cap block from the piece end to the opening (x 0–0.33 / 1.17–1.5, CAP top), so the cap wraps the reveal — the jamb top used to be split into 2–3 short blocks with V-notches (visual review r2).
- **Door_150_Cut reveal faces are limewash** (WALL_A, so they take the zone's plaster style; `VKI_TIM_REVEAL`, alternatives "planks" and "cap") — the 1.0 m oak reveal filled the 0.84 m N–S partition doorway from the north-looking camera. Measured reveal luma by Day: oak 0.05, scrubbed planks 0.18 (reads as a closed door), hewn cap 0.35 (merges with the cap top), limewash 0.45 (reads as the plastered side of an opening).
- Door piers end at the jambs' outer faces (x 0.19 / 1.31), and the footing under an opening tops out at z −0.10 (`VKI_TIM_FOOT_TOP`) — the pier end and the floor-level footing top were coplanar with the reveal and the floor.
- `Window_150_Cut`: the sill slab is |y| ≤ 0.28 (flush with the caps; §3.2 allows ≤ 0.30), and the cap segments run 0.04 into it — the Full and Cut footprints now match, and the 2 × 10 cm V-slots beside the sill are closed, which also moved the cap end ring off the Corner post face (a false T4 error).
- `Plain_300` keeps a stud at 1.5 as well as 0.75 and 2.25 — `Plain_300` = 150A ⊕ 150B, and every node shows one full stud.
- The footing band (body faces below z 0) is DRESS at t 1.5 and darker; the body's upward faces are oak; small oak plugs sit behind the half-stud tops (`vki_tim_body_finish`) — a pale limewash band showed under the sole, and a plaster speck showed at 150|150 joints.
- Cap tops keep their grain along the wall (`vki_top_faces(..., along=X)`) — short members such as jamb tops turned their grain across.
- **Post tops stay ENDGRAIN** (resolving §2.2, which says both CAP and ENDGRAIN): each top maps onto the one centred log end of `T_VK_EndGrain`, padded (`VKI_TIM_POST_FILL` 0.26: corners at uv radius 0.37, inside the 0.44 ring), so no bark and no second ring show. Seen from the game camera the square cuts the rings like a hewn beam end; it does not read as a round log slice. The hewn CAP cross-grain (`VKI_TIM_POST_TOP="cap"`) was tried: posts merge into the cap line and the nodes lose their accent.
- **Fireplace:** the hearth socket is at (1.5, −0.55, 0.85), not (1.5, −0.6, 0.5), at 400 W with a 0.40 m radius — at the spec position it blew the logs and flames out to white. The hearthstones and firebox floor are DRESS with soot toward the fire. The brick back and cheeks carry `vki_dark` 0.56 / 0.52 plus a 0.34 ramp (the bricks were nearly as bright as the flames). There are seven flame tongues with a brighter core profile (`VKI_TIM_FLAMES`, `VKI_TIM_FLAME_PROFILE`). The crane is swung out so the pot hangs at (1.0, −0.62), beside the fire — from the 50° camera it hid a third of the fire.
- **Leaves:** the hinge axis lies on the room-side face (planks at local y 0.004–0.084, room-side straps start 0.10 from the hinge) — centred planks swung into the jamb and the Corner post. The leaf measures 0.83 × 2.16 (Full) / 0.95 (Cut), 5 mm clear of the jambs; `vki_leaf_width` holds the measured 0.83 and `vki_leaf_clearance` = 0.005 (§3.3 said 0.84 × 2.20).
- **Apron:** it spans local y 0.15–1.65 (starting at the class P outer face) with the strip y 0.15–0.30 4 mm lower; the doorstone is two chamfered DRESS slabs, not STONE_BLOCK_IN; `M_VKI_ApronCobble` has a tint of (.74, .72, .70); the AREA light is 60 W Day / 25 W Night, not 120 / 40 — the apron must close up to class P doors too, never share z 0 with a footing, and not out-shine the windows.
- **Window spot** (`VKI_TIM_WIN_SPOT`, replacing §6's 60° / 350 W): at local (0.75, 2.0, 4.2), aimed at (0.75, −1.35, 0), cone 24°, blend 0.15, radius 0.05, 1000 W Day / 150 W Night — the pool now lands 0.7–1.5 m inside the room with glazing-bar shadows, and no longer puts hot patches on the caps.

### 10.3 Metadata and tooling (§3.4, §5, §7)

- **`vki_rebuild` refreshes instances:** after a rebuild it re-copies the master metadata onto every instance (its mesh, or a VARI_* mesh with that `vki_base`), keeping the placement-only keys (`VKI_PLACEMENT_KEYS` / `_PREFIXES`: vki_piece, vki_rot, vki_at, vki_style, vki_back_line, vki_back_y, vki_reuse, vki_mount, vki_host*, vki_hug*, vki_link*, vki_target, vki_prompt, vki_facing_min, vki_leaf_state, vki_leaf_deg, …) — instances used to ship stale footprints, lights and colliders in the FBX. New test **T10i** (in `vki_test_all`) compares every instance in the VKI_* / WS_vki_* scenes with its master.
- **Door pieces carry `vki_nav="door"` plus `vki_nav_open=[0.33, 1.17]`** (§3.4 nav values: block / walk / none / door) — a whole-piece "block" made a leafless doorway look blocked to a nav or BFS consumer. BFS should use `vki_collider`.
- **Hug at posts (§5 placement):** a `wall_floor` hug keeps 0.005 clear of every post square — placed posts, and inferred Corner posts at every junction node on the back-wall line — so it clamps at POST_HW + 0.005 (0.315 O / 0.215 P) from a side wall line near a node, not at the proud line. The limiter is recorded in `vki_hug_limit`. A post or junction inside the prop's span gives `vki_hug_fail` — the post squares reach 0.31 past the wall line (the proud line is 0.285), so hugged props sat 25 mm inside Corner posts. Assembler: skip rhythm Mid posts where a wall-backed prop spans the node (§2.3), or place props first.
- The shared `VKI_Key` / `VKI_Fill` hold the Day preset values at rest; `vki_shot` sets and restores presets and calls `vki_flush_lights` — Blender ignores light changes made in the same Python call as a render unless they are flushed.
- `vki_scene` forces `eevee.use_shadows = True` on every VKI scene (§6 said copy VillageKit, which has scene shadows off) — otherwise there are no window pools and no key shadows.

### 10.4 Camera (§1)

- **D_fit gets a 0.4 m far margin:** D_fit = (L + 1.5 + 0.4 + 1.428·h_fit) / 0.737 (`vki_fit_camera(bounds, family)`, `VKI_FIT_MARGIN`; `vki_shot` uses it when a scene has `vki_room_bounds` but no `vki_cam_dist`). The plain formula puts the north wall line on the top frame edge and cut off the far caps (+0.28) and post tops (+0.31). Ashlar gets no margin: its h_fit of 3.97 is a feature height below the 4.5 m wall top, which leaves the frame by design, so the chapel stays a fit scene at D 21.94. The look test becomes D 18.567, target (4.5, 3.803).

### 10.5 Look gate G1 decisions and final levels (§2.4, §3.2, §6)

Made by the coordinator. The user may override them; every alternative stays switchable (`VKI_G1` in `vki_core`).

| Decision | Choice | Alternative kept |
|---|---|---|
| Side-wall south corners | **Rake** (Cut-height SW/SE Corner posts) | pillar: `vki_looktest(pillar=True)`, Full plain piece + Full Corner post |
| Exit leaf | **Closed**; no `FX_DoorSpill` needed | ajar 30°: `leaf_deg=30` + PKG-L FX_DoorSpill |
| Wobble / cap sag | **On** (`VKI_FLAGS`) | off (imperceptible at D 18, costs nothing) |
| Key-light shadows | **On** (`VKI_Key.data.use_shadow`) | off (the room reads flat) |

| Light / material | Day | Night |
|---|---|---|
| `VKI_Key` (SUN 62°, SSW, angle 8°) | 1.0 (1, .95, .88) | 0.5 (.62, .70, 1.0) |
| `VKI_Fill` (SUN, shadowless, along the view) | 0.6 (.85, .90, 1.0) | 0.8 (.62, .70, 1.0) |
| World (lighting colour × strength) | (.52, .50, .46) × 0.65 | (.10, .12, .20) × 0.8 |
| Window spots | 1000 W (.82, .88, 1.0) | 150 W (.62, .70, 1.0) |
| Hearth socket | 400 W (1, .52, .22), radius 0.40 | same |
| Apron AREA | 60 W | 25 W |
| `M_VKI_Window_Day` / `_Night` strength | 0.65 (was 1.0 in §4.3) | 0.35 |
| `M_VKI_GlowIn` | pure emitter: core (1, .60, .16), rim (1, .13, 0), strength 2.2 − 1.6·rim (§4.3's colours rendered cream under AgX) | same |
| `M_VKI_FlagRustic` | tint 1.12 (BC display luma 0.373 → ~0.39, inside 0.25–0.45) | same |

The Night start values of §6 remain available as `VKI_NIGHT_SPEC`. These numbers drive both the Blender lights and the future Unity `LGT_` empties; the socket values live in the masters' `vki_lights`.

**Measured on the look test** (1920 × 1080 fit shots, `vki_lt_levels`: floor = world-rectangle metric; fire / glass / bricks / hearth = p90 luma (p95 for the glass) of the pixels whose camera ray hits a GLOW / WINDOW / BRICK / DRESS face):

| | Walkable floor | Fire | NE glass | Firebox bricks | Hearthstones |
|---|---|---|---|---|---|
| Day | **0.266** (≥ 0.25) | **0.787** | 0.721 | 0.487 | 0.473 |
| Night | **0.155** (≥ 0.15) | **0.787** | 0.501 | 0.484 | 0.456 |

The fire is the brightest thing by Day and by Night and the windows come second. T17 is clean on every render.

### 10.6 Test changes (§9)

- **T3:** a rake's low end uses the Cut reference and the Cut post top — the rake is Cut there by design (§2.4).
- **T4:** redefined per node (`vki_t4_coverage`).
  - The post must cover a **fixed node square**: ±POST_HW at L/T/X, the Mid square (±MID_HW along the wall × ±POST_HW across) at steps and free ends.
  - Every wall vertex inside that square must lie inside the post.
  - Every uncovered end-plane vertex (the open end outline) must lie inside the post.
  - A 2 cm ray grid over the square must hit the post first; rays in the chamfer corners are skipped.
  - Why: the old square came from the post's own bbox, so an undersized post always passed.
  - Validated: known-bad Mid post at an L, Cut post under Full walls, Mid post turned 90° at a step and a shifted post all fail; the C3 rigs and a Window_150_Cut beside a Corner_Cut (new rig WinCutL) pass.
- **T5:** skips overlaps whose front (2 mm along the normal) lies inside another solid — butt-joint faces that also sit on a floor joint cannot render.
- **T5S (new, per master):** as in 10.1. It is part of `vki_test_pieces` and validated on the pre-fix masters, where it found the half-stud/body-top and rake overlaps.
- **T7:** walls may have boundary edges only in their end planes and are closed everywhere else.
- **T10i (new):** as in 10.3.
- **T11:**
  - The FLOOR even-node / parity rule applies only when `vki_uv_lock == "world"`, because the Apron uses the FLOOR slot with its own t 4.0 UVs.
  - New check: `rot0_90` pieces (Floor_Sill_150) only at 0 or 90.
- **T12:** post rules at object level (10.1); room-level rules still need `vki_rooms`.
- **T13:** checks §2.6's cap ramp. §9's "zero within 0.25 of the cap" contradicted the formula. "Moved nothing" now counts only when some body vertex is eligible to move.
- **Levels:** the look-test floor luma uses world rectangles (`VKI_LT_FLOOR_RECTS`) rather than pixel boxes, so it survives camera changes. `vki_lt_levels` adds the material-masked fire / glass / bricks / hearth percentiles.
- **Still open for PKG-S:** the T4 FamStep and PintoO rigs need a second family.

### 10.7 Look-test and assembler notes

- The look test uses the Cottage footprint (hall FlagRustic, bedroom Boards_NS) with Timber Cut partitions, standing in for the Board family that does not exist yet.
- Every N–S Cut doorway gets an overlay mat on each side, never across the threshold. From the north-looking camera the reveal hides the doorway's floor.
- Keep sill runs straight: two `Floor_Sill_150` meeting at an L overlap in a 0.1 m square.
- Next to Corner posts, clear max(proud line, POST_HW + 0.005) — `vki_place` now does this.
- Specials (e.g. `Fireplace_300_Cut`) are never placed on Cut runs (T12).
- Every look-test render made before `vki_flush_lights` existed may show the previous call's light values; only `renders/interior/corefix/` is current.

## 11. Amendments after the package and assembly stage (2026-09-26)

The built kit is described in [docs/INTERIOR_KIT.md](../../INTERIOR_KIT.md). Changes to the spec made while the
packages and the nine rooms were built, each with its reason:

### 11.1 Pieces

- **Wattle window shutter** (§3.2): swung up against the wall above the opening (`VKI_WAT_WIN["shutter_deg"]` 170)
  instead of propped 55° inward. From the 50° camera any board propped into the room hides the opening; at 170° the
  daylight opening reads. Angles ≤ 120 still build the propped version with its stick.
- **Wattle `Door_150_Full`** has no leaf: `Leaf_Plank_Full` is 2.16 m and the opening 2.00 m. It is a leafless doorway.
- **Ashlar exit leaves**: the pointed `DoorWide_300` opens 1.60 m (0.70–2.30), so it takes the new
  `Leaf_Wide160_Cut_L/R` (0.795 m). The Stone `DoorWide_300` keeps `Leaf_Wide_Cut_L/R` (0.89 m).
- **`Apron_Wide_300x150`** (new, `vki_floors`): local x 0..3.0 at its `DoorWide_300`'s origin, with a three-slab
  doorstone. Centring `Apron_300x150` on a wide door put it 0.75 m off the 1.5 lattice (T11).
- **Stone specials**: `Hearth_300_Cut` is cut open from above so the fire shows; the hearth breast is stepped.
- **Home furniture tops** are pale hewn boards instead of `M_VKI_WoodScrubbed`, which rendered at floor luma (the §4.3
  prop-top rule failed). Tavern bar and table tops keep the scrubbed planks.
- **Table dressing sets** (`TableDress_Tavern_A/B/C`) use the furniture budget (1500 tris) instead of dressing (400).
- **Still water** (`M_VKI_WaterMurky`) is a flat dark material, roughness 0.6: the textured water broke the interior lights
  into white glitter, and a glossy flat surface mirrored the room. `Barrel_Water` uses it instead of the exterior
  `M_VK_Water`.

### 11.2 Light levels (supersede §3.2 / §6 values; the masters' `vki_lights` hold them)

- **Hearth_300**: POINT 400 W at (1.45, −0.60, 0.84), radius 0.40 (the §3.2 socket blew the fire out to white).
- **Forge_300**: 150 W at (1.5, −0.66, 1.85) plus a 25 W bed glow at (1.5, −0.82, 1.40). §3.2's 450–900 W burned the
  coals and slabs white and turned the room orange.
- **Hearth_Open**: 250 W at (0, −0.28, 0.74); **Oven_150**: 150 W at (0, −0.72, 1.05).
- Candles 15–30 W, lanterns 60 W (socket in front of the pane), all without shadows.
- **Measured levels** in the nine rooms (walkable floor luma): all pass except Townhouse_F1 0.187 and Smithy 0.221 by
  Day (target 0.25) and Tavern_F1 0.114 by Night (target 0.15). Left as warnings: the floors there are dark by design
  (Boards_NS, EarthSooty, a night guest floor), and Unity lighting will be set up separately.

### 11.3 Assembly

- The assembler (`vki_rooms`) made 15 plan changes, listed with reasons in `VKI_PLAN_CHANGES` (among them a Townhouse_F1
  plan typo, the chapel pews moved 0.75 m south, the tavern kitchen props pulled clear of the oven).
- Rhythm posts are skipped where a prop touches the post square; required posts go in first.
- A wall_floor prop whose hug fails stands 3 cm off its proud line (`vki_pull`). Between two O Corner posts there are
  2.37 m, so two 1.20 m wall-backed props or a `Bed_Box` never fit side by side without it.
- Edge pieces (the altar rail) may be let into walls and posts by up to `vki_edge_let_in` (0.32).
- `FX_WindowPool` is placed by Day only.
- Palette warnings remain where caps are dark stone by design: the Ashlar chapel (Dress caps), the Stone townhouse,
  and the tavern at night.

### 11.4 Tooling

- `vki_ns()` skips a package text that fails to load and reports it in `VKI_LOAD_ERRORS` (core texts still raise), so
  one engineer's broken push cannot stop the others.
- `vki_flush_lights` and `vki_depsgraph` handle scenes without a depsgraph (a non-active scene after a restart).
- **Blender 4.4 crash with parallel builders**: Blender's GPU-buffer garbage collector (`DRW_cache_free_old_batches`)
  walks every scene's depsgraph; after objects are deleted in a scene that is not being displayed, that depsgraph can
  still point at them, and Blender crashes with an access violation. Set
  `bpy.context.preferences.system.vbo_time_out = 0` (the collector then returns at once) whenever scripts rebuild
  scenes other than the one on screen. It crashed three times before this was found.
