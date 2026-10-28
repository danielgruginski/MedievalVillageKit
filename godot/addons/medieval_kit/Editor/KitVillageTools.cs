#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;

namespace MedievalKit.Editor;

/// <summary>
/// Outdoor maps from layouts (FULL_PORT_PLAN phase 5): <see cref="BuildVillage"/> builds a layout into a scene of its
/// own (a KitLevel holding the KitVillage, VK_ValleyTown's sun and sky, a camera at the arrival, the navmesh) with the
/// ground's mesh, control map and materials saved beside it; <see cref="WalkVillage"/> checks it can be played. kit_cli:
/// village &lt;layout.json&gt; &lt;scene.tscn&gt;. Unity: KitVillageTools.
/// </summary>
public static class KitVillageTools
{
    /// <summary>a point in the map's plan metres (x east, y north), from the village's space</summary>
    static Vector2 Plan(Vector3 p) => new(p.X, -p.Z);

    /// <summary>the village's not-walkable outlines in its own space: the forest beyond the walls, the sea, the ground
    /// under the tiers, and the raised crop beds (soft pieces, no collider: Unity carves them in play)</summary>
    public static List<(Vector3[] poly, float bottom, float top)> NotWalkable(KitVillage v)
    {
        var o = new List<(Vector3[], float, float)>();
        static Vector3[] Box(UnityMath.Rect r) => new[] { new Vector3(r.xMin, 0, -r.yMin), new Vector3(r.xMax, 0, -r.yMin), new Vector3(r.xMax, 0, -r.yMax), new Vector3(r.xMin, 0, -r.yMax) };
        foreach (var r in v.Outside()) o.Add((Box(r), -200f, 400f));                      // beyond the walls: floor to sky
        foreach (var r in v.UnderTerrain()) o.Add((Box(r), -200f, 1f));                   // under the raised cells, up to a metre (their tops stay)
        foreach (var r in v.UnderSea()) o.Add((Box(r), -200f, KitVillage.SeaWalkTop));  // the bed and drowned shore (quays and water stairs stay)
        float h = KitVillage.BedSize / 2f;
        foreach (var n in KitNodes.Below(v, "Node3D").OfType<Node3D>().Where(n => n is KitPiece kp && kp.Piece.StartsWith("SM_VK_Crop_", StringComparison.Ordinal)))
        {
            var t = Rel(v, n);
            o.Add((new[] { new Vector3(-h, 0, -h), new Vector3(h, 0, -h), new Vector3(h, 0, h), new Vector3(-h, 0, h) }.Select(c => t * c).ToArray(), -200f, 400f));
        }
        return o;
    }

    static Transform3D Rel(Node root, Node3D n)
    {
        var t = Transform3D.Identity;
        for (Node c = n; c != null && c != root; c = c.GetParent()) if (c is Node3D c3) t = c3.Transform * t;
        return t;
    }

    /// <summary>the village's navmesh (0.1 m cells, the kit's walker): its solid colliders (doors that open and
    /// breakables broken; `shut`: them whole), nothing beyond its walls; the village must be in the tree</summary>
    public static NavigationMesh Bake(KitVillage v, bool shut = false) =>
        KitNavMesh.Bake(v, 0.1f, NotWalkable(v), shut ? KitPiece.Solid | KitPiece.Passable : KitPiece.Solid);

