# ===================== WS_SLUMS: shacks and the slums' clutter (Saltmere's slums) =====================
# prefix slm_. Daniel 2026-10-25: model pieces for the slums -- shack walls of rough and patched planks and of wattle
# with mud, plank lean-to / patched thatch / sailcloth roofs, stilts for the shore shacks, and their junk.
# Executed after the other modules in the same namespace: borrows the humble set's hum_rod / hum_sq / hum_tube /
# hum_daub / hum_patch / hum_post and the water set's wat_seg / wat_rod / wat_rope / wat_sag / wat_annulus.
# Conventions as the other wall families: a wall module is 3 m along X centred on the cell edge, outer face toward -Y;
# corners sit at the origin facing -X / -Y; roofs are one 3 m bay, origin at the bay centre on the wall top (placed at
# z = SLM_HW). Shacks are one cell (3 m) deep. Stilt pieces have their deck top at z 0.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

SLM_HW = 2.25        # shack wall top
SLM_F = -0.05        # outer face of the planks (wall-local y)
SLM_T = 0.04         # plank thickness
SLM_LEAN = 0.85      # the lean-to's rise over the 3 m depth (front low, back high)
SLM_RIDGE = 1.15     # the thatch / sail gable's ridge over the wall top
SLM_STYLE = {"plaster": "Daub", "roof": "Thatch"}

# ================================================================ helpers
def slm_board(k, x0, x1, z0, z1, y=SLM_F, t=SLM_T, mi=PLANKS, tilt=0.0, roll=0.0):
    """an upright board from x0 to x1, z0 to z1, its outer face at y (tilted in its plane / leaning out)"""
    k.box(((x0 + x1) / 2, y + t / 2, (z0 + z1) / 2), (x1 - x0, t, z1 - z0), mi, rot=(roll, tilt, 0), bevel=0.008)


def slm_frame(k, seed, top=True):
    """the hidden frame: a sole plate on two stones, inside battens, a top plate"""
    k.box((0, 0.04, 0.12), (2.96, 0.1, 0.12), WOOD, bevel=0.02)                         # sole plate z 0.06..0.18
    for x in (-0.95, 0.95): rock(k, (x, 0.03, 0.02), (0.34, 0.26, 0.2), seed=seed + int(x * 10), tilt=0.05)
    for z in (0.55, 1.75): k.box((0, 0.05, z), (2.92, 0.05, 0.09), WOOD, bevel=0.012)    # battens inside
    if top: k.box((0, 0.05, SLM_HW - 0.05), (2.96, 0.1, 0.1), WOOD, bevel=0.015)        # top plate


def slm_boards(k, rnd, x0, x1, z0, z1, skip=(), kinds=(PLANKS, PLANKS, PLANKS, WOOD, BARK_OAK)):
    """a run of upright boards from x0 to x1 (uneven widths, small gaps, ragged ends); skip: (xa, xb, za, zb) holes"""
    x = x0
    while x < x1 - 0.05:
        w = min(rnd.uniform(0.18, 0.3), x1 - x)
        if x1 - (x + w) < 0.12: w = x1 - x
        a, b = x + rnd.uniform(0.0, 0.012), x + w
        mi = rnd.choice(kinds)
        lo = z0 + rnd.uniform(-0.02, 0.03); hi = z1 + rnd.uniform(-0.05, 0.03)
        if SLM_HW - 0.012 < hi < SLM_HW + 0.008: hi = SLM_HW + 0.012                  # never level with the top plate
        y = SLM_F + rnd.uniform(0.0, 0.007)
        segs_ = [(lo, hi)]
        for (xa, xb, za, zb) in skip:
            if b > xa and a < xb:
                nxt = []
                for (p, q) in segs_:
                    if q <= za or p >= zb: nxt.append((p, q)); continue
                    if za > p: nxt.append((p, za))
                    if zb < q: nxt.append((zb, q))
                segs_ = nxt
                a, b = max(a, x), b
        for (p, q) in segs_:
            if q - p > 0.06:
                slm_board(k, a, b, p, q, y=y, mi=mi, tilt=rnd.uniform(-0.012, 0.012))
        x += w


def slm_door(k, rnd, x0, x1, z1, curtain=False):
    """a doorway from x0 to x1 up to z1: a crooked plank door standing ajar (or a sack curtain), a lintel board"""
    k.box(((x0 + x1) / 2, SLM_F - 0.012, z1 + 0.06), (x1 - x0 + 0.24, 0.05, 0.12), WOOD, bevel=0.012)   # lintel
    for x in (x0, x1): k.box((x, SLM_F + 0.02, (0.18 + z1) / 2), (0.08, 0.06, z1 - 0.18), WOOD, bevel=0.012)
    k.quad([(x0 + 0.04, 0.09, 0.18), (x1 - 0.04, 0.09, 0.18), (x1 - 0.04, 0.09, z1), (x0 + 0.04, 0.09, z1)], VOID,
           uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])                                                   # the dark inside
    if curtain:
        n = 6; W = x1 - x0 - 0.06
        for i in range(n):
            xa = x0 + 0.03 + W * i / n; xb = xa + W / n + 0.01
            k.box(((xa + xb) / 2, SLM_F - 0.02 + 0.012 * math.sin(i * 1.9), (0.3 + z1) / 2 + 0.05),
                  (xb - xa, 0.012, z1 - 0.3), BURLAP, rot=(0, 0, 0.06 * math.sin(i * 2.3)), bevel=0.003)
        return
    sub = Kit(); W = x1 - x0 - 0.08; H = z1 - 0.22
    xs = 0.0
    while xs < W - 0.04:
        w = min(rnd.uniform(0.15, 0.22), W - xs)
        sub.box((xs + w / 2, 0, H / 2), (w - 0.006, 0.035, H - rnd.uniform(0.0, 0.04)), PLANKS, bevel=0.006)
        xs += w
    for z in (0.25, H - 0.25): sub.box((W / 2, 0.03, z), (W - 0.04, 0.03, 0.1), WOOD, bevel=0.008)
    sub.box((W / 2, 0.03, H / 2), (math.hypot(W - 0.1, H - 0.6), 0.03, 0.09), WOOD,
            rot=(0, -math.atan2(H - 0.6, W - 0.1), 0), bevel=0.008)                               # the brace
    for z in (0.3, H - 0.3): sub.box((0.12, -0.024, z), (0.24, 0.012, 0.04), IRON, bevel=0.003)   # strap hinges
    ang = math.radians(rnd.uniform(28, 40))
    merge_kit(k, sub, Matrix.Translation((x0 + 0.04, SLM_F - 0.04, 0.2)) @ Matrix.Rotation(ang, 4, "Z"))


