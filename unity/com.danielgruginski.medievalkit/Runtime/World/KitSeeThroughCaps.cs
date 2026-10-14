using System.Collections.Generic;
using Unity.Collections;
using UnityEngine;
using UnityEngine.Rendering;

namespace MedievalKit
{
    /// <summary>
    /// Real caps for the see-through (2026-10-13, MedievalSetting; the user: "All the problems we are having happen because
    /// the hole shows part of the geometry it was not supposed to show" -- hollow insides, back faces, pieces overlapping
    /// inside a wall, a trunk sliced lengthways). The user's call: the hole stays for what covers the walker (roofs, upper
    /// floors, canopies), and what stands on the ground is cut with a proper finish. Each piece is cut at
    /// <see cref="Height"/> over its base (a building's floor, a tree's or a prop's foot): the shader removes what is above
    /// inside the hole, and a cap -- the piece's own cross-section at the cut, filled -- closes the stub, drawn only where
    /// the hole opened it (KitSeeThrough.hlsl, rendering layer <see cref="KitSeeThrough.CapBit"/>). The kit's solid pieces
    /// are closed, so their sections are closed loops (checked on walls, corners, the bell tower, the town wall and its
    /// tower, a palisade, trees, a well); sheets (leaf cards, a door leaf, a window pane) are open and get no cap.
    /// <para>The cut is kept per renderer in its rendering layer (<see cref="KitSeeThrough.WithCut"/>: an offset over its own
    /// origin in <see cref="Step"/> steps), so the shader cuts exactly where the cap lies; the piece's own mesh is drawn,
    /// shared by all its instances. A cap mesh is made per mesh, cut and set of solid materials, so the instances of a
    /// piece share one (Greywall: 4,255 cut pieces, 161 cap meshes).</para>
    /// <para>Baked and pooled (2026-10-14, spike round 3; the user: "do they all use the same cut model or each individual
    /// pine has an individual model?"): the cap meshes come from a bake (<see cref="KitSeeThroughCapBank"/>, Resources
    /// "KitSeeThroughCaps": Tools > Medieval Kit > Bake See-through Caps, and before every player build, by MedievalKit.
    /// Editor's KitSeeThroughCapsBake), so a player build has them -- the kit's meshes are not Read/Write, and only editor
    /// code may read them; in the editor what the bake lacks is still made in play, between frames (<see cref="Flush"/>,
    /// from KitSeeThroughCapsHook). And a cut piece no longer gets a cap renderer of its own (4,255 in Greywall): it is
    /// registered with its cap mesh, and a pool of <see cref="PoolSize"/> renderers is laid each frame over the registered
    /// pieces in the hole's reach (the cone from the camera to the walker), the nearest to the walker first.</para>
    /// <para>Spike round 1 (2026-10-13, the user's shots): caps that overlap fought in one plane -- within one piece (a stone
    /// corner's quoin blocks sit in its rubble core: two filled outlines in one plane, 51 of Greywall's 161 cap meshes) and
    /// between pieces (a corner over its walls' ends). Now every cap is stacked, by area, larger below: inside a cap mesh
    /// each outline lies <see cref="Layer"/> above the larger ones it overlaps, and in a building each piece's cap lies
    /// <see cref="RankStride"/> layers above the larger caps it overlaps (a rank pass when its caps are known) -- distinct
    /// heights, so nothing ties whatever the depth buffer; a few millimetres at most, far under a pixel. A section's loops are told
    /// outer from hole by the faces' own direction, not by nesting (a root inside a trunk left a gap in the trunk's cap);
    /// bark caps take the kit's end grain, its rings centred on each cut; a house gets a floor over its walls' box, shown
    /// only where the hole opens it (the grass inside showed).</para>
    /// </summary>
    public static class KitSeeThroughCaps
    {
        /// <summary>the cut over each piece's base (m): MedievalSetting's GameCamera.keepBelow</summary>
        public const float Height = 1.4f;
        /// <summary>the cut's offset is kept in the rendering layer in these steps (local units)</summary>
        public const float Step = 0.05f;
        const float Weld = 1e-3f;               // section points closer than this are one
        const float Tile = 0.5f;                // the cap's texture: tiles per (local) metre

        /// <summary>one step of the caps' stacking (m): an outline over the larger ones it overlaps in its own cap</summary>
        public const float Layer = 0.0005f;
        /// <summary>a piece's cap over the larger caps of its building it overlaps: this many layers (a cap holds up to 7)</summary>
        public const int RankStride = 8;
        /// <summary>cap renderers in the pool: the caps drawn at once, the pieces nearest the walker in the hole's cone first</summary>
        public const int PoolSize = 96;

        /// <summary>a cut piece and its cap (shared by the instances of its mesh, cut and solid materials)</summary>
        public sealed class Piece
        {
            public MeshRenderer r;
            public Transform t;
            public Mesh cap;
            public Material[] mats;
            /// <summary>the piece's own mesh bounds (the cap renderer takes them: the shader's in-the-way tests agree)</summary>
            public Bounds local;
            /// <summary>the cap's area (world, m2) and its height over the cut (world m: under it, stacked by area)</summary>
            public float area, offset = -0.001f;
            public KitSeeThrough.Building building;
            internal Vector3 at, centre;            // world, measured with the piece at `at`
            internal float radius;
        }

