# ===================== VKI ROOMS ADVENTURE: the adventure kit's levels (docs/ADVENTURE_KIT.md) =====================
# Loaded by vki_ns() right after vki_rooms_dungeon, whose tables it extends: three more levels continue the dungeon's
# descent, linked by passages (a breach in a wall, or a tunnel tile in cave rock: vki_link "passage"), built and
# checked like every interior (vki_build_scene, vki_check, vki_rooms_shots). Build them with
# vki_build_all(VKI_ADVENTURE_SCENES).
#   surface -> B1 gaol -> B2 crypt -(passage)-> B3 temple -(passage)-> B4 caverns -(tunnel)-> B5 goblin warren
#   VKI_Dungeon_B3  the sunken temple (Ancient), 10 x 6: the breach from the crypt opens on a gallery of traps (two
#                   spike pits across the direct way, a pressure plate under a dart wall, a blade slot, a boulder, a
#                   lever), a trilithon gateway with a half-raised portcullis, the sanctum (guardian statues, the
#                   golden idol on its altar, braziers, columns standing, broken and fallen, roots by a broken
#                   wall), a vault (low front wall) behind a rolling stone disc left ajar, and a breach down to the
#                   caverns
#   VKI_Dungeon_B4  the caverns (a cave map), 10 x 6: a chasm splits the cave east-west, crossed by one rope bridge;
#                   the south shelf has a rock bulge, an underground pool, glowing mushrooms and crystals; the north
#                   shelf a rock mass in its west corner, a spur from the back wall, a fallen adventurer and a spider
#                   nest (corner webs, egg sacs, a cocoon, webbed floor) before the tunnel on down; two tunnels in the
#                   north shelf's back wall lead back to the sewer and the falls (the world graph, vki_world)
#   VKI_Dungeon_B5  the goblin warren (a cave map), 10 x 6: rock tongues part three chambers off a hall -- the
#                   rat-run entry behind a stake barricade (burrow, rat hole, refuse, totem), the camp (fire pit with
#                   a spitted haunch, lean-to, bedrolls), the chief's hoard (loot heap, coins, iron chest, bones)
#   VKI_Cave_Breach a transitions demo (a cave map with walls), 14 x 9: a dungeon hall dug into the rock (its walls
#                   backed by the rock, wall-backed tiles), its north wall broken through into a cave pocket (the
#                   300 breach), its east wall breached into the main cave; a corridor through
#                   the rock that runs out into the cave (its walls let into the rock, earth spilt over the seam); the
#                   ruined front of an ancient shrine standing in the cave, breached; a tunnel on east
# Plan legend additions (vki_rooms): "PP" / "P" passage (a scene link: R["passages"]), "S1".."S4" / "s1" "s2" / "1".."4"
# named pieces (R["specials"]). In a cave map (R["cave"]) a cell coded "##" is rock. Pits (spike pits, chasm tiles, the
# pool) come from R["pits"] (piece, x, y) at their min corners; they replace the floor of their cells.
# Cell codes here are a generated view: "vv" pit / chasm, "==" bridge, "~~" pool, "Ss" arrival spawn, "Sx" the tunnel
# on. Walls in a cave map: wall tokens on its inner grid lines (not the frame) are laid out like any partition
# (R["family"]["partition"], named pieces, doors, "XX" / "X" breaches) and the rock tiles on their nodes are the
# wall-backed ones. Every top-level name starts with vki_/VKI_ (T18).

VKI_ADVENTURE_SCENES = ["VKI_Dungeon_B3", "VKI_Dungeon_B4", "VKI_Dungeon_B5"]


# ---------------------------------------------------------------- cave levels: R["cave"] = True
# The plan is a cell map: a cell coded "##" is rock, every other cell is open floor, everything outside the map is
# rock (the plan's wall tokens are only a frame). Rock tiles (vki_fam_cave) stand on every node of the map whose four
# cells are not all open; floors cover the map and a ring of cells round it (the rock may wander off a cell);
# R["tunnels"] = {(i, j): link id} puts the tunnel tile on a perimeter node whose rock is a straight Full face
# (R["tunnel_kinds"] = {link id: "Adit"} takes the mine's timbered adit instead, vki_fam_mine); R["tracks"] lays a
# mine's track (vki_mine_tracks, vki_rooms_mine);
# R["cave_heights"] = {(c, r): "C" | "F"} overrides a rock cell's height.
def vki_cave_cells(R, P):
    """{(c, r): 'O' | 'C' | 'F'} for the map and a ring of one cell round it. A rock cell is Cut (C) in the south
    ring and the map's south row, or when open floor lies within two cells to its north (a 3 m rock would hide it
    from the camera), else Full (F)."""
    nc, nr, codes = P["nc"], P["nr"], P["codes"]
    rock = lambda c, r: not (0 <= c < nc and 0 <= r < nr) or codes.get((c, r)) == "##"
    ov = R.get("cave_heights", {})
    out = {}
    for c in range(-1, nc + 1):
        for r in range(-1, nr + 1):
            if not rock(c, r):
                out[(c, r)] = "O"
            elif (c, r) in ov:
                out[(c, r)] = ov[(c, r)]
            else:
                south = r == -1 or (r == 0 and 0 <= c < nc)
                out[(c, r)] = "C" if south or any(not rock(c, r + d) for d in (1, 2)) else "F"
    return out


def vki_cave_walls(name, R, P):
    """the walls drawn inside a cave map (wall tokens on its inner grid lines; the frame only borders the map):
    vki_rooms_layout's pieces, posts and door cells for them (partition family, named pieces, breaches) -> dict(pieces,
    posts, doors, segs, problems, arms {node: "SENW" subset: the wall arms from each node})"""
    nc, nr = P["nc"], P["nr"]
    ew = {q: (t if 0 < q[1] < nr else "  ") for q, t in P["ew"].items()}
    ns = {q: (t if 0 < q[0] < nc else " ") for q, t in P["ns"].items()}
    if not any(t.strip() for t in list(ew.values()) + list(ns.values())):
        return dict(pieces=[], posts=[], doors=[], segs={}, problems=[], arms={})
    L = vki_rooms_layout(name, R=dict(R, cave=False, open_frame=True), P=dict(P, ew=ew, ns=ns))
    arms = {}
    for pc in L["pieces"]:
        for d in range(pc["n"]):
            if pc["ori"] == "EW":
                a, b, sa, sb = (pc["k"] + d, pc["line"]), (pc["k"] + d + 1, pc["line"]), "E", "W"
            else:
                a, b, sa, sb = (pc["line"], pc["k"] + d), (pc["line"], pc["k"] + d + 1), "N", "S"
            arms[a] = arms.get(a, "") + sa
            arms[b] = arms.get(b, "") + sb
    return dict(pieces=L["pieces"], posts=L["posts"], doors=L["doors"], segs=L["segs"], problems=L["problems"],
                arms=arms)


