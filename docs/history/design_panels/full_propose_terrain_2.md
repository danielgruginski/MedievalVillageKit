# Terrain Tile Kit: marching-squares (corner-driven) proposal

**Scope:** terrain tile kit only. **Perspective:** stylized environment art (WoW / Warcraft III look). **Target:** Blender 4.4 procedural generation, Unity at runtime.
**Reference code:** `vk_helpers.py` (Kit, NK via vk_nature, `place()`/`place_v()`, `kit_mats()`), `vk_tex.py`, `vk_texgen.py`, `vk_mat.py`, `vk_nature.py`.

---

## 0. Key decisions at a glance

| Decision | Value | Why |
|---|---|---|
| Tile size `TT` | **3.0 m = CELL** | One terrain tile equals one building cell. Wall modules sit on tile edges. |
| Corner lattice | Corner (i,j) at world **(3i, 3j)**, which are the building-grid intersections where wall corners go | A building footprint is flat when all its footprint corners are equal. You get 1.5 m of guaranteed flat apron for free. |
| Tier height `TH` | **3.0 m = H1** | Chunky WC3-style proportions (tier = tile). Also enables split-level "hillside" houses whose upper-floor door opens onto the next tier. |
| Height constraint R1 | Corners that share a tile edge differ by at most 1 level. Diagonals may differ by 2. | Gives a closed case set: 16 binary masks plus one 3-level "Stair3" case. |
| Water constraint W1 | A water corner's 8 neighbours must all have the same level | Shore tiles and cliff tiles never mix. Phase 1–2 stay small. |
| Transition position | Every transition crosses a tile edge at its **midpoint** and **perpendicular** to it | This is the seam contract. |
| Irregularity | Profile-only at seams. All variation along the contour fades to 0 inside a 0.35 m end zone. Seams are styled as natural vertical rock joints. | Seams stay exact without looking extruded. |
| Texturing | Ground uses **world-planar** mapping. Cliffs use **manual world triplanar** with strata keyed to world Z. No texture depends on baked UVs. | Textures stay continuous across tiles, rotations and levels. Strata line up map-wide. |
| Surface types (grass/dirt/sand/soil/cobble) | Same corner data, rendered as **per-pixel marching squares** in the ground shader (bilinear corner-data texture plus noise threshold) | 0 extra meshes. No combinatorial explosion with height cases. Seamless by construction. |
| Unique meshes | Phase 1: **8 shapes / 22 variant meshes**. Phase 2: **+7 shapes / 12 meshes**. | |

---

## 1. Grid and registration with the village kit

- Blender world axes: X = east, Y = north, Z = up. Corner (i,j) is at (3i, 3j). Tile (i,j) spans corners (i,j) to (i+1,j+1), i.e. the square [3i, 3i+3] × [3j, 3j+3].
- **Tile mesh pivot:** the tile centre (3i+1.5, 3j+1.5), at z = `base_level * TH`. Mesh-local coordinates are x, y ∈ [−1.5, 1.5].
- Building walls (3 m, centred on the cell edge, 0.5 m thick) lie exactly on tile edges.
- `build_house_v()` uses the footprint **centre** as origin, with x ∈ [−L/2, L/2] and y ∈ [−3, 3]. Snap formula for an n×2 house with footprint min-corner at lattice (a, b):
  - rot 0/180: `origin = (3a + 1.5n, 3b + 3.0, L*TH)`
  - rot 90/270: `origin = (3a + 3.0, 3b + 1.5n, L*TH)`
  - Only rotations that are multiples of 90° are allowed.
- Fences (`prop_fence`, 3.0 m) and `low_wall(L=CELL)` modules coincide with tile edges.

---

## 2. Corner data model

```
Corner { uint8 level;     // 0..7  -> z = level*TH (0..21 m)
         bool  water;     // lake bed at this corner
         uint8 surface; } // 0 grass, 1 dirt, 2 cobble, 3 soil(farm), 4 sand, 5 forest floor
TileFlags { bool saddleBridge; bool steps; }   // optional per-tile overrides
```

- **R1 (height):** for every tile edge, |level_a − level_b| ≤ 1. Enforce it by relaxation, which only lowers corners and is deterministic:
  `repeat: H = min(H, min4(H) + 1) until stable`
- **W1 (water):** `water[c]` requires `level[n] == level[c]` for all 8 neighbours n. The editor or generator flattens neighbours down to that level (or rejects the edit), then re-runs R1.
- **Surface** never changes geometry. It only feeds the ground shader (section 9).
- **Consequence of R1:** within one tile the corner levels relative to the minimum are either all in {0,1} (binary case) or exactly the pattern (2,1,0,1) up to rotation ("Stair3", 0 and 2 on a diagonal). No other 3-level pattern can satisfy R1.
- **Consequence of W1:** any tile with a water corner has all 4 corners at the same level. It uses the shore table only.

---

## 3. Cases and unique meshes

### 3.1 Corner order, bits and canonical shapes

