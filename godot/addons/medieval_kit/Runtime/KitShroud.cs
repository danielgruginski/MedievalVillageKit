using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit;

/// <summary>
/// The shroud of an underground level (the Diablo-like cave look): what lies away from where the walker can go darkens
/// with that distance, down to black a few metres in, so the rock between the passages fades into the black round the
/// level instead of ending at a pale top and a cliff edge (every KitLit material, Shaders/kit_shroud.gdshaderinc). On a
/// level's scene (a chain's play scene carries one): while it is in the tree, the walkable ground near the level's floor
/// (the navmesh regions in its world; the rock tops' unreachable islands left out) is drawn into a distance field of
/// <see cref="cell"/>-metre cells and handed to the shader as globals (built again on each arrival,
/// <see cref="KitTravel.Arrived"/>); out of the tree, the shroud is off. Tune <see cref="darkFrom"/> /
/// <see cref="blackAt"/> live (the remote inspector): they take effect at once. Unity: KitShroud.
/// </summary>
[GlobalClass]
public partial class KitShroud : Node3D
{
    float dark = 0.2f, black = 3f, top = 0.4f;

    /// <summary>metres from the walkable ground where the darkening starts (the passages' walls stay lit)</summary>
    [Export] public float darkFrom { get => dark; set { dark = value; if (active == this) Apply(); } }
    /// <summary>metres from the walkable ground where it is black</summary>
    [Export] public float blackAt { get => black; set { black = value; if (active == this) Apply(); } }
    /// <summary>the light the rock's tops keep (faces turned up, well above the floor): dim, so the rock reads as dark
    /// mass, not pale tiles</summary>
    [Export(PropertyHint.Range, "0,1")] public float topLight { get => top; set { top = value; if (active == this) Apply(); } }
    /// <summary>the field's cell (m)</summary>
    [Export] public float cell = 0.5f;
    /// <summary>the walkable ground counted: within this height (m) of the level's floor (cave rock tops carry navmesh
    /// islands no one reaches)</summary>
    [Export] public float floorBand = 1.6f;

    /// <summary>the field's range: distances beyond it read as this (m)</summary>
    const float Range = 10f;
    public static readonly StringName TexParam = "kit_shroud_tex", RectParam = "kit_shroud_rect",
                                      ArgsParam = "kit_shroud_args", Args2Param = "kit_shroud_args2";
    static KitShroud active;
    ImageTexture tex;             // (not `field`: C# 14's keyword inside a property)
    float floorY;
    int builds;

    /// <summary>the shroud now drawn (null: none)</summary>
    public static KitShroud Active => IsInstanceValid(active) ? active : null;
    /// <summary>the floor it found (world y) and its distance field (null before a build)</summary>
    public float FloorY => floorY;
    public Texture2D Field => tex;

    public override void _EnterTree()
    {
        KitTravel.Arrived += OnArrived;
        _ = BuildSoon();
    }

    public override void _ExitTree()
    {
        KitTravel.Arrived -= OnArrived;
        builds++;                                                          // a build on its way stops
        if (active != this) return;
        active = null;
        RenderingServer.GlobalShaderParameterSet(ArgsParam, Vector4.Zero);
    }

    void OnArrived(string level, KitSpawn spawn)
    {
        if (IsInsideTree()) _ = BuildSoon();
    }

    /// <summary>once the level's navmesh is in and the walker stands on it (a chain's pieces streamed in round it); a
    /// few seconds at most</summary>
    async Task BuildSoon()
    {
        int mine = ++builds;
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        ulong start = Time.GetTicksMsec();
        while (Time.GetTicksMsec() - start < 5000)
        {
            if (mine != builds || !IsInsideTree()) return;
            var w = KitTravel.Walker;
            if (!KitTravel.Travelling && w != null && OnNavMesh(w.GlobalPosition) && SpawnHeight() != null) break;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        }
        if (mine == builds && IsInsideTree()) Build();
    }

    bool OnNavMesh(Vector3 p)
    {
        var map = GetWorld3D().NavigationMap;
        if (NavigationServer3D.MapGetIterationId(map) == 0) return false;
        return NavigationServer3D.MapGetClosestPoint(map, p).DistanceTo(p) <= 0.4f;
    }

    void Apply()
    {
        RenderingServer.GlobalShaderParameterSet(ArgsParam, new Vector4(1f, darkFrom, Mathf.Max(darkFrom + 0.1f, blackAt), Range));
        RenderingServer.GlobalShaderParameterSet(Args2Param, new Vector4(floorY, topLight, 0f, 0f));
    }

