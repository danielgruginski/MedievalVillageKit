using System;
using System.Collections.Generic;
using System.Linq;

namespace MedievalKit
{
    /// <summary>
    /// Furniture codes for the generators (dungeons, house interiors): pieces from a table (code, how many, "wall" along
    /// the walls / "mid" in the middle) go on free cells of a rectangular room, a cell apart from each other, and only
    /// where every walkable cell of the room stays reachable from its ways in (doors, gaps, a stair's arrival "Ss").
    /// </summary>
    internal static class KitFurnisher
    {
        internal static readonly HashSet<string> Flat = new HashSet<string> { "br", "st", "gc", "bo", "rf", "rg", "ts" };     // overlays: walked over

        /// <summary>every walkable cell of the room (no code, a stair's arrival "Ss" or an overlay; not a stair's own cells)
        /// connects to ONE way in (so every other door and the arrival too)</summary>
        internal static bool Connected(int c0, int r0, int c1, int r1, Dictionary<(int, int), string> codes, HashSet<(int, int)> ways, HashSet<(int, int)> noWalk)
        {
            bool Walk((int, int) p) => p.Item1 >= c0 && p.Item1 <= c1 && p.Item2 >= r0 && p.Item2 <= r1 && !noWalk.Contains(p) &&
                                      (!codes.TryGetValue(p, out var cc) || cc == ".." || cc == "Ss" || Flat.Contains(cc));
            var walk = new List<(int, int)>();
            for (int c = c0; c <= c1; c++) for (int r = r0; r <= r1; r++) if (Walk((c, r))) walk.Add((c, r));
            if (walk.Count == 0) return true;
            var seed = walk.Where(q => ways.Contains(q) || (codes.TryGetValue(q, out var cc) && cc == "Ss")).DefaultIfEmpty(walk[0]).First();
            var seen = new HashSet<(int, int)> { seed };
            var todo = new Stack<(int, int)>();
            todo.Push(seed);
            while (todo.Count > 0)
            {
                var (c, r) = todo.Pop();
                foreach (var q in new[] { (c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1) })
                    if (Walk(q) && seen.Add(q)) todo.Push(q);
            }
            return seen.Count == walk.Count;
        }

        internal static void Place(Random rnd, int c0, int r0, int c1, int r1, IEnumerable<(string code, int min, int max, string place)> table,
                                   Dictionary<(int, int), string> codes, HashSet<(int, int)> reserved, HashSet<(int, int)> ways,
                                   HashSet<(int, int)> noWalk, Func<string, (int, int)> fp)
        {
            int W = c1 - c0 + 1, H = r1 - r0 + 1;
            var cells = Enumerable.Range(c0, W).SelectMany(c => Enumerable.Range(r0, H).Select(r => (c, r))).ToList();
            bool Has((int, int) p) => p.Item1 >= c0 && p.Item1 <= c1 && p.Item2 >= r0 && p.Item2 <= r1;
            bool Edge((int, int) p) => p.Item1 == c0 || p.Item1 == c1 || p.Item2 == r0 || p.Item2 == r1;
            bool Free((int, int) p) => Has(p) && !reserved.Contains(p) && (!codes.TryGetValue(p, out var cc) || cc == "..");
            bool Connected() => KitFurnisher.Connected(c0, r0, c1, r1, codes, ways, noWalk);
            foreach (var (code, mn, mx, place) in table)
            {
                int n = rnd.Next(mn, mx + 1);
                var (fw, fd) = fp(code);
                for (int k = 0; k < n; k++)
                {
                    var spots = new List<List<(int, int)>>();
                    foreach (var c in cells)
                        foreach (var (w, d) in fw == fd ? new[] { (fw, fd) } : new[] { (fw, fd), (fd, fw) })
                        {
                            var blk = Enumerable.Range(0, w).SelectMany(a => Enumerable.Range(0, d).Select(b => (c.Item1 + a, c.Item2 + b))).ToList();
                            if (!blk.All(Free)) continue;
                            bool onEdge = blk.Any(Edge);
                            if ((place == "wall") != onEdge && !(place == "mid" && W < 4 && H < 4)) continue;
                            if (place == "wall" && w > d && !blk.All(q => q.Item2 == r0 || q.Item2 == r1)) continue;   // the long side on the wall
                            if (place == "wall" && d > w && !blk.All(q => q.Item1 == c0 || q.Item1 == c1)) continue;
                            spots.Add(blk);
                        }
                    List<(int, int)> pick = null;
                    foreach (var blk in spots.OrderBy(_ => rnd.Next()))
                    {
                        foreach (var q in blk) codes[q] = code;
                        if (Flat.Contains(code) || Connected()) { pick = blk; break; }
                        foreach (var q in blk) codes.Remove(q);              // it would cut part of the room off: another spot
                    }
                    if (pick == null) break;
                    foreach (var q in pick)                                  // a cell clear round it (blocks of one code must not touch)
                        foreach (var dq in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                        {
                            var nq = (q.Item1 + dq.Item1, q.Item2 + dq.Item2);
                            if (!pick.Contains(nq)) reserved.Add(nq);
                        }
                }
            }
        }
    }
}
