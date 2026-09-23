def hum_weeds(coll, origin, r, runs, p=0.55, parts=None):
    for (x, y, rot) in runs:
        if r.random() < p:
            o = place_v(coll, "SM_VK_Deco_Weeds", x, y, 0, rot, origin, {})
            if parts is not None: parts.append(o)


def hum_fence(coll, a, b, origin, gate_at=None, parts=None):
    """fence_run() that also returns/collects the placed instances"""
    a = Vector(a); b = Vector(b); n = max(1, round((b - a).length / 3)); d = (b - a) / n
    rot = math.degrees(math.atan2(d.y, d.x)); out = []
    for i in range(n):
        c = a + d * (i + 0.5)
        out.append(place_v(coll, "SM_VK_Prop_FenceGate" if gate_at == i else "SM_VK_Prop_Fence", c.x, c.y, 0, rot, origin, {}))
    if parts is not None: parts.extend(out)
    return out


def build_hovel(coll, origin, seed=0, variant="cruck"):
    """Hovel (T1, 4 beds): 2x2 wattle-and-daub hut under a thatch 'haystack', cruck gables, smoke vent.
    Lot 3x3 cells: x -6..3, y -6..3 (house x -3..3, y -3..3). The door is on the R gable end (x = 3) and
    faces the street; the L cell column is the yard, the y -6..-3 strip the garden.
    variant: "cruck" | "hip" (hipped L end, vent moves to bay 1) | "leanto" (LeanTo_Thatch_Low on the L gable end)"""
    r = random.Random(seed)
    ends = ("hip", "cruck") if variant == "hip" else ("cruck", "cruck")
    parts = hum_block(coll, origin, 2, {"F": ".W", "B": "..", "L": "..", "R": "DW"}, ends=ends,
                      vents=(1,) if variant == "hip" else (0,))

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    if variant == "leanto":
        P("SM_VK_LeanTo_Thatch_Low", -3.0, 0.0, 0, -90, HUM_STYLE)
        P("SM_VK_Prop_HayBale", -4.4, 0.45, 0, 90 + r.uniform(-4, 4))
        P("SM_VK_Prop_Sacks", -4.5, -0.8, 0, r.uniform(-20, 20))
    else:
        P("SM_VK_Prop_Woodpile", -4.45, 0.35, 0, 90, HUM_STYLE)
    P("SM_VK_Prop_ChickenCoop_Wattle", -4.4, -2.55, 0, -90)
    P("SM_VK_Animal_Chickens", -4.5, -4.75, 0, r.uniform(0, 360))
    P("SM_VK_Prop_GardenBed", -0.9, -5.0, 0, 0)
    P("SM_VK_Prop_Bench", 1.35, -3.62, 0, 0)
    P("SM_VK_Prop_Planter", 2.65, -3.5, 0, 0)
    P("SM_VK_Deco_Bush", 2.2, -5.1, 0, r.uniform(0, 360))
    hum_weeds(coll, origin, r, [(-1.5, -3.05, 0), (-1.5, 3.05, 180), (1.5, 3.05, 180), (3.05, 1.5, 90), (-3.05, 1.5, -90)], parts=parts)
    return parts


def build_longhouse(coll, origin, seed=0):
    """Longhouse (T1, 8 beds + 4 livestock): 5x2 thatch 'loaf' on 2.4 m daub walls, vents in bays 1 and 3.
    People end L (cruck gable, door at y +1.5), byre end R (plank gable, byre door at y -1.5).
    Lot 8x3 cells: x -10.5..13.5, y -6..3; fenced paddock x 7.5..13.5, y -6..3 in front of the byre door,
    gate on the far side (x 13.5)."""
    r = random.Random(seed)
    parts = hum_block(coll, origin, 5, {"F": ".W.W.", "B": "....W", "L": "D.", "R": "B."}, ends=("cruck", "planks"), vents=(1, 3))

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    # paddock
    hum_fence(coll, (7.5, -6.0), (13.5, -6.0), origin, parts=parts)
    hum_fence(coll, (7.5, 3.0), (13.5, 3.0), origin, parts=parts)
    hum_fence(coll, (13.5, -6.0), (13.5, 3.0), origin, gate_at=1, parts=parts)
    hum_fence(coll, (7.5, -6.0), (7.5, -3.0), origin, parts=parts)
    P("SM_VK_Prop_HayRack", 10.6, 1.75, 0, 0)
    P("SM_VK_Prop_Trough", 12.75, -3.9, 0, 90)
    P("SM_VK_Prop_HayBale", 8.7, -5.05, 0, 12)
    P("SM_VK_Animal_Cow", 9.9, -2.7, 0, 195 + r.uniform(-12, 12))
    P("SM_VK_Animal_Horse", 11.9, -0.3, 0, 250 + r.uniform(-10, 10))
    P("SM_VK_Animal_Sheep", 10.9, -4.9, 0, 20 + r.uniform(-20, 20))
    P("SM_VK_Animal_Sheep", 12.4, -1.9, 0, 205 + r.uniform(-20, 20))
    # people end: yard x -10.5..-7.5, front strip y -6..-3
    P("SM_VK_Prop_Bench", -8.05, -0.4, 0, -90)
    P("SM_VK_Prop_ChickenCoop_Wattle", -9.35, -2.6, 0, 180)
    P("SM_VK_Animal_Chickens", -9.3, -4.9, 0, r.uniform(0, 360))
    P("SM_VK_Prop_GardenBed", -4.5, -5.0, 0, 0)
    P("SM_VK_Prop_Woodpile", 1.5, -4.95, 0, 0, HUM_STYLE)
    P("SM_VK_Deco_Bush", -8.9, 2.3, 0, r.uniform(0, 360))
    hum_weeds(coll, origin, r, [(-6.0, -3.05, 0), (4.5, -3.05, 0), (-3.0, 3.05, 180), (3.0, 3.05, 180), (-7.55, -1.5, -90)], parts=parts)
    return parts


