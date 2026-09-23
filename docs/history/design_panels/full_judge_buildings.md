# Village Kit expansion: judge report and final spec (new house types and village features)

## 1. Verdict

### 1.1 Scores

| Criterion | P1 | P2 | P3 |
|---|---|---|---|
| Concreteness | 9 | 5 | 9 |
| Correctness / feasibility | 8 | 7 | 7 |
| Fit to the WoW-style colony-sim kit | 8 | 7 | 9 |
| Risk (10 = safest) | 7 | 7 | 6 |
| **Overall** | **8.0** | **6.5** | **7.8** |

- **P1** knows the code best and covers the most gameplay.
  - It follows the code's real rules: material slots are append-only, and `full_rebuild()` appends the missing slots.
  - It adds construction stages by piece substitution, stockpile fill levels, sockets, a housing ladder tied to colonist needs, and every production chain.
  - Weak points: it adds little skyline variety, and it has several geometry and placement errors (see §3).
- **P2 arrived truncated.** Its F1–F14 family definitions, its infrastructure section and half its buildings are missing, so nobody can build from it alone. What survived is useful:
  - the seam and risk list;
  - recipe JSON for Unity;
  - `Roof_X`, the cruciform church and the T-plan guildhall;
  - the flat-roofed keep.
- **P3 reads the renders best.** I checked its diagnosis against `nature_town_aerial.png` and it holds:
  - about 18 near-identical orange roofs;
  - only 3 blue, 1 green and 4 thatch roofs;
  - no way to tell a building's function from the colony camera.

  It also has the best skyline tools: a 3 m roof family, `roof_field()`, cross gables, half-hips, gable chimneys, ridge emblems, district weights, a neighbour rule, and wobble/grime rules. It refactors more of the core roof code than the others and has several geometry errors (see §3).

### 1.2 Base and grafts

**The base is P1:** its infrastructure, colony loop, housing ladder and chains. Grafted onto it:

- **From P3:**
  - the S roof family, `_Single` roofs and `roof_field()` (T, X, cross gable, half-hip);
  - StoneUp and PlasterUp upper floors with flat wobble and `grime=False`;
  - gable chimneys, vents, emblems, banners and bunting;
  - district weights and the neighbour rule;
  - shop goods as separate props;
  - open post bays, `Ceiling_Cell` and the turret stack;
  - the water datum, LVL = 1.5 and 4.243 m grid diagonals;
  - the wobble rule for pieces that are not 3 m long;
  - acceptance tests from the aerial camera.
- **From P2:**
  - recipe JSON and stripping unused material slots from the FBX;
  - checks for seams between stacked floors, exposed ends of lower roofs, corner-tower radius, and the gable-front alley;
  - `Roof_X`, the cruciform church, the T-plan guildhall and the keep, all scheduled late.

## 2. Contradictions resolved

| Topic | P1 | P2 | P3 | Decision | Reason |
|---|---|---|---|---|---|
| Material slots 45–49 | WATTLE, HIDE, PIGSKIN, COAL, MEAT | — | WATTLE, NET, GOLD, LEATHER, CANVAS | **WATTLE, HIDE, PIGSKIN, COAL, NET** | GOLD→BRONZE, CANVAS→CLOTH_B, LEATHER=HIDE, MEAT→APPLE |
| Wattle wall height | 2.4 | (H0) | 1.9 (longhouse 2.2) | **2.4**; doors only under gable-type ends | the thatch roll hangs ≈0.70 m below the wall top |
| Log wall height | 3.0 | — | 2.6 | **3.0** | keeps Porch, LeanTo, Stair_Ext and timber upper floors usable |
| Construction stages | 0–4 | 0–3 | 0–3 | **0 Site, 1 Walls, 2 Frame, 3 Done** | 4 distinct looks are enough |
| Roof depths | always 6 m | flat keep | S, M, L | **M plus S (3 m) now; L deferred** | S unlocks huts and cross gables cheaply |
| One-bay roof | `Roof_Gable1` | — | `_Single` | **`Roof_Single` / `RoofThatch_Single` / `RoofS_Single`** | same piece under one name |
| Diagonal of player-drawn walls | 2.121 | — | 4.243 | **4.243 on grid; 2.121 only for contour pieces** | see §3 |
| Town wall | 2.0 thick, walk 6.0, reuse guard tower | 1.5 thick, walk 5.8 | 1.6 thick, walk 5.0, new towers | **2.0 thick, walk 6.2, reuse `guard_tower`** | the hoarding floor top is 6.2 |
| Blue roofs | civic only | — | 12 %, including market | **civic/faith buildings and the noble district only** | keeps landmarks readable |
| Terrace frontage | eave-front plus gable-front with valleys | alley | party gables; gable-front stands alone | **eave-front terraces (Flush / Firewall / Cap); gable-front houses stand alone with a 1-cell alley; valley family deferred** | cost |
| Water wheel | overshot on a race | — | undershot | **undershot by default; overshot race only on hillsides** | a race on a flat map has no source |
| Gallery | posts from the ground | — | cantilever under the eave | **both: `Gallery_Timber` and `Gallery_Top`** | courtyards vs. street fronts |
| Oriel / turret | octagon r 0.95 | TowerS | stack r 1.0 at (−0.45, −0.45) | **stack r 1.1 at (−0.6, −0.6)** | the turret must contain the eave corner |
| Market hall | `Wall_Arcade` ×10 | — | posts + ceiling | **`Wall_Arcade_Open` + `Ceiling_Cell`** | the arcade module's loggia blocks the hall |
| Sockets | child empties of the root | recipe JSON | empties made in `finish()` | **stored as JSON on the piece, turned into empties by `place_v` under the root, also written to the recipe** | instances share mesh data only |
| Terrain step | Hs | TSTEP | 1.5 | **LVL = 1.5 (requested from the terrain track)** | 2 LVL = H1 |
| Water datum | water 0 (pier), bank 0 (bridge) | WZ | bank 0 / water −0.6 / bed −1.5 | **bank 0, water −0.6, bed −1.5, piles to −3.0** | one datum for everything |

## 3. Wrong claims in the proposals

**P1**

1. **Market hall "pure reuse, `Wall_Arcade` on all 10 perimeter modules": wrong.**
   - `wall_arcade()` builds a 2.6 m loggia behind each arch: a floor, a plank ceiling, and a plaster back wall with a door and window at local y = +2.6.
   - On a 6 m deep hall, the back walls of the two long sides stand 0.8 m apart, and the loggias of the end modules cut across them.
   - Fix: `Wall_Arcade_Open` plus `Ceiling_Cell`.
2. **Wall walk "z 6.0 = guard_tower hoarding floor": off by 0.2.** The hoarding floor box is centred at z0 + 0.1 and is 0.2 thick, so its top is 6.2.
3. **`TownWall_Stair` (12 steps of 0.25 × 0.25, rising 3.0 over 3 m) is 45°.** Two modules up to 6.2 would be 46°, steeper than the default Unity NavMesh maximum slope of 45°. Fix: three modules of 2.067 m rise each, 34.6°.
4. **Palisade and town wall `_Diag` = 2.121 is the wrong diagonal.**
   - 2.121 is the marching-squares contour diagonal (edge midpoint to edge midpoint).
   - Walls the player draws on cell edges need the cell diagonal, 4.243.
5. **Hovel front "WD" puts the door on the eave wall, under a low roof.**
   - The thatch eave roll is centred at the eave tip minus TRT/2, with radius ≈0.24, so its bottom is ≈0.70 m below the wall top.
   - With HW 2.4 that is 1.70 m above ground, 1.35 m out from the wall.
6. **Hovel `_LeanTo` on the back wall collides with the thatch.**
   - `lean_to()` meets the wall at z 3.0–3.3.
   - The wattle wall top is 2.4, and the thatch underside at the wall line is ≈2.1.
   - Fix: put the lean-to on a gable end, or add `LeanTo_Low`.
7. **"Two `Roof_Hip` make a pyramid, no new piece needed": the pyramid is right, but the finial is doubled.**
   - Each piece also adds its apex finial at local x = −1.5: an ico of r 0.24, a 0.7 m pole and a bronze ball.
   - Two pieces put two copies at the same point, rotated 180°: the pole faces are coplanar and the icos interpenetrate, which z-fights.
   - Fix: `finial=False` on the second piece.
8. **Merchant house: loading doors "in the same cell" under `Roof_Gable_Hoist` do not line up.**
   - The hoist hangs on the ridge line (end-wall y = 0), which is the seam between the two end modules centred at ±1.5.
   - The rope therefore hangs 1.5 m away from any loading door.
   - Fix: put stacked loading doors under `Roof_CrossGable_Hoist` on an eave bay.
9. **Courtyard house "U-plan 4×4" has no courtyard.** Its two 2-cell junction squares fill the whole 4-cell front range.
10. **Overshot race on 4.6 m trestles as the default watermill has no water source on flat maps.**
11. **`Wall_Stone_Passage` (hw 1.25, spring 1.5) cuts into the floor above.** `arch_ring()` places 0.42 m voussoirs at radius hw + 0.19, so the ring tops out at ≈3.15, inside the upper floor's belt beam (z 3.0–3.3).
12. **`Wall_Log_B` is not optional.** Without the +0.15 m course offset on the end walls, the corner logs of the two directions sit at the same heights and interpenetrate.
13. **Two water datums.** The pier uses water = 0 with the deck at +0.6; the bridge uses bank = 0.

**P3**

1. **Watermill code gets the wheel rotation wrong.**
   - It places `WaterWheel` at rot 90 with `spin_axis="local X"`, so the axle runs along world Y, parallel to the end wall.
   - `Mill_WheelPier` is at `wx + 1.0` on the X axis, so the axle must run along X.
   - Correct: rot = 0.
2. **"`Roof_TJunction` lets a 1-cell-wide wing join" is wrong.** Its zfun uses `roof_z(|x|)`, the 6 m profile, so the wing is 2 cells wide.
3. **Half-hip at 60° over 52° slopes gives jagged creases.** The creases are no longer at 45° and miss the 0.25 m grid vertices that the `roof_hip`-style triangulation relies on. Fix: use the same 52° pitch with ZC = `roof_z(1.5)` = 2.27.
4. **Stone gables with `roof_slab(k, −1.5, 1.85, s)`: the slab pokes through the parapet.** It passes the parapet face at 1.75 (party) or 1.80 (stepped) by 0.10 or 0.05 m.
5. **Roof families: "scale y by HALF/3, keep the z logic" breaks the S gable window.** For S the timber gable window reaches 1.83 m, above the 1.73 m gable top, so it pierces the roof.
6. **HW 1.9 with a 0.9 × 1.65 door does not work.**
   - The thatch roll then hangs at ≈1.2 m.
   - Sill (0.35) to wall plate (1.8) leaves only 1.45 m.
7. **`Wall_Passage` crown = spring 2.0 + hw 1.2 = 3.2, above H1 = 3.0.**
8. **Slate with `shingle_layout(nrow=10, ncol=7)` crashes.** `gen_roofs.paint()` hard-codes its pick and tint arrays as (8, 6), so a 10×7 layout indexes out of range.
9. **Manor U-plan leaves a 3 m court and misses a mirrored corner.**
   - A 5-cell hall with two 2×2 junction squares leaves a 1-cell (3 m) court.
   - The second junction needs a mirrored `Roof_LCorner`, because no rotation of the existing piece fits.
10. **Coaching inn "street range 4×2 around a 3×3 yard" is too short.** Two 2-cell wings plus a 3-cell yard need 2 + 3 + 2 = 7 cells.
11. **Turret at (−0.45, −0.45) with r 1.0 does not contain the hip eave corner.** The corner is 1.27 m from the turret centre, so the eave tip pokes out.
12. **Cross gable has no eave stop.** The neighbouring `Roof_Mid` has no end caps, so its eave (ay 3.0–4.35) is cut open at x = ±1.5.
13. **Log walls of 2.6 m break Porch, LeanTo, Stair_Ext and upper floors** (P3 noticed the porch clash itself).

**P2**

1. The proposal is truncated, so F1–F14, the wobble-envelope fix and buildings B1–B16 cannot be checked.
2. Its surviving numbers are correct:
   - chapel ridge 8.69;
   - 1.91 m hip-corner distance;
   - 2.7 m eave clash that forces an alley between gable-front houses.

## 4. Constants and conventions

```python
CELL=3.0; H1=3.0; H2=2.8; HB=4.2; HC=4.5        # existing
HW=2.4          # wattle wall top
HS=2.6          # shed wall top
LVL=1.5         # terrain step height (requested from the terrain track)
WATER_Z=-0.6; BED_Z=-1.5; PILE_Z=-3.0           # relative to the flat bank at z = 0
WALK_Z=6.2      # town-wall walk = top of the guard_tower hoarding floor
SKIRT_Z=-0.6    # hidden skirt on every new piece that touches the ground
RIDGE_M=4.19; RIDGE_S=2.27                      # ridge height above the wall top: M = 6 m deep, S = 3 m deep
```

