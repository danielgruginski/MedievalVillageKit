using System;

namespace MedievalKit.UnityMath;

/// <summary>
/// Unity's Mathf as the room generators use it, so the ported generators stay line for line with the Unity kit's and the
/// same seed gives the same level in both engines. Godot's Mathf differs where it matters: Lerp does not clamp,
/// SmoothStep is the Hermite of x between two edges, there is no DeltaAngle, and its trig works in single precision
/// (Unity's goes through double). The generators' files alias it (<c>using Mathf = MedievalKit.UnityMath.Mathf;</c>);
/// everything else in the addon keeps Godot's.
/// Unity's editor runs C# on Mono, which keeps float locals and the steps of an expression in double precision and
/// rounds to float only where a value goes into a field, an array element, a call or a cast (measured 2026-10-28; .NET
/// rounds after every step). A sum of products rounded once can differ from one rounded at each step, so what Unity's
/// own Mathf and Vector2 compute in several steps is computed in double here and rounded once; the generators do the
/// same with their own float locals ("Mono: in double" comments).
/// </summary>
public static class Mathf
{
    public const float PI = (float)Math.PI;
    public const float Deg2Rad = PI * 2f / 360f;
    public const float Rad2Deg = 1f / Deg2Rad;
    public const float Infinity = float.PositiveInfinity;
    public const float Epsilon = float.Epsilon;

    public static float Sin(float f) => (float)Math.Sin(f);
    public static float Cos(float f) => (float)Math.Cos(f);
    public static float Tan(float f) => (float)Math.Tan(f);
    public static float Atan(float f) => (float)Math.Atan(f);
    public static float Atan2(float y, float x) => (float)Math.Atan2(y, x);
    public static float Sqrt(float f) => (float)Math.Sqrt(f);
    public static float Pow(float f, float p) => (float)Math.Pow(f, p);
    public static float Abs(float f) => Math.Abs(f);
    public static int Abs(int v) => Math.Abs(v);
    public static float Min(float a, float b) => a < b ? a : b;
    public static float Min(float a, float b, float c) => Min(Min(a, b), c);
    public static int Min(int a, int b) => a < b ? a : b;
    public static float Max(float a, float b) => a > b ? a : b;
    public static float Max(float a, float b, float c) => Max(Max(a, b), c);
    public static int Max(int a, int b) => a > b ? a : b;
    public static float Min(params float[] v) { float m = v[0]; for (int i = 1; i < v.Length; i++) if (v[i] < m) m = v[i]; return m; }
    public static float Max(params float[] v) { float m = v[0]; for (int i = 1; i < v.Length; i++) if (v[i] > m) m = v[i]; return m; }
    public static int Min(params int[] v) { int m = v[0]; for (int i = 1; i < v.Length; i++) if (v[i] < m) m = v[i]; return m; }
    public static int Max(params int[] v) { int m = v[0]; for (int i = 1; i < v.Length; i++) if (v[i] > m) m = v[i]; return m; }
    public static float Sign(float f) => f >= 0f ? 1f : -1f;
    public static float Round(float f) => (float)Math.Round(f);
    public static float Floor(float f) => (float)Math.Floor(f);
    public static float Ceil(float f) => (float)Math.Ceiling(f);
    public static int RoundToInt(float f) => (int)Math.Round(f);
    public static int FloorToInt(float f) => (int)Math.Floor(f);
    public static int CeilToInt(float f) => (int)Math.Ceiling(f);

    public static float Clamp(float v, float min, float max) => v < min ? min : v > max ? max : v;
    public static int Clamp(int v, int min, int max) => v < min ? min : v > max ? max : v;
    public static float Clamp01(float v) => v < 0f ? 0f : v > 1f ? 1f : v;
    public static float Lerp(float a, float b, float t) => (float)(a + ((double)b - a) * Clamp01(t));
    public static float InverseLerp(float a, float b, float v) => a != b ? Clamp01((float)(((double)v - a) / ((double)b - a))) : 0f;