```
 NW(8) ----- NE(4)        bit order is CCW from SW, so a 90° CCW rotation
   |           |          is a 1-bit rotate-left:  rotl(m) = ((m<<1)|(m>>3)) & 15
   |   tile    |
 SW(1) ----- SE(2)        mask = OR of bits whose corner is "high" (cliff) / "land" (shore)
```

Canonical orientation for every shape: the distinguished corner is at **SW** (rows shown as `NW NE / SW SE`).

| Shape | Canonical | Masks covered (rot 0/90/180/270) | Meaning |
|---|---|---|---|
| Flat | `L L / L L` | 0, 15 | no transition |
| Corner | `L L / H L` (mask 1) | 1, 2, 4, 8 | convex knob around the high corner |
| Edge | `L L / H H` (mask 3) | 3, 6, 12, 9 | straight transition, high side south |
| Inner | `H H / L H` (mask 14) | 14, 13, 11, 7 | concave bay around the low corner |
| SaddleA | `L H / H L` (mask 5) | 5, 10 | the two high corners are separate knobs, low ground connects (default) |
| SaddleB | same mask | 5, 10 | high ground connects as a ridge, two bays (if `saddleBridge`) |
| Stair3 | `1 0 / 2 1` | rotation = index of the "2" corner | tier-2 knob at SW, tier-1 bay at NE |
| Steps | Edge + carved stairs | same as Edge when `steps` flag set | walkable connection between tiers |

- Every shape is mirror-symmetric, so **rotations are enough**. No negative-scale mirroring is needed. Mirrored looks are generated as separate variant seeds instead.
- For comparison, full Δ≤2 support (WC3-style A/B/C corners) would need 17 rotation classes. R1 needs 5 plus SaddleB.

### 3.2 Lookup table (4-bit mask to mesh and rotation)

`rot` is in 90° steps, CCW seen from above in Blender.

| mask | shape | rot | | mask | shape | rot |
|---|---|---|---|---|---|---|
| 0 | Flat (level b) | hash&3 | | 8 | Corner | 3 |
| 1 | Corner | 0 | | 9 | Edge | 3 |
| 2 | Corner | 1 | | 10 | Saddle | 1 |
| 3 | Edge | 0 | | 11 | Inner | 2 |
| 4 | Corner | 2 | | 12 | Edge | 2 |
| 5 | Saddle | 0 | | 13 | Inner | 1 |
| 6 | Edge | 1 | | 14 | Inner | 0 |
| 7 | Inner | 3 | | 15 | Flat (level b+1) | hash&3 |

```python
BIT=(1,2,4,8)  # SW,SE,NE,NW
def resolve(h, w, fl, i, j, seed):          # h,w: 4-tuples in SW,SE,NE,NW order
    hv=vhash(i,j,seed)
    if any(w):                                # W1 guarantees equal levels
        m=sum(b for b,wi in zip(BIT,w) if not wi)   # land bits
        if m==0:  return ("Water_Bed", hv&3, h[0])
        if m==15: return ("Flat", hv&3, h[0])
        s,r=SHAPE[m]; s={"Saddle":"SaddleB" if fl.saddleBridge else "SaddleA"}.get(s,s)
        return ("Shore_"+s, r, h[0])
    b=min(h); rel=[x-b for x in h]
    if max(rel)==0: return ("Flat", hv&3, b)
    if max(rel)==2: return ("Cliff_Stair3", rel.index(2), b)
    m=sum(bit for bit,x in zip(BIT,rel) if x==1)
    if m==15: return ("Flat", hv&3, b+1)
    s,r=SHAPE[m]
    if s=="Saddle": s="SaddleB" if fl.saddleBridge else "SaddleA"
    if s=="Edge" and fl.steps: s="Steps"
    return ("Cliff_"+s, r, b)
```

- **Variant:** `v = (vhash(i,j,seed) >> 4) % n_variants(piece)`.
- **Hash:** `vhash = murmur-style mix of (i*73856093 ^ j*19349663 ^ seed*83492791)` using uint32 arithmetic. Write it identically in Python (mask with `& 0xffffffff`) and in C#.
- **Saddle default:** knobs separate for cliffs, water connected for shores. Saddle choice never affects seams (all 4 edges are transitions either way), so it can be changed per tile freely.

### 3.3 Rotation and placement convention

- **Blender:** `place(coll, piece, 3i+1.5, 3j+1.5, base*TH, 90*rot, (0,0,0))` rotates about the tile centre. Canonical SW corner (−1.5, −1.5) maps under +90° to (1.5, −1.5) = SE, consistent with `rotl`.
- **Unity** (Y-up, left-handed, standard FBX axis conversion): `yaw = −90*rot`.
  - Verify once with the asymmetric Corner tile: the canonical knob must land at the (−X, −Z) corner of an unrotated instance.
  - If it lands mirrored, flip the global sign. Never patch individual pieces.

---

## 4. Seam contract

This is the part that must never be violated.

**Principle:** everything on a tile edge is a pure function of that edge's two corner records. Each tile builder produces its boundary from `edge_profile(kind)` and never from its own interior.

### 4.1 Edge kinds