**Conventions kept from the kit:**
- Wall modules are 3 m wide, centred on the cell edge, outer face toward −Y. The post on the left edge belongs to the module.
- Corners sit at the origin with their outer faces toward −X and −Y.
- Roofs are one piece per 3 m bay, placed at z = wall top.

**New conventions:**
- **Ridge-mounted pieces** (vents, party chimneys, bellcotes, emblems, roof banners) have their origin at the ridge apex. The builder places them at z = wall_top + RIDGE(family).
- **Contour pieces** pivot at the segment midpoint, with their face toward −Y (the low or water side).
- **Animated parts** are separate objects with the pivot on their axis. They carry `spin_axis` or `hinge_axis` and `rpm`, like `Windmill_Sails` today.
- **Lit elements** use only GLOW, so Unity can toggle "working" per instance.

## 5. M0: infrastructure (3.5 days)

### 5.1 Materials (append only)

| Index | Constant | Material | Source |
|---|---|---|---|
| 45 | WATTLE | M_VK_Wattle | T_VK_Wattle, `TILE[45]=1.0` |
| 46 | HIDE | M_VK_Hide | flat (0.50, 0.33, 0.20), rough 0.80 |
| 47 | PIGSKIN | M_VK_Pigskin | flat (0.90, 0.62, 0.56), rough 0.70 |
| 48 | COAL | M_VK_Coal | flat (0.045, 0.043, 0.050), rough 0.95 |
| 49 | NET | M_VK_Net | T_VK_Net alpha card, built like the M_VK_Foliage node tree (alpha > 0.5 gate, DITHERED, no backface culling); `TILE[49]=1.0` |

- The unpack line becomes `...,MUSH_GLOW,WATTLE,HIDE,PIGSKIN,COAL,NET=range(50)`.
- No existing indices change.

### 5.2 Variants and textures

**New `VARIANT_MATS` entries:**
- **roof:** `"Slate":("T_VK_RoofSlate",None)`, `"Shingle":("T_VK_RoofShingle",None)`
- **plaster:** `"Daub":(0.80,0.65,0.47)`, `"Sage":(0.90,1.02,0.84)`, `"Sky":(0.88,0.97,1.12)`
- **cloth:** `"Purple":(0.35,0.12,0.45)`, `"White":(0.92,0.90,0.85)`

**Texture code changes in `vk_texgen.py`:**
- `shingle_layout(S, seed, nrow=8, ncol=6, round_amt=0.27, chip_amt=0.012)`.
- `paint()` sizes its pick and tint arrays as `(nrow, ncol)` instead of the hard-coded (8, 6).

**New textures:**

| Texture | Layout | Palette | Other |
|---|---|---|---|
| T_VK_RoofSlate | nrow 10, ncol 7, round_amt 0.02, bottoms U(0.93, 0.97) | (0.26,0.29,0.34), (0.30,0.33,0.38), (0.23,0.26,0.31), (0.33,0.33,0.37) | ±0.03 purple/green tilt per slate; moss 0.15; depth 0.035 |
| T_VK_RoofShingle | nrow 9, ncol 10, round_amt 0, chip_amt 0.035 | (0.42,0.36,0.29), (0.47,0.41,0.33), (0.38,0.33,0.27), (0.52,0.49,0.44) | grain: colour × (0.9 + 0.1·fbm(ay=8)); moss 0.3; depth 0.04 |
| T_VK_Wattle (512, tile 1.0) | h = `weave(S, 16, 251, 0.3)` | colour lerp (0.36,0.26,0.16) → (0.58,0.45,0.28) by h | AO = `cavity_ao(h)`; depth 0.02 |
| T_VK_Net (512) | `lattice(S, 8)` | (0.55, 0.47, 0.34) | alpha = lead < 0.05 |

### 5.3 `finish()`: wobble, grime and sockets

```python
def finish(s, name, coll, wobble=True, grime=True, loc=(0,0,0), wobble_env="fade"):
    # "fade" (existing): y += 0.035*sin(2*pi*x/3+0.9)*sin(pi*clamp(z,0,6)/6);  x += 0.02*sin(2*pi*z/2.3+0.4)
    # "flat": y += 0.035*sin(2*pi*x/3+0.9) at every z; no x wobble
    ...
    o["sockets"] = json.dumps(s.sockets)   # set by Kit.socket(kind, pos, rot=(0,0,0), **props)
```

**Wobble rules:**
- **Upper floors use `wobble_env="flat"`.** This applies to the StoneUp and PlasterUp families.
  - The fade envelope of a ground stone or plaster wall is exactly 1 at z = 3.0.
  - So a flat-wobble upper piece meets it with no step, and flat pieces stack on each other exactly.
  - Timber upper floors don't need it: their face is 0.15 m proud of the stone and hides the step.
- **`wobble=True` only when the piece's ends at ±L/2 satisfy L/2 ≡ 1.5 (mod 3)**, which means L = 3, 9 or 15.
  - A 6 m piece has the phase sin(0.9) at its ends, while a 3 m neighbour has −sin(0.9) at its ends. That tears the seam by 5.5 cm.
  - So these get `wobble=False`: 2.121, 4.243, 4.5 and 6 m pieces, logs, and all round or radial pieces.

**Grime rule:**
- `grime=False` for any piece whose local z = 0 is not the ground: upper families, turret segments, parapets, scaffold, galleries, anything mounted on the ridge or a wall, and emblems.
- Below-ground skirts keep grime: they come out at 0.62, which reads as a damp line.

**Socket kinds:**

| Kind | Where |
|---|---|
| Door | 0.9 m outside the door, facing out |
| Work | colonist work spot |
| Stock | stockpile or goods anchor |
| Smoke | chimneys, vents, fires |
| Fire | open fires, forges, kilns |
| Light | lanterns, lit windows |
| Spin | animated rotating parts |

### 5.4 Roof code

```python
@contextmanager
def roof_family(fam):                      # "M" (existing) | "S"
    global HALF, EAVE, RIDGE, GX, OVER
    old = (HALF, EAVE, RIDGE, GX, OVER)
    HALF, OVER, gxo = {"M": (3.0, 1.35, 0.95), "S": (1.5, 0.90, 0.60)}[fam]
    EAVE = HALF + OVER; RIDGE = roof_z(0); GX = 1.5 + gxo
    try: yield
    finally: HALF, EAVE, RIDGE, GX, OVER = old
```

- **`roof_profile()`**
  - `ys = [HALF*t for t in (0,.25,.5,.75,1)] + [HALF+OVER/3, HALF+2*OVER/3, EAVE]`.
  - For M this reproduces [0, 0.75, 1.5, 2.25, 3.0, 3.45, 3.9, 4.35] exactly.
- **`gable_end(k, kind, trim=True, window=None, mirror=False)`**
  - YC = HALF + 0.02.
  - Outline ys = `[YC] + [HALF*t for t in (5/6,4/6,3/6,2/6,1/6,0)]`, which is identical for M.
  - Joist ends at `-(HALF-0.5)+i` for i < round(2·HALF). Studs at ±1.6·HALF/3.
  - `window` defaults to `HALF >= 3`.
  - XF = {timber 1.90, stone 1.80, planks 1.76, cruck 1.64, flush 1.75, stepped 1.75, logs 1.75, hoist 1.90}.
- **`roof_hip(k, mat, tabs=True, finial=True)`.**
- **Safety of the context manager:**
  - I checked that no function captures HALF, EAVE, RIDGE or GX in a default argument, so switching them is safe.
  - `roof_L_corner()` stays M-only because its ys are hard-coded.
- **`roof_field(k, zfun, xs, ys, mat, regions, free_eaves, ridge_lines)`** generalises `roof_hip` and the L corner:
  - vertices on a 0.25 m grid;
  - each quad is split along the diagonal parallel to the crease that runs through it;
  - every crease must be a ±45° line through grid vertices, which all zfuns below satisfy;
  - underside offset RT·1.25 for tile, TRT·1.2 for thatch;
  - UVs per region as in `roof_L_corner`;
  - `eave_tabs()` on free eaves; WOOD fascia on open edges.

### 5.5 Wall families and `build_block()`

| Family | Wall height | Face y | Chars | Corner / inner corner | Stage-1 piece | Wobble | Grime |
|---|---|---|---|---|---|---|---|
| Stone (exists) | 3.0 | −0.25 | `. W D S P A a X` | Corner_Stone / InnerCorner_Stone | Wall_Stone_Half(_Door) | fade | on |
| Plaster (exists) | 3.0 | −0.24 | `. W D S` | Corner_Plaster / InnerCorner_Plaster | Wall_Plaster_Frame(_Door) | fade | on |
| Wattle | 2.4 | −0.15 | `. W D B` | Corner_Wattle / InnerCorner_Wattle | Wall_Wattle_Frame | fade | on |
| Log | 3.0 | −0.255 | `. W D` (end faces use `_B`) | Corner_Log / — | Wall_Log_Half(_B) | off | on |
| Shed | 2.6 | −0.07 | `. W D B` | Corner_Shed / — | Wall_Shed_Frame | fade | on |
| Posts | 3.0 | open | `.` | Corner_Posts | itself | off | on |
| PostsBarn | 4.2 | open | `.` | Corner_PostsBarn | itself | off | on |
| Barn (exists) | 4.2 | −0.20 | `. D` | Corner_Barn | Wall_Posts_Barn | fade | on |
| Timber (exists, upper) | 2.8 | −0.40 | `. W D O` (`.` still picks V, X or K randomly) | Corner_Timber / InnerCorner_Timber | Wall_Timber_Frame | fade | off |
| StoneUp | 2.8 | −0.25 | `. W T X L D` | Corner_StoneUp / InnerCorner_StoneUp | Wall_StoneUp_Half | flat | off |
| PlasterUp | 2.8 | −0.24 | `. W O` | Corner_PlasterUp / InnerCorner_PlasterUp | Wall_Timber_Frame | flat | off |

**Character codes:**

| Char | Meaning |
|---|---|
| `.` | plain wall |
| `W` | window |
| `D` | door |
| `B` | byre or wide door |
| `S` | shop front |
| `P` | passage arch |
| `A` | existing arcade (with loggia) |
| `a` | open arcade |
| `X` | arrow slit |
| `T` | twin window |
| `L` | loading door |
| `O` | oriel (Timber) or ox-eye (PlasterUp) |
| `-` | no wall here; the neighbour owns it |

```python
def build_block(coll, origin, n, style, floors, depth=2, faces=None, ends=("gable","gable"),
                breakers=(), skip=(), stage=3, meta=None, dress=True, allow_low_eave_doors=False):
    """n cells along local X; depth 2 -> M roof, 1 -> S roof.
    floors: wall family per level, bottom first: ["Stone","Timber"], ["Wattle"], ["Stone","StoneUp","StoneUp"].
    faces: {"F":[str per level], "B":[...], "L":[...], "R":[...]}; F = -Y long side, B = +Y, L = -X end, R = +X end.
           Long sides have n chars, read left to right from outside; ends have `depth` chars. Missing -> auto.
    ends: gable|hip|halfhip|stepped|flush|hoist|planks|stone|cruck|logs|none   ("none" -> Roof_Mid_CapL/R)
    breakers: ("chimney",i) ("chimney_gable","L"|"R") ("vent",i) ("dormer",i) ("cross",i) ("cross_hoist",i)
              ("turret",corner,kind) ("gallery",side,level,cells) ("gallery_top",side,cells) ("emblem",end,kind)
              ("banner",side,i,level) ("bellcote",i) ("stair_stone",side,i)
    skip: {(side, level)} walls (and the corners on those lines) owned by a neighbour.
    returns dict(root=..., wall_top=..., parts=[...])"""
```

**Rules:**
- **Roof height:** wall_top = the sum of the family heights. Roofs go at z = wall_top. Depth 1 uses the S family (`with roof_family("S")` pieces).
- **Ends:**
  - The end at L is rotated 180°, the end at R 0°.
  - Thatch with an unsupported end kind falls back to tile Red, as `build_L_v` already does.
  - n = 1 needs gable-type ends and uses `*_Single`.
  - n = 2 with hips at both ends uses `Roof_Hip` + `Roof_Hip_Plain`.
