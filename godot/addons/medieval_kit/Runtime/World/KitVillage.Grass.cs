using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;

namespace MedievalKit;

public partial class KitVillage
{
    /// <summary>the grass's material (the build saves it beside the ground)</summary>
    public ShaderMaterial GrassMaterialInstance { get; private set; }

    /// <summary>
    /// Grass blades over the grass (layout "grass": false turns it off; {spacing, height: [min, max], edge, shadows, tip}):
    /// a clump every `spacing` (0.5 m) on a jittered grid, thinning where the control map turns to dirt or paving, out at
    /// the clearing's edge (edge 1.12: a little into the forest) and on steep ground, never inside a building, prop, fence
    /// or tree; standing on the ground (or the terrain's tops and ramps, not its faces), taller in patches, darker in the
    /// forest's shade. Written as a clump list on a <see cref="KitGrass"/> beside the ground, which draws the blades.
    /// Godot: the heights come from <see cref="Height"/> and its slope (Unity casts rays at the ground's and the
    /// terrain's colliders). Unity: KitVillage.Grass.
    /// </summary>
    void Grass(ShaderMaterial groundMat)
    {
        var g = L["grass"];
        if (g != null && g.IsBool() && !g.B()) return;
        float spacing = g?["spacing"].Fq() ?? 0.5f, edge = g?["edge"].Fq() ?? 1.12f;
        if (ControlImage == null) { notes.Add("no ground for the grass"); return; }
        var shader = ResourceLoader.Exists(KitPaths.Shaders + "KitGrass.gdshader") ? GD.Load<Shader>(KitPaths.Shaders + "KitGrass.gdshader") : null;
        if (shader == null) { notes.Add("no KitGrass shader: no grass"); return; }

        GrassMaterialInstance = new ShaderMaterial { Shader = shader, ResourceName = $"{Name}_Grass" };
        if (groundMat != null)
            foreach (var t in new[] { "grass_map", "macro_map", "grass_sat" })
            {
                var v = groundMat.GetShaderParameter(t);
                if (v.VariantType != Variant.Type.Nil) GrassMaterialInstance.SetShaderParameter(t, v);
            }
        if (g?["tip"] is JsonArray tip && tip.Count >= 3)                  // the blades' tip tint (a burnt land's: dull straw)
            GrassMaterialInstance.SetShaderParameter("tip_color", new Color(tip[0].F(), tip[1].F(), tip[2].F(), 1f));

        // what stands on the ground (buildings, props, fences, trees), with bounds for a quick test
        var blocked = occupied.Select(o => (poly: o.poly, min: new Vector2(o.poly.Min(p => p.x), o.poly.Min(p => p.y)),
                                            max: new Vector2(o.poly.Max(p => p.x), o.poly.Max(p => p.y)))).ToList();
        var ctl = ReadControl();
        int tw = ControlImage.GetWidth(), th = ControlImage.GetHeight();
        float Ctl(Vector2 q, int ch)
        {
            int i = Mathf.Clamp(Mathf.FloorToInt((q.x + M) * CtlPerM), 0, tw - 1), j = Mathf.Clamp(Mathf.FloorToInt((q.y + M) * CtlPerM), 0, th - 1);
            var c = ctl[j * tw + i];
            return ch == 0 ? c.R : ch == 1 ? c.G : c.B;
        }
        // the ground's slope at q: the up component of its normal, from Height's differences 0.25 m either side
        float Up(Vector2 q)
        {
            const float e = 0.25f;
            float gx = (Height(q + new Vector2(e, 0)) - Height(q - new Vector2(e, 0))) / (2 * e), gy = (Height(q + new Vector2(0, e)) - Height(q - new Vector2(0, e))) / (2 * e);
            return 1f / Mathf.Sqrt(1f + gx * gx + gy * gy);
        }
        int seed = (L["seed"].Iq() ?? 1) * 7919 + 11;
        var r = new System.Random(seed);
        float Rn() => (float)r.NextDouble();
        var origin = Local(-M, -M, 0f);                 // the ground object's place: clump positions are relative to it
        var data = new List<byte>();
        Godot.Vector3 lo = Godot.Vector3.Inf, hi = -Godot.Vector3.Inf;
        int nx = Mathf.CeilToInt((W + 8f) / spacing), ny = Mathf.CeilToInt((H + 8f) / spacing), clumps = 0;
        for (int j = 0; j < ny; j++)
            for (int i = 0; i < nx; i++)
            {
                var q = new Vector2(-4f + (i + Rn()) * spacing, -4f + (j + Rn()) * spacing);
                float c = Clearing(q);
                if (c > edge + 0.04f) continue;
                float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(edge - 0.08f, edge + 0.04f, c));
                w *= 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.12f, 0.5f, Mathf.Max(Mathf.Max(Ctl(q, 0), Ctl(q, 1) * 1.5f), Ctl(q, 2))));
                if (w <= 0.02f || Rn() > w) continue;
                if (blocked.Any(b => q.x >= b.min.x && q.y >= b.min.y && q.x <= b.max.x && q.y <= b.max.y && InPoly(q, b.poly))) continue;
                if (OnStair(q)) continue;                                             // a terrain's flight of stairs
                if (SeaDist(q) < 0.8f) continue;                                      // the sea, its quays' coping, its shore
                bool ramp = HasTerrain && OnRampTile(q);
                if (HasTerrain && NearCliff(q, 0.6f) && !ramp) continue;            // the faces carry no grass, the tops and ramps do
                if (Up(q) < (ramp ? 0.7f : 0.82f)) continue;                          // too steep
                var root = Local(q.x, q.y, Height(q)) - origin;
                float shade = Mathf.Lerp(1f, 0.82f, Mathf.InverseLerp(1.0f, 1.25f, c));
                float tall = Mathf.InverseLerp(0.6f, 1.25f, Mathf.Lerp(0.75f, 1.2f, Noise(q.x, q.y, 6f)) * Mathf.Lerp(0.8f, 1f, w));
                var tint = new Color(shade * (0.94f + 0.12f * Rn()), shade * (0.95f + 0.1f * Rn()), shade * (0.9f + 0.15f * Rn()));
                KitGrass.Write(data, root, tint, tall);
                lo = lo.Min(root); hi = hi.Max(root);
                clumps++;
            }
        if (clumps == 0) return;
        var kg = new KitGrass { Name = "Grass", Position = origin };
        kg.material = GrassMaterialInstance;
        kg.seed = seed;
        kg.minHeight = g?["height"]?[0].Fq() ?? 0.3f; kg.maxHeight = g?["height"]?[1].Fq() ?? 0.58f;
        kg.castShadows = g?["shadows"].Bq() ?? true;
        kg.clumps = data.ToArray();
        kg.localBounds = new Aabb(lo - new Godot.Vector3(0.5f, 0f, 0.5f), hi - lo + new Godot.Vector3(1f, 1.5f, 1f));
        groundT.AddChild(kg);
        kg.Owner = SceneOwner;
        notes.Add($"grass: {clumps} clumps ({data.Count / 1024} KB)");
    }
}
