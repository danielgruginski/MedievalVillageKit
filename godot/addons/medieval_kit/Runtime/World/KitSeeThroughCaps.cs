using System.Collections.Generic;
using Godot;

namespace MedievalKit;

/// <summary>
/// Real caps for the see-through: Unity's KitSeeThroughCaps (read its notes for the why). The hole stays for what covers
/// the walker (roofs, upper floors, canopies); what stands on the ground is cut with a proper finish. Each piece is cut at
/// <see cref="Height"/> over its base (a building's floor): the shader removes what is above inside the hole, and a cap --
/// the piece's own cross-section at the cut, filled -- closes the stub, drawn only where the hole opened it
/// (kit_see_through.gdshaderinc, <see cref="KitSeeThrough.CapBit"/>). The kit's solid pieces are closed, so their sections
/// are closed loops; sheets (leaf cards, a door leaf, a window pane) get no cap.
/// <para>The cut is kept in the piece's marks (<see cref="KitSeeThrough.WithCut"/>: an offset over its own origin in
/// <see cref="Step"/> steps), so the shader cuts exactly where the cap lies. A cap mesh is made per mesh, cut and set of
/// solid materials, so the instances of a piece share one; they come baked (<see cref="KitSeeThroughCapBank"/>,
/// `kit_cli -- bakecaps`), and what the bank lacks is made in play, a few milliseconds a frame (<see cref="Flush"/>: Godot
/// reads a mesh back from the GPU). A cut piece has no cap node of its own: it is registered, and a pool of
/// <see cref="PoolSize"/> mesh instances is laid each frame over the registered pieces in the hole's reach (the cone from
/// the camera to the walker), the nearest to the walker first (<see cref="LayPool"/>, from KitCamera).</para>
/// <para>Caps that overlap are stacked by area, larger below: inside a cap mesh each outline lies <see cref="Layer"/>
/// above the larger ones it overlaps, and in a building each piece's cap <see cref="RankStride"/> layers above the larger
/// caps it overlaps (<see cref="Settle"/>). A section's loops are told outer from hole by the faces' own direction; bark
/// caps take the kit's end grain, its rings centred on each cut. Not yet here: a house's floor over its walls' box (Unity's
/// Floor: it needs phase 5's KitVillage and its box per house). FULL_PORT_PLAN phase 6.</para>
/// </summary>
public static class KitSeeThroughCaps
{
    /// <summary>the cut over each piece's base (m): the camera's KeepBelow</summary>
    public const float Height = 1.4f;
    /// <summary>the cut's offset is kept in the marks in these steps (local units)</summary>
    public const float Step = KitSeeThrough.CutStep;
    const float Weld = 1e-3f;               // section points closer than this are one
    const float Tile = 0.5f;                // the cap's texture: tiles per (local) metre
    /// <summary>one step of the caps' stacking (m): an outline over the larger ones it overlaps in its own cap</summary>
    public const float Layer = 0.0005f;
    /// <summary>a piece's cap over the larger caps of its building it overlaps: this many layers (a cap holds up to 7)</summary>
    public const int RankStride = 8;
    /// <summary>cap mesh instances in the pool: the caps drawn at once, the pieces nearest the walker in the hole's cone first</summary>
    public const int PoolSize = 96;
    /// <summary>milliseconds a frame for making the caps the bank lacks</summary>
    public static float FlushMs = 4f;
    /// <summary>off: the pool draws nothing (the cuts stay; the back faces' cap pass is all there is)</summary>
    public static bool Enabled = true;

    /// <summary>a cut piece and its cap (shared by the instances of its mesh, cut and solid materials)</summary>
    public sealed class Piece
    {
        public MeshInstance3D G;
        public Mesh Cap;
        public Material[] Mats;
        /// <summary>the cap's area (world, m²) and its height over the cut (world m: under it, stacked by area)</summary>
        public float Area, Offset = -0.001f;
        public KitSeeThrough.Building Building;
        internal Vector3 At, Centre;
        internal float Radius;
    }

    /// <summary>a cap mesh (null: the section filled nothing), each surface's source surface, which take the end grain, its area</summary>
    public sealed class CapData
    {
        public ArrayMesh Mesh;
        public int[] Mats;
        public bool[] Grain;
        public float Area;
    }

    static readonly Dictionary<(Mesh, int, uint, uint), CapData> cache = new();
    static readonly Queue<(MeshInstance3D g, Mesh mesh, int q, uint solid, uint bark, KitSeeThrough.Building b)> pending = new();
    static readonly List<Piece> pieces = new();
    static readonly Dictionary<KitSeeThrough.Building, List<Piece>> byBuilding = new();
    static readonly HashSet<KitSeeThrough.Building> unranked = new();
    static Dictionary<(string, int, uint, uint), KitSeeThroughCapEntry> banked;
    static Material endGrain;
    static bool endGrainRead;