def slm_window(k, rnd, x0, x1, z0, z1, flap=PLANKS):
    """a small window hole with a sill and a lintel, its board flap propped open on a stick (or a hanging rag)"""
    k.box(((x0 + x1) / 2, SLM_F - 0.015, z0 - 0.03), (x1 - x0 + 0.18, 0.07, 0.06), WOOD, bevel=0.01)
    k.box(((x0 + x1) / 2, SLM_F - 0.012, z1 + 0.03), (x1 - x0 + 0.16, 0.05, 0.06), WOOD, bevel=0.01)
    k.quad([(x0, 0.09, z0), (x1, 0.09, z0), (x1, 0.09, z1), (x0, 0.09, z1)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    if flap == BURLAP:
        k.box(((x0 + x1) / 2 + 0.05, SLM_F - 0.03, (z0 + z1) / 2 + 0.02), (x1 - x0 - 0.1, 0.012, z1 - z0 - 0.04),
              BURLAP, rot=(0.12, 0.05, 0), bevel=0.003)
        return
    sub = Kit(); W = x1 - x0 + 0.06; H = z1 - z0 + 0.06; n = 3
    for i in range(n): sub.box((-W / 2 + W * (i + 0.5) / n, 0, -H / 2), (W / n - 0.006, 0.03, H), flap, bevel=0.006)
    sub.box((0, 0.025, -H * 0.6), (W - 0.04, 0.025, 0.06), WOOD, bevel=0.006)
    merge_kit(k, sub, Matrix.Translation(((x0 + x1) / 2, SLM_F - 0.02, z1 + 0.04)) @ Matrix.Rotation(math.radians(-50), 4, "X"))
    zb = z1 + 0.04 - H * math.cos(math.radians(50)); yb = SLM_F - 0.02 - H * math.sin(math.radians(50))
    hum_rod(k, ((x0 + x1) / 2 + 0.1, SLM_F - 0.03, z0 - 0.02), ((x0 + x1) / 2 + 0.1, yb + 0.03, zb + 0.03), 0.018, segs=5)


def slm_patches(k, rnd, holes):
    """the patched wall's mending: boards nailed across, a hide, sacking, a gap stuffed with straw"""
    def clear(x, z, w, h): return all(not (x + w / 2 > a and x - w / 2 < b and z + h / 2 > c and z - h / 2 < d) for a, b, c, d in holes)
    tries = 0; made = 0; kinds = ["cross", "hide", "sack", "cross", "straw"]
    while made < 4 and tries < 40:
        tries += 1
        kind = kinds[made % len(kinds)]
        x = rnd.uniform(-1.15, 1.15); z = rnd.uniform(0.45, 1.9)
        if kind == "cross":
            w, h = rnd.uniform(0.7, 1.1), 0.16
            if not clear(x, z, w, h): continue
            k.box((x, SLM_F - 0.022, z), (w, 0.035, h), rnd.choice((WOOD, PLANKS)), rot=(0, rnd.uniform(-0.12, 0.12), 0), bevel=0.008)
        elif kind == "hide":
            w, h = rnd.uniform(0.45, 0.65), rnd.uniform(0.4, 0.55)
            if not clear(x, z, w, h): continue
            hum_sq(k, (x, SLM_F - 0.012, z), (w / 2, 0.012, h / 2), e=0.35, nu=10, nv=4, mi=HIDE,
                   disp=lambda n: 1.0 + 0.08 * math.sin(5 * n.x + 1) * math.sin(4 * n.z + 2))
        elif kind == "sack":
            w, h = rnd.uniform(0.4, 0.55), rnd.uniform(0.35, 0.5)
            if not clear(x, z, w, h): continue
            k.box((x, SLM_F - 0.01, z), (w, 0.012, h), BURLAP, rot=(0, rnd.uniform(-0.2, 0.2), 0), bevel=0.003)
        else:
            w, h = 0.22, rnd.uniform(0.3, 0.45)
            if not clear(x, z, w, h): continue
            hum_sq(k, (x, SLM_F + 0.01, z), (w / 2, 0.05, h / 2), e=0.6, nu=8, nv=5, mi=HAY,
                   disp=lambda n: 1.0 + 0.12 * math.sin(9 * n.z + 1.3))
        holes = list(holes) + [(x - w / 2, x + w / 2, z - h / 2, z + h / 2)]
        made += 1


# ================================================================ WALLS (3 m, outer face -Y)
SLM_DOOR = (-1.05, -0.2, 1.85)        # x0, x1, top: the doorway (off centre: the shack's door is never in the middle)
SLM_WIN = (0.25, 0.85, 1.05, 1.5)     # x0, x1, z0, z1


def slm_wall_planks(k, opening="", patched=False, seed=0):
    rnd = random.Random(seed)
    slm_frame(k, seed)
    holes = []
    if opening == "D": holes.append((SLM_DOOR[0], SLM_DOOR[1], 0.0, SLM_DOOR[2]))
    if opening == "W": holes.append(SLM_WIN)
    skip = [(a, b, c, d) for a, b, c, d in holes]
    slm_boards(k, rnd, -1.5, 1.5, 0.1, SLM_HW - 0.03, skip=skip,
               kinds=(PLANKS, PLANKS, WOOD, BARK_OAK, PLANKS) if patched else (PLANKS, PLANKS, PLANKS, WOOD, BARK_OAK))
    if opening == "D": slm_door(k, rnd, *SLM_DOOR)
    if opening == "W": slm_window(k, rnd, *SLM_WIN, flap=BURLAP if patched else PLANKS)
    if patched: slm_patches(k, rnd, holes)


def slm_daub(k, x0, x1, z0, z1, seed, face=-0.075, back=0.03, mi=PLASTER):
    """mud daub over wattle: a slab, subdivided, its outer face lumpy and sagging (more than the cottages')"""
    vs = k.box(((x0 + x1) / 2, (face + back) / 2, (z0 + z1) / 2), (x1 - x0, back - face, z1 - z0), mi, bevel=0)
    nx = max(1, int(round((x1 - x0) / 0.25))); nz = max(1, int(round((z1 - z0) / 0.28)))
    vs = hum_cut(k, vs, [x0 + (x1 - x0) * i / nx for i in range(1, nx)], [z0 + (z1 - z0) * j / nz for j in range(1, nz)])
    rnd = random.Random(seed)
    for v in sorted(vs, key=lambda v: (round(v.co.x, 3), round(v.co.z, 3), round(v.co.y, 3))):
        if v.co.y > face + 0.005: continue
        x, z = v.co.x, v.co.z
        if x0 + 0.01 < x < x1 - 0.01 and z0 + 0.01 < z < z1 - 0.01:
            v.co.y -= 0.02 * math.sin(math.pi * (x - x0) / (x1 - x0)) * math.sin(math.pi * (z - z0) / (z1 - z0)) + rnd.uniform(-0.012, 0.012)
            v.co.x += rnd.uniform(-0.015, 0.015); v.co.z += rnd.uniform(-0.015, 0.015)


def slm_wall_wattle(k, opening="", seed=0):
    """wattle and mud between rough posts, the mud fallen off in patches; a sack over the door or the window"""
    rnd = random.Random(seed)
    slm_frame(k, seed, top=False)
    k.box((0, 0.0, SLM_HW - 0.06), (2.96, 0.16, 0.12), WOOD, bevel=0.02)            # top plate
    posts = (-0.7, 0.7) if opening == "" else ((0.15,) if opening == "W" else (0.6,))
    for x in posts: hum_rod(k, (x + rnd.uniform(-0.04, 0.04), -0.02, 0.15), (x, -0.02, SLM_HW - 0.1), 0.065, 0.055, segs=6)
    if opening == "D":
        x0, x1, zt = SLM_DOOR
        slm_daub(k, -1.5, x0 - 0.04, 0.18, SLM_HW - 0.12, seed)
        slm_daub(k, x1 + 0.04, 1.5, 0.18, SLM_HW - 0.12, seed + 1)
        slm_daub(k, x0 - 0.04, x1 + 0.04, zt + 0.12, SLM_HW - 0.12, seed + 2)
        slm_door(k, rnd, x0, x1, zt, curtain=True)
        spots = [(-1.3, 1.2), (0.95, 0.75), (0.75, 1.75)]
    elif opening == "W":
        x0, x1, z0, z1 = SLM_WIN
        slm_daub(k, -1.5, x0 - 0.04, 0.18, SLM_HW - 0.12, seed)
        slm_daub(k, x1 + 0.04, 1.5, 0.18, SLM_HW - 0.12, seed + 1)
        slm_daub(k, x0 - 0.04, x1 + 0.04, 0.18, z0 - 0.06, seed + 2)
        slm_daub(k, x0 - 0.04, x1 + 0.04, z1 + 0.06, SLM_HW - 0.12, seed + 3)
        slm_window(k, rnd, x0, x1, z0, z1, flap=BURLAP)
        spots = [(-0.9, 1.4), (-0.45, 0.6), (1.2, 0.85)]
    else:
        slm_daub(k, -1.5, 1.5, 0.18, SLM_HW - 0.12, seed)
        spots = [(-1.0, 1.45), (0.2, 0.7), (0.95, 1.6), (-0.25, 1.9)]
    for i, (x, z) in enumerate(spots):
        hum_patch(k, (x, -0.09, z), (1, 0, 0), (0, 0, 1), (0, -1, 0), rnd.uniform(0.32, 0.5), rnd.uniform(0.26, 0.42), seed=seed * 7 + i)
    k.project([f for f in k.bm.faces if f.material_index == PLASTER], SOIL)          # mud, not the cottages' daub


def slm_corner(k):
    """a rough corner post on a flat stone"""
    hum_rod(k, (-0.05, -0.05, -0.3), (-0.06, -0.05, SLM_HW + 0.06), 0.085, 0.075, segs=7, mi=WOOD)
    rock(k, (-0.06, -0.06, 0.03), (0.34, 0.34, 0.16), seed=31, tilt=0.04)


# ================================================================ ROOFS (one 3 m bay, origin at the wall top)
def slm_roof_leanto(k, left=False, right=False, seed=0):
    """plank lean-to: low over the front wall (y -1.5), high over the back (y +1.5); boards down the slope,
    overlapping, a few short or gone (a hide over the gap), stones holding them down; the ends' triangles boarded"""
    rnd = random.Random(seed)
    a = math.atan2(SLM_LEAN, 3.0)
    def z_of(y): return (y + 1.5) * SLM_LEAN / 3.0
    x0 = -1.75 if left else -1.5; x1 = 1.75 if right else 1.5
    for x in (-1.2, 0.0, 1.2):                                                          # rafters
        wat_seg(k, (x, -1.9, z_of(-1.9) + 0.05), (x, 1.75, z_of(1.75) + 0.05), 0.09, 0.11, WOOD, bevel=0.015)
    k.box((0, 1.5, SLM_LEAN / 2), (3.0, 0.1, 0.1), WOOD, bevel=0.012)                   # (hidden) back strut rail
    k.box((0, 1.48, SLM_LEAN - 0.02), (3.0, 0.14, 0.1), WOOD, bevel=0.015)               # back plate
    for x in ((-1.4, 1.4) if (left or right) else (0.0,)):
        k.box((x, 1.48, SLM_LEAN / 2 - 0.03), (0.1, 0.1, SLM_LEAN - 0.06), WOOD, bevel=0.012)   # stub posts
    # the back's strip of boards over the back wall, up to the roof
    xb = -1.5
    while xb < 1.5 - 0.05:
        w = min(rnd.uniform(0.2, 0.3), 1.5 - xb)
        if 1.5 - (xb + w) < 0.12: w = 1.5 - xb
        k.box((xb + w / 2, 1.5 + 0.06 + rnd.uniform(0, 0.006), (SLM_LEAN + 0.02) / 2 - 0.02),
              (w - 0.006, SLM_T, SLM_LEAN + 0.02), rnd.choice((PLANKS, PLANKS, WOOD)), bevel=0.006)
        xb += w
    # roof boards down the slope
    x = x0; i = 0
    while x < x1 - 0.05:
        w = min(rnd.uniform(0.22, 0.3), x1 - x)
        if x1 - (x + w) < 0.12: w = x1 - x
        y0 = -1.95 + rnd.uniform(-0.04, 0.03); y1 = 1.78 + rnd.uniform(-0.03, 0.04)
        lift = 0.13 + (0.025 if i % 2 else 0.0)
        gone = rnd.random() < 0.08 and x0 + 0.4 < x < x1 - 0.6
        if gone:
            ym = rnd.uniform(-0.6, 0.6); yy = (y0 + y1) / 2
            for (p, q) in ((y0, ym - 0.35), (ym + 0.35, y1)):
                c = (p + q) / 2
                k.box((x + w / 2, c, z_of(c) + lift), (w - 0.01, q - p, 0.035), PLANKS, rot=(a, 0, 0), bevel=0.006)
            c = ym
            hum_sq(k, (x + w / 2, c, z_of(c) + lift + 0.01), (w * 0.9, 0.45, 0.02), e=0.4, nu=10, nv=4, mi=HIDE,
                   rot=Matrix.Rotation(a, 4, "X"))
        else:
            c = (y0 + y1) / 2
            k.box((x + w / 2, c, z_of(c) + lift), (w - 0.01, y1 - y0, 0.035), rnd.choice((PLANKS, PLANKS, PLANKS, WOOD)),
                  rot=(a, rnd.uniform(-0.01, 0.01), rnd.uniform(-0.012, 0.012)), bevel=0.006)
        x += w; i += 1
    for j in range(rnd.randint(1, 2)):                                                  # stones holding it down
        y = rnd.uniform(-1.2, 1.0); xs = rnd.uniform(-1.1, 1.1)
        rock(k, (xs, y, z_of(y) + 0.23), (0.24, 0.2, 0.14), seed=seed * 3 + j, rot_z=a, tilt=0.05)
    for side, on in ((-1, left), (1, right)):                                           # the end's triangle
        if not on: continue
        xe = side * 1.5 - side * 0.03
        y = -1.5
        while y < 1.5 - 0.05:
            w = min(rnd.uniform(0.2, 0.3), 1.5 - y)
            if 1.5 - (y + w) < 0.12: w = 1.5 - y
            top = z_of(y + w / 2) + 0.08
            k.box((xe, y + w / 2, top / 2 - 0.02), (SLM_T, w - 0.006, top + 0.04), rnd.choice((PLANKS, PLANKS, WOOD)), bevel=0.006)
            y += w


def slm_thatch_side(k, s, x0, x1, rnd):
    """one slope of the patched thatch gable: a lumpy slab from the eave to the ridge, fresh straw patches"""
    a = math.atan2(SLM_RIDGE + 0.2, 1.75)
    L = math.hypot(1.75 + 0.15, SLM_RIDGE + 0.35)
    c = Vector(((x0 + x1) / 2, s * (1.75 - 0.15) / 2 - s * 0.05, (SLM_RIDGE - 0.2) / 2 + 0.12))
    k.box(tuple(c), (x1 - x0, L, 0.26), THATCH, rot=(-s * a, 0, 0), bevel=0.05, segs=2, jitter=0.02, seed=rnd.randrange(999))
    px0 = rnd.uniform(x0 + 0.5, (x0 + x1) / 2 - 0.4)
    for j in range(2):                                                                  # fresh straw patches, apart
        u = rnd.uniform(-0.5, -0.15) if j == 0 else rnd.uniform(0.05, 0.35)
        px = px0 if j == 0 else rnd.uniform((x0 + x1) / 2 + 0.4, x1 - 0.5)
        p = c + Vector((px - c.x, s * u * math.cos(a) * L / 2 * 1.0, -u * math.sin(a) * L / 2 + 0.15))
        hum_sq(k, tuple(p), (rnd.uniform(0.35, 0.55), rnd.uniform(0.3, 0.42), 0.05), e=0.5, nu=10, nv=4, mi=HAY,
               rot=Matrix.Rotation(-s * a, 4, "X"))
    pts = [(x0, s * 1.95, -0.2), ((x0 + x1) / 2, s * 1.97, -0.22), (x1, s * 1.95, -0.2)]
    hum_tube(k, pts, 0.11, segs=7, mi=THATCH, lump=0.12, seed=rnd.random() * 9)        # the eave roll
    return a


def slm_roof_thatch(k, ends=0, seed=0):
    """a low patched thatch gable over a 3 m deep shack (ridge along X); ends: 0 mid, 1 the +X end, 2 both ends"""
    rnd = random.Random(seed)
    x0 = -1.75 if ends == 2 else -1.5; x1 = 1.75 if ends >= 1 else 1.5
    for x in (-1.1, 1.1):                                                               # couples under it
        for s in (-1, 1):
            wat_seg(k, (x, s * 1.6, -0.05), (x, 0.0, SLM_RIDGE + 0.02), 0.08, 0.09, WOOD, bevel=0.012)
    hum_rod(k, (x0, 0, SLM_RIDGE + 0.02), (x1, 0, SLM_RIDGE + 0.02), 0.06, segs=6)       # ridge pole
    for s in (-1, 1): slm_thatch_side(k, s, x0, x1, rnd)
    hum_tube(k, [(x0, 0, SLM_RIDGE + 0.16), (0, 0, SLM_RIDGE + 0.19), (x1, 0, SLM_RIDGE + 0.16)], 0.16, segs=8,
             mi=THATCH, lump=0.1, seed=seed + 0.5)                                     # ridge roll
    # a sack patch and a rope over the ridge with a stone weight hanging each side
    xs = rnd.uniform(-0.8, 0.8); a = math.atan2(SLM_RIDGE + 0.2, 1.75)
    k.box((xs, -0.8, SLM_RIDGE * 0.5 + 0.28), (0.6, 0.62, 0.015), BURLAP, rot=(a, 0, rnd.uniform(-0.2, 0.2)), bevel=0.003)
    xr = rnd.uniform(-0.9, 0.9)
    for s in (-1, 1):
        wat_rope(k, [Vector((xr, 0, SLM_RIDGE + 0.33)), Vector((xr, s * 0.9, SLM_RIDGE * 0.55 + 0.32)),
                     Vector((xr, s * 1.75, 0.0)), Vector((xr, s * 1.95, -0.35))], r=0.018)
        rock(k, (xr, s * 1.97, -0.5), (0.22, 0.2, 0.24), seed=seed * 5 + s, tilt=0.1)
    for e in ((1,) if ends == 1 else ((-1, 1) if ends == 2 else ())):                   # the gable's boards
        xe = e * 1.47
        y = -1.5
        while y < 1.5 - 0.05:
            w = min(rnd.uniform(0.2, 0.3), 1.5 - y)
            if 1.5 - (y + w) < 0.12: w = 1.5 - y
            top = SLM_RIDGE * (1 - abs(y + w / 2) / 1.6) + 0.02
            if top > 0.05:
                k.box((xe, y + w / 2, top / 2 - 0.03), (SLM_T, w - 0.006, top + 0.06), rnd.choice((PLANKS, WOOD)), bevel=0.006)
            y += w


def slm_sheet(k, P, nu, nv, mi, t=0.012):
    """a thin solid sheet over a grid P(i, j) (i 0..nu, j 0..nv), t thick along its own normal (so a hanging or upright
    sheet keeps its thickness: two layers offset sideways would lie nearly in one plane), both sides drawn, edges closed"""
    G = [[Vector(P(i, j)) for j in range(nv + 1)] for i in range(nu + 1)]
    def N(i, j):
        du = G[min(i + 1, nu)][j] - G[max(i - 1, 0)][j]; dv = G[i][min(j + 1, nv)] - G[i][max(j - 1, 0)]
        n = du.cross(dv)
        return n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))
    top = [[k.bm.verts.new(G[i][j]) for j in range(nv + 1)] for i in range(nu + 1)]
    bot = [[k.bm.verts.new(G[i][j] - N(i, j) * t) for j in range(nv + 1)] for i in range(nu + 1)]
    fs = []
    for i in range(nu):
        for j in range(nv):
            fs.append(k.bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1])))
            fs.append(k.bm.faces.new((bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j], bot[i][j])))
    ring = [(i, 0) for i in range(nu)] + [(nu, j) for j in range(nv)] + [(i, nv) for i in range(nu, 0, -1)] + [(0, j) for j in range(nv, 0, -1)]
    for n_ in range(len(ring)):
        (i, j), (i2, j2) = ring[n_], ring[(n_ + 1) % len(ring)]
        fs.append(k.bm.faces.new((top[i][j], bot[i][j], bot[i2][j2], top[i2][j2])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)                                      # closed: every face outward
    k.bm.normal_update()
    k.project(fs, mi)
    return fs


def slm_roof_sail(k, ends=0, seed=0):
    """an old sail thrown over a ridge pole and tied down to the wall tops, sagging between the couples; a patch;
    ends: 0 mid, 1 forked pole at the +X end, 2 both ends"""
    rnd = random.Random(seed)
    x0 = -1.65 if ends == 2 else -1.5; x1 = 1.65 if ends >= 1 else 1.5
    R = SLM_RIDGE - 0.1
    hum_rod(k, (x0 - 0.1 if ends == 2 else x0, 0, R), (x1 + 0.1 if ends >= 1 else x1, 0, R), 0.055, segs=6)
    for e in ((1,) if ends == 1 else ((-1, 1) if ends == 2 else ())):                   # forked poles
        xe = e * 1.45
        hum_rod(k, (xe, 0, -0.1), (xe, 0, R - 0.08), 0.06, segs=6)
        for s in (-1, 1): hum_rod(k, (xe, 0, R - 0.1), (xe, s * 0.1, R + 0.12), 0.035, segs=5)
    nu, nv = 8, 10
    def P(i, j):
        x = x0 + (x1 - x0) * i / nu; v = -1.0 + 2.0 * j / nv                           # v -1 (front) .. 1 (back)
        y = v * 1.72
        z = R * (1 - abs(v)) + 0.06 - 0.12 * (1 - abs(v)) * math.sin(math.pi * (x - x0) / (x1 - x0)) * (1 if ends == 0 else 0.6)
        z -= 0.05 * math.sin(3.1 * x + 2 * v + seed) * (1 - abs(v)) ** 0.5
        if abs(v) > 0.85: z -= (abs(v) - 0.85) * 1.3                                     # the hem hanging over the wall top
        return Vector((x, y, z))
    slm_sheet(k, P, nu, nv, BURLAP)
    px = rnd.uniform(x0 + 0.5, x1 - 0.9); pv = rnd.uniform(-0.6, -0.25)
    def Q(i, j):
        x = px + 0.7 * i / 3; v = pv + 0.3 * j / 3
        p = P(0, 0); y = v * 1.72
        z = R * (1 - abs(v)) + 0.075 - 0.12 * (1 - abs(v)) * math.sin(math.pi * (x - x0) / (x1 - x0)) * (1 if ends == 0 else 0.6)
        z -= 0.05 * math.sin(3.1 * x + 2 * v + seed) * (1 - abs(v)) ** 0.5
        return Vector((x, y, z))
    slm_sheet(k, Q, 3, 3, CLOTH_A, t=0.008)                                             # a red patch
    for e in ((1,) if ends == 1 else ((-1, 1) if ends == 2 else ())):                   # the gable's canvas flap
        xe = e * 1.5
        def F(i, j, xe=xe):
            y = -1.45 + 2.9 * i / 6
            top = max(0.03, R * (1 - abs(y) / 1.72) - 0.02)
            return Vector((xe + e * 0.04 * math.sin(math.pi * j / 4) * math.sin(math.pi * i / 6), y, -0.02 + top * j / 4))
        slm_sheet(k, F, 6, 4, BURLAP, t=0.012)
    for s in (-1, 1):                                                                   # ties to the wall top
        for x in ((x0 + 0.3, x1 - 0.3) if ends else (0.0,)):
            wat_rope(k, [Vector((x, s * 1.66, 0.02)), Vector((x, s * 1.62, -0.12)), Vector((x, s * 1.55, -0.22))], r=0.014)


# ================================================================ STILTS (deck top at z 0)
def slm_stilt_posts(k, pts, rnd, z1=-0.12, z0=-3.2):
    for (x, y) in pts:
        lean = (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12))
        mid = Vector((x - lean[0] * 0.5, y - lean[1] * 0.5, -1.6))
        hum_rod(k, (x - lean[0], y - lean[1], z0), tuple(mid), 0.085, 0.08, segs=7, mi=BARK_MOSSY)
        hum_rod(k, tuple(mid), (x, y, z1), 0.08, 0.075, segs=7, mi=WOOD)


