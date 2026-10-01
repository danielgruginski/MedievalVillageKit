# ===================== VKI WORLD: the world graph (docs/WORLD_GRAPH.md) =====================
# Loaded by vki_ns() after the level texts. Every level's scene links make one graph: the interiors' R["links"]
# (VKI_ROOMS) and the valley's (vk_mod_entrances ENT_TOWN_LINKS; the valley is level VKI_TOWN). A link (level, id, kind,
# target) takes the walker to its target level, onto that level's link back -- its link whose target is the level
# left -- at that link's SPN_<id> spawn. Two placeholders stand for levels outside the graph (VKI_WORLD_HOLES):
# "@return" (back to wherever the game came from: the building interiors, the demos) and "@deep" (an open end below:
# the mine's lift).
#   vki_world_links()             -> [dict(level, id, kind, target)], the valley's with its piece
#   vki_world_check(built=True)   -> (errors, notes): targets that are no level, one-way links, ambiguous arrivals (two
#                                    links back), two links from one level to one target, kinds that don't pair
#                                    (VKI_WORLD_PAIRS), and with built=True a link object (vki_link, vki_link_id,
#                                    vki_target) and an SPN_ spawn for each link in its built scene / the valley
#   vki_world_json(path=None)     -> the graph as a dict (written as JSON when path is given; docs/world_graph.json)
# Every top-level name starts with vki_/VKI_ (T18).

VKI_WORLD_HOLES = {"@return": "back to wherever the game came from (building interiors, demos)",
                   "@deep": "an open end below (the mine's lift; no deeper level is built yet)"}
VKI_WORLD_PAIRS = {("passage", "passage"), ("stair_up", "stair_down"), ("stair_down", "stair_up"), ("lift", "lift")}
VKI_WORLD_JSON = os.path.join(VKI_ROOT, "docs", "world_graph.json")


def vki_world_links():
    """every level's links: [dict(level, id, kind, target)] (the valley's carry their piece)"""
    out = []
    for lvl, R in VKI_ROOMS.items():
        for (lid, kind, target) in R.get("links", []):
            out.append(dict(level=lvl, id=lid, kind=kind, target=target))
    for (lid, kind, target, piece) in ENT_TOWN_LINKS:
        out.append(dict(level=VKI_TOWN, id=lid, kind=kind, target=target, piece=piece))
    return out


def vki_world_level_objects(lvl):
    """the objects of a built level (the valley: its collection), or None when it is not built"""
    if lvl == VKI_TOWN:
        c = bpy.data.collections.get(VKI_TOWN)
        return list(c.all_objects) if c is not None else None
    sc = bpy.data.scenes.get(lvl)
    return list(sc.objects) if sc is not None else None


def vki_world_check(built=True):
    """(errors, notes) for the world graph; see the header"""
    links = vki_world_links()
    levels = set(VKI_ROOMS) | {VKI_TOWN}
    by = {}
    for l in links:
        by.setdefault(l["level"], []).append(l)
    errors, notes = [], []
    for l in links:
        t, tag = l["target"], f'{l["level"]}:{l["id"]}'
        if t in VKI_WORLD_HOLES:
            notes.append(f"{tag} -> {t}: {VKI_WORLD_HOLES[t]}")
            continue
        if t not in levels:
            errors.append(f"{tag} -> {t}: no such level")
            continue
        back = [b for b in by.get(t, []) if b["target"] == l["level"]]
        if not back:
            errors.append(f"{tag} -> {t}: one-way ({t} has no link back to {l['level']})")
        elif len(back) > 1:
            errors.append(f"{tag} -> {t}: {len(back)} links back ({', '.join(b['id'] for b in back)}), the arrival "
                          f"is ambiguous")
        elif (l["kind"], back[0]["kind"]) not in VKI_WORLD_PAIRS:
            errors.append(f"{tag} ({l['kind']}) -> {t}:{back[0]['id']} ({back[0]['kind']}): kinds don't pair")
    for lvl, ls in by.items():
        seen = {}
        for l in ls:
            if l["target"] not in VKI_WORLD_HOLES:
                seen.setdefault(l["target"], []).append(l["id"])
        for t, ids in seen.items():
            if len(ids) > 1:
                errors.append(f"{lvl}: {len(ids)} links to {t} ({', '.join(ids)})")
    if built:
        for lvl, ls in sorted(by.items()):
            objs = vki_world_level_objects(lvl)
            if objs is None:
                notes.append(f"{lvl}: not built")
                continue
            for l in ls:
                lk = [o for o in objs if o.get("vki_link") and o.get("vki_link_id") == l["id"]]
                sp = [o for o in objs if o.get("vki_spawn_id") == l["id"]]
                if len(lk) != 1:
                    errors.append(f"{lvl}:{l['id']}: {len(lk)} link objects in the built level")
                elif lk[0].get("vki_target") != l["target"] or lk[0].get("vki_link") != l["kind"]:
                    errors.append(f"{lvl}:{l['id']}: the built link is {lk[0].get('vki_link')} -> "
                                  f"{lk[0].get('vki_target')} (rebuild the level)")
                if len(sp) != 1:
                    errors.append(f"{lvl}:{l['id']}: {len(sp)} SPN_ spawns in the built level")
    return errors, notes


def vki_world_json(path=None):
    """the world graph for a Unity scene loader: {start, holes, levels: {level: {kind, links: [{id, kind, target,
    arrive}]}}} -- arrive is the target level's link back (where the walker lands), None for a hole or a one-way
    link. Written to path (VKI_WORLD_JSON for the docs) when given."""
    import json
    by = {}
    for l in vki_world_links():
        by.setdefault(l["level"], []).append(l)
    out = {"version": 1, "start": VKI_TOWN, "holes": VKI_WORLD_HOLES, "levels": {}}
    for lvl in sorted(by):
        rows = []
        for l in by[lvl]:
            back = [b for b in by.get(l["target"], []) if b["target"] == lvl]
            row = dict(id=l["id"], kind=l["kind"], target=l["target"], arrive=back[0]["id"] if len(back) == 1 else None)
            if l.get("piece"):
                row["piece"] = l["piece"]
            rows.append(row)
        kind = "exterior" if lvl == VKI_TOWN else VKI_ROOMS[lvl].get("building", "")
        out["levels"][lvl] = dict(kind=kind, links=rows)
    if path:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(out, indent=1) + "\n")
    return out
