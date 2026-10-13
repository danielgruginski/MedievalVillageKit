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
    /// origin in <see cref="Step"/> steps), so the shader cuts exactly where the cap lies. A cap is a child of its piece
    /// (same materials, the texture laid flat on the cut, lit as a level face), sharing its bounds and its see-through
    /// bits; cap meshes are cached per mesh, cut and solid materials, so the instances of a piece share one.</para>
    /// <para>Prototype: when the level starts, <see cref="Cut"/> sets each piece's cut and queues its cap; the editor makes
    /// the queued caps between frames (<see cref="Flush"/>, from MedievalKit.Editor's KitSeeThroughCapsHook): the kit's
    /// meshes are not Read/Write, and in play mode only editor code may read them (Mesh.AcquireReadOnlyMeshData). A player
    /// build gets no caps until they are baked (the cut itself works there).</para>
    /// </summary>
    public static class KitSeeThroughCaps
    {
        /// <summary>the cut over each piece's base (m): MedievalSetting's GameCamera.keepBelow</summary>
        public const float Height = 1.4f;
        /// <summary>the cut's offset is kept in the rendering layer in these steps (local units)</summary>
        public const float Step = 0.05f;
        const float Weld = 1e-3f;               // section points closer than this are one
        const float Tile = 0.5f;                // the cap's texture: tiles per (local) metre

        static readonly Dictionary<(Mesh, int, uint), (Mesh mesh, int[] mats)> cache = new Dictionary<(Mesh, int, uint), (Mesh, int[])>();
        static readonly Queue<(MeshRenderer r, Mesh mesh, int q, uint solid, KitSeeThrough.Building b)> pending =
            new Queue<(MeshRenderer, Mesh, int, uint, KitSeeThrough.Building)>();
        static float flushStart = -1f;
        static int flushPlaced;

        /// <summary>caps still to make</summary>
        public static int Pending => pending.Count;

        /// <summary>made since the start: caps placed, cap meshes made, polygons that could not be filled</summary>
        public static int Placed, Made, Failed;

        static bool Solid(Material m) =>
            m != null && m.shader != null && m.shader.name == "MedievalKit/KitLit" && m.HasProperty("_Cull") && m.GetFloat("_Cull") > 1.5f
            && (!m.HasProperty("_Surface") || m.GetFloat("_Surface") < 0.5f);

        /// <summary>the renderer's cut at baseY + <see cref="Height"/> (world), kept in its rendering layer; where it spans the
        /// cut, its cap is queued (made by <see cref="Flush"/>; a building's caps open with it)</summary>
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
            for (int s = 0; s < mats.Length && s < mesh.subMeshCount && s < 32; s++) if (Solid(mats[s])) solid |= 1u << s;
            if (solid == 0) return;
            pending.Enqueue((r, mesh, q, solid, b));
        }

        /// <summary>make queued caps for up to `budgetMs` of this frame; returns how many are left. Editor only for now
        /// (see the class).</summary>
        public static int Flush(float budgetMs = 8f)
        {
            if (pending.Count == 0) return 0;
            float start = Time.realtimeSinceStartup;
            if (flushStart < 0f) { flushStart = start; flushPlaced = Placed; }
            while (pending.Count > 0 && (Time.realtimeSinceStartup - start) * 1000f < budgetMs)
            {
                var (r, mesh, q, solid, b) = pending.Dequeue();
                if (r == null) continue;
                var cap = Place(r, mesh, q, solid);
                if (cap != null && b != null) b.caps.Add(cap);
            }
            if (pending.Count == 0)
            {
                Debug.Log($"[KitSeeThroughCaps] {Placed - flushPlaced} caps placed ({Made} cap meshes so far, {Failed} polygons not filled) " +
                          $"over {(Time.realtimeSinceStartup - flushStart) * 1000f:F0} ms");
                flushStart = -1f;
            }
            return pending.Count;
        }

        static MeshRenderer Place(MeshRenderer r, Mesh mesh, int q, uint solid)
        {
            var t = r.transform;
            float sy = t.localToWorldMatrix.m11;
            var b = mesh.bounds;
            var mats = r.sharedMaterials;
            var key = (mesh, q, solid);
            if (!cache.TryGetValue(key, out var cap)) cache[key] = cap = Make(mesh, q * Step, solid);
            if (cap.mesh == null) return null;

            var go = new GameObject("SeeThroughCap");
            go.layer = r.gameObject.layer;
            go.transform.SetParent(t, false);
            // a millimetre or few under the cut, by place: the caps of pieces that overlap (a wall's end inside a corner
            // buttress) do not lie in one plane and fight
            var p = t.position;
            float jitter = 0.001f + 0.003f * Mathf.Repeat(Mathf.Sin(p.x * 12.9898f + p.z * 78.233f) * 43758.5453f, 1f);
            go.transform.localPosition = new Vector3(0f, -jitter / sy, 0f);
            go.AddComponent<MeshFilter>().sharedMesh = cap.mesh;
            var cr = go.AddComponent<MeshRenderer>();
            var cm = new Material[cap.mats.Length];
            for (int i = 0; i < cm.Length; i++) cm[i] = mats[cap.mats[i]];
            cr.sharedMaterials = cm;
            cr.shadowCastingMode = ShadowCastingMode.Off;
            cr.receiveShadows = r.receiveShadows;
            cr.lightProbeUsage = r.lightProbeUsage;
            cr.renderingLayerMask = r.renderingLayerMask | KitSeeThrough.CapBit;
            cr.localBounds = new Bounds(b.center + new Vector3(0f, jitter / sy, 0f), b.size);   // the piece's own bounds
            Placed++;
            return cr;
        }

        // ------------------------------------------------------------------ the section

        struct Seg { public Vector2 a, b; public int sub; }

        /// <summary>the mesh's solid submeshes cut at local y, filled: a cap mesh (one submesh per material that has a cap)
        /// and the source submesh of each</summary>
        static (Mesh, int[]) Make(Mesh mesh, float y, uint solid)
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
            catch (System.Exception e) { Debug.LogWarning($"[KitSeeThroughCaps] {mesh.name}: {e.Message}"); return (null, null); }
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
                    if (n == 2 && (a - b).sqrMagnitude > Weld * Weld) segs.Add(new Seg { a = a, b = b, sub = s });
                }
            }
            // closed loops per material first; what is left open (a solid whose faces change material round it) together
            var loopsBySub = new Dictionary<int, List<List<Vector2>>>();
            var left = new List<Seg>();
            var bySub = new Dictionary<int, List<Seg>>();
            foreach (var sg in segs) { if (!bySub.TryGetValue(sg.sub, out var l)) bySub[sg.sub] = l = new List<Seg>(); l.Add(sg); }
            foreach (var kv in bySub)
                foreach (var (loop, sub) in Loops(kv.Value, left))
                {
                    if (!loopsBySub.TryGetValue(sub, out var l)) loopsBySub[sub] = l = new List<List<Vector2>>();
                    l.Add(loop);
                }
            if (left.Count > 0)
                foreach (var (loop, sub) in Loops(new List<Seg>(left), null))
                {
                    if (!loopsBySub.TryGetValue(sub, out var l)) loopsBySub[sub] = l = new List<List<Vector2>>();
                    l.Add(loop);
                }

            var verts = new List<Vector3>();
            var subs = new List<int>();
            var tris = new List<List<int>>();
            foreach (var kv in loopsBySub)
            {
                var idx = new List<int>();
                foreach (var poly in Polygons(kv.Value))
                {
                    var t = new List<int>();
                    if (!EarClip(poly, t)) { Failed++; continue; }
                    int o = verts.Count;
                    foreach (var p in poly) verts.Add(new Vector3(p.x, y, p.y));
                    for (int i = 0; i + 2 < t.Count; i += 3)
                    {
                        Vector2 a = poly[t[i]], b = poly[t[i + 1]], c = poly[t[i + 2]];
                        float cr = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
                        if (cr > 0) { idx.Add(o + t[i]); idx.Add(o + t[i + 2]); idx.Add(o + t[i + 1]); }   // facing up (Unity winds clockwise)
                        else { idx.Add(o + t[i]); idx.Add(o + t[i + 1]); idx.Add(o + t[i + 2]); }
                    }
                }
                if (idx.Count == 0) continue;
                subs.Add(kv.Key); tris.Add(idx);
            }
            if (subs.Count == 0) return (null, null);
            var m = new Mesh { name = mesh.name + "_Cap" };
            if (verts.Count > 65000) m.indexFormat = IndexFormat.UInt32;
            m.SetVertices(verts);
            var nrm = new Vector3[verts.Count]; var uv = new Vector2[verts.Count]; var col = new Color[verts.Count]; var tan = new Vector4[verts.Count];
            for (int i = 0; i < verts.Count; i++)
            {
                nrm[i] = Vector3.up; uv[i] = new Vector2(verts[i].x, verts[i].z) * Tile;
                col[i] = new Color(1f, 1f, 1f, 0f);           // no baked shading, no moss
                tan[i] = new Vector4(1f, 0f, 0f, 1f);
            }
            m.normals = nrm; m.uv = uv; m.colors = col; m.tangents = tan;
            m.subMeshCount = subs.Count;
            for (int s = 0; s < subs.Count; s++) m.SetTriangles(tris[s], s);
            m.RecalculateBounds();
            Made++;
            return (m, subs.ToArray());
        }

        static float Side(float d) => Mathf.Abs(d) < 1e-6f ? 1e-6f : d;      // a vertex on the plane counts as above

        static long Key(Vector2 p) => ((long)Mathf.RoundToInt(p.x / Weld) << 32) ^ (Mathf.RoundToInt(p.y / Weld) & 0xffffffffL);

        /// <summary>the closed loops the segments make (each with the submesh most of its segments came from); the segments
        /// of open or branching parts go to `left` (or are dropped when it is null)</summary>
        static IEnumerable<(List<Vector2>, int)> Loops(List<Seg> segs, List<Seg> left)
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
                var votes = new Dictionary<int, int>();
                long prev = long.MinValue, cur = start;
                do
                {
                    loop.Add(pos[cur]);
                    var nb = adj[cur][0].to == prev ? adj[cur][1] : adj[cur][0];
                    votes.TryGetValue(segs[nb.seg].sub, out int nv); votes[segs[nb.seg].sub] = nv + 1;
                    prev = cur; cur = nb.to;
                } while (cur != start && loop.Count <= comp.Count);
                int sub = -1, best = -1;
                foreach (var kv in votes) if (kv.Value > best) { best = kv.Value; sub = kv.Key; }
                if (loop.Count >= 3) yield return (loop, sub);
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

        /// <summary>loops to fillable polygons: each outer loop (counter-clockwise) with the loops directly inside it merged
        /// in as holes</summary>
        static IEnumerable<List<Vector2>> Polygons(List<List<Vector2>> raw)
        {
            var loops = new List<List<Vector2>>();
            foreach (var l in raw) { var c = Clean(l); if (c.Count >= 3 && Mathf.Abs(Area(c)) > 1e-6f) loops.Add(c); }
            int n = loops.Count;
            var depth = new int[n];
            var parent = new int[n];
            for (int i = 0; i < n; i++)
            {
                parent[i] = -1;
                for (int j = 0; j < n; j++)
                    if (i != j && Inside(loops[i][0], loops[j])) depth[i]++;
            }
            for (int i = 0; i < n; i++)
            {
                if (depth[i] % 2 == 0) continue;
                for (int j = 0; j < n; j++)
                    if (i != j && depth[j] == depth[i] - 1 && Inside(loops[i][0], loops[j])) { parent[i] = j; break; }
            }
            for (int i = 0; i < n; i++)
            {
                if (depth[i] % 2 != 0) continue;
                var outer = new List<Vector2>(loops[i]);
                if (Area(outer) < 0) outer.Reverse();
                var holes = new List<List<Vector2>>();
                for (int j = 0; j < n; j++)
                    if (parent[j] == i) { var h = new List<Vector2>(loops[j]); if (Area(h) > 0) h.Reverse(); holes.Add(h); }
                var merged = Merge(outer, holes);
                if (merged != null) yield return merged; else Failed++;
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