| Kind | Corners (a, b) | Transition |
|---|---|---|
| `F` Flat land | same level, both land | none, z = level·TH |
| `B` Flat bed | both water | none, z = level·TH − 1.05 |
| `C` Cliff | levels differ by 1, both land | cliff profile at the midpoint, t oriented high→low |
| `S` Shore | same level, one water | shore profile at the midpoint, t oriented land→water |

`t` is the coordinate along the edge measured from its midpoint (t ∈ [−1.5, 1.5]), positive toward the low or water corner.

### 4.2 Crossing geometry

- The transition contour **crosses the edge exactly at t = 0**.
- It leaves the edge **perpendicular** to it.
- For the first and last **0.35 m of contour length** it is a **pure extrusion** of the canonical profile along the edge normal.
- Together these guarantee G1 continuity: the same cross-section, the same normals, no crease.

### 4.3 Canonical cliff profile C (TH = 3.0; scale z by TH/3 if TH changes)

Columns: `t` (m, + toward low side), `z` (m above the low level), material, then vertex colour Col.R = AO, Col.B = rim highlight, Col.A = moss gate.

| pt | t | z | mat | R | B | A | note |
|---|---|---|---|---|---|---|---|
| — | −1.50, −1.00 | 3.000 | G | 1 | 0 | 0 | flat high (edge-only samples) |
| p0 | −0.60 | 3.000 | G | 1.00 | 0.0 | 0 | lip rounding start |
| p1 | −0.40 | 2.985 | G | 1.00 | 0.5 | 0 | |
| p2 | −0.22 | 2.945 | G | 1.00 | 1.0 | 0 | sunlit grass crest |
| p3 | −0.05 | 2.880 | G | 0.95 | 0.6 | 0 | |
| p4 | +0.08 | 2.790 | G/C | 0.85 | 0 | 0 | grass lip outer edge (0.16 m overhang), **sharp** |
| p5 | +0.06 | 2.690 | C | 0.55 | 0 | 0 | lip underside |
| p6 | −0.08 | 2.640 | C | 0.40 | 0 | 0 | root/soil recess, **sharp** |
| p7 | −0.04 | 2.300 | C | 0.75 | 0 | 1 | tan band |
| p8 | +0.02 | 2.080 | C | 0.90 | 0 | 1 | tan overhang |
| p9 | −0.07 | 1.950 | C | 0.55 | 0 | 1 | shale recess |
| p10 | −0.05 | 1.620 | C | 0.80 | 0 | 1 | |
| p11 | +0.10 | 1.550 | C | 1.00 | 0 | 1 | up-facing sandstone ledge (moss catches) |
| p12 | +0.10 | 0.950 | C | 0.80 | 0 | 1 | |
| p13 | +0.18 | 0.720 | C | 0.85 | 0 | 1 | toe band |
| p14 | +0.32 | 0.300 | C | 0.70 | 0 | 1 | |
| p15 | +0.50 | 0.080 | C/G | 0.60 | 0 | 1 | toe skirt |
| p16 | +0.60 | 0.000 | G | 0.62 | 0 | 0 | floor |
| — | +1.00 / +1.50 | 0.000 | G | 0.90 / 1.00 | 0 | 0 | flat low; AO reaches 1.0 by t = +1.2 |

- **Band:** t ∈ [−0.6, +0.6]. A 3 m face at about 77° average, with a 0.16 m grassy overhang and two strata ledges.
- **Material boundaries:** always at p4 and p15.
- **Sharp edges:** only the contour-parallel edges at p4 and p6 are sharp. No other sharp edge may touch a tile boundary.

### 4.4 Canonical shore profile S (z relative to the land level; water plane `ZW = −0.25`, bed `ZB = −1.05`)

Col.G is the sand/wet weight: 0 = grass, 0.5 = dry sand, 1 = wet or under water.

| pt | t | z | R | G | B |
|---|---|---|---|---|---|
| — | −1.50, −1.00 | 0 | 1 | 0 | 0 |
| s0 | −0.75 | 0.000 | 1.00 | 0 | 0 |
| s1 | −0.55 | −0.010 | 1.00 | 0 | 1.0 |
| s2 | −0.44 | −0.045 | 0.95 | 0 | 0.3 |
| s3 | −0.46 | −0.150 | 0.60 | 0.5 | 0 |
| s4 | −0.40 | −0.175 | 0.75 | 0.5 | 0 |
| s5 | −0.20 | −0.215 | 0.90 | 0.75 | 0 |
| s6 | 0.00 | −0.250 | 0.90 | 1 | 0 |
| s7 | +0.30 | −0.420 | 0.85 | 1 | 0 |
| s8 | +0.60 | −0.700 | 0.75 | 1 | 0 |
| s9 | +0.90 | −0.930 | 0.65 | 1 | 0 |
| s10 | +1.20 | −1.050 | 0.55 | 1 | 0 |
| — | +1.50 | −1.050 | 0.55 | 1 | 0 |

