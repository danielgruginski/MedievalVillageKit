# ===================== VKI PROPS LIBRARY: bookcases, books, scrolls (2026-10-14) =====================
# Loaded by vki_ns() (VKI_TEXTS, after vki_props_orc). Every top-level name starts with vki_/VKI_ (T18).
# The user, for the RPG's skill books (found on shelves around the towns, kept in the guild hall's library): "shelves
# and books as 3D assets, it is actually weird we don't have those". Bookcases full, half empty and narrow, a scroll
# rack, a desk's books, a closed and an open book, a heap of books on the floor.
# Books, scrolls and their pages are painted on the book atlas T_VKI_Books (M_VKI_Books; vki_tex_library paints it)
# and sit on the TEXTILE slot, overridden per master (k.slot_mats) -- no prop of this package uses textiles. Wood as
# the home furniture: oak WOOD sides, pale HEWN shelf and top boards (vki_home_top), dark board backs.
# Conventions as vki_props_home: origin at the footprint centre on the floor (a table dressing: on the table top),
# back toward local +Y, front -Y. Every book, scroll and ribbon is closed (test T7): a book is a 12-triangle box, a
# scroll a 7-sided roll, so a full 1.40 m case and the scroll rack stay inside the furniture budget.
# Build: g["vki_ws_build"]("library", VKI_LIB_NAMES); test: g["vki_test_pieces"](VKI_LIB_NAMES) -> {}.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

VKI_BOOK_CELLS = ("spine_oxblood", "spine_brown", "spine_green", "spine_blue", "spine_black", "spine_vellum",
                  "cover_oxblood", "cover_brown", "cover_green", "cover_blue", "cover_black", "cover_vellum",
                  "pages", "spread", "scroll", "scroll_end")          # keep in sync with vki_tex_library
VKI_BOOK_PAD = 12 / 512
VKI_BOOK_COLOURS = ("oxblood", "brown", "green", "blue", "black", "vellum")
VKI_BOOK_WEIGHTS = (0.22, 0.26, 0.15, 0.15, 0.12, 0.10)
VKI_LIB_MAT = "M_VKI_Books"
VKI_LIB_T = 0.035                 # case sides
VKI_LIB_SHELF_T = 0.04            # shelf boards
# a box's faces in unit corners (x, y, z in 0 / 1), wound counter-clockwise seen from outside
VKI_LIB_FACES = {"-y": ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), "+y": ((1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)),
                 "+z": ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)), "-z": ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)),
                 "+x": ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), "-x": ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1))}


def vki_book_uv(cell, u, v):
    """cell-local (u, v) in 0..1 -> atlas uv on T_VKI_Books: 4 x 4 cells, row 0 at the top of the image"""
    i = VKI_BOOK_CELLS.index(cell) if isinstance(cell, str) else int(cell)
    col, row = i % 4, i // 4
    u = min(max(u, 0.0), 1.0); v = min(max(v, 0.0), 1.0)
    return ((col + VKI_BOOK_PAD + u * (1 - 2 * VKI_BOOK_PAD)) / 4, (3 - row + VKI_BOOK_PAD + v * (1 - 2 * VKI_BOOK_PAD)) / 4)


def vki_lib_box(k, M, w, d, h, cells, skip=()):
    """a box w (x) by d (y) by h (z) standing on its local z = 0, centred in x and y, carried by M (4x4) into the
    piece; every face on the book atlas: cells = {face: (cell, (u0, u1), (v0, v1))} with u, v the face's own
    coordinates (-y / +y: x and z; +-z: x and y; +x: y and z; -x: y reversed and z). Faces in `skip` are left out."""
    bm = k.bm
    vs = {}
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                vs[(a, b, c)] = bm.verts.new(M @ Vector(((a - 0.5) * w, (b - 0.5) * d, c * h)))
    out = []
    for key, quad in VKI_LIB_FACES.items():
        if key in skip or key not in cells:
            continue
        cell, (u0, u1), (v0, v1) = cells[key]
        f = bm.faces.new([vs[q] for q in quad])
        f.material_index = VKI_TEXTILE
        for l, (a, b, c) in zip(f.loops, quad):
            fu, fv = {"-y": (a, c), "+y": (a, c), "+z": (a, b), "-z": (a, b), "+x": (b, c), "-x": (1 - b, c)}[key]
            l[k.uv].uv = vki_book_uv(cell, u0 + (u1 - u0) * fu, v0 + (v1 - v0) * fv)
        out.append(f)
    return out