    /// <summary>while set (the bake), <see cref="Cut"/> only collects each piece's cap key here: nothing is queued or registered</summary>
    public static HashSet<(Mesh mesh, string source, int q, uint solid, uint bark)> Collecting;

    /// <summary>caps still to make</summary>
    public static int Pending => pending.Count;
    /// <summary>pieces registered with a cap; cap meshes made in play; polygons that could not be filled; caps taken from
    /// the bank; bank entries ignored (their mesh changed)</summary>
    public static int Registered, Made, Failed, Baked, Stale;
    /// <summary>the pieces registered with a cap (the checks)</summary>
    public static IReadOnlyList<Piece> Pieces => pieces;
    /// <summary>caps the pool drew in its last frame</summary>
    public static int Shown { get; private set; }

    // ------------------------------------------------------------------ the bank

    /// <summary>the baked caps by source, cut and surfaces (loaded once; none: everything is made in play)</summary>
    static Dictionary<(string, int, uint, uint), KitSeeThroughCapEntry> Bank
    {
        get
        {
            if (banked != null) return banked;
            banked = new();
            if (!ResourceLoader.Exists(KitSeeThroughCapBank.Path)) return banked;
            var bank = GD.Load<KitSeeThroughCapBank>(KitSeeThroughCapBank.Path);
            if (bank != null)
                foreach (var e in bank.Entries)
                    if (e != null) banked[(e.Source, e.Q, (uint)e.Solid, (uint)e.Bark)] = e;
            return banked;
        }
    }

    /// <summary>forget the bank (it was baked again) and every cap made from it</summary>
    public static void ResetBank() { banked = null; cache.Clear(); Baked = 0; Stale = 0; }

    /// <summary>a mesh's name for the bank: its piece's (the KitPiece it stands in) and its own</summary>
    public static string SourceOf(Node g, Mesh mesh)
    {
        string own = !string.IsNullOrEmpty(mesh.ResourceName) ? mesh.ResourceName : g.Name.ToString();
        for (var n = g; n != null; n = n.GetParent())
            if (n is KitPiece kp) return kp.Piece + "/" + own;
        return mesh.ResourcePath != "" ? mesh.ResourcePath : own;
    }

    /// <summary>a mesh's vertices (every surface): with its bounds, what tells a re-exported mesh from the one baked</summary>
    public static int VertexCount(Mesh mesh)
    {
        if (mesh is not ArrayMesh am) return 0;
        int n = 0;
        for (int s = 0; s < am.GetSurfaceCount(); s++) n += am.SurfaceGetArrayLen(s);
        return n;
    }

    static bool FromBank(MeshInstance3D g, (Mesh mesh, int q, uint solid, uint bark) key, out CapData cap)
    {
        cap = null;
        if (!Bank.TryGetValue((SourceOf(g, key.mesh), key.q, key.solid, key.bark), out var e)) return false;
        var b = key.mesh.GetAabb();
        if (e.VertexCount != VertexCount(key.mesh) || (e.Bounds.Position - b.Position).LengthSquared() > 1e-8f || (e.Bounds.Size - b.Size).LengthSquared() > 1e-8f)
        {
            Stale++;
            return false;
        }
        cache[key] = cap = new CapData { Mesh = e.Cap, Mats = e.Mats, Grain = e.Grain, Area = e.Area };
        Baked++;
        return true;
    }

    // ------------------------------------------------------------------ cutting

    /// <summary>a one-sided solid kit material: its back faces get a cap pass (gdx_export gives it KitLitCap as next_pass)</summary>
    static bool Solid(Material m) =>
        m is ShaderMaterial { NextPass: ShaderMaterial { Shader: { } s } } && s.ResourcePath == KitPaths.Shaders + "KitLitCap.gdshader";

    static bool Bark(Material m) => m != null && m.ResourcePath.GetFile().StartsWith("M_VK_Bark");

    static Material EndGrain
    {
        get
        {
            if (!endGrainRead)
            {
                endGrainRead = true;
                string p = KitPaths.Materials + "M_VK_EndGrain.tres";
                endGrain = ResourceLoader.Exists(p) ? GD.Load<Material>(p) : null;
            }
            return endGrain;
        }
    }

