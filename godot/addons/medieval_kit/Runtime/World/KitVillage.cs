using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;
using Rect = MedievalKit.UnityMath.Rect;

namespace MedievalKit;

/// <summary>
/// An outdoor map (a village, a hamlet, a farmstead) built from a layout: the outdoor counterpart of
/// <see cref="KitRoom"/>. The layout (JSON, plan metres: x east, y north, origin at the map's south-west corner)
/// gives the clearing in the forest, roads as curves through points, paved or trodden areas, buildings (the kit's
/// structures or generated houses) turned to face a point, props, fences along polylines, single trees, the forest
/// and its undergrowth, dressing, spawns, markers for the game (NPCs, a respawn point) and exits at road ends.
/// Build makes: the ground (a mesh with the kit's terrain material, gentle relief rising into the forest, a level
/// pad under each building, roads and paving painted into its control map, so nothing follows a tile grid), the
/// pieces placed on it, colliders (buildings, props, fences, tree trunks, an invisible wall round the clearing
/// broken only by the roads, the map's border) and the links. Same layout and seed, same map (in this engine: the
/// Unity kit's map of a layout follows the same rules, not the same numbers).
/// Plan space -> this node's local space: (x, y, h) -> (x, h, -y); a turn of `deg` about plan z -> `deg` about y.
/// The fields keep the Unity kit's names. Unity: KitVillage.
/// </summary>
[GlobalClass, Tool]
public partial class KitVillage : Node3D
{
    /// <summary>the layout as JSON (see the Unity package's LEVEL_BUILDING.md, outdoor maps; the addon's MANUAL)</summary>
    [Export(PropertyHint.MultilineText)] public string layout = "";
    /// <summary>the kit's terrain material (null: res://kit/materials/M_VK_Terrain.tres); Build makes a copy carrying
    /// this map's control map</summary>
    [Export] public Material groundMaterial;
    /// <summary>the sea's water (null: the addon's Materials/KitSea.tres; none there: the water quads keep their own)</summary>
    [Export] public Material seaMaterial;
    /// <summary>a moored hull's waterline footprint, cut out of the sea (null: the addon's Materials/KitWaterMask.tres)</summary>
    [Export] public Material waterMaskMaterial;
    /// <summary>for generated houses (null: the kit's, <see cref="KitHouseRules.Default"/>)</summary>
    [Export] public KitHouseRules houseRules;

    [ExportToolButton("Build")] public Callable BuildButton => Callable.From(Build);
    [ExportToolButton("Clear")] public Callable ClearButton => Callable.From(Clear);

    /// <summary>how pieces are made (a game may pool them); the village names, places and parents them</summary>
    public static Func<PackedScene, Node3D> Spawn = ps => ps.Instantiate<Node3D>();

    public List<string> notes = new();
    public ArrayMesh GroundMesh { get; private set; }
    /// <summary>the control map (R dirt, G cobble, B sand), plan row j at image row (height - 1 - j): the terrain shader
    /// reads it from its north end</summary>
    public Image ControlImage { get; private set; }
    public ImageTexture ControlMap { get; private set; }
    public ShaderMaterial GroundMaterialInstance { get; private set; }

    /// <summary>a raised bed's frame across (m; the Blender kit's crop beds, vk_helpers bed_frame): the bake keeps the
    /// navmesh off it (Unity carves it in play)</summary>
    public const float BedSize = 2.92f;

    const float Res = 1f;            // ground mesh spacing (m)
    const int CtlPerM = 4;           // control map pixels per metre

    JsonObject L;
    float W, H, M;                   // the map (walkable, walled) and the margin of forest drawn round it
    System.Random rnd;
    Node3D groundT, buildT, propT, natureT, logicT, wallT;
    readonly List<(Vector2[] poly, float h)> pads = new();
    readonly List<(Vector2[] poly, string id)> occupied = new();
    readonly List<(string id, Vector2[] pts, float width, string surface)> roads = new();
    readonly List<(Vector2 c, Vector2 r, float lumps, string surface, int seed)> areas = new();
    readonly Dictionary<string, (Node3D t, Vector2 at, float rot)> builtById = new();
    readonly List<(Vector2 c, Vector2 r, float lumps, int seed)> clears = new();
    readonly List<(Vector2 c, Vector2 r, float rot, float h, float top)> mounds = new();

    Node SceneOwner => Owner ?? this;

    // ------------------------------------------------------------------ plan space
    public static Godot.Vector3 Local(float x, float y, float h) => new(x, h, -y);
    public static Basis Turn(float deg) => new(Godot.Vector3.Up, deg * Mathf.Deg2Rad);
    static Vector2 V(JsonNode t) => new(t[0].F(), t[1].F());
    static Vector2 Rot(Vector2 v, float deg) { float r = deg * Mathf.Deg2Rad, c = Mathf.Cos(r), s = Mathf.Sin(r); return new Vector2(c * v.x - s * v.y, s * v.x + c * v.y); }
    static float Ang(Vector2 v) => Mathf.Atan2(v.y, v.x) * Mathf.Rad2Deg;
    /// <summary>a point of this node's local space in plan space</summary>
    static Vector2 Plan(Godot.Vector3 p) => new(p.X, -p.Z);

    public void Clear()
    {
        foreach (var c in KitNodes.Children(this).ToList())
        {
            RemoveChild(c);
            c.QueueFree();
        }
    }

    public void Build()
    {
        Clear();
        notes.Clear(); pads.Clear(); occupied.Clear(); roads.Clear(); areas.Clear(); builtById.Clear(); seaHulls.Clear();
        L = KitJson.ParseObject(layout);
        var size = L["size"] as JsonArray;
        W = size != null ? size[0].F() : 100f; H = size != null ? size[1].F() : 100f;
        M = L["margin"].Fq() ?? 24f;
        rnd = new System.Random(L["seed"].Iq() ?? 1);
        rz = null;                       // the forest dressing's own stream (KitVillage.ForestDress.cs)
        groundT = Group("Ground"); buildT = Group("Buildings"); propT = Group("Props"); natureT = Group("Nature");
        logicT = Group("Logic"); wallT = Group("Walls");
        clears.Clear();
        clears.AddRange(Clearings(L, W, H));
        foreach (var r in L["roads"] as JsonArray ?? new JsonArray())
            roads.Add((r["id"].S(), Spline(r["points"].AsArray().Select(V).ToList()), r["width"].Fq() ?? 3f, r["surface"].S() ?? "dirt"));
        int ai = 0;
        foreach (var a in L["areas"] as JsonArray ?? new JsonArray())
            areas.Add((V(a["centre"]), V(a["radius"]), a["lumps"].Fq() ?? 0.15f, a["surface"].S() ?? "dirt", 31 + ai++));
        mounds.Clear();
        foreach (var m in L["mounds"] as JsonArray ?? new JsonArray())
        {
            var r = m["radius"];
            var rv = r is JsonArray ? V(r) : new Vector2(r.Fq() ?? 6f, r.Fq() ?? 6f);
            mounds.Add((V(m["centre"]), rv, m["rot"].Fq() ?? 0f, m["height"].Fq() ?? 2f, Mathf.Clamp(m["top"].Fq() ?? 0.3f, 0f, 0.9f)));
        }
        ParseTerrain();                  // the tiers, before anything stands on them

        Buildings();                     // first: their pads shape the ground
        Ground();
        Terrain();                       // the terrain tiles over the ground (KitVillage.Terrain.cs)
        Gardens();
        Props();
        SeaMasks();                      // the moored hulls' negative space in the water (KitVillage.Terrain.cs)
        Fences();
        Trees();
        DressTerrain();                  // the cliffs' and ramps' dressing, clear of what stands there now
        Forest();
        Scatter();
        Markers();
        Links();
        Encounters();
        Exits();
        Walls();
        foreach (var t in new[] { buildT, propT, natureT }) Swap(t, null);   // the map's palette, its nature too (props swap their own first)
        PieceSwaps();                    // some of the nature's pieces only (KitVillage.Patches.cs)
        Patches();                       // ground patches round what stands, into the control map (KitVillage.Patches.cs)
        Grass(GroundMaterialInstance);   // last: it keeps clear of everything placed
    }

    /// <summary>a material by the name a layout gives it: a kit material's name, a res:// path, or (a Unity layout) a
    /// .mat asset path whose file name is a kit material's</summary>
    static Material MaterialNamed(string to)
    {
        if (string.IsNullOrEmpty(to)) return null;
        if (to.StartsWith("res://")) return ResourceLoader.Exists(to) ? GD.Load<Material>(to) : null;
        string want = to.EndsWith(".mat") ? System.IO.Path.GetFileNameWithoutExtension(to) : to;
        return KitInteriorRules.Default.Mat(want);
    }

    /// <summary>a material's kit name (its library file's)</summary>
    static string NameOf(Material m) => m == null ? null : !string.IsNullOrEmpty(m.ResourcePath) ? m.ResourcePath.GetFile().GetBaseName() : m.ResourceName;

    /// <summary>material swaps by name, {"M_VK_RoofRed": "M_VK_Thatch"}: the layout's "swap" (the whole map's palette,
    /// e.g. a goblin camp's hide and thatch), overridden by an entry's own "swap"; the one swapped in is a kit material's
    /// name or a res:// path</summary>
    void Swap(Node go, JsonNode spec)
    {
        var map = new Dictionary<string, string>();
        foreach (var src in new[] { L["swap"], spec?["swap"] })
            if (src is JsonObject o) foreach (var kv in o) map[kv.Key] = kv.Value.S();
        if (map.Count == 0 || go == null) return;
        foreach (var mi in Meshes(go))
        {
            if (mi.Mesh == null) continue;
            bool changed = false;
            for (int i = 0; i < mi.Mesh.GetSurfaceCount(); i++)
            {
                var cur = mi.GetActiveMaterial(i);
                string n = NameOf(cur);
                if (n == null || !map.TryGetValue(n, out var to)) continue;
                var m = MaterialNamed(to);
                if (m == null) { notes.Add($"no material {to} to swap in"); continue; }
                mi.SetSurfaceOverrideMaterial(i, m); changed = true;
            }
            if (changed) Editable(mi);
        }
    }