    public static float SmoothStep(float from, float to, float t)
    {
        double u = Clamp01(t);
        u = -2.0 * u * u * u + 3.0 * u * u;
        return (float)(to * u + from * (1.0 - u));
    }

    public static float Repeat(float t, float length) => Clamp((float)(t - (double)Floor(t / length) * length), 0f, length);

    public static float DeltaAngle(float current, float target)
    {
        double d = Repeat(target - current, 360f);
        if (d > 180.0) d -= 360.0;
        return (float)d;
    }

    public static bool Approximately(float a, float b) =>
        Math.Abs(b - a) < Math.Max(1e-6f * Math.Max(Math.Abs(a), Math.Abs(b)), Epsilon * 8f);

    /// <summary>Unity's Mathf.PerlinNoise (native code there), matched against 400 of its samples (2026-10-28, to 1e-5):
    /// Ken Perlin's improved noise in 3D at z = 0, on |x| and |y| (the noise is mirrored about the axes), mapped by
    /// (n + 0.69) / 1.483 -- about 0..1, a lattice point 0.4652731</summary>
    public static float PerlinNoise(float x, float y)
    {
        x = Math.Abs(x); y = Math.Abs(y);
        float fx = (float)Math.Floor(x), fy = (float)Math.Floor(y);
        int X = (int)fx & 255, Y = (int)fy & 255;
        x -= fx; y -= fy;
        float u = Fade(x), v = Fade(y);
        int A = Perm[X] + Y, AA = Perm[A], AB = Perm[A + 1], B = Perm[X + 1] + Y, BA = Perm[B], BB = Perm[B + 1];
        float n = Lerp0(v, Lerp0(u, Grad(Perm[AA], x, y), Grad(Perm[BA], x - 1, y)),
                           Lerp0(u, Grad(Perm[AB], x, y - 1), Grad(Perm[BB], x - 1, y - 1)));
        return (n + 0.69f) / 1.483f;
    }

    static float Fade(float t) => t * t * t * (t * (t * 6f - 15f) + 10f);
    static float Lerp0(float t, float a, float b) => a + t * (b - a);

    static float Grad(int h, float x, float y)
    {
        h &= 15;
        float u = h < 8 ? x : y, v = h < 4 ? y : h == 12 || h == 14 ? x : 0f;
        return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
    }

    static readonly int[] Perm = MakePerm();

    static int[] MakePerm()
    {
        int[] p =
        {
            151,160,137,91,90,15,131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,190,6,148,
            247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,88,237,149,56,87,174,20,125,136,171,168,68,175,
            74,165,71,134,139,48,27,166,77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,102,143,54,
            65,25,63,161,1,216,80,73,209,76,132,187,208,89,18,169,200,196,135,130,116,188,159,86,164,100,109,198,173,186,3,64,
            52,217,226,250,124,123,5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,223,183,170,213,
            119,248,152,2,44,154,163,70,221,153,101,155,167,43,172,9,129,22,39,253,19,98,108,110,79,113,224,232,178,185,112,104,
            218,246,97,228,251,34,242,193,238,210,144,12,191,179,162,241,81,51,145,235,249,14,239,107,49,192,214,31,181,199,106,157,
            184,84,204,176,115,121,50,45,127,4,150,254,138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180,
        };
        var o = new int[512];
        for (int i = 0; i < 512; i++) o[i] = p[i & 255];
        return o;
    }
}

/// <summary>Unity's Rect (lower-case members): x, y the min corner, width, height</summary>
public struct Rect
{
    public float x, y, width, height;

    public Rect(float x, float y, float width, float height) { this.x = x; this.y = y; this.width = width; this.height = height; }

    public static Rect MinMaxRect(float xmin, float ymin, float xmax, float ymax) => new(xmin, ymin, xmax - xmin, ymax - ymin);