def vki_cave_tiles(R, P, cells, problems, arms=None):
    """[dict(piece, x, y, rot, node, code, tunnel)] -- one rock tile per node with any rock around it: the master of
    the corner code's rotation class (a variant by the node's hash), turned to show it; tunnels on their nodes; on a
    node with walls (arms {node: "SENW" subset}) the wall-backed master of the code and arms"""
    nc, nr = P["nc"], P["nr"]
    tun = dict(R.get("tunnels", {}))
    arms = arms or {}
    out = []
    for i in range(nc + 1):
        for j in range(nr + 1):
            code = "".join(cells[c] for c in ((i - 1, j - 1), (i, j - 1), (i, j), (i - 1, j)))
            lid = tun.pop((i, j), None)
            if code == "OOOO":
                if lid:
                    problems.append(f"cave: tunnel {lid} at node ({i},{j}) has no rock")
                continue
            a_ = arms.get((i, j), "")
            if a_:
                ok = vki_cav_arms_ok(code, a_)
                if len(ok) < len(set(a_)):
                    problems.append(f"cave: a wall at node ({i},{j}) runs into solid rock (corners {code}, arms {a_})")
                if lid:
                    problems.append(f"cave: tunnel {lid} at node ({i},{j}) is on a wall")
                if ok:
                    m, ma, kk = vki_cav_canon_arms(code, ok)
                    out.append(dict(piece=f"SM_VKI_Rock_Cave_{m}_Wall{ma}", x=VKI_IG * i, y=VKI_IG * j,
                                    rot=(90 * kk + 180) % 360 - 180, node=(i, j), code=code, tunnel=None, arms=ok))
                    continue
            if lid:
                kk = vki_cav_rot("OOFF", code)
                if kk is None:
                    problems.append(f"cave: tunnel {lid} at node ({i},{j}) needs a straight Full face, corners {code}")
                else:
                    kind = R.get("tunnel_kinds", {}).get(lid, "Tunnel")     # "Adit": the mine's timbered mouth
                    out.append(dict(piece="SM_VKI_Rock_Cave_OOFF_" + kind, x=VKI_IG * i, y=VKI_IG * j,
                                    rot=(90 * kk + 180) % 360 - 180, node=(i, j), code=code, tunnel=lid))
                    continue
            m, kk = vki_cav_canon(code)
            vs = VKI_CAV_VARIANTS.get(m, "AB")
            var = vs[min(len(vs) - 1, int(vki_hash01(i, j, 91) * len(vs)))]
            out.append(dict(piece=f"SM_VKI_Rock_Cave_{m}_{var}", x=VKI_IG * i, y=VKI_IG * j,
                            rot=(90 * kk + 180) % 360 - 180, node=(i, j), code=code, tunnel=None))
    for (i, j), lid in tun.items():
        problems.append(f"cave: tunnel {lid} at node ({i},{j}) is off the map")
    return out


def vki_cave_flow(cells, sinks):
    """flow directions over painted water cells (streams, sewer channels; for Unity's water shaders): a breadth-first
    search from the sinks ({cell: (dx, dy)}, the way the water leaves there); every other reached cell flows toward
    its neighbour one step nearer a sink. -> {cell: (dx, dy)} (cells no sink reaches: left out, still water)"""
    flow = {tuple(c): tuple(d) for c, d in sinks.items() if tuple(c) in cells}
    todo = list(flow)
    while todo:
        nxt = []
        for c in todo:
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (c[0] + d[0], c[1] + d[1])
                if q in cells and q not in flow:
                    flow[q] = (-d[0], -d[1])
                    nxt.append(q)
        todo = nxt
    return flow


def vki_cave_tile_flow(cs, flow):
    """a water tile's flow: the normalised sum of its water corners' flows, or None"""
    fx = sum(flow[c][0] for c in cs if c in flow)
    fy = sum(flow[c][1] for c in cs if c in flow)
    L = math.hypot(fx, fy)
    return [round(fx / L, 3), round(fy / L, 3)] if L > 1e-6 else None


def vki_cave_ground(R, P, zmap, problems):
    """the chasm and the streams: cells coded "vv" or "==" (under a bridge) are chasm, cells coded "ss" stream. A
    ground tile stands on every node with chasm or stream among its four cells (code SW SE NE NW, X / O; never
    rotated; the node's parity picks Q00..Q11): the chasm's where the chasm is (a stream there counts as chasm: it
    pours in), else the stream's. A stream cell next to a chasm cell gets a waterfall (Prop_Waterfall_Chasm on its
    centre, facing the chasm) and is a sink of the stream's flow (R["stream_sinks"] adds more: {cell: (dx, dy)}).
    -> (tiles [dict(piece, x, y, node, code, style, flow)], {cell: set of its quarters (qa, qb) the tiles cover},
    the waterfalls as prop tuples)"""
    nc, nr, codes = P["nc"], P["nr"], P["codes"]
    inside = lambda c: 0 <= c[0] < nc and 0 <= c[1] < nr
    xs = {c for c, v in codes.items() if v in ("vv", "==") and inside(c)}
    ss = {c for c, v in codes.items() if v == "ss" and inside(c)}
    pc = vki_rooms_pit_cells(R)
    falls, sinks = [], {}
    for c in sorted(ss):
        for d, rot in (((0, -1), 0), ((1, 0), 90), ((0, 1), 180), ((-1, 0), -90)):
            if (c[0] + d[0], c[1] + d[1]) in xs:
                falls.append(("Waterfall_Chasm", VKI_IG * (c[0] + 0.5), VKI_IG * (c[1] + 0.5), rot, None, None,
                              {"hug": False}))
                sinks.setdefault(c, d)
    for c, d in R.get("stream_sinks", {}).items():
        sinks.setdefault(tuple(c), tuple(d))
    flow = vki_cave_flow(ss, sinks)
    tiles, cov = [], {}
    for i in range(nc + 1):
        for j in range(nr + 1):
            cs = ((i - 1, j - 1), (i, j - 1), (i, j), (i - 1, j))
            chasm, stream = any(c in xs for c in cs), any(c in ss for c in cs)
            if not (chasm or stream):
                continue
            if any(c in pc for c in cs):
                problems.append(f"cave: the {'chasm' if chasm else 'stream'} at node ({i},{j}) touches a pit cell")
            if chasm:
                code = "".join("X" if (c in xs or c in ss) else "O" for c in cs)
                piece = "SM_VKI_Ground_Cave_XXXX" if code == "XXXX" else f"SM_VKI_Ground_Cave_{code}_Q{i % 2}{j % 2}"
            else:
                code = "".join("X" if c in ss else "O" for c in cs)
                piece = "SM_VKI_Ground_Stream_XXXX" if code == "XXXX" else \
                    f"SM_VKI_Ground_Stream_{code}_Q{i % 2}{j % 2}"
            zc = next((c for c in cs if c not in xs and c not in ss and inside(c)), None)
            zn = zmap.get(zc) if zc else None
            t = dict(piece=piece, x=VKI_IG * i, y=VKI_IG * j, node=(i, j), code=code,
                     style={"floor": R["zones"][zn]["floor"]} if zn else None)
            if stream and not chasm:
                t["flow"] = vki_cave_tile_flow([c for c in cs if c in ss], flow)
            tiles.append(t)
            for c, q in zip(cs, ((1, 1), (0, 1), (0, 0), (1, 0))):
                cov.setdefault(c, set()).add(q)
    return tiles, cov, falls


VKI_CAVE_CHANNELS = (("ww", "Sewer", "channel_sinks"), ("ll", "Lava", "lava_sinks"))   # code, tile set, sinks key