        static readonly Dictionary<(Mesh, int, uint, uint), (Mesh mesh, int[] mats, bool[] grain, float area)> cache =
            new Dictionary<(Mesh, int, uint, uint), (Mesh, int[], bool[], float)>();
        static readonly Queue<(MeshRenderer r, Mesh mesh, int q, uint solid, uint bark, KitSeeThrough.Building b)> pending =
            new Queue<(MeshRenderer, Mesh, int, uint, uint, KitSeeThrough.Building)>();
        static readonly List<Piece> pieces = new List<Piece>();
        static readonly Dictionary<KitSeeThrough.Building, List<Piece>> byBuilding = new Dictionary<KitSeeThrough.Building, List<Piece>>();
        static readonly HashSet<KitSeeThrough.Building> unranked = new HashSet<KitSeeThrough.Building>();
        static readonly Dictionary<string, Material> named = new Dictionary<string, Material>();

        /// <summary>a material the level does not use, by name (the editor hook looks in the package; a build, in the bank)</summary>
        public static System.Func<string, Material> FindMaterial;

        /// <summary>while set (the bake), <see cref="Cut"/> only collects each piece's cap key here: nothing is queued or
        /// registered, no floor is made</summary>
        public static HashSet<(Mesh, int, uint, uint)> Collecting;

        static KitSeeThroughCapBank bank;
        static bool bankRead;

        /// <summary>the baked caps (Resources "KitSeeThroughCaps"; none: everything is made in play, in the editor only)</summary>
        public static KitSeeThroughCapBank Bank
        {
            get
            {
                if (!bankRead)
                {
                    bankRead = true;
                    bank = Resources.Load<KitSeeThroughCapBank>(KitSeeThroughCapBank.ResourceName);
                    if (bank != null)
                        foreach (var e in bank.entries)
                        {
                            if (e == null || e.source == null) continue;
                            if (e.source.vertexCount != e.vertexCount || !Near(e.source.bounds, e.bounds)) { Stale++; continue; }
                            var key = (e.source, e.q, e.solid, e.bark);
                            if (!cache.ContainsKey(key)) { cache[key] = e.cap != null ? (e.cap, e.mats, e.grain, e.area) : (null, null, null, 0f); Baked++; }
                        }
                }
                return bank;
            }
        }

        static bool Near(Bounds a, Bounds b) => (a.center - b.center).sqrMagnitude < 1e-8f && (a.size - b.size).sqrMagnitude < 1e-8f;

        /// <summary>forget the bank (it was baked again) and what came from it</summary>
        public static void ResetBank()
        {
            bank = null; bankRead = false; Baked = 0; Stale = 0;
            cache.Clear();
        }

        /// <summary>a new play session (domain reload or not): nothing registered, the pool gone with the last session's scenes</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void NewSession()
        {
            pending.Clear(); pieces.Clear(); byBuilding.Clear(); unranked.Clear();
            pool.Clear(); poolFilters.Clear(); poolRoot = null; poolFrame = -1;
            System.Array.Clear(shown, 0, shown.Length);
            Registered = Made = Failed = Missed = 0;
            var gone = new List<(Mesh, int, uint, uint)>();
            foreach (var kv in cache) if (kv.Value.mesh == null && kv.Value.mats != null) gone.Add(kv.Key);   // made in play, destroyed since
            foreach (var k in gone) cache.Remove(k);
        }

        /// <summary>the materials a level's renderers use, by name (the end grain, the floors)</summary>
        public static void Learn(GameObject root)
        {
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
                foreach (var m in r.sharedMaterials)
                    if (m != null && !named.ContainsKey(m.name)) named[m.name] = m;
        }

        static Material Named(params string[] names)
        {
            foreach (var n in names)
            {
                if (named.TryGetValue(n, out var m) && m != null) return m;
                m = FindMaterial?.Invoke(n);
                if (m == null && Bank != null)
                    foreach (var bm in bank.materials) if (bm != null && bm.name == n) { m = bm; break; }
                if (m != null) { named[n] = m; return m; }
            }
            return null;
        }

        static bool Bark(Material m) => m != null && m.name.StartsWith("M_VK_Bark");
        static float flushStart = -1f;
        static int flushRegistered;

        /// <summary>caps still to make (in the editor, in play)</summary>
        public static int Pending => pending.Count;

        /// <summary>pieces registered with a cap; cap meshes made in play; polygons that could not be filled; pieces a player
        /// build found no baked cap for; caps taken from the bank; bank entries ignored (their mesh changed)</summary>
        public static int Registered, Made, Failed, Missed, Baked, Stale;

        /// <summary>the pieces registered with a cap (the spike's checks)</summary>
        public static IReadOnlyList<Piece> Pieces => pieces;

        static bool Solid(Material m) =>
            m != null && m.shader != null && m.shader.name == "MedievalKit/KitLit" && m.HasProperty("_Cull") && m.GetFloat("_Cull") > 1.5f
            && (!m.HasProperty("_Surface") || m.GetFloat("_Surface") < 0.5f);

