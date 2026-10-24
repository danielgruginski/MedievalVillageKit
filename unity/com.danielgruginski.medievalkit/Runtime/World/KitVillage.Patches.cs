using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
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
        /// yard read as cow print); the grass thins on a
        /// patch. Its own random stream: the rest of the map stays where it was.
        /// </summary>
        void Patches()
        {
            var list = L["patches"] as JArray;
            if (list == null || list.Count == 0 || ControlMap == null) return;
            var px = ControlMap.GetPixels();
            int tw = ControlMap.width, th = ControlMap.height;
            var road = px.Select(c => c.r).ToArray();                    // the roads and areas, before any patch
            var r = new System.Random(((int?)L["seed"] ?? 1) * 104729 + 17);
            float Rn() => (float)r.NextDouble();
            int k = 0;
            foreach (var p in list)
            {
                k++;
                string surface = (string)p["surface"] ?? "sand";
                int ch = surface == "dirt" ? 0 : surface == "cobble" ? 1 : 2;
                bool onRoads = (bool?)p["onRoads"] ?? false;
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
                if (p["spots"] is JArray spots)                                 // [[x, y, r]]: a burnt shed's ash, where a slab lay
                {
                    float strength = (float?)p["strength"] ?? 0.9f;
                    foreach (var e in spots.OfType<JArray>())
                    {
                        float rad = e.Count > 2 ? (float)e[2] : 2.5f;
                        Disc((float)e[0], (float)e[1], rad, strength, Mathf.Min(2f, rad * 0.6f));
                    }
                }
                else if (p["centre"] != null)                                   // a lumpy oval with a soft, noisy rim (a burnt
                {                                                               // edge of a wood, the ground round a burned farm)
                    var c = V(p["centre"]);
                    var rv = p["radius"] is JArray ? V(p["radius"]) : new Vector2((float?)p["radius"] ?? 10f, (float?)p["radius"] ?? 10f);
                    float lumps = (float?)p["lumps"] ?? 0.25f, edge = Mathf.Clamp((float?)p["edge"] ?? 0.2f, 0.02f, 0.9f), strength = (float?)p["strength"] ?? 0.9f;
                    float band = (float?)p["band"] ?? 0f;                     // > 0: only a rim this deep (of the radius): a singed
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
                else if (p["around"] is JArray around)
                {
                    var names = around.Select(a => (string)a).ToList();
                    float share = (float?)p["share"] ?? 1f, radius = (float?)p["radius"] ?? 1.2f;
                    var (lo, hi) = LoHi(p["strength"], 0.6f, 0.95f);
                    int rings = 0;
                    foreach (var t in natureT.Cast<Transform>().Concat(propT.Cast<Transform>()))
                    {
                        if (!names.Any(n => IsPiece(t.name, n))) continue;
                        if (Rn() >= share) continue;
                        float rad = radius * t.localScale.x * (0.6f + Rn() * 0.7f), peak = lo + Rn() * (hi - lo);
                        var lp = t.localPosition;
                        Disc(-lp.x, -lp.z, rad, peak, 1.4f);                     // plan space
                        rings++;
                    }
                    notes.Add($"patches: {rings} {surface} rings");
                }
                else
                {
                    float scale = (float?)p["scale"] ?? 15f, cover = Mathf.Clamp((float?)p["cover"] ?? 0.2f, 0.01f, 0.95f), strength = (float?)p["strength"] ?? 0.8f;
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
                    if (v > px[i][ch]) { var c = px[i]; c[ch] = v; px[i] = c; }
                }
            }
            ControlMap.SetPixels(px);
            ControlMap.Apply();
        }

        static float Fbm(float x, float y)
        {
            float s = 0f, a = 1f, n = 0f;
            for (int o = 0; o < 3; o++) { s += a * Mathf.PerlinNoise(x, y); n += a; x = x * 2.03f + 17.1f; y = y * 2.03f + 5.3f; a *= 0.5f; }
            return s / n;
        }

        static (float lo, float hi) LoHi(JToken t, float lo, float hi) =>
            t is JArray a && a.Count >= 2 ? ((float)a[0], (float)a[1]) : t != null && t.Type != JTokenType.Null ? ((float)t, (float)t) : (lo, hi);

        /// <summary>a placed piece's object by the layout's name for it (the prefab names <see cref="Prefab"/> tries)</summary>
        static bool IsPiece(string objectName, string piece)
        {
            string n = objectName.Replace("(Clone)", "").Trim();
            return n == piece || n == "SM_VK_" + piece || n == "SM_VKI_Prop_" + piece || n == "SM_VKI_" + piece;
        }

        /// <summary>material swaps for some pieces of the nature only (layout "pieceSwaps": [{pieces, swap}], 2026-10-24), and a
        /// forest zone's swap on all the nature inside its oval: a
        /// burnt wood's dead trees and stumps charred while the map's own timber -- a palisade, an orc's fresh-cut stumps
        /// (props) -- keeps its wood; a prop takes its own "swap" instead. After the map's palette, so its names are the
        /// palette's results.</summary>
        void PieceSwaps()
        {
            int zi = 0;                                                         // a forest zone's swap on all the nature well inside it
            foreach (var z in L["forest"]?["zones"] as JArray ?? new JArray())  // (the cliffs' lip plants and boulders too; the
            {                                                                   // forest's own pieces took it as they were placed)
                zi++;
                if (z["swap"] == null || z["centre"] == null || z["radius"] == null) continue;
                float core = 1f - Mathf.Clamp((float?)z["fade"] ?? 0.25f, 0.01f, 0.9f);   // not over the rim, where the map's
                foreach (Transform t in natureT)                                          // green trees mix in (their crowns
                {                                                                         // would go black)
                    var lp = t.localPosition;
                    if (Blob(new Vector2(-lp.x, -lp.z), V(z["centre"]), V(z["radius"]), (float?)z["lumps"] ?? 0.2f, 71 + 13 * zi) < core) Swap(t.gameObject, z);
                }
            }
            foreach (var e in L["pieceSwaps"] as JArray ?? new JArray())
            {
                var names = (e["pieces"] as JArray ?? new JArray()).Select(a => (string)a).ToList();
                foreach (Transform t in natureT)
                    if (names.Any(n => IsPiece(t.name, n))) Swap(t.gameObject, e);
            }
        }
    }
}