    /// <summary>the piece's cut at baseY + <see cref="Height"/> (world), kept in its marks; where it spans the cut, it is
    /// registered with its cap -- baked, made before, or queued to be made -- and a building's caps open with it</summary>
    public static void Cut(GeometryInstance3D g, float baseY, KitSeeThrough.Building b = null)
    {
        var t = g.GlobalTransform;
        float sy = t.Basis.Y.Y;
        if (sy < 1e-4f) return;
        int q = Mathf.Clamp(Mathf.RoundToInt((baseY + Height - t.Origin.Y) / sy / Step), -512, 511);
        KitSeeThrough.SetLayers(g, KitSeeThrough.WithCut(KitSeeThrough.Layers(g), q));
        if (g is not MeshInstance3D mi || mi.Mesh == null) return;
        var mesh = mi.Mesh;
        if (t.Basis.Y.Normalized().AngleTo(Vector3.Up) > Mathf.DegToRad(1f)) return;   // tilted: the cut would not lie level in its space
        float y = q * Step;
        var bb = mesh.GetAabb();
        if (y <= bb.Position.Y + 1e-3f || y >= bb.End.Y - 1e-3f) return;
        uint solid = 0, bark = 0;
        for (int s = 0; s < mesh.GetSurfaceCount() && s < 32; s++)
        {
            var m = mi.GetActiveMaterial(s);
            if (Solid(m)) { solid |= 1u << s; if (Bark(m)) bark |= 1u << s; }
        }
        if (solid == 0) return;
        if (Collecting != null) { Collecting.Add((mesh, SourceOf(mi, mesh), q, solid, bark)); return; }
        var key = (mesh, q, solid, bark);
        if (cache.TryGetValue(key, out var cap) || FromBank(mi, key, out cap))
        {
            if (cap.Mesh != null) Register(mi, cap, b);
            return;
        }
        pending.Enqueue((mi, mesh, q, solid, bark, b));
    }

    /// <summary>make queued caps for up to `budgetMs` of this frame; returns how many are left</summary>
    public static int Flush(float budgetMs)
    {
        if (pending.Count == 0) return 0;
        ulong start = Time.GetTicksUsec();
        int made0 = Made;
        while (pending.Count > 0 && (Time.GetTicksUsec() - start) / 1000f < budgetMs)
        {
            var (g, mesh, q, solid, bark, b) = pending.Dequeue();
            if (!GodotObject.IsInstanceValid(g)) continue;
            var key = (mesh, q, solid, bark);
            if (!cache.TryGetValue(key, out var cap)) cache[key] = cap = MakeCap(mesh, q, solid, bark);
            if (cap.Mesh != null) Register(g, cap, b);
        }
        if (pending.Count == 0)
        {
            Settle();
            GD.Print($"[KitSeeThroughCaps] {Registered} caps registered ({Made} cap meshes made in play, {Failed} polygons not " +
                     $"filled; {Baked} from the bank, {Stale} stale): bake them (kit_cli -- bakecaps) to skip this");
        }
        return pending.Count;
    }

    static void Register(MeshInstance3D g, CapData cap, KitSeeThrough.Building b)
    {
        var cm = new Material[cap.Mats.Length];
        for (int i = 0; i < cm.Length; i++)
            cm[i] = cap.Grain[i] && EndGrain != null ? EndGrain : g.GetActiveMaterial(cap.Mats[i]);
        var t = g.GlobalTransform;
        var p = new Piece { G = g, Cap = cap.Mesh, Mats = cm, Area = cap.Area * Mathf.Abs(t.Basis.X.Length() * t.Basis.Z.Length()), Building = b };
        Measure(p);
        pieces.Add(p);
        Registered++;
        if (b != null)
        {
            if (!byBuilding.TryGetValue(b, out var l)) byBuilding[b] = l = new List<Piece>();
            l.Add(p);
            unranked.Add(b);
        }
    }

    static void Measure(Piece p)
    {
        p.At = p.G.GlobalPosition;
        var wb = KitSeeThrough.WorldAabb(p.G);
        p.Centre = wb.GetCenter();
        p.Radius = wb.Size.Length() * 0.5f;
    }

    /// <summary>stack the caps of the buildings that got new ones (larger below; each over the larger caps it overlaps in
    /// the same cut plane by <see cref="RankStride"/> layers): when a level's cuts are set, and when the caps the bank
    /// lacked are made</summary>
    public static void Settle()
    {
        foreach (var b in unranked) if (byBuilding.TryGetValue(b, out var l)) Rank(l);
        unranked.Clear();
    }

    static void Rank(List<Piece> caps)
    {
        caps.Sort((a, b) => b.Area.CompareTo(a.Area));
        var rank = new int[caps.Count];
        var foot = new Aabb[caps.Count];
        for (int i = 0; i < caps.Count; i++)
        {
            var p = caps[i];
            if (!GodotObject.IsInstanceValid(p.G)) continue;
            foot[i] = (p.G.GlobalTransform * p.Cap.GetAabb()).Grow(0.01f);
            int r = 0;
            for (int j = 0; j < i; j++)
                if (GodotObject.IsInstanceValid(caps[j].G) && Mathf.Abs(foot[j].GetCenter().Y - foot[i].GetCenter().Y) < 0.02f && foot[j].Intersects(foot[i]))
                    r = Mathf.Max(r, rank[j] + 1);
            rank[i] = Mathf.Min(r, 15);
            p.Offset = -0.001f + rank[i] * RankStride * Layer;
        }
    }

    // ------------------------------------------------------------------ the pool

    static readonly List<MeshInstance3D> pool = new();
    static readonly Piece[] shown = new Piece[PoolSize];
    static readonly List<(float d, Piece p)> near = new();
    static Node3D poolRoot;
    static ulong poolFrame = ulong.MaxValue;
    static readonly StringName RandomParam = "object_random";