def vki_cave_channels(R, P, problems):
    """the channels: sewer water (cells coded "ww", vki_fam_sewer) and dwarven lava ("ll", vki_fam_dwarf). A channel
    tile stands on every node with channel among its four cells: the master of the code's rotation class (SW SE NE NW,
    X / O) of its set, turned to show it. It carries the channel over its X quarters only, and no floor, so the cells
    round a channel keep whole floors. Flow (vki_flow) runs toward R["channel_sinks"] / R["lava_sinks"].
    -> (tiles [dict(piece, x, y, rot, node, code, flow)], every channel cell)"""
    nc, nr, codes = P["nc"], P["nr"], P["codes"]
    inside = lambda c: 0 <= c[0] < nc and 0 <= c[1] < nr
    kinds = {cc: {c for c, v in codes.items() if v == cc and inside(c)} for cc, _, _ in VKI_CAVE_CHANNELS}
    wet = {c for c, v in codes.items() if v in ("vv", "==", "ss")}
    tiles, allx = [], set()
    for cc, tset, sk in VKI_CAVE_CHANNELS:
        xs = kinds[cc]
        others = wet | {c for c2, cs2 in kinds.items() if c2 != cc for c in cs2}
        flow = vki_cave_flow(xs, R.get(sk, {}))
        for i in range(nc + 1):
            for j in range(nr + 1):
                cs = ((i - 1, j - 1), (i, j - 1), (i, j), (i - 1, j))
                if not any(c in xs for c in cs):
                    continue
                if any(c in others for c in cs):
                    problems.append(f"cave: the {tset.lower()} channel at node ({i},{j}) touches other water")
                code = "".join("X" if c in xs else "O" for c in cs)
                m, kk = vki_cav_canon(code)
                tiles.append(dict(piece=f"SM_VKI_Ground_{tset}_{m}", x=VKI_IG * i, y=VKI_IG * j,
                                  rot=(90 * kk + 180) % 360 - 180, node=(i, j), code=code,
                                  flow=vki_cave_tile_flow([c for c in cs if c in xs], flow)))
        allx |= xs
    return tiles, allx


def vki_cave_layout(name, R, P, zmap):
    """vki_rooms_layout for a cave level: no wall pieces or posts; rock tiles; the chasm's ground tiles; floors --
    Floor_150 on every map cell (rock or open: the rock never recedes off its own cells, so the ring needs none) that
    no ground tile touches, Floor_075 quarters on the quarters of a cell the ground tiles leave, nothing on pits"""
    nc, nr = P["nc"], P["nr"]
    WL = vki_cave_walls(name, R, P)
    problems = list(WL["problems"])
    cells = vki_cave_cells(R, P)
    rocks = vki_cave_tiles(R, P, cells, problems, WL["arms"])
    grounds, cov, falls = vki_cave_ground(R, P, zmap, problems)
    chans, ccells = vki_cave_channels(R, P, problems)
    pcells = vki_rooms_pit_cells(R)
    floors = []
    for c in range(nc):
        for r in range(nr):
            if (c, r) in pcells or (c, r) in ccells:
                continue
            zn = zmap.get((c, r))
            st = {"floor": R["zones"][zn]["floor"]}
            q = cov.get((c, r), set())
            if not q:
                floors.append(dict(piece=f"SM_VKI_Floor_150_Q{c % 2}{r % 2}", x=VKI_IG * c, y=VKI_IG * r, zone=zn,
                                   style=st))
                continue
            for qa in (0, 1):
                for qb in (0, 1):
                    if (qa, qb) not in q:
                        floors.append(dict(piece=f"SM_VKI_Floor_075_R{(2 * c + qa) % 4}{(2 * r + qb) % 4}",
                                           x=VKI_IG * c + 0.75 * qa, y=VKI_IG * r + 0.75 * qb, zone=zn, style=st))
    return dict(name=name, R=R, P=P, nc=nc, nr=nr, W=P["W"], D=P["D"], zmap=zmap, segs=WL["segs"],
                pieces=WL["pieces"], posts=WL["posts"], floors=floors, doors=WL["doors"], stair_cells={},
                pit_cells=pcells, problems=problems, rocks=rocks, grounds=grounds + chans, cells=cells,
                auto_props=falls + (vki_mine_tracks(R, P, problems) if R.get("tracks") else []))   # + track


def vki_cave_tunnel(ctx, rk, o):
    """a tunnel tile carries its scene link (as a passage): R["links"] entry (id, "passage", target), the spawn at
    its vki_spawn_local"""
    R = ctx["R"]
    lid = rk["tunnel"]
    lk = next((l for l in R["links"] if l[0] == lid), None)
    if lk is None:
        ctx["notes"].append(f"tunnel {lid} at node {rk['node']} has no R['links'] entry")
        return None
    o["vki_link"] = "passage"
    o["vki_link_id"] = lid
    o["vki_target"] = lk[2]
    o["vki_prompt"] = o.get("vki_prompt_text", "Go through")
    o["vki_facing_min"] = 60
    sl = vki_get(o, "vki_spawn_local", None) or [0.0, -1.60]
    sx, sy = vki_rooms_local(rk, sl[0], sl[1])
    vki_rooms_spawn(ctx, lid, round(sx, 4), round(sy, 4), (180 - rk["rot"]) % 360, o)
    ctx["links"][lid] = o
    return o

VKI_PLANS.update({
    "VKI_Dungeon_B3": """
      0  1  2  3  4  5  6  7  8  9
     +##+##+S1+##+##+##+S2+S4+##+##+
   5 #BO .. .. ..#CI lp2.. .. .. SG#
     +                             +
   4 #.. cr pp ..#gc ..2.. CA BZ AI#
     +            ==+==+           +
   3 PSs .. vv ..1.. .. .. .. BZ AI#
     +                             +
   2 #.. .. vv ..1.. .. .. cr .. SG#
     +                             +
   1 #.. sf bs ..:sb .. .. cb .. SxP
     +                             +
   0 tur .. .. BZ:.. cf cf .. .. urt
     +==+s1+==+==+==+==+==+s1+==+==+
""",
    "VKI_Dungeon_B4": """
      0  1  2  3  4  5  6  7  8  9  10 11
     +##+##+##+##+##+##+##+##+##+##+##+##+
   6 ### ## .. ## CR SM .. .. .. .. co wb#
     +                                   +
   5 ### MG .. .. .. .. gv .. .. .. es Sx#
     +                                   +
   4 #vv vv .. sf .. .. vv == vv .. .. ..#
     +                                   +
   3 #vv vv vv vv vv vv vv == vv vv vv vv#
     +                                   +
   2 #.. .. .. vv vv vv .. .. .. .. vv vv#
     +                                   +
   1 #Ss .. .. .. .. .. .. ~~ ~~ CR .. ..#
     +                                   +
   0 t.. .. .. gv MG .. .. ~~ ~~ .. .. ##t
     +==+==+==+==+==+==+==+==+==+==+==+==+
""",    "VKI_Dungeon_B5": """
      0  1  2  3  4  5  6  7  8  9
     +##+##+##+##+##+##+##+##+##+##+
   5 #Ss .. TO ## .. LT .. ## .. lp#
     +                             +
   4 #.. .. .. ## br .. br ## gc sk#
     +                             +
   3 #.. BA .. .. .. FP .. .. CI ..#
     +                             +
   2 #.. .. BR .. .. .. .. .. .. BR#
     +                             +
   1 #rh rf .. ## ## .. ba ## bo ..#
     +                             +
   0 tbw .. .. ## ## br .. ## ## urt
     +==+==+==+==+==+==+==+==+==+==+
""",})