    /// <summary>a change below an instanced piece saved with the scene: the piece marked editable</summary>
    void Editable(Node n)
    {
        for (var p = n; p != null && p != this; p = p.GetParent())
            if (!string.IsNullOrEmpty(p.SceneFilePath) && p.Owner != null) { SceneOwner.SetEditableInstance(p, true); return; }
    }

    static IEnumerable<MeshInstance3D> Meshes(Node go) =>
        (go is MeshInstance3D m ? new[] { m } : Enumerable.Empty<MeshInstance3D>()).Concat(KitNodes.Below(go, "MeshInstance3D").OfType<MeshInstance3D>());

    Node3D Group(string n)
    {
        var t = new Node3D { Name = n };
        AddChild(t);
        t.Owner = SceneOwner;
        return t;
    }

    /// <summary>a node's transform in this node's space (n below it), without the tree</summary>
    Transform3D Rel(Node3D n)
    {
        var t = Transform3D.Identity;
        for (Node c = n; c != null && c != this; c = c.GetParent()) if (c is Node3D c3) t = c3.Transform * t;
        return t;
    }

    /// <summary>a mesh's box in this node's space</summary>
    Aabb BoundsOf(MeshInstance3D mi) => Rel(mi) * mi.GetAabb();

    /// <summary>the piece a mesh belongs to: its nearest KitPiece above it (else the mesh itself), whose name tells what
    /// it is (a wall, a door, a roof)</summary>
    static Node PieceOf(Node n)
    {
        for (var p = n; p != null; p = p.GetParent()) if (p is KitPiece) return p;
        return n;
    }

    PackedScene Prefab(string name)
    {
        if (string.IsNullOrEmpty(name)) return null;
        foreach (var n in new[] { name, "SM_VK_" + name, "SM_VKI_Prop_" + name, "SM_VKI_" + name })
        {
            string st = KitPaths.Structures + n + ".tscn";
            if (ResourceLoader.Exists(st)) return GD.Load<PackedScene>(st);
            var p = KitInteriorRules.Default.Prefab(n);
            if (p != null) return p;
        }
        notes.Add($"no prefab {name}");
        return null;
    }

    /// <summary>a piece made under parent, named after its scene (a structure's id is set by the caller)</summary>
    Node3D Make(PackedScene ps, Node3D parent)
    {
        var go = Spawn(ps);
        parent.AddChild(go, true);
        go.Owner = SceneOwner;
        return go;
    }

