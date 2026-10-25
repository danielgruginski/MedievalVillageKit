using System;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A top-down picture of a level and where it lies in the world: the picture's size, the world x, z of its top-left
    /// corner and its width and height as world vectors; and a walk grid over it (a char a cell, top row first, '1'
    /// walkable) with the reach of the walkable ground in each row and column. A game's area map extends it with what is
    /// on the map; a minimap and a camera's <see cref="KitWalkWindow"/> read it. Serializable (JsonUtility). From the Guild
    /// RPG's AreaMapData (FULL_PORT_PLAN phase 3a).
    /// </summary>
    [Serializable]
    public class KitMapFrame
    {
        /// <summary>the picture's size (px)</summary>
        public int width, height;
        /// <summary>world x, z of the picture's top-left corner; its width and its height as world x, z vectors</summary>
        public Vector2 origin, right, down;
        /// <summary>the walk grid's size (cells across the picture) and its cells, a char each, top row first ('1': walkable)</summary>
        public int fogW, fogH;
        public string walk = "";

        /// <summary>a world point on the picture: 0..1 across from the left, 0..1 down from the top</summary>
        public Vector2 ToMap(Vector3 world)
        {
            var d = new Vector2(world.x, world.z) - origin;
            return new Vector2(Vector2.Dot(d, right) / Mathf.Max(1e-4f, right.sqrMagnitude),
                               Vector2.Dot(d, down) / Mathf.Max(1e-4f, down.sqrMagnitude));
        }

        /// <summary>a world direction on the picture (x right, y down)</summary>
        public Vector2 DirOnMap(Vector3 dir)
        {
            var d = new Vector2(dir.x, dir.z);
            return new Vector2(Vector2.Dot(d, right.normalized), Vector2.Dot(d, down.normalized));
        }

        /// <summary>a point on the picture back in the world (x, z)</summary>
        public Vector2 FromMap(Vector2 uv) => origin + uv.x * right + uv.y * down;

        /// <summary>a world offset (x, z) as an offset on the picture</summary>
        public Vector2 MapDelta(Vector2 d) => new Vector2(Vector2.Dot(d, right) / Mathf.Max(1e-4f, right.sqrMagnitude),
                                                          Vector2.Dot(d, down) / Mathf.Max(1e-4f, down.sqrMagnitude));

        // the walk grid's reach in each row (first and last walkable cell across) and each column (down), read once
        [NonSerialized] int[] rowLo, rowHi, colLo, colHi;

        void Spans()
        {
            if (rowLo != null) return;
            rowLo = new int[fogH]; rowHi = new int[fogH]; colLo = new int[fogW]; colHi = new int[fogW];
            for (int j = 0; j < fogH; j++) { rowLo[j] = int.MaxValue; rowHi[j] = -1; }
            for (int i = 0; i < fogW; i++) { colLo[i] = int.MaxValue; colHi[i] = -1; }
            for (int j = 0; j < fogH; j++)
                for (int i = 0; i < fogW; i++)
                {
                    int k = j * fogW + i;
                    if (k >= walk.Length || walk[k] != '1') continue;
                    rowLo[j] = Mathf.Min(rowLo[j], i); rowHi[j] = Mathf.Max(rowHi[j], i);
                    colLo[i] = Mathf.Min(colLo[i], j); colHi[i] = Mathf.Max(colHi[i], j);
                }
        }

        /// <summary>how far across the picture (u) the walkable ground reaches in the rows between v0 and v1 (false: none)</summary>
        public bool AcrossIn(float v0, float v1, out float u0, out float u1)
        {
            Spans();
            return Span(v0, v1, fogH, fogW, rowLo, rowHi, out u0, out u1);
        }

        /// <summary>how far down the picture (v) the walkable ground reaches in the columns between u0 and u1 (false: none)</summary>
        public bool DownIn(float u0, float u1, out float v0, out float v1)
        {
            Spans();
            return Span(u0, u1, fogW, fogH, colLo, colHi, out v0, out v1);
        }

        static bool Span(float a, float b, int n, int m, int[] lo, int[] hi, out float s0, out float s1)
        {
            s0 = 0f; s1 = 1f;
            if (n <= 0 || m <= 0) return false;
            int k0 = Mathf.Clamp(Mathf.FloorToInt(a * n), 0, n - 1), k1 = Mathf.Clamp(Mathf.CeilToInt(b * n) - 1, 0, n - 1);
            int l = int.MaxValue, h = -1;
            for (int k = k0; k <= k1; k++)
                if (hi[k] >= 0) { l = Mathf.Min(l, lo[k]); h = Mathf.Max(h, hi[k]); }
            if (h < 0) return false;
            s0 = l / (float)m; s1 = (h + 1) / (float)m;
            return true;
        }
    }

    /// <summary>
    /// Keeps a window on a level -- a camera's view, a minimap -- over its walkable ground (the Guild RPG, 2026-10-11: at a
    /// map's border the camera showed ground nobody can walk on, "boxing the field of view into the action area"). The
    /// window follows a point (the player) until its edge would pass, by more than a pad, the walkable ground (the frame's
    /// walk grid) in the rows and the columns it covers; a window wider than the ground there is centred on it; and the
    /// point always stays inside an inner part of the window (clear of a HUD, inside a minimap's disc). The bounds move
    /// gently: a road out coming into view swings the window over rather than jumping. On the frame's picture (uv).
    /// </summary>
    public class KitWalkWindow
    {
        const float Open = 1e3f;                                 // no ground in the band: no bound

        KitMapFrame of;
        bool set;
        float u0, u1, v0, v1;                                    // where the window's focus may be
        Vector2 last;

        /// <summary>start again at once (a new level, after a cut)</summary>
        public void Reset() => set = false;

        /// <summary>the window's focus (uv) for the point p: <paramref name="view"/> is the window round its focus,
        /// <paramref name="keep"/> where in it the point must stay (both offsets round the focus), <paramref name="pad"/> how
        /// far the window may reach past the ground, <paramref name="k"/> how much of the way the bounds move now (1: at once)</summary>
        public Vector2 Fit(KitMapFrame d, Vector2 p, Rect view, Rect keep, Vector2 pad, float k)
        {
            if (d != of) { of = d; set = false; }
            var f = set ? last : p;
            for (int pass = 0; pass < (set ? 1 : 3); pass++)              // the first time: settle the bands round the point
            {
                float tu0 = -Open, tu1 = Open, tv0 = -Open, tv1 = Open;
                if (d.AcrossIn(f.y + view.yMin, f.y + view.yMax, out var a, out var b)) { tu0 = a - pad.x - view.xMin; tu1 = b + pad.x - view.xMax; }
                if (d.DownIn(f.x + view.xMin, f.x + view.xMax, out var c, out var e)) { tv0 = c - pad.y - view.yMin; tv1 = e + pad.y - view.yMax; }
                if (!set || pass > 0) { u0 = tu0; u1 = tu1; v0 = tv0; v1 = tv1; }
                else { u0 = Ease(u0, tu0, k); u1 = Ease(u1, tu1, k); v0 = Ease(v0, tv0, k); v1 = Ease(v1, tv1, k); }
                f = new Vector2(Within(p.x, u0, u1), Within(p.y, v0, v1));
            }
            set = true;
            f.x = Mathf.Clamp(f.x, p.x - keep.xMax, p.x - keep.xMin);
            f.y = Mathf.Clamp(f.y, p.y - keep.yMax, p.y - keep.yMin);
            last = f;
            return f;
        }

        static float Within(float x, float lo, float hi) => lo > hi ? (lo + hi) / 2f : Mathf.Clamp(x, lo, hi);

        // a bound to or from "none" changes at once (easing from 1000 would take seconds)
        static float Ease(float from, float to, float k) => Mathf.Abs(from) >= Open || Mathf.Abs(to) >= Open ? to : Mathf.Lerp(from, to, k);
    }
}