    /// <summary>the pool's caps over the registered pieces the hole can reach this frame: those whose bounds meet the cone
    /// from the camera to the walker (the hole's radius there), the nearest to the walker first; the shader draws each
    /// only where the hole opened its piece. Nothing while the hole is shut. The kit's camera calls it each frame after
    /// setting the globals; it also makes a few of the caps the bank lacked (<see cref="Flush"/>).</summary>
    public static void LayPool(Camera3D cam)
    {
        ulong frame = Engine.GetProcessFrames();
        if (poolFrame == frame) return;
        poolFrame = frame;
        if (pending.Count > 0) Flush(FlushMs);
        var see = KitSeeThrough.Hole;
        near.Clear();
        if (see.W > 0f && pieces.Count > 0)
        {
            Vector3 eye = cam.GlobalPosition, walker = new Vector3(see.X, see.Y, see.Z);
            var d = walker - eye;
            float L = d.Length();
            if (L > 1e-3f)
            {
                d /= L;
                bool audit = frame % 60 == 0;                                   // (pieces freed, or moved)
                for (int i = pieces.Count - 1; i >= 0; i--)
                {
                    var p = pieces[i];
                    if (!GodotObject.IsInstanceValid(p.G)) { pieces.RemoveAt(i); continue; }
                    if (!p.G.IsInsideTree()) continue;                          // a level held out of the tree
                    if (audit && p.G.GlobalPosition != p.At) Measure(p);
                    var v = p.Centre - eye;
                    float t = v.Dot(d);
                    if (t < -p.Radius || t > L + p.Radius) continue;
                    float tc = Mathf.Clamp(t, 0f, L), reach = see.W * tc / L + p.Radius + 0.25f;
                    if ((v - d * tc).LengthSquared() > reach * reach) continue;
                    if (!p.G.IsVisibleInTree()) continue;
                    near.Add(((p.Centre - walker).LengthSquared(), p));
                }
                near.Sort((a, b) => a.d.CompareTo(b.d));
            }
        }
        int n = Enabled ? Mathf.Min(near.Count, PoolSize) : 0;
        if (n > 0 && (pool.Count == 0 || !GodotObject.IsInstanceValid(poolRoot))) MakePool(cam);
        for (int i = 0; i < pool.Count; i++)
        {
            var ci = pool[i];
            if (i >= n) { if (ci.Visible) ci.Visible = false; shown[i] = null; continue; }
            var p = near[i].p;
            var t = p.G.GlobalTransform;
            ci.GlobalTransform = new Transform3D(t.Basis, t.Origin + t.Basis.Y.Normalized() * p.Offset);
            if (shown[i] != p)
            {
                shown[i] = p;
                ci.Mesh = p.Cap;
                for (int s = 0; s < p.Cap.GetSurfaceCount() && s < p.Mats.Length; s++) ci.SetSurfaceOverrideMaterial(s, p.Mats[s]);
                ci.Layers = p.G.Layers;
                var rnd = p.G.GetInstanceShaderParameter(RandomParam);
                if (rnd.VariantType != Variant.Type.Nil) ci.SetInstanceShaderParameter(RandomParam, rnd);
            }
            KitSeeThrough.SetLayers(ci, KitSeeThrough.Layers(p.G) | KitSeeThrough.CapBit);   // its building open or not
            ci.SetInstanceShaderParameter(KitSeeThrough.BMinParam, p.G.GetInstanceShaderParameter(KitSeeThrough.BMinParam));
            ci.SetInstanceShaderParameter(KitSeeThrough.BMaxParam, p.G.GetInstanceShaderParameter(KitSeeThrough.BMaxParam));
            if (!ci.Visible) ci.Visible = true;
        }
        Shown = n;
    }

    static void MakePool(Camera3D cam)
    {
        pool.Clear();
        poolRoot = new Node3D { Name = "KitSeeThroughCaps" };
        cam.GetTree().Root.AddChild(poolRoot);
        for (int i = 0; i < PoolSize; i++)
        {
            var ci = new MeshInstance3D { Name = $"Cap{i}", CastShadow = GeometryInstance3D.ShadowCastingSetting.Off, Visible = false };
            poolRoot.AddChild(ci);
            pool.Add(ci);
            shown[i] = null;
        }
    }

    // ------------------------------------------------------------------ the section

    struct Seg { public Vector2 a, b, n; public int sub; }

