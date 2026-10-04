using System.Collections;
using UnityEngine;
using UnityEngine.AI;

namespace MedievalKit
{
    /// <summary>
    /// The shroud of an underground level (the Diablo-like cave look): what lies away from where the walker can go
    /// darkens with that distance, down to black a few metres in, so the rock between the passages fades into the black
    /// round the level instead of ending at a pale top and a cliff edge (KitLit's forward pass, KitShroud.hlsl). On a
    /// level's scene (a chain's play scene carries one): while it is enabled, the walkable ground near the level's floor
    /// (the navmesh; the rock tops' unreachable islands left out) is drawn into a distance field of
    /// <see cref="cell"/>-metre cells and handed to the shader as globals; disabled (the level held switched off, or
    /// left), the shroud is off. Tune <see cref="darkFrom"/> / <see cref="blackAt"/> live in play mode.
    /// </summary>
    [DisallowMultipleComponent]
    public class KitShroud : MonoBehaviour
    {
        [Tooltip("Metres from the walkable ground where the darkening starts (the passages' walls stay lit).")]
        public float darkFrom = 0.2f;
        [Tooltip("Metres from the walkable ground where it is black.")]
        public float blackAt = 3f;
        [Tooltip("The light the rock's tops keep (faces turned up, well above the floor): dim, so the rock reads as " +
                 "dark mass, not pale tiles.")]
        [Range(0, 1)] public float topLight = 0.4f;
        [Tooltip("The field's cell (m).")]
        public float cell = 0.5f;
        [Tooltip("The walkable ground counted: within this height (m) of the level's floor (cave rock tops carry navmesh " +
                 "islands no one reaches).")]
        public float floorBand = 1.6f;

        /// <summary>the field's range: distances beyond it read as this (m)</summary>
        const float Range = 10f;
        static readonly int IdTex = Shader.PropertyToID("_KitShroudTex"), IdRect = Shader.PropertyToID("_KitShroudRect"),
                            IdArgs = Shader.PropertyToID("_KitShroudArgs"), IdArgs2 = Shader.PropertyToID("_KitShroudArgs2");
        static KitShroud active;
        Texture2D field;
        float floorY;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetStatics()
        {
            active = null;
            Shader.SetGlobalVector(IdArgs, Vector4.zero);
        }

        void OnEnable()
        {
            KitTravel.Arrived += OnArrived;
            StartCoroutine(BuildSoon());
        }

        void OnArrived(string level, KitSpawn spawn)
        {
            if (isActiveAndEnabled) StartCoroutine(BuildSoon());
        }

        /// <summary>once the level's navmesh is in and the walker stands on it (its pieces streamed in round it); a few
        /// seconds at most</summary>
        IEnumerator BuildSoon()
        {
            yield return null;
            for (float t = 0f; t < 5f; t += Time.unscaledDeltaTime)
            {
                var w = KitTravel.Walker;
                if (!KitTravel.Travelling && w != null && NavMesh.SamplePosition(w.position, out _, 0.4f, NavMesh.AllAreas) &&
                    SpawnHeight() != null) break;                    // a chain's pieces (and their spawns) stream in
                yield return null;
            }
            Build();
        }

        void OnDisable()
        {
            KitTravel.Arrived -= OnArrived;
            if (active != this) return;
            active = null;
            Shader.SetGlobalVector(IdArgs, Vector4.zero);
        }

        void OnDestroy()
        {
            if (field != null) Destroy(field);
        }

        void OnValidate()
        {
            if (active == this) Apply();
        }

        void Apply()
        {
            Shader.SetGlobalVector(IdArgs, new Vector4(1f, darkFrom, Mathf.Max(darkFrom + 0.1f, blackAt), Range));
            Shader.SetGlobalVector(IdArgs2, new Vector4(floorY, topLight, 0f, 0f));
        }