- **Log family:** L and R faces use the `_B` pieces.
- **Wattle doors:** `D` or `B` only on an end whose kind is gable, cruck or planks, unless `allow_low_eave_doors=True`. Otherwise raise `ValueError`.
- **One breaker per bay:** at most one of {chimney, vent, dormer, cross}.
  - No dormer or cross gable in an end bay, and no dormer on thatch.
  - `chimney_gable` never on a stepped or flush end.
- **Legacy code:** `build_house_v`, `build_L_v` and the other existing builders stay untouched, which protects the regression test. `build_L_block(a, b, ...)` is the new L-plan equivalent with the same arguments as `build_block`.

### 5.6 Building root, metadata, recipe, export

- **Root Empty.** Every new `build_*` creates an Empty `BLD_<Type>_<seq>` at (ox, oy, 0) with rot z = orz. It carries:
  - `building_type`, `tier`, `district`;
  - `footprint` [w, d] in cells, `lot` [w, d];
  - `beds`, `jobs`, `storage`, `landmark`, `upgrade_to`, `stage`.
- **Parenting.** `place_v(..., parent=root, stage=S)` parents each instance with `o.matrix_parent_inverse = Mroot.inverted()`.
  - Mroot = `Translation((ox, oy, 0)) @ Rotation(orz, 4, "Z")`, computed directly.
  - Don't read `root.matrix_world` before a depsgraph update.
- **Sockets.** For each placed piece, read `src["sockets"]` and create child Empties `SOCK_<Kind>_<n>` under the root. Instances share mesh data only, so sockets can't be children of the source object.
- **Recipe.** `export_recipe(root, path)` writes:
  ```json
  {"type":"Hovel","tier":1,"footprint":[2,2],"lot":[3,3],"meta":{},
   "parts":[{"piece":"SM_VK_Wall_Wattle_Door","style":{"plaster":"Daub"},"pos":[0,0,0],"rot_z":90,
             "stages":[null,"SM_VK_Wall_Wattle_Frame","SM_VK_Wall_Wattle_Door","SM_VK_Wall_Wattle_Door"]}],
   "extras_by_stage":{"0":[],"1":[],"2":[]},
   "sockets":[{"kind":"Smoke","pos":[0,0,0],"rot":[0,0,0]}]}
  ```
- **FBX.** `export_kit_fbx()` exports each SM_VK piece from a temporary copy with unused material slots removed. Otherwise every mesh carries all 50 slots.

### 5.7 Construction stages

| Stage | Ground walls | Corners | Upper floors | Roofs and extras |
|---|---|---|---|---|
| 0 Site | Foundation_Wall | Foundation_Corner | none | no roof; BuildSite_Cell on every footprint cell; construction pile |
| 1 Walls | stage-1 piece of the family | Stone → Corner_Stone_Half; others real | none | no roof; Scaffold on level 0; pile; Prop_MortarTub (masonry) or Prop_Sawhorse (timber) |
| 2 Frame | real | real | Timber / PlasterUp → Wall_Timber_Frame; StoneUp → Wall_StoneUp_Half; others real | roof frames; chimneys real; no dormers, emblems, banners, porches, awnings, flower boxes or planters; Scaffold on every level; Prop_LadderLean |
| 3 Done | real | real | real | none |

**Roof substitution at stage 2:**

| Finished roof piece | Frame piece |
|---|---|
| Roof_Mid, Roof_CrossGable* | Roof_Mid_Frame |
| all gable kinds, Roof_HalfHip, RoofThatch_Gable* | Roof_Gable_Frame |
| Roof_Hip*, RoofThatch_Hip | Roof_Hip_Frame |
| *_Single | Roof_Single_Frame |
| Roof_LCorner (and its mirror) | Roof_LCorner_Frame (mirrored as needed) |
| Roof_T | Mid_Frame at (±1.5, 0) + Mid_Frame rot 90 at (0, 1.5) |
| Roof_X | as Roof_T, plus Mid_Frame rot 90 at (0, −1.5) |
| S roofs | RoofS_*_Frame |

- Implement as `stage_piece(piece, stage, level) -> list[(piece, dx, dy, drot)]`.
- The construction pile goes on the first free lot cell next to the door:
  - Pile_Stone_2 for Stone or StoneUp;
  - Pile_Logs_2 for Log or Wattle;
  - otherwise Pile_Planks_2.

### 5.8 District styles and the neighbour rule

`district_style(seed, district, prev=None)`. The legacy `random_style(seed)` stays unchanged.

| District | Ground | Upper | Storeys | Roof | End kinds | Plaster | Cloth |
|---|---|---|---|---|---|---|---|
| fringe | Wattle .5, Log .3, Stone .2 | — | 1 (.85), 2 (.15) | Thatch .75, Shingle .25 | cruck .45, hip .35, planks .2 | Daub .6, Cream .4 | Green, Red |
| craft | Stone .7, Plaster .3 | Timber .8, PlasterUp .2 | 1 (.3), 2 (.7) | Red .35, Green .2, Shingle .2, Slate .15, Thatch .1 | gable .5, hip .2, halfhip .2, hoist .1 | Cream, White, Ochre, Rose | Red, Yellow |
| market | Stone .55, Plaster .45 | PlasterUp .45, Timber .55 | 2 (.25), 3 (.5), 4 (.25) | Red .45, Slate .3, Green .15, Shingle .1 | flush .35, stepped .25, hoist .2, gable .2 | all 7 | all 6 |
| waterfront | Stone .5, Shed .5 | Timber | 1–3 | Slate .4, Shingle .3, Red .3 | hoist .4, gable .4, hip .2 | White, Sky, Cream | Blue, White |
| noble | Stone | StoneUp .7, PlasterUp .3 | 2 (.3), 3 (.5), 4 (.2) | Slate .5, Blue .35, Red .15 | stepped .5, halfhip .2, hip .3 | White .5, Cream .3, Sky .2 | Purple, Blue |

- Blue is used only by civic and faith buildings and the noble district.
- **Neighbour rule:** a new house must differ from each adjacent house (same street side, ≤ 6 m apart) in at least 2 of:
  - storeys;
  - roof material;
  - end kind;
  - orientation (eave or gable to the street);
  - depth family.

  Reroll up to 8 times, then accept.

## 6. Piece catalogue

**Flag abbreviations** used in the "Flags" columns:

| Code | Meaning |
|---|---|
| std | fade wobble, grime on |
| ng | wobble off, grime on |
| nw | wobble off, grime off |
| fw | flat wobble, grime off |

All pieces are named `SM_VK_<name>`.

### M1: construction and stock (3 days)

| Piece | Geometry | Materials | Flags / sockets |
|---|---|---|---|
| BuildSite_Cell | SOIL quad 2.9×2.9 at z 0.01; border of 4 boxes 2.9×0.12×0.05; 6 seeded pegs 0.04×0.04×0.25 | SOIL, WOOD | ng |
| Foundation_Wall | trench SOIL 3.0×0.8×0.02 at (0, −0.05, 0.01); `stone_panel(-1.5,1.5,0,0.45)`; `plinth()`; stakes 0.05×0.05×0.7 at (−1.5, ±0.9); string 0.01² along x at y −0.9, z 0.55 | STONE, SOIL, WOOD, IRON | ng |
| Foundation_Corner | `rock()` 1.0×1.0×0.45 at (−0.05, −0.05, 0.2); stake at (−0.9, −0.9) | STONE, WOOD | ng |
| Wall_Stone_Half / _Half_Door | `stone_panel` to z 1.2, then six 0.5 m columns up to a seeded top in U(1.2, 1.9); `plinth()`, `batter()`; 3 loose ASHLAR blocks 0.5×0.3×0.3 on top. `_Door` leaves an opening x ±0.68 up to 1.9 with jamb stones | STONE, ASHLAR | std |
| Corner_Stone_Half | quoin loop of `corner_stone` stopped at z 1.6 | STONE | ng |
| Wall_Plaster_Frame / _Door | `plaster_ground` without its PLASTER boxes: plinth, beams, posts, braces | STONE, WOOD | std |
| Wall_Timber_Frame | `timber_frame("V")` without the infill; add 2 knee braces | WOOD | fade, grime off |
| Roof_Mid_Frame | per side: rafters 0.12×0.18 at x ∈ {−1.2, −0.6, 0, 0.6, 1.2}, 2 boxes each (pitch 0→HALF, kick HALF→EAVE−0.2); ridge beam 3.0×0.22×0.30 at RIDGE−0.45; purlins 0.14×0.18 at ay HALF/3 and 2·HALF/3; 5 battens 0.05×0.08 at ay 0.4, 1.0, 1.6, 2.2, 2.8 (scaled by HALF/3) | WOOD | nw |
| Roof_Gable_Frame / Roof_Single_Frame / Roof_Hip_Frame / Roof_LCorner_Frame | Mid_Frame extended to x 2.2 (Single ±2.2) plus the timber members of `gable_end` without infill or window. Hip: common rafters for local x ≤ 0, 2 hip rafters on the diagonals, jack rafters every 0.6. LCorner: both wings, valley rafters on y = ±x (y > 0), both ridge beams | WOOD | nw |
| Scaffold_Wall | standards r 0.07 at (−1.5, −1.35) and (−1.5, −0.55), z 0–3.0; ledgers r 0.05 at z 1.4 and 2.6; putlogs 0.08×1.1×0.08 at x −1.5 and 0, z 2.6; deck of 2 PLANKS 3.0×0.28×0.04 at z 2.66, y −0.95 and −1.25 (clear of opened shutters, which reach y −0.82 below z 2.25); 1 brace; 6 lashings. Stacks per storey | BARK_BIRCH, PLANKS, BURLAP | nw |
| Scaffold_Corner / Scaffold_Ladder | standard at (−1.35, −1.35) + ledgers along −X and −Y. Ladder: rails 0.06×0.04, 0.45 wide, from (0, −2.1, 0) to (0, −1.4, 3.0), rungs every 0.3 | same | nw |
| Prop_Wheelbarrow / Prop_MortarTub / Prop_LadderLean / Prop_ShearLegs | barrow: tray 1.0×0.6×0.3, wheel r 0.2. Tub: PLANKS 0.9×0.6×0.3 + CLAY fill. Ladder: 3.2 m. Shear legs: 5 m tripod + rope + ASHLAR 0.8×0.6×0.5 | | ng |
| Pile_Logs_1/2/3 | 3 / 7 (4+3) / 10 (4+3+2+1) logs, 2.8 m long, r U(0.15, 0.20), BARK_OAK with ENDGRAIN discs; 2 chock stakes | | ng; SOCK_Stock |
| Pile_Planks_1/2/3 | 2 stacks 2.8×0.85, 4 / 9 / 14 layers of 3 boards 0.25×0.05, stickers every 3 layers (height ≤ 0.86) | PLANKS | ng |
| Pile_Stone_1/2/3 | ASHLAR blocks 0.6×0.4×0.35 on 2 pallets 1.3×1.0×0.12; 6 / 14 / 24 blocks; ±3° jitter | | ng |
| Pile_Sacks_1/2/3 | 4 / 9 / 16 `prop_sacks` units on a pallet | | ng |
| Stockpile_Border | 4 boards 2.9×0.1×0.12 inset 0.05, 4 pegs | PLANKS | ng |

Every pile fits inside 2.9 × 2.9 × 1.6.

