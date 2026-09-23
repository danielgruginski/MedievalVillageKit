Now the material code and the images.

# Stone texture rework (T_VK_Stone): critique and procedural recipe

## 0. Summary
- The current rubble has five main problems. The stones look like soap bars. The surface looks like sponge. The mortar is nearly black and covers 20% of the tile. The colours form a beige and grey patchwork. The painted light has no direction.
- Replace it with **course-seeded anisotropic power-Voronoi stones**. Each stone gets its exact distance to its edge, faceted faces made of flat planes, a quarter-circle bevel and top-lit hue-shifted painted light. The mortar becomes a lighter recessed fill with contact shadows.
- Keep **tile = 3.0 m**. It equals CELL and H1, so neighbouring modules join without a seam.
- Make two new variants. **T_VK_StoneBlock** is a jointless face for modelled blocks (this is required). **T_VK_FieldStone** is a parameter preset for rural buildings. Only re-shade Ashlar.

---

## 1. What is wrong now (measured and observed)

Measured from T_VK_Stone_BC.png (every 4th pixel):
- Pixels with luminance < 0.25 (mortar): **19.6%**
- Mortar mean: sRGB (0.176, 0.149, 0.122), **#2D261F**, almost black
- Stone mean: (0.555, 0.512, 0.446), #8E8372
- Tile mean: (0.48, 0.44, 0.38), #7A7061
- Stone to mortar ratio: about 3.4:1 in sRGB and about 15:1 in linear

| Area | Problem (with the cause in `gen_stone`) |
|---|---|
| **Shapes** | Every stone is an axis-aligned rounded rectangle with the same 40 px (11.7 cm) corner radius. The result is soap bars or bread loaves. The 6 row bands run straight across the whole tile and head joints are exactly vertical, so it reads like a brick grid. `split` (35%) cuts a slot into two half-height slabs of *identical length*, which gives a "hot-dog pair" motif you can recognise at a glance. |
| **Silhouette** | The edge noise `fbm(fmin=4,fmax=60)*4.5` px nibbles every edge evenly, like torn paper or a cookie cutter. Real chips are occasional, angular bites. |
| **Surface** | `facets()` is `-abs(fbm)`, which makes a web of thin *ridges*. In the _H map these show as bright worm lines, like brain coral or foam. Their amplitude (0.10+0.04) beats the form: the dome falloff is only 15–22%. There are no flat faces anywhere. |
| **Mortar** | Joints are 13–30 px (4–9 cm) wide and flat (0.09 ± 0.02). Colour 0.26/0.22/0.18 multiplied by `cavity_ao` (floor 0.25, ao_in_albedo 0.55) comes out near black, so joints read as holes. At game distance the mips average the dark joints in and the wall goes muddy. The vertex grime (0.62 at the base) makes it worse. |
| **Colour** | 4 sand colours and 3 neutral greys are picked uniformly, giving about 57/43 camouflage. Beige saturation is about 0.28 against 0.10 for grey, so the beige stones pop like sponge cake. Each stone is one flat colour with no light-to-shadow gradient. The green lichen specks read as mould. |
| **Lighting** | `painted_light` runs on `blur(h,2.5)` and lights the *wrinkles*, not the stone form. `rim` adds +0.06 all the way round, a non-directional halo that looks like a sticker outline. L = (-0.35, 0.75, 0.55) has a side component, which is wrong for a texture used on walls facing all four directions and on the octagonal windmill. |
| **At game distance** | A 3 m wall is 30–60 px on screen. About 40 stones become 5–10 px each, and the beige/grey patchwork turns into salt-and-pepper noise. This is visible on the windmill and guard tower in village_special_buildings.png. |
| **Kit side (makes the texture look worse)** | (a) `Kit.box()` gives every box a hashed UV offset. `stone_panel` pieces around windows and doors, and the 7 cm strips from `arch_cut_panels`, therefore show pattern **discontinuities** at each sub-panel seam. (b) The 3 m rubble is mapped onto *modelled* blocks (door jamb blocks, voussoirs, windmill quoins, sills, steps, well ring), so mortar lines cut through single blocks. (c) The `rock()` pop-outs (`wall_rocks` n=6 per wall, plinth rocks, corner quoins, lintels) use T_VK_Rock, which has a different palette and noise and is placed randomly against the painted courses. Together this gives "stones on stones". |

---

