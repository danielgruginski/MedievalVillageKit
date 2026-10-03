using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Cave maps (vki_rooms_adventure.vki_cave_layout): the plan is a cell map, "##" is rock and everything outside the
    /// map is rock. A rock tile stands on every node whose four cells are not all open (its corner code SW SE NE NW of
    /// O open / C cut rock / F full rock picks the master and its turn); walls on the map's inner grid lines are laid out
    /// like partitions, and the rock tiles on their nodes are the wall-backed ones. Chasm ("vv", "==" under a bridge) and
    /// stream ("ss") cells get dual-grid ground tiles, sewer ("ww") and lava ("ll") cells channel tiles; R["tunnels"]
    /// puts a tunnel (or a mine's adit) on a straight Full face; R["tracks"] lays a mine's track.
    /// </summary>
    public partial class KitRoomLayout
    {
        public class Rock { public string piece, code, tunnel, arms; public float x, y, rot; public (int, int) node; }
        public class Ground { public string piece, code, floorStyle; public float x, y, rot; public (int, int) node; public Vector2? flow; }

        public readonly List<Rock> rocks = new List<Rock>();
        public readonly List<Ground> grounds = new List<Ground>();
        public readonly JArray autoProps = new JArray();               // waterfalls, track tiles
        public Dictionary<(int, int), char> cells;
        public bool IsCave => (bool?)R["cave"] == true;

        const string Arms = "SENW";                                     // arm i runs from the node between corners i and i + 1

        static (int, int) Key(string k) { var a = k.Split('|'); return (int.Parse(a[0]), int.Parse(a[1])); }

        /// <summary>vki_cav_canon: the smallest rotation of a corner code; the master turned 90 k shows `code`</summary>
        public static (string m, int k) Canon(string code)
        {
            string best = null; int bk = 0;
            for (int k = 0; k < 4; k++)
            {
                var m = new string(Enumerable.Range(0, 4).Select(i => code[(i + k) % 4]).ToArray());
                if (best == null || string.CompareOrdinal(m, best) < 0) { best = m; bk = k; }
            }
            return (best, bk);
        }

        static (string m, string ma, int k) CanonArms(string code, string arms)
        {
            string bm = null, bma = null; int bk = 0;
            for (int k = 0; k < 4; k++)
            {
                var m = new string(Enumerable.Range(0, 4).Select(i => code[(i + k) % 4]).ToArray());
                var ma = new string(Enumerable.Range(0, 4).Where(i => arms.Contains(Arms[(i + k) % 4])).Select(i => Arms[i]).ToArray());
                int c = bm == null ? -1 : string.CompareOrdinal(m, bm);
                if (bm == null || c < 0 || (c == 0 && string.CompareOrdinal(ma, bma) < 0)) { bm = m; bma = ma; bk = k; }
            }
            return (bm, bma, bk);
        }

        static string ArmsOk(string code, string arms) =>
            new string(Enumerable.Range(0, 4).Where(i => arms.Contains(Arms[i]) && (code[i] == 'O' || code[(i + 1) % 4] == 'O')).Select(i => Arms[i]).ToArray());

        static int? RotOf(string master, string code)
        {
            for (int k = 0; k < 4; k++)
                if (Enumerable.Range(0, 4).All(i => master[i] == code[(i + k) % 4])) return k;
            return null;
        }

        static float Turn(int k) => (90 * k + 180) % 360 - 180;

        /// <summary>vki_hash01: integer lattice hash -> [0, 1], identical to the Blender kit's</summary>
        public static double Hash01(long ix, long iz, long seed)
        {
            ulong h = unchecked((ulong)(ix * 374761393L + iz * 668265263L + (seed & 0xFFFFFFFFL) * 2246822519L)) & 0xFFFFFFFFUL;
            h = ((h ^ (h >> 13)) * 1274126177UL) & 0xFFFFFFFFUL;
            h = (h ^ (h >> 16)) & 0xFFFFFFFFUL;
            return h / 4294967295.0;
        }

        void RunCave()
        {
            // the walls drawn inside the map (its frame only borders it), laid out like partitions
            var P2 = new KitRoomPlan { nc = nc, nr = nr };
            foreach (var kv in P.ew) P2.ew[kv.Key] = kv.Key.Item2 > 0 && kv.Key.Item2 < nr ? kv.Value : "  ";
            foreach (var kv in P.ns) P2.ns[kv.Key] = kv.Key.Item1 > 0 && kv.Key.Item1 < nc ? kv.Value : " ";
            foreach (var kv in P.codes) P2.codes[kv.Key] = kv.Value;
            var armsAt = new Dictionary<(int, int), string>();
            if (P2.ew.Values.Any(t => t.Trim().Length > 0) || P2.ns.Values.Any(t => t.Trim().Length > 0))
            {
                var R2 = (JObject)R.DeepClone();
                R2["cave"] = false; R2["open_frame"] = true;
                var W = Build(rules, R2, P2, fpCells);
                pieces.AddRange(W.pieces); posts.AddRange(W.posts); problems.AddRange(W.problems);
                foreach (var kv in W.segs) segs[kv.Key] = kv.Value;
                void Arm((int, int) n, char a) => armsAt[n] = (armsAt.TryGetValue(n, out var s) ? s : "") + a;
                foreach (var pc in W.pieces)
                    for (int d = 0; d < pc.n; d++)
                    {
                        if (pc.ori == "EW") { Arm((pc.k + d, pc.line), 'E'); Arm((pc.k + d + 1, pc.line), 'W'); }
                        else { Arm((pc.line, pc.k + d), 'N'); Arm((pc.line, pc.k + d + 1), 'S'); }
                    }
            }
            cells = CaveCells();
            CaveTiles(armsAt);
            var cov = CaveGround();
            var ccells = CaveChannels();
            pitCells = PitCells();
            stairCells = StairCells();
            var zones = (JObject)R["zones"];
            for (int c = 0; c < nc; c++)
                for (int r = 0; r < nr; r++)
                {
                    if (pitCells.ContainsKey((c, r)) || ccells.Contains((c, r))) continue;
                    if (stairCells.TryGetValue((c, r), out var sc) && sc.kind == "Down") continue;
                    string zn = zmap[(c, r)];
                    string fs = zn != null ? (string)zones[zn]?["floor"] : null;
                    if (!cov.TryGetValue((c, r), out var q))
                    {
                        floors.Add(new Floor { piece = $"SM_VKI_Floor_150_Q{c % 2}{r % 2}", x = IG * c, y = IG * r, zone = zn, floorStyle = fs });
                        continue;
                    }
                    for (int qa = 0; qa < 2; qa++)
                        for (int qb = 0; qb < 2; qb++)
                            if (!q.Contains((qa, qb)))
                                floors.Add(new Floor { piece = $"SM_VKI_Floor_075_R{(2 * c + qa) % 4}{(2 * r + qb) % 4}", x = IG * c + 0.75f * qa, y = IG * r + 0.75f * qb, zone = zn, floorStyle = fs });
                }
            if (R["tracks"] is JArray) MineTracks();
        }

        /// <summary>vki_cave_cells: 'O' open, else rock: Cut in the south ring and row, or with open floor within two
        /// cells to its north (a 3 m rock would hide it from the camera), else Full. The map plus a ring round it.
        /// Portals (<see cref="KitPortal"/>): beyond a map's opening the floor runs on (open) with cut rock the band
        /// either side; a connector's seam row is cut rock in the band and, past it, what the map beyond makes of its
        /// ring there (its south ring cut, the others full), so both maps agree on every cell they share.</summary>
        Dictionary<(int, int), char> CaveCells()
        {
            var beyondOpen = new HashSet<(int, int)>();
            var forced = new Dictionary<(int, int), char>();
            foreach (var pt in KitPortal.Of(R))
            {
                if (pt.at < 0) continue;
                char s = pt.Side;
                if (pt.seam)
                {
                    char ring = s == 'N' ? 'C' : 'F';            // the map beyond: its south ring is cut, the rest full
                    for (int k = 0; k < KitPortal.EdgeLength(s, nc, nr); k++) forced[pt.Cell(k, 0, nc, nr)] = ring;
                }
                for (int k = pt.at - KitPortal.Margin; k < pt.at + pt.width + KitPortal.Margin; k++)
                {
                    bool gap = k >= pt.at && k < pt.at + pt.width;
                    var q = pt.seam ? pt.Cell(k, 0, nc, nr) : pt.Beyond(k, nc, nr);
                    if (gap) { forced.Remove(q); if (!pt.seam) beyondOpen.Add(q); }
                    else forced[q] = 'C';
                }
            }
            bool IsRock(int c, int r) => !(c >= 0 && c < nc && r >= 0 && r < nr) ? !beyondOpen.Contains((c, r)) : (P.codes.TryGetValue((c, r), out var v) && v == "##");
            var ov = R["cave_heights"] as JObject;
            var o = new Dictionary<(int, int), char>();
            for (int c = -1; c <= nc; c++)
                for (int r = -1; r <= nr; r++)
                {
                    if (!IsRock(c, r)) { o[(c, r)] = 'O'; continue; }
                    var h = (string)ov?[$"{c}|{r}"];
                    if (h != null) { o[(c, r)] = h[0]; continue; }
                    if (forced.TryGetValue((c, r), out var fh)) { o[(c, r)] = fh; continue; }
                    bool south = r == -1 || (r == 0 && c >= 0 && c < nc);
                    o[(c, r)] = south || !IsRock(c, r + 1) || !IsRock(c, r + 2) ? 'C' : 'F';
                }
            return o;
        }

        string Corner(int i, int j) => new string(new[] { cells[(i - 1, j - 1)], cells[(i, j - 1)], cells[(i, j)], cells[(i - 1, j)] });

        /// <summary>vki_cave_tiles: one rock tile per node with rock round it (a variant by the node's hash), tunnels on
        /// their nodes, the wall-backed masters where walls meet the node</summary>
        void CaveTiles(Dictionary<(int, int), string> armsAt)
        {
            var tun = new Dictionary<(int, int), string>();
            if (R["tunnels"] is JObject tj) foreach (var kv in tj) tun[Key(kv.Key)] = (string)kv.Value;
            // a connector's seam lines: the map beyond builds the rock tiles there
            var seams = new HashSet<char>(KitPortal.Of(R).Where(pt => pt.seam).Select(pt => pt.Side));
            bool OnSeam(int i, int j) => (seams.Contains('S') && j == 0) || (seams.Contains('N') && j == nr) || (seams.Contains('W') && i == 0) || (seams.Contains('E') && i == nc);
            for (int i = 0; i <= nc; i++)
                for (int j = 0; j <= nr; j++)
                {
                    if (OnSeam(i, j)) continue;
                    string code = Corner(i, j);
                    tun.TryGetValue((i, j), out var lid);
                    tun.Remove((i, j));
                    if (code == "OOOO")
                    {
                        if (lid != null) problems.Add($"cave: tunnel {lid} at node ({i},{j}) has no rock");
                        continue;
                    }
                    if (armsAt.TryGetValue((i, j), out var a_) && a_.Length > 0)
                    {
                        string ok = ArmsOk(code, a_);
                        if (ok.Length < a_.Distinct().Count()) problems.Add($"cave: a wall at node ({i},{j}) runs into solid rock (corners {code}, arms {a_})");
                        if (lid != null) problems.Add($"cave: tunnel {lid} at node ({i},{j}) is on a wall");
                        if (ok.Length > 0)
                        {
                            var (m, ma, kk) = CanonArms(code, ok);
                            rocks.Add(new Rock { piece = $"SM_VKI_Rock_Cave_{m}_Wall{ma}", x = IG * i, y = IG * j, rot = Turn(kk), node = (i, j), code = code, arms = ok });
                            continue;
                        }
                    }
                    if (lid != null)
                    {
                        var kk = RotOf("OOFF", code);
                        if (kk == null) problems.Add($"cave: tunnel {lid} at node ({i},{j}) needs a straight Full face, corners {code}");
                        else
                        {
                            string kind = (string)R["tunnel_kinds"]?[lid] ?? "Tunnel";
                            rocks.Add(new Rock { piece = "SM_VKI_Rock_Cave_OOFF_" + kind, x = IG * i, y = IG * j, rot = Turn(kk.Value), node = (i, j), code = code, tunnel = lid });
                            continue;
                        }
                    }
                    var (mm, k) = Canon(code);
                    string vs = mm == "FFOO" || mm == "CCOO" ? "ABC" : "AB";
                    char v = vs[Mathf.Min(vs.Length - 1, (int)(Hash01(i, j, 91) * vs.Length))];
                    rocks.Add(new Rock { piece = $"SM_VKI_Rock_Cave_{mm}_{v}", x = IG * i, y = IG * j, rot = Turn(k), node = (i, j), code = code });
                }
            foreach (var kv in tun) problems.Add($"cave: tunnel {kv.Value} at node ({kv.Key.Item1},{kv.Key.Item2}) is off the map");
        }

        static readonly (int, int)[] Dirs4 = { (1, 0), (-1, 0), (0, 1), (0, -1) };

        /// <summary>vki_cave_flow: from the sinks, every reached water cell flows toward the neighbour one step nearer</summary>
        static Dictionary<(int, int), (int, int)> Flow(HashSet<(int, int)> water, JObject sinks, Dictionary<(int, int), (int, int)> extra = null)
        {
            var flow = new Dictionary<(int, int), (int, int)>();
            if (extra != null) foreach (var kv in extra) if (water.Contains(kv.Key)) flow[kv.Key] = kv.Value;
            if (sinks != null)
                foreach (var kv in sinks)
                {
                    var c = Key(kv.Key);
                    if (water.Contains(c) && !flow.ContainsKey(c)) flow[c] = ((int)kv.Value[0], (int)kv.Value[1]);
                }
            var todo = flow.Keys.ToList();
            while (todo.Count > 0)
            {
                var nxt = new List<(int, int)>();
                foreach (var c in todo)
                    foreach (var d in Dirs4)
                    {
                        var q = (c.Item1 + d.Item1, c.Item2 + d.Item2);
                        if (water.Contains(q) && !flow.ContainsKey(q)) { flow[q] = (-d.Item1, -d.Item2); nxt.Add(q); }
                    }
                todo = nxt;
            }
            return flow;
        }

        static Vector2? TileFlow(IEnumerable<(int, int)> cs, Dictionary<(int, int), (int, int)> flow)
        {
            float fx = 0, fy = 0;
            foreach (var c in cs) if (flow.TryGetValue(c, out var f)) { fx += f.Item1; fy += f.Item2; }
            var v = new Vector2(fx, fy);
            return v.magnitude > 1e-6f ? v.normalized : (Vector2?)null;
        }

        (int, int)[] CornerCells(int i, int j) => new[] { (i - 1, j - 1), (i, j - 1), (i, j), (i - 1, j) };

        /// <summary>vki_cave_ground: chasm and stream ground tiles (never turned; the node's parity picks Q00..Q11),
        /// waterfalls where a stream meets the chasm. -> the cell quarters the tiles cover</summary>
        Dictionary<(int, int), HashSet<(int, int)>> CaveGround()
        {
            bool Inside((int, int) c) => c.Item1 >= 0 && c.Item1 < nc && c.Item2 >= 0 && c.Item2 < nr;
            var xs = new HashSet<(int, int)>(P.codes.Where(kv => (kv.Value == "vv" || kv.Value == "==") && Inside(kv.Key)).Select(kv => kv.Key));
            var ss = new HashSet<(int, int)>(P.codes.Where(kv => kv.Value == "ss" && Inside(kv.Key)).Select(kv => kv.Key));
            var pc = PitCells();
            var sinks = new Dictionary<(int, int), (int, int)>();
            foreach (var c in ss.OrderBy(c => c.Item1).ThenBy(c => c.Item2))
                foreach (var (d, rot) in new[] { ((0, -1), 0), ((1, 0), 90), ((0, 1), 180), ((-1, 0), -90) })
                    if (xs.Contains((c.Item1 + d.Item1, c.Item2 + d.Item2)))
                    {
                        autoProps.Add(new JArray("Waterfall_Chasm", IG * (c.Item1 + 0.5f), IG * (c.Item2 + 0.5f), rot, null, null, new JObject { ["hug"] = false }));
                        if (!sinks.ContainsKey(c)) sinks[c] = d;
                    }
            var flow = Flow(ss, R["stream_sinks"] as JObject, sinks);
            var zones = (JObject)R["zones"];
            var cov = new Dictionary<(int, int), HashSet<(int, int)>>();
            var quarters = new[] { (1, 1), (0, 1), (0, 0), (1, 0) };
            for (int i = 0; i <= nc; i++)
                for (int j = 0; j <= nr; j++)
                {
                    var cs = CornerCells(i, j);
                    bool chasm = cs.Any(xs.Contains), stream = cs.Any(ss.Contains);
                    if (!chasm && !stream) continue;
                    if (cs.Any(pc.ContainsKey)) problems.Add($"cave: the {(chasm ? "chasm" : "stream")} at node ({i},{j}) touches a pit cell");
                    string code, piece;
                    if (chasm)
                    {
                        code = new string(cs.Select(c => xs.Contains(c) || ss.Contains(c) ? 'X' : 'O').ToArray());
                        piece = code == "XXXX" ? "SM_VKI_Ground_Cave_XXXX" : $"SM_VKI_Ground_Cave_{code}_Q{i % 2}{j % 2}";
                    }
                    else
                    {
                        code = new string(cs.Select(c => ss.Contains(c) ? 'X' : 'O').ToArray());
                        piece = code == "XXXX" ? "SM_VKI_Ground_Stream_XXXX" : $"SM_VKI_Ground_Stream_{code}_Q{i % 2}{j % 2}";
                    }
                    var zc = cs.Where(c => !xs.Contains(c) && !ss.Contains(c) && Inside(c)).Select(c => ((int, int)?)c).FirstOrDefault();
                    string zn = zc != null ? zmap[zc.Value] : null;
                    grounds.Add(new Ground
                    {
                        piece = piece, x = IG * i, y = IG * j, node = (i, j), code = code,
                        floorStyle = zn != null ? (string)zones[zn]?["floor"] : null,
                        flow = stream && !chasm ? TileFlow(cs.Where(ss.Contains), flow) : null
                    });
                    for (int k = 0; k < 4; k++)
                    {
                        if (!cov.TryGetValue(cs[k], out var set)) cov[cs[k]] = set = new HashSet<(int, int)>();
                        set.Add(quarters[k]);
                    }
                }
            return cov;
        }

        /// <summary>vki_cave_channels: sewer water ("ww") and lava ("ll") channel tiles, no floor under them</summary>
        HashSet<(int, int)> CaveChannels()
        {
            bool Inside((int, int) c) => c.Item1 >= 0 && c.Item1 < nc && c.Item2 >= 0 && c.Item2 < nr;
            var all = new HashSet<(int, int)>();
            var kinds = new[] { ("ww", "Sewer", "channel_sinks"), ("ll", "Lava", "lava_sinks") };
            var wet = new HashSet<(int, int)>(P.codes.Where(kv => kv.Value == "vv" || kv.Value == "==" || kv.Value == "ss").Select(kv => kv.Key));
            foreach (var (cc, tset, sk) in kinds)
            {
                var xs = new HashSet<(int, int)>(P.codes.Where(kv => kv.Value == cc && Inside(kv.Key)).Select(kv => kv.Key));
                if (xs.Count == 0) continue;
                var others = new HashSet<(int, int)>(wet.Concat(P.codes.Where(kv => kv.Value != cc && (kv.Value == "ww" || kv.Value == "ll")).Select(kv => kv.Key)));
                var flow = Flow(xs, R[sk] as JObject);
                for (int i = 0; i <= nc; i++)
                    for (int j = 0; j <= nr; j++)
                    {
                        var cs = CornerCells(i, j);
                        if (!cs.Any(xs.Contains)) continue;
                        if (cs.Any(others.Contains)) problems.Add($"cave: the {tset.ToLowerInvariant()} channel at node ({i},{j}) touches other water");
                        string code = new string(cs.Select(c => xs.Contains(c) ? 'X' : 'O').ToArray());
                        var (m, k) = Canon(code);
                        grounds.Add(new Ground { piece = $"SM_VKI_Ground_{tset}_{m}", x = IG * i, y = IG * j, rot = Turn(k), node = (i, j), code = code, flow = TileFlow(cs.Where(xs.Contains), flow) });
                    }
                all.UnionWith(xs);
            }
            return all;
        }

        /// <summary>vki_mine_tracks: track tiles along R["tracks"] polylines (axis-aligned, whole 1.5 m tiles); a tile's
        /// kind and turn from its connections; an end marked "open" runs on out of the level</summary>
        void MineTracks()
        {
            const int N = 1, E = 2, S = 4, Wb = 8;
            int Bit(int dx, int dy) => dx == 0 ? (dy > 0 ? N : S) : (dx > 0 ? E : Wb);
            (long, long) K(float x, float y) => ((long)Mathf.Round(x * 1000f), (long)Mathf.Round(y * 1000f));
            var conn = new Dictionary<(long, long), int>();
            var pos = new Dictionary<(long, long), Vector2>();
            var opened = new HashSet<(long, long)>();
            int li = 0;
            foreach (var line in (JArray)R["tracks"])
            {
                var pts = line.Select(p => new Vector2((float)p[0], (float)p[1])).ToList();
                var seq = new List<Vector2> { pts[0] };
                bool bad = false;
                for (int s = 0; s + 1 < pts.Count && !bad; s++)
                {
                    var d = pts[s + 1] - pts[s];
                    int n = Mathf.RoundToInt((Mathf.Abs(d.x) + Mathf.Abs(d.y)) / IG);
                    if ((Mathf.Abs(d.x) > 1e-6f && Mathf.Abs(d.y) > 1e-6f) || n == 0) { problems.Add($"track {li}: a segment is not axis-aligned whole tiles"); bad = true; break; }
                    for (int t = 1; t <= n; t++) seq.Add(pts[s] + d * t / n);
                }
                for (int s = 0; s + 1 < seq.Count; s++)
                {
                    int dx = Mathf.RoundToInt((seq[s + 1].x - seq[s].x) / IG), dy = Mathf.RoundToInt((seq[s + 1].y - seq[s].y) / IG);
                    var ka = K(seq[s].x, seq[s].y); var kb = K(seq[s + 1].x, seq[s + 1].y);
                    pos[ka] = seq[s]; pos[kb] = seq[s + 1];
                    conn[ka] = (conn.TryGetValue(ka, out var ca) ? ca : 0) | Bit(dx, dy);
                    conn[kb] = (conn.TryGetValue(kb, out var cb) ? cb : 0) | Bit(-dx, -dy);
                }
                if (seq.Count >= 2)
                    foreach (var (end, nb) in new[] { (0, 1), (seq.Count - 1, seq.Count - 2) })
                    {
                        var p = line[end == 0 ? 0 : line.Count() - 1];
                        if (p.Count() > 2 && (string)p[2] == "open")
                        {
                            var ke = K(seq[end].x, seq[end].y);
                            conn[ke] |= Bit(Mathf.RoundToInt((seq[end].x - seq[nb].x) / IG), Mathf.RoundToInt((seq[end].y - seq[nb].y) / IG));
                            opened.Add(ke);
                        }
                    }
                li++;
            }
            int Rot90(int m)    // N -> W, E -> N, S -> E, W -> S
            {
                int o = 0;
                if ((m & N) != 0) o |= Wb; if ((m & E) != 0) o |= N; if ((m & S) != 0) o |= E; if ((m & Wb) != 0) o |= S;
                return o;
            }
            var bases = new[] { ("End", 4), ("Straight", 5), ("Curve", 6), ("Tee", 14), ("Cross", 15) };
            foreach (var kv in conn.OrderBy(k => k.Key.Item1).ThenBy(k => k.Key.Item2))
            {
                string kind = null; float rot = 0f;
                foreach (var (kn, m0) in bases)
                {
                    int m = m0;
                    for (int k = 0; k < 4 && kind == null; k++) { if (m == kv.Value) { kind = kn; rot = Turn(k); } m = Rot90(m); }
                    if (kind != null) break;
                }
                if (kind == null) continue;
                var p = pos[kv.Key];
                autoProps.Add(new JArray("Overlay_Track_" + kind, Mathf.Round(p.x * 10000f) / 10000f, Mathf.Round(p.y * 10000f) / 10000f, rot, null, null, new JObject { ["hug"] = false }));
            }
        }
    }
}
