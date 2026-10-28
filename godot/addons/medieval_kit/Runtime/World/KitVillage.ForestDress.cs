using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;
using Rect = MedievalKit.UnityMath.Rect;

namespace MedievalKit;

// 2026-10-24 (a burnt wood read as black poles planted on a grid): the forest's own dressing, all optional keys of
// "forest" --
//   "clumps": {scale, gaps}      glades: about `gaps` of the forest's spots left open in noise `scale` m across
//                                (the undergrowth fills them); the edges ragged
//   "lean": {pieces, share, max} a `share` of those pieces leaning up to `max` degrees (sunk a little at the foot)
//   "fallen": {pieces, share, length, as}
//                                a `share` of those pieces beyond the clearing's wall lying on the ground, laid along
//                                its slope (`length`, 5 m: the trunk's, checked for a cliff), their roots up; the
//                                trunk's capsule turns with them; with "as" that piece instead (modelled lying along
//                                +X, root end at -X: Prop_BurntLog), its middle half a length out from the foot
//   "zones": [{centre, radius, lumps, fade, species, undergrowth, scatter, swap}]
//                                a region of the map with its own pieces (a burnt edge of a green wood): inside its
//                                lumpy oval its lists replace the map's (a list it leaves out keeps the map's), over
//                                its rim (`fade` of the radius, 0.25) the two mix, and what it places takes its swap
// Their draws come from a stream of their own, and a glade's spot still draws what a tree would have: a map without
// these keys builds as before, and one with them keeps its other trees where they were. Unity: KitVillage.ForestDress.cs.
public partial class KitVillage
{
    System.Random rz;
    System.Random Rz => rz ??= new System.Random((L["seed"].Iq() ?? 1) * 7919 + 101);

    JsonArray ForestZones() => L["forest"] is JsonObject f && f["zones"] is JsonArray zs ? zs : new JsonArray();

    /// <summary>the zone's list for this spot (and the zone, for its swap), or the map's</summary>
    (List<(string piece, float w)> list, JsonNode zone) InZone(Vector2 q, List<(string piece, float w)> list, string key)
    {
        int i = 0;
        foreach (var z in ForestZones())
        {
            i++;
            var zl = Weights(z[key]);
            if (zl.Count == 0 || z["centre"] == null || z["radius"] == null) continue;
            float b = Blob(q, V(z["centre"]), Radius(z["radius"], 10f), z["lumps"].Fq() ?? 0.2f, 71 + 13 * i);
            float fade = Mathf.Clamp(z["fade"].Fq() ?? 0.25f, 0.01f, 0.9f);
            float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1f - fade, 1f + fade, b));
            if (w <= 0f) continue;
            if (w >= 1f || Rz.NextDouble() < w) return (zl, z);
        }
        return (list, null);
    }

    /// <summary>the glades among the forest's spots (forest "clumps"): true where a tree is left out</summary>
    Func<Vector2, bool> Glades(JsonNode c, List<Vector2> spots)
    {
        if (c is not JsonObject || spots.Count == 0) return _ => false;
        float scale = Mathf.Max(2f, c["scale"].Fq() ?? 16f), gaps = Mathf.Clamp(c["gaps"].Fq() ?? 0.3f, 0f, 0.9f);
        float N(Vector2 q) => Fbm(q.x / scale + 61.3f, q.y / scale + 17.9f);
        var s = spots.Select(N).OrderBy(x => x).ToList();
        float under = s[Mathf.Clamp(Mathf.RoundToInt(gaps * (s.Count - 1)), 0, s.Count - 1)];
        return q => { float n = N(q); return n < under - 0.03f || (n < under + 0.03f && Rz.NextDouble() < 0.5); };
    }

    /// <summary>a placed tree leaning or lying (forest "lean", "fallen"): turned about the level line across the way it
    /// falls, its foot staying put</summary>
    void Fell(Node3D go, string piece, Vector2 q, float scale, bool mayLie)
    {
        if (go == null || L["forest"] is not JsonObject f) return;
        bool Named(JsonNode t) => t is JsonObject o && o["pieces"] is JsonArray a && a.Any(x => x.S() == piece);
        // turned deg about the level line across dir: its top goes towards dir (Godot's right-handed turn about up x dir)
        static Basis Across(Vector2 dir, float deg) =>
            new(Godot.Vector3.Up.Cross(Local(dir.x, dir.y, 0f).Normalized()).Normalized(), deg * Mathf.Deg2Rad);
        var fall = f["fallen"];
        if (mayLie && Named(fall) && Rz.NextDouble() < (fall["share"].Fq() ?? 0.1f))
        {
            float len = (fall["length"].Fq() ?? 5f) * scale, h0 = Height(q);
            float yaw0 = (float)Rz.NextDouble() * 360f;
            string lay = fall["as"].S();                                  // a piece modelled lying along +X (a fallen trunk)
            for (int k = 0; k < 4; k++)                                   // the first way with no cliff or steep ground under it
            {
                var dir = Rot(Vector2.right, yaw0 + 90f * k);
                float h1 = Height(q + dir * len);
                bool ok = Mathf.Abs(h1 - h0) < 1.5f && Clearing(q + dir * len) > (f["wallAt"].Fq() ?? 1.08f);   // its crown
                                                                          // end beyond the wall too: never across a path
                for (float s = 1f; ok && s <= len; s += 1f) ok = !NearCliff(q + dir * s, 0.8f);
                if (!ok) continue;
                float slope = Mathf.Atan2(h1 - h0, len) * Mathf.Rad2Deg;
                if (!string.IsNullOrEmpty(lay) && Prefab(lay) != null)    // the standing tree swapped for it: its root end
                {                                                         // at the foot, its crown end along dir
                    var log = Place(natureT, lay, q + dir * len * 0.5f, Ang(dir), scale);
                    if (log == null) return;
                    log.Basis = Across(dir, -slope) * log.Basis;          // its crown end up the slope
                    log.Position = Local(q.x + dir.x * len * 0.5f, q.y + dir.y * len * 0.5f, (h0 + h1) * 0.5f - 0.05f);
                    KitSolid.Nature(log, SceneOwner);
                    go.GetParent()?.RemoveChild(go);                      // freed at the frame's end: the caller may still
                    go.QueueFree();                                       // swap its materials
                    return;
                }
                go.Basis = Across(dir, 90f - slope - (float)Rz.NextDouble() * 4f) * go.Basis;
                go.Position += Godot.Vector3.Up * 0.22f * scale;          // its trunk on the ground, not half in it
                return;
            }
        }
        var lean = f["lean"];
        if (Named(lean) && Rz.NextDouble() < (lean["share"].Fq() ?? 0.4f))
        {
            float deg = (float)Rz.NextDouble() * (lean["max"].Fq() ?? 14f);
            go.Basis = Across(Rot(Vector2.right, (float)Rz.NextDouble() * 360f), deg) * go.Basis;
            go.Position -= Godot.Vector3.Up * Mathf.Sin(deg * Mathf.Deg2Rad) * 0.6f * scale;   // its roots' high side in the ground
        }
    }
}
