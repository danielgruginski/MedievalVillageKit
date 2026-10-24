#if TOOLS
using System.Text.Json;
using System.Text.RegularExpressions;
using Godot;

namespace MedievalKit.Editor;

/// <summary>Runs on every kit piece's .glb (gdx_export.py names it in each .glb.import) and makes the piece what
/// Unity's KitBuilder makes a prefab:
///  - the root a KitPiece named after the piece, with the master's Blender properties (glTF extras) and the Blender
///    slot of each surface (pieces.json's slot_map);
///  - colliders: vki_collider boxes (Blender piece space; not on walk-over overlays, vki_nav "none", as in the kit's walk
///    check; on layer KitPiece.Passable for doors that open and breakables, else KitPiece.Solid), a walkable slab on each open quarter of a cave / stream ground tile, the whole mesh on a piece with a
///    ground material (terrain, paving, stair: KitTerrain but water);
///  - shadows from both faces, as Blender casts them (the one-sided materials cull what the camera sees, not the sun);
///  - every surface must have taken its material from the shared library (res://kit/materials/, mapped by name).</summary>
[Tool]
public partial class KitImport : EditorScenePostImport
{
    static JsonDocument pieces;

    static JsonElement PieceData(string name)
    {
        pieces ??= JsonDocument.Parse(Godot.FileAccess.GetFileAsString(KitPaths.Pieces));
        return pieces.RootElement.TryGetProperty(name, out var d) ? d : default;
    }

    /// <summary>a Blender box [cx, cy, cz, sx, sy, sz] -> a Godot box shape under `body` ((x, y, z) -> (x, z, -y))</summary>
    static void AddBox(Node3D body, Node owner, float cx, float cy, float cz, float sx, float sy, float sz)
    {
        var cs = new CollisionShape3D
        {
            Shape = new BoxShape3D { Size = new Vector3(Mathf.Abs(sx), Mathf.Abs(sz), Mathf.Abs(sy)) },
            Position = new Vector3(cx, cz, -cy),
        };
        body.AddChild(cs);
        cs.Owner = owner;
    }

    static bool Flag(Godot.Collections.Dictionary<string, string> p, string key) =>
        p.Get(key) is string v && v != "" && v != "0" && v != "False";

    public override GodotObject _PostImport(Node scene)
    {
        string name = GetSourceFile().GetFile().GetBaseName();
        MeshInstance3D mi = null;
        foreach (var n in scene.FindChildren("*", "MeshInstance3D", true, false))
        {
            mi = (MeshInstance3D)n;
            mi.CastShadow = GeometryInstance3D.ShadowCastingSetting.DoubleSided;
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                var m = mi.Mesh.SurfaceGetMaterial(s);
                if (m == null || !m.ResourcePath.StartsWith(KitPaths.Materials))
                    GD.PushWarning($"{GetSourceFile()}: surface {s} has no library material ({m})");
            }
        }
        var props = mi != null && mi.HasMeta("extras") ? KitProps.FromVariant(mi.GetMeta("extras").AsGodotDictionary()) : new();
        var data = PieceData(name);
        var slots = new int[mi?.Mesh.GetSurfaceCount() ?? 0];
        for (int i = 0; i < slots.Length; i++) slots[i] = -1;
        bool ground = false;
        if (data.ValueKind == JsonValueKind.Object)
        {
            foreach (var kv in data.GetProperty("slot_map").EnumerateObject())
            {
                int surf = kv.Value.GetInt32();
                if (surf >= 0 && surf < slots.Length) slots[surf] = int.Parse(kv.Name);
            }
            foreach (var m in data.GetProperty("surfaces").EnumerateArray())
            {
                string mn = m.GetString();
                var mat = mn != null ? ResourceLoader.Load<ShaderMaterial>(KitPaths.Materials + mn + ".tres") : null;
                string sh = mat?.Shader?.ResourcePath ?? "";
                if (sh.StartsWith(KitPaths.Shaders + "KitTerrain") && !sh.EndsWith("Water.gdshader")) ground = true;
            }
        }

        // the root becomes a KitPiece (a script set at import; the managed wrapper is replaced, so set through the engine)
        ulong id = scene.GetInstanceId();
        scene.SetScript(GD.Load<Script>(KitPaths.Runtime + "KitPiece.cs"));
        var root = (Node3D)InstanceFromId(id);
        root.Name = name;
        root.Set(KitPiece.PropertyName.Piece, name);
        root.Set(KitPiece.PropertyName.Props, props);
        root.Set(KitPiece.PropertyName.BlenderSlots, slots);

        bool passable = Flag(props, "vki_openable") || Flag(props, "vki_breakable");
        StaticBody3D body = null;
        StaticBody3D Body()
        {
            if (body != null) return body;
            body = new StaticBody3D { Name = "Collision", CollisionLayer = passable ? KitPiece.Passable : KitPiece.Solid };
            root.AddChild(body);
            body.Owner = root;
            return body;
        }
        string col = props.Get("vki_collider");
        bool walkOver = props.Get("vki_class") == "overlay" && props.Get("vki_nav") == "none";
        if (!string.IsNullOrEmpty(col) && !walkOver)
        {
            try
            {
                foreach (var b in JsonDocument.Parse(col).RootElement.EnumerateArray())
                    AddBox(Body(), root, b[0].GetSingle(), b[1].GetSingle(), b[2].GetSingle(), b[3].GetSingle(), b[4].GetSingle(), b[5].GetSingle());
            }
            catch (JsonException) { GD.PushWarning($"{name}: bad vki_collider"); }
        }
        // a chasm / stream ground tile owns the floor of its open quarters (the cave layout lays no Floor_075 there), but
        // its vki_collider only blocks the chasm: the open quarters get a walkable slab (top at floor level)
        var g = Regex.Match(name, @"^SM_VKI_Ground_(Cave|Stream)_([OX]{4})(_|$)");
        if (g.Success)
        {
            var quarter = new[] { (-0.375f, -0.375f), (0.375f, -0.375f), (0.375f, 0.375f), (-0.375f, 0.375f) };   // SW SE NE NW, Blender x / y
            for (int i = 0; i < 4; i++)
                if (g.Groups[2].Value[i] == 'O') AddBox(Body(), root, quarter[i].Item1, quarter[i].Item2, -0.05f, 0.75f, 0.75f, 0.1f);
        }
        if (ground && mi != null)       // walkable terrain / paving: the mesh itself
        {
            var gb = new StaticBody3D { Name = "Ground" };
            var shape = new CollisionShape3D { Shape = mi.Mesh.CreateTrimeshShape() };
            root.AddChild(gb);
            gb.Owner = root;
            gb.AddChild(shape);
            shape.Owner = root;
        }
        return root;
    }
}
#endif
