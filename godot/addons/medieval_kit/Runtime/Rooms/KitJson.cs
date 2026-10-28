using System;
using System.Globalization;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace MedievalKit;

/// <summary>
/// The room records and rules are JSON (System.Text.Json.Nodes here; Unity's kit uses Newtonsoft's JObject). These read a
/// node the way Newtonsoft's casts do -- a number made in memory (a float or a double) reads as either, an int from a
/// fractional number rounds to even, a missing node is null for the nullable reads -- and add nodes the way JArray.Add
/// does: a node that already has a parent goes in as a copy (System.Text.Json throws instead).
/// </summary>
public static class KitJson
{
    static readonly JsonDocumentOptions Lenient = new() { AllowTrailingCommas = true, CommentHandling = JsonCommentHandling.Skip };
    static readonly JsonSerializerOptions Indented = new() { WriteIndented = true, Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
    static readonly JsonSerializerOptions Compact = new() { WriteIndented = false, Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping };

    public static JsonNode Parse(string text) => JsonNode.Parse(text, null, Lenient);

    /// <summary>a JSON object from text; empty or blank text: an empty object</summary>
    public static JsonObject ParseObject(string text) =>
        string.IsNullOrWhiteSpace(text) ? new JsonObject() : (JsonObject)Parse(text);

    public static string Text(JsonNode n, bool indented = true) => n?.ToJsonString(indented ? Indented : Compact) ?? "null";

    /// <summary>a value as a node: nodes as they are (a copy when they already have a parent), numbers, strings, bools</summary>
    public static JsonNode V(object v) => v switch
    {
        null => null,
        JsonNode n => n.Parent != null ? n.DeepClone() : n,
        string s => JsonValue.Create(s),
        float f => JsonValue.Create(f),
        double d => JsonValue.Create(d),
        int i => JsonValue.Create(i),
        long l => JsonValue.Create(l),
        bool b => JsonValue.Create(b),
        _ => throw new ArgumentException($"KitJson.V: {v.GetType().Name}"),
    };

    /// <summary>Newtonsoft's new JArray(a, b, ...): each item a value or a node (nested, not spread)</summary>
    public static JsonArray A(params object[] items)
    {
        var a = new JsonArray();
        foreach (var it in items) a.Add(V(it));
        return a;
    }

    /// <summary>JArray.Add: a node that has a parent goes in as a copy</summary>
    public static void Push(this JsonArray a, object v) => a.Add(V(v));

    public static JsonValueKind Kind(this JsonNode n) => n == null ? JsonValueKind.Null : n.GetValueKind();
    public static bool IsStr(this JsonNode n) => n is JsonValue && n.GetValueKind() == JsonValueKind.String;
    public static bool IsBool(this JsonNode n) => n is JsonValue && n.GetValueKind() is JsonValueKind.True or JsonValueKind.False;
    public static int Len(this JsonNode n) => n is JsonArray a ? a.Count : n is JsonObject o ? o.Count : 0;
    public static JsonObject Obj(this JsonNode n) => n as JsonObject;
    public static JsonArray Arr(this JsonNode n) => n as JsonArray;

    static double Num(JsonNode n)
    {
        if (n is not JsonValue v) throw new InvalidCastException($"not a value: {n?.ToJsonString() ?? "null"}");
        if (v.TryGetValue(out double d)) return d;
        if (v.TryGetValue(out float f)) return f;
        if (v.TryGetValue(out int i)) return i;
        if (v.TryGetValue(out long l)) return l;
        if (v.TryGetValue(out decimal m)) return (double)m;
        if (v.TryGetValue(out bool b)) return b ? 1 : 0;
        if (v.TryGetValue(out string s)) return double.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture);
        if (v.TryGetValue(out JsonElement e) && e.ValueKind == JsonValueKind.Number) return e.GetDouble();
        throw new InvalidCastException($"not a number: {v.ToJsonString()}");
    }

    static bool Missing(JsonNode n) => n == null || (n is JsonValue && n.GetValueKind() == JsonValueKind.Null);

    public static double D(this JsonNode n) => Num(n);
    public static float F(this JsonNode n) => (float)Num(n);
    public static int I(this JsonNode n)
    {
        if (n is JsonValue v && v.TryGetValue(out int i)) return i;
        if (n is JsonValue v2 && v2.TryGetValue(out long l)) return checked((int)l);
        return Convert.ToInt32(Num(n));                  // Newtonsoft: a fractional number rounds to even
    }
    public static bool B(this JsonNode n)
    {
        if (n is JsonValue v && v.TryGetValue(out bool b)) return b;
        if (n is JsonValue s && s.TryGetValue(out string t)) return bool.Parse(t);
        return Num(n) != 0;
    }

    public static float? Fq(this JsonNode n) => Missing(n) ? null : n.F();
    public static double? Dq(this JsonNode n) => Missing(n) ? null : n.D();
    public static int? Iq(this JsonNode n) => Missing(n) ? null : n.I();
    public static bool? Bq(this JsonNode n) => Missing(n) ? null : n.B();

    /// <summary>Newtonsoft's (string) cast: null for a missing node, a number's or bool's text otherwise</summary>
    public static string S(this JsonNode n)
    {
        if (Missing(n)) return null;
        if (n is JsonValue v && v.TryGetValue(out string s)) return s;
        if (n is JsonValue b && b.TryGetValue(out bool bv)) return bv ? "True" : "False";
        if (n is JsonValue) return Num(n).ToString(CultureInfo.InvariantCulture);
        return n.ToJsonString(Compact);
    }
}