    // ------------------------------------------------------------------ curves and shapes
    /// <summary>a Catmull-Rom curve through the points, sampled every metre or so</summary>
    public static Vector2[] Spline(List<Vector2> p)
    {
        if (p.Count < 2) return p.ToArray();
        var o = new List<Vector2>();
        for (int i = 0; i < p.Count - 1; i++)
        {
            Vector2 p0 = p[Mathf.Max(0, i - 1)], p1 = p[i], p2 = p[i + 1], p3 = p[Mathf.Min(p.Count - 1, i + 2)];
            int n = Mathf.Max(2, Mathf.CeilToInt((p2 - p1).magnitude));
            for (int k = 0; k < n; k++)
            {
                float t = k / (float)n, t2 = t * t, t3 = t2 * t;
                o.Add(0.5f * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3));
            }
        }
        o.Add(p[p.Count - 1]);
        return o.ToArray();
    }

    /// <summary>a closed Catmull-Rom curve through the points (a ring), its first point repeated at the end</summary>
    public static Vector2[] ClosedSpline(List<Vector2> p)
    {
        if (p.Count < 3) return p.Concat(p.Take(1)).ToArray();
        var o = new List<Vector2>();
        int m = p.Count;
        for (int i = 0; i < m; i++)
        {
            Vector2 p0 = p[(i - 1 + m) % m], p1 = p[i], p2 = p[(i + 1) % m], p3 = p[(i + 2) % m];
            int n = Mathf.Max(2, Mathf.CeilToInt((p2 - p1).magnitude));
            for (int k = 0; k < n; k++)
            {
                float t = k / (float)n, t2 = t * t, t3 = t2 * t;
                o.Add(0.5f * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3));
            }
        }
        o.Add(p[0]);
        return o.ToArray();
    }

    static float DistToPolyline(Vector2 q, Vector2[] pts)
    {
        float best = float.MaxValue;
        for (int i = 0; i < pts.Length - 1; i++)
        {
            Vector2 a = pts[i], b = pts[i + 1], ab = b - a;
            float t = ab.sqrMagnitude < 1e-6f ? 0 : Mathf.Clamp01(Vector2.Dot(q - a, ab) / ab.sqrMagnitude);
            best = Mathf.Min(best, (q - (a + ab * t)).magnitude);
        }
        return best;
    }

    static bool InPoly(Vector2 q, Vector2[] poly)
    {
        bool inside = false;
        for (int i = 0, j = poly.Length - 1; i < poly.Length; j = i++)
            if ((poly[i].y > q.y) != (poly[j].y > q.y) && q.x < (poly[j].x - poly[i].x) * (q.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)
                inside = !inside;
        return inside;
    }

    static float DistToPoly(Vector2 q, Vector2[] poly)
    {
        if (InPoly(q, poly)) return 0f;
        var closed = poly.Concat(new[] { poly[0] }).ToArray();
        return DistToPolyline(q, closed);
    }

    /// <summary>a lumpy ellipse: &lt; 1 inside</summary>
    static float Blob(Vector2 q, Vector2 c, Vector2 r, float lumps, int seed)
    {
        float a = Mathf.Atan2(q.y - c.y, q.x - c.x);
        float k = 1 + lumps * (Mathf.Sin(3 * a + seed * 0.7f) * 0.6f + Mathf.Sin(5 * a + seed * 1.3f) * 0.4f);
        float dx = (q.x - c.x) / (r.x * k), dy = (q.y - c.y) / (r.y * k);
        return Mathf.Sqrt(dx * dx + dy * dy);
    }

    /// <summary>the clearing (one lumpy oval) or the clearings (glades along a path: their union) of a layout</summary>
    static List<(Vector2 c, Vector2 r, float lumps, int seed)> Clearings(JsonObject lay, float w, float h)
    {
        var list = (lay["clearings"] as JsonArray)?.ToList() ?? new List<JsonNode>();
        if (list.Count == 0) list.Add(lay["clearing"] ?? new JsonObject());
        return list.Select((cl, i) => (cl["centre"] != null ? V(cl["centre"]) : new Vector2(w / 2, h / 2),
                                      cl["radius"] != null ? V(cl["radius"]) : new Vector2(w / 2 - 12, h / 2 - 12),
                                      cl["lumps"].Fq() ?? 0.1f, 3 + 7 * i)).ToList();
    }

    static float Union(Vector2 q, List<(Vector2 c, Vector2 r, float lumps, int seed)> cs) =>
        cs.Count == 0 ? 0f : cs.Min(k => Blob(q, k.c, k.r, k.lumps, k.seed));

    /// <summary>&lt; 1 inside the clearing (or any of the clearings)</summary>
    float Clearing(Vector2 q) => Union(q, clears);

    // ------------------------------------------------------------------ ground
    float Noise(float x, float y, float s) => Mathf.PerlinNoise(x / s + 31.7f, y / s + 17.3f);

    /// <summary>the ground's natural height: a gentle relief, rising into the forest</summary>
    float Natural(Vector2 q)
    {
        float relief = L["relief"].Fq() ?? 0.3f, rim = L["rim"].Fq() ?? 2.5f;
        float h = relief * ((Noise(q.x, q.y, 23f) - 0.5f) * 2f + (Noise(q.x, q.y, 7f) - 0.5f) * 0.5f);
        h += rim * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.95f, 1.35f, Clearing(q)));
        foreach (var m in mounds) h += Mound(q, m);
        return h;
    }

    /// <summary>a mound's rise at q (a barrow, a knoll): an ellipse turned by rot degrees, rising smoothly from its rim
    /// to a rounded crown that is flat over `top` of its radius</summary>
    static float Mound(Vector2 q, (Vector2 c, Vector2 r, float rot, float h, float top) m)
    {
        var d = Rot(q - m.c, -m.rot);
        float e = Mathf.Sqrt((d.x / m.r.x) * (d.x / m.r.x) + (d.y / m.r.y) * (d.y / m.r.y));
        if (e >= 1f) return 0f;
        float t = Mathf.Clamp01((1f - e) / (1f - m.top));
        return m.h * t * t * (3f - 2f * t);
    }

    /// <summary>the natural height on the terrain: a raised cell's tier, else the natural ground, flattened towards a
    /// cliff's foot</summary>
    float Base(Vector2 q)
    {
        if (!HasTerrain) return Natural(q);
        int l = LevelAt(q);
        if (l > 0) return l * Tier;
        float h = Natural(q), w = TerrainNear(q);
        return w > 0f ? Mathf.Lerp(h, 0f, w) : h;
    }

    /// <summary>the ground's height: natural (on the terrain's tiers), levelled to each building's pad near it; on the
    /// sea its water's surface (what is put there floats)</summary>
    public float Height(Vector2 q)
    {
        if (InSea(q)) return SeaWater;
        float h = Base(q);
        if (HasTerrain && LevelAt(q) > 0) return h;                       // a tier is flat
        foreach (var (poly, ph) in pads)
        {
            float d = DistToPoly(q, poly);
            if (d < 4f) h = Mathf.Lerp(ph, h, Mathf.SmoothStep(0f, 1f, d / 4f));
        }
        return h;
    }

    /// <summary>the ground mesh's height at a mesh vertex (plan point): the sea's bed, hidden under a tier, else Height</summary>
    float GroundZ(Vector2 q) => SeaGround(q, out float sz) ? sz : HasTerrain && LevelAt(q) > 0 ? 0f : Height(q);

    void Ground()
    {
        // the mesh spans the map and its margin; its own origin sits at the margin's south-west corner (the terrain
        // material projects its control map in object space, from 0)
        float GW = W + 2 * M, GH = H + 2 * M;
        int nx = Mathf.CeilToInt(GW / Res) + 1, ny = Mathf.CeilToInt(GH / Res) + 1;
        var z = new float[nx * ny];
        var verts = new Godot.Vector3[nx * ny];
        var cols = new Color[nx * ny];
        for (int j = 0; j < ny; j++)
            for (int i = 0; i < nx; i++)
            {
                var o = new Vector2(Mathf.Min(GW, i * Res), Mathf.Min(GH, j * Res));
                var q = o - new Vector2(M, M);
                z[j * nx + i] = GroundZ(q);
                verts[j * nx + i] = Local(o.x, o.y, z[j * nx + i]);
                float shade = Mathf.Lerp(1f, 0.82f, Mathf.InverseLerp(1.0f, 1.25f, Clearing(q)));     // the forest floor in shade
                cols[j * nx + i] = new Color(shade, 0f, 0f, 0f);
            }
        // normals from the height field (central differences); Godot's front faces wind clockwise seen from them
        var norms = new Godot.Vector3[nx * ny];
        for (int j = 0; j < ny; j++)
            for (int i = 0; i < nx; i++)
            {
                float hx = z[j * nx + Math.Min(i + 1, nx - 1)] - z[j * nx + Math.Max(i - 1, 0)];
                float hy = z[Math.Min(j + 1, ny - 1) * nx + i] - z[Math.Max(j - 1, 0) * nx + i];
                float dx = (Math.Min(i + 1, nx - 1) - Math.Max(i - 1, 0)) * Res, dy = (Math.Min(j + 1, ny - 1) - Math.Max(j - 1, 0)) * Res;
                norms[j * nx + i] = new Godot.Vector3(-hx / dx, 1f, hy / dy).Normalized();        // plan +y is -z
            }
        var tris = new List<int>();
        for (int j = 0; j < ny - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int a = j * nx + i, b = a + 1, c = a + nx, d = c + 1;
                tris.AddRange(new[] { a, c, b, b, c, d });
            }
        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = verts;
        arrays[(int)Mesh.ArrayType.Normal] = norms;
        arrays[(int)Mesh.ArrayType.Color] = cols;
        arrays[(int)Mesh.ArrayType.Index] = tris.ToArray();
        var mesh = new ArrayMesh { ResourceName = $"{Name}_Ground" };
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        arrays.Dispose();
        GroundMesh = mesh;
        var go = new MeshInstance3D { Name = "Ground", Mesh = mesh, Position = Local(-M, -M, 0f) };
        groundT.AddChild(go);
        go.Owner = SceneOwner;
        PaintControl();
        var gm = groundMaterial ?? KitInteriorRules.Default.Mat("M_VK_Terrain");
        if (gm is ShaderMaterial sm)
        {
            GroundMaterialInstance = (ShaderMaterial)sm.Duplicate();
            GroundMaterialInstance.ResourceName = $"{Name}_Ground";
            GroundMaterialInstance.SetShaderParameter("ctl_map", ControlMap);
            GroundMaterialInstance.SetShaderParameter("ctl_scale", new Godot.Vector2(1f / GW, 1f / GH));
            go.MaterialOverride = GroundMaterialInstance;
        }
        else notes.Add("no ground material (M_VK_Terrain)");
        var body = new StaticBody3D { Name = "GroundBody", CollisionLayer = KitPiece.Solid };
        go.AddChild(body);
        body.Owner = SceneOwner;
        var shape = new CollisionShape3D { Name = "Mesh", Shape = mesh.CreateTrimeshShape() };
        body.AddChild(shape);
        shape.Owner = SceneOwner;
    }

    /// <summary>the control map: R dirt (roads, trodden areas, doorsteps), G cobble (paved areas), B sand</summary>
    void PaintControl()
    {
        int tw = Mathf.CeilToInt((W + 2 * M) * CtlPerM), th = Mathf.CeilToInt((H + 2 * M) * CtlPerM);
        var px = new Color[tw * th];
        var boxes = roads.Select(r => (min: new Vector2(r.pts.Min(p => p.x), r.pts.Min(p => p.y)) - Vector2.one * (r.width / 2 + 2),
                                       max: new Vector2(r.pts.Max(p => p.x), r.pts.Max(p => p.y)) + Vector2.one * (r.width / 2 + 2))).ToList();
        var doors = builtById.Values.SelectMany(b => DoorsOf(b.t)).Select(DoorPoint).ToList();
        for (int j = 0; j < th; j++)
            for (int i = 0; i < tw; i++)
            {
                var q = new Vector2((i + 0.5f) / CtlPerM - M, (j + 0.5f) / CtlPerM - M);
                float n = (Noise(q.x, q.y, 3.1f) - 0.5f) * 0.9f;
                float dirt = 0f, cob = 0f, sand = 0f;
                for (int ri = 0; ri < roads.Count; ri++)
                {
                    var (_, pts, width, surface) = roads[ri];
                    if (q.x < boxes[ri].min.x || q.y < boxes[ri].min.y || q.x > boxes[ri].max.x || q.y > boxes[ri].max.y) continue;
                    float d = DistToPolyline(q, pts) + n;
                    float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(width / 2 - 0.6f, width / 2 + 0.6f, d));
                    if (surface == "cobble") cob = Mathf.Max(cob, w); else dirt = Mathf.Max(dirt, w);
                }
                foreach (var (c, r, lumps, surface, seed) in areas)
                {
                    float b = Blob(q, c, r, lumps, seed) + n * 0.08f;
                    float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.85f, 1.05f, b));
                    if (surface == "cobble") { cob = Mathf.Max(cob, w * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1.0f, 0.7f, b))); dirt = Mathf.Max(dirt, w); }
                    else if (surface == "sand") sand = Mathf.Max(sand, w);  // the material's sand layer (a burnt map's ash, the Northfields' burnt ground)
                    else dirt = Mathf.Max(dirt, w);
                }
                foreach (var dp in doors)
                {
                    float d = (q - dp).magnitude + n;
                    dirt = Mathf.Max(dirt, 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1.4f, 2.6f, d)));
                }
                if (HasSea)                                                     // the sea's bed and its shore: wet dirt, no grass
                    dirt = Mathf.Max(dirt, 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.2f, 1.4f, SeaDist(q) + n * 0.6f)));
                px[j * tw + i] = new Color(dirt, cob, sand, 0f);
            }
        ControlImage = Image.CreateEmpty(tw, th, false, Image.Format.Rgba8);
        WriteControl(px, tw, th);
    }

    /// <summary>the control map's pixels (plan rows, south first) into the image (north first) and its texture</summary>
    void WriteControl(Color[] px, int tw, int th)
    {
        for (int j = 0; j < th; j++)
            for (int i = 0; i < tw; i++) ControlImage.SetPixel(i, th - 1 - j, px[j * tw + i]);
        if (ControlMap == null || ControlMap.GetWidth() != tw || ControlMap.GetHeight() != th) { ControlMap = ImageTexture.CreateFromImage(ControlImage); ControlMap.ResourceName = $"{Name}_GroundControl"; }
        else ControlMap.Update(ControlImage);
    }

    /// <summary>the control map's pixels back (plan rows, south first)</summary>
    Color[] ReadControl()
    {
        int tw = ControlImage.GetWidth(), th = ControlImage.GetHeight();
        var px = new Color[tw * th];
        for (int j = 0; j < th; j++)
            for (int i = 0; i < tw; i++) px[j * tw + i] = ControlImage.GetPixel(i, th - 1 - j);
        return px;
    }

    // ------------------------------------------------------------------ buildings
    /// <summary>a piece's doors: the pieces below it named for a door</summary>
    static List<Node3D> DoorsOf(Node3D inst) =>
        KitNodes.Below(inst, "Node3D").OfType<Node3D>().Where(t => t != inst && t.Name.ToString().Contains("Door") && PieceOf(t) == t).ToList();

    /// <summary>a door's middle (its mesh's box's centre, else its place), plan space</summary>
    Vector2 DoorPoint(Node3D door)
    {
        var mi = Meshes(door).FirstOrDefault();
        return Plan(mi != null ? BoundsOf(mi).GetCenter() : Rel(door).Origin);
    }

    /// <summary>a prefab's footprint (plan space, unturned, about its origin) and its front (the side its door is on)</summary>
    (Rect box, Vector2 front) Measure(Node3D inst) { var (box, _, front) = MeasureWalls(inst); return (box, front); }

    Rect PlanBox(IEnumerable<MeshInstance3D> rs, Godot.Vector3 fallback)
    {
        var list = rs.Where(r => r.Mesh != null).ToList();
        var b = list.Count > 0 ? BoundsOf(list[0]) : new Aabb(fallback - Godot.Vector3.One * 0.5f, Godot.Vector3.One);
        foreach (var r in list) b = b.Merge(BoundsOf(r));
        return Rect.MinMaxRect(b.Position.X, -b.End.Z, b.End.X, -b.Position.Z);
    }

    /// <summary>as Measure, plus the box of its walls alone (what one bumps into: no eaves, signs or porches)</summary>
    (Rect box, Rect walls, Vector2 front) MeasureWalls(Node3D inst)
    {
        var save = inst.Transform;
        inst.Transform = new Transform3D(Basis.Identity.Scaled(save.Basis.Scale), Godot.Vector3.Zero);
        var rs = Meshes(inst).ToList();
        var box = PlanBox(rs, Rel(inst).Origin);
        var wallRs = rs.Where(r => { string n = PieceOf(r).Name; return n.Contains("Wall") || n.Contains("Corner") || n.Contains("Foundation"); }).ToList();
        var walls = wallRs.Count > 0 ? PlanBox(wallRs, Rel(inst).Origin) : box;
        Vector2 front = new Vector2(0f, -1f);
        var doors = DoorsOf(inst);
        if (doors.Count > 0)
        {
            var dl = DoorPoint(doors[0]);
            var d = dl - box.center;
            // the door's side: the axis it opens along (its own forward), on the side of the walls it stands at; a
            // building with a yard (the smithy's forge, the training yard, the woodcutter's) has a box whose nearest
            // edge is not the door's. Without a turn to read: the axis it sits nearest the edge of
            var fw = Rel(doors[0]).Basis.Z;                               // the piece's front (Blender -Y) is its +Z
            var fp = new Vector2(fw.X, -fw.Z);
            var dw = dl - walls.center;
            if (fp.sqrMagnitude > 0.01f && Mathf.Abs(Mathf.Abs(fp.x) - Mathf.Abs(fp.y)) > 0.2f)
                front = Mathf.Abs(fp.x) > Mathf.Abs(fp.y) ? new Vector2(Mathf.Sign(dw.x), 0f) : new Vector2(0f, Mathf.Sign(dw.y));
            else
            {
                float ex = Mathf.Abs(d.x) / Mathf.Max(0.1f, box.width / 2), ey = Mathf.Abs(d.y) / Mathf.Max(0.1f, box.height / 2);
                front = ex > ey ? new Vector2(Mathf.Sign(d.x), 0f) : new Vector2(0f, Mathf.Sign(d.y));
            }
        }
        inst.Transform = save;
        return (box, walls, front);
    }

    static Vector2[] Corners(Rect box, Vector2 at, float deg, float grow = 0f)
    {
        var r = new Rect(box.xMin - grow, box.yMin - grow, box.width + 2 * grow, box.height + 2 * grow);
        return new[] { new Vector2(r.xMin, r.yMin), new Vector2(r.xMax, r.yMin), new Vector2(r.xMax, r.yMax), new Vector2(r.xMin, r.yMax) }
            .Select(c => Rot(c, deg) + at).ToArray();
    }

    float Facing(JsonNode spec, Vector2 at, Vector2 front)
    {
        if (spec["rot"] != null) return spec["rot"].F();
        Vector2 target;
        if (spec["face"] is JsonArray fa) target = V(fa);
        else if (spec["face"].IsStr() && spec["face"].S().StartsWith("road:"))
        {
            var rd = roads.FirstOrDefault(r => r.id == spec["face"].S().Substring(5));
            target = rd.pts != null ? rd.pts.OrderBy(p => (p - at).sqrMagnitude).First() : at + Vector2.down;
        }
        else return 0f;
        return Ang(target - at) - Ang(front);
    }

    void Place(Node3D go, Vector2 at, float h, float deg)
    {
        go.Transform = new Transform3D(Turn(deg).Scaled(go.Basis.Scale), Local(at.x, at.y, h));
    }

    void Buildings()
    {
        var rules = houseRules ?? KitHouseRules.Default;
        foreach (var b in L["buildings"] as JsonArray ?? new JsonArray())
        {
            string id = b["id"].S() ?? "building";
            var at = V(b["at"]);
            Node3D inst;
            if (b["house"] is JsonObject hs)
            {
                var hg = new KitHouseGenerator { Name = id, rules = houseRules };
                buildT.AddChild(hg, true);
                hg.Owner = SceneOwner;
                hg.cells = hs["cells"].Iq() ?? 2; hg.stories = hs["stories"].Iq() ?? 1; hg.seed = hs["seed"].Iq() ?? 1;
                if (hs["shape"].S() == "L") hg.shape = KitHouseGenerator.Shape.L;
                if (hs["front"] != null) hg.front = hs["front"].S();
                hg.Generate();
                inst = hg;
            }
            else
            {
                var pf = Prefab(b["structure"].S());
                if (pf == null) continue;
                inst = Make(pf, buildT);
                inst.Name = id;
                if (b["swap"] != null) Swap(inst, b);
            }
            var (box, walls, front) = MeasureWalls(inst);
            float deg = Facing(b, at, front);
            float h = Base(at);
            Place(inst, at, h, deg);
            var poly = Corners(box, at, deg);
            foreach (var (op, oid) in occupied)
                if (poly.Any(p => InPoly(p, op)) || op.Any(p => InPoly(p, poly))) notes.Add($"{id} overlaps {oid}");
            foreach (var rd in roads)
                if (rd.pts.Any(p => InPoly(p, Corners(box, at, deg, rd.width / 2 - 0.3f)))) notes.Add($"{id} stands on road {rd.id}");
            float wallAt = L["forest"]?["wallAt"].Fq() ?? 1.08f;
            if (poly.Any(c => Clearing(c) > wallAt)) notes.Add($"{id} reaches past the forest's wall (move it in or widen the clearing)");
            occupied.Add((poly, id));
            // its pad levels the ground round it -- not one on a terrain tier (the tier is flat; easing the ground
            // below up to it would bury the cliff's foot and bank a second way up)
            if (!HasTerrain || LevelAt(at) == 0) pads.Add((Corners(box, at, deg, 1.2f), h));
            builtById[id] = (inst, at, deg);
            AddBox(inst, walls, h: 4f, inset: 0.1f);
            Dress(inst, walls);
            if (b["door"] is JsonObject door) Door(inst, id, door, at, deg);
        }
    }

    /// <summary>a building's own dressing outside its walls' box (barrels by the door, a trough, hay, a table and
    /// stools, its yard's fence, a lean-to's posts, a bell tower beside the nave): boxes over what one bumps into
    /// (<see cref="KitSolid.Box"/>: below 1.2 m, part by part), or the walkers go through it. Left as they are: what
    /// is overhead (eaves, signs' arms, lanterns), the porch one walks onto, a yard's gate, soft dressing (weeds, ivy,
    /// flower boxes), piers and decks.</summary>
    void Dress(Node3D inst, Rect walls)
    {
        var inner = new Rect(walls.xMin - 0.05f, walls.yMin - 0.05f, walls.width + 0.1f, walls.height + 0.1f);
        var toInst = Rel(inst).AffineInverse();
        float floor = Rel(inst).Origin.Y;
        foreach (var pieceNode in Meshes(inst).Select(PieceOf).OfType<Node3D>().Distinct().ToList())
        {
            string n = pieceNode.Name;
            if (pieceNode == inst || KitSolid.IsSoft(n) || new[] { "Wall", "Corner", "Foundation", "Roof", "Porch", "Door", "Window", "Gate" }.Any(n.Contains))
                continue;
            var ms = Meshes(pieceNode).Where(m => m.Mesh != null).ToList();
            if (ms.Count == 0) continue;
            var all = ms.Select(BoundsOf).Aggregate((a, c) => a.Merge(c));
            if (all.Position.Y > floor + 1.8f) continue;
            bool inside = true;
            foreach (var mi in ms)
            {
                var b = mi.GetAabb();
                var rel = toInst * Rel(mi);
                foreach (float x in new[] { b.Position.X, b.End.X })
                    foreach (float z in new[] { b.Position.Z, b.End.Z })
                    {
                        var l = rel * new Godot.Vector3(x, b.Position.Y, z);
                        if (!inner.Contains(new Vector2(l.X, -l.Z))) inside = false;
                    }
            }
            if (!inside) KitSolid.Box(pieceNode, owner: SceneOwner);
        }
    }

    /// <summary>a box collider over a footprint (plan space about the object's origin)</summary>
    void AddBox(Node3D go, Rect box, float h, float inset)
    {
        var body = new StaticBody3D { Name = "Box", CollisionLayer = KitPiece.Solid };
        go.AddChild(body, true);
        body.Owner = SceneOwner;
        var c = new CollisionShape3D
        {
            Shape = new BoxShape3D { Size = new Godot.Vector3(Mathf.Max(0.2f, box.width - 2 * inset), h, Mathf.Max(0.2f, box.height - 2 * inset)) },
            Position = new Godot.Vector3(box.center.x, h / 2, -box.center.y),
        };
        body.AddChild(c);
        c.Owner = SceneOwner;
    }

    /// <summary>a trigger box (the link's) on a node: Area3D with a KitLink</summary>
    KitLink LinkAt(string name, Vector2 at, float h, float deg, Godot.Vector3 size, Godot.Vector3 centre)
    {
        var lk = new KitLink { Name = name, Monitorable = false };
        logicT.AddChild(lk, true);
        lk.Owner = SceneOwner;
        lk.Transform = new Transform3D(Turn(deg), Local(at.x, at.y, h));
        var cs = new CollisionShape3D { Name = "Trigger", Shape = new BoxShape3D { Size = size }, Position = centre };
        lk.AddChild(cs);
        cs.Owner = SceneOwner;
        return lk;
    }

    /// <summary>a building's door as a scene link: a trigger on the door, a spawn on the doorstep facing out</summary>
    void Door(Node3D inst, string id, JsonObject spec, Vector2 at, float deg)
    {
        var dt = DoorsOf(inst).FirstOrDefault();
        Vector2 dp;
        if (dt != null) dp = DoorPoint(dt);
        else if ((inst as KitPiece)?.Has("vki_spawn_local") == true) dp = at;    // a link piece (a cave mouth): its origin is the opening
        else { notes.Add($"{id}: no door piece for its link"); return; }
        var (_, front) = Measure(inst);
        var outward = Rot(front, deg);                       // the door faces out along the building's front
        var lk = LinkAt("LNK_" + id, dp + outward * 0.6f, Height(dp), Ang(outward) - 90f, new Godot.Vector3(1.6f, 2.2f, 1.2f), new Godot.Vector3(0, 1.1f, 0));
        lk.LinkId = id; lk.Kind = "exit"; lk.Target = spec["target"].S() ?? ""; lk.Prompt = spec["prompt"].S() ?? "Enter"; lk.FacingMin = 75f;
        lk.Arrive = spec["arrive"].S() ?? "";                // the spawn inside (e.g. an interior's "front")
        SpawnAt(id, dp + outward * 1.8f, Bearing(outward));
    }

    static float Bearing(Vector2 dir) => Mathf.Repeat(90f - Ang(dir), 360f);

    // ------------------------------------------------------------------ props, fences, trees
    Node3D Place(Node3D parent, string piece, Vector2 at, float deg, float scale = 1f, bool collide = false)
    {
        var pf = Prefab(piece);
        if (pf == null) return null;
        var go = Make(pf, parent);
        if (Mathf.Abs(scale - 1f) > 1e-3f) go.Scale = Godot.Vector3.One * scale;
        Place(go, at, Height(at), deg);
        if (collide)
        {
            var (box, _) = Measure(go);
            AddBox(go, box, h: 2.5f, inset: 0.15f);
        }
        return go;
    }

    /// <summary>gardens: crop beds in a grid (turned with the garden), a fence round them with a gate on one side</summary>
    void Gardens()
    {
        foreach (var g in L["gardens"] as JsonArray ?? new JsonArray())
        {
            var at = V(g["at"]);
            float deg = g["rot"].Fq() ?? 0f, cell = g["cell"].Fq() ?? 3.3f;
            var size = g["beds"] as JsonArray;
            int cols = size != null ? size[0].I() : 2, rows = size != null ? size[1].I() : 2;
            var crops = (g["crops"] as JsonArray)?.Select(c => c.S()).ToList() ?? new List<string> { "Crop_Cabbage" };
            float w = cols * cell, d = rows * cell;
            int k = 0;
            for (int i = 0; i < cols; i++)
                for (int j = 0; j < rows; j++)
                {
                    var local = new Vector2((i + 0.5f) * cell - w / 2, (j + 0.5f) * cell - d / 2);
                    Place(propT, crops[k++ % crops.Count], at + Rot(local, deg), deg + 90f * rnd.Next(4));
                }
            var box = new Rect(-w / 2 - 0.8f, -d / 2 - 0.8f, w + 1.6f, d + 1.6f);
            occupied.Add((Corners(box, at, deg), g["id"].S() ?? "garden"));
            string fence = g["fence"].S();
            if (fence == null) continue;
            // the fence: the box's four sides, the gate side ("S" by default: the garden's local -y) left with a gate
            var c4 = Corners(box, at, deg);              // SW, SE, NE, NW in the garden's frame
            string gateSide = g["gate"].S() ?? "S";
            var sides = new[] { ("S", c4[0], c4[1]), ("E", c4[1], c4[2]), ("N", c4[2], c4[3]), ("W", c4[3], c4[0]) };
            foreach (var (sd, a, b) in sides)
            {
                var spec = new JsonObject { ["piece"] = fence, ["smooth"] = false, ["points"] = KitJson.A(KitJson.A(a.x, a.y), KitJson.A(b.x, b.y)) };
                if (sd == gateSide && g["gatePiece"] != null) { spec["gate"] = g["gatePiece"].S(); spec["gateAt"] = KitJson.A(0.5); }
                FenceLine(spec);
            }
        }
    }

    void Props()
    {
        foreach (var p in L["props"] as JsonArray ?? new JsonArray())
        {
            var at = V(p["at"]);
            string pn = p["piece"].S();
            var pf = Prefab(pn);
            if (pf == null) continue;
            var go = Make(pf, propT);
            float scale = p["scale"].Fq() ?? 1f;
            if (Mathf.Abs(scale - 1f) > 1e-3f) go.Scale = Godot.Vector3.One * scale;
            var (box, front) = Measure(go);
            float deg = Facing(p, at, front);
            Place(go, at, p["z"].Fq() ?? Height(at), deg);   // "z": its own height (a jetty over the sea at its quay's)
            if (p["swap"] != null) Swap(go, p);
            string pieceName = (go as KitPiece)?.Piece ?? pn;
            if (p["collide"].Bq() ?? true)
            {
                if (KitSolid.IsTrunk(pieceName)) KitSolid.Trunk(go, SceneOwner);   // a tree or a stump as the forest's: its trunk
                else if (InSea(at)) SeaSurface(go);                               // a jetty, a mole: walked on over the water
                else KitSolid.Box(go, owner: SceneOwner);                        // what one bumps into: a signpost's post, not its arms
            }
            if (InSea(at) && IsHull(pieceName)) seaHulls.Add((go, at));          // its waterline cut out of the sea
            if (p["colliders"].Bq() == false)                                     // the piece's own colliders off too (a burrow mound one walks up onto)
            {
                foreach (var cs in KitNodes.Below(go, "CollisionShape3D").OfType<CollisionShape3D>()) cs.Disabled = true;
                Editable(go);
            }
            if (p["dress"].Bq() ?? true) Dress(go, pieceName);
            occupied.Add((Corners(box, at, deg), pn));
        }
    }

    /// <summary>a prop standing in the sea (a jetty, a breakwater): its own meshes collide, so the navmesh walks its deck
    /// or crest over the water (no ground under it to walk on, as a pier on land has) and its rails and parapets block</summary>
    void SeaSurface(Node3D go)
    {
        foreach (var mi in Meshes(go))
        {
            if (mi.Mesh == null) continue;
            var body = new StaticBody3D { Name = "Surface", CollisionLayer = KitPiece.Solid, Transform = Rel(go).AffineInverse() * Rel(mi) };
            go.AddChild(body, true);
            body.Owner = SceneOwner;
            var cs = new CollisionShape3D { Shape = mi.Mesh.CreateTrimeshShape() };
            body.AddChild(cs);
            cs.Owner = SceneOwner;
        }
    }

    /// <summary>the pieces a kit piece is only the base of, in its own frame (Godot metres -- Unity's frame with x
    /// mirrored -- and degrees), with a roof material (in place of its M_VK_Roof*): the gatehouse's block is finished
    /// by def_dress_gatehouse (vk_mod_defence) -- a timber storey on the walk (6.2), its slate hip roof and the towers'
    /// cones (9.0), the portcullis raised under the arch, the leaves open against the vault, banners on the town side;
    /// without them its flat top and open towers show</summary>
    public static readonly Dictionary<string, (string piece, Godot.Vector3 at, float rot, string roof)[]> Dressings = new()
    {
        ["SM_VK_Gatehouse_Block"] = new (string, Godot.Vector3, float, string)[]
        {
            ("SM_VK_Gatehouse_Portcullis", new(0f, 3.6f, 2.4f), 0f, null),
            ("SM_VK_Gatehouse_GateLeaf", new(-1.75f, 0f, 1.2f), 90f, null),
            ("SM_VK_Gatehouse_GateLeaf", new(1.75f, 0f, 1.2f), 90f, null),
            ("SM_VK_Wall_Timber_Window", new(-1.5f, 6.2f, 3f), 0f, null),
            ("SM_VK_Wall_Timber_Window", new(1.5f, 6.2f, 3f), 0f, null),
            ("SM_VK_Wall_Timber_X", new(-4.5f, 6.2f, -3f), 180f, null),
            ("SM_VK_Wall_Timber_Window", new(-1.5f, 6.2f, -3f), 180f, null),
            ("SM_VK_Wall_Timber_Window", new(1.5f, 6.2f, -3f), 180f, null),
            ("SM_VK_Wall_Timber_X", new(4.5f, 6.2f, -3f), 180f, null),
            ("SM_VK_Wall_Timber_Door", new(-6f, 6.2f, -1.5f), -90f, null),
            ("SM_VK_Wall_Timber", new(-6f, 6.2f, 1.5f), -90f, null),
            ("SM_VK_Wall_Timber_Door", new(6f, 6.2f, -1.5f), 90f, null),
            ("SM_VK_Wall_Timber", new(6f, 6.2f, 1.5f), 90f, null),
            ("SM_VK_Corner_Timber", new(-6f, 6.2f, -3f), -90f, null),
            ("SM_VK_Corner_Timber", new(6f, 6.2f, -3f), 180f, null),
            ("SM_VK_Roof_Hip", new(-4.5f, 9f, 0f), 180f, "M_VK_Roof_Slate"),
            ("SM_VK_Roof_Mid", new(-1.5f, 9f, 0f), 0f, "M_VK_Roof_Slate"),
            ("SM_VK_Roof_Mid", new(1.5f, 9f, 0f), 0f, "M_VK_Roof_Slate"),
            ("SM_VK_Roof_Hip", new(4.5f, 9f, 0f), 0f, "M_VK_Roof_Slate"),
            ("SM_VK_Roof_Cone_R2", new(-4.4f, 9f, 3f), 0f, "M_VK_Roof_Slate"),
            ("SM_VK_Roof_Cone_R2", new(4.4f, 9f, 3f), 0f, "M_VK_Roof_Slate"),
            ("SM_VK_Banner_Wall", new(-3f, 9f, -3.18f), 180f, null),
            ("SM_VK_Banner_Wall", new(3f, 9f, -3.18f), 180f, null),
        },
    };

    /// <summary>a piece's dressing (Dressings) as its children ("dress": false in the layout leaves it bare)</summary>
    void Dress(Node3D go, string piece)
    {
        if (!Dressings.TryGetValue(piece, out var parts)) return;
        foreach (var (n, at, rot, roof) in parts)
        {
            var pf = Prefab(n);
            if (pf == null) continue;
            var c = Make(pf, go);
            c.Transform = new Transform3D(Turn(rot), at);
            if (roof == null) continue;
            var m = MaterialNamed(roof);
            if (m == null) { notes.Add($"no material {roof} for {n}"); continue; }
            foreach (var mi in Meshes(c))
                for (int i = 0; i < (mi.Mesh?.GetSurfaceCount() ?? 0); i++)
                    if (NameOf(mi.GetActiveMaterial(i))?.StartsWith("M_VK_Roof", StringComparison.Ordinal) == true) mi.SetSurfaceOverrideMaterial(i, m);
            Editable(c);
        }
    }

    void Fences()
    {
        foreach (var f in L["fences"] as JsonArray ?? new JsonArray()) FenceLine(f);
    }

    void FenceLine(JsonNode f)
    {
        string piece = f["piece"].S() ?? "Prop_Fence", gate = f["gate"].S();
        string door = f["gateDoor"].S();               // doors in the gate's frame (a breakable gate: the way in)
        bool doorFlip = f["gateDoorFlip"].Bq() ?? false;
        var gates = (f["gateAt"] as JsonArray)?.Select(g => g.F()).OrderBy(g => g).ToList() ?? new List<float>();
        bool closed = f["closed"].Bq() ?? false, flip = f["flip"].Bq() ?? false, collide = f["collide"].Bq() ?? true;
        float offset = f["offset"].Fq() ?? 0f;
        float Length(string pn)
        {
            var pf = Prefab(pn);
            if (pf == null) return 0f;
            var probe = Make(pf, propT);
            var (bx, _) = Measure(probe);
            propT.RemoveChild(probe);
            probe.Free();
            return Mathf.Max(bx.width, bx.height);
        }
        float len = Length(piece);
        if (len <= 0f) return;
        float gw = gate != null && gates.Count > 0 ? Length(gate) : 0f;
        var pts = f["points"].AsArray().Select(V).ToList();
        if (closed) pts.Add(pts[0]);
        var curve = f["smooth"].Bq() ?? true ? (closed ? ClosedSpline(pts.Take(pts.Count - 1).ToList()) : Spline(pts)) : pts.ToArray();
        if (Mathf.Abs(offset) > 1e-3f)             // the line shifted sideways (left of the way it runs): a walkway behind a wall
            curve = curve.Select((q, i) =>
            {
                var d = curve[Mathf.Min(i + 1, curve.Length - 1)] - curve[Mathf.Max(i - 1, 0)];
                return q + new Vector2(-d.y, d.x).normalized * offset;
            }).ToArray();
        // walk the curve: runs of pieces between the gates, each piece turned along its chord and stretched to fit its
        // run; a gate keeps its own width
        float total = 0; var cum = new List<float> { 0 };
        for (int i = 1; i < curve.Length; i++) { total += (curve[i] - curve[i - 1]).magnitude; cum.Add(total); }
        Vector2 At(float s)
        {
            if (closed) s = Mathf.Repeat(s, total);
            int i = Mathf.Clamp(cum.FindIndex(c => c >= s), 1, curve.Length - 1);
            float t = Mathf.InverseLerp(cum[i - 1], cum[i], s);
            return Vector2.Lerp(curve[i - 1], curve[i], t);
        }
        void Lay(string pn, float s0, float s1, float pieceLen, bool isGate)
        {
            Vector2 a = At(s0), b = At(s1), mid = (a + b) / 2;
            float deg = Ang(b - a) + (flip ? 180f : 0f);
            var go = Place(propT, pn, mid, deg, 1f, collide: collide && !isGate);
            if (isGate && door != null)
            {
                var d = Place(propT, door, mid, deg + (doorFlip ? 180f : 0f));
                if (d != null) d.Name = "GATE_" + d.Name;
                else notes.Add($"no gate door {door}");
            }
            float chord = (b - a).magnitude;
            if (go != null && Mathf.Abs(chord - pieceLen) > 0.05f) go.Basis = go.Basis * Basis.FromScale(new Godot.Vector3(chord / pieceLen, 1f, 1f));
            if (collide || isGate) occupied.Add((Corners(new Rect(-chord / 2, -0.3f, chord, 0.6f), mid, Ang(b - a)), isGate ? "gate" : "fence"));
        }
        void Run(float s0, float s1)
        {
            float runLen = s1 - s0;
            if (runLen < len * 0.4f) return;
            int n = Mathf.Max(1, Mathf.RoundToInt(runLen / len));
            float step = runLen / n;
            for (int k = 0; k < n; k++) Lay(piece, s0 + k * step, s0 + (k + 1) * step, len, false);
        }
        var gs = gates.Select(g => g * total).ToList();
        if (gs.Count == 0) Run(0f, total);
        else
        {
            for (int i = 0; i < gs.Count; i++)
            {
                Lay(gate, gs[i] - gw / 2, gs[i] + gw / 2, gw, true);
                float next = i + 1 < gs.Count ? gs[i + 1] : closed ? gs[0] + total : total + gw / 2;
                Run(gs[i] + gw / 2, next - gw / 2);
            }
            if (!closed) Run(0f, gs[0] - gw / 2);
        }
        // pieces along the line, turned with it (a ladder up to a walkway: it leans on the deck only when it stands
        // where and as a walkway piece does)
        foreach (var e in f["along"] as JsonArray ?? new JsonArray())
        {
            string pn = e["piece"].S();
            if (pn == null) continue;
            foreach (var fr in e["at"] as JsonArray ?? new JsonArray())
            {
                float s = fr.F() * total;
                Vector2 a = At(s - 0.5f), b = At(s + 0.5f);
                var go = Place(propT, pn, At(s), Ang(b - a) + (flip ? 180f : 0f) + (e["rot"].Fq() ?? 0f), 1f, collide: e["collide"].Bq() ?? false);
                if (go == null) notes.Add($"no piece {pn} along a fence");
            }
        }
    }

    void Trees()
    {
        foreach (var t in L["trees"] as JsonArray ?? new JsonArray())
        {
            var at = V(t["at"]);
            var go = Place(natureT, t["piece"].S(), at, t["rot"].Fq() ?? (float)(rnd.NextDouble() * 360), t["scale"].Fq() ?? 1f);
            if (go != null) Trunk(go);
            occupied.Add((Corners(new Rect(-1, -1, 2, 2), at, 0), t["piece"].S()));
        }
    }

    void Trunk(Node3D tree) => KitSolid.Trunk(tree, SceneOwner);          // 0.45 m round its pivot (a burnt tree 0.4, its box gone)

    /// <summary>may a piece stand here: `keep` metres off roads and areas, `keepBuilt` off buildings, gardens and
    /// props (a tree's crown is wider than its trunk), off the map's very edge</summary>
    bool Free(Vector2 q, float keep, float keepBuilt = -1f, bool margin = false)
    {
        if (keepBuilt < 0) keepBuilt = keep;
        if (!margin && (q.x < 0.5f || q.y < 0.5f || q.x > W - 0.5f || q.y > H - 0.5f)) return false;
        if (margin && (q.x < -M || q.y < -M || q.x > W + M || q.y > H + M)) return false;
        if (NearCliff(q, 1.6f)) return false;                              // off the terrain's cliff lines and ramps
        if (SeaDist(q) < 1.5f) return false;                               // and out of the sea, off its shore
        foreach (var rd in roads) if (DistToPolyline(q, rd.pts) < rd.width / 2 + keep) return false;
        foreach (var a in areas) if (Blob(q, a.c, a.r, a.lumps, a.seed) < 1.05f + keep / Mathf.Max(1f, Mathf.Min(a.r.x, a.r.y))) return false;
        foreach (var (poly, _) in occupied) if (DistToPoly(q, poly) < keepBuilt) return false;
        return true;
    }

    /// <summary>the forest's ragged edge: the clearing's outline broken by two noises</summary>
    float EdgeAt(Vector2 q, float edge) => edge + (Noise(q.x, q.y, 8f) - 0.5f) * 0.16f + (Noise(q.x + 50f, q.y, 21f) - 0.5f) * 0.12f;

    List<(string piece, float w)> Weights(JsonNode t) =>
        (t as JsonArray ?? new JsonArray()).Select(e => (e[0].S(), e[1].F())).ToList();

    string Pick(List<(string piece, float w)> ws)
    {
        float s = ws.Sum(w => w.w), r = (float)rnd.NextDouble() * s;
        foreach (var (p, w) in ws) { if ((r -= w) <= 0) return p; }
        return ws.Last().piece;
    }

    /// <summary>dart throwing with a minimum spacing, in a region</summary>
    List<Vector2> Darts(Func<Vector2, bool> where, float spacing, int tries, float pad = 0f)
    {
        var o = new List<Vector2>();
        var grid = new Dictionary<(int, int), List<Vector2>>();
        (int, int) G(Vector2 p) => (Mathf.FloorToInt(p.x / spacing), Mathf.FloorToInt(p.y / spacing));
        for (int k = 0; k < tries; k++)
        {
            var q = new Vector2((float)rnd.NextDouble() * (W + 2 * pad) - pad, (float)rnd.NextDouble() * (H + 2 * pad) - pad);
            var (gx, gy) = G(q);
            bool clash = false;
            for (int a = -1; a <= 1 && !clash; a++)
                for (int b = -1; b <= 1 && !clash; b++)
                    if (grid.TryGetValue((gx + a, gy + b), out var l) && l.Any(p => (p - q).sqrMagnitude < spacing * spacing)) clash = true;
            if (clash || !where(q)) continue;
            o.Add(q);
            if (!grid.TryGetValue((gx, gy), out var cell)) grid[(gx, gy)] = cell = new List<Vector2>();
            cell.Add(q);
        }
        return o;
    }

    void Forest()
    {
        var f = L["forest"];
        if (f == null) return;
        float spacing = f["spacing"].Fq() ?? 3.4f, edge = f["edge"].Fq() ?? 0.97f;
        var trees = Weights(f["species"]);
        if (trees.Count == 0) return;
        float keepRoad = f["keepRoad"].Fq() ?? 2.5f, keepBuilt = f["keepBuilt"].Fq() ?? 4.5f;
        var spots = Darts(q => Clearing(q) > EdgeAt(q, edge) && Free(q, keepRoad, keepBuilt, margin: true) && !Shades(q), spacing, 90000, M);
        var glade = Glades(f["clumps"], spots);                          // KitVillage.ForestDress.cs: clumps, zones, lean, fallen
        float wallAt = f["wallAt"].Fq() ?? 1.08f;
        var near = new List<Vector2>();
        foreach (var q in spots)
        {
            float s = 0.85f + (float)rnd.NextDouble() * 0.35f;
            var (list, zone) = InZone(q, trees, "species");
            string piece = Pick(list);
            float deg = (float)rnd.NextDouble() * 360f;                   // drawn for a glade's spot too: the others stay put
            if (glade(q)) continue;
            near.Add(q);
            var go = Place(natureT, piece, q, deg, s);
            if (go == null) continue;
            Trunk(go);
            Fell(go, piece, q, s, Clearing(q) > wallAt + 0.04f);
            if (zone != null) Swap(go, zone);
        }
        var under = Weights(f["undergrowth"]);
        if (under.Count > 0)
        {
            float us = f["undergrowthSpacing"].Fq() ?? 2.6f;
            foreach (var q in Darts(q => Clearing(q) > EdgeAt(q, edge) - 0.08f && q.x > -4 && q.y > -4 && q.x < W + 4 && q.y < H + 4 && Free(q, 1.2f, 1.8f, margin: true) && !HidesFoot(q, 0.5f) && near.All(t => (t - q).sqrMagnitude > 1.2f), us, 30000, 4f))
            {
                var (list, zone) = InZone(q, under, "undergrowth");
                var go = Place(natureT, Pick(list), q, (float)rnd.NextDouble() * 360f, 0.8f + (float)rnd.NextDouble() * 0.4f);
                KitSolid.Nature(go, SceneOwner);
                if (go != null && zone != null) Swap(go, zone);
            }
        }
        // stragglers: single trees and pairs out in the clearing near its edge, so the forest frays instead of ending
        // on a line
        int strag = f["stragglers"].Iq() ?? 12;
        var lone = Darts(q => { float c = Clearing(q); return c > 0.72f && c < EdgeAt(q, edge) - 0.04f && Free(q, keepRoad + 1f, keepBuilt + 2f) && !Shades(q); }, 7f, 20000)
            .OrderBy(_ => rnd.Next()).Take(strag).ToList();
        foreach (var q in lone)
        {
            var (list, zone) = InZone(q, trees, "species");
            string piece = Pick(list);
            float deg = (float)rnd.NextDouble() * 360f, s = 0.8f + (float)rnd.NextDouble() * 0.35f;
            var go = Place(natureT, piece, q, deg, s);
            if (go != null)
            {
                Trunk(go);
                Fell(go, piece, q, s, false);                           // in the clearing: it may lean, never lie
                if (zone != null) Swap(go, zone);
            }
            occupied.Add((Corners(new Rect(-1.5f, -1.5f, 3f, 3f), q, 0), "straggler"));
        }
    }

    void Scatter()
    {
        foreach (var s in L["scatter"] as JsonArray ?? new JsonArray())
        {
            var ws = Weights(s["pieces"]);
            int count = s["count"].Iq() ?? 20;
            float keep = s["keep"].Fq() ?? 1.5f, spacing = s["spacing"].Fq() ?? 2.5f;
            var spots = Darts(q => Clearing(q) < 0.95f && Free(q, keep) && !HidesFoot(q, 0.5f), spacing, 20000).OrderBy(_ => rnd.Next()).Take(count);
            foreach (var q in spots)
            {
                var (list, zone) = InZone(q, ws, "scatter");                // a forest zone's own scatter (a burnt edge's stumps)
                var go = Place(natureT, Pick(list), q, (float)rnd.NextDouble() * 360f, 0.8f + (float)rnd.NextDouble() * 0.4f);
                KitSolid.Nature(go, SceneOwner);
                if (go != null && zone != null) Swap(go, zone);
            }
        }
    }

    /// <summary>points in the forest just beyond the clearing's wall, away from the roads (plan space): what a walk test
    /// checks cannot be reached. Reads the layout, so it works on a map loaded from its scene.</summary>
    public List<Vector2> ForestProbes(int count = 24)
    {
        var lay = KitJson.ParseObject(layout);
        var size = lay["size"] as JsonArray;
        float w = size != null ? size[0].F() : 100f, h = size != null ? size[1].F() : 100f;
        var cs = Clearings(lay, w, h);
        float wallAt = lay["forest"]?["wallAt"].Fq() ?? 1.08f;
        var rds = (lay["roads"] as JsonArray ?? new JsonArray()).Select(x => (Spline(x["points"].AsArray().Select(V).ToList()), x["width"].Fq() ?? 3f)).ToList();
        var o = new List<Vector2>();
        int per = Mathf.Max(4, count / cs.Count);
        foreach (var (c, r, lumps, seed) in cs)
        {
            int got = 0;
            for (int k = 0; k < per * 4 && got < per; k++)
            {
                float a = k / (float)(per * 4) * Mathf.PI * 2;
                var dir = new Vector2(Mathf.Cos(a), Mathf.Sin(a));
                float lo = 0, hi = Mathf.Max(w, h);
                for (int it = 0; it < 30; it++) { float mid = (lo + hi) / 2; if (Blob(c + dir * mid, c, r, lumps, seed) < wallAt) lo = mid; else hi = mid; }
                var q = c + dir * (lo + 3f);                                 // 3 m past the wall's line: beyond its band
                if (q.x < 2 || q.y < 2 || q.x > w - 2 || q.y > h - 2) continue;
                if (Union(q, cs) < wallAt) continue;                          // inside another glade
                if (rds.Any(rd => DistToPolyline(q, rd.Item1) < rd.Item2 / 2 + 6f)) continue;
                if (o.Count > 0 && (o[o.Count - 1] - q).magnitude < 6f) continue;
                o.Add(q); got++;
            }
        }
        return o;
    }

    // ------------------------------------------------------------------ spawns, markers, exits, walls
    void SpawnAt(string id, Vector2 at, float bearing)
    {
        var sp = new KitSpawn { Name = "SPN_" + id, SpawnId = id, FacingDeg = bearing, Kind = KitMarker.MarkerKind.Spawn };
        logicT.AddChild(sp, true);
        sp.Owner = SceneOwner;
        sp.Transform = new Transform3D(KitSpawn.FromBearing(bearing), Local(at.x, at.y, Height(at)));
    }

    /// <summary>ways in and out that are no building's door (layout "links": [{id, at, target, arrive, prompt, size: [w, h,
    /// d], rot, kind, walkInto, facingMin, spawn: {at, facing}}]; a game's well shaft and burrow hole): a trigger box
    /// standing on the ground at the spot (its size, 1.6 x 2.2 x 1.6 by default; turned by "rot" as a prop is), a KitLink
    /// LNK_id on it (KitLink's own defaults where a key is left out) and, with "spawn", where one coming back through it
    /// stands (SPN_id, its facing a bearing)</summary>
    void Links()
    {
        foreach (var k in L["links"] as JsonArray ?? new JsonArray())
        {
            string id = k["id"].S();
            if (string.IsNullOrEmpty(id) || k["at"] == null) { notes.Add("a link with no id or no spot"); continue; }
            var at = V(k["at"]);
            var size = k["size"] as JsonArray;
            var sz = size != null && size.Count >= 3 ? new Godot.Vector3(size[0].F(), size[1].F(), size[2].F()) : new Godot.Vector3(1.6f, 2.2f, 1.6f);
            var lk = LinkAt("LNK_" + id, at, Height(at), k["rot"].Fq() ?? 0f, sz, new Godot.Vector3(0f, sz.Y / 2f, 0f));
            lk.LinkId = id; lk.Target = k["target"].S() ?? ""; lk.Arrive = k["arrive"].S() ?? "";
            if (k["kind"] != null) lk.Kind = k["kind"].S();
            if (k["prompt"] != null) lk.Prompt = k["prompt"].S();
            if (k["walkInto"] != null) lk.WalkInto = k["walkInto"].B();
            if (k["facingMin"] != null) lk.FacingMin = k["facingMin"].F();
            if (string.IsNullOrEmpty(lk.Target)) notes.Add($"link {id}: no target");
            if (k["spawn"] is JsonObject sp && sp["at"] != null) SpawnAt(id, V(sp["at"]), sp["facing"].Fq() ?? 0f);
        }
    }

    void Markers()
    {
        foreach (var s in L["spawns"] as JsonArray ?? new JsonArray())
            SpawnAt(s["id"].S(), V(s["at"]), s["facing"].Fq() ?? 0f);
        foreach (var m in L["markers"] as JsonArray ?? new JsonArray())
        {
            var at = V(m["at"]);
            float facing = m["facing"].Fq() ?? 0f;
            var mk = new KitMarker { Name = $"MRK_{m["role"].S()}_{m["id"].S()}", Kind = KitMarker.MarkerKind.Other };
            mk.Props = new Godot.Collections.Dictionary<string, string>
            {
                ["vki_role"] = m["role"].S() ?? "", ["vki_marker_id"] = m["id"].S() ?? "",
                ["vki_facing_deg"] = facing.ToString(CultureInfo.InvariantCulture),
            };
            if (m["note"] != null) mk.Props["vki_note"] = m["note"].S();
            logicT.AddChild(mk, true);
            mk.Owner = SceneOwner;
            mk.Transform = new Transform3D(KitSpawn.FromBearing(facing), Local(at.x, at.y, Height(at)));
        }
    }

    /// <summary>encounters ([{id, creature, budget, boss, points: [[x, y, h], ...], note}]): a KitEncounter each with its
    /// spawn points as children; `h` lifts a point off the ground (archers on a walkway)</summary>
    void Encounters()
    {
        foreach (var e in L["encounters"] as JsonArray ?? new JsonArray())
        {
            var pts = (e["points"] as JsonArray ?? new JsonArray()).Select(p => (q: new Vector2(p[0].F(), p[1].F()), h: p.Len() > 2 ? p[2].F() : 0f)).ToList();
            if (pts.Count == 0) continue;
            var c = new Vector2(pts.Average(p => p.q.x), pts.Average(p => p.q.y));
            string id = e["id"].S() ?? "encounter";
            float x0 = pts.Min(p => p.q.x) - 2, x1 = pts.Max(p => p.q.x) + 2, y0 = pts.Min(p => p.q.y) - 2, y1 = pts.Max(p => p.q.y) + 2;
            var en = new KitEncounter
            {
                Name = "ENC_" + id, EncounterId = id, RoomType = e["room"].S() ?? "outdoors", Creature = e["creature"].S() ?? "",
                Budget = e["budget"].Iq() ?? pts.Count, Boss = e["boss"].Bq() ?? false, Depth = e["depth"].Iq() ?? 0,
                Size = new Godot.Vector3(x1 - x0, 3f, y1 - y0),
            };
            logicT.AddChild(en, true);
            en.Owner = SceneOwner;
            en.Position = Local(c.x, c.y, Height(c));
            for (int k = 0; k < pts.Count; k++)
            {
                var sp = new Node3D { Name = $"Spawn_{k}" };
                en.AddChild(sp);
                sp.Owner = SceneOwner;
                sp.Position = Local(pts[k].q.x, pts[k].q.y, Height(pts[k].q) + pts[k].h) - en.Position;
            }
        }
    }

    void Exits()
    {
        foreach (var e in L["exits"] as JsonArray ?? new JsonArray())
        {
            var rd = roads.FirstOrDefault(r => r.id == e["road"].S());
            if (rd.pts == null) { notes.Add($"exit {e["id"].S()}: no road {e["road"].S()}"); continue; }
            bool atStart = e["end"].S() == "start";
            Vector2 tip = atStart ? rd.pts[0] : rd.pts[rd.pts.Length - 1], back = atStart ? rd.pts[Mathf.Min(4, rd.pts.Length - 1)] : rd.pts[Mathf.Max(0, rd.pts.Length - 5)];
            var inward = (back - tip).normalized;
            // the end of the road inside the map
            var edgeAt = tip;
            for (int k = 0; k < 40 && (edgeAt.x < 1 || edgeAt.y < 1 || edgeAt.x > W - 1 || edgeAt.y > H - 1); k++) edgeAt += inward;
            string id = e["id"].S();
            var at = edgeAt + inward * 1.5f;
            var lk = LinkAt("LNK_" + id, at, Height(at), Ang(-inward) - 90f, new Godot.Vector3(rd.width + 1f, 2.4f, 2f), new Godot.Vector3(0, 1.2f, 0));
            lk.LinkId = id; lk.Kind = "exit"; lk.Target = e["target"].S() ?? "@deep"; lk.Prompt = e["prompt"].S() ?? "Leave"; lk.FacingMin = 0f;
            lk.WalkInto = true;                                // the road runs on: walk on to take it
            lk.Arrive = e["arrive"].S() ?? "";                 // the spawn on the map beyond (its exit back, usually)
            SpawnAt(id, edgeAt + inward * 5f, Bearing(inward));
        }
    }

    /// <summary>invisible walls: the outline of the walkable ground (inside the clearings up to `wallAt`, a little inside
    /// the forest, and along every road), found on a one-metre grid and walled with boxes a cell thick, so junctions of
    /// roads and glades of any shape close; plus the map's border (a road's end is an exit one uses, not a way off)</summary>
    void Walls()
    {
        var body = new StaticBody3D { Name = "WallBodies", CollisionLayer = KitPiece.Solid };
        wallT.AddChild(body);
        body.Owner = SceneOwner;
        void Wall(Vector2 a, Vector2 b, string n, float thick = 0.6f)
        {
            var mid = (a + b) / 2;
            var c = new CollisionShape3D
            {
                Name = n, Shape = new BoxShape3D { Size = new Godot.Vector3((b - a).magnitude + 0.3f, 4f, thick) },
                Transform = new Transform3D(Turn(Ang(b - a)), Local(mid.x, mid.y, Height(mid) + 2f)),
            };
            body.AddChild(c, true);
            c.Owner = SceneOwner;
        }
        const float cell = 1f;
        var walk = WalkGrid(L, W, H);
        int nx = walk.GetLength(0), ny = walk.GetLength(1);
        bool Edge(int i, int j)        // forest beside walkable ground (eight neighbours: no corner slips through)
        {
            if (walk[i, j]) return false;
            for (int a = -1; a <= 1; a++)
                for (int b = -1; b <= 1; b++)
                {
                    int x = i + a, y = j + b;
                    if (x >= 0 && y >= 0 && x < nx && y < ny && walk[x, y]) return true;
                }
            return false;
        }
        int made = 0;
        for (int j = 0; j < ny; j++)
            for (int i = 0; i < nx;)
            {
                if (!Edge(i, j)) { i++; continue; }
                int i1 = i;
                while (i1 + 1 < nx && i1 + 1 - i < 8 && Edge(i1 + 1, j)) i1++;      // runs of up to 8 m keep each box near the ground
                float y = (j + 0.5f) * cell;
                Wall(new Vector2(i * cell, y), new Vector2((i1 + 1) * cell, y), $"Wall_{made++}", cell);
                i = i1 + 1;
            }
        // the border, except where an exit's road leaves the map
        var corners = new[] { new Vector2(0, 0), new Vector2(W, 0), new Vector2(W, H), new Vector2(0, H) };
        for (int s = 0; s < 4; s++)
        {
            Vector2 a = corners[s], b = corners[(s + 1) % 4];
            int n = Mathf.CeilToInt((b - a).magnitude / 4f);
            for (int k = 0; k < n; k++)
            {
                Vector2 p0 = Vector2.Lerp(a, b, k / (float)n), p1 = Vector2.Lerp(a, b, (k + 1) / (float)n);
                Wall(p0, p1, "Border");
            }
        }
    }

    /// <summary>the walkable ground on a one-metre grid (cell (i, j) centred on (i + 0.5, j + 0.5) in plan metres): inside
    /// the clearings up to the forest's `wallAt`, and a band along every road. Walls() walls its outline; the bake leaves
    /// out the rest (<see cref="Outside"/>)</summary>
    static bool[,] WalkGrid(JsonObject lay, float w, float h)
    {
        float ring = lay["forest"]?["wallAt"].Fq() ?? 1.08f;
        var cs = Clearings(lay, w, h);
        var rds = (lay["roads"] as JsonArray ?? new JsonArray()).Select(r => (pts: Spline(r["points"].AsArray().Select(V).ToList()), width: r["width"].Fq() ?? 3f)).ToList();
        int nx = Mathf.CeilToInt(w), ny = Mathf.CeilToInt(h);
        var walk = new bool[nx, ny];
        for (int i = 0; i < nx; i++)
            for (int j = 0; j < ny; j++)
            {
                var q = new Vector2(i + 0.5f, j + 0.5f);
                walk[i, j] = Union(q, cs) < ring || rds.Any(r => DistToPolyline(q, r.pts) < r.width / 2 + 1.0f);
            }
        return walk;
    }

    /// <summary>the ground beyond the walls, in plan rectangles (x, y, w, h), for the bake to leave out (KitNavMesh's
    /// obstructions): the one-metre cells off the walkable grid -- the walls' own cells too, so nothing is left on their
    /// tops -- in runs along each row, joined north while a row repeats them; and the forest drawn round the map. Without
    /// it the forest carried a navmesh of its own, bigger than the map's, for a spawn point by the wall to snap to (cut
    /// off from the clearing) and a wander or a click to land on. Reads the layout, so it works on a map loaded from its
    /// scene.</summary>
    public List<Rect> Outside()
    {
        var lay = KitJson.ParseObject(layout);
        var size = lay["size"] as JsonArray;
        float w = size != null ? size[0].F() : 100f, h = size != null ? size[1].F() : 100f;
        float m = (lay["margin"].Fq() ?? 24f) + 8f;
        var walk = WalkGrid(lay, w, h);
        int nx = walk.GetLength(0), ny = walk.GetLength(1);
        var o = new List<Rect>();
        var open = new Dictionary<(int, int), Rect>();        // the runs still growing north, by their first and last cell
        for (int j = 0; j <= ny; j++)
        {
            var next = new Dictionary<(int, int), Rect>();
            for (int i = 0; j < ny && i < nx;)
            {
                if (walk[i, j]) { i++; continue; }
                int i1 = i;
                while (i1 + 1 < nx && !walk[i1 + 1, j]) i1++;
                next[(i, i1)] = open.TryGetValue((i, i1), out var r) ? new Rect(r.x, r.y, r.width, r.height + 1) : new Rect(i, j, i1 - i + 1, 1);
                open.Remove((i, i1));
                i = i1 + 1;
            }
            o.AddRange(open.Values);
            open = next;
        }
        o.Add(new Rect(-m, -m, w + 2 * m, m));                  // the forest round the map: south, north, west, east
        o.Add(new Rect(-m, h, w + 2 * m, m));
        o.Add(new Rect(-m, 0, m, h));
        o.Add(new Rect(w, 0, m, h));
        return o;
    }
}
