using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A random town sewer for <see cref="KitRoom"/> (the sewer kit's pieces, docs/SEWER_KIT.md): a cave map whose tunnels
    /// are walled in old brick (the rock between them is the kit's rock tiles, wall-backed behind the brick). The tunnels
    /// follow a street grid -- a trunk across the map and branches off it to the grid's crossings, a walkway either side of
    /// a water channel ("ww" channel tiles) -- with dry passages two cells wide closing loops. Every channel runs from its
    /// heads (an outfall pouring from a north wall, a culvert under an end wall) to one outlet (the trunk's downstream end,
    /// a culvert: R["channel_sinks"], the flow Unity's water shaders read). Some crossings are vaulted chambers: a cistern
    /// (a basin the channels meet in) or a hall. Cross walls stand over the channels (a culvert under them, doors on the
    /// walkways), slab bridges join walkways the water parts (as few as keep every walkway reachable, then one every few
    /// strides), sluice gates sit in the branches. Natural grottoes open off the tunnels through breaches in the brick; the
    /// one farthest from the way in is the lair (its point of interest: the rat king's junk throne) and holds the tunnel on
    /// down. The way in is a ladder up to the street (a scene link, as a passage). Torches on the full walls, sludge,
    /// puddles and drain grates on the walkways, glowing mushrooms, refuse and bones in the grottoes, barrels and crates in
    /// the chambers, the kit's debris by zone theme; an encounter in every grotto and chamber and along the tunnels, harder
    /// the farther the walk from the ladder (the lair's the boss).
    /// </summary>
    public static class KitSewerGenerator
    {
        [Serializable]
        public class Options
        {
            public int nc = 30, nr = 22, seed = 7;
            [Tooltip("Share of the street grid's crossings the tunnels reach (the rest stays rock: room for the grottoes).")]
            [Range(0.3f, 1f)] public float reach = 0.85f;
            [Tooltip("Dry passages two cells wide closing loops between the tunnels, per crossing reached.")]
            [Range(0f, 1f)] public float loops = 0.35f;
            [Tooltip("Vaulted chambers on the crossings: a cistern (a basin the channels meet in) or a hall.")]
            public int chambers = 2;
            [Tooltip("Natural caves the tunnels have broken into (a breach in the brick); the one farthest from the ladder is the lair.")]
            public int grottoes = 2;
            [Tooltip("Cross walls over the channels (a culvert under them, a door on the walkways).")]
            public int crossWalls = 2;
            [Range(0f, 1f)] public float debris = 0.35f;     // loose debris (the kit's scatter by zone theme): share of the open cells
            [Tooltip("The ladder up to the street (the way in): its link id (its spawn's id too), the scene it leads to, the spawn there.")]
            public string upId = "up", upTarget = "@return", upArrive = "";
            [Tooltip("A tunnel on down in the lair's rock (else a passage in a north wall): the scene it leads to; empty: none.")]
            public string deep = "";
            public string deepId = "down", deepArrive = "";
            [Tooltip("The encounters' creature tag, and the lair's (the boss).")]
            public string creature = "rat", boss = "boss";
            [Tooltip("The lair's point of interest (2 x 2 cells), e.g. POI_RatKing; empty: none.")]
            public string poi = "POI_RatKing";
            [Tooltip("How many encounters (0: by the level's size): one in every grotto and chamber, the rest along the tunnels.")]
            public int encounters = 0;
        }

        const float IG = 1.5f;
        static readonly (int, int)[] D4 = { (1, 0), (-1, 0), (0, 1), (0, -1) };
        static (int, int) Add((int, int) a, (int, int) d, int k = 1) => (a.Item1 + k * d.Item1, a.Item2 + k * d.Item2);
        static (int, int) Neg((int, int) d) => (-d.Item1, -d.Item2);
        static List<(int, int)> Sorted(IEnumerable<(int, int)> s) => s.OrderBy(q => q.Item1).ThenBy(q => q.Item2).ToList();
        static float X((int, int) q) => IG * (q.Item1 + 0.5f);
        static float Y((int, int) q) => IG * (q.Item2 + 0.5f);

        /// <summary>n lines from lo to hi, evenly spread, each nudged a cell where the lines stay six cells apart</summary>
        static int[] Spread(System.Random rnd, int n, int lo, int hi)
        {
            var a = new int[n];
            for (int k = 0; k < n; k++) a[k] = Mathf.RoundToInt(Mathf.Lerp(lo, hi, n == 1 ? 0.5f : k / (float)(n - 1)));
            for (int k = 0; k < n; k++)
            {
                int v = Mathf.Clamp(a[k] + rnd.Next(-1, 2), lo, hi);
                if ((k == 0 || v - a[k - 1] >= 6) && (k == n - 1 || a[k + 1] - v >= 6)) a[k] = v;
            }
            return a;
        }

        public static (string plan, JObject record) Generate(Options o)
        {
            var rnd = new System.Random(o.seed);
            int nc = Mathf.Max(20, o.nc), nr = Mathf.Max(16, o.nr);
            var notes = new List<string>();
            bool Inside((int, int) q) => q.Item1 >= 1 && q.Item1 <= nc - 2 && q.Item2 >= 1 && q.Item2 <= nr - 2;

            // ---- the street grid: tunnel lines every 9-11 cells across, 6-8 up; the trunk along the middle line, branches
            // off it (a random tree over the grid's crossings), dry passages closing loops
            int gx = Mathf.Max(2, 1 + (nc - 8) / 9), gy = Mathf.Max(2, 1 + (nr - 8) / 7);
            int[] GX = Spread(rnd, gx, 3, nc - 4), GY = Spread(rnd, gy, 4, nr - 5);
            (int, int) At((int, int) n) => (GX[n.Item1], GY[n.Item2]);
            bool OnGrid((int, int) n) => n.Item1 >= 0 && n.Item1 < gx && n.Item2 >= 0 && n.Item2 < gy;
            int trunk = gy / 2;
            var reached = new HashSet<(int, int)>();
            var wet = new List<((int, int) a, (int, int) b)>();
            var dry = new List<((int, int) a, (int, int) b)>();
            for (int ix = 0; ix < gx; ix++) { reached.Add((ix, trunk)); if (ix > 0) wet.Add(((ix - 1, trunk), (ix, trunk))); }
            int want = Mathf.Clamp(Mathf.RoundToInt(gx * gy * o.reach), gx + 1, gx * gy);
            while (reached.Count < want)
            {
                var cand = Sorted(reached).SelectMany(a => D4.Select(d => (a, b: Add(a, d)))).Where(e => OnGrid(e.b) && !reached.Contains(e.b)).ToList();
                if (cand.Count == 0) break;
                var e = cand[rnd.Next(cand.Count)];
                wet.Add((e.a, e.b)); reached.Add(e.b);
            }
            var used = new HashSet<((int, int), (int, int))>(wet.SelectMany(e => new[] { (e.a, e.b), (e.b, e.a) }));
            var spare = Sorted(reached).SelectMany(a => new[] { (1, 0), (0, 1) }.Select(d => (a, b: Add(a, d))))
                                       .Where(e => reached.Contains(e.b) && !used.Contains((e.a, e.b))).ToList();
            foreach (var e in spare.OrderBy(_ => rnd.Next()).Take(Mathf.RoundToInt(reached.Count * o.loops * 0.5f))) dry.Add(e);
            (int, int) Dir((int, int) a, (int, int) b) => (Math.Sign(b.Item1 - a.Item1), Math.Sign(b.Item2 - a.Item2));
            List<(int, int)> Dirs(List<((int, int) a, (int, int) b)> es, (int, int) n) =>
                es.Where(e => e.a == n || e.b == n).Select(e => e.a == n ? Dir(e.a, e.b) : Dir(e.b, e.a)).ToList();

            // ---- the tunnels: three cells wide (walkway, channel, walkway) round every crossing and along every branch,
            // the dry passages two
            var open = new HashSet<(int, int)>();
            var water = new HashSet<(int, int)>();
            void Box(int c0, int c1, int r0, int r1, HashSet<(int, int)> s) { for (int c = c0; c <= c1; c++) for (int r = r0; r <= r1; r++) s.Add((c, r)); }
            HashSet<(int, int)> Rect(((int, int) a, (int, int) b) e, bool isDry)
            {
                var (xa, ya) = At(e.a); var (xb, yb) = At(e.b);
                int x0 = Math.Min(xa, xb), x1 = Math.Max(xa, xb), y0 = Math.Min(ya, yb), y1 = Math.Max(ya, yb);
                var s = new HashSet<(int, int)>();
                if (!isDry) { if (ya == yb) Box(x0 - 1, x1 + 1, ya - 1, ya + 1, s); else Box(xa - 1, xa + 1, y0 - 1, y1 + 1, s); }
                else { if (ya == yb) Box(x0 + 2, x1 - 2, ya, ya + 1, s); else Box(xa, xa + 1, y0 + 2, y1 - 2, s); }
                return s;
            }
            HashSet<(int, int)> Own((int, int) n)
            {
                var (x, y) = At(n);
                var s = new HashSet<(int, int)>();
                Box(x - 1, x + 1, y - 1, y + 1, s);
                foreach (var e in wet.Where(e => e.a == n || e.b == n)) s.UnionWith(Rect(e, false));
                foreach (var e in dry.Where(e => e.a == n || e.b == n)) s.UnionWith(Rect(e, true));
                return s;
            }
            foreach (var n in reached) { var (x, y) = At(n); Box(x - 1, x + 1, y - 1, y + 1, open); }
            foreach (var e in wet)
            {
                open.UnionWith(Rect(e, false));
                var (xa, ya) = At(e.a); var (xb, yb) = At(e.b);
                if (ya == yb) for (int c = Math.Min(xa, xb); c <= Math.Max(xa, xb); c++) water.Add((c, ya));
                else for (int r = Math.Min(ya, yb); r <= Math.Max(ya, yb); r++) water.Add((xa, r));
            }
            foreach (var e in dry) open.UnionWith(Rect(e, true));

            // ---- chambers on crossings (not the trunk's ends): a cistern 7 x 7 round a basin of 3 x 3, else a hall 7 x 5;
            // two rock cells at least between them and any other tunnel
            var chambers = new Dictionary<(int, int), (int hw, int hh, bool cistern)>();
            var trunkEnds = new HashSet<(int, int)> { (0, trunk), (gx - 1, trunk) };
            foreach (var n in Sorted(reached).OrderBy(_ => rnd.Next()))
            {
                if (chambers.Count >= o.chambers) break;
                if (trunkEnds.Contains(n)) continue;
                var (x, y) = At(n);
                var own = Own(n);
                foreach (var (hw, hh, cis) in rnd.NextDouble() < 0.55 ? new[] { (3, 3, true), (3, 2, false) } : new[] { (3, 2, false) })
                {
                    if (x - hw < 1 || x + hw > nc - 2 || y - hh < 1 || y + hh > nr - 2) continue;
                    bool clear = true;
                    for (int c = x - hw - 2; c <= x + hw + 2 && clear; c++)
                        for (int r = y - hh - 2; r <= y + hh + 2 && clear; r++)
                            if (open.Contains((c, r)) && !own.Contains((c, r))) clear = false;
                    if (!clear) continue;
                    chambers[n] = (hw, hh, cis);
                    Box(x - hw, x + hw, y - hh, y + hh, open);
                    if (cis) Box(x - 1, x + 1, y - 1, y + 1, water);
                    break;
                }
            }
            bool InChamber((int, int) q) => chambers.Any(kv => Math.Abs(q.Item1 - At(kv.Key).Item1) <= kv.Value.hw && Math.Abs(q.Item2 - At(kv.Key).Item2) <= kv.Value.hh);
            bool NearCrossing((int, int) q, int k) => reached.Any(n => Math.Abs(q.Item1 - At(n).Item1) <= k && Math.Abs(q.Item2 - At(n).Item2) <= k);

            // ---- channel heads: a branch ending at a crossing runs on to the tunnel's end wall (a culvert under it, an
            // outfall when the wall is a north one with full rock behind); a dry passage running on: the channel ends at
            // the crossing (its rim). The outlet: the trunk's east end
            var heads = new List<((int, int) cell, (int, int) d)>();
            foreach (var n in Sorted(reached))
            {
                var wd = Dirs(wet, n);
                if (wd.Count != 1) continue;
                var outD = Neg(wd[0]);
                if (Dirs(dry, n).Contains(outD)) continue;
                var (x, y) = At(n);
                bool hasCh = chambers.TryGetValue(n, out var ch);
                if (hasCh && ch.cistern) continue;                       // the basin is its head
                int ext = hasCh ? (outD.Item1 != 0 ? ch.hw : ch.hh) : 1;
                for (int k = 1; k <= ext; k++) water.Add(Add((x, y), outD, k));
                heads.Add((Add((x, y), outD, ext), outD));
            }
            var sinks = new JObject();
            var outlet = heads.Where(h => h.d == (1, 0)).OrderByDescending(h => h.cell.Item1).ThenBy(h => Math.Abs(h.cell.Item2 - GY[trunk]))
                              .Concat(heads.OrderByDescending(h => h.cell.Item1)).FirstOrDefault();
            if (heads.Count > 0) sinks[$"{outlet.cell.Item1}|{outlet.cell.Item2}"] = new JArray(outlet.d.Item1, outlet.d.Item2);
            else notes.Add("no channel head: no outlet");
            var brick = new HashSet<(int, int)>(open);

            // ---- the rock behind a wall (vki_cave_cells): full unless open floor lies within two cells to its north
            bool IsRock((int, int) q) => !open.Contains(q);
            char Height(int c, int r) => r <= 0 || !IsRock((c, r + 1)) || !IsRock((c, r + 2)) ? 'C' : 'F';
            bool Walkway((int, int) q) => brick.Contains(q) && !water.Contains(q);

            // ---- the ladder up to the street: on the north wall of a walkway along an east-west branch, the westmost
            // whose rock behind is full (the arrival a cell in front of it)
            var ladderCands = new List<(int, int)>();
            foreach (var e in wet)
            {
                var (xa, ya) = At(e.a); var (xb, yb) = At(e.b);
                if (ya != yb) continue;
                for (int c = Math.Min(xa, xb) + 2; c <= Math.Max(xa, xb) - 2; c++)
                {
                    var w = (c, ya + 1);
                    if (Walkway(w) && Walkway((c - 1, ya + 1)) && Walkway((c + 1, ya + 1)) && IsRock((c, ya + 2)) && !InChamber(w) && Height(c, ya + 2) == 'F')
                        ladderCands.Add(w);
                }
            }
            if (ladderCands.Count == 0)                                   // any walkway with rock to its north
                ladderCands = Sorted(brick.Where(q => Walkway(q) && IsRock((q.Item1, q.Item2 + 1)) && Walkway((q.Item1 - 1, q.Item2)) && Walkway((q.Item1 + 1, q.Item2))));
            var ladder = ladderCands.OrderBy(q => q.Item1 + rnd.NextDouble() * 1.5).First();
            var passages = new JObject();
            var keepRock = new HashSet<(int, int)>();                      // rock left whole: the ladder's and the outfalls' full rock
            void Keep((int, int) q) { for (int a = -1; a <= 1; a++) for (int b = 1; b <= 3; b++) keepRock.Add((q.Item1 + a, q.Item2 + b)); }
            Keep(ladder);
            foreach (var h in heads.Where(h => h.d == (0, 1))) Keep(h.cell);

            // ---- cross walls over the channels: away from the crossings and the ladder; a culvert under the wall, a door on
            // each walkway (or a door and a plain wall)
            var ew = new Dictionary<(int, int), string>();
            var ns = new Dictionary<(int, int), string>();
            var doorCells = new HashSet<(int, int)>();
            var cross = new List<(string ori, int line, int at, bool both)>();
            var crossCands = new List<(string, int, int)>();
            foreach (var e in wet)
            {
                var (xa, ya) = At(e.a); var (xb, yb) = At(e.b);
                if (ya == yb)
                    for (int i = Math.Min(xa, xb) + 3; i <= Math.Max(xa, xb) - 2; i++)
                    {
                        var cells = new[] { (i - 1, ya - 1), (i, ya - 1), (i - 1, ya + 1), (i, ya + 1) };
                        if (cells.All(Walkway) && !cells.Any(InChamber) && !cells.Any(q => NearCrossing(q, 1)))
                            crossCands.Add(("NS", i, ya));
                    }
                else
                    for (int j = Math.Min(ya, yb) + 3; j <= Math.Max(ya, yb) - 2; j++)
                    {
                        var cells = new[] { (xa - 1, j - 1), (xa - 1, j), (xa + 1, j - 1), (xa + 1, j) };
                        if (cells.All(Walkway) && !cells.Any(InChamber) && !cells.Any(q => NearCrossing(q, 1)))
                            crossCands.Add(("EW", j, xa));
                    }
            }
            crossCands = crossCands.Where(cw => cw.Item1 != "NS" || !(Math.Abs(cw.Item2 - ladder.Item1) <= 2 && Math.Abs(cw.Item3 + 1 - ladder.Item2) <= 1)).ToList();
            foreach (var cw in crossCands.OrderBy(_ => rnd.Next()))
            {
                if (cross.Count >= o.crossWalls) break;
                if (cross.Any(q => q.ori == cw.Item1 && q.at == cw.Item3 && Math.Abs(q.line - cw.Item2) < 6)) continue;
                cross.Add((cw.Item1, cw.Item2, cw.Item3, rnd.NextDouble() < 0.6));
            }

            // ---- grottoes: natural caves grown from a breach in a walkway's wall into rock two cells clear of every
            // other tunnel (a neck two deep lets them reach it); the walls between them and the brick stay, but for the breach
            var grotto = new Dictionary<(int, int), int>();
            var breachSegs = new HashSet<(string, int, int)>();
            var ways = new HashSet<(int, int)>();                          // doorways, breaches, the ladder's foot: kept clear
            int nGrottoes = 0;
            for (int g = 0; g < o.grottoes; g++)
            {
                // the distance (8-neighbour steps) from every open cell
                var dist = new Dictionary<(int, int), int>();
                var q0 = new Queue<(int, int)>();
                foreach (var q in Sorted(open)) { dist[q] = 0; q0.Enqueue(q); }
                while (q0.Count > 0)
                {
                    var q = q0.Dequeue();
                    if (dist[q] >= 4) continue;
                    for (int a = -1; a <= 1; a++)
                        for (int b = -1; b <= 1; b++)
                        {
                            var p = (q.Item1 + a, q.Item2 + b);
                            if (p.Item1 < -1 || p.Item1 > nc || p.Item2 < -1 || p.Item2 > nr || dist.ContainsKey(p)) continue;
                            dist[p] = dist[q] + 1; q0.Enqueue(p);
                        }
                }
                int Dist((int, int) p) => dist.TryGetValue(p, out var v) ? v : 9;
                // contacts: two walkway cells side by side on a wall with rock beyond; the rock room beyond them scores it
                var contacts = new List<(List<(int, int)> rock, List<(int, int)> walk, (int, int) d, double score)>();
                foreach (var w in Sorted(brick.Where(Walkway)))
                    foreach (var d in D4)
                    {
                        var lat = (Math.Abs(d.Item2), Math.Abs(d.Item1));
                        var w2 = Add(w, lat);
                        var r1 = Add(w, d); var r2 = Add(w2, d);
                        if (!Walkway(w2) || !IsRock(r1) || !IsRock(r2) || !Inside(r1) || !Inside(r2)) continue;
                        if (w == ladder || w2 == ladder || ways.Contains(w) || ways.Contains(w2)) continue;
                        if (Math.Abs(w.Item1 - ladder.Item1) + Math.Abs(w.Item2 - ladder.Item2) < 3) continue;
                        int room = 0;
                        for (int k = 2; k <= 7; k++)
                            for (int s = -3; s <= 4; s++)
                            {
                                var p = Add(Add(w, d, k), lat, s);
                                if (Inside(p) && IsRock(p) && Dist(p) >= 3) room++;
                            }
                        double pref = d == (0, -1) || d == (0, 1) ? 1.0 : 0.75;     // a breach the camera sees: in an east-west wall
                        // the first grotto far from the ladder (it is likely the lair: the farthest)
                        double far = g == 0 ? 0.6 * (Math.Abs(w.Item1 - ladder.Item1) + Math.Abs(w.Item2 - ladder.Item2)) : 0;
                        contacts.Add((new List<(int, int)> { r1, r2 }, new List<(int, int)> { w, w2 }, d, room * pref + far + rnd.NextDouble() * 4));
                    }
                var best = contacts.OrderByDescending(cn => cn.score).FirstOrDefault();
                if (best.rock == null || best.score < 14) { notes.Add($"grotto {g}: no room left in the rock"); break; }
                var neck = new HashSet<(int, int)>(best.rock.Concat(best.rock.Select(p => Add(p, best.d))));
                bool Allowed((int, int) p) => Inside(p) && IsRock(p) && !grotto.ContainsKey(p) && !keepRock.Contains(p) && (Dist(p) >= 3 || neck.Contains(p));
                var region = new HashSet<(int, int)>(neck.Where(Allowed));
                int target = rnd.Next(18, 33);
                while (region.Count < target)
                {
                    var frontier = Sorted(region).SelectMany(p => D4.Select(d => Add(p, d))).Where(p => !region.Contains(p) && Allowed(p)).Distinct().ToList();
                    if (frontier.Count == 0) break;
                    var pick = frontier.OrderByDescending(p => 2 * D4.Count(d => region.Contains(Add(p, d))) + rnd.NextDouble() * 2.5).First();
                    region.Add(pick);
                }
                // every cell inside an open 2 x 2 block (the rock's lobes close one-cell necks), no cells meeting at a corner only
                for (int pass = 0; pass < 3; pass++)
                {
                    foreach (var p in Sorted(region))
                    {
                        var blocks = new[] { (p.Item1 - 1, p.Item2 - 1), (p.Item1, p.Item2 - 1), (p.Item1 - 1, p.Item2), p }
                            .Select(b => new[] { b, (b.Item1 + 1, b.Item2), (b.Item1, b.Item2 + 1), (b.Item1 + 1, b.Item2 + 1) }).ToList();
                        bool In((int, int) q) => region.Contains(q) || best.walk.Contains(q);
                        if (blocks.Any(bl => bl.All(In))) continue;
                        var fill = blocks.Where(bl => bl.All(q => In(q) || Allowed(q))).OrderByDescending(bl => bl.Count(In)).FirstOrDefault();
                        if (fill != null) foreach (var q in fill) if (!In(q)) region.Add(q);
                    }
                    for (int c = 0; c < nc - 1; c++)
                        for (int r = 0; r < nr - 1; r++)
                        {
                            bool a = region.Contains((c, r)), b = region.Contains((c + 1, r)), d = region.Contains((c, r + 1)), e = region.Contains((c + 1, r + 1));
                            if ((a && e && !b && !d) || (b && d && !a && !e))
                            {
                                var opts = (a ? new[] { (c + 1, r), (c, r + 1) } : new[] { (c, r), (c + 1, r + 1) }).Where(Allowed).ToList();
                                if (opts.Count > 0) region.Add(opts[0]);
                            }
                        }
                }
                region.RemoveWhere(p => !Inside(p) || !IsRock(p));
                if (region.Count < 8) { notes.Add($"grotto {g}: too small ({region.Count} cells)"); continue; }
                foreach (var p in region) { grotto[p] = nGrottoes; open.Add(p); }
                foreach (var (w, r) in best.walk.Zip(best.rock, (w, r) => (w, r)))
                {
                    if (best.d.Item2 != 0) breachSegs.Add(("EW", w.Item1, Math.Max(w.Item2, r.Item2)));
                    else breachSegs.Add(("NS", Math.Max(w.Item1, r.Item1), w.Item2));
                    ways.Add(w); ways.Add(r);
                }
                nGrottoes++;
            }

            // ---- walls on the grid lines: brick | rock (full north walls where the rock behind is full, cut elsewhere),
            // brick | grotto (cut, the breach in it), grotto | rock bare
            for (int j = 1; j < nr; j++)
                for (int i = 0; i < nc; i++)
                {
                    var s = (i, j - 1); var n = (i, j);
                    bool so = open.Contains(s), no = open.Contains(n);
                    if (so && no)
                    {
                        if (brick.Contains(s) != brick.Contains(n)) ew[(i, j)] = breachSegs.Contains(("EW", i, j)) ? "xx" : "==";
                        continue;
                    }
                    if (so == no) continue;
                    var fl = so ? s : n;
                    if (!brick.Contains(fl)) continue;
                    ew[(i, j)] = so ? (Height(i, j) == 'F' ? "##" : "==") : "==";
                }
            for (int i = 1; i < nc; i++)
                for (int r = 0; r < nr; r++)
                {
                    var w = (i - 1, r); var e = (i, r);
                    bool wo = open.Contains(w), eo = open.Contains(e);
                    if (wo && eo)
                    {
                        if (brick.Contains(w) != brick.Contains(e)) ns[(i, r)] = breachSegs.Contains(("NS", i, r)) ? "x" : ":";
                        continue;
                    }
                    if (wo == eo) continue;
                    var fl = wo ? w : e; var rk = wo ? e : w;
                    if (!brick.Contains(fl)) continue;
                    ns[(i, r)] = Height(rk.Item1, rk.Item2) == 'F' ? "#" : ":";
                }
            // the heads: a culvert under the end wall (its walkways' end walls full beside it), an outfall in a full north wall
            foreach (var (cell, d) in heads)
            {
                var (c, r) = cell;
                if (d == (1, 0) || d == (-1, 0))
                {
                    int i = d.Item1 > 0 ? c + 1 : c;
                    ns[(i, r)] = "1";
                    foreach (var rr in new[] { r - 1, r + 1 }) if (ns.ContainsKey((i, rr))) ns[(i, rr)] = "#";
                }
                else if (d == (0, 1)) ew[(c, r + 1)] = Height(c, r + 1) == 'F' && ew.TryGetValue((c, r + 1), out var t) && t == "##" ? "S2" : "s1";
                else ew[(c, r)] = "s1";
            }
            ew[(ladder.Item1, ladder.Item2 + 1)] = "S1";
            passages[$"EW|{ladder.Item1}|{ladder.Item2 + 1}"] = o.upId;
            ways.Add(ladder);
            foreach (var (ori, line, at, both) in cross)
            {
                if (ori == "NS")
                {
                    ns[(line, at)] = "1"; ns[(line, at + 1)] = "d"; ns[(line, at - 1)] = both ? "d" : "#";
                    foreach (var r in both ? new[] { at - 1, at + 1 } : new[] { at + 1 }) { doorCells.Add((line - 1, r)); doorCells.Add((line, r)); }
                }
                else
                {
                    ew[(at, line)] = "s1"; ew[(at - 1, line)] = "dd"; ew[(at + 1, line)] = both ? "dd" : "==";
                    foreach (var c in both ? new[] { at - 1, at + 1 } : new[] { at - 1 }) { doorCells.Add((c, line - 1)); doorCells.Add((c, line)); }
                }
            }
            ways.UnionWith(doorCells);

            // ---- the walk: open floor (water only on a bridge's deck, across it), the walls between cells (doors and
            // breaches pass)
            var bridges = new Dictionary<(int, int), (int, int)>();      // a channel cell -> the deck's axis
            var blocked = new HashSet<(int, int)>();                     // furniture
            bool Blocks(string t) => !string.IsNullOrWhiteSpace(t) && t != "dd" && t != "d" && t != "xx" && t != "XX" && t != "x" && t != "X";
            bool Pass((int, int) a, (int, int) b)
            {
                if (a.Item1 == b.Item1) return !(ew.TryGetValue((a.Item1, Math.Max(a.Item2, b.Item2)), out var t) && Blocks(t));
                return !(ns.TryGetValue((Math.Max(a.Item1, b.Item1), a.Item2), out var u) && Blocks(u));
            }
            bool Walk((int, int) q) => open.Contains(q) && (!water.Contains(q) || bridges.ContainsKey(q)) && !blocked.Contains(q);
            IEnumerable<(int, int)> Steps((int, int) q)
            {
                foreach (var d in D4)
                {
                    var p = Add(q, d);
                    if (!Walk(p) || !Pass(q, p)) continue;
                    if (bridges.TryGetValue(q, out var ax) && d != ax && d != Neg(ax)) continue;
                    if (bridges.TryGetValue(p, out var ax2) && d != ax2 && d != Neg(ax2)) continue;
                    yield return p;
                }
            }
            Dictionary<(int, int), int> Reach((int, int) start)
            {
                var dd = new Dictionary<(int, int), int> { [start] = 0 };
                var qq = new Queue<(int, int)>(); qq.Enqueue(start);
                while (qq.Count > 0) { var q = qq.Dequeue(); foreach (var p in Steps(q)) if (!dd.ContainsKey(p)) { dd[p] = dd[q] + 1; qq.Enqueue(p); } }
                return dd;
            }
            int WalkCount() => open.Count(Walk);

            // ---- bridges: a slab across a straight stretch of channel (walkway both sides, no wall on its stretch, clear
            // of the heads and other bridges); first as few as join every walkway, then one every few strides
            var comp = new Dictionary<(int, int), int>();
            foreach (var q in Sorted(open.Where(Walk)))
            {
                if (comp.ContainsKey(q)) continue;
                int id = comp.Count == 0 ? 0 : comp.Values.Max() + 1;
                foreach (var p in Reach(q).Keys) comp[p] = id;
            }
            var parent = comp.Values.Distinct().ToDictionary(v => v, v => v);
            int Find(int v) { while (parent[v] != v) v = parent[v] = parent[parent[v]]; return v; }
            var headCells = new HashSet<(int, int)>(heads.Select(h => h.cell));
            var bridgeCands = new List<((int, int) cell, (int, int) ax)>();
            foreach (var w in Sorted(water))
                foreach (var (along, ax) in new[] { ((1, 0), (0, 1)), ((0, 1), (1, 0)) })
                {
                    if (!water.Contains(Add(w, along)) || !water.Contains(Add(w, Neg(along)))) continue;
                    if (!Walkway(Add(w, ax)) || !Walkway(Add(w, Neg(ax))) || !InBrickWalk(w)) continue;
                    if (!Pass(w, Add(w, ax)) || !Pass(w, Add(w, Neg(ax)))) continue;
                    if (!Pass(w, Add(w, along)) || !Pass(w, Add(w, Neg(along)))) continue;            // a culvert beside it
                    if (headCells.Any(h => Math.Abs(h.Item1 - w.Item1) + Math.Abs(h.Item2 - w.Item2) <= 1)) continue;
                    if (Math.Abs(w.Item1 - ladder.Item1) + Math.Abs(w.Item2 - ladder.Item2) <= 1) continue;
                    bridgeCands.Add((w, ax));
                }
            bool InBrickWalk((int, int) w) => brick.Contains(w);
            bool NearBridge((int, int) w, int k) => bridges.Keys.Any(b => Math.Max(Math.Abs(b.Item1 - w.Item1), Math.Abs(b.Item2 - w.Item2)) <= k);
            foreach (var (w, ax) in bridgeCands.OrderBy(_ => rnd.Next()))
            {
                if (NearBridge(w, 1)) continue;
                int a = Find(comp[Add(w, ax)]), b = Find(comp[Add(w, Neg(ax))]);
                if (a == b) continue;
                bridges[w] = ax; parent[a] = b;
            }
            foreach (var (w, ax) in bridgeCands.OrderBy(_ => rnd.Next()))
                if (!NearBridge(w, 5) && rnd.NextDouble() < 0.7) bridges[w] = ax;
            foreach (var b in bridges) { ways.Add(Add(b.Key, b.Value)); ways.Add(Add(b.Key, Neg(b.Value))); }
            var walk0 = Reach(ladder);
            int lost = WalkCount() - walk0.Count;
            if (lost > 0) notes.Add($"{lost} walkway cells out of reach of the ladder");

            // ---- the lair: the grotto farthest from the ladder (its nearest cell); its point of interest on a free 2 x 2
            // block with a clear ring, nearest its middle
            var props = new JArray();
            var codes = new Dictionary<(int, int), string>();
            var NH = new JObject { ["hug"] = false };
            var reserved = new HashSet<(int, int)>(ways);
            int lair = -1;
            if (nGrottoes > 0)
                lair = Enumerable.Range(0, nGrottoes).OrderByDescending(g => grotto.Where(kv => kv.Value == g).Select(kv => walk0.TryGetValue(kv.Key, out var v) ? v : 0).DefaultIfEmpty(0).Min()).First();
            List<(int, int)> CellsOf(int g) => Sorted(grotto.Where(kv => kv.Value == g).Select(kv => kv.Key));
            (float, float) Mid(List<(int, int)> cs) => ((float)cs.Average(q => q.Item1), (float)cs.Average(q => q.Item2));
            (int, int)? poiAt = null;
            if (lair >= 0 && !string.IsNullOrEmpty(o.poi))
            {
                var cs = CellsOf(lair); var set = new HashSet<(int, int)>(cs); var (mx, my) = Mid(cs);
                // a 2 x 2 block of the lair's free floor, those with the most floor round them first, then nearest its middle;
                // the first that leaves the walk whole
                int Ring((int, int) p) => Enumerable.Range(-1, 4).Sum(a => Enumerable.Range(-1, 4).Count(b => set.Contains((p.Item1 + a, p.Item2 + b))));
                var spots = cs.Where(p => new[] { p, (p.Item1 + 1, p.Item2), (p.Item1, p.Item2 + 1), (p.Item1 + 1, p.Item2 + 1) }.All(q => set.Contains(q) && !reserved.Contains(q)))
                              .OrderByDescending(p => Mathf.Min(Ring(p), 14)).ThenBy(p => Math.Abs(p.Item1 + 0.5f - mx) + Math.Abs(p.Item2 + 0.5f - my)).ToList();
                foreach (var sp in spots)
                {
                    var blk = new[] { sp, (sp.Item1 + 1, sp.Item2), (sp.Item1, sp.Item2 + 1), (sp.Item1 + 1, sp.Item2 + 1) };
                    int before = Reach(ladder).Count;
                    foreach (var q in blk) blocked.Add(q);
                    if (Reach(ladder).Count < before - 4) { foreach (var q in blk) blocked.Remove(q); continue; }
                    foreach (var q in blk) codes[q] = "@@";
                    props.Add(new JArray(o.poi, IG * (sp.Item1 + 1), IG * (sp.Item2 + 1), 0, null, null, NH.DeepClone()));
                    poiAt = sp;
                    foreach (var q in blk) foreach (var d in D4) reserved.Add(Add(q, d));
                    break;
                }
                if (poiAt == null) notes.Add($"no room for {o.poi} in the lair");
            }

            // ---- the way on down: a tunnel in a straight full rock face north of a grotto (the lair's first), two cells
            // of floor in front of it; else a passage in a north wall with two cells of walkway in front
            var tunnels = new JObject();
            if (!string.IsNullOrEmpty(o.deep))
            {
                bool done = false;
                foreach (var g in Enumerable.Range(0, nGrottoes).OrderBy(g => g == lair ? 0 : 1))
                {
                    var set = new HashSet<(int, int)>(CellsOf(g));
                    var cand = new List<(int, int)>();
                    foreach (var p in CellsOf(g))
                    {
                        var (c, r) = p;                                  // node (c + 1, r + 1): cells (c, r) and (c + 1, r) open in front
                        var front = new[] { (c, r), (c + 1, r) };
                        var under = new[] { (c, r - 1), (c + 1, r - 1) };
                        var rock = new[] { (c, r + 1), (c + 1, r + 1) };
                        if (!front.All(set.Contains) || !under.All(q => set.Contains(q)) || !rock.All(IsRock)) continue;
                        if (rock.Any(q => Height(q.Item1, q.Item2) != 'F') || front.Concat(under).Any(reserved.Contains)) continue;
                        cand.Add(p);
                    }
                    var at = cand.OrderBy(p => Math.Abs(p.Item1 - Mid(CellsOf(g)).Item1)).Cast<(int, int)?>().FirstOrDefault();
                    if (at.HasValue)
                    {
                        var t = at.Value;
                        tunnels[$"{t.Item1 + 1}|{t.Item2 + 1}"] = o.deepId;
                        foreach (var q in new[] { t, (t.Item1 + 1, t.Item2) }) { codes[q] = "Sx"; reserved.Add(q); }
                        reserved.Add((t.Item1, t.Item2 - 1)); reserved.Add((t.Item1 + 1, t.Item2 - 1));
                        done = true; break;
                    }
                }
                if (!done)
                {
                    var far = Sorted(brick.Where(q => Walkway(q) && Walkway((q.Item1, q.Item2 - 1)) && ew.TryGetValue((q.Item1, q.Item2 + 1), out var t) && (t == "##")
                                                    && !reserved.Contains(q) && !reserved.Contains((q.Item1, q.Item2 - 1))))
                              .OrderByDescending(q => walk0.TryGetValue(q, out var v) ? v : -1).FirstOrDefault();
                    if (walk0.ContainsKey(far))
                    {
                        ew[(far.Item1, far.Item2 + 1)] = "PP";
                        passages[$"EW|{far.Item1}|{far.Item2 + 1}"] = o.deepId;
                        reserved.Add(far); reserved.Add((far.Item1, far.Item2 - 1));
                    }
                    else notes.Add("no place for the way down");
                }
            }

            // ---- furniture where the walk allows it: glowing mushrooms, a boulder, crystals along the grottoes' rock; barrels
            // and crates against the chambers' walls; refuse and bones round the lair (walked over)
            bool TryBlock((int, int) q, string code)
            {
                if (!Walk(q) || reserved.Contains(q) || codes.ContainsKey(q) || bridges.ContainsKey(q)) return false;
                int before = Reach(ladder).Count;
                blocked.Add(q);
                if (Reach(ladder).Count < before - 1) { blocked.Remove(q); return false; }
                codes[q] = code;
                foreach (var d in D4) reserved.Add(Add(q, d));
                return true;
            }
            for (int g = 0; g < nGrottoes; g++)
            {
                var cs = CellsOf(g);
                var edge = cs.Where(p => D4.Any(d => IsRock(Add(p, d)))).OrderBy(_ => rnd.Next()).ToList();
                int mg = Mathf.Max(1, cs.Count / 8), placedMg = 0, placedB = 0, placedC = 0;
                foreach (var p in edge)
                {
                    if (placedMg < mg && TryBlock(p, "MG")) { placedMg++; continue; }
                    if (placedB < 1 && rnd.NextDouble() < 0.5 && TryBlock(p, "BD")) { placedB++; continue; }
                    if (placedC < 1 && rnd.NextDouble() < 0.25 && TryBlock(p, "CR")) placedC++;
                }
                int flat = g == lair ? 4 : 1;
                foreach (var p in cs.Where(p => Walk(p) && !reserved.Contains(p) && !codes.ContainsKey(p)).OrderBy(_ => rnd.Next()).Take(flat))
                    codes[p] = g == lair && rnd.NextDouble() < 0.4 ? "bo" : "rf";
            }
            foreach (var kv in chambers)
            {
                var (x, y) = At(kv.Key);
                var (hw, hh, _) = kv.Value;
                var rim = Sorted(Enumerable.Range(x - hw, 2 * hw + 1).SelectMany(c => Enumerable.Range(y - hh, 2 * hh + 1).Select(r => (c, r))))
                          .Where(p => Walkway(p) && D4.Any(d => IsRock(Add(p, d))) && !D4.Any(d => water.Contains(Add(p, d)))).OrderBy(_ => rnd.Next()).ToList();
                int n = 0, want2 = 2 + rnd.Next(3);
                foreach (var p in rim) { if (n >= want2) break; if (TryBlock(p, rnd.NextDouble() < 0.5 ? "ba" : "bx")) n++; }
            }
            // flat dressing on the walkways: puddles, drain grates; sludge (record props, off the cell's middle)
            var walkways = Sorted(brick.Where(q => Walkway(q) && !reserved.Contains(q) && !codes.ContainsKey(q) && !blocked.Contains(q)));
            foreach (var p in walkways.OrderBy(_ => rnd.Next()).Take(walkways.Count / 28)) codes[p] = "pd";
            foreach (var p in walkways.Where(p => !codes.ContainsKey(p) && D4.Any(d => water.Contains(Add(p, d)))).OrderBy(_ => rnd.Next()).Take(walkways.Count / 40)) codes[p] = "dg";
            foreach (var p in walkways.Where(p => !codes.ContainsKey(p)).OrderBy(_ => rnd.Next()).Take(walkways.Count / 22))
                props.Add(new JArray("Overlay_Sludge", Math.Round(X(p) + (rnd.NextDouble() - 0.5) * 0.6, 2), Math.Round(Y(p) + (rnd.NextDouble() - 0.5) * 0.6, 2),
                                     rnd.Next(4) * 90, null, null, NH.DeepClone()));

            // ---- bridges and sluice gates (record props): a bridge's slab spans its axis (rot 0 over an east-west channel);
            // a gate across a straight stretch of a branch, clear of the bridges (rot 0 across a south-north channel)
            foreach (var b in bridges.OrderBy(k => k.Key.Item1).ThenBy(k => k.Key.Item2))
                props.Add(new JArray("Bridge_Sewer", X(b.Key), Y(b.Key), b.Value == (0, 1) ? 0 : 90, null, null, NH.DeepClone()));
            int sluices = 0;
            foreach (var (w, ax) in bridgeCands.Where(bc => !bridges.ContainsKey(bc.cell) && !NearBridge(bc.cell, 2) && !InChamber(bc.cell) && bc.cell.Item2 != GY[trunk])
                                               .OrderBy(bc => bc.ax == (1, 0) ? 0 : 1).ThenBy(_ => rnd.Next()))
            {
                if (sluices >= Mathf.Max(1, heads.Count / 2)) break;
                if (props.OfType<JArray>().Any(pp => (string)pp[0] == "Sluice" && Math.Abs((float)pp[1] - X(w)) + Math.Abs((float)pp[2] - Y(w)) < 9f)) continue;
                props.Add(new JArray("Sluice", X(w), Y(w), ax == (1, 0) ? 0 : 90, null, null, NH.DeepClone()));
                sluices++;
            }
            // torches on the full north walls, every fourth cell or so, not over the specials
            foreach (var kv in ew.Where(kv => kv.Value == "##").OrderBy(kv => kv.Key.Item1).ThenBy(kv => kv.Key.Item2))
            {
                var (i, j) = kv.Key;
                var below = (i, j - 1);
                if (!Walkway(below) || (i + 2 * j) % 4 != 0) continue;
                if (new[] { i - 1, i + 1 }.Any(k => ew.TryGetValue((k, j), out var t) && t != "##" && t != "==")) continue;
                props.Add(new JArray("Torch_Wall", X(below), Y(below), 0, null, "wall_hung"));
            }

            // ---- encounters: every grotto (the lair's the boss, by its throne) and chamber, the rest spread along the
            // tunnels at least eight strides from the ladder; each its spawn points within three strides, the budget
            // growing with the walk from the ladder
            var walk = Reach(ladder);
            // a spawn point: walked floor off the doorways, breaches and bridges (beside furniture is fine; walked-over dressing too)
            var flatCodes = new HashSet<string> { "pd", "dg", "rf", "bo" };
            bool Spot((int, int) q) => walk.ContainsKey(q) && !ways.Contains(q) && !bridges.ContainsKey(q) && !water.Contains(q) && q != ladder &&
                                       (!codes.TryGetValue(q, out var cq) || flatCodes.Contains(cq));
            (int, int)? Nearest(IEnumerable<(int, int)> cells, float mx, float my) =>
                cells.Where(Spot).OrderBy(q => Math.Abs(q.Item1 - mx) + Math.Abs(q.Item2 - my)).Cast<(int, int)?>().FirstOrDefault();
            var sites = new List<((int, int) at, string room, bool boss, int[] box)>();
            for (int g = 0; g < nGrottoes; g++)
            {
                var cs = CellsOf(g); var (mx, my) = Mid(cs);
                if (g == lair && poiAt.HasValue) { mx = poiAt.Value.Item1 + 0.5f; my = poiAt.Value.Item2 + 0.5f; }
                var at = Nearest(cs, mx, my);
                if (at.HasValue)
                    sites.Add((at.Value, g == lair ? "lair" : "grotto", g == lair, new[] { cs.Min(q => q.Item1), cs.Min(q => q.Item2), cs.Max(q => q.Item1) + 1, cs.Max(q => q.Item2) + 1 }));
            }
            foreach (var kv in chambers.OrderBy(k => k.Key.Item1).ThenBy(k => k.Key.Item2))
            {
                var (x, y) = At(kv.Key); var (hw, hh, cis) = kv.Value;
                var cs = Enumerable.Range(x - hw, 2 * hw + 1).SelectMany(c => Enumerable.Range(y - hh, 2 * hh + 1).Select(r => (c, r))).ToList();
                var at = Nearest(cs, x + (cis ? 2 : 0), y + 1);
                if (at.HasValue) sites.Add((at.Value, cis ? "cistern" : "hall", false, new[] { x - hw, y - hh, x + hw + 1, y + hh + 1 }));
            }
            int total = o.encounters > 0 ? o.encounters : Mathf.Clamp(walk.Count / 40, 4, 14);
            var tunnelSpots = Sorted(brick.Where(q => Spot(q) && walk[q] >= 8));
            while (sites.Count < total)
            {
                var pick = tunnelSpots.Where(q => sites.All(s => Math.Abs(s.at.Item1 - q.Item1) + Math.Abs(s.at.Item2 - q.Item2) >= 7))
                                      .OrderByDescending(q => Math.Min(walk[q] / 2, sites.Select(s => Math.Abs(s.at.Item1 - q.Item1) + Math.Abs(s.at.Item2 - q.Item2)).DefaultIfEmpty(99).Min()) + rnd.NextDouble())
                                      .Cast<(int, int)?>().FirstOrDefault();
                if (pick == null) break;
                var p = pick.Value;
                sites.Add((p, "sewer", false, new[] { p.Item1 - 2, p.Item2 - 2, p.Item1 + 3, p.Item2 + 3 }));
            }
            var encounters = new JArray();
            int k2 = 0;
            foreach (var (at, room, boss, box) in sites.OrderBy(s => walk.TryGetValue(s.at, out var v) ? v : 0))
            {
                int d0 = walk.TryGetValue(at, out var dv) ? dv : 0;
                int budget = 1 + d0 / 12 + (boss ? 3 : 0);
                // spawn points: within three strides of the site, spread
                var near = new Dictionary<(int, int), int> { [at] = 0 };
                var qq = new Queue<(int, int)>(); qq.Enqueue(at);
                while (qq.Count > 0) { var q = qq.Dequeue(); if (near[q] >= 3) continue; foreach (var p in Steps(q)) if (!near.ContainsKey(p) && !water.Contains(p)) { near[p] = near[q] + 1; qq.Enqueue(p); } }
                var free = Sorted(near.Keys.Where(Spot));
                var pts = new List<(int, int)> { at };
                while (pts.Count < Math.Min(free.Count, Math.Min(6, 1 + budget)))
                    pts.Add(free.OrderByDescending(q => pts.Min(p => Math.Abs(p.Item1 - q.Item1) + Math.Abs(p.Item2 - q.Item2))).First());
                encounters.Add(new JObject
                {
                    ["id"] = $"{room}{k2++}", ["room"] = room, ["creature"] = boss ? o.boss : o.creature,
                    ["budget"] = budget, ["boss"] = boss, ["depth"] = d0 / 8,
                    ["box"] = new JArray(IG * box[0], IG * box[1], IG * box[2], IG * box[3]),
                    ["points"] = new JArray(pts.Select(q => new JArray(X(q), Y(q)))),
                });
            }

            // ---- the plan's codes and the zones: the brick (walkways and water: sewer paving and brick), each grotto (cave
            // floor), the rock
            foreach (var q in Enumerable.Range(0, nc).SelectMany(c => Enumerable.Range(0, nr).Select(r => (c, r))))
                if (!open.Contains(q)) codes[q] = "##";
                else if (water.Contains(q)) codes[q] = "ww";
            JArray Boxes(IEnumerable<(int, int)> cells)
            {
                var a = new JArray();
                foreach (var row in cells.GroupBy(q => q.Item2).OrderBy(gr => gr.Key))
                {
                    var cs = row.Select(q => q.Item1).OrderBy(c => c).ToList();
                    int s = cs[0], prev = cs[0];
                    foreach (var c in cs.Skip(1).Append(int.MaxValue))
                    {
                        if (c == prev + 1) { prev = c; continue; }
                        a.Add(new JArray(s, prev, row.Key, row.Key));
                        s = prev = c;
                    }
                }
                return a;
            }
            var zones = new JObject { ["sewer"] = new JObject { ["cells"] = Boxes(brick), ["floor"] = "SewerFloor", ["wall"] = "SewerBrick" } };
            for (int g = 0; g < nGrottoes; g++) zones[g == lair ? "lair" : $"grotto{g}"] = new JObject { ["cells"] = Boxes(CellsOf(g)), ["floor"] = "CaveFloor" };
            zones["rock"] = new JObject { ["cells"] = "rest", ["floor"] = "CaveFloor" };
            var links = new JArray();
            var up = new JArray(o.upId, "passage", o.upTarget); if (!string.IsNullOrEmpty(o.upArrive)) up.Add(o.upArrive);
            links.Add(up);
            if (!string.IsNullOrEmpty(o.deep)) { var dn = new JArray(o.deepId, "passage", o.deep); if (!string.IsNullOrEmpty(o.deepArrive)) dn.Add(o.deepArrive); links.Add(dn); }
            var R = new JObject
            {
                ["building"] = "Sewer", ["floor"] = -1, ["preset"] = "Sewer",
                ["family"] = new JObject { ["perimeter"] = "Cave", ["partition"] = "Sewer" },
                ["cave"] = true, ["pools"] = false, ["rush_mats"] = false, ["partition_wall"] = "zone",
                ["specials"] = new JObject { ["S1"] = "Wall_Sewer_Ladder_150_Full", ["S2"] = "Wall_Sewer_Outfall_150_Full",
                                             ["s1"] = "Wall_Sewer_Culvert_150_Cut", ["1"] = "Wall_Sewer_Culvert_150_Full" },
                ["passages"] = passages, ["tunnels"] = tunnels, ["channel_sinks"] = sinks,
                ["zones"] = zones, ["links"] = links, ["props"] = props, ["props_from_codes"] = true,
                ["encounters"] = encounters,
                ["debris"] = new JObject { ["density"] = o.debris, ["seed"] = o.seed },
                ["generated"] = new JObject { ["generator"] = "sewer", ["seed"] = o.seed, ["nc"] = nc, ["nr"] = nr, ["notes"] = new JArray(notes) },
            };
            return (KitDungeonGenerator.Plan(nc, nr, codes, ew, ns), R);
        }
    }
}