- s2 to s3 is a small turf roll: a grassy overhanging lip of about 0.1 m over the sand.
- The waterline sits exactly at t = 0 (s6), so the contour *is* the waterline.
- **Foam strip:** its own faces at z = −0.24, t ∈ [−0.12, +0.25]. Its end cross-section (2 vertices) is part of the contour.
- **Water plane:** a 3×3 m quad at `ZW` for every tile with at least one water corner.

### 4.5 Flat edge vertex lists

- `F`: t = −1.5, −1.0, …, 1.5 (0.5 m step, 7 vertices), z = level·TH, normal (0,0,1), Col = (1, 0, 0, 0).
- `B`: t = −1.5, 0, 1.5 at ZB, Col.R = 0.55, Col.G = 1.
- `C` and `S`: flat samples at |t| = 1.0 and 1.5 plus the profile points (21 and 14 vertices).

### 4.6 What must match along an edge (checked by the tests in section 13)

- Vertex count and positions (within 1e-4 m).
- Normals: custom split normals on boundary vertices, set to the analytic 2D profile normal rotated into the edge plane.
- Vertex colour RGBA.
- Material index of faces touching each boundary segment.
- Sharp-edge flags crossing the boundary.
- Foam UV (U integer at the seam).

### 4.7 Final snap pass (last step of every tile build)

Every vertex with |x| or |y| within 1e-4 of 1.5 is overwritten from `edge_profile()`: z, colour and normal. Coordinates are written from the same float constants and rounded to 1e-5. This makes seams correct regardless of interior bugs.

### 4.8 LOD invariance

LOD1 decimates the interior only (contour sampling 0.5 m instead of 0.25 m, 8 of the 17 profile points for interior rings). **Boundary vertex lists are identical at every LOD**, so chunks at different LODs never crack.

---

## 5. Contour shapes and tile construction (generator recipe)

**Contour curves** (all pass through edge midpoints and are perpendicular there):
- **Corner and Inner:** quarter circle of radius 1.5 centred on the distinguished corner. Arc length 2.356 m.
- **Edge:** straight line y = 0.
- **SaddleA/B and Stair3:** superellipse |x/1.5|^n + |y/1.5|^n = 1 with **n = 1.5**, centred on the corner. Its 45° radius is 1.336 m instead of 1.5.
  - This leaves a 0.37 m flat ledge between the two bands along the diagonal. A circle would leave 0.04 m.
  - It only changes the tile interior, so seams are unaffected.
- **Orientation:** every contour runs with the **high/land side on the left**, so sweep frames and foam U run the same way across seams.
- **Clearances:** every contour stays at least 1.5 m from every edge it does not cross. So the band (±0.6) plus the AO falloff (1.2) never reaches a flat edge.

**Build steps** (new module `vk_terrain.py`, class `TK(NK)` to reuse `NK.lcard()` and the custom normals from `nk_finish`):

1. **Slices.** For base b, slice 1 uses mask(rel ≥ 1). Stair3 adds slice 2 (mask(rel ≥ 2) = knob, raised by TH).
   - Slice 2 omits its floor.
   - Slice 1's top region under the knob is simply covered (≤ 1.4 m² hidden).
   - The upper toe skirt tucks 0.05 m below the lower top to avoid z-fighting.
2. **Sweep.** Sweep the profile along each contour, sampled every **0.25 m** (Edge 12 segments, arcs 10, superellipse arcs about 9).
3. **Regions.** Build the flat regions with `mathutils.geometry.delaunay_2d_cdt`:
   - Inputs: the tile square boundary (using the exact edge vertex lists), band offset curves at t = ±0.6, and interior grid points at 0.5 m.
   - Use output_type 3 (inside, holes removed); check on 4.4.
4. **Lip fringe.** `k.lcard()` hanging grass cards:
   - Cell "tallgrass", with about 15% "wildflowers".
   - Card 0.35 × 0.30 m, `up=(0,0,-1)`, rows=1, cols=2, bend 0.15.
   - Placed at p4 + 0.02 m outward, every 0.35 ± 0.1 m.
   - Keep cards ≥ 0.15 m from tile ends.
   - Material LEAVES (existing atlas).
5. **Toe rubble.** `boulder(k, …, mi=ROCK_MOSSY, sub=1, cuts=5)`:
   - 2–3 per Edge, 1–2 per arc.
   - Size 0.25–0.55 m, centres at t ∈ [0.35, 0.7].
   - Centres ≥ 0.45 m from tile edges, so rubble never crosses a seam.
6. **Irregularity** (section 6), then **AO/colour**, then the **snap pass**, then `tk_finish`.
7. **Steps variant.** Carve into the canonical Edge for x ∈ [−1.0, 1.0] (aligned to the 0.5 m edge grid):
   - 12 risers of 0.25 m and 12 treads of 0.25 m, from (y = +1.5, z = 0) to (y = −1.5, z = 3.0).
   - Top and bottom treads are flush with the flat edges.
   - Rock cheek walls 0.5 m thick on each side.
   - Step blocks via `k.box(..., ASHLAR, jitter=0.02)`, plus 3 short wooden rail posts.

