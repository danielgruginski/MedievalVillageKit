using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    public partial class KitVillage
    {
        /// <summary>the grass's material (the editor saves it beside the ground)</summary>
        public Material GrassMaterialInstance { get; private set; }

        /// <summary>
        /// Grass blades over the grass (layout "grass": false turns it off; {spacing, height: [min, max], edge, shadows}):
        /// a clump every `spacing` (0.5 m) on a jittered grid, thinning where the control map turns to dirt or paving, out
        /// at the clearing's edge (edge 1.12: a little into the forest) and on steep ground, never inside a building, prop,
        /// fence or tree; standing on the ground mesh itself, taller in patches, darker in the forest's shade. Written as
        /// a clump list on a <see cref="KitGrass"/> beside the ground, which culls and draws the blades on the GPU.
        /// </summary>
        void Grass(Material groundMat)
        {
            var g = L["grass"];
            if (g != null && g.Type == JTokenType.Boolean && !(bool)g) return;
            var shader = Shader.Find("MedievalKit/KitGrass");
            if (shader == null) { notes.Add("no KitGrass shader: no grass"); return; }
            float spacing = (float?)g?["spacing"] ?? 0.5f, edge = (float?)g?["edge"] ?? 1.12f;
            var ground = groundT.GetComponentInChildren<MeshCollider>();
            if (ground == null || ControlMap == null) { notes.Add("no ground for the grass"); return; }
            Physics.SyncTransforms();

            GrassMaterialInstance = new Material(shader) { name = $"{name}_Grass" };
            if (groundMat != null)
                foreach (var t in new[] { "_GrassMap", "_MacroMap" })
                    if (groundMat.HasProperty(t)) GrassMaterialInstance.SetTexture(t, groundMat.GetTexture(t));

            // what stands on the ground (buildings, props, fences, trees), with bounds for a quick test
            var blocked = occupied.Select(o => (poly: o.poly, min: new Vector2(o.poly.Min(p => p.x), o.poly.Min(p => p.y)),
                                                max: new Vector2(o.poly.Max(p => p.x), o.poly.Max(p => p.y)))).ToList();
            var ctl = ControlMap.GetPixels();
            int tw = ControlMap.width, th = ControlMap.height;
            float Ctl(Vector2 q, int ch)
            {
                int i = Mathf.Clamp(Mathf.FloorToInt((q.x + M) * CtlPerM), 0, tw - 1), j = Mathf.Clamp(Mathf.FloorToInt((q.y + M) * CtlPerM), 0, th - 1);
                return ctl[j * tw + i][ch];
            }
            int seed = ((int?)L["seed"] ?? 1) * 7919 + 11;
            var r = new System.Random(seed);
            float Rn() => (float)r.NextDouble();
            var origin = Local(-M, -M, 0f);                 // the ground object's place: clump positions are relative to it
            var data = new List<byte>();
            Vector3 lo = Vector3.positiveInfinity, hi = Vector3.negativeInfinity;
            int nx = Mathf.CeilToInt((W + 8f) / spacing), ny = Mathf.CeilToInt((H + 8f) / spacing), clumps = 0;
            for (int j = 0; j < ny; j++)
                for (int i = 0; i < nx; i++)
                {
                    var q = new Vector2(-4f + (i + Rn()) * spacing, -4f + (j + Rn()) * spacing);
                    float c = Clearing(q);
                    if (c > edge + 0.04f) continue;
                    float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(edge - 0.08f, edge + 0.04f, c));
                    w *= 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.12f, 0.5f, Mathf.Max(Ctl(q, 0), Ctl(q, 1) * 1.5f)));
                    if (w <= 0.02f || Rn() > w) continue;
                    if (blocked.Any(b => q.x >= b.min.x && q.y >= b.min.y && q.x <= b.max.x && q.y <= b.max.y && InPoly(q, b.poly))) continue;
                    var top = transform.TransformPoint(Local(q.x, q.y, 50f));
                    if (!ground.Raycast(new Ray(top, -transform.up), out var hit, 200f)) continue;
                    if (Vector3.Dot(hit.normal, transform.up) < 0.82f) continue;          // too steep
                    var root = transform.InverseTransformPoint(hit.point) - origin;
                    float shade = Mathf.Lerp(1f, 0.82f, Mathf.InverseLerp(1.0f, 1.25f, c));
                    float tall = Mathf.InverseLerp(0.6f, 1.25f, Mathf.Lerp(0.75f, 1.2f, Noise(q.x, q.y, 6f)) * Mathf.Lerp(0.8f, 1f, w));
                    var tint = new Color(shade * (0.94f + 0.12f * Rn()), shade * (0.95f + 0.1f * Rn()), shade * (0.9f + 0.15f * Rn()));
                    KitGrass.Write(data, root, tint, tall);
                    lo = Vector3.Min(lo, root); hi = Vector3.Max(hi, root);
                    clumps++;
                }
            if (clumps == 0) return;
            var go = new GameObject("Grass");
            go.transform.SetParent(groundT, false);
            go.transform.localPosition = origin;
            var kg = go.AddComponent<KitGrass>();
            kg.material = GrassMaterialInstance;
            kg.seed = seed;
            kg.minHeight = (float?)g?["height"]?[0] ?? 0.3f; kg.maxHeight = (float?)g?["height"]?[1] ?? 0.58f;
            kg.castShadows = (bool?)g?["shadows"] ?? true;
            kg.clumps = data.ToArray();
            kg.localBounds = new Bounds((lo + hi) / 2, hi - lo + new Vector3(1f, 1.5f, 1f));
            notes.Add($"grass: {clumps} clumps, up to {clumps * KitGrass.MaxBlades * 3} tris, drawn on the GPU ({data.Count / 1024} KB)");
        }
    }
}
