using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>Bridges over chasms and channels (pieces with vki_bridge deck rects: the rope bridge, the dwarf and sewer
/// bridges, stepping stones). The chasm and channel tiles (vki_class "ground") carry 1 m blocking boxes so nobody walks
/// into them; Blender's walk check treats them as soft under a deck. Here: every deck gets a walkable box at floor
/// level, and the ground tiles' blocking boxes are cut round the deck (the box is disabled and what is left of it
/// outside the decks goes on a "KitDeckCuts" body under the root, so the chasm edge beside the bridge still stops a
/// walker). Run once after a level or room is built, before it is saved (the level builder does); the root need not be
/// in the tree. `owner` owns the new nodes (the scene root being packed); pieces whose boxes change are marked editable
/// instances of it. Returns the boxes cut. Unity: KitDecks.Apply.</summary>
public static class KitDecks
{
    const string CutName = "KitDeckCuts";

    public static int Apply(Node3D root, Node owner = null)
    {
        owner ??= root;
        root.GetNodeOrNull(CutName)?.Free();
        var decks = new List<Rect2>();                       // in root space, x / z
        var pieces = root.FindChildren("*", "", true, false).OfType<KitPiece>().ToList();
        foreach (var kp in pieces)
        {
            string js = kp.Get("vki_bridge");
            if (string.IsNullOrEmpty(js)) continue;
            foreach (var d in ParseRects(js))
            {
                // Blender local (x0, y0, x1, y1) -> Godot local: x -> x, y -> -z; a walkable slab, top at floor level
                var center = new Vector3((d[0] + d[2]) / 2f, -0.05f, -(d[1] + d[3]) / 2f);
                var size = new Vector3(Mathf.Abs(d[2] - d[0]), 0.1f, Mathf.Abs(d[3] - d[1]));
                var body = Body(kp, owner);
                var cs = new CollisionShape3D { Name = "Deck", Shape = new BoxShape3D { Size = size }, Position = center };
                body.AddChild(cs);
                cs.Owner = owner;
                decks.Add(RootRect(root, cs, size, out _, out _));
            }
        }
        if (decks.Count == 0) return 0;
        StaticBody3D cuts = null;
        int n = 0;
        foreach (var kp in pieces)
        {
            if (kp.Get("vki_class") != "ground") continue;
            if (kp.GetNodeOrNull<StaticBody3D>("Collision") is not { } body) continue;
            foreach (var cs in body.GetChildren().OfType<CollisionShape3D>())
            {
                if (cs.Disabled || cs.Shape is not BoxShape3D box) continue;
                if (cs.Position.Y + box.Size.Y / 2f <= 0.01f) continue;     // the tile's own floor slabs: walked on, not cut
                var r = RootRect(root, cs, box.Size, out float y0, out float y1);
                var hit = decks.Where(d => d.Intersects(r)).ToList();
                if (hit.Count == 0) continue;
                var left = new List<Rect2> { r };
                foreach (var d in hit) left = left.SelectMany(p => Subtract(p, d)).ToList();
                cs.Disabled = true;
                MarkEditable(kp, owner);
                if (cuts == null)
                {
                    cuts = new StaticBody3D { Name = CutName, CollisionLayer = KitPiece.Solid };
                    root.AddChild(cuts);
                    cuts.Owner = owner;
                }
                foreach (var p in left.Where(p => p.Size.X > 1e-3f && p.Size.Y > 1e-3f))
                {
                    var c = new CollisionShape3D
                    {
                        Shape = new BoxShape3D { Size = new Vector3(p.Size.X, y1 - y0, p.Size.Y) },
                        Position = new Vector3(p.GetCenter().X, (y0 + y1) / 2f, p.GetCenter().Y),
                    };
                    cuts.AddChild(c);
                    c.Owner = owner;
                }
                n++;
            }
        }
        return n;
    }

    static StaticBody3D Body(KitPiece kp, Node owner)
    {
        if (kp.GetNodeOrNull<StaticBody3D>("Collision") is { } b) return b;
        b = new StaticBody3D { Name = "Collision", CollisionLayer = KitPiece.Solid };
        kp.AddChild(b);
        b.Owner = owner;
        return b;
    }

    /// <summary>a change below an instanced piece is saved only if the instance is editable in the packed scene</summary>
    static void MarkEditable(KitPiece kp, Node owner)
    {
        if (kp != owner && !string.IsNullOrEmpty(kp.SceneFilePath)) owner.SetEditableInstance(kp, true);
    }

    static List<float[]> ParseRects(string js)
    {
        var o = new List<float[]>();
        var nums = js.Replace("[", " ").Replace("]", " ").Split(new[] { ',', ' ' }, System.StringSplitOptions.RemoveEmptyEntries)
                     .Select(s => float.Parse(s, CultureInfo.InvariantCulture)).ToArray();
        for (int i = 0; i + 3 < nums.Length; i += 4) o.Add(new[] { nums[i], nums[i + 1], nums[i + 2], nums[i + 3] });
        return o;
    }

    /// <summary>n's transform relative to root, by its parents (works outside the tree)</summary>
    public static Transform3D RelativeTo(Node3D n, Node root)
    {
        var t = n.Transform;
        for (var p = n.GetParent(); p != null && p != root; p = p.GetParent())
            if (p is Node3D p3) t = p3.Transform * t;
        return t;
    }

    /// <summary>a box (size, centred on shape node cs) as an x / z rect in root space (turns of 90 degrees)</summary>
    static Rect2 RootRect(Node3D root, Node3D cs, Vector3 size, out float y0, out float y1)
    {
        var t = RelativeTo(cs, root);
        var h = size / 2f;
        var pts = new List<Vector3>();
        foreach (var sx in new[] { -1f, 1f }) foreach (var sy in new[] { -1f, 1f }) foreach (var sz in new[] { -1f, 1f })
            pts.Add(t * (h * new Vector3(sx, sy, sz)));
        y0 = pts.Min(p => p.Y); y1 = pts.Max(p => p.Y);
        float x0 = pts.Min(p => p.X), x1 = pts.Max(p => p.X), z0 = pts.Min(p => p.Z), z1 = pts.Max(p => p.Z);
        return new Rect2(x0, z0, x1 - x0, z1 - z0);
    }

    /// <summary>a - b as up to four rects</summary>
    static IEnumerable<Rect2> Subtract(Rect2 a, Rect2 b)
    {
        if (!a.Intersects(b)) { yield return a; yield break; }
        float ax0 = a.Position.X, ax1 = a.End.X, ay0 = a.Position.Y, ay1 = a.End.Y;
        float bx0 = b.Position.X, bx1 = b.End.X, by0 = b.Position.Y, by1 = b.End.Y;
        static Rect2 MinMax(float x0, float y0, float x1, float y1) => new(x0, y0, x1 - x0, y1 - y0);
        float ix0 = Mathf.Max(ax0, bx0), ix1 = Mathf.Min(ax1, bx1);
        if (by0 > ay0) yield return MinMax(ax0, ay0, ax1, by0);       // below the deck
        if (by1 < ay1) yield return MinMax(ax0, by1, ax1, ay1);       // above
        float ry0 = Mathf.Max(ay0, by0), ry1 = Mathf.Min(ay1, by1);
        if (ix0 > ax0) yield return MinMax(ax0, ry0, ix0, ry1);       // left of it
        if (ix1 < ax1) yield return MinMax(ix1, ry0, ax1, ry1);       // right of it
    }
}