def slm_deck(k, x0, x1, y0, y1, rnd, top=0.0):
    """deck boards along X across y0..y1, top at `top`, on joists along Y"""
    y = y0
    while y < y1 - 0.05:
        w = min(rnd.uniform(0.2, 0.28), y1 - y)
        if y1 - (y + w) < 0.12: w = y1 - y
        if rnd.random() < 0.06:                                                         # a broken board
            k.box((x0 + 0.6, y + w / 2, top - 0.02), (1.1, w - 0.01, 0.04), PLANKS, rot=(0, 0.04, 0), bevel=0.006)
        else:
            k.box(((x0 + x1) / 2, y + w / 2, top - 0.02 - rnd.uniform(0, 0.006)), (x1 - x0 - rnd.uniform(0, 0.04), w - 0.01, 0.04),
                  rnd.choice((PLANKS, PLANKS, WOOD)), rot=(0, 0, rnd.uniform(-0.01, 0.01)), bevel=0.006)
        y += w
    for x in (x0 + 0.25, (x0 + x1) / 2, x1 - 0.25):
        k.box((x, (y0 + y1) / 2, top - 0.11), (0.1, y1 - y0 - 0.04, 0.14), WOOD, bevel=0.015)


def slm_stilts(k, seed=4):
    """a 3 x 3 m platform for a shack, on six crooked stilts with braces, deck top at z 0"""
    rnd = random.Random(seed)
    slm_deck(k, -1.5, 1.5, -1.5, 1.5, rnd)
    for y in (-1.35, 0.0, 1.35): k.box((0, y, -0.25), (2.95, 0.14, 0.14), WOOD, bevel=0.02)     # bearers
    pts = [(-1.3, -1.35), (1.3, -1.35), (-1.3, 1.35), (1.3, 1.35), (0.0, -1.35), (0.0, 1.35)]
    slm_stilt_posts(k, pts, rnd, z1=-0.3)
    for y in (-1.35, 1.35):
        wat_seg(k, (-1.3, y, -2.4), (0.0, y, -0.45), 0.08, 0.1, WOOD, bevel=0.015)
        wat_seg(k, (1.3, y, -2.4), (0.0, y, -0.45), 0.08, 0.1, WOOD, bevel=0.015)
    for x in (-1.3, 1.3): wat_seg(k, (x, -1.35, -2.0), (x, 1.35, -0.5), 0.08, 0.1, WOOD, bevel=0.015)


