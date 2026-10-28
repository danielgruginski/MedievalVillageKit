using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// Fire on a thing in the world, made of <see cref="FireFx"/>'s parts: <see cref="Blaze"/> -- flames on spots on its
/// timbers, catching at the one nearest where it was lit and spreading one spot at a time, embers, a glow, a smoke column,
/// a flickering light -- for a siege engine set alight; <see cref="Collapse"/> when it falls in; <see cref="Smoulder"/>
/// for what is left once it has burned down; <see cref="Burst"/> for a fire circle going off; <see cref="Steady"/> for the
/// kit's torches, braziers and hearths; <see cref="Splash"/> for a bolt of fire landing. Each goes under the parent it is
/// given (the one-off ones under the current scene), so it leaves with its level. Unity: Fire.
/// </summary>
public static class Fire
{
    /// <summary>the fires' sounds, played by the game (the kit has none): a loop on a node, a one-shot at a point (id,
    /// where, volume, pitch); unset = silent</summary>
    public static Action<string, Node3D, float, float> SoundLoop;
    public static Action<string, Vector3, float, float> SoundAt;

    /// <summary>seconds between one spot catching and the next (the siege tower's 18: alight all over in about 6 s)</summary>
    public const float SpreadSeconds = 0.35f;

    static Node Scene => ((SceneTree)Engine.GetMainLoop()).CurrentScene ?? ((SceneTree)Engine.GetMainLoop()).Root;

    /// <summary>a fire on a thing (<paramref name="local"/>: its box in the parent's space), flames on the
    /// <paramref name="spots"/> (the parent's space, on its timbers; none: round its footprint) at <paramref name="scale"/>
    /// (1: the siege tower's); lit from <paramref name="from"/> (a world point) it catches at the spot nearest it and
    /// spreads, else it is alight all over at once</summary>
    public static Node3D Blaze(Node3D parent, Aabb local, IList<Vector3> spots = null, float scale = 1f, Vector3? from = null)
    {
        var list = new List<Vector3>(spots != null && spots.Count > 0 ? spots : Footprint(local));
        if (from.HasValue)
        {
            var f = parent.GlobalTransform.AffineInverse() * from.Value;
            list.Sort((a, b) => (a - f).LengthSquared().CompareTo((b - f).LengthSquared()));
        }
        var go = new Blazing { Name = "Fire" };
        parent.AddChild(go);                                              // at the parent's origin: the spots are in its space
        go.Init(list, scale > 0f ? scale : 1f, local, from.HasValue ? 1 : list.Count);
        SoundLoop?.Invoke("blaze_loop", go, Mathf.Clamp(scale, 0.6f, 1.4f), 1f);
        return go;
    }

    /// <summary>a blaze falling in: a gust of sparks and big puffs of smoke, its flames going out over the first half of
    /// <paramref name="seconds"/> (the highest first), then it is gone; any other fire dies down (<see cref="Douse"/>)</summary>
    public static void Collapse(Node3D fire, float seconds = 6f)
    {
        if (fire == null || !GodotObject.IsInstanceValid(fire)) return;
        if (fire is not Blazing b) { Douse(fire, seconds); return; }
        b.Collapse(seconds * 0.5f);
        SoundAt?.Invoke("earth", fire.GlobalPosition, 0.9f, 0.7f);
        FireFx.FreeAfter(fire, seconds);
    }

    /// <summary>a fire dying down: its particles stop coming (the last ones live out their time), its light fades, then it
    /// is gone</summary>
    public static void Douse(Node3D fire, float seconds = 5f)
    {
        if (fire == null || !GodotObject.IsInstanceValid(fire)) return;
        if (fire is Blazing b) b.SetProcess(false);                      // no more spots catching
        foreach (var ps in FireFx.Parts(fire)) ps.Emitting = false;
        foreach (var f in KitNodes.Below(fire, "").OfType<FireFlicker>()) f.FadeOut(seconds * 0.6f);
        FireFx.FreeAfter(fire, seconds);
    }