**Do not** send terrain through `full_rebuild()`, `Kit.finish()` or `Kit.project()`. `finish(wobble=True)` shifts y by 0.035·sin(2πx/3 + 0.9)·…, which is **non-zero at x = ±1.5** and would break every seam after rotation.

Use a dedicated `tk_finish()` modelled on `nk_finish`:
- Remap used material slots.
- Apply `normals_split_custom_set_from_vertices`.
- Set custom properties: `o["kit"]="VillageTerrain"`, `o["case"]`, `o["variant"]`, `o["tile_m"]=3.0`, `o["tier_m"]=3.0`, `o["sockets"]` (JSON, section 7).

---

## 6. Hand-made irregularity without breaking seams

1. **Along-contour window.** W(s) = smoothstep(0.35, 0.75, s) · smoothstep(0.35, 0.75, L − s), where s is the arc length in metres. W and W′ are both 0 at the ends, so there is no seam and no crease. Everything variable is multiplied by W:
   - **Plan wobble:** the contour is offset laterally by up to ±0.15 m (2-octave `mathutils.noise`, seeded by variant).
   - **Lip crest undulation:** p0–p4 z ±0.04 m; lip overhang 0.10–0.22 m.
   - **Face blocks:** the face is split into blocks 0.7–1.2 m wide.
     - Each block is pushed out +0.04…+0.14 m relative to the canonical profile, with ±4° yaw and a slight lean.
     - Vertical creases at block joints.
     - Plus 0.05 m of fbm on the face.
2. **Seams hidden as joints.** Because every interior block bulges outward, the canonical profile at each seam reads as a **recessed vertical joint** between rock blocks. The eye takes the seam as geology. Strata ledges (p8/p9, p10/p11) are part of the canonical profile, so they run unbroken across the whole cliff line.
3. **Flat pillows.** On `Flat_v1..v3` and on the flat regions of cliff/shore tiles:
   - Displacement D = A · noise(x, y, seed) · Wx · Wy · Wband.
   - Wx = smoothstep(0, 0.6, 1.5 − |x|), same for y, so zero value and zero slope at edges.
   - Wband = smoothstep(0, 0.6, distance to band).
   - A = 0.08 m on Flat, 0.05 m on regions.
   - `Flat_v0` ("Build") has A = 0, for building footprints.
4. **World-space variation lives in shaders, not geometry** (macro tint, surface noise). Tile prefabs stay position-independent and instanceable.
5. **Optional Unity-only upgrade:** while merging chunks, apply one world-space noise (±0.06 m) to vertices of flat regions, weighted by a per-vertex "displaceable" value (Col.B is taken, so store it in UV2.x). Because this is the same world function on both sides, seams stay exact. The Blender preview can apply the identical function.

---

## 7. Variants and anti-repetition

**Variant counts (Phase 1):**

| Piece | Variants |
|---|---|
| Flat | 4 (v0 = Build) |
| Edge | 4 |
| Corner | 3 |
| Inner | 3 |
| SaddleA | 2 |
| SaddleB | 2 |
| Stair3 | 2 |
| Steps | 2 |

"Mirrored" looks come from separate noise seeds, not negative scale.

Other measures:
- Flat and Water_Bed tiles also get a random rotation from `hash & 3` (their edges are rotation-invariant).
- Ground and cliff textures are world-mapped with periods **not** equal to 3 m (grass 4.0, dirt 2.5, sand 2.0), plus a 48 m macro texture. Tile boundaries are invisible on flat ground.
- The cliff texture spans **6 m × 6 m (two tiers)**, so alternating tiers get different strata palettes.
- **Scatter sockets per variant** (stored as `o["sockets"]` = list of `(kind, x, y, z, nx, ny, nz)`, exported as a JSON sidecar for Unity):
  - `toe`: ferns (`make_fern`), mushrooms, pebbles.
  - `lip`: wildflowers, `Bush_Round`, `Plant_TallGrass`.
  - `shore`: reeds (`make_tufts(..., "reeds")`), lily pads.
  - `face`: hanging moss or ivy cards.
  - 4–10 sockets per tile, chosen deterministically with `vhash`.

---

## 8. Heights, tiers and stacking

- A tile mesh is placed at `z = base*TH` where `base = min(corner levels)`. Tall relief comes from consecutive tiers:
  - Two neighbouring Edge tiles leave a **1.8 m grass ledge** (contours 3 m apart minus 2 × 0.6 m bands).
  - Stair3 diagonals leave 0.37 m, which reads as one 6 m corner buttress with a strata break.
- Levels 0–7 (0–21 m). The existing village is at level 0 (z = 0). Lakes at level 0 sit 0.25 m below the village ground.
- **Pathing (grid):**
  - Flat tiles are walkable at their level.
  - Cliff, Stair3 and Saddle tiles are blocked.
  - **Steps** connects its high-side neighbour and its low-side neighbour.
  - Shore tiles are walkable on the land half (or use NavMesh baking from the LOD1 collider).
