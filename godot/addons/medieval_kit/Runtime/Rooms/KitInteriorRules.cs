using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Nodes;
using Godot;

namespace MedievalKit;

/// <summary>
/// What <see cref="KitRoom"/> builds rooms from: res://kit/data/interior_rules.json (vkx_export_interior_rules: the
/// grid, families, plan tokens, style slots and materials, and every Blender room record and plan as presets), the
/// kit's pieces by name (pieces.json's scenes) and the style materials by name (res://kit/materials/). Point
/// <see cref="RulesPath"/> at a copy to customise. Unity: KitInteriorRules (a ScriptableObject with prefab and material
/// lists; here the kit's data files are the lists).
/// </summary>
[GlobalClass, Tool]
public partial class KitInteriorRules : Resource
{
    [Export(PropertyHint.File, "*.json")] public string RulesPath = KitPaths.Data + "interior_rules.json";

    static KitInteriorRules shared;
    /// <summary>the kit's own rules (res://kit/data/interior_rules.json), loaded once</summary>
    public static KitInteriorRules Default => shared ??= new KitInteriorRules();

    /// <summary>a piece the kit does not have, by name (the game's own: a dead goblin for a cave's finds). Null: none.
    /// Unity: KitInteriorRules.External (there the editor also searches the project).</summary>
    public static Func<string, PackedScene> External;

    /// <summary>what a room needs of a piece without placing it: its Blender properties (pieces.json, as text: JSON
    /// values stay JSON strings), its mesh box in Blender piece space (x0, y0, z0, x1, y1, z1; null without a mesh) and
    /// the Blender slot of each surface</summary>
    public sealed class PieceInfo
    {
        public string name;
        public PackedScene scene;
        public Godot.Collections.Dictionary<string, string> props = new();
        public float[] box;
        public int[] slots = Array.Empty<int>();
        public string Get(string key, string fallback = null) => props.Get(key, fallback);
        public bool Has(string key) => props.Has(key);
        public float GetFloat(string key, float fallback = 0f) => props.GetFloat(key, fallback);
    }

    JsonObject json;
    string jsonPath;
    readonly Dictionary<string, PieceInfo> infos = new();

    public JsonObject Json
    {
        get
        {
            if (json == null || jsonPath != RulesPath)
            {
                jsonPath = RulesPath;
                json = FileAccess.FileExists(RulesPath) ? KitJson.ParseObject(FileAccess.GetFileAsString(RulesPath)) : new JsonObject();
            }
            return json;
        }
    }

    public IEnumerable<string> RoomNames => (Json["rooms"] as JsonObject)?.Select(p => p.Key) ?? Enumerable.Empty<string>();

    /// <summary>a kit room's record (a copy), its zones back in their listed order (the first listed wins where zones
    /// overlap; the export sorts keys and keeps the order in "zone_order")</summary>
    public JsonObject Room(string name)
    {
        if (Json["rooms"]?[name] is not JsonObject src) return null;
        var r = (JsonObject)src.DeepClone();
        if (r["zone_order"] is JsonArray order && r["zones"] is JsonObject zones)
        {
            var z = new JsonObject();
            foreach (var n in order) if (zones[n.S()] != null) z[n.S()] = zones[n.S()].DeepClone();
            foreach (var p in zones) if (z[p.Key] == null) z[p.Key] = p.Value?.DeepClone();
            r["zones"] = z;
        }
        r.Remove("zone_order");
        return r;
    }

    public string Plan(string name) => Json["plans"]?[name].S();

    // pieces.json, parsed once for all rules
    static Dictionary<string, JsonElement> pieceData;

    static Dictionary<string, JsonElement> PieceData()
    {
        if (pieceData != null) return pieceData;
        pieceData = new Dictionary<string, JsonElement>();
        if (!FileAccess.FileExists(KitPaths.Pieces)) return pieceData;
        using var doc = JsonDocument.Parse(FileAccess.GetFileAsString(KitPaths.Pieces));
        foreach (var kv in doc.RootElement.EnumerateObject()) pieceData[kv.Name] = kv.Value.Clone();
        return pieceData;
    }

    /// <summary>a piece by name: the kit's (pieces.json), else <see cref="External"/>'s for names that are not the
    /// kit's ("SM_..."). Null: none.</summary>
    public PieceInfo Info(string name)
    {
        if (name == null) return null;
        if (infos.TryGetValue(name, out var info)) return info;
        if (PieceData().TryGetValue(name, out var pd))
        {
            info = new PieceInfo { name = name, scene = GD.Load<PackedScene>(pd.GetProperty("glb").GetString()) };
            if (pd.TryGetProperty("props", out var pp)) info.props = KitProps.FromJson(pp);
            if (pd.TryGetProperty("slot_map", out var sm))
            {
                int n = pd.TryGetProperty("surfaces", out var su) ? su.GetArrayLength() : 0;
                info.slots = Enumerable.Repeat(-1, n).ToArray();
                foreach (var kv in sm.EnumerateObject())
                {
                    int s = kv.Value.GetInt32();
                    if (s >= 0 && s < n) info.slots[s] = int.Parse(kv.Name);
                }
            }
            if (info.scene == null) info = null;
        }
        else if (!name.StartsWith("SM_") && External?.Invoke(name) is { } ext)
        {
            info = new PieceInfo { name = name, scene = ext };
            var probe = ext.Instantiate();
            if (probe is KitPiece kp) { info.props = kp.Props.Duplicate(); info.slots = kp.BlenderSlots; }
            probe.Free();
        }
        if (info != null && info.scene != null && info.box == null) info.box = MeshBox(info);
        infos[name] = info;
        return info;
    }

    public PackedScene Prefab(string name) => Info(name)?.scene;

    /// <summary>the box of a piece's mesh in Blender piece space (x0, y0, z0, x1, y1, z1), as Unity reads its prefab's
    /// MeshFilter: a kit piece's mesh (the glb's MeshInstance3D under its KitPiece root); a scene without one (a game's
    /// prefab), none. Godot (x, y, z) is Blender (x, -z, y).</summary>
    static float[] MeshBox(PieceInfo info)
    {
        var inst = info.scene.Instantiate();
        try
        {
            var mi = inst is KitPiece kp ? kp.MeshInstance : null;
            if (mi?.Mesh == null) return null;
            var b = mi.Transform * mi.Mesh.GetAabb();
            return new[] { b.Position.X, -b.End.Z, b.Position.Y, b.End.X, -b.Position.Z, b.End.Y };
        }
        finally { inst.Free(); }
    }

    readonly Dictionary<string, Material> mats = new();

    public Material Mat(string name)
    {
        if (name == null) return null;
        if (mats.TryGetValue(name, out var m)) return m;
        string path = KitPaths.Materials + name + ".tres";
        m = ResourceLoader.Exists(path) ? GD.Load<Material>(path) : null;
        mats[name] = m;
        return m;
    }

    /// <summary>vki_style_mat: a style key + value (e.g. wall_a = PlasterCream) -> its material name; values may also be
    /// material names ("M_...").</summary>
    public string StyleMatName(string key, string value)
    {
        if (value == null) return null;
        if (value.StartsWith("M_")) return value;
        return Json["styles"]?[key]?[value].S();
    }

    /// <summary>vki_rooms_put's piece names: "Torch_Wall" -> "SM_VKI_Torch_Wall", full names unchanged.</summary>
    public static string Full(string piece) => piece.StartsWith("SM_") ? piece : "SM_VKI_" + piece;
}
