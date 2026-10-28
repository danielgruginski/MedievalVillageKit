using Godot;

namespace MedievalKit;

/// <summary>
/// A fire's light wavering (a child of any Light3D: a burning engine's, a campfire's, a kit light by a fire): three layers
/// of noise move its brightness, its colour (deep orange when low, yellower when high) and a little of its range, and the
/// light itself drifts a few centimetres. <see cref="Level"/> scales it (a fire still catching), <see cref="FadeOut"/>
/// dims it to nothing. Freed, it gives the light back as it found it. Unity: FireFlicker.
/// </summary>
public partial class FireFlicker : Node
{
    static readonly Color Low = new(1f, 0.48f, 0.16f), High = new(1f, 0.64f, 0.32f);
    static FastNoiseLite noise;

    /// <summary>scales its brightness (a fire half alight: about half)</summary>
    public float Level = 1f;
    /// <summary>colours it with the flicker, deep orange to yellow (off: the light keeps its own colour)</summary>
    public bool Tint = true;
    /// <summary>how much it wavers (1: a fire's own light; a room's big light by its hearth: less)</summary>
    public float Depth = 1f;

    Light3D l;
    float baseE, baseRange, seed;
    double fadeFrom = -1, fadeFor = 1;
    Color baseColour;
    Vector3 home;

    /// <summary>where it drifts round (its light's own place, unless a fire moves it)</summary>
    public Vector3 Home { get => home; set => home = value; }

    static double Now => Time.GetTicksMsec() / 1000.0;

    /// <summary>Unity's PerlinNoise (0..1)</summary>
    static float Perlin(float x, float y)
    {
        noise ??= new FastNoiseLite { NoiseType = FastNoiseLite.NoiseTypeEnum.Perlin, Frequency = 1f };
        return Mathf.Clamp(0.5f + 0.5f * noise.GetNoise2D(x, y) * 1.4f, 0f, 1f);
    }

    public override void _Ready()
    {
        l = GetParent() as Light3D;
        seed = GD.Randf() * 100f;
        if (l == null) return;
        home = l.Position;
        baseE = l.LightEnergy; baseColour = l.LightColor;
        baseRange = l is OmniLight3D o ? o.OmniRange : l is SpotLight3D s ? s.SpotRange : 0f;
    }

    /// <summary>dim to nothing over this long</summary>
    public void FadeOut(float seconds) { fadeFrom = Now; fadeFor = Mathf.Max(0.1f, seconds); }

    public override void _Process(double delta)
    {
        if (l == null || !IsInstanceValid(l)) return;
        float t = (float)Now;
        float n = 0.55f * Perlin(t * 5.3f, seed) + 0.3f * Perlin(t * 11.7f, seed + 3.1f) + 0.15f * Perlin(t * 23f, seed + 6.7f);
        float k = fadeFrom < 0 ? 1f : Mathf.Clamp(1f - (float)((Now - fadeFrom) / fadeFor), 0f, 1f);
        l.LightEnergy = baseE * Level * k * (1f + Depth * (0.45f * n - 0.25f));
        if (Tint) l.LightColor = Low.Lerp(High, n);
        float range = baseRange * (1f + Depth * (0.1f * n - 0.05f));
        if (l is OmniLight3D o) o.OmniRange = range; else if (l is SpotLight3D s) s.SpotRange = range;
        float sd = t * 0.9f;                                            // a slow drift, about 12 cm each way
        l.Position = home + 0.24f * new Vector3(Perlin(sd, seed + 11f) - 0.5f, Perlin(sd, seed + 23f) - 0.5f, Perlin(sd, seed + 37f) - 0.5f);
    }

    public override void _ExitTree()
    {
        if (l == null || !IsInstanceValid(l) || !IsQueuedForDeletion()) return;     // (a held level comes back flickering)
        l.LightEnergy = baseE; l.LightColor = baseColour; l.Position = home;
        if (l is OmniLight3D o) o.OmniRange = baseRange; else if (l is SpotLight3D s) s.SpotRange = baseRange;
    }
}
