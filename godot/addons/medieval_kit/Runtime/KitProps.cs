using System.Globalization;
using System.Text.Json;
using Godot;
using Props = Godot.Collections.Dictionary<string, string>;

namespace MedievalKit;

/// <summary>Blender custom properties (vki_* and friends), kept as text: JSON values stay JSON strings. Every kit
/// node carries them as an exported Props dictionary (Unity: KitPropsBehaviour).</summary>
public static class KitProps
{
    public static string Get(this Props p, string key, string fallback = null) =>
        p != null && p.TryGetValue(key, out var v) ? v : fallback;

    public static bool Has(this Props p, string key) => p != null && p.ContainsKey(key);

    public static float GetFloat(this Props p, string key, float fallback = 0f) =>
        float.TryParse(p.Get(key), NumberStyles.Float, CultureInfo.InvariantCulture, out var v) ? v : fallback;

    /// <summary>A JSON object of Blender properties (a layout's "props") -> text values.</summary>
    public static Props FromJson(JsonElement o)
    {
        var p = new Props();
        if (o.ValueKind != JsonValueKind.Object) return p;
        foreach (var kv in o.EnumerateObject())
            p[kv.Name] = kv.Value.ValueKind == JsonValueKind.String ? kv.Value.GetString() : kv.Value.GetRawText();
        return p;
    }

    /// <summary>glTF extras as Godot imports them (node meta "extras") -> text values.</summary>
    public static Props FromVariant(Godot.Collections.Dictionary extras)
    {
        var p = new Props();
        if (extras == null) return p;
        foreach (var kv in extras)
            p[kv.Key.AsString()] = kv.Value.VariantType == Variant.Type.String ? kv.Value.AsString() : Json.Stringify(kv.Value);
        return p;
    }
}
