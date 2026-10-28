using System.Collections.Generic;
using Godot;

namespace MedievalKit;

/// <summary>
/// Grass blades over an outdoor map's grass (the village builder writes the clump list: where each clump stands, its
/// tint and height; 16 bytes a clump, as Unity's). Built once in _Ready from <see cref="clumps"/> (saved in the scene):
/// the clumps go into MultiMeshInstance3D chunks of <see cref="ChunkSize"/> metres (internal children, not saved), so
/// Godot's frustum culls a chunk at a time and its visibility range drops chunks past <see cref="reach"/>. Every clump
/// is the same small mesh of <see cref="MaxBlades"/> blades whose vertices carry only their blade and corner; the vertex
/// shader (Shaders/KitGrass.gdshader) grows each clump's 5-7 blades from a hash of its root, sways them in the wind and
/// parts them round the walker (the see-through's walker position), so no blade geometry is held but the one mesh and
/// the per-clump data (tint, height, root). Nothing runs per frame on the CPU. Positions are this node's local space,
/// which is the ground mesh's object space (plan x, h, -y; the ground's origin at the map margin's south-west corner):
/// the shader reads the ground's grass colour under each blade there (<c>grass_map</c>, <c>macro_map</c>,
/// <c>grass_sat</c> copied from the ground material). Unity: KitGrass (there a compute cull and one indirect draw per
/// camera; Godot's own culling of the chunks does that job here).
/// </summary>
[GlobalClass, Tool]
public partial class KitGrass : Node3D
{
    /// <summary>the grass's material (MedievalKit Shaders/KitGrass.gdshader; the village copies the ground's grass maps
    /// into it)</summary>
    [Export] public ShaderMaterial material;
    /// <summary>clumps, 16 bytes each: x, y, z (float, local), then tint r, g, b (x 200) and height (x 255) (bytes)</summary>
    [Export] public byte[] clumps;
    /// <summary>the clumps' bounds in local space (the village sets it; informational: each chunk works out its own)</summary>
    [Export] public Aabb localBounds;
    [Export] public float minHeight = 0.3f, maxHeight = 0.58f;
    [Export] public int seed = 1;
    [Export] public bool castShadows = true;
    /// <summary>clumps farther than this from the camera are not drawn (m; per chunk, from its middle)</summary>
    [Export] public float reach = 90f;

    public const int MaxBlades = 7, VertsPerBlade = 9;          // 3 triangles a blade, unindexed
    /// <summary>a chunk's side (m): one MultiMeshInstance3D, culled as one</summary>
    public const float ChunkSize = 16f;
    public int Clumps => clumps == null ? 0 : clumps.Length / 16;

    static ArrayMesh clumpMesh;
    readonly List<MultiMeshInstance3D> chunks = new();