    /// <summary>what is left of a fire: pale smoke rising from the ash, a few embers, flames dying down over the first half
    /// minute (on the three lowest of its <paramref name="spots"/>; none: in the ash) and a light dying with them; the
    /// smoke thins over two minutes to a wisp that stays. <paramref name="age"/>: seconds it has smouldered already</summary>
    public static Node3D Smoulder(Node3D parent, Aabb local, float age = 0f, IList<Vector3> spots = null)
    {
        var go = new Smouldering { Name = "Smoulder" };
        parent.AddChild(go);
        go.Init(local, age, spots);
        return go;
    }

    /// <summary>a ring of fire going off on the ground (a fire circle): flames shooting up round its edge and a few
    /// inside, in two waves, a flash on the ground, sparks falling back and a puff of pale smoke; gone in a few seconds</summary>
    public static void Burst(Vector3 at, float radius)
    {
        var go = new Node3D { Name = "FireBurst" };
        Scene.AddChild(go);
        go.GlobalPosition = at;
        SoundAt?.Invoke("fire_spray", at, 0.8f, 1f);
        float r = Mathf.Max(0.5f, radius);
        int ring = Mathf.Clamp(Mathf.RoundToInt(r * 2f * Mathf.Pi * 2.2f), 8, 60), inside = Mathf.Clamp(Mathf.RoundToInt(3f * r * r), 3, 40);
        Shoot(go, "Ring", r, 0f, ring, new Vector2(0.9f, 1.5f), new Vector2(1.5f, 3f), new Vector2(0.9f, 1.4f), 0f);
        Shoot(go, "Ring2", r, 0f, ring / 2, new Vector2(0.9f, 1.5f), new Vector2(1.5f, 3f), new Vector2(0.9f, 1.4f), 0.2f);   // a second, smaller wave
        Shoot(go, "Inside", r * 0.85f, 1f, inside, new Vector2(0.5f, 0.9f), new Vector2(1f, 2f), new Vector2(0.6f, 1f), 0f);
        Shoot(go, "Inside2", r * 0.85f, 1f, inside / 2, new Vector2(0.5f, 0.9f), new Vector2(1f, 2f), new Vector2(0.6f, 1f), 0.2f);
        FireFx.Particles("Flash", go, FireFx.Source.Box(new Vector3(0f, 0.35f, 0f), Vector3.Zero), FireFx.GlowMaterial, 1, (ps, pm) =>
        {
            FireFx.OneShot(ps, 1, 0f);
            ps.Lifetime = 0.6f;
            pm.ScaleMin = pm.ScaleMax = 2.5f * r;
            pm.Color = new Color(1f, 0.42f, 0.1f);
            pm.ColorRamp = new GradientTexture1D { Gradient = FireFx.Grad(new[] { Colors.White, Colors.White }, new[] { 0f, 1f }, new[] { 1f, 0.7f, 0f }, new[] { 0f, 0.25f, 1f }) };
            pm.ScaleCurve = FireFx.CurveTex(0f, 0.7f, 1f, 1f);
        });
        FireFx.Particles("Sparks", go, FireFx.Source.Box(Vector3.Zero, new Vector3(r * 1.6f, 0.05f, r * 1.6f)), FireFx.EmberMaterial, 30, (ps, pm) =>
        {
            FireFx.OneShot(ps, 30, 0f);
            FireFx.Life(ps, pm, 0.9f, 1.5f);
            pm.Direction = Vector3.Up; pm.Spread = 35f;
            pm.InitialVelocityMin = 2.5f; pm.InitialVelocityMax = 4.5f;
            pm.ScaleMin = 0.04f; pm.ScaleMax = 0.08f;
            pm.Gravity = new Vector3(0f, -0.5f * 9.81f, 0f);                // falling back
            FireFx.EmberLook(ps, pm);
        });
        FireFx.Particles("Smoke", go, FireFx.Source.Box(Vector3.Zero, new Vector3(r * 1.6f, 0.05f, r * 1.6f)), FireFx.SmokeMaterial, 10, (ps, pm) =>
        {
            FireFx.OneShot(ps, 10, 0.12f);
            FireFx.Life(ps, pm, 2f, 3f);
            pm.ScaleMin = 1.4f; pm.ScaleMax = 2.2f;
            FireFx.Rise(pm, 0.6f, 1.2f);
            FireFx.SmokeLook(ps, pm, 0.8f, true);
        });
        FireFx.FreeAfter(go, 3.5f);
    }