def slm_walkway(k, seed=5):
    """a 3 m plank walkway along X, 1.2 m wide, on two pairs of stilts, a rope rail on one side"""
    rnd = random.Random(seed)
    y = -0.6
    while y < 0.6 - 0.05:
        w = min(rnd.uniform(0.18, 0.26), 0.6 - y)
        if 0.6 - (y + w) < 0.1: w = 0.6 - y
        k.box((0, y + w / 2, -0.02), (3.0 - rnd.uniform(0, 0.05), w - 0.012, 0.04), rnd.choice((PLANKS, WOOD)),
              rot=(0, 0, rnd.uniform(-0.012, 0.012)), bevel=0.006)
        y += w
    for x in (-1.2, 1.2): k.box((x, 0, -0.12), (0.12, 1.3, 0.14), WOOD, bevel=0.02)
    for y in (-0.5, 0.5): k.box((0, y, -0.1), (2.98, 0.1, 0.1), WOOD, bevel=0.015)
    slm_stilt_posts(k, [(-1.2, -0.55), (-1.2, 0.55), (1.2, -0.55), (1.2, 0.55)], rnd, z1=-0.18)
    for x in (-1.2, 1.2): hum_rod(k, (x, -0.66, -0.1), (x - 0.02, -0.66, 0.95), 0.045, segs=6)
    wat_rope(k, wat_sag(Vector((-1.5, -0.66, 0.88)), Vector((1.5, -0.66, 0.88)), 0.12, n=8), r=0.02)


