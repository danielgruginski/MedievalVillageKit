using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A random cave level (vki_rooms_adventure.vki_cave_generate, in outline): a cellular automaton over random rock
    /// (44 %) with a meandering passage carved west to east and a few round chambers; five smoothing passes; passages
    /// at least two cells wide; the largest open region kept. A chasm winds west-east with a rope bridge (and natural
    /// land bridges where it would cut the cave in two), pools, cave dressing, a tunnel in the west and east walls, an
    /// optional point of interest. The result is a plan and a room record for <see cref="KitRoom"/>.
    /// </summary>
    public static class KitCaveGenerator
    {
        [Serializable]
        public class Options
        {
            public int nc = 24, nr = 16, seed = 7, pools = 2, props = 18;
            public bool chasm = true;
            public string poi;              // e.g. "POI_WyrmBones": a w x h point of interest near the centre
            public int poiW = 2, poiH = 2;
            public string poiCode = "WY";
        }

        const float IG = 1.5f;

        static float VNoise(float u, float w, int seed)
        {
            int i0 = Mathf.FloorToInt(u), j0 = Mathf.FloorToInt(w);
            float fu = u - i0, fw = w - j0, su = fu * fu * (3 - 2 * fu), sw = fw * fw * (3 - 2 * fw);
            float a = (float)KitRoomLayout.Hash01(i0, j0, seed), b = (float)KitRoomLayout.Hash01(i0 + 1, j0, seed);
            float c = (float)KitRoomLayout.Hash01(i0, j0 + 1, seed), d = (float)KitRoomLayout.Hash01(i0 + 1, j0 + 1, seed);
            return Mathf.Lerp(Mathf.Lerp(a, b, su), Mathf.Lerp(c, d, su), sw);
        }

        /// <summary>vki_rooms_mkplan: an ASCII plan from cell codes (frame walls "##" / "==" / "#" / "t")</summary>
        public static string MakePlan(int nc, int nr, Dictionary<(int, int), string> codes)
        {
            var sb = new StringBuilder("\n      " + string.Join(" ", Enumerable.Range(0, nc).Select(i => i.ToString().PadLeft(2))) + "\n");
            for (int j = nr; j >= 0; j--)
            {
                sb.Append("     +");
                for (int i = 0; i < nc; i++)
                {
                    string tok = j == nr ? "##" : j == 0 ? "==" : "  ";
                    sb.Append(tok).Append(j == 0 || j == nr || i == nc - 1 ? "+" : " ");
                }
                sb.Append('\n');
                if (j == 0) break;
                int r = j - 1;
                sb.Append("  ").Append(r.ToString().PadLeft(2)).Append(' ');
                for (int i = 0; i <= nc; i++)
                {
                    sb.Append(i == 0 || i == nc ? (r == 0 ? "t" : "#") : " ");
                    if (i < nc) sb.Append(codes.TryGetValue((i, r), out var c) ? c : "..");
                }
                sb.Append('\n');
            }
            return sb.ToString();
        }

        public static (string plan, JObject record) Generate(Options o)
        {
            var rnd = new System.Random(o.seed);
            int nc = o.nc, nr = o.nr;
            var cells = new List<(int, int)>();
            for (int c = 0; c < nc; c++) for (int r = 0; r < nr; r++) cells.Add((c, r));
            var rock = cells.ToDictionary(p => p, p => rnd.NextDouble() < 0.44);
            var carved = new HashSet<(int, int)>();
            int y = rnd.Next(nr / 3, 2 * nr / 3 + 1);
            int[] steps = { -1, 0, 0, 1 };
            for (int c = 0; c < nc; c++)                              // the main passage, west edge to east edge
            {
                y = Mathf.Clamp(y + steps[rnd.Next(4)], 2, nr - 3);
                for (int d = -1; d <= 1; d++) carved.Add((c, y + d));
            }
            for (int k = 0; k < Mathf.Max(2, nc * nr / 90); k++)     // round chambers
            {
                double cx = 2 + rnd.NextDouble() * (nc - 5), cy = 2 + rnd.NextDouble() * (nr - 5), rad = 1.6 + rnd.NextDouble() * 1.6;
                foreach (var p in cells) if ((p.Item1 - cx) * (p.Item1 - cx) + ((p.Item2 - cy) * 1.2) * ((p.Item2 - cy) * 1.2) < rad * rad) carved.Add(p);
            }
            foreach (var p in carved) rock[p] = false;
            bool IsRock(int c, int r) => !(c >= 0 && c < nc && r >= 0 && r < nr) || rock[(c, r)];
            for (int pass = 0; pass < 5; pass++)
            {
                var nw = new Dictionary<(int, int), bool>();
                foreach (var (c, r) in cells)
                {
                    int n = 0;
                    for (int dc = -1; dc <= 1; dc++) for (int dr = -1; dr <= 1; dr++) if ((dc != 0 || dr != 0) && IsRock(c + dc, r + dr)) n++;
                    nw[(c, r)] = !carved.Contains((c, r)) && (n >= 5 || (n > 3 && rock[(c, r)]));
                }
                rock = nw;
            }
            for (int pass = 0; pass < 4; pass++)                      // two-cell passages: an open cell needs a 2 x 2 open block
            {
                var keep = new HashSet<(int, int)>();
                foreach (var (c, r) in cells)
                {
                    if (rock[(c, r)]) continue;
                    for (int dc = -1; dc <= 0; dc++)
                        for (int dr = -1; dr <= 0; dr++)
                        {
                            var blk = new[] { (c + dc, r + dr), (c + dc + 1, r + dr), (c + dc, r + dr + 1), (c + dc + 1, r + dr + 1) };
                            if (blk.All(q => !IsRock(q.Item1, q.Item2))) foreach (var q in blk) keep.Add(q);
                        }
                }
                rock = cells.ToDictionary(p => p, p => !keep.Contains(p));
            }
            var big = Largest(cells.Where(p => !rock[p]));
            rock = cells.ToDictionary(p => p, p => !big.Contains(p));
            var codes = cells.Where(p => rock[p]).ToDictionary(p => p, p => "##");
            var xs = new HashSet<(int, int)>();
            (int, int)? bridge = null;
            if (o.chasm)                                               // a connected winding path, one or two cells wide
            {
                int c0 = (int)(nc * 0.08), c1 = (int)(nc * 0.92);
                double yy = nr / 2.0 + (rnd.NextDouble() * 2 - 1), ph = rnd.NextDouble() * 6.3;
                HashSet<int> prev = null;
                for (int c = c0; c < c1; c++)
                {
                    double want = nr / 2.0 + 0.25 * nr * Math.Sin((c - c0) * 0.38 + ph);
                    yy += Math.Max(-1.0, Math.Min(1.0, want - yy));
                    int w = VNoise(c * 0.45f, 0.3f, o.seed) > 0.4f ? 2 : 1;
                    int r0 = (int)Math.Round(yy - (w - 1) / 2.0);
                    var rows = new HashSet<int>(Enumerable.Range(r0, w));
                    if (prev != null && !prev.Overlaps(rows))
                        for (int r = Math.Min(prev.Max(), rows.Max()); r <= Math.Max(prev.Min(), rows.Min()); r++) rows.Add(r);
                    foreach (var r in rows) if (big.Contains((c, r))) xs.Add((c, r));
                    prev = rows;
                }
                foreach (var c in Enumerable.Range(0, nc).OrderBy(c => Math.Abs(c - nc / 2.0)))
                {
                    var col = xs.Where(q => q.Item1 == c).Select(q => q.Item2).OrderBy(r => r).ToList();
                    if (col.Count == 2 && col[1] == col[0] + 1)
                    {
                        int r = col[0];
                        var land = from a in new[] { -1, 0, 1 } from q in new[] { r - 2, r - 1, r + 2, r + 3 } select (c + a, q);
                        if (land.All(q => big.Contains(q) && !xs.Contains(q))) { bridge = (c, r); break; }
                    }
                }
                if (bridge == null && xs.Count > 0)                    // shape one column (and its landings) for the bridge
                {
                    int c = xs.Select(q => q.Item1).Distinct().OrderBy(cc => Math.Abs(cc - nc / 2.0)).First();
                    int r = Mathf.Clamp(xs.Where(q => q.Item1 == c).Min(q => q.Item2), 2, nr - 4);
                    xs.RemoveWhere(q => q.Item1 == c);
                    foreach (var a in new[] { -1, 0, 1 }) foreach (var q in new[] { r - 2, r - 1, r + 2, r + 3 }) xs.Remove((c + a, q));
                    for (int q = r - 2; q <= r + 3; q++)
                        foreach (var a in (q == r || q == r + 1) ? new[] { 0 } : new[] { -1, 0, 1 })
                            if (c + a >= 0 && c + a < nc && q >= 0 && q < nr) { big.Add((c + a, q)); rock[(c + a, q)] = false; codes.Remove((c + a, q)); }
                    xs.Add((c, r)); xs.Add((c, r + 1));
                    bridge = (c, r);
                }
                for (int k = 0; k < 6; k++)                           // natural land bridges: gaps in the chasm
                {
                    var fl = new HashSet<(int, int)>(big.Where(q => !xs.Contains(q)));
                    if (bridge is (int, int) b) { fl.Add(b); fl.Add((b.Item1, b.Item2 + 1)); }
                    var regs = Regions(fl).OrderByDescending(g => g.Count).ToList();
                    if (regs.Count < 2 || regs[1].Count < 4) break;
                    int? best = null;
                    foreach (var c in xs.Select(q => q.Item1).Distinct())
                    {
                        if (bridge is (int, int) bb && c == bb.Item1) continue;
                        var col = xs.Where(q => q.Item1 == c).ToList();
                        int lo = col.Min(q => q.Item2), hi = col.Max(q => q.Item2);
                        var ends = new[] { (c, lo - 1), (c, hi + 1) };
                        if (ends.Any(regs[0].Contains) && ends.Any(regs[1].Contains) && (best == null || Math.Abs(c - nc / 2.0) > Math.Abs(best.Value - nc / 2.0))) best = c;
                    }
                    if (best == null) break;
                    xs.RemoveWhere(q => q.Item1 == best.Value);
                }
                foreach (var p in xs) codes[p] = "vv";
                if (bridge is (int, int) br) codes[br] = codes[(br.Item1, br.Item2 + 1)] = "==";
            }
            bool NearX(int c, int r) { for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) if (xs.Contains((c + a, r + b))) return true; return false; }
            var clear = new HashSet<(int, int)>();
            if (bridge is (int, int) bl)
                foreach (var a in new[] { -1, 0, 1 }) foreach (var q in new[] { -2, -1, 2, 3 }) clear.Add((bl.Item1 + a, bl.Item2 + q));
            bool Free(int c, int r) => big.Contains((c, r)) && !xs.Contains((c, r)) && !clear.Contains((c, r)) && !codes.ContainsKey((c, r));
            var tunnels = new JObject();
            var links = new JArray();
            foreach (var (side, i, cs) in new[] { ("west", 0, new[] { 0, 1 }), ("east", nc, new[] { nc - 1, nc - 2 }) })
            {
                var js = Enumerable.Range(2, Math.Max(0, nr - 3)).Where(j => cs.All(c => Enumerable.Range(-2, 4).All(d => Free(c, j + d)))).ToList();
                if (js.Count == 0) continue;
                int jj = js.OrderBy(j => Math.Abs(j - nr / 2.0)).First();
                tunnels[$"{i}|{jj}"] = side;
                links.Add(new JArray(side, "passage", "@return"));
                foreach (var c in cs) for (int d = -2; d <= 1; d++) clear.Add((c, jj + d));
                codes[(cs[0], jj - 1)] = codes[(cs[0], jj)] = "Sx";
            }
            var plist = new JArray();
            var NH = new JObject { ["hug"] = false };
            if (bridge is (int, int) bp)
                plist.Add(new JArray("RopeBridge_420", IG * bp.Item1 + 0.75f, IG * (bp.Item2 + 1), 0, null, null, NH.DeepClone()));
            if (!string.IsNullOrEmpty(o.poi))                          // the point of interest: the open block nearest the centre
            {
                var blocks = cells.Where(p => Enumerable.Range(-1, o.poiW + 2).All(a => Enumerable.Range(-1, o.poiH + 2).All(b => Free(p.Item1 + a, p.Item2 + b))) &&
                                              !Enumerable.Range(0, o.poiW).Any(a => Enumerable.Range(0, o.poiH).Any(b => NearX(p.Item1 + a, p.Item2 + b)))).ToList();
                if (blocks.Count > 0)
                {
                    var (c, r) = blocks.OrderBy(q => Math.Pow(q.Item1 + o.poiW / 2.0 - nc / 2.0, 2) + Math.Pow(q.Item2 + o.poiH / 2.0 - nr / 2.0, 2)).First();
                    plist.Add(new JArray(o.poi, IG * (c + o.poiW / 2f), IG * (r + o.poiH / 2f), 0, null, null, NH.DeepClone()));
                    for (int a = 0; a < o.poiW; a++) for (int b = 0; b < o.poiH; b++) codes[(c + a, r + b)] = o.poiCode;
                }
            }
            var pits = new JArray();
            var used = new List<(int, int)>();
            var cand = cells.Where(p => Enumerable.Range(-1, 4).All(a => Enumerable.Range(-1, 4).All(b => Free(p.Item1 + a, p.Item2 + b))) &&
                                        !new[] { (0, 0), (1, 0), (0, 1), (1, 1) }.Any(d => NearX(p.Item1 + d.Item1, p.Item2 + d.Item2)))
                            .OrderBy(_ => rnd.Next()).ToList();
            foreach (var (c, r) in cand)
            {
                if (pits.Count >= o.pools) break;
                var blk = new[] { (c, r), (c + 1, r), (c, r + 1), (c + 1, r + 1) };
                if (blk.Any(q => used.Any(u => Math.Abs(q.Item1 - u.Item1) < 4 && Math.Abs(q.Item2 - u.Item2) < 4))) continue;
                pits.Add(new JArray("Pit_Pool_300x300", IG * c, IG * r));
                foreach (var q in blk) { codes[q] = "~~"; used.Add(q); }
            }
            var kinds = new[] { ("Crystals", "CR"), ("Mushrooms_Glow", "MG"), ("Stalagmites", "SM"), ("Boulders", "BD"), ("Overlay_Gravel", "gv"),
                                ("Crystals", "CR"), ("Stalagmites", "SM"), ("Mushrooms_Glow", "MG") };
            var spots = cells.Where(p => Enumerable.Range(-1, 3).All(a => Enumerable.Range(-1, 3).All(b => Free(p.Item1 + a, p.Item2 + b)))).OrderBy(_ => rnd.Next()).ToList();
            var placedAt = new List<(int, int)>();
            foreach (var (c, r) in spots)
            {
                if (placedAt.Count >= o.props) break;
                if (placedAt.Any(u => Math.Abs(c - u.Item1) + Math.Abs(r - u.Item2) < 4)) continue;
                var (piece, code) = kinds[placedAt.Count % kinds.Length];
                plist.Add(new JArray(piece, IG * (c + 0.5f), IG * (r + 0.5f), 0, null, null, NH.DeepClone()));
                codes[(c, r)] = code;
                placedAt.Add((c, r));
            }
            var R = new JObject
            {
                ["building"] = "Dungeon", ["floor"] = -9, ["preset"] = "Cavern",
                ["family"] = new JObject { ["perimeter"] = "Cave", ["partition"] = "Cave" },
                ["cave"] = true, ["pools"] = false,
                ["zones"] = new JObject { ["cavern"] = new JObject { ["cells"] = "rest", ["floor"] = "CaveFloor" } },
                ["tunnels"] = tunnels, ["links"] = links, ["pits"] = pits, ["props"] = plist,
                ["generated"] = new JObject { ["seed"] = o.seed, ["nc"] = nc, ["nr"] = nr },
            };
            return (MakePlan(nc, nr, codes), R);
        }

        static List<HashSet<(int, int)>> Regions(IEnumerable<(int, int)> open)
        {
            var set = new HashSet<(int, int)>(open);
            var seen = new HashSet<(int, int)>();
            var out_ = new List<HashSet<(int, int)>>();
            foreach (var p in set)
            {
                if (seen.Contains(p)) continue;
                var reg = new HashSet<(int, int)>();
                var todo = new Stack<(int, int)>();
                todo.Push(p); seen.Add(p);
                while (todo.Count > 0)
                {
                    var (c, r) = todo.Pop();
                    reg.Add((c, r));
                    foreach (var q in new[] { (c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1) })
                        if (set.Contains(q) && seen.Add(q)) todo.Push(q);
                }
                out_.Add(reg);
            }
            return out_;
        }

        static HashSet<(int, int)> Largest(IEnumerable<(int, int)> open) =>
            Regions(open).OrderByDescending(g => g.Count).FirstOrDefault() ?? new HashSet<(int, int)>();
    }
}
