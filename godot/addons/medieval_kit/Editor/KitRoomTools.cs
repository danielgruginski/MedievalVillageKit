#if TOOLS
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.Json.Nodes;
using Godot;

namespace MedievalKit.Editor;

/// <summary>
/// Checks for KitRoom and the room generators (FULL_PORT_PLAN phase 4), each on a host node in the tree:
/// <see cref="WalkTest"/> (a room's navmesh: every spawn, link and encounter point and every floor cell on the first
/// spawn's island), <see cref="ValidateGenerators"/> (seeds of each generator built and walk-tested),
/// <see cref="GoldenTest"/> (the kit's Blender rooms rebuilt from their plans against Blender's export) and
/// <see cref="Dump"/> (the generators' plans, records and placements as JSON lines, to diff against Unity's for the same
/// seeds). kit_cli: rooms validate | golden | dump. Unity: KitRoomTools.
/// </summary>
public static class KitRoomTools
{
    /// <summary>plan codes of open floor (the island check's cells; any other code is a prop's)</summary>
    static readonly HashSet<string> FloorCodes = new() { "..", "Ss", "Sx", "==", "ss" };

    /// <summary>the last walk test's numbers: spawns / points reached, of, floor cells reached, of</summary>
    public static (int ok, int total, int floorOk, int floorTotal) LastWalk;

    /// <summary>the generator runs of the validation and the dump, as Unity's ValidateGenerators</summary>
    public static List<(string label, Action<KitRoom, int> make)> Runs(string which)
    {
        var runs = new List<(string, Action<KitRoom, int>)>();
        bool all = which == "all";
        if (all || which == "cave")
        {
            runs.Add(("cave maze", (r, sd) => { r.cave.seed = sd; r.RandomCave(); }));
            runs.Add(("cave open", (r, sd) => { r.cave.seed = sd; r.cave.layout = "Open"; r.RandomCave(); }));
        }
        if (all || which == "dungeon")
            foreach (var th in new[] { "Dungeon", "Crypt", "Warren", "Hideout" })
                runs.Add(($"dungeon {th}", (r, sd) => { r.dungeon.seed = sd; r.dungeon.theme = th; r.RandomDungeon(); }));
        if (all || which == "sewer")
        {
            runs.Add(("sewer", (r, sd) => { r.sewer.seed = sd; r.RandomSewer(); }));
            runs.Add(("sewer large", (r, sd) => { r.sewer.seed = sd; r.sewer.nc = 40; r.sewer.nr = 28; r.sewer.deep = "@deep"; r.RandomSewer(); }));
        }
        if (all || which == "connector")
            foreach (var (f, t) in new[] { ("S", "N"), ("W", "E"), ("S", "E"), ("N", "W") })
                runs.Add(($"connector {f}-{t}", (r, sd) => { r.connector.seed = sd; r.connector.from = f; r.connector.to = t; r.RandomConnector(); }));
        if (all || which == "interior")
            foreach (var kind in new[] { "Cottage", "Townhouse", "Tavern", "Workshop" })
                runs.Add(($"interior {kind}", (r, sd) => { r.interior.seed = sd; r.interior.kind = kind; r.RandomInterior(); }));
        return runs;
    }

    static KitRoom NewRoom(Node host, string name)
    {
        var room = new KitRoom { Name = name, buildLights = false };
        host.AddChild(room);
        return room;
    }

    static void Free(Node n)
    {
        n.GetParent()?.RemoveChild(n);
        n.Free();
    }

