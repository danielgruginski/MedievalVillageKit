using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// Colliders for the exterior (VK) pieces nothing else gives one: a building's own dressing (barrels by its door, a
/// trough, hay, a table and stools, its yard's fence, a bell tower beside the nave), the forest's bushes, stumps and
/// rocks, an exterior prop reused in a room; trees and stumps their trunks (in place of an interior prop's box). The
/// navmeshes are baked from colliders (KitNavMesh), so a piece without one is walked through. Soft and flat pieces
/// (plants, weeds, ivy, crops, chickens), ladders and what one walks on (piers, decks, steps) stay as they are. The
/// bodies go on layer <see cref="KitPiece.Solid"/>; `owner` owns them (the scene root being saved: null, the piece's
/// own owner). Unity: KitSolid.
/// </summary>
public static class KitSolid
{
    static readonly string[] Soft = { "Plant_", "Deco_", "Crop_", "Grass", "Flower", "Animal_Chickens", "Ladder", "Overlay_",
                                      "Pier", "Deck", "Stairs", "Steps" };

    /// <summary>the walkers step over less (KitNavMesh's AgentMaxClimb)</summary>
    const float Low = 0.35f;
    /// <summary>the grid the parts of a piece are told apart on (m, in the piece's own units)</summary>
    const float Cell = 0.25f;
    const string BodyName = "Solid";

    /// <summary>a piece one walks through (a plant, weeds, ivy, crops, chickens, an overlay), climbs (a ladder) or walks
    /// on (a pier, a deck, steps)</summary>
    public static bool IsSoft(string name) => Soft.Any(name.Contains);

    /// <summary>a solid body of its own under the piece (the import's vki_collider boxes, or one made here)</summary>
    static bool HasCollider(Node3D go) =>
        KitNodes.Children(go).OfType<StaticBody3D>().Any(b => KitNodes.Children(b).OfType<CollisionShape3D>().Any(c => !c.Disabled));

    static IEnumerable<MeshInstance3D> Meshes(Node3D go) =>
        (go is MeshInstance3D m ? new[] { m } : Enumerable.Empty<MeshInstance3D>()).Concat(KitNodes.Below(go, "MeshInstance3D").OfType<MeshInstance3D>());

    /// <summary>n's transform in go's space (n below go)</summary>
    static Transform3D RelTo(Node3D go, Node3D n)
    {
        var t = Transform3D.Identity;
        for (Node c = n; c != null && c != go; c = c.GetParent()) if (c is Node3D c3) t = c3.Transform * t;
        return t;
    }

    static StaticBody3D Body(Node3D go, Transform3D at, Node owner)
    {
        var body = new StaticBody3D { Name = BodyName, CollisionLayer = KitPiece.Solid, Transform = at };
        go.AddChild(body, true);
        body.Owner = owner ?? go.Owner ?? go;
        return body;
    }

    static void Shape(StaticBody3D body, Shape3D shape, Vector3 at, Node owner)
    {
        var cs = new CollisionShape3D { Shape = shape, Position = at };
        body.AddChild(cs, true);
        cs.Owner = owner ?? body.Owner;
    }