        /// <summary>the renderer's cut at baseY + <see cref="Height"/> (world), kept in its rendering layer; where it spans the
        /// cut, it is registered with its cap -- baked, made before, or queued to be made (the editor) -- and a building's
        /// caps open with it</summary>
        public static void Cut(MeshRenderer r, float baseY, KitSeeThrough.Building b = null)
        {
            var t = r.transform;
            float sy = t.localToWorldMatrix.m11;
            if (sy < 1e-4f) return;
            int q = Mathf.Clamp(Mathf.RoundToInt((baseY + Height - t.position.y) / sy / Step), -512, 511);
            r.renderingLayerMask = KitSeeThrough.WithCut(r.renderingLayerMask, q);
            var mf = r.GetComponent<MeshFilter>();
            var mesh = mf != null ? mf.sharedMesh : null;
            if (mesh == null) return;
            if (Vector3.Angle(t.up, Vector3.up) > 1f) return;           // tilted: the cut would not lie level in its space
            float y = q * Step;
            var bb = mesh.bounds;
            if (y <= bb.min.y + 1e-3f || y >= bb.max.y - 1e-3f) return;
            var mats = r.sharedMaterials;
            uint solid = 0;
            uint bark = 0;
            for (int s = 0; s < mats.Length && s < mesh.subMeshCount && s < 32; s++)
                if (Solid(mats[s])) { solid |= 1u << s; if (Bark(mats[s])) bark |= 1u << s; }
            if (solid == 0) return;
            var key = (mesh, q, solid, bark);
            if (Collecting != null) { Collecting.Add(key); return; }
            _ = Bank;
            if (cache.TryGetValue(key, out var cap) && (cap.mesh != null || cap.mats == null))
            {
                if (cap.mesh != null) Register(r, cap, b);
                return;
            }
            if (Application.isEditor) pending.Enqueue((r, mesh, q, solid, bark, b));
            else Missed++;                                              // a player build: not baked
        }

        /// <summary>a house's floor: a plank quad over its walls' box (the BoxCollider KitVillage puts on its root), at its
        /// floor, a cap of its building (drawn only where the hole opened it): the ground inside a house is the map's grass</summary>
        public static MeshRenderer Floor(KitSeeThrough.Building b)
        {
            if (Collecting != null) return null;
            var root = b.Root;
            var box = root != null ? root.GetComponent<BoxCollider>() : null;
            var mat = Named("M_VK_Planks", "M_VK_Wood");
            if (box == null || mat == null) return null;
            float hx = Mathf.Max(0.1f, box.size.x * 0.5f - 0.05f), hz = Mathf.Max(0.1f, box.size.z * 0.5f - 0.05f);
            var c = box.center;
            var m = new Mesh { name = root.name + "_SeeThroughFloor" };
            m.vertices = new[] { new Vector3(c.x - hx, 0.02f, c.z - hz), new Vector3(c.x - hx, 0.02f, c.z + hz), new Vector3(c.x + hx, 0.02f, c.z + hz), new Vector3(c.x + hx, 0.02f, c.z - hz) };
            m.uv = new[] { new Vector2(c.x - hx, c.z - hz) * Tile, new Vector2(c.x - hx, c.z + hz) * Tile, new Vector2(c.x + hx, c.z + hz) * Tile, new Vector2(c.x + hx, c.z - hz) * Tile };
            m.normals = new[] { Vector3.up, Vector3.up, Vector3.up, Vector3.up };
            m.tangents = new[] { new Vector4(1, 0, 0, 1), new Vector4(1, 0, 0, 1), new Vector4(1, 0, 0, 1), new Vector4(1, 0, 0, 1) };
            m.colors = new[] { new Color(1, 1, 1, 0), new Color(1, 1, 1, 0), new Color(1, 1, 1, 0), new Color(1, 1, 1, 0) };
            m.triangles = new[] { 0, 1, 2, 0, 2, 3 };
            m.RecalculateBounds();
            var go = new GameObject("SeeThroughFloor");
            go.layer = root.gameObject.layer;
            go.transform.SetParent(root, false);
            go.AddComponent<MeshFilter>().sharedMesh = m;
            var fr = go.AddComponent<MeshRenderer>();
            fr.sharedMaterial = mat;
            fr.shadowCastingMode = ShadowCastingMode.Off;
            fr.renderingLayerMask = 1u | KitSeeThrough.GroupBit | KitSeeThrough.CapBit | (b.open ? KitSeeThrough.OpenBit : 0u);
            b.caps.Add(fr);
            return fr;
        }

        /// <summary>make queued caps for up to `budgetMs` of this frame (the editor, in play); returns how many are left</summary>
        public static int Flush(float budgetMs = 8f)
        {
            if (pending.Count == 0) return 0;
            float start = Time.realtimeSinceStartup;
            if (flushStart < 0f) { flushStart = start; flushRegistered = Registered; }
            while (pending.Count > 0 && (Time.realtimeSinceStartup - start) * 1000f < budgetMs)
            {
                var (r, mesh, q, solid, bark, b) = pending.Dequeue();
                if (r == null) continue;
                var key = (mesh, q, solid, bark);
                if (!cache.TryGetValue(key, out var cap) || (cap.mesh == null && cap.mats != null)) cache[key] = cap = Make(mesh, q * Step, solid, bark);
                if (cap.mesh != null) Register(r, cap, b);
            }
            if (pending.Count == 0)
            {
                Settle();
                Debug.Log($"[KitSeeThroughCaps] {Registered - flushRegistered} more caps registered in play ({Made} cap meshes made so far, " +
                          $"{Failed} polygons not filled; {Baked} from the bake, {Stale} stale) over {(Time.realtimeSinceStartup - flushStart) * 1000f:F0} ms");
                flushStart = -1f;
            }
            return pending.Count;
        }

        /// <summary>the bake's cap for a mesh, its cut (in <see cref="Step"/>s) and solid / bark submeshes</summary>
        public static (Mesh mesh, int[] mats, bool[] grain, float area) MakeCap(Mesh mesh, int q, uint solid, uint bark) =>
            Make(mesh, q * Step, solid, bark);

