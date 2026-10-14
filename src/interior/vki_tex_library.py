# ===================== VKI library textures: the book atlas (the library props, vki_props_library) =====================
# Text vki_tex_library (src/interior/vki_tex_library.py). Executed on demand after vki_tex, never by vki_ns():
#   g={}
#   for t in ("vk_tex","vk_texgen","vk_tex2","vk_mat","vki_tex","vki_tex_library"): exec(bpy.data.texts[t].as_string(),g)
#   g["vki_tex_run"]("T_VKI_Books")
# T_VKI_Books (2026-10-14): 4 x 4 cells, painted 512 and stored 256 (1024 in all), row 0 at the top, in the order of
# VKI_BOOK_CELLS -- keep it in sync with vki_props_library, which maps the books onto it (vki_book_uv). M_VKI_Books takes
# it, on the library props' TEXTILE slot (k.slot_mats). Cell coordinates: u left -> right, v bottom -> top.
#   spine_*   a book's back, u across it, v up it: two designs side by side (u 0-0.5: four raised bands and a title
#             label; u 0.5-1: three bands, gold rules at head and tail, the title tooled on the leather), each darker
#             toward its joints (the rounded back); the head and tail worn pale
#   cover_*   a board, u across, v up: mottled leather, worn corners, a tooled frame and lozenge (gold on the oxblood,
#             blue and black, blind on the others; vellum plain and stained)
#   pages     the page edges, the leaves along v, stacked across u, the boards' dark edges at u 0 and 1
#   spread    an open book's two pages (gutter at u 0.5): text in brown ink, a red initial, a framed picture
#   scroll    a rolled sheet's outside (u around, v along); scroll_end its end, the rolled layers in a spiral
# Every top-level name starts with vki_/VKI_ (test T18).

VKI_BOOK_CELLS = ("spine_oxblood", "spine_brown", "spine_green", "spine_blue", "spine_black", "spine_vellum",
                  "cover_oxblood", "cover_brown", "cover_green", "cover_blue", "cover_black", "cover_vellum",
                  "pages", "spread", "scroll", "scroll_end")
VKI_BOOK_LEATHER = {"oxblood": "#6E2620", "brown": "#6E4A2C", "green": "#34503A", "blue": "#2E3E5A",
                    "black": "#2A2522", "vellum": "#CBB990"}
VKI_BOOK_GILT = ("oxblood", "blue", "black")          # covers tooled in gold (the rest blind)
VKI_BOOK_GOLD = "#C8A14C"
VKI_BOOK_INK = "#2C2016"
VKI_BOOK_PARCH = "#D6C8A2"

VKI_TEX_JOBS.update({"T_VKI_Books": lambda: vki_gen_books()})


def vki_bk_uv(PW, PH):
    """cell coordinates for a PW x PH painting: u left -> right, v bottom -> top (pixel centres)"""
    y, x = np.mgrid[0:PH, 0:PW].astype(f32)
    return ((x + 0.5) / PW).astype(f32), (1.0 - (y + 0.5) / PH).astype(f32)


def vki_bk_box(u, v, u0, u1, v0, v1, s=0.004):
    """soft rectangle coverage"""
    d = np.minimum(np.minimum(u - u0, u1 - u), np.minimum(v - v0, v1 - v))
    return smooth(-s, s, d)


def vki_bk_dot(u, v, cu, cv, r, sx=1.0, s=0.004):
    """soft round dot (sx stretches it across u, for a cell painted narrower than it is used)"""
    return smooth(r + s, r - s, np.sqrt(((u - cu) * sx) ** 2 + (v - cv) ** 2))


def vki_bk_letters(rng, u, v, u0, u1, v0, v1, rows=1, w=0.010):
    """rows of short strokes -- tooled or inked lettering too small to read"""
    cov = np.zeros(u.shape, f32)
    for r_ in range(rows):
        vc = v0 + (v1 - v0) * (r_ + 0.5) / rows
        x = u0
        while x < u1:
            ln = rng.uniform(0.03, 0.09) * (u1 - u0) / 0.6
            if x + ln > u1: break
            cov = np.maximum(cov, vki_bk_box(u, v, x, x + ln, vc - w / 2, vc + w / 2, 0.003))
            x += ln + rng.uniform(0.02, 0.05) * (u1 - u0) / 0.6
    return cov