    /// <summary>the walkable triangles in world space: every enabled navigation region in this node's world (Unity:
    /// NavMesh.CalculateTriangulation), its convex polygons fanned</summary>
    List<Vector3> Triangles()
    {
        var tris = new List<Vector3>();
        var map = GetWorld3D().NavigationMap;      // (worlds compared by their RIDs: a wrapper may differ)
        foreach (var r in KitNodes.Below(GetTree().Root, "NavigationRegion3D").OfType<NavigationRegion3D>())
        {
            if (!r.Enabled || !r.IsInsideTree() || r.GetWorld3D().NavigationMap != map || r.NavigationMesh == null) continue;
            var nm = r.NavigationMesh;
            var t = r.GlobalTransform;
            var v = nm.GetVertices();
            for (int i = 0; i < nm.GetPolygonCount(); i++)
            {
                var poly = nm.GetPolygon(i);
                for (int k = 1; k + 1 < poly.Length; k++)
                {
                    tris.Add(t * v[poly[0]]); tris.Add(t * v[poly[k]]); tris.Add(t * v[poly[k + 1]]);
                }
            }
        }
        return tris;
    }

    /// <summary>the distance field from the navmesh as it is now (on entering the tree and each arrival; again after the
    /// walkable ground changes)</summary>
    public void Build()
    {
        var v = Triangles();
        if (v.Count < 3) return;
        // the floor: the height most of the walkable area lies at
        float floor = FloorHeight(v);
        floorY = floor;
        float minX = float.MaxValue, minZ = float.MaxValue, maxX = float.MinValue, maxZ = float.MinValue;
        for (int t = 0; t < v.Count; t += 3)
        {
            if (!OnFloor(v, t, floor)) continue;
            for (int k = 0; k < 3; k++)
            {
                var p = v[t + k];
                minX = Mathf.Min(minX, p.X); maxX = Mathf.Max(maxX, p.X);
                minZ = Mathf.Min(minZ, p.Z); maxZ = Mathf.Max(maxZ, p.Z);
            }
        }
        if (minX > maxX) return;
        float margin = Range + 1f;
        minX -= margin; minZ -= margin; maxX += margin; maxZ += margin;
        float c = Mathf.Max(0.1f, cell);
        int w = Mathf.Clamp(Mathf.CeilToInt((maxX - minX) / c), 1, 4096), h = Mathf.Clamp(Mathf.CeilToInt((maxZ - minZ) / c), 1, 4096);
        const float Far = 1e6f;
        var d = new float[w * h];
        System.Array.Fill(d, Far);

        // the walkable cells: cell centres inside a floor triangle, and the cells under its corners
        for (int t = 0; t < v.Count; t += 3)
        {
            if (!OnFloor(v, t, floor)) continue;
            Vector2 a = Xz(v[t]), b = Xz(v[t + 1]), e = Xz(v[t + 2]);
            int x0 = Cell(Mathf.Min(a.X, Mathf.Min(b.X, e.X)), minX, c, w), x1 = Cell(Mathf.Max(a.X, Mathf.Max(b.X, e.X)), minX, c, w);
            int z0 = Cell(Mathf.Min(a.Y, Mathf.Min(b.Y, e.Y)), minZ, c, h), z1 = Cell(Mathf.Max(a.Y, Mathf.Max(b.Y, e.Y)), minZ, c, h);
            for (int z = z0; z <= z1; z++)
                for (int x = x0; x <= x1; x++)
                    if (Inside(new Vector2(minX + (x + 0.5f) * c, minZ + (z + 0.5f) * c), a, b, e)) d[z * w + x] = 0f;
            foreach (var p in new[] { a, b, e }) d[Cell(p.Y, minZ, c, h) * w + Cell(p.X, minX, c, w)] = 0f;
        }

        // the distance to the nearest walkable cell (two chamfer passes, in cells)
        const float D1 = 1f, D2 = 1.41421356f;
        for (int z = 0; z < h; z++)
            for (int x = 0; x < w; x++)
            {
                int i = z * w + x;
                float m = d[i];
                if (x > 0) m = Mathf.Min(m, d[i - 1] + D1);
                if (z > 0)
                {
                    m = Mathf.Min(m, d[i - w] + D1);
                    if (x > 0) m = Mathf.Min(m, d[i - w - 1] + D2);
                    if (x < w - 1) m = Mathf.Min(m, d[i - w + 1] + D2);
                }
                d[i] = m;
            }
        for (int z = h - 1; z >= 0; z--)
            for (int x = w - 1; x >= 0; x--)
            {
                int i = z * w + x;
                float m = d[i];
                if (x < w - 1) m = Mathf.Min(m, d[i + 1] + D1);
                if (z < h - 1)
                {
                    m = Mathf.Min(m, d[i + w] + D1);
                    if (x < w - 1) m = Mathf.Min(m, d[i + w + 1] + D2);
                    if (x > 0) m = Mathf.Min(m, d[i + w - 1] + D2);
                }
                d[i] = m;
            }

        // row z of the image at v = z (the shader's uv.y runs along world z the same way)
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = (byte)Mathf.RoundToInt(Mathf.Clamp(d[i] * c / Range, 0f, 1f) * 255f);
        var img = Image.CreateFromData(w, h, false, Image.Format.R8, px);
        if (tex != null && tex.GetWidth() == w && tex.GetHeight() == h) tex.Update(img);
        else tex = ImageTexture.CreateFromImage(img);
        RenderingServer.GlobalShaderParameterSet(TexParam, tex);
        RenderingServer.GlobalShaderParameterSet(RectParam, new Vector4(minX, minZ, 1f / (w * c), 1f / (h * c)));
        active = this;
        Apply();
    }