### M2: skyline pack (3.5 days)

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Roof_Single, RoofThatch_Single | slabs (thatch: `thatch_slab`) from −GX to GX with end caps at both ends; eave tabs or rolls; ridge or thatch cap from −GX−0.1 to GX+0.1; `gable_end` at +X and a copy mirrored with `Matrix.Scale(-1,4,(1,0,0))` plus `bmesh.ops.reverse_faces`; thatch rake rolls at ±GX | nw |
| Roof_Hip_Plain | `roof_hip(finial=False)` | nw |
| Chimney_Gable_H24 / H30 / H58 / H86 | end-wall-local (outer −Y), one per wall top 2.4 / 3.0 / 5.8 / 8.6. Base 1.6 (x) × 1.0 (y −0.25..−1.25), z 0–2.2. Weathering from 1.6 to 1.0 wide over z 2.2–2.5. Flue 1.0 × 0.8 (y −0.25..−1.05) up to Ztop−0.2, where **Ztop = wall_top + 4.19 + 1.0 = 7.59 / 8.19 / 10.99 / 13.79**. Cap `rock` 1.2×1.0×0.2; 2 CLAY pots as in `chimney()`. The flue pierces the verge, which is intended | ng; SOCK_Smoke at (0, −0.65, Ztop+0.5) |
| Chimney_Party | origin at the ridge apex; stack 1.8 × 1.0 from −1.2 to +1.3; cap 2.0×1.2×0.2; 3 pots | nw; 3 × Smoke |
| Roof_Vent | origin at the ridge apex, placed at RIDGE−0.15. Body 1.2×0.8×0.6 WOOD; 4 slats 1.1×0.04×0.14 per long side at 30°; 2 ROOF cap slabs 1.45×0.6×0.06 at 40°, meeting at z 0.95 | nw; Smoke at (0, 0, 1.0) |
| RoofThatch_Vent | THATCH half-ico r 0.55 scaled (1.4, 1, 0.7) with a VOID slot 0.6×0.25 on each side | nw; Smoke |
| Roof_Gable_Flush | slabs from −1.5 to 1.6 with an end cap at 1.6; eave tabs; ridge. STONE parapet x 1.25–1.75, top `roof_z(ay)+0.30` for ay 0–3.0, then down the kick to the kneeler; ASHLAR coping 0.62×0.12 along the rakes; ASHLAR kneeler 0.70 × 0.80 (ay 3.0–3.8) × 0.55; triangle `gable_end("flush")` in STONE, no bargeboards or finial | nw |
| Roof_Firewall | origin on the unit boundary: the Flush parapet, coping and kneelers only (x −0.25..0.25, ay −3.8..3.8); no slabs or triangle | nw |
| Roof_Gable_Stepped | Flush, but the parapet is 6 steps: step k (0..5) covers ay ∈ [3.0−0.5(k+1), 3.0−0.5k], top `roof_z(3.0-0.5*(k+1))+0.30`; ASHLAR cap 0.62×0.56×0.10 per step. Pinnacle 0.5×0.5×0.9 on step 5 (top 4.49), a 4-segment cap 0.6 × 0.4, and a BRONZE ico r 0.12. Ox-eye: WINDOW disc r 0.30 at z 0.45·top, with an ASHLAR `ring(0.30, 0.46, 0.2)` | nw |
| Roof_Gable_Hoist | Roof_Gable with the gable window replaced by a VOID door 1.0×1.5 at z 0.5–2.0, a WOOD frame and one PLANKS leaf open 100°. Hood: 2 ROOF slabs 0.85×1.4 at 40°, eave at z 2.25, apex 2.80, running out to XF+1.3. Beam 1.6×0.2×0.2 at z 2.45 (XF−0.2 to XF+1.4); pulley `ring(0.08, 0.18, 0.06)` at XF+1.25; rope down to z −1.6; BURLAP sack 0.5×0.4×0.6 | nw |
| Emblem_Ridge_<kind> (13) | origin at the gable finial top, placed at (end x ± (0.95+0.08), 0, wall_top+RIDGE+0.9). IRON spike 0.06×0.06×1.4; emblem ≤ 1.2×1.2, 0.12 thick, centred at +1.3. Kinds: anvil, pretzel (24-segment tube r 0.07, BREAD), tankard, fish (STEEL), key (BRONZE), sheaf (20 boxes, HAY), horseshoe, scissors, mortar, saw, axe, shield (CLOTH_A with a PAPER cross), book | nw |
| Banner_Wall | wall-local, origin at the storey top. IRON pole r 0.03, 1.2 m along −y, with a stay. Cloth hangs in the YZ plane: 0.9 wide × 2.2 long, 6 strips, x-wave ±0.04, swallowtail notch 0.3, double-sided CLOTH_A; optional PAPER disc 0.5 appliqué | nw |
| Banner_Pole / Banner_Roof | 6 m pole r 0.06 on a stone base 0.5×0.5×0.4 with a 1.6×1.0 flag (6×4 wave grid). Roof version: 3 m pole at the ridge apex + 1.8 m pennant | nw |
| Prop_Bunting_6 / _9 | catenary with sag 0.5 / 0.8; 0.30 × 0.35 triangles every 0.35 cycling CLOTH_A, CLOTH_B, YELLOW, LEAF | nw |
| Sign_<kind> | `shop_sign(k, emblem)` extended with the new emblems, scaled 0.45 | nw |

### M3: humble walls, S roofs, camp and early props (5.5 days)

**Wattle (HW 2.4)**

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Wall_Wattle | `plinth()` rubble, z 0–0.35. Sole plate 3.0×0.26×0.20 at z 0.45. PLASTER daub panel x ±1.5, z 0.55–2.2, y ±0.12, cut with `grid_cut`; outer vertices jittered ±0.015 except at x = ±1.5. Left post 0.24 (x) × 0.30 (y) × 1.85 at x −1.5; stud 0.16×0.20 at x 0. Wall plate 3.0×0.30×0.20 at z 2.3 in 3 boxes sagging 0.04 at x 0. 1–2 seeded bare patches: a WATTLE 7-gon about 0.6×0.45 at y −0.125 with a 0.03 PLASTER lip | std |
| Wall_Wattle_Window | opening x ±0.35, z 1.10–1.65; VOID at y +0.06; log lintel `_cyl` r 0.09 × 1.1 at z 1.74; top-hinged PLANKS shutter 0.8×0.65 open 55°, prop stick 0.03×0.9 | std |
| Wall_Wattle_Door | opening x ±0.45, z 0.35–2.15; 4-board leaf ajar 25°; threshold 1.1×0.5×0.12 | std; Door |
| Wall_Wattle_Byre | opening x ±1.0, z 0.35–2.10; lower leaf closed, upper leaf open 90°; HAY spill | std; Door |
| Wall_Wattle_Frame | stage 1: plinth, plates and posts; WATTLE panel (quads on both sides) up to z 1.3 | std |
| Corner_Wattle / InnerCorner_Wattle | post 0.28×0.28×2.4 at (−0.1, −0.1) on a rock 0.6×0.6×0.4. Inner corner: post 0.24² at (0.1, 0.1) | ng |
| RoofThatch_Gable_Cruck | thatch gable (slab, rolls, cap, rake roll) + `gable_end("cruck", trim=False)`. Daub triangle (PLASTER) with one WATTLE patch. Per side, a quadratic Bézier in (y, z) from P0 (±2.7, −2.4) via P1 (±2.9, 0.6) to P2 (0, under(0)−0.15), built from 7 WOOD boxes 0.24 × 0.30 at x = 1.64. Midpoint (2.125, 0.475) stays under the roof. Collar 0.18×0.20 at z 1.6; tie beam at z 0; VOID smoke vent 0.5×0.35 at under(0)−0.6 | nw (the blades reach the ground) |

**Log (3.0 m)**

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Wall_Log | 9 logs, `_cyl` r 0.165 ± 0.015 (seeded by course i, same seeds as the corners), 10 segments, x ±1.5, centres z = 0.47 + 0.30·i, y −0.09. PLASTER chinking 3.0×0.07×0.07 at y −0.20. STONE plinth 3.0×0.6×0.33 + rocks | ng |
| Wall_Log_Window | courses cut at x ±0.55 with ENDGRAIN discs; `window_frame(-0.5, 0.5, 1.1, 2.0, face=-0.25)` with shutters | ng |
| Wall_Log_Door | opening x ±0.6, z 0.33–2.4; lintel log r 0.2 × 1.8 at z 2.55; 5-board door with Z battens, ajar 20° | ng; Door |
| Wall_Log_B, _B_Window, _B_Door | same with courses at z = 0.62 + 0.30·i and the plinth raised to 0.46; used on the L/R faces | ng |
| Wall_Log_Half, Wall_Log_B_Half | first 5 courses (stage 1) | ng |
| Corner_Log | per course: X log from x −0.5 to 0 at (y −0.09, z_i), Y log from y −0.5 to 0 at (x −0.09, z_i + 0.15); ENDGRAIN discs at the −0.5 ends; foot rock 0.9×0.9×0.4 | ng |
| Roof_Gable_Logs | Roof_Gable slabs + `gable_end("logs")`: logs r 0.16 at z = 0.16 + 0.30·i up to under(0)−0.2, cut to the rake, ENDGRAIN caps, window 0.5×0.5 at z 1.2. Use with the Shingle roof style | nw |

**Shed (2.6 m) and open bays**

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Wall_Shed | 3 sill stones 0.4×0.4×0.25 at x −1.2, 0, 1.2; sill beam 3.0×0.22×0.20 at z 0.3; PLANKS boards z 0.4–2.6, y −0.02..0.06, cut every 0.3 in x only; battens 0.06×0.04 every 0.3 at y −0.05; post 0.2² at x −1.5; top plate at z 2.5; 1 brace | std |
| Wall_Shed_Door / _Wide / _Window / _Frame | door 1.1×2.0 with Z brace, ajar 30°. Wide: 1.8×2.1, two leaves, one open 100°. Window: 0.6×0.5 at z 1.5–2.0, VOID, flap propped 45°. Frame: no boards | std; Door |
| Corner_Shed | post 0.22² at (−0.12, −0.12) on a rock | ng |
| Wall_Posts (3.0) / Wall_Posts_Barn (4.2) | post 0.28² at x −1.5 on a stone pad 0.5×0.5×0.2; beam 3.0×0.3×0.3 at z H−0.15; 2 knee braces 0.14² × 0.7 at 45° | ng |
| Corner_Posts / Corner_Posts_Barn | post 0.30² at (−0.15, −0.15) + pad; braces along +X and +Y | ng |
| Ceiling_Cell | PLANKS 3.0×3.0×0.06 at z H−0.36; 3 joists 0.2×3.0×0.25 at x −1, 0, 1 | nw |

**S roof family** (built inside `with roof_family("S")`):
- Pieces: `RoofS_Mid`, `RoofS_Gable`, `RoofS_Gable_Planks`, `RoofS_Hip`, `RoofS_Single`, `RoofThatchS_Mid / _Gable / _Hip / _Single`, and `RoofS_{Mid,Gable,Hip,Single}_Frame`.
- Geometry: ridge 2.27, eave overhang 0.9 (tip −0.09), verge GX 2.1.
- Gable window off; 3 joist ends. All nw.

**Camp and early props (ng)**

| Piece | Geometry |
|---|---|
| Tent_A | 2.4 × 3.0 × 2.1; ridge pole r 0.05 on 2 uprights; 2 CLOTH_B slabs 2.42 long with 3 sag rows (middle −0.06); back triangle; front flaps tied open 30° over a VOID triangle; 4 guy ropes and pegs |
| Tent_Bell | lathe [(1.8, 0), (1.8, 0.5), (0.08, 2.8)], 16 segments, CLOTH_B; centre pole; door flap |
| Prop_Campfire | 9 rocks on a ring of r 0.58; 5-log teepee; GLOW ico r 0.18; tripod + IRON pot. Sockets: Smoke, Fire, Light |
| Prop_Bedroll | CLOTH_B roll r 0.12 × 0.7 + mat 0.7×1.6 |
| Prop_Wagon_Covered | bed 3.2×1.4×0.35 at z 0.8; 4 wheels r 0.45; 5 hoop tubes r 0.8; CLOTH_B half-cylinder cover r 0.82 × 3.4 |
| Prop_ChoppingBlock | stump lathe r 0.3 × 0.5 (BARK_OAK, ENDGRAIN top) + axe (WOOD 0.7 handle, STEEL head) |
| Prop_Sawhorse | 2 X-legs + 1.2 m beam |
| Prop_SawPit | 3.2×0.9 PLANKS-lined pit with a VOID floor at −1.2; log on 2 trestles; two-man saw; PAPER sawdust icos. Sockets: 2 × Work |
| Crop_Saplings | `soil_bed` + 12 saplings from the vk_nature generator at scale 0.5, merged |
| Prop_StaddleStone | lathe [(0.18, 0), (0.14, 0.45), (0.35, 0.5), (0.35, 0.62), (0, 0.64)], ROCK |
| Prop_GranaryStep | 3 detached stone steps ending 0.3 short of the door |
| Prop_Privy | 1.2×1.2×2.2 plank booth, pent roof at 12°, VOID crescent in the door |
| Prop_WaysideShrine | pillar 0.6×0.6×1.8 on 2 steps; gabled niche of 2 ROOF slabs 0.9×0.5; PAPER lathe statue; GLOW candles; flowers |
| Prop_HayRack | hay rack |
| Livestock (each mesh faces +X, origin at the feet) | Sheep: ico r 0.42 scaled (1.35, .85, .85) at z 0.62, CLOTH_B, jitter 0.04; VOID head 0.2×0.18×0.24; legs 0.07² × 0.42. Pig: ico r 0.4 scaled (1.5, .9, .85), PIGSKIN; snout cylinder; spiral tail. Cow: body 1.6×0.6×0.7 at z 1.0 with bevel 0.2, HIDE with PAPER patches; horns; PIGSKIN udder. Goat: sheep × 0.8 in HIDE with horns. Horse_Draft: body 1.7×0.5×0.65 at z 1.25, neck at 45° |