    /// <summary>a small fire that stays where it is (the kit's torches, braziers, hearths and fire pits, a bonfire):
    /// flames licking up off a patch <paramref name="patch"/> wide (x, z) at <paramref name="at"/> (the parent's space) at
    /// <paramref name="scale"/> (a torch's 0.18, a bonfire's 0.9), a few sparks off the bigger ones and a thin pale smoke
    /// outdoors; the flames and sparks kept <see cref="FireFx.Still"/>; already burning when it is first seen</summary>
    public static Node3D Steady(Node3D parent, Vector3 at, Vector2 patch, float scale, bool sparks, bool smoke)
    {
        var go = new Node3D { Name = "Fire" };
        parent.AddChild(go);
        float rate = (5f + 12f * scale) * Mathf.Max(1f, Mathf.Max(patch.X, patch.Y) / 0.4f);   // a hearth's long bed: more
        var src = FireFx.Source.Box(at, new Vector3(Mathf.Max(0.04f, patch.X), 0.02f, Mathf.Max(0.04f, patch.Y)));
        FireFx.Still(FireFx.Flames(go, src, scale, rate, Mathf.CeilToInt(rate * 1.3f) + 2));
        FireFx.Still(FireFx.Flames(go, src, scale, rate * 0.5f, Mathf.CeilToInt(rate * 0.7f) + 2, true));
        if (sparks)
            FireFx.Still(FireFx.Embers(go, FireFx.Source.Box(at + Vector3.Up * 0.1f, new Vector3(patch.X, 0.05f, patch.Y)),
                                       1f + 2.5f * scale, 0.35f + 0.5f * scale, Mathf.RoundToInt(6f * scale), 16));
        if (smoke)                                                  // the breeze is the world's: not still
            FireFx.Smoke(go, FireFx.Source.Box(at + Vector3.Up * (0.5f + 1.4f * scale), new Vector3(0.2f, 0.1f, 0.2f) * (0.5f + scale)),
                         1f + 1.5f * scale, 0.4f + 0.7f * scale, 0.7f + 1.4f * scale, 0.22f, 3.5f, 0.8f, true, 14);
        FireFx.Warm(go, 3f);
        SoundLoop?.Invoke("fire_loop", go, Mathf.Clamp(scale * 2.2f, 0.35f, 1.5f), Mathf.Lerp(1.15f, 0.8f, Mathf.Clamp(scale, 0f, 1f)));
        return go;
    }

    /// <summary>a bolt of fire bursting where it lands: a puff of flames, a spray of sparks, a flash and a moment of light;
    /// <paramref name="size"/> 1 a Firebolt's</summary>
    public static void Splash(Vector3 at, float size = 1f)
    {
        var go = new Node3D { Name = "FireSplash" };
        Scene.AddChild(go);
        go.GlobalPosition = at;
        SoundAt?.Invoke("spell_hit", at, 0.8f, 0.75f);
        FireFx.Particles("Flames", go, FireFx.Source.Box(Vector3.Zero, Vector3.One * 0.3f * size), FireFx.BodyMaterial, 8, (ps, pm) =>
        {
            FireFx.OneShot(ps, 8, 0f);
            FireFx.Life(ps, pm, 0.35f, 0.6f);
            pm.ScaleMin = 0.45f * size; pm.ScaleMax = 0.75f * size;
            pm.AngleMin = -7f; pm.AngleMax = 7f;
            FireFx.Rise(pm, 0.6f + 0.4f * size, 1.2f + 1.4f * size);
            FireFx.FlameLook(ps, pm, false);
        });
        FireFx.Particles("Sparks", go, FireFx.Source.Box(Vector3.Zero, Vector3.One * 0.2f * size), FireFx.EmberMaterial, 12, (ps, pm) =>
        {
            FireFx.OneShot(ps, 12, 0f);
            FireFx.Life(ps, pm, 0.5f, 1f);
            pm.Direction = Vector3.Up; pm.Spread = 180f;
            pm.InitialVelocityMin = 2f * size; pm.InitialVelocityMax = 4f * size;
            pm.ScaleMin = 0.04f; pm.ScaleMax = 0.07f;
            pm.Gravity = new Vector3(0f, -0.5f * 9.81f, 0f);
            FireFx.EmberLook(ps, pm);
        });
        FireFx.Particles("Flash", go, FireFx.Source.Box(Vector3.Zero, Vector3.Zero), FireFx.GlowMaterial, 1, (ps, pm) =>
        {
            FireFx.OneShot(ps, 1, 0f);
            ps.Lifetime = 0.3f;
            pm.ScaleMin = pm.ScaleMax = 1.6f * size;
            pm.Color = new Color(1f, 0.45f, 0.12f);
            pm.ColorRamp = new GradientTexture1D { Gradient = FireFx.Grad(new[] { Colors.White, Colors.White }, new[] { 0f, 1f }, new[] { 0.8f, 0f }, new[] { 0f, 1f }) };
        });
        FireFx.Lamp(go, Vector3.Zero, 4f * size, 5f * size).FadeOut(0.4f);
        FireFx.FreeAfter(go, 1.5f);
    }