        static void Register(MeshRenderer r, (Mesh mesh, int[] mats, bool[] grain, float area) cap, KitSeeThrough.Building b)
        {
            var src = r.sharedMaterials;
            var grain = Named("M_VK_EndGrain");
            var cm = new Material[cap.mats.Length];
            for (int i = 0; i < cm.Length; i++)
                cm[i] = cap.grain[i] && grain != null ? grain : cap.mats[i] < src.Length ? src[cap.mats[i]] : null;
            var t = r.transform;
            var p = new Piece
            {
                r = r, t = t, cap = cap.mesh, mats = cm, local = r.GetComponent<MeshFilter>().sharedMesh.bounds,
                area = cap.area * Mathf.Abs(t.lossyScale.x * t.lossyScale.z), building = b,
            };
            Measure(p);
            pieces.Add(p);
            Registered++;
            if (b != null)
            {
                if (!byBuilding.TryGetValue(b, out var l)) byBuilding[b] = l = new List<Piece>();
                l.Add(p);
                unranked.Add(b);
            }
            if (!hooked) { hooked = true; RenderPipelineManager.beginCameraRendering += BeginCamera; }
        }

        static void Measure(Piece p)
        {
            p.at = p.t.position;
            var wb = p.r.bounds;
            p.centre = wb.center;
            p.radius = wb.extents.magnitude;
        }

        /// <summary>stack the caps of the buildings that got new ones (larger below; each over the larger caps it overlaps in
        /// the same cut plane by <see cref="RankStride"/> layers): when a level's cuts are set, and when the editor has made
        /// what the bake lacked</summary>
        public static void Settle()
        {
            foreach (var b in unranked) if (byBuilding.TryGetValue(b, out var l)) Rank(l);
            unranked.Clear();
        }

        static void Rank(List<Piece> caps)
        {
            caps.Sort((a, b) => b.area.CompareTo(a.area));
            var rank = new int[caps.Count];
            var foot = new Bounds[caps.Count];
            for (int i = 0; i < caps.Count; i++)
            {
                var p = caps[i];
                if (p.r == null) continue;
                var mb = p.cap.bounds;
                foot[i] = new Bounds(p.t.TransformPoint(mb.center), Vector3.Scale(mb.size, p.t.lossyScale) + new Vector3(0.02f, 0.02f, 0.02f));
                int r = 0;
                for (int j = 0; j < i; j++)
                    if (caps[j].r != null && Mathf.Abs(foot[j].center.y - foot[i].center.y) < 0.02f && foot[j].Intersects(foot[i]))
                        r = Mathf.Max(r, rank[j] + 1);
                rank[i] = Mathf.Min(r, 15);
                p.offset = -0.001f + rank[i] * RankStride * Layer;
            }
        }

        // ------------------------------------------------------------------ the pool

        static readonly int SeeId = Shader.PropertyToID("_KitSeeThrough");
        static readonly List<MeshRenderer> pool = new List<MeshRenderer>();
        static readonly List<MeshFilter> poolFilters = new List<MeshFilter>();
        static readonly Piece[] shown = new Piece[PoolSize];
        static readonly List<(float d, Piece p)> near = new List<(float, Piece)>();
        static readonly System.Comparison<(float d, Piece p)> ByDistance = (a, b) => a.d.CompareTo(b.d);
        static Transform poolRoot;
        static int poolFrame = -1;
        static bool hooked;

        static void BeginCamera(ScriptableRenderContext ctx, Camera cam)
        {
            if (cam != null && cam == Camera.main) LayPool(cam);
        }

        /// <summary>the pool's caps over the registered pieces the hole can reach this frame: those whose bounds meet the cone
        /// from the camera to the walker (the hole's radius there), the nearest to the walker first; the shader draws each
        /// only where the hole opened its piece. Nothing while the hole is shut.</summary>
        static void LayPool(Camera cam)
        {
            if (poolFrame == Time.frameCount) return;
            poolFrame = Time.frameCount;
            var see = Shader.GetGlobalVector(SeeId);
            near.Clear();
            if (see.w > 0f && pieces.Count > 0)
            {
                Vector3 eye = cam.transform.position, walker = see;
                var d = walker - eye;
                float L = d.magnitude;
                if (L > 1e-3f)
                {
                    d /= L;
                    bool audit = Time.frameCount % 60 == 0;                     // (pieces of unloaded or moved levels)
                    for (int i = pieces.Count - 1; i >= 0; i--)
                    {
                        var p = pieces[i];
                        if (audit)
                        {
                            if (p.r == null) { pieces.RemoveAt(i); continue; }
                            if (p.t.position != p.at) Measure(p);
                        }
                        var v = p.centre - eye;
                        float t = Vector3.Dot(v, d);
                        if (t < -p.radius || t > L + p.radius) continue;
                        float tc = Mathf.Clamp(t, 0f, L), reach = see.w * tc / L + p.radius + 0.25f;
                        if ((v - d * tc).sqrMagnitude > reach * reach) continue;
                        if (p.r == null) { pieces.RemoveAt(i); continue; }      // its level was unloaded
                        if (!p.r.enabled || !p.r.gameObject.activeInHierarchy) continue;
                        near.Add(((p.centre - walker).sqrMagnitude, p));
                    }
                    near.Sort(ByDistance);
                }
            }
            int n = Mathf.Min(near.Count, PoolSize);
            if (n > 0 && pool.Count == 0) MakePool();
            for (int i = 0; i < pool.Count; i++)
            {
                var cr = pool[i];
                if (cr == null) continue;
                if (i >= n) { if (cr.enabled) cr.enabled = false; shown[i] = null; continue; }
                var p = near[i].p;
                var t = p.t;
                float ly = p.offset / Mathf.Max(1e-4f, t.localToWorldMatrix.m11);
                cr.transform.SetPositionAndRotation(t.TransformPoint(0f, ly, 0f), t.rotation);
                cr.transform.localScale = t.lossyScale;
                if (shown[i] != p)
                {
                    shown[i] = p;
                    poolFilters[i].sharedMesh = p.cap;
                    cr.sharedMaterials = p.mats;
                    cr.gameObject.layer = p.r.gameObject.layer;
                    cr.receiveShadows = p.r.receiveShadows;
                    cr.lightProbeUsage = p.r.lightProbeUsage;
                }
                cr.localBounds = new Bounds(p.local.center - new Vector3(0f, ly, 0f), p.local.size);   // the piece's own bounds
                cr.renderingLayerMask = p.r.renderingLayerMask | KitSeeThrough.CapBit;            // its building open or not
                if (!cr.enabled) cr.enabled = true;
            }
        }