VKI_PLANS.update({
    "VKI_Cave_Breach": """
       0  1  2  3  4  5  6  7  8  9 10 11 12 13
     +##+##+##+##+##+##+##+##+##+##+##+##+##+##+
   8 ### ## MG .. .. .. .. ## cn AI .. ## ## ###
     +                                         +
   7 ### ## .. .. ## ## .. ## .. .. CR ## ## ###
     +   ##+XX+XX+##+##+   s2+s1+s1+s2+        +
   6 ####.. .. .. .. sk#.. .. .. .. .. .. CR ###
     +                                         +
   5 ####.. .. .. .. ..#.. .. KH .. .. .. .. ..#
     +                                         +
   4 ####.. SA SA .. ..X.. .. .. .. .. .. .. Sx#
     +                                         +
   3 ####.. .. .. .. cn#.. .. .. .. SM .. .. Sx#
     +   ==+==+dd+==+==+                       +
   2 ### ## ##:..:## ## ## MG .. .. gv .. ## ###
     +            ==+==+==+                    +
   1 ### ## ##:.. .. .. sp .. BD ~~ ~~ MG ## ###
     +         ==+==+==+==+                    +
   0 t## ## ## ## ## ## ## ## .. ~~ ~~ .. ## ##t
     +==+==+==+==+==+==+==+==+==+==+==+==+==+==+
""",
})
VKI_ADVENTURE_DEMOS = ["VKI_Cave_Breach"]

VKI_ROOMS.update({
    "VKI_Dungeon_B3": dict(
        building="Dungeon", floor=-3, preset="Dungeon", family=dict(perimeter="Ancient", partition="Ancient"),
        partition_wall="zone", pools=False,
        debris=dict(density=0.40, seed=13),                                  # loose debris (vki_props_debris)
        specials={"S1": "Wall_Dungeon_DartTrap_150_Full", "S2": "Wall_Ancient_Relief_150_Full",
                  "2": "Wall_Ancient_Vault_300_Full", "S4": "Wall_Ancient_Broken_150_Full",
                  "s1": "Wall_Ancient_Collapsed_150_Cut", "1": "Wall_Ancient_DoorWide_300_Full"},
        zones={"gallery": dict(cells=[(0, 3, 0, 5)], floor="AncientFlag", wall="AncientIn", cap="AncientCap"),
               "vault": dict(cells=[(4, 5, 4, 5)], floor="AncientFlag", wall="AncientIn"),
               "sanctum": dict(cells="rest", floor="AncientFlag", wall="AncientIn")},
        passages={("NS", 3, 0): "crypt", ("NS", 1, 10): "caverns"},
        links=[("crypt", "passage", "VKI_Dungeon_B2"), ("caverns", "passage", "VKI_Dungeon_B4")],
        # the portcullis hangs half raised (its full travel: the bars' tips at 0.75); the vault door is in the
        # vault's east side (a Full wall facing the camera hid the loot, T19), its stone disc rolled a metre south, in
        # front of the wall, leaving 1.0 m of the opening; the vault's south side is a Cut wall
        door_leaves={("NS", 2, 4): dict(piece="Leaf_Portcullis_300", z=0.75, state="raised"),
                     ("NS", 4, 6): dict(piece="Leaf_VaultDisc_300", socket=[0.5, -0.42, 0.0], state="ajar")},
        pits=[("Pit_SpikePit_150", 3.0, 3.0), ("Pit_SpikePit_150", 3.0, 4.5)],
        props=[  # the gallery of traps (x 0-6)
               ("Boulder", 0.8, 8.2, 0, None, None), ("Overlay_CrackedFloor", 2.25, 6.75, 0, None, None),
               ("Overlay_PressurePlate", 3.75, 6.75, 0, None, None),            # under the dart wall's line of fire
               ("Overlay_BladeSlot_150", 3.75, 2.25, 0, None, None),
               ("Skeleton_Fallen", 2.25, 2.25, 0, None, None), ("Urns", 0.75, 0.75, 0, None, None),  # blade victim
               ("Brazier_Stone", 5.25, 0.75, 0, None, None),
               ("Lever_Wall", 0.75, 2.25, 90, None, "wall_hung"), ("Torch_Wall", 0.75, 6.75, 90, None, "wall_hung"),
               ("Roots_Wall", 2.0, 8.25, 0, None, "wall_hung"),
               # the sanctum (x 6-15)
               ("Statue_Broken", 6.9, 2.25, 0, None, None), ("Column_Fallen", 9.0, 0.9, 0, None, None),
               ("Column_Ancient", 11.25, 6.75, 0, None, None), ("Column_Broken", 11.25, 2.25, 0, None, None),
               ("Overlay_CrackedFloor", 12.75, 3.75, 0, None, None),
               ("Altar_Idol", 14.0, 6.0, -90, None, None),
               ("Statue_Guardian", 14.2, 8.25, -90, None, None), ("Statue_Guardian", 14.2, 3.75, -90, None, None),
               ("Brazier_Stone", 12.75, 6.9, 0, None, None), ("Brazier_Stone", 12.75, 5.1, 0, None, None),
               ("Urns", 14.25, 0.75, 0, None, None),
               ("Roots_Wall", 12.75, 8.25, 0, None, "wall_hung"),                 # beside the broken wall
               # the vault (x 6-9, y 6-9)
               ("Chest_Iron", 6.85, 8.3, 0, None, None), ("LootPile", 8.0, 8.1, 0, None, None),
               ("Overlay_GoldCoins", 7.4, 6.9, 0, None, None)]),
    # the cave levels are cell maps ("##" = rock; vki_cave_layout): organic rock tiles on the dual grid, no walls. The
    # rock's foot and outline wander up to ~0.5 m into a cell next to rock: props there stand off it with the hug off.
    "VKI_Dungeon_B4": dict(
        building="Dungeon", floor=-4, preset="Cavern", family=dict(perimeter="Cave", partition="Cave"), cave=True,
        pools=False,
        debris=dict(density=0.50, seed=14),                                  # loose debris (vki_props_debris)
        zones={"cavern": dict(cells="rest", floor="CaveFloor")},
        # the town connection (vki_world): the ways back to the sewer (S1's "caverns") and the falls (VKI_Cave_Falls'
        # "west") are two more tunnels in the back wall of the north shelf
        tunnels={(0, 1): "temple", (12, 6): "warren", (7, 7): "falls", (9, 7): "sewer"},
        links=[("temple", "passage", "VKI_Dungeon_B3"), ("warren", "passage", "VKI_Dungeon_B5"),
               ("falls", "passage", "VKI_Cave_Falls"), ("sewer", "passage", "VKI_Sewer_S1")],
        # 12 x 7: the chasm ("vv") winds the width of the cave from under the west rock to under the east rock, one
        # to two cells wide, swinging up and down round row 3; one rope bridge crosses it where it runs two cells
        # wide (cells (7,3)-(7,4), "=="); the pool on the south shelf keeps a cell clear of it
        pits=[("Pit_Pool_300x300", 10.5, 0.0)],
        props=[  # the bridge
               ("RopeBridge_420", 11.25, 6.0, 0, None, None, {"hug": False}),
               # the south shelf
               ("Overlay_Gravel", 5.9, 1.0, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 6.75, 1.0, 0, None, None, {"hug": False}), ("Crystals", 14.25, 2.2, 0, None, None, {"hug": False}),
               # the north shelf and the spider nest; a fallen adventurer between them
               ("Mushrooms_Glow", 2.6, 8.0, 0, None, None, {"hug": False}), ("Skeleton_Fallen", 5.0, 7.4, 0, None, None, {"hug": False}),
               ("Crystals", 7.3, 9.3, 0, None, None, {"hug": False}), ("Stalagmites", 8.25, 9.4, 0, None, None, {"hug": False}),
               ("Overlay_Gravel", 9.75, 8.4, 0, None, None, {"hug": False}),
               ("Web_Corner", 17.25, 9.75, -90, None, None, {"hug": False}), ("Cocoon", 15.75, 10.15, 0, None, None, {"hug": False}),
               ("EggSacs", 15.0, 8.0, 0, None, None, {"hug": False}), ("Overlay_WebFloor", 16.3, 7.6, 0, None, None, {"hug": False})]),
    "VKI_Dungeon_B5": dict(
        building="Dungeon", floor=-5, preset="Cavern", family=dict(perimeter="Cave", partition="Cave"), cave=True,
        pools=False,
        debris=dict(density=0.38, seed=15),                                  # loose debris (vki_props_debris)
        zones={"warren": dict(cells=[(0, 2, 0, 5)], floor="EarthDamp"),
               "cave": dict(cells="rest", floor="CaveFloor")},
        tunnels={(0, 5): "caverns"},
        links=[("caverns", "passage", "VKI_Dungeon_B4")],
        # rock tongues from the north and south walls part three chambers off a hall (rows 2-3) that runs the width
        # of the cave; every opening is two cells wide (the rock's lobes and foot take ~0.6 m off each side of a gap)
        props=[  # the rat-run entry (x 0-4.5), behind a stake barricade
               ("Totem_Goblin", 3.2, 7.8, 0, None, None, {"hug": False}), ("Barricade_Stakes", 2.2, 5.0, 0, None, None, {"hug": False}),
               ("Burrow", 1.4, 1.3, 0, None, None, {"hug": False}), ("RatHole_Wall", 0.15, 2.25, 90, None, None, {"hug": False}),
               ("Overlay_Refuse", 2.4, 2.6, 0, None, None, {"hug": False}), ("Brazier", 3.3, 3.0, 0, None, None, {"hug": False}),
               # the camp (x 6-10.5): the fire in the hall, the lean-to between the north tongues
               ("FirePit_Camp", 8.25, 4.5, 0, None, None, {"hug": False}), ("LeanTo", 8.25, 7.8, 0, None, None, {"hug": False}),
               ("Overlay_Bedroll", 7.2, 6.5, 90, None, None, {"hug": False}), ("Overlay_Bedroll", 9.4, 6.4, 90, None, None, {"hug": False}),
               ("Overlay_Bedroll", 9.0, 1.4, 0, None, None, {"hug": False}), ("Barrel", 9.4, 2.7, 0, None, None, {"hug": False}),
               # the chief's hoard (x 12-15)
               ("LootPile", 13.5, 7.8, 0, None, None, {"hug": False}), ("Skeleton_Sitting", 14.0, 6.9, -90, None, None, {"hug": False}),
               ("Chest_Iron", 13.2, 5.0, 0, None, None, {"hug": False}), ("Overlay_GoldCoins", 13.5, 6.4, 0, None, None, {"hug": False}),
               ("Overlay_Bones", 12.8, 2.3, 0, None, None, {"hug": False}), ("Urns", 14.1, 1.0, 0, None, None, {"hug": False}),
               ("Brazier", 13.8, 3.2, 0, None, None, {"hug": False})]),
})