## 2. Target look (rules the algorithm must follow)
1. **Shapes first:** chunky, angular convex polygons (4–7 sides) with mostly flat bed joints (≤ 14°) and head joints leaning up to about 20°. Include a clear size hierarchy: normal stones, a few tall "jumpers" and small pinning stones ("snecks").
2. **Three values per stone:** a bright top bevel (about 0.72 sRGB), a mid face (0.55–0.62) and a dark lower bevel with the mortar (0.25–0.40). Faces are split into 2–3 flat facets, each lit differently by ±8%.
3. **Hue shift:** highlights warm, shadows cool. Light comes **from the top** only.
4. **Detail only at edges:** occasional chips, 1 crack per about 5 stones, moss on ledges. Fine-grain noise stays at ±2% or less.
5. **Mortar is a mid-dark warm grey**, 10–13% of the area, recessed, and shadowed under each stone.

---

## 3. Algorithm (numpy, tileable, uses the vk_tex helpers)

### 3.0 Constants
- `S_out=1024`. Generate at `SS=2` (S=2048) and box-downsample at the end. All **pixel-valued** parameters (blur sigmas, cavity radii, crack steps) double at SS. fbm frequencies are in cycles per tile and do not change.
- `tile=3.0`, `depth=0.06` m, `m2px=S/tile` (682.7 at SS). All distances below are in metres.

### 3.1 New helper `pvoronoi()` (add to vk_tex.py, about 30 lines)
The current `voronoi()` returns unsigned distances and no second ID, so it cannot give an exact distance to the edge. The new helper is a power diagram that tracks the 3 nearest seeds and wraps signed deltas.
```
for i,(px,py): dx=x-px; dx-=np.round(dx); dx*=sx     # signed toroidal delta
               dy=y-py; dy-=np.round(dy); dy*=sy
               P=dx*dx+dy*dy-w[i]                     # power distance
               insert (P,dx,dy,i) into sorted top-3 via np.where cascades
def border(a,b):                                       # distance to the a|b bisector
    ex,ey=a.dx-b.dx, a.dy-b.dy; L=hypot(ex,ey)+1e-9
    e=(b.P-a.P)/(2L)                                   # in scaled space
    return e/hypot(ex/L*sx, ey/L*sy)                   # undo anisotropy -> real UV
edge = softmin(border(1,2), border(1,3), k=0.01m)      # exact, corners ~1 cm rounded
return I1, I2, edge*tile (m), (d1x/sx, d1y/sy)*tile (m, local offset from seed)
```
- softmin is `-k*log(exp(-a/k)+exp(-b/k))`.
- Speed: with about 45 seeds at 2048², expect 10–20 s. It is about 3× faster if you only evaluate seeds from courses c-1..c+1 inside each course band.

### 3.2 Course and seed layout (all in metres, then /tile to UV)
1. **Courses:** 7 heights `H=U(0.30,0.56)`, rescaled so the sum is exactly 3.0. y grows downward, matching the array rows and the world down direction.
2. **Stone lengths per course:**
   - 70% `U(0.50,0.95)`, 20% `U(0.95,1.25)`, 10% `U(0.28,0.45)`.
   - Draw until the sum is at least 3.0, then rescale to exactly 3.0.
   - Random course phase `U(0,3)`. The seed goes at the centre of each length.
   - Vertical jitter is `±0.10·H_c`.
3. **Break the joints:** if any head joint lies within 0.12 m of a head joint in the course below (check wrap-around, so course 6 against course 0), shift that course's phase by +0.15 m and retry, up to 10 times.
4. **Anisotropy:** `sx=1.0, sy=1.8`. Bed-joint slope is at most δ/(sy²·H), which is about 14°. Head-joint lean is about sy²·jitter/L, which is about 20°.
5. **Power weights:** `w_i = κ·(L_i/2/tile)²` with **κ=0.5**. The partial weight keeps joints near their intended positions. With κ=1, long stones bulge more than 6 cm into the courses above and below. κ=0 (plain Voronoi) is an acceptable fallback.
6. **Jumpers:** 3 per tile, on different course boundaries and at least 0.8 m apart.
   - Remove the nearest seed in each of the two courses.
   - Add a seed on the boundary line with L_eff = 0.8 m.
   - Check that the cell height is at least 1.4× the mean course height; if not, multiply w by 1.5.
