using System.Collections.Generic;
using Godot;

namespace MedievalKit;

/// <summary>
/// What the see-through (Shaders/kit_see_through.gdshaderinc) needs to know of a level's pieces: Unity's KitSeeThrough.cs
/// (read its notes for the why of each rule). Unity keeps the marks in each renderer's rendering layer mask and gives the
/// shader every renderer's bounds; Godot has neither, so both are instance uniforms on each GeometryInstance3D:
/// <c>kit_layers</c> (the same bits), <c>kit_bmin</c> / <c>kit_bmax</c> (its world bounds, <see cref="Bound"/>, set when a
/// level starts). The marks:
/// <list type="bullet">
/// <item><b>Loose pieces</b> (<see cref="Loose"/>: trees, bushes, rocks, props) open down to the walker's feet; the
/// nature is <b>round</b> too (in the way by the ellipsoid inside its bounds).</item>
/// <item><b>A building opens as one</b> (<see cref="Building"/>): its pieces carry <see cref="GroupBit"/> and its tag;
/// each frame (<see cref="DecideAll"/>, from <see cref="KitCamera"/>) it opens when its own surface hides the walker in
/// the hidden check's view (<see cref="KitSeeThroughProbe"/>), or without a check when its pieces' boxes cross the sight
/// lines (<see cref="Crosses"/>).</item>
/// <item><b>Walls placed as props</b> (<see cref="IsStanding"/>) open in runs (<see cref="Runs"/>).</item>
/// <item><b>Cuts and caps</b>: a piece's cut kept in its bits (<see cref="WithCut"/>).</item>
/// </list>
/// Unlike Unity, where KitVillage keeps its buildings and decides them, the buildings register here and the camera
/// decides them all (FULL_PORT_PLAN phase 6).
/// </summary>
public static class KitSeeThrough
{
    public const int LooseLayer = 16, RoundLayer = 17, GroupLayer = 18, OpenLayer = 19;
    public const uint LooseBit = 1u << LooseLayer, RoundBit = 1u << RoundLayer, GroupBit = 1u << GroupLayer, OpenBit = 1u << OpenLayer;
    public const int CapLayer = 20, CutLayer = 21;
    public const uint CapBit = 1u << CapLayer, CutBit = 1u << CutLayer, CutMask = 0x3FFu << 22;
    /// <summary>never cut: what a character carries (a weapon, a shield, a held prop) when drawn with kit materials</summary>
    public const int KeepLayer = 15;
    public const uint KeepBit = 1u << KeepLayer;
    public const int TagShift = 8, MaxTag = 100;
    public const uint TagMask = 0x7Fu << TagShift;
    /// <summary>a piece's cut never lies under the walker's feet + this (m)</summary>
    public const float AboveFeet = 0.05f;
    /// <summary>the cut's offset step (m, local units): KitSeeThroughCaps.Step in Unity</summary>
    public const float CutStep = 0.05f;
    /// <summary>the hidden check's camera has this bit in its cull mask (over the 20 visual layers; the shader's
    /// KIT_PROBE_CAMERA)</summary>
    public const uint ProbeCameraBit = 1u << 20;

    public static readonly StringName LayersParam = "kit_layers", BMinParam = "kit_bmin", BMaxParam = "kit_bmax";
    public static readonly StringName SeeParam = "kit_see_through", ArgsParam = "kit_see_through_args";
    /// <summary>the globals as last set (<see cref="Set"/>; a game reads them here: Godot reads globals back only in the
    /// editor)</summary>
    public static Vector4 Hole { get; private set; }
    public static Vector4 Args { get; private set; }

    /// <summary>set the see-through's globals for every kit shader: the hole (its middle, xyz, at the walker's chest; its
    /// radius, w: 0 shut) and its args (the walker's feet height, the height kept over them, the near and body margins)</summary>
    public static void Set(Vector4 hole, Vector4 args)
    {
        Hole = hole; Args = args;
        RenderingServer.GlobalShaderParameterSet(SeeParam, hole);
        RenderingServer.GlobalShaderParameterSet(ArgsParam, args);
    }

    static int nextTag;
    static readonly int[] probeTags = new int[MaxTag + 1];
    static int probeAll;
    static double probeAt = -10;
    public const float ProbeFresh = 1.5f;
    public const float OpenShare = 0.01f, Hold = 0.3f;

