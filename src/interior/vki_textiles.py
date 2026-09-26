# ===================== VKI textile atlas (INTERIOR_SPEC §4.2: T_VKI_Textiles) =====================
# Text vki_textiles (src/interior/vki_textiles.py); executed after vki_tex into the same namespace (see vki_tex's header):
#   g["vki_tex_run"]("T_VKI_Textiles")            # one MCP call
# Layout (the contract shared with vki_core's VKI_TEXTILE_CELLS / vki_textile_map, which own the mapping at runtime):
#   2048 x 2048 painted, stored 1024 x 1024 (T_VKI_Textiles_BC / _N / _R). 2 columns x 4 rows of 2:1 cells (1024 x 512 at
#   2048). Cell i: col = i % 2, row = i // 2, row 0 at the TOP of the image. Order: 0 rug_madder, 1 rug_indigo, 2 runner,
#   3 hanging_heraldic, 4 tapestry_millefleur, 5 quilt_patch, 6 blanket_wool, 7 altar_frontal.
#   Inset padding PAD_U = 24/1024, PAD_V = 24/512 of a cell; cell-local (u, v) in 0..1 maps to
#   U = (col + PAD_U + u*(1-2*PAD_U)) / 2,  V = (3 - row + PAD_V + v*(1-2*PAD_V)) / 4      (v = 0 at the cell's bottom)
#   The padding continues the cell (clamped edge; the runner wraps in u). The runner is periodic in u with period 1/4
#   of the cell (so u 0..1, 0..0.5 or 0..0.25 all chain); it is drawn for u 0..1 <-> 1.5 m (Runner_150), v 0..1 <-> 1.0 m.
# Every top-level name starts with vki_/VKI_ (T18).

VKI_TX_CELLS = ("rug_madder", "rug_indigo", "runner", "hanging_heraldic", "tapestry_millefleur", "quilt_patch",
                "blanket_wool", "altar_frontal")
VKI_TX_PAD_U = 24 / 1024
VKI_TX_PAD_V = 24 / 512
VKI_TX_SIZE_M = {"rug_madder": (2.6, 1.3), "rug_indigo": (2.6, 1.3), "runner": (1.5, 1.0), "hanging_heraldic": (2.4, 1.2),
                 "tapestry_millefleur": (2.7, 1.35), "quilt_patch": (2.0, 1.0), "blanket_wool": (2.0, 1.0),
                 "altar_frontal": (1.8, 0.9)}          # nominal size of each cell's content, for motif / thread scale


def vki_tx_uv(i, u, v):
    """atlas UV of cell i at cell-local (u, v) in 0..1: the vki_textile_map formula (for tests; vki_core owns the runtime copy)"""
    col, row = i % 2, i // 2
    return ((col + VKI_TX_PAD_U + u * (1 - 2 * VKI_TX_PAD_U)) / 2, (3 - row + VKI_TX_PAD_V + v * (1 - 2 * VKI_TX_PAD_V)) / 4)


# ------------------------------------------------------------------ rectangular (non-square) helpers
def vki_tx_fbm(Hc, Wc, Wm, Hm, beta, seed, fmin=1.0, fmax=None, ax=1.0, ay=1.0):
    """periodic fractal noise on an Hc x Wc canvas that spans Wm x Hm metres; fmin / fmax in cycles per metre"""
    rng = np.random.default_rng(seed)
    F = np.fft.fft2(rng.standard_normal((Hc, Wc)))
    FX, FY = np.meshgrid(np.fft.fftfreq(Wc) * Wc / Wm, np.fft.fftfreq(Hc) * Hc / Hm)
    r = np.sqrt((FX * ax) ** 2 + (FY * ay) ** 2); r[0, 0] = 1.0
    amp = r ** (-beta / 2.0); amp[r < fmin] = 0.0
    if fmax is not None: amp[r > fmax] = 0.0
    amp[0, 0] = 0.0
    o = np.real(np.fft.ifft2(F * amp)).astype(f32)
    return (o - o.mean()) / (o.std() + 1e-8)


def vki_tx_blur(a, sigma):
    """periodic gaussian blur (sigma in px) for rectangular 2D / 3D arrays"""
    H, W = a.shape[:2]
    g = np.exp(-2.0 * (np.pi * sigma) ** 2 * (np.fft.fftfreq(W)[None, :] ** 2 + np.fft.fftfreq(H)[:, None] ** 2))
    if a.ndim == 2: return np.real(np.fft.ifft2(np.fft.fft2(a) * g)).astype(f32)
    return np.stack([np.real(np.fft.ifft2(np.fft.fft2(a[..., i]) * g)) for i in range(a.shape[2])], -1).astype(f32)


def vki_tx_light(col, h01, depth, pxx, pxy, hig=0.08, log=0.12, post=0.0, ex=2.0):
    """paint_form_light for rectangular canvases (anisotropic pixel size pxx, pxy in metres)"""
    Ln = np.array([-0.12, 0.80, 0.58], f32); Ln /= np.linalg.norm(Ln)
    hb = vki_tx_blur(h01, 3.0) * depth * ex
    gx = (np.roll(hb, -1, 1) - np.roll(hb, 1, 1)) / (2 * pxx); gr = (np.roll(hb, -1, 0) - np.roll(hb, 1, 0)) / (2 * pxy)
    L = np.sqrt(gx * gx + gr * gr + 1)
    s_ = np.clip((-gx * Ln[0] + gr * Ln[1] + Ln[2]) / L, 0, 1) - Ln[2]
    q = s_ / 0.10; s_ = lerp(s_, (np.floor(q) + smooth(0.3, 0.7, q - np.floor(q))) * 0.10, post)
    hi = np.clip(s_ / 0.35, 0, 1)[..., None]; col = lerp(col * (1 + hig * hi), hx(ST_HI), 0.18 * hi)
    lo = np.clip(-s_ / 0.45, 0, 1)[..., None]; col = lerp(col * (1 - log * lo), hx(ST_SH), 0.28 * lo)
    return col.astype(f32)