7. **Snecks:** at about 25% of the points where a head joint meets a bed joint (about 8 per tile), add a seed with `w=U(-0.003,-0.001)` UV². The result is 8–15 cm pinning stones. Drop any whose cell is smaller than 60 cm².
8. **Validation:** every non-sneck cell must be at least 0.2× its expected area. Otherwise lower κ or remove the seed. The target is about 42 cells in total.
9. **Domain warp before `pvoronoi`:**
   - `X=(x+0.0045*fbm(S,3.2,seed+1,fmin=2,fmax=16))%1`
   - `Y=(y+0.0035*fbm(S,3.2,seed+2,fmin=2,fmax=16))%1`
   - This gives about 1.3 cm σ of gentle bowing with no nibbling.

### 3.3 Stone height (gather per-stone arrays through I1)
Local coordinates: `lu,lv` = d1 in metres. `R_i=0.5·min(L_i,H_i)`.
- **Protrusion** `b0`: `U(0.56,0.70)`. Jumpers 0.68. Snecks `U(0.48,0.54)`, slightly recessed.
- **Tilt:** `(tx,ty)=U(-0.12,0.12)` height units per metre, applied as `tx·lu+ty·lv`.
- **Facets** (this replaces `facets()`). For K=3 planes plus a flat top:
  - `θ_k=θ0+2πk/3+U(-0.4,0.4)`, `r_k=U(0.30,0.60)·R_i`, `s_k=U(0.6,1.2)`/m. On 30% of stones set `s_0=1.6`, for a face split by a single ridge.
  - `face = b0 + tilt − max_k( s_k·relu(lu·cosθ_k + lv·sinθ_k − r_k) )`
  - This is the min of the planes: a flat top with chamfer facets and crisp ridges.
- **Edge profile:**
  - Joint half-width `g = clip(0.008 + 0.006·fbm(S,2.0,seed+21,fmin=3,fmax=30), 0.004, 0.02)` m.
  - Chips: `chip = 0.025·smooth(1.0,1.9,fbm(S,2.3,seed+20,fmin=10,fmax=80))`. This covers about 12% of the edge length.
  - `e_eff = edge − chip`
  - `t = clip((e_eff − g)/0.045, 0, 1)`, a 4.5 cm bevel.
  - `shoulder = sqrt(1 − (1−t)²)`, a quarter circle.
  - `h_st = face − 0.45·(1−shoulder)`. At the border this falls below mortar level, so the mortar line comes out naturally, about 2.5 cm on average and wider at corners and around low stones.
- **Detail** (small amounts only):
  - `+0.012·fbm(S,2.8,seed+13,fmin=6,fmax=48,ax=1.8)` for horizontal "strokes"
  - `−0.03·smooth(1.9,2.3,fbm(S,2.0,seed+14,fmin=40,fmax=200))` for sparse pits, about 1.5% coverage
  - `−0.04·chipzone`, where `chipzone = smooth(0.2,0.6,chip/0.025)·(1−smooth(g,g+0.05,edge))`
  - **No grain above 0.004.**

### 3.4 Mortar and combine
- `mortar_h = 0.24 + 0.025·fbm(S,2.0,seed+6,fmin=12,fmax=160) + 0.008·fbm(S,1.2,seed+16,fmin=150)`
- `h = smax(h_st, mortar_h, k=0.015)` with `smax(a,b,k) = (a+b+sqrt((a−b)²+k²))/2`
- `stone = smooth(−0.012, 0.012, h_st − mortar_h)` is the anti-aliased colour mask.

### 3.5 Cracks
- `crack_segments(S, rng, n=6, steps=(5,12), step_px=(0.015,0.03)·m2px, w0=0.0035·m2px, branch=0.15, jit=0.5)` then `draw_segments(wrap=True)`.
- Mask with `stone · smooth(g, g+0.015, edge) · gate[I1]`, where `gate = rng.random(N) < 0.2`. Cracks then stop at the joints and appear on about 1 in 5 stones.
- Height: `−0.10·crack`.

### 3.6 Moss and lichen masks (restrained on the town stone)
- `k1 = 0.015·m2px`
- `ledge = (1−stone)·np.roll(stone, −k1, 0)` marks mortar directly above the top of a stone.
- `patch = smooth(0.8,1.6,fbm(S,3.0,seed+30,fmin=2,fmax=24))`
- `clump = smooth(−0.2,0.6,fbm(S,1.8,seed+31,fmin=40,fmax=200))`
- `moss = patch · clump · max(ledge, 0.6·rimTop)`, where rimTop comes from 3.8. **Target coverage: 3%.** Height `+0.035·moss`.
- `lich = smooth(1.9,2.3,fbm(S,2.2,seed+9,fmin=18,fmax=110)) · stone · smooth(0.3,0.6,shoulder)`. Target coverage about 1.5%. `lich_rim = smooth(1.75,1.9,…) − lich`.