def vki_lib_book(k, M, w, d, h, colour, design=0, skip=()):
    """a closed book standing on its local z = 0: thickness w along x, the spine on -y (design 0 / 1: the left / right
    half of its spine cell), page edges on +-z and +y (the boards' edges painted in), the covers on +-x"""
    sp, cv = "spine_" + colour, "cover_" + colour
    cells = {"-y": (sp, (0.5 * design, 0.5 * design + 0.5), (0, 1)), "+y": ("pages", (0, 1), (0, 1)),
             "+z": ("pages", (0, 1), (0, 1)), "-z": ("pages", (0, 1), (0, 1)),
             "+x": (cv, (0, 1), (0, 1)), "-x": (cv, (0, 1), (0, 1))}
    return vki_lib_box(k, M, w, d, h, cells, skip)


def vki_lib_pick(rng):
    return rng.choices(VKI_BOOK_COLOURS, VKI_BOOK_WEIGHTS)[0], rng.randrange(2)


def vki_lib_lying(k, x, y, z, w, d, h, colour, design=0, rz=0.0, skip=()):
    """a book lying on its back cover: its length h along x (centred on x, y), thickness w up from z, the spine toward
    -y (turned rz about z); the front cover up. Returns the top's height."""
    M = Matrix.Translation((x, y, z + w / 2)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Translation((-h / 2, 0, 0)) \
        @ Matrix.Rotation(math.pi / 2, 4, "Y")
    vki_lib_book(k, M, w, d, h, colour, design, skip=skip)
    return z + w


def vki_lib_stack(k, rng, x, y, z, n, hmax, dmax, rz=0.0):
    """n books lying in a stack (biggest at the bottom), each a little turned; returns the top's height"""
    hb = hmax * rng.uniform(0.85, 1.0); db = min(dmax, hb * rng.uniform(0.66, 0.78))
    for i in range(n):
        col, des = vki_lib_pick(rng)
        w = rng.uniform(0.035, 0.065)
        s = 1.0 - 0.06 * i * rng.uniform(0.5, 1.5)
        z = vki_lib_lying(k, x + rng.uniform(-0.01, 0.01), y + rng.uniform(-0.008, 0.008), z, w, db * s, hb * s, col, des,
                          rz=rz + rng.uniform(-0.08, 0.08))
    return z


def vki_lib_shelf(k, rng, x0, x1, z, yf, hmax, dmax, fill=0.96, lean=0.35, flat=0.08):
    """fill one shelf from x0 to x1 with books standing, their spines near the line yf (-Y side): runs of a set (one
    leather, design and height), a gap now and then (1 - fill), a book leaning on its left neighbour after a gap
    (lean: the chance), now and then a few lying flat (flat). Returns how many books."""
    x = x0 + rng.uniform(0.0, 0.008)
    n, run, prev_h = 0, 0, None
    while True:
        if run <= 0:
            col, des = vki_lib_pick(rng)
            hh = hmax * rng.uniform(0.60, 0.97); dd = dmax * rng.uniform(0.62, 0.92)
            ww = rng.uniform(0.032, 0.062); run = rng.choice((1, 1, 1, 2, 3, 4, 5))
        if rng.random() < flat and x1 - x > hmax * 0.8:                         # a few lying flat
            hb = min(hmax * 0.85, x1 - x - 0.01)
            vki_lib_stack(k, rng, x + hb / 2 + 0.015, yf + dmax * 0.4, z, rng.randint(2, 4), hb, dmax * 0.85)
            x += hb + 0.035; run = 0; prev_h = None; n += 1               # (the stack's books are turned a little)
            continue
        if rng.random() > fill:                                                   # a gap, maybe a book leaning into it
            gap = rng.uniform(0.04, 0.12)
            if prev_h and rng.random() < lean and x + gap < x1:
                a = rng.uniform(0.12, 0.32)
                h_ = min(hh, prev_h * 0.97); w_ = ww
                R = Matrix.Rotation(-a, 4, "Y")
                mnx = -w_ / 2 * math.cos(a) - h_ * math.sin(a); mnz = -w_ / 2 * math.sin(a)
                mxx = w_ / 2 * math.cos(a)
                if x - mnx + mxx > x1: break
                M = Matrix.Translation((x - mnx, yf + rng.uniform(0.0, 0.012) + dd / 2, z - mnz)) @ R
                vki_lib_book(k, M, w_, dd, h_, col, des)
                x = x - mnx + mxx + rng.uniform(0.002, 0.01); n += 1; run -= 1; prev_h = None
                continue
            x += gap; prev_h = None
            continue
        if x + ww > x1:
            break
        M = Matrix.Translation((x + ww / 2, yf + rng.uniform(0.0, 0.014) + dd / 2, z))
        vki_lib_book(k, M, ww, dd, hh * rng.uniform(0.985, 1.0), col, des)
        x += ww + rng.uniform(0.0, 0.003); n += 1; run -= 1; prev_h = hh
    return n


def vki_lib_scroll(k, M, r, ln, segs=7, ribbon=None):
    """a rolled sheet along its local +y from 0 to ln, both ends on scroll_end (the one on -y square to the eye), the
    roll's outside on the scroll cell (u around, v along); ribbon: (y, cloth slot) a closed band tied round"""
    bm = k.bm
    ang = [2 * math.pi * i / segs for i in range(segs)]
    r0 = [bm.verts.new(M @ Vector((r * math.cos(a), 0.0, r * math.sin(a)))) for a in ang]
    r1 = [bm.verts.new(M @ Vector((r * math.cos(a), ln, r * math.sin(a)))) for a in ang]
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((r0[i], r1[i], r1[j], r0[j]))
        f.material_index = VKI_TEXTILE; f.smooth = True
        for l, (u, v) in zip(f.loops, ((i / segs, 0.0), (i / segs, 1.0), ((i + 1) / segs, 1.0), ((i + 1) / segs, 0.0))):
            l[k.uv].uv = vki_book_uv("scroll", u, v)
    caps = [(r0, False), (r1, True)]
    for ring, rev in caps:
        f = bm.faces.new(list(reversed(ring)) if rev else ring)
        f.material_index = VKI_TEXTILE
        for l, a in zip(f.loops, list(reversed(ang)) if rev else ang):
            l[k.uv].uv = vki_book_uv("scroll_end", 0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a))
    if ribbon:
        yb, mi = ribbon
        rr = r * 1.07
        b0 = [bm.verts.new(M @ Vector((rr * math.cos(a), yb - 0.007, rr * math.sin(a)))) for a in ang]
        b1 = [bm.verts.new(M @ Vector((rr * math.cos(a), yb + 0.007, rr * math.sin(a)))) for a in ang]
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((b0[i], b1[i], b1[j], b0[j])); f.material_index = mi; f.smooth = True
        for ring in (b0, list(reversed(b1))):
            bm.faces.new(ring).material_index = mi
    return r0 + r1