    static double Now => Time.GetTicksMsec() / 1000.0;

    // ------------------------------------------------------------------ the marks on a piece

    /// <summary>a piece's marks (0: none)</summary>
    public static uint Layers(GeometryInstance3D g)
    {
        var v = g.GetInstanceShaderParameter(LayersParam);
        return v.VariantType == Variant.Type.Nil ? 0u : (uint)v.AsInt64();
    }

    public static void SetLayers(GeometryInstance3D g, uint m) => g.SetInstanceShaderParameter(LayersParam, (long)m);

    /// <summary>every piece under root gets its world bounds for the shader ("in the walker's way": Unity's renderer
    /// bounds). A level calls it once it stands (KitLevel); a piece that moves later keeps its old box.</summary>
    public static int Bound(Node root)
    {
        int n = 0;
        foreach (var g in Geometry(root))
        {
            var b = WorldAabb(g);
            g.SetInstanceShaderParameter(BMinParam, b.Position);
            g.SetInstanceShaderParameter(BMaxParam, b.End);
            n++;
        }
        return n;
    }

    /// <summary>the meshes (geometry instances) under a node, itself included</summary>
    public static IEnumerable<GeometryInstance3D> Geometry(Node root)
    {
        if (root is GeometryInstance3D self) yield return self;
        foreach (var n in KitNodes.Below(root, "GeometryInstance3D"))
            if (n is GeometryInstance3D g) yield return g;
    }

    public static Aabb WorldAabb(GeometryInstance3D g) => g.GlobalTransform * g.GetAabb();

    static Aabb WorldAabb(IEnumerable<GeometryInstance3D> gs)
    {
        bool any = false;
        var all = new Aabb();
        foreach (var g in gs)
        {
            if (!IsInstanceValid(g)) continue;
            var b = WorldAabb(g);
            all = any ? all.Merge(b) : b;
            any = true;
        }
        return all;
    }

    static bool IsInstanceValid(GodotObject o) => o != null && GodotObject.IsInstanceValid(o);

    /// <summary>every mesh under node is never cut (<see cref="KeepBit"/>)</summary>
    public static void Keep(Node node)
    {
        if (node == null) return;
        foreach (var g in Geometry(node)) SetLayers(g, Layers(g) | KeepBit);
    }

    /// <summary>the mask with the cut at q steps over the piece's origin</summary>
    public static uint WithCut(uint mask, int q) => (mask & ~CutMask) | CutBit | ((uint)(q & 0x3FF) << 22);

    /// <summary>the piece's cut (world y), when it has one</summary>
    public static bool CutY(GeometryInstance3D g, out float y)
    {
        y = 0f;
        uint m = Layers(g);
        if ((m & CutBit) == 0) return false;
        int q = (int)((m >> 22) & 0x3FF);
        if (q >= 512) q -= 1024;
        var t = g.GlobalTransform;
        y = t.Origin.Y + t.Basis.Y.Y * (q * CutStep);
        return true;
    }

    /// <summary>where a cut piece is cut while the walker's feet are at `feet`: its own cut, never under the feet</summary>
    public static bool CutAt(GeometryInstance3D g, float feet, out float y)
    {
        if (!CutY(g, out y)) return false;
        y = Mathf.Max(y, feet + AboveFeet);
        return true;
    }

    // ------------------------------------------------------------------ the hidden check's answer

    /// <summary>the hidden check's answer (KitSeeThroughProbe): pixels per tag over the body, the body's pixels; null:
    /// forget it (the walker was moved)</summary>
    public static void Probed(int[] tags, int all)
    {
        System.Array.Clear(probeTags, 0, probeTags.Length);
        if (tags == null) { probeAt = -10; probeAll = 0; return; }
        System.Array.Copy(tags, probeTags, Mathf.Min(tags.Length, probeTags.Length));
        probeAll = all;
        probeAt = Now;
    }

    /// <summary>is a hidden check deciding the buildings (a recent read)?</summary>
    public static bool Probing => Now - probeAt < ProbeFresh;

    // ------------------------------------------------------------------ loose pieces, standing walls, buildings