def slm_stilt_ladder(k):
    """a ladder from a deck's edge (origin, top at z 0) down 2.6 m, leaning out toward -Y"""
    for x in (-0.22, 0.22): hum_rod(k, (x, -0.75, -2.65), (x, -0.02, 0.35), 0.035, segs=6)
    for i in range(8):
        t = (i + 0.5) / 8.5; z = -2.65 + (3.0) * t; y = -0.75 + 0.73 * t
        if i == 5: continue                                                             # one rung gone
        hum_rod(k, (-0.24, y, z), (0.24, y, z), 0.02, segs=5)


# ================================================================ PROPS
def slm_junk_pile(k, seed=6):
    """a heap of broken boards, a cartwheel, pottery shards and rags against a wall"""
    rnd = random.Random(seed)
    for i in range(9):                                                                  # boards
        L = rnd.uniform(0.6, 1.5); x = rnd.uniform(-0.6, 0.6); y = rnd.uniform(-0.3, 0.35)
        k.box((x, y, 0.06 + i * 0.035), (L, rnd.uniform(0.12, 0.22), 0.03), rnd.choice((PLANKS, WOOD, PLANKS)),
              rot=(rnd.uniform(-0.25, 0.25), rnd.uniform(-0.3, 0.3), rnd.uniform(0, math.pi)), bevel=0.006)
    sub = Kit()                                                                         # a broken cartwheel
    wat_annulus(sub, (0, 0, 0), 0.38, 0.45, 0.07, WOOD, n=14, axis="Z")
    for j in range(5):
        a_ = 2 * math.pi * j / 6
        sub.box((0.2 * math.cos(a_), 0.2 * math.sin(a_), 0), (0.4, 0.05, 0.04), WOOD, rot=(0, 0, a_), bevel=0.006)
    _cyl(sub, (0, 0, 0), 0.09, 0.09, 0.14, 8, WOOD)
    merge_kit(k, sub, Matrix.Translation((0.35, 0.3, 0.48)) @ Matrix.Rotation(math.radians(70), 4, "X"))
    for i in range(5):                                                                  # shards
        k.box((rnd.uniform(-0.7, 0.7), rnd.uniform(-0.45, -0.2), 0.03), (rnd.uniform(0.08, 0.16), rnd.uniform(0.06, 0.12), 0.03),
              CLAY, rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 3)), bevel=0.008)
    for i in range(3):                                                                  # rags
        hum_sq(k, (rnd.uniform(-0.5, 0.3), rnd.uniform(-0.2, 0.3), 0.2 + 0.1 * i), (0.22, 0.16, 0.06), e=0.6, nu=8, nv=5,
               mi=rnd.choice((BURLAP, CLOTH_A, CLOTH_B)), rot=Matrix.Rotation(rnd.uniform(0, 3), 4, "Z"))