    /// <summary>
    /// Boxes over what one bumps into: for each mesh under go when go has no solid body yet, its faces lower than `head`
    /// metres over go's foot, gathered on a grid into the separate parts they stand as -- a signpost's post, not its arms;
    /// each post of a canopy or a gallery, not its roof or deck; a barrel, a table -- one box over each part, in the
    /// mesh's own space (it turns and scales with it), `inset` in from its sides. A hollow part (walls round a floor: a
    /// lean-to's back and sides, an L of planks) gets boxes along its walls instead, so what they stand round stays open
    /// to walk into. Faces lower than a step (a plank floor, a threshold) are walked on and part nothing; the boxes still
    /// reach down to the ground. Returns how many boxes.
    /// </summary>
    public static int Box(Node3D go, float head = 1.2f, float inset = 0.05f, Node owner = null)
    {
        int n = 0;
        if (go == null || HasCollider(go)) return 0;
        foreach (var mi in Meshes(go).ToList())
        {
            var m = mi.Mesh;
            if (m == null) continue;
            var rel = RelTo(go, mi);
            var up = go.Basis;                           // heights over go's foot, with go's own turn and scale
            var v = new List<Vector3>();
            var tri = new List<int>();
            for (int s = 0; s < m.GetSurfaceCount(); s++)
            {
                using var arrays = m.SurfaceGetArrays(s);
                var sv = arrays[(int)Mesh.ArrayType.Vertex].AsVector3Array();
                var si = arrays[(int)Mesh.ArrayType.Index].AsInt32Array();
                int b0 = v.Count;
                v.AddRange(sv);
                if (si.Length > 0) tri.AddRange(si.Select(i => i + b0));
                else tri.AddRange(Enumerable.Range(b0, sv.Length));
            }
            if (v.Count == 0) continue;
            var wy = v.Select(p => (up * (rel * p)).Y).ToArray();
            float top = head, step = Low;
            // the faces below `top`, sampled every 0.1 m: per grid cell the extent of the samples above a step, and
            // the lowest of all (where its box starts)
            var cells = new Dictionary<(int, int), (Vector3 lo, Vector3 hi)>();
            var foot = new Dictionary<(int, int), float>();
            for (int i = 0; i + 2 < tri.Count; i += 3)
            {
                int a = tri[i], b = tri[i + 1], c = tri[i + 2];
                if (Mathf.Min(wy[a], Mathf.Min(wy[b], wy[c])) >= top) continue;            // overhead
                Vector3 A = v[a], B = v[b], C = v[c];
                float edge = Mathf.Max((B - A).Length(), Mathf.Max((C - B).Length(), (A - C).Length()));
                int k = Mathf.Clamp(Mathf.CeilToInt(edge / 0.1f), 1, 40);
                for (int s = 0; s <= k; s++)
                    for (int r = 0; r <= k - s; r++)
                    {
                        var p = A + (B - A) * (s / (float)k) + (C - A) * (r / (float)k);
                        float y = wy[a] + (wy[b] - wy[a]) * (s / (float)k) + (wy[c] - wy[a]) * (r / (float)k);
                        if (y >= top) continue;
                        var key = (Mathf.FloorToInt(p.X / Cell), Mathf.FloorToInt(p.Z / Cell));
                        foot[key] = foot.TryGetValue(key, out var f) ? Mathf.Min(f, p.Y) : p.Y;
                        if (y < step) continue;                                 // walked on, not into
                        cells[key] = cells.TryGetValue(key, out var e) ? (e.lo.Min(p), e.hi.Max(p)) : (p, p);
                    }
            }
            StaticBody3D body = null;
            void AddBox(Vector3 lo, Vector3 hi)
            {
                body ??= Body(go, rel, owner);
                var size = new Vector3(Mathf.Max(0.1f, hi.X - lo.X - 2 * inset), hi.Y - lo.Y, Mathf.Max(0.1f, hi.Z - lo.Z - 2 * inset));
                Shape(body, new BoxShape3D { Size = size }, (lo + hi) / 2f, owner);
                n++;
            }
            // the parts: cells joined side by side or corner to corner
            var seen = new HashSet<(int, int)>();
            foreach (var start in cells.Keys)
            {
                if (!seen.Add(start)) continue;
                var lo = cells[start].lo; var hi = cells[start].hi;
                var todo = new Stack<(int, int)>();
                var part = new List<(int x, int z)> { start };
                todo.Push(start);
                while (todo.Count > 0)
                {
                    var (x, z) = todo.Pop();
                    for (int dx = -1; dx <= 1; dx++)
                        for (int dz = -1; dz <= 1; dz++)
                        {
                            var q = (x + dx, z + dz);
                            if (!cells.TryGetValue(q, out var e) || !seen.Add(q)) continue;
                            lo = lo.Min(e.lo); hi = hi.Max(e.hi);
                            part.Add(q);
                            todo.Push(q);
                        }
                }
                lo.Y = Mathf.Min(lo.Y, part.Min(c => foot[c]));                   // down to the ground
                int w = part.Max(c => c.x) - part.Min(c => c.x) + 1, d = part.Max(c => c.z) - part.Min(c => c.z) + 1;
                if (part.Count < 8 || part.Count >= 0.6f * w * d)                 // solid enough: one box
                {
                    AddBox(lo, hi);
                    continue;
                }
                // hollow: its cells in rectangles (along a row, then as deep as the row runs), a box over each
                var free = new HashSet<(int, int)>(part);
                foreach (var c0 in part.OrderBy(c => c.z).ThenBy(c => c.x))
                {
                    if (!free.Contains(c0)) continue;
                    int rw = 1, rd = 1;
                    while (free.Contains((c0.x + rw, c0.z))) rw++;
                    while (Enumerable.Range(0, rw).All(i => free.Contains((c0.x + i, c0.z + rd)))) rd++;
                    Vector3 rlo = Vector3.Inf, rhi = -Vector3.Inf;
                    for (int i = 0; i < rw; i++)
                        for (int j = 0; j < rd; j++)
                        {
                            var key = (c0.x + i, c0.z + j);
                            free.Remove(key);
                            rlo = rlo.Min(cells[key].lo); rhi = rhi.Max(cells[key].hi);
                            rlo.Y = Mathf.Min(rlo.Y, foot[key]);
                        }
                    AddBox(rlo, rhi);
                }
            }
        }
        return n;
    }