    /// <summary>a room's navmesh (KitNavMesh.Bake: its solid colliders, 0.05 m cells, the kit's walker), then: every
    /// spawn, link and encounter point on the island of the spawn that holds most of them, and every floor cell (the
    /// plan's open cells, not a stair's own; where the navmesh lies at the start's height) on it too. The room must be
    /// in the tree.</summary>
    public static string WalkTest(KitRoom room, float voxel = 0.05f)
    {
        var nm = KitNavMesh.Bake(room, voxel);
        var points = KitWalkTest.Points(room);
        var res = KitWalkTest.Run(nm, points);
        var map = KitWalkTest.Join(nm);
        var start = points.FirstOrDefault(p => p.Name == res.Start);
        int home = start != null ? map.At(start.At) : -1;
        int floorPts = 0, islands = 0;
        var islandAt = new List<string>();
        if (!string.IsNullOrEmpty(room.plan) && start != null)
        {
            var pl = KitRoomPlan.Parse(room.plan);
            for (int c = 0; c < pl.nc; c++)
                for (int r = 0; r < pl.nr; r++)
                {
                    if (room.Layout != null && room.Layout.stairCells.ContainsKey((c, r))) continue;      // a stair's own cells: its steps
                    if (pl.codes.TryGetValue((c, r), out var code) && !FloorCodes.Contains(code)) continue;  // a prop's cell: slivers round it
                    var q = new Vector3(1.5f * c + 0.75f, start.At.Y, -(1.5f * r + 0.75f));
                    int at = map.At(q, 0.35f, 0.3f);
                    if (at < 0) continue;
                    floorPts++;
                    if (at != home) { islands++; if (islandAt.Count < 6) islandAt.Add($"{c},{r}"); }
                }
        }
        LastWalk = (res.Reached, res.Total, floorPts - islands, floorPts);
        return $"{room.Name}: {res}; floor {floorPts - islands}/{floorPts} reachable" + (islands > 0 ? $" (islands at cells {string.Join(" ", islandAt)})" : "");
    }

    /// <summary>`count` seeds of each generator run ("cave", "dungeon", "sewer", "connector", "interior" or "all"), each
    /// built and walk-tested; the failing seeds listed. Unity: KitRoomTools.ValidateGenerators.</summary>
    public static string ValidateGenerators(Node host, int count, string which, int firstSeed = 1)
    {
        var sb = new StringBuilder();
        var t0 = DateTime.Now;
        foreach (var (label, make) in Runs(which))
        {
            var bad = new List<string>();
            int built = 0;
            for (int sd = firstSeed; sd < firstSeed + count; sd++)
            {
                var room = NewRoom(host, $"{label} {sd}".Replace(' ', '_'));
                try
                {
                    make(room, sd);
                    built++;
                    string line = WalkTest(room);
                    var w = LastWalk;
                    if (!(w.ok == w.total && w.floorOk == w.floorTotal)) bad.Add($"{sd} ({w.ok}/{w.total}, floor {w.floorOk}/{w.floorTotal}: {line})");
                }
                catch (Exception e) { bad.Add($"{sd} (error: {e.GetBaseException().Message})"); }
                finally { Free(room); }
            }
            string l = $"{label}: {built - bad.Count}/{count} seeds walkable" + (bad.Count > 0 ? $"; failing: {string.Join("; ", bad)}" : "");
            sb.AppendLine(l);
            GD.Print("[rooms] " + l);
        }
        sb.AppendLine($"({(DateTime.Now - t0).TotalSeconds:0} s)");
        return sb.ToString();
    }

    static string F(float v) => Math.Round(v, 3).ToString(CultureInfo.InvariantCulture);

