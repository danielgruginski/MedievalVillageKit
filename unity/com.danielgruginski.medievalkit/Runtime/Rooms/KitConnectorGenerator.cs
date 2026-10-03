using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A connector for a chain of generated maps (<see cref="KitPortal"/>): a short passage in bare rock from an opening
    /// on one edge to an opening on another, both seams (the maps either side build the rock tiles on the seam lines and
    /// the floor runs on into them). Straight across (south to north, west to east) or turning a corner, winding a
    /// little, sometimes widening into a small chamber; glowing mushrooms for light; debris. Small enough to build
    /// while one walks through it, which is what it is for: the next map loads behind it.
    /// </summary>
    public static class KitConnectorGenerator
    {
        [Serializable]
        public class Options
        {
            [Tooltip("The edge the map one comes from meets: N, S, E or W.")]
            public string from = "S";
            [Tooltip("The edge the next map meets (not the same as From).")]
            public string to = "N";
            [Tooltip("Cells from one opening to the other along the way (about 8-14).")]
            public int length = 10;
            [Tooltip("The openings' width in cells: the maps either side use the same.")]
            public int width = 2;
            [Tooltip("The openings' first cell along their edges; -1: the generator picks.")]
            public int fromAt = -1, toAt = -1;
            public int seed = 1;
            [Tooltip("Cave: cave floor. Dungeon: a dressed-stone floor (the sides stay bare rock, as at every seam).")]
            public string style = "Cave";
            [Range(0, 1)] public float debris = 0.3f;
        }

        const float IG = 1.5f;
        static readonly (int, int)[] N4 = { (1, 0), (-1, 0), (0, 1), (0, -1) };

        public static (string plan, JObject record) Generate(Options o)
        {
            var rnd = new System.Random(o.seed);
            char a = Side(o.from), b = Side(o.to);
            if (b == a) b = KitPortal.Opposite(a);
            int w = Mathf.Clamp(o.width, 1, 3);
            int band = w + 2 * KitPortal.Margin;                      // the seam row the maps either side share
            bool straight = b == KitPortal.Opposite(a);
            int L = Mathf.Max(2 * KitPortal.Approach + 2, o.length);
            int nc, nr;
            if (straight)
            {
                int across = band + 2 * rnd.Next(1, 3);                // room to wind
                (nc, nr) = a == 'N' || a == 'S' ? (across, L) : (L, across);
            }
            else nc = nr = Mathf.Max(band + 3, L / 2 + KitPortal.Approach + 1);
            var pa = new KitPortal { id = "from", side = a.ToString(), width = w, seam = true, at = o.fromAt };
            var pb = new KitPortal { id = "to", side = b.ToString(), width = w, seam = true, at = o.toAt };
            // where the openings sit along their edges: anywhere in the band's reach when straight; round a corner, each
            // in the half of its edge away from the other's edge, so the way has some length
            foreach (var (p, other) in new[] { (pa, b), (pb, a) })
            {
                if (p.at >= 0) continue;
                int len = KitPortal.EdgeLength(p.Side, nc, nr);
                int lo = KitPortal.Margin, hi = len - w - KitPortal.Margin;
                if (!straight)
                {
                    // along N / S edges k runs east, along E / W edges north: the other edge lies at k's high end if it is E or N
                    bool otherHigh = other == 'E' || other == 'N';
                    if (otherHigh) hi = Mathf.Max(lo, Mathf.Min(hi, len / 2 - w));
                    else lo = Mathf.Min(hi, Mathf.Max(lo, (len + 1) / 2));
                }
                p.at = rnd.Next(lo, Mathf.Max(lo, hi) + 1);
            }

            var open = new HashSet<(int, int)>();
            for (int d = 0; d < KitPortal.Approach; d++) { open.UnionWith(pa.Row(d, nc, nr)); open.UnionWith(pb.Row(d, nc, nr)); }
            // the way between the approaches' ends: a w x w brush walked toward the far end, wandering sideways now and
            // then, kept a cell in from the outer edges and clear of the seam rows
            (int, int) Anchor(KitPortal p) => p.Side == 'N' ? (p.at, nr - KitPortal.Approach - (w - 1)) : p.Side == 'S' ? (p.at, KitPortal.Approach - 1)
                                           : p.Side == 'E' ? (nc - KitPortal.Approach - (w - 1), p.at) : (KitPortal.Approach - 1, p.at);
            int x0 = 1, y0 = 1, x1 = nc - w - 1, y1 = nr - w - 1;
            if (a == 'S' || b == 'S') y0 = Mathf.Max(y0, KitPortal.Approach - 1);
            if (a == 'N' || b == 'N') y1 = Mathf.Min(y1, nr - KitPortal.Approach - (w - 1));
            if (a == 'W' || b == 'W') x0 = Mathf.Max(x0, KitPortal.Approach - 1);
            if (a == 'E' || b == 'E') x1 = Mathf.Min(x1, nc - KitPortal.Approach - (w - 1));
            var cur = Anchor(pa); var goal = Anchor(pb);
            var path = new List<(int, int)>();
            void Brush((int, int) q) { for (int i = 0; i < w; i++) for (int j = 0; j < w; j++) open.Add((q.Item1 + i, q.Item2 + j)); path.Add(q); }
            Brush(cur);
            for (int step = 0; step < 6 * (nc + nr) && cur != goal; step++)
            {
                int dx = Math.Sign(goal.Item1 - cur.Item1), dy = Math.Sign(goal.Item2 - cur.Item2);
                (int, int) next;
                if (rnd.NextDouble() < 0.28)                             // wander across the way
                {
                    bool alongY = Math.Abs(goal.Item2 - cur.Item2) >= Math.Abs(goal.Item1 - cur.Item1);
                    int s = rnd.Next(2) == 0 ? -1 : 1;
                    next = alongY ? (cur.Item1 + s, cur.Item2) : (cur.Item1, cur.Item2 + s);
                }
                else if (dx != 0 && (dy == 0 || rnd.Next(2) == 0)) next = (cur.Item1 + dx, cur.Item2);
                else next = (cur.Item1, cur.Item2 + dy);
                next = (Mathf.Clamp(next.Item1, x0, Mathf.Max(x0, x1)), Mathf.Clamp(next.Item2, y0, Mathf.Max(y0, y1)));
                cur = next;
                Brush(cur);
            }
            Brush(goal);
            // now and then a small chamber partway along
            if (path.Count > 6 && rnd.NextDouble() < 0.6)
            {
                var (cx, cy) = path[path.Count / 3 + rnd.Next(Mathf.Max(1, path.Count / 3))];
                float rad = 1.4f + (float)rnd.NextDouble() * 0.8f;
                float mx = cx + w / 2f, my = cy + w / 2f;
                for (int c = x0; c <= x1 + w - 1; c++)
                    for (int r = y0; r <= y1 + w - 1; r++)
                        if ((c + 0.5f - mx) * (c + 0.5f - mx) + (r + 0.5f - my) * (r + 0.5f - my) <= rad * rad) open.Add((c, r));
            }

            var codes = new Dictionary<(int, int), string>();
            for (int c = 0; c < nc; c++) for (int r = 0; r < nr; r++) if (!open.Contains((c, r))) codes[(c, r)] = "##";
            // glowing mushrooms against the rock where the way is wide enough to keep two cells free past them
            var approach = new HashSet<(int, int)>(Enumerable.Range(0, KitPortal.Approach).SelectMany(d => pa.Row(d, nc, nr).Concat(pb.Row(d, nc, nr))));
            var plist = new JArray();
            int lights = 0;
            foreach (var q in open.OrderBy(_ => rnd.Next()).ToList())
            {
                if (lights >= 2) break;
                if (approach.Contains(q) || !N4.Any(d => !open.Contains((q.Item1 + d.Item1, q.Item2 + d.Item2)))) continue;
                var rest = new HashSet<(int, int)>(open.Where(c => c != q && !codes.ContainsKey(c)));
                if (!Connected(rest) || N4.Select(d => (q.Item1 + d.Item1, q.Item2 + d.Item2)).Where(rest.Contains).Any(n => !InBlock(n, rest))) continue;
                codes[q] = "MG";
                lights++;
            }
            var zone = new JObject { ["cells"] = "rest", ["floor"] = o.style == "Dungeon" ? "DungeonFlag" : "CaveFloor" };
            var R = new JObject
            {
                ["building"] = "Dungeon", ["floor"] = -9, ["preset"] = "Cavern",
                ["family"] = new JObject { ["perimeter"] = "Cave", ["partition"] = "Cave" },
                ["cave"] = true, ["pools"] = false, ["rush_mats"] = false,
                ["zones"] = new JObject { ["passage"] = zone },
                ["links"] = new JArray(), ["props"] = plist,
                ["portals"] = new JArray(pa.ToJson(), pb.ToJson()),
                ["debris"] = new JObject { ["density"] = o.debris, ["seed"] = o.seed },
                ["generated"] = new JObject { ["generator"] = "connector", ["from"] = a.ToString(), ["to"] = b.ToString(), ["seed"] = o.seed, ["nc"] = nc, ["nr"] = nr },
            };
            return (KitCaveGenerator.MakePlan(nc, nr, codes), R);
        }

        static char Side(string s) => string.IsNullOrEmpty(s) ? 'S' : char.ToUpperInvariant(s[0]) is char c && "NSEW".IndexOf(c) >= 0 ? c : 'S';

        static bool InBlock((int, int) n, HashSet<(int, int)> cells) =>
            new[] { (0, 0), (-1, 0), (0, -1), (-1, -1) }.Any(b => new[] { (0, 0), (1, 0), (0, 1), (1, 1) }
                .All(d => cells.Contains((n.Item1 + b.Item1 + d.Item1, n.Item2 + b.Item2 + d.Item2))));

        static bool Connected(HashSet<(int, int)> cells)
        {
            if (cells.Count == 0) return true;
            var seen = new HashSet<(int, int)> { cells.First() };
            var todo = new Stack<(int, int)>(seen);
            while (todo.Count > 0)
            {
                var (c, r) = todo.Pop();
                foreach (var (dc, dr) in N4) { var q = (c + dc, r + dr); if (cells.Contains(q) && seen.Add(q)) todo.Push(q); }
            }
            return seen.Count == cells.Count;
        }
    }
}