    /// <summary>flames bursting up off a circle on the ground (thickness 0: its edge, 1: all of it), after `delay` s</summary>
    static void Shoot(Node3D parent, string name, float radius, float thickness, int count, Vector2 size, Vector2 rise, Vector2 life, float delay)
    {
        if (count <= 0) return;
        FireFx.Particles(name, parent, FireFx.Source.Box(Vector3.Zero, Vector3.Zero), FireFx.BodyMaterial, count, (ps, pm) =>
        {
            FireFx.OneShot(ps, count, delay);
            FireFx.Life(ps, pm, life.X, life.Y);
            pm.ScaleMin = size.X; pm.ScaleMax = size.Y;
            pm.AngleMin = -7f; pm.AngleMax = 7f;
            pm.EmissionShape = ParticleProcessMaterial.EmissionShapeEnum.Ring;      // flat on the ground
            pm.EmissionRingAxis = Vector3.Up;
            pm.EmissionRingRadius = radius;
            pm.EmissionRingInnerRadius = radius * (1f - Mathf.Clamp(thickness, 0f, 1f));
            pm.EmissionRingHeight = 0.01f;
            FireFx.Rise(pm, rise.X, rise.Y);
            FireFx.FlameLook(ps, pm, false);
        });
    }

    /// <summary>spots round a footprint (when a thing has none of its own): its corners and the middles of its sides, a
    /// little in, low, a third and two thirds of the way up, and two near the top</summary>
    static List<Vector3> Footprint(Aabb b)
    {
        var list = new List<Vector3>();
        var c = b.GetCenter();
        float ex = b.Size.X * 0.5f * 0.85f, ez = b.Size.Z * 0.5f * 0.85f, h = b.Size.Y;
        foreach (float y in new[] { 0.08f, 0.38f, 0.65f })
            for (int i = 0; i < 8; i++)
            {
                float a = i * Mathf.Pi * 0.25f;                     // round to the corners and the sides' middles
                list.Add(new Vector3(c.X + Mathf.Round(Mathf.Cos(a)) * ex, b.Position.Y + y * h, c.Z + Mathf.Round(Mathf.Sin(a)) * ez));
            }
        list.Add(new Vector3(c.X - ex * 0.4f, b.Position.Y + 0.9f * h, c.Z + ez * 0.3f));
        list.Add(new Vector3(c.X + ex * 0.4f, b.Position.Y + 0.9f * h, c.Z - ez * 0.3f));
        return list;
    }
}

/// <summary>a blaze catching spot by spot (<see cref="Fire.Blaze"/>, the spots nearest first): the flames, the glow and the
/// embers come from the spots alight; the smoke, the glow, the embers and the light grow with them; falling in, they go
/// out spot by spot, the highest first</summary>
public partial class Blazing : Node3D
{
    List<Vector3> spots;
    float scale;
    double next, fadeFrom, fadeFor;
    int lit, litAtFall;
    Aabb local;
    GpuParticles3D body, core, glow, embers, smoke;
    FireFlicker lamp;
    static double Now => Time.GetTicksMsec() / 1000.0;

