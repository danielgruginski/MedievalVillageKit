"""Same seed, same level: the room generators' dumps from Unity and Godot side by side (FULL_PORT_PLAN phase 4).

usage: py tools/rooms_parity.py <unity.jsonl> <godot.jsonl> [--verbose]

Godot: kit_cli -- rooms dump all <count> <first seed> <out.jsonl>. Unity: the same runs and seeds through KitRoom
(tools/rooms_parity_unity.cs, run in the Unity editor); one JSON object a line: label, seed, plan, record, placed
[piece, what, x, y, z, rot], spawns [id, x, y, facing], links, encounters [id, creature, budget, points], notes. For
each level: the plan must be the same text, the record the same JSON (numbers to 1e-4), the placements the same multiset (pieces, what,
places to 2 mm, turns to 0.05 degrees), and the same spawns, links, encounters and notes (numbers left out: node
names and slide lengths print differently).
"""
import json
import re
import sys


def load(p):
    """the objects one after another (a record may span lines: Unity's is indented)"""
    out, text, i, dec = {}, open(p, encoding="utf-8").read(), 0, json.JSONDecoder()
    while True:
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            return out
        d, i = dec.raw_decode(text, i)
        out[(d["label"], d["seed"])] = d


def same(a, b, path="", tol=1e-4, diffs=None):
    """JSON values equal, numbers within tol; the first differences into diffs"""
    if diffs is not None and len(diffs) >= 5:
        return False
    if isinstance(a, bool) or isinstance(b, bool):
        ok = a == b
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        ok = abs(a - b) <= tol
    elif isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            if diffs is not None:
                diffs.append(f"{path}: keys {sorted(set(a) ^ set(b))}")
            return False
        return all([same(a[k], b[k], f"{path}.{k}", tol, diffs) for k in a])
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            if diffs is not None:
                diffs.append(f"{path}: {len(a)} vs {len(b)} items")
            return False
        return all([same(x, y, f"{path}[{i}]", tol, diffs) for i, (x, y) in enumerate(zip(a, b))])
    else:
        ok = a == b
    if not ok and diffs is not None:
        diffs.append(f"{path}: {json.dumps(a)[:80]} vs {json.dumps(b)[:80]}")
    return ok


def unmatched(a, b, tol=0.002, rtol=0.05):
    """placements of a with no partner in b (same piece and what, places within tol, turns within rtol degrees)"""
    left = {}
    for q in b:
        left.setdefault((q[0], q[1]), []).append(q)
    out = []
    for p in a:
        cands = left.get((p[0], p[1]), [])
        for i, q in enumerate(cands):
            dr = abs((p[5] - q[5] + 180) % 360 - 180)
            if abs(p[2] - q[2]) <= tol and abs(p[3] - q[3]) <= tol and abs(p[4] - q[4]) <= tol and dr <= rtol:
                cands.pop(i)
                break
        else:
            out.append(p)
    return out


def note(n):
    """a note without node-name suffixes and numbers (Godot names a second Bed_Straw Bed_Straw2; slides print 0,32 / 0,33)"""
    return re.sub(r"-?\d+([.,]\d+)?", "", n)


def main():
    u, g = load(sys.argv[1]), load(sys.argv[2])
    verbose = "--verbose" in sys.argv
    bad = 0
    for k in sorted(set(u) | set(g)):
        a, b = u.get(k), g.get(k)
        tag = f"{k[0]} seed {k[1]}"
        if a is None or b is None:
            print(f"{tag}: only in {'godot' if a is None else 'unity'}")
            bad += 1
            continue
        if "error" in a or "error" in b:
            print(f"{tag}: error unity={a.get('error', '')[:100]!r} godot={b.get('error', '')[:100]!r}")
            bad += 1
            continue
        probs = []
        if a["plan"] != b["plan"]:
            probs.append("plan differs")
        d = []
        if not same(a["record"], b["record"], "record", diffs=d):
            probs.append("record: " + "; ".join(d))
        only_u, only_g = unmatched(a["placed"], b["placed"]), unmatched(b["placed"], a["placed"])
        if only_u or only_g:
            probs.append(f"placed: {len(a['placed'])} vs {len(b['placed'])}, {len(only_u)} only in unity, {len(only_g)} only in godot"
                         + (f" (unity {only_u[:3]}, godot {only_g[:3]})" if verbose else ""))
        a["notes"], b["notes"] = [note(n) for n in a["notes"]], [note(n) for n in b["notes"]]
        for f in ("spawns", "links", "encounters", "notes"):
            d = []
            if not same(sorted(a[f], key=json.dumps), sorted(b[f], key=json.dumps), f, tol=0.002, diffs=d):
                probs.append(f"{f}: " + "; ".join(d))
        if probs:
            bad += 1
            print(f"{tag}: " + " | ".join(probs))
        elif verbose:
            print(f"{tag}: same ({len(a['placed'])} pieces)")
    n = len(set(u) | set(g))
    print(f"{n - bad}/{n} levels the same")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