def vki_lib_open_book(k, M, W=0.42, D=0.30, colour="brown"):
    """an open book lying flat (W across both pages, D tall, on its local z = 0): two boards a little proud of the page
    blocks, the blocks dipping toward the gutter, the spread on top, a cloth ribbon over the bottom edge"""
    cv = "cover_" + colour
    for s in (-1, 1):
        Mb = M @ Matrix.Translation((s * (W / 4 + 0.002), 0, 0))
        vki_lib_box(k, Mb, W / 2 + 0.004, D + 0.012, 0.007,
                    {f: (cv, (0, 1), (0, 1)) for f in ("+z", "-z", "-y", "+y", "+x", "-x")})
        Mp = M @ Matrix.Translation((s * (W / 4 - 0.004), 0, 0.0065)) @ Matrix.Rotation(-s * math.radians(4.0), 4, "Y")
        vki_lib_box(k, Mp, W / 2 - 0.016, D - 0.008, 0.02,
                    {"+z": ("spread", (0.0, 0.5) if s < 0 else (0.5, 1.0), (0, 1)),
                     "-y": ("pages", (0, 1), (0, 1)), "+y": ("pages", (0, 1), (0, 1)),
                     "+x": ("pages", (0, 1), (0, 1)), "-x": ("pages", (0, 1), (0, 1)), "-z": ("pages", (0, 1), (0, 1))})
    rb = vki_home_box(k, 0.035, 0.047, -D / 2 - 0.012, 0.03, 0.026, 0.0285, CLOTH_A, bev=0.0)  # the ribbon on the right page
    bmesh.ops.transform(k.bm, matrix=M, verts=rb)


