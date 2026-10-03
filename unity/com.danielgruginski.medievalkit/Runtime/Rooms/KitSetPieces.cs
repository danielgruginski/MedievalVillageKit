using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Set-pieces and dressing for the generators, as record props ([name, x, y, rot, style, mount, opts]): the groups
    /// furniture codes cannot say (a bar counter with its cask racks behind it, an altar between statues and braziers,
    /// pillars on the grid's nodes), the dressing on the tables the codes place, things hung on the walls. A set-piece
    /// holds its cells with the code "@@" (furniture the record places: the codes' furniture skips it, the walk checks
    /// treat it as a prop), and only where the room stays walkable from its ways in.
    /// </summary>
    internal static class KitSetPieces
    {
        const float IG = 1.5f;
        internal const string Held = "@@";

        /// <summary>a rectangular room: its codes, the cells kept clear (doorways and the like), its ways in, the cells
        /// no one walks (a stair's), and what stands on each side of a cell ("wall": 0 nothing / open, 1 a plain wall, 2
        /// a plain wall of full height)</summary>
        internal sealed class Area
        {
            public int c0, r0, c1, r1;
            public Dictionary<(int, int), string> codes;
            public HashSet<(int, int)> reserved, ways, noWalk;
            public Func<(int, int), char, int> wall;

            public bool Has((int, int) p) => p.Item1 >= c0 && p.Item1 <= c1 && p.Item2 >= r0 && p.Item2 <= r1;
            bool Coded((int, int) p) => codes.TryGetValue(p, out var cc) && cc != "..";
            public bool Free((int, int) p) => Has(p) && !reserved.Contains(p) && !Coded(p);
            /// <summary>free of furniture and of ways, though in some piece's clear ring</summary>
            public bool Bare((int, int) p) => Has(p) && !ways.Contains(p) && !noWalk.Contains(p) && !Coded(p) && !N4(p).Any(ways.Contains);
            public bool Connected() => KitFurnisher.Connected(c0, r0, c1, r1, codes, ways, noWalk);
            public IEnumerable<(int, int)> Cells => Enumerable.Range(c0, c1 - c0 + 1).SelectMany(c => Enumerable.Range(r0, r1 - r0 + 1).Select(r => (c, r)));
            /// <summary>the cells along side s, in order along the side's run direction</summary>
            public List<(int, int)> Line(char s) =>
                s == 'N' ? Enumerable.Range(c0, c1 - c0 + 1).Select(c => (c, r1)).ToList()
              : s == 'S' ? Enumerable.Range(c0, c1 - c0 + 1).Select(c => (c, r0)).ToList()
              : s == 'W' ? Enumerable.Range(r0, r1 - r0 + 1).Select(r => (c0, r)).ToList()
              : Enumerable.Range(r0, r1 - r0 + 1).Select(r => (c1, r)).ToList();
        }

        internal static IEnumerable<(int, int)> N4((int, int) p) => new[] { (p.Item1 + 1, p.Item2), (p.Item1 - 1, p.Item2), (p.Item1, p.Item2 + 1), (p.Item1, p.Item2 - 1) };
        /// <summary>the rot that turns a piece's back to side s: N 0, S 180, W 90, E -90</summary>
        internal static float BackTo(char s) => s == 'N' ? 0f : s == 'S' ? 180f : s == 'W' ? 90f : -90f;
        static (int, int) Out(char s) => s == 'N' ? (0, 1) : s == 'S' ? (0, -1) : s == 'W' ? (-1, 0) : (1, 0);
        /// <summary>a piece's local +x at BackTo(s): along the wall</summary>
        static (int, int) Along(char s) => s == 'N' ? (1, 0) : s == 'S' ? (-1, 0) : s == 'W' ? (0, 1) : (0, -1);
        static (int, int) Add((int, int) p, (int, int) d, int k = 1) => (p.Item1 + k * d.Item1, p.Item2 + k * d.Item2);
        static float X((int, int) p) => IG * (p.Item1 + 0.5f);
        static float Y((int, int) p) => IG * (p.Item2 + 0.5f);

        internal static JArray Prop(string name, float x, float y, float rot, string mount = null, JObject opts = null)
        {
            var a = new JArray(name, Math.Round(x, 3), Math.Round(y, 3), rot, null, mount);
            if (opts != null) a.Add(opts);
            return a;
        }

        /// <summary>codes on cells, kept only if every cell was free and the room stays connected; the `keep` cells
        /// (inside the room, without furniture) are then reserved clear</summary>
        static bool Hold(Area a, IEnumerable<((int, int) cell, string code)> put, IEnumerable<(int, int)> keep, bool loose = false)
        {
            var list = put.ToList();
            var k = keep.ToList();
            if (!list.All(q => loose ? a.Bare(q.cell) : a.Free(q.cell)) || list.Select(q => q.cell).Distinct().Count() != list.Count) return false;
            if (k.Any(q => !a.Has(q) || a.noWalk.Contains(q) || (a.codes.TryGetValue(q, out var cc) && cc != ".." && cc != "Ss") || list.Any(l => l.cell == q))) return false;
            foreach (var (q, code) in list) a.codes[q] = code;
            if (!a.Connected()) { foreach (var (q, _) in list) a.codes.Remove(q); return false; }
            foreach (var q in k) a.reserved.Add(q);
            foreach (var (q, _) in list) foreach (var n in N4(q)) if (a.Has(n) && !a.codes.ContainsKey(n)) a.reserved.Add(n);
            return true;
        }

        /// <summary>a bar against a wall (east, west or north): counters a cell out from it with cask racks behind them,
        /// an end piece where the run stops and, behind the end, the way in for the barkeep</summary>
        internal static bool Bar(System.Random rnd, Area a, JArray props)
        {
            foreach (var s in new[] { 'E', 'W', 'N' }.OrderBy(_ => rnd.Next()))
            {
                var o = Out(s); var t = Along(s);
                var line = a.Line(s);
                for (int n = Mathf.Min(3, line.Count - 3); n >= 1; n--)          // the longest run that fits
                foreach (var w0 in line.OrderBy(_ => rnd.Next()))
                {
                    var p0 = Add(w0, o, -1);
                    var counters = Enumerable.Range(0, n).Select(i => Add(p0, t, i)).ToList();
                    var racks = counters.Select(q => Add(q, o)).ToList();
                    var end = Add(p0, t, -1);
                    var access = Add(end, o);
                    var way = Add(access, t, -1);
                    if (!racks.All(q => a.Has(q) && a.wall(q, s) >= 1)) continue;
                    var put = counters.Concat(racks).Append(end).Select(q => (q, Held));
                    var keep = new[] { access, way }.Concat(counters.Append(end).Select(q => Add(q, o, -1)));
                    if (!Hold(a, put, keep)) continue;
                    float rot = BackTo(s);
                    foreach (var q in racks) props.Add(Prop("CaskRack_150", X(q), Y(q), rot));
                    foreach (var q in counters) props.Add(Prop("Bar_Counter_150", X(q), Y(q), rot));
                    props.Add(Prop("Bar_End_150", X(end), Y(end), rot));
                    return true;
                }
            }
            return false;
        }

        /// <summary>a centrepiece against a wall (an altar two cells wide, a hoard's chest one), with a piece on the wall
        /// either side of it (statues) and braziers before it; the way up to it kept clear. Sides tried: the given order</summary>
        internal static bool Shrine(System.Random rnd, Area a, JArray props, string centre, int w, string flank, string brazier, string sides = "NEW")
        {
            foreach (var s in sides)
            {
                var o = Out(s); var t = Along(s);
                var line = a.Line(s);
                foreach (var f0 in line.OrderBy(q => Math.Abs(line.IndexOf(q) + (w + 1) / 2f - (line.Count - 1) / 2f)).ThenBy(_ => rnd.Next()))
                {
                    var mid = Enumerable.Range(1, w).Select(i => Add(f0, t, i)).ToList();
                    var f1 = Add(f0, t, w + 1);
                    var run = new List<(int, int)> { f0 }.Concat(mid).Append(f1).ToList();
                    if (!run.All(q => a.Has(q) && a.wall(q, s) >= 1)) continue;
                    var flanks = flank != null ? new List<(int, int)> { f0, f1 } : new List<(int, int)>();
                    var fires = brazier == null ? new List<(int, int)>() : w >= 2 ? mid.Select(q => Add(q, o, -1)).ToList() : new List<(int, int)> { Add(f0, o, -1), Add(f1, o, -1) };
                    var approach = w >= 2 ? mid.Select(q => Add(q, o, brazier != null ? -2 : -1)).ToList() : new List<(int, int)> { Add(mid[0], o, -1), Add(mid[0], o, -2) };
                    var put = mid.Concat(flanks).Concat(fires).Select(q => (q, Held));
                    if (!Hold(a, put, approach)) continue;
                    float rot = BackTo(s);
                    float cx = mid.Average(q => X(q)), cy = mid.Average(q => Y(q));
                    props.Add(Prop(centre, cx, cy, rot));
                    foreach (var q in flanks) props.Add(Prop(flank, X(q), Y(q), rot));
                    for (int i = 0; i < fires.Count; i++)
                    {
                        // two cells wide: before the centrepiece, pushed apart to frame the way up to it
                        float push = w >= 2 ? (i == 0 ? -0.15f : 0.15f) : 0f;
                        props.Add(Prop(brazier, X(fires[i]) + push * t.Item1, Y(fires[i]) + push * t.Item2, 0f));
                    }
                    return true;
                }
            }
            return false;
        }

        /// <summary>pillars on the grid's nodes (each takes a corner of four cells, which stay walkable): along the
        /// room's long axis, two cells in from the walls, every second node; one line down the middle in a room five
        /// deep, two lines in a deeper one. Only where the four cells round a node are bare</summary>
        internal static int Pillars(Area a, JArray props, string piece)
        {
            int W = a.c1 - a.c0 + 1, H = a.r1 - a.r0 + 1;
            bool alongX = W >= H;
            int len = alongX ? W : H, dep = alongX ? H : W, l0 = alongX ? a.c0 : a.r0, d0 = alongX ? a.r0 : a.c0;
            if (len < 6 || dep < 5) return 0;
            var lines = dep >= 6 ? new[] { d0 + 2, d0 + dep - 2 } : new[] { d0 + dep / 2 };
            int k = 0;
            foreach (int d in lines)
                for (int l = l0 + 2; l <= l0 + len - 2; l += 2)          // nodes two cells in from either end
                {
                    var (i, j) = alongX ? (l, d) : (d, l);
                    var four = new[] { (i - 1, j - 1), (i, j - 1), (i - 1, j), (i, j) };
                    if (!four.All(a.Bare)) continue;
                    props.Add(Prop(piece, IG * i, IG * j, 0f, null, new JObject { ["hug"] = false }));
                    k++;
                }
            return k;
        }

        /// <summary>pieces hung on full-height plain walls (lanterns, chains, tool walls), apart from each other and
        /// from the ways in; `over` limits them to cells with those codes (a tool wall over its bench), else to cells
        /// without furniture</summary>
        internal static int WallHung(System.Random rnd, Area a, JArray props, string piece, int n, int gap = 3, ICollection<string> over = null)
        {
            var cands = new List<((int, int) q, char s)>();
            foreach (var s in "NEWS")
                foreach (var q in a.Line(s))
                {
                    if (a.wall(q, s) < 2 || a.ways.Contains(q) || N4(q).Any(a.ways.Contains) || a.noWalk.Contains(q)) continue;
                    bool coded = a.codes.TryGetValue(q, out var cc) && cc != "..";
                    if (over != null ? !(coded && over.Contains(cc)) : coded) continue;
                    cands.Add((q, s));
                }
            var got = new List<(int, int)>();
            foreach (var (q, s) in cands.OrderBy(_ => rnd.Next()))
            {
                if (got.Count >= n) break;
                if (got.Any(g => Math.Max(Math.Abs(g.Item1 - q.Item1), Math.Abs(g.Item2 - q.Item2)) < gap)) continue;
                props.Add(Prop(piece, X(q), Y(q), BackTo(s), "wall_hung"));
                got.Add(q);
            }
            return got.Count;
        }

        /// <summary>dressing on the tables the codes place: a trestle block ("TB", its forms included) has its table at
        /// the block's centre, along the block; a small table ("tb") at its cell's centre</summary>
        internal static void TableTops(System.Random rnd, Area a, JArray props, string[] big, string[] small, float share = 0.85f)
        {
            var seen = new HashSet<(int, int)>();
            foreach (var q in a.Cells)
            {
                if (seen.Contains(q) || !a.codes.TryGetValue(q, out var code) || (code != "TB" && code != "tb")) continue;
                var blk = new List<(int, int)> { q };
                seen.Add(q);
                for (int i = 0; i < blk.Count; i++)
                    foreach (var nq in N4(blk[i]))
                        if (a.Has(nq) && !seen.Contains(nq) && a.codes.TryGetValue(nq, out var nc) && nc == code) { seen.Add(nq); blk.Add(nq); }
                var pool = code == "TB" ? big : small;
                if (pool == null || pool.Length == 0 || rnd.NextDouble() > share) continue;
                int bc0 = blk.Min(b => b.Item1), bc1 = blk.Max(b => b.Item1), br0 = blk.Min(b => b.Item2), br1 = blk.Max(b => b.Item2);
                float rot = (code == "TB" && br1 - br0 > bc1 - bc0 ? 90f : 0f) + (rnd.Next(2) == 0 ? 0f : 180f);
                props.Add(Prop(pool[rnd.Next(pool.Length)], IG * (bc0 + bc1 + 1) / 2f, IG * (br0 + br1 + 1) / 2f, rot, "table", new JObject { ["on"] = true }));
            }
        }

        /// <summary>a code on a free cell beside an anchor (a chest by a bed, a log basket by the hearth): inside a
        /// clear ring is fine, a doorway's is not; `ok` filters the cells (against a wall, say)</summary>
        internal static (int, int)? Beside(System.Random rnd, Area a, IEnumerable<(int, int)> anchor, string code, Func<(int, int), bool> ok = null)
        {
            var anc = anchor.ToList();
            foreach (var p in anc.SelectMany(N4).Distinct().Where(p => !anc.Contains(p) && a.Bare(p) && (ok == null || ok(p))).OrderBy(_ => rnd.Next()).ToList())
                if (Hold(a, new[] { (p, code) }, Array.Empty<(int, int)>(), loose: true)) return p;
            return null;
        }

        /// <summary>codes on consecutive cells along a plain wall (an oven and its worktable, a bench), the cells before
        /// them kept clear</summary>
        internal static List<(int, int)> Strip(System.Random rnd, Area a, string[] codes, string sides = "NEWS")
        {
            foreach (var s in sides.OrderBy(_ => rnd.Next()))
            {
                var o = Out(s); var t = Along(s);
                foreach (var w0 in a.Line(s).OrderBy(_ => rnd.Next()))
                {
                    var run = Enumerable.Range(0, codes.Length).Select(i => Add(w0, t, i)).ToList();
                    if (!run.All(q => a.Has(q) && a.wall(q, s) >= 1)) continue;
                    if (!Hold(a, run.Select((q, i) => (q, codes[i])), run.Select(q => Add(q, o, -1)))) continue;
                    return run;
                }
            }
            return null;
        }
    }
}
