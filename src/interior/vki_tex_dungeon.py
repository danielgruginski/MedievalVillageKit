# ===================== VKI dungeon textures (docs/DUNGEON_KIT.md) =====================
# Text vki_tex_dungeon (src/interior/vki_tex_dungeon.py). Executed on demand after vki_tex, never by vki_ns():
#   g={}
#   for t in ("vk_tex","vk_texgen","vk_tex2","vk_mat","vki_tex","vki_tex_dungeon"): exec(bpy.data.texts[t].as_string(),g)
#   g["vki_tex_run"]("T_VKI_DungeonIn")          # exactly ONE generator per MCP call
# Adds the dungeon sets to vki_tex's VKI_TEX_JOBS; the generators are vki_tex's (vki_gen_blocks), so the interior rules
# hold: painted at 2048, stored at 1024, cavity AO folded into the albedo, no moss, lichen or cracks.
#   T_VKI_DungeonIn    walls (t 1.5): big coursed blocks (courses 0.34-0.42 m, blocks 0.5-0.75 m), cool dark greys with
#                      a few warmer stones, deep rounded arrises and wide dark joints -- chunky, reads block by block
#   T_VKI_DungeonFlag  floors (t 3.0): worn slabs 0.9-1.5 m in five unequal courses, dark and cool, chipped edges
# Every top-level name starts with vki_/VKI_ (test T18).

VKI_TEX_JOBS.update({
    "T_VKI_DungeonIn":   lambda: vki_gen_blocks(seed=71, T=1.5, nrow=4, blocks=(3, 2, 3, 2), pal=("S3", "S6", "S1"),
                                                mortar="#2E2A27", chip=0.9, depth=0.035, gap=0.0065, wjit=0.28, min_sep=0.14,
                                                tone=0.62, mtone=1.0, cham_m=0.05, dnoise=0.004, dfmax=14,
                                                rows=(0.40, 0.34, 0.42, 0.36), vrange=(0.80, 1.12), warm_amp=2.5,
                                                out_prefix="T_VKI_DungeonIn"),
    "T_VKI_DungeonFlag": lambda: vki_gen_blocks(seed=72, T=3.0, nrow=5, blocks=(3, 2, 3, 2, 3), pal=("S3", "S6", "S5", "S1"),
                                                mortar="#2A2623", chip=1.0, depth=0.03, gap=0.007, wjit=0.35, min_sep=0.25,
                                                tone=0.56, mtone=1.0, cham_m=0.03, dnoise=0.003, dfmax=10,
                                                rows=(0.62, 0.55, 0.66, 0.58, 0.60), vrange=(0.82, 1.12), warm_amp=2.0,
                                                out_prefix="T_VKI_DungeonFlag"),
    # adventure kit: the ruined temple -- huge weathered blocks (courses 0.5 m, blocks 0.75 / 1.5 m, deep rounded
    # arrises, heavy chipping), pale greenish-tan; big pale floor slabs
    "T_VKI_AncientIn":   lambda: vki_gen_blocks(seed=81, T=1.5, nrow=3, blocks=(2, 1, 2), pal=("S2", "S4", "S1"),
                                                mortar="#3A382F", chip=1.4, depth=0.04, gap=0.006, wjit=0.20, min_sep=0.25,
                                                tone=0.80, mtone=1.0, cham_m=0.07, dnoise=0.005, dfmax=12,
                                                rows=(0.52, 0.46, 0.52), vrange=(0.84, 1.10), warm_amp=1.5,
                                                out_prefix="T_VKI_AncientIn"),
    "T_VKI_AncientFlag": lambda: vki_gen_blocks(seed=82, T=3.0, nrow=4, blocks=(2, 3, 2, 3), pal=("S2", "S1", "S4"),
                                                mortar="#34322A", chip=1.2, depth=0.03, gap=0.006, wjit=0.30, min_sep=0.30,
                                                tone=0.70, mtone=1.0, cham_m=0.04, dnoise=0.003, dfmax=10,
                                                rows=(0.80, 0.70, 0.82, 0.68), vrange=(0.84, 1.10), warm_amp=1.5,
                                                out_prefix="T_VKI_AncientFlag"),
    # the caves: natural rock -- fracture facets, lumps, bedding, hairline cracks, damp runs; no joints (v1 small plates
    # read as cobbles in grout, v2 flagrustic plates as stacked masonry)
    "T_VKI_CaveRock":    lambda: vki_gen_rockface(seed=95, T=1.5, depth=0.10, tone=1.0, out_prefix="T_VKI_CaveRock"),
    # packed cave earth with pebbles and a grey dust haze (the interior earth generator, no rushes)
    "T_VKI_CaveFloor":   lambda: vki_gen_earthfloor(seed=93, T=3.0, depth=0.03, rushes=0.0, soot=0.35,
                                                    out_prefix="T_VKI_CaveFloor"),
    "T_VKI_Web":         lambda: vki_gen_web(),
})


