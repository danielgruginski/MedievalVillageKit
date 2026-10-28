using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;
using UVector3 = MedievalKit.UnityMath.Vector3;

namespace MedievalKit;

/// <summary>
/// A room built from a typed plan (vki_rooms.vki_build_scene, structure only): walls by family and height, rakes,
/// posts (required + rhythm), floors (600 / 300 / Q150 by parity), dais, sills, exits (door, closed leaf, apron,
/// rush mat, link, spawn), stairs, barred gates, passages, door leaves, pits, doorway mats, window light pools and
/// the pieces' lights. The plan is the ASCII grid of the Blender kit (docs/INTERIOR_PLANS.md: one cell = 1.5 m,
/// row 0 is the south / camera side); the room record (JSON) gives the families, zones and their styles, links,
/// stairs and the rest. Presets are the kit's own rooms (KitInteriorRules).
/// Blender room space (x east, y north, z up) maps to this node's local space as (x, z, -y); a turn `rot` about
/// Blender z is a turn of `rot` about Godot y. The fields keep the Unity kit's names (<c>kr.dungeon.seed = 42;
/// kr.RandomDungeon();</c>). Unity: KitRoom.
/// </summary>
[GlobalClass, Tool]
public partial class KitRoom : Node3D
{
    /// <summary>the rules (null: the kit's own, <see cref="KitInteriorRules.Default"/>)</summary>
    [Export] public KitInteriorRules rules;
    /// <summary>a kit room (e.g. VKI_Hovel_F0) whose plan and record Load Preset copies here</summary>
    [Export] public string preset = "";
    [Export(PropertyHint.MultilineText)] public string plan = "";
    /// <summary>the room record as JSON: family, zones (cells, floor, wall styles), links, stairs, sills, pits...</summary>
    [Export(PropertyHint.MultilineText)] public string record = "";
    /// <summary>Auto: the record's prop list, else furniture from the plan's cell codes. Record / Codes: only that one.</summary>
    [Export] public Furniture furniture = Furniture.Auto;
    /// <summary>add the lights of the pieces' light sockets (windows, aprons, hearths, candles)</summary>
    [Export] public bool buildLights = true;
    /// <summary>Random Cave: the cellular automaton's map size (cells of 1.5 m), seed, chasm, pools and dressing</summary>
    [Export] public KitCaveOptions cave = new();
    /// <summary>Random Dungeon: map size, seed, number of rooms, theme (Dungeon / Crypt / Warren / Hideout), cave pockets, loops, debris</summary>
    [Export] public KitDungeonOptions dungeon = new();
    /// <summary>Random Sewer: map size, seed, how far the tunnels reach, loops, chambers, grottoes, cross walls, the ladder up and the way down, encounters</summary>
    [Export] public KitSewerOptions sewer = new();
    /// <summary>Random Interior: kind (Cottage / Townhouse / Tavern / Workshop), seed, size (0: by kind)</summary>
    [Export] public KitInteriorOptions interior = new();
    /// <summary>Random Connector: a short passage between two maps of a chain (from / to edges, length, openings, seed)</summary>
    [Export] public KitConnectorOptions connector = new();

    [ExportToolButton("Load Preset")] public Callable LoadPresetButton => Callable.From(() => { LoadPreset(preset); Generate(); });
    [ExportToolButton("Generate")] public Callable GenerateButton => Callable.From(Generate);
    [ExportToolButton("Random Cave")] public Callable RandomCaveButton => Callable.From(RandomCave);
    [ExportToolButton("Random Dungeon")] public Callable RandomDungeonButton => Callable.From(RandomDungeon);
    [ExportToolButton("Random Sewer")] public Callable RandomSewerButton => Callable.From(RandomSewer);
    [ExportToolButton("Random Interior")] public Callable RandomInteriorButton => Callable.From(RandomInterior);
    [ExportToolButton("Random Connector")] public Callable RandomConnectorButton => Callable.From(RandomConnector);
    [ExportToolButton("Clear")] public Callable ClearButton => Callable.From(Clear);

    /// <summary>how pieces are made (a game may pool them); the room names, places and parents them</summary>
    public static Func<PackedScene, Node3D> Spawn = ps => ps.Instantiate<Node3D>();

    public class Placed
    {
        public string piece, group, what;
        public float x, y, z, rot;      // Blender room space
        public float atX, atY;          // the requested point (props: before mounting / hugging)
        public string mount;
        public Node3D go;
        public KitPiece kp;
        public float[] box;             // the mesh's box, Blender piece space (KitInteriorRules.PieceInfo.box)
        public Dictionary<string, string> style;
    }

    public List<Placed> placed = new();
    public List<string> notes = new();
    public List<(Godot.Vector3 pos, float w, string type)> lightsBuilt = new();
    public KitRoomLayout Layout { get; private set; }

    KitInteriorRules Rules => rules ?? KitInteriorRules.Default;
    JsonObject J => Rules.Json;
    JsonObject R;
    string tag;
    bool night;
    Node3D shell, props, logic, lightRoot;
    readonly Dictionary<string, Node3D> linkObjs = new();

    /// <summary>the node that owns what the build adds (saved with the edited scene in the editor)</summary>
    Node SceneOwner => Owner ?? this;

    public void LoadPreset(string name)
    {
        preset = name;
        plan = Rules.Plan(name) ?? "";
        record = Rules.Room(name) is { } r ? KitJson.Text(r) : "";
    }

