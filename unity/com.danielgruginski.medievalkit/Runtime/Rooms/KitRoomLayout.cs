using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>A parsed ASCII room plan (vki_rooms.vki_parse_plan): walls between nodes, codes in cells.
    /// Node (i, j) is at (1.5 i, 1.5 j) m; row 0 is the camera (south) side.</summary>
    public class KitRoomPlan
    {
        public int nc, nr;
        public readonly Dictionary<(int, int), string> ew = new Dictionary<(int, int), string>();    // (i, j) -> E-W token, node (i,j)..(i+1,j)
        public readonly Dictionary<(int, int), string> ns = new Dictionary<(int, int), string>();    // (i, r) -> N-S char, node (i,r)..(i,r+1)
        public readonly Dictionary<(int, int), string> codes = new Dictionary<(int, int), string>(); // (c, r) -> cell code

        static readonly Regex Labels = new Regex(@"^\s*\d+(\s+\d+)*\s*$");

        public static KitRoomPlan Parse(string txt)
        {
            var lines = txt.Replace("\r", "").Split('\n').Select(l => l.TrimEnd()).Where(l => l.Trim().Length > 0).ToList();
            var body = lines.Where(l => !Labels.IsMatch(l)).ToList();
            var nodes = body.Where(l => l.TrimStart().StartsWith("+")).ToList();
            var cells = body.Where(l => !l.TrimStart().StartsWith("+")).ToList();
            if (nodes.Count == 0) throw new FormatException("plan: no node rows");
            int c0 = nodes[0].IndexOf('+');
            var p = new KitRoomPlan { nc = (nodes[0].Length - 1 - c0) / 3, nr = cells.Count };
            if (nodes.Count != p.nr + 1) throw new FormatException($"plan: {nodes.Count} node rows for {p.nr} cell rows");
            string Ch(string l, int i) => i < l.Length ? l[i].ToString() : " ";
            for (int k = 0; k < nodes.Count; k++)
            {
                int j = p.nr - k;
                for (int i = 0; i < p.nc; i++) p.ew[(i, j)] = Ch(nodes[k], c0 + 3 * i + 1) + Ch(nodes[k], c0 + 3 * i + 2);
            }
            for (int k = 0; k < cells.Count; k++)
            {
                int r = p.nr - 1 - k;
                string l = cells[k];
                string lab = l.Substring(0, Math.Min(c0, l.Length)).Trim();
                if (lab.Length > 0 && int.Parse(lab) != r) throw new FormatException($"plan: row label {lab} where row {r} was expected");
                for (int i = 0; i <= p.nc; i++) p.ns[(i, r)] = Ch(l, c0 + 3 * i);
                for (int i = 0; i < p.nc; i++) p.codes[(i, r)] = Ch(l, c0 + 3 * i + 1) + Ch(l, c0 + 3 * i + 2);
            }
            return p;
        }
    }

    /// <summary>
    /// The pure layout of a room (vki_rooms.vki_rooms_layout, walled rooms): wall pieces with the 300 pairing and the
    /// B variant, posts (required + optional rhythm), floors (600 / 300 / Q150 by parity), from a plan and a room record
    /// (the VKI_ROOMS dict as JSON). Coordinates are the room's (Blender) x east, y north, rotation about z in degrees.
    /// </summary>
    public partial class KitRoomLayout
    {
        public class Seg { public string ori, tok, kind, height, role, fam; public int i, j; }

        public class Piece
        {
            public string piece, kind, height, fam, cls, ori, role, var, tok;
            public int n, line, k;
            public float x, y, rot;
            public List<(int, int)> faceA = new List<(int, int)>(), faceB = new List<(int, int)>();
            public (int, int)[] nodes;
            public Dictionary<(int, int), string> hEnd = new Dictionary<(int, int), string>();
            public string Key => $"{ori}|{k}|{line}";
        }

        public class Post { public (int, int) node; public float x, y, rot; public string fam, height, kind, why, piece; public bool req; }
        public class Floor { public string piece, zone; public float x, y; public string floorStyle; }

        public JObject rules, R;
        public KitRoomPlan P;
        public int nc, nr;
        public float IG, W, D;
        public Dictionary<(int, int), string> zmap;
        public readonly Dictionary<(string, int, int), Seg> segs = new Dictionary<(string, int, int), Seg>();
        public readonly List<Piece> pieces = new List<Piece>();
        public readonly List<Post> posts = new List<Post>();
        public readonly List<Floor> floors = new List<Floor>();
        public readonly List<string> problems = new List<string>();
        public Dictionary<(int, int), (string kind, int index)> stairCells;
        public Dictionary<(int, int), string> pitCells;

        /// <summary>Optional: a piece's vki_fp_cells "w,d" (from its prefab), for pits.</summary>
        public Func<string, string> fpCells;

        public static KitRoomLayout Build(JObject rules, JObject room, string planText, Func<string, string> fpCells = null) =>
            Build(rules, room, KitRoomPlan.Parse(planText), fpCells);

        public static KitRoomLayout Build(JObject rules, JObject room, KitRoomPlan plan, Func<string, string> fpCells = null)
        {
            var L = new KitRoomLayout { rules = rules, R = room, P = plan, fpCells = fpCells };
            L.Run();
            return L;
        }

        JObject Fam(string f) => (JObject)rules["families"][f];
        static bool Even(float a) => Mathf.Abs(a / 3f - Mathf.Round(a / 3f)) < 1e-6f;

        public static Vector2 Frame(float x, float y, float rot, float lx, float ly)
        {
            float r = rot * Mathf.Deg2Rad;
            return new Vector2(x + Mathf.Cos(r) * lx - Mathf.Sin(r) * ly, y + Mathf.Sin(r) * lx + Mathf.Cos(r) * ly);
        }

        Dictionary<(int, int), string> ZoneMap()
        {
            var zc = new Dictionary<(int, int), string>();
            string rest = null;
            foreach (var z in (JObject)R["zones"])
            {
                if (z.Value["cells"].Type == JTokenType.String) { if ((string)z.Value["cells"] == "rest") rest ??= z.Key; continue; }
                foreach (var b in z.Value["cells"])
                    for (int c = (int)b[0]; c <= (int)b[1]; c++)
                        for (int r = (int)b[2]; r <= (int)b[3]; r++)
                            if (!zc.ContainsKey((c, r))) zc[(c, r)] = z.Key;
            }
            for (int c = 0; c < nc; c++)
                for (int r = 0; r < nr; r++)
                    if (!zc.ContainsKey((c, r))) zc[(c, r)] = rest;
            return zc;
        }

        public string WallName(string fam, string kind, string height, int n, string var, string side, string special)
        {
            switch (kind)
            {
                case "Plain": return n == 2 ? $"SM_VKI_Wall_{fam}_Plain_300_{height}" : $"SM_VKI_Wall_{fam}_Plain_150{var}_{height}";
                case "Window": return $"SM_VKI_Wall_{fam}_Window_150_{height}";
                case "Door": case "Exit": return $"SM_VKI_Wall_{fam}_Door_150_{height}";
                case "ExitWide": return $"SM_VKI_Wall_{fam}_DoorWide_300_{height}";
                case "Lancet": return $"SM_VKI_Wall_{fam}_Lancet_150_{height}";
                case "LancetTall": return $"SM_VKI_Wall_{fam}_LancetTall_150_Full";
                case "Rake": return $"SM_VKI_Wall_{fam}_Rake_150_{side}";
                case "Special": return $"SM_VKI_Wall_{fam}_{special}_{height}";
                case "Bars": return n == 2 ? $"SM_VKI_Wall_{fam}_Plain_300_Full" : $"SM_VKI_Wall_{fam}_Plain_150A_Full";
                case "BarsGate": return $"SM_VKI_Wall_{fam}_Door_150_Full";
                case "Niche": return $"SM_VKI_Wall_{fam}_Niche_150_{height}";
                case "Passage": return $"SM_VKI_Wall_{fam}_Passage_150_Full";
                case "Gap": return $"SM_VKI_Wall_{fam}_Gap_150_{height}";
                case "Breach": return $"SM_VKI_Wall_{fam}_Breach_{(n == 2 ? 300 : 150)}_{height}";
                case "Named": return special.StartsWith("SM_VKI_") ? special : "SM_VKI_" + special;
            }
            throw new ArgumentException(kind);
        }

        /// <summary>vki_parse_name's family: the token after the class, when it is a family</summary>
        string NameFamily(string n)
        {
            if (!n.StartsWith("SM_VKI_")) return null;
            var tk = n.Substring(7).Split('_');
            return tk.Length > 1 && rules["families"][tk[1]] != null ? tk[1] : null;
        }

        public Dictionary<(int, int), (string, int)> StairCells()
        {
            var o = new Dictionary<(int, int), (string, int)>();
            var st = R["stairs"] as JArray;
            if (st == null) return o;
            for (int si = 0; si < st.Count; si++)
            {
                var s = st[si];
                for (int d = 0; d < 3; d++)
                {
                    var c = Frame((float)s[1], (float)s[2], (float)s[3], 0.75f, 0.75f + IG * d);
                    o[(Mathf.FloorToInt(c.x / IG), Mathf.FloorToInt(c.y / IG))] = ((string)s[0], si);
                }
            }
            return o;
        }

        public Dictionary<(int, int), string> PitCells()
        {
            var o = new Dictionary<(int, int), string>();
            if (!(R["pits"] is JArray pits)) return o;
            foreach (var pt in pits)
            {
                string piece = ((string)pt[0]).StartsWith("SM_") ? (string)pt[0] : "SM_VKI_" + (string)pt[0];
                int w = 1, d = 1;
                string fp = fpCells?.Invoke(piece);
                if (!string.IsNullOrEmpty(fp)) { var a = fp.Split(','); w = int.Parse(a[0]); d = int.Parse(a[1]); }
                else
                {
                    var m = Regex.Match(piece, @"_(\d{3})x(\d{3})(_|$)");
                    var m1 = Regex.Match(piece, @"_(\d{3})[A-Z]?(_|$)");
                    if (m.Success) { w = Mathf.Max(1, Mathf.RoundToInt(int.Parse(m.Groups[1].Value) / 100f / IG)); d = Mathf.Max(1, Mathf.RoundToInt(int.Parse(m.Groups[2].Value) / 100f / IG)); }
                    else if (m1.Success) { w = d = Mathf.Max(1, Mathf.RoundToInt(int.Parse(m1.Groups[1].Value) / 100f / IG)); }
                }
                int c0 = Mathf.RoundToInt((float)pt[1] / IG), r0 = Mathf.RoundToInt((float)pt[2] / IG);
                for (int a = 0; a < w; a++) for (int b = 0; b < d; b++) o[(c0 + a, r0 + b)] = piece;
            }
            return o;
        }

        void Run()
        {
            IG = (float)rules["ig"];
            nc = P.nc; nr = P.nr; W = IG * nc; D = IG * nr;
            zmap = ZoneMap();
            if ((bool?)R["cave"] == true) { RunCave(); return; }       // a cave map: rock tiles (KitCaveLayout.cs)
            string famP = (string)R["family"]["perimeter"];
            string famI = (string)R["family"]["partition"] ?? famP;
            var tokEW = (JObject)rules["tok_ew"]; var tokNS = (JObject)rules["tok_ns"]; var own = (JObject)rules["own_family"];
            (string, string) Tok(JObject t, string k) { var v = t[k]; return v == null ? (null, null) : ((string)v[0], (string)v[1]); }

            foreach (var kv in P.ew)
            {
                var (i, j) = kv.Key;
                if (tokEW[kv.Value] == null) problems.Add($"plan: unknown E-W token '{kv.Value}' at node ({i},{j})");
                var (kind, ht) = Tok(tokEW, kv.Value);
                string role = j == nr ? "N" : (j == 0 ? "S" : "part");
                segs[("EW", i, j)] = new Seg { ori = "EW", i = i, j = j, tok = kv.Value, kind = kind, height = ht, role = role,
                    fam = (kind != null ? (string)own[kind] : null) ?? (role == "part" ? famI : famP) };
            }
            foreach (var kv in P.ns)
            {
                var (i, r) = kv.Key;
                if (tokNS[kv.Value] == null) problems.Add($"plan: unknown N-S char '{kv.Value}' at node ({i},{r})");
                var (kind, ht) = Tok(tokNS, kv.Value);
                string role = i == 0 ? "W" : (i == nc ? "E" : "part");
                segs[("NS", i, r)] = new Seg { ori = "NS", i = i, j = r, tok = kv.Value, kind = kind, height = ht, role = role,
                    fam = (kind != null ? (string)own[kind] : null) ?? (role == "part" ? famI : famP) };
            }
            bool Walls(Seg s) => s != null && s.kind != null && s.kind != "Rail";
            Seg Get(string o, int a, int b) => segs.TryGetValue((o, a, b), out var s) ? s : null;
            bool open = R["open_frame"] != null && (bool)R["open_frame"];
            if (!open)
            {
                for (int i = 0; i < nc; i++) foreach (var j in new[] { 0, nr }) if (!Walls(Get("EW", i, j))) problems.Add($"plan: perimeter gap at E-W segment ({i},{j})");
                for (int r = 0; r < nr; r++) foreach (var i in new[] { 0, nc }) if (!Walls(Get("NS", i, r))) problems.Add($"plan: perimeter gap at N-S segment ({i},{r})");
            }
            var arms = new Dictionary<(int, int), HashSet<string>>();
            void Arm((int, int) nd, string a) { if (!arms.TryGetValue(nd, out var s)) arms[nd] = s = new HashSet<string>(); s.Add(a); }
            foreach (var s in segs.Values)
            {
                if (!Walls(s)) continue;
                if (s.ori == "EW") { Arm((s.i, s.j), "E"); Arm((s.i + 1, s.j), "W"); }
                else { Arm((s.i, s.j), "N"); Arm((s.i, s.j + 1), "S"); }
            }
            bool Junction((int, int) nd)
            {
                if (!arms.TryGetValue(nd, out var a)) return false;
                if (a.Count >= 3) return true;
                return a.Count == 2 && !(a.SetEquals(new[] { "E", "W" }) || a.SetEquals(new[] { "N", "S" }));
            }
            var ppts = (R["props"] as JArray ?? new JArray()).Select(p => new Vector2((float)p[1], (float)p[2])).ToList();
            string special = (string)R["special"];
            var specials = R["specials"] as JObject;
            var zones = (JObject)R["zones"];
            var limeFams = new HashSet<string> { "Timber", "Stone", "Wattle", "Dungeon", "Ancient", "Sewer", "Dwarf" };

            foreach (var (ori, nline, nalong) in new[] { ("EW", nr + 1, nc), ("NS", nc + 1, nr) })
                for (int ln = 0; ln < nline; ln++)
                {
                    int k = 0;
                    while (k < nalong)
                    {
                        var s = ori == "EW" ? Get(ori, k, ln) : Get(ori, ln, k);
                        if (!Walls(s)) { k++; continue; }
                        string kind = s.kind, ht = s.height, fam = s.fam, role = s.role;
                        int n = 1;
                        string named = null;
                        if (kind == "Named")
                        {
                            named = (string)specials?[s.tok.Trim()];
                            if (string.IsNullOrEmpty(named))
                            {
                                problems.Add($"plan: named token '{s.tok}' at {ori} ({k},{ln}) has no R['specials'] entry");
                                named = $"SM_VKI_Wall_{fam}_Plain_150A_{ht}";
                            }
                            if (named.Contains("_300_") || named.EndsWith("_300")) n = 2;
                        }
                        var s2 = ori == "EW" ? Get(ori, k + 1, ln) : Get(ori, ln, k + 1);
                        if (kind == "Special" || kind == "ExitWide")
                        {
                            if (s2 == null || s2.kind != kind) problems.Add($"plan: {s.tok} at {ori} ({k},{ln}) needs a second cell");
                            n = 2;
                        }
                        else if (kind == "Plain" || kind == "Bars" || kind == "Breach")
                        {
                            var mid = ori == "EW" ? (k + 1, ln) : (ln, k + 1);
                            if (k % 2 == 0 && s2 != null && s2.kind == kind && s2.height == ht && s2.fam == fam && !Junction(mid)) n = 2;
                        }
                        if (kind == "Rake" && !(bool)Fam(fam)["rake"]) { kind = "Plain"; ht = "Full"; }
                        if (kind == "Special" && string.IsNullOrEmpty(special)) problems.Add($"plan: FF at {ori} ({k},{ln}) but the room has no special");
                        float x0, x1, y0, y1, rot, ox, oy;
                        List<(int, int)> fa, fb;
                        (int, int)[] nodes;
                        if (ori == "EW")
                        {
                            x0 = IG * k; x1 = IG * (k + n); y0 = IG * ln; y1 = y0;
                            if (role == "S") { rot = 180; ox = x1; oy = y0; } else { rot = 0; ox = x0; oy = y0; }
                            var north = Enumerable.Range(0, n).Select(d => (k + d, ln)).ToList();
                            var south = Enumerable.Range(0, n).Select(d => (k + d, ln - 1)).ToList();
                            if (rot == 180) { fa = north; fb = south; } else { fa = south; fb = north; }
                            nodes = new[] { (k, ln), (k + n, ln) };
                        }
                        else
                        {
                            y0 = IG * k; y1 = IG * (k + n); x0 = IG * ln; x1 = x0;
                            if (role == "E") { rot = -90; ox = x0; oy = y1; } else { rot = 90; ox = x0; oy = y0; }
                            var east = Enumerable.Range(0, n).Select(d => (ln, k + d)).ToList();
                            var west = Enumerable.Range(0, n).Select(d => (ln - 1, k + d)).ToList();
                            if (rot == -90) { fa = west; fb = east; } else { fa = east; fb = west; }
                            nodes = new[] { (ln, k), (ln, k + n) };
                        }
                        bool Inside((int, int) c) => c.Item1 >= 0 && c.Item1 < nc && c.Item2 >= 0 && c.Item2 < nr;
                        string var = "A";
                        bool limewash = fam == "Stone" && fa.Any(c => zmap.TryGetValue(c, out var zn) && zn != null &&
                                                                       ((string)zones[zn]?["wall"] ?? "").StartsWith("Plaster"));
                        if (kind == "Plain" && n == 1 && ht == "Full" && role != "part" && limeFams.Contains(fam) && k % 2 == 1 && !limewash)
                        {
                            var m = ori == "EW" ? new Vector2(x0 + IG * 0.5f, y0) : new Vector2(x0, y0 + IG * 0.5f);
                            if (!ppts.Any(pp => (pp - m).magnitude < 1.3f)) var = "B";
                        }
                        string side = null;
                        if (kind == "Rake")
                        {
                            side = role == "W" ? "L" : "R";
                            if ((role != "W" && role != "E") || k != 0) problems.Add($"plan: rake 't' at {ori} ({ln},{k}) is not the south-most side-wall piece");
                        }
                        string pname = WallName(fam, kind, kind != "Rake" ? ht : "Rake", n, var, side, kind == "Named" ? named : special);
                        if (kind == "Named") { var pf = NameFamily(pname); if (pf != null) fam = pf; }
                        var pc = new Piece
                        {
                            piece = pname, kind = kind, height = ht, fam = fam, cls = (string)Fam(fam)["cls"], n = n, ori = ori,
                            role = role, line = ln, k = k, x = ox, y = oy, rot = rot, var = var, tok = s.tok, nodes = nodes,
                            faceA = fa.Where(Inside).ToList(), faceB = fb.Where(Inside).ToList()
                        };
                        foreach (var nd in nodes) pc.hEnd[nd] = kind == "Rake" ? (nd.Item2 == 0 ? "Cut" : "Full") : ht;
                        pieces.Add(pc);
                        k += n;
                    }
                }

            // ---- posts (§2.3): ends per node
            var ends = new SortedDictionary<(int, int), List<(Vector2 d, string fam, string cls, string h)>>();
            foreach (var pc in pieces)
                foreach (var (nd, other) in new[] { (pc.nodes[0], pc.nodes[1]), (pc.nodes[1], pc.nodes[0]) })
                {
                    var d = new Vector2(other.Item1 - nd.Item1, other.Item2 - nd.Item2).normalized;
                    if (!ends.TryGetValue(nd, out var l)) ends[nd] = l = new List<(Vector2, string, string, string)>();
                    l.Add((d, pc.fam, pc.cls, pc.hEnd[nd]));
                }
            var stairNodes = new HashSet<(int, int)>();
            if (R["stairs"] is JArray sts)
                foreach (var st in sts)
                {
                    var pts = Enumerable.Range(0, 4).Select(d => new Vector2(0, IG * d)).Append(new Vector2(IG, 3 * IG));
                    foreach (var lp in pts)
                    {
                        var w = Frame((float)st[1], (float)st[2], (float)st[3], lp.x, lp.y);
                        stairNodes.Add((Mathf.RoundToInt(w.x / IG), Mathf.RoundToInt(w.y / IG)));
                    }
                }
            var prio = rules["post_prio"].Select(x => (string)x).ToList();
            bool rhythmSides = R["rhythm_sides"] != null && R["rhythm_sides"].Type == JTokenType.Boolean && (bool)R["rhythm_sides"];
            foreach (var kv in ends)
            {
                var nd = kv.Key; var es = kv.Value;
                bool corner = es.Any(a => es.Any(b => Mathf.Abs(a.d.x * b.d.y - a.d.y * b.d.x) > 0.5f));
                string pf = es.Select(e => e.fam).Distinct().OrderBy(f => prio.IndexOf(f)).First();
                string ph = es.Any(e => e.h == "Full") ? "Full" : "Cut";
                bool alongX = Mathf.Abs(es[0].d.x) > 0.5f;
                float x = IG * nd.Item1, y = IG * nd.Item2;
                Post Make(string kind, float rot, string why, bool req) => new Post { node = nd, x = x, y = y, fam = pf, height = ph, kind = kind, rot = rot, why = why, req = req };
                if (corner) posts.Add(Make("Corner", 0, "L/T/X junction", true));
                else if (es.Count == 1) posts.Add(Make("Mid", alongX ? 0 : 90, "free end", true));
                else if (es.Skip(1).Any(e => (e.h, e.fam, e.cls) != (es[0].h, es[0].fam, es[0].cls))) posts.Add(Make("Mid", alongX ? 0 : 90, "height/family/class step", true));
                else
                {
                    string fam = es[0].fam;
                    float along = alongX ? x : y;
                    bool sideWall = (nd.Item1 == 0 || nd.Item1 == nc) && !alongX;
                    bool rh = (bool)Fam(fam)["rhythm"] || (fam == "Ashlar" && rhythmSides && sideWall);
                    if (rh && Even(along) && !stairNodes.Contains(nd)) posts.Add(Make("Mid", alongX ? 0 : 90, "rhythm (even node)", false));
                }
                if (posts.Count > 0 && posts[posts.Count - 1].node == nd && posts[posts.Count - 1].fam == "Ashlar" &&
                    posts[posts.Count - 1].kind == "Mid" && posts[posts.Count - 1].height == "Cut")
                { posts[posts.Count - 1].kind = "Corner"; posts[posts.Count - 1].rot = 0; }
            }
            foreach (var p in posts) p.piece = $"SM_VKI_Post_{p.fam}_{p.kind}_{p.height}";

            // ---- floors (§2.7): greedy 600 -> 300 (even nodes) -> Q150 per zone; Stair_Down footprints and pits excluded
            stairCells = StairCells();
            pitCells = PitCells();
            foreach (var z in zones)
            {
                string zn = z.Key;
                string floorStyle = (string)z.Value["floor"];
                var cells = new HashSet<(int, int)>(zmap.Where(c => c.Value == zn &&
                    !(stairCells.TryGetValue(c.Key, out var sc) && sc.kind == "Down") && !pitCells.ContainsKey(c.Key)).Select(c => c.Key));
                if (z.Value["dais"] != null && z.Value["dais"].Type == JTokenType.Boolean && (bool)z.Value["dais"])
                {
                    foreach (var dz in R["dais"] as JArray ?? new JArray())
                    {
                        float dx = (float)dz[0], dy = (float)dz[1];
                        var blk = new HashSet<(int, int)>();
                        for (int a = 0; a < 2; a++) for (int b = 0; b < 2; b++) blk.Add((Mathf.RoundToInt(dx / IG) + a, Mathf.RoundToInt(dy / IG) + b));
                        if (!blk.IsSubsetOf(cells)) problems.Add($"floors: dais at ({dx},{dy}) leaves zone {zn}");
                        cells.ExceptWith(blk);
                        floors.Add(new Floor { piece = "SM_VKI_Floor_Dais_300", x = dx, y = dy, zone = zn, floorStyle = floorStyle });
                    }
                    if (cells.Count > 0) problems.Add($"floors: dais zone {zn} cells without a dais");
                    continue;
                }
                foreach (var (S, n) in new[] { (6f, 4), (3f, 2) })
                    foreach (var (i, j) in cells.OrderBy(c => c.Item1).ThenBy(c => c.Item2).ToList())
                    {
                        float x = IG * i, y = IG * j;
                        var blk = new List<(int, int)>();
                        for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) blk.Add((i + a, j + b));
                        if (Even(x) && Even(y) && blk.All(cells.Contains))
                        {
                            cells.ExceptWith(blk);
                            floors.Add(new Floor { piece = $"SM_VKI_Floor_{(int)(S * 100)}", x = x, y = y, zone = zn, floorStyle = floorStyle });
                        }
                    }
                foreach (var (i, j) in cells.OrderBy(c => c.Item1).ThenBy(c => c.Item2))
                    floors.Add(new Floor { piece = $"SM_VKI_Floor_150_Q{i % 2}{j % 2}", x = IG * i, y = IG * j, zone = zn, floorStyle = floorStyle });
            }
        }
    }
}