### 3.7 Final height and normal
- Build `h` from 3.3 to 3.6, then `h = clip(blur(h, 1.2px@SS), 0, 1)`.
- Compute the normal from the **same final h**, after moss and cracks, so highlights do not float.
- `write_set` runs `normal_from_height(h, 0.06, 3.0)` itself. Pass it the downsampled h.
- Check: maximum tilt about 60° on bevels, and mean normal xy ≈ 0.

### 3.8 Colour (all values sRGB, written straight into the _BC pixels)

**Stone families (weights):**

| Family | Weight | sRGB | Hex |
|---|---|---|---|
| Warm grey | 40% | (0.604, 0.580, 0.537) | #9A9489 |
| Cool blue-grey | 22% | (0.545, 0.565, 0.588) | #8B9096 |
| Pale limestone | 15% | (0.702, 0.671, 0.604) | #B3AB9A |
| Ochre sandstone | 13% | (0.690, 0.600, 0.459) | #B09975 |
| Dark slate | 10% | (0.431, 0.427, 0.435) | #6E6D6F |

**Per-stone variation:**
- Value `×U(0.93,1.06)`.
- Temperature `t~N(0,1)·0.012` applied as (+t, 0, −t).
- **Neighbour-aware assignment:** build adjacency from the unique (I1, I2) pairs where `edge < 0.01`. Colour stones in random order, and never put ochre next to ochre, limestone next to limestone, or slate next to slate.
- Reject any stone more than 1.8σ from the mean luminance, so no stone stands out when the pattern repeats.

**Layers, in this order:**
1. `col = base[I1]·(1+0.04·fbm(S,3.0,seed+7,fmin=3,fmax=24))·(1 − 0.07·clip(lv/R,−1,1))`. The second factor lightens the top of each stone.
2. Painted light:
   - `n_p = normal_from_height(blur(h,3px@SS), depth·4, tile)`
   - `light = painted_light(n_p, L=(−0.20, 0.80, 0.56))`. A flat surface gives 0.56.
   - `col *= 1 + 0.45·(light − 0.56)`. Result: top bevel about ×1.18, facets ±8%, lower bevel about ×0.75.
3. Hue shift:
   - `hi = clip((light−0.56)/0.44, 0, 1)`, `lo = clip((0.56−light)/0.56, 0, 1)`
   - `col *= (1 + hi·(0.06, 0.03, −0.05)) · (1 + lo·(−0.06, −0.03, 0.06))`
4. Directional rims (these replace the uniform `rim`):
   - `band = smooth(0,0.25,t)·(1−smooth(0.55,0.9,t))`
   - `rimTop = band·smooth(0.3,0.7,n_p.y)`, then `col += 0.09·rimTop·(1.0, 0.96, 0.86)`
   - `rimBot = band·smooth(0.3,0.7,−n_p.y)`, then `col *= 1 − 0.15·rimBot`
5. Chips `×(1+0.06·chipzone)` (fresh stone is lighter). Cracks `×(1−0.45·crack)`, plus a lit lower lip `+0.08·np.roll(crack, +2px, 0)·(1−crack)`.
6. Lichen: mix 0.6 toward (0.74, 0.72, 0.55) #BDB88C, and multiply the rim by 0.93.
7. **Mortar:** base (0.380, 0.345, 0.300) #61584D, multiplied by `(1+0.05·fbm(fmin=150))`. Composite with `stone`.
8. **Contact shadow** (strong 3D read at distance):
   - `cs_k = clip((np.roll(h, k, 0) − h − 0.04)/0.15, 0, 1)` with k = 0.012 m in px
   - `cs = max(cs_k, 0.6·cs_2k)`, then `col *= 1 − 0.28·cs`
9. **Moss:** `ramp3(moss_h, (0.20,0.30,0.10) #334D1A, (0.33,0.45,0.14), (0.47,0.58,0.20) #789433)` mixed in by `moss`.
10. **AO:** `ao = cavity_ao(h, radii=(4,12,32)@SS, k=(2.0,1.5,0.9), floor=0.45)`, then `write_set(..., ao=ao, ao_in_albedo=0.40)`. Mortar ends up at about #463F37 and about #2F2A25 at its deepest.