def build_pigsty(coll, origin, seed=0):
    """Pig sty (3x3 lot, x/y -4.5..4.5): 6x6 m yard in low dry-stone walls with a gate in front (-Y),
    wattle back wall carrying two thatch lean-tos (shelter over the back half), mud wallow, trough, 3 pigs"""
    r = random.Random(seed); parts = []

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    for x in (-1.5, 1.5):
        P("SM_VK_Wall_Wattle", x, 3.0, 0, 0, HUM_STYLE)
        P("SM_VK_LeanTo_Thatch_Low", x, 3.0, 0, 0, HUM_STYLE)
    for (x, y, rt) in ((-3.0, 1.5, 90), (-3.0, -1.5, 90), (3.0, 1.5, 90), (3.0, -1.5, 90), (-1.5, -3.0, 0)):
        P("SM_VK_LowWall", x, y, 0, rt)
    P("SM_VK_Prop_FenceGate", 1.5, -3.0, 0, 0)
    for (x, y) in ((-3.0, 3.0), (3.0, 3.0), (-3.0, -3.0), (3.0, -3.0), (0.0, -3.0), (-3.0, 0.0), (3.0, 0.0)):
        P("SM_VK_LowWall_Post", x, y, 0, 0)
    P("SM_VK_Deco_MudWallow", 0.3, -0.9, 0, r.uniform(-15, 15))
    P("SM_VK_Animal_Pig", -0.5, -1.2, 0, 20 + r.uniform(-20, 20))
    P("SM_VK_Animal_Pig", 1.3, -0.3, 0, 150 + r.uniform(-20, 20))
    P("SM_VK_Animal_Pig", -1.0, 1.7, 0, 260 + r.uniform(-20, 20))
    P("SM_VK_Prop_Trough", -1.55, -2.05, 0, 0)
    P("SM_VK_Prop_Sacks", 3.9, -2.2, 0, 30)
    P("SM_VK_Prop_HayBale", 3.9, 1.9, 0, 80)
    hum_weeds(coll, origin, r, [(-1.5, -3.4, 0), (-3.4, 1.5, -90), (3.4, -1.5, 90)], p=0.8, parts=parts)
    return parts


def build_sheepfold(coll, origin, seed=0):
    """Sheepfold (3x3 lot, x/y -4.5..4.5): fenced pen with a wattle back wall (daub side into the pen) carrying
    two thatch lean-to shelters, hay rack, trough, five sheep and a goat; gate in the front fence (-Y)"""
    r = random.Random(seed); parts = []

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    for x in (-3.0, 0.0, 3.0): P("SM_VK_Wall_Wattle", x, 4.5, 0, 0, HUM_STYLE)
    for x in (0.0, 3.0): P("SM_VK_LeanTo_Thatch_Low", x, 4.5, 0, 0, HUM_STYLE)
    P("SM_VK_Corner_Wattle", -4.5, 4.5, 0, 0, HUM_STYLE)
    P("SM_VK_Corner_Wattle", 4.5, 4.5, 0, 90, HUM_STYLE)
    hum_fence(coll, (-4.5, 4.2), (-4.5, -4.5), origin, parts=parts)
    hum_fence(coll, (4.5, -4.5), (4.5, 4.2), origin, parts=parts)
    hum_fence(coll, (-4.5, -4.5), (4.5, -4.5), origin, gate_at=1, parts=parts)
    P("SM_VK_Prop_HayRack", -3.0, 2.65, 0, 0)
    P("SM_VK_Prop_Trough", 2.2, -3.3, 0, 0)
    for i, (x, y) in enumerate(((-1.8, -1.2), (0.4, -0.2), (1.6, -2.0), (-0.6, 1.4), (2.4, 2.3))):
        P("SM_VK_Animal_Sheep", x, y, 0, r.uniform(0, 360))
    P("SM_VK_Animal_Goat", -3.1, -2.8, 0, r.uniform(0, 360))
    P("SM_VK_Prop_HayBale", 3.3, 1.2, 0, 10)
    return parts