    static readonly string[] Standing = { "TownWall", "Palisade", "Gatehouse", "Gate", "Tower" };

    /// <summary>a piece that stands as architecture though it is placed as a prop (along a line, as a fence)</summary>
    public static bool IsStanding(string name)
    {
        foreach (var w in Standing) if (name.Contains(w)) return true;
        return false;
    }

    /// <summary>every mesh of the pieces under group (its children) opens down to the walker's feet, but the standing
    /// ones; round: in the way by the ellipsoid inside its bounds (trees, bushes, rocks)</summary>
    public static int Loose(Node group, bool round = false)
    {
        int n = 0;
        uint bits = LooseBit | (round ? RoundBit : 0u);
        foreach (var piece in KitNodes.Children(group))
        {
            if (IsStanding(piece.Name)) continue;
            foreach (var g in Geometry(piece)) { SetLayers(g, Layers(g) | bits); n++; }
        }
        return n;
    }

    /// <summary>the standing pieces under group, in runs that open as one: modules whose boxes touch (grown 0.3 m)</summary>
    public static List<Building> Runs(Node group)
    {
        var parts = new List<(List<GeometryInstance3D> gs, Aabb b)>();
        foreach (var piece in KitNodes.Children(group))
        {
            if (!IsStanding(piece.Name)) continue;
            var gs = new List<GeometryInstance3D>(Geometry(piece));
            if (gs.Count == 0) continue;
            parts.Add((gs, WorldAabb(gs).Grow(0.3f)));
        }
        var up = new int[parts.Count];
        for (int i = 0; i < up.Length; i++) up[i] = i;
        int Top(int i) { while (up[i] != i) i = up[i] = up[up[i]]; return i; }
        for (int i = 0; i < parts.Count; i++)
            for (int j = i + 1; j < parts.Count; j++)
                if (parts[i].b.Intersects(parts[j].b)) up[Top(i)] = Top(j);
        var runs = new Dictionary<int, List<GeometryInstance3D>>();
        for (int i = 0; i < parts.Count; i++)
        {
            if (!runs.TryGetValue(Top(i), out var l)) runs[Top(i)] = l = new List<GeometryInstance3D>();
            l.AddRange(parts[i].gs);
        }
        var list = new List<Building>();
        foreach (var l in runs.Values) list.Add(new Building(group as Node3D, l.ToArray()) { PerPiece = true });
        return list;
    }

    static readonly List<Building> live = new List<Building>();

    /// <summary>a building's pieces, opened together</summary>
    public class Building
    {
        public readonly GeometryInstance3D[] Pieces;
        public bool Open { get; private set; }
        /// <summary>its tag in the hidden check's view</summary>
        public readonly int Tag;
        /// <summary>its pieces' caps, opened with them</summary>
        public readonly List<GeometryInstance3D> Caps = new List<GeometryInstance3D>();
        /// <summary>a run of walls placed as props: each piece cut over its own foot (a house: over its floor)</summary>
        public bool PerPiece;
        /// <summary>a house's root; a run's: the group its pieces stand in</summary>
        public readonly Node3D Root;
        /// <summary>a house's floor (world y): its root's height</summary>
        public float Floor => IsInstanceValid(Root) ? Root.GlobalPosition.Y : 0f;
        double seenAt = -10;
        Aabb all;
        Vector3 at = new Vector3(float.NaN, 0, 0);

        public Building(Node3D root) : this(root, new List<GeometryInstance3D>(Geometry(root)).ToArray()) { }

        /// <summary>these pieces as one (root: what they move with); registered for <see cref="DecideAll"/> until the root
        /// leaves the tree</summary>
        public Building(Node3D root, GeometryInstance3D[] pieces)
        {
            Root = root;
            Pieces = pieces;
            Tag = nextTag++ % MaxTag + 1;
            uint t = (uint)Tag << TagShift;
            foreach (var g in pieces) SetLayers(g, ((Layers(g) | GroupBit) & ~OpenBit & ~TagMask) | t);
            live.Add(this);
        }

        /// <summary>its root was freed (a level held out of the tree by KitTravel keeps its buildings: they wait)</summary>
        public bool Gone => !IsInstanceValid(Root);