def vki_lib_case(k, W, D=0.36, H=2.0, shelves=(0.10, 0.56, 1.02, 1.48), seed=0):
    """a bookcase W wide: oak sides, a plinth, dark board backs, hewn shelf boards (tops at `shelves`) and a proud top
    board; returns (inner x0, x1, front line y, [(shelf top, clear height)])"""
    X, Y, t = W / 2, D / 2, VKI_LIB_T
    for a, b in ((-X, -X + t), (X - t, X)):
        vki_home_box(k, a, b, -Y, Y, 0.0, H - 0.06, WOOD, bev=0.008)
    vki_home_box(k, -X + t, X - t, -Y, -Y + 0.03, 0.0, shelves[0] - VKI_LIB_SHELF_T, WOOD, bev=0.006)   # plinth
    bk = vki_home_box(k, -X + t, X - t, Y - 0.02, Y, shelves[0] - VKI_LIB_SHELF_T, H - 0.06, WOOD, bev=0.0)
    k.set_dark(bk, 0.25)
    for j, z in enumerate(shelves):
        vki_home_top(k, -X + t - 0.004, X - t + 0.004, -Y + 0.006, Y - 0.021, z - VKI_LIB_SHELF_T, z, boards=1, bev=0.008,
                     seed=seed * 10 + j)
    vki_home_top(k, -X - 0.015, X + 0.015, -Y - 0.02, Y, H - 0.06, H, boards=1, bev=0.014, seed=seed * 10 + 9)
    tops = list(shelves) + [H - 0.06 + VKI_LIB_SHELF_T]
    return -X + t, X - t, -Y + 0.012, [(z, tops[i + 1] - VKI_LIB_SHELF_T - z) for i, z in enumerate(shelves)]


def vki_lib_bookcase_150(k):
    """bookcase 1.40 x 0.36 x 2.00, wall_floor: four shelves of books -- runs of a set, a gap or two with a book
    leaning into it, now and then a few lying flat"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(150)
    x0, x1, yf, sh = vki_lib_case(k, 1.40, seed=1)
    for z, clear in sh:
        vki_lib_shelf(k, rng, x0 + 0.004, x1 - 0.004, z, yf, clear - 0.025, 0.30)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.70, 0]])


def vki_lib_bookcase_075(k):
    """narrow bookcase 0.70 x 0.36 x 2.00, wall_floor: four shelves of books"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(75)
    x0, x1, yf, sh = vki_lib_case(k, 0.70, seed=2)
    for z, clear in sh:
        vki_lib_shelf(k, rng, x0 + 0.004, x1 - 0.004, z, yf, clear - 0.025, 0.30, flat=0.04)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.60, 0]])


