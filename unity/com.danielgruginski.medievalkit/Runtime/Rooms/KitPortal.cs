using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A way from one generated map into the next: an opening on one of the map's edges where the floor runs on into the
    /// neighbouring map (a connector), so the world continues without a cut. Maps are never turned, so a north portal
    /// meets the next piece's south one. At the seam the opening's cells are open and the `Margin` cells either side of
    /// it are cut rock, in both maps; the big map builds the rock tiles on the seam line, a connector ("seam": true)
    /// leaves them to it. Record: R["portals"] = [{id, side, at, width, target, seam}].
    /// </summary>
    [Serializable]
    public class KitPortal
    {
        /// <summary>cells of cut rock either side of an opening at a seam (the band both maps agree on)</summary>
        public const int Margin = 2;
        /// <summary>cells the way runs straight in from the edge before it may turn</summary>
        public const int Approach = 3;

        public string id = "north";
        [Tooltip("The edge it opens on: N, S, E or W (north reads best from the game camera, then south).")]
        public string side = "N";
        [Tooltip("The opening's first cell along the edge (its west / south end); -1: the generator picks.")]
        public int at = -1;
        [Tooltip("The opening's width in cells (2: the narrowest the rock tiles leave walkable).")]
        public int width = 2;
        [Tooltip("The map beyond, for the chain.")]
        public string target;
        [Tooltip("A connector's end: the map on the other side builds the seam's rock tiles.")]
        public bool seam;

        public char Side => string.IsNullOrEmpty(side) ? 'N' : char.ToUpperInvariant(side[0]);

        public JObject ToJson() => new JObject
        {
            ["id"] = id, ["side"] = Side.ToString(), ["at"] = at, ["width"] = width, ["target"] = target, ["seam"] = seam,
        };

        public static KitPortal FromJson(JToken t) => new KitPortal
        {
            id = (string)t["id"] ?? "portal", side = (string)t["side"] ?? "N", at = (int?)t["at"] ?? -1,
            width = Mathf.Max(1, (int?)t["width"] ?? 2), target = (string)t["target"], seam = (bool?)t["seam"] ?? false,
        };

        public static List<KitPortal> Of(JObject record) =>
            record?["portals"] is JArray a ? a.Select(FromJson).ToList() : new List<KitPortal>();

        public static (int, int) Outward(char s) => s == 'N' ? (0, 1) : s == 'S' ? (0, -1) : s == 'E' ? (1, 0) : (-1, 0);
        public static char Opposite(char s) => s == 'N' ? 'S' : s == 'S' ? 'N' : s == 'E' ? 'W' : 'E';
        /// <summary>the bearing (0 north, 90 east) looking into the map through the portal</summary>
        public static float Inward(char s) => s == 'N' ? 180f : s == 'S' ? 0f : s == 'E' ? 270f : 90f;
        public static int EdgeLength(char s, int nc, int nr) => s == 'N' || s == 'S' ? nc : nr;

        /// <summary>the map cell at `k` cells along the portal's edge and `d` cells in from it (d 0: the edge row)</summary>
        public (int, int) Cell(int k, int d, int nc, int nr)
        {
            char s = Side;
            return s == 'N' ? (k, nr - 1 - d) : s == 'S' ? (k, d) : s == 'E' ? (nc - 1 - d, k) : (d, k);
        }

        /// <summary>the cell just beyond the edge, `k` along it (outside the map: the neighbour's seam row)</summary>
        public (int, int) Beyond(int k, int nc, int nr) => Cell(k, -1, nc, nr);

        /// <summary>the opening's cells `d` in from the edge</summary>
        public IEnumerable<(int, int)> Row(int d, int nc, int nr) => Enumerable.Range(at, width).Select(k => Cell(k, d, nc, nr));

        /// <summary>opens the portal in a generator's cell map: picks `at` when unset (where the way in is shortest, the
        /// middle of the edge breaking ties), the opening's cells `Approach` cells straight in, then an L-shaped way as
        /// wide as the opening (in along the edge's normal first) until it meets a cell `reach` accepts.
        /// -> the cells opened; the caller adds them to its map</summary>
        public List<(int, int)> Carve(int nc, int nr, Func<(int, int), bool> reach, System.Random rnd)
        {
            char s = Side;
            int len = EdgeLength(s, nc, nr);
            width = Mathf.Clamp(width, 1, Mathf.Max(1, len - 2 * Margin));
            var targets = new List<(int, int)>();
            for (int c = 0; c < nc; c++) for (int r = 0; r < nr; r++) if (reach((c, r))) targets.Add((c, r));
            int Dist((int, int) a) => targets.Count == 0 ? 0 : targets.Min(t => Math.Abs(t.Item1 - a.Item1) + Math.Abs(t.Item2 - a.Item2));
            if (at < 0)
            {
                int lo = Margin, hi = len - width - Margin;
                at = hi < lo ? Mathf.Max(0, (len - width) / 2)
                   : Enumerable.Range(lo, hi - lo + 1).OrderBy(k => Dist(Cell(k + width / 2, Approach - 1, nc, nr)) + 0.15f * Mathf.Abs(k - (len - width) / 2f))
                                                       .ThenBy(_ => rnd.Next()).First();
            }
            var cells = new List<(int, int)>();
            for (int d = 0; d < Approach; d++) cells.AddRange(Row(d, nc, nr));
            if (targets.Count == 0 || cells.Any(reach)) return cells;
            // the way on: a square brush as wide as the opening, its corner walked from the approach's end to the nearest target
            int w = width;
            (int, int) Clamp((int, int) a) => (Mathf.Clamp(a.Item1, 1, Mathf.Max(1, nc - w - 1)), Mathf.Clamp(a.Item2, 1, Mathf.Max(1, nr - w - 1)));
            var cur = s == 'N' ? (at, nr - Approach - (w - 1)) : s == 'S' ? (at, Approach - 1) : s == 'E' ? (nc - Approach - (w - 1), at) : (Approach - 1, at);
            var end = cells.Skip(cells.Count - w).First();
            var goal = Clamp(targets.OrderBy(t => Math.Abs(t.Item1 - end.Item1) + Math.Abs(t.Item2 - end.Item2)).First());
            bool Brush((int, int) a)
            {
                bool hit = false;
                for (int i = 0; i < w; i++)
                    for (int j = 0; j < w; j++)
                    {
                        var q = (a.Item1 + i, a.Item2 + j);
                        if (q.Item1 < 0 || q.Item1 >= nc || q.Item2 < 0 || q.Item2 >= nr) continue;
                        if (reach(q)) hit = true;
                        if (!cells.Contains(q)) cells.Add(q);
                    }
                return hit;
            }
            bool yFirst = s == 'N' || s == 'S';
            for (int step = 0; step < 4 * (nc + nr); step++)
            {
                if (Brush(cur) || cur == goal) break;
                bool moveY = yFirst ? cur.Item2 != goal.Item2 : cur.Item1 == goal.Item1;
                cur = moveY ? (cur.Item1, cur.Item2 + Math.Sign(goal.Item2 - cur.Item2)) : (cur.Item1 + Math.Sign(goal.Item1 - cur.Item1), cur.Item2);
            }
            return cells;
        }

        /// <summary>the middle of the opening on the seam line, in the map's Blender space (x east, y north)</summary>
        public Vector2 SeamPoint(int nc, int nr, float ig = 1.5f)
        {
            float mid = ig * (at + width / 2f);
            char s = Side;
            return s == 'N' ? new Vector2(mid, ig * nr) : s == 'S' ? new Vector2(mid, 0f) : s == 'E' ? new Vector2(ig * nc, mid) : new Vector2(0f, mid);
        }
    }
}