VKI_ROOMS.update({
    "VKI_Cave_Breach": dict(
        building="Dungeon", floor=-4, preset="Cavern", family=dict(perimeter="Cave", partition="Dungeon"), cave=True,
        pools=False, partition_wall="zone",
        debris=dict(density=0.40, seed=16),                                  # loose debris (vki_props_debris)
        specials={"s1": "Wall_Ancient_Breach_300_Cut", "s2": "Wall_Ancient_Collapsed_150_Cut"},
        zones={"hall": dict(cells=[(1, 5, 3, 6)], floor="DungeonFlag", wall="DungeonIn"),
               "corridor": dict(cells=[(3, 3, 1, 2), (4, 6, 1, 1)], floor="DungeonFlag", wall="DungeonIn"),
               "shrine": dict(cells=[(8, 10, 7, 8)], floor="AncientFlag", wall="AncientIn"),
               "cave": dict(cells="rest", floor="CaveFloor")},
        tunnels={(14, 4): "east"},
        links=[("east", "passage", "@return")],
        pits=[("Pit_Pool_300x300", 13.5, 0.0)],
        # the hall (x 1.5-9, y 4.5-10.5): rock behind its north and west walls and under the low south wall, its east
        # wall standing free in the cave with a breach; the corridor from its door runs through the rock and out
        # into the cave at x 10.5 (earth spilt over the seam); the shrine's ruined front (Ancient, Cut) on y 10.5
        props=[("Torch_Wall", 2.25, 6.75, 90, None, "wall_hung"), ("Torch_Wall", 2.25, 9.75, 0, None, "wall_hung"),
               ("Candles_Floor", 8.0, 5.2, 0, None, None), ("Skeleton_Sitting", 8.25, 9.75, 0, None, None),
               ("Mushrooms_Glow", 3.9, 12.4, 0, None, None, {"hug": False}),
               ("Sarcophagus", 4.5, 6.75, 0, None, None),
               ("Overlay_Spill", 10.5, 2.25, -90, None, None, {"hug": False}),
               ("Mushrooms_Glow", 11.3, 3.8, 0, None, None, {"hug": False}), ("Stalagmites", 15.75, 5.25, 0, None, None, {"hug": False}),
               ("Overlay_Gravel", 16.0, 3.9, 0, None, None, {"hug": False}), ("Boulders", 12.9, 2.5, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 17.25, 1.9, 0, None, None, {"hug": False}), ("Crystals", 18.3, 9.5, 0, None, None, {"hug": False}),
               ("Crystals", 15.75, 11.4, 0, None, None, {"hug": False}), ("Altar_Idol", 14.25, 12.5, 0, None, None, {"hug": False}),
               ("Candles_Floor", 12.75, 12.6, 0, None, None, {"hug": False}),
               # before the shrine's broken front: the head of its fallen colossus, face up (a point of interest,
               # vki_props_poi), a lane kept clear to the breach
               ("POI_ColossusHead", 13.2, 7.3, 0, None, None, {"hug": False})]),
})