### M4: town tier (6 days)

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Wall_StoneUp | `stone_panel(-1.5,1.5,0,2.8)`; ASHLAR belt centred at (0, −0.33, 0.10), size (3.0, 0.20, 0.20); `wall_rocks(n=4, z 0.4–2.6)` | fw |
| Wall_StoneUp_Window | opening x ±0.45, z 0.75–1.95; ASHLAR jambs 0.18; lintel `rock` 1.3×0.22×0.3; `window_frame` with shutters | fw |
| Wall_StoneUp_Twin | lights x −0.62..−0.12 and 0.12..0.62, z 0.75–1.80, with semicircular heads r 0.25 (WINDOW fans); colonnette lathe r 0.07; ASHLAR surround 0.15 | fw |
| Wall_StoneUp_Slit | VOID 0.14×1.0 at z 0.9–1.9 in an ASHLAR surround 0.5×1.3 (the `guard_tower` slit) | fw |
| Wall_StoneUp_Loading | opening x ±0.65, z 0–2.1; 2 PLANKS leaves open 100° with IRON straps; lintel 1.7×0.3×0.25; sill beam 1.6×0.4×0.15 | fw; Stock |
| Wall_StoneUp_Door / _Half | door opening x ±0.55, z 0–2.2 (Door socket). Half: ragged top U(1.0, 1.8) | fw |
| Corner_StoneUp / InnerCorner_StoneUp | core 0.8×0.8×2.8; alternating quoins 1.05×0.62 / 0.62×1.05, 0.44 high (the `corner_stone` loop at H2) | nw |
| Wall_PlasterUp / _Window / _Oxeye | plaster box y −0.24..0.20, z 0–2.8, `grid_cut`; WOOD band 3.0×0.20×0.15 at z 0.08, y −0.30. Window 0.9×1.2 at z 0.8–2.0 with shutters. Ox-eye: WINDOW disc r 0.35 at z 1.6 with an ASHLAR ring | fw |
| Corner_PlasterUp / InnerCorner_PlasterUp | WOOD post 0.34² × 2.8, as the upper part of `corner_plaster` | nw |
| Wall_Stone_Shop / Wall_Plaster_Shop | opening x ±1.1, z 0.85–2.35 (the plaster version has posts at ±1.25); WOOD lintel 2.6×0.3×0.25; counter PLANKS 2.2×0.6×0.07 at z 0.85 on 2 WOOD brackets at 45°; canopy PLANKS 2.3×0.75×0.06 hinged at 2.35, raised 50°, 2 IRON rods; VOID at y +0.10; shelf 2.2×0.3 at z 1.55 | std; Stock at (0, −0.55, 0.92)

 |
| Prop_ShopGoods_{Bread, Produce, Cloth, Pots, Tools, Meat, Candles, Fish, Boots, Bottles} | each fits within 2.0×0.5×0.45 on the counter. Bread and Produce reuse the `market_stall` goods code. Cloth: 3 CLOTH_A bolts r 0.09 × 0.5, so the style recolours them. Pots: CLAY lathes. Meat: APPLE / PIGSKIN hams. Candles: PAPER + GLOW. Fish: STEEL. Bottles: STAINED | ng |
| Roof_Pent | origin at the wall face (0, −0.3, 0). ROOF slab 3.2 × 1.5 (out) × 0.08, sloping down at 22° (outer edge at −0.6); WOOD fascia; 2 three-box curved brackets at x ±1.2, running from (−0.3, −0.9) to (−1.2, −0.4) | nw |
| Wall_Stone_Passage (+ `_Gated`) | arch hw **1.2**, spring **1.4**, crown **2.6** (ring top 3.0), using `arch_cut_panels`, `arch_ring(n=9)` and `arch_soffit`; plinth split; cobble strip. `_Gated`: 2 PLANKS leaves 1.2×2.5 open 100° | std; Door ±0.9 |
| Passage_Vault | placed at house-local y 0 between the front and back passage walls. `arch_soffit(1.2, 1.4, y −2.75..2.75, STONE)`; PLASTER side walls x ±1.2..±1.45, z 0–1.4; cobble floor 2.4×5.5 | ng |
| Wall_Arcade_Open | `wall_arcade()` without the loggia floor, ceiling, back facade and lantern | ng |
| Gallery_Timber / Gallery_End | PLANKS deck 3.0×1.3×0.08 with its top at H1, y −0.30..−1.60; joists every 0.75; post 0.22² at (−1.5, −1.5) from z 0 to 4.05; knee braces; handrail at H1+1.0, bottom rail at H1+0.12, balusters r 0.03 every 0.2. `_End` adds the post at +1.5 and a side rail | nw |
| Gallery_Top | top storey only. Deck 3.0×1.0×0.1 at the storey base, y −0.45..−1.45; 2 brackets 0.9 at 45°; post 0.18² at (−1.45, −1.35), 2.1 high (its top is 0.70 below the wall top; the eave underside at ay 4.35 is −0.64); rails at 1.0 and 0.15; balusters 0.06 every 0.2 | nw |
| Turret_Corbel / Turret_Seg / Turret_Seg_Stone / Turret_Cap | axis at corner-local (**−0.6, −0.6**), **r 1.1**, 12 sides. Corbel: lathe [(0.2, −1.2), (0.45, −0.9), (0.7, −0.6), (0.9, −0.3), (1.1, 0)] with ASHLAR rings; its top sits at the first upper floor. Seg: H2 tall, PLASTER with 6 WOOD posts, sill and head rings, 3 WINDOW 0.5×1.0 facing −X/−Y. Seg_Stone: STONE with 1 slit. Cap: cone r 1.35 × h 2.8, bell-cast skirt of 0.3 at KICK, ROOF UVs as in `guard_tower`, WOOD finial 0.6 + BRONZE ball. **Stack:** one Seg per upper storey plus one above the wall top. On a 3-storey house the cap base is at 11.4 and the tip at 14.2 | nw |
| Corner_Party_Stone / Corner_Party_Timber | pilaster 0.30 (x) × 0.12 proud of the face (stone face −0.25, timber −0.40) × H1 or H2 | ng / nw |
| Roof_Mid_CapL / Roof_Mid_CapR | Roof_Mid with `end_caps=(True,False)` / `(False,True)` | nw |
| Roof_LCorner_Mirror | Roof_LCorner mirrored in X, with `reverse_faces` | nw |
| Roof_T | `roof_field`, x −3..3, y −EAVE..3. zfun = `roof_z(|y|)` for y ≤ 0, else `max(roof_z(|y|), roof_z(|x|))`. Eave tabs on −Y; ridge A from −3 to 3 and ridge B from 0 to 3. Neighbours: Roof_Mid at x = ±4.5 and Roof_Mid rot 90 at y = 4.5 | nw |
| Roof_X | `roof_field` on [−3, 3]²; zfun = `max(roof_z(|y|), roof_z(|x|))`; 4 valleys; ridges along both axes; Mid pieces on all 4 sides | nw |
| Roof_CrossGable / Roof_CrossGable_Hoist | replaces a Roof_Mid bay: x ±1.5, y −3.6..4.35. zfun = `roof_z(|y|)`, except for y ≤ −1.5, where it is `max(roof_z(|y|), 0.35+(1.5-|x|)*tan52)`. Cross ridge at 2.27; valleys from (±1.5, −3) to (0, −1.5). Timber triangle face at y −3.40 with a window 0.8×0.8 at z 0.55–1.35 (Hoist version: door 0.8×1.2 + beam + pulley + rope). **Eave stops:** WOOD 0.06 boards at x = ±1.5 following the neighbour eave, ay 3.0–4.35, from `roof_z(ay)+0.02` down to `roof_z(ay)-0.36` | nw |
| Roof_HalfHip / RoofThatch_HalfHip | drop-in for Roof_Gable (x −1.5..GX 2.45). zfun = `min(roof_z(|y|), roof_z(max(0, x)))`. The hip starts at 2.27 on the wall line, reaches the ridge at local x 0, and the creases are \|y\| = x. Gable wall = `gable_end` outline clipped by the hip underside (a trapezoid). Hip eave tabs (tile) or eave roll (thatch); rake rolls on the lower verges | nw |
| Roof_Mid_Hatch / Roof_Mid_Skylight | Roof_Mid plus a 1.0×1.0 WOOD frame centred at ay 1.7 on −Y. Hatch: PLANKS lid open 65° over VOID. Skylight: WINDOW 0.9² set 0.02 proud | nw |
| Roof_Bellcote | origin at the ridge apex. ASHLAR 0.9 (x) × 0.5 × 1.6; VOID arch hw 0.25, spring 0.8; `bell(k, 1.25, 0.22)`; 2 ROOF slabs 0.7×0.4 at 45° | nw |
| Stair_Stone_Ext | same run as `ext_stair`: 13 steps, rise 3.3, run 2.7, climbing +X to a landing at x 1.35–2.85, z 3.3. Solid ASHLAR wedge y −0.3..−1.4; VOID arch under the upper half (hw 0.6); parapet 0.3 × 0.7. About 50°, so Unity needs a NavMeshLink | ng; Door at the landing |
| Stoop_Stone | 3 ASHLAR steps 1.8 wide, rise 0.18, tread 0.35 (top 0.54); cheeks 0.3×1.05×0.6 | ng |
| Prop_CellarHatch / _Open | curb 1.5×1.3; slope from z 0.55 at y −0.3 to 0.10 at y −1.6 (25°); 2 PLANKS leaves 0.72×1.25 with IRON straps. `_Open`: one leaf rotated 160°, VOID well, 3 steps | ng |

Optional in M4, coordinated with the stone-texture track: `SLOT["stone"]=STONE` with tints Warm (1.06, 0.98, 0.88), Grey (0.92, 0.95, 1.00) and Dark (0.75, 0.75, 0.78).

### M5: water (4 days)

All heights use the water datum (bank 0, water −0.6).

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Pier_Deck | 3×3, centred on the cell. Deck top +0.05. 13 planks 0.22 × 3.0 × 0.07 along X, 1 cm gaps, ±1 cm z jitter, one plank 0.4 short. Stringers 0.2×0.3 at y ±1.2. Cap beam along Y at x −1.5. Piles r 0.16 at (−1.5, ±1.35) from −3.0 to +0.35, lean ≤ 5°. X-brace at z −1.8..−0.35 | ng |
| Pier_End / Pier_Stairs / Pier_Rail | End: piles at (+1.5, ±1.35) + cap; 2 bollards (lathe r 0.18 × 0.5); ladder to −1.4; lantern pole (Light). Stairs: 1.5 wide, 4 steps from +0.05 to −0.55. Rail: posts 0.12² every 1.5, 1.0 high, rope sag 0.12 | ng |
| Prop_Rowboat / Prop_Barge | Rowboat 4.2×1.35×0.55: hull lofted from 7 U-sections of 5 vertices (bmesh bridge), sheer +0.15, PLANKS with UVs along the length; gunwale strip in the **SHUTTER** slot; 2 thwarts; 2 oars 0.06×2.4. Barge 7.5×2.6×0.8: square raked ends, 5.5 m mast, yard, furled CLOTH_B sail, crates, barrels, steering oar. Origin at the waterline | nw |
| Bridge_Wood_Mid / _End / _Bent | Mid: deck top +0.35, 12 planks 3.4 × 0.25 × 0.07 across; 5 stringers 0.2×0.3; posts 0.14² at x −1.5 and 0, y ±1.6, 1.05 high; top and mid rails. End: deck rises from +0.05 (bank) to +0.35; rock abutment 3.4 wide at x −1.5..−0.3; rails flare out 0.3. Bent: 3 piles r 0.14 at y −1.3, 0, 1.3 from −3.0 to 0.0; cap 3.6×0.3×0.3; X-brace. Placed at every seam between two bridge modules | ng |
| Bridge_Stone_Span (6 m) / _Ramp (3 m) / _Pier | Span: 4.5 m clear + 0.75 half-piers. Segmental intrados springing at −0.6, apex +0.8 (R 2.51). ASHLAR voussoirs 0.45 deep. Deck +1.2 at the ends, +1.3 in the middle; 3.2 between parapets 0.35 × 0.8 with coping 0.45×0.12. Ramp: deck from +1.2 down to 0.0 (21.8°); newel 0.6×0.6×1.1; wing walls 1.5 m splayed 30°. Pier: pointed cutwater 1.5 × 3.9 with 1.2 m noses, z −2.0..−0.6, at seams between spans | nw (6 m) |
| Bridge_Log | squared log r 0.3 × 4.5 + one pole handrail; pairs with `Rock_StepStones` | ng |
| Quay_Straight (3.0) / Quay_Diag (2.121) / Quay_Post / Quay_Stair | Face −Y toward the water. ASHLAR coping 0.5 × 0.25 at z −0.25..0. STONE face 0.9 thick from 0 down to **−2.0**. ROCK_MOSSY strip from −0.6 to −2.0. IRON ring `ring(0.1, 0.16)` at (0, −0.52, −0.4). Post: ASHLAR 0.6×0.6×0.9. Stair: 4 steps of 0.15 cut to −0.6, 1.2 wide | Straight ng; Diag, Post nw |
| WaterWheel (animated) | R 2.4, width 1.0; **axle along local X**. Rims `ring(2.15, 2.4, 0.12, axis X)` at x ±0.45; 8 spokes per side 0.12², r 0.3–2.2; 16 PLANKS paddles 1.0 × 0.5 × 0.08 at r 2.1–2.6; hub r 0.35 × 1.1; axle r 0.15 from x −1.1 to +1.2. Origin at the hub; `spin_axis="local X"`, `rpm=6` | nw; Spin |
| Wall_Stone_Axle / Mill_WheelPier / Prop_Millstone | Axle wall: Wall_Stone + ASHLAR bearing 0.6×0.3×0.6 at z 1.3 + VOID disc r 0.2. Pier: STONE 0.8×1.0, z −1.5..+1.5, ASHLAR bearing at 1.3. Millstone: lathe r 0.65 × 0.3 with an eye ring | std / ng |
| Prop_NetRack / Prop_FishRack / Prop_Creels / Pile_Fish_1–3 | Net rack: 2 posts 2.4 + NET card 3.0×1.8 with BREAD floats. Fish rack: A-frame 3 m, 2 rows of STEEL flattened icos. Creels: HAY lathe baskets. Pile_Fish: crates of STEEL fish | ng |
| Prop_LavoirBasin / Prop_WallFountain / Prop_HandPump | Basin: ASHLAR curb 5.4×2.0×0.45, WATER at 0.3, 4 slabs tilted 20° (4 × Work). Wall fountain: back slab 1.2×0.25×1.8, BRONZE spout, half-lathe basin r 0.8, WATER stream card. Hand pump: 1.4 m WOOD/IRON pump + trough | ng |