def vki_lib_bookcase_sparse(k):
    """bookcase 1.40 x 0.36 x 2.00, half empty: a short run and a stack below, a few books leaning, a lidded crock and
    scrolls lying on another shelf, the top shelf nearly bare"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(1501)
    x0, x1, yf, sh = vki_lib_case(k, 1.40, seed=3)
    (z0, c0), (z1, c1), (z2, c2), (z3, c3) = sh
    vki_lib_shelf(k, rng, x0 + 0.004, x0 + 0.62, z0, yf, c0 - 0.025, 0.30, fill=1.0, flat=0.0)
    vki_lib_stack(k, rng, x1 - 0.22, yf + 0.13, z0, 3, 0.34, 0.27)
    vki_lib_shelf(k, rng, x0 + 0.004, x0 + 0.36, z1, yf, c1 - 0.025, 0.30, fill=0.9, lean=0.0, flat=0.0)
    for i in range(2):                                                          # two leaning in the empty half
        a = 0.28 + 0.12 * i; h_ = 0.30 - 0.03 * i; w_ = 0.05
        mnx = -w_ / 2 * math.cos(a) - h_ * math.sin(a); mnz = -w_ / 2 * math.sin(a)
        M = Matrix.Translation((x0 + 0.40 + 0.09 * i - mnx, yf + 0.12, z1 - mnz)) @ Matrix.Rotation(-a, 4, "Y")
        col, des = vki_lib_pick(rng)
        vki_lib_book(k, M, w_, 0.22, h_, col, des)
    vki_home_crock(k, x0 + 0.16, yf + 0.14, z2, r=0.10, h=0.24, lid=True, seed=7)
    for i in range(4):                                                          # scrolls lying along the shelf
        r = 0.028 + 0.006 * (i % 2)
        M = Matrix.Translation((x0 + 0.42 + 0.02 * (i % 2), yf + 0.05 + 0.065 * i, z2 + r)) @ Matrix.Rotation(-math.pi / 2, 4, "Z")
        vki_lib_scroll(k, M, r, 0.30 + 0.03 * (i % 3), ribbon=(0.15, CLOTH_A) if i == 1 else None)
    vki_lib_shelf(k, rng, x1 - 0.42, x1 - 0.004, z2, yf, c2 - 0.025, 0.30, fill=1.0, flat=0.0)
    vki_lib_stack(k, rng, x0 + 0.30, yf + 0.13, z3, 2, 0.30, 0.24)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.70, 0]])


def vki_lib_scrollrack(k):
    """scroll rack 1.20 x 0.34 x 1.30, wall_floor: five by five pigeonholes in thin dark oak boards on a plinth (dark,
    so the scrolls' pale ends read from the game camera), each holding two or three rolled scrolls, some lying on the
    others, their ends out; a ribbon round a few"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(120)
    W, D, H = 1.20, 0.34, 1.30
    X, Y, t, b = W / 2, D / 2, VKI_LIB_T, 0.02
    for a_, b_ in ((-X, -X + t), (X - t, X)):
        vki_home_box(k, a_, b_, -Y, Y, 0.0, H - 0.05, WOOD, bev=0.008)
    vki_home_box(k, -X + t, X - t, -Y, -Y + 0.03, 0.0, 0.08, WOOD, bev=0.006)
    bk = vki_home_box(k, -X + t, X - t, Y - 0.018, Y, 0.08, H - 0.05, WOOD, bev=0.0)
    k.set_dark(bk, 0.25)
    vki_home_top(k, -X - 0.012, X + 0.012, -Y - 0.015, Y, H - 0.05, H, boards=1, bev=0.012, seed=121)
    cols, rows = 5, 5
    z0, z1 = 0.08, H - 0.05
    ch = (z1 - z0 - b) / rows
    cw = (2 * (X - t) - b * (cols - 1)) / cols
    for r_ in range(rows + 1):                                                 # the shelves of the grid
        zb = z0 + r_ * ch
        if r_ == rows: break
        k.set_dark(vki_home_box(k, -X + t, X - t, -Y + 0.004, Y - 0.018, zb, zb + b, WOOD, bev=0.0), 0.15)
    for r_ in range(rows):
        za, zb = z0 + r_ * ch + b, z0 + (r_ + 1) * ch
        for c_ in range(1, cols):
            xc = -X + t + c_ * (cw + b) - b
            k.set_dark(vki_home_box(k, xc, xc + b, -Y + 0.004, Y - 0.018, za, zb if r_ < rows - 1 else z1, WOOD, bev=0.0), 0.15)
        for c_ in range(cols):                                                 # the scrolls in each hole
            cx0 = -X + t + c_ * (cw + b)
            n = rng.choice((2, 2, 3, 3))
            if rng.random() < 0.04: continue                                   # an empty hole
            placed = []
            for i in range(n):
                r = rng.uniform(0.022, 0.036)
                for _ in range(12):
                    px = rng.uniform(cx0 + r + 0.004, cx0 + cw - r - 0.004)
                    pz = za + r if len(placed) < 2 or rng.random() < 0.4 else za + r + rng.uniform(0.035, 0.05)
                    if all((px - qx) ** 2 + (pz - qz) ** 2 > (r + qr + 0.002) ** 2 for qx, qz, qr in placed):
                        break
                else:
                    continue
                if pz + r > zb - 0.005: continue
                placed.append((px, pz, r))
                M = Matrix.Translation((px, -Y + rng.uniform(0.01, 0.05), pz))
                rib = (rng.uniform(0.08, 0.16), CLOTH_A) if rng.random() < 0.18 else None
                vki_lib_scroll(k, M, r, rng.uniform(0.24, 0.28), segs=6, ribbon=rib)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.60, 0]])


