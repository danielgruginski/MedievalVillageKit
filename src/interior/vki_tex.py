# ===================== VKI interior textures (docs/history/interior_design/INTERIOR_SPEC.md §4.2) =====================
# Text vki_tex (src/interior/vki_tex.py). Executed on demand, never by vki_ns():
#   g={}
#   for t in ("vk_tex","vk_texgen","vk_tex2","vk_mat","vki_tex","vki_textiles"): exec(bpy.data.texts[t].as_string(),g)
#   g["vki_tex_run"]("T_VKI_Boards_NS")          # exactly ONE generator per MCP call (10-60 s each)
#   g["vki_tex_stats"]("T_VKI_Boards_NS")        # size / mean luma of the stored _BC
# Rules: copies of the exterior generators, never edits, so exterior textures stay bit-identical; paint at S=2048 and
# store 1024 via down2 (Ash: 1024 -> 512); vki_write_set writes + packs only _BC/_N/_R (files in vk_tex's TEXDIR), with
# the cavity AO folded into the albedo. No moss, no lichen, no cracks (thin dark lines read as hairs).
# Every top-level name starts with vki_/VKI_ (test T18); nothing is imported at top level: np, math, os, json, bpy and the
# exterior helpers (grid fbm blur smooth voronoi normal_from_height cavity_ao painted_light write_map draw_segments wrapd
# lerp smin down2 hx luma f32 / ramp3 / stone_layout paint_form_light _pal _fpal ST_HI ST_SH ST_MO FIELD_PAL _stamp_domes
# voronoi_edge2) come from the namespace the exterior texts were executed into.
# The M_VKI_* materials are built by vki_core's vki_apply_mats() from these images, by name.

VKI_AO = ((2, 6, 18), (2.0, 1.5, 0.8), 0.45)      # cavity_ao radii / weights / floor for every interior set


def vki_write_set(prefix, albedo, height, rough, depth_m, tile_m, ao=None, ao_in_albedo=0.35):
    """write + pack _BC (cavity AO folded in), _N (OpenGL Y+, slope in metres from depth_m / tile_m) and _R only"""
    if ao is None: ao = cavity_ao(height, *VKI_AO)
    bc = np.clip(albedo * (1 - ao_in_albedo + ao_in_albedo * ao)[..., None], 0, 1).astype(f32)
    write_map(prefix + "_BC", bc)
    write_map(prefix + "_N", normal_from_height(height, depth_m, tile_m) * 0.5 + 0.5, True)
    write_map(prefix + "_R", np.clip(rough, 0, 1).astype(f32), True)
    im = bpy.data.images.get(prefix + "_BC")
    if im is not None:
        im["vki_tile_m"] = float(tile_m); im["vki_depth_m"] = float(depth_m)
    return bc


def vki_tex_stats(prefix):
    """size and mean Rec.709 luma (display values) of the stored _BC"""
    im = bpy.data.images[prefix + "_BC"]; W, H = im.size
    a = np.empty(W * H * 4, f32); im.pixels.foreach_get(a); a = a.reshape(H, W, 4)[..., :3]
    return dict(size=(W, H), luma=round(float(luma(a).mean()), 4), rgb=[round(float(v), 4) for v in a.reshape(-1, 3).mean(0)],
                packed=im.packed_file is not None)


def vki_cast_shadow(hm, px, n=12, slope=0.8, soft=0.002):
    """painted drop shadow for the kit light (from +V, slightly left): hm in metres. 1 where a taller texel lies up-image"""
    occ = np.zeros_like(hm)
    for k in range(1, n + 1): occ = np.maximum(occ, np.roll(hm, (k, int(round(0.15 * k))), (0, 1)) - hm - k * px * slope)
    return blur(smooth(0, soft, occ), 1.2)


def vki_strands(col, h, items, nseg=5, pk=0.1):
    """paint tapered, slightly bowed strands (rushes, straw) in place; tileable.
    items: (x0, y0, ang, L, w, bend, c0, c1, lv) in px; bend = bow as a fraction of L; c0 root / c1 tip colour; lv = height
    level of the strand. Height: max(h, lv + pk * round cross-section). Later items lie on top. col may be None."""
    S = h.shape[0]; offs = (-S, 0, S)
    ts = np.linspace(0, 1, nseg + 1)
    for (x0, y0, ang, L, w, bend, c0, c1, lv) in items:
        dx, dy = math.cos(ang), math.sin(ang); nx, ny = -dy, dx
        bo = bend * L * 4 * ts * (1 - ts)
        P = np.stack([x0 + dx * L * ts + nx * bo, y0 + dy * L * ts + ny * bo], 1)
        W = w * (0.3 + 0.7 * np.sqrt(np.sin(np.pi * np.clip(ts, 0.03, 0.97))))
        c0 = np.asarray(c0, f32); c1 = np.asarray(c1, f32)
        for i in range(nseg):
            ax, ay = P[i]; bx, by = P[i + 1]; wa, wb = W[i], W[i + 1]; r = max(wa, wb) * 0.5 + 1.5
            ex, ey = bx - ax, by - ay; L2 = ex * ex + ey * ey + 1e-6
            for ox in offs:
                for oy in offs:
                    lx = int(max(0, math.floor(min(ax, bx) + ox - r))); hx_ = int(min(S, math.ceil(max(ax, bx) + ox + r)))
                    ly = int(max(0, math.floor(min(ay, by) + oy - r))); hy_ = int(min(S, math.ceil(max(ay, by) + oy + r)))
                    if lx >= hx_ or ly >= hy_: continue
                    yy, xx = np.mgrid[ly:hy_, lx:hx_].astype(f32)
                    qx = xx + 0.5 - (ax + ox); qy = yy + 0.5 - (ay + oy)
                    t = np.clip((qx * ex + qy * ey) / L2, 0, 1); d = np.hypot(qx - t * ex, qy - t * ey)
                    ww = wa + (wb - wa) * t
                    m = np.clip(ww * 0.5 - d + 0.5, 0, 1)
                    if not m.any(): continue
                    prof = np.sqrt(np.clip(1 - (2 * d / np.maximum(ww, 1e-3)) ** 2, 0, 1))
                    hw = h[ly:hy_, lx:hx_]; np.maximum(hw, m * (lv + pk * prof), out=hw)
                    if col is not None:
                        tt = (ts[i] + (ts[i + 1] - ts[i]) * t)[..., None]
                        cc = c0 + (c1 - c0) * tt
                        cw = col[ly:hy_, lx:hx_]; cw[:] = cw + (cc - cw) * m[..., None]


# ------------------------------------------------------------------ floorboards (Boards_NS / _EW, BoardsV)
def vki_board_layout(rng, nb, joints, T, min_sep=0.12, min_seg=0.45, tries=400):
    """butt-joint positions (v in 0..1, sorted) for each of nb boards. Joints of neighbouring boards (also of the last
    and the first board, which meet across the tile edge) are >= min_sep m apart; redraws until that holds"""
    if joints <= 0: return [np.zeros(0, f32) for _ in range(nb)]
    def far(a, c): return float(np.abs(wrapd(a[:, None] - c[None, :])).min()) * T >= min_sep
    for _outer in range(100):
        J = []
        for b in range(nb):
            for _t in range(tries):
                seg = rng.uniform(0.5, 1.5, joints); seg = seg / seg.sum()
                if seg.min() * T < min_seg: continue
                j = np.sort((rng.uniform(0, 1) + np.concatenate([[0.0], np.cumsum(seg)[:-1]])) % 1)
                if b > 0 and not far(j, J[-1]): continue
                if b == nb - 1 and not far(j, J[0]): continue
                J.append(j.astype(f32)); break
            else:
                break
        if len(J) == nb: return J
    raise RuntimeError("vki_board_layout: no layout found")


