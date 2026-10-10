using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// An outdoor map (a village, a hamlet, a farmstead) built from a layout: the outdoor counterpart of
    /// <see cref="KitRoom"/>. The layout (JSON, plan metres: x east, y north, origin at the map's south-west corner)
    /// gives the clearing in the forest, roads as curves through points, paved or trodden areas, buildings (the kit's
    /// structures or generated houses) turned to face a point, props, fences along polylines, single trees, the forest
    /// and its undergrowth, dressing, spawns, markers for the game (NPCs, a respawn point) and exits at road ends.
    /// Build makes: the ground (a mesh with the kit's terrain material, gentle relief rising into the forest, a level
    /// pad under each building, roads and paving painted into its control map, so nothing follows a tile grid), the
    /// pieces placed on it, colliders (buildings, props, fences, tree trunks, an invisible wall round the clearing
    /// broken only by the roads, the map's border) and the links. Same layout and seed, same map.
    /// Plan space -> this transform's local space: (x, y, h) -> (-x, h, -y); a turn of `deg` about plan z -> -deg about y.
    /// </summary>
    public partial class KitVillage : MonoBehaviour
    {
        [Tooltip("The layout as JSON (see Documentation~/LEVEL_BUILDING.md, outdoor maps).")]
        [TextArea(8, 40)] public string layout;
        [Tooltip("The kit's terrain material (M_VK_Terrain); Build makes a copy carrying this map's control map.")]
        public Material groundMaterial;
        [Tooltip("For generated houses (Generated/KitHouseRules.asset).")]
        public KitHouseRules houseRules;
        [Tooltip("The pieces the layout names, by prefab name (the editor fills it from the package).")]
        public List<GameObject> prefabs = new List<GameObject>();
        [Tooltip("The materials the layout's swaps name (the editor fills it).")]
        public List<Material> materials = new List<Material>();

        /// <summary>How pieces are instantiated (the editor keeps prefab links).</summary>
        public static Func<GameObject, Transform, GameObject> Spawn = (prefab, parent) => Instantiate(prefab, parent);

        [NonSerialized] public List<string> notes = new List<string>();
        public Mesh GroundMesh { get; private set; }
        public Texture2D ControlMap { get; private set; }
        public Material GroundMaterialInstance { get; private set; }

        const float Res = 1f;            // ground mesh spacing (m)
        const int CtlPerM = 4;           // control map pixels per metre

        JObject L;
        float W, H, M;                   // the map (walkable, walled) and the margin of forest drawn round it
        System.Random rnd;
        Transform groundT, buildT, propT, natureT, logicT, wallT;
        readonly List<(Vector2[] poly, float h)> pads = new List<(Vector2[], float)>();
        readonly List<(Vector2[] poly, string id)> occupied = new List<(Vector2[], string)>();
        readonly List<(string id, Vector2[] pts, float width, string surface)> roads = new List<(string, Vector2[], float, string)>();
        readonly List<(Vector2 c, Vector2 r, float lumps, string surface, int seed)> areas = new List<(Vector2, Vector2, float, string, int)>();
        readonly Dictionary<string, (Transform t, Vector2 at, float rot)> builtById = new Dictionary<string, (Transform, Vector2, float)>();
        readonly List<(Vector2 c, Vector2 r, float lumps, int seed)> clears = new List<(Vector2, Vector2, float, int)>();

        // ------------------------------------------------------------------ plan space
        public static Vector3 Local(float x, float y, float h) => new Vector3(-x, h, -y);
        public static Quaternion Turn(float deg) => Quaternion.Euler(0f, -deg, 0f);
        static Vector2 V(JToken t) => new Vector2((float)t[0], (float)t[1]);
        static Vector2 Rot(Vector2 v, float deg) { float r = deg * Mathf.Deg2Rad, c = Mathf.Cos(r), s = Mathf.Sin(r); return new Vector2(c * v.x - s * v.y, s * v.x + c * v.y); }
        static float Ang(Vector2 v) => Mathf.Atan2(v.y, v.x) * Mathf.Rad2Deg;

        public void Clear()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                var c = transform.GetChild(i).gameObject;
                if (Application.isPlaying) Destroy(c); else DestroyImmediate(c);
            }
        }

        public void Build()
        {
            Clear();
            notes.Clear(); pads.Clear(); occupied.Clear(); roads.Clear(); areas.Clear(); builtById.Clear();
            L = JObject.Parse(string.IsNullOrWhiteSpace(layout) ? "{}" : layout);
            var size = L["size"] as JArray;
            W = size != null ? (float)size[0] : 100f; H = size != null ? (float)size[1] : 100f;
            M = (float?)L["margin"] ?? 24f;
            rnd = new System.Random((int?)L["seed"] ?? 1);
            groundT = Group("Ground"); buildT = Group("Buildings"); propT = Group("Props"); natureT = Group("Nature");
            logicT = Group("Logic"); wallT = Group("Walls");
            clears.Clear();
            clears.AddRange(Clearings(L, W, H));
            foreach (var r in L["roads"] as JArray ?? new JArray())
                roads.Add(((string)r["id"], Spline(((JArray)r["points"]).Select(V).ToList()), (float?)r["width"] ?? 3f, (string)r["surface"] ?? "dirt"));
            int ai = 0;
            foreach (var a in L["areas"] as JArray ?? new JArray())
                areas.Add((V(a["centre"]), V(a["radius"]), (float?)a["lumps"] ?? 0.15f, (string)a["surface"] ?? "dirt", 31 + ai++));

            Buildings();                     // first: their pads shape the ground
            Ground();
            Gardens();
            Props();
            Fences();
            Trees();
            Forest();
            Scatter();
            Markers();
            Encounters();
            Exits();
            Walls();
            foreach (var t in new[] { buildT, propT, natureT }) Swap(t.gameObject, null);   // the map's palette, its nature too (props swap their own first)
            Grass(GroundMaterialInstance);   // last: it keeps clear of everything placed
        }

        /// <summary>material swaps by name, {"M_VK_RoofRed": "M_VK_Thatch"}: the layout's "swap" (the whole map's palette,
        /// e.g. a goblin camp's hide and thatch), overridden by an entry's own "swap"; the one swapped in is a kit material's
        /// name or a map's own material's asset path (a burnt map's charred leaves, cut out like the kit's)</summary>
        void Swap(GameObject go, JToken spec)
        {
            var map = new Dictionary<string, string>();
            foreach (var src in new[] { L["swap"], spec?["swap"] })
                if (src is JObject o) foreach (var kv in o) map[kv.Key] = (string)kv.Value;
            if (map.Count == 0 || go == null) return;
            foreach (var r in go.GetComponentsInChildren<Renderer>())
            {
                var mats = r.sharedMaterials;
                bool changed = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    if (mats[i] == null || !map.TryGetValue(mats[i].name, out var to)) continue;
                    string want = to.EndsWith(".mat") ? System.IO.Path.GetFileNameWithoutExtension(to) : to;
                    var m = materials.FirstOrDefault(x => x != null && x.name == want);
                    if (m == null) { notes.Add($"no material {to} to swap in"); continue; }
                    mats[i] = m; changed = true;
                }
                if (changed) r.sharedMaterials = mats;
            }
        }

        Transform Group(string n)
        {
            var t = new GameObject(n).transform;
            t.SetParent(transform, false);
            return t;
        }

        GameObject Prefab(string name)
        {
            if (string.IsNullOrEmpty(name)) return null;
            foreach (var n in new[] { name, "SM_VK_" + name, "SM_VKI_Prop_" + name, "SM_VKI_" + name })
            {
                var p = prefabs.FirstOrDefault(g => g != null && g.name == n);
                if (p != null) return p;
            }
            notes.Add($"no prefab {name}");
            return null;
        }

        // ------------------------------------------------------------------ curves and shapes
        /// <summary>a Catmull-Rom curve through the points, sampled every metre or so</summary>
        public static Vector2[] Spline(List<Vector2> p)
        {
            if (p.Count < 2) return p.ToArray();
            var o = new List<Vector2>();
            for (int i = 0; i < p.Count - 1; i++)
            {
                Vector2 p0 = p[Mathf.Max(0, i - 1)], p1 = p[i], p2 = p[i + 1], p3 = p[Mathf.Min(p.Count - 1, i + 2)];
                int n = Mathf.Max(2, Mathf.CeilToInt((p2 - p1).magnitude));
                for (int k = 0; k < n; k++)
                {
                    float t = k / (float)n, t2 = t * t, t3 = t2 * t;
                    o.Add(0.5f * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3));
                }
            }
            o.Add(p[p.Count - 1]);
            return o.ToArray();
        }

        /// <summary>a closed Catmull-Rom curve through the points (a ring), its first point repeated at the end</summary>
        public static Vector2[] ClosedSpline(List<Vector2> p)
        {
            if (p.Count < 3) return p.Concat(p.Take(1)).ToArray();
            var o = new List<Vector2>();
            int m = p.Count;
            for (int i = 0; i < m; i++)
            {
                Vector2 p0 = p[(i - 1 + m) % m], p1 = p[i], p2 = p[(i + 1) % m], p3 = p[(i + 2) % m];
                int n = Mathf.Max(2, Mathf.CeilToInt((p2 - p1).magnitude));
                for (int k = 0; k < n; k++)
                {
                    float t = k / (float)n, t2 = t * t, t3 = t2 * t;
                    o.Add(0.5f * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3));
                }
            }
            o.Add(p[0]);
            return o.ToArray();
        }

        static float DistToPolyline(Vector2 q, Vector2[] pts)
        {
            float best = float.MaxValue;
            for (int i = 0; i < pts.Length - 1; i++)
            {
                Vector2 a = pts[i], b = pts[i + 1], ab = b - a;
                float t = ab.sqrMagnitude < 1e-6f ? 0 : Mathf.Clamp01(Vector2.Dot(q - a, ab) / ab.sqrMagnitude);
                best = Mathf.Min(best, (q - (a + ab * t)).magnitude);
            }
            return best;
        }

        static bool InPoly(Vector2 q, Vector2[] poly)
        {
            bool inside = false;
            for (int i = 0, j = poly.Length - 1; i < poly.Length; j = i++)
                if ((poly[i].y > q.y) != (poly[j].y > q.y) && q.x < (poly[j].x - poly[i].x) * (q.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)
                    inside = !inside;
            return inside;
        }

        static float DistToPoly(Vector2 q, Vector2[] poly)
        {
            if (InPoly(q, poly)) return 0f;
            var closed = poly.Concat(new[] { poly[0] }).ToArray();
            return DistToPolyline(q, closed);
        }

        /// <summary>a lumpy ellipse: &lt; 1 inside</summary>
        static float Blob(Vector2 q, Vector2 c, Vector2 r, float lumps, int seed)
        {
            float a = Mathf.Atan2(q.y - c.y, q.x - c.x);
            float k = 1 + lumps * (Mathf.Sin(3 * a + seed * 0.7f) * 0.6f + Mathf.Sin(5 * a + seed * 1.3f) * 0.4f);
            float dx = (q.x - c.x) / (r.x * k), dy = (q.y - c.y) / (r.y * k);
            return Mathf.Sqrt(dx * dx + dy * dy);
        }

        /// <summary>the clearing (one lumpy oval) or the clearings (glades along a path: their union) of a layout</summary>
        static List<(Vector2 c, Vector2 r, float lumps, int seed)> Clearings(JObject lay, float w, float h)
        {
            var list = lay["clearings"] as JArray ?? new JArray();
            if (list.Count == 0) list.Add(lay["clearing"] ?? new JObject());
            return list.Select((cl, i) => (cl["centre"] != null ? V(cl["centre"]) : new Vector2(w / 2, h / 2),
                                          cl["radius"] != null ? V(cl["radius"]) : new Vector2(w / 2 - 12, h / 2 - 12),
                                          (float?)cl["lumps"] ?? 0.1f, 3 + 7 * i)).ToList();
        }

        static float Union(Vector2 q, List<(Vector2 c, Vector2 r, float lumps, int seed)> cs) =>
            cs.Count == 0 ? 0f : cs.Min(k => Blob(q, k.c, k.r, k.lumps, k.seed));

        /// <summary>&lt; 1 inside the clearing (or any of the clearings)</summary>
        float Clearing(Vector2 q) => Union(q, clears);

        // ------------------------------------------------------------------ ground
        float Noise(float x, float y, float s) => Mathf.PerlinNoise(x / s + 31.7f, y / s + 17.3f);

        /// <summary>the ground's natural height: a gentle relief, rising into the forest</summary>
        float Natural(Vector2 q)
        {
            float relief = (float?)L["relief"] ?? 0.3f, rim = (float?)L["rim"] ?? 2.5f;
            float h = relief * ((Noise(q.x, q.y, 23f) - 0.5f) * 2f + (Noise(q.x, q.y, 7f) - 0.5f) * 0.5f);
            h += rim * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.95f, 1.35f, Clearing(q)));
            return h;
        }

        /// <summary>the ground's height: natural, levelled to each building's pad near it</summary>
        public float Height(Vector2 q)
        {
            float h = Natural(q);
            foreach (var (poly, ph) in pads)
            {
                float d = DistToPoly(q, poly);
                if (d < 4f) h = Mathf.Lerp(ph, h, Mathf.SmoothStep(0f, 1f, d / 4f));
            }
            return h;
        }

        void Ground()
        {
            // the mesh spans the map and its margin; its own origin sits at the margin's south-west corner (the terrain
            // material projects its control map in object space, from 0)
            float GW = W + 2 * M, GH = H + 2 * M;
            int nx = Mathf.CeilToInt(GW / Res) + 1, ny = Mathf.CeilToInt(GH / Res) + 1;
            var verts = new Vector3[nx * ny];
            var cols = new Color[nx * ny];
            for (int j = 0; j < ny; j++)
                for (int i = 0; i < nx; i++)
                {
                    var o = new Vector2(Mathf.Min(GW, i * Res), Mathf.Min(GH, j * Res));
                    var q = o - new Vector2(M, M);
                    verts[j * nx + i] = Local(o.x, o.y, Height(q));
                    float shade = Mathf.Lerp(1f, 0.82f, Mathf.InverseLerp(1.0f, 1.25f, Clearing(q)));     // the forest floor in shade
                    cols[j * nx + i] = new Color(shade, 0f, 0f, 0f);
                }
            var tris = new List<int>();
            for (int j = 0; j < ny - 1; j++)
                for (int i = 0; i < nx - 1; i++)
                {
                    int a = j * nx + i, b = a + 1, c = a + nx, d = c + 1;
                    tris.AddRange(new[] { a, b, c, b, d, c });
                }
            var mesh = new Mesh { name = $"{name}_Ground", indexFormat = verts.Length > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16 };
            mesh.vertices = verts; mesh.colors = cols; mesh.triangles = tris.ToArray();
            mesh.RecalculateNormals(); mesh.RecalculateBounds();
            // the triangles wind for the mirrored plan space: make the normals face up
            if (mesh.normals.Length > 0 && mesh.normals[0].y < 0) { tris.Reverse(); mesh.triangles = tris.ToArray(); mesh.RecalculateNormals(); }
            GroundMesh = mesh;
            var go = new GameObject("Ground");
            go.transform.SetParent(groundT, false);
            go.transform.localPosition = Local(-M, -M, 0f);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            ControlMap = PaintControl();
            if (groundMaterial != null)
            {
                GroundMaterialInstance = new Material(groundMaterial) { name = $"{name}_Ground" };
                GroundMaterialInstance.SetTexture("_CtlMap", ControlMap);
                GroundMaterialInstance.SetVector("_CtlScale", new Vector4(1f / GW, 1f / GH, 0, 0));
                mr.sharedMaterial = GroundMaterialInstance;
            }
            else notes.Add("no ground material (M_VK_Terrain)");
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
        }

        /// <summary>the control map: R dirt (roads, trodden areas, doorsteps), G cobble (paved areas)</summary>
        Texture2D PaintControl()
        {
            int tw = Mathf.CeilToInt((W + 2 * M) * CtlPerM), th = Mathf.CeilToInt((H + 2 * M) * CtlPerM);
            var px = new Color[tw * th];
            var boxes = roads.Select(r => (min: new Vector2(r.pts.Min(p => p.x), r.pts.Min(p => p.y)) - Vector2.one * (r.width / 2 + 2),
                                           max: new Vector2(r.pts.Max(p => p.x), r.pts.Max(p => p.y)) + Vector2.one * (r.width / 2 + 2))).ToList();
            var doors = builtById.Values.Select(b => b.t.GetComponentsInChildren<Transform>().Where(t => t.name.Contains("Door")).Select(t => t.GetComponentInChildren<Renderer>() is Renderer r ? r.bounds.center : t.position).ToList()).SelectMany(x => x)
                                 .Select(p => transform.InverseTransformPoint(p)).Select(p => new Vector2(-p.x, -p.z)).ToList();
            for (int j = 0; j < th; j++)
                for (int i = 0; i < tw; i++)
                {
                    var q = new Vector2((i + 0.5f) / CtlPerM - M, (j + 0.5f) / CtlPerM - M);
                    float n = (Noise(q.x, q.y, 3.1f) - 0.5f) * 0.9f;
                    float dirt = 0f, cob = 0f;
                    for (int ri = 0; ri < roads.Count; ri++)
                    {
                        var (_, pts, width, surface) = roads[ri];
                        if (q.x < boxes[ri].min.x || q.y < boxes[ri].min.y || q.x > boxes[ri].max.x || q.y > boxes[ri].max.y) continue;
                        float d = DistToPolyline(q, pts) + n;
                        float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(width / 2 - 0.6f, width / 2 + 0.6f, d));
                        if (surface == "cobble") cob = Mathf.Max(cob, w); else dirt = Mathf.Max(dirt, w);
                    }
                    foreach (var (c, r, lumps, surface, seed) in areas)
                    {
                        float b = Blob(q, c, r, lumps, seed) + n * 0.08f;
                        float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.85f, 1.05f, b));
                        if (surface == "cobble") { cob = Mathf.Max(cob, w * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1.0f, 0.7f, b))); dirt = Mathf.Max(dirt, w); }
                        else dirt = Mathf.Max(dirt, w);
                    }
                    foreach (var dp in doors)
                    {
                        float d = (q - dp).magnitude + n;
                        dirt = Mathf.Max(dirt, 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1.4f, 2.6f, d)));
                    }
                    px[j * tw + i] = new Color(dirt, cob, 0f, 0f);
                }
            var tex = new Texture2D(tw, th, TextureFormat.RGBA32, false, true) { name = $"{name}_GroundControl", wrapMode = TextureWrapMode.Clamp };
            tex.SetPixels(px);
            tex.Apply();
            return tex;
        }

        // ------------------------------------------------------------------ buildings
        /// <summary>a prefab's footprint (plan space, unturned, about its origin) and its front (the side its door is on)</summary>
        (Rect box, Vector2 front) Measure(GameObject inst) { var (box, _, front) = MeasureWalls(inst); return (box, front); }

        Rect PlanBox(IEnumerable<Renderer> rs, Vector3 fallback)
        {
            var list = rs.ToList();
            var b = list.Count > 0 ? list[0].bounds : new Bounds(fallback, Vector3.one);
            foreach (var r in list) b.Encapsulate(r.bounds);
            var lo = transform.InverseTransformPoint(b.min); var hi = transform.InverseTransformPoint(b.max);
            return Rect.MinMaxRect(Mathf.Min(-lo.x, -hi.x), Mathf.Min(-lo.z, -hi.z), Mathf.Max(-lo.x, -hi.x), Mathf.Max(-lo.z, -hi.z));
        }

        /// <summary>as Measure, plus the box of its walls alone (what one bumps into: no eaves, signs or porches)</summary>
        (Rect box, Rect walls, Vector2 front) MeasureWalls(GameObject inst)
        {
            var saveP = inst.transform.localPosition; var saveR = inst.transform.localRotation;
            inst.transform.localPosition = Vector3.zero; inst.transform.localRotation = Quaternion.identity;
            var rs = inst.GetComponentsInChildren<Renderer>();
            var box = PlanBox(rs, inst.transform.position);
            var wallRs = rs.Where(r => r.name.Contains("Wall") || r.name.Contains("Corner") || r.name.Contains("Foundation")).ToList();
            var walls = wallRs.Count > 0 ? PlanBox(wallRs, inst.transform.position) : box;
            Vector2 front = new Vector2(0f, -1f);
            var doors = inst.GetComponentsInChildren<Transform>().Where(t => t != inst.transform && t.name.Contains("Door")).ToList();
            if (doors.Count > 0)
            {
                var dl = transform.InverseTransformPoint(doors[0].GetComponentInChildren<Renderer>() is Renderer dr ? dr.bounds.center : doors[0].position);
                var d = new Vector2(-dl.x, -dl.z) - box.center;
                // the door's side: the axis it opens along (its own forward), on the side of the walls it stands at; a
                // building with a yard (the smithy's forge, the training yard, the woodcutter's) has a box whose nearest
                // edge is not the door's. Without a turn to read: the axis it sits nearest the edge of
                var fw = transform.InverseTransformDirection(doors[0].forward);
                var fp = new Vector2(-fw.x, -fw.z);
                var dw = new Vector2(-dl.x, -dl.z) - walls.center;
                if (fp.sqrMagnitude > 0.01f && Mathf.Abs(Mathf.Abs(fp.x) - Mathf.Abs(fp.y)) > 0.2f)
                    front = Mathf.Abs(fp.x) > Mathf.Abs(fp.y) ? new Vector2(Mathf.Sign(dw.x), 0f) : new Vector2(0f, Mathf.Sign(dw.y));
                else
                {
                    float ex = Mathf.Abs(d.x) / Mathf.Max(0.1f, box.width / 2), ey = Mathf.Abs(d.y) / Mathf.Max(0.1f, box.height / 2);
                    front = ex > ey ? new Vector2(Mathf.Sign(d.x), 0f) : new Vector2(0f, Mathf.Sign(d.y));
                }
            }
            inst.transform.localPosition = saveP; inst.transform.localRotation = saveR;
            return (box, walls, front);
        }

        static Vector2[] Corners(Rect box, Vector2 at, float deg, float grow = 0f)
        {
            var r = new Rect(box.xMin - grow, box.yMin - grow, box.width + 2 * grow, box.height + 2 * grow);
            return new[] { new Vector2(r.xMin, r.yMin), new Vector2(r.xMax, r.yMin), new Vector2(r.xMax, r.yMax), new Vector2(r.xMin, r.yMax) }
                .Select(c => Rot(c, deg) + at).ToArray();
        }

        float Facing(JToken spec, Vector2 at, Vector2 front)
        {
            if (spec["rot"] != null) return (float)spec["rot"];
            Vector2 target;
            if (spec["face"] is JArray fa) target = V(fa);
            else if (spec["face"] is JValue fs && ((string)fs).StartsWith("road:"))
            {
                var rd = roads.FirstOrDefault(r => r.id == ((string)fs).Substring(5));
                target = rd.pts != null ? rd.pts.OrderBy(p => (p - at).sqrMagnitude).First() : at + Vector2.down;
            }
            else return 0f;
            return Ang(target - at) - Ang(front);
        }

        void Buildings()
        {
            foreach (var b in L["buildings"] as JArray ?? new JArray())
            {
                string id = (string)b["id"] ?? "building";
                var at = V(b["at"]);
                GameObject inst;
                if (b["house"] is JObject hs)
                {
                    inst = new GameObject(id);
                    inst.transform.SetParent(buildT, false);
                    var hg = inst.AddComponent<KitHouseGenerator>();
                    hg.rules = houseRules;
                    hg.cells = (int?)hs["cells"] ?? 2; hg.stories = (int?)hs["stories"] ?? 1; hg.seed = (int?)hs["seed"] ?? 1;
                    if ((string)hs["shape"] == "L") hg.shape = KitHouseGenerator.Shape.L;
                    if (hs["front"] != null) hg.front = (string)hs["front"];
                    if (houseRules == null) { notes.Add($"{id}: no house rules"); continue; }
                    hg.Generate();
                }
                else
                {
                    var pf = Prefab((string)b["structure"]);
                    if (pf == null) continue;
                    inst = Spawn(pf, buildT);
                    inst.name = id;
                    if (b["swap"] != null) Swap(inst, b);
                }
                var (box, walls, front) = MeasureWalls(inst);
                float deg = Facing(b, at, front);
                float h = Natural(at);
                inst.transform.localPosition = Local(at.x, at.y, h);
                inst.transform.localRotation = Turn(deg);
                var poly = Corners(box, at, deg);
                foreach (var (op, oid) in occupied)
                    if (poly.Any(p => InPoly(p, op)) || op.Any(p => InPoly(p, poly))) notes.Add($"{id} overlaps {oid}");
                foreach (var rd in roads)
                    if (rd.pts.Any(p => InPoly(p, Corners(box, at, deg, rd.width / 2 - 0.3f)))) notes.Add($"{id} stands on road {rd.id}");
                float wallAt = (float?)L["forest"]?["wallAt"] ?? 1.08f;
                if (poly.Any(c => Clearing(c) > wallAt)) notes.Add($"{id} reaches past the forest's wall (move it in or widen the clearing)");
                occupied.Add((poly, id));
                pads.Add((Corners(box, at, deg, 1.2f), h));
                builtById[id] = (inst.transform, at, deg);
                AddBox(inst, walls, h: 4f, inset: 0.1f);
                Dress(inst, walls);
                if (b["door"] is JObject door) Door(inst, id, door, at, deg);
            }
        }

        /// <summary>a building's own dressing outside its walls' box (barrels by the door, a trough, hay, a table and
        /// stools, its yard's fence, a lean-to's posts, a bell tower beside the nave): boxes over what one bumps into
        /// (<see cref="KitSolid.Box"/>: below 1.2 m, part by part), or the walkers go through it. Left as they are: what
        /// is overhead (eaves, signs' arms, lanterns), the porch one walks onto, a yard's gate, soft dressing (weeds, ivy,
        /// flower boxes), piers and decks.</summary>
        void Dress(GameObject inst, Rect walls)
        {
            var inner = new Rect(walls.xMin - 0.05f, walls.yMin - 0.05f, walls.width + 0.1f, walls.height + 0.1f);
            float floor = inst.transform.position.y;
            foreach (var mf in inst.GetComponentsInChildren<MeshFilter>())
            {
                string n = mf.name;
                if (mf.sharedMesh == null || KitSolid.IsSoft(n) || new[] { "Wall", "Corner", "Foundation", "Roof", "Porch", "Door", "Window", "Gate" }.Any(n.Contains))
                    continue;
                var r = mf.GetComponent<Renderer>();
                if (r == null || r.bounds.min.y > floor + 1.8f) continue;
                var b = mf.sharedMesh.bounds;
                bool inside = true;
                foreach (float x in new[] { b.min.x, b.max.x })
                    foreach (float z in new[] { b.min.z, b.max.z })
                    {
                        var l = inst.transform.InverseTransformPoint(mf.transform.TransformPoint(new Vector3(x, b.min.y, z)));
                        if (!inner.Contains(new Vector2(-l.x, -l.z))) inside = false;
                    }
                if (!inside) KitSolid.Box(mf.gameObject);
            }
        }

        /// <summary>a box collider over a footprint (plan space about the object's origin)</summary>
        void AddBox(GameObject go, Rect box, float h, float inset)
        {
            var c = go.AddComponent<BoxCollider>();
            c.center = new Vector3(-box.center.x, h / 2, -box.center.y);
            c.size = new Vector3(Mathf.Max(0.2f, box.width - 2 * inset), h, Mathf.Max(0.2f, box.height - 2 * inset));
        }

        /// <summary>a building's door as a scene link: a trigger on the door, a spawn on the doorstep facing out</summary>
        void Door(GameObject inst, string id, JObject spec, Vector2 at, float deg)
        {
            var dt = inst.GetComponentsInChildren<Transform>().FirstOrDefault(t => t != inst.transform && t.name.Contains("Door"));
            Vector2 dp;
            if (dt != null)
            {
                var dr = dt.GetComponentInChildren<Renderer>();
                var dl = transform.InverseTransformPoint(dr != null ? dr.bounds.center : dt.position);
                dp = new Vector2(-dl.x, -dl.z);
            }
            else if (inst.GetComponent<KitPiece>()?.Has("vki_spawn_local") == true) dp = at;    // a link piece (a cave mouth): its origin is the opening
            else { notes.Add($"{id}: no door piece for its link"); return; }
            var (_, front) = Measure(inst);
            var outward = Rot(front, deg);                       // the door faces out along the building's front
            var go = new GameObject("LNK_" + id);
            go.transform.SetParent(logicT, false);
            go.transform.localPosition = Local(dp.x + outward.x * 0.6f, dp.y + outward.y * 0.6f, Height(dp));
            go.transform.localRotation = Turn(Ang(outward) - 90f);
            var tr = go.AddComponent<BoxCollider>();
            tr.isTrigger = true; tr.center = new Vector3(0, 1.1f, 0); tr.size = new Vector3(1.6f, 2.2f, 1.2f);
            var lk = go.AddComponent<KitLink>();
            lk.linkId = id; lk.kind = "exit"; lk.target = (string)spec["target"]; lk.prompt = (string)spec["prompt"] ?? "Enter"; lk.facingMin = 75f;
            lk.arrive = (string)spec["arrive"];                  // the spawn inside (e.g. an interior's "front")
            SpawnAt(id, dp + outward * 1.8f, Bearing(outward));
        }

        static float Bearing(Vector2 dir) => Mathf.Repeat(90f - Ang(dir), 360f);

        // ------------------------------------------------------------------ props, fences, trees
        GameObject Place(Transform parent, string piece, Vector2 at, float deg, float scale = 1f, bool collide = false)
        {
            var pf = Prefab(piece);
            if (pf == null) return null;
            var go = Spawn(pf, parent);
            go.transform.localPosition = Local(at.x, at.y, Height(at));
            go.transform.localRotation = Turn(deg);
            if (Mathf.Abs(scale - 1f) > 1e-3f) go.transform.localScale = Vector3.one * scale;
            if (collide)
            {
                var (box, _) = Measure(go);
                AddBox(go, box, h: 2.5f, inset: 0.15f);
            }
            return go;
        }

        /// <summary>gardens: crop beds in a grid (turned with the garden), a fence round them with a gate on one side</summary>
        void Gardens()
        {
            foreach (var g in L["gardens"] as JArray ?? new JArray())
            {
                var at = V(g["at"]);
                float deg = (float?)g["rot"] ?? 0f, cell = (float?)g["cell"] ?? 3.3f;
                var size = g["beds"] as JArray;
                int cols = size != null ? (int)size[0] : 2, rows = size != null ? (int)size[1] : 2;
                var crops = (g["crops"] as JArray)?.Select(c => (string)c).ToList() ?? new List<string> { "Crop_Cabbage" };
                float w = cols * cell, d = rows * cell;
                int k = 0;
                for (int i = 0; i < cols; i++)
                    for (int j = 0; j < rows; j++)
                    {
                        var local = new Vector2((i + 0.5f) * cell - w / 2, (j + 0.5f) * cell - d / 2);
                        Place(propT, crops[k++ % crops.Count], at + Rot(local, deg), deg + 90f * rnd.Next(4));
                    }
                var box = new Rect(-w / 2 - 0.8f, -d / 2 - 0.8f, w + 1.6f, d + 1.6f);
                occupied.Add((Corners(box, at, deg), (string)g["id"] ?? "garden"));
                string fence = (string)g["fence"];
                if (fence == null) continue;
                // the fence: the box's four sides, the gate side ("S" by default: the garden's local -y) left with a gate
                var c4 = Corners(box, at, deg);              // SW, SE, NE, NW in the garden's frame
                string gateSide = (string)g["gate"] ?? "S";
                var sides = new[] { ("S", c4[0], c4[1]), ("E", c4[1], c4[2]), ("N", c4[2], c4[3]), ("W", c4[3], c4[0]) };
                foreach (var (sd, a, b) in sides)
                {
                    var spec = new JObject { ["piece"] = fence, ["smooth"] = false, ["points"] = new JArray(new JArray(a.x, a.y), new JArray(b.x, b.y)) };
                    if (sd == gateSide && g["gatePiece"] != null) { spec["gate"] = (string)g["gatePiece"]; spec["gateAt"] = new JArray(0.5); }
                    FenceLine(spec);
                }
            }
        }

        void Props()
        {
            foreach (var p in L["props"] as JArray ?? new JArray())
            {
                var at = V(p["at"]);
                var pf = Prefab((string)p["piece"]);
                if (pf == null) continue;
                var go = Spawn(pf, propT);
                float scale = (float?)p["scale"] ?? 1f;
                if (Mathf.Abs(scale - 1f) > 1e-3f) go.transform.localScale = Vector3.one * scale;
                var (box, front) = Measure(go);
                float deg = Facing(p, at, front);
                go.transform.localPosition = Local(at.x, at.y, Height(at));
                go.transform.localRotation = Turn(deg);
                if (p["swap"] != null) Swap(go, p);
                if ((bool?)p["collide"] ?? true)
                {
                    if (KitSolid.IsTrunk(pf.name)) KitSolid.Trunk(go);       // a tree or a stump as the forest's: its trunk
                    else KitSolid.Box(go);                                  // what one bumps into: a signpost's post, not its arms
                }
                if ((bool?)p["dress"] ?? true) Dress(go, pf.name);
                occupied.Add((Corners(box, at, deg), (string)p["piece"]));
            }
        }

        /// <summary>the pieces a kit piece is only the base of, in its own frame (Unity metres and degrees), with a roof
        /// material (in place of its M_VK_Roof*): the gatehouse's block is finished by def_dress_gatehouse (vk_mod_defence) -- a timber storey on the
        /// walk (6.2), its slate hip roof and the towers' cones (9.0), the portcullis raised under the arch, the leaves open
        /// against the vault, banners on the town side; without them its flat top and open towers show</summary>
        public static readonly Dictionary<string, (string piece, Vector3 at, float rot, string roof)[]> Dressings =
            new Dictionary<string, (string, Vector3, float, string)[]>
            {
                ["SM_VK_Gatehouse_Block"] = new (string, Vector3, float, string)[]
                {
                    ("SM_VK_Gatehouse_Portcullis", new Vector3(0f, 3.6f, 2.4f), 0f, null),
                    ("SM_VK_Gatehouse_GateLeaf", new Vector3(1.75f, 0f, 1.2f), -90f, null),
                    ("SM_VK_Gatehouse_GateLeaf", new Vector3(-1.75f, 0f, 1.2f), -90f, null),
                    ("SM_VK_Wall_Timber_Window", new Vector3(1.5f, 6.2f, 3f), 0f, null),
                    ("SM_VK_Wall_Timber_Window", new Vector3(-1.5f, 6.2f, 3f), 0f, null),
                    ("SM_VK_Wall_Timber_X", new Vector3(4.5f, 6.2f, -3f), 180f, null),
                    ("SM_VK_Wall_Timber_Window", new Vector3(1.5f, 6.2f, -3f), 180f, null),
                    ("SM_VK_Wall_Timber_Window", new Vector3(-1.5f, 6.2f, -3f), 180f, null),
                    ("SM_VK_Wall_Timber_X", new Vector3(-4.5f, 6.2f, -3f), 180f, null),
                    ("SM_VK_Wall_Timber_Door", new Vector3(6f, 6.2f, -1.5f), 90f, null),
                    ("SM_VK_Wall_Timber", new Vector3(6f, 6.2f, 1.5f), 90f, null),
                    ("SM_VK_Wall_Timber_Door", new Vector3(-6f, 6.2f, -1.5f), -90f, null),
                    ("SM_VK_Wall_Timber", new Vector3(-6f, 6.2f, 1.5f), -90f, null),
                    ("SM_VK_Corner_Timber", new Vector3(6f, 6.2f, -3f), 90f, null),
                    ("SM_VK_Corner_Timber", new Vector3(-6f, 6.2f, -3f), 180f, null),
                    ("SM_VK_Roof_Hip", new Vector3(4.5f, 9f, 0f), 180f, "M_VK_Roof_Slate"),
                    ("SM_VK_Roof_Mid", new Vector3(1.5f, 9f, 0f), 0f, "M_VK_Roof_Slate"),
                    ("SM_VK_Roof_Mid", new Vector3(-1.5f, 9f, 0f), 0f, "M_VK_Roof_Slate"),
                    ("SM_VK_Roof_Hip", new Vector3(-4.5f, 9f, 0f), 0f, "M_VK_Roof_Slate"),
                    ("SM_VK_Roof_Cone_R2", new Vector3(4.4f, 9f, 3f), 0f, "M_VK_Roof_Slate"),
                    ("SM_VK_Roof_Cone_R2", new Vector3(-4.4f, 9f, 3f), 0f, "M_VK_Roof_Slate"),
                    ("SM_VK_Banner_Wall", new Vector3(3f, 9f, -3.18f), 180f, null),
                    ("SM_VK_Banner_Wall", new Vector3(-3f, 9f, -3.18f), 180f, null),
                },
            };

        /// <summary>a piece's dressing (Dressings) as its children ("dress": false in the layout leaves it bare)</summary>
        void Dress(GameObject go, string piece)
        {
            if (!Dressings.TryGetValue(piece, out var parts)) return;
            foreach (var (n, at, rot, roof) in parts)
            {
                var pf = Prefab(n);
                if (pf == null) continue;
                var c = Spawn(pf, go.transform);
                c.transform.localPosition = at;
                c.transform.localRotation = Quaternion.Euler(0f, rot, 0f);
                if (roof == null) continue;
                var m = materials.FirstOrDefault(x => x != null && x.name == roof);
                if (m == null) { notes.Add($"no material {roof} for {n}"); continue; }
                foreach (var r in c.GetComponentsInChildren<Renderer>())
                {
                    var ms = r.sharedMaterials;
                    for (int i = 0; i < ms.Length; i++)
                        if (ms[i] != null && ms[i].name.StartsWith("M_VK_Roof", StringComparison.Ordinal)) ms[i] = m;
                    r.sharedMaterials = ms;
                }
            }
        }

        void Fences()
        {
            foreach (var f in L["fences"] as JArray ?? new JArray()) FenceLine(f);
        }

        void FenceLine(JToken f)
        {
            {
                string piece = (string)f["piece"] ?? "Prop_Fence", gate = (string)f["gate"];
                string door = (string)f["gateDoor"];               // doors in the gate's frame (a breakable gate: the way in)
                bool doorFlip = (bool?)f["gateDoorFlip"] ?? false;
                var gates = (f["gateAt"] as JArray)?.Select(g => (float)g).OrderBy(g => g).ToList() ?? new List<float>();
                bool closed = (bool?)f["closed"] ?? false, flip = (bool?)f["flip"] ?? false, collide = (bool?)f["collide"] ?? true;
                float offset = (float?)f["offset"] ?? 0f;
                float Length(string pn)
                {
                    var pf = Prefab(pn);
                    if (pf == null) return 0f;
                    var probe = Spawn(pf, propT);
                    var (bx, _) = Measure(probe);
                    if (Application.isPlaying) Destroy(probe); else DestroyImmediate(probe);
                    return Mathf.Max(bx.width, bx.height);
                }
                float len = Length(piece);
                if (len <= 0f) return;
                float gw = gate != null && gates.Count > 0 ? Length(gate) : 0f;
                var pts = ((JArray)f["points"]).Select(V).ToList();
                if (closed) pts.Add(pts[0]);
                var curve = (bool?)f["smooth"] ?? true ? (closed ? ClosedSpline(pts.Take(pts.Count - 1).ToList()) : Spline(pts)) : pts.ToArray();
                if (Mathf.Abs(offset) > 1e-3f)             // the line shifted sideways (left of the way it runs): a walkway behind a wall
                    curve = curve.Select((q, i) =>
                    {
                        var d = curve[Mathf.Min(i + 1, curve.Length - 1)] - curve[Mathf.Max(i - 1, 0)];
                        return q + new Vector2(-d.y, d.x).normalized * offset;
                    }).ToArray();
                // walk the curve: runs of pieces between the gates, each piece turned along its chord and stretched to fit its
                // run; a gate keeps its own width
                float total = 0; var cum = new List<float> { 0 };
                for (int i = 1; i < curve.Length; i++) { total += (curve[i] - curve[i - 1]).magnitude; cum.Add(total); }
                Vector2 At(float s)
                {
                    if (closed) s = Mathf.Repeat(s, total);
                    int i = Mathf.Clamp(cum.FindIndex(c => c >= s), 1, curve.Length - 1);
                    float t = Mathf.InverseLerp(cum[i - 1], cum[i], s);
                    return Vector2.Lerp(curve[i - 1], curve[i], t);
                }
                void Lay(string pn, float s0, float s1, float pieceLen, bool isGate)
                {
                    Vector2 a = At(s0), b = At(s1), mid = (a + b) / 2;
                    float deg = Ang(b - a) + (flip ? 180f : 0f);
                    var go = Place(propT, pn, mid, deg, 1f, collide: collide && !isGate);
                    if (isGate && door != null)
                    {
                        var d = Place(propT, door, mid, deg + (doorFlip ? 180f : 0f));
                        if (d != null) d.name = "GATE_" + d.name;
                        else notes.Add($"no gate door {door}");
                    }
                    float chord = (b - a).magnitude;
                    if (go != null && Mathf.Abs(chord - pieceLen) > 0.05f) go.transform.localScale = new Vector3(chord / pieceLen, 1f, 1f);
                    if (collide || isGate) occupied.Add((Corners(new Rect(-chord / 2, -0.3f, chord, 0.6f), mid, Ang(b - a)), isGate ? "gate" : "fence"));
                }
                void Run(float s0, float s1)
                {
                    float runLen = s1 - s0;
                    if (runLen < len * 0.4f) return;
                    int n = Mathf.Max(1, Mathf.RoundToInt(runLen / len));
                    float step = runLen / n;
                    for (int k = 0; k < n; k++) Lay(piece, s0 + k * step, s0 + (k + 1) * step, len, false);
                }
                var gs = gates.Select(g => g * total).ToList();
                if (gs.Count == 0) Run(0f, total);
                else
                {
                    for (int i = 0; i < gs.Count; i++)
                    {
                        Lay(gate, gs[i] - gw / 2, gs[i] + gw / 2, gw, true);
                        float next = i + 1 < gs.Count ? gs[i + 1] : closed ? gs[0] + total : total + gw / 2;
                        Run(gs[i] + gw / 2, next - gw / 2);
                    }
                    if (!closed) Run(0f, gs[0] - gw / 2);
                }
                // pieces along the line, turned with it (a ladder up to a walkway: it leans on the deck only when it
                // stands where and as a walkway piece does)
                foreach (var e in f["along"] as JArray ?? new JArray())
                {
                    string pn = (string)e["piece"];
                    if (pn == null) continue;
                    foreach (var fr in e["at"] as JArray ?? new JArray())
                    {
                        float s = (float)fr * total;
                        Vector2 a = At(s - 0.5f), b = At(s + 0.5f);
                        var go = Place(propT, pn, At(s), Ang(b - a) + (flip ? 180f : 0f) + ((float?)e["rot"] ?? 0f), 1f,
                                       collide: (bool?)e["collide"] ?? false);
                        if (go == null) notes.Add($"no piece {pn} along a fence");
                    }
                }
            }
        }

        void Trees()
        {
            foreach (var t in L["trees"] as JArray ?? new JArray())
            {
                var at = V(t["at"]);
                var go = Place(natureT, (string)t["piece"], at, (float?)t["rot"] ?? (float)(rnd.NextDouble() * 360), (float?)t["scale"] ?? 1f);
                if (go != null) Trunk(go);
                occupied.Add((Corners(new Rect(-1, -1, 2, 2), at, 0), (string)t["piece"]));
            }
        }

        static void Trunk(GameObject tree) => KitSolid.Trunk(tree);          // 0.45 m round its pivot (a burnt tree 0.4, its box gone)

        /// <summary>may a piece stand here: `keep` metres off roads and areas, `keepBuilt` off buildings, gardens and
        /// props (a tree's crown is wider than its trunk), off the map's very edge</summary>
        bool Free(Vector2 q, float keep, float keepBuilt = -1f, bool margin = false)
        {
            if (keepBuilt < 0) keepBuilt = keep;
            if (!margin && (q.x < 0.5f || q.y < 0.5f || q.x > W - 0.5f || q.y > H - 0.5f)) return false;
            if (margin && (q.x < -M || q.y < -M || q.x > W + M || q.y > H + M)) return false;
            foreach (var rd in roads) if (DistToPolyline(q, rd.pts) < rd.width / 2 + keep) return false;
            foreach (var a in areas) if (Blob(q, a.c, a.r, a.lumps, a.seed) < 1.05f + keep / Mathf.Max(1f, Mathf.Min(a.r.x, a.r.y))) return false;
            foreach (var (poly, _) in occupied) if (DistToPoly(q, poly) < keepBuilt) return false;
            return true;
        }

        /// <summary>the forest's ragged edge: the clearing's outline broken by two noises</summary>
        float EdgeAt(Vector2 q, float edge) => edge + (Noise(q.x, q.y, 8f) - 0.5f) * 0.16f + (Noise(q.x + 50f, q.y, 21f) - 0.5f) * 0.12f;

        List<(string piece, float w)> Weights(JToken t) =>
            (t as JArray ?? new JArray()).Select(e => ((string)e[0], (float)e[1])).ToList();

        string Pick(List<(string piece, float w)> ws)
        {
            float s = ws.Sum(w => w.w), r = (float)rnd.NextDouble() * s;
            foreach (var (p, w) in ws) { if ((r -= w) <= 0) return p; }
            return ws.Last().piece;
        }

        /// <summary>dart throwing with a minimum spacing, in a region</summary>
        List<Vector2> Darts(Func<Vector2, bool> where, float spacing, int tries, float pad = 0f)
        {
            var o = new List<Vector2>();
            var grid = new Dictionary<(int, int), List<Vector2>>();
            (int, int) G(Vector2 p) => (Mathf.FloorToInt(p.x / spacing), Mathf.FloorToInt(p.y / spacing));
            for (int k = 0; k < tries; k++)
            {
                var q = new Vector2((float)rnd.NextDouble() * (W + 2 * pad) - pad, (float)rnd.NextDouble() * (H + 2 * pad) - pad);
                var (gx, gy) = G(q);
                bool clash = false;
                for (int a = -1; a <= 1 && !clash; a++)
                    for (int b = -1; b <= 1 && !clash; b++)
                        if (grid.TryGetValue((gx + a, gy + b), out var l) && l.Any(p => (p - q).sqrMagnitude < spacing * spacing)) clash = true;
                if (clash || !where(q)) continue;
                o.Add(q);
                if (!grid.TryGetValue((gx, gy), out var cell)) grid[(gx, gy)] = cell = new List<Vector2>();
                cell.Add(q);
            }
            return o;
        }

        void Forest()
        {
            var f = L["forest"];
            if (f == null) return;
            float spacing = (float?)f["spacing"] ?? 3.4f, edge = (float?)f["edge"] ?? 0.97f;
            var trees = Weights(f["species"]);
            if (trees.Count == 0) return;
            float keepRoad = (float?)f["keepRoad"] ?? 2.5f, keepBuilt = (float?)f["keepBuilt"] ?? 4.5f;
            var spots = Darts(q => Clearing(q) > EdgeAt(q, edge) && Free(q, keepRoad, keepBuilt, margin: true), spacing, 90000, M);
            foreach (var q in spots)
            {
                float s = 0.85f + (float)rnd.NextDouble() * 0.35f;
                var go = Place(natureT, Pick(trees), q, (float)rnd.NextDouble() * 360f, s);
                if (go != null) Trunk(go);
            }
            var under = Weights(f["undergrowth"]);
            if (under.Count > 0)
            {
                float us = (float?)f["undergrowthSpacing"] ?? 2.6f;
                var near = spots;
                foreach (var q in Darts(q => Clearing(q) > EdgeAt(q, edge) - 0.08f && q.x > -4 && q.y > -4 && q.x < W + 4 && q.y < H + 4 && Free(q, 1.2f, 1.8f, margin: true) && near.All(t => (t - q).sqrMagnitude > 1.2f), us, 30000, 4f))
                    KitSolid.Nature(Place(natureT, Pick(under), q, (float)rnd.NextDouble() * 360f, 0.8f + (float)rnd.NextDouble() * 0.4f));
            }
            // stragglers: single trees and pairs out in the clearing near its edge, so the forest frays instead of
            // ending on a line
            int strag = (int?)f["stragglers"] ?? 12;
            var lone = Darts(q => { float c = Clearing(q); return c > 0.72f && c < EdgeAt(q, edge) - 0.04f && Free(q, keepRoad + 1f, keepBuilt + 2f); }, 7f, 20000)
                .OrderBy(_ => rnd.Next()).Take(strag).ToList();
            foreach (var q in lone)
            {
                var go = Place(natureT, Pick(trees), q, (float)rnd.NextDouble() * 360f, 0.8f + (float)rnd.NextDouble() * 0.35f);
                if (go != null) Trunk(go);
                occupied.Add((Corners(new Rect(-1.5f, -1.5f, 3f, 3f), q, 0), "straggler"));
            }
        }

        void Scatter()
        {
            foreach (var s in L["scatter"] as JArray ?? new JArray())
            {
                var ws = Weights(s["pieces"]);
                int count = (int?)s["count"] ?? 20;
                float keep = (float?)s["keep"] ?? 1.5f, spacing = (float?)s["spacing"] ?? 2.5f;
                var spots = Darts(q => Clearing(q) < 0.95f && Free(q, keep), spacing, 20000).OrderBy(_ => rnd.Next()).Take(count);
                foreach (var q in spots) KitSolid.Nature(Place(natureT, Pick(ws), q, (float)rnd.NextDouble() * 360f, 0.8f + (float)rnd.NextDouble() * 0.4f));
            }
        }

        /// <summary>points in the forest just beyond the clearing's wall, away from the roads (plan space): what a walk
        /// test checks cannot be reached. Reads the layout, so it works on a map loaded from its scene.</summary>
        public List<Vector2> ForestProbes(int count = 24)
        {
            var lay = JObject.Parse(string.IsNullOrWhiteSpace(layout) ? "{}" : layout);
            var size = lay["size"] as JArray;
            float w = size != null ? (float)size[0] : 100f, h = size != null ? (float)size[1] : 100f;
            var cs = Clearings(lay, w, h);
            float wallAt = (float?)lay["forest"]?["wallAt"] ?? 1.08f;
            var rds = (lay["roads"] as JArray ?? new JArray()).Select(x => (Spline(((JArray)x["points"]).Select(V).ToList()), (float?)x["width"] ?? 3f)).ToList();
            var o = new List<Vector2>();
            int per = Mathf.Max(4, count / cs.Count);
            foreach (var (c, r, lumps, seed) in cs)
            {
                int got = 0;
                for (int k = 0; k < per * 4 && got < per; k++)
                {
                    float a = k / (float)(per * 4) * Mathf.PI * 2;
                    var dir = new Vector2(Mathf.Cos(a), Mathf.Sin(a));
                    float lo = 0, hi = Mathf.Max(w, h);
                    for (int it = 0; it < 30; it++) { float mid = (lo + hi) / 2; if (Blob(c + dir * mid, c, r, lumps, seed) < wallAt) lo = mid; else hi = mid; }
                    var q = c + dir * (lo + 3f);                                 // 3 m past the wall's line: beyond its band
                    if (q.x < 2 || q.y < 2 || q.x > w - 2 || q.y > h - 2) continue;
                    if (Union(q, cs) < wallAt) continue;                          // inside another glade
                    if (rds.Any(rd => DistToPolyline(q, rd.Item1) < rd.Item2 / 2 + 6f)) continue;
                    if (o.Count > 0 && (o[o.Count - 1] - q).magnitude < 6f) continue;
                    o.Add(q); got++;
                }
            }
            return o;
        }

        // ------------------------------------------------------------------ spawns, markers, exits, walls
        void SpawnAt(string id, Vector2 at, float bearing)
        {
            var go = new GameObject("SPN_" + id);
            go.transform.SetParent(logicT, false);
            go.transform.localPosition = Local(at.x, at.y, Height(at));
            go.transform.localRotation = KitSpawn.FromBearing(bearing);
            var sp = go.AddComponent<KitSpawn>();
            sp.spawnId = id; sp.facingDeg = bearing;
        }

        void Markers()
        {
            foreach (var s in L["spawns"] as JArray ?? new JArray())
                SpawnAt((string)s["id"], V(s["at"]), (float?)s["facing"] ?? 0f);
            foreach (var m in L["markers"] as JArray ?? new JArray())
            {
                var at = V(m["at"]);
                var go = new GameObject($"MRK_{(string)m["role"]}_{(string)m["id"]}");
                go.transform.SetParent(logicT, false);
                go.transform.localPosition = Local(at.x, at.y, Height(at));
                float facing = (float?)m["facing"] ?? 0f;
                go.transform.localRotation = KitSpawn.FromBearing(facing);
                var mk = go.AddComponent<KitMarker>();
                mk.kind = KitMarker.Kind.Other;
                mk.props = new List<KitProp>
                {
                    new KitProp { key = "vki_role", value = (string)m["role"] ?? "" },
                    new KitProp { key = "vki_marker_id", value = (string)m["id"] ?? "" },
                    new KitProp { key = "vki_facing_deg", value = facing.ToString(CultureInfo.InvariantCulture) },
                };
                if (m["note"] != null) mk.props.Add(new KitProp { key = "vki_note", value = (string)m["note"] });
            }
        }

        /// <summary>encounters ([{id, creature, budget, boss, points: [[x, y, h], ...], note}]): a KitEncounter each with
        /// its spawn points as children; `h` lifts a point off the ground (archers on a walkway)</summary>
        void Encounters()
        {
            foreach (var e in L["encounters"] as JArray ?? new JArray())
            {
                var pts = (e["points"] as JArray ?? new JArray()).Select(p => (q: new Vector2((float)p[0], (float)p[1]), h: p.Count() > 2 ? (float)p[2] : 0f)).ToList();
                if (pts.Count == 0) continue;
                var c = new Vector2(pts.Average(p => p.q.x), pts.Average(p => p.q.y));
                string id = (string)e["id"] ?? "encounter";
                var go = new GameObject("ENC_" + id);
                go.transform.SetParent(logicT, false);
                go.transform.localPosition = Local(c.x, c.y, Height(c));
                var en = go.AddComponent<KitEncounter>();
                en.encounterId = id; en.roomType = (string)e["room"] ?? "outdoors"; en.creature = (string)e["creature"] ?? "";
                en.budget = (int?)e["budget"] ?? pts.Count; en.boss = (bool?)e["boss"] ?? false; en.depth = (int?)e["depth"] ?? 0;
                float x0 = pts.Min(p => p.q.x) - 2, x1 = pts.Max(p => p.q.x) + 2, y0 = pts.Min(p => p.q.y) - 2, y1 = pts.Max(p => p.q.y) + 2;
                en.size = new Vector3(x1 - x0, 3f, y1 - y0);
                for (int k = 0; k < pts.Count; k++)
                {
                    var sp = new GameObject($"Spawn_{k}").transform;
                    sp.SetParent(go.transform, false);
                    sp.localPosition = Local(pts[k].q.x, pts[k].q.y, Height(pts[k].q) + pts[k].h) - go.transform.localPosition;
                }
            }
        }

        void Exits()
        {
            foreach (var e in L["exits"] as JArray ?? new JArray())
            {
                var rd = roads.FirstOrDefault(r => r.id == (string)e["road"]);
                if (rd.pts == null) { notes.Add($"exit {(string)e["id"]}: no road {(string)e["road"]}"); continue; }
                bool atStart = (string)e["end"] == "start";
                Vector2 tip = atStart ? rd.pts[0] : rd.pts[rd.pts.Length - 1], back = atStart ? rd.pts[Mathf.Min(4, rd.pts.Length - 1)] : rd.pts[Mathf.Max(0, rd.pts.Length - 5)];
                var inward = (back - tip).normalized;
                // the end of the road inside the map
                var edgeAt = tip;
                for (int k = 0; k < 40 && (edgeAt.x < 1 || edgeAt.y < 1 || edgeAt.x > W - 1 || edgeAt.y > H - 1); k++) edgeAt += inward;
                string id = (string)e["id"];
                var go = new GameObject("LNK_" + id);
                go.transform.SetParent(logicT, false);
                var at = edgeAt + inward * 1.5f;
                go.transform.localPosition = Local(at.x, at.y, Height(at));
                go.transform.localRotation = Turn(Ang(-inward) - 90f);
                var tr = go.AddComponent<BoxCollider>();
                tr.isTrigger = true; tr.center = new Vector3(0, 1.2f, 0); tr.size = new Vector3(rd.width + 1f, 2.4f, 2f);
                var lk = go.AddComponent<KitLink>();
                lk.linkId = id; lk.kind = "exit"; lk.target = (string)e["target"] ?? "@deep"; lk.prompt = (string)e["prompt"] ?? "Leave"; lk.facingMin = 0f;
                lk.walkInto = true;                                // the road runs on: walk on to take it
                lk.arrive = (string)e["arrive"];                 // the spawn on the map beyond (its exit back, usually)
                SpawnAt(id, edgeAt + inward * 5f, Bearing(inward));
            }
        }

        /// <summary>invisible walls: the outline of the walkable ground (inside the clearings up to `wallAt`, a little inside
        /// the forest, and along every road), found on a one-metre grid and walled with boxes a cell thick, so junctions
        /// of roads and glades of any shape close; plus the map's border (a road's end is an exit one uses, not a way off)</summary>
        void Walls()
        {
            void Wall(Vector2 a, Vector2 b, string n, float thick = 0.6f)
            {
                var go = new GameObject(n);
                go.transform.SetParent(wallT, false);
                var mid = (a + b) / 2;
                go.transform.localPosition = Local(mid.x, mid.y, Height(mid));
                go.transform.localRotation = Turn(Ang(b - a));
                var c = go.AddComponent<BoxCollider>();
                c.center = new Vector3(0, 2f, 0); c.size = new Vector3((b - a).magnitude + 0.3f, 4f, thick);
            }
            const float cell = 1f;
            var walk = WalkGrid(L, W, H);
            int nx = walk.GetLength(0), ny = walk.GetLength(1);
            bool Edge(int i, int j)        // forest beside walkable ground (eight neighbours: no corner slips through)
            {
                if (walk[i, j]) return false;
                for (int a = -1; a <= 1; a++)
                    for (int b = -1; b <= 1; b++)
                    {
                        int x = i + a, y = j + b;
                        if (x >= 0 && y >= 0 && x < nx && y < ny && walk[x, y]) return true;
                    }
                return false;
            }
            int made = 0;
            for (int j = 0; j < ny; j++)
                for (int i = 0; i < nx;)
                {
                    if (!Edge(i, j)) { i++; continue; }
                    int i1 = i;
                    while (i1 + 1 < nx && i1 + 1 - i < 8 && Edge(i1 + 1, j)) i1++;      // runs of up to 8 m keep each box near the ground
                    float y = (j + 0.5f) * cell;
                    Wall(new Vector2(i * cell, y), new Vector2((i1 + 1) * cell, y), $"Wall_{made++}", cell);
                    i = i1 + 1;
                }
            // the border, except where an exit's road leaves the map
            var corners = new[] { new Vector2(0, 0), new Vector2(W, 0), new Vector2(W, H), new Vector2(0, H) };
            for (int s = 0; s < 4; s++)
            {
                Vector2 a = corners[s], b = corners[(s + 1) % 4];
                int n = Mathf.CeilToInt((b - a).magnitude / 4f);
                for (int k = 0; k < n; k++)
                {
                    Vector2 p0 = Vector2.Lerp(a, b, k / (float)n), p1 = Vector2.Lerp(a, b, (k + 1) / (float)n);
                    Wall(p0, p1, "Border");
                }
            }
        }

        /// <summary>the walkable ground on a one-metre grid (cell (i, j) centred on (i + 0.5, j + 0.5) in plan metres): inside
        /// the clearings up to the forest's `wallAt`, and a band along every road. Walls() walls its outline; the bake leaves
        /// out the rest (<see cref="Outside"/>)</summary>
        static bool[,] WalkGrid(JObject lay, float w, float h)
        {
            float ring = (float?)lay["forest"]?["wallAt"] ?? 1.08f;
            var cs = Clearings(lay, w, h);
            var rds = (lay["roads"] as JArray ?? new JArray()).Select(r => (pts: Spline(((JArray)r["points"]).Select(V).ToList()), width: (float?)r["width"] ?? 3f)).ToList();
            int nx = Mathf.CeilToInt(w), ny = Mathf.CeilToInt(h);
            var walk = new bool[nx, ny];
            for (int i = 0; i < nx; i++)
                for (int j = 0; j < ny; j++)
                {
                    var q = new Vector2(i + 0.5f, j + 0.5f);
                    walk[i, j] = Union(q, cs) < ring || rds.Any(r => DistToPolyline(q, r.pts) < r.width / 2 + 1.0f);
                }
            return walk;
        }

        /// <summary>the ground beyond the walls, in plan rectangles (x, y, w, h), for the bake to leave out (KitNavBake marks
        /// them Not Walkable): the one-metre cells off the walkable grid -- the walls' own cells too, so nothing is left on
        /// their tops -- in runs along each row, joined north while a row repeats them; and the forest drawn round the map.
        /// Without it the forest carried a navmesh of its own, bigger than the map's, for a spawn point by the wall to snap
        /// to (cut off from the clearing) and a wander or a click to land on. Reads the layout, so it works on a map loaded
        /// from its scene.</summary>
        public List<Rect> Outside()
        {
            var lay = JObject.Parse(string.IsNullOrWhiteSpace(layout) ? "{}" : layout);
            var size = lay["size"] as JArray;
            float w = size != null ? (float)size[0] : 100f, h = size != null ? (float)size[1] : 100f;
            float m = ((float?)lay["margin"] ?? 24f) + 8f;
            var walk = WalkGrid(lay, w, h);
            int nx = walk.GetLength(0), ny = walk.GetLength(1);
            var o = new List<Rect>();
            var open = new Dictionary<(int, int), Rect>();        // the runs still growing north, by their first and last cell
            for (int j = 0; j <= ny; j++)
            {
                var next = new Dictionary<(int, int), Rect>();
                for (int i = 0; j < ny && i < nx;)
                {
                    if (walk[i, j]) { i++; continue; }
                    int i1 = i;
                    while (i1 + 1 < nx && !walk[i1 + 1, j]) i1++;
                    next[(i, i1)] = open.TryGetValue((i, i1), out var r) ? new Rect(r.x, r.y, r.width, r.height + 1) : new Rect(i, j, i1 - i + 1, 1);
                    open.Remove((i, i1));
                    i = i1 + 1;
                }
                o.AddRange(open.Values);
                open = next;
            }
            o.Add(new Rect(-m, -m, w + 2 * m, m));                  // the forest round the map: south, north, west, east
            o.Add(new Rect(-m, h, w + 2 * m, m));
            o.Add(new Rect(-m, 0, m, h));
            o.Add(new Rect(w, 0, m, h));
            return o;
        }
    }
}