    /// <summary>a built room as one JSON object: its plan and record, every placement (piece, what, x, y, z, rot in
    /// Blender room space), spawns, links, encounters and notes; Unity's dump writes the same</summary>
    public static JsonObject Describe(KitRoom room, string label, int seed)
    {
        var placed = new JsonArray();
        foreach (var p in room.placed) placed.Add(KitJson.A(p.piece, p.what, Math.Round(p.x, 3), Math.Round(p.y, 3), Math.Round(p.z, 3), Math.Round(p.rot, 2)));
        var spawns = new JsonArray();
        foreach (var s in KitNodes.Below(room, "").OfType<KitSpawn>())
            spawns.Add(KitJson.A(s.SpawnId, Math.Round(s.Position.X, 3), Math.Round(-s.Position.Z, 3), Math.Round(s.FacingDeg, 2)));
        var links = new JsonArray();
        foreach (var l in KitNodes.Below(room, "").OfType<KitLink>().Select(l => $"{l.LinkId}:{l.Kind}->{l.Target}").OrderBy(s => s, StringComparer.Ordinal))
            links.Add(l);
        var enc = new JsonArray();
        foreach (var e in KitNodes.Below(room, "").OfType<KitEncounter>())
            enc.Add(KitJson.A(e.EncounterId, e.Creature, e.Budget, e.Points.Count()));
        var notes = new JsonArray();
        foreach (var n in room.notes) notes.Add(n);
        return new JsonObject
        {
            ["label"] = label, ["seed"] = seed, ["plan"] = room.plan, ["record"] = KitJson.ParseObject(room.record),
            ["placed"] = placed, ["spawns"] = spawns, ["links"] = links, ["encounters"] = enc, ["notes"] = notes,
        };
    }

    /// <summary>the generators' levels for seeds firstSeed.. (each run of <see cref="Runs"/>) as JSON lines in `outPath`,
    /// for tools/rooms_parity.py to diff against Unity's dump of the same seeds</summary>
    public static string Dump(Node host, string which, int count, int firstSeed, string outPath)
    {
        var sb = new StringBuilder();
        int n = 0;
        foreach (var (label, make) in Runs(which))
            for (int sd = firstSeed; sd < firstSeed + count; sd++)
            {
                var room = NewRoom(host, "Dump");
                try
                {
                    make(room, sd);
                    sb.Append(KitJson.Text(Describe(room, label, sd), false)).Append('\n');
                    n++;
                }
                catch (Exception e) { sb.Append(KitJson.Text(new JsonObject { ["label"] = label, ["seed"] = sd, ["error"] = e.ToString() }, false)).Append('\n'); }
                finally { Free(room); }
            }
        using (var f = FileAccess.Open(outPath, FileAccess.ModeFlags.Write)) f.StoreString(sb.ToString());
        return $"dump: {n} levels -> {outPath}";
    }

    class Item
    {
        public string piece, what; public float x, y, z, rot, tol = 0.002f; public Dictionary<string, string> mat; public bool used, debris;
    }

    static float AngDiff(float a, float b) { float d = Mathf.PosMod(a - b, 360f); return Mathf.Min(d, 360f - d); }

    /// <summary>a Godot layout transform's turn about y (Blender's about z), degrees</summary>
    static float Yaw(JsonNode basis) => Mathf.RadToDeg(Mathf.Atan2(-basis[0][2].F(), basis[0][0].F()));

    /// <summary>surface -> material name where a placed piece's surface was given another material than its own</summary>
    static Dictionary<string, string> Overrides(KitRoom.Placed p)
    {
        var o = new Dictionary<string, string>();
        var mi = p.kp?.MeshInstance;
        if (mi?.Mesh == null) return o;
        for (int i = 0; i < mi.Mesh.GetSurfaceCount(); i++)
            if (mi.GetSurfaceOverrideMaterial(i) is { } m && m != mi.Mesh.SurfaceGetMaterial(i))
                o[i.ToString()] = m.ResourcePath.GetFile().GetBaseName();
        return o;
    }

    static string MatStr(Dictionary<string, string> m) =>
        m == null || m.Count == 0 ? "{}" : "{" + string.Join(", ", m.OrderBy(k => int.Parse(k.Key)).Select(k => $"{k.Key}:{k.Value.Split("__s")[0]}")) + "}";