- **Phase 3 options** (specified so they do not disturb Phase 1 data):
  - *Ramps* via half-level corners (`level + 0.5` with a ramp flag): 2 tiles long for 26.6°. Six meshes: RampLow, RampHigh, SideLow L/R, SideHigh L/R.
  - *Tall cliffs* (relax R1 to Δ ≤ 2): 17 rotation classes.
  - *CliffWater* (cliff toe into the lake bed).
  - *Waterfalls*, *bridges*, *beach vs grass-bank* shore styles.

---

## 9. Materials, textures and UVs

### 9.1 Vertex colour "Col" semantics (terrain only)

| Channel | Ground material | Cliff material |
|---|---|---|
| R | AO | AO |
| G | shore sand/wet weight | (not used) |
| B | lip rim highlight | (not used) |
| A | (not used) | moss gate (same convention as `mossy_material`) |

Unity imports a single colour set, which matches.

### 9.2 New materials

Append these to `kit_mats()` to keep existing indices stable: `TGROUND=45`, `TCLIFF=46`, `TFOAM=47`.

**M_VK_TerrainGround** (new builder `terrain_ground_material()` in vk_mat.py):
- `Geometry.Position` (world) feeds every texture, so no UVs are used:
  - grass at xy/4.0, dirt at xy/2.5, sand at xy/2.0, soil (existing T_VK_Soil) at xy/1.0.
  - macro at xy/48, noise at xy/12.
- **Surface masks** come from the corner-data texture (section 10).
- Sand = max(smoothstep(0.2, 0.45, Col.G), m_sand). Wet = smoothstep(0.6, 0.95, Col.G), which gives colour ×0.6 and roughness 0.35.
- **Rim:** grass is lerped toward its light tone ×1.15 by 0.35·Col.B. This is the painted sunlit lip.
- **Transition outline:** darken by 0.2·4·m·(1−m) at every surface boundary.
- Macro tint: ×(0.9 + 0.2·macro.R), and a hue lerp toward (1.05, 1.0, 0.8) by 0.3·macro.G.
- Normal: `Bump` from the world-mapped blended H maps, strength 0.4.

**M_VK_Cliff:**
- **Manual triplanar.** Weights = |N_world|⁴, normalised, using `Geometry.Normal` (world).
  - X projection: (y, z)/6. Y projection: (x, z)/6. Z projection: (x, y)/6.
  - Blend BC and H, and use `Bump` on the blended H (strength 0.8).
- **Do not use the Image Texture node's BOX projection.** It blends by *object-space* normal, which is wrong on rotated instances.
- **Moss:** same maths as `mossy_material` with M_VK_RockMossy's values (thresh 0.66, soft 0.12, noise_amt 0.75), gated by Col.A.
- Macro tint as above. AO = ×Col.R.

**Also used:**
- **M_VK_TerrainFoam:** alpha-clipped. UV0 = (s along contour / 1.5, t across).
- **M_VK_Water:** the existing material with alpha 0.75. In Unity, a depth-fade tint plus a depth-edge foam line.
- **M_VK_Leaves** (fringe cards) and **M_VK_RockMossy** (rubble): existing.

**Unity:** Shader Graph with world XZ for ground, the Triplanar node (Type Normal) for cliffs, and vertex colour read identically.

### 9.3 New textures (vk_texgen.py, all written with `write_set`)

- **gen_grass(S=1024, seed=301, tile=4.0, depth=0.02)**
  - Clump fbm (β 2.8, fmin 2) mapped to a 3-tone ramp: dark (0.13, 0.27, 0.07), mid (0.29, 0.47, 0.12), light (0.52, 0.66, 0.20).
  - About 2500 painted blade strokes via `draw_segments`: 10–22 px long, 2–3 px wide, ±35° around a per-clump direction, tips +12%.
  - 0.3% white/yellow flower specks.
  - `painted_light` on the blurred height. Roughness 0.9.
- **gen_dirt(S=1024, seed=311, tile=2.5, depth=0.03)**
  - Packed earth ramp (0.42, 0.31, 0.20) to (0.55, 0.43, 0.29).
  - Voronoi pebbles as in `gen_soil`, plus short `crack_segments`. Roughness 0.95.
- **gen_sand(S=1024, seed=321, tile=2.0, depth=0.015)**
  - (0.80, 0.70, 0.50), ripples from fbm with `ax=6`, sparse pebbles. Roughness 0.8.
- **gen_cliff(S=2048, seed=331, tile=6.0, depth=0.08).** Two tiers of strata. Band limits as fractions of TH from each tier bottom, aligned with the geometric ledges:
  - 0–0.24: toe blocks, cool grey (0.38, 0.37, 0.38).
  - 0.24–0.52: sandstone, ochre (0.66, 0.54, 0.38), large facets (`facets()`), vertical joints every 0.6–1.4 m.
  - 0.52–0.68: shale, grey-blue (0.45, 0.47, 0.52), 6–8 laminations, recessed and darker.
  - 0.68–0.87: tan (0.72, 0.63, 0.48), rounded weathering.
  - 0.87–1.0: under-lip soil (0.24, 0.17, 0.11) with dangling roots (`crack_segments(dirbias=π/2)`).
  - Upper tier: sandstone becomes granite (0.58, 0.57, 0.55) and shale becomes purple-grey (0.46, 0.42, 0.48).
  - Painted light: +15% on the top 3 cm of each band, −25% under overhangs.
  - Vertical fractures: `crack_segments(n=18, dirbias=π/2, jit=0.25)`.
  - Share the rock palette and `painted_light` direction with the reworked `T_VK_Stone` so village masonry and cliffs read as the same geology.