def vki_gen_floorboards(S=2048, seed=611, T=3.0, depth=0.02, nb=12, joints=3, orient="NS", tone=0.0, knot_p=0.20,
                        grey_p=0.08, scrub=0.22, wob=0.0005, gap=(0.0035, 0.0075), out_prefix="T_VKI_Boards_NS", write=True):
    """scrubbed oak boards 0.25 m wide (nb per tile) with `joints` butt joints per board per tile, 8 mm treenails only at
    the joints, knots on knot_p of the segments, grey_p old-grey segments. The layout is built for boards running along
    V (NS) and transposed for EW before painting, so the painted light stays on +V for both. joints=0 gives full-length
    boards (BoardsV, the Board wall family) with ~1 small knot per board instead. scrub = share of lye-washed grey-blond
    mixed into the oak ramp; wob = edge straightness noise (m); gap = edge-distance ramp of the board joints (m)."""
    rng = np.random.default_rng(seed); px = T / S; bw = T / nb; fs = T / 1.5
    J = vki_board_layout(rng, nb, joints, T)
    x, y = grid(S); V = (1 - y).astype(f32)
    xe = (x + wob / T * fbm(S, 2.5, seed + 9, fmin=2 * fs, fmax=10 * fs)) % 1              # sawn edges, not ruler-straight
    bi = np.minimum((xe * nb).astype(np.int32), nb - 1); fu = ((xe * nb) % 1).astype(f32); del x, y, xe
    nj = max(joints, 1); nseg = nb * nj
    if joints > 0:
        Jm = np.stack(J)
        rel = ((V[..., None] - Jm[bi]) % 1).astype(f32)                 # height above each joint of this board (cyclic)
        k = rel.argmin(-1).astype(np.int32)
        dj = (np.minimum(rel, 1 - rel).min(-1) * T).astype(f32); del rel
        seglen = ((np.roll(Jm, -1, 1) - Jm) % 1).astype(f32); seglen[seglen <= 0] = 1.0
    else:
        Jm = np.zeros((nb, 1), f32); k = np.zeros((S, S), np.int32); dj = np.full((S, S), 9.0, f32); seglen = np.ones((nb, 1), f32)
    seg = bi * nj + k; del k, V
    tint = rng.uniform(0.88, 1.08, nseg).astype(f32)
    grey = np.zeros(nseg, f32); ng = int(round(grey_p * nseg))
    if ng:                                                  # old-grey segments on boards at least 2 apart (no clusters)
        order = rng.permutation(nseg); used = []
        for s_ in order:
            b_ = int(s_) // nj
            if all(min((b_ - u_) % nb, (u_ - b_) % nb) >= 2 for u_ in used):
                grey[s_] = 1.0; used.append(b_)
            if len(used) >= ng: break
    phase = rng.uniform(0, 1, nseg).astype(f32)
    tilt = rng.uniform(-0.03, 0.03, nseg).astype(f32); slope = rng.uniform(-0.05, 0.05, nseg).astype(f32)
    rs = rng.integers(0, S, nseg); cs = rng.integers(0, S, nseg)
    G = fbm(S, 1.8, seed, fmin=4 * fs, ay=12); G2 = fbm(S, 1.5, seed + 1, fmin=30 * fs, ay=18)
    rows = np.arange(S)[:, None]; cols = np.arange(S)[None, :]
    ri = (rows + rs[seg]) % S; ci = (cols + cs[seg]) % S
    Gs = G[ri, ci]; G2s = G2[ri, ci]; del G, G2, ri, ci
    # knots
    kcore = np.zeros((S, S), f32); kring = np.zeros((S, S), f32); khalo = np.zeros((S, S), f32)
    kl = []
    if joints > 0:
        for s_ in rng.choice(nseg, int(round(knot_p * nseg)), replace=False):
            b_, k_ = divmod(int(s_), nj)
            kl.append((b_, float((Jm[b_, k_] + rng.uniform(0.2, 0.8) * seglen[b_, k_]) % 1), 1.0))
    else:
        for b_ in range(nb):
            for _ in range(int(rng.integers(0, 3))): kl.append((b_, float(rng.uniform(0, 1)), 0.7))
    for (b_, kv, ksz) in kl:
        rx = rng.uniform(0.0075, 0.0125) * ksz; ry = 1.6 * rx; kf = rng.uniform(0.3, 0.7)
        cxp = (b_ + kf) / nb * S; cyp = (1 - kv) * S; R = int(3.0 * ry / px) + 2
        ir = np.arange(int(cyp) - R, int(cyp) + R + 1); ic = np.arange(int(cxp) - R, int(cxp) + R + 1)
        yy = ((ir + 0.5 - cyp) * px)[:, None]; xx = ((ic + 0.5 - cxp) * px)[None, :]
        d = np.sqrt((xx / rx) ** 2 + (yy / ry) ** 2).astype(f32)
        ix = np.ix_(ir % S, ic % S)
        kcore[ix] = np.maximum(kcore[ix], smooth(1.0, 0.7, d))
        kring[ix] = np.maximum(kring[ix], np.exp(-((d - 1.15) / 0.15) ** 2))
        khalo[ix] = np.maximum(khalo[ix], np.exp(-(d / 2.4) ** 2))
    # treenails: two per board end at every butt joint, 8 mm, 35 mm from the joint
    if joints > 0:
        dpu = np.minimum(np.abs(fu - 0.3), np.abs(fu - 0.7)) * bw
        peg = smooth(0.004 + px, 0.004 - px, np.sqrt(dpu * dpu + (dj - 0.035) ** 2)).astype(f32); del dpu
    else:
        peg = np.zeros((S, S), f32)
    de = (np.minimum(fu, 1 - fu) * bw).astype(f32)
    gapm = (smooth(gap[0], gap[1], de) * smooth(0.0025, 0.006, dj)).astype(f32); del dj
    # arris bands along the long edges: the left edge faces the light (Ln.x < 0), the right edge turns away. After the EW
    # transpose the left edge becomes the top edge, which faces +V: still lit.
    arl = (smooth(gap[0], gap[0] + 0.002, fu * bw) * (1 - smooth(gap[1], gap[1] + 0.005, fu * bw))).astype(f32)
    arr_ = (smooth(gap[0], gap[0] + 0.002, (1 - fu) * bw) * (1 - smooth(gap[1], gap[1] + 0.005, (1 - fu) * bw))).astype(f32); del de
    bow = 1 - 0.3 * (2 * fu - 1) ** 2
    top = 0.55 + 0.25 * bow + 0.05 * Gs + 0.02 * G2s + tilt[seg] + slope[seg] * (fu - 0.5) - 0.05 * kcore - 0.03 * peg
    h = (gapm * top + (1 - gapm) * 0.08).astype(f32); del top, bow
    arcs = 0.03 * np.sin(2 * np.pi * (1.3 * fu + 0.25 * Gs + phase[seg]))
    t = np.clip(0.58 + tone + 0.12 * Gs + 0.05 * G2s + arcs - 0.08 * khalo, 0, 1); del arcs
    col = ramp3(t, hx("#3A2414"), hx("#74492A"), hx("#A07448"), 0.5) * tint[seg][..., None]; del t
    col = lerp(col, luma(col)[..., None] * np.array([1.06, 1.0, 0.90], f32), scrub)            # scrubbed: less orange
    col = lerp(col, luma(col)[..., None] * np.array([1.02, 1.0, 0.96], f32) * 1.04, 0.25 * grey[seg][..., None])
    col = col * (1 + 0.10 * arl - 0.12 * arr_)[..., None]; del arl, arr_
    col = lerp(col, col * 0.72, 0.6 * kring[..., None]); col = lerp(col, hx("#40271A"), 0.85 * kcore[..., None])
    col = lerp(col, hx("#4A3020") * (1 + 0.1 * G2s)[..., None], 0.9 * peg[..., None])
    col = lerp(np.broadcast_to(hx("#2A1C12"), col.shape), col, gapm[..., None]).astype(f32)
    R = (0.78 + 0.04 * Gs + 0.12 * (1 - gapm)).astype(f32)
    del Gs, G2s, kcore, kring, khalo, peg, fu, bi, seg
    if orient == "EW":
        col = np.ascontiguousarray(col.swapaxes(0, 1)); h = np.ascontiguousarray(h.T); R = np.ascontiguousarray(R.T)
    col, _ = paint_form_light(col, h, depth, T, hig=0.12, log=0.18, post=0.25)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(R)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ dressed blocks (Flagstone, AshlarIn)