    /// <summary>a random cave level (KitCaveGenerator) from the `cave` settings: fills the plan and record, builds</summary>
    public void RandomCave()
    {
        var (p, r) = KitCaveGenerator.Generate(cave);
        preset = "";
        plan = p;
        record = KitJson.Text(r);
        Generate();
    }

    /// <summary>a random house ground floor (KitInteriorGenerator) from the `interior` settings: fills the plan and record, builds</summary>
    public void RandomInterior()
    {
        var (p, r) = KitInteriorGenerator.Generate(interior, CodeFootprint);
        preset = "";
        plan = p;
        record = KitJson.Text(r);
        Generate();
    }

    /// <summary>a furniture code's footprint in cells: its largest piece (what PropsFromCodes picks for a block that fits it);
    /// public for tools that write interiors with <see cref="KitInteriorGenerator"/> themselves</summary>
    public (int, int) CodeFootprint(string code)
    {
        var best = (1, 1);
        foreach (var kv in (JsonObject)J["codes"])
        {
            if (kv.Value.S() != code) continue;
            var piece = Resolve(kv.Key);
            var f = piece != null ? Rules.Info(piece)?.Get("vki_fp_cells") : null;
            if (f == null && piece != null && J["reuse"]?[piece]?["fp"] is JsonArray rf) f = $"{rf[0].I()},{rf[1].I()}";
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
        foreach (var kv in (JsonObject)J["codes"])
        {
            if (!inv.TryGetValue(kv.Value.S(), out var l)) inv[kv.Value.S()] = l = new List<string>();
            l.Add(kv.Key);
        }
        (int, int) Fp(string code)          // the largest piece of a code (what PropsFromCodes picks for a block that fits it)
        {
            var best = (1, 1);
            if (!inv.TryGetValue(code, out var shorts)) return best;
            foreach (var sn in shorts)
            {
                var piece = Resolve(sn);
                var f = piece != null ? Rules.Info(piece)?.Get("vki_fp_cells") : null;
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
        record = KitJson.Text(r);
        Generate();
    }

    /// <summary>a random town sewer (KitSewerGenerator) from the `sewer` settings: fills the plan and record, builds</summary>
    public void RandomSewer()
    {
        var (p, r) = KitSewerGenerator.Generate(sewer);
        preset = "";
        plan = p;
        record = KitJson.Text(r);
        Generate();
    }

    /// <summary>a connector between two maps of a chain (KitConnectorGenerator) from the `connector` settings</summary>
    public void RandomConnector()
    {
        var (p, r) = KitConnectorGenerator.Generate(connector);
        preset = "";
        plan = p;
        record = KitJson.Text(r);
        Generate();
    }

    public void Clear()
    {
        foreach (var c in KitNodes.Children(this).ToList())
        {
            RemoveChild(c);
            c.QueueFree();
        }
        placed.Clear();
        lightsBuilt.Clear();
    }

    public void Generate()
    {
        Clear();
        notes.Clear();
        linkObjs.Clear();
        R = KitJson.ParseObject(record);
        Defaults(R);
        Layout = KitRoomLayout.Build(J, R, plan, FpCells);
        notes.AddRange(Layout.problems);
        string nm = string.IsNullOrEmpty(preset) ? Name.ToString() : preset;
        tag = nm.StartsWith("VKI_") ? nm.Substring(4) : nm;
        night = R["preset"].S() == "Night";
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
                o.kp?.Set("vki_flow", $"[{fl.x.ToString(CultureInfo.InvariantCulture)}, {fl.y.ToString(CultureInfo.InvariantCulture)}]");
        }
        foreach (var rk in Layout.rocks)                // cave maps: the dual-grid rock tiles
        {
            string piece = rk.piece;
            if (Rules.Prefab(piece) == null && (piece.EndsWith("_B") || piece.EndsWith("_C"))) piece = piece.Substring(0, piece.Length - 1) + "A";
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
        foreach (var s in R["sills"] as JsonArray ?? new JsonArray())
            Put(shell, "SM_VKI_Floor_Sill_150", s[0].F(), s[1].F(), s[2].F(), s[3].F(), null, "sill");
        foreach (var s in R["stairs"] as JsonArray ?? new JsonArray())
            Stair(s[0].S(), s[1].F(), s[2].F(), s[3].F(), s[4].S(), s.Len() > 5 ? s[5].S() : "RailR");
        foreach (var pt in R["pits"] as JsonArray ?? new JsonArray())
            Put(shell, KitInteriorRules.Full(pt[0].S()), pt[1].F(), pt[2].F(), 0f, 0f, null, "pit");
        Portals();
        Furnish();                     // before the rhythm posts and doorway mats, which make room for props
        Encounters();
        Markers();
        Rhythm();
        Mats();
        Pools();
        Debris();                       // loose debris by zone theme (R["debris"])
        KitDecks.Apply(this, SceneOwner);   // bridges: walkable decks, the chasm's blocking boxes cut round them
        if (buildLights) Lights();
    }

    /// <summary>a bare plan still builds: timber walls, a board floor, a front exit back to where one came from</summary>
    static void Defaults(JsonObject r)
    {
        if (r["family"] is not JsonObject) r["family"] = new JsonObject { ["perimeter"] = "Timber", ["partition"] = "Board" };
        if (r["zones"] is not JsonObject z || z.Count == 0) r["zones"] = new JsonObject { ["room"] = new JsonObject { ["cells"] = "rest", ["floor"] = "Boards_NS" } };
        if (r["links"] is not JsonArray) r["links"] = new JsonArray { KitJson.A("front", "exit", "@return") };
        if (r["preset"] == null) r["preset"] = "Day";
    }

    Node3D Group(string n)
    {
        var t = new Node3D { Name = n };
        AddChild(t);
        t.Owner = SceneOwner;
        return t;
    }

    string FpCells(string piece) => Rules.Info(piece)?.Get("vki_fp_cells");

    static Vector2 Frame(float x, float y, float rot, float lx, float ly)
    {
        double r = rot * Math.PI / 180.0, c = Math.Cos(r), s = Math.Sin(r);
        return new Vector2((float)(x + c * lx - s * ly), (float)(y + s * lx + c * ly));
    }

    static float R4(float v) => (float)Math.Round(v, 4);
    static float Mod360(float a) => ((a % 360f) + 360f) % 360f;
    static string Inv(float v) => v.ToString(CultureInfo.InvariantCulture);

    /// <summary>Blender room space -> this node's local space</summary>
    static Godot.Vector3 Local(float x, float y, float z) => new(x, z, -y);

    static JsonNode PropJ(KitPiece kp, string key)
    {
        string v = kp?.Get(key);
        if (v == null) return null;
        if (v.Length > 0 && (v[0] == '[' || v[0] == '{'))
            try { return KitJson.Parse(v); } catch (Exception) { return JsonValue.Create(v); }
        return JsonValue.Create(v);
    }

    // ------------------------------------------------------------------ placement (vki_rooms_put)
    Placed Put(Node3D parent, string piece, float x, float y, float rot, float z, Dictionary<string, string> style, string what)
    {
        var info = Rules.Info(piece);
        if (info == null) { notes.Add($"no prefab {piece} ({what} at {x:0.##}, {y:0.##})"); return null; }
        var go = Spawn(info.scene);
        string shortName = piece.StartsWith("SM_VKI_") ? piece.Substring(7) : piece.StartsWith("SM_VK_") ? piece.Substring(6) : piece;
        go.Name = $"{tag}_{shortName}";
        parent.AddChild(go, true);          // a readable unique name: links and leaves refer to their door by it
        go.Owner = SceneOwner;
        go.Position = Local(x, y, z);
        go.Rotation = new Godot.Vector3(0f, rot * Mathf.Deg2Rad, 0f);
        go.Scale = Godot.Vector3.One;
        var kp = go as KitPiece;
        var st = new Dictionary<string, string>();
        bool reuse = piece.StartsWith("SM_VK_") && !piece.StartsWith("SM_VKI_");
        if (reuse)
            foreach (var kv in (JsonObject)J["reuse_style"]) st[kv.Key] = kv.Value.S();
        if (style != null) foreach (var kv in style) st[kv.Key] = kv.Value;
        if (night)
        {
            if (reuse) { if (style == null || !style.ContainsKey("window")) st["window"] = "Window_Night"; }
            else if (Uses(kp, J["slots"]["window"].I(), J["slots"]["stained"].I()))
                foreach (var kv in (JsonObject)J["night_style"])
                    if (style == null || !style.ContainsKey(kv.Key)) st[kv.Key] = kv.Value.S();
        }
        if (st.Count > 0) ApplyStyle(go, kp, st);
        if (reuse && piece.StartsWith("SM_VK_Prop_")) KitSolid.Box(go, owner: SceneOwner);      // an exterior prop has no vki_collider: walked through
        var p = new Placed { piece = piece, group = parent.Name, what = what, x = x, y = y, z = z, rot = rot, atX = x, atY = y, go = go, kp = kp, box = info.box, style = st };
        placed.Add(p);
        return p;
    }

    static bool Uses(KitPiece kp, params int[] slots) => kp != null && kp.BlenderSlots.Any(slots.Contains);

    /// <summary>vki_variant_apply: each style key swaps the material of its Blender slot (wall_b defaults to wall_a).</summary>
    void ApplyStyle(Node3D go, KitPiece kp, Dictionary<string, string> style)
    {
        var mr = kp?.MeshInstance;
        if (kp == null || mr?.Mesh == null) return;
        var st = new Dictionary<string, string>(style);
        if (st.ContainsKey("wall_a") && !st.ContainsKey("wall_b")) st["wall_b"] = st["wall_a"];
        bool changed = false;
        int n = mr.Mesh.GetSurfaceCount();
        foreach (var kv in st)
        {
            var slot = J["slots"][kv.Key];
            if (slot == null) continue;
            int s = slot.I();
            if (!kp.BlenderSlots.Contains(s)) continue;
            string mn = Rules.StyleMatName(kv.Key, kv.Value);
            var m = Rules.Mat(mn);
            if (m == null) { notes.Add($"{go.Name}: no material for {kv.Key}={kv.Value} ({mn ?? "not in the style table"})"); continue; }
            for (int i = 0; i < n && i < kp.BlenderSlots.Length; i++)
                if (kp.BlenderSlots[i] == s && mr.GetActiveMaterial(i) != m) { mr.SetSurfaceOverrideMaterial(i, m); changed = true; }
        }
        if (changed && SceneOwner != go) SceneOwner.SetEditableInstance(go, true);    // saved with the scene
    }

    // ------------------------------------------------------------------ vki_rooms_wall_style
    Dictionary<string, string> WallStyle(KitRoomLayout.Piece pc)
    {
        var zones = (JsonObject)R["zones"];
        string famDef = J["families"][pc.fam]["wall_a"].S();
        string Zs(List<(int, int)> cells, string key)
        {
            foreach (var c in cells)
                if (Layout.zmap.TryGetValue(c, out var zn) && zn != null && zones[zn]?[key] != null && zones[zn][key].S() != "")
                    return zones[zn][key].S();
            return null;
        }
        var st = new Dictionary<string, string>();
        if (pc.role == "part")
        {
            if (R["partition_wall"].S() == "zone")
            {
                st["wall_a"] = Zs(pc.faceA, "wall") ?? famDef;
                st["wall_b"] = Zs(pc.faceB, "wall") ?? famDef;
            }
        }
        else
        {
            st["wall_a"] = Zs(pc.faceA, "wall") ?? famDef;
            st["wall_b"] = R["exterior"].S() ?? famDef;
        }
        if (st.Count > 0 && st["wall_a"] == famDef && st["wall_b"] == famDef) st.Clear();
        string cap = Zs(pc.faceA, "cap");
        if (cap != null) st["cap"] = cap;
        if (pc.kind == "Special" && R["special_style"] is JsonObject ss)
            foreach (var kv in ss) st[kv.Key] = kv.Value.S();
        if (pc.kind == "Window" && pc.height == "Full" && R["window_style"] is JsonObject ws)
            foreach (var kv in ws) st[kv.Key] = kv.Value.S();
        if ((pc.kind == "Lancet" || pc.kind == "LancetTall") && R["lancet_style"] is JsonObject ls)   // e.g. leaded glass
            foreach (var kv in ls) st[kv.Key] = kv.Value.S();
        return st;
    }

    static Dictionary<string, string> StyleOf(JsonNode t) =>
        t is JsonObject o ? o.ToDictionary(p => p.Key, p => p.Value.S()) : null;

    // ------------------------------------------------------------------ links and spawns
    void Link(Placed o, string kind, string id, string target, string prompt)
    {
        var kp = o.kp;
        kp?.Set("vki_link", kind); kp?.Set("vki_link_id", id); kp?.Set("vki_target", target);
        kp?.Set("vki_prompt", prompt); kp?.Set("vki_facing_min", "60");
        var l = KitNodes.Children(o.go).OfType<KitLink>().FirstOrDefault();
        if (l == null)
        {
            l = new KitLink { Name = "KitLink", Monitorable = false };
            o.go.AddChild(l);
            l.Owner = SceneOwner;
        }
        l.LinkId = id; l.Kind = kind; l.Target = target ?? ""; l.Prompt = prompt; l.FacingMin = 60f;
        if (LinkEntry(id) is JsonArray le && le.Count > 3 && le[3].IsStr()) l.Arrive = le[3].S();   // [id, kind, target, arrive]
        if (PropJ(kp, "vki_trigger") is JsonArray b && b.Count >= 6 && !KitNodes.Children(l).OfType<CollisionShape3D>().Any())
        {
            var cs = new CollisionShape3D
            {
                Name = "Trigger",
                Shape = new BoxShape3D { Size = new Godot.Vector3(Mathf.Abs(b[3].F()), Mathf.Abs(b[5].F()), Mathf.Abs(b[4].F())) },
                Position = new Godot.Vector3(b[0].F(), b[2].F(), -b[1].F()),
            };
            l.AddChild(cs);
            cs.Owner = SceneOwner;
        }
        linkObjs[id] = o.go;
    }

    /// <summary>R["portals"] (generated maps chained into a world): a KitPortalMarker on the middle of each opening
    /// on the map's edge, facing out, and a spawn a cell and a half in, facing in</summary>
    void Portals()
    {
        foreach (var pt in KitPortal.Of(R))
        {
            if (pt.at < 0) { notes.Add($"portal {pt.id}: no opening (at -1)"); continue; }
            var sp = pt.SeamPoint(Layout.P.nc, Layout.P.nr, Layout.IG);
            var m = new KitPortalMarker
            {
                Name = "PRT_" + pt.id, PortalId = pt.id, Side = pt.Side.ToString(), At = pt.at, Width = pt.width,
                Target = pt.target ?? "", Seam = pt.seam,
            };
            logic.AddChild(m);
            m.Owner = SceneOwner;
            m.Transform = new Transform3D(KitSpawn.FromBearing(KitPortal.Inward(pt.Side) + 180f), Local(sp.x, sp.y, 0f));
            var (dx, dy) = KitPortal.Outward(pt.Side);
            float inset = 1.5f * Layout.IG;
            SpawnPoint(pt.id, R4(sp.x - dx * inset), R4(sp.y - dy * inset), KitPortal.Inward(pt.Side), null);
        }
    }

    void SpawnPoint(string id, float x, float y, float facing, Placed host)
    {
        var sp = new KitSpawn { Name = "SPN_" + id, SpawnId = id, FacingDeg = facing, Kind = KitMarker.MarkerKind.Spawn };
        sp.Props = new Godot.Collections.Dictionary<string, string>
        {
            ["vki_spawn_id"] = id, ["vki_facing_deg"] = Inv(facing), ["vki_link_obj"] = host?.go.Name.ToString() ?? "",
        };
        logic.AddChild(sp, true);
        sp.Owner = SceneOwner;
        sp.Transform = new Transform3D(KitSpawn.FromBearing(facing), Local(x, y, 0f));
    }

    JsonNode LinkEntry(string id) => (R["links"] as JsonArray ?? new JsonArray()).FirstOrDefault(l => l[0].S() == id);

    /// <summary>vki_rooms_exit: door + closed leaf (two for a wide door) + apron + rush mat inside + link + spawn</summary>
    void Exit(KitRoomLayout.Piece pc, Placed door)
    {
        float T = J["t"][pc.cls].F();
        bool wide = pc.kind == "ExitWide";
        float Lp = J["ig"].F() * pc.n;
        var socks = PropJ(door.kp, "vki_leaf_socket") as JsonArray;
        var leaves = new List<(string piece, float sx, float sy)>();
        if (wide)
        {
            if (!(socks != null && socks.Count > 0 && socks[0] is JsonArray))
                socks = KitJson.A(KitJson.A(0.60, -T / 2 + 0.05, 0.0), KitJson.A(2.40, -T / 2 + 0.05, 0.0));
            var lv = PropJ(door.kp, "vki_leaf") as JsonArray;
            var names = lv != null && lv.Count == 2 ? lv.Select(x => x.S()).ToArray()
                : pc.fam == "Ashlar" ? new[] { "SM_VKI_Leaf_Wide160_Cut_L", "SM_VKI_Leaf_Wide160_Cut_R" }
                : new[] { "SM_VKI_Leaf_Wide_Cut_L", "SM_VKI_Leaf_Wide_Cut_R" };
            for (int i = 0; i < 2; i++) leaves.Add((names[i], socks[i][0].F(), socks[i][1].F()));
        }
        else
        {
            float sx = 0.33f, sy = -T / 2 + 0.05f;
            if (socks != null && socks.Count > 0 && socks[0] is not JsonArray) { sx = socks[0].F(); sy = socks[1].F(); }
            string lv = PropJ(door.kp, "vki_leaf") is JsonValue v && v.IsStr() ? v.S() : null;
            lv = lv != null && lv.EndsWith("_Cut") && Rules.Prefab(lv) != null ? lv : null;
            leaves.Add((lv ?? "SM_VKI_Leaf_Plank_Cut", sx, sy));
        }
        foreach (var (lp, sx, sy) in leaves)
        {
            var w = Frame(pc.x, pc.y, pc.rot, sx, sy);
            var lf = Put(shell, lp, R4(w.x), R4(w.y), pc.rot, 0f, null, "leaf");
            lf?.kp?.Set("vki_leaf_state", "closed");
            lf?.kp?.Set("vki_leaf_deg", "0");
            lf?.kp?.Set("vki_leaf_door", door.go.Name);
        }
        string apron; float off;
        if (wide && Rules.Prefab("SM_VKI_Apron_Wide_300x150") != null) { apron = "SM_VKI_Apron_Wide_300x150"; off = 0f; }
        else { apron = "SM_VKI_Apron_300x150"; off = wide ? 0.75f : 0f; }
        var a = Frame(pc.x, pc.y, pc.rot, off, 0f);
        Put(shell, apron, R4(a.x), R4(a.y), pc.rot, 0f, StyleOf(R["apron_style"]), "apron");
        var m = Frame(pc.x, pc.y, pc.rot, Lp / 2, -0.75f);
        Put(props, "SM_VKI_RushMat", R4(m.x), R4(m.y), 0f, 0f, null, "exitmat");
        var lk = (R["links"] as JsonArray ?? new JsonArray()).FirstOrDefault(l => l[1].S() == "exit");
        string id = lk != null ? lk[0].S() : "front", target = lk != null ? lk[2].S() : "@return";
        Link(door, "exit", id, target, "Leave");
        var sl = PropJ(door.kp, "vki_spawn_local") as JsonArray;
        var s = Frame(pc.x, pc.y, pc.rot, sl != null ? sl[0].F() : Lp / 2, sl != null ? sl[1].F() : -1.60f);
        SpawnPoint(id, R4(s.x), R4(s.y), Mod360(180f - pc.rot), door);
    }

    /// <summary>vki_rooms_stair: the stair piece carries the link; spawn at its vki_spawn_local</summary>
    void Stair(string kind, float x, float y, float rot, string lid, string var)
    {
        var o = Put(shell, KitRoomLayout.StairPiece(kind, var), x, y, rot, 0f, null, "stair");
        if (o == null) return;
        var lk = LinkEntry(lid);
        Link(o, kind == "Up" ? "stair_up" : "stair_down", lid, lk != null ? lk[2].S() : "",
             o.kp?.Get("vki_prompt_text") ?? (kind == "Up" ? "Go upstairs" : "Go downstairs"));      // a hatch: "Climb up" / "Climb down"
        var sl = PropJ(o.kp, "vki_spawn_local") as JsonArray;
        float lx = sl != null ? sl[0].F() : (kind == "Up" ? 0.75f : 2.25f), ly = sl != null ? sl[1].F() : (kind == "Up" ? -0.75f : 3.75f);
        float fac = o.kp != null && o.kp.Has("vki_spawn_facing") ? o.kp.GetFloat("vki_spawn_facing") : (kind == "Up" ? 180f : 90f);
        var s = Frame(x, y, rot, lx, ly);
        SpawnPoint(lid, R4(s.x), R4(s.y), Mod360(fac - rot), o);
    }

    /// <summary>vki_rooms_passage: the wall piece carries the link R["passages"][key]</summary>
    void Passage(KitRoomLayout.Piece pc, Placed o)
    {
        string lid = R["passages"]?[pc.Key].S();
        var lk = lid != null ? LinkEntry(lid) : null;
        if (lk == null) { notes.Add($"passage at {pc.ori} ({pc.k},{pc.line}) has no R['passages'] / links entry"); return; }
        Link(o, "passage", lid, lk[2].S(), o.kp?.Get("vki_prompt_text") ?? "Go through");
        var sl = PropJ(o.kp, "vki_spawn_local") as JsonArray;
        var s = Frame(pc.x, pc.y, pc.rot, sl != null ? sl[0].F() : 0.75f, sl != null ? sl[1].F() : -1.60f);
        SpawnPoint(lid, R4(s.x), R4(s.y), Mod360(180f - pc.rot), o);
    }

    /// <summary>R["encounters"] (generated dungeons): a KitEncounter per room, its spawn points as children</summary>
    void Encounters()
    {
        if (R["encounters"] is not JsonArray es) return;
        foreach (var e in es)
        {
            var box = e["box"];
            float x0 = box[0].F(), y0 = box[1].F(), x1 = box[2].F(), y1 = box[3].F();
            var en = new KitEncounter
            {
                Name = "ENC_" + e["id"].S(), EncounterId = e["id"].S() ?? "", RoomType = e["room"].S() ?? "",
                Creature = e["creature"].S() ?? "", Budget = e["budget"].Iq() ?? 1, Depth = e["depth"].Iq() ?? 0,
                Boss = e["boss"].Bq() ?? false, Size = new Godot.Vector3(x1 - x0, 3f, y1 - y0),
            };
            logic.AddChild(en, true);
            en.Owner = SceneOwner;
            en.Position = Local((x0 + x1) / 2f, (y0 + y1) / 2f, 0f);
            int k = 0;
            foreach (var pt in e["points"] as JsonArray ?? new JsonArray())
            {
                var sp = new Node3D { Name = $"Spawn_{k++}" };
                en.AddChild(sp);
                sp.Owner = SceneOwner;
                sp.Position = Local(pt[0].F(), pt[1].F(), 0f) - en.Position;
            }
        }
    }

    /// <summary>R["markers"] ([{id, role, at: [x, y], facing, note}]: loot to search, an npc's place...): a KitMarker each
    /// (vki_role, vki_marker_id, vki_facing_deg, vki_note) for the game</summary>
    void Markers()
    {
        foreach (var m in R["markers"] as JsonArray ?? new JsonArray())
        {
            var at = m["at"] as JsonArray;
            if (at == null || at.Count < 2) continue;
            float facing = m["facing"].Fq() ?? 0f;
            var mk = new KitMarker { Name = $"MRK_{m["role"].S()}_{m["id"].S()}", Kind = KitMarker.MarkerKind.Other };
            mk.Props = new Godot.Collections.Dictionary<string, string>
            {
                ["vki_role"] = m["role"].S() ?? "", ["vki_marker_id"] = m["id"].S() ?? "", ["vki_facing_deg"] = Inv(facing),
            };
            if (m["note"] != null) mk.Props["vki_note"] = m["note"].S();
            logic.AddChild(mk, true);
            mk.Owner = SceneOwner;
            mk.Transform = new Transform3D(KitSpawn.FromBearing(facing), Local(at[0].F(), at[1].F(), 0f));
        }
    }

    /// <summary>vki_cave_tunnel: a tunnel tile carries its scene link, as a passage</summary>
    void Tunnel(KitRoomLayout.Rock rk, Placed o)
    {
        var lk = LinkEntry(rk.tunnel);
        if (lk == null) { notes.Add($"tunnel {rk.tunnel} at node ({rk.node.Item1},{rk.node.Item2}) has no links entry"); return; }
        Link(o, "passage", rk.tunnel, lk[2].S(), o.kp?.Get("vki_prompt_text") ?? "Go through");
        var sl = PropJ(o.kp, "vki_spawn_local") as JsonArray;
        var sp = Frame(rk.x, rk.y, rk.rot, sl != null ? sl[0].F() : 0f, sl != null ? sl[1].F() : -1.60f);
        SpawnPoint(rk.tunnel, R4(sp.x), R4(sp.y), Mod360(180f - rk.rot), o);
    }

    /// <summary>vki_rooms_door_leaf: R["door_leaves"][key] = {piece, deg, z, socket, state}</summary>
    void DoorLeaf(KitRoomLayout.Piece pc, Placed door)
    {
        var spec = R["door_leaves"][pc.Key];
        string piece = KitInteriorRules.Full(spec["piece"].S());
        JsonNode s = spec["socket"] is JsonArray sj && sj.Count > 0 ? sj : PropJ(door.kp, "vki_leaf_socket");
        if (!(s is JsonArray sa && sa.Count > 0)) s = KitJson.A(0.33, -0.2, 0.0);
        if (s[0] is JsonArray) s = s[0];
        float deg = spec["deg"] != null ? spec["deg"].F() : 0f, z = spec["z"] != null ? spec["z"].F() : 0f;
        var w = Frame(pc.x, pc.y, pc.rot, s[0].F(), s[1].F());
        var lf = Put(shell, piece, R4(w.x), R4(w.y), pc.rot - deg, z, null, "leaf");
        lf?.kp?.Set("vki_leaf_state", spec["state"].S() ?? (deg != 0f || z != 0f ? "open" : "closed"));
        lf?.kp?.Set("vki_leaf_deg", Inv(deg));
        lf?.kp?.Set("vki_leaf_door", door.go.Name);
    }

    /// <summary>vki_rooms_gate: the barred door's own leaf, opened R["gates"][key] degrees (default gate_deg)</summary>
    void Gate(KitRoomLayout.Piece pc, Placed door)
    {
        string lv = door.kp?.Get("vki_leaf");
        if (lv == null || lv.StartsWith("[")) return;
        var s = PropJ(door.kp, "vki_leaf_socket") as JsonArray ?? KitJson.A(0.33, -0.022, 0.0);
        float deg = R["gates"]?[pc.Key] != null ? R["gates"][pc.Key].F() : J["gate_deg"].F();
        var w = Frame(pc.x, pc.y, pc.rot, s[0].F() + (deg < 0 ? 0.045f : 0f), s[1].F());
        var lf = Put(shell, lv, R4(w.x), R4(w.y), pc.rot - deg, 0f, null, "gate");
        lf?.kp?.Set("vki_leaf_state", deg != 0f ? "open" : "closed");
        lf?.kp?.Set("vki_leaf_deg", Inv(deg));
        lf?.kp?.Set("vki_leaf_door", door.go.Name);
    }

    // ------------------------------------------------------------------ boxes (vki_rooms_obj_box / wall_env)
    public struct Box
    {
        public UVector3 a, b;
        public bool Hits(Box o) => a.x < o.b.x && o.a.x < b.x && a.y < o.b.y && o.a.y < b.y && a.z < o.b.z && o.a.z < b.z;
    }

    /// <summary>a piece's mesh box in Blender piece space; Unity reads the root's mesh, an empty box without one</summary>
    static float[] MeshBoxOf(Placed p) => p.box ?? new float[6];

    /// <summary>world (room) AABB of a placed piece's mesh, in Blender room space (a, b: x, y, z)</summary>
    public static Box ObjBox(Placed p)
    {
        var mb = MeshBoxOf(p);
        float[] xs = { mb[0], mb[3] }, ys = { mb[1], mb[4] };
        var lo = new UVector3(float.MaxValue, float.MaxValue, p.z + mb[2]);
        var hi = new UVector3(float.MinValue, float.MinValue, p.z + mb[5]);
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
        float chw = J["cap_hw"]?[cls] != null ? J["cap_hw"][cls].F() : (cls == "O" ? 0.28f : 0.18f);
        string fam = p.kp.Get("vki_family");
        float H = p.kp.Get("vki_height", "Full") == "Cut" ? J["cut_h"].F()
            : fam != null && J["families"][fam] != null ? J["families"][fam]["H"].F() : 3f;
        var lo = new UVector3(float.MaxValue, float.MaxValue, -0.30f);
        var hi = new UVector3(float.MinValue, float.MinValue, H);
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
    static bool Truthy(string v) => KitPiece.Truthy(v);

    /// <summary>vki_rooms_rhythm: optional rhythm Mid posts, skipped where a prop, overlay or stair touches the post square</summary>
    void Rhythm()
    {
        var obst = placed.Where(p => ((Cls(p) == "prop" || Cls(p) == "overlay") && !Truthy(p.kp?.Get("vki_edge"))) ||
                                     p.kp?.Get("vki_link") == "stair_up" || p.kp?.Get("vki_link") == "stair_down")
                         .Select(p => (p, box: ObjBox(p))).ToList();
        foreach (var p in Layout.posts)
        {
            if (p.req) continue;
            string cls = J["families"][p.fam]["cls"].S();
            float hx = J["mid_hw"][cls][0].F(), hy = J["mid_hw"][cls][1].F();
            if (Mathf.Approximately(p.rot, 90f)) (hx, hy) = (hy, hx);
            float top = (p.height == "Full" ? J["families"][p.fam]["H"].F() : J["cut_h"].F()) + J["post_top"].F();
            var box = new Box
            {
                a = new UVector3(p.x - hx - 0.005f, p.y - hy - 0.005f, J["post_z0"].F()),
                b = new UVector3(p.x + hx + 0.005f, p.y + hy + 0.005f, top)
            };
            var hit = obst.FirstOrDefault(o => box.Hits(o.box));
            if (hit.p != null) { notes.Add($"rhythm post at node ({p.node.Item1},{p.node.Item2}) skipped: {hit.p.go.Name}"); continue; }
            Put(shell, p.piece, p.x, p.y, p.rot, 0f, null, "rhythm");
        }
    }

    /// <summary>vki_rooms_mats: a RushMat each side of every N-S Cut doorway, shifted 0.75 along it when blocked</summary>
    void Mats()
    {
        if (R["rush_mats"] != null && R["rush_mats"].IsBool() && !R["rush_mats"].B()) return;
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
                    var rect = new Box { a = new UVector3(cx - 0.40f, cy - 0.60f, 0f), b = new UVector3(cx + 0.40f, cy + 0.60f, 0.03f) };
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

    /// <summary>vki_rooms_pools: FX_WindowPool under every Full window / lancet in Day rooms, but none whose patch
    /// (about 1.1 x 1.4 m round its centre) reaches a stair's or a hatch's cells: it lies at floor height and glowed
    /// over the shaft (2026-10-12, the hamlet chapel's stair down under its east lancet)</summary>
    void Pools()
    {
        if (night || (R["pools"] != null && R["pools"].IsBool() && !R["pools"].B()) ||
            Rules.Prefab("SM_VKI_FX_WindowPool") == null) return;
        var dais = (R["dais"] as JsonArray ?? new JsonArray()).Select(d => (d[0].F(), d[1].F())).ToList();
        foreach (var pc in Layout.pieces)
        {
            if ((pc.kind != "Window" && pc.kind != "Lancet" && pc.kind != "LancetTall") || pc.height != "Full") continue;
            var c = Frame(pc.x, pc.y, pc.rot, 0.75f, -1.15f);
            if (OverOpening(c, 0.6f))
            {
                notes.Add($"window pool at {c.x:0.##}, {c.y:0.##} left out: it would lie over a stair or a hatch");
                continue;
            }
            float z = dais.Any(d => d.Item1 <= c.x && c.x <= d.Item1 + 3f && d.Item2 <= c.y && c.y <= d.Item2 + 3f) ? 0.20f : 0f;
            Put(props, "SM_VKI_FX_WindowPool", pc.x, pc.y, pc.rot, z, null, "pool");
        }
    }

    /// <summary>a spot (room metres) within `r` of a stair's or a hatch's cell: no floor of its own there</summary>
    bool OverOpening(Vector2 c, float r)
    {
        float ig = Layout.IG;
        for (int i = 0; i < 9; i++)
        {
            var cell = (Mathf.FloorToInt((c.x + (i % 3 - 1) * r) / ig), Mathf.FloorToInt((c.y + (i / 3 - 1) * r) / ig));
            if ((Layout.stairCells != null && Layout.stairCells.ContainsKey(cell)) || (Layout.pitCells != null && Layout.pitCells.ContainsKey(cell)))
                return true;
        }
        return false;
    }

    /// <summary>linear -> sRGB, the light colours' space (as KitBuilder's lights)</summary>
    static float Srgb(double c)
    {
        c = Math.Clamp(c, 0.0, 1.0);
        return (float)(c <= 0.0031308 ? 12.92 * c : 1.055 * Math.Pow(c, 1.0 / 2.4) - 0.055);
    }

    /// <summary>vki_rooms_lights: a light per vki_lights socket of the placed pieces (Day / Night power), the energy and
    /// range as KitBuilder makes a level's Blender lights</summary>
    void Lights()
    {
        int n = 0;
        foreach (var p in placed.Where(q => q.group == "Shell").Concat(placed.Where(q => q.group == "Props")))
        {
            if (PropJ(p.kp, "vki_lights") is not JsonArray ls) continue;
            foreach (var Ls in ls)
            {
                string typ = Ls["type"].S() ?? "POINT";
                float wd = Ls["w_day"].Fq() ?? Ls["w"].Fq() ?? 100f, wn = Ls["w_night"].Fq() ?? Ls["w"].Fq() ?? 100f;
                var cd = Ls["color_day"] ?? Ls["color"] ?? KitJson.A(1, 1, 1);
                var cn = Ls["color_night"] ?? Ls["color"] ?? KitJson.A(1, 1, 1);
                float w = night ? wn : wd;
                var col = night ? cn : cd;
                var pl = Ls["pos"];
                var pw = Frame(p.x, p.y, p.rot, pl[0].F(), pl[1].F());
                var pos = Local(pw.x, pw.y, p.z + pl[2].F());
                float energy = w / (4f * Mathf.PI * Mathf.PI);
                float range = Mathf.Clamp(10f * Mathf.Sqrt(energy), 1.5f, 60f);
                Light3D L;
                if (typ == "SPOT")
                {
                    // Blender / Unity give the cone's full angle and the share of it blended; Godot the half angle and a
                    // falloff exponent (KitBuilder's: half-way where Blender's is)
                    double blend = Math.Clamp(Ls["blend"].Dq() ?? 0.35, 0.01, 1.0);
                    L = new SpotLight3D
                    {
                        SpotRange = range, SpotAttenuation = 2f, SpotAngle = (Ls["cone"].Fq() ?? 60f) / 2f,
                        SpotAngleAttenuation = (float)(Math.Log(1.0 - blend / 2.0) / Math.Log(0.5)),
                    };
                }
                else L = new OmniLight3D { OmniRange = range, OmniAttenuation = 2f };
                L.Name = $"LIT_{tag}_{n:00}_{Ls["role"].S() ?? typ.ToLowerInvariant()}";
                L.LightEnergy = energy;
                L.LightColor = new Color(Srgb(col[0].D()), Srgb(col[1].D()), Srgb(col[2].D()));
                L.ShadowEnabled = (Ls["shadows"].Iq() ?? 1) != 0;
                lightRoot.AddChild(L, true);
                L.Owner = SceneOwner;
                L.Position = pos;
                if (Ls["aim"] is JsonArray am)
                {
                    var aw = Frame(p.x, p.y, p.rot, am[0].F(), am[1].F());
                    var dir = Local(aw.x, aw.y, p.z + am[2].F()) - pos;
                    if (dir.LengthSquared() > 1e-8f)
                        L.Basis = Basis.LookingAt(dir.Normalized(), Math.Abs(dir.Normalized().Y) > 0.999f ? Godot.Vector3.Forward : Godot.Vector3.Up);
                }
                lightsBuilt.Add((pos, w, typ));
                n++;
            }
        }
    }
}