def vki_gen_web(S=1024, seed=5, out_prefix="T_VKI_Web"):
    """spider silk (RGBA, stored _BC with alpha): a radial orb web (15 spokes, a spiral of catching thread, a few loose
    strands) centred at (0.5, 0.5), anti-aliased lines 5-8 px wide (a web card is ~1 m: thinner silk vanished at game
    distance), pale grey-white; alpha = the silk"""
    rng = np.random.default_rng(seed)
    segs = []
    cx = cy = S / 2
    n = 15
    angs = [2 * math.pi * i / n + rng.uniform(-0.12, 0.12) for i in range(n)]
    R = S * 0.49
    for a in angs:
        segs.append((cx, cy, cx + math.cos(a) * R * rng.uniform(0.9, 1.0), cy + math.sin(a) * R * rng.uniform(0.9, 1.0), 8.0))
    r = S * 0.04
    while r < R * 0.9:
        for i in range(n):
            a0, a1 = angs[i], angs[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0.0)
            r0, r1 = r, r + S * 0.0035
            segs.append((cx + math.cos(a0) * r0, cy + math.sin(a0) * r0, cx + math.cos(a1) * r1, cy + math.sin(a1) * r1, 6.0))
            r = r1
        r += S * 0.022
    for _ in range(10):
        x0, y0 = rng.uniform(0, S, 2); a = rng.uniform(0, 2 * math.pi); L = rng.uniform(0.1, 0.35) * S
        segs.append((x0, y0, x0 + math.cos(a) * L, y0 + math.sin(a) * L, 5.0))
    m = np.clip(draw_segments(S, segs), 0, 1).astype(f32)
    col = np.stack([m * 0.0 + 0.86, m * 0.0 + 0.87, m * 0.0 + 0.90], -1).astype(f32)
    rgba = np.concatenate([col, m[..., None]], -1)
    img = bpy.data.images.get(out_prefix + "_BC")
    if img is None:
        img = bpy.data.images.new(out_prefix + "_BC", S, S, alpha=True)
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    img.update()
    img.filepath_raw = os.path.join(TEXDIR, out_prefix + "_BC.png"); img.file_format = "PNG"; img.save(); img.pack()
    return rgba


def vki_rock_cells(S, pts, sy=1.0):
    """nearest-seed Voronoi only (tileable): cell id and the offset (ox, oy) from its seed, in tile units"""
    x, y = grid(S)
    best = np.full((S, S), np.inf, f32); ID = np.zeros((S, S), np.int32)
    for i, (px_, py_) in enumerate(pts):
        dx = x - px_; dx -= np.round(dx); dy = y - py_; dy -= np.round(dy)
        d = dx * dx + (dy * sy) ** 2
        m = d < best; best = np.where(m, d, best); ID[m] = i
    P = np.asarray(pts, f32)
    ox = x - P[ID, 0]; ox -= np.round(ox); oy = y - P[ID, 1]; oy -= np.round(oy)
    return ID, ox.astype(f32), oy.astype(f32)


