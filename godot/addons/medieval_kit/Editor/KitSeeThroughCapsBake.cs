#if TOOLS
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit.Editor;

/// <summary>
/// Bakes the see-through's caps (<see cref="KitSeeThroughCapBank"/>): puts each built layout in the tree (its own
/// see-through set-up off: <see cref="KitLevel.SetUpSeeThrough"/>), asks it which caps its pieces need
/// (<see cref="KitSeeThrough.SetUpLevel"/> with <see cref="KitSeeThroughCaps.Collecting"/> set), frees it, makes each cap
/// mesh once (<see cref="KitSeeThroughCaps.MakeCap"/>) and saves them all to <see cref="KitSeeThroughCapBank.Path"/>.
/// Bake again after a re-export or a rebuild of the layouts (a stale entry is made again in play, with a stall).
/// kit_cli: bakecaps [layout ...] (default: every built layout but the catalogs). Unity: KitSeeThroughCapsBake (Tools >
/// Medieval Kit > Bake See-through Caps, and before every player build).
/// </summary>
public partial class KitSeeThroughCapsBake : RefCounted
{
    /// <summary>bake the caps of these layouts (none: every built layout but the catalogs); returns a report line</summary>
    public string Bake(string[] names)
    {
        var tree = (SceneTree)Engine.GetMainLoop();
        ulong t0 = Time.GetTicksMsec();
        IEnumerable<string> layouts = names != null && names.Length > 0 ? names : DirAccess.GetFilesAt(KitPaths.LayoutScenes).Where(f => f.EndsWith(".tscn") && !f.StartsWith("Catalog_"))
                             .Select(f => f.GetBaseName()).ToList();
        var keys = new HashSet<(Mesh mesh, string source, int q, uint solid, uint bark)>();
        int levels = 0, buildings = 0;
        KitLevel.SetUpSeeThrough = false;
        try
        {
            foreach (var name in layouts)
            {
                string path = KitPaths.LayoutScenes + name + ".tscn";
                if (!ResourceLoader.Exists(path)) { GD.PushWarning($"[bakecaps] no layout {name}"); continue; }
                var level = GD.Load<PackedScene>(path).Instantiate();
                tree.Root.AddChild(level);
                KitSeeThroughCaps.Collecting = keys;
                try { buildings += KitSeeThrough.SetUpLevel(level).Count; }
                finally { KitSeeThroughCaps.Collecting = null; }
                tree.Root.RemoveChild(level);
                level.Free();
                levels++;
            }
        }
        finally { KitLevel.SetUpSeeThrough = true; }

        var bank = new KitSeeThroughCapBank();
        int made = 0, empty = 0, failed0 = KitSeeThroughCaps.Failed, tris = 0;
        var done = new HashSet<(string, int, uint, uint)>();
        foreach (var k in keys.OrderBy(k => k.source).ThenBy(k => k.q))
        {
            if (!done.Add((k.source, k.q, k.solid, k.bark))) continue;        // (one mesh named twice: once)
            var cap = KitSeeThroughCaps.MakeCap(k.mesh, k.q, k.solid, k.bark);
            var e = new KitSeeThroughCapEntry
            {
                Source = k.source, Q = k.q, Solid = k.solid, Bark = k.bark, VertexCount = KitSeeThroughCaps.VertexCount(k.mesh),
                Bounds = k.mesh.GetAabb(), Mats = cap.Mats ?? System.Array.Empty<int>(), Grain = cap.Grain ?? System.Array.Empty<bool>(), Area = cap.Area,
            };
            if (cap.Mesh != null)
            {
                cap.Mesh.ResourceName = $"{k.source.Replace('/', '_')}_q{k.q}_{k.solid:x}_Cap";
                e.Cap = cap.Mesh;
                for (int s = 0; s < cap.Mesh.GetSurfaceCount(); s++) tris += cap.Mesh.SurfaceGetArrayIndexLen(s) / 3;
                made++;
            }
            else empty++;
            bank.Entries.Add(e);
        }
        string report = $"{levels} levels ({buildings} buildings), {done.Count} caps needed: {made} cap meshes ({tris} triangles), " +
                        $"{empty} sections empty, {KitSeeThroughCaps.Failed - failed0} polygons not filled, {(Time.GetTicksMsec() - t0) / 1000.0:F1} s";
        bank.Report = $"{Time.GetDatetimeStringFromSystem()} {report}";
        var err = ResourceSaver.Save(bank, KitSeeThroughCapBank.Path, ResourceSaver.SaverFlags.Compress);
        KitSeeThroughCaps.ResetBank();
        return $"BAKECAPS {report} -> {KitSeeThroughCapBank.Path} ({err})";
    }
}
#endif