    /// <summary>the mesh's solid surfaces cut at local y = q x <see cref="Step"/>, filled: a cap mesh (one surface per
    /// material that has a cap), the source surface of each, and which take the end grain (bark). The bake calls it.</summary>
    public static CapData MakeCap(Mesh mesh, int q, uint solid, uint bark)
    {
        float y = q * Step;
        var segs = new List<Seg>();
        try
        {
            for (int s = 0; s < mesh.GetSurfaceCount() && s < 32; s++)
            {
                if ((solid & (1u << s)) == 0) continue;
                using var arr = mesh.SurfaceGetArrays(s);                       // (disposed: see KitClickToMove.Cast)
                var v = arr[(int)Mesh.ArrayType.Vertex].AsVector3Array();
                var nv = arr[(int)Mesh.ArrayType.Normal];
                var nrm = nv.VariantType == Variant.Type.Nil ? null : nv.AsVector3Array();
                var iv = arr[(int)Mesh.ArrayType.Index];
                var tri = iv.VariantType == Variant.Type.Nil ? null : iv.AsInt32Array();
                int count = tri != null && tri.Length > 0 ? tri.Length : v.Length;
                for (int i = 0; i + 2 < count; i += 3)
                {
                    int i0 = tri != null && tri.Length > 0 ? tri[i] : i, i1 = tri != null && tri.Length > 0 ? tri[i + 1] : i + 1, i2 = tri != null && tri.Length > 0 ? tri[i + 2] : i + 2;
                    Vector3 p0 = v[i0], p1 = v[i1], p2 = v[i2];
                    float d0 = Side(p0.Y - y), d1 = Side(p1.Y - y), d2 = Side(p2.Y - y);
                    int n = 0; Vector2 a = default, b = default;
                    void Edge(Vector3 pa, float da, Vector3 pb, float db)
                    {
                        if ((da < 0) == (db < 0)) return;
                        var x = pa.Lerp(pb, da / (da - db));
                        if (n == 0) a = new Vector2(x.X, x.Z); else b = new Vector2(x.X, x.Z);
                        n++;
                    }
                    Edge(p0, d0, p1, d1); Edge(p1, d1, p2, d2); Edge(p2, d2, p0, d0);
                    // the face's outward side: the vertex normals' (Godot winds front faces clockwise in a right-handed
                    // space, so the cross product alone points in)
                    var fn = (p1 - p0).Cross(p2 - p0);
                    if (nrm != null && nrm.Length == v.Length) { if (fn.Dot(nrm[i0] + nrm[i1] + nrm[i2]) < 0f) fn = -fn; }
                    else fn = -fn;
                    if (n == 2 && (a - b).LengthSquared() > Weld * Weld) segs.Add(new Seg { a = a, b = b, n = new Vector2(fn.X, fn.Z), sub = s });
                }
            }
        }
        catch (System.Exception e) { GD.PushWarning($"[KitSeeThroughCaps] {mesh.ResourceName}: {e.Message}"); return new CapData(); }

        // closed loops per material first; what is left open (a solid whose faces change material round it) together
        var loopsBySub = new Dictionary<int, List<(List<Vector2>, bool)>>();
        var left = new List<Seg>();
        var bySub = new Dictionary<int, List<Seg>>();
        foreach (var sg in segs) { if (!bySub.TryGetValue(sg.sub, out var l)) bySub[sg.sub] = l = new List<Seg>(); l.Add(sg); }
        void Keep((List<Vector2> loop, int sub, bool solidIn) x)
        {
            if (!loopsBySub.TryGetValue(x.sub, out var l)) loopsBySub[x.sub] = l = new List<(List<Vector2>, bool)>();
            l.Add((x.loop, x.solidIn));
        }
        foreach (var kv in bySub) foreach (var x in Loops(kv.Value, left)) Keep(x);
        if (left.Count > 0) foreach (var x in Loops(new List<Seg>(left), null)) Keep(x);

        // every outline, filled; then stacked by area (larger below), each Layer over the larger ones it overlaps
        var polys = new List<(List<Vector2> poly, List<int> tri, Vector2 centre, float radius, int sub, Rect2 box, float area)>();
        foreach (var kv in loopsBySub)
            foreach (var (poly, centre, radius) in Polygons(kv.Value))
            {
                var t = new List<int>();
                if (!EarClip(poly, t)) { Failed++; continue; }
                float area = 0f;
                for (int i = 0; i + 2 < t.Count; i += 3) area += Mathf.Abs(Cross(poly[t[i]], poly[t[i + 1]], poly[t[i + 2]])) * 0.5f;
                Vector2 mn = poly[0], mx = poly[0];
                foreach (var p in poly) { mn = mn.Min(p); mx = mx.Max(p); }
                polys.Add((poly, t, centre, radius, kv.Key, new Rect2(mn, mx - mn), area));
            }
        polys.Sort((a, b) => b.area.CompareTo(a.area));
        var layer = new int[polys.Count];
        for (int i = 0; i < polys.Count; i++)
            for (int j = 0; j < i; j++)
                if (polys[j].box.Intersects(polys[i].box)) layer[i] = Mathf.Min(RankStride - 1, Mathf.Max(layer[i], layer[j] + 1));

        // one surface per source surface (Godot's surfaces keep their own vertices)
        var subs = new List<int>();
        var grains = new List<bool>();
        var verts = new List<List<Vector3>>();
        var uvs = new List<List<Vector2>>();
        var tris = new List<List<int>>();
        float total = 0f;
        for (int k = 0; k < polys.Count; k++)
        {
            var (poly, t, centre, radius, sub, _, area) = polys[k];
            int si = subs.IndexOf(sub);
            if (si < 0)
            {
                si = subs.Count; subs.Add(sub); grains.Add((bark & (1u << sub)) != 0);
                verts.Add(new List<Vector3>()); uvs.Add(new List<Vector2>()); tris.Add(new List<int>());
            }
            bool grain = grains[si];
            float py = y + layer[k] * Layer;
            int o = verts[si].Count;
            foreach (var p in poly)
            {
                verts[si].Add(new Vector3(p.X, py, p.Y));
                // end grain: the rings centred on this cut; anything else: its texture laid flat
                uvs[si].Add(grain ? new Vector2(0.5f, 0.5f) + (p - centre) / (2f * Mathf.Max(radius, 0.05f)) : p * Tile);
            }
            var idx = tris[si];
            for (int i = 0; i + 2 < t.Count; i += 3)
            {
                // facing up: Godot's front faces wind clockwise as seen, and seen from above (screen up = -z) a triangle
                // whose (x, z) cross product is positive turns clockwise
                if (Cross(poly[t[i]], poly[t[i + 1]], poly[t[i + 2]]) > 0) { idx.Add(o + t[i]); idx.Add(o + t[i + 1]); idx.Add(o + t[i + 2]); }
                else { idx.Add(o + t[i]); idx.Add(o + t[i + 2]); idx.Add(o + t[i + 1]); }
            }
            total += area;
        }
        if (subs.Count == 0) return new CapData();
        var m = new ArrayMesh { ResourceName = mesh.ResourceName + "_Cap" };
        for (int s = 0; s < subs.Count; s++)
        {
            int c = verts[s].Count;
            var nrm = new Vector3[c]; var tan = new float[c * 4]; var col = new Color[c];
            for (int i = 0; i < c; i++)
            {
                nrm[i] = Vector3.Up;
                tan[i * 4] = 1f; tan[i * 4 + 3] = 1f;
                col[i] = new Color(1f, 1f, 1f, 0f);           // no baked shading, no moss
            }
            using var arrays = new Godot.Collections.Array();
            arrays.Resize((int)Mesh.ArrayType.Max);
            arrays[(int)Mesh.ArrayType.Vertex] = verts[s].ToArray();
            arrays[(int)Mesh.ArrayType.Normal] = nrm;
            arrays[(int)Mesh.ArrayType.Tangent] = tan;
            arrays[(int)Mesh.ArrayType.Color] = col;
            arrays[(int)Mesh.ArrayType.TexUV] = uvs[s].ToArray();
            arrays[(int)Mesh.ArrayType.Index] = tris[s].ToArray();
            m.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        }
        Made++;
        return new CapData { Mesh = m, Mats = subs.ToArray(), Grain = grains.ToArray(), Area = total };
    }