def vki_gen_blocks(S=2048, seed=15, T=3.0, nrow=6, blocks=(4, 6, 5, 4, 6, 5), pal=("S1", "S2", "S4"), mortar="#5E564C",
                   chip=0.5, depth=0.025, gap=0.0045, wjit=0.15, min_sep=0.12, tone=1.0, mtone=1.0, cham_m=0.04,
                   dnoise=0.0035, dfmax=27, hig=0.13, log=0.19, post=0.25, out_prefix="T_VKI_Flagstone", write=True,
                   rows=None, vrange=(0.92, 1.06), warm_amp=1.0):
    """copy of vk_tex2.gen_ashlar (v2) made general: nrow courses of T/nrow, blocks[r] blocks in course r (widths
    jittered by +-wjit), joints of adjacent courses >= min_sep m apart, palette keys pal, mortar colour, chip amount.
    gap = half the joint width in metres; cham_m = width of the rounded arris; dnoise / dfmax = amplitude (m) and top
    frequency (per metre) of the joint-line wander. tone / mtone scale the stone / mortar colour.
    Fix r1 (defaults keep the old output bit-identical): rows = relative course heights (unequal courses, e.g. for
    hand-laid flags), vrange = per-stone value range, warm_amp = scale of the per-stone warm / cool shift."""
    rng = np.random.default_rng(seed); px = T / S
    nrow = len(blocks)
    if rows is not None:
        rh = np.array(rows, np.float64); rh = rh / rh.sum()
        rb = np.concatenate([[0.0], np.cumsum(rh)]); rb[-1] = 1.0
    else:
        rh = rb = None
    for _try in range(2000):
        Wd = []
        for r in range(nrow):
            w = (1 + rng.uniform(-wjit, wjit, blocks[r])) / blocks[r]; Wd.append(w / w.sum())
        off = rng.uniform(0, 1, nrow)
        E = [(np.concatenate([[0.0], np.cumsum(Wd[r])[:-1]]) - off[r]) % 1 for r in range(nrow)]
        sep = min(float(np.abs(wrapd(E[r][:, None] - E[(r + 1) % nrow][None, :])).min()) for r in range(nrow)) * T
        if sep >= min_sep: break
    x, y = grid(S)
    X = (x + fbm(S, 3.5, seed + 1) * 0.004 / T) % 1; Y = (y + fbm(S, 3.5, seed + 2) * 0.004 / T) % 1; del x, y
    if rb is None:
        row = np.minimum((Y * nrow).astype(np.int32), nrow - 1); v = ((Y * nrow) % 1).astype(f32); del Y
        rowh = np.full(nrow, T / nrow, f32)
    else:
        row = np.clip(np.searchsorted(rb, Y, side="right") - 1, 0, nrow - 1).astype(np.int32)
        v = np.clip((Y - rb[row]) / rh[row], 0, 1).astype(f32); del Y
        rowh = (rh * T).astype(f32)
    dx = np.zeros((S, S), f32); u = np.zeros((S, S), f32); sid = np.zeros((S, S), np.int32)
    base_id = np.concatenate([[0], np.cumsum(blocks)[:-1]]).astype(np.int32)
    for r in range(nrow):
        m = row == r; xo = (X[m] + off[r]) % 1; e = np.concatenate([[0.0], np.cumsum(Wd[r])])
        c = np.clip(np.searchsorted(e, xo, side="right") - 1, 0, blocks[r] - 1)
        uu = (xo - e[c]) / Wd[r][c]; u[m] = uu; dx[m] = np.minimum(uu, 1 - uu) * Wd[r][c] * T; sid[m] = base_id[r] + c
    del X
    dy = np.minimum(v, 1 - v) * rowh[row]
    d = (np.minimum(dx, dy) + dnoise * fbm(S, 2.6, seed + 3, fmin=2 * T, fmax=dfmax * T)).astype(f32); del dx, dy
    mask = smooth(gap, gap + 0.003, d); cham = smooth(gap, gap + cham_m, d)
    nid = int(sum(blocks)); tv = rng.uniform(-1, 1, (nid, 2)).astype(f32)
    chipm = smooth(1.5, 2.0, fbm(S, 2.6, seed + 5, fmin=2 * T, fmax=20 * T)) * (1 - smooth(gap + 0.006, gap + 0.06, d)) * chip
    hs = (0.45 + 0.42 * cham + (tv[sid, 0] * (u - 0.5) + tv[sid, 1] * (v - 0.5)) * 0.08 * cham
          + 0.004 * fbm(S, 1.8, seed + 4, fmin=20 * T, fmax=100 * T) * cham - 0.3 * chipm)
    h = blur(np.clip(mask * hs + (1 - mask) * 0.12, 0, 1), 1.4).astype(f32); del hs, cham, u, v
    keys = list(pal); P = np.stack([_pal(k_) for k_ in keys])
    pid = rng.integers(0, len(keys), nid); val = rng.uniform(vrange[0], vrange[1], nid).astype(f32); warm = rng.uniform(-1, 1, nid).astype(f32)
    brgb = (P[pid] * val[:, None] * (1 + warm_amp * warm[:, None] * np.array([0.02, 0.0, -0.025], f32)) * tone).astype(f32)
    base = brgb[sid] * (1 + 0.018 * fbm(S, 2.2, seed + 7, fmin=4 * T, fmax=23 * T, ax=2.5, angle=0.4))[..., None]
    mcol = hx(mortar) * mtone * (1 + 0.05 * fbm(S, 1.5, seed + 8, fmin=7 * T, fmax=50 * T))[..., None]
    col = lerp(mcol, base, mask[..., None]).astype(f32); del base, mcol, sid
    col, n_s = paint_form_light(col, h, depth, T, hig=hig, log=log, post=post)
    dp = d - gap
    band = (smooth(0, 0.003, dp) - smooth(0.008, 0.016, dp)).astype(f32)
    rim = (band * smooth(0.2, 0.5, n_s[..., 1])).astype(f32)
    col = lerp(col * (1 + 0.08 * rim[..., None]), hx(ST_HI), 0.30 * rim[..., None])
    under = (band * smooth(0.15, 0.45, -n_s[..., 1]))[..., None]; col = lerp(col * (1 - 0.2 * under), hx(ST_SH), 0.22 * under)
    col = lerp(col, lerp(col, luma(col)[..., None], 0.5) * 1.1, 0.6 * chipm[..., None])
    col *= (1 + 0.03 * fbm(S, 2.0, seed + 50, fmin=1.5, fmax=5))[..., None]
    rough = np.clip(0.8 + 0.04 * fbm(S, 2.4, seed + 9, fmin=6) + 0.12 * (1 - mask) - 0.05 * rim, 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(rough)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ rustic flags in packed earth (FlagRustic)
def vki_flag_seeds(seed, T=3.0, rows=(0.38, 0.55), cols=(0.45, 0.75), aspect=1.0, pk_frac=0.08):
    """copy of vk_tex2.fieldstone_seeds with the row / column pitch, aspect and packer share as parameters"""
    rng = np.random.default_rng(seed)
    rw = []; s_ = 0
    while s_ < T: p = rng.uniform(*rows); rw.append(p); s_ += p
    rw = np.array(rw) * T / s_; y0 = np.concatenate([[0], np.cumsum(rw)])
    pts = []
    for r in range(len(rw)):
        xs = []; s_ = 0
        while s_ < T: p = rng.uniform(*cols); xs.append(p); s_ += p
        xs = np.array(xs) * T / s_; xc = np.concatenate([[0], np.cumsum(xs)])[:-1] + xs / 2 + rng.uniform(0, T)
        for i, xx in enumerate(xc):
            pts.append(((xx + rng.uniform(-0.25, 0.25) * xs[i]) % T / T, ((y0[r] + rw[r] / 2 + rng.uniform(-0.15, 0.15) * rw[r]) % T) / T))
    pts = np.array(pts, f32)
    s4 = 256; x, y = grid(s4); F1, F2, ID = voronoi(x, y, pts, 1.0, aspect)
    n = len(pts); ang_x = 2 * np.pi * x; ang_y = 2 * np.pi * y
    cx = np.arctan2(np.bincount(ID.ravel(), np.sin(ang_x).ravel(), n), np.bincount(ID.ravel(), np.cos(ang_x).ravel(), n)) / (2 * np.pi) % 1
    cy = np.arctan2(np.bincount(ID.ravel(), np.sin(ang_y).ravel(), n), np.bincount(ID.ravel(), np.cos(ang_y).ravel(), n)) / (2 * np.pi) % 1
    pts = np.stack([cx, cy], 1).astype(f32)
    F1, F2, ID = voronoi(x, y, pts, 1.0, aspect)
    a = ID; b = np.roll(ID, -1, 1); c = np.roll(ID, -1, 0); d = np.roll(b, -1, 0)
    trip = ((a != b) & (a != c) & (b != c)) | ((a != b) & (a != d) & (b != d))
    ty, tx = np.nonzero(trip); cand = np.stack([(tx + 1) / s4, (ty + 1) / s4], 1)
    rng.shuffle(cand); pk = []
    for q in cand:
        if len(pk) >= int(pk_frac * n): break
        if all(math.hypot(wrapd(q[0] - p[0]) * T, wrapd(q[1] - p[1]) * T) > 0.3 for p in pk): pk.append(q)
    w = np.concatenate([np.zeros(n, f32), np.full(len(pk), -(0.05 / T) ** 2, f32)])
    return np.concatenate([pts, np.array(pk, f32).reshape(-1, 2)]).astype(f32), w, n


def vki_gen_flagrustic(S=2048, seed=33, T=3.0, depth=0.035, aspect=1.0, rows=(0.38, 0.55), cols=(0.45, 0.75),
                       prot=(0.010, 0.018), joint="#4A3A2C", tone=0.72, calm=0.4, gapw=(0.016, 0.004), pk_frac=0.0,
                       out_prefix="T_VKI_FlagRustic", write=True):
    """copy of vk_tex2.gen_fieldstone without moss or lichen: flat, irregular flags (rows x cols pitch in metres,
    protrusion prot) set in packed-earth joints with pebbles; tone scales the stone palette for floor luma, calm pulls
    every flag's colour toward the mean (no standout flag), gapw = (half joint width, its variation) in metres,
    pk_frac = share of small packer stones (0: their triangles read as a repeating mark on a floor)."""
    rng = np.random.default_rng(seed + 7); px = T / S
    pts, w, nmain = vki_flag_seeds(seed, T, rows, cols, aspect, pk_frac=pk_frac)
    N = len(pts)
    x, y = grid(S)
    ID, E1, E2, ox, oy = voronoi_edge2(x, y, pts, w, 1.0, aspect)
    del x, y
    E1m = E1 * T; E2m = E2 * T; del E1, E2
    kk = rng.uniform(0.02, 0.05, N).astype(f32)
    d = smin(E1m, E2m, kk[ID]) + 0.004 * fbm(S, 2.0, seed + 3, fmin=8, fmax=40); del E1m, E2m
    g = np.clip(gapw[0] + gapw[1] * fbm(S, 2.0, seed + 4, fmin=6, fmax=30), 0.6 * gapw[0], 1.4 * gapw[0]).astype(f32)
    dp = (d - g).astype(f32); stone = smooth(-0.0015, 0.0015, dp); del d
    area = np.bincount(ID.ravel(), minlength=N).astype(f32) * px * px
    rb = np.clip(0.3 * np.sqrt(area / np.pi), 0.03, 0.06).astype(f32)
    pr = rng.uniform(prot[0], prot[1], N).astype(f32); pr[nmain:] = rng.uniform(0.6 * prot[0], 0.6 * prot[1], N - nmain)
    tx_, ty_ = rng.uniform(-0.012, 0.012, (2, N)).astype(f32)
    lx = ox * T; ly = -oy * T; del ox, oy
    th = np.radians(90 * np.arange(4)[None, :] + rng.uniform(-35, 35, (N, 4))).astype(f32)
    sk = rng.uniform(0.015, 0.03, (N, 4)).astype(f32); ak = rng.uniform(0.35, 0.75, (N, 4)).astype(f32); fs_ = rng.uniform(-1, 1, (N, 4)).astype(f32)
    Rst = np.sqrt(area / np.pi).astype(f32)
    best = np.full((S, S), np.inf, f32); kst = np.zeros((S, S), np.int8)
    for q in range(4):
        v = sk[ID, q] * (ak[ID, q] * Rst[ID] - (lx * np.cos(th[ID, q]) + ly * np.sin(th[ID, q])))
        m = v < best; best = np.where(m, v, best); kst[m] = q
    facet = np.minimum(0, best).astype(f32); del best
    fs_act = np.where(facet < -0.002, np.take_along_axis(fs_[ID], kst[..., None].astype(np.int64), -1)[..., 0], 0).astype(f32)
    hm = (0.002 + 0.0012 * fbm(S, 1.5, seed + 6, fmin=40)).astype(f32)
    gp = (0.0004 * fbm(S, 1.8, seed + 13, fmin=60, fmax=300)).astype(f32)
    hface = np.maximum(pr[ID] + tx_[ID] * lx + ty_[ID] * ly + facet + 0.004 * smooth(0, 0.1, dp) ** 0.7 + gp, hm + 0.006)
    sb = np.clip(dp / rb[ID], 0, 1); prof = 1 - (1 - sb) ** 2
    h = np.where(dp > 0, hm + (hface - hm) * prof, hm).astype(f32); gpp = (gp * prof * (dp > 0)).astype(f32); del hface, prof, sb, lx, ly, facet
    peb = np.zeros((S, S), f32); segs = []
    gapy, gapx = np.nonzero((dp[::8, ::8] < -0.004))
    sel = rng.choice(len(gapy), size=min(len(gapy), int(len(gapy) * 0.02)), replace=False)
    for i in sel:
        r_ = rng.uniform(0.004, 0.0075) / px; cx_, cy_ = gapx[i] * 8 + rng.uniform(0, 8), gapy[i] * 8 + rng.uniform(0, 8)
        segs.append((cx_, cy_, cx_ + rng.uniform(-0.3, 0.3) * r_, cy_ + rng.uniform(-0.2, 0.2) * r_, 2 * r_))
    if segs: peb = draw_segments(S, segs) * (1 - stone)
    h = np.maximum(h, peb * (0.006 - 0.002 * (1 - blur(peb, 2.0))))
    keys = list(FIELD_PAL.keys()); prb = np.array([FIELD_PAL[k_] for k_ in keys]); prb /= prb.sum()
    PAL = np.stack([_fpal(k_) for k_ in keys]) * tone
    pid = rng.choice(len(keys), N, p=prb)
    for i in range(nmain, N): pid[i] = keys.index("S6") if rng.random() < 0.5 else keys.index("S3")
    val = rng.uniform(0.9, 1.07, N).astype(f32); warm = rng.uniform(-1, 1, N).astype(f32)
    wm = np.stack([1 + 0.02 * warm, np.ones(N, f32), 1 - 0.025 * warm], 1)
    srgb = PAL[pid] * val[:, None] * wm
    srgb = lerp(srgb, srgb.mean(0, keepdims=True), calm)
    col = srgb[ID].astype(f32)
    col *= (1 + 0.035 * fs_act)[..., None]
    col *= (1 + 0.02 * fbm(S, 2.2, seed + 40, fmin=12, fmax=70, ax=2.5, angle=0.5))[..., None]
    speck_st = rng.random(N) < 0.30
    sp = fbm(S, 0.5, seed + 41, fmin=300)
    dark = (sp > 1.9) & speck_st[ID]; light_ = (sp < -1.9) & speck_st[ID]; del sp
    col = np.where(dark[..., None], lerp(col, hx("#5A5652") * tone, 0.8), col)
    col = np.where(light_[..., None], lerp(col, hx("#C9C3B6") * tone, 0.8), col); del dark, light_
    soil = hx(joint) * (1 + 0.06 * fbm(S, 1.8, seed + 15, fmin=10, fmax=200))[..., None]
    soil = lerp(soil, hx("#7A7066") * (0.85 + 0.3 * blur(peb, 1.5))[..., None], peb[..., None])
    col = lerp(soil, col, stone[..., None]).astype(f32); del soil
    col, n_s = paint_form_light(col, np.clip((h - gpp) / depth, 0, 1), depth, T, hig=0.14, log=0.18, post=0.25, ex=1.2)
    band = (smooth(0, 0.005, dp) - smooth(0.015, 0.03, dp)).astype(f32)
    rim = (band * smooth(0.20, 0.50, n_s[..., 1])).astype(f32)
    col = lerp(col * (1 + 0.08 * rim[..., None]), hx(ST_HI), 0.28 * rim[..., None])
    under = (band * smooth(0.15, 0.45, -n_s[..., 1]))[..., None]; col = lerp(col * (1 - 0.2 * under), hx(ST_SH), 0.22 * under)
    sh = vki_cast_shadow(h, px, n=16, slope=1.0, soft=0.004)[..., None]
    col = lerp(col * (1 - 0.35 * sh), hx(ST_SH), 0.2 * sh)
    col *= (1 + 0.03 * fbm(S, 2.0, seed + 50, fmin=1.5, fmax=5))[..., None]
    h01 = blur(np.clip(h / depth, 0, 1), 1.0)
    R = np.clip(0.86 * stone + 0.95 * (1 - stone) + 0.03 * fs_act - 0.05 * rim, 0.6, 0.98).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h01), down2(R)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ earth floor with strewn rushes (Earth, EarthSooty)