    bool OnFloor(List<Vector3> v, int t, float floor) => Mathf.Abs((v[t].Y + v[t + 1].Y + v[t + 2].Y) / 3f - floor) <= floorBand;

    /// <summary>the level's floor: of the heights (0.25 m bands) holding a good share of the walkable area, the one
    /// nearest the level's spawns (else the walker's, else the lowest). Not simply the largest: a cave's flat rock
    /// tops carry navmesh islands that can outweigh its winding floor.</summary>
    float FloorHeight(List<Vector3> v)
    {
        var area = new Dictionary<int, float>();
        float total = 0f;
        for (int t = 0; t < v.Count; t += 3)
        {
            Vector3 a = v[t], b = v[t + 1], e = v[t + 2];
            int band = Mathf.RoundToInt((a.Y + b.Y + e.Y) / 3f * 4f);
            float s = (b - a).Cross(e - a).Length() * 0.5f;
            area[band] = (area.TryGetValue(band, out var x) ? x : 0f) + s;
            total += s;
        }
        float? near = SpawnHeight();
        if (near == null && KitTravel.Walker != null) near = KitTravel.Walker.GlobalPosition.Y;
        int best = int.MaxValue; float bestScore = float.MaxValue;
        foreach (var kv in area)
        {
            if (kv.Value < total * 0.05f) continue;
            float score = near.HasValue ? Mathf.Abs(kv.Key / 4f - near.Value) : kv.Key;
            if (score < bestScore) { bestScore = score; best = kv.Key; }
        }
        return best == int.MaxValue ? (near ?? 0f) : best / 4f;
    }

    /// <summary>the middle height of the loaded levels' spawns in this world (they stand on the floor; a walker on its
    /// way, or a test walker left on a rock top, may not), or null without any</summary>
    float? SpawnHeight()
    {
        var map = GetWorld3D().NavigationMap;
        var ys = KitNodes.Below(GetTree().Root, "").OfType<KitSpawn>().Where(s => s.IsInsideTree() && s.GetWorld3D().NavigationMap == map)
                         .Select(s => s.GlobalPosition.Y).OrderBy(y => y).ToList();
        return ys.Count == 0 ? null : ys[ys.Count / 2];
    }

    static Vector2 Xz(Vector3 p) => new(p.X, p.Z);
    static int Cell(float x, float min, float c, int n) => Mathf.Clamp(Mathf.FloorToInt((x - min) / c), 0, n - 1);

    static bool Inside(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
    {
        float d1 = (p.X - b.X) * (a.Y - b.Y) - (a.X - b.X) * (p.Y - b.Y);
        float d2 = (p.X - c.X) * (b.Y - c.Y) - (b.X - c.X) * (p.Y - c.Y);
        float d3 = (p.X - a.X) * (c.Y - a.Y) - (c.X - a.X) * (p.Y - a.Y);
        bool neg = d1 < 0 || d2 < 0 || d3 < 0, pos = d1 > 0 || d2 > 0 || d3 > 0;
        return !(neg && pos);
    }
}
