using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;
using Rect = MedievalKit.UnityMath.Rect;

namespace MedievalKit;

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
/// ledges of stacked cliffs, rubble and plants at the foot. The tiles are merged into one ArrayMesh in the ground's own
/// space (one surface per material) so they share its material (the grass, the roads and the paving painted into its
/// control map carry on over the tops), with a trimesh collider; the level-0 ground stays the ground mesh, flattened
/// towards a cliff's foot and sunk under the raised cells. Height (pieces, markers, the walk test) stands on the tiers.
/// The sea (2026-10-18, harbour round 1: a docks map): sea cells are level 0 and water, the land beside them one level
/// up; the ground is lowered to the bed under them (1.5 m below level 0, a beach slope where level-0 land meets them),
/// a water plane 0.6 m below level 0 covers them and carries on through the forest margin past the map, and where
/// the land beside them carries a quay flag the cliff layer becomes vk_terrain_quay's harbour wall (qy_pick).
/// Unity: KitVillage.Terrain.cs (same rules; the meshes are built into the scene instead of saved as assets).
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
    /// <summary>the terrain tiles merged (null: the layout has no terrain); saved inside the map's scene</summary>
    public ArrayMesh TerrainMesh { get; private set; }
    StaticBody3D terrainCollider;
    List<(Vector2 step, Vector2 dv)> rampSteps;        // each ramp's step (its middle) and the way it climbs, read once
    bool HasTerrain => tLevel != null;

    // the sea: cells of water at level 0 (vk_terrain's TGrid.water) and the quay flags of the land cells beside them
    // (TGrid.quay: 1 wall, 2 water stairs, 3 slipway)
    bool[,] tSea;
    int[,] tQuay;
    bool HasSea;
    float tQuayDress;
    readonly Dictionary<(int, int), string> quayV = new();   // grid points with a quay tile: its variant
    /// <summary>the water plane over the sea cells (null: no sea)</summary>
    public ArrayMesh SeaMesh { get; private set; }
    /// <summary>the moored hulls' waterline footprints (null: none), drawn with waterMaskMaterial so the sea leaves them
    /// dry</summary>
    public ArrayMesh SeaMaskMesh { get; private set; }
    readonly List<(Node3D go, Vector2 at)> seaHulls = new();
    /// <summary>a boat's hull (it is hollow: the water must not fill it): the kit's ships, boats, rowboat and barge</summary>
    static bool IsHull(string piece) => piece.Contains("_Ship_") || piece.Contains("_Boat_") || piece.EndsWith("_Rowboat") || piece.EndsWith("_Barge");
    /// <summary>the sea's water surface and bed below level 0 (vk_terrain's WATER_Z, BED_Z); the navmesh leaves the sea
    /// out up to SeaWalkTop (the water stairs' landing, 0.35 m below level 0, stays walkable)</summary>
    public const float SeaWater = -0.6f, SeaBed = -1.5f, SeaWalkTop = -0.45f;
    const float SeaSink = 0.03f;                       // the ground this far under the quay tiles' own bed
    static readonly string[] QuayTiles =
    {
        "SM_VKT_Quay_Edge_A", "SM_VKT_Quay_Edge_Stair", "SM_VKT_Quay_Edge_Slip", "SM_VKT_Quay_Outer_A", "SM_VKT_Quay_Inner_A", "SM_VKT_Quay_Saddle_A",
    };
    const string WaterQuad = "SM_VKT_WaterQuad";
    static readonly string[] QuayProps = { "SM_VK_Harbour_Bollard", "SM_VK_Harbour_Fender", "SM_VK_Harbour_Ring" };
    const string SeaMatPath = "res://addons/medieval_kit/Materials/KitSea.tres";
    const string WaterMaskMatPath = "res://addons/medieval_kit/Materials/KitWaterMask.tres";

    static readonly string[] DressFace = { "SM_VK_Rock_Boulder_A", "SM_VK_Rock_Boulder_B", "SM_VK_Rock_Boulder_Flat" };
    static readonly string[] DressRubble = { "SM_VK_Rock_Small_A", "SM_VK_Rock_Small_B", "SM_VK_Rock_Pebbles", "SM_VK_Rock_Small_A", "SM_VK_Rock_Cluster" };
    static readonly string[] DressPlants = { "SM_VK_Plant_Fern", "SM_VK_Plant_TallGrass", "SM_VK_Bush_Round", "SM_VK_Plant_Fern", "SM_VK_Plant_TallGrass" };
    static readonly (string piece, float s0, float s1)[] DressLip =
    {
        ("SM_VK_Plant_Fern", 0.6f, 0.85f), ("SM_VK_Bush_Round", 0.35f, 0.5f), ("SM_VK_Rock_Small_A", 0.6f, 0.95f),
        ("SM_VK_Plant_TallGrass", 0.75f, 1f), ("SM_VK_Rock_Small_B", 0.6f, 0.9f),
    };
    const string LipGrass = "SM_VKT_LipGrass";

    /// <summary>every piece a layout's terrain may use</summary>
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

    /// <summary>and the pieces a terrain's sea uses: the quay tiles, the water quad, the quay dressing</summary>
    public static IEnumerable<string> SeaPieces() => QuayTiles.Concat(QuayProps).Append(WaterQuad);

    // ------------------------------------------------------------------ the grid
    /// <summary>the layout's terrain as a grid of cell levels, ramps and stairs (before anything stands on the ground)</summary>
    void ParseTerrain()
    {
        tLevel = null; TerrainMesh = null; terrainCollider = null; rampSteps = null;
        tSea = null; tQuay = null; HasSea = false; SeaMesh = null; SeaMaskMesh = null; seaHulls.Clear(); quayV.Clear();
        if (L["terrain"] is not JsonObject T) return;
        tO = T["origin"] != null ? V(T["origin"]) : Vector2.zero;
        tW = Mathf.Max(1, Mathf.CeilToInt((W - tO.x) / TT));
        tH = Mathf.Max(1, Mathf.CeilToInt((H - tO.y) / TT));
        tLevel = new int[tW, tH]; tRamp = new int[tW, tH];
        tStair = new bool[tW, tH]; tWalled = new bool[tW, tH]; tStiff = new bool[tW, tH];
        tDress = T["dress"].Fq() ?? 1f;
        int ai = 0;
        foreach (var a in T["areas"] as JsonArray ?? new JsonArray())
        {
            int lv = Mathf.Clamp(a["level"].Iq() ?? 1, 0, 8);
            bool stiff = a["stiff"].Bq() ?? false;
            var inside = TerrainShape(a, 53 + ai++);
            if (inside == null) { notes.Add("terrain area without rect, ellipse or poly"); continue; }
            for (int j = 0; j < tH; j++)
                for (int i = 0; i < tW; i++)
                    if (inside(CellMid(i, j))) { tLevel[i, j] = lv; if (stiff) tStiff[i, j] = true; }
        }
        ParseSea(T);
        foreach (var rp in T["ramps"] as JsonArray ?? new JsonArray())
        {
            var at = V(rp["at"]);
            if (!Cell(at, out int ri, out int rj)) { notes.Add($"terrain ramp at {at} is off the grid"); continue; }
            int dir = Array.IndexOf(new[] { "", "N", "E", "S", "W" }, (rp["dir"].S() ?? "").ToUpperInvariant());
            if (dir <= 0)                                                  // towards the neighbour one level up
                for (int d = 1; d <= 4 && dir <= 0; d++)
                    if (Lv(ri + DirV[d].dx, rj + DirV[d].dy) == tLevel[ri, rj] + 1 && In(ri + DirV[d].dx, rj + DirV[d].dy)) dir = d;
            if (dir <= 0) { notes.Add($"terrain ramp at {at}: no cell one level up beside it"); continue; }
            int width = Mathf.Max(1, rp["width"].Iq() ?? 1);
            int px = Mathf.Abs(DirV[dir].dy), py = Mathf.Abs(DirV[dir].dx);   // across the ramp
            for (int k = 0; k < width; k++)
            {
                int o = k - (width - 1) / 2, ci = ri + px * o, cj = rj + py * o;
                if (!In(ci, cj)) continue;
                if (Lv(ci + DirV[dir].dx, cj + DirV[dir].dy) != tLevel[ci, cj] + 1)
                    notes.Add($"terrain ramp at {at}: cell ({ci}, {cj}) has no step of one level ahead");
                tRamp[ci, cj] = dir;
                tStair[ci, cj] = rp["stair"].Bq() ?? false;
                tWalled[ci, cj] = rp["walled"].Bq() ?? false;
            }
        }
    }

    /// <summary>the terrain's "sea": cells whose middle lies in one of its shapes become sea (level 0, water; after the
    /// areas, so it cuts into them), and with "quay" (default true) every land cell touching them (8 neighbours) a quay
    /// wall; then "quays" sets the flag of the land cells in its shapes: "kind" wall / stairs / slip / none</summary>
    void ParseSea(JsonObject T)
    {
        tSea = new bool[tW, tH]; tQuay = new int[tW, tH];
        tQuayDress = T["quayDress"].Fq() ?? tDress;
        int si = 0;
        var walls = new List<(int, int)>();
        foreach (var s in T["sea"] as JsonArray ?? new JsonArray())
        {
            var inside = TerrainShape(s, 71 + si++);
            if (inside == null) { notes.Add("terrain sea without rect, ellipse or poly"); continue; }
            bool quay = s["quay"].Bq() ?? true;
            for (int j = 0; j < tH; j++)
                for (int i = 0; i < tW; i++)
                    if (inside(CellMid(i, j)))
                    {
                        tLevel[i, j] = 0; tSea[i, j] = HasSea = true;
                        if (quay) for (int dj = -1; dj <= 1; dj++) for (int di = -1; di <= 1; di++) if (In(i + di, j + dj)) walls.Add((i + di, j + dj));
                    }
        }
        foreach (var (i, j) in walls) if (!tSea[i, j]) tQuay[i, j] = 1;
        int qi = 0;
        foreach (var q in T["quays"] as JsonArray ?? new JsonArray())
        {
            var inside = TerrainShape(q, 89 + qi++);
            if (inside == null) { notes.Add("terrain quay without rect, ellipse or poly"); continue; }
            string kind = (q["kind"].S() ?? "wall").ToLowerInvariant();
            int flag = Array.IndexOf(new[] { "none", "wall", "stairs", "slip" }, kind);
            if (flag < 0) { notes.Add($"terrain quay kind {kind}: wall, stairs, slip or none"); continue; }
            for (int j = 0; j < tH; j++)
                for (int i = 0; i < tW; i++)
                    if (!tSea[i, j] && inside(CellMid(i, j))) tQuay[i, j] = flag;
        }
    }

    bool SeaAt(int i, int j) => HasSea && tSea[Mathf.Clamp(i, 0, tW - 1), Mathf.Clamp(j, 0, tH - 1)];   // held to the grid: the sea runs on past the map

    /// <summary>in a sea cell (beyond the grid: beside one, the sea carries on through the margin)</summary>
    bool InSea(Vector2 q) => HasSea && SeaAt(Mathf.FloorToInt((q.x - tO.x) / TT), Mathf.FloorToInt((q.y - tO.y) / TT));

    /// <summary>how far q is from the nearest sea cell (0 inside one; 99 beyond 6 m or with no sea)</summary>
    float SeaDist(Vector2 q) => HasSea ? CellDist(q, SeaAt) : 99f;

    /// <summary>how far q is from the nearest cell (held to the grid) that passes the test, within two cells (99: none)</summary>
    float CellDist(Vector2 q, Func<int, int, bool> test)
    {
        int ci = Mathf.FloorToInt((q.x - tO.x) / TT), cj = Mathf.FloorToInt((q.y - tO.y) / TT);
        float best = 99f;
        for (int dj = -2; dj <= 2; dj++)
            for (int di = -2; di <= 2; di++)
            {
                int i = ci + di, j = cj + dj;
                if (!test(i, j)) continue;
                float x0 = tO.x + i * TT, y0 = tO.y + j * TT;
                float dx = Mathf.Max(0f, Mathf.Max(x0 - q.x, q.x - (x0 + TT))), dy = Mathf.Max(0f, Mathf.Max(y0 - q.y, q.y - (y0 + TT)));
                best = Mathf.Min(best, Mathf.Sqrt(dx * dx + dy * dy));
            }
        return best;
    }

    /// <summary>the ground's height at a ground vertex on or in the sea (false: none of the cells meeting at q is sea).
    /// Against raised land (a quay's or a cliff's face, which go down to the bed) the bed, a little under the quay tiles'
    /// own; elsewhere a beach: from the level-0 land's height at the water's edge down to the bed 3 m out</summary>
    bool SeaGround(Vector2 q, out float z)
    {
        z = 0f;
        if (!HasSea) return false;
        bool sea = false, raised = false;
        foreach (var d in new[] { new Vector2(-0.01f, -0.01f), new Vector2(0.01f, -0.01f), new Vector2(0.01f, 0.01f), new Vector2(-0.01f, 0.01f) })
        {
            var p = q + d;
            int i = Mathf.Clamp(Mathf.FloorToInt((p.x - tO.x) / TT), 0, tW - 1), j = Mathf.Clamp(Mathf.FloorToInt((p.y - tO.y) / TT), 0, tH - 1);
            if (tSea[i, j]) sea = true;
            else if (tLevel[i, j] > 0 && In(Mathf.FloorToInt((p.x - tO.x) / TT), Mathf.FloorToInt((p.y - tO.y) / TT))) raised = true;
        }
        if (!sea) return false;
        float bed = SeaBed - SeaSink;
        if (raised) { z = bed; return true; }
        float shore = CellDist(q, (i, j) => !SeaAt(i, j) && Lv(Mathf.Clamp(i, 0, tW - 1), Mathf.Clamp(j, 0, tH - 1)) == 0);
        z = Mathf.Lerp(Base(q), bed, Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(shore / TT)));
        return true;
    }

    /// <summary>the sea cells as rows of rectangles (plan metres): the navmesh bake leaves them out up to
    /// <see cref="SeaWalkTop"/> (the bed and the drowned beach; the quays' tops and their water stairs stay walkable)</summary>
    public List<Rect> UnderSea()
    {
        var list = new List<Rect>();
        if (!HasSea) return list;
        for (int j = 0; j < tH; j++)
            for (int i = 0; i < tW; i++)
            {
                if (!tSea[i, j]) continue;
                int s = i;
                while (i + 1 < tW && tSea[i + 1, j]) i++;
                list.Add(Rect.MinMaxRect(tO.x + s * TT, tO.y + j * TT, tO.x + (i + 1) * TT, tO.y + (j + 1) * TT));
            }
        return list;
    }

    /// <summary>a terrain area's test: {"rect": [x0, y0, x1, y1]}, {"ellipse": {centre, radius, lumps}} or {"poly": [[x, y], ...]}</summary>
    static Func<Vector2, bool> TerrainShape(JsonNode a, int seed)
    {
        if (a["rect"] is JsonArray r && r.Count >= 4)
        {
            float x0 = Mathf.Min(r[0].F(), r[2].F()), x1 = Mathf.Max(r[0].F(), r[2].F());
            float y0 = Mathf.Min(r[1].F(), r[3].F()), y1 = Mathf.Max(r[1].F(), r[3].F());
            return q => q.x >= x0 && q.x <= x1 && q.y >= y0 && q.y <= y1;
        }
        if (a["ellipse"] is JsonObject e)
        {
            var c = V(e["centre"]);
            var rad = Radius(e["radius"], 6f);
            float lumps = e["lumps"].Fq() ?? 0f;
            return q => Blob(q, c, rad, lumps, seed) < 1f;
        }
        if (a["poly"] is JsonArray p && p.Count >= 3)
        {
            var poly = p.Select(V).ToArray();
            return q => InPoly(q, poly);
        }
        return null;
    }

    /// <summary>a radius as [rx, ry] or one number (missing: fallback)</summary>
    static Vector2 Radius(JsonNode r, float fallback) => r is JsonArray ? V(r) : new Vector2(r.Fq() ?? fallback, r.Fq() ?? fallback);

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

    /// <summary>how near q is to raised ground or the sea (1 at a cliff's foot or the water's edge, 0 from 3.5 m out):
    /// the ground's relief flattens there, so a cliff's toe meets level ground and a beach runs down from level 0</summary>
    float TerrainNear(Vector2 q)
    {
        if (!HasTerrain) return 0f;
        float best = CellDist(q, (i, j) => Lv(i, j) > 0 || (HasSea && SeaAt(i, j)));
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
    public bool OnStair(Vector2 q)
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

    /// <summary>the raised cells as rows of rectangles (plan metres, pulled 0.4 m in): the navmesh bake leaves the
    /// ground under them out up to a metre above it (a tall hill's hollow inside carries no navmesh)</summary>
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
    static string TileVariant(int cas, uint h, bool stiff)
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
    /// pieces, the stairs' own on theirs), a collider; then the sea</summary>
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
                if (QuayPick(c, lo, hi, out string quay, out int qr))      // a harbour wall instead of the cliff layer
                {
                    recs.Add((I, J, hi, quay, qr, false));
                    quayV[(I, J)] = quay.Substring(quay.LastIndexOf('_') + 1);
                    continue;
                }
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
                    if (cliff) piece = $"SM_VKT_Cliff_{CaseNames[cas]}_{TileVariant(cas, Hash(I, J, l), stiff)}";
                    // a cliff layer on an identical one (same case, same turn) needs no skirt: it would show on the
                    // lip of the layer below
                    recs.Add((I, J, l, piece, r, cliff && cas != FULL && pc == cas && pr == r));
                    pc = cliff ? cas : -1; pr = r;
                }
            }

        var tm = MergeTiles(recs, $"{Name}_Terrain", out int missing, out int verts);
        if (missing > 0) notes.Add($"terrain: {missing} tiles had no piece");
        if (tm == null) notes.Add("terrain: nothing raised");
        else
        {
            TerrainMesh = tm;
            // as the ground: its material projects the control map in the object space from the margin's corner
            var go = new MeshInstance3D { Name = "Terrain", Mesh = tm, Position = Local(-M, -M, 0f) };
            groundT.AddChild(go);
            go.Owner = SceneOwner;
            terrainCollider = new StaticBody3D { Name = "TerrainBody", CollisionLayer = KitPiece.Solid };
            go.AddChild(terrainCollider);
            terrainCollider.Owner = SceneOwner;
            var shape = new CollisionShape3D { Name = "Mesh", Shape = tm.CreateTrimeshShape() };
            terrainCollider.AddChild(shape);
            shape.Owner = SceneOwner;
            int raised = 0;
            for (int j = 0; j < tH; j++) for (int i = 0; i < tW; i++) if (tLevel[i, j] > 0) raised++;
            notes.Add($"terrain: {raised} raised cells, {recs.Count} tiles{(HasSea ? $" ({quayV.Count} quay)" : "")}, {verts} verts");
        }
        Sea();
    }

    /// <summary>vk_terrain_quay's qy_pick: a grid point whose land corners stand one level over its sea corners, a land
    /// corner carrying a quay flag, takes a Quay tile (the marching-squares case of its land, its quarter turns) on the
    /// land's layer; an Edge point whose two land cells both carry stairs (or both a slipway) gets the flight (the slip)</summary>
    bool QuayPick((int lv, int i, int j)[] c, int lo, int hi, out string piece, out int r)
    {
        piece = null; r = 0;
        if (!HasSea || hi != lo + 1) return false;
        int m = 0;
        bool anySea = false, flagged = false, stair = true, slip = true;
        for (int k = 0; k < 4; k++)
        {
            var x = c[k];
            if (tSea[x.i, x.j]) { if (x.lv != lo) return false; anySea = true; continue; }
            if (x.lv != hi) return false;
            m |= 1 << k;
            int f = tQuay[x.i, x.j];
            flagged |= f != 0; stair &= f == 2; slip &= f == 3;
        }
        if (!anySea || m == 0 || !flagged) return false;
        var (cas, rr) = MS[m];
        r = rr;
        string v = cas == EDGE && slip ? "Slip" : cas == EDGE && stair ? "Stair" : "A";
        piece = $"SM_VKT_Quay_{CaseNames[cas]}_{v}";
        return true;
    }

    /// <summary>the sea's material: the village's, else the addon's KitSea (null: the water quads keep their own)</summary>
    Material SeaMat() => seaMaterial ?? (ResourceLoader.Exists(SeaMatPath) ? GD.Load<Material>(SeaMatPath) : null);

    Material WaterMaskMat() => waterMaskMaterial ?? (ResourceLoader.Exists(WaterMaskMatPath) ? GD.Load<Material>(WaterMaskMatPath) : null);

    /// <summary>the sea's water: vk_terrain's water quad (3 x 3 m, 0.6 below its level) on every grid point a sea cell
    /// meets, held to the grid beyond it, so the water runs on under the forest margin past the map; one mesh in the
    /// ground's space, with no collider (the navmesh leaves the sea out: <see cref="UnderSea"/>)</summary>
    void Sea()
    {
        if (!HasSea) return;
        var recs = new List<(int I, int J, int l, string piece, int r, bool stacked)>();
        int i0 = Mathf.FloorToInt((-M - tO.x) / TT), i1 = Mathf.CeilToInt((W + M - tO.x) / TT);
        int j0 = Mathf.FloorToInt((-M - tO.y) / TT), j1 = Mathf.CeilToInt((H + M - tO.y) / TT);
        for (int J = j0; J <= j1; J++)
            for (int I = i0; I <= i1; I++)
                if (SeaAt(I - 1, J - 1) || SeaAt(I, J - 1) || SeaAt(I, J) || SeaAt(I - 1, J)) recs.Add((I, J, 0, WaterQuad, 0, false));
        var sm = MergeTiles(recs, $"{Name}_Sea", out _, out _);
        if (sm == null) { notes.Add("sea: no water quad (SM_VKT_WaterQuad)"); return; }
        var sea = SeaMat();
        if (sea != null) for (int s = 0; s < sm.GetSurfaceCount(); s++) sm.SurfaceSetMaterial(s, sea);
        else notes.Add("sea: no sea material (Materials/KitSea.tres): the water quads keep their own");
        SeaMesh = sm;
        var go = new MeshInstance3D { Name = "Sea", Mesh = sm, Position = Local(-M, -M, 0f), CastShadow = GeometryInstance3D.ShadowCastingSetting.Off };
        groundT.AddChild(go);
        go.Owner = SceneOwner;
        int cells = 0;
        for (int j = 0; j < tH; j++) for (int i = 0; i < tW; i++) if (tSea[i, j]) cells++;
        notes.Add($"sea: {cells} cells, {recs.Count} water quads");
    }

    /// <summary>each hull moored in the sea, sliced at the water's height where it floats: the convex outline of where
    /// its meshes cross the water plane (a boat's waterline), fanned into one mesh drawn with waterMaskMaterial, which
    /// keeps the sea from drawing water inside it: the boat stays dry however low it sits. Built once with the level,
    /// saved inside the map's scene</summary>
    void SeaMasks()
    {
        if (!HasSea || seaHulls.Count == 0) return;
        var verts = new List<Godot.Vector3>(); var tris = new List<int>();
        var toGround = Rel(groundT).AffineInverse();
        foreach (var (go, at) in seaHulls)
        {
            if (!IsInstanceValid(go)) continue;
            float wy = Height(at);                                        // the water's surface, in the village's space
            var pts = new List<Vector2>();
            foreach (var mi in Meshes(go))
            {
                var mesh = mi.Mesh; if (mesh == null) continue;
                var tf = Rel(mi);
                for (int s = 0; s < mesh.GetSurfaceCount(); s++)
                {
                    if (!Triangles(mesh, s)) continue;
                    using var arr = mesh.SurfaceGetArrays(s);
                    var v = arr[(int)Mesh.ArrayType.Vertex].AsVector3Array();
                    var iv = arr[(int)Mesh.ArrayType.Index];
                    var t = iv.VariantType == Variant.Type.Nil ? null : iv.AsInt32Array();
                    if (t == null || t.Length == 0) t = Enumerable.Range(0, v.Length - v.Length % 3).ToArray();
                    var w = new Godot.Vector3[v.Length];
                    for (int k = 0; k < v.Length; k++) w[k] = tf * v[k];
                    for (int k = 0; k + 2 < t.Length; k += 3)
                        for (int e = 0; e < 3; e++)
                        {
                            Godot.Vector3 a = w[t[k + e]], b = w[t[k + (e + 1) % 3]];
                            float da = a.Y - wy, db = b.Y - wy;
                            if ((da < 0f) == (db < 0f)) continue;
                            pts.Add(Plan(a.Lerp(b, da / (da - db))));
                        }
                }
            }
            var hull = ConvexHull(pts);
            if (hull.Count < 3) { notes.Add($"sea mask: {go.Name} does not cross the water"); continue; }
            var c = Vector2.zero; foreach (var p in hull) c += p; c /= hull.Count;
            int b0 = verts.Count;
            verts.Add(toGround * Local(c.x, c.y, wy));
            foreach (var p in hull) verts.Add(toGround * Local(p.x, p.y, wy));
            // the hull runs anticlockwise in plan (seen from above); Godot's front faces wind clockwise seen from them
            for (int k = 0; k < hull.Count; k++) { tris.Add(b0); tris.Add(b0 + 1 + (k + 1) % hull.Count); tris.Add(b0 + 1 + k); }
        }
        seaHulls.Clear();
        if (tris.Count == 0) return;
        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = verts.ToArray();
        arrays[(int)Mesh.ArrayType.Normal] = Enumerable.Repeat(Godot.Vector3.Up, verts.Count).ToArray();
        arrays[(int)Mesh.ArrayType.Index] = tris.ToArray();
        var mask = new ArrayMesh { ResourceName = $"{Name}_SeaMask" };
        mask.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        arrays.Dispose();
        var mat = WaterMaskMat();
        if (mat != null) mask.SurfaceSetMaterial(0, mat);
        else notes.Add("sea mask: no waterMaskMaterial (Materials/KitWaterMask.tres): the hulls fill with water");
        SeaMaskMesh = mask;
        var mgo = new MeshInstance3D { Name = "SeaMask", Mesh = mask, CastShadow = GeometryInstance3D.ShadowCastingSetting.Off };
        groundT.AddChild(mgo);
        mgo.Owner = SceneOwner;
        notes.Add($"sea mask: {verts.Count} verts over the moored hulls");
    }

    /// <summary>a mesh's surface is a triangle list (an ArrayMesh's lines or points are not; any other mesh's are)</summary>
    static bool Triangles(Mesh mesh, int s) => mesh is not ArrayMesh am || am.SurfaceGetPrimitiveType(s) == Mesh.PrimitiveType.Triangles;

    /// <summary>the convex hull of plan points (Andrew's monotone chain), counter-clockwise</summary>
    static List<Vector2> ConvexHull(List<Vector2> pts)
    {
        var p = pts.Distinct().OrderBy(q => q.x).ThenBy(q => q.y).ToList();
        if (p.Count < 3) return p;
        static float Cross(Vector2 o, Vector2 a, Vector2 b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
        var h = new List<Vector2>();
        for (int pass = 0; pass < 2; pass++)
        {
            int start = h.Count;
            foreach (var q in pass == 0 ? p : Enumerable.Reverse(p))
            {
                while (h.Count >= start + 2 && Cross(h[h.Count - 2], h[h.Count - 1], q) <= 0f) h.RemoveAt(h.Count - 1);
                h.Add(q);
            }
            h.RemoveAt(h.Count - 1);
        }
        return h;
    }

    /// <summary>one surface of a tile piece, in the piece's root space, and the material it is drawn with in the merge</summary>
    sealed class TileSurface
    {
        public Godot.Vector3[] v, n;
        public Color[] col;
        public int[] t;
        public Material m;
    }

    /// <summary>a tile piece's surfaces (null: no piece or no mesh): the terrain's surfaces (M_VK_Terrain*) take the
    /// map's ground material (its grass, roads and paving), the others (the stairs' stone, the water) keep their own</summary>
    List<TileSurface> ReadTile(string piece)
    {
        var pf = Prefab(piece);
        if (pf == null) return null;
        var inst = pf.Instantiate();
        try
        {
            var mi = inst as MeshInstance3D ?? KitNodes.Below(inst, "MeshInstance3D").OfType<MeshInstance3D>().FirstOrDefault();
            if (mi?.Mesh == null) return null;
            var toRoot = Transform3D.Identity;                                // the mesh in the piece root's space
            for (Node c = mi; c != null && c != inst; c = c.GetParent()) if (c is Node3D c3) toRoot = c3.Transform * toRoot;
            var nb = toRoot.Basis.Inverse().Transposed();
            var list = new List<TileSurface>();
            var mesh = mi.Mesh;
            for (int s = 0; s < mesh.GetSurfaceCount(); s++)
            {
                if (!Triangles(mesh, s)) continue;
                var m = mi.GetActiveMaterial(s);
                if (m == null || (NameOf(m) ?? "").StartsWith("M_VK_Terrain", StringComparison.Ordinal)) m = GroundMaterialInstance ?? m;
                if (m == null) continue;
                using var arr = mesh.SurfaceGetArrays(s);
                var v = arr[(int)Mesh.ArrayType.Vertex].AsVector3Array();
                var nv = arr[(int)Mesh.ArrayType.Normal];
                var n = nv.VariantType == Variant.Type.Nil ? null : nv.AsVector3Array();
                var cv = arr[(int)Mesh.ArrayType.Color];
                var col = cv.VariantType == Variant.Type.Nil ? null : cv.AsColorArray();
                var iv = arr[(int)Mesh.ArrayType.Index];
                var t = iv.VariantType == Variant.Type.Nil ? null : iv.AsInt32Array();
                if (t == null || t.Length == 0) t = Enumerable.Range(0, v.Length - v.Length % 3).ToArray();
                var ts = new TileSurface { v = new Godot.Vector3[v.Length], n = new Godot.Vector3[v.Length], col = new Color[v.Length], t = t, m = m };
                for (int k = 0; k < v.Length; k++)
                {
                    ts.v[k] = toRoot * v[k];
                    ts.n[k] = n != null && k < n.Length ? (nb * n[k]).Normalized() : Godot.Vector3.Up;
                    ts.col[k] = col != null && col.Length == v.Length ? col[k] : Colors.White;
                }
                list.Add(ts);
            }
            return list.Count > 0 ? list : null;
        }
        finally { inst.Free(); }
    }

    /// <summary>tiles (grid point, level, piece, quarter turns, drop the skirt) merged into one mesh in the ground
    /// object's space, a surface per material (null: nothing)</summary>
    ArrayMesh MergeTiles(List<(int I, int J, int l, string piece, int r, bool stacked)> recs, string meshName, out int missing, out int vertCount)
    {
        var cache = new Dictionary<string, List<TileSurface>>();
        var order = new List<Material>();
        var buckets = new Dictionary<Material, (List<Godot.Vector3> v, List<Godot.Vector3> n, List<Color> c, List<int> t)>();
        missing = 0; vertCount = 0;
        foreach (var rec in recs)
        {
            if (!cache.TryGetValue(rec.piece, out var src)) cache[rec.piece] = src = ReadTile(rec.piece);
            if (src == null) { missing++; continue; }
            var rot = Turn(90f * rec.r);                                       // an anticlockwise quarter in plan
            var at = Local(tO.x + TT * rec.I + M, tO.y + TT * rec.J + M, rec.l * Tier);   // the ground object's space
            foreach (var s in src)
            {
                if (!buckets.TryGetValue(s.m, out var b)) { buckets[s.m] = b = (new(), new(), new(), new()); order.Add(s.m); }
                int b0 = b.v.Count;
                for (int k = 0; k < s.v.Length; k++)
                {
                    b.v.Add(rot * s.v[k] + at);
                    b.n.Add(rot * s.n[k]);
                    b.c.Add(s.col[k]);
                }
                var t = s.t;
                for (int k = 0; k + 2 < t.Length; k += 3)
                {
                    if (rec.stacked && Mathf.Min(s.v[t[k]].Y, s.v[t[k + 1]].Y, s.v[t[k + 2]].Y) < -2.5f) continue;   // the skirt
                    b.t.Add(b0 + t[k]); b.t.Add(b0 + t[k + 1]); b.t.Add(b0 + t[k + 2]);
                }
            }
        }
        ArrayMesh mesh = null;
        foreach (var m in order)
        {
            var b = buckets[m];
            if (b.t.Count == 0) continue;
            mesh ??= new ArrayMesh { ResourceName = meshName };
            var arrays = new Godot.Collections.Array();
            arrays.Resize((int)Mesh.ArrayType.Max);
            arrays[(int)Mesh.ArrayType.Vertex] = b.v.ToArray();
            arrays[(int)Mesh.ArrayType.Normal] = b.n.ToArray();
            arrays[(int)Mesh.ArrayType.Color] = b.c.ToArray();
            arrays[(int)Mesh.ArrayType.Index] = b.t.ToArray();
            mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
            arrays.Dispose();
            mesh.SurfaceSetMaterial(mesh.GetSurfaceCount() - 1, m);
            vertCount += b.v.Count;
        }
        return mesh;
    }

    /// <summary>the cliffs' and ramps' dressing (Build calls it once the buildings, props and trees stand: it keeps out
    /// of their footprints)</summary>
    void DressTerrain()
    {
        if (!HasTerrain || TerrainMesh == null) return;
        DressCliffs();
        DressRamps();
        DressQuays();
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
    public bool OnRampTile(Vector2 q)
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

    /// <summary>a dressing piece under parent at (x, y, z) plan, turned deg, scaled s (null: no such piece)</summary>
    Node3D Dressing(Node3D parent, string piece, float x, float y, float z, float deg, float s)
    {
        var pf = Prefab(piece);
        if (pf == null) return null;
        var go = Make(pf, parent);
        go.Transform = new Transform3D(Turn(deg).Scaled(Godot.Vector3.One * s), Local(x, y, z));
        return go;
    }

    bool ClearOfBuilt(Vector2 q, float pad)
    {
        foreach (var (poly, _) in occupied) if (DistToPoly(q, poly) < pad) return false;
        return true;
    }

    /// <summary>vk_terrain's tk_ramp_dress: a few stones and plants where each ramp or flight meets the cliffs on its
    /// two sides (they break up the joint and its earth bank; beside a flight, out past its flanking wall); a walled
    /// ramp stays clean</summary>
    void DressRamps()
    {
        if (tDress <= 0f) return;
        var rng = new System.Random((L["seed"].Iq() ?? 1) * 37 + 7);
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
                        if (!ClearOfBuilt(new Vector2(wx, wy), 0.3f)) continue;
                        float deg = (float)rng.NextDouble() * 360f, sc = pk.s * (0.85f + 0.3f * (float)rng.NextDouble());
                        Dressing(natureT, pk.piece, wx, wy, z - 0.03f, deg, sc);
                    }
                    // a boulder on the earth bank beside the ramp's tongue: it hides the bank's pale wedge and the
                    // foot of the face's open end (round 2 of the cliffs pass: every ramp read as a gap with two
                    // flaps); long side along the bank, from the ramp's foot up to the face, sunk a little, its inner
                    // edge at the tongue's edge
                    {
                        bool big = rng.NextDouble() < 0.5;
                        float lx = -0.62f - wall, ly = -0.55f;
                        float wx = cx - sx * lx + fx * ly, wy = cy - sy * lx + fy * ly;
                        string bn = big ? "SM_VK_Rock_Boulder_B" : "SM_VK_Rock_Boulder_A";
                        if (ClearOfBuilt(new Vector2(wx, wy), 0.3f))
                        {
                            float deg = (fx != 0 ? 0f : 90f) + (float)rng.NextDouble() * 40f - 20f;
                            float sc = (big ? 0.56f : 0.88f) * (0.9f + 0.2f * (float)rng.NextDouble());
                            Dressing(natureT, bn, wx, wy, z - 0.12f, deg, sc);
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
        var rng = new System.Random((L["seed"].Iq() ?? 1) * 31 + 5);
        float U(float a, float b) => a + (float)rng.NextDouble() * (b - a);
        string PickOf(string[] a) => a[rng.Next(a.Length)];
        void Put(string piece, float x, float y, float z, float deg, float s) => Dressing(natureT, piece, x, y, z, deg, s);
        for (int j = 0; j < tH; j++)
            for (int i = 0; i < tW; i++)
                foreach (var (di, dj) in new[] { (1, 0), (0, 1) })
                {
                    int ii = i + di, jj = j + dj;
                    if (ii >= tW || jj >= tH) continue;
                    int la = tLevel[i, j], lb = tLevel[ii, jj];
                    if (la == lb || tRamp[i, j] != 0 || tRamp[ii, jj] != 0) continue;
                    if (QuayEdge(i, j, di)) continue;                        // a harbour wall: dressed stone, no rock dressing
                    var (hiI, hiJ, loI, loJ) = la > lb ? (i, j, ii, jj) : (ii, jj, i, j);
                    bool wet = HasSea && tSea[loI, loJ];                     // a cliff into the sea: nothing at its drowned foot
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
                        if (DressFree(bx, by, -1)) Put(PickOf(DressFace), bx, by, zb, U(0f, 360f), U(0.42f, 0.72f) * (h <= Tier ? 1f : 1.35f));
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
                                // (both draws before the call, in Unity's order)
                                float deg = rot + U(-8f, 8f), sc = U(0.8f, 1.2f);
                                Put(LipGrass, cx + tx * t, cy + ty * t, lm * Tier, deg, sc);
                            }
                    }
                    if (rng.NextDouble() < 0.6 * tDress && !wet)             // rubble at the foot
                    {
                        int n = rng.Next(2, 5);
                        for (int k = 0; k < n; k++)
                        {
                            float t = Along(), off = U(0.35f, 0.95f);
                            string nm = PickOf(DressRubble);
                            float rx = cx + tx * t + ox * off, ry = cy + ty * t + oy * off;
                            if (DressFree(rx, ry, lLo)) Put(nm, rx, ry, zl - 0.05f, U(0f, 360f), nm.EndsWith("Cluster") ? U(0.35f, 0.55f) : U(0.6f, 1.2f));
                        }
                    }
                    if (rng.NextDouble() < 0.45 * tDress && !wet)            // plants at the foot
                    {
                        float t = Along(), off = U(0.5f, 1f);
                        string nm = PickOf(DressPlants);
                        float px = cx + tx * t + ox * off, py = cy + ty * t + oy * off;
                        if (DressFree(px, py, lLo)) Put(nm, px, py, zl, U(0f, 360f), nm.EndsWith("Round") ? U(0.45f, 0.65f) : U(0.7f, 1.05f));
                    }
                }
    }

    /// <summary>the edge between cell (i, j) and its east (di 1) or north (di 0) neighbour ends at a quay tile</summary>
    bool QuayEdge(int i, int j, int di) =>
        quayV.Count > 0 && (di == 1 ? quayV.ContainsKey((i + 1, j)) || quayV.ContainsKey((i + 1, j + 1))
                                    : quayV.ContainsKey((i, j + 1)) || quayV.ContainsKey((i + 1, j + 1)));

    /// <summary>the harbour props along the quay walls (vk_mod_harbour's, on the wall line facing the water at the
    /// land's height, as qy_demo stands them): on each 3 m of wall between two quay points a bollard on the coping
    /// (two in five), a fender hung on the face (one in two), a mooring ring (one in five), kept 0.8 m from the run's
    /// corners and clear of the water stairs' and the slipway's tiles; "quayDress" scales them (default "dress")</summary>
    void DressQuays()
    {
        if (quayV.Count == 0 || tQuayDress <= 0f) return;
        var rng = new System.Random((L["seed"].Iq() ?? 1) * 43 + 9);
        for (int j = 0; j < tH; j++)
            for (int i = 0; i < tW; i++)
                foreach (var (di, dj) in new[] { (1, 0), (0, 1) })
                {
                    int ii = i + di, jj = j + dj;
                    if (ii >= tW || jj >= tH || tSea[i, j] == tSea[ii, jj]) continue;
                    var (hiI, hiJ, loI, loJ) = tSea[ii, jj] ? (i, j, ii, jj) : (ii, jj, i, j);
                    if (tLevel[hiI, hiJ] != tLevel[loI, loJ] + 1) continue;
                    // the wall's two ends, along the edge: (a) its west / south end, (b) its east / north end
                    var a = di == 1 ? (i + 1, j) : (i, j + 1);
                    var b = (i + 1, j + 1);
                    if (!quayV.TryGetValue(a, out var va) || !quayV.TryGetValue(b, out var vb)) continue;
                    int ox = loI - hiI, oy = loJ - hiJ;                     // towards the water
                    var mid = new Vector2(tO.x + 1.5f * (hiI + loI) + 1.5f, tO.y + 1.5f * (hiJ + loJ) + 1.5f);
                    var along = new Vector2(Mathf.Abs(oy), Mathf.Abs(ox));  // from end a to end b
                    float lo = va == "A" ? -0.7f : 0.2f, hi = vb == "A" ? 0.7f : -0.2f;   // 1.7 m clear of a flight or a slip
                    if (hi < lo) continue;
                    float deg = Mathf.Atan2(oy, ox) * Mathf.Rad2Deg + 90f, z = tLevel[hiI, hiJ] * Tier;
                    var used = new List<float>();
                    foreach (var (piece, p) in new[] { (QuayProps[0], 0.4), (QuayProps[1], 0.5), (QuayProps[2], 0.2) })
                    {
                        double roll = rng.NextDouble(), u = rng.NextDouble();
                        if (roll >= p * tQuayDress) continue;
                        float t = Mathf.Lerp(lo, hi, (float)u);
                        if (used.Any(x => Mathf.Abs(x - t) < 0.6f)) continue;
                        var q = mid + along * t;
                        if (!ClearOfBuilt(q, 0.4f)) continue;
                        var go = Dressing(propT, piece, q.x, q.y, z, deg, 1f);
                        if (go == null) continue;
                        if (piece == QuayProps[0]) KitSolid.Box(go, owner: SceneOwner);   // a bollard is bumped into; the others hang on the face
                        used.Add(t);
                    }
                }
    }
}
