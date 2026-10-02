using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Furniture (vki_rooms_props + vki_place, in outline): each prop of the room record, or each block of the plan's
    /// cell codes, goes in by its mount. wall_floor: back on the proud line of the wall behind it, slid off side walls;
    /// wall_hung: back on the wall face (or hung from the top); table: on its host's top; floor: pushed off walls.
    /// </summary>
    public partial class KitRoom
    {
        public enum Furniture { Auto, Record, Codes, None }

        void Furnish()
        {
            JArray list = null;
            var rec = R["props"] as JArray;
            switch (furniture)
            {
                case Furniture.Auto:
                    list = rec != null && rec.Count > 0 ? rec : PropsFromCodes();
                    if (rec != null && rec.Count > 0 && (bool?)R["props_from_codes"] == true)     // both (generated dungeons)
                    {
                        list = new JArray(rec);
                        foreach (var a in PropsFromCodes()) list.Add(a);
                    }
                    break;
                case Furniture.Record: list = rec; break;
                case Furniture.Codes: list = PropsFromCodes(); break;
            }
            if (list != null && Layout.autoProps.Count > 0)            // a cave's waterfalls and track tiles
            {
                list = new JArray(list);
                foreach (var a in Layout.autoProps) list.Add(a.DeepClone());
            }
            if (list != null) PlaceProps(list);
        }

        float ProudLine(string cls) => J["proud_line"]?[cls] != null ? (float)J["proud_line"][cls] : (cls == "O" ? 0.285f : 0.185f);

        /// <summary>the prefab's mesh box in its Blender local space (x0, y0, z0, x1, y1, z1)</summary>
        static float[] LocalBox(GameObject go)
        {
            var mf = go.GetComponent<MeshFilter>();
            var b = mf != null && mf.sharedMesh != null ? mf.sharedMesh.bounds : new Bounds(Vector3.zero, Vector3.one * 0.5f);
            return new[] { -b.max.x, -b.max.z, b.min.y, -b.min.x, -b.min.z, b.max.y };
        }

        struct Seg { public Vector2 p0, p1; public string cls, height, name; public float H; }

        List<Seg> WallSegs()
        {
            var o = new List<Seg>();
            foreach (var p in placed)
            {
                if (Cls(p) != "wall" || !p.kp.Has("vki_len")) continue;
                float L = p.kp.GetFloat("vki_len");
                string fam = p.kp.Get("vki_family"), ht = p.kp.Get("vki_height", "Full");
                o.Add(new Seg
                {
                    p0 = Frame(p.x, p.y, p.rot, 0f, 0f), p1 = Frame(p.x, p.y, p.rot, L, 0f),
                    cls = p.kp.GetFloat("vki_thick", 0.5f) < 0.4f ? "P" : "O", height = ht, name = p.go.name,
                    H = ht == "Cut" ? (float)J["cut_h"] : fam != null && J["families"][fam] != null ? (float)J["families"][fam]["H"] : 3f
                });
            }
            return o;
        }

        /// <summary>vki_rooms_resolve: "Chest" -> SM_VKI_Prop_Chest, "Prop_Loom" -> SM_VK_Prop_Loom, full names as they are</summary>
        string Resolve(string s)
        {
            var c = s.StartsWith("SM_") ? new[] { s } : s.StartsWith("Prop_") ? new[] { "SM_VK_" + s, "SM_VKI_" + s } : new[] { "SM_VKI_Prop_" + s, "SM_VKI_" + s };
            return c.FirstOrDefault(n => rules.Prefab(n) != null);
        }

        static bool Reused(string piece) => piece.StartsWith("SM_VK_") && !piece.StartsWith("SM_VKI_");
        string MountOf(string piece, KitPiece kp) => kp?.Get("vki_mount") ?? (string)J["reuse"]?[piece]?["mount"] ?? "floor";

        /// <summary>a prop list in the record's format: [name, x, y, rot, style, mount, {on, hug, z, link}]</summary>
        void PlaceProps(JArray list)
        {
            var done = new List<Placed>();
            foreach (var pr in list)
            {
                string shortName = (string)pr[0];
                float x = (float)pr[1], y = (float)pr[2], rot = (float)pr[3];
                var style = StyleOf(pr[4]);
                string mount = pr.Count() > 5 ? (string)pr[5] : null;
                var opts = pr.Count() > 6 ? pr[6] as JObject : null;
                string piece = Resolve(shortName);
                if (piece == null) { notes.Add($"no prefab for prop {shortName} at {x:0.##}, {y:0.##}"); continue; }
                bool edge = mount == "edge";
                string mEff = edge ? null : mount;
                string mnt = mEff ?? MountOf(piece, rules.Prefab(piece).GetComponent<KitPiece>());
                float z = opts?["z"] != null ? (float)opts["z"] : 0f;
                Placed host = null;
                if ((bool?)opts?["on"] == true)
                {
                    host = Enumerable.Reverse(done).FirstOrDefault(h => h.mount != "table" && Mathf.Abs(h.atX - x) < 1e-4f && Mathf.Abs(h.atY - y) < 1e-4f);
                    if (host != null)
                        z += host.kp != null && host.kp.Has("vki_table_z") ? host.kp.GetFloat("vki_table_z") + host.z : ObjBox(host).b.z;
                }
                bool? hug = opts?["hug"] != null ? (bool?)opts["hug"] : mnt == "wall_floor" ? (bool?)null : (edge || mnt == "table") ? false : true;
                var o = Put(props, piece, x, y, rot, z, style, "prop");
                if (o == null) continue;
                Mount(o, mEff, hug);
                if (host != null)       // table dressing stands on the centre of its host's top
                {
                    var hb = ObjBox(host);
                    Move(o, o.x + (hb.a.x + hb.b.x) / 2 - x, o.y + (hb.a.y + hb.b.y) / 2 - y, o.z);
                    o.kp?.Set("vki_on", host.go.name);
                }
                if (opts?["link"] != null) PropLink(o, (string)opts["link"]);
                if (edge) o.kp?.Set("vki_edge_piece", "1");
                done.Add(o);
            }
        }

        void Move(Placed o, float x, float y, float z)
        {
            o.x = x; o.y = y; o.z = z;
            o.go.transform.localPosition = new Vector3(-x, z, -y);
        }

        /// <summary>vki_place's mounts, without the post-square and pull refinements</summary>
        void Mount(Placed o, string mountArg, bool? hug)
        {
            var kp = o.kp;
            bool reuse = Reused(o.piece);
            string cls = reuse ? "prop" : Cls(o);
            string mount = mountArg ?? MountOf(o.piece, kp);
            o.mount = mount;
            kp?.Set("vki_mount", mount);
            kp?.Set("vki_at", $"[{o.atX.ToString(System.Globalization.CultureInfo.InvariantCulture)}, {o.atY.ToString(System.Globalization.CultureInfo.InvariantCulture)}]");
            if (cls != "prop" && cls != "overlay" && cls != "fx") return;
            float r = o.rot * Mathf.Deg2Rad;
            var a = new Vector2(Mathf.Cos(r), Mathf.Sin(r));       // along
            var b = new Vector2(-Mathf.Sin(r), Mathf.Cos(r));      // toward the back
            var P = new Vector2(o.x, o.y);
            var bx = LocalBox(o.go);
            float cx = reuse ? (bx[0] + bx[3]) / 2 : 0f, cy = reuse ? (bx[1] + bx[4]) / 2 : 0f;
            float zz = o.z;
            var segs = WallSegs();
            Vector2 O;
            if (mount == "wall_floor" || mount == "wall_hung")
            {
                float backL = kp != null && kp.Has("vki_back_y") ? kp.GetFloat("vki_back_y") : bx[4];
                float pa = Vector2.Dot(P, a), pb = Vector2.Dot(P, b);
                Seg? best = null; float wb = 0f;
                foreach (var sg in segs)
                {
                    var d = sg.p1 - sg.p0;
                    if (d.magnitude < 1e-6f || Mathf.Abs(Vector2.Dot(d.normalized, b)) > 1e-3f) continue;   // not parallel to the back wall
                    float w = Vector2.Dot(sg.p0, b);
                    if (w - pb <= 1e-6f) continue;                                                        // behind the point
                    float s0 = Mathf.Min(Vector2.Dot(sg.p0, a), Vector2.Dot(sg.p1, a)), s1 = Mathf.Max(Vector2.Dot(sg.p0, a), Vector2.Dot(sg.p1, a));
                    if (pa < s0 - 1e-4f || pa > s1 + 1e-4f) continue;
                    if (best == null || w < wb) { best = sg; wb = w; }
                }
                string wc = "O"; float H = (float)J["families"]["Timber"]["H"];
                if (best == null) wb = Mathf.Floor(pb / Layout.IG + 1e-6f) * Layout.IG + Layout.IG;
                else { wc = best.Value.cls; H = best.Value.H; kp?.Set("vki_host", best.Value.name); }
                float gap;
                if (mount == "wall_floor") gap = ProudLine(wc);
                else
                {
                    gap = (float)J["t"][wc] / 2f;
                    if (kp?.Get("vki_mount_ref") == "top") zz = H - kp.GetFloat("vki_mount_offset", 0.25f);
                }
                float ob = wb - gap - backL, oa = pa - cx, slide = 0f;
                if (hug ?? mount == "wall_floor")
                {
                    // slide along the wall (<= 0.30) off the proud lines of side walls the prop would cross
                    float half = (bx[3] - bx[0]) / 2, lo = pa - half, hi = pa + half, bLo = ob + bx[1], bHi = ob + backL;
                    var need = new List<float>();
                    foreach (var sg in segs)
                    {
                        var d = sg.p1 - sg.p0;
                        if (d.magnitude < 1e-6f || Mathf.Abs(Vector2.Dot(d.normalized, a)) > 1e-3f) continue;
                        float sa = Vector2.Dot(sg.p0, a);
                        float t0 = Mathf.Min(Vector2.Dot(sg.p0, b), Vector2.Dot(sg.p1, b)), t1 = Mathf.Max(Vector2.Dot(sg.p0, b), Vector2.Dot(sg.p1, b));
                        if (t1 < bLo - 1e-4f || t0 > bHi + 1e-4f) continue;
                        float pl = ProudLine(sg.cls);
                        if (sa >= pa && hi > sa - pl) need.Add(sa - pl - hi);
                        else if (sa < pa && lo < sa + pl) need.Add(sa + pl - lo);
                    }
                    // post squares reach past the proud line (0.31 / 0.21 from the wall line): keep 5 mm clear of them
                    foreach (var pp in placed)
                    {
                        if (Cls(pp) != "post") continue;
                        var pb_ = ObjBox(pp);
                        var cs = new[] { new Vector2(pb_.a.x, pb_.a.y), new Vector2(pb_.b.x, pb_.a.y), new Vector2(pb_.a.x, pb_.b.y), new Vector2(pb_.b.x, pb_.b.y) };
                        float pa0 = cs.Min(c => Vector2.Dot(c, a)), pa1 = cs.Max(c => Vector2.Dot(c, a));
                        float pb0 = cs.Min(c => Vector2.Dot(c, b)), pb1 = cs.Max(c => Vector2.Dot(c, b));
                        if (pb1 < bLo + 1e-6f || pb0 > bHi - 1e-6f || pa1 < lo - 0.305f || pa0 > hi + 0.305f) continue;
                        if (pa0 > lo + 1e-6f && pa1 < hi - 1e-6f) continue;                    // a post inside the span: nothing to slide
                        if ((pa0 + pa1) / 2 >= pa && hi > pa0 - 0.005f) need.Add(pa0 - 0.005f - hi);
                        else if ((pa0 + pa1) / 2 < pa && lo < pa1 + 0.005f) need.Add(pa1 + 0.005f - lo);
                    }
                    need.RemoveAll(v => Mathf.Abs(v) < 1e-9f);
                    bool neg = need.Any(v => v < 0), pos = need.Any(v => v > 0);
                    if (neg && pos) notes.Add($"{o.go.name}: walls on both sides, not slid");
                    else if (need.Count > 0)
                    {
                        slide = neg ? need.Min() : need.Max();
                        if (Mathf.Abs(slide) > 0.30f + 1e-6f) { notes.Add($"{o.go.name}: would need a {slide:0.00} m slide, left in place"); slide = 0f; }
                    }
                }
                O = a * (oa + slide) + b * ob;
            }
            else
            {
                O = P - (a * cx + b * cy);
                if (hug == true)
                {
                    // floor prop: pushed off nearby walls' proud lines
                    var cs = new[] { new Vector2(bx[0], bx[1]), new Vector2(bx[3], bx[1]), new Vector2(bx[3], bx[4]), new Vector2(bx[0], bx[4]) }
                        .Select(c => O + a * c.x + b * c.y).ToList();
                    var lo = new Vector2(cs.Min(c => c.x), cs.Min(c => c.y));
                    var hi = new Vector2(cs.Max(c => c.x), cs.Max(c => c.y));
                    var need = new[] { new List<float>(), new List<float>() };
                    foreach (var sg in segs)
                    {
                        float pl = ProudLine(sg.cls);
                        for (int ax = 0; ax < 2; ax++)
                        {
                            if (Mathf.Abs(sg.p0[ax] - sg.p1[ax]) > 1e-6f) continue;
                            float w = sg.p0[ax], t0 = Mathf.Min(sg.p0[1 - ax], sg.p1[1 - ax]), t1 = Mathf.Max(sg.p0[1 - ax], sg.p1[1 - ax]);
                            if (t1 < lo[1 - ax] || t0 > hi[1 - ax] || w < lo[ax] - pl || w > hi[ax] + pl) continue;
                            if ((lo[ax] + hi[ax]) / 2 >= w) { if (lo[ax] < w + pl) need[ax].Add(w + pl - lo[ax]); }
                            else if (hi[ax] > w - pl) need[ax].Add(w - pl - hi[ax]);
                        }
                    }
                    var slide = Vector2.zero; bool fail = false;
                    for (int ax = 0; ax < 2; ax++)
                    {
                        if (need[ax].Count == 0) continue;
                        if (need[ax].Min() < 0 && need[ax].Max() > 0) fail = true;
                        else slide[ax] = need[ax].OrderByDescending(v => Mathf.Abs(v)).First();
                    }
                    if (fail || Mathf.Max(Mathf.Abs(slide.x), Mathf.Abs(slide.y)) > 0.30f + 1e-6f)
                    {
                        if (slide != Vector2.zero || fail) notes.Add($"{o.go.name}: too close to walls to hug, left in place");
                    }
                    else O += slide;
                }
            }
            Move(o, O.x, O.y, zz);
        }

        /// <summary>vki_rooms_prop_link: a prop that carries a scene link (the mine's lift, a treadwheel)</summary>
        void PropLink(Placed o, string lid)
        {
            var lk = LinkEntry(lid);
            if (lk == null) { notes.Add($"prop {o.go.name} carries link {lid}: no links entry"); return; }
            Link(o, (string)lk[1], lid, (string)lk[2], o.kp?.Get("vki_prompt_text") ?? "Use");
            var sl = PropJ(o.kp, "vki_spawn_local") as JArray;
            var s = Frame(o.x, o.y, o.rot, sl != null ? (float)sl[0] : 0f, sl != null ? (float)sl[1] : -1.60f);
            float fac = o.kp != null && o.kp.Has("vki_spawn_facing") ? o.kp.GetFloat("vki_spawn_facing") : 180f;
            SpawnPoint(lid, R4(s.x), R4(s.y), Mod360(fac - o.rot), o);
        }

        /// <summary>Writes the furniture of the plan's codes into the record's prop list, to edit by hand.</summary>
        public int CodesToRecord()
        {
            if (Layout == null) Generate();
            var list = PropsFromCodes();
            var rec = JObject.Parse(string.IsNullOrWhiteSpace(record) ? "{}" : record);
            rec["props"] = list;
            record = rec.ToString(Newtonsoft.Json.Formatting.Indented);
            return list.Count;
        }

        // ------------------------------------------------------------------ furniture from the plan's cell codes
        /// <summary>
        /// The plan's cell codes (TB table, CH chest, BX bed...; rules "codes") as a prop list: each block of equal codes
        /// (not split by walls) takes the largest piece of that code whose footprint fits, at the block's centre; 1-cell
        /// pieces fill every cell. Wall-backed and wall-hung pieces turn their back to the block side with the most wall,
        /// others lie along the block. Call after Generate (it reads the layout).
        /// </summary>
        public JArray PropsFromCodes()
        {
            var outList = new JArray();
            if (Layout == null) return outList;
            var inv = new Dictionary<string, List<string>>();
            foreach (var kv in (JObject)J["codes"])
            {
                string c = (string)kv.Value;
                if (!inv.TryGetValue(c, out var l)) inv[c] = l = new List<string>();
                l.Add(kv.Key);
            }
            var P = Layout.P;
            bool Wall(string ori, int i, int j, out bool full)
            {
                full = false;
                if (!Layout.segs.TryGetValue((ori, i, j), out var s) || s.kind == null || s.kind == "Rail") return false;
                full = s.height != "Cut";
                return true;
            }
            // the cells either side of a doorway stay clear of the forms the codes add round tables
            var doorway = new HashSet<(int, int)>(Layout.pieces
                .Where(pc => pc.kind == "Door" || pc.kind == "Exit" || pc.kind == "ExitWide" || pc.kind == "Gap" || pc.kind == "Breach" || pc.kind == "Passage" || pc.kind == "BarsGate")
                .SelectMany(pc => pc.faceA.Concat(pc.faceB)));
            var seen = new HashSet<(int, int)>();
            for (int r0 = 0; r0 < P.nr; r0++)
                for (int c0 = 0; c0 < P.nc; c0++)
                {
                    if (seen.Contains((c0, r0)) || !P.codes.TryGetValue((c0, r0), out var code) || !inv.ContainsKey(code)) continue;
                    var blob = new List<(int, int)>();
                    var q = new Queue<(int, int)>();
                    q.Enqueue((c0, r0)); seen.Add((c0, r0));
                    while (q.Count > 0)
                    {
                        var (c, r) = q.Dequeue();
                        blob.Add((c, r));
                        foreach (var (dc, dr) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                        {
                            var n = (c + dc, r + dr);
                            if (seen.Contains(n) || !P.codes.TryGetValue(n, out var nc) || nc != code) continue;
                            bool walled = dc != 0 ? Wall("NS", Mathf.Max(c, n.Item1), r, out _) : Wall("EW", c, Mathf.Max(r, n.Item2), out _);
                            if (walled) continue;
                            seen.Add(n); q.Enqueue(n);
                        }
                    }
                    var cands = inv[code].Select(sn => (sn, piece: Resolve(sn))).Where(t => t.piece != null).Select(t =>
                    {
                        var kp = rules.Prefab(t.piece).GetComponent<KitPiece>();
                        string fp = kp?.Get("vki_fp_cells");
                        int w = 1, d = 1;
                        if (fp != null) { var f = fp.Split(','); w = int.Parse(f[0]); d = int.Parse(f[1]); }
                        else if (J["reuse"]?[t.piece] is JObject ru) { w = (int)ru["fp"][0]; d = (int)ru["fp"][1]; }
                        return (t.sn, t.piece, w, d, mount: MountOf(t.piece, kp));
                    }).ToList();
                    if (cands.Count == 0) { notes.Add($"plan code {code}: no prefab for {string.Join(", ", inv[code])}"); continue; }
                    int bc0 = blob.Min(b => b.Item1), bc1 = blob.Max(b => b.Item1), br0 = blob.Min(b => b.Item2), br1 = blob.Max(b => b.Item2);
                    int bw = bc1 - bc0 + 1, bh = br1 - br0 + 1;
                    bool Fits((string sn, string piece, int w, int d, string mount) c) => (c.w <= bw && c.d <= bh) || (c.d <= bw && c.w <= bh);
                    var fit = cands.Where(Fits).ToList();
                    var pick = (fit.Count > 0 ? fit : cands)
                        .OrderBy(c => fit.Count > 0 ? -(c.w * c.d) : c.w * c.d)
                        .ThenBy(c => Reused(c.piece) ? 1 : 0).ThenBy(c => c.sn.Length).First();
                    var pkp = rules.Prefab(pick.piece).GetComponent<KitPiece>();
                    bool table = pkp != null && pkp.Has("vki_table_z") && pick.mount != "table";
                    bool trestle = table && pick.piece.Contains("Trestle");
                    bool flat = pkp?.Get("vki_class") == "overlay" || pick.piece.Contains("_Rug_");
                    // the block as tiles of the footprint (a row of pews, a stack of crates); tables stay one piece
                    var groups = new List<List<(int, int)>> { blob };
                    bool rect = blob.Count == bw * bh;
                    if (!table && rect)
                        foreach (var (tw, th) in new[] { (pick.w, pick.d), (pick.d, pick.w) })
                            if (bw % tw == 0 && bh % th == 0 && bw * bh > tw * th)
                            {
                                groups = new List<List<(int, int)>>();
                                for (int ti = 0; ti < bw / tw; ti++)
                                    for (int tj = 0; tj < bh / th; tj++)
                                        groups.Add(blob.Where(b => (b.Item1 - bc0) / tw == ti && (b.Item2 - br0) / th == tj).ToList());
                                break;
                            }
                    if (!rect && pick.w == 1 && pick.d == 1) groups = blob.Select(b => new List<(int, int)> { b }).ToList();
                    foreach (var g in groups)
                    {
                        int gc0 = g.Min(b => b.Item1), gc1 = g.Max(b => b.Item1), gr0 = g.Min(b => b.Item2), gr1 = g.Max(b => b.Item2);
                        int gw = gc1 - gc0 + 1, gh = gr1 - gr0 + 1;
                        float x = Layout.IG * (gc0 + gc1 + 1) / 2f, y = Layout.IG * (gr0 + gr1 + 1) / 2f;
                        float rot = pick.w > pick.d && gh > gw ? 90f : 0f;                 // along the block
                        if (!table && !flat)
                        {
                            // the back to the side of the block with the most wall: N 0, S 180, W 90, E -90
                            float Cover(string side)
                            {
                                float s = 0f;
                                if (side == "N" || side == "S")
                                    for (int c = gc0; c <= gc1; c++) { if (Wall("EW", c, side == "N" ? gr1 + 1 : gr0, out _)) s += 1f; }
                                else
                                    for (int r = gr0; r <= gr1; r++) { if (Wall("NS", side == "E" ? gc1 + 1 : gc0, r, out _)) s += 1f; }
                                return s;
                            }
                            var sides = new[] { ("N", 0f), ("S", 180f), ("W", 90f), ("E", -90f) }
                                .Where(sd => (sd.Item1 == "N" || sd.Item1 == "S") ? pick.w <= gw && pick.d <= gh : pick.w <= gh && pick.d <= gw)
                                .Select(sd => (sd.Item2, cover: Cover(sd.Item1))).Where(sd => sd.cover > 0f).ToList();
                            if (sides.Count > 0) rot = sides.OrderByDescending(sd => sd.cover).First().Item1;
                        }
                        outList.Add(new JArray(pick.sn, Mathf.Round(x * 1000f) / 1000f, Mathf.Round(y * 1000f) / 1000f, rot, null, null));
                        if (trestle)
                        {
                            // forms along both long sides, 0.75 m out, where no wall line runs between
                            string form = pick.w >= 2 ? "Form_300" : "Form_150";
                            bool across = Mathf.Approximately(rot, 90f);
                            foreach (var sgn in new[] { -1f, 1f })
                            {
                                float fx = across ? x + sgn * 0.75f : x, fy = across ? y : y + sgn * 0.75f;
                                if (fx < 0.3f || fy < 0.3f || fx > Layout.W - 0.3f || fy > Layout.D - 0.3f) continue;
                                bool blocked = false;
                                if (!across && Mathf.Abs(fy / Layout.IG - Mathf.Round(fy / Layout.IG)) < 1e-4f)
                                    for (int c = gc0; c <= gc1; c++) blocked |= Wall("EW", c, Mathf.RoundToInt(fy / Layout.IG), out _);
                                if (across && Mathf.Abs(fx / Layout.IG - Mathf.Round(fx / Layout.IG)) < 1e-4f)
                                    for (int r = gr0; r <= gr1; r++) blocked |= Wall("NS", Mathf.RoundToInt(fx / Layout.IG), r, out _);
                                // and only on free cells (or the table's own): a form at a cell edge reaches into the next row
                                float hx = across ? 0.175f : (pick.w >= 2 ? 1.35f : 0.60f), hy = across ? (pick.w >= 2 ? 1.35f : 0.60f) : 0.175f;
                                for (int c = Mathf.FloorToInt((fx - hx) / Layout.IG); c <= Mathf.FloorToInt((fx + hx - 1e-3f) / Layout.IG); c++)
                                    for (int r = Mathf.FloorToInt((fy - hy) / Layout.IG); r <= Mathf.FloorToInt((fy + hy - 1e-3f) / Layout.IG); r++)
                                        if ((P.codes.TryGetValue((c, r), out var cc) && cc.Trim('.', ' ').Length > 0 && cc != code && cc != "fm") || doorway.Contains((c, r)))
                                            blocked = true;
                                if (!blocked) outList.Add(new JArray(form, fx, fy, rot, null, null));
                            }
                        }
                    }
                }
            return outList;
        }
    }
}