    static float Side(float d) => Mathf.Abs(d) < 1e-6f ? 1e-6f : d;      // a vertex on the plane counts as above

    static long Key(Vector2 p) => ((long)Mathf.RoundToInt(p.X / Weld) << 32) ^ (Mathf.RoundToInt(p.Y / Weld) & 0xffffffffL);

    /// <summary>the closed loops the segments make (each with the surface most of its segments came from, and whether the
    /// solid lies inside it -- by the faces' own direction: an outer boundary's faces look out of it, a hole's into it);
    /// the segments of open or branching parts go to `left` (or are dropped when it is null)</summary>
    static IEnumerable<(List<Vector2>, int, bool)> Loops(List<Seg> segs, List<Seg> left)
    {
        var pos = new Dictionary<long, Vector2>();
        var adj = new Dictionary<long, List<(long to, int seg)>>();
        var seen = new HashSet<(long, long)>();
        for (int i = 0; i < segs.Count; i++)
        {
            long ka = Key(segs[i].a), kb = Key(segs[i].b);
            if (ka == kb) continue;
            var e = ka < kb ? (ka, kb) : (kb, ka);
            if (!seen.Add(e)) continue;                    // a face doubled: its section once
            pos[ka] = segs[i].a; pos[kb] = segs[i].b;
            if (!adj.TryGetValue(ka, out var la)) adj[ka] = la = new List<(long, int)>();
            if (!adj.TryGetValue(kb, out var lb)) adj[kb] = lb = new List<(long, int)>();
            la.Add((kb, i)); lb.Add((ka, i));
        }
        var done = new HashSet<long>();
        foreach (var start in adj.Keys)
        {
            if (done.Contains(start)) continue;
            var comp = new List<long>();
            var st = new Stack<long>(); st.Push(start); done.Add(start);
            bool ok = true;
            while (st.Count > 0)
            {
                var c = st.Pop(); comp.Add(c);
                if (adj[c].Count != 2) ok = false;
                foreach (var (to, _) in adj[c]) if (done.Add(to)) st.Push(to);
            }
            if (!ok)
            {
                if (left != null)
                {
                    var cs = new HashSet<long>(comp);
                    foreach (var c in comp) foreach (var (to, sg) in adj[c]) if (c < to && cs.Contains(to)) left.Add(segs[sg]);
                }
                continue;
            }
            var loop = new List<Vector2>();
            var steps = new List<(Vector2 d, Vector2 n)>();
            var votes = new Dictionary<int, int>();
            long prev = long.MinValue, cur = start;
            do
            {
                loop.Add(pos[cur]);
                var nb = adj[cur][0].to == prev ? adj[cur][1] : adj[cur][0];
                votes.TryGetValue(segs[nb.seg].sub, out int nv); votes[segs[nb.seg].sub] = nv + 1;
                steps.Add((pos[nb.to] - pos[cur], segs[nb.seg].n));
                prev = cur; cur = nb.to;
            } while (cur != start && loop.Count <= comp.Count);
            int sub = -1, best = -1;
            foreach (var kv in votes) if (kv.Value > best) { best = kv.Value; sub = kv.Key; }
            if (loop.Count < 3) continue;
            // walked counter-clockwise, the loop's region lies left of each step, its outside to the right
            bool ccw = Area(loop) > 0;
            float vote = 0;
            foreach (var (d, fn) in steps)
            {
                var outward = ccw ? new Vector2(d.Y, -d.X) : new Vector2(-d.Y, d.X);
                float ln = fn.Length();
                if (ln > 1e-12f) vote += (fn / ln).Dot(outward);
            }
            yield return (loop, sub, vote >= 0);
        }
    }