### M6: production props (5 days, all ng unless noted)

| Group | Pieces and key numbers |
|---|---|
| Quarry | `Quarry_Face_Straight` (3.0) / `_Diag` (2.121, nw) / `_Corner`: 3.0 high = 2 LVL; 2 benches, each 1.5 high × 0.8 deep; ROCK blocks with jitter 0.02 and flat cuts; VOID drill lines 0.02×0.6; 6 rubble rocks at the foot. `Quarry_Floor`: 3×3 ROCK slab, a split block, 3 IRON wedges. `Prop_QuarrySled`, `Prop_Banker` (ASHLAR 1.2×0.6×0.8 + half-carved lathe drum) |
| Crane | `Prop_TreadwheelCrane`: A-frame 5.5, jib 7.0 at 40°, hook + ASHLAR 0.8×0.6×0.5. Wheel is a separate object: 2 × `ring(1.6, 1.8)` 1.2 apart + 16 treads; `spin_axis="local Y"`. Landmark at 9 m |
| Clay | `Prop_BottleKiln`: lathe [(2.2,0),(2.3,1.5),(2.0,3.5),(1.1,5.0),(0.8,6.0)], 16 segments, CLAY, GLOW stoke hole (Smoke, Fire). `Prop_ClayPit`: CLAY quad 3×3 at z 0.01 + WATER puddle + spade. `Prop_PottersWheel`. `Pile_Bricks_1–3` (CLAY 0.25×0.12×0.07 stacks) |
| Mine | `Mine_Portal`: posts 0.35 × 3.0, cap 3.6; 3 timber sets 0.8 apart into a VOID tunnel 2.5 × 2.6 × 3.0; plank lagging; lantern; 5-boulder mound (`boulder()`), so it also works on flat ground. `Rail_Straight` (3.0), `Rail_Curve` (r 3, 90°), `Rail_Diag` (4.243, nw), `Rail_End`: STEEL rails 0.05×0.07 at gauge 0.8, 6 sleepers 1.2×0.18×0.1. `Prop_Minecart`: 1.2×0.8×0.6, 4 wheels r 0.15, ore heap. `Pile_Ore_1–3`: flattened jittered ico r 0.8 / 1.1 / 1.4, z-scale 0.55, ROCK with STEEL flecks. `Pile_Coal_1–3` (COAL) |
| Iron | `Prop_CharcoalMound`: half-ico r 2.0 × h 1.4, SOIL with COAL patches, 4 VOID vents (4 × Smoke). `Prop_Bloomery`: lathe [(1.2,0),(1.1,1.0),(0.9,2.2),(0.7,3.2)] STONE/CLAY, GLOW arch 0.4×0.5 (Fire, Smoke). `Prop_Bellows`: HIDE wedge 1.0×0.6 |
| Leather and cloth | `Prop_TanningPit`: stone rim 1.2×1.2×0.3, HIDE liquid. `Prop_HideFrame`: 1.4×1.8 frame + HIDE quad + lacing. `Prop_DyeVat`: stave `_cyl` r 0.6×0.8 + 2 IRON hoops; liquid disc in **CLOTH_A**, so `{"cloth":"Blue"}` gives a blue vat. `Prop_ClothRack`: posts 3.2, poles at 2.2 / 2.6 / 3.0, 7 strips 0.5×2.0 in CLOTH_A, CLOTH_B, YELLOW, PAPER. `Prop_Loom` (2.0×1.3×1.8, warp as 20 boxes 0.01 thick, CLOTH_A roll). `Prop_SpinningWheel`. `Pile_Hides_1–3`. `Pile_Wool_1–3` (CLOTH_B bales 0.8×0.6×0.6) |
| Food | `Kiln_Oast`: round STONE wall r 2.2 × 5.0, 16 segments; ROOF cone r 2.4 × h 3.6; white PLASTER cowl 0.8×0.8×1.0 with a slanted top and a vane (top 10.6). `Prop_MashTun` (barrel r 0.9). `Prop_CiderPress` (frame 1.4×1.0×2.0, screw r 0.1, basin). `Prop_Skep` (HAY lathe r 0.28 × 0.45). `Prop_BeeBench` (3 skeps under a Roof_Pent). `Prop_HerbBundles` (pole with 6 bundles). `Prop_Cauldron`. `Prop_DryingRack_{Meat,Herbs}`. `Prop_Antlers`. `Prop_Dovecote`: lathe r 2.0 × 5.0, 3 rows of VOID holes 0.15×0.2, cone r 2.2 × 3.0, open lantern, 8.5 m |
| Crops | new `gen_crops` atlas cells + `crop_rows`: `Crop_Hops` (poles 4.5–5.0 with twine and vine cards), `Crop_Barley`, `Crop_Flax` (blue flowers (0.35, 0.5, 0.95)), `Crop_Vines` (1.4 m trellis rows), `Crop_Sunflower` (2 m) |

### M7: defence and elite pieces (5 days)

| Piece | Geometry | Flags |
|---|---|---|
| Palisade_Straight (3.0) / _Diag (4.243) | 10 / 14 logs Ø 0.30 ± 0.04 at 0.30 spacing; heights U(3.3, 3.9), seeded; 0.45 cone tips (WOOD); BARK_OAK shafts sunk to −0.8; inner rails 0.14×0.2 at z 1.0 and 2.6 on +Y, with BURLAP lashings | ng / nw |
| Palisade_Post / _Walk / _Gate / _GateLeaf / _Tower / Prop_Beacon | Post: 3 logs Ø 0.4 × 4.2 at a vertex. Walk: catwalk 1.0 wide at z 2.3, y 0.25..1.25, on posts at x −1.5 and 0 (+ `_Ladder`). Gate: posts Ø 0.45 × 5.2 at x ±1.5, lintel log at 4.4. GateLeaf: separate object 1.45×3.4, hinge pivot, `hinge_axis`. Tower: 1 cell, 4 logs Ø 0.36 × 6.5, platform at 4.5, log parapet 1.1, 4-segment cone r 2.6 × 2.2 (thatch or shingle). Beacon: IRON basket on a 5 m pole, GLOW, Smoke | ng |
| TownWall_Straight | 2.0 thick (y −1.0..+1.0, outer face −Y). Outer batter +0.35 at the base, fading to 0 at z 1.8. STONE panels with `grid_cut` + `wall_rocks`. ASHLAR string course at 5.6. Outer parapet (y −1.0..−0.5) breast to 7.1; merlons 0.9 wide at x ±0.75 up to 7.9, each with a VOID slit 0.1×0.55; coping 0.12. ASHLAR walk at **6.2**, y −0.5..+1.0. Skirt to −1.5 | std |
| TownWall_Diag / _Corner_Out / _Corner_In / _Step / _Ruin | Diag 4.243 (nw). Step: base and walk rise by LVL over 3 m. Ruin: ragged top U(3.8, 5.2), no merlons, rubble `rock()` heap | std / nw |
| TownWall_Stair | 3.0 run, 2.067 rise, 8 steps (rise 0.258, tread 0.375) against the inner face, y 1.0..2.1; solid support down to local −4.2. Placed at z 0, 2.067 and 4.133 (34.6°) | ng |
| GuardTower_Wall2 / GuardTower_WallL | `guard_tower()` with 1.2 m gaps cut in the hoarding breastwork on 2 opposite / 2 adjacent sides; centred on a grid vertex; ground door facing +Y (inside) | ng |
| TownWall_Tower_Round / Roof_Cone_R{1.2, 2.2, 3.4} | Tower: r 3.0 on a vertex; walk at 8.5; ring of 16 merlons; 3 levels of slits; openings at 6.2 on ±X. Cones: 16 segments, h 1.9·r, bell-cast skirt of 0.25·r at KICK, finial | ng / nw |
| Gatehouse_Block (+ Portcullis, Gate_Leaf) | 3×2 cells centred on the wall line; masonry to 6.2. Passage along Y: hw 1.6, spring 2.8, crown 4.4. IRON portcullis (separate object, 0.08 bars at 0.3 pitch) half raised at y −2.4; 2 PLANKS leaves (separate objects). Half-round towers r 1.8 at (±3.0, −3.0) up to 9.0 with Roof_Cone_R2.2. Above 6.2: Wall_Timber* + Corner_Timber, `Wall_Timber_Door` onto the walk on both end walls; Roof_Hip ends + Roof_Mid at 9.0 | ng |
| Parapet_Crenel / Parapet_Corner / Roof_Pyramid_6 / Roof_Pyramid_9 | Parapet: 6 corbels 0.3×0.45×0.4 at x −1.25 + 0.5i, z −0.4..0; breast 0.9 high at y −0.6..−0.25; merlons 0.9 × 0.8 at x ±0.75; coping 0.12; walk slab 3.0×1.2. Pyramids: 4-segment cone rotated 45°, r 2.83 × h 2.86 and r 4.88 × h 4.93, ROOF UVs as in `guard_tower` | nw |
| Training props | `Prop_TrainingDummy` (post, crossbar, BURLAP head, CLOTH_A shield); `Prop_ArcheryButt` (straw disc r 0.6 × 0.3 on an A-frame; rings YELLOW / CLOTH_A / CLOTH_B); `Prop_ArmorStand` | ng |

### M8: civic pieces (1 day of pieces)

| Piece | Geometry |
|---|---|
| Prop_MarketCross | 3 octagonal ASHLAR steps (r 1.8 / 1.4 / 1.0, each 0.3 high), tapering shaft 3.5, small gabled head; 5.3 m total |
| Prop_Maypole | lathe pole 9.0 in CLOTH_A/B bands; wreath `ring()` at 7.0 in LEAVES + PINK/YELLOW icos; 8 ribbons 0.08 wide from 7.0 to stakes at r 3.2, sag 0.3 |
| Prop_Stage | plank platform 6×3×0.8 with a CLOTH_A canopy |
| Prop_Stocks / Prop_Pillory | 2 posts, holed plank, bench |
| Prop_BathTub | half barrel r 0.7 with WATER |
| LowWall_GateArch / LowWall_Diag / Deco_Hedge (3.0 and 4.243) | gate: single-cell arch with `arch_ring`. Hedge: FOLIAGE clumps via the `make_bush` logic, trimmed to 3.0×0.8×1.2 |
| Chapel_InnerCorner | concave corner for HC 4.5 walls |

## 7. House types

The effort column covers only the builder, once its milestone's pieces exist.

