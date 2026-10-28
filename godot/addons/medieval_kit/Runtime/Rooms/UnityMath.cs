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