def vki_gen_rockface(S=2048, seed=95, T=1.5, depth=0.10, n=5, tone=1.0, out_prefix="T_VKI_CaveRock", write=True):
    """natural rock (cave walls, rock masses), no joints: fracture facets at two scales (jittered 5 x 5 and 9 x 9
    Voronoi cells, wider than tall, each a tilted plane; the steps between them soften into arrises), broad lumps, wavy
    bedding (small ledges and tone bands, a pale mineral seam here and there), hairline cracks along some of the large
    fracture edges, fine grain and darker damp runs down the face; cool brown-grey. Height, form light and a light cast
    shadow (from the facets only) painted like the other sets."""
    rng = np.random.default_rng(seed); px = T / S
    x, y = grid(S)
    pts = [((i + 0.5 + rng.uniform(-0.38, 0.38)) / n, (j + 0.5 + rng.uniform(-0.30, 0.30)) / n)
           for j in range(n) for i in range(n)]
    N = len(pts)
    ID, E1, E2, ox, oy = voronoi_edge2(x, y, pts, None, 1.0, 1.5)
    del x, y, E2
    E1m = E1 * T; del E1
    tx_ = rng.uniform(-0.12, 0.12, N).astype(f32); ty_ = rng.uniform(-0.06, 0.16, N).astype(f32)
    off = rng.uniform(0.0, 0.03, N).astype(f32)
    facet = (off[ID] + tx_[ID] * ox * T + ty_[ID] * oy * T).astype(f32); del ox, oy
    n2 = 9
    pts2 = [((i + 0.5 + rng.uniform(-0.4, 0.4)) / n2, (j + 0.5 + rng.uniform(-0.35, 0.35)) / n2)
            for j in range(n2) for i in range(n2)]
    ID2, ox2, oy2 = vki_rock_cells(S, pts2, 1.4)
    N2 = len(pts2)
    t2x = rng.uniform(-0.07, 0.07, N2).astype(f32); t2y = rng.uniform(-0.04, 0.09, N2).astype(f32)
    off2 = rng.uniform(0.0, 0.012, N2).astype(f32)
    facet = blur(facet + off2[ID2] + t2x[ID2] * ox2 * T + t2y[ID2] * oy2 * T, 2.5).astype(f32)
    del ox2, oy2
    lo = fbm(S, 2.6, seed + 1, fmin=1.0, fmax=5)
    mid = fbm(S, 2.0, seed + 2, fmin=5, fmax=24)
    warp = fbm(S, 2.4, seed + 3, fmin=1.0, fmax=4)
    yy = np.mgrid[0:S, 0:S][0].astype(f32) * px
    strata = np.sin(2 * math.pi * (yy / (T / 5.0)) + 1.2 * warp).astype(f32)
    seam = (smooth(0.93, 0.99, np.abs(np.sin(2 * math.pi * yy / (T / 2.0) + 1.2 * warp))) *
            smooth(0.3, 1.2, mid)).astype(f32)
    del yy, warp
    ledge = smooth(0.55, 0.95, strata)
    grain = fbm(S, 1.4, seed + 4, fmin=60, fmax=500)
    hf = facet                                                     # the sharp relief (casts the painted shadow)
    h = (0.05 + 0.015 * lo + 0.003 * mid + hf + 0.002 * ledge + 0.0012 * grain).astype(f32)
    hmin = float(np.percentile(h, 1.0))
    h01 = np.clip((h - hmin) / depth, 0, 1).astype(f32)
    # hairline cracks: on the large fracture edges where a low-frequency gate allows, 2-4 mm wide
    gate = smooth(0.4, 1.0, fbm(S, 2.4, seed + 5, fmin=2, fmax=10))
    cw = 0.0012 + 0.0008 * smooth(-1, 1, fbm(S, 2.0, seed + 6, fmin=10, fmax=60))
    crack = (smooth(0, 1, 1 - E1m / cw) * gate).astype(f32); del E1m, gate, cw
    h01 = np.clip(h01 - 0.20 * crack, 0, 1)
    # colour
    val = rng.uniform(0.95, 1.05, N).astype(f32); warm = rng.uniform(-1, 1, N2).astype(f32)
    base = lerp(hx("#58514A"), hx("#7E766B"), np.clip(0.5 + 0.28 * lo + 0.10 * mid, 0, 1)[..., None])
    base = base * val[ID][..., None] * np.stack([1 + 0.025 * warm[ID2], np.ones((S, S), f32), 1 - 0.025 * warm[ID2]], -1)
    del ID, ID2
    base = base * (1 + 0.08 * strata)[..., None]
    base = lerp(base, hx("#A69C8A"), 0.35 * seam[..., None]); del seam
    base = base * (1 + 0.05 * grain)[..., None]
    runs = smooth(0.8, 2.0, fbm(S, 2.2, seed + 7, fmin=3, fmax=40, ay=6.0))
    base = lerp(base, base * np.array([0.78, 0.80, 0.84], f32), 0.6 * runs[..., None])
    speck = fbm(S, 0.5, seed + 8, fmin=300)
    base = np.where((speck > 2.3)[..., None], lerp(base, hx("#3E3934"), 0.5), base)
    base = np.where((speck < -2.3)[..., None], lerp(base, hx("#B5AD9F"), 0.4), base); del speck
    col = (base * tone).astype(f32); del base
    col, n_s = paint_form_light(col, h01, depth, T, hig=0.16, log=0.20, post=0.10, ex=1.4)
    sh = vki_cast_shadow(hf, px, n=10, slope=0.9, soft=0.003)[..., None]
    col = lerp(col * (1 - 0.18 * sh), hx(ST_SH), 0.10 * sh)
    col = lerp(col, hx("#1F1B18"), 0.70 * crack[..., None])
    R = np.clip(0.90 - 0.10 * runs + 0.05 * crack, 0.6, 0.98).astype(f32)
    bc, hh, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(blur(h01, 1.0)), down2(R)
    if write: vki_write_set(out_prefix, bc, hh, R1, depth, T)
    return bc