- **T_VK_TerrainMacro (512², 48 m):** R = value, G = dry/lush hue, B = threshold noise (β 2.2).
- **T_VK_Foam (512², 1.5 m):** scalloped white bands with alpha, stored in _BC and _Mask.

---

## 10. Surfaces (dirt paths, sand, farmland, cobble): marching squares in the shader

This is the "dirt-path set": **0 meshes.** The same corner lattice drives it:

- **Data texture.** `T_VK_TerrainData_<map>` with one texel per corner: R = dirt, G = cobble, B = soil, A = forest floor (one-hot).
  - Filtering: Linear. Extension: EXTEND.
  - Sampled at `uv = ((P.xy − O)/3 + 0.5) / Ncorners`.
  - Bilinear filtering *is* marching-squares interpolation: inside a tile it depends only on the 4 corners, on an edge only on 2. It is continuous everywhere, so seams are free.
- **Mask per layer, in priority order** (soil < dirt < cobble, sand from Col.G or data):
  `m = smoothstep(0.42, 0.58, w + 0.35*(noise − 0.5))`, then composite, then the transition outline.
- **Path widths:**
  - A single row of dirt corners gives a winding path about 3 m wide.
  - The house-front rule auto-paints dirt on the 2 corners in front of each door.
  - The plaza is a block of cobble corners (flagstone texture in Phase 3; reuse `T_VK_Ashlar` until then).
- **Retire `road_strip()` and `MC_WK_Dirt`** on terrain maps.
- **Upgrade path, if hand-painted WC3-style masks are wanted later:** a 6-shape mask atlas selected per tile by a point-sampled case/rotation texture. It follows the same edge contract.

---

## 11. Buildings and props on tiles

- **Placement rule.** A building occupying footprint cells needs:
  - every footprint corner at the same level L, with no water;
  - all footprint tiles swapped to `Flat_v0`;
  - building z = L·TH.
- **Plain and window walls** may back onto cliff or shore tiles.
  - The worst case is 0.9 m of flat grass between the wall line and the lip start (0.54 m beyond the 0.36 m plinth).
  - Flower boxes (0.55 m) fit.
- **Door walls, and walls carrying a Porch (1.85 m deep), Stair_Ext (1.4 m), Awning, Wall_Stall or LeanTo** require the tile directly in front to be `Flat` at level L.
- **Hillside houses** (Phase 3, enabled by TH = H1):
  - The front corner row is at L; the middle and back rows are at L+1.
  - The front cell's tiles are Edge cliffs hidden inside the ground floor. The back cell is Flat at L+1.
  - The ground floor exists only in the front cell. Its rear becomes a new `SM_VK_Wall_Stone_Retain` (plus `SM_VK_Corner_Stone_Retain`).
  - The upper back wall uses the existing `SM_VK_Wall_Timber_Door`, opening onto the hill at z = H1.
  - Where side cliffs meet the side walls, cover the junction with `SM_VK_Deco_Ivy_A` or rubble.
- **Fences and low walls:** only on `F` edges (3 m modules equal tile edges). Fences along lips come in Phase 3.
- **Props and trees:** raycast down onto the terrain.
  - Blender: `scene.ray_cast` on the merged chunk.
  - Unity: `Physics.Raycast` against the LOD1 collider.
  - Trees sink 0.1 m. `Flat_v0` guarantees z = L·TH exactly for building-attached props.
- **Existing `make_pond`** stays a prop for small puddles. Real water uses the shore set.

---

## 12. Polycount budget (LOD0 / LOD1 triangles)

| Piece | LOD0 | LOD1 | Notes |
|---|---|---|---|
| Flat | 72 | 72 (merged-chunk simplification) | 6×6 grid, 0.5 m |
| Cliff_Edge | ≤ 800 | ≤ 450 | band 12×16 quads = 384, regions ~60, rubble 3×80, cards 8×4 |
| Cliff_Corner / Inner | ≤ 650 | ≤ 380 | |
| Cliff_SaddleA / B / Stair3 | ≤ 1000 | ≤ 550 | 2 contours |
| Cliff_Steps | ≤ 1000 | ≤ 600 | |
| Shore_Edge | ≤ 400 | ≤ 250 | band 12×10 quads, foam 24, water 2 |
| Shore_Corner / Inner | ≤ 350 | ≤ 220 | |
| Shore_Saddles | ≤ 600 | ≤ 350 | |
| Water_Bed | 8 | 8 | edge step 1.5 m |
| Water_Plane | 2 | 2 | |

**Example map:** 64×64 tiles (192 m) with 70% flat, 18% cliff, 7% shore, 5% water comes to about **0.82 M triangles at LOD0**. With LOD1 beyond 40 m and a typical colony-sim view, roughly 0.25 M are visible.

