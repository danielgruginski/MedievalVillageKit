using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// What the see-through (Shaders/KitSeeThrough.hlsl) needs to know of a level's pieces, set when the level starts
    /// (KitVillage.Start; nothing is saved in the scene). 2026-10-13 (MedievalSetting, the user's screenshots: a tree cut
    /// to a stump at the hole's foot, a wall end standing whole in a roof's hole, holes ending straight at a joint):
    /// <list type="bullet">
    /// <item><b>Loose pieces</b> (<see cref="Loose"/>): trees, bushes, rocks, props carry rendering layer
    /// <see cref="LooseLayer"/> and open down to the walker's feet; a building's pieces keep their foot (the walls'
    /// footprint). The nature is <b>round</b> too (<see cref="RoundLayer"/>): in the way when the ellipsoid inside its
    /// bounds meets the sight lines to the walker's chest or head, not its box (a bush's box reaches the feet of a walker
    /// beside it: the whole bush went).</item>
    /// <item><b>A building opens as one</b> (<see cref="Building"/>): the shader opens only a piece in the walker's way
    /// (its bounds reach into the line of sight to the walker's upper body), so of a house's walls and roof one piece
    /// opened and its neighbour did not. A building's pieces carry <see cref="GroupLayer"/> instead, and each frame
    /// (<see cref="Decide"/>, from KitVillage.LateUpdate) the building is tested piece by piece: when one is in the way,
    /// all of them carry <see cref="OpenLayer"/> and open (still only in the hole, in front of the walker, above its feet
    /// + the foot kept). On the CPU a piece is in the way when a sight line to the walker's waist, middle or head (and a
    /// half-width to each side) crosses its own box, turned with it (<see cref="Crosses"/>): the world box of a turned
    /// piece is loose (a chapel at 37 degrees opened its corner buttress beside a walker it did not hide).</item>
    /// <item><b>Walls placed as props</b> (<see cref="IsStanding"/>: a town wall, a palisade, a gatehouse, a gate, a tower,
    /// laid along a line as a fence is) are not loose: they keep their foot as a building's walls do, and each run of
    /// them (modules whose boxes touch, <see cref="Runs"/>) opens as one, as a building does (Greywall's town wall is 125
    /// modules under Props).</item>
    /// <item><b>Cuts and caps</b> (<see cref="KitSeeThroughCaps"/>): every piece is cut at 1.4 m over its base, kept in its
    /// rendering layer (<see cref="CutBit"/> and an offset over its origin, <see cref="WithCut"/>), and a piece spanning
    /// the cut gets a real cap (<see cref="CapBit"/>) drawn where the hole opened it.</item>
    /// </list>
    /// </summary>
    public static class KitSeeThrough
    {
        /// <summary>rendering layers (bits) the shader reads: kKitSeeThroughLoose / Round / Group / Open</summary>
        public const int LooseLayer = 16, RoundLayer = 17, GroupLayer = 18, OpenLayer = 19;
        public const uint LooseBit = 1u << LooseLayer, RoundBit = 1u << RoundLayer, GroupBit = 1u << GroupLayer, OpenBit = 1u << OpenLayer;
        /// <summary>a real cap (KitSeeThroughCaps), a cut kept in the layer, and the cut's offset (bits 22-31: signed, in
        /// KitSeeThroughCaps.Step, over the renderer's origin, local units): kKitSeeThroughCapMesh / Cut in the shader</summary>
        public const int CapLayer = 20, CutLayer = 21;
        public const uint CapBit = 1u << CapLayer, CutBit = 1u << CutLayer, CutMask = 0x3FFu << 22;

        /// <summary>the mask with the cut at q steps over the renderer's origin</summary>
        public static uint WithCut(uint mask, int q) => (mask & ~CutMask) | CutBit | ((uint)(q & 0x3FF) << 22);

        /// <summary>the renderer's cut (world y), when it has one</summary>
        public static bool CutY(Renderer r, out float y)
        {
            y = 0f;
            uint m = r.renderingLayerMask;
            if ((m & CutBit) == 0) return false;
            int q = (int)((m >> 22) & 0x3FF);
            if (q >= 512) q -= 1024;
            var M = r.transform.localToWorldMatrix;
            y = M.m13 + M.m11 * (q * KitSeeThroughCaps.Step);
            return true;
        }

        static readonly int SeeId = Shader.PropertyToID("_KitSeeThrough"), ArgsId = Shader.PropertyToID("_KitSeeThroughArgs");

        static readonly string[] Standing = { "TownWall", "Palisade", "Gatehouse", "Gate", "Tower" };

        /// <summary>a piece that stands as architecture though it is placed as a prop (along a line, as a fence)</summary>
        public static bool IsStanding(string name)
        {
            foreach (var w in Standing) if (name.Contains(w)) return true;
            return false;
        }

        /// <summary>every mesh of the pieces under group (its children) opens down to the walker's feet (no foot kept),
        /// but the standing ones (<see cref="IsStanding"/>); round: in the way by the ellipsoid inside its bounds (trees,
        /// bushes, rocks), not by the box</summary>
        public static int Loose(GameObject group, bool round = false)
        {
            int n = 0;
            uint bits = LooseBit | (round ? RoundBit : 0u);
            foreach (Transform piece in group.transform)
            {
                if (IsStanding(piece.name)) continue;
                foreach (var r in piece.GetComponentsInChildren<MeshRenderer>(true)) { r.renderingLayerMask |= bits; n++; }
            }
            return n;
        }

        /// <summary>the standing pieces under group (<see cref="IsStanding"/>), in runs that open as one: modules whose
        /// boxes touch (grown 0.3 m) are one run</summary>
        public static List<Building> Runs(GameObject group)
        {
            var parts = new List<(MeshRenderer[] rs, Bounds b)>();
            foreach (Transform piece in group.transform)
            {
                if (!IsStanding(piece.name)) continue;
                var rs = piece.GetComponentsInChildren<MeshRenderer>(true);
                if (rs.Length == 0) continue;
                var b = rs[0].bounds;
                foreach (var r in rs) b.Encapsulate(r.bounds);
                b.Expand(0.6f);
                parts.Add((rs, b));
            }
            var up = new int[parts.Count];
            for (int i = 0; i < up.Length; i++) up[i] = i;
            int Top(int i) { while (up[i] != i) i = up[i] = up[up[i]]; return i; }
            for (int i = 0; i < parts.Count; i++)
                for (int j = i + 1; j < parts.Count; j++)
                    if (parts[i].b.Intersects(parts[j].b)) up[Top(i)] = Top(j);
            var runs = new Dictionary<int, List<MeshRenderer>>();
            for (int i = 0; i < parts.Count; i++)
            {
                if (!runs.TryGetValue(Top(i), out var l)) runs[Top(i)] = l = new List<MeshRenderer>();
                l.AddRange(parts[i].rs);
            }
            var list = new List<Building>();
            foreach (var l in runs.Values) list.Add(new Building(group.transform, l.ToArray()) { perPiece = true });
            return list;
        }

        /// <summary>a building's pieces, opened together</summary>
        public class Building
        {
            public MeshRenderer[] pieces;
            public bool open;
            /// <summary>its pieces' caps (KitSeeThroughCaps), opened with them</summary>
            public readonly List<MeshRenderer> caps = new List<MeshRenderer>();
            /// <summary>a run of walls placed as props: each piece cut over its own foot (a house: over its floor)</summary>
            public bool perPiece;
            /// <summary>a house's floor (world y): its root's height</summary>
            public float Floor => root != null ? root.position.y : 0f;
            readonly Transform root;
            Bounds all;                       // all its pieces (world), measured with the root at `at`
            Vector3 at = new Vector3(float.NaN, 0f, 0f);

            public Building(GameObject root) : this(root.transform, root.GetComponentsInChildren<MeshRenderer>(true)) { }

            /// <summary>these pieces as one (root: what they move with)</summary>
            public Building(Transform root, MeshRenderer[] pieces)
            {
                this.root = root;
                this.pieces = pieces;
                foreach (var r in pieces) r.renderingLayerMask = (r.renderingLayerMask | GroupBit) & ~OpenBit;
            }

            /// <summary>its pieces' bounds together (measured again if the level moved)</summary>
            Bounds All()
            {
                if (root == null || root.position == at) return all;
                at = root.position;
                bool any = false;
                foreach (var r in pieces)
                    if (r != null) { if (any) all.Encapsulate(r.bounds); else { all = r.bounds; any = true; } }
                return all;
            }

            void Set(bool on)
            {
                if (on == open) return;
                open = on;
                foreach (var r in pieces)
                    if (r != null) r.renderingLayerMask = on ? r.renderingLayerMask | OpenBit : r.renderingLayerMask & ~OpenBit;
                foreach (var r in caps)
                    if (r != null) r.renderingLayerMask = on ? r.renderingLayerMask | OpenBit : r.renderingLayerMask & ~OpenBit;
            }

            /// <summary>open when one of its pieces is in the walker's way</summary>
            public void Decide(Vector3 cam, Vector4 see, Vector4 args)
            {
                bool on = false;
                bool walker = see.x != 0f || see.y != 0f || see.z != 0f;   // (the hole may be shut: the hidden check)
                if (walker && InTheWay(All(), cam, see, args))             // (most buildings: nowhere near)
                    foreach (var r in pieces)
                        if (r != null && r.enabled && r.gameObject.activeInHierarchy && InTheWay(r.bounds, cam, see, args)
                            && Crosses(r, cam, see, args)) { on = true; break; }
                Set(on);
            }
        }

        /// <summary>each building open or not for this frame's see-through (the globals the game set, the main camera)</summary>
        public static void Decide(List<Building> buildings)
        {
            var cam = Camera.main;
            if (cam == null || buildings == null) return;
            Vector4 see = Shader.GetGlobalVector(SeeId), args = Shader.GetGlobalVector(ArgsId);
            var at = cam.transform.position;
            foreach (var b in buildings) b.Decide(at, see, args);
        }

        /// <summary>KitSeeThroughInTheWay (the box): do the bounds meet the wedge from the camera to the walker's upper body
        /// (a box args.w each side of it, from 0.9 to 1.9 times its chest's height over its feet)?</summary>
        public static bool InTheWay(Bounds b, Vector3 cam, Vector4 see, Vector4 args)
        {
            float w = args.w;
            if (w <= 0) return true;
            float feet = args.x, chest = see.y - feet, waist = feet + 0.9f * chest, head = feet + 1.9f * chest;
            var dc = new Vector3(see.x, 0.5f * (waist + head), see.z) - cam;
            var e = new Vector3(w, 0.5f * (head - waist), w);
            Vector3 bmin = b.min, bmax = b.max;
            float lo = 0, hi = 1;
            for (int i = 0; i < 3; i++)
            {
                Le(dc[i] - e[i], bmax[i] - cam[i], ref lo, ref hi);
                Le(-(dc[i] + e[i]), cam[i] - bmin[i], ref lo, ref hi);
            }
            return lo <= hi;
        }

        /// <summary>does a sight line from the camera to the walker's waist, middle or head (at its centre and args.w to
        /// either side, square to the view) cross the renderer's own box (its local bounds, turned with it)?</summary>
        public static bool Crosses(Renderer r, Vector3 cam, Vector4 see, Vector4 args)
        {
            float feet = args.x, chest = see.y - feet;
            var f = new Vector3(see.x - cam.x, 0f, see.z - cam.z);
            var side = f.sqrMagnitude > 1e-6f ? new Vector3(f.z, 0f, -f.x).normalized * Mathf.Max(args.w, 0f) : Vector3.zero;
            var m = r.transform.worldToLocalMatrix;
            var box = r.localBounds;
            var a = m.MultiplyPoint3x4(cam);
            for (int k = 0; k < 3; k++)
            {
                var at = new Vector3(see.x, feet + (0.9f + 0.5f * k) * chest, see.z);
                for (int j = -1; j <= 1; j++)
                    if (Segment(a, m.MultiplyPoint3x4(at + side * j), box)) return true;
            }
            return false;
        }

        /// <summary>does the segment a-b meet the box (slabs)?</summary>
        static bool Segment(Vector3 a, Vector3 b, Bounds box)
        {
            Vector3 d = b - a, mn = box.min, mx = box.max;
            float lo = 0f, hi = 1f;
            for (int i = 0; i < 3; i++)
            {
                if (Mathf.Abs(d[i]) < 1e-6f) { if (a[i] < mn[i] || a[i] > mx[i]) return false; continue; }
                float t1 = (mn[i] - a[i]) / d[i], t2 = (mx[i] - a[i]) / d[i];
                if (t1 > t2) { float t = t1; t1 = t2; t2 = t; }
                lo = Mathf.Max(lo, t1); hi = Mathf.Min(hi, t2);
                if (lo > hi) return false;
            }
            return true;
        }

        static void Le(float a, float b, ref float lo, ref float hi)
        {
            if (a > 1e-6f) hi = Mathf.Min(hi, b / a);
            else if (a < -1e-6f) lo = Mathf.Max(lo, b / a);
            else if (b < 0) hi = -1;
        }
    }
}