def vki_gen_rocktop(S=2048, seed=97, T=1.2, depth=0.012, tone=1.0, out_prefix="T_VKI_CaveTop", write=True):
    """the cut tops of the cave's rock tiles: calm pale rock with only fine grain, a faint mottle, specks and a few
    tiny pits -- no structure larger than a few centimetres, so the rotated, repeated tiles never show a grid"""
    rng = np.random.default_rng(seed); px = T / S
    grain = fbm(S, 1.2, seed + 1, fmin=80, fmax=600)
    mott = fbm(S, 1.8, seed + 2, fmin=24, fmax=90)
    h = (0.5 + 0.25 * grain + 0.15 * mott).astype(f32)
    h01 = np.clip((h - h.min()) / (h.max() - h.min() + 1e-6), 0, 1).astype(f32)
    base = lerp(hx("#8A8176"), hx("#9C9388"), np.clip(0.5 + 0.18 * mott, 0, 1)[..., None])
    base = base * (1 + 0.05 * grain)[..., None]
    speck = fbm(S, 0.4, seed + 3, fmin=400)
    base = np.where((speck > 2.2)[..., None], lerp(base, hx("#4E4842"), 0.55), base)
    base = np.where((speck < -2.3)[..., None], lerp(base, hx("#C8C0B2"), 0.45), base)
    col = (base * tone).astype(f32)
    col, n_s = paint_form_light(col, h01, depth, T, hig=0.10, log=0.12, post=0.0, ex=1.0)
    R = np.clip(0.9 + 0.03 * grain, 0.6, 0.98).astype(f32)
    bc, hh, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h01), down2(R)
    if write: vki_write_set(out_prefix, bc, hh, R1, depth, T)
    return bc


VKI_TEX_JOBS.update({"T_VKI_CaveTop": lambda: vki_gen_rocktop()})

# sewer kit (docs/SEWER_KIT.md): old wet brick -- grimy dark red-browns, a few near-black overfired bricks,
# dark mortar -- for the walls (t 1.5, bricks 0.25 x 0.075); brick paving for the walkways (t 3.0, pavers 0.50 x 0.25)
VKI_TEX_JOBS.update({
    "T_VKI_SewerBrick": lambda: vki_gen_brick(seed=641, T=1.5, nr=20, nbk=6, out_prefix="T_VKI_SewerBrick",
                                              pal=[(0.33, 0.21, 0.16), (0.29, 0.19, 0.15), (0.36, 0.24, 0.18),
                                                   (0.30, 0.22, 0.17), (0.27, 0.22, 0.18)],
                                              mortar="#3E3A33", over=0.18, over_col="#231915", vrange=(0.80, 1.06)),
    "T_VKI_SewerFloor": lambda: vki_gen_brick(seed=642, T=3.0, nr=12, nbk=6, depth=0.025, out_prefix="T_VKI_SewerFloor",
                                              pal=[(0.36, 0.25, 0.19), (0.31, 0.24, 0.19), (0.40, 0.29, 0.21),
                                                   (0.28, 0.25, 0.21)],
                                              mortar="#3C3730", over=0.12, over_col="#2A221C", vrange=(0.84, 1.06)),
})