    /// <summary>the kit's Blender rooms (interior_rules' presets) rebuilt from their plans and records, against Blender's
    /// export of the same rooms (res://kit/data/layouts/&lt;room&gt;.json): pieces (shell to 2 mm, props to 5 cm, turns to
    /// a degree, debris not compared), the materials restyled per surface, spawns (2 mm, half a degree), links, lights.
    /// Unity: KitRoomTools.GoldenTest (Smithy and Townhouse_F1 differ there by known 0.3 m prop slides).</summary>
    public static string GoldenTest(Node host, string log = null)
    {
        var rules = KitInteriorRules.Default;
        var summary = new StringBuilder();
        var detail = new StringBuilder();
        int totalOk = 0, totalBad = 0;
        foreach (var name in rules.RoomNames)
        {
            string lp = $"{KitPaths.LayoutData}{name}.json";
            if (!FileAccess.FileExists(lp)) { summary.AppendLine($"{name}: no exported level"); continue; }
            var lv = KitJson.ParseObject(FileAccess.GetFileAsString(lp));
            var room = NewRoom(host, name);
            try
            {
                room.buildLights = true;
                room.LoadPreset(name);
                room.Generate();
                int myDebris = room.placed.Count(p => p.what == "debris");
                var mine = room.placed.Where(p => p.what != "debris").Select(p => new Item { piece = p.piece, what = p.what, x = p.x, y = p.y, z = p.z, rot = p.rot, mat = Overrides(p) }).ToList();
                var theirs = new List<Item>();
                foreach (var p in lv["placements"].AsArray())
                {
                    string coll = p["coll"].S() ?? "";
                    string pn = p["piece"].S();
                    if (pn.StartsWith("U_") && p["props"]?["vki_piece"] != null) pn = p["props"]["vki_piece"].S();   // a restyle exported as its own mesh
                    var o = p["origin"];
                    theirs.Add(new Item
                    {
                        piece = pn, x = o[0].F(), y = -o[2].F(), z = o[1].F(), rot = Yaw(p["basis"]),
                        tol = coll.EndsWith("_Shell") ? 0.002f : 0.05f,       // props: the general idea, not to the millimetre
                        debris = coll.EndsWith("_Props") && p["props"]?["vki_prop_index"] == null && !pn.Contains("RushMat") && !pn.Contains("WindowPool"),
                        mat = (p["mat"] as JsonObject)?.ToDictionary(q => q.Key, q => q.Value.S()) ?? new Dictionary<string, string>(),
                    });
                }
                var missing = new List<Item>();
                var matBad = new List<string>();
                foreach (var t in theirs)
                {
                    var m = mine.FirstOrDefault(u => !u.used && u.piece == t.piece && Math.Abs(u.x - t.x) < t.tol && Math.Abs(u.y - t.y) < t.tol &&
                                                     Math.Abs(u.z - t.z) < t.tol && AngDiff(u.rot, t.rot) < 1f);
                    if (m == null) { missing.Add(t); continue; }
                    m.used = true;
                    if (MatStr(m.mat) != MatStr(t.mat)) matBad.Add($"{t.piece} @ {F(t.x)},{F(t.y)}: godot {MatStr(m.mat)} blender {MatStr(t.mat)}");
                }
                var extra = mine.Where(u => !u.used).ToList();
                var debris = missing.Where(i => i.debris).ToList();         // strewn by vki_rooms_debris: not compared
                missing = missing.Where(i => !i.debris).ToList();
                // spawns
                var spB = lv["markers"].AsArray().Where(mk => mk["props"]?["vki_spawn_id"] != null)
                    .Select(mk => (id: mk["props"]["vki_spawn_id"].S(), at: new Vector3(mk["origin"][0].F(), mk["origin"][1].F(), mk["origin"][2].F()), facing: mk["props"]["vki_facing_deg"].F())).ToList();
                var spG = KitNodes.Below(room, "").OfType<KitSpawn>().Select(s => (id: s.SpawnId, at: s.Position, facing: s.FacingDeg)).ToList();
                var spBad = new List<string>();
                foreach (var b in spB)
                {
                    var u = spG.FirstOrDefault(s => s.id == b.id);
                    if (u.id == null) spBad.Add($"spawn {b.id}: missing");
                    else if ((u.at - b.at).Length() > 0.002f || AngDiff(u.facing, b.facing) > 0.5f)
                        spBad.Add($"spawn {b.id}: godot {u.at} {u.facing} vs blender {b.at} {b.facing}");
                }
                if (spG.Count != spB.Count) spBad.Add($"spawns: godot {spG.Count} vs blender {spB.Count}");
                // links
                var lkB = lv["placements"].AsArray().Where(p => p["props"]?["vki_link"] != null)
                    .Select(p => $"{p["props"]["vki_link_id"].S()}:{p["props"]["vki_link"].S()}->{p["props"]["vki_target"].S()}").OrderBy(s => s, StringComparer.Ordinal).ToList();
                var lkG = KitNodes.Below(room, "").OfType<KitLink>().Select(l => $"{l.LinkId}:{l.Kind}->{l.Target}").OrderBy(s => s, StringComparer.Ordinal).ToList();
                string lkRes = lkB.SequenceEqual(lkG) ? "ok" : $"godot [{string.Join(", ", lkG)}] vs blender [{string.Join(", ", lkB)}]";
                // lights (the pieces' and the props' sockets)
                var ltB = lv["lights"].AsArray().Where(l => l["name"].S().StartsWith("LIT_"))
                    .Select(l => (at: new Vector3(l["origin"][0].F(), l["origin"][1].F(), l["origin"][2].F()), w: l["energy"].F())).ToList();
                var ltG = room.lightsBuilt.ToList();
                int ltOk = ltB.Count(b => ltG.Any(u => (u.pos - b.at).Length() < 0.06f && Math.Abs(u.w - b.w) < 0.01f));

                int ok = theirs.Count - debris.Count - missing.Count;
                bool good = missing.Count == 0 && extra.Count == 0 && matBad.Count == 0 && spBad.Count == 0 && lkRes == "ok" && ltOk == ltB.Count && ltG.Count == ltB.Count;
                if (good) totalOk++; else totalBad++;
                summary.AppendLine($"{name}: {(good ? "OK" : "DIFF")}  pieces {ok}/{theirs.Count - debris.Count} matched, {missing.Count} missing, {extra.Count} extra, " +
                                   $"{matBad.Count} material diffs, debris {debris.Count} in Blender / {myDebris} here (strewn, not compared); spawns {spB.Count - spBad.Count(s => s.StartsWith("spawn "))}/{spB.Count}; links {lkRes}; " +
                                   $"lights {ltOk}/{ltB.Count} (godot {ltG.Count})");
                detail.AppendLine($"==== {name}");
                foreach (var t in missing) detail.AppendLine($"  missing (blender only): {t.piece} @ {F(t.x)},{F(t.y)},{F(t.z)} rot {t.rot:0.#}");
                foreach (var u in extra) detail.AppendLine($"  extra (godot only): {u.piece} @ {F(u.x)},{F(u.y)},{F(u.z)} rot {u.rot:0.#} [{u.what}]");
                foreach (var s in matBad) detail.AppendLine($"  material: {s}");
                foreach (var s in spBad) detail.AppendLine($"  {s}");
                if (lkRes != "ok") detail.AppendLine($"  links: {lkRes}");
                foreach (var b in ltB.Where(b => !ltG.Any(u => (u.pos - b.at).Length() < 0.06f && Math.Abs(u.w - b.w) < 0.01f)))
                    detail.AppendLine($"  light missing: {b.at} {b.w} W");
                foreach (var n in room.notes) detail.AppendLine($"  note: {n}");
            }
            catch (Exception e) { summary.AppendLine($"{name}: ERROR {e.GetBaseException().Message}"); totalBad++; }
            finally { Free(room); }
        }
        string text = $"KitRoom golden test: {totalOk} rooms match, {totalBad} differ\n{summary}\n{detail}";
        if (log != null) using (var f = FileAccess.Open(log, FileAccess.ModeFlags.Write)) f.StoreString(text);
        return $"KitRoom golden test: {totalOk} rooms match, {totalBad} differ\n{summary}";
    }
}
#endif