        /// <summary>the distance field from the navmesh as it is now (called on enabling; again after the walkable
        /// ground changes)</summary>
        public void Build()
        {
            var tri = NavMesh.CalculateTriangulation();
            var v = tri.vertices;
            var idx = tri.indices;
            if (idx == null || idx.Length < 3) return;
            // the floor: the height most of the walkable area lies at
            float floor = FloorHeight(v, idx);
            floorY = floor;
            float minX = float.MaxValue, minZ = float.MaxValue, maxX = float.MinValue, maxZ = float.MinValue;
            for (int t = 0; t < idx.Length; t += 3)
            {
                if (!OnFloor(v, idx, t, floor)) continue;
                for (int k = 0; k < 3; k++)
                {
                    var p = v[idx[t + k]];
                    minX = Mathf.Min(minX, p.x); maxX = Mathf.Max(maxX, p.x);
                    minZ = Mathf.Min(minZ, p.z); maxZ = Mathf.Max(maxZ, p.z);
                }
            }
            if (minX > maxX) return;
            float margin = Range + 1f;
            minX -= margin; minZ -= margin; maxX += margin; maxZ += margin;
            float c = Mathf.Max(0.1f, cell);
            int w = Mathf.Clamp(Mathf.CeilToInt((maxX - minX) / c), 1, 4096), h = Mathf.Clamp(Mathf.CeilToInt((maxZ - minZ) / c), 1, 4096);
            const float Far = 1e6f;
            var d = new float[w * h];
            for (int i = 0; i < d.Length; i++) d[i] = Far;

            // the walkable cells: cell centres inside a floor triangle, and the cells under its corners
            for (int t = 0; t < idx.Length; t += 3)
            {
                if (!OnFloor(v, idx, t, floor)) continue;
                Vector2 a = Xz(v[idx[t]]), b = Xz(v[idx[t + 1]]), e = Xz(v[idx[t + 2]]);
                int x0 = Cell(Mathf.Min(a.x, Mathf.Min(b.x, e.x)), minX, c, w), x1 = Cell(Mathf.Max(a.x, Mathf.Max(b.x, e.x)), minX, c, w);
                int z0 = Cell(Mathf.Min(a.y, Mathf.Min(b.y, e.y)), minZ, c, h), z1 = Cell(Mathf.Max(a.y, Mathf.Max(b.y, e.y)), minZ, c, h);
                for (int z = z0; z <= z1; z++)
                    for (int x = x0; x <= x1; x++)
                        if (Inside(new Vector2(minX + (x + 0.5f) * c, minZ + (z + 0.5f) * c), a, b, e)) d[z * w + x] = 0f;
                foreach (var p in new[] { a, b, e }) d[Cell(p.y, minZ, c, h) * w + Cell(p.x, minX, c, w)] = 0f;
            }

            // the distance to the nearest walkable cell (two chamfer passes, in cells)
            const float D1 = 1f, D2 = 1.41421356f;
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                {
                    int i = z * w + x;
                    float m = d[i];
                    if (x > 0) m = Mathf.Min(m, d[i - 1] + D1);
                    if (z > 0)
                    {
                        m = Mathf.Min(m, d[i - w] + D1);
                        if (x > 0) m = Mathf.Min(m, d[i - w - 1] + D2);
                        if (x < w - 1) m = Mathf.Min(m, d[i - w + 1] + D2);
                    }
                    d[i] = m;
                }
            for (int z = h - 1; z >= 0; z--)
                for (int x = w - 1; x >= 0; x--)
                {
                    int i = z * w + x;
                    float m = d[i];
                    if (x < w - 1) m = Mathf.Min(m, d[i + 1] + D1);
                    if (z < h - 1)
                    {
                        m = Mathf.Min(m, d[i + w] + D1);
                        if (x < w - 1) m = Mathf.Min(m, d[i + w + 1] + D2);
                        if (x > 0) m = Mathf.Min(m, d[i + w - 1] + D2);
                    }
                    d[i] = m;
                }

            var px = new byte[w * h];
            for (int i = 0; i < px.Length; i++) px[i] = (byte)Mathf.RoundToInt(Mathf.Clamp01(d[i] * c / Range) * 255f);
            if (field == null || field.width != w || field.height != h)
            {
                if (field != null) Destroy(field);
                field = new Texture2D(w, h, TextureFormat.R8, false, true)
                {
                    name = "KitShroud", filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp,
                };
            }
            field.SetPixelData(px, 0);
            field.Apply(false, false);
            Shader.SetGlobalTexture(IdTex, field);
            Shader.SetGlobalVector(IdRect, new Vector4(minX, minZ, 1f / (w * c), 1f / (h * c)));
            active = this;
            Apply();
        }

        bool OnFloor(Vector3[] v, int[] idx, int t, float floor) =>
            Mathf.Abs((v[idx[t]].y + v[idx[t + 1]].y + v[idx[t + 2]].y) / 3f - floor) <= floorBand;

        /// <summary>the level's floor: of the heights (0.25 m bands) holding a good share of the walkable area, the one
        /// nearest the level's spawns (else the walker's, else the lowest). Not simply the largest: a cave's flat rock
        /// tops carry navmesh islands that can outweigh its winding floor.</summary>
        static float FloorHeight(Vector3[] v, int[] idx)
        {
            var area = new System.Collections.Generic.Dictionary<int, float>();
            float total = 0f;
            for (int t = 0; t < idx.Length; t += 3)
            {
                Vector3 a = v[idx[t]], b = v[idx[t + 1]], e = v[idx[t + 2]];
                int band = Mathf.RoundToInt((a.y + b.y + e.y) / 3f * 4f);
                float s = Vector3.Cross(b - a, e - a).magnitude * 0.5f;
                area[band] = (area.TryGetValue(band, out var x) ? x : 0f) + s;
                total += s;
            }
            float? near = SpawnHeight();
            if (near == null && KitTravel.Walker != null) near = KitTravel.Walker.position.y;
            int best = int.MaxValue; float bestScore = float.MaxValue;
            foreach (var kv in area)
            {
                if (kv.Value < total * 0.05f) continue;
                float score = near.HasValue ? Mathf.Abs(kv.Key / 4f - near.Value) : kv.Key;
                if (score < bestScore) { bestScore = score; best = kv.Key; }
            }
            return best == int.MaxValue ? (near ?? 0f) : best / 4f;
        }

        /// <summary>the middle height of the loaded levels' spawns (they stand on the floor; a walker on its way, or a test
        /// walker left on a rock top, may not), or null without any</summary>
        static float? SpawnHeight()
        {
            var ys = new System.Collections.Generic.List<float>();
            foreach (var s in FindObjectsByType<KitSpawn>(FindObjectsSortMode.None)) ys.Add(s.transform.position.y);
            if (ys.Count == 0) return null;
            ys.Sort();
            return ys[ys.Count / 2];
        }

        static Vector2 Xz(Vector3 p) => new Vector2(p.x, p.z);
        static int Cell(float x, float min, float c, int n) => Mathf.Clamp(Mathf.FloorToInt((x - min) / c), 0, n - 1);

        static bool Inside(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
        {
            float d1 = (p.x - b.x) * (a.y - b.y) - (a.x - b.x) * (p.y - b.y);
            float d2 = (p.x - c.x) * (b.y - c.y) - (b.x - c.x) * (p.y - c.y);
            float d3 = (p.x - a.x) * (c.y - a.y) - (c.x - a.x) * (p.y - a.y);
            bool neg = d1 < 0 || d2 < 0 || d3 < 0, pos = d1 > 0 || d2 > 0 || d3 > 0;
            return !(neg && pos);
        }
    }
}