**Expected averages:** stone ≈ (0.57, 0.55, 0.51), tile ≈ **(0.54, 0.52, 0.48) #8A857A**. That is lighter and less yellow than now and sits clearly below the plaster (0.93, 0.85, 0.67).

### 3.9 Roughness
- Stone: `0.78 + 0.05·fbm(S,2.4,seed+11,fmin=6) − 0.06·rimTop` (worn top edges are slightly smoother).
- Mortar 0.93, moss 0.96, lichen 0.88, cracks 0.95.
- For Unity, smoothness = 1 − R, packed into the URP Lit metallic alpha.

### 3.10 Output
- Downsample BC, h, R and AO with `a.reshape(1024,2,1024,2,…).mean((1,3))`, then call `write_set("T_VK_Stone", …, depth=0.06, tile=3.0)`.
- Set `PBR_SETS["T_VK_Stone"]=dict(depth=0.06, tile=3.0, stones=[...])` (the metadata is described in §5.4).
- Set `MAT_MAP["M_VK_Stone"]` to nstr **1.0**, down from 1.1, because the new relief is stronger.

---

## 4. Tuning knobs (default values)
| Knob | Default | Effect |
|---|---|---|
| courses | 7 | Stone scale at game distance. Use 8 for a finer look. |
| sy | 1.8 | Flatness of the bed joints (1.4 = more polygonal, 2.2 = more coursed) |
| κ | 0.5 | Stone size contrast against course regularity |
| g | 0.008 m | Mortar coverage. **Target 10–13%.** |
| bevel / drop | 0.045 m / 0.45 | Softness of the edges |
| facet slope | 0.6–1.2 /m | How chiselled the faces look |
| painted-light gain | 0.45 | Keep at 0.5 or below to avoid double lighting with the normal map |

---

## 5. Variants

### 5.1 T_VK_StoneBlock (jointless dressed face). Required.
- **Use:** every modelled block (quoins, voussoirs, sills, lintels, steps, thresholds, caps, well ring, plinth rocks, pop-outs).
- **Recipe:**
  - Tile 1.5 m, depth 0.03.
  - `pvoronoi` on a 4×4 jittered grid (jitter 0.35 of a cell, sx = sy = 1). Each cell is a facet with one plane: slope `U(0.15,0.45)`/m, offset ±0.03 around 0.6.
  - Soften the step creases with `blur(3px@SS)`, plus a thin chisel groove `−0.03·(1−smooth(0,0.01,edge))`.
  - Broad value fbm (fmin 1.5, fmax 10) ±5%, strokes ±2%, 2 cracks, 1.5% lichen, no moss.
  - Warm grey family only, (0.62, 0.595, 0.55) #9E9887, ±4% per cell.
  - Same top-lit painted light and hue shift, but **no bevel or dome**, because the geometry bevels already supply the edges.
  - Roughness 0.76.
- **Integration:**
  - Append `STONE_BLOCK` as index 45 at the **end** of `kit_mats()` so existing indices do not change. Set `TILE[45]=1.5`.
  - In `Kit.box()`: `if mi==STONE and bevel>0 and sorted(size)[1]<0.7: mi=STONE_BLOCK`. This keeps chimneys, the tower plinth and the oven as rubble and converts quoins, sills and steps.
  - Call `rock(..., mi=STONE_BLOCK)` in `plinth`, `corner_stone`, `wall_rocks`, the lintels, the chimney caps and `arch_ring`. T_VK_Rock stays on natural boulders only.
  - Optional: `finish()` overwrites `Col`. If it multiplied instead, a per-block tint of ×U(0.88, 1.06) could be written in `box()`.

### 5.2 T_VK_FieldStone (rough rural stone). Worth making because it is only a parameter preset.
- **Use:** barn, stable, farm walls, well, graveyard wall. In a colony sim it also shows building tier: field stone for poor buildings, rubble for town houses, ashlar for civic buildings.
- **Differences from the rubble:**
  - No courses: toroidal Poisson-disk seeds (about 48, minimum distance 0.30 m) with sy = 1.25.
  - Lengths 0.30–0.80 m.
  - `g=0.016±0.008`.
  - Bevel 0.075 m using a cosine dome instead of the quarter circle, so stones are pillowier.
  - Facet slopes halved.
  - Dry-stone joints: `mortar_h=0.10`, colour (0.22, 0.20, 0.17).
  - Palette: ochre raised to 25%, and a brown family (0.52, 0.46, 0.38) added.
  - Moss 10%, lichen 4%, depth 0.08.

