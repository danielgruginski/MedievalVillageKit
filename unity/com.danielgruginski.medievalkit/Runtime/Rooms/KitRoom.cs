using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A room built from a typed plan (vki_rooms.vki_build_scene, structure only): walls by family and height, rakes,
    /// posts (required + rhythm), floors (600 / 300 / Q150 by parity), dais, sills, exits (door, closed leaf, apron,
    /// rush mat, link, spawn), stairs, barred gates, passages, door leaves, pits, doorway mats, window light pools and
    /// the pieces' lights. The plan is the ASCII grid of the Blender kit (docs/INTERIOR_PLANS.md: one cell = 1.5 m,
    /// row 0 is the south / camera side); the room record (JSON) gives the families, zones and their styles, links,
    /// stairs and the rest. Presets are the kit's own rooms (KitInteriorRules).
    /// Blender room space (x east, y north, z up) maps to this transform's local space as (-x, z, -y).
    /// </summary>
    public partial class KitRoom : MonoBehaviour
    {
        public KitInteriorRules rules;
        [Tooltip("A kit room (e.g. VKI_Hovel_F0) whose plan and record Load Preset copies here.")]
        public string preset;
        [TextArea(6, 30)] public string plan;
        [Tooltip("The room record as JSON: family, zones (cells, floor, wall styles), links, stairs, sills, pits...")]
        [TextArea(6, 30)] public string record;
        [Tooltip("Auto: the record's prop list, else furniture from the plan's cell codes. Record / Codes: only that one.")]
        public Furniture furniture = Furniture.Auto;
        [Tooltip("Add the Unity lights of the pieces' light sockets (windows, aprons, hearths, candles).")]
        public bool buildLights = true;
        [Tooltip("Random Cave: the cellular automaton's map size (cells of 1.5 m), seed, chasm, pools and dressing.")]
        public KitCaveGenerator.Options cave = new KitCaveGenerator.Options();
        [Tooltip("Random Dungeon: map size, seed, number of rooms, theme (Dungeon / Crypt / Warren), cave pockets, loops, debris.")]
        public KitDungeonGenerator.Options dungeon = new KitDungeonGenerator.Options();
        [Tooltip("Random Interior: kind (Cottage / Townhouse / Tavern / Workshop), seed, size (0: by kind).")]
        public KitInteriorGenerator.Options interior = new KitInteriorGenerator.Options();
        [Tooltip("Random Connector: a short passage between two maps of a chain (from / to edges, length, openings, seed).")]
        public KitConnectorGenerator.Options connector = new KitConnectorGenerator.Options();

        /// <summary>How pieces are instantiated (the editor keeps prefab links).</summary>
        public static Func<GameObject, Transform, GameObject> Spawn = (prefab, parent) => Instantiate(prefab, parent);

        public class Placed
        {
            public string piece, group, what;
            public float x, y, z, rot;      // Blender room space
            public float atX, atY;          // the requested point (props: before mounting / hugging)
            public string mount;
            public GameObject go;
            public KitPiece kp;
            public Dictionary<string, string> style;
        }

        [NonSerialized] public List<Placed> placed = new List<Placed>();
        [NonSerialized] public List<string> notes = new List<string>();
        [NonSerialized] public List<(Vector3 pos, float w, string type)> lightsBuilt = new List<(Vector3, float, string)>();
        public KitRoomLayout Layout { get; private set; }

        JObject J => rules.Json;
        JObject R;
        string tag;
        bool night;
        Transform shell, props, logic, lightRoot;
        readonly Dictionary<string, Transform> linkObjs = new Dictionary<string, Transform>();

        public void LoadPreset(string name)
        {
            preset = name;
            plan = rules.Plan(name);
            record = rules.Room(name)?.ToString(Newtonsoft.Json.Formatting.Indented);
        }

        /// <summary>a random cave level (KitCaveGenerator) from the `cave` settings: fills the plan and record, builds</summary>
        public void RandomCave()
        {
            var (p, r) = KitCaveGenerator.Generate(cave);
            preset = "";
            plan = p;
            record = r.ToString(Newtonsoft.Json.Formatting.Indented);
            Generate();
        }

        /// <summary>a random house ground floor (KitInteriorGenerator) from the `interior` settings: fills the plan and record, builds</summary>
        public void RandomInterior()
        {
            var (p, r) = KitInteriorGenerator.Generate(interior, CodeFootprint);
            preset = "";
            plan = p;
            record = r.ToString(Newtonsoft.Json.Formatting.Indented);
            Generate();
        }

        /// <summary>a furniture code's footprint in cells: its largest piece (what PropsFromCodes picks for a block that fits it)</summary>
        (int, int) CodeFootprint(string code)
        {
            var best = (1, 1);
            foreach (var kv in (JObject)rules.Json["codes"])
            {
                if ((string)kv.Value != code) continue;
                var piece = Resolve(kv.Key);
                var f = piece != null ? rules.Prefab(piece).GetComponent<KitPiece>()?.Get("vki_fp_cells") : null;
                if (f == null && piece != null && rules.Json["reuse"]?[piece]?["fp"] is JArray rf) f = $"{(int)rf[0]},{(int)rf[1]}";
                if (f == null) continue;
                var a = f.Split(',');
                var wd = (int.Parse(a[0]), int.Parse(a[1]));
                if (wd.Item1 * wd.Item2 > best.Item1 * best.Item2) best = wd;
            }
            return best;
        }

        /// <summary>a random dungeon level (KitDungeonGenerator) from the `dungeon` settings: fills the plan and record, builds</summary>
        public void RandomDungeon()
        {
            var inv = new Dictionary<string, List<string>>();
            foreach (var kv in (JObject)rules.Json["codes"])
            {
                if (!inv.TryGetValue((string)kv.Value, out var l)) inv[(string)kv.Value] = l = new List<string>();
                l.Add(kv.Key);
            }
            (int, int) Fp(string code)          // the largest piece of a code (what PropsFromCodes picks for a block that fits it)
            {
                var best = (1, 1);
                if (!inv.TryGetValue(code, out var shorts)) return best;
                foreach (var sn in shorts)
                {
                    var piece = Resolve(sn);
                    var f = piece != null ? rules.Prefab(piece).GetComponent<KitPiece>()?.Get("vki_fp_cells") : null;
                    if (f == null) continue;
                    var a = f.Split(',');
                    var wd = (int.Parse(a[0]), int.Parse(a[1]));
                    if (wd.Item1 * wd.Item2 > best.Item1 * best.Item2) best = wd;
                }
                return best;
            }
            var (p, r) = KitDungeonGenerator.Generate(dungeon, Fp);
            preset = "";
            plan = p;
            record = r.ToString(Newtonsoft.Json.Formatting.Indented);
            Generate();
        }

        /// <summary>a connector between two maps of a chain (KitConnectorGenerator) from the `connector` settings</summary>
        public void RandomConnector()
        {
            var (p, r) = KitConnectorGenerator.Generate(connector);
            preset = "";
            plan = p;
            record = r.ToString(Newtonsoft.Json.Formatting.Indented);
            Generate();
        }

        public void Clear()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                var c = transform.GetChild(i).gameObject;
                if (Application.isPlaying) Destroy(c); else DestroyImmediate(c);
            }
            placed.Clear();
            lightsBuilt.Clear();
        }

        public void Generate()
        {
            Clear();
            notes.Clear();
            linkObjs.Clear();
            if (rules == null) { notes.Add("no rules asset"); return; }
            R = JObject.Parse(string.IsNullOrWhiteSpace(record) ? "{}" : record);
            Defaults(R);
            Layout = KitRoomLayout.Build(J, R, plan, FpCells);
            notes.AddRange(Layout.problems);
            string nm = string.IsNullOrEmpty(preset) ? name : preset;
            tag = nm.StartsWith("VKI_") ? nm.Substring(4) : nm;
            night = (string)R["preset"] == "Night";
            shell = Group("Shell"); props = Group("Props"); logic = Group("Logic"); lightRoot = Group("Lights");

            foreach (var pc in Layout.pieces)
            {
                var o = Put(shell, pc.piece, pc.x, pc.y, pc.rot, 0f, WallStyle(pc), "wall");
                if (o == null) continue;
                o.kp?.Set("vki_room_role", pc.role);
                if (pc.kind == "Exit" || pc.kind == "ExitWide") Exit(pc, o);
                else if (pc.kind == "BarsGate") Gate(pc, o);
                else if (pc.kind == "Passage" || (pc.kind == "Named" && R["passages"]?[pc.Key] != null)) Passage(pc, o);
                if (R["door_leaves"]?[pc.Key] != null) DoorLeaf(pc, o);
            }
            foreach (var gt in Layout.grounds)              // cave maps: chasm / stream / channel ground tiles
            {
                var st = gt.floorStyle != null ? new Dictionary<string, string> { ["floor"] = gt.floorStyle } : null;
                var o = Put(shell, gt.piece, gt.x, gt.y, gt.rot, 0f, st, "ground");
                if (o != null && gt.flow is Vector2 fl)     // the water's direction, for water shaders
                    o.kp?.Set("vki_flow", $"[{fl.x.ToString(System.Globalization.CultureInfo.InvariantCulture)}, {fl.y.ToString(System.Globalization.CultureInfo.InvariantCulture)}]");
            }
            foreach (var rk in Layout.rocks)                // cave maps: the dual-grid rock tiles
            {
                string piece = rk.piece;
                if (rules.Prefab(piece) == null && (piece.EndsWith("_B") || piece.EndsWith("_C"))) piece = piece.Substring(0, piece.Length - 1) + "A";
                var o = Put(shell, piece, rk.x, rk.y, rk.rot, 0f, null, "rock");
                if (o == null) continue;
                o.kp?.Set("vki_room_role", "rock");
                if (rk.tunnel != null) Tunnel(rk, o);
            }
            foreach (var p in Layout.posts) if (p.req) Put(shell, p.piece, p.x, p.y, p.rot, 0f, null, "post");
            foreach (var f in Layout.floors)
            {
                var st = f.floorStyle != null && f.floorStyle != "Boards_NS" ? new Dictionary<string, string> { ["floor"] = f.floorStyle } : null;
                Put(shell, f.piece, f.x, f.y, 0f, 0f, st, f.piece.Contains("Dais") ? "dais" : "floor");
            }
            foreach (var s in R["sills"] as JArray ?? new JArray())
                Put(shell, "SM_VKI_Floor_Sill_150", (float)s[0], (float)s[1], (float)s[2], (float)s[3], null, "sill");
            foreach (var s in R["stairs"] as JArray ?? new JArray())
                Stair((string)s[0], (float)s[1], (float)s[2], (float)s[3], (string)s[4], s.Count() > 5 ? (string)s[5] : "RailR");
            foreach (var pt in R["pits"] as JArray ?? new JArray())
                Put(shell, KitInteriorRules.Full((string)pt[0]), (float)pt[1], (float)pt[2], 0f, 0f, null, "pit");
            Portals();
            Furnish();                     // before the rhythm posts and doorway mats, which make room for props
            Encounters();
            Markers();
            Rhythm();
            Mats();
            Pools();
            Debris();                       // loose debris by zone theme (R["debris"])
            KitDecks.Apply(transform);      // bridges: walkable decks, the chasm's blocking boxes cut round them
            if (buildLights) Lights();
        }

        /// <summary>a bare plan still builds: timber walls, a board floor, a front exit back to where one came from</summary>
        static void Defaults(JObject r)
        {
            if (!(r["family"] is JObject)) r["family"] = new JObject { ["perimeter"] = "Timber", ["partition"] = "Board" };
            if (!(r["zones"] is JObject z) || z.Count == 0) r["zones"] = new JObject { ["room"] = new JObject { ["cells"] = "rest", ["floor"] = "Boards_NS" } };
            if (!(r["links"] is JArray)) { var l = new JArray(); l.Add(new JArray("front", "exit", "@return")); r["links"] = l; }   // new JArray(JArray) would copy
            if (r["preset"] == null) r["preset"] = "Day";
        }

        Transform Group(string n)
        {
            var t = new GameObject(n).transform;
            t.SetParent(transform, false);
            return t;
        }

        string FpCells(string piece) => rules.Prefab(piece)?.GetComponent<KitPiece>()?.Get("vki_fp_cells");

        static Vector2 Frame(float x, float y, float rot, float lx, float ly)
        {
            double r = rot * Math.PI / 180.0, c = Math.Cos(r), s = Math.Sin(r);
            return new Vector2((float)(x + c * lx - s * ly), (float)(y + s * lx + c * ly));
        }

        static float R4(float v) => (float)Math.Round(v, 4);
        static float Mod360(float a) => ((a % 360f) + 360f) % 360f;

        static JToken PropJ(KitPiece kp, string key)
        {
            string v = kp?.Get(key);
            if (v == null) return null;
            if (v.Length > 0 && (v[0] == '[' || v[0] == '{'))
                try { return JToken.Parse(v); } catch (Exception) { return v; }
            return v;
        }

        // ------------------------------------------------------------------ placement (vki_rooms_put)
        Placed Put(Transform parent, string piece, float x, float y, float rot, float z, Dictionary<string, string> style, string what)
        {
            var prefab = rules.Prefab(piece);
            if (prefab == null) { notes.Add($"no prefab {piece} ({what} at {x:0.##}, {y:0.##})"); return null; }
            var go = Spawn(prefab, parent);
            string shortName = piece.StartsWith("SM_VKI_") ? piece.Substring(7) : piece.StartsWith("SM_VK_") ? piece.Substring(6) : piece;
            go.name = $"{tag}_{shortName}";
            go.transform.localPosition = new Vector3(-x, z, -y);
            go.transform.localRotation = Quaternion.Euler(0f, -rot, 0f);
            go.transform.localScale = Vector3.one;
            var kp = go.GetComponent<KitPiece>();
            var st = new Dictionary<string, string>();
            bool reuse = piece.StartsWith("SM_VK_") && !piece.StartsWith("SM_VKI_");
            if (reuse)
                foreach (var kv in (JObject)J["reuse_style"]) st[kv.Key] = (string)kv.Value;
            if (style != null) foreach (var kv in style) st[kv.Key] = kv.Value;
            if (night)
            {
                if (reuse) { if (style == null || !style.ContainsKey("window")) st["window"] = "Window_Night"; }
                else if (Uses(kp, (int)J["slots"]["window"], (int)J["slots"]["stained"]))
                    foreach (var kv in (JObject)J["night_style"])
                        if (style == null || !style.ContainsKey(kv.Key)) st[kv.Key] = (string)kv.Value;
            }
            if (st.Count > 0) ApplyStyle(go, kp, st);
            if (reuse && piece.StartsWith("SM_VK_Prop_")) KitSolid.Box(go);      // an exterior prop has no vki_collider: walked through
            var p = new Placed { piece = piece, group = parent.name, what = what, x = x, y = y, z = z, rot = rot, atX = x, atY = y, go = go, kp = kp, style = st };
            placed.Add(p);
            return p;
        }

        static bool Uses(KitPiece kp, params int[] slots) => kp != null && kp.blenderSlots.Any(slots.Contains);

        /// <summary>vki_variant_apply: each style key swaps the material of its Blender slot (wall_b defaults to wall_a).</summary>
        void ApplyStyle(GameObject go, KitPiece kp, Dictionary<string, string> style)
        {
            var mr = go.GetComponent<MeshRenderer>();
            if (kp == null || mr == null) return;
            var st = new Dictionary<string, string>(style);
            if (st.ContainsKey("wall_a") && !st.ContainsKey("wall_b")) st["wall_b"] = st["wall_a"];
            var mats = mr.sharedMaterials;
            bool changed = false;
            foreach (var kv in st)
            {
                var slot = J["slots"][kv.Key];
                if (slot == null) continue;
                int s = (int)slot;
                if (!kp.blenderSlots.Contains(s)) continue;
                string mn = rules.StyleMatName(kv.Key, kv.Value);
                var m = rules.Mat(mn);
                if (m == null) { notes.Add($"{go.name}: no material for {kv.Key}={kv.Value} ({mn ?? "not in the style table"})"); continue; }
                for (int i = 0; i < mats.Length && i < kp.blenderSlots.Length; i++)
                    if (kp.blenderSlots[i] == s && mats[i] != m) { mats[i] = m; changed = true; }
            }
            if (changed) mr.sharedMaterials = mats;
        }

        // ------------------------------------------------------------------ vki_rooms_wall_style
        Dictionary<string, string> WallStyle(KitRoomLayout.Piece pc)
        {
            var zones = (JObject)R["zones"];
            string famDef = (string)J["families"][pc.fam]["wall_a"];
            string Zs(List<(int, int)> cells, string key)
            {
                foreach (var c in cells)
                    if (Layout.zmap.TryGetValue(c, out var zn) && zn != null && zones[zn]?[key] != null && (string)zones[zn][key] != "")
                        return (string)zones[zn][key];
                return null;
            }
            var st = new Dictionary<string, string>();
            if (pc.role == "part")
            {
                if ((string)R["partition_wall"] == "zone")
                {
                    st["wall_a"] = Zs(pc.faceA, "wall") ?? famDef;
                    st["wall_b"] = Zs(pc.faceB, "wall") ?? famDef;
                }
            }
            else
            {
                st["wall_a"] = Zs(pc.faceA, "wall") ?? famDef;
                st["wall_b"] = (string)R["exterior"] ?? famDef;
            }
            if (st.Count > 0 && st["wall_a"] == famDef && st["wall_b"] == famDef) st.Clear();
            string cap = Zs(pc.faceA, "cap");
            if (cap != null) st["cap"] = cap;
            if (pc.kind == "Special" && R["special_style"] is JObject ss)
                foreach (var kv in ss) st[kv.Key] = (string)kv.Value;
            if (pc.kind == "Window" && pc.height == "Full" && R["window_style"] is JObject ws)
                foreach (var kv in ws) st[kv.Key] = (string)kv.Value;
            return st;
        }

        static Dictionary<string, string> StyleOf(JToken t) =>
            t is JObject o ? o.Properties().ToDictionary(p => p.Name, p => (string)p.Value) : null;

        // ------------------------------------------------------------------ links and spawns
        void Link(Placed o, string kind, string id, string target, string prompt)
        {
            var kp = o.kp;
            kp?.Set("vki_link", kind); kp?.Set("vki_link_id", id); kp?.Set("vki_target", target);
            kp?.Set("vki_prompt", prompt); kp?.Set("vki_facing_min", "60");
            var l = o.go.GetComponent<KitLink>() ?? o.go.AddComponent<KitLink>();
            l.linkId = id; l.kind = kind; l.target = target; l.prompt = prompt; l.facingMin = 60f;
            if (LinkEntry(id) is JArray le && le.Count > 3 && le[3].Type == JTokenType.String) l.arrive = (string)le[3];   // [id, kind, target, arrive]
            if (PropJ(kp, "vki_trigger") is JArray b && b.Count >= 6 && o.go.GetComponents<BoxCollider>().All(c => !c.isTrigger))
            {
                var c = o.go.AddComponent<BoxCollider>();
                c.isTrigger = true;
                c.center = new Vector3(-(float)b[0], (float)b[2], -(float)b[1]);
                c.size = new Vector3(Mathf.Abs((float)b[3]), Mathf.Abs((float)b[5]), Mathf.Abs((float)b[4]));
            }
            linkObjs[id] = o.go.transform;
        }

        /// <summary>R["portals"] (generated maps chained into a world): a KitPortalMarker on the middle of each opening
        /// on the map's edge, facing out, and a spawn a cell and a half in, facing in</summary>
        void Portals()
        {
            foreach (var pt in KitPortal.Of(R))
            {
                if (pt.at < 0) { notes.Add($"portal {pt.id}: no opening (at -1)"); continue; }
                var sp = pt.SeamPoint(Layout.P.nc, Layout.P.nr, Layout.IG);
                var go = new GameObject("PRT_" + pt.id);
                go.transform.SetParent(logic, false);
                go.transform.localPosition = new Vector3(-sp.x, 0f, -sp.y);
                go.transform.localRotation = KitSpawn.FromBearing(KitPortal.Inward(pt.Side) + 180f);
                var m = go.AddComponent<KitPortalMarker>();
                m.portalId = pt.id; m.side = pt.Side.ToString(); m.at = pt.at; m.width = pt.width; m.target = pt.target; m.seam = pt.seam;
                var (dx, dy) = KitPortal.Outward(pt.Side);
                float inset = 1.5f * Layout.IG;
                SpawnPoint(pt.id, R4(sp.x - dx * inset), R4(sp.y - dy * inset), KitPortal.Inward(pt.Side), null);
            }
        }

        void SpawnPoint(string id, float x, float y, float facing, Placed host)
        {
            var go = new GameObject("SPN_" + id);
            go.transform.SetParent(logic, false);
            go.transform.localPosition = new Vector3(-x, 0f, -y);
            go.transform.localRotation = KitSpawn.FromBearing(facing);
            var sp = go.AddComponent<KitSpawn>();
            sp.spawnId = id;
            sp.facingDeg = facing;
            var m = go.AddComponent<KitMarker>();
            m.kind = KitMarker.Kind.Spawn;
            m.props = new List<KitProp>
            {
                new KitProp { key = "vki_spawn_id", value = id },
                new KitProp { key = "vki_facing_deg", value = facing.ToString(System.Globalization.CultureInfo.InvariantCulture) },
                new KitProp { key = "vki_link_obj", value = host?.go.name ?? "" },
            };
        }

        JToken LinkEntry(string id) => (R["links"] as JArray ?? new JArray()).FirstOrDefault(l => (string)l[0] == id);

        /// <summary>vki_rooms_exit: door + closed leaf (two for a wide door) + apron + rush mat inside + link + spawn</summary>
        void Exit(KitRoomLayout.Piece pc, Placed door)
        {
            float T = (float)J["t"][pc.cls];
            bool wide = pc.kind == "ExitWide";
            float Lp = (float)J["ig"] * pc.n;
            var socks = PropJ(door.kp, "vki_leaf_socket") as JArray;
            var leaves = new List<(string piece, float sx, float sy)>();
            if (wide)
            {
                if (!(socks != null && socks.Count > 0 && socks[0] is JArray))
                    socks = new JArray(new JArray(0.60, -T / 2 + 0.05, 0.0), new JArray(2.40, -T / 2 + 0.05, 0.0));
                var lv = PropJ(door.kp, "vki_leaf") as JArray;
                var names = lv != null && lv.Count == 2 ? lv.Select(x => (string)x).ToArray()
                    : pc.fam == "Ashlar" ? new[] { "SM_VKI_Leaf_Wide160_Cut_L", "SM_VKI_Leaf_Wide160_Cut_R" }
                    : new[] { "SM_VKI_Leaf_Wide_Cut_L", "SM_VKI_Leaf_Wide_Cut_R" };
                for (int i = 0; i < 2; i++) leaves.Add((names[i], (float)socks[i][0], (float)socks[i][1]));
            }
            else
            {
                float sx = 0.33f, sy = -T / 2 + 0.05f;
                if (socks != null && socks.Count > 0 && !(socks[0] is JArray)) { sx = (float)socks[0]; sy = (float)socks[1]; }
                string lv = PropJ(door.kp, "vki_leaf") is JValue v && v.Type == JTokenType.String ? (string)v : null;
                lv = lv != null && lv.EndsWith("_Cut") && rules.Prefab(lv) != null ? lv : null;
                leaves.Add((lv ?? "SM_VKI_Leaf_Plank_Cut", sx, sy));
            }
            foreach (var (lp, sx, sy) in leaves)
            {
                var w = Frame(pc.x, pc.y, pc.rot, sx, sy);
                var lf = Put(shell, lp, R4(w.x), R4(w.y), pc.rot, 0f, null, "leaf");
                lf?.kp?.Set("vki_leaf_state", "closed");
                lf?.kp?.Set("vki_leaf_deg", "0");
                lf?.kp?.Set("vki_leaf_door", door.go.name);
            }
            string apron; float off;
            if (wide && rules.Prefab("SM_VKI_Apron_Wide_300x150") != null) { apron = "SM_VKI_Apron_Wide_300x150"; off = 0f; }
            else { apron = "SM_VKI_Apron_300x150"; off = wide ? 0.75f : 0f; }
            var a = Frame(pc.x, pc.y, pc.rot, off, 0f);
            Put(shell, apron, R4(a.x), R4(a.y), pc.rot, 0f, StyleOf(R["apron_style"]), "apron");
            var m = Frame(pc.x, pc.y, pc.rot, Lp / 2, -0.75f);
            Put(props, "SM_VKI_RushMat", R4(m.x), R4(m.y), 0f, 0f, null, "exitmat");
            var lk = (R["links"] as JArray ?? new JArray()).FirstOrDefault(l => (string)l[1] == "exit");
            string id = lk != null ? (string)lk[0] : "front", target = lk != null ? (string)lk[2] : "@return";
            Link(door, "exit", id, target, "Leave");
            var sl = PropJ(door.kp, "vki_spawn_local") as JArray;
            var s = Frame(pc.x, pc.y, pc.rot, sl != null ? (float)sl[0] : Lp / 2, sl != null ? (float)sl[1] : -1.60f);
            SpawnPoint(id, R4(s.x), R4(s.y), Mod360(180f - pc.rot), door);
        }

        /// <summary>vki_rooms_stair: the stair piece carries the link; spawn at its vki_spawn_local</summary>
        void Stair(string kind, float x, float y, float rot, string lid, string var)
        {
            var o = Put(shell, $"SM_VKI_Stair_{kind}_150x450_{var}", x, y, rot, 0f, null, "stair");
            if (o == null) return;
            var lk = LinkEntry(lid);
            Link(o, kind == "Up" ? "stair_up" : "stair_down", lid, lk != null ? (string)lk[2] : "", kind == "Up" ? "Go upstairs" : "Go downstairs");
            var sl = PropJ(o.kp, "vki_spawn_local") as JArray;
            float lx = sl != null ? (float)sl[0] : (kind == "Up" ? 0.75f : 2.25f), ly = sl != null ? (float)sl[1] : (kind == "Up" ? -0.75f : 3.75f);
            float fac = o.kp != null && o.kp.Has("vki_spawn_facing") ? o.kp.GetFloat("vki_spawn_facing") : (kind == "Up" ? 180f : 90f);
            var s = Frame(x, y, rot, lx, ly);
            SpawnPoint(lid, R4(s.x), R4(s.y), Mod360(fac - rot), o);
        }

        /// <summary>vki_rooms_passage: the wall piece carries the link R["passages"][key]</summary>
        void Passage(KitRoomLayout.Piece pc, Placed o)
        {
            string lid = (string)R["passages"]?[pc.Key];
            var lk = lid != null ? LinkEntry(lid) : null;
            if (lk == null) { notes.Add($"passage at {pc.ori} ({pc.k},{pc.line}) has no R['passages'] / links entry"); return; }
            Link(o, "passage", lid, (string)lk[2], o.kp?.Get("vki_prompt_text") ?? "Go through");
            var sl = PropJ(o.kp, "vki_spawn_local") as JArray;
            var s = Frame(pc.x, pc.y, pc.rot, sl != null ? (float)sl[0] : 0.75f, sl != null ? (float)sl[1] : -1.60f);
            SpawnPoint(lid, R4(s.x), R4(s.y), Mod360(180f - pc.rot), o);
        }

        /// <summary>R["encounters"] (generated dungeons): a KitEncounter per room, its spawn points as children</summary>
        void Encounters()
        {
            if (!(R["encounters"] is JArray es)) return;
            foreach (var e in es)
            {
                var box = e["box"];
                float x0 = (float)box[0], y0 = (float)box[1], x1 = (float)box[2], y1 = (float)box[3];
                var go = new GameObject("ENC_" + (string)e["id"]);
                go.transform.SetParent(logic, false);
                go.transform.localPosition = new Vector3(-(x0 + x1) / 2f, 0f, -(y0 + y1) / 2f);
                var en = go.AddComponent<KitEncounter>();
                en.encounterId = (string)e["id"]; en.roomType = (string)e["room"]; en.creature = (string)e["creature"];
                en.budget = (int?)e["budget"] ?? 1; en.depth = (int?)e["depth"] ?? 0; en.boss = (bool?)e["boss"] ?? false;
                en.size = new Vector3(x1 - x0, 3f, y1 - y0);
                int k = 0;
                foreach (var pt in e["points"] as JArray ?? new JArray())
                {
                    var sp = new GameObject($"Spawn_{k++}").transform;
                    sp.SetParent(go.transform, false);
                    sp.localPosition = new Vector3(-(float)pt[0], 0f, -(float)pt[1]) - go.transform.localPosition;
                }
            }
        }

        /// <summary>R["markers"] ([{id, role, at: [x, y], facing, note}]: loot to search, an npc's place...): a KitMarker each
        /// (vki_role, vki_marker_id, vki_facing_deg, vki_note) for the game</summary>
        void Markers()
        {
            foreach (var m in R["markers"] as JArray ?? new JArray())
            {
                var at = m["at"] as JArray;
                if (at == null || at.Count < 2) continue;
                float facing = (float?)m["facing"] ?? 0f;
                var go = new GameObject($"MRK_{(string)m["role"]}_{(string)m["id"]}");
                go.transform.SetParent(logic, false);
                go.transform.localPosition = new Vector3(-(float)at[0], 0f, -(float)at[1]);
                go.transform.localRotation = KitSpawn.FromBearing(facing);
                var mk = go.AddComponent<KitMarker>();
                mk.kind = KitMarker.Kind.Other;
                mk.props = new List<KitProp>
                {
                    new KitProp { key = "vki_role", value = (string)m["role"] ?? "" },
                    new KitProp { key = "vki_marker_id", value = (string)m["id"] ?? "" },
                    new KitProp { key = "vki_facing_deg", value = facing.ToString(System.Globalization.CultureInfo.InvariantCulture) },
                };
                if (m["note"] != null) mk.props.Add(new KitProp { key = "vki_note", value = (string)m["note"] });
            }
        }

        /// <summary>vki_cave_tunnel: a tunnel tile carries its scene link, as a passage</summary>
        void Tunnel(KitRoomLayout.Rock rk, Placed o)
        {
            var lk = LinkEntry(rk.tunnel);
            if (lk == null) { notes.Add($"tunnel {rk.tunnel} at node ({rk.node.Item1},{rk.node.Item2}) has no links entry"); return; }
            Link(o, "passage", rk.tunnel, (string)lk[2], o.kp?.Get("vki_prompt_text") ?? "Go through");
            var sl = PropJ(o.kp, "vki_spawn_local") as JArray;
            var sp = Frame(rk.x, rk.y, rk.rot, sl != null ? (float)sl[0] : 0f, sl != null ? (float)sl[1] : -1.60f);
            SpawnPoint(rk.tunnel, R4(sp.x), R4(sp.y), Mod360(180f - rk.rot), o);
        }

        /// <summary>vki_rooms_door_leaf: R["door_leaves"][key] = {piece, deg, z, socket, state}</summary>
        void DoorLeaf(KitRoomLayout.Piece pc, Placed door)
        {
            var spec = R["door_leaves"][pc.Key];
            string piece = KitInteriorRules.Full((string)spec["piece"]);
            JToken s = spec["socket"] is JArray sj && sj.Count > 0 ? sj : PropJ(door.kp, "vki_leaf_socket");
            if (!(s is JArray sa && sa.Count > 0)) s = new JArray(0.33, -0.2, 0.0);
            if (s[0] is JArray) s = s[0];
            float deg = spec["deg"] != null ? (float)spec["deg"] : 0f, z = spec["z"] != null ? (float)spec["z"] : 0f;
            var w = Frame(pc.x, pc.y, pc.rot, (float)s[0], (float)s[1]);
            var lf = Put(shell, piece, R4(w.x), R4(w.y), pc.rot - deg, z, null, "leaf");
            lf?.kp?.Set("vki_leaf_state", (string)spec["state"] ?? (deg != 0f || z != 0f ? "open" : "closed"));
            lf?.kp?.Set("vki_leaf_deg", deg.ToString(System.Globalization.CultureInfo.InvariantCulture));
            lf?.kp?.Set("vki_leaf_door", door.go.name);
        }

        /// <summary>vki_rooms_gate: the barred door's own leaf, opened R["gates"][key] degrees (default gate_deg)</summary>
        void Gate(KitRoomLayout.Piece pc, Placed door)
        {
            string lv = door.kp?.Get("vki_leaf");
            if (lv == null || lv.StartsWith("[")) return;
            var s = PropJ(door.kp, "vki_leaf_socket") as JArray ?? new JArray(0.33, -0.022, 0.0);
            float deg = R["gates"]?[pc.Key] != null ? (float)R["gates"][pc.Key] : (float)J["gate_deg"];
            var w = Frame(pc.x, pc.y, pc.rot, (float)s[0] + (deg < 0 ? 0.045f : 0f), (float)s[1]);
            var lf = Put(shell, lv, R4(w.x), R4(w.y), pc.rot - deg, 0f, null, "gate");
            lf?.kp?.Set("vki_leaf_state", deg != 0f ? "open" : "closed");
            lf?.kp?.Set("vki_leaf_deg", deg.ToString(System.Globalization.CultureInfo.InvariantCulture));
            lf?.kp?.Set("vki_leaf_door", door.go.name);
        }

        // ------------------------------------------------------------------ boxes (vki_rooms_obj_box / wall_env)
        public struct Box
        {
            public Vector3 a, b;
            public bool Hits(Box o) => a.x < o.b.x && o.a.x < b.x && a.y < o.b.y && o.a.y < b.y && a.z < o.b.z && o.a.z < b.z;
        }

        /// <summary>world (room) AABB of a placed piece's mesh, in Blender room space</summary>
        public static Box ObjBox(Placed p)
        {
            var mf = p.go.GetComponent<MeshFilter>();
            var mb = mf != null && mf.sharedMesh != null ? mf.sharedMesh.bounds : new Bounds();
            float[] xs = { -mb.max.x, -mb.min.x }, ys = { -mb.max.z, -mb.min.z };
            var lo = new Vector3(float.MaxValue, float.MaxValue, p.z + mb.min.y);
            var hi = new Vector3(float.MinValue, float.MinValue, p.z + mb.max.y);
            foreach (var lx in xs)
                foreach (var ly in ys)
                {
                    var w = Frame(p.x, p.y, p.rot, lx, ly);
                    lo.x = Mathf.Min(lo.x, w.x); lo.y = Mathf.Min(lo.y, w.y);
                    hi.x = Mathf.Max(hi.x, w.x); hi.y = Mathf.Max(hi.y, w.y);
                }
            return new Box { a = lo, b = hi };
        }

        Box WallEnv(Placed p)
        {
            float L = p.kp.Has("vki_len") ? p.kp.GetFloat("vki_len") : 1.5f;
            string cls = p.kp.GetFloat("vki_thick", 0.5f) < 0.4f ? "P" : "O";
            float chw = J["cap_hw"]?[cls] != null ? (float)J["cap_hw"][cls] : (cls == "O" ? 0.28f : 0.18f);
            string fam = p.kp.Get("vki_family");
            float H = p.kp.Get("vki_height", "Full") == "Cut" ? (float)J["cut_h"]
                : fam != null && J["families"][fam] != null ? (float)J["families"][fam]["H"] : 3f;
            var lo = new Vector3(float.MaxValue, float.MaxValue, -0.30f);
            var hi = new Vector3(float.MinValue, float.MinValue, H);
            foreach (var lx in new[] { 0f, L })
                foreach (var ly in new[] { -chw, chw })
                {
                    var w = Frame(p.x, p.y, p.rot, lx, ly);
                    lo.x = Mathf.Min(lo.x, w.x); lo.y = Mathf.Min(lo.y, w.y);
                    hi.x = Mathf.Max(hi.x, w.x); hi.y = Mathf.Max(hi.y, w.y);
                }
            return new Box { a = lo, b = hi };
        }

        string Cls(Placed p) => p.kp?.Get("vki_class") ?? "prop";
        static bool Truthy(string v) => !string.IsNullOrEmpty(v) && v != "0" && v != "False" && v != "false";

        /// <summary>vki_rooms_rhythm: optional rhythm Mid posts, skipped where a prop, overlay or stair touches the post square</summary>
        void Rhythm()
        {
            var obst = placed.Where(p => ((Cls(p) == "prop" || Cls(p) == "overlay") && !Truthy(p.kp?.Get("vki_edge"))) ||
                                         p.kp?.Get("vki_link") == "stair_up" || p.kp?.Get("vki_link") == "stair_down")
                             .Select(p => (p, box: ObjBox(p))).ToList();
            foreach (var p in Layout.posts)
            {
                if (p.req) continue;
                string cls = (string)J["families"][p.fam]["cls"];
                float hx = (float)J["mid_hw"][cls][0], hy = (float)J["mid_hw"][cls][1];
                if (Mathf.Approximately(p.rot, 90f)) (hx, hy) = (hy, hx);
                float top = (p.height == "Full" ? (float)J["families"][p.fam]["H"] : (float)J["cut_h"]) + (float)J["post_top"];
                var box = new Box
                {
                    a = new Vector3(p.x - hx - 0.005f, p.y - hy - 0.005f, (float)J["post_z0"]),
                    b = new Vector3(p.x + hx + 0.005f, p.y + hy + 0.005f, top)
                };
                var hit = obst.FirstOrDefault(o => box.Hits(o.box));
                if (hit.p != null) { notes.Add($"rhythm post at node ({p.node.Item1},{p.node.Item2}) skipped: {hit.p.go.name}"); continue; }
                Put(shell, p.piece, p.x, p.y, p.rot, 0f, null, "rhythm");
            }
        }

        /// <summary>vki_rooms_mats: a RushMat each side of every N-S Cut doorway, shifted 0.75 along it when blocked</summary>
        void Mats()
        {
            if (R["rush_mats"] != null && R["rush_mats"].Type == JTokenType.Boolean && !(bool)R["rush_mats"]) return;
            var kinds = new HashSet<string> { "wall", "post", "prop", "overlay", "link", "leaf" };
            foreach (var pc in Layout.pieces)
            {
                if (pc.kind != "Door" || pc.ori != "NS") continue;
                var obst = placed.Where(p => kinds.Contains(Cls(p))).Select(p => Cls(p) == "wall" ? WallEnv(p) : ObjBox(p)).ToList();
                float x0 = pc.x, yc = pc.y + (Mathf.Approximately(pc.rot, 90f) ? 0.75f : -0.75f);
                foreach (var sx in new[] { -0.75f, 0.75f })
                {
                    bool done = false;
                    foreach (var dy in new[] { 0f, 0.75f, -0.75f })
                    {
                        float cx = x0 + sx, cy = yc + dy;
                        var rect = new Box { a = new Vector3(cx - 0.40f, cy - 0.60f, 0f), b = new Vector3(cx + 0.40f, cy + 0.60f, 0.03f) };
                        if (cx - 0.4f < 0 || cx + 0.4f > Layout.W || cy - 0.6f < 0 || cy + 0.6f > Layout.D) continue;
                        if (obst.Any(b => rect.Hits(b))) continue;
                        Put(props, "SM_VKI_RushMat", cx, cy, 90f, 0f, null, "doormat");
                        obst.Add(rect);
                        done = true;
                        break;
                    }
                    if (!done) notes.Add($"doorway mat at x {x0 + sx:0.00}, y {yc:0.00} skipped (no free spot)");
                }
            }
        }

        /// <summary>vki_rooms_pools: FX_WindowPool under every Full window / lancet in Day rooms</summary>
        void Pools()
        {
            if (night || (R["pools"] != null && R["pools"].Type == JTokenType.Boolean && !(bool)R["pools"]) ||
                rules.Prefab("SM_VKI_FX_WindowPool") == null) return;
            var dais = (R["dais"] as JArray ?? new JArray()).Select(d => ((float)d[0], (float)d[1])).ToList();
            foreach (var pc in Layout.pieces)
            {
                if ((pc.kind != "Window" && pc.kind != "Lancet" && pc.kind != "LancetTall") || pc.height != "Full") continue;
                var c = Frame(pc.x, pc.y, pc.rot, 0.75f, -1.15f);
                float z = dais.Any(d => d.Item1 <= c.x && c.x <= d.Item1 + 3f && d.Item2 <= c.y && c.y <= d.Item2 + 3f) ? 0.20f : 0f;
                Put(props, "SM_VKI_FX_WindowPool", pc.x, pc.y, pc.rot, z, null, "pool");
            }
        }

        /// <summary>vki_rooms_lights: a Unity light per vki_lights socket of the placed pieces (Day / Night power)</summary>
        void Lights()
        {
            int n = 0;
            foreach (var p in placed.Where(q => q.group == "Shell").Concat(placed.Where(q => q.group == "Props")))
            {
                if (!(PropJ(p.kp, "vki_lights") is JArray ls)) continue;
                foreach (var Ls in ls)
                {
                    string typ = (string)Ls["type"] ?? "POINT";
                    float wd = (float?)Ls["w_day"] ?? (float?)Ls["w"] ?? 100f, wn = (float?)Ls["w_night"] ?? (float?)Ls["w"] ?? 100f;
                    var cd = Ls["color_day"] ?? Ls["color"] ?? new JArray(1, 1, 1);
                    var cn = Ls["color_night"] ?? Ls["color"] ?? new JArray(1, 1, 1);
                    float w = night ? wn : wd;
                    var col = night ? cn : cd;
                    var pl = Ls["pos"];
                    var pw = Frame(p.x, p.y, p.rot, (float)pl[0], (float)pl[1]);
                    var pos = new Vector3(-pw.x, p.z + (float)pl[2], -pw.y);
                    var go = new GameObject($"LIT_{tag}_{n:00}_{(string)Ls["role"] ?? typ.ToLowerInvariant()}");
                    go.transform.SetParent(lightRoot, false);
                    go.transform.localPosition = pos;
                    if (Ls["aim"] is JArray am)
                    {
                        var aw = Frame(p.x, p.y, p.rot, (float)am[0], (float)am[1]);
                        var dir = new Vector3(-aw.x, p.z + (float)am[2], -aw.y) - pos;
                        if (dir.sqrMagnitude > 1e-8f) go.transform.localRotation = Quaternion.LookRotation(dir, Mathf.Abs(dir.normalized.y) > 0.999f ? Vector3.forward : Vector3.up);
                    }
                    var L = go.AddComponent<Light>();
                    var c = new Color((float)col[0], (float)col[1], (float)col[2]).gamma;
                    L.color = c;
                    L.intensity = w / (4f * Mathf.PI * Mathf.PI);
                    if (typ == "SPOT")
                    {
                        L.type = LightType.Spot;
                        L.spotAngle = (float?)Ls["cone"] ?? 60f;
                        L.innerSpotAngle = L.spotAngle * (1f - ((float?)Ls["blend"] ?? 0.35f));
                    }
                    else L.type = LightType.Point;
                    L.range = Mathf.Clamp(10f * Mathf.Sqrt(L.intensity), 1.5f, 60f);
                    L.shadows = ((int?)Ls["shadows"] ?? 1) != 0 ? LightShadows.Soft : LightShadows.None;
                    lightsBuilt.Add((pos, w, typ));
                    n++;
                }
            }
        }
    }
}