| Type (tier) | Role | Look | New pieces | Reused | Footprint (lot) | Effort / milestone |
|---|---|---|---|---|---|---|
| Settler camp (T0) | first shelter, 2 beds per tent, first storage | canvas, fire glow, covered wagon | tents, campfire, bedroll, covered wagon | Crates, Sacks, BarrelStack, Pile_Logs_1 | 3×3 | S / M3 |
| Hovel (T1) | cheapest home, 4 beds | "haystack" thatch on 2.4 m daub walls; cruck gables; vent smoke; no chimney | wattle set, cruck gable, thatch vent | RoofThatch_Mid/Hip, Woodpile, GardenBed, Chickens, Deco_Weeds | 2×2 (3×3) | S / M3 |
| Longhouse (T1) | 8 beds + 4 livestock | low thatch "loaf", 15 m long; people at one end, byre at the other | Wall_Wattle_Byre | RoofThatch_Mid ×3, RoofThatch_Gable_Planks, Fence, Trough, HayBale, Cow, Sheep | 5×2 (8×3) | S / M3 |
| Log cabin (T1–2) | frontier home for woodcutters and hunters | dark logs, silver shingle roof, big gable chimney | log set, Roof_Gable_Logs, Shingle | Roof_Mid, Porch, Woodpile, Stump, Log_Fallen | 2×2 or 3×2 (3×3) | S / M3 |
| Cottage variants (T2) | standard home, 6 beds | existing cottage plus chimney-gable, half-hip, cross-gable, gallery, PlasterUp and slate/shingle options | none beyond M2 and M4 | everything existing | 2–4×2 | S / M2 + M4 |
| Rowhouse terrace (T3) | dense housing with shop slots; firewalls stop fire spread | continuous colour blocks, stepped ridges, party chimneys and firewalls | Flush, Firewall, Mid_Cap, Chimney_Party, Corner_Party, shops, PlasterUp, Passage | all walls, roofs, awnings, signs | units 1–3 × 2; 4–8 units | M / M4 |
| Gable-front townhouse (T3) | craftsman or merchant house on the plaza | steep 6 m gable to the street, oriel, hoist, shop | Roof_Gable_Hoist, shop | Wall_Timber_Oriel, Balcony, Sign | 2 × 3 (+1 alley cell) | S / M4 |
| Corner house (T3–4) | anchor at a street corner, 2 shops | L-plan with a turret on the convex corner (tip 14.2) | turret stack, shops | Roof_LCorner, InnerCorner_* | L 3+2 | S / M4 |
| Stone merchant house (T4) | rich trader, storage 40 | all stone, stepped gables, slate, cross-gable hoist over stacked loading doors, twin windows | StoneUp, Stepped, CrossGable_Hoist, CellarHatch, Stair_Stone_Ext | Wall_Stone_*, Corner_Stone, Roof_Mid | 3×2 + 3×1 yard | S / M4 |
| Courtyard inn (T4) | lodging and trade hub | U-plan around a yard, galleries, cart passage, stable range | Passage + Vault, Gallery_Timber, LCorner_Mirror | build_stable, Well, Cart, Trough, Bunting, TavernSign | 7×5 | M / M4 |
| Tower house (T5) | minor noble; security; landmark | 4-storey stone tower; domestic (slate pyramid, 4 stone turrets) or fortified (parapet, bartizans, inner pyramid, banner) | Parapet, Pyramid_6, Turret_Seg_Stone | Roof_Hip + Hip_Plain, Stair_Stone_Ext | 2×2 (3×3) | M / M7 |
| Manor (T5) | lord's residence | L-plan hall + attached tower house + walled forecourt, dovecote, hedges | LowWall_GateArch, Deco_Hedge | build_L_block, tower house, Fountain | lot 8×7 | L / M7 |
| Almshouse (T3 civic) | beds for the poor | 4 one-cell units under one roof, bellcote | Roof_Bellcote | Wall_Stone_* | 4×2 | S / M4 |

### 7.1 Recipes

- **Camp**
  - Tent_A at (−2.5, 1.5, 10°) and (2.2, 2.0, −15°); Tent_Bell at (0, −2.6); Campfire at (0, 0).
  - 4 bedrolls; wagon at (4.2, −1.5, 30°); Crates, Sacks, BarrelStack, Pile_Logs_1.
- **Hovel**
  - `build_block(n=2, floors=["Wattle"], style=district_style(s,"fringe"), faces={"R":["DW"],"F":[".W"],"B":[".."],"L":[".."]}, ends=("cruck","cruck"), breakers=[("vent",0)])`.
  - The door is on the R gable end, which faces the street.
  - Variant: `ends=("hip","cruck")`.
  - Lean-to variant: `LeanTo_Thatch` on the L gable end (not the eave wall).
  - Upgrade look: `Chimney_Gable_H24` on L replaces the vent.
  - Upgrade in place, 2×2 → cottage 2×2 → townhouse 2×2 (P1 rule), with `upgrade_to` metadata.
- **Longhouse**
  - `n=5, floors=["Wattle"], ends=("cruck","planks"), faces={"L":["D."],"R":["B."],"F":[".W.W."],"B":["....W"]}`, vents in bays 1 and 3.
  - Paddock of 3×3 cells off R, with FenceGate, Trough, HayBale, 1 Cow and 2 Sheep.
- **Log cabin**
  - `floors=["Log"]`, style roof "Shingle", `ends=("logs","logs")`, `("chimney_gable","L")`, F "DW" or "WDW"; Porch allowed.
  - Dress: ChoppingBlock, Woodpile, Stump.
- **Cottage**
  - `build_cottage(seed, district)` uses district weights.
  - Chimney_Gable with p .30 instead of the ridge chimney; halfhip per district (M4); cross gable p .20 if n ≥ 3 (M4); Gallery_Top on the back, p .15 (M4); PlasterUp per district (M4).
- **Terrace**: `build_terrace(coll, x0, x1, y_street, side, seed, district="market")`.
  1. **Unit size:** w ∈ {1: .2, 2: .5, 3: .3}. Storeys ∈ {2: .25, 3: .5, 4: .25}; if equal to the previous unit, change by ±1 with p .6.
  2. **Style:** plaster must differ from the previous unit.
  3. **Ground string** per module from {S .45, D .3, W .25}, with at least one D per unit. Every 4th unit with w ≥ 2 gets one P (a Passage_Vault goes behind it).
  4. **Boundary between equal-height units:**
     - no end walls; both end bays are Roof_Mid;
     - Roof_Firewall on even boundaries, and always when the roof materials differ;
     - Chimney_Party on odd boundaries;
     - Corner_Party on F and B on every level where the families or styles differ.
  5. **Boundary between unequal heights (taller unit t, lower unit l):**
     - t places its end walls and the corners at (x_b, ±3) only on levels f_l … f_t−1;
     - t's end = "flush" (the parapet on x_b); l's end = "none" (Roof_Mid_CapL or CapR).
  6. **Street ends** use {stepped .3, flush .3, gable .2, halfhip .2}.
  7. **Dressing:** Banner_Wall on every 2nd unit at level 1; Awning or Roof_Pent over S modules; the Sign kind matches the goods.
- **Gable-front townhouse**
  - `n=3, depth=2, floors=["Plaster","Timber","Timber"]`, placed so that R faces the street.
  - R faces: `["SD","OW","WW"]`; `ends=("gable","hoist")`; plus `("emblem","R",kind)`.
  - Keep one empty cell to each neighbour.
- **Corner house**
  - `build_L_block(a=1, b=1, floors=["Stone","Timber","Timber"])` with S modules on both street faces.
  - Turret: Corbel at z 3.0, Seg at 3.0, 5.8 and 8.6, Cap at 11.4; axis at world (−3.6, −3.6).
  - Banner_Wall on the corner.
- **Merchant house**
  - `n=3, floors=["Stone","StoneUp","StoneUp"]`.
  - F faces `["SDS","TLT","WLW"]`; B `[".W.","D.W","W.W"]` with `("stair_stone","B",0)` up to the B door in bay 1.
  - `ends=("stepped","stepped")`, roof Slate; `("cross_hoist",1)`, `("chimney",0)`.
  - CellarHatch at F bay 2; optional stone turret at FL (p .5).
  - Yard 3×1 with a cart, BarrelStack and Crates.
- **Courtyard inn**
  - Front range n = 7: `Roof_LCorner` at the left junction, `Roof_LCorner_Mirror` at the right, 3 Mid bays with a P in the middle cell.
  - Wings 2 wide, going 3 cells back (Mid ×2 + Gable, rot 90).
  - Gallery_Timber on the yard faces; `build_stable` across the back.
- **Tower house (domestic)**
  - `n=2, floors=["Stone","StoneUp","StoneUp","StoneUp"]`, F level 0 "XX", F level 1 ".D" via `("stair_stone","F",0)`.
  - Ends hip + hip (Roof_Hip + Roof_Hip_Plain, apex 15.59), slate.
  - 4 stone turrets: corbel at 8.6, Segs 8.6–14.2, caps to 17.0.
- **Tower house (fortified)**
  - Same walls, but Parapet_Crenel ×8 + ×4 corners at 11.4 and Roof_Pyramid_6 inside (apex ≈14.4).
  - 4 stone turrets r 0.85 corbelled at 11.4; Banner_Roof.
- **Manor**
  - `build_L_block(a=4, b=2, floors=["Stone","StoneUp"], roof "Slate")`.
  - Domestic tower house at the far end of wing A. The tower owns the shared wall; the hall end there is `none`.
  - Forecourt 6×4: LowWall + LowWall_GateArch, Deco_Hedge parterre, Fountain, Dovecote; banners in Purple.
- **Almshouse**
  - `n=4, floors=["Stone"]`, F "DDDD", `("bellcote",1)`, gable ends; garden beds in front.

## 8. Village features

