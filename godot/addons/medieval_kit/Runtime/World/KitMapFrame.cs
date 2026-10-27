using Godot;

namespace MedievalKit;

/// <summary>
/// A top-down picture of a level and where it lies in the world: the picture's size, the world x, z of its top-left
/// corner and its width and height as world vectors; and a walk grid over it (a char a cell, top row first, '1'
/// walkable) with the reach of the walkable ground in each row and column. A game's area map extends it with what is on
/// the map; a minimap and a camera's <see cref="KitWalkWindow"/> read it. Unity: KitMapFrame (FULL_PORT_PLAN 3a / 6).
/// </summary>
public class KitMapFrame
{
    /// <summary>the picture's size (px)</summary>
    public int Width, Height;
    /// <summary>world x, z of the picture's top-left corner; its width and its height as world x, z vectors</summary>
    public Vector2 Origin, Right, Down;
    /// <summary>the walk grid's size (cells across the picture) and its cells, a char each, top row first ('1': walkable)</summary>
    public int FogW, FogH;
    public string Walk = "";

    /// <summary>a world point on the picture: 0..1 across from the left, 0..1 down from the top</summary>
    public Vector2 ToMap(Vector3 world)
    {
        var d = new Vector2(world.X, world.Z) - Origin;
        return new Vector2(d.Dot(Right) / Mathf.Max(1e-4f, Right.LengthSquared()), d.Dot(Down) / Mathf.Max(1e-4f, Down.LengthSquared()));
    }

    /// <summary>a world direction on the picture (x right, y down)</summary>
    public Vector2 DirOnMap(Vector3 dir)
    {
        var d = new Vector2(dir.X, dir.Z);
        return new Vector2(d.Dot(Right.Normalized()), d.Dot(Down.Normalized()));
    }

    /// <summary>a point on the picture back in the world (x, z)</summary>
    public Vector2 FromMap(Vector2 uv) => Origin + uv.X * Right + uv.Y * Down;

    /// <summary>a world offset (x, z) as an offset on the picture</summary>
    public Vector2 MapDelta(Vector2 d) => new Vector2(d.Dot(Right) / Mathf.Max(1e-4f, Right.LengthSquared()),
                                                      d.Dot(Down) / Mathf.Max(1e-4f, Down.LengthSquared()));

    // the walk grid's reach in each row (first and last walkable cell across) and each column (down), read once
    int[] rowLo, rowHi, colLo, colHi;

    void Spans()
    {
        if (rowLo != null) return;
        rowLo = new int[FogH]; rowHi = new int[FogH]; colLo = new int[FogW]; colHi = new int[FogW];
        for (int j = 0; j < FogH; j++) { rowLo[j] = int.MaxValue; rowHi[j] = -1; }
        for (int i = 0; i < FogW; i++) { colLo[i] = int.MaxValue; colHi[i] = -1; }
        for (int j = 0; j < FogH; j++)
            for (int i = 0; i < FogW; i++)
            {
                int k = j * FogW + i;
                if (k >= Walk.Length || Walk[k] != '1') continue;
                rowLo[j] = Mathf.Min(rowLo[j], i); rowHi[j] = Mathf.Max(rowHi[j], i);
                colLo[i] = Mathf.Min(colLo[i], j); colHi[i] = Mathf.Max(colHi[i], j);
            }
    }

    /// <summary>how far across the picture (u) the walkable ground reaches in the rows between v0 and v1 (false: none)</summary>
    public bool AcrossIn(float v0, float v1, out float u0, out float u1)
    {
        Spans();
        return Span(v0, v1, FogH, FogW, rowLo, rowHi, out u0, out u1);
    }

    /// <summary>how far down the picture (v) the walkable ground reaches in the columns between u0 and u1 (false: none)</summary>
    public bool DownIn(float u0, float u1, out float v0, out float v1)
    {
        Spans();
        return Span(u0, u1, FogW, FogH, colLo, colHi, out v0, out v1);
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
/// Keeps a window on a level -- a camera's view, a minimap -- over its walkable ground: the window follows a point (the
/// player) until its edge would pass, by more than a pad, the walkable ground (the frame's walk grid) in the rows and the
/// columns it covers; a window wider than the ground there is centred on it; and the point always stays inside an inner
/// part of the window (clear of a HUD). The bounds move gently. On the frame's picture (uv). Unity: KitWalkWindow.
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

    /// <summary>the window's focus (uv) for the point p: view is the window round its focus, keep where in it the point
    /// must stay (both offsets round the focus), pad how far the window may reach past the ground, k how much of the way
    /// the bounds move now (1: at once)</summary>
    public Vector2 Fit(KitMapFrame d, Vector2 p, Rect2 view, Rect2 keep, Vector2 pad, float k)
    {
        if (d != of) { of = d; set = false; }
        var f = set ? last : p;
        for (int pass = 0; pass < (set ? 1 : 3); pass++)
        {
            float tu0 = -Open, tu1 = Open, tv0 = -Open, tv1 = Open;
            if (d.AcrossIn(f.Y + view.Position.Y, f.Y + view.End.Y, out var a, out var b)) { tu0 = a - pad.X - view.Position.X; tu1 = b + pad.X - view.End.X; }
            if (d.DownIn(f.X + view.Position.X, f.X + view.End.X, out var c, out var e)) { tv0 = c - pad.Y - view.Position.Y; tv1 = e + pad.Y - view.End.Y; }
            if (!set || pass > 0) { u0 = tu0; u1 = tu1; v0 = tv0; v1 = tv1; }
            else { u0 = Ease(u0, tu0, k); u1 = Ease(u1, tu1, k); v0 = Ease(v0, tv0, k); v1 = Ease(v1, tv1, k); }
            f = new Vector2(Within(p.X, u0, u1), Within(p.Y, v0, v1));
        }
        set = true;
        f.X = Mathf.Clamp(f.X, p.X - keep.End.X, p.X - keep.Position.X);
        f.Y = Mathf.Clamp(f.Y, p.Y - keep.End.Y, p.Y - keep.Position.Y);
        last = f;
        return f;
    }

    static float Within(float x, float lo, float hi) => lo > hi ? (lo + hi) / 2f : Mathf.Clamp(x, lo, hi);

    static float Ease(float from, float to, float k) => Mathf.Abs(from) >= Open || Mathf.Abs(to) >= Open ? to : Mathf.Lerp(from, to, k);
}
