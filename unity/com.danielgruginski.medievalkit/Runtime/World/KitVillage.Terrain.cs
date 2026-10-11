using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Terrain tiles on an outdoor map (2026-10-11, the user: the kit's terrain tiles "as an extra tool for building
    /// things ... to add some terrain variation on the maps"). The layout's "terrain" raises ground in 1.5 m tiers on a
    /// 3 m grid -- terraces, plateaus, knolls with cliff sides -- built from the kit's dual-grid tiles (SM_VKT_*) as
    /// vk_terrain lays them: marching squares on the grid's corners, each corner taking the levels of the four cells
    /// meeting there; a flat tile at their lowest level (above the ground), a cliff layer for every level above that, so a
    /// tall step stacks (a layer on an identical one drops its skirt); variants by a hash of the corner, square ones where
    /// an area is "stiff". Ramps and stairs climb a step where the layout puts them (a ramp cell climbs towards its higher
    /// neighbour: the cliff tiles on that edge become half ramps, or a middle one between two). The cliffs are dressed as
    /// vk_terrain's tk_cliff_dress does: boulders sunk in the face, plants and stones on the lip, lip grass on the middle
    /// ledges of stacked cliffs, rubble and plants at the foot. The tiles are merged into one mesh in the ground's own
    /// space so they share its material (the grass, the roads and the paving painted into its control map carry on over
    /// the tops), with a collider; the level-0 ground stays the ground mesh, flattened towards a cliff's foot and sunk
    /// under the raised cells. Height (pieces, markers, the walk test) stands on the tiers.
    /// </summary>
    public partial class KitVillage
    {
        const float TT = 3f, Tier = 1.5f;
        const int EMPTY = 0, FULL = 1, EDGE = 2, OUTER = 3, INNER = 4, SADDLE = 5;
        static readonly string[] CaseNames = { "Empty", "Full", "Edge", "Outer", "Inner", "Saddle" };
        // marching squares on the corners SW 1, SE 2, NE 4, NW 8 (set: at or above the layer) -> (case, quarter turns
        // anticlockwise from the canonical piece), vk_terrain's MS
        static readonly (int c, int r)[] MS =
        {
            (EMPTY, 0), (OUTER, 1), (OUTER, 2), (EDGE, 2), (OUTER, 3), (SADDLE, 0), (EDGE, 3), (INNER, 2),
            (OUTER, 0), (EDGE, 1), (SADDLE, 1), (INNER, 1), (EDGE, 0), (INNER, 0), (INNER, 3), (FULL, 0),
        };
        static readonly (int dx, int dy)[] DirV = { (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0) };   // ramp: 1 N, 2 E, 3 S, 4 W

        int tW, tH;
        Vector2 tO;
        int[,] tLevel, tRamp;
        bool[,] tStair, tWalled, tStiff;
        float tDress;
        /// <summary>the terrain tiles merged (null: the layout has no terrain); the editor saves it beside the ground</summary>
        public Mesh TerrainMesh { get; private set; }
        MeshCollider terrainCollider;
        List<(Vector2 step, Vector2 dv)> rampSteps;        // each ramp's step (its middle) and the way it climbs, read once
        bool HasTerrain => tLevel != null;

        static readonly string[] DressFace = { "SM_VK_Rock_Boulder_A", "SM_VK_Rock_Boulder_B", "SM_VK_Rock_Boulder_Flat" };
        static readonly string[] DressRubble = { "SM_VK_Rock_Small_A", "SM_VK_Rock_Small_B", "SM_VK_Rock_Pebbles", "SM_VK_Rock_Small_A", "SM_VK_Rock_Cluster" };
        static readonly string[] DressPlants = { "SM_VK_Plant_Fern", "SM_VK_Plant_TallGrass", "SM_VK_Bush_Round", "SM_VK_Plant_Fern", "SM_VK_Plant_TallGrass" };
        static readonly (string piece, float s0, float s1)[] DressLip =
        {
            ("SM_VK_Plant_Fern", 0.6f, 0.85f), ("SM_VK_Bush_Round", 0.35f, 0.5f), ("SM_VK_Rock_Small_A", 0.6f, 0.95f),
            ("SM_VK_Plant_TallGrass", 0.75f, 1f), ("SM_VK_Rock_Small_B", 0.6f, 0.9f),
        };
        const string LipGrass = "SM_VKT_LipGrass";

        /// <summary>every piece a layout's terrain may use (the editor hands them to the map)</summary>
        public static IEnumerable<string> TerrainPieces()
        {
            yield return "SM_VKT_Cliff_Full_A";
            foreach (var v in new[] { "A", "B", "C" }) yield return "SM_VKT_Cliff_Edge_" + v;
            foreach (var c in new[] { "Outer", "Inner" }) foreach (var v in new[] { "A", "B", "Sq" }) yield return $"SM_VKT_Cliff_{c}_{v}";
            yield return "SM_VKT_Cliff_Saddle_A";
            foreach (var h in new[] { "HalfE", "HalfW" }) { yield return $"SM_VKT_Ramp_{h}_A"; yield return $"SM_VKT_Ramp_{h}_W"; yield return $"SM_VKT_Stair_{h}_A"; }
            yield return "SM_VKT_Ramp_Mid_A"; yield return "SM_VKT_Stair_Mid_A";
            foreach (var n in DressFace.Concat(DressRubble).Concat(DressPlants).Concat(DressLip.Select(d => d.piece)).Distinct()) yield return n;
            yield return LipGrass;
        }

        // ------------------------------------------------------------------ the grid
        /// <summary>the layout's terrain as a grid of cell levels, ramps and stairs (before anything stands on the ground)</summary>
        void ParseTerrain()
        {
            tLevel = null; TerrainMesh = null; terrainCollider = null; rampSteps = null;
            if (!(L["terrain"] is JObject T)) return;
            tO = T["origin"] != null ? V(T["origin"]) : Vector2.zero;
            tW = Mathf.Max(1, Mathf.CeilToInt((W - tO.x) / TT));
            tH = Mathf.Max(1, Mathf.CeilToInt((H - tO.y) / TT));
            tLevel = new int[tW, tH]; tRamp = new int[tW, tH];
            tStair = new bool[tW, tH]; tWalled = new bool[tW, tH]; tStiff = new bool[tW, tH];
            tDress = (float?)T["dress"] ?? 1f;
            int ai = 0;
            foreach (var a in T["areas"] as JArray ?? new JArray())
            {
                int lv = Mathf.Clamp((int?)a["level"] ?? 1, 0, 8);
                bool stiff = (bool?)a["stiff"] ?? false;
                var inside = Shape(a, 53 + ai++);
                if (inside == null) { notes.Add("terrain area without rect, ellipse or poly"); continue; }
                for (int j = 0; j < tH; j++)
                    for (int i = 0; i < tW; i++)
                        if (inside(CellMid(i, j))) { tLevel[i, j] = lv; if (stiff) tStiff[i, j] = true; }
            }
            foreach (var rp in T["ramps"] as JArray ?? new JArray())
            {
                var at = V(rp["at"]);
                if (!Cell(at, out int ri, out int rj)) { notes.Add($"terrain ramp at {at} is off the grid"); continue; }
                int dir = Array.IndexOf(new[] { "", "N", "E", "S", "W" }, ((string)rp["dir"] ?? "").ToUpperInvariant());
                if (dir <= 0)                                                  // towards the neighbour one level up
                    for (int d = 1; d <= 4 && dir <= 0; d++)
                        if (Lv(ri + DirV[d].dx, rj + DirV[d].dy) == tLevel[ri, rj] + 1 && In(ri + DirV[d].dx, rj + DirV[d].dy)) dir = d;
                if (dir <= 0) { notes.Add($"terrain ramp at {at}: no cell one level up beside it"); continue; }
                int width = Mathf.Max(1, (int?)rp["width"] ?? 1);
                int px = Mathf.Abs(DirV[dir].dy), py = Mathf.Abs(DirV[dir].dx);   // across the ramp
                for (int k = 0; k < width; k++)
                {
                    int o = k - (width - 1) / 2, ci = ri + px * o, cj = rj + py * o;
                    if (!In(ci, cj)) continue;
                    if (Lv(ci + DirV[dir].dx, cj + DirV[dir].dy) != tLevel[ci, cj] + 1)
                        notes.Add($"terrain ramp at {at}: cell ({ci}, {cj}) has no step of one level ahead");
                    tRamp[ci, cj] = dir;
                    tStair[ci, cj] = (bool?)rp["stair"] ?? false;
                    tWalled[ci, cj] = (bool?)rp["walled"] ?? false;
                }
            }
        }

        /// <summary>a terrain area's test: {"rect": [x0, y0, x1, y1]}, {"ellipse": {centre, radius, lumps}} or {"poly": [[x, y], ...]}</summary>
        static Func<Vector2, bool> Shape(JToken a, int seed)
        {
            if (a["rect"] is JArray r && r.Count >= 4)
            {
                float x0 = Mathf.Min((float)r[0], (float)r[2]), x1 = Mathf.Max((float)r[0], (float)r[2]);
                float y0 = Mathf.Min((float)r[1], (float)r[3]), y1 = Mathf.Max((float)r[1], (float)r[3]);
                return q => q.x >= x0 && q.x <= x1 && q.y >= y0 && q.y <= y1;
            }
            if (a["ellipse"] is JObject e)
            {
                var c = V(e["centre"]);
                var rr = e["radius"];
                var rad = rr is JArray ? V(rr) : new Vector2((float?)rr ?? 6f, (float?)rr ?? 6f);
                float lumps = (float?)e["lumps"] ?? 0f;
                return q => Blob(q, c, rad, lumps, seed) < 1f;
            }
            if (a["poly"] is JArray p && p.Count >= 3)
            {
                var poly = p.Select(V).ToArray();
                return q => InPoly(q, poly);
            }
            return null;
        }

        Vector2 CellMid(int i, int j) => tO + new Vector2((i + 0.5f) * TT, (j + 0.5f) * TT);
        bool In(int i, int j) => i >= 0 && j >= 0 && i < tW && j < tH;
        int Lv(int i, int j) => In(i, j) ? tLevel[i, j] : 0;

        bool Cell(Vector2 q, out int i, out int j)
        {
            i = Mathf.FloorToInt((q.x - tO.x) / TT); j = Mathf.FloorToInt((q.y - tO.y) / TT);
            return In(i, j);
        }

        /// <summary>the terrain's level at q (0: the ground, or no terrain)</summary>
        int LevelAt(Vector2 q) => HasTerrain && Cell(q, out int i, out int j) ? tLevel[i, j] : 0;

        /// <summary>how near q is to raised ground (1 at a cliff's foot, 0 from 3.5 m out): the ground's relief flattens
        /// there, so a cliff's toe meets level ground</summary>
        float TerrainNear(Vector2 q)
        {
            if (!HasTerrain) return 0f;
            int ci = Mathf.FloorToInt((q.x - tO.x) / TT), cj = Mathf.FloorToInt((q.y - tO.y) / TT);
            float best = 99f;
            for (int dj = -2; dj <= 2; dj++)
                for (int di = -2; di <= 2; di++)
                {
                    int i = ci + di, j = cj + dj;
                    if (Lv(i, j) <= 0) continue;
                    float x0 = tO.x + i * TT, y0 = tO.y + j * TT;
                    float dx = Mathf.Max(0f, Mathf.Max(x0 - q.x, q.x - (x0 + TT))), dy = Mathf.Max(0f, Mathf.Max(y0 - q.y, q.y - (y0 + TT)));
                    best = Mathf.Min(best, Mathf.Sqrt(dx * dx + dy * dy));
                }
            return best >= 3.5f ? 0f : Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(3.5f, 0.5f, best));
        }

        /// <summary>within r of a cliff line or a ramp (the forest, the undergrowth, stragglers and scatter keep off: a
        /// tree on a lip or a bush in a face reads wrong)</summary>
        bool NearCliff(Vector2 q, float r)
        {
            if (!HasTerrain) return false;
            int l = LevelAt(q);
            for (int k = 0; k < 8; k++)
            {
                float a = k * Mathf.PI / 4f;
                if (LevelAt(q + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * r) != l) return true;
            }
            return false;
        }

        /// <summary>on a flight of stairs (its half of the low cell and of the cell above): no grass there</summary>
        bool OnStair(Vector2 q)
        {
            if (!HasTerrain || !Cell(q, out int i, out int j)) return false;
            float lx = q.x - (tO.x + i * TT), ly = q.y - (tO.y + j * TT);           // within the cell, 0..3
            float Edge(int d) => d == 1 ? TT - ly : d == 2 ? TT - lx : d == 3 ? ly : lx; // distance to the cell's side towards d
            if (tRamp[i, j] != 0 && tStair[i, j] && Edge(tRamp[i, j]) < 1.7f) return true;
            for (int d = 1; d <= 4; d++)                                            // the cell above a flight: its lower half
            {
                int bi = i - DirV[d].dx, bj = j - DirV[d].dy;
                if (In(bi, bj) && tRamp[bi, bj] == d && tStair[bi, bj] && Edge((d + 1) % 4 + 1) < 1.7f) return true;
            }
            return false;
        }

        /// <summary>the raised cells as rows of rectangles (plan metres, pulled 0.4 m in): the navmesh bake makes the
        /// ground under them Not Walkable up to a metre above it (a tall hill's hollow inside carries no navmesh)</summary>
        public List<Rect> UnderTerrain()
        {
            var list = new List<Rect>();
            if (!HasTerrain) return list;
            for (int j = 0; j < tH; j++)
                for (int i = 0; i < tW; i++)
                {
                    if (tLevel[i, j] <= 0) continue;
                    int s = i;
                    while (i + 1 < tW && tLevel[i + 1, j] > 0) i++;
                    list.Add(Rect.MinMaxRect(tO.x + s * TT + 0.4f, tO.y + j * TT + 0.4f, tO.x + (i + 1) * TT - 0.4f, tO.y + (j + 1) * TT - 0.4f));
                }
            return list;
        }

        // ------------------------------------------------------------------ the tiles
        static uint Hash(int x, int y, int z, uint seed = 0)
        {
            unchecked
            {
                uint h = seed;
                h ^= (uint)x * 0x8da6b343u; h ^= (uint)y * 0xd8163841u; h ^= (uint)z * 0xcb1ab31fu;
                h ^= h >> 16; h *= 0x7feb352du; h ^= h >> 15; h *= 0x846ca68bu; h ^= h >> 16;
                return h;
            }
        }

        /// <summary>vk_terrain's pick_var: Edge A/B/C 25/45/30, Outer and Inner A/B 40/60, the square ones where stiff</summary>
        static string Variant(int cas, uint h, bool stiff)
        {
            if (cas != EDGE && cas != OUTER && cas != INNER) return "A";
            if (stiff) return cas == EDGE ? "A" : "Sq";
            float x = ((h >> 8) % 1000) / 1000f;
            if (cas == EDGE) return x < 0.25f ? "A" : x < 0.70f ? "B" : "C";
            return x < 0.4f ? "A" : "B";
        }

        /// <summary>an Edge layer crossed by a ramp: "HalfE" / "HalfW" (on the canonical piece's east or west side), "Mid"
        /// (both), or null (vk_terrain's ramp_override)</summary>
        string RampOver((int lv, int i, int j)[] c, int l, int r, out bool stair, out bool walled)
        {
            stair = walled = false;
            int hit = 0;
            foreach (int cs in new[] { 1, 3 })                                // the canonical piece's crossing sides
            {
                int ws = (cs + r) % 4;
                var a = c[ws]; var b = c[(ws + 1) % 4];
                var (lo, hi) = a.lv < b.lv ? (a, b) : (b, a);
                if (lo.lv != l - 1 || hi.lv != l) continue;
                int d = tRamp[lo.i, lo.j];
                if (d == 0 || DirV[d] != (hi.i - lo.i, hi.j - lo.j)) continue;
                hit |= cs == 1 ? 1 : 2;
                stair |= tStair[lo.i, lo.j]; walled |= tWalled[lo.i, lo.j];
            }
            return hit == 3 ? "Mid" : hit == 1 ? "HalfE" : hit == 2 ? "HalfW" : null;
        }

        /// <summary>the tiles: merged into one mesh in the ground's own space (the ground's material on the terrain's
        /// pieces, the stairs' own on theirs), a collider; then the cliffs dressed</summary>
        void Terrain()
        {
            if (!HasTerrain) return;
            var recs = new List<(int I, int J, int l, string piece, int r, bool stacked)>();
            for (int J = 0; J <= tH; J++)
                for (int I = 0; I <= tW; I++)
                {
                    // the four cells meeting at this grid point: SW, SE, NE, NW (held to the grid at its edges)
                    var c = new[] { C(I - 1, J - 1), C(I, J - 1), C(I, J), C(I - 1, J) };
                    int lo = c.Min(x => x.lv), hi = c.Max(x => x.lv);
                    if (hi <= 0) continue;
                    bool stiff = c.Any(x => tStiff[x.i, x.j]);
                    if (lo >= 1) recs.Add((I, J, lo, "SM_VKT_Cliff_Full_A", (int)(Hash(I, J, 0) & 3), false));
                    int pc = -1, pr = -1;
                    for (int l = lo + 1; l <= hi; l++)
                    {
                        int m = 0;
                        for (int k = 0; k < 4; k++) if (c[k].lv >= l) m |= 1 << k;
                        var (cas, r) = MS[m];
                        if (cas == EMPTY) { pc = -1; continue; }
                        string piece = null;
                        if (cas == EDGE)
                        {
                            var ro = RampOver(c, l, r, out bool stair, out bool walled);
                            if (ro != null) piece = stair ? $"SM_VKT_Stair_{ro}_A" : $"SM_VKT_Ramp_{ro}_{(ro != "Mid" && walled ? "W" : "A")}";
                        }
                        bool cliff = piece == null;
                        if (cliff) piece = $"SM_VKT_Cliff_{CaseNames[cas]}_{Variant(cas, Hash(I, J, l), stiff)}";
                        // a cliff layer on an identical one (same case, same turn) needs no skirt: it would show on the
                        // lip of the layer below
                        recs.Add((I, J, l, piece, r, cliff && cas != FULL && pc == cas && pr == r));
                        pc = cliff ? cas : -1; pr = r;
                    }
                }

            var verts = new List<Vector3>(); var norms = new List<Vector3>(); var cols = new List<Color>();
            var tris = new Dictionary<Material, List<int>>();
            var cache = new Dictionary<string, (Vector3[] v, Vector3[] n, Color[] col, (int[] t, Material m)[] subs)>();
            int missing = 0;
            foreach (var rec in recs)
            {
                if (!cache.TryGetValue(rec.piece, out var src))
                {
                    var pf = Prefab(rec.piece);
                    var mf = pf != null ? pf.GetComponentInChildren<MeshFilter>() : null;
                    if (mf == null || mf.sharedMesh == null) { cache[rec.piece] = src = (null, null, null, null); }
                    else
                    {
                        var mesh = mf.sharedMesh;
                        var mats = mf.GetComponent<MeshRenderer>() != null ? mf.GetComponent<MeshRenderer>().sharedMaterials : new Material[0];
                        var toRoot = pf.transform.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                        var v = mesh.vertices.Select(p => toRoot.MultiplyPoint3x4(p)).ToArray();
                        var n = mesh.normals.Select(p => toRoot.MultiplyVector(p).normalized).ToArray();
                        var cl = mesh.colors.Length == v.Length ? mesh.colors : Enumerable.Repeat(Color.white, v.Length).ToArray();
                        var subs = new (int[], Material)[mesh.subMeshCount];
                        for (int s = 0; s < mesh.subMeshCount; s++)
                        {
                            var m = s < mats.Length ? mats[s] : null;
                            // the terrain's pieces take the map's ground material (its grass, roads and paving), the
                            // stairs keep their own
                            if (m == null || m.name.StartsWith("M_VK_Terrain")) m = GroundMaterialInstance != null ? GroundMaterialInstance : m;
                            subs[s] = (mesh.GetTriangles(s), m);
                        }
                        cache[rec.piece] = src = (v, n, cl, subs);
                    }
                }
                if (src.v == null) { missing++; continue; }
                var rot = Quaternion.Euler(0f, -90f * rec.r, 0f);              // an anticlockwise quarter in plan: -90 about y
                var at = Local(tO.x + TT * rec.I + M, tO.y + TT * rec.J + M, rec.l * Tier);   // the ground object's space
                int b = verts.Count;
                for (int k = 0; k < src.v.Length; k++)
                {
                    verts.Add(rot * src.v[k] + at);
                    norms.Add(k < src.n.Length ? rot * src.n[k] : Vector3.up);
                    cols.Add(src.col[k]);
                }
                foreach (var (t, m) in src.subs)
                {
                    var key = m != null ? m : GroundMaterialInstance;
                    if (key == null) continue;
                    if (!tris.TryGetValue(key, out var list)) tris[key] = list = new List<int>();
                    for (int k = 0; k + 2 < t.Length; k += 3)
                    {
                        if (rec.stacked && Mathf.Min(src.v[t[k]].y, Mathf.Min(src.v[t[k + 1]].y, src.v[t[k + 2]].y)) < -2.5f) continue;   // the skirt
                        list.Add(b + t[k]); list.Add(b + t[k + 1]); list.Add(b + t[k + 2]);
                    }
                }
            }
            if (missing > 0) notes.Add($"terrain: {missing} tiles had no piece");
            if (verts.Count == 0) { notes.Add("terrain: nothing raised"); return; }
            var tm = new Mesh { name = $"{name}_Terrain", indexFormat = verts.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16 };
            tm.SetVertices(verts); tm.SetNormals(norms); tm.SetColors(cols);
            var keys = tris.Keys.ToList();
            tm.subMeshCount = keys.Count;
            for (int s = 0; s < keys.Count; s++) tm.SetTriangles(tris[keys[s]], s);
            tm.RecalculateBounds();
            TerrainMesh = tm;
            var go = new GameObject("Terrain");
            go.transform.SetParent(groundT, false);
            go.transform.localPosition = Local(-M, -M, 0f);                    // as the ground: the material projects from there
            go.AddComponent<MeshFilter>().sharedMesh = tm;
            go.AddComponent<MeshRenderer>().sharedMaterials = keys.ToArray();
            terrainCollider = go.AddComponent<MeshCollider>();
            terrainCollider.sharedMesh = tm;
            int raised = 0;
            for (int j = 0; j < tH; j++) for (int i = 0; i < tW; i++) if (tLevel[i, j] > 0) raised++;
            notes.Add($"terrain: {raised} raised cells, {recs.Count} tiles, {verts.Count} verts");
        }

        /// <summary>the cliffs' and ramps' dressing (Build calls it once the buildings, props and trees stand: it keeps out
        /// of their footprints)</summary>
        void DressTerrain()
        {
            if (!HasTerrain || TerrainMesh == null) return;
            DressCliffs();
            DressRamps();
        }

        /// <summary>may a dressing piece go here: on the level it is meant for (any: -1), off every ramp's tiles, out of
        /// what stands on the map (buildings, props, gardens, trees)</summary>
        bool DressFree(float x, float y, int level)
        {
            var q = new Vector2(x, y);
            if (level >= 0 && LevelAt(q) != level) return false;
            if (OnRampTile(q)) return false;
            foreach (var (poly, _) in occupied) if (DistToPoly(q, poly) < 0.3f) return false;
            return true;
        }

        /// <summary>within a ramp's tiles (its slope, its earth banks and the cliff bending down to it): 1.5 m either side of
        /// its step, from 1.5 m past one side of the low cell to 1.5 m past the other</summary>
        bool OnRampTile(Vector2 q)
        {
            if (!HasTerrain) return false;
            if (rampSteps == null)
            {
                rampSteps = new List<(Vector2 step, Vector2 dv)>();
                for (int j = 0; j < tH; j++)
                    for (int i = 0; i < tW; i++)
                        if (tRamp[i, j] != 0)
                        {
                            var dv = new Vector2(DirV[tRamp[i, j]].dx, DirV[tRamp[i, j]].dy);
                            rampSteps.Add((CellMid(i, j) + dv * (TT / 2f), dv));
                        }
            }
            foreach (var (step, dv) in rampSteps)
            {
                var r = q - step;
                if (Mathf.Abs(Vector2.Dot(r, dv)) <= TT / 2f && Mathf.Abs(Vector2.Dot(r, new Vector2(-dv.y, dv.x))) <= TT) return true;
            }
            return false;
        }

        /// <summary>a tall tree here would hide a cliff from the camera or seem to grow out of a lip. The camera looks north
        /// 50 degrees down, so a crown h m up covers the ground about 0.84 h north of its trunk: no tree up to 14 m south of
        /// a higher level, nor 3 m to either side of that strip (past a face's end); none on a raised top within 4 m of its
        /// own south lip (its crown over the face); none where its foot hides behind a higher top (<see cref="HidesFoot"/>)
        /// (round 2 of the cliffs pass: an 8 m strip still let the pines' crowns bury the faces)</summary>
        bool Shades(Vector2 q)
        {
            if (!HasTerrain) return false;
            int l = LevelAt(q);
            for (float k = 1.5f; k <= 14f; k += 1.5f)
                for (float s = -3f; s <= 3f; s += 3f)
                    if (LevelAt(q + new Vector2(s, k)) > l) return true;
            if (l > 0) for (float k = 1f; k <= 4f; k += 1f) if (LevelAt(q - new Vector2(0f, k)) < l) return true;
            return HidesFoot(q, 2f);
        }

        /// <summary>something standing here would have its foot hidden behind a higher top to its south (the camera sees
        /// over a drop d m about 0.84 d of the ground behind it): within `pad` + 0.84 x the drop of a north edge</summary>
        bool HidesFoot(Vector2 q, float pad)
        {
            if (!HasTerrain) return false;
            int l = LevelAt(q);
            for (float k = 0.75f; k <= pad + 0.84f * 3f * Tier; k += 0.75f)
            {
                int d = LevelAt(q - new Vector2(0f, k)) - l;
                if (d > 0 && k <= pad + 0.84f * d * Tier) return true;
            }
            return false;
        }

        /// <summary>vk_terrain's tk_ramp_dress: a few stones and plants where each ramp or flight meets the cliffs on its
        /// two sides (they break up the joint and its earth bank; beside a flight, out past its flanking wall); a walled
        /// ramp stays clean</summary>
        void DressRamps()
        {
            if (tDress <= 0f) return;
            var rng = new System.Random(((int?)L["seed"] ?? 1) * 37 + 7);
            // (round 2: out beyond the bank boulder -- a tuft on it and a pebble in every mouth made the ramps look stamped)
            var picks = new (string piece, float lx, float ly, float s, float skip)[]
            {
                ("SM_VK_Rock_Small_A", -1.8f, -1.35f, 0.9f, 0.35f), ("SM_VK_Plant_Fern", -2.4f, -1.2f, 0.8f, 0.3f),
                ("SM_VK_Plant_TallGrass", -2.0f, -0.7f, 1f, 0.3f), ("SM_VK_Rock_Small_B", -0.45f, -1.9f, 0.6f, 0.6f),
            };
            for (int j = 0; j < tH; j++)
                for (int i = 0; i < tW; i++)
                {
                    int d = tRamp[i, j];
                    if (d == 0 || tWalled[i, j]) continue;
                    var (fx, fy) = DirV[d];
                    float wall = tStair[i, j] ? 0.5f : 0f;
                    foreach (var (sx, sy) in new[] { (fy, -fx), (-fy, fx) })
                    {
                        if (In(i + sx, j + sy) && tRamp[i + sx, j + sy] == d) continue;   // a wider ramp goes on that way
                        float cx = tO.x + TT * i + 1.5f + sx * 1f + fx * 1.5f, cy = tO.y + TT * j + 1.5f + sy * 1f + fy * 1.5f;
                        float z = tLevel[i, j] * Tier;
                        foreach (var pk in picks)
                        {
                            if (rng.NextDouble() < pk.skip) continue;
                            float lx = pk.lx - wall;
                            if (wall > 0f && lx > -wall - 0.15f) continue;
                            // local x points to the ramp (against the side), local y uphill
                            float wx = cx - sx * lx + fx * pk.ly, wy = cy - sy * lx + fy * pk.ly;
                            bool clear = true;
                            foreach (var (poly, _) in occupied) if (DistToPoly(new Vector2(wx, wy), poly) < 0.3f) { clear = false; break; }
                            if (!clear) continue;
                            var pf = Prefab(pk.piece);
                            if (pf == null) continue;
                            var go = Spawn(pf, natureT);
                            go.transform.localPosition = Local(wx, wy, z - 0.03f);
                            go.transform.localRotation = Turn((float)rng.NextDouble() * 360f);
                            go.transform.localScale = Vector3.one * pk.s * (0.85f + 0.3f * (float)rng.NextDouble());
                        }
                        // a boulder on the earth bank beside the ramp's tongue: it hides the bank's pale wedge and the
                        // foot of the face's open end (round 2 of the cliffs pass: every ramp read as a gap with two
                        // flaps); long side along the bank, from the ramp's foot up to the face, sunk a little, its inner
                        // edge at the tongue's edge
                        {
                            bool big = rng.NextDouble() < 0.5;
                            float lx = -0.62f - wall, ly = -0.55f;
                            float wx = cx - sx * lx + fx * ly, wy = cy - sy * lx + fy * ly;
                            bool clear = true;
                            foreach (var (poly, _) in occupied) if (DistToPoly(new Vector2(wx, wy), poly) < 0.3f) { clear = false; break; }
                            var pf = clear ? Prefab(big ? "SM_VK_Rock_Boulder_B" : "SM_VK_Rock_Boulder_A") : null;
                            if (pf != null)
                            {
                                var go = Spawn(pf, natureT);
                                go.transform.localPosition = Local(wx, wy, z - 0.12f);
                                go.transform.localRotation = Turn((fx != 0 ? 0f : 90f) + (float)rng.NextDouble() * 40f - 20f);
                                go.transform.localScale = Vector3.one * (big ? 0.56f : 0.88f) * (0.9f + 0.2f * (float)rng.NextDouble());
                            }
                        }
                    }
                }
        }

        (int lv, int i, int j) C(int i, int j)
        {
            i = Mathf.Clamp(i, 0, tW - 1); j = Mathf.Clamp(j, 0, tH - 1);
            return (tLevel[i, j], i, j);
        }

        /// <summary>vk_terrain's tk_cliff_dress along the straight runs of every step without a ramp: a boulder sunk in
        /// the face, plants and stones on the lip, lip grass on the middle ledges of a stacked cliff, rubble and plants at
        /// the foot; "dress" in the layout scales it (0: none)</summary>
        void DressCliffs()
        {
            if (tDress <= 0f) return;
            var rng = new System.Random(((int?)L["seed"] ?? 1) * 31 + 5);
            float U(float a, float b) => a + (float)rng.NextDouble() * (b - a);
            string Pick(string[] a) => a[rng.Next(a.Length)];
            void Put(string piece, float x, float y, float z, float deg, float s)
            {
                var pf = Prefab(piece);
                if (pf == null) return;
                var go = Spawn(pf, natureT);
                go.transform.localPosition = Local(x, y, z);
                go.transform.localRotation = Turn(deg);
                go.transform.localScale = Vector3.one * s;
            }
            for (int j = 0; j < tH; j++)
                for (int i = 0; i < tW; i++)
                    foreach (var (di, dj) in new[] { (1, 0), (0, 1) })
                    {
                        int ii = i + di, jj = j + dj;
                        if (ii >= tW || jj >= tH) continue;
                        int la = tLevel[i, j], lb = tLevel[ii, jj];
                        if (la == lb || tRamp[i, j] != 0 || tRamp[ii, jj] != 0) continue;
                        var (hiI, hiJ, loI, loJ) = la > lb ? (i, j, ii, jj) : (ii, jj, i, j);
                        int ox = loI - hiI, oy = loJ - hiJ, tx = Mathf.Abs(oy), ty = Mathf.Abs(ox);
                        float cx = tO.x + 1.5f * (hiI + loI) + 1.5f, cy = tO.y + 1.5f * (hiJ + loJ) + 1.5f;
                        bool Straight(int sg) => Lv(hiI + sg * tx, hiJ + sg * ty) == tLevel[hiI, hiJ] && Lv(loI + sg * tx, loJ + sg * ty) == tLevel[loI, loJ];
                        bool sl = Straight(-1), sr = Straight(1);
                        float Along(float lim = 1.1f) => U(sl ? -lim : -0.2f, sr ? lim : 0.2f);
                        int lHi = tLevel[hiI, hiJ], lLo = tLevel[loI, loJ];
                        float zl = lLo * Tier, h = (lHi - lLo) * Tier;
                        if (oy < 0 && rng.NextDouble() < 0.35 * tDress)          // a boulder sunk into a face the camera sees (on
                        {                                                         // the others it reads as a stone on the lip)
                            float t = Along(), off = U(-0.05f, 0.2f), zb = zl + h * U(0.12f, 0.4f);
                            float bx = cx + tx * t + ox * off, by = cy + ty * t + oy * off;
                            if (DressFree(bx, by, -1)) Put(Pick(DressFace), bx, by, zb, U(0f, 360f), U(0.42f, 0.72f) * (h <= Tier ? 1f : 1.35f));
                        }
                        if (rng.NextDouble() < 0.3 * tDress)                     // plants and stones on the lip
                        {
                            int n = rng.Next(1, 3);
                            for (int k = 0; k < n; k++)
                            {
                                float t = Along(), off = U(-1.4f, -0.9f);        // on the top, a metre back from the lip
                                var d = DressLip[rng.Next(DressLip.Length)];
                                float lx = cx + tx * t + ox * off, ly = cy + ty * t + oy * off;
                                if (DressFree(lx, ly, lHi)) Put(d.piece, lx, ly, lHi * Tier - 0.03f, U(0f, 360f), U(d.s0, d.s1));
                            }
                        }
                        if (lHi - lLo >= 2)                                       // grass on the middle ledges of a stacked cliff
                        {
                            float rot = Mathf.Atan2(oy, ox) * Mathf.Rad2Deg + 90f;
                            for (int lm = lLo + 1; lm < lHi; lm++)
                                foreach (float t0 in new[] { -1.1f, -0.4f, 0.3f, 1f })
                                {
                                    if ((t0 < -0.2f && !sl) || (t0 > 0.2f && !sr) || rng.NextDouble() < 0.45) continue;
                                    float t = t0 + U(-0.15f, 0.15f);
                                    Put(LipGrass, cx + tx * t, cy + ty * t, lm * Tier, rot + U(-8f, 8f), U(0.8f, 1.2f));
                                }
                        }
                        if (rng.NextDouble() < 0.6 * tDress)                     // rubble at the foot
                        {
                            int n = rng.Next(2, 5);
                            for (int k = 0; k < n; k++)
                            {
                                float t = Along(), off = U(0.35f, 0.95f);
                                string nm = Pick(DressRubble);
                                float rx = cx + tx * t + ox * off, ry = cy + ty * t + oy * off;
                                if (DressFree(rx, ry, lLo)) Put(nm, rx, ry, zl - 0.05f, U(0f, 360f), nm.EndsWith("Cluster") ? U(0.35f, 0.55f) : U(0.6f, 1.2f));
                            }
                        }
                        if (rng.NextDouble() < 0.45 * tDress)                    // plants at the foot
                        {
                            float t = Along(), off = U(0.5f, 1f);
                            string nm = Pick(DressPlants);
                            float px = cx + tx * t + ox * off, py = cy + ty * t + oy * off;
                            if (DressFree(px, py, lLo)) Put(nm, px, py, zl, U(0f, 360f), nm.EndsWith("Round") ? U(0.45f, 0.65f) : U(0.7f, 1.05f));
                        }
                    }
        }
    }
}