    internal void Init(List<Vector3> spots, float scale, Aabb local, int lit)
    {
        this.spots = spots; this.scale = scale; this.local = local;
        float sx = local.Size.X, sz = local.Size.Z, h = local.Size.Y;
        var c = local.GetCenter();
        int n = spots.Count;
        body = FireFx.Flames(this, FireFx.Source.Spots(spots, 1, 0.4f * scale), scale, 0f, 12 * n);
        core = FireFx.Flames(this, FireFx.Source.Spots(spots, 1, 0.25f * scale), scale, 0f, 6 * n, true);
        glow = FireFx.Glow(this, FireFx.Source.Spots(spots, 1, 0.5f * scale), 3f * scale, 0f, 0.12f);   // faint: the light warms the ground
        embers = FireFx.Embers(this, FireFx.Source.Spots(spots, 1, 0.5f * scale), 0f, 1f, 10, 100);
        smoke = FireFx.Smoke(this, FireFx.Source.Box(new Vector3(c.X, local.Position.Y + 0.6f * h, c.Z), new Vector3(0.56f * sx, 0.3f * h, 0.56f * sz)),
                             0f, 2.6f * scale, 4f * scale, 0.8f, 5f, 1.4f, false);
        lamp = FireFx.Lamp(this, new Vector3(c.X, local.Position.Y + 0.5f * h, c.Z), 3.5f, Mathf.Clamp(1.8f * Mathf.Max(sx, sz), 6f, 12f));
        Set(lit);
        if (embers != null) for (int i = 0; i < 20; i++) embers.EmitParticle(Transform3D.Identity, Vector3.Zero, Colors.White, Colors.White, 0);   // the rags catching
        next = Now + Fire.SpreadSeconds;
    }

    public override void _Process(double delta)
    {
        if (spots == null) return;
        if (fadeFor > 0) { Dying(); return; }
        if (Now < next) return;
        if (lit >= spots.Count) { SetProcess(false); return; }
        next = Now + Fire.SpreadSeconds;
        Set(lit + 1);
    }

    /// <summary>the first n spots alight</summary>
    void Set(int n)
    {
        lit = Mathf.Clamp(n, 1, spots.Count);
        FireFx.SetSpots(body, spots, lit, 0.4f * scale);
        FireFx.SetSpots(core, spots, lit, 0.25f * scale);
        FireFx.SetSpots(glow, spots, lit, 0.5f * scale);
        FireFx.SetSpots(embers, spots, lit, 0.5f * scale);
        float g = 0.3f + 0.7f * lit / spots.Count;                  // the rest grows from a third to full
        FireFx.Rate(body, 7f * lit);
        FireFx.Rate(core, 3.5f * lit);
        FireFx.Rate(glow, 3f * g);
        FireFx.Rate(embers, 10f * g);
        FireFx.Rate(smoke, 10f * g);
        if (lamp == null) return;
        lamp.Level = g;
        var mid = Vector3.Zero;                                     // the light over the spots alight
        for (int i = 0; i < lit; i++) mid += spots[i];
        lamp.Home = mid / lit + Vector3.Up * 0.5f;
    }

    /// <summary>falling in: a gust of sparks and a dozen big puffs of smoke from all over it (its own column stops), the
    /// flames going out over <paramref name="fade"/> s, the highest first, the light fading with them</summary>
    internal void Collapse(float fade)
    {
        spots = spots.GetRange(0, lit);
        spots.Sort((a, b) => a.Y.CompareTo(b.Y));                   // the lowest alight longest
        litAtFall = lit;
        fadeFrom = Now; fadeFor = Mathf.Max(0.1f, fade);
        SetProcess(true);
        lamp?.FadeOut(fade);
        if (embers != null) for (int i = 0; i < 40; i++) embers.EmitParticle(Transform3D.Identity, Vector3.Zero, Colors.White, Colors.White, 0);
        if (smoke == null) return;
        var rng = new Random();
        float R(float a, float b) => a + (float)rng.NextDouble() * (b - a);
        var lo = local.Position; var hi = local.End; var c = local.GetCenter();
        for (int i = 0; i < 12; i++)
        {
            var p = new Vector3(R(lo.X, hi.X) * 0.7f + c.X * 0.3f, lo.Y + local.Size.Y * R(0.15f, 0.6f), R(lo.Z, hi.Z) * 0.7f + c.Z * 0.3f);
            float s = R(3f, 4.5f) * scale / Mathf.Max(0.1f, (smoke.ProcessMaterial as ParticleProcessMaterial)?.ScaleMax ?? 1f);
            var xf = new Transform3D(Basis.Identity.Scaled(Vector3.One * s), GlobalTransform * p);
            smoke.EmitParticle(xf, new Vector3(0f, R(0.8f, 1.5f), 0f), Colors.White, Colors.White,
                               (uint)(GpuParticles3D.EmitFlags.Position | GpuParticles3D.EmitFlags.RotationScale | GpuParticles3D.EmitFlags.Velocity));
        }
        smoke.Emitting = false;
    }