    public float xMin => x;
    public float yMin => y;
    public float xMax => x + width;
    public float yMax => y + height;
    public Vector2 center => new(x + width / 2f, y + height / 2f);
    public Vector2 min => new(x, y);
    public Vector2 max => new(x + width, y + height);

    public bool Contains(Vector2 p) => p.x >= xMin && p.x < xMax && p.y >= yMin && p.y < yMax;
    public bool Overlaps(Rect o) => o.xMax > xMin && o.xMin < xMax && o.yMax > yMin && o.yMin < yMax;
}

/// <summary>Unity's Vector3 as far as the rooms' boxes use it (lower-case members), Blender room space</summary>
public struct Vector3
{
    public float x, y, z;

    public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
}

/// <summary>Unity's Vector2 (lower-case members, its == within 1e-5, its normalized) for the ported generators.</summary>
public struct Vector2 : IEquatable<Vector2>
{
    public float x, y;

    public Vector2(float x, float y) { this.x = x; this.y = y; }

    public static Vector2 zero => new(0f, 0f);
    public static Vector2 one => new(1f, 1f);
    public static Vector2 up => new(0f, 1f);
    public static Vector2 down => new(0f, -1f);
    public static Vector2 left => new(-1f, 0f);
    public static Vector2 right => new(1f, 0f);

    public static Vector2 Lerp(Vector2 a, Vector2 b, float t)
    {
        double u = Mathf.Clamp01(t);
        return new Vector2((float)(a.x + ((double)b.x - a.x) * u), (float)(a.y + ((double)b.y - a.y) * u));
    }

    public static Vector2 Min(Vector2 a, Vector2 b) => new(Math.Min(a.x, b.x), Math.Min(a.y, b.y));
    public static Vector2 Max(Vector2 a, Vector2 b) => new(Math.Max(a.x, b.x), Math.Max(a.y, b.y));

    public float this[int i]
    {
        get => i == 0 ? x : i == 1 ? y : throw new IndexOutOfRangeException();
        set { if (i == 0) x = value; else if (i == 1) y = value; else throw new IndexOutOfRangeException(); }
    }

    public float sqrMagnitude => (float)((double)x * x + (double)y * y);
    public float magnitude => (float)Math.Sqrt((double)x * x + (double)y * y);

    public Vector2 normalized
    {
        get
        {
            float m = magnitude;
            return m > 1e-5f ? this / m : zero;
        }
    }

    public static float Dot(Vector2 a, Vector2 b) => (float)((double)a.x * b.x + (double)a.y * b.y);
    public static float Distance(Vector2 a, Vector2 b) => (a - b).magnitude;

    public static Vector2 operator +(Vector2 a, Vector2 b) => new(a.x + b.x, a.y + b.y);
    public static Vector2 operator -(Vector2 a, Vector2 b) => new(a.x - b.x, a.y - b.y);
    public static Vector2 operator -(Vector2 a) => new(-a.x, -a.y);
    public static Vector2 operator *(Vector2 a, float d) => new(a.x * d, a.y * d);
    public static Vector2 operator *(float d, Vector2 a) => new(a.x * d, a.y * d);
    public static Vector2 operator /(Vector2 a, float d) => new(a.x / d, a.y / d);

    public static bool operator ==(Vector2 a, Vector2 b)
    {
        double dx = a.x - b.x, dy = a.y - b.y;
        return dx * dx + dy * dy < 1e-5f * 1e-5f;
    }

    public static bool operator !=(Vector2 a, Vector2 b) => !(a == b);
    public bool Equals(Vector2 o) => x.Equals(o.x) && y.Equals(o.y);
    public override bool Equals(object o) => o is Vector2 v && Equals(v);
    public override int GetHashCode() => x.GetHashCode() ^ (y.GetHashCode() << 2);
    public override string ToString() => $"({x:F2}, {y:F2})";
}