    // ------------------------------------------------------------------ filling

    static float Area(List<Vector2> p)
    {
        float a = 0;
        for (int i = 0, j = p.Count - 1; i < p.Count; j = i++) a += (p[j].X - p[i].X) * (p[j].Y + p[i].Y);
        return a * 0.5f;                                   // > 0: counter-clockwise (in x, z)
    }

    static List<Vector2> Clean(List<Vector2> p)
    {
        var q = new List<Vector2>(p);
        bool changed = true;
        while (changed && q.Count >= 3)
        {
            changed = false;
            for (int i = 0; i < q.Count && q.Count >= 3; i++)
            {
                Vector2 a = q[(i + q.Count - 1) % q.Count], b = q[i], c = q[(i + 1) % q.Count];
                float cr = (b.X - a.X) * (c.Y - b.Y) - (b.Y - a.Y) * (c.X - b.X);
                if ((b - a).LengthSquared() < Weld * Weld || Mathf.Abs(cr) < 1e-7f * Mathf.Max(1e-6f, (b - a).Length() * (c - b).Length()))
                { q.RemoveAt(i); i--; changed = true; }
            }
        }
        return q;
    }

    static bool Inside(Vector2 pt, List<Vector2> poly)
    {
        bool c = false;
        for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            if ((poly[i].Y > pt.Y) != (poly[j].Y > pt.Y) && pt.X < (poly[j].X - poly[i].X) * (pt.Y - poly[i].Y) / (poly[j].Y - poly[i].Y) + poly[i].X)
                c = !c;
        return c;
    }

    /// <summary>loops to fillable polygons: each outer loop (the solid inside it, counter-clockwise) with the holes
    /// directly inside it merged in; an outer loop inside another (a root inside a trunk, two pieces of one mesh) is
    /// filled on its own, not cut out. Also the outer loop's centre and reach (for the end grain).</summary>
    static IEnumerable<(List<Vector2>, Vector2, float)> Polygons(List<(List<Vector2> loop, bool solidIn)> raw)
    {
        var loops = new List<List<Vector2>>();
        var solidIn = new List<bool>();
        foreach (var (l, si) in raw) { var c = Clean(l); if (c.Count >= 3 && Mathf.Abs(Area(c)) > 1e-6f) { loops.Add(c); solidIn.Add(si); } }
        int n = loops.Count;
        var parent = new int[n];
        for (int i = 0; i < n; i++)
        {
            parent[i] = -1;
            if (solidIn[i]) continue;
            float best = float.MaxValue;
            for (int j = 0; j < n; j++)                                    // a hole goes to the smallest outer round it
                if (i != j && solidIn[j] && Inside(loops[i][0], loops[j]) && Mathf.Abs(Area(loops[j])) < best)
                { best = Mathf.Abs(Area(loops[j])); parent[i] = j; }
        }
        for (int i = 0; i < n; i++)
        {
            if (!solidIn[i]) continue;
            var outer = new List<Vector2>(loops[i]);
            if (Area(outer) < 0) outer.Reverse();
            var centre = Vector2.Zero;
            foreach (var p in outer) centre += p;
            centre /= outer.Count;
            float reach = 0f;
            foreach (var p in outer) reach = Mathf.Max(reach, (p - centre).Length());
            var holes = new List<List<Vector2>>();
            for (int j = 0; j < n; j++)
                if (parent[j] == i) { var h = new List<Vector2>(loops[j]); if (Area(h) > 0) h.Reverse(); holes.Add(h); }
            var merged = Merge(outer, holes);
            if (merged != null) yield return (merged, centre, reach); else Failed++;
        }
    }