        Aabb All()
        {
            if (!IsInstanceValid(Root) || Root.GlobalPosition == at) return all;
            at = Root.GlobalPosition;
            all = WorldAabb(Pieces);
            return all;
        }

        void Set(bool on)
        {
            if (on == Open) return;
            Open = on;
            foreach (var g in Pieces) if (IsInstanceValid(g)) SetLayers(g, on ? Layers(g) | OpenBit : Layers(g) & ~OpenBit);
            foreach (var g in Caps) if (IsInstanceValid(g)) SetLayers(g, on ? Layers(g) | OpenBit : Layers(g) & ~OpenBit);
        }

        /// <summary>open while it is in the walker's way: its surface over the walker in the hidden check's view (held a
        /// moment), or without a check, one of its pieces' boxes across the sight lines</summary>
        public void Decide(Vector3 cam, Vector4 see, Vector4 args)
        {
            bool on = false;
            bool walker = see.X != 0f || see.Y != 0f || see.Z != 0f;
            if (walker && Probing)
            {
                int px = probeTags[Tag];
                if (px >= (Open ? 1 : Mathf.Max(2, Mathf.CeilToInt(OpenShare * probeAll)))) seenAt = Now;
                on = Now - seenAt < Hold;
            }
            else if (walker && InTheWay(All(), cam, see, args))
                foreach (var g in Pieces)
                    if (IsInstanceValid(g) && g.IsVisibleInTree() && InTheWay(WorldAabb(g), cam, see, args) && Crosses(g, cam, see, args))
                    { on = true; break; }
            Set(on);
        }
    }

    /// <summary>every live building open or not for this frame's see-through (the camera's position, the globals it set)</summary>
    public static void DecideAll(Vector3 cam, Vector4 see, Vector4 args)
    {
        live.RemoveAll(b => b.Gone);
        foreach (var b in live) if (b.Root.IsInsideTree()) b.Decide(cam, see, args);
    }

    /// <summary>
    /// The see-through's buildings, cuts and caps for a level that stands (KitLevel calls it after <see cref="Bound"/>):
    /// each premade structure in it (a KitStructure, or a layout's VKX_ST_ group) opens as one building, its pieces cut
    /// <see cref="KitSeeThroughCaps.Height"/> over its floor (its root's height) with caps. Unity's
    /// KitVillage.SetUpSeeThrough does this for its villages (loose nature and props, walls in runs, houses with floors);
    /// here too: a village's structures are left to it. The cap bake calls it with KitSeeThroughCaps.Collecting set.
    /// </summary>
    public static List<Building> SetUpLevel(Node level)
    {
        var list = new List<Building>();
        foreach (var n in KitNodes.Below(level, "Node3D"))
        {
            if (n is not Node3D s || !IsStructure(s)) continue;
            bool inner = false;                                        // (a structure inside one already taken, or a village's: its own)
            for (var p = s.GetParent(); p != null && p != level && !inner; p = p.GetParent()) inner = p is KitVillage || (p is Node3D pn && IsStructure(pn));
            if (inner) continue;
            var gs = new List<GeometryInstance3D>(Geometry(s)).ToArray();
            if (gs.Length == 0) continue;
            var b = new Building(s, gs);
            list.Add(b);
            foreach (var g in gs) KitSeeThroughCaps.Cut(g, b.Floor, b);
        }
        KitSeeThroughCaps.Settle();
        return list;
    }

    static bool IsStructure(Node3D n) => n is KitStructure || n.Name.ToString().StartsWith("VKX_ST_");

    /// <summary>the buildings registered now (a level's, while it is in the tree)</summary>
    public static IReadOnlyList<Building> Buildings => live;

    // ------------------------------------------------------------------ the shader's tests on the CPU

    /// <summary>KitSeeThroughInTheWay (the box): do the bounds meet the wedge from the camera to the walker's upper body?</summary>
    public static bool InTheWay(Aabb b, Vector3 cam, Vector4 see, Vector4 args)
    {
        float w = args.W;
        if (w <= 0) return true;
        float feet = args.X, chest = see.Y - feet, waist = feet + 0.9f * chest, head = feet + 1.9f * chest;
        var dc = new Vector3(see.X, 0.5f * (waist + head), see.Z) - cam;
        var e = new Vector3(w, 0.5f * (head - waist), w);
        Vector3 bmin = b.Position, bmax = b.End;
        float lo = 0, hi = 1;
        for (int i = 0; i < 3; i++)
        {
            Le(dc[i] - e[i], bmax[i] - cam[i], ref lo, ref hi);
            Le(-(dc[i] + e[i]), cam[i] - bmin[i], ref lo, ref hi);
        }
        return lo <= hi;
    }