def vki_gen_earthfloor(S=2048, seed=456, T=3.0, depth=0.03, rushes=1.0, soot=0.0, out_prefix="T_VKI_Earth", write=True):
    """copy of vk_tex2.gen_dirt_v2 without grass: calm packed earth with a few clods and pebbles, strewn rushes
    (0.12-0.32 m long, 4-7 mm wide, with drop shadows) and strewing herbs. soot=1 adds charcoal specks, an ash haze and
    iron-scale flakes (the smithy floor)."""
    rng = np.random.default_rng(seed); px = T / S; a = (T / 4.0) ** 2; fs = T / 4.0; ar = (T / 1.5) ** 2
    lo = fbm(S, 2.6, seed, fmin=1.5, fmax=8); mid = fbm(S, 2.2, seed + 1, fmin=8 * fs, fmax=48 * fs)
    loose = smooth(0.3, 1.5, fbm(S, 2.4, seed + 2, fmin=2, fmax=10))          # 0 packed .. 1 loose
    col = lerp(hx("#6A4E35"), hx("#7C5E41"), (0.5 + 0.16 * lo)[..., None])            # calm: no 2 m patches
    col = col * (1 + 0.035 * mid[..., None])
    col = lerp(col, col * np.array([0.95, 0.96, 1.0], f32), 0.4 * (1 - loose)[..., None])
    items = []
    for _ in range(int(800 * a * 1.3)):
        cx, cy = rng.uniform(0, S, 2); l_ = loose[int(cy) % S, int(cx) % S]
        if rng.random() > 0.25 + 0.75 * l_: continue
        r = rng.uniform(0.018, 0.06) / px
        items.append((cx, cy, r * rng.uniform(0.85, 1.35), r * rng.uniform(0.5, 0.9), rng.uniform(0, math.pi), rng.uniform(0.08, 0.25) * (0.5 + 0.5 * l_)))
    Hc, Cc, _ = _stamp_domes(S, items, flat=0.8, irr=0.35, rng=rng); del Cc
    h = 0.35 + 0.03 * mid + 0.3 * blur(Hc, 2.0); del Hc
    g = fbm(S, 0.8, seed + 3, fmin=180 * fs, fmax=1000 * fs)
    lite = smooth(1.7, 2.4, g) * (0.5 + 0.5 * loose); dark = smooth(1.8, 2.6, -g); del g
    col = lerp(col, hx("#A88E68"), 0.5 * lite[..., None]); col = lerp(col, hx("#4E3624"), 0.45 * dark[..., None])
    h = h + 0.05 * lite - 0.04 * dark; del lite, dark
    peb = []
    for _ in range(int(620 * a * 0.35)):
        cx, cy = rng.uniform(0, S, 2)
        if rng.random() > 0.3 + 0.7 * loose[int(cy) % S, int(cx) % S]: continue
        big = rng.random() < 0.03; r = (rng.uniform(0.028, 0.045) if big else rng.uniform(0.010, 0.022)) / px
        peb.append((cx, cy, r * rng.uniform(0.95, 1.35), r * rng.uniform(0.6, 0.9), rng.uniform(0, math.pi), 0.5 if big else 0.4))
    Hp, Cp, IDp = _stamp_domes(S, peb, flat=0.3, irr=0.28, rng=rng)
    if peb:
        PAL = np.stack([hx(c_) for c_ in ("#9A9082", "#A89E8C", "#8C8174", "#A0876A", "#B2A48A", "#8A7258", "#A6906F", "#7D776E")])
        pid = rng.integers(0, len(PAL), len(peb)); val = rng.uniform(0.85, 1.0, len(peb)).astype(f32)
        buried = rng.uniform(0.1, 0.5, len(peb)).astype(f32)
        ide = np.maximum(IDp, 0)
        pc = (PAL[pid] * val[:, None])[ide] * (1 + 0.06 * fbm(S, 1.5, seed + 4, fmin=60))[..., None]
        pc = lerp(pc, col, (buried[ide] * (1 - smooth(0.1, 0.5, Hp / 0.5)))[..., None])
        col = lerp(col, pc, Cp[..., None]); h = h + 0.45 * Hp; del pc, ide
    del Hp, IDp
    if soot > 0:
        haze = smooth(-1.0, 1.2, fbm(S, 2.4, seed + 20, fmin=3, fmax=16))
        col = col * (1 - 0.10 * soot)
        col = lerp(col, hx("#5E5954") * (1 + 0.05 * mid)[..., None], (0.36 * soot * (0.7 + 0.3 * haze))[..., None]); del haze
        sp = []
        for _ in range(int(250 * soot * ar)):
            cx, cy = rng.uniform(0, S, 2); r = rng.uniform(0.002, 0.006) / px
            sp.append((cx, cy, r, r * rng.uniform(0.6, 1.0), rng.uniform(0, math.pi), 0.15))
        Hs, Cs, _ = _stamp_domes(S, sp, flat=0.4, irr=0.4, rng=rng)
        col = lerp(col, hx("#25211F"), 0.9 * Cs[..., None]); h = h + 0.2 * Hs; del Hs, Cs
        fl = []
        for _ in range(int(120 * soot * ar)):
            cx, cy = rng.uniform(0, S, 2); r = rng.uniform(0.0015, 0.003) / px
            fl.append((cx, cy, r, r * rng.uniform(0.5, 0.9), rng.uniform(0, math.pi), 0.12))
        Hf, Cf, _ = _stamp_domes(S, fl, flat=0.15, irr=0.5, rng=rng)
        col = lerp(col, hx("#4D4A48"), 0.85 * Cf[..., None]); h = h + 0.15 * Hf; del Hf, Cf
    col = np.ascontiguousarray(col, f32); h = np.ascontiguousarray(h, f32)
    if rushes > 0:
        # cut rushes lie in loose bundles of 1-4 near-parallel stems: a bundle reads as a pale 1-3 cm strip at game
        # distance, where a lone 5 mm stem would read as a hair. Pale, low relief and a short soft shadow.
        xs, ys = grid(256); cl = rng.uniform(0, 1, (12, 2)); _, _, IDc = voronoi(xs, ys, cl); ang_c = rng.uniform(0, math.pi, 12)
        its = []
        for _ in range(int(round(110 * rushes * ar / 2.5))):
            cx, cy = rng.uniform(0, S, 2)
            a0 = ang_c[IDc[int(cy / S * 256) % 256, int(cx / S * 256) % 256]] + rng.uniform(-0.5, 0.5)
            u_ = rng.random()
            if u_ < 0.15: cb = hx("#A3A866")
            elif u_ < 0.25: cb = hx("#A68C62")
            else: cb = lerp(hx("#B8A466"), hx("#D6C488"), rng.random())
            Lb = rng.uniform(0.12, 0.32)
            for q in range(int(rng.integers(1, 5))):
                a1 = a0 + rng.uniform(-0.08, 0.08); off = (q - 1.5) * rng.uniform(0.006, 0.011) / px
                L = Lb * rng.uniform(0.8, 1.1) / px; w = rng.uniform(0.004, 0.007) / px
                sx = cx - math.sin(a0) * off + math.cos(a0) * rng.uniform(-0.03, 0.03) / px
                sy = cy + math.cos(a0) * off + math.sin(a0) * rng.uniform(-0.03, 0.03) / px
                c0 = cb * rng.uniform(0.94, 1.05); c1 = c0 * rng.uniform(0.95, 1.08)
                its.append((sx - math.cos(a1) * L / 2, sy - math.sin(a1) * L / 2, a1, L, w, rng.uniform(-0.06, 0.06), c0, c1,
                            0.50 + 0.02 * rng.random()))
        vki_strands(col, h, its, nseg=5, pk=0.04)
        segs = [[], [], []]
        for _ in range(int(round(12 * rushes * ar))):
            bx, by = rng.uniform(0, S, 2); k_ = int(rng.integers(0, 3))
            for _d in range(int(rng.integers(3, 7))):
                fx, fy = bx + rng.normal(0, 0.012 / px), by + rng.normal(0, 0.012 / px); r = rng.uniform(0.0015, 0.0025) / px
                segs[k_].append((fx, fy, fx + 0.01, fy, 2 * r))
        for k_, c_ in enumerate(("#D2C79E", "#B4A6C0", "#8A9460")):
            if segs[k_]:
                m = draw_segments(S, segs[k_]); col = lerp(col, hx(c_), 0.9 * m[..., None]); h = np.maximum(h, m * 0.66)
    h = np.clip(h, 0, 1).astype(f32)
    col, _ = paint_form_light(np.clip(col, 0, 1).astype(f32), h, depth, T, hig=0.14, log=0.16, post=0.25, ex=1.5)
    sh = vki_cast_shadow(h * depth, px, n=8, slope=1.0)[..., None]
    col = lerp(col * (1 - 0.15 * sh), hx(ST_SH), 0.08 * sh); del sh
    R = np.clip(0.92 - 0.05 * (1 - loose) - 0.10 * Cp, 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(R)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ limewash (PlasterIn)
def vki_gen_plaster_in(S=2048, seed=23, T=1.5, depth=0.015, blot=0.2, tone=0.88, out_prefix="T_VKI_PlasterIn", write=True):
    """copy of vk_texgen.gen_plaster with no cracks and no brick patches; blot = strength of the soft darker blots
    (0.3 outdoors); tone brings the limewash into 0.60-0.80 luma. Even: the blots and highlights live at 0.3-0.5 m
    (not the exterior's 1 m, which repeats visibly on a 1.5 m tile), the relief is soft trowel undulation, and the
    fine lime grain is only a colour speckle (no relief), so the wall reads smooth."""
    lumps = fbm(S, 3.2, seed, fmin=2); strokes = fbm(S, 2.8, seed + 1, fmin=3, fmax=60, ax=3.5)
    trowel = fbm(S, 2.6, seed + 3, fmin=5, fmax=40, ax=2.5, angle=0.35)
    hp = 0.62 + 0.05 * lumps + 0.025 * strokes + 0.018 * trowel
    h = blur(np.clip(hp, 0, 1), 3.0).astype(f32); del hp
    base = np.array([0.93, 0.85, 0.67], f32) * tone
    col = base * (1 + 0.015 * lumps[..., None] + 0.022 * trowel[..., None])
    bl = smooth(0.4, 2.0, fbm(S, 3.0, seed + 6, fmin=3, fmax=30))
    col = col * (1 - blot * bl[..., None]) + np.array([0.88, 0.76, 0.56], f32) * tone * blot * bl[..., None]
    hi = smooth(0.6, 2.1, fbm(S, 3.0, seed + 14, fmin=3, fmax=30))
    col = col * (1 - 0.18 * hi[..., None]) + np.array([0.95, 0.91, 0.80], f32) * tone * 0.18 * hi[..., None]
    col = col * (1 + 0.012 * fbm(S, 1.0, seed + 2, fmin=120, fmax=600))[..., None]            # lime grain (colour only)
    del bl, hi, lumps, strokes, trowel
    col, _ = paint_form_light(col.astype(f32), h, depth, T, hig=0.08, log=0.12, post=0.0)
    rough = np.clip(0.92 + 0.03 * fbm(S, 2.4, seed + 8, fmin=6), 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(rough)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ coursed rubble (StoneIn + _stones.json)
def vki_gen_stone_in(S=2048, seed=10, T=1.5, L=None, mortar="#857B6C", out_prefix="T_VKI_StoneIn", write=True,
                     GAP=0.0095, GRAIN=0.00035, PITS=0.001, HIG=0.14, LOG=0.20, POST=0.25, CAST=0.35, CALM=0.65, json_min=0.08):
    """copy of vk_tex2.gen_stone: courses = len(L['H']) (not 7), no cracks, no lichen, no moss, own mortar colour,
    lighter painted light, stone colours pulled CALM toward their mean (the layout's contrasting neighbours would make
    the 1.5 m repeat obvious). Writes <out_prefix>_stones.json with the stones of w*h > json_min m^2 (pop-out stones)."""
    import time; t0 = time.time()
    if L is None: L = stone_layout(seed, T, lacing=False, NC=4)
    NC = len(L['H']); HN = 0.06
    rng = np.random.default_rng(seed + 500)
    stones, packers, courses = L['stones'], L['packers'], L['courses']; N = L['N']; P = len(packers); NS = N + P
    y0, yc = L['y0'], L['yc']; px = T / S
    x, y = grid(S); X = (x * T).astype(f32); Y = (T * (1 - y)).astype(f32); del x, y
    xs = (np.arange(S) * T / S).astype(f32)
    B = np.stack([y0[r] + np.interp(xs, L['beds'][r][0], L['beds'][r][1], period=T) for r in range(NC)] +
                 [y0[0] + np.interp(xs, L['beds'][0][0], L['beds'][0][1], period=T) + T]).astype(f32)
    B0 = B[0][None, :]; Yw = (B0 + (Y - B0) % T).astype(f32); del Y
    R = np.zeros((S, S), np.int32)
    for j in range(1, NC): R += (Yw >= B[j][None, :])
    colsI = np.broadcast_to(np.arange(S)[None, :], (S, S))
    dB = (Yw - B[R, colsI] - 0.0025).astype(f32); dT = (B[R + 1, colsI] - Yw - 0.0025).astype(f32)
    lab = np.zeros((S, S), np.int32); dL = np.zeros((S, S), f32); dR = np.zeros((S, S), f32); lx = np.zeros((S, S), f32); ly = np.zeros((S, S), f32)
    for r, c in enumerate(courses):
        m = R == r; Xm = X[m]; Ym = Yw[m]
        s = (wrapd(Xm[:, None] - c['J'][None, :] - c['t'][None, :] * (Ym[:, None] - yc[r]), T) / np.sqrt(1 + c['t'] ** 2)[None, :]).astype(f32)
        sp = np.where(s >= 0, s, np.inf); kL = sp.argmin(1); dL[m] = sp.min(1)
        dR[m] = np.where(s < 0, -s, np.inf).min(1)
        lab[m] = L['base'][r] + kL
        cx = (c['J'][kL] + c['w'][kL] / 2) % T; lx[m] = wrapd(Xm - cx, T); ly[m] = Ym - yc[r]
        del s, sp
    del X, Yw, R
    def arr(fn, dflt=0.0):
        a_ = np.full(NS, dflt, f32)
        for i, s_ in enumerate(stones): a_[i] = fn(s_)
        return a_
    kk = arr(lambda s_: s_['k']); kk[N:] = 0.004
    k = kk[lab]
    d = smin(smin(smin(dB, dT, k), dL, k), dR, k)
    cA = np.zeros((NS, 4), f32); cB = np.ones((NS, 4), f32); cC = np.zeros((NS, 4), f32); cE = np.zeros((NS, 4), bool)
    for i, s_ in enumerate(stones):
        for ci, (en, a_, b_, cc) in enumerate(s_['corners']): cE[i, ci] = en; cA[i, ci] = a_; cB[i, ci] = b_; cC[i, ci] = cc
    pairs = ((dL, dB), (dR, dB), (dL, dT), (dR, dT))
    for ci, (d1, d2) in enumerate(pairs):
        a_ = cA[lab, ci]; b_ = cB[lab, ci]; cc = cC[lab, ci]
        dC = np.where(cE[lab, ci], (a_ * d1 + b_ * d2 - cc) / np.sqrt(a_ * a_ + b_ * b_ + 1e-9), 9.0).astype(f32)
        d = smin(d, dC, k)
    del k
    d = (d + 0.002 * fbm(S, 2.0, seed + 3, fmin=10, fmax=40)).astype(f32)
    g = np.clip(GAP + 0.0025 * fbm(S, 2.0, seed + 4, fmin=6, fmax=30), 0.005, 0.013).astype(f32)
    for bi in range(2):
        be = np.full(NS, -1, np.int32); ba = np.zeros(NS, f32); bra = np.ones(NS, f32); brb = np.ones(NS, f32)
        for i, s_ in enumerate(stones):
            if len(s_['bites']) > bi: e, al, ra, rb_ = s_['bites'][bi]; be[i] = e; ba[i] = al; bra[i] = ra; brb[i] = rb_
        E = be[lab]
        if (E < 0).all(): continue
        along = np.where(E <= 1, lx, ly); across = np.select([E == 0, E == 1, E == 2], [dT, dB, dL], dR) - g
        esd = (np.sqrt(((along - ba[lab]) / bra[lab]) ** 2 + (across / brb[lab]) ** 2) - 1) * np.minimum(bra[lab], brb[lab])
        d = np.where(E >= 0, np.minimum(d, g + esd), d).astype(f32)
    plx = lx.copy(); ply = ly.copy()
    for pi, q in enumerate(packers):
        m = lab == q['parent']; d1, d2 = pairs[q['ci']]
        e1 = d1[m] - q['c'] / (3 * q['a']); e2 = d2[m] - q['c'] / (3 * q['b'])
        dp_ = -(np.sqrt((e1 / q['rx']) ** 2 + (e2 / q['ry']) ** 2) - 1) * q['ry']
        take = dp_ > d[m]
        sub = d[m]; sub[take] = dp_[take]; d[m] = sub
        sl = lab[m]; sl[take] = N + pi; lab[m] = sl
        sx = plx[m]; sx[take] = e1[take]; plx[m] = sx
        sy = ply[m]; sy[take] = e2[take]; ply[m] = sy
    lx, ly = plx, ply; del plx, ply
    dp = (d - g).astype(f32); stone = smooth(-0.0012, 0.0012, dp)
    ispk = lab >= N
    pp = arr(lambda s_: s_['p']); txa = arr(lambda s_: s_['tx']); tya = arr(lambda s_: s_['ty'])
    rb = arr(lambda s_: s_['rb']); inr = arr(lambda s_: s_['inr'])
    ww = arr(lambda s_: s_['w']); HH = arr(lambda s_: s_['H'])
    for pi, q in enumerate(packers):
        pp[N + pi] = q['p']; rb[N + pi] = 0.5 * q['ry']; inr[N + pi] = 0.5 * q['ry']; ww[N + pi] = 2 * q['rx']; HH[N + pi] = 2 * q['ry']
    FAC = np.zeros((NS, 4, 4), f32)
    for i, s_ in enumerate(stones): FAC[i] = s_['fac']
    hm = (0.004 + 0.003 * smooth(-0.006, 0, dp) + 0.0006 * fbm(S, 1.2, seed + 6, fmin=120)).astype(f32)
    best = np.full((S, S), np.inf, f32); kst = np.zeros((S, S), np.int8)
    for kq in range(4):
        th = FAC[lab, kq, 0]; sk = FAC[lab, kq, 1]; ak = FAC[lab, kq, 2]
        Rk = 0.5 * (np.abs(np.cos(th)) * ww[lab] + np.abs(np.sin(th)) * HH[lab])
        v = sk * (ak * Rk - (lx * np.cos(th) + ly * np.sin(th)))
        v = np.where(ispk, np.inf, v).astype(f32)
        mm = v < best; best = np.where(mm, v, best); kst[mm] = kq
    facet = np.minimum(0, np.where(np.isinf(best), 0, best)).astype(f32); del best
    fs_act = np.where(facet < -0.002, np.take_along_axis(FAC[lab, :, 3], kst[..., None].astype(np.int64), -1)[..., 0], 0).astype(f32)
    gp = (GRAIN * fbm(S, 1.8, seed + 13, fmin=60, fmax=300) - PITS * smooth(2.5, 2.9, fbm(S, 2.0, seed + 14, fmin=40, fmax=200))).astype(f32)
    hface = (pp[lab] + txa[lab] * lx + tya[lab] * ly + facet + 0.006 * smooth(0, 0.85 * np.maximum(inr[lab], 0.005), dp) ** 0.7 + gp).astype(f32)
    hface = np.maximum(hface, hm + 0.012)
    sb = np.clip(dp / rb[lab], 0, 1); prof = 1 - (1 - sb) ** 2
    h_st = (hm + (hface - hm) * prof).astype(f32); gp = (gp * prof * (dp > 0)).astype(f32); del hface, sb, prof, facet
    chip = np.zeros((S, S), f32)
    for ci in range(2):
        ce = np.full(NS, -1, np.int32); ca = np.zeros(NS, f32); cr = np.ones(NS, f32)
        for i, s_ in enumerate(stones):
            if len(s_['chips']) > ci: e, al, rr = s_['chips'][ci]; ce[i] = e; ca[i] = al; cr[i] = rr
        E = ce[lab]
        if (E < 0).all(): continue
        along = np.where(E == 0, lx, ly); across = np.select([E == 0, E == 2], [dT, dL], dR) - g
        rr = np.sqrt((along - ca[lab]) ** 2 + across ** 2); disc = (1 - smooth(cr[lab] - 0.003, cr[lab], rr)) * (E >= 0) * (1 - ispk)
        plane = hm + 0.006 + 0.577 * dp
        cut = disc * smooth(0.0, 0.0015, h_st - plane)
        h_st = np.where(disc > 0, lerp(h_st, np.minimum(h_st, plane), disc), h_st).astype(f32)
        chip = np.maximum(chip, cut * (dp > 0))
    h = np.where(dp > 0, h_st, hm).astype(f32); del h_st, dL, dR, lx, ly, g
    # ---- colour ----
    PALs = np.stack([_pal(kq) for kq in PAL_KEYS])
    pid = np.zeros(NS, np.int32); val = np.ones(NS, f32); warm = np.zeros(NS, f32)
    for i, s_ in enumerate(stones): pid[i] = s_['pid']; val[i] = s_['val']; warm[i] = s_['warm']
    for pi, q in enumerate(packers): pid[N + pi] = q['pid']; val[N + pi] = rng.uniform(0.9, 1.0); warm[N + pi] = rng.uniform(-1, 1)
    wm = np.stack([1 + 0.02 * warm, np.ones(NS, f32), 1 - 0.025 * warm], 1)
    stone_rgb = PALs[pid] * val[:, None] * wm
    stone_rgb = lerp(stone_rgb, stone_rgb[:N].mean(0, keepdims=True), CALM)   # ~14 stones per 1.5 m tile: no standouts
    col = stone_rgb[lab].astype(f32)
    col *= (1 + 0.035 * fs_act)[..., None]
    vloc = np.clip(dB / np.maximum(dB + dT, 1e-4), 0, 1).astype(f32); del dB, dT
    col *= (0.94 + 0.09 * vloc)[..., None]
    for j, ang in enumerate((0.35, 1.40, 2.44)):
        st = fbm(S, 2.2, seed + 40 + j, fmin=12, fmax=70, ax=2.5, angle=ang)
        col *= np.where(lab % 3 == j, 1 + 0.018 * st, 1.0)[..., None]
    mort = hx(mortar) * (1 + 0.05 * fbm(S, 1.5, seed + 15, fmin=20, fmax=150))[..., None]
    ledge = ((1 - stone) * np.roll(stone, -8, 0)).astype(f32)
    mort = mort * (1 + 0.06 * ledge)[..., None]
    col = lerp(mort, col, stone[..., None]).astype(f32); del mort, ledge
    Ln = np.array([-0.12, 0.80, 0.58], f32); Ln /= np.linalg.norm(Ln)
    n_s = normal_from_height(blur(np.clip((h - gp) / HN, 0, 1), 4.0), HN * 2.0, T)
    s_ = painted_light(n_s, Ln) - Ln[2]
    q = s_ / 0.10; s_ = lerp(s_, (np.floor(q) + smooth(0.3, 0.7, q - np.floor(q))) * 0.10, POST)
    HI = hx(ST_HI); SH = hx(ST_SH)
    hi = np.clip(s_ / 0.35, 0, 1)[..., None]; col = lerp(col * (1 + HIG * hi), HI, 0.18 * hi)
    lo = np.clip(-s_ / 0.45, 0, 1)[..., None]; col = lerp(col * (1 - LOG * lo), SH, 0.28 * lo); del hi, lo, s_, q
    band = (smooth(0, 0.004, dp) - smooth(0.012, 0.024, dp)).astype(f32)
    rim = (band * smooth(0.20, 0.50, n_s[..., 1])).astype(f32)
    col = lerp(col * (1 + 0.06 * rim[..., None]), HI, 0.20 * rim[..., None])
    under = (band * smooth(0.15, 0.45, -n_s[..., 1]))[..., None]
    col = lerp(col * (1 - 0.20 * under), SH, 0.22 * under); del under, band, n_s
    occ = np.zeros((S, S), f32)
    for kq in range(1, 21): occ = np.maximum(occ, np.roll(h, (kq, int(round(0.15 * kq))), (0, 1)) - h - kq * px * 1.43)
    sh = blur(smooth(0, 0.004, occ), 1.2)[..., None]; del occ
    col = lerp(col * (1 - CAST * sh), SH, 0.25 * sh); del sh
    lc = luma(col)[..., None]
    col = lerp(col, lerp(col, lc, 0.5) * 1.12, 0.7 * chip[..., None])
    line = np.clip(np.roll(chip, 2, 0) - chip, 0, 1)[..., None]; col = lerp(col, SH, 0.4 * line); del lc, line
    col *= (1 + 0.03 * fbm(S, 2.0, seed + 50, fmin=1.5, fmax=5))[..., None]
    h01 = blur(np.clip(h / HN, 0, 1), 1.0)
    Rgh = np.clip(0.82 + 0.03 * fs_act - 0.06 * rim - 0.08 * chip + 0.11 * (1 - stone), 0.60, 0.97).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h01), down2(Rgh)
    if write:
        vki_write_set(out_prefix, bc, h1, R1, HN, T)
        meta = [dict(u=s_['cx'] / T, v=s_['cy'] / T, w=s_['w'], h=s_['H'], lab=i) for i, s_ in enumerate(stones) if s_['w'] * s_['H'] > json_min]
        with open(os.path.join(TEXDIR, out_prefix + "_stones.json"), "w") as f: json.dump(meta, f)
    return dict(bc=bc, N=N, packers=P, courses=NC, time=time.time() - t0)


# ------------------------------------------------------------------ wattle (WattleIn, the INFILL slot)
def vki_gen_wattle_in(S=2048, seed=251, T=1.5, depth=0.035, nst=6, nrod=28, tone=1.12, out_prefix="T_VKI_WattleIn", write=True):
    """copy of vk_tex2.gen_wattle: nst stakes and nrod rods per tile (both even, so the weave wraps), painted at
    S and stored at S/2, lighter touch, lifted so the wall luma stays >= 0.35"""
    assert nst % 2 == 0 and nrod % 2 == 0, "nst and nrod must be even for the weave to wrap"
    rng = np.random.default_rng(seed)
    x, y = grid(S); X = x * T; Y = (1 - y) * T; del x, y
    sp = T / nst; pitch = T / nrod
    Yw = (Y + 0.005 * fbm(S, 3.0, seed + 1, fmin=1, fmax=4)) % T; del Y
    row = np.floor(Yw / pitch).astype(np.int32) % nrod; v = (Yw / pitch) % 1; del Yw
    thick = rng.uniform(0.78, 0.98, nrod).astype(f32)
    vv = (v - 0.5) / (0.5 * thick[row]); prof = np.sqrt(np.clip(1 - vv * vv, 0, 1)).astype(f32); del vv, v
    wz = np.cos(np.pi * (X / sp - 0.5) + np.pi * row).astype(f32)
    rod = np.where(prof > 0, 0.30 + 0.22 * wz + 0.40 * prof ** 0.8, 0.05).astype(f32)
    streak = fbm(S, 1.6, seed + 3, fmin=15, fmax=250, ax=8)
    rod = rod + 0.02 * streak * prof
    su = ((X / sp) % 1 - 0.5) * sp / 0.018; sprof = np.sqrt(np.clip(1 - su * su, 0, 1)).astype(f32); del su, X
    stake = np.where(sprof > 0, 0.42 + 0.18 * sprof, 0).astype(f32) * (wz < 0.2)
    isstake = stake > rod
    h = blur(np.clip(np.maximum(rod, stake), 0, 1).astype(f32), 1.6); del rod, stake
    tone_r = rng.uniform(0, 1, nrod).astype(f32)
    c0 = np.array([0.36, 0.26, 0.16], f32) * tone; c1 = np.array([0.58, 0.45, 0.28], f32) * tone
    col = lerp(c0, c1, (0.3 + 0.5 * tone_r[row])[..., None] * (0.6 + 0.4 * prof[..., None]))
    col = col * (1 + 0.08 * streak)[..., None] * (0.72 + 0.38 * (wz * 0.5 + 0.5))[..., None]
    col = np.where(isstake[..., None], np.array([0.40, 0.31, 0.20], f32) * tone * (0.8 + 0.3 * sprof[..., None]), col)
    grey = smooth(0.6, 1.6, fbm(S, 2.6, seed + 4, fmin=2, fmax=20))
    col = lerp(col, np.array([0.52, 0.50, 0.44], f32) * tone * (0.7 + 0.3 * prof[..., None]), 0.30 * grey[..., None]); del grey
    col, n_s = paint_form_light(col.astype(f32), h, depth, T, hig=0.14, log=0.20, post=0.25)
    gapm = ((prof <= 0) & ~isstake)
    col = np.where(gapm[..., None], col * 0.55, col)
    Rg = np.clip(0.82 + 0.02 * streak + 0.1 * gapm, 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(Rg)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ dressed stone surface (StoneBlockIn; also M_VKI_Dress)
def vki_gen_stoneblock_in(S=2048, seed=18, T=1.5, depth=0.05, nf=4, out_prefix="T_VKI_StoneBlockIn", write=True):
    """copy of vk_tex2.gen_stoneblock: no lichen, no crack; nf x nf chiselled facets (4 at T=1.5 keeps the exterior's
    ~0.4 m facet and gives >= 12 elements per tile)"""
    rng = np.random.default_rng(seed); px = T / S
    pts = []
    for j in range(nf):
        for i in range(nf):
            pts.append(((i + 0.5 + rng.uniform(-0.3, 0.3) + 0.5 * (j % 2)) / nf, (j + 0.5 + rng.uniform(-0.3, 0.3)) / nf))
    pts = np.array(pts, f32) % 1; n = len(pts)
    x, y = grid(S)
    off = rng.uniform(-0.002, 0.002, n).astype(f32); sl = rng.uniform(0.015, 0.035, n).astype(f32); th = rng.uniform(0, 2 * math.pi, n)
    tau = 0.006
    Dmin = np.full((S, S), np.inf, f32); ID1 = np.zeros((S, S), np.int32)
    for i, (cx_, cy_) in enumerate(pts):
        dx = wrapd(x - cx_) * T; dy = wrapd(y - cy_) * T; D = dx * dx + dy * dy; m = D < Dmin; Dmin = np.where(m, D, Dmin); ID1[m] = i
    num = np.zeros((S, S), f32); den = np.zeros((S, S), f32); wmax = np.zeros((S, S), f32)
    for i, (cx_, cy_) in enumerate(pts):
        dx = wrapd(x - cx_) * T; dy = wrapd(y - cy_) * T; w = np.exp(-(dx * dx + dy * dy - Dmin) / tau).astype(f32)
        num += w * (off[i] + sl[i] * (dx * math.cos(th[i]) + dy * math.sin(th[i]))); den += w; wmax = np.maximum(wmax, w)
    h = (num / den).astype(f32); crease = (1 - wmax / den).astype(f32); del num, den, wmax, Dmin, x, y
    pits = smooth(2.2, 2.7, fbm(S, 1.5, seed + 9, fmin=60, fmax=400)).astype(f32)
    grain = (0.00015 * fbm(S, 1.8, seed + 2, fmin=60, fmax=300) - 0.0008 * pits).astype(f32)
    h01 = np.clip(0.5 + h / depth, 0, 1).astype(f32)
    h01g = np.clip(0.5 + (h + grain) / depth, 0, 1).astype(f32)
    fval = rng.uniform(-1, 1, n).astype(f32)
    # calmer than outdoors: the S1 / S2 drift is a quarter as strong and per facet, not in 1 m blotches
    t_ = (0.5 + 0.12 * fbm(S, 2.5, seed + 1, fmin=3, fmax=12))[..., None]
    col = lerp(_pal('S1') * 0.93, _pal('S2') * 0.90, t_) * (1 + 0.05 * fval[ID1])[..., None] * (1 + 0.04 * fbm(S, 1.0, seed + 8, fmin=80, fmax=500))[..., None] * (1 - 0.18 * pits)[..., None]
    col *= (1 + 0.02 * fbm(S, 2.2, seed + 5, fmin=12, fmax=70, ax=2.5, angle=0.4))[..., None]
    col, n_s = paint_form_light(col.astype(f32), h01, depth, T, hig=0.12, log=0.16, post=0.2, ex=1.0)
    col *= (1 - 0.05 * smooth(0.3, 0.5, crease))[..., None]
    col *= (1 + 0.03 * fbm(S, 2.0, seed + 50, fmin=1.5, fmax=5))[..., None]
    Rg = np.clip(0.86 + 0.03 * fbm(S, 2.0, seed + 7, fmin=4, fmax=60), 0.6, 0.97).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h01g), down2(Rg)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ brick (the BRICK slot: oven, firebox, breasts)
def vki_gen_brick(S=2048, seed=621, T=1.5, depth=0.02, nr=20, nbk=6, out_prefix="T_VKI_Brick", write=True,
                  pal=None, mortar="#9C9284", over=0.10, over_col="#5C3324", vrange=(0.88, 1.08)):
    """running bond from vk_texgen.gen_plaster's brick patch (nr rows, even so it wraps; nbk bricks per row), 8 mm lime
    joints #9C9284, gen_plaster's brick palette with per-brick value U(.88,1.08), 10 % overfired #5C3324, edge chips.
    Soot is vertex colour, not texture. Sewer kit: pal (brick colours), mortar, over (overfired share), over_col and
    vrange may be changed; the defaults keep T_VKI_Brick as it was."""
    assert nr % 2 == 0, "nr must be even for the running bond to wrap"
    rng = np.random.default_rng(seed); px = T / S
    x, y = grid(S)
    X = (x + 0.0012 / T * fbm(S, 3.0, seed + 1, fmin=4, fmax=60)) % 1; Y = (y + 0.0012 / T * fbm(S, 3.0, seed + 2, fmin=4, fmax=60)) % 1; del x, y
    br = np.minimum((Y * nr).astype(np.int32), nr - 1); bv = ((Y * nr) % 1).astype(f32)
    bxo = (X * nbk + 0.5 * (br % 2)) % nbk; bci = np.minimum(bxo.astype(np.int32), nbk - 1); bu = (bxo % 1).astype(f32); del X, Y, bxo
    bid = br * nbk + bci; nb_ = nr * nbk; del bci
    d = (np.minimum(np.minimum(bu, 1 - bu) * T / nbk, np.minimum(bv, 1 - bv) * T / nr) + 0.0012 * fbm(S, 2.4, seed + 3, fmin=20, fmax=200)).astype(f32)
    g = 0.004
    mask = smooth(g, g + 0.0015, d); prof = smooth(g, g + 0.012, d)
    bpal = np.array(pal if pal is not None else
                    [(0.60, 0.33, 0.22), (0.52, 0.29, 0.20), (0.64, 0.40, 0.27), (0.56, 0.36, 0.25)], f32)
    pid = rng.integers(0, len(bpal), nb_); val = rng.uniform(vrange[0], vrange[1], nb_).astype(f32)
    brgb = bpal[pid] * val[:, None]
    over_ = rng.choice(nb_, int(round(over * nb_)), replace=False)                 # overfired: darker, not black holes
    brgb[over_] = lerp(brgb[over_], hx(over_col) * rng.uniform(0.9, 1.1, (len(over_), 1)), 0.65)
    tilt = rng.uniform(-1, 1, (nb_, 2)).astype(f32); proud = rng.uniform(-0.04, 0.04, nb_).astype(f32)
    chip = smooth(1.4, 1.9, fbm(S, 2.6, seed + 5, fmin=8, fmax=80)) * (1 - smooth(g + 0.002, g + 0.02, d))
    face = 0.55 + 0.25 * prof + proud[bid] + (tilt[bid, 0] * (bu - 0.5) + tilt[bid, 1] * (bv - 0.5)) * 0.05 + 0.02 * fbm(S, 2.0, seed + 6, fmin=30, fmax=300) - 0.25 * chip
    h = blur(np.clip(mask * face + (1 - mask) * 0.2, 0, 1), 1.4).astype(f32); del face
    mott = fbm(S, 2.2, seed + 7, fmin=12, fmax=120)
    col = brgb[bid] * (0.92 + 0.12 * prof)[..., None] * (1 + 0.06 * mott)[..., None]
    mcol = hx(mortar) * (1 + 0.05 * fbm(S, 1.5, seed + 8, fmin=20, fmax=200))[..., None]
    col = lerp(mcol, col, mask[..., None]).astype(f32); del mcol, mott
    col, n_s = paint_form_light(col, h, depth, T, hig=0.15, log=0.22, post=0.25)
    col = lerp(col, lerp(col, luma(col)[..., None], 0.4) * 1.08, 0.6 * chip[..., None])
    col *= (1 + 0.03 * fbm(S, 2.0, seed + 50, fmin=1.5, fmax=5))[..., None]
    Rg = np.clip(0.84 + 0.04 * fbm(S, 2.4, seed + 9, fmin=6) + 0.08 * (1 - mask), 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(Rg)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ hearth ash (the ASH slot)
def vki_gen_ash(S=1024, seed=631, T=0.75, depth=0.02, out_prefix="T_VKI_Ash", write=True):
    """pale grey ash bed: soft domes 1-4 cm, char lumps 0.6-2 cm (#2A2624 with #4A4440 edges), pale flakes #D8D2C6.
    No embers (embers are GLOW geometry). Painted at S=1024, stored 512."""
    rng = np.random.default_rng(seed); px = T / S; ar = (T / 0.75) ** 2
    lo = fbm(S, 2.4, seed, fmin=3, fmax=16); fine = fbm(S, 1.2, seed + 1, fmin=60, fmax=400)
    col = lerp(hx("#7E7872"), hx("#B3ADA4"), (0.55 + 0.18 * lo)[..., None]) * (1 + 0.04 * fine)[..., None]
    items = []
    for _ in range(int(140 * ar)):
        cx, cy = rng.uniform(0, S, 2); r = rng.uniform(0.005, 0.02) / px
        items.append((cx, cy, r * rng.uniform(0.9, 1.3), r * rng.uniform(0.6, 1.0), rng.uniform(0, math.pi), rng.uniform(0.15, 0.4)))
    Hd, Cd, _ = _stamp_domes(S, items, flat=0.8, irr=0.3, rng=rng); del Cd
    h = 0.35 + 0.35 * blur(Hd, 2.0) + 0.03 * fine; del Hd
    lumps = []
    for _ in range(int(60 * ar)):
        cx, cy = rng.uniform(0, S, 2); r = rng.uniform(0.003, 0.01) / px
        lumps.append((cx, cy, r * rng.uniform(0.9, 1.4), r * rng.uniform(0.6, 1.0), rng.uniform(0, math.pi), 0.35))
    Hc, Cc, _ = _stamp_domes(S, lumps, flat=0.3, irr=0.45, rng=rng)
    core = smooth(0.08, 0.2, Hc)
    col = lerp(col, hx("#4A4440"), 0.9 * Cc[..., None]); col = lerp(col, hx("#2A2624") * (1 + 0.1 * fine)[..., None], 0.85 * core[..., None])
    h = np.maximum(h, 0.35 + 0.7 * Hc); del Hc
    fl = []
    for _ in range(int(160 * ar)):
        cx, cy = rng.uniform(0, S, 2); r = rng.uniform(0.002, 0.005) / px
        fl.append((cx, cy, r, r * rng.uniform(0.4, 0.8), rng.uniform(0, math.pi), 0.1))
    Hf, Cf, _ = _stamp_domes(S, fl, flat=0.15, irr=0.5, rng=rng)
    col = lerp(col, hx("#D8D2C6"), 0.8 * Cf[..., None]); h = h + 0.1 * Hf; del Hf
    h = np.clip(h, 0, 1).astype(f32)
    col, _ = paint_form_light(np.clip(col, 0, 1).astype(f32), h, depth, T, hig=0.12, log=0.18, post=0.25)
    Rg = np.clip(0.95 - 0.05 * Cc, 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(Rg)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ bedding straw (the STRAW slot, RushMat)
def vki_gen_strawbed(S=2048, seed=97, T=1.5, depth=0.03, n_top=900, n_under=1400, out_prefix="T_VKI_StrawBed", write=True):
    """calm bedding straw: a mid-straw ground, an under-layer of slightly darker strands and ~n_top flat top strands
    (8-22 cm, 6-10 mm: flat, painterly straws, not hairs) in clumped directions, #B08A45 / #C9A456 / #D9BD6E with paler
    tips, 18 % old grey #9A8E6E; gaps #4A3A22 only as soft shade. Much lower contrast than gen_straw."""
    rng = np.random.default_rng(seed); px = T / S
    lo = fbm(S, 2.4, seed, fmin=3, fmax=12)
    col = lerp(hx("#846A3C"), hx("#957844"), (0.5 + 0.2 * lo)[..., None]).astype(f32)
    col = np.ascontiguousarray(col); h = np.full((S, S), 0.1, f32)
    xs, ys = grid(256); cl = rng.uniform(0, 1, (28, 2)); _, _, IDc = voronoi(xs, ys, cl); ang_c = rng.uniform(0, math.pi, 28)
    TOP = [hx("#B08A45"), hx("#C9A456"), hx("#D9BD6E")]; GREY = hx("#9A8E6E"); TIPW = hx("#E6D69A")
    def strand(level, dark, wr):
        cx, cy = rng.uniform(0, S, 2)
        a0 = ang_c[IDc[int(cy / S * 256) % 256, int(cx / S * 256) % 256]] + rng.uniform(-0.45, 0.45)
        L = rng.uniform(0.08, 0.22) / px; w = rng.uniform(*wr) / px
        c0 = GREY * rng.uniform(0.95, 1.08) if rng.random() < 0.18 else TOP[int(rng.integers(0, 3))] * rng.uniform(0.92, 1.05)
        c1 = lerp(c0, TIPW, rng.uniform(0.15, 0.4))
        if rng.random() < 0.5: c0, c1 = c1, c0
        return (cx - math.cos(a0) * L / 2, cy - math.sin(a0) * L / 2, a0, L, w, rng.uniform(-0.06, 0.06), c0 * dark, c1 * dark, level)
    under = [strand(0.30 + 0.10 * i / n_under, 0.84, (0.005, 0.008)) for i in range(n_under)]
    vki_strands(col, h, under, nseg=4, pk=0.05)
    top = [strand(0.45 + 0.15 * i / n_top, 1.0, (0.006, 0.010)) for i in range(n_top)]
    vki_strands(col, h, top, nseg=4, pk=0.05)
    h = blur(np.clip(h, 0, 1), 1.2).astype(f32)
    col, _ = paint_form_light(np.clip(col, 0, 1).astype(f32), h, depth, T, hig=0.15, log=0.14, post=0.25, ex=1.5)
    sh = vki_cast_shadow(h * depth, px, n=8, slope=1.0)[..., None]
    col = lerp(col * (1 - 0.15 * sh), hx("#4A3A22"), 0.12 * sh); del sh
    Rg = np.clip(0.88 + 0.04 * fbm(S, 2.0, seed + 5, fmin=10, fmax=200), 0, 1).astype(f32)
    bc, h1, R1 = down2(np.clip(col, 0, 1).astype(f32)), down2(h), down2(Rg)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return bc


# ------------------------------------------------------------------ the §4.2 jobs (one per MCP call)
VKI_TEX_JOBS = {
    "T_VKI_Boards_NS":   lambda: vki_gen_floorboards(seed=611, T=3.0, depth=0.02, nb=12, joints=3, orient="NS", out_prefix="T_VKI_Boards_NS"),
    "T_VKI_Boards_EW":   lambda: vki_gen_floorboards(seed=611, T=3.0, depth=0.02, nb=12, joints=3, orient="EW", out_prefix="T_VKI_Boards_EW"),
    "T_VKI_BoardsV":     lambda: vki_gen_floorboards(seed=611, T=1.5, depth=0.02, nb=6, joints=0, orient="NS", tone=0.13, wob=0.0002,
                                                     gap=(0.004, 0.0085), out_prefix="T_VKI_BoardsV"),
    # fix r1: unequal courses (0.40-0.62 m), wider length jitter, more per-stone value / warm-cool spread and a little
    # more joint wander, so the flags read as hand-laid dressed paving, not brick or tile (review r1)
    "T_VKI_Flagstone":   lambda: vki_gen_blocks(seed=15, T=3.0, nrow=6, blocks=(4, 6, 5, 5, 4, 6), pal=("S1", "S2", "S4"), mortar="#5E564C", chip=0.5,
                                                gap=0.005, wjit=0.34, tone=0.64, mtone=0.85, cham_m=0.018, dnoise=0.0022, dfmax=10,
                                                rows=(0.62, 0.40, 0.55, 0.45, 0.58, 0.40), vrange=(0.86, 1.10), warm_amp=2.0,
                                                out_prefix="T_VKI_Flagstone"),
    "T_VKI_AshlarIn":    lambda: vki_gen_blocks(seed=14, T=1.5, nrow=3, blocks=(3, 2, 3), pal=("S2",), mortar="#736A5E", chip=0.6,
                                                gap=0.0035, wjit=0.10, tone=1.02, cham_m=0.035, dnoise=0.0016, dfmax=14,
                                                out_prefix="T_VKI_AshlarIn"),
    "T_VKI_FlagRustic":  lambda: vki_gen_flagrustic(seed=33, T=3.0, aspect=1.0, prot=(0.010, 0.018), joint="#4A3A2C", out_prefix="T_VKI_FlagRustic"),
    "T_VKI_Earth":       lambda: vki_gen_earthfloor(seed=456, T=3.0, rushes=1.0, soot=0.0, out_prefix="T_VKI_Earth"),
    "T_VKI_EarthSooty":  lambda: vki_gen_earthfloor(seed=456, T=3.0, rushes=0.2, soot=1.0, out_prefix="T_VKI_EarthSooty"),
    "T_VKI_PlasterIn":   lambda: vki_gen_plaster_in(seed=23, T=1.5, depth=0.015, blot=0.2, out_prefix="T_VKI_PlasterIn"),
    "T_VKI_StoneIn":     lambda: vki_gen_stone_in(L=stone_layout(10, T=1.5, lacing=False, NC=4), mortar="#857B6C", out_prefix="T_VKI_StoneIn"),
    "T_VKI_WattleIn":    lambda: vki_gen_wattle_in(T=1.5, nst=6, nrod=28, out_prefix="T_VKI_WattleIn"),
    "T_VKI_StoneBlockIn": lambda: vki_gen_stoneblock_in(seed=18, T=1.5, out_prefix="T_VKI_StoneBlockIn"),
    "T_VKI_Brick":       lambda: vki_gen_brick(seed=621, T=1.5, nr=20, nbk=6, out_prefix="T_VKI_Brick"),
    "T_VKI_Ash":         lambda: vki_gen_ash(S=1024, seed=631, T=0.75, out_prefix="T_VKI_Ash"),
    "T_VKI_StrawBed":    lambda: vki_gen_strawbed(seed=97, T=1.5, out_prefix="T_VKI_StrawBed"),
    "T_VKI_Textiles":    lambda: vki_gen_textiles_atlas(S=2048, seed=950),          # text vki_textiles
}


def vki_tex_run(name):
    """run ONE §4.2 generator by output name; returns timing and the stored _BC stats"""
    import time; t0 = time.time()
    VKI_TEX_JOBS[name]()
    out = dict(name=name, seconds=round(time.time() - t0, 1))
    try: out.update(vki_tex_stats(name))
    except Exception as e: out["stats_error"] = repr(e)
    return out