### 5.3 Cut stone
- T_VK_Ashlar already covers this. Keep its block layout and only re-shade it with §3.8 steps 2–4 and 8, and a lighter mortar (0.45, 0.41, 0.36). That gives one consistent lighting language across all stone. This is low priority.
- For the terrain track: the same generator with sy = 1, 0.18–0.30 m seeds, a 0.03 m bevel and no facets produces cobbles for the path tiles.

### 5.4 Stone metadata for aligned pop-outs (optional)
- Export `stones=[(u, v, w_m, h_m)]` for cells larger than 0.25 m². Use `v = 1 − row/S`, because `write_map` flips the rows.
- With the UV offset at 0 on a −Y-facing module: `x = −3u` wrapped into [−1.5, 1.5), and `z = 3v`.
- `wall_rocks` can then extrude 2–4 real painted stones per module, at `(0.9w, 0.06–0.10, 0.9h)` with StoneBlock, instead of random boxes.

---

## 6. Pitfalls
1. **Tiling:**
   - Use only `fbm` (FFT-periodic), wrapped signed deltas (`d-=round(d)`), `np.roll`, `warp()` and `draw_segments(wrap=True)`.
   - Do not use `np.gradient`, or scipy filters with a reflect boundary.
   - Course heights and per-course lengths must sum **exactly** to 3.0.
2. **UV offsets in Kit.box():**
   - Add a `uv_offset` parameter, and have `stone_panel`, `arch_cut_panels` and the `wall_stone_*` plinth band pass (0, 0).
   - Because TILE[STONE] = 3.0 = CELL and modules span x ∈ [−1.5, 1.5], the pattern then runs continuously across sub-panels *and* neighbouring modules.
   - Keep random offsets only for individual blocks.
3. **Light direction:**
   - The painted light must be top-lit (x component 0.2 or less), because the texture is used on every facade direction.
   - Keep the painted gain at 0.45 or below, with nstr 1.0, to avoid double shading.
4. **No vertical gradients in the texture:** it repeats every 3 m on chimneys, the 8.5 m windmill and the tower, so any gradient would show as bands. Ground grime stays in the `finish()` vertex colour.
5. **Mip darkening:** thin, mid-dark joints keep distant walls from going muddy.
   - Check that the 1/32 downsample mean is within 0.02 of the full-res mean.
   - Consider the Kaiser mip filter in Unity.
6. **Power weights:** check cell areas after `pvoronoi`. Weights that are too large delete cells or merge courses.
7. **Aliasing:** the min-of-planes ridges and the bevel have kinks. Supersample at 2× and blur 1.2 px before computing normals.
8. **sRGB:** the hex values above are the values written into the BC pixels. In Unity:
   - BC: sRGB.
   - N: normal map. It is already OpenGL Y+, which matches Unity, so no green flip.
   - R: import as linear and invert into smoothness.
   - H: only if you use parallax, at a strength of 0.02 or less.

## 7. Acceptance checks
| Check | Target |
|---|---|
| Mortar mask coverage | 10–13% |
| Tile mean BC | (0.54, 0.52, 0.48) ± 0.03 |
| Mortar mean | 0.26–0.30 |
| Per-stone luminance σ | 0.045–0.06 |
| 32×32 downsample | Shows about 7 soft courses, with low-frequency luminance σ of 0.03–0.05 and no speckle |
| Tiling | `np.roll(bc, (S//2, S//2))` shows no seams |
| Repetition | 4 modules side by side: no stone draws the eye |
| Close-up (town_detail camera) | Facets, top highlights and lower shadows are readable, with no sponge texture |

Files read: `C:/Users/danie/AppData/Roaming/Claude/scratch-workspaces/ec03f06b-60f5-4d5d-94a9-dff3a56c5f56/f8ddc2b6-f8a4-41c6-98db-14b97d4348ea/scratch-2026-09-23-d49817/code/`
- `vk_texgen.py`: `gen_stone` at L5–54, `gen_ashlar`, `gen_rock`
- `vk_tex.py`
- `vk_mat.py`
- `vk_helpers.py`: `Kit.project`/`box` at L79–118, `stone_panel`/`plinth` at L164–168, `rock`/`plinth`/`wall_rocks`/`corner_stone` at L1695–1747, `chimney` at L1818, `arch_cut_panels` at L1838, `windmill` at L1501