    /// <summary>the spots alight dwindling with the time left, then nothing more coming (the last flames live out)</summary>
    void Dying()
    {
        float k = 1f - (float)((Now - fadeFrom) / fadeFor);
        if (k > 0f)
        {
            int n = Mathf.CeilToInt(litAtFall * k);
            if (n != lit) Set(n);
            return;
        }
        foreach (var ps in FireFx.Parts(this)) ps.Emitting = false;
        SetProcess(false);
    }
}

/// <summary>a fire burned down (<see cref="Fire.Smoulder"/>): flames dying down and their light for the first half minute,
/// pale smoke thinning over two minutes to a wisp that stays (with a few embers)</summary>
public partial class Smouldering : Node3D
{
    const float FlameSeconds = 30f, TaperSeconds = 120f, SmokeRate = 3f, Flame0 = 0.55f, Flame1 = 0.35f;

    GpuParticles3D smoke, flames;
    double start;
    static double Now => Time.GetTicksMsec() / 1000.0;

    internal void Init(Aabb local, float age, IList<Vector3> given)
    {
        start = Now - age;
        var c = local.GetCenter();
        float sx = local.Size.X, sz = local.Size.Z, y0 = local.Position.Y;
        smoke = FireFx.Smoke(this, FireFx.Source.Box(new Vector3(c.X, y0 + 0.5f, c.Z), new Vector3(0.5f * sx, 0.4f, 0.5f * sz)),
                             SmokeRate, 1.5f, 2.5f, 0.65f, 7f, 0.9f, true, 80);
        FireFx.Embers(this, FireFx.Source.Box(new Vector3(c.X, y0 + 0.2f, c.Z), new Vector3(0.6f * sx, 0.2f, 0.6f * sz)), 1.5f, 0.5f, 0, 12);
        if (age < FlameSeconds)
        {
            var spots = new List<Vector3>();
            if (given != null && given.Count >= 3)
            {
                spots.AddRange(given);                              // the lowest three: the base's timbers
                spots.Sort((a, b) => a.Y.CompareTo(b.Y));
            }
            else
            {
                spots.Add(new Vector3(c.X - 0.2f * sx, y0 + 0.15f, c.Z - 0.15f * sz));      // three in the ash bed
                spots.Add(new Vector3(c.X + 0.22f * sx, y0 + 0.2f, c.Z + 0.1f * sz));
                spots.Add(new Vector3(c.X + 0.02f * sx, y0 + 0.12f, c.Z + 0.28f * sz));
            }
            flames = FireFx.Flames(this, FireFx.Source.Spots(spots, 3, 0.14f), Flame0, 6f, 16);
            var lamp = FireFx.Lamp(this, new Vector3(c.X, y0 + 1f, c.Z), 1.2f, Mathf.Clamp(1.6f * Mathf.Max(sx, sz), 5f, 9f));
            lamp.FadeOut(FlameSeconds - age);
            FireFx.FreeAfter(lamp.GetParent(), FlameSeconds - age + 0.1f);
        }
        _Process(0);                                                // the rates for its age, then
        if (age > 0f) FireFx.Warm(this, 6f);                        // smoking already when the level comes back
    }

    public override void _Process(double delta)
    {
        float t = (float)(Now - start);
        if (flames != null && t >= FlameSeconds)
        {
            flames.Emitting = false;
            FireFx.FreeAfter(flames, 1.5f);
            flames = null;
        }
        if (flames != null) FireFx.FlameSize(flames, Mathf.Lerp(Flame0, Flame1, t / FlameSeconds));
        FireFx.Rate(smoke, SmokeRate * Mathf.Lerp(1f, 0.3f, Mathf.Min(1f, t / TaperSeconds)));
        if (t >= TaperSeconds && flames == null) SetProcess(false);    // the wisp stays as it is
    }
}
