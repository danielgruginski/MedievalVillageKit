using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;
using Rect = MedievalKit.UnityMath.Rect;

namespace MedievalKit;

/// <summary>Ground patches painted into the control map, and material swaps on some of the nature's pieces. Unity:
/// KitVillage.Patches.cs.</summary>
public partial class KitVillage
{
    /// <summary>
    /// Patches of another ground painted into the control map once the nature stands (layout "patches": [{surface, scale,
    /// cover, strength} or {surface, around, share, radius, strength} or {surface, spots: [[x, y, r]], strength} or
    /// {surface, centre, radius, lumps, edge, band, strength}]; 2026-10-24, a burnt land's ash and scorched earth:
    /// its grass ground read as one flat grey). "surface" is the layer: "sand" (B) or "cobble" (G), whose looks the map's
    /// ground material gives (the burnt maps: pale ash and fire-baked earth), or "dirt" (R). Without "around": noise
    /// patches about "scale" m across over about "cover" of the map, "strength" (0.8) at their heart. With "around" (piece
    /// names, as the layout names them): a ragged ring under a "share" (1) of those pieces in the nature and the props,
    /// "radius" m (1.2, times the piece's scale, varied), its strength drawn from "strength" [lo, hi] -- under the shader's
    /// threshold (0.5) a ring breaks up or is gone. "spots": ragged discs `r` m (2.5) where the layout says (a burnt
    /// shed's ash, in place of the old flat ash slab). "centre": a lumpy oval as the areas' (`lumps`), its rim soft and
    /// broken by noise over `edge` of its radius (0.2) -- unlike an area it keeps nothing off it (a burnt edge running
    /// into a wood); with `band` only its rim that deep (a singed fringe: the dirt layer over a burn's edge). Roads and
    /// trodden areas stay clear unless the patch says "onRoads" (a scorched yard round its fires; noise patches over a
    /// yard read as cow print); the grass thins on a patch. Its own random stream: the rest of the map stays where it was.
    /// </summary>
    void Patches()
    {
        var list = L["patches"] as JsonArray;
        if (list == null || list.Count == 0 || ControlImage == null) return;
        var px = ReadControl();
        int tw = ControlImage.GetWidth(), th = ControlImage.GetHeight();
        var road = px.Select(c => c.R).ToArray();                    // the roads and areas, before any patch
        var r = new System.Random((L["seed"].Iq() ?? 1) * 104729 + 17);
        float Rn() => (float)r.NextDouble();
        int k = 0;
        foreach (var p in list)
        {
            k++;
            string surface = p["surface"].S() ?? "sand";
            int ch = surface == "dirt" ? 0 : surface == "cobble" ? 1 : 2;
            bool onRoads = p["onRoads"].Bq() ?? false;
            var add = new float[tw * th];
            // a ragged disc of `rad` m at (cx, cy) in plan space, `peak` at its heart, its edge broken by `jag` m of noise
            void Disc(float cx, float cy, float rad, float peak, float jag)
            {
                int ci = Mathf.RoundToInt((cx + M) * CtlPerM), cj = Mathf.RoundToInt((cy + M) * CtlPerM), rr = Mathf.CeilToInt((rad * 1.6f + jag) * CtlPerM);
                for (int j = Mathf.Max(0, cj - rr); j < Mathf.Min(th, cj + rr); j++)
                    for (int i = Mathf.Max(0, ci - rr); i < Mathf.Min(tw, ci + rr); i++)
                    {
                        float x = (i + 0.5f) / CtlPerM - M, y = (j + 0.5f) / CtlPerM - M;
                        float d = Mathf.Sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) + (Mathf.PerlinNoise(x * 1.7f + 9f + k, y * 1.7f + 4f) - 0.5f) * jag;
                        float v = (1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0f, rad, d))) * peak;
                        if (v > add[j * tw + i]) add[j * tw + i] = v;
                    }
            }
            if (p["spots"] is JsonArray spots)                              // [[x, y, r]]: a burnt shed's ash, where a slab lay
            {
                float strength = p["strength"].Fq() ?? 0.9f;
                foreach (var e in spots.OfType<JsonArray>())
                {
                    if (e.Count < 2) continue;
                    float rad = e.Count > 2 ? e[2].F() : 2.5f;
                    Disc(e[0].F(), e[1].F(), rad, strength, Mathf.Min(2f, rad * 0.6f));
                }
            }
            else if (p["centre"] != null)                                   // a lumpy oval with a soft, noisy rim (a burnt
            {                                                               // edge of a wood, the ground round a burned farm)
                var c = V(p["centre"]);
                var rv = Radius(p["radius"], 10f);
                float lumps = p["lumps"].Fq() ?? 0.25f, edge = Mathf.Clamp(p["edge"].Fq() ?? 0.2f, 0.02f, 0.9f), strength = p["strength"].Fq() ?? 0.9f;
                float band = p["band"].Fq() ?? 0f;                          // > 0: only a rim this deep (of the radius): a singed
                                                                            // fringe round a burn painted with its own oval
                float reach = Mathf.Max(rv.x, rv.y) * (1f + lumps) * (1f + edge) + 2f;
                int i0 = Mathf.Max(0, Mathf.FloorToInt((c.x - reach + M) * CtlPerM)), i1 = Mathf.Min(tw, Mathf.CeilToInt((c.x + reach + M) * CtlPerM));
                int j0 = Mathf.Max(0, Mathf.FloorToInt((c.y - reach + M) * CtlPerM)), j1 = Mathf.Min(th, Mathf.CeilToInt((c.y + reach + M) * CtlPerM));
                for (int j = j0; j < j1; j++)
                    for (int i = i0; i < i1; i++)
                    {
                        float x = (i + 0.5f) / CtlPerM - M, y = (j + 0.5f) / CtlPerM - M;
                        float b = Blob(new Vector2(x, y), c, rv, lumps, 91 + k) + (Fbm(x / 5f + 3.3f * k, y / 5f + 1.7f) - 0.5f) * edge;
                        float v = (1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1f - edge, 1f + edge * 0.5f, b))) * strength;
                        if (band > 0f) v *= Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1f - band - edge * 0.5f, 1f - band + edge * 0.5f, b));
                        add[j * tw + i] = v;
                    }
            }
            else if (p["around"] is JsonArray around)
            {
                var names = around.Select(a => a.S()).Where(a => a != null).ToList();
                float share = p["share"].Fq() ?? 1f, radius = p["radius"].Fq() ?? 1.2f;
                var (lo, hi) = LoHi(p["strength"], 0.6f, 0.95f);
                int rings = 0;
                foreach (var t in KitNodes.Children(natureT).Concat(KitNodes.Children(propT)).OfType<Node3D>())
                {
                    string pn = PieceName(t);
                    if (!names.Any(n => IsPiece(pn, n))) continue;
                    if (Rn() >= share) continue;
                    float rad = radius * t.Scale.X * (0.6f + Rn() * 0.7f), peak = lo + Rn() * (hi - lo);
                    var at = Plan(t.Position);                              // the groups stand at the village's origin
                    Disc(at.x, at.y, rad, peak, 1.4f);
                    rings++;
                }
                notes.Add($"patches: {rings} {surface} rings");
            }
            else
            {
                float scale = p["scale"].Fq() ?? 15f, cover = Mathf.Clamp(p["cover"].Fq() ?? 0.2f, 0.01f, 0.95f), strength = p["strength"].Fq() ?? 0.8f;
                float ox = 13.7f * k + 3.1f, oy = 7.9f * k + 7.7f;
                float N(float x, float y) => Fbm(x / scale + ox, y / scale + oy);
                // where the patches start: the noise's level that leaves `cover` of the map above it (sampled every 2 m)
                var s = new List<float>();
                for (float y = 0; y < H; y += 2f) for (float x = 0; x < W; x += 2f) s.Add(N(x, y));
                s.Sort();
                float from = s[Mathf.Clamp(Mathf.RoundToInt((1f - cover) * (s.Count - 1)), 0, s.Count - 1)] - 0.04f;
                for (int j = 0; j < th; j++)
                    for (int i = 0; i < tw; i++)
                    {
                        float x = (i + 0.5f) / CtlPerM - M, y = (j + 0.5f) / CtlPerM - M;
                        add[j * tw + i] = Mathf.Clamp01(Mathf.InverseLerp(from, from + 0.18f, N(x, y))) * strength;   // a wide ramp: the
                    }                                                                                                   // height blend frays its edge
            }
            for (int i = 0; i < px.Length; i++)
            {
                float v = ch == 0 || onRoads ? add[i] : add[i] * (1f - 0.8f * road[i]);
                if (v > Channel(px[i], ch)) px[i] = WithChannel(px[i], ch, v);
            }
        }
        WriteControl(px, tw, th);
    }

    static float Channel(Color c, int ch) => ch == 0 ? c.R : ch == 1 ? c.G : ch == 2 ? c.B : c.A;

    static Color WithChannel(Color c, int ch, float v)
    {
        switch (ch)
        {
            case 0: c.R = v; break;
            case 1: c.G = v; break;
            case 2: c.B = v; break;
            default: c.A = v; break;
        }
        return c;
    }

    static float Fbm(float x, float y)
    {
        float s = 0f, a = 1f, n = 0f;
        for (int o = 0; o < 3; o++) { s += a * Mathf.PerlinNoise(x, y); n += a; x = x * 2.03f + 17.1f; y = y * 2.03f + 5.3f; a *= 0.5f; }
        return s / n;
    }

    static (float lo, float hi) LoHi(JsonNode t, float lo, float hi) =>
        t is JsonArray a && a.Count >= 2 ? (a[0].F(), a[1].F()) : t.Fq() is float f ? (f, f) : (lo, hi);

    /// <summary>a placed piece's kit name (its KitPiece's), else its node's name (Godot numbers a repeated name)</summary>
    static string PieceName(Node n) => n is KitPiece kp && !string.IsNullOrEmpty(kp.Piece) ? kp.Piece : n.Name.ToString();

    /// <summary>a placed piece by the layout's name for it (the prefab names <see cref="Prefab"/> tries)</summary>
    static bool IsPiece(string objectName, string piece)
    {
        string n = objectName.Trim();
        return n == piece || n == "SM_VK_" + piece || n == "SM_VKI_Prop_" + piece || n == "SM_VKI_" + piece;
    }

    /// <summary>material swaps for some pieces of the nature only (layout "pieceSwaps": [{pieces, swap}], 2026-10-24), and a
    /// forest zone's swap on all the nature inside its oval: a burnt wood's dead trees and stumps charred while the map's
    /// own timber -- a palisade, an orc's fresh-cut stumps (props) -- keeps its wood; a prop takes its own "swap" instead.
    /// After the map's palette, so its names are the palette's results.</summary>
    void PieceSwaps()
    {
        int zi = 0;                                                         // a forest zone's swap on all the nature well inside it
        foreach (var z in L["forest"] is JsonObject fo && fo["zones"] is JsonArray zs ? zs : new JsonArray())
        {                                                                   // (the cliffs' lip plants and boulders too; the
            zi++;                                                           // forest's own pieces took it as they were placed)
            if (z["swap"] == null || z["centre"] == null || z["radius"] == null) continue;
            float core = 1f - Mathf.Clamp(z["fade"].Fq() ?? 0.25f, 0.01f, 0.9f);   // not over the rim, where the map's
            var c = V(z["centre"]); var rad = Radius(z["radius"], 10f);              // green trees mix in (their crowns
            float lumps = z["lumps"].Fq() ?? 0.2f;                                   // would go black)
            foreach (var t in KitNodes.Children(natureT).OfType<Node3D>().ToList())
                if (Blob(Plan(t.Position), c, rad, lumps, 71 + 13 * zi) < core) Swap(t, z);
        }
        foreach (var e in L["pieceSwaps"] as JsonArray ?? new JsonArray())
        {
            var names = (e["pieces"] as JsonArray ?? new JsonArray()).Select(a => a.S()).Where(a => a != null).ToList();
            foreach (var t in KitNodes.Children(natureT).OfType<Node3D>().ToList())
                if (names.Any(n => IsPiece(PieceName(t), n))) Swap(t, e);
        }
    }
}