VKI_ROOMS_CODES.update({"Boulder": "BO", "Overlay_CrackedFloor": "cr", "Overlay_PressurePlate": "pp",
                        "Overlay_BladeSlot_150": "bs", "Skeleton_Fallen": "sf", "Urns": "ur", "Brazier_Stone": "BZ",
                        "Statue_Broken": "sb", "Column_Fallen": "cf", "Column_Ancient": "CA", "Column_Broken": "cb",
                        "Altar_Idol": "AI", "Statue_Guardian": "SG", "LootPile": "lp", "Chest_Iron": "CI",
                        "Overlay_GoldCoins": "gc", "Stalagmites": "SM", "Overlay_Gravel": "gv", "Mushrooms_Glow": "MG",
                        "Crystals": "CR", "Boulders": "BD", "Web_Corner": "wb", "RockPillar_Full": "RP",
                        "RockPillar_Cut": "rp", "EggSacs": "es", "Overlay_WebFloor": "wf", "Cocoon": "co",
                        "Barricade_Stakes": "BA", "Burrow": "bw", "RatHole_Wall": "rh", "Overlay_Refuse": "rf",
                        "FirePit_Camp": "FP", "LeanTo": "LT", "Totem_Goblin": "TO", "Overlay_Bedroll": "br",
                        "Overlay_Spill": "sp",
                        "RopeBridge_420": "=="})


# ---------------------------------------------------------------- VKI_Adventure_Catalog (a viewer scene, like VKI_Catalog)
# every adventure master (and the dungeon family's adventure additions), labelled, in rows by group, on an AncientFlag
# floor that leaves the pits open, Day preset; a camera per group (VKI_AdvCat_Cam_G<i>, the game pitch). The vault and
# the secret door show their leaves in place. Rebuild: g["vki_adventure_catalog"]().
VKI_ADVENTURE_CATALOG = [
    ("Ancient walls, Full, and rakes", 0.0,
     ["SM_VKI_Wall_Ancient_Plain_150A_Full", "SM_VKI_Wall_Ancient_Plain_150B_Full", "SM_VKI_Wall_Ancient_Plain_300_Full",
      "SM_VKI_Wall_Ancient_Relief_150_Full", "SM_VKI_Wall_Ancient_Broken_150_Full", "SM_VKI_Wall_Ancient_Broken_300_Full",
      "SM_VKI_Wall_Ancient_Door_150_Full", "SM_VKI_Wall_Ancient_DoorWide_300_Full", "SM_VKI_Wall_Ancient_Vault_300_Full",
      "SM_VKI_Wall_Ancient_Passage_150_Full", "SM_VKI_Wall_Ancient_Rake_150_L", "SM_VKI_Wall_Ancient_Rake_150_R"]),
    ("Ancient walls, Cut; posts", -6.0,
     ["SM_VKI_Wall_Ancient_Plain_150A_Cut", "SM_VKI_Wall_Ancient_Plain_300_Cut", "SM_VKI_Wall_Ancient_Collapsed_150_Cut",
      "SM_VKI_Wall_Ancient_Door_150_Cut", "SM_VKI_Wall_Ancient_DoorWide_300_Cut", "SM_VKI_Post_Ancient_Corner_Full",
      "SM_VKI_Post_Ancient_Corner_Cut", "SM_VKI_Post_Ancient_Mid_Full", "SM_VKI_Post_Ancient_Mid_Cut"]),
    ("Cave rock tiles: Full rock", -12.0, [n for n in VKI_CAV_ROCK_NAMES if "C" not in n.split("_")[4]]),
    ("Cave rock tiles: Cut rock", -18.0, [n for n in VKI_CAV_ROCK_NAMES if "F" not in n.split("_")[4]]),
    ("Cave rock tiles: Full meets Cut", -24.0,
     [n for n in VKI_CAV_ROCK_NAMES if {"C", "F"} <= set(n.split("_")[4])][:13]),
    ("Cave rock tiles: Full meets Cut (cont.)", -30.0,
     [n for n in VKI_CAV_ROCK_NAMES if {"C", "F"} <= set(n.split("_")[4])][13:]),
    ("Cave walls, for walled levels, and posts", -36.0, VKI_CWL_NAMES),
    ("Chasm ground tiles, node parity Q00", -42.0, [n for n in VKI_CAV_GROUND_NAMES if n.endswith("_Q00")]),
    ("Chasm ground tiles, node parity Q10", -48.0, [n for n in VKI_CAV_GROUND_NAMES if n.endswith("_Q10")]),
    ("Chasm ground tiles, node parity Q01", -54.0, [n for n in VKI_CAV_GROUND_NAMES if n.endswith("_Q01")]),
    ("Chasm ground tiles, node parity Q11; the all-chasm tile", -60.0,
     [n for n in VKI_CAV_GROUND_NAMES if n.endswith("_Q11")] + ["SM_VKI_Ground_Cave_XXXX"]),
    ("Quarter floors (Floor_075), the rope bridge", -66.0,
     [n for n in VKI_CAV_GROUND_NAMES if n.startswith("SM_VKI_Floor_075_")] + ["SM_VKI_Prop_RopeBridge_420"]),
    ("Dungeon additions: passage, dart wall, secret door; leaves", -72.0,
     ["SM_VKI_Wall_Dungeon_Passage_150_Full", "SM_VKI_Wall_Dungeon_DartTrap_150_Full",
      "SM_VKI_Wall_Dungeon_Secret_150_Full", "SM_VKI_Leaf_Iron_Full", "SM_VKI_Leaf_SecretStone_Full",
      "SM_VKI_Leaf_Portcullis_300", "SM_VKI_Leaf_VaultDisc_300"]),
    ("Pits", -79.5,
     ["SM_VKI_Pit_SpikePit_150", "SM_VKI_Pit_Chasm_150x300", "SM_VKI_Pit_ChasmBridge_150x300",
      "SM_VKI_Pit_Pool_300x300"]),
    ("Traps and loot", -85.5,
     ["SM_VKI_Overlay_PressurePlate", "SM_VKI_Overlay_BladeSlot_150", "SM_VKI_Prop_Lever_Wall", "SM_VKI_Prop_Boulder",
      "SM_VKI_Prop_Chest_Iron", "SM_VKI_Prop_Urns", "SM_VKI_Prop_LootPile", "SM_VKI_Overlay_GoldCoins",
      "SM_VKI_Prop_Skeleton_Fallen"]),
    ("Temple furniture", -91.5,
     ["SM_VKI_Prop_Statue_Guardian", "SM_VKI_Prop_Statue_Broken", "SM_VKI_Prop_Altar_Idol", "SM_VKI_Prop_Column_Ancient",
      "SM_VKI_Prop_Column_Broken", "SM_VKI_Prop_Column_Fallen", "SM_VKI_Prop_Brazier_Stone",
      "SM_VKI_Overlay_CrackedFloor", "SM_VKI_Prop_Roots_Floor", "SM_VKI_Prop_Roots_Wall"]),
    ("Monster lairs", -97.5,
     ["SM_VKI_Overlay_Bedroll", "SM_VKI_Prop_FirePit_Camp", "SM_VKI_Prop_Totem_Goblin", "SM_VKI_Prop_LeanTo",
      "SM_VKI_Prop_Barricade_Stakes", "SM_VKI_Overlay_Refuse", "SM_VKI_Prop_Web_Corner", "SM_VKI_Overlay_WebFloor",
      "SM_VKI_Prop_EggSacs", "SM_VKI_Prop_Cocoon", "SM_VKI_Prop_Burrow", "SM_VKI_Prop_RatHole_Wall"]),
    ("Cave dressing", -103.5,
     ["SM_VKI_Prop_Stalagmites", "SM_VKI_Prop_Crystals", "SM_VKI_Prop_Mushrooms_Glow", "SM_VKI_Prop_RockPillar_Cut",
      "SM_VKI_Prop_RockPillar_Full", "SM_VKI_Prop_Boulders", "SM_VKI_Overlay_Gravel"]),
    ("Transitions: breaches (Dungeon, Ancient), the spill", -109.5, VKI_BRK_NAMES + ["SM_VKI_Overlay_Spill"]),
] + [("Wall-backed rock tiles (%d/5)" % (i + 1), -115.5 - 6.0 * i, VKI_CAV_BACKED_NAMES[23 * i:23 * (i + 1)])
     for i in range(5)]