def vki_bk_leather(P, rng, key, PW=None):
    """leather of one colour: base, mottle and grain (colour, height, roughness), PW wide"""
    PW = PW or P
    base = hx(VKI_BOOK_LEATHER[key])
    mot = fbm(P, 2.6, int(rng.integers(1 << 30)), fmin=3, fmax=40)[:, :PW]
    grain = fbm(P, 1.0, int(rng.integers(1 << 30)), fmin=120, fmax=420)[:, :PW]
    col = (np.zeros((P, PW, 3), f32) + base) * (1 + 0.025 * mot + 0.012 * grain)[..., None]
    h = (0.5 + 0.012 * grain + 0.008 * mot).astype(f32)
    R = np.full((P, PW), 0.74 if key == "vellum" else 0.6, f32) + 0.015 * mot
    return col.astype(f32), h, R.astype(f32), grain


def vki_bk_spine_half(P, rng, key, design):
    """one spine design, P tall and P / 2 wide (u 0..1 across the spine)"""
    PW = P // 2
    u, v = vki_bk_uv(PW, P)
    col, h, R, grain = vki_bk_leather(P, rng, key, PW)
    light = key == "vellum"
    col *= (1 - 0.30 * (2 * np.abs(u - 0.5)) ** 2)[..., None]               # the rounded back, darker toward the joints
    gold = np.zeros(u.shape, f32); ink = np.zeros(u.shape, f32)
    bands = (0.20, 0.39, 0.58, 0.77) if design == 0 else (0.25, 0.50, 0.75)
    for vc in bands:
        d = np.abs(v - vc)
        rid = smooth(0.016, 0.0, d)                                        # a raised band (the cords under the leather)
        h += 0.32 * rid
        col *= (1 - 0.18 * smooth(0.020, 0.012, d) * smooth(0.0, 0.010, d))[..., None]
        if light:
            ink = np.maximum(ink, vki_bk_box(u, v, 0.08, 0.92, vc - 0.002, vc + 0.002, 0.002) * 0.5)
        else:
            for s_ in (-1, 1):
                gold = np.maximum(gold, vki_bk_box(u, v, 0.06, 0.94, vc + s_ * 0.027 - 0.0022, vc + s_ * 0.027 + 0.0022, 0.002))
    if design == 0:
        lab = vki_bk_box(u, v, 0.12, 0.88, 0.615, 0.735, 0.006)               # the title label between bands 2 and 3
        if light:
            ink = np.maximum(ink, vki_bk_letters(rng, u, v, 0.16, 0.84, 0.63, 0.72, rows=2, w=0.008))
        else:
            lc = hx("#1F1A17") if key == "oxblood" else hx("#7A2419")
            col = lerp(col, (lc * (1 + 0.02 * grain)[..., None]).astype(f32), lab[..., None])
            h += 0.06 * lab
            gold = np.maximum(gold, vki_bk_box(u, v, 0.13, 0.87, 0.618, 0.732, 0.002) - vki_bk_box(u, v, 0.15, 0.85, 0.624, 0.726, 0.002))
            gold = np.maximum(gold, vki_bk_letters(rng, u, v, 0.20, 0.80, 0.635, 0.715, rows=2, w=0.009))
        for vc in ((0.20 + 0.39) / 2, (0.39 + 0.58) / 2, (0.77 + 1.0) / 2 - 0.02):   # a fleuron in the other panels
            if light: break
            gold = np.maximum(gold, vki_bk_dot(u, v, 0.5, vc, 0.022, sx=0.5))
            for s_ in (-1, 1):
                gold = np.maximum(gold, vki_bk_dot(u, v, 0.5 + s_ * 0.16, vc, 0.010, sx=0.5))
    else:
        if not light:
            for vc in (0.055, 0.075, 0.925, 0.945):                        # gold rules at head and tail
                gold = np.maximum(gold, vki_bk_box(u, v, 0.04, 0.96, vc - 0.0025, vc + 0.0025, 0.002))
            gold = np.maximum(gold, vki_bk_letters(rng, u, v, 0.18, 0.82, 0.58, 0.67, rows=2, w=0.010))
            for vc in (0.375, 0.845):                                     # a small lozenge in two panels
                d = np.abs((u - 0.5) * 0.5) / 0.05 + np.abs(v - vc) / 0.03
                gold = np.maximum(gold, smooth(1.0, 0.8, d))
        else:
            ink = np.maximum(ink, vki_bk_letters(rng, u, v, 0.18, 0.82, 0.56, 0.68, rows=3, w=0.007))
    wear = np.maximum(smooth(0.03, 0.0, v), smooth(0.97, 1.0, v))           # head and tail rubbed pale
    wn = 0.5 + 0.5 * fbm(P, 1.6, int(rng.integers(1 << 30)), fmin=20, fmax=200)[:, :PW]
    col = lerp(col, col * 1.15 + 0.01, (0.35 * wear * (0.7 + 0.3 * wn))[..., None])
    R += 0.12 * wear
    gc = hx(VKI_BOOK_GOLD) * (1 + 0.04 * grain)[..., None]
    col = lerp(col, gc.astype(f32), (0.95 * gold)[..., None])
    R = lerp(R, 0.32, gold); h -= 0.06 * gold
    col = lerp(col, hx(VKI_BOOK_INK), (0.85 * ink)[..., None])
    return col.astype(f32), np.clip(h, 0, 1).astype(f32), np.clip(R, 0.05, 1).astype(f32)