    /// <summary>
    /// A navmesh over the map from its own colliders: from the start spawn, every spawn, marker and encounter point on the
    /// ground reachable (on its island), and no point in the forest just beyond the clearing's wall. A marker in a cage
    /// is a prisoner, shut in by design; an encounter point lifted off the ground (archers on a walkway) is out of reach
    /// by design. `repair`: an encounter point not reached moves to the nearest spot within 3 m on the reached ground,
    /// with a line naming it (move the layout's point too). Breakables (doors that open, a goblin gate) count as broken;
    /// then a navmesh with them whole lists what they shut off. -> a report; its first line "ok" when all is well.
    /// </summary>
    public static string WalkVillage(KitVillage v, string start = "arrival", bool repair = false)
    {
        var lines = new List<string>();
        int bad = 0;
        var nm = Bake(v);
        var map = KitWalkTest.Join(nm);
        var toV = v.GlobalTransform.AffineInverse();
        Vector3 Here(Node3D n) => toV * n.GlobalPosition;
        var spawns = KitNodes.Below(v.GetParent() ?? v, "").OfType<KitSpawn>().ToList();
        var from = spawns.FirstOrDefault(s => s.SpawnId == start) ?? spawns.FirstOrDefault();
        if (from == null) return "1 problems: no spawn to start from";
        int home = map.At(Here(from), 1.2f, 1.2f);
        if (home < 0) return $"1 problems: the start spawn {from.SpawnId} is off the navmesh";
        bool Reach(Vector3 p) => map.At(p, 1.2f, 1.2f) == home;
        var checks = new List<(string id, Vector3 p)>();
        foreach (var s in spawns)
        {
            checks.Add(($"spawn {s.SpawnId}", Here(s)));
            if (!Reach(Here(s))) { bad++; lines.Add($"spawn {s.SpawnId} not reached"); }
        }
        var cages = KitNodes.Below(v, "").OfType<KitPiece>().Where(k => k.Name.ToString().Contains("Cage"))
            .SelectMany(k => KitNodes.Below(k, "MeshInstance3D").OfType<MeshInstance3D>()).Select(mi => Rel(v, mi) * mi.GetAabb()).ToList();
        bool Caged(Vector3 p) => cages.Any(b => p.X >= b.Position.X && p.X <= b.End.X && p.Z >= b.Position.Z && p.Z <= b.End.Z && p.Y > b.Position.Y - 1f && p.Y < b.End.Y);
        int markers = 0, caged = 0;
        foreach (var m in KitNodes.Below(v, "").OfType<KitMarker>().Where(m => m is not KitSpawn))
        {
            markers++;
            if (Reach(Here(m))) { checks.Add((m.Name, Here(m))); continue; }
            if (Caged(Here(m))) { caged++; continue; }           // a prisoner, shut in
            bad++; lines.Add($"{m.Name} not reached");
        }
        // encounters' spawn points on the ground (the ones lifted off it, archers on a walkway or up a tower, are out of
        // reach by design)
        int encPts = 0, moved = 0;
        foreach (var e in KitNodes.Below(v, "").OfType<KitEncounter>())
            foreach (var sp in KitNodes.Children(e).OfType<Node3D>())
            {
                var p = Here(sp);
                if (p.Y - v.Height(new UnityMath.Vector2(p.X, -p.Z)) > 0.5f) continue;
                encPts++;
                string id = $"{e.EncounterId}/{sp.Name}";
                if (!Reach(p))
                {
                    var was = Plan(p);
                    Vector3? to = null;
                    for (float r = 0.25f; repair && to == null && r < 3.01f; r += 0.25f)
                    {
                        int n = Mathf.CeilToInt(2f * Mathf.Pi * r / 0.25f);
                        for (int k = 0; k < n && to == null; k++)
                        {
                            float a = 2f * Mathf.Pi * k / n;
                            var q = p + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r;
                            q.Y = v.Height(new UnityMath.Vector2(q.X, -q.Z));
                            if (map.At(q, 0.05f, 0.5f) == home && map.At(q + new Vector3(0.5f, 0, 0), 0.05f, 0.5f) == home && map.At(q - new Vector3(0.5f, 0, 0), 0.05f, 0.5f) == home
                                && map.At(q + new Vector3(0, 0, 0.5f), 0.05f, 0.5f) == home && map.At(q - new Vector3(0, 0, 0.5f), 0.05f, 0.5f) == home) to = q;
                        }
                    }
                    if (to is { } t)
                    {
                        sp.Position = sp.Transform.Origin + (v.GlobalTransform * t - sp.GlobalPosition);
                        var now = Plan(t);
                        moved++; lines.Add($"{id} at ({was.X:0.#}, {was.Y:0.#}) not reached: moved {(now - was).Length():0.0} m to ({now.X:0.#}, {now.Y:0.#}) -- move it in the layout too");
                    }
                    else { bad++; lines.Add($"{id} at ({was.X:0.#}, {was.Y:0.#}) not reached"); }
                }
                checks.Add((id, Here(sp)));
            }
        int probes = 0;
        foreach (var q in v.ForestProbes())
        {
            var p = KitVillage.Local(q.x, q.y, v.Height(q));
            probes++;
            if (map.At(p, 0.5f, 1f) == home) { bad++; lines.Add($"the forest leaks at ({q.x:0.#}, {q.y:0.#})"); }
        }
        var breakables = KitNodes.Below(v, "").OfType<KitPiece>().Where(p => p.Flag("vki_breakable")).ToList();
        lines.Insert(0, (bad == 0 ? "ok" : $"{bad} problems") + $": {spawns.Count} spawns, {markers} markers{(caged > 0 ? $" ({caged} in a cage)" : "")}, " +
                        $"{encPts} encounter points{(moved > 0 ? $" ({moved} moved)" : "")}, {probes} forest probes" +
                        (breakables.Count > 0 ? $", {breakables.Count} breakable" : "") + $"; navmesh {map.Count} islands");
        if (breakables.Count > 0)
        {
            // the breakables whole: what they shut off from the start
            var open = checks.Where(c => Reach(c.p)).ToList();
            var whole = KitWalkTest.Join(Bake(v, shut: true));
            int home2 = whole.At(Here(from), 1.2f, 1.2f);
            var cut = open.Where(c => whole.At(c.p, 1.2f, 1.2f) != home2).Select(c => c.id).ToList();
            lines.Add(cut.Count > 0 ? $"behind the breakables ({string.Join(", ", breakables.Select(b => b.Name))}): {cut.Count} of {open.Count} -- {string.Join(", ", cut)}"
                                    : $"the breakables ({string.Join(", ", breakables.Select(b => b.Name))}) shut nothing off: there is a way round");
        }
        if (bad > 0) GD.PushWarning($"{v.Name} walk test: {string.Join("\n", lines)}");
        return string.Join("\n", lines);
    }

    static string Read(string path) =>
        path.StartsWith("res://") || path.StartsWith("user://") ? FileAccess.GetFileAsString(path) : System.IO.File.ReadAllText(path);

    /// <summary>saves a built resource beside the scene and makes the scene refer to the file</summary>
    static void SaveBeside(Resource r, string path, List<string> report)
    {
        if (r == null) return;
        var err = ResourceSaver.Save(r, path);
        if (err == Error.Ok) r.TakeOverPath(path); else report.Add($"saving {path}: {err}");
    }

    /// <summary>builds the layout at `layoutPath` (a res:// or file path) into the scene `scenePath` (res://, made or
    /// replaced), under `host` (in the tree, for the bake); returns the report: read every line</summary>
    public static string BuildVillage(Node host, string layoutPath, string scenePath)
    {
        string text = Read(layoutPath);
        var L = KitJson.ParseObject(text);
        string mapName = L["name"].S() ?? scenePath.GetFile().GetBaseName();
        string folder = $"{scenePath.GetBaseDir()}/{mapName}_Ground";
        DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath(folder));
        var report = new List<string>();
        var root = new KitLevel { Name = mapName, LevelName = mapName };
        host.AddChild(root);
        try
        {
            string lit = KitPaths.LayoutScenes + "VK_ValleyTown.tscn";
            if (ResourceLoader.Exists(lit))
            {
                var lv = GD.Load<PackedScene>(lit).Instantiate();
                foreach (var n in KitNodes.Below(lv, "").Where(n => n is DirectionalLight3D || n is WorldEnvironment))
                {
                    var c = n.Duplicate();
                    if (n is Node3D n3 && c is Node3D c3) c3.Transform = Rel(lv, n3);
                    root.AddChild(c);
                    c.Owner = root;
                }
                lv.Free();
            }
            var v = new KitVillage { Name = "Village", layout = text };
            root.AddChild(v);
            v.Owner = root;
            // the terrain material: the layout's "ground" (a kit material's name or a res:// path -- a map of its own
            // colours: a burnt land's scorched grass and ash), else the kit's
            string groundName = L["ground"].S();
            if (!string.IsNullOrEmpty(groundName))
            {
                string gp = groundName.StartsWith("res://") ? groundName : KitPaths.Materials + (groundName.EndsWith(".mat") ? groundName.GetFile().GetBaseName() : groundName) + ".tres";
                v.groundMaterial = ResourceLoader.Exists(gp) ? GD.Load<Material>(gp) : null;
                if (v.groundMaterial == null) report.Add($"no ground material {groundName}: the kit's terrain instead");
            }
            v.Build();
            SaveBeside(v.GroundMesh, $"{folder}/{mapName}_Ground.res", report);
            SaveBeside(v.TerrainMesh, $"{folder}/{mapName}_Terrain.res", report);
            SaveBeside(v.SeaMesh, $"{folder}/{mapName}_Sea.res", report);
            SaveBeside(v.SeaMaskMesh, $"{folder}/{mapName}_SeaMask.res", report);
            SaveBeside(v.ControlMap, $"{folder}/{mapName}_GroundControl.res", report);
            SaveBeside(v.GroundMaterialInstance, $"{folder}/{mapName}_Ground.tres", report);
            SaveBeside(v.GrassMaterialInstance, $"{folder}/{mapName}_Grass.tres", report);
            // a camera at the arrival, at the game's angle
            var arrival = KitNodes.Below(v, "").OfType<KitSpawn>().FirstOrDefault(s => s.SpawnId == (L["start"].S() ?? "arrival"))
                          ?? KitNodes.Below(v, "").OfType<KitSpawn>().FirstOrDefault();
            var at = arrival != null ? arrival.GlobalPosition : v.GlobalPosition;
            var cam = new Camera3D { Name = "Camera", Fov = 30f, Far = 400f };
            root.AddChild(cam);
            cam.Owner = root;
            cam.GlobalTransform = new Transform3D(Basis.FromEuler(new Vector3(Mathf.DegToRad(-50f), 0f, 0f)), at + new Vector3(0f, 26f, 22f));
            // the walk test first: an encounter point it finds cut off moves onto the ground before the bake
            report.Add("walk test: " + WalkVillage(v, L["start"].S() ?? "arrival", repair: true));
            var nm = Bake(v);
            SaveBeside(nm, $"{folder}/{mapName}_nav.res", report);
            var nav = new KitNavMesh { Name = "KitNavMesh", NavigationMesh = nm };
            v.AddChild(nav);
            nav.Owner = root;
            var packed = new PackedScene();
            var err = packed.Pack(root);
            if (err == Error.Ok) err = ResourceSaver.Save(packed, scenePath);
            report.Add($"{scenePath}: {(err == Error.Ok ? "saved" : $"not saved ({err})")}, {KitNodes.Below(v, "MeshInstance3D").Count} meshes, " +
                       $"{KitNodes.Below(v, "CollisionShape3D").Count} collision shapes");
            report.AddRange(v.notes.Distinct());
        }
        finally
        {
            host.RemoveChild(root);
            root.Free();
        }
        return string.Join("\n", report);
    }
}
#endif