def vki_adventure_catalog():
    """(re)build VKI_Adventure_Catalog; returns {group: camera name}"""
    return vki_kit_catalog("VKI_Adventure_Catalog", VKI_ADVENTURE_CATALOG, "VKI_AdvCat_", "AncientFlag",
                           host=("SM_VKI_Wall_Ancient_Plain_150A_Full", "SM_VKI_Post_Ancient_Mid_Full"),
                           leaf_on=(("Vault_300_Full", 0.0), ("Secret_150_Full", 0.0)),
                           fy=(int(math.floor(min(gr[1] for gr in VKI_ADVENTURE_CATALOG) - 4.5)), 6))


# ---------------------------------------------------------------- a generated cave: a large map to test the tileset
def vki_rooms_mkplan(nc, nr, codes, ew=None, ns=None):
    """an ASCII plan (the §6 format) from cell codes {(c, r): 2 chars} and optional wall tokens ew {(i, j): 2 chars} /
    ns {(i, r): 1 char}; the perimeter defaults to "##" (north), "==" (south), "#" and "t" (the side walls' row 0)"""
    ew, ns = ew or {}, ns or {}
    lines = ["      " + " ".join("%2d" % i for i in range(nc))]
    for j in range(nr, -1, -1):
        l = "     +"
        for i in range(nc):
            tok = ew.get((i, j), "##" if j == nr else ("==" if j == 0 else "  "))
            l += tok + ("+" if (j in (0, nr) or i == nc - 1 or tok.strip()) else " ")
        lines.append(l)
        if j == 0:
            break
        r = j - 1
        l = "  %2d " % r
        for i in range(nc + 1):
            l += ns.get((i, r), ("t" if r == 0 else "#") if i in (0, nc) else " ")
            if i < nc:
                l += codes.get((i, r), "..")
        lines.append(l)
    return "\n" + "\n".join(lines) + "\n"