def slm_crate(k, c, s, rnd, broken=False, rz=0.0):
    sub = Kit()
    for (x, y, sx, sy) in ((0, -s / 2 + 0.01, s, 0.02), (0, s / 2 - 0.01, s, 0.02), (-s / 2 + 0.01, 0, 0.02, s - 0.04), (s / 2 - 0.01, 0, 0.02, s - 0.04)):
        n = 3
        for i in range(n):
            if broken and i == 2 and x == 0 and y < 0: continue
            z = s * (i + 0.5) / n
            sub.box((x, y, z), (sx, sy, s / n - 0.012), PLANKS, bevel=0.004)
    sub.box((0, 0, 0.012), (s - 0.02, s - 0.02, 0.02), PLANKS, bevel=0.004)
    for (x, y) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        sub.box((x * (s / 2 - 0.03), y * (s / 2 - 0.03), s / 2), (0.05, 0.05, s), WOOD, bevel=0.008)
    if broken: hum_sq(sub, (0, 0, s * 0.85), (s * 0.4, s * 0.4, s * 0.25), e=0.6, nu=8, nv=5, mi=HAY)
    merge_kit(k, sub, Matrix.Translation(c) @ Matrix.Rotation(rz, 4, "Z"))


def slm_crates_broken(k, seed=7):
    rnd = random.Random(seed)
    slm_crate(k, (-0.32, 0.0, 0.0), 0.6, rnd, broken=True, rz=0.1)
    slm_crate(k, (0.36, 0.08, 0.0), 0.55, rnd, rz=-0.25)
    slm_crate(k, (-0.25, 0.05, 0.6), 0.5, rnd, broken=True, rz=0.5)
    for i in range(2):
        k.box((0.5 + 0.2 * i, -0.45, 0.02), (0.55, 0.12, 0.02), PLANKS, rot=(0, 0, 0.6 + 0.9 * i), bevel=0.004)