def vki_tx_ao(h, radii=(4, 12, 36), k=(2.0, 1.5, 0.8), floor=0.45):
    """cavity_ao for rectangular canvases (radii in painted px = the stored-size VKI_AO radii x 2)"""
    occ = np.zeros_like(h)
    for r, kk in zip(radii, k): occ += np.maximum(vki_tx_blur(h, r) - h, 0) * kk
    return np.clip(1 - occ, floor, 1).astype(f32)


def vki_tx_aa(d, px):
    """coverage of the inside (d < 0) of a signed distance field, anti-aliased over one pixel"""
    return np.clip(0.5 - d / px, 0, 1).astype(f32)


def vki_tx_box(X, Y, x0, y0, x1, y1):
    """signed distance (m) to an axis-aligned rectangle"""
    dx = np.maximum(x0 - X, X - x1); dy = np.maximum(y0 - Y, Y - y1)
    return (np.where((dx > 0) | (dy > 0), np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)), np.maximum(dx, dy))).astype(f32)


def vki_tx_lozenge(X, Y, cx, cy, a, b):
    """approximate signed distance (m) to a lozenge with half-diagonals a (x) and b (y)"""
    return ((np.abs(X - cx) / a + np.abs(Y - cy) / b - 1) * (a * b / math.hypot(a, b))).astype(f32)


def vki_tx_seg(X, Y, ax_, ay_, bx, by):
    """distance (m) to a segment"""
    ex, ey = bx - ax_, by - ay_; L2 = ex * ex + ey * ey + 1e-12
    t = np.clip(((X - ax_) * ex + (Y - ay_) * ey) / L2, 0, 1)
    return np.hypot(X - ax_ - t * ex, Y - ay_ - t * ey).astype(f32)


def vki_tx_paint(col, m, c):
    """lerp colour c into col by coverage m (in place friendly, returns the array)"""
    return col + (np.asarray(c, f32) - col) * m[..., None]


# ------------------------------------------------------------------ cell painters
# Each returns col (H,W,3), h (H,W, 0..1), R (H,W) on the content canvas; X, Y in metres (Y up, v = Y / Hm).
def vki_tx_pile(Hc, Wc, Wm, Hm, seed, amt=0.06):
    """knotted-pile / woven-thread impression: fine noise plus soft abrash bands along x"""
    fine = vki_tx_fbm(Hc, Wc, Wm, Hm, 1.0, seed, fmin=60)
    abr = vki_tx_fbm(Hc, Wc, Wm, Hm, 2.0, seed + 1, fmin=0.8, fmax=6, ay=40.0)
    return (1 + amt * fine + 0.035 * abr).astype(f32), fine