def vki_cave_generate(name="VKI_Cave_Test", nc=24, nr=16, seed=7, chasm=True, pools=2, props=18, build=True,
                      poi=None):
    """a cave level from a cellular automaton, registered in VKI_PLANS / VKI_ROOMS and built (vki_build_scene):
    random rock (44 %) with a meandering main passage carved from the west edge to the east edge (three cells tall)
    and a few round chambers kept open; five smoothing passes (rock at >= 5 rock neighbours, open at <= 3; outside
    counts as rock); every open cell kept only if it lies in some 2 x 2 open block (passages two cells wide); the
    largest open region kept. A chasm winds west-east (one to two cells, a row step of at most one per column, so it
    stays connected) with a rope bridge where it runs two cells wide; pools (2 x 2, a cell clear of the chasm); cave
    dressing on cells with open ground all round; a tunnel in the west and east walls. poi = (piece, w, h, code): a
    point of interest (vki_props_poi) on the w x h block of open cells, with a cell of open ground all round and clear
    of the chasm, nearest the map's centre, placed before the pools and dressing. Returns the build summary (or the R
    dict when build=False)."""
    rnd = random.Random(seed)
    cells = [(c, r) for c in range(nc) for r in range(nr)]
    rock = {p: rnd.random() < 0.44 for p in cells}
    carved = set()
    y = rnd.randint(nr // 3, 2 * nr // 3)
    for c in range(nc):                                      # the main passage, west edge to east edge
        y = max(2, min(nr - 3, y + rnd.choice((-1, 0, 0, 1))))
        carved.update((c, y + d) for d in (-1, 0, 1))
    for _ in range(max(2, nc * nr // 90)):                  # round chambers
        cx, cy, rad = rnd.uniform(2, nc - 3), rnd.uniform(2, nr - 3), rnd.uniform(1.6, 3.2)
        carved.update(p for p in cells if (p[0] - cx) ** 2 + ((p[1] - cy) * 1.2) ** 2 < rad * rad)
    for p in carved:
        rock[p] = False
    isrock = lambda c, r: not (0 <= c < nc and 0 <= r < nr) or rock[(c, r)]
    for _ in range(5):
        new = {}
        for (c, r) in cells:
            n = sum(isrock(c + dc, r + dr) for dc in (-1, 0, 1) for dr in (-1, 0, 1) if dc or dr)
            new[(c, r)] = False if (c, r) in carved else (True if n >= 5 else (False if n <= 3 else rock[(c, r)]))
        rock = new
    for _ in range(4):                                       # two-cell passages: an open cell needs a 2 x 2 open block
        keep = set()
        for (c, r) in cells:
            if not rock[(c, r)]:
                for dc in (-1, 0):
                    for dr in (-1, 0):
                        blk = [(c + dc + a, r + dr + b) for a in (0, 1) for b in (0, 1)]
                        if all(not isrock(*q) for q in blk):
                            keep.update(blk)
        rock = {p: p not in keep for p in cells}
    regions, seen = [], set()                                # the largest open region
    for p in cells:
        if rock[p] or p in seen:
            continue
        reg, todo = [], [p]
        seen.add(p)
        while todo:
            c, r = todo.pop()
            reg.append((c, r))
            for q in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if q in rock and not rock[q] and q not in seen:
                    seen.add(q)
                    todo.append(q)
        regions.append(reg)
    big = set(max(regions, key=len)) if regions else set()
    rock = {p: p not in big for p in cells}
    codes = {p: "##" for p in cells if rock[p]}
    xs = set()
    bridge = None
    if chasm:                                                # a connected winding path, one or two cells wide
        c0, c1 = int(nc * 0.08), int(nc * 0.92)
        y = nr / 2 + rnd.uniform(-1, 1)
        ph = rnd.uniform(0, 6.3)
        prev = None
        for c in range(c0, c1):
            want = nr / 2 + 0.25 * nr * math.sin((c - c0) * 0.38 + ph)
            y = y + max(-1.0, min(1.0, want - y))
            w = 2 if vki_vnoise(c * 0.45, 0.3, seed) > 0.4 else 1
            r0 = int(round(y - (w - 1) / 2))
            rows = set(range(r0, r0 + w))
            if prev is not None:                             # keep it 4-connected with the last column
                lo, hi = min(prev | rows), max(prev | rows)
                if not (prev & rows):
                    rows |= set(range(min(max(prev), max(rows)), max(min(prev), min(rows)) + 1))
            for r in rows:
                if (c, r) in big:
                    xs.add((c, r))
            prev = rows
        bridge = None
        for c in sorted(range(nc), key=lambda c: abs(c - nc / 2)):
            col = sorted(r for (cc, r) in xs if cc == c)
            if len(col) == 2 and col[1] == col[0] + 1:     # landings: ground two cells deep, a cell either side
                r = col[0]
                land = [(c + a, q) for a in (-1, 0, 1) for q in (r - 2, r - 1, r + 2, r + 3)]
                if all(q in big and q not in xs for q in land):
                    bridge = (c, r)
                    break
        if bridge is None and xs:                            # shape one column (and its landings) for the bridge
            c = min({cc for (cc, _) in xs}, key=lambda cc: abs(cc - nc / 2))
            r = max(2, min(nr - 4, min(rr_ for (cc, rr_) in xs if cc == c)))
            xs -= {q for q in xs if q[0] == c}
            for a in (-1, 0, 1):
                for q in (r - 2, r - 1, r + 2, r + 3):
                    xs.discard((c + a, q))
            for q in (r - 2, r - 1, r, r + 1, r + 2, r + 3):
                for a in ((-1, 0, 1) if q not in (r, r + 1) else (0,)):
                    if 0 <= c + a < nc:
                        big.add((c + a, q))
                        rock[(c + a, q)] = False
                        codes.pop((c + a, q), None)
            xs |= {(c, r), (c, r + 1)}
            bridge = (c, r)
        def pieces():
            fl = {q for q in big if q not in xs}
            if bridge:                                         # the rope bridge joins its two landings
                fl |= {(bridge[0], bridge[1]), (bridge[0], bridge[1] + 1)}
            out_, seen_ = [], set()
            for q0 in fl:
                if q0 in seen_:
                    continue
                reg_, todo_ = set(), [q0]
                seen_.add(q0)
                while todo_:
                    c_, r_ = todo_.pop()
                    reg_.add((c_, r_))
                    for q in ((c_ + 1, r_), (c_ - 1, r_), (c_, r_ + 1), (c_, r_ - 1)):
                        if q in fl and q not in seen_:
                            seen_.add(q)
                            todo_.append(q)
                out_.append(reg_)
            return sorted(out_, key=len, reverse=True)
        for _ in range(6):                                     # natural land bridges: gaps in the chasm
            regs = pieces()
            if len(regs) < 2 or len(regs[1]) < 4:
                break
            a_, b_ = regs[0], regs[1]
            best = None
            for c_ in {q[0] for q in xs}:
                col_ = [q for q in xs if q[0] == c_ and (bridge is None or c_ != bridge[0])]
                if not col_:
                    continue
                lo_, hi_ = min(q[1] for q in col_), max(q[1] for q in col_)
                ends = {(c_, lo_ - 1), (c_, hi_ + 1)}
                if (ends & a_) and (ends & b_):
                    best = c_ if best is None or abs(c_ - nc / 2) > abs(best - nc / 2) else best
            if best is None:
                break
            xs -= {q for q in xs if q[0] == best}
        for p in xs:
            codes[p] = "vv"
        if bridge:
            c, r = bridge
            codes[(c, r)] = codes[(c, r + 1)] = "=="
    near_x = lambda c, r, d=1: any((c + a, r + b) in xs for a in range(-d, d + 1) for b in range(-d, d + 1))
    clear_ = set()                                           # the bridge's landings stay clear of props
    if bridge:
        clear_ = {(bridge[0] + a, bridge[1] + q) for a in (-1, 0, 1) for q in (-2, -1, 2, 3)}
    free = lambda c, r: (c, r) in big and (c, r) not in xs and (c, r) not in clear_ and codes.get((c, r), "..") == ".."
    tun, links = {}, []
    for side, i, cs_ in (("west", 0, (0, 1)), ("east", nc, (nc - 1, nc - 2))):
        js = [j for j in range(2, nr - 1) if all(free(c_, j + d) for c_ in cs_ for d in (-2, -1, 0, 1))]
        if js:
            j = min(js, key=lambda j: abs(j - nr / 2))
            tun[(i, j)] = side
            links.append((side, "passage", "@return"))
            for c_ in cs_:
                for d in (-2, -1, 0, 1):
                    clear_.add((c_, j + d))
            codes[(cs_[0], j - 1)] = codes[(cs_[0], j)] = "Sx"
    poi_prop = None
    if poi:                                                  # the point of interest: the open block nearest the centre
        pc_, pw, ph_, pcode = poi
        blocks = [(c, r) for (c, r) in cells if all(free(c + a, r + b) for a in range(-1, pw + 1) for b in range(-1, ph_ + 1))
                  and not any(near_x(c + a, r + b) for a in range(pw) for b in range(ph_))]
        if blocks:
            c, r = min(blocks, key=lambda q: (q[0] + pw / 2 - nc / 2) ** 2 + (q[1] + ph_ / 2 - nr / 2) ** 2)
            poi_prop = (pc_, VKI_IG * (c + pw / 2), VKI_IG * (r + ph_ / 2), 0, None, None, {"hug": False})
            for a in range(pw):
                for b in range(ph_):
                    codes[(c + a, r + b)] = pcode
    pits, used = [], set()
    cand = [(c, r) for (c, r) in cells if all(free(c + a, r + b) for a in range(-1, 3) for b in range(-1, 3))
            and not any(near_x(c + a, r + b) for a in (0, 1) for b in (0, 1))]
    rnd.shuffle(cand)
    for (c, r) in cand:
        if len(pits) >= pools:
            break
        blk = [(c + a, r + b) for a in (0, 1) for b in (0, 1)]
        if any(any(abs(q[0] - u[0]) < 4 and abs(q[1] - u[1]) < 4 for u in used) for q in blk):
            continue
        pits.append(("Pit_Pool_300x300", VKI_IG * c, VKI_IG * r))
        for q in blk:
            codes[q] = "~~"
            used.add(q)
    NH = {"hug": False}
    plist = []
    if chasm and bridge:
        plist.append(("RopeBridge_420", VKI_IG * bridge[0] + 0.75, VKI_IG * (bridge[1] + 1), 0, None, None, NH))
    if poi_prop:
        plist.append(poi_prop)
    kinds = [("Crystals", "CR"), ("Mushrooms_Glow", "MG"), ("Stalagmites", "SM"), ("Boulders", "BD"),
             ("Overlay_Gravel", "gv"), ("Crystals", "CR"), ("Stalagmites", "SM"), ("Mushrooms_Glow", "MG")]
    spots = [(c, r) for (c, r) in cells if all(free(c + a, r + b) for a in (-1, 0, 1) for b in (-1, 0, 1))]
    rnd.shuffle(spots)
    placed = []
    for (c, r) in spots:
        if len(placed) >= props:
            break
        if any(abs(c - u[0]) + abs(r - u[1]) < 4 for u in placed):
            continue
        piece, code = kinds[len(placed) % len(kinds)]
        plist.append((piece, VKI_IG * (c + 0.5), VKI_IG * (r + 0.5), 0, None, None, NH))
        codes[(c, r)] = code
        placed.append((c, r))
    R = dict(building="Dungeon", floor=-9, preset="Cavern", family=dict(perimeter="Cave", partition="Cave"), cave=True,
             pools=False, zones={"cavern": dict(cells="rest", floor="CaveFloor")}, tunnels=tun, links=links, pits=pits,
             props=plist, generated=dict(seed=seed, nc=nc, nr=nr), debris=dict(density=0.34, seed=seed))
    VKI_PLANS[name] = vki_rooms_mkplan(nc, nr, codes)
    VKI_ROOMS[name] = R
    if not build:
        return R
    out = vki_build_scene(name)
    bpy.data.scenes[name]["vki_generated"] = json.dumps(dict(nc=nc, nr=nr, seed=seed, chasm=chasm, pools=pools,
                                                             props=props, poi=list(poi) if poi else None))
    return out
