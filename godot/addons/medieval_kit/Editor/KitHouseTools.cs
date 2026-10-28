#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Nodes;
using Godot;

namespace MedievalKit.Editor;

/// <summary>House generator tooling: a set of random houses saved as scenes with a showcase, and a dump to diff against
/// the Unity kit's houses for the same seeds. kit_cli: houses [count] [first seed]; rooms housedump. Unity:
/// KitHouseTools.</summary>
public static class KitHouseTools
{
    public const string OutFolder = "res://kit_houses";

    static string NameOf(KitHouseGenerator g) => g.shape == KitHouseGenerator.Shape.L
        ? $"House_L{2 + g.armCells}x{2 + g.wingCells}_{g.stories}st_{g.seed}"
        : $"House_{g.cells}x2_{g.stories}st_{g.seed}";

    /// <summary>saves a generated house as a scene in res://kit_houses (kit pieces stay instanced scenes)</summary>
    public static string SaveAsScene(KitHouseGenerator g, string name = null)
    {
        DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath(OutFolder));
        string path = $"{OutFolder}/{name ?? NameOf(g)}.tscn";
        var packed = new PackedScene();
        var err = packed.Pack(g);
        if (err == Error.Ok) err = ResourceSaver.Save(packed, path);
        return err == Error.Ok ? path : $"(failed: {err})";
    }

    /// <summary>the generator for house i of a set (the Unity kit's mix): about a third L-houses, the rest 2-4 bays, a
    /// quarter of one storey</summary>
    static KitHouseGenerator Make(System.Random rnd, int seed0, int i)
    {
        var g = new KitHouseGenerator { Name = "House" };
        if (rnd.NextDouble() < 0.33)
        {
            g.shape = KitHouseGenerator.Shape.L;      // about a third are L-houses (build_L_v)
            g.armCells = 1 + rnd.Next(2); g.wingCells = 1 + rnd.Next(2);
        }
        else g.cells = 2 + rnd.Next(3);              // 2-4 bays, as the valley's infill houses
        g.stories = rnd.NextDouble() < 0.25 ? 1 : 2;
        g.seed = seed0 + i * 37;
        return g;
    }

    /// <summary>a set of random houses as scenes plus res://kit_houses/HouseShowcase.tscn laying them out in rows, lit
    /// like the pilot (the kit's house diorama)</summary>
    public static string GenerateHouseSet(Node host, int count, int seed0)
    {
        var rules = KitHouseRules.Default;
        rules.Load();
        var rnd = new System.Random(seed0);
        var show = new Node3D { Name = "HouseShowcase" };
        host.AddChild(show);
        var paths = new List<string>();
        try
        {
            float x = 0, z = 0, rowDepth = 0;
            for (int i = 0; i < count; i++)
            {
                var g = Make(rnd, seed0, i);
                host.AddChild(g);
                g.Generate();
                paths.Add(SaveAsScene(g));
                host.RemoveChild(g);
                g.Free();
                bool isL = g.shape == KitHouseGenerator.Shape.L;
                float w = (isL ? (2 + g.armCells) : g.cells) * rules.cell + 4f;
                if (x + w > 48f) { x = 0; z += rowDepth; rowDepth = 0; }
                // an L-house's pivot is its corner block: shift it so the footprint sits centred in its slot
                var inst = GD.Load<PackedScene>(paths[^1]).Instantiate<Node3D>();
                inst.Position = new Vector3(x + w / 2 - (isL ? 0.5f * rules.cell * g.armCells : 0f), 0, z);
                show.AddChild(inst, true);
                inst.Owner = show;
                x += w; rowDepth = Mathf.Max(rowDepth, (isL ? rules.cell * (2 + g.wingCells) : rules.depth) + 7f);
            }
            string lit = KitPaths.LayoutScenes + "Pilot.tscn";
            if (ResourceLoader.Exists(lit))
            {
                var lv = GD.Load<PackedScene>(lit).Instantiate();
                foreach (var n in KitNodes.Below(lv, "").Where(n => n is DirectionalLight3D || n is WorldEnvironment))
                {
                    var c = n.Duplicate();
                    if (n is Node3D n3 && c is Node3D c3) c3.Transform = Placed(lv, n3);       // the level is not in the tree
                    show.AddChild(c);
                    c.Owner = show;
                }
                lv.Free();
            }
            var ground = new MeshInstance3D { Name = "Ground", Mesh = new PlaneMesh { Size = new Vector2(70, z + rowDepth + 24) }, Position = new Vector3(24, -0.01f, (z + rowDepth) / 2 - 6) };
            show.AddChild(ground);
            ground.Owner = show;
            var packed = new PackedScene();
            packed.Pack(show);
            ResourceSaver.Save(packed, $"{OutFolder}/HouseShowcase.tscn");
        }
        finally { host.RemoveChild(show); show.Free(); }
        int missing = rules.missing.Count;
        return $"houses: {paths.Count} -> {OutFolder} (showcase HouseShowcase.tscn)" + (missing > 0 ? $"; rules name {missing} pieces the kit lacks: {string.Join(", ", rules.missing.Take(8))}" : "");
    }

    /// <summary>the houses of a set (count, first seed 1000) as JSON lines: each piece's scene name and place in
    /// Blender house space, for tools/rooms_parity.py --houses against the Unity kit's</summary>
    public static string Dump(Node host, int count, string outPath)
    {
        var rnd = new System.Random(1000);
        var sb = new StringBuilder();
        for (int i = 0; i < count; i++)
        {
            var g = Make(rnd, 1000, i);
            host.AddChild(g);
            g.Generate();
            var placed = new JsonArray();
            foreach (var n in KitNodes.Children(g).OfType<Node3D>())
            {
                string piece = (n as KitPiece)?.Piece ?? n.SceneFilePath.GetFile().GetBaseName();
                placed.Add(KitJson.A(piece, Math.Round(n.Position.X, 3), Math.Round(-n.Position.Z, 3), Math.Round(n.Position.Y, 3), Math.Round(Mathf.RadToDeg(n.Rotation.Y), 1)));
            }
            var style = new JsonObject();
            foreach (var kv in g.LastStyle.OrderBy(k => k.Key, StringComparer.Ordinal)) style[kv.Key] = kv.Value;
            sb.Append(KitJson.Text(new JsonObject { ["label"] = $"house {g.shape} {g.cells} {g.armCells}x{g.wingCells} {g.stories}st", ["seed"] = g.seed, ["style"] = style, ["placed"] = placed }, false)).Append('\n');
            host.RemoveChild(g);
            g.Free();
        }
        using (var f = FileAccess.Open(outPath, FileAccess.ModeFlags.Write)) f.StoreString(sb.ToString());
        return $"housedump: {count} houses -> {outPath}";
    }

    /// <summary>a node's transform in the space of `root` above it (outside the tree, where GlobalTransform is not known)</summary>
    static Transform3D Placed(Node root, Node3D n)
    {
        var t = Transform3D.Identity;
        for (Node c = n; c != null && c != root; c = c.GetParent()) if (c is Node3D c3) t = c3.Transform * t;
        return t;
    }
}
#endif