def vki_lib_dress_books(k):
    """table dressing (origin on the table top, placed at z 0.80), within 0.80 x 0.40: a stack of three books, an
    open book, an ink pot and a quill"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(801)
    vki_lib_stack(k, rng, -0.26, 0.04, 0.0, 3, 0.28, 0.21, rz=0.15)
    vki_lib_open_book(k, Matrix.Translation((0.10, -0.03, 0.0)) @ Matrix.Rotation(-0.12, 4, "Z"), W=0.40, D=0.28,
                      colour="oxblood")
    vki_home_cyl(k, 0.36, 0.13, 0.0, 0.032, 0.026, 0.05, segs=VKI_HOME_SEG_D, mi=IRON)                # ink pot
    vki_home_box(k, 0.355, 0.367, 0.12, 0.13, 0.04, 0.19, PAPER, bev=0.0, rot=(0.30, 0.25, 0))         # the quill
    vki_home_meta(k, "table", "dressing", use=[], vki_table_z=VKI_HOME_TABLE_Z,
                  vki_fits=["SM_VKI_Prop_Table_Trestle_150", "SM_VKI_Prop_Table_Trestle_300", "SM_VKI_Prop_Table_Small"],
                  vki_note="origin on the table-top surface: place at the table's origin with z = 0.80")


def vki_lib_book_single(k):
    """one closed book lying on its back, 0.26 x 0.19 x 0.055, oxblood with gold tooling (a skill book, a tome on the
    ground)"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    vki_lib_lying(k, 0.0, 0.0, 0.0, 0.055, 0.19, 0.26, "oxblood", 0)
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="none")


def vki_lib_book_open(k):
    """an open book lying flat, 0.42 x 0.30 (origin on what it lies on: a table at z 0.80, a desk, a lectern)"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    vki_lib_open_book(k, Matrix(), W=0.42, D=0.30, colour="brown")
    vki_home_meta(k, "table", "dressing", use=[], vki_table_z=VKI_HOME_TABLE_Z, vki_nav="none",
                  vki_note="origin on the surface it lies on")


def vki_lib_books_pile(k):
    """a heap of books on the floor, about 1.05 x 0.60: two stacks, two lying loose at angles, one propped against a
    stack"""
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(902)
    vki_lib_stack(k, rng, -0.22, 0.05, 0.0, 5, 0.32, 0.25, rz=0.2)
    vki_lib_stack(k, rng, 0.16, 0.12, 0.0, 3, 0.30, 0.23, rz=-0.35)
    for x, y, rz in ((0.30, -0.16, 0.9), (-0.05, -0.20, -0.5)):
        col, des = vki_lib_pick(rng)
        vki_lib_lying(k, x, y, 0.0, rng.uniform(0.035, 0.06), 0.20, 0.27, col, des, rz=rz)
    a = 0.5                                                                     # propped against the big stack
    col, des = vki_lib_pick(rng)
    M = Matrix.Translation((-0.50, 0.05, 0.013)) @ Matrix.Rotation(0.2, 4, "Z") @ Matrix.Rotation(a, 4, "Y")
    vki_lib_book(k, M, 0.05, 0.22, 0.30, col, des)
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="none")


VKI_LIB_SPECS = [
    ("SM_VKI_Prop_Bookcase_150", vki_lib_bookcase_150, "prop"),
    ("SM_VKI_Prop_Bookcase_150_Sparse", vki_lib_bookcase_sparse, "prop"),
    ("SM_VKI_Prop_Bookcase_075", vki_lib_bookcase_075, "prop"),
    ("SM_VKI_Prop_ScrollRack_120", vki_lib_scrollrack, "prop"),
    ("SM_VKI_Prop_TableDress_Books", vki_lib_dress_books, "prop"),
    ("SM_VKI_Prop_Book", vki_lib_book_single, "prop"),
    ("SM_VKI_Prop_Book_Open", vki_lib_book_open, "prop"),
    ("SM_VKI_Prop_Books_Pile", vki_lib_books_pile, "prop"),
]
VKI_LIB_NAMES = [n_ for n_, _, _ in VKI_LIB_SPECS]
vki_register([(n_, fn_, {"grime": gr_}, "library") for n_, fn_, gr_ in VKI_LIB_SPECS])