# dwarven halls (docs/DWARF_KIT.md): dark granite ashlar walls (t 1.5: three 0.5 m courses, blocks 0.75 / 1.5 m, tight
# crisp joints, little chipping), and the hall floor -- square polished slabs on a checker of two granites with a carved
# groove inside every slab edge
def vki_gen_dwarffloor(S=2048, seed=111, T=3.0, n=4, depth=0.02, out_prefix="T_VKI_DwarfFloor", write=True):
    """dwarven hall floor (t 3.0): n x n square slabs (0.75 m) on a checker of a darker and a paler granite, 2.5 mm
    joints, a groove cut 0.09 m inside every slab edge (the carved panel line), fine granite speckle, polished"""
    rng = np.random.default_rng(seed)
    x, y = grid(S)
    X = (x * n) % 1; Y = (y * n) % 1
    ci = np.minimum((x * n).astype(np.int32), n - 1); cj = np.minimum((y * n).astype(np.int32), n - 1); del x, y
    d = (np.minimum(np.minimum(X, 1 - X), np.minimum(Y, 1 - Y)) * T / n).astype(f32); del X, Y
    g = 0.0025
    mask = smooth(g, g + 0.002, d)
    groove = (1.0 - smooth(0.004, 0.010, np.abs(d - 0.09))).astype(f32)
    cheq = ((ci + cj) % 2).astype(f32)
    sid = ci * n + cj; del ci, cj
    val = rng.uniform(0.93, 1.05, n * n).astype(f32)
    dk, pl = hx("#4C5054"), hx("#7C7F7B")
    base = (dk[None, None, :] * (1 - cheq[..., None]) + pl[None, None, :] * cheq[..., None]) * val[sid][..., None]
    speck = fbm(S, 0.6, seed + 3, fmin=80, fmax=500)
    base = base * (1 + 0.10 * np.clip(speck, -1.5, 1.5))[..., None]
    base = base * (1 + 0.03 * fbm(S, 2.0, seed + 4, fmin=3, fmax=30))[..., None]
    h = blur(np.clip(mask * (0.55 + 0.30 * smooth(g, g + 0.02, d) - 0.40 * groove) + (1 - mask) * 0.12, 0, 1), 1.2).astype(f32)
    col = lerp(hx("#26272A")[None, None, :], base, mask[..., None])
    col = col * (1 - 0.40 * groove)[..., None]
    col, n_s = paint_form_light(col.astype(f32), h, depth, T, hig=0.12, log=0.18, post=0.20)
    rough = np.clip(0.55 + 0.05 * fbm(S, 2.2, seed + 9, fmin=6) + 0.35 * (1 - mask) + 0.25 * groove, 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(rough)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


VKI_TEX_JOBS.update({
    "T_VKI_DwarfIn": lambda: vki_gen_blocks(seed=101, T=1.5, nrow=3, blocks=(2, 1, 2), pal=("S6", "S3"),
                                            mortar="#232326", chip=0.25, depth=0.03, gap=0.0032, wjit=0.10, min_sep=0.30,
                                            tone=0.62, mtone=1.0, cham_m=0.02, dnoise=0.0015, dfmax=10,
                                            rows=(0.50, 0.50, 0.50), vrange=(0.86, 1.06), warm_amp=0.6,
                                            out_prefix="T_VKI_DwarfIn"),
    "T_VKI_DwarfFloor": lambda: vki_gen_dwarffloor(),
    # the plain floor of the halls' walkways, side rooms and forge (the checker is kept for the processional runner):
    # big granite flags in four 0.75 m courses, 1.0-1.5 m long, crisp tight joints, calm tone
    "T_VKI_DwarfFlag": lambda: vki_gen_blocks(seed=121, T=3.0, nrow=4, blocks=(2, 3, 2, 3), pal=("S6", "S3"),
                                              mortar="#26272A", chip=0.12, depth=0.02, gap=0.0026, wjit=0.12,
                                              min_sep=0.30, tone=0.76, mtone=1.0, cham_m=0.015, dnoise=0.0012,
                                              dfmax=8, vrange=(0.90, 1.05),
                                              warm_amp=0.4, out_prefix="T_VKI_DwarfFlag"),
})