def vki_bk_spine(P, rng, key):
    a = vki_bk_spine_half(P, rng, key, 0); b = vki_bk_spine_half(P, rng, key, 1)
    return tuple(np.concatenate([x, y], axis=1).astype(f32) for x, y in zip(a, b))


def vki_bk_cover(P, rng, key):
    """a board: mottled leather, rubbed corners and edges, a tooled double frame and a centre lozenge"""
    u, v = vki_bk_uv(P, P)
    col, h, R, grain = vki_bk_leather(P, rng, key)
    light = key == "vellum"
    blot = fbm(P, 2.4, int(rng.integers(1 << 30)), fmin=3, fmax=30)
    col *= (1 + 0.015 * blot)[..., None]
    corner = np.full(u.shape, 9.0, f32)
    for cu in (0.0, 1.0):
        for cv in (0.0, 1.0):
            corner = np.minimum(corner, np.sqrt((u - cu) ** 2 + (v - cv) ** 2))
    edge = np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v))
    col = lerp(col, col * 1.2 + 0.01, (0.4 * smooth(0.10, 0.0, corner))[..., None])
    col *= (1 - 0.06 * smooth(0.03, 0.0, edge))[..., None]
    tool = np.zeros(u.shape, f32)
    if not light:
        for ins in (0.075, 0.105):
            tool = np.maximum(tool, vki_bk_box(u, v, ins, 1 - ins, ins, 1 - ins, 0.002)
                              - vki_bk_box(u, v, ins + 0.006, 1 - ins - 0.006, ins + 0.006, 1 - ins - 0.006, 0.002))
        d = np.abs(u - 0.5) / 0.20 + np.abs(v - 0.5) / 0.28
        tool = np.maximum(tool, smooth(1.03, 1.0, d) * smooth(0.95, 0.98, d))
        tool = np.maximum(tool, vki_bk_dot(u, v, 0.5, 0.5, 0.025))
        for cu in (0.075, 0.925):                                        # corner fleurons
            for cv in (0.075, 0.925):
                tool = np.maximum(tool, vki_bk_dot(u, v, cu, cv, 0.016))
    if key in VKI_BOOK_GILT:
        gc = hx(VKI_BOOK_GOLD) * (1 + 0.04 * grain)[..., None]
        col = lerp(col, gc.astype(f32), (0.9 * tool)[..., None]); R = lerp(R, 0.32, tool)
    else:
        col *= (1 - 0.35 * tool)[..., None]                               # blind tooling, pressed dark
    h -= 0.10 * tool
    if light:
        st = smooth(1.2, 2.2, fbm(P, 2.6, int(rng.integers(1 << 30)), fmin=3, fmax=24))
        col = lerp(col, col * 0.85, (0.25 * st)[..., None])
    R += 0.05 * smooth(0.12, 0.0, corner)
    return col.astype(f32), np.clip(h, 0, 1).astype(f32), np.clip(R, 0.05, 1).astype(f32)


def vki_bk_pages(P, rng):
    """page edges: leaves along v, stacked across u, a little grimier toward the outside; the boards' edges dark at
    u 0 and 1"""
    u, v = vki_bk_uv(P, P)
    base = hx("#DCCDA6")
    n = fbm(P, 2.0, int(rng.integers(1 << 30)), fmin=3, fmax=30)
    fine = fbm(P, 1.0, int(rng.integers(1 << 30)), fmin=60, fmax=300, ay=8.0)    # streaks along v
    leaves = (0.5 + 0.5 * np.sin(2 * math.pi * u * 38 + 2.0 * fine)) ** 2
    col = (np.zeros((P, P, 3), f32) + base) * (1 + 0.012 * n - 0.16 * leaves)[..., None]
    grime = smooth(0.2, 0.0, np.minimum(v, 1 - v))
    col *= (1 - 0.04 * grime)[..., None]
    board = np.maximum(smooth(0.075, 0.06, u), smooth(0.925, 0.94, u))
    col = lerp(col, hx("#3B2819") * (1 + 0.02 * n)[..., None], board[..., None])
    h = (0.5 - 0.05 * leaves + 0.25 * board).astype(f32)
    R = (0.85 - 0.2 * board).astype(f32)
    return col.astype(f32), np.clip(h, 0, 1).astype(f32), R


def vki_bk_spread(P, rng):
    """an open book: two pages (gutter at u 0.5) of brown text, a red initial on the left page, a framed picture on
    the right; the paper darker into the gutter and at the outer edges"""
    u, v = vki_bk_uv(P, P)
    base = hx(VKI_BOOK_PARCH)
    n = fbm(P, 2.2, int(rng.integers(1 << 30)), fmin=3, fmax=30)
    col = (np.zeros((P, P, 3), f32) + base) * (1 + 0.015 * n)[..., None]
    gut = np.abs(u - 0.5)
    col *= (1 - 0.30 * smooth(0.06, 0.0, gut) - 0.10 * smooth(0.04, 0.0, np.minimum(u, 1 - u)))[..., None]
    ink = np.zeros(u.shape, f32); red = np.zeros(u.shape, f32); blue = np.zeros(u.shape, f32)
    for pg in (0, 1):
        a0 = 0.5 * pg + (0.09 if pg == 0 else 0.06); a1 = 0.5 * pg + (0.44 if pg == 0 else 0.41)
        nl = 22
        for i in range(nl):
            vc = 0.86 - i * (0.86 - 0.14) / (nl - 1)
            x0 = a0
            if pg == 0 and i < 4: x0 = a0 + 0.075                         # the initial's lines start after it
            if pg == 1 and 6 <= i < 14:                                     # the picture takes part of these lines
                continue
            x1 = a1 - (rng.uniform(0.05, 0.25) * (a1 - a0) if i % 7 == 6 else 0.0)
            ink = np.maximum(ink, vki_bk_letters(rng, u, v, x0, x1, vc - 0.006, vc + 0.006, rows=1, w=0.0075))
        if pg == 0:
            red = np.maximum(red, vki_bk_box(u, v, a0, a0 + 0.065, 0.765, 0.875, 0.003))
        else:
            fr = vki_bk_box(u, v, a0, a1, 0.43, 0.70, 0.002) - vki_bk_box(u, v, a0 + 0.01, a1 - 0.01, 0.44, 0.69, 0.002)
            red = np.maximum(red, fr)
            blue = np.maximum(blue, vki_bk_box(u, v, a0 + 0.02, a1 - 0.02, 0.45, 0.68, 0.003) * (0.55 + 0.45 * smooth(-1, 1, n)))
    col = lerp(col, hx("#4E6A8A"), (0.75 * blue)[..., None])
    col = lerp(col, hx("#8E2A1C"), (0.9 * red)[..., None])
    col = lerp(col, hx(VKI_BOOK_INK), (0.85 * ink)[..., None])
    h = (0.5 + 0.006 * n - 0.04 * smooth(0.05, 0.0, gut)).astype(f32)
    return col.astype(f32), np.clip(h, 0, 1).astype(f32), np.full((P, P), 0.86, f32)


def vki_bk_scroll(P, rng):
    """a rolled sheet's outside: parchment, mottled and stained, darker at the two rolled ends (v 0 and 1)"""
    u, v = vki_bk_uv(P, P)
    n = fbm(P, 2.4, int(rng.integers(1 << 30)), fmin=2, fmax=30)
    st = smooth(1.1, 2.0, fbm(P, 2.8, int(rng.integers(1 << 30)), fmin=3, fmax=24))
    col = (np.zeros((P, P, 3), f32) + hx(VKI_BOOK_PARCH)) * (1 + 0.02 * n)[..., None]
    col = lerp(col, col * 0.9, (0.15 * st)[..., None])
    col *= (1 - 0.25 * smooth(0.05, 0.0, np.minimum(v, 1 - v)))[..., None]
    lip = smooth(0.012, 0.0, np.abs(u - 0.83))                              # the sheet's free edge along the roll
    col *= (1 - 0.2 * lip)[..., None]
    h = (0.5 + 0.008 * n + 0.1 * lip).astype(f32)
    return col.astype(f32), np.clip(h, 0, 1).astype(f32), np.full((P, P), 0.84, f32)


def vki_bk_scroll_end(P, rng):
    """a scroll's end seen square on: the rolled layers as a dark spiral on parchment, a hollow core"""
    u, v = vki_bk_uv(P, P)
    du, dv = u - 0.5, v - 0.5
    r = np.sqrt(du * du + dv * dv) / 0.5
    a = np.arctan2(dv, du) / (2 * math.pi)
    ph = r * 9.0 - a
    ring = smooth(0.80, 0.95, np.abs(ph - np.floor(ph) - 0.5) * 2)       # 1 on the spiral's line, 0 between turns
    n = fbm(P, 2.0, int(rng.integers(1 << 30)), fmin=3, fmax=30)
    col = (np.zeros((P, P, 3), f32) + hx(VKI_BOOK_PARCH)) * (0.94 + 0.02 * n)[..., None]
    col = lerp(col, col * 0.45, (0.8 * ring)[..., None])
    col = lerp(col, hx("#2A2016"), smooth(0.14, 0.08, r)[..., None])
    col *= (1 - 0.25 * smooth(0.85, 1.0, r))[..., None]
    h = (0.5 - 0.15 * ring - 0.3 * smooth(0.14, 0.08, r)).astype(f32)
    return col.astype(f32), np.clip(h, 0, 1).astype(f32), np.full((P, P), 0.85, f32)


def vki_gen_books(S=2048, seed=4711, depth=0.004, T=0.8, out_prefix="T_VKI_Books", write=True):
    """paint the 16 cells at 512 (S 2048), store the atlas at S / 2"""
    P = S // 4
    BC = np.zeros((S, S, 3), f32); H = np.zeros((S, S), f32); R = np.zeros((S, S), f32)
    for i, name in enumerate(VKI_BOOK_CELLS):
        rng = np.random.default_rng(seed + 31 * i)
        kind, _, key = name.partition("_")
        if kind == "spine": col, h, r = vki_bk_spine(P, rng, key)
        elif kind == "cover": col, h, r = vki_bk_cover(P, rng, key)
        elif name == "pages": col, h, r = vki_bk_pages(P, rng)
        elif name == "spread": col, h, r = vki_bk_spread(P, rng)
        elif name == "scroll": col, h, r = vki_bk_scroll(P, rng)
        else: col, h, r = vki_bk_scroll_end(P, rng)
        col, _ = paint_form_light(np.clip(col, 0, 1).astype(f32), h, depth, T / 4, hig=0.10, log=0.14, post=0.0)
        r0, c0 = (i // 4) * P, (i % 4) * P
        BC[r0:r0 + P, c0:c0 + P] = np.clip(col, 0, 1); H[r0:r0 + P, c0:c0 + P] = h; R[r0:r0 + P, c0:c0 + P] = r
    bc, h1, R1 = down2(BC), down2(H), down2(np.clip(R, 0.05, 1).astype(f32))
    if write: vki_write_set(out_prefix, bc, h1, R1, depth, T)
    return dict(cells=len(VKI_BOOK_CELLS), size=S // 2)