**Unity chunking:** 8×8-tile chunks, `CombineMeshes` per material (Ground, Cliff, Leaves, RockMossy, Foam, Water: at most 6 draw calls per chunk). Rebuild only the chunks touched by a corner edit (a corner touches at most 4 tiles).

---

## 13. Build order

**Phase 1: grass and cliff height set** (the MVP colony-sim terrain)
- `vk_terrain.py`: constants `TT=CELL`, `TH=H1`, `BAND=0.6`, `ZW=-0.25`, `ZB=-1.05`, `EDGE_STEP=0.5`; `edge_profile()`, `contour()`, `sweep()`, `fill_regions()`, `snap_boundary()`, `tk_finish()`, `build_case(shape, variant, lod)`, `resolve()`, `vhash()`.
- 22 meshes: `SM_VK_Terr_Flat_v0..3`, `SM_VK_Terr_Cliff_{Edge v0..3, Corner v0..2, Inner v0..2, SaddleA v0..1, SaddleB v0..1, Stair3 v0..1, Steps v0..1}`.
- `gen_grass`, `gen_cliff`, T_VK_TerrainMacro, the ground material (grass-only path), the cliff material.
- Tests T1–T4 passing.
- A demo map (`build_terrain(coll, H, W, SURF, origin=(1000,0), merge_chunks=True)`) that re-lays part of the town with a 2-tier chapel plateau and a terrace street with Steps.

**Phase 2: water, shore and surfaces**
- 12 meshes: `SM_VK_Terr_Shore_{Edge v0..2, Corner v0..1, Inner v0..1, SaddleA v0, SaddleB v0}`, `SM_VK_Terr_Water_Bed_v0..1`, `SM_VK_Terr_Water_Plane`.
- Foam, `gen_sand`, `gen_dirt`.
- The corner-data texture and splat shader (dirt, soil, sand, forest floor).
- Door-yard auto-paint and socket scatter.

**Phase 3:** half-level ramps, hillside houses plus retaining walls, cobble plaza texture, CliffWater, waterfalls, bridges, lip fences, beach/bank styles.

---

## 14. Automated seam verification (Blender)

**T1 `edge_signature_test()`** (per mesh and per rotation; this is the primary test)
- For each variant mesh and each of the 4 rotations, collect vertices with |x| or |y| within 1e-5 of 1.5.
- Convert each to edge-local (t, z).
- Compare with `edge_profile(kind)` built from the corner values that rotation implies:
  - position within 1e-4 m;
  - normal (`me.corner_normals`, averaged per vertex) within 0.5°;
  - Col within 1/255;
  - material index of the adjacent faces;
  - sharp flags.
- Cost is O(meshes), so run it after every regeneration.

**T2 `coverage_test()`**
- Enumerate all level quadruples in {0,1,2}⁴ that satisfy R1, and all 16 water masks.
- `resolve()` must return an existing mesh.
- The rotated mesh's four edge kinds must equal the edge kinds of the quadruple.

**T3 `random_grid_test(seed, N=24)`** (20 seeds)
1. Levels: `floor(clip(fbm*2.2 + 1, 0, 3))`, then R1 relaxation. Lakes where `H==0 & noise < −0.4`, then W1. Flags: 10% steps, 50% bridge.
2. Instantiate numerically: `foreach_get` vertex arrays, rotate, translate to `(3i+1.5, 3j+1.5, b*TH)`. No objects needed.
3. Append all tiles to one bmesh (excluding loose parts with material LEAVES, FOAM or RockMossy) and run `bmesh.ops.remove_doubles(dist=1e-4)`.
4. Assert:
   - open boundary edges lie only on the map border (count 0 inside);
   - no edge has more than 2 faces;
   - the maximum normal deviation between the two tiles at each merged seam vertex is below 0.5°.
5. On failure, report `(i, j, side, case, rot, variant, max_dev)`.

**T4 visual.** Render a "seam debug" material: world grid lines every 3 m in red, base colour = hash(variant), plus a lit Eevee pass. Use a "rotation torture" map where every mask appears with every variant and every neighbour combination. Take one top view and one 3/4 view.

**T5 fuzz.** 10k random corner edits on the map. After R1/W1 enforcement, `resolve()` must never fail and T3 must still pass.

**Unity mirror.** Port T1 and T3 as EditMode tests.
- FBX import: Mesh Compression **Off** (quantisation cracks seams), Normals: **Import**, Tangents: Calculate (MikkTSpace), Bake Axis Conversion **On**, scale 1.
- Keep the map origin near (0,0,0).

---

## 15. Open questions (none block Phase 1)

1. **TH = 3.0 vs 1.5.** 3.0 is recommended for WC3 chunkiness and split-level houses. Everything scales from one constant, but the texture strata and the profile z values would need re-tuning for 1.5.
2. **Saddle defaults** (knobs for cliffs, water-connected for shores). Gameplay might prefer data-driven choices; `saddleBridge` already allows that.
3. **Steps at 45°.** Is that acceptable for villager traversal until Phase 3 ramps?