# Stone texture rework: verdict and final spec

## 0. Verdict

**Proposal 1 wins and is the base of this spec.** It uses a course partition with function-defined joints, a lacing course, packer stones, a top-rim, underside and cast-shadow paint stack, a distance analysis, and an exact bisector helper. From Proposal 2 this spec takes:
- the concrete `STONE_BLOCK` slot and the automatic reassignment in `box()`;
- moving the `rock()` pop-outs to one stone family;
- the ledge-moss mask;
- the maths that undoes anisotropy in the power diagram;
- exporting stone metadata so pop-out stones line up with painted ones;
- the rule against vertical gradients;
- mapping stone types to building tiers;
- the mip-mean test.

I checked every claim against the code (`vk_texgen.py` L5–54, `vk_tex.py`, `vk_helpers.py` L79–148, L164–235, L1500–1525, L1695–1860, `vk_mat.py` MAT_MAP) and against `T_VK_Stone_BC.png`, `town_detail.png` and `catalog_walls.png`. Both proposals measured the current texture correctly: about 20 % of the tile is mortar, and the mortar averages #2D261F to #2E2720. That matches the code: 0.26 × (0.45 + 0.55 × 0.25) ≈ 0.15.

---

## 1. Scores

For Risk, 10 means lowest risk.

| | Concreteness | Correctness / feasibility | Fit to the WoW colony-sim kit | Risk | **Total** |
|---|---|---|---|---|---|
| **P1** | 9 | 7 | 9 | 7 | **32/40** |
| **P2** | 8 | 7 | 8 | 5 | **28/40** |

- **P1:** the layout is deterministic and easy to control, and the paint stack is the strongest "painted" read. The distance maths is correct. It has a few wrong mechanisms and one sign error (§2).
- **P2:** its kit integration is excellent. The power-Voronoi rubble, however, needs a tuning loop (κ, weights, jumpers, validation). Its edge distance is not exact, and its crack gating does not produce the density it promises.

---

## 2. Claims that are wrong or inaccurate

| # | Source | Claim | Reality / fix |
|---|---|---|---|
| 1 | P1 | `smooth(...)**0.5` "has infinite slope at the edge" | False. Near t = 0, smoothstep ≈ 3t², so √ ≈ 1.73t, which is a finite slope. The 2–3 px cliff ring comes from `mask=smooth(gap,gap+2,d)`, which jumps from `mortar_h` 0.09 to `stone_h` ≥ 0.36 in 2 px (≈1.35 cm up over 0.6 cm, about 65°). **Fix:** the bevel must run continuously from mortar level to the face (§5.5). A mask must not blend two heights. |
| 2 | P1 and P2 | The quarter-circle bevel `√(1−(1−s)²)` is "no cliff" | It has a **vertical tangent** at s = 0. **Use `prof = 1−(1−s)²`** instead: slope 2× at the edge (about 50–55° with our numbers) and 0 at the crest. |
| 3 | P1 | Cast-shadow march `roll(h,(k, round(−0.15k)))` | Wrong x sign. With L.x = −0.12 the light comes from −u, so the occluder is up-**left**: `np.roll(h,(k, +round(0.15k)),(0,1))`. As written, the shadows slant against the painted light. |
| 4 | P1 | Flat-face light response = 0.587 | Actually `Ln.z` = 0.583. Compute it in code; do not hard-code it. |
| 5 | P1 | Offset (0,0) for STONE and ASHLAR "makes every module seam continuous", applied to "boxes ≥ 1.5 m" | (a) Wrong for Ashlar at `TILE[ASHLAR]=2.5`: at x = ±1.5, u = ±0.6, a 0.2-tile mismatch. It only holds after re-tiling Ashlar to 3.0 (§6.3). (b) The ≥ 1.5 m filter misses window sub-panels (1.1 m) and the 7 cm `arch_cut_panels` strips, so those seams stay broken. Use the `bevel==0` rule (§7). |
| 6 | P1 | "Hide corners with modelled quoins" (presented as new) | Quoins already exist: `corner_stone()` L1738, alternating 1.05/0.62 m `rock()` blocks, and the windmill L1519. Only their material needs to change. |
| 7 | P1 | Per-building stone tint through "the existing vertex colour `Col`" | `Col` is not free. `finish()` overwrites it with grime (L138–140), and `mossy_material` gates on its alpha. Use `VARIANT_MATS` tints instead (§6.5). |
| 8 | P1 | `crack_segments` "with a custom start point" | The helper has no such parameter. Add `starts=` (§4). |
| 9 | P1 / P2 | "Voussoirs" use the 3 m rubble | Only partly true. The door voussoirs and jambs of the `wall_stone_door` base (L208/211) use STONE. `arch_ring` (L1830) defaults to **ROCK**, and so do `rock()` pop-outs, plinth rocks, quoins, the lintel, the current `chimney()` caps (L1818) and the impost (L1858). The real STONE-on-a-single-block cases are: sills L184, L208/211, thresholds and steps L221–222/1527/1589, the well ring and cap L893/896, tower quoins L1576, jambs and lintel L1586–1587, and slabs L1146/L1451. |
| 10 | P2 | `n=6` random cracks, gated `rng.random(N)<0.2` per stone, gives "1 in 5 stones cracked" | This gives about 1–2 surviving cracks per tile, not about 8. Seed the cracks **on edges of chosen stones** (§5.5). |
| 11 | P2 | `softmin(border(1,2),border(1,3))` described as an "exact" edge distance | It is only exact when the nearest bisector belongs to the 2nd or 3rd-nearest seed by power distance. With sy = 1.8 and power weights this fails near the corners of long cells. The exact method is the minimum over all seeds (P1's formula). Bisectors that are not edges lie outside the convex cell, so they never lower the minimum. |
| 12 | P2 | The `box()` rule `sorted(size)[1]<0.7` catches the modelled blocks | It misses thin slabs: the L1146 oven slab (1.5 × 0.8 × 0.12) and the L1451 step (… × 0.1). Add `or min(size)<0.25`. The swap must also happen **before** `box()` assigns `material_index`. |
| 13 | P2 | Facet slopes of 0.6–1.2 h01/m read as "chiselled" | That is 2–4° of real tilt, so the engine normal barely shows planes. The chiselled look comes only from the ×4 painted exaggeration. Use 5–9° (§5.5). |
| 14 | P1 | Mossy variant with a baked `(1−yu/T)^1.5` gradient | Conflicts with P2's (correct) pitfall. The texture repeats vertically on chimneys, the 8.5 m windmill and the tower, so a baked gradient bands. No vertical gradients in any stone texture. |

---

## 3. Contradictions resolved

| Topic | P1 | P2 | **Decision** |
|---|---|---|---|
| Rubble layout | Course partition | Course-seeded anisotropic power Voronoi | **Partition.** Straight, controllable joints, exact distances per term, no tuning loop. Power Voronoi is kept for StoneBlock and FieldStone. |
| Courses | 6 + lacing course | 7 | **6 + 1 lacing course** (`lacing=True` flag) |
| Jumpers | Optional | 3 per tile | **None in v1.** They fight the stagger rule and add risk. Revisit in v1.1. |
| Bevel | Quarter circle | Quarter circle | **Parabolic, spanning mortar to face** (§5.5) |
| Facet slope | 6–11° | 2–4° | **5–9°** (0.08–0.15 m/m) |
| Edge distance helper | Exact, all seeds | Top-3 softmin | **Exact, all seeds**, with P2's anisotropy undo |
| Normal map | Compute at 2k, average | From the downsampled h through `write_set` | **P2.** Keep `write_set` unchanged. |
| Painted light | Posterise + HI/SH tints | Gain + hue multipliers | **P1**, with the posterise blend lowered to 0.35 |
| Contact shadow | Height-field march | 2-tap | **P1 march** with the sign fix |
| Moss on town stone | None | 3 % ledge moss | **About 2 % ledge moss** (P2 mask, P1 colours) |
| AO in albedo | 0.30 | 0.40 | **0.30**, floor 0.40 |
| Base roughness | 0.84 | 0.78 | **0.82** |
| StoneBlock tile | 1.2 m | 1.5 m | **1.2 m**, with continuous crease blend (§6.1) |
| FieldStone tile / seeds | 2.0 m, rows + Lloyd | Poisson disk | **3.0 m** (seamless with modules at offset 0), **rows + 1 Lloyd step** |
| Mossy variant | Full set, vertical gradient | — | **Deferred**, and never with a vertical gradient |
| Cut stone | Retune Ashlar | Re-shade Ashlar | **Shared `paint_masonry()` plus re-tile Ashlar to 3.0** |
| Wall pop-outs | — | Metadata-aligned | **Adopt**, and reduce their count |
| Chimney scale | Tile 1.8 m override | — | **Adopt** |

---

## 4. Helper changes in `vk_tex.py` (do these first)

```python
def wrapd(d, P=1.0): return (d + P*0.5) % P - P*0.5              # signed periodic delta
def lerp(a, b, t):   return a + (b - a)*t
def smin(a, b, k):                                                  # polynomial smooth-min, k may be an array
    h = np.clip(0.5 + 0.5*(b - a)/k, 0, 1); return b + (a - b)*h - k*h*(1 - h)
def down2(a):                                                       # 2x box downsample, tile-safe
    S = a.shape[0]//2; return a.reshape(S, 2, S, 2, *a.shape[2:]).mean(axis=(1, 3)).astype(f32)
def hx(s): return np.array([int(s[i:i+2], 16) for i in (1, 3, 5)], f32)/255.0   # "#9B9384" -> sRGB floats

# crack_segments(..., starts=None): if starts is given, run walk(x, y, a, nsteps, w0, 0) for each (x, y, a, nsteps)
#                                   instead of the random loop

def voronoi_edge(x, y, pts, w=None, sx=1.0, sy=1.0):
    """Tileable power diagram. Returns ID1, ID2 (neighbour across the nearest edge),
       E (exact distance to the cell border, UV units, real space), ox, oy (offset from own seed, UV)."""
    pts = np.asarray(pts, f32); N = len(pts); w = np.zeros(N, f32) if w is None else np.asarray(w, f32)
    P1 = np.full(x.shape, np.inf, f32); ID1 = np.zeros(x.shape, np.int32)
    for i, (px, py) in enumerate(pts):
        dx = wrapd(x - px)*sx; dy = wrapd(y - py)*sy; P = dx*dx + dy*dy - w[i]
        m = P < P1; P1 = np.where(m, P, P1); ID1[m] = i
    ax, ay = pts[ID1, 0], pts[ID1, 1]; ox, oy = wrapd(x - ax), wrapd(y - ay)
    E = np.full(x.shape, np.inf, f32); ID2 = np.zeros_like(ID1)
    for j, (bx, by) in enumerate(pts):
        abx = wrapd(bx - ax)*sx; aby = wrapd(by - ay)*sy; L = np.hypot(abx, aby) + 1e-9
        dbx = ox*sx - abx; dby = oy*sy - aby; Pb = dbx*dbx + dby*dby - w[j]
        e = (Pb - P1)/(2*L)/np.hypot(abx/L*sx, aby/L*sy)       # scaled-space distance -> real space
        e = np.where(ID1 == j, np.inf, e); m = e < E; E = np.where(m, e, E); ID2[m] = j
    return ID1, ID2, E, ox, oy
```

`write_set` stays unchanged.

---

## 5. `gen_stone()` v2: T_VK_Stone (coursed rubble)

### 5.1 Frame
- Signature: `gen_stone(S=2048, seed=9, T=3.0, depth=0.06, lacing=True)`. Work at 2048, then `down2` to a **1024** output.
- Coordinates in metres:
  - `x, y = grid(S)`, `X = x*T`, `Y = T*(1 - y)`. Y points up, because array row 0 is the image top (v = 1): `write_map` flips the rows.
  - `px = T/S` (0.00146 m).
- All pixel radii below are **@2k**.
- Everything must wrap: use `fbm`, `wrapd`, `np.roll`, `np.interp(period=T)` and `draw_segments(wrap=True)`. Never use `np.gradient` or reflect-boundary filters.
- Before the full render, run a **seed search**: build the layout only (§5.2–5.3 design values plus the colour assignment) for seeds 0–49. Keep the seeds that pass the layout tests in §9.1 (stone count, maximum area ratio, neighbour rules), then fully render the best 2–3.

### 5.2 Layout (partition)
```
Courses (7): nL = 3 or 4 (lacing index; never 0 or 6).
  H[r] ~ U(0.34,0.54); lacing H[nL] ~ U(0.20,0.24); rescale the other 6 so ΣH = 3.0 exactly.
  y0 = [0, cumsum(H)]                                  # design bed heights, y0[7] = 3.0
Bed lines B[r](x), r = 0..6, as (8,S) arrays over columns:
  B[r] = y0[r] + np.interp(xs, xp, fp, period=T), 5 vertices, xp = (k + U(-0.2,0.2))*T/5 mod T (sorted),
  fp ~ U(-0.025, 0.025) m (r = 0: ±0.008); B[7] = B[0] + T.
  Re-draw if any B[r+1]-B[r] < 0.7*H[r].
Band per pixel: Yw = B0 + (Y - B0) % T  (B0 = B[0][col]);  r = Σ_{j=1..6} (Yw >= B[j][col])
  dB = Yw - B[r][col] - 0.0025 ;  dT = B[r+1][col] - Yw - 0.0025        # beds 0.5 cm wider than heads
Head joints of course r: widths ~ lognormal(ln(1.45*H[r]), 0.30), clipped to
  [max(0.28, 0.75H), min(1.20, 2.6H)]  (lacing: median 3.0H, clip [0.45, 1.20]);
  draw until Σ >= T, rescale to T; re-draw if any width falls outside [0.25, 1.30].
  J = (x0_r + cumsum) mod T, sorted; tilt t ~ U(-0.30, 0.30) (lacing ±0.15); yc[r] = (y0[r]+y0[r+1])/2.
Stagger: each joint, evaluated at the shared bed (J + t*(y0[r]-yc[r])), must be ≥ 0.12 m (wrapped) from
  every joint of course r-1 evaluated at the same bed. Also check course 0 against course 6 at y = 0 ≡ 3.0.
  Up to 30 re-draws, then relax to 0.09 m.
Labelling (vectorised per course band; about 5 joints × 600k pixels):
  s_k = wrapd(X - J_k - t_k*(Yw - yc[r]), T) / sqrt(1 + t_k²)
  dL = min over s_k >= 0 ; kL = its argmin ; dR = min over (-s_k), s_k < 0 ; lab = base[r] + kL
  (valid because every width < T/2)
Stone centre: cx = J_kL + w/2 (mod T), cy = yc[r]; local offset (wrapd(X-cx,T), Yw-cy).
```
Expected result: 30–36 stones (typical 0.67 × 0.46 m) plus 6–10 packers per 9 m².

### 5.3 Silhouette (signed distance, positive inside the stone)
```
k_i ~ U(0.012, 0.035) per stone (crisp vs worn)
d = smin(smin(smin(dB, dT, k), dL, k), dR, k)
Corner chamfers (each corner p = 0.5): BL(dL,dB), BR(dR,dB), TL(dL,dT), TR(dR,dT)
  a, b ~ U(0.6,1.4), c ~ U(0.03,0.10), clipped so each leg c/a, c/b ≤ 0.3*min(w,H)
  dC = (a*d1 + b*d2 - c)/sqrt(a²+b²);  disabled corners: dC = 9.0;  d = smin(d, dC, k)
d += 0.002 * fbm(S,2.0,seed+3,fmin=10,fmax=40)                    # gentle wobble only
g  = clip(0.0085 + 0.0025*fbm(S,2.0,seed+4,fmin=6,fmax=30), 0.005, 0.013)   # joint half-width
```
**Bites** (worked on a wrapped bounding-box slice per stone):
- 0/1/2 bites per stone with probabilities 0.4/0.4/0.2; 65 % sit on the top edge or top corners.
- Each is an ellipse centred on the edge, semi-axes U(0.0075, 0.0175) m along the edge by U(0.005, 0.01) m across it.
- `d = where(lab==i, minimum(d, g + ellipse_sd), d)`, where `ellipse_sd` is negative inside the ellipse.

**Packers:**
- Candidates are corners with both legs ≥ 0.06 m. Accept with p = 0.25, keeping packers at least 0.10 m apart.
- Centre: the centroid of the chamfer triangle, (c/3a, c/3b) from the corner towards that stone.
- Shape: `rx = 0.30*min(c/a, c/b)`, `ry = 0.75*rx`.
- `d_p = -ellipse_sd`. Where `d_p > d`, set `lab = packer_id` and `d = d_p`.
- Packer parameters: protrusion 0.018–0.022 m, bevel radius 0.5·ry, no facets, palette S6 (50 %) or S3.

Final quantities: `dp = d - g` (inside the visible stone where dp > 0) and `stone = smooth(-0.0012, 0.0012, dp)`, the anti-aliased mask for colour only.

### 5.4 Per-stone parameter arrays (indexed by `lab`)
| Parameter | Value |
|---|---|
| Protrusion `p` | U(0.028, 0.036) m |
| Tilt `tx, ty` | U(−0.035, 0.035) m/m |
| Facets (K = 4) | `θ_k = 90°k + U(−35°,35°)`, `s_k ~ U(0.08,0.15)` m/m, `a_k ~ U(0.3,0.7)`, `fsign_k ~ U(−1,1)` |
| Bevel radius `r` | clip(0.12·min(w,H), 0.03, 0.06) m |
| Inner radius | `inr = 0.5·min(w,H) − 0.0085` |
| Face chips | count 0/1/2 with probabilities 0.4/0.45/0.15; disc radius U(0.02, 0.045) m, centred on the top or side edge |
| Crack flag | True for about 1 stone in 6 |
| Colour | palette ID, `val`, `warm` (§5.6) |

### 5.5 Height (metres, then h01 = h/0.06)
```
hm    = 0.004 + 0.003*smooth(-0.006, 0, dp) + 0.0006*fbm(S,1.2,seed+6,fmin=120)   # mortar with meniscus
R_k   = 0.5*(|cosθ_k|*w + |sinθ_k|*H)
facet = min(0, min_k s_k*(a_k*R_k - (lx*cosθ_k + ly*sinθ_k)))                   # flat top plus chamfer planes
hface = p + tx*lx + ty*ly + facet + 0.006*smooth(0, 0.85*inr, dp)**0.7
        + 0.0006*fbm(S,1.8,seed+13,fmin=60,fmax=300)                            # grain (faces only)
        - 0.0015*smooth(2.2, 2.6, fbm(S,2.0,seed+14,fmin=40,fmax=200))           # sparse pits
hface = maximum(hface, hm + 0.012)
s     = clip(dp/r, 0, 1);  prof = 1 - (1 - s)**2                                  # finite slope, flat crest
h_st  = hm + (hface - hm)*prof                                                    # meets mortar continuously
Face chips: inside each disc, h_st = min(h_st, hm + 0.006 + 0.577*dp)             # 30° plane rising from the edge
Cracks:     h_st -= 0.012*crack
h     = where(dp > 0, h_st, hm);  h01 = blur(clip(h/0.06, 0, 1), 1.0)
```
**Cracks.** Call `crack_segments(S, rng, starts=[...], step_px=(8,15), w0=2.5, branch=0.15, jit=0.5)`:
- One start per flagged stone, at a random point on its top or side edge (dp ≈ 0.01 m).
- Angle pointing inward ±30°.
- `nsteps` chosen so the length is ≤ 0.6 × the stone's width.
- Draw with `draw_segments`, then multiply by `(stone > 0.5) * isin(lab, cracked_ids)`.

Delete `facets()` / `-|fbm|` from this texture completely.

### 5.6 Palette (sRGB, the values written to the `_BC` bytes)
| ID | Role | Hex | Share |
|---|---|---|---|
| S1 | warm grey (base) | **#9B9384** | 38 % |
| S2 | pale limestone | **#B0A792** | 16 % |
| S3 | cool blue-grey | **#8B8F93** | 20 % |
| S4 | soft sandstone (desaturated from P1's #AD967A, saturation 0.23 vs 0.29) | **#A99682** | 12 % |
| S5 | mauve accent | **#9E8886** | 6 % |
| S6 | slate (packers, lacing) | **#74767A** | 8 %; 60 % of lacing stones |
| HI / SH | highlight / shadow tint | **#F4E9CC / #3E3A4C** | – |
| MO | lime mortar | **#6E6557** | – |
| Lichen | sage / ochre / pale | #A9B38C / #C8963E / #DAD5BD | 60/30/10 |
| Moss | deep / mid / tip | #3A5226 / #5F7F34 / #93AE52 | – |

**Per stone:**
- `val ~ U(0.93, 1.06)`.
- `warm ~ U(−1, 1)`: `rgb *= (1+0.02w, 1, 1−0.025w)`.

**Assignment:**
- Build adjacency from the design values: stones sharing a head joint, plus stones in adjacent courses whose x-ranges overlap on the shared bed, including wrap.
- Assign in random order with re-rolls (up to 50 per stone):
  - no touching pair shares S4, S5 or S6;
  - touching stones differ in luma by at least 4 %;
  - no stone is more than 1.8σ from the mean luma.

### 5.7 Paint stack (in this order, at 2k)
1. **Local colour:** `col = hx(pal)[pid[lab]]*val[lab]*warm_mul[lab]`.
2. **Facet tint:** where `facet < −0.002`, with `k*` = the active plane: `col *= 1 + 0.035*fsign[lab,k*]`.
3. **Per-stone gradient:** `vloc = clip(dB/(dB+dT), 0, 1)`, then `col *= 0.94 + 0.09*vloc`.
4. **Brush strokes:** three fields `fbm(S,2.2,seed+40+j,fmin=12,fmax=70,ax=4,angle=(0.35,1.40,2.44)[j])`, chosen by `lab%3`: `col *= 1 + 0.025*stroke`.
5. **Mortar composite:**
   - `mort = hx(MO)*(1+0.05*fbm(S,1.5,seed+15,fmin=20,fmax=150))`.
   - `ledge = (1-stone)*np.roll(stone, -8, 0)` marks the lower lip of each bed joint; `mort *= 1 + 0.06*ledge`.
   - `col = lerp(mort, col, stone)`.
6. **Form light:**
   - `Ln = normalize(-0.12, 0.80, 0.58)`.
   - `n_s = normal_from_height(blur(h01,4.0), 0.06*2.0, 3.0)`.
   - `s = painted_light(n_s, Ln) - Ln[2]`.
   - Soft posterise: `q = s/0.10; s = lerp(s, (floor(q)+smooth(0.3,0.7,q-floor(q)))*0.10, 0.35)`.
   - `hi = clip(s/0.35,0,1)`: `col = lerp(col*(1+0.28*hi), HI, 0.18*hi)`.
   - `lo = clip(-s/0.45,0,1)`: `col = lerp(col*(1-0.30*lo), SH, 0.28*lo)`.
7. **Top rim (the signature):**
   - `band = smooth(0,0.004,dp) - smooth(0.012,0.024,dp)`.
   - `rim = band*smooth(0.20,0.50,n_s[...,1])`.
   - `col = lerp(col*(1+0.10*rim), HI, 0.40*rim)`.
   - This replaces the old all-round `rim`.
8. **Underside:** `under = band*smooth(0.15,0.45,-n_s[...,1])`, then `col = lerp(col*0.80, SH, 0.25*under)`.
9. **Cast shadow** (sign fixed):
   - For k = 1..20: `occ = max(occ, np.roll(h, (k, round(0.15*k)), (0,1)) - h - k*px*1.43)` (h in metres).
   - `sh = blur(smooth(0, 0.004, occ), 1.2)`, then `col = lerp(col*(1-0.45*sh), SH, 0.30*sh)`.
10. **Chips:**
    - Chip faces: `col = lerp(col, lerp(col, luma(col), 0.5)*1.12, 0.7)`.
    - Line under each chip: `clip(np.roll(chip,2,0)-chip,0,1)`, then `col = lerp(col, SH, 0.5*line)`.
11. **Cracks:**
    - `col = lerp(col, lerp(col*0.5, SH, 0.4), crack)`.
    - Lit lip below the crack: `col *= 1 + 0.08*np.roll(crack,3,0)*(1-crack)`.
12. **Lichen:**
    - 3–5 colonies, each 8–25 dots of radius 0.004–0.012 m inside a 6–12 cm patch.
    - Only where `stone>0.5 & vloc>0.4`; alpha 0.85; at most 3 % of stone area; +0.001 m height.
13. **Ledge moss:**
    - `moss = smooth(0.8,1.6,fbm(S,3.0,seed+30,fmin=2,fmax=24)) * smooth(-0.2,0.6,fbm(S,1.8,seed+31,fmin=40,fmax=200)) * max(ledge, 0.6*rim)`.
    - Tune the first threshold until about 2 % of the tile has moss > 0.5.
    - Colour from a 3-stop ramp driven by `fbm(fmin=60)`; +0.003 m height.
14. **Macro breakup:** `col *= 1 + 0.03*fbm(S,2.0,seed+50,fmin=1.5,fmax=5)`. Keep it at ±3 % or less. **No vertical gradients.**

### 5.8 Roughness, AO, output
- **Roughness:** `R = clip(0.82 + 0.03*fsign* - 0.06*rim - 0.08*chip + 0.11*(1-stone) + 0.04*lichen + 0.10*moss, 0.60, 0.97)`.
- **Downsample:** `bc, h1, R1 = down2(col), down2(h01), down2(R)`.
- **AO:** `ao = cavity_ao(h1, radii=(3,10,30), k=(2.0,1.5,0.9), floor=0.40)`.
- **Write:** `write_set("T_VK_Stone", bc, h1, R1, 0.06, 3.0, ao=ao, ao_in_albedo=0.30)`.
- **Registry:** `PBR_SETS["T_VK_Stone"]=dict(depth=0.06, tile=3.0)`. `MAT_MAP["M_VK_Stone"]` nstr changes from **1.1 to 1.0**.
- **Unity import:**
  - BC: sRGB.
  - N: Normal map (OpenGL Y+ already, so no flip).
  - R: linear; store 1−R in the Metallic alpha as smoothness.
  - AO: occlusion strength 0.5, because 30 % is already baked into BC.
  - H: parallax only, at strength ≤ 0.02.

### 5.9 Stone metadata (for aligned pop-outs)
Write `Textures/T_VK_Stone_stones.json` as a list of `{u: cx/3, v: yc/3, w, h, lab}` for every stone with w·H > 0.25 m². For a −Y-facing module at UV offset 0, the stone sits at `x_local = wrapd(-3u, 3.0)` and `z = 3v`.

### 5.10 Tuning knobs (in this order)
| Knob | Default | Effect |
|---|---|---|
| `g` | 0.0085 | Mortar coverage |
| `lo` gain | 0.30 | Underside darkness |
| `hi` gain | 0.28 | Top-edge highlight strength |
| Width median | 1.45·H | Stone scale at game distance |
| `k_i` range | 0.012–0.035 | Crisp vs worn corners |
| `s_k` range | 0.08–0.15 | How chiselled the faces look |
| Posterise blend | 0.35 | Hand-painted banding; 0 turns it off |

---

## 6. Variants

### 6.1 T_VK_StoneBlock (required): jointless dressed face for every modelled block
- Signature: `gen_stoneblock(S=2048, seed=17, T=1.2, depth=0.05)`.
- **Seeds:** a 4 × 3 jittered grid (cell 0.30 × 0.40 m, jitter 0.35 × cell), w = 0.
- **Edges:** `ID1, ID2, E, ox, oy = voronoi_edge(x, y, pts)`; convert `E_m = E*T`.
- **Facet planes:** `h_i(p) = U(-0.003,0.003) + s_i*(p-c_i)·(cosθ_i, sinθ_i)`, with `s_i ~ U(0.05,0.12)` m/m (3–7°).
  - Evaluate `h_a` using the own seed and `h_b` using the `ID2` seed (offset `wrapd(x-bx)`, `wrapd(y-by)`).
- **Continuous crease:** `h = lerp(h_a, h_b, 0.5*(1-smooth(0,0.006,E_m)))`, which is continuous across the bisector.
  - Then `h -= 0.0012*(1-smooth(0,0.003,E_m))` for the chisel groove.
  - Grain: `+0.0004*fbm(fmin=60,fmax=300)`.
  - One hairline crack at −0.004 m.
  - `h01 = clip(0.5 + h/0.05, 0, 1)`.
- **Colour:**
  - `lerp(S1, S2, smooth(-0.6,0.6,fbm(S,2.5,seed+1,fmin=1.5,fmax=6)))*(1+0.04*fval[ID1])`.
  - Strokes ±2 %, then paint steps 6, 12 and 14 (no rim, underside or cast shadow; the geometry bevels supply the edges).
  - Crease line: `col *= 1-0.10*(1-smooth(0,0.004,E_m))`.
  - 1–2 lichen colonies.
- **Roughness:** `0.78 + 0.03*fbm`.
- **Write:** `ao_in_albedo=0.25`.
- **Use:** sills, jambs, voussoirs, lintels, steps, thresholds, quoins, caps, the well ring, pop-outs, and every horizontal STONE face. The random UV offset per box stays and gives variety.

### 6.2 T_VK_FieldStone (worth it): rough rural and dry-stone walling
- Signature: `gen_fieldstone(S=2048, seed=31, T=3.0, depth=0.08)`. The tile is 3.0 m so that modules join seamlessly at offset 0.
- **Seeds:**
  - Rows with pitch U(0.28, 0.40) m, rescaled so Σ = 3.0.
  - Along each row, spacing U(0.35, 0.65) m, rescaled to 3.0.
  - Jitter ±25 % in x and ±15 % in y.
  - One Lloyd step, done at S/4 using a circular-mean centroid per ID (`bincount` of the cos/sin of 2πx and 2πy).
  - Add 12 % packer seeds at triple points with `w = -(0.05/T)²`.
  - Call `voronoi_edge(..., sx=1, sy=1.35)`.
- **Gaps:** `g = clip(0.012+0.005*fbm(fmin=6,fmax=30), 0.006, 0.02)` m. Gaps are soil #3A3029 (±6 %) at h = 0.002 m. In 25 % of gaps, add pebbles: 0.8–1.5 cm ellipses, #7A7066, h = 0.008 m.
- **Stones:**
  - Protrusion 0.035–0.050 m.
  - Bevel `r = clip(0.4*sqrt(area/π), 0.04, 0.09)`, same `prof`.
  - Facet slopes 0.04–0.08.
- **Palette:** S1 30 %, S4 25 %, brown #85766A 15 %, S3 15 %, S2 10 %, S6 5 %. On 30 % of stones add granite speckle (#5A5652 / #C9C3B6, 1–2 px @1k, 3 % coverage). This is the only place high-frequency speckle is allowed.
- **Paint and weathering:** full paint stack; moss 6–8 % (ledges plus upward bevels `n_s.y > 0.5`); lichen 3 %; no vertical gradient.
- **Roughness:** 0.86 stone, 0.95 soil, 0.92 moss. `ao_in_albedo=0.35`.
- **Tier mapping** (colony-sim readable): field stone for poor and rural buildings (barn and stable plinths, farm walls, graveyard wall, and a new dry-stone field-wall fence piece), rubble for town houses, ashlar for civic buildings.

### 6.3 Ashlar (retune, not a new texture)
- Move paint steps 6–9 and 14 plus AO into `paint_masonry(col, h01, dp, stone, S, T, depth)` and call it from `gen_stone`, `gen_fieldstone` and `gen_ashlar`.
- Re-tile Ashlar to **3.0 m**: `nrow=6` (0.5 m courses kept), `blocks=[4,5,4,5,4,5]`. Set `TILE[ASHLAR]=3.0`.
- Mortar #736A5E. Drop `facets()` there too.

### 6.4 Mossy stone
Deferred to last. When it is built, bake uniform moss (about 10 %, ledges and joints) with **no vertical gradient**. Do the ground-up concentration in the engine shader with a world-height mask.

### 6.5 Tint variants (no new textures)
- Add `VARIANT_MATS["stone"] = {"Rubble": None, "Field": ("T_VK_FieldStone", None), "Warm": ("T_VK_Stone", (1.04,1.00,0.94)), "Cool": ("T_VK_Stone", (0.95,0.98,1.03)), "Dark": ("T_VK_Stone", (0.88,0.88,0.88))}`.
- Add `SLOT["stone"] = STONE`, and base `"M_VK_Stone"` in `variant_mat`.
- Add the matching `MAT_MAP` entries (for example `"M_VK_Stone_Warm": dict(prefix="T_VK_Stone", tint=(1.04,1.0,0.94), nstr=1.0)`) so that `apply_pbr_all()` builds them as PBR.
- `random_style(seed)` picks one per building.

---

## 7. Kit integration (`vk_helpers.py`, `vk_mat.py`)

1. **New slots:**
   - Constants: `STONE_BLOCK, FIELDSTONE = 45, 46`.
   - Append `tex_mat("M_VK_StoneBlock","T_VK_StoneBlock"), tex_mat("M_VK_FieldStone","T_VK_FieldStone")` at the **end** of `kit_mats()`, so existing indices do not change.
   - `TILE[45]=1.2`, `TILE[46]=3.0`.
   - `MAT_MAP` entries with nstr 1.0 (FieldStone 1.1).
   - The textures must exist before `kit_mats()` runs. All pieces must be rebuilt, because existing meshes have 45 slots.
2. **`Kit.box(..., uv_offset=None, tile=None)`:**
   - At the **top**, before any material assignment: `if mi==STONE and bevel>0 and (sorted(size)[1]<0.7 or min(size)<0.25): mi=STONE_BLOCK`.
   - Offset: `(0,0) if mi in (STONE, ASHLAR, FIELDSTONE) and bevel==0 else` the existing hash offset.
   - This covers `stone_panel`, both `plinth`s, `arch_cut_panels` strips, `corner_stone` cores, L2430 and L2664.
3. **`project(..., tile=None)`:**
   - `t = tile or TILE.get(mi,1.0)`.
   - Per face: `if mi==STONE and abs(n.z)>0.7`: set `f.material_index=STONE_BLOCK` and use `TILE[STONE_BLOCK]`.
4. **Chimney:** `chimney()` (L1818) stack box gets `tile=1.8`, giving about 2.5 stones across 1.0 m.
5. **Pop-outs to STONE_BLOCK:**
   - `rock()` default `mi` becomes `STONE_BLOCK`; `arch_ring` default `mi=STONE_BLOCK`; impost L1858 becomes STONE_BLOCK.
   - Replace `ROCK` with `STONE_BLOCK` in the building and prop code of `vk_helpers.py` (fountain, well, graves, slabs).
   - **Keep `ROCK` / `ROCK_MOSSY` in `vk_nature.py`** for natural boulders only.
6. **`wall_rocks`:**
   - Replace random placement with stones chosen from `T_VK_Stone_stones.json`: centre `(wrapd(-3u,3), face, 3v)`, size `(0.9w, U(0.06,0.10), 0.9h)`, `STONE_BLOCK`, `tilt=0.02`, honouring `avoid`.
   - Counts: plain 2, window 1, door 1 (down from 6/4/3).
   - This removes the "stones on stones" look.

---

## 8. Build order (highest value first)

| # | Item | Why | Effort |
|---|---|---|---|
| 1 | §4 helpers | Prerequisite | S |
| 2 | **`gen_stone` v2** (§5) + nstr 1.0 + depth 0.06 + JSON metadata | The actual request, and the biggest visual gain | L |
| 3 | UV offset rule + `tile=` param + chimney 1.8; rebuild pieces | Removes seams around every window and door; bed joints land at z = 0 and 3.0 | S |
| 4 | `voronoi_edge` + **StoneBlock** + slot 45 + `box()`/`project()` reassignment + ROCK→STONE_BLOCK in vk_helpers | No more mortar lines across single blocks; one stone family | M |
| 5 | Aligned `wall_rocks` from the metadata | Real silhouette depth that matches the painted stones | S |
| 6 | `paint_masonry()` shared + Ashlar re-tile to 3.0 | One lighting language across all masonry | S–M |
| 7 | **FieldStone** + slot 46 + `VARIANT_MATS["stone"]` + tier mapping + dry-stone field-wall piece | Colony-sim building tiers, rural variety | M |
| 8 | Mossy stone (uniform) | Nice to have | S |

---

## 9. Acceptance tests

### 9.1 Numeric, on the 1024 output (luma = 0.2126R + 0.7152G + 0.0722B on sRGB)
| Check | Target |
|---|---|
| Joint coverage (`down2(stone) < 0.5`) | 10–14 % |
| Joint mean | ≈ #4A444A–#555048 (luma 0.27–0.33); p1 of joints ≥ #20 |
| Stone mean | ≈ #9A9283 ± 0.03 |
| Tile mean | ≈ #908879 ± 0.03 (luma 0.53–0.58) |
| Stone luma p5 / p50 / p95 | 0.32–0.42 / 0.53–0.58 / 0.70–0.76 (p95 on top rims, p5 on undersides) |
| Per-stone mean luma σ | 0.04–0.06 |
| Neighbours | 100 % of touching pairs differ by ≥ 4 % luma; no same-family S4, S5 or S6 pairs |
| Layout | 30–36 stones + 6–10 packers; no stone > 2.5 × median area; widths 0.28–1.20 m |
| Height | Mortar h01 0.07–0.13; faces 0.45–0.62; mean normal xy \|·\| < 0.01; max bevel tilt ≤ 65° |
| Tiling | `np.roll(·,(512,512))` on BC, N and H: mean \|Δ\| across the wrapped seam ≤ 1.5 × the interior neighbour \|Δ\| |
| Mips | 1/32 downsample mean within 0.02 of full-res; a 32 × 32 thumbnail shows about 7 soft courses and no speckle |
| Repetition | Tile 4 × 1, blur σ = 20 px: luma range < 8 % |
| Runtime | `gen_stone` ≤ 60 s at 2k in Blender Python |
| StoneBlock / FieldStone | No mortar in StoneBlock; FieldStone gap coverage 12–16 %, tile luma 0.48–0.54 |

### 9.2 Visual renders
1. **`town_detail` framing (2 m):** every stone reads as a volume lit from above, with 2–4 planes, a cream top lip, a violet underside and recessed mortar. No sponge surface and no pillows.
2. **`town_street` (12 m):** no beige and grey patchwork. The bed-joint rhythm and lacing course are visible. No seams at window or door sub-panels or between modules.
3. **Colony camera (40 m, 50° pitch, plus a 128 px per tile mip preview):** stones still read as value patches. The ground floor sits clearly between dark timber and light plaster in value.
4. **`catalog_walls` / `catalog_props` / `village_special_buildings`:** sills, voussoirs, well ring, quoins and steps show no mortar lines. Chimneys show at least 2 stones across. The windmill and tower show no horizontal banding.
5. **Pop-outs:** aligned `wall_rocks` sit exactly over painted stones.

---

## 10. Pitfalls

- **Pillows:** never blend stone and mortar heights with a mask. The bevel must start at mortar level. Never use a profile with a vertical tangent at the edge, and never give every stone the same `k` or `r`.
- **Double darkening:** baked AO, the painted shadow, `finish()` grime (0.62 at the ground) and SSAO all multiply. Keep `ao_in_albedo` at 0.30 or below and the mortar floor at about #40 or above.
- **Baked light fighting engine light:** keep the highlight gain at +30 % or less and the light near-vertical. The texture is used on every façade direction, on the octagonal windmill and on a 90°-rotated corner.
- **Aliasing:** anything that must survive at the colony camera has to be at least 8 px wide at 1k (at least 2.3 cm): the dark under-band, the top rim, and value differences between stones. Hairline cracks and lichen dots are close-up only.
- **Pixel radii:** all blur, roll and march values here are @2k. Halve them if the generator runs at 1k.
- **Colour space:** the hex values are sRGB byte values, because `write_map` stores `img.pixels` unconverted. Convert to linear only if you switch to float images.
- **Wrap:** course 0 against 6 and the x wrap must appear in both the stagger and the adjacency checks. `np.interp` needs `period=T` and xp sorted in [0, T).
- **Slot changes** need a full rebuild of pieces and variant meshes (`variant_mesh` copies the old slot list).