#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit.Editor;

/// <summary>Is a level playable: on its baked navmesh (KitNavMesh.Bake), can a walker get from a spawn to every spawn,
/// link and encounter point? The navmesh's polygons are joined where they share an edge; each point is put on the
/// nearest polygon within 1.5 m across and 1 m up or down (where a creature or the walker is put down), and the start is
/// the spawn whose island holds the most points. Unity: KitRoomTools.WalkTest (paths from the first spawn).</summary>
public static class KitWalkTest
{
    public const float Reach = 1.5f, Rise = 1f;

    public record Point(string Name, Vector3 At);

    public record Result(int Reached, int Total, string Start, List<string> Missed, int Islands, int Polygons)
    {
        public override string ToString() =>
            $"walk {Reached}/{Total} from {Start} ({Polygons} polygons, {Islands} islands)" +
            (Missed.Count > 0 ? $"; not reached: {string.Join(", ", Missed)}" : "");
    }

    /// <summary>the level's spawns, links (their trigger's centre at the link piece's floor) and encounter points, in
    /// root space</summary>
    public static List<Point> Points(Node3D root)
    {
        var o = new List<Point>();
        foreach (var n in root.FindChildren("*", "", true, false))
        {
            if (n is KitSpawn s) o.Add(new Point("spawn " + s.SpawnId, KitDecks.RelativeTo(s, root).Origin));
            else if (n is KitLink l && l.GetParent() is Node3D piece)
            {
                var c = l.GetChildren().OfType<CollisionShape3D>().FirstOrDefault();
                var at = KitDecks.RelativeTo(c != null ? c : l, root).Origin;
                at.Y = KitDecks.RelativeTo(piece, root).Origin.Y;
                o.Add(new Point("link " + l.LinkId, at));
            }
            else if (n is KitEncounter e)
                foreach (var pt in e.Points) o.Add(new Point($"encounter {e.EncounterId} {pt.Name}", KitDecks.RelativeTo(pt, root).Origin));
        }
        return o;
    }

    /// <summary>a navmesh's polygons joined into islands where they share an edge</summary>
    public sealed class Islands
    {
        public Vector3[] verts;
        public int[][] polys;
        public int[] island;              // polygon -> its island's id
        public int Count;

        /// <summary>the island of the polygon nearest p within `reach` across and `rise` up / down, or -1</summary>
        public int At(Vector3 p, float reach = Reach, float rise = Rise)
        {
            int pi = Nearest(p, verts, polys, reach, rise);
            return pi >= 0 ? island[pi] : -1;
        }
    }

    public static Islands Join(NavigationMesh nm)
    {
        var verts = nm.GetVertices();
        int np = nm.GetPolygonCount();
        var polys = new int[np][];
        for (int i = 0; i < np; i++) polys[i] = nm.GetPolygon(i);
        // join polygons sharing an edge (vertices keyed by position, to the millimetre)
        var parent = Enumerable.Range(0, np).ToArray();
        int Find(int a) { while (parent[a] != a) a = parent[a] = parent[parent[a]]; return a; }
        (long, long, long) Key(int vi) => ((long)Math.Round(verts[vi].X * 1000), (long)Math.Round(verts[vi].Y * 1000), (long)Math.Round(verts[vi].Z * 1000));
        var edges = new Dictionary<((long, long, long), (long, long, long)), int>();
        for (int i = 0; i < np; i++)
        {
            var p = polys[i];
            for (int k = 0; k < p.Length; k++)
            {
                var a = Key(p[k]); var b = Key(p[(k + 1) % p.Length]);
                var e = a.CompareTo(b) < 0 ? (a, b) : (b, a);
                if (edges.TryGetValue(e, out int j)) parent[Find(i)] = Find(j);
                else edges[e] = i;
            }
        }
        return new Islands
        {
            verts = verts, polys = polys, island = Enumerable.Range(0, np).Select(Find).ToArray(),
            Count = Enumerable.Range(0, np).Count(i => Find(i) == i),
        };
    }

    public static Result Run(NavigationMesh nm, List<Point> points)
    {
        var map = Join(nm);
        int np = map.polys.Length, islands = map.Count;
        var home = new int[points.Count];               // point -> its island (-1: off the navmesh)
        for (int i = 0; i < points.Count; i++) home[i] = map.At(points[i].At);
        var starts = Enumerable.Range(0, points.Count).Where(i => points[i].Name.StartsWith("spawn ") && home[i] >= 0).ToList();
        if (starts.Count == 0) return new Result(0, points.Count, "nowhere (no spawn on the navmesh)", points.Select(p => p.Name).ToList(), islands, np);
        int best = starts.OrderByDescending(s => home.Count(h => h == home[s])).First();
        var missed = Enumerable.Range(0, points.Count).Where(i => home[i] != home[best])
            .Select(i => home[i] < 0 ? points[i].Name + " (off the navmesh)" : points[i].Name).ToList();
        return new Result(points.Count - missed.Count, points.Count, points[best].Name, missed, islands, np);
    }

    /// <summary>the polygon nearest p within `reach` across and `rise` up / down, or -1</summary>
    static int Nearest(Vector3 p, Vector3[] verts, int[][] polys, float reach = Reach, float rise = Rise)
    {
        int best = -1;
        float bestD = float.MaxValue;
        for (int i = 0; i < polys.Length; i++)
        {
            var poly = polys[i];
            for (int k = 1; k + 1 < poly.Length; k++)
            {
                var q = ClosestOnTriangle(p, verts[poly[0]], verts[poly[k]], verts[poly[k + 1]]);
                var d = q - p;
                float across = new Vector2(d.X, d.Z).Length();
                if (across > reach || Mathf.Abs(d.Y) > rise) continue;
                float dist = d.Length();
                if (dist < bestD) { bestD = dist; best = i; }
            }
        }
        return best;
    }

    /// <summary>Ericson, Real-Time Collision Detection 5.1.5</summary>
    static Vector3 ClosestOnTriangle(Vector3 p, Vector3 a, Vector3 b, Vector3 c)
    {
        Vector3 ab = b - a, ac = c - a, ap = p - a;
        float d1 = ab.Dot(ap), d2 = ac.Dot(ap);
        if (d1 <= 0 && d2 <= 0) return a;
        var bp = p - b;
        float d3 = ab.Dot(bp), d4 = ac.Dot(bp);
        if (d3 >= 0 && d4 <= d3) return b;
        float vc = d1 * d4 - d3 * d2;
        if (vc <= 0 && d1 >= 0 && d3 <= 0) return a + ab * (d1 / (d1 - d3));
        var cp = p - c;
        float d5 = ab.Dot(cp), d6 = ac.Dot(cp);
        if (d6 >= 0 && d5 <= d6) return c;
        float vb = d5 * d2 - d1 * d6;
        if (vb <= 0 && d2 >= 0 && d6 <= 0) return a + ac * (d2 / (d2 - d6));
        float va = d3 * d6 - d5 * d4;
        if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) return b + (c - b) * ((d4 - d3) / (d4 - d3 + (d5 - d6)));
        float den = 1f / (va + vb + vc);
        return a + ab * (vb * den) + ac * (vc * den);
    }
}
#endif