    static float Cross(Vector2 a, Vector2 b, Vector2 c) => (b.X - a.X) * (c.Y - a.Y) - (b.Y - a.Y) * (c.X - a.X);

    static bool InTri(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
    {
        float d1 = Cross(a, b, p), d2 = Cross(b, c, p), d3 = Cross(c, a, p);
        bool neg = d1 < -1e-9f || d2 < -1e-9f || d3 < -1e-9f, pos = d1 > 1e-9f || d2 > 1e-9f || d3 > 1e-9f;
        return !(neg && pos);
    }

    /// <summary>the holes joined to the outer loop by bridges (Eberly): one simple polygon</summary>
    static List<Vector2> Merge(List<Vector2> outer, List<List<Vector2>> holes)
    {
        holes.Sort((h1, h2) => MaxX(h2).CompareTo(MaxX(h1)));
        var poly = outer;
        foreach (var h in holes)
        {
            int mi = 0;
            for (int i = 1; i < h.Count; i++) if (h[i].X > h[mi].X) mi = i;
            var M = h[mi];
            float bx = float.MaxValue; int be = -1;
            for (int i = 0; i < poly.Count; i++)
            {
                Vector2 a = poly[i], b = poly[(i + 1) % poly.Count];
                if ((a.Y > M.Y) == (b.Y > M.Y)) continue;
                float x = a.X + (M.Y - a.Y) * (b.X - a.X) / (b.Y - a.Y);
                if (x >= M.X && x < bx) { bx = x; be = i; }
            }
            if (be < 0) return null;
            int pi = poly[be].X > poly[(be + 1) % poly.Count].X ? be : (be + 1) % poly.Count;
            var I = new Vector2(bx, M.Y);
            Vector2 P = poly[pi];
            float bestCos = -2f;
            for (int k = 0; k < poly.Count; k++)
            {
                if (k == pi) continue;
                Vector2 pk = poly[k], pp = poly[(k + poly.Count - 1) % poly.Count], pn = poly[(k + 1) % poly.Count];
                if (Cross(pp, pk, pn) >= 0) continue;           // not reflex
                if (!InTri(pk, M, I, P)) continue;
                var dv = pk - M; float cos = dv.X / Mathf.Max(dv.Length(), 1e-9f);
                if (cos > bestCos) { bestCos = cos; pi = k; }
            }
            var np = new List<Vector2>(poly.Count + h.Count + 2);
            for (int i = 0; i <= pi; i++) np.Add(poly[i]);
            for (int i = 0; i <= h.Count; i++) np.Add(h[(mi + i) % h.Count]);
            np.Add(poly[pi]);
            for (int i = pi + 1; i < poly.Count; i++) np.Add(poly[i]);
            poly = np;
        }
        return poly;
    }

    static float MaxX(List<Vector2> p) { float m = float.MinValue; foreach (var v in p) m = Mathf.Max(m, v.X); return m; }

    /// <summary>a simple counter-clockwise polygon (bridged holes allowed) to triangles; false if it would not close</summary>
    static bool EarClip(List<Vector2> p, List<int> outTri)
    {
        var V = new List<int>(p.Count);
        for (int i = 0; i < p.Count; i++) V.Add(i);
        int guard = 0;
        while (V.Count > 3 && guard++ < 100000)
        {
            bool found = false;
            for (int i = 0; i < V.Count; i++)
            {
                int a = V[(i + V.Count - 1) % V.Count], b = V[i], c = V[(i + 1) % V.Count];
                if (Cross(p[a], p[b], p[c]) <= 1e-9f) continue;
                bool inside = false;
                for (int j = 0; j < V.Count && !inside; j++)
                {
                    int k = V[j];
                    if (k == a || k == b || k == c) continue;
                    var pk = p[k];
                    if (pk == p[a] || pk == p[b] || pk == p[c]) continue;   // a bridge's twin
                    if (InTri(pk, p[a], p[b], p[c])) inside = true;
                }
                if (inside) continue;
                outTri.Add(a); outTri.Add(b); outTri.Add(c);
                V.RemoveAt(i);
                found = true;
                break;
            }
            if (found) continue;
            // no ear: drop a flat (collinear) corner if there is one, else give up
            int flat = -1;
            for (int i = 0; i < V.Count; i++)
            {
                int a = V[(i + V.Count - 1) % V.Count], b = V[i], c = V[(i + 1) % V.Count];
                if (Mathf.Abs(Cross(p[a], p[b], p[c])) <= 1e-9f) { flat = i; break; }
            }
            if (flat < 0) return false;
            V.RemoveAt(flat);
        }
        if (V.Count == 3 && Cross(p[V[0]], p[V[1]], p[V[2]]) > 0) { outTri.Add(V[0]); outTri.Add(V[1]); outTri.Add(V[2]); }
        return outTri.Count > 0;
    }
}