    /// <summary>an upright capsule round a round piece's pivot (a bush's middle, a stump's trunk), `radius` metres in its
    /// own units, as tall as the piece</summary>
    public static void Round(Node3D go, float radius, Node owner = null)
    {
        var mi = Meshes(go).FirstOrDefault();
        if (mi?.Mesh == null || HasCollider(go)) return;
        var b = mi.Mesh.GetAabb();
        if (b.Size.Y * Mathf.Abs((go.Basis * RelTo(go, mi).Basis).Scale.Y) < Low) return;
        Shape(Body(go, RelTo(go, mi), owner), new CapsuleShape3D { Radius = radius, Height = Mathf.Max(b.Size.Y, 2f * radius) },
              new Vector3(0f, b.GetCenter().Y, 0f), owner);
    }

    /// <summary>a piece of nature by its name: a bush gets a round core (60% of its spread), a tree or a stump its trunk
    /// (<see cref="Trunk"/>), a rock or a log a box; plants none</summary>
    public static void Nature(Node3D go, Node owner = null)
    {
        if (go == null || IsSoft(go.Name)) return;
        var mi = Meshes(go).FirstOrDefault();
        if (mi?.Mesh == null) return;
        var b = mi.Mesh.GetAabb();
        string name = go.Name;
        if (name.Contains("Bush")) Round(go, Mathf.Max(0.2f, 0.3f * Mathf.Min(b.Size.X, b.Size.Z)), owner);
        else if (IsTrunk(name)) Trunk(go, owner);
        else if (name.Contains("Rock") || name.Contains("Log")) Box(go, 3f, 0.1f, owner);
    }

    /// <summary>a tree or a stump (not a tree nursery's crop)</summary>
    public static bool IsTrunk(string name) => (name.Contains("Tree") || name.Contains("Stump")) && !IsSoft(name);

    /// <summary>
    /// A tree or a stump stands on its trunk, by its name: the colliders the piece brought are switched off (an interior
    /// prop's export box, its bounds: the burnt stump's over its whole root spread, a burnt tree's over its crown --
    /// taller than a walker, so the bake left walkable ground inside it; switched off, not freed: they belong to the
    /// piece's own scene), and an upright capsule round the pivot comes, in the piece's own units: a tree 0.45 m and 4 m
    /// tall (a burnt tree's trunk 0.4), a stump 0.5 (a burnt stump's 0.32: its roots, under 0.2 m, are walked over) as
    /// tall as the piece.
    /// </summary>
    public static void Trunk(Node3D go, Node owner = null)
    {
        if (go == null) return;
        foreach (var body in KitNodes.Below(go, "StaticBody3D").OfType<StaticBody3D>().ToList())
        {
            if (body.Name == BodyName) { body.GetParent().RemoveChild(body); body.QueueFree(); continue; }
            foreach (var cs in KitNodes.Children(body).OfType<CollisionShape3D>()) cs.Disabled = true;
            var own = owner ?? go.Owner;
            if (own != null && own != go) own.SetEditableInstance(go, true);
        }
        string name = go.Name;
        if (name.Contains("Tree"))
        {
            Shape(Body(go, Transform3D.Identity, owner), new CapsuleShape3D { Radius = name.Contains("BurntTree") ? 0.4f : 0.45f, Height = 4f },
                  new Vector3(0, 2f, 0), owner);
            return;
        }
        var mi = Meshes(go).FirstOrDefault();
        if (mi?.Mesh == null) return;
        var b = mi.Mesh.GetAabb();
        if (b.Size.Y * Mathf.Abs((go.Basis * RelTo(go, mi).Basis).Scale.Y) < Low) return;
        float r = name.Contains("BurntStump") ? 0.32f : 0.5f;
        Shape(Body(go, RelTo(go, mi), owner), new CapsuleShape3D { Radius = r, Height = Mathf.Max(b.Size.Y, 2f * r) },
              new Vector3(0f, b.GetCenter().Y, 0f), owner);
    }
}