    /// <summary>pack a clump (the village): its root (this node's local space), its tint (about 1: the ground's grass
    /// colour times this) and how tall it is (0..1: 0.6x .. 1.25x the blades' length)</summary>
    public static void Write(List<byte> data, Vector3 root, Color tint, float tall)
    {
        data.AddRange(System.BitConverter.GetBytes(root.X));
        data.AddRange(System.BitConverter.GetBytes(root.Y));
        data.AddRange(System.BitConverter.GetBytes(root.Z));
        data.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tint.R * 200f), 0, 255));
        data.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tint.G * 200f), 0, 255));
        data.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tint.B * 200f), 0, 255));
        data.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tall * 255f), 0, 255));
    }

    public override void _Ready() => Rebuild();

    /// <summary>the chunks made again from the clump list (on entering; call it after changing the clumps or the
    /// settings of a grass already in the tree)</summary>
    public void Rebuild()
    {
        foreach (var c in chunks) if (IsInstanceValid(c)) { RemoveChild(c); c.QueueFree(); }
        chunks.Clear();
        int n = Clumps;
        if (n == 0 || material == null) return;

        // the clumps by chunk
        var byChunk = new Dictionary<Vector2I, List<int>>();
        for (int i = 0; i < n; i++)
        {
            float x = System.BitConverter.ToSingle(clumps, i * 16), z = System.BitConverter.ToSingle(clumps, i * 16 + 8);
            var key = new Vector2I(Mathf.FloorToInt(x / ChunkSize), Mathf.FloorToInt(z / ChunkSize));
            if (!byChunk.TryGetValue(key, out var list)) byChunk[key] = list = new List<int>();
            list.Add(i);
        }

        var mesh = ClumpMesh();
        float tallest = maxHeight * 1.25f;
        foreach (var (key, list) in byChunk)
        {
            // the chunk's node at its clumps' middle (the visibility range measures from it), instances relative to it
            Vector3 lo = new(float.MaxValue, float.MaxValue, float.MaxValue), hi = -lo;
            foreach (int i in list)
            {
                var p = Root(i);
                lo = lo.Min(p); hi = hi.Max(p);
            }
            var mid = (lo + hi) * 0.5f;
            // per instance: a 3 x 4 transform (rows; a translation), colour (tint rgb, height a), custom (root xyz, local)
            var buf = new float[list.Count * 20];
            for (int k = 0; k < list.Count; k++)
            {
                int i = list[k], o = k * 20;
                var p = Root(i);
                var d = p - mid;
                buf[o] = 1f; buf[o + 3] = d.X;
                buf[o + 5] = 1f; buf[o + 7] = d.Y;
                buf[o + 10] = 1f; buf[o + 11] = d.Z;
                buf[o + 12] = clumps[i * 16 + 12] / 200f;
                buf[o + 13] = clumps[i * 16 + 13] / 200f;
                buf[o + 14] = clumps[i * 16 + 14] / 200f;
                buf[o + 15] = clumps[i * 16 + 15] / 255f;
                buf[o + 16] = p.X; buf[o + 17] = p.Y; buf[o + 18] = p.Z;
            }
            var mm = new MultiMesh
            {
                TransformFormat = MultiMesh.TransformFormatEnum.Transform3D, UseColors = true, UseCustomData = true,
                Mesh = mesh, InstanceCount = list.Count,
            };
            mm.Buffer = buf;
            var mmi = new MultiMeshInstance3D
            {
                Name = $"GrassChunk_{key.X}_{key.Y}", Multimesh = mm, MaterialOverride = material, Position = mid,
                CastShadow = castShadows ? GeometryInstance3D.ShadowCastingSetting.On : GeometryInstance3D.ShadowCastingSetting.Off,
                CustomAabb = new Aabb(lo - mid - new Vector3(1.2f, 0.3f, 1.2f), hi - lo + new Vector3(2.4f, tallest + 0.6f, 2.4f)),
                VisibilityRangeEnd = reach,
            };
            AddChild(mmi, false, InternalMode.Back);
            mmi.SetInstanceShaderParameter("grass_params", new Vector3(minHeight, maxHeight, seed));
            chunks.Add(mmi);
        }
    }

    Vector3 Root(int i) => new(System.BitConverter.ToSingle(clumps, i * 16), System.BitConverter.ToSingle(clumps, i * 16 + 4),
                               System.BitConverter.ToSingle(clumps, i * 16 + 8));

    /// <summary>the one clump mesh every chunk draws: MaxBlades blades of VertsPerBlade vertices (unindexed triangles),
    /// each vertex's UV its blade and its corner; the vertex shader puts them in place (the positions here only give the
    /// mesh its bounds)</summary>
    static ArrayMesh ClumpMesh()
    {
        if (clumpMesh != null) return clumpMesh;
        int[] corner = { 0, 2, 1, 1, 2, 3, 2, 4, 3 };   // (foot L, mid L, foot R), (foot R, mid L, mid R), (mid L, tip, mid R)
        var verts = new Vector3[MaxBlades * VertsPerBlade];
        var uvs = new Vector2[verts.Length];
        var normals = new Vector3[verts.Length];
        for (int b = 0; b < MaxBlades; b++)
            for (int k = 0; k < VertsPerBlade; k++)
            {
                int v = b * VertsPerBlade + k;
                verts[v] = new Vector3(0f, corner[k] * 0.2f, 0f);
                uvs[v] = new Vector2(b, corner[k]);
                normals[v] = Vector3.Back;
            }
        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = verts;
        arrays[(int)Mesh.ArrayType.Normal] = normals;
        arrays[(int)Mesh.ArrayType.TexUV] = uvs;
        clumpMesh = new ArrayMesh();
        clumpMesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        arrays.Dispose();
        // a clump's reach: its blades (0.16 m round the root, leaning out) swayed and parted
        clumpMesh.CustomAabb = new Aabb(new Vector3(-1.2f, -0.3f, -1.2f), new Vector3(2.4f, 1.6f, 2.4f));
        return clumpMesh;
    }
}