        static void MakePool()
        {
            poolRoot = new GameObject("KitSeeThroughCaps").transform;     // (not DontSave: it goes with the play session)
            Object.DontDestroyOnLoad(poolRoot.gameObject);
            for (int i = 0; i < PoolSize; i++)
            {
                var go = new GameObject("SeeThroughCap");
                go.transform.SetParent(poolRoot, false);
                poolFilters.Add(go.AddComponent<MeshFilter>());
                var cr = go.AddComponent<MeshRenderer>();
                cr.shadowCastingMode = ShadowCastingMode.Off;
                cr.enabled = false;
                pool.Add(cr);
            }
        }

        // ------------------------------------------------------------------ the section

        struct Seg { public Vector2 a, b, n; public int sub; }

        /// <summary>the mesh's solid submeshes cut at local y, filled: a cap mesh (one submesh per material that has a cap),
        /// the source submesh of each, and which take the end grain (bark)</summary>
        static (Mesh, int[], bool[], float) Make(Mesh mesh, float y, uint solid, uint bark)
        {
            Vector3[] v;
            var tris0 = new int[mesh.subMeshCount][];
            try
            {
                using (var data = Mesh.AcquireReadOnlyMeshData(mesh))
                {
                    var md = data[0];
                    using (var pos = new NativeArray<Vector3>(md.vertexCount, Allocator.Temp))
                    {
                        md.GetVertices(pos);
                        v = pos.ToArray();
                    }
                    for (int s = 0; s < md.subMeshCount && s < tris0.Length; s++)
                    {
                        if ((solid & (1u << s)) == 0) continue;
                        using (var idx = new NativeArray<int>(md.GetSubMesh(s).indexCount, Allocator.Temp))
                        {
                            md.GetIndices(idx, s);
                            tris0[s] = idx.ToArray();
                        }
                    }
                }
            }
            catch (System.Exception e) { Debug.LogWarning($"[KitSeeThroughCaps] {mesh.name}: {e.Message}"); return (null, null, null, 0f); }
            var segs = new List<Seg>();
            for (int s = 0; s < mesh.subMeshCount && s < 32; s++)
            {
                if ((solid & (1u << s)) == 0 || tris0[s] == null) continue;
                var tri = tris0[s];
                for (int i = 0; i + 2 < tri.Length; i += 3)
                {
                    Vector3 p0 = v[tri[i]], p1 = v[tri[i + 1]], p2 = v[tri[i + 2]];
                    float d0 = Side(p0.y - y), d1 = Side(p1.y - y), d2 = Side(p2.y - y);
                    int n = 0; Vector2 a = default, b = default;
                    void Edge(Vector3 pa, float da, Vector3 pb, float db)
                    {
                        if ((da < 0) == (db < 0)) return;
                        var x = Vector3.Lerp(pa, pb, da / (da - db));
                        if (n == 0) a = new Vector2(x.x, x.z); else b = new Vector2(x.x, x.z);
                        n++;
                    }
                    Edge(p0, d0, p1, d1); Edge(p1, d1, p2, d2); Edge(p2, d2, p0, d0);
                    var fn = Vector3.Cross(p1 - p0, p2 - p0);                  // the face's outward side (Unity's winding)
                    if (n == 2 && (a - b).sqrMagnitude > Weld * Weld) segs.Add(new Seg { a = a, b = b, n = new Vector2(fn.x, fn.z), sub = s });
                }
            }
            // closed loops per material first; what is left open (a solid whose faces change material round it) together
            var loopsBySub = new Dictionary<int, List<(List<Vector2>, bool)>>();
            var left = new List<Seg>();
            var bySub = new Dictionary<int, List<Seg>>();
            foreach (var sg in segs) { if (!bySub.TryGetValue(sg.sub, out var l)) bySub[sg.sub] = l = new List<Seg>(); l.Add(sg); }
            foreach (var kv in bySub)
                foreach (var (loop, sub, solidIn) in Loops(kv.Value, left))
                {
                    if (!loopsBySub.TryGetValue(sub, out var l)) loopsBySub[sub] = l = new List<(List<Vector2>, bool)>();
                    l.Add((loop, solidIn));
                }
            if (left.Count > 0)
                foreach (var (loop, sub, solidIn) in Loops(new List<Seg>(left), null))
                {
                    if (!loopsBySub.TryGetValue(sub, out var l)) loopsBySub[sub] = l = new List<(List<Vector2>, bool)>();
                    l.Add((loop, solidIn));
                }

            // every outline, filled; then stacked by area (larger below), each Layer over the larger ones it overlaps
            var polys = new List<(List<Vector2> poly, List<int> tri, Vector2 centre, float radius, int sub, Rect box, float area)>();
            foreach (var kv in loopsBySub)
                foreach (var (poly, centre, radius) in Polygons(kv.Value))
                {
                    var t = new List<int>();
                    if (!EarClip(poly, t)) { Failed++; continue; }
                    float area = 0f;
                    for (int i = 0; i + 2 < t.Count; i += 3)
                    {
                        Vector2 a = poly[t[i]], b = poly[t[i + 1]], c = poly[t[i + 2]];
                        area += Mathf.Abs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)) * 0.5f;
                    }
                    Vector2 mn = poly[0], mx = poly[0];
                    foreach (var p in poly) { mn = Vector2.Min(mn, p); mx = Vector2.Max(mx, p); }
                    polys.Add((poly, t, centre, radius, kv.Key, Rect.MinMaxRect(mn.x, mn.y, mx.x, mx.y), area));
                }
            polys.Sort((a, b) => b.area.CompareTo(a.area));
            var layer = new int[polys.Count];
            for (int i = 0; i < polys.Count; i++)
                for (int j = 0; j < i; j++)
                    if (polys[j].box.Overlaps(polys[i].box)) layer[i] = Mathf.Min(RankStride - 1, Mathf.Max(layer[i], layer[j] + 1));

