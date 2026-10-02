using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Bridges over chasms and channels (pieces with vki_bridge deck rects: the rope bridge, the dwarf and sewer bridges,
    /// stepping stones). The chasm and channel tiles (vki_class "ground") carry 1 m blocking boxes so nobody walks into
    /// them; Blender's walk check treats them as soft under a deck. Here: every deck gets a walkable box at floor level,
    /// and the ground tiles' blocking boxes are cut round the deck (the rest of each box stays, so the chasm edge beside
    /// the bridge still stops a walker). Run once after a level or room is built (KitRoom and the level builder do).
    /// </summary>
    public static class KitDecks
    {
        const string CutName = "KitDeckCuts";

        public static int Apply(Transform root)
        {
            var old = root.Find(CutName);
            if (old != null) { if (Application.isPlaying) Object.Destroy(old.gameObject); else Object.DestroyImmediate(old.gameObject); }
            var decks = new List<Rect>();                       // in root space, x / z
            foreach (var kp in root.GetComponentsInChildren<KitPiece>())
            {
                string js = kp.Get("vki_bridge");
                if (string.IsNullOrEmpty(js)) continue;
                foreach (var d in ParseRects(js))
                {
                    // Blender local (x0, y0, x1, y1) -> Unity local: x -> -x, y -> -z; a walkable slab, top at floor level
                    var deck = kp.gameObject.AddComponent<BoxCollider>();
                    deck.center = new Vector3(-(d[0] + d[2]) / 2f, -0.05f, -(d[1] + d[3]) / 2f);
                    deck.size = new Vector3(Mathf.Abs(d[2] - d[0]), 0.1f, Mathf.Abs(d[3] - d[1]));
                    decks.Add(RootRect(root, kp.transform, deck.center, deck.size, out _, out _));
                }
            }
            if (decks.Count == 0) return 0;
            Transform cuts = null;
            int n = 0;
            foreach (var kp in root.GetComponentsInChildren<KitPiece>())
            {
                if (kp.Get("vki_class") != "ground") continue;
                foreach (var bc in kp.GetComponents<BoxCollider>())
                {
                    if (!bc.enabled || bc.isTrigger) continue;
                    if (bc.center.y + bc.size.y / 2f <= 0.01f) continue;      // the tile's own floor slabs: walked on, not cut
                    var r = RootRect(root, kp.transform, bc.center, bc.size, out float y0, out float y1);
                    var hit = decks.Where(d => d.Overlaps(r)).ToList();
                    if (hit.Count == 0) continue;
                    var pieces = new List<Rect> { r };
                    foreach (var d in hit) pieces = pieces.SelectMany(p => Subtract(p, d)).ToList();
                    bc.enabled = false;
                    bc.center = Vector3.zero; bc.size = Vector3.zero;  // NavMeshBuilder collects disabled colliders too
                    if (cuts == null)
                    {
                        cuts = new GameObject(CutName).transform;
                        cuts.SetParent(root, false);
                    }
                    foreach (var p in pieces.Where(p => p.width > 1e-3f && p.height > 1e-3f))
                    {
                        var c = cuts.gameObject.AddComponent<BoxCollider>();
                        c.center = new Vector3(p.center.x, (y0 + y1) / 2f, p.center.y);
                        c.size = new Vector3(p.width, y1 - y0, p.height);
                    }
                    n++;
                }
            }
            return n;
        }

        static List<float[]> ParseRects(string js)
        {
            var o = new List<float[]>();
            var nums = js.Replace("[", " ").Replace("]", " ").Split(new[] { ',', ' ' }, System.StringSplitOptions.RemoveEmptyEntries)
                         .Select(s => float.Parse(s, CultureInfo.InvariantCulture)).ToArray();
            for (int i = 0; i + 3 < nums.Length; i += 4) o.Add(new[] { nums[i], nums[i + 1], nums[i + 2], nums[i + 3] });
            return o;
        }

        /// <summary>a box (local centre / size on transform t) as an x / z rect in root space (turns of 90 degrees)</summary>
        static Rect RootRect(Transform root, Transform t, Vector3 center, Vector3 size, out float y0, out float y1)
        {
            var h = size / 2f;
            var pts = new List<Vector3>();
            foreach (var sx in new[] { -1f, 1f }) foreach (var sy in new[] { -1f, 1f }) foreach (var sz in new[] { -1f, 1f })
                pts.Add(root.InverseTransformPoint(t.TransformPoint(center + Vector3.Scale(h, new Vector3(sx, sy, sz)))));
            y0 = pts.Min(p => p.y); y1 = pts.Max(p => p.y);
            float x0 = pts.Min(p => p.x), x1 = pts.Max(p => p.x), z0 = pts.Min(p => p.z), z1 = pts.Max(p => p.z);
            return Rect.MinMaxRect(x0, z0, x1, z1);
        }

        /// <summary>a - b as up to four rects</summary>
        static IEnumerable<Rect> Subtract(Rect a, Rect b)
        {
            if (!a.Overlaps(b)) { yield return a; yield break; }
            float ix0 = Mathf.Max(a.xMin, b.xMin), ix1 = Mathf.Min(a.xMax, b.xMax);
            if (b.yMin > a.yMin) yield return Rect.MinMaxRect(a.xMin, a.yMin, a.xMax, b.yMin);       // below the deck
            if (b.yMax < a.yMax) yield return Rect.MinMaxRect(a.xMin, b.yMax, a.xMax, a.yMax);       // above
            float ry0 = Mathf.Max(a.yMin, b.yMin), ry1 = Mathf.Min(a.yMax, b.yMax);
            if (ix0 > a.xMin) yield return Rect.MinMaxRect(a.xMin, ry0, ix0, ry1);                   // left of it
            if (ix1 < a.xMax) yield return Rect.MinMaxRect(ix1, ry0, a.xMax, ry1);                   // right of it
        }
    }
}
