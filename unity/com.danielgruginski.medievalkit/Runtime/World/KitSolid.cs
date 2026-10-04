using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Colliders for the exterior (VK) pieces nothing else gives one: a building's own dressing (barrels by its door, a
    /// trough, hay, a table and stools, its yard's fence, a bell tower beside the nave), the forest's bushes, stumps and
    /// rocks, an exterior prop reused in a room. The navmeshes are baked from colliders (KitNavBake), so a piece without
    /// one is walked through. Soft and flat pieces (plants, weeds, ivy, crops, chickens), ladders and what one walks on
    /// (piers, decks, steps) stay as they are.
    /// </summary>
    public static class KitSolid
    {
        static readonly string[] Soft = { "Plant_", "Deco_", "Crop_", "Grass", "Flower", "Animal_Chickens", "Ladder", "Overlay_",
                                          "Pier", "Deck", "Stairs", "Steps" };

        /// <summary>the walkers step over less (KitNavMesh's agentClimb)</summary>
        const float Low = 0.35f;
        /// <summary>the grid the parts of a piece are told apart on (m, in the piece's own units)</summary>
        const float Cell = 0.25f;

        /// <summary>a piece one walks through (a plant, weeds, ivy, crops, chickens, an overlay), climbs (a ladder) or walks
        /// on (a pier, a deck, steps)</summary>
        public static bool IsSoft(string name) => Soft.Any(name.Contains);

        static bool HasCollider(Component c) => c.GetComponents<Collider>().Any(x => !x.isTrigger);

        /// <summary>
        /// Boxes over what one bumps into: for each mesh under go with no collider of its own, its faces lower than
        /// `head` metres over go's foot, gathered on a grid into the separate parts they stand as -- a signpost's post,
        /// not its arms; each post of a canopy or a gallery, not its roof or deck; a barrel, a table -- one box over each
        /// part, in the mesh's own space (it turns and scales with it), `inset` in from its sides. Parts lower than a step
        /// are left to walk over. Returns how many boxes.
        /// </summary>
        public static int Box(GameObject go, float head = 1.2f, float inset = 0.05f)
        {
            int n = 0;
            float top = go.transform.position.y + head;
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            {
                var m = mf.sharedMesh;
                if (m == null || HasCollider(mf)) continue;
                var t = mf.transform;
                if (!m.isReadable && !Application.isEditor)                      // a player build cannot read it: its bounds
                {
                    if (m.bounds.size.y * Mathf.Abs(t.lossyScale.y) < Low) continue;
                    var whole = mf.gameObject.AddComponent<BoxCollider>();
                    whole.center = m.bounds.center;
                    whole.size = new Vector3(Mathf.Max(0.1f, m.bounds.size.x - 2 * inset), m.bounds.size.y, Mathf.Max(0.1f, m.bounds.size.z - 2 * inset));
                    n++;
                    continue;
                }
                var v = m.vertices;
                var tri = m.triangles;
                var wy = v.Select(p => t.TransformPoint(p).y).ToArray();
                // the faces below `top`, sampled every 0.1 m: per grid cell the samples' extent
                var cells = new Dictionary<(int, int), (Vector3 lo, Vector3 hi)>();
                for (int i = 0; i < tri.Length; i += 3)
                {
                    int a = tri[i], b = tri[i + 1], c = tri[i + 2];
                    if (Mathf.Min(wy[a], wy[b], wy[c]) >= top) continue;            // overhead
                    Vector3 A = v[a], B = v[b], C = v[c];
                    float edge = Mathf.Max((B - A).magnitude, (C - B).magnitude, (A - C).magnitude);
                    int k = Mathf.Clamp(Mathf.CeilToInt(edge / 0.1f), 1, 40);
                    for (int s = 0; s <= k; s++)
                        for (int r = 0; r <= k - s; r++)
                        {
                            var p = A + (B - A) * (s / (float)k) + (C - A) * (r / (float)k);
                            float y = wy[a] + (wy[b] - wy[a]) * (s / (float)k) + (wy[c] - wy[a]) * (r / (float)k);
                            if (y >= top) continue;
                            var key = (Mathf.FloorToInt(p.x / Cell), Mathf.FloorToInt(p.z / Cell));
                            cells[key] = cells.TryGetValue(key, out var e) ? (Vector3.Min(e.lo, p), Vector3.Max(e.hi, p)) : (p, p);
                        }
                }
                // the parts: cells joined side by side or corner to corner
                var seen = new HashSet<(int, int)>();
                foreach (var start in cells.Keys)
                {
                    if (!seen.Add(start)) continue;
                    var lo = cells[start].lo; var hi = cells[start].hi;
                    var todo = new Stack<(int, int)>();
                    todo.Push(start);
                    while (todo.Count > 0)
                    {
                        var (x, z) = todo.Pop();
                        for (int dx = -1; dx <= 1; dx++)
                            for (int dz = -1; dz <= 1; dz++)
                            {
                                var q = (x + dx, z + dz);
                                if (!cells.TryGetValue(q, out var e) || !seen.Add(q)) continue;
                                lo = Vector3.Min(lo, e.lo); hi = Vector3.Max(hi, e.hi);
                                todo.Push(q);
                            }
                    }
                    if ((hi.y - lo.y) * Mathf.Abs(t.lossyScale.y) < Low) continue;     // stepped over
                    var box = mf.gameObject.AddComponent<BoxCollider>();
                    box.center = (lo + hi) / 2f;
                    box.size = new Vector3(Mathf.Max(0.1f, hi.x - lo.x - 2 * inset), hi.y - lo.y, Mathf.Max(0.1f, hi.z - lo.z - 2 * inset));
                    n++;
                }
            }
            return n;
        }

        /// <summary>an upright capsule round a round piece's pivot (a bush's middle, a stump's trunk), `radius` metres in its
        /// own units, as tall as the piece</summary>
        public static void Round(GameObject go, float radius)
        {
            var mf = go.GetComponentInChildren<MeshFilter>();
            if (mf == null || mf.sharedMesh == null || HasCollider(mf)) return;
            var b = mf.sharedMesh.bounds;
            if (b.size.y * Mathf.Abs(mf.transform.lossyScale.y) < Low) return;
            var c = mf.gameObject.AddComponent<CapsuleCollider>();
            c.direction = 1;
            c.center = new Vector3(0f, b.center.y, 0f);
            c.radius = radius;
            c.height = Mathf.Max(b.size.y, 2f * radius);
        }

        /// <summary>a piece of nature by its name: a bush gets a round core (60% of its spread), a stump its trunk, a rock or
        /// a log a box; plants none</summary>
        public static void Nature(GameObject go)
        {
            if (go == null || IsSoft(go.name)) return;
            var mf = go.GetComponentInChildren<MeshFilter>();
            if (mf == null || mf.sharedMesh == null) return;
            var b = mf.sharedMesh.bounds;
            if (go.name.Contains("Bush")) Round(go, Mathf.Max(0.2f, 0.3f * Mathf.Min(b.size.x, b.size.z)));
            else if (go.name.Contains("Stump")) Round(go, 0.5f);
            else if (go.name.Contains("Rock") || go.name.Contains("Log")) Box(go, 3f, 0.1f);
        }
    }
}