def vki_tx_rug_madder(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape; rng = np.random.default_rng(seed)
    Xw = X + 0.004 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 2, fmin=1, fmax=12)
    Yw = Y + 0.004 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 3, fmin=1, fmax=12)
    FR = 0.075; x0, x1 = FR, Wm - FR
    dB = np.minimum(np.minimum(Xw - x0, x1 - Xw), np.minimum(Yw, Hm - Yw))
    IV, BL, MD, GD, DK = hx("#D9C9A0"), hx("#2C3E66"), hx("#8E2B22"), hx("#B8862E"), hx("#1E2A48")
    col = np.broadcast_to(MD, X.shape + (3,)).astype(f32).copy()
    h = np.full(X.shape, 0.55, f32)
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.215, px), hx("#5A1A16"))          # dark red line inside the border
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.205, px), IV)                      # inner guard stripe
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.19, px), BL)                       # blue border
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.04, px), IV)                       # outer guard stripe
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.025, px), DK)                      # selvedge
    # border motif: small gold / ivory rosettes every 0.13 m along the border's centre line
    inb = (dB > 0.04) & (dB < 0.19)
    s_ = np.where(np.abs(np.minimum(Xw - x0, x1 - Xw) - 0.115) < np.abs(np.minimum(Yw, Hm - Yw) - 0.115), Yw, Xw)
    ph = ((s_ / 0.13) % 1 - 0.5) * 0.13
    dd = np.minimum(np.abs(np.minimum(Xw - x0, x1 - Xw) - 0.115), np.abs(np.minimum(Yw, Hm - Yw) - 0.115))
    ros = vki_tx_lozenge(ph, dd, 0, 0, 0.045, 0.045)
    col = vki_tx_paint(col, vki_tx_aa(ros, px) * inb, GD); col = vki_tx_paint(col, vki_tx_aa(ros + 0.018, px) * inb, MD)
    # field: a chain of three lozenges with gold outline, blue inside, ivory inner lozenge and a madder heart
    cy = Hm / 2; cxs = (Wm / 2 - 0.66, Wm / 2, Wm / 2 + 0.66)
    fld = dB > 0.215
    bar = vki_tx_box(Xw, Yw, cxs[0], cy - 0.018, cxs[2], cy + 0.018)
    col = vki_tx_paint(col, vki_tx_aa(bar, px) * fld, GD)
    for cx in cxs:
        L0 = vki_tx_lozenge(Xw, Yw, cx, cy, 0.29, 0.34)
        col = vki_tx_paint(col, vki_tx_aa(L0, px) * fld, GD)
        col = vki_tx_paint(col, vki_tx_aa(L0 + 0.022, px), BL)
        col = vki_tx_paint(col, vki_tx_aa(vki_tx_lozenge(Xw, Yw, cx, cy, 0.15, 0.18), px), IV)
        col = vki_tx_paint(col, vki_tx_aa(vki_tx_lozenge(Xw, Yw, cx, cy, 0.11, 0.13), px), MD)
        col = vki_tx_paint(col, vki_tx_aa(vki_tx_lozenge(Xw, Yw, cx, cy, 0.035, 0.04), px), GD)
        h = h + 0.05 * vki_tx_aa(L0, px)
    # field fillers: small ivory / gold stars on a staggered 0.2 m lattice, clear of the lozenges
    gx_ = ((Xw - Wm / 2) / 0.2) % 1 - 0.5; gy_ = ((Yw - cy) / 0.2 + 0.5 * (np.floor((Xw - Wm / 2) / 0.2) % 2)) % 1 - 0.5
    star = np.minimum(vki_tx_lozenge(gx_ * 0.2, gy_ * 0.2, 0, 0, 0.028, 0.012), vki_tx_lozenge(gx_ * 0.2, gy_ * 0.2, 0, 0, 0.012, 0.028))
    far = np.min(np.stack([vki_tx_lozenge(Xw, Yw, cx, cy, 0.29, 0.34) for cx in cxs]), 0) > 0.03
    col = vki_tx_paint(col, vki_tx_aa(star, px) * far * (dB > 0.25), hx("#C9B27A"))
    # spandrels: blue triangles in the field corners
    for sx in (x0 + 0.215, x1 - 0.215):
        for sy in (0.215, Hm - 0.215):
            tri = np.abs(Xw - sx) / 0.17 + np.abs(Yw - sy) / 0.13 - 1
            col = vki_tx_paint(col, vki_tx_aa(tri * 0.1, px) * fld, hx("#243457"))
    pile, fine = vki_tx_pile(Hc, Wc, Wm, Hm, seed + 5)
    col = col * pile[..., None]
    h = h + 0.03 * fine
    # fringes along the short ends
    fz = (X < x0) | (X > x1)
    t = Y / 0.009; fr = t - np.floor(t); prof = np.sqrt(np.clip(1 - ((fr - 0.5) / 0.4) ** 2, 0, 1)).astype(f32)
    ln = rng.uniform(0.7, 1.0, int(Hm / 0.009) + 3)[np.floor(t).astype(np.int32)]
    reach = np.where(X < x0, (x0 - X) / FR, (X - x1) / FR)
    thr = prof * (reach < ln)
    fcol = IV * (0.72 + 0.28 * prof)[..., None]
    col = np.where(fz[..., None], lerp(hx("#3A3026") + 0 * col, fcol, thr[..., None]), col)
    h = np.where(fz, 0.25 + 0.25 * thr, h)
    R = np.where(fz, 0.85, 0.92).astype(f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_rug_indigo(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape; rng = np.random.default_rng(seed)
    Xw = X + 0.003 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 2, fmin=1, fmax=12)
    Yw = Y + 0.003 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 3, fmin=1, fmax=12)
    FR = 0.07; x0, x1 = FR, Wm - FR
    IN, IV, MD, OC, DK = hx("#2F4470"), hx("#D9C9A0"), hx("#8E2B22"), hx("#B8862E"), hx("#1C2946")
    col = np.broadcast_to(IN, X.shape + (3,)).astype(f32).copy(); h = np.full(X.shape, 0.55, f32)
    st = 0.035                                                    # kilim step
    qx = (np.floor(Xw / st) + 0.5) * st; qy = (np.floor(Yw / st) + 0.5) * st
    # long-edge borders: stepped teeth (ivory / madder)
    de = np.minimum(Yw, Hm - Yw)
    col = vki_tx_paint(col, vki_tx_aa(de - 0.10, px), DK)
    tooth = ((qx / 0.14) % 1 - 0.5) * 0.14
    teeth = (np.abs(tooth) / 0.07 + np.minimum(np.floor(de / st) * st, 0.1) / 0.075 - 1)
    col = vki_tx_paint(col, vki_tx_aa(teeth * 0.05, px) * (de < 0.08), MD)
    col = vki_tx_paint(col, vki_tx_aa(np.abs(de - 0.088) - 0.006, px), IV)
    # end bands (constant x): ivory / madder with stepped ivory diamonds / ochre, mirrored at both ends
    xe = np.minimum(Xw - x0, x1 - Xw)
    bands = [(0.00, 0.03, IV), (0.03, 0.13, MD), (0.13, 0.15, IV), (0.15, 0.19, OC), (0.19, 0.21, IV), (0.21, 0.29, MD), (0.29, 0.31, IV)]
    for (a_, b_, c_) in bands:
        col = vki_tx_paint(col, vki_tx_aa(np.maximum(a_ - xe, xe - b_), px) * (de > 0.10), c_)
    for (c0, hw) in ((0.08, 0.05), (0.25, 0.04)):
        dq = ((qy / (2.6 * hw)) % 1 - 0.5) * (2.6 * hw)
        dia = np.abs(np.floor(np.abs(np.minimum(qx - x0, x1 - qx) - c0) / st) * st) + np.abs(dq) - hw
        col = vki_tx_paint(col, vki_tx_aa(dia, px) * (np.abs(xe - c0) < hw + 0.01) * (de > 0.10), IV)
    # three stepped medallions along the centre
    cy = Hm / 2
    for cx in (Wm / 2 - 0.62, Wm / 2, Wm / 2 + 0.62):
        ddx = np.abs(np.floor(np.abs(Xw - cx) / st) * st); ddy = np.abs(np.floor(np.abs(Yw - cy) / st) * st)
        m0 = ddx / 0.27 + ddy / 0.33
        col = vki_tx_paint(col, (m0 < 1.0).astype(f32), IV)
        col = vki_tx_paint(col, (m0 < 0.86).astype(f32), MD)
        col = vki_tx_paint(col, (m0 < 0.55).astype(f32), OC)
        col = vki_tx_paint(col, (m0 < 0.40).astype(f32), IN)
        col = vki_tx_paint(col, ((ddx < st * 0.9) & (ddy < st * 0.9)).astype(f32), IV)
        h = h + 0.04 * (m0 < 1.0)
    # little stepped crosses scattered in the field between the medallions
    for cx in (Wm / 2 - 0.31, Wm / 2 + 0.31, Wm / 2 - 0.93, Wm / 2 + 0.93):
        for cy2 in (cy - 0.24, cy + 0.24):
            crs = (np.abs(Xw - cx) < 0.04) & (np.abs(Yw - cy2) < 0.012) | (np.abs(Xw - cx) < 0.012) & (np.abs(Yw - cy2) < 0.04)
            col = vki_tx_paint(col, crs.astype(f32), OC)
    col = vki_tx_blur(col, 0.6)
    pile, fine = vki_tx_pile(Hc, Wc, Wm, Hm, seed + 5, amt=0.05)
    col = col * pile[..., None]; h = h + 0.025 * fine
    fz = (X < x0) | (X > x1)
    t = Y / 0.012; fr = t - np.floor(t); prof = np.sqrt(np.clip(1 - ((fr - 0.5) / 0.38) ** 2, 0, 1)).astype(f32)
    ln = rng.uniform(0.65, 1.0, int(Hm / 0.012) + 3)[np.floor(t).astype(np.int32)]
    reach = np.where(X < x0, (x0 - X) / FR, (X - x1) / FR)
    thr = prof * (reach < ln)
    col = np.where(fz[..., None], lerp(hx("#3A3026") + 0 * col, hx("#CDBE98") * (0.72 + 0.28 * prof)[..., None], thr[..., None]), col)
    h = np.where(fz, 0.25 + 0.25 * thr, h)
    R = np.where(fz, 0.85, 0.92).astype(f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_runner(X, Y, Wm, Hm, px, seed):
    """ONE period (X in 0..Wm/4 of the 1.5 m runner); the caller tiles it 4x. Every noise field is periodic over the
    period canvas, so u = 0 and u = 1 (and every quarter) match exactly."""
    Hc, Wc = X.shape; P = X.max() + (X[0, 1] - X[0, 0]) / 2          # period width in metres (0.375)
    RD, GD, DR = hx("#7A2020"), hx("#C49A3A"), hx("#4E1414")
    Xw = X + 0.002 * vki_tx_fbm(Hc, Wc, P, Hm, 3.0, seed + 2, fmin=3, fmax=30)
    Yw = Y + 0.002 * vki_tx_fbm(Hc, Wc, P, Hm, 3.0, seed + 3, fmin=3, fmax=30)
    col = np.broadcast_to(RD, X.shape + (3,)).astype(f32).copy(); h = np.full(X.shape, 0.55, f32)
    de = np.minimum(Yw, Hm - Yw)
    col = vki_tx_paint(col, vki_tx_aa(de - 0.03, px), DR)
    col = vki_tx_paint(col, vki_tx_aa(np.abs(de - 0.038) - 0.007, px), GD)
    col = vki_tx_paint(col, vki_tx_aa(np.abs(de - 0.118) - 0.007, px), GD)
    # border band: gold dashes, 6 per period
    dp = ((Xw / (P / 6)) % 1 - 0.5) * (P / 6)
    dash = vki_tx_box(dp, de, -0.018, 0.064, 0.018, 0.092)
    col = vki_tx_paint(col, vki_tx_aa(dash, px), GD)
    # centre: one quatrefoil per period (gold outline, dark red inside, ivory heart), small gold lozenges between
    cx, cy = P / 2, Hm / 2
    q = np.min(np.stack([np.hypot(Xw - cx - ox, Yw - cy - oy) - 0.058 for ox, oy in ((0.06, 0), (-0.06, 0), (0, 0.06), (0, -0.06))]), 0)
    col = vki_tx_paint(col, vki_tx_aa(q, px), GD)
    col = vki_tx_paint(col, vki_tx_aa(q + 0.012, px), hx("#5C1818"))
    col = vki_tx_paint(col, vki_tx_aa(vki_tx_lozenge(Xw, Yw, cx, cy, 0.045, 0.045), px), GD)
    col = vki_tx_paint(col, vki_tx_aa(np.hypot(Xw - cx, Yw - cy) - 0.016, px), hx("#E0D2A8"))
    for lx in (0.0, P):
        col = vki_tx_paint(col, vki_tx_aa(vki_tx_lozenge(Xw, Yw, lx, cy, 0.035, 0.05), px), GD)
        for oy in (-0.26, 0.26):
            col = vki_tx_paint(col, vki_tx_aa(np.hypot(Xw - lx, Yw - cy - oy) - 0.014, px), GD)
    for oy in (-0.26, 0.26):
        col = vki_tx_paint(col, vki_tx_aa(vki_tx_lozenge(Xw, Yw, cx, cy + oy, 0.03, 0.03), px), hx("#A8452C"))
    gold = (np.abs(col - GD[None, None, :]).sum(-1) < 0.05).astype(f32)
    h = h + 0.08 * gold
    fine = vki_tx_fbm(Hc, Wc, P, Hm, 1.0, seed + 5, fmin=60)
    streak = vki_tx_fbm(Hc, Wc, P, Hm, 1.4, seed + 6, fmin=20, ax=4.0)
    col = col * (1 + 0.05 * fine + 0.025 * streak)[..., None]
    h = h + 0.02 * fine
    R = (0.9 - 0.2 * gold).astype(f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_hanging(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape; rng = np.random.default_rng(seed)
    Xw = X + 0.004 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 2, fmin=1, fmax=12)
    Yw = Y + 0.004 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 3, fmin=1, fmax=12)
    MD, BL, GD = hx("#8E2B22"), hx("#2C3E66"), hx("#C49A3A")
    col = np.where((Xw < Wm / 2)[..., None], MD, BL).astype(f32); h = np.full(X.shape, 0.55, f32)
    # chevron across both halves, three gold crosses, a gold border line
    apex = (Wm / 2, Hm * 0.80); arms = ((0.10, 0.12), (Wm - 0.10, 0.12))
    dch = np.minimum(vki_tx_seg(Xw, Yw, arms[0][0], arms[0][1], *apex), vki_tx_seg(Xw, Yw, *apex, arms[1][0], arms[1][1]))
    col = vki_tx_paint(col, vki_tx_aa(dch - 0.075, px), hx("#7A5A22"))
    col = vki_tx_paint(col, vki_tx_aa(dch - 0.062, px), GD)
    for (cx, cy) in ((0.42, Hm * 0.72), (Wm - 0.42, Hm * 0.72), (Wm / 2, Hm * 0.36)):
        crs = np.minimum(vki_tx_box(Xw, Yw, cx - 0.10, cy - 0.028, cx + 0.10, cy + 0.028), vki_tx_box(Xw, Yw, cx - 0.028, cy - 0.10, cx + 0.028, cy + 0.10))
        crs = np.minimum(crs, np.hypot(Xw - cx, Yw - cy) - 0.045)
        col = vki_tx_paint(col, vki_tx_aa(crs - 0.012, px), hx("#7A5A22")); col = vki_tx_paint(col, vki_tx_aa(crs, px), GD)
    body = vki_tx_box(Xw, Yw, 0.035, 0.10, Wm - 0.035, Hm - 0.085)
    col = vki_tx_paint(col, vki_tx_aa(np.abs(body) - 0.009, px) * (body > -0.03), GD)
    gold = (np.abs(col - GD[None, None, :]).sum(-1) < 0.06).astype(f32)
    h = h + 0.08 * gold
    # rod sleeve at the top with loops, fringe at the bottom
    top = Yw > Hm - 0.075
    loops = (((Xw / 0.20) % 1) < 0.45)
    col = np.where(top[..., None], np.where(loops[..., None], hx("#3A2A20"), col * 0.55), col)
    h = np.where(top, 0.62, h)
    fz = Y < 0.07
    t = X / 0.010; fr = t - np.floor(t); prof = np.sqrt(np.clip(1 - ((fr - 0.5) / 0.4) ** 2, 0, 1)).astype(f32)
    grp = (np.floor(t / 5) % 2).astype(bool)
    ln = rng.uniform(0.7, 1.0, int(Wm / 0.010) + 3)[np.floor(t).astype(np.int32)]
    thr = prof * ((0.07 - Y) / 0.07 < ln)
    fc = np.where(grp[..., None], GD, MD) * (0.72 + 0.28 * prof)[..., None]
    col = np.where(fz[..., None], lerp(hx("#2E2620") + 0 * col, fc, thr[..., None]), col)
    h = np.where(fz, 0.25 + 0.25 * thr, h)
    # soft vertical folds of a hung cloth
    fold = np.sin(2 * np.pi * (Xw / 0.34 + 0.15 * vki_tx_fbm(Hc, Wc, Wm, Hm, 2.5, seed + 7, fmin=0.5, fmax=4)))
    col = col * (1 + 0.05 * fold)[..., None]
    fine = vki_tx_fbm(Hc, Wc, Wm, Hm, 1.4, seed + 5, fmin=30, ax=0.3)
    col = col * (1 + 0.04 * fine)[..., None]; h = h + 0.02 * fine
    R = np.where(gold > 0.5, 0.7, 0.9).astype(f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_tapestry(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape; rng = np.random.default_rng(seed)
    FG, BR, GD = hx("#23402E"), hx("#6E2A22"), hx("#C49A3A")
    col = np.broadcast_to(FG, X.shape + (3,)).astype(f32).copy(); h = np.full(X.shape, 0.55, f32)
    dB = np.minimum(np.minimum(X, Wm - X), np.minimum(Y, Hm - Y))
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.13, px), GD)
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.118, px), BR)
    col = vki_tx_paint(col, vki_tx_aa(np.abs(dB - 0.012) - 0.006, px), GD)
    # border: small gold four-petal flowers every 0.14 m
    s_ = np.where(np.minimum(X, Wm - X) < np.minimum(Y, Hm - Y), Y, X)
    ph = ((s_ / 0.14) % 1 - 0.5) * 0.14
    bf = np.min(np.stack([np.hypot(ph - ox, dB - 0.065 - oy) - 0.014 for ox, oy in ((0.016, 0), (-0.016, 0), (0, 0.016), (0, -0.016))]), 0)
    col = vki_tx_paint(col, vki_tx_aa(bf, px) * (dB < 0.118) * (dB > 0.02), GD)
    # millefleur field: Poisson-disk flowers with leaves
    FL = [hx(c) for c in ("#E8DDBE", "#D98A8A", "#7F9CCB", "#D8B64A", "#B8432F", "#E8DDBE")]
    LV = [hx("#4E7A44"), hx("#6B8F4E"), hx("#3E6538")]
    pts = []
    x0, x1, y0, y1 = 0.16, Wm - 0.16, 0.16, Hm - 0.16
    for _ in range(6000):
        p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 0.068 ** 2 for q in pts[-400:]): pts.append(p)
        if len(pts) >= 420: break
    ix = lambda xm: int(xm / Wm * Wc); iy = lambda ym: int((1 - ym / Hm) * Hc)
    for (fx, fy) in pts:
        R_ = rng.uniform(0.014, 0.026); c = FL[int(rng.integers(0, len(FL)))]; rot = rng.uniform(0, 2 * math.pi)
        r0, r1 = iy(fy + 0.06), iy(fy - 0.06) + 1; c0, c1 = ix(fx - 0.06), ix(fx + 0.06) + 1
        r0, c0 = max(r0, 0), max(c0, 0); r1, c1 = min(r1, Hc), min(c1, Wc)
        sx, sy = X[r0:r1, c0:c1] - fx, Y[r0:r1, c0:c1] - fy
        cw = col[r0:r1, c0:c1]; hw = h[r0:r1, c0:c1]
        for k_ in range(int(rng.integers(2, 4))):                                   # leaves first
            a = rot + k_ * 2.1 + rng.uniform(-0.4, 0.4); lx, ly = math.cos(a) * R_ * 1.5, math.sin(a) * R_ * 1.5
            u_ = (sx - lx) * math.cos(a) + (sy - ly) * math.sin(a); v_ = -(sx - lx) * math.sin(a) + (sy - ly) * math.cos(a)
            lf = np.sqrt((u_ / (R_ * 0.95)) ** 2 + (v_ / (R_ * 0.42)) ** 2) - 1
            cw[:] = vki_tx_paint(cw, vki_tx_aa(lf * R_ * 0.42, px), LV[int(rng.integers(0, 3))])
        th = np.arctan2(sy, sx) - rot; r = np.hypot(sx, sy)
        pet = r - R_ * (0.55 + 0.45 * np.abs(np.cos(2.5 * th)))
        cw[:] = vki_tx_paint(cw, vki_tx_aa(pet, px), c * rng.uniform(0.9, 1.05))
        cw[:] = vki_tx_paint(cw, vki_tx_aa(r - R_ * 0.28, px), hx("#D8B64A") if c[2] > 0.5 else hx("#6E2A22"))
        hw[:] = np.maximum(hw, 0.55 + 0.06 * vki_tx_aa(pet, px))
    fold = np.sin(2 * np.pi * (X / 0.40 + 0.15 * vki_tx_fbm(Hc, Wc, Wm, Hm, 2.5, seed + 7, fmin=0.5, fmax=4)))
    fine = vki_tx_fbm(Hc, Wc, Wm, Hm, 1.4, seed + 5, fmin=30, ax=0.3)
    col = col * (1 + 0.04 * fold + 0.04 * fine)[..., None]; h = h + 0.02 * fine
    R = np.full(X.shape, 0.9, f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_quilt(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape; rng = np.random.default_rng(seed)
    PAL = [hx(c) for c in ("#9E5A4C", "#7E8A62", "#B08A48", "#56627A", "#C8B894", "#9A5B34", "#6E6440", "#4E6A8A")]
    BIND = 0.045; nx_, ny_ = 6, 3
    col = np.zeros(X.shape + (3,), f32); h = np.full(X.shape, 0.5, f32)
    pw, ph_ = (Wm - 2 * BIND) / nx_, (Hm - 2 * BIND) / ny_
    ci = np.clip(np.floor((X - BIND) / pw), 0, nx_ - 1).astype(np.int32); cj = np.clip(np.floor((Y - BIND) / ph_), 0, ny_ - 1).astype(np.int32)
    pick = np.zeros((nx_, ny_), np.int32); kind = rng.integers(0, 4, (nx_, ny_))
    for i in range(nx_):
        for j in range(ny_):
            bad = {pick[i - 1, j]} if i else set()
            if j: bad.add(pick[i, j - 1])
            choices = [k for k in range(len(PAL)) if k not in bad]
            pick[i, j] = choices[int(rng.integers(0, len(choices)))]
    base = np.stack(PAL)[pick[ci, cj]]
    lx = X - BIND - ci * pw; ly = Y - BIND - cj * ph_
    kd = kind[ci, cj]
    chk = ((np.floor(lx / 0.028) + np.floor(ly / 0.028)) % 2 == 0)
    stripe = (np.floor(lx / 0.022) % 2 == 0)
    dots = (np.hypot((lx % 0.04) - 0.02, (ly % 0.04) - 0.02) < 0.006)
    patt = np.where(kd == 1, np.where(chk, 1.07, 0.93), np.where(kd == 2, np.where(stripe, 1.06, 0.95), np.where(kd == 3, np.where(dots, 1.18, 0.98), 1.0)))
    col = base * patt[..., None]
    de = np.minimum(np.minimum(lx, pw - lx), np.minimum(ly, ph_ - ly))
    pill = np.sqrt(np.clip(de / 0.05, 0, 1))
    h = 0.35 + 0.25 * pill
    col = col * (0.86 + 0.14 * pill)[..., None]
    # running stitches 12 mm inside every seam
    along = np.where(np.abs(np.minimum(lx, pw - lx) - 0.012) < np.abs(np.minimum(ly, ph_ - ly) - 0.012), ly, lx)
    sd = np.minimum(np.abs(np.minimum(lx, pw - lx) - 0.012), np.abs(np.minimum(ly, ph_ - ly) - 0.012))
    dash = ((along / 0.022) % 1) < 0.55
    stc = vki_tx_aa(sd - 0.0022, px) * dash * (de > 0.006)
    col = vki_tx_paint(col, stc, hx("#E6DCC0")); h = h + 0.05 * stc
    # binding
    dB = np.minimum(np.minimum(X, Wm - X), np.minimum(Y, Hm - Y))
    bm = vki_tx_aa(dB - BIND, px)
    col = vki_tx_paint(col, bm, hx("#4A3326")); h = lerp(h, 0.55 + 0.1 * np.sqrt(np.clip(dB / BIND, 0, 1)), bm)
    fine = vki_tx_fbm(Hc, Wc, Wm, Hm, 1.2, seed + 5, fmin=40)
    col = col * (1 + 0.04 * fine)[..., None]; h = h + 0.02 * fine
    R = np.full(X.shape, 0.92, f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_blanket(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape
    CR, BR = hx("#CFC2A6"), hx("#6B4A32")
    fuzz = vki_tx_fbm(Hc, Wc, Wm, Hm, 1.2, seed + 1, fmin=30); pill = vki_tx_fbm(Hc, Wc, Wm, Hm, 2.2, seed + 2, fmin=6, fmax=40)
    col = (CR * (1 + 0.035 * fuzz + 0.012 * pill)[..., None]).astype(f32); h = (0.5 + 0.03 * fuzz + 0.03 * pill).astype(f32)
    Xw = X + 0.003 * vki_tx_fbm(Hc, Wc, Wm, Hm, 3.0, seed + 3, fmin=1, fmax=10)
    xe = np.minimum(Xw, Wm - Xw)
    for (a_, b_) in ((0.15, 0.23), (0.115, 0.13), (0.25, 0.265)):
        col = vki_tx_paint(col, vki_tx_aa(np.maximum(a_ - xe, xe - b_), px), BR * (1 + 0.05 * fuzz)[..., None])
    # blanket stitch along all edges
    dB = np.minimum(np.minimum(X, Wm - X), np.minimum(Y, Hm - Y))
    along = np.where(np.minimum(X, Wm - X) < np.minimum(Y, Hm - Y), Y, X)
    st = vki_tx_aa(np.abs(((along / 0.025) % 1 - 0.5) * 0.025) - 0.0018, px) * (dB < 0.016)
    col = vki_tx_paint(col, np.maximum(st, vki_tx_aa(dB - 0.004, px)), BR); h = h + 0.05 * st
    R = np.full(X.shape, 0.95, f32)
    return col.astype(f32), h.astype(f32), R


def vki_tx_altar(X, Y, Wm, Hm, px, seed):
    Hc, Wc = X.shape; rng = np.random.default_rng(seed)
    RD, GD, DK = hx("#7A2020"), hx("#C49A3A"), hx("#4A1414")
    # tone-on-tone damask lattice
    lat = np.abs(((X / 0.12) % 1) - 0.5) * 0.12 / 0.06 + np.abs(((Y / 0.16) % 1) - 0.5) * 0.16 / 0.08
    dam = vki_tx_aa(np.abs(lat - 0.9) * 0.02 - 0.0025, px)
    col = np.broadcast_to(RD, X.shape + (3,)).astype(f32) * (1 + 0.08 * dam)[..., None]
    col = vki_tx_paint(col, vki_tx_aa(np.hypot(((X / 0.12) % 1 - 0.5) * 0.12, ((Y / 0.16) % 1 - 0.5) * 0.16) - 0.008, px), hx("#8E3026"))
    h = np.full(X.shape, 0.5, f32)
    # orphreys with small red crosses
    for ox in (Wm * 0.27, Wm * 0.73):
        ob = vki_tx_box(X, Y, ox - 0.05, 0.03, ox + 0.05, Hm - 0.13)
        col = vki_tx_paint(col, vki_tx_aa(ob, px), GD)
        cyy = ((Y / 0.10) % 1 - 0.5) * 0.10
        crs = np.minimum(vki_tx_box(X - ox, cyy, -0.022, -0.007, 0.022, 0.007), vki_tx_box(X - ox, cyy, -0.007, -0.022, 0.007, 0.022))
        col = vki_tx_paint(col, vki_tx_aa(crs, px) * (ob < -0.004), hx("#8E2B22"))
        col = vki_tx_paint(col, vki_tx_aa(np.abs(ob) - 0.003, px), hx("#7A5A22"))
    # central cross (pattee-like: flared arms)
    cx, cy = Wm / 2, (Hm - 0.13 + 0.03) / 2
    ax_ = np.abs(X - cx); ay_ = np.abs(Y - cy)
    vert = np.maximum(ax_ - (0.022 + 0.05 * (ay_ / 0.24) ** 2), ay_ - 0.24)
    horz = np.maximum(ay_ - (0.022 + 0.05 * (ax_ / 0.17) ** 2), ax_ - 0.17)
    crs = np.minimum(vert, horz)
    col = vki_tx_paint(col, vki_tx_aa(crs - 0.01, px), DK); col = vki_tx_paint(col, vki_tx_aa(crs, px), GD)
    # superfrontal with lozenges, fringe below it, hem and edge cord
    sf = Y > Hm - 0.10
    col = np.where(sf[..., None], GD, col)
    lz = vki_tx_lozenge(((X / 0.09) % 1 - 0.5) * 0.09, Y - (Hm - 0.05), 0, 0, 0.03, 0.03)
    col = vki_tx_paint(col, vki_tx_aa(lz, px) * sf, hx("#8E2B22"))
    fz = (Y <= Hm - 0.10) & (Y > Hm - 0.15)
    t = X / 0.008; fr = t - np.floor(t); prof = np.sqrt(np.clip(1 - ((fr - 0.5) / 0.4) ** 2, 0, 1)).astype(f32)
    ln = rng.uniform(0.7, 1.0, int(Wm / 0.008) + 3)[np.floor(t).astype(np.int32)]
    thr = prof * (((Hm - 0.10) - Y) / 0.05 < ln)
    col = np.where(fz[..., None], lerp(col, GD * (0.72 + 0.28 * prof)[..., None], thr[..., None]), col)
    col = vki_tx_paint(col, vki_tx_aa(Y - 0.028, px), GD)
    dB = np.minimum(np.minimum(X, Wm - X), np.minimum(Y, Hm - Y))
    col = vki_tx_paint(col, vki_tx_aa(dB - 0.008, px), hx("#9A7A34"))
    gold = (np.abs(col - GD[None, None, :]).sum(-1) < 0.08).astype(f32)
    speck = vki_tx_fbm(Hc, Wc, Wm, Hm, 0.8, seed + 8, fmin=80)
    col = col * (1 + gold[..., None] * 0.08 * speck[..., None])
    h = h + 0.08 * gold + 0.1 * thr * fz
    fine = vki_tx_fbm(Hc, Wc, Wm, Hm, 1.4, seed + 5, fmin=30, ax=0.3)
    col = col * (1 + 0.035 * fine)[..., None]; h = h + 0.02 * fine
    R = (0.88 - 0.22 * gold).astype(f32)
    return col.astype(f32), h.astype(f32), R


VKI_TX_PAINTERS = {"rug_madder": vki_tx_rug_madder, "rug_indigo": vki_tx_rug_indigo, "runner": vki_tx_runner,
                   "hanging_heraldic": vki_tx_hanging, "tapestry_millefleur": vki_tx_tapestry, "quilt_patch": vki_tx_quilt,
                   "blanket_wool": vki_tx_blanket, "altar_frontal": vki_tx_altar}


def vki_tx_cell(name, CW, CH, seed, depth):
    """paint one cell at CW x CH px (padding included): returns col, h, R, ao at that size"""
    pu = int(round(VKI_TX_PAD_U * CW)); pv = int(round(VKI_TX_PAD_V * CH)); Wc, Hc = CW - 2 * pu, CH - 2 * pv
    Wm, Hm = VKI_TX_SIZE_M[name]
    periodic = name == "runner"
    if periodic:                                    # paint one of 4 periods, filter it periodically, tile it
        Wp = Wc // 4; assert Wp * 4 == Wc
        Wpm = Wm / 4
        X = np.broadcast_to(((np.arange(Wp) + 0.5) / Wp * Wpm).astype(f32)[None, :], (Hc, Wp)).copy()
    else:
        Wp, Wpm = Wc, Wm
        X = np.broadcast_to(((np.arange(Wc) + 0.5) / Wc * Wm).astype(f32)[None, :], (Hc, Wc)).copy()
    Y = np.broadcast_to(((1 - (np.arange(Hc) + 0.5) / Hc) * Hm).astype(f32)[:, None], (Hc, Wp)).copy()
    pxx, pxy = Wpm / Wp, Hm / Hc; px = 0.5 * (pxx + pxy) * 1.2
    col, h, R = VKI_TX_PAINTERS[name](X, Y, Wm, Hm, px, seed)
    h = np.clip(h, 0, 1).astype(f32)
    # filters on a padded canvas: rows reflect; columns reflect, or none for the periodic runner
    P = 48
    pw = ((P, P), (0, 0)) if periodic else ((P, P), (P, P))
    colp = np.pad(col, pw + ((0, 0),), mode="reflect"); hp = np.pad(h, pw, mode="reflect")
    colp = vki_tx_light(colp, hp, 0.03, pxx, pxy, hig=0.08, log=0.12, post=0.0)      # painted relief depth 3 cm
    aop = vki_tx_ao(hp)
    sl = (slice(P, P + Hc), slice(None) if periodic else slice(P, P + Wp))
    col, ao = colp[sl], aop[sl]
    if periodic:
        col = np.tile(col, (1, 4, 1)); h = np.tile(h, (1, 4)); R = np.tile(R, (1, 4)); ao = np.tile(ao, (1, 4))
    mu = "wrap" if periodic else "edge"
    def ext(a):                                     # continue the cell into its padding: clamp, the runner wraps in u
        a = np.pad(a, ((0, 0), (pu, pu)) + ((0, 0),) * (a.ndim - 2), mode=mu)
        return np.pad(a, ((pv, pv), (0, 0)) + ((0, 0),) * (a.ndim - 2), mode="edge")
    return ext(np.clip(col, 0, 1)), ext(h), ext(R), ext(ao)


def vki_gen_textiles_atlas(S=2048, seed=950, depth=0.004, tile=4.0, out_prefix="T_VKI_Textiles", write=True):
    """the 2 x 4 textile atlas (layout in the header): each cell is painted over its content at S/2 x S/4 px, lit and
    occluded on its own canvas (no bleed between cells), extended into its padding, then the atlas is stored at S/2"""
    CW, CH = S // 2, S // 4
    col = np.zeros((S, S, 3), f32); h = np.zeros((S, S), f32); R = np.ones((S, S), f32); ao = np.ones((S, S), f32)
    for i, name in enumerate(VKI_TX_CELLS):
        c_, r_ = i % 2, i // 2
        cc, hh, rr, aa = vki_tx_cell(name, CW, CH, seed + 37 * i, depth)
        ys, xs = slice(r_ * CH, (r_ + 1) * CH), slice(c_ * CW, (c_ + 1) * CW)
        col[ys, xs] = cc; h[ys, xs] = hh; R[ys, xs] = rr; ao[ys, xs] = aa
    bc, h1, R1, ao1 = down2(col), down2(h), down2(R), down2(ao)
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, tile, ao=ao1, ao_in_albedo=0.35)
    return bc