def slm_rain_barrel(k):
    """a barrel catching the roof's water from a plank chute on a post"""
    prof = [(0.0, 0.0), (0.3, 0.0), (0.33, 0.12), (0.36, 0.42), (0.35, 0.72), (0.31, 0.88), (0.29, 0.9)]
    lathe(k, prof, center=(0, 0, 0), segs=14, mi=WOOD)
    for z, r in ((0.12, 0.335), (0.76, 0.345)):
        lathe(k, [(r, z - 0.03), (r + 0.012, z - 0.03), (r + 0.012, z + 0.03), (r, z + 0.03)], center=(0, 0, 0), segs=14, mi=IRON)
    _cyl(k, (0, 0, 0.8), 0.27, 0.27, 0.01, 14, WATER)
    hum_rod(k, (0.42, 0.1, 0.0), (0.42, 0.1, 1.55), 0.05, segs=6)
    k.box((0.2, 0.1, 1.2), (0.6, 0.1, 0.03), PLANKS, rot=(0, 0.55, 0), bevel=0.006)
    for s in (-1, 1): k.box((0.2, 0.1 + s * 0.05, 1.24), (0.6, 0.02, 0.06), PLANKS, rot=(0, 0.55, 0), bevel=0.004)


def slm_privy(k, seed=8):
    """a plank privy: 1.1 x 1.1 m, a mono-pitch board roof, the door ajar"""
    rnd = random.Random(seed)
    W = 1.1; H0 = 2.0; H1 = 2.25
    for (x, y) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        hum_rod(k, (x * W / 2, y * W / 2, -0.2), (x * W / 2, y * W / 2, (H0 if y < 0 else H1) - 0.05), 0.045, segs=6)
    for side in ("B", "L", "R"):
        n = 5
        for i in range(n):
            u = -W / 2 + W * (i + 0.5) / n
            if side == "B":
                c = (u, W / 2 - 0.02, (H1 - 0.1) / 2 + 0.05); s = (W / n - 0.01, 0.03, H1 - 0.15)
            else:
                xx = (-1 if side == "L" else 1) * (W / 2 - 0.02); top = H0 + (H1 - H0) * (u + W / 2) / W - 0.08
                c = (xx, u, top / 2 + 0.05); s = (0.03, W / n - 0.01, top - 0.05)
            k.box(c, s, rnd.choice((PLANKS, PLANKS, WOOD)), bevel=0.005)
    a = math.atan2(H1 - H0, W)
    k.box((0, 0, (H0 + H1) / 2 + 0.03), (W + 0.25, math.hypot(W, H1 - H0) + 0.25, 0.035), PLANKS, rot=(a, 0, 0), bevel=0.006)
    k.box((0, -W / 2 + 0.01, H0 - 0.15), (W, 0.04, 0.12), WOOD, bevel=0.008)
    k.quad([(-0.4, -W / 2 + 0.05, 0.05), (0.4, -W / 2 + 0.05, 0.05), (0.4, -W / 2 + 0.05, H0 - 0.22), (-0.4, -W / 2 + 0.05, H0 - 0.22)],
           VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    sub = Kit()
    for i in range(4): sub.box((0.1 + 0.2 * i, 0, (H0 - 0.25) / 2), (0.19, 0.03, H0 - 0.3), PLANKS, bevel=0.005)
    merge_kit(k, sub, Matrix.Translation((-0.42, -W / 2 - 0.02, 0.05)) @ Matrix.Rotation(-0.6, 4, "Z"))


def slm_washing_line(k, seed=9):
    """two forked poles 3.2 m apart, a sagging line, rags and shirts hung out"""
    rnd = random.Random(seed)
    for x in (-1.6, 1.6):
        hum_rod(k, (x, 0, -0.2), (x, 0, 1.75), 0.04, segs=6)
        for s in (-1, 1): hum_rod(k, (x, 0, 1.7), (x + s * 0.09, 0, 1.92), 0.025, segs=5)
    line = wat_sag(Vector((-1.6, 0, 1.82)), Vector((1.6, 0, 1.82)), 0.18, n=10)
    wat_rope(k, line, r=0.012)
    for i in range(5):
        t = 0.12 + 0.18 * i + rnd.uniform(-0.03, 0.03)
        p = line[0].lerp(line[-1], t); p.z = 1.82 - 0.18 * math.sin(math.pi * t)
        w = rnd.uniform(0.35, 0.6); h = rnd.uniform(0.4, 0.7)
        k.box((p.x, rnd.uniform(-0.02, 0.02), p.z - h / 2), (w, 0.012, h), rnd.choice((CLOTH_A, CLOTH_B, BURLAP, CLOTH_B)),
              rot=(rnd.uniform(-0.12, 0.12), 0, rnd.uniform(-0.1, 0.1)), bevel=0.003)


def slm_ladder(k):
    """a rickety ladder leaning on a wall: foot at the origin, top 2.4 m up against y +0.65; a rung broken"""
    for x in (-0.2, 0.22): hum_rod(k, (x, 0.0, 0.0), (x * 0.95, 0.65, 2.45), 0.03, segs=6)
    for i in range(7):
        t = (i + 0.6) / 7.6
        y = 0.65 * t; z = 2.45 * t
        if i == 3:
            hum_rod(k, (-0.2, y, z), (0.02, y - 0.05, z - 0.18), 0.017, segs=5)        # broken, hanging
            continue
        hum_rod(k, (-0.21, y, z), (0.21, y, z), 0.018, segs=5)


# ================================================================ builders
SLM_WALLS = {"planks": ("SM_VK_Shack_Wall_Planks", "SM_VK_Shack_Wall_Planks_Door", "SM_VK_Shack_Wall_Planks_Window"),
             "patched": ("SM_VK_Shack_Wall_Patched", "SM_VK_Shack_Wall_Patched_Door", "SM_VK_Shack_Wall_Patched_Window"),
             "wattle": ("SM_VK_Shack_Wall_Wattle", "SM_VK_Shack_Wall_Wattle_Door", "SM_VK_Shack_Wall_Wattle_Window")}


def build_shack(coll, origin, seed=0, bays=1, walls="planks", roof="leanto", stilts=0.0, props=True):
    """A slum shack, `bays` cells along local X, one cell deep (y -1.5..1.5); its door in the front (-Y) wall's first
    bay, a window in the last front bay or the back. walls: planks | patched | wattle; roof: leanto | thatch | sail.
    stilts > 0: on a stilt platform per bay with its deck top that high, a ladder down from the door, a walkway along
    the front. props: a rain barrel, junk, crates or a washing line round it. Lot: x -L/2-1.5 .. L/2+1.5, y -4.5..3."""
    r = random.Random(seed); n = bays; L = n * CELL; parts = []; z = stilts
    plain, door, win = SLM_WALLS[walls]

    def P(nm, x, y, zz, rot, sty=None):
        o = place_v(coll, nm, x, y, zz, rot, origin, sty if sty is not None else SLM_STYLE); parts.append(o); return o
    for i in range(n):
        x = -L / 2 + 1.5 + 3 * i
        P(door if i == 0 else (win if i == n - 1 else plain), x, -1.5, z, 0)
        P(win if (n == 1 or i == 0) and r.random() < 0.6 else plain, L / 2 - 1.5 - 3 * i, 1.5, z, 180)
    P(win if n == 1 else plain, -L / 2, 0.0, z, -90)
    P(plain, L / 2, 0.0, z, 90)
    for (cx, cy, rr) in ((-L / 2, -1.5, 0), (L / 2, -1.5, 90), (L / 2, 1.5, 180), (-L / 2, 1.5, -90)):
        P("SM_VK_Shack_Corner", cx, cy, z, rr)
    for i in range(n):
        x = -L / 2 + 1.5 + 3 * i
        if roof == "leanto":
            nm = "SM_VK_Shack_Roof_LeanTo" + ("_Single" if n == 1 else ("_EndL" if i == 0 else ("_EndR" if i == n - 1 else "_Mid")))
            P(nm, x, 0, z + SLM_HW, 0)
        else:
            base = "SM_VK_Shack_Roof_Thatch" if roof == "thatch" else "SM_VK_Shack_Roof_Sail"
            if n == 1: P(base + "_Single", x, 0, z + SLM_HW, 0)
            elif i == 0: P(base + "_End", x, 0, z + SLM_HW, 180)
            elif i == n - 1: P(base + "_End", x, 0, z + SLM_HW, 0)
            else: P(base + "_Mid", x, 0, z + SLM_HW, 0)
    if stilts > 0:
        for i in range(n): P("SM_VK_Shack_Stilts", -L / 2 + 1.5 + 3 * i, 0, z, 0, {})
        for i in range(n): P("SM_VK_Shack_Walkway", -L / 2 + 1.5 + 3 * i, -2.1, z, 0, {})
        dx = (SLM_DOOR[0] + SLM_DOOR[1]) / 2 - L / 2 + 1.5
        P("SM_VK_Shack_StiltLadder", dx + 1.6, -2.7, z, 0, {})
        return parts
    if props:
        P("SM_VK_Slum_RainBarrel", L / 2 + 0.55, -1.0, 0, r.choice((0, 90, 180)), {})
        pick = r.random()
        if pick < 0.4: P("SM_VK_Slum_JunkPile", L / 2 + 0.75, 1.0, 0, -90 + r.uniform(-15, 15), {})
        elif pick < 0.75: P("SM_VK_Slum_Crates_Broken", -L / 2 - 0.75, 0.8, 0, r.uniform(-20, 20), {})
        else: P("SM_VK_Slum_WashingLine", 0.0, -3.6, 0, r.uniform(-6, 6), {})
        if r.random() < 0.5: P("SM_VK_Slum_Ladder", -L / 2 - 0.1, -0.6, 0, -90, {})
    return parts


# ================================================================ SPECS
_slm_w = dict(wobble=True, grime=True)
_slm_n = dict(wobble=False, grime=True)
WS_SPECS = [
    ("SM_VK_Shack_Wall_Planks", lambda k: slm_wall_planks(k, "", False, seed=41), _slm_w),
    ("SM_VK_Shack_Wall_Planks_Door", lambda k: slm_wall_planks(k, "D", False, seed=42), _slm_w),
    ("SM_VK_Shack_Wall_Planks_Window", lambda k: slm_wall_planks(k, "W", False, seed=43), _slm_w),
    ("SM_VK_Shack_Wall_Patched", lambda k: slm_wall_planks(k, "", True, seed=44), _slm_w),
    ("SM_VK_Shack_Wall_Patched_Door", lambda k: slm_wall_planks(k, "D", True, seed=45), _slm_w),
    ("SM_VK_Shack_Wall_Patched_Window", lambda k: slm_wall_planks(k, "W", True, seed=46), _slm_w),
    ("SM_VK_Shack_Wall_Wattle", lambda k: slm_wall_wattle(k, "", seed=47), _slm_w),
    ("SM_VK_Shack_Wall_Wattle_Door", lambda k: slm_wall_wattle(k, "D", seed=48), _slm_w),
    ("SM_VK_Shack_Wall_Wattle_Window", lambda k: slm_wall_wattle(k, "W", seed=49), _slm_w),
    ("SM_VK_Shack_Corner", slm_corner, _slm_n),
    ("SM_VK_Shack_Roof_LeanTo_Mid", lambda k: slm_roof_leanto(k, False, False, seed=51), _slm_n),
    ("SM_VK_Shack_Roof_LeanTo_EndL", lambda k: slm_roof_leanto(k, True, False, seed=52), _slm_n),
    ("SM_VK_Shack_Roof_LeanTo_EndR", lambda k: slm_roof_leanto(k, False, True, seed=53), _slm_n),
    ("SM_VK_Shack_Roof_LeanTo_Single", lambda k: slm_roof_leanto(k, True, True, seed=54), _slm_n),
    ("SM_VK_Shack_Roof_Thatch_Mid", lambda k: slm_roof_thatch(k, 0, seed=55), _slm_n),
    ("SM_VK_Shack_Roof_Thatch_End", lambda k: slm_roof_thatch(k, 1, seed=56), _slm_n),
    ("SM_VK_Shack_Roof_Thatch_Single", lambda k: slm_roof_thatch(k, 2, seed=57), _slm_n),
    ("SM_VK_Shack_Roof_Sail_Mid", lambda k: slm_roof_sail(k, 0, seed=58), _slm_n),
    ("SM_VK_Shack_Roof_Sail_End", lambda k: slm_roof_sail(k, 1, seed=59), _slm_n),
    ("SM_VK_Shack_Roof_Sail_Single", lambda k: slm_roof_sail(k, 2, seed=60), _slm_n),
    ("SM_VK_Shack_Stilts", slm_stilts, _slm_n),
    ("SM_VK_Shack_Walkway", slm_walkway, _slm_n),
    ("SM_VK_Shack_StiltLadder", slm_stilt_ladder, _slm_n),
    ("SM_VK_Slum_JunkPile", slm_junk_pile, _slm_n),
    ("SM_VK_Slum_Crates_Broken", slm_crates_broken, _slm_n),
    ("SM_VK_Slum_RainBarrel", slm_rain_barrel, _slm_n),
    ("SM_VK_Slum_Privy", slm_privy, _slm_n),
    ("SM_VK_Slum_WashingLine", slm_washing_line, _slm_n),
    ("SM_VK_Slum_Ladder", slm_ladder, _slm_n),
]
EXTRA_SPECS += WS_SPECS