    /// <summary>does a sight line from the camera to the walker's waist, middle or head (at its centre and args.w to
    /// either side, square to the view) cross the piece's own box (its local bounds, turned with it)?</summary>
    public static bool Crosses(GeometryInstance3D g, Vector3 cam, Vector4 see, Vector4 args)
    {
        float feet = args.X, chest = see.Y - feet;
        var f = new Vector3(see.X - cam.X, 0f, see.Z - cam.Z);
        var side = f.LengthSquared() > 1e-6f ? new Vector3(f.Z, 0f, -f.X).Normalized() * Mathf.Max(args.W, 0f) : Vector3.Zero;
        var m = g.GlobalTransform.AffineInverse();
        var box = g.GetAabb();
        var a = m * cam;
        for (int k = 0; k < 3; k++)
        {
            var at = new Vector3(see.X, feet + (0.9f + 0.5f * k) * chest, see.Z);
            for (int j = -1; j <= 1; j++)
                if (Segment(a, m * (at + side * j), box)) return true;
        }
        return false;
    }

    static bool Segment(Vector3 a, Vector3 b, Aabb box)
    {
        Vector3 d = b - a, mn = box.Position, mx = box.End;
        float lo = 0f, hi = 1f;
        for (int i = 0; i < 3; i++)
        {
            if (Mathf.Abs(d[i]) < 1e-6f) { if (a[i] < mn[i] || a[i] > mx[i]) return false; continue; }
            float t1 = (mn[i] - a[i]) / d[i], t2 = (mx[i] - a[i]) / d[i];
            if (t1 > t2) (t1, t2) = (t2, t1);
            lo = Mathf.Max(lo, t1); hi = Mathf.Min(hi, t2);
            if (lo > hi) return false;
        }
        return true;
    }

    static void Le(float a, float b, ref float lo, ref float hi)
    {
        if (a > 1e-6f) hi = Mathf.Min(hi, b / a);
        else if (a < -1e-6f) lo = Mathf.Max(lo, b / a);
        else if (b < 0) hi = -1;
    }

    /// <summary>a point along a screen ray the see-through has opened (the hole round the walker's chest, above the height
    /// kept over its feet, short of the walker): a pointer there looks past it. Read from the globals (KitCamera sets
    /// them). `of` (the collider hit, a building's root) brings the piece's marks. Unity: KitSeeThrough.Opened.</summary>
    public static bool Opened(Vector3 point, float distance, Vector3 rayFrom, Vector3 rayDir, Node of = null)
    {
        var hole = Hole;
        if (hole.W <= 0f) return false;
        var chest = new Vector3(hole.X, hole.Y, hole.Z) - rayFrom;
        if (distance >= chest.Dot(rayDir)) return false;
        if (rayDir.Cross(chest).LengthSquared() > hole.W * hole.W) return false;
        var args = Args;
        float keep = args.Y;
        var g = of != null ? MeshOf(of) : null;
        if (g != null)
        {
            uint m = Layers(g);
            if ((m & GroupBit) != 0 && (m & OpenBit) == 0) return false;
            if (CutAt(g, args.X, out float cut)) return point.Y > cut;
            if ((m & LooseBit) != 0) keep = -0.25f;
        }
        return point.Y > args.X + keep;
    }

    /// <summary>the mesh a hit stands for: the nearest geometry up its parents (a piece's body is a sibling of its mesh), or
    /// the first below it (a building's root)</summary>
    static GeometryInstance3D MeshOf(Node n)
    {
        for (var p = n; p != null; p = p.GetParent())
        {
            if (p is GeometryInstance3D g) return g;
            foreach (var c in KitNodes.Children(p)) if (c is GeometryInstance3D cg) return cg;
            if (p is KitPiece) break;
        }
        foreach (var g in Geometry(n)) return g;
        return null;
    }
}