            var verts = new List<Vector3>();
            var uvs = new List<Vector2>();
            var subs = new List<int>();
            var grains = new List<bool>();
            var tris = new List<List<int>>();
            float total = 0f;
            for (int k = 0; k < polys.Count; k++)
            {
                var (poly, t, centre, radius, sub, _, area) = polys[k];
                int si = subs.IndexOf(sub);
                if (si < 0) { si = subs.Count; subs.Add(sub); grains.Add((bark & (1u << sub)) != 0); tris.Add(new List<int>()); }
                bool grain = grains[si];
                var idx = tris[si];
                float py = y + layer[k] * Layer;
                int o = verts.Count;
                foreach (var p in poly)
                {
                    verts.Add(new Vector3(p.x, py, p.y));
                    // end grain: the rings centred on this cut; anything else: its texture laid flat
                    uvs.Add(grain ? new Vector2(0.5f, 0.5f) + (p - centre) / (2f * Mathf.Max(radius, 0.05f)) : p * Tile);
                }
                for (int i = 0; i + 2 < t.Count; i += 3)
                {
                    Vector2 a = poly[t[i]], b = poly[t[i + 1]], c = poly[t[i + 2]];
                    float cr = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
                    if (cr > 0) { idx.Add(o + t[i]); idx.Add(o + t[i + 2]); idx.Add(o + t[i + 1]); }   // facing up (Unity winds clockwise)
                    else { idx.Add(o + t[i]); idx.Add(o + t[i + 1]); idx.Add(o + t[i + 2]); }
                }
                total += area;
            }
            if (subs.Count == 0) return (null, null, null, 0f);
            var m = new Mesh { name = mesh.name + "_Cap" };
            if (verts.Count > 65000) m.indexFormat = IndexFormat.UInt32;
            m.SetVertices(verts);
            var nrm = new Vector3[verts.Count]; var uv = new Vector2[verts.Count]; var col = new Color[verts.Count]; var tan = new Vector4[verts.Count];
            for (int i = 0; i < verts.Count; i++)
            {
                nrm[i] = Vector3.up; uv[i] = uvs[i];
                col[i] = new Color(1f, 1f, 1f, 0f);           // no baked shading, no moss
                tan[i] = new Vector4(1f, 0f, 0f, 1f);
            }
            m.normals = nrm; m.uv = uv; m.colors = col; m.tangents = tan;
            m.subMeshCount = subs.Count;
            for (int s = 0; s < subs.Count; s++) m.SetTriangles(tris[s], s);
            m.RecalculateBounds();
            Made++;
            return (m, subs.ToArray(), grains.ToArray(), total);
        }

        static float Side(float d) => Mathf.Abs(d) < 1e-6f ? 1e-6f : d;      // a vertex on the plane counts as above

        static long Key(Vector2 p) => ((long)Mathf.RoundToInt(p.x / Weld) << 32) ^ (Mathf.RoundToInt(p.y / Weld) & 0xffffffffL);

        /// <summary>the closed loops the segments make (each with the submesh most of its segments came from, and whether the
        /// solid lies inside it -- by the faces' own direction: an outer boundary's faces look out of it, a hole's into it);
        /// the segments of open or branching parts go to `left` (or are dropped when it is null)</summary>
        static IEnumerable<(List<Vector2>, int, bool)> Loops(List<Seg> segs, List<Seg> left)
        {
            var pos = new Dictionary<long, Vector2>();
            var adj = new Dictionary<long, List<(long to, int seg)>>();
            var seen = new HashSet<(long, long)>();
            for (int i = 0; i < segs.Count; i++)
            {
                long ka = Key(segs[i].a), kb = Key(segs[i].b);
                if (ka == kb) continue;
                var e = ka < kb ? (ka, kb) : (kb, ka);
                if (!seen.Add(e)) continue;                    // a face doubled: its section once
                pos[ka] = segs[i].a; pos[kb] = segs[i].b;
                if (!adj.TryGetValue(ka, out var la)) adj[ka] = la = new List<(long, int)>();
                if (!adj.TryGetValue(kb, out var lb)) adj[kb] = lb = new List<(long, int)>();
                la.Add((kb, i)); lb.Add((ka, i));
            }
            var done = new HashSet<long>();
            foreach (var start in adj.Keys)
            {
                if (done.Contains(start)) continue;
                var comp = new List<long>();
                var st = new Stack<long>(); st.Push(start); done.Add(start);
                bool ok = true;
                while (st.Count > 0)
                {
                    var c = st.Pop(); comp.Add(c);
                    if (adj[c].Count != 2) ok = false;
                    foreach (var (to, _) in adj[c]) if (done.Add(to)) st.Push(to);
                }
                if (!ok)
                {
                    if (left != null)
                    {
                        var cs = new HashSet<long>(comp);
                        foreach (var c in comp) foreach (var (to, sg) in adj[c]) if (c < to && cs.Contains(to)) left.Add(segs[sg]);
                    }
                    continue;
                }
                var loop = new List<Vector2>();
                var steps = new List<(Vector2 d, Vector2 n)>();
                var votes = new Dictionary<int, int>();
                long prev = long.MinValue, cur = start;
                do
                {
                    loop.Add(pos[cur]);
                    var nb = adj[cur][0].to == prev ? adj[cur][1] : adj[cur][0];
                    votes.TryGetValue(segs[nb.seg].sub, out int nv); votes[segs[nb.seg].sub] = nv + 1;
                    steps.Add((pos[nb.to] - pos[cur], segs[nb.seg].n));
                    prev = cur; cur = nb.to;
                } while (cur != start && loop.Count <= comp.Count);
                int sub = -1, best = -1;
                foreach (var kv in votes) if (kv.Value > best) { best = kv.Value; sub = kv.Key; }
                if (loop.Count < 3) continue;
                // walked counter-clockwise, the loop's region lies left of each step, its outside to the right
                bool ccw = Area(loop) > 0;
                float vote = 0;
                foreach (var (d, fn) in steps)
                {
                    var outward = ccw ? new Vector2(d.y, -d.x) : new Vector2(-d.y, d.x);
                    float ln = fn.magnitude;
                    if (ln > 1e-12f) vote += Vector2.Dot(fn / ln, outward);
                }
                yield return (loop, sub, vote >= 0);
            }
        }

        // ------------------------------------------------------------------ filling

        static float Area(List<Vector2> p)
        {
            float a = 0;
            for (int i = 0, j = p.Count - 1; i < p.Count; j = i++) a += (p[j].x - p[i].x) * (p[j].y + p[i].y);
            return a * 0.5f;                                   // > 0: counter-clockwise
        }

        static List<Vector2> Clean(List<Vector2> p)
        {
            var q = new List<Vector2>(p);
            bool changed = true;
            while (changed && q.Count >= 3)
            {
                changed = false;
                for (int i = 0; i < q.Count && q.Count >= 3; i++)
                {
                    Vector2 a = q[(i + q.Count - 1) % q.Count], b = q[i], c = q[(i + 1) % q.Count];
                    float cr = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x);
                    if ((b - a).sqrMagnitude < Weld * Weld || Mathf.Abs(cr) < 1e-7f * Mathf.Max(1e-6f, (b - a).magnitude * (c - b).magnitude))
                    { q.RemoveAt(i); i--; changed = true; }
                }
            }
            return q;
        }

        static bool Inside(Vector2 pt, List<Vector2> poly)
        {
            bool c = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
                if ((poly[i].y > pt.y) != (poly[j].y > pt.y) && pt.x < (poly[j].x - poly[i].x) * (pt.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)
                    c = !c;
            return c;
        }

        /// <summary>loops to fillable polygons: each outer loop (the solid inside it, counter-clockwise) with the holes
        /// directly inside it merged in; an outer loop inside another (a root inside a trunk, two pieces of one mesh) is
        /// filled on its own, not cut out. Also the outer loop's centre and reach (for the end grain).</summary>
        static IEnumerable<(List<Vector2>, Vector2, float)> Polygons(List<(List<Vector2> loop, bool solidIn)> raw)
        {
            var loops = new List<List<Vector2>>();
            var solidIn = new List<bool>();
            foreach (var (l, si) in raw) { var c = Clean(l); if (c.Count >= 3 && Mathf.Abs(Area(c)) > 1e-6f) { loops.Add(c); solidIn.Add(si); } }
            int n = loops.Count;
            var parent = new int[n];
            for (int i = 0; i < n; i++)
            {
                parent[i] = -1;
                if (solidIn[i]) continue;
                float best = float.MaxValue;
                for (int j = 0; j < n; j++)                                    // a hole goes to the smallest outer round it
                    if (i != j && solidIn[j] && Inside(loops[i][0], loops[j]) && Mathf.Abs(Area(loops[j])) < best)
                    { best = Mathf.Abs(Area(loops[j])); parent[i] = j; }
            }
            for (int i = 0; i < n; i++)
            {
                if (!solidIn[i]) continue;
                var outer = new List<Vector2>(loops[i]);
                if (Area(outer) < 0) outer.Reverse();
                var centre = Vector2.zero;
                foreach (var p in outer) centre += p;
                centre /= outer.Count;
                float reach = 0f;
                foreach (var p in outer) reach = Mathf.Max(reach, (p - centre).magnitude);
                var holes = new List<List<Vector2>>();
                for (int j = 0; j < n; j++)
                    if (parent[j] == i) { var h = new List<Vector2>(loops[j]); if (Area(h) > 0) h.Reverse(); holes.Add(h); }
                var merged = Merge(outer, holes);
                if (merged != null) yield return (merged, centre, reach); else Failed++;
            }
        }

        static float Cross(Vector2 a, Vector2 b, Vector2 c) => (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);

        static bool InTri(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
        {
            float d1 = Cross(a, b, p), d2 = Cross(b, c, p), d3 = Cross(c, a, p);
            bool neg = d1 < -1e-9f || d2 < -1e-9f || d3 < -1e-9f, pos = d1 > 1e-9f || d2 > 1e-9f || d3 > 1e-9f;
            return !(neg && pos);
        }

        /// <summary>the holes joined to the outer loop by bridges (Eberly): one simple polygon</summary>
        static List<Vector2> Merge(List<Vector2> outer, List<List<Vector2>> holes)
        {
            holes.Sort((h1, h2) => MaxX(h2).CompareTo(MaxX(h1)));
            var poly = outer;
            foreach (var h in holes)
            {
                int mi = 0;
                for (int i = 1; i < h.Count; i++) if (h[i].x > h[mi].x) mi = i;
                var M = h[mi];
                float bx = float.MaxValue; int be = -1;
                for (int i = 0; i < poly.Count; i++)
                {
                    Vector2 a = poly[i], b = poly[(i + 1) % poly.Count];
                    if ((a.y > M.y) == (b.y > M.y)) continue;
                    float x = a.x + (M.y - a.y) * (b.x - a.x) / (b.y - a.y);
                    if (x >= M.x && x < bx) { bx = x; be = i; }
                }
                if (be < 0) return null;
                int pi = poly[be].x > poly[(be + 1) % poly.Count].x ? be : (be + 1) % poly.Count;
                var I = new Vector2(bx, M.y);
                Vector2 P = poly[pi];
                float bestCos = -2f;
                for (int k = 0; k < poly.Count; k++)
                {
                    if (k == pi) continue;
                    Vector2 pk = poly[k], pp = poly[(k + poly.Count - 1) % poly.Count], pn = poly[(k + 1) % poly.Count];
                    if (Cross(pp, pk, pn) >= 0) continue;           // not reflex
                    if (!InTri(pk, M, I, P)) continue;
                    var dv = pk - M; float cos = dv.x / Mathf.Max(dv.magnitude, 1e-9f);
                    if (cos > bestCos) { bestCos = cos; pi = k; }
                }
                var np = new List<Vector2>(poly.Count + h.Count + 2);
                for (int i = 0; i <= pi; i++) np.Add(poly[i]);
                for (int i = 0; i <= h.Count; i++) np.Add(h[(mi + i) % h.Count]);
                np.Add(poly[pi]);
                for (int i = pi + 1; i < poly.Count; i++) np.Add(poly[i]);
                poly = np;
            }
            return poly;
        }

        static float MaxX(List<Vector2> p) { float m = float.MinValue; foreach (var v in p) m = Mathf.Max(m, v.x); return m; }

        /// <summary>a simple counter-clockwise polygon (bridged holes allowed) to triangles; false if it would not close</summary>
        static bool EarClip(List<Vector2> p, List<int> outTri)
        {
            var V = new List<int>(p.Count);
            for (int i = 0; i < p.Count; i++) V.Add(i);
            int guard = 0;
            while (V.Count > 3 && guard++ < 100000)
            {
                bool found = false;
                for (int i = 0; i < V.Count; i++)
                {
                    int a = V[(i + V.Count - 1) % V.Count], b = V[i], c = V[(i + 1) % V.Count];
                    if (Cross(p[a], p[b], p[c]) <= 1e-9f) continue;
                    bool inside = false;
                    for (int j = 0; j < V.Count && !inside; j++)
                    {
                        int k = V[j];
                        if (k == a || k == b || k == c) continue;
                        var pk = p[k];
                        if (pk == p[a] || pk == p[b] || pk == p[c]) continue;   // a bridge's twin
                        if (InTri(pk, p[a], p[b], p[c])) inside = true;
                    }
                    if (inside) continue;
                    outTri.Add(a); outTri.Add(b); outTri.Add(c);
                    V.RemoveAt(i);
                    found = true;
                    break;
                }
                if (found) continue;
                // no ear: drop a flat (collinear) corner if there is one, else give up
                int flat = -1;
                for (int i = 0; i < V.Count; i++)
                {
                    int a = V[(i + V.Count - 1) % V.Count], b = V[i], c = V[(i + 1) % V.Count];
                    if (Mathf.Abs(Cross(p[a], p[b], p[c])) <= 1e-9f) { flat = i; break; }
                }
                if (flat < 0) return false;
                V.RemoveAt(flat);
            }
            if (V.Count == 3 && Cross(p[V[0]], p[V[1]], p[V[2]]) > 0) { outTri.Add(V[0]); outTri.Add(V[1]); outTri.Add(V[2]); }
            return outTri.Count > 0;
        }
    }
}