| Feature | Role | Look / tell | New pieces | Reused | Footprint | Effort / milestone |
|---|---|---|---|---|---|---|
| Stockpile yard | player-zoned storage | bordered cells with piles | Stockpile_Border, Pile_* | — | n cells | S / M1 |
| Woodcutter's lodge | logs, 2 jobs | log cabin + LeanTo over Pile_Logs_3; end grain seen from above | ChoppingBlock, Sawhorse | log cabin, LeanTo, Stump | cabin 2×2, lot 3×3 | S / M3 |
| Forester's hut | replants trees | 1-cell Shed hut with RoofS_Single + sapling nursery | Crop_Saplings | Shed set, Fence | lot 3×2 | S / M3 |
| Sawpit yard | logs → planks (T1) | pit, log on trestles, sawdust | Prop_SawPit | Pile_Logs, Pile_Planks | 2×1 + pile | S / M3 |
| Carpenter / cooper | planks → goods | 2×2 cottage + 2 LeanTo, half-built barrel, saw emblem | — | cottage, Table, Pile_Planks | lot 3×2 | S / M3 |
| Granary | grain storage, less spoilage | Shed walls at z 0.75 on 9 staddle stones, thatch pyramid (2 hips), detached steps | StaddleStone, GranaryStep | Shed set, RoofThatch_Hip, Sacks | 2×2 | S / M3 |
| Storehouse | general storage (T2) | 3×2 barn with one Posts_Barn cart bay + bordered yard | — | Wall_Barn, Posts_Barn, piles | 3×2 + 3×2 | S / M3 |
| Root cellar | vegetable storage | earth mound + stone portal + vent | Prop_RootCellar (half-ellipsoid 3×4×1.6 SOIL, `wall_stone_door` arch at 0.8 scale) | Plant_TallGrass | 1×2 | S / M3 |
| Pig sty / sheepfold / byre | animal products | LowWall pen + pent shelter; fence pen + LeanTo_Thatch; barn + paddock | animals, HayRack | LowWall, Fence, LeanTo_Thatch, Trough, build_barn | 3×3 each | S / M3 |
| Privy / wayside shrine | hygiene; faith coverage | plank booth; candle niche at crossroads | Privy, Shrine | — | sub-cell | S / M3 |
| Market hall | market in bad weather; landmark | open arcade ground floor, timber upper floor, hip ends, cupola | Wall_Arcade_Open, Ceiling_Cell | Roof_Hip, Roof_Cupola, MarketStall, Banner_Wall | 4×2 | S / M4 |
| School | education | 3×2, 2 floors, bellcote, book emblem | Roof_Bellcote | cottage walls, Bench | lot 3×3 | S / M4 |
| Watermill | flour on rivers | 3×2 house + turning wheel over the water | WaterWheel, Wall_Stone_Axle, WheelPier, Millstone | walls, roofs, Sacks, Cart | 3×2 + wheel strip | M / M5 |
| Fisher's hut | fish, 2 jobs | Shed 2×1 with RoofS on the bank, pier, rowboat, net rack | pier set, boats, racks | Crates | 2×1 + 1×3 pier | S / M5 |
| Smokehouse | preserves fish and meat | 1×1 stone hut, RoofS_Single, vent smoke | — | Wall_Stone, Roof_Vent | 1×1 | S / M5 |
| Lavoir | washing; social | 2×1 open posts + RoofS over a basin | LavoirBasin | Wall_Posts, Laundry | 2×1 | S / M5 |
| Bridges / docks / quays | crossings, harbour | see M5 | M5 set | LampPost | per river | M / M5 |
| Sawmill | powered planks (T2) | 3×2 open shed on Posts_Barn + frame saw next to the wheel | Prop_FrameSaw (2.6 m posts, blade sash, 6 m log carriage) | M5 wheel set | 3×2 + wheel | M / M6 |
| Quarry + mason's yard | stone | stepped pale cut faces; treadwheel crane | quarry set, crane, Banker | LeanTo, rocks, Pile_Stone | 3×3 (quarry faces on cliffs) | M / M6 |
| Clay pit + kiln | bricks, pots, roof tiles | bottle kiln smoke | kiln set | shop `_Pots` | lot 3×3 | S / M6 |
| Mine | ore | portal in a rock mound, rails, cart, spoil heap | mine set | Lantern, LeanTo | 2×2 | M / M6 |
| Charcoal burner + bloomery | fuel → iron for the blacksmith | smoking mound; glowing furnace | CharcoalMound, Bloomery, Bellows, coal/ore piles | Anvil, LeanTo | lot 2×2 each | S / M6 |
| Tannery | hides → leather (edge of town) | pits and hide frames | tannery props | LeanTo, Roof_Vent | lot 3×3 | S / M6 |
| Dyer's yard | dyed cloth (T4 luxury) | 3–4 vats in different cloth colours + cloth racks: the most colourful spot in the village | DyeVat, ClothRack | Laundry | lot 3×2 | S / M6 |
| Weaver | cloth | townhouse with a Cloth shop front + loom | Loom, SpinningWheel | shop, Roof_Pent | townhouse | S / M6 |
| Brewery + oast | ale for the tavern | 3×2 range + round oast with a white cowl | Kiln_Oast, MashTun, Crop_Hops/Barley | BarrelStack | lot 5×3 | M / M6 |
| Orchard + cider house | cider | 4 Tree_Apple + press under a LeanTo | CiderPress | Tree_Apple, LadderLean | lot 4×2 | S / M6 |
| Apiary + chandler | honey, wax, candles | bee benches in lavender; Candles shop front | Skep, BeeBench | Crop_Lavender | 2×2 | S / M6 |
| Herbalist / butcher / hunter | healing; meat; game | herb bundles + cauldron; Meat shop + sty; cabin + antlers + hide frames | HerbBundles, Cauldron, Antlers | Sign_Potion, GardenBed, cabin | lot 3×3 each | S / M6 |
| Palisade ring → town wall + gatehouse | defence tiers | see M7; the gatehouse replaces the palisade gate on the same middle cell | M7 set | GuardTower | per wall | M–L / M7 |
| Barracks + training yard | soldiers, training | 4×2, 2 floors, slits, Gallery on the yard side, archery butts | training props | WeaponRack, Banner_Pole | lot 4×5 | S / M7 |
| Market cross / festival green / stocks | plaza centre; happiness; law | see M8 | M8 props | Bunting, Festoon, Bench | 1×1 / 4×4 / 1×1 | S / M8 |
| Bathhouse / wash house / healer | hygiene; health | stone house with 2 vents + tubs; 4 posts + 2 Roof_Hip over a basin; 3×2 with Gallery and bellcote | BathTub | Roof_Vent, Laundry, Gallery | 4×3 / 2×2 / 3×3 | S / M8 |
| Guildhall | guild policies, prestige | T-plan: street range `Gable, Mid, Roof_T, Mid, Gable` (18 m) + rear wing of 2 cells; `Wall_Arcade_Open` on the 4 central bays; Balcony; Cupola | Roof_T | Wall_Timber*, Roof_Cupola | 6×4 | M / M8 |
| Cruciform church | faith tier 2 | nave 4×2 + crossing 2×2 (Roof_X) + 1-bay transepts (Roof_Gable_Stone) + chancel with a hip; BellTower at the west end | Chapel_InnerCorner, Roof_X | Chapel_* walls, BellTower | 8×4 | M / M8 |
| Trading post | trade with outsiders | covered wagon, bell tent, hitching rail, scales emblem | — | camp pieces, Crates | lot 3×3 | S / M8 |
| Keep (optional) | stronghold | 3×3, 5 floors StoneUp, walls to 14.2; parapet, Pyramid_9 (apex 19.3); 4 turrets | — | M7 set | 3×3 | L / after M8 |

**Deferred:** L roof family (9 m deep tithe barn), gable-front valley family, a deeper jetty (0.45 m offset plus +0.25 roof lift), thatch eyebrow dormer, overshot race with `MillRace` and `_Spout`.

## 9. Terrain interface (agree with the terrain track)

1. **Grid.** Terrain tile = CELL = 3.0, with tile corners on kit grid vertices (primal grid).
   - A cell is flat when its 4 corners are equal.
   - A footprint is buildable when every cell in it is flat at the same level.
   - If the terrain track picks a dual grid instead, the same contour meshes go on cell edges; only placement code changes.
2. **Step height.** LVL = 1.5 is requested: two levels equal H1.
3. **Contour pieces** (quay, quarry face, retaining walls, cliff props):
   - Straight 3.0 along a cell centre-line; Diag 2.121 between adjacent edge midpoints; saddle cases 5 and 10 are two diagonals.
   - Pivot at the segment midpoint, face −Y toward the lower side.
   - Heights are multiples of LVL.
4. **Grid-drawn pieces** (palisade, town wall, low wall, hedge, fence, rails): Straight 3.0 on cell edges, Diag 4.243 across a cell, joint pieces at vertices. `_Step` covers slope tiles.
5. **Water.** Water tiles use water −0.6 and bed −1.5. Piles go to −3.0, the quay face to −2.0 and the town-wall skirt to −1.5.
6. **Skirts.** New ground-contact pieces carry a hidden skirt to −0.6. Existing walls get skirts only after the M0 regression snapshot, in a separate commit (`SKIRT_EXISTING=True`).
7. **Watermill check.** The house-local rectangle x ∈ [L/2+0.85, L/2+1.85], y ∈ [−3.9, 0.9] must be water. If the shoreline does not reach the end wall, add `Quay_Straight` in front of it.

## 10. Build order (one engineer, about 38 days)

| # | Milestone | New meshes | Days | Why it comes here |
|---|---|---|---|---|
| M0 | Infrastructure (§5) + regression snapshot | 0 | 3.5 | every later piece depends on the API; stages and sockets can't be retrofitted cheaply |
| M1 | Construction + stock | ~30 | 3 | the core colony-sim feedback loop; applies to every existing building immediately |
| M2 | Skyline pack + district styles + retrofit | ~35 | 3.5 | fixes the "field of orange wedges" across the whole existing town at low cost |
| M3 | Humble walls, S roofs, camp, T0–T1 houses, early chain | ~60 | 5.5 | early game currently has no housing below the cottage |
| M4 | Town tier (StoneUp, shops, `roof_field`, turrets, galleries) + terraces, merchant, inn, market hall | ~50 | 6 | T3–T4 housing and dense streets |
| M5 | Water set + watermill, fisher, smokehouse, lavoir | ~28 | 4 | depends on the terrain track's water tiles |
| M6 | Production props + chains | ~45 | 5 | stone, metal, cloth, food chains |
| M7 | Defence + tower house, manor, barracks | ~35 | 5 | late-game edge and landmarks |
| M8 | Civic props + guildhall, church, bathhouse | ~12 | 3 | polish and happiness buildings |

**Cross-track dependencies:**
- The stone-texture rework should land before M4 and M7. StoneUp, quays, bridges and a town wall 7.9 m tall show a 3.0 m stone tile across large areas; ask that track for macro variation.
- The terrain track must confirm LVL, the grid convention and the water datum before M5.

## 11. Acceptance tests

### 11.1 Automated `kit_qa()` (must return an empty list after every milestone)

1. **Material slots.** Every `SM_VK_*` mesh has exactly 50 slots; no face index is above 49.
2. **Stage coverage.** Every builder runs for stage 0, 1, 2 and 3, and every `stage_piece` target exists.
3. **Wobble rule.** Every spec with `wobble=True` has its length L in `PIECE_META` with L/2 % 3 == 1.5.
4. **Horizontal seams.** For each wall family, place `.`, `W` and `D` at x = 0, 3 and 6. The outer-skin vertices (|y − face| < 0.06) at x = 1.5 and 4.5 must match in y within 2 mm.
5. **Stacked seams.** Wall_Stone with Wall_StoneUp at z 3.0, and StoneUp on StoneUp at z 5.8: outer-skin vertices at the seam match within 2 mm.
6. **Roof continuity.** For every roof piece, the edge vertices at x = ±1.5 lie on `roof_z(|y|)+roof_sag` within 5 mm. `roof_family("M")` must reproduce the old `roof_profile()` exactly.
7. **Sockets.** Every piece containing GLOW, clay pots or fire has a Smoke, Light or Fire socket. Every door piece has a Door socket at (0, −0.9, 0).
8. **Wattle door rule.** `build_block` raises on a Wattle door under an eave or hip end.
9. **Piles.** Every Pile_* fits within 2.9×2.9×1.6. Scaffold planks do not overlap any SHUTTER face in the M1 stage renders (bounding-box test).
10. **Slopes.** Every walkable stair or ramp is ≤ 35° (town-wall stair 34.6°, bridge ramp 21.8°). `ext_stair` and `Stair_Stone_Ext` (≈50°) are flagged for NavMeshLink.
11. **Triangle budget.** Each piece has ≤ 1.5× the triangle count of the heaviest existing piece in its category (walls, roofs, props, landmarks).

### 11.2 Regression (M0)

- Before M0, `snapshot_kit()` records the vertex count and bounding box of all 146 pieces.
- After M0 (with SKIRT_EXISTING off), every piece must match within 1e-5.
- Re-render `nature_town_aerial.png` from the saved camera: mean absolute pixel difference < 0.5 %.

### 11.3 Visual checks (catalog sheets like `catalog_walls.png` + targeted renders)

- **M1:** strip of stages 0–3 for a 3×2 two-storey stone cottage and for the tavern (L-plan).
  - No floating parts; a frame in every roof bay at stage 2.
  - Piles of all 3 levels on a 3 m grid.
- **M2:** re-render the aerial camera with a district-built demo town (`build_town2`).
  - A roof-ID pass (roof materials swapped for flat emission colours) shows Red ≤ 45 % of roof pixels.
  - No 3 consecutive houses on a street share (roof material, end kind, storeys).
  - Emblems on the blacksmith, bakery and tavern read as ≥ 8 px silhouettes at 1920×1080.
  - Close-up of the pyramid apex shows no z-fighting.
  - Stepped and flush parapets fully hide the slab ends.
- **M3:** line-up of camp, hovel, longhouse, cabin and a 2-storey cottage.
  - Measured ridges: hovel/longhouse 6.59 (+ thatch cap), cabin 7.19, cottage 9.99.
  - Hovel eave-roll underside ≥ 1.65; cruck blades stay under the thatch.
  - Log corners alternate with no interpenetration.
- **M4:** 8-unit terrace from 3 seeds.
  - Close-ups at an equal-height boundary with a firewall and at an unequal one (Flush + Mid_Cap): no open roof section and no hole in an end wall.
  - The corner-house turret contains the eave corner (distance check < r).
  - Cross-gable eave stops close the neighbour eave.
  - Half-hip creases are clean (no sawtooth).
  - Passage ring top ≤ 3.0; merchant house hoist rope lines up with the loading doors.
- **M5:** river test scene (2-cell river).
  - Wood bridge End + Bent + End.
  - Stone bridge Ramp + Span + Ramp = 12 m.
  - Pier of 3 decks + End.
  - Watermill: wheel dips 0.5 m into the water and spins about an axle perpendicular to the end wall over a 120-frame turntable.
- **M6:** colony-camera crop of each production building.
  - Props and piles cover ≥ 30 % of the lot.
  - Its roof or yard tell (vent, cowl, crane, kiln, vats, mound smoke) is identifiable at 1920×1080.
- **M7:** wall circuit of 20 modules with 2 GuardTower_Wall2, 1 gatehouse and 3 stair runs.
  - Walk surface at 6.2 ± 0.02 from wall to hoarding to gatehouse door.
  - Merlons don't pierce the hoarding; gate leaves and portcullis move about their pivots.
- **Unity smoke test (after M1, M4 and M7):**
  - Import 5 pieces + 1 recipe JSON; the prefab assembles at stages 0–3.
  - Sockets arrive as child transforms.
  - Renderer material count equals the number of materials actually used (unused slots stripped).
  - Spin and hinge objects rotate about their pivots